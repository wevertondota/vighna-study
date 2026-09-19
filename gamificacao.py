"""Gamificação comportamental do VighnaStudy.

A camada recompensa comportamentos úteis e verificáveis sem alterar domínio,
fila inteligente, agendamento ou qualquer métrica acadêmica. Não há XP por
acerto isolado: isso evita incentivar questões fáceis ou repetição artificial.

Os eventos são idempotentes e persistentes. Um marco conquistado não é retirado
se o catálogo crescer ou se o domínio oscilar depois.
"""

from __future__ import annotations

import json
from contextlib import closing
from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from typing import Any, Callable

from regularidade import (
    MIN_FOCUS_SECONDS_FOR_STUDY_DAY,
    load_valid_activity_days,
)
from statistics_core.periods import statistical_timezone

GAMIFICATION_VERSION = "gamificacao_v1"
XP_PER_LEVEL = 250

BASE_POINTS = {
    "study_day": 20,
    "qualified_review": 15,
    "error_recovery": 30,
    "topic_consolidated": 80,
}

STREAK_MILESTONES = {3: 20, 7: 50, 14: 120, 30: 300, 60: 700, 100: 1500}
COVERAGE_MILESTONES = {10: 25, 25: 60, 50: 140, 75: 250, 100: 500}
REVISION_MILESTONES = {1: 15, 10: 60, 25: 150, 50: 350}
RECOVERY_MILESTONES = {1: 20, 5: 75, 10: 150, 25: 400}
CONSOLIDATION_MILESTONES = {1: 50, 5: 120, 10: 250, 25: 700, 50: 1400}


@dataclass(frozen=True)
class GamificationSnapshot:
    concurso_id: int
    total_xp: int
    level: int
    level_progress_xp: int
    level_required_xp: int
    level_progress_rate: float
    events_count: int
    achievements_earned: int
    achievements_total: int
    current_streak_days: int
    best_streak_days: int
    active_study_days: int
    qualified_reviews: int
    recovered_questions: int
    consolidated_topics: int
    question_coverage_rate: float | None
    breakdown: dict[str, int] = field(default_factory=dict)
    achievements: list[dict[str, Any]] = field(default_factory=list)
    recent_events: list[dict[str, Any]] = field(default_factory=list)
    generated_at: str = ""
    version: str = GAMIFICATION_VERSION

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def ensure_gamification_schema(connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS gamificacao_eventos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chave TEXT NOT NULL UNIQUE,
            tipo TEXT NOT NULL,
            concurso_id INTEGER,
            topico_id INTEGER,
            origem_id INTEGER,
            pontos INTEGER NOT NULL DEFAULT 0,
            titulo TEXT NOT NULL,
            detalhe TEXT,
            ocorrido_em TEXT NOT NULL,
            metadata_json TEXT,
            versao TEXT NOT NULL DEFAULT 'gamificacao_v1',
            criado_em TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
        )
        """
    )
    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_gamificacao_eventos_tipo_data
        ON gamificacao_eventos(tipo, ocorrido_em DESC)
        """
    )
    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_gamificacao_eventos_concurso_data
        ON gamificacao_eventos(concurso_id, ocorrido_em DESC)
        """
    )


def _iso_now() -> str:
    return datetime.now(statistical_timezone()).isoformat(timespec="seconds")


def _insert_event(
    connection,
    *,
    key: str,
    event_type: str,
    points: int,
    title: str,
    detail: str,
    occurred_at: str,
    concurso_id: int | None = None,
    topico_id: int | None = None,
    source_id: int | None = None,
    metadata: dict[str, Any] | None = None,
) -> bool:
    cursor = connection.execute(
        """
        INSERT OR IGNORE INTO gamificacao_eventos (
            chave, tipo, concurso_id, topico_id, origem_id, pontos,
            titulo, detalhe, ocorrido_em, metadata_json, versao
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            str(key),
            str(event_type),
            int(concurso_id) if concurso_id is not None else None,
            int(topico_id) if topico_id is not None else None,
            int(source_id) if source_id is not None else None,
            int(points),
            str(title),
            str(detail or ""),
            str(occurred_at),
            json.dumps(metadata or {}, ensure_ascii=False, sort_keys=True),
            GAMIFICATION_VERSION,
        ),
    )
    return bool(cursor.rowcount)


