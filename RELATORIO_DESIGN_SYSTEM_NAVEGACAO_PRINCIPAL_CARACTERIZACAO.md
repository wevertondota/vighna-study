# VighnaStudy — Design System — Navegação principal

## Relatório de caracterização isolada

**Data:** 2026-10-07
**Base oficial analisada:** `VighnaStudy_0.29.59_DesignSystem_Dashboard_Bloco_I_COMPLETO.zip`
**SHA-256 da base:** `f5938a96e6aed5f03b4f1664a9090ffbf2472030f9e77d0dbd2f859e587bcfaa`
**Versão:** `0.29.59`
**Build:** `calendar-week-forecast-v1`
**Schema:** `25`
**Design System atual:** **972 tokens** = 102 semânticos + 870 de componente
**Status do macroescopo anterior:** Dashboard A–I formalmente encerrado e validado no Windows
**Alterações de produção nesta etapa:** **nenhuma**

---

## 1. Objetivo

Esta caracterização inicia o segundo macroitem da ordem de migração do Plano Mestre: **Navegação principal**.

A finalidade desta etapa é descobrir a arquitetura de navegação que realmente existe na versão atual do Vighna, separar o que já foi centralizado no macroescopo Dashboard do que ainda está ativo fora do Design System e definir um primeiro recorte implementável sem ampliar o risco de cascata.

Nenhum stylesheet, token, arquivo funcional, banco, comportamento de navegação ou atalho foi modificado.

---

## 2. Conclusão executiva

A Navegação principal atual **não é uma barra lateral persistente** nem um menu global único. Ela é composta por três mecanismos distintos:

1. **cabeçalho operacional do Dashboard**, de onde partem Busca global, Central de Questões, Configurações e troca de perfil;
2. **Busca global / command palette**, aberta por `Ctrl+K`, que funciona como o principal roteador transversal do aplicativo;
3. **controles de retorno ao Dashboard** existentes em telas secundárias, normalmente por botão `← Voltar` e também pelo atalho global `Ctrl+H`.

O primeiro mecanismo já foi centralizado no **Dashboard — Bloco A: Shell e cabeçalho**. Portanto, ele **não deve ser migrado novamente** no macroescopo Navegação principal.

O primeiro consumidor visual ativo ainda não centralizado e com fronteira segura é a janela **`JanelaBuscaGlobal`**, definida em `navegacao.py`.

### Decisão desta caracterização

**APROVADO PARA IMPLEMENTAÇÃO ISOLADA:** Busca global / command palette.

Não é recomendado migrar, no mesmo lote, os botões `← Voltar` das telas secundárias, porque eles reutilizam contratos genéricos compartilhados (`subtleButton`) e uma alteração global nesse seletor poderia atingir ações que não são de navegação.

---

## 3. O que já está concluído e não deve ser duplicado

O cabeçalho do Dashboard já centralizou no Bloco A:

- `dashboardTopBar`;
- `globalSearchTrigger`;
- `questionsNavButton`;
- `topAccentButton`;
- `topProfileBar`;
- `topProfileLabel`;
- `topProfileCombo`;
- `subtleButton` quando usado dentro do cabeçalho do Dashboard;
- título e subtítulo do Dashboard.

Essa migração já possui contratos `dashboard.*` próprios para busca, navegação, perfil, ação secundária e configuração, incluindo estados normal, hover e pressed quando existentes.

### Implicação

O bloco histórico `ESTILO_BUSCA_GLOBAL_*` ainda contém regras físicas para `globalSearchTrigger`, porém elas são hoje **sombreadas** pela camada final tokenizada do Dashboard. A futura implementação da Navegação principal não deve criar um segundo conjunto de tokens para esse gatilho.

A regra de preservação é:

> o botão que abre a Busca global continua pertencendo ao contrato visual do Dashboard; o diálogo aberto por ele passa a pertencer ao contrato da Navegação principal.

---

## 4. Arquitetura funcional da Navegação principal

### 4.1 Atalhos globais

`SistemaEstudos.configurar_atalhos_globais()` registra **8 atalhos**:

- `Ctrl+K` — Busca global;
- `Ctrl+F` — Modo Foco;
- `Ctrl+Shift+F` — restaurar/trazer Modo Foco;
- `F8` — alternar pausa do Modo Foco;
- `Ctrl+Shift+Q` — restaurar/trazer bateria de questões;
- `Ctrl+Q` — Central de Questões;
- `Ctrl+Shift+C` — checkpoint rápido;
- `Ctrl+H` — Dashboard.

Esses atalhos são **comportamento**, não aparência. Devem permanecer byte a byte equivalentes durante a centralização visual.

### 4.2 Catálogo da Busca global

`obter_comandos_busca_global()` expõe atualmente **18 comandos**, distribuídos em:

- 8 de ESTUDO;
- 4 de SISTEMA;
- 3 de NAVEGAÇÃO;
- 2 de ANÁLISE;
- 1 de PLANEJAMENTO.

A command palette também incorpora os tópicos incluídos do perfil ativo e conserva até 6 comandos recentes em `busca_global_recentes`.

A lógica de pesquisa faz normalização textual, pontuação por correspondência direta/aproximada e tolerância a pequenas variações de digitação. Nenhuma dessas rotinas faz parte do escopo visual.

### 4.3 Roteamento

`executar_comando_busca_global()` encaminha a seleção para os destinos já existentes, incluindo Dashboard, Foco, seções do Dashboard, revisão, treino adaptativo, simulado, Banco de Erros, Central de Questões, Estatísticas, Relatórios, Calendário, Pausa, Perfis, Configurações, Backup e Diagnóstico.

**Regra de proteção:** a implementação visual não deve alterar catálogo, prioridades, pesquisa, persistência de recentes, atalhos nem roteamento.

---

## 5. Primeiro recorte implementável — `JanelaBuscaGlobal`

Arquivo funcional: `navegacao.py`.

A janela possui **9 `objectName`**:

1. `globalSearchDialog`;
2. `globalSearchTitle`;
3. `globalSearchSubtitle`;
4. `globalSearchShortcut`;
5. `globalSearchInput`;
6. `globalSearchResults`;
7. `globalSearchStatus`;
8. `globalSearchHint`;
9. `globalSearchCloseButton`.

### Consumidores visuais ativos

Ativos e relevantes à aparência:

- `globalSearchDialog` — canvas/superfície do diálogo;
- `globalSearchTitle` — título;
- `globalSearchSubtitle`, `globalSearchStatus` e `globalSearchHint` — texto secundário/discreto;
- `globalSearchShortcut` — badge do atalho;
- `globalSearchInput` — campo de pesquisa, seleção de texto e foco;
- `globalSearchResults` — tabela, seleção e divisórias;
- `QHeaderView::section` dentro do diálogo — cabeçalho da tabela.

### Consumidor oculto

`globalSearchCloseButton` existe apenas como compatibilidade/fechamento programático, mas é criado com `setVisible(False)`. Não precisa de contrato cromático próprio nesta migração.

### Propriedades inefetivas no estado atual

O QSS Claro define `alternate-background-color` para a tabela, porém `JanelaBuscaGlobal` não ativa `setAlternatingRowColors(True)`. Assim, essa propriedade não participa da aparência atual e não precisa orientar o orçamento do primeiro recorte.

`gridline-color: transparent` também não é um consumidor cromático material, porque a tabela executa `setShowGrid(False)`.

---

## 6. Hardcodes ativos identificados

Os estilos da command palette permanecem em três blocos históricos:

- `ESTILO_BUSCA_GLOBAL_CLARO`;
- `ESTILO_BUSCA_GLOBAL_ESCURO`;
- `ESTILO_BUSCA_GLOBAL_FUTURISTA`.

A parte referente ao **diálogo** ainda usa valores cromáticos físicos e continua vencedora na cascata atual.

### Claro — contratos visuais ativos

- diálogo: `#F5F8FC`;
- título: `#10233F`;
- texto secundário: `#718096`;
- badge: `#EDF3FA`, `#49637F`, `#D1DEEB`;
- input: `#FFFFFF`, `#16263D`, `#BFD1E5`;
- seleção do input: `#CFE2FB`;
- foco do input: `#4B88CF`;
- tabela: `#FFFFFF`, `#203149`, `#D8E3EF`;
- seleção da tabela: `#E7F1FF`, `#174F8A`;
- divisor de item: `#EDF2F7`;
- cabeçalho: `#F4F7FB`, `#617187`, `#DBE5EF`.

### Escuro — contratos visuais ativos

- diálogo: `#0F1722`;
- título: `#F2F6FB`;
- texto secundário: `#8FA1B5`;
- badge: `#172334`, `#A9BDD2`, `#34495F`;
- input: `#111C2A`, `#EDF4FB`, `#3D5873`;
- seleção do input: `#315F91`;
- foco do input: `#6AA3DF`;
- tabela: `#111C2A`, `#DBE6F1`, `#30465E`;
- seleção da tabela: `#203D5D`, `#EAF5FF`;
- divisor de item: `#203044`;
- cabeçalho: `#142131`, `#90A4B8`, `#30445A`.

### Futurista — contratos visuais ativos

- diálogo: `#0F1520`;
- título: `#F3F7FB`;
- texto secundário: `#AEB7C4`;
- badge: `#232C38`, `#D3DBE5`, `#5D6774`;
- input: `#202833`, `#F3F7FB`, `#4C5563`;
- seleção do input: `#555AF0`;
- foco do input: `#8086FF`;
- tabela: `#1D2430`, `#DDE5EE`, `#465162`;
- seleção da tabela: `#343C8A`, `#F8FAFC`;
- divisor de item: `#2E3644`;
- cabeçalho: `#232C38`, `#C2CAD4`, `#465162`.

