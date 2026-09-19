# RELATÓRIO — PASSO 8: TENDÊNCIAS E COMPARAÇÕES TEMPORAIS V2

Data de conclusão: 18/09/2026
Versão: `0.24.0`
Build: `tendencias-temporais-v2`
Schema: `18`

## 1. Estado inicial

O Passo 8 partiu do estado validado do Passo 7, com Núcleo Estatístico oficial, Progresso do Edital V2, Fila Inteligente V3 ativa e fila candidata restrita ao modo sombra.

Durante a execução interrompida pelo limite do Codex, já haviam sido criados `analise_temporal.py`, `test_analise_temporal.py`, a tabela futura de snapshots de progresso e a migração principal das abas Histórico/Tendências. A retomada preservou esse trabalho, reexecutou os testes e concluiu as validações restantes.

O erro intermediário `KeyError: 'segundos'` foi corrigido no adaptador de Histórico, normalizando a estrutura de foco retornada pela camada temporal (`seconds/sessions/active_days` para as chaves de compatibilidade `segundos/sessoes/dias_ativos`). O teste que havia falhado passou após a correção.

## 2. Diferença documental de cobertura

A diferença de `52,12%` para `50,83%` já havia sido explicada pelo usuário: depois do relatório anterior foram incluídas 6 novas questões, alterando o universo de 236 para 242 enquanto 123 permaneciam respondidas.

Não houve correção de fórmula nem restauração do denominador antigo.

No checkpoint atual desta conclusão, o catálogo do concurso ativo contém **259 questões ativas** e **123 questões únicas respondidas**, portanto a cobertura de questões atual calculada pelo Núcleo Estatístico é aproximadamente **47,49%**. O valor é derivado do banco atual e não é fixado no código.

## 3. Auditoria da aba Histórico

A aba Histórico foi reposicionada para responder à pergunta: **“O que aconteceu no período?”**

Ela passou a priorizar dados cronológicos e descritivos:

- taxa de acerto no período;
- tentativas;
- questões únicas;
- sessões de questões;
- foco efetivo global;
- dias com foco global;
- sessões de foco global;
- revisões qualificadas;
- série cronológica diária.

Componentes antigos de inferência, como “maior evolução”, “maior queda”, evolução por disciplina e domínio observado legado, deixaram de ser parte visível do Histórico. Campos de compatibilidade continuam existindo no adaptador somente para evitar quebra de widgets/código legado ainda não removido.

## 4. Auditoria da aba Tendências

A aba Tendências foi reposicionada para responder à pergunta: **“O desempenho está mudando?”**

Ela agora diferencia explicitamente:

- desempenho atual;
- comparação entre período atual e período anterior equivalente;
- `performance_trend@1` oficial;
- suficiência estatística;
- comparação por disciplina;
- comparação por tópico;
- série diária/semana agregada quando o período é longo;
- histórico real futuro do progresso do edital.

Foi removida a antiga semântica de “primeira metade × segunda metade”.

## 5. Duplicações eliminadas

A lógica temporal relevante foi retirada da UI e centralizada em `analise_temporal.py`.

A UI deixou de calcular diretamente:

- divisão artificial do período em metades;
- delta de acurácia entre metades;
- comparação própria de revisões/dia;
- comparação própria de questões/dia;
- evolução por disciplina por consultas paralelas;
- domínio histórico baseado em `efetividade_sessoes.dominio_medio_depois`.

Também foi removido do `main.py` o helper antigo `definir_tendencia_evolucao`, que já não possuía consumidores e ainda continha linguagem baseada em “metades”.

## 6. Arquitetura temporal criada

Foi criado `analise_temporal.py`, com o snapshot central `TemporalAnalyticsSnapshot`.

O snapshot contém:

- concurso;
- período atual;
- período anterior equivalente;
- métricas atuais;
- métricas anteriores;
- comparações;
- série diária;
- série de apresentação;
- disciplinas;
- tópicos;
- tendência oficial;
- suficiência;
- avisos de linhagem;
- foco global;
- histórico futuro de progresso;
- horário e versão de geração.

`banco.obter_analise_temporal()` passou a ser o adaptador único para a UI.

## 7. Períodos oficiais

São suportados:

- 7 dias;
- 30 dias;
- 60 dias;
- 90 dias;
- período personalizado.

Os períodos são construídos a partir de `statistics_core.periods.StatisticalPeriods`.

O intervalo personalizado recebido da UI tem fim inclusivo e é convertido internamente para `end_exclusive` no dia seguinte. O período anterior é derivado por `previous_equivalent()` e possui a mesma duração do atual.

## 8. Comparação atual × anterior

A comparação de acurácia somente é considerada válida quando **ambos** os períodos possuem:

- pelo menos 10 tentativas efetivas;
- pelo menos 2 dias ativos.

Quando essa base não existe, a interface mostra `Dados insuficientes para comparação` e detalha os requisitos faltantes.

