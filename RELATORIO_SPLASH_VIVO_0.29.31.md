# VighnaStudy 0.29.31 — tela de carregamento viva

## Objetivo

Refinar a tela de inicialização e impedir que ela pareça travada quando alguma etapa pesada do pré-carregamento ocupa a thread principal do VighnaStudy.

## Alterações visuais

A tela de carregamento foi reorganizada para concentrar a informação em um bloco único e mais compacto:

- identidade VighnaStudy com logo real;
- subtítulo `Preparando seu ambiente de estudo`;
- etapa corrente e percentual na mesma linha;
- descrição da atividade logo abaixo;
- barra de progresso posicionada junto ao status;
- percentual removido do interior da barra;
- rodapé discreto `motor de inteligência Vighna`;
- bordas e contrastes suavizados.

## Barra de progresso viva

A barra mantém o percentual informado pelo pré-carregamento como referência real. O valor não avança artificialmente quando o Vighna ainda está processando uma etapa.

Para transmitir atividade contínua, a barra passou a usar:

- transição amortecida até o novo percentual;
- brilho/shimmer que atravessa continuamente a parte preenchida;
- pequeno pulso visual na frente do preenchimento;
- texto da etapa com reticências animadas.

Assim, se o progresso permanecer em 12% durante uma operação pesada, o valor continua em 12%, mas a interface deixa claro que o Vighna continua trabalhando.

## Processo independente do splash

A principal mudança estrutural é que a tela de carregamento agora roda em um processo auxiliar independente.

Antes, tanto a animação quanto o pré-carregamento usavam a thread gráfica principal. Quando uma consulta, cálculo ou montagem de widgets demorava, o event loop ficava temporariamente ocupado e a animação congelava junto.

Agora:

1. o processo auxiliar do splash é iniciado antes das importações pesadas do aplicativo;
2. o processo principal grava apenas o estado atual — texto, detalhe e percentual — em um arquivo temporário;
3. o splash lê esse estado e mantém sua própria animação a aproximadamente 30 FPS;
4. operações síncronas pesadas no processo principal não interrompem mais o shimmer nem as reticências;
5. ao abrir a janela principal, o processo do splash é encerrado e o arquivo temporário é removido.

O processo auxiliar também verifica se o processo principal ainda existe para evitar uma janela órfã em caso de encerramento inesperado.

## Fallback

Foi mantida uma `JanelaInicializacao` local. Se o processo auxiliar não puder ser criado, o Vighna continua abrindo com uma versão visualmente atualizada da tela de carregamento, em vez de impedir a inicialização.

## Compatibilidade com o executável

O worker usa o próprio `VighnaStudy.exe` com um argumento interno quando o aplicativo está empacotado. Em execução por Python, ele usa o mesmo `main.py`.

Não foi adicionada dependência externa nem alteração de schema. O `VighnaStudy.spec` não precisa de módulo Qt adicional.

## Versão

- `VIGHNA_VERSION = 0.29.31`
- `VIGHNA_BUILD = startup-splash-vivo-processo-independente-v1`
- `VIGHNA_SCHEMA = 23`

## Validações realizadas

- `python -m py_compile main.py startup_splash.py versao.py`: OK
- `test_startup_splash_vivo_0_29_31.py`: 9/9 OK
- `test_startup_rapido.py`: 3/3 OK
- `test_startup_integridade_rapida_0_29_22.py`: 3/3 OK
- `test_build_pyinstaller.py`: 4/4 OK
- `PRAGMA integrity_check`: `ok`
- `PRAGMA foreign_key_check`: 0 violações
- SHA-256 do `estudos.db` original e atualizado: idêntico

## Limitação desta validação

O ambiente usado para preparar o checkpoint não possui PySide6. Portanto, a execução visual final precisa ser confirmada no Windows ao executar `main.py` ou gerar o `VighnaStudy.exe`. A sintaxe, integração, fluxo de processo, build e integridade do banco foram validados sem alterar os dados acadêmicos.
