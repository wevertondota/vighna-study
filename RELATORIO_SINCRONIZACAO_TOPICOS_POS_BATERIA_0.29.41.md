# VighnaStudy 0.29.41 — Sincronização da lista de tópicos após bateria

## Sintoma reproduzido
Após concluir uma bateria pelo tópico `Estatuto do Desarmamento - LEI Nº 10.826`, a janela detalhada do tópico já mostrava a revisão consolidada de 27/09/2026 (257 questões, 194 acertos, 75,5%) e próxima revisão em 25/10/2026, mas a lista da disciplina continuava exibindo os dados anteriores (`2` revisões, última `—`, próxima `26/09/2026`, `89,0%`).

## Causa
A partir do pré-carregamento do Dashboard e das disciplinas, a tela de disciplina passou a reaproveitar `_topicos_precarregados`. A bateria gravava corretamente a sessão e a revisão no SQLite, porém alguns caminhos de resolução retornavam para `carregar_topicos()` sem antes chamar `notificar_dados_alterados("questoes")`. Assim, `carregar_topicos()` reutilizava o snapshot anterior da disciplina em vez de consultar os dados recém-gravados.

O banco do checkpoint confirma que a persistência estava correta; o problema era exclusivamente de sincronização visual/cache.

## Correções

### 1. Invalidação automática ao encerrar uma bateria
`JanelaResolverQuestoes` agora localiza a janela principal e invalida o escopo `questoes` ao terminar uma sessão que realmente gravou respostas. A invalidação acontece antes de o controle voltar à tela chamadora.

Isso cobre baterias abertas por:
- botão `Estudar` da disciplina;
- janela detalhada do tópico;
- revisão inteligente;
- calendário;
- algoritmo;
- demais fluxos que reutilizam o resolvedor unificado.

O mesmo tratamento foi aplicado ao encerramento pela janela (`X`) quando respostas já haviam sido preservadas.

### 2. Revisões manuais
Criação, edição, exclusão e alteração da próxima revisão na janela do tópico agora também invalidam o cache de revisões antes da tela anterior voltar a carregar os dados.

### 3. Ordem correta de invalidação
Em operações da disciplina/tópico que alteram dados, a invalidação passou a ocorrer antes de `carregar_topicos()`, evitando a reconstrução da tabela com um cache que ainda estava válido.

### 4. Nome vazio em tópicos com capítulos
Foi corrigido um segundo problema observado no mesmo checkpoint: tópicos que possuem capítulos usam uma célula visual própria e deixam o texto do `QTableWidgetItem` vazio. Ao abrir o tópico por duplo clique, a janela recebia `item.text()` e aparecia como `Tópico —`, podendo também gerar sessões com `topico_nome = "Tópico"`.

Agora a abertura usa o nome original armazenado em `Qt.UserRole + 4`.

## Estado esperado do tópico do checkpoint
Os dados persistidos no banco para `Estatuto do Desarmamento - LEI Nº 10.826` são:
- revisões totais: 3 (2 legadas + 1 interna);
- última revisão: 27/09/2026;
- próxima revisão: 25/10/2026;
- percentual da revisão mais recente: 75,5%;
- revisão interna: 257 questões / 194 acertos.

Com a correção, a lista da disciplina passa a refletir esses dados ao retornar da bateria.

## Validação
- `python -m py_compile main.py versao.py`
- `python -m unittest -v test_sincronizacao_topicos_pos_bateria_0_29_41.py`
- testes de regressão do ciclo persistente e dos caminhos funcionais da navegação rápida (o teste histórico de versão 0.29.40, por definição, espera a versão anterior).

## Versão
- `0.29.41`
- build: `sincronizacao-topicos-pos-bateria-v1`
