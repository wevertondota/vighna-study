# VighnaStudy — Design System do Dashboard — Bloco I

## Relatório de implementação, regressão e checkpoint

**Base de entrada:** `VighnaStudy_0.29.59_DesignSystem_Dashboard_Bloco_H_COMPLETO.zip`
**SHA-256 da base:** `935e6ce9ad5af642556d4205b12d5d995c1b20c26643e0b4b0a06260da53af3e`
**Versão:** `0.29.59`
**Build:** `calendar-week-forecast-v1`
**Schema:** `25`
**Escopo:** Dashboard — **Bloco I: componentes QPainter ativos**
**Origem do escopo:** auditoria de encerramento do Dashboard após o Bloco H.

---

## 1. Motivo do Bloco I

A auditoria de encerramento do Dashboard concluiu que os Blocos A–H cobriam o QSS ativo do Dashboard, mas ainda existiam dois consumidores visuais ativos com cores físicas locais em `paintEvent()`:

1. `DashboardPlanningArcWidget`, no card **Planejamento de hoje**;
2. `DashboardDonutWidget`, no card **Qualidade do aprendizado**.

Nenhum outro painel foi incluído neste bloco. `priorityQueuePanel` permanece explicitamente oculto/dormente e não foi alterado.

---

## 2. Implementação realizada

Foram acrescentados exatamente **6 tokens de componente**, todos de cor e sem gradientes:

- `dashboard.planning_arc_track` → `#52CFF3E1`;
- `dashboard.planning_arc_fill` → `#B9FFE3`;
- `dashboard.planning_arc_text` → `#F4FFFA`;
- `dashboard.quality_donut_track_dark` → `#263B4F`;
- `dashboard.quality_donut_track_light` → `#DCE5ED`;
- `dashboard.quality_donut_fill` → `#2FB4C7`.

Os seis contratos possuem os mesmos valores físicos nos temas Claro, Escuro e Futurista, reproduzindo exatamente o comportamento anterior. A escolha entre trilha clara/escura do donut continua dependendo de `cor_texto.lightness() > 150`.

O Design System passa de:

- **102 tokens semânticos**;
- **864 tokens de componente**;
- **966 tokens totais**;

para:

- **102 tokens semânticos**;
- **870 tokens de componente**;
- **972 tokens totais**.

No domínio `dashboard.*`, o total passa para **458 tokens**, sendo **413 cores** e **45 gradientes**.

---

## 3. Arquivos de produção alterados

A alteração de produção ficou limitada a:

- `main.py` — troca apenas da origem das cores dos dois `paintEvent()`;
- `ui/design/tokens.py` — seis novos contratos de componente;
- `ui/design/palette.py` — quatro valores físicos ainda ausentes da paleta (`#52CFF3E1`, `#F4FFFA`, `#263B4F`, `#DCE5ED`); `#B9FFE3` e `#2FB4C7` já existiam;
- `ui/design/themes.py` — resolução dos seis tokens nos três temas;
- `DESIGN_SYSTEM.md` — documentação do consumo QPainter do Dashboard.

`tema.py` permaneceu byte a byte inalterado.

### Hashes de referência após o Bloco I

- `main.py`: `0ef8b3214a566cfaf1d329e84d701bb0ca776b15bdf2e647dccbc6e4fb2a7cb7`;
- `tema.py`: `4184e806b6695f56bc7d3977bb2ac6d745de335850bade417a3c47aa9d18a105`;
- `ui/design/tokens.py`: `70bc61276e312a7d02e83dba4cdc8f121bcb8dd3d7c8ca761bde288dcb0b1223`;
- `ui/design/themes.py`: `ce761cd6d2a17c02035b0af05cad2c43b1cbb6ce8ae0e25c133db727ff63d911`;
- `ui/design/palette.py`: `fc4e44d632c2bc573562e52613326c82a613adee270b80aa1ca7df8c6c2476bb`.

---

## 4. Preservação estrita de comportamento e geometria

### `DashboardPlanningArcWidget`

Permaneceram inalterados:

- tamanho mínimo e máximo;
- cálculo de `largura`, `altura`, `x`, `y` e `QRectF`;
- largura de caneta `8`;
- `Qt.RoundCap`;
- arco-base de `180°`;
- cálculo `atual / meta`, clamp de 0 a 1 e arco proporcional;
- fonte Segoe UI, 16 pt, bold;
- texto central e alinhamento.

Somente `QColor(...)` foi substituído por `qcolor(tema_atual, token)`.

### `DashboardDonutWidget`

Permaneceram inalterados:

- tamanhos 128–150 px;
- margem `16`;
- construção do retângulo;
- uso da cor de texto derivada da palette do widget;
- decisão de trilha `lightness() > 150`;
- largura de caneta `11`;
- `Qt.RoundCap`;
- arco completo `360°`;
- início em `90°` e cálculo do arco de valor;
- fonte Segoe UI, 16 pt, bold;
- texto central e alinhamento.

Somente as cores físicas locais foram substituídas pelos tokens correspondentes.

---

## 5. Equivalência cromática e reversibilidade

A equivalência foi validada no nível dos valores físicos do Qt:

- `QColor(207, 243, 225, 82)` corresponde exatamente a `#52CFF3E1` no formato `#AARRGGBB` usado pelo Design System;
- `#B9FFE3`, `#F4FFFA`, `#263B4F`, `#DCE5ED` e `#2FB4C7` são reproduzidos literalmente pelos novos contratos.

O teste específico reverte somente as cinco substituições de código feitas no Bloco I e recupera exatamente o hash do `main.py` do checkpoint H:

`08a1be37f347f4e79dff2587e259323259c855ea360d9a507b62aacc65a259bf`

Como `tema.py` não foi alterado, os hashes canônicos do QSS permanecem exatamente os do Bloco H:

- Claro: `cef0365e8cdd703fc73df505529d0e97672e5c49f036c0cba3b7ee50d42f23fe`;
- Escuro: `5e365d9be91deb9d29532b8954c4cc8d66acf8142f019d3706aafba0a3e548cb`;
- Futurista: `edc56b82ac5c720c06dac89700ec039d4d62536a31709d881ff1078960605dce`.

Nos três temas permanecem **0 marcadores de token QSS não resolvidos**.

---

## 6. Testes

Foi criado:

`test_design_system_dashboard_bloco_i.py`

### Teste específico do Bloco I

**8/8 testes aprovados.**

A suíte verifica:

- orçamento exato de seis tokens;
- valores físicos nos três temas;
- alpha exato da trilha do arco;
- ausência de `QColor(...)` e hexadecimais físicos nos dois consumidores;
- preservação de geometria e lógica;
- rollback exato de `main.py` ao checkpoint H;
- `tema.py` byte a byte inalterado;
- arquivos protegidos e metadados;
- manutenção do `priorityQueuePanel` dormente.

### Bateria dirigida cumulativa

Foi executada a bateria composta por:

- fundação do Design System;
- controles compartilhados;
- Calendário;
- Dashboard A, B, C, D, E, F, G, H e I.

Com stub Qt mínimo apenas para os adaptadores no ambiente Linux sem PySide6:

**102/102 testes aprovados — 0 falhas e 0 erros.**

---

## 7. Banco, compilação e arquivos protegidos

Compilação estática aprovada para:

- `main.py`;
- `tema.py`;
- `ui/design/tokens.py`;
- `ui/design/themes.py`;
- `ui/design/palette.py`;
- `ui/design/adapters.py`.

Banco validado em leitura:

- `PRAGMA integrity_check` → **ok**;
- `PRAGMA foreign_key_check` → **0 violações**;
- SHA-256 `estudos.db` → `034940a33ea792957d8fafbf5c528db7cd895db69031696fbdd3f0a0ce5a41ef`.

Arquivos funcionais protegidos mantidos byte a byte:

- `versao.py`: `8436214451a591c0a3d3429f62d53c0c01cfc0cc7311d71e57fcf060f5b39642`;
- `foco.py`: `8fbe4659f3371683738a3fa239a789b3bca26ab47dc68f38a69829a33afd03ed`;
- `jogos.py`: `498aab65a2a13efa070ae2f912536b5ddc1aada31e23a28846def6a617492286`;
- `checkpoint.py`: `947295fdf2035d6f65d5d43f70e1d6e5e1c411d92eaca264a469a221b6b61c38`.

Versão, build e schema continuam `0.29.59`, `calendar-week-forecast-v1` e `25`.

---

## 8. Validação manual necessária no Windows

Antes de declarar o Dashboard encerrado, validar nos temas **Claro, Escuro e Futurista**:

1. card **Planejamento de hoje**: trilha semitransparente, arco preenchido e texto central;
2. progresso em 0%, parcial e completo, se os estados estiverem disponíveis;
3. card **Qualidade do aprendizado**: trilha, preenchimento do donut e texto central;
4. alternância dos três temas sem mudança de geometria, espessura ou alinhamento;
5. ausência de artefatos, flicker ou cores divergentes;
6. Blocos A–H permanecem normais;
7. **Revisões prioritárias** continua invisível.

O ambiente Linux atual não possui PySide6 real; portanto a equivalência automatizada deste bloco é contratual/estrutural e cromática. A confirmação final de renderização continua sendo a validação manual no Windows, como nos blocos anteriores.

---

## 9. Estado após implementação

**Bloco I implementado e aprovado pelas verificações automatizadas.**

O macroescopo Dashboard ainda não deve ser marcado como formalmente encerrado até a validação manual do Bloco I. Após essa confirmação, executar uma auditoria final curta com os bloqueios definidos em `RELATORIO_AUDITORIA_ENCERRAMENTO_DASHBOARD.md`. Se nenhum consumidor ativo físico reaparecer, o Dashboard poderá ser encerrado e o projeto seguirá para o próximo macroitem do Plano Mestre.
