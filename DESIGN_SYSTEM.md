# Design System do VighnaStudy

## Escopo atual

Este documento descreve a fundação criada na Etapa 2 e as integrações de caracterização já concluídas. `icones.py` consome `icon.*`; o splash externo, o indicador de tarefas e somente o fallback `JanelaInicializacao` de `main.py` consomem tokens visuais fixos. Em `tema.py`, os controles genéricos compartilhados, o domínio Calendário e o Resolvedor migrado nas Etapas 3E-A1/3E-A2 consomem tokens. O calendário mensal também usa `qcolor()` nos seus `QTextCharFormat`. O chrome geral da sessão permanece legado. A cascata dos temas continua inalterada.

A API central fica em `ui/design/` e possui quatro níveis:

```text
paleta física -> token semântico -> token de componente -> consumidor
   ColorValue     canvas.app        answer.correct_*       QSS
                                                          QPainter
                                                          QtAwesome
```

## Arquitetura

### `palette.py`: paleta física

Contém valores de cor, sem papel visual. `ColorValue` aceita `#RRGGBB`, `#AARRGGBB` no padrão do Qt e `transparent`; normaliza hexadecimais e rejeita formatos inválidos. `PhysicalPalette` é imutável e falha explicitamente quando uma referência não existe.

Os identificadores `hex_...` são propositadamente físicos. Eles evitam atribuir significado a uma cor antes de sabermos onde ela será usada. A paleta desta etapa é um recorte literal e representativo do estado atual, não uma tentativa de cadastrar as 3.310 cores inventariadas.

### `tokens.py`: contrato

`TokenSpec` registra caminho, nível e tipo. Existem dois níveis públicos:

- semântico: `canvas.*`, `surface.*`, `text.*`, `border.*`, `action.*`, `feedback.*`, `focus.*`, `icon.*`, `overlay.*`, `glow.*` e `gradient.*`;
- componente temático: `answer.*`, `progress.*`, `calendar.*`, `chart.*` e `focus_mode.*`;
- componente fixo: `system_status.*`, `startup.*` e `task_indicator.*`.

`VisualState` padroniza os estados `normal`, `hover`, `pressed`, `selected`, `focused`, `keyboard_focus`, `checked`, `disabled`, `correct`, `incorrect` e `struck`.

Um token semântico descreve uma intenção reaproveitável. Um token de componente só existe quando o vocabulário geral não expressa adequadamente a necessidade do produto. `specific.*` não faz parte do contrato público.

### `themes.py`: temas e resolução

Claro, Escuro e Futurista implementam exatamente o mesmo contrato. Cada `ThemeDefinition` contém:

- referências da camada semântica/de componente para a paleta física;
- variantes de gradiente próprias do tema;
- validação integral do contrato na construção;
- acesso explícito por `color()`, `gradient()` e `resolve()`.

O Futurista possui uma representação completa na nova infraestrutura, sem depender do objeto do tema Escuro. Isso apenas torna a fundação apta a uma separação futura. A cascata legada `Escuro + overrides Futurista` de `tema.py` não foi alterada nem contornada.

Os tokens de componente fixo são cadastrados com o mesmo valor nos três contratos e resolvidos por `fixed_color()`/`fixed_gradient()`. A importação valida essa invariância. Assim, splash e indicador não passam a variar com o tema por efeito colateral.

Tokens ausentes e acessos com tipo errado geram `TokenNotFoundError`; não existe fallback silencioso.

### `gradients.py`: gradientes estruturados

`GradientSpec` armazena:

- direção por `x1`, `y1`, `x2`, `y2`;
- dois ou mais stops ordenados e únicos;
- posição de cada stop no intervalo de 0 a 1;
- `ColorValue` em cada stop, inclusive alpha por `#AARRGGBB`;
- variante por tema, mantida no respectivo `ThemeDefinition`.

Das 201 ocorrências inventariadas, foram migrados os dois `QLinearGradient` do splash, quatro gradientes QSS de controles compartilhados e os gradientes de alternativa selecionada, correta, incorreta e tachada do Resolvedor. Os demais gradientes legados continuam inalterados.

