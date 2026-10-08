# VighnaStudy — Design System do Dashboard — Bloco G — Caracterização

## Estudo por questões

**Data:** 2026-10-07
**Base analisada:** `VighnaStudy_0.29.59_DesignSystem_Dashboard_Bloco_F_COMPLETO.zip`
**SHA-256 da base:** `1a9e759c60f6bbd53c6c751456e4e3842284fa75cd4eb60a20a5292a482372dc`
**Versão:** `0.29.59`
**Build:** `calendar-week-forecast-v1`
**Schema:** `25`
**Design System antes do Bloco G:** **884 tokens** — 102 semânticos + 782 de componente.

---

## 1. Decisão de recorte

A análise do checkpoint F confirma que **Estudo por questões** é um recorte visual próprio, coeso e isolável do Dashboard. Portanto, a próxima subdivisão operacional pode ser formalizada como:

**Dashboard — Bloco G: Estudo por questões**

Esta denominação não cria uma nova macroetapa do Plano Mestre. Ela apenas subdivide, de forma operacional e reversível, o macroescopo já existente de migração do **Dashboard**.

A regra permanece a mesma: **centralizar a origem dos valores visuais sem redesenhar o componente**. Nesta caracterização não foram alterados código de produção, banco, comportamento, textos, geometria, sinais, slots ou algoritmos.

### Posição estrutural importante

O painel é construído mais abaixo no método, porém é inserido em `dashboard_estrategias_slot`, cujo ponto visual fica após os Acessos rápidos e antes da Visão geral. Portanto, a ordem de construção no `main.py` não deve ser confundida com a ordem visual do Dashboard.

---

## 2. Fronteira segura confirmada

O recorte é ancorado por:

`QWidget#dashboardRoot QFrame#studyNowPanel`

Todo contrato novo do Bloco G deve permanecer descendente dessa âncora.

O painel contém:

- cabeçalho recolhível **Estudo por questões**;
- resumo do banco de questões;
- card **Revisão Inteligente**;
- card **Treino Adaptativo**;
- card **Simulado**;
- card **Banco de Erros**;
- rodapé de **Modo manual** e gerenciamento do banco.

O painel ativo no `main.py` é `self.dashboard_estudo_questoes_painel` e seu conteúdo recolhível é `self.dashboard_estudar_conteudo`.

---

## 3. Cabeçalho do painel

Consumidores ativos:

- `studyNowPanel`;
- `studyNowIcon`;
- `dashboardSectionToggle`;
- `dashboardActionSectionSubtitle`;
- `dashboardCollapsibleContent`.

O `dashboardSectionToggle` usa a mesma infraestrutura das demais seções recolhíveis do Dashboard. O estado persistido é:

`dashboard_secao_estudar_expandida`

Estados que devem permanecer visual e funcionalmente equivalentes:

- expandido;
- recolhido (`expanded=false`);
- hover.

A nova camada não deve criar regra global para `dashboardSectionToggle`; deve atuar apenas dentro de `studyNowPanel`.

O botão interno `self.botao_estudar_agora` é deliberadamente invisível e mantido apenas por compatibilidade. Ele não é um consumidor visual do Bloco G e não deve gerar token.

---

## 4. Resumo do banco de questões

O painel apresenta quatro métricas em `questionsFoundationText`:

- total de questões;
- desempenho;
- erros;
- tópicos.

Esses elementos mudam apenas o texto exibido. Não possuem propriedades visuais dinâmicas próprias no `main.py`.

A migração deve centralizar somente o contrato visual atualmente efetivo e preservar integralmente a atualização dos valores.

---

## 5. Revisão Inteligente

Estrutura ativa:

- `studyActionCard[actionRole="review"]`;
- `studyCardIcon`;
- `studyActionTitle`;
- `studyReviewCount`;
- `studyActionDescription`;
- `studyReviewDetail`;
- `subtleButton` no botão **Revisar**.

O botão **Revisar** possui um estado funcional relevante: ele pode ficar desabilitado quando não há conteúdo disponível na fila de revisão. Portanto, a caracterização deve preservar:

- normal;
- hover;
- disabled.

A quantidade, o detalhe e a habilitação do botão são atualizados pela lógica existente. Nada disso pertence ao Design System.

---

## 6. Treino Adaptativo

Estrutura ativa:

- `strategyCompactCard[actionRole="adaptive"]`;
- `strategyCardIcon`;
- `strategyCardTitle`;
- `strategyCardDescription`;
- `studyAdaptiveCriteria`;
- `adaptiveDashboardButton`.

