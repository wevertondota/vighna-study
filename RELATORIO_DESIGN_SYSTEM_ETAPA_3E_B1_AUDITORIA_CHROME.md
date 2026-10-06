# Design System Vighna — Etapa 3E-B1

## Auditoria do chrome da sessão do Resolvedor

Data da caracterização: 06/10/2026  
Commit de partida: `204bad5` (`refactor(theme): migra acoes e feedback do resolvedor`)  
Natureza desta etapa: documental; nenhum QSS, token, comportamento, layout, banco, schema, versão ou build foi alterado.

## 1. Conclusão executiva

O chrome moderno efetivamente ativo não é representado integralmente pelas 133 ocorrências hexadecimais dos três blocos `ESTILO_RESOLVEDOR_*`. A cascata final contém ainda 32 ocorrências ativas nos checkboxes legados e 21 em seletores genéricos não alcançados pela busca original (`subtleButton` e `mockExamTimer`). Portanto:

- 133 ocorrências estão nos blocos modernos;
- 165 ocorrências estão ativas dentro do universo da busca ampla de 316 (`133 + 32`);
- 186 ocorrências realmente incidem na sessão ativa quando se incluem os 21 genéricos omitidos pela heurística;
- 167 dessas 186 pertencem ao chrome candidato à migração futura;
- 19 pertencem a recortes deliberadamente separados: 9 do painel de Modo Foco e 10 do cartão/corpo do enunciado;
- o resumo final é uma janela, estrutura e domínio visual próprios e deve seguir para uma futura **3E-C**, não para a 3E-B2.

A equivalência visual completa entre temas é rara. Só `canvas.app` pode ser reutilizado diretamente para o fundo da janela. `text.on_action` pode substituir apenas o texto branco declarado no hover Futurista de Pular. `progress.fill_gradient`, hoje sem consumidor, pode ser recaracterizado com segurança para o gradiente real do progresso da sessão. Os demais papéis exigem estimativa de 56 tokens novos para preservar exatamente a aparência atual, bem acima do sinal de alerta de 20. A recomendação é dividir a migração e revisar o orçamento antes de qualquer alteração.

## 2. Método e critério de contagem

A caracterização foi feita sobre:

- `JanelaResolverQuestoes` em `main.py`;
- `JanelaResumoResolucaoQuestoes` somente para delimitar domínio;
- os três blocos modernos `ESTILO_RESOLVEDOR_CLARO`, `ESTILO_RESOLVEDOR_ESCURO` e `ESTILO_RESOLVEDOR_FUTURISTA`;
- as folhas completas retornadas por `stylesheet_claro()`, `stylesheet_escuro()` e `stylesheet_futurista()`;
- seletores legados e genéricos que ainda vencem ou fornecem propriedades não redeclaradas;
- testes atuais do Resolvedor e das etapas 3E-A1/3E-A2.

“Ocorrência” significa um literal hexadecimal no código-fonte, não quantidade de pixels, widgets ou aplicações em runtime. Cores repetidas em propriedades ou temas diferentes são ocorrências distintas. Hexadecimais já migrados para marcadores de token não entram na conta.

## 3. O chrome que realmente existe

### 3.1 Componentes ativos e pertencentes ao chrome

