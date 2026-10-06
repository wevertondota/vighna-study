# Auditoria do Design System após a Etapa 3D

## 1. Resumo executivo

O contrato atual é **utilizável e pode avançar para a migração do Resolvedor**, mas ainda não deve ser considerado estabilizado. A auditoria encontrou 247 tokens públicos: 102 semânticos e 145 de componente. Desses, 145 possuem consumo literal em código de produção e 102 ainda não possuem consumidor ativo.

O número de tokens sem consumo é alto (41,3%), porém não representa, sozinho, 102 tokens desnecessários. Ele reúne três grupos diferentes:

- 33 tokens `answer.*` preparados justamente para a próxima migração;
- 21 tokens de `chart.*` e `focus_mode.*`, cujos módulos ainda não foram migrados;
- 48 tokens semânticos ou de apoio ainda provisórios, incluindo feedback, glow, overlays, gradientes e estados futuros.

A Etapa 3D não produziu inflação descontrolada: os 51 tokens adicionados nela estão todos consumidos. Dentro desse conjunto, foram encontrados três candidatos fortes de consolidação, sem recomendação de remoção imediata.

A principal ressalva antes da Etapa 3E é que **existência semântica não significa compatibilidade visual pronta**. A família `answer.*` cobre boa parte dos papéis do Resolvedor, mas alguns valores atuais, estados ausentes e direções de gradiente ainda não correspondem à linha de base legada. Esses ajustes devem ser caracterizados e autorizados dentro da futura migração, não nesta auditoria.

**Recomendação:** prosseguir para a Etapa 3E com orçamento e testes de caracterização explícitos; não fazer uma consolidação ampla do contrato antes dela.

## 2. Estado auditado

- VighnaStudy: `0.29.59`;
- build: `calendar-week-forecast-v1`;
- schema declarado: `25`;
- commit inicial: `0154194` (`refactor(theme): migra calendario para design system`);
- contrato: 247 tokens;
- alterações desta etapa: somente este relatório e `MAPA_TOKENS_DESIGN_SYSTEM.csv`;
- nenhuma alteração em `ui/design/`, `tema.py`, `main.py`, banco, schema, versão ou build.

## 3. Metodologia

Foram lidos integralmente os documentos e fontes exigidos: `AGENTS.md`, `DESIGN_SYSTEM.md`, o inventário da Etapa 1, os relatórios das Etapas 2, 3A, 3B, 3C e 3D, além de `tokens.py`, `themes.py`, `palette.py`, `gradients.py` e `adapters.py`.

Para esta auditoria, um **uso** é uma referência literal ao caminho público do token em código Python de produção fora de `ui/design/`. Não entram na contagem:

- a declaração do contrato;
- os mapas internos dos temas;
- testes;
- relatórios e documentação.

Essa escolha evita contar a própria implementação como consumidor. Uma ocorrência única pode alimentar vários widgets em runtime, portanto “um consumidor” é sinal para revisão, não condenação automática.

Cada token foi classificado no CSV por uma ou mais categorias solicitadas:

1. semântico global;
2. componente legitimamente específico;
3. possível duplicação semântica;
4. alias conceitual;
5. token excessivamente específico;
6. token atualmente não consumido;
7. token provisório;
8. poderia reutilizar outro existente;
9. necessário para preservar diferença visual real.

As comparações de duplicidade consideraram intenção, valores nos três temas e, para gradientes, direção e stops. Igualdade física isolada não foi tratada como prova de equivalência semântica.

A matriz completa, com os 247 tokens, valores por tema, estado, consumidores, quantidade de usos, classificação e observação, está em `MAPA_TOKENS_DESIGN_SYSTEM.csv`.

## 4. Dimensão e saúde do contrato

### 4.1 Por nível e tipo

| Nível | Cores | Gradientes | Total | Sem consumo | Um uso | Múltiplos usos |
|---|---:|---:|---:|---:|---:|---:|
| Semântico | 93 | 9 | 102 | 43 | 21 | 38 |
| Componente | 137 | 8 | 145 | 59 | 16 | 70 |
| **Total** | **230** | **17** | **247** | **102** | **37** | **108** |

