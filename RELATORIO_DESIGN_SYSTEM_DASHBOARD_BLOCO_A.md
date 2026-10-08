# RELATÓRIO — DESIGN SYSTEM — DASHBOARD GERAL — BLOCO A

**Projeto:** VighnaStudy 0.29.59
**Build:** `calendar-week-forecast-v1`
**Schema:** `25`
**Base recebida:** `SistemaEstudos(7).zip`
**SHA-256 da base:** `028107fe96e79a2f23a1cd8871d2ea639b37a047a18b33960e74eb3eea50adf7`

## 1. Escopo executado

Foi implementado somente o **Bloco A — Shell e cabeçalho do Dashboard**, conforme a caracterização anterior.

Entraram no escopo visual:

- `dashboardPage`;
- `dashboardScroll`;
- `dashboardRoot`;
- `dashboardTopBar`;
- `pageTitle` e `pageSubtitle`;
- gatilho da busca global `globalSearchTrigger`;
- botão `questionsNavButton`;
- botões `subtleButton` existentes dentro do cabeçalho (`Retomar bateria` e `Gerenciar`);
- `topAccentButton` (configurações);
- `topProfileBar`;
- `topProfileLabel`;
- `topProfileCombo`.

Não foram migrados Foco, Pós-Foco, Planejamento, cards analíticos, fila/recomendação, calendário, jogos, Resolvedor, widgets `QPainter` nem seletores legados/órfãos do Dashboard.

## 2. Estratégia adotada

A implementação foi feita de forma aditiva e conservadora. O código de construção do Dashboard em `main.py` não foi alterado.

Foram criados contratos próprios do Dashboard no Design System e três camadas QSS finais, uma por tema, estritamente escopadas ao shell/cabeçalho. Elas alteram somente propriedades cromáticas já caracterizadas e deixam layout, dimensões, raios, padding, tipografia, sinais, slots, atalhos, visibilidade, persistência e regras de negócio sob responsabilidade do código já existente.

As camadas foram acrescentadas ao final dos stylesheets de Claro, Escuro e Futurista. Como o Futurista historicamente deriva do stylesheet Escuro, ele recebe a camada escura pela própria arquitetura existente e, ao final, a camada futurista específica a sobrescreve. Há teste explícito garantindo essa composição e a reversibilidade para o baseline anterior.

## 3. Design System

### Antes

- Tokens semânticos: **102**
- Tokens de componente: **412**
- Total: **514**

### Depois

- Tokens semânticos: **102**
- Tokens de componente: **453**
- Total: **555**

Crescimento do Bloco A: **41 tokens**, sendo:

- **38 tokens de cor**;
- **3 tokens de gradiente**.

Os novos contratos cobrem canvas, título/subtítulo, topbar, barra e seletor de perfil, busca, navegação, ações secundárias e botão de configuração, incluindo estados hover/pressed já existentes no baseline.

A paleta física recebeu apenas as cores que ainda não estavam registradas. O total passou para **788 entradas físicas**.

## 4. Paridade visual

Os valores dos novos tokens reproduzem os valores previamente caracterizados nos três temas.

Hashes canônicos dos stylesheets completos após o Bloco A:

| Tema | SHA-256 QSS canônico |
|---|---|
| Claro | `257d65d1427b26067616ee97408571e5354bd618bd512cfabd4b887d314bdb9b` |
| Escuro | `777e1ffb22578576303bc7123a936eeb264ac712faed3efef3fbd9f6cebdcba5` |
| Futurista | `53f523143c157af9cfa8f22619dcb23fed38f230d6d299fd7e119570ff042e14` |

Foi adicionada uma prova de regressão que remove somente as novas camadas do Bloco A. Após essa remoção, os QSS retornam exatamente aos hashes históricos anteriores:

| Tema | Baseline anterior recuperado |
|---|---|
| Claro | `ae984441b7a8eed69fcc9427003d28c96f631a2e7ed8c2b60504469af7441ab4` |
| Escuro | `1a5a8ed63656acff1afdd27ce501a7cde18a157b1cb95e01dd305129f18847fd` |
| Futurista | `4b118824e007ab2d02141e87fd994c58df0bd6fb07eff64ed5ad0ecfce090e4c` |

Isso comprova que, na composição de stylesheet, a mudança estrutural desta etapa está limitada às novas camadas previstas.

## 5. Arquivos funcionais alterados

- `tema.py` — novas camadas tokenizadas do shell/cabeçalho e composição final por tema;
- `ui/design/tokens.py` — 41 novos contratos `dashboard.*`;
- `ui/design/themes.py` — mapeamentos Claro/Escuro/Futurista e três gradientes;
- `ui/design/palette.py` — registro das cores físicas necessárias.

Também foi criado:

- `test_design_system_dashboard_bloco_a.py` — teste específico de contrato, escopo, paridade, reversibilidade, integridade e preservação do código protegido.

Os testes históricos do Design System que mantêm contagem global ou snapshot QSS foram atualizados para reconhecer o novo orçamento de 555 tokens e os novos snapshots. Nos testes históricos que verificam diferenças entre etapas anteriores, a camada do Dashboard é removida antes da comparação, preservando o significado original desses testes.

## 6. Arquivos protegidos — preservação byte a byte

Nenhum destes arquivos foi alterado:

| Arquivo | SHA-256 |
|---|---|
| `main.py` | `be93709926ac1e4c783468d7409afcfe6b3de200b289f0f0b13f9fc0359defb1` |
| `estudos.db` | `034940a33ea792957d8fafbf5c528db7cd895db69031696fbdd3f0a0ce5a41ef` |
| `versao.py` | `8436214451a591c0a3d3429f62d53c0c01cfc0cc7311d71e57fcf060f5b39642` |
| `foco.py` | `8fbe4659f3371683738a3fa239a789b3bca26ab47dc68f38a69829a33afd03ed` |
| `jogos.py` | `498aab65a2a13efa070ae2f912536b5ddc1aada31e23a28846def6a617492286` |
| `checkpoint.py` | `947295fdf2035d6f65d5d43f70e1d6e5e1c411d92eaca264a469a221b6b61c38` |

Metadados permanecem:

- `VIGHNA_VERSION = "0.29.59"`;
- `VIGHNA_BUILD = "calendar-week-forecast-v1"`;
- `VIGHNA_SCHEMA = 25`.

## 7. Banco de dados

Validação realizada no banco recebido:

- `PRAGMA integrity_check` → **ok**;
- `PRAGMA foreign_key_check` → **0 violações**;
- hash do banco inalterado.

Nenhuma migração de schema ou escrita funcional foi executada.

## 8. Testes executados

### Teste específico do Bloco A

`test_design_system_dashboard_bloco_a.py`:

- **7/7 aprovados**.

Ele valida:

- orçamento de 555 tokens;
- tipos dos 41 novos tokens;
- valores visuais nos três temas;
- escopo restrito dos seletores;
- ausência de hex literal nas novas camadas;
- ausência de marcador de token não resolvido no QSS final;
- hashes QSS novos;
- recuperação exata dos três baselines anteriores ao remover somente o Bloco A;
- hierarquia do Dashboard intacta em `main.py`;
- hashes dos arquivos protegidos;
- integridade e chaves estrangeiras do banco.

### Regressão direcionada

Foram executados em conjunto os testes do novo Bloco A, Jogos Passo 5, feedback/explicação B2g e Resumo Final Passo B:

- **34/34 aprovados**.

### Suíte histórica do Design System no ambiente Linux

Resultado atual: **195 testes executados**, com **6 falhas e 6 erros**. Essa mesma verificação na base original, antes do Bloco A, apresentou **188 testes**, também com **6 falhas e 6 erros**.

Portanto, o Bloco A adicionou 7 testes aprovados e **não introduziu nova falha na suíte histórica**.

As seis falhas já existiam em `test_design_system_resolvedor_enunciado_b2f.py`, que conserva snapshots/expectativas de uma base B2c anterior. Os seis erros restantes decorrem do harness Linux sem a instalação Qt/PySide6 completa para testes de QPainter/ícones; não são falhas funcionais descobertas nesta etapa.

`py_compile` também foi executado com sucesso em todos os arquivos Python alterados.

## 9. O que não foi feito

- não houve alteração em `main.py`;
- não houve alteração do banco;
- não houve alteração de versão/build/schema;
- não houve limpeza dos 32 seletores legados/órfãos já caracterizados;
- não houve migração dos dois candidatos adicionais do tema Claro;
- não houve alteração dos widgets `QPainter`;
- não houve avanço para o próximo bloco do Dashboard;
- o executável Windows não foi recompilado neste ambiente Linux.

## 10. Validação manual necessária no Windows

Antes de iniciar o próximo bloco, validar visualmente o executável/fonte nos três temas:

1. abrir o Dashboard e comparar fundo, título, subtítulo e topbar;
2. testar hover da busca global;
3. testar normal/hover/pressed de `Central de Questões` quando aplicável;
4. tornar `Retomar bateria` visível e testar normal/hover;
5. testar hover/pressed do botão de configurações;
6. testar `topProfileCombo`, incluindo hover/foco e troca real de perfil;
7. testar `Gerenciar` normal/hover;
8. alternar Claro → Escuro → Futurista → Claro e verificar ausência de resíduos visuais;
9. confirmar que layout, alturas, larguras, espaçamentos e comportamento permaneceram idênticos;
10. confirmar que Foco, Planejamento e demais blocos abaixo do cabeçalho não sofreram mudança visual decorrente desta etapa.

## 11. Próximo passo

Somente após a validação manual do Bloco A no Windows deve ser iniciada a próxima subdivisão do Dashboard definida pelo roadmap. O próximo trabalho deve novamente começar por delimitação de escopo/baseline do bloco específico, sem aproveitar este Bloco A como autorização para migrar o Dashboard inteiro.