| Grupo | Implementação real | Estados reais | Observação |
|---|---|---|---|
| Janela da sessão | `QDialog#questionSolverDialog` | normal | Fundo geral; equivalência exata com `canvas.app`. |
| Cabeçalho | `pageTitle`, `pageSubtitle` | normal | Título “Resolver questões” e subtítulo contextual. |
| Retorno | `QPushButton#subtleButton` (“Dashboard”) | normal, hover | É o “Voltar” existente. Não há botão separado chamado Voltar. |
| Encerrar | `questionSessionEndButton` | normal, hover | Ação destrutiva; sem pressed/disabled locais. |
| Cronômetro | `mockExamTimer` | normal, oculto/visível | Badge não interativo, visível somente em simulado. |
| Overview | `questionSessionOverviewCard` | normal | Cartão superior da sessão. |
| Rótulo do overview | `questionSessionEyebrow` | normal | “PROGRESSO DA SESSÃO”. |
| Contador | `questionSessionProgressText` | normal | Exibe “Questão N de total”; não é percentual. |
| Ciclo | `questionSessionCycleText` | normal, oculto/visível | Texto contextual; não é chip. |
| Progresso | `questionSessionProgress` e `::chunk` | valor corrente | Trilho e preenchimento; texto interno invisível; sem borda. |
| Miniestatísticas | `questionSessionMiniStat`, `MiniLabel`, `MiniValue` | neutral, success, danger, warning | Respondidas, Acertos, Erros e Puladas. Não existe miniestatística “Pendentes”. |
| Contexto da questão | `questionSolverDiscipline`, `questionSolverMeta`, `questionSolverQuestionIndex` | normal | Disciplina, tópico/metadado e índice. |
| Painel de ações | `questionSessionActionPanel` | normal | Contém flags, Pular e Confirmar/Próxima; o primário já pertence à 3E-A2. |
| Dúvida | `questionSessionDoubt` | normal, hover do indicador, checked, disabled do indicador | Texto e indicador permanecem parcialmente em camada legada. |
| Análise | `questionSessionAnalysisFlag` | normal, hover do indicador, checked | Não há regra local disabled. |
| Pular | `questionSessionSkipButton` | normal, hover | Sem pressed/disabled locais. |

Não foram encontrados divisor autônomo, percentual separado de progresso, badge de status geral, estado selected/focused do chrome, nem botão adicional de navegação. Confirmar/Próxima e o feedback pós-resposta já foram concluídos na 3E-A2 e não são reabertos aqui.

### 3.2 Componentes deliberadamente separados

- **Modo Foco:** `questionSessionFocusBar`, `questionSessionFocusState` e seus botões compartilham a janela, mas constituem um recurso contextual próprio. Seus 9 literais modernos foram classificados como outro recorte e não entram na 3E-B2 proposta.
- **Corpo pedagógico:** `questionSolverStatementCard`, `questionSolverStatement` e o texto do enunciado possuem 10 literais modernos. São conteúdo da questão, não chrome; devem permanecer fora desta etapa.
- **Núcleo de resposta/editor/feedback:** já migrado em 3E-A1/3E-A2.
- **Configuração pré-sessão:** perfil, disponibilidade e cartão de configuração pertencem ao fluxo de entrada, não à sessão ativa.
- **Resumo final:** separado na seção 11.

## 4. Decomposição dos 133 literais modernos

| Componente/estado | Claro | Escuro | Futurista | Total | Classificação |
|---|---:|---:|---:|---:|---|
| Fundo da janela | 1 | 1 | 1 | 3 | chrome |
| Título e subtítulo | 2 | 2 | 2 | 6 | chrome |
| Superfície/borda do overview | 2 | 2 | 4 | 8 | chrome |
| Eyebrow, contador e ciclo | 3 | 3 | 3 | 9 | chrome |
| Progresso: trilho e preenchimento | 3 | 3 | 4 | 10 | chrome |
| Miniestatísticas | 7 | 7 | 7 | 21 | chrome |
| Barra/estado do Modo Foco | 2 | 2 | 5 | 9 | outro recorte |
| `subtleButton` escopado | 0 | 0 | 6 | 6 | chrome |
| Disciplina, metadado e índice | 3 | 3 | 3 | 9 | chrome |
| Cartão/texto do enunciado | 3 | 3 | 4 | 10 | corpo pedagógico |
| Painel de ações | 2 | 2 | 3 | 7 | chrome |
| Texto dos checkboxes | 0 | 0 | 3 | 3 | chrome |
| Pular | 5 | 5 | 6 | 16 | chrome |
| Encerrar | 5 | 5 | 6 | 16 | chrome |
| **Total** | **39** | **39** | **55** | **133** | |