Nenhum gradiente é necessário para reproduzir a command palette atual.

---

## 7. Orçamento preliminar de tokens

A centralização pode ser feita conservadoramente com aproximadamente **20 novos tokens de componente, todos de cor**, por exemplo sob o domínio `navigation.command_*` ou nome equivalente definido na implementação.

Contratos materiais previstos:

1. canvas do diálogo;
2. título;
3. texto secundário/meta;
4. badge — superfície;
5. badge — texto;
6. badge — borda;
7. input — superfície;
8. input — texto;
9. input — borda;
10. input — seleção;
11. input — borda de foco;
12. resultados — superfície;
13. resultados — texto;
14. resultados — borda;
15. resultados — seleção de fundo;
16. resultados — texto selecionado;
17. resultados — divisor de item;
18. cabeçalho — superfície;
19. cabeçalho — texto;
20. cabeçalho — divisor/borda.

O número **não deve ser congelado antes da implementação**. Se um contrato semântico existente reproduzir exatamente o papel e os valores necessários sem criar acoplamento indevido, ele pode ser reutilizado. Do mesmo modo, não se deve criar token para `transparent` ou para propriedades atualmente inefetivas apenas para inflar cobertura.

Estimativa após esse recorte, se os 20 contratos forem necessários: **992 tokens totais**.

---

## 8. Risco de cascata

O risco deste primeiro recorte é **baixo a moderado**, desde que os novos seletores permaneçam estritamente escopados a:

`QDialog#globalSearchDialog`

### Riscos identificados

1. `QLabel`, `QLineEdit`, `QTableWidget` e `QHeaderView` possuem estilos globais em `tema.py`; usar seletores sem o pai `#globalSearchDialog` poderia vazar para dezenas de telas.
2. `globalSearchTrigger` está no mesmo bloco histórico `ESTILO_BUSCA_GLOBAL_*`, mas já pertence ao Dashboard A. A nova camada não deve sobrescrevê-lo por acidente.
3. O Futurista possui sua própria camada histórica de Busca global, além da herança estrutural do tema; a camada final precisa vencer de maneira explícita e previsível.
4. A tabela usa estado de seleção real; a comparação deve cobrir pelo menos uma linha selecionada e uma não selecionada.
5. O campo de busca precisa ser comparado em normal, foco e seleção de texto.

---

## 9. Controles de retorno — por que ficam fora do primeiro recorte

Foram localizados controles explícitos de retorno ao Dashboard em telas como:

- Central de Questões;
- Resumo do dia;
- Calendário;
- Relatórios;
- Estatísticas;
- Disciplina.

Além disso, há retornos ao Dashboard em fluxos de sessão e no Resolvedor.

O problema técnico é que cinco das telas principais reutilizam `subtleButton`, um `objectName` compartilhado por muitas ações que **não são navegação**. A Central de Questões usa `backButton`, que atualmente nem possui um contrato dedicado comparável aos demais.

Migrar esses botões no mesmo lote exigiria ou:

- alterar globalmente `subtleButton`, provocando risco de vazamento; ou
- introduzir um marcador visual específico (`objectName`/property) nos controles de retorno, o que aumenta o número de arquivos funcionais tocados.

### Decisão

Esses controles permanecem **fora do primeiro recorte**. Após a command palette, deve ser feita uma auditoria curta da Navegação principal para decidir se os retornos justificam um segundo recorte isolado ou se sua aparência deve ser absorvida posteriormente pela etapa de controles globais/compartilhados.

Isso evita transformar a Navegação principal em uma refatoração transversal de todos os botões secundários do sistema.

---

## 10. Arquivos que a primeira implementação provavelmente precisará alterar

Se a implementação seguir a caracterização, os arquivos de produção esperados são:

- `tema.py` — adicionar camada final tokenizada do diálogo e compô-la nos três temas;
- `ui/design/tokens.py` — novos contratos `navigation.*`;
- `ui/design/themes.py` — valores por tema;
- `ui/design/palette.py` — somente cores físicas ainda ausentes da paleta, se houver.

### Arquivos que **não precisam** ser alterados para esse recorte

- `main.py`;
- `navegacao.py`;
- `estudos.db`;
- `versao.py`;
- `foco.py`;
- `jogos.py`;
- `checkpoint.py`.

Os `objectName` existentes em `navegacao.py` são suficientes para uma migração exclusivamente visual.

---

## 11. Baseline e rollback

### Checkpoint de rollback

`VighnaStudy_0.29.59_DesignSystem_Dashboard_Bloco_I_COMPLETO.zip`

