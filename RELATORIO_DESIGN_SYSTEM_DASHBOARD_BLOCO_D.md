# VighnaStudy — Design System do Dashboard — Bloco D

## 1. Base e objetivo

Implementação executada sobre a base manualmente validada no Windows:

`VighnaStudy_0.29.59_DesignSystem_Dashboard_Bloco_C_COMPLETO.zip`

Metadados preservados:

- versão: `0.29.59`;
- build: `calendar-week-forecast-v1`;
- schema: `25`.

O Bloco D migra para o Design System a seção **Visão geral do Dashboard**, limitada a:

1. **Ritmo de estudo**;
2. **Qualidade do aprendizado**;
3. **Progresso do edital**.

A caracterização prévia está registrada em `RELATORIO_DESIGN_SYSTEM_DASHBOARD_BLOCO_D_CARACTERIZACAO.md`.

## 2. Escopo implementado

### 2.1 Estrutura comum da Visão geral

Os três cards `QFrame#dashboardOverviewCard` agora são tratados por uma camada aditiva e estritamente escopada, utilizando a propriedade dinâmica `overviewRole`:

- `rhythm`;
- `quality`;
- `projection`.

Foram tokenizados os contratos comuns de card, borda, títulos, textos auxiliares, divisores e estados específicos de cada função.

### 2.2 Ritmo de estudo

Foram tokenizados:

- valor principal e legenda;
- labels das linhas;
- indicadores e valores de hoje/atraso;
- estados `ok` e `attention`;
- resumo de Foco.

As propriedades `metricRole` e `statusRole` continuam sendo atribuídas exatamente pelo código existente.

O `focusProgressBar` **não recebeu contrato duplicado**, pois já é atendido pelos tokens `focus_mode.progress_*` criados em etapa anterior.

### 2.3 Qualidade do aprendizado

Foram tokenizados:

- eyebrow e texto de apoio;
- caixa de tendência;
- borda e superfície;
- estado neutro;
- estados `positive`, `negative` e `stable`;
- label e rodapé.

A lógica que calcula e aplica `trendRole` permaneceu intocada.

`DashboardDonutWidget` foi deliberadamente excluído: o donut continua desenhado por `QPainter` no `main.py`, sem qualquer alteração nesta etapa.

### 2.4 Progresso do edital

Foram tokenizados:

- título e textos do card;
- porcentagem;
- trilha, borda e preenchimento da barra;
- cards métricos;
- estados `consolidating`, `consolidated` e `domain`;
- botões de ação inferiores;
- gradientes normal e hover das ações.

A estrutura recolhível e a persistência já existentes foram preservadas.

## 3. Itens deliberadamente fora do Bloco D

Não foram alterados:

- Shell e cabeçalho do Bloco A;
- Foco e Planejamento do Bloco B;
- Recomendação, Seu progresso e Acessos rápidos do Bloco C;
- `dashboardGroupToggle` compartilhado entre seções;
- notificações e demais áreas inferiores do Dashboard;
- `DashboardPlanningArcWidget`;
- `DashboardDonutWidget`;
- qualquer pintura `QPainter`;
- geometria, tipografia, margens, cálculos ou comportamento funcional.

## 4. Design System

Antes do Bloco D:

- 102 tokens semânticos;
- 577 tokens de componente;
- **679 tokens totais**.

Depois do Bloco D:

- 102 tokens semânticos;
- 622 tokens de componente;
- **724 tokens totais**.

Acréscimo exato:

- **42 tokens de cor**;
- **3 tokens de gradiente**;
- **45 tokens de componente**.

Os novos contratos estão organizados nas famílias `dashboard.overview_*`, `dashboard.rhythm_*`, `dashboard.quality_*` e `dashboard.projection_*`.

`ui/design/palette.py` recebeu os registros físicos necessários para validar centralmente as cores legadas usadas por esses contratos. Esses registros físicos não alteram o orçamento de 45 novos tokens.

## 5. Arquivos de produção alterados

Somente a infraestrutura visual foi modificada:

- `ui/design/tokens.py`;
- `ui/design/themes.py`;
- `ui/design/palette.py`;
- `tema.py`.

`main.py` não foi alterado.

A camada `ESTILO_DASHBOARD_BLOCO_D`:

- é tokenizada;
- não contém hexadecimal literal;
- fica sob `#dashboardRoot`;
- usa `overviewRole` para impedir vazamento entre os três cards;
- não contém código `QPainter`;
- não captura notificações, Planejamento, Foco ou os blocos A–C.

## 6. Preservação funcional

Os principais arquivos protegidos permaneceram byte a byte idênticos à base C:

| Arquivo | SHA-256 |
|---|---|
| `main.py` | `be93709926ac1e4c783468d7409afcfe6b3de200b289f0f0b13f9fc0359defb1` |
| `estudos.db` | `034940a33ea792957d8fafbf5c528db7cd895db69031696fbdd3f0a0ce5a41ef` |
| `versao.py` | `8436214451a591c0a3d3429f62d53c0c01cfc0cc7311d71e57fcf060f5b39642` |
| `foco.py` | `8fbe4659f3371683738a3fa239a789b3bca26ab47dc68f38a69829a33afd03ed` |
| `jogos.py` | `498aab65a2a13efa070ae2f912536b5ddc1aada31e23a28846def6a617492286` |
| `checkpoint.py` | `947295fdf2035d6f65d5d43f70e1d6e5e1c411d92eaca264a469a221b6b61c38` |

