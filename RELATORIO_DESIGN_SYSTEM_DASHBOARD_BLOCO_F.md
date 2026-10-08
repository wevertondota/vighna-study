# VighnaStudy — Design System do Dashboard — Bloco F

## Relatório de implementação, regressão e checkpoint

**Base de entrada:** `VighnaStudy_0.29.59_DesignSystem_Dashboard_Bloco_E_COMPLETO(1).zip`
**Versão:** `0.29.59`
**Build:** `calendar-week-forecast-v1`
**Schema:** `25`
**Escopo:** Dashboard — **Planejamento completo**
**Método:** caracterização isolada, migração visual aditiva, escopo estrito, preservação de comportamento, prova de reversibilidade, testes cumulativos e validação de banco.

---

## 1. Estado de partida

O Bloco E era o checkpoint validado manualmente no Windows. Antes do Bloco F, o Design System possuía:

- **102 tokens semânticos**;
- **683 tokens de componente**;
- **785 tokens totais**.

Hashes canônicos do QSS da base E:

- Claro: `81f1c8fc6eebb10cd8dccea854795798f3871a11da372eea4baf02b5f71eb2c4`
- Escuro: `ef56315047f797aabc02a33118b97a4f6992c775e696c9b1d61509030df45186`
- Futurista: `29e36ecb0c7cbb06dfe15821c7c07b84ad6a81dc75a48f2d5fe56db70fe9079d`

O arquivo `main.py`, o banco e os metadados do aplicativo foram tratados como protegidos.

---

## 2. Caracterização prévia

A caracterização foi registrada em:

`RELATORIO_DESIGN_SYSTEM_DASHBOARD_BLOCO_F_CARACTERIZACAO.md`

O recorte operacional foi limitado ao painel:

`QWidget#dashboardRoot QFrame#planningPanel`

Foram incluídos os contratos visuais ativos do Planejamento completo, entre eles:

- painel e cabeçalho recolhível;
- Plano imediato;
- Meta de hoje e seus estados de progresso;
- Próximos 7 dias e níveis de carga;
- prioridade visual do dia atual;
- ações de meta, Jornada do Dia e Plano Automático;
- Resumo do planejamento;
- Redistribuição e sugestão disponível;
- Metas da semana;
- estados da meta semanal;
- métricas e barras de progresso semanais.

Foram preservadas as propriedades dinâmicas existentes:

- `goalState`;
- `weekState`;
- `loadLevel`;
- `today`;
- `hasPlan`;
- `hasSuggestion`;
- `journeyState`.

A persistência `dashboard_secao_planejamento_expandida` também permanece inalterada.

### Objetos compartilhados

`weeklyGoalStatus` e `planningSummaryButton` possuem consumidores fora deste painel. Por isso, o Bloco F não cria regras globais para esses objectNames: todas as novas regras permanecem descendentes de `#planningPanel`.

### Seletores históricos não promovidos

`weeklyGoalSetupButton` e `weeklyGoalEmptyDescription` não possuem consumidor ativo no recorte atual e não foram promovidos a contratos do Design System.

---

## 3. Implementação realizada

Foi criada a camada aditiva:

`ESTILO_DASHBOARD_BLOCO_F`

Ela é renderizada após o Bloco E nos três temas e todos os seus seletores são estritamente escopados a:

`QWidget#dashboardRoot QFrame#planningPanel`

Foram acrescentados **99 tokens de componente**:

- **82 tokens de cor**;
- **17 tokens de gradiente**.

Assim, o Design System passa para:

- **102 tokens semânticos**;
- **782 tokens de componente**;
- **884 tokens totais**.

A caracterização havia estimado preliminarmente até 108 novos contratos. A implementação final ficou 9 tokens abaixo dessa estimativa porque a leitura completa da cascata mostrou que alguns gradientes históricos do Futurista não eram valores efetivos: regras posteriores ou de maior especificidade já os substituíam. Foram centralizados os valores efetivamente exibidos, sem redesenhar o módulo.

Em ações que são visualmente sólidas nos temas Claro/Escuro, o contrato de background foi mantido como gradiente de stops idênticos. Isso preserva uma API visual uniforme para o mesmo componente sem alterar a aparência.

---

## 4. Arquivos de produção alterados

A implementação de produção ficou restrita a quatro arquivos:

- `ui/design/tokens.py` — registro dos novos contratos;
- `ui/design/palette.py` — valores físicos ainda ausentes na paleta central;
- `ui/design/themes.py` — mapeamento dos três temas e gradientes;
- `tema.py` — camada QSS tokenizada e composição após o Bloco E.

Não houve alteração em:

- `main.py`;
- `estudos.db`;
- `versao.py`;
- `foco.py`;
- `jogos.py`;
- `checkpoint.py`.

Os testes históricos que registram o snapshot global do Design System foram atualizados apenas para reconhecer a nova contagem, o novo snapshot QSS ou retirar a camada F antes de validar checkpoints anteriores.

---

## 5. Equivalência visual e isolamento

Foi feita comparação da cascata efetiva antes/depois para **64 estados/consumidores representativos do Planejamento completo** nos temas Claro, Escuro e Futurista.

