# VighnaStudy 0.29.59 — linha de base e inventário visual para Design System

Data da auditoria: 06/10/2026

Etapa: 1 — inventário, sem migração visual

Versão: `0.29.59`

Build: `calendar-week-forecast-v1`

Schema: `25`
Commit inicial: `6b02718e4da05c5a61122d96aadc7929274e5227`

## 1. Estado inicial

- `AGENTS.md` lido e seguido.
- Branch inicial: `main`, sincronizada com `origin/main` (`+0/-0`).
- Árvore de trabalho inicialmente limpa.
- Nenhum arquivo funcional, banco, schema, layout, dimensão, comportamento ou estilo foi alterado nesta etapa.
- A versão e o build permaneceram inalterados.

### Linha de base de testes antes do inventário

- `py_compile` de `main.py`, `banco.py`, `tema.py`, `icones.py`, `foco.py`, `startup_splash.py` e `versao.py`: aprovado.
- Teste atual `test_calendario_previsao_semanal_0_29_59.py`: **10/10**.
- Testes visuais/funcionais pertinentes de resolvedor, teclado, editor inline, QtAwesome, transparência, Modo Foco, Dashboard e splash: **42 aprovados**.
- Foi detectada uma falha preexistente e histórica em `test_dashboard_futurista_neo_0_29_34.py::test_paleta_neo_tem_hierarquia_semantica`: o teste ainda exige `#06131D`, valor da versão 0.29.34 que já não existe em `tema.py` na versão 0.29.59. O teste e o código não foram modificados.

## 2. Metodologia e escopo

O corpus principal foi formado pelos arquivos rastreados pelo Git que pertencem ao código ativo. Foram pesquisados:

- hexadecimais de 3, 6 e 8 dígitos;
- `rgb(...)`, `rgba(...)` e `QColor(...)`;
- `QBrush(...)`, `QPen(...)` e `QLinearGradient`;
- `qlineargradient` e seus stops;
- `background`, `background-color`, `border`, `border-color`, `color` e transparência;
- estados QSS e propriedades dinâmicas como `hover`, `pressed`, `selected`, `checked`, `focus`, `disabled`, `answerState`, `eliminated` e `keyboardFocus`;
- estilos diretos fora de `tema.py`;
- camada QtAwesome e recursos bitmap/ICO.

Foram excluídos das métricas da aplicação ativa: `.git`, `.venv`, `dist`, `build`, backups, checkpoints de recuperação, relatórios antigos e testes. Esses arquivos continuam existentes, mas incluí-los inflaria a contagem com cópias históricas que não participam da interface atual.

Não há arquivos QSS, CSS, UI ou SVG ativos separados: o QSS está embutido principalmente em `tema.py`. Foram encontrados valores visuais ativos em cinco arquivos de código:

- `tema.py`;
- `main.py`;
- `startup_splash.py`;
- `tarefas_pesadas.py`;
- `icones.py`.

Também foram inspecionados `assets/config_gear.png`, `assets/config_gear_clean.png`, `vighnastudy.ico` e o logo Base64 embutido em `main.py`.

### Convenções do CSV

O arquivo `INVENTARIO_VISUAL_DESIGN_SYSTEM.csv` contém uma linha por ocorrência e as colunas:

`tipo`, `valor`, `valor_canonico`, `arquivo`, `linha`, `tema`, `componente`, `estado`, `funcao_visual`, `ocorrencias`, `contexto`, `observacao`.

- Hexadecimais foram normalizados para maiúsculas.
- `rgba`/`QColor` numérico foram convertidos para uma representação canônica com alpha, quando possível.
- A classificação semântica é conservadora. Casos ambíguos permanecem como `uso específico/a revisar`.
- Cores dos pixels de bitmaps não entram na contagem de cores de código; os recursos aparecem como linhas próprias e com metadados.
- A contagem de seletores é aproximada, baseada nos blocos QSS encontrados.

## 3. Resumo quantitativo

| Métrica | Resultado |
|---|---:|
| Cores distintas no código ativo | **3.310** |
| Ocorrências literais de cor | **6.953** |
| Hexadecimais | 6.545 |
| `rgba(...)` | 118 |
| `QColor(...)` numérico | 4 |
| `transparent` | 286 |
| Cores construídas dinamicamente | 5 |
| Gradientes | **201** |
| Formulações de gradiente distintas | **171** |
| Grupos de gradientes exatamente duplicados | 24 |
| Ocorrências redundantes dentro desses grupos | 30 |
| Usos de `QBrush`/`QPen` inventariados | 22 |
| Cores hardcoded fora de `tema.py` | **132 ocorrências / 84 distintas** |
| Valores visuais hardcoded, aproximadamente | **7.154** |

