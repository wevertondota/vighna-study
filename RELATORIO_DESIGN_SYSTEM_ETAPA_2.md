# Relatório — Design System Vighna — Etapa 2

## Resultado

Foi criada uma fundação central, tipada e isolada para o futuro Design System. Nenhum componente foi migrado e nenhum consumidor legado foi conectado. Os estilos atuais continuam sendo fornecidos por `tema.py` e pelos hardcodes já existentes.

Versão observada e preservada: VighnaStudy `0.29.59`, build `calendar-week-forecast-v1`, schema `25`.

## Entradas utilizadas

Foram lidos integralmente:

- `AGENTS.md`;
- `RELATORIO_INVENTARIO_VISUAL_DESIGN_SYSTEM.md`;
- as 7.185 linhas de dados de `INVENTARIO_VISUAL_DESIGN_SYSTEM.csv`.

O CSV foi validado como um todo, com 12 colunas e digest lógico SHA-256 `4b697ce98d7235c6e23d27ac206f54c1b1fb001c393175f0fbd9b8437a3fa90e`. A arquitetura foi orientada pelos papéis e hotspots encontrados, não por consolidação automática das 3.310 cores distintas.

## Arquivos criados

```text
ui/__init__.py
ui/design/__init__.py
ui/design/palette.py
ui/design/tokens.py
ui/design/gradients.py
ui/design/themes.py
ui/design/adapters.py
test_design_system.py
DESIGN_SYSTEM.md
RELATORIO_DESIGN_SYSTEM_ETAPA_2.md
```

Nenhum arquivo funcional legado foi editado.

## Decisões arquitetônicas

### Quatro níveis

1. **Paleta física:** `ColorValue` e `PhysicalPalette`, com valores literais validados e imutáveis.
2. **Tokens semânticos:** contrato independente de cor para canvas, superfícies, texto, bordas, ações, feedback, foco, ícones, overlays, glow e gradientes.
3. **Tokens de componente:** somente para respostas, progresso, calendário, gráficos e Modo Foco.
4. **Adaptadores:** saídas para QSS, QColor, QBrush, QPen, QLinearGradient e QtAwesome.

### Imutabilidade e falha explícita

Paletas e definições de tema usam mapas imutáveis. Um token inexistente, uma referência física ausente ou o uso de cor como gradiente falha explicitamente. Não há fallback visual silencioso.

### Qt desacoplado

Importar `ui.design` não importa PySide6, QtWidgets, QtAwesome, `tema.py`, `main.py` nem `icones.py`. Os adaptadores QPainter usam importação tardia de `PySide6.QtGui` e funcionam sem `QApplication`.

### Futurista representável de forma independente

O novo `FUTURISTIC_THEME` cumpre sozinho o mesmo contrato dos demais temas. Isso prepara uma separação futura, mas não altera o mecanismo atual: `tema.py` continua compondo Futurista sobre Escuro com seus overrides legados.

### Sem criação de nova estética

Os valores da fundação são amostras literais já encontradas na interface atual, especialmente no resolvedor e no Modo Foco. Eles validam o contrato; não constituem paleta estética nova nem alegam cobrir todas as variações históricas.

## Tokens definidos

### Semânticos: 77

- 72 tokens de cor;
- 5 tokens de gradiente;
- famílias: `canvas`, `surface`, `text`, `border`, `action`, `feedback`, `focus`, `icon`, `overlay`, `glow` e `gradient`.

### De componente: 71

- 65 tokens de cor;
- 6 tokens de gradiente;
- famílias: `answer`, `progress`, `calendar`, `chart` e `focus_mode`.

Total do contrato: **148 tokens**. O tamanho é intencionalmente muito menor que o número de literais inventariados. `specific.*` permaneceu fora da API pública.

### Estados suportados

`normal`, `hover`, `pressed`, `selected`, `focused`, `keyboard_focus`, `checked`, `disabled`, `correct`, `incorrect` e `struck` são enumerados na API. Os estados específicos de resposta possuem papéis próprios quando o inventário demonstrou necessidade.

