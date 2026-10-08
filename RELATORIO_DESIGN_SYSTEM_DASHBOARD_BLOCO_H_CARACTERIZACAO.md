# VighnaStudy — Design System do Dashboard — Bloco H — Caracterização

## Disciplinas e acabamento inferior do Dashboard

**Data:** 2026-10-07
**Base analisada:** `VighnaStudy_0.29.59_DesignSystem_Dashboard_Bloco_G_COMPLETO.zip`
**SHA-256 da base:** `dbea3edad4bad49d58aaa549353bfc789c07707aefb2f2c81844a3da64d1cbee`
**Versão:** `0.29.59`
**Build:** `calendar-week-forecast-v1`
**Schema:** `25`
**Design System antes do Bloco H:** **945 tokens** — 102 semânticos + 843 de componente.

---

## 1. Decisão de recorte

A análise estrutural após o Bloco G encontrou dois trechos abaixo de **Estudo por questões**:

1. `priorityQueuePanel` — **Revisões prioritárias**;
2. a seção visível **Disciplinas**.

O primeiro trecho não deve ser promovido a um novo bloco visual neste momento. Embora ainda seja construído no `main.py`, ele é finalizado com:

`fila_painel.setVisible(False)`

Além disso, a chave `fila` não integra mais `obter_secoes_recolhiveis_dashboard()`. O botão `dashboard_toggle_fila` permanece no código por compatibilidade histórica, mas o painel não participa da interface efetivamente apresentada ao usuário.

Portanto, a caracterização aprova como próximo recorte operacional real:

**Dashboard — Bloco H: Disciplinas e acabamento inferior**

Esta decisão corrige a hipótese preliminar registrada na caracterização do Bloco G de que `priorityQueuePanel` seria necessariamente o próximo painel a migrar. A inspeção completa confirma que ele é hoje um consumidor visual dormente. Não é adequado cristalizar novos tokens apenas para uma interface deliberadamente invisível.

`priorityQueuePanel` deve permanecer intacto nesta etapa e ser reavaliado na auditoria final de hardcodes do Dashboard ou se voltar a ser exibido no produto.

---

## 2. Posição estrutural

A seção **Disciplinas** é o último bloco visual ativo montado no método do Dashboard antes de:

- `self.aplicar_estados_secoes_dashboard()`;
- `layout.addStretch()`;
- associação do conteúdo ao `QScrollArea`;
- retorno da tela.

Isso faz do Bloco H o **último recorte de seção ativa na montagem atual do Dashboard**.

Isso não significa, por si só, que o macroescopo Dashboard estará encerrado após H. Ainda será necessária uma auditoria final específica para:

- hardcodes históricos já anulados pela cascata;
- componentes desenhados por `QPainter` deliberadamente deixados fora dos blocos anteriores;
- `priorityQueuePanel` dormente;
- seletores órfãos/legados;
- confirmação de que nenhum consumidor visual ativo do Dashboard ficou sem contrato central.

---

## 3. Fronteira segura confirmada

A seção não possui um único `QFrame` pai envolvendo cabeçalho e grade com um `objectName` exclusivo. A fronteira segura é composta por consumidores únicos dentro de `dashboardRoot`:

- `QFrame#dashboardCenterBar` — barra central de cabeçalho;
- `QPushButton#dashboardSectionToggleCentered` — título recolhível **Disciplinas**;
- `QPushButton#sectionEditButton` — ação **Edição**;
- `QWidget#dashboardCollapsibleContent` — estrutura de conteúdo, compartilhada com outras seções;
- `QPushButton#disciplineButton` — cartões/botões dinâmicos das disciplinas.

A camada H deve usar `QWidget#dashboardRoot` como raiz e selecionar somente os consumidores exclusivos do bloco.

### Regra importante

`dashboardCollapsibleContent` é compartilhado por diversas seções já migradas. O Bloco H **não deve criar contrato visual global novo para esse objectName**. Seu `background: transparent` é estrutural e deve permanecer como está.

Exemplos seguros de seleção:

`QWidget#dashboardRoot QFrame#dashboardCenterBar`

`QWidget#dashboardRoot QFrame#dashboardCenterBar QPushButton#sectionEditButton:hover`

`QWidget#dashboardRoot QPushButton#disciplineButton`

---

## 4. Cabeçalho — Disciplinas

O cabeçalho é um `dashboardCenterBar` centralizado, com tamanho fixo atual de 390 × 50. Geometria, alinhamento, margens e dimensões não pertencem à migração cromática e devem ser preservados.

