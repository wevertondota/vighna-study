# RELATÓRIO — DESIGN SYSTEM DO DASHBOARD — BLOCO C
## Caracterização prévia: Recomendação do algoritmo + Seu progresso + Acessos rápidos

**Base de referência:** `VighnaStudy_0.29.59_DesignSystem_Dashboard_Bloco_B_COMPLETO.zip`
**Versão:** `0.29.59`
**Build:** `calendar-week-forecast-v1`
**Schema:** `25`
**Design System antes do bloco:** 620 tokens (102 semânticos + 518 de componente)

## 1. Objetivo

Caracterizar o terceiro recorte do Dashboard antes da migração visual, preservando integralmente comportamento, estrutura, banco e lógica. O recorte é exatamente o definido no roadmap de longo prazo:

- `dashboardTodayAction` — Recomendação do algoritmo;
- elementos `algorithm*` do card;
- CTA `dashboardTodayPrimaryButton` — “Começar agora”;
- ação secundária `dashboardTodayButton` — explicação da recomendação;
- `focusQuickCard[cardRole="progress"]` — “Seu progresso”;
- `dashboardQuickAccess[embedded="false"]` — Acessos rápidos;
- botões auxiliares dentro de Acessos rápidos.

## 2. Fora do escopo

Permanecem fora deste bloco:

- Foco e Planejamento de hoje já migrados no Bloco B;
- `dashboardQuickAccess[embedded="true"]`, usado no objetivo diário do Foco;
- Visão geral (`dashboardOverviewCard`);
- `DashboardDonutWidget` e qualquer outro `QPainter`;
- notificações/alertas;
- Estudo por questões;
- Planejamento completo;
- Regularidade e Conquistas ocultas fora do card compacto;
- lógica de Fila Inteligente, montagem da recomendação e ações dos botões.

## 3. Estrutura funcional preservada

A Recomendação é criada em `main.py` sem necessidade de alteração estrutural. O frame recebe simultaneamente:

- `actionRole="neutral"` na criação;
- `simpleHero=True`;
- `heroCentral=True` posteriormente.

Na atualização, `actionRole` pode assumir `neutral`, `late`, `strategic` ou `active`. A migração visual não deve corrigir nem reinterpretar a cascata histórica desses estados. O objetivo é reproduzir o estado visual efetivo atual.

O card “Seu progresso” usa:

- `focusQuickCard` com `cardRole="progress"`;
- `focusQuickIcon`;
- `dashboardProgressBadge`;
- `dashboardTodayProgress`;
- `subtleButton`.

Os Acessos rápidos usam outro `dashboardQuickAccess`, mas com `embedded=False`. Essa distinção é essencial para não capturar o `dashboardQuickAccess[embedded="true"]` já migrado dentro do Foco.

## 4. Comportamentos que não podem mudar

Devem permanecer byte a byte em `main.py`:

- abertura do modo um-clique;
- continuação de sessão pausada;
- explicação da recomendação;
- atualização de nível/XP/conquistas;
- abertura da tela de Conquistas;
- expansão/recolhimento de Acessos rápidos;
- Pausa, Estatísticas, Relatórios e Calendário;
- atualização de ícones da interface;
- persistência das seções do Dashboard.

## 5. Estado visual efetivo antes da migração

A cascata histórica contém várias camadas antigas. Para este bloco, a referência correta não é um bloco isolado, mas o resultado final efetivo do stylesheet do Bloco B.

### Tema Claro

- Recomendação: card branco, borda cinza-azulada, ícone azul claro, CTA azul médio e texto secundário azul discreto.
- Seu progresso: card branco, ícone azul-petróleo, progresso azul e ação vazada neutra.
- Acessos rápidos: faixa em branco/azul muito claro; botões auxiliares neutros; Pausa mantém identidade verde-água.

### Tema Escuro

- Recomendação: superfície azul-marinho muito escura, CTA em gradiente azul, corpo interno mais claro e controles azulados.
- Seu progresso: card em gradiente azul-petróleo escuro, progresso azul e ação secundária escura.
- Acessos rápidos: faixa azul-marinho; botões auxiliares escuros; Pausa mantém verde-água.

### Tema Futurista

- Recomendação: gradiente grafite, CTA violeta/índigo e ícone em gradiente grafite.
- Seu progresso: gradiente verde, textos claros, progresso verde-claro e botão secundário grafite.
- Acessos rápidos: gradiente grafite; botões auxiliares azul-marinho e Pausa em gradiente verde-azulado.

## 6. Ponto importante sobre `actionRole`

As regras históricas de `actionRole` existem, mas a composição atual também aplica `simpleHero` e `heroCentral`. Pela especificidade e ordem final da cascata, a aparência efetiva da recomendação fica dominada pelas regras do hero. O Bloco C deve **preservar esse resultado**, sem reativar diferenças visuais de `late`, `strategic` ou `active` como efeito colateral.

## 7. Estratégia de migração

A implementação deve ser aditiva:

1. criar tokens específicos de componente para este recorte;
2. criar gradientes próprios quando o tema Futurista já usa gradiente;
3. adicionar uma camada QSS final, estritamente escopada a `#dashboardRoot` e aos objetos do Bloco C;
4. não remover estilos legados nesta etapa;
5. não alterar geometria, fontes, espaçamentos, alturas ou raios;
6. não tocar em `main.py`;
7. não tocar em `QPainter`;
8. comprovar que remover a nova camada recupera exatamente os hashes QSS do Bloco B.

## 8. Baseline QSS do Bloco B

SHA-256 do stylesheet renderizado antes da implementação:

- Claro: `e64712aa2db6e76b96c602cdfa1f07368d600b230b6dcd22df69baf2c0d1b965`
- Escuro: `ec5f74a55f9dc27ee9d4224a38bc2274988d1f77399e4547fccb4a12dc8a2076`
- Futurista: `b3857bcefe2bbba078b6e05f3203b8c2a7664cf255537535c877c45eb8465753`

## 9. Arquivos protegidos na implementação

A etapa deve manter byte a byte, entre outros:

- `main.py`;
- `estudos.db`;
- `versao.py`;
- `foco.py`;
- `jogos.py`;
- `checkpoint.py`.

## 10. Critério de aprovação

O Bloco C só pode ser considerado tecnicamente pronto quando:

- a nova camada usar apenas tokens;
- não houver cor física literal no novo QSS;
- o escopo não alcançar o objetivo diário `embedded=true`;
- os três temas renderizarem sem marcadores não resolvidos;
- a remoção da camada C recuperar exatamente o QSS do Bloco B;
- banco e metadados permanecerem inalterados;
- testes anteriores continuarem com a mesma linha de base;
- a validação manual no Windows confirmar paridade visual e funcional.
