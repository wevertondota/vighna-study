# VighnaStudy 0.29.43 — Otimização de startup e warm cache

## Objetivo

Reduzir o tempo de abertura sem introduzir lazy loading perceptível no primeiro acesso a Estatísticas, Relatórios, Central de Questões ou demais telas. O pré-carregamento completo antes do Dashboard foi preservado.

Base: checkpoint 0.29.42 (`microtemas-refino-crimes-pessoa-v1`).
Nova versão: **0.29.43** — build **`startup-warm-cache-v1`** — schema **25**.

## Diagnóstico usado

O benchmark real no Windows indicou aproximadamente 99 s na preparação de Estatísticas, com os maiores custos em Histórico, Tendências, Conquistas, Mapa de domínio, Progresso, Disciplinas, Algoritmo e Pontos fracos. O principal padrão encontrado foi a repetição dos mesmos cálculos caros durante uma única abertura e a expiração do cache de memória enquanto o próprio startup ainda estava em andamento.

## Alterações implementadas

### 1. Fase estável de cache durante todo o startup

`CacheAnalitico` agora possui uma fase estável. Enquanto o pré-carregamento completo está em execução, entradas válidas não expiram por TTL. Invalidações explícitas continuam funcionando.

Isso impede que um snapshot calculado no Dashboard expire antes de Conquistas, Mapa de domínio ou Progresso utilizá-lo.

### 2. Reuso das mesmas chaves no Dashboard e nas Estatísticas

Métricas globais e fila adaptativa passaram a usar a mesma chave de cache em todos os consumidores relevantes. O pré-carregamento das abas de Estatísticas também deixou de forçar uma invalidação desnecessária na primeira aba.

### 3. Cálculo hierárquico em uma única leitura

`StatisticsService` ganhou:

- `get_hierarchy_metrics()`;
- `get_hierarchy_metrics_periods()`.

Tópicos, disciplinas e global agora podem ser calculados a partir da mesma leitura de tentativas, catálogo, tópicos ativos e revisões. A análise temporal reutiliza uma leitura all-time para os períodos atual, anterior e oficial, filtrando os eventos em memória.

Foi conferida equivalência exata entre a nova hierarquia e as APIs anteriores de tópico, disciplina e global no banco real.

### 4. Progresso como snapshot compartilhado

O snapshot de Progresso passou a reutilizar `get_hierarchy_metrics()` e passou a carregar também, em cada disciplina, desempenho e número de tentativas. Isso permitiu reutilizar o mesmo snapshot na tabela de Disciplinas.

A saída antiga e a nova da tela de Disciplinas foram comparadas no banco real e permaneceram idênticas.

### 5. Pontos fracos sem recalcular todos os tópicos

`listar_ranking_topicos()` agora deriva seu ranking do snapshot oficial de Progresso já calculado. Antes, a função executava novamente a bateria de métricas por tópico.

A saída antiga e a nova foram comparadas no banco real e permaneceram idênticas.

### 6. Warm cache persistente entre sessões

Foi criado `cache_persistente.py` e quatro tabelas derivadas/descartáveis:

- `cache_persistente`;
- `cache_revisoes`;
- `cache_meta`;
- `cache_controle`.

Resultados caros são persistidos assim que são calculados. Portanto, o Vighna **não precisa fazer uma recalculação pesada ao fechar**. O fechamento continua rápido e a próxima abertura pode reutilizar os snapshots já produzidos.

O cache preserva tipos usados pelos snapshots, incluindo chaves inteiras, tuplas, conjuntos, datas e datetimes.

### 7. Invalidação por revisões da base

Triggers SQLite incrementam revisões por domínio quando dados-fonte mudam:

- `academico`;
- `catalogo`;
- `configuracao`;
- `foco`.

Cada cache registra as revisões com as quais foi calculado. Se qualquer dependência mudar, a entrada deixa de ser considerada válida automaticamente.

Isso substitui a dependência exclusiva de TTL por validade baseada no estado real do banco.

### 8. Migrações do startup não invalidam o warm cache

Durante `criar_banco()`, os contadores de revisão são suspensos. Assim, `CREATE IF NOT EXISTS`, backfills/migrações idempotentes e manutenção estrutural não fazem um cache válido parecer desatualizado a cada abertura.

Foi testado o cenário completo:

1. calcular e persistir cache;
2. encerrar a memória do processo;
3. executar `criar_banco()` novamente;
4. abrir nova sessão;
5. recuperar o mesmo cache sem chamar o carregador novamente.

