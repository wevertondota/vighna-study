# Recuperação segura do banco — atualização após as 14 questões novas

## Base utilizada

Esta recuperação parte diretamente do banco enviado pelo usuário em 20/09/2026 (`estudos(3).db`).
Antes da recuperação ele contém:

- 2.522 registros físicos de questões;
- 2.509 questões ativas;
- 13 questões na lixeira;
- 270 questões ativas de Direito Penal;
- 18 questões ativas em TÍTULO VI – Dos Crimes Contra a Dignidade Sexual.

As 14 questões recém-adicionadas são os IDs 2509 a 2522 e foram preservadas integralmente.

## O que foi acrescentado

Foram acrescentadas somente 42 questões que não existiam no banco enviado:

- 7 de Crimes Contra a Liberdade Sexual;
- 18 de Crimes Sexuais Contra Vulnerável;
- 5 de Exposição da Intimidade Sexual;
- 6 históricas de Ultraje Público ao Pudor;
- 6 históricas do Título XII — crimes contra as instituições democráticas.

Nenhum registro preexistente foi modificado.

## Resultado

- 2.564 registros físicos;
- 2.551 questões ativas;
- 13 questões na lixeira;
- 312 questões ativas de Direito Penal;
- 54 questões ativas em Crimes Contra a Dignidade Sexual;
- 29 questões ativas em Crimes Contra o Estado Democrático de Direito.

Validação SQLite:

- `PRAGMA integrity_check`: `ok`;
- `PRAGMA foreign_key_check`: 0 problemas.

## Como aplicar

1. Feche completamente o VighnaStudy.
2. Copie o conteúdo do pacote completo para `C:\SistemaEstudos`.
3. Execute `aplicar_recuperacao_banco.bat`.
4. O banco existente será preservado em `backups` antes da troca.
5. Teste com `python main.py`.
6. Confira a Central de Questões e Direito Penal.
7. Depois execute `atualizar_exe.bat`.

## Contagem esperada na Central de Questões

Depois da recuperação, a Central deve mostrar **2.551 questões ativas**.