Contagens continuam podendo ser comparadas descritivamente sem que volume seja interpretado como melhora acadêmica.

## 9. Critérios de suficiência

A suficiência é calculada na camada temporal e retorna:

- estado;
- `ready`;
- requisitos;
- quantidades faltantes.

A UI apenas apresenta esses resultados.

Ausência de base não é transformada em `0%`, melhora, queda ou estabilidade.

## 10. Tendência oficial

`performance_trend@1` continua sendo a tendência acadêmica oficial.

Ela permanece separada da comparação entre períodos de calendário. A Dashboard também foi alinhada para exibir a tendência oficial, em vez de usar uma comparação própria dos últimos 7 dias.

No banco real atual, `performance_trend@1` está em `insufficient_data`: a janela possui volume de tentativas, mas ainda não possui diversidade temporal/sessões suficiente para certificar tendência.

## 11. Séries diárias

A série diária é contínua no intervalo selecionado.

Para dias sem respostas:

- tentativas = `0`;
- acertos = `0`;
- questões únicas = `0`;
- sessões = `0`;
- taxa de acerto = `None`.

Assim, dias sem atividade não são desenhados como `0%` de desempenho.

Para períodos superiores a 30 dias, a camada fornece uma série de apresentação semanal explícita. Taxas semanais são recalculadas a partir de acertos/tentativas, sem média simples de taxas diárias.

## 12. Revisões e linhagem

A análise temporal respeita `revisoes.concurso_id`.

- revisão com `concurso_id` do perfil entra na métrica;
- revisão de outro concurso é excluída;
- revisão histórica com `concurso_id IS NULL` continua `legacy_limited` e não é atribuída ao perfil por inferência.

No banco real atual existem **5 revisões históricas sem linhagem de concurso** e **0 revisões com nova linhagem**. Por isso, as revisões qualificadas do perfil atual são 0 e as 5 antigas são reportadas como legado excluído quando pertinente.

## 13. Foco global

`sessoes_foco` continua sem linhagem histórica inequívoca de concurso.

Por isso, foco é tratado explicitamente como métrica **global de hábito** e não como métrica acadêmica do concurso ativo.

A UI foi renomeada para deixar esse escopo visível.

## 14. Domínio legado

`efetividade_sessoes.dominio_medio_depois` não é `mastery_score@1` versionado historicamente.

Ele deixou de alimentar a tendência principal e foi removido das opções visíveis do gráfico de Histórico.

Não houve conversão nem backfill desse indicador para domínio oficial.

## 15. Domínio atual oficial

O domínio atual continua disponível por meio do Núcleo Estatístico quando necessário, com estado e evidência correspondentes.

Ele não é copiado para dias passados e não é usado como uma série temporal retroativa.

## 16. Persistência histórica futura

Foi criada a tabela:

`progresso_snapshots_diarios`

Ela registra, a partir do Passo 8:

- cobertura de tópicos;
- cobertura de questões;
- distribuição de evidência;
- evidência suficiente;
- consolidação;
- domínio global atual e seu estado;
- versões de métrica/snapshot;
- data e instante real da captura.

## 17. Schema do snapshot diário

A tabela possui chave lógica única por:

`concurso_id + data + metric_version + snapshot_version`

A migração é aditiva e o schema do projeto passou de 17 para 18.

## 18. Política de captura

O mecanismo permite no máximo um estado efetivo por dia/perfil/versão.

- refresh sem mudança é no-op;
- mudança real no mesmo dia atualiza a linha;
- dia novo cria nova linha;
- alteração real de catálogo pode atualizar o snapshot do dia.

O snapshot não conta como atividade acadêmica.

## 19. Ausência de backfill

Nenhum snapshot histórico foi fabricado.

Na validação final foi capturado **1 snapshot real do estado atual**, datado de **18/09/2026**. Portanto, a interface deve informar que o histórico de progresso está disponível a partir dessa data e que ainda não existe série suficiente para tendência de progresso.

## 20. Disciplinas

A comparação por disciplina usa métricas oficiais do próprio escopo e eventos brutos agregados pelo Núcleo Estatístico.

Não há média simples entre tópicos.

A interface mostra:

- taxa atual;
- taxa anterior;
- delta em pontos percentuais quando comparável;
- tentativas atuais/anteriores;
- estado comparável/não comparável.

## 21. Tópicos

A comparação por tópico exige a mesma base mínima oficial em ambos os períodos.

Tópicos sem base suficiente permanecem `Não comparável ainda` e não são classificados como “maior queda”.

## 22. Maior evolução/queda

“Maior evolução” e “ponto de atenção” só podem surgir entre tópicos que possuem comparação temporal válida.

Sem essa base, a UI informa que ainda não existem amostras comparáveis.

Não há fallback de “menor domínio” sob o rótulo de queda temporal.

## 23. Gráficos

