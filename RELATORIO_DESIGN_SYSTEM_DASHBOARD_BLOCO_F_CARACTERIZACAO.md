# VighnaStudy — Design System do Dashboard — Bloco F — Caracterização

## Planejamento completo

**Data:** 2026-10-07
**Base analisada:** `VighnaStudy_0.29.59_DesignSystem_Dashboard_Bloco_E_COMPLETO(1).zip`
**SHA-256 da base:** `5ffb288f334b04412e8158765eaba33ba2354adc14258200376935a3758b0e13`
**Versão:** `0.29.59`
**Build:** `calendar-week-forecast-v1`
**Schema:** `25`
**Design System antes do Bloco F:** **785 tokens** — 102 semânticos + 683 de componente.

---

## 1. Objetivo da caracterização

Caracterizar, sem alterar a base, o próximo recorte isolável do Dashboard: **Planejamento completo**, localizado abaixo da Central de atenção e antes de **Estudo por questões**.

A regra continua sendo a mesma do Plano Mestre: nesta fase deve-se **centralizar a origem dos valores visuais sem redesenhar o Vighna**. Portanto, esta etapa não modifica estrutura, comportamento, banco, cálculos, textos, geometria, estados ou fluxo funcional.

Nenhum arquivo de produção foi alterado nesta caracterização.

---

## 2. Fronteira segura confirmada

O recorte é ancorado por:

- `QFrame#planningPanel` — painel completo de Planejamento;
- `QPushButton#dashboardSectionToggle` — somente quando descendente de `planningPanel`;
- `QLabel#planningSectionSubtitle`;
- `QPushButton#planningGoalButton`;
- `QWidget#dashboardCollapsibleContent` — conteúdo estrutural recolhível;
- subseção **Plano imediato**;
- bloco **Meta de hoje**;
- bloco **Próximos 7 dias**;
- linha de ações do planejamento;
- bloco **Metas da semana**.

O novo contrato deve ficar estritamente sob:

`QWidget#dashboardRoot QFrame#planningPanel`

Isso impede que seletores compartilhados atinjam o Planejamento compacto da primeira dobra ou outras seções do Dashboard.

---

## 3. Elementos ativos do Bloco F

### 3.1. Cabeçalho

Consumidores ativos:

- `planningPanel`;
- `dashboardSectionToggle`;
- `planningSectionSubtitle`;
- `planningGoalButton`.

O botão `dashboardSectionToggle` é compartilhado com outras seções do Dashboard. Ele **não pode receber contrato global novo** neste bloco. A migração deve contextualizá-lo dentro de `planningPanel`.

### 3.2. Plano imediato — textos e estrutura

Consumidores ativos:

- `planningSubsectionTitle`;
- `planningSubsectionHint`;
- `planningMicroLabel`;
- `planningItemTitle`.

### 3.3. Meta de hoje

Consumidores ativos:

- `dailyGoalBox`;
- `dailyGoalValue`;
- `dailyGoalProgress`;
- `planningHint`.

Estados funcionais existentes em `goalState`:

- `desativada`;
- `andamento`;
- `concluida`.

Na aparência histórica, `desativada` e `andamento` compartilham parte do contrato e `concluida` altera principalmente hint e preenchimento da barra. Essa equivalência deve ser preservada; não deve ser “melhorada” nesta fase.

### 3.4. Próximos 7 dias

Consumidores ativos:

- `weeklyLoadBox`;
- `planningTotalBadge`;
- `weeklyLoadDays`;
- sete instâncias de `weekDayLoad`;
- `weekDayName`;
- `weekDayDate`;
- `weekDayCount`.

Propriedades dinâmicas usadas nos cards diários:

- `loadLevel="vazia"`;
- `loadLevel="leve"`;
- `loadLevel="moderada"`;
- `loadLevel="alta"`;
- `today=true/false`.

O estado `today=true` possui precedência visual própria e deve continuar prevalecendo sobre a classificação de carga do mesmo card.

### 3.5. Ações do Planejamento

Consumidores ativos:

- `planningJourneyButton` — Jornada do dia;
- `planningAutoPlanButton` — Plano automático;
- duas instâncias de `planningSummaryButton` — Resumo do dia e Fechamento semanal;
- `planningRedistributeButton` — Redistribuir carga.

