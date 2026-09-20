# Relatório — otimização da abertura do VighnaStudy

## Objetivo
Reduzir a espera de aproximadamente 3–4 segundos antes da primeira exibição do Dashboard.

## Ajustes aplicados
- o Vighna constrói apenas o **Dashboard** no caminho crítico de abertura;
- Disciplina, Sessão de estudo, Resumo do dia, Calendário, Central de Questões, Estatísticas e Relatórios passaram a ser criados no **primeiro acesso** e depois permanecem em memória;
- o tema global passou a ser aplicado depois da árvore inicial do Dashboard estar pronta, evitando recálculos de estilo durante a criação de telas que nem serão usadas naquele momento;
- a atualização analítica do Dashboard foi movida para o primeiro ciclo do event loop, permitindo que a janela apareça antes das consultas;
- o backup automático de abertura continua ativo, mas é disparado em thread após a interface aparecer;
- janelas auxiliares (Modo Foco, Pausa, Diagnóstico e Busca Global) passaram a ter importação lazy;
- `pypdf` agora só é importado quando uma importação PDF é realmente solicitada.

## Comportamento esperado
A janela principal deve aparecer sensivelmente antes. O primeiro acesso a uma tela secundária pode custar alguns décimos adicionais apenas uma vez; acessos seguintes usam a tela já criada.

## Segurança
- o `PRAGMA integrity_check` de abertura foi mantido;
- `criar_banco()` foi mantido no startup;
- o backup automático de abertura foi preservado;
- nenhuma regra do motor de estudo, fila, revisão ou estatísticas foi alterada.
