# VighnaStudy — Design System — Dashboard — Bloco B
## Implementação: Foco + Planejamento de hoje

**Data:** 2026-10-07
**Base de entrada:** `VighnaStudy_0.29.59_DesignSystem_Dashboard_Bloco_A_COMPLETO.zip`
**SHA-256 da base:** `c1bb6089208827af2de978ad3ea9a4676cc91fa084eda9fbcabfc4b4247bc576`

**Versão:** `0.29.59`
**Build:** `calendar-week-forecast-v1`
**Schema:** `25`

## 1. Resultado

O Bloco B do Dashboard foi implementado de forma aditiva e conservadora. O recorte migrado é **Foco + Planejamento de hoje**, sem alteração de estrutura, comportamento, banco ou desenho `QPainter`.

O Design System passou de **555** para **620 tokens**:

- semânticos: **102 → 102**;
- componente: **453 → 518**;
- acréscimo: **65 tokens**;
- composição do acréscimo: **60 cores + 5 gradientes**.

## 2. Arquivos de produção alterados

Somente a infraestrutura visual do Design System e sua camada de composição foram alteradas:

- `ui/design/tokens.py` — novos contratos do Dashboard Bloco B;
- `ui/design/themes.py` — valores e gradientes para Claro, Escuro e Futurista;
- `ui/design/palette.py` — registro das cores físicas novas necessárias;
- `tema.py` — três camadas QSS aditivas e composição final.

Não houve mudança em `main.py`.

## 3. Escopo implementado

### Foco

Foram tokenizados:

- superfície e borda do painel;
- card protagonista e seu gradiente;
- ícone, título e selo;
- descrição, detalhe, legenda e valor;
- caixa de objetivo embutida;
- barra de progresso;
- CTA principal, hover e os estados que já existiam efetivamente.

A caixa `dashboardQuickAccess` só é estilizada quando aparece dentro de `focusDashboardMainCard` e possui `embedded="true"`. O card independente **Seu progresso** não foi capturado pelo novo escopo.

### Planejamento de hoje

Foram tokenizados:

- card e borda;
- ícone, título e data;
- textos da meta diária;
- progresso legado compatível;
- painel operacional;
- títulos, detalhes e valores operacionais;
- divisor;
- rótulo semanal;
- estados padrão, concluído, atenção e ativo;
- botão de resumo e hover.

`DashboardPlanningArcWidget` permanece integralmente fora da migração.

## 4. Gradientes adicionados

- `dashboard.focus_card_gradient`;
- `dashboard.focus_action_gradient`;
- `dashboard.focus_action_hover_gradient`;
- `dashboard.planning_card_gradient`;
- `dashboard.planning_progress_gradient`.

Os gradientes reproduzem os estados sólidos ou graduados que já eram efetivos em cada tema. Quando a aparência legada era uma cor sólida, o contrato usa stops idênticos para manter a mesma percepção sem introduzir variação visual.

## 5. Cascata preservada

As novas constantes são:

- `ESTILO_DASHBOARD_BLOCO_B_CLARO`;
- `ESTILO_DASHBOARD_BLOCO_B_ESCURO`;
- `ESTILO_DASHBOARD_BLOCO_B_FUTURISTA`.

Elas são anexadas ao fim da composição correspondente. No Futurista, a arquitetura continua sendo:

1. stylesheet Escuro completo;
2. camada Futurista histórica;
3. shell Futurista do Bloco A;
4. camada Futurista final do Bloco B.

A herança da camada B Escura ocorre naturalmente porque `stylesheet_futurista()` continua derivando de `stylesheet_escuro()`.

## 6. Prova de isolamento QSS

Hashes canônicos do stylesheet completo após o Bloco B:

| Tema | SHA-256 canônico |
|---|---|
| Claro | `9ba6faf327ad1fcc81bc73750b17c482bce8e2673a65aa6752b6ba41e915b987` |
| Escuro | `7f77d8aa23eeb8e9d3bbacf5b2589f3617bbee2b0d3864e7b43ae91e6669d477` |
| Futurista | `4869e85bff334d33d7af227e06cd951d31883d548bb8f90df041fedd605c8377` |

Ao remover somente as camadas do Bloco B, os hashes retornam exatamente ao checkpoint validado do Bloco A:

| Tema | Bloco A recuperado |
|---|---|
| Claro | `257d65d1427b26067616ee97408571e5354bd618bd512cfabd4b887d314bdb9b` |
| Escuro | `777e1ffb22578576303bc7123a936eeb264ac712faed3efef3fbd9f6cebdcba5` |
| Futurista | `53f523143c157af9cfa8f22619dcb23fed38f230d6d299fd7e119570ff042e14` |

Isso prova que a alteração visual global é isolável e reversível como uma camada aditiva.

## 7. Arquivos protegidos

Os seguintes hashes permaneceram idênticos à base A:

| Arquivo | SHA-256 |
|---|---|
| `main.py` | `be93709926ac1e4c783468d7409afcfe6b3de200b289f0f0b13f9fc0359defb1` |
| `estudos.db` | `034940a33ea792957d8fafbf5c528db7cd895db69031696fbdd3f0a0ce5a41ef` |
| `versao.py` | `8436214451a591c0a3d3429f62d53c0c01cfc0cc7311d71e57fcf060f5b39642` |
| `foco.py` | `8fbe4659f3371683738a3fa239a789b3bca26ab47dc68f38a69829a33afd03ed` |
| `jogos.py` | `498aab65a2a13efa070ae2f912536b5ddc1aada31e23a28846def6a617492286` |
| `checkpoint.py` | `947295fdf2035d6f65d5d43f70e1d6e5e1c411d92eaca264a469a221b6b61c38` |

Portanto, o Bloco B não alterou fluxo funcional nem dados.

## 8. Testes

Foi criado `test_design_system_dashboard_bloco_b.py` com **8 testes**, todos aprovados. Eles validam:

- orçamento exato de 65 tokens;
- valores de todos os 60 tokens de cor nos três temas;
- direção/stops dos 5 gradientes nos três temas;
- ausência de hexadecimais literais nas novas camadas;
- escopo obrigatório sob `#dashboardRoot`;
- exclusão de **Seu progresso**, recomendação e overview;
- exclusão explícita de `QPainter`;
- hashes QSS do Bloco B;
- recuperação exata dos hashes do Bloco A ao remover a nova camada;
- permanência dos arquivos protegidos;
- versão/build/schema.

### Bateria dirigida

Executados em conjunto:

- Dashboard Bloco A;
- Dashboard Bloco B;
- Jogos Passo 5;
- feedback/explicação B2g;
- Resumo Final Passo A;
- Resumo Final Passo B.

**Resultado: 50/50 testes aprovados.**

### Suíte histórica ampla

`203` testes do padrão `test_design_system*.py` foram executados no ambiente Linux disponível.

Resultado:

- **6 falhas**;
- **6 erros**.

Esse é o mesmo saldo preexistente registrado na base A: nenhuma nova falha/erro foi adicionada pelo Bloco B. Os erros continuam ligados a dependências Qt gráficas não disponíveis no ambiente Linux de teste; as falhas históricas restantes concentram-se no teste legado `test_design_system_resolvedor_enunciado_b2f.py`, que já carrega snapshots/contagens antigos.

## 9. Banco e compilação

- `PRAGMA integrity_check`: **ok**;
- `PRAGMA foreign_key_check`: **0 violações**;
- `py_compile` nos arquivos de produção alterados e testes do Dashboard: **aprovado**;
- contratos dos temas Claro, Escuro e Futurista: **válidos**.

## 10. Metadados preservados

- versão: `0.29.59`;
- build: `calendar-week-forecast-v1`;
- schema: `25`.

Nenhum incremento artificial de versão foi feito apenas pela migração do Design System.

## 11. Executável

O executável **não foi reconstruído no Linux**. A reconstrução e a validação visual devem continuar sendo feitas no Windows após a abertura do pacote final.

## 12. Validação manual necessária

Antes de declarar o Bloco B encerrado, validar no Windows os temas **Claro, Escuro e Futurista**, observando especificamente:

- painel de Foco;
- card protagonista e CTA;
- caixa de objetivo embutida;
- barra de progresso;
- Planejamento de hoje;
- estados semanais;
- botão do resumo;
- ausência de alteração visual no card **Seu progresso**;
- arco de Planejamento sem mudança de desenho;
- funcionamento normal de navegação e atualização do Dashboard.

Após essa validação, o Bloco B pode virar a nova base de referência para o próximo recorte do Dashboard.
