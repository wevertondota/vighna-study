"""Snapshot e regras de apresentação do Mapa de Domínio V2.

O módulo é deliberadamente independente do Qt e do banco. Ele recebe o
snapshot oficial do Progresso do Edital e transforma as métricas já calculadas
em uma visão analítica de domínio, mantendo evidência, cobertura e
consolidação como dimensões separadas.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Iterable

from progresso_edital import EVIDENCE_LABELS, EVIDENCE_ORDER

DOMAIN_MAP_VERSION = "domain_map_v2"

DOMAIN_BANDS = (
    ("baixo", "Baixo", 0.0, 50.0),
    ("intermediario", "Intermediário", 50.0, 70.0),
    ("bom", "Bom", 70.0, 85.0),
    ("alto", "Alto", 85.0, 100.000001),
)

DISPLAY_STATE_ORDER = {
    "Não iniciado": 0,
    "Dados insuficientes": 1,
    "Provisório": 2,
    "Mensurável": 3,
    "Consolidado": 4,
}


@dataclass(frozen=True)
class DomainMapSnapshot:
    concurso_id: int
    total_topics: int
    unstarted_topics: int
    insufficient_topics: int
    provisional_topics: int
    measurable_topics: int
    consolidated_topics: int
    insufficient_evidence_topics: int
    low_evidence_topics: int
    moderate_evidence_topics: int
    high_evidence_topics: int
    sufficient_evidence_topics: int
    disciplines: list[dict[str, Any]] = field(default_factory=list)
    topics: list[dict[str, Any]] = field(default_factory=list)
    generated_at: str = ""
    metric_version: str = "1"
    snapshot_version: str = DOMAIN_MAP_VERSION

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def domain_band(score: float | int | None) -> dict[str, Any] | None:
    """Retorna faixa visual; None continua sendo ausência, nunca zero."""
    if score is None:
        return None
    value = max(0.0, min(100.0, float(score)))
    for code, label, minimum, maximum in DOMAIN_BANDS:
        if minimum <= value < maximum:
            return {
                "code": code,
                "label": label,
                "min": minimum,
                "max_exclusive": maximum,
            }
    return None


def topic_display_state(topic: dict[str, Any]) -> str:
    attempts = int(topic.get("tentativas") or 0)
    if attempts <= 0:
        return "Não iniciado"
    if topic.get("consolidacao") == "consolidated":
        return "Consolidado"

    evidence = str(topic.get("evidencia") or "insufficient")
    mastery = topic.get("dominio_score")
    if mastery is None or evidence == "insufficient":
        return "Dados insuficientes"
    if evidence == "low":
        return "Provisório"
    return "Mensurável"


def _topic_map_item(topic: dict[str, Any]) -> dict[str, Any]:
    item = dict(topic)
    state = topic_display_state(topic)
    mastery = topic.get("dominio_score")
    evidence = str(topic.get("evidencia") or "insufficient")
    band = domain_band(mastery)
    item.update({
        "display_state": state,
        "display_state_order": DISPLAY_STATE_ORDER[state],
        "domain_band": None if band is None else band["code"],
        "domain_band_label": None if band is None else band["label"],
        "mastery_measurable": (
            mastery is not None and evidence in {"moderate", "high"}
        ),
        "mastery_provisional": mastery is not None and evidence == "low",
        "evidence_label": EVIDENCE_LABELS.get(evidence, "Insuficiente"),
        "evidence_order": EVIDENCE_ORDER.get(evidence, 0),
        "consolidation_label": (
            "Consolidado"
            if topic.get("consolidacao") == "consolidated"
            else (
                "Não consolidado"
                if topic.get("consolidacao") == "not_consolidated"
                else "Dados insuficientes"
            )
        ),
    })
    return item


def _discipline_map_item(
    subject: dict[str, Any],
    topics: list[dict[str, Any]],
) -> dict[str, Any]:
    evidence = str(subject.get("evidencia") or "insufficient")
    mastery = subject.get("dominio")
    band = domain_band(mastery)
    states = {
        state: sum(1 for topic in topics if topic["display_state"] == state)
        for state in DISPLAY_STATE_ORDER
    }
    measurable = sum(1 for topic in topics if topic["mastery_measurable"])
    provisional = sum(1 for topic in topics if topic["mastery_provisional"])
    return {
        **subject,
        "evidencia": evidence,
        "evidencia_rotulo": EVIDENCE_LABELS.get(evidence, "Insuficiente"),
        "evidencia_ordem": EVIDENCE_ORDER.get(evidence, 0),
        "dominio_faixa": None if band is None else band["code"],
        "dominio_faixa_rotulo": None if band is None else band["label"],
        "dominio_provisorio": mastery is not None and evidence == "low",
        "dominio_mensuravel": mastery is not None and evidence in {"moderate", "high"},
        "topicos_mensuraveis": measurable,
        "topicos_provisorios": provisional,
        "topicos_sem_base": states["Não iniciado"] + states["Dados insuficientes"],
        "estados_topicos": states,
    }


def build_domain_map_snapshot(
    progress_snapshot: dict[str, Any] | Any,
    *,
    generated_at: str | None = None,
) -> DomainMapSnapshot:
    """Monta o mapa sem consultas adicionais e sem recalcular métricas oficiais."""
    data = (
        progress_snapshot.to_dict()
        if hasattr(progress_snapshot, "to_dict")
        else dict(progress_snapshot)
    )
    topics = [_topic_map_item(item) for item in data.get("topicos", [])]
    topics.sort(
        key=lambda item: (
            str(item.get("disciplina") or "").casefold(),
            str(item.get("topico") or "").casefold(),
        )
    )

    by_subject: dict[int, list[dict[str, Any]]] = {}
    for topic in topics:
        by_subject.setdefault(int(topic["disciplina_id"]), []).append(topic)

    subjects = []
    for subject in data.get("disciplinas", []):
        subject_id = int(subject["disciplina_id"])
        subjects.append(
            _discipline_map_item(subject, by_subject.get(subject_id, []))
        )
    subjects.sort(key=lambda item: str(item.get("disciplina") or "").casefold())

    def count_state(name: str) -> int:
        return sum(1 for item in topics if item["display_state"] == name)

    return DomainMapSnapshot(
        concurso_id=int(data.get("concurso_id") or 0),
        total_topics=len(topics),
        unstarted_topics=count_state("Não iniciado"),
        insufficient_topics=count_state("Dados insuficientes"),
        provisional_topics=count_state("Provisório"),
        measurable_topics=sum(1 for item in topics if item["mastery_measurable"]),
        consolidated_topics=count_state("Consolidado"),
        insufficient_evidence_topics=sum(
            1 for item in topics if item.get("evidencia") == "insufficient"
        ),
        low_evidence_topics=sum(1 for item in topics if item.get("evidencia") == "low"),
        moderate_evidence_topics=sum(
            1 for item in topics if item.get("evidencia") == "moderate"
        ),
        high_evidence_topics=sum(1 for item in topics if item.get("evidencia") == "high"),
        sufficient_evidence_topics=sum(
            1 for item in topics if item.get("evidencia") in {"moderate", "high"}
        ),
        disciplines=subjects,
        topics=topics,
        generated_at=(
            generated_at
            or data.get("generated_at")
            or datetime.now().astimezone().isoformat(timespec="seconds")
        ),
    )


def _normalize(value: Any) -> str:
    return str(value or "").strip().casefold()


def filter_domain_topics(
    topics: Iterable[dict[str, Any]],
    *,
    discipline: str = "",
    evidence: str = "",
    state: str = "",
    domain: str = "",
    consolidation: str = "",
    search: str = "",
) -> list[dict[str, Any]]:
    """Filtra tópicos sem reinterpretar as métricas oficiais."""
    discipline_n = _normalize(discipline)
    evidence_n = _normalize(evidence)
    state_n = _normalize(state)
    domain_n = _normalize(domain)
    consolidation_n = _normalize(consolidation)
    search_n = _normalize(search)
    result = []
    for item in topics:
        if discipline_n and _normalize(item.get("disciplina")) != discipline_n:
            continue
        if evidence_n and _normalize(item.get("evidencia")) != evidence_n:
            continue
        if state_n and _normalize(item.get("display_state")) != state_n:
            continue
        # Filtro de domínio deliberadamente exclui tópicos sem faixa.
        if domain_n and _normalize(item.get("domain_band")) != domain_n:
            continue
        if (
            consolidation_n
            and _normalize(item.get("consolidacao")) != consolidation_n
        ):
            continue
        if search_n:
            haystack = f"{item.get('disciplina', '')} {item.get('topico', '')}".casefold()
            if search_n not in haystack:
                continue
        result.append(item)
    return result


def sort_domain_topics(
    topics: Iterable[dict[str, Any]],
    order: str = "curricular",
) -> list[dict[str, Any]]:
    """Ordenações de apresentação; nunca representa prioridade de estudo."""
    items = list(topics)
    order = str(order or "curricular")
    curricular = lambda item: (
        str(item.get("disciplina") or "").casefold(),
        str(item.get("topico") or "").casefold(),
    )
    if order == "mastery_asc":
        return sorted(items, key=lambda item: (
            item.get("dominio_score") is None,
            float(item.get("dominio_score") or 0.0),
            *curricular(item),
        ))
    if order == "mastery_desc":
        return sorted(items, key=lambda item: (
            item.get("dominio_score") is None,
            -(float(item.get("dominio_score") or 0.0)),
            *curricular(item),
        ))
    if order == "evidence_desc":
        return sorted(items, key=lambda item: (
            -int(item.get("evidence_order") or 0),
            *curricular(item),
        ))
    if order == "coverage_desc":
        return sorted(items, key=lambda item: (
            item.get("cobertura_questoes") is None,
            -(float(item.get("cobertura_questoes") or 0.0)),
            *curricular(item),
        ))
    if order == "last_activity_desc":
        dated = [item for item in items if item.get("ultima_atividade")]
        undated = [item for item in items if not item.get("ultima_atividade")]
        dated.sort(
            key=lambda item: (
                str(item.get("ultima_atividade") or ""),
                *curricular(item),
            ),
            reverse=True,
        )
        undated.sort(key=curricular)
        return dated + undated
    return sorted(items, key=curricular)
