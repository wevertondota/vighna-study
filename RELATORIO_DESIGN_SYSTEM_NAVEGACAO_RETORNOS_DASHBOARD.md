# RELATÓRIO TÉCNICO — DESIGN SYSTEM — NAVEGAÇÃO PRINCIPAL — RETORNOS AO DASHBOARD

**Projeto:** VighnaStudy
**Versão:** 0.29.59
**Build:** `calendar-week-forecast-v1`
**Schema:** 25
**Data:** 2026-10-07
**Base de implementação:** `VighnaStudy_0.29.59_DesignSystem_Navegacao_Busca_Global_COMPLETO.zip`
**Status:** implementação e validação automatizada concluídas; validação manual no Windows pendente.

## 1. Objetivo

Concluir o segundo recorte da macroetapa **Navegação principal**, centralizando a aparência dos retornos `← Voltar` das seis telas principais que ainda dependiam do seletor histórico compartilhado `QPushButton#subtleButton`.

O recorte foi definido pela auditoria pós-Busca global para evitar qualquer migração global de `subtleButton`, que é reutilizado em diversos controles sem função de navegação.

## 2. Escopo implementado

Foram marcados exclusivamente os botões `← Voltar` criados pelas funções:

1. `criar_tela_resumo_dia` — callback preservado: `self.voltar_inicio`;
2. `criar_tela_sessao_estudo` — callback preservado: `self.pausar_sessao_estudo`;
3. `criar_tela_calendario` — callback preservado: `self.voltar_inicio`;
4. `criar_tela_relatorios` — callback preservado: `self.voltar_inicio`;
5. `criar_tela_estatisticas` — callback preservado: `self.voltar_inicio`;
6. `criar_tela_disciplina` — callback preservado: `self.voltar_inicio`.

A Central de Questões permaneceu fora do recorte porque seu retorno usa `objectName="backButton"` e já é atendido pelo contrato visual existente.

## 3. Estratégia de isolamento

O `objectName="subtleButton"` foi preservado. Em cada um dos seis retornos foi adicionada somente a propriedade dinâmica:

```python
voltar.setProperty(
    "navigationBack",
    True
)
```

A nova camada QSS usa exclusivamente:

```css
QPushButton#subtleButton[navigationBack="true"]
QPushButton#subtleButton[navigationBack="true"]:hover
```

Uma varredura final por regex encontrou **96 ocorrências** de `setObjectName("subtleButton")` no `main.py`; somente **6** recebem `navigationBack`. Assim, os outros **90 consumidores** permanecem fora da nova camada.

## 4. Tokens adicionados

Foram adicionados **6 tokens de componente**:

### Cores — 4
- `navigation.back_text`
- `navigation.back_border`
- `navigation.back_hover_text`
- `navigation.back_hover_border`

### Gradientes — 2
- `navigation.back_surface_gradient`
- `navigation.back_hover_surface_gradient`

Contagem do Design System:

- antes: **992** tokens = 102 semânticos + 890 de componente;
- depois: **998** tokens = 102 semânticos + 896 de componente.

## 5. Paridade visual preservada

Os valores históricos vencedores foram reproduzidos exatamente.

| Tema | Estado normal | Texto | Borda | Hover | Texto hover | Borda hover |
|---|---|---|---|---|---|---|
| Claro | `#FFFFFF` | `#334155` | `#CFD8E3` | `#F6FBFF` | `#235F98` | `#9FC7E7` |
| Escuro | `#162333` | `#DCE6F0` | `#33475E` | `#1C3145` | `#9BD5FF` | `#4D89B8` |
| Futurista | `#162B42 → #0D1D30` | `#E7F5FF` | `#40688D` | `#1A3854 → #10263D` | `#C8F6FF` | `#56DFFF` |

No Futurista foi preservada a direção diagonal `x1:0, y1:0, x2:1, y2:1`. Claro e Escuro usam o mesmo mecanismo de gradiente com extremos iguais para manter um contrato único sem alterar a aparência.

## 6. Arquivos de produção alterados

### `main.py`
Alteração limitada às seis marcações `navigationBack=True`. O diff contra a base contém somente esses seis blocos. Removendo-os, o SHA-256 retorna exatamente ao checkpoint da Busca global:

`0ef8b3214a566cfaf1d329e84d701bb0ca776b15bdf2e647dccbc6e4fb2a7cb7`

SHA-256 atual:

`66a8dadf431b1eecb3467124856319dc6b7e797dc9bf4f52901a104b6fe174ad`

### `tema.py`
Adicionada a camada `ESTILO_NAVEGACAO_RETORNOS_DASHBOARD`, composta depois da Busca global nos três temas. O rollback da camada recupera exatamente o hash da base da Busca global.

SHA-256 atual:

`f48d44a124b43cb2019594c67d3ba761b0ecaf678982cf905c6beac968d36f55`

### `ui/design/tokens.py`
Adicionados 4 contratos de cor e 2 de gradiente.

SHA-256 atual:

`05b25411e1e454a06241c1e375a56bb34edbf79f7fe0fb7149556398bd3f138f`

### `ui/design/themes.py`
Adicionados os valores dos seis contratos para Claro, Escuro e Futurista.

