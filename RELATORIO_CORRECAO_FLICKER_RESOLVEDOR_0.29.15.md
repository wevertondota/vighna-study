# VighnaStudy 0.29.15 — correção do flash visual entre questões

Data: 24/09/2026
Build: `resolver-transicao-sem-flicker-v1`
Schema: 22 (inalterado)

## Sintoma

Ao clicar em **Próxima questão**, um pequeno controle visual piscava por uma fração de segundo na região central da área de alternativas. No print fornecido, o artefato tem dimensões e aparência compatíveis com o controle de eliminação de alternativa (`QToolButton` com o símbolo de tesoura).

## Causa técnica

A área de alternativas é destruída e reconstruída a cada troca de questão. Havia duas condições capazes de produzir um repaint intermediário no Windows/Qt:

1. os frames antigos eram removidos do layout com `deleteLater()`, permanecendo vivos até o próximo ciclo do event loop;
2. os novos controles de cada alternativa eram criados sem parent explícito e só recebiam a hierarquia visual quando inseridos no layout.

Durante a recomposição, o sistema podia pintar isoladamente um dos pequenos controles antes de a nova geometria estar estabilizada.

## Correção

- a reconstrução das alternativas agora ocorre com atualizações visuais temporariamente suspensas por `setUpdatesEnabled(False)`;
- os widgets antigos são ocultados antes de `deleteLater()`;
- `QFrame`, `QToolButton`, `QRadioButton` e `QLabel` das alternativas recebem parent explícito desde a criação;
- as atualizações são reativadas somente depois de toda a nova lista estar montada;
- ao final, o container recebe um único `update()` já no estado final.

A lógica acadêmica, o banco de dados, os gabaritos, o fluxo de resposta e os estilos não foram alterados.

## Validação realizada

- `python -m py_compile main.py versao.py`: OK;
- teste estrutural `test_resolver_transicao_0_29_15.py`: 4/4 OK;
- `PRAGMA integrity_check`: `ok`;
- `PRAGMA foreign_key_check`: 0 violações;
- hash do `estudos.db` antes/depois: idêntico.

## Limitação do ambiente

O ambiente de correção não possui PySide6 instalado, portanto a reprodução visual final no compositor do Windows não pôde ser executada aqui. A alteração foi direcionada exatamente ao ciclo de vida dos widgets observado no código e ao artefato exibido no print. A validação visual final deve ser feita executando o projeto no Windows.