## Arquitetura de gradientes

Cada `GradientSpec` é imutável e contém:

- `GradientDirection(x1, y1, x2, y2)`;
- sequência de `GradientStop(position, ColorValue)`;
- validação de extensão da direção;
- mínimo de dois stops;
- posições únicas, ordenadas e no intervalo `[0, 1]`;
- suporte a alpha pelo formato Qt `#AARRGGBB`;
- variantes armazenadas separadamente em Claro, Escuro e Futurista.

O adaptador QSS produz `qlineargradient(...)`; o adaptador QPainter produz `QLinearGradient`. As 201 ocorrências do inventário não foram migradas.

## Testes criados

`test_design_system.py` cobre:

1. contrato idêntico nos três temas;
2. ausência de tokens obrigatórios faltantes;
3. formatos de cores e referências físicas;
4. stops e variantes de gradientes;
5. saídas QSS e QtAwesome;
6. QColor, QBrush, QPen e QLinearGradient sem QApplication;
7. falhas explícitas para token ausente ou tipo errado;
8. importação sem PySide6, código legado ou QtAwesome;
9. presença de todos os estados exigidos.

Na linha de base, `py_compile` dos hotspots funcionais passou. O módulo histórico `test_dashboard_futurista_neo_0_29_34.py` continua contendo duas asserções obsoletas: versão `0.29.34` e presença de `#06131D`. Conforme a regra da tarefa, nenhuma delas foi usada para reintroduzir a cor ou reduzir a versão atual.

## Validação final

- `py_compile`: pacote novo, teste novo e hotspots `tema.py`, `main.py`, `startup_splash.py`, `icones.py` e `tarefas_pesadas.py` — passou.
- `unittest`: Design System, integração QtAwesome e calendário semanal 0.29.59 — 24 testes, todos passaram.
- `unittest`: núcleo de estatísticas e integridade de dados — 32 testes, todos passaram.
- `testes_smoke.py`: `VighnaStudy 0.29.59: testes smoke OK`.
- Total explícito de testes unitários nesta validação: 56, além da suíte smoke.

A auditoria do worktree confirmou que `tema.py`, `main.py`, `startup_splash.py`, `tarefas_pesadas.py`, `icones.py`, `banco.py` e `versao.py` permanecem idênticos ao `HEAD`. Versão `0.29.59`, build `calendar-week-forecast-v1` e schema `25` foram preservados. Não houve substituição de cor, gradiente ou estilo existente.

## Riscos

- A grande quantidade de variações contextuais em `tema.py` ainda exige caracterização por tela antes de mapear um literal para um token.
- Cores fisicamente iguais podem representar papéis distintos; o contrato não autoriza consolidação automática.
- Cores próximas podem ser variações intencionais ou acidentes históricos; a decisão depende de baseline visual.
- A cascata Futurista sobre Escuro segue ativa no legado e deve ser preservada até uma migração completa e comparada.
- Gradientes repetidos ou quase repetidos ainda não foram consolidados.
- `main.py`, `startup_splash.py`, `tarefas_pesadas.py` e `icones.py` ainda contêm decisões visuais locais.
- Tokens iniciais de `chart.*` e alguns papéis de calendário precisarão ser confirmados contra todos os gráficos e estados reais durante a migração.

## Deliberadamente deixado para a Etapa 3

- Conectar `tema.py` ao novo pacote.
- Substituir qualquer hexadecimal, rgba, QColor, QBrush, QPen ou gradiente legado.
- Migrar QSS ou componentes.
- Migrar `icones.py` para `icon.*`.
- Alterar a cascata do Futurista.
- Consolidar os 201 gradientes inventariados.
- Resolver valores classificados como `specific.*`/a revisar.
- Criar nova paleta estética.
- Remover duplicidades ou hardcodes existentes.
- Incrementar versão, build ou schema.

## Critério para a próxima etapa

A migração só deve começar com autorização nova, por módulo, usando a checklist visual da Etapa 1 e comparação antes/depois nos três temas. Mudanças de infraestrutura, migração e eventual redesign devem continuar separadas.