O valor aproximado de hardcodes soma ocorrências de cores e expressões de gradiente. Os stops também aparecem como cores, portanto essa medida representa decisões literais encontradas, não tokens semânticos únicos.

### Distribuição por tema

| Tema/contexto | Ocorrências | Cores distintas | Observação |
|---|---:|---:|---|
| Claro | 2.713 | 1.135 | Tema completo mais camadas específicas de componentes |
| Escuro | 2.432 | 1.038 | Tema completo; também é base herdada pelo Futurista |
| Futurista | 1.742 | 1.220 | Overrides e componentes próprios; em execução herda também o Escuro |
| Splash/overlay fixo escuro | 35 | 23 | Paleta fora do seletor de temas |
| Uso específico/a revisar | 31 | 28 | Desenho por `QPainter`, fallbacks e casos sem semântica segura |

As quantidades por tema não devem ser somadas como se fossem a aparência final independente do Futurista: `stylesheet_futurista()` retorna `stylesheet_escuro()` mais uma camada de overrides.

## 4. Inventário consolidado por função visual

O detalhamento por ocorrência está no CSV. A tabela abaixo resume os papéis encontrados e valores representativos, sem propor substituição.

| Função visual | Claro | Escuro | Futurista | Observação |
|---|---|---|---|---|
| 1. Background da aplicação | `#F5F7FA` | `#111827` | `#07111E` | Definido no início dos stylesheets principais |
| 2. Superfícies/cards | `#FFFFFF`, `#F8FBFF` | `#182235` | `#0D1D2D`, `#10283C` | Muitas variantes por módulo |
| 3. Superfícies secundárias | `#F8FAFC`, `#F1F5F9` | `#172033`, `#273449` | `#0C1A29`, `#132B40` | Inclui controles, rows e painéis internos |
| 4. Texto principal | `#111827`, `#1F2937` | `#F8FAFC`, `#E5E7EB` | `#EAF7FF`, `#F3FBFF` | Há variações quase brancas por componente |
| 5. Texto secundário | `#475569`, `#64748B` | `#CBD5E1`, `#94A3B8` | `#B6D9E8`, `#87A6C2` | Papel com grande fragmentação |
| 6. Texto discreto/muted | `#718096`, `#94A3B8` | `#64748B`, `#94A3B8` | `#607A8E`, `#82ABC5` | Também usado em texto desabilitado em alguns módulos |
| 7. Bordas | `#DBE3ED`, `#CBD5E1`, `#E2E8F0` | `#334155`, `#475569` | `#315A7A`, `#355F82`, `#3F7599` | Principal família de duplicidades próximas |
| 8. Bordas de foco | `#6EA5DD`, `#5966D9` | `#60A5FA`, `#8B95FF` | `#70C6E8`, `#4BC9F2` | Foco de controle e foco de alternativa usam famílias distintas |
| 9. Cor primária | `#0F3989`, `#1D4ED8`, `#2563EB` | `#2563EB`, `#60A5FA` | azuis `#355F9F`/`#4C7EE0`, índigo `#4447E8` e ciano | Não existe uma única primária global hoje |
| 10. Hover | `#F1F5F9`, `#F8FAFC` | `#273449` | `#17314B`, `#183850` | Muitos componentes criam variantes próprias |
| 11. Pressed | `#0A3266` e variantes | azuis escuros específicos | `#0F2235`, `#981827` | O Modo Foco usa família vermelha própria |
| 12. Selected | `#DBEAFE`, `#2563EB` | `#172554`, `#2563EB` | `#1D4F79`, `#285B8D` | Tabelas, calendário, tabs e respostas não compartilham um único valor |
| 13. Disabled | cinzas claros por controle | cinzas/azuis dessaturados | `#0D1827`, `#638097`, `#28465D` | Texto, fundo e borda aparecem desacoplados |
| 14. Success | `#15803D`, `#16A34A`, `#DCFCE7` | `#86EFAC`, `#163523` | `#3ECF8E`, `#69EFC1`, verdes azulados | Sucesso genérico e acerto de questão se sobrepõem parcialmente |
| 15. Warning | `#92400E`, `#D97706`, `#FEF3C7` | `#FDE68A`, `#3A2E0B` | `#FFE07A`, `#332B12` e âmbar | Inclui atraso, atenção e simulado |
| 16. Danger/error | `#B91C1C`, `#DC2626`, `#FEE2E2` | `#FCA5A5`, `#3F1D27` | `#FF6677`, `#FF9BAC`, fundos vinho | Erro, perigo e resposta incorreta usam famílias próximas, não idênticas |
| 17. Info | azuis `#1D4ED8`/`#2563EB` | `#93C5FD` | cianos/azuis `#7CC6E8`, `#5ED8FF` | Frequentemente coincide com primária |
| 18. Foco de teclado | `#5966D9` | `#8B95FF` | `#4BC9F2` | Definição explícita em `ESTILO_RESOLVEDOR_TECLADO_*` |
| 19. Respostas corretas | verdes de acerto por tema | verdes claros sobre fundo escuro | gradientes verdes e `#3ECF8E` | Estado crítico para baseline visual |
| 20. Respostas incorretas | vermelhos de erro por tema | rosa/vermelho sobre vinho | gradiente `#3A1820`→`#2A1017`, borda `#FF6677` | Não deve ser confundido com danger genérico |
| 21. Alternativas tachadas | `#E7ECF2`, `#8796A8`, `#718096` | `#0B121C`, `#526276`, `#627488` | gradiente `#07101A`→`#060D16`, borda `#3E617A` | Tem estado normal, hover e botão checked próprios |
| 22. Progresso | trilhos claros + azuis | trilhos azul-acinzentados + azul | ciano/azul e brilho animado no splash | Inclui `QProgressBar`, anéis e arcos por `QPainter` |
| 23. Calendário | hoje azul, atraso vermelho, futuro verde | equivalentes claros sobre fundos escuros | ciano/rosa/verde e cards previstos | Parte mensal tem cores dinâmicas em `main.py`; semana fica em `tema.py` |
| 24. Gráficos | amarelo `#E6A700`, laranja `#F97316`, ciano `#2FB4C7` etc. | alguns valores escolhidos por condição | idem | Cores de `QPainter` estão majoritariamente fora de `tema.py` |
| 25. Ícones | `#355874`, `#FFFFFF`, `#0F3989` | `#BED0E1`, `#FFFFFF` | `#B6D9E8`, `#FFFFFF` | QtAwesome possui dicionário separado em `icones.py` |
| 26. Gradientes | 40 ocorrências | 31 ocorrências | 128 ocorrências | Mais 2 gradientes de pintura do splash |
| 27. Overlays/transparências | `transparent` e `rgba` em cards/hover | idem | uso intenso de alpha e camadas translúcidas | Não há propriedade `opacity:` direta; alpha está embutido nas cores |
| 28. Brilho/glow futurista | pouco ou inexistente fora do tema | herdado apenas quando aplicável | cianos, azuis e `rgba`, além do shimmer do splash | Deve permanecer papel próprio, não simples `primary` |
| 29. Uso específico/a revisar | fallbacks e cores locais | idem | idem | 5 `QColor` dinâmicos, desenho customizado e componentes sem equivalência segura |

