# VighnaStudy 0.29.36 — Refino do gradiente do card Seu progresso

## Objetivo
Aproximar o fundo verde do card `Seu progresso` da referência visual enviada, sem alterar sua estrutura, conteúdo ou comportamento.

## Alteração visual
O gradiente anterior era diagonal e mantinha verde relativamente forte até a base. O novo gradiente passa a ser predominantemente vertical, com sete pontos de transição:

- topo verde-esmeralda vivo: `#07A975`;
- transições intermediárias: `#0D9069`, `#107A5D`, `#136652`, `#184B42`, `#1A3939`;
- base azul-petróleo escura: `#1D2831`.

A borda foi suavizada para `#2AA182`, mais próxima do contorno verde discreto da referência.

## Arquivos alterados
- `tema.py`
- `versao.py`
- `test_dashboard_palette_reference_0_29_35.py`

## Validação
- compilação sintática de `tema.py`, `versao.py` e `main.py`;
- teste de regressão da paleta do Dashboard;
- verificação explícita da direção vertical e dos sete stops do gradiente.

## Versão
- `0.29.36`
- build: `dashboard-progress-gradient-reference-v2`
