# RELATÓRIO — DASHBOARD: MODO FOCO + SEU PROGRESSO

Data: 2026-09-18
Versão: 0.27.3
Build: `dashboard-focus-progress`
Schema: 19

## Objetivo
Reorganizar o principal quadrante do Dashboard para deixar de usar metade do espaço com um card separado de **Sessão rápida** e aproveitar essa área para um card de **Seu progresso**.

## Alterações

### Cabeçalho
O chip de XP foi retirado do cabeçalho para evitar duplicação de informação. O topo permanece dedicado a:
- marca;
- busca global;
- Central de Questões;
- Configurações;
- perfil ativo.

### Card esquerdo — Modo Foco
O Modo Foco continua sendo a ação principal.

A antiga Sessão rápida foi incorporada ao card em uma faixa compacta:
- 5 min;
- 10 min;
- 15 min;
- botão `Rápida` para iniciar imediatamente a duração selecionada.

A sessão completa continua disponível pelo botão principal `Iniciar Foco`.

### Card direito — Seu progresso
Novo card dedicado à progressão do Vighna:
- badge circular com nível;
- nível atual;
- XP total;
- barra de progresso do nível;
- XP atual / XP requerido para o próximo nível;
- quantidade de conquistas;
- próxima conquista mais próxima;
- acesso direto a `Estatísticas → Conquistas`.

O card consome o mesmo snapshot oficial de gamificação já existente; não introduz nova fórmula de XP.

## Compatibilidade
- Regularidade continua fora do Dashboard principal.
- A aba `Estatísticas → Conquistas` continua sendo a visão detalhada.
- A gamificação continua sem alterar Fila Inteligente, domínio, evidência, revisão ou agendamento.
- Fila Inteligente V3 permanece decisória.

## Validação
- `python -m py_compile main.py versao.py` ✅
- `python -m unittest discover -q` → 199 testes aprovados ✅
- `python testes_smoke.py` ✅
- `PRAGMA integrity_check` → `ok` ✅
- `PRAGMA foreign_key_check` → 0 violações ✅
- checkpoint nativo completo e validado ✅

## Observação visual
A validação final de proporção e espaçamento deve ser feita no Windows com PySide6, especialmente em 1366 px de largura.
