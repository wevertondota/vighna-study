# Relatório — Design System Vighna — Etapa 3B: Startup e tarefas pesadas

## Resultado

A subpaleta fixa do splash externo, do indicador de tarefas pesadas e do fallback interno `JanelaInicializacao` foi centralizada no Design System sem alteração intencional de aparência ou comportamento.

O visual permanece deliberadamente independente de Claro, Escuro e Futurista. Os tokens fixos têm valores idênticos nos três contratos e a API valida essa invariância antes de entregá-los aos consumidores.

Versão preservada: VighnaStudy `0.29.59`, build `calendar-week-forecast-v1`, schema `25`.

## Arquivos alterados

- `startup_splash.py`: cores QSS, QPainter, barra, shimmer e pulso passam a usar a API fixa.
- `tarefas_pesadas.py`: somente o stylesheet de `IndicadorTarefa` passa a usar tokens.
- `main.py`: somente o import da API e o bloco de estilo de `JanelaInicializacao` foram alterados.
- `ui/design/palette.py`: registra os 24 valores físicos exatos da subpaleta.
- `ui/design/tokens.py`: acrescenta 20 tokens de cor e 2 de gradiente.
- `ui/design/themes.py`: mapeia os tokens fixos igualmente nos três contratos e valida invariância.
- `ui/design/adapters.py`: acrescenta adaptadores `fixed_*` e coordenadas dinâmicas opcionais para QLinearGradient.
- `ui/design/__init__.py`: expõe a nova API pública.
- `test_design_system_startup_tarefas.py`: caracteriza equivalência, alpha, stops, consumidores e timing.
- `DESIGN_SYSTEM.md`: documenta o contrato de componente fixo.
- `RELATORIO_DESIGN_SYSTEM_ETAPA_3B_STARTUP_TAREFAS.md`: registra esta etapa.

Nenhum trecho de calendário, gráficos, tabelas, Dashboard, resolvedor ou Modo Foco foi migrado.

## Caracterização anterior

Antes da substituição, cinco testes registraram e comprovaram programaticamente:

- cores estruturais nos três fluxos;
- cores específicas do splash e do indicador;
- stops `0.0`, `0.55` e `1.0` da barra;
- stops `0.0`, `0.50` e `1.0` do shimmer;
- canais RGB e alpha do shimmer;
- RGB e alpha dinâmico do pulso.

Essa linha de base passou integralmente antes de os consumidores serem modificados.

## Hardcodes removidos

Foram removidas **52 ocorrências de cor** dos trechos migrados:

| Consumidor | Hexadecimais | QColor numérico/dinâmico | Total |
|---|---:|---:|---:|
| `startup_splash.py` | 18 | 4 | 22 |
| `tarefas_pesadas.py` | 14 | 0 | 14 |
| `main.py::JanelaInicializacao` | 16 | 0 | 16 |
| **Total** | **48** | **4** | **52** |

Essas ocorrências representam 24 valores físicos distintos. Após a migração, nenhum desses literais permanece nos três trechos consumidores. Outros hardcodes fora do escopo foram preservados.

## Tokens criados

### Compartilhados entre startup e tarefa: 11

- `system_status.canvas`
- `system_status.border`
- `system_status.surface`
- `system_status.surface_border`
- `system_status.text_primary`
- `system_status.text_status`
- `system_status.text_secondary`
- `system_status.text_accent`
- `system_status.progress_track`
- `system_status.progress_border`
- `system_status.progress_fill`

### Específicos do startup: 8

- `startup.logo_surface`
- `startup.logo_border`
- `startup.subtitle_text`
- `startup.footer_text`
- `startup.logo_fallback`
- `startup.progress_pulse`
- `startup.progress_gradient`
- `startup.shimmer_gradient`

### Específicos do indicador: 3

- `task_indicator.mark_surface`
- `task_indicator.mark_border`
- `task_indicator.mark_text`

Total: **22 tokens novos**, sendo 20 de cor e 2 de gradiente. O contrato passa de 148 para 170 tokens: 77 semânticos e 93 de componente.

Nenhum token temático preexistente reproduzia simultaneamente o valor exato e a semântica fixa desses componentes. Em vez de aproximar cores ou alterar tokens gerais, os 11 papéis `system_status.*` são reutilizados pelos três consumidores.

## Valores estruturais antes e depois

