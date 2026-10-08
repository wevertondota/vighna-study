# VighnaStudy — Auditoria de encerramento do macroescopo Dashboard

**Data:** 2026-10-07
**Base auditada:** `VighnaStudy_0.29.59_DesignSystem_Dashboard_Bloco_H_COMPLETO.zip`
**SHA-256 da base:** `935e6ce9ad5af642556d4205b12d5d995c1b20c26643e0b4b0a06260da53af3e`
**Versão:** `0.29.59`
**Build:** `calendar-week-forecast-v1`
**Schema:** `25`
**Design System:** **966 tokens** = 102 semânticos + 864 de componente
**Tokens `dashboard.*`:** **452** = 407 de cor + 45 de gradiente

---

## 1. Objetivo

Esta auditoria verifica se o primeiro macroescopo da ordem de migração — **Dashboard** — pode ser formalmente encerrado após os Blocos A–H, ou se ainda existe consumidor visual **ativo** cuja origem cromática permanece fora do Design System.

A auditoria não redesenha a interface e não altera arquivos de produção. O critério adotado é distinguir:

1. consumidor ativo e visível;
2. consumidor estrutural sem contrato cromático próprio;
3. consumidor já atendido por token compartilhado de outro módulo;
4. consumidor dormente/oculto de compatibilidade;
5. hardcode histórico de QSS já sombreado pela cascata tokenizada;
6. hardcode ativo ainda vencedor fora do Design System.

---

## 2. Estado consolidado A–H

A montagem ativa do Dashboard está coberta pelos seguintes recortes:

- **A — Shell e cabeçalho**;
- **B — Foco + Planejamento de hoje**;
- **C — Recomendação + Seu progresso + Acessos rápidos**;
- **D — Visão geral**;
- **E — Notificações e alertas**;
- **F — Planejamento completo**;
- **G — Estudo por questões**;
- **H — Disciplinas e acabamento inferior**.

As camadas A–H são aditivas. A inspeção das definições tokenizadas confirmou **zero hexadecimal literal, zero `rgb/rgba()` literal e zero `qlineargradient()` físico** dentro das próprias camadas novas. Gradientes aparecem somente por marcadores de token.

O Bloco H também eliminou o último hardcode cromático inline ativo conhecido na grade de disciplinas desligadas: o mecanismo `setStyleSheet()` foi preservado, mas os nove valores físicos agora vêm de `qss_color()`.

---

## 3. Cobertura estrutural dos consumidores QSS

Foram extraídos os `objectName` construídos em `criar_tela_inicial()` e em `carregar_botoes_disciplinas()`.

- **175 objectNames únicos** foram encontrados;
- **161** aparecem diretamente nas camadas tokenizadas A–H;
- **14** não aparecem diretamente nessas camadas.

Os 14 restantes foram classificados e **nenhum representa, sozinho, um painel visual ativo não migrado**:

| Consumidor | Classificação | Decisão |
|---|---|---|
| `dashboardCollapsibleContent` | estrutural | mantém `background: transparent`; não requer contrato cromático próprio |
| `dashboardPlanningTopContainer` | estrutural | container sem aparência própria |
| `weeklyGoalMetricsContainer` | estrutural | container sem aparência própria |
| `weeklyLoadDays` | estrutural | container sem aparência própria |
| `focusProgressBar` | ativo | já usa tokens `focus_mode.progress_*` de componente compartilhado |
| `dashboardTodaySeparator` | inativo | é criado, mas não é inserido no layout atual |
| `focusDashboardMetricText` | compatibilidade oculta | métricas superiores estão `setVisible(False)`; demais usos pertencem aos painéis ocultos de Regularidade/Conquistas |
| `myEvolutionPanel` | oculto | Regularidade e Conquistas são explicitamente ocultadas no Dashboard |
| `mutedLabel` | oculto no recorte | usos do Dashboard estão dentro dos painéis ocultos acima |
| `priorityQueuePanel` | dormente | explicitamente `setVisible(False)` |
| `queueCount` | dormente | descendente de `priorityQueuePanel` |
| `priorityQueueSourceBadge` | dormente | descendente de `priorityQueuePanel` |
| `priorityQueueExplanation` | dormente | descendente de `priorityQueuePanel` |
| `priorityQueueTable` | dormente | descendente de `priorityQueuePanel` |

Conclusão desta parte: **não foi encontrado novo painel QSS ativo que justifique outro bloco de seção depois de H**.

