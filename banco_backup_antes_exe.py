import sqlite3
from pathlib import Path


CAMINHO_BANCO = Path(__file__).with_name("estudos.db")


def conectar():
    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


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

        conexao.execute("""
            CREATE TABLE IF NOT EXISTS controle_topico (
                topico_id INTEGER PRIMARY KEY,
                revisoes_iniciais INTEGER NOT NULL DEFAULT 0,
                proxima_revisao TEXT,
                percentual_inicial REAL,
                observacao_inicial TEXT,
                texto_erros_inicial TEXT,
                continuacao_inicial TEXT,
                FOREIGN KEY (topico_id)
                    REFERENCES topicos(id)
                    ON DELETE CASCADE
            )
        """)

        conexao.execute("""
            CREATE TABLE IF NOT EXISTS migracoes (
                nome TEXT PRIMARY KEY,
                executada_em TEXT NOT NULL
            )
        """)

        disciplinas = [
            "Geral",
            "Direito Penal",
            "Direito Administrativo",
            "CTB",
            "Português",
            "Matemática",
            "Informática"
        ]

        for nome in disciplinas:
            conexao.execute(
                "INSERT OR IGNORE INTO disciplinas (nome) VALUES (?)",
                (nome,)
            )


def listar_disciplinas():
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
        dados = conexao.execute(
            "SELECT id, nome FROM disciplinas"
        ).fetchall()

    return sorted(
        dados,
        key=lambda item: (ordem.get(item[1], 99), item[1].lower())
    )


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


def listar_topicos(nome_disciplina):
    percentual = _expressao_percentual_atual()
    revisoes = _expressao_revisoes_totais()

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
                {percentual} AS percentual_atual
            FROM topicos t
            JOIN disciplinas d
                ON d.id = t.disciplina_id
            LEFT JOIN controle_topico c
                ON c.topico_id = t.id
            WHERE d.nome = ?
            ORDER BY t.nome COLLATE NOCASE
            """,
            (nome_disciplina,)
        ).fetchall()


def adicionar_topico(nome_disciplina, nome_topico):
    with conectar() as conexao:
        disciplina = conexao.execute(
            "SELECT id FROM disciplinas WHERE nome = ?",
            (nome_disciplina,)
        ).fetchone()

        if disciplina is None:
            cursor = conexao.execute(
                "INSERT INTO disciplinas (nome) VALUES (?)",
                (nome_disciplina,)
            )
            disciplina_id = cursor.lastrowid
        else:
            disciplina_id = disciplina[0]

        try:
            cursor = conexao.execute(
                """
                INSERT INTO topicos (disciplina_id, nome)
                VALUES (?, ?)
                """,
                (disciplina_id, nome_topico)
            )

            conexao.execute(
                """
                INSERT OR IGNORE INTO controle_topico (topico_id)
                VALUES (?)
                """,
                (cursor.lastrowid,)
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


def registrar_revisao(
    topico_id,
    data,
    questoes,
    acertos,
    observacao="",
    texto_erros="",
    continuacao="",
    proxima_revisao=None
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

        conexao.execute(
            """
            INSERT OR IGNORE INTO controle_topico (topico_id)
            VALUES (?)
            """,
            (topico_id,)
        )

        if proxima_revisao is not None:
            conexao.execute(
                """
                UPDATE controle_topico
                SET proxima_revisao = ?
                WHERE topico_id = ?
                """,
                (proxima_revisao, topico_id)
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
        conexao.execute(
            """
            UPDATE revisoes
            SET
                data = ?,
                questoes = ?,
                acertos = ?,
                observacao = ?,
                texto_erros = ?,
                continuacao = ?
            WHERE id = ?
            """,
            (
                data,
                questoes,
                acertos,
                observacao,
                texto_erros,
                continuacao,
                revisao_id
            )
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
            ORDER BY data DESC, id DESC
            """,
            (topico_id,)
        ).fetchall()


def obter_resumo_topico(topico_id):
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

        novas = conexao.execute(
            "SELECT COUNT(*) FROM revisoes WHERE topico_id = ?",
            (topico_id,)
        ).fetchone()[0]

        ultima = conexao.execute(
            """
            SELECT
                data,
                ROUND(100.0 * acertos / questoes, 1)
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
            "revisoes_totais": revisoes_iniciais + novas,
            "ultima_revisao": ultima_revisao,
            "proxima_revisao": proxima_revisao,
            "percentual_atual": percentual_atual,
        }


def listar_pendencias(data_referencia):
    percentual = _expressao_percentual_atual()
    revisoes = _expressao_revisoes_totais()

    with conectar() as conexao:
        return conexao.execute(
            f"""
            SELECT
                t.id,
                d.nome,
                t.nome,
                {revisoes} AS revisoes_totais,
                c.proxima_revisao,
                {percentual} AS percentual_atual
            FROM topicos t
            JOIN disciplinas d
                ON d.id = t.disciplina_id
            JOIN controle_topico c
                ON c.topico_id = t.id
            WHERE
                c.proxima_revisao IS NOT NULL
                AND c.proxima_revisao <= ?
            ORDER BY
                c.proxima_revisao ASC,
                CASE
                    WHEN ({percentual}) IS NULL THEN 999
                    ELSE ({percentual})
                END ASC,
                d.nome COLLATE NOCASE,
                t.nome COLLATE NOCASE
            """,
            (data_referencia,)
        ).fetchall()


def obter_dashboard(data_referencia):
    percentual = _expressao_percentual_atual()

    with conectar() as conexao:
        total_topicos = conexao.execute(
            "SELECT COUNT(*) FROM topicos"
        ).fetchone()[0]

        atrasadas = conexao.execute(
            """
            SELECT COUNT(*)
            FROM controle_topico
            WHERE
                proxima_revisao IS NOT NULL
                AND proxima_revisao < ?
            """,
            (data_referencia,)
        ).fetchone()[0]

        hoje = conexao.execute(
            """
            SELECT COUNT(*)
            FROM controle_topico
            WHERE proxima_revisao = ?
            """,
            (data_referencia,)
        ).fetchone()[0]

        total_questoes = conexao.execute(
            "SELECT COALESCE(SUM(questoes), 0) FROM revisoes"
        ).fetchone()[0]

        revisoes_programa = conexao.execute(
            "SELECT COUNT(*) FROM revisoes"
        ).fetchone()[0]

        revisoes_iniciais = conexao.execute(
            """
            SELECT COALESCE(SUM(revisoes_iniciais), 0)
            FROM controle_topico
            """
        ).fetchone()[0]

        media = conexao.execute(
            f"""
            SELECT ROUND(AVG(percentual_atual), 1)
            FROM (
                SELECT
                    {percentual} AS percentual_atual
                FROM topicos t
                LEFT JOIN controle_topico c
                    ON c.topico_id = t.id
            )
            WHERE percentual_atual IS NOT NULL
            """
        ).fetchone()[0]

        return {
            "total_topicos": total_topicos,
            "atrasadas": atrasadas,
            "hoje": hoje,
            "total_questoes": total_questoes,
            "revisoes_totais": revisoes_iniciais + revisoes_programa,
            "media_atual": media,
        }
