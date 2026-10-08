# VighnaStudy — Design System
## Cards globais — Bloco B: `studyActionCard` compartilhado

**Data:** 2026-10-08
**Base oficial:** `VighnaStudy_0.29.59_DesignSystem_Cards_Globais_Bloco_A_COMPLETO.zip`
**SHA-256 da base:** `cdc3d5c4900666c8a4fc3a906693efa87bc59345da20b1a5305f35205c8c730c`
**Situação da base:** Bloco A validado manualmente no Windows.
**Objetivo:** centralizar, sem redesenho, somente a superfície e as bordas do shell compartilhado `studyActionCard`, preservando os estados `review` e `adaptive` e mantendo o consumidor do Dashboard sob o contrato específico já existente.

---

## 1. Escopo implementado

Foi implementado exatamente o recorte aprovado na auditoria pós-Bloco A:

- `QFrame#studyActionCard`;
- `QFrame#studyActionCard[actionRole="review"]`;
- `QFrame#studyActionCard[actionRole="adaptive"]`;
- somente propriedades cromáticas de superfície e borda.

Permaneceram fora do Bloco B:

- `studyActionTitle`;
- `studyActionDescription`;
- `studyColumnTitle`;
- `studyReviewSourceBadge`;
- botões internos;
- `strategyCompactCard`;
- `myEvolutionStatCard`;
- qualquer regra de layout, raio, margem, padding, tipografia ou comportamento.

`main.py` não precisou ser alterado. Nenhum `objectName`, propriedade dinâmica, callback ou fluxo funcional foi modificado.

---

## 2. Contrato criado

Foram adicionados **5 tokens de componente**:

### Cores

- `card.study_action_border`;
- `card.study_action_review_border`;
- `card.study_action_adaptive_border`.

### Gradientes

- `card.study_action_surface_gradient`;
- `card.study_action_adaptive_surface_gradient`.

O Design System passou de:

- **1006 → 1011 tokens totais**;
- **904 → 909 tokens de componente**;
- **933 → 936 tokens de cor**;
- **73 → 75 tokens de gradiente**;
- tokens semânticos permaneceram em **102**.

A arquitetura é a mesma nos três temas. Claro e Escuro usam gradientes degenerados quando a superfície histórica era uma cor sólida; o Futurista preserva o gradiente diagonal real.

---

## 3. Valores preservados por tema

### Claro

| Papel | Valor preservado |
|---|---|
| superfície normal | `#FBFCFE → #FBFCFE` |
| borda normal | `#CDD8E6` |
| borda `review` | `#D1DEED` |
| superfície `adaptive` | `#FAF9FF → #FAF9FF` |
| borda `adaptive` | `#D9D2F5` |

### Escuro

| Papel | Valor preservado |
|---|---|
| superfície normal | `#152232 → #152232` |
| borda normal | `#354A64` |
| borda `review` | `#34516D` |
| superfície `adaptive` | `#152232 → #152232` |
| borda `adaptive` | `#5B51A6` |

### Futurista

| Papel | Valor preservado |
|---|---|
| superfície normal | `#EB0C1F2F → #EB091624` |
| borda normal | `#2C5069` |
| borda `review` | `#3CCFF0` |
| superfície `adaptive` | `#EB0C1F2F → #EB091624` |
| borda `adaptive` | `#736BDF` |

Os valores `#EB0C1F2F` e `#EB091624` correspondem aos stops históricos `rgba(12,31,47,235)` e `rgba(9,22,36,235)` na convenção ARGB usada pela paleta Qt.

---

## 4. Paleta física

Foram necessários **6 novos valores físicos** na paleta central:

- `#CDD8E6`;
- `#D1DEED`;
- `#FAF9FF`;
- `#D9D2F5`;
- `#5B51A6`;
- `#736BDF`.

Os demais valores utilizados pelo Bloco B já existiam na paleta.

---

## 5. Camada QSS adicionada

Foi criada em `tema.py` a camada final:

`ESTILO_CARDS_GLOBAIS_BLOCO_B`

Ela possui apenas três seletores:

- shell normal;
- estado `review`;
- estado `adaptive`.

A camada não contém cor física literal, `rgba(...)`, raio, padding, margem, tipografia, dimensões ou lógica de interação. Todos os valores cromáticos vêm do Design System via `render_qss()`.

A nova camada é composta **depois do Bloco A** em Claro, Escuro e Futurista.

---

## 6. Preservação do Dashboard

O Dashboard possui um `studyActionCard` de Revisão Inteligente já centralizado no contrato `dashboard.study_questions_*`.

Esse consumidor não foi migrado novamente. Os seletores do Dashboard permanecem mais específicos, por exemplo:

`QWidget#dashboardRoot QFrame#studyNowPanel QFrame#studyActionCard[actionRole="review"]`

A nova camada global usa apenas:

`QFrame#studyActionCard[...]`

Portanto, o contrato específico do Dashboard continua prevalecendo pela cascata/especificidade. O teste do Bloco B verifica explicitamente a permanência desse isolamento.

---

## 7. Arquivos de produção/documentação alterados

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

## 8. Testes e infraestrutura de compatibilidade

Foi criado `test_design_system_cards_globais_bloco_b.py`, com **10 testes específicos**, cobrindo:

- orçamento de tokens e tipos;
- valores exatos de cor por tema;
- direção e stops dos dois gradientes;
- escopo restrito aos três seletores autorizados;
- consumo exato dos cinco tokens;
- ausência de cores físicas na nova camada;
- ausência de geometria/tipografia/comportamento;
- preservação do override específico do Dashboard;
- resolução integral dos tokens;
- ordem de composição após o Bloco A;
- rollback exato de `tema.py` ao checkpoint A;
- hashes dos arquivos protegidos, banco, versão, build e schema.

A infraestrutura histórica de testes foi atualizada somente para neutralizar a nova camada B ao comparar snapshots antigos e para refletir a nova contagem cumulativa do contrato. Nenhum desses ajustes afeta o programa em produção.

---

## 9. Validação automatizada

### Bloco B específico

`test_design_system_cards_globais_bloco_b.py`:

**10/10 aprovados**.

### Cards globais A + B

**20/20 aprovados**.

### Bateria dirigida cumulativa

Fundação + Controles compartilhados + Calendário + Dashboard A–I + Navegação Busca Global + Navegação Retornos:

**131/131 aprovados — 0 falhas e 0 erros.**

### Navegação funcional de regressão

`test_responsividade_navegacao.py` + `test_ver_questoes_topico_navegacao.py`:

**12/12 aprovados**.

### Suíte ampla de Design System

Baseline do Bloco A:

- **294 testes**;
- **8 falhas históricas**;
- **7 erros ambientais/Qt**.

Após Cards globais B:

- **304 testes**;
- **as mesmas 8 falhas históricas**;
- **os mesmos 7 erros ambientais/Qt**.

As dez execuções adicionais correspondem ao novo arquivo de testes do Bloco B. Não surgiu nova falha ou erro atribuível à implementação.

### Compilação

`py_compile` aprovado para os arquivos de produção relevantes.

### Banco

- `PRAGMA integrity_check` → **ok**;
- `PRAGMA foreign_key_check` → **0 violações**.

### QSS final

Claro, Escuro e Futurista:

- **0 marcadores `{{color:...}}` não resolvidos**;
- **0 marcadores `{{gradient:...}}` não resolvidos**.

Hashes canônicos do QSS final desta implementação:

- Claro: `e469ffc574d230caac3c4034d9c06eb4c1dc5305d30131d9f6b97f75513c1ce0`;
- Escuro: `dae9d8172cd669be8d6fe3cd8d493e66d63ca4dfa7a3302c888f49b8d2ddeb63`;
- Futurista: `f8737df77b6c5f8ad6ae03055fc06694a4b77ad3baae0f3936c084a0433d5a4f`.

---

## 10. Validação manual recomendada no Windows

Validar nos temas **Claro, Escuro e Futurista**:

1. **Explicação da recomendação** — testar recomendação de origem `revisao` e outra origem (`adaptive`);
2. **Estudar Agora V5** — conferir o card recomendado nos dois estados quando disponíveis;
3. **Próxima recomendação** — conferir o `studyActionCard` sem `actionRole`;
4. **Fechamento semanal** — conferir os três `studyActionCard` sem `actionRole`;
5. confirmar que fundo, borda, raio, espaçamento e tipografia permanecem visualmente iguais;
6. conferir o card de **Revisão Inteligente do Dashboard**, que deve permanecer inalterado;
7. conferir rapidamente Cards globais A, Busca Global e os retornos `← Voltar` para ausência de regressão.

---

## 11. Conclusão

**Cards globais — Bloco B implementado e aprovado pelas validações automatizadas.**

Este checkpoint ainda deve ser validado manualmente no Windows antes de se tornar a nova base oficial.

Após a validação manual, o próximo passo correto é uma **auditoria curta de Cards globais**, especificamente para decidir o destino de `myEvolutionStatCard`. Não deve ser presumido automaticamente um Bloco C.
