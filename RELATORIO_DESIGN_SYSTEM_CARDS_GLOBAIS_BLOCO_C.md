# VighnaStudy — Design System
## Cards globais — Bloco C: `myEvolutionStatCard` compartilhado

**Data:** 2026-10-08
**Base oficial:** `VighnaStudy_0.29.59_DesignSystem_Cards_Globais_Bloco_B_COMPLETO.zip`
**SHA-256 da base:** `592a6bac04cac4a901df57449e132df6c45d8094e7eac6e37cdd679a910e340e`
**Situação da base:** Bloco B validado manualmente no Windows.
**Objetivo:** centralizar, sem redesenho, somente o shell visual compartilhado `myEvolutionStatCard` e as cores dos seus textos internos, preservando a família `myEvolution*` restante, geometria, tipografia e comportamento.

---

## 1. Escopo implementado

Foi implementado exatamente o recorte aprovado na auditoria pós-Bloco B:

- `QFrame#myEvolutionStatCard` — superfície e borda;
- `QFrame#myEvolutionStatCard QLabel#myEvolutionStatLabel` — cor do rótulo;
- `QFrame#myEvolutionStatCard QLabel#myEvolutionStatValue` — cor do valor;
- `QFrame#myEvolutionStatCard QLabel#myEvolutionStatDetail` — cor do detalhe.

Permaneceram fora do Bloco C:

- `myEvolutionFilterBar`;
- `myEvolutionPanel`;
- `myEvolutionTitle` e `myEvolutionSectionTitle`;
- `myEvolutionInsight*`;
- `evidenceTone`;
- `evolutionChartCard`, `evolutionDisciplineCard` e demais cards de Estatísticas;
- tabelas, gráficos, combos e filtros;
- raio, padding, margens, dimensões e tipografia;
- qualquer lógica de recomendação, algoritmo ou estatística.

`main.py` não precisou ser alterado. Os seis pontos de construção já existentes de `myEvolutionStatCard` foram preservados e nenhum consumidor recebeu propriedade nova.

---

## 2. Contrato criado

Foram adicionados **5 tokens de componente**.

### Cores

- `card.evolution_stat_border`;
- `card.evolution_stat_label_text`;
- `card.evolution_stat_value_text`;
- `card.evolution_stat_detail_text`.

### Gradiente

- `card.evolution_stat_surface_gradient`.

O Design System passou de:

- **1011 → 1016 tokens totais**;
- **909 → 914 tokens de componente**;
- **936 → 940 tokens de cor**;
- **75 → 76 tokens de gradiente**;
- tokens semânticos permaneceram em **102**.

O domínio `card.*` passa a ter **18 tokens**: 15 de cor e 3 de gradiente.

A mesma arquitetura é usada nos três temas. Claro e Escuro usam gradientes degenerados para reproduzir superfícies sólidas; o Futurista preserva o gradiente diagonal histórico.

---

## 3. Valores históricos preservados

### Claro

| Papel | Valor preservado |
|---|---|
| superfície | `#FFFFFF → #FFFFFF` |
| borda | `#D8E0EA` |
| rótulo | `#758397` |
| valor | `#233247` |
| detalhe | `#8995A5` |

### Escuro

| Papel | Valor preservado |
|---|---|
| superfície | `#111D2B → #111D2B` |
| borda | `#33475D` |
| rótulo | `#8999AC` |
| valor | `#E0E8F0` |
| detalhe | `#78899D` |

### Futurista

| Papel | Valor preservado |
|---|---|
| superfície | `#0D2032 → #091725` |
| borda | `#2D5670` |
| rótulo | `#7794A7` |
| valor | `#DCECF3` |
| detalhe | `#6F8CA0` |

Todos os gradientes do Bloco C usam a direção histórica diagonal `x1:0, y1:0, x2:1, y2:1`.

---

## 4. Paleta física

A implementação confirmou a previsão da auditoria: foram necessários **9 novos valores físicos**, todos ausentes da paleta do checkpoint B:

- `#D8E0EA`;
- `#758397`;
- `#8995A5`;
- `#111D2B`;
- `#8999AC`;
- `#E0E8F0`;
- `#0D2032`;
- `#091725`;
- `#2D5670`.

Os demais valores usados pelo Bloco C já existiam na paleta central (`#FFFFFF`, `#233247`, `#33475D`, `#78899D`, `#7794A7`, `#DCECF3`, `#6F8CA0`).

---

## 5. Camada QSS adicionada

Foi criada em `tema.py` a camada final:

`ESTILO_CARDS_GLOBAIS_BLOCO_C`

Ela possui exatamente quatro seletores:

1. shell `myEvolutionStatCard`;
2. `myEvolutionStatLabel` descendente do card;
3. `myEvolutionStatValue` descendente do card;
4. `myEvolutionStatDetail` descendente do card.

A camada não contém cor física literal, `rgba(...)`, raio, padding, margem, tipografia, dimensões, propriedades dinâmicas ou lógica de interação. Todos os valores cromáticos vêm do Design System via `render_qss()`.

A nova camada é composta **depois do Bloco B** em Claro, Escuro e Futurista.

A especificidade descendente evita alterar labels `myEvolutionStat*` utilizados fora do card e deixa `myEvolutionFilterBar`/`myEvolutionPanel` integralmente sob a cascata histórica.

---

## 6. Arquivos alterados

### Produção / documentação

- `ui/design/palette.py`;
- `ui/design/tokens.py`;
- `ui/design/themes.py`;
- `tema.py`;
- `DESIGN_SYSTEM.md`.

### Testes / compatibilidade histórica

- `_design_system_test_helpers.py` — passa a retirar também o Bloco C ao reproduzir snapshots de fases anteriores;
- testes cumulativos com contagens de contrato atualizados para 1016/914;
- `test_design_system_controles_compartilhados.py` — contagem estrutural de gradientes atualizada em +1;
- `test_design_system_cards_globais_bloco_a.py` e `test_design_system_cards_globais_bloco_b.py` — compatibilidade de rollback preservada diante da nova camada posterior;
- novo `test_design_system_cards_globais_bloco_c.py`.

Permaneceram byte a byte iguais à base oficial:

- `main.py` — `66a8dadf431b1eecb3467124856319dc6b7e797dc9bf4f52901a104b6fe174ad`;
- `navegacao.py` — `2cb3439a580cf867af9870750a82e06777718961dd84819e0705a96838c8b862`;
- `estudos.db` — `034940a33ea792957d8fafbf5c528db7cd895db69031696fbdd3f0a0ce5a41ef`;
- `versao.py` — `8436214451a591c0a3d3429f62d53c0c01cfc0cc7311d71e57fcf060f5b39642`;
- `foco.py` — `8fbe4659f3371683738a3fa239a789b3bca26ab47dc68f38a69829a33afd03ed`;
- `jogos.py` — `498aab65a2a13efa070ae2f912536b5ddc1aada31e23a28846def6a617492286`;
- `checkpoint.py` — `947295fdf2035d6f65d5d43f70e1d6e5e1c411d92eaca264a469a221b6b61c38`.

Não houve alteração de versão, build ou schema: **0.29.59 / calendar-week-forecast-v1 / 25**.

Hashes dos principais arquivos modificados após o Bloco C:

- `tema.py`: `52df75a6b0aa6e95cd7cabf0a3ccf1b3c3d47dca9746e7a0166306ff32c55778`;
- `ui/design/tokens.py`: `98b6e3292c5d0c02647f7cffb323cf1f6cc2005959838b1c97bdd5deedb8434a`;
- `ui/design/themes.py`: `d991af58b1bb23a5edddcc34976f7c481adee0881febf01a1567ae34a18c31a3`;
- `ui/design/palette.py`: `eaad7d16865db1674cf39aee096ee45b7dfb36fde4b3f6a6af6950c4ced9e578`.

---

## 7. Testes específicos e rollback

Foi criado `test_design_system_cards_globais_bloco_c.py`, com **11 testes específicos**, cobrindo:

- orçamento total e tipo dos cinco tokens;
- valores exatos por tema;
- direção e stops do gradiente;
- escopo restrito ao shell e textos descendentes;
- ausência da família `myEvolution*` fora do recorte;
- consumo exato dos cinco tokens;
- ausência de cores físicas na nova camada;
- ausência de geometria, tipografia e comportamento;
- preservação dos consumidores existentes sem novas marcações;
- resolução completa por `render_qss()`;
- ordem de composição após o Bloco B;
- rollback exato de `tema.py` ao checkpoint B;
- hashes de arquivos protegidos, banco, versão, build e schema.

O rollback da camada C restaura `tema.py` exatamente ao SHA-256 do checkpoint B:

`51bc6fd2748137ea8cfe45988ef718f4eb6117fa8728202769aff7f2d5c7cefc`

---

## 8. Validação automatizada

### Cards globais A + B + C

**31/31 aprovados — 0 falhas e 0 erros.**

### Bateria dirigida cumulativa

Fundação + Controles compartilhados + Calendário + Dashboard A–I + Navegação Busca Global + Navegação Retornos + Cards globais A:

**131/131 aprovados — 0 falhas e 0 erros.**

### Navegação funcional de regressão

`test_responsividade_navegacao.py` + `test_ver_questoes_topico_navegacao.py`:

**12/12 aprovados.**

### Suíte ampla de Design System

Baseline do Bloco B:

- **304 testes**;
- **8 falhas históricas**;
- **7 erros ambientais/Qt**.

Após Cards globais C:

- **315 testes**;
- **as mesmas 8 falhas históricas**;
- **os mesmos 7 erros ambientais/Qt**.

As 11 execuções adicionais correspondem ao novo arquivo de testes do Bloco C. Não surgiu nova falha ou erro atribuível à implementação.

### Compilação

`py_compile` aprovado para os arquivos de produção relevantes, incluindo `main.py`, `tema.py`, `navegacao.py` e o núcleo `ui/design`.

### Banco

- `PRAGMA integrity_check` → **ok**;
- `PRAGMA foreign_key_check` → **0 violações**.

### QSS final

Claro, Escuro e Futurista:

- **0 marcadores `{{color:...}}` não resolvidos**;
- **0 marcadores `{{gradient:...}}` não resolvidos**.

Hashes canônicos do QSS final desta implementação:

- Claro: `c0387f63d43a694e8f52f111bbff42bc8987fca35cbc8872e5a09d793fc55920`;
- Escuro: `624a50c8170b80fc2072d6b67bdab363a1d2b13ea70b278f480de161e0a89ea7`;
- Futurista: `1186a6e205dc54698e99baeb1e00beb87282b2c7015c1c6c7436d1956dc45583`.

---

## 9. Validação manual recomendada no Windows

Validar nos temas **Claro, Escuro e Futurista**:

1. **Explicação da recomendação** — conferir evidências objetivas, componentes da Fila Inteligente e eixos V5;
2. **Estudar Agora V5** — conferir os cards dos eixos V5;
3. **Laboratório do Algoritmo** — conferir os indicadores baseados em `myEvolutionStatCard`;
4. **Minha evolução / Estatísticas** — conferir os indicadores principais;
5. observar fundo, borda, raio, espaçamento, rótulo, valor e detalhe;
6. confirmar que `myEvolutionFilterBar` e `myEvolutionPanel` não mudaram;
7. conferir labels `myEvolutionStat*` que apareçam fora de `myEvolutionStatCard`;
8. fazer uma passagem rápida por Cards globais A/B, Dashboard e Navegação para ausência de regressão.

---

## 10. Conclusão

**Cards globais — Bloco C implementado e aprovado pelas validações automatizadas.**

Este checkpoint ainda deve ser validado manualmente no Windows antes de se tornar a nova base oficial.

Como a auditoria pós-Bloco B não encontrou outro candidato global claro depois de `myEvolutionStatCard`, o próximo passo correto, após a validação manual, é uma **auditoria final curta de encerramento de Cards globais**. Não deve ser criado Bloco D automaticamente.
