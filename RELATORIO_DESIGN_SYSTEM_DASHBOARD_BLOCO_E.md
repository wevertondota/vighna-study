# VighnaStudy — Design System do Dashboard — Bloco E

## Relatório de implementação, regressão e checkpoint

**Base de entrada:** `VighnaStudy_0.29.59_DesignSystem_Dashboard_Bloco_D_COMPLETO.zip`
**Versão:** `0.29.59`
**Build:** `calendar-week-forecast-v1`
**Schema:** `25`
**Escopo:** Dashboard — **Notificações e alertas**
**Método:** caracterização antes da alteração, migração visual aditiva, preservação de comportamento, comparação de cascata, hashes, testes e validação de banco.

---

## 1. Estado de partida

O Bloco D já havia sido validado manualmente no Windows. Assim, o trabalho deste bloco partiu diretamente desse checkpoint, sem refazer A, B, C ou D.

Antes do Bloco E, o Design System possuía:

- **102 tokens semânticos**;
- **622 tokens de componente**;
- **724 tokens totais**.

Os hashes canônicos do QSS da base D eram:

- Claro: `67eb7f0c5eee80785bbe7595d4ca9374c9fc2985b34034ede312c06e69e49e08`
- Escuro: `1109df37ba34574f0607dd9ee3839a770c74aed8906dece461e9c2e8b81f7624`
- Futurista: `07717d507c118a34f4b8ca7c62556c60a8b0fdc874f7d30f379d19b4ed379d6c`

---

## 2. Caracterização prévia

Antes da implementação foi produzido o relatório:

`RELATORIO_DESIGN_SYSTEM_DASHBOARD_BLOCO_E_CARACTERIZACAO.md`

A leitura do código confirmou que o bloco ativo de Notificações utiliza os seguintes contratos visuais:

- `dashboardNotificationsPanel`;
- `dashboardGroupToggle`, exclusivamente quando descendente do painel de notificações;
- `dashboardNotificationsSubtitle`;
- `dashboardCollapsibleContent`;
- `dashboardAttentionCard` com `attentionRole="priority"` e `attentionRole="pace"`;
- `dashboardAttentionIcon`;
- `dashboardAttentionEyebrow`;
- `dashboardAttentionTitle`;
- `dashboardAttentionDescription`;
- `dashboardAttentionMeta`;
- `dashboardAttentionBadge`;
- `dashboardPaceBadge`;
- `syllabusAlertButton`;
- `syllabusForecastButton`;
- `dashboardAttentionFooter`;
- `dashboardAttentionFooterItem`;
- `dashboardAttentionFooterHint`.

### Estados preservados

O card prioritário mantém a propriedade dinâmica `alertState`, com os estados existentes:

- `monitorar`;
- `atencao`;
- `critico`;
- `ok`.

A persistência da seção também foi preservada:

`dashboard_secao_notificacoes_expandida`

O comportamento que pode expandir automaticamente a seção diante de alerta crítico não foi modificado.

### Seletores antigos não promovidos a contrato

A caracterização encontrou seletores sem consumidor ativo em `main.py`, entre eles:

- `dashboardNoticeRow`;
- `dashboardNoticeLabel`;
- `dashboardNoticeTitle`;
- `dashboardNoticeIcon`;
- `dashboardNoticeDescription`;
- `dashboardNoticeSummary`;
- variantes antigas de `dashboardNotificationsTitle`, `dashboardNotificationsMenu` e `dashboardNotificationsFooter`.

Eles **não foram migrados** para o novo Design System. Isso evita transformar código visual órfão em API permanente.

---

## 3. Implementação realizada

A implementação criou uma nova camada:

`ESTILO_DASHBOARD_BLOCO_E`

A camada foi anexada depois do Bloco D e permanece estritamente escopada ao painel:

`QWidget#dashboardRoot QFrame#dashboardNotificationsPanel`

Nenhuma regra global foi criada para `dashboardGroupToggle`; o seletor compartilhado só é atingido dentro do módulo de Notificações.

O Bloco E adicionou **61 tokens de componente**, todos de cor. Nenhum novo gradiente foi necessário.

Após a implementação, o Design System passou para:

- **102 tokens semânticos**;
- **683 tokens de componente**;
- **785 tokens totais**.

Os 61 contratos cobrem:

- superfície/borda do painel;
- texto e hover do cabeçalho recolhível;
- subtítulo;
- superfícies e bordas dos estados prioritários;
- ícone dos estados normal/ok/crítico;
- eyebrow, título, descrição e metadados;
- badges normal/ok/crítico;
- botão de alerta normal/hover/desabilitado;
- card de ritmo;
- ícone e badge de ritmo;
- botão de previsão normal/hover/desabilitado;
- rodapé, itens e hint.

---

## 4. Arquivos de produção alterados

Em relação ao ZIP D, apenas quatro arquivos de produção foram modificados:

- `ui/design/tokens.py`;
- `ui/design/themes.py`;
- `ui/design/palette.py`;
- `tema.py`.

Não houve alteração funcional em:

- `main.py`;
- `estudos.db`;
- `versao.py`;
- `foco.py`;
- `jogos.py`;
- `checkpoint.py`.

Também não houve alteração de versão, build ou schema.

### Hashes dos arquivos protegidos

