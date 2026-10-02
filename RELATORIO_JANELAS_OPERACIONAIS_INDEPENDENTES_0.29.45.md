# VighnaStudy 0.29.45 — bateria e Modo Foco acessíveis durante a navegação

Build: `janelas-operacionais-independentes-v1`

## Problema tratado

A bateria de questões era aberta como `QDialog` pertencente à janela que a iniciou. No Windows, essa relação de propriedade pode transformar a bateria em uma janela operacional dependente: ela não recebe um comportamento confiável de item independente na barra de tarefas e a navegação para o Dashboard fica pouco natural. O efeito fica mais perceptível quando o Modo Foco também está aberto.

## Alterações

### Bateria de questões como janela top-level

`JanelaResolverQuestoes` agora é criada sem `parent` Qt e recebe flags explícitas de janela normal do Windows (`Qt.Window`, menu de sistema, minimizar, maximizar e fechar). O objeto de origem continua guardado apenas como controlador lógico, sem vínculo de propriedade visual.

Consequências:

- a bateria pode permanecer aberta enquanto o usuário usa o Dashboard e outras áreas do Vighna;
- minimizar a bateria não bloqueia a janela principal;
- restauração deixa de depender da hierarquia de `QDialog` do chamador;
- o estado atual da questão, alternativas marcadas e progresso permanecem preservados.

### Botão Dashboard dentro da bateria

Foi adicionado `Dashboard` ao cabeçalho da sessão. Ele minimiza a bateria e traz a janela principal para frente sem encerrar a sessão.

Nas baterias comuns, minimizar pausa o cronômetro da questão atual e restaurar retoma a contagem. O período em que a bateria ficou minimizada não entra no tempo registrado da questão. Em simulados, o relógio continua correndo, preservando o comportamento de prova cronometrada.

### Restauração confiável

A janela principal mantém uma referência funcional da bateria top-level em andamento. Foram adicionados:

- botão contextual `Retomar bateria` no topo do Dashboard, visível apenas quando existe uma bateria ativa;
- atalho `Ctrl+Shift+Q` para restaurar a bateria;
- restauração com `showNormal()`, `raise_()` e `activateWindow()`.

O Modo Foco já utilizava a mesma arquitetura top-level independente e mantém `Ctrl+Shift+F` para restauração. Com o Dashboard novamente acessível durante a bateria, o usuário passa a ter um ponto seguro para restaurar tanto a bateria quanto o Foco mesmo quando o Windows agrupa/minimiza as janelas do mesmo aplicativo.

### Fechamento do Vighna

Como a bateria deixou de ser filha Qt da janela principal, `SistemaEstudos.closeEvent()` agora localiza e fecha explicitamente baterias top-level antes de encerrar o aplicativo. A confirmação já existente continua sendo respeitada: se o usuário cancelar o encerramento da bateria, o fechamento do Vighna também é cancelado.

### Fluxo de reforço pós-bateria

O reforço de questões erradas também passou a usar `exec_nao_modal()`, eliminando um caminho residual que ainda poderia tornar uma nova bateria modal.

## Validação

- `python -m compileall -q .`: aprovado;
- `test_janelas_operacionais_0_29_45.py`: **8 testes aprovados**;
- `PRAGMA integrity_check`: `ok`;
- `PRAGMA foreign_key_check`: 0 violações;
- SHA-256 do `estudos.db` permanece idêntico ao checkpoint recebido, portanto a implementação não alterou os dados.

## Validação visual pendente

O ambiente possui PySide6 6.11.2 e permitiu validar sintaxe, arquitetura e testes automatizados. Ainda assim, o comportamento visual da barra de tarefas deve ser confirmado manualmente no Windows após atualizar o executável.

### Roteiro recomendado no Windows

1. iniciar uma bateria normal;
2. clicar em `Dashboard` e confirmar que a bateria minimiza sem encerrar;
3. abrir o setor de jogos e navegar normalmente;
4. usar `Retomar bateria` ou `Ctrl+Shift+Q` e confirmar que a mesma questão volta intacta;
5. repetir com o Modo Foco ativo e usar `Ctrl+Shift+F` para restaurá-lo;
6. minimizar bateria e Modo Foco e confirmar que ambos podem ser recuperados pelo Vighna;
7. fechar o Vighna com uma bateria ainda aberta e confirmar que a sessão é tratada antes do encerramento do aplicativo.
