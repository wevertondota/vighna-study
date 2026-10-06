# Design System Vighna — Etapa 3E-B2a

## Migração da estrutura e leitura do chrome do Resolvedor

Data: 06/10/2026
Commit de partida: `398321e` (`docs(theme): audita chrome do resolvedor`)

## 1. Resumo executivo

A estrutura e a leitura da sessão ativa do Resolvedor foram conectadas ao
Design System sem alteração visual ou comportamental. O recorte contém fundo,
cabeçalho, overview, contador/ciclo, progresso, miniestatísticas e contexto da
questão. Ações, flags, Modo Foco, enunciado e resumo final permaneceram fora.

O contrato passou de 274 para 293 tokens:

- 102 semânticos, sem alteração;
- 191 de componente, antes 172;
- 19 tokens novos, exatamente o orçamento revisado;
- um token existente reutilizado: `canvas.app`;
- um token existente recaracterizado: `progress.fill_gradient`;
- 66 hardcodes removidos do recorte, com zero remanescente nele;
- os hashes completos de Claro, Escuro e Futurista permaneceram idênticos.

`main.py`, comportamento, layout, banco, schema, versão e build não foram
alterados.

## 2. Caracterização anterior à migração

A baseline foi capturada programaticamente antes da substituição. Os três
blocos modernos continham `39/39/55` hexadecimais. O recorte autorizado
correspondia a `21/21/24`, totalizando 66 ocorrências.

| Papel | Claro | Escuro | Futurista |
|---|---|---|---|
| janela | `#F5F7FA` | `#101722` | `#0B111D` |
| título | `#172033` | `#F3F6FA` | `#F5F7FB` |
| subtítulo | `#718096` | `#96A3B3` | `#AAB5C2` |
| overview: superfície | `#FFFFFF` | `#182230` | gradiente da seção 8 |
| overview: borda | `#DDE4EC` | `#344154` | `#475364` |
| eyebrow | `#7B8797` | `#8392A5` | `#AAB4C0` |
| contador | `#202B3C` | `#EDF2F7` | `#F5F7FB` |
| ciclo | `#657286` | `#A1ADBB` | `#B8C1CD` |
| trilho | `#E8EDF3` | `#2C3745` | `#3B424F` |
| miniestatística: superfície | `#F7F9FC` | `#141D29` | `#171F2B` |
| miniestatística: borda | `#E3E8EF` | `#2D3949` | `#344050` |
| rótulo | `#7A8798` | `#8D9BAD` | `#98A5B4` |
| valor neutro | `#1F2937` | `#F2F5F8` | `#F8FAFC` |
| acertos | `#17815D` | `#79D6AA` | `#82DBB4` |
| erros | `#C44758` | `#F08A98` | `#F28B99` |
| puladas | `#B16A18` | `#E5B16B` | `#E9B66E` |
| disciplina | `#5866C8` | `#96A0FF` | `#969FFF` |
| tópico/metadado | `#5D697A` | `#A8B4C2` | `#B6C0CB` |
| índice | `#606BC9` | `#9BA4FF` | `#9BA4FF` |

Não existe estado “Pendentes”: as quatro miniestatísticas reais permanecem
neutro/Respondidas, success/Acertos, danger/Erros e warning/Puladas.

## 3. Cascata preservada

Nenhum seletor foi movido, reagrupado ou teve sua especificidade alterada.

- Claro: stylesheet base, `ESTILO_RESOLVEDOR_CLARO` e camadas posteriores;
- Escuro: stylesheet base, `ESTILO_RESOLVEDOR_ESCURO` e camadas posteriores;
- Futurista: `stylesheet_escuro()` completo, overrides Futuristas,
  `ESTILO_RESOLVEDOR_FUTURISTA` e demais camadas posteriores.

Declarações legadas sombreadas não foram removidas. A herança Futurista
continua explícita em `stylesheet_futurista()`.

## 4. Escopo efetivamente migrado