Elementos ativos:

- `dashboardCenterBar`;
- `dashboardSectionToggleCentered`;
- `sectionEditButton`.

O título é recolhível e utiliza a infraestrutura existente de `definir_estado_secao_dashboard()`.

Estado persistido:

`dashboard_secao_disciplinas_expandida`

O preset executivo e o fallback atual usam **Disciplinas recolhida por padrão**.

Estados a preservar no título:

- expandido;
- recolhido (`expanded=false`);
- hover.

A análise da cascata final mostra uma particularidade relevante: apesar de existirem regras históricas específicas para `expanded=false`, a declaração vencedora final de cor do título é a mesma nos estados expandido e recolhido, nos três temas. A implementação **não deve inventar uma diferenciação visual que hoje não existe**.

Também não há um estado `pressed` materialmente diferente para o título na cascata efetiva.

---

## 5. Botão Edição

`sectionEditButton` é o botão de gerenciamento da seção e abre `JanelaDisciplinas`.

Estados visuais efetivos:

- normal;
- hover;
- pressed.

Os três estados possuem contratos cromáticos próprios e devem ser centralizados sem modificar:

- texto;
- tamanho fixo 92 × 34;
- tooltip;
- conexão com `abrir_disciplinas()`;
- atualização posterior das disciplinas e do Dashboard.

A busca no `main.py` atual encontrou apenas um consumidor com `objectName="sectionEditButton"`, dentro desta seção. Mesmo assim, a nova camada deve permanecer sob `#dashboardRoot` para manter a disciplina de escopo usada nos blocos anteriores.

---

## 6. Grade dinâmica de disciplinas

O conteúdo é criado em `carregar_botoes_disciplinas()`.

Quando existem disciplinas no perfil, cada uma é representada por:

`QPushButton#disciplineButton`

A grade atual usa três colunas e espaçamento já definido no layout. Nada disso deve ser alterado.

Estados visuais efetivos da disciplina ativa:

- normal;
- hover.

Não há aparência específica efetiva para `pressed`; a cascata atual mantém nesse instante o mesmo contrato principal do estado normal.

O clique deve continuar chamando `abrir_disciplina(nome)` exatamente como hoje.

A busca no `main.py` encontrou um único local de criação de `disciplineButton`, portanto o risco de vazamento por objectName é baixo. Ainda assim, o seletor novo deve ficar sob `QWidget#dashboardRoot`.

---

## 7. Estado de disciplina desligada — hotspot crítico

Este é o ponto técnico mais importante do Bloco H.

Quando uma disciplina está pausada/desligada, `carregar_botoes_disciplinas()` aplica `setStyleSheet()` diretamente no botão, com valores físicos hardcoded diferentes por tema.

### Claro

- superfície: `#E2E8F0`;
- texto: `#64748B`;
- borda: `#CBD5E1`.

### Escuro

- superfície: `#28313D`;
- texto: `#94A3B8`;
- borda: `#475569`.

### Futurista

- superfície: `#173244`;
- texto: `#8FA8B8`;
- borda: `#466477`.

Também são preservados no estilo inline:

- `text-align:left`;
- `padding-left:14px`.

O texto do botão passa a receber `• desligada`, e o tooltip informa que a disciplina está desligada temporariamente.

### Consequência para a implementação

Diferentemente dos Blocos F e G, **não é possível centralizar integralmente o Bloco H alterando somente `tema.py`**. O stylesheet aplicado diretamente ao widget tem precedência própria e mantém as cores fora da camada central.

A opção conservadora recomendada é:

1. **manter o mecanismo atual de `setStyleSheet()`**;
2. manter exatamente a mesma ramificação Claro/Escuro/Futurista e a mesma precedência;
3. substituir apenas os três valores físicos por resolução de tokens via `qss_color()`;
4. não converter o estado para nova property dinâmica nesta fase;
5. não remover o stylesheet inline nesta fase.

Essa abordagem altera a **origem dos valores**, não o comportamento nem a aparência, em conformidade com a regra central do Plano Mestre.

Portanto, no Bloco H, `main.py` deixa de ser totalmente imutável: deve ser permitido apenas um diff mínimo e auditável no import do adaptador e nas cores do estilo inline das disciplinas desligadas.

---

## 8. Estado sem disciplinas

Se `listar_disciplinas_gerenciamento()` retornar vazio, a seção cria um `QLabel` genérico com a mensagem:

> Nenhuma matéria está incluída neste perfil. Use “Gerenciar perfis” → “Conteúdos do perfil”.