## 5. Hotspots visuais

| Arquivo | Cores hardcoded | Distintas | Gradientes | Seletores/estilos aproximados | Responsabilidade |
|---|---:|---:|---:|---:|---|
| `tema.py` | **6.821** | **3.263** | **199** | ~3.757 seletores; 3 chamadas de composição | Stylesheets completos Claro/Escuro/Futurista, Dashboard, resolvedor, tópico, calendário, Modo Foco e overrides históricos |
| `main.py` | 88 + 4 dinâmicas | 72 | 0 | ~41 seletores/fragments; 5 `setStyleSheet` | Paletas de tabelas, calendário mensal, disciplinas pausadas, gráficos `QPainter` e fallback interno do splash |
| `startup_splash.py` | 21 + 1 dinâmica | 20 | 2 | ~9 seletores; 2 `setStyleSheet` | Splash externo, barra viva, shimmer e paleta fixa escura |
| `tarefas_pesadas.py` | 14 | 14 | 0 | ~9 seletores; 1 `setStyleSheet` | Indicador/overlay de tarefas com paleta própria fixa |
| `icones.py` | 9 | 5 | 0 | dicionário de 3 temas × 3 papéis | Cores dos ícones QtAwesome e fallback |

`tema.py` é o maior hotspot, mas não é uma fonte única de verdade: 132 ocorrências de cor permanecem fora dele.

## 6. Duplicidades e inconsistências

### Valores idênticos mais repetidos