Há 408 referências literais em código de produção. O contrato tem 145 tokens ativos (58,7%) e 102 sem consumidor ativo (41,3%).

### 4.2 Por família

| Família | Tokens | Sem consumo | Um uso | Múltiplos usos | Ocorrências | Consumidores principais |
|---|---:|---:|---:|---:|---:|---|
| `canvas` | 3 | 2 | 1 | 0 | 1 | `tema.py` |
| `surface` | 12 | 2 | 1 | 9 | 36 | `tema.py` |
| `text` | 17 | 1 | 7 | 9 | 41 | `tema.py` |
| `border` | 15 | 0 | 6 | 9 | 38 | `tema.py` |
| `action` | 13 | 6 | 1 | 6 | 44 | `tema.py` |
| `feedback` | 16 | 16 | 0 | 0 | 0 | ainda não integrado |
| `focus` | 2 | 1 | 0 | 1 | 3 | `tema.py` |
| `icon` | 6 | 3 | 0 | 3 | 9 | `icones.py` |
| `overlay` | 5 | 3 | 1 | 1 | 4 | `tema.py` |
| `glow` | 4 | 4 | 0 | 0 | 0 | ainda não integrado |
| `gradient` | 9 | 5 | 4 | 0 | 4 | `tema.py` |
| `answer` | 33 | 33 | 0 | 0 | 0 | reservado para o Resolvedor |
| `progress` | 7 | 3 | 4 | 0 | 4 | `tema.py` |
| `calendar` | 62 | 2 | 6 | 54 | 172 | `tema.py`, `main.py` |
| `chart` | 11 | 11 | 0 | 0 | 0 | módulo ainda não migrado |
| `focus_mode` | 10 | 10 | 0 | 0 | 0 | módulo ainda não migrado |
| `system_status` | 11 | 0 | 0 | 11 | 32 | `main.py`, `startup_splash.py`, `tarefas_pesadas.py` |
| `startup` | 8 | 0 | 3 | 5 | 13 | `main.py`, `startup_splash.py` |
| `task_indicator` | 3 | 0 | 3 | 0 | 3 | `tarefas_pesadas.py` |

### 4.3 Diagnóstico das famílias gerais

- `border.*` é a família mais madura: todos os 15 tokens têm consumo.
- `surface.*`, `text.*` e `action.*` já sustentam os controles compartilhados, mas ainda contêm papéis preparados para módulos futuros.
- `feedback.*` e `glow.*` são semanticamente coerentes, porém permanecem totalmente desconectados. Devem ser avaliados durante as migrações que realmente exibem feedback e brilho.
- `icon.*` está saudável para o escopo 3A: três papéis ativos e três papéis de reserva.
- `overlay.*` ainda mistura overlays de tela e seleção de texto. A separação é semanticamente válida, mas os três papéis sem consumo devem ser confirmados antes de se tornarem dependências de novos módulos.
- `gradient.*` é coerente como infraestrutura, embora cinco dos nove gradientes semânticos ainda sejam provisórios.

### 4.4 Diagnóstico das famílias de componente

- `answer.*`: semanticamente apropriada, mas totalmente provisória até a Etapa 3E. Não deve ser removida; também não deve ser conectada sem recaracterização.
- `progress.*`: quatro tokens ativos; `complete`, `warning` e `fill_gradient` ainda não são consumidos.
- `calendar.*`: família extensa, mas com 60 de 62 tokens ativos e diferenças reais entre temas/estados.
- `chart.*`: os 11 tokens são provisórios e não consumidos; as séries são justificáveis, enquanto eixo, grade e rótulo devem ser comparados aos semânticos globais quando o gráfico for migrado.
- `focus_mode.*`: os 10 tokens são provisórios; oito cores partem de aliases conceituais, mas várias divergem fisicamente dos globais após os overrides de compatibilidade.
- `system_status.*`, `startup.*` e `task_indicator.*`: específicos, porém justificados. Formam a subpaleta fixa de inicialização e tarefas, usada por três fluxos e deliberadamente independente do tema.

