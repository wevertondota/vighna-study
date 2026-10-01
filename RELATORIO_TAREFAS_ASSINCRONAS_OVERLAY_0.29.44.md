# VighnaStudy 0.29.44 — tarefas assíncronas e indicador visual

Build: `tarefas-assincronas-overlay-v1`

## Objetivo

Eliminar as pequenas travadas percebidas após alterações acadêmicas, principalmente ao concluir uma bateria/responder questões, sem adotar lazy loading que transfira o atraso para o primeiro clique em Estatísticas, Relatórios ou outras telas.

A versão mantém o princípio do Vighna: dados importantes continuam sendo preparados antecipadamente. A diferença é que recomputações posteriores passam a ocorrer fora da thread da interface e recebem feedback visual quando duram o suficiente para serem percebidas.

## Infraestrutura central

Foi criado `tarefas_pesadas.py` com dois componentes:

- `CoordenadorTarefas`: fila serial baseada em `QThreadPool`/`QRunnable`;
- `IndicadorTarefa`: janela visual reutilizável para operações demoradas.

A fila usa uma única thread de trabalho propositalmente. Isso evita que duas reconstruções estatísticas concorrentes disputem o mesmo SQLite e simplifica a coerência do warm cache.

Cada worker usa apenas rotinas que abrem suas próprias conexões ao SQLite, evitando reutilizar uma conexão da thread da interface.

## Comportamento visual

### Tarefas rápidas

O indicador não aparece imediatamente. Há atraso de aproximadamente 280 ms antes de exibi-lo, evitando piscadas em operações que terminam quase instantaneamente.

### Recalculo após alteração acadêmica

Ao terminar uma sessão com respostas gravadas:

1. a resposta/sessão já está persistida;
2. os caches afetados são invalidados;
3. a alteração é classificada como `tentativas`, sem marcar o catálogo da Central como alterado;
4. um debounce de aproximadamente 450 ms aglutina mudanças próximas;
5. o recálculo ocorre em worker;
6. a interface continua processando eventos;
7. ao terminar, Estatísticas, Relatórios e estruturas já carregadas são reapreparadas com os snapshots novos.

Se outra alteração ocorrer enquanto o worker ainda calcula, o resultado antigo não é aplicado à UI; uma nova rodada é agendada. O cache persistente também usa revisões da base para impedir a persistência de snapshots obsoletos.

### Acesso a tela dependente enquanto recalcula

Se o usuário tentar abrir Estatísticas/Relatórios/Dashboard que precisam dos dados ainda em processamento, o indicador existente é promovido para espera visual bloqueante. Assim não há cálculo pesado escondido nem uma janela aparentemente congelada.

### Estatísticas sem troca visual de abas

Depois do recálculo, todas as abas de Estatísticas continuam sendo preparadas antecipadamente, inclusive quando a tela está aberta. Durante esse percurso interno, updates visuais e sinais do QTabWidget são temporariamente suspensos; a aba que o usuário estava vendo é restaurada no fim. Isso evita flicker e mantém as demais abas prontas para o próximo clique.

## Fechamento

`closeEvent()` agora possui preparação assíncrona:

- exibe imediatamente `Preparando a próxima sessão`;
- consolida warm cache persistente;
- gera o backup de fechamento;
- só então autoriza a janela principal a encerrar.

Se já houver um recálculo em andamento quando o usuário pede para fechar, o Vighna espera visualmente a rodada atual terminar e depois executa a consolidação final. Se havia apenas um recálculo agendado e ainda não iniciado, ele é cancelado porque a tarefa de fechamento já fará o aquecimento completo.

Se o fechamento for solicitado exatamente quando o worker termina, o Vighna pula a repintura/preparação de telas que seriam descartadas e segue diretamente para cache + backup.

Falha de warm cache não impede o fechamento. Falha de backup preserva a política histórica do projeto e também não deixa o aplicativo preso.

## Backup manual

O backup manual também foi movido para o `CoordenadorTarefas`. A cópia consistente do banco ocorre fora da thread da interface e recebe indicador visual.

## Aquecimento de dados

Foi criado `aquecimento_dados.py`, módulo sem dependência de Qt, para recalcular/persistir em worker:

- progresso do edital;
- métricas globais;
- estatísticas por disciplina;
- regularidade;
- análise temporal e histórico;
- tendências do período aberto;
- fila adaptativa;
- gamificação/conquistas;
- caderno de erros;
- relatório estratégico do período padrão.

O módulo reutiliza os caches persistentes/revisionados implementados na 0.29.43.

## Coalescência

Mudanças próximas não disparam múltiplas recomputações simultâneas. O Vighna:

- agrupa alterações por aproximadamente 450 ms;
- mantém no máximo um worker estatístico de cada vez;
- registra que uma nova rodada é necessária se outra alteração ocorrer durante o cálculo.

Isso evita o padrão `resposta 1 → recalcula tudo / resposta 2 → recalcula tudo` quando as mudanças chegam muito próximas.

## Preservação do pré-carregamento

Não foi introduzido lazy loading das Estatísticas ou Relatórios. Após uma alteração, o Vighna continua reapreparando as telas já construídas para que a navegação posterior permaneça imediata.

A Central de Questões também deixa de ser marcada como suja por uma simples resposta. O catálogo só é invalidado por mudanças reais em questões/estrutura.

## Checkpoint

O núcleo obrigatório do checkpoint passou a incluir também:

- `tarefas_pesadas.py`;
- `aquecimento_dados.py`.

Assim um checkpoint incompleto sem a nova infraestrutura não pode ser tratado como restauração completa da versão atual.

## Validação

Foram executados os testes selecionados da nova infraestrutura, núcleo estatístico, warm cache, banco único, microtemas e responsividade:

- **128 testes aprovados**;
- `python -m compileall -q .`: aprovado;
- `PRAGMA integrity_check`: `ok`;
- `PRAGMA foreign_key_check`: 0 violações;
- conteúdo de todas as tabelas não relacionadas a cache comparado com a base 0.29.43: **nenhuma diferença**;
- contagens das 50 tabelas preservadas.

Em teste anterior do aquecimento puro sobre uma cópia do banco após uma resposta simulada, a primeira consolidação ficou em aproximadamente **0,64 s** no ambiente de análise e a repetição com caches quentes em aproximadamente **0,03 s**. Esses tempos não representam o Qt/Windows do usuário; servem apenas para validar o comportamento do núcleo de dados.

## Limitação do ambiente de validação

O ambiente de análise não possui PySide6 instalado. Portanto, foi possível validar sintaxe, estrutura, banco, comportamento do núcleo sem Qt e testes estáticos de integração, mas não executar aqui a animação/janela real do `QThreadPool`/`QDialog`.

A validação visual definitiva deve ser feita no Windows do usuário, observando principalmente:

1. concluir uma bateria de uma ou mais questões;
2. continuar navegando enquanto `Atualizando seu progresso` estiver ativo;
3. abrir Estatísticas durante um recálculo;
4. fechar o Vighna durante um recálculo;
5. executar backup manual;
6. confirmar que não há flicker de abas nas Estatísticas.
