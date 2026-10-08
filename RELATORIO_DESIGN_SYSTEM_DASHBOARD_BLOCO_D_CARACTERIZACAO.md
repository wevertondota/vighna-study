# VighnaStudy — Design System do Dashboard — Bloco D — Caracterização

## 1. Base analisada

Caracterização realizada sobre a base manualmente validada no Windows:

`VighnaStudy_0.29.59_DesignSystem_Dashboard_Bloco_C_COMPLETO.zip`

Metadados de referência:

- versão: `0.29.59`;
- build: `calendar-week-forecast-v1`;
- schema: `25`;
- Design System antes deste bloco: **679 tokens** — 102 semânticos + 577 de componente.

Nenhuma alteração funcional foi necessária para caracterizar o recorte.

## 2. Recorte seguro identificado

O próximo recorte isolável do Dashboard é a seção **Visão geral**, formada por três cards que compartilham `QFrame#dashboardOverviewCard`, diferenciados pela propriedade dinâmica `overviewRole`:

1. `rhythm` — **Ritmo de estudo**;
2. `quality` — **Qualidade do aprendizado**;
3. `projection` — **Progresso do edital**.

A propriedade `overviewRole` permite escopar o novo contrato sem capturar cards de Foco, Planejamento, Recomendação, Seu progresso, Acessos rápidos ou seções inferiores.

## 3. Ritmo de estudo

Elementos visuais caracterizados:

- `dashboardOverviewTitle`;
- `dashboardOverviewInfo`;
- `dashboardOverviewDivider`;
- `dashboardRhythmMainValue`;
- `dashboardRhythmCaption`;
- `dashboardOverviewVerticalDivider`;
- `dashboardRhythmLine`;
- `dashboardRhythmDot`;
- `dashboardRhythmLineLabel`;
- `dashboardRhythmLineValue`;
- `dashboardFocusSummary`;
- `focusProgressBar`;
- `dashboardRhythmStatus`.

Estados já existentes e que devem ser preservados:

- `metricRole="today"`;
- `metricRole="late"`;
- `statusRole="ok"`;
- `statusRole="attention"`.

O `focusProgressBar` já consome contratos existentes do Design System (`focus_mode.progress_*`). Portanto, ele **não deve receber tokens duplicados** neste bloco.

## 4. Qualidade do aprendizado

Elementos visuais caracterizados:

- `dashboardOverviewTitle`;
- `dashboardOverviewInfo`;
- `dashboardOverviewDivider`;
- `dashboardOverviewVerticalDivider`;
- `dashboardQualityEyebrow`;
- `dashboardQualityCaption`;
- `dashboardQualityTrendBox`;
- `dashboardQualityTrendValue`;
- `dashboardQualityTrendLabel`;
- `dashboardQualityFooter`.

Estados dinâmicos existentes em `dashboardQualityTrendValue`:

- `trendRole="none"`;
- `trendRole="positive"`;
- `trendRole="negative"`;
- `trendRole="stable"`.

### Exclusão obrigatória: donut QPainter

O card contém `DashboardDonutWidget`, desenhado por `QPainter`. O desenho ainda usa cores programáticas diretamente em `main.py`, incluindo a trilha calculada e `QColor("#2FB4C7")`.

Esse componente foi deliberadamente **excluído do Bloco D**. Migrá-lo exigiria alterar o caminho programático de pintura e, portanto, deve ocorrer em etapa própria. O objetivo atual é manter `main.py` byte a byte idêntico.

## 5. Progresso do edital

Elementos visuais caracterizados:

- `dashboardProjectionTitleButton`;
- `dashboardOverviewDivider`;
- `dashboardCollapsibleContent` interno;
- `dashboardProjectionCaption`;
- `dashboardProjectionDetail`;
- `dashboardProjectionPercent`;
- `dashboardProjectionBar`;
- `dashboardProjectionMetric`;
- `dashboardProjectionMetricLabel`;
- `dashboardProjectionMetricValue`;
- `effectivenessOpenButton`;
- `syllabusOpenButton`.

Estados de `dashboardProjectionMetric` já existentes:

- `metricRole="notStarted"`;
- `metricRole="consolidating"`;
- `metricRole="consolidated"`;
- `metricRole="domain"`.

A barra de progresso possui trilha, borda e preenchimento próprios. Os dois botões inferiores compartilham o mesmo contrato visual e podem usar um único par de gradientes normal/hover.

## 6. Persistência e comportamento que não podem mudar

A seção já possui estado persistente, entre outros, por meio de:

- `dashboard_secao_resumo_expandida`;
- `dashboard_secao_progresso_expandida`.

Nenhuma alteração de sinal, slot, visibilidade, cálculo, atualização assíncrona ou persistência é necessária para a migração visual.

O seletor `dashboardGroupToggle` aparece em outras seções do Dashboard. Ele não é exclusivo da Visão geral e, por isso, **não deve ser migrado neste bloco**, evitando ampliar o escopo para notificações ou outros agrupamentos.

## 7. Cascata por tema

A caracterização foi feita sobre a aparência efetivamente resultante da cascata final dos temas Claro, Escuro e Futurista, e não apenas sobre a primeira regra encontrada no QSS legado.

O Futurista continua derivando do stylesheet Escuro. Assim, a camada D futurista deve permanecer aditiva: recebe a camada D escura por herança e aplica somente o override D futurista no final.

## 8. Contrato proposto

O mapeamento exige **45 novos tokens de componente**:

- **42 tokens de cor**;
- **3 tokens de gradiente**.

Famílias propostas:

- `dashboard.overview_*`;
- `dashboard.rhythm_*`;
- `dashboard.quality_*`;
- `dashboard.projection_*`.

Resultado esperado após a implementação:

- 102 tokens semânticos;
- 622 tokens de componente;
- **724 tokens totais**.

## 9. Regras de implementação

A implementação deve:

- ser exclusivamente aditiva;
- criar uma camada `ESTILO_DASHBOARD_BLOCO_D`;
- escopar todos os seletores sob `#dashboardRoot`;
- usar `overviewRole` para separar os três cards;
- preservar todos os estados dinâmicos já existentes;
- não alterar `main.py`;
- não alterar `estudos.db`;
- não alterar versão, build ou schema;
- não tocar `DashboardDonutWidget`/`QPainter`;
- não capturar Foco, Planejamento, Recomendação, Seu progresso, Acessos rápidos ou notificações;
- recuperar exatamente o checkpoint C quando a camada D for removida da renderização.