| Valor | Ocorrências | Uso predominante |
|---|---:|---|
| `#FFFFFF` | 384 | superfícies, texto inverso e ícones |
| `transparent` | 286 | labels, scroll areas, botões ghost e overlays |
| `#334155` | 154 | bordas e superfícies do Escuro |
| `#F8FAFC` | 109 | superfície/texto claro dependendo do tema |
| `#64748B` | 95 | texto secundário, ícones e bordas |
| `#94A3B8` | 94 | muted no Escuro e estados inativos |
| `#CBD5E1` | 85 | bordas claras e texto secundário escuro |
| `#E2E8F0` | 82 | bordas/superfícies claras |
| `#475569` | 79 | texto/borda secundária |
| `#1D4ED8` | 73 | primary/selected/info |

O mesmo valor muda de função entre temas; por exemplo, `#F8FAFC` pode ser superfície no Claro e texto principal no Escuro. A futura camada de tokens não pode tratar valor físico como sinônimo de papel semântico.

### Cores quase idênticas

Foram encontradas muitas famílias com distância RGB muito pequena usadas no mesmo papel:

- superfícies claras: `#FFFFFF`, `#FBFDFF`, `#FBFCFE`, `#FAFCFE`;
- superfícies quase brancas: `#F8FAFC`, `#F7F9FC`, `#F8FBFD`, `#F8FBFF`, `#F7FAFC`;
- bordas escuras: `#334155`, `#344154`, `#314357`, `#304157`, `#30445A`;
- superfícies escuras próximas: `#182235`, `#172033`, `#1F2937`, `#1D293D`;
- textos/ícones azulados próximos: `#BED0E1` no Escuro e `#B6D9E8` no Futurista;
- primárias concorrentes: azul institucional (`#0F3989`), azul de seleção (`#1D4ED8`/`#2563EB`), índigo do resolvedor (`#4F46E5`/`#6366F1`/`#4447E8`) e ciano Futurista (`#4BC9F2`/`#70C6E8`).

Parte dessas diferenças pode ser intencional para profundidade; parte parece crescimento incremental por componente. A classificação definitiva exige comparação visual, não substituição automática por proximidade matemática.

### Hardcodes fora do sistema principal

Em `main.py`:

- `aplicar_destaque_tabela()` define paletas completas Claro/Escuro/Futurista para perigo, alerta, atenção, sucesso e inativo;
- `carregar_botoes_disciplinas()` cria estilos inline diferentes para disciplina pausada;
- `atualizar_calendario_mes()` define cores de hoje, atrasada e agendada fora de `tema.py`;
- `SeletorEstrelas`, `IndicadorEstrelasFila`, `IndicadorChamasPrioridade`, `DashboardDonutWidget` e `DashboardPlanningArcWidget` desenham com `QColor`, `QBrush` e `QPen` próprios;
- `JanelaInicializacao` repete uma paleta de splash fixa.

Em `startup_splash.py` e `tarefas_pesadas.py` há componentes com paleta fixa escura, independentemente do tema selecionado.

### Paleta duplicada de inicialização/overlay

Há 16 cores em comum entre `main.py` e `startup_splash.py`. Onze aparecem nos três pontos: `main.py`, `startup_splash.py` e `tarefas_pesadas.py`:

`#071522`, `#081927`, `#081A28`, `#15364C`, `#214A64`, `#315B76`, `#3A8DF1`, `#67B7FF`, `#8FAAC0`, `#EAF4FF`, `#F5F8FF`.

Isso caracteriza uma subpaleta real de startup/tarefa, mas hoje ela está copiada, não centralizada.

### Diferenças entre componentes semelhantes

- O resolvedor usa uma família índigo própria para ação, seleção e foco, diferente dos azuis do Dashboard.
- O Modo Foco usa CTA vermelho com gradiente nos três temas, enquanto outras ações primárias usam azul/índigo.
- Calendário mensal e semana prevista implementam a mesma semântica por caminhos diferentes: `QTextCharFormat` dinâmico em `main.py` versus QSS em `tema.py`.
- O Futurista alterna entre azul, índigo e ciano para ações de alta prioridade.
- Estados `success`, resposta correta e revisão realizada compartilham verdes próximos sem um contrato explícito.

## 7. Inventário de gradientes

Foram encontradas **201 ocorrências**: 199 `qlineargradient` em `tema.py` e 2 `QLinearGradient` em `startup_splash.py`.

### Distribuição

| Tema | Gradientes |
|---|---:|
| Claro | 40 |
| Escuro | 31 |
| Futurista | 128 |
| Splash fixo | 2 |

| Direção | Quantidade |
|---|---:|
| Horizontal (`x1:0,y1:0 → x2:1,y2:0`) | 129 |
| Diagonal (`x1:0,y1:0 → x2:1,y2:1`) | 67 |
| Vertical (`x1:0,y1:0 → x2:0,y2:1`) | 3 |
| Dinâmica por coordenadas de pintura | 2 |

