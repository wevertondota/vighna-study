# VighnaStudy — Design System
## Auditoria curta de Cards globais após o Bloco A

**Data:** 2026-10-07
**Base auditada:** `VighnaStudy_0.29.59_DesignSystem_Cards_Globais_Bloco_A_COMPLETO.zip`
**SHA-256:** `cdc3d5c4900666c8a4fc3a906693efa87bc59345da20b1a5305f35205c8c730c`
**Situação manual:** Bloco A validado no Windows pelo usuário.
**Objetivo:** confirmar o Bloco A, revisar consumidores compartilhados ainda fora do contrato `card.*` e decidir, sem implementar, se existe justificativa para um próximo recorte.

---

## 1. Baseline confirmado

O ZIP final do Bloco A foi extraído novamente para uma árvore independente. Os arquivos de produção relevantes (`main.py`, `tema.py`, `estudos.db`, `versao.py`, `foco.py`, `jogos.py`, `navegacao.py`, `ui/design/palette.py`, `ui/design/tokens.py` e `ui/design/themes.py`) são byte a byte idênticos à árvore auditada.

O Design System permanece em:

- **1006 tokens totais**;
- **102 tokens semânticos**;
- **904 tokens de componente**;
- **933 tokens de cor**;
- **73 tokens de gradiente**;
- **8 tokens `card.*`**, todos pertencentes ao Bloco A.

Verificações reexecutadas nesta auditoria:

- `test_design_system_cards_globais_bloco_a.py`: **10/10 aprovados**;
- regressão funcional de navegação: **12/12 aprovados**;
- `py_compile` dos arquivos de produção relevantes: **aprovado**;
- `PRAGMA integrity_check`: **ok**;
- `PRAGMA foreign_key_check`: **0 violações**;
- QSS final Claro/Escuro/Futurista: **0 tokens de cor não resolvidos e 0 tokens de gradiente não resolvidos**.

A suíte ampla não precisou ser usada como critério desta auditoria, porque nenhum arquivo de produção foi alterado após o checkpoint já testado no Bloco A.

---

## 2. Correção de inventário do Bloco A

A caracterização inicial registrou cinco construções de `dialogCard`. A varredura AST completa encontrou **sete construções ativas**:

- quatro em `JanelaEstudoTopico`;
- duas em `JanelaRevisao`;
- uma na tela de Disciplina (`SistemaEstudos.criar_tela_disciplina`).

Isso **não exige correção de código**. A camada do Bloco A usa o seletor global `QFrame#dialogCard`, portanto as duas construções de `JanelaRevisao` já foram centralizadas automaticamente. Não há override específico posterior de `dialogCard` nessas duas instâncias, e os valores cromáticos do token reproduzem a cascata anterior.

Conclusão: trata-se de uma **correção documental de cobertura**, não de uma regressão nem de uma pendência de implementação.

---

## 3. Inventário amplo de cards

A análise estática de `main.py` encontrou **63 `objectName` diferentes contendo “card”**, distribuídos por **113 pontos de construção**. Esse número não significa que 63 componentes devam ser migrados no macroescopo Cards globais.

A maior parte é específica de domínio e deve permanecer para os macroescopos próprios do Plano Mestre. Exemplos:

- `questionEditorCard`, `questionHistoryFilterCard`, `questionSessionSummaryCard` → Central/Resolvedor de Questões;
- `planningSettingsCard` → Planejamento;
- `calendarForecastCard` → Calendário;
- `focusDashboardMainCard`, `focusQuickCard` → Modo Foco;
- `effectivenessStatCard`, `evolutionChartCard`, `evolutionDisciplineCard` → Estatísticas/Relatórios;
- cards `topic*` → detalhes/evolução de tópico.

Portanto, **não é correto perseguir todos os nomes contendo “Card” nesta etapa**. O critério continua sendo compartilhamento real entre domínios e função de superfície visual reutilizável.

---

## 4. Principal pendência global: `studyActionCard`

A auditoria confirmou **sete construções ativas** de `studyActionCard` em cinco contextos:

1. `JanelaExplicacaoRecomendacao`;
2. `JanelaEstudarAgoraV5`;
3. `JanelaProximaRecomendacaoAlgoritmo`;
4. `JanelaFechamentoSemanal` — três cards;
5. Dashboard — um card de Revisão Inteligente.

Os quatro fluxos fora do Dashboard são efetivamente alcançáveis no programa: há chamadas ativas para Fechamento semanal, Estudar Agora V5, Próxima recomendação e Explicação da recomendação.

O consumidor do Dashboard **já está centralizado** pelo contrato `dashboard.study_questions_*`, com seletores de maior especificidade sob `#dashboardRoot #studyNowPanel`. Restam, portanto, **seis construções não-Dashboard** dependentes das regras físicas históricas de `tema.py`.

### Aparência efetiva atual do shell não-Dashboard

#### Claro

- superfície normal: `#FBFCFE`;
- borda normal: `#CDD8E6`;
- borda `review`: `#D1DEED`;
- superfície `adaptive`: `#FAF9FF`;
- borda `adaptive`: `#D9D2F5`;
- raio efetivo: 9 px.

#### Escuro

- superfície normal: `#152232`;
- borda normal: `#354A64`;
- borda `review`: `#34516D`;
- superfície `adaptive`: igual à normal;
- borda `adaptive`: `#5B51A6`;
- raio efetivo: 9 px.

#### Futurista

- superfície normal: gradiente diagonal `rgba(12,31,47,235) → rgba(9,22,36,235)`;
- borda normal: `#2C5069`;
- borda `review`: `#3CCFF0`;
- superfície `adaptive`: igual à superfície normal;
- borda `adaptive`: `#736BDF`;
- raio efetivo: 9 px.

Esses valores ainda são físicos no QSS histórico para os consumidores não-Dashboard.

---

## 5. Por que `studyActionCard` justifica um Bloco B

Ele atende aos critérios de Cards globais:

- é reutilizado em **mais de um domínio funcional**;
- funciona como shell visual, não como regra de negócio;
- possui estados visuais reais (`actionRole="review"` e `actionRole="adaptive"`);
- possui aparência diferente nos três temas, incluindo gradiente no Futurista;
- o Dashboard já possui um contrato próprio, o que permite preservar esse consumidor por especificidade sem duplicar sua migração.

A migração pode ser conservadora e restrita ao shell e aos estados cromáticos. Não há necessidade de alterar callbacks, layouts, raios, margens ou lógica.

### Recorte aprovado

**Cards globais — Bloco B: `studyActionCard` compartilhado**

Escopo recomendado:

- `QFrame#studyActionCard`;
- `QFrame#studyActionCard[actionRole="review"]`;
- `QFrame#studyActionCard[actionRole="adaptive"]`;
- somente propriedades cromáticas de superfície e borda.

Não incluir no Bloco B os textos `studyActionTitle`, `studyActionDescription`, `studyColumnTitle`, badges ou botões. Esses `objectName` também aparecem fora do card e em outros domínios; centralizá-los junto do shell aumentaria o raio de regressão sem necessidade.

### Contrato estimado

A solução mais enxuta é de aproximadamente **5 novos tokens de componente**:

- `card.study_action_surface_gradient`;
- `card.study_action_border`;
- `card.study_action_review_border`;
- `card.study_action_adaptive_surface_gradient`;
- `card.study_action_adaptive_border`.

Os temas Claro e Escuro podem usar gradientes degenerados (dois stops iguais), padrão já utilizado pelo Design System, enquanto o Futurista preserva o gradiente atual. Assim, a mesma arquitetura é mantida nos três temas.

Estimativa de contrato após o bloco: **1006 → 1011 tokens**.

---

## 6. `myEvolutionStatCard`: candidato posterior, não misturar agora

Foram confirmadas **seis construções** de `myEvolutionStatCard` em:

- Explicação da recomendação;
- Estudar Agora V5;
- Laboratório do Algoritmo;
- Minha evolução.

O componente também é compartilhado e permanece um candidato real a centralização. Entretanto, ele está fortemente acoplado à família visual `myEvolution*`: atualmente compartilha regra com `myEvolutionFilterBar` e `myEvolutionPanel`, além de possuir rótulos/valores/detalhes próprios e gradiente Futurista.

Por isso, **não deve ser misturado ao Bloco B**. Após validar `studyActionCard`, uma nova auditoria curta decidirá entre:

- um eventual Bloco C isolado para `myEvolutionStatCard`; ou
- sua migração junto ao macroescopo posterior de Estatísticas/Relatórios, caso isso produza arquitetura mais coerente.

Nenhuma decisão antecipada é necessária agora.

---

## 7. Risco de cascata do Bloco B

O risco é controlável.

O único `studyActionCard` dentro do Dashboard é o card de Revisão Inteligente. As regras já centralizadas do Dashboard usam seletores mais específicos, como:

`QWidget#dashboardRoot QFrame#studyNowPanel QFrame#studyActionCard[...]`

Uma camada global de Cards B pode usar somente `QFrame#studyActionCard[...]`. Assim, o contrato do Dashboard continua vencendo por especificidade. Mesmo assim, o teste do Bloco B deve verificar explicitamente essa não-interferência nos três temas.

Não é necessário adicionar propriedade dinâmica nova nem alterar `main.py` para isolar o recorte.

---

## 8. Veredito

### Bloco A

**APROVADO E VALIDADO.**

A base oficial passa a ser:

`VighnaStudy_0.29.59_DesignSystem_Cards_Globais_Bloco_A_COMPLETO.zip`

A correção de inventário de `dialogCard` é documental e não exige patch.

### Macroescopo Cards globais

**AINDA NÃO ENCERRAR.**

Existe uma pendência compartilhada objetiva e suficientemente isolável: `studyActionCard` fora do Dashboard.

### Próximo passo aprovado

**Implementar Cards globais — Bloco B: `studyActionCard` compartilhado**, com escopo cromático mínimo e sem redesenho.

Após validação manual do Bloco B, realizar nova auditoria curta antes de decidir sobre `myEvolutionStatCard` ou qualquer Bloco C.
