# VighnaStudy — Design System do Dashboard — Bloco C

## 1. Base e objetivo

Implementação executada sobre a base manualmente validada no Windows:

`VighnaStudy_0.29.59_DesignSystem_Dashboard_Bloco_B_COMPLETO.zip`

Metadados preservados:

- versão: `0.29.59`;
- build: `calendar-week-forecast-v1`;
- schema: `25`.

O Bloco C migra, de forma aditiva e conservadora, três áreas do Dashboard para o Design System:

1. **Recomendação do algoritmo**;
2. **Seu progresso**;
3. **Acessos rápidos** independentes.

A caracterização anterior continua registrada em `RELATORIO_DESIGN_SYSTEM_DASHBOARD_BLOCO_C_CARACTERIZACAO.md`.

## 2. Escopo implementado

### 2.1 Recomendação do algoritmo

Foram tokenizados, sem alterar a hierarquia de widgets:

- card `dashboardTodayAction`;
- ícone;
- título e subtítulo;
- botão de ajuda e hover;
- corpo da recomendação;
- texto de prontidão;
- CTA principal, hover e pressed;
- ação secundária e hover.

As propriedades dinâmicas `actionRole`, `simpleHero` e `heroCentral` permanecem no mesmo código de `main.py`. O Bloco C **não introduz uma nova diferenciação visual por `actionRole`**, preservando a aparência efetivamente resultante da cascata anterior.

### 2.2 Seu progresso

O escopo é restrito a:

`QFrame#focusQuickCard[cardRole="progress"]`

Foram tokenizados:

- card e borda;
- ícone;
- título, descrição e detalhe;
- badge;
- trilha e preenchimento da barra de progresso;
- botão secundário e hover.

O card protagonista do **Foco**, já migrado no Bloco B, não é capturado por esta camada.

### 2.3 Acessos rápidos

O escopo é restrito a:

`QFrame#dashboardQuickAccess[embedded="false"]`

Foram tokenizados:

- superfície e borda do agrupador;
- texto do toggle;
- botões de toolbar e hover;
- botão de Pausa e hover.

A caixa `dashboardQuickAccess[embedded="true"]`, usada dentro do Foco, permanece sob o contrato do Bloco B e não foi remigrada.

## 3. Itens deliberadamente fora do Bloco C

Não foram migrados neste passo:

- Foco e Planejamento de hoje já concluídos no Bloco B;
- cards da Visão geral;
- Ritmo de estudo;
- Qualidade;
- Progresso do edital;
- notificações e demais seções inferiores;
- `DashboardPlanningArcWidget`;
- `DashboardDonutWidget`;
- qualquer desenho realizado por `QPainter`;
- geometria, fontes, paddings, margens ou comportamento funcional.

## 4. Design System

Antes do Bloco C:

- 102 tokens semânticos;
- 518 tokens de componente;
- **620 tokens totais**.

Depois do Bloco C:

- 102 tokens semânticos;
- 577 tokens de componente;
- **679 tokens totais**.

Acréscimo exato:

- **48 tokens de cor**;
- **11 tokens de gradiente**;
- **59 tokens de componente**.

Os 11 gradientes cobrem card/ícone/CTA da recomendação, card/preenchimento do progresso e superfícies/estados dos acessos rápidos.

`ui/design/palette.py` recebeu 112 registros físicos necessários para que as cores legadas usadas pelos novos contratos sejam reconhecidas pela validação central da paleta. Isso não significa 112 novos tokens: o orçamento contratual deste passo continua sendo 59 tokens.

## 5. Arquivos de produção alterados

Somente a infraestrutura visual do Design System e sua composição foram alteradas:

- `ui/design/tokens.py`;
- `ui/design/themes.py`;
- `ui/design/palette.py`;
- `tema.py`.

`main.py` não foi alterado.

A nova camada `ESTILO_DASHBOARD_BLOCO_C` é única, tokenizada e estritamente escopada sob `#dashboardRoot`. Ela não contém hexadecimal literal e não contém código `QPainter`.

## 6. Preservação funcional

Os seguintes arquivos permaneceram byte a byte idênticos à base B:

| Arquivo | SHA-256 |
|---|---|
| `main.py` | `be93709926ac1e4c783468d7409afcfe6b3de200b289f0f0b13f9fc0359defb1` |
| `estudos.db` | `034940a33ea792957d8fafbf5c528db7cd895db69031696fbdd3f0a0ce5a41ef` |
| `versao.py` | `8436214451a591c0a3d3429f62d53c0c01cfc0cc7311d71e57fcf060f5b39642` |
| `foco.py` | `8fbe4659f3371683738a3fa239a789b3bca26ab47dc68f38a69829a33afd03ed` |
| `jogos.py` | `498aab65a2a13efa070ae2f912536b5ddc1aada31e23a28846def6a617492286` |
| `checkpoint.py` | `947295fdf2035d6f65d5d43f70e1d6e5e1c411d92eaca264a469a221b6b61c38` |

