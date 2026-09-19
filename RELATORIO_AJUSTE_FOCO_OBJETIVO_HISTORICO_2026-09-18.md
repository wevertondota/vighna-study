# RELATÓRIO — FOCO COM OBJETIVO DIÁRIO E HISTÓRICO

Data: 2026-09-18
Versão: 0.27.5
Build: `focus-goal-history`
Schema: 19

## Objetivo
Simplificar o quadrante principal do Dashboard e tornar o card de Foco mais informativo.

## Alterações visuais

### Cabeçalho externo removido
Foi removido do layout visível o cabeçalho redundante:
- ícone externo;
- título `Foco`;
- subtítulo explicativo;
- data no canto direito.

O próprio card esquerdo passa a se chamar **Foco** e representa diretamente o módulo.

### Sessão rápida removida
Foram retirados do card:
- presets de 5/10/15 minutos;
- botão `Rápida`;
- texto `10 min selecionados • início imediato`.

As rotinas internas antigas podem permanecer no código por compatibilidade, mas não são mais expostas no Dashboard.

### Novo bloco `Objetivo de hoje`
O espaço passou a mostrar:
- objetivo diário derivado da meta semanal;
- progresso `foco realizado / objetivo diário` quando houver meta;
- barra de progresso;
- mensagem para definir meta quando a meta estiver desativada;
- última sessão de foco válida;
- melhor sessão da semana.

### Histórico de foco
`obter_resumo_foco()` agora retorna também:
- `ultima_sessao`;
- `melhor_sessao_semana`.

Esses dados são globais de foco e não alteram métricas acadêmicas nem Fila Inteligente.

### Configurações
O botão de Configurações continua exibindo apenas uma engrenagem e recebeu reforço visual de tamanho/peso para maior legibilidade.

## Validação
- `python -m py_compile main.py banco.py versao.py` ✅
- `python -m unittest discover -q` → 199 testes ✅
- `python testes_smoke.py` ✅
- SQLite `PRAGMA integrity_check` → `ok` ✅
- `PRAGMA foreign_key_check` → 0 violações ✅

## Observações
O ambiente de validação não possui a interface PySide6 disponível para inspeção visual final; o ajuste visual deve ser conferido no Windows do usuário.