Esse label:

- não possui `objectName` próprio;
- apenas herda o contrato global de texto/label;
- não possui hardcode visual local.

Não há justificativa para criar um token exclusivo ou alterar seu `objectName` no Bloco H. O estado vazio deve permanecer dependente do contrato global existente.

---

## 9. Cascata visual efetiva — valores representativos

Foi executada leitura estática da cascata final do checkpoint G para os consumidores do bloco. A prova de implementação deverá repetir essa comparação antes/depois.

### 9.1. Claro

- `dashboardCenterBar`: superfície `#FFFFFF`, borda `#D9E3EF`;
- título: texto efetivo `#243B5A`;
- hover do título: superfície `#F1EFFF`, sem mudança material do texto;
- **Edição** normal: `#EAF2FF` / texto `#1D4ED8` / borda `#93C5FD`;
- **Edição** hover: `#DBEAFE` / `#1E40AF` / `#60A5FA`;
- **Edição** pressed: superfície `#BFDBFE`, borda `#3B82F6`;
- disciplina ativa: `#FFFFFF` / texto `#1F2937` / borda `#DBE3ED`;
- disciplina ativa hover: `#EFF6FF` / borda `#93C5FD`;
- disciplina desligada: `#E2E8F0` / `#64748B` / `#CBD5E1`.

### 9.2. Escuro

- `dashboardCenterBar`: superfície `#151F2D`, borda `#2D4054`;
- título: texto efetivo `#D7E4F2`;
- hover do título: superfície `#201E43`, sem mudança material do texto;
- **Edição** normal: `#172554` / texto `#BFDBFE` / borda `#3B82F6`;
- **Edição** hover: `#1E3A8A` / `#DBEAFE` / `#60A5FA`;
- **Edição** pressed: superfície `#1E40AF`, borda `#93C5FD`;
- disciplina ativa: `#1F2937` / texto `#E5E7EB` / borda `#334155`;
- disciplina ativa hover: `#172554` / borda `#3B82F6`;
- disciplina desligada: `#28313D` / `#94A3B8` / `#475569`.

### 9.3. Futurista

O Futurista herda o Escuro e recebe overrides posteriores. Para esta seção, o resultado final é majoritariamente sólido; não foi identificado gradiente efetivo necessário no recorte.

- `dashboardCenterBar`: superfície `#202833`, borda `#445061`;
- título: texto efetivo `#D7E4F2`;
- hover do título: superfície efetiva `#201E43`;
- **Edição** mantém atualmente os mesmos valores cromáticos do Escuro;
- disciplina ativa: `#1F2937` / texto `#D8EEFF` / borda `#334155`;
- disciplina ativa hover: `#172554` / texto `#F4FBFF` / borda `#3B82F6`;
- disciplina desligada: `#173244` / `#8FA8B8` / `#466477`.

Há declarações Futuristas históricas com gradiente para `dashboardCenterBar`, mas elas são anuladas pela cascata final mais específica. **Esses gradientes não devem virar tokens do Bloco H.**

---

## 10. Revisões prioritárias — decisão explícita de não migração

`priorityQueuePanel` possui diversos estilos hardcoded e consumidores próprios:

- `queueCount`;
- `priorityQueueSourceBadge`;
- `priorityQueueExplanation`;
- `priorityQueueTable` e cabeçalho;
- `dashboardSectionToggle`.

Entretanto, no produto atual:

- o painel é explicitamente ocultado com `setVisible(False)`;
- a chave `fila` não é retornada por `obter_secoes_recolhiveis_dashboard()`;
- o usuário não consegue torná-lo visível pelo fluxo normal do Dashboard;
- sua função útil foi transferida para Revisão Inteligente/Recomendação/Planejamento compacto.

Criar agora uma família de tokens para esse painel faria o Design System consolidar uma interface dormente como contrato permanente. Isso é contrário à política já usada nos blocos anteriores de não promover estilo órfão/inativo.

Decisão: **fora do Bloco H**.

Na auditoria final do Dashboard, ele deverá ser classificado como uma das seguintes opções, sem antecipar a decisão nesta fase:

- compatibilidade dormente justificada;
- candidato a remoção futura;
- candidato a tokenização somente se houver plano de reativação.

---

## 11. ObjectNames e risco de vazamento

Busca no `main.py` atual:

- `dashboardCenterBar`: 1 consumidor;
- `dashboardSectionToggleCentered`: 1 consumidor;
- `sectionEditButton`: 1 consumidor;
- `disciplineButton`: 1 ponto de criação;
- `dashboardCollapsibleContent`: 9 consumidores.

