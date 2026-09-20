# Ajuste do Dashboard — primeira dobra

Data: 2026-09-19
Versão: 0.29.3
Build: dashboard-primary-action-first-fold

## Objetivo

Fazer com que a recomendação do algoritmo apareça mais cedo em telas com menor altura útil, sem alterar o motor de inteligência nem a lógica de seleção da sessão.

## Alterações

- Os Acessos rápidos foram movidos para depois do conjunto “Recomendação do algoritmo + Seu resumo de hoje”.
- O cabeçalho recebeu compactação vertical leve.
- Os cards Foco e Seu progresso foram compactados verticalmente sem remover informações.
- A faixa de Acessos rápidos passou a funcionar como bloco independente e mais baixo.
- O texto do atalho foi padronizado para “Acessos rápidos”.
- A recomendação e o resumo permanecem lado a lado, preservando a proporção 3:1.

## Ordem visual resultante

1. Cabeçalho
2. Foco + Seu progresso
3. Recomendação do algoritmo + Seu resumo de hoje
4. Acessos rápidos
5. Estudo por questões e demais blocos

## Validação

- `python -m py_compile main.py tema.py`: OK
- `python -m unittest test_dashboard_inteligencia.py test_responsividade_navegacao.py test_responsividade_relatorios.py`: 17 testes OK
- `python testes_smoke.py`: mantém a falha preexistente em `foco histórico`; não relacionada ao ajuste visual deste build.
