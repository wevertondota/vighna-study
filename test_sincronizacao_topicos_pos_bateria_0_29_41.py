import unittest
from pathlib import Path

MAIN = Path('main.py').read_text(encoding='utf-8')
VERSAO = Path('versao.py').read_text(encoding='utf-8')


class TestSincronizacaoTopicosPosBateria(unittest.TestCase):
    def test_resolvedor_invalida_cache_apos_sessao(self):
        self.assertIn('def _notificar_dados_alterados_raiz(widget, escopo="all"):', MAIN)
        self.assertIn('def _notificar_dados_pos_sessao(self):', MAIN)
        self.assertIn('_notificar_dados_alterados_raiz(self, "questoes")', MAIN)
        self.assertIn('self._notificar_dados_pos_sessao()\n        self.accept()', MAIN)

    def test_encerramento_por_x_tambem_invalida(self):
        trecho = MAIN[MAIN.index('def closeEvent(\n        self,\n        event\n    ):', MAIN.index('class JanelaResolverQuestoes')):]
        self.assertIn('self._notificar_dados_pos_sessao()', trecho)
        self.assertIn('self.reject()', trecho)

    def test_topico_com_capitulos_usa_nome_original(self):
        self.assertIn('nome_topico = item.data(Qt.UserRole + 4) or item.text()', MAIN)
        self.assertIn('JanelaTopico(\n            item.data(Qt.UserRole),\n            str(nome_topico),', MAIN)

    def test_revisao_manual_invalida_antes_de_recarregar(self):
        self.assertIn(
            'self.notificar_dados_alterados("revisoes")\n            self.carregar_topicos()',
            MAIN,
        )

    def test_versao(self):
        self.assertIn('VIGHNA_VERSION = "0.29.41"', VERSAO)
        self.assertIn('VIGHNA_BUILD = "sincronizacao-topicos-pos-bateria-v1"', VERSAO)


if __name__ == '__main__':
    unittest.main()
