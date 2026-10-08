# VighnaStudy — Design System
## Cards globais — Bloco A: Superfícies básicas e métricas

**Data:** 2026-10-07
**Base oficial:** `VighnaStudy_0.29.59_DesignSystem_Navegacao_Retornos_Dashboard_COMPLETO.zip`
**SHA-256 da base:** `7e02d3709dd33a9707a4af143734e82d85a6da2906ba311c0e1014df8361c163`
**Objetivo:** centralizar, sem redesenhar, os shells genéricos `dialogCard`, `metricCard` e `miniStat`, preservando integralmente aparência, geometria e comportamento.

---

## 1. Escopo implementado

Foi implementado exatamente o recorte aprovado na caracterização:

- `QFrame#dialogCard`;
- `QFrame#metricCard`;
- `QFrame#miniStat`;
- `QLabel#metricLabel` e `QLabel#metricValue` **somente quando descendentes de `metricCard`**;
- `QLabel#miniStatLabel` e `QLabel#miniStatValue` **somente quando descendentes de `miniStat`**.

Não foram migrados neste lote:

- `studyActionCard`;
- `myEvolutionStatCard`;
- `filterBar`;
- cards específicos de Dashboard, Resolvedor, Calendário, Modo Foco, Estatísticas, Relatórios, Evolução ou Configurações.

Nenhum `objectName`, callback, layout, margem, padding, raio, tipografia, tamanho ou comportamento foi alterado.

---

## 2. Contrato criado

Foram adicionados **8 tokens de componente, todos do tipo `COLOR`**:

- `card.dialog_surface`;
- `card.dialog_border`;
- `card.metric_surface`;
- `card.metric_border`;
- `card.mini_stat_surface`;
- `card.mini_stat_border`;
- `card.metric_label_text`;
- `card.metric_value_text`.

O Design System passou de:

- **998 → 1006 tokens totais**;
- **896 → 904 tokens de componente**;
- **925 → 933 tokens de cor**;
- gradientes permaneceram em **73**;
- tokens semânticos permaneceram em **102**.

---

## 3. Valores preservados por tema

### Claro

| Token | Valor |
|---|---|
| `card.dialog_surface` | `#FFFFFF` |
| `card.dialog_border` | `#DBE3ED` |
| `card.metric_surface` | `#FFFFFF` |
| `card.metric_border` | `#E2E8F0` |
| `card.mini_stat_surface` | `#FBFDFF` |
| `card.mini_stat_border` | `#D9E5F0` |
| `card.metric_label_text` | `#64748B` |
| `card.metric_value_text` | `#111827` |

### Escuro e Futurista

| Token | Valor |
|---|---|
| `card.dialog_surface` | `#182235` |
| `card.dialog_border` | `#334155` |
| `card.metric_surface` | `#182235` |
| `card.metric_border` | `#334155` |
| `card.mini_stat_surface` | `#182235` |
| `card.mini_stat_border` | `#334155` |
| `card.metric_label_text` | `#94A3B8` |
| `card.metric_value_text` | `#F8FAFC` |

O Futurista continua deliberadamente igual ao Escuro neste recorte, exatamente como na baseline visual anterior.

---

## 4. Paleta física

Somente um novo valor físico precisou ser registrado:

`#D9E5F0`

Todos os demais valores já existiam na paleta central.

---

## 5. Camada QSS adicionada

Foi criada em `tema.py` a camada final:

`ESTILO_CARDS_GLOBAIS_BLOCO_A`

Ela altera somente propriedades cromáticas:

- `background-color`;
- `border-color`;
- `color`.

A camada não contém:

- hexadecimal físico;
- gradiente;
- `border-radius`;
- `padding`;
- `margin`;
- `font-size`;
- `font-weight`;
- propriedades de geometria ou comportamento.

Os textos foram deliberadamente escopados aos seus respectivos cards. Portanto, usos históricos de `metricLabel`, `miniStatLabel` e `miniStatValue` fora desses shells não são atingidos pelo novo contrato.

---

## 6. Arquivos de produção/documentação alterados

- `ui/design/palette.py`;
- `ui/design/tokens.py`;
- `ui/design/themes.py`;
- `tema.py`;
- `DESIGN_SYSTEM.md`.

Permaneceram byte a byte iguais à base oficial:

- `main.py` — `66a8dadf431b1eecb3467124856319dc6b7e797dc9bf4f52901a104b6fe174ad`;
- `navegacao.py` — `2cb3439a580cf867af9870750a82e06777718961dd84819e0705a96838c8b862`;
- `estudos.db` — `034940a33ea792957d8fafbf5c528db7cd895db69031696fbdd3f0a0ce5a41ef`;
- `versao.py` — `8436214451a591c0a3d3429f62d53c0c01cfc0cc7311d71e57fcf060f5b39642`;
- `foco.py` — `8fbe4659f3371683738a3fa239a789b3bca26ab47dc68f38a69829a33afd03ed`;
- `jogos.py` — `498aab65a2a13efa070ae2f912536b5ddc1aada31e23a28846def6a617492286`;
- `checkpoint.py` — `947295fdf2035d6f65d5d43f70e1d6e5e1c411d92eaca264a469a221b6b61c38`.

Não houve alteração de versão, build ou schema: **0.29.59 / calendar-week-forecast-v1 / 25**.

---

## 7. Testes novos e compatibilidade da suíte

Foi criado `test_design_system_cards_globais_bloco_a.py`, com **10 testes específicos** cobrindo:

- orçamento final do contrato;
- tipo dos 8 tokens;
- valores exatos nos três temas;
- paridade deliberada Escuro/Futurista;
- escopo preciso dos seletores;
- ausência de cores físicas e gradientes na nova camada;
- resolução completa dos tokens;
- preservação de geometria/tipografia fora da camada;
- composição posterior à Navegação;
- rollback exato de `tema.py` ao checkpoint anterior;
- arquivos protegidos, banco, versão, build e schema.

Os testes históricos de Design System foram ajustados **somente na infraestrutura de teste** para:

1. reconhecer a nova contagem global de tokens;
2. retirar a camada Cards A quando comparam snapshots de etapas antigas.

Foi criado `_design_system_test_helpers.py` para centralizar essa neutralização em snapshots históricos. Não há impacto no código de produção.

---

## 8. Validação automatizada

### Teste específico

`test_design_system_cards_globais_bloco_a.py`:

**10/10 aprovados**.

### Bateria dirigida cumulativa

Fundação + Controles compartilhados + Calendário + Dashboard A–I + Navegação Busca Global + Navegação Retornos + Cards globais A:

**131/131 aprovados — 0 falhas e 0 erros.**

### Navegação funcional de regressão

`test_responsividade_navegacao.py` + `test_ver_questoes_topico_navegacao.py`:

**12/12 aprovados.**

### Suíte ampla de Design System

Baseline anterior:

- **284 testes**;
- **8 falhas históricas**;
- **7 erros ambientais/Qt**.

Após Cards globais A:

- **294 testes**;
- **as mesmas 8 falhas históricas**;
- **os mesmos 7 erros ambientais/Qt**.

As 10 execuções adicionais correspondem exatamente ao novo arquivo de testes. Não surgiu falha ou erro novo atribuível ao Bloco A.

### Compilação

`py_compile` aprovado para os arquivos de produção relevantes, incluindo:

- `main.py`;
- `tema.py`;
- `ui/design/palette.py`;
- `ui/design/tokens.py`;
- `ui/design/themes.py`;
- `ui/design/adapters.py`;
- `navegacao.py`;
- `versao.py`.

### Banco

- `PRAGMA integrity_check` → **ok**;
- `PRAGMA foreign_key_check` → **0 violações**.

### QSS final

Claro, Escuro e Futurista:

- **0 marcadores `{{color:...}}` não resolvidos**;
- **0 marcadores `{{gradient:...}}` não resolvidos**.

---

## 9. Validação manual recomendada no Windows

Validar nos temas **Claro, Escuro e Futurista**:

1. **Disciplina** — painel de ações do tópico selecionado (`dialogCard`);
2. **Estudar tópico** — cabeçalho, Ciclo de questões, Configuração e Lista (`dialogCard`);
3. **Estudar tópico** — três cards métricos (`metricCard`);
4. **Fechamento semanal** — seis miniestatísticas (`miniStat`);
5. confirmar que raio, espaçamento, tipografia e dimensões permanecem iguais;
6. conferir labels `metricLabel` / `miniStatLabel` / `miniStatValue` fora desses cards para confirmar ausência de vazamento;
7. conferir rapidamente Dashboard, Busca Global e os retornos `← Voltar`.

---

## 10. Conclusão

**Cards globais — Bloco A implementado e aprovado pelas verificações automatizadas.**

O checkpoint ainda deve passar pela validação manual no Windows antes de ser adotado como base oficial.

Após a validação manual, o próximo passo correto é uma **auditoria curta de Cards globais**, sem presumir previamente um Bloco B. Essa auditoria decidirá se `studyActionCard`, `myEvolutionStatCard` ou outro grupo compartilhado realmente justifica um recorte adicional.