def _table_columns(connection, table: str) -> set[str]:
    try:
        return {str(row[1]) for row in connection.execute(f"PRAGMA table_info({table})")}
    except Exception:
        return set()


def _sync_study_days(connect: Callable, connection, *, as_of: date) -> int:
    days = load_valid_activity_days(
        connect,
        as_of=as_of,
        min_focus_seconds=MIN_FOCUS_SECONDS_FOR_STUDY_DAY,
    )
    inserted = 0
    for day in sorted(days):
        sources = dict(days[day])
        parts = []
        if int(sources.get("attempts") or 0):
            parts.append(f"{int(sources['attempts'])} tentativa(s)")
        if int(sources.get("reviews") or 0):
            parts.append(f"{int(sources['reviews'])} revisão(ões)")
        if int(sources.get("focus_sessions") or 0):
            parts.append(f"{int(sources['focus_sessions'])} sessão(ões) de foco")
        inserted += int(
            _insert_event(
                connection,
                key=f"study_day:{day.isoformat()}",
                event_type="study_day",
                points=BASE_POINTS["study_day"],
                title="Dia de estudo válido",
                detail=" • ".join(parts) or "Atividade acadêmica válida registrada.",
                occurred_at=f"{day.isoformat()}T12:00:00",
                metadata={"sources": sources, "global": True},
            )
        )
    return inserted


def _sync_reviews(connection) -> int:
    columns = _table_columns(connection, "revisoes")
    if not columns:
        return 0
    occurred_expr = "COALESCE(realizada_em, data)" if "realizada_em" in columns else "data"
    concurso_expr = "concurso_id" if "concurso_id" in columns else "NULL"
    rows = connection.execute(
        f"""
        SELECT id, topico_id, {concurso_expr}, {occurred_expr}, COALESCE(questoes, 0)
        FROM revisoes
        WHERE COALESCE(questoes, 0) > 0
        ORDER BY id
        """
    ).fetchall()
    inserted = 0
    for revision_id, topic_id, contest_id, occurred_at, questions in rows:
        inserted += int(
            _insert_event(
                connection,
                key=f"qualified_review:{int(revision_id)}",
                event_type="qualified_review",
                points=BASE_POINTS["qualified_review"],
                title="Revisão concluída",
                detail=f"{int(questions or 0)} questão(ões) registradas na revisão.",
                occurred_at=str(occurred_at or _iso_now()),
                concurso_id=int(contest_id) if contest_id is not None else None,
                topico_id=int(topic_id) if topic_id is not None else None,
                source_id=int(revision_id),
                metadata={"legacy_limited": contest_id is None},
            )
        )
    return inserted


def _sync_recoveries(connection) -> tuple[int, int]:
    columns = _table_columns(connection, "tentativas_questoes")
    if not columns:
        return 0, 0
    if "questao_id_snapshot" in columns:
        question_expr = "COALESCE(questao_id, questao_id_snapshot)"
    else:
        question_expr = "questao_id"
    concurso_expr = "concurso_id" if "concurso_id" in columns else "NULL"
    rows = connection.execute(
        f"""
        SELECT id, {question_expr}, {concurso_expr}, respondida_em, correta
        FROM tentativas_questoes
        WHERE {question_expr} IS NOT NULL
          AND correta IN (0, 1)
        ORDER BY respondida_em, id
        """
    ).fetchall()
    seen_wrong: set[int] = set()
    recovered: set[int] = set()
    inserted = 0
    for attempt_id, question_id, contest_id, occurred_at, correct in rows:
        qid = int(question_id)
        if int(correct or 0) == 0:
            seen_wrong.add(qid)
            continue
        if qid not in seen_wrong or qid in recovered:
            continue
        recovered.add(qid)
        inserted += int(
            _insert_event(
                connection,
                key=f"error_recovery:{qid}",
                event_type="error_recovery",
                points=BASE_POINTS["error_recovery"],
                title="Erro recuperado",
                detail="Uma questão antes errada foi respondida corretamente depois.",
                occurred_at=str(occurred_at or _iso_now()),
                concurso_id=int(contest_id) if contest_id is not None else None,
                source_id=int(attempt_id),
                metadata={"questao_id": qid},
            )
        )
    return inserted, len(recovered)