Dentro desses 133, 114 pertencem ao chrome futuro e 19 aos dois recortes separados.

## 5. Explicação das 316 ocorrências da busca ampla

A busca ampla anterior capturava qualquer regra cujo seletor contivesse `questionSolver` ou `questionSession`. Ela misturava fonte efetiva, duplicação temática, regras sombreadas e componentes de outros fluxos.

| Camada | Quantidade | Situação |
|---|---:|---|
| A. Chrome moderno efetivamente ativo | 114 | Parte dos blocos modernos que pertence ao chrome. |
| B. Legado ainda ativo por cascata | 32 | Checkboxes: 16 no Claro e 16 no Escuro; o Futurista herda os indicadores escuros e substitui apenas textos. |
| C. Declarações legadas sombreadas | 119 | 66 nos blocos legados Claro/Escuro, 16 genéricos Claro/Escuro e 37 Futuristas; não determinam a cascata final. |
| D. Resumo/finalização | 14 | 7 Claro + 7 Escuro em seletores compartilhados de cartão, detalhe e tabela. |
| E. Outros recortes | 37 | 19 modernos ativos (Modo Foco e enunciado) + 18 da configuração/perfil/disponibilidade pré-sessão. |
| **Total da heurística** | **316** | |

Detalhe das duplicidades/sombreamento:

- cada bloco legado Claro e Escuro contribui 65 ocorrências: 33 sombreadas, 16 ainda ativas nos checkboxes, 7 do resumo e 9 da configuração pré-sessão;
- os grupos genéricos relacionados ao Resolvedor somam 8 por tema Claro/Escuro e estão sombreados pelos seletores modernos escopados;
- o bloco Futurista legado de 24 ocorrências e outro grupo Futurista genérico de 13 estão sombreados por regras posteriores e/ou mais específicas;
- “duplicidade” aqui é a repetição de uma função visual em camadas/temas, não uma autorização para removê-la: a precedência atual deve ser preservada.

Assim, **165 das 316 ocorrências determinam a sessão visual ativa** (`114 + 32 + 19`). Outras 151 são regras sombreadas, resumo ou configuração (`119 + 14 + 18`); dentro das 165, os 19 literais de Modo Foco/enunciado continuam deliberadamente fora do chrome.

### 5.1 O que a busca de 316 não contava

A heurística por nome do seletor não alcançou:

- 12 ocorrências finais de `QPushButton#subtleButton` no Claro/Escuro (normal e hover), que estilizam o botão Dashboard;
- 9 ocorrências de `QLabel#mockExamTimer` nos três temas.

Somadas às 165 ativas, elas produzem **186 ocorrências ativas reais**. O alvo do chrome é **167**: 114 modernas + 32 legadas de checkboxes + 21 genéricas. As 19 modernas restantes ficam fora do recorte.

## 6. Cascata final por tema

### Claro

O stylesheet base contém regras genéricas e o legado do Resolvedor. Ao final da composição entram, nesta ordem relevante, `ESTILO_RESOLVEDOR_CLARO`, detalhes de tópico, eliminadas, teclado, editor de explicação e calendário. Os seletores escopados por `QDialog#questionSolverDialog` vencem as regras genéricas/legadas equivalentes. Como o bloco moderno Claro não redeclara os indicadores dos checkboxes, suas regras legadas continuam ativas. `subtleButton` e `mockExamTimer` continuam vindo de seletores genéricos finais.

### Escuro

Repete a arquitetura do Claro com `ESTILO_RESOLVEDOR_ESCURO`. O bloco moderno prevalece sobre progressos, cartões, textos, Pular e Encerrar anteriores. Os indicadores e estados dos checkboxes continuam no legado Escuro. Dashboard e cronômetro continuam em regras genéricas.

### Futurista

