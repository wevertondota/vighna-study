# VighnaStudy — Design System
## Modo Foco — Integração no Resolvedor

**Data:** 2026-10-08
**Versão:** 0.29.59
**Build:** `calendar-week-forecast-v1`
**Schema:** 25

## 1. Base e objetivo

A implementação foi realizada sobre a base oficial validada:

`VighnaStudy_0.29.59_DesignSystem_Cards_Globais_Bloco_C_COMPLETO.zip`

SHA-256 da base:
`7e5cf5fc582d1638eda0a0ef108672e2ae2edbb5811bfcfd4c57f342efa86aa3`

O objetivo deste bloco foi centralizar exclusivamente a faixa contextual do **Modo Foco embutida no Resolvedor de questões**, identificada por `questionSessionFocusBar`, sem redesenho e sem alteração de comportamento.

A caracterização anterior havia confirmado que `JanelaModoFoco` e `JanelaPosFoco` já estavam centralizadas. A única pendência material restante do macroescopo eram 15 ocorrências cromáticas físicas na faixa de foco do Resolvedor, correspondentes a 9 papéis visuais.

## 2. Escopo implementado

Foram centralizados somente:

- superfície da faixa `QFrame#questionSessionFocusBar`;
- borda da faixa;
- texto de estado `QLabel#questionSessionFocusState`;
- superfície, texto e borda dos `QPushButton#subtleButton` descendentes da faixa;
- superfície, texto e borda no estado `:hover` desses botões.

Os botões foram deliberadamente isolados pelo seletor descendente:

`QDialog#questionSolverDialog QFrame#questionSessionFocusBar QPushButton#subtleButton`

Assim, o contrato compartilhado `subtleButton` usado em outras partes do programa não foi alterado.

Ficaram fora do escopo: geometria, espaçamentos, tipografia, textos, ícones, callbacks, atalhos, objectNames, lógica do Modo Foco, `main.py`, `foco.py`, banco de dados e qualquer redesenho.

## 3. Tokens adicionados

Foram adicionados 9 tokens de componente, todos do tipo **COLOR**:

1. `focus_mode.session_bar_surface`
2. `focus_mode.session_bar_border`
3. `focus_mode.session_bar_status_text`
4. `focus_mode.session_bar_button_surface`
5. `focus_mode.session_bar_button_text`
6. `focus_mode.session_bar_button_border`
7. `focus_mode.session_bar_button_hover_surface`
8. `focus_mode.session_bar_button_hover_text`
9. `focus_mode.session_bar_button_hover_border`

### Contagem do Design System

| Métrica | Antes | Depois |
|---|---:|---:|
| Tokens semânticos | 102 | 102 |
| Tokens de componente | 914 | 923 |
| Total de tokens | 1016 | 1025 |
| Cores | 940 | 949 |
| Gradientes | 76 | 76 |
| `focus_mode.*` | 44 | 53 |
| `post_focus.*` | 39 | 39 |

Nenhum gradiente novo foi necessário.

## 4. Valores físicos preservados

| Papel | Claro | Escuro | Futurista |
|---|---|---|---|
| Faixa — superfície | `#F7F9FC` | `#151E2A` | `#151D28` |
| Faixa — borda | `#E1E6ED` | `#303D4E` | `#354151` |
| Estado — texto | `#536173` | `#A7B4C3` | `#B1BCC9` |
| Botão — superfície | `#FFFFFF` | `#162333` | `#232B36` |
| Botão — texto | `#334155` | `#DCE6F0` | `#D1D9E2` |
| Botão — borda | `#CFD8E3` | `#33475E` | `#5A6472` |
| Hover — superfície | `#F6FBFF` | `#1C3145` | `#2C3643` |
| Hover — texto | `#235F98` | `#9BD5FF` | `#FFFFFF` |
| Hover — borda | `#9FC7E7` | `#4D89B8` | `#7A8594` |

A paleta física precisou registrar apenas seis valores que ainda não existiam nela:

`#E1E6ED`, `#151E2A`, `#303D4E`, `#A7B4C3`, `#354151`, `#B1BCC9`.

Os demais valores já pertenciam à paleta centralizada.

## 5. Arquitetura aplicada

Foi adicionada ao `tema.py` a camada final:

`ESTILO_MODO_FOCO_INTEGRACAO_RESOLVEDOR`

Ela contém somente referências `{{color:...}}`; não contém hexadecimais, `rgb/rgba`, dimensões, tipografia ou propriedades comportamentais.

A camada é composta após Cards Globais C nos três temas. Os blocos físicos históricos anteriores foram mantidos como camada de compatibilidade, preservando reversibilidade; a camada tokenizada final prevalece pela cascata.

Também foram atualizados os helpers de teste para que snapshots históricos anteriores continuem reproduzíveis ao remover programaticamente a nova camada.

## 6. Arquivos de produção

Arquivos do Design System alterados:

- `tema.py`
- `ui/design/tokens.py`
- `ui/design/themes.py`
- `ui/design/palette.py`
- `DESIGN_SYSTEM.md`

Infraestrutura/testes atualizados:

- `_design_system_test_helpers.py`
- `test_design_system_modo_foco_integracao_resolvedor.py`
- expectativas de contagem nos testes de contrato corrente;
- ajuste do rollback do teste de Cards Globais C para isolar a nova camada posterior.

Arquivos protegidos que permaneceram byte a byte inalterados:

| Arquivo | SHA-256 |
|---|---|
| `main.py` | `66a8dadf431b1eecb3467124856319dc6b7e797dc9bf4f52901a104b6fe174ad` |
| `foco.py` | `8fbe4659f3371683738a3fa239a789b3bca26ab47dc68f38a69829a33afd03ed` |
| `navegacao.py` | `2cb3439a580cf867af9870750a82e06777718961dd84819e0705a96838c8b862` |
| `estudos.db` | `034940a33ea792957d8fafbf5c528db7cd895db69031696fbdd3f0a0ce5a41ef` |
| `versao.py` | `8436214451a591c0a3d3429f62d53c0c01cfc0cc7311d71e57fcf060f5b39642` |
| `jogos.py` | `498aab65a2a13efa070ae2f912536b5ddc1aada31e23a28846def6a617492286` |
| `checkpoint.py` | `947295fdf2035d6f65d5d43f70e1d6e5e1c411d92eaca264a469a221b6b61c38` |

Hashes dos principais arquivos modificados antes da inclusão deste relatório no checkpoint:

| Arquivo | SHA-256 |
|---|---|
| `tema.py` | `e657f9863f2aa94add737b3a90db8fbc83d931ee41f9c7174fbd5d42e429b731` |
| `ui/design/tokens.py` | `89dd394856f763bd8f84265d14d2f53a13a2359a408fd88d07ad3eaf3efac2e3` |
| `ui/design/themes.py` | `ecd60904c59beac849e6f055cec691019a61896df47aee84b3a86e81c1e66fd0` |
| `ui/design/palette.py` | `a5acd1e1ded879c862506cbed1cbc45f46e049650c23a29aa9f17de1dcd107cc` |

## 7. Validações automatizadas

### Teste específico do bloco

`test_design_system_modo_foco_integracao_resolvedor.py`

**11/11 aprovados.**

O teste verifica orçamento/tipo dos tokens, valores por tema, consumo exato, isolamento dos seletores, ausência de cromatismo físico na nova camada, renderização, ordem de composição, preservação de `main.py`/`foco.py`, rollback para Cards C e integridade de metadados/banco.

### Testes históricos do Modo Foco

- `test_design_system_modo_foco_passo_1.py`
- `test_design_system_modo_foco_passo_2.py`
- `test_design_system_pos_foco_passo_3.py`

**26/26 aprovados.**

### Bateria dirigida cumulativa

**131/131 aprovados.**

### Regressão funcional de navegação

**12/12 aprovados.**

### Suíte ampla `test_design_system*.py`

Resultado atual:

- 326 testes executados;
- 8 falhas históricas;
- 6 erros ambientais/Qt;
- nenhuma nova falha atribuível a este bloco.

As 8 falhas são as mesmas pendências históricas de expectativas/hashes de checkpoints antigos do Resolvedor. A contagem de erros ambientais caiu de 7 no baseline anterior para 6 nesta execução; não surgiu erro novo do bloco.

### Compilação

`py_compile` aprovado para:

`tema.py`, `ui/design/tokens.py`, `ui/design/themes.py`, `ui/design/palette.py`, `main.py`, `foco.py`, `navegacao.py`, `jogos.py`, `checkpoint.py` e `versao.py`.

### Banco

- `PRAGMA integrity_check`: `ok`
- `PRAGMA foreign_key_check`: 0 violações

### Renderização QSS

Nenhum `{{color:...}}` ou `{{gradient:...}}` ficou sem resolução nos três temas.

Hashes do QSS final:

- Claro: `3415bf6413b6356229704186341fad548eec492820a30568d9b338b1a8a05fab`
- Escuro: `09d651e454db99920342c633422c23dcaa6b13ae36e0e727b61d4efcb11c2d03`
- Futurista: `129fcb3ef8f2d4a0b7d97987f0df356fbca003e30f88eb74ef8a4570b2c4f058`

## 8. Validação manual necessária no Windows

Antes de tornar este checkpoint a base oficial, validar nos temas Claro, Escuro e Futurista uma sessão de questões com o Modo Foco ativo. Confirmar:

- superfície e borda da faixa de foco;
- texto de estado, inclusive variações ativo/pausado;
- botões `Pausar` e `Abrir foco` em estado normal;
- hover dos dois botões;
- ausência de alteração nos demais `subtleButton` do programa;
- ausência de alteração visual/comportamental nas janelas principais de Modo Foco e Pós-Foco.

## 9. Conclusão

A implementação está tecnicamente aprovada e mantém a premissa da Fase A: **a origem cromática foi centralizada sem redesenhar o componente**.

O checkpoint deve permanecer como **candidato** até a validação manual no Windows. Após essa validação, o próximo passo é uma auditoria final curta do macroescopo Modo Foco; não há autorização implícita para criar outro bloco de implementação.