Os gráficos mantidos respondem perguntas específicas:

- desempenho diário;
- volume de tentativas;
- revisões qualificadas;
- histórico futuro de cobertura de questões.

Com apenas um snapshot de progresso, o gráfico de progresso não inventa uma linha e mostra que a coleta acabou de começar.

## 24. Performance e consultas

A análise usa APIs em lote para tópicos e disciplinas.

Em medição real com **88 tópicos**, **6 disciplinas** e série de 30 dias, a montagem completa do `TemporalAnalyticsSnapshot` executou **44 SELECTs**, sem crescimento por consulta individual de tópico. O teste automatizado de N+1 também passou.

## 25. Testes

Foi criado `test_analise_temporal.py`, cobrindo os cenários A–W solicitados, incluindo:

- períodos sem dados;
- base insuficiente;
- delta em pontos percentuais;
- separação entre tendência oficial e comparação temporal;
- dias sem respostas;
- isolamento de revisões por concurso;
- `legacy_limited`;
- foco global;
- domínio legado;
- snapshot futuro sem backfill;
- dois dias reais;
- atualização do snapshot do mesmo dia;
- alteração de catálogo;
- volumes diferentes entre disciplinas;
- tópico não comparável;
- período personalizado;
- timezone `America/Sao_Paulo`;
- N+1;
- preservação da Fila V3.

Após a retomada foram executados **116 testes unittest**, todos aprovados.

O smoke test também foi atualizado para o novo contrato de revisões qualificadas: a revisão criada pela fixture agora recebe `concurso_id`, e a validação de tópicos usa o snapshot temporal em vez do antigo campo legado de tendência. Resultado final: `VighnaStudy 0.24.0: testes smoke OK`.

## 26. Resultados no banco real

Estado observado na conclusão:

- concurso ativo: 40;
- 259 questões ativas no universo do concurso;
- 123 questões únicas respondidas no concurso ativo;
- cobertura de questões: aproximadamente 47,49%;
- 88 tópicos ativos no perfil;
- 1 tópico iniciado;
- 123 tentativas do concurso ativo;
- 100 acertos;
- 23 erros;
- taxa atual: aproximadamente 81,30%;
- 2 dias ativos dentro das tentativas do concurso analisadas no período oficial;
- 15 sessões de questões do concurso no período;
- 5 revisões antigas sem `concurso_id`;
- 0 revisões qualificadas novas;
- 1 snapshot diário real de progresso após a validação.

As tentativas totais do banco são 129: 123 pertencem ao concurso 40 e 6 pertencem ao concurso 3. A análise do concurso ativo não mistura os dois perfis.

## 27. Comparações reais atualmente válidas

Para 7, 30, 60 e 90 dias, **nenhuma comparação de taxa atual × período anterior é ainda válida**.

O período atual possui volume suficiente, mas o período anterior equivalente possui 0 tentativas e 0 dias ativos.

Também não existem, no banco real atual, disciplinas ou tópicos com base suficiente nos dois períodos para classificação de melhora/queda.

Esse resultado é intencional: a interface deve mostrar `Dados insuficientes` em vez de fabricar tendência.

## 28. Status da fila sombra

Fila ativa:

`fila_inteligente_v3`

Fila candidata:

`fila_candidate_shadow_v1`

`used_for_queue_order = false`

O gate permanece:

`INFRAESTRUTURA PRONTA / AMOSTRA AINDA INSUFICIENTE`

No checkpoint final há 0 observações sombra persistidas e os bloqueadores são somente os mínimos de amostra real definidos no Passo 6.

## 29. Validações finais

Concluídas:

- `python -m unittest discover -v` → **116/116 OK**;
- `python testes_smoke.py` → **OK**;
- `py_compile` dos módulos alterados/principais → **OK**;
- verificação de whitespace final nos arquivos alterados → **OK**;
- `PRAGMA integrity_check` → **ok**;
- `PRAGMA foreign_key_check` → **0 violações**.

O ambiente de validação disponível não possui `ruff`, `flake8` ou `pycodestyle`, portanto não foi possível executar o linter específico do ambiente Windows do projeto. Também não possui `PySide6`, então a inicialização gráfica real de `main.py` não pôde ser executada neste container. O arquivo `main.py` foi compilado com sucesso e os testes/smoke sem GUI passaram.

## 30. Recomendação para o Passo 9

A base está pronta para o próximo módulo analítico: **Mapa de Domínio**.

O Mapa de Domínio deve consumir o estado oficial atual e sempre exibir domínio junto do nível de evidência. Ele não deve transformar `insufficient_data` em zero e não deve depender da fila inteligente para ordenar ou classificar aprendizado.

A série temporal de domínio/consolidação deve permanecer limitada aos snapshots reais coletados a partir desta etapa; enquanto houver um único snapshot, o sistema deve continuar informando que ainda não existe série histórica suficiente.