def _sync_consolidations(connection, concurso_id: int, progress_snapshot: dict[str, Any]) -> tuple[int, int]:
    topics = list(progress_snapshot.get("topicos") or [])
    consolidated = [item for item in topics if bool(item.get("consolidacao_certificada"))]
    inserted = 0
    now = _iso_now()
    for item in consolidated:
        topic_id = int(item.get("topico_id"))
        inserted += int(
            _insert_event(
                connection,
                key=f"topic_consolidated:{int(concurso_id)}:{topic_id}",
                event_type="topic_consolidated",
                points=BASE_POINTS["topic_consolidated"],
                title="Tópico consolidado",
                detail=f"{item.get('disciplina') or 'Disciplina'} — {item.get('topico') or 'Tópico'}",
                occurred_at=now,
                concurso_id=int(concurso_id),
                topico_id=topic_id,
                metadata={"backfilled_current_state": True},
            )
        )
    return inserted, len(consolidated)


def _milestone_defs(
    *,
    concurso_id: int,
    regularity_snapshot: dict[str, Any],
    progress_snapshot: dict[str, Any],
    revision_count: int,
    recovery_count: int,
    consolidated_count: int,
) -> list[dict[str, Any]]:
    best_streak = int(regularity_snapshot.get("best_streak_days") or 0)
    coverage = float(progress_snapshot.get("question_coverage_rate") or 0.0)
    defs: list[dict[str, Any]] = []
    for target, points in STREAK_MILESTONES.items():
        defs.append({
            "key": f"achievement:streak:{target}",
            "category": "Sequência",
            "title": f"{target} dias em sequência",
            "target": target,
            "current": best_streak,
            "unit": "dias",
            "points": points,
            "concurso_id": None,
            "detail": f"Alcançou uma sequência de {target} dias de estudo válido.",
        })
    for target, points in COVERAGE_MILESTONES.items():
        defs.append({
            "key": f"achievement:coverage:{int(concurso_id)}:{target}",
            "category": "Cobertura",
            "title": f"{target}% das questões exploradas",
            "target": float(target),
            "current": coverage,
            "unit": "%",
            "points": points,
            "concurso_id": int(concurso_id),
            "detail": f"Atingiu {target}% de cobertura de questões no perfil ativo.",
        })
    for target, points in REVISION_MILESTONES.items():
        defs.append({
            "key": f"achievement:revisions:{target}",
            "category": "Revisões",
            "title": f"{target} revisão" + ("" if target == 1 else "ões"),
            "target": target,
            "current": revision_count,
            "unit": "revisões",
            "points": points,
            "concurso_id": None,
            "detail": f"Registrou {target} revisão(ões) com questões.",
        })
    for target, points in RECOVERY_MILESTONES.items():
        defs.append({
            "key": f"achievement:recoveries:{target}",
            "category": "Recuperação",
            "title": f"{target} erro" + (" recuperado" if target == 1 else "s recuperados"),
            "target": target,
            "current": recovery_count,
            "unit": "recuperações",
            "points": points,
            "concurso_id": None,
            "detail": f"Recuperou {target} questão(ões) antes respondidas incorretamente.",
        })
    for target, points in CONSOLIDATION_MILESTONES.items():
        defs.append({
            "key": f"achievement:consolidations:{int(concurso_id)}:{target}",
            "category": "Consolidação",
            "title": f"{target} tópico" + (" consolidado" if target == 1 else "s consolidados"),
            "target": target,
            "current": consolidated_count,
            "unit": "tópicos",
            "points": points,
            "concurso_id": int(concurso_id),
            "detail": f"Consolidou {target} tópico(s) com os critérios oficiais do Vighna.",
        })
    return defs