- fundo de `QDialog#questionSolverDialog`;
- `pageTitle` e `pageSubtitle`;
- superfície, borda e gradiente do `questionSessionOverviewCard`;
- `questionSessionEyebrow`;
- contador `questionSessionProgressText`;
- texto `questionSessionCycleText`;
- trilho e preenchimento de `questionSessionProgress`;
- superfície, borda, label, valor neutro e três acentos das miniestatísticas;
- disciplina, tópico/metadados e índice da questão.

Não foram tocados Dashboard/retorno, cronômetro, Pular, Encerrar, painel
inferior, Dúvida, Análise, checkboxes, Confirmar/Próxima, feedback,
alternativas, enunciado, Modo Foco, configuração pré-sessão ou resumo final.

## 5. Token existente reutilizado

`canvas.app` foi conectado ao fundo da janela depois de reconfirmada a
equivalência exata nos três temas:

- Claro `#F5F7FA`;
- Escuro `#101722`;
- Futurista `#0B111D`.

`focus_mode.canvas` não foi usado, apesar da coincidência física, porque sua
semântica pertence a outro domínio.

## 6. Tokens novos e justificativa individual

| Token | Consumidor | Justificativa |
|---|---|---|
| `session.title_text` | título | Hierarquia e triple próprios; nenhum `text.*` coincide. |
| `session.subtitle_text` | subtítulo | Valores finais diferentes de `text.muted`. |
| `session.panel_surface` | overview Claro/Escuro | Superfície coordenada da sessão; `surface.*` diverge no Escuro. |
| `session.overview_border` | borda do overview | Nenhum `border.*` reproduz os três temas. |
| `session.overview_gradient` | overview Futurista | Gradiente diagonal próprio, sem equivalente global. |
| `session.eyebrow_text` | “PROGRESSO DA SESSÃO” | Papel hierárquico e valores próprios. |
| `progress.session_text` | contador | `progress.text` já possui outro consumidor e diverge. |
| `session.cycle_text` | texto de ciclo | Papel contextual próprio da sessão. |
| `progress.session_track` | trilho | Só o Claro coincide com `progress.track`; não há equivalência tripla. |
| `session.metric_surface` | miniestatística | Superfície própria do cartão métrico. |
| `session.metric_border` | miniestatística | Borda própria nos três temas. |
| `session.metric_label_text` | rótulo métrico | Hierarquia e valores próprios. |
| `session.metric_value_text` | valor neutro | `text.primary` coincide somente no Claro. |
| `session.metric_success_text` | Acertos | `feedback.success_text` possui outros valores e outra fronteira. |
| `session.metric_danger_text` | Erros | `feedback.danger_text` não reproduz a cascata real. |
| `session.metric_warning_text` | Puladas | `feedback.warning_text` não reproduz a cascata real. |
| `session.discipline_text` | disciplina | Acento contextual sem equivalente triplo. |
| `session.meta_text` | tópico/metadados | Texto contextual diferente dos papéis gerais. |
| `session.question_index_text` | índice | Acento próprio do índice da questão. |

A família `session.*` é de componente porque coordena uma sessão de questões e
não descreve uma intenção global. Não foi criada família `solver.*`.

## 7. Valores dos tokens novos

| Token | Claro | Escuro | Futurista |
|---|---|---|---|
| `session.title_text` | `#172033` | `#F3F6FA` | `#F5F7FB` |
| `session.subtitle_text` | `#718096` | `#96A3B3` | `#AAB5C2` |
| `session.panel_surface` | `#FFFFFF` | `#182230` | `#202733`* |
| `session.overview_border` | `#DDE4EC` | `#344154` | `#475364` |
| `session.eyebrow_text` | `#7B8797` | `#8392A5` | `#AAB4C0` |
| `progress.session_text` | `#202B3C` | `#EDF2F7` | `#F5F7FB` |
| `session.cycle_text` | `#657286` | `#A1ADBB` | `#B8C1CD` |
| `progress.session_track` | `#E8EDF3` | `#2C3745` | `#3B424F` |
| `session.metric_surface` | `#F7F9FC` | `#141D29` | `#171F2B` |
| `session.metric_border` | `#E3E8EF` | `#2D3949` | `#344050` |
| `session.metric_label_text` | `#7A8798` | `#8D9BAD` | `#98A5B4` |
| `session.metric_value_text` | `#1F2937` | `#F2F5F8` | `#F8FAFC` |
| `session.metric_success_text` | `#17815D` | `#79D6AA` | `#82DBB4` |
| `session.metric_danger_text` | `#C44758` | `#F08A98` | `#F28B99` |
| `session.metric_warning_text` | `#B16A18` | `#E5B16B` | `#E9B66E` |
| `session.discipline_text` | `#5866C8` | `#96A0FF` | `#969FFF` |
| `session.meta_text` | `#5D697A` | `#A8B4C2` | `#B6C0CB` |
| `session.question_index_text` | `#606BC9` | `#9BA4FF` | `#9BA4FF` |