Estados já previstos no código/QSS:

- `journeyState="nova"`;
- `journeyState="ativa"`;
- `journeyState="pausada"`;
- `journeyState="encerrada"`;
- `hasPlan=true/false`;
- `hasSuggestion=true/false`;
- `hover`;
- `pressed` onde já existe visual efetivo.

A caracterização encontrou uma particularidade importante: os trechos que tentam definir `journeyState` e `hasPlan` aparecem durante a montagem do Dashboard antes da criação desses dois botões. O Bloco F **não deve corrigir essa ordem**, porque isso seria alteração comportamental. O objetivo aqui é apenas preservar o contrato visual existente para os estados já descritos.

### 3.6. Metas da semana

Consumidores ativos:

- `weeklyGoalBox`;
- `weeklyGoalTitle`;
- `weeklyGoalPeriod`;
- `weeklyGoalStatus`;
- `weeklyGoalEmptyState`;
- `weeklyGoalEmptyTitle`;
- `weeklyGoalMetricsContainer`;
- três instâncias de `weeklyGoalMetric`;
- `weeklyGoalMetricTitle`;
- `weeklyGoalValue`;
- `weeklyGoalProgress`;
- `weeklyGoalHint`.

Estados de `weeklyGoalStatus`:

- `weekState="desativada"`;
- `weekState="andamento"`;
- `weekState="atencao"`;
- `weekState="concluida"`.

Estados das métricas semanais:

- `goalState="desativada"`;
- `goalState="andamento"`;
- `goalState="concluida"`.

O estado vazio alterna visibilidade com `weeklyGoalMetricsContainer`; essa lógica não pertence ao Design System e não deve ser alterada.

---

## 4. Elementos compartilhados que exigem escopo estrito

Há dois casos especialmente sensíveis:

### `weeklyGoalStatus`

O mesmo `objectName` também aparece no **Planejamento de hoje** da primeira dobra, já migrado no Bloco B. A camada F deve selecionar somente:

`#dashboardRoot #planningPanel QLabel#weeklyGoalStatus`

### `planningSummaryButton`

O mesmo `objectName` também é usado no card compacto da primeira dobra. No Bloco F existem duas instâncias adicionais dentro do Planejamento completo. A nova camada deve ser limitada a:

`#dashboardRoot #planningPanel QPushButton#planningSummaryButton`

Sem esse contexto, o Bloco F poderia regressar visualmente o Bloco B já validado.

---

## 5. Elementos deliberadamente fora do escopo

Não pertencem ao Bloco F:

- card compacto **Planejamento de hoje** (`dashboardInsightSummary`) — já concluído no Bloco B;
- `DashboardPlanningArcWidget` e qualquer `QPainter` do card compacto;
- `planningSettingsScroll`, `planningSettingsContent`, `planningSettingsCard`, `planningSettingsTitle`;
- `planningLoadLight`, `planningLoadModerate`, `planningLoadHigh`;
- a janela `JanelaPlanejamento` aberta por **Definir metas**;
- telas/diálogos da Jornada do Dia;
- janela do Plano de Ação Automático;
- Resumo do dia;
- Fechamento semanal;
- Redistribuição de carga;
- **Estudo por questões**, que começa imediatamente após `planningPanel`;
- Disciplinas e demais seções inferiores;
- banco, consultas, métricas e algoritmos.

Esses diálogos e telas pertencem a módulos posteriores do Plano Mestre (Modais/Configurações ou seus módulos próprios), não ao recorte visual do Dashboard.

---

## 6. Seletores legados sem consumidor ativo

Dentro das famílias históricas do Planejamento existem pelo menos dois nomes estilizados que não possuem consumidor ativo no `main.py` atual:

- `weeklyGoalSetupButton`;
- `weeklyGoalEmptyDescription`.

Eles **não devem ser promovidos a tokens do Bloco F** apenas porque ainda aparecem no QSS legado.

A mesma regra usada no Bloco E deve ser mantida: estilo órfão não vira contrato permanente do Design System.

---

## 7. Cascata visual efetiva por tema