Todas as ocorrências, componentes, estados, direções, stops e cores estão descritos nas linhas `tipo=gradiente` do CSV.

### Grupos idênticos mais relevantes

| Ocorrências | Tema | Direção/stops | Componentes/finalidade aparente |
|---:|---|---|---|
| 5 | Futurista | horizontal, `0 #355F9F → 1 #4C7EE0` | botões primários, planejamento, pós-foco e ação do Dashboard |
| 3 | Futurista | horizontal, `0 #126F80 → 1 #286E9C` | navegação/ações da Central de Questões |
| 3 | Futurista | diagonal, `0 #0D2032 → 1 #091725` | cards/painéis elevados escuros |
| 3 | Futurista | diagonal, `0 #0D2236 → 1 #081626` | hero e notificações do Dashboard |
| 2 | Escuro | horizontal, `#315FAE → #3F72C8 → #5488DE` | CTA principal normal |
| 2 | Escuro | horizontal, `#3C6CBC → #4C80D4 → #6297E9` | hover do CTA principal |
| 2 | Futurista | horizontal, `#4447E8 → #4347E1 → #3C42D2` | CTA índigo do Dashboard/resolvedor |
| 2 por tema | Claro/Escuro/Futurista | famílias vermelhas de 3 stops | CTA do Modo Foco repetido no Dashboard e na tela de foco |

### Gradientes quase iguais

- `#202733 → #222A36 → #1D2430` aparece com stop intermediário `0.52` e `0.55`.
- Famílias de CTA azul usam stops muito próximos, mas não idênticos, entre Dashboard, planejamento e resolvedor.
- Gradientes vermelhos do Modo Foco mantêm estrutura idêntica entre módulos, mas variam levemente por tema.
- Gradientes diagonais de superfícies Futuristas repetem a mesma direção e profundidade com pequenas variações de azul muito escuro.

### Gradientes por `QPainter`

`startup_splash.py` contém:

- barra viva horizontal: `#2E74D8` em `0.0`, `#3A8DF1` em `0.55`, `#4CA8FF` em `1.0`;
- brilho móvel horizontal com coordenadas dinâmicas: transparente `QColor(125,215,255,0)`, centro `QColor(175,232,255,150)` e transparente no final.

## 8. Ícones e recursos visuais

### QtAwesome / `icones.py`

As cores são determinadas por `CORES_ICONES`, separado de `tema.py`, e resolvidas por `cor_icone(tema, papel)`. `criar_icone()` passa a cor para `qta.icon()` e possui fallback seguro para arquivo.

| Tema | `acao` | `destaque` | `configuracao` |
|---|---|---|---|
| Claro | `#355874` | `#FFFFFF` | `#0F3989` |
| Escuro | `#BED0E1` | `#FFFFFF` | `#BED0E1` |
| Futurista | `#B6D9E8` | `#FFFFFF` | `#B6D9E8` |

Conclusões:

- as cores seguem o tema por chave, mas são hardcoded numa segunda estrutura temática;
- `#FFFFFF` é repetido nos três temas;
- `acao` e `configuracao` são idênticos no Escuro e Futurista;
- há quatro pontos de chamada em `main.py`, cobrindo dez destinos de interface por meio de loops;
- glifos Unicode e ícones textuais fora de QtAwesome continuam herdando `color` do QSS e não passam por `CORES_ICONES`.

### Recursos bitmap

| Recurso | Dimensão inspecionada | Uso | Achado |
|---|---:|---|---|
| `assets/config_gear.png` | 128×128 RGBA | fallback da engrenagem | imagem branca com alpha, independente de tema |
| `assets/config_gear_clean.png` | 128×128 RGBA | não referenciado | byte a byte idêntico a `config_gear.png` |
| `vighnastudy.ico` | ICO multirresolução; primeiro frame 16×16 | executável, atalho e splash | recurso próprio, não tokenizado |
| `main.py::VIGHNASTUDY_LOGO_BASE64` | 86×210 RGBA | logo embutido | milhares de cores de pixel/alpha; fora da paleta QSS |

Os dois PNGs de engrenagem têm o mesmo SHA-256: `72d38a03e2fa506244c907fbca0f175992fee3ce8c6d04ad4dd43e4fb15b4e6e`.

## 9. Paletas atuais consolidadas

Esta seção descreve o estado encontrado; não é proposta de substituição.

### Claro

