# VighnaStudy 0.29.37 — Card `Planejamento de hoje` alinhado à referência

## Objetivo
Ajustar o card `Planejamento de hoje` para ficar visualmente o mais próximo possível da referência aprovada pelo usuário, dentro da interface real do VighnaStudy.

## Arquivos alterados
- `main.py`
- `tema.py`
- `versao.py`
- `test_dashboard_planejamento_referencia_0_29_37.py`

## Ajustes aplicados
### 1) Card `Planejamento de hoje`
- migração do fundo para gradiente verde-esmeralda, com a mesma família cromática do mock aprovado;
- cabeçalho mantido com ícone à esquerda, data abaixo do título e selo de status à direita;
- reforço tipográfico para melhor leitura sobre o fundo verde.

### 2) Meta de questões
- substituição do bloco textual central por um **indicador em arco semicircular**;
- valor principal centralizado no formato `atual / meta`, como na referência;
- preservação da lógica já existente de atualização da meta diária.

### 3) Bloco operacional e semana
- remoção do contêiner escuro interno para aproximar a composição da referência;
- manutenção das colunas `Revisões pendentes` e `Para concluir o dia`;
- badges semanais mantidos e refinados para conversar melhor com o card verde.

### 4) CTA inferior
- botão `VER PLANEJAMENTO COMPLETO →` ajustado para um tom escuro translúcido, seguindo a estética da referência.

## Validação executada
- `python -m py_compile main.py tema.py versao.py`
- `python -m unittest -v test_dashboard_planejamento_referencia_0_29_37.py`

## Versão
- `0.29.37`
- build: `dashboard-planejamento-referencia-v1`
