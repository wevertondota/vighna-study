# Relatório do Design System — Etapa 3E-A2: ações e feedback do Resolvedor

## 1. Resumo executivo e escopo migrado

A Etapa 3E-A foi concluída somente no recorte autorizado: lápis de edição da
explicação, Salvar, Cancelar, Confirmar/Próxima e feedback pós-resposta. Não
houve mudança de lógica, aparência, texto, geometria, especificidade ou ordem
dos seletores. `main.py`, `banco.py`, versão, build e schema não foram
alterados.

O contrato passou de 264 para 274 tokens:

- 102 tokens semânticos, quantidade inalterada;
- 172 tokens de componente, antes 162;
- 60 tokens `answer.*`, antes 50;
- 10 tokens novos, todos consumidos e dentro do orçamento máximo de 14;
- 52 tokens `answer.*` consumidos, antes 42;
- os mesmos oito tokens `answer.*` anteriores continuam sem consumo.

Foram removidas as 69 ocorrências hexadecimais da baseline da 3E-A1: 36 das
ações do editor, 23 de Confirmar/Próxima e 10 do feedback. Restam zero no
escopo 3E-A2.

## 2. Caracterização anterior à migração

### 2.1 Precedência final

A cascata caracterizada foi:

1. controles genéricos do stylesheet do tema;
2. regras gerais/legadas da sessão;
3. `ESTILO_RESOLVEDOR_CLARO` ou `ESTILO_RESOLVEDOR_ESCURO`;
4. camadas de alternativas eliminadas e foco de teclado;
5. `ESTILO_RESOLVEDOR_EXPLICACAO_EDITOR_*`;
6. no Futurista, todo `stylesheet_escuro()` primeiro e os overrides Futuristas
   depois, sem remoção ou reorganização.

As regras locais possuem IDs adicionais e vencem os estados genéricos de
`QPushButton`. Salvar e Cancelar não tinham seletores locais de hover, pressed
ou disabled. O lápis tinha apenas normal e hover. A ação primária tinha apenas
normal e hover. Portanto, fora do hover, pressed/disabled preservavam as
declarações normais locais; durante pressão com o ponteiro dentro do botão,
`:hover` também casa e continua sendo o estado visual entregue.

No Futurista há uma precedência histórica importante: o seletor posterior
`QDialog#questionSolverDialog QFrame#questionSolverFeedback` possui dois IDs e
vence os seletores herdados `QFrame#questionSolverFeedback[resultState=...]`.
Assim, correta e errada terminam com a mesma superfície/borda neutra nesse
tema. Essa precedência foi preservada, não “corrigida”.

### 2.2 Lápis

Todos os valores são opacos; não há alpha nem gradiente.

| Tema | Normal: superfície / texto / borda | Hover: superfície / texto / borda | Pressed | Disabled |
|---|---|---|---|---|
| Claro | `#FFFFFF / #475569 / #CBD5E1` | `#EEF2FF / #4338CA / #A5B4FC` | sem seletor; normal, ou hover sob ponteiro | sem seletor; normal |
| Escuro | `#182235 / #CBD5E1 / #475569` | `#273449 / #FFFFFF / #8B95FF` | sem seletor; normal, ou hover sob ponteiro | sem seletor; normal |
| Futurista | `#0D1D2D / #B6D9E8 / #355F82` | `#15324A / #F2FBFF / #4BC9F2` | sem seletor; normal, ou hover sob ponteiro | sem seletor; normal |

### 2.3 Salvar

| Tema | Normal: superfície / texto / borda | Hover | Pressed | Disabled |
|---|---|---|---|---|
| Claro | `#4F46E5 / #FFFFFF / #4338CA` | igual ao normal | igual ao normal | igual ao normal |
| Escuro | `#6366F1 / #FFFFFF / #818CF8` | igual ao normal | igual ao normal | igual ao normal |
| Futurista | `#19527A / #F1FAFF / #4BC9F2` | igual ao normal | igual ao normal | igual ao normal |

### 2.4 Cancelar

| Tema | Normal: superfície / texto / borda | Hover | Pressed | Disabled |
|---|---|---|---|---|
| Claro | `#FFFFFF / #475569 / #CBD5E1` | igual ao normal | igual ao normal | igual ao normal |
| Escuro | `#1F2937 / #CBD5E1 / #475569` | igual ao normal | igual ao normal | igual ao normal |
| Futurista | `#0D1D2D / #B6D9E8 / #355F82` | igual ao normal | igual ao normal | igual ao normal |

### 2.5 Confirmar e Próxima

Os dois botões usam o mesmo `objectName="primaryButton"`; a troca de widget e
texto não muda a cascata visual.

| Tema | Normal: gradiente / texto / borda | Hover: gradiente / borda | Pressed | Disabled |
|---|---|---|---|---|
| Claro | `#4B50DF -> #586DE3 / #FFFFFF / #7885F0` | `#595EE8 -> #6579EC / #98A2F7` | sem seletor local; normal, ou hover sob ponteiro | sem seletor local; normal |
| Escuro | `#4B50DF -> #586DE3 / #FFFFFF / #7885F0` | `#595EE8 -> #6579EC / #A2AAFF` | sem seletor local; normal, ou hover sob ponteiro | sem seletor local; normal |
| Futurista | `#4447E8 -> #4347E1 -> #3C42D2 / #FFFFFF / #7C83FF` | `#5355F2 -> #4F54EB -> #464DDE / #B1B7FF` | sem seletor local; normal, ou hover sob ponteiro | sem seletor local; normal |