---

## 4. `priorityQueuePanel` — classificação final

A auditoria confirma a decisão da caracterização H.

`priorityQueuePanel`:

- continua construído para compatibilidade;
- é adicionado ao layout e imediatamente ocultado por `fila_painel.setVisible(False)`;
- não integra `obter_secoes_recolhiveis_dashboard()`;
- não pode ser reaberto pelo fluxo normal do Dashboard;
- possui QSS legado próprio, mas não é consumidor visual apresentado ao usuário.

**Classificação:** compatibilidade dormente justificada.

**Decisão:** não criar tokens para ele agora. Se houver reativação futura, a condição de aceite deve exigir caracterização/tokenização antes de torná-lo visível.

---

## 5. Hardcodes históricos de QSS

O `tema.py` ainda conserva grande quantidade de regras históricas do Dashboard com valores físicos. Isso é consequência intencional da estratégia aditiva usada nos Blocos A–H: as camadas novas foram acrescentadas ao final da cascata para permitir reversibilidade e comparação exata com os checkpoints anteriores.

A auditoria separa esse fato de um hardcode ativo:

- as **camadas novas A–H** são tokenizadas;
- os valores efetivamente migrados são sobrescritos por essas camadas finais;
- seletores antigos órfãos, estados históricos e regras sombreadas continuam no arquivo como **camada de compatibilidade**;
- sua remoção em massa agora reduziria a capacidade de rollback e ampliaria desnecessariamente o escopo.

**Decisão:** essa dívida não bloqueia, por si só, a conclusão operacional do módulo. Deve permanecer registrada para a auditoria global de hardcodes/limpeza prevista em fase posterior do Design System.

---

## 6. Bloqueadores reais encontrados — QPainter ativo

A auditoria encontrou **dois consumidores visuais ativos que continuam fora do Design System**. Ambos já haviam sido deliberadamente adiados nos blocos anteriores.

### 6.1 `DashboardPlanningArcWidget`

O widget está efetivamente visível no card **Planejamento de hoje** e é inserido no layout em `main.py`.

O `paintEvent()` ainda contém três valores cromáticos físicos:

- trilha: `QColor(207, 243, 225, 82)` — equivalente Qt a `#52CFF3E1`;
- arco de progresso: `#B9FFE3`;
- texto central: `#F4FFFA`.

Geometria, largura da caneta, cap, tipografia e cálculo do progresso não são problemas de Design System e devem permanecer intactos.

### 6.2 `DashboardDonutWidget`

O widget está efetivamente visível no card **Qualidade do aprendizado** da Visão geral.

O `paintEvent()` ainda contém:

- trilha para fundo escuro: `#263B4F`;
- trilha para fundo claro: `#DCE5ED`;
- arco de valor: `#2FB4C7`.

O texto central usa `self.palette().color(self.foregroundRole())`; portanto essa parte já não possui um valor físico local e não precisa ser substituída apenas por esta auditoria.

### 6.3 Resultado

Esses dois widgets são **ativos**, **visíveis** e suas cores são definidas diretamente no código de componente. Portanto, enquanto permanecerem assim, não é correto declarar que o Dashboard está integralmente centralizado.

---

## 7. Decisão de encerramento

### Resultado da auditoria

**DASHBOARD AINDA NÃO APROVADO PARA ENCERRAMENTO FORMAL.**

O motivo não é um novo painel de layout. O único bloqueio material encontrado é a pintura programática dos dois widgets `QPainter` ativos.

Assim, a auditoria fornece fundamento técnico para criar **um único recorte final**, agora baseado em evidência e não em suposição:

**Dashboard — Bloco I: componentes QPainter ativos**

Escopo estrito:

1. `DashboardPlanningArcWidget`;
2. `DashboardDonutWidget`.

Nenhum outro painel do Dashboard deve entrar nesse bloco.

---

## 8. Orçamento preliminar para o Bloco I

A solução mais conservadora é preservar literalmente a lógica atual e trocar apenas a origem das cores.

Uma implementação provável usa **6 tokens de cor de componente**, sem gradientes:

- `dashboard.planning_arc_track` → `#52CFF3E1`;
- `dashboard.planning_arc_fill` → `#B9FFE3`;
- `dashboard.planning_arc_text` → `#F4FFFA`;
- `dashboard.quality_donut_track_dark` → `#263B4F`;
- `dashboard.quality_donut_track_light` → `#DCE5ED`;
- `dashboard.quality_donut_fill` → `#2FB4C7`.