\* No Futurista, `session.panel_surface` é a variante plana contratual e usa o
primeiro stop do overview. O QSS real não a consome nesse tema: consome
`session.overview_gradient`. Claro e Escuro continuam entregando
`background-color`, sem conversão para gradiente.

Foram registrados 53 valores físicos literais ainda ausentes na paleta. Eles
não são tokens e não alteram o orçamento público.

## 8. Gradientes

### `progress.fill_gradient`

O token não possuía consumidor e duplicava provisoriamente o gradiente de ação.
Uma busca em `tema.py`, `main.py`, `ui/` e testes confirmou zero consumidores
antes da alteração. Ele foi recaracterizado para o progresso real:

| Tema | Antes | Depois |
|---|---|---|
| Claro | horizontal `#4B50DF → #586DE3` | horizontal `0 #4F5FE8; 1 #6B86F2` |
| Escuro | horizontal `#4B50DF → #586DE3` | horizontal `0 #5964E8; 1 #6E8BEF` |
| Futurista | horizontal `0 #4447E8; .52 #4347E1; 1 #3C42D2` | horizontal `0 #5358EA; .52 #5B64EE; 1 #718BF5` |

Após a migração, possui três consumidores, um em cada bloco moderno. Não foi
criado `progress.session_gradient`. `progress.track`, `progress.fill`,
`progress.text` e `progress.border` não foram alterados.

### `session.overview_gradient`

| Tema | Direção | Stops | Consumo no QSS |
|---|---|---|---|
| Claro | diagonal `(0,0) → (1,1)` | `0 #FFFFFF; 1 #FFFFFF` | não; mantém superfície plana |
| Escuro | diagonal `(0,0) → (1,1)` | `0 #182230; 1 #182230` | não; mantém superfície plana |
| Futurista | diagonal `(0,0) → (1,1)` | `0 #202733; .55 #222A36; 1 #1D2430` | sim |

Todos os stops são opacos. Direção, posições e cores entregues pelo QSS são
idênticas à baseline. `gradient.surface_elevated` não foi reutilizado.

Foram migrados dois papéis de gradiente em quatro ocorrências de QSS: três de
progresso e uma do overview Futurista.

## 9. Hardcodes antes e depois

| Grupo | Antes | Depois | Removidos |
|---|---:|---:|---:|
| Claro — estrutura/leitura | 21 | 0 | 21 |
| Escuro — estrutura/leitura | 21 | 0 | 21 |
| Futurista — estrutura/leitura | 24 | 0 | 24 |
| **Total B2a** | **66** | **0** | **66** |

Métricas ampliadas:

- três blocos modernos antes: 133 (`39/39/55`);
- três blocos modernos depois: 67 (`18/18/31`);
- dos 67 restantes, 48 pertencem ao chrome futuro e 19 a Modo Foco/enunciado;
- chrome ativo antes da B2a: 167 hardcodes;
- chrome ativo remanescente: **101** (`48` modernos + `32` checkboxes legados
  ativos + `21` seletores genéricos de navegação/cronômetro);
- nenhuma declaração legada sombreada foi tocada.

## 10. Hashes completos de QSS

A normalização foi mantida estritamente em caixa hexadecimal e whitespace.