- canvas: `#F5F7FA`;
- superfícies: `#FFFFFF`, `#F8FAFC`, `#F8FBFF`, `#F1F5F9`;
- texto principal: `#111827`, `#1F2937`;
- texto secundário/muted: `#475569`, `#64748B`, `#718096`, `#94A3B8`;
- bordas: `#DBE3ED`, `#CBD5E1`, `#E2E8F0`;
- azul institucional/ação: `#0F3989`, `#1D4ED8`, `#2563EB`, com hover/pressed `#1A4BA8`/`#0A3266` em parte do Dashboard;
- sucesso: `#15803D`, `#16A34A`, `#DCFCE7`;
- warning: `#92400E`, `#D97706`, `#FEF3C7`;
- danger: `#B91C1C`, `#DC2626`, `#FEE2E2`;
- foco de teclado da alternativa: `#5966D9`.

### Escuro

- canvas: `#111827`;
- superfícies: `#182235`, `#172033`, `#1F2937`, `#273449`;
- texto principal: `#F8FAFC`, `#E5E7EB`;
- texto secundário/muted: `#CBD5E1`, `#94A3B8`, `#64748B`;
- bordas: `#334155`, `#475569`;
- ação/seleção: `#2563EB`, `#1D4ED8`, `#60A5FA`, `#93C5FD`;
- sucesso: `#86EFAC`, fundo `#163523`;
- warning: `#FDE68A`, fundo `#3A2E0B`;
- danger: `#FCA5A5`, fundo `#3F1D27`;
- foco de teclado da alternativa: `#8B95FF`.

### Futurista

O tema final é a soma do Escuro com os valores abaixo:

- canvas: `#07111E`;
- superfícies: `#0D1D2D`, `#0C1A29`, `#10283C`, `#132B40`;
- texto principal: `#EAF7FF`, `#F3FBFF`, `#E7F5FF`;
- texto secundário/muted: `#B6D9E8`, `#9FC4DD`, `#87A6C2`, `#82ABC5`, `#607A8E`;
- bordas: `#315A7A`, `#355F82`, `#3F7599`;
- ações: famílias azul (`#355F9F`→`#4C7EE0`), índigo (`#4447E8`) e ciano (`#4BC9F2`, `#70C6E8`);
- sucesso/acerto: `#3ECF8E`, `#69EFC1`;
- incorreto/danger: `#FF6677`, `#FF9BAC`, fundos vinho;
- foco de teclado da alternativa: `#4BC9F2`;
- glow/progresso: `#5ED8FF`, `#3A8DF1`, alphas ciano/azul;
- Modo Foco: família vermelha própria (`#B51F31`→`#D62B3D`→`#F04458`).

## 10. Proposta inicial de taxonomia de tokens — não implementada

A taxonomia deve separar papel semântico de valor físico e permitir valores diferentes por tema.

### Canvas e superfícies

- `canvas.app`, `canvas.page`, `canvas.dialog`;
- `surface.primary`, `surface.secondary`, `surface.tertiary`;
- `surface.elevated`, `surface.inset`, `surface.interactive`;
- `surface.hover`, `surface.pressed`, `surface.selected`, `surface.disabled`;
- `surface.overlay`, `surface.scrim`;
- `surface.splash`, `surface.task_indicator`.

### Texto

- `text.primary`, `text.secondary`, `text.muted`, `text.disabled`;
- `text.inverse`, `text.link`, `text.on_primary`;
- `text.success`, `text.warning`, `text.danger`, `text.info`.

### Bordas e foco

- `border.default`, `border.subtle`, `border.strong`;
- `border.hover`, `border.active`, `border.selected`, `border.disabled`;
- `border.focus_control`, `border.focus_keyboard`;
- `focus.ring`, `focus.ring_keyboard`.

### Ações

- `action.primary`, `action.primary_hover`, `action.primary_pressed`, `action.primary_disabled`;
- `action.secondary`, `action.secondary_hover`, `action.secondary_pressed`;
- `action.ghost`, `action.ghost_hover`;
- `action.danger`, `action.danger_hover`;
- `action.focus_mode`, `action.focus_mode_hover`, `action.focus_mode_pressed`.

O grupo `focus_mode` é necessário porque o CTA vermelho do Modo Foco não corresponde à primária azul/índigo do restante do produto.

### Feedback semântico

Para cada família `success`, `warning`, `danger` e `info`:

- `.surface`, `.surface_subtle`, `.text`, `.border`, `.icon`.

Também devem existir papéis separados para `attention` e `late`, pois hoje nem todo warning significa a mesma coisa.

### Questões e respostas