`stylesheet_futurista()` é composto por `stylesheet_escuro()` completo seguido dos overrides Futuristas. Depois dos blocos Futuristas gerais entram `ESTILO_RESOLVEDOR_FUTURISTA`, detalhes, eliminadas, teclado, editor e calendário. Portanto:

- o override Futurista deve continuar existindo;
- as regras modernas Futuristas escopadas vencem os valores herdados do Escuro para janela, overview, progresso, métricas, contexto, painel e botões;
- o texto dos checkboxes é substituído no bloco moderno Futurista, mas os indicadores continuam herdados do legado Escuro;
- o `subtleButton` escopado Futurista vence o gradiente genérico Futurista;
- especificidade e ordem não podem ser reorganizadas numa migração mecânica.

## 7. Gradientes restantes

Todos os stops são opacos; não há alpha parcial.

| Componente | Tema | Direção | Stops atuais | Candidato existente | Decisão |
|---|---|---|---|---|---|
| Overview | Futurista | diagonal `(0,0) → (1,1)` | `0 #202733`, `0.55 #222A36`, `1 #1D2430` | nenhum | Novo `session.overview_gradient`. |
| Progresso | Claro | horizontal `(0,0) → (1,0)` | `0 #4F5FE8`, `1 #6B86F2` | `progress.fill_gradient` | Recaracterizar token hoje sem consumidor. |
| Progresso | Escuro | horizontal `(0,0) → (1,0)` | `0 #5964E8`, `1 #6E8BEF` | `progress.fill_gradient` | Idem. |
| Progresso | Futurista | horizontal `(0,0) → (1,0)` | `0 #5358EA`, `0.52 #5B64EE`, `1 #718BF5` | `progress.fill_gradient` | Idem; preservar stop intermediário. |
| Painel de ações | Futurista | horizontal `(0,0) → (1,0)` | `0 #171F2B`, `1 #151D28` | nenhum | Novo `session.action_panel_gradient`. |

O gradiente diagonal do cartão do enunciado (`#171F2B → #141C27`) foi inventariado no CSV, mas fica fora do chrome. Nenhum gradiente existente tem direção, posições e cores iguais aos gradientes de overview ou painel. `gradient.action_primary` não é candidato: representa ação e possui outros stops.

## 8. Tokens existentes: reutilização e recaracterização

### Reutilização exata autorizável

| Token | Consumidor | Evidência |
|---|---|---|
| `canvas.app` | fundo de `questionSolverDialog` | Valores exatos `#F5F7FA / #101722 / #0B111D`. `focus_mode.canvas` também coincide, mas tem semântica incorreta. |
| `text.on_action` | texto do hover Futurista de Pular | A declaração existe somente no Futurista e é `#FFFFFF`; não implica usar o token para os demais textos. |

### Recaracterização possível

| Token | Estado atual | Proposta |
|---|---|---|
| `progress.fill_gradient` | Sem consumidor; hoje duplica o gradiente primário de ação | Passar a representar o preenchimento real da sessão com direção e stops da seção 7. |

### Famílias verificadas e não reutilizadas

- `progress.track`, `progress.fill`, `progress.text` e `progress.border` já são consumidos por um `QProgressBar` genérico Futurista e não coincidem nos três temas com a sessão. `progress.complete` e `progress.warning` não representam estados reais do progresso desta tela.
- `action.secondary*` e `action.destructive*` têm semântica próxima, mas não reproduzem simultaneamente superfície, texto e borda atuais de Dashboard, Pular e Encerrar. Mudar os globais afetaria consumidores já migrados.
- `surface.*`, `text.*` e `border.*` não apresentam triples completos equivalentes, salvo os casos explicitamente listados.
- `feedback.*` não coincide com os acentos textuais das miniestatísticas; feedback pós-resposta já possui outra fronteira semântica.
- `focus.*`, `icon.*` e `overlay.*` não possuem consumidor visual próprio neste chrome. O glifo do cronômetro faz parte do texto da label.
- `answer.*` não deve ser reutilizado: é o domínio da resposta. Nenhum dos oito tokens `answer.*` ainda sem consumidor ganhou correspondência legítima.

