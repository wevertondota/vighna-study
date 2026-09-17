# Correção — checkpoint_manifest.json duplicado

Data: 2026-09-17
Versão: 0.23.5

## Sintoma
Ao executar `python testes_smoke.py` depois de extrair um checkpoint diretamente na raiz do projeto, a geração do checkpoint de teste podia emitir `UserWarning: Duplicate name: 'checkpoint_manifest.json'` e falhar com `SHA-256 não corresponde ao manifesto`.

## Causa
O arquivo `checkpoint_manifest.json` pertence ao próprio ZIP de checkpoint. Depois de extraído na raiz do projeto, ele era identificado como um `.json` normal por `_arquivos_do_projeto()`. Na geração seguinte, o manifesto antigo era adicionado ao ZIP como arquivo do projeto e, ao final, um novo `checkpoint_manifest.json` era gravado com o mesmo nome.

## Correção
`checkpoint_manifest.json` foi adicionado a `ARQUIVOS_IGNORADOS` em `checkpoint.py`. Assim, manifestos extraídos na raiz são ignorados pelo inventário e o gerador grava somente o manifesto novo do checkpoint atual.

## Validação
- `python -m py_compile checkpoint.py testes_smoke.py main.py tema.py foco.py banco.py`
- `python testes_smoke.py`
- Resultado: `VighnaStudy 0.23.5: testes smoke OK`
- Validação adicional recomendada: extrair o checkpoint corrigido em uma pasta limpa e executar novamente os testes smoke.
