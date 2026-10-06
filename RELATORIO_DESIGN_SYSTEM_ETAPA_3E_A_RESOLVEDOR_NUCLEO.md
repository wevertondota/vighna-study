# Relatório do Design System — Etapa 3E-A1: núcleo do Resolvedor

## 1. Resumo executivo

A Etapa 3E-A foi dividida, por decisão explícita após a revisão do orçamento,
em 3E-A1 e 3E-A2. Esta entrega migra somente o núcleo de alternativas,
indicador, foco de teclado, tachamento, tesoura, estados correta/incorreta,
explicação e corpo do editor inline. As ações do editor, Confirmar/Próxima e o
feedback semântico posterior à resposta permanecem para a 3E-A2.

Não houve mudança intencional de aparência ou comportamento. Os hashes
canônicos completos dos stylesheets Claro, Escuro e Futurista são idênticos à
baseline anterior. `main.py`, banco, schema, versão e build não foram alterados.

O contrato passou de 247 para 264 tokens:

- 102 tokens semânticos, sem alteração;
- 162 tokens de componente, antes 145;
- 50 tokens `answer.*`, antes 33;
- 17 tokens novos, exatamente dentro do orçamento aprovado para a 3E-A1;
- 42 tokens `answer.*` consumidos pelo QSS;
- 8 tokens `answer.*` ainda sem consumo explícito.

## 2. Escopo efetivamente migrado

- alternativa normal e hover;
- alternativa selecionada;
- indicador/radio normal, hover e checked;
- texto da alternativa e texto do radio de Certo/Errado;
- foco por teclado, inclusive sua precedência sobre seleção e tachamento;
- alternativa tachada e hover tachado;
- tesoura normal, hover, checked e disabled;
- alternativa correta, incorreta e gabarito correto revelado;
- gradientes Futuristas de seleção, correta, incorreta e tachamento;
- superfície, borda e texto da explicação;
- título da explicação;
- superfície, borda, texto e seleção do corpo do editor inline.

Os mesmos seletores continuam atendendo alternativas A–E, variações de
quantidade de alternativas e Certo/Errado. Nenhuma ramificação funcional foi
alterada.

## 3. Escopo deliberadamente deixado para 3E-A2

- botão/lápis de edição e seu hover;
- botões Salvar e Cancelar;
- ação Confirmar/Próxima e seu hover;
- superfícies/bordas específicas do feedback `resultState="correta"` e
  `resultState="errada"`;
- título do feedback posterior à confirmação;
- chrome geral da sessão, overview, miniestatísticas, progresso, controles de
  pular/encerrar e painel de ações.

Há 69 ocorrências hexadecimais nos seletores especificamente reservados para a
3E-A2: 36 nas ações do editor, 23 em Confirmar/Próxima e 10 nos estados/título
do feedback. Hardcodes de chrome e declarações legadas sombreadas pela cascata
também permanecem fora desta contagem e não foram tocados.

## 4. Arquivos alterados

- `ui/design/tokens.py`: 17 papéis `answer.*` adicionados;
- `ui/design/palette.py`: 46 cores físicas literais da baseline registradas;
- `ui/design/themes.py`: valores dos três temas, gradientes e correções dos
  tokens provisórios;
- `tema.py`: consumo por `render_qss()` nos blocos autorizados;
- `test_design_system_resolvedor_nucleo.py`: caracterização completa da 3E-A1;
- `test_correcao_real_0_29_54.py`: expectativa antiga de hexadecimal local
  atualizada para token + QSS resolvido;
- `test_design_system_controles_compartilhados.py`: caracterização da 3C
  ajustada porque `answer.*` deixou de estar fora de escopo;
- `DESIGN_SYSTEM.md`: escopo corrente e fronteira `answer.*` documentados;
- este relatório.

Não houve alteração em `main.py`, `banco.py`, `versao.py`, handlers, atalhos ou
persistência.

## 5. Tokens novos e justificativa

