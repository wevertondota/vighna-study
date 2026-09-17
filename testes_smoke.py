"""Testes rápidos do núcleo sem tocar no banco real do usuário.

Execute com: python testes_smoke.py
"""

from pathlib import Path
from contextlib import closing
import sqlite3
import tempfile
import shutil
from datetime import datetime, timedelta

import banco
from inteligencia import CacheAnalitico, MotorRecomendacaoV5
import jornada
import evolucao
import laboratorio
import checkpoint
from versao import VIGHNA_VERSION


def assert_true(cond, msg):
    if not cond:
        raise AssertionError(msg)


def main():
    original = banco.CAMINHO_BANCO
    with tempfile.TemporaryDirectory(prefix="vighna_smoke_") as temp:
        banco.CAMINHO_BANCO = Path(temp) / "estudos.db"
        banco.criar_banco()
        with banco.conectar() as con:
            ok = con.execute("PRAGMA integrity_check").fetchone()[0]
            assert_true(str(ok).lower() == "ok", "integridade SQLite")
            nomes_indices = {r[0] for r in con.execute(
                "SELECT name FROM sqlite_master WHERE type='index'"
            ).fetchall()}
            assert_true("idx_revisoes_topico_data" in nomes_indices, "índice de revisões")
            assert_true("idx_tentativas_concurso_data" in nomes_indices, "índice de tentativas")
            assert_true("idx_revisoes_prazo" in nomes_indices, "índice de prazo de revisão")
            colunas_revisoes = {r[1] for r in con.execute("PRAGMA table_info(revisoes)").fetchall()}
            assert_true({"prevista_para","realizada_em","dias_atraso","prazo_historico_valido"}.issubset(colunas_revisoes), "migração do histórico de prazo")
            colunas_tci = {r[1] for r in con.execute("PRAGMA table_info(topico_concurso_importancia)").fetchall()}
            assert_true("pausado" in colunas_tci, "migração de tópico desligado")
            assert_true("idx_tci_concurso_operacional" in nomes_indices, "índice de tópicos operacionais")
            colunas_dci = {r[1] for r in con.execute("PRAGMA table_info(disciplina_concurso_inclusao)").fetchall()}
            assert_true("pausado" in colunas_dci, "migração de disciplina desligada")
            assert_true("idx_dci_concurso_estado" in nomes_indices, "índice de disciplinas operacionais")

        with banco.conectar() as con:
            concurso_id = int(con.execute(
                "SELECT id FROM concursos WHERE e_padrao = 1 ORDER BY id LIMIT 1"
            ).fetchone()[0])
            con.execute("INSERT OR IGNORE INTO disciplinas(nome) VALUES ('CTB')")
            disciplina_id = int(con.execute(
                "SELECT id FROM disciplinas WHERE nome = 'CTB'"
            ).fetchone()[0])
            con.execute(
                "INSERT OR IGNORE INTO topicos(disciplina_id, nome) VALUES (?, 'Habilitação Smoke')",
                (disciplina_id,),
            )
            topico_id = int(con.execute(
                "SELECT id FROM topicos WHERE disciplina_id = ? AND nome = 'Habilitação Smoke'",
                (disciplina_id,),
            ).fetchone()[0])
            con.execute(
                """INSERT OR IGNORE INTO capitulos_topico(topico_id, nome, ordem)
                   VALUES (?, 'Capítulo Smoke', 1)""",
                (topico_id,),
            )
            capitulo_id = int(con.execute(
                """SELECT id FROM capitulos_topico
                   WHERE topico_id = ? AND nome = 'Capítulo Smoke'""",
                (topico_id,),
            ).fetchone()[0])
            con.execute(
                """INSERT OR REPLACE INTO disciplina_concurso_inclusao
                   (disciplina_id, concurso_id, incluido) VALUES (?, ?, 1)""",
                (disciplina_id, concurso_id),
            )
            con.execute(
                """INSERT OR REPLACE INTO topico_concurso_importancia
                   (topico_id, concurso_id, importancia, incluido) VALUES (?, ?, 5, 1)""",
                (topico_id, concurso_id),
            )

        # Desativação temporária: tópico desligado e questão desativada não entram
        # nas novas sessões, mas continuam administráveis e reversíveis.
        qid_smoke = banco.criar_questao(
            topico_id,
            "Questão smoke de desligamento temporário?",
            [
                {"letra": "A", "texto": "Correta", "correta": True},
                {"letra": "B", "texto": "Distrator", "correta": False},
            ],
            explicacao="Smoke",
            capitulo_id=capitulo_id,
        )
        questao_smoke = banco.obter_questao(
            qid_smoke
        )
        assert_true(
            not questao_smoke["analise_pendente"],
            "questão nasce sem análise pendente"
        )
        assert_true(
            banco.definir_questao_analise_pendente(
                qid_smoke,
                True
            ),
            "questão pode ser separada para análise"
        )
        questao_smoke = banco.obter_questao(
            qid_smoke
        )
        assert_true(
            questao_smoke["analise_pendente"]
            and questao_smoke["analise_solicitada_em"],
            "marcação de análise é persistida"
        )
        questoes_administrativas = banco.listar_questoes(
            concurso_id,
            incluir_inativas=True,
            incluir_topicos_pausados=True,
            incluir_disciplinas_pausadas=True
        )
        assert_true(
            any(
                item["id"] == qid_smoke
                and item["analise_pendente"]
                and item["analise_solicitada_em"]
                and item["capitulo_id"] == capitulo_id
                and item["capitulo"] == "Capítulo Smoke"
                for item in questoes_administrativas
            ),
            "Central recebe análise e classificação por capítulo"
        )
        assert_true(
            banco.definir_questao_analise_pendente(
                qid_smoke,
                False
            )
            and not banco.obter_questao(
                qid_smoke
            )["analise_pendente"],
            "marcação de análise pode ser removida"
        )
        with banco.conectar() as con:
            topico_equivalente_id = int(
                con.execute(
                    """
                    INSERT INTO topicos(disciplina_id, nome)
                    VALUES (?, 'Título I: Da habilitação smoke')
                    """,
                    (
                        disciplina_id,
                    )
                ).lastrowid
            )
            con.execute(
                """
                INSERT INTO topico_concurso_importancia
                    (topico_id, concurso_id, importancia, incluido)
                VALUES (?, ?, 3, 1)
                """,
                (
                    topico_equivalente_id,
                    concurso_id,
                )
            )
        equivalentes = (
            banco.listar_topicos_equivalentes_com_questoes(
                concurso_id,
                topico_equivalente_id
            )
        )
        assert_true(
            len(equivalentes) == 1
            and equivalentes[0]["topico_id"] == topico_id
            and equivalentes[0]["quantidade"] == 1,
            "tópico equivalente localiza questões do mesmo conteúdo"
        )
        assert_true(any(q[0] == topico_id for q in banco.listar_topicos("CTB", concurso_id)), "tópico inicialmente ativo")
        assert_true(any(q["id"] == qid_smoke for q in banco.listar_questoes(concurso_id)), "questão inicialmente ativa")
        banco.definir_topico_pausado(topico_id, True, concurso_id)
        assert_true(not any(q[0] == topico_id for q in banco.listar_topicos("CTB", concurso_id)), "tópico desligado sai da operação")
        adm = banco.listar_topicos_gerenciamento("CTB", concurso_id)
        assert_true(any(q[0] == topico_id and bool(q[7]) for q in adm), "tópico desligado permanece administrável")
        assert_true(not any(q["id"] == qid_smoke for q in banco.listar_questoes(concurso_id)), "questões de tópico desligado saem da operação")
        assert_true(any(q["id"] == qid_smoke and q["topico_pausado"] for q in banco.listar_questoes(concurso_id, incluir_topicos_pausados=True)), "questão permanece visível na administração")
        banco.definir_topico_pausado(topico_id, False, concurso_id)
        assert_true(any(q[0] == topico_id for q in banco.listar_topicos("CTB", concurso_id)), "tópico reativado")
        banco.arquivar_questao(qid_smoke)
        assert_true(not any(q["id"] == qid_smoke for q in banco.listar_questoes(concurso_id)), "questão desativada sai das novas sessões")
        assert_true(any(q["id"] == qid_smoke and not q["ativa"] for q in banco.listar_questoes(concurso_id, incluir_inativas=True)), "questão desativada permanece armazenada")
        banco.reativar_questao(qid_smoke)

        # Disciplina desligada: permanece administrável, mas sai de toda a operação.
        assert_true(any(nome == "CTB" for _, nome in banco.listar_disciplinas(concurso_id)), "disciplina inicialmente ativa")
        banco.definir_disciplina_pausada(disciplina_id, True, concurso_id)
        assert_true(not any(nome == "CTB" for _, nome in banco.listar_disciplinas(concurso_id)), "disciplina desligada sai da operação")
        ger = banco.listar_disciplinas_gerenciamento(concurso_id)
        assert_true(any(i == disciplina_id and p for i, nome, p in ger), "disciplina desligada permanece administrável")
        assert_true(not banco.listar_questoes(concurso_id), "questões da disciplina desligada saem da operação")
        adm_q = banco.listar_questoes(
            concurso_id, incluir_inativas=True, incluir_topicos_pausados=True,
            incluir_disciplinas_pausadas=True
        )
        assert_true(any(q["id"] == qid_smoke and q["disciplina_pausada"] for q in adm_q), "questões da disciplina desligada permanecem administráveis")
        banco.definir_disciplina_pausada(disciplina_id, False, concurso_id)
        assert_true(any(nome == "CTB" for _, nome in banco.listar_disciplinas(concurso_id)), "disciplina reativada")

        rec = MotorRecomendacaoV5(
            fila=[{
                "topico_id": topico_id, "disciplina": "CTB", "topico": "Habilitação Smoke",
                "score": 80, "nivel": "Alta", "proxima": "2026-09-15",
                "percentual": 60, "revisoes": 1, "importancia": 5,
            }],
            adaptativas=[{"topico_id": topico_id, "questoes_disponiveis": 30, "motivo_principal": "domínio frágil"}],
            contexto={"foco": {"semana_segundos": 3600}, "distribuicao": {}, "recentes": [], "faltam_hoje": 3600},
            calibracao={},
            perfil_decisoes={},
            hoje="2026-09-15",
            pesos={"urgencia": 45, "necessidade": 40, "momento": 15},
            proteger_revisoes_vencidas=True,
        ).montar()
        assert_true(rec["origem"] == "revisao", "origem da recomendação")
        assert_true(rec["score_explicado"], "explicação do score")
        assert_true(rec["versao_motor"] == 5, "motor V5")
        assert_true(set(rec["eixos_v5"]) == {"urgencia", "necessidade", "momento"}, "eixos V5")

        cache = CacheAnalitico()
        contador = {"n": 0}
        def carregar():
            contador["n"] += 1
            return 42
        assert_true(cache.obter("x", carregar) == 42, "cache primeira leitura")
        assert_true(cache.obter("x", carregar) == 42 and contador["n"] == 1, "cache reaproveita")

        # Calibração: cinco sessões reais de 20 min com 10 respostas cada.
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with banco.conectar() as con:
            for _ in range(5):
                foco_id = int(con.execute(
                    """INSERT INTO sessoes_foco
                       (inicio, fim, duracao_planejada, duracao_efetiva, disciplina_id, topico_id,
                        disciplina_nome, topico_nome, tipo_atividade, concluida)
                       VALUES (?, ?, 1200, 1200, ?, ?, 'CTB', 'Habilitação Smoke', 'Questões', 1)""",
                    (agora, agora, disciplina_id, topico_id),
                ).lastrowid)
                qs_id = int(con.execute(
                    """INSERT INTO sessoes_questoes
                       (concurso_id, iniciado_em, encerrado_em, modo, objetivo, concluida)
                       VALUES (?, ?, ?, 'Treino', 10, 1)""",
                    (concurso_id, agora, agora),
                ).lastrowid)
                con.execute(
                    "INSERT INTO foco_questoes(sessao_foco_id, sessao_questoes_id) VALUES (?, ?)",
                    (foco_id, qs_id),
                )
                for _q in range(10):
                    con.execute(
                        """INSERT INTO tentativas_questoes
                           (sessao_id, concurso_id, respondida_em, correta, disciplina_id_snapshot,
                            topico_id_snapshot, disciplina_snapshot, topico_snapshot)
                           VALUES (?, ?, ?, 1, ?, ?, 'CTB', 'Habilitação Smoke')""",
                        (qs_id, concurso_id, agora, disciplina_id, topico_id),
                    )
        calibracao = banco.obter_calibracao_foco(120)
        assert_true(calibracao["por_disciplina"]["CTB"]["amostras_questoes"] == 5, "amostras de calibração")
        assert_true(abs(calibracao["por_disciplina"]["CTB"]["segundos_por_questao"] - 120.0) < 0.01, "ritmo real por questão")

        hoje_data = datetime.now().date()
        prevista = hoje_data - timedelta(days=2)
        with banco.conectar() as con:
            con.execute("INSERT OR IGNORE INTO controle_topico(topico_id) VALUES (?)", (topico_id,))
            con.execute("UPDATE controle_topico SET proxima_revisao = ? WHERE topico_id = ?", (prevista.isoformat(), topico_id))
        banco.registrar_revisao(
            topico_id, hoje_data.isoformat(), 10, 8, "smoke evolução",
            proxima_revisao=(hoje_data + timedelta(days=7)).isoformat(),
        )
        revisoes = banco.listar_revisoes_topico(topico_id)
        assert_true(revisoes[0][11] >= 0, "índice legado de tentativas preservado")
        assert_true(revisoes[0][12] == prevista.isoformat(), "prazo planejado preservado")
        assert_true(revisoes[0][14] == 2 and revisoes[0][15] == 1, "atraso histórico preciso")
        prazos = banco.obter_estatisticas_prazos_revisoes(concurso_id, 30, hoje_data.isoformat())
        assert_true(prazos["total_com_prazo"] == 1, "amostra de prazo")
        assert_true(prazos["atrasadas"] == 1 and abs(prazos["atraso_medio_dias"] - 2.0) < 0.01, "estatística de atraso")

        hist = evolucao.obter_evolucao_historica(concurso_id, 30)
        assert_true(hist["foco"]["segundos"] >= 6000, "foco histórico")
        assert_true(hist["resumo"]["questoes"] >= 50, "questões históricas")
        assert_true(hist["revisoes_periodo"] >= 1, "revisões históricas")
        assert_true(hist["foco"]["dias_ativos"] >= 1, "consistência histórica")
        assert_true(hist["topicos_tendencia"], "tópicos em movimento")
        assert_true(any("foco_minutos" in item for item in hist["serie"]), "série histórica integrada")
        assert_true(hist["prazos_revisao"]["total_com_prazo"] == 1, "pontualidade integrada ao histórico")

        rel = laboratorio.montar_laboratorio(
            fila=[{
                "topico_id": topico_id, "disciplina": "CTB", "topico": "Habilitação Smoke",
                "score": 80, "nivel": "Alta", "proxima": hoje_data.isoformat(),
                "percentual": 60, "revisoes": 1, "importancia": 5,
            }],
            adaptativas=[{
                "topico_id": topico_id, "disciplina": "CTB", "topico": "Habilitação Smoke",
                "questoes_disponiveis": 30, "dominio": 55, "importancia": 5,
                "urgencia": 88, "componentes": {
                    "dominio": 45, "erros": 60, "evidencia": 50, "variedade": 40,
                    "estabilidade": 35, "recencia": 55, "urgencia": 88, "importancia": 100,
                },
            }],
            contexto={"foco": {"semana_segundos": 3600}, "distribuicao": {}, "recentes": [], "faltam_hoje": 3600},
            hoje=hoje_data.isoformat(), pesos={"urgencia": 45, "necessidade": 40, "momento": 15},
            proteger_revisoes_vencidas=True,
        )
        assert_true(rel["ranking"], "ranking do laboratório")
        assert_true(rel["recomendacao"]["versao_motor"] == 5, "laboratório usa V5")
        assert_true("score" in laboratorio.explicar_topico(rel, "Habilitação"), "explicação de tópico")

        rid = banco.registrar_recomendacao_estudo(concurso_id, rec)
        assert_true(rid > 0, "registro de recomendação")
        banco.atualizar_decisao_recomendacao(rid, "aceita", rec["minutos"])
        perfil = banco.obter_perfil_decisoes_recomendacao(concurso_id)
        assert_true(perfil["aceitas"] == 1, "histórico de decisões")

        # Jornada do Dia: monta fila, prepara o Foco e persiste o resultado.
        jd = jornada.gerar_jornada(
            concurso_id,
            recomendacao=rec,
            fila=[{
                "topico_id": topico_id, "disciplina": "CTB", "topico": "Habilitação Smoke",
                "score": 80, "nivel": "Alta", "proxima": "2026-09-15",
                "percentual": 60, "revisoes": 1, "importancia": 5,
                "motivo": "revisão pendente",
            }],
            plano={"itens": []},
            data_ref=datetime.now().date().isoformat(),
        )
        assert_true(jd["itens"], "jornada possui atividades")
        item = jornada.proximo_item(jd)
        assert_true(item is not None, "jornada possui próxima atividade")
        prep = jornada.preparar_item(item, jd["data"], concurso_id)
        assert_true(prep["origem"] == "Jornada do Dia", "origem da preparação da jornada")
        assert_true(str(prep["plano_chave"]).startswith("jornada|"), "chave da jornada")
        jd2 = jornada.marcar_por_plano_chave(
            concurso_id, prep["plano_chave"], True, sessao_id=999, duracao_efetiva=900
        )
        marcado = next(i for i in jd2["itens"] if i["id"] == item["id"])
        assert_true(marcado["status"] == "concluida", "conclusão da atividade da jornada")
        pausada = jornada.definir_status_jornada(concurso_id, "pausada", jd["data"])
        assert_true(pausada["status"] == "pausada", "pausa da jornada")

        # Checkpoint Total V3: inventário atual + banco + auditoria contra mudanças.
        projeto_smoke = Path(temp) / "projeto_checkpoint"
        projeto_smoke.mkdir(parents=True, exist_ok=True)
        origem_projeto = Path(__file__).resolve().parent
        for origem, nome_rel in checkpoint._arquivos_do_projeto(origem_projeto):
            destino = projeto_smoke / nome_rel
            destino.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(origem, destino)
        with closing(
            sqlite3.connect(
                projeto_smoke / "estudos.db"
            )
        ) as con:
            con.execute("CREATE TABLE smoke_checkpoint(id INTEGER PRIMARY KEY, valor TEXT)")
            con.execute("INSERT INTO smoke_checkpoint(valor) VALUES ('ok')")
            con.commit()

        localizar_original = checkpoint.localizar_pasta_projeto
        localizar_banco_original = checkpoint.localizar_banco_ativo
        try:
            checkpoint.localizar_pasta_projeto = lambda: projeto_smoke
            checkpoint.localizar_banco_ativo = lambda pasta_projeto=None: projeto_smoke / "estudos.db"
            cp = checkpoint.gerar_checkpoint_completo("smoke-protecao-total")
            inspecao = checkpoint.inspecionar_checkpoint(cp["caminho"])
            assert_true(inspecao["banco_incluido"], "checkpoint completo inclui banco")
            auditoria = checkpoint.auditar_protecao_checkpoint(cp["caminho"])
            assert_true(auditoria["completo"], "auditoria reconhece proteção completa")
            assert_true(not auditoria["faltantes"] and not auditoria["alterados"], "inventário integral protegido")

            alvo_alteracao = projeto_smoke / "navegacao.py"
            alvo_alteracao.write_text(alvo_alteracao.read_text(encoding="utf-8") + "\n# smoke-change\n", encoding="utf-8")
            auditoria_mudou = checkpoint.auditar_protecao_checkpoint(cp["caminho"])
            assert_true(not auditoria_mudou["completo"], "auditoria detecta projeto alterado")
            assert_true("navegacao.py" in auditoria_mudou["alterados"], "auditoria identifica arquivo alterado")
        finally:
            checkpoint.localizar_pasta_projeto = localizar_original
            checkpoint.localizar_banco_ativo = localizar_banco_original

    banco.CAMINHO_BANCO = original
    print(f"VighnaStudy {VIGHNA_VERSION}: testes smoke OK")


if __name__ == "__main__":
    try:
        main()
    finally:
        pass
