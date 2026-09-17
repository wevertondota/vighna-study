# Ajuste do quadrante guiado do Dashboard

Arquivos alterados:
- `main.py`
- `tema.py`

## O que foi ajustado

1. Reorganização do quadrante "Recomendado pelo algoritmo".
2. O botão de ajuda `?` saiu do card interno esquerdo e foi para o topo do bloco principal.
3. O card esquerdo (Modo guiado) ficou mais limpo e equilibrado.
4. O card direito (Próximo passo) passou a usar empilhamento vertical estável, com melhor distribuição do botão "Começar agora" e do link "Por que esta recomendação?".
5. O botão principal recebeu largura máxima controlada para evitar excesso visual.
6. A largura mínima do card de ação foi reduzida para deixar o quadrante mais proporcional.

## Validação

- `python -m py_compile main.py tema.py`
