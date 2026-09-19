"""Testes do Passo 9: Mapa de Domínio V2."""

from __future__ import annotations

import inspect
import unittest

import mapa_dominio
from mapa_dominio import (
    build_domain_map_snapshot,
    domain_band,
    filter_domain_topics,
    sort_domain_topics,
    topic_display_state,
)


def topic(
    topic_id=1,
    *,
    subject_id=1,
    subject="Direito Penal",
    name="Furto",
    attempts=0,
    mastery=None,
    evidence="insufficient",
    coverage=None,
    consolidation="insufficient_data",
    unique=0,
    reviews=0,
    last=None,
):
    return {
        "topico_id": topic_id,
        "disciplina_id": subject_id,
        "disciplina": subject,
        "topico": name,
        "tentativas": attempts,
        "questoes_unicas": unique,
        "dominio_score": mastery,
        "dominio_estado": "insufficient_data" if mastery is None else "ok",
        "evidencia": evidence,
        "evidencia_rotulo": evidence.title(),
        "cobertura_questoes": coverage,
        "consolidacao": consolidation,
        "consolidacao_estado": (
            "insufficient_data" if consolidation == "insufficient_data" else "ok"
        ),
        "revisoes": reviews,
        "ultima_atividade": last,
        "desempenho_recente": None,
        "tendencia_desempenho": None,
        "questoes_ativas": 10,
        "questoes_respondidas": unique,
    }


def snapshot(topics, subjects=None):
    if subjects is None:
        subject_ids = sorted({item["disciplina_id"] for item in topics})
        subjects = []
        for subject_id in subject_ids:
            first = next(item for item in topics if item["disciplina_id"] == subject_id)
            subjects.append({
                "disciplina_id": subject_id,
                "disciplina": first["disciplina"],
                "total_topicos": sum(
                    1 for item in topics if item["disciplina_id"] == subject_id
                ),
                "cobertura_topicos": None,
                "cobertura_questoes": None,
                "evidencia": "insufficient",
                "evidencia_rotulo": "Insuficiente",
                "consolidados": 0,
                "dominio": None,
                "dominio_estado": "insufficient_data",
            })
    return {
        "concurso_id": 40,
        "topicos": topics,
        "disciplinas": subjects,
        "generated_at": "2026-09-18T15:00:00-03:00",
    }


