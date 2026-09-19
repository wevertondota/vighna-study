"""Testes rápidos do núcleo sem tocar no banco real do usuário.

Execute com: python testes_smoke.py
"""

from pathlib import Path
from contextlib import closing
import sqlite3
import tempfile
import shutil
import gc
import json
from datetime import datetime, timedelta

import banco
from inteligencia import CacheAnalitico, MotorRecomendacaoV5
import jornada
import evolucao
import laboratorio
import checkpoint
from importador_pdf import analisar_texto_questoes_pdf
from versao import VIGHNA_VERSION


def assert_true(cond, msg):
    if not cond:
        raise AssertionError(msg)


def main():
    # Importação por texto colado reutiliza o parser VPQ/genérico do importador.
    texto_importacao = """VIGHNA PDF — VPQ 1.1
DISCIPLINA: Direito Penal
TÓPICO: Furto
FONTE: Código Penal
QUANTIDADE: 1
ALTERNATIVAS: A-D

QUESTÃO 1
Qual alternativa está correta?
A) Primeira.
B) Segunda.
C) Terceira.
D) Quarta.
GABARITO: C
EXPLICAÇÃO: A alternativa C é a correta.
"""
    analise_texto = analisar_texto_questoes_pdf(texto_importacao, [])
    assert_true(analise_texto["quantidade"] == 1, "texto colado detecta questão")
    assert_true(analise_texto["com_gabarito"] == 1, "texto colado detecta gabarito")
    assert_true(analise_texto["vpq_detectado"], "texto colado reconhece VPQ")
    assert_true(not analise_texto["vpq_bloqueia_importacao"], "VPQ colado íntegro pode importar")

    original = banco.CAMINHO_BANCO
    try:
        with tempfile.TemporaryDirectory(
            prefix="vighna_smoke_",
            ignore_cleanup_errors=True,
        ) as temp:
            banco.CAMINHO_BANCO = Path(temp) / "estudos.db"
            banco.criar_banco()

            # Fila Inteligente V3: os oito sinais convergem para um score único
            # e um cenário claramente frágil deve superar um cenário saudável.
            config_fila = banco._carregar_configuracao_espacamento_fila()
            dominio_fragil = {
                "score": 42.0,
                "cobertura": 28.0,
                "tentativas_historicas": 12,
                "desempenho_base": 78.0,
                "desempenho_recente": 48.0,
                "desempenho": 55.0,
                "dias_desde_ultima": 35,
            }
            dominio_forte = {
                "score": 88.0,
                "cobertura": 92.0,
                "tentativas_historicas": 20,
                "desempenho_base": 90.0,
                "desempenho_recente": 91.0,
                "desempenho": 91.0,
                "dias_desde_ultima": 2,
            }
            fila_fragil = banco._calcular_score_fila_inteligente_v3(
                dominio_fragil, 5, "2026-09-01", 1, 90.0, config_fila
            )
            fila_forte = banco._calcular_score_fila_inteligente_v3(
                dominio_forte, 2, "2026-12-20", 5, 5.0, config_fila
            )
            assert_true(
                fila_fragil["score"] > fila_forte["score"],
                "fila consolidada prioriza cenário mais frágil",
            )
            assert_true(
                set(fila_fragil["componentes"]) == {
                    "atraso", "dominio", "erros_recentes", "queda",
                    "importancia", "cobertura", "revisoes", "espacamento"
                },
                "fila possui os oito fatores auditáveis",
            )
            assert_true(
                abs(sum(float(v) for v in fila_fragil["pesos"].values()) - 100.0) < 0.01,
                "pesos da fila somam 100%",
            )

            # Identidade estrutural: nomes podem mudar sem alterar a entidade
            # lógica nem romper imports que ainda usem o rótulo anterior.
            auditoria_estrutura = banco.auditar_estrutura_conteudos()
            assert_true(
                auditoria_estrutura["ok"],
                "árvore inicial possui identidades estáveis e sem colisões",
            )
            assert_true(
                auditoria_estrutura["sem_chave_estavel"] == {
                    "disciplinas": 0, "topicos": 0, "capitulos": 0
                },
                "toda a árvore recebe chave estável",
            )

            disciplina_identidade_id = banco.adicionar_disciplina(
                "Estrutura Smoke"
            )
            assert_true(
                disciplina_identidade_id is not None,
                "disciplina de identidade criada",
            )
            assert_true(
                banco.adicionar_topico("Estrutura Smoke", "Tópico Smoke"),
                "tópico de identidade criado",
            )
            topico_identidade_id = banco.resolver_topico_id_estrutural(
                "Estrutura Smoke", "Tópico Smoke"
            )
            assert_true(
                topico_identidade_id is not None,
                "tópico é resolvido por nome atual",
            )
            assert_true(
                banco.adicionar_capitulo(
                    topico_identidade_id, "Capítulo Smoke"
                ),
                "capítulo de identidade criado",
            )
            capitulo_identidade_id = banco.resolver_capitulo_id_estrutural(
                topico_identidade_id, "Capítulo Smoke"
            )
            assert_true(
                capitulo_identidade_id is not None,
                "capítulo é resolvido por nome atual",
            )

            identidade_disc_antes = banco.obter_identidade_conteudo(
                "disciplina", disciplina_identidade_id
            )
            identidade_top_antes = banco.obter_identidade_conteudo(
                "topico", topico_identidade_id
            )
            identidade_cap_antes = banco.obter_identidade_conteudo(
                "capitulo", capitulo_identidade_id
            )

            assert_true(
                banco.renomear_disciplina(
                    disciplina_identidade_id, "Estrutura Smoke Renomeada"
                ),
                "disciplina pode ser renomeada",
            )
            assert_true(
                banco.renomear_topico(
                    topico_identidade_id, "Tópico Smoke Renomeado"
                ),
                "tópico pode ser renomeado",
            )
            assert_true(
                banco.renomear_capitulo(
                    capitulo_identidade_id, "Capítulo Smoke Renomeado"
                ),
                "capítulo pode ser renomeado",
            )

            assert_true(
                banco.resolver_disciplina_id_estrutural("Estrutura Smoke")
                == disciplina_identidade_id,
                "alias antigo de disciplina continua resolvendo",
            )
            assert_true(
                banco.resolver_topico_id_estrutural(
                    "Estrutura Smoke", "Tópico Smoke"
                ) == topico_identidade_id,
                "aliases antigos de disciplina e tópico continuam resolvendo",
            )
            assert_true(
                banco.resolver_capitulo_id_estrutural(
                    topico_identidade_id, "Capítulo Smoke"
                ) == capitulo_identidade_id,
                "alias antigo de capítulo continua resolvendo",
            )

            identidade_disc_depois = banco.obter_identidade_conteudo(
                "disciplina", disciplina_identidade_id
            )
            identidade_top_depois = banco.obter_identidade_conteudo(
                "topico", topico_identidade_id
            )
            identidade_cap_depois = banco.obter_identidade_conteudo(
                "capitulo", capitulo_identidade_id
            )
            assert_true(
                identidade_disc_antes["chave_estavel"]
                == identidade_disc_depois["chave_estavel"],
                "renomear disciplina não altera sua identidade",
            )
            assert_true(
                identidade_top_antes["chave_estavel"]
                == identidade_top_depois["chave_estavel"],
                "renomear tópico não altera sua identidade",
            )
            assert_true(
                identidade_cap_antes["chave_estavel"]
                == identidade_cap_depois["chave_estavel"],
                "renomear capítulo não altera sua identidade",
            )
            assert_true(
                banco.resolver_topico_id_estrutural(
                    identidade_disc_depois["chave_estavel"],
                    identidade_top_depois["chave_estavel"],
                ) == topico_identidade_id,
                "conteúdo também pode ser localizado pelas chaves estáveis",
            )
            assert_true(
                not banco.adicionar_topico(
                    "Estrutura Smoke Renomeada", "Tópico Smoke"
                ),
                "alias histórico não pode ser reutilizado por outro tópico",
            )
            assert_true(
                banco.auditar_estrutura_conteudos()["ok"],
                "auditoria estrutural continua íntegra após renomeações",
            )

            # Direito Penal depende de uma árvore legal especial. Mesmo se o
            # rótulo visual de um título for alterado, parte, capítulos e
            # ordenação devem continuar ligados à mesma identidade.
            titulo_penal_canonico = "TÍTULO I – DOS CRIMES CONTRA A PESSOA"
            titulo_penal_id = banco.resolver_topico_id_estrutural(
                "Direito Penal", titulo_penal_canonico
            )
            assert_true(titulo_penal_id is not None, "título penal canônico resolvido")
            assert_true(
                banco.renomear_topico(
                    titulo_penal_id, "Crimes contra a Pessoa — exibição smoke"
                ),
                "título penal pode ter rótulo visual alterado",
            )
            assert_true(
                banco.resolver_topico_id_estrutural(
                    "Direito Penal", titulo_penal_canonico
                ) == titulo_penal_id,
                "nome legal anterior permanece como alias do título penal",
            )
            assert_true(
                banco.obter_parte_direito_penal(
                    "Crimes contra a Pessoa — exibição smoke"
                ) == "PARTE ESPECIAL",
                "parte penal é preservada pela identidade, não pelo texto atual",
            )
            assert_true(
                len(banco.listar_capitulos_topico(titulo_penal_id)) == 7,
                "capítulos oficiais sobrevivem à renomeação do título",
            )
            assert_true(
                banco.renomear_topico(titulo_penal_id, titulo_penal_canonico),
                "título penal restaurado após teste",
            )

            # Página Tópico: a identidade canônica do conteúdo precisa ser
            # recuperável independentemente da tela que abriu a página.
            with closing(banco.conectar()) as con_contexto:
                linha_topico = con_contexto.execute(
                    "SELECT id FROM topicos ORDER BY id LIMIT 1"
                ).fetchone()
            assert_true(linha_topico is not None, "banco possui tópico para teste")
            contexto_topico = banco.obter_contexto_topico(int(linha_topico[0]))
            assert_true(
                contexto_topico is not None
                and contexto_topico["topico_id"] == int(linha_topico[0])
                and bool(contexto_topico["disciplina_nome"]),
                "página Tópico recupera disciplina e identidade canônica"
            )

            # Biblioteca de Prompts IA: criação e atualização precisam
            # sobreviver ao fechamento da conexão, reproduzindo o ciclo real
            # de fechar e reabrir a janela.
            prompt_smoke_id = banco.criar_prompt_ia(
                "Prompt smoke",
                "Texto inicial do prompt smoke.",
                "Smoke"
            )
            prompt_smoke = banco.obter_prompt_ia(prompt_smoke_id)
            assert_true(
                prompt_smoke is not None
                and prompt_smoke["texto"] == "Texto inicial do prompt smoke.",
                "prompt IA persiste após criação"
            )
            atualizado_prompt = banco.atualizar_prompt_ia(
                prompt_smoke_id,
                "Prompt smoke atualizado",
                "Texto alterado e persistente.",
                "Smoke atualizado"
            )
            assert_true(atualizado_prompt, "prompt IA atualiza registro existente")
            with closing(sqlite3.connect(banco.CAMINHO_BANCO)) as con_prompt:
                linha_prompt = con_prompt.execute(
                    "SELECT nome, categoria, texto FROM prompts_ia WHERE id = ?",
                    (prompt_smoke_id,)
                ).fetchone()
            assert_true(
                linha_prompt == (
                    "Prompt smoke atualizado",
                    "Smoke atualizado",
                    "Texto alterado e persistente.",
                ),
                "alterações de prompt ficam gravadas no SQLite"
            )

            # Direito Penal: a migração precisa corrigir estruturas legadas,
            # remover divisões artificiais e criar os títulos/capítulos oficiais.
            with closing(banco.conectar()) as con, con:
                concurso_padrao = int(con.execute(
                    "SELECT id FROM concursos WHERE e_padrao = 1 ORDER BY id LIMIT 1"
                ).fetchone()[0])
                con.execute("INSERT OR IGNORE INTO disciplinas(nome) VALUES ('Direito Penal')")
                penal_id = int(con.execute(
                    "SELECT id FROM disciplinas WHERE nome = 'Direito Penal'"
                ).fetchone()[0])

                # Um alias antigo com histórico/configuração personalizada.
                alias_id = int(con.execute(
                    "INSERT INTO topicos(disciplina_id, nome) VALUES (?, 'Aplicação da Lei Penal')",
                    (penal_id,),
                ).lastrowid)
                con.execute(
                    "INSERT INTO revisoes(topico_id, data, questoes, acertos) VALUES (?, '2026-09-15', 10, 7)",
                    (alias_id,),
                )
                con.execute(
                    """INSERT INTO topico_concurso_importancia
                       (topico_id, concurso_id, importancia, incluido, pausado)
                       VALUES (?, ?, 8, 1, 0)""",
                    (alias_id, concurso_padrao),
                )

                penas_id = int(con.execute(
                    "SELECT id FROM topicos WHERE disciplina_id = ? AND nome = 'TÍTULO V – DAS PENAS'",
                    (penal_id,),
                ).fetchone()[0])
                con.execute(
                    "UPDATE topicos SET nome = 'Título V: Das penas' WHERE id = ?",
                    (penas_id,),
                )
                con.execute(
                    "UPDATE capitulos_topico SET nome = 'Capítulo I: Das penas' WHERE topico_id = ? AND ordem = 1",
                    (penas_id,),
                )

                dignidade_id = int(con.execute(
                    "SELECT id FROM topicos WHERE disciplina_id = ? AND nome = 'TÍTULO VI – DOS CRIMES CONTRA A DIGNIDADE SEXUAL'",
                    (penal_id,),
                ).fetchone()[0])
                con.execute(
                    "UPDATE topicos SET nome = 'Título VI: Dos crimes contra a dignidade sexual' WHERE id = ?",
                    (dignidade_id,),
                )
                con.execute("DELETE FROM capitulos_topico WHERE topico_id = ?", (dignidade_id,))
                for ordem, nome in enumerate((
                    'Capítulo I – Dos Crimes Contra a Liberdade Sexual',
                    'Capítulo I-A: Da exposição da intimidade sexual',
                    'Capítulo II – Dos Crimes Sexuais Contra Vulnerável',
                    'Capítulo III: Do assédio sexual',
                    'Capítulo IV: Disposições gerais',
                    'Capítulo V: Do lenocínio e do tráfico de pessoa para fim de prostituição ou outra forma de exploração sexual',
                    'Capítulo VI: Disposições gerais',
                    'Capítulo VII: Da divulgação de cena de estupro ou de cena de estupro de vulnerável, de cena de sexo ou de pornografia',
                ), start=1):
                    con.execute(
                        "INSERT INTO capitulos_topico(topico_id, nome, ordem) VALUES (?, ?, ?)",
                        (dignidade_id, nome, ordem),
                    )

                # Reabre a migração para simular um banco vindo de uma versão
                # anterior do VighnaStudy.
                con.execute(
                    "DELETE FROM migracoes WHERE nome = 'direito_penal_nomenclatura_oficial_v2'"
                )

            # A migração é executada na abertura seguinte, como acontecerá
            # quando o usuário instalar a atualização sobre o banco atual.
            banco.criar_banco()

            with closing(banco.conectar()) as con, con:
                penal_id = int(con.execute(
                    "SELECT id FROM disciplinas WHERE nome = 'Direito Penal'"
                ).fetchone()[0])
                titulos = con.execute(
                    "SELECT id, nome FROM topicos WHERE disciplina_id = ? ORDER BY id",
                    (penal_id,),
                ).fetchall()
                nomes_titulos = [linha[1] for linha in titulos]
                assert_true(len(titulos) == 20, "Direito Penal possui 20 títulos oficiais")
                nomes_ordenados = [linha[1] for linha in banco.listar_topicos_gerenciamento("Direito Penal")]
                assert_true(
                    nomes_ordenados == [titulo for titulo, _ in banco.ESTRUTURA_DIREITO_PENAL],
                    "Direito Penal usa nomenclatura e ordem oficiais de Parte Geral e Parte Especial",
                )
                total_capitulos = con.execute(
                    """SELECT COUNT(*) FROM capitulos_topico c
                       JOIN topicos t ON t.id = c.topico_id
                       WHERE t.disciplina_id = ?""",
                    (penal_id,),
                ).fetchone()[0]
                assert_true(total_capitulos == 56, "Direito Penal possui 56 capítulos oficiais")
                assert_true(
                    'Aplicação da Lei Penal' not in nomes_titulos,
                    "alias legado de Direito Penal é consolidado",
                )
                assert_true(
                    'TÍTULO XII – DOS CRIMES CONTRA O ESTADO DEMOCRÁTICO DE DIREITO' in nomes_titulos,
                    "Título XII é criado",
                )

                geral_i = int(con.execute(
                    "SELECT id FROM topicos WHERE disciplina_id = ? AND nome = 'TÍTULO I – DA APLICAÇÃO DA LEI PENAL'",
                    (penal_id,),
                ).fetchone()[0])
                assert_true(
                    con.execute("SELECT COUNT(*) FROM capitulos_topico WHERE topico_id = ?", (geral_i,)).fetchone()[0] == 0,
                    "Título I da Parte Geral não possui capítulos artificiais",
                )
                assert_true(
                    con.execute("SELECT COUNT(*) FROM revisoes WHERE topico_id = ?", (geral_i,)).fetchone()[0] == 1,
                    "histórico do tópico legado é preservado",
                )
                assert_true(
                    con.execute(
                        "SELECT importancia FROM topico_concurso_importancia WHERE topico_id = ? AND concurso_id = ?",
                        (geral_i, concurso_padrao),
                    ).fetchone()[0] == 8,
                    "importância personalizada do tópico legado é preservada",
                )

                penas_id = int(con.execute(
                    "SELECT id FROM topicos WHERE disciplina_id = ? AND nome = 'TÍTULO V – DAS PENAS'",
                    (penal_id,),
                ).fetchone()[0])
                capitulos_penas = [linha[0] for linha in con.execute(
                    "SELECT nome FROM capitulos_topico WHERE topico_id = ? ORDER BY ordem",
                    (penas_id,),
                ).fetchall()]
                assert_true(
                    capitulos_penas[0] == 'Capítulo I – Das Espécies de Pena'
                    and len(capitulos_penas) == 7,
                    "Título V da Parte Geral usa os sete capítulos corretos",
                )

                pessoa_id = int(con.execute(
                    "SELECT id FROM topicos WHERE disciplina_id = ? AND nome = 'TÍTULO I – DOS CRIMES CONTRA A PESSOA'",
                    (penal_id,),
                ).fetchone()[0])
                capitulos_pessoa = [linha[0] for linha in con.execute(
                    "SELECT nome FROM capitulos_topico WHERE topico_id = ? ORDER BY ordem",
                    (pessoa_id,),
                ).fetchall()]
                assert_true(
                    capitulos_pessoa[-1] == 'Capítulo VII – Dos Crimes Contra a Inviolabilidade dos Segredos'
                    and len(capitulos_pessoa) == 7,
                    "Crimes contra a pessoa inclui o Capítulo VII",
                )

                dignidade_id = int(con.execute(
                    "SELECT id FROM topicos WHERE disciplina_id = ? AND nome = 'TÍTULO VI – DOS CRIMES CONTRA A DIGNIDADE SEXUAL'",
                    (penal_id,),
                ).fetchone()[0])
                capitulos_dignidade = [linha[0] for linha in con.execute(
                    "SELECT nome FROM capitulos_topico WHERE topico_id = ? ORDER BY ordem",
                    (dignidade_id,),
                ).fetchall()]
                assert_true(
                    capitulos_dignidade == [
                        'Capítulo I – Dos Crimes Contra a Liberdade Sexual',
                        'Capítulo II – Dos Crimes Sexuais Contra Vulnerável',
                        'Capítulo III – Do Lenocínio e do Tráfico de Pessoas para Fim de Prostituição ou Outra Forma de Exploração Sexual',
                        'Capítulo IV – Do Ultraje Público ao Pudor',
                        'Capítulo V – Disposições Gerais',
                    ],
                    "Dignidade sexual segue a estrutura informada",
                )

                titulo_xii = int(con.execute(
                    "SELECT id FROM topicos WHERE disciplina_id = ? AND nome = 'TÍTULO XII – DOS CRIMES CONTRA O ESTADO DEMOCRÁTICO DE DIREITO'",
                    (penal_id,),
                ).fetchone()[0])
                assert_true(
                    con.execute("SELECT COUNT(*) FROM capitulos_topico WHERE topico_id = ?", (titulo_xii,)).fetchone()[0] == 6,
                    "Título XII possui seis capítulos",
                )

            with closing(banco.conectar()) as con, con:
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

            with closing(banco.conectar()) as con, con:
                concurso_id = int(con.execute(
                    "SELECT id FROM concursos WHERE e_padrao = 1 ORDER BY id LIMIT 1"
                ).fetchone()[0])
                disciplina_id = int(con.execute(
                    "SELECT id FROM disciplinas WHERE nome = ?",
                    (banco.CTB_NOME_OFICIAL,),
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
            pool_topico = banco.listar_questoes_resolucao(
                concurso_id,
                topico_id=topico_id,
                somente_ineditas=False,
                aleatorio=False,
            )
            assert_true(
                any(
                    item["id"] == qid_smoke
                    and item.get("capitulo_id") == capitulo_id
                    and item.get("capitulo") == "Capítulo Smoke"
                    for item in pool_topico
                ),
                "pool de estudo do tópico preserva capítulo para filtros da sessão",
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
            with closing(banco.conectar()) as con, con:
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
            assert_true(any(nome == banco.CTB_NOME_OFICIAL for _, nome in banco.listar_disciplinas(concurso_id)), "disciplina inicialmente ativa")
            banco.definir_disciplina_pausada(disciplina_id, True, concurso_id)
            assert_true(not any(nome == banco.CTB_NOME_OFICIAL for _, nome in banco.listar_disciplinas(concurso_id)), "disciplina desligada sai da operação")
            ger = banco.listar_disciplinas_gerenciamento(concurso_id)
            assert_true(any(i == disciplina_id and p for i, nome, p in ger), "disciplina desligada permanece administrável")
            assert_true(not banco.listar_questoes(concurso_id), "questões da disciplina desligada saem da operação")
            adm_q = banco.listar_questoes(
                concurso_id, incluir_inativas=True, incluir_topicos_pausados=True,
                incluir_disciplinas_pausadas=True
            )
            assert_true(any(q["id"] == qid_smoke and q["disciplina_pausada"] for q in adm_q), "questões da disciplina desligada permanecem administráveis")
            banco.definir_disciplina_pausada(disciplina_id, False, concurso_id)
            assert_true(any(nome == banco.CTB_NOME_OFICIAL for _, nome in banco.listar_disciplinas(concurso_id)), "disciplina reativada")

            # Banco mestre: detecção de duplicidade e edição/movimentação em lote.
            qid_duplicada = banco.criar_questao(
                topico_id,
                "Questão smoke de desligamento temporário?",
                [
                    {"letra": "A", "texto": "Correta", "correta": True},
                    {"letra": "B", "texto": "Distrator", "correta": False},
                ],
                explicacao="Duplicada smoke",
                capitulo_id=capitulo_id,
            )
            grupos_dup = banco.listar_grupos_questoes_duplicadas(concurso_id)
            assert_true(
                any({qid_smoke, qid_duplicada}.issubset(set(grupo["ids"])) for grupo in grupos_dup),
                "banco mestre detecta duplicidade por conteúdo completo",
            )
            atualizadas_lote = banco.atualizar_questoes_lote(
                [qid_smoke, qid_duplicada],
                {"dificuldade": "Difícil", "banca": "Smoke Banca"},
            )
            assert_true(atualizadas_lote == 2, "edição em lote atualiza duas questões")
            assert_true(
                banco.obter_questao(qid_duplicada)["dificuldade"] == "Difícil"
                and banco.obter_questao(qid_duplicada)["banca"] == "Smoke Banca",
                "metadados da edição em lote persistem",
            )

            with closing(banco.conectar()) as con, con:
                destino_id = int(con.execute(
                    "INSERT INTO topicos(disciplina_id, nome) VALUES (?, 'Destino lote smoke')",
                    (disciplina_id,),
                ).lastrowid)
                con.execute(
                    """INSERT INTO topico_concurso_importancia
                       (topico_id, concurso_id, importancia, incluido)
                       VALUES (?, ?, 3, 1)""",
                    (destino_id, concurso_id),
                )
            movidas = banco.atualizar_questoes_lote(
                [qid_duplicada],
                {"topico_id": destino_id, "capitulo_id": None},
            )
            assert_true(movidas == 1, "movimentação em lote atualiza classificação")
            assert_true(
                banco.obter_questao(qid_duplicada)["topico_id"] == destino_id
                and banco.obter_questao(qid_duplicada)["capitulo_id"] is None,
                "movimentação preserva questão e troca destino",
            )

            # Motor de Sessão Unificado V1: congela a fila, registra a origem
            # e diferencia apresentada/respondida/pulada/não alcançada.
            qid_motor_3 = banco.criar_questao(
                topico_id,
                "Questão smoke do motor unificado 3?",
                [
                    {"letra": "A", "texto": "Correta", "correta": True},
                    {"letra": "B", "texto": "Distrator", "correta": False},
                ],
                dificuldade="Média",
                capitulo_id=capitulo_id,
            )
            qid_motor_4 = banco.criar_questao(
                topico_id,
                "Questão smoke do motor unificado 4?",
                [
                    {"letra": "A", "texto": "Correta", "correta": True},
                    {"letra": "B", "texto": "Distrator", "correta": False},
                ],
                dificuldade="Difícil",
                capitulo_id=capitulo_id,
            )
            fila_motor = [
                {"id": qid_smoke, "motivo_inteligente": "smoke 1"},
                {"id": qid_duplicada, "motivo_inteligente": "smoke 2"},
                {"id": qid_motor_3, "motivo_inteligente": "smoke 3"},
                {"id": qid_motor_4, "motivo_inteligente": "smoke 4"},
            ]
            sessao_motor = banco.iniciar_sessao_questoes(
                concurso_id,
                "Sessão manual smoke",
                len(fila_motor),
                origem="manual",
                contexto={"origem_teste": "smoke"},
                versao_motor="sessao_unificado_v1",
            )
            assert_true(
                banco.registrar_fila_sessao_questoes(sessao_motor, fila_motor) == 4,
                "motor unificado congela toda a fila",
            )
            itens_motor = banco.obter_itens_sessao_questoes(sessao_motor)
            assert_true(
                len(itens_motor) == 4
                and all(item["estado"] == "planejada" for item in itens_motor),
                "fila nasce integralmente planejada",
            )
            assert_true(
                itens_motor[0]["capitulo"] == "Capítulo Smoke"
                and itens_motor[0]["dificuldade"] == "Difícil",
                "snapshot da fila preserva classificação e dificuldade",
            )

            item_1 = banco.marcar_item_sessao_apresentado(
                sessao_motor, 1, qid_smoke
            )
            tentativa_1 = banco.registrar_tentativa_questao(
                sessao_motor,
                qid_smoke,
                concurso_id,
                alternativa_marcada="A",
                tempo_segundos=17,
                item_sessao_id=item_1,
            )
            assert_true(
                tentativa_1["correta"] is True
                and tentativa_1["item_sessao_id"] == item_1,
                "tentativa fica vinculada à apresentação correta",
            )

            item_2 = banco.marcar_item_sessao_apresentado(
                sessao_motor, 2, qid_duplicada
            )
            banco.registrar_tentativa_questao(
                sessao_motor,
                qid_duplicada,
                concurso_id,
                alternativa_marcada=None,
                tempo_segundos=9,
                item_sessao_id=item_2,
            )
            banco.marcar_item_sessao_apresentado(
                sessao_motor, 3, qid_motor_3
            )
            banco.encerrar_sessao_questoes(sessao_motor, concluida=False)

            itens_motor = banco.obter_itens_sessao_questoes(sessao_motor)
            estados_motor = [item["estado"] for item in itens_motor]
            assert_true(
                estados_motor == [
                    "respondida",
                    "pulada",
                    "nao_respondida",
                    "nao_alcancada",
                ],
                "motor distingue resposta, pulo, apresentação sem resposta e item não alcançado",
            )
            resumo_motor = banco.obter_resumo_sessao_questoes(sessao_motor)
            assert_true(
                resumo_motor["origem"] == "manual"
                and resumo_motor["versao_motor"] == "sessao_unificado_v1"
                and resumo_motor["planejadas"] == 4
                and resumo_motor["apresentadas"] == 3
                and resumo_motor["respondidas"] == 1
                and resumo_motor["puladas"] == 1
                and resumo_motor["nao_respondidas"] == 1
                and resumo_motor["nao_alcancadas"] == 1,
                "resumo unificado expõe a telemetria completa da sessão",
            )
            with closing(banco.conectar()) as con, con:
                colunas_sessao = {
                    r[1] for r in con.execute(
                        "PRAGMA table_info(sessoes_questoes)"
                    ).fetchall()
                }
                colunas_tentativas = {
                    r[1] for r in con.execute(
                        "PRAGMA table_info(tentativas_questoes)"
                    ).fetchall()
                }
                assert_true(
                    {"origem", "contexto_json", "versao_motor"}.issubset(colunas_sessao),
                    "sessão possui origem e contexto padronizados",
                )
                assert_true(
                    "item_sessao_id" in colunas_tentativas,
                    "tentativa referencia o item apresentado",
                )

            rec = MotorRecomendacaoV5(
                fila=[{
                    "topico_id": topico_id, "disciplina": "CTB", "topico": "Habilitação Smoke",
                    "score": 80, "nivel": "Alta", "proxima": "2026-09-15",
                    "percentual": 60, "revisoes": 1, "importancia": 5,
                }],
                adaptativas=[{
                    "topico_id": topico_id,
                    "questoes_disponiveis": 30,
                    "motivo_principal": "domínio frágil",
                    "dominio": 49,
                    "nivel_dominio": "Em desenvolvimento",
                    "desempenho_base": 78,
                    "desempenho_recente": 60,
                    "tentativas_historicas": 10,
                    "dias_desde_ultima": 22,
                    "importancia": 5,
                    "criticas": 1,
                    "recorrentes": 1,
                    "recuperacao": 0,
                    "cobertura": 45,
                }],
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
            evidencias = {item.get("chave"): item for item in rec.get("evidencias_objetivas", [])}
            assert_true("dominio" in evidencias, "recomendação expõe domínio concreto")
            assert_true("queda" in evidencias and "18" in evidencias["queda"]["valor"], "recomendação expõe queda recente")
            assert_true("sem_pratica" in evidencias and "22" in evidencias["sem_pratica"]["valor"], "recomendação expõe tempo sem prática")
            assert_true("importancia" in evidencias, "recomendação expõe importância")
            assert_true(bool(rec.get("resumo_decisao")), "recomendação possui resumo factual")
            assert_true(any(item.get("selecionado") for item in rec.get("ranking_resumo", [])), "ranking marca candidato selecionado")

            cache = CacheAnalitico()
            contador = {"n": 0}
            def carregar():
                contador["n"] += 1
                return 42
            assert_true(cache.obter("x", carregar) == 42, "cache primeira leitura")
            assert_true(cache.obter("x", carregar) == 42 and contador["n"] == 1, "cache reaproveita")

            # Calibração: cinco sessões reais de 20 min com 10 respostas cada.
            agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with closing(banco.conectar()) as con, con:
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
            with closing(banco.conectar()) as con, con:
                con.execute("INSERT OR IGNORE INTO controle_topico(topico_id) VALUES (?)", (topico_id,))
                con.execute("UPDATE controle_topico SET proxima_revisao = ? WHERE topico_id = ?", (prevista.isoformat(), topico_id))
            banco.registrar_revisao(
                topico_id, hoje_data.isoformat(), 10, 8, "smoke evolução",
                proxima_revisao=(hoje_data + timedelta(days=7)).isoformat(),
                concurso_id=concurso_id,
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
            assert_true(
                hist["temporal_snapshot"]["topics"],
                "tópicos presentes na análise temporal",
            )
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
            with closing(banco.conectar()) as con:
                linha_exp = con.execute(
                    "SELECT explicacao_json FROM recomendacoes_estudo WHERE id = ?",
                    (rid,),
                ).fetchone()
            dados_exp = json.loads(linha_exp[0]) if linha_exp and linha_exp[0] else {}
            assert_true(bool(dados_exp.get("evidencias_objetivas")), "histórico preserva evidências da recomendação")
            assert_true(bool(dados_exp.get("criterio_selecao_v5")), "histórico preserva critério do Motor V5")
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

            # No Windows, qualquer handle SQLite ainda aguardando coleta pode
            # impedir a remoção imediata do diretório temporário. Restaura o
            # banco real antes da limpeza e força a coleta dos objetos locais.
            banco.CAMINHO_BANCO = original
            gc.collect()

    finally:
        banco.CAMINHO_BANCO = original
        gc.collect()
    print(f"VighnaStudy {VIGHNA_VERSION}: testes smoke OK")


if __name__ == "__main__":
    try:
        main()
    finally:
        pass
