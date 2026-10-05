# VighnaStudy 0.29.56 — navegação das alternativas pelo teclado

## Alteração

A bateria de questões passa a aceitar navegação completa pelas alternativas sem substituir o comportamento do mouse.

- **↑ / ←**: move o foco para a alternativa anterior.
- **↓ / →**: move o foco para a alternativa seguinte.
- O percurso é circular: após a última alternativa, a próxima volta à primeira e vice-versa.
- **Espaço**: tacha ou restaura a alternativa atualmente focada.
- **Enter (1ª vez)**: seleciona a alternativa focada, com o mesmo efeito acadêmico do clique esquerdo.
- **Enter (2ª vez)**: se a alternativa focada já estiver selecionada, confirma a resposta.

## Proteções de interação

O foco de teclado foi separado da seleção efetiva. Portanto, usar as setas não marca uma resposta inadvertidamente. O Espaço só é capturado como comando de tachamento quando o foco real está dentro de uma alternativa; controles como **Marcar como dúvida** continuam recebendo Espaço normalmente.

O filtro de teclado é instalado apenas durante a vida da janela do resolvedor e removido quando ela é encerrada. O clique no card, o radio button e a tesoura continuam funcionando como antes.

## Visual

A alternativa percorrida pelas setas recebe uma borda de foco própria nos temas Claro, Escuro e Futurista. Esse indicador é independente do estado de seleção e do tachamento.

## Versão

- Versão: **0.29.56**
- Build: `question-keyboard-navigation-v1`
- Schema: **25** (sem alteração de banco)