Hashes dos quatro arquivos de produção alterados:

| Arquivo | SHA-256 |
|---|---|
| `tema.py` | `fc8ac868d53503d557f7166c36183f7108639635f43b6806ebf5783d9be97736` |
| `ui/design/tokens.py` | `d5851288d90f4cbdc546f42d2fa5e963bf8eb9faac166aa1643363c94c1327ce` |
| `ui/design/themes.py` | `2c2bf3a8d517268000d03be873de167830c69a85418055b74ebb61d3dc65a637` |
| `ui/design/palette.py` | `7638e526d482b3d82be92c893def159a49bf9c5d4bfb515f5b72d3446f094629` |

## 7. Prova de aditividade QSS

Hashes normalizados do checkpoint C:

- Claro: `64ea82086ca9575c727925b6e0ebae18bc45d0f760e94ca1d3bab679be16f273`;
- Escuro: `d3011c1a6f28b7d89678129ab6462d6cb4b1b9ce19e2084dc1f3e52e5a6cda2c`;
- Futurista: `69f5d9733fd68f2665f8f3a534cf7b2f88fc07890b309837302737809ebea488`.

Hashes normalizados após o Bloco D:

- Claro: `67eb7f0c5eee80785bbe7595d4ca9374c9fc2985b34034ede312c06e69e49e08`;
- Escuro: `1109df37ba34574f0607dd9ee3839a770c74aed8906dece461e9c2e8b81f7624`;
- Futurista: `07717d507c118a34f4b8ca7c62556c60a8b0fdc874f7d30f379d19b4ed379d6c`.

A remoção programática somente da camada D recupera **exatamente** os três hashes do checkpoint C. No Futurista, a prova remove tanto a camada D herdada do Escuro quanto o override D futurista final, preservando a arquitetura histórica do tema.

## 8. Testes

### Testes específicos do Bloco D

Foi criado `test_design_system_dashboard_bloco_d.py` com **9 testes**, todos aprovados. A suíte verifica:

- orçamento exato de 45 tokens;
- valores das 42 cores nos três temas;
- direção e stops dos 3 gradientes;
- isolamento por `overviewRole`;
- preservação de `metricRole`, `statusRole` e `trendRole`;
- preservação da persistência das seções;
- ausência de hexadecimal literal na nova camada;
- exclusão de `DashboardDonutWidget`/`QPainter`;
- hashes QSS do Bloco D;
- recuperação exata do checkpoint C;
- hashes dos arquivos protegidos;
- versão, build e schema.

### Bateria dirigida

Executados em conjunto:

- Dashboard Bloco A;
- Dashboard Bloco B;
- Dashboard Bloco C;
- Dashboard Bloco D;
- Jogos Passo 5;
- feedback/explicação B2g;
- Resumo Final Passo A;
- Resumo Final Passo B.

**Resultado: 68/68 testes aprovados.**

Os testes cumulativos foram atualizados apenas para reconhecer a nova contagem global, o novo snapshot QSS ou para retirar a camada D antes de comparar checkpoints históricos A/B/C. Isso mantém as provas antigas válidas sem redefinir seus contratos.

### Suíte histórica ampla

Foram executados **221 testes** do padrão `test_design_system*.py`.

Resultado:

- **6 falhas**;
- **6 erros**.

O saldo é o mesmo registrado na base C. As seis falhas continuam concentradas em `test_design_system_resolvedor_enunciado_b2f.py`; os seis erros continuam sendo os mesmos ligados às limitações Qt/ambiente da suíte histórica. O Bloco D não acrescentou falha ou erro de regressão.

## 9. Banco, compilação e renderização

- `PRAGMA integrity_check`: **ok**;
- `PRAGMA foreign_key_check`: **0 violações**;
- `py_compile` de `main.py`, `tema.py`, módulos `ui/design` alterados e teste D: **aprovado**;
- Claro, Escuro e Futurista: **nenhum marcador de token não resolvido**.

## 10. Validação manual necessária

Antes de encerrar o Bloco D, validar no Windows os temas **Claro, Escuro e Futurista**, observando:

- card **Ritmo de estudo**;
- estados hoje/atraso e ok/atenção;
- resumo e barra de Foco dentro do card;
- card **Qualidade do aprendizado**;
- tendências neutra, positiva, negativa e estável quando disponíveis;
- donut, confirmando que permaneceu visualmente inalterado;
- card **Progresso do edital** aberto e recolhido;
- barra de progresso;
- métricas por estado;
- botões inferiores em normal/hover;
- persistência da expansão das seções;
- ausência de alteração visual ou funcional nos Blocos A, B e C.

O executável não foi reconstruído neste ambiente. No Windows, usar `atualizar_exe.bat` antes da validação manual.