| Token | Justificativa |
|---|---|
| `answer.indicator_surface` | Superfície própria do círculo do radio, distinta do card em todos os temas. |
| `answer.indicator_border` | Borda normal própria do indicador. |
| `answer.indicator_hover_border` | Hover do indicador diverge das bordas de hover do card. |
| `answer.indicator_checked_border` | A borda checked diverge do preenchimento em Escuro e Futurista. |
| `answer.indicator_text` | Texto do radio/Certo-Errado difere do texto de alternativa no Claro e Futurista. |
| `answer.struck_hover_surface` | Superfície exclusiva do card tachado em hover. |
| `answer.struck_hover_border` | Borda exclusiva do card tachado em hover. |
| `answer.struck_gradient` | Preserva o gradiente diagonal tachado Futurista e variantes planas dos demais temas. |
| `answer.eliminate_text` | Cor normal específica da tesoura. |
| `answer.eliminate_hover_surface` | Superfície de hover específica da tesoura. |
| `answer.eliminate_hover_text` | Cor de ícone/texto da tesoura em hover. |
| `answer.eliminate_checked_surface` | Superfície da tesoura quando a alternativa está tachada. |
| `answer.eliminate_checked_text` | Cor da tesoura checked. |
| `answer.eliminate_checked_border` | Borda da tesoura checked. |
| `answer.explanation_border` | Borda do contêiner de explicação diverge das bordas gerais. |
| `answer.explanation_title_text` | Título possui hierarquia e valores próprios, especialmente no Futurista. |
| `answer.editor_text` | Texto do editor diverge de `answer.explanation_text` e do texto geral. |

Não foi criada família paralela nem token por seletor. A seleção textual do
editor reutiliza `text.selection_accent` para o foreground e
`answer.editor_selection` para o background.

## 6. Tokens existentes reutilizados

Foram consumidos 26 tokens existentes: 25 da família `answer.*` e o token
semântico `text.selection_accent`.

Principais grupos reutilizados:

- normal/hover: `answer.normal_*` e `answer.hover_*`;
- seleção: `answer.selected_surface`, `answer.selected_border` e
  `answer.selected_gradient`;
- teclado: `answer.keyboard_focus_border`;
- correção: `answer.correct_surface`, `answer.correct_border` e
  `answer.correct_gradient`;
- erro: `answer.incorrect_surface`, `answer.incorrect_border` e
  `answer.incorrect_gradient`;
- tachamento: `answer.struck_surface`, `answer.struck_border` e
  `answer.struck_text`;
- explicação/editor: `answer.explanation_*`, `answer.editor_*` e
  `text.selection_accent`;
- estado disabled da tesoura: `answer.disabled_text`.

## 7. Tokens provisórios corrigidos

Foram recaracterizados 15 caminhos existentes: 13 de cor e dois gradientes.

- `answer.normal_text` e `answer.selected_text`;
- `answer.keyboard_focus_border`;
- `answer.checked_indicator`;
- `answer.disabled_text`;
- `answer.struck_surface`, `answer.struck_border`, `answer.struck_text`;
- `answer.explanation_surface`, `answer.explanation_text`;
- `answer.editor_surface`, `answer.editor_border`, `answer.editor_selection`;
- direção de `answer.correct_gradient`;
- direção de `answer.incorrect_gradient`.

Os valores de foco confirmados foram `#5966D9`, `#8B95FF` e `#4BC9F2` para
Claro, Escuro e Futurista. Os gradientes correta/incorreta passaram a registrar
a direção diagonal real `(0,0) -> (1,1)`; o QSS não foi alterado para se adaptar
ao token.

## 8. Comparação antes/depois

