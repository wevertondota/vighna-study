# RELATÓRIO — AJUSTE DO MÓDULO FOCO / PROGRESSO

Data: 2026-09-18
Versão: 0.27.4
Build: `focus-progress-compact`
Schema: 19

## Objetivo
Refinar a área principal do Dashboard para remover a linha redundante de métricas acima do card **Foco** e aproveitar melhor a altura disponível. Ajustar também a visibilidade do botão de **Configurações**.

## Alterações realizadas

### 1. Linha redundante removida
Foi removida do layout visível a linha superior com:
- `0 min de foco hoje`
- `0 sessões hoje`
- `Meta semanal desativada`

Esses rótulos permanecem internamente apenas por compatibilidade com a rotina de atualização, mas não são mais exibidos no topo do módulo.

### 2. Cards subiram no layout
Com a remoção da linha redundante:
- os cards **Modo Foco** e **Seu progresso** passam a ocupar o espaço imediatamente abaixo do cabeçalho do bloco Foco;
- a composição ficou mais compacta e direta;
- a altura mínima dos cards foi levemente reduzida para melhorar o encaixe visual.

### 3. Ícone de Configurações
O botão de Configurações foi mantido como botão compacto de engrenagem, mas recebeu ajuste direto para ficar mais legível:
- fonte maior;
- peso maior;
- cor branca explícita.

## Arquivos alterados
- `main.py`
- `versao.py`

## Validação local
- `python -m py_compile main.py versao.py` ✅
- `python -m unittest -q test_gamificacao.py test_regularidade.py` ✅

## Resultado esperado
No Dashboard inicial:
- não deve mais existir a faixa de métricas acima dos cards do bloco Foco;
- os cards **Modo Foco** e **Seu progresso** devem subir;
- o botão de **Configurações** deve mostrar apenas uma engrenagem mais clara e visível.