As revisões permaneceram idênticas e `cache_controle.suspenso` voltou corretamente para 0.

### 9. Snapshots persistidos

Foram colocados sob warm cache revisionado, entre outros:

- métricas globais;
- progresso do edital;
- análise temporal;
- regularidade;
- índices de domínio;
- prioridades adaptativas;
- duplicidades da Central;
- integridade histórica;
- Caderno de Erros;
- relatório estratégico.

O checkpoint entregue já contém uma fotografia quente dos principais cálculos do perfil ativo em 01/10/2026. Se o banco não mudar, a primeira abertura deste checkpoint pode reutilizá-la. Qualquer mudança real invalida automaticamente o que depender dela.

### 10. Central de Questões

Também foram mantidas as otimizações diagnosticadas anteriormente:

- consulta de integridade histórica reescrita sem `EXISTS` correlacionado;
- Caderno de Erros refeito em lote, eliminando padrão N+1;
- detecção de duplicidades protegida por cache persistente de catálogo.

A saída do Caderno, integridade histórica e duplicidades foi comparada com a implementação anterior no banco real e permaneceu equivalente.

## Medições locais de engenharia

Os tempos abaixo foram medidos no ambiente Linux de análise e **não devem ser comparados diretamente aos segundos do Windows**. Servem para confirmar o comportamento frio/quente do mecanismo.

| Operação | Frio | Warm persistente |
|---|---:|---:|
| Métricas globais | ~40–53 ms | ~2 ms |
| Progresso | ~73–78 ms | ~3–4 ms |
| Temporal 30 dias | ~214–246 ms | ~5 ms |
| Domínio | ~21–23 ms | ~4 ms |
| Prioridades | ~139–156 ms | ~7–8 ms |
| Duplicidades | ~344–362 ms | ~1,5–1,6 ms |
| Integridade histórica | ~8–9 ms | ~1–1,5 ms |
| Caderno de Erros | ~18 ms | ~3–4 ms |
| Regularidade | ~9 ms | ~2 ms |
| Relatório estratégico | ~18–25 ms* | ~1,6 ms |

\* No teste frio, dependências como domínio/prioridades já haviam sido aquecidas pela sequência que simula o startup.

Após persistir os caches, foi executado novamente `criar_banco()`. Os payloads e revisões permaneceram byte-a-byte iguais; em seguida, métricas globais, progresso, temporal e duplicidades foram recuperados em aproximadamente 1,6–5,1 ms no ambiente de análise.

## Preservação do banco acadêmico

O banco final foi comparado tabela por tabela com o checkpoint 0.29.42 antes das alterações.

- nenhuma tabela acadêmica preexistente teve conteúdo alterado;
- as únicas tabelas novas são as quatro tabelas de cache;
- `PRAGMA integrity_check`: `ok`;
- `PRAGMA foreign_key_check`: 0 violações;
- ciclo 5 de Crimes contra a Pessoa: 131 respondidas e 222 pendentes, preservado.

## Testes

Suíte principal de núcleo após as alterações:

- **163 testes aprovados**;
- **10 subtests aprovados**.

Teste específico do piloto de microtemas/Crimes contra a Pessoa:

- **6 testes aprovados**.

Também foram validadas manualmente:

- equivalência das métricas hierárquicas com as APIs anteriores;
- equivalência da tabela de Disciplinas;
- equivalência do ranking de Pontos fracos;
- persistência do cache após nova execução de `criar_banco()`;
- invalidação do cache após mutação real de tabela-fonte;
- preservação de tipos no round-trip JSON.

O ambiente de análise não possui PySide6, portanto os testes que exigem execução real da interface Qt não podem ser executados aqui. Os testes de startup baseados em código/núcleo foram executados quando não dependiam do runtime Qt. Testes históricos que fixam literalmente uma versão antiga do Vighna falham apenas na asserção de versão após o bump para 0.29.43 e não indicam regressão funcional.

## Próxima medição recomendada

Executar novamente no Windows o mesmo benchmark detalhado usado na versão 0.29.42. Ele permitirá comparar diretamente 0.29.42 × 0.29.43 no mesmo computador.

A expectativa arquitetural é que as maiores reduções apareçam em:

- Progresso;
- Conquistas;
- Mapa de domínio;
- Disciplinas;
- Pontos fracos;
- Histórico/Tendências;
- Algoritmo;
- Relatório estratégico;
- Central em aberturas subsequentes.

Não foi introduzido lazy loading como estratégia de desempenho: o Vighna continua preparando as telas antes de liberar o Dashboard.
