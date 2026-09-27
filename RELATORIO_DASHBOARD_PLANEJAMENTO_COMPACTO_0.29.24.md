# VighnaStudy 0.29.24 — Planejamento compacto no Dashboard

## Objetivo
Substituir exclusivamente o card **Seu resumo de hoje**, localizado ao lado da **Recomendação do algoritmo**, por um card compacto de **Planejamento de hoje**, mantendo os demais cards e a seção completa de Planejamento inalterados.

## Alterações
- Título do card: `Planejamento de hoje`.
- Mantida a data corrente no cabeçalho.
- Métricas exibidas:
  - Meta de questões do dia;
  - Revisões pendentes;
  - Revisões já agendadas para os próximos 7 dias;
  - Situação das metas da semana.
- A barra inferior do card passa a representar o progresso da meta diária de questões.
- Adicionado botão `VER PLANEJAMENTO ↓` que expande a seção Planejamento e rola o Dashboard até ela.
- Os dados são reaproveitados das rotinas já existentes; não foi criada uma segunda lógica de planejamento.
- Foco, Seu progresso, Recomendação do algoritmo, Estudo por questões e Planejamento completo não foram redesenhados.

## Versão
- Versão: `0.29.24`
- Build: `dashboard-planejamento-compacto-v1`
- Schema: `23` (inalterado)

## Validação
- `python -m py_compile main.py versao.py tema.py banco.py`: OK
- `test_dashboard_inteligencia.py` + `test_startup_rapido.py`: 9/9 OK
- `PRAGMA integrity_check`: `ok`
- `PRAGMA foreign_key_check`: 0 violações
- `estudos.db`: não modificado pela alteração

## Arquivos modificados
- `main.py`
- `versao.py`
- `test_dashboard_inteligencia.py`
