# VighnaStudy 0.29.32 — composição harmônica do splash

## Objetivo

Refinar exclusivamente a composição visual da tela de carregamento criada na versão 0.29.31, preservando o progresso real, o shimmer contínuo e o processo independente do splash.

## Ajustes de composição

A tela foi reorganizada para funcionar como um único conjunto visual, em vez de três blocos separados.

- altura da janela reduzida de `346 px` para `318 px`, eliminando parte do vazio estrutural;
- conjunto completo centralizado verticalmente com respiro equivalente acima e abaixo;
- eixo principal do conteúdo deslocado para coincidir com o início do texto `VighnaStudy`;
- card de carregamento passa a começar no mesmo eixo horizontal do título;
- logo permanece à esquerda como âncora visual, sem empurrar o card para o eixo anterior;
- largura útil do card reduzida de forma natural pelo recuo de `68 px`;
- distância entre cabeçalho e card reduzida para `19 px`;
- distância entre card e assinatura ajustada para `25 px`;
- assinatura `motor de inteligência Vighna` centralizada no mesmo eixo do card;
- linhas longas do rodapé removidas;
- caixa do logo reduzida para `54 x 54 px`, com símbolo maior proporcionalmente;
- borda externa, borda do logo e borda do card suavizadas para diminuir o efeito de caixas sobre caixas;
- título ajustado para `23 px` para equilibrar melhor sua relação com o logo e o card.

## Barra de progresso

Nenhuma regressão funcional foi introduzida. Permanecem:

- percentual verdadeiro;
- avanço amortecido;
- shimmer contínuo;
- pulso discreto na frente do preenchimento;
- reticências animadas;
- execução do splash em processo independente.

## Fallback

A `JanelaInicializacao` local recebeu a mesma geometria e a mesma composição do splash externo. Assim, se o worker independente não puder ser criado, a aparência continua coerente.

## Versão

- `VIGHNA_VERSION = 0.29.32`
- `VIGHNA_BUILD = startup-splash-composicao-harmonica-v1`
- `VIGHNA_SCHEMA = 23`

## Dados

Não houve alteração de schema, banco de questões, estatísticas ou inteligência. A mudança é restrita à apresentação do splash e aos metadados de versão.

## Validações realizadas

- `python -m py_compile main.py startup_splash.py versao.py test_startup_splash_harmonia_0_29_32.py`: OK;
- `test_startup_splash_harmonia_0_29_32.py`: 8/8 OK;
- `test_startup_rapido.py`: 3/3 OK;
- `test_startup_integridade_rapida_0_29_22.py`: 3/3 OK;
- `test_build_pyinstaller.py`: 4/4 OK;
- total focado: 18/18 testes aprovados;
- `PRAGMA integrity_check`: `ok`;
- `PRAGMA foreign_key_check`: 0 violações;
- SHA-256 de `estudos.db`: `6e73df5942723106f9347b949a1b6cd41f655b58bada1d416b35028fd9a9d1fd`;
- hash do banco idêntico ao checkpoint 0.29.31.

## Limitação da validação

O ambiente de preparação não possui PySide6. A composição foi validada estruturalmente no código, mas a renderização final deve ser conferida no Windows ao executar o VighnaStudy.