## 5. Mapeamento de consumo

### 5.1 Tokens sem consumidor ativo: 102

Agrupados por família:

- `canvas`: `canvas.app`, `canvas.dialog`;
- `surface`: `surface.pressed`, `surface.disabled`;
- `text`: `text.on_feedback`;
- `action`: `action.primary`, `action.primary_hover`, `action.primary_pressed`, `action.primary_disabled`, `action.destructive`, `action.destructive_hover`;
- `feedback`: os 16 tokens `feedback.success_*`, `feedback.warning_*`, `feedback.danger_*` e `feedback.info_*`;
- `focus`: `focus.keyboard`;
- `icon`: `icon.default`, `icon.muted`, `icon.disabled`;
- `overlay`: `overlay.scrim`, `overlay.light`, `overlay.dark`;
- `glow`: `glow.primary`, `glow.focus`, `glow.success`, `glow.danger`;
- `gradient`: `gradient.action_primary`, `gradient.action_primary_hover`, `gradient.surface_elevated`, `gradient.hero`, `gradient.progress`;
- `answer`: todos os 33 tokens da família;
- `progress`: `progress.complete`, `progress.warning`, `progress.fill_gradient`;
- `calendar`: `calendar.weekend_text`, `calendar.outside_month_text`;
- `chart`: todos os 11 tokens da família;
- `focus_mode`: todos os 10 tokens da família.

Os 102 tokens estão identificados individualmente no CSV. A ausência de consumo é mais preocupante nos papéis genéricos sem módulo-alvo claro do que em `answer.*`, `chart.*` e `focus_mode.*`, que têm destinos conhecidos.

### 5.2 Tokens com exatamente um uso: 37

- `canvas.inset`;
- `surface.focused`;
- `text.inverse`, `text.selected`, `text.choice`, `text.interactive_hover`, `text.control_subtle`, `text.readonly`, `text.popup`;
- `border.active`, `border.selected`, `border.focus`, `border.control_subtle`, `border.control_hover`, `border.checked`;
- `action.checked`;
- `overlay.selection_subtle`;
- `gradient.control_input`, `gradient.control_header`, `gradient.control_tab`, `gradient.control_selected`;
- `progress.track`, `progress.border`, `progress.fill`, `progress.text`;
- `calendar.today_surface`, `calendar.today_text`, `calendar.late_surface`, `calendar.late_text`, `calendar.scheduled_surface`, `calendar.scheduled_text`;
- `startup.progress_pulse`, `startup.progress_gradient`, `startup.shimmer_gradient`;
- `task_indicator.mark_surface`, `task_indicator.mark_border`, `task_indicator.mark_text`.

Os casos de um uso são, em geral, adaptadores programáticos ou pontos centralizados de renderização. Não há recomendação de remoção baseada apenas nessa contagem.

## 6. Duplicidade conceitual e aliases

### 6.1 Resultado quantitativo

O CSV marca 28 tokens para revisão de reutilização:

- 23 aliases conceituais cujo valor atual coincide com o token de origem nos três temas;
- 5 candidatos adicionais encontrados por revisão semântica entre famílias ou papéis irmãos.

Isso não significa recomendar 28 remoções. Muitos aliases de componente são fronteiras deliberadas que permitem divergência futura sem contaminar o token global.

Os 23 aliases exatos se distribuem assim:

- 11 em `answer.*`;
- 2 em `progress.*`;
- 8 em `chart.*`;
- 2 em `focus_mode.*`.

Exemplos válidos de alias que podem precisar permanecer independentes são `answer.correct_surface` versus `feedback.success_surface` e `chart.series_3` versus `feedback.success_icon`: a igualdade física atual não garante que o domínio continuará igual.

### 6.2 Candidatos fortes, sem alteração nesta etapa