- `answer.normal_surface`, `answer.normal_border`, `answer.normal_text`;
- `answer.hover_surface`, `answer.hover_border`;
- `answer.selected_surface`, `answer.selected_border`, `answer.selected_text`;
- `answer.keyboard_focus_border`;
- `answer.correct_surface`, `answer.correct_border`, `answer.correct_text`;
- `answer.incorrect_surface`, `answer.incorrect_border`, `answer.incorrect_text`;
- `answer.struck_surface`, `answer.struck_border`, `answer.struck_text`;
- `answer.explanation_surface`, `answer.explanation_text`;
- `answer.editor_surface`, `answer.editor_border`, `answer.editor_selection`.

### Progresso, calendário e gráficos

- `progress.track`, `progress.fill`, `progress.fill_secondary`, `progress.glow`;
- `calendar.today_surface`, `calendar.today_border`, `calendar.today_text`;
- `calendar.late`, `calendar.scheduled`, `calendar.completed`;
- `calendar.forecast_review`, `calendar.forecast_recommendation`, `calendar.forecast_simulation`;
- `chart.axis`, `chart.grid`, `chart.track`, `chart.series_1` a `chart.series_n`;
- `chart.positive`, `chart.negative`, `chart.neutral`.

### Ícones, alpha e Futurista

- `icon.action`, `icon.highlight`, `icon.configuration`, `icon.disabled`, `icon.inverse`;
- `overlay.hover`, `overlay.selected`, `overlay.modal`, `overlay.disabled`;
- `glow.primary`, `glow.focus`, `glow.success`, `glow.progress`;
- `gradient.action_primary`, `gradient.action_primary_hover`;
- `gradient.focus_mode`, `gradient.focus_mode_hover`;
- `gradient.hero`, `gradient.surface_elevated`, `gradient.answer_correct`, `gradient.answer_incorrect`, `gradient.answer_struck`.

### Grupo provisório para exceções

- `specific.startup_*`;
- `specific.task_indicator_*`;
- `specific.gamification_*`;
- `specific.priority_flame_*`;
- `specific.review_calendar_*`.

Esses nomes são provisórios. Só devem ser promovidos ou fundidos após baseline visual e revisão de semântica.

## 11. Checklist de linha de base visual

Não foram gerados screenshots automáticos. A aplicação usa estado real de perfil, banco, cache e tarefas de startup; não há fixture visual isolada e determinística. Abrir o fluxo completo apenas para captura poderia alterar estado operacional. Conforme solicitado, não foi usado contorno frágil.

Checklist para captura manual posterior:

| Tela/estado | Claro | Escuro | Futurista | Observação de captura |
|---|:---:|:---:|:---:|---|
| Dashboard — visão completa | ☐ | ☐ | ☐ | Capturar primeira dobra e rolagem completa |
| Navegação principal/cabeçalho | ☐ | ☐ | ☐ | Normal, hover, item ativo e Configurações |
| Dashboard — recomendação e resumo | ☐ | ☐ | ☐ | Com dados e estado vazio |
| Bateria de questões — enunciado e progresso | ☐ | ☐ | ☐ | Antes de responder |
| Alternativa normal | ☐ | ☐ | ☐ | Sem hover e com hover |
| Alternativa focada pelo teclado | ☐ | ☐ | ☐ | `keyboardFocus=true` claramente visível |
| Alternativa selecionada | ☐ | ☐ | ☐ | Antes da confirmação |
| Alternativa tachada | ☐ | ☐ | ☐ | Normal e hover |
| Resposta correta | ☐ | ☐ | ☐ | Selecionada correta e gabarito revelado |
| Resposta incorreta | ☐ | ☐ | ☐ | Escolha errada mais indicação correta |
| Feedback/explicação | ☐ | ☐ | ☐ | Com texto curto e longo |
| Editor inline de explicação | ☐ | ☐ | ☐ | Editor, Salvar e Cancelar |
| Modo Foco — preparação | ☐ | ☐ | ☐ | Presets, campos e CTA |
| Modo Foco — ativo/pausado | ☐ | ☐ | ☐ | Timer, progresso e estados dos botões |
| Modo Foco — pós-foco | ☐ | ☐ | ☐ | Resultado e ações de continuidade |
| Calendário mensal | ☐ | ☐ | ☐ | Hoje, atrasada, agendada e seleção |
| Semana prevista | ☐ | ☐ | ☐ | Passado, hoje, futuro e cards de cada tipo |
| Central de Questões | ☐ | ☐ | ☐ | Lista, filtros, seleção e estado vazio |
| Visualizador de questão | ☐ | ☐ | ☐ | Alternativas longas e Certo/Errado |
| Detalhe de tópico | ☐ | ☐ | ☐ | Hero, métricas, ações e tabs |
| Estatísticas — visão geral | ☐ | ☐ | ☐ | Dados reais e estado vazio |
| Estatísticas — gráficos/tendências | ☐ | ☐ | ☐ | Legenda, eixos, séries e tooltips |
| Configurações | ☐ | ☐ | ☐ | Formulários, foco, disabled e seletor de tema |
| Modal de confirmação/alerta/erro | ☐ | ☐ | ☐ | Pelo menos um de cada papel semântico |
| Modais de importação/planejamento | ☐ | ☐ | ☐ | Conteúdo longo, tabelas e ações |
| Indicador de tarefa pesada | ☐ | ☐ | ☐ | É visual fixo; registrar sobre cada tema |
| Splash/startup externo | n/a | n/a | ☐ fixo | Capturar início, meio e final da barra |
| Fallback interno de inicialização | n/a | n/a | ☐ fixo | Comparar com splash externo |

