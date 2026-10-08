# VighnaStudy — Design System do Dashboard — Bloco E — Caracterização

## 1. Base analisada

Caracterização realizada sobre a base manualmente validada no Windows:

`VighnaStudy_0.29.59_DesignSystem_Dashboard_Bloco_D_COMPLETO.zip`

Metadados de referência:

- versão: `0.29.59`;
- build: `calendar-week-forecast-v1`;
- schema: `25`;
- Design System antes deste bloco: **724 tokens** — 102 semânticos + 622 de componente.

A base foi analisada sem alteração funcional. Os hashes QSS canônicos do checkpoint D são:

- Claro: `67eb7f0c5eee80785bbe7595d4ca9374c9fc2985b34034ede312c06e69e49e08`;
- Escuro: `1109df37ba34574f0607dd9ee3839a770c74aed8906dece461e9c2e8b81f7624`;
- Futurista: `07717d507c118a34f4b8ca7c62556c60a8b0fdc874f7d30f379d19b4ed379d6c`.

## 2. Recorte seguro identificado

O próximo recorte isolável é **Notificações e alertas — Central de atenção**.

A estrutura ativa no `main.py` é formada por:

- `dashboardNotificationsPanel`;
- `dashboardGroupToggle`, contextualizado dentro do painel de notificações;
- `dashboardNotificationsSubtitle`;
- `dashboardCollapsibleContent`;
- dois `dashboardAttentionCard`, separados por `attentionRole="priority"` e `attentionRole="pace"`;
- ícones, textos, badges e rodapé da Central de atenção;
- `syllabusAlertButton` e `syllabusForecastButton`.

O recorte pode ser migrado sem alterar `main.py`, sinais, slots, consultas, cálculos, cache, persistência ou estado de expansão.

## 3. Cabeçalho e painel

O painel possui superfície e borda próprias nos três temas. O botão `dashboardGroupToggle` é compartilhado com outras áreas do Dashboard, mas dentro deste bloco será selecionado **somente quando descendente de `dashboardNotificationsPanel`**, evitando qualquer mudança visual na Visão geral ou em outras seções.

Estados preservados:

- normal;
- hover;
- `expanded="false"`.

Na cascata atual, o texto do estado recolhido coincide com o estado normal. Portanto, não é necessário inventar uma cor exclusiva para o estado recolhido.

`dashboardNotificationsSubtitle` possui contrato cromático próprio por tema.

## 4. Card “Prioridade agora”

O card usa:

- `attentionRole="priority"`;
- `alertState="monitorar"` como estado inicial;
- `alertState="atencao"` quando há alerta de atenção;
- `alertState="ok"` quando não há alerta ativo;
- `alertState="critico"` quando a prioridade é crítica.

A cascata atual diferencia visualmente `ok` e `critico`. Os estados `monitorar` e `atencao` usam deliberadamente a mesma base visual. Essa relação deve ser preservada, não “corrigida”.

Consumidores ativos:

- `dashboardAttentionIcon`;
- `dashboardAttentionEyebrow`;
- `dashboardAttentionTitle`;
- `dashboardAttentionDescription`;
- `dashboardAttentionMeta`;
- `dashboardAttentionBadge`;
- `syllabusAlertButton`.

O botão de prioridade possui estados normal, hover e disabled. O disabled é efetivamente usado quando não existe alerta ativo.

## 5. Card “Ritmo do edital”

O segundo card usa `attentionRole="pace"` e não possui `alertState` dinâmico.

Consumidores ativos:

- `dashboardAttentionIcon`;
- `dashboardAttentionEyebrow`;
- `dashboardAttentionTitle`;
- `dashboardAttentionDescription`;
- `dashboardAttentionMeta`;
- `dashboardPaceBadge`;
- `syllabusForecastButton`.

O botão de previsão possui estados normal, hover e disabled. Na aparência efetiva atual, o disabled preserva superfície e texto do estado normal e altera apenas a borda.

## 6. Rodapé da Central de atenção

O rodapé ativo é composto por:

- `dashboardAttentionFooter`;
- `dashboardAttentionFooterItem`;
- `dashboardAttentionFooterHint`.

Ele apresenta superfície, borda, texto de métricas e texto auxiliar específicos por tema.

## 7. Seletores antigos deliberadamente excluídos

Foram encontrados no QSS histórico seletores como:

- `dashboardNoticeRow`;
- `dashboardNoticeLabel`;
- `dashboardNoticeTitle`;
- `dashboardNoticeIcon`;
- `dashboardNoticeDescription`;
- `dashboardNoticeSummary`;
- `dashboardNotificationsTitle`;
- `dashboardNotificationsMenu`;
- `dashboardNotificationsFooter` e variantes antigas.

Esses nomes **não possuem consumidor ativo no `main.py` atual**. Eles não serão migrados para o novo Design System. Isso evita transformar estilo morto em contrato permanente.

Também não será criado um contrato global para `dashboardGroupToggle`; o escopo será estritamente contextual ao painel de notificações.

## 8. Valores efetivos da cascata

A caracterização considerou a declaração vencedora final, e não apenas a primeira regra encontrada.

### Claro

- painel: `#FFFFFF`, borda `#E2E8F0`;
- prioridade base: `#FFF9EE`, borda `#EAD9B5`;
- prioridade OK: `#F5FAF7`, borda `#D4E7DB`;
- prioridade crítica: `#FFF3F1`, borda `#E8CBC7`;
- ritmo do edital: `#F4F8FD`, borda `#D4E2F0`;
- rodapé: `#FBFCFE`, borda `#E1E7EF`.

### Escuro

- painel: `#151F2D`, borda `#2D4054`;
- prioridade base: `#2B271F`, borda `#5C5137`;
- prioridade OK: `#1D2B25`, borda `#365545`;
- prioridade crítica: `#322120`, borda `#6F4441`;
- ritmo do edital: `#1C2835`, borda `#36516E`;
- rodapé: `#1D242D`, borda `#343E4B`.

### Futurista

- painel: `#202833`, borda efetiva `#2D5874`;
- prioridade base: `rgba(49,39,21,225)`;
- prioridade OK: `rgba(16,43,34,225)`;
- prioridade crítica: `rgba(51,26,27,225)`;
- ritmo do edital: `rgba(10,32,50,230)`;
- rodapé: `rgba(11,26,38,220)`.

Na implementação tokenizada, valores `rgba()` serão registrados em `#AARRGGBB`, formato canônico do Qt, mantendo o mesmo alpha e a mesma cor.

## 9. Persistência e comportamento que não podem mudar

A seção usa o estado persistente `dashboard_secao_notificacoes_expandida` e também pode ser aberta automaticamente quando há alerta crítico.

A migração não pode alterar:

- `alternar_secao_dashboard()`;
- `definir_estado_secao_dashboard()`;
- abertura automática por criticidade;
- cálculo de alertas;
- níveis `Monitorar`, `Atenção` e `Crítico`;
- cálculo da previsão do edital;
- habilitação/desabilitação dos dois botões;
- textos ou tooltips;
- chamadas à tela de Progresso;
- banco de dados ou cache analítico.

## 10. Contrato proposto

O recorte exige **61 novos tokens de componente**, todos de cor e sem novos gradientes.

Famílias propostas:

- `dashboard.notifications_*`;
- `dashboard.attention_priority_*`;
- `dashboard.attention_*`;
- `dashboard.attention_pace_*`;
- `dashboard.attention_forecast_*`.

Resultado esperado após implementação:

- 102 tokens semânticos;
- 683 tokens de componente;
- **785 tokens totais**.

## 11. Regras de implementação

A implementação deve:

- ser aditiva e exclusivamente visual;
- criar `ESTILO_DASHBOARD_BLOCO_E`;
- escopar cada seletor sob `#dashboardRoot` e `#dashboardNotificationsPanel`;
- representar explicitamente os estados `monitorar`, `atencao`, `ok` e `critico` sem alterar a equivalência visual atual;
- preservar estados normal/hover/disabled dos botões;
- não alterar `main.py`;
- não alterar `estudos.db`;
- não alterar versão, build ou schema;
- não tocar Planejamento completo, Estudo por questões, Disciplinas ou QPainter;
- não migrar seletores antigos sem consumidor;
- recuperar exatamente o checkpoint D quando a camada E for removida da renderização.
