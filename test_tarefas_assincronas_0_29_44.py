import sys
import types
import unittest
from pathlib import Path

import aquecimento_dados


ROOT = Path(__file__).resolve().parent
MAIN = (ROOT / "main.py").read_text(encoding="utf-8")
VERSAO = (ROOT / "versao.py").read_text(encoding="utf-8")
TAREFAS = (ROOT / "tarefas_pesadas.py").read_text(encoding="utf-8")


class TarefasAssincronas044Tests(unittest.TestCase):
    def test_versao_build(self):
        self.assertIn('VIGHNA_VERSION = "0.29.44"', VERSAO)
        self.assertIn('VIGHNA_BUILD = "tarefas-assincronas-overlay-v1"', VERSAO)

    def test_worker_fora_da_thread_ui(self):
        self.assertIn("class CoordenadorTarefas(QObject)", TAREFAS)
        self.assertIn("QThreadPool", TAREFAS)
        self.assertIn("class _Worker(QRunnable)", TAREFAS)
        self.assertIn("self.pool.setMaxThreadCount(1)", TAREFAS)

    def test_resposta_invalida_como_tentativa_nao_catalogo(self):
        self.assertIn('_notificar_dados_alterados_raiz(self, "tentativas")', MAIN)
        self.assertIn('{"all", "questoes", "tentativas", "topicos", "revisoes"}', MAIN)

    def test_fechamento_tem_warm_cache_e_backup_assincronos(self):
        self.assertIn("def _executar_tarefa_fechamento(self):", MAIN)
        self.assertIn('"fechamento",', MAIN)
        self.assertIn('fazer_backup("fechamento")', MAIN)
        self.assertIn("aquecer_dados_derivados(", MAIN)
        self.assertIn("evento.ignore()", MAIN)

    def test_preparo_estatisticas_nao_troca_aba_visivel(self):
        self.assertIn("self.abas_estatisticas.setUpdatesEnabled(False)", MAIN)
        self.assertIn("self.abas_estatisticas.setUpdatesEnabled(True)", MAIN)
        self.assertIn("Atualizando todas as abas com os novos snapshots sem trocar a aba visível.", MAIN)

    def test_fechamento_pula_repintura_desnecessaria(self):
        self.assertIn("Se o usuário pediu para fechar enquanto o worker concluía", MAIN)
        self.assertIn("Atualização concluída; preparando a próxima sessão e o backup.", MAIN)

    def test_aquecimento_orquestra_snapshots_sem_qt(self):
        chamadas = []
        fake_banco = types.ModuleType("banco")

        def registrar(nome, retorno):
            def fn(*args, **kwargs):
                chamadas.append((nome, args, kwargs))
                return retorno
            return fn

        fake_banco.obter_snapshot_progresso_edital = registrar(
            "progresso", {"topicos": [], "disciplinas": []}
        )
        fake_banco.obter_metricas_globais_nucleo = registrar("global", {"metrics": {}})
        fake_banco.obter_estatisticas_disciplinas = registrar("disciplinas", [])
        fake_banco.obter_snapshot_regularidade = registrar("regularidade", {"r": 1})
        fake_banco.obter_analise_temporal = registrar("temporal", {"t": 1})
        fake_banco.obter_prioridades_sessao_adaptativa = registrar("fila", [])
        fake_banco.obter_snapshot_gamificacao = registrar("gamificacao", {"g": 1})
        fake_banco.listar_caderno_erros_questoes = registrar("erros", [])
        fake_banco.obter_relatorio_estrategico = registrar("relatorio", {"x": 1})

        fake_evolucao = types.ModuleType("evolucao")
        fake_evolucao.obter_evolucao_historica = registrar("historico", {"h": 1})

        antigo_banco = sys.modules.get("banco")
        antigo_evolucao = sys.modules.get("evolucao")
        sys.modules["banco"] = fake_banco
        sys.modules["evolucao"] = fake_evolucao
        etapas = []
        try:
            resultado = aquecimento_dados.aquecer_dados_derivados(
                7,
                hoje="2026-10-01",
                tendencias_inicio="2026-09-01",
                tendencias_fim="2026-09-30",
                relatorio_inicio="2026-09-01",
                relatorio_fim="2026-09-30",
                reportar=lambda t, d, p: etapas.append((p, t)),
            )
        finally:
            if antigo_banco is None:
                sys.modules.pop("banco", None)
            else:
                sys.modules["banco"] = antigo_banco
            if antigo_evolucao is None:
                sys.modules.pop("evolucao", None)
            else:
                sys.modules["evolucao"] = antigo_evolucao

        nomes = [item[0] for item in chamadas]
        self.assertIn("progresso", nomes)
        self.assertIn("global", nomes)
        self.assertIn("temporal", nomes)
        self.assertIn("fila", nomes)
        self.assertIn("relatorio", nomes)
        self.assertTrue(resultado["gamificacao"])
        self.assertEqual(etapas[-1][0], 100)


if __name__ == "__main__":
    unittest.main()