## 9. Estimativa de tokens novos

Foi proposta uma família pequena `session.*`, e não `solver.*`, porque estes papéis coordenam o chrome de uma sessão de questões, independem do conteúdo da resposta e não pertencem ao resumo final. Os tokens `progress.session_*` permanecem na família de progresso. Valores “—” significam que o tema atual usa outra propriedade (por exemplo, gradiente em vez de superfície plana); a futura definição contratual ainda precisará receber um valor não consumido.

### 9.1 Estrutura, progresso e métricas — 19 tokens

| Token proposto | Nível | Consumidor/estado | Claro | Escuro | Futurista | Por que não reutilizar |
|---|---|---|---|---|---|---|
| `session.title_text` | componente | título | `#172033` | `#F3F6FA` | `#F5F7FB` | Nenhum `text.*` coincide nos três temas. |
| `session.subtitle_text` | componente | subtítulo | `#718096` | `#96A3B3` | `#AAB5C2` | Idem. |
| `session.panel_surface` | componente | overview/action, normal | `#FFFFFF` | `#182230` | — | `surface.*` diverge no Escuro; Futurista usa gradiente. |
| `session.overview_border` | componente | overview, normal | `#DDE4EC` | `#344154` | `#475364` | Nenhum `border.*` coincide. |
| `session.overview_gradient` | componente/gradiente | overview, normal | — | — | `0 #202733; .55 #222A36; 1 #1D2430` | Gradiente próprio, sem equivalente. |
| `session.eyebrow_text` | componente | rótulo superior | `#7B8797` | `#8392A5` | `#AAB4C0` | Nenhum `text.*` coincide. |
| `progress.session_text` | componente | contador de questão | `#202B3C` | `#EDF2F7` | `#F5F7FB` | `progress.text` diverge. |
| `session.cycle_text` | componente | texto de ciclo | `#657286` | `#A1ADBB` | `#B8C1CD` | Nenhum `text.*` coincide. |
| `progress.session_track` | componente | trilho | `#E8EDF3` | `#2C3745` | `#3B424F` | Só o Claro coincide com `progress.track`. |
| `session.metric_surface` | componente | miniestatística | `#F7F9FC` | `#141D29` | `#171F2B` | Sem triple global equivalente. |
| `session.metric_border` | componente | miniestatística | `#E3E8EF` | `#2D3949` | `#344050` | Sem triple global equivalente. |
| `session.metric_label_text` | componente | rótulo | `#7A8798` | `#8D9BAD` | `#98A5B4` | Sem triple global equivalente. |
| `session.metric_value_text` | componente | valor neutro | `#1F2937` | `#F2F5F8` | `#F8FAFC` | `text.primary` coincide apenas no Claro. |
| `session.metric_success_text` | componente | acertos | `#17815D` | `#79D6AA` | `#82DBB4` | `feedback.success_text` não coincide. |
| `session.metric_danger_text` | componente | erros | `#C44758` | `#F08A98` | `#F28B99` | `feedback.danger_text` não coincide. |
| `session.metric_warning_text` | componente | puladas | `#B16A18` | `#E5B16B` | `#E9B66E` | `feedback.warning_text` não coincide. |
| `session.discipline_text` | componente | disciplina | `#5866C8` | `#96A0FF` | `#969FFF` | Papel contextual próprio. |
| `session.meta_text` | componente | tópico/metadado | `#5D697A` | `#A8B4C2` | `#B6C0CB` | Sem triple global equivalente. |
| `session.question_index_text` | componente | índice | `#606BC9` | `#9BA4FF` | `#9BA4FF` | Sem triple global equivalente. |

Além desses 19, esta fase reutilizaria `canvas.app` e recaracterizaria `progress.fill_gradient`.

