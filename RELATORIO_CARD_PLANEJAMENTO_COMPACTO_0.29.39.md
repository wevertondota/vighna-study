# VighnaStudy 0.29.39 — Card `Planejamento de hoje` mais compacto

## Objetivo
Reduzir a altura visual do card `Planejamento de hoje` para liberar mais espaço vertical na primeira dobra do Dashboard e permitir que os cards `Recomendação do algoritmo` e `Seu progresso` apareçam menos cortados.

## Arquivos alterados
- `main.py`
- `versao.py`
- `test_dashboard_planejamento_compacto_0_29_39.py`

## Ajustes aplicados
### 1) Altura geral do card
- `minimumHeight` do card reduzido de `174` para `160`.
- margens internas superiores e inferiores reduzidas.
- espaçamento vertical geral do layout reduzido.

### 2) Cabeçalho
- ícone do cabeçalho reduzido de `34x34` para `30x30`.
- menor distância entre ícone, título e data.

### 3) Área da meta
- gauge semicircular compactado:
  - tamanho mínimo reduzido;
  - altura máxima menor;
  - arco levemente mais fino;
  - texto central um pouco menor;
  - posicionamento mais alto no bloco.

### 4) Blocos operacionais
- `Revisões pendentes` e `Para concluir o dia` com margens e espaçamentos internos menores.
- linha `SEMANA` aproximada do conteúdo superior.
- botão `VER PLANEJAMENTO COMPLETO` fixado em altura mais enxuta.

## Resultado esperado
- primeira dobra do Dashboard mais eficiente em telas com altura limitada;
- maior chance de visualização completa dos cards `Recomendação do algoritmo` e `Seu progresso` sem corte inferior.

## Validação executada
- `python -m py_compile main.py versao.py`
- `python -m unittest -v test_dashboard_planejamento_compacto_0_29_39.py`

## Versão
- `0.29.39`
- build: `dashboard-planejamento-compacto-v1`