- `main.py`: `be93709926ac1e4c783468d7409afcfe6b3de200b289f0f0b13f9fc0359defb1`
- `estudos.db`: `034940a33ea792957d8fafbf5c528db7cd895db69031696fbdd3f0a0ce5a41ef`
- `versao.py`: `8436214451a591c0a3d3429f62d53c0c01cfc0cc7311d71e57fcf060f5b39642`
- `foco.py`: `8fbe4659f3371683738a3fa239a789b3bca26ab47dc68f38a69829a33afd03ed`
- `jogos.py`: `498aab65a2a13efa070ae2f912536b5ddc1aada31e23a28846def6a617492286`
- `checkpoint.py`: `947295fdf2035d6f65d5d43f70e1d6e5e1c411d92eaca264a469a221b6b61c38`

---

## 5. Equivalência visual da cascata

Foi feita uma comparação automatizada entre a cascata efetiva legada e a nova camada tokenizada para as propriedades visuais do módulo.

Após normalização das formas equivalentes de cor — inclusive conversão de `rgba(...)` para a forma canônica usada pelo Qt — o comparador encontrou:

**0 diferenças nas propriedades-alvo.**

Isso confirma que o Bloco E centralizou os valores no Design System sem redesenhar intencionalmente o módulo.

Os estados `monitorar` e `atencao` permanecem visualmente equivalentes porque essa é a situação da base atual; ambos foram explicitados no contrato para permitir evolução futura sem depender de coincidência implícita.

---

## 6. Hashes QSS após o Bloco E

Hashes canônicos do QSS renderizado final:

- Claro: `81f1c8fc6eebb10cd8dccea854795798f3871a11da372eea4baf02b5f71eb2c4`
- Escuro: `ef56315047f797aabc02a33118b97a4f6992c775e696c9b1d61509030df45186`
- Futurista: `29e36ecb0c7cbb06dfe15821c7c07b84ad6a81dc75a48f2d5fe56db70fe9079d`

Foi executada também a prova inversa: retirando somente a camada E do QSS final, os hashes recuperam **exatamente** o checkpoint D nos três temas.

Isso demonstra que a alteração visual deste bloco é aditiva e isolável.

---

## 7. Testes específicos do Bloco E

Foi criado `test_design_system_dashboard_bloco_e.py` com **9 testes**, todos aprovados.

A suíte verifica, entre outros pontos:

- orçamento e contagem exatos dos novos tokens;
- valores de cor dos três temas;
- escopo estrito do novo QSS;
- estados `monitorar`, `atencao`, `critico` e `ok`;
- consumidores ativos e persistência existente;
- não migração dos seletores órfãos;
- ausência de marcadores de token não resolvidos;
- novos hashes do QSS;
- recuperação exata do checkpoint D ao retirar a camada E;
- preservação dos arquivos protegidos e dos metadados.

---

## 8. Bateria dirigida cumulativa

Foram executadas em conjunto as suítes de:

- Dashboard Bloco A;
- Dashboard Bloco B;
- Dashboard Bloco C;
- Dashboard Bloco D;
- Dashboard Bloco E;
- Jogos Passo 5;
- feedback/explicação B2g;
- Resumo Final Passo A;
- Resumo Final Passo B.

**Resultado: 77/77 testes aprovados.**

Os testes históricos cumulativos foram atualizados somente para reconhecer a nova contagem global, o snapshot QSS vigente ou para retirar a camada E antes de validar checkpoints anteriores. Seus contratos históricos foram mantidos.

---

## 9. Suíte histórica ampla

Foi executado o conjunto `test_design_system*.py`.

**Total: 230 testes.**

Resultado:

- **6 falhas**;
- **6 erros**.

Esse saldo é o mesmo da base D, acrescido apenas dos 9 testes novos aprovados do Bloco E. As seis falhas continuam concentradas no contrato histórico `test_design_system_resolvedor_enunciado_b2f.py`; os seis erros continuam ligados às limitações Qt do ambiente de teste sem `PySide6.QtGui` completo.

Portanto, o Bloco E **não acrescentou nova falha nem novo erro de regressão** à suíte histórica.

---

## 10. Banco, compilação e renderização

Validações concluídas:

- `py_compile` dos módulos principais e de `ui/design`: **aprovado**;
- `PRAGMA integrity_check`: **ok**;
- `PRAGMA foreign_key_check`: **0 violações**;
- Claro, Escuro e Futurista: **nenhum marcador `{{color:...}}` ou `{{gradient:...}}` não resolvido**.

A implementação não realizou escrita intencional no banco.

---

## 11. Validação manual recomendada no Windows

Após executar `atualizar_exe.bat`, validar os três temas — **Claro, Escuro e Futurista** — observando especialmente:

1. abrir e recolher **Notificações e alertas** e confirmar a persistência do estado;
2. conferir o estado sem alerta (`ok`) e o botão de alerta desabilitado;
3. conferir, quando houver dados compatíveis, os estados `monitorar`/`atencao` e `critico`;
4. no estado crítico, confirmar que o comportamento de abertura automática continua funcionando;
5. conferir o card de ritmo e seu badge;
6. testar **Abrir progresso** / previsão nos estados habilitado e desabilitado;
7. conferir o rodapé de sinais e seus textos;
8. alternar entre Claro, Escuro e Futurista para detectar qualquer vazamento de estilo para outros módulos.

Alguns estados dependem dos dados atuais do perfil e podem não surgir naturalmente em uma única execução.

---

## 12. Delimitação do bloco

O Bloco E não migrou:

- Planejamento completo;
- Estudo por questões;
- Disciplinas/acabamento;
- componentes desenhados por `QPainter`;
- seletores órfãos do Dashboard;
- lógica de alertas ou algoritmo de prioridade.

Esses itens permanecem para etapas posteriores, conforme o roadmap do Dashboard.

Com a validação manual aprovada, o próximo recorte previsto é o **Bloco F — Planejamento completo**.
