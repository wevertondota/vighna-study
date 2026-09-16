from datetime import datetime
from banco import conectar, criar_banco


NOME_MIGRACAO = "excel_estado_inicial_2026_09_15"


# revisoes_iniciais, proxima_revisao, percentual_inicial,
# observacao, texto_erros, continuacao
DADOS = {
    "Geral": {
        "Direito Constitucional -> art 1 ao 5": (1, "2026-10-07", 0.0, None, None, None),
        "Direito Constitucional -> 6 ao 17": (1, "2026-10-08", 0.0, "Art 17", None, None),
        "Estatuto GCM Federal": (1, "2026-10-09", 0.0, None, None, None),
        "Lei Orgânica Municipal de Toledo": (2, "2026-10-03", 74.0, None, None, None),
        "Estatuto do Desarmamento": (2, "2026-09-26", 89.0, None, None, None),
    },

    "Direito Penal": {
        "Título I: Da aplicação da lei penal": (2, "2026-09-20", 67.0, None, None, None),
        "Título II: Do crime": (2, "2026-10-22", 90.0, None, None, None),
        "Título III: Da imputabilidade penal": (3, "2026-10-26", 87.0, None, None, None),
        "Título IV: Do concurso de pessoas": (1, "2026-09-24", 85.0, None, None, None),
        "Título V: Das penas": (2, "2026-09-24", 89.0, None, None, None),
        "Título VI: Das medidas de segurança": (2, "2026-09-22", 70.0, None, None, None),
        "Título VII: Da ação penal": (2, "2026-09-24", 86.0, None, None, None),
        "Título VIII: Da extinção da punibilidade": (1, "2026-09-24", 75.0, None, None, None),
        "Título I: Dos crimes contra a pessoa": (2, "2026-09-28", 81.0, None, None, None),
        "Título II: Dos crimes contra o patrimônio": (1, "2026-09-16", 60.0, None, None, None),
        "Título VI: Dos crimes contra a dignidade sexual": (1, "2026-07-17", 49.0, None, None, None),
    },

    "Direito Administrativo": {
        "Regime Jurídico Administrativo": (2, "2026-09-22", 80.0, None, None, None),
        "Conceito de Direito Administrativo e Administração Pública": (2, "2026-09-26", 100.0, None, None, None),
    },

    "CTB": {
        "Capítulo I: Disposições Preliminares": (1, "2026-09-15", 0.0, None, None, None),
        "Capítulo II: Do Sistema Nacional de Trânsito": (2, "2026-10-15", 89.0, None, None, None),
        "Capítulo III: Das Normas Gerais de Circulação e Conduta": (2, "2026-11-02", 93.0, None, None, None),
        "Capítulo III-A: Da Condução de Veículos por Motoristas Profissionais": (0, "2026-08-28", None, None, None, None),
        "Capítulo IV: Dos Pedestres e Condutores de Veículos não Motorizados": (0, "2026-09-15", None, None, None, None),
        "Capítulo V: Do Cidadão": (0, "2026-09-16", None, None, None, None),
        "Capítulo VI: Da Educação para o Trânsito": (0, "2026-09-17", None, None, None, None),
        "Capítulo VII: Da Sinalização de Trânsito": (0, "2026-09-18", None, None, None, None),
        "Capítulo VIII: Da Engenharia de Tráfego, da Operação, da Fiscalização e do Policiamento Ostensivo de Trânsito": (0, "2026-09-19", None, None, None, None),
        "Capítulo IX: Dos Veículos": (0, "2026-09-20", None, None, None, None),
        "Capítulo X: Dos Veículos em Circulação Internacional": (0, "2026-09-21", None, None, None, None),
        "Capítulo XI: Do Registro de Veículos": (0, "2026-09-22", None, None, None, None),
        "Capítulo XII: Do Licenciamento": (0, "2026-09-23", None, None, None, None),
        "Capítulo XIII: Da Condução de Escolares": (0, "2026-09-24", None, None, None, None),
        "Capítulo XIII-A: Da Condução de Moto-Frete": (0, "2026-09-25", None, None, None, None),
        "Capítulo XIV: Da Habilitação": (1, "2026-09-21", 71.0, None, None, None),
        "Capítulo XV: Das Infrações": (2, "2026-09-21", 87.0, None, None, None),
        "Capítulo XVI: Das Penalidades": (2, "2026-09-23", 83.0, None, None, None),
        "Capítulo XVII: Das Medidas Administrativas": (1, "2026-10-05", 73.0, None, None, None),
        "Capítulo XVIII: Do Processo Administrativo": (1, "2026-09-21", 52.0, None, None, None),
        "Capítulo XIX: Dos Crimes de Trânsito": (2, "2026-09-19", 65.0, None, None, None),
        "Capítulo XX: Disposições Finais e Transitórias": (0, "2026-09-28", None, None, None, None),
    },

    "Português": {
        "Hífen": (1, "2026-09-15", 100.0, None, None, None),
    },
}


