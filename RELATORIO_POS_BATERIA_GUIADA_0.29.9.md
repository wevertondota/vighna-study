# VighnaStudy 0.29.9 — Pós-bateria guiado pelo algoritmo

## Objetivo
Reorganizar a janela exibida ao terminar uma bateria iniciada pelo card **Recomendado pelo algoritmo**, mantendo o usuário dentro do fluxo guiado de estudo e apresentando um resumo mais útil da sessão.

## Alterações
- A janela guiada passa a usar o título **Sessão concluída** e mostra disciplina e tópico.
- O resumo principal exibe: questões processadas, acertos, erros, aproveitamento, tempo total e tempo médio por questão.
- Puladas, dúvidas e inéditas respondidas ficam em uma linha auxiliar compacta.
- Foi criado o bloco **Cobertura e revisão**, com:
  - questões cobertas na rodada;
  - percentual de cobertura;
  - questões restantes;
  - estado da revisão;
  - próxima revisão ou indicação de que ainda não foi reagendada.
- Não existe bloco **Leitura do Vighna** nessa janela.
- O botão principal agora é **CONTINUAR PELO ALGORITMO**.
- Permanecem as ações de reforço **Revisar toda a bateria** e **Rever erradas**.
- **Voltar ao Dashboard** encerra o fluxo guiado sem abrir outra área.
- **Banco de questões** fica como ação secundária explícita e só abre a Central quando escolhido.
- Ao escolher **Continuar pelo algoritmo**, a fila é recalculada com os resultados já consolidados e uma tela curta de **Próxima recomendação** é exibida antes da próxima bateria.
- O reforço de questões erradas continua sem impacto acadêmico duplicado; ao terminar, seu botão de saída agora retorna ao resumo da bateria.

## Revisão por cobertura
A lógica da versão 0.29.8 foi preservada. Assim, se uma revisão tiver 80 questões e a primeira bateria cobrir 40, a janela informa **40/80**, **50%**, **40 restantes** e **Revisão em andamento**. Ao continuar pelo algoritmo, o Motor V5 recalcula a prioridade já com essa cobertura consolidada.

## Compatibilidade
- Nenhuma alteração de schema.
- Nenhum `estudos.db` é incluído nesta atualização.
- `banco.py` e `ciclo_estudo.py` da 0.29.8 seguem no pacote para preservar integralmente a lógica de cobertura.
- Versão: **0.29.9**
- Build: `guided-post-battery-flow-v1`

## Validação
- `python -m py_compile main.py banco.py ciclo_estudo.py versao.py`: OK.
- 10 testes de pós-bateria, startup e configuração do build: OK (incluem os 3 testes específicos do novo fluxo).
- Os 6 testes de cobertura e ciclo exercitaram a lógica, mas falharam no `tearDown` no Windows: conexões SQLite ainda abertas impedem a exclusão dos bancos temporários (`PermissionError: WinError 32`).