A aparência atual é resultado de várias camadas históricas sobrepostas. O Bloco F não pode copiar apenas o primeiro bloco `PLANEJAMENTO REORGANIZADO V1`; deve reproduzir o resultado final da cascata.

### Claro

A aparência efetiva usa:

- painel principal branco com borda cinza-azulada;
- caixas internas quase brancas;
- textos em cinza/azul escuro;
- progresso diário azul e conclusão verde;
- carga dos próximos dias com estados neutro, verde, amarelo e vermelho muito suaves;
- ações principais azuis;
- ações secundárias brancas/azuis com estados hover e pressed;
- sugestão de redistribuição em amarelo suave;
- metas semanais com estados neutro, atenção e concluído.

### Escuro

A aparência efetiva usa:

- painel azul-marinho escuro;
- caixas internas em azul-marinho mais profundo;
- textos claros/desaturados;
- progresso azul e conclusão verde;
- cards de carga com superfícies verde/amarela/vermelha escuras;
- ações principais azuis;
- ações secundárias azul-marinho com bordas azuis;
- sugestão de redistribuição em marrom/âmbar escuro;
- metas semanais com badges escuros e estados verde/laranja.

### Futurista

O Futurista continua herdando primeiro o stylesheet Escuro e aplicando depois seus overrides. No Planejamento completo há mistura histórica de:

- `background` com `qlineargradient`;
- `background-color` em regras posteriores;
- bordas e estados reescritos em camadas de especificidade diferente.

Isso aparece especialmente em:

- `planningPanel`;
- caixas `dailyGoalBox`, `weeklyLoadBox`, `weeklyGoalBox`;
- cards `weekDayLoad`;
- botões de ação;
- barras de progresso.

Portanto, a implementação deve usar **comparação da cascata efetiva**, e não simplesmente transcrever a última regra textual encontrada. O Futurista é o tema de maior risco do Bloco F.

---

## 8. Persistência e comportamento que devem permanecer intactos

A seção Planejamento utiliza a configuração persistente:

`dashboard_secao_planejamento_expandida`

Devem permanecer intactos:

- expansão/recolhimento da seção;
- texto e seta do toggle;
- abertura de `JanelaPlanejamento`;
- meta diária de questões;
- cálculo de revisões do dia e atrasadas;
- carga dos próximos 7 dias;
- limites `planejamento_limite_leve` e `planejamento_limite_moderada`;
- geração de `loadLevel`;
- detecção de sobrecarga e `hasSuggestion`;
- metas semanais de questões, revisões e dias;
- cálculo de ritmo semanal;
- estados `desativada`, `andamento`, `atencao` e `concluida`;
- abertura da Jornada do Dia;
- Plano de Ação Automático;
- Resumo do dia;
- Fechamento semanal;
- Redistribuição de carga;
- sinais, slots e chamadas de atualização do Dashboard.

Nenhuma dessas rotinas precisa ser alterada para a centralização visual.

---

## 9. Estratégia de implementação recomendada

A implementação deve ser exclusivamente aditiva:

1. criar contratos `dashboard.planning_full_*` para não confundir o Planejamento completo com os tokens `dashboard.planning_*` já pertencentes ao card compacto do Bloco B;
2. manter os mesmos nomes de tokens nos três temas;
3. criar uma camada final `ESTILO_DASHBOARD_BLOCO_F`;
4. escopar todas as regras em `#dashboardRoot #planningPanel`;
5. utilizar propriedades dinâmicas já existentes, sem criar estados novos;
6. preservar a hierarquia histórica de prioridade entre `today` e `loadLevel`;
7. preservar equivalências visuais atuais entre estados que hoje coincidem;
8. não remover regras legadas nesta etapa;
9. não alterar `main.py`;
10. não alterar `estudos.db`, versão, build ou schema;
11. não tocar nos diálogos acionados pelos botões;
12. provar rollback removendo somente a camada F e recuperando exatamente o checkpoint E.

---

## 10. Orçamento preliminar do contrato

O Bloco F é substancialmente maior que os blocos D e E. A matriz preliminar de decisões visuais foi decomposta em:

- painel/cabeçalho;
- Plano imediato;
- meta diária;
- carga de 7 dias e seus estados;
- Jornada do dia;
- Plano automático;
- ações secundárias;
- redistribuição sugerida;
- Metas da semana e seus estados.