SHA-256:

`f5938a96e6aed5f03b4f1664a9090ffbf2472030f9e77d0dbd2f859e587bcfaa`

### Hashes protegidos atuais

- `main.py`: `0ef8b3214a566cfaf1d329e84d701bb0ca776b15bdf2e647dccbc6e4fb2a7cb7`;
- `tema.py`: `4184e806b6695f56bc7d3977bb2ac6d745de335850bade417a3c47aa9d18a105`;
- `navegacao.py`: `2cb3439a580cf867af9870750a82e06777718961dd84819e0705a96838c8b862`;
- `ui/design/tokens.py`: `70bc61276e312a7d02e83dba4cdc8f121bcb8dd3d7c8ca761bde288dcb0b1223`;
- `ui/design/themes.py`: `ce761cd6d2a17c02035b0af05cad2c43b1cbb6ce8ae0e25c133db727ff63d911`;
- `ui/design/palette.py`: `fc4e44d632c2bc573562e52613326c82a613adee270b80aa1ca7df8c6c2476bb`;
- `estudos.db`: `034940a33ea792957d8fafbf5c528db7cd895db69031696fbdd3f0a0ce5a41ef`;
- `versao.py`: `8436214451a591c0a3d3429f62d53c0c01cfc0cc7311d71e57fcf060f5b39642`;
- `foco.py`: `8fbe4659f3371683738a3fa239a789b3bca26ab47dc68f38a69829a33afd03ed`;
- `jogos.py`: `498aab65a2a13efa070ae2f912536b5ddc1aada31e23a28846def6a617492286`;
- `checkpoint.py`: `947295fdf2035d6f65d5d43f70e1d6e5e1c411d92eaca264a469a221b6b61c38`.

Hashes QSS do checkpoint final do Dashboard, para referência de rollback da próxima implementação:

- Claro: `43a889513b8b66814eba82e843b969f733f84eab74ab638f7ee622f82c7ab96c`;
- Escuro: `56dfdb0b68dfa37f58774c361d2f5809bea10cf05526f4fc88599ca13c5a87d0`;
- Futurista: `bac2f89881f1989aa89bc464a95b872b41bb06ee4f8f32b93134e42cc794fd70`.

### Reversibilidade exigida

A futura camada da command palette deve poder ser removida integralmente e devolver exatamente os QSS acima, sem exigir reversão de `main.py` ou `navegacao.py`.

---

## 12. Verificações realizadas nesta caracterização

- Design System importado sem Qt: **972 tokens** confirmados;
- `py_compile` aprovado para `navegacao.py`, `main.py`, `tema.py` e módulos centrais do Design System;
- `PRAGMA integrity_check` → **ok**;
- `PRAGMA foreign_key_check` → **0 violações**;
- nenhuma alteração de produção realizada;
- nenhum comando de navegação, atalho ou rota modificado.

O ambiente Linux atual não possui PySide6 real; portanto a renderização do diálogo não foi executada nesta etapa de caracterização. A metodologia mantém a validação visual final no Windows após a futura implementação.

---

## 13. Critérios de aceite da futura implementação

A implementação da Busca global só deve ser aprovada se:

1. reproduzir exatamente os valores visuais atuais em Claro, Escuro e Futurista;
2. manter `globalSearchTrigger` sob responsabilidade do Dashboard A;
3. alterar apenas a origem cromática da command palette;
4. não alterar dimensões, espaçamento, tipografia, pesquisa, ordenação, recentes, atalhos ou roteamento;
5. cobrir estado normal do diálogo, badge, input normal/focado, seleção de texto, tabela normal e linha selecionada;
6. não gerar vazamento para outros `QDialog`, `QLineEdit`, `QTableWidget` ou `QHeaderView`;
7. deixar `navegacao.py` byte a byte inalterado, salvo evidência técnica posterior que torne isso impossível;
8. permitir rollback exato ao QSS do checkpoint I;
9. manter banco, versão, build e schema intactos;
10. passar validação manual no Windows nos três temas.

---

## 14. Decisão final da caracterização

**NAVEGAÇÃO PRINCIPAL — CARACTERIZAÇÃO INICIAL CONCLUÍDA.**

A análise confirma que parte relevante da Navegação principal já foi absorvida pelo Dashboard A e não deve ser duplicada.

O próximo passo seguro é implementar **somente a Busca global / command palette (`JanelaBuscaGlobal`)** como primeiro recorte do macroescopo Navegação principal.

Após essa implementação e validação manual, fazer uma auditoria curta do macroescopo para decidir, com base no estado real, se os controles `← Voltar` exigem um segundo recorte próprio.

**Status:** APROVADO PARA IMPLEMENTAÇÃO ISOLADA DA BUSCA GLOBAL.
