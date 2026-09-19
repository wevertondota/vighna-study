# RELATÓRIO — AJUSTE DA ENGRENAGEM DE CONFIGURAÇÕES (VERSÃO LIMPA)

Data: 2026-09-18
Versão: 0.27.7
Build: `config-gear-clean`
Schema: 19

## Objetivo
Corrigir o resultado anterior do botão de Configurações, que ainda aparentava um quadrado interno no ícone. Substituir por uma engrenagem limpa, sem moldura e com fundo transparente.

## Alterações realizadas

### 1. Novo ícone limpo
O asset `assets/config_gear.png` foi substituído por uma nova engrenagem limpa:
- sem quadrado ao redor;
- sem fundo;
- pensada para uso como ícone de interface;
- em branco, para melhor contraste sobre o botão azul.

### 2. Integração
O código do botão permaneceu o mesmo, reaproveitando:
- `QIcon`;
- fundo normal do botão;
- fallback para `⚙` se o asset não existir.

## Arquivos alterados
- `assets/config_gear.png`
- `versao.py`

## Validação local
- `python -m py_compile main.py versao.py` ✅
- `python -m unittest -q test_gamificacao.py test_regularidade.py` ✅

## Resultado esperado
No cabeçalho:
- o botão de Configurações deve mostrar apenas uma engrenagem limpa;
- sem quadrado interno;
- usando somente o fundo azul normal do botão.
