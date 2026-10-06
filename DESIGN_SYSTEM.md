# Design System do VighnaStudy

## Escopo atual

Este documento descreve a fundação criada na Etapa 2 e sua primeira integração de caracterização. Ela permanece desconectada de `tema.py`, `main.py`, `startup_splash.py` e `tarefas_pesadas.py`; `icones.py` consome apenas os tokens `icon.action`, `icon.highlight` e `icon.configuration`, preservando seus valores legados. A cascata dos temas e os demais estilos continuam inalterados.

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
- componente: `answer.*`, `progress.*`, `calendar.*`, `chart.*` e `focus_mode.*`.

`VisualState` padroniza os estados `normal`, `hover`, `pressed`, `selected`, `focused`, `keyboard_focus`, `checked`, `disabled`, `correct`, `incorrect` e `struck`.

Um token semântico descreve uma intenção reaproveitável. Um token de componente só existe quando o vocabulário geral não expressa adequadamente a necessidade do produto. `specific.*` não faz parte do contrato público.

### `themes.py`: temas e resolução

Claro, Escuro e Futurista implementam exatamente o mesmo contrato. Cada `ThemeDefinition` contém:

- referências da camada semântica/de componente para a paleta física;
- variantes de gradiente próprias do tema;
- validação integral do contrato na construção;
- acesso explícito por `color()`, `gradient()` e `resolve()`.

O Futurista possui uma representação completa na nova infraestrutura, sem depender do objeto do tema Escuro. Isso apenas torna a fundação apta a uma separação futura. A cascata legada `Escuro + overrides Futurista` de `tema.py` não foi alterada nem contornada.

Tokens ausentes e acessos com tipo errado geram `TokenNotFoundError`; não existe fallback silencioso.

### `gradients.py`: gradientes estruturados

`GradientSpec` armazena:

- direção por `x1`, `y1`, `x2`, `y2`;
- dois ou mais stops ordenados e únicos;
- posição de cada stop no intervalo de 0 a 1;
- `ColorValue` em cada stop, inclusive alpha por `#AARRGGBB`;
- variante por tema, mantida no respectivo `ThemeDefinition`.

As 201 ocorrências legadas não foram migradas. Foram modelados somente gradientes representativos necessários para validar a arquitetura.

### `adapters.py`: consumidores

Os adaptadores não mantêm estado e não exigem widgets ativos. O pacote `ui.design` não importa PySide6 nem QtAwesome durante sua importação. `PySide6.QtGui` só é carregado quando um adaptador Qt é efetivamente chamado.

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
- `gradient.action_primary` — gradiente semântico de ação.

Não se deve usar nomes de cor (`blue_500`) no contrato semântico, nomes de tela para papéis gerais, nem números de versão no caminho.

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

Não concatene alpha ou altere a cor devolvida no consumidor. Se o papel precisar de uma variante, ela deve existir no contrato.

## Consumo em QPainter

Os adaptadores retornam objetos prontos de `PySide6.QtGui`:

```python
from ui.design import qbrush, qcolor, qlineargradient, qpen

cor = qcolor("escuro", "text.primary")
pincel = qbrush("escuro", "surface.primary")
caneta = qpen("escuro", "border.default", width=1.5)
gradiente = qlineargradient("futurista", "gradient.hero")
```

Essas funções não criam `QApplication` e não importam `QtWidgets`.

## Consumo futuro em QtAwesome

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
