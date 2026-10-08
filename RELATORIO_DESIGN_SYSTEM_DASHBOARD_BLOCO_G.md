# VighnaStudy — Design System do Dashboard — Bloco G

## Relatório de implementação, regressão e checkpoint

**Base de entrada:** `VighnaStudy_0.29.59_DesignSystem_Dashboard_Bloco_F_COMPLETO.zip`
**SHA-256 da base:** `1a9e759c60f6bbd53c6c751456e4e3842284fa75cd4eb60a20a5292a482372dc`
**Versão:** `0.29.59`
**Build:** `calendar-week-forecast-v1`
**Schema:** `25`
**Escopo:** Dashboard — **Estudo por questões**
**Método:** caracterização isolada, migração visual aditiva, escopo estrito, preservação de comportamento, prova de reversibilidade, comparação de cascata, regressão cumulativa e validação do banco.

---

## 1. Estado de partida

O Bloco F era o checkpoint validado manualmente no Windows. Antes do Bloco G, o Design System possuía:

- **102 tokens semânticos**;
- **782 tokens de componente**;
- **884 tokens totais**.

Hashes canônicos do QSS da base F:

- Claro: `197d1f1051896765152d637943a3c2c0660b81a4514f58a01867377a3144bebd`
- Escuro: `922d7951bf5edde14ab712112aff8484510bb48702e8f5307e6bef6476c6b1f5`
- Futurista: `dd3fb829eae39970f600047328bb905878f3a152b8b40eef44f9b4fa872a214b`

`main.py`, o banco, a versão, o build e o schema foram tratados como protegidos.

---

## 2. Caracterização prévia

A caracterização foi registrada em:

`RELATORIO_DESIGN_SYSTEM_DASHBOARD_BLOCO_G_CARACTERIZACAO.md`

O recorte foi limitado a:

`QWidget#dashboardRoot QFrame#studyNowPanel`

Foram incluídos:

- cabeçalho recolhível **Estudo por questões**;
- resumo do banco de questões;
- **Revisão Inteligente**;
- **Treino Adaptativo**;
- **Simulado**;
- **Banco de Erros**;
- rodapé **Modo manual**.

A persistência `dashboard_secao_estudar_expandida`, os cálculos, a disponibilidade das ações, a fila de revisão, o treino adaptativo, a criação do simulado, o Banco de Erros e o gerenciamento manual permanecem fora do Design System e não foram alterados.

### Risco de objectNames compartilhados

Foram confirmados nomes reutilizados fora do painel, entre eles `studyNowIcon`, `studyActionCard`, `studyActionTitle`, `adaptiveDashboardButton`, `mockExamDashboardButton` e `subtleButton`.

Por isso, **toda a nova camada é descendente de `#dashboardRoot #studyNowPanel`**. Não foi criada regra global nova para esses consumidores.

---

## 3. Implementação realizada

Foi criada a camada aditiva:

`ESTILO_DASHBOARD_BLOCO_G`

Ela é renderizada **depois do Bloco F** nos três temas.

Foram acrescentados **61 tokens de componente**:

- **55 tokens de cor**;
- **6 tokens de gradiente**.

O Design System passa para:

- **102 tokens semânticos**;
- **843 tokens de componente**;
- **945 tokens totais**.

A estimativa da caracterização era de aproximadamente 60–70 contratos, portanto o resultado final permanece dentro do orçamento previsto.

A família criada é:

`dashboard.study_questions_*`

Foram centralizados somente os valores efetivamente vencedores da cascata. Nos temas Claro/Escuro, contratos que precisam compartilhar a mesma API de gradiente com o Futurista usam gradientes planos de dois stops idênticos; isso mantém a aparência sólida existente.

O estado `disabled` dos `subtleButton` foi preservado sem criar uma aparência artificial: a cascata anterior não possuía override cromático separado para esse estado nesse recorte, portanto o botão desabilitado continua recebendo o contrato normal somado ao comportamento nativo do Qt.