Assim, o único nome materialmente compartilhado no recorte é `dashboardCollapsibleContent`, que não deve receber nova camada H.

O risco de vazamento é significativamente menor que no Bloco G, mas a raiz `#dashboardRoot` continua obrigatória.

---

## 12. Comportamento e dados protegidos

O Bloco H não pode alterar:

- `alternar_secao_dashboard("disciplinas")`;
- `definir_estado_secao_dashboard()`;
- persistência `dashboard_secao_disciplinas_expandida`;
- estado inicial recolhido no preset executivo;
- `listar_disciplinas_gerenciamento()`;
- ordem das disciplinas;
- distribuição em três colunas;
- texto e tooltip da disciplina desligada;
- `abrir_disciplina()`;
- `abrir_disciplinas()`;
- atualização de disciplinas/perfis após fechar a janela de edição;
- banco, consultas ou cache;
- geometria do cabeçalho e dos botões;
- comportamento do `priorityQueuePanel` oculto.

`JanelaDisciplinas` e a tela aberta ao clicar em uma disciplina são **módulos externos ao recorte visual do Dashboard** e não devem ser migradas por H.

---

## 13. Arquivos e baseline

Hashes confirmados no checkpoint G:

- `main.py`: `be93709926ac1e4c783468d7409afcfe6b3de200b289f0f0b13f9fc0359defb1`;
- `tema.py`: `b9c49105c69748b93ecd1779e21b4220f11c5ff7c7efa15a5b7d39f6b0aaab22`;
- `ui/design/tokens.py`: `98f3d9f05cd9722b675d62d2d76ed75a6dfeee7851331e0142ded83634f8cc12`;
- `ui/design/themes.py`: `f77df751600e9e77d200a064249b5dd32387aa9dc64c8f0ed7b5be41dca4a1b5`;
- `estudos.db`: `034940a33ea792957d8fafbf5c528db7cd895db69031696fbdd3f0a0ce5a41ef`;
- `versao.py`: `8436214451a591c0a3d3429f62d53c0c01cfc0cc7311d71e57fcf060f5b39642`;
- `foco.py`: `8fbe4659f3371683738a3fa239a789b3bca26ab47dc68f38a69829a33afd03ed`;
- `jogos.py`: `498aab65a2a13efa070ae2f912536b5ddc1aada31e23a28846def6a617492286`;
- `checkpoint.py`: `947295fdf2035d6f65d5d43f70e1d6e5e1c411d92eaca264a469a221b6b61c38`.

Hashes QSS canônicos do checkpoint G:

- Claro: `d0e0149638447e981bdaa0a7099f57ba3d95654808992f52da98ad984b0c4de2`;
- Escuro: `4df67944497bf40a3246ec85d3e863411378936bace30f582d5e28f612f8b166`;
- Futurista: `1227869ce6d10ab4068e13dacd71bb37be8f009a6d22380b2218ed66382e502b`.

Nos três temas, o QSS renderizado do checkpoint G possui **0 marcadores de token não resolvidos**.

Banco validado em modo somente leitura:

- `PRAGMA integrity_check`: **ok**;
- `PRAGMA foreign_key_check`: **0 violações**.

A suíte específica do Bloco G foi reexecutada durante esta caracterização:

**9/9 testes aprovados.**

---

## 14. Orçamento preliminar de tokens

O Bloco H é menor que F e G.

A cascata efetiva sugere aproximadamente **21–24 novos tokens de componente**, provavelmente todos de **cor**, distribuídos entre:

- superfície e borda do cabeçalho;
- texto/hover do título;
- normal/hover/pressed do botão Edição;
- normal/hover dos botões de disciplina;
- superfície/texto/borda do estado desligado.

**Não há gradiente efetivo que precise ser promovido neste recorte**, salvo se a prova de equivalência durante a implementação revelar uma declaração vencedora não capturada na caracterização.

O total não deve ser congelado antes da implementação. Estados materialmente idênticos devem compartilhar contrato quando isso não apagar significado.

Família recomendada:

`dashboard.disciplines_*`

---

## 15. Regra especial para `main.py`

Nos Blocos F e G, `main.py` permaneceu byte a byte protegido. No Bloco H isso não é compatível com a meta de centralização integral da própria seção por causa do stylesheet inline das disciplinas desligadas.

A implementação fica autorizada a alterar `main.py` **somente** para:

1. disponibilizar `qss_color` a partir da API pública de `ui.design`;
2. substituir os nove valores cromáticos físicos usados nos três ramos de tema por tokens do estado desligado.

Nenhuma outra alteração em `main.py` deve ser aceita no diff.

A implementação deve provar que:

- os textos das strings QSS, fora das cores, permanecem equivalentes;
- a mesma ramificação por tema continua ativa;
- não surgiu property nova;
- não mudou a ordem de execução;
- não mudou o estado hover/pressed da disciplina desligada;
- o clique e o tooltip permanecem iguais.

---

## 16. Regras de implementação propostas

A futura implementação do Bloco H deverá:

1. criar uma camada aditiva própria, preferencialmente `ESTILO_DASHBOARD_BLOCO_H`;
2. compor essa camada **após o Bloco G** nos três temas;
3. manter todos os seletores QSS novos sob `QWidget#dashboardRoot`;
4. não criar regra H para `dashboardCollapsibleContent`;
5. centralizar somente as declarações visualmente vencedoras da cascata;
6. preservar a igualdade visual entre título expandido e recolhido;
7. preservar normal/hover/pressed do botão Edição;
8. preservar normal/hover das disciplinas ativas;
9. centralizar o estado desligado usando tokens no stylesheet inline existente, sem mudar a mecânica;
10. não tocar `priorityQueuePanel`;
11. não tocar `JanelaDisciplinas` nem a tela de detalhes de disciplina;
12. não alterar `estudos.db`, `versao.py`, `foco.py`, `jogos.py` ou `checkpoint.py`;
13. não alterar versão, build ou schema;
14. provar rollback exato do QSS ao checkpoint G ao retirar somente a camada H;
15. provar, separadamente, que a substituição dos valores inline em `main.py` produz exatamente as mesmas strings cromáticas por tema.

---

## 17. Testes obrigatórios para a implementação

A implementação deve incluir, no mínimo:

- contagem e tipo dos novos tokens;
- ausência de cores/gradientes físicos hardcoded em `ESTILO_DASHBOARD_BLOCO_H`;
- escopo `#dashboardRoot` em todos os seletores novos;
- verificação de que `dashboardCollapsibleContent` não foi capturado pela camada H;
- equivalência programática da cascata para cabeçalho, toggle, Edição e disciplina ativa;
- teste normal/hover/pressed quando aplicável;
- teste específico dos três estilos de disciplina desligada via `qss_color()`;
- teste de diff restrito de `main.py` ou assertions equivalentes para impedir alterações comportamentais;
- QSS dos três temas sem tokens pendentes;
- novos hashes QSS;
- rollback QSS exato ao checkpoint G;
- hashes dos arquivos protegidos;
- `integrity_check` e `foreign_key_check` do banco;
- bateria dirigida cumulativa A–H e demais etapas já protegidas;
- comparação da suíte ampla com o mesmo baseline histórico/ambiental do checkpoint G.

---

## 18. Validação manual futura no Windows

Depois da implementação, validar Claro, Escuro e Futurista:

1. abrir e recolher **Disciplinas**;
2. confirmar persistência do estado recolhido/expandido;
3. conferir hover do título;
4. conferir **Edição** normal, hover e pressed;
5. abrir **Edição** e confirmar que `JanelaDisciplinas` continua funcionando sem alteração funcional;
6. conferir pelo menos uma disciplina ativa em normal e hover;
7. abrir uma disciplina ativa;
8. conferir uma disciplina desligada, inclusive texto `• desligada`, tooltip e clique;
9. quando possível, desligar/reativar uma disciplina e confirmar recarregamento visual;
10. conferir o estado sem disciplinas apenas se houver perfil adequado para isso;
11. confirmar que `priorityQueuePanel` continua invisível;
12. confirmar que os Blocos A–G permanecem sem regressão visual.

---

## 19. Status da caracterização

**APROVADO PARA IMPLEMENTAÇÃO ISOLADA.**

Formalização recomendada:

**Dashboard — Bloco H: Disciplinas e acabamento inferior**

A implementação deve partir exclusivamente do checkpoint G validado manualmente:

`VighnaStudy_0.29.59_DesignSystem_Dashboard_Bloco_G_COMPLETO.zip`

Após H e sua validação manual, o próximo passo não deve ser inventar automaticamente um Bloco I. Deve ser feita uma **auditoria de encerramento do macroescopo Dashboard** para decidir, com base no código real, se existe outro consumidor ativo a migrar ou se o Dashboard pode ser formalmente fechado antes do próximo item do Plano Mestre.