| Token candidato | Reutilização possível | Motivo | Recomendação |
|---|---|---|---|
| `progress.fill_gradient` | `gradient.progress` | direção e stops idênticos nos três temas; ambos sem consumo | decidir quando o próximo progresso for migrado |
| `calendar.forecast_count_text` | `calendar.forecast_badge_text` | mesma função de metadado compacto e mesmos valores | bom candidato após teste visual |
| `calendar.forecast_open_hover_surface` | `calendar.forecast_toggle_checked_surface` | mesma superfície de ênfase interativa e mesmos valores | revisar nomenclatura/precedência antes de aliasar |
| `calendar.forecast_action_text` | `calendar.today_text` | mesmo acento nos três temas | manter separado se “ação” precisar evoluir independentemente |
| `calendar.selected_text` | `text.on_action` | texto branco idêntico nos três temas | candidato a alias interno, preservando o nome público se necessário |

### 6.3 Comparações solicitadas

- `calendar.forecast_card_text` **não** equivale a `text.secondary`: os valores divergem nos três temas e o primeiro representa conteúdo principal do card.
- `calendar.forecast_open_text` **não** deve ser trocado por `action.*`: `action.*` representa superfícies/ações, não a cor textual discreta do comando; os valores também divergem.
- `calendar.forecast_completed` **não** equivale a `feedback.success_icon`: o estado “realizado” tem valores próprios em Claro, Escuro e Futurista.

## 7. Tokens possivelmente específicos demais

Três tokens merecem revisão prioritária:

- `progress.fill_gradient`;
- `calendar.forecast_count_text`;
- `calendar.forecast_open_hover_surface`.

`calendar.forecast_action_text` e `calendar.selected_text` também são candidatos de alias, mas seus nomes públicos expressam papéis úteis e não foram classificados como excessivamente específicos.

Os tokens de `system_status.*` parecem numerosos quando vistos isoladamente, mas são compartilhados pelos fluxos de splash, fallback e tarefa pesada. Seus 32 usos e a independência deliberada de tema justificam a subpaleta.

Não foi encontrado token que represente conteúdo textual do calendário em vez de decisão visual. `forecast_review`, `forecast_recommendation`, `forecast_simulation` e `forecast_completed` nomeiam categorias visuais de card, não strings de conteúdo.

## 8. Auditoria específica de `calendar.*`

### 8.1 Situação geral

- total atual: 62 tokens;
- existentes antes da 3D: 11;
- criados na 3D: 51;
- tokens ativos: 60;
- tokens sem consumidor: 2;
- tokens com um uso: 6;
- tokens com múltiplos usos: 54;
- ocorrências totais: 172;
- gradientes: 0.

### 8.2 Os 51 tokens criados na Etapa 3D

Todos os 51 têm consumidor ativo. Quatro possuem uma única referência literal (`late_surface`, `late_text`, `scheduled_surface`, `scheduled_text`) e 47 têm múltiplas referências. Isso confirma que a expansão da Etapa 3D foi motivada por uso real, não por antecipação abstrata.

Há três candidatos fortes de consolidação dentro desses 51:

- `forecast_count_text`;
- `forecast_open_hover_surface`;
- `forecast_action_text`.

Os demais preservam diferenças de valor, função, tema ou precedência. Casos visualmente próximos como badge versus contador e painel mensal versus painel semanal divergem em pelo menos um tema e não devem ser unidos por similaridade.

### 8.3 Tokens anteriores sem consumo

- `calendar.weekend_text`;
- `calendar.outside_month_text`.

Ambos permanecem componentes semanticamente plausíveis e foram classificados como provisórios. Não devem ser removidos antes de confirmar se o `QCalendarWidget` pode expor esses papéis de forma estável sem alterar a renderização atual.

## 9. Gradientes

Há 17 tokens de gradiente:

- 9 semânticos;
- 8 de componente;
- 6 consumidos;
- 11 sem consumidor.

Gradientes consumidos:

- `gradient.control_input`;
- `gradient.control_header`;
- `gradient.control_tab`;
- `gradient.control_selected`;
- `startup.progress_gradient`;
- `startup.shimmer_gradient`.

Gradientes sem consumidor:

- `gradient.action_primary`;
- `gradient.action_primary_hover`;
- `gradient.surface_elevated`;
- `gradient.hero`;
- `gradient.progress`;
- `answer.selected_gradient`;
- `answer.correct_gradient`;
- `answer.incorrect_gradient`;
- `progress.fill_gradient`;
- `focus_mode.action_gradient`;
- `focus_mode.action_hover_gradient`.

`gradient.action_primary`, `gradient.progress` e `progress.fill_gradient` possuem especificações idênticas nos três temas. O papel semântico de ação e o de progresso podem evoluir separadamente, mas `progress.fill_gradient` é o candidato mais fraco do trio.

Os gradientes `answer.*` não são descartáveis: o Futurista usa gradientes reais nos estados selecionado, correto e incorreto. Entretanto, a auditoria encontrou uma incompatibilidade importante para a futura 3E: `answer.correct_gradient` e `answer.incorrect_gradient` estão registrados horizontalmente, enquanto o QSS atual do Resolvedor Futurista usa direção diagonal. Nenhuma correção foi aplicada nesta etapa.

Não há gradientes sem variante de tema nem stops inválidos; o contrato continua estruturalmente consistente.

## 10. Paleta física

- cores físicas registradas: 309;
- cores referenciadas por exatamente um token: 184;
- cores compartilhadas por mais de um token: 102;
- cores físicas órfãs: 23;
- duplicidades literais na lista física: 0.

As 23 cores órfãs são:

`#000000`, `#132B40`, `#173046`, `#183850`, `#1D466D`, `#355F9F`, `#3E7397`, `#4C7EE0`, `#4C7FD1`, `#55A7D5`, `#596579`, `#7C899B`, `#7DADFF`, `#8490A1`, `#8EAFC3`, `#981827`, `#9FB1C3`, `#B9D7FF`, `#BCE7FF`, `#DCE4ED`, `#FF7382`, `#FFABB3`, `#FFD0C9`.

Esses valores podem ser resíduos do inventário inicial ou reservas para migrações futuras. A remoção agora reduziria rastreabilidade sem benefício funcional; recomenda-se reavaliá-los após Resolvedor, Modo Foco e gráficos.

## 11. Consistência de nomenclatura

O padrão predominante `<objeto>_<estado>_<propriedade>` está claro em `answer.*` e na maior parte de `calendar.*`. Foram encontrados os seguintes pontos de atenção:

| Caso | Problema | Recomendação futura |
|---|---|---|
| `progress.complete`, `progress.warning` | não informa se o valor é fill, texto ou ícone | renomear apenas em mudança contratual planejada |
| `calendar.forecast_review`, `forecast_recommendation`, `forecast_simulation`, `forecast_completed` | papel visual implícito; hoje funcionam como acento | documentar como `accent` antes de ampliar a família |
| `calendar.legend_today`, `legend_late`, `legend_scheduled` | não explicita marker/fill/text | manter por compatibilidade e esclarecer na documentação |
| `focus_mode.action`, `focus_mode.danger` | propriedade visual implícita | definir se são surface, fill ou accent na migração do módulo |
| `system_status.text_primary` versus `startup.subtitle_text` | família fixa usa prefixo `text_`, demais usam sufixo `_text` | não renomear sem estratégia de compatibilidade |
| `startup.progress_pulse` | não explicita fill/glow | esclarecer no contrato; o uso programático atual é válido |

Os estados básicos (`hover`, `pressed`, `selected`, `focused`, `keyboard_focus`, `checked`, `disabled`, `correct`, `incorrect`, `struck`) estão nomeados de maneira coerente. Estados de domínio do calendário (`today`, `late`, `scheduled`, `past`, `completed`) são extensões legítimas e não precisam entrar no enum genérico apenas por existirem.

## 12. Pré-análise do Resolvedor

### 12.1 Matriz preliminar