### 9.2 Painel, navegação e ações — 22 tokens

| Token proposto | Consumidor/estado | Claro | Escuro | Futurista |
|---|---|---|---|---|
| `session.action_panel_gradient` | painel normal | — | — | `0 #171F2B; 1 #151D28` |
| `session.action_panel_border` | painel normal | `#DDE4EC` | `#344154` | `#3A4656` |
| `session.navigation_surface` | Dashboard normal | `#FFFFFF` | `#162333` | `#232B36` |
| `session.navigation_text` | Dashboard normal | `#334155` | `#DCE6F0` | `#D1D9E2` |
| `session.navigation_border` | Dashboard normal | `#CFD8E3` | `#33475E` | `#5A6472` |
| `session.navigation_hover_surface` | Dashboard hover | `#F6FBFF` | `#1C3145` | `#2C3643` |
| `session.navigation_hover_text` | Dashboard hover | `#235F98` | `#9BD5FF` | `#FFFFFF` |
| `session.navigation_hover_border` | Dashboard hover | `#9FC7E7` | `#4D89B8` | `#7A8594` |
| `session.timer_surface` | cronômetro | `#F5F3FF` | `#2E1065` | `#152A46` |
| `session.timer_text` | cronômetro | `#6D28D9` | `#DDD6FE` | `#9EEEFF` |
| `session.timer_border` | cronômetro | `#C4B5FD` | `#7C3AED` | `#42CAE9` |
| `session.skip_surface` | Pular normal | `#F5F7FA` | `#202B39` | `#202833` |
| `session.skip_text` | Pular normal | `#4F5D6E` | `#C8D1DC` | `#CED6E0` |
| `session.skip_border` | Pular normal | `#CCD5DF` | `#445265` | `#505B69` |
| `session.skip_hover_surface` | Pular hover | `#EDF1F5` | `#273444` | `#293341` |
| `session.skip_hover_border` | Pular hover | `#AFBAC8` | `#607086` | `#707C8B` |
| `session.end_surface` | Encerrar normal | `#FFF7F8` | `#2B2027` | `#2A2026` |
| `session.end_text` | Encerrar normal | `#A54050` | `#FFB8C2` | `#FFBAC4` |
| `session.end_border` | Encerrar normal | `#E9BCC4` | `#724350` | `#70434F` |
| `session.end_hover_surface` | Encerrar hover | `#FFF0F2` | `#38262D` | `#38262E` |
| `session.end_hover_text` | Encerrar hover | — | — | `#FFD5DB` |
| `session.end_hover_border` | Encerrar hover | `#DC929E` | `#985766` | `#9A5968` |

Não se propõe `session.skip_hover_text`: Claro/Escuro herdam o texto normal e o Futurista pode usar `text.on_action`. Os 22 tokens são necessários porque `action.secondary*`/`action.destructive*` não modelam o tratamento triplo atual sem mudar valores globais.

### 9.3 Flags/checkboxes — 15 tokens

