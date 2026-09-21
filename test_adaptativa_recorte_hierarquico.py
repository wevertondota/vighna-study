"""Cobertura do recorte hierárquico da Sessão Adaptativa V2.

O teste é somente-leitura e usa o primeiro capítulo ativo com questões no
perfil atual para garantir que a seleção por capítulo não vaze questões de
outros capítulos.
"""

import banco


def test_adaptativa_respeita_recorte_capitulo():
    concurso_id, _ = banco.obter_concurso_ativo()
    candidato = None

    for disciplina_id, disciplina_nome in banco.listar_disciplinas(concurso_id):
        for topico in banco.listar_topicos(disciplina_nome, concurso_id=concurso_id):
            topico_id = int(topico[0])
            for capitulo_id, _nome, _ordem, _dificuldade, pausado in banco.listar_capitulos_topico(
                topico_id, concurso_id=concurso_id
            ):
                if pausado:
                    continue
                with banco.conectar() as conexao:
                    total = conexao.execute(
                        "SELECT COUNT(*) FROM questoes WHERE ativa = 1 AND capitulo_id = ?",
                        (int(capitulo_id),),
                    ).fetchone()[0]
                if int(total or 0) > 0:
                    candidato = (
                        int(disciplina_id),
                        topico_id,
                        int(capitulo_id),
                        int(total),
                    )
                    break
            if candidato:
                break
        if candidato:
            break

    assert candidato is not None, "O banco de teste precisa ter ao menos um capítulo com questão ativa."
    disciplina_id, topico_id, capitulo_id, total = candidato

    plano = banco.planejar_sessao_adaptativa_global(
        concurso_id,
        quantidade=min(5, total),
        disciplina_id=disciplina_id,
        topicos_ids=[topico_id],
        capitulos_ids=[capitulo_id],
    )
    assert plano["quantidade"] == min(5, total)
    assert all(int(item["topico_id"]) == topico_id for item in plano["alocacoes"])
    assert sum(int(item["quantidade"]) for item in plano["alocacoes"]) == min(5, total)

    selecao = banco.selecionar_sessao_adaptativa_global(
        concurso_id,
        quantidade=min(5, total),
        disciplina_id=disciplina_id,
        topicos_ids=[topico_id],
        capitulos_ids=[capitulo_id],
    )
    ids = [int(item["id"]) for item in selecao["fila"]]
    assert len(ids) == min(5, total)

    with banco.conectar() as conexao:
        marcadores = ",".join("?" for _ in ids)
        linhas = conexao.execute(
            f"SELECT id, topico_id, capitulo_id FROM questoes WHERE id IN ({marcadores})",
            ids,
        ).fetchall()

    assert len(linhas) == len(ids)
    assert all(int(linha[1]) == topico_id for linha in linhas)
    assert all(int(linha[2]) == capitulo_id for linha in linhas)


def test_adaptativa_recorte_vazio_nao_vaza_conteudo():
    concurso_id, _ = banco.obter_concurso_ativo()
    prioridades = banco.obter_prioridades_sessao_adaptativa(
        concurso_id,
        capitulos_ids=[],
    )
    assert prioridades == []