Gradientes fixos também podem receber coordenadas dinâmicas no adaptador QPainter. Direção efetiva, stops, posições e alpha permanecem centralizados sem congelar a geometria calculada em runtime.

### `adapters.py`: consumidores

Os adaptadores não mantêm estado e não exigem widgets ativos. O pacote `ui.design` não importa PySide6 nem QtAwesome durante sua importação. `PySide6.QtGui` só é carregado quando um adaptador Qt é efetivamente chamado.

Para componentes deliberadamente independentes do tema existem `fixed_qss_color()`, `fixed_qss_gradient()`, `fixed_qcolor()` e `fixed_qlineargradient()`. Esses adaptadores só aceitam caminhos declarados em `FIXED_TOKEN_PATHS`.

## Contrato e nomenclatura

Os caminhos usam letras minúsculas e `_`, com segmentos separados por ponto:

```text
<família>.<papel>
<componente>.<papel>[_<estado>]
```

Exemplos válidos:

- `canvas.app` — fundo estrutural da aplicação;
- `text.muted` — texto discreto, independentemente da cor física;
- `action.primary_hover` — cor da ação primária em hover;
- `feedback.danger_border` — borda de feedback de erro/perigo;
- `answer.keyboard_focus_border` — borda exclusiva da navegação por teclado;
- `calendar.week_predicted_surface` — superfície da semana prevista;
- `calendar.late_surface` — marcação mensal de revisão atrasada;
- `calendar.forecast_review` — acento de um card de revisão na Semana prevista;
- `gradient.action_primary` — gradiente semântico de ação.
- `system_status.progress_track` — trilho fixo compartilhado por startup e tarefas;
- `startup.shimmer_gradient` — brilho móvel do splash com alpha preservado.

Não se deve usar nomes de cor (`blue_500`) no contrato semântico, nomes de tela para papéis gerais, nem números de versão no caminho.

No domínio `calendar.*`, os papéis mensais (`today_*`, `late_*`,
`scheduled_*`, `selected_*`) permanecem separados dos papéis da Semana
prevista (`forecast_*`). Uma coincidência física entre esses grupos não autoriza
compartilhar o token: os estados têm ciclos de evolução e consumidores distintos.
Papéis realmente comuns à semana, como `week_predicted_*` e `today_border`, são
reutilizados entre seus seletores.

No domínio `answer.*`, a fronteira semântica separa a alternativa do restante
da sessão. A Etapa 3E-A1 caracteriza superfície, borda, texto, indicador,
foco de teclado, tachamento, tesoura, correção, explicação e corpo do editor.
Os tokens `answer.struck_gradient` e `answer.correct_gradient`, por exemplo,
preservam direção e stops próprios; igualdade física com `feedback.*` não
autoriza a consolidação. A Etapa 3E-A2 caracteriza as ações do editor, a ação
primária Confirmar/Próxima e o painel de feedback. Este último consome
`feedback.success_*`/`feedback.danger_*` somente nos papéis de superfície e
borda que foram recaracterizados contra a cascata real; as alternativas
continuam independentes em `answer.correct_*`/`answer.incorrect_*`.

## Consumo em QSS

Para uma propriedade de cor:

```python
from ui.design import qss_color

cor = qss_color("claro", "text.primary")
trecho = f"QLabel {{ color: {cor}; }}"
```

Para um gradiente:

```python
from ui.design import qss_gradient

fundo = qss_gradient("futurista", "gradient.action_primary")
trecho = f"QPushButton {{ background: {fundo}; }}"
```

Para blocos QSS extensos, `render_qss()` evita converter todo o texto em
`f-string` e resolve apenas marcadores explícitos:

```python
from ui.design import render_qss

trecho = render_qss("claro", """
QLineEdit {
    color: {{color:text.control}};
    border: 1px solid {{color:border.default}};
    background: {{gradient:gradient.control_input}};
}
""")
```

Os únicos formatos reconhecidos são `{{color:caminho}}` e
`{{gradient:caminho}}`; tokens ausentes ou do tipo errado continuam falhando
explicitamente.

Não concatene alpha ou altere a cor devolvida no consumidor. Se o papel precisar de uma variante, ela deve existir no contrato.

Para um visual deliberadamente fixo:

```python
from ui.design import fixed_qss_color

cor = fixed_qss_color("system_status.text_primary")
```

## Consumo em QPainter

Os adaptadores retornam objetos prontos de `PySide6.QtGui`:

```python
from ui.design import qbrush, qcolor, qlineargradient, qpen

cor = qcolor("escuro", "text.primary")
pincel = qbrush("escuro", "surface.primary")
caneta = qpen("escuro", "border.default", width=1.5)
gradiente = qlineargradient("futurista", "gradient.hero")
```

Quando a geometria nasce no `paintEvent`, as coordenadas podem ser informadas sem recriar os stops:

```python
from ui.design import fixed_qlineargradient

gradiente = fixed_qlineargradient(
    "startup.progress_gradient",
    coordinates=(esquerda, 0, direita, 0),
)
```

Essas funções não criam `QApplication` e não importam `QtWidgets`.

## Consumo em QtAwesome

`qtawesome_color()` devolve a representação de cor aceita pelo argumento `color=`:

```python
from ui.design import qtawesome_color

cor = qtawesome_color("futurista", "icon.configuration")
# qta.icon("fa5s.cog", color=cor)  # integração reservada para etapa futura
```

`icones.py` usa essa função para resolver `icon.action`, `icon.highlight` e `icon.configuration`. Os nomes dos glifos, tamanhos, lógica QtAwesome e fallback por arquivo continuam sob responsabilidade da camada de ícones; QtAwesome não se torna dependência do núcleo do Design System.

## Como criar um token

Antes de criar um token:

1. Identifique o papel visual em mais de um estado ou tema, usando o inventário e a tela real.
2. Verifique se um token semântico existente já descreve a intenção.
3. Use token de componente somente se a semântica for inseparável do domínio, como resposta correta ou semana prevista.
4. Adicione um `TokenSpec` ao nível e tipo corretos em `tokens.py`.
5. Mapeie o token nos três temas. Não copie automaticamente o valor entre temas.
6. Registre na paleta qualquer valor físico novo já aprovado.
7. Acrescente testes de contrato e do adaptador relevante.
8. Migre o consumidor em uma mudança separada, com comparação visual antes/depois.

Se o componente for comprovadamente fixo, registre o mesmo valor nos três contratos, inclua o caminho em `FIXED_TOKEN_PATHS` e consuma somente pelos adaptadores `fixed_*`. Não use esse mecanismo para evitar uma decisão temática ainda não caracterizada.

## Quando não criar um token

Não crie um token:

- para cada literal ou seletor encontrado no inventário;
- apenas porque duas cores próximas parecem equivalentes;
- para codificar o nome de um widget, arquivo ou versão;
- para expor `specific.*` sem função comprovada;
- para preservar uma duplicidade acidental antes da caracterização visual;
- quando um token existente já representa o mesmo papel e estado;
- quando o valor é dado de conteúdo, e não decisão do sistema visual.

## Como criar posteriormente uma nova paleta

Uma nova paleta deve ser preparada sem alterar caminhos públicos:

1. registre os valores físicos aprovados em `palette.py`;
2. crie uma `ThemeDefinition` completa para o novo tema;
3. mapeie todos os tokens semânticos e de componente por intenção;
4. defina cada variante de gradiente com direção e stops explícitos;
5. execute a validação de contrato e os testes de formatos;
6. compare a baseline visual nas telas críticas antes de conectar consumidores.

Componentes não devem conhecer nomes físicos nem ramificar diretamente por tema. A troca de paleta ocorre no mapeamento do tema.

## Regras contra novos hardcodes

- Código migrado deve consumir um caminho de token, nunca um hexadecimal local.
- QSS gerado deve usar `qss_color()` ou `qss_gradient()`.
- QPainter deve usar `qcolor()`, `qpen()`, `qbrush()` ou `qlineargradient()`.
- QtAwesome deve receber `qtawesome_color()` quando sua migração for autorizada.
- Todo token público precisa existir nos três temas e ter teste de contrato.
- Fallbacks silenciosos são proibidos; token ausente deve falhar no desenvolvimento.
- Migração e mudança estética são trabalhos separados.
- A cascata legada só poderá ser removida após migração completa e baseline aprovada.