| Token proposto | Consumidor/estado | Claro | Escuro | Futurista |
|---|---|---|---|---|
| `session.doubt_text` | Dúvida normal | `#475569` | `#CBD5E1` | `#B7C1CD` |
| `session.doubt_checked_text` | Dúvida checked | `#1D4ED8` | `#93C5FD` | `#AEB5FF` |
| `session.flag_indicator_surface` | ambos, indicador normal | `#FFFFFF` | `#111827` | `#111827` |
| `session.doubt_indicator_border` | Dúvida normal | `#64748B` | `#94A3B8` | `#94A3B8` |
| `session.doubt_indicator_hover_border` | Dúvida hover | `#2563EB` | `#60A5FA` | `#60A5FA` |
| `session.doubt_indicator_checked_surface` | Dúvida checked | `#2563EB` | `#3B82F6` | `#3B82F6` |
| `session.doubt_indicator_checked_border` | Dúvida checked | `#1D4ED8` | `#93C5FD` | `#93C5FD` |
| `session.doubt_indicator_disabled_surface` | Dúvida disabled | `#E2E8F0` | `#1F2937` | `#1F2937` |
| `session.doubt_indicator_disabled_border` | Dúvida disabled | `#94A3B8` | `#475569` | `#475569` |
| `session.analysis_text` | Análise normal | `#64748B` | `#94A3B8` | `#B7C1CD` |
| `session.analysis_checked_text` | Análise checked | `#92400E` | `#FBBF24` | `#F0C47C` |
| `session.analysis_indicator_border` | Análise normal | `#94A3B8` | `#64748B` | `#64748B` |
| `session.analysis_indicator_hover_border` | Análise hover | `#D97706` | `#F59E0B` | `#F59E0B` |
| `session.analysis_indicator_checked_surface` | Análise checked | `#F59E0B` | `#D97706` | `#D97706` |
| `session.analysis_indicator_checked_border` | Análise checked | `#B45309` | `#FBBF24` | `#FBBF24` |

O único triple coincidente encontrado fora dessas famílias foi `calendar.badge_border` para a superfície disabled de Dúvida; a semântica é incompatível e a reutilização foi rejeitada.

### 9.4 Orçamento consolidado

| Classe | Quantidade |
|---|---:|
| Tokens existentes reutilizáveis | 2 (`canvas.app`, `text.on_action`) |
| Token existente a recaracterizar | 1 (`progress.fill_gradient`) |
| Novos: estrutura/progresso/métricas/contexto | 19 |
| Novos: painel/navegação/ações | 22 |
| Novos: flags/checkboxes | 15 |
| **Novos estimados** | **56** |

O número excede claramente o alerta de 20, mas não decorre de “token por seletor”: estados de superfície, texto e borda são propriedades independentes e divergem entre os três temas. Reduzir artificialmente a conta exigiria alterar a aparência, misturar domínios ou mudar tokens globais já consumidos.

## 10. Riscos de uma futura migração

1. **Cascata híbrida dos checkboxes:** migrar apenas o texto deixaria indicadores legados; migrar apenas indicadores mudaria a herança Futurista.
2. **`subtleButton` compartilhado:** o mesmo objectName estiliza Dashboard e botões do painel de Modo Foco. O escopo do seletor precisa continuar explícito.
3. **Futurista composto:** remover herança ou reorganizar seletores muda precedência mesmo com cores iguais.
4. **Gradientes:** igualdade por cores é insuficiente; direção, posição do stop `0.52` e opacidade fazem parte do contrato visual.
5. **Ações sem estados locais:** não se devem inventar pressed/disabled; regras genéricas de menor especificidade não criam um estado visual efetivo quando o seletor por ID mantém as propriedades.
6. **Contrato inflado:** 56 tokens novos de uma só vez dificultariam revisão e ocultariam regressões de fronteira.
7. **Resumo compartilhado:** alguns seletores têm nomes `questionSession*`, mas são consumidos pela janela de resumo; migrá-los junto ampliaria o risco de cascata.

## 11. Resumo final da sessão

Decisão: **opção B — futura 3E-C**.

Justificativas:

- existe classe própria, `JanelaResumoResolucaoQuestoes`, distinta de `JanelaResolverQuestoes`;
- possui cartões, métricas, tabelas, detalhes, integração com foco e ações próprias;
- mantém seletores e paleta parcialmente compartilhados por nome, mas com estrutura visual maior e outra finalidade;
- a busca ampla já expõe 14 literais próprios apenas em um subconjunto de seletores, sem contar todos os nomes não capturados pela heurística;
- incluir o resumo elevaria o orçamento e o risco semânticos da 3E-B2.

O rótulo `questionSessionSummaryDetail` usado dentro do feedback de erro de banco deve ser revisitado na 3E-C: compartilhar nome não torna o feedback parte do resumo.