SHA-256 atual:

`f084674c8beffbcbf48d38ebd6224cd45224293c69ae9ed9c13ec68cb57bd719`

### `DESIGN_SYSTEM.md`
Documentação atualizada para registrar o recorte.

## 7. Arquivos protegidos preservados

Permaneceram byte a byte iguais ao checkpoint da Busca global:

- `navegacao.py` — `2cb3439a580cf867af9870750a82e06777718961dd84819e0705a96838c8b862`;
- `estudos.db` — `034940a33ea792957d8fafbf5c528db7cd895db69031696fbdd3f0a0ce5a41ef`;
- `versao.py` — `8436214451a591c0a3d3429f62d53c0c01cfc0cc7311d71e57fcf060f5b39642`;
- `foco.py` — `8fbe4659f3371683738a3fa239a789b3bca26ab47dc68f38a69829a33afd03ed`;
- `jogos.py` — `498aab65a2a13efa070ae2f912536b5ddc1aada31e23a28846def6a617492286`;
- `checkpoint.py` — `947295fdf2035d6f65d5d43f70e1d6e5e1c411d92eaca264a469a221b6b61c38`;
- `ui/design/palette.py` — `f1545db7520fe5ec6f471ac84257c85a1fe8e89dc8ad060a85ad7fba8cc07aed`.

Não houve alteração de versão, build ou schema.

## 8. Validação automatizada

### Teste específico + regressão da Busca global

`test_design_system_navegacao_retornos_dashboard.py` + `test_design_system_navegacao_busca_global.py`:

**19/19 aprovados** — sendo 10 testes novos do recorte e 9 da Busca global.

O teste específico comprova:

- exatamente seis retornos marcados;
- Central de Questões excluída;
- camada QSS restrita à propriedade dinâmica;
- valores históricos exatos nos três temas;
- gradientes preservados;
- composição posterior à Busca global;
- rollback exato de `main.py` e `tema.py`;
- arquivos protegidos, banco, versão, build e schema preservados.

### Bateria dirigida cumulativa

Blocos Dashboard A–I + módulos dirigidos de Resolvedor/Jogos/Resumo final + Busca global + Retornos:

**131/131 aprovados**.

### Navegação funcional

`test_responsividade_navegacao.py` + `test_ver_questoes_topico_navegacao.py`:

**12/12 aprovados**.

Foram preservados, entre outros, `Ctrl+H`, retorno responsivo ao Dashboard, carga lazy da Central e navegação contextual de questões.

### Suíte ampla de Design System

- checkpoint Busca global: **274 testes; 8 falhas históricas + 7 erros ambientais**;
- recorte Retornos: **284 testes; as mesmas 8 falhas históricas + os mesmos 7 erros ambientais**.

O conjunto de nomes das 15 ocorrências é exatamente idêntico entre base e implementação. Portanto, não surgiu falha nova atribuível ao recorte.

### Compilação

`py_compile` aprovado para:

- `main.py`;
- `tema.py`;
- `ui/design/tokens.py`;
- `ui/design/themes.py`;
- `ui/design/palette.py`.

### Banco

- `PRAGMA integrity_check`: **ok**;
- `PRAGMA foreign_key_check`: **0 violações**.

### Resolução QSS

Claro, Escuro e Futurista: **0 marcadores `{{color:...}}` ou `{{gradient:...}}` não resolvidos** no stylesheet final.

## 9. Ajustes em testes históricos

Testes históricos que retiram camadas posteriores para comparar snapshots antigos foram atualizados para retirar também `ESTILO_NAVEGACAO_RETORNOS_DASHBOARD`. Isso é manutenção de compatibilidade da suíte e não mudança de produção.

Os snapshots globais atuais usados por três testes dirigidos também foram atualizados para refletir a nova camada legítima. O resultado final da suíte ampla voltou exatamente ao mesmo passivo histórico do checkpoint anterior.

## 10. Checklist de validação manual no Windows

Validar nos temas **Claro, Escuro e Futurista**:

1. abrir **Resumo do dia** e testar `← Voltar` normal e hover;
2. abrir **Sessão de estudo** e testar `← Voltar`, inclusive o comportamento de pausa já existente;
3. abrir **Calendário** e testar retorno;
4. abrir **Relatórios** e testar retorno;
5. abrir **Estatísticas** e testar retorno;
6. abrir uma **Disciplina** e testar retorno;
7. abrir **Central de Questões** e confirmar que seu `backButton` não mudou inesperadamente;
8. testar `Ctrl+H` e o fluxo de retorno ao Dashboard;
9. observar outros botões `subtleButton` em telas diversas e confirmar ausência de alteração visual;
10. repetir os pontos relevantes nos três temas, especialmente os gradientes do Futurista.

## 11. Conclusão

O recorte **Navegação principal — Retornos ao Dashboard** foi implementado de forma isolada, reversível e sem mudança comportamental conhecida.

**Resultado automatizado: APROVADO.**

A macroetapa Navegação principal **ainda não deve ser formalmente encerrada** até a validação manual deste checkpoint no Windows. Após aprovação manual, deve ser executada uma auditoria final curta de encerramento da Navegação principal antes de avançar ao próximo macroitem do Plano Mestre.
