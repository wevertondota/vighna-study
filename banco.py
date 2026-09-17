import sqlite3
import sys
import random
import json
import math
import re
import statistics
import unicodedata
from datetime import date, datetime, timedelta
from pathlib import Path


if getattr(sys, "frozen", False):
    PASTA_APLICACAO = Path(sys.executable).resolve().parent
else:
    PASTA_APLICACAO = Path(__file__).resolve().parent

CAMINHO_BANCO = PASTA_APLICACAO / "estudos.db"


def conectar():
    conexao = sqlite3.connect(CAMINHO_BANCO, timeout=10)
    conexao.execute("PRAGMA foreign_keys = ON")
    conexao.execute("PRAGMA busy_timeout = 5000")
    conexao.execute("PRAGMA temp_store = MEMORY")
    return conexao


def criar_banco():
    with conectar() as conexao:
        # Ajustes seguros para uso local: WAL reduz bloqueios entre leituras e
        # escritas curtas; NORMAL evita sincronizações excessivas sem abrir mão
        # da durabilidade esperada do SQLite em desktop.
        try:
            conexao.execute("PRAGMA journal_mode = WAL")
            conexao.execute("PRAGMA synchronous = NORMAL")
        except sqlite3.DatabaseError:
            pass

        conexao.execute("""
            CREATE TABLE IF NOT EXISTS disciplinas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE
            )
        """)

        conexao.execute("""
            CREATE TABLE IF NOT EXISTS topicos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                disciplina_id INTEGER NOT NULL,
                nome TEXT NOT NULL,
                UNIQUE (disciplina_id, nome),
                FOREIGN KEY (disciplina_id)
                    REFERENCES disciplinas(id)
                    ON DELETE CASCADE
            )
        """)

        conexao.execute("""
            CREATE TABLE IF NOT EXISTS revisoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topico_id INTEGER NOT NULL,
                data TEXT NOT NULL,
                questoes INTEGER NOT NULL,
                acertos INTEGER NOT NULL,
                observacao TEXT,
                texto_erros TEXT,
                continuacao TEXT,
                FOREIGN KEY (topico_id)
                    REFERENCES topicos(id)
                    ON DELETE CASCADE
            )
        """)

        colunas_revisoes = {
            linha[1]
            for linha in conexao.execute(
                "PRAGMA table_info(revisoes)"
            ).fetchall()
        }

        if "origem" not in colunas_revisoes:
            conexao.execute(
                """
                ALTER TABLE revisoes
                ADD COLUMN origem TEXT NOT NULL DEFAULT 'manual'
                """
            )

        if "confianca" not in colunas_revisoes:
            conexao.execute(
                """
                ALTER TABLE revisoes
                ADD COLUMN confianca TEXT
                """
            )

        if "sessao_questoes_id" not in colunas_revisoes:
            conexao.execute(
                """
                ALTER TABLE revisoes
                ADD COLUMN sessao_questoes_id INTEGER
                """
            )

        # Histórico preciso de prazo: registros antigos permanecem explicitamente
        # sem validade histórica para não inferir datas que o banco não guardava.
        for coluna, definicao in (
            ("prevista_para", "TEXT"),
            ("realizada_em", "TEXT"),
            ("dias_atraso", "INTEGER"),
            ("prazo_historico_valido", "INTEGER NOT NULL DEFAULT 0"),
        ):
            if coluna not in colunas_revisoes:
                conexao.execute(
                    f"ALTER TABLE revisoes ADD COLUMN {coluna} {definicao}"
                )

        conexao.execute("""
            CREATE TABLE IF NOT EXISTS controle_topico (
                topico_id INTEGER PRIMARY KEY,
                revisoes_iniciais INTEGER NOT NULL DEFAULT 0,
                proxima_revisao TEXT,
                percentual_inicial REAL,
                importancia INTEGER NOT NULL DEFAULT 3,
                observacao_inicial TEXT,
                texto_erros_inicial TEXT,
                continuacao_inicial TEXT,
                FOREIGN KEY (topico_id)
                    REFERENCES topicos(id)
                    ON DELETE CASCADE
            )
        """)

        colunas_controle = {
            linha[1]
            for linha in conexao.execute(
                "PRAGMA table_info(controle_topico)"
            ).fetchall()
        }

        if "importancia" not in colunas_controle:
            conexao.execute(
                """
                ALTER TABLE controle_topico
                ADD COLUMN importancia INTEGER NOT NULL DEFAULT 3
                """
            )

        conexao.execute("""
            CREATE TABLE IF NOT EXISTS configuracoes (
                chave TEXT PRIMARY KEY,
                valor TEXT NOT NULL
            )
        """)

        configuracoes_padrao = {
            "usar_importancia_fila": "1",
            "aplicar_penalizacao_queda": "1",
            "questoes_revisao_min_registro": "5",
            "questoes_revisao_min_agendamento": "10",
            "mostrar_modo_um_clique": "1",
            "calibracao_automatica_foco": "1",
            "aprender_decisoes_estudar_agora": "1",
            "motor_v5_peso_urgencia": "45",
            "motor_v5_peso_necessidade": "40",
            "motor_v5_peso_momento": "15",
            "motor_v5_proteger_revisoes_vencidas": "1",
        }

        for chave, valor in configuracoes_padrao.items():
            conexao.execute(
                """
                INSERT OR IGNORE INTO configuracoes (chave, valor)
                VALUES (?, ?)
                """,
                (chave, valor)
            )

        conexao.execute("""
            CREATE TABLE IF NOT EXISTS prompts_ia (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                categoria TEXT,
                texto TEXT NOT NULL,
                criado_em TEXT NOT NULL
                    DEFAULT (datetime('now', 'localtime')),
                atualizado_em TEXT NOT NULL
                    DEFAULT (datetime('now', 'localtime'))
            )
        """)

        conexao.execute("""
            CREATE INDEX IF NOT EXISTS idx_prompts_ia_nome
            ON prompts_ia(nome COLLATE NOCASE)
        """)

        conexao.execute("""
            CREATE INDEX IF NOT EXISTS idx_prompts_ia_categoria
            ON prompts_ia(categoria COLLATE NOCASE)
        """)

        # ------------------------------------------------------
        # PAUSA & DESAFIOS
        # ------------------------------------------------------

        conexao.execute("""
            CREATE TABLE IF NOT EXISTS jogos_resultados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                jogo TEXT NOT NULL,
                pontuacao INTEGER NOT NULL DEFAULT 0,
                nivel INTEGER,
                duracao_segundos INTEGER,
                movimentos INTEGER,
                criado_em TEXT NOT NULL
                    DEFAULT (datetime('now', 'localtime'))
            )
        """)

        conexao.execute("""
            CREATE INDEX IF NOT EXISTS idx_jogos_resultados_jogo_data
            ON jogos_resultados(jogo, criado_em DESC)
        """)

        # ------------------------------------------------------
        # MODO FOCO
        # ------------------------------------------------------

        conexao.execute("""
            CREATE TABLE IF NOT EXISTS sessoes_foco (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inicio TEXT NOT NULL,
                fim TEXT,
                duracao_planejada INTEGER NOT NULL DEFAULT 0,
                duracao_efetiva INTEGER NOT NULL DEFAULT 0,
                disciplina_id INTEGER,
                topico_id INTEGER,
                disciplina_nome TEXT,
                topico_nome TEXT,
                tipo_atividade TEXT NOT NULL DEFAULT 'Estudo livre',
                concluida INTEGER NOT NULL DEFAULT 0,
                observacao TEXT,
                criado_em TEXT NOT NULL
                    DEFAULT (datetime('now', 'localtime')),
                FOREIGN KEY (disciplina_id)
                    REFERENCES disciplinas(id)
                    ON DELETE SET NULL,
                FOREIGN KEY (topico_id)
                    REFERENCES topicos(id)
                    ON DELETE SET NULL
            )
        """)

        colunas_sessoes_foco = {
            linha[1]
            for linha in conexao.execute(
                "PRAGMA table_info(sessoes_foco)"
            ).fetchall()
        }

        if "meta_questoes" not in colunas_sessoes_foco:
            conexao.execute(
                """
                ALTER TABLE sessoes_foco
                ADD COLUMN meta_questoes INTEGER NOT NULL DEFAULT 0
                """
            )

        if "origem" not in colunas_sessoes_foco:
            conexao.execute(
                """
                ALTER TABLE sessoes_foco
                ADD COLUMN origem TEXT
                """
            )

        if "plano_chave" not in colunas_sessoes_foco:
            conexao.execute(
                """
                ALTER TABLE sessoes_foco
                ADD COLUMN plano_chave TEXT
                """
            )

        conexao.execute("""
            CREATE INDEX IF NOT EXISTS idx_sessoes_foco_inicio
            ON sessoes_foco(inicio DESC)
        """)

        conexao.execute("""
            CREATE INDEX IF NOT EXISTS idx_sessoes_foco_topico
            ON sessoes_foco(topico_id, inicio DESC)
        """)

        conexao.execute("""
            CREATE TABLE IF NOT EXISTS migracoes (
                nome TEXT PRIMARY KEY,
                executada_em TEXT NOT NULL
            )
        """)

        disciplinas_padrao = [
            "Geral",
            "Direito Penal",
            "Direito Administrativo",
            "CTB",
            "Português",
            "Matemática",
            "Informática"
        ]

        # Em bancos novos, cria a estrutura inicial.
        # Depois disso, as disciplinas passam a ser totalmente
        # gerenciadas pelo usuário e uma disciplina excluída não
        # será recriada automaticamente ao abrir o programa.
        quantidade_disciplinas = conexao.execute(
            """
            SELECT COUNT(*)
            FROM disciplinas
            """
        ).fetchone()[0]

        if quantidade_disciplinas == 0:
            for nome in disciplinas_padrao:
                conexao.execute(
                    """
                    INSERT OR IGNORE INTO disciplinas (nome)
                    VALUES (?)
                    """,
                    (nome,)
                )

        # ------------------------------------------------------
        # PERFIS DE CONCURSO
        # ------------------------------------------------------

        conexao.execute("""
            CREATE TABLE IF NOT EXISTS concursos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE,
                e_padrao INTEGER NOT NULL DEFAULT 0
            )
        """)

        conexao.execute("""
            CREATE TABLE IF NOT EXISTS topico_concurso_importancia (
                topico_id INTEGER NOT NULL,
                concurso_id INTEGER NOT NULL,
                importancia INTEGER NOT NULL DEFAULT 3,
                incluido INTEGER NOT NULL DEFAULT 1,
                pausado INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (
                    topico_id,
                    concurso_id
                ),
                FOREIGN KEY (topico_id)
                    REFERENCES topicos(id)
                    ON DELETE CASCADE,
                FOREIGN KEY (concurso_id)
                    REFERENCES concursos(id)
                    ON DELETE CASCADE
            )
        """)

        # Capítulos são conteúdos internos de um tópico (por exemplo, os
        # capítulos de um Título do Código Penal). Eles têm configuração
        # própria por perfil, mas não substituem o tópico pai na agenda.
        conexao.execute("""
            CREATE TABLE IF NOT EXISTS capitulos_topico (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topico_id INTEGER NOT NULL,
                nome TEXT NOT NULL,
                ordem INTEGER NOT NULL DEFAULT 0,
                UNIQUE (topico_id, nome),
                FOREIGN KEY (topico_id)
                    REFERENCES topicos(id)
                    ON DELETE CASCADE
            )
        """)

        conexao.execute("""
            CREATE TABLE IF NOT EXISTS capitulo_concurso_config (
                capitulo_id INTEGER NOT NULL,
                concurso_id INTEGER NOT NULL,
                dificuldade INTEGER NOT NULL DEFAULT 3,
                pausado INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (capitulo_id, concurso_id),
                FOREIGN KEY (capitulo_id)
                    REFERENCES capitulos_topico(id)
                    ON DELETE CASCADE,
                FOREIGN KEY (concurso_id)
                    REFERENCES concursos(id)
                    ON DELETE CASCADE
            )
        """)

        colunas_topico_concurso = {
            linha[1]
            for linha in conexao.execute(
                "PRAGMA table_info(topico_concurso_importancia)"
            ).fetchall()
        }

        if "incluido" not in colunas_topico_concurso:
            conexao.execute(
                """
                ALTER TABLE topico_concurso_importancia
                ADD COLUMN incluido INTEGER NOT NULL DEFAULT 1
                """
            )

        if "pausado" not in colunas_topico_concurso:
            conexao.execute(
                """
                ALTER TABLE topico_concurso_importancia
                ADD COLUMN pausado INTEGER NOT NULL DEFAULT 0
                """
            )

        conexao.execute("""
            CREATE TABLE IF NOT EXISTS disciplina_concurso_inclusao (
                disciplina_id INTEGER NOT NULL,
                concurso_id INTEGER NOT NULL,
                incluido INTEGER NOT NULL DEFAULT 1,
                PRIMARY KEY (
                    disciplina_id,
                    concurso_id
                ),
                FOREIGN KEY (disciplina_id)
                    REFERENCES disciplinas(id)
                    ON DELETE CASCADE,
                FOREIGN KEY (concurso_id)
                    REFERENCES concursos(id)
                    ON DELETE CASCADE
            )
        """)

        colunas_disciplina_concurso = {
            linha[1]
            for linha in conexao.execute(
                "PRAGMA table_info(disciplina_concurso_inclusao)"
            ).fetchall()
        }

        if "pausado" not in colunas_disciplina_concurso:
            conexao.execute(
                """
                ALTER TABLE disciplina_concurso_inclusao
                ADD COLUMN pausado INTEGER NOT NULL DEFAULT 0
                """
            )

        # ------------------------------------------------------
        # BANCO DE QUESTÕES
        # ------------------------------------------------------

        conexao.execute("""
            CREATE TABLE IF NOT EXISTS questoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topico_id INTEGER NOT NULL,
                capitulo_id INTEGER,
                enunciado TEXT NOT NULL,
                explicacao TEXT,
                banca TEXT,
                ano INTEGER,
                fonte TEXT,
                dificuldade TEXT,
                ativa INTEGER NOT NULL DEFAULT 1,
                criado_em TEXT NOT NULL DEFAULT (
                    datetime('now', 'localtime')
                ),
                atualizado_em TEXT NOT NULL DEFAULT (
                    datetime('now', 'localtime')
                ),
                FOREIGN KEY (topico_id)
                    REFERENCES topicos(id)
                    ON DELETE CASCADE,
                FOREIGN KEY (capitulo_id)
                    REFERENCES capitulos_topico(id)
                    ON DELETE SET NULL
            )
        """)

        colunas_questoes = {
            linha[1]
            for linha in conexao.execute(
                "PRAGMA table_info(questoes)"
            ).fetchall()
        }

        if "capitulo_id" not in colunas_questoes:
            conexao.execute(
                """
                ALTER TABLE questoes
                ADD COLUMN capitulo_id INTEGER
                """
            )

        if "excluida" not in colunas_questoes:
            conexao.execute(
                """
                ALTER TABLE questoes
                ADD COLUMN excluida INTEGER NOT NULL DEFAULT 0
                """
            )

        if "excluida_em" not in colunas_questoes:
            conexao.execute(
                """
                ALTER TABLE questoes
                ADD COLUMN excluida_em TEXT
                """
            )

        if "analise_pendente" not in colunas_questoes:
            conexao.execute(
                """
                ALTER TABLE questoes
                ADD COLUMN analise_pendente INTEGER NOT NULL DEFAULT 0
                """
            )

        if "analise_solicitada_em" not in colunas_questoes:
            conexao.execute(
                """
                ALTER TABLE questoes
                ADD COLUMN analise_solicitada_em TEXT
                """
            )

        conexao.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_questoes_analise_pendente
            ON questoes(analise_pendente, id)
            """
        )

        conexao.execute("""
            CREATE TABLE IF NOT EXISTS alternativas_questoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                questao_id INTEGER NOT NULL,
                letra TEXT NOT NULL,
                texto TEXT NOT NULL,
                correta INTEGER NOT NULL DEFAULT 0,
                ordem INTEGER NOT NULL,
                UNIQUE (
                    questao_id,
                    letra
                ),
                FOREIGN KEY (questao_id)
                    REFERENCES questoes(id)
                    ON DELETE CASCADE
            )
        """)

        # Estrutura criada desde a fundação para que o resolvedor futuro
        # possa registrar sessões e tentativas sem redesenhar o banco.
        conexao.execute("""
            CREATE TABLE IF NOT EXISTS sessoes_questoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                concurso_id INTEGER,
                iniciado_em TEXT NOT NULL,
                encerrado_em TEXT,
                modo TEXT,
                objetivo INTEGER,
                concluida INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (concurso_id)
                    REFERENCES concursos(id)
                    ON DELETE SET NULL
            )
        """)

        # ------------------------------------------------------
        # EFETIVIDADE E CALIBRAÇÃO DAS SESSÕES
        # ------------------------------------------------------

        conexao.execute("""
            CREATE TABLE IF NOT EXISTS foco_questoes (
                sessao_foco_id INTEGER NOT NULL,
                sessao_questoes_id INTEGER NOT NULL,
                criado_em TEXT NOT NULL
                    DEFAULT (datetime('now', 'localtime')),
                PRIMARY KEY (sessao_foco_id, sessao_questoes_id),
                FOREIGN KEY (sessao_foco_id)
                    REFERENCES sessoes_foco(id)
                    ON DELETE CASCADE,
                FOREIGN KEY (sessao_questoes_id)
                    REFERENCES sessoes_questoes(id)
                    ON DELETE CASCADE
            )
        """)

        conexao.execute("""
            CREATE INDEX IF NOT EXISTS idx_foco_questoes_questoes
            ON foco_questoes(sessao_questoes_id)
        """)

        conexao.execute("""
            CREATE TABLE IF NOT EXISTS efetividade_sessoes (
                sessao_id INTEGER PRIMARY KEY,
                concurso_id INTEGER,
                modo TEXT,
                escopo TEXT,
                criado_em TEXT NOT NULL
                    DEFAULT (datetime('now', 'localtime')),
                finalizado_em TEXT,
                concluida INTEGER NOT NULL DEFAULT 0,
                topicos INTEGER NOT NULL DEFAULT 0,
                respostas INTEGER NOT NULL DEFAULT 0,
                acertos INTEGER NOT NULL DEFAULT 0,
                desempenho REAL,
                tempo_segundos INTEGER NOT NULL DEFAULT 0,
                dominio_medio_antes REAL,
                dominio_medio_depois REAL,
                cobertura_media_antes REAL,
                cobertura_media_depois REAL,
                recorrentes_antes INTEGER NOT NULL DEFAULT 0,
                recorrentes_depois INTEGER NOT NULL DEFAULT 0,
                criticas_antes INTEGER NOT NULL DEFAULT 0,
                criticas_depois INTEGER NOT NULL DEFAULT 0,
                estrategia_json TEXT,
                versao_algoritmo TEXT NOT NULL DEFAULT 'efetividade_v1',
                FOREIGN KEY (sessao_id)
                    REFERENCES sessoes_questoes(id)
                    ON DELETE CASCADE,
                FOREIGN KEY (concurso_id)
                    REFERENCES concursos(id)
                    ON DELETE SET NULL
            )
        """)

        conexao.execute("""
            CREATE TABLE IF NOT EXISTS efetividade_topicos_sessao (
                sessao_id INTEGER NOT NULL,
                topico_id INTEGER,
                disciplina_snapshot TEXT,
                topico_snapshot TEXT,
                motivo_principal TEXT,
                motivo_detalhado TEXT,
                prioridade_adaptativa REAL,
                planejadas INTEGER NOT NULL DEFAULT 0,
                respostas INTEGER NOT NULL DEFAULT 0,
                acertos INTEGER NOT NULL DEFAULT 0,
                tempo_segundos INTEGER NOT NULL DEFAULT 0,
                dominio_antes REAL,
                dominio_depois REAL,
                cobertura_antes REAL,
                cobertura_depois REAL,
                recorrentes_antes INTEGER NOT NULL DEFAULT 0,
                recorrentes_depois INTEGER NOT NULL DEFAULT 0,
                criticas_antes INTEGER NOT NULL DEFAULT 0,
                criticas_depois INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (
                    sessao_id,
                    topico_id
                ),
                FOREIGN KEY (sessao_id)
                    REFERENCES sessoes_questoes(id)
                    ON DELETE CASCADE,
                FOREIGN KEY (topico_id)
                    REFERENCES topicos(id)
                    ON DELETE SET NULL
            )
        """)

        conexao.execute("""
            CREATE INDEX IF NOT EXISTS idx_efetividade_sessoes_concurso
            ON efetividade_sessoes(
                concurso_id,
                criado_em
            )
        """)

        conexao.execute("""
            CREATE INDEX IF NOT EXISTS idx_efetividade_topicos_topico
            ON efetividade_topicos_sessao(
                topico_id,
                sessao_id
            )
        """)

        conexao.execute("""
            CREATE TABLE IF NOT EXISTS simulados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sessao_id INTEGER NOT NULL UNIQUE,
                concurso_id INTEGER,
                tipo TEXT NOT NULL,
                tempo_limite_minutos INTEGER NOT NULL DEFAULT 0,
                preferir_ineditas INTEGER NOT NULL DEFAULT 1,
                configuracao_json TEXT,
                criado_em TEXT NOT NULL
                    DEFAULT (datetime('now', 'localtime')),
                FOREIGN KEY (sessao_id)
                    REFERENCES sessoes_questoes(id)
                    ON DELETE CASCADE,
                FOREIGN KEY (concurso_id)
                    REFERENCES concursos(id)
                    ON DELETE SET NULL
            )
        """)

        conexao.execute("""
            CREATE INDEX IF NOT EXISTS idx_simulados_concurso
            ON simulados(
                concurso_id,
                criado_em
            )
        """)

        conexao.execute("""
            CREATE TABLE IF NOT EXISTS tentativas_questoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sessao_id INTEGER,
                questao_id INTEGER,
                concurso_id INTEGER,
                respondida_em TEXT NOT NULL,
                alternativa_marcada TEXT,
                correta INTEGER,
                marcada_duvida INTEGER NOT NULL DEFAULT 0,
                tempo_segundos INTEGER,
                FOREIGN KEY (sessao_id)
                    REFERENCES sessoes_questoes(id)
                    ON DELETE SET NULL,
                FOREIGN KEY (questao_id)
                    REFERENCES questoes(id)
                    ON DELETE SET NULL,
                FOREIGN KEY (concurso_id)
                    REFERENCES concursos(id)
                    ON DELETE SET NULL
            )
        """)

        colunas_tentativas = {
            linha[1]
            for linha in conexao.execute(
                "PRAGMA table_info(tentativas_questoes)"
            ).fetchall()
        }

        if "revisao_id" not in colunas_tentativas:
            conexao.execute(
                """
                ALTER TABLE tentativas_questoes
                ADD COLUMN revisao_id INTEGER
                """
            )

        # ------------------------------------------------------
        # INTEGRIDADE HISTÓRICA DAS TENTATIVAS
        # ------------------------------------------------------

        colunas_snapshot = {
            "questao_id_snapshot": "INTEGER",
            "topico_id_snapshot": "INTEGER",
            "disciplina_id_snapshot": "INTEGER",
            "disciplina_snapshot": "TEXT",
            "topico_snapshot": "TEXT",
            "enunciado_snapshot": "TEXT",
            "alternativas_snapshot": "TEXT",
            "gabarito_snapshot": "TEXT",
            "explicacao_snapshot": "TEXT",
            "banca_snapshot": "TEXT",
            "ano_snapshot": "INTEGER",
            "fonte_snapshot": "TEXT",
            "dificuldade_snapshot": "TEXT",
            "snapshot_origem": "TEXT",
        }

        for nome_coluna, tipo_coluna in colunas_snapshot.items():
            if nome_coluna not in colunas_tentativas:
                conexao.execute(
                    f"""
                    ALTER TABLE tentativas_questoes
                    ADD COLUMN {nome_coluna} {tipo_coluna}
                    """
                )

        conexao.execute("""
            CREATE INDEX IF NOT EXISTS idx_tentativas_questao_snapshot
            ON tentativas_questoes(questao_id_snapshot)
        """)

        conexao.execute("""
            CREATE INDEX IF NOT EXISTS idx_tentativas_topico_snapshot
            ON tentativas_questoes(topico_id_snapshot)
        """)

        migracao_snapshot = conexao.execute(
            """
            SELECT 1
            FROM migracoes
            WHERE nome = 'tentativas_snapshot_v1'
            """
        ).fetchone()

        if migracao_snapshot is None:
            # Tentativas anteriores à criação do snapshot não possuem uma
            # fotografia verdadeira do momento da resposta. Para impedir
            # perda futura caso a questão seja arquivada/movida, congelamos
            # a versão que existe AGORA e marcamos explicitamente como
            # "migrado". A interface informa essa diferença ao usuário.
            questoes_legadas = conexao.execute(
                """
                SELECT DISTINCT
                    q.id,
                    q.topico_id,
                    d.id,
                    d.nome,
                    t.nome,
                    q.enunciado,
                    q.explicacao,
                    q.banca,
                    q.ano,
                    q.fonte,
                    q.dificuldade
                FROM tentativas_questoes tq
                JOIN questoes q
                    ON q.id = tq.questao_id
                JOIN topicos t
                    ON t.id = q.topico_id
                JOIN disciplinas d
                    ON d.id = t.disciplina_id
                WHERE
                    tq.enunciado_snapshot IS NULL
                """
            ).fetchall()

            for questao in questoes_legadas:
                alternativas = conexao.execute(
                    """
                    SELECT
                        letra,
                        texto,
                        correta,
                        ordem
                    FROM alternativas_questoes
                    WHERE questao_id = ?
                    ORDER BY ordem, letra
                    """,
                    (
                        questao[0],
                    )
                ).fetchall()

                alternativas_serializadas = [
                    {
                        "letra": item[0],
                        "texto": item[1],
                        "correta": bool(
                            item[2]
                        ),
                        "ordem": int(
                            item[3]
                        ),
                    }
                    for item in alternativas
                ]

                gabarito = next(
                    (
                        item[
                            "letra"
                        ]
                        for item in alternativas_serializadas
                        if item[
                            "correta"
                        ]
                    ),
                    None
                )

                conexao.execute(
                    """
                    UPDATE tentativas_questoes
                    SET
                        questao_id_snapshot = ?,
                        topico_id_snapshot = ?,
                        disciplina_id_snapshot = ?,
                        disciplina_snapshot = ?,
                        topico_snapshot = ?,
                        enunciado_snapshot = ?,
                        alternativas_snapshot = ?,
                        gabarito_snapshot = ?,
                        explicacao_snapshot = ?,
                        banca_snapshot = ?,
                        ano_snapshot = ?,
                        fonte_snapshot = ?,
                        dificuldade_snapshot = ?,
                        snapshot_origem = 'migrado'
                    WHERE
                        questao_id = ?
                        AND enunciado_snapshot IS NULL
                    """,
                    (
                        questao[0],
                        questao[1],
                        questao[2],
                        questao[3],
                        questao[4],
                        questao[5],
                        json.dumps(
                            alternativas_serializadas,
                            ensure_ascii=False
                        ),
                        gabarito,
                        questao[6] or "",
                        questao[7] or "",
                        questao[8],
                        questao[9] or "",
                        questao[10]
                        or "Não informada",
                        questao[0],
                    )
                )

            conexao.execute(
                """
                INSERT INTO migracoes (
                    nome,
                    executada_em
                )
                VALUES (
                    'tentativas_snapshot_v1',
                    datetime('now', 'localtime')
                )
                """
            )

        conexao.execute("""
            CREATE INDEX IF NOT EXISTS idx_questoes_topico
            ON questoes(topico_id)
        """)

        conexao.execute("""
            CREATE INDEX IF NOT EXISTS idx_questoes_banca
            ON questoes(banca)
        """)

        conexao.execute("""
            CREATE INDEX IF NOT EXISTS idx_questoes_ano
            ON questoes(ano)
        """)

        conexao.execute("""
            CREATE INDEX IF NOT EXISTS idx_tentativas_questao
            ON tentativas_questoes(questao_id)
        """)

        conexao.execute("""
            CREATE INDEX IF NOT EXISTS idx_tentativas_concurso_questao
            ON tentativas_questoes(
                concurso_id,
                questao_id
            )
        """)

        conexao.execute("""
            CREATE INDEX IF NOT EXISTS idx_tentativas_sessao
            ON tentativas_questoes(sessao_id)
        """)

        conexao.execute("""
            CREATE INDEX IF NOT EXISTS idx_tentativas_revisao
            ON tentativas_questoes(revisao_id)
        """)

        conexao.execute("""
            CREATE INDEX IF NOT EXISTS idx_revisoes_origem_data
            ON revisoes(
                topico_id,
                data,
                origem
            )
        """)

        conexao.execute(
            """
            INSERT OR IGNORE INTO concursos (
                nome,
                e_padrao
            )
            VALUES ('Padrão', 1)
            """
        )

        concurso_padrao = conexao.execute(
            """
            SELECT id
            FROM concursos
            WHERE e_padrao = 1
            ORDER BY id
            LIMIT 1
            """
        ).fetchone()

        if concurso_padrao is None:
            concurso_padrao_id = conexao.execute(
                """
                INSERT INTO concursos (
                    nome,
                    e_padrao
                )
                VALUES ('Padrão', 1)
                """
            ).lastrowid
        else:
            concurso_padrao_id = concurso_padrao[0]

        # Preserva os pesos que o usuário já configurou antes
        # da criação dos perfis de concurso.
        conexao.execute(
            """
            INSERT OR IGNORE INTO topico_concurso_importancia (
                topico_id,
                concurso_id,
                importancia,
                incluido
            )
            SELECT
                topico_id,
                ?,
                COALESCE(importancia, 3),
                1
            FROM controle_topico
            """,
            (concurso_padrao_id,)
        )

        migracao_inclusao = conexao.execute(
            """
            SELECT 1
            FROM migracoes
            WHERE nome = 'perfis_inclusao_v1'
            """
        ).fetchone()

        if migracao_inclusao is None:
            # Todos os perfis que JÁ existiam antes deste recurso
            # preservam o comportamento anterior: tudo incluído.
            conexao.execute(
                """
                INSERT OR IGNORE INTO disciplina_concurso_inclusao (
                    disciplina_id,
                    concurso_id,
                    incluido
                )
                SELECT
                    d.id,
                    c.id,
                    1
                FROM disciplinas d
                CROSS JOIN concursos c
                """
            )

            conexao.execute(
                """
                INSERT OR IGNORE INTO topico_concurso_importancia (
                    topico_id,
                    concurso_id,
                    importancia,
                    incluido
                )
                SELECT
                    t.id,
                    c.id,
                    3,
                    1
                FROM topicos t
                CROSS JOIN concursos c
                """
            )

            conexao.execute(
                """
                INSERT INTO migracoes (
                    nome,
                    executada_em
                )
                VALUES (
                    'perfis_inclusao_v1',
                    datetime('now')
                )
                """
            )

        ativo = conexao.execute(
            """
            SELECT valor
            FROM configuracoes
            WHERE chave = 'concurso_ativo_id'
            """
        ).fetchone()

        ativo_valido = False

        if ativo is not None:
            try:
                ativo_id = int(ativo[0])

                existe = conexao.execute(
                    """
                    SELECT 1
                    FROM concursos
                    WHERE id = ?
                    """,
                    (ativo_id,)
                ).fetchone()

                ativo_valido = (
                    existe is not None
                )
            except (
                TypeError,
                ValueError
            ):
                ativo_valido = False

        if not ativo_valido:
            conexao.execute(
                """
                INSERT INTO configuracoes (
                    chave,
                    valor
                )
                VALUES (
                    'concurso_ativo_id',
                    ?
                )
                ON CONFLICT(chave)
                DO UPDATE SET valor = excluded.valor
                """,
                (
                    str(concurso_padrao_id),
                )
            )


        # ------------------------------------------------------
        # RECOMENDAÇÕES — HISTÓRICO DE DECISÕES DO MOTOR V4
        # ------------------------------------------------------
        conexao.execute("""
            CREATE TABLE IF NOT EXISTS recomendacoes_estudo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                concurso_id INTEGER,
                criado_em TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
                origem TEXT,
                disciplina_id INTEGER,
                topico_id INTEGER,
                disciplina_nome TEXT,
                topico_nome TEXT,
                atividade TEXT,
                minutos_sugeridos INTEGER NOT NULL DEFAULT 0,
                questoes_alvo INTEGER NOT NULL DEFAULT 0,
                score_total REAL,
                explicacao_json TEXT,
                decisao TEXT NOT NULL DEFAULT 'exibida',
                decidido_em TEXT,
                minutos_escolhidos INTEGER,
                FOREIGN KEY (concurso_id) REFERENCES concursos(id) ON DELETE SET NULL,
                FOREIGN KEY (disciplina_id) REFERENCES disciplinas(id) ON DELETE SET NULL,
                FOREIGN KEY (topico_id) REFERENCES topicos(id) ON DELETE SET NULL
            )
        """)

        # ------------------------------------------------------
        # ÍNDICES DE PERFORMANCE — consultas mais frequentes
        # ------------------------------------------------------
        indices_performance = [
            "CREATE INDEX IF NOT EXISTS idx_revisoes_topico_data ON revisoes(topico_id, data DESC)",
            "CREATE INDEX IF NOT EXISTS idx_revisoes_data ON revisoes(data)",
            "CREATE INDEX IF NOT EXISTS idx_revisoes_prazo ON revisoes(prazo_historico_valido, realizada_em, dias_atraso)",
            "CREATE INDEX IF NOT EXISTS idx_controle_topico_proxima ON controle_topico(proxima_revisao, topico_id)",
            "CREATE INDEX IF NOT EXISTS idx_topicos_disciplina_nome ON topicos(disciplina_id, nome COLLATE NOCASE)",
            "CREATE INDEX IF NOT EXISTS idx_tci_concurso_incluido ON topico_concurso_importancia(concurso_id, incluido, topico_id)",
            "CREATE INDEX IF NOT EXISTS idx_tci_concurso_operacional ON topico_concurso_importancia(concurso_id, incluido, pausado, topico_id)",
            "CREATE INDEX IF NOT EXISTS idx_dci_concurso_incluido ON disciplina_concurso_inclusao(concurso_id, incluido, disciplina_id)",
            "CREATE INDEX IF NOT EXISTS idx_dci_concurso_estado ON disciplina_concurso_inclusao(concurso_id, incluido, pausado, disciplina_id)",
            "CREATE INDEX IF NOT EXISTS idx_questoes_topico_ativa ON questoes(topico_id, ativa, id)",
            "CREATE INDEX IF NOT EXISTS idx_sessoes_questoes_concurso_inicio ON sessoes_questoes(concurso_id, iniciado_em DESC)",
            "CREATE INDEX IF NOT EXISTS idx_tentativas_concurso_data ON tentativas_questoes(concurso_id, respondida_em DESC)",
            "CREATE INDEX IF NOT EXISTS idx_tentativas_sessao_correta ON tentativas_questoes(sessao_id, correta)",
            "CREATE INDEX IF NOT EXISTS idx_sessoes_foco_disciplina_inicio ON sessoes_foco(disciplina_id, inicio DESC)",
            "CREATE INDEX IF NOT EXISTS idx_sessoes_foco_atividade_inicio ON sessoes_foco(tipo_atividade, inicio DESC)",
            "CREATE INDEX IF NOT EXISTS idx_recomendacoes_concurso_data ON recomendacoes_estudo(concurso_id, criado_em DESC)",
            "CREATE INDEX IF NOT EXISTS idx_recomendacoes_topico ON recomendacoes_estudo(topico_id, criado_em DESC)",
            "CREATE INDEX IF NOT EXISTS idx_recomendacoes_decisao ON recomendacoes_estudo(decisao, criado_em DESC)",
        ]
        for comando in indices_performance:
            conexao.execute(comando)

        # Materializa os capítulos padrão logo na abertura. Assim, títulos de
        # Direito Penal já chegam completos, inclusive antes do primeiro
        # clique na tela de disciplina.
        topicos_penal = conexao.execute(
            """
            SELECT t.id
            FROM topicos t
            JOIN disciplinas d ON d.id = t.disciplina_id
            WHERE d.nome = 'Direito Penal'
            """
        ).fetchall()
        for (topico_id,) in topicos_penal:
            _garantir_capitulos_padrao(topico_id, conexao)

        conexao.execute(
            """
            INSERT OR IGNORE INTO capitulo_concurso_config (
                capitulo_id, concurso_id, dificuldade, pausado
            )
            SELECT c.id, co.id, 3, 0
            FROM capitulos_topico c
            CROSS JOIN concursos co
            """
        )

        try:
            conexao.execute("PRAGMA optimize")
        except sqlite3.DatabaseError:
            pass


def listar_concursos():
    with conectar() as conexao:
        return conexao.execute(
            """
            SELECT
                id,
                nome,
                e_padrao
            FROM concursos
            ORDER BY
                e_padrao DESC,
                nome COLLATE NOCASE
            """
        ).fetchall()


def obter_concurso_padrao():
    with conectar() as conexao:
        linha = conexao.execute(
            """
            SELECT
                id,
                nome
            FROM concursos
            WHERE e_padrao = 1
            ORDER BY id
            LIMIT 1
            """
        ).fetchone()

        if linha is None:
            cursor = conexao.execute(
                """
                INSERT INTO concursos (
                    nome,
                    e_padrao
                )
                VALUES ('Padrão', 1)
                """
            )

            return (
                cursor.lastrowid,
                "Padrão"
            )

        return linha


def obter_concurso_ativo():
    with conectar() as conexao:
        linha = conexao.execute(
            """
            SELECT valor
            FROM configuracoes
            WHERE chave = 'concurso_ativo_id'
            """
        ).fetchone()

        concurso_id = None

        if linha is not None:
            try:
                concurso_id = int(
                    linha[0]
                )
            except (
                TypeError,
                ValueError
            ):
                concurso_id = None

        if concurso_id is not None:
            concurso = conexao.execute(
                """
                SELECT
                    id,
                    nome
                FROM concursos
                WHERE id = ?
                """,
                (concurso_id,)
            ).fetchone()

            if concurso is not None:
                return concurso

        padrao = conexao.execute(
            """
            SELECT
                id,
                nome
            FROM concursos
            WHERE e_padrao = 1
            ORDER BY id
            LIMIT 1
            """
        ).fetchone()

        if padrao is None:
            cursor = conexao.execute(
                """
                INSERT INTO concursos (
                    nome,
                    e_padrao
                )
                VALUES ('Padrão', 1)
                """
            )

            padrao = (
                cursor.lastrowid,
                "Padrão"
            )

        conexao.execute(
            """
            INSERT INTO configuracoes (
                chave,
                valor
            )
            VALUES (
                'concurso_ativo_id',
                ?
            )
            ON CONFLICT(chave)
            DO UPDATE SET valor = excluded.valor
            """,
            (
                str(padrao[0]),
            )
        )

        return padrao


def definir_concurso_ativo(concurso_id):
    concurso_id = int(
        concurso_id
    )

    with conectar() as conexao:
        existe = conexao.execute(
            """
            SELECT 1
            FROM concursos
            WHERE id = ?
            """,
            (concurso_id,)
        ).fetchone()

        if existe is None:
            return False

        conexao.execute(
            """
            INSERT INTO configuracoes (
                chave,
                valor
            )
            VALUES (
                'concurso_ativo_id',
                ?
            )
            ON CONFLICT(chave)
            DO UPDATE SET valor = excluded.valor
            """,
            (
                str(concurso_id),
            )
        )

        return True


def adicionar_concurso(nome):
    """
    Perfis novos começam vazios.
    O usuário escolhe explicitamente as matérias/tópicos,
    ou pode duplicar um perfil existente.
    """
    nome = str(
        nome
    ).strip()

    if not nome:
        return None

    with conectar() as conexao:
        try:
            cursor = conexao.execute(
                """
                INSERT INTO concursos (
                    nome,
                    e_padrao
                )
                VALUES (?, 0)
                """,
                (nome,)
            )

            return cursor.lastrowid

        except sqlite3.IntegrityError:
            return None


def renomear_concurso(
    concurso_id,
    novo_nome
):
    novo_nome = str(
        novo_nome
    ).strip()

    if not novo_nome:
        return False

    with conectar() as conexao:
        linha = conexao.execute(
            """
            SELECT e_padrao
            FROM concursos
            WHERE id = ?
            """,
            (concurso_id,)
        ).fetchone()

        if (
            linha is None
            or linha[0] == 1
        ):
            return False

        try:
            conexao.execute(
                """
                UPDATE concursos
                SET nome = ?
                WHERE id = ?
                """,
                (
                    novo_nome,
                    concurso_id
                )
            )

            return True

        except sqlite3.IntegrityError:
            return False


def excluir_concurso(concurso_id):
    concurso_id = int(
        concurso_id
    )

    with conectar() as conexao:
        linha = conexao.execute(
            """
            SELECT
                nome,
                e_padrao
            FROM concursos
            WHERE id = ?
            """,
            (concurso_id,)
        ).fetchone()

        if (
            linha is None
            or linha[1] == 1
        ):
            return False

        ativo = conexao.execute(
            """
            SELECT valor
            FROM configuracoes
            WHERE chave = 'concurso_ativo_id'
            """
        ).fetchone()

        estava_ativo = False

        if ativo is not None:
            try:
                estava_ativo = (
                    int(ativo[0])
                    == concurso_id
                )
            except (
                TypeError,
                ValueError
            ):
                estava_ativo = False

        conexao.execute(
            """
            DELETE FROM concursos
            WHERE id = ?
            """,
            (concurso_id,)
        )

        if estava_ativo:
            padrao = conexao.execute(
                """
                SELECT id
                FROM concursos
                WHERE e_padrao = 1
                ORDER BY id
                LIMIT 1
                """
            ).fetchone()

            if padrao is not None:
                conexao.execute(
                    """
                    INSERT INTO configuracoes (
                        chave,
                        valor
                    )
                    VALUES (
                        'concurso_ativo_id',
                        ?
                    )
                    ON CONFLICT(chave)
                    DO UPDATE SET valor = excluded.valor
                    """,
                    (
                        str(padrao[0]),
                    )
                )

        return True


def duplicar_concurso(
    concurso_origem_id,
    novo_nome
):
    novo_id = adicionar_concurso(
        novo_nome
    )

    if novo_id is None:
        return None

    with conectar() as conexao:
        # Copia as matérias associadas.
        conexao.execute(
            """
            INSERT INTO disciplina_concurso_inclusao (
                disciplina_id,
                concurso_id,
                incluido,
                pausado
            )
            SELECT
                disciplina_id,
                ?,
                incluido,
                COALESCE(pausado, 0)
            FROM disciplina_concurso_inclusao
            WHERE concurso_id = ?
            """,
            (
                novo_id,
                concurso_origem_id
            )
        )

        # Copia tópicos, inclusão e importância.
        conexao.execute(
            """
            INSERT INTO topico_concurso_importancia (
                topico_id,
                concurso_id,
                importancia,
                incluido,
                pausado
            )
            SELECT
                topico_id,
                ?,
                importancia,
                incluido,
                COALESCE(pausado, 0)
            FROM topico_concurso_importancia
            WHERE concurso_id = ?
            """,
            (
                novo_id,
                concurso_origem_id
            )
        )

    return novo_id


def listar_conteudos_concurso(concurso_id):
    """Retorna disciplinas e tópicos do perfil em duas consultas, sem N+1."""
    concurso_id = int(concurso_id)

    ordem = {
        "Geral": 0,
        "Direito Penal": 1,
        "Direito Administrativo": 2,
        "CTB": 3,
        "Português": 4,
        "Matemática": 5,
        "Informática": 6,
    }

    with conectar() as conexao:
        disciplinas_rows = conexao.execute(
            """
            SELECT
                d.id,
                d.nome,
                COALESCE(dc.incluido, 0) AS incluida
            FROM disciplinas d
            LEFT JOIN disciplina_concurso_inclusao dc
                ON dc.disciplina_id = d.id
               AND dc.concurso_id = ?
            """,
            (concurso_id,),
        ).fetchall()

        topicos_rows = conexao.execute(
            """
            SELECT
                t.disciplina_id,
                t.id,
                t.nome,
                COALESCE(tc.incluido, 0) AS incluido,
                COALESCE(tc.importancia, 3) AS importancia
            FROM topicos t
            LEFT JOIN topico_concurso_importancia tc
                ON tc.topico_id = t.id
               AND tc.concurso_id = ?
            ORDER BY t.disciplina_id, t.nome COLLATE NOCASE
            """,
            (concurso_id,),
        ).fetchall()

    por_disciplina = {}
    for disciplina_id, topico_id, topico, incluido, importancia in topicos_rows:
        por_disciplina.setdefault(int(disciplina_id), []).append({
            "topico_id": int(topico_id),
            "topico": str(topico),
            "incluido": bool(incluido),
            "importancia": int(importancia or 3),
        })

    disciplinas_rows = sorted(
        disciplinas_rows,
        key=lambda item: (ordem.get(item[1], 99), str(item[1]).lower()),
    )

    return [
        {
            "disciplina_id": int(disciplina_id),
            "disciplina": str(nome),
            "incluida": bool(incluida),
            "topicos": por_disciplina.get(int(disciplina_id), []),
        }
        for disciplina_id, nome, incluida in disciplinas_rows
    ]


def salvar_conteudos_concurso(
    concurso_id,
    disciplinas,
    topicos
):
    """
    disciplinas: iterable de (disciplina_id, incluido)
    topicos: iterable de (topico_id, incluido, importancia)
    """
    concurso_id = int(
        concurso_id
    )

    with conectar() as conexao:
        existe = conexao.execute(
            """
            SELECT 1
            FROM concursos
            WHERE id = ?
            """,
            (concurso_id,)
        ).fetchone()

        if existe is None:
            return False

        for disciplina_id, incluido in disciplinas:
            conexao.execute(
                """
                INSERT INTO disciplina_concurso_inclusao (
                    disciplina_id,
                    concurso_id,
                    incluido
                )
                VALUES (?, ?, ?)
                ON CONFLICT(
                    disciplina_id,
                    concurso_id
                )
                DO UPDATE SET
                    incluido = excluded.incluido
                """,
                (
                    int(disciplina_id),
                    concurso_id,
                    1 if incluido else 0
                )
            )

        for (
            topico_id,
            incluido,
            importancia
        ) in topicos:
            importancia = max(
                1,
                min(
                    5,
                    int(importancia)
                )
            )

            conexao.execute(
                """
                INSERT INTO topico_concurso_importancia (
                    topico_id,
                    concurso_id,
                    importancia,
                    incluido
                )
                VALUES (?, ?, ?, ?)
                ON CONFLICT(
                    topico_id,
                    concurso_id
                )
                DO UPDATE SET
                    importancia = excluded.importancia,
                    incluido = excluded.incluido
                """,
                (
                    int(topico_id),
                    concurso_id,
                    importancia,
                    1 if incluido else 0
                )
            )

            # Mantém compatibilidade do peso do perfil Padrão
            # com versões anteriores do programa.
            padrao = conexao.execute(
                """
                SELECT e_padrao
                FROM concursos
                WHERE id = ?
                """,
                (concurso_id,)
            ).fetchone()

            if (
                padrao is not None
                and padrao[0] == 1
            ):
                conexao.execute(
                    """
                    INSERT OR IGNORE INTO controle_topico (
                        topico_id
                    )
                    VALUES (?)
                    """,
                    (int(topico_id),)
                )

                conexao.execute(
                    """
                    UPDATE controle_topico
                    SET importancia = ?
                    WHERE topico_id = ?
                    """,
                    (
                        importancia,
                        int(topico_id)
                    )
                )

        return True


def contar_conteudos_concurso(concurso_id):
    concurso_id = int(
        concurso_id
    )

    with conectar() as conexao:
        disciplinas = conexao.execute(
            """
            SELECT COUNT(*)
            FROM disciplina_concurso_inclusao
            WHERE
                concurso_id = ?
                AND incluido = 1
            """,
            (concurso_id,)
        ).fetchone()[0]

        topicos = conexao.execute(
            """
            SELECT COUNT(*)
            FROM topico_concurso_importancia
            WHERE
                concurso_id = ?
                AND incluido = 1
            """,
            (concurso_id,)
        ).fetchone()[0]

        return (
            int(disciplinas or 0),
            int(topicos or 0)
        )


def adicionar_disciplina(nome):
    nome = str(
        nome
    ).strip()

    if not nome:
        return None

    concurso_ativo_id = (
        obter_concurso_ativo()[0]
    )

    concurso_padrao_id = (
        obter_concurso_padrao()[0]
    )

    with conectar() as conexao:
        try:
            cursor = conexao.execute(
                """
                INSERT INTO disciplinas (
                    nome
                )
                VALUES (?)
                """,
                (nome,)
            )

            disciplina_id = (
                cursor.lastrowid
            )

            # A nova disciplina nasce visível no perfil Padrão
            # e no perfil atualmente selecionado.
            for concurso_id in {
                concurso_padrao_id,
                concurso_ativo_id
            }:
                conexao.execute(
                    """
                    INSERT INTO disciplina_concurso_inclusao (
                        disciplina_id,
                        concurso_id,
                        incluido
                    )
                    VALUES (?, ?, 1)
                    ON CONFLICT(
                        disciplina_id,
                        concurso_id
                    )
                    DO UPDATE SET
                        incluido = 1
                    """,
                    (
                        disciplina_id,
                        concurso_id
                    )
                )

            return disciplina_id

        except sqlite3.IntegrityError:
            return None


def renomear_disciplina(
    disciplina_id,
    novo_nome
):
    novo_nome = str(
        novo_nome
    ).strip()

    if not novo_nome:
        return False

    with conectar() as conexao:
        try:
            cursor = conexao.execute(
                """
                UPDATE disciplinas
                SET nome = ?
                WHERE id = ?
                """,
                (
                    novo_nome,
                    int(
                        disciplina_id
                    )
                )
            )

            return (
                cursor.rowcount > 0
            )

        except sqlite3.IntegrityError:
            return False


def obter_resumo_disciplina(
    disciplina_id
):
    with conectar() as conexao:
        disciplina = conexao.execute(
            """
            SELECT nome
            FROM disciplinas
            WHERE id = ?
            """,
            (
                int(
                    disciplina_id
                ),
            )
        ).fetchone()

        if disciplina is None:
            return None

        topicos = conexao.execute(
            """
            SELECT COUNT(*)
            FROM topicos
            WHERE disciplina_id = ?
            """,
            (
                int(
                    disciplina_id
                ),
            )
        ).fetchone()[0]

        revisoes_programa = conexao.execute(
            """
            SELECT COUNT(*)
            FROM revisoes r
            JOIN topicos t
                ON t.id = r.topico_id
            WHERE t.disciplina_id = ?
            """,
            (
                int(
                    disciplina_id
                ),
            )
        ).fetchone()[0]

        revisoes_importadas = conexao.execute(
            """
            SELECT COALESCE(
                SUM(
                    COALESCE(
                        c.revisoes_iniciais,
                        0
                    )
                ),
                0
            )
            FROM topicos t
            LEFT JOIN controle_topico c
                ON c.topico_id = t.id
            WHERE t.disciplina_id = ?
            """,
            (
                int(
                    disciplina_id
                ),
            )
        ).fetchone()[0]

        questoes_programa = conexao.execute(
            """
            SELECT COALESCE(
                SUM(r.questoes),
                0
            )
            FROM revisoes r
            JOIN topicos t
                ON t.id = r.topico_id
            WHERE t.disciplina_id = ?
            """,
            (
                int(
                    disciplina_id
                ),
            )
        ).fetchone()[0]

        return {
            "nome": disciplina[0],
            "topicos": int(
                topicos or 0
            ),
            "revisoes_programa": int(
                revisoes_programa or 0
            ),
            "revisoes_importadas": int(
                revisoes_importadas or 0
            ),
            "revisoes_totais": int(
                (revisoes_programa or 0)
                + (revisoes_importadas or 0)
            ),
            "questoes_programa": int(
                questoes_programa or 0
            )
        }


def excluir_disciplina(
    disciplina_id
):
    """
    Exclusão GLOBAL e permanente.
    As FKs com ON DELETE CASCADE removem tópicos, revisões,
    controle de tópicos e associações com concursos.
    """
    with conectar() as conexao:
        cursor = conexao.execute(
            """
            DELETE FROM disciplinas
            WHERE id = ?
            """,
            (
                int(
                    disciplina_id
                ),
            )
        )

        return (
            cursor.rowcount > 0
        )


def listar_disciplinas(
    concurso_id=None,
    somente_incluidas=True,
    incluir_pausadas=False
):
    ordem = {
        "Geral": 0,
        "Direito Penal": 1,
        "Direito Administrativo": 2,
        "CTB": 3,
        "Português": 4,
        "Matemática": 5,
        "Informática": 6,
    }

    if concurso_id is None:
        concurso_id = obter_concurso_ativo()[0]

    with conectar() as conexao:
        if somente_incluidas:
            filtro_pausa = "" if incluir_pausadas else "AND COALESCE(dc.pausado, 0) = 0"
            dados = conexao.execute(
                f"""
                SELECT
                    d.id,
                    d.nome
                FROM disciplinas d
                JOIN disciplina_concurso_inclusao dc
                    ON dc.disciplina_id = d.id
                    AND dc.concurso_id = ?
                    AND dc.incluido = 1
                    {filtro_pausa}
                """,
                (concurso_id,)
            ).fetchall()
        else:
            dados = conexao.execute(
                """
                SELECT id, nome
                FROM disciplinas
                """
            ).fetchall()

    return sorted(
        dados,
        key=lambda item: (
            ordem.get(item[1], 99),
            item[1].lower()
        )
    )


def listar_disciplinas_gerenciamento(concurso_id=None):
    """Lista disciplinas incluídas no perfil, inclusive as temporariamente desligadas."""
    if concurso_id is None:
        concurso_id = obter_concurso_ativo()[0]
    ordem = {
        "Geral": 0, "Direito Penal": 1, "Direito Administrativo": 2,
        "CTB": 3, "Português": 4, "Matemática": 5, "Informática": 6,
    }
    with conectar() as conexao:
        dados = conexao.execute(
            """
            SELECT d.id, d.nome, COALESCE(dc.pausado, 0) AS pausado
            FROM disciplinas d
            JOIN disciplina_concurso_inclusao dc
              ON dc.disciplina_id = d.id
             AND dc.concurso_id = ?
             AND dc.incluido = 1
            """,
            (int(concurso_id),),
        ).fetchall()
    return sorted(
        [(int(i), str(n), bool(p)) for i, n, p in dados],
        key=lambda item: (ordem.get(item[1], 99), item[1].lower()),
    )


def definir_disciplina_pausada(disciplina_id, pausada=True, concurso_id=None):
    """Desliga/reativa uma disciplina no perfil sem remover seus dados."""
    if concurso_id is None:
        concurso_id = obter_concurso_ativo()[0]
    disciplina_id = int(disciplina_id)
    concurso_id = int(concurso_id)
    valor = 1 if pausada else 0
    with conectar() as conexao:
        linha = conexao.execute(
            """
            SELECT incluido
            FROM disciplina_concurso_inclusao
            WHERE disciplina_id = ? AND concurso_id = ?
            """,
            (disciplina_id, concurso_id),
        ).fetchone()
        if linha is None or not bool(linha[0]):
            return False
        conexao.execute(
            """
            UPDATE disciplina_concurso_inclusao
            SET pausado = ?
            WHERE disciplina_id = ? AND concurso_id = ?
            """,
            (valor, disciplina_id, concurso_id),
        )
    return True


def disciplina_esta_pausada(disciplina_id, concurso_id=None):
    if concurso_id is None:
        concurso_id = obter_concurso_ativo()[0]
    with conectar() as conexao:
        linha = conexao.execute(
            """
            SELECT COALESCE(pausado, 0)
            FROM disciplina_concurso_inclusao
            WHERE disciplina_id = ? AND concurso_id = ? AND incluido = 1
            """,
            (int(disciplina_id), int(concurso_id)),
        ).fetchone()
    return bool(linha and linha[0])


def listar_disciplinas_pausadas(concurso_id=None):
    return [
        item for item in listar_disciplinas_gerenciamento(concurso_id)
        if item[2]
    ]


def _expressao_percentual_atual():
    return """
        COALESCE(
            (
                SELECT ROUND(
                    100.0 * r.acertos / r.questoes,
                    1
                )
                FROM revisoes r
                WHERE r.topico_id = t.id
                ORDER BY r.data DESC, r.id DESC
                LIMIT 1
            ),
            c.percentual_inicial
        )
    """


def _expressao_revisoes_totais():
    return """
        COALESCE(c.revisoes_iniciais, 0)
        +
        (
            SELECT COUNT(*)
            FROM revisoes r
            WHERE r.topico_id = t.id
        )
    """


def listar_topicos(
    nome_disciplina,
    concurso_id=None,
    incluir_pausados=False
):
    percentual = _expressao_percentual_atual()
    revisoes = _expressao_revisoes_totais()

    if concurso_id is None:
        concurso_id = (
            obter_concurso_ativo()[0]
        )

    filtro_pausa = "" if incluir_pausados else "AND COALESCE(tc.pausado, 0) = 0"

    with conectar() as conexao:
        return conexao.execute(
            f"""
            SELECT
                t.id,
                t.nome,
                {revisoes} AS quantidade_revisoes,
                (
                    SELECT r.data
                    FROM revisoes r
                    WHERE r.topico_id = t.id
                    ORDER BY r.data DESC, r.id DESC
                    LIMIT 1
                ) AS ultima_revisao,
                c.proxima_revisao,
                {percentual} AS percentual_atual,
                COALESCE(
                    tc.importancia,
                    3
                ) AS importancia
            FROM topicos t
            JOIN disciplinas d
                ON d.id = t.disciplina_id
            JOIN disciplina_concurso_inclusao dc
                ON dc.disciplina_id = d.id
                AND dc.concurso_id = ?
                AND dc.incluido = 1
                AND COALESCE(dc.pausado, 0) = 0
            JOIN topico_concurso_importancia tc
                ON tc.topico_id = t.id
                AND tc.concurso_id = ?
                AND tc.incluido = 1
                {filtro_pausa}
            LEFT JOIN controle_topico c
                ON c.topico_id = t.id
            WHERE d.nome = ?
            ORDER BY t.nome COLLATE NOCASE
            """,
            (
                concurso_id,
                concurso_id,
                nome_disciplina
            )
        ).fetchall()


def listar_topicos_gerenciamento(nome_disciplina, concurso_id=None):
    """Lista tópicos incluídos no perfil, inclusive os temporariamente desligados.

    Mantém os sete campos históricos de ``listar_topicos`` e acrescenta
    ``pausado`` como oitavo valor.
    """
    percentual = _expressao_percentual_atual()
    revisoes = _expressao_revisoes_totais()
    if concurso_id is None:
        concurso_id = obter_concurso_ativo()[0]

    with conectar() as conexao:
        return conexao.execute(
            f"""
            SELECT
                t.id,
                t.nome,
                {revisoes} AS quantidade_revisoes,
                (
                    SELECT r.data
                    FROM revisoes r
                    WHERE r.topico_id = t.id
                    ORDER BY r.data DESC, r.id DESC
                    LIMIT 1
                ) AS ultima_revisao,
                c.proxima_revisao,
                {percentual} AS percentual_atual,
                COALESCE(tc.importancia, 3) AS importancia,
                COALESCE(tc.pausado, 0) AS pausado
            FROM topicos t
            JOIN disciplinas d
                ON d.id = t.disciplina_id
            JOIN disciplina_concurso_inclusao dc
                ON dc.disciplina_id = d.id
                AND dc.concurso_id = ?
                AND dc.incluido = 1
            JOIN topico_concurso_importancia tc
                ON tc.topico_id = t.id
                AND tc.concurso_id = ?
                AND tc.incluido = 1
            LEFT JOIN controle_topico c
                ON c.topico_id = t.id
            WHERE d.nome = ?
            ORDER BY t.nome COLLATE NOCASE
            """,
            (concurso_id, concurso_id, nome_disciplina),
        ).fetchall()


def definir_topico_pausado(topico_id, pausado=True, concurso_id=None):
    """Desliga/reativa um tópico apenas no perfil informado, sem apagar dados."""
    if concurso_id is None:
        concurso_id = obter_concurso_ativo()[0]
    topico_id = int(topico_id)
    concurso_id = int(concurso_id)
    valor = 1 if pausado else 0
    with conectar() as conexao:
        existe = conexao.execute(
            "SELECT 1 FROM topicos WHERE id = ?", (topico_id,)
        ).fetchone()
        if existe is None:
            return False
        conexao.execute(
            """
            INSERT OR IGNORE INTO topico_concurso_importancia
                (topico_id, concurso_id, importancia, incluido, pausado)
            VALUES (?, ?, 3, 1, 0)
            """,
            (topico_id, concurso_id),
        )
        conexao.execute(
            """
            UPDATE topico_concurso_importancia
            SET pausado = ?
            WHERE topico_id = ? AND concurso_id = ?
            """,
            (valor, topico_id, concurso_id),
        )
    return True


def topico_esta_pausado(topico_id, concurso_id=None):
    if concurso_id is None:
        concurso_id = obter_concurso_ativo()[0]
    with conectar() as conexao:
        linha = conexao.execute(
            """
            SELECT COALESCE(pausado, 0)
            FROM topico_concurso_importancia
            WHERE topico_id = ? AND concurso_id = ?
            """,
            (int(topico_id), int(concurso_id)),
        ).fetchone()
    return bool(linha and linha[0])


def listar_topicos_pausados_ids(concurso_id=None):
    if concurso_id is None:
        concurso_id = obter_concurso_ativo()[0]
    with conectar() as conexao:
        linhas = conexao.execute(
            """
            SELECT topico_id
            FROM topico_concurso_importancia
            WHERE concurso_id = ?
              AND incluido = 1
              AND COALESCE(pausado, 0) = 1
            """,
            (int(concurso_id),),
        ).fetchall()
    return {int(linha[0]) for linha in linhas}


def adicionar_topico(
    nome_disciplina,
    nome_topico
):
    concurso_ativo_id = (
        obter_concurso_ativo()[0]
    )
    concurso_padrao_id = (
        obter_concurso_padrao()[0]
    )

    with conectar() as conexao:
        disciplina = conexao.execute(
            """
            SELECT id
            FROM disciplinas
            WHERE nome = ?
            """,
            (nome_disciplina,)
        ).fetchone()

        if disciplina is None:
            cursor = conexao.execute(
                """
                INSERT INTO disciplinas (nome)
                VALUES (?)
                """,
                (nome_disciplina,)
            )
            disciplina_id = (
                cursor.lastrowid
            )
        else:
            disciplina_id = disciplina[0]

        try:
            cursor = conexao.execute(
                """
                INSERT INTO topicos (
                    disciplina_id,
                    nome
                )
                VALUES (?, ?)
                """,
                (
                    disciplina_id,
                    nome_topico
                )
            )

            topico_id = cursor.lastrowid

            conexao.execute(
                """
                INSERT OR IGNORE INTO controle_topico (
                    topico_id
                )
                VALUES (?)
                """,
                (topico_id,)
            )

            perfis_iniciais = {
                concurso_padrao_id,
                concurso_ativo_id
            }

            for concurso_id in perfis_iniciais:
                conexao.execute(
                    """
                    INSERT INTO disciplina_concurso_inclusao (
                        disciplina_id,
                        concurso_id,
                        incluido
                    )
                    VALUES (?, ?, 1)
                    ON CONFLICT(
                        disciplina_id,
                        concurso_id
                    )
                    DO UPDATE SET
                        incluido = 1
                    """,
                    (
                        disciplina_id,
                        concurso_id
                    )
                )

                conexao.execute(
                    """
                    INSERT INTO topico_concurso_importancia (
                        topico_id,
                        concurso_id,
                        importancia,
                        incluido
                    )
                    VALUES (?, ?, 3, 1)
                    ON CONFLICT(
                        topico_id,
                        concurso_id
                    )
                    DO UPDATE SET
                        incluido = 1
                    """,
                    (
                        topico_id,
                        concurso_id
                    )
                )

            return True

        except sqlite3.IntegrityError:
            return False


def renomear_topico(topico_id, novo_nome):
    with conectar() as conexao:
        try:
            conexao.execute(
                "UPDATE topicos SET nome = ? WHERE id = ?",
                (novo_nome, topico_id)
            )
            return True
        except sqlite3.IntegrityError:
            return False


def excluir_topico(topico_id):
    with conectar() as conexao:
        conexao.execute(
            "DELETE FROM topicos WHERE id = ?",
            (topico_id,)
        )


def contar_revisoes_programa(topico_id):
    with conectar() as conexao:
        return conexao.execute(
            "SELECT COUNT(*) FROM revisoes WHERE topico_id = ?",
            (topico_id,)
        ).fetchone()[0]


def atualizar_importancia_topico(
    topico_id,
    importancia,
    concurso_id=None
):
    importancia = max(
        1,
        min(
            5,
            int(importancia)
        )
    )

    if concurso_id is None:
        concurso_id = (
            obter_concurso_ativo()[0]
        )

    with conectar() as conexao:
        linha = conexao.execute(
            """
            SELECT incluido
            FROM topico_concurso_importancia
            WHERE
                topico_id = ?
                AND concurso_id = ?
            """,
            (
                topico_id,
                concurso_id
            )
        ).fetchone()

        incluido = (
            1
            if linha is None
            else int(linha[0])
        )

        conexao.execute(
            """
            INSERT INTO topico_concurso_importancia (
                topico_id,
                concurso_id,
                importancia,
                incluido
            )
            VALUES (
                ?,
                ?,
                ?,
                ?
            )
            ON CONFLICT(
                topico_id,
                concurso_id
            )
            DO UPDATE SET
                importancia = excluded.importancia
            """,
            (
                topico_id,
                concurso_id,
                importancia,
                incluido
            )
        )

        padrao = conexao.execute(
            """
            SELECT e_padrao
            FROM concursos
            WHERE id = ?
            """,
            (concurso_id,)
        ).fetchone()

        if (
            padrao is not None
            and padrao[0] == 1
        ):
            conexao.execute(
                """
                INSERT OR IGNORE INTO controle_topico (
                    topico_id
                )
                VALUES (?)
                """,
                (topico_id,)
            )

            conexao.execute(
                """
                UPDATE controle_topico
                SET importancia = ?
                WHERE topico_id = ?
                """,
                (
                    importancia,
                    topico_id
                )
            )


def obter_importancia_topico(
    topico_id,
    concurso_id=None
):
    if concurso_id is None:
        concurso_id = (
            obter_concurso_ativo()[0]
        )

    with conectar() as conexao:
        linha = conexao.execute(
            """
            SELECT importancia
            FROM topico_concurso_importancia
            WHERE
                topico_id = ?
                AND concurso_id = ?
            """,
            (
                topico_id,
                concurso_id
            )
        ).fetchone()

        if linha is None:
            return 3

        return int(
            linha[0]
        )


def _normalizar_chave_conteudo(texto):
    texto = unicodedata.normalize(
        "NFD",
        str(texto or "")
    )
    texto = "".join(
        caractere
        for caractere in texto
        if unicodedata.category(caractere) != "Mn"
    )
    return " ".join(texto.lower().split())


# Estrutura de estudo baseada na organização vigente do Código Penal e nos
# títulos já cadastrados em Direito Penal. Quando a lei não traz capítulos
# formais, o conteúdo é apresentado como uma divisão interna estudável.
CAPITULOS_DIREITO_PENAL = {
    _normalizar_chave_conteudo("Título I: Da aplicação da lei penal"): (
        "Capítulo I: Da aplicação da lei penal",
        "Capítulo II: Da aplicação da lei penal no espaço",
    ),
    _normalizar_chave_conteudo("Título II: Do crime"): (
        "Capítulo I: Do crime",
        "Capítulo II: Da relação de causalidade",
        "Capítulo III: Da consumação e da tentativa",
        "Capítulo IV: Da desistência voluntária e do arrependimento eficaz",
        "Capítulo V: Do arrependimento posterior",
        "Capítulo VI: Do crime impossível",
        "Capítulo VII: Do crime doloso e do crime culposo",
        "Capítulo VIII: Da agravação pelo resultado",
        "Capítulo IX: Do erro",
        "Capítulo X: Da ilicitude",
        "Capítulo XI: Da culpabilidade",
        "Capítulo XII: Do concurso de pessoas",
    ),
    _normalizar_chave_conteudo("Título III: Da imputabilidade penal"): (
        "Disposições gerais sobre a imputabilidade penal",
    ),
    _normalizar_chave_conteudo("Título IV: Do concurso de pessoas"): (
        "Disposições gerais sobre o concurso de pessoas",
    ),
    _normalizar_chave_conteudo("Título V: Das penas"): (
        "Capítulo I: Das penas",
        "Capítulo II: Da cominação das penas",
        "Capítulo III: Da aplicação da pena",
        "Capítulo IV: Da suspensão condicional da pena",
        "Capítulo V: Do livramento condicional",
        "Capítulo VI: Dos efeitos da condenação",
        "Capítulo VII: Da reabilitação",
    ),
    _normalizar_chave_conteudo("Título VI: Das medidas de segurança"): (
        "Capítulo I: Das medidas de segurança",
        "Capítulo II: Da cessação da periculosidade",
    ),
    _normalizar_chave_conteudo("Título VII: Da ação penal"): (
        "Capítulo I: Da ação penal",
        "Capítulo II: Da ação civil",
    ),
    _normalizar_chave_conteudo("Título VIII: Da extinção da punibilidade"): (
        "Capítulo I: Da extinção da punibilidade",
        "Capítulo II: Da prescrição",
    ),
    _normalizar_chave_conteudo("Título I: Dos crimes contra a pessoa"): (
        "Capítulo I: Dos crimes contra a vida",
        "Capítulo II: Das lesões corporais",
        "Capítulo III: Da periclitação da vida e da saúde",
        "Capítulo IV: Da rixa",
        "Capítulo V: Dos crimes contra a honra",
        "Capítulo VI: Dos crimes contra a liberdade individual",
    ),
    _normalizar_chave_conteudo("Título II: Dos crimes contra o patrimônio"): (
        "Capítulo I: Do furto",
        "Capítulo II: Do roubo e da extorsão",
        "Capítulo III: Da usurpação",
        "Capítulo IV: Do dano",
        "Capítulo V: Da apropriação indébita",
        "Capítulo VI: Do estelionato e outras fraudes",
        "Capítulo VII: Da receptação",
        "Capítulo VIII: Disposições gerais",
    ),
    _normalizar_chave_conteudo("Título III: Dos crimes contra a propriedade imaterial"): (
        "Capítulo I: Dos crimes contra a propriedade intelectual",
        "Capítulo II: Dos crimes contra o privilégio de invenção",
        "Capítulo III: Dos crimes contra as marcas de indústria e comércio",
        "Capítulo IV: Dos crimes de concorrência desleal",
    ),
    _normalizar_chave_conteudo("Título IV: Dos crimes contra a organização do trabalho"): (
        "Disposições sobre os crimes contra a organização do trabalho",
    ),
    _normalizar_chave_conteudo("Título V: Dos crimes contra o sentimento religioso e contra o respeito aos mortos"): (
        "Capítulo I: Dos crimes contra o sentimento religioso",
        "Capítulo II: Dos crimes contra o respeito aos mortos",
    ),
    _normalizar_chave_conteudo("Título VI: Dos crimes contra a dignidade sexual"): (
        "Capítulo I: Dos crimes contra a liberdade sexual",
        "Capítulo I-A: Da exposição da intimidade sexual",
        "Capítulo II: Dos crimes sexuais contra vulnerável",
        "Capítulo III: Do assédio sexual",
        "Capítulo IV: Disposições gerais",
        "Capítulo V: Do lenocínio e do tráfico de pessoa para fim de prostituição ou outra forma de exploração sexual",
        "Capítulo VI: Disposições gerais",
        "Capítulo VII: Da divulgação de cena de estupro ou de cena de estupro de vulnerável, de cena de sexo ou de pornografia",
    ),
    _normalizar_chave_conteudo("Título VII: Dos crimes contra a família"): (
        "Capítulo I: Dos crimes contra o casamento",
        "Capítulo II: Dos crimes contra o estado de filiação",
        "Capítulo III: Dos crimes contra a assistência familiar",
        "Capítulo IV: Dos crimes contra o pátrio poder, tutela ou curatela",
    ),
    _normalizar_chave_conteudo("Título VIII: Dos crimes contra a incolumidade pública"): (
        "Capítulo I: Dos crimes de perigo comum",
        "Capítulo II: Dos crimes contra a segurança dos meios de comunicação e transporte e outros serviços públicos",
        "Capítulo III: Dos crimes contra a saúde pública",
    ),
    _normalizar_chave_conteudo("Título IX: Dos crimes contra a paz pública"): (
        "Disposições sobre os crimes contra a paz pública",
    ),
    _normalizar_chave_conteudo("Título X: Dos crimes contra a fé pública"): (
        "Capítulo I: Da moeda falsa",
        "Capítulo II: Da falsidade de títulos e outros papéis públicos",
        "Capítulo III: Da falsidade documental",
        "Capítulo IV: De outras falsidades",
        "Capítulo V: Das fraudes em certames de interesse público",
        "Capítulo VI: Disposições gerais",
    ),
    _normalizar_chave_conteudo("Título XI: Dos crimes contra a administração pública"): (
        "Capítulo I: Dos crimes praticados por funcionário público contra a administração em geral",
        "Capítulo II: Dos crimes praticados por particular contra a administração em geral",
        "Capítulo II-A: Dos crimes praticados por particular contra a administração pública estrangeira",
        "Capítulo III: Dos crimes contra a administração da justiça",
        "Capítulo IV: Dos crimes contra as finanças públicas",
    ),
}

# A disciplina também possui alguns tópicos sem o prefixo "Título". Eles
# representam os mesmos blocos do Código Penal e, por isso, recebem a mesma
# árvore de capítulos ao serem exibidos na tabela.
CAPITULOS_DIREITO_PENAL.update({
    _normalizar_chave_conteudo("Aplicação da Lei Penal"):
        CAPITULOS_DIREITO_PENAL[
            _normalizar_chave_conteudo("Título I: Da aplicação da lei penal")
        ],
    _normalizar_chave_conteudo("Do Crime"):
        CAPITULOS_DIREITO_PENAL[
            _normalizar_chave_conteudo("Título II: Do crime")
        ],
    _normalizar_chave_conteudo("Imputabilidade Penal"):
        CAPITULOS_DIREITO_PENAL[
            _normalizar_chave_conteudo("Título III: Da imputabilidade penal")
        ],
    _normalizar_chave_conteudo("Concurso de Pessoas"):
        CAPITULOS_DIREITO_PENAL[
            _normalizar_chave_conteudo("Título IV: Do concurso de pessoas")
        ],
    _normalizar_chave_conteudo("Das Penas"):
        CAPITULOS_DIREITO_PENAL[
            _normalizar_chave_conteudo("Título V: Das penas")
        ],
    _normalizar_chave_conteudo("Crimes contra o Patrimônio"):
        CAPITULOS_DIREITO_PENAL[
            _normalizar_chave_conteudo(
                "Título II: Dos crimes contra o patrimônio"
            )
        ],
})


def _obter_capitulos_padrao_topico(topico_id, conexao):
    linha = conexao.execute(
        """
        SELECT d.nome, t.nome
        FROM topicos t
        JOIN disciplinas d ON d.id = t.disciplina_id
        WHERE t.id = ?
        """,
        (int(topico_id),)
    ).fetchone()

    if linha is None or _normalizar_chave_conteudo(linha[0]) != "direito penal":
        return ()

    return CAPITULOS_DIREITO_PENAL.get(
        _normalizar_chave_conteudo(linha[1]),
        ()
    )


def _garantir_capitulos_padrao(topico_id, conexao):
    capitulos = _obter_capitulos_padrao_topico(topico_id, conexao)
    for ordem, nome in enumerate(capitulos, start=1):
        conexao.execute(
            """
            INSERT OR IGNORE INTO capitulos_topico (topico_id, nome, ordem)
            VALUES (?, ?, ?)
            """,
            (int(topico_id), nome, ordem)
        )
    return bool(capitulos)


def topico_possui_capitulos(topico_id):
    with conectar() as conexao:
        existe = conexao.execute(
            "SELECT 1 FROM capitulos_topico WHERE topico_id = ? LIMIT 1",
            (int(topico_id),)
        ).fetchone()
        return bool(existe) or bool(
            _obter_capitulos_padrao_topico(topico_id, conexao)
        )


def listar_capitulos_topico(topico_id, concurso_id=None):
    if concurso_id is None:
        concurso_id = obter_concurso_ativo()[0]

    with conectar() as conexao:
        _garantir_capitulos_padrao(topico_id, conexao)
        conexao.execute(
            """
            INSERT OR IGNORE INTO capitulo_concurso_config (
                capitulo_id, concurso_id, dificuldade, pausado
            )
            SELECT id, ?, 3, 0
            FROM capitulos_topico
            WHERE topico_id = ?
            """,
            (int(concurso_id), int(topico_id))
        )
        return conexao.execute(
            """
            SELECT
                c.id,
                c.nome,
                c.ordem,
                COALESCE(cc.dificuldade, 3) AS dificuldade,
                COALESCE(cc.pausado, 0) AS pausado
            FROM capitulos_topico c
            LEFT JOIN capitulo_concurso_config cc
                ON cc.capitulo_id = c.id
                AND cc.concurso_id = ?
            WHERE c.topico_id = ?
            ORDER BY c.ordem, c.nome COLLATE NOCASE
            """,
            (int(concurso_id), int(topico_id))
        ).fetchall()


def listar_capitulos_perfil(disciplina_nome=None, concurso_id=None):
    """Lista capítulos disponíveis para classificar uma questão no perfil."""
    if concurso_id is None:
        concurso_id = obter_concurso_ativo()[0]

    with conectar() as conexao:
        if disciplina_nome:
            topicos = conexao.execute(
                """
                SELECT t.id
                FROM topicos t
                JOIN disciplinas d ON d.id = t.disciplina_id
                WHERE d.nome = ?
                """,
                (str(disciplina_nome),)
            ).fetchall()
            for (topico_id,) in topicos:
                _garantir_capitulos_padrao(topico_id, conexao)

        filtro_disciplina = "AND d.nome = ?" if disciplina_nome else ""
        parametros = [int(concurso_id)]
        if disciplina_nome:
            parametros.append(str(disciplina_nome))

        return conexao.execute(
            f"""
            SELECT c.id, c.nome, c.topico_id, t.nome, d.nome
            FROM capitulos_topico c
            JOIN topicos t ON t.id = c.topico_id
            JOIN disciplinas d ON d.id = t.disciplina_id
            JOIN topico_concurso_importancia tc
                ON tc.topico_id = t.id
                AND tc.concurso_id = ?
                AND tc.incluido = 1
            WHERE 1 = 1 {filtro_disciplina}
            ORDER BY d.nome COLLATE NOCASE, t.nome COLLATE NOCASE,
                c.ordem, c.nome COLLATE NOCASE
            """,
            parametros
        ).fetchall()


def adicionar_capitulo(topico_id, nome_capitulo):
    nome_capitulo = str(nome_capitulo or "").strip()
    if not nome_capitulo:
        return False

    with conectar() as conexao:
        try:
            proxima_ordem = conexao.execute(
                """
                SELECT COALESCE(MAX(ordem), 0) + 1
                FROM capitulos_topico
                WHERE topico_id = ?
                """,
                (int(topico_id),)
            ).fetchone()[0]
            cursor = conexao.execute(
                """
                INSERT INTO capitulos_topico (topico_id, nome, ordem)
                VALUES (?, ?, ?)
                """,
                (int(topico_id), nome_capitulo, int(proxima_ordem))
            )
            conexao.execute(
                """
                INSERT OR IGNORE INTO capitulo_concurso_config (
                    capitulo_id, concurso_id, dificuldade, pausado
                )
                SELECT ?, id, 3, 0 FROM concursos
                """,
                (int(cursor.lastrowid),)
            )
            return True
        except sqlite3.IntegrityError:
            return False


def renomear_capitulo(capitulo_id, novo_nome):
    novo_nome = str(novo_nome or "").strip()
    if not novo_nome:
        return False
    with conectar() as conexao:
        try:
            cursor = conexao.execute(
                "UPDATE capitulos_topico SET nome = ? WHERE id = ?",
                (novo_nome, int(capitulo_id))
            )
            return cursor.rowcount > 0
        except sqlite3.IntegrityError:
            return False


def definir_capitulo_pausado(capitulo_id, pausado=True, concurso_id=None):
    if concurso_id is None:
        concurso_id = obter_concurso_ativo()[0]
    with conectar() as conexao:
        existe = conexao.execute(
            "SELECT 1 FROM capitulos_topico WHERE id = ?",
            (int(capitulo_id),)
        ).fetchone()
        if existe is None:
            return False
        conexao.execute(
            """
            INSERT INTO capitulo_concurso_config (
                capitulo_id, concurso_id, dificuldade, pausado
            ) VALUES (?, ?, 3, ?)
            ON CONFLICT(capitulo_id, concurso_id)
            DO UPDATE SET pausado = excluded.pausado
            """,
            (int(capitulo_id), int(concurso_id), 1 if pausado else 0)
        )
    return True


def atualizar_dificuldade_capitulo(capitulo_id, dificuldade, concurso_id=None):
    if concurso_id is None:
        concurso_id = obter_concurso_ativo()[0]
    dificuldade = max(1, min(5, int(dificuldade)))
    with conectar() as conexao:
        existe = conexao.execute(
            "SELECT 1 FROM capitulos_topico WHERE id = ?",
            (int(capitulo_id),)
        ).fetchone()
        if existe is None:
            return False
        conexao.execute(
            """
            INSERT INTO capitulo_concurso_config (
                capitulo_id, concurso_id, dificuldade, pausado
            ) VALUES (?, ?, ?, 0)
            ON CONFLICT(capitulo_id, concurso_id)
            DO UPDATE SET dificuldade = excluded.dificuldade
            """,
            (int(capitulo_id), int(concurso_id), dificuldade)
        )
    return True


def _data_iso_segura(valor):
    texto = str(valor or "").strip()[:10]
    if not texto:
        return None
    try:
        return date.fromisoformat(texto).isoformat()
    except (TypeError, ValueError):
        return None


def _metadados_prazo_revisao(prevista_para, realizada_em):
    prevista = _data_iso_segura(prevista_para)
    realizada = _data_iso_segura(realizada_em)
    if prevista is None or realizada is None:
        return {
            "prevista_para": None,
            "realizada_em": realizada,
            "dias_atraso": None,
            "prazo_historico_valido": 0,
        }
    atraso = (date.fromisoformat(realizada) - date.fromisoformat(prevista)).days
    return {
        "prevista_para": prevista,
        "realizada_em": realizada,
        "dias_atraso": int(atraso),
        "prazo_historico_valido": 1,
    }


def registrar_revisao(
    topico_id,
    data,
    questoes,
    acertos,
    observacao="",
    texto_erros="",
    continuacao="",
    proxima_revisao=None,
    origem="manual",
    confianca=None,
    sessao_questoes_id=None
):
    with conectar() as conexao:
        controle = conexao.execute(
            "SELECT proxima_revisao FROM controle_topico WHERE topico_id = ?",
            (topico_id,),
        ).fetchone()
        prevista_ativa = controle[0] if controle else None
        prazo = _metadados_prazo_revisao(prevista_ativa, data)

        conexao.execute(
            """
            INSERT INTO revisoes (
                topico_id, data, questoes, acertos, observacao, texto_erros,
                continuacao, origem, confianca, sessao_questoes_id,
                prevista_para, realizada_em, dias_atraso, prazo_historico_valido
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                topico_id, data, questoes, acertos, observacao, texto_erros,
                continuacao, str(origem or "manual"), confianca,
                sessao_questoes_id, prazo["prevista_para"],
                prazo["realizada_em"], prazo["dias_atraso"],
                prazo["prazo_historico_valido"],
            )
        )

        conexao.execute(
            "INSERT OR IGNORE INTO controle_topico (topico_id) VALUES (?)",
            (topico_id,),
        )
        if proxima_revisao is not None:
            conexao.execute(
                "UPDATE controle_topico SET proxima_revisao = ? WHERE topico_id = ?",
                (proxima_revisao, topico_id),
            )


def atualizar_revisao(
    revisao_id,
    data,
    questoes,
    acertos,
    observacao="",
    texto_erros="",
    continuacao=""
):
    with conectar() as conexao:
        linha = conexao.execute(
            "SELECT prevista_para, prazo_historico_valido FROM revisoes WHERE id = ?",
            (revisao_id,),
        ).fetchone()
        if linha and int(linha[1] or 0) == 1:
            prazo = _metadados_prazo_revisao(linha[0], data)
        else:
            prazo = {
                "realizada_em": _data_iso_segura(data),
                "dias_atraso": None,
                "prazo_historico_valido": 0,
            }
        conexao.execute(
            """
            UPDATE revisoes
            SET data = ?, questoes = ?, acertos = ?, observacao = ?,
                texto_erros = ?, continuacao = ?, realizada_em = ?,
                dias_atraso = ?, prazo_historico_valido = ?
            WHERE id = ?
            """,
            (data, questoes, acertos, observacao, texto_erros, continuacao,
             prazo["realizada_em"], prazo["dias_atraso"],
             prazo["prazo_historico_valido"], revisao_id),
        )


def excluir_revisao(revisao_id):
    with conectar() as conexao:
        conexao.execute(
            "DELETE FROM revisoes WHERE id = ?",
            (revisao_id,)
        )


def atualizar_proxima_revisao(topico_id, proxima_revisao):
    with conectar() as conexao:
        conexao.execute(
            """
            INSERT OR IGNORE INTO controle_topico (topico_id)
            VALUES (?)
            """,
            (topico_id,)
        )

        conexao.execute(
            """
            UPDATE controle_topico
            SET proxima_revisao = ?
            WHERE topico_id = ?
            """,
            (proxima_revisao, topico_id)
        )


def listar_revisoes_topico(topico_id):
    with conectar() as conexao:
        return conexao.execute(
            """
            SELECT
                r.id,
                r.data,
                r.questoes,
                r.acertos,
                ROUND(
                    100.0 * r.acertos / r.questoes,
                    1
                ) AS percentual,
                r.observacao,
                r.texto_erros,
                r.continuacao,
                COALESCE(
                    r.origem,
                    'manual'
                ) AS origem,
                COALESCE(
                    r.confianca,
                    ''
                ) AS confianca,
                r.sessao_questoes_id,
                (
                    SELECT COUNT(*)
                    FROM tentativas_questoes tq
                    WHERE tq.revisao_id = r.id
                ) AS tentativas_vinculadas,
                r.prevista_para,
                r.realizada_em,
                r.dias_atraso,
                COALESCE(r.prazo_historico_valido, 0) AS prazo_historico_valido
            FROM revisoes r
            WHERE r.topico_id = ?
            ORDER BY r.data DESC, r.id DESC
            """,
            (topico_id,)
        ).fetchall()


def obter_estatisticas_prazos_revisoes(
    concurso_id=None,
    dias=30,
    data_referencia=None
):
    if concurso_id is None:
        concurso_id = obter_concurso_ativo()[0]
    concurso_id = int(concurso_id)
    dias = max(1, int(dias or 30))
    fim = date.fromisoformat(_data_iso_segura(data_referencia) or date.today().isoformat())
    inicio = fim - timedelta(days=dias - 1)
    fim_anterior = inicio - timedelta(days=1)
    inicio_anterior = fim_anterior - timedelta(days=dias - 1)

    def resumir(de, ate):
        with conectar() as conexao:
            linha = conexao.execute(
                """
                SELECT
                    COUNT(*),
                    SUM(CASE WHEN COALESCE(r.dias_atraso, 0) <= 0 THEN 1 ELSE 0 END),
                    SUM(CASE WHEN r.dias_atraso > 0 THEN 1 ELSE 0 END),
                    AVG(CASE WHEN r.dias_atraso > 0 THEN r.dias_atraso END),
                    AVG(ABS(COALESCE(r.dias_atraso, 0))),
                    MAX(COALESCE(r.dias_atraso, 0))
                FROM revisoes r
                JOIN topicos t ON t.id = r.topico_id
                JOIN disciplinas d ON d.id = t.disciplina_id
                JOIN disciplina_concurso_inclusao dc
                  ON dc.disciplina_id = d.id AND dc.concurso_id = ? AND dc.incluido = 1 AND COALESCE(dc.pausado, 0) = 0
                JOIN topico_concurso_importancia tc
                  ON tc.topico_id = t.id AND tc.concurso_id = ? AND tc.incluido = 1
                WHERE COALESCE(r.prazo_historico_valido, 0) = 1
                  AND r.realizada_em BETWEEN ? AND ?
                """,
                (concurso_id, concurso_id, de.isoformat(), ate.isoformat()),
            ).fetchone()
        total = int(linha[0] or 0)
        no_prazo = int(linha[1] or 0)
        atrasadas = int(linha[2] or 0)
        return {
            "total_com_prazo": total,
            "no_prazo": no_prazo,
            "atrasadas": atrasadas,
            "percentual_no_prazo": (100.0 * no_prazo / total) if total else None,
            "atraso_medio_dias": float(linha[3]) if linha[3] is not None else None,
            "desvio_medio_dias": float(linha[4]) if linha[4] is not None else None,
            "maior_atraso_dias": int(linha[5]) if linha[5] is not None else None,
        }

    atual = resumir(inicio, fim)
    atual.update({
        "inicio": inicio.isoformat(),
        "fim": fim.isoformat(),
        "anterior": resumir(inicio_anterior, fim_anterior),
        "historico_parcial": True,
    })
    return atual


def obter_resumo_topico(
    topico_id,
    concurso_id=None
):
    if concurso_id is None:
        concurso = (
            obter_concurso_ativo()
        )
        concurso_id = concurso[0]
        concurso_nome = concurso[1]
    else:
        with conectar() as conexao:
            linha_concurso = conexao.execute(
                """
                SELECT nome
                FROM concursos
                WHERE id = ?
                """,
                (concurso_id,)
            ).fetchone()

        concurso_nome = (
            linha_concurso[0]
            if linha_concurso is not None
            else "—"
        )

    with conectar() as conexao:
        controle = conexao.execute(
            """
            SELECT
                COALESCE(revisoes_iniciais, 0),
                proxima_revisao,
                percentual_inicial
            FROM controle_topico
            WHERE topico_id = ?
            """,
            (topico_id,)
        ).fetchone()

        if controle is None:
            revisoes_iniciais = 0
            proxima_revisao = None
            percentual_inicial = None
        else:
            revisoes_iniciais = controle[0]
            proxima_revisao = controle[1]
            percentual_inicial = controle[2]

        importancia_linha = conexao.execute(
            """
            SELECT importancia
            FROM topico_concurso_importancia
            WHERE
                topico_id = ?
                AND concurso_id = ?
            """,
            (
                topico_id,
                concurso_id
            )
        ).fetchone()

        importancia = (
            3
            if importancia_linha is None
            else importancia_linha[0]
        )

        novas = conexao.execute(
            """
            SELECT COUNT(*)
            FROM revisoes
            WHERE topico_id = ?
            """,
            (topico_id,)
        ).fetchone()[0]

        ultima = conexao.execute(
            """
            SELECT
                data,
                ROUND(
                    100.0 * acertos / questoes,
                    1
                )
            FROM revisoes
            WHERE topico_id = ?
            ORDER BY data DESC, id DESC
            LIMIT 1
            """,
            (topico_id,)
        ).fetchone()

        if ultima is None:
            ultima_revisao = None
            percentual_atual = percentual_inicial
        else:
            ultima_revisao = ultima[0]
            percentual_atual = ultima[1]

        return {
            "revisoes_iniciais": revisoes_iniciais,
            "revisoes_programa": novas,
            "revisoes_totais": (
                revisoes_iniciais
                + novas
            ),
            "ultima_revisao": ultima_revisao,
            "proxima_revisao": proxima_revisao,
            "percentual_atual": percentual_atual,
            "importancia": int(
                importancia or 3
            ),
            "concurso_id": concurso_id,
            "concurso_nome": concurso_nome
        }






def listar_prompts_ia():
    with conectar() as conexao:
        linhas = conexao.execute(
            """
            SELECT
                id,
                nome,
                COALESCE(
                    categoria,
                    ''
                ),
                texto,
                criado_em,
                atualizado_em
            FROM prompts_ia
            ORDER BY
                nome COLLATE NOCASE,
                id
            """
        ).fetchall()

    return [
        {
            "id": int(
                linha[0]
            ),
            "nome": linha[1],
            "categoria": (
                linha[2]
                or ""
            ),
            "texto": linha[3],
            "criado_em": linha[4],
            "atualizado_em": linha[5],
        }
        for linha in linhas
    ]


def obter_prompt_ia(
    prompt_id
):
    with conectar() as conexao:
        linha = conexao.execute(
            """
            SELECT
                id,
                nome,
                COALESCE(
                    categoria,
                    ''
                ),
                texto,
                criado_em,
                atualizado_em
            FROM prompts_ia
            WHERE id = ?
            """,
            (
                int(
                    prompt_id
                ),
            )
        ).fetchone()

    if linha is None:
        return None

    return {
        "id": int(
            linha[0]
        ),
        "nome": linha[1],
        "categoria": (
            linha[2]
            or ""
        ),
        "texto": linha[3],
        "criado_em": linha[4],
        "atualizado_em": linha[5],
    }


def criar_prompt_ia(
    nome,
    texto,
    categoria=""
):
    nome = str(
        nome
        or ""
    ).strip()

    texto = str(
        texto
        or ""
    ).strip()

    categoria = str(
        categoria
        or ""
    ).strip()

    if not nome:
        raise ValueError(
            "Informe um nome para o prompt."
        )

    if not texto:
        raise ValueError(
            "O texto do prompt não pode ficar vazio."
        )

    with conectar() as conexao:
        cursor = conexao.execute(
            """
            INSERT INTO prompts_ia (
                nome,
                categoria,
                texto,
                criado_em,
                atualizado_em
            )
            VALUES (
                ?,
                ?,
                ?,
                datetime('now', 'localtime'),
                datetime('now', 'localtime')
            )
            """,
            (
                nome,
                categoria,
                texto,
            )
        )

        prompt_id = cursor.lastrowid

    return int(
        prompt_id
    )


def atualizar_prompt_ia(
    prompt_id,
    nome,
    texto,
    categoria=""
):
    nome = str(
        nome
        or ""
    ).strip()

    texto = str(
        texto
        or ""
    ).strip()

    categoria = str(
        categoria
        or ""
    ).strip()

    if not nome:
        raise ValueError(
            "Informe um nome para o prompt."
        )

    if not texto:
        raise ValueError(
            "O texto do prompt não pode ficar vazio."
        )

    with conectar() as conexao:
        cursor = conexao.execute(
            """
            UPDATE prompts_ia
            SET
                nome = ?,
                categoria = ?,
                texto = ?,
                atualizado_em = datetime(
                    'now',
                    'localtime'
                )
            WHERE id = ?
            """,
            (
                nome,
                categoria,
                texto,
                int(
                    prompt_id
                ),
            )
        )

        atualizado = (
            cursor.rowcount > 0
        )

    return atualizado


def excluir_prompt_ia(
    prompt_id
):
    with conectar() as conexao:
        cursor = conexao.execute(
            """
            DELETE FROM prompts_ia
            WHERE id = ?
            """,
            (
                int(
                    prompt_id
                ),
            )
        )

        excluido = (
            cursor.rowcount > 0
        )

    return excluido


def duplicar_prompt_ia(
    prompt_id
):
    original = obter_prompt_ia(
        prompt_id
    )

    if original is None:
        raise ValueError(
            "Prompt não encontrado."
        )

    return criar_prompt_ia(
        (
            original[
                "nome"
            ]
            + " — cópia"
        ),
        original[
            "texto"
        ],
        original[
            "categoria"
        ]
    )


def _normalizar_alternativas_questao(
    alternativas
):
    resultado = []

    for ordem, alternativa in enumerate(
        alternativas,
        start=1
    ):
        letra = str(
            alternativa.get(
                "letra",
                ""
            )
        ).strip().upper()

        texto = str(
            alternativa.get(
                "texto",
                ""
            )
        ).strip()

        correta = bool(
            alternativa.get(
                "correta",
                False
            )
        )

        if not letra or not texto:
            continue

        resultado.append({
            "letra": letra,
            "texto": texto,
            "correta": 1 if correta else 0,
            "ordem": ordem,
        })

    corretas = sum(
        item["correta"]
        for item in resultado
    )

    if len(resultado) < 2:
        raise ValueError(
            "A questão precisa ter pelo menos duas alternativas."
        )

    if corretas != 1:
        raise ValueError(
            "A questão precisa ter exatamente uma alternativa correta."
        )

    return resultado


def _resolver_classificacao_questao(topico_id, capitulo_id, conexao):
    """Aceita título, capítulo ou ambos e retorna a classificação coerente."""
    topico_id = int(topico_id) if topico_id is not None else None
    capitulo_id = int(capitulo_id) if capitulo_id is not None else None

    if capitulo_id is not None:
        capitulo = conexao.execute(
            """
            SELECT topico_id
            FROM capitulos_topico
            WHERE id = ?
            """,
            (capitulo_id,)
        ).fetchone()
        if capitulo is None:
            raise ValueError("O capítulo selecionado não existe.")
        topico_capitulo_id = int(capitulo[0])
        if topico_id is not None and topico_id != topico_capitulo_id:
            raise ValueError(
                "O capítulo selecionado não pertence ao título informado."
            )
        topico_id = topico_capitulo_id

    if topico_id is None:
        raise ValueError("Informe um título ou um capítulo para a questão.")

    existe_topico = conexao.execute(
        "SELECT 1 FROM topicos WHERE id = ?",
        (topico_id,)
    ).fetchone()
    if existe_topico is None:
        raise ValueError("O título selecionado não existe.")

    return topico_id, capitulo_id


def questao_existe(
    topico_id,
    enunciado,
    ignorar_id=None
):
    enunciado = str(
        enunciado
    ).strip()

    if not enunciado:
        return False

    with conectar() as conexao:
        parametros = [
            int(
                topico_id
            ),
            enunciado,
        ]

        sql = """
            SELECT 1
            FROM questoes
            WHERE topico_id = ?
              AND LOWER(TRIM(enunciado))
                  = LOWER(TRIM(?))
        """

        if ignorar_id is not None:
            sql += """
              AND id <> ?
            """
            parametros.append(
                int(
                    ignorar_id
                )
            )

        sql += """
            LIMIT 1
        """

        return (
            conexao.execute(
                sql,
                parametros
            ).fetchone()
            is not None
        )


def criar_questao(
    topico_id,
    enunciado,
    alternativas,
    explicacao="",
    banca="",
    ano=None,
    fonte="",
    dificuldade="Não informada",
    ativa=True,
    capitulo_id=None
):
    enunciado = str(
        enunciado
    ).strip()

    if not enunciado:
        raise ValueError(
            "O enunciado da questão não pode ficar vazio."
        )

    alternativas = (
        _normalizar_alternativas_questao(
            alternativas
        )
    )

    if ano in (
        "",
        None,
        0
    ):
        ano = None
    else:
        ano = int(
            ano
        )

    with conectar() as conexao:
        topico_id, capitulo_id = _resolver_classificacao_questao(
            topico_id,
            capitulo_id,
            conexao
        )

        cursor = conexao.execute(
            """
            INSERT INTO questoes (
                topico_id,
                capitulo_id,
                enunciado,
                explicacao,
                banca,
                ano,
                fonte,
                dificuldade,
                ativa
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                topico_id,
                capitulo_id,
                enunciado,
                str(
                    explicacao
                    or ""
                ).strip(),
                str(
                    banca
                    or ""
                ).strip(),
                ano,
                str(
                    fonte
                    or ""
                ).strip(),
                str(
                    dificuldade
                    or "Não informada"
                ).strip(),
                1 if ativa else 0,
            )
        )

        questao_id = (
            cursor.lastrowid
        )

        for alternativa in alternativas:
            conexao.execute(
                """
                INSERT INTO alternativas_questoes (
                    questao_id,
                    letra,
                    texto,
                    correta,
                    ordem
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    questao_id,
                    alternativa[
                        "letra"
                    ],
                    alternativa[
                        "texto"
                    ],
                    alternativa[
                        "correta"
                    ],
                    alternativa[
                        "ordem"
                    ],
                )
            )

        return questao_id


def criar_questoes_lote(
    registros
):
    ids = []

    with conectar() as conexao:
        for registro in registros:
            enunciado = str(
                registro.get(
                    "enunciado",
                    ""
                )
            ).strip()

            if not enunciado:
                raise ValueError(
                    "Há uma questão sem enunciado no lote."
                )

            alternativas = (
                _normalizar_alternativas_questao(
                    registro.get(
                        "alternativas",
                        []
                    )
                )
            )

            ano = registro.get(
                "ano"
            )

            if ano in (
                "",
                None,
                0
            ):
                ano = None
            else:
                ano = int(
                    ano
                )

            topico_id, capitulo_id = _resolver_classificacao_questao(
                registro.get("topico_id"),
                registro.get("capitulo_id"),
                conexao
            )

            cursor = conexao.execute(
                """
                INSERT INTO questoes (
                    topico_id,
                    capitulo_id,
                    enunciado,
                    explicacao,
                    banca,
                    ano,
                    fonte,
                    dificuldade,
                    ativa
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
                """,
                (
                    topico_id,
                    capitulo_id,
                    enunciado,
                    str(
                        registro.get(
                            "explicacao",
                            ""
                        )
                        or ""
                    ).strip(),
                    str(
                        registro.get(
                            "banca",
                            ""
                        )
                        or ""
                    ).strip(),
                    ano,
                    str(
                        registro.get(
                            "fonte",
                            ""
                        )
                        or ""
                    ).strip(),
                    str(
                        registro.get(
                            "dificuldade",
                            "Não informada"
                        )
                        or "Não informada"
                    ).strip(),
                )
            )

            questao_id = (
                cursor.lastrowid
            )

            for alternativa in alternativas:
                conexao.execute(
                    """
                    INSERT INTO alternativas_questoes (
                        questao_id,
                        letra,
                        texto,
                        correta,
                        ordem
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        questao_id,
                        alternativa[
                            "letra"
                        ],
                        alternativa[
                            "texto"
                        ],
                        alternativa[
                            "correta"
                        ],
                        alternativa[
                            "ordem"
                        ],
                    )
                )

            ids.append(
                questao_id
            )

    return ids


def obter_questao(
    questao_id
):
    with conectar() as conexao:
        linha = conexao.execute(
            """
            SELECT
                q.id,
                q.topico_id,
                q.capitulo_id,
                d.id,
                d.nome,
                t.nome,
                c.nome,
                q.enunciado,
                q.explicacao,
                q.banca,
                q.ano,
                q.fonte,
                q.dificuldade,
                q.ativa,
                COALESCE(q.excluida, 0),
                q.criado_em,
                q.atualizado_em,
                COALESCE(q.analise_pendente, 0),
                q.analise_solicitada_em
            FROM questoes q
            JOIN topicos t
                ON t.id = q.topico_id
            JOIN disciplinas d
                ON d.id = t.disciplina_id
            LEFT JOIN capitulos_topico c
                ON c.id = q.capitulo_id
            WHERE q.id = ?
            """,
            (
                int(
                    questao_id
                ),
            )
        ).fetchone()

        if linha is None:
            return None

        alternativas = conexao.execute(
            """
            SELECT
                letra,
                texto,
                correta,
                ordem
            FROM alternativas_questoes
            WHERE questao_id = ?
            ORDER BY ordem, letra
            """,
            (
                int(
                    questao_id
                ),
            )
        ).fetchall()

    return {
        "id": linha[0],
        "topico_id": linha[1],
        "capitulo_id": linha[2],
        "disciplina_id": linha[3],
        "disciplina": linha[4],
        "topico": linha[5],
        "capitulo": linha[6] or "",
        "enunciado": linha[7],
        "explicacao": linha[8] or "",
        "banca": linha[9] or "",
        "ano": linha[10],
        "fonte": linha[11] or "",
        "dificuldade": (
            linha[12]
            or "Não informada"
        ),
        "ativa": bool(
            linha[13]
        ),
        "excluida": bool(
            linha[14]
        ),
        "criado_em": linha[15],
        "atualizado_em": linha[16],
        "analise_pendente": bool(
            linha[17]
        ),
        "analise_solicitada_em": linha[18],
        "alternativas": [
            {
                "letra": alternativa[0],
                "texto": alternativa[1],
                "correta": bool(
                    alternativa[2]
                ),
                "ordem": alternativa[3],
            }
            for alternativa
            in alternativas
        ],
    }


def definir_questao_analise_pendente(
    questao_id,
    marcada=True
):
    marcada = bool(
        marcada
    )

    with conectar() as conexao:
        cursor = conexao.execute(
            """
            UPDATE questoes
            SET
                analise_pendente = ?,
                analise_solicitada_em = CASE
                    WHEN ? = 1
                    THEN datetime('now', 'localtime')
                    ELSE NULL
                END,
                atualizado_em = datetime('now', 'localtime')
            WHERE
                id = ?
                AND COALESCE(excluida, 0) = 0
            """,
            (
                1 if marcada else 0,
                1 if marcada else 0,
                int(
                    questao_id
                ),
            )
        )

        return cursor.rowcount > 0


def atualizar_questao(
    questao_id,
    topico_id,
    enunciado,
    alternativas,
    explicacao="",
    banca="",
    ano=None,
    fonte="",
    dificuldade="Não informada",
    ativa=True,
    capitulo_id=None
):
    enunciado = str(
        enunciado
    ).strip()

    if not enunciado:
        raise ValueError(
            "O enunciado da questão não pode ficar vazio."
        )

    alternativas = (
        _normalizar_alternativas_questao(
            alternativas
        )
    )

    if ano in (
        "",
        None,
        0
    ):
        ano = None
    else:
        ano = int(
            ano
        )

    with conectar() as conexao:
        topico_id, capitulo_id = _resolver_classificacao_questao(
            topico_id,
            capitulo_id,
            conexao
        )
        cursor = conexao.execute(
            """
            UPDATE questoes
            SET
                topico_id = ?,
                capitulo_id = ?,
                enunciado = ?,
                explicacao = ?,
                banca = ?,
                ano = ?,
                fonte = ?,
                dificuldade = ?,
                ativa = ?,
                atualizado_em = datetime(
                    'now',
                    'localtime'
                )
            WHERE id = ?
            """,
            (
                topico_id,
                capitulo_id,
                enunciado,
                str(
                    explicacao
                    or ""
                ).strip(),
                str(
                    banca
                    or ""
                ).strip(),
                ano,
                str(
                    fonte
                    or ""
                ).strip(),
                str(
                    dificuldade
                    or "Não informada"
                ).strip(),
                1 if ativa else 0,
                int(
                    questao_id
                ),
            )
        )

        if cursor.rowcount <= 0:
            return False

        conexao.execute(
            """
            DELETE FROM alternativas_questoes
            WHERE questao_id = ?
            """,
            (
                int(
                    questao_id
                ),
            )
        )

        for alternativa in alternativas:
            conexao.execute(
                """
                INSERT INTO alternativas_questoes (
                    questao_id,
                    letra,
                    texto,
                    correta,
                    ordem
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    int(
                        questao_id
                    ),
                    alternativa[
                        "letra"
                    ],
                    alternativa[
                        "texto"
                    ],
                    alternativa[
                        "correta"
                    ],
                    alternativa[
                        "ordem"
                    ],
                )
            )

        return True


def obter_integridade_questao(
    questao_id
):
    questao_id = int(
        questao_id
    )

    with conectar() as conexao:
        questao = conexao.execute(
            """
            SELECT
                id,
                ativa,
                COALESCE(excluida, 0)
            FROM questoes
            WHERE id = ?
            """,
            (
                questao_id,
            )
        ).fetchone()

        if questao is None:
            return None

        tentativas = conexao.execute(
            """
            SELECT COUNT(*)
            FROM tentativas_questoes
            WHERE
                COALESCE(
                    questao_id_snapshot,
                    questao_id
                ) = ?
            """,
            (
                questao_id,
            )
        ).fetchone()[0]

    return {
        "questao_id": questao_id,
        "ativa": bool(
            questao[1]
        ),
        "excluida": bool(
            questao[2]
        ),
        "tentativas": int(
            tentativas
            or 0
        ),
        "possui_historico": (
            int(
                tentativas
                or 0
            ) > 0
        ),
    }


def arquivar_questao(
    questao_id
):
    with conectar() as conexao:
        cursor = conexao.execute(
            """
            UPDATE questoes
            SET
                ativa = 0,
                excluida = 0,
                atualizado_em = datetime(
                    'now',
                    'localtime'
                )
            WHERE id = ?
            """,
            (
                int(
                    questao_id
                ),
            )
        )

        return (
            cursor.rowcount > 0
        )


def reativar_questao(
    questao_id
):
    with conectar() as conexao:
        cursor = conexao.execute(
            """
            UPDATE questoes
            SET
                ativa = 1,
                excluida = 0,
                excluida_em = NULL,
                atualizado_em = datetime(
                    'now',
                    'localtime'
                )
            WHERE id = ?
            """,
            (
                int(
                    questao_id
                ),
            )
        )

        return (
            cursor.rowcount > 0
        )


def remover_questao_com_integridade(
    questao_id
):
    """
    Questão com tentativa nunca é apagada fisicamente.
    Sem tentativas, a exclusão definitiva continua permitida.
    """

    integridade = obter_integridade_questao(
        questao_id
    )

    if integridade is None:
        return {
            "sucesso": False,
            "acao": "nao_encontrada",
            "tentativas": 0,
        }

    if integridade[
        "possui_historico"
    ]:
        sucesso = arquivar_questao(
            questao_id
        )

        return {
            "sucesso": sucesso,
            "acao": "arquivada",
            "tentativas": integridade[
                "tentativas"
            ],
        }

    with conectar() as conexao:
        cursor = conexao.execute(
            """
            DELETE FROM questoes
            WHERE id = ?
            """,
            (
                int(
                    questao_id
                ),
            )
        )

        sucesso = (
            cursor.rowcount > 0
        )

    return {
        "sucesso": sucesso,
        "acao": "excluida",
        "tentativas": 0,
    }


def mover_questao_para_lixeira(
    questao_id
):
    with conectar() as conexao:
        cursor = conexao.execute(
            """
            UPDATE questoes
            SET
                ativa = 0,
                excluida = 1,
                excluida_em = datetime(
                    'now',
                    'localtime'
                ),
                atualizado_em = datetime(
                    'now',
                    'localtime'
                )
            WHERE id = ?
            """,
            (
                int(
                    questao_id
                ),
            )
        )
        return (
            cursor.rowcount > 0
        )


def restaurar_questao_da_lixeira(
    questao_id,
    reativar=True
):
    with conectar() as conexao:
        cursor = conexao.execute(
            """
            UPDATE questoes
            SET
                excluida = 0,
                excluida_em = NULL,
                ativa = ?,
                atualizado_em = datetime(
                    'now',
                    'localtime'
                )
            WHERE id = ?
            """,
            (
                1 if reativar else 0,
                int(
                    questao_id
                ),
            )
        )
        return (
            cursor.rowcount > 0
        )


def excluir_questao_permanentemente(
    questao_id
):
    with conectar() as conexao:
        conexao.execute(
            """
            DELETE FROM alternativas_questoes
            WHERE questao_id = ?
            """,
            (
                int(
                    questao_id
                ),
            )
        )
        cursor = conexao.execute(
            """
            DELETE FROM questoes
            WHERE id = ?
            """,
            (
                int(
                    questao_id
                ),
            )
        )
        return (
            cursor.rowcount > 0
        )


def listar_questoes_lixeira(
    concurso_id=None
):
    if concurso_id is None:
        concurso_id = (
            obter_concurso_ativo()[0]
        )

    with conectar() as conexao:
        linhas = conexao.execute(
            """
            SELECT
                q.id,
                q.topico_id,
                d.nome,
                t.nome,
                q.enunciado,
                q.banca,
                q.ano,
                q.fonte,
                q.dificuldade,
                q.ativa,
                COALESCE(q.excluida, 0),
                q.excluida_em,
                COALESCE(tc.pausado, 0) AS topico_pausado,
                COALESCE(dc.pausado, 0) AS disciplina_pausada
            FROM questoes q
            JOIN topicos t
                ON t.id = q.topico_id
            JOIN disciplinas d
                ON d.id = t.disciplina_id
            JOIN disciplina_concurso_inclusao dc
                ON dc.disciplina_id = d.id
                AND dc.concurso_id = ?
                AND dc.incluido = 1
            JOIN topico_concurso_importancia tc
                ON tc.topico_id = t.id
                AND tc.concurso_id = ?
                AND tc.incluido = 1
            WHERE COALESCE(q.excluida, 0) = 1
            ORDER BY
                COALESCE(q.excluida_em, q.atualizado_em, q.criado_em) DESC,
                d.nome COLLATE NOCASE,
                t.nome COLLATE NOCASE,
                q.id DESC
            """,
            (
                concurso_id,
                concurso_id,
            )
        ).fetchall()

    return [
        {
            "id": linha[0],
            "topico_id": linha[1],
            "disciplina": linha[2],
            "topico": linha[3],
            "enunciado": linha[4],
            "banca": linha[5] or "",
            "ano": linha[6],
            "fonte": linha[7] or "",
            "dificuldade": (
                linha[8]
                or "Não informada"
            ),
            "ativa": bool(
                linha[9]
            ),
            "excluida": bool(
                linha[10]
            ),
            "excluida_em": linha[11],
            "topico_pausado": bool(
                linha[12]
            ),
            "disciplina_pausada": bool(
                linha[13]
            ),
        }
        for linha in linhas
    ]


def excluir_questao(
    questao_id
):
    """
    Mantido por compatibilidade.
    Agora envia a questão para a lixeira lógica do banco.
    """

    return mover_questao_para_lixeira(
        questao_id
    )


def listar_questoes(
    concurso_id=None,
    incluir_inativas=False,
    incluir_topicos_pausados=False,
    incluir_disciplinas_pausadas=False
):
    if concurso_id is None:
        concurso_id = (
            obter_concurso_ativo()[0]
        )

    filtro_ativa = (
        ""
        if incluir_inativas
        else "AND q.ativa = 1"
    )
    filtro_pausa = (
        ""
        if incluir_topicos_pausados
        else "AND COALESCE(tc.pausado, 0) = 0"
    )
    filtro_disciplina_pausa = (
        ""
        if incluir_disciplinas_pausadas
        else "AND COALESCE(dc.pausado, 0) = 0"
    )

    with conectar() as conexao:
        linhas = conexao.execute(
            f"""
            SELECT
                q.id,
                q.topico_id,
                d.nome,
                t.nome,
                q.enunciado,
                q.banca,
                q.ano,
                q.fonte,
                q.dificuldade,
                q.ativa,
                (
                    SELECT aq.letra
                    FROM alternativas_questoes aq
                    WHERE
                        aq.questao_id = q.id
                        AND aq.correta = 1
                    ORDER BY aq.ordem
                    LIMIT 1
                ) AS gabarito,
                (
                    SELECT COUNT(*)
                    FROM alternativas_questoes aq2
                    WHERE aq2.questao_id = q.id
                ) AS quantidade_alternativas,
                CASE
                    WHEN TRIM(
                        COALESCE(
                            q.explicacao,
                            ''
                        )
                    ) <> ''
                    THEN 1
                    ELSE 0
                END AS tem_explicacao,
                COALESCE(tc.pausado, 0) AS topico_pausado,
                COALESCE(dc.pausado, 0) AS disciplina_pausada,
                COALESCE(q.analise_pendente, 0) AS analise_pendente,
                q.analise_solicitada_em
            FROM questoes q
            JOIN topicos t
                ON t.id = q.topico_id
            JOIN disciplinas d
                ON d.id = t.disciplina_id
            JOIN disciplina_concurso_inclusao dc
                ON dc.disciplina_id = d.id
                AND dc.concurso_id = ?
                AND dc.incluido = 1
                {filtro_disciplina_pausa}
            JOIN topico_concurso_importancia tc
                ON tc.topico_id = t.id
                AND tc.concurso_id = ?
                AND tc.incluido = 1
            WHERE 1 = 1
                AND COALESCE(q.excluida, 0) = 0
                {filtro_ativa}
                {filtro_pausa}
            ORDER BY
                d.nome COLLATE NOCASE,
                t.nome COLLATE NOCASE,
                q.id
            """,
            (
                concurso_id,
                concurso_id,
            )
        ).fetchall()

    return [
        {
            "id": linha[0],
            "topico_id": linha[1],
            "disciplina": linha[2],
            "topico": linha[3],
            "enunciado": linha[4],
            "banca": linha[5] or "",
            "ano": linha[6],
            "fonte": linha[7] or "",
            "dificuldade": (
                linha[8]
                or "Não informada"
            ),
            "ativa": bool(
                linha[9]
            ),
            "gabarito": linha[10] or "",
            "quantidade_alternativas": int(
                linha[11] or 0
            ),
            "tem_explicacao": bool(
                linha[12]
            ),
            "topico_pausado": bool(
                linha[13]
            ),
            "disciplina_pausada": bool(
                linha[14]
            ),
            "analise_pendente": bool(
                linha[15]
            ),
            "analise_solicitada_em": linha[16],
        }
        for linha in linhas
    ]




def obter_resumo_integridade_historica_questoes(
    concurso_id=None
):
    """
    Resume a cobertura dos snapshots históricos das tentativas.

    - resposta: snapshot verdadeiro criado no momento da resposta;
    - migrado: tentativa antiga congelada com a versão disponível quando
      a migração de integridade foi executada;
    - sem_snapshot: registro que não possui conteúdo histórico suficiente.
    """

    if concurso_id is None:
        concurso_id = obter_concurso_ativo()[0]

    concurso_id = int(concurso_id)

    with conectar() as conexao:
        linha = conexao.execute(
            """
            SELECT
                COUNT(*) AS total,
                SUM(
                    CASE
                        WHEN snapshot_origem = 'resposta'
                        THEN 1
                        ELSE 0
                    END
                ) AS originais,
                SUM(
                    CASE
                        WHEN snapshot_origem = 'migrado'
                        THEN 1
                        ELSE 0
                    END
                ) AS migrados,
                SUM(
                    CASE
                        WHEN enunciado_snapshot IS NULL
                        THEN 1
                        ELSE 0
                    END
                ) AS sem_snapshot
            FROM tentativas_questoes
            WHERE concurso_id = ?
            """,
            (concurso_id,)
        ).fetchone()

        arquivadas = conexao.execute(
            """
            SELECT COUNT(DISTINCT q.id)
            FROM questoes q
            WHERE
                q.ativa = 0
                AND EXISTS (
                    SELECT 1
                    FROM tentativas_questoes tq
                    WHERE
                        tq.concurso_id = ?
                        AND COALESCE(
                            tq.questao_id_snapshot,
                            tq.questao_id
                        ) = q.id
                )
            """,
            (concurso_id,)
        ).fetchone()[0]

    total = int(linha[0] or 0)
    originais = int(linha[1] or 0)
    migrados = int(linha[2] or 0)
    sem_snapshot = int(linha[3] or 0)
    arquivadas = int(arquivadas or 0)

    protegidas = max(
        0,
        total - sem_snapshot
    )

    cobertura = (
        round(
            100.0 * protegidas / total,
            1
        )
        if total > 0
        else 100.0
    )

    if total <= 0:
        status = 'Sem histórico'
        estado = 'empty'
    elif sem_snapshot > 0:
        status = 'Atenção'
        estado = 'warning'
    elif migrados > 0:
        status = 'Protegida · legado identificado'
        estado = 'legacy'
    else:
        status = 'Protegida'
        estado = 'ok'

    return {
        'total_tentativas': total,
        'snapshots_originais': originais,
        'snapshots_migrados': migrados,
        'sem_snapshot': sem_snapshot,
        'protegidas': protegidas,
        'cobertura_percentual': cobertura,
        'questoes_arquivadas_com_historico': arquivadas,
        'status': status,
        'estado': estado,
    }

def _pontuacao_recencia_dominio(
    data_texto
):
    if not data_texto:
        return 0.0, None

    texto = str(
        data_texto
    )[:10]

    try:
        data_evento = datetime.strptime(
            texto,
            "%Y-%m-%d"
        ).date()
    except Exception:
        return 0.0, None

    dias = max(
        0,
        (
            date.today()
            - data_evento
        ).days
    )

    if dias <= 7:
        score = 100.0
    elif dias <= 14:
        score = 90.0
    elif dias <= 30:
        score = 75.0
    elif dias <= 45:
        score = 60.0
    elif dias <= 60:
        score = 45.0
    elif dias <= 90:
        score = 25.0
    else:
        score = 10.0

    return score, dias


def _classificar_nivel_dominio(
    score,
    tentativas_efetivas
):
    if int(
        tentativas_efetivas
        or 0
    ) <= 0:
        return (
            "Sem evidência",
            0
        )

    score = float(
        score
        or 0.0
    )

    if score < 30:
        return (
            "Crítico",
            1
        )

    if score < 50:
        return (
            "Frágil",
            2
        )

    if score < 70:
        return (
            "Em desenvolvimento",
            3
        )

    if score < 85:
        return (
            "Consolidando",
            4
        )

    if score < 95:
        return (
            "Dominado",
            5
        )

    return (
        "Domínio forte",
        6
    )


def _qualidade_evidencia_dominio(
    tentativas,
    dias_ativos,
    questoes_unicas,
    revisoes_ponderadas=0.0
):
    """Classifica a robustez da evidência usada pelo Domínio V2."""

    tentativas = int(
        tentativas
        or 0
    )
    dias_ativos = int(
        dias_ativos
        or 0
    )
    questoes_unicas = int(
        questoes_unicas
        or 0
    )
    revisoes_ponderadas = float(
        revisoes_ponderadas
        or 0.0
    )

    if tentativas <= 0:
        return "Sem evidência"

    if (
        tentativas < 5
        or questoes_unicas < 2
    ):
        return "Muito limitada"

    if (
        tentativas < 10
        or dias_ativos < 2
        or questoes_unicas < 3
    ):
        return "Limitada"

    if (
        tentativas < 20
        or dias_ativos < 3
        or questoes_unicas < 5
    ):
        return "Moderada"

    if (
        tentativas >= 40
        and dias_ativos >= 5
        and questoes_unicas >= 10
        and revisoes_ponderadas >= 2.0
    ):
        return "Forte"

    return "Boa"


def _limitar_score_dominio(
    valor
):
    return max(
        0.0,
        min(
            100.0,
            float(
                valor
                or 0.0
            )
        )
    )


def obter_indices_dominio_topicos(
    concurso_id=None
):
    """
    Índice de Domínio V2.

    A V2 separa desempenho de robustez da evidência e evita tratar um
    percentual alto obtido em poucas questões como domínio consolidado.

    Componentes do score bruto:
    - desempenho recente: 30%
    - variedade/cobertura: 20%
    - estabilidade temporal: 15%
    - recência: 10%
    - controle de erros e recuperação: 15%
    - robustez da evidência: 10%

    Ajustes adicionais:
    - dúvidas marcadas podem reduzir até 8 pontos;
    - limites de evidência impedem níveis altos com amostra pequena,
      pouca variedade ou poucos dias independentes de prática;
    - revisões manuais/automáticas entram apenas como parte da robustez
      da evidência, sem substituir respostas reais a questões.
    """

    if concurso_id is None:
        concurso_id = (
            obter_concurso_ativo()[0]
        )

    concurso_id = int(
        concurso_id
    )

    with conectar() as conexao:
        topicos_linhas = conexao.execute(
            """
            SELECT
                t.id,
                d.id,
                d.nome,
                t.nome,
                COALESCE(
                    ct.revisoes_iniciais,
                    0
                )
            FROM topicos t
            JOIN disciplinas d
                ON d.id = t.disciplina_id
            JOIN disciplina_concurso_inclusao dc
                ON dc.disciplina_id = d.id
                AND dc.concurso_id = ?
                AND dc.incluido = 1
                AND COALESCE(dc.pausado, 0) = 0
            JOIN topico_concurso_importancia tc
                ON tc.topico_id = t.id
                AND tc.concurso_id = ?
                AND tc.incluido = 1
            LEFT JOIN controle_topico ct
                ON ct.topico_id = t.id
            ORDER BY
                d.nome COLLATE NOCASE,
                t.nome COLLATE NOCASE
            """,
            (
                concurso_id,
                concurso_id,
            )
        ).fetchall()

        questoes_linhas = conexao.execute(
            """
            SELECT
                q.id,
                q.topico_id
            FROM questoes q
            JOIN topicos t
                ON t.id = q.topico_id
            JOIN disciplinas d
                ON d.id = t.disciplina_id
            JOIN disciplina_concurso_inclusao dc
                ON dc.disciplina_id = d.id
                AND dc.concurso_id = ?
                AND dc.incluido = 1
                AND COALESCE(dc.pausado, 0) = 0
            JOIN topico_concurso_importancia tc
                ON tc.topico_id = t.id
                AND tc.concurso_id = ?
                AND tc.incluido = 1
            WHERE q.ativa = 1
            """,
            (
                concurso_id,
                concurso_id,
            )
        ).fetchall()

        tentativas_linhas = conexao.execute(
            """
            SELECT
                COALESCE(
                    tq.questao_id_snapshot,
                    tq.questao_id
                ) AS questao_ref,
                COALESCE(
                    tq.topico_id_snapshot,
                    q.topico_id
                ) AS topico_ref,
                tq.respondida_em,
                tq.correta,
                tq.id,
                COALESCE(
                    tq.marcada_duvida,
                    0
                )
            FROM tentativas_questoes tq
            LEFT JOIN questoes q
                ON q.id = tq.questao_id
            WHERE
                tq.concurso_id = ?
                AND tq.correta IS NOT NULL
                AND COALESCE(
                    tq.topico_id_snapshot,
                    q.topico_id
                ) IS NOT NULL
            ORDER BY
                tq.respondida_em DESC,
                tq.id DESC
            """,
            (
                concurso_id,
            )
        ).fetchall()

        revisoes_linhas = conexao.execute(
            """
            SELECT
                r.topico_id,
                r.data,
                r.questoes,
                r.acertos,
                COALESCE(
                    r.origem,
                    'manual'
                ),
                r.confianca
            FROM revisoes r
            JOIN topicos t
                ON t.id = r.topico_id
            JOIN disciplinas d
                ON d.id = t.disciplina_id
            JOIN disciplina_concurso_inclusao dc
                ON dc.disciplina_id = d.id
                AND dc.concurso_id = ?
                AND dc.incluido = 1
                AND COALESCE(dc.pausado, 0) = 0
            JOIN topico_concurso_importancia tc
                ON tc.topico_id = t.id
                AND tc.concurso_id = ?
                AND tc.incluido = 1
            ORDER BY
                r.data DESC,
                r.id DESC
            """,
            (
                concurso_id,
                concurso_id,
            )
        ).fetchall()

    topicos = {
        int(
            linha[0]
        ): {
            "topico_id": int(
                linha[0]
            ),
            "disciplina_id": int(
                linha[1]
            ),
            "disciplina": linha[2],
            "topico": linha[3],
            "revisoes_iniciais": int(
                linha[4]
                or 0
            ),
        }
        for linha in topicos_linhas
    }

    questoes_ativas = {
        topico_id: set()
        for topico_id in topicos
    }

    for questao_id, topico_id in questoes_linhas:
        topico_id = int(
            topico_id
        )

        if topico_id in questoes_ativas:
            questoes_ativas[
                topico_id
            ].add(
                int(
                    questao_id
                )
            )

    tentativas_topico = {
        topico_id: []
        for topico_id in topicos
    }

    historico_questao = {
        topico_id: {}
        for topico_id in topicos
    }

    revisoes_topico = {
        topico_id: []
        for topico_id in topicos
    }

    for linha in tentativas_linhas:
        questao_ref = linha[0]
        topico_ref = linha[1]

        if (
            questao_ref is None
            or topico_ref is None
        ):
            continue

        topico_ref = int(
            topico_ref
        )

        if topico_ref not in topicos:
            continue

        registro = {
            "questao_id": int(
                questao_ref
            ),
            "respondida_em": linha[2],
            "correta": bool(
                linha[3]
            ),
            "tentativa_id": int(
                linha[4]
            ),
            "duvida": bool(
                linha[5]
            ),
        }

        tentativas_topico[
            topico_ref
        ].append(
            registro
        )

        historico_questao[
            topico_ref
        ].setdefault(
            int(
                questao_ref
            ),
            []
        ).append(
            registro
        )

    for linha in revisoes_linhas:
        topico_ref = int(
            linha[0]
        )

        if topico_ref not in revisoes_topico:
            continue

        revisoes_topico[
            topico_ref
        ].append({
            "data": linha[1],
            "questoes": int(
                linha[2]
                or 0
            ),
            "acertos": int(
                linha[3]
                or 0
            ),
            "origem": linha[4],
            "confianca": linha[5],
        })

    resultados = {}

    for topico_id, dados_topico in topicos.items():
        todas = tentativas_topico[
            topico_id
        ]

        total_historico = len(
            todas
        )

        # Janela operacional: o passado muito antigo não deve mascarar
        # melhora ou queda atual, mas continua valendo como evidência.
        consideradas = todas[
            :50
        ]
        recentes = consideradas[
            :15
        ]

        total = len(
            consideradas
        )
        total_recente = len(
            recentes
        )

        acertos = sum(
            1
            for item in consideradas
            if item[
                "correta"
            ]
        )
        acertos_recentes = sum(
            1
            for item in recentes
            if item[
                "correta"
            ]
        )

        desempenho_base = (
            100.0
            * acertos
            / total
            if total > 0
            else 0.0
        )

        desempenho_recente = (
            100.0
            * acertos_recentes
            / total_recente
            if total_recente > 0
            else 0.0
        )

        if total > 15:
            desempenho = (
                desempenho_recente
                * 0.65
                + desempenho_base
                * 0.35
            )
        else:
            desempenho = desempenho_base

        ativas = questoes_ativas[
            topico_id
        ]

        respondidas_ativas = {
            item[
                "questao_id"
            ]
            for item in todas
            if item[
                "questao_id"
            ] in ativas
        }

        unicas_historicas = {
            item[
                "questao_id"
            ]
            for item in todas
        }

        if ativas:
            unicas_recentes = {
                item[
                    "questao_id"
                ]
                for item in consideradas
                if item[
                    "questao_id"
                ] in ativas
            }
        else:
            unicas_recentes = {
                item[
                    "questao_id"
                ]
                for item in consideradas
            }

        cobertura = (
            100.0
            * len(
                respondidas_ativas
            )
            / len(
                ativas
            )
            if ativas
            else 0.0
        )

        alvo_variedade = (
            min(
                12,
                len(
                    ativas
                )
            )
            if ativas
            else 12
        )

        diversidade_recente = (
            100.0
            * len(
                unicas_recentes
            )
            / alvo_variedade
            if alvo_variedade > 0
            else 0.0
        )
        diversidade_recente = min(
            100.0,
            diversidade_recente
        )

        if ativas:
            variedade = (
                cobertura
                * 0.55
                + diversidade_recente
                * 0.45
            )
        else:
            variedade = diversidade_recente

        # --------------------------------------------------
        # Estabilidade temporal
        # --------------------------------------------------

        por_dia = {}

        for item in consideradas:
            dia = str(
                item[
                    "respondida_em"
                ]
                or ""
            )[:10]

            if not dia:
                continue

            acumulado = por_dia.setdefault(
                dia,
                [
                    0,
                    0,
                ]
            )
            acumulado[0] += 1
            acumulado[1] += (
                1
                if item[
                    "correta"
                ]
                else 0
            )

        dias_ordenados = sorted(
            por_dia.keys(),
            reverse=True
        )[
            :6
        ]

        percentuais_dia = [
            (
                100.0
                * por_dia[
                    dia
                ][1]
                / por_dia[
                    dia
                ][0]
            )
            for dia in dias_ordenados
            if por_dia[
                dia
            ][0] > 0
        ]

        dias_ativos = len(
            percentuais_dia
        )

        dias_ativos_historicos = len({
            str(
                item[
                    "respondida_em"
                ]
                or ""
            )[:10]
            for item in todas
            if str(
                item[
                    "respondida_em"
                ]
                or ""
            )[:10]
        })

        if percentuais_dia:
            media_dias = (
                sum(
                    percentuais_dia
                )
                / len(
                    percentuais_dia
                )
            )

            variancia = (
                sum(
                    (
                        valor
                        - media_dias
                    ) ** 2
                    for valor in percentuais_dia
                )
                / len(
                    percentuais_dia
                )
            )

            desvio = math.sqrt(
                variancia
            )

            consistencia = max(
                0.0,
                100.0
                - min(
                    100.0,
                    desvio
                    * 2.0
                )
            )

            evidencia_temporal_recente = min(
                100.0,
                dias_ativos
                * 20.0
            )

            estabilidade = (
                evidencia_temporal_recente
                * (
                    0.5
                    + 0.5
                    * consistencia
                    / 100.0
                )
            )
        else:
            consistencia = 0.0
            estabilidade = 0.0

        ultima_resposta = (
            consideradas[0][
                "respondida_em"
            ]
            if consideradas
            else None
        )

        recencia, dias_desde_ultima = (
            _pontuacao_recencia_dominio(
                ultima_resposta
            )
        )

        # --------------------------------------------------
        # Erros, recorrência e recuperação
        # --------------------------------------------------

        criticas = 0
        recorrentes = 0
        recuperacao = 0
        recuperadas = 0
        erros_isolados = 0
        dominadas = 0

        for questao_id in ativas:
            historico = historico_questao[
                topico_id
            ].get(
                questao_id,
                []
            )

            if not historico:
                continue

            total_q = len(
                historico
            )
            acertos_q = sum(
                1
                for item in historico
                if item[
                    "correta"
                ]
            )
            erros_q = (
                total_q
                - acertos_q
            )

            taxa_q = (
                100.0
                * acertos_q
                / total_q
                if total_q > 0
                else 0.0
            )

            erros_consecutivos = 0

            for item in historico:
                if not item[
                    "correta"
                ]:
                    erros_consecutivos += 1
                else:
                    break

            acertos_consecutivos = 0

            for item in historico:
                if item[
                    "correta"
                ]:
                    acertos_consecutivos += 1
                else:
                    break

            if (
                total_q >= 3
                and acertos_consecutivos >= 3
            ):
                dominadas += 1

            if erros_q <= 0:
                continue

            # A V2 reconhece recuperação real: erros antigos deixam de
            # manter uma questão artificialmente crítica após sequência
            # recente consistente de acertos.
            if acertos_consecutivos >= 3:
                recuperadas += 1
                continue

            if acertos_consecutivos in (
                1,
                2,
            ):
                recuperacao += 1
                continue

            if (
                erros_consecutivos >= 3
                or (
                    erros_q >= 3
                    and taxa_q < 50.0
                )
            ):
                criticas += 1

            elif (
                erros_consecutivos >= 2
                or (
                    erros_q >= 2
                    and taxa_q < 70.0
                )
            ):
                recorrentes += 1

            else:
                erros_isolados += 1

        base_questoes_erro = max(
            1,
            len(
                respondidas_ativas
            )
        )

        penalidade_absoluta = (
            criticas
            * 18.0
            + recorrentes
            * 10.0
            + recuperacao
            * 4.0
            + erros_isolados
            * 1.5
        )

        penalidade_proporcional = min(
            35.0,
            (
                (
                    criticas
                    + recorrentes
                    * 0.60
                    + recuperacao
                    * 0.25
                )
                / base_questoes_erro
            )
            * 35.0
        )

        bonus_recuperacao = min(
            10.0,
            (
                recuperadas
                / base_questoes_erro
            )
            * 16.0
        )

        controle_erros = _limitar_score_dominio(
            100.0
            - penalidade_absoluta
            - penalidade_proporcional
            + bonus_recuperacao
        )

        # --------------------------------------------------
        # Robustez da evidência
        # --------------------------------------------------

        revisoes = revisoes_topico[
            topico_id
        ]

        revisoes_ponderadas = 0.0

        for revisao in revisoes:
            confianca = str(
                revisao.get(
                    "confianca"
                )
                or ""
            ).strip().lower()

            if confianca == "muito_baixa":
                peso_revisao = 0.25
            elif confianca == "baixa":
                peso_revisao = 0.50
            else:
                peso_revisao = 1.0

            revisoes_ponderadas += peso_revisao

        revisoes_ponderadas += min(
            4,
            int(
                dados_topico.get(
                    "revisoes_iniciais",
                    0
                )
                or 0
            )
        ) * 0.40

        score_volume = min(
            100.0,
            total_historico
            / 30.0
            * 100.0
        )

        score_unicas = min(
            100.0,
            len(
                unicas_historicas
            )
            / 10.0
            * 100.0
        )

        score_dias = min(
            100.0,
            dias_ativos_historicos
            / 6.0
            * 100.0
        )

        score_revisoes = min(
            100.0,
            revisoes_ponderadas
            / 4.0
            * 100.0
        )

        evidencia = (
            score_volume
            * 0.35
            + score_unicas
            * 0.30
            + score_dias
            * 0.20
            + score_revisoes
            * 0.15
        )

        # Dúvida marcada representa menor confiança mesmo quando a
        # alternativa está correta. Ela reduz pouco, mas impede que uma
        # sequência insegura pareça domínio absoluto.
        amostra_duvida = consideradas[
            :30
        ]
        duvidas = sum(
            1
            for item in amostra_duvida
            if item.get(
                "duvida"
            )
        )
        taxa_duvida = (
            100.0
            * duvidas
            / len(
                amostra_duvida
            )
            if amostra_duvida
            else 0.0
        )
        penalidade_duvida = min(
            8.0,
            taxa_duvida
            * 0.08
        )

        if total <= 0:
            bruto = 0.0
            score_ajustado = 0.0
            score = 0.0
            limite_evidencia = 0.0
        else:
            bruto = (
                desempenho
                * 0.30
                + variedade
                * 0.20
                + estabilidade
                * 0.15
                + recencia
                * 0.10
                + controle_erros
                * 0.15
                + evidencia
                * 0.10
            )

            score_ajustado = max(
                0.0,
                bruto
                - penalidade_duvida
            )

            limite_evidencia = 100.0

            if (
                total_historico < 3
                or len(
                    unicas_historicas
                ) < 2
            ):
                limite_evidencia = min(
                    limite_evidencia,
                    49.0
                )

            elif (
                total_historico < 7
                or dias_ativos_historicos < 2
            ):
                limite_evidencia = min(
                    limite_evidencia,
                    59.0
                )

            elif (
                total_historico < 12
                or len(
                    unicas_historicas
                ) < 3
            ):
                limite_evidencia = min(
                    limite_evidencia,
                    69.0
                )

            elif (
                total_historico < 20
                or len(
                    unicas_historicas
                ) < 4
                or dias_ativos_historicos < 3
            ):
                limite_evidencia = min(
                    limite_evidencia,
                    84.0
                )

            # Dominado exige variedade e repetição temporal mínimas.
            if (
                score_ajustado >= 85.0
                and (
                    total_historico < 20
                    or len(
                        unicas_historicas
                    ) < 4
                    or dias_ativos_historicos < 3
                    or variedade < 45.0
                    or criticas > 0
                    or recorrentes > 0
                    or taxa_duvida > 30.0
                )
            ):
                limite_evidencia = min(
                    limite_evidencia,
                    84.0
                )

            # Domínio forte exige evidência bem mais robusta e ausência
            # de fragilidade atualmente aberta.
            if (
                score_ajustado >= 95.0
                and (
                    total_historico < 40
                    or len(
                        unicas_historicas
                    ) < 8
                    or dias_ativos_historicos < 5
                    or variedade < 70.0
                    or criticas > 0
                    or recorrentes > 0
                    or recencia < 75.0
                    or taxa_duvida > 20.0
                )
            ):
                limite_evidencia = min(
                    limite_evidencia,
                    94.0
                )

            score = min(
                score_ajustado,
                limite_evidencia
            )

        score = round(
            _limitar_score_dominio(
                score
            ),
            1
        )

        nivel, ordem_nivel = (
            _classificar_nivel_dominio(
                score,
                total
            )
        )

        qualidade = (
            _qualidade_evidencia_dominio(
                total_historico,
                dias_ativos_historicos,
                len(
                    unicas_historicas
                ),
                revisoes_ponderadas
            )
        )

        pontos_fortes = []
        motivos = []

        if total <= 0:
            motivos.append(
                "Ainda não há respostas internas efetivas neste tópico."
            )
        else:
            if desempenho >= 80.0:
                pontos_fortes.append(
                    "desempenho recente forte"
                )

            if variedade >= 70.0:
                pontos_fortes.append(
                    "boa variedade de questões"
                )

            if estabilidade >= 70.0:
                pontos_fortes.append(
                    "resultado estável em dias diferentes"
                )

            if recuperadas > 0:
                pontos_fortes.append(
                    (
                        f"{recuperadas} erro(s) recuperado(s) "
                        "com sequência de acertos"
                    )
                )

            if recencia >= 90.0:
                pontos_fortes.append(
                    "prática recente"
                )

            if evidencia >= 70.0:
                pontos_fortes.append(
                    "evidência quantitativa consistente"
                )

            if limite_evidencia < 100.0:
                motivos.append(
                    (
                        "A nota está limitada pela quantidade, variedade "
                        "ou distribuição temporal da evidência."
                    )
                )

            if criticas > 0:
                motivos.append(
                    f"{criticas} questão(ões) com erro crítico aberto."
                )

            if recorrentes > 0:
                motivos.append(
                    f"{recorrentes} questão(ões) com erro recorrente aberto."
                )

            if recuperacao > 0:
                motivos.append(
                    f"{recuperacao} questão(ões) ainda em recuperação."
                )

            if variedade < 50.0 and (
                ativas
                or unicas_historicas
            ):
                motivos.append(
                    "A variedade de questões ainda é baixa para confirmar domínio."
                )

            if taxa_duvida >= 20.0:
                motivos.append(
                    (
                        f"{taxa_duvida:.0f}% das respostas recentes foram "
                        "marcadas com dúvida."
                    )
                )

            if (
                dias_desde_ultima is not None
                and dias_desde_ultima > 30
            ):
                motivos.append(
                    (
                        f"Última resposta interna há "
                        f"{dias_desde_ultima} dias."
                    )
                )

            if evidencia < 45.0:
                motivos.append(
                    "A robustez da evidência ainda é limitada."
                )

            if not pontos_fortes:
                pontos_fortes.append(
                    "evidência ainda em formação"
                )

            if not motivos:
                motivos.append(
                    "Nenhum limitador relevante está aberto no momento."
                )

        resultados[
            topico_id
        ] = {
            **dados_topico,
            "versao_indice": "dominio_v2",
            "score": score,
            "score_bruto": round(
                bruto,
                1
            ),
            "score_ajustado": round(
                score_ajustado,
                1
            ),
            "nivel": nivel,
            "ordem_nivel": ordem_nivel,
            "qualidade_evidencia": qualidade,
            "desempenho": round(
                desempenho,
                1
            ),
            "desempenho_base": round(
                desempenho_base,
                1
            ),
            "desempenho_recente": round(
                desempenho_recente,
                1
            ),
            "variedade": round(
                _limitar_score_dominio(
                    variedade
                ),
                1
            ),
            "diversidade_recente": round(
                diversidade_recente,
                1
            ),
            "cobertura": round(
                min(
                    100.0,
                    cobertura
                ),
                1
            ),
            "estabilidade": round(
                estabilidade,
                1
            ),
            "consistencia": round(
                consistencia,
                1
            ),
            "recencia": round(
                recencia,
                1
            ),
            "controle_erros": round(
                controle_erros,
                1
            ),
            "evidencia": round(
                evidencia,
                1
            ),
            "score_volume": round(
                score_volume,
                1
            ),
            "score_unicas": round(
                score_unicas,
                1
            ),
            "score_dias": round(
                score_dias,
                1
            ),
            "score_revisoes": round(
                score_revisoes,
                1
            ),
            "tentativas": total,
            "tentativas_historicas": total_historico,
            "acertos": acertos,
            "dias_ativos": dias_ativos,
            "dias_ativos_historicos": dias_ativos_historicos,
            "questoes_ativas": len(
                ativas
            ),
            "questoes_respondidas": len(
                respondidas_ativas
            ),
            "questoes_unicas": len(
                unicas_historicas
            ),
            "questoes_dominadas": dominadas,
            "criticas": criticas,
            "recorrentes": recorrentes,
            "recuperacao": recuperacao,
            "recuperadas": recuperadas,
            "erros_isolados": erros_isolados,
            "duvidas": duvidas,
            "taxa_duvida": round(
                taxa_duvida,
                1
            ),
            "penalidade_duvida": round(
                penalidade_duvida,
                1
            ),
            "revisoes": len(
                revisoes
            ),
            "revisoes_ponderadas": round(
                revisoes_ponderadas,
                2
            ),
            "ultima_resposta": (
                ultima_resposta
            ),
            "dias_desde_ultima": (
                dias_desde_ultima
            ),
            "limite_evidencia": round(
                limite_evidencia,
                1
            ),
            "pontos_fortes": pontos_fortes,
            "motivos": motivos,
            "pesos": {
                "desempenho": 30,
                "variedade": 20,
                "estabilidade": 15,
                "recencia": 10,
                "controle_erros": 15,
                "evidencia": 10,
            },
        }

    return resultados


def obter_indice_dominio_topico(
    topico_id,
    concurso_id=None
):
    topico_id = int(
        topico_id
    )

    indices = obter_indices_dominio_topicos(
        concurso_id
    )

    if topico_id in indices:
        return indices[
            topico_id
        ]

    return {
        "topico_id": topico_id,
        "versao_indice": "dominio_v2",
        "score": 0.0,
        "score_bruto": 0.0,
        "score_ajustado": 0.0,
        "nivel": "Sem evidência",
        "ordem_nivel": 0,
        "qualidade_evidencia": "Sem evidência",
        "desempenho": 0.0,
        "desempenho_base": 0.0,
        "desempenho_recente": 0.0,
        "variedade": 0.0,
        "diversidade_recente": 0.0,
        "cobertura": 0.0,
        "estabilidade": 0.0,
        "consistencia": 0.0,
        "recencia": 0.0,
        "controle_erros": 100.0,
        "evidencia": 0.0,
        "score_volume": 0.0,
        "score_unicas": 0.0,
        "score_dias": 0.0,
        "score_revisoes": 0.0,
        "tentativas": 0,
        "tentativas_historicas": 0,
        "acertos": 0,
        "dias_ativos": 0,
        "dias_ativos_historicos": 0,
        "questoes_ativas": 0,
        "questoes_respondidas": 0,
        "questoes_unicas": 0,
        "questoes_dominadas": 0,
        "criticas": 0,
        "recorrentes": 0,
        "recuperacao": 0,
        "recuperadas": 0,
        "erros_isolados": 0,
        "duvidas": 0,
        "taxa_duvida": 0.0,
        "penalidade_duvida": 0.0,
        "revisoes": 0,
        "revisoes_ponderadas": 0.0,
        "ultima_resposta": None,
        "dias_desde_ultima": None,
        "limite_evidencia": 0.0,
        "pontos_fortes": [],
        "motivos": [
            "Tópico sem evidência interna disponível."
        ],
        "pesos": {
            "desempenho": 30,
            "variedade": 20,
            "estabilidade": 15,
            "recencia": 10,
            "controle_erros": 15,
            "evidencia": 10,
        },
    }


def obter_estatisticas_banco_questoes(
    concurso_id=None
):
    questoes = listar_questoes(
        concurso_id,
        incluir_inativas=False
    )

    return {
        "total": len(
            questoes
        ),
        "disciplinas": len({
            item["disciplina"]
            for item in questoes
        }),
        "topicos": len({
            item["topico_id"]
            for item in questoes
        }),
        "com_explicacao": sum(
            1
            for item in questoes
            if item[
                "tem_explicacao"
            ]
        ),
    }




def obter_perfil_selecao_inteligente_questoes(
    concurso_id=None,
    disciplina_id=None,
    topico_id=None
):
    """
    Analisa todas as questões visíveis no recorte atual e classifica
    cada uma de acordo com seu histórico individual.

    Categorias:
    - inedita
    - recorrente
    - recuperacao
    - erro
    - controle
    - dominada
    """

    if concurso_id is None:
        concurso_id = (
            obter_concurso_ativo()[0]
        )

    concurso_id = int(
        concurso_id
    )

    parametros = [
        concurso_id,
        concurso_id,
    ]

    filtros = [
        "q.ativa = 1"
    ]

    if disciplina_id is not None:
        filtros.append(
            "d.id = ?"
        )
        parametros.append(
            int(
                disciplina_id
            )
        )

    if topico_id is not None:
        filtros.append(
            "t.id = ?"
        )
        parametros.append(
            int(
                topico_id
            )
        )

    with conectar() as conexao:
        linhas = conexao.execute(
            f"""
            SELECT
                q.id,
                q.topico_id,
                d.id AS disciplina_id,
                d.nome AS disciplina,
                t.nome AS topico,
                q.enunciado,
                q.banca,
                q.ano,
                q.dificuldade
            FROM questoes q
            JOIN topicos t
                ON t.id = q.topico_id
            JOIN disciplinas d
                ON d.id = t.disciplina_id
            JOIN disciplina_concurso_inclusao dc
                ON dc.disciplina_id = d.id
                AND dc.concurso_id = ?
                AND dc.incluido = 1
                AND COALESCE(dc.pausado, 0) = 0
            JOIN topico_concurso_importancia tc
                ON tc.topico_id = t.id
                AND tc.concurso_id = ?
                AND tc.incluido = 1
                AND COALESCE(tc.pausado, 0) = 0
            WHERE
                {' AND '.join(filtros)}
            ORDER BY
                d.nome COLLATE NOCASE,
                t.nome COLLATE NOCASE,
                q.id
            """,
            parametros
        ).fetchall()

        ids_questoes = [
            int(
                linha[0]
            )
            for linha in linhas
        ]

        historico = {}

        if ids_questoes:
            marcadores = ",".join(
                "?"
                for _ in ids_questoes
            )

            tentativas = conexao.execute(
                f"""
                SELECT
                    tq.questao_id,
                    tq.correta,
                    tq.respondida_em,
                    tq.marcada_duvida,
                    tq.id
                FROM tentativas_questoes tq
                WHERE
                    tq.concurso_id = ?
                    AND tq.questao_id IN (
                        {marcadores}
                    )
                ORDER BY
                    tq.questao_id,
                    tq.respondida_em DESC,
                    tq.id DESC
                """,
                [
                    concurso_id,
                    *ids_questoes,
                ]
            ).fetchall()

            for tentativa in tentativas:
                historico.setdefault(
                    int(
                        tentativa[0]
                    ),
                    []
                ).append({
                    "correta": (
                        None
                        if tentativa[1] is None
                        else bool(
                            tentativa[1]
                        )
                    ),
                    "respondida_em": tentativa[2],
                    "duvida": bool(
                        tentativa[3]
                    ),
                    "id": tentativa[4],
                })

    questoes = []

    totais_topico = {}

    for linha in linhas:
        questao_id = int(
            linha[0]
        )
        tentativas = historico.get(
            questao_id,
            []
        )
        efetivas = [
            item
            for item in tentativas
            if item[
                "correta"
            ] is not None
        ]

        total = len(
            efetivas
        )
        acertos = sum(
            1
            for item in efetivas
            if item[
                "correta"
            ]
        )
        erros = (
            total
            - acertos
        )

        taxa = (
            100.0
            * acertos
            / total
            if total > 0
            else None
        )

        erros_consecutivos = 0

        for item in efetivas:
            if item[
                "correta"
            ]:
                break

            erros_consecutivos += 1

        acertos_consecutivos = 0

        for item in efetivas:
            if not item[
                "correta"
            ]:
                break

            acertos_consecutivos += 1

        teve_erro = (
            erros > 0
        )

        if total == 0:
            categoria = "inedita"
            categoria_rotulo = "Inédita"
            prioridade_base = 70.0

        elif (
            erros_consecutivos >= 2
            or (
                erros >= 2
                and taxa is not None
                and taxa < 70.0
            )
        ):
            categoria = "recorrente"
            categoria_rotulo = "Erro recorrente"
            prioridade_base = (
                100.0
                + 8.0
                * erros_consecutivos
                + 2.0
                * erros
            )

        elif (
            teve_erro
            and acertos_consecutivos in (
                1,
                2
            )
        ):
            categoria = "recuperacao"
            categoria_rotulo = "Em recuperação"
            prioridade_base = (
                90.0
                - 5.0
                * acertos_consecutivos
                + erros
            )

        elif teve_erro:
            categoria = "erro"
            categoria_rotulo = "Erro anterior"
            prioridade_base = (
                82.0
                + erros
            )

        elif (
            total >= 3
            and acertos_consecutivos >= 3
        ):
            categoria = "dominada"
            categoria_rotulo = "Dominada"
            prioridade_base = 25.0

        else:
            categoria = "controle"
            categoria_rotulo = "Controle"
            prioridade_base = 45.0

        ultima_resposta = (
            efetivas[0][
                "respondida_em"
            ]
            if efetivas
            else None
        )

        duvida = any(
            item[
                "duvida"
            ]
            for item in tentativas
        )

        if duvida:
            prioridade_base += 8.0

        topico_chave = int(
            linha[1]
        )

        acumulado = totais_topico.setdefault(
            topico_chave,
            {
                "respondidas": 0,
                "acertos": 0,
            }
        )
        acumulado[
            "respondidas"
        ] += total
        acumulado[
            "acertos"
        ] += acertos

        questoes.append({
            "id": questao_id,
            "topico_id": topico_chave,
            "disciplina_id": int(
                linha[2]
            ),
            "disciplina": linha[3],
            "topico": linha[4],
            "enunciado": linha[5],
            "banca": linha[6] or "",
            "ano": linha[7],
            "dificuldade": (
                linha[8]
                or "Não informada"
            ),
            "tentativas_anteriores": total,
            "inedita": (
                total == 0
            ),
            "categoria_inteligente": categoria,
            "categoria_rotulo": categoria_rotulo,
            "tentativas": total,
            "acertos": acertos,
            "erros": erros,
            "taxa_acerto": taxa,
            "erros_consecutivos": (
                erros_consecutivos
            ),
            "acertos_consecutivos": (
                acertos_consecutivos
            ),
            "teve_erro": teve_erro,
            "duvida": duvida,
            "ultima_resposta": ultima_resposta,
            "prioridade_base": (
                prioridade_base
            ),
        })

    total_respondidas = sum(
        item[
            "tentativas"
        ]
        for item in questoes
    )
    total_acertos = sum(
        item[
            "acertos"
        ]
        for item in questoes
    )

    taxa_global = (
        100.0
        * total_acertos
        / total_respondidas
        if total_respondidas > 0
        else None
    )

    if total_respondidas == 0:
        perfil = "primeiro_contato"
        perfil_rotulo = "Primeiro contato"

    elif taxa_global < 70.0:
        perfil = "fraco"
        perfil_rotulo = "Desempenho fraco"

    elif taxa_global < 85.0:
        perfil = "medio"
        perfil_rotulo = "Desempenho intermediário"

    else:
        perfil = "forte"
        perfil_rotulo = "Desempenho forte"

    for questao in questoes:
        topico_resumo = totais_topico[
            questao[
                "topico_id"
            ]
        ]
        respondidas_topico = int(
            topico_resumo[
                "respondidas"
            ]
        )
        acertos_topico = int(
            topico_resumo[
                "acertos"
            ]
        )

        taxa_topico = (
            100.0
            * acertos_topico
            / respondidas_topico
            if respondidas_topico > 0
            else None
        )

        questao[
            "desempenho_topico"
        ] = taxa_topico

        if (
            taxa_topico is not None
            and taxa_topico < 70.0
        ):
            questao[
                "prioridade_base"
            ] += 10.0

        elif (
            taxa_topico is not None
            and taxa_topico >= 85.0
            and questao[
                "categoria_inteligente"
            ] == "dominada"
        ):
            questao[
                "prioridade_base"
            ] -= 5.0

    contagens = {}

    for questao in questoes:
        categoria = questao[
            "categoria_inteligente"
        ]
        contagens[
            categoria
        ] = (
            contagens.get(
                categoria,
                0
            )
            + 1
        )

    return {
        "questoes": questoes,
        "perfil": perfil,
        "perfil_rotulo": (
            perfil_rotulo
        ),
        "respondidas": (
            total_respondidas
        ),
        "acertos": total_acertos,
        "taxa_global": taxa_global,
        "contagens": contagens,
        "total_disponivel": len(
            questoes
        ),
    }


def _pesos_selecao_inteligente(
    perfil
):
    if perfil == "primeiro_contato":
        return {
            "inedita": 0.85,
            "recorrente": 0.05,
            "recuperacao": 0.04,
            "erro": 0.03,
            "controle": 0.02,
            "dominada": 0.01,
        }

    if perfil == "fraco":
        return {
            "recorrente": 0.30,
            "recuperacao": 0.22,
            "erro": 0.13,
            "inedita": 0.25,
            "controle": 0.05,
            "dominada": 0.05,
        }

    if perfil == "medio":
        return {
            "recorrente": 0.20,
            "recuperacao": 0.15,
            "erro": 0.10,
            "inedita": 0.40,
            "controle": 0.08,
            "dominada": 0.07,
        }

    return {
        "recorrente": 0.10,
        "recuperacao": 0.10,
        "erro": 0.07,
        "inedita": 0.50,
        "controle": 0.10,
        "dominada": 0.13,
    }


def _ordenar_bucket_inteligente(
    categoria,
    itens
):
    itens = list(
        itens
    )

    if categoria == "inedita":
        random.shuffle(
            itens
        )
        return itens

    if categoria in (
        "recorrente",
        "recuperacao",
        "erro",
    ):
        random.shuffle(
            itens
        )
        itens.sort(
            key=lambda item: (
                -item[
                    "prioridade_base"
                ],
                (
                    item[
                        "taxa_acerto"
                    ]
                    if item[
                        "taxa_acerto"
                    ] is not None
                    else 101.0
                ),
                -item[
                    "erros"
                ],
            )
        )
        return itens

    # Controle/dominada: primeiro as menos recentes para espaçar
    # a confirmação de retenção.
    random.shuffle(
        itens
    )
    itens.sort(
        key=lambda item: (
            item[
                "ultima_resposta"
            ]
            or "",
            -item[
                "prioridade_base"
            ],
        )
    )
    return itens



def _score_urgencia_sessao_adaptativa(
    proxima_revisao,
    revisoes_totais=0
):
    """
    Converte a situação temporal do tópico em 0–100.

    A urgência não substitui a fila de revisão tradicional; ela é apenas
    uma das dimensões usadas para escolher tópicos em uma sessão global.
    """

    hoje = date.today()

    if proxima_revisao:
        try:
            data_revisao = datetime.strptime(
                str(
                    proxima_revisao
                )[:10],
                "%Y-%m-%d"
            ).date()
        except Exception:
            data_revisao = None
    else:
        data_revisao = None

    if data_revisao is None:
        if int(
            revisoes_totais
            or 0
        ) <= 0:
            return (
                60.0,
                "sem agendamento • primeiro contato"
            )

        return (
            35.0,
            "sem próxima revisão definida"
        )

    diferenca = (
        data_revisao
        - hoje
    ).days

    if diferenca < 0:
        atraso = abs(
            diferenca
        )

        return (
            min(
                100.0,
                90.0
                + atraso * 2.0
            ),
            (
                f"revisão vencida há {atraso} dia(s)"
            )
        )

    if diferenca == 0:
        return (
            88.0,
            "revisão vence hoje"
        )

    if diferenca <= 3:
        return (
            76.0,
            (
                f"revisão em {diferenca} dia(s)"
            )
        )

    if diferenca <= 7:
        return (
            64.0,
            (
                f"revisão em {diferenca} dia(s)"
            )
        )

    if diferenca <= 14:
        return (
            45.0,
            (
                f"revisão em {diferenca} dia(s)"
            )
        )

    if diferenca <= 30:
        return (
            30.0,
            (
                f"revisão em {diferenca} dia(s)"
            )
        )

    return (
        15.0,
        (
            f"revisão em {diferenca} dia(s)"
        )
    )



def _pesos_topicos_adaptativa_v2():
    """Pesos percentuais da Seleção Adaptativa V2 (somam 100)."""
    return {
        "dominio": 20,
        "erros": 18,
        "evidencia": 15,
        "variedade": 12,
        "estabilidade": 10,
        "recencia": 8,
        "urgencia": 10,
        "importancia": 7,
    }


def _normalizar_pesos_adaptativos_v2(pesos):
    pesos = {
        chave: max(0.0, float(valor or 0.0))
        for chave, valor in dict(pesos or {}).items()
    }
    total = sum(pesos.values())
    if total <= 0:
        return pesos
    return {
        chave: valor / total
        for chave, valor in pesos.items()
    }


def _pesos_categorias_adaptativas_v2(indice):
    """
    Define a composição das questões dentro de um tópico já escolhido.

    A V2 muda a mistura conforme a necessidade real do tópico:
    - erro aberto -> mais recorrentes/recuperação;
    - pouca evidência/variedade -> mais inéditas;
    - instabilidade -> mais controle;
    - conteúdo antigo já bem dominado -> retenção/controle.
    """
    indice = dict(indice or {})

    tentativas = int(indice.get("tentativas_historicas", 0) or 0)
    score = float(indice.get("dominio", indice.get("score", 0.0)) or 0.0)
    evidencia = float(indice.get("evidencia", 0.0) or 0.0)
    variedade = float(indice.get("variedade", 0.0) or 0.0)
    estabilidade = float(indice.get("estabilidade", 0.0) or 0.0)
    recencia = float(indice.get("recencia", 0.0) or 0.0)
    controle_erros = float(indice.get("controle_erros", 100.0) or 0.0)
    criticas = int(indice.get("criticas", 0) or 0)
    recorrentes = int(indice.get("recorrentes", 0) or 0)
    recuperacao = int(indice.get("recuperacao", 0) or 0)

    if tentativas <= 0:
        return {
            "inedita": 0.86,
            "controle": 0.08,
            "recorrente": 0.02,
            "recuperacao": 0.02,
            "erro": 0.01,
            "dominada": 0.01,
        }, "Exploração inicial"

    pesos = {
        "recorrente": 0.18,
        "recuperacao": 0.15,
        "erro": 0.09,
        "inedita": 0.38,
        "controle": 0.13,
        "dominada": 0.07,
    }

    fragilidade_erros = max(0.0, min(1.0, (100.0 - controle_erros) / 100.0))
    lacuna_evidencia = max(0.0, min(1.0, (100.0 - evidencia) / 100.0))
    lacuna_variedade = max(0.0, min(1.0, (100.0 - variedade) / 100.0))
    instabilidade = max(0.0, min(1.0, (100.0 - estabilidade) / 100.0))
    desatualizacao = max(0.0, min(1.0, (100.0 - recencia) / 100.0))

    pesos["recorrente"] += 0.22 * fragilidade_erros
    pesos["recuperacao"] += 0.18 * fragilidade_erros
    pesos["erro"] += 0.08 * fragilidade_erros

    if criticas > 0 or recorrentes > 0:
        pesos["recorrente"] += 0.10
    if recuperacao > 0:
        pesos["recuperacao"] += 0.10

    lacuna_exploracao = max(lacuna_evidencia, lacuna_variedade)
    pesos["inedita"] += 0.30 * lacuna_exploracao

    # Instabilidade deve ser validada com questões de controle; a parcela é
    # reduzida quando a base histórica é muito pequena, pois nesse caso a
    # prioridade correta é ampliar evidência, não chamar ausência de dados de
    # "instabilidade".
    fator_temporal = min(1.0, tentativas / 12.0)
    pesos["controle"] += 0.18 * instabilidade * fator_temporal

    if score >= 70.0:
        pesos["controle"] += 0.12 * desatualizacao
        pesos["dominada"] += 0.10 * desatualizacao

    pesos = _normalizar_pesos_adaptativos_v2(pesos)

    necessidades = {
        "Correção de fragilidade": fragilidade_erros + (0.20 if criticas or recorrentes else 0.0),
        "Consolidação da recuperação": (0.75 if recuperacao > 0 else 0.0) + 0.25 * fragilidade_erros,
        "Ampliação de evidência": max(lacuna_evidencia, lacuna_variedade),
        "Validação de estabilidade": instabilidade * fator_temporal,
        "Teste de retenção": desatualizacao if score >= 70.0 else 0.0,
        "Equilíbrio adaptativo": 0.25,
    }
    estrategia = max(necessidades, key=necessidades.get)
    return pesos, estrategia

def obter_prioridades_sessao_adaptativa(
    concurso_id=None,
    disciplina_id=None,
    topicos_ids=None
):
    """
    Ranking estratégico de tópicos da Seleção Adaptativa V2.

    A V2 usa diretamente os sinais do Índice de Domínio V2:
    - fragilidade do domínio: 20%
    - erros abertos/recuperação: 18%
    - insuficiência de evidência: 15%
    - variedade insuficiente: 12%
    - instabilidade recente: 10%
    - necessidade de retenção/recência: 8%
    - urgência da revisão: 10%
    - importância do tópico: 7%

    O objetivo é não confundir "nota baixa" com uma única causa. Um tópico
    pode entrar na sessão por erro recorrente, pouca evidência, baixa
    variedade, instabilidade, desatualização ou urgência temporal.
    """

    if concurso_id is None:
        concurso_id = obter_concurso_ativo()[0]

    concurso_id = int(concurso_id)
    disciplina_id = int(disciplina_id) if disciplina_id is not None else None

    if topicos_ids is None:
        topicos_ids_set = None
    else:
        topicos_ids_set = {int(topico_id) for topico_id in topicos_ids}

    indices = obter_indices_dominio_topicos(concurso_id)

    with conectar() as conexao:
        linhas = conexao.execute(
            """
            SELECT
                t.id,
                d.id,
                d.nome,
                t.nome,
                COALESCE(tc.importancia, 3) AS importancia,
                c.proxima_revisao,
                (
                    COALESCE(c.revisoes_iniciais, 0)
                    + (
                        SELECT COUNT(*)
                        FROM revisoes r
                        WHERE r.topico_id = t.id
                    )
                ) AS revisoes_totais
            FROM topicos t
            JOIN disciplinas d
                ON d.id = t.disciplina_id
            JOIN disciplina_concurso_inclusao dc
                ON dc.disciplina_id = d.id
                AND dc.concurso_id = ?
                AND dc.incluido = 1
                AND COALESCE(dc.pausado, 0) = 0
            JOIN topico_concurso_importancia tc
                ON tc.topico_id = t.id
                AND tc.concurso_id = ?
                AND tc.incluido = 1
                AND COALESCE(tc.pausado, 0) = 0
            LEFT JOIN controle_topico c
                ON c.topico_id = t.id
            ORDER BY
                d.nome COLLATE NOCASE,
                t.nome COLLATE NOCASE
            """,
            (concurso_id, concurso_id)
        ).fetchall()

    pesos_percentuais = _pesos_topicos_adaptativa_v2()
    pesos = {chave: valor / 100.0 for chave, valor in pesos_percentuais.items()}

    rotulos_motivo = {
        "dominio": "domínio frágil",
        "erros": "erros abertos ou recuperação",
        "evidencia": "evidência insuficiente",
        "variedade": "variedade insuficiente",
        "estabilidade": "instabilidade recente",
        "recencia": "retenção / recência",
        "urgencia": "revisão vencida ou próxima",
        "importancia": "importância do tópico",
    }

    resultados = []

    for linha in linhas:
        topico_id = int(linha[0])
        disciplina_atual_id = int(linha[1])

        if disciplina_id is not None and disciplina_atual_id != disciplina_id:
            continue
        if topicos_ids_set is not None and topico_id not in topicos_ids_set:
            continue

        dominio = indices.get(topico_id)
        if dominio is None:
            continue

        quantidade_questoes = int(dominio.get("questoes_ativas", 0) or 0)
        if quantidade_questoes <= 0:
            continue

        score_dominio = float(dominio.get("score", 0.0) or 0.0)
        baixo_dominio = max(0.0, min(100.0, 100.0 - score_dominio))

        controle_erros = float(dominio.get("controle_erros", 100.0) or 0.0)
        criticas = int(dominio.get("criticas", 0) or 0)
        recorrentes = int(dominio.get("recorrentes", 0) or 0)
        recuperacao = int(dominio.get("recuperacao", 0) or 0)
        recuperadas = int(dominio.get("recuperadas", 0) or 0)

        score_erros = max(
            max(0.0, min(100.0, 100.0 - controle_erros)),
            min(100.0, criticas * 45.0 + recorrentes * 28.0 + recuperacao * 12.0)
        )

        evidencia = float(dominio.get("evidencia", 0.0) or 0.0)
        score_evidencia = max(0.0, min(100.0, 100.0 - evidencia))

        variedade = float(dominio.get("variedade", 0.0) or 0.0)
        score_variedade = max(0.0, min(100.0, 100.0 - variedade))

        tentativas_historicas = int(dominio.get("tentativas_historicas", 0) or 0)
        estabilidade = float(dominio.get("estabilidade", 0.0) or 0.0)
        fator_temporal = min(1.0, tentativas_historicas / 12.0)
        score_estabilidade = max(
            0.0,
            min(100.0, (100.0 - estabilidade) * fator_temporal)
        )

        recencia = float(dominio.get("recencia", 0.0) or 0.0)
        if tentativas_historicas <= 0:
            score_recencia = 45.0
        else:
            score_recencia = max(0.0, min(100.0, 100.0 - recencia))

        urgencia, motivo_urgencia = _score_urgencia_sessao_adaptativa(
            linha[5], linha[6]
        )

        importancia = max(1, min(5, int(linha[4] or 3)))
        score_importancia = (importancia - 1) / 4.0 * 100.0

        componentes = {
            "dominio": baixo_dominio,
            "erros": score_erros,
            "evidencia": score_evidencia,
            "variedade": score_variedade,
            "estabilidade": score_estabilidade,
            "recencia": score_recencia,
            "urgencia": urgencia,
            "importancia": score_importancia,
        }

        contribuicoes = {
            chave: componentes[chave] * pesos[chave]
            for chave in pesos
        }
        score = sum(contribuicoes.values())

        motivo_principal_chave = max(
            contribuicoes,
            key=lambda chave: (contribuicoes[chave], pesos[chave])
        )

        motivos_detalhados = []
        qualidade_evidencia = str(dominio.get("qualidade_evidencia", "Sem evidência"))

        if score_dominio < 70.0:
            motivos_detalhados.append(f"domínio {score_dominio:.0f}/100")
        if criticas > 0 or recorrentes > 0 or recuperacao > 0:
            motivos_detalhados.append(
                f"erros: {criticas} crítica(s), {recorrentes} recorrente(s), "
                f"{recuperacao} em recuperação"
            )
        if evidencia < 55.0:
            motivos_detalhados.append(
                f"evidência {evidencia:.0f}/100 ({qualidade_evidencia.lower()})"
            )
        if variedade < 55.0:
            motivos_detalhados.append(f"variedade {variedade:.0f}/100")
        if tentativas_historicas >= 5 and estabilidade < 55.0:
            motivos_detalhados.append(f"estabilidade {estabilidade:.0f}/100")
        if tentativas_historicas > 0 and recencia < 60.0:
            dias = dominio.get("dias_desde_ultima")
            if dias is not None:
                motivos_detalhados.append(f"última prática há {int(dias)} dia(s)")
        if urgencia >= 76.0:
            motivos_detalhados.append(motivo_urgencia)
        if importancia >= 4:
            motivos_detalhados.append(f"importância {importancia}/5")
        if recuperadas > 0:
            motivos_detalhados.append(f"{recuperadas} erro(s) já recuperado(s)")

        if not motivos_detalhados:
            motivos_detalhados.append(rotulos_motivo[motivo_principal_chave])

        resultados.append({
            "versao_selecao": "adaptativa_v2",
            "topico_id": topico_id,
            "disciplina_id": disciplina_atual_id,
            "disciplina": linha[2],
            "topico": linha[3],
            "importancia": importancia,
            "proxima_revisao": linha[5],
            "revisoes_totais": int(linha[6] or 0),
            "questoes_disponiveis": quantidade_questoes,
            "dominio": score_dominio,
            "nivel_dominio": dominio.get("nivel", "Sem evidência"),
            "qualidade_evidencia": qualidade_evidencia,
            "evidencia": round(evidencia, 1),
            "variedade": round(variedade, 1),
            "estabilidade": round(estabilidade, 1),
            "recencia": round(recencia, 1),
            "controle_erros": round(controle_erros, 1),
            "cobertura": round(float(dominio.get("cobertura", 0.0) or 0.0), 1),
            "tentativas_historicas": tentativas_historicas,
            "questoes_unicas": int(dominio.get("questoes_unicas", 0) or 0),
            "dias_ativos_historicos": int(dominio.get("dias_ativos_historicos", 0) or 0),
            "dias_desde_ultima": dominio.get("dias_desde_ultima"),
            "taxa_duvida": float(dominio.get("taxa_duvida", 0.0) or 0.0),
            "criticas": criticas,
            "recorrentes": recorrentes,
            "recuperacao": recuperacao,
            "recuperadas": recuperadas,
            "baixo_dominio": round(baixo_dominio, 1),
            "urgencia": round(urgencia, 1),
            "score_importancia": round(score_importancia, 1),
            "score_erros": round(score_erros, 1),
            "score_evidencia": round(score_evidencia, 1),
            "score_variedade": round(score_variedade, 1),
            "score_estabilidade": round(score_estabilidade, 1),
            "score_recencia": round(score_recencia, 1),
            "score_adaptativo": round(score, 1),
            "motivo_principal_chave": motivo_principal_chave,
            "motivo_principal": rotulos_motivo[motivo_principal_chave],
            "motivo_urgencia": motivo_urgencia,
            "motivo_detalhado": " • ".join(motivos_detalhados),
            "componentes": componentes,
            "contribuicoes": contribuicoes,
            "pesos_adaptativos": pesos_percentuais,
        })

    resultados.sort(
        key=lambda item: (
            -item["score_adaptativo"],
            -item["importancia"],
            item["disciplina"].lower(),
            item["topico"].lower(),
        )
    )
    return resultados

def planejar_sessao_adaptativa_global(
    concurso_id=None,
    quantidade=30,
    disciplina_id=None,
    topicos_ids=None
):
    """
    Distribui o objetivo da sessão entre os tópicos mais estratégicos.

    A V2 mantém uma base mínima por tópico quando a quantidade permite,
    porque isso produz evidência útil sem fragmentar demais a sessão. A ordem
    dos tópicos já vem do ranking estratégico baseado no Domínio V2.
    """

    if concurso_id is None:
        concurso_id = (
            obter_concurso_ativo()[0]
        )

    concurso_id = int(
        concurso_id
    )

    prioridades = obter_prioridades_sessao_adaptativa(
        concurso_id,
        disciplina_id=disciplina_id,
        topicos_ids=topicos_ids
    )

    total_disponivel = sum(
        int(
            item[
                "questoes_disponiveis"
            ]
        )
        for item in prioridades
    )

    quantidade_solicitada = max(
        1,
        int(
            quantidade
            or 1
        )
    )

    quantidade_alvo = min(
        quantidade_solicitada,
        total_disponivel
    )

    if (
        quantidade_alvo <= 0
        or not prioridades
    ):
        return {
            "concurso_id": concurso_id,
            "quantidade_solicitada": (
                quantidade_solicitada
            ),
            "quantidade": 0,
            "total_disponivel": (
                total_disponivel
            ),
            "prioridades": prioridades,
            "alocacoes": [],
            "resumo_motivos": {},
            "topicos_utilizados": 0,
            "tempo_estimado_minutos": 0,
            "versao_selecao": "adaptativa_v2",
            "pesos": _pesos_topicos_adaptativa_v2(),
        }

    # Aproximadamente um tópico para cada 7 questões, com teto de 6.
    # Isso evita sessões excessivamente fragmentadas e ajuda a atingir o
    # mínimo de evidência usado pela integração automática de revisões.
    max_topicos = max(
        1,
        min(
            6,
            int(
                math.ceil(
                    quantidade_alvo
                    / 7.0
                )
            ),
            len(
                prioridades
            ),
        )
    )

    candidatos = list(
        prioridades[
            :max_topicos
        ]
    )

    capacidade_candidatos = sum(
        int(
            item[
                "questoes_disponiveis"
            ]
        )
        for item in candidatos
    )

    proximo_indice = len(
        candidatos
    )

    while (
        capacidade_candidatos < quantidade_alvo
        and proximo_indice < len(
            prioridades
        )
    ):
        proximo = prioridades[
            proximo_indice
        ]
        candidatos.append(
            proximo
        )
        capacidade_candidatos += int(
            proximo[
                "questoes_disponiveis"
            ]
        )
        proximo_indice += 1

    alocacoes = {
        item[
            "topico_id"
        ]: 0
        for item in candidatos
    }

    disponivel = {
        item[
            "topico_id"
        ]: int(
            item[
                "questoes_disponiveis"
            ]
        )
        for item in candidatos
    }

    restante = quantidade_alvo

    # Base conservadora: quando houver espaço, tenta colocar até 5 questões
    # em cada tópico escolhido.
    base_por_topico = (
        5
        if quantidade_alvo >= 5
        else 1
    )

    for item in candidatos:
        if restante <= 0:
            break

        topico_id = item[
            "topico_id"
        ]

        minimo = min(
            base_por_topico,
            disponivel[
                topico_id
            ],
            restante
        )

        alocacoes[
            topico_id
        ] += minimo

        disponivel[
            topico_id
        ] -= minimo

        restante -= minimo

    # Limite de concentração inicial. Se não houver capacidade suficiente
    # nos outros tópicos, uma segunda passagem relaxa esse limite.
    if len(
        candidatos
    ) >= 3:
        limite_concentracao = max(
            base_por_topico,
            int(
                math.ceil(
                    quantidade_alvo
                    * 0.40
                )
            )
        )
    elif len(
        candidatos
    ) == 2:
        limite_concentracao = max(
            base_por_topico,
            int(
                math.ceil(
                    quantidade_alvo
                    * 0.65
                )
            )
        )
    else:
        limite_concentracao = (
            quantidade_alvo
        )

    pesos_topicos = {
        item[
            "topico_id"
        ]: max(
            5.0,
            float(
                item[
                    "score_adaptativo"
                ]
            )
        )
        for item in candidatos
    }

    soma_pesos = sum(
        pesos_topicos.values()
    ) or 1.0

    def escolher_topico(
        respeitar_limite
    ):
        elegiveis = []

        for item in candidatos:
            topico_id = item[
                "topico_id"
            ]

            if disponivel[
                topico_id
            ] <= 0:
                continue

            if (
                respeitar_limite
                and alocacoes[
                    topico_id
                ] >= limite_concentracao
            ):
                continue

            alvo_teorico = (
                quantidade_alvo
                * pesos_topicos[
                    topico_id
                ]
                / soma_pesos
            )

            deficit = (
                alvo_teorico
                - alocacoes[
                    topico_id
                ]
            )

            elegiveis.append(
                (
                    deficit,
                    item[
                        "score_adaptativo"
                    ],
                    item[
                        "importancia"
                    ],
                    -alocacoes[
                        topico_id
                    ],
                    item
                )
            )

        if not elegiveis:
            return None

        elegiveis.sort(
            key=lambda item: (
                -item[0],
                -item[1],
                -item[2],
                -item[3],
                item[4][
                    "disciplina"
                ].lower(),
                item[4][
                    "topico"
                ].lower(),
            )
        )

        return elegiveis[0][4]

    while restante > 0:
        escolhido = escolher_topico(
            True
        )

        if escolhido is None:
            escolhido = escolher_topico(
                False
            )

        if escolhido is None:
            break

        topico_id = escolhido[
            "topico_id"
        ]

        alocacoes[
            topico_id
        ] += 1
        disponivel[
            topico_id
        ] -= 1
        restante -= 1

    alocacoes_lista = []

    resumo_motivos = {}

    for item in candidatos:
        quantidade_topico = (
            alocacoes[
                item[
                    "topico_id"
                ]
            ]
        )

        if quantidade_topico <= 0:
            continue

        registro = {
            **item,
            "quantidade": (
                quantidade_topico
            ),
        }

        alocacoes_lista.append(
            registro
        )

        motivo = item[
            "motivo_principal"
        ]

        resumo_motivos[
            motivo
        ] = (
            resumo_motivos.get(
                motivo,
                0
            )
            + quantidade_topico
        )

    alocacoes_lista.sort(
        key=lambda item: (
            -item[
                "score_adaptativo"
            ],
            -item[
                "quantidade"
            ],
            item[
                "disciplina"
            ].lower(),
            item[
                "topico"
            ].lower(),
        )
    )

    quantidade_final = sum(
        item[
            "quantidade"
        ]
        for item in alocacoes_lista
    )

    return {
        "concurso_id": concurso_id,
        "quantidade_solicitada": (
            quantidade_solicitada
        ),
        "quantidade": quantidade_final,
        "total_disponivel": (
            total_disponivel
        ),
        "prioridades": prioridades,
        "alocacoes": (
            alocacoes_lista
        ),
        "resumo_motivos": (
            resumo_motivos
        ),
        "topicos_utilizados": len(
            alocacoes_lista
        ),
        # Estimativa simples V1: aproximadamente 75 s por questão.
        "tempo_estimado_minutos": int(
            math.ceil(
                quantidade_final
                * 1.25
            )
        ),
        "versao_selecao": "adaptativa_v2",
        "pesos": _pesos_topicos_adaptativa_v2(),
    }



def selecionar_questoes_adaptativas_v2(
    concurso_id,
    topico_id,
    quantidade,
    indice_topico=None
):
    """Seleciona as questões de um tópico com composição dinâmica V2."""
    perfil = obter_perfil_selecao_inteligente_questoes(
        concurso_id,
        topico_id=topico_id
    )

    quantidade = max(1, int(quantidade or 1))
    quantidade = min(quantidade, int(perfil.get("total_disponivel", 0) or 0))

    if indice_topico is None:
        indice_topico = obter_indice_dominio_topico(topico_id, concurso_id)

    pesos, estrategia = _pesos_categorias_adaptativas_v2(indice_topico)

    if quantidade <= 0:
        return {
            **perfil,
            "fila": [],
            "composicao": {},
            "modo": "Treino adaptativo",
            "versao_selecao": "adaptativa_v2",
            "estrategia_v2": estrategia,
            "pesos_categorias": pesos,
        }

    buckets = {}
    for item in perfil["questoes"]:
        buckets.setdefault(item["categoria_inteligente"], []).append(item)

    for categoria in list(buckets):
        buckets[categoria] = _ordenar_bucket_inteligente(categoria, buckets[categoria])

    selecionadas = []
    usados = set()
    contagem = {}
    categorias_ordenadas = [
        "recorrente", "recuperacao", "erro", "inedita", "controle", "dominada"
    ]

    motivos_categoria = {
        "inedita": "Questão inédita para ampliar variedade e evidência.",
        "recorrente": "Erro recorrente priorizado para corrigir fragilidade aberta.",
        "recuperacao": "Questão em recuperação para confirmar retenção após erro.",
        "erro": "Erro anterior selecionado para verificar correção do conceito.",
        "controle": "Questão de controle para medir estabilidade e retenção.",
        "dominada": "Amostra de retenção em conteúdo previamente dominado.",
    }

    while len(selecionadas) < quantidade:
        disponiveis = [categoria for categoria in categorias_ordenadas if buckets.get(categoria)]
        if not disponiveis:
            break

        melhor_categoria = max(
            disponiveis,
            key=lambda categoria: (
                pesos.get(categoria, 0.0) * quantidade - contagem.get(categoria, 0),
                pesos.get(categoria, 0.0),
                -categorias_ordenadas.index(categoria),
            )
        )

        item = buckets[melhor_categoria].pop(0)
        if item["id"] in usados:
            continue
        usados.add(item["id"])

        selecionadas.append({
            **item,
            "versao_selecao_adaptativa": "adaptativa_v2",
            "estrategia_questoes_v2": estrategia,
            "peso_categoria_adaptativo": round(100.0 * pesos.get(melhor_categoria, 0.0), 1),
            "motivo_inteligente": motivos_categoria[melhor_categoria],
            "score_inteligente": round(float(item["prioridade_base"]), 1),
        })
        contagem[melhor_categoria] = contagem.get(melhor_categoria, 0) + 1

    composicao = {}
    for item in selecionadas:
        rotulo = item["categoria_rotulo"]
        composicao[rotulo] = composicao.get(rotulo, 0) + 1

    return {
        **perfil,
        "fila": selecionadas,
        "composicao": composicao,
        "modo": "Treino adaptativo",
        "versao_selecao": "adaptativa_v2",
        "estrategia_v2": estrategia,
        "pesos_categorias": pesos,
    }

def selecionar_sessao_adaptativa_global(
    concurso_id=None,
    quantidade=30,
    disciplina_id=None,
    topicos_ids=None
):
    """
    Constrói a fila final da Seleção Adaptativa V2.

    Nível 1: prioriza tópicos pelos oito sinais estratégicos da V2.
    Nível 2: dentro de cada tópico, muda dinamicamente a mistura entre
    inéditas, erros recorrentes, recuperação, controle e retenção.
    """
    plano = planejar_sessao_adaptativa_global(
        concurso_id,
        quantidade=quantidade,
        disciplina_id=disciplina_id,
        topicos_ids=topicos_ids
    )

    if concurso_id is None:
        concurso_id = plano["concurso_id"]

    filas_por_topico = {}
    composicao_inteligente = {}
    estrategias_questoes = {}

    for alocacao in plano["alocacoes"]:
        selecao = selecionar_questoes_adaptativas_v2(
            concurso_id,
            topico_id=alocacao["topico_id"],
            quantidade=alocacao["quantidade"],
            indice_topico=alocacao
        )

        fila_topico = []
        estrategias_questoes[
            f"{alocacao['disciplina']} › {alocacao['topico']}"
        ] = selecao.get("estrategia_v2", "Equilíbrio adaptativo")

        for item in selecao["fila"]:
            item_enriquecido = {
                **item,
                "sessao_adaptativa": True,
                "versao_selecao_adaptativa": "adaptativa_v2",
                "prioridade_topico": alocacao["score_adaptativo"],
                "dominio_topico": alocacao["dominio"],
                "nivel_dominio_topico": alocacao["nivel_dominio"],
                "qualidade_evidencia_topico": alocacao.get("qualidade_evidencia", "—"),
                "estrategia_topico_v2": selecao.get("estrategia_v2", "Equilíbrio adaptativo"),
                "motivo_adaptativo": (
                    "Prioridade V2 do tópico: " + alocacao["motivo_detalhado"]
                    + " | Estratégia das questões: "
                    + selecao.get("estrategia_v2", "Equilíbrio adaptativo")
                ),
                "motivo_adaptativo_principal": alocacao["motivo_principal"],
            }
            fila_topico.append(item_enriquecido)

            rotulo_categoria = item.get("categoria_rotulo", "Outras")
            composicao_inteligente[rotulo_categoria] = (
                composicao_inteligente.get(rotulo_categoria, 0) + 1
            )

        filas_por_topico[alocacao["topico_id"]] = fila_topico

    # Intercala tópicos para evitar blocos longos da mesma matéria.
    fila_final = []
    ordem_topicos = [item["topico_id"] for item in plano["alocacoes"]]

    while True:
        adicionou = False
        for topico_id in ordem_topicos:
            fila_topico = filas_por_topico.get(topico_id, [])
            if not fila_topico:
                continue
            fila_final.append(fila_topico.pop(0))
            adicionou = True
        if not adicionou:
            break

    composicao_topicos = {
        f"{item['disciplina']} › {item['topico']}": item["quantidade"]
        for item in plano["alocacoes"]
    }

    return {
        "fila": fila_final,
        "plano": plano,
        "composicao_topicos": composicao_topicos,
        "composicao_inteligente": composicao_inteligente,
        "estrategias_questoes": estrategias_questoes,
        "resumo_motivos": plano["resumo_motivos"],
        "modo": "Treino adaptativo",
        "versao_selecao": "adaptativa_v2",
        "perfil_rotulo": "Seleção Adaptativa V2",
    }

def obter_disponibilidade_simulado_disciplinas(
    concurso_id=None
):
    if concurso_id is None:
        concurso_id = (
            obter_concurso_ativo()[0]
        )

    concurso_id = int(
        concurso_id
    )

    with conectar() as conexao:
        linhas = conexao.execute(
            """
            SELECT
                d.id,
                d.nome,
                COUNT(
                    DISTINCT CASE
                        WHEN q.ativa = 1
                        THEN t.id
                    END
                ) AS topicos_com_questao,
                COUNT(
                    CASE
                        WHEN q.ativa = 1
                        THEN q.id
                    END
                ) AS questoes_ativas,
                COUNT(
                    CASE
                        WHEN
                            q.ativa = 1
                            AND NOT EXISTS (
                                SELECT 1
                                FROM tentativas_questoes tq
                                WHERE
                                    tq.concurso_id = ?
                                    AND tq.correta IS NOT NULL
                                    AND COALESCE(
                                        tq.questao_id_snapshot,
                                        tq.questao_id
                                    ) = q.id
                            )
                        THEN q.id
                    END
                ) AS ineditas,
                AVG(
                    CASE
                        WHEN q.ativa = 1
                        THEN COALESCE(
                            tc.importancia,
                            3
                        )
                    END
                ) AS importancia_media
            FROM disciplinas d
            JOIN disciplina_concurso_inclusao dc
                ON dc.disciplina_id = d.id
                AND dc.concurso_id = ?
                AND dc.incluido = 1
                AND COALESCE(dc.pausado, 0) = 0
            JOIN topicos t
                ON t.disciplina_id = d.id
            JOIN topico_concurso_importancia tc
                ON tc.topico_id = t.id
                AND tc.concurso_id = ?
                AND tc.incluido = 1
                AND COALESCE(tc.pausado, 0) = 0
            LEFT JOIN questoes q
                ON q.topico_id = t.id
            GROUP BY
                d.id,
                d.nome
            HAVING questoes_ativas > 0
            ORDER BY
                d.nome COLLATE NOCASE
            """,
            (
                concurso_id,
                concurso_id,
                concurso_id,
            )
        ).fetchall()

    resultado = []

    for linha in linhas:
        topicos = int(
            linha[2]
            or 0
        )
        disponiveis = int(
            linha[3]
            or 0
        )
        ineditas = int(
            linha[4]
            or 0
        )
        importancia = float(
            linha[5]
            or 3.0
        )

        # Peso estrutural:
        # número de tópicos com questões, moderadamente ajustado pela
        # importância do perfil. Não usa domínio, acertos ou erros.
        fator_importancia = (
            0.60
            + 0.40
            * (
                importancia
                / 3.0
            )
        )

        peso = max(
            0.1,
            topicos
            * fator_importancia
        )

        resultado.append({
            "disciplina_id": int(
                linha[0]
            ),
            "disciplina": linha[1],
            "topicos": topicos,
            "disponiveis": disponiveis,
            "ineditas": ineditas,
            "importancia_media": round(
                importancia,
                2
            ),
            "peso_estrutural": round(
                peso,
                4
            ),
        })

    return resultado


def planejar_simulado_vighna(
    concurso_id=None,
    quantidade=50
):
    """
    Simulado Vighna:
    distribui questões pela estrutura do perfil, não pelas fraquezas.

    Critérios:
    - quantidade de tópicos da disciplina com questões;
    - importância média dos tópicos;
    - capacidade real do banco.
    """

    if concurso_id is None:
        concurso_id = (
            obter_concurso_ativo()[0]
        )

    concurso_id = int(
        concurso_id
    )

    disciplinas = (
        obter_disponibilidade_simulado_disciplinas(
            concurso_id
        )
    )

    total_disponivel = sum(
        item[
            "disponiveis"
        ]
        for item in disciplinas
    )

    solicitado = max(
        1,
        int(
            quantidade
            or 1
        )
    )

    alvo = min(
        solicitado,
        total_disponivel
    )

    if (
        alvo <= 0
        or not disciplinas
    ):
        return {
            "tipo": "Vighna",
            "quantidade_solicitada": solicitado,
            "quantidade": 0,
            "total_disponivel": total_disponivel,
            "alocacoes": [],
            "criterio": (
                "Estrutura do perfil + importância média."
            ),
        }

    # Se houver questões suficientes, garante uma presença mínima das
    # disciplinas antes de distribuir o restante proporcionalmente.
    alocacoes = {
        item[
            "disciplina_id"
        ]: 0
        for item in disciplinas
    }

    restante = alvo

    ordenadas = sorted(
        disciplinas,
        key=lambda item: (
            -item[
                "peso_estrutural"
            ],
            item[
                "disciplina"
            ].lower(),
        )
    )

    if alvo >= len(
        ordenadas
    ):
        for item in ordenadas:
            if restante <= 0:
                break

            if item[
                "disponiveis"
            ] <= 0:
                continue

            alocacoes[
                item[
                    "disciplina_id"
                ]
            ] += 1
            restante -= 1

    pesos = {
        item[
            "disciplina_id"
        ]: float(
            item[
                "peso_estrutural"
            ]
        )
        for item in ordenadas
    }

    soma_pesos = sum(
        pesos.values()
    ) or 1.0

    while restante > 0:
        elegiveis = []

        for item in ordenadas:
            disciplina_id = item[
                "disciplina_id"
            ]

            atual = alocacoes[
                disciplina_id
            ]

            if atual >= item[
                "disponiveis"
            ]:
                continue

            alvo_teorico = (
                alvo
                * pesos[
                    disciplina_id
                ]
                / soma_pesos
            )

            deficit = (
                alvo_teorico
                - atual
            )

            elegiveis.append(
                (
                    deficit,
                    item[
                        "peso_estrutural"
                    ],
                    -atual,
                    item
                )
            )

        if not elegiveis:
            break

        elegiveis.sort(
            key=lambda valor: (
                -valor[0],
                -valor[1],
                -valor[2],
                valor[3][
                    "disciplina"
                ].lower(),
            )
        )

        escolhida = elegiveis[0][3]

        alocacoes[
            escolhida[
                "disciplina_id"
            ]
        ] += 1

        restante -= 1

    alocacoes_lista = []

    for item in disciplinas:
        quantidade_item = alocacoes[
            item[
                "disciplina_id"
            ]
        ]

        if quantidade_item <= 0:
            continue

        alocacoes_lista.append({
            **item,
            "quantidade": (
                quantidade_item
            ),
        })

    alocacoes_lista.sort(
        key=lambda item: (
            -item[
                "quantidade"
            ],
            -item[
                "peso_estrutural"
            ],
            item[
                "disciplina"
            ].lower(),
        )
    )

    return {
        "tipo": "Vighna",
        "quantidade_solicitada": solicitado,
        "quantidade": sum(
            item[
                "quantidade"
            ]
            for item in alocacoes_lista
        ),
        "total_disponivel": total_disponivel,
        "alocacoes": alocacoes_lista,
        "criterio": (
            "Distribuição pela estrutura do perfil e importância média, "
            "sem usar domínio, acertos ou erros."
        ),
    }


def planejar_simulado_personalizado(
    concurso_id,
    quantidades_por_disciplina
):
    concurso_id = int(
        concurso_id
    )

    disponibilidade = {
        item[
            "disciplina_id"
        ]: item
        for item in (
            obter_disponibilidade_simulado_disciplinas(
                concurso_id
            )
        )
    }

    alocacoes = []
    solicitada = 0
    quantidade_final = 0
    ajustes = []

    for disciplina_id, quantidade in (
        quantidades_por_disciplina.items()
    ):
        disciplina_id = int(
            disciplina_id
        )
        quantidade = max(
            0,
            int(
                quantidade
                or 0
            )
        )

        if quantidade <= 0:
            continue

        solicitada += quantidade

        item = disponibilidade.get(
            disciplina_id
        )

        if item is None:
            ajustes.append(
                (
                    f"Disciplina #{disciplina_id}: "
                    "sem questões disponíveis."
                )
            )
            continue

        real = min(
            quantidade,
            item[
                "disponiveis"
            ]
        )

        if real < quantidade:
            ajustes.append(
                (
                    f"{item['disciplina']}: solicitado {quantidade}, "
                    f"disponível {real}."
                )
            )

        if real <= 0:
            continue

        alocacoes.append({
            **item,
            "quantidade": real,
        })

        quantidade_final += real

    alocacoes.sort(
        key=lambda item: (
            item[
                "disciplina"
            ].lower(),
        )
    )

    return {
        "tipo": "Personalizado",
        "quantidade_solicitada": solicitada,
        "quantidade": quantidade_final,
        "alocacoes": alocacoes,
        "ajustes": ajustes,
        "criterio": (
            "Quantidades definidas manualmente pelo usuário."
        ),
    }


def _selecionar_questoes_simulado_disciplina(
    concurso_id,
    disciplina_id,
    quantidade,
    preferir_ineditas=True
):
    """
    Seleção para prova, sem usar desempenho.

    Dentro da matéria, distribui as questões entre os tópicos disponíveis
    em rodadas sucessivas, evitando que um tópico com banco muito maior
    domine sozinho o simulado.

    Se preferir_ineditas=True, percorre primeiro as inéditas de todos os
    tópicos e só depois completa com questões já respondidas.
    """

    concurso_id = int(
        concurso_id
    )
    disciplina_id = int(
        disciplina_id
    )
    quantidade = max(
        0,
        int(
            quantidade
            or 0
        )
    )

    if quantidade <= 0:
        return []

    todas = listar_questoes_resolucao(
        concurso_id,
        disciplina_id=disciplina_id,
        somente_ineditas=False,
        aleatorio=True
    )

    if not todas:
        return []

    por_topico = {}

    for item in todas:
        topico_id = int(
            item[
                "topico_id"
            ]
        )

        grupo = por_topico.setdefault(
            topico_id,
            {
                "ineditas": [],
                "demais": [],
            }
        )

        if item.get(
            "inedita"
        ):
            grupo[
                "ineditas"
            ].append(
                item
            )
        else:
            grupo[
                "demais"
            ].append(
                item
            )

    topicos_ordem = list(
        por_topico.keys()
    )
    random.shuffle(
        topicos_ordem
    )

    for grupo in por_topico.values():
        random.shuffle(
            grupo[
                "ineditas"
            ]
        )
        random.shuffle(
            grupo[
                "demais"
            ]
        )

    selecionadas = []
    usados = set()

    def consumir_rodadas(
        nome_fila
    ):
        while len(
            selecionadas
        ) < quantidade:
            adicionou = False

            ordem_rodada = list(
                topicos_ordem
            )
            random.shuffle(
                ordem_rodada
            )

            for topico_id in ordem_rodada:
                fila = por_topico[
                    topico_id
                ][
                    nome_fila
                ]

                while (
                    fila
                    and fila[0][
                        "id"
                    ] in usados
                ):
                    fila.pop(
                        0
                    )

                if not fila:
                    continue

                item = fila.pop(
                    0
                )

                if item[
                    "id"
                ] in usados:
                    continue

                usados.add(
                    item[
                        "id"
                    ]
                )
                selecionadas.append(
                    item
                )
                adicionou = True

                if len(
                    selecionadas
                ) >= quantidade:
                    break

            if not adicionou:
                break

    if preferir_ineditas:
        consumir_rodadas(
            "ineditas"
        )
        consumir_rodadas(
            "demais"
        )
    else:
        # Junta ambas as origens mantendo a aleatoriedade, mas conserva
        # o balanceamento tópico a tópico.
        for grupo in por_topico.values():
            combinado = (
                grupo[
                    "ineditas"
                ]
                + grupo[
                    "demais"
                ]
            )
            random.shuffle(
                combinado
            )
            grupo[
                "todos"
            ] = combinado

        consumir_rodadas(
            "todos"
        )

    return selecionadas


def selecionar_questoes_simulado(
    concurso_id,
    plano,
    preferir_ineditas=True
):
    concurso_id = int(
        concurso_id
    )

    plano = dict(
        plano
        or {}
    )

    filas = {}
    ordem = []

    for alocacao in plano.get(
        "alocacoes",
        []
    ):
        disciplina_id = int(
            alocacao[
                "disciplina_id"
            ]
        )

        fila = (
            _selecionar_questoes_simulado_disciplina(
                concurso_id,
                disciplina_id,
                alocacao[
                    "quantidade"
                ],
                preferir_ineditas=(
                    preferir_ineditas
                )
            )
        )

        for item in fila:
            item[
                "sessao_simulado"
            ] = True
            item[
                "motivo_simulado"
            ] = (
                "Selecionada para composição de simulado; "
                "a seleção não prioriza fraquezas individuais."
            )

        filas[
            disciplina_id
        ] = fila

        ordem.append(
            disciplina_id
        )

    # Intercala matérias para evitar blocos longos da mesma disciplina.
    fila_final = []

    while True:
        adicionou = False

        for disciplina_id in ordem:
            fila = filas.get(
                disciplina_id,
                []
            )

            if not fila:
                continue

            fila_final.append(
                fila.pop(
                    0
                )
            )
            adicionou = True

        if not adicionou:
            break

    return {
        "fila": fila_final,
        "plano": plano,
        "preferir_ineditas": bool(
            preferir_ineditas
        ),
    }


def montar_simulado_vighna(
    concurso_id,
    quantidade,
    preferir_ineditas=True
):
    plano = planejar_simulado_vighna(
        concurso_id,
        quantidade
    )

    selecao = selecionar_questoes_simulado(
        concurso_id,
        plano,
        preferir_ineditas=(
            preferir_ineditas
        )
    )

    return {
        **selecao,
        "tipo": "Vighna",
    }


def montar_simulado_personalizado(
    concurso_id,
    quantidades_por_disciplina,
    preferir_ineditas=True
):
    plano = planejar_simulado_personalizado(
        concurso_id,
        quantidades_por_disciplina
    )

    selecao = selecionar_questoes_simulado(
        concurso_id,
        plano,
        preferir_ineditas=(
            preferir_ineditas
        )
    )

    return {
        **selecao,
        "tipo": "Personalizado",
    }



def _alocar_quantidades_simulado_por_peso(
    disciplinas,
    quantidade,
    campo_peso="peso_estrutural"
):
    """Aloca uma quantidade de questões preservando capacidade real."""
    disciplinas = [dict(item) for item in (disciplinas or [])]
    total_disponivel = sum(int(item.get("disponiveis", 0) or 0) for item in disciplinas)
    solicitado = max(1, int(quantidade or 1))
    alvo = min(solicitado, total_disponivel)

    if alvo <= 0 or not disciplinas:
        return [], solicitado, alvo, total_disponivel

    alocacoes = {int(item["disciplina_id"]): 0 for item in disciplinas}
    ordenadas = sorted(
        disciplinas,
        key=lambda item: (
            -float(item.get(campo_peso, 0.0) or 0.0),
            item.get("disciplina", "").lower(),
        )
    )
    restante = alvo

    # Presença mínima quando a prova comporta todas as matérias.
    if alvo >= len(ordenadas):
        for item in ordenadas:
            if restante <= 0:
                break
            if int(item.get("disponiveis", 0) or 0) <= 0:
                continue
            alocacoes[int(item["disciplina_id"])] += 1
            restante -= 1

    pesos = {
        int(item["disciplina_id"]): max(0.001, float(item.get(campo_peso, 0.0) or 0.0))
        for item in ordenadas
    }
    soma_pesos = sum(pesos.values()) or 1.0

    while restante > 0:
        elegiveis = []
        for item in ordenadas:
            disciplina_id = int(item["disciplina_id"])
            atual = alocacoes[disciplina_id]
            disponiveis = int(item.get("disponiveis", 0) or 0)
            if atual >= disponiveis:
                continue
            alvo_teorico = alvo * pesos[disciplina_id] / soma_pesos
            deficit = alvo_teorico - atual
            elegiveis.append((
                deficit,
                pesos[disciplina_id],
                -atual,
                item,
            ))

        if not elegiveis:
            break

        elegiveis.sort(
            key=lambda valor: (
                -valor[0],
                -valor[1],
                -valor[2],
                valor[3].get("disciplina", "").lower(),
            )
        )
        escolhida = elegiveis[0][3]
        alocacoes[int(escolhida["disciplina_id"])] += 1
        restante -= 1

    resultado = []
    for item in disciplinas:
        qtd = alocacoes[int(item["disciplina_id"])]
        if qtd <= 0:
            continue
        novo = dict(item)
        novo["quantidade"] = qtd
        resultado.append(novo)

    resultado.sort(
        key=lambda item: (
            -int(item.get("quantidade", 0) or 0),
            -float(item.get(campo_peso, 0.0) or 0.0),
            item.get("disciplina", "").lower(),
        )
    )
    return resultado, solicitado, sum(item["quantidade"] for item in resultado), total_disponivel


def obter_disponibilidade_simulado_estrategico_disciplinas(concurso_id=None):
    """
    Acrescenta uma pressão estratégica moderada à estrutura do perfil.

    A distribuição nunca vira um treino adaptativo: a fragilidade só corrige
    moderadamente o peso estrutural da disciplina (faixa de 0,82x a 1,18x).
    """
    if concurso_id is None:
        concurso_id = obter_concurso_ativo()[0]
    concurso_id = int(concurso_id)

    disciplinas = obter_disponibilidade_simulado_disciplinas(concurso_id)
    prioridades = obter_prioridades_sessao_adaptativa(concurso_id)

    por_disciplina = {}
    for item in prioridades:
        por_disciplina.setdefault(int(item["disciplina_id"]), []).append(
            float(item.get("score_adaptativo", 0.0) or 0.0)
        )

    resultado = []
    for item in disciplinas:
        scores = sorted(
            por_disciplina.get(int(item["disciplina_id"]), []),
            reverse=True,
        )
        if scores:
            # Usa a metade mais frágil da matéria, sem deixar um único tópico
            # extremo dominar a prova inteira.
            n = max(1, (len(scores) + 1) // 2)
            pressao = sum(scores[:n]) / n
        else:
            pressao = 50.0

        # 0 -> 0,82x | 50 -> 1,00x | 100 -> 1,18x
        fator = 0.82 + 0.36 * max(0.0, min(100.0, pressao)) / 100.0
        novo = dict(item)
        novo["pressao_estrategica"] = round(pressao, 1)
        novo["fator_estrategico"] = round(fator, 3)
        novo["peso_simulado_estrategico"] = round(
            float(item.get("peso_estrutural", 0.0) or 0.0) * fator,
            4,
        )
        resultado.append(novo)

    return resultado


def planejar_simulado_inteligente(
    concurso_id=None,
    quantidade=50,
    estrategia="equilibrado"
):
    """Planejamento dos modos Equilibrado e Estratégico do Simulado V2."""
    if concurso_id is None:
        concurso_id = obter_concurso_ativo()[0]
    concurso_id = int(concurso_id)
    estrategia = str(estrategia or "equilibrado").strip().lower()

    if estrategia not in ("equilibrado", "estrategico"):
        estrategia = "equilibrado"

    if estrategia == "equilibrado":
        plano = planejar_simulado_vighna(concurso_id, quantidade)
        plano = dict(plano)
        plano["tipo"] = "Equilibrado"
        plano["estrategia"] = "equilibrado"
        plano["versao_simulado"] = "simulado_v2"
        plano["criterio"] = (
            "Estrutura do perfil + importância média, sem priorizar fraquezas pessoais."
        )
        return plano

    disciplinas = obter_disponibilidade_simulado_estrategico_disciplinas(concurso_id)
    alocacoes, solicitado, quantidade_final, total_disponivel = (
        _alocar_quantidades_simulado_por_peso(
            disciplinas,
            quantidade,
            campo_peso="peso_simulado_estrategico",
        )
    )

    return {
        "tipo": "Estratégico",
        "estrategia": "estrategico",
        "versao_simulado": "simulado_v2",
        "quantidade_solicitada": solicitado,
        "quantidade": quantidade_final,
        "total_disponivel": total_disponivel,
        "alocacoes": alocacoes,
        "criterio": (
            "Estrutura do perfil com ajuste moderado por fragilidades do Domínio V2; "
            "não concentra a prova como um treino adaptativo."
        ),
    }


def _selecionar_questoes_simulado_disciplina_estrategico(
    concurso_id,
    disciplina_id,
    quantidade,
    preferir_ineditas=True
):
    """Seleção tópico a tópico com viés moderado para fragilidades."""
    concurso_id = int(concurso_id)
    disciplina_id = int(disciplina_id)
    quantidade = max(0, int(quantidade or 0))
    if quantidade <= 0:
        return []

    todas = listar_questoes_resolucao(
        concurso_id,
        disciplina_id=disciplina_id,
        somente_ineditas=False,
        aleatorio=True,
    )
    if not todas:
        return []

    prioridades = obter_prioridades_sessao_adaptativa(
        concurso_id,
        disciplina_id=disciplina_id,
    )
    score_topico = {
        int(item["topico_id"]): float(item.get("score_adaptativo", 50.0) or 50.0)
        for item in prioridades
    }

    grupos = {}
    for item in todas:
        topico_id = int(item["topico_id"])
        grupo = grupos.setdefault(topico_id, {"ineditas": [], "demais": [], "usadas": 0})
        chave = "ineditas" if item.get("inedita") else "demais"
        grupo[chave].append(item)

    for grupo in grupos.values():
        random.shuffle(grupo["ineditas"])
        random.shuffle(grupo["demais"])

    selecionadas = []
    usados = set()

    while len(selecionadas) < quantidade:
        candidatos = []
        pesos = []

        for topico_id, grupo in grupos.items():
            if preferir_ineditas:
                fila = grupo["ineditas"] if grupo["ineditas"] else grupo["demais"]
            else:
                fila = grupo["ineditas"] + grupo["demais"]

            fila = [item for item in fila if int(item["id"]) not in usados]
            if not fila:
                continue

            prioridade = max(0.0, min(100.0, score_topico.get(topico_id, 50.0)))
            # Viés propositalmente moderado (1,00 a 1,70) e penalidade por
            # repetição do mesmo tópico para preservar formato de prova.
            peso = (1.0 + 0.70 * prioridade / 100.0) / (1.0 + 0.75 * grupo["usadas"])
            candidatos.append((topico_id, fila))
            pesos.append(max(0.05, peso))

        if not candidatos:
            break

        indice = random.choices(range(len(candidatos)), weights=pesos, k=1)[0]
        topico_id, fila = candidatos[indice]
        item = random.choice(fila)
        qid = int(item["id"])
        if qid in usados:
            continue

        usados.add(qid)
        grupos[topico_id]["usadas"] += 1
        # Retira da fila original para evitar custo crescente.
        for chave in ("ineditas", "demais"):
            grupos[topico_id][chave] = [
                q for q in grupos[topico_id][chave] if int(q["id"]) != qid
            ]

        item["prioridade_estrategica_topico"] = round(score_topico.get(topico_id, 50.0), 1)
        selecionadas.append(item)

    return selecionadas


def montar_simulado_inteligente(
    concurso_id,
    quantidade,
    estrategia="equilibrado",
    preferir_ineditas=True
):
    estrategia = str(estrategia or "equilibrado").strip().lower()
    plano = planejar_simulado_inteligente(
        concurso_id,
        quantidade,
        estrategia=estrategia,
    )

    if estrategia == "estrategico":
        filas = {}
        ordem = []
        for alocacao in plano.get("alocacoes", []):
            disciplina_id = int(alocacao["disciplina_id"])
            fila = _selecionar_questoes_simulado_disciplina_estrategico(
                concurso_id,
                disciplina_id,
                alocacao["quantidade"],
                preferir_ineditas=preferir_ineditas,
            )
            for item in fila:
                item["sessao_simulado"] = True
                item["motivo_simulado"] = (
                    "Simulado estratégico V2: leve reforço de fragilidades, "
                    "preservando diversidade de tópicos e formato de prova."
                )
            filas[disciplina_id] = fila
            ordem.append(disciplina_id)

        fila_final = []
        while True:
            adicionou = False
            for disciplina_id in ordem:
                fila = filas.get(disciplina_id, [])
                if not fila:
                    continue
                fila_final.append(fila.pop(0))
                adicionou = True
            if not adicionou:
                break

        return {
            "fila": fila_final,
            "plano": plano,
            "preferir_ineditas": bool(preferir_ineditas),
            "tipo": "Estratégico",
            "estrategia": "estrategico",
            "versao_simulado": "simulado_v2",
        }

    selecao = selecionar_questoes_simulado(
        concurso_id,
        plano,
        preferir_ineditas=preferir_ineditas,
    )
    return {
        **selecao,
        "tipo": "Equilibrado",
        "estrategia": "equilibrado",
        "versao_simulado": "simulado_v2",
    }


def analisar_resultado_simulado_v2(
    sessao_id,
    concurso_id,
    dominio_antes=None
):
    """Analisa um simulado concluído sem mexer na agenda de revisões."""
    sessao_id = int(sessao_id)
    concurso_id = int(concurso_id)
    dominio_antes = dict(dominio_antes or {})

    with conectar() as conexao:
        linhas = conexao.execute(
            """
            SELECT
                tq.id,
                COALESCE(tq.questao_id_snapshot, tq.questao_id) AS questao_id,
                COALESCE(tq.topico_id_snapshot, q.topico_id) AS topico_id,
                COALESCE(tq.disciplina_snapshot, d.nome, '—') AS disciplina,
                COALESCE(tq.topico_snapshot, t.nome, '—') AS topico,
                COALESCE(NULLIF(tq.dificuldade_snapshot, ''), NULLIF(q.dificuldade, ''), 'Não informada') AS dificuldade,
                tq.correta,
                tq.marcada_duvida,
                (
                    SELECT COUNT(*)
                    FROM tentativas_questoes p
                    WHERE p.concurso_id = ?
                      AND COALESCE(p.sessao_id, -1) <> ?
                      AND COALESCE(p.questao_id_snapshot, p.questao_id) = COALESCE(tq.questao_id_snapshot, tq.questao_id)
                      AND p.correta = 0
                ) AS erros_anteriores
            FROM tentativas_questoes tq
            LEFT JOIN questoes q ON q.id = tq.questao_id
            LEFT JOIN topicos t ON t.id = COALESCE(tq.topico_id_snapshot, q.topico_id)
            LEFT JOIN disciplinas d ON d.id = t.disciplina_id
            WHERE tq.sessao_id = ?
            ORDER BY tq.id
            """,
            (concurso_id, sessao_id, sessao_id),
        ).fetchall()

    def bucket_dificuldade(valor):
        texto = str(valor or "").strip().lower()
        if texto in ("fácil", "facil"):
            return "Fácil"
        if texto in ("média", "media", "médio", "medio"):
            return "Média"
        if texto in ("difícil", "dificil"):
            return "Difícil"
        return "Não informada"

    por_dificuldade = {
        chave: {"total": 0, "respondidas": 0, "acertos": 0, "erros": 0, "puladas": 0}
        for chave in ("Fácil", "Média", "Difícil", "Não informada")
    }
    por_topico = {}
    erros_novos = 0
    erros_recorrentes = 0
    erros_recuperados = 0

    for linha in linhas:
        questao_id = linha[1]
        topico_id = linha[2]
        dificuldade = bucket_dificuldade(linha[5])
        correta = linha[6]
        erros_anteriores = int(linha[8] or 0)

        bucket = por_dificuldade[dificuldade]
        bucket["total"] += 1
        if correta is None:
            bucket["puladas"] += 1
        else:
            bucket["respondidas"] += 1
            if int(correta) == 1:
                bucket["acertos"] += 1
                if erros_anteriores > 0:
                    erros_recuperados += 1
            else:
                bucket["erros"] += 1
                if erros_anteriores > 0:
                    erros_recorrentes += 1
                else:
                    erros_novos += 1

        if topico_id is None:
            continue
        topico_id = int(topico_id)
        item = por_topico.setdefault(
            topico_id,
            {
                "topico_id": topico_id,
                "disciplina": linha[3],
                "topico": linha[4],
                "respondidas": 0,
                "acertos": 0,
                "erros": 0,
                "puladas": 0,
            },
        )
        if correta is None:
            item["puladas"] += 1
        else:
            item["respondidas"] += 1
            if int(correta) == 1:
                item["acertos"] += 1
            else:
                item["erros"] += 1

    for dados in por_dificuldade.values():
        dados["desempenho"] = (
            round(100.0 * dados["acertos"] / dados["respondidas"], 1)
            if dados["respondidas"] > 0 else None
        )

    categorias = {
        "confirmado": [],
        "superestimado": [],
        "recuperacao": [],
        "piorou": [],
        "monitorar": [],
        "insuficiente": [],
    }
    topicos_resultado = []

    for topico_id, item in por_topico.items():
        antes = dominio_antes.get(str(topico_id), dominio_antes.get(topico_id, {}))
        if isinstance(antes, (int, float)):
            score_antes = float(antes)
        else:
            score_antes = float(dict(antes or {}).get("score", 0.0) or 0.0)

        depois_obj = obter_indice_dominio_topico(topico_id, concurso_id)
        score_depois = float((depois_obj or {}).get("score", 0.0) or 0.0)
        desempenho = (
            100.0 * item["acertos"] / item["respondidas"]
            if item["respondidas"] > 0 else None
        )
        delta = score_depois - score_antes

        if item["respondidas"] < 3:
            categoria = "insuficiente"
        elif score_antes >= 75.0 and desempenho is not None and desempenho < 60.0:
            categoria = "superestimado"
        elif score_antes < 70.0 and desempenho is not None and desempenho >= 75.0 and delta >= 2.0:
            categoria = "recuperacao"
        elif desempenho is not None and (desempenho < 50.0 or delta <= -5.0):
            categoria = "piorou"
        elif desempenho is not None and desempenho >= 75.0 and score_depois >= 70.0 and delta >= -3.0:
            categoria = "confirmado"
        else:
            categoria = "monitorar"

        registro = {
            **item,
            "desempenho": round(desempenho, 1) if desempenho is not None else None,
            "dominio_antes": round(score_antes, 1),
            "dominio_depois": round(score_depois, 1),
            "delta_dominio": round(delta, 1),
            "categoria": categoria,
        }
        categorias[categoria].append(registro)
        topicos_resultado.append(registro)

    topicos_resultado.sort(
        key=lambda item: (
            item["categoria"],
            item["disciplina"].lower(),
            item["topico"].lower(),
        )
    )

    return {
        "versao": "simulado_v2",
        "por_dificuldade": por_dificuldade,
        "erros": {
            "novos": erros_novos,
            "recorrentes": erros_recorrentes,
            "recuperados": erros_recuperados,
        },
        "validacao_dominio": {
            chave: len(valor)
            for chave, valor in categorias.items()
        },
        "topicos": topicos_resultado,
    }


def registrar_analise_simulado_v2(sessao_id, analise):
    """Persiste a análise V2 no JSON do simulado para relatórios futuros."""
    sessao_id = int(sessao_id)
    with conectar() as conexao:
        linha = conexao.execute(
            "SELECT configuracao_json FROM simulados WHERE sessao_id = ?",
            (sessao_id,),
        ).fetchone()
        if linha is None:
            return False
        try:
            config = json.loads(linha[0] or "{}")
        except Exception:
            config = {}
        config["analise_v2"] = dict(analise or {})
        conexao.execute(
            "UPDATE simulados SET configuracao_json = ? WHERE sessao_id = ?",
            (json.dumps(config, ensure_ascii=False, default=str), sessao_id),
        )
    return True

def registrar_configuracao_simulado(
    sessao_id,
    configuracao
):
    sessao_id = int(
        sessao_id
    )

    configuracao = dict(
        configuracao
        or {}
    )

    concurso_id = configuracao.get(
        "concurso_id"
    )

    if concurso_id is not None:
        concurso_id = int(
            concurso_id
        )

    tipo = str(
        configuracao.get(
            "tipo_simulado"
        )
        or "Personalizado"
    )

    tempo = max(
        0,
        int(
            configuracao.get(
                "tempo_limite_minutos"
            )
            or 0
        )
    )

    preferir = bool(
        configuracao.get(
            "preferir_ineditas",
            True
        )
    )

    resumo_config = {
        "tipo": tipo,
        "versao_simulado": configuracao.get(
            "versao_simulado",
            "simulado_v1"
        ),
        "estrategia_simulado": configuracao.get(
            "estrategia_simulado",
            "prova_real"
        ),
        "tempo_limite_minutos": tempo,
        "preferir_ineditas": preferir,
        "plano": configuracao.get(
            "plano_simulado",
            {}
        ),
        "dominio_antes": configuracao.get(
            "dominio_antes_simulado",
            {}
        ),
    }

    with conectar() as conexao:
        conexao.execute(
            """
            INSERT OR REPLACE INTO simulados (
                sessao_id,
                concurso_id,
                tipo,
                tempo_limite_minutos,
                preferir_ineditas,
                configuracao_json
            )
            VALUES (
                ?,
                ?,
                ?,
                ?,
                ?,
                ?
            )
            """,
            (
                sessao_id,
                concurso_id,
                tipo,
                tempo,
                1 if preferir else 0,
                json.dumps(
                    resumo_config,
                    ensure_ascii=False,
                    default=str
                ),
            )
        )



def obter_resumo_simulados_dashboard(
    concurso_id=None
):
    """Resumo compacto dos simulados concluídos do perfil ativo."""

    if concurso_id is None:
        concurso_id = obter_concurso_ativo()[0]

    concurso_id = int(concurso_id)

    with conectar() as conexao:
        linhas = conexao.execute(
            """
            SELECT
                s.id,
                s.criado_em,
                s.tipo,
                COUNT(
                    CASE
                        WHEN tq.correta IS NOT NULL
                        THEN 1
                    END
                ) AS respondidas,
                SUM(
                    CASE
                        WHEN tq.correta = 1
                        THEN 1
                        ELSE 0
                    END
                ) AS acertos
            FROM simulados s
            JOIN sessoes_questoes sq
                ON sq.id = s.sessao_id
            LEFT JOIN tentativas_questoes tq
                ON tq.sessao_id = s.sessao_id
            WHERE
                s.concurso_id = ?
                AND sq.encerrado_em IS NOT NULL
            GROUP BY
                s.id,
                s.criado_em,
                s.tipo
            HAVING respondidas > 0
            ORDER BY
                s.criado_em DESC,
                s.id DESC
            """,
            (concurso_id,)
        ).fetchall()

    if not linhas:
        return {
            "realizados": 0,
            "ultimo_percentual": None,
            "melhor_percentual": None,
            "ultimo_tipo": None,
            "ultimo_em": None,
        }

    resultados = []

    for linha in linhas:
        respondidas = int(linha[3] or 0)
        acertos = int(linha[4] or 0)
        percentual = (
            100.0 * acertos / respondidas
            if respondidas > 0
            else None
        )

        resultados.append({
            "id": int(linha[0]),
            "criado_em": linha[1],
            "tipo": linha[2],
            "respondidas": respondidas,
            "acertos": acertos,
            "percentual": percentual,
        })

    ultimo = resultados[0]
    percentuais = [
        item["percentual"]
        for item in resultados
        if item["percentual"] is not None
    ]

    return {
        "realizados": len(resultados),
        "ultimo_percentual": ultimo["percentual"],
        "melhor_percentual": max(percentuais) if percentuais else None,
        "ultimo_tipo": ultimo["tipo"],
        "ultimo_em": ultimo["criado_em"],
    }


def obter_configuracao_simulado(
    sessao_id
):
    with conectar() as conexao:
        linha = conexao.execute(
            """
            SELECT
                id,
                sessao_id,
                concurso_id,
                tipo,
                tempo_limite_minutos,
                preferir_ineditas,
                configuracao_json,
                criado_em
            FROM simulados
            WHERE sessao_id = ?
            """,
            (
                int(
                    sessao_id
                ),
            )
        ).fetchone()

    if linha is None:
        return None

    try:
        config = json.loads(
            linha[6]
            or "{}"
        )
    except Exception:
        config = {}

    return {
        "id": linha[0],
        "sessao_id": linha[1],
        "concurso_id": linha[2],
        "tipo": linha[3],
        "tempo_limite_minutos": int(
            linha[4]
            or 0
        ),
        "preferir_ineditas": bool(
            linha[5]
        ),
        "configuracao": config,
        "criado_em": linha[7],
    }


def selecionar_questoes_inteligentes(
    concurso_id=None,
    disciplina_id=None,
    topico_id=None,
    quantidade=20
):
    perfil = (
        obter_perfil_selecao_inteligente_questoes(
            concurso_id,
            disciplina_id=disciplina_id,
            topico_id=topico_id
        )
    )

    quantidade = max(
        1,
        int(
            quantidade
        )
    )

    quantidade = min(
        quantidade,
        perfil[
            "total_disponivel"
        ]
    )

    if quantidade <= 0:
        return {
            **perfil,
            "fila": [],
            "composicao": {},
            "modo": "Sessão inteligente",
        }

    pesos = _pesos_selecao_inteligente(
        perfil[
            "perfil"
        ]
    )

    buckets = {}

    for item in perfil[
        "questoes"
    ]:
        buckets.setdefault(
            item[
                "categoria_inteligente"
            ],
            []
        ).append(
            item
        )

    for categoria in list(
        buckets
    ):
        buckets[
            categoria
        ] = _ordenar_bucket_inteligente(
            categoria,
            buckets[
                categoria
            ]
        )

    selecionadas = []
    usados = set()
    contagem_selecionada = {}

    categorias_ordenadas = [
        "recorrente",
        "recuperacao",
        "erro",
        "inedita",
        "controle",
        "dominada",
    ]

    while len(
        selecionadas
    ) < quantidade:
        disponiveis = [
            categoria
            for categoria in categorias_ordenadas
            if buckets.get(
                categoria
            )
        ]

        if not disponiveis:
            break

        # Escolhe a categoria que está mais abaixo da cota adaptativa.
        melhor_categoria = max(
            disponiveis,
            key=lambda categoria: (
                (
                    pesos.get(
                        categoria,
                        0.0
                    )
                    * quantidade
                )
                - contagem_selecionada.get(
                    categoria,
                    0
                ),
                pesos.get(
                    categoria,
                    0.0
                ),
                -categorias_ordenadas.index(
                    categoria
                ),
            )
        )

        item = buckets[
            melhor_categoria
        ].pop(
            0
        )

        if item[
            "id"
        ] in usados:
            continue

        usados.add(
            item[
                "id"
            ]
        )

        motivo = {
            "inedita": (
                "Questão inédita para ampliar a cobertura."
            ),
            "recorrente": (
                "Erro recorrente com prioridade elevada."
            ),
            "recuperacao": (
                "Questão em recuperação; precisa confirmar retenção."
            ),
            "erro": (
                "Questão já errada anteriormente."
            ),
            "controle": (
                "Questão de controle para validar estabilidade."
            ),
            "dominada": (
                "Questão dominada usada como amostra de retenção."
            ),
        }[
            melhor_categoria
        ]

        selecionadas.append({
            **item,
            "motivo_inteligente": motivo,
            "score_inteligente": round(
                float(
                    item[
                        "prioridade_base"
                    ]
                ),
                1
            ),
        })

        contagem_selecionada[
            melhor_categoria
        ] = (
            contagem_selecionada.get(
                melhor_categoria,
                0
            )
            + 1
        )

    composicao = {}

    for item in selecionadas:
        rotulo = item[
            "categoria_rotulo"
        ]
        composicao[
            rotulo
        ] = (
            composicao.get(
                rotulo,
                0
            )
            + 1
        )

    return {
        **perfil,
        "fila": selecionadas,
        "composicao": composicao,
        "modo": "Sessão inteligente",
    }


def selecionar_questoes_por_modo(
    concurso_id=None,
    disciplina_id=None,
    topico_id=None,
    quantidade=20,
    modo="Sessão inteligente"
):
    modo = str(
        modo
        or "Sessão inteligente"
    )

    perfil = (
        obter_perfil_selecao_inteligente_questoes(
            concurso_id,
            disciplina_id=disciplina_id,
            topico_id=topico_id
        )
    )

    quantidade = max(
        1,
        int(
            quantidade
        )
    )

    if modo == "Sessão inteligente":
        return selecionar_questoes_inteligentes(
            concurso_id,
            disciplina_id=disciplina_id,
            topico_id=topico_id,
            quantidade=quantidade
        )

    candidatos = list(
        perfil[
            "questoes"
        ]
    )

    if modo == "Apenas inéditas":
        candidatos = [
            item
            for item in candidatos
            if item[
                "categoria_inteligente"
            ] == "inedita"
        ]
        random.shuffle(
            candidatos
        )

    elif modo == "Revisar erros":
        candidatos = [
            item
            for item in candidatos
            if item[
                "teve_erro"
            ]
        ]

        ordem = {
            "recorrente": 0,
            "recuperacao": 1,
            "erro": 2,
            "dominada": 3,
            "controle": 4,
            "inedita": 5,
        }

        random.shuffle(
            candidatos
        )
        candidatos.sort(
            key=lambda item: (
                ordem.get(
                    item[
                        "categoria_inteligente"
                    ],
                    9
                ),
                -item[
                    "prioridade_base"
                ],
                (
                    item[
                        "taxa_acerto"
                    ]
                    if item[
                        "taxa_acerto"
                    ] is not None
                    else 101.0
                ),
            )
        )

    else:
        random.shuffle(
            candidatos
        )

    fila = candidatos[
        :min(
            quantidade,
            len(
                candidatos
            )
        )
    ]

    for item in fila:
        if modo == "Apenas inéditas":
            motivo = (
                "Questão inédita."
            )
        elif modo == "Revisar erros":
            motivo = (
                "Selecionada pelo histórico de erro."
            )
        else:
            motivo = (
                "Seleção aleatória."
            )

        item[
            "motivo_inteligente"
        ] = motivo
        item[
            "score_inteligente"
        ] = round(
            float(
                item[
                    "prioridade_base"
                ]
            ),
            1
        )

    composicao = {}

    for item in fila:
        rotulo = item[
            "categoria_rotulo"
        ]
        composicao[
            rotulo
        ] = (
            composicao.get(
                rotulo,
                0
            )
            + 1
        )

    return {
        **perfil,
        "fila": fila,
        "composicao": composicao,
        "modo": modo,
    }


def contar_questoes_disponiveis_por_modo(
    concurso_id=None,
    disciplina_id=None,
    topico_id=None,
    modo="Sessão inteligente"
):
    perfil = (
        obter_perfil_selecao_inteligente_questoes(
            concurso_id,
            disciplina_id=disciplina_id,
            topico_id=topico_id
        )
    )

    modo = str(
        modo
        or "Sessão inteligente"
    )

    if modo == "Apenas inéditas":
        return int(
            perfil[
                "contagens"
            ].get(
                "inedita",
                0
            )
        )

    if modo == "Revisar erros":
        return sum(
            1
            for item in perfil[
                "questoes"
            ]
            if item[
                "teve_erro"
            ]
        )

    return int(
        perfil[
            "total_disponivel"
        ]
    )


def _normalizar_nome_topico_equivalente(
    nome
):
    texto = unicodedata.normalize(
        "NFD",
        str(
            nome
            or ""
        ).lower()
    )
    texto = "".join(
        caractere
        for caractere in texto
        if unicodedata.category(
            caractere
        ) != "Mn"
    )
    texto = re.sub(
        r"^(?:titulo|capitulo|secao)\s+"
        r"(?:[ivxlcdm]+|\d+)\s*[:.\-–—]?\s*",
        "",
        texto
    )
    texto = re.sub(
        r"^(?:da|das|de|do|dos)\s+",
        "",
        texto
    )
    texto = re.sub(
        r"[^a-z0-9]+",
        " ",
        texto
    )

    return " ".join(
        texto.split()
    )


def listar_topicos_equivalentes_com_questoes(
    concurso_id,
    topico_id
):
    concurso_id = int(
        concurso_id
    )
    topico_id = int(
        topico_id
    )

    with conectar() as conexao:
        origem = conexao.execute(
            """
            SELECT
                disciplina_id,
                nome
            FROM topicos
            WHERE id = ?
            """,
            (
                topico_id,
            )
        ).fetchone()

        if origem is None:
            return []

        candidatos = conexao.execute(
            """
            SELECT
                t.id,
                t.nome,
                COUNT(q.id) AS quantidade
            FROM topicos t
            JOIN questoes q
                ON q.topico_id = t.id
                AND q.ativa = 1
                AND COALESCE(q.excluida, 0) = 0
            JOIN disciplina_concurso_inclusao dc
                ON dc.disciplina_id = t.disciplina_id
                AND dc.concurso_id = ?
                AND dc.incluido = 1
                AND COALESCE(dc.pausado, 0) = 0
            JOIN topico_concurso_importancia tc
                ON tc.topico_id = t.id
                AND tc.concurso_id = ?
                AND tc.incluido = 1
                AND COALESCE(tc.pausado, 0) = 0
            WHERE
                t.disciplina_id = ?
                AND t.id <> ?
            GROUP BY
                t.id,
                t.nome
            ORDER BY
                quantidade DESC,
                t.nome COLLATE NOCASE,
                t.id
            """,
            (
                concurso_id,
                concurso_id,
                int(
                    origem[0]
                ),
                topico_id,
            )
        ).fetchall()

    chave_origem = (
        _normalizar_nome_topico_equivalente(
            origem[1]
        )
    )

    if not chave_origem:
        return []

    return [
        {
            "topico_id": int(
                candidato[0]
            ),
            "nome": str(
                candidato[1]
            ),
            "quantidade": int(
                candidato[2]
                or 0
            ),
        }
        for candidato in candidatos
        if (
            _normalizar_nome_topico_equivalente(
                candidato[1]
            )
            == chave_origem
        )
    ]


def listar_questoes_resolucao(
    concurso_id=None,
    disciplina_id=None,
    topico_id=None,
    somente_ineditas=False,
    limite=None,
    aleatorio=False
):
    """
    Lista questões aptas para uma sessão de resolução.

    Uma questão é considerada inédita quando ainda não existe resposta
    efetiva para ela no perfil informado. Registros pulados, cujo campo
    correta é NULL, não retiram a condição de inédita.
    """

    if concurso_id is None:
        concurso_id = (
            obter_concurso_ativo()[0]
        )

    concurso_id = int(
        concurso_id
    )

    parametros = [
        concurso_id,
        concurso_id,
        concurso_id,
    ]

    filtros = [
        "q.ativa = 1"
    ]

    if disciplina_id is not None:
        filtros.append(
            "d.id = ?"
        )
        parametros.append(
            int(
                disciplina_id
            )
        )

    if topico_id is not None:
        filtros.append(
            "t.id = ?"
        )
        parametros.append(
            int(
                topico_id
            )
        )

    if somente_ineditas:
        filtros.append(
            """
            NOT EXISTS (
                SELECT 1
                FROM tentativas_questoes tq_inedita
                WHERE
                    tq_inedita.questao_id = q.id
                    AND tq_inedita.concurso_id = ?
                    AND tq_inedita.correta IS NOT NULL
            )
            """
        )
        parametros.append(
            concurso_id
        )

    ordem = (
        "RANDOM()"
        if aleatorio
        else (
            "d.nome COLLATE NOCASE, "
            "t.nome COLLATE NOCASE, "
            "q.id"
        )
    )

    limite_sql = ""

    if limite is not None:
        limite = max(
            1,
            int(
                limite
            )
        )
        limite_sql = "LIMIT ?"
        parametros.append(
            limite
        )

    with conectar() as conexao:
        linhas = conexao.execute(
            f"""
            SELECT
                q.id,
                q.topico_id,
                d.id AS disciplina_id,
                d.nome AS disciplina,
                t.nome AS topico,
                q.enunciado,
                q.banca,
                q.ano,
                q.dificuldade,
                (
                    SELECT COUNT(*)
                    FROM tentativas_questoes tq
                    WHERE
                        tq.questao_id = q.id
                        AND tq.concurso_id = ?
                        AND tq.correta IS NOT NULL
                ) AS tentativas_anteriores
            FROM questoes q
            JOIN topicos t
                ON t.id = q.topico_id
            JOIN disciplinas d
                ON d.id = t.disciplina_id
            JOIN disciplina_concurso_inclusao dc
                ON dc.disciplina_id = d.id
                AND dc.concurso_id = ?
                AND dc.incluido = 1
                AND COALESCE(dc.pausado, 0) = 0
            JOIN topico_concurso_importancia tc
                ON tc.topico_id = t.id
                AND tc.concurso_id = ?
                AND tc.incluido = 1
                AND COALESCE(tc.pausado, 0) = 0
            WHERE
                {' AND '.join(filtros)}
            ORDER BY {ordem}
            {limite_sql}
            """,
            parametros
        ).fetchall()

    return [
        {
            "id": linha[0],
            "topico_id": linha[1],
            "disciplina_id": linha[2],
            "disciplina": linha[3],
            "topico": linha[4],
            "enunciado": linha[5],
            "banca": linha[6] or "",
            "ano": linha[7],
            "dificuldade": (
                linha[8]
                or "Não informada"
            ),
            "tentativas_anteriores": int(
                linha[9] or 0
            ),
            "inedita": (
                int(
                    linha[9] or 0
                ) == 0
            ),
        }
        for linha in linhas
    ]



def _media_ou_none(
    valores
):
    valores = [
        float(
            valor
        )
        for valor in valores
        if valor is not None
    ]

    if not valores:
        return None

    return (
        sum(
            valores
        )
        / len(
            valores
        )
    )


def iniciar_medicao_efetividade_sessao(
    sessao_id,
    configuracao
):
    """
    Congela a linha de base ANTES da primeira resposta da sessão.

    Sessões anteriores à instalação desta versão não são reconstruídas,
    porque não existe forma confiável de saber qual era exatamente o
    Índice de Domínio naquele instante.
    """

    sessao_id = int(
        sessao_id
    )

    configuracao = dict(
        configuracao
        or {}
    )

    concurso_id = int(
        configuracao.get(
            "concurso_id"
        )
        or obter_concurso_ativo()[0]
    )

    fila = list(
        configuracao.get(
            "fila"
        )
        or []
    )

    modo = str(
        configuracao.get(
            "modo"
        )
        or "Sessão de questões"
    )

    estrategia = dict(
        configuracao.get(
            "estrategia_adaptativa"
        )
        or {}
    )

    escopo = str(
        estrategia.get(
            "escopo"
        )
        or (
            configuracao.get(
                "topico_nome"
            )
            or configuracao.get(
                "disciplina_nome"
            )
            or "Perfil ativo"
        )
    )

    # Agrupa o plano efetivamente recebido pelo resolvedor.
    topicos_planejados = {}

    for item in fila:
        topico_id = item.get(
            "topico_id"
        )

        if topico_id is None:
            continue

        topico_id = int(
            topico_id
        )

        registro = topicos_planejados.setdefault(
            topico_id,
            {
                "topico_id": topico_id,
                "disciplina": str(
                    item.get(
                        "disciplina"
                    )
                    or "—"
                ),
                "topico": str(
                    item.get(
                        "topico"
                    )
                    or "—"
                ),
                "planejadas": 0,
                "motivos": {},
                "detalhes": [],
                "prioridades": [],
            }
        )

        registro[
            "planejadas"
        ] += 1

        motivo = str(
            item.get(
                "motivo_adaptativo_principal"
            )
            or (
                "seleção inteligente"
                if modo
                == "Sessão inteligente"
                else modo.lower()
            )
        )

        registro[
            "motivos"
        ][
            motivo
        ] = (
            registro[
                "motivos"
            ].get(
                motivo,
                0
            )
            + 1
        )

        detalhe = str(
            item.get(
                "motivo_adaptativo"
            )
            or item.get(
                "motivo_inteligente"
            )
            or ""
        ).strip()

        if (
            detalhe
            and detalhe
            not in registro[
                "detalhes"
            ]
        ):
            registro[
                "detalhes"
            ].append(
                detalhe
            )

        prioridade = item.get(
            "prioridade_topico"
        )

        if prioridade is not None:
            try:
                registro[
                    "prioridades"
                ].append(
                    float(
                        prioridade
                    )
                )
            except Exception:
                pass

    if not topicos_planejados:
        return None

    indices = (
        obter_indices_dominio_topicos(
            concurso_id
        )
    )

    linhas_topicos = []

    for topico_id, registro in (
        topicos_planejados.items()
    ):
        indice = indices.get(
            topico_id,
            {}
        )

        motivo_principal = max(
            registro[
                "motivos"
            ],
            key=lambda chave: (
                registro[
                    "motivos"
                ][
                    chave
                ],
                chave
            )
        )

        prioridade_media = (
            _media_ou_none(
                registro[
                    "prioridades"
                ]
            )
        )

        linhas_topicos.append({
            **registro,
            "motivo_principal": (
                motivo_principal
            ),
            "motivo_detalhado": (
                " | ".join(
                    registro[
                        "detalhes"
                    ][
                        :3
                    ]
                )
            ),
            "prioridade_adaptativa": (
                prioridade_media
            ),
            "dominio_antes": float(
                indice.get(
                    "score",
                    0.0
                )
                or 0.0
            ),
            "cobertura_antes": float(
                indice.get(
                    "cobertura",
                    0.0
                )
                or 0.0
            ),
            "recorrentes_antes": int(
                indice.get(
                    "recorrentes",
                    0
                )
                or 0
            ),
            "criticas_antes": int(
                indice.get(
                    "criticas",
                    0
                )
                or 0
            ),
        })

    dominio_medio = _media_ou_none([
        item[
            "dominio_antes"
        ]
        for item in linhas_topicos
    ])

    cobertura_media = (
        _media_ou_none([
            item[
                "cobertura_antes"
            ]
            for item in linhas_topicos
        ])
    )

    recorrentes_antes = sum(
        item[
            "recorrentes_antes"
        ]
        for item in linhas_topicos
    )

    criticas_antes = sum(
        item[
            "criticas_antes"
        ]
        for item in linhas_topicos
    )

    estrategia_resumida = {
        "escopo": escopo,
        "modo": modo,
        "composicao_topicos": (
            estrategia.get(
                "composicao_topicos",
                {}
            )
        ),
        "resumo_motivos": (
            estrategia.get(
                "resumo_motivos",
                {}
            )
        ),
        "pesos": (
            (
                estrategia.get(
                    "plano",
                    {}
                )
                or {}
            ).get(
                "pesos",
                {}
            )
        ),
    }

    with conectar() as conexao:
        conexao.execute(
            """
            INSERT OR REPLACE INTO efetividade_sessoes (
                sessao_id,
                concurso_id,
                modo,
                escopo,
                criado_em,
                finalizado_em,
                concluida,
                topicos,
                respostas,
                acertos,
                desempenho,
                tempo_segundos,
                dominio_medio_antes,
                dominio_medio_depois,
                cobertura_media_antes,
                cobertura_media_depois,
                recorrentes_antes,
                recorrentes_depois,
                criticas_antes,
                criticas_depois,
                estrategia_json,
                versao_algoritmo
            )
            VALUES (
                ?,
                ?,
                ?,
                ?,
                datetime(
                    'now',
                    'localtime'
                ),
                NULL,
                0,
                ?,
                0,
                0,
                NULL,
                0,
                ?,
                NULL,
                ?,
                NULL,
                ?,
                0,
                ?,
                0,
                ?,
                'efetividade_v1'
            )
            """,
            (
                sessao_id,
                concurso_id,
                modo,
                escopo,
                len(
                    linhas_topicos
                ),
                dominio_medio,
                cobertura_media,
                recorrentes_antes,
                criticas_antes,
                json.dumps(
                    estrategia_resumida,
                    ensure_ascii=False,
                    default=str
                ),
            )
        )

        conexao.execute(
            """
            DELETE FROM efetividade_topicos_sessao
            WHERE sessao_id = ?
            """,
            (
                sessao_id,
            )
        )

        for item in linhas_topicos:
            conexao.execute(
                """
                INSERT INTO efetividade_topicos_sessao (
                    sessao_id,
                    topico_id,
                    disciplina_snapshot,
                    topico_snapshot,
                    motivo_principal,
                    motivo_detalhado,
                    prioridade_adaptativa,
                    planejadas,
                    respostas,
                    acertos,
                    tempo_segundos,
                    dominio_antes,
                    dominio_depois,
                    cobertura_antes,
                    cobertura_depois,
                    recorrentes_antes,
                    recorrentes_depois,
                    criticas_antes,
                    criticas_depois
                )
                VALUES (
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    0,
                    0,
                    0,
                    ?,
                    NULL,
                    ?,
                    NULL,
                    ?,
                    0,
                    ?,
                    0
                )
                """,
                (
                    sessao_id,
                    item[
                        "topico_id"
                    ],
                    item[
                        "disciplina"
                    ],
                    item[
                        "topico"
                    ],
                    item[
                        "motivo_principal"
                    ],
                    item[
                        "motivo_detalhado"
                    ],
                    item[
                        "prioridade_adaptativa"
                    ],
                    item[
                        "planejadas"
                    ],
                    item[
                        "dominio_antes"
                    ],
                    item[
                        "cobertura_antes"
                    ],
                    item[
                        "recorrentes_antes"
                    ],
                    item[
                        "criticas_antes"
                    ],
                )
            )

    return {
        "sessao_id": sessao_id,
        "topicos": len(
            linhas_topicos
        ),
        "dominio_medio_antes": (
            dominio_medio
        ),
        "cobertura_media_antes": (
            cobertura_media
        ),
        "recorrentes_antes": (
            recorrentes_antes
        ),
        "criticas_antes": (
            criticas_antes
        ),
    }


def finalizar_medicao_efetividade_sessao(
    sessao_id
):
    sessao_id = int(
        sessao_id
    )

    with conectar() as conexao:
        cabecalho = conexao.execute(
            """
            SELECT
                concurso_id
            FROM efetividade_sessoes
            WHERE sessao_id = ?
            """,
            (
                sessao_id,
            )
        ).fetchone()

        if cabecalho is None:
            return None

        concurso_id = cabecalho[0]

        linhas_base = conexao.execute(
            """
            SELECT
                topico_id
            FROM efetividade_topicos_sessao
            WHERE sessao_id = ?
            """,
            (
                sessao_id,
            )
        ).fetchall()

        sessao = conexao.execute(
            """
            SELECT
                concluida
            FROM sessoes_questoes
            WHERE id = ?
            """,
            (
                sessao_id,
            )
        ).fetchone()

    if concurso_id is None:
        return None

    concurso_id = int(
        concurso_id
    )

    indices = obter_indices_dominio_topicos(
        concurso_id
    )

    topicos_ids = [
        int(
            linha[0]
        )
        for linha in linhas_base
        if linha[0] is not None
    ]

    with conectar() as conexao:
        desempenho_topico = conexao.execute(
            """
            SELECT
                COALESCE(
                    tq.topico_id_snapshot,
                    q.topico_id
                ) AS topico_ref,
                COUNT(
                    CASE
                        WHEN tq.correta IS NOT NULL
                        THEN 1
                    END
                ) AS respostas,
                SUM(
                    CASE
                        WHEN tq.correta = 1
                        THEN 1
                        ELSE 0
                    END
                ) AS acertos,
                SUM(
                    CASE
                        WHEN tq.correta IS NOT NULL
                        THEN COALESCE(
                            tq.tempo_segundos,
                            0
                        )
                        ELSE 0
                    END
                ) AS tempo_segundos
            FROM tentativas_questoes tq
            LEFT JOIN questoes q
                ON q.id = tq.questao_id
            WHERE tq.sessao_id = ?
            GROUP BY
                topico_ref
            """,
            (
                sessao_id,
            )
        ).fetchall()

        mapa_desempenho = {
            int(
                linha[0]
            ): {
                "respostas": int(
                    linha[1]
                    or 0
                ),
                "acertos": int(
                    linha[2]
                    or 0
                ),
                "tempo_segundos": int(
                    linha[3]
                    or 0
                ),
            }
            for linha in desempenho_topico
            if linha[0] is not None
        }

        for topico_id in topicos_ids:
            indice = indices.get(
                topico_id,
                {}
            )

            resultado = mapa_desempenho.get(
                topico_id,
                {
                    "respostas": 0,
                    "acertos": 0,
                    "tempo_segundos": 0,
                }
            )

            conexao.execute(
                """
                UPDATE efetividade_topicos_sessao
                SET
                    respostas = ?,
                    acertos = ?,
                    tempo_segundos = ?,
                    dominio_depois = ?,
                    cobertura_depois = ?,
                    recorrentes_depois = ?,
                    criticas_depois = ?
                WHERE
                    sessao_id = ?
                    AND topico_id = ?
                """,
                (
                    resultado[
                        "respostas"
                    ],
                    resultado[
                        "acertos"
                    ],
                    resultado[
                        "tempo_segundos"
                    ],
                    float(
                        indice.get(
                            "score",
                            0.0
                        )
                        or 0.0
                    ),
                    float(
                        indice.get(
                            "cobertura",
                            0.0
                        )
                        or 0.0
                    ),
                    int(
                        indice.get(
                            "recorrentes",
                            0
                        )
                        or 0
                    ),
                    int(
                        indice.get(
                            "criticas",
                            0
                        )
                        or 0
                    ),
                    sessao_id,
                    topico_id,
                )
            )

        linhas_finais = conexao.execute(
            """
            SELECT
                dominio_antes,
                dominio_depois,
                cobertura_antes,
                cobertura_depois,
                recorrentes_antes,
                recorrentes_depois,
                criticas_antes,
                criticas_depois,
                respostas,
                acertos,
                tempo_segundos
            FROM efetividade_topicos_sessao
            WHERE sessao_id = ?
            """,
            (
                sessao_id,
            )
        ).fetchall()

        dominio_antes = _media_ou_none([
            linha[0]
            for linha in linhas_finais
        ])
        dominio_depois = _media_ou_none([
            linha[1]
            for linha in linhas_finais
        ])
        cobertura_antes = _media_ou_none([
            linha[2]
            for linha in linhas_finais
        ])
        cobertura_depois = _media_ou_none([
            linha[3]
            for linha in linhas_finais
        ])

        recorrentes_antes = sum(
            int(
                linha[4]
                or 0
            )
            for linha in linhas_finais
        )
        recorrentes_depois = sum(
            int(
                linha[5]
                or 0
            )
            for linha in linhas_finais
        )
        criticas_antes = sum(
            int(
                linha[6]
                or 0
            )
            for linha in linhas_finais
        )
        criticas_depois = sum(
            int(
                linha[7]
                or 0
            )
            for linha in linhas_finais
        )

        respostas = sum(
            int(
                linha[8]
                or 0
            )
            for linha in linhas_finais
        )
        acertos = sum(
            int(
                linha[9]
                or 0
            )
            for linha in linhas_finais
        )
        tempo_segundos = sum(
            int(
                linha[10]
                or 0
            )
            for linha in linhas_finais
        )

        desempenho = (
            100.0
            * acertos
            / respostas
            if respostas > 0
            else None
        )

        concluida = bool(
            sessao[0]
        ) if sessao is not None else False

        conexao.execute(
            """
            UPDATE efetividade_sessoes
            SET
                finalizado_em = datetime(
                    'now',
                    'localtime'
                ),
                concluida = ?,
                topicos = ?,
                respostas = ?,
                acertos = ?,
                desempenho = ?,
                tempo_segundos = ?,
                dominio_medio_antes = ?,
                dominio_medio_depois = ?,
                cobertura_media_antes = ?,
                cobertura_media_depois = ?,
                recorrentes_antes = ?,
                recorrentes_depois = ?,
                criticas_antes = ?,
                criticas_depois = ?
            WHERE sessao_id = ?
            """,
            (
                1 if concluida else 0,
                len(
                    linhas_finais
                ),
                respostas,
                acertos,
                desempenho,
                tempo_segundos,
                dominio_antes,
                dominio_depois,
                cobertura_antes,
                cobertura_depois,
                recorrentes_antes,
                recorrentes_depois,
                criticas_antes,
                criticas_depois,
                sessao_id,
            )
        )

    return obter_efetividade_sessao(
        sessao_id
    )


def obter_efetividade_sessao(
    sessao_id
):
    sessao_id = int(
        sessao_id
    )

    with conectar() as conexao:
        linha = conexao.execute(
            """
            SELECT
                es.sessao_id,
                es.concurso_id,
                es.modo,
                es.escopo,
                es.criado_em,
                es.finalizado_em,
                es.concluida,
                es.topicos,
                es.respostas,
                es.acertos,
                es.desempenho,
                es.tempo_segundos,
                es.dominio_medio_antes,
                es.dominio_medio_depois,
                es.cobertura_media_antes,
                es.cobertura_media_depois,
                es.recorrentes_antes,
                es.recorrentes_depois,
                es.criticas_antes,
                es.criticas_depois,
                es.estrategia_json
            FROM efetividade_sessoes es
            WHERE es.sessao_id = ?
            """,
            (
                sessao_id,
            )
        ).fetchone()

        if linha is None:
            return None

        topicos = conexao.execute(
            """
            SELECT
                topico_id,
                disciplina_snapshot,
                topico_snapshot,
                motivo_principal,
                motivo_detalhado,
                prioridade_adaptativa,
                planejadas,
                respostas,
                acertos,
                tempo_segundos,
                dominio_antes,
                dominio_depois,
                cobertura_antes,
                cobertura_depois,
                recorrentes_antes,
                recorrentes_depois,
                criticas_antes,
                criticas_depois
            FROM efetividade_topicos_sessao
            WHERE sessao_id = ?
            ORDER BY
                prioridade_adaptativa DESC,
                disciplina_snapshot COLLATE NOCASE,
                topico_snapshot COLLATE NOCASE
            """,
            (
                sessao_id,
            )
        ).fetchall()

    try:
        estrategia = json.loads(
            linha[20]
            or "{}"
        )
    except Exception:
        estrategia = {}

    def delta(
        antes,
        depois
    ):
        if (
            antes is None
            or depois is None
        ):
            return None

        return float(
            depois
        ) - float(
            antes
        )

    dados_topicos = []

    for item in topicos:
        respostas = int(
            item[7]
            or 0
        )
        acertos = int(
            item[8]
            or 0
        )

        dados_topicos.append({
            "topico_id": item[0],
            "disciplina": (
                item[1]
                or "—"
            ),
            "topico": (
                item[2]
                or "—"
            ),
            "motivo_principal": (
                item[3]
                or "—"
            ),
            "motivo_detalhado": (
                item[4]
                or ""
            ),
            "prioridade_adaptativa": (
                item[5]
            ),
            "planejadas": int(
                item[6]
                or 0
            ),
            "respostas": respostas,
            "acertos": acertos,
            "desempenho": (
                100.0
                * acertos
                / respostas
                if respostas > 0
                else None
            ),
            "tempo_segundos": int(
                item[9]
                or 0
            ),
            "dominio_antes": item[10],
            "dominio_depois": item[11],
            "delta_dominio": delta(
                item[10],
                item[11]
            ),
            "cobertura_antes": item[12],
            "cobertura_depois": item[13],
            "delta_cobertura": delta(
                item[12],
                item[13]
            ),
            "recorrentes_antes": int(
                item[14]
                or 0
            ),
            "recorrentes_depois": int(
                item[15]
                or 0
            ),
            "delta_recorrentes": (
                int(
                    item[14]
                    or 0
                )
                - int(
                    item[15]
                    or 0
                )
            ),
            "criticas_antes": int(
                item[16]
                or 0
            ),
            "criticas_depois": int(
                item[17]
                or 0
            ),
            "delta_criticas": (
                int(
                    item[16]
                    or 0
                )
                - int(
                    item[17]
                    or 0
                )
            ),
        })

    return {
        "sessao_id": int(
            linha[0]
        ),
        "concurso_id": linha[1],
        "modo": (
            linha[2]
            or "—"
        ),
        "escopo": (
            linha[3]
            or "—"
        ),
        "criado_em": linha[4],
        "finalizado_em": linha[5],
        "concluida": bool(
            linha[6]
        ),
        "topicos_quantidade": int(
            linha[7]
            or 0
        ),
        "respostas": int(
            linha[8]
            or 0
        ),
        "acertos": int(
            linha[9]
            or 0
        ),
        "desempenho": linha[10],
        "tempo_segundos": int(
            linha[11]
            or 0
        ),
        "tempo_medio_questao": (
            float(
                linha[11]
                or 0
            )
            / int(
                linha[8]
                or 0
            )
            if int(
                linha[8]
                or 0
            ) > 0
            else None
        ),
        "dominio_antes": linha[12],
        "dominio_depois": linha[13],
        "delta_dominio": delta(
            linha[12],
            linha[13]
        ),
        "cobertura_antes": linha[14],
        "cobertura_depois": linha[15],
        "delta_cobertura": delta(
            linha[14],
            linha[15]
        ),
        "recorrentes_antes": int(
            linha[16]
            or 0
        ),
        "recorrentes_depois": int(
            linha[17]
            or 0
        ),
        "delta_recorrentes": (
            int(
                linha[16]
                or 0
            )
            - int(
                linha[17]
                or 0
            )
        ),
        "criticas_antes": int(
            linha[18]
            or 0
        ),
        "criticas_depois": int(
            linha[19]
            or 0
        ),
        "delta_criticas": (
            int(
                linha[18]
                or 0
            )
            - int(
                linha[19]
                or 0
            )
        ),
        "estrategia": estrategia,
        "topicos": dados_topicos,
    }


def obter_central_efetividade(
    concurso_id=None,
    dias=90,
    somente_adaptativas=True
):
    if concurso_id is None:
        concurso_id = (
            obter_concurso_ativo()[0]
        )

    concurso_id = int(
        concurso_id
    )

    parametros = [
        concurso_id,
    ]

    filtros = [
        "es.finalizado_em IS NOT NULL"
    ]

    if somente_adaptativas:
        filtros.append(
            "es.modo = 'Treino adaptativo'"
        )

    if dias is not None:
        dias = max(
            1,
            int(
                dias
            )
        )

        filtros.append(
            "date(es.criado_em) >= date('now', ?)"
        )
        parametros.append(
            f"-{dias} days"
        )

    with conectar() as conexao:
        ids_linhas = conexao.execute(
            f"""
            SELECT
                es.sessao_id
            FROM efetividade_sessoes es
            WHERE
                es.concurso_id = ?
                AND {' AND '.join(filtros)}
            ORDER BY
                es.criado_em DESC,
                es.sessao_id DESC
            """,
            parametros
        ).fetchall()

    sessoes = [
        obter_efetividade_sessao(
            linha[0]
        )
        for linha in ids_linhas
    ]

    sessoes = [
        item
        for item in sessoes
        if item is not None
    ]

    total_sessoes = len(
        sessoes
    )

    respostas = sum(
        item[
            "respostas"
        ]
        for item in sessoes
    )

    acertos = sum(
        item[
            "acertos"
        ]
        for item in sessoes
    )

    tempo_segundos = sum(
        item[
            "tempo_segundos"
        ]
        for item in sessoes
    )

    desempenho = (
        100.0
        * acertos
        / respostas
        if respostas > 0
        else None
    )

    todos_topicos = [
        topico
        for sessao in sessoes
        for topico in sessao[
            "topicos"
        ]
    ]

    delta_dominio = _media_ou_none([
        item[
            "delta_dominio"
        ]
        for item in todos_topicos
    ])

    delta_cobertura = _media_ou_none([
        item[
            "delta_cobertura"
        ]
        for item in todos_topicos
    ])

    delta_recorrentes = sum(
        item[
            "delta_recorrentes"
        ]
        for item in todos_topicos
    )

    delta_criticas = sum(
        item[
            "delta_criticas"
        ]
        for item in todos_topicos
    )

    tempo_medio = (
        tempo_segundos
        / respostas
        if respostas > 0
        else None
    )

    # --------------------------------------------------------
    # EFETIVIDADE POR MOTIVO DE SELEÇÃO
    # --------------------------------------------------------

    motivos = {}

    for sessao in sessoes:
        if sessao[
            "modo"
        ] != "Treino adaptativo":
            continue

        for topico in sessao[
            "topicos"
        ]:
            motivo = topico[
                "motivo_principal"
            ]

            info = motivos.setdefault(
                motivo,
                {
                    "motivo": motivo,
                    "sessoes_ids": set(),
                    "planejadas": 0,
                    "respostas": 0,
                    "acertos": 0,
                    "delta_dominio_lista": [],
                    "delta_cobertura_lista": [],
                    "delta_recorrentes": 0,
                    "delta_criticas": 0,
                }
            )

            info[
                "sessoes_ids"
            ].add(
                sessao[
                    "sessao_id"
                ]
            )
            info[
                "planejadas"
            ] += topico[
                "planejadas"
            ]
            info[
                "respostas"
            ] += topico[
                "respostas"
            ]
            info[
                "acertos"
            ] += topico[
                "acertos"
            ]

            if topico[
                "delta_dominio"
            ] is not None:
                info[
                    "delta_dominio_lista"
                ].append(
                    topico[
                        "delta_dominio"
                    ]
                )

            if topico[
                "delta_cobertura"
            ] is not None:
                info[
                    "delta_cobertura_lista"
                ].append(
                    topico[
                        "delta_cobertura"
                    ]
                )

            info[
                "delta_recorrentes"
            ] += topico[
                "delta_recorrentes"
            ]
            info[
                "delta_criticas"
            ] += topico[
                "delta_criticas"
            ]

    motivos_lista = []

    for motivo, info in motivos.items():
        respostas_motivo = info[
            "respostas"
        ]
        acertos_motivo = info[
            "acertos"
        ]

        motivos_lista.append({
            "motivo": motivo,
            "sessoes": len(
                info[
                    "sessoes_ids"
                ]
            ),
            "planejadas": info[
                "planejadas"
            ],
            "respostas": (
                respostas_motivo
            ),
            "acertos": acertos_motivo,
            "desempenho": (
                100.0
                * acertos_motivo
                / respostas_motivo
                if respostas_motivo > 0
                else None
            ),
            "delta_dominio": (
                _media_ou_none(
                    info[
                        "delta_dominio_lista"
                    ]
                )
            ),
            "delta_cobertura": (
                _media_ou_none(
                    info[
                        "delta_cobertura_lista"
                    ]
                )
            ),
            "delta_recorrentes": info[
                "delta_recorrentes"
            ],
            "delta_criticas": info[
                "delta_criticas"
            ],
        })

    motivos_lista.sort(
        key=lambda item: (
            -item[
                "respostas"
            ],
            item[
                "motivo"
            ].lower(),
        )
    )

    # --------------------------------------------------------
    # BASE DE CALIBRAÇÃO
    # --------------------------------------------------------

    adaptativas = [
        item
        for item in sessoes
        if item[
            "modo"
        ] == "Treino adaptativo"
    ]

    respostas_adaptativas = sum(
        item[
            "respostas"
        ]
        for item in adaptativas
    )

    quantidade_adaptativas = len(
        adaptativas
    )

    if (
        quantidade_adaptativas < 3
        or respostas_adaptativas < 50
    ):
        confianca = "Insuficiente"
        status = "Coletando base"
        orientacao = (
            "Mantenha os pesos atuais. Ainda há pouca evidência "
            "para avaliar a estratégia adaptativa."
        )

    elif (
        quantidade_adaptativas < 8
        or respostas_adaptativas < 150
    ):
        confianca = "Inicial"
        status = "Base inicial"
        orientacao = (
            "Já existem sinais úteis, mas ainda não é recomendável "
            "alterar automaticamente os pesos."
        )

    elif (
        quantidade_adaptativas < 20
        or respostas_adaptativas < 500
    ):
        confianca = "Moderada"
        status = "Base moderada"
        orientacao = (
            "A amostra já permite comparar motivos de seleção com "
            "mais segurança; alterações ainda devem ser manuais e graduais."
        )

    else:
        confianca = "Forte"
        status = "Base robusta"
        orientacao = (
            "Há volume suficiente para uma futura rotina assistida de "
            "calibração, mantendo confirmação explícita do usuário."
        )

    observacoes = []

    for item in motivos_lista:
        if (
            item[
                "respostas"
            ] < 20
        ):
            continue

        desempenho_motivo = item[
            "desempenho"
        ]
        delta_dom = item[
            "delta_dominio"
        ]
        delta_cob = item[
            "delta_cobertura"
        ]

        if (
            desempenho_motivo is not None
            and desempenho_motivo < 60.0
        ):
            observacoes.append(
                (
                    f"{item['motivo']}: desempenho de "
                    f"{desempenho_motivo:.0f}% indica dificuldade real "
                    "nas questões selecionadas."
                )
            )

        elif (
            delta_dom is not None
            and delta_dom >= 4.0
        ):
            observacoes.append(
                (
                    f"{item['motivo']}: ganho médio de domínio de "
                    f"{delta_dom:+.1f} ponto(s) por tópico."
                )
            )

        elif (
            delta_cob is not None
            and delta_cob >= 10.0
        ):
            observacoes.append(
                (
                    f"{item['motivo']}: ampliou a cobertura em média "
                    f"{delta_cob:+.1f} p.p. por tópico."
                )
            )

    if not observacoes:
        observacoes.append(
            (
                "A central ainda está acumulando sessões para identificar "
                "padrões confiáveis por motivo de seleção."
            )
        )

    return {
        "periodo_dias": dias,
        "somente_adaptativas": bool(
            somente_adaptativas
        ),
        "sessoes": sessoes,
        "motivos": motivos_lista,
        "resumo": {
            "sessoes": total_sessoes,
            "respostas": respostas,
            "acertos": acertos,
            "desempenho": desempenho,
            "delta_dominio": (
                delta_dominio
            ),
            "delta_cobertura": (
                delta_cobertura
            ),
            "delta_recorrentes": (
                delta_recorrentes
            ),
            "delta_criticas": (
                delta_criticas
            ),
            "tempo_segundos": (
                tempo_segundos
            ),
            "tempo_medio_questao": (
                tempo_medio
            ),
        },
        "calibracao": {
            "status": status,
            "confianca": confianca,
            "sessoes_adaptativas": (
                quantidade_adaptativas
            ),
            "respostas_adaptativas": (
                respostas_adaptativas
            ),
            "orientacao": orientacao,
            "observacoes": observacoes[
                :5
            ],
            "versao_selecao": "adaptativa_v2",
            "pesos_atuais": {
                "Domínio frágil": 20,
                "Erros/recuperação": 18,
                "Evidência": 15,
                "Variedade": 12,
                "Estabilidade": 10,
                "Recência": 8,
                "Urgência": 10,
                "Importância": 7,
            },
        },
    }


def iniciar_sessao_questoes(
    concurso_id,
    modo,
    objetivo
):
    concurso_id = int(
        concurso_id
    )
    objetivo = max(
        1,
        int(
            objetivo
        )
    )

    with conectar() as conexao:
        concurso = conexao.execute(
            """
            SELECT 1
            FROM concursos
            WHERE id = ?
            """,
            (
                concurso_id,
            )
        ).fetchone()

        if concurso is None:
            raise ValueError(
                "O perfil informado não existe."
            )

        cursor = conexao.execute(
            """
            INSERT INTO sessoes_questoes (
                concurso_id,
                iniciado_em,
                modo,
                objetivo,
                concluida
            )
            VALUES (
                ?,
                datetime(
                    'now',
                    'localtime'
                ),
                ?,
                ?,
                0
            )
            """,
            (
                concurso_id,
                str(
                    modo
                    or "Aleatórias"
                ),
                objetivo,
            )
        )

        return cursor.lastrowid


def registrar_tentativa_questao(
    sessao_id,
    questao_id,
    concurso_id,
    alternativa_marcada=None,
    marcada_duvida=False,
    tempo_segundos=None
):
    sessao_id = int(
        sessao_id
    )
    questao_id = int(
        questao_id
    )
    concurso_id = int(
        concurso_id
    )

    alternativa = (
        str(
            alternativa_marcada
        ).strip().upper()
        if alternativa_marcada
        else None
    )

    with conectar() as conexao:
        sessao = conexao.execute(
            """
            SELECT
                concurso_id,
                encerrado_em
            FROM sessoes_questoes
            WHERE id = ?
            """,
            (
                sessao_id,
            )
        ).fetchone()

        if sessao is None:
            raise ValueError(
                "A sessão de questões não existe."
            )

        if sessao[1] is not None:
            raise ValueError(
                "A sessão de questões já foi encerrada."
            )

        if (
            sessao[0] is not None
            and int(
                sessao[0]
            ) != concurso_id
        ):
            raise ValueError(
                "A sessão pertence a outro perfil."
            )

        questao = conexao.execute(
            """
            SELECT
                q.id,
                q.topico_id,
                d.id AS disciplina_id,
                d.nome AS disciplina,
                t.nome AS topico,
                q.enunciado,
                q.explicacao,
                q.banca,
                q.ano,
                q.fonte,
                q.dificuldade,
                q.ativa
            FROM questoes q
            JOIN topicos t
                ON t.id = q.topico_id
            JOIN disciplinas d
                ON d.id = t.disciplina_id
            WHERE q.id = ?
            """,
            (
                questao_id,
            )
        ).fetchone()

        if questao is None:
            raise ValueError(
                "A questão não existe."
            )

        if not bool(
            questao[11]
        ):
            raise ValueError(
                "A questão está arquivada e não pode receber novas tentativas."
            )

        alternativas_linhas = conexao.execute(
            """
            SELECT
                letra,
                texto,
                correta,
                ordem
            FROM alternativas_questoes
            WHERE questao_id = ?
            ORDER BY ordem, letra
            """,
            (
                questao_id,
            )
        ).fetchall()

        alternativas_snapshot = [
            {
                "letra": str(
                    item[0]
                ).strip().upper(),
                "texto": item[1],
                "correta": bool(
                    item[2]
                ),
                "ordem": int(
                    item[3]
                ),
            }
            for item in alternativas_linhas
        ]

        gabarito = next(
            (
                item[
                    "letra"
                ]
                for item in alternativas_snapshot
                if item[
                    "correta"
                ]
            ),
            None
        )

        if not gabarito:
            raise ValueError(
                "A questão não possui gabarito válido."
            )

        letras_existentes = {
            item[
                "letra"
            ]
            for item in alternativas_snapshot
        }

        if alternativa is None:
            resultado = None
        else:
            if alternativa not in letras_existentes:
                raise ValueError(
                    "A alternativa marcada não existe nesta questão."
                )

            resultado = (
                1
                if alternativa == gabarito
                else 0
            )

        if tempo_segundos is None:
            tempo_segundos = None
        else:
            tempo_segundos = max(
                0,
                int(
                    tempo_segundos
                )
            )

        cursor = conexao.execute(
            """
            INSERT INTO tentativas_questoes (
                sessao_id,
                questao_id,
                concurso_id,
                respondida_em,
                alternativa_marcada,
                correta,
                marcada_duvida,
                tempo_segundos,
                questao_id_snapshot,
                topico_id_snapshot,
                disciplina_id_snapshot,
                disciplina_snapshot,
                topico_snapshot,
                enunciado_snapshot,
                alternativas_snapshot,
                gabarito_snapshot,
                explicacao_snapshot,
                banca_snapshot,
                ano_snapshot,
                fonte_snapshot,
                dificuldade_snapshot,
                snapshot_origem
            )
            VALUES (
                ?,
                ?,
                ?,
                datetime(
                    'now',
                    'localtime'
                ),
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                'resposta'
            )
            """,
            (
                sessao_id,
                questao_id,
                concurso_id,
                alternativa,
                resultado,
                1 if marcada_duvida else 0,
                tempo_segundos,
                questao[0],
                questao[1],
                questao[2],
                questao[3],
                questao[4],
                questao[5],
                json.dumps(
                    alternativas_snapshot,
                    ensure_ascii=False
                ),
                gabarito,
                questao[6] or "",
                questao[7] or "",
                questao[8],
                questao[9] or "",
                questao[10]
                or "Não informada",
            )
        )

        return {
            "tentativa_id": cursor.lastrowid,
            "gabarito": gabarito,
            "alternativa_marcada": alternativa,
            "correta": (
                None
                if resultado is None
                else bool(
                    resultado
                )
            ),
            "pulada": (
                resultado is None
            ),
        }


def encerrar_sessao_questoes(
    sessao_id,
    concluida=True
):
    with conectar() as conexao:
        cursor = conexao.execute(
            """
            UPDATE sessoes_questoes
            SET
                encerrado_em = datetime(
                    'now',
                    'localtime'
                ),
                concluida = ?
            WHERE
                id = ?
                AND encerrado_em IS NULL
            """,
            (
                1 if concluida else 0,
                int(
                    sessao_id
                ),
            )
        )

        return (
            cursor.rowcount > 0
        )


def obter_resumo_sessao_questoes(
    sessao_id
):
    sessao_id = int(
        sessao_id
    )

    with conectar() as conexao:
        sessao = conexao.execute(
            """
            SELECT
                sq.id,
                sq.concurso_id,
                c.nome,
                sq.iniciado_em,
                sq.encerrado_em,
                sq.modo,
                sq.objetivo,
                sq.concluida
            FROM sessoes_questoes sq
            LEFT JOIN concursos c
                ON c.id = sq.concurso_id
            WHERE sq.id = ?
            """,
            (
                sessao_id,
            )
        ).fetchone()

        if sessao is None:
            return None

        resumo = conexao.execute(
            """
            SELECT
                COUNT(*) AS processadas,
                SUM(
                    CASE
                        WHEN correta IS NOT NULL
                        THEN 1
                        ELSE 0
                    END
                ) AS respondidas,
                SUM(
                    CASE
                        WHEN correta = 1
                        THEN 1
                        ELSE 0
                    END
                ) AS acertos,
                SUM(
                    CASE
                        WHEN correta = 0
                        THEN 1
                        ELSE 0
                    END
                ) AS erros,
                SUM(
                    CASE
                        WHEN correta IS NULL
                        THEN 1
                        ELSE 0
                    END
                ) AS puladas,
                SUM(
                    CASE
                        WHEN marcada_duvida = 1
                        THEN 1
                        ELSE 0
                    END
                ) AS duvidas
            FROM tentativas_questoes
            WHERE sessao_id = ?
            """,
            (
                sessao_id,
            )
        ).fetchone()

    respondidas = int(
        resumo[1] or 0
    )
    acertos = int(
        resumo[2] or 0
    )

    desempenho = (
        100.0
        * acertos
        / respondidas
        if respondidas > 0
        else None
    )

    return {
        "sessao_id": sessao[0],
        "concurso_id": sessao[1],
        "concurso": sessao[2] or "—",
        "iniciado_em": sessao[3],
        "encerrado_em": sessao[4],
        "modo": sessao[5] or "",
        "objetivo": int(
            sessao[6] or 0
        ),
        "concluida": bool(
            sessao[7]
        ),
        "processadas": int(
            resumo[0] or 0
        ),
        "respondidas": respondidas,
        "acertos": acertos,
        "erros": int(
            resumo[3] or 0
        ),
        "puladas": int(
            resumo[4] or 0
        ),
        "duvidas": int(
            resumo[5] or 0
        ),
        "desempenho": desempenho,
    }




def obter_contextos_revisao_automatica_sessao(
    sessao_id
):
    """
    Identifica todos os pares tópico/data tocados pela sessão e retorna
    a consolidação diária real de respostas daquele tópico.

    A consolidação considera todas as respostas internas do mesmo tópico
    naquele dia, inclusive as de outras sessões. Questões puladas não
    entram no total de questões/acertos.
    """

    sessao_id = int(
        sessao_id
    )

    with conectar() as conexao:
        pares = conexao.execute(
            """
            SELECT DISTINCT
                COALESCE(
                    tq.topico_id_snapshot,
                    q.topico_id
                ) AS topico_id_resposta,
                SUBSTR(
                    tq.respondida_em,
                    1,
                    10
                ) AS data_resposta
            FROM tentativas_questoes tq
            LEFT JOIN questoes q
                ON q.id = tq.questao_id
            WHERE
                tq.sessao_id = ?
                AND tq.correta IS NOT NULL
                AND COALESCE(
                    tq.topico_id_snapshot,
                    q.topico_id
                ) IS NOT NULL
            ORDER BY
                data_resposta,
                topico_id_resposta
            """,
            (
                sessao_id,
            )
        ).fetchall()

        resultado = []

        for topico_id, data_resposta in pares:
            topico = conexao.execute(
                """
                SELECT
                    t.nome,
                    d.nome
                FROM topicos t
                JOIN disciplinas d
                    ON d.id = t.disciplina_id
                WHERE t.id = ?
                """,
                (
                    topico_id,
                )
            ).fetchone()

            consolidado = conexao.execute(
                """
                SELECT
                    COUNT(*),
                    COALESCE(
                        SUM(tq.correta),
                        0
                    )
                FROM tentativas_questoes tq
                LEFT JOIN questoes q
                    ON q.id = tq.questao_id
                WHERE
                    COALESCE(
                        tq.topico_id_snapshot,
                        q.topico_id
                    ) = ?
                    AND tq.correta IS NOT NULL
                    AND SUBSTR(
                        tq.respondida_em,
                        1,
                        10
                    ) = ?
                """,
                (
                    topico_id,
                    data_resposta,
                )
            ).fetchone()

            revisao_existente = conexao.execute(
                """
                SELECT id
                FROM revisoes
                WHERE
                    topico_id = ?
                    AND data = ?
                    AND COALESCE(
                        origem,
                        'manual'
                    ) = 'questoes_internas'
                ORDER BY id
                LIMIT 1
                """,
                (
                    topico_id,
                    data_resposta,
                )
            ).fetchone()

            controle = conexao.execute(
                """
                SELECT
                    COALESCE(
                        revisoes_iniciais,
                        0
                    ),
                    percentual_inicial
                FROM controle_topico
                WHERE topico_id = ?
                """,
                (
                    topico_id,
                )
            ).fetchone()

            if controle is None:
                revisoes_iniciais = 0
                percentual_inicial = None
            else:
                revisoes_iniciais = int(
                    controle[0]
                    or 0
                )
                percentual_inicial = controle[1]

            anterior = conexao.execute(
                """
                SELECT
                    ROUND(
                        100.0 * acertos / questoes,
                        1
                    )
                FROM revisoes
                WHERE
                    topico_id = ?
                    AND data < ?
                ORDER BY
                    data DESC,
                    id DESC
                LIMIT 1
                """,
                (
                    topico_id,
                    data_resposta,
                )
            ).fetchone()

            if anterior is None:
                percentual_anterior = (
                    percentual_inicial
                )
            else:
                percentual_anterior = anterior[0]

            revisoes_anteriores_programa = conexao.execute(
                """
                SELECT COUNT(*)
                FROM revisoes
                WHERE
                    topico_id = ?
                    AND data < ?
                """,
                (
                    topico_id,
                    data_resposta,
                )
            ).fetchone()[0]

            total_revisoes_anteriores = (
                revisoes_iniciais
                + int(
                    revisoes_anteriores_programa
                    or 0
                )
            )

            # "Primeiro contato" significa que, antes do dia atual,
            # o tópico nunca teve revisão nem histórico importado.
            # Se houver várias sessões no mesmo dia, todas continuam
            # compondo esse primeiro contato e atualizam a mesma revisão.
            primeiro_contato = (
                total_revisoes_anteriores == 0
            )

            numero_revisao = (
                total_revisoes_anteriores
                + 1
            )

            questoes = int(
                consolidado[0]
                or 0
            )
            acertos = int(
                consolidado[1]
                or 0
            )

            percentual = (
                100.0
                * acertos
                / questoes
                if questoes > 0
                else None
            )

            resultado.append({
                "topico_id": int(
                    topico_id
                ),
                "topico": (
                    topico[0]
                    if topico
                    else "—"
                ),
                "disciplina": (
                    topico[1]
                    if topico
                    else "—"
                ),
                "data": data_resposta,
                "questoes": questoes,
                "acertos": acertos,
                "percentual": percentual,
                "revisao_id": (
                    revisao_existente[0]
                    if revisao_existente
                    else None
                ),
                "numero_revisao": int(
                    numero_revisao
                ),
                "percentual_anterior": (
                    percentual_anterior
                ),
                "revisoes_anteriores": int(
                    total_revisoes_anteriores
                ),
                "primeiro_contato": bool(
                    primeiro_contato
                ),
            })

    return resultado


def salvar_revisao_automatica_questoes(
    topico_id, data, questoes, acertos, confianca,
    proxima_revisao=None, sessao_questoes_id=None
):
    """Consolida revisão interna diária e preserva o prazo histórico original."""
    topico_id = int(topico_id)
    questoes = int(questoes)
    acertos = int(acertos)
    with conectar() as conexao:
        existente = conexao.execute(
            """SELECT id, prevista_para, realizada_em, dias_atraso,
                      COALESCE(prazo_historico_valido, 0)
               FROM revisoes
               WHERE topico_id = ? AND data = ?
                 AND COALESCE(origem, 'manual') = 'questoes_internas'
               ORDER BY id LIMIT 1""",
            (topico_id, data),
        ).fetchone()
        observacao = (
            "Revisão consolidada automaticamente a partir das questões "
            "respondidas no VighnaStudy."
        )
        prazo = None
        if existente is None:
            controle = conexao.execute(
                "SELECT proxima_revisao FROM controle_topico WHERE topico_id = ?",
                (topico_id,),
            ).fetchone()
            prazo = _metadados_prazo_revisao(controle[0] if controle else None, data)
            cursor = conexao.execute(
                """INSERT INTO revisoes (
                       topico_id, data, questoes, acertos, observacao, texto_erros,
                       continuacao, origem, confianca, sessao_questoes_id,
                       prevista_para, realizada_em, dias_atraso, prazo_historico_valido
                   ) VALUES (?, ?, ?, ?, ?, '', '', 'questoes_internas', ?, ?, ?, ?, ?, ?)""",
                (topico_id, data, questoes, acertos, observacao, confianca,
                 sessao_questoes_id, prazo["prevista_para"], prazo["realizada_em"],
                 prazo["dias_atraso"], prazo["prazo_historico_valido"]),
            )
            revisao_id = cursor.lastrowid
            criada = True
        else:
            revisao_id = existente[0]
            criada = False
            conexao.execute(
                """UPDATE revisoes SET questoes = ?, acertos = ?, observacao = ?,
                       origem = 'questoes_internas', confianca = ?, sessao_questoes_id = ?
                   WHERE id = ?""",
                (questoes, acertos, observacao, confianca, sessao_questoes_id, revisao_id),
            )
            prazo = {
                "prevista_para": existente[1], "realizada_em": existente[2],
                "dias_atraso": existente[3], "prazo_historico_valido": int(existente[4] or 0),
            }

        conexao.execute(
            """UPDATE tentativas_questoes SET revisao_id = ?
               WHERE id IN (
                 SELECT tq.id FROM tentativas_questoes tq
                 LEFT JOIN questoes q ON q.id = tq.questao_id
                 WHERE COALESCE(tq.topico_id_snapshot, q.topico_id) = ?
                   AND tq.correta IS NOT NULL
                   AND SUBSTR(tq.respondida_em, 1, 10) = ?
               )""",
            (revisao_id, topico_id, data),
        )
        conexao.execute(
            "INSERT OR IGNORE INTO controle_topico (topico_id) VALUES (?)",
            (topico_id,),
        )
        if proxima_revisao is not None:
            conexao.execute(
                "UPDATE controle_topico SET proxima_revisao = ? WHERE topico_id = ?",
                (proxima_revisao, topico_id),
            )
    return {"revisao_id": int(revisao_id), "criada": criada, **prazo}


def listar_tentativas_revisao_automatica(
    revisao_id
):
    with conectar() as conexao:
        linhas = conexao.execute(
            """
            SELECT
                COALESCE(
                    tq.questao_id_snapshot,
                    tq.questao_id
                ) AS questao_ref,
                COALESCE(
                    tq.enunciado_snapshot,
                    q.enunciado,
                    '[Conteúdo histórico indisponível]'
                ) AS enunciado,
                tq.respondida_em,
                tq.alternativa_marcada,
                COALESCE(
                    tq.gabarito_snapshot,
                    (
                        SELECT aq.letra
                        FROM alternativas_questoes aq
                        WHERE
                            aq.questao_id = tq.questao_id
                            AND aq.correta = 1
                        ORDER BY aq.ordem
                        LIMIT 1
                    )
                ) AS gabarito,
                tq.correta,
                tq.marcada_duvida,
                tq.tempo_segundos,
                tq.id
            FROM tentativas_questoes tq
            LEFT JOIN questoes q
                ON q.id = tq.questao_id
            WHERE tq.revisao_id = ?
            ORDER BY
                tq.respondida_em,
                tq.id
            """,
            (
                int(
                    revisao_id
                ),
            )
        ).fetchall()

    resultado = []

    for linha in linhas:
        if linha[5] is None:
            status = "Pulada"
        elif int(
            linha[5]
        ) == 1:
            status = "Correta"
        else:
            status = "Errada"

        resultado.append({
            "questao_id": linha[0],
            "enunciado": linha[1],
            "respondida_em": linha[2],
            "marcada": linha[3] or "",
            "gabarito": linha[4] or "",
            "status": status,
            "duvida": bool(
                linha[6]
            ),
            "tempo_segundos": linha[7],
            "tentativa_id": linha[8],
        })

    return resultado


def obter_tentativa_questao_snapshot(
    tentativa_id
):
    tentativa_id = int(
        tentativa_id
    )

    with conectar() as conexao:
        linha = conexao.execute(
            """
            SELECT
                tq.id,
                tq.respondida_em,
                tq.alternativa_marcada,
                tq.correta,
                tq.marcada_duvida,
                tq.tempo_segundos,
                tq.snapshot_origem,
                COALESCE(
                    tq.questao_id_snapshot,
                    tq.questao_id
                ) AS questao_ref,
                COALESCE(
                    tq.topico_id_snapshot,
                    q.topico_id
                ) AS topico_id_ref,
                COALESCE(
                    tq.disciplina_id_snapshot,
                    d.id
                ) AS disciplina_id_ref,
                COALESCE(
                    d.nome,
                    tq.disciplina_snapshot,
                    '—'
                ) AS disciplina,
                COALESCE(
                    tq.topico_snapshot,
                    t.nome,
                    '—'
                ) AS topico,
                COALESCE(
                    tq.enunciado_snapshot,
                    q.enunciado,
                    '[Conteúdo histórico indisponível]'
                ) AS enunciado,
                tq.alternativas_snapshot,
                tq.gabarito_snapshot,
                COALESCE(
                    tq.explicacao_snapshot,
                    q.explicacao,
                    ''
                ) AS explicacao,
                COALESCE(
                    tq.banca_snapshot,
                    q.banca,
                    ''
                ) AS banca,
                COALESCE(
                    tq.ano_snapshot,
                    q.ano
                ) AS ano,
                COALESCE(
                    tq.fonte_snapshot,
                    q.fonte,
                    ''
                ) AS fonte,
                COALESCE(
                    tq.dificuldade_snapshot,
                    q.dificuldade,
                    'Não informada'
                ) AS dificuldade,
                CASE
                    WHEN q.id IS NULL
                    THEN 0
                    ELSE q.ativa
                END AS ativa_atual
            FROM tentativas_questoes tq
            LEFT JOIN questoes q
                ON q.id = tq.questao_id
            LEFT JOIN topicos t
                ON t.id = q.topico_id
            LEFT JOIN disciplinas d
                ON d.id = t.disciplina_id
            WHERE tq.id = ?
            """,
            (
                tentativa_id,
            )
        ).fetchone()

        if linha is None:
            return None

        alternativas = []

        if linha[13]:
            try:
                alternativas = json.loads(
                    linha[13]
                )
            except Exception:
                alternativas = []

        if not alternativas and linha[7] is not None:
            atuais = conexao.execute(
                """
                SELECT
                    letra,
                    texto,
                    correta,
                    ordem
                FROM alternativas_questoes
                WHERE questao_id = ?
                ORDER BY ordem, letra
                """,
                (
                    int(
                        linha[7]
                    ),
                )
            ).fetchall()

            alternativas = [
                {
                    "letra": item[0],
                    "texto": item[1],
                    "correta": bool(
                        item[2]
                    ),
                    "ordem": item[3],
                }
                for item in atuais
            ]

    gabarito = (
        linha[14]
        or next(
            (
                item.get(
                    "letra"
                )
                for item in alternativas
                if item.get(
                    "correta"
                )
            ),
            ""
        )
        or ""
    )

    # Normaliza a marcação de correta de acordo com o gabarito congelado.
    alternativas_normalizadas = []

    for ordem, alternativa in enumerate(
        alternativas,
        start=1
    ):
        letra = str(
            alternativa.get(
                "letra",
                ""
            )
        ).strip().upper()

        alternativas_normalizadas.append({
            "letra": letra,
            "texto": str(
                alternativa.get(
                    "texto",
                    ""
                )
            ),
            "correta": (
                letra == gabarito
            ),
            "ordem": int(
                alternativa.get(
                    "ordem",
                    ordem
                )
                or ordem
            ),
        })

    origem = (
        linha[6]
        or ""
    )

    return {
        "id": linha[7],
        "questao_id": linha[7],
        "tentativa_id": linha[0],
        "respondida_em": linha[1],
        "alternativa_marcada": (
            linha[2]
            or ""
        ),
        "resultado_correto": (
            None
            if linha[3] is None
            else bool(
                linha[3]
            )
        ),
        "duvida": bool(
            linha[4]
        ),
        "tempo_segundos": linha[5],
        "snapshot_origem": origem,
        "snapshot_preservado": (
            origem == "resposta"
        ),
        "snapshot_legado": (
            origem == "migrado"
        ),
        "topico_id": linha[8],
        "disciplina_id": linha[9],
        "disciplina": linha[10],
        "topico": linha[11],
        "enunciado": linha[12],
        "alternativas": alternativas_normalizadas,
        "gabarito": gabarito,
        "explicacao": linha[15] or "",
        "banca": linha[16] or "",
        "ano": linha[17],
        "fonte": linha[18] or "",
        "dificuldade": (
            linha[19]
            or "Não informada"
        ),
        "ativa": bool(
            linha[20]
        ),
        "historico": True,
    }


def listar_historico_tentativas_questoes(
    concurso_id=None
):
    """
    Histórico individual baseado na versão da questão existente no
    momento da resposta. Tentativas antigas migradas são identificadas
    como snapshot legado.
    """

    if concurso_id is None:
        concurso_id = (
            obter_concurso_ativo()[0]
        )

    concurso_id = int(
        concurso_id
    )

    with conectar() as conexao:
        linhas = conexao.execute(
            """
            SELECT
                tq.id,
                tq.sessao_id,
                COALESCE(
                    tq.questao_id_snapshot,
                    tq.questao_id
                ) AS questao_ref,
                tq.respondida_em,
                COALESCE(
                    tq.disciplina_id_snapshot,
                    d.id
                ) AS disciplina_id_ref,
                COALESCE(
                    tq.disciplina_snapshot,
                    d.nome,
                    '—'
                ) AS disciplina,
                COALESCE(
                    tq.topico_id_snapshot,
                    q.topico_id
                ) AS topico_id_ref,
                COALESCE(
                    tq.topico_snapshot,
                    t.nome,
                    '—'
                ) AS topico,
                COALESCE(
                    tq.enunciado_snapshot,
                    q.enunciado,
                    '[Conteúdo histórico indisponível]'
                ) AS enunciado,
                COALESCE(
                    tq.banca_snapshot,
                    q.banca,
                    ''
                ) AS banca,
                COALESCE(
                    tq.ano_snapshot,
                    q.ano
                ) AS ano,
                COALESCE(
                    tq.dificuldade_snapshot,
                    q.dificuldade,
                    'Não informada'
                ) AS dificuldade,
                tq.alternativa_marcada,
                COALESCE(
                    tq.gabarito_snapshot,
                    (
                        SELECT aq.letra
                        FROM alternativas_questoes aq
                        WHERE
                            aq.questao_id = tq.questao_id
                            AND aq.correta = 1
                        ORDER BY aq.ordem
                        LIMIT 1
                    )
                ) AS gabarito,
                tq.correta,
                tq.marcada_duvida,
                tq.tempo_segundos,
                sq.modo,
                COALESCE(
                    tq.snapshot_origem,
                    ''
                ) AS snapshot_origem,
                CASE
                    WHEN q.id IS NULL
                    THEN 0
                    ELSE q.ativa
                END AS ativa_atual
            FROM tentativas_questoes tq
            LEFT JOIN questoes q
                ON q.id = tq.questao_id
            LEFT JOIN topicos t
                ON t.id = q.topico_id
            LEFT JOIN disciplinas d
                ON d.id = t.disciplina_id
            LEFT JOIN sessoes_questoes sq
                ON sq.id = tq.sessao_id
            WHERE tq.concurso_id = ?
            ORDER BY
                tq.respondida_em DESC,
                tq.id DESC
            """,
            (
                concurso_id,
            )
        ).fetchall()

    resultado = []

    for linha in linhas:
        if linha[14] is None:
            status = "Pulada"
        elif int(
            linha[14]
        ) == 1:
            status = "Correta"
        else:
            status = "Errada"

        resultado.append({
            "tentativa_id": linha[0],
            "sessao_id": linha[1],
            "questao_id": linha[2],
            "respondida_em": linha[3],
            "disciplina_id": linha[4],
            "disciplina": linha[5],
            "topico_id": linha[6],
            "topico": linha[7],
            "enunciado": linha[8],
            "banca": linha[9] or "",
            "ano": linha[10],
            "dificuldade": (
                linha[11]
                or "Não informada"
            ),
            "alternativa_marcada": (
                linha[12]
                or ""
            ),
            "gabarito": (
                linha[13]
                or ""
            ),
            "correta": (
                None
                if linha[14] is None
                else bool(
                    linha[14]
                )
            ),
            "status": status,
            "duvida": bool(
                linha[15]
            ),
            "tempo_segundos": linha[16],
            "modo": linha[17] or "",
            "snapshot_origem": (
                linha[18]
                or ""
            ),
            "snapshot_preservado": (
                linha[18] == "resposta"
            ),
            "snapshot_legado": (
                linha[18] == "migrado"
            ),
            "ativa": bool(
                linha[19]
            ),
        })

    return resultado


def listar_caderno_erros_questoes(
    concurso_id=None
):
    """
    Consolida erros por ID original da questão.
    Questões arquivadas permanecem no caderno, mas não podem ser
    respondidas novamente até serem reativadas.
    """

    if concurso_id is None:
        concurso_id = (
            obter_concurso_ativo()[0]
        )

    concurso_id = int(
        concurso_id
    )

    with conectar() as conexao:
        referencias = conexao.execute(
            """
            SELECT DISTINCT
                COALESCE(
                    questao_id_snapshot,
                    questao_id
                )
            FROM tentativas_questoes
            WHERE
                concurso_id = ?
                AND correta = 0
                AND COALESCE(
                    questao_id_snapshot,
                    questao_id
                ) IS NOT NULL
            """,
            (
                concurso_id,
            )
        ).fetchall()

        resultado = []

        for referencia_linha in referencias:
            questao_id = int(
                referencia_linha[0]
            )

            atual = conexao.execute(
                """
                SELECT
                    q.id,
                    q.topico_id,
                    d.id,
                    d.nome,
                    t.nome,
                    q.enunciado,
                    q.banca,
                    q.ano,
                    q.dificuldade,
                    q.ativa
                FROM questoes q
                JOIN topicos t
                    ON t.id = q.topico_id
                JOIN disciplinas d
                    ON d.id = t.disciplina_id
                WHERE q.id = ?
                """,
                (
                    questao_id,
                )
            ).fetchone()

            if atual is not None:
                dados_questao = {
                    "questao_id": atual[0],
                    "topico_id": atual[1],
                    "disciplina_id": atual[2],
                    "disciplina": atual[3],
                    "topico": atual[4],
                    "enunciado": atual[5],
                    "banca": atual[6] or "",
                    "ano": atual[7],
                    "dificuldade": (
                        atual[8]
                        or "Não informada"
                    ),
                    "ativa": bool(
                        atual[9]
                    ),
                }
            else:
                snapshot = conexao.execute(
                    """
                    SELECT
                        COALESCE(
                            topico_id_snapshot,
                            0
                        ),
                        COALESCE(
                            disciplina_id_snapshot,
                            0
                        ),
                        COALESCE(
                            disciplina_snapshot,
                            '—'
                        ),
                        COALESCE(
                            topico_snapshot,
                            '—'
                        ),
                        COALESCE(
                            enunciado_snapshot,
                            '[Conteúdo histórico indisponível]'
                        ),
                        COALESCE(
                            banca_snapshot,
                            ''
                        ),
                        ano_snapshot,
                        COALESCE(
                            dificuldade_snapshot,
                            'Não informada'
                        )
                    FROM tentativas_questoes
                    WHERE
                        concurso_id = ?
                        AND COALESCE(
                            questao_id_snapshot,
                            questao_id
                        ) = ?
                    ORDER BY
                        respondida_em DESC,
                        id DESC
                    LIMIT 1
                    """,
                    (
                        concurso_id,
                        questao_id,
                    )
                ).fetchone()

                if snapshot is None:
                    continue

                dados_questao = {
                    "questao_id": questao_id,
                    "topico_id": snapshot[0],
                    "disciplina_id": snapshot[1],
                    "disciplina": snapshot[2],
                    "topico": snapshot[3],
                    "enunciado": snapshot[4],
                    "banca": snapshot[5] or "",
                    "ano": snapshot[6],
                    "dificuldade": (
                        snapshot[7]
                        or "Não informada"
                    ),
                    "ativa": False,
                }

            tentativas = conexao.execute(
                """
                SELECT
                    respondida_em,
                    correta,
                    marcada_duvida,
                    alternativa_marcada
                FROM tentativas_questoes
                WHERE
                    concurso_id = ?
                    AND COALESCE(
                        questao_id_snapshot,
                        questao_id
                    ) = ?
                ORDER BY
                    respondida_em DESC,
                    id DESC
                """,
                (
                    concurso_id,
                    questao_id,
                )
            ).fetchall()

            efetivas = [
                item
                for item in tentativas
                if item[1] is not None
            ]

            total = len(
                efetivas
            )
            acertos = sum(
                1
                for item in efetivas
                if int(
                    item[1]
                ) == 1
            )
            erros = sum(
                1
                for item in efetivas
                if int(
                    item[1]
                ) == 0
            )

            if erros <= 0:
                continue

            taxa = (
                100.0
                * acertos
                / total
                if total > 0
                else 0.0
            )

            erros_consecutivos = 0

            for item in efetivas:
                if int(
                    item[1]
                ) == 0:
                    erros_consecutivos += 1
                else:
                    break

            acertos_consecutivos = 0

            for item in efetivas:
                if int(
                    item[1]
                ) == 1:
                    acertos_consecutivos += 1
                else:
                    break

            duvida = any(
                bool(
                    item[2]
                )
                for item in tentativas
            )

            ultima_tentativa = (
                tentativas[0][0]
                if tentativas
                else None
            )

            ultimo_resultado = (
                (
                    "Pulada"
                    if tentativas[0][1] is None
                    else (
                        "Correta"
                        if int(
                            tentativas[0][1]
                        ) == 1
                        else "Errada"
                    )
                )
                if tentativas
                else "—"
            )

            if (
                erros_consecutivos >= 3
                or (
                    erros >= 3
                    and taxa < 50.0
                )
            ):
                status = "Crítica"
                ordem_status = 0

            elif acertos_consecutivos >= 3:
                status = "Recuperada"
                ordem_status = 3

            elif (
                erros_consecutivos >= 2
                or (
                    erros >= 2
                    and taxa < 70.0
                )
            ):
                status = "Recorrente"
                ordem_status = 1

            else:
                status = "Erro isolado"
                ordem_status = 2

            resultado.append({
                **dados_questao,
                "tentativas": total,
                "acertos": acertos,
                "erros": erros,
                "taxa_acerto": taxa,
                "erros_consecutivos": (
                    erros_consecutivos
                ),
                "acertos_consecutivos": (
                    acertos_consecutivos
                ),
                "duvida": duvida,
                "ultima_tentativa": (
                    ultima_tentativa
                ),
                "ultimo_resultado": (
                    ultimo_resultado
                ),
                "status": status,
                "ordem_status": (
                    ordem_status
                ),
                "inedita": False,
                "tentativas_anteriores": total,
            })

    resultado.sort(
        key=lambda item: (
            item[
                "ordem_status"
            ],
            0 if item[
                "ativa"
            ] else 1,
            -item[
                "erros_consecutivos"
            ],
            item[
                "taxa_acerto"
            ],
            -item[
                "erros"
            ],
            item[
                "disciplina"
            ].lower(),
            item[
                "topico"
            ].lower(),
            item[
                "questao_id"
            ],
        )
    )

    return resultado


def obter_estatisticas_historico_questoes(
    concurso_id=None
):
    historico = listar_historico_tentativas_questoes(
        concurso_id
    )

    respondidas = [
        item
        for item in historico
        if item[
            "status"
        ] in (
            "Correta",
            "Errada"
        )
    ]

    acertos = sum(
        1
        for item in respondidas
        if item[
            "status"
        ] == "Correta"
    )

    erros = sum(
        1
        for item in respondidas
        if item[
            "status"
        ] == "Errada"
    )

    desempenho = (
        100.0
        * acertos
        / len(
            respondidas
        )
        if respondidas
        else None
    )

    caderno = listar_caderno_erros_questoes(
        concurso_id
    )

    return {
        "tentativas": len(
            historico
        ),
        "respondidas": len(
            respondidas
        ),
        "acertos": acertos,
        "erros": erros,
        "puladas": sum(
            1
            for item in historico
            if item[
                "status"
            ] == "Pulada"
        ),
        "duvidas": sum(
            1
            for item in historico
            if item[
                "duvida"
            ]
        ),
        "desempenho": desempenho,
        "questoes_unicas": len({
            item[
                "questao_id"
            ]
            for item in respondidas
        }),
        "caderno_total": len(
            caderno
        ),
        "criticas": sum(
            1
            for item in caderno
            if item[
                "status"
            ] == "Crítica"
        ),
        "recorrentes": sum(
            1
            for item in caderno
            if item[
                "status"
            ] == "Recorrente"
        ),
        "recuperadas": sum(
            1
            for item in caderno
            if item[
                "status"
            ] == "Recuperada"
        ),
    }



def obter_central_minha_evolucao(
    concurso_id=None,
    dias=30
):
    """
    Consolida a visão estratégica de evolução do perfil.

    A evolução temporal usa tentativas internas preservadas por snapshot,
    enquanto o domínio atual usa o Índice de Domínio já calculado pelo
    VighnaStudy. Nenhuma métrica histórica é reconstruída a partir da
    versão atual de uma questão.
    """

    if concurso_id is None:
        concurso_id = obter_concurso_ativo()[0]

    concurso_id = int(concurso_id)
    dias = max(7, min(365, int(dias or 30)))

    hoje = date.today()
    inicio_recente = hoje - timedelta(days=dias - 1)
    fim_anterior = inicio_recente - timedelta(days=1)
    inicio_anterior = fim_anterior - timedelta(days=dias - 1)

    with conectar() as conexao:
        linhas = conexao.execute(
            """
            SELECT
                tq.respondida_em,
                tq.correta,
                COALESCE(
                    tq.disciplina_snapshot,
                    d.nome,
                    '—'
                ) AS disciplina,
                COALESCE(
                    tq.topico_id_snapshot,
                    q.topico_id
                ) AS topico_ref,
                COALESCE(
                    tq.questao_id_snapshot,
                    tq.questao_id
                ) AS questao_ref
            FROM tentativas_questoes tq
            LEFT JOIN questoes q
                ON q.id = tq.questao_id
            LEFT JOIN topicos t_ref
                ON t_ref.id = COALESCE(
                    tq.topico_id_snapshot,
                    q.topico_id
                )
            LEFT JOIN disciplinas d
                ON d.id = t_ref.disciplina_id
            JOIN disciplina_concurso_inclusao dc
                ON dc.disciplina_id = t_ref.disciplina_id
                AND dc.concurso_id = ?
                AND dc.incluido = 1
                AND COALESCE(dc.pausado, 0) = 0
            JOIN topico_concurso_importancia tc
                ON tc.topico_id = t_ref.id
                AND tc.concurso_id = ?
                AND tc.incluido = 1
            WHERE
                tq.concurso_id = ?
                AND tq.correta IS NOT NULL
            ORDER BY
                tq.respondida_em ASC,
                tq.id ASC
            """,
            (
                concurso_id,
                concurso_id,
                concurso_id,
            )
        ).fetchall()

    def converter_data(valor):
        texto = str(valor or '')[:10]
        try:
            return date.fromisoformat(texto)
        except (TypeError, ValueError):
            return None

    tentativas = []
    for linha in linhas:
        data_item = converter_data(linha[0])
        if data_item is None:
            continue
        tentativas.append({
            'data': data_item,
            'correta': bool(linha[1]),
            'disciplina': linha[2] or '—',
            'topico_id': linha[3],
            'questao_id': linha[4],
        })

    def dentro(item, inicio, fim):
        return inicio <= item['data'] <= fim

    recentes = [
        item for item in tentativas
        if dentro(item, inicio_recente, hoje)
    ]
    anteriores = [
        item for item in tentativas
        if dentro(item, inicio_anterior, fim_anterior)
    ]

    def resumo_periodo(items):
        total = len(items)
        acertos = sum(1 for item in items if item['correta'])
        desempenho = (
            100.0 * acertos / total
            if total > 0 else None
        )
        return {
            'questoes': total,
            'acertos': acertos,
            'erros': total - acertos,
            'desempenho': desempenho,
            'dias_ativos': len({item['data'] for item in items}),
            'questoes_unicas': len({item['questao_id'] for item in items if item['questao_id'] is not None}),
        }

    resumo_recente = resumo_periodo(recentes)
    resumo_anterior = resumo_periodo(anteriores)

    if (
        resumo_recente['desempenho'] is not None
        and resumo_anterior['desempenho'] is not None
    ):
        variacao_desempenho = (
            resumo_recente['desempenho']
            - resumo_anterior['desempenho']
        )
    else:
        variacao_desempenho = None

    indices = obter_indices_dominio_topicos(concurso_id)
    indices_com_evidencia = [
        item for item in indices.values()
        if int(item.get('tentativas') or 0) > 0
    ]
    dominio_medio = (
        sum(float(item.get('score') or 0.0) for item in indices_com_evidencia)
        / len(indices_com_evidencia)
        if indices_com_evidencia else None
    )

    # Estado corrente do edital, seguindo as mesmas regras da interface.
    total_topicos = 0
    consolidados = 0
    por_disciplina_indices = {}

    for _, disciplina in listar_disciplinas(concurso_id):
        topicos = listar_topicos(disciplina, concurso_id)
        total_topicos += len(topicos)
        for topico in topicos:
            revisoes = int(topico[2] or 0)
            percentual = topico[5]
            if (
                revisoes >= 4
                and percentual is not None
                and float(percentual) >= 85.0
            ):
                consolidados += 1

            dominio = indices.get(int(topico[0]))
            if dominio and int(dominio.get('tentativas') or 0) > 0:
                por_disciplina_indices.setdefault(disciplina, []).append(dominio)

    # Comparação por disciplina baseada em tentativas preservadas.
    nomes_disciplinas = [nome for _, nome in listar_disciplinas(concurso_id)]
    disciplinas = []

    for nome in nomes_disciplinas:
        itens_recentes = [item for item in recentes if item['disciplina'] == nome]
        itens_anteriores = [item for item in anteriores if item['disciplina'] == nome]
        rr = resumo_periodo(itens_recentes)
        ra = resumo_periodo(itens_anteriores)

        if rr['desempenho'] is not None and ra['desempenho'] is not None:
            delta = rr['desempenho'] - ra['desempenho']
        else:
            delta = None

        evidencias_dominio = por_disciplina_indices.get(nome, [])
        score_dominio = (
            sum(float(item.get('score') or 0.0) for item in evidencias_dominio)
            / len(evidencias_dominio)
            if evidencias_dominio else None
        )

        if score_dominio is None:
            nivel = 'Sem evidência'
        elif score_dominio < 30:
            nivel = 'Crítico'
        elif score_dominio < 50:
            nivel = 'Frágil'
        elif score_dominio < 70:
            nivel = 'Em desenvolvimento'
        elif score_dominio < 85:
            nivel = 'Consolidando'
        elif score_dominio < 95:
            nivel = 'Dominado'
        else:
            nivel = 'Domínio forte'

        disciplinas.append({
            'disciplina': nome,
            'dominio': score_dominio,
            'nivel': nivel,
            'desempenho': rr['desempenho'],
            'variacao': delta,
            'questoes': rr['questoes'],
            'questoes_anteriores': ra['questoes'],
            'dias_ativos': rr['dias_ativos'],
        })

    disciplinas.sort(
        key=lambda item: (
            item['dominio'] is None,
            -(item['dominio'] or 0.0),
            item['disciplina'].lower(),
        )
    )

    comparaveis = [
        item for item in disciplinas
        if (
            item['variacao'] is not None
            and item['questoes'] >= 5
            and item['questoes_anteriores'] >= 5
        )
    ]

    maior_evolucao = (
        max(comparaveis, key=lambda item: item['variacao'])
        if comparaveis else None
    )
    maior_queda = (
        min(comparaveis, key=lambda item: item['variacao'])
        if comparaveis else None
    )

    dominio_validos = [item for item in disciplinas if item['dominio'] is not None]
    menor_dominio = (
        min(dominio_validos, key=lambda item: item['dominio'])
        if dominio_validos else None
    )

    caderno = listar_caderno_erros_questoes(concurso_id)
    recuperadas = sum(1 for item in caderno if item.get('status') == 'Recuperada')
    recorrentes = sum(1 for item in caderno if item.get('status') in ('Crítica', 'Recorrente'))

    # Série diária completa para o intervalo selecionado.
    por_dia = {}
    for item in recentes:
        chave = item['data']
        registro = por_dia.setdefault(chave, [0, 0])
        registro[0] += 1
        registro[1] += 1 if item['correta'] else 0

    serie = []
    cursor = inicio_recente
    while cursor <= hoje:
        total, acertos = por_dia.get(cursor, [0, 0])
        serie.append({
            'data': cursor.isoformat(),
            'questoes': total,
            'desempenho': (
                100.0 * acertos / total
                if total > 0 else None
            ),
        })
        cursor += timedelta(days=1)

    return {
        'dias': dias,
        'data_inicio': inicio_recente.isoformat(),
        'data_fim': hoje.isoformat(),
        'resumo': resumo_recente,
        'resumo_anterior': resumo_anterior,
        'variacao_desempenho': variacao_desempenho,
        'dominio_medio': dominio_medio,
        'topicos_com_evidencia': len(indices_com_evidencia),
        'total_topicos': total_topicos,
        'consolidados': consolidados,
        'disciplinas': disciplinas,
        'maior_evolucao': maior_evolucao,
        'maior_queda': maior_queda,
        'menor_dominio': menor_dominio,
        'recuperadas': recuperadas,
        'erros_recorrentes': recorrentes,
        'serie': serie,
    }

def obter_eventos_previsao_edital(
    concurso_id=None
):
    """
    Retorna eventos temporais confiáveis para previsão do edital.

    - data_inicio:
      primeira revisão registrada no VighnaStudy apenas quando o tópico
      não possuía revisões importadas. Assim não tratamos um tópico legado
      como se tivesse sido iniciado recentemente.

    - data_consolidacao:
      início da fase de consolidação ATUAL do tópico, quando esse momento
      pode ser determinado por revisões registradas no VighnaStudy.

    O estado consolidado segue a regra da interface:
    pelo menos 4 revisões totais + desempenho >= 85%.
    """

    if concurso_id is None:
        concurso_id = (
            obter_concurso_ativo()[0]
        )

    with conectar() as conexao:
        linhas = conexao.execute(
            """
            WITH base AS (
                SELECT
                    t.id AS topico_id,
                    d.nome AS disciplina,
                    t.nome AS topico,
                    COALESCE(
                        c.revisoes_iniciais,
                        0
                    ) AS revisoes_iniciais,
                    c.percentual_inicial AS percentual_inicial,
                    COALESCE(
                        tc.importancia,
                        3
                    ) AS importancia
                FROM topicos t
                JOIN disciplinas d
                    ON d.id = t.disciplina_id
                JOIN disciplina_concurso_inclusao dc
                    ON dc.disciplina_id = d.id
                    AND dc.concurso_id = ?
                    AND dc.incluido = 1
                    AND COALESCE(dc.pausado, 0) = 0
                JOIN topico_concurso_importancia tc
                    ON tc.topico_id = t.id
                    AND tc.concurso_id = ?
                    AND tc.incluido = 1
                LEFT JOIN controle_topico c
                    ON c.topico_id = t.id
            ),
            revs AS (
                SELECT
                    r.topico_id,
                    r.data,
                    r.id,
                    ROUND(
                        100.0
                        * r.acertos
                        / r.questoes,
                        1
                    ) AS percentual,
                    ROW_NUMBER() OVER (
                        PARTITION BY r.topico_id
                        ORDER BY r.data ASC, r.id ASC
                    ) AS rn
                FROM revisoes r
                JOIN base b
                    ON b.topico_id = r.topico_id
            ),
            calc AS (
                SELECT
                    rv.topico_id,
                    rv.data,
                    rv.id,
                    rv.rn,
                    rv.percentual,
                    (
                        b.revisoes_iniciais
                        + rv.rn
                    ) AS revisoes_totais,
                    CASE
                        WHEN
                            (
                                b.revisoes_iniciais
                                + rv.rn
                            ) >= 4
                            AND rv.percentual >= 85.0
                        THEN 1
                        ELSE 0
                    END AS consolidado
                FROM revs rv
                JOIN base b
                    ON b.topico_id = rv.topico_id
            ),
            atual AS (
                SELECT
                    b.topico_id,
                    b.disciplina,
                    b.topico,
                    b.revisoes_iniciais,
                    b.percentual_inicial,
                    b.importancia,
                    (
                        SELECT COUNT(*)
                        FROM revs rv
                        WHERE rv.topico_id = b.topico_id
                    ) AS revisoes_programa,
                    (
                        SELECT rv.percentual
                        FROM revs rv
                        WHERE rv.topico_id = b.topico_id
                        ORDER BY rv.rn DESC
                        LIMIT 1
                    ) AS percentual_ultima,
                    (
                        SELECT rv.data
                        FROM revs rv
                        WHERE rv.topico_id = b.topico_id
                        ORDER BY rv.rn DESC
                        LIMIT 1
                    ) AS ultima_revisao
                FROM base b
            )
            SELECT
                a.topico_id,
                a.disciplina,
                a.topico,
                a.revisoes_iniciais,
                a.revisoes_programa,
                (
                    a.revisoes_iniciais
                    + a.revisoes_programa
                ) AS revisoes_totais,
                CASE
                    WHEN a.revisoes_programa > 0
                    THEN a.percentual_ultima
                    ELSE a.percentual_inicial
                END AS percentual_atual,
                a.importancia,
                CASE
                    WHEN a.revisoes_iniciais = 0
                    THEN (
                        SELECT MIN(rv.data)
                        FROM revs rv
                        WHERE rv.topico_id = a.topico_id
                    )
                    ELSE NULL
                END AS data_inicio,
                CASE
                    WHEN
                        (
                            a.revisoes_iniciais
                            + a.revisoes_programa
                        ) >= 4
                        AND (
                            CASE
                                WHEN a.revisoes_programa > 0
                                THEN a.percentual_ultima
                                ELSE a.percentual_inicial
                            END
                        ) >= 85.0
                    THEN
                        CASE
                            -- Se houve queda para fora da consolidação,
                            -- usamos a primeira revisão consolidada depois
                            -- da última queda.
                            WHEN EXISTS (
                                SELECT 1
                                FROM calc c0
                                WHERE
                                    c0.topico_id = a.topico_id
                                    AND c0.consolidado = 0
                            )
                            THEN (
                                SELECT MIN(c1.data)
                                FROM calc c1
                                WHERE
                                    c1.topico_id = a.topico_id
                                    AND c1.consolidado = 1
                                    AND c1.rn > COALESCE(
                                        (
                                            SELECT MAX(c2.rn)
                                            FROM calc c2
                                            WHERE
                                                c2.topico_id = a.topico_id
                                                AND c2.consolidado = 0
                                        ),
                                        0
                                    )
                            )

                            -- Sem queda registrada: só conseguimos datar
                            -- a consolidação se o estado importado inicial
                            -- ainda não era consolidado.
                            WHEN NOT (
                                a.revisoes_iniciais >= 4
                                AND a.percentual_inicial >= 85.0
                            )
                            THEN (
                                SELECT MIN(c3.data)
                                FROM calc c3
                                WHERE
                                    c3.topico_id = a.topico_id
                                    AND c3.consolidado = 1
                            )

                            -- Já chegou consolidado do legado:
                            -- a data real de consolidação é desconhecida.
                            ELSE NULL
                        END
                    ELSE NULL
                END AS data_consolidacao,
                a.ultima_revisao
            FROM atual a
            ORDER BY
                a.disciplina COLLATE NOCASE,
                a.topico COLLATE NOCASE
            """,
            (
                concurso_id,
                concurso_id
            )
        ).fetchall()

    return [
        {
            "topico_id": linha[0],
            "disciplina": linha[1],
            "topico": linha[2],
            "revisoes_iniciais": int(
                linha[3] or 0
            ),
            "revisoes_programa": int(
                linha[4] or 0
            ),
            "revisoes_totais": int(
                linha[5] or 0
            ),
            "percentual_atual": linha[6],
            "importancia": int(
                linha[7] or 3
            ),
            "data_inicio": linha[8],
            "data_consolidacao": linha[9],
            "ultima_revisao": linha[10],
        }
        for linha in linhas
    ]


def listar_revisoes_agendadas_periodo(
    data_inicio,
    data_fim,
    concurso_id=None
):
    """
    Retorna as revisões cuja próxima revisão está dentro do período,
    respeitando as disciplinas e tópicos incluídos no perfil ativo.
    """
    percentual = _expressao_percentual_atual()
    revisoes = _expressao_revisoes_totais()

    if concurso_id is None:
        concurso_id = (
            obter_concurso_ativo()[0]
        )

    with conectar() as conexao:
        return conexao.execute(
            f"""
            SELECT
                t.id,
                d.nome,
                t.nome,
                {revisoes} AS revisoes_totais,
                c.proxima_revisao,
                {percentual} AS percentual_atual,
                COALESCE(
                    tc.importancia,
                    3
                ) AS importancia
            FROM topicos t
            JOIN disciplinas d
                ON d.id = t.disciplina_id
            JOIN disciplina_concurso_inclusao dc
                ON dc.disciplina_id = d.id
                AND dc.concurso_id = ?
                AND dc.incluido = 1
                AND COALESCE(dc.pausado, 0) = 0
            JOIN topico_concurso_importancia tc
                ON tc.topico_id = t.id
                AND tc.concurso_id = ?
                AND tc.incluido = 1
                AND COALESCE(tc.pausado, 0) = 0
            JOIN controle_topico c
                ON c.topico_id = t.id
            WHERE
                c.proxima_revisao IS NOT NULL
                AND c.proxima_revisao >= ?
                AND c.proxima_revisao <= ?
            ORDER BY
                c.proxima_revisao ASC,
                d.nome COLLATE NOCASE,
                t.nome COLLATE NOCASE
            """,
            (
                concurso_id,
                concurso_id,
                data_inicio,
                data_fim
            )
        ).fetchall()


def listar_pendencias(
    data_referencia,
    concurso_id=None
):
    percentual = _expressao_percentual_atual()
    revisoes = _expressao_revisoes_totais()

    if concurso_id is None:
        concurso_id = (
            obter_concurso_ativo()[0]
        )

    with conectar() as conexao:
        return conexao.execute(
            f"""
            SELECT
                t.id,
                d.nome,
                t.nome,
                {revisoes} AS revisoes_totais,
                c.proxima_revisao,
                {percentual} AS percentual_atual,
                COALESCE(
                    tc.importancia,
                    3
                ) AS importancia
            FROM topicos t
            JOIN disciplinas d
                ON d.id = t.disciplina_id
            JOIN disciplina_concurso_inclusao dc
                ON dc.disciplina_id = d.id
                AND dc.concurso_id = ?
                AND dc.incluido = 1
                AND COALESCE(dc.pausado, 0) = 0
            JOIN topico_concurso_importancia tc
                ON tc.topico_id = t.id
                AND tc.concurso_id = ?
                AND tc.incluido = 1
                AND COALESCE(tc.pausado, 0) = 0
            JOIN controle_topico c
                ON c.topico_id = t.id
            WHERE
                c.proxima_revisao IS NOT NULL
                AND c.proxima_revisao <= ?
            ORDER BY
                c.proxima_revisao ASC,
                CASE
                    WHEN ({percentual}) IS NULL
                        THEN 999
                    ELSE ({percentual})
                END ASC,
                d.nome COLLATE NOCASE,
                t.nome COLLATE NOCASE
            """,
            (
                concurso_id,
                concurso_id,
                data_referencia
            )
        ).fetchall()


def obter_dashboard(
    data_referencia,
    concurso_id=None
):
    percentual = _expressao_percentual_atual()

    if concurso_id is None:
        concurso_id = (
            obter_concurso_ativo()[0]
        )

    with conectar() as conexao:
        filtro = """
            FROM topicos t
            JOIN disciplinas d
                ON d.id = t.disciplina_id
            JOIN disciplina_concurso_inclusao dc
                ON dc.disciplina_id = d.id
                AND dc.concurso_id = ?
                AND dc.incluido = 1
                AND COALESCE(dc.pausado, 0) = 0
            JOIN topico_concurso_importancia tc
                ON tc.topico_id = t.id
                AND tc.concurso_id = ?
                AND tc.incluido = 1
                AND COALESCE(tc.pausado, 0) = 0
            LEFT JOIN controle_topico c
                ON c.topico_id = t.id
        """

        total_topicos = conexao.execute(
            f"""
            SELECT COUNT(*)
            {filtro}
            """,
            (
                concurso_id,
                concurso_id
            )
        ).fetchone()[0]

        atrasadas = conexao.execute(
            f"""
            SELECT COUNT(*)
            {filtro}
            WHERE
                c.proxima_revisao IS NOT NULL
                AND c.proxima_revisao < ?
            """,
            (
                concurso_id,
                concurso_id,
                data_referencia
            )
        ).fetchone()[0]

        hoje = conexao.execute(
            f"""
            SELECT COUNT(*)
            {filtro}
            WHERE c.proxima_revisao = ?
            """,
            (
                concurso_id,
                concurso_id,
                data_referencia
            )
        ).fetchone()[0]

        total_questoes = conexao.execute(
            """
            SELECT COALESCE(
                SUM(r.questoes),
                0
            )
            FROM revisoes r
            JOIN topicos t
                ON t.id = r.topico_id
            JOIN disciplinas d
                ON d.id = t.disciplina_id
            JOIN disciplina_concurso_inclusao dc
                ON dc.disciplina_id = d.id
                AND dc.concurso_id = ?
                AND dc.incluido = 1
                AND COALESCE(dc.pausado, 0) = 0
            JOIN topico_concurso_importancia tc
                ON tc.topico_id = t.id
                AND tc.concurso_id = ?
                AND tc.incluido = 1
            """,
            (
                concurso_id,
                concurso_id
            )
        ).fetchone()[0]

        revisoes_programa = conexao.execute(
            """
            SELECT COUNT(*)
            FROM revisoes r
            JOIN topicos t
                ON t.id = r.topico_id
            JOIN disciplinas d
                ON d.id = t.disciplina_id
            JOIN disciplina_concurso_inclusao dc
                ON dc.disciplina_id = d.id
                AND dc.concurso_id = ?
                AND dc.incluido = 1
                AND COALESCE(dc.pausado, 0) = 0
            JOIN topico_concurso_importancia tc
                ON tc.topico_id = t.id
                AND tc.concurso_id = ?
                AND tc.incluido = 1
            """,
            (
                concurso_id,
                concurso_id
            )
        ).fetchone()[0]

        revisoes_iniciais = conexao.execute(
            f"""
            SELECT COALESCE(
                SUM(
                    COALESCE(
                        c.revisoes_iniciais,
                        0
                    )
                ),
                0
            )
            {filtro}
            """,
            (
                concurso_id,
                concurso_id
            )
        ).fetchone()[0]

        media = conexao.execute(
            f"""
            SELECT ROUND(
                AVG(percentual_atual),
                1
            )
            FROM (
                SELECT
                    {percentual}
                    AS percentual_atual
                {filtro}
            )
            WHERE percentual_atual IS NOT NULL
            """,
            (
                concurso_id,
                concurso_id
            )
        ).fetchone()[0]

        return {
            "total_topicos": int(
                total_topicos or 0
            ),
            "atrasadas": int(
                atrasadas or 0
            ),
            "hoje": int(
                hoje or 0
            ),
            "total_questoes": int(
                total_questoes or 0
            ),
            "revisoes_totais": int(
                (revisoes_iniciais or 0)
                + (revisoes_programa or 0)
            ),
            "media_atual": media,
        }




# ==========================================================
# CONFIGURAÇÕES
# ==========================================================

def obter_configuracao_texto(
    chave,
    padrao=None
):
    with conectar() as conexao:
        linha = conexao.execute(
            """
            SELECT valor
            FROM configuracoes
            WHERE chave = ?
            """,
            (chave,)
        ).fetchone()

        if linha is None:
            return padrao

        return str(
            linha[0]
        )


def definir_configuracao_texto(
    chave,
    valor
):
    with conectar() as conexao:
        conexao.execute(
            """
            INSERT INTO configuracoes (
                chave,
                valor
            )
            VALUES (?, ?)
            ON CONFLICT(chave)
            DO UPDATE SET
                valor = excluded.valor
            """,
            (
                chave,
                str(valor)
            )
        )


def obter_configuracao_int(
    chave,
    padrao=0
):
    valor = obter_configuracao_texto(
        chave,
        None
    )

    if valor is None:
        return int(
            padrao
        )

    try:
        return int(
            float(valor)
        )
    except (
        TypeError,
        ValueError
    ):
        return int(
            padrao
        )


def definir_configuracao_int(
    chave,
    valor
):
    definir_configuracao_texto(
        chave,
        int(valor)
    )


def obter_configuracao_bool(chave, padrao=True):
    with conectar() as conexao:
        linha = conexao.execute(
            """
            SELECT valor
            FROM configuracoes
            WHERE chave = ?
            """,
            (chave,)
        ).fetchone()

        if linha is None:
            return bool(padrao)

        return str(linha[0]).strip() in {
            "1",
            "true",
            "True",
            "sim",
            "on"
        }


def definir_configuracao_bool(chave, valor):
    valor_texto = "1" if bool(valor) else "0"

    with conectar() as conexao:
        conexao.execute(
            """
            INSERT INTO configuracoes (chave, valor)
            VALUES (?, ?)
            ON CONFLICT(chave)
            DO UPDATE SET valor = excluded.valor
            """,
            (chave, valor_texto)
        )

# ==========================================================
# ESTATÍSTICAS
# ==========================================================

def obter_estatisticas_disciplinas(
    data_referencia,
    concurso_id=None
):
    """
    Estatísticas somente do conteúdo incluído no perfil ativo.
    """

    if concurso_id is None:
        concurso_id = (
            obter_concurso_ativo()[0]
        )

    resultados = []

    for _, nome_disciplina in listar_disciplinas(
        concurso_id
    ):
        topicos = listar_topicos(
            nome_disciplina,
            concurso_id
        )

        total_topicos = len(
            topicos
        )

        revisoes_totais = sum(
            int(item[2] or 0)
            for item in topicos
        )

        percentuais = [
            float(item[5])
            for item in topicos
            if item[5] is not None
        ]

        if percentuais:
            media_atual = round(
                sum(percentuais)
                / len(percentuais),
                1
            )
        else:
            media_atual = None

        atrasadas = sum(
            1
            for item in topicos
            if item[4]
            and item[4] < data_referencia
        )

        hoje = sum(
            1
            for item in topicos
            if item[4] == data_referencia
        )

        with conectar() as conexao:
            questoes = conexao.execute(
                """
                SELECT COALESCE(
                    SUM(r.questoes),
                    0
                )
                FROM revisoes r
                JOIN topicos t
                    ON t.id = r.topico_id
                JOIN disciplinas d
                    ON d.id = t.disciplina_id
                JOIN disciplina_concurso_inclusao dc
                    ON dc.disciplina_id = d.id
                    AND dc.concurso_id = ?
                    AND dc.incluido = 1
                    AND COALESCE(dc.pausado, 0) = 0
                JOIN topico_concurso_importancia tc
                    ON tc.topico_id = t.id
                    AND tc.concurso_id = ?
                    AND tc.incluido = 1
                WHERE d.nome = ?
                """,
                (
                    concurso_id,
                    concurso_id,
                    nome_disciplina
                )
            ).fetchone()[0]

        resultados.append(
            (
                nome_disciplina,
                total_topicos,
                revisoes_totais,
                media_atual,
                int(questoes or 0),
                atrasadas,
                hoje
            )
        )

    return resultados


def listar_ranking_topicos(
    limite=20,
    ordem="asc",
    concurso_id=None
):
    """
    Ranking pelo percentual atual apenas do perfil ativo.
    """
    percentual = _expressao_percentual_atual()
    revisoes = _expressao_revisoes_totais()

    if concurso_id is None:
        concurso_id = (
            obter_concurso_ativo()[0]
        )

    direcao = (
        "DESC"
        if str(ordem).lower() == "desc"
        else "ASC"
    )

    with conectar() as conexao:
        return conexao.execute(
            f"""
            SELECT
                t.id,
                d.nome,
                t.nome,
                {revisoes} AS revisoes_totais,
                {percentual} AS percentual_atual,
                c.proxima_revisao,
                (
                    SELECT r.data
                    FROM revisoes r
                    WHERE r.topico_id = t.id
                    ORDER BY r.data DESC, r.id DESC
                    LIMIT 1
                ) AS ultima_revisao
            FROM topicos t
            JOIN disciplinas d
                ON d.id = t.disciplina_id
            JOIN disciplina_concurso_inclusao dc
                ON dc.disciplina_id = d.id
                AND dc.concurso_id = ?
                AND dc.incluido = 1
                AND COALESCE(dc.pausado, 0) = 0
            JOIN topico_concurso_importancia tc
                ON tc.topico_id = t.id
                AND tc.concurso_id = ?
                AND tc.incluido = 1
                AND COALESCE(tc.pausado, 0) = 0
            LEFT JOIN controle_topico c
                ON c.topico_id = t.id
            WHERE ({percentual}) IS NOT NULL
            ORDER BY
                percentual_atual {direcao},
                revisoes_totais ASC,
                d.nome COLLATE NOCASE,
                t.nome COLLATE NOCASE
            LIMIT ?
            """,
            (
                concurso_id,
                concurso_id,
                int(limite)
            )
        ).fetchall()


def listar_revisoes_recentes(
    limite=30,
    concurso_id=None
):
    if concurso_id is None:
        concurso_id = (
            obter_concurso_ativo()[0]
        )

    with conectar() as conexao:
        return conexao.execute(
            """
            SELECT
                r.id,
                t.id AS topico_id,
                r.data,
                d.nome AS disciplina,
                t.nome AS topico,
                r.questoes,
                r.acertos,
                ROUND(
                    100.0 * r.acertos / r.questoes,
                    1
                ) AS percentual
            FROM revisoes r
            JOIN topicos t
                ON t.id = r.topico_id
            JOIN disciplinas d
                ON d.id = t.disciplina_id
            JOIN disciplina_concurso_inclusao dc
                ON dc.disciplina_id = d.id
                AND dc.concurso_id = ?
                AND dc.incluido = 1
                AND COALESCE(dc.pausado, 0) = 0
            JOIN topico_concurso_importancia tc
                ON tc.topico_id = t.id
                AND tc.concurso_id = ?
                AND tc.incluido = 1
            ORDER BY
                r.data DESC,
                r.id DESC
            LIMIT ?
            """,
            (
                concurso_id,
                concurso_id,
                int(limite)
            )
        ).fetchall()



# ==========================================================
# RELATÓRIOS POR PERÍODO
# ==========================================================


def obter_relatorio_estrategico(
    data_inicio,
    data_fim,
    concurso_id=None
):
    """
    Relatórios Estratégicos V1.

    Consolida sinais já existentes no VighnaStudy em uma leitura acionável:
    situação atual, evolução, riscos e prioridades recomendadas.

    Não estima probabilidade de aprovação. O estado de preparação é uma
    classificação explicável baseada em domínio atual, evidência disponível,
    desempenho no período e erros abertos.
    """

    if concurso_id is None:
        concurso_id = obter_concurso_ativo()[0]

    concurso_id = int(concurso_id)

    try:
        inicio = date.fromisoformat(str(data_inicio)[:10])
        fim = date.fromisoformat(str(data_fim)[:10])
    except (TypeError, ValueError):
        raise ValueError("Período inválido para o relatório estratégico.")

    if inicio > fim:
        inicio, fim = fim, inicio

    dias = (fim - inicio).days + 1
    fim_anterior = inicio - timedelta(days=1)
    inicio_anterior = fim_anterior - timedelta(days=dias - 1)

    with conectar() as conexao:
        linhas = conexao.execute(
            """
            SELECT
                tq.respondida_em,
                tq.correta,
                COALESCE(tq.marcada_duvida, 0),
                COALESCE(tq.questao_id_snapshot, tq.questao_id) AS questao_ref,
                COALESCE(tq.topico_id_snapshot, q.topico_id) AS topico_ref,
                COALESCE(tq.disciplina_snapshot, d.nome, '—') AS disciplina,
                COALESCE(tq.topico_snapshot, t_ref.nome, '—') AS topico
            FROM tentativas_questoes tq
            LEFT JOIN questoes q
                ON q.id = tq.questao_id
            LEFT JOIN topicos t_ref
                ON t_ref.id = COALESCE(tq.topico_id_snapshot, q.topico_id)
            LEFT JOIN disciplinas d
                ON d.id = t_ref.disciplina_id
            JOIN disciplina_concurso_inclusao dc
                ON dc.disciplina_id = t_ref.disciplina_id
                AND dc.concurso_id = ?
                AND dc.incluido = 1
                AND COALESCE(dc.pausado, 0) = 0
            JOIN topico_concurso_importancia tc
                ON tc.topico_id = t_ref.id
                AND tc.concurso_id = ?
                AND tc.incluido = 1
            WHERE
                tq.concurso_id = ?
                AND tq.correta IS NOT NULL
                AND substr(tq.respondida_em, 1, 10) >= ?
                AND substr(tq.respondida_em, 1, 10) <= ?
            ORDER BY tq.respondida_em ASC, tq.id ASC
            """,
            (
                concurso_id,
                concurso_id,
                concurso_id,
                inicio_anterior.isoformat(),
                fim.isoformat(),
            )
        ).fetchall()

        simulados_linhas = conexao.execute(
            """
            SELECT
                s.criado_em,
                s.tipo,
                s.configuracao_json
            FROM simulados s
            WHERE
                s.concurso_id = ?
                AND substr(s.criado_em, 1, 10) >= ?
                AND substr(s.criado_em, 1, 10) <= ?
            ORDER BY s.criado_em DESC, s.id DESC
            """,
            (
                concurso_id,
                inicio.isoformat(),
                fim.isoformat(),
            )
        ).fetchall()

    def converter_data(valor):
        try:
            return date.fromisoformat(str(valor or '')[:10])
        except (TypeError, ValueError):
            return None

    tentativas = []
    for linha in linhas:
        data_item = converter_data(linha[0])
        if data_item is None:
            continue
        tentativas.append({
            "data": data_item,
            "correta": bool(linha[1]),
            "duvida": bool(linha[2]),
            "questao_id": linha[3],
            "topico_id": int(linha[4]) if linha[4] is not None else None,
            "disciplina": linha[5] or "—",
            "topico": linha[6] or "—",
        })

    atuais = [item for item in tentativas if inicio <= item["data"] <= fim]
    anteriores = [
        item for item in tentativas
        if inicio_anterior <= item["data"] <= fim_anterior
    ]

    def resumir(items):
        total = len(items)
        acertos = sum(1 for item in items if item["correta"])
        return {
            "questoes": total,
            "acertos": acertos,
            "erros": total - acertos,
            "desempenho": (100.0 * acertos / total) if total else None,
            "dias_ativos": len({item["data"] for item in items}),
            "questoes_unicas": len({item["questao_id"] for item in items if item["questao_id"] is not None}),
            "topicos": len({item["topico_id"] for item in items if item["topico_id"] is not None}),
            "duvidas": sum(1 for item in items if item["duvida"]),
        }

    resumo = resumir(atuais)
    resumo_anterior = resumir(anteriores)

    desempenho_delta = None
    if resumo["desempenho"] is not None and resumo_anterior["desempenho"] is not None:
        desempenho_delta = resumo["desempenho"] - resumo_anterior["desempenho"]

    questoes_delta = resumo["questoes"] - resumo_anterior["questoes"]
    dias_ativos_delta = resumo["dias_ativos"] - resumo_anterior["dias_ativos"]

    indices = obter_indices_dominio_topicos(concurso_id)
    prioridades = obter_prioridades_sessao_adaptativa(concurso_id)
    caderno = listar_caderno_erros_questoes(concurso_id)

    total_topicos = len(indices)
    indices_evidencia = [
        item for item in indices.values()
        if int(item.get("tentativas_historicas", item.get("tentativas", 0)) or 0) > 0
    ]
    topicos_com_evidencia = len(indices_evidencia)
    cobertura_evidencia = (
        100.0 * topicos_com_evidencia / total_topicos
        if total_topicos else 0.0
    )
    dominio_medio = (
        sum(float(item.get("score") or 0.0) for item in indices_evidencia) / len(indices_evidencia)
        if indices_evidencia else None
    )

    criticas_abertas = sum(int(item.get("criticas") or 0) for item in indices.values())
    recorrentes_abertas = sum(int(item.get("recorrentes") or 0) for item in indices.values())
    recuperacao_aberta = sum(int(item.get("recuperacao") or 0) for item in indices.values())
    recuperadas = sum(1 for item in caderno if item.get("status") == "Recuperada")

    # Desempenho por disciplina no período e no período anterior.
    nomes = sorted({
        item.get("disciplina") or "—"
        for item in indices.values()
    }, key=lambda valor: valor.lower())

    disciplinas = []
    maior_evolucao = None
    maior_queda = None

    for nome in nomes:
        dominio_itens = [
            item for item in indices.values()
            if (item.get("disciplina") or "—") == nome
        ]
        evidencias = [
            item for item in dominio_itens
            if int(item.get("tentativas_historicas", item.get("tentativas", 0)) or 0) > 0
        ]
        dominio_disc = (
            sum(float(item.get("score") or 0.0) for item in evidencias) / len(evidencias)
            if evidencias else None
        )
        cobertura_disc = (
            100.0 * len(evidencias) / len(dominio_itens)
            if dominio_itens else 0.0
        )

        atual_disc = resumir([item for item in atuais if item["disciplina"] == nome])
        anterior_disc = resumir([item for item in anteriores if item["disciplina"] == nome])
        delta = None
        if atual_disc["desempenho"] is not None and anterior_disc["desempenho"] is not None:
            delta = atual_disc["desempenho"] - anterior_disc["desempenho"]

        criticas_disc = sum(int(item.get("criticas") or 0) for item in dominio_itens)
        recorrentes_disc = sum(int(item.get("recorrentes") or 0) for item in dominio_itens)

        if dominio_disc is None and atual_disc["questoes"] < 5:
            nivel = "Evidência insuficiente"
        elif (
            criticas_disc >= 2
            or (dominio_disc is not None and dominio_disc < 50.0)
            or (atual_disc["desempenho"] is not None and atual_disc["questoes"] >= 5 and atual_disc["desempenho"] < 55.0)
        ):
            nivel = "Atenção"
        elif (
            cobertura_disc < 35.0
            or (dominio_disc is not None and dominio_disc < 70.0)
            or (atual_disc["desempenho"] is not None and atual_disc["questoes"] >= 5 and atual_disc["desempenho"] < 70.0)
        ):
            nivel = "Em construção"
        elif (
            dominio_disc is not None
            and dominio_disc >= 85.0
            and cobertura_disc >= 60.0
            and criticas_disc == 0
            and recorrentes_disc <= 1
            and (atual_disc["desempenho"] is None or atual_disc["desempenho"] >= 80.0)
        ):
            nivel = "Forte"
        else:
            nivel = "Boa"

        registro = {
            "disciplina": nome,
            "preparacao": nivel,
            "dominio": dominio_disc,
            "cobertura_evidencia": cobertura_disc,
            "desempenho": atual_disc["desempenho"],
            "variacao": delta,
            "questoes": atual_disc["questoes"],
            "questoes_anteriores": anterior_disc["questoes"],
            "criticas": criticas_disc,
            "recorrentes": recorrentes_disc,
        }
        disciplinas.append(registro)

        if delta is not None and atual_disc["questoes"] >= 5 and anterior_disc["questoes"] >= 5:
            if maior_evolucao is None or delta > maior_evolucao["variacao"]:
                maior_evolucao = registro
            if maior_queda is None or delta < maior_queda["variacao"]:
                maior_queda = registro

    # Estado geral de preparação. É descritivo e não probabilístico.
    if dominio_medio is None and resumo["questoes"] < 5:
        preparacao = "Evidência insuficiente"
    elif (
        criticas_abertas >= 3
        or (dominio_medio is not None and dominio_medio < 50.0)
        or (resumo["desempenho"] is not None and resumo["questoes"] >= 10 and resumo["desempenho"] < 55.0)
    ):
        preparacao = "Atenção"
    elif (
        cobertura_evidencia < 35.0
        or (dominio_medio is not None and dominio_medio < 70.0)
        or (resumo["desempenho"] is not None and resumo["questoes"] >= 10 and resumo["desempenho"] < 70.0)
    ):
        preparacao = "Em construção"
    elif (
        dominio_medio is not None
        and dominio_medio >= 85.0
        and cobertura_evidencia >= 65.0
        and criticas_abertas == 0
        and recorrentes_abertas <= 2
        and (resumo["desempenho"] is None or resumo["desempenho"] >= 80.0)
    ):
        preparacao = "Forte"
    else:
        preparacao = "Boa"

    # Leitura de validações registradas nos Simulados Inteligentes V2.
    validacoes_simulado = []
    for criado_em, tipo, configuracao_json in simulados_linhas:
        try:
            config = json.loads(configuracao_json or "{}")
        except Exception:
            config = {}
        analise = config.get("analise_v2") or {}
        for item in analise.get("topicos") or []:
            categoria = str(item.get("categoria") or "")
            if categoria not in ("superestimado", "piorou"):
                continue
            validacoes_simulado.append({
                "categoria": categoria,
                "disciplina": item.get("disciplina") or "—",
                "topico": item.get("topico") or "—",
                "topico_id": item.get("topico_id"),
                "desempenho": item.get("desempenho"),
                "dominio_antes": item.get("dominio_antes"),
                "dominio_depois": item.get("dominio_depois"),
                "criado_em": criado_em,
                "tipo": tipo,
            })

    riscos = []
    vistos_risco = set()

    def adicionar_risco(nivel, titulo, detalhe, chave=None, topico_id=None):
        chave_final = chave or (titulo, detalhe)
        if chave_final in vistos_risco:
            return
        vistos_risco.add(chave_final)
        riscos.append({
            "nivel": nivel,
            "titulo": titulo,
            "detalhe": detalhe,
            "topico_id": topico_id,
        })

    for item in validacoes_simulado[:4]:
        desempenho = item.get("desempenho")
        texto_desempenho = (
            f"{float(desempenho):.0f}% no simulado"
            if desempenho is not None else "resultado fraco no simulado"
        )
        if item["categoria"] == "superestimado":
            titulo = "Domínio possivelmente superestimado"
            detalhe = f"{item['disciplina']} › {item['topico']} • {texto_desempenho}."
            nivel = "alto"
        else:
            titulo = "Queda confirmada em simulado"
            detalhe = f"{item['disciplina']} › {item['topico']} • {texto_desempenho}."
            nivel = "alto"
        adicionar_risco(nivel, titulo, detalhe, ("sim", item.get("topico_id"), item["categoria"]), item.get("topico_id"))

    if desempenho_delta is not None and desempenho_delta <= -5.0:
        adicionar_risco(
            "medio",
            "Desempenho em queda",
            f"O período caiu {abs(desempenho_delta):.1f} p.p. em relação ao período anterior.",
            "queda_periodo",
        )

    if cobertura_evidencia < 35.0 and total_topicos > 0:
        adicionar_risco(
            "medio",
            "Cobertura de evidência baixa",
            f"Apenas {topicos_com_evidencia} de {total_topicos} tópicos possuem respostas suficientes para compor o domínio.",
            "cobertura_evidencia",
        )

    for item in prioridades[:8]:
        if len(riscos) >= 6:
            break
        score = float(item.get("score_adaptativo") or 0.0)
        if score < 36.0:
            continue
        motivo = item.get("motivo_principal_chave")
        if motivo == "erros":
            nivel = "alto" if int(item.get("criticas") or 0) > 0 else "medio"
            titulo = "Erros ainda abertos"
        elif motivo == "recencia":
            nivel = "medio"
            titulo = "Retenção precisa ser testada"
        elif motivo in ("evidencia", "variedade"):
            nivel = "medio"
            titulo = "Evidência ainda insuficiente"
        elif motivo == "estabilidade":
            nivel = "medio"
            titulo = "Resultado instável"
        elif motivo == "urgencia":
            nivel = "medio"
            titulo = "Revisão exige atenção"
        else:
            nivel = "medio"
            titulo = "Domínio ainda frágil"
        adicionar_risco(
            nivel,
            titulo,
            f"{item['disciplina']} › {item['topico']} • {item.get('motivo_detalhado') or item.get('motivo_principal')}.",
            ("adapt", item.get("topico_id"), motivo),
            item.get("topico_id"),
        )

    if not riscos:
        adicionar_risco(
            "baixo",
            "Nenhum risco crítico identificado",
            "Os sinais atuais não apontam uma fragilidade dominante. Continue acumulando evidência e validando retenção.",
            "sem_risco",
        )

    # Recomendações. Primeiro entram discrepâncias observadas em simulado,
    # depois o ranking Adaptativo V2 completa a lista.
    acoes = []
    vistos_acao = set()

    def adicionar_acao(prioridade, titulo, detalhe, acao, topico_id=None, disciplina=None, topico=None):
        chave = topico_id if topico_id is not None else (titulo, detalhe)
        if chave in vistos_acao:
            return
        vistos_acao.add(chave)
        acoes.append({
            "prioridade": float(prioridade),
            "titulo": titulo,
            "detalhe": detalhe,
            "acao": acao,
            "topico_id": topico_id,
            "disciplina": disciplina,
            "topico": topico,
        })

    for item in validacoes_simulado[:3]:
        adicionar_acao(
            110.0 if item["categoria"] == "superestimado" else 105.0,
            f"Revalidar {item['disciplina']} › {item['topico']}",
            "O simulado apresentou desempenho incompatível com o domínio esperado.",
            "Fazer treino adaptativo e depois um novo teste de retenção.",
            item.get("topico_id"),
            item.get("disciplina"),
            item.get("topico"),
        )

    mapa_acao = {
        "erros": ("Corrigir fragilidade", "Fazer treino adaptativo com foco em erros recorrentes e recuperação."),
        "evidencia": ("Ampliar evidência", "Resolver mais questões, priorizando itens inéditos."),
        "variedade": ("Aumentar variedade", "Resolver questões diferentes do mesmo tópico antes de elevar a confiança do domínio."),
        "estabilidade": ("Estabilizar desempenho", "Fazer uma sessão curta de controle e comparar o resultado com tentativas recentes."),
        "recencia": ("Testar retenção", "Resolver uma amostra sem revisão prévia para verificar retenção real."),
        "urgencia": ("Executar revisão", "Realizar a revisão pendente e validar com algumas questões."),
        "dominio": ("Fortalecer domínio", "Fazer treino adaptativo até reduzir a fragilidade do tópico."),
        "importancia": ("Priorizar no ciclo", "Manter o tópico entre as próximas sessões por sua importância no perfil."),
    }

    for item in prioridades:
        if len(acoes) >= 5:
            break
        chave = item.get("motivo_principal_chave") or "dominio"
        titulo_acao, texto_acao = mapa_acao.get(chave, mapa_acao["dominio"])
        adicionar_acao(
            item.get("score_adaptativo") or 0.0,
            f"{titulo_acao}: {item['disciplina']} › {item['topico']}",
            item.get("motivo_detalhado") or item.get("motivo_principal") or "Prioridade adaptativa elevada.",
            texto_acao,
            item.get("topico_id"),
            item.get("disciplina"),
            item.get("topico"),
        )

    if not acoes:
        adicionar_acao(
            0.0,
            "Manter o ciclo atual",
            "Não há uma prioridade dominante com os dados disponíveis.",
            "Continue estudando e acumulando respostas para melhorar a precisão das recomendações.",
        )

    acoes.sort(key=lambda item: -item["prioridade"])
    acoes = acoes[:5]

    # Ordena riscos por severidade e conserva no máximo seis.
    ordem_nivel = {"alto": 0, "medio": 1, "baixo": 2}
    riscos.sort(key=lambda item: ordem_nivel.get(item["nivel"], 9))
    riscos = riscos[:6]

    disciplinas.sort(
        key=lambda item: (
            {"Atenção": 0, "Em construção": 1, "Evidência insuficiente": 2, "Boa": 3, "Forte": 4}.get(item["preparacao"], 9),
            item["dominio"] is None,
            item["dominio"] if item["dominio"] is not None else 999.0,
            item["disciplina"].lower(),
        )
    )

    return {
        "versao": "relatorio_estrategico_v1",
        "periodo": {
            "inicio": inicio.isoformat(),
            "fim": fim.isoformat(),
            "dias": dias,
            "inicio_anterior": inicio_anterior.isoformat(),
            "fim_anterior": fim_anterior.isoformat(),
        },
        "situacao": {
            "preparacao": preparacao,
            "dominio_medio": dominio_medio,
            "desempenho": resumo["desempenho"],
            "questoes": resumo["questoes"],
            "dias_ativos": resumo["dias_ativos"],
            "total_topicos": total_topicos,
            "topicos_com_evidencia": topicos_com_evidencia,
            "cobertura_evidencia": cobertura_evidencia,
            "criticas_abertas": criticas_abertas,
            "recorrentes_abertas": recorrentes_abertas,
            "em_recuperacao": recuperacao_aberta,
            "recuperadas": recuperadas,
        },
        "evolucao": {
            "desempenho_delta": desempenho_delta,
            "questoes_delta": questoes_delta,
            "dias_ativos_delta": dias_ativos_delta,
            "resumo_anterior": resumo_anterior,
            "maior_evolucao": maior_evolucao,
            "maior_queda": maior_queda,
        },
        "disciplinas": disciplinas,
        "riscos": riscos,
        "acoes": acoes,
        "simulados_validacoes": validacoes_simulado,
    }


def obter_relatorio_periodo(
    data_inicio,
    data_fim,
    concurso_id=None
):
    """
    Resume apenas revisões detalhadas registradas no programa
    dentro do período informado e do perfil de concurso ativo.
    """

    if concurso_id is None:
        concurso_id = (
            obter_concurso_ativo()[0]
        )

    with conectar() as conexao:
        linha = conexao.execute(
            """
            SELECT
                COUNT(*) AS revisoes,
                COALESCE(
                    SUM(r.questoes),
                    0
                ) AS questoes,
                COALESCE(
                    SUM(r.acertos),
                    0
                ) AS acertos,
                COUNT(
                    DISTINCT r.topico_id
                ) AS topicos,
                COUNT(
                    DISTINCT d.id
                ) AS disciplinas
            FROM revisoes r
            JOIN topicos t
                ON t.id = r.topico_id
            JOIN disciplinas d
                ON d.id = t.disciplina_id
            JOIN disciplina_concurso_inclusao dc
                ON dc.disciplina_id = d.id
                AND dc.concurso_id = ?
                AND dc.incluido = 1
                AND COALESCE(dc.pausado, 0) = 0
            JOIN topico_concurso_importancia tc
                ON tc.topico_id = t.id
                AND tc.concurso_id = ?
                AND tc.incluido = 1
            WHERE
                r.data >= ?
                AND r.data <= ?
            """,
            (
                concurso_id,
                concurso_id,
                data_inicio,
                data_fim
            )
        ).fetchone()

        revisoes = int(
            linha[0] or 0
        )
        questoes = int(
            linha[1] or 0
        )
        acertos = int(
            linha[2] or 0
        )
        topicos = int(
            linha[3] or 0
        )
        disciplinas = int(
            linha[4] or 0
        )

        percentual = (
            round(
                100.0
                * acertos
                / questoes,
                1
            )
            if questoes > 0
            else None
        )

        return {
            "revisoes": revisoes,
            "questoes": questoes,
            "acertos": acertos,
            "percentual": percentual,
            "topicos": topicos,
            "disciplinas": disciplinas
        }


def obter_relatorio_disciplinas_periodo(
    data_inicio,
    data_fim,
    concurso_id=None
):
    if concurso_id is None:
        concurso_id = (
            obter_concurso_ativo()[0]
        )

    with conectar() as conexao:
        return conexao.execute(
            """
            SELECT
                d.nome,
                COUNT(*) AS revisoes,
                COALESCE(
                    SUM(r.questoes),
                    0
                ) AS questoes,
                COALESCE(
                    SUM(r.acertos),
                    0
                ) AS acertos,
                CASE
                    WHEN SUM(r.questoes) > 0
                    THEN ROUND(
                        100.0
                        * SUM(r.acertos)
                        / SUM(r.questoes),
                        1
                    )
                    ELSE NULL
                END AS percentual,
                COUNT(
                    DISTINCT r.topico_id
                ) AS topicos
            FROM revisoes r
            JOIN topicos t
                ON t.id = r.topico_id
            JOIN disciplinas d
                ON d.id = t.disciplina_id
            JOIN disciplina_concurso_inclusao dc
                ON dc.disciplina_id = d.id
                AND dc.concurso_id = ?
                AND dc.incluido = 1
                AND COALESCE(dc.pausado, 0) = 0
            JOIN topico_concurso_importancia tc
                ON tc.topico_id = t.id
                AND tc.concurso_id = ?
                AND tc.incluido = 1
            WHERE
                r.data >= ?
                AND r.data <= ?
            GROUP BY
                d.id,
                d.nome
            ORDER BY
                percentual ASC,
                questoes DESC,
                d.nome COLLATE NOCASE
            """,
            (
                concurso_id,
                concurso_id,
                data_inicio,
                data_fim
            )
        ).fetchall()


def obter_relatorio_topicos_periodo(
    data_inicio,
    data_fim,
    concurso_id=None
):
    if concurso_id is None:
        concurso_id = (
            obter_concurso_ativo()[0]
        )

    with conectar() as conexao:
        return conexao.execute(
            """
            SELECT
                t.id,
                d.nome,
                t.nome,
                COUNT(*) AS revisoes,
                COALESCE(
                    SUM(r.questoes),
                    0
                ) AS questoes,
                COALESCE(
                    SUM(r.acertos),
                    0
                ) AS acertos,
                CASE
                    WHEN SUM(r.questoes) > 0
                    THEN ROUND(
                        100.0
                        * SUM(r.acertos)
                        / SUM(r.questoes),
                        1
                    )
                    ELSE NULL
                END AS percentual,
                MIN(r.data) AS primeira_no_periodo,
                MAX(r.data) AS ultima_no_periodo
            FROM revisoes r
            JOIN topicos t
                ON t.id = r.topico_id
            JOIN disciplinas d
                ON d.id = t.disciplina_id
            JOIN disciplina_concurso_inclusao dc
                ON dc.disciplina_id = d.id
                AND dc.concurso_id = ?
                AND dc.incluido = 1
                AND COALESCE(dc.pausado, 0) = 0
            JOIN topico_concurso_importancia tc
                ON tc.topico_id = t.id
                AND tc.concurso_id = ?
                AND tc.incluido = 1
            WHERE
                r.data >= ?
                AND r.data <= ?
            GROUP BY
                t.id,
                d.nome,
                t.nome
            ORDER BY
                percentual ASC,
                questoes DESC,
                d.nome COLLATE NOCASE,
                t.nome COLLATE NOCASE
            """,
            (
                concurso_id,
                concurso_id,
                data_inicio,
                data_fim
            )
        ).fetchall()


def obter_relatorio_diario_periodo(
    data_inicio,
    data_fim,
    concurso_id=None
):
    if concurso_id is None:
        concurso_id = (
            obter_concurso_ativo()[0]
        )

    with conectar() as conexao:
        return conexao.execute(
            """
            SELECT
                r.data,
                COUNT(*) AS revisoes,
                COALESCE(
                    SUM(r.questoes),
                    0
                ) AS questoes,
                COALESCE(
                    SUM(r.acertos),
                    0
                ) AS acertos,
                CASE
                    WHEN SUM(r.questoes) > 0
                    THEN ROUND(
                        100.0
                        * SUM(r.acertos)
                        / SUM(r.questoes),
                        1
                    )
                    ELSE NULL
                END AS percentual
            FROM revisoes r
            JOIN topicos t
                ON t.id = r.topico_id
            JOIN disciplinas d
                ON d.id = t.disciplina_id
            JOIN disciplina_concurso_inclusao dc
                ON dc.disciplina_id = d.id
                AND dc.concurso_id = ?
                AND dc.incluido = 1
                AND COALESCE(dc.pausado, 0) = 0
            JOIN topico_concurso_importancia tc
                ON tc.topico_id = t.id
                AND tc.concurso_id = ?
                AND tc.incluido = 1
            WHERE
                r.data >= ?
                AND r.data <= ?
            GROUP BY
                r.data
            ORDER BY
                r.data ASC
            """,
            (
                concurso_id,
                concurso_id,
                data_inicio,
                data_fim
            )
        ).fetchall()

# ==========================================================
# PLANO DE AÇÃO AUTOMÁTICO V1
# ==========================================================


def _normalizar_carga_plano_acao(carga):
    valor = str(carga or "moderada").strip().lower()
    mapa = {
        "leve": "leve",
        "light": "leve",
        "moderada": "moderada",
        "moderado": "moderada",
        "medium": "moderada",
        "intensa": "intensa",
        "intenso": "intensa",
        "high": "intensa",
    }
    return mapa.get(valor, "moderada")


def _recalcular_resumo_plano_acao(plano):
    itens = list(plano.get("itens") or [])
    datas = sorted({str(item.get("data") or "") for item in itens if item.get("data")})
    return {
        "acoes": len(itens),
        "questoes": sum(int(item.get("questoes") or 0) for item in itens),
        "revisoes": sum(int(item.get("quantidade_revisoes") or 0) for item in itens),
        "dias_com_acao": len(datas),
        "simulados": sum(1 for item in itens if item.get("tipo") == "Simulado"),
    }


def _candidato_plano_por_prioridade(item, questoes_base):
    chave = str(item.get("motivo_principal_chave") or "dominio")
    disciplina = item.get("disciplina") or "—"
    topico = item.get("topico") or "—"
    topico_id = item.get("topico_id")
    detalhe = item.get("motivo_detalhado") or item.get("motivo_principal") or "Prioridade adaptativa relevante."

    mapa = {
        "erros": (
            "Treino adaptativo",
            "Corrigir fragilidade",
            "Focar em erros recorrentes e recuperação.",
            questoes_base,
        ),
        "evidencia": (
            "Questões",
            "Ampliar evidência",
            "Resolver questões, priorizando itens inéditos.",
            questoes_base,
        ),
        "variedade": (
            "Questões",
            "Aumentar variedade",
            "Resolver questões diferentes do mesmo tópico.",
            questoes_base,
        ),
        "estabilidade": (
            "Sessão de controle",
            "Estabilizar desempenho",
            "Fazer uma sessão curta de controle sem revisão imediata antes.",
            max(8, questoes_base - 3),
        ),
        "recencia": (
            "Teste de retenção",
            "Testar retenção",
            "Resolver uma amostra sem revisão prévia para verificar retenção real.",
            max(8, questoes_base - 3),
        ),
        "urgencia": (
            "Revisão",
            "Executar revisão",
            "Realizar a revisão pendente e validar com algumas questões.",
            0,
        ),
        "importancia": (
            "Treino adaptativo",
            "Priorizar no ciclo",
            "Manter o tópico entre as próximas sessões por sua importância.",
            questoes_base,
        ),
    }
    tipo, prefixo, acao, qtd = mapa.get(
        chave,
        (
            "Treino adaptativo",
            "Fortalecer domínio",
            "Fazer treino adaptativo até reduzir a fragilidade do tópico.",
            questoes_base,
        ),
    )

    return {
        "tipo": tipo,
        "titulo": f"{prefixo}: {disciplina} › {topico}",
        "detalhe": detalhe,
        "acao": acao,
        "topico_id": int(topico_id) if topico_id is not None else None,
        "disciplina": disciplina,
        "topico": topico,
        "questoes": int(qtd),
        "quantidade_revisoes": 1 if tipo == "Revisão" else 0,
        "prioridade": float(item.get("score_adaptativo") or 0.0),
        "origem": "adaptativo_v2",
        "fixa": False,
        "motivo_chave": chave,
    }


def gerar_plano_acao_automatico(
    concurso_id=None,
    data_inicio=None,
    carga="moderada",
    horizonte=7,
    variacao=0,
):
    """
    Plano de Ação Automático V2.

    Transforma sinais dos Relatórios Estratégicos, Domínio V2, Seleção
    Adaptativa V2, revisões e tempo real do Modo Foco em uma agenda explicável.
    Não altera revisões nem cria sessões automaticamente: é um plano de ação.
    """

    if concurso_id is None:
        concurso_id = obter_concurso_ativo()[0]
    concurso_id = int(concurso_id)

    if data_inicio is None:
        inicio = date.today()
    elif isinstance(data_inicio, date):
        inicio = data_inicio
    else:
        inicio = date.fromisoformat(str(data_inicio)[:10])

    horizonte = max(3, min(14, int(horizonte or 7)))
    fim = inicio + timedelta(days=horizonte - 1)
    carga = _normalizar_carga_plano_acao(carga)
    variacao = max(0, int(variacao or 0))

    config_carga = {
        "leve": {"fator": 0.65, "max_acoes": 2, "dias_padrao": 5, "simulado": 0},
        "moderada": {"fator": 1.0, "max_acoes": 3, "dias_padrao": 6, "simulado": 20},
        "intensa": {"fator": 1.30, "max_acoes": 4, "dias_padrao": 7, "simulado": 30},
    }[carga]

    meta_diaria = max(0, obter_configuracao_int("meta_questoes_diaria", 60))
    if meta_diaria <= 0:
        meta_diaria = 60
    meta_semanal = max(0, obter_configuracao_int("meta_questoes_semanal", 0))
    dias_meta = max(0, min(7, obter_configuracao_int("meta_dias_estudo_semanal", 0)))

    dias_estudo_alvo = dias_meta if dias_meta > 0 else config_carga["dias_padrao"]
    dias_estudo_alvo = max(1, min(horizonte, dias_estudo_alvo))

    if meta_semanal > 0:
        referencia_diaria = max(10, round(meta_semanal / max(1, dias_estudo_alvo)))
    else:
        referencia_diaria = meta_diaria

    alvo_questoes_dia = max(15, round(referencia_diaria * config_carga["fator"]))
    questoes_base = max(
        8,
        min(
            30,
            round(alvo_questoes_dia / max(1, config_carga["max_acoes"])),
        ),
    )

    datas = [inicio + timedelta(days=i) for i in range(horizonte)]

    # Escolhe dias de estudo distribuídos ao longo da janela.
    if dias_estudo_alvo >= horizonte:
        datas_estudo = list(datas)
    elif dias_estudo_alvo == 1:
        datas_estudo = [datas[0]]
    else:
        indices = []
        for i in range(dias_estudo_alvo):
            pos = round(i * (horizonte - 1) / (dias_estudo_alvo - 1))
            if pos not in indices:
                indices.append(pos)
        while len(indices) < dias_estudo_alvo:
            for pos in range(horizonte):
                if pos not in indices:
                    indices.append(pos)
                    if len(indices) >= dias_estudo_alvo:
                        break
        datas_estudo = [datas[i] for i in sorted(indices[:dias_estudo_alvo])]

    itens = []
    ocupacao = {d.isoformat(): 0 for d in datas}
    questoes_por_dia = {d.isoformat(): 0 for d in datas}

    def adicionar_item(item, data_item, fixa=False):
        data_txt = data_item.isoformat() if isinstance(data_item, date) else str(data_item)[:10]
        novo = dict(item)
        novo["data"] = data_txt
        novo["fixa"] = bool(fixa or novo.get("fixa"))
        novo["ordem"] = len(itens) + 1
        itens.append(novo)
        ocupacao[data_txt] = ocupacao.get(data_txt, 0) + 1
        questoes_por_dia[data_txt] = questoes_por_dia.get(data_txt, 0) + int(novo.get("questoes") or 0)

    # 1) Revisões vencidas e de hoje: ficam no primeiro dia e são agrupadas.
    pendentes = listar_pendencias(inicio.isoformat(), concurso_id)
    if pendentes:
        nomes = [f"{row[1]} › {row[2]}" for row in pendentes]
        detalhe = "; ".join(nomes[:4])
        if len(nomes) > 4:
            detalhe += f"; +{len(nomes) - 4} tópico(s)"
        adicionar_item({
            "tipo": "Revisão",
            "titulo": f"Revisões pendentes ({len(pendentes)})",
            "detalhe": detalhe,
            "acao": "Regularizar as revisões vencidas ou previstas para hoje.",
            "topico_id": None,
            "disciplina": "Várias",
            "topico": "Revisões pendentes",
            "questoes": 0,
            "quantidade_revisoes": len(pendentes),
            "prioridade": 120.0,
            "origem": "agenda_revisoes",
            "motivo_chave": "revisao_pendente",
        }, inicio, fixa=True)

    # 2) Revisões futuras: uma ação agrupada por data prevista.
    futuras = listar_revisoes_agendadas_periodo(
        (inicio + timedelta(days=1)).isoformat(),
        fim.isoformat(),
        concurso_id,
    )
    por_data = {}
    for row in futuras:
        por_data.setdefault(str(row[4]), []).append(row)
    for data_txt, rows in sorted(por_data.items()):
        try:
            dia = date.fromisoformat(data_txt[:10])
        except Exception:
            continue
        nomes = [f"{row[1]} › {row[2]}" for row in rows]
        detalhe = "; ".join(nomes[:4])
        if len(nomes) > 4:
            detalhe += f"; +{len(nomes) - 4} tópico(s)"
        adicionar_item({
            "tipo": "Revisão",
            "titulo": f"Revisões programadas ({len(rows)})",
            "detalhe": detalhe,
            "acao": "Executar as revisões previstas e validar a retenção.",
            "topico_id": None,
            "disciplina": "Várias" if len(rows) > 1 else rows[0][1],
            "topico": "Revisões programadas" if len(rows) > 1 else rows[0][2],
            "questoes": 0,
            "quantidade_revisoes": len(rows),
            "prioridade": 100.0,
            "origem": "agenda_revisoes",
            "motivo_chave": "revisao_programada",
        }, dia, fixa=True)

    # Relatório usa os últimos 30 dias para orientar a semana seguinte.
    periodo_fim = inicio
    periodo_inicio = inicio - timedelta(days=29)
    relatorio = obter_relatorio_estrategico(
        periodo_inicio.isoformat(),
        periodo_fim.isoformat(),
        concurso_id,
    )
    prioridades = obter_prioridades_sessao_adaptativa(concurso_id)

    candidatos = []
    usados_topico = set()

    # Discrepâncias/ações estratégicas vêm primeiro.
    for acao in relatorio.get("acoes") or []:
        topico_id = acao.get("topico_id")
        # A recomendação genérica "manter o ciclo" do relatório serve como
        # estado vazio e não deve virar uma tarefa artificial no plano.
        if topico_id is None and not acao.get("disciplina") and not acao.get("topico"):
            continue
        titulo = str(acao.get("titulo") or "Ação estratégica")
        titulo_lower = titulo.lower()
        if "revalidar" in titulo_lower:
            tipo = "Treino adaptativo"
            prefixo = "Revalidar domínio"
            qtd = questoes_base
        elif "testar retenção" in titulo_lower:
            tipo = "Teste de retenção"
            prefixo = "Testar retenção"
            qtd = max(8, questoes_base - 3)
        elif "executar revisão" in titulo_lower:
            tipo = "Revisão"
            prefixo = "Executar revisão"
            qtd = 0
        elif "evidência" in titulo_lower or "variedade" in titulo_lower:
            tipo = "Questões"
            prefixo = "Ampliar evidência"
            qtd = questoes_base
        elif "estabilizar" in titulo_lower:
            tipo = "Sessão de controle"
            prefixo = "Estabilizar desempenho"
            qtd = max(8, questoes_base - 3)
        else:
            tipo = "Treino adaptativo"
            prefixo = "Fortalecer domínio"
            qtd = questoes_base
        candidatos.append({
            "tipo": tipo,
            "titulo": f"{prefixo}: {acao.get('disciplina') or '—'} › {acao.get('topico') or '—'}",
            "detalhe": acao.get("detalhe") or "Prioridade identificada pelo Relatório Estratégico.",
            "acao": acao.get("acao") or "Executar a ação recomendada.",
            "topico_id": int(topico_id) if topico_id is not None else None,
            "disciplina": acao.get("disciplina") or "—",
            "topico": acao.get("topico") or "—",
            "questoes": int(qtd),
            "quantidade_revisoes": 1 if tipo == "Revisão" else 0,
            "prioridade": float(acao.get("prioridade") or 0.0) + 25.0,
            "origem": "relatorio_estrategico_v1",
            "fixa": False,
            "motivo_chave": "estrategico",
        })
        if topico_id is not None:
            usados_topico.add(int(topico_id))

    # O ranking Adaptativo V2 completa o pool e fornece reservas.
    for item in prioridades[:20]:
        tid = item.get("topico_id")
        if tid is not None and int(tid) in usados_topico:
            continue
        candidatos.append(_candidato_plano_por_prioridade(item, questoes_base))
        if tid is not None:
            usados_topico.add(int(tid))

    # V2: o plano também observa o tempo REAL do Modo Foco. Isso não muda
    # datas de revisões fixas; apenas reordena o pool flexível para reduzir
    # concentração excessiva e favorecer matérias pouco trabalhadas.
    try:
        resumo_foco = obter_resumo_foco(inicio)
        distribuicao_foco = {
            str(item.get("disciplina") or ""): float(item.get("percentual") or 0.0)
            for item in (resumo_foco.get("distribuicao_semana") or [])
        }
        recentes_foco = listar_sessoes_foco(6)
    except Exception:
        resumo_foco = {}
        distribuicao_foco = {}
        recentes_foco = []

    ultimas_disciplinas = [
        str(item.get("disciplina") or "").strip()
        for item in recentes_foco[:3]
        if str(item.get("disciplina") or "").strip()
    ]
    topicos_foco_recentes = {
        int(item.get("topico_id"))
        for item in recentes_foco[:8]
        if item.get("topico_id") not in (None, "")
    }
    total_foco_semana = int(resumo_foco.get("semana_segundos") or 0)

    for candidato in candidatos:
        disciplina = str(candidato.get("disciplina") or "").strip()
        original = float(candidato.get("prioridade") or 0.0)
        ajuste = 0.0
        percentual = float(distribuicao_foco.get(disciplina, 0.0) or 0.0)
        repeticoes = sum(1 for nome in ultimas_disciplinas if nome == disciplina)
        if ultimas_disciplinas and ultimas_disciplinas[0] == disciplina:
            ajuste -= 8.0
        if repeticoes > 1:
            ajuste -= 3.0 * (repeticoes - 1)
        if percentual >= 50.0:
            ajuste -= 7.0
        elif total_foco_semana > 0 and percentual <= 15.0:
            ajuste += 4.0
        tid = candidato.get("topico_id")
        if tid not in (None, "") and int(tid) in topicos_foco_recentes:
            ajuste -= 12.0
            candidato["foco_recente_no_topico"] = True
        candidato["prioridade_original"] = original
        candidato["ajuste_ritmo_foco"] = ajuste
        candidato["prioridade"] = original + ajuste
        if ajuste != 0:
            candidato["ritmo_foco_semana_percentual"] = percentual

    candidatos.sort(
        key=lambda item: (
            -float(item.get("prioridade") or 0.0),
            str(item.get("disciplina") or "").lower(),
            str(item.get("topico") or "").lower(),
        )
    )

    # Rotação controlada para "Regenerar" oferecer variação sem aleatoriedade opaca.
    if candidatos and variacao:
        deslocamento = variacao % len(candidatos)
        candidatos = candidatos[deslocamento:] + candidatos[:deslocamento]

    # Evita sobrepor uma ação adaptativa ao mesmo tópico quando ele já está
    # explicitamente em uma revisão individual. Ações agrupadas não bloqueiam.
    capacidade_total = max(
        1,
        dias_estudo_alvo * config_carga["max_acoes"] - len(itens),
    )
    selecionados = candidatos[:max(3, capacidade_total)]
    reservas = candidatos[max(3, capacidade_total):]

    def melhor_data_flexivel(item):
        # Prioriza os dias escolhidos para estudo, balanceando nº de ações e questões.
        candidatas = list(datas_estudo)
        if not candidatas:
            candidatas = list(datas)
        # Treino/sessão na data inicial é permitido; simulado será tratado depois.
        return min(
            candidatas,
            key=lambda d: (
                ocupacao.get(d.isoformat(), 0) >= config_carga["max_acoes"],
                ocupacao.get(d.isoformat(), 0),
                questoes_por_dia.get(d.isoformat(), 0),
                d,
            ),
        )

    for item in selecionados:
        if len(itens) >= dias_estudo_alvo * config_carga["max_acoes"] + len(por_data) + (1 if pendentes else 0):
            break
        adicionar_item(item, melhor_data_flexivel(item), fixa=False)

    # Simulado de validação: só em cargas moderada/intensa e com banco suficiente.
    stats_questoes = obter_estatisticas_banco_questoes(concurso_id)
    qtd_simulado = int(config_carga["simulado"] or 0)
    if qtd_simulado > 0 and int(stats_questoes.get("total") or 0) >= qtd_simulado:
        # Usa um dia tardio e preferencialmente menos carregado.
        ultimos = datas_estudo[max(0, len(datas_estudo)//2):] or datas_estudo or datas
        dia_sim = min(
            ultimos,
            key=lambda d: (
                ocupacao.get(d.isoformat(), 0),
                questoes_por_dia.get(d.isoformat(), 0),
                -d.toordinal(),
            ),
        )
        adicionar_item({
            "tipo": "Simulado",
            "titulo": f"Simulado de validação ({qtd_simulado} questões)",
            "detalhe": "Medir o desempenho sem correção imediata e confrontar o resultado com o Domínio V2.",
            "acao": "Fazer um Simulado Inteligente V2 em modo equilibrado ou prova real.",
            "topico_id": None,
            "disciplina": "Geral",
            "topico": "Simulado",
            "questoes": qtd_simulado,
            "quantidade_revisoes": 0,
            "prioridade": 55.0,
            "origem": "plano_acao_v1",
            "fixa": False,
            "motivo_chave": "validacao",
        }, dia_sim, fixa=False)

    # Ordena cronologicamente e preserva prioridade dentro do dia.
    itens.sort(key=lambda item: (item.get("data") or "", -float(item.get("prioridade") or 0.0), item.get("titulo") or ""))
    for ordem, item in enumerate(itens, 1):
        item["ordem"] = ordem

    plano = {
        "versao": "plano_acao_automatico_v2",
        "concurso_id": concurso_id,
        "gerado_em": datetime.now().isoformat(timespec="seconds"),
        "inicio": inicio.isoformat(),
        "fim": fim.isoformat(),
        "horizonte": horizonte,
        "carga": carga,
        "variacao": variacao,
        "alvo_questoes_dia": alvo_questoes_dia,
        "dias_estudo_alvo": dias_estudo_alvo,
        "max_acoes_dia": config_carga["max_acoes"],
        "preparacao": (relatorio.get("situacao") or {}).get("preparacao"),
        "itens": itens,
        "reservas": reservas[:10],
        "criterios": [
            "revisões vencidas e programadas",
            "Relatório Estratégico V1",
            "Índice de Domínio V2",
            "Seleção Adaptativa V2",
            "metas diária/semanal configuradas",
            "tempo real do Modo Foco e rotação entre disciplinas",
            f"carga {carga}",
        ],
    }
    plano["resumo"] = _recalcular_resumo_plano_acao(plano)
    return plano


def redistribuir_plano_acao_automatico(plano):
    plano = json.loads(json.dumps(plano or {}, ensure_ascii=False))
    itens = list(plano.get("itens") or [])
    if not itens:
        plano["resumo"] = _recalcular_resumo_plano_acao(plano)
        return plano

    inicio = date.fromisoformat(str(plano.get("inicio"))[:10])
    horizonte = max(1, int(plano.get("horizonte") or 7))
    dias_alvo = max(1, min(horizonte, int(plano.get("dias_estudo_alvo") or horizonte)))
    datas = [inicio + timedelta(days=i) for i in range(horizonte)]
    if dias_alvo >= horizonte:
        datas_estudo = list(datas)
    else:
        indices = []
        for i in range(dias_alvo):
            pos = round(i * (horizonte - 1) / max(1, dias_alvo - 1))
            if pos not in indices:
                indices.append(pos)
        datas_estudo = [datas[i] for i in indices] or [datas[0]]

    ocupacao = {d.isoformat(): 0 for d in datas}
    questoes = {d.isoformat(): 0 for d in datas}

    # Fixas conservam a data.
    for item in itens:
        if not item.get("fixa"):
            continue
        dt = str(item.get("data") or inicio.isoformat())[:10]
        ocupacao[dt] = ocupacao.get(dt, 0) + 1
        questoes[dt] = questoes.get(dt, 0) + int(item.get("questoes") or 0)

    flexiveis = [item for item in itens if not item.get("fixa")]
    flexiveis.sort(key=lambda item: (-float(item.get("prioridade") or 0.0), -(int(item.get("questoes") or 0))))

    for item in flexiveis:
        candidatas = datas_estudo or datas
        # Simulados preferem a metade final da janela.
        if item.get("tipo") == "Simulado" and len(candidatas) > 2:
            candidatas = candidatas[len(candidatas)//2:]
        dia = min(
            candidatas,
            key=lambda d: (
                ocupacao.get(d.isoformat(), 0),
                questoes.get(d.isoformat(), 0),
                d,
            ),
        )
        dt = dia.isoformat()
        item["data"] = dt
        ocupacao[dt] = ocupacao.get(dt, 0) + 1
        questoes[dt] = questoes.get(dt, 0) + int(item.get("questoes") or 0)

    itens.sort(key=lambda item: (item.get("data") or "", -float(item.get("prioridade") or 0.0), item.get("titulo") or ""))
    for ordem, item in enumerate(itens, 1):
        item["ordem"] = ordem
    plano["itens"] = itens
    plano["resumo"] = _recalcular_resumo_plano_acao(plano)
    plano["redistribuido_em"] = datetime.now().isoformat(timespec="seconds")
    return plano


def substituir_atividade_plano_acao_automatico(plano, indice):
    plano = json.loads(json.dumps(plano or {}, ensure_ascii=False))
    itens = list(plano.get("itens") or [])
    reservas = list(plano.get("reservas") or [])
    indice = int(indice)
    if indice < 0 or indice >= len(itens):
        raise IndexError("Atividade inválida.")
    atual = itens[indice]
    if atual.get("fixa"):
        raise ValueError("Revisões vinculadas à agenda não são substituídas automaticamente.")
    if not reservas:
        # Regera uma reserva adicional alterando a rotação da semana.
        novo = gerar_plano_acao_automatico(
            plano.get("concurso_id"),
            plano.get("inicio"),
            plano.get("carga", "moderada"),
            plano.get("horizonte", 7),
            int(plano.get("variacao") or 0) + 1,
        )
        existentes = {
            (item.get("topico_id"), item.get("tipo"), item.get("titulo"))
            for item in itens
        }
        reservas = [
            item for item in (novo.get("itens") or []) + (novo.get("reservas") or [])
            if not item.get("fixa")
            and (item.get("topico_id"), item.get("tipo"), item.get("titulo")) not in existentes
        ]
    if not reservas:
        raise ValueError("Não há outra atividade relevante disponível para substituir esta ação.")

    substituta = dict(reservas.pop(0))
    data_original = atual.get("data")
    substituta["data"] = data_original
    substituta["fixa"] = False
    # A atividade removida vira reserva, mantendo possibilidade de desfazer por nova substituição.
    removida = dict(atual)
    removida.pop("data", None)
    removida["fixa"] = False
    reservas.append(removida)
    itens[indice] = substituta

    itens.sort(key=lambda item: (item.get("data") or "", -float(item.get("prioridade") or 0.0), item.get("titulo") or ""))
    for ordem, item in enumerate(itens, 1):
        item["ordem"] = ordem
    plano["itens"] = itens
    plano["reservas"] = reservas[:10]
    plano["resumo"] = _recalcular_resumo_plano_acao(plano)
    return plano


def _chave_plano_acao_automatico(concurso_id):
    return f"plano_acao_automatico_v1_{int(concurso_id)}"


def salvar_plano_acao_automatico(plano, indices=None, concurso_id=None):
    if concurso_id is None:
        concurso_id = (plano or {}).get("concurso_id") or obter_concurso_ativo()[0]
    concurso_id = int(concurso_id)
    plano_salvo = json.loads(json.dumps(plano or {}, ensure_ascii=False))
    itens = list(plano_salvo.get("itens") or [])
    if indices is not None:
        permitidos = {int(i) for i in indices}
        itens = [item for idx, item in enumerate(itens) if idx in permitidos]
    plano_salvo["itens"] = itens
    plano_salvo["concurso_id"] = concurso_id
    plano_salvo["aceito_em"] = datetime.now().isoformat(timespec="seconds")
    plano_salvo["ativo"] = True
    plano_salvo["resumo"] = _recalcular_resumo_plano_acao(plano_salvo)
    # Reservas são úteis apenas durante a edição do preview.
    plano_salvo.pop("reservas", None)
    definir_configuracao_texto(
        _chave_plano_acao_automatico(concurso_id),
        json.dumps(plano_salvo, ensure_ascii=False),
    )
    return plano_salvo


def obter_plano_acao_automatico(concurso_id=None):
    if concurso_id is None:
        concurso_id = obter_concurso_ativo()[0]
    concurso_id = int(concurso_id)
    bruto = obter_configuracao_texto(_chave_plano_acao_automatico(concurso_id), None)
    if not bruto:
        return None
    try:
        plano = json.loads(bruto)
    except Exception:
        return None
    if int(plano.get("concurso_id") or concurso_id) != concurso_id:
        return None
    pausados = listar_topicos_pausados_ids(concurso_id)
    if pausados:
        plano["itens"] = [
            item for item in list(plano.get("itens") or [])
            if item.get("topico_id") in (None, "")
            or int(item.get("topico_id")) not in pausados
        ]
    plano["resumo"] = _recalcular_resumo_plano_acao(plano)
    return plano


def excluir_plano_acao_automatico(concurso_id=None):
    if concurso_id is None:
        concurso_id = obter_concurso_ativo()[0]
    concurso_id = int(concurso_id)
    definir_configuracao_texto(_chave_plano_acao_automatico(concurso_id), "")

# ==========================================================
# PAUSA & DESAFIOS
# ==========================================================

_JOGOS_VALIDOS = {
    "chimpanze",
    "memoria",
    "sequencia",
    "quebra_cabeca",
}


def registrar_resultado_jogo(
    jogo,
    pontuacao=0,
    nivel=None,
    duracao_segundos=None,
    movimentos=None,
):
    jogo = str(jogo or "").strip().lower()
    if jogo not in _JOGOS_VALIDOS:
        raise ValueError("Jogo inválido.")

    def inteiro_ou_none(valor):
        if valor is None:
            return None
        try:
            return max(0, int(valor))
        except Exception:
            return None

    try:
        pontuacao = max(0, int(pontuacao or 0))
    except Exception:
        pontuacao = 0

    nivel = inteiro_ou_none(nivel)
    duracao_segundos = inteiro_ou_none(duracao_segundos)
    movimentos = inteiro_ou_none(movimentos)

    with conectar() as conexao:
        cursor = conexao.execute(
            """
            INSERT INTO jogos_resultados (
                jogo,
                pontuacao,
                nivel,
                duracao_segundos,
                movimentos
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                jogo,
                pontuacao,
                nivel,
                duracao_segundos,
                movimentos,
            ),
        )
        return cursor.lastrowid


def obter_recordes_jogos():
    resultado = {
        jogo: {
            "partidas": 0,
            "melhor_pontuacao": None,
            "melhor_nivel": None,
            "melhor_tempo": None,
            "melhor_movimentos": None,
            "ultimo_resultado": None,
        }
        for jogo in _JOGOS_VALIDOS
    }

    with conectar() as conexao:
        linhas = conexao.execute(
            """
            SELECT
                jogo,
                pontuacao,
                nivel,
                duracao_segundos,
                movimentos,
                criado_em
            FROM jogos_resultados
            ORDER BY criado_em DESC, id DESC
            """
        ).fetchall()

    for jogo, pontuacao, nivel, duracao, movimentos, criado_em in linhas:
        if jogo not in resultado:
            continue
        item = resultado[jogo]
        item["partidas"] += 1

        if item["ultimo_resultado"] is None:
            item["ultimo_resultado"] = criado_em

        if pontuacao is not None:
            pontuacao = int(pontuacao)
            atual = item["melhor_pontuacao"]
            item["melhor_pontuacao"] = pontuacao if atual is None else max(atual, pontuacao)

        if nivel is not None:
            nivel = int(nivel)
            atual = item["melhor_nivel"]
            item["melhor_nivel"] = nivel if atual is None else max(atual, nivel)

        if duracao is not None and int(duracao) >= 0:
            duracao = int(duracao)
            atual = item["melhor_tempo"]
            item["melhor_tempo"] = duracao if atual is None else min(atual, duracao)

        if movimentos is not None and int(movimentos) > 0:
            movimentos = int(movimentos)
            atual = item["melhor_movimentos"]
            item["melhor_movimentos"] = movimentos if atual is None else min(atual, movimentos)

    return resultado


def listar_resultados_jogos(jogo=None, limite=30):
    try:
        limite = max(1, min(200, int(limite)))
    except Exception:
        limite = 30

    parametros = []
    filtro = ""
    if jogo is not None:
        jogo = str(jogo or "").strip().lower()
        if jogo not in _JOGOS_VALIDOS:
            return []
        filtro = "WHERE jogo = ?"
        parametros.append(jogo)

    parametros.append(limite)

    with conectar() as conexao:
        linhas = conexao.execute(
            f"""
            SELECT
                id,
                jogo,
                pontuacao,
                nivel,
                duracao_segundos,
                movimentos,
                criado_em
            FROM jogos_resultados
            {filtro}
            ORDER BY criado_em DESC, id DESC
            LIMIT ?
            """,
            parametros,
        ).fetchall()

    return [
        {
            "id": linha[0],
            "jogo": linha[1],
            "pontuacao": linha[2],
            "nivel": linha[3],
            "duracao_segundos": linha[4],
            "movimentos": linha[5],
            "criado_em": linha[6],
        }
        for linha in linhas
    ]



# ==========================================================
# MODO FOCO
# ==========================================================

_TIPOS_ATIVIDADE_FOCO = (
    "Estudo livre",
    "Questões",
    "Treino adaptativo",
    "Teste de retenção",
    "Revisão",
    "Sessão de controle",
    "Leitura / teoria",
    "Resumo / anotações",
    "Simulado",
    "Outro",
)


def tipos_atividade_foco():
    return list(_TIPOS_ATIVIDADE_FOCO)


def registrar_sessao_foco(
    inicio,
    fim,
    duracao_planejada,
    duracao_efetiva,
    disciplina_id=None,
    topico_id=None,
    tipo_atividade="Estudo livre",
    concluida=False,
    observacao=None,
    disciplina_nome=None,
    topico_nome=None,
    meta_questoes=0,
    origem=None,
    plano_chave=None,
):
    inicio = str(inicio or "").strip()
    fim = str(fim or "").strip() or None
    if not inicio:
        raise ValueError("O início da sessão de foco é obrigatório.")

    try:
        duracao_planejada = max(0, int(duracao_planejada or 0))
    except Exception:
        duracao_planejada = 0
    try:
        duracao_efetiva = max(0, int(duracao_efetiva or 0))
    except Exception:
        duracao_efetiva = 0

    tipo_atividade = str(tipo_atividade or "Estudo livre").strip()
    if tipo_atividade not in _TIPOS_ATIVIDADE_FOCO:
        tipo_atividade = "Outro"

    disciplina_id = int(disciplina_id) if disciplina_id not in (None, "") else None
    topico_id = int(topico_id) if topico_id not in (None, "") else None
    observacao = str(observacao or "").strip() or None
    try:
        meta_questoes = max(0, int(meta_questoes or 0))
    except Exception:
        meta_questoes = 0
    origem = str(origem or "").strip() or None
    plano_chave = str(plano_chave or "").strip() or None

    with conectar() as conexao:
        if disciplina_id is not None and not disciplina_nome:
            linha = conexao.execute(
                "SELECT nome FROM disciplinas WHERE id = ?",
                (disciplina_id,),
            ).fetchone()
            disciplina_nome = linha[0] if linha else None

        if topico_id is not None and not topico_nome:
            linha = conexao.execute(
                """
                SELECT t.nome, d.id, d.nome
                FROM topicos t
                JOIN disciplinas d ON d.id = t.disciplina_id
                WHERE t.id = ?
                """,
                (topico_id,),
            ).fetchone()
            if linha:
                topico_nome = linha[0]
                if disciplina_id is None:
                    disciplina_id = linha[1]
                if not disciplina_nome:
                    disciplina_nome = linha[2]

        cursor = conexao.execute(
            """
            INSERT INTO sessoes_foco (
                inicio,
                fim,
                duracao_planejada,
                duracao_efetiva,
                disciplina_id,
                topico_id,
                disciplina_nome,
                topico_nome,
                tipo_atividade,
                concluida,
                observacao,
                meta_questoes,
                origem,
                plano_chave
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                inicio,
                fim,
                duracao_planejada,
                duracao_efetiva,
                disciplina_id,
                topico_id,
                str(disciplina_nome or "").strip() or None,
                str(topico_nome or "").strip() or None,
                tipo_atividade,
                1 if concluida else 0,
                observacao,
                meta_questoes,
                origem,
                plano_chave,
            ),
        )
        return cursor.lastrowid


def listar_sessoes_foco(limite=20):
    try:
        limite = max(1, min(200, int(limite)))
    except Exception:
        limite = 20

    with conectar() as conexao:
        linhas = conexao.execute(
            """
            SELECT
                id,
                inicio,
                fim,
                duracao_planejada,
                duracao_efetiva,
                disciplina_nome,
                topico_nome,
                tipo_atividade,
                concluida,
                observacao,
                meta_questoes,
                origem,
                plano_chave,
                disciplina_id,
                topico_id
            FROM sessoes_foco
            WHERE duracao_efetiva > 0
            ORDER BY inicio DESC, id DESC
            LIMIT ?
            """,
            (limite,),
        ).fetchall()

    return [
        {
            "id": row[0],
            "inicio": row[1],
            "fim": row[2],
            "duracao_planejada": int(row[3] or 0),
            "duracao_efetiva": int(row[4] or 0),
            "disciplina": row[5],
            "topico": row[6],
            "tipo_atividade": row[7],
            "concluida": bool(row[8]),
            "observacao": row[9],
            "meta_questoes": int(row[10] or 0),
            "origem": row[11],
            "plano_chave": row[12],
            "disciplina_id": row[13],
            "topico_id": row[14],
        }
        for row in linhas
    ]


def obter_resumo_foco(data_referencia=None):
    if data_referencia is None:
        referencia = date.today()
    elif isinstance(data_referencia, datetime):
        referencia = data_referencia.date()
    elif isinstance(data_referencia, date):
        referencia = data_referencia
    else:
        texto = str(data_referencia or "").strip()[:10]
        try:
            referencia = datetime.strptime(texto, "%Y-%m-%d").date()
        except Exception:
            referencia = date.today()

    inicio_semana = referencia - timedelta(days=referencia.weekday())
    fim_semana = inicio_semana + timedelta(days=6)
    hoje = referencia.isoformat()

    with conectar() as conexao:
        hoje_row = conexao.execute(
            """
            SELECT
                COALESCE(SUM(duracao_efetiva), 0),
                COUNT(*),
                COALESCE(SUM(CASE WHEN concluida = 1 THEN 1 ELSE 0 END), 0)
            FROM sessoes_foco
            WHERE substr(inicio, 1, 10) = ?
              AND duracao_efetiva > 0
            """,
            (hoje,),
        ).fetchone()

        semana_row = conexao.execute(
            """
            SELECT
                COALESCE(SUM(duracao_efetiva), 0),
                COUNT(*),
                COALESCE(SUM(CASE WHEN concluida = 1 THEN 1 ELSE 0 END), 0),
                COUNT(DISTINCT substr(inicio, 1, 10))
            FROM sessoes_foco
            WHERE substr(inicio, 1, 10) BETWEEN ? AND ?
              AND duracao_efetiva > 0
            """,
            (inicio_semana.isoformat(), fim_semana.isoformat()),
        ).fetchone()

        distribuicao_rows = conexao.execute(
            """
            SELECT
                CASE
                    WHEN disciplina_nome IS NULL OR trim(disciplina_nome) = ''
                    THEN 'Livre / outros'
                    ELSE disciplina_nome
                END AS grupo,
                COALESCE(SUM(duracao_efetiva), 0) AS segundos,
                COUNT(*) AS sessoes
            FROM sessoes_foco
            WHERE substr(inicio, 1, 10) BETWEEN ? AND ?
              AND duracao_efetiva > 0
            GROUP BY grupo
            ORDER BY segundos DESC, grupo COLLATE NOCASE
            """,
            (inicio_semana.isoformat(), fim_semana.isoformat()),
        ).fetchall()

        total_row = conexao.execute(
            """
            SELECT COALESCE(SUM(duracao_efetiva), 0), COUNT(*)
            FROM sessoes_foco
            WHERE duracao_efetiva > 0
            """
        ).fetchone()

    hoje_segundos = int(hoje_row[0] or 0)
    hoje_sessoes = int(hoje_row[1] or 0)
    semana_segundos = int(semana_row[0] or 0)
    semana_sessoes = int(semana_row[1] or 0)

    distribuicao_semana = []
    for nome, segundos, sessoes in distribuicao_rows:
        segundos = int(segundos or 0)
        distribuicao_semana.append({
            "disciplina": str(nome or "Livre / outros"),
            "segundos": segundos,
            "sessoes": int(sessoes or 0),
            "percentual": (
                round(100.0 * segundos / semana_segundos, 1)
                if semana_segundos > 0
                else 0.0
            ),
        })

    return {
        "data": hoje,
        "inicio_semana": inicio_semana.isoformat(),
        "fim_semana": fim_semana.isoformat(),
        "hoje_segundos": hoje_segundos,
        "hoje_sessoes": hoje_sessoes,
        "hoje_concluidas": int(hoje_row[2] or 0),
        "semana_segundos": semana_segundos,
        "semana_sessoes": semana_sessoes,
        "semana_concluidas": int(semana_row[2] or 0),
        "dias_com_foco_semana": int(semana_row[3] or 0),
        "media_sessao_semana": (
            int(round(semana_segundos / semana_sessoes))
            if semana_sessoes > 0 else 0
        ),
        "distribuicao_semana": distribuicao_semana,
        "total_segundos": int(total_row[0] or 0),
        "total_sessoes": int(total_row[1] or 0),
    }



def registrar_vinculo_foco_questoes(sessao_foco_id, sessao_questoes_id):
    sessao_foco_id = int(sessao_foco_id)
    sessao_questoes_id = int(sessao_questoes_id)
    with conectar() as conexao:
        foco = conexao.execute(
            "SELECT 1 FROM sessoes_foco WHERE id = ?",
            (sessao_foco_id,),
        ).fetchone()
        questoes = conexao.execute(
            "SELECT 1 FROM sessoes_questoes WHERE id = ?",
            (sessao_questoes_id,),
        ).fetchone()
        if foco is None or questoes is None:
            return False
        conexao.execute(
            """
            INSERT OR IGNORE INTO foco_questoes (sessao_foco_id, sessao_questoes_id)
            VALUES (?, ?)
            """,
            (sessao_foco_id, sessao_questoes_id),
        )
    return True


def obter_resultado_foco_questoes(sessao_foco_id):
    """Agrega as baterias de questões executadas durante uma sessão de Foco."""
    sessao_foco_id = int(sessao_foco_id)
    with conectar() as conexao:
        linhas = conexao.execute(
            """
            SELECT
                fq.sessao_questoes_id,
                es.dominio_medio_antes,
                es.dominio_medio_depois,
                es.cobertura_media_antes,
                es.cobertura_media_depois,
                es.tempo_segundos
            FROM foco_questoes fq
            LEFT JOIN efetividade_sessoes es
                ON es.sessao_id = fq.sessao_questoes_id
            WHERE fq.sessao_foco_id = ?
            ORDER BY fq.criado_em, fq.sessao_questoes_id
            """,
            (sessao_foco_id,),
        ).fetchall()

    if not linhas:
        return None

    resumos = []
    antes = []
    depois = []
    cobertura_antes = []
    cobertura_depois = []
    tempo_questoes = 0
    for linha in linhas:
        resumo = obter_resumo_sessao_questoes(linha[0])
        if resumo:
            resumos.append(resumo)
        if linha[1] is not None:
            antes.append(float(linha[1]))
        if linha[2] is not None:
            depois.append(float(linha[2]))
        if linha[3] is not None:
            cobertura_antes.append(float(linha[3]))
        if linha[4] is not None:
            cobertura_depois.append(float(linha[4]))
        tempo_questoes += int(linha[5] or 0)

    respondidas = sum(int(item.get("respondidas") or 0) for item in resumos)
    acertos = sum(int(item.get("acertos") or 0) for item in resumos)
    erros = sum(int(item.get("erros") or 0) for item in resumos)
    puladas = sum(int(item.get("puladas") or 0) for item in resumos)
    desempenho = (100.0 * acertos / respondidas) if respondidas > 0 else None
    dominio_antes = (sum(antes) / len(antes)) if antes else None
    dominio_depois = (sum(depois) / len(depois)) if depois else None
    cobertura_ini = (sum(cobertura_antes) / len(cobertura_antes)) if cobertura_antes else None
    cobertura_fim = (sum(cobertura_depois) / len(cobertura_depois)) if cobertura_depois else None

    return {
        "sessoes_questoes_ids": [int(linha[0]) for linha in linhas],
        "sessoes_questoes": len(linhas),
        "respondidas": respondidas,
        "acertos": acertos,
        "erros": erros,
        "puladas": puladas,
        "desempenho": desempenho,
        "dominio_antes": dominio_antes,
        "dominio_depois": dominio_depois,
        "delta_dominio": (
            dominio_depois - dominio_antes
            if dominio_antes is not None and dominio_depois is not None
            else None
        ),
        "cobertura_antes": cobertura_ini,
        "cobertura_depois": cobertura_fim,
        "delta_cobertura": (
            cobertura_fim - cobertura_ini
            if cobertura_ini is not None and cobertura_fim is not None
            else None
        ),
        "tempo_questoes_segundos": tempo_questoes,
    }


def listar_sessoes_foco_periodo(data_inicio, data_fim):
    inicio = str(data_inicio or "")[:10]
    fim = str(data_fim or "")[:10]
    with conectar() as conexao:
        linhas = conexao.execute(
            """
            SELECT
                id, inicio, fim, duracao_planejada, duracao_efetiva,
                disciplina_id, topico_id, disciplina_nome, topico_nome,
                tipo_atividade, concluida, observacao, meta_questoes,
                origem, plano_chave
            FROM sessoes_foco
            WHERE substr(inicio, 1, 10) BETWEEN ? AND ?
              AND duracao_efetiva > 0
            ORDER BY inicio DESC, id DESC
            """,
            (inicio, fim),
        ).fetchall()
    return [
        {
            "id": int(row[0]), "inicio": row[1], "fim": row[2],
            "duracao_planejada": int(row[3] or 0),
            "duracao_efetiva": int(row[4] or 0),
            "disciplina_id": row[5], "topico_id": row[6],
            "disciplina": row[7], "topico": row[8],
            "tipo_atividade": row[9], "concluida": bool(row[10]),
            "observacao": row[11], "meta_questoes": int(row[12] or 0),
            "origem": row[13], "plano_chave": row[14],
        }
        for row in linhas
    ]


def obter_fechamento_semanal(data_referencia=None, concurso_id=None):
    """Consolida foco, questões, revisões e sinais estratégicos da semana."""
    if data_referencia is None:
        referencia = date.today()
    elif isinstance(data_referencia, datetime):
        referencia = data_referencia.date()
    elif isinstance(data_referencia, date):
        referencia = data_referencia
    else:
        try:
            referencia = date.fromisoformat(str(data_referencia)[:10])
        except Exception:
            referencia = date.today()

    if concurso_id is None:
        concurso_id = obter_concurso_ativo()[0]
    concurso_id = int(concurso_id)

    inicio = referencia - timedelta(days=referencia.weekday())
    fim = inicio + timedelta(days=6)
    anterior_inicio = inicio - timedelta(days=7)
    anterior_fim = inicio - timedelta(days=1)
    resumo_foco = obter_resumo_foco(referencia)

    def desempenho_periodo(conexao, di, df):
        row = conexao.execute(
            """
            SELECT
                COUNT(CASE WHEN tq.correta IS NOT NULL THEN 1 END),
                COALESCE(SUM(CASE WHEN tq.correta = 1 THEN 1 ELSE 0 END), 0)
            FROM tentativas_questoes tq
            WHERE tq.concurso_id = ?
              AND substr(tq.respondida_em, 1, 10) BETWEEN ? AND ?
            """,
            (concurso_id, di.isoformat(), df.isoformat()),
        ).fetchone()
        respondidas = int(row[0] or 0)
        acertos = int(row[1] or 0)
        return respondidas, acertos, (100.0 * acertos / respondidas if respondidas else None)

    with conectar() as conexao:
        respondidas, acertos, desempenho = desempenho_periodo(conexao, inicio, fim)
        ant_resp, ant_acertos, ant_desempenho = desempenho_periodo(
            conexao, anterior_inicio, anterior_fim
        )

        revisoes = int(conexao.execute(
            """
            SELECT COUNT(*)
            FROM revisoes r
            JOIN topicos t ON t.id = r.topico_id
            JOIN disciplinas d ON d.id = t.disciplina_id
            JOIN disciplina_concurso_inclusao dc
              ON dc.disciplina_id = d.id AND dc.concurso_id = ? AND dc.incluido = 1 AND COALESCE(dc.pausado, 0) = 0
            JOIN topico_concurso_importancia tc
              ON tc.topico_id = t.id AND tc.concurso_id = ? AND tc.incluido = 1
            WHERE r.data BETWEEN ? AND ?
            """,
            (concurso_id, concurso_id, inicio.isoformat(), fim.isoformat()),
        ).fetchone()[0] or 0)

        disciplinas_rows = conexao.execute(
            """
            SELECT
                COALESCE(tq.disciplina_snapshot, d.nome, '—') AS disciplina,
                COUNT(CASE WHEN tq.correta IS NOT NULL THEN 1 END) AS respondidas,
                COALESCE(SUM(CASE WHEN tq.correta = 1 THEN 1 ELSE 0 END), 0) AS acertos
            FROM tentativas_questoes tq
            LEFT JOIN questoes q ON q.id = tq.questao_id
            LEFT JOIN topicos t ON t.id = q.topico_id
            LEFT JOIN disciplinas d ON d.id = t.disciplina_id
            WHERE tq.concurso_id = ?
              AND substr(tq.respondida_em, 1, 10) BETWEEN ? AND ?
              AND tq.correta IS NOT NULL
            GROUP BY disciplina
            ORDER BY respondidas DESC, disciplina COLLATE NOCASE
            """,
            (concurso_id, inicio.isoformat(), fim.isoformat()),
        ).fetchall()

        atual_por_disc = {}
        for nome, qtd, ac in disciplinas_rows:
            qtd = int(qtd or 0); ac = int(ac or 0)
            atual_por_disc[str(nome)] = {
                "questoes": qtd,
                "acertos": ac,
                "desempenho": (100.0 * ac / qtd if qtd else None),
            }

        anterior_rows = conexao.execute(
            """
            SELECT
                COALESCE(tq.disciplina_snapshot, d.nome, '—') AS disciplina,
                COUNT(CASE WHEN tq.correta IS NOT NULL THEN 1 END) AS respondidas,
                COALESCE(SUM(CASE WHEN tq.correta = 1 THEN 1 ELSE 0 END), 0) AS acertos
            FROM tentativas_questoes tq
            LEFT JOIN questoes q ON q.id = tq.questao_id
            LEFT JOIN topicos t ON t.id = q.topico_id
            LEFT JOIN disciplinas d ON d.id = t.disciplina_id
            WHERE tq.concurso_id = ?
              AND substr(tq.respondida_em, 1, 10) BETWEEN ? AND ?
              AND tq.correta IS NOT NULL
            GROUP BY disciplina
            """,
            (concurso_id, anterior_inicio.isoformat(), anterior_fim.isoformat()),
        ).fetchall()

    anterior_por_disc = {}
    for nome, qtd, ac in anterior_rows:
        qtd = int(qtd or 0); ac = int(ac or 0)
        anterior_por_disc[str(nome)] = (100.0 * ac / qtd if qtd else None, qtd)

    evolucoes = []
    for nome, atual in atual_por_disc.items():
        anterior = anterior_por_disc.get(nome)
        if not anterior or atual["desempenho"] is None or anterior[0] is None:
            continue
        if atual["questoes"] < 5 or anterior[1] < 5:
            continue
        evolucoes.append({
            "disciplina": nome,
            "delta": float(atual["desempenho"] - anterior[0]),
            "desempenho": atual["desempenho"],
            "questoes": atual["questoes"],
        })
    evolucoes.sort(key=lambda item: item["delta"], reverse=True)

    try:
        prioridades = obter_prioridades_sessao_adaptativa(concurso_id)[:3]
    except Exception:
        prioridades = []

    meta_horas = max(0, obter_configuracao_int("meta_foco_semanal_horas", 0))
    meta_segundos = meta_horas * 3600
    foco_pct = (
        min(100.0, 100.0 * resumo_foco["semana_segundos"] / meta_segundos)
        if meta_segundos > 0 else None
    )

    return {
        "inicio": inicio.isoformat(),
        "fim": fim.isoformat(),
        "foco_segundos": int(resumo_foco["semana_segundos"]),
        "sessoes": int(resumo_foco["semana_sessoes"]),
        "sessoes_concluidas": int(resumo_foco["semana_concluidas"]),
        "dias_com_foco": int(resumo_foco["dias_com_foco_semana"]),
        "distribuicao_foco": list(resumo_foco["distribuicao_semana"]),
        "meta_foco_horas": meta_horas,
        "meta_foco_percentual": foco_pct,
        "questoes": respondidas,
        "acertos": acertos,
        "desempenho": desempenho,
        "desempenho_anterior": ant_desempenho,
        "delta_desempenho": (
            desempenho - ant_desempenho
            if desempenho is not None and ant_desempenho is not None
            else None
        ),
        "revisoes": revisoes,
        "disciplinas_questoes": atual_por_disc,
        "maior_evolucao": evolucoes[0] if evolucoes else None,
        "prioridades": prioridades,
    }

# ============================================================
# EFICIÊNCIA V4 — calibração e histórico de recomendações
# ============================================================

def obter_calibracao_foco(dias=120):
    """Aprende durações a partir do tempo REAL das sessões concluídas.

    Estimativas nunca entram aqui. Para ritmo de questões, usa somente
    questões efetivamente respondidas em baterias vinculadas ao Modo Foco.
    """
    try:
        dias = max(14, min(3650, int(dias)))
    except Exception:
        dias = 120
    limite = (date.today() - timedelta(days=dias)).isoformat()

    with conectar() as conexao:
        linhas = conexao.execute(
            """
            SELECT
                sf.id,
                COALESCE(NULLIF(trim(sf.disciplina_nome), ''), 'Livre / outros') AS disciplina,
                COALESCE(NULLIF(trim(sf.tipo_atividade), ''), 'Estudo livre') AS atividade,
                sf.duracao_efetiva,
                sf.concluida,
                COUNT(CASE WHEN tq.correta IS NOT NULL THEN 1 END) AS respondidas
            FROM sessoes_foco sf
            LEFT JOIN foco_questoes fq
                ON fq.sessao_foco_id = sf.id
            LEFT JOIN tentativas_questoes tq
                ON tq.sessao_id = fq.sessao_questoes_id
            WHERE sf.duracao_efetiva > 0
              AND substr(sf.inicio, 1, 10) >= ?
            GROUP BY sf.id, disciplina, atividade, sf.duracao_efetiva, sf.concluida
            ORDER BY sf.inicio DESC
            """,
            (limite,),
        ).fetchall()

    por_disciplina_raw = {}
    por_atividade_raw = {}
    global_q = []
    for _sid, disciplina, atividade, duracao, concluida, respondidas in linhas:
        duracao = int(duracao or 0)
        respondidas = int(respondidas or 0)
        disciplina = str(disciplina or "Livre / outros")
        atividade = str(atividade or "Estudo livre")
        if bool(concluida) and duracao >= 60:
            por_atividade_raw.setdefault(atividade, []).append(duracao / 60.0)
        if respondidas >= 5 and duracao >= 60:
            segundos_q = duracao / float(respondidas)
            # Remove valores evidentemente incompatíveis com uma bateria real.
            if 8 <= segundos_q <= 900:
                global_q.append(segundos_q)
                por_disciplina_raw.setdefault(disciplina, []).append(segundos_q)

    por_disciplina = {}
    for nome, valores in por_disciplina_raw.items():
        por_disciplina[nome] = {
            "amostras_questoes": len(valores),
            "segundos_por_questao": round(float(statistics.median(valores)), 2),
        }

    por_atividade = {}
    for nome, valores in por_atividade_raw.items():
        por_atividade[nome] = {
            "amostras": len(valores),
            "mediana_minutos": round(float(statistics.median(valores)), 1),
        }

    return {
        "dias": dias,
        "sessoes_analisadas": len(linhas),
        "por_disciplina": por_disciplina,
        "por_atividade": por_atividade,
        "questoes_global": {
            "amostras": len(global_q),
            "segundos_por_questao": (
                round(float(statistics.median(global_q)), 2) if global_q else None
            ),
        },
    }


def registrar_recomendacao_estudo(concurso_id, recomendacao):
    recomendacao = dict(recomendacao or {})
    concurso_id = int(concurso_id) if concurso_id not in (None, "") else None
    topico_id = recomendacao.get("topico_id")
    disciplina_id = None
    if topico_id not in (None, ""):
        try:
            topico_id = int(topico_id)
            with conectar() as conexao:
                linha = conexao.execute(
                    "SELECT disciplina_id FROM topicos WHERE id = ?",
                    (topico_id,),
                ).fetchone()
                if linha:
                    disciplina_id = int(linha[0])
                else:
                    topico_id = None
                    disciplina_id = None
        except Exception:
            topico_id = None
            disciplina_id = None

    explicacao = {
        "versao_motor": recomendacao.get("versao_motor"),
        "score_explicado": recomendacao.get("score_explicado") or [],
        "motivos": recomendacao.get("motivos") or [],
        "calibracao_aplicada": bool(recomendacao.get("calibracao_aplicada")),
    }
    with conectar() as conexao:
        cursor = conexao.execute(
            """
            INSERT INTO recomendacoes_estudo (
                concurso_id, origem, disciplina_id, topico_id,
                disciplina_nome, topico_nome, atividade,
                minutos_sugeridos, questoes_alvo, score_total,
                explicacao_json, decisao
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'exibida')
            """,
            (
                concurso_id,
                str(recomendacao.get("origem") or ""),
                disciplina_id,
                topico_id,
                str(recomendacao.get("disciplina") or "") or None,
                str(recomendacao.get("topico") or "") or None,
                str(recomendacao.get("atividade") or "") or None,
                int(recomendacao.get("minutos") or 0),
                int(recomendacao.get("questoes_alvo") or 0),
                float(recomendacao.get("score_total") or 0.0),
                json.dumps(explicacao, ensure_ascii=False),
            ),
        )
        return int(cursor.lastrowid)


def atualizar_decisao_recomendacao(recomendacao_id, decisao, minutos_escolhidos=None):
    if recomendacao_id in (None, ""):
        return False
    decisao = str(decisao or "").strip().lower() or "ignorada"
    minutos = None
    if minutos_escolhidos not in (None, ""):
        try:
            minutos = max(0, int(minutos_escolhidos))
        except Exception:
            minutos = None
    with conectar() as conexao:
        cursor = conexao.execute(
            """
            UPDATE recomendacoes_estudo
            SET decisao = ?,
                decidido_em = datetime('now', 'localtime'),
                minutos_escolhidos = ?
            WHERE id = ?
            """,
            (decisao, minutos, int(recomendacao_id)),
        )
        return cursor.rowcount > 0


def obter_perfil_decisoes_recomendacao(concurso_id, dias=90):
    concurso_id = int(concurso_id)
    try:
        dias = max(14, min(730, int(dias)))
    except Exception:
        dias = 90
    limite = (date.today() - timedelta(days=dias)).isoformat()
    with conectar() as conexao:
        linhas = conexao.execute(
            """
            SELECT decisao, minutos_sugeridos, minutos_escolhidos
            FROM recomendacoes_estudo
            WHERE concurso_id = ?
              AND substr(criado_em, 1, 10) >= ?
              AND decisao <> 'exibida'
            ORDER BY criado_em DESC, id DESC
            LIMIT 300
            """,
            (concurso_id, limite),
        ).fetchall()

    aceitas_valores = []
    aceitas = 0
    ignoradas = 0
    diretas = 0
    for decisao, sugeridos, escolhidos in linhas:
        decisao = str(decisao or "").lower()
        if decisao in {"aceita", "aceita_direta"}:
            aceitas += 1
            if decisao == "aceita_direta":
                diretas += 1
            valor = escolhidos if escolhidos not in (None, 0) else sugeridos
            if valor:
                aceitas_valores.append(int(valor))
        elif decisao in {"ignorada", "cancelada"}:
            ignoradas += 1

    total = aceitas + ignoradas
    return {
        "dias": dias,
        "total_decisoes": total,
        "aceitas": aceitas,
        "aceitas_diretas": diretas,
        "ignoradas": ignoradas,
        "taxa_aceite": (100.0 * aceitas / total if total else None),
        "mediana_minutos_aceitos": (
            float(statistics.median(aceitas_valores)) if aceitas_valores else None
        ),
    }
