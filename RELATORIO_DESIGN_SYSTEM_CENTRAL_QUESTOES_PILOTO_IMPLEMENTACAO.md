# VighnaStudy 0.29.59 — Design System — Central de Questões
## Piloto cromático: faixa de inventário — implementação e auditoria

**Data:** 08/10/2026
**Base original, preservada:** `VighnaStudy_0.29.59_DesignSystem_Modo_Foco_Integracao_Resolvedor_COMPLETO(1).zip`
**SHA-256 da base:** `1a3a2ce13809e182ffa54e30070803bfe60356946375a9d3bc7a675edc98d9b4`
**Versão/build/schema:** `0.29.59` / `calendar-week-forecast-v1` / `25` (sem alterações)
**Escopo:** somente as cores da faixa de inventário da Central de Questões.

## 1. Mudanças em produção

| Arquivo | Alteração |
|---|---|
| `tema.py` | Substituição de 5 declarações cromáticas em cada uma das 2 regras Claro/Escuro; mantém os seletores, outros atributos e ordem da cascata. |
| `ui/design/tokens.py` | Inclusão de 5 tokens de componente `questions_center.inventory_*`. |
| `ui/design/themes.py` | Mapeamentos por tema com os valores físicos originais (Claro, Escuro e Futurista). |
| `ui/design/palette.py` | Inclusão da única cor física ainda ausente: `#121C2D`. |

Foram migrados os quatro seletores `QFrame#questionsInventoryStrip`, `QLabel#questionsInventoryValue`, `QLabel#questionsInventoryLabel`, `QFrame#questionsInventoryDivider`.

Contratos criados:

| Token | Claro | Escuro | Futurista |
|---|---|---|---|
| `questions_center.inventory_surface` | `#FFFFFF` | `#121C2D` | `#121C2D` |
| `questions_center.inventory_border` | `#DBE3ED` | `#334155` | `#334155` |
| `questions_center.inventory_value_text` | `#4338CA` | `#A5B4FC` | `#A5B4FC` |
| `questions_center.inventory_label_text` | `#64748B` | `#94A3B8` | `#94A3B8` |
| `questions_center.inventory_divider` | `#E2E8F0` | `#334155` | `#334155` |

**Contagem de tokens:** 1025 → **1030** (5 novos componentes cromáticos). Nenhum token antigo foi modificado.

A cascata legada do tema Futurista continua: `stylesheet_escuro()` + overrides Futurista. O mapeamento futurista permanece explícito em `themes.py`, mas os seletores do piloto são efetivamente herdados do escuro.

## 2. Validação de equivalência

A composição integral de `tema.stylesheet_claro()`, `tema.stylesheet_escuro()` e `tema.stylesheet_futurista()` foi comparada com a versão original. Como `render_qss` devolve os hexadecimais em maiúsculas e o QSS antigo os escrevia em minúsculas, a comparação é **byte a byte após normalização somente da capitalização dos hexadecimais**. Fora essa capitalização, o QSS gerado permaneceu idêntico em cada tema.

| Tema | SHA-256 do QSS canônico, igual antes/depois | Resultado |
|---|---|---|
| Claro | `39462b13d99fc62f585b6d7881e41fc724dd4b681343358c97b2a7321ab2a1ac` | Conforme |
| Escuro | `3025a872da4f2e331ea0f9903b175cc940cdc43e256a83ed7809f9e027244ec5` | Conforme |
| Futurista | `ea2243c33271d031227c45fd1788d060f1f16759074e1ab8d36763de6b5b8826` | Conforme |

Todos os marcadores `{{color:...}}` e `{{gradient:...}}` foram resolvidos nos 3 estilos completos. Assim, as regras de propriedade, especificidade, pseudoestado, espaçamento, tipografia e ordem na cascata não mudaram. **Esta é uma evidência estática de equivalência, não uma validação visual nativa do Qt.**

## 3. Testes executados

- **12/12** — novo `test_design_system_central_questoes_piloto.py`: contrato, cores nos 3 temas, consumidores, seletores, resolução, paridade QSS completa, proteção de arquivos e integridade do SQLite.
- **28/28** — testes legados selecionados, aplicáveis ao estado atual: contrato/isolation do Design System, workspace e navegação das questões, ciclo persistente e 6 testes funcionais estáticos da Central de Seleção.
- **40/40 no conjunto direcionado**; `py_compile` sem falhas nos arquivos alterados, no teste de regressão e no `main.py`.
- `PRAGMA integrity_check = ok` e `PRAGMA foreign_key_check` sem linhas.
- `main.py`, `foco.py`, `navegacao.py`, `jogos.py`, `checkpoint.py`, `estudos.db`, `versao.py` mantêm hashes originais.

**Limites dos testes:** o ambiente de auditoria não tem `PySide6` instalado. Para comparar o QSS sem iniciar a GUI, foi usado somente um stub de importação de `QApplication`; não foi executado nenhum teste de renderização nativa. Os testes antigos com expectativas fixas de 1025 tokens ou hashes exatos do arquivo anterior não foram considerados compatíveis com uma migração legítima do contrato. O teste histórico da Central, que fixa versão/build `0.29.27`, teve apenas esse caso de versão excluído; os demais 6 casos foram executados. A bateria completa de testes dependentes de Qt deve ser executada no Windows antes do encerramento do piloto.

## 4. Integridade do pacote e rollback

O novo checkpoint é cópia do **ZIP original** com substituição estrita dos quatro arquivos de produção e adição deste relatório, do novo teste e do patch auditável. O banco continua sendo exatamente o original, sem migração de schema.

Para reverter, restaure o ZIP base cujo SHA-256 é informado no início. Alternativamente, o patch `PATCH_DESIGN_SYSTEM_CENTRAL_QUESTOES_PILOTO.diff` delimita as alterações para revisão com `git diff`/`git apply -R` quando aplicado a uma árvore Git compatível. Os arquivos `MANIFEST_SHA256.txt`, `PACOTE_MANIFEST.json` e `MAPA_TOKENS_DESIGN_SYSTEM.csv` preservados dentro do ZIP são **snapshots históricos**, não atestações da compilação 0.29.59-piloto.

## 5. Validação manual no Windows (pendente)

1. Faça backup da sua instalação atual e extraia o novo ZIP **em outra pasta**. Não misture arquivos com cópias anteriores.
2. Abra o VighnaStudy usando sua forma habitual de execução; confirme versão e acesso à Central de Questões.
3. Verifique a faixa de inventário (fundo, contorno, valores numéricos, rótulos e divisórias) nos temas Claro, Escuro e Futurista, comparando visualmente com a base anterior.
4. Confirme que filtros, consulta/seleção de questões, importação, abertura do Resolvedor, navegação e Modo Foco funcionam sem comportamento diferente.
5. No terminal com dependências instaladas, execute: `python -m unittest -v test_design_system_central_questoes_piloto`.
6. Reporte quaisquer discrepâncias visuais antes de avançar ao próximo conjunto da Central.

**Status:** implementação mínima concluída; piloto *aguardando validação manual no Windows*. Macroescopo **Central de Questões permanece aberto**.
