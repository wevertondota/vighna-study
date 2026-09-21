from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent


class BancoUnicoTests(unittest.TestCase):
    def test_banco_e_backup_usam_caminho_central(self):
        banco = (ROOT / 'banco.py').read_text(encoding='utf-8')
        backup = (ROOT / 'backup.py').read_text(encoding='utf-8')
        self.assertIn('from caminhos import CAMINHO_BANCO, PASTA_DADOS', banco)
        self.assertIn('from caminhos import CAMINHO_BANCO, PASTA_BACKUPS, PASTA_DADOS', backup)
        self.assertNotIn('Path(sys.executable).resolve().parent / "estudos.db"', banco)

    def test_atualizador_nunca_regride_banco_principal(self):
        update = (ROOT / 'atualizar_exe.bat').read_text(encoding='utf-8')
        self.assertIn('copiar_banco_consistente.py "%CD%\\estudos.db" "%TEMP_DADOS%\\estudos.db"', update)
        self.assertNotIn('copy /Y "%TEMP_DADOS%\\estudos.db" "%CD%\\estudos.db"', update)
        self.assertNotIn('copy /Y "%TEMP_DADOS%\\estudos.db" "%SAIDA_NOVA%\\estudos.db"', update)
        self.assertIn('estudos_legado_dist_antes_unificacao.db', update)

    def test_build_nao_cria_segunda_copia_operacional(self):
        create = (ROOT / 'criar_exe.bat').read_text(encoding='utf-8')
        self.assertNotIn('copy /Y "estudos.db" "dist\\SistemaEstudos\\estudos.db"', create)

    def test_checkpoint_aponta_para_raiz(self):
        checkpoint = (ROOT / 'checkpoint.py').read_text(encoding='utf-8')
        trecho = checkpoint.split('def localizar_banco_ativo', 1)[1].split('PASTA_PROJETO =', 1)[0]
        self.assertIn('pasta / "estudos.db"', trecho)
        self.assertNotIn('sys.executable', trecho)


if __name__ == '__main__':
    unittest.main()
