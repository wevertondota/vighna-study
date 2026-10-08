# VighnaStudy — Design System — Navegação principal

## Auditoria curta pós-Busca global

**Data:** 2026-10-07
**Base oficial auditada:** `VighnaStudy_0.29.59_DesignSystem_Navegacao_Busca_Global_COMPLETO.zip`
**SHA-256 da base:** `b32522817960c6b786687994b42f4fd576b5d7452486b459a96b77d337708fa6`
**Versão:** `0.29.59`
**Build:** `calendar-week-forecast-v1`
**Schema:** `25`
**Design System:** **992 tokens** = 102 semânticos + 890 de componente
**Busca global:** implementada e validada manualmente no Windows
**Alterações de produção nesta auditoria:** **nenhuma**

---

## 1. Objetivo

Esta auditoria verifica o que ainda resta do macroescopo **Navegação principal** depois da centralização e validação manual da Busca global / command palette.

O foco é responder, com base no código atual, se os controles `← Voltar` e demais retornos exigem um segundo recorte próprio ou se o macroescopo já pode ser encerrado.

Nenhum stylesheet, token, arquivo funcional, banco, atalho ou rota foi alterado.

---

## 2. Conclusão executiva

A Navegação principal **ainda não deve ser encerrada**.

A auditoria encontrou **seis controles ativos de retorno nas telas principais** que ainda recebem sua aparência de `QPushButton#subtleButton`, seletor nomeado compartilhado cuja camada vencedora permanece com valores cromáticos físicos em `tema.py`.

Esses seis controles são:

1. Resumo do dia;
2. Sessão de estudo;
3. Calendário;
4. Relatórios;
5. Estatísticas;
6. Disciplina.

Todos exibem `← Voltar`. Cinco chamam `self.voltar_inicio`; o botão da Sessão de estudo chama `self.pausar_sessao_estudo`, retornando ao Dashboard com a semântica adicional de pausar a sessão.

A **Central de Questões** também possui `← Voltar`, mas usa `objectName="backButton"`. Como não existe regra específica para `backButton`, esse controle herda o `QPushButton` genérico, que já foi centralizado na Etapa 3C por tokens semânticos. Portanto, **Central de Questões não é bloqueador**.

### Decisão

**É necessário um segundo e último recorte da Navegação principal:**

> **Navegação principal — Retornos ao Dashboard**

O recorte deve atingir somente os seis `subtleButton` de retorno das telas principais, sem alterar globalmente `subtleButton`.

---

## 3. Inventário dos `← Voltar` ativos

A varredura estática encontrou exatamente **7** criações de `QPushButton("← Voltar")` em `main.py`.

| Tela | Função | objectName | Ação | Situação |
|---|---|---|---|---|
| Central de Questões | `criar_tela_questoes` | `backButton` | `self.voltar_inicio` | já centralizado indiretamente pelo botão genérico |
| Resumo do dia | `criar_tela_resumo_dia` | `subtleButton` | `self.voltar_inicio` | pendente |
| Sessão de estudo | `criar_tela_sessao_estudo` | `subtleButton` | `self.pausar_sessao_estudo` | pendente |
| Calendário | `criar_tela_calendario` | `subtleButton` | `self.voltar_inicio` | pendente |
| Relatórios | `criar_tela_relatorios` | `subtleButton` | `self.voltar_inicio` | pendente |
| Estatísticas | `criar_tela_estatisticas` | `subtleButton` | `self.voltar_inicio` | pendente |
| Disciplina | `criar_tela_disciplina` | `subtleButton` | `self.voltar_inicio` | pendente |

O inventário foi verificado programaticamente: **6 `subtleButton` + 1 `backButton`**.

---

## 4. Por que `backButton` não exige um novo contrato

`tema.py` possui **0 seletores contendo `backButton`**.

Por isso, o botão da Central de Questões recebe a aparência do `QPushButton` genérico. Esse bloco já consome tokens do Design System, incluindo:

- `action.secondary`;
- `action.secondary_hover`;
- `action.secondary_pressed`;
- `action.secondary_disabled`;
- `text.primary`;
- `text.disabled`;
- `border.strong`;
- `border.hover`;
- `border.active`;
- `border.disabled`.

Assim, a origem cromática efetiva desse botão já está centralizada, ainda que seu `objectName` seja específico.

---

## 5. Por que os seis `subtleButton` ainda são pendência real

`main.py` contém **65 usos de `setObjectName("subtleButton")`**. O seletor é compartilhado por ações de edição, cancelamento, ajuda, visualização, manutenção, sessões, relatórios, Dashboard e outros fluxos.

Alterar `QPushButton#subtleButton` globalmente dentro do macroescopo Navegação principal seria inadequado porque atingiria dezenas de controles que não são navegação.

Os seis retornos principais, entretanto, são consumidores visuais ativos da Navegação principal e ainda dependem dos seguintes valores físicos vencedores:

### Claro

Normal:

- superfície `#FFFFFF`;
- texto `#334155`;
- borda `#CFD8E3`.

Hover:

- superfície `#F6FBFF`;
- texto `#235F98`;
- borda `#9FC7E7`.

### Escuro

Normal:

- superfície `#162333`;
- texto `#DCE6F0`;
- borda `#33475E`.

Hover:

- superfície `#1C3145`;
- texto `#9BD5FF`;
- borda `#4D89B8`.

### Futurista

Normal:

- gradiente diagonal `#162B42 → #0D1D30`;
- texto `#E7F5FF`;
- borda `#40688D`.

Hover:

- gradiente diagonal `#1A3854 → #10263D`;
- texto `#C8F6FF`;
- borda `#56DFFF`.

Esses valores permanecem em blocos históricos de compatibilidade e ainda são a origem efetiva da aparência desses seis botões.

---

## 6. Estratégia recomendada para o segundo recorte

A alternativa de menor risco é **preservar `objectName="subtleButton"`** e acrescentar somente uma propriedade dinâmica aos seis retornos principais, por exemplo:

`navigationBack = true`

A camada final do Design System poderá então usar seletores de alta precisão, como:

`QPushButton#subtleButton[navigationBack="true"]`

Isso evita:

- mudar a aparência dos outros 59 usos de `subtleButton`;
- renomear objectNames existentes;
- alterar callbacks;
- alterar o comportamento das telas;
- transformar a etapa em uma migração global de botões nomeados.

### Arquivos funcionais previstos

A implementação provavelmente exigirá alteração mínima em `main.py`: apenas seis `setProperty(...)`, um em cada botão identificado.

Não há evidência de necessidade de alterar:

- `navegacao.py`;
- banco;
- versão;
- build;
- schema;
- callbacks;
- atalhos globais;
- lógica de `QStackedWidget`.

---

## 7. Orçamento preliminar

O recorte é pequeno. A estimativa é de **aproximadamente 6–8 novos tokens de componente**, dependendo da forma final usada para representar os fundos sólidos de Claro/Escuro e os dois gradientes do Futurista.

Papéis materiais esperados:

- fundo normal;
- texto normal;
- borda normal;
- fundo hover;
- texto hover;
- borda hover;
- gradiente normal Futurista, se separado;
- gradiente hover Futurista, se separado.

O orçamento não deve ser congelado antes da implementação. O objetivo é usar o menor contrato capaz de preservar exatamente a aparência atual nos três temas.

---

## 8. Retornos que ficam fora deste recorte

Foram encontrados **3 textos explícitos `Voltar ao Dashboard`** em fluxos modais/de sessão. Eles não pertencem ao retorno entre telas principais do `QStackedWidget` e possuem donos funcionais próprios:

- resumo da resolução de questões;
- próxima recomendação do algoritmo;
- resumo da sessão.