Para preservar inclusive diferenças de gradiente do Futurista sem acoplar visualmente o Planejamento completo ao card compacto, o orçamento inicial proposto é:

- **81 tokens de cor**;
- **27 tokens de gradiente**;
- **108 tokens de componente** no Bloco F.

Previsão após implementação, se a matriz for confirmada pelos testes de equivalência:

- 102 tokens semânticos;
- 791 tokens de componente;
- **893 tokens totais**.

Esse número é um orçamento de implementação, não uma autorização para criar tokens redundantes. Se a comparação formal mostrar que dois contratos são semanticamente o mesmo estado e podem ser compartilhados sem acoplar módulos distintos, a contagem pode ser reduzida antes do checkpoint final.

---

## 11. Baseline técnico do checkpoint E

Hashes canônicos do QSS antes do Bloco F:

- Claro: `81f1c8fc6eebb10cd8dccea854795798f3871a11da372eea4baf02b5f71eb2c4`;
- Escuro: `ef56315047f797aabc02a33118b97a4f6992c775e696c9b1d61509030df45186`;
- Futurista: `29e36ecb0c7cbb06dfe15821c7c07b84ad6a81dc75a48f2d5fe56db70fe9079d`.

Arquivos protegidos no checkpoint E:

- `main.py`: `be93709926ac1e4c783468d7409afcfe6b3de200b289f0f0b13f9fc0359defb1`;
- `estudos.db`: `034940a33ea792957d8fafbf5c528db7cd895db69031696fbdd3f0a0ce5a41ef`;
- `versao.py`: `8436214451a591c0a3d3429f62d53c0c01cfc0cc7311d71e57fcf060f5b39642`;
- `foco.py`: `8fbe4659f3371683738a3fa239a789b3bca26ab47dc68f38a69829a33afd03ed`;
- `jogos.py`: `498aab65a2a13efa070ae2f912536b5ddc1aada31e23a28846def6a617492286`;
- `checkpoint.py`: `947295fdf2035d6f65d5d43f70e1d6e5e1c411d92eaca264a469a221b6b61c38`.

Validação de banco feita em modo somente leitura durante a caracterização:

- `PRAGMA integrity_check`: **ok**;
- `PRAGMA foreign_key_check`: **0 violações**.

Os três stylesheets atuais renderizam com:

- **0** marcadores `{{color:...}}` não resolvidos;
- **0** marcadores `{{gradient:...}}` não resolvidos.

---

## 12. Critério de aprovação futuro do Bloco F

O Bloco F só deve ser considerado concluído quando:

- somente o Planejamento completo for atingido;
- o Planejamento compacto do Bloco B permanecer byte/visual funcionalmente preservado;
- `weeklyGoalStatus` e `planningSummaryButton` não vazarem para fora de `planningPanel`;
- estados de `loadLevel`, `today`, `goalState`, `weekState`, `hasPlan`, `hasSuggestion` e `journeyState` mantiverem o comportamento existente;
- nenhuma cor física literal for introduzida na nova camada tokenizada;
- Claro, Escuro e Futurista não tiverem marcadores não resolvidos;
- remover a camada F recuperar exatamente os hashes QSS do checkpoint E;
- os arquivos protegidos permanecerem idênticos;
- banco e metadados permanecerem íntegros;
- a suíte dirigida dos Blocos A–F passar;
- a suíte histórica não ganhar regressões novas;
- a validação manual no Windows confirmar paridade visual e funcional nos três temas.

---

## 13. Conclusão da caracterização

O **Bloco F — Planejamento completo é isolável sem alteração de `main.py`**.

O recorte está suficientemente delimitado para implementação conservadora. O principal risco não é funcional, mas de **cascata e compartilhamento de `objectName`**, especialmente no Futurista e nos dois nomes compartilhados com o Bloco B (`weeklyGoalStatus` e `planningSummaryButton`).

Próximo passo recomendado: implementar a camada F partindo exclusivamente do checkpoint E, seguida por comparação de cascata, testes específicos, prova de rollback, auditoria de banco e geração do novo ZIP para validação manual no Windows.
