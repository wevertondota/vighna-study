# RELATÓRIO — AJUSTE DO DASHBOARD: XP COMPACTO NO CABEÇALHO

Data: 2026-09-18
Versão: 0.27.1
Build: `dashboard-xp-compact`
Schema: 19

## Objetivo
Deixar o Dashboard inicial mais limpo, retirando os painéis horizontais de **Regularidade** e **Conquistas** da área principal, mantendo apenas um indicador compacto de XP/progresso no cabeçalho.

## Alterações realizadas

### 1. Cabeçalho
Foi criado um chip compacto de gamificação ao lado do bloco **Perfil ativo**.

Conteúdo exibido:
- nível atual;
- XP total;
- progresso até o próximo nível;
- quantidade de marcos conquistados no subtítulo.

Comportamento:
- clique no chip abre `Estatísticas → Conquistas`.

### 2. Dashboard principal
Os painéis:
- `Regularidade`;
- `Conquistas`;

foram mantidos internamente para compatibilidade, mas ficaram **ocultos no layout principal**.

Isso reduz a altura visual do Dashboard e devolve foco para:
- Foco;
- Sessão rápida;
- Acessos rápidos;
- demais cards operacionais.

### 3. Atualização de dados
A rotina `atualizar_gamificacao_dashboard()` passou a atualizar dois destinos:
- os rótulos internos do painel de Conquistas (compatibilidade);
- o novo chip compacto do cabeçalho.

## Arquivos alterados
- `main.py`
- `versao.py`

## Validação local
- `python -m py_compile main.py versao.py` ✅
- `python -m unittest -q test_gamificacao.py test_regularidade.py` ✅

## Resultado esperado
No Dashboard inicial:
- não devem mais aparecer os blocos horizontais de Regularidade e Conquistas;
- deve aparecer, próximo ao seletor de perfil, um chip como:
  - `Nível 2 · 255 XP`
  - barra curta de progresso;
  - subtítulo com progresso/marcos.

## Observação
A camada de gamificação continua sem interferir na Fila Inteligente e continua acessível integralmente em `Estatísticas → Conquistas`.
