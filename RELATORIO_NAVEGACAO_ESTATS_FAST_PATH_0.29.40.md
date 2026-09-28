# VighnaStudy 0.29.40 — navegação sem refresh redundante em Estatísticas

## Objetivo
Eliminar microtravadas causadas por verificações e refreshes desnecessários ao alternar entre abas de Estatísticas que já foram pré-carregadas e continuam válidas.

## Diagnóstico
O startup já pré-calculava todas as abas de Estatísticas, mas o sinal `currentChanged` ainda chamava o fluxo de agendamento em toda troca de aba. Mesmo quando a aba estava limpa, o callback chegava a `atualizar_estatisticas()`, que validava data/perfil/resumo antes de concluir que não havia nada para atualizar.

## Ajustes aplicados
### 1) Fast path em memória
Foi criado `_estatisticas_visivel_precisa_atualizacao()`.

Quando a aba está limpa, o resumo está limpo, a data de referência é a de hoje e o perfil já foi sincronizado, a troca de aba agora termina sem:
- criar `QTimer`;
- consultar o perfil no SQLite;
- reconstruir tabelas;
- recalcular métricas;
- atualizar labels analíticos já válidos.

### 2) Dupla proteção contra trabalho obsoleto
O estado é verificado:
- antes de agendar o refresh;
- novamente quando o callback do timer é executado.

Assim, navegação rápida entre abas não executa um refresh que deixou de ser necessário no intervalo entre o clique e o callback.

### 3) Entrada em Estatísticas
Ao entrar na tela, o perfil ativo é validado uma única vez. Se o perfil mudou, as abas são invalidadas; depois disso, alternar entre elas usa somente estado em memória.

### 4) Perfil ativo
A troca de perfil agora invalida explicitamente:
- Estatísticas;
- Relatórios;
- Central de Questões.

Isso garante que o novo fast path nunca reaproveite como limpo um snapshot pertencente ao perfil anterior.

### 5) Dashboard
O Dashboard já possuía o fast path equivalente: `_agendar_atualizacao_dashboard()` retorna imediatamente quando `_dashboard_sujo` é falso e a data não mudou. Esse comportamento foi preservado.

## Comportamento esperado
- após o carregamento inicial, trocar entre abas de Estatísticas sem alterar dados deve ser essencialmente uma troca visual;
- depois de responder questões, revisar, usar Foco ou alterar dados, somente as visões invalidadas serão recalculadas;
- voltar ao Dashboard sem mudanças continua sem refresh;
- quando os dados realmente mudarem, o refresh necessário permanece postergado para depois do repaint.

## Arquivos alterados
- `main.py`
- `versao.py`
- `test_navegacao_estatisticas_fast_path_0_29_40.py`

## Validação
- `python -m py_compile main.py versao.py estatisticas_lazy.py`
- `python -m unittest -v test_estatisticas_lazy.py test_navegacao_estatisticas_fast_path_0_29_40.py`

## Versão
- `0.29.40`
- build: `navegacao-estatisticas-fast-path-v1`