---

## 4. Arquivos de produção alterados

A implementação de produção ficou restrita a quatro arquivos:

- `ui/design/tokens.py` — novos contratos `dashboard.study_questions_*`;
- `ui/design/palette.py` — valores físicos necessários ainda ausentes da paleta central;
- `ui/design/themes.py` — mapeamentos de Claro, Escuro e Futurista;
- `tema.py` — nova camada QSS tokenizada e composição após o Bloco F.

Não houve alteração em:

- `main.py`;
- `estudos.db`;
- `versao.py`;
- `foco.py`;
- `jogos.py`;
- `checkpoint.py`.

Os testes de snapshot existentes foram atualizados apenas onde necessário para reconhecer a nova contagem global, os novos hashes finais e a existência de uma camada G posterior aos checkpoints A–F.

---

## 5. Equivalência visual da cascata

Foi executada uma comparação programática entre o QSS final do checkpoint F e o QSS após o Bloco G, modelando **46 consumidores/estados do painel** nos três temas.

Foram comparadas as propriedades visuais relevantes:

- `background` / `background-color`;
- `color`;
- `border-color` / cor efetiva de `border`.

A normalização considera equivalentes representações sintaticamente diferentes do mesmo valor, incluindo `rgba(r,g,b,a)` e hexadecimal ARGB, além de gradientes planos de stops idênticos versus superfície sólida.

**Resultado: 0 diferenças visuais materiais.**

Isso cobre, entre outros:

- painel e cabeçalho;
- estado recolhido e hover do cabeçalho;
- resumo do banco;
- Revisão Inteligente;
- botão Revisar normal/hover/disabled;
- Treino Adaptativo e CTA normal/hover;
- Simulado, badge, estatísticas e CTA normal/hover;
- Banco de Erros;
- rodapé Modo manual;
- `subtleButton` normal/hover.

### Isolamento

A própria estrutura da camada foi auditada: todos os seletores novos permanecem sob `#dashboardRoot #studyNowPanel`. Assim, objectNames compartilhados em importação, relatórios, recomendações, Resolvedor e outras telas não recebem a camada G.

---

## 6. Hashes QSS após o Bloco G

Hashes canônicos do QSS renderizado final:

- Claro: `d0e0149638447e981bdaa0a7099f57ba3d95654808992f52da98ad984b0c4de2`
- Escuro: `4df67944497bf40a3246ec85d3e863411378936bace30f582d5e28f612f8b166`
- Futurista: `1227869ce6d10ab4068e13dacd71bb37be8f009a6d22380b2218ed66382e502b`

Nos três temas há **0 marcadores `{{color:...}}` ou `{{gradient:...}}` não resolvidos**.

### Prova de reversibilidade

Retirando somente a camada G:

- Claro recupera exatamente o hash do checkpoint F;
- Escuro recupera exatamente o hash do checkpoint F;
- Futurista recupera exatamente o hash do checkpoint F após retirar a camada G final e a camada G escura herdada.

Portanto, o Bloco G permanece aditivo e isolável.

---

## 7. Testes específicos do Bloco G

Foi criado:

`test_design_system_dashboard_bloco_g.py`

**Resultado: 9/9 testes aprovados.**

A suíte valida:

- orçamento final de 61 novos tokens;
- 55 cores e 6 gradientes;
- valores representativos dos três temas;
- gradientes Futuristas;
- ausência de cores/gradientes hardcoded na camada G;
- escopo estrito de todos os seletores;
- consumidores e estados ativos no `main.py`;
- proteção dos objectNames compartilhados;
- QSS final sem tokens pendentes;
- hashes finais;
- rollback exato ao checkpoint F;
- hashes de arquivos protegidos;
- versão, build e schema;
- ordem F → G na composição dos três temas.

---

## 8. Bateria dirigida cumulativa

Foram executadas conjuntamente as suítes:

- Dashboard Blocos A, B, C, D, E, F e G;
- Jogos Passo 5;
- feedback/explicação B2g;
- Resumo Final Passo A;
- Resumo Final Passo B.

**Resultado: 95/95 testes aprovados.**

---

## 9. Suíte ampla comparada ao checkpoint F

Foi usada a mesma instrumentação Linux com stub mínimo de Qt para comparar os dois checkpoints.

### Checkpoint F

- **239 testes** executados;
- **6 falhas históricas**;
- **7 erros ambientais/Qt**.

### Bloco G

- **248 testes** executados;
- **6 falhas históricas**;
- **7 erros ambientais/Qt**.

As nove verificações acrescentadas pelo Bloco G passaram. As seis falhas continuam sendo exatamente as do teste histórico `test_design_system_resolvedor_enunciado_b2f.py`. Os sete erros também são os mesmos da base quando executada com a mesma instrumentação, decorrentes da ausência de uma instalação PySide6/Qt completa e do isolamento desse ambiente.

**O Bloco G não acrescentou falha nem erro de regressão à suíte ampla.**

---

## 10. Banco e arquivos protegidos

Validação em modo somente leitura:

- `PRAGMA integrity_check`: **ok**;
- `PRAGMA foreign_key_check`: **0 violações**.

Hashes confirmados, byte a byte:

- `main.py`: `be93709926ac1e4c783468d7409afcfe6b3de200b289f0f0b13f9fc0359defb1`
- `estudos.db`: `034940a33ea792957d8fafbf5c528db7cd895db69031696fbdd3f0a0ce5a41ef`
- `versao.py`: `8436214451a591c0a3d3429f62d53c0c01cfc0cc7311d71e57fcf060f5b39642`
- `foco.py`: `8fbe4659f3371683738a3fa239a789b3bca26ab47dc68f38a69829a33afd03ed`
- `jogos.py`: `498aab65a2a13efa070ae2f912536b5ddc1aada31e23a28846def6a617492286`
- `checkpoint.py`: `947295fdf2035d6f65d5d43f70e1d6e5e1c411d92eaca264a469a221b6b61c38`

Metadados preservados:

- versão `0.29.59`;
- build `calendar-week-forecast-v1`;
- schema `25`.

---

## 11. Validação manual obrigatória no Windows

A implementação está aprovada automaticamente, mas o Bloco G só deve ser marcado como concluído após a validação real no Windows.

Checklist:

1. conferir **Estudo por questões** expandido e recolhido nos temas Claro, Escuro e Futurista;
2. conferir hover do cabeçalho e persistência do estado expandido/recolhido;
3. conferir as quatro métricas do resumo do banco;
4. conferir Revisão Inteligente com conteúdo e sem conteúdo, inclusive botão Revisar habilitado/desabilitado;
5. abrir Revisão e confirmar o comportamento existente;
6. conferir Treino Adaptativo e hover do CTA; abrir o modo;
7. conferir Simulado, badge, três estatísticas e hover do CTA; abrir o modo;
8. conferir Banco de Erros e abrir **Praticar**;
9. conferir o rodapé Modo manual e os hovers de **Escolher manualmente** e **Gerenciar banco**;
10. confirmar que importação, relatório estratégico, recomendações, Resolvedor e demais telas que reutilizam objectNames como `subtleButton`, `adaptiveDashboardButton` e `mockExamDashboardButton` não sofreram alteração visual;
11. confirmar que os Blocos A–F do Dashboard continuam visual e funcionalmente inalterados.

---

## 12. Status

**IMPLEMENTAÇÃO AUTOMÁTICA APROVADA.**

Pendente somente:

**validação manual no Windows pelo usuário.**

Após essa confirmação, `VighnaStudy_0.29.59_DesignSystem_Dashboard_Bloco_G_COMPLETO.zip` pode se tornar o novo checkpoint oficial.