Também existem retornos e ações de navegação em Resolvedor, Foco, Pausa e jogos. Esses controles pertencem aos seus respectivos módulos e não devem ser puxados para um contrato global de Navegação principal apenas por conterem a palavra “Dashboard” ou “Voltar”.

Em especial, o botão `Dashboard` do Resolvedor já possui a propriedade `sessionNavigation=true` e contrato próprio da etapa do Resolvedor.

Essa delimitação evita sobreposição de ownership entre módulos.

---

## 9. O que já está concluído no macroescopo

Após a Busca global validada no Windows, estão resolvidos:

- cabeçalho operacional do Dashboard — já centralizado no Dashboard A;
- gatilho visual da Busca global — Dashboard A;
- Central de Questões no cabeçalho — Dashboard A;
- Configurações no cabeçalho — Dashboard A;
- seletor de perfil no cabeçalho — Dashboard A;
- command palette `JanelaBuscaGlobal` — 20 tokens `navigation.command_*`;
- `Ctrl+K`, `Ctrl+H` e demais atalhos — comportamento preservado;
- botão `← Voltar` da Central de Questões — aparência herdada do botão genérico já tokenizado.

O único grupo material ainda pendente dentro da navegação entre telas principais é o conjunto dos **seis `← Voltar` com `subtleButton`**.

---

## 10. Verificações realizadas

Na base oficial atual:

- Design System: **992 tokens** confirmados;
- teste específico da Busca global: **9/9 aprovado**;
- testes de navegação aplicáveis `test_responsividade_navegacao.py` + `test_ver_questoes_topico_navegacao.py`: **12/12 aprovados**;
- `py_compile` de `main.py`, `navegacao.py`, `tema.py` e módulos centrais do Design System: **OK**;
- `PRAGMA integrity_check`: **ok**;
- `PRAGMA foreign_key_check`: **0 violações**;
- auditoria estática dos `← Voltar`: **7/7 classificados**;
- `subtleButton` em `main.py`: **65 consumidores**;
- propriedade específica de retorno de navegação atualmente existente: **0**;
- alterações de produção durante esta auditoria: **0**.

Uma bateria histórica mais ampla de testes de navegação foi também inspecionada. Os problemas observados nela foram somente três asserções de versões antigas (`0.29.40`, `0.29.56`, `0.29.57`) e um erro ambiental por ausência de PySide6 no Linux; não indicam regressão da base atual.

---

## 11. Critérios de aceite do segundo recorte

A implementação de **Retornos ao Dashboard** só deve ser aprovada se:

1. atingir exatamente os seis `subtleButton` de `← Voltar` das telas principais;
2. não alterar os outros usos de `subtleButton`;
3. manter a Central de Questões visualmente inalterada;
4. reproduzir exatamente normal/hover em Claro, Escuro e Futurista;
5. preservar os gradientes Futuristas atuais;
6. manter textos, dimensões, callbacks e tooltips;
7. não alterar `voltar_inicio` nem `pausar_sessao_estudo`;
8. preservar `Ctrl+H` e demais atalhos;
9. permitir rollback exato ao checkpoint da Busca global;
10. manter banco, versão, build e schema intactos;
11. passar validação manual no Windows nas sete telas principais.

---

## 12. Decisão final

**NAVEGAÇÃO PRINCIPAL — AINDA NÃO ENCERRADA.**

A auditoria justifica tecnicamente **um segundo recorte isolado e pequeno**:

> **Navegação principal — Retornos ao Dashboard**

O recorte deverá centralizar somente os seis `← Voltar` que ainda dependem do `subtleButton` hardcoded, usando marcação específica para evitar qualquer mudança nos demais 59 consumidores do mesmo objectName.

Após a implementação e validação manual desse recorte, uma auditoria final curta deverá confirmar o encerramento do macroescopo Navegação principal. Não há, no estado atual, evidência de necessidade de um terceiro recorte.