### 2.6 Feedback correto e errado

“Texto/acento” abaixo é o texto da explicação, já migrado na 3E-A1. O título
foi migrado nesta etapa. Todos os valores são opacos e planos.

| Tema | Correto: superfície / borda | Errado: superfície / borda | Título | Texto/acento |
|---|---|---|---|---|
| Claro | `#F0FDF4 / #86EFAC` | `#FEF2F2 / #FCA5A5` | `#111827` | `#475569` |
| Escuro | `#163523 / #22C55E` | `#3F1218 / #EF4444` | `#F8FAFC` | `#CBD5E1` |
| Futurista | `#171F2B / #3A4656` | `#171F2B / #3A4656` | `#F8FAFC` | `#CBD5E1` |

Os valores Futuristas são a cascata final, não os estados Escuros herdados e
sombreados.

## 3. Tokens existentes reutilizados

Foram reutilizados dez caminhos existentes no escopo novo:

- `gradient.action_primary` e `gradient.action_primary_hover`;
- `text.on_action` e `text.on_feedback`;
- `icon.default`;
- `answer.editor_border`;
- `feedback.success_surface`, `feedback.success_border`;
- `feedback.danger_surface`, `feedback.danger_border`.

`answer.editor_border` foi reutilizado somente porque a equivalência visual e
de domínio foi confirmada nos três temas: a borda das ações secundárias do
editor é a mesma borda do editor inline. `icon.default` expressa corretamente
o lápis e os textos das ações secundárias.

## 4. `feedback.*` efetivamente utilizados

Quatro tokens ganharam consumidor:

- `feedback.success_surface`;
- `feedback.success_border`;
- `feedback.danger_surface`;
- `feedback.danger_border`.

Os quatro foram separados dos valores físicos usados por `answer.correct_*` e
`answer.incorrect_*`. A igualdade anterior era apenas provisória. No Claro e
Escuro, o painel possui valores próprios; no Futurista, o override neutro
posterior define a cascata final.

`feedback.success_text` e `feedback.danger_text` não foram forçados: o título
é comum aos dois resultados e corresponde semanticamente a `text.on_feedback`.

## 5. `answer.*` utilizados

Dez novos `answer.*` ganharam consumidor:

- `answer.edit_action_surface`;
- `answer.edit_action_hover_surface`;
- `answer.edit_action_hover_text`;
- `answer.edit_action_hover_border`;
- `answer.save_action_surface`;
- `answer.save_action_text`;
- `answer.save_action_border`;
- `answer.cancel_action_surface`;
- `answer.primary_action_border`;
- `answer.primary_action_hover_border`.

Além deles, `answer.editor_border` foi reutilizado. Nenhum dos oito tokens
`answer.*` anteriormente sem uso passou a ser consumido.

## 6. Tokens novos e justificativa individual

| Token | Justificativa |
|---|---|
| `answer.edit_action_surface` | A superfície normal do lápis não coincide com token geral nos três temas. |
| `answer.edit_action_hover_surface` | Hover próprio do lápis, diferente de `action.ghost_hover` e de superfícies gerais. |
| `answer.edit_action_hover_text` | Acento de hover próprio, inclusive `#4338CA` no Claro e `#F2FBFF` no Futurista. |
| `answer.edit_action_hover_border` | Borda de hover própria nos três temas. |
| `answer.save_action_surface` | Salvar possui superfícies diferentes da ação primária geral nos três temas. |
| `answer.save_action_text` | O Futurista usa `#F1FAFF`, portanto `text.on_action` não é equivalente. |
| `answer.save_action_border` | Borda própria de Salvar em cada tema. |
| `answer.cancel_action_surface` | O Futurista diverge de `action.secondary`; não houve equivalência tripla. |
| `answer.primary_action_border` | Borda normal de Confirmar/Próxima não possui papel global equivalente. |
| `answer.primary_action_hover_border` | Borda hover varia de modo próprio por tema. |

Não foram criados tokens para estados que não existiam na cascata real.

## 7. Tokens provisórios corrigidos

Cinco caminhos existentes foram recaracterizados sem afetar consumidores
migrados:

- `feedback.success_surface`;
- `feedback.success_border`;
- `feedback.danger_surface`;
- `feedback.danger_border`;
- `text.on_feedback`.

Os quatro `feedback.*` deixaram de derivar dos mesmos valores físicos de
`answer.*`. `text.on_feedback` passou a reproduzir o título real do painel:
`#111827`, `#F8FAFC`, `#F8FAFC`.

## 8. Hardcodes antes e depois