Estados visuais efetivos do botão:

- normal;
- hover.

O `actionRole="adaptive"` é parte do contrato visual do card e deve continuar sendo respeitado. Ele não deve ser removido nem renomeado.

---

## 7. Simulado

Estrutura ativa:

- `strategyCompactCard[actionRole="simulation"]`;
- `strategyCardIcon` contextualizado no card de simulado;
- `strategyCardTitle`;
- `assessmentBadge`;
- `strategyCardDescription`;
- três `assessmentStat`;
- `assessmentStatLabel`;
- `assessmentStatValue`;
- `mockExamDashboardButton`.

Estados visuais efetivos do botão:

- normal;
- hover.

O card de Simulado possui identidade cromática própria nos três temas e deve continuar diferente do Treino Adaptativo e do Banco de Erros.

Os três valores de estatística — Último, Melhor e Realizados — são dados dinâmicos, mas não alteram o contrato visual do componente.

---

## 8. Banco de Erros

Estrutura ativa:

- `strategyCompactCard[actionRole="recovery"]`;
- `strategyCardIcon`;
- `strategyCardTitle`;
- `studyReviewCount`;
- `strategyCardDescription`;
- `studyAdaptiveCriteria`;
- `subtleButton` no botão **Praticar**.

O estado `actionRole="recovery"` atualmente utiliza a base visual do `strategyCompactCard`; não existe contrato cromático exclusivo que deva ser inventado nesta fase.

A migração deve preservar exatamente essa relação: **ausência de diferenciação específica também é parte da aparência atual**.

---

## 9. Rodapé — modo manual

Estrutura ativa:

- `studyManualFooter`;
- `studyReviewSourceBadge` com o texto “MODO MANUAL”;
- `dashboardTodayDetail`;
- dois `subtleButton`:
  - **Escolher manualmente**;
  - **Gerenciar banco**.

Esses botões usam um objectName extremamente compartilhado no aplicativo. Qualquer regra nova deve ser obrigatoriamente contextualizada dentro de `studyNowPanel`.

---

## 10. ObjectNames compartilhados — risco de vazamento

Este bloco possui mais risco de vazamento que os Blocos E e F porque vários nomes também são usados fora do Dashboard.

### Compartilhados fora do painel

Foram confirmados no `main.py` consumidores externos de:

- `studyNowIcon` — inclusive em fluxo de importação e outras telas;
- `dashboardActionSectionSubtitle`;
- `studyActionCard`;
- `studyActionTitle`;
- `studyActionDescription`;
- `studyReviewSourceBadge`;
- `adaptiveDashboardButton` — também usado em relatório estratégico;
- `mockExamDashboardButton` — também usado em relatório estratégico;
- `subtleButton` — amplamente reutilizado em todo o programa.

Há ainda famílias de estilo historicamente compartilhadas com diálogos de recomendação e outras telas de estudo.

### Regra obrigatória

Toda regra nova deve começar, direta ou indiretamente, por:

`QWidget#dashboardRoot QFrame#studyNowPanel`

Exemplos seguros:

`QWidget#dashboardRoot QFrame#studyNowPanel QLabel#studyActionTitle`

`QWidget#dashboardRoot QFrame#studyNowPanel QPushButton#adaptiveDashboardButton:hover`

`QWidget#dashboardRoot QFrame#studyNowPanel QPushButton#subtleButton:disabled`

Nenhum desses objectNames deve receber contrato global novo no Bloco G.

---

## 11. Seletores históricos fora do recorte

A cascata contém vários seletores relacionados semanticamente a estudo/avaliação, mas que **não possuem consumidor dentro de `studyNowPanel` atual**. Eles não devem ser promovidos a tokens do Bloco G apenas porque aparecem no QSS.

Entre eles:

- `dashboardActionSectionTitle`;
- `studyActionMetric`;
- `studyReviewFooter`;
- `studyColumnTitle`;
- `studyManualButton`;
- `smartReviewDashboardButton`;
- `studyScoreBreakdown`;
- `assessmentPanel`;
- `assessmentTitle`;
- `assessmentDescription`;
- `assessmentHeadline`;
- `studyActionCard[actionRole="adaptive"]` quando usado fora deste painel.

Alguns desses nomes continuam ativos em outras telas do Vighna. Isso não os torna parte deste recorte.

---

## 12. Cascata visual efetiva