| Papel | Claro | Escuro | Futurista | Resultado |
|---|---|---|---|---|
| alternativa normal | `#FFFFFF / #E0E6ED` | `#151F2C / #2F3D4D` | `#111A27 / #2B3747` | idêntico |
| hover | `#F9FAFC / #BEC9D6` | `#192534 / #4A5A6E` | `#162130 / #46566A` | idêntico |
| selecionada | `#F0F2FF / #7882E8` | `#1D2440 / #747FE9` | gradiente `#1B213A -> #18243A`, borda `#757FFF` | idêntico |
| foco teclado | `#5966D9` | `#8B95FF` | `#4BC9F2` | idêntico |
| indicador checked | `#5965D8 / #5965D8` | `#626DE0 / #A4ABFF` | `#6269E8 / #ADB2FF` | idêntico |
| tachada | `#E7ECF2 / #8796A8` | `#0B121C / #526276` | gradiente `#07101A -> #08121D -> #060D16`, borda `#3E617A` | idêntico |
| correta | `#EEF9F4 / #64B992` | `#173127 / #4EAD80` | gradiente `#153127 -> #12271F`, borda `#4EBA86` | idêntico |
| incorreta | `#FFF1F3 / #E18491` | `#351D24 / #D76676` | gradiente `#351C24 -> #2A171D`, borda `#D96777` | idêntico |
| explicação | `#F8FAFC / #DBE3ED` | `#1F2937 / #334155` | `#171F2B / #3A4656` | idêntico |
| editor | `#FFFFFF / #CBD5E1 / #334155` | `#111827 / #475569 / #E2E8F0` | `#0A1725 / #355F82 / #E7F5FF` | idêntico |

## 9. Gradientes

| Token | Tema | Direção | Stops |
|---|---|---|---|
| `answer.selected_gradient` | Claro | horizontal | `0 #F0F2FF`, `1 #F0F2FF` |
|  | Escuro | horizontal | `0 #1D2440`, `1 #1D2440` |
|  | Futurista | horizontal | `0 #1B213A`, `1 #18243A` |
| `answer.correct_gradient` | Claro | diagonal | `0 #EEF9F4`, `1 #EEF9F4` |
|  | Escuro | diagonal | `0 #173127`, `1 #173127` |
|  | Futurista | diagonal | `0 #153127`, `1 #12271F` |
| `answer.incorrect_gradient` | Claro | diagonal | `0 #FFF1F3`, `1 #FFF1F3` |
|  | Escuro | diagonal | `0 #351D24`, `1 #351D24` |
|  | Futurista | diagonal | `0 #351C24`, `1 #2A171D` |
| `answer.struck_gradient` | Claro | diagonal | `0 #E7ECF2`, `1 #E7ECF2` |
|  | Escuro | diagonal | `0 #0B121C`, `1 #0B121C` |
|  | Futurista | diagonal | `0 #07101A`, `0.55 #08121D`, `1 #060D16` |

Não há mudança de direção, posição, alpha ou cor no QSS entregue.

## 10. Estados e precedência

A ordem de composição não mudou:

1. stylesheet legado do tema;
2. `ESTILO_RESOLVEDOR_*`;
3. camada de eliminadas com alta especificidade;
4. camada de foco por teclado;
5. editor de explicação.

No Futurista permanece `stylesheet_escuro() + overrides Futurista`. A camada de
foco continua posterior à seleção e ao tachamento, portanto o foco visual segue
visível sem modificar seleção, Espaço, Enter ou auto-repeat.

## 11. Hardcodes

- 116 ocorrências hexadecimais foram removidas de `tema.py` nos trechos
  efetivamente migrados;
- 111 marcadores foram introduzidos; a diferença decorre de gradientes, pois um
  marcador substitui múltiplos stops;
- as camadas completas de eliminadas e foco por teclado ficaram sem hexadecimal;
- 69 ocorrências permanecem deliberadamente nos seletores reservados à 3E-A2;
- declarações legadas sombreadas e chrome da sessão permanecem fora do escopo.

Não houve substituição global de hexadecimal.

## 12. Tokens `answer.*` sem consumo

Os oito tokens ainda sem consumidor explícito são:

- `answer.correct_text`;
- `answer.disabled_border`;
- `answer.disabled_surface`;
- `answer.focused_border`;
- `answer.incorrect_text`;
- `answer.pressed_border`;
- `answer.pressed_surface`;
- `answer.selected_text`.

Eles não foram forçados no QSS porque não existe estado legado correspondente
ou porque o texto atualmente herda o estado normal. A consolidação ou remoção
continua adiada.

## 13. Testes e validação

### Infraestrutura e caracterização