Resultado material:

**0 diferenças visuais relevantes nas propriedades-alvo.**

A única diferença sintática encontrada foi `border-color: transparent` explicitado na barra de métrica semanal dos temas Claro/Escuro. O contrato vencedor continua com `border: none`, portanto essa declaração não produz mudança visual. No Futurista, a borda efetiva existente continua preservada.

Também foi verificado especificamente o risco de vazamento para o Planejamento compacto do Bloco B. Os consumidores compartilhados `weeklyGoalStatus` e `planningSummaryButton` mantêm a mesma cascata fora de `#planningPanel`.

**Vazamento detectado para o Bloco B: 0.**

---

## 6. Hashes QSS após o Bloco F

Hashes canônicos do QSS renderizado final:

- Claro: `197d1f1051896765152d637943a3c2c0660b81a4514f58a01867377a3144bebd`
- Escuro: `922d7951bf5edde14ab712112aff8484510bb48702e8f5307e6bef6476c6b1f5`
- Futurista: `dd3fb829eae39970f600047328bb905878f3a152b8b40eef44f9b4fa872a214b`

Não há marcadores `{{color:...}}` ou `{{gradient:...}}` não resolvidos no QSS final.

### Prova de reversibilidade

Retirando somente a camada F:

- o Claro recupera exatamente o hash do Bloco E;
- o Escuro recupera exatamente o hash do Bloco E;
- o Futurista recupera exatamente o hash do Bloco E após retirar sua camada F final e a camada F escura herdada.

Portanto, o Bloco F é aditivo e isolável em relação ao checkpoint E.

---

## 7. Testes específicos do Bloco F

Foi criado:

`test_design_system_dashboard_bloco_f.py`

Resultado:

**9/9 testes aprovados.**

A suíte verifica:

- orçamento final de 99 novos tokens;
- tipos de token (82 cores e 17 gradientes);
- valores representativos nos três temas;
- gradientes Futuristas;
- escopo estrito de todos os seletores;
- consumidores e propriedades dinâmicas do `main.py`;
- isolamento dos objectNames compartilhados;
- ausência de tokens não resolvidos;
- hashes QSS finais;
- rollback exato ao checkpoint E;
- hashes dos arquivos protegidos e metadados.

---

## 8. Bateria dirigida cumulativa

Foram executadas juntas as suítes:

- Dashboard Bloco A;
- Dashboard Bloco B;
- Dashboard Bloco C;
- Dashboard Bloco D;
- Dashboard Bloco E;
- Dashboard Bloco F;
- Jogos Passo 5;
- feedback/explicação B2g;
- Resumo Final Passo A;
- Resumo Final Passo B.

**Resultado: 86/86 testes aprovados.**

---

## 9. Suíte ampla e comparação com a base E

A varredura `test_design_system*.py` foi executada no ambiente Linux de análise.

### Base E

- 230 testes executados;
- 6 falhas históricas;
- 6 erros de ambiente/compatibilidade Qt.

### Bloco F

- 239 testes executados;
- 6 falhas históricas;
- 6 erros de ambiente/compatibilidade Qt.

As seis falhas são as mesmas já presentes na base E e pertencem ao teste histórico `test_design_system_resolvedor_enunciado_b2f.py`. Os seis erros também são os mesmos da base, associados à ausência de uma instalação Qt/PySide6 completa neste ambiente de análise.

**O Bloco F não adicionou nova falha nem novo erro à suíte ampla.**

---

## 10. Banco e arquivos protegidos

Validação do banco em modo somente leitura:

- `PRAGMA integrity_check`: **ok**;
- `PRAGMA foreign_key_check`: **0 violações**.

Hashes preservados:

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

A implementação está aprovada automaticamente, mas o Bloco F só deve ser considerado **concluído e validado** após a conferência manual no Windows.

Checklist recomendado:

1. abrir o Vighna com o tema **Claro** e conferir o Planejamento completo expandido/recolhido;
2. repetir em **Escuro** e **Futurista**;
3. verificar Meta de hoje em estado normal e concluído;
4. verificar os sete dias, incluindo dia atual e cargas leve/moderada/alta quando presentes;
5. verificar hover/pressed dos botões de meta, Jornada, Plano Automático, Resumo e Redistribuição;
6. conferir estados de Jornada existentes (`nova`, `pausada`, `encerrada`) quando alcançáveis;
7. conferir Plano Automático com/sem plano;
8. conferir Redistribuição com/sem sugestão;
9. conferir Metas da semana em estados desativada, andamento, atenção e concluída quando alcançáveis;
10. conferir barra de progresso semanal e estado concluído;
11. confirmar que o Planejamento compacto da primeira dobra não sofreu alteração visual;
12. confirmar que abrir, recolher e navegar pelo Dashboard preserva o comportamento e a persistência existentes.

Se os doze pontos forem aprovados, o ZIP deste relatório pode se tornar a nova base oficial para o próximo bloco do Dashboard.

---

## 12. Status

**Bloco F implementado e validado automaticamente.**
**Pendente:** validação manual no Windows pelo usuário.