Recomenda-se padronizar resolução, escala do Windows, tamanho da janela, perfil, massa de dados e ordem de interação antes das capturas.

## 12. Riscos para a futura migração

1. **Cascata do Futurista:** ele herda todo o Escuro e aplica overrides. Migrar por busca/substituição pode mudar precedência e aparência.
2. **Volume e fragmentação:** 3.310 cores distintas e 171 gradientes distintos tornam inviável mapear valor físico diretamente para um token único.
3. **Semântica compartilhada por valores:** a mesma cor exerce papéis diferentes dependendo do tema.
4. **Semântica diferente com cores próximas:** pequenas diferenças podem representar profundidade intencional ou apenas deriva histórica.
5. **Estilos fora de `tema.py`:** calendário, tabelas, gráficos, splash, tarefa pesada e ícones não serão migrados apenas alterando o stylesheet principal.
6. **Desenho por `QPainter`:** `QPen`, `QBrush`, gradientes e alpha exigem tokens utilizáveis em código, não apenas strings QSS.
7. **Estados do resolvedor:** seleção, foco de teclado, tachado, correta e incorreta se sobrepõem por seletor e ordem de composição.
8. **Recursos bitmap:** engrenagem, ICO e logo não respondem automaticamente ao tema.
9. **Teste visual histórico desatualizado:** o teste da 0.29.34 fixa uma cor removida; antes da migração, a estratégia de testes deve distinguir contrato atual de snapshots históricos.
10. **Ausência de screenshots determinísticos:** sem baseline visual controlada, regressões de contraste, cascata e hierarquia podem passar por testes de texto/AST.
11. **Representação de alpha:** QSS/Qt usa combinações de `rgba`, `QColor` numérico e transparência em recurso; a normalização precisa preservar o modelo de alpha.
12. **Duplicação de assets:** os dois PNGs idênticos podem gerar manutenção divergente no futuro.

## 13. Ordem recomendada para uma futura migração

1. Criar baseline manual determinística e atualizar testes de caracterização da versão atual.
2. Definir a API de tokens e o mapeamento por tema, ainda sem remover estilos legados.
3. Migrar fundamentos globais: canvas, superfícies, texto, bordas e estados básicos de controles.
4. Migrar `icones.py` e a subpaleta duplicada de splash/indicador de tarefa.
5. Migrar controles compartilhados: botões, inputs, tabelas, tabs, scrollbars, badges e progressos.
6. Migrar calendário mensal e semana prevista juntos, unificando a semântica hoje separada entre `main.py` e `tema.py`.
7. Migrar o resolvedor como módulo fechado, com todos os estados de alternativa e editor inline cobertos por baseline.
8. Migrar Modo Foco e pausa, preservando deliberadamente a família vermelha do CTA.
9. Migrar Dashboard por submódulos, começando pelos cards básicos e deixando heroes/gradientes/overrides Futuristas por último.
10. Migrar Estatísticas e widgets desenhados por `QPainter`, definindo antes a estratégia de séries de gráficos.
11. Migrar modais, telas menos frequentes e exceções marcadas `specific.*`.
12. Remover valores legados somente após comparação visual dos três temas e busca global final.

## 14. Conclusão da Etapa 1

O Vighna já possui agrupamentos temáticos e vários blocos semânticos, mas a linguagem visual atual cresceu por camadas. `tema.py` concentra a maior parte das decisões, enquanto `main.py`, splash, tarefas e ícones mantêm subsistemas próprios. O inventário e a taxonomia acima são uma linha de base; nenhum token foi criado e nenhuma cor foi substituída.

**Parar nesta etapa. Não iniciar a Etapa 2 sem autorização.**