## 12. Mapa recomendado de migração

Não se recomenda uma 3E-B2 monolítica. Ordem proposta, baseada nas dependências reais:

1. **3E-B2a — estrutura e leitura:** janela, cabeçalho, overview, contador/ciclo, progresso, miniestatísticas e contexto da questão. Estimativa: 19 novos + `canvas.app` + recaracterização de `progress.fill_gradient`.
2. **3E-B2b — painel e ações:** painel, Dashboard, cronômetro, Pular e Encerrar. Estimativa: 22 novos + `text.on_action`. Como ainda supera 20, requer revisão explícita ou divisão entre cabeçalho e rodapé.
3. **3E-B2c — flags:** Dúvida e Análise, incluindo todos os indicadores herdados. Estimativa: 15 novos. Migrar os três temas conjuntamente para eliminar a camada híbrida.
4. **3E-C — resumo final:** caracterização e migração independentes.

Modo Foco, corpo do enunciado, Dashboard geral, gráficos, controles avançados e aliases continuam fora.

## 13. Validação de estado

Esta etapa não criou nem modificou testes funcionais. Resultados:

| Validação | Resultado |
|---|---|
| `py_compile` de `tema.py`, `main.py` e `ui/design` | passou |
| Design System atual + 3E-A1 + 3E-A2 | 28/28 passaram |
| `testes_smoke.py` | passou — `VighnaStudy 0.29.59: testes smoke OK` |
| Suíte principal do Resolvedor | 59 executados; 49 passaram; 10 falhas de linha de base, detalhadas abaixo; recorte aplicável reexecutado em separado: 49/49 |

Das dez falhas da suíte principal:

- nove são expectativas históricas de versão/build/schema (`0.29.46`, `0.29.51`, schema `22`, `0.29.53`, `0.29.54`, `0.29.55`, `0.29.56`, `0.29.57` e `0.29.58`) contra o estado atual correto `0.29.59 / calendar-week-forecast-v1 / schema 25`;
- uma é a asserção textual antiga de `test_cobertura_pulo_reincidente.py`, que procura a frase literal `retorno de questão pulada` em `main.py`; o comportamento coberto pelos outros dois testes do mesmo arquivo passou. A divergência já existe no commit de partida e não foi causada por esta etapa documental.

Como nenhum arquivo de código foi alterado, os hashes canônicos permaneceram:

| Tema | Hash SHA-256 canônico esperado |
|---|---|
| Claro | `139709f8c57e00f16848668f9226703c7f8ff391dd9aea2bba8b2eae20ac2c5f` |
| Escuro | `ebbc21363d0035058301d060eb099fb2d33b992e8537c20f9bf1e77f8a2b4f3e` |
| Futurista | `0e588bb372946b4a6f61ad406c817fd155cac8c3c4286e9f93b7a09d06dc8622` |

Banco e metadados:

- `PRAGMA integrity_check`: `ok`;
- `PRAGMA foreign_key_check`: zero violações;
- SHA-256 do schema SQLite: `240e65de128ff81959d6277489c03a5599c7fc404b08d5ace5b79596b00f43a9`;
- contrato de Design System: 274 tokens, sendo 102 semânticos e 172 de componente;
- versão: `0.29.59`;
- build: `calendar-week-forecast-v1`;
- schema declarado: `25`;
- banco, schema, `main.py`, `tema.py`, `ui/design`, testes e `versao.py` permaneceram inalterados.

## 14. Recomendação final

**Dividir novamente antes de migrar.** A arquitetura atual permite uma primeira fatia coesa de leitura/estrutura com menos de 20 tokens novos. As ações e flags devem ser revisadas em lotes próprios. Não há evidência para alterar tokens globais, atravessar a fronteira `answer.*` ou incorporar o resumo final. O CSV `MAPA_CHROME_RESOLVEDOR.csv` é o inventário operacional para a próxima revisão.