class DomainMapTests(unittest.TestCase):
    def test_a_unstarted_topic(self):
        result = build_domain_map_snapshot(snapshot([topic()])).to_dict()
        self.assertEqual(result["unstarted_topics"], 1)
        self.assertEqual(result["topics"][0]["display_state"], "Não iniciado")

    def test_b_single_correct_attempt_remains_insufficient(self):
        item = topic(attempts=1, mastery=None, evidence="insufficient", unique=1)
        result = build_domain_map_snapshot(snapshot([item])).topics[0]
        self.assertEqual(result["display_state"], "Dados insuficientes")
        self.assertIsNone(result["domain_band"])

    def test_c_low_evidence_is_provisional(self):
        item = topic(attempts=4, mastery=92.0, evidence="low", coverage=40.0)
        result = build_domain_map_snapshot(snapshot([item])).topics[0]
        self.assertEqual(result["display_state"], "Provisório")
        self.assertTrue(result["mastery_provisional"])
        self.assertFalse(result["mastery_measurable"])
        self.assertEqual(result["domain_band"], "alto")

    def test_d_moderate_evidence_is_measurable(self):
        item = topic(attempts=12, mastery=68.0, evidence="moderate")
        result = build_domain_map_snapshot(snapshot([item])).topics[0]
        self.assertEqual(result["display_state"], "Mensurável")
        self.assertTrue(result["mastery_measurable"])

    def test_e_high_evidence_is_measurable(self):
        item = topic(attempts=30, mastery=88.0, evidence="high")
        result = build_domain_map_snapshot(snapshot([item])).topics[0]
        self.assertEqual(result["display_state"], "Mensurável")
        self.assertTrue(result["mastery_measurable"])

    def test_f_none_mastery_never_becomes_zero(self):
        result = build_domain_map_snapshot(snapshot([
            topic(attempts=8, mastery=None, evidence="moderate")
        ])).topics[0]
        self.assertIsNone(result["dominio_score"])
        self.assertIsNone(result["domain_band"])
        self.assertEqual(result["display_state"], "Dados insuficientes")

    def test_g_zero_mastery_is_valid_low_band(self):
        result = build_domain_map_snapshot(snapshot([
            topic(attempts=12, mastery=0.0, evidence="moderate")
        ])).topics[0]
        self.assertEqual(result["dominio_score"], 0.0)
        self.assertEqual(result["domain_band"], "baixo")
        self.assertEqual(result["display_state"], "Mensurável")

    def test_h_official_consolidation_wins_display_state(self):
        result = build_domain_map_snapshot(snapshot([
            topic(attempts=30, mastery=90.0, evidence="high",
                  consolidation="consolidated")
        ])).topics[0]
        self.assertEqual(result["display_state"], "Consolidado")
        self.assertEqual(result["consolidation_label"], "Consolidado")

    def test_i_high_mastery_does_not_imply_consolidation(self):
        result = build_domain_map_snapshot(snapshot([
            topic(attempts=30, mastery=95.0, evidence="high",
                  consolidation="not_consolidated")
        ])).topics[0]
        self.assertEqual(result["display_state"], "Mensurável")
        self.assertEqual(result["consolidation_label"], "Não consolidado")

    def test_j_coverage_and_mastery_are_independent(self):
        low_mastery = topic(1, attempts=20, mastery=35.0, evidence="high", coverage=100.0)
        high_mastery = topic(2, attempts=6, mastery=90.0, evidence="low", coverage=20.0)
        result = build_domain_map_snapshot(snapshot([low_mastery, high_mastery])).topics
        self.assertEqual(result[0]["cobertura_questoes"], 100.0)
        self.assertEqual(result[0]["domain_band"], "baixo")
        self.assertEqual(result[1]["cobertura_questoes"], 20.0)
        self.assertEqual(result[1]["domain_band"], "alto")
        self.assertEqual(result[1]["display_state"], "Provisório")

    def test_k_domain_bands_boundaries(self):
        self.assertEqual(domain_band(49.9)["code"], "baixo")
        self.assertEqual(domain_band(50)["code"], "intermediario")
        self.assertEqual(domain_band(70)["code"], "bom")
        self.assertEqual(domain_band(85)["code"], "alto")
        self.assertIsNone(domain_band(None))

    def test_l_counts_are_separate(self):
        items = [
            topic(1),
            topic(2, attempts=1),
            topic(3, attempts=4, mastery=72, evidence="low"),
            topic(4, attempts=12, mastery=72, evidence="moderate"),
            topic(5, attempts=30, mastery=90, evidence="high", consolidation="consolidated"),
        ]
        result = build_domain_map_snapshot(snapshot(items))
        self.assertEqual(result.unstarted_topics, 1)
        self.assertEqual(result.insufficient_topics, 1)
        self.assertEqual(result.provisional_topics, 1)
        self.assertEqual(result.measurable_topics, 2)
        self.assertEqual(result.consolidated_topics, 1)
        self.assertEqual(result.sufficient_evidence_topics, 2)

    def test_m_subject_uses_official_subject_mastery(self):
        subjects = [{
            "disciplina_id": 1,
            "disciplina": "Direito Penal",
            "total_topicos": 2,
            "cobertura_topicos": 100.0,
            "cobertura_questoes": 70.0,
            "evidencia": "high",
            "evidencia_rotulo": "Alta",
            "consolidados": 0,
            "dominio": 81.0,
            "dominio_estado": "ok",
        }]
        items = [
            topic(1, attempts=10, mastery=10, evidence="moderate"),
            topic(2, attempts=100, mastery=100, evidence="high"),
        ]
        result = build_domain_map_snapshot(snapshot(items, subjects)).disciplines[0]
        self.assertEqual(result["dominio"], 81.0)
        self.assertNotEqual(result["dominio"], 55.0)
        self.assertEqual(result["evidencia"], "high")

    def test_n_subject_without_base_stays_insufficient(self):
        result = build_domain_map_snapshot(snapshot([topic()])).disciplines[0]
        self.assertIsNone(result["dominio"])
        self.assertEqual(result["evidencia"], "insufficient")
        self.assertEqual(result["topicos_sem_base"], 1)

    def test_o_filter_by_evidence(self):
        items = build_domain_map_snapshot(snapshot([
            topic(1, attempts=4, mastery=70, evidence="low"),
            topic(2, attempts=20, mastery=70, evidence="high"),
        ])).topics
        result = filter_domain_topics(items, evidence="high")
        self.assertEqual([item["topico_id"] for item in result], [2])

    def test_p_filter_by_state(self):
        items = build_domain_map_snapshot(snapshot([
            topic(1),
            topic(2, attempts=4, mastery=70, evidence="low"),
        ])).topics
        result = filter_domain_topics(items, state="Provisório")
        self.assertEqual([item["topico_id"] for item in result], [2])

    def test_q_filter_by_domain_excludes_none(self):
        items = build_domain_map_snapshot(snapshot([
            topic(1),
            topic(2, attempts=20, mastery=40, evidence="moderate"),
        ])).topics
        result = filter_domain_topics(items, domain="baixo")
        self.assertEqual([item["topico_id"] for item in result], [2])

    def test_r_filter_searches_subject_and_topic(self):
        items = build_domain_map_snapshot(snapshot([
            topic(1, subject="Direito Penal", name="Furto"),
            topic(2, subject="CTB", name="Velocidade"),
        ])).topics
        self.assertEqual(len(filter_domain_topics(items, search="furto")), 1)
        self.assertEqual(len(filter_domain_topics(items, search="ctb")), 1)


    def test_s_filter_by_consolidation(self):
        items = build_domain_map_snapshot(snapshot([
            topic(1, attempts=20, mastery=82, evidence="high",
                  consolidation="consolidated"),
            topic(2, attempts=20, mastery=72, evidence="high",
                  consolidation="not_consolidated"),
            topic(3, attempts=1, mastery=None, evidence="insufficient",
                  consolidation="insufficient_data"),
        ])).topics
        result = filter_domain_topics(items, consolidation="consolidated")
        self.assertEqual([item["topico_id"] for item in result], [1])

    def test_s_curricular_order(self):
        items = build_domain_map_snapshot(snapshot([
            topic(1, subject="Z", name="B"),
            topic(2, subject="A", name="C"),
            topic(3, subject="A", name="A"),
        ])).topics
        ordered = sort_domain_topics(items, "curricular")
        self.assertEqual([item["topico_id"] for item in ordered], [3, 2, 1])

    def test_t_mastery_order_keeps_none_last(self):
        items = build_domain_map_snapshot(snapshot([
            topic(1),
            topic(2, attempts=10, mastery=20, evidence="moderate"),
            topic(3, attempts=10, mastery=90, evidence="moderate"),
        ])).topics
        asc = sort_domain_topics(items, "mastery_asc")
        desc = sort_domain_topics(items, "mastery_desc")
        self.assertEqual([item["topico_id"] for item in asc], [2, 3, 1])
        self.assertEqual([item["topico_id"] for item in desc], [3, 2, 1])

    def test_u_module_has_no_database_dependency(self):
        source = inspect.getsource(mapa_dominio)
        self.assertNotIn("import banco", source)
        self.assertNotIn("sqlite3", source)

    def test_v_topic_display_state_is_pure_presentation(self):
        item = topic(attempts=20, mastery=80, evidence="high",
                     consolidation="not_consolidated")
        self.assertEqual(topic_display_state(item), "Mensurável")
        self.assertEqual(item["consolidacao"], "not_consolidated")

    def test_w_last_activity_is_preserved(self):
        result = build_domain_map_snapshot(snapshot([
            topic(attempts=5, mastery=70, evidence="low", last="2026-09-18T10:00:00-03:00")
        ])).topics[0]
        self.assertEqual(result["ultima_atividade"], "2026-09-18T10:00:00-03:00")

    def test_x_snapshot_preserves_metric_version_contract(self):
        result = build_domain_map_snapshot(snapshot([topic()]))
        self.assertEqual(result.metric_version, "1")
        self.assertEqual(result.snapshot_version, "domain_map_v2")


if __name__ == "__main__":
    unittest.main()
