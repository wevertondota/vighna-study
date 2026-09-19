# RELATÓRIO — CORREÇÃO DOS BOTÕES DE ACESSO RÁPIDO

Data: 2026-09-19
Versão: 0.28.3
Build: `quick-access-height-fix`
Schema: 19

## Problema observado
Os botões da área **Acessos rápidos** apareciam com a borda inferior recortada no Dashboard.

## Diagnóstico
O problema não estava na largura dos botões nem no card em si. Havia uma restrição contraditória de altura:

- os botões tinham `setMaximumHeight(36)` no `main.py`;
- o tema aplica `min-height`, `padding` e bordas aos mesmos `QPushButton`;
- em Qt Style Sheets, essa combinação pode produzir um `sizeHint` maior que 36 px;
- o `maximumHeight` forçava o widget a uma altura menor que a necessária para renderizar completamente a moldura, fazendo a borda inferior parecer cortada.

## Correção aplicada
Foi removido o limite máximo de 36 px dos quatro botões de acesso rápido:

- Pausa;
- Estatísticas;
- Relatórios;
- Calendário.

Mantivemos:

- altura mínima de 34 px;
- expansão horizontal;
- política vertical fixa baseada no `sizeHint` calculado pelo Qt.

Assim, o tema pode determinar a altura visual necessária e o rodapé de Acessos rápidos cresce poucos pixels quando necessário, sem recorte.

## Arquivos alterados
- `main.py`
- `versao.py`

## Validação
- `python -m py_compile main.py versao.py` ✅
- `python -m unittest discover -q` → **212 testes OK** ✅
- `python testes_smoke.py` ✅
- SQLite `integrity_check` = `ok` ✅
- SQLite `foreign_key_check` = vazio ✅

## Observação
A correção foi propositalmente mínima: não alteramos o design, as cores, os ícones ou os temas Escuro/Futurista. Apenas removemos a restrição que causava o recorte.
