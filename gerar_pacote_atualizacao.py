"""Ferramenta do desenvolvedor para gerar pacotes compactos verificáveis.

Exemplo (executar na raiz de uma nova versão já alterada):
python gerar_pacote_atualizacao.py pacote.zip --base-version 0.29.59 \
    --base-build updates-center-v1 --description "Correção visual" versao.py tema.py
"""
import argparse
import json
import zipfile
from pathlib import Path
from vighna_update_engine import FORMAT, hash_file, valid_source_path, version_from_file


def main():
    p = argparse.ArgumentParser()
    p.add_argument('output')
    p.add_argument('--base-version', required=True)
    p.add_argument('--base-build', required=True)
    p.add_argument('--description', required=True)
    p.add_argument('files', nargs='+')
    args = p.parse_args()
    root = Path(__file__).resolve().parent
    files = sorted(set(args.files + ['versao.py']))
    if any(not valid_source_path(f) or not (root / f).is_file() for f in files):
        p.error('Somente fontes permitidas existentes, relativas à raiz, podem ser empacotadas.')
    version, build, schema = version_from_file(root / 'versao.py')
    if (version, build) == (args.base_version, args.base_build):
        p.error('Atualize versao.py antes de gerar o pacote.')
    manifest = {'format':FORMAT, 'base_version':args.base_version,'base_build':args.base_build,
                'target_version':version,'target_build':build,'schema':schema,
                'description':args.description,'files':{f:hash_file(root/f) for f in files}}
    output = Path(args.output).resolve()
    if output.exists():
        p.error('O destino já existe; não é permitido sobrescrever um pacote sem revisão.')
    with zipfile.ZipFile(output, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('manifest.json', json.dumps(manifest, indent=2, ensure_ascii=False))
        for f in files:
            archive.write(root/f, f)
    print(output, '\n', hash_file(output))


if __name__ == '__main__':
    main()
