# VighnaStudy — Design System — Dashboard — Bloco B
## Caracterização prévia: Foco + Planejamento de hoje

**Data:** 2026-10-07
**Base validada:** `VighnaStudy_0.29.59_DesignSystem_Dashboard_Bloco_A_COMPLETO.zip`
**SHA-256 da base:** `c1bb6089208827af2de978ad3ea9a4676cc91fa084eda9fbcabfc4b4247bc576`
**Versão:** `0.29.59`
**Build:** `calendar-week-forecast-v1`
**Schema:** `25`
**Design System no início:** 102 tokens semânticos + 453 tokens de componente = **555 tokens**.

## 1. Objetivo

Caracterizar o segundo recorte do Dashboard antes de qualquer migração visual: o módulo **Foco** da primeira dobra e o card **Planejamento de hoje**. O objetivo é separar decisões visuais migráveis de estrutura, comportamento, estado e desenho programático, mantendo a base validada no Windows como referência.

## 2. Fronteira confirmada

O Bloco B contém somente:

- `dashboardFocusPanel`;
- `focusDashboardMainCard`;
- ícone, título, selo, descrição, valor, legenda e detalhes do card de Foco;
- caixa de objetivo embutida `dashboardQuickAccess[embedded="true"]` dentro do card de Foco;
- `dashboardTodayProgress`;
- `dashboardFocusPrimaryButton` e seus estados visuais;
- `dashboardInsightSummary`, cujo conteúdo atual é **Planejamento de hoje**;
- cabeçalho, data e estado semanal do Planejamento;
- textos auxiliares da meta diária;
- progresso legado oculto do resumo, preservado por compatibilidade;
- painel operacional, linhas de revisão/carga/semana, divisor e estados semanais;
- `planningSummaryButton`.

Ficam expressamente fora do Bloco B:

- `focusQuickCard[cardRole="progress"]` — card **Seu progresso**, reservado para bloco posterior;
- card de recomendação do algoritmo e `algorithmRecommendationBody`;
- acessos rápidos gerais do Dashboard;
- cards de visão geral, notificações, disciplinas e demais seções inferiores;
- qualquer limpeza dos seletores órfãos já inventariados;
- `DashboardPlanningArcWidget` enquanto implementação `QPainter`.

## 3. Arquitetura estrutural observada

A seção de Foco nasce em `main.py` como `self.dashboard_hoje_painel`, com `objectName="dashboardFocusPanel"`. O card protagonista é `foco_hoje`, com `objectName="focusDashboardMainCard"`.

Dentro dele existe uma caixa `dashboardQuickAccess` com propriedade dinâmica `embedded=True`. Esse detalhe é essencial: o mesmo `objectName` aparece em outras regiões do Dashboard, de modo que a migração só pode atingir essa caixa quando ela estiver descendente de `focusDashboardMainCard` e com a propriedade `embedded="true"`.

O card da direita é `self.dashboard_resumo_ia`, com `objectName="dashboardInsightSummary"`, atualmente usado para **Planejamento de hoje**. O arco da meta diária é uma instância de `DashboardPlanningArcWidget`, desenhada programaticamente. O QSS do Bloco B não deve tentar migrar sua paleta interna.

## 4. Estados dinâmicos que devem permanecer intactos

Foram identificados estados dependentes de propriedades Qt, especialmente em `weeklyGoalStatus`, incluindo estados como conclusão, atenção e andamento/ativo. A migração pode fornecer tokens para essas aparências, mas não pode alterar:

- nomes das propriedades;
- valores atribuídos em tempo de execução;
- rotinas de atualização do Dashboard;
- sinais/slots;
- temporizadores;
- ordem de construção dos widgets;
- visibilidade dos campos mantidos por compatibilidade.

## 5. Cascata visual efetiva caracterizada

A aparência final não vem de uma única folha. O Dashboard continua recebendo regras históricas sobrepostas de `tema.py`, e o tema Futurista ainda deriva do stylesheet Escuro antes de aplicar suas substituições próprias.

### Claro

O Foco termina com painel e card claros, bordas cinza-azuladas, acentos azul-petróleo, progresso azul e botão principal azul. O Planejamento termina com card branco, acentos azuis, painel operacional muito claro, estados semanais cinza/verde/laranja e botão de contorno azul.

### Escuro

O Foco termina com card em gradiente vinho escuro, acentos rosados e CTA em gradiente vermelho. O Planejamento termina com superfícies azul-marinho, textos claros, estados escuros e CTA secundário azulado.

Não existe regra `:pressed` própria e efetiva para o CTA de Foco no tema Escuro; portanto o Bloco B não deve inventar uma transição nova nesse tema.

### Futurista

O Foco termina com gradiente grafite, acentos rosa pálido e CTA violeta/índigo. O Planejamento termina com gradiente grafite, progresso verde-claro, painel operacional transparente, estados próprios e botão de contorno cinza-claro.

O Futurista recebe primeiro a camada Escura por herança e só depois sua camada final; esse encadeamento deve ser preservado.

## 6. Estratégia de migração aprovada

A migração deve ser **aditiva**:

1. acrescentar contratos semânticos de componente em `ui/design/tokens.py`;
2. cadastrar somente cores físicas ainda ausentes em `ui/design/palette.py`;
3. mapear Claro, Escuro e Futurista em `ui/design/themes.py`;
4. criar três camadas QSS tokenizadas e estritamente escopadas em `tema.py`;
5. anexá-las ao fim de cada composição temática, sem apagar as regras legadas nesta etapa;
6. deixar `main.py`, banco, versão, build, schema e módulos já concluídos byte a byte intactos;
7. deixar `DashboardPlanningArcWidget` fora da camada.

A razão para manter as regras legadas é permitir rollback simples e provar que a nova etapa é uma sobrescrita final localizada, não uma reescrita do Dashboard.

## 7. Orçamento previsto

A caracterização de decisões cromáticas resultou em:

- **60 tokens de cor**;
- **5 tokens de gradiente**;
- total do Bloco B: **65 tokens**.

Com isso, a previsão é passar de 555 para **620 tokens** no Design System, mantendo 102 semânticos e elevando os tokens de componente de 453 para 518.

## 8. Critérios de aprovação

O Bloco B só pode ser considerado tecnicamente concluído se:

- os 65 contratos forem válidos nos três temas;
- não houver hexadecimal literal nas novas camadas QSS;
- todos os seletores novos estiverem sob `#dashboardRoot`;
- o card **Seu progresso** permanecer fora do escopo;
- não houver seletor para `QPainter`/`DashboardPlanningArcWidget`;
- a remoção das novas camadas recuperar exatamente o snapshot QSS do Bloco A;
- `main.py`, `estudos.db`, `versao.py`, `foco.py`, `jogos.py` e `checkpoint.py` preservarem seus hashes da base A;
- `py_compile` passar;
- banco permanecer íntegro;
- regressões históricas não aumentarem;
- por fim, houver validação manual no Windows nos três temas.
