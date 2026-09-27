# VighnaStudy 0.29.38 — Fundo do card `Planejamento de hoje` equalizado

## Objetivo
Remover o fundo verde do card `Planejamento de hoje` e alinhar sua base visual ao mesmo fundo dos cards `Foco` e `Recomendação do algoritmo`.

## Arquivos alterados
- `tema.py`
- `versao.py`
- `test_dashboard_planejamento_fundo_0_29_38.py`

## Ajustes aplicados
### 1) Fundo do card
- substituição do gradiente verde por um gradiente escuro da mesma família do Dashboard futurista;
- borda harmonizada com os cards vizinhos.

### 2) Elementos internos
- ícone, títulos, detalhes, divisor e botão inferior reequilibrados para o novo fundo escuro;
- manutenção do indicador em arco semicircular implantado na versão anterior.

### 3) Coerência visual
- o card `Planejamento de hoje` agora conversa com `Foco` e `Recomendação do algoritmo` em superfície e contraste, sem perder a hierarquia interna.

## Validação executada
- `python -m py_compile main.py tema.py versao.py`
- `python -m unittest -v test_dashboard_planejamento_fundo_0_29_38.py`

## Versão
- `0.29.38`
- build: `dashboard-planejamento-fundo-equalizado-v1`