def localizar_topico(conexao, disciplina, topico):
    return conexao.execute(
        """
        SELECT t.id
        FROM topicos t
        JOIN disciplinas d ON d.id = t.disciplina_id
        WHERE d.nome = ? AND t.nome = ?
        """,
        (disciplina, topico)
    ).fetchone()


def main():
    criar_banco()

    with conectar() as conexao:
        ja_executada = conexao.execute(
            "SELECT 1 FROM migracoes WHERE nome = ?",
            (NOME_MIGRACAO,)
        ).fetchone()

        if ja_executada:
            print("Esta migração já foi executada anteriormente.")
            print("Nada foi alterado.")
            return

        importados = 0
        nao_encontrados = []

        for disciplina, topicos in DADOS.items():
            for nome_topico, dados in topicos.items():
                encontrado = localizar_topico(
                    conexao,
                    disciplina,
                    nome_topico
                )

                if encontrado is None:
                    nao_encontrados.append(
                        f"{disciplina} -> {nome_topico}"
                    )
                    continue

                topico_id = encontrado[0]

                (
                    revisoes_iniciais,
                    proxima_revisao,
                    percentual_inicial,
                    observacao,
                    texto_erros,
                    continuacao
                ) = dados

                conexao.execute(
                    """
                    INSERT INTO controle_topico (
                        topico_id,
                        revisoes_iniciais,
                        proxima_revisao,
                        percentual_inicial,
                        observacao_inicial,
                        texto_erros_inicial,
                        continuacao_inicial
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)

                    ON CONFLICT(topico_id)
                    DO UPDATE SET
                        revisoes_iniciais = excluded.revisoes_iniciais,
                        proxima_revisao = excluded.proxima_revisao,
                        percentual_inicial = excluded.percentual_inicial,
                        observacao_inicial = excluded.observacao_inicial,
                        texto_erros_inicial = excluded.texto_erros_inicial,
                        continuacao_inicial = excluded.continuacao_inicial
                    """,
                    (
                        topico_id,
                        revisoes_iniciais,
                        proxima_revisao,
                        percentual_inicial,
                        observacao,
                        texto_erros,
                        continuacao
                    )
                )

                importados += 1

        conexao.execute(
            """
            INSERT INTO migracoes (nome, executada_em)
            VALUES (?, ?)
            """,
            (
                NOME_MIGRACAO,
                datetime.now().isoformat(timespec="seconds")
            )
        )

    print()
    print("MIGRAÇÃO CONCLUÍDA")
    print("------------------")
    print(f"Tópicos atualizados com dados do Excel: {importados}")

    if nao_encontrados:
        print()
        print("Tópicos não encontrados:")
        for item in nao_encontrados:
            print(" -", item)

    print()
    print("As revisões que você já registrou no programa foram preservadas.")
    print("Os números antigos do Excel entram como histórico inicial,")
    print("sem inventar quantidade de questões ou acertos.")


if __name__ == "__main__":
    main()