Portanto, o Bloco C não modifica fluxo, dados, regras de estudo ou lógica de atualização do Dashboard.

## 7. Prova de aditividade QSS

Hashes normalizados da base B:

- Claro: `9ba6faf327ad1fcc81bc73750b17c482bce8e2673a65aa6752b6ba41e915b987`;
- Escuro: `7f77d8aa23eeb8e9d3bbacf5b2589f3617bbee2b0d3864e7b43ae91e6669d477`;
- Futurista: `4869e85bff334d33d7af227e06cd951d31883d548bb8f90df041fedd605c8377`.

Hashes normalizados após o Bloco C:

- Claro: `64ea82086ca9575c727925b6e0ebae18bc45d0f760e94ca1d3bab679be16f273`;
- Escuro: `d3011c1a6f28b7d89678129ab6462d6cb4b1b9ce19e2084dc1f3e52e5a6cda2c`;
- Futurista: `69f5d9733fd68f2665f8f3a534cf7b2f88fc07890b309837302737809ebea488`.

A remoção programática apenas da camada C recupera **exatamente** os três hashes normalizados do checkpoint B. No Futurista, a verificação remove tanto a camada C herdada do Escuro quanto o override C final do próprio Futurista, respeitando a arquitetura histórica do tema.

## 8. Testes do Bloco C

Foi criado `test_design_system_dashboard_bloco_c.py` com **9 testes**, todos aprovados. A suíte valida:

- orçamento exato de 59 tokens;
- 48 cores nos três temas;
- direção e stops dos 11 gradientes;
- ausência de hexadecimais literais no novo QSS;
- escopo obrigatório sob `#dashboardRoot`;
- isolamento entre `embedded="false"` e `embedded="true"`;
- isolamento do Foco do Bloco B, overview e componentes `QPainter`;
- preservação dos estados/propriedades dinâmicas do `main.py`;
- hashes QSS do Bloco C;
- recuperação exata do checkpoint B ao retirar C;
- hashes dos arquivos protegidos;
- versão/build/schema.

### Bateria dirigida

Executados em conjunto:

- Dashboard Bloco A;
- Dashboard Bloco B;
- Dashboard Bloco C;
- Jogos Passo 5;
- feedback/explicação B2g;
- Resumo Final Passo A;
- Resumo Final Passo B.

**Resultado: 59/59 testes aprovados.**

Os testes históricos cumulativos que mantinham a contagem global ou o snapshot QSS do checkpoint B foram atualizados para reconhecer a nova camada C. Nos testes de checkpoints mais antigos, C é removido antes da comparação histórica. O teste de Pausa/Jogos passou a ignorar apenas o novo `dashboardQuickAccess[embedded="false"] #pauseNavButton`, sem relaxar a validação do hub de Pausa ou dos Jogos.

### Suíte histórica ampla

Foram executados **212 testes** do padrão `test_design_system*.py`.

Resultado:

- **6 falhas**;
- **6 erros**.

Esse saldo é exatamente o mesmo registrado antes do Bloco C. As seis falhas continuam concentradas no teste histórico `test_design_system_resolvedor_enunciado_b2f.py`; os seis erros continuam ligados às limitações Qt/ambiente já conhecidas. Não foi adicionada falha ou erro de regressão pelo Bloco C.

## 9. Banco e compilação

- `PRAGMA integrity_check`: **ok**;
- `PRAGMA foreign_key_check`: **0 violações**;
- `py_compile` dos arquivos de produção alterados e testes do Dashboard: **aprovado**;
- renderização dos temas Claro, Escuro e Futurista: sem marcador de token não resolvido.

## 10. Validação manual necessária

Antes de declarar o Bloco C encerrado, validar no Windows os temas **Claro, Escuro e Futurista**, observando especialmente:

- card **Recomendação do algoritmo**;
- botão de ajuda;
- CTA **Começar agora** em normal, hover e pressed;
- ação secundária;
- card **Seu progresso**;
- badge e barra de progresso;
- botão do card de progresso;
- **Acessos rápidos** independentes;
- botão de Pausa e demais botões rápidos;
- ausência de alteração no Foco e Planejamento do Bloco B;
- navegação e atualização normal do Dashboard.

O executável não foi reconstruído no ambiente Linux. A reconstrução deve continuar pelo `atualizar_exe.bat` no Windows antes da inspeção visual final.

## 11. Próximo recorte recomendado

Após a validação manual do Bloco C, o próximo recorte seguro é a **Visão geral do Dashboard**, tratando Ritmo de estudo, Qualidade e Progresso do edital de forma conservadora. Componentes desenhados por `QPainter`, em especial o donut de Qualidade, devem continuar isolados e caracterizados antes de qualquer migração específica do desenho.