def _sync_milestones(connection, definitions: list[dict[str, Any]]) -> int:
    inserted = 0
    now = _iso_now()
    for item in definitions:
        if float(item["current"] or 0) < float(item["target"]):
            continue
        inserted += int(
            _insert_event(
                connection,
                key=item["key"],
                event_type=f"achievement.{str(item['category']).lower()}",
                points=int(item["points"]),
                title=str(item["title"]),
                detail=str(item["detail"]),
                occurred_at=now,
                concurso_id=item.get("concurso_id"),
                metadata={
                    "category": item["category"],
                    "target": item["target"],
                    "backfilled_current_state": True,
                },
            )
        )
    return inserted


def _read_snapshot(
    connection,
    *,
    concurso_id: int,
    regularity_snapshot: dict[str, Any],
    progress_snapshot: dict[str, Any],
    milestone_defs: list[dict[str, Any]],
    recovery_count: int,
) -> GamificationSnapshot:
    total_xp = int(connection.execute(
        "SELECT COALESCE(SUM(pontos), 0) FROM gamificacao_eventos"
    ).fetchone()[0] or 0)
    events_count = int(connection.execute(
        "SELECT COUNT(*) FROM gamificacao_eventos"
    ).fetchone()[0] or 0)
    earned_keys = {
        str(row[0])
        for row in connection.execute(
            "SELECT chave FROM gamificacao_eventos WHERE tipo LIKE 'achievement.%'"
        ).fetchall()
    }
    achievements = []
    for item in milestone_defs:
        current = float(item["current"] or 0)
        target = float(item["target"] or 0)
        earned = item["key"] in earned_keys
        if item["unit"] == "%":
            progress_text = f"{current:.0f}% / {target:.0f}%"
        else:
            progress_text = f"{int(current)} / {int(target)} {item['unit']}"
        achievements.append({
            "key": item["key"],
            "category": item["category"],
            "title": item["title"],
            "earned": earned,
            "current": current,
            "target": target,
            "unit": item["unit"],
            "progress_rate": min(100.0, 100.0 * current / target) if target > 0 else 0.0,
            "progress_text": progress_text,
            "points": int(item["points"]),
        })

    breakdown = {"Dias de estudo": 0, "Revisões": 0, "Recuperações": 0, "Consolidações": 0, "Marcos": 0}
    for event_type, points in connection.execute(
        "SELECT tipo, COALESCE(SUM(pontos), 0) FROM gamificacao_eventos GROUP BY tipo"
    ).fetchall():
        if event_type == "study_day":
            breakdown["Dias de estudo"] += int(points or 0)
        elif event_type == "qualified_review":
            breakdown["Revisões"] += int(points or 0)
        elif event_type == "error_recovery":
            breakdown["Recuperações"] += int(points or 0)
        elif event_type == "topic_consolidated":
            breakdown["Consolidações"] += int(points or 0)
        elif str(event_type).startswith("achievement."):
            breakdown["Marcos"] += int(points or 0)

    recent_events = []
    for row in connection.execute(
        """
        SELECT ocorrido_em, titulo, detalhe, pontos, tipo
        FROM gamificacao_eventos
        ORDER BY ocorrido_em DESC, id DESC
        LIMIT 12
        """
    ).fetchall():
        recent_events.append({
            "occurred_at": row[0],
            "title": row[1],
            "detail": row[2] or "",
            "points": int(row[3] or 0),
            "type": row[4],
        })

    level = total_xp // XP_PER_LEVEL + 1
    progress_xp = total_xp % XP_PER_LEVEL
    active_days = int(connection.execute(
        "SELECT COUNT(*) FROM gamificacao_eventos WHERE tipo = 'study_day'"
    ).fetchone()[0] or 0)
    revision_count = int(connection.execute(
        "SELECT COUNT(*) FROM gamificacao_eventos WHERE tipo = 'qualified_review'"
    ).fetchone()[0] or 0)

    return GamificationSnapshot(
        concurso_id=int(concurso_id),
        total_xp=total_xp,
        level=level,
        level_progress_xp=progress_xp,
        level_required_xp=XP_PER_LEVEL,
        level_progress_rate=round(100.0 * progress_xp / XP_PER_LEVEL, 1),
        events_count=events_count,
        achievements_earned=len(earned_keys),
        achievements_total=len(milestone_defs),
        current_streak_days=int(regularity_snapshot.get("current_streak_days") or 0),
        best_streak_days=int(regularity_snapshot.get("best_streak_days") or 0),
        active_study_days=active_days,
        qualified_reviews=revision_count,
        recovered_questions=int(recovery_count),
        consolidated_topics=int(progress_snapshot.get("consolidated_topics") or 0),
        question_coverage_rate=(
            float(progress_snapshot["question_coverage_rate"])
            if progress_snapshot.get("question_coverage_rate") is not None
            else None
        ),
        breakdown=breakdown,
        achievements=achievements,
        recent_events=recent_events,
        generated_at=_iso_now(),
    )


