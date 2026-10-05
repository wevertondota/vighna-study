# VighnaStudy 0.29.57 — terceiro Enter avança a bateria

## Objetivo
Completar o fluxo de resolução de questões pelo teclado sem necessidade do mouse.

## Fluxo do Enter
1. Primeiro Enter: seleciona a alternativa atualmente focada.
2. Segundo Enter: confirma a resposta selecionada.
3. Terceiro Enter: executa a ação de **Próxima questão**.
4. Na última questão, o terceiro Enter conclui/entrega a sessão pelo mesmo fluxo já usado pelo botão final.

## Preservado
- Setas continuam apenas navegando entre alternativas.
- Espaço continua tachando/destachando a alternativa em foco.
- Mouse, clique no card e tesoura continuam funcionando.
- Cada nova questão reinicia `resposta_confirmada`, recomeçando o ciclo do Enter.

## Detalhe técnico
Após a confirmação, o botão de avanço recebe o foco visual. O filtro global de teclado consome o Enter pós-confirmação e chama `proxima()` diretamente, evitando disparo duplicado pelo próprio `QPushButton`. Repetições automáticas do Enter mantido pressionado são consumidas sem executar novas etapas.

## Versão
- Versão: **0.29.57**
- Build: `question-keyboard-navigation-enter-next-v2`
- Schema: 25 (sem alteração)