| Grupo | Antes | Depois | Removidos |
|---|---:|---:|---:|
| lápis, Salvar e Cancelar | 36 | 0 | 36 |
| Confirmar/Próxima | 23 | 0 | 23 |
| feedback/título | 10 | 0 | 10 |
| **Total 3E-A2** | **69** | **0** | **69** |

Fora do escopo, os três blocos modernos `ESTILO_RESOLVEDOR_*` ainda contêm
133 ocorrências (`39/39/55`) ligadas a chrome, overview, miniestatísticas,
progresso, pular, encerrar, painel geral e outras áreas não autorizadas. Uma
varredura ampla de todos os seletores legados `questionSolver*` e
`questionSession*`, incluindo duplicidades sombreadas e resumo da sessão,
encontra 316 ocorrências. Nenhuma foi tocada nesta etapa.

## 9. Valores antes/depois

Cada marcador novo resolve exatamente para os valores das tabelas de
caracterização. O QSS canônico entregue antes e depois é idêntico. Não houve
aproximação, conversão de alpha ou alteração de caixa relevante à
normalização.

## 10. Gradientes

| Token | Tema | Direção | Stops | Alpha |
|---|---|---|---|---|
| `gradient.action_primary` | Claro/Escuro | `(0,0) -> (1,0)` | `0 #4B50DF`, `1 #586DE3` | opaco |
|  | Futurista | `(0,0) -> (1,0)` | `0 #4447E8`, `0.52 #4347E1`, `1 #3C42D2` | opaco |
| `gradient.action_primary_hover` | Claro/Escuro | `(0,0) -> (1,0)` | `0 #595EE8`, `1 #6579EC` | opaco |
|  | Futurista | `(0,0) -> (1,0)` | `0 #5355F2`, `0.52 #4F54EB`, `1 #464DDE` | opaco |

Direção, posições, quantidade de stops, cores e alpha são idênticos à linha de
base. A equivalência foi confirmada antes da conexão.

## 11. Hashes completos de QSS

A normalização permaneceu limitada a caixa hexadecimal e whitespace.

| Tema | Antes | Depois |
|---|---|---|
| Claro | `139709f8c57e00f16848668f9226703c7f8ff391dd9aea2bba8b2eae20ac2c5f` | mesmo |
| Escuro | `ebbc21363d0035058301d060eb099fb2d33b992e8537c20f9bf1e77f8a2b4f3e` | mesmo |
| Futurista | `0e588bb372946b4a6f61ad406c817fd155cac8c3c4286e9f93b7a09d06dc8622` | mesmo |

## 12. Testes

- `py_compile`: passou;
- Etapas 2, 3A, 3B, 3C, 3D, 3E-A1 e 3E-A2: 59/59 passaram;
- testes novos 3E-A2: 9/9 passaram, incluídos nos 59;
- smoke: passou;
- Certo/Errado funcional: passou;
- conjunto de Resolvedor, alternativas, tesoura, teclado, Enter 1/2/3,
  auto-repeat, correta/incorreta, editor, salvar, cancelar, bloqueio de Próxima,
  Confirmar, Próxima e conclusão: 57/57 expectativas aplicáveis passaram;
- o comando bruto desse conjunto teve 68 testes e 11 falhas exclusivamente de
  expectativas históricas de versão/build/schema, separadas do resultado.

## 13. Banco, schema, versão e build

- `PRAGMA integrity_check`: `ok`;
- `PRAGMA foreign_key_check`: zero violações;
- SHA-256 do schema SQLite:
  `240e65de128ff81959d6277489c03a5599c7fc404b08d5ace5b79596b00f43a9`;
- versão: `0.29.59`;
- build: `calendar-week-forecast-v1`;
- schema declarado: `25`;
- `main.py`, `banco.py`, `versao.py` e bancos não foram alterados.

## 14. Regressões encontradas

Não foi encontrada regressão funcional ou visual. Uma expectativa da Etapa 3C
contava oito marcadores de gradiente; ela foi atualizada para 14 porque esta
etapa adiciona seis consumidores autorizados (normal/hover nos três blocos do
Resolvedor). A linha de base de QSS permaneceu idêntica.

A caracterização também tornou explícito o override neutro do feedback
Futurista. Ele já existia e foi preservado.

## 15. Métricas consolidadas

- contrato antes: 264;
- contrato depois: 274;
- tokens novos: 10;
- tokens existentes reutilizados no novo escopo: 10;
- tokens provisórios corrigidos: 5;
- `feedback.*` que ganharam consumidor: 4;
- `answer.*` que ganharam consumidor: 10 novos; nenhum dos oito provisórios;
- hardcodes removidos: 69;
- hardcodes remanescentes no escopo 3E-A2: 0;
- hardcodes nos três blocos modernos do Resolvedor fora do escopo: 133;
- tokens `answer.*` consumidos: 52 de 60;
- hashes antes/depois: idênticos nos três temas.

## 16. Recomendação para 3E-B

Manter a 3E-B separada e recaracterizar apenas o próximo recorte autorizado.
Não aproveitar a próxima etapa para remover declarações sombreadas, consolidar
aliases ou migrar o chrome geral. A precedência Futurista e os oito tokens
`answer.*` sem consumo devem continuar explícitos até haver um caso real.