| Estado/elemento | Token provavelmente reutilizável | Token de componente existente | Novo token possivelmente necessário | Justificativa |
|---|---|---|---|---|
| alternativa normal | `surface.*`, `border.*`, `text.*` como origem | `answer.normal_surface`, `normal_border`, `normal_text` | nenhum para o papel básico | superfície e borda já reproduzem a estrutura; texto precisa recaracterização |
| hover | `surface.hover`, `border.hover` como origem | `answer.hover_surface`, `answer.hover_border` | nenhum | nomes e valores de superfície/borda já existem |
| selecionada | `text.on_action`, `action.primary` | `answer.selected_surface`, `selected_border`, `selected_text`, `selected_gradient`, `checked_indicator` | possivelmente 2–3 papéis do indicador de rádio | gradiente do card existe; fill/borda do indicador divergem nos temas |
| foco por teclado | `focus.keyboard` como origem | `answer.keyboard_focus_border` | nenhum | o caminho existe, mas seus valores atuais não são os da linha de base |
| tachada | `text.muted`, `surface.disabled` como referência | `answer.struck_surface`, `struck_border`, `struck_text` | `struck_gradient`, `struck_hover_surface`, `struck_hover_border` | o Futurista usa gradiente e os três temas têm hover próprio |
| correta | `feedback.success_*` como origem | `answer.correct_surface`, `correct_border`, `correct_text`, `correct_gradient` | nenhum para o card | stops existem; direção do gradiente Futurista precisa ser corrigida na migração |
| incorreta | `feedback.danger_*` como origem | `answer.incorrect_surface`, `incorrect_border`, `incorrect_text`, `incorrect_gradient` | nenhum para o card | mesma ressalva de direção do gradiente |
| explicação | `text.secondary`, `feedback.*` | `answer.explanation_surface`, `answer.explanation_text` | `answer.explanation_border` e talvez `explanation_title` | a caixa atual tem borda e título próprios sem token correspondente |
| editor inline | `text.primary`, `text.on_action`, `overlay.selection` | `answer.editor_surface`, `editor_border`, `editor_selection` | `answer.editor_text` e, se necessário, papéis de ação do editor | valores do editor atual não coincidem integralmente com os três tokens existentes |
| tesoura | `icon.muted`, `icon.action`, `action.ghost` como referência | nenhum token `answer.*` específico | 5–7 papéis para normal, hover, checked e disabled | os valores atuais não coincidem com os tokens genéricos nos três temas |
| confirmar/próxima | `gradient.action_primary`, `gradient.action_primary_hover`, `text.on_action` | nenhum adicional obrigatório | 2 papéis de borda, se a caracterização confirmar | os gradientes globais coincidem com o botão primário do Resolvedor |
| feedback pós-resposta | `feedback.success_*`, `feedback.danger_*` | `answer.correct_*`, `answer.incorrect_*`, `answer.explanation_*` | 1–2 papéis de borda/título | pode compor tokens já existentes sem criar família paralela |

### 12.2 Incompatibilidades objetivas a tratar na 3E

Sem alterar nada nesta etapa, foram registrados estes pontos:

- `answer.keyboard_focus_border` não contém hoje as cores legadas do foco do Resolvedor (`#5966D9`, `#8B95FF`, `#4BC9F2`);
- `answer.struck_*` não contém os valores finais dos blocos de alta especificidade `ESTILO_RESOLVEDOR_ELIMINADAS_*`;
- falta representação do gradiente tachado Futurista e do hover tachado;
- `answer.correct_gradient` e `answer.incorrect_gradient` têm stops compatíveis, mas direção incompatível com o Futurista atual;
- `answer.checked_indicator` coincide apenas com parte da caracterização do rádio; Escuro e Futurista usam valores próprios;
- `answer.normal_text`, `answer.explanation_*` e `answer.editor_*` precisam comparação pela cascata final, não simples substituição textual.

Esses achados são evidência de que os tokens `answer.*` são provisórios. Corrigi-los agora quebraria a regra documental desta etapa e anteciparia a migração.

## 13. Orçamento arquitetônico para a Etapa 3E

Para o núcleo interativo solicitado na pré-análise, a estimativa é:

- **30 a 31 tokens existentes reutilizáveis**, sendo 27 de `answer.*` e 3–4 semânticos/gradientes globais;
- **12 a 18 tokens novos** para lacunas reais, sobretudo tachado, tesoura, bordas de ação, editor e caixa de explicação.

Os seis tokens `answer.pressed_*`, `answer.focused_border` e `answer.disabled_*` sem estado legado explícito não devem ser forçados apenas para aumentar consumo.

Se a futura 3E incluir também todo o chrome de sessão — overview, miniestatísticas, barra de foco, progresso, pular, encerrar e painel de ações — a contagem deve ser refeita após caracterização. Essa camada possui decisões visuais próprias e pode exigir papéis adicionais.

Sinais de alerta:

- ultrapassar 18 tokens novos apenas para os estados centrais listados acima;
- criar um token por seletor em vez de por papel;
- criar novas famílias paralelas a `answer.*` ou `feedback.*`;
- conectar tokens provisórios sem provar igualdade nos três temas;
- alterar valores globais para satisfazer somente o Resolvedor.

O intervalo é um orçamento de revisão, não um limite arbitrário. Diferenças visuais comprovadas continuam tendo precedência.

## 14. Riscos

1. **Inflação silenciosa por antecipação:** 102 tokens ainda não consumidos tornam fácil adicionar mais papéis sem evidência de uso.
2. **Alias prematuro:** 23 aliases são fisicamente iguais hoje, mas vários representam fronteiras de domínio legítimas.
3. **Cascata do Futurista:** o QSS efetivo resulta de Escuro + overrides; comparar apenas blocos isolados pode produzir falsos equivalentes.
4. **Gradientes provisórios:** direção, não apenas stops, precisa ser caracterizada no Resolvedor.
5. **Contagem de consumo literal:** referências construídas dinamicamente não seriam detectadas; não foi encontrado indício de construção dinâmica no consumo atual.
6. **Nomes ambíguos:** alguns tokens não explicitam surface/text/border/accent e podem gerar reutilização indevida.
7. **Paleta órfã:** 23 cores físicas sem token aumentam a superfície de manutenção, mas removê-las antes das próximas migrações pode perder referência histórica.

## 15. Validação executada

- `py_compile` de `ui/design/*.py`, consumidores das Etapas 3A/3B/3C/3D, `tema.py`, `main.py` e testes pertinentes: passou;
- `test_design_system.py` + 3A + 3B + 3C + 3D: **42 testes passaram**;
- `testes_smoke.py`: `VighnaStudy 0.29.59: testes smoke OK`;
- `PRAGMA integrity_check`: `ok`;
- `PRAGMA foreign_key_check`: zero violações;
- SHA-256 de `estudos.db` antes e depois dos testes: `81abf14ddb8cb41cf42ecee3f1e41a27a91338dac94093221f4f734ed7811f92`;
- SHA-256 do schema SQLite antes e depois: `0a9385cc1aa85cb3824a728b28da00244a4368b7df79826f6e224ef82f26f04c`;
- versão, build e schema declarado permaneceram `0.29.59`, `calendar-week-forecast-v1` e `25`.

## 16. Recomendação final

**Prosseguir para a Etapa 3E sem uma etapa prévia de correção ampla.**

A arquitetura tem fronteiras úteis e já sustenta múltiplos consumidores reais. O crescimento do calendário foi alto, mas justificado por consumo e diferenças visuais concretas. A dívida existente está concentrada em tokens provisórios e aliases ainda não validados por migração.

Para a 3E:

1. caracterizar a cascata final dos três temas antes de conectar `answer.*`;
2. corrigir somente os tokens existentes que não reproduzem a linha de base do Resolvedor;
3. criar tokens novos apenas para lacunas comprovadas;
4. manter a família `feedback.*` como origem semântica, sem eliminar a fronteira `answer.*` automaticamente;
5. revisar os 28 candidatos de alias somente depois que o Resolvedor estiver migrado e seus testes de equivalência estiverem estáveis.

Nenhuma correção, consolidação ou migração foi aplicada nesta etapa.
