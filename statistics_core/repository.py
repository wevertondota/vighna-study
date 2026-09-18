"""Leituras normalizadas e em lote para o Nucleo Estatistico."""

from __future__ import annotations

from collections.abc import Callable
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime

from .periods import StatisticalPeriod


@dataclass(frozen=True)
class AttemptEvent:
    id: int
    question_id: int | None
    topic_id: int | None
    subject_id: int | None
    session_id: int | None
    occurred_at: str
    correct: bool
    doubt: bool

    @property
    def day(self) -> str:
        return self.occurred_at[:10]


@dataclass(frozen=True)
class ReviewEvent:
    id: int
    topic_id: int
    subject_id: int
    occurred_at: str
    question_count: int
    correct_count: int
    qualified_profile_id: int | None
    lineage_known: bool

    @property
    def day(self) -> str:
        return self.occurred_at[:10]


@dataclass(frozen=True)
class CatalogItem:
    question_id: int
    topic_id: int
    subject_id: int


def _sql_timestamp(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.replace(tzinfo=None).isoformat(sep=" ", timespec="seconds")


class MetricsRepository:
    """Repositorio de leitura. Nenhum metodo modifica o banco."""

    def __init__(self, connection_factory: Callable):
        self._connect = connection_factory

    @staticmethod
    def _period_clause(period: StatisticalPeriod, column: str) -> tuple[str, list]:
        parts = [f"{column} < ?"]
        params = [_sql_timestamp(period.end_exclusive)]
        if period.start is not None:
            parts.insert(0, f"{column} >= ?")
            params.insert(0, _sql_timestamp(period.start))
        return " AND ".join(parts), params

    def load_attempts(
        self,
        period: StatisticalPeriod,
        concurso_id: int | None = None,
        topic_id: int | None = None,
        subject_id: int | None = None,
        question_id: int | None = None,
    ) -> list[AttemptEvent]:
        period_sql, params = self._period_clause(period, "tq.respondida_em")
        where = ["tq.correta IN (0, 1)", period_sql]

        if concurso_id is not None:
            where.append("tq.concurso_id = ?")
            params.append(int(concurso_id))
        if topic_id is not None:
            where.append("COALESCE(tq.topico_id_snapshot, q.topico_id) = ?")
            params.append(int(topic_id))
        if subject_id is not None:
            where.append(
                "COALESCE(tq.disciplina_id_snapshot, t.disciplina_id) = ?"
            )
            params.append(int(subject_id))
        if question_id is not None:
            where.append("COALESCE(tq.questao_id_snapshot, tq.questao_id) = ?")
            params.append(int(question_id))

        sql = f"""
            SELECT
                tq.id,
                COALESCE(tq.questao_id_snapshot, tq.questao_id),
                COALESCE(tq.topico_id_snapshot, q.topico_id),
                COALESCE(tq.disciplina_id_snapshot, t.disciplina_id),
                tq.sessao_id,
                tq.respondida_em,
                tq.correta,
                COALESCE(tq.marcada_duvida, 0)
            FROM tentativas_questoes tq
            LEFT JOIN questoes q ON q.id = tq.questao_id
            LEFT JOIN topicos t
                ON t.id = COALESCE(tq.topico_id_snapshot, q.topico_id)
            WHERE {' AND '.join(where)}
            ORDER BY tq.respondida_em DESC, tq.id DESC
        """

        with closing(self._connect()) as connection:
            rows = connection.execute(sql, params).fetchall()

        return [
            AttemptEvent(
                id=int(row[0]),
                question_id=int(row[1]) if row[1] is not None else None,
                topic_id=int(row[2]) if row[2] is not None else None,
                subject_id=int(row[3]) if row[3] is not None else None,
                session_id=int(row[4]) if row[4] is not None else None,
                occurred_at=str(row[5]),
                correct=bool(row[6]),
                doubt=bool(row[7]),
            )
            for row in rows
        ]

    def load_active_catalog(
        self,
        concurso_id: int | None = None,
        topic_id: int | None = None,
        subject_id: int | None = None,
    ) -> list[CatalogItem]:
        joins = """
            JOIN topicos t ON t.id = q.topico_id
            JOIN disciplinas d ON d.id = t.disciplina_id
        """
        where = ["q.ativa = 1", "COALESCE(q.excluida, 0) = 0"]
        params: list[int] = []

        if concurso_id is not None:
            joins += """
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
            """
            params.extend([int(concurso_id), int(concurso_id)])
        if topic_id is not None:
            where.append("t.id = ?")
            params.append(int(topic_id))
        if subject_id is not None:
            where.append("d.id = ?")
            params.append(int(subject_id))

        with closing(self._connect()) as connection:
            rows = connection.execute(
                f"""
                SELECT q.id, t.id, d.id
                FROM questoes q
                {joins}
                WHERE {' AND '.join(where)}
                ORDER BY q.id
                """,
                params,
            ).fetchall()

        return [CatalogItem(int(row[0]), int(row[1]), int(row[2])) for row in rows]

    def load_active_topics(
        self,
        concurso_id: int | None = None,
        subject_id: int | None = None,
    ) -> list[tuple[int, int]]:
        joins = "JOIN disciplinas d ON d.id = t.disciplina_id"
        params: list[int] = []
        where = ["1 = 1"]
        if concurso_id is not None:
            joins += """
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
            """
            params.extend([int(concurso_id), int(concurso_id)])
        if subject_id is not None:
            where.append("d.id = ?")
            params.append(int(subject_id))

        with closing(self._connect()) as connection:
            rows = connection.execute(
                f"""
                SELECT t.id, d.id
                FROM topicos t
                {joins}
                WHERE {' AND '.join(where)}
                ORDER BY t.id
                """,
                params,
            ).fetchall()
        return [(int(row[0]), int(row[1])) for row in rows]

    def load_reviews(
        self,
        period: StatisticalPeriod,
        concurso_id: int | None = None,
        topic_id: int | None = None,
        subject_id: int | None = None,
    ) -> list[ReviewEvent]:
        # Bancos migrados usam revisoes.concurso_id como autoridade. Em bancos
        # realmente antigos, ainda sem a coluna, preservamos a leitura legada
        # por tentativas apenas para permitir abertura/migracao compativel.
        period_sql, params = self._period_clause(
            period,
            "COALESCE(r.realizada_em, r.data)",
        )
        where = [period_sql]
        if topic_id is not None:
            where.append("r.topico_id = ?")
            params.append(int(topic_id))
        if subject_id is not None:
            where.append("t.disciplina_id = ?")
            params.append(int(subject_id))

        with closing(self._connect()) as connection:
            review_columns = {
                str(row[1])
                for row in connection.execute(
                    "PRAGMA table_info(revisoes)"
                ).fetchall()
            }
            has_direct_lineage = "concurso_id" in review_columns
            direct_lineage_sql = (
                "r.concurso_id"
                if has_direct_lineage
                else "NULL"
            )
            rows = connection.execute(
                f"""
                SELECT
                    r.id,
                    r.topico_id,
                    t.disciplina_id,
                    COALESCE(r.realizada_em, r.data),
                    COALESCE(r.questoes, 0),
                    COALESCE(r.acertos, 0),
                    {direct_lineage_sql} AS direct_profile,
                    COUNT(tq.id) AS member_count,
                    COUNT(DISTINCT tq.concurso_id) AS profile_count,
                    MIN(tq.concurso_id) AS only_profile
                FROM revisoes r
                JOIN topicos t ON t.id = r.topico_id
                LEFT JOIN tentativas_questoes tq ON tq.revisao_id = r.id
                WHERE {' AND '.join(where)}
                GROUP BY r.id
                ORDER BY COALESCE(r.realizada_em, r.data) DESC, r.id DESC
                """,
                params,
            ).fetchall()

        reviews = []
        for row in rows:
            direct_profile = int(row[6]) if row[6] is not None else None
            member_count = int(row[7] or 0)
            profile_count = int(row[8] or 0)
            only_profile = int(row[9]) if row[9] is not None else None
            if has_direct_lineage:
                qualified_profile = direct_profile
                lineage_known = direct_profile is not None
            else:
                lineage_known = member_count > 0 and profile_count == 1
                qualified_profile = only_profile if lineage_known else None
            if (
                concurso_id is not None
                and lineage_known
                and qualified_profile != int(concurso_id)
            ):
                continue
            reviews.append(
                ReviewEvent(
                    id=int(row[0]),
                    topic_id=int(row[1]),
                    subject_id=int(row[2]),
                    occurred_at=str(row[3]),
                    question_count=int(row[4] or 0),
                    correct_count=int(row[5] or 0),
                    qualified_profile_id=qualified_profile,
                    lineage_known=lineage_known,
                )
            )
        return reviews

    def count_question_sessions(
        self,
        period: StatisticalPeriod,
        concurso_id: int | None = None,
        completed_only: bool = False,
    ) -> int:
        period_sql, params = self._period_clause(period, "sq.iniciado_em")
        where = [period_sql]
        if concurso_id is not None:
            where.append("sq.concurso_id = ?")
            params.append(int(concurso_id))
        if completed_only:
            where.append("sq.concluida = 1")
        with closing(self._connect()) as connection:
            row = connection.execute(
                f"SELECT COUNT(*) FROM sessoes_questoes sq WHERE {' AND '.join(where)}",
                params,
            ).fetchone()
        return int(row[0] or 0)
