# VighnaStudy — Design System
## Caracterização do macroescopo: Cards globais

**Data:** 2026-10-07
**Base oficial analisada:** `VighnaStudy_0.29.59_DesignSystem_Navegacao_Retornos_Dashboard_COMPLETO.zip`
**SHA-256 da base:** `7e02d3709dd33a9707a4af143734e82d85a6da2906ba311c0e1014df8361c163`
**Objetivo desta etapa:** caracterizar o próximo macroescopo do Plano Mestre sem alterar arquivos de produção e definir um primeiro recorte pequeno, reversível e visualmente conservador.

---

## 1. Baseline confirmado

A árvore de trabalho usada nesta análise foi comparada com a extração do ZIP oficial. Os arquivos `main.py`, `tema.py`, `estudos.db`, `versao.py`, `foco.py`, `jogos.py`, `navegacao.py`, `ui/design/tokens.py`, `ui/design/themes.py` e `ui/design/palette.py` são byte a byte idênticos entre as duas cópias.

O Design System possui atualmente:

- **998 tokens totais**;
- **102 tokens semânticos**;
- **896 tokens de componente**;
- **925 tokens de cor**;
- **73 tokens de gradiente**;
- **nenhum token `card.*` existente**.

Banco de dados:

- `PRAGMA integrity_check = ok`;
- `PRAGMA foreign_key_check = 0 violações`.

A suíte ampla de Design System, executada com o mesmo stub de Qt usado nas etapas anteriores neste ambiente, manteve o baseline conhecido:

- **284 testes executados**;
- **8 falhas históricas**;
- **7 erros ambientais/Qt**;
- nenhum resultado novo foi produzido, pois esta caracterização não modifica código.

O ambiente Linux desta análise não possui PySide6 nativo. Por isso, os testes que dependem diretamente do Qt real continuam sendo validação manual no Windows, como nas etapas anteriores.

---

## 2. O que “Cards globais” significa no código atual

O projeto não possui hoje uma única classe `Card` nem um único seletor global responsável por todos os cartões. A palavra “card” aparece em componentes de naturezas muito diferentes.

A inspeção separou os consumidores em três grupos:

### 2.1. Cards realmente genéricos e compartilhados

São estruturas sem domínio funcional próprio, usadas apenas como superfícies de organização visual:

| Família | Consumidores ativos observados | Contextos | Estado visual |
|---|---:|---|---|
| `dialogCard` | 5 construções | `JanelaEstudoTopico` e tela de Disciplina | normal |
| `metricCard` | 3 instâncias geradas por helper | `JanelaEstudoTopico` | normal |
| `miniStat` | 6 instâncias geradas por loop | `JanelaFechamentoSemanal` | normal |

Essas famílias são o núcleo mais seguro para iniciar o macroescopo Cards globais.

### 2.2. Cards compartilhados, mas já acoplados a um domínio

Exemplos importantes:

- `studyActionCard`: usado no Dashboard, em diálogos do Motor V5 e no Fechamento semanal;
- `myEvolutionStatCard`: usado em Minha evolução e em telas de explicação/recomendação do algoritmo.

Apesar de aparecerem em mais de uma tela, eles carregam semântica própria, estados como `actionRole`, regras de cascata específicas e, no Futurista, gradientes próprios. Tratá-los como “card base” agora misturaria fundação visual com domínio do algoritmo/evolução.

Eles devem ser reavaliados em um recorte posterior, depois que a fundação básica estiver centralizada.

### 2.3. Cards específicos de módulos

Foram encontrados numerosos cards de Resolvedor, Calendário, Modo Foco, Configurações, Estatísticas, Relatórios, Edital, Central de Questões e outros recursos. Exemplos: `questionSessionSummaryCard`, `calendarForecastCard`, `focusHeroMiniCard`, `effectivenessStatCard`, `topicMetricCard`, `evolutionChartCard`.

Esses componentes **não devem ser absorvidos pelo primeiro bloco de Cards globais**. Muitos já pertencem a domínios previamente centralizados ou a macroescopos posteriores do Plano Mestre.

---

## 3. Consumidores do primeiro recorte

### 3.1. `dialogCard`

Há quatro construções em `JanelaEstudoTopico`:

1. cabeçalho do diálogo;
2. ciclo de questões;
3. configuração da bateria;
4. lista de questões.

Há ainda uma construção ativa na tela de Disciplina:

5. painel de ações do tópico selecionado.

O componente não possui hover, pressed, checked, selected nem propriedades dinâmicas. É somente uma superfície com borda e raio.

### 3.2. `metricCard`

O helper local de `JanelaEstudoTopico` gera três cartões:

- Questões disponíveis;
- Inéditas;
- Com erro anterior.

O shell do card também não possui estados interativos.

### 3.3. `miniStat`

`JanelaFechamentoSemanal` cria seis cards de resumo:

- Foco efetivo;
- Sessões;
- Dias com foco;
- Questões;
- Desempenho;
- Revisões.

Também não há estados interativos no shell.

---

## 4. Aparência efetiva atual por tema

A cascata final foi inspecionada nos stylesheets resolvidos de Claro, Escuro e Futurista.

### `dialogCard`

| Tema | Fundo | Borda | Raio |
|---|---|---|---:|
| Claro | `#FFFFFF` | `#DBE3ED` | 11 px |
| Escuro | `#182235` | `#334155` | 11 px |
| Futurista | `#182235` | `#334155` | 11 px |

### `metricCard`

| Tema | Fundo | Borda | Raio |
|---|---|---|---:|
| Claro | `#FFFFFF` | `#E2E8F0` | 10 px |
| Escuro | `#182235` | `#334155` | 10 px |
| Futurista | `#182235` | `#334155` | 10 px |

### `miniStat`

| Tema | Fundo | Borda | Raio |
|---|---|---|---:|
| Claro | `#FBFDFF` | `#D9E5F0` | 10 px |
| Escuro | `#182235` | `#334155` | 10 px |
| Futurista | `#182235` | `#334155` | 10 px |

### Tipografia interna dos cards métricos

| Papel | Claro | Escuro | Futurista |
|---|---|---|---|
| rótulo | `#64748B` | `#94A3B8` | `#94A3B8` |
| valor | `#111827` | `#F8FAFC` | `#F8FAFC` |

**Observação importante:** nesse recorte, o Futurista herda deliberadamente os valores do Escuro. A Fase A deve preservar isso exatamente; não é o momento de dar uma nova identidade visual a esses cards.

---

## 5. Cascata e risco de vazamento

Os três shells genéricos possuem regras simples no stylesheet-base. Não há override final específico para `dialogCard`, `metricCard` ou `miniStat` que altere seus fundos/bordas depois dessas regras.

Há, porém, seletores de texto compartilhados fora dos cards:

- `metricLabel` também é usado como eyebrow/cabeçalho em outros pontos;
- `miniStatLabel` e `miniStatValue` também são reutilizados em interfaces do Resolvedor e do Plano Automático.

Portanto, **não é recomendável substituir globalmente esses seletores de texto no primeiro bloco**.

A implementação segura deve acrescentar seletores finais escopados aos cards, por exemplo conceitualmente:

```text
QFrame#metricCard QLabel#metricLabel
QFrame#metricCard QLabel#metricValue
QFrame#miniStat QLabel#miniStatLabel
QFrame#miniStat QLabel#miniStatValue
```

Assim, o card passa a consumir o Design System sem alterar os consumidores históricos dos mesmos `objectName` em outras telas.

---

## 6. Elementos deliberadamente fora do primeiro recorte

### `filterBar`

É compartilhado entre Relatórios e Disciplina, mas representa uma barra de filtros, não um card de conteúdo. Deve permanecer fora do bloco inicial para não misturar cartões com controles compartilhados.

### `studyActionCard`

É ativo fora do Dashboard e merece atenção posterior, mas possui:

- uso no Dashboard já centralizado e escopado;
- uso em três diálogos do Motor V5;
- uso no Fechamento semanal;
- estados `actionRole="review"` e `actionRole="adaptive"`;
- gradiente próprio no Futurista;
- várias camadas históricas de QSS.

Migrá-lo junto com `dialogCard` aumentaria desnecessariamente o risco do primeiro lote.

### `myEvolutionStatCard`

Também é compartilhado entre Minha evolução e telas do algoritmo, com gradiente específico no Futurista. Deve ser caracterizado junto do bloco compartilhado de algoritmo/evolução, não no núcleo básico.

### Cards específicos de domínio

Não entram neste recorte cards de:

- Dashboard — macro já encerrado;
- Navegação — macro já encerrado;
- Resolvedor/Resumo final — contratos já existentes;
- Calendário — contrato `calendar.*` já existente;
- Modo Foco/Pausa/Jogos — macro posterior;
- Estatísticas/Relatórios/Evolução/Configurações — macroescopos próprios;
- estilos mortos/históricos sem consumidor ativo comprovado.

---

## 7. Recorte proposto

### Cards globais — Bloco A: Superfícies básicas e métricas

**Inclui somente:**

- `QFrame#dialogCard`;
- `QFrame#metricCard`;
- `QFrame#miniStat`;
- textos internos de `metricCard` e `miniStat`, mediante seletores descendentes escopados.

### Contrato proposto

Estimativa conservadora: **8 novos tokens de componente, todos de cor**.

```text
card.dialog_surface
card.dialog_border
card.metric_surface
card.metric_border
card.mini_stat_surface
card.mini_stat_border
card.metric_label_text
card.metric_value_text
```

`card.metric_label_text` e `card.metric_value_text` podem ser compartilhados entre `metricCard` e `miniStat`, porque os dois papéis são equivalentes e os valores efetivos coincidem nos três temas.

Não há necessidade de token de gradiente neste Bloco A.

### Impacto estimado no contrato

- atual: **998 tokens**;
- após implementação proposta: **1006 tokens**;
- cores: +8;
- gradientes: +0.

### Paleta física

Todos os valores necessários já existem em `ui/design/palette.py`, **exceto `#D9E5F0`**, usado na borda clara de `miniStat`. A implementação provavelmente exigirá registrar apenas esse novo valor físico.

---

## 8. Arquivos que podem mudar na implementação

A implementação do Bloco A deve poder ficar limitada a:

- `ui/design/palette.py` — provável inclusão de `#D9E5F0`;
- `ui/design/tokens.py` — contrato `card.*`;
- `ui/design/themes.py` — mapeamento dos três temas;
- `tema.py` — nova camada final tokenizada e escopada;
- `DESIGN_SYSTEM.md` — documentação do novo domínio;
- novo teste específico de Cards globais.

**Não há necessidade prevista de alterar:**

- `main.py`;
- `navegacao.py`;
- `foco.py`;
- `jogos.py`;
- `banco.py`;
- `estudos.db`;
- `versao.py`;
- schema ou comportamento.

Os `objectName` existentes já fornecem todos os anchors necessários.

---

## 9. Estratégia de implementação recomendada

A metodologia deve seguir a mesma aplicada aos blocos anteriores:

1. manter as regras históricas intactas como camada de compatibilidade;
2. adicionar uma camada final `ESTILO_CARDS_GLOBAIS_BLOCO_A`;
3. resolver somente cores por `render_qss()`;
4. preservar raio, margens, padding, tipografia, tamanhos e layouts;
5. usar no Futurista exatamente os valores efetivos atuais do Escuro para esse recorte;
6. não alterar comportamento ou hierarquia dos widgets;
7. validar que retirar a nova camada recupera a baseline anterior.

Essa abordagem mantém reversibilidade e evita uma limpeza ampla de QSS durante a Fase A.

---

## 10. Validação prevista para o Bloco A

### Automática

A implementação deverá verificar, no mínimo:

- existência dos 8 tokens em todos os temas;
- tipos corretos (`COLOR`);
- 0 tokens QSS não resolvidos;
- paridade exata dos valores efetivos antes/depois para os três temas;
- ausência de cores físicas na nova camada;
- nenhum novo gradiente;
- nenhum `main.py` alterado;
- `py_compile` dos arquivos de produção modificados;
- bateria específica do Bloco A;
- bateria dirigida cumulativa do Design System;
- comparação com o baseline conhecido da suíte ampla;
- `PRAGMA integrity_check`;
- `PRAGMA foreign_key_check`.

### Manual no Windows

Após gerar o checkpoint, validar nos três temas:

- tela de Disciplina: painel de ações do tópico selecionado (`dialogCard`);
- Estudar tópico: cabeçalho, Ciclo de questões, Configuração e Lista (`dialogCard`);
- Estudar tópico: três cards métricos (`metricCard`);
- Fechamento semanal: seis miniestatísticas (`miniStat`);
- ausência de mudança visual em labels reutilizados fora desses cards;
- ausência de mudança em Dashboard, Busca Global e retornos de navegação.

---

## 11. Veredito

**APROVADO PARA IMPLEMENTAÇÃO ISOLADA.**

O primeiro lote de Cards globais deve ser:

> **Cards globais — Bloco A: Superfícies básicas e métricas**

O recorte é pequeno, possui consumidores ativos identificados, não exige mudança de comportamento, não exige alteração de `main.py` e permite inaugurar o domínio `card.*` sem antecipar decisões sobre cards do Motor V5, Evolução, Modo Foco, Resolvedor ou outros módulos.

Após a implementação e validação manual desse Bloco A, deve ser feita uma auditoria curta para decidir o próximo recorte de Cards globais — provavelmente o grupo compartilhado `studyActionCard` / `myEvolutionStatCard` — sem presumir antecipadamente que ele será necessário ou que terá o mesmo contrato.
