# Ambiente de execução

Este projeto é desenvolvido no Windows usando Git Bash.

Ao executar comandos de terminal:

- Prefira ferramentas e sintaxe Bash.
- Não use cmdlets do PowerShell quando houver equivalente em Bash.
- Execute comandos Bash através de:

  C:\Program Files\Git\bin\bash.exe -lc "<comando>"

- Para localizar executáveis, use `which` ou `command -v`.
- Para procurar texto, use `grep` ou `rg`.
- Para localizar arquivos, use `find`.
- Para listar arquivos, use `ls`.
- Para manipulação textual, prefira `sed`, `awk`, `cut`, `sort`, `head` e `tail`.
- Para Git, use diretamente os comandos `git`.
- Considere caminhos Bash no formato `/c/...` quando estiver dentro do Bash.

Antes de assumir que uma ferramenta não está instalada, verifique dentro do Git Bash com:

  command -v <ferramenta>