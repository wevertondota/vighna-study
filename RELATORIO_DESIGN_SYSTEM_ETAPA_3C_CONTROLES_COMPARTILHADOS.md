# Relatório — Design System Vighna — Etapa 3C: Controles compartilhados

## Resultado

Os blocos QSS inequivocamente globais dos controles compartilhados foram conectados ao Design System sem alteração visual intencional. A comparação automatizada do stylesheet completo de Claro, Escuro e Futurista manteve os mesmos hashes canônicos da linha de base, normalizando apenas caixa hexadecimal e espaços.

A cascata existente foi preservada: o Futurista continua sendo `stylesheet_escuro() + overrides`. Estilos específicos de Dashboard, resolvedor, Calendário, Modo Foco, gráficos, cards, modais e seletores nomeados não foram migrados.

Versão preservada: VighnaStudy `0.29.59`, build `calendar-week-forecast-v1`, schema `25`.

## Arquivos alterados

- `tema.py`: somente valores visuais dos blocos globais autorizados passam por tokens.
- `ui/design/palette.py`: registra os valores físicos exatos usados pelos controles caracterizados.
- `ui/design/tokens.py`: acrescenta papéis compartilhados comprovados e quatro gradientes de controle.
- `ui/design/themes.py`: mapeia os papéis nos três temas com os valores legados exatos.
- `ui/design/adapters.py`: acrescenta `render_qss()` para resolver marcadores explícitos em blocos QSS extensos.
- `ui/design/__init__.py`: publica `render_qss()` e atualiza a descrição do estágio de integração.
- `test_design_system.py`: testa o novo adaptador e atualiza a caracterização de `border.default` para a borda global real do tema Escuro.
- `test_design_system_controles_compartilhados.py`: caracteriza o stylesheet completo, valores, estados, gradientes e cascata.
- `DESIGN_SYSTEM.md`: documenta a integração incremental e o consumo por marcadores.
- `RELATORIO_DESIGN_SYSTEM_ETAPA_3C_CONTROLES_COMPARTILHADOS.md`: registra esta etapa.

Não houve alteração em `main.py`, banco, schema, versão, build, layouts, dimensões ou lógica funcional.

## Estratégia e caracterização anterior

Antes da substituição, foram capturados hashes SHA-256 do QSS integral após uma normalização estritamente não visual: caixa dos hexadecimais e sequência de espaços. A linha de base foi:

| Tema | Hash canônico |
|---|---|
| Claro | `139709f8c57e00f16848668f9226703c7f8ff391dd9aea2bba8b2eae20ac2c5f` |
| Escuro | `ebbc21363d0035058301d060eb099fb2d33b992e8537c20f9bf1e77f8a2b4f3e` |
| Futurista | `0e588bb372946b4a6f61ad406c817fd155cac8c3c4286e9f93b7a09d06dc8622` |

Os 3/3 testes de baseline passaram antes da substituição. Depois da migração, os mesmos três hashes continuaram idênticos. Essa verificação abrange o QSS final inteiro, inclusive a ordem da cascata e os estilos específicos que permaneceram legados.

## Blocos migrados

Foram migrados aproximadamente **61 blocos/grupos de seletores**, distribuídos entre:

- `QPushButton` genérico: normal, hover, pressed e disabled;
- `QLineEdit`, `QTextEdit`, `QPlainTextEdit` quando presente, `QComboBox`, `QSpinBox`, `QDateEdit` e `QAbstractSpinBox` quando presente;
- foco, hover e readonly explicitamente existentes nesses inputs;
- popup genérico de `QComboBox`;
- `QCheckBox` e `QRadioButton` do Futurista, inclusive checked;
- `QTableWidget` e `QTreeWidget` genéricos;
- `QHeaderView::section` genérico;
- `QTabWidget::pane` e `QTabBar`, inclusive selected;
- scrollbar vertical genérica, inclusive hover e páginas/linhas transparentes;
- `QProgressBar` genérico do Futurista;
- `QToolTip` genérico nos três temas.

Os estados cobertos são normal, hover, pressed, focused, selected, checked, disabled e readonly, conforme existiam no QSS legado. Nenhum estado novo foi inventado.

## Blocos deliberadamente não migrados

- `#primaryButton`, `#subtleButton` e variantes nomeadas: aparecem combinados com seletores de Dashboard, resolvedor e módulos específicos em várias camadas; migrá-los isoladamente nesta etapa teria risco de precedência incidental.
- `QToolButton` Futurista: não estava no escopo explícito e possui tratamento próprio.
- scrollbar horizontal Futurista: usa uma paleta/camada diferente da scrollbar vertical final e exige caracterização isolada.
- seletores de item de tabela com maior especificidade, como `QTableWidget::item:selected`: permanecem legados porque não são equivalentes ao estado de seleção do bloco genérico.
- blocos iniciais de Claro/Escuro que são sobrescritos por refinamentos finais: mantidos para não reestruturar a cascata.
- badges/chips, cards, modais e botões nomeados: são específicos ou ambíguos.
- Dashboard, resolvedor, alternativas, Modo Foco, calendário, semana prevista, Central de Questões, gráficos e QPainter: fora do escopo.

