# VighnaStudy 0.29.23 — Ciclo persistente de questões

**Versão:** 0.29.23  
**Build:** `ciclo-questoes-persistente-v1`  
**Schema:** 23  
**Base:** checkpoint enviado em 26/09/2026 16:19:44 (0.29.22).

## Objetivo

Permitir que uma bateria de questões de um tópico seja tratada como uma rodada persistente, podendo ser interrompida e retomada em outro dia sem reapresentar as questões já respondidas naquela rodada.

O recurso é independente do filtro **Somente inéditas**:

- **Somente inéditas:** considera o histórico acadêmico global do perfil.
- **Pendentes do ciclo:** considera apenas o conjunto congelado da rodada atual e exclui o que já foi respondido nessa rodada.

## Funcionamento implementado

Na janela **Estudar tópico** foi adicionado o card **Ciclo de questões**.

Sem ciclo ativo, estão disponíveis:

- `Bateria avulsa`;
- `Iniciar novo ciclo com o conjunto filtrado`.

Com ciclo ativo, o Vighna oferece por padrão:

- `Continuar ciclo atual (N pendentes)`;
- `Bateria avulsa`.

Ao criar o ciclo, o Vighna congela os IDs das questões correspondentes aos filtros daquele momento. A quantidade escolhida limita somente a primeira bateria; as demais questões permanecem pendentes para sessões futuras.

Ao continuar o ciclo, os filtros de histórico, capítulo e dificuldade ficam bloqueados para evitar que o conjunto congelado seja alterado no meio da rodada.

## Estados do ciclo

Cada questão do ciclo possui estado próprio:

- `pendente`;
- `respondida`.

Uma resposta correta ou errada encerra o item no ciclo. O histórico acadêmico continua sendo registrado normalmente em `tentativas_questoes` e continua alimentando a inteligência do Vighna.

### Questões puladas

Foi preservada a regra já existente do Vighna:

- primeiro pulo: a questão volta ao final da bateria e continua pendente no ciclo;
- segundo pulo: o Vighna converte o pulo em erro efetivo; a questão passa a contar como respondida no ciclo e continua alimentando a inteligência como erro.

## Persistência

Foram acrescentadas duas tabelas no schema 23:

- `ciclos_questoes` — identifica cada rodada persistente por perfil e tópico;
- `ciclo_questoes_itens` — guarda o snapshot de IDs e o estado de cada questão.

Há no máximo um ciclo ativo por perfil+tópico.

Novas questões importadas após o início do ciclo não entram automaticamente na rodada em andamento. Elas ficam disponíveis para o próximo ciclo.

Se uma questão do ciclo ficar arquivada ou indisponível posteriormente, ela é indicada como indisponível e não volta indevidamente para a fila.

## Preservação da inteligência

O recurso adiciona uma camada de controle de cobertura. Não substitui nem reinicia:

- tentativas;
- acertos/erros;
- snapshots históricos;
- revisões;
- `controle_topico`;
- domínio e métricas;
- importância por concurso;
- banco de erros;
- sessões anteriores.

A migração é aditiva: o `estudos.db` do usuário não é substituído pelo pacote.

## Revisões

O mecanismo de revisão do Vighna já possuía cobertura integral persistente (`obter_estado_cobertura_revisao` / `selecionar_questoes_revisao_cobertura`), que prioriza apenas as questões ainda não cobertas na revisão em andamento. Esse mecanismo foi mantido.

O novo **Ciclo de questões** estende a mesma ideia às baterias comuns iniciadas em **Estudar tópico**, sem alterar a lógica das revisões já existente.

## Interface

Além do card de ciclo em **Estudar tópico**:

- o tópico passa a mostrar o progresso `Ciclo: X/Y` quando houver ciclo ativo;
- o resolvedor mostra no cabeçalho da sessão `Ciclo X/Y • N pendentes`;
- existe a ação **Encerrar ciclo**, que cancela apenas a rodada, preservando todas as respostas e o histórico já produzidos.

## Validação

Foram executados 22 testes direcionados, incluindo:

- criação e snapshot do ciclo;
- continuidade entre sessões;
- conclusão automática;
- uma única rodada ativa por perfil+tópico;
- encerramento manual sem exclusão dos itens;
- comportamento do primeiro e segundo pulo;
- regressão da cobertura integral de revisão;
- workspace e navegação de questões por tópico.

Resultado: **22/22 testes aprovados**.

Também foram compilados os 99 arquivos Python do projeto presentes na raiz do checkpoint: **0 erros de sintaxe**.

A migração foi testada em cópia do `estudos.db` do checkpoint:

- `quick_check = ok`;
- `foreign_key_check = 0`;
- criação das duas tabelas confirmada;
- ciclo de teste criado para o Título V – Das Penas;
- questão respondida removida da lista de pendentes;
- encerramento do ciclo preservou o histórico.

## Observação sobre o banco

Este pacote não contém `estudos.db`, `estudos.db-wal` ou `estudos.db-shm`. Na primeira abertura, `criar_banco()` cria apenas as estruturas novas do schema 23 no banco local existente.