A aparência atual não vem de um único bloco QSS. Há várias camadas históricas, incluindo paletas do Dashboard, estilos globais de botões e overrides por tema. A implementação não poderá simplesmente copiar o primeiro seletor encontrado.

A prova de equivalência deverá usar a declaração vencedora final para cada consumidor/estado.

### 12.1. Claro

Contratos representativos atualmente efetivos:

- painel: superfície branca e borda azul-cinza clara;
- subtítulo: cinza azulado;
- resumo do banco: azul escuro;
- Revisão: card branco com borda azul muito suave;
- Adaptativo: card branco com borda verde suave;
- Simulado: card branco com borda âmbar suave;
- Banco de Erros: card-base branco;
- títulos: azul/cinza muito escuro;
- textos auxiliares: cinza azulado;
- botão Adaptativo: verde;
- botão Simulado: âmbar;
- rodapé manual: cinza muito claro com borda suave;
- botões sutis: branco/cinza-azulado, com hover próprio.

Valores representativos observados na cascata final incluem:

- painel `#FFFFFF` / borda `#E2E8F0`;
- card Adaptativo borda `#D4E7DD`;
- card Simulado borda `#ECDCB9`;
- ação Adaptativa `#4F8E69`;
- ação Simulado `#D09A34`;
- rodapé manual `#F8FAFC` / borda `#E0E6EE`.

### 12.2. Escuro

Contratos representativos:

- painel azul-marinho escuro;
- cards internos em superfícies escuras diferenciadas por função;
- textos claros e auxiliares desaturados;
- Adaptativo em verde-petróleo;
- Simulado em âmbar escuro;
- estatísticas em superfície azul-marinho mais profunda;
- rodapé manual mais escuro que o painel.

Valores representativos:

- painel `#151F2D` / borda `#2D4054`;
- Revisão `#152232`;
- Adaptativo `#171F31`;
- Simulado `#201E19`;
- ação Adaptativa `#2E8B7B`;
- ação Simulado `#A97523`;
- rodapé manual `#0E1825` / borda `#304157`.

### 12.3. Futurista

O Futurista apresenta a maior complexidade de cascata. Há coexistência histórica de:

- gradientes;
- `background-color` posteriores;
- bordas reescritas em camadas diferentes;
- estilos herdados do Escuro;
- overrides Futuristas próprios;
- regras globais de harmonização dos botões.

Os pontos que exigem prova explícita de equivalência são:

- superfície do `studyNowPanel`;
- cards Revisão/Adaptativo/Simulado/Banco de Erros;
- ícones do cabeçalho e dos cards;
- botões Adaptativo e Simulado;
- `subtleButton` normal/hover/disabled;
- badges e estatísticas do Simulado.

Gradientes aparecem historicamente no painel, cards e CTAs. A implementação deve centralizar **somente os gradientes que realmente participarem do resultado final da cascata**, evitando cristalizar declarações já anuladas por regras posteriores.

---

## 13. Comportamento e dados protegidos

O Bloco G não pode alterar:

- `alternar_secao_dashboard("estudar")`;
- `definir_estado_secao_dashboard()`;
- persistência `dashboard_secao_estudar_expandida`;
- estado inicial recolhido do setor no preset executivo;
- atualização do resumo do banco de questões;
- cálculo e exibição da Revisão Inteligente;
- habilitação/desabilitação do botão Revisar;
- Treino Adaptativo;
- criação de Simulado;
- Banco de Erros;
- estatísticas Último/Melhor/Realizados;
- resolução manual de questões;
- abertura do gerenciamento do banco;
- `self.botao_estudar_agora` oculto de compatibilidade;
- qualquer consulta ao banco;
- qualquer algoritmo de seleção, fila, domínio ou recomendação.

Não há necessidade técnica identificada de alterar `main.py` para a migração visual deste recorte.

---

## 14. Arquivos protegidos e baseline

Hashes da base F confirmados:

- `main.py`: `be93709926ac1e4c783468d7409afcfe6b3de200b289f0f0b13f9fc0359defb1`;
- `estudos.db`: `034940a33ea792957d8fafbf5c528db7cd895db69031696fbdd3f0a0ce5a41ef`;
- `versao.py`: `8436214451a591c0a3d3429f62d53c0c01cfc0cc7311d71e57fcf060f5b39642`;
- `foco.py`: `8fbe4659f3371683738a3fa239a789b3bca26ab47dc68f38a69829a33afd03ed`;
- `jogos.py`: `498aab65a2a13efa070ae2f912536b5ddc1aada31e23a28846def6a617492286`;
- `checkpoint.py`: `947295fdf2035d6f65d5d43f70e1d6e5e1c411d92eaca264a469a221b6b61c38`.