## Adaptador QSS

`render_qss(tema, template)` resolve somente:

- `{{color:caminho.do_token}}` por `qss_color()`;
- `{{gradient:caminho.do_token}}` por `qss_gradient()`.

O adaptador mantém o QSS legível sem transformar as aproximadamente 22 mil linhas de `tema.py` em `f-string`. Tokens ausentes ou do tipo errado continuam falhando explicitamente pela API pública. Não há widget ativo, estado global ou efeito colateral de importação.

## Tokens reutilizados

Foram reutilizadas famílias já públicas, entre elas:

- `surface.primary`, `surface.secondary`, `surface.tertiary`, `surface.elevated`, `surface.inset`, `surface.hover` e `surface.selected`;
- `text.primary`, `text.secondary`, `text.muted`, `text.disabled`, `text.inverse`, `text.link`, `text.on_action`;
- `border.default`, `border.subtle`, `border.strong`, `border.hover`, `border.active`, `border.selected`, `border.disabled`, `border.focus`;
- `action.secondary`, `action.secondary_hover`, `action.secondary_pressed`, `action.secondary_disabled`, `action.ghost`, `action.ghost_hover`;
- `focus.ring`, `overlay.selection`;
- `progress.track`, `progress.fill` e `progress.text`.

Alguns valores provisórios desses tokens, definidos na fundação ainda desconectada da UI, foram refinados para os valores efetivos dos controles globais. Os consumidores anteriores não sofreram impacto: ícones usam apenas `icon.*`; startup e tarefas usam tokens fixos `system_status.*`, `startup.*` e `task_indicator.*`.

Como `answer.*`, `calendar.*`, `chart.*` e `focus_mode.*` originalmente derivavam de parte desses papéis semânticos, seus valores anteriores foram explicitados nos overrides de componente. Isso impede que a caracterização dos controles altere silenciosamente contratos de módulos fora do escopo. A única exceção é `progress.*` Futurista, consumido pelo `QProgressBar` genérico autorizado nesta etapa.

## Tokens novos

Foram criados **26 tokens**, o menor conjunto encontrado que preserva papéis distintos sem aproximar valores:

### Semânticos de cor: 21

- superfícies: `surface.interactive`, `surface.inverse`, `surface.focused`;
- texto: `text.control`, `text.selected`, `text.choice`, `text.header`, `text.interactive_hover`, `text.selection_accent`, `text.control_subtle`, `text.readonly`, `text.popup`;
- bordas: `border.control_subtle`, `border.control_hover`, `border.divider`, `border.divider_strong`, `border.grid`, `border.control_indicator`, `border.checked`;
- ação/overlay: `action.checked`, `overlay.selection_subtle`.

### Semânticos de gradiente: 4

- `gradient.control_input`;
- `gradient.control_header`;
- `gradient.control_tab`;
- `gradient.control_selected`.

### Componente: 1

- `progress.border`.

O contrato passa de 170 para **196 tokens**: 102 semânticos e 94 de componente. Nenhum `specific.*` foi promovido.

Os papéis `control_subtle`/`selection_subtle` foram mantidos separados porque a primeira camada Futurista ainda governa `QPlainTextEdit` e readonly, enquanto a camada final governa o subconjunto refinado. Consolidá-los alteraria valores ou a cascata.

## Valores antes e depois

Exemplos representativos da equivalência:

| Papel | Claro | Escuro | Futurista |
|---|---|---|---|
| botão genérico | `#FFFFFF` → `action.secondary` | `#1F2937` → `action.secondary` | `#11253A` → `action.secondary` |
| texto de input final | `#182033` → `text.control` | `#EDF1F7` → `text.control` | `#EEF9FF` → `text.control` |
| borda de input final | `#CBD3DF` → `border.default` | `#40536A` → `border.default` | `#40668B` → `border.default` |
| foco final | `#7667E8` → `focus.ring` | `#8879F3` → `focus.ring` | `#59E3FF` → `focus.ring` |
| seleção de tabela | `#EEEAFF` → `surface.selected` | `#39336E` → `surface.selected` | `#234766` → `surface.selected` |
| barra de progresso | legado não explícito nesse bloco | legado não explícito nesse bloco | `#4AA5D3` → `progress.fill` |

Todos os valores depois são resolvidos exatamente para o literal anterior; não houve aproximação de cor.

## Gradientes migrados

Foram centralizados **quatro gradientes QSS**, todos do refinamento global Futurista:

| Token | Direção | Stops preservados | Uso |
|---|---|---|---|
| `gradient.control_input` | diagonal `(0,0) → (1,1)` | `0.0 #10253A`, `1.0 #0A1829` | inputs finais |
| `gradient.control_header` | horizontal `(0,0) → (1,0)` | `0.0 #132C45`, `1.0 #0C1D31` | header de tabela |
| `gradient.control_tab` | horizontal `(0,0) → (1,0)` | `0.0 #132B42`, `1.0 #0C1D30` | tab normal |
| `gradient.control_selected` | horizontal `(0,0) → (1,0)` | `0.0 #0E6677`, `1.0 #323E8E` | tab selecionada |

As posições, direções e cores foram preservadas. As variantes Claro/Escuro existem para manter contrato uniforme, embora esses temas continuem usando cor sólida nos blocos atuais.

## Hardcodes removidos e remanescentes

Em `tema.py` foram substituídas:

- **151 ocorrências hexadecimais**;
- **3 ocorrências de `transparent`**;
- **4 expressões `qlineargradient`**, cujos 8 stops estão incluídos nas 151 ocorrências hexadecimais.

Assim, foram removidas **154 ocorrências locais de valor de cor** e centralizados quatro gradientes. O QSS fonte contém 146 marcadores de cor e quatro de gradiente; os marcadores não aparecem no stylesheet entregue à aplicação.

Permanecem em `tema.py`, deliberadamente fora do escopo ou ambíguos: 6.266 ocorrências hexadecimais, 118 `rgb/rgba`, 283 usos de `transparent` e 195 gradientes. Não se estabeleceu meta de zerar hardcodes nesta etapa.

## Testes

### Aprovados

- `py_compile` de `tema.py`, `ui/design/*.py` e testes alterados;
- Design System + caracterização 3C: **19/19**;
- Etapas 3A e 3B + integração QtAwesome: **21/21**;
- Calendário 0.29.59: **10/10**;
- resolvedor, alternativas e janelas operacionais: **28/28 verificações aplicáveis**; três asserções separadas fixam versões antigas;
- bateria histórica de Dashboard/transparência: **26/26 verificações aplicáveis**; onze asserções antigas de versão/layout foram identificadas separadamente;
- Dashboard Futurista 0.29.34: **5/5 verificações aplicáveis**; as duas falhas históricas são a versão 0.29.34 e a antiga exigência de `#06131D`;
- `testes_smoke.py`: `VighnaStudy 0.29.59: testes smoke OK`.

Também foram executados testes históricos de startup/splash/tarefas. As verificações aplicáveis não apontaram regressão da Etapa 3C; persistem asserções de builds antigos, uma expectativa de layout de splash já substituída e dois erros de limpeza de SQLite no Windows por conexão histórica não fechada.

### Falhas históricas não corrigidas

Os testes versionados entre 0.29.28 e 0.29.51 ainda contêm asserções literais para versão/build e alguns layouts posteriormente evoluídos. Alterar código atual para fazê-los passar violaria a linha de base 0.29.59. Em especial, o teste 0.29.34 que exige `#06131D` continua deliberadamente separado, conforme decisão da Etapa 2.

## Regressões encontradas e corrigidas

Durante a migração, a primeira caracterização do botão disabled Claro revelou que `action.secondary_disabled` ainda representava o valor provisório da fundação. O mapeamento foi corrigido para `#F8FAFC`, valor legado real, antes de avançar para os demais grupos. Depois disso, cada grupo manteve os hashes completos.

Uma asserção auxiliar dos testes comparava hexadecimais em minúsculas e quebras de linha internas do gradiente. Ela foi tornada insensível apenas à caixa e à formatação; o hash canônico e as verificações de stops continuaram garantindo os valores.

## Riscos observados

- `tema.py` possui muitas camadas e seletores repetidos; precedência e especificidade continuam sendo o principal risco das próximas migrações.
- Os seletores nomeados de botão misturam semântica global e de módulo; exigem uma etapa própria de caracterização antes de centralização.
- O Futurista continua herdando todo o Escuro. Remover ou simplificar overrides antes da migração completa pode alterar telas não relacionadas.
- A validação por hash comprova equivalência textual canônica do QSS, mas a baseline manual continua recomendada para efeitos dependentes do motor Qt e do sistema operacional.
- A quantidade de hardcodes remanescentes confirma que futuras etapas devem continuar pequenas e por domínio.

## Recomendações para a próxima etapa

1. Caracterizar os seletores nomeados compartilhados (`primary`, `secondary`, `subtle`, `ghost`) por consumidor antes de decidir se são realmente globais.
2. Migrar um domínio autorizado por vez, preservando os testes de hash completo como guarda de cascata.
3. Tratar a scrollbar horizontal Futurista e os estados de item de tabela em uma etapa de controles avançados, não junto de módulos de produto.
4. Manter Dashboard, resolvedor, Calendário, Modo Foco e gráficos em etapas independentes, pois cada um possui paleta e precedência próprias.

## Limite desta etapa

Nenhum calendário, resolvedor, alternativa, Modo Foco, Dashboard, gráfico, QPainter, card específico, modal específico ou gradiente exclusivo de módulo foi migrado. A Etapa 3C termina nos controles compartilhados descritos acima.
