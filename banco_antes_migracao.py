import sqlite3
from pathlib import Path


CAMINHO_BANCO = Path(__file__).with_name("estudos.db")


def conectar():
    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


# ==========================================================
# CRIAÇÃO DO BANCO
# ==========================================================

def criar_banco():

    with conectar() as conexao:

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

        disciplinas = [
            "Direito Penal",
            "Direito Administrativo",
            "CTB",
            "Português",
            "Matemática",
            "Informática"
        ]

        for nome in disciplinas:

            conexao.execute(
                """
                INSERT OR IGNORE INTO disciplinas (nome)
                VALUES (?)
                """,
                (nome,)
            )

        # Mantém alguns tópicos iniciais de Direito Penal
        penal_id = conexao.execute(
            """
            SELECT id
            FROM disciplinas
            WHERE nome = ?
            """,
            ("Direito Penal",)
        ).fetchone()[0]

        quantidade = conexao.execute(
            """
            SELECT COUNT(*)
            FROM topicos
            WHERE disciplina_id = ?
            """,
            (penal_id,)
        ).fetchone()[0]

        if quantidade == 0:

            topicos = [
                "Aplicação da Lei Penal",
                "Do Crime",
                "Imputabilidade Penal",
                "Concurso de Pessoas",
                "Das Penas"
            ]

            conexao.executemany(
                """
                INSERT INTO topicos (
                    disciplina_id,
                    nome
                )
                VALUES (?, ?)
                """,
                [
                    (penal_id, nome)
                    for nome in topicos
                ]
            )


# ==========================================================
# DISCIPLINAS
# ==========================================================

def listar_disciplinas():

    with conectar() as conexao:

        return conexao.execute(
            """
            SELECT id, nome
            FROM disciplinas
            ORDER BY id
            """
        ).fetchall()


# ==========================================================
# TÓPICOS
# ==========================================================

def listar_topicos(nome_disciplina):

    with conectar() as conexao:

        return conexao.execute(
            """
            SELECT
                t.id,
                t.nome,

                (
                    SELECT COUNT(*)
                    FROM revisoes r
                    WHERE r.topico_id = t.id
                ) AS quantidade_revisoes,

                (
                    SELECT r.data
                    FROM revisoes r
                    WHERE r.topico_id = t.id
                    ORDER BY
                        r.data DESC,
                        r.id DESC
                    LIMIT 1
                ) AS ultima_revisao,

                (
                    SELECT
                        ROUND(
                            100.0 * r.acertos / r.questoes,
                            1
                        )
                    FROM revisoes r
                    WHERE r.topico_id = t.id
                    ORDER BY
                        r.data DESC,
                        r.id DESC
                    LIMIT 1
                ) AS percentual

            FROM topicos t

            JOIN disciplinas d
                ON d.id = t.disciplina_id

            WHERE d.nome = ?

            ORDER BY
                t.nome COLLATE NOCASE
            """,
            (nome_disciplina,)
        ).fetchall()


def adicionar_topico(
    nome_disciplina,
    nome_topico
):

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

            disciplina_id = cursor.lastrowid

        else:
            disciplina_id = disciplina[0]

        try:

            conexao.execute(
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

            return True

        except sqlite3.IntegrityError:
            return False


# ==========================================================
# REVISÕES
# ==========================================================

def registrar_revisao(
    topico_id,
    data,
    questoes,
    acertos,
    observacao="",
    texto_erros="",
    continuacao=""
):

    with conectar() as conexao:

        conexao.execute(
            """
            INSERT INTO revisoes (
                topico_id,
                data,
                questoes,
                acertos,
                observacao,
                texto_erros,
                continuacao
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                topico_id,
                data,
                questoes,
                acertos,
                observacao,
                texto_erros,
                continuacao
            )
        )


def listar_revisoes_topico(topico_id):

    with conectar() as conexao:

        return conexao.execute(
            """
            SELECT
                id,
                data,
                questoes,
                acertos,

                ROUND(
                    100.0 * acertos / questoes,
                    1
                ) AS percentual,

                observacao,
                texto_erros,
                continuacao

            FROM revisoes

            WHERE topico_id = ?

            ORDER BY
                data DESC,
                id DESC
            """,
            (topico_id,)
        ).fetchall()