# VighnaStudy — Design System do Dashboard — Bloco H

## Relatório de implementação, regressão e checkpoint

**Base de entrada:** `VighnaStudy_0.29.59_DesignSystem_Dashboard_Bloco_G_COMPLETO.zip`
**SHA-256 da base:** `dbea3edad4bad49d58aaa549353bfc789c07707aefb2f2c81844a3da64d1cbee`
**Versão:** `0.29.59`
**Build:** `calendar-week-forecast-v1`
**Schema:** `25`
**Escopo:** Dashboard — **Disciplinas e acabamento inferior**
**Método:** caracterização isolada, migração cromática aditiva, exceção mínima auditada em `main.py` para o estado desligado, preservação de comportamento, prova de reversibilidade, comparação de cascata, regressão cumulativa e validação do banco.

---

## 1. Estado de partida

O Bloco G era o checkpoint validado manualmente no Windows. Antes do Bloco H, o Design System possuía:

- **102 tokens semânticos**;
- **843 tokens de componente**;
- **945 tokens totais**.

Hashes canônicos do QSS da base G:

- Claro: `d0e0149638447e981bdaa0a7099f57ba3d95654808992f52da98ad984b0c4de2`
- Escuro: `4df67944497bf40a3246ec85d3e863411378936bace30f582d5e28f612f8b166`
- Futurista: `1227869ce6d10ab4068e13dacd71bb37be8f009a6d22380b2218ed66382e502b`

A caracterização definiu uma exceção controlada em relação aos Blocos F e G: `main.py` poderia receber **somente** a substituição dos nove valores cromáticos inline das disciplinas desligadas por chamadas a `qss_color()`, além do import necessário.

---

## 2. Caracterização prévia

A caracterização está registrada em:

`RELATORIO_DESIGN_SYSTEM_DASHBOARD_BLOCO_H_CARACTERIZACAO.md`

O recorte ativo foi formalizado como:

**Dashboard — Bloco H: Disciplinas e acabamento inferior**

Consumidores incluídos:

- `dashboardCenterBar`;
- `dashboardSectionToggleCentered`;
- `sectionEditButton`;
- `disciplineButton`;
- estado inline das disciplinas desligadas.

Ficaram explicitamente fora:

- `dashboardCollapsibleContent`, por ser compartilhado com outras seções;
- `priorityQueuePanel`, porque permanece deliberadamente oculto e dormente;
- `JanelaDisciplinas` e a tela de detalhe de disciplina;
- geometria, layout, persistência e comportamento funcional.

---

## 3. Implementação realizada

Foi criada a camada aditiva:

`ESTILO_DASHBOARD_BLOCO_H`

Ela é composta **depois do Bloco G** nos três temas.

Foram acrescentados exatamente **21 tokens de componente**, todos de cor:

- **21 tokens de cor**;
- **0 tokens de gradiente**.

O Design System passa para:

- **102 tokens semânticos**;
- **864 tokens de componente**;
- **966 tokens totais**.

A família criada é:

`dashboard.disciplines_*`

Contratos centralizados:

- superfície e borda do cabeçalho;
- texto e hover do título;
- normal/hover/pressed do botão **Edição**;
- normal/hover dos botões de disciplina;
- superfície/texto/borda do estado **desligado**.

Nenhum gradiente histórico sem efeito visual foi promovido a token.

---

## 4. Arquivos de produção alterados

A implementação de produção ficou limitada a:

- `ui/design/tokens.py` — 21 novos contratos `dashboard.disciplines_*`;
- `ui/design/palette.py` — somente valores físicos ainda ausentes da paleta central;
- `ui/design/themes.py` — mapeamentos Claro, Escuro e Futurista;
- `tema.py` — nova camada QSS tokenizada H e composição após G;
- `main.py` — **exceção mínima previamente autorizada**, apenas no estado desligado.

### Diff autorizado de `main.py`

O diff em `main.py` contém apenas:

1. adição de `qss_color` ao import de `ui.design`;
2. substituição dos três valores físicos de cor em cada um dos três ramos de tema da disciplina desligada por tokens:
   - `dashboard.disciplines_disabled_surface`;
   - `dashboard.disciplines_disabled_text`;
   - `dashboard.disciplines_disabled_border`.

A ramificação `futurista / escuro / else`, o `setStyleSheet()` inline, `text-align:left`, `padding-left:14px`, texto `• desligada`, tooltip, clique e ordem de execução permaneceram intactos.

A prova automatizada reverte exatamente essas duas mudanças e recupera o hash do `main.py` do checkpoint G:

`be93709926ac1e4c783468d7409afcfe6b3de200b289f0f0b13f9fc0359defb1`

Novo hash do `main.py` após H:

`08a1be37f347f4e79dff2587e259323259c855ea360d9a507b62aacc65a259bf`

---

## 5. Equivalência visual da cascata

Foi executada comparação programática entre o QSS final do checkpoint G e o QSS após H nos três temas.

Consumidores/estados comparados:

- `dashboardCenterBar`;
- título normal;
- título hover;
- título recolhido;
- título recolhido + hover;
- **Edição** normal;
- **Edição** hover;
- **Edição** pressed;
- conteúdo compartilhado;
- disciplina ativa normal;
- disciplina ativa hover;
- label do estado vazio.

**Resultado: 0 diferenças visuais materiais.**

O estado desligado foi validado separadamente pela resolução exata de `qss_color()` nos três ramos de tema, preservando os mesmos valores físicos caracterizados.

### Isolamento

Todos os seletores novos da camada H permanecem sob `QWidget#dashboardRoot`. A camada:

- não contém `dashboardCollapsibleContent`;
- não contém `priorityQueuePanel`;
- não contém hexadecimal, `rgba()` ou `qlineargradient` hardcoded.

---

## 6. Hashes QSS após o Bloco H

Hashes canônicos do QSS renderizado final:

- Claro: `cef0365e8cdd703fc73df505529d0e97672e5c49f036c0cba3b7ee50d42f23fe`
- Escuro: `5e365d9be91deb9d29532b8954c4cc8d66acf8142f019d3706aafba0a3e548cb`
- Futurista: `edc56b82ac5c720c06dac89700ec039d4d62536a31709d881ff1078960605dce`

Nos três temas há **0 marcadores `{{color:...}}` ou `{{gradient:...}}` não resolvidos**.

### Prova de reversibilidade

Retirando somente a camada H:

- Claro recupera exatamente o hash do checkpoint G;
- Escuro recupera exatamente o hash do checkpoint G;
- Futurista recupera exatamente o hash do checkpoint G após retirar a camada H final e a camada H escura herdada.

A alteração mínima de `main.py` também possui prova de reversão exata ao hash G.

---

## 7. Testes específicos do Bloco H

Foi criado:

`test_design_system_dashboard_bloco_h.py`

**Resultado: 9/9 testes aprovados.**

A suíte valida:

- 966 tokens totais e 864 de componente;
- exatamente 21 novos tokens H de cor e 0 gradientes;
- valores representativos dos três temas;
- escopo estrito e ausência de hardcodes na camada H;
- ausência de captura de `dashboardCollapsibleContent` e `priorityQueuePanel`;
- consumidores e comportamento protegido no `main.py`;
- diff mínimo autorizado de `main.py` e rollback exato ao hash G;
- nove resoluções `qss_color()` do estado desligado;
- QSS final sem tokens pendentes;
- hashes finais;
- rollback QSS exato ao checkpoint G;
- hashes de arquivos protegidos;
- versão, build e schema;
- ordem G → H na composição dos três temas.

---

## 8. Bateria dirigida cumulativa

Foram executadas conjuntamente as suítes já protegidas, incluindo Dashboard A–H e os recortes cumulativos relacionados.

**Resultado: 104/104 testes aprovados.**

Nenhuma regressão dirigida foi introduzida.

---

## 9. Suíte ampla comparada ao checkpoint G

Foi utilizada a mesma instrumentação Linux/stub usada no checkpoint anterior.

### Checkpoint G

- **248 testes**;
- **6 falhas históricas**;
- **7 erros ambientais/Qt**.

### Bloco H

- **257 testes**;
- **6 falhas históricas**;
- **7 erros ambientais/Qt**.

As nove verificações acrescentadas pelo Bloco H passaram. As seis falhas continuam restritas ao teste histórico do Resolvedor B2f. Os sete erros permanecem nas mesmas categorias ambientais/Qt do checkpoint G.

**O Bloco H não acrescentou falha nem erro de regressão à suíte ampla.**

---

## 10. Banco, compilação e arquivos protegidos

Validação do banco em modo somente leitura:

- `PRAGMA integrity_check`: **ok**;
- `PRAGMA foreign_key_check`: **0 violações**.

Compilação estática dos arquivos de produção alterados:

- `main.py`: **OK**;
- `tema.py`: **OK**;
- `ui/design/tokens.py`: **OK**;
- `ui/design/themes.py`: **OK**;
- `ui/design/palette.py`: **OK**.

Arquivos que permaneceram byte a byte idênticos ao checkpoint G:

- `estudos.db`: `034940a33ea792957d8fafbf5c528db7cd895db69031696fbdd3f0a0ce5a41ef`;
- `versao.py`: `8436214451a591c0a3d3429f62d53c0c01cfc0cc7311d71e57fcf060f5b39642`;
- `foco.py`: `8fbe4659f3371683738a3fa239a789b3bca26ab47dc68f38a69829a33afd03ed`;
- `jogos.py`: `498aab65a2a13efa070ae2f912536b5ddc1aada31e23a28846def6a617492286`;
- `checkpoint.py`: `947295fdf2035d6f65d5d43f70e1d6e5e1c411d92eaca264a469a221b6b61c38`.

Metadados preservados:

- versão `0.29.59`;
- build `calendar-week-forecast-v1`;
- schema `25`.

---

## 11. `priorityQueuePanel`

A decisão da caracterização foi preservada integralmente.

`priorityQueuePanel` continua:

- existente por compatibilidade histórica;
- explicitamente oculto;
- fora da camada H;
- sem novos tokens próprios.

Sua classificação definitiva deve ocorrer na auditoria de encerramento do Dashboard, não nesta implementação.

---

## 12. Validação manual obrigatória no Windows

A implementação está aprovada automaticamente, mas o Bloco H só deve ser marcado como concluído após validação real no Windows.

Checklist:

1. abrir/recolher **Disciplinas** em Claro, Escuro e Futurista e confirmar persistência;
2. conferir hover do título;
3. conferir **Edição** em normal, hover e pressed e abrir a janela de edição;
4. conferir pelo menos uma disciplina ativa em normal/hover e abrir a disciplina;
5. conferir uma disciplina desligada, inclusive `• desligada`, tooltip e clique;
6. se viável, desligar/reativar uma disciplina e confirmar o recarregamento visual;
7. conferir o estado sem disciplinas apenas se houver perfil adequado;
8. confirmar que `priorityQueuePanel` continua invisível;
9. confirmar que os Blocos A–G permanecem visual e funcionalmente inalterados.

---

## 13. Status

**IMPLEMENTAÇÃO AUTOMÁTICA APROVADA.**

Pendente somente:

**validação manual no Windows pelo usuário.**

Após essa confirmação, `VighnaStudy_0.29.59_DesignSystem_Dashboard_Bloco_H_COMPLETO.zip` pode se tornar o novo checkpoint oficial.

O passo seguinte não deve ser a criação automática de um Bloco I. Deve ser executada uma **auditoria de encerramento do macroescopo Dashboard** para decidir, com base no código real, se o Dashboard pode ser formalmente fechado ou se ainda existe consumidor visual ativo não centralizado.