| Papel | Antes | Depois |
|---|---|---|
| canvas | `#071522` | `system_status.canvas` → `#071522` |
| borda externa | `#214A64` | `system_status.border` → `#214A64` |
| superfície interna | `#081927` | `system_status.surface` → `#081927` |
| borda interna | `#15364C` | `system_status.surface_border` → `#15364C` |
| texto principal | `#F5F8FF` | `system_status.text_primary` → `#F5F8FF` |
| texto de status | `#EAF4FF` | `system_status.text_status` → `#EAF4FF` |
| texto secundário | `#8FAAC0` | `system_status.text_secondary` → `#8FAAC0` |
| texto percentual | `#67B7FF` | `system_status.text_accent` → `#67B7FF` |
| trilho do progresso | `#081A28` | `system_status.progress_track` → `#081A28` |
| borda do progresso | `#315B76` | `system_status.progress_border` → `#315B76` |
| preenchimento sólido | `#3A8DF1` | `system_status.progress_fill` → `#3A8DF1` |

As variações exclusivas de logo, subtítulo, rodapé, pulso e marca do indicador também mantêm exatamente seus valores caracterizados.

## Gradientes antes e depois

### Barra viva

| Stop | Antes | Depois |
|---:|---|---|
| 0.0 | `#2E74D8` | `#2E74D8` |
| 0.55 | `#3A8DF1` | `#3A8DF1` |
| 1.0 | `#4CA8FF` | `#4CA8FF` |

`startup.progress_gradient` mantém direção horizontal e recebe em runtime as mesmas coordenadas `left → right` da área preenchida.

### Shimmer

| Stop | Antes RGBA | Depois ARGB Qt | Alpha |
|---:|---|---|---:|
| 0.0 | `(125, 215, 255, 0)` | `#007DD7FF` | 0 |
| 0.50 | `(175, 232, 255, 150)` | `#96AFE8FF` | 150 |
| 1.0 | `(125, 215, 255, 0)` | `#007DD7FF` | 0 |

`startup.shimmer_gradient` mantém as coordenadas móveis `centro - 36 → centro + 36`, sem alterar fase, velocidade ou largura.

Não havia gradiente QSS nesses três trechos; portanto, nenhum foi inventado. Foram migrados os dois QLinearGradient programáticos existentes.

## Exceções justificadas

O alpha do ponto luminoso à frente da barra continua calculado em runtime pela mesma fórmula e faixa. Apenas o RGB base `(111, 195, 255)` foi centralizado em `startup.progress_pulse`; `setAlpha(intensidade)` preserva a animação sem criar dezenas de tokens de alpha.

Dimensões, raios, fontes, espaçamentos, intervalos e coordenadas não são tokens de cor e permaneceram locais.

## Preservação de comportamento

- Splash continua em processo separado e antes das importações pesadas.
- Importar `startup_splash.py` continua sem carregar PySide6.
- Intervalos de 30 ms, 80 ms e 320 ms foram preservados.
- Fase e incremento do shimmer permanecem inalterados.
- O indicador continua sendo `QFrame` filho, sem janela nativa.
- Atraso mínimo de 850 ms, threading, exibição, ocultação e posicionamento foram preservados.
- O fallback interno mantém dimensões, estrutura, textos e barra existentes.

## Testes e resultado

A validação abrange:

- `py_compile` dos arquivos alterados;
- contrato e adapters do Design System;
- testes da Etapa 3A;
- caracterização nova de startup/tarefas;
- testes históricos pertinentes de preload, splash vivo, alinhamento e harmonia;
- testes de tarefas assíncronas e indicador embutido;
- smoke tests.

Os testes históricos de versão permanecem tratados separadamente, pois fixam builds antigos sem relação com esta refatoração.

Resultado final:

- `py_compile`: aprovado para todos os arquivos funcionais, infraestrutura e testes alterados;
- Design System, Etapa 3A, QtAwesome e caracterização 3B: **31/31 aprovados**;
- preload, splash, tarefas assíncronas e indicador embutido, com asserções históricas de versão excluídas: **34/34 aprovados**;
- startup rápido: **3/3 aprovados**;
- total final explícito: **68/68 testes aprovados**, além dos 5/5 da caracterização anterior à substituição;
- `testes_smoke.py`: `VighnaStudy 0.29.59: testes smoke OK`.

## Riscos observados

- O splash externo é iniciado muito cedo; a garantia de importação sem Qt precisa permanecer protegida por teste.
- Gradientes desenhados em coordenadas de runtime não podem ser substituídos por coordenadas normalizadas sem alterar a aparência.
- Os tokens fixos estão presentes nos três contratos para manter uniformidade da API, mas qualquer divergência futura é erro de contrato, não uma variante temática.
- O bloco autorizado de `main.py` fica dentro de um arquivo muito grande; revisões futuras devem continuar auditando o diff por faixa para evitar migração incidental.

## Limite desta etapa

Nenhum controle compartilhado, calendário, resolvedor, Modo Foco, Dashboard, gráfico ou tabela foi migrado. Esses módulos exigem autorização posterior.