def build_gamification_snapshot(
    connect: Callable,
    concurso_id: int,
    progress_snapshot: dict[str, Any],
    regularity_snapshot: dict[str, Any],
    *,
    as_of: date | datetime | None = None,
    synchronize: bool = True,
) -> GamificationSnapshot:
    """Sincroniza eventos factuais e retorna o estado motivacional atual.

    A sincronização é idempotente e não escreve em tabelas acadêmicas.
    """
    if as_of is None:
        ref = datetime.now(statistical_timezone()).date()
    elif isinstance(as_of, datetime):
        ref = as_of.astimezone(statistical_timezone()).date() if as_of.tzinfo else as_of.date()
    else:
        ref = as_of

    with closing(connect()) as connection:
        ensure_gamification_schema(connection)
        if synchronize:
            _sync_study_days(connect, connection, as_of=ref)
            _sync_reviews(connection)
            _, recovery_count = _sync_recoveries(connection)
            _, consolidated_count = _sync_consolidations(
                connection, int(concurso_id), progress_snapshot
            )
            revision_count = int(connection.execute(
                "SELECT COUNT(*) FROM gamificacao_eventos WHERE tipo = 'qualified_review'"
            ).fetchone()[0] or 0)
            definitions = _milestone_defs(
                concurso_id=int(concurso_id),
                regularity_snapshot=regularity_snapshot,
                progress_snapshot=progress_snapshot,
                revision_count=revision_count,
                recovery_count=recovery_count,
                consolidated_count=consolidated_count,
            )
            _sync_milestones(connection, definitions)
            connection.commit()
        else:
            recovery_count = int(connection.execute(
                "SELECT COUNT(*) FROM gamificacao_eventos WHERE tipo = 'error_recovery'"
            ).fetchone()[0] or 0)
            revision_count = int(connection.execute(
                "SELECT COUNT(*) FROM gamificacao_eventos WHERE tipo = 'qualified_review'"
            ).fetchone()[0] or 0)
            consolidated_count = int(progress_snapshot.get("consolidated_topics") or 0)
            definitions = _milestone_defs(
                concurso_id=int(concurso_id),
                regularity_snapshot=regularity_snapshot,
                progress_snapshot=progress_snapshot,
                revision_count=revision_count,
                recovery_count=recovery_count,
                consolidated_count=consolidated_count,
            )
        return _read_snapshot(
            connection,
            concurso_id=int(concurso_id),
            regularity_snapshot=regularity_snapshot,
            progress_snapshot=progress_snapshot,
            milestone_defs=definitions,
            recovery_count=recovery_count,
        )