| Tema | Antes | Depois |
|---|---|---|
| Claro | `139709f8c57e00f16848668f9226703c7f8ff391dd9aea2bba8b2eae20ac2c5f` | mesmo |
| Escuro | `ebbc21363d0035058301d060eb099fb2d33b992e8537c20f9bf1e77f8a2b4f3e` | mesmo |
| Futurista | `0e588bb372946b4a6f61ad406c817fd155cac8c3c4286e9f93b7a09d06dc8622` | mesmo |

Nenhum marcador `{{color:...}}` ou `{{gradient:...}}` permanece no stylesheet
entregue em runtime.

## 11. Testes

- `py_compile`: passou;
- Design System, 3A, 3B, 3C, 3D, 3E-A1, 3E-A2 e 3E-B2a: 67/67 passaram;
- testes novos 3E-B2a: 8/8, incluídos nos 67;
- smoke: `VighnaStudy 0.29.59: testes smoke OK`;
- ciclo persistente, Banco de Erros e janelas operacionais/simulado: 50
  executados; 49 passaram e uma falha foi somente a expectativa histórica
  `0.29.45 / janelas-operacionais-independentes-v1`;
- suíte principal do Resolvedor: 59 executados, 49 passaram e dez falhas de
  linha de base; o recorte aplicável foi reexecutado em separado e passou
  49/49;
- as dez falhas de linha de base são nove expectativas históricas de
  versão/build/schema e a expectativa textual antiga `retorno de questão
  pulada`;
- progresso/ciclo, miniestatísticas, Certo/Errado, alternativas, tesoura,
  correta/incorreta, Enter 1/2/3, auto-repeat, editor e conclusão permaneceram
  cobertos e passaram no recorte aplicável.

Os testes históricos foram atualizados somente onde o crescimento legítimo do
contrato ou a nova contagem de marcadores tornava a expectativa corrente
incorreta. Nenhum teste funcional foi alterado.

## 12. Banco, schema, versão e build

- `PRAGMA integrity_check`: `ok`;
- `PRAGMA foreign_key_check`: zero violações;
- SHA-256 do schema SQLite:
  `240e65de128ff81959d6277489c03a5599c7fc404b08d5ace5b79596b00f43a9`;
- versão: `0.29.59`;
- build: `calendar-week-forecast-v1`;
- schema declarado: `25`;
- banco, `main.py`, `banco.py` e `versao.py` permaneceram inalterados.

## 13. Regressões

Nenhuma regressão visual, funcional ou de persistência foi encontrada. Os
hashes integrais provam equivalência do QSS normalizado; os testes de contrato
confirmam valores, direção, stops, alpha e ausência de marcadores não
resolvidos.

Os `ResourceWarning` emitidos por testes antigos de banco são preexistentes e
não representam falha. As falhas históricas permaneceram exatamente separadas
como na B1.

## 14. Elementos restantes e recomendação

Permanecem para revisão futura:

- B2b: painel inferior, Dashboard/retorno, cronômetro, Pular e Encerrar;
- B2c: Dúvida, Análise e indicadores dos checkboxes;
- recortes separados: Modo Foco e corpo do enunciado;
- 3E-C: resumo final da sessão.

Recomendação: manter a próxima entrega separada. A B1 estimou 22 tokens para o
painel e ações da B2b, acima do sinal de alerta de 20; portanto esse orçamento
deve ser revisado antes da migração. Não iniciar B2c ou 3E-C junto dela.

## 15. Métricas consolidadas

- contrato antes: 274;
- contrato depois: 293;
- tokens novos: 19;
- tokens existentes reutilizados: 1 (`canvas.app`);
- tokens recaracterizados: 1 (`progress.fill_gradient`);
- hardcodes removidos: 66;
- hardcodes remanescentes no escopo B2a: 0;
- hardcodes ainda restantes no chrome ativo: 101;
- gradientes migrados: 2 papéis, 4 ocorrências;
- hashes antes/depois: idênticos nos três temas;
- testes aplicáveis: todos aprovados nos conjuntos executados.
