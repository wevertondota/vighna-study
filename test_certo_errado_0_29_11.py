"""Teste funcional não gráfico do formato CERTO_ERRADO do VighnaStudy 0.29.11."""

from __future__ import annotations

import gc
import shutil
import sqlite3
import tempfile
from pathlib import Path

import banco
from importador_pdf import analisar_vpq_1_0


def testar_importacao_vpq():
    texto = """VIGHNA PDF — VPQ 1.1
DISCIPLINA: Direito Constitucional
TÍTULO: Título de teste
CAPÍTULO: Capítulo de teste
FONTE: Teste automatizado
QUANTIDADE: 3
FORMATO: CERTO-ERRADO

QUESTÃO 1
A afirmação número um está correta.
GABARITO: CERTO
EXPLICAÇÃO: Item correto.

QUESTÃO 2
A afirmação número dois está incorreta.
GABARITO: ERRADO
EXPLICAÇÃO: Item incorreto.

QUESTÃO 3
A afirmação número três está correta.
GABARITO: C
EXPLICAÇÃO: Abreviação aceita.
"""
    analise = analisar_vpq_1_0(texto, [])
    assert not analise.get("vpq_bloqueia_importacao"), analise
    assert analise.get("vpq_metadados", {}).get("formato") == "CERTO_ERRADO"
    questoes = analise["questoes"]
    assert len(questoes) == 3
    assert [q["gabarito"] for q in questoes] == ["C", "E", "C"]
    for questao in questoes:
        assert questao["tipo_questao"] == "CERTO_ERRADO"
        assert [a["letra"] for a in questao["alternativas"]] == ["C", "E"]


def testar_banco_e_simulado():
    origem = Path(__file__).with_name("estudos.db")
    assert origem.exists(), "estudos.db de teste não encontrado"

    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as pasta:
        destino = Path(pasta) / "estudos.db"
        shutil.copy2(origem, destino)
        caminho_original = banco.CAMINHO_BANCO
        banco.CAMINHO_BANCO = str(destino)
        try:
            banco.criar_banco()
            concurso_id = banco.obter_concurso_ativo()[0]

            with sqlite3.connect(destino) as conexao:
                colunas = {
                    linha[1]
                    for linha in conexao.execute("PRAGMA table_info(questoes)")
                }
                assert "tipo_questao" in colunas
                linha = conexao.execute(
                    """
                    SELECT t.id, d.id
                    FROM topicos t
                    JOIN disciplinas d ON d.id = t.disciplina_id
                    JOIN topico_concurso_importancia tc
                      ON tc.topico_id = t.id
                     AND tc.concurso_id = ?
                     AND tc.incluido = 1
                    JOIN disciplina_concurso_inclusao dc
                      ON dc.disciplina_id = d.id
                     AND dc.concurso_id = ?
                     AND dc.incluido = 1
                    LIMIT 1
                    """,
                    (concurso_id, concurso_id),
                ).fetchone()
            assert linha, "Nenhum tópico disponível para o teste"
            topico_id, disciplina_id = map(int, linha)

            questao_id = banco.criar_questao(
                topico_id,
                "Item Certo/Errado de teste.",
                [
                    {"letra": "C", "texto": "Certo", "correta": True},
                    {"letra": "E", "texto": "Errado", "correta": False},
                ],
                explicacao="Teste automatizado.",
                fonte="teste_certo_errado_0_29_11.py",
                tipo_questao="CERTO_ERRADO",
            )

            questao = banco.obter_questao(questao_id)
            assert questao["tipo_questao"] == "CERTO_ERRADO"
            assert [a["letra"] for a in questao["alternativas"]] == ["C", "E"]

            disponibilidade = banco.obter_disponibilidade_simulado_disciplinas(
                concurso_id,
                tipo_questao="CERTO_ERRADO",
            )
            por_disciplina = {int(item["disciplina_id"]): item for item in disponibilidade}
            assert por_disciplina[disciplina_id]["disponiveis"] >= 1

            equilibrado = banco.montar_simulado_inteligente(
                concurso_id,
                1,
                estrategia="equilibrado",
                tipo_questao="CERTO_ERRADO",
            )
            assert equilibrado["fila"]
            assert all(q["tipo_questao"] == "CERTO_ERRADO" for q in equilibrado["fila"])

            personalizado = banco.montar_simulado_personalizado(
                concurso_id,
                {disciplina_id: 1},
                tipo_questao="CERTO_ERRADO",
            )
            assert personalizado["fila"]
            assert all(q["tipo_questao"] == "CERTO_ERRADO" for q in personalizado["fila"])
        finally:
            banco.CAMINHO_BANCO = caminho_original
            gc.collect()


def main():
    testar_importacao_vpq()
    testar_banco_e_simulado()
    print("VighnaStudy 0.29.11: CERTO_ERRADO OK")


if __name__ == "__main__":
    main()