Hashes QSS canônicos do checkpoint F:

- Claro: `197d1f1051896765152d637943a3c2c0660b81a4514f58a01867377a3144bebd`;
- Escuro: `922d7951bf5edde14ab712112aff8484510bb48702e8f5307e6bef6476c6b1f5`;
- Futurista: `dd3fb829eae39970f600047328bb905878f3a152b8b40eef44f9b4fa872a214b`.

Banco validado em modo somente leitura:

- `PRAGMA integrity_check`: **ok**;
- `PRAGMA foreign_key_check`: **0 violações**.

---

## 15. Orçamento preliminar de tokens

A caracterização indica um recorte de porte intermediário/grande.

O teto preliminar é de aproximadamente **60–70 novos contratos de componente**, combinando:

- superfícies e bordas do painel/cards;
- textos e ícones;
- badges;
- estatísticas;
- estados normal/hover/disabled de ações;
- gradientes realmente efetivos no Futurista.

Este número **não deve ser congelado antes da implementação**. A prova completa da cascata pode reduzir o total quando dois estados forem materialmente equivalentes ou quando um gradiente histórico estiver anulado por regra posterior.

A meta correta é a menor quantidade de tokens capaz de reproduzir, sem perda, a aparência atual dos três temas.

Família recomendada:

`dashboard.study_questions_*`

---

## 16. Regras de implementação propostas

A implementação do Bloco G deverá:

1. criar uma camada aditiva própria, preferencialmente `ESTILO_DASHBOARD_BLOCO_G`;
2. adicionar a camada **após o Bloco F** nos três temas;
3. manter todos os seletores sob `#dashboardRoot #studyNowPanel`;
4. não alterar geometria, margens, espaçamentos, fontes ou layout salvo quando não forem necessários à centralização cromática;
5. não alterar `main.py`;
6. não alterar `estudos.db`;
7. não alterar versão, build ou schema;
8. não tocar Revisões prioritárias (`priorityQueuePanel`), que é o próximo painel independente;
9. não tocar Disciplinas;
10. não migrar estilos de diálogos/telas que apenas reutilizam objectNames deste bloco;
11. preservar normal/hover/disabled dos `subtleButton` dentro do painel;
12. preservar normal/hover dos botões Adaptativo e Simulado;
13. preservar a diferenciação cromática dos quatro modos exatamente como está hoje;
14. provar que remover somente a camada G recupera exatamente os hashes QSS do checkpoint F.

---

## 17. Testes obrigatórios para a implementação

A futura implementação deve incluir, no mínimo:

- contagem e tipo dos novos tokens;
- ausência de cores/gradientes hardcoded dentro da nova camada;
- escopo estrito de todos os seletores;
- presença dos consumidores ativos no `main.py`;
- teste específico de não vazamento para:
  - fluxo de importação;
  - telas de recomendação;
  - relatório estratégico;
  - Resolvedor e demais consumidores de `subtleButton`;
- renderização dos três temas sem tokens pendentes;
- hashes QSS novos;
- rollback exato ao checkpoint F;
- hashes dos arquivos protegidos;
- integridade do banco;
- bateria cumulativa dos Blocos A–G e demais etapas já protegidas.

---

## 18. Validação manual futura no Windows

Após a implementação, a validação manual deve conferir nos temas Claro, Escuro e Futurista:

- painel expandido e recolhido;
- hover do cabeçalho;
- quatro métricas do resumo;
- Revisão Inteligente com conteúdo e sem conteúdo;
- botão Revisar habilitado e desabilitado;
- Treino Adaptativo e hover do botão;
- Simulado, badge, três estatísticas e hover do botão;
- Banco de Erros;
- rodapé Modo Manual;
- hover dos três `subtleButton` visíveis no recorte;
- abertura de Revisão, Adaptativo, Simulado, Banco de Erros, resolução manual e gerenciamento;
- persistência do estado expandido/recolhido;
- ausência de mudança visual nas telas externas que reutilizam os mesmos objectNames.

---

## 19. Resultado da caracterização

**APROVADO para implementação isolada.**

O próximo recorte operacional fica formalmente definido como:

**Dashboard — Bloco G — Estudo por questões**

A implementação pode ser realizada diretamente sobre `VighnaStudy_0.29.59_DesignSystem_Dashboard_Bloco_F_COMPLETO.zip`, mantendo o checkpoint F como baseline de rollback.