- `py_compile` dos arquivos alterados: passou;
- Etapas 2, 3A, 3B, 3C, 3D e 3E-A1: 50/50 passaram;
- testes novos 3E-A1: 8/8 passaram, incluídos nos 50;
- smoke: `VighnaStudy 0.29.59: testes smoke OK`;
- calendário 0.29.59: 10/10 passaram.

### Resolvedor e teclado

Foram executados os testes de interação de alternativas, clique no card,
tesoura, tachamento, setas, Espaço, Enter 1/2/3, bloqueio de auto-repeat,
Certo/Errado, correção, transição, editor inline, salvar, cancelar, bloqueio de
Próxima e janelas operacionais.

- comando bruto: 86 testes, com 14 falhas históricas/preexistentes;
- conjunto aplicável, removendo somente as expectativas históricas: 72/72
  passaram;
- a asserção histórica que exigia `#3E617A` diretamente no fonte foi atualizada
  para exigir o token e o mesmo valor no stylesheet resolvido;
- as demais exceções são expectativas de versões/builds anteriores, schema 22
  e a grafia antiga `Pausa & Desafios`; nenhuma está ligada ao diff desta etapa.

Um teste antigo de layout do Dashboard também continua esperando margem já
substituída antes desta etapa; o teste atual de calendário passou isoladamente.

## 14. Hashes completos de QSS

| Tema | Antes | Depois |
|---|---|---|
| Claro | `139709f8c57e00f16848668f9226703c7f8ff391dd9aea2bba8b2eae20ac2c5f` | mesmo |
| Escuro | `ebbc21363d0035058301d060eb099fb2d33b992e8537c20f9bf1e77f8a2b4f3e` | mesmo |
| Futurista | `0e588bb372946b4a6f61ad406c817fd155cac8c3c4286e9f93b7a09d06dc8622` | mesmo |

A normalização continua restrita a caixa hexadecimal e whitespace. Não foi
relaxada para acomodar a migração.

## 15. Banco, schema, versão e build

- `PRAGMA integrity_check`: `ok`;
- `PRAGMA foreign_key_check`: zero violações;
- SHA-256 do schema SQLite:
  `240e65de128ff81959d6277489c03a5599c7fc404b08d5ace5b79596b00f43a9`,
  idêntico ao registrado na Etapa 3D;
- versão: `0.29.59`, inalterada;
- build: `calendar-week-forecast-v1`, inalterado;
- schema declarado: `25`, inalterado;
- nenhum arquivo de banco ou schema foi modificado.

## 16. Regressões encontradas e corrigidas

Não foi encontrada regressão funcional ou visual. Durante a implementação, a
validação do contrato recusou referências físicas ainda não cadastradas; as
cores literais da baseline foram então registradas na paleta, sem aproximação.

Duas caracterizações de testes foram atualizadas:

- o contador de gradientes da 3C passou de quatro para oito após a integração
  autorizada dos quatro gradientes do Resolvedor;
- o teste de tachamento deixou de exigir hexadecimal no fonte e passou a
  verificar token + QSS resolvido.

## 17. Riscos

- A cascata Futurista ainda depende do stylesheet Escuro e exige testes de hash
  em qualquer alteração futura.
- Há declarações legadas sombreadas no mesmo domínio; removê-las agora alteraria
  o QSS entregue, ainda que o resultado visual aparente fosse igual.
- Oito tokens `answer.*` continuam provisórios/sem consumo.
- A 3E-A2 deverá tratar ações e feedback sem fundir a semântica da alternativa
  com `feedback.*` apenas por igualdade física.
- Não houve captura automatizada de screenshots; a equivalência foi comprovada
  por valores caracterizados, precedência e hashes integrais.

## 18. Recomendação para 3E-A2

Prosseguir em uma entrega separada com orçamento revisado de dez tokens para
lápis, Salvar/Cancelar e Confirmar/Próxima, seguido de uma decisão explícita
sobre os quatro papéis visuais próprios do feedback pós-resposta. Antes de
migrar, recapturar a cascata final e manter os três hashes canônicos completos.

Não iniciar chrome geral, Modo Foco, Dashboard, gráficos, controles avançados
ou consolidação de aliases junto com a 3E-A2.