Esse desenho permite manter inclusive a decisão atual do donut de escolher a trilha pela luminosidade do `foregroundRole`, alterando apenas os `QColor(...)` físicos para adaptadores do Design System. O orçamento deve ser confirmado na implementação e não congelado artificialmente antes da prova de equivalência.

### Restrições do Bloco I

- não alterar dimensões, arcos, ângulos, espessuras ou fontes;
- não alterar cálculo de progresso;
- não alterar a lógica de luminosidade do donut, salvo se uma prova de equivalência demonstrar outra abordagem estritamente idêntica;
- não redesenhar Claro/Escuro/Futurista;
- não tocar `priorityQueuePanel`;
- não limpar QSS legado em massa;
- não alterar banco, versão, build ou schema;
- provar equivalência de pixels/cores por estado nos três temas;
- validar manualmente no Windows após a implementação.

---

## 9. Validações executadas nesta auditoria

### Design System

- tokens semânticos: **102**;
- tokens de componente: **864**;
- total: **966**;
- tokens `dashboard.*`: **452** (407 cores + 45 gradientes).

### Testes A–H

A suíte específica dos oito blocos foi executada com o mesmo stub mínimo de Qt utilizado nos testes estruturais:

- **69 testes**;
- **797 subtests**;
- **todos aprovados**.

Também foram reexecutados individualmente:

- Bloco G: **9/9**;
- Bloco H: **9/9**.

A tentativa de coleta direta por `pytest` sem stub falha porque o ambiente Linux atual não possui `PySide6`; isso é uma limitação ambiental conhecida e não uma regressão do código.

### Compilação

`py_compile` aprovado para:

- `main.py`;
- `tema.py`;
- `ui/design/tokens.py`;
- `ui/design/themes.py`;
- `ui/design/palette.py`;
- `ui/design/adapters.py`.

### Banco

- `PRAGMA integrity_check` → **ok**;
- `PRAGMA foreign_key_check` → **0 violações**;
- SHA-256 de `estudos.db` → `034940a33ea792957d8fafbf5c528db7cd895db69031696fbdd3f0a0ce5a41ef`.

### Hashes atuais de referência

- `main.py`: `08a1be37f347f4e79dff2587e259323259c855ea360d9a507b62aacc65a259bf`;
- `tema.py`: `4184e806b6695f56bc7d3977bb2ac6d745de335850bade417a3c47aa9d18a105`;
- `ui/design/tokens.py`: `31eb447c05dd3f54ad0436d4e4c5b6efe915d77abe6656d4672898e71e47cc56`;
- `ui/design/themes.py`: `2685cee27f329872f9da7922815b7c18b3e454b9522302641be8ecf4d57fc1a7`;
- `ui/design/palette.py`: `57f7fce0d8e2395de83b9043979c7f50ddeb23b6e07b9c7163d9d982da6bb482`.

---

## 10. Critério para encerrar o Dashboard depois do Bloco I

Depois da implementação e validação manual do Bloco I, repetir esta auditoria com os seguintes bloqueios:

1. nenhum `QColor`, `QPen`, `QBrush` ou `QLinearGradient` físico deve permanecer em consumidor **ativo** específico do Dashboard;
2. nenhum `setStyleSheet()` ativo do Dashboard deve conter cor física local;
3. todos os componentes ativos QSS devem estar tokenizados diretamente ou usar contrato compartilhado já tokenizado;
4. `priorityQueuePanel` deve continuar explicitamente classificado como dormente, ou ser migrado antes de qualquer reativação;
5. camadas A–I devem permanecer sem hardcodes físicos;
6. banco e comportamento devem permanecer intactos;
7. validação manual dos três temas deve ser aprovada.

Se esses critérios passarem, o macroescopo **Dashboard** poderá ser formalmente encerrado e o projeto seguirá para o próximo item do Plano Mestre, sem necessidade de outro bloco de Dashboard.

---

## 11. Status final

**AUDITORIA CONCLUÍDA.**
**Dashboard A–H: aprovado e preservado.**
**Encerramento do macroescopo Dashboard: BLOQUEADO por 2 widgets QPainter ativos.**
**Próximo passo recomendado: Bloco I — componentes QPainter ativos (arco + donut).**
