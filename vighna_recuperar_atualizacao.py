"""Recuperação manual de emergência após interrupção elétrica/travamento.

Não restaura o banco de estudos nem executa migrações; reverte apenas
código e executável registrados como transação incompleta.
"""
import os
import subprocess
from pathlib import Path
from vighna_update_engine import recover_incomplete_updates


def main():
    root = Path(__file__).resolve().parent
    if os.name == 'nt':
        proc = subprocess.run(['tasklist','/FI','IMAGENAME eq VighnaStudy.exe','/NH'],
                              capture_output=True,text=True,errors='replace')
        if proc.returncode != 0 or any(line.strip().lower().startswith('vighnastudy.exe ')
                                       for line in proc.stdout.splitlines()):
            raise RuntimeError('Feche todas as instâncias do Vighna antes de recuperar.')
    recovered = recover_incomplete_updates(root)
    if recovered:
        print('Instalações incompletas recuperadas:', ', '.join(recovered))
    else:
        print('Nenhuma instalação interrompida identificada.')


if __name__ == '__main__':
    main()
