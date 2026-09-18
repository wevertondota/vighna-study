# Especificação Técnica do Núcleo Estatístico do VighnaStudy

**Versão do contrato:** 1.0  
**Data:** 18/09/2026  
**Base:** `RELATORIO_AUDITORIA_NUCLEO_ESTATISTICO.md`  
**Estado:** especificação normativa para a futura centralização; nenhuma fórmula, tela ou estrutura de banco foi alterada nesta etapa.

## 1. Finalidade e regra normativa

Este documento define o significado único das métricas oficiais do VighnaStudy. A cadeia obrigatória é:

```text
dado bruto -> métrica oficial versionada -> consumidores
```

Dashboard, Estatísticas, Fila Inteligente, Progresso, Tendências, Gamificação e relatórios não devem recalcular nem reinterpretar uma métrica oficial. Eles podem escolher período, escopo e apresentação, mas devem receber o valor e seus metadados do Núcleo Estatístico.

Os termos **DEVE**, **NÃO DEVE** e **PODE** são normativos. Fórmulas novas deste documento são o contrato de destino; não passam a descrever o resultado do código atual até que uma etapa posterior as implemente, teste e migre os consumidores.

Toda resposta futura do Núcleo deve informar, além do valor:

- `metric_id` e `metric_version`;
- escopo (`concurso_id`, disciplina, tópico, questão ou sessão);
- `period_start`, `period_end_exclusive` e timezone;
- `calculated_at`;
- estado `ok`, `insufficient_data`, `unavailable` ou `legacy_limited`;
- denominador, quando houver taxa;
- parâmetros não padrão e avisos de qualidade.

Percentuais são calculados com precisão completa e arredondados apenas na apresentação, por padrão para uma casa decimal. Divisão por zero retorna `insufficient_data`, nunca zero por conveniência.

## 2. Vocabulário oficial e universo de dados

### 2.1 Evento de resposta efetiva

Uma **tentativa efetiva** é uma linha de `tentativas_questoes` com `correta IN (0, 1)`. Ela representa uma alternativa efetivamente submetida e avaliada.

Uma linha com `correta IS NULL` é um **pulo**, não uma resposta, não um acerto e não um erro. Pulos possuem métricas próprias e jamais entram no denominador da taxa de acerto.

O identificador histórico da questão é `COALESCE(questao_id_snapshot, questao_id)`. O tópico e a disciplina históricos devem usar primeiro os respectivos IDs de snapshot, com relações atuais apenas como fallback. Nomes servem para exibição, não para agrupamento.

### 2.2 Escopo de perfil

Toda métrica acadêmica por perfil DEVE filtrar `tentativas_questoes.concurso_id`. Conteúdo corrente DEVE ainda respeitar inclusão e pausa de disciplina e tópico quando a métrica se referir ao universo ativo.

Tentativas históricas não são apagadas da estatística de desempenho porque a questão foi arquivada depois. Já cobertura é uma fotografia contra o catálogo ativo no instante do cálculo.

As tabelas `revisoes` e `sessoes_foco` não possuem hoje `concurso_id`. Portanto:

- revisões não podem ser tratadas como inequivocamente pertencentes a um perfil, salvo quando a linhagem das tentativas comprovar um único perfil;
- foco pode produzir métricas globais, mas não métricas oficiais por perfil sem vínculo inequívoco;
- associar o tópico ao perfil não prova que o evento ocorreu naquele perfil;
- valores afetados devem retornar `legacy_limited` ou `unavailable`, não ser silenciosamente compartilhados.

### 2.3 Universo ativo

Para catálogo, cobertura, progresso curricular e fila, um item está ativo quando:

1. a disciplina está incluída e não pausada no perfil;
2. o tópico está incluído e não pausado no perfil;
3. a questão está ativa e não excluída.

O Domínio V2 atual não cumpre o item 2 em todas as consultas. O contrato oficial exige o filtro uniforme.

### 2.4 Data de atribuição

- tentativa: `respondida_em`;
- sessão de questões: `iniciado_em` para contagem de sessões e `respondida_em` para respostas;
- revisão realizada: `realizada_em`; enquanto o legado não a tiver, `data` pode ser usado com aviso `legacy_limited`;
- revisão prevista: data corrente de `controle_topico.proxima_revisao`;
- foco: `inicio`, desde que `duracao_efetiva > 0` e o registro tenha sido finalizado;
- desempate cronológico: timestamp e, depois, `id`.

## 3. Acerto por tentativa não é questão única

As duas unidades não são intercambiáveis:

| Grandeza | Unidade | Regra |
|---|---|---|
| respostas/tentativas | evento | conta cada resposta efetiva |
| acertos | evento | conta cada tentativa com `correta = 1` |
| erros | evento | conta cada tentativa com `correta = 0` |
| questões únicas respondidas | questão | `COUNT(DISTINCT questao_ref)` entre tentativas efetivas |
| tentativas por questão | evento por questão | total de respostas efetivas daquela questão |
| último resultado | estado da questão | resultado da tentativa efetiva mais recente |

Exemplo obrigatório de referência:

```text
Questão A: erro, erro, erro, erro, acerto

attempt_count                 = 5
correct_attempt_count         = 1
incorrect_attempt_count       = 4
answered_unique_question_count = 1
last_attempt_result           = correct
```

A taxa global é `1 / 5 = 20%`. Não existe uma “taxa por questão” igual a 100% só porque o último resultado foi acerto. Quando o produto quiser medir o estado mais recente das questões, deve usar outra métrica explicitamente nomeada, como `latest_result_correct_question_rate`, e nunca chamá-la de `accuracy_rate`.

## 4. Períodos estatísticos oficiais

O timezone do contrato 1.0 é `America/Sao_Paulo`. Os intervalos são semiabertos: incluem o início e excluem o fim. O instante de referência é `as_of` e, se omitido, é o instante do cálculo.

| Período | Identificador | Limites exatos |
|---|---|---|
| hoje | `today` | início do dia civil de `as_of` até início do dia seguinte |
| últimos 7 dias | `last_7_days` | início do dia de `as_of - 6 dias` até início do dia seguinte a `as_of` |
| últimos 30 dias | `last_30_days` | início do dia de `as_of - 29 dias` até início do dia seguinte a `as_of` |
| anterior equivalente | `previous_equivalent` | intervalo imediatamente anterior, adjacente e com a mesma quantidade de dias civis |
| histórico total | `all_time` | sem limite inferior até `as_of`, inclusive por meio do fim exclusivo adequado |

“Últimos 7 dias” inclui hoje e contém exatamente sete datas civis. Não significa “últimas 168 horas”. Comparações devem receber explicitamente o par de intervalos. Datas-texto atuais são interpretadas como horário local legado; até a persistência carregar offset, o resultado deve declarar `legacy_local_time`.

## 5. Disposição dos cálculos encontrados na auditoria

| Cálculo atual | Avaliação | Destino contratual |
|---|---|---|
| tentativa individual, resultado, sessão, perfil e snapshots | correto e confiável | manter como fonte bruta principal |
| respostas, acertos e erros por sessão com `correta IS NOT NULL` | correto | centralizar sem mudar a aritmética |
| questões únicas por `questao_id`/snapshot | correto | manter com identidade histórica padronizada |
| pulos separados de acertos/erros | correto | manter como `skipped_attempt_count` |
| duração efetiva de foco finalizado | correta em escopo global | manter; por perfil fica indisponível até haver identidade |
| duração de sessão por soma de `tempo_segundos` | útil, mas incompleta se faltarem tempos | manter com indicador de cobertura temporal |
| duração de parede da sessão | calculável, mas inclui interrupções | manter como telemetria, não como tempo ativo |
| percentual da revisão mais recente | aritmeticamente correto, semanticamente limitado | manter renomeado `latest_review_accuracy_rate`; nunca usar como domínio ou “média atual” |
| média simples dos percentuais mais recentes dos tópicos | inconsistente e não ponderada | substituir pelas agregações oficiais; não migrar o rótulo “média atual” |
| média das médias das disciplinas | estatisticamente incorreta | retirar após comparação; recalcular dos eventos brutos |
| soma de `revisoes.questoes` chamada de “questões respondidas” | ambígua e pode divergir das tentativas | renomear `review_reported_question_count` ou substituir por `answered_attempt_count` |
| tendência do Histórico baseada em tentativas | base correta | tornar a fonte oficial de desempenho temporal |
| tendência do dashboard/aba baseada em revisões | válida apenas como tendência de revisões | manter somente com nome de revisão; substituir como tendência de desempenho |
| pontos fracos pelo último percentual de revisão | insuficiente | substituir por domínio + evidência + erros + tendência |
| estados de progresso por 3/4 revisões e último percentual | regra simples, mas não mede consolidação | preservar como `legacy_review_progress_state` durante transição; substituir por `topic_consolidation_status` |
| Domínio V2 | sofisticado e explicável, com boa proteção contra pouca amostra | preservar para caracterização; substituir de forma versionada pelo domínio oficial após testes |
| evidência embutida no Domínio V2 | útil, mas mistura estimativa e confiança | extrair como dimensão oficial independente |
| cobertura embutida no Domínio V2 | útil, mas mistura conteúdo visto e conhecimento | publicar separadamente; domínio oficial não usa cobertura diretamente |
| classificação de erros e recuperação do Domínio V2 | valiosa | manter como componente oficial de controle de erros |
| prioridade V3 e recomendador | consumidores/decisores, não métricas fundamentais | devem consumir métricas oficiais e manter fórmula própria versionada |
| fallback legado da fila | produz prioridades não comparáveis na mesma lista | descontinuar apenas após paridade e cobertura do caminho oficial |
| pontualidade com `prazo_historico_valido = 1` | correta e prudente | manter; registros sem prazo permanecem insuficientes |
| revisões iniciais agregadas | dado legado real, mas sem eventos | manter como agregado; não fabricar datas, resultados ou distribuição |
| snapshots `efetividade_*` | fotografias derivadas válidas | manter como observação histórica; nunca somar como tentativa bruta |
| domínio observado por snapshots | série parcial, não reconstrução histórica | manter qualificado; não chamar de histórico completo de domínio |
| sessões legadas sem itens congelados | telemetria insuficiente | manter com flag; não inferir planejadas, puladas ou não alcançadas |
| revisões compartilhadas entre perfis | inconsistente | não certificar métricas por perfil até migração de identidade/linhagem |
| tópico pausado incluído no Domínio V2 | inconsistente | filtro obrigatório no domínio oficial |

## 6. Métricas fundamentais por entidade

### 6.1 Questões e tentativas

- `answered_attempt_count`: número de tentativas efetivas.
- `answered_unique_question_count`: questões distintas com ao menos uma tentativa efetiva.
- `correct_attempt_count` e `incorrect_attempt_count`: acertos e erros por evento.
- `accuracy_rate` e `error_rate`: taxas complementares sobre tentativas efetivas.
- `question_attempt_count`: tentativas efetivas de uma questão.
- `last_attempt_at`: data/hora da tentativa efetiva mais recente.
- `last_attempt_result`: `correct`, `incorrect` ou `insufficient_data`.
- `recent_result_sequence`: últimos resultados em ordem do mais recente para o mais antigo; janela padrão 10, configurável até 50.
- `skipped_attempt_count`: pulos, fora das taxas de acerto e erro.

### 6.2 Sessões de questões

- `question_session_count`: sessões iniciadas no período, inclusive vazias/interrompidas.
- `completed_question_session_count`: sessões com `concluida = 1`.
- `session_answered_attempt_count`, `session_correct_attempt_count` e `session_incorrect_attempt_count`: contagens dentro da sessão.
- `session_accuracy_rate`: acertos da sessão divididos por respostas efetivas.
- `session_active_duration_seconds`: soma dos `tempo_segundos` válidos das tentativas; só é completa quando todas as respostas efetivas têm tempo válido.
- `session_wall_duration_seconds`: `encerrado_em - iniciado_em`; telemetria separada, nunca substituto silencioso do tempo ativo.
- `last_question_session_at`: maior `iniciado_em` dentro do escopo.

Quantidade planejada, apresentada, não respondida e não alcançada são métricas auxiliares de itens congelados. Em sessões legadas sem itens, ficam indisponíveis; `objetivo` não deve ser usado como fato de que as questões foram planejadas individualmente.

### 6.3 Atividade

Um **dia estudado** é uma data civil com ao menos um dos seguintes eventos atribuíveis ao escopo: tentativa efetiva, foco persistido com duração positiva ou revisão manual qualificada. Revisão automática derivada de tentativas não cria um segundo dia. No perfil, fontes sem `concurso_id` ou linhagem inequívoca ficam excluídas e geram aviso de cobertura.

- `study_day_count`: quantidade de datas civis distintas estudadas.
- `last_study_date`: data civil do último evento qualificável.
- `answered_attempt_count` por período: respostas efetivas pelo timestamp da tentativa.
- `question_session_count` por período: sessões pelo timestamp de início.
- `study_frequency_days_per_week`: `study_day_count / calendar_day_count * 7`, somente em intervalos de pelo menos 7 dias.

Frequência mede regularidade de dias, não volume de questões. Volume e frequência devem ser exibidos separadamente.

### 6.4 Tópico

Cada tópico publica:

- tentativas, questões únicas, acertos, erros e taxa de acerto recalculados dos eventos brutos;
- sessões distintas que contêm ao menos uma tentativa efetiva do tópico;
- última atividade qualificável;
- revisões qualificadas e seus resultados;
- desempenho recente e tendência;
- domínio atual;
- cobertura do banco de questões;
- nível de evidência;
- estado de consolidação.

### 6.5 Disciplina, perfil/concurso e global

As métricas equivalentes são recalculadas sobre a união dos registros brutos do escopo. Não se calcula taxa de acerto da disciplina pela média das taxas de seus tópicos. Domínio agregado é recalculado aplicando a mesma fórmula aos eventos do escopo, acompanhado de cobertura e evidência agregadas; não é média simples de domínios de tópico.

No perfil, somente dados inequivocamente atribuídos ao `concurso_id` entram. Global significa todos os perfis, com deduplicação por ID de evento — não soma de telas por perfil, pois conteúdo/eventos podem se sobrepor.

### 6.6 Revisões

- `scheduled_review_count`: agendas correntes cuja próxima data cai no período.
- `completed_review_count`: eventos de revisão realizados e atribuíveis ao escopo.
- `overdue_review_count`: agendas correntes com `proxima_revisao < data de as_of`.
- `last_review_at`: última revisão realizada qualificável.
- `next_review_date`: próxima data corrente; não é histórico de agendamento.
- `review_accuracy_rate`: `SUM(acertos) / SUM(questoes) * 100` no conjunto de revisões, nunca média dos percentuais.
- `topic_review_count`: número de eventos de revisão qualificáveis do tópico.

Uma revisão só participa de estatística por perfil se tiver perfil explícito ou se todos os seus membros comprovados pertencerem ao mesmo perfil. `revisoes_iniciais` participa apenas de `legacy_initial_review_count`, não de taxa, tendência, pontualidade ou datas.

## 7. Domínio

### 7.1 Fórmula atual: `legacy_domain_v2`

O código atual usa as últimas 50 tentativas como base, as últimas 15 como janela recente, até seis dias recentes para estabilidade, as últimas 30 para dúvida e o histórico completo para volume/evidência.

Se houver mais de 15 tentativas consideradas:

```text
desempenho = 0,65 * desempenho_recente + 0,35 * desempenho_base
```

Caso contrário, usa `desempenho_base`.

```text
dominio_bruto =
    0,30 * desempenho
  + 0,20 * variedade
  + 0,15 * estabilidade
  + 0,10 * recencia
  + 0,15 * controle_erros
  + 0,10 * evidencia
  - penalidade_duvida
```

`variedade = 0,55 * cobertura + 0,45 * diversidade_recente` quando existem questões ativas. Estabilidade combina número de dias recentes e dispersão dos percentuais diários. Recência usa degraus de 100 até 7 dias, 90 até 14, 75 até 30, 60 até 45, 45 até 60, 25 até 90 e 10 depois disso.

As subfórmulas atuais relevantes são:

```text
cobertura = questões ativas distintas já respondidas / questões ativas * 100
diversidade_recente = min(100, questões ativas distintas nas últimas 50
                                 / min(12, questões ativas) * 100)

consistencia = max(0, 100 - min(100, 2 * desvio_padrao(percentuais_dos_dias)))
evidencia_temporal_recente = min(100, dias_recentes * 20)
estabilidade = evidencia_temporal_recente * (0,5 + 0,5 * consistencia / 100)

penalidade_absoluta = 18*criticas + 10*recorrentes
                    + 4*em_recuperacao + 1,5*isoladas
penalidade_proporcional = min(35,
    (criticas + 0,60*recorrentes + 0,25*em_recuperacao)
    / max(1, questões_ativas_respondidas) * 35)
bonus_recuperacao = min(10,
    recuperadas / max(1, questões_ativas_respondidas) * 16)
controle_erros = clamp(100 - penalidade_absoluta
                            - penalidade_proporcional
                            + bonus_recuperacao, 0, 100)

score_volume = min(100, tentativas_historicas / 30 * 100)
score_unicas = min(100, questões_unicas_historicas / 10 * 100)
score_dias = min(100, dias_historicos / 6 * 100)
score_revisoes = min(100, revisoes_ponderadas / 4 * 100)
evidencia = 0,35*score_volume + 0,30*score_unicas
          + 0,20*score_dias + 0,15*score_revisoes
```

Revisões de confiança muito baixa, baixa e demais pesam respectivamente 0,25, 0,50 e 1,00; cada revisão inicial importada, limitada às quatro primeiras, pesa 0,40. A penalidade de dúvida é `min(8, taxa_duvida_nas_ultimas_30 * 0,08)`.

Os tetos atuais são 49 se houver menos de 3 tentativas ou 2 únicas; 59 se houver menos de 7 tentativas ou 2 dias; 69 se houver menos de 12 tentativas ou 3 únicas; e 84 se houver menos de 20 tentativas, 4 únicas ou 3 dias. Scores de 85 ou mais ainda exigem variedade mínima de 45, ausência de erros críticos/recorrentes e taxa de dúvida no máximo 30%; scores de 95 ou mais exigem 40 tentativas, 8 únicas, 5 dias, variedade 70, recência mínima 75 e dúvida no máximo 20%. Se esses requisitos extras falharem, aplicam-se tetos 84 ou 94.

**Vantagens:** usa recência, diversidade, estabilidade, erros por questão, recuperação, dúvidas e tetos contra amostra pequena; respostas antigas ainda contribuem como evidência sem dominar totalmente o desempenho recente; é explicável em componentes.

**Problemas:** mistura conhecimento, cobertura e confiança no mesmo número; revisões podem contaminar perfis; tópicos pausados entram em parte do universo; arquivar questões altera cobertura retroativamente; médias do score podem dar peso igual a tópicos desiguais; estabilidade diária é sensível a dias com apenas uma resposta.

**Poucas questões:** os tetos evitam declarar domínio forte, mas o score mistura a penalização de confiança com o conhecimento estimado. **Muitas questões:** a janela limita o peso do passado, mas o histórico continua elevando evidência. **Respostas antigas:** afetam histórico, cobertura, erros e evidência; só as 50 mais recentes afetam o desempenho-base. **Recentes:** recebem peso alto pela janela de 15. **Revisões:** entram na evidência, não diretamente no desempenho. **Erros consecutivos:** reduzem controle de erros. **Recuperação:** um ou dois acertos mudam a questão para recuperação; três acertos recentes retiram o erro aberto e podem gerar bônus.

O V2 deve permanecer intacto até haver testes de caracterização, mas seu resultado deve ser identificado como legado durante a transição.

### 7.2 Definição oficial proposta: `mastery_score@1`

Domínio é o **grau atual de conhecimento demonstrado** no escopo. Não é volume, cobertura curricular, quantidade de revisões, prioridade ou confiança estatística.

Componentes reutilizados e ajustados do V2:

```text
current_performance =
    accuracy(last 50),                                      se N <= 15
    0,65 * accuracy(last 15) + 0,35 * accuracy(last 50),   se N > 15

mastery_raw =
    0,55 * current_performance
  + 0,25 * error_control
  + 0,15 * temporal_stability
  + 0,05 * recency
  - doubt_penalty

mastery_score = clamp(mastery_raw, 0, 100)
```

Regras:

- `error_control` mantém a classificação explicável de erros e recuperação do V2;
- `temporal_stability` mantém a lógica de até seis dias, mas um dia só é elegível com pelo menos 3 tentativas efetivas no escopo; com menos de 2 dias elegíveis, o componente é neutro (`50`) e recebe aviso de evidência temporal baixa;
- `recency` mantém os degraus do V2;
- `doubt_penalty` mantém o máximo de 8 pontos nas últimas 30 tentativas;
- cobertura e evidência não entram na fórmula; são dimensões obrigatórias ao lado do domínio;
- revisões só influenciam domínio quando produzem tentativas efetivas. Um percentual manual agregado não substitui eventos de resposta;
- respostas antigas deixam de dominar pela janela de 50, mas permanecem na evidência e no histórico de erros;
- recuperação posterior melhora desempenho recente e controle de erros; erro antigo recuperado não mantém punição permanente.

Faixas descritivas iniciais, configuráveis:

| Score | Faixa |
|---:|---|
| 0 a 29,9 | crítico |
| 30 a 49,9 | frágil |
| 50 a 69,9 | em desenvolvimento |
| 70 a 84,9 | consolidando |
| 85 a 94,9 | dominado |
| 95 a 100 | domínio forte |

Com evidência `Insuficiente`, o serviço pode calcular `mastery_estimate` para diagnóstico, mas `mastery_score` público retorna `insufficient_data`. Com evidência `Baixa`, o valor deve ser exibido como **provisório** e não pode, sozinho, consolidar nem ranquear um ponto forte. Isso preserva a separação entre estimativa e confiança sem deformar o score com tetos de amostra.

## 8. Nível de evidência

`evidence_level@1` usa regras de corte, não uma fórmula opaca. Entradas: tentativas efetivas (`N`), questões únicas (`U`), sessões distintas com respostas (`S`), dias ativos (`D`), amplitude entre primeiro e último dia (`T`) e revisões qualificadas em dias posteriores ao primeiro estudo (`R`).

| Categoria | Requisitos cumulativos |
|---|---|
| Insuficiente | `N < 3` ou `U < 2` |
| Baixa | atende ao mínimo anterior, mas não atende à Moderada |
| Moderada | `N >= 10`, `U >= 5`, `S >= 2`, `D >= 3` e (`T >= 7 dias` ou `R >= 1`) |
| Alta | `N >= 30`, `U >= 10`, `S >= 4`, `D >= 5`, `T >= 21 dias` e `R >= 2` em datas distintas |

Cada categoria também possui ordem técnica `0..3`. Se a linhagem de revisão não for confiável, `R` é desconhecido, não zero. Nesse caso, a categoria pode chegar a Moderada pela amplitude temporal, mas não a Alta, que exige revisão qualificada. Sessões nulas em tentativas legadas não são inventadas; se a contagem necessária não puder ser demonstrada, aplica-se a categoria comprovável mais baixa e o aviso `legacy_limited`.

Assim, 3 respostas únicas e 100% de acerto resultam em evidência Baixa; 80 respostas, 10 ou mais questões, múltiplas sessões e distribuição temporal podem chegar a Alta. Os domínios podem ser 100 e 85 respectivamente, mas a confiança e as decisões permitidas serão diferentes.

## 9. Cobertura

Cobertura mede quanto do conteúdo disponível foi trabalhado, não quão bem foi aprendido.

### 9.1 Cobertura de questões

```text
question_coverage_rate =
    active_unique_questions_answered / active_available_questions * 100
```

O numerador contém questões atualmente ativas do escopo com pelo menos uma tentativa efetiva histórica no perfil. O denominador é o catálogo ativo conforme a seção 2.3. Sem questões disponíveis, retorna `insufficient_data`, não 0 nem 100.

### 9.2 Cobertura de tópicos

```text
topic_coverage_rate =
    active_topics_with_at_least_one_effective_attempt / active_topics * 100
```

Um tópico “estudado” para esta métrica exige tentativa efetiva; revisão inicial importada, agenda ou foco sem vínculo a questões não prova cobertura do banco de questões.

### 9.3 Limitações

- o catálogo atual não preserva integralmente o denominador histórico; arquivo, exclusão e importação podem alterar a cobertura recalculada;
- quantidade de questões no banco não garante representatividade uniforme do conteúdo;
- tópicos sem questões não têm cobertura de questão calculável, embora existam curricularmente;
- cobertura alta pode coexistir com domínio baixo e vice-versa;
- snapshots permitem preservar tentativas, mas não reconstruir com segurança todo catálogo disponível em uma data passada.

## 10. Desempenho recente e tendência

`recent_performance_rate@1` usa as 15 tentativas efetivas mais recentes do escopo. A tendência usa duas janelas consecutivas e não sobrepostas:

- janela atual: tentativas 1 a 15, do mais recente para trás;
- janela anterior: tentativas 16 a 30;
- cada janela precisa ter pelo menos 10 tentativas efetivas;
- o conjunto precisa abranger pelo menos 2 datas civis e 2 sessões distintas comprováveis.

```text
trend_delta_pp = accuracy(current_window) - accuracy(previous_window)
```

| Resultado | Regra inicial configurável |
|---|---|
| melhora | `trend_delta_pp >= +5,0` |
| estabilidade | `-5,0 < trend_delta_pp < +5,0` |
| queda | `trend_delta_pp <= -5,0` |
| dados insuficientes | qualquer requisito de amostra não atendido |

A sequência recente de uma questão é informativa, mas uma resposta isolada contra outra não constitui tendência. Em disciplina, perfil e global, as janelas são refeitas sobre as tentativas brutas daquele escopo; tendências de tópicos não são promediadas.

## 11. Tópico consolidado

`topic_consolidation_status@1` possui três estados: `consolidated`, `not_consolidated` e `insufficient_data`. Os parâmetros são configuráveis e seus valores padrão são:

```text
mastery_score >= 85
evidence_level >= Moderate
distinct_answered_session_count >= 3
qualified_review_count >= 1, posterior ao primeiro contato
performance_trend != decline
critical_open_error_count = 0
last_activity_age_days <= 30
```

Se domínio, evidência, revisão qualificada ou tendência não puderem ser avaliados, o estado é `insufficient_data`, não `not_consolidated`. Uma única sessão perfeita não consolida um tópico. Consolidação é um estado derivado atual e pode ser perdido por queda, erro crítico ou envelhecimento da evidência; seu histórico futuro deve ser persistido como evento, não reconstruído por suposição.

## 12. Regras de agregação

| Tipo de métrica | Questão -> tópico -> disciplina -> perfil -> global |
|---|---|
| tentativas, acertos, erros, sessões e revisões | somar eventos deduplicados por ID; no global, nunca somar resultados já agregados por perfil |
| questões únicas | `COUNT(DISTINCT questao_ref)` no conjunto bruto; não somar contagens se houver possibilidade de sobreposição |
| dias estudados | união das datas civis; nunca soma dos dias de tópicos |
| taxa de acerto/erro | recalcular `SUM(numerador) / SUM(denominador)`; nunca média simples de percentuais |
| resultado de revisões | recalcular `SUM(acertos) / SUM(questoes)` apenas em eventos qualificados |
| última atividade/tentativa/sessão/revisão | máximo dos timestamps válidos |
| próxima revisão | mínimo das próximas datas correntes válidas; contagens continuam separadas |
| duração | somar durações ativas completas; duração parcial mantém aviso |
| cobertura de questões | união de questões ativas respondidas / união de questões ativas disponíveis |
| cobertura de tópicos | tópicos ativos estudados / tópicos ativos |
| evidência | reaplicar os cortes aos eventos do escopo; não usar média das categorias |
| desempenho recente e tendência | reconstruir janelas dos eventos do escopo |
| domínio | reaplicar `mastery_score@1` aos eventos do escopo; nunca média simples dos tópicos |
| consolidação | contar/proporcionar tópicos consolidados; não calcular “média de consolidação” |
| sequência recente/último resultado | não agregar; retornar por questão ou lista ordenada |

Domínio agregado descreve conhecimento demonstrado no conjunto efetivamente respondido. Deve sempre ser apresentado com cobertura, pois muitas tentativas concentradas em poucos tópicos podem gerar domínio agregado robusto sem cobrir a disciplina inteira.

## 13. Dados insuficientes

Zero é um valor; ausência de base para concluir é um estado. Contagens podem retornar zero. Taxas, tendências e inferências seguem estas regras:

| Métrica/uso | Mínimo oficial |
|---|---|
| taxa de acerto/erro | 1 tentativa efetiva |
| último resultado/sequência | 1 tentativa efetiva |
| duração ativa da sessão | tempo válido em 100% das tentativas efetivas da sessão; caso contrário valor parcial + aviso ou `insufficient_data` para comparação |
| cobertura de questões | pelo menos 1 questão ativa disponível |
| domínio público | `N >= 3` e `U >= 2`; com evidência Baixa, valor provisório |
| tendência | duas janelas com ao menos 10 tentativas cada, 2 dias e 2 sessões no conjunto |
| comparação entre períodos | ao menos 10 tentativas e 2 dias ativos em cada período para taxa; contagens podem ser comparadas sem inferência |
| pontos fracos por domínio | domínio calculável e evidência ao menos Baixa; tópicos sem evidência formam uma lista separada de “não avaliados” |
| consolidação | todos os componentes obrigatórios disponíveis |
| pontualidade | `prevista_para`, `realizada_em` e `prazo_historico_valido = 1` |
| frequência semanal | período com ao menos 7 dias civis |

Interface e algoritmos não devem converter `insufficient_data` em 0, “ruim”, “não estudado” ou “estável”. O payload deve trazer `missing_requirements`, por exemplo `{"attempts_needed": 7, "unique_questions_needed": 3}`.

## 14. Dicionário de métricas oficiais

Nas entradas abaixo, “agregação: recalcular” significa operar sobre registros brutos conforme a seção 12.

### 14.1 Respostas e questões

**NOME:** Total de respostas  
**Identificador técnico:** `answered_attempt_count`  
**Descrição:** Quantidade de alternativas submetidas e avaliadas.  
**Fonte dos dados:** `tentativas_questoes`.  
**Fórmula:** `COUNT(*) WHERE correta IN (0,1)`.  
**Unidade:** tentativas.  
**Nível de agregação:** questão, sessão, tópico, disciplina, perfil, período e global.  
**Quantidade mínima de dados:** nenhuma; retorna 0.  
**Pode retornar dados insuficientes:** não.  
**Consumidores previstos:** Dashboard, Estatísticas, Sessão, Tendências, Fila e relatórios.  
**Observações:** pulos não entram.

**NOME:** Questões únicas respondidas  
**Identificador técnico:** `answered_unique_question_count`  
**Descrição:** Quantidade de questões distintas com resposta efetiva.  
**Fonte dos dados:** `tentativas_questoes`, IDs/snapshots.  
**Fórmula:** `COUNT(DISTINCT questao_ref)`.  
**Unidade:** questões.  
**Nível de agregação:** tópico, disciplina, perfil, período e global.  
**Quantidade mínima de dados:** nenhuma; retorna 0.  
**Pode retornar dados insuficientes:** não.  
**Consumidores previstos:** Dashboard, Estatísticas, Cobertura, Evidência e relatórios.  
**Observações:** uma questão respondida cinco vezes conta uma vez.

**NOME:** Acertos  
**Identificador técnico:** `correct_attempt_count`  
**Descrição:** Tentativas efetivas corretas.  
**Fonte dos dados:** `tentativas_questoes`.  
**Fórmula:** `COUNT(*) WHERE correta = 1`.  
**Unidade:** tentativas.  
**Nível de agregação:** todos.  
**Quantidade mínima de dados:** nenhuma; retorna 0.  
**Pode retornar dados insuficientes:** não.  
**Consumidores previstos:** todos os consumidores acadêmicos.  
**Observações:** não representa questões atualmente dominadas.

**NOME:** Erros  
**Identificador técnico:** `incorrect_attempt_count`  
**Descrição:** Tentativas efetivas incorretas.  
**Fonte dos dados:** `tentativas_questoes`.  
**Fórmula:** `COUNT(*) WHERE correta = 0`.  
**Unidade:** tentativas.  
**Nível de agregação:** todos.  
**Quantidade mínima de dados:** nenhuma; retorna 0.  
**Pode retornar dados insuficientes:** não.  
**Consumidores previstos:** todos os consumidores acadêmicos.  
**Observações:** `acertos + erros = respostas efetivas`.

**NOME:** Taxa de acerto  
**Identificador técnico:** `accuracy_rate`  
**Descrição:** Percentual de tentativas efetivas corretas.  
**Fonte dos dados:** `tentativas_questoes`.  
**Fórmula:** `correct_attempt_count / answered_attempt_count * 100`.  
**Unidade:** percentual.  
**Nível de agregação:** questão, sessão, tópico, disciplina, perfil, período e global.  
**Quantidade mínima de dados:** 1 tentativa efetiva.  
**Pode retornar dados insuficientes:** sim.  
**Consumidores previstos:** Dashboard, Estatísticas, Sessão, Tendências e relatórios.  
**Observações:** recalcular; nunca média de percentuais.

**NOME:** Taxa de erro  
**Identificador técnico:** `error_rate`  
**Descrição:** Percentual de tentativas efetivas incorretas.  
**Fonte dos dados:** `tentativas_questoes`.  
**Fórmula:** `incorrect_attempt_count / answered_attempt_count * 100`.  
**Unidade:** percentual.  
**Nível de agregação:** questão, sessão, tópico, disciplina, perfil, período e global.  
**Quantidade mínima de dados:** 1 tentativa efetiva.  
**Pode retornar dados insuficientes:** sim.  
**Consumidores previstos:** Estatísticas, Caderno de erros, Fila e relatórios.  
**Observações:** salvo arredondamento de exibição, complementa `accuracy_rate` até 100%.

**NOME:** Tentativas por questão  
**Identificador técnico:** `question_attempt_count`  
**Descrição:** Número de respostas efetivas registradas para uma questão.  
**Fonte dos dados:** `tentativas_questoes`.  
**Fórmula:** `COUNT(*)` por `questao_ref` com resultado efetivo.  
**Unidade:** tentativas.  
**Nível de agregação:** questão.  
**Quantidade mínima de dados:** nenhuma; retorna 0.  
**Pode retornar dados insuficientes:** não.  
**Consumidores previstos:** Histórico da questão, Erros, Domínio e Evidência.  
**Observações:** não deduplicar respostas repetidas.

**NOME:** Última tentativa  
**Identificador técnico:** `last_attempt_at`  
**Descrição:** Data/hora da resposta efetiva mais recente.  
**Fonte dos dados:** `tentativas_questoes.respondida_em`.  
**Fórmula:** registro máximo por `(respondida_em, id)`.  
**Unidade:** timestamp.  
**Nível de agregação:** questão, tópico, disciplina, perfil e global.  
**Quantidade mínima de dados:** 1 tentativa efetiva.  
**Pode retornar dados insuficientes:** sim.  
**Consumidores previstos:** Histórico, Fila, Recência e relatórios.  
**Observações:** horário local legado deve ser sinalizado.

**NOME:** Último resultado  
**Identificador técnico:** `last_attempt_result`  
**Descrição:** Resultado da tentativa efetiva mais recente.  
**Fonte dos dados:** `tentativas_questoes.correta`.  
**Fórmula:** `correct` se 1, `incorrect` se 0 no registro mais recente.  
**Unidade:** enumeração.  
**Nível de agregação:** questão.  
**Quantidade mínima de dados:** 1 tentativa efetiva.  
**Pode retornar dados insuficientes:** sim.  
**Consumidores previstos:** Histórico, Caderno de erros e Fila.  
**Observações:** não substitui taxa histórica.

**NOME:** Sequência recente de resultados  
**Identificador técnico:** `recent_result_sequence`  
**Descrição:** Sequência ordenada dos resultados mais recentes de uma questão.  
**Fonte dos dados:** `tentativas_questoes`.  
**Fórmula:** últimos `N` resultados por `(respondida_em DESC, id DESC)`, padrão 10.  
**Unidade:** lista de `correct|incorrect`.  
**Nível de agregação:** questão.  
**Quantidade mínima de dados:** 1 tentativa efetiva.  
**Pode retornar dados insuficientes:** sim.  
**Consumidores previstos:** Caderno de erros, explicação de Domínio e Fila.  
**Observações:** tamanho real e solicitado devem acompanhar o valor.

### 14.2 Sessões e atividade

**NOME:** Total de sessões de questões  
**Identificador técnico:** `question_session_count`  
**Descrição:** Sessões iniciadas no escopo, mesmo sem resposta.  
**Fonte dos dados:** `sessoes_questoes`.  
**Fórmula:** `COUNT(DISTINCT id)` por `iniciado_em`.  
**Unidade:** sessões.  
**Nível de agregação:** tópico quando demonstrável por tentativa/item, disciplina, perfil, período e global.  
**Quantidade mínima de dados:** nenhuma; retorna 0.  
**Pode retornar dados insuficientes:** não para perfil/global; sim para escopo acadêmico de sessão vazia legado.  
**Consumidores previstos:** Dashboard, Histórico e relatórios.  
**Observações:** sessões vazias devem ser identificadas, não descartadas silenciosamente.

**NOME:** Sessões concluídas  
**Identificador técnico:** `completed_question_session_count`  
**Descrição:** Sessões marcadas como concluídas.  
**Fonte dos dados:** `sessoes_questoes.concluida`.  
**Fórmula:** `COUNT(*) WHERE concluida = 1`.  
**Unidade:** sessões.  
**Nível de agregação:** perfil, período e global; tópico/disciplinas quando o escopo for demonstrável.  
**Quantidade mínima de dados:** nenhuma; retorna 0.  
**Pode retornar dados insuficientes:** não.  
**Consumidores previstos:** Dashboard, Histórico e Efetividade.  
**Observações:** concluída não implica que atingiu o objetivo.

**NOME:** Questões respondidas na sessão  
**Identificador técnico:** `session_answered_attempt_count`  
**Descrição:** Respostas efetivas pertencentes à sessão.  
**Fonte dos dados:** `tentativas_questoes.sessao_id`.  
**Fórmula:** `answered_attempt_count` filtrado pela sessão.  
**Unidade:** tentativas.  
**Nível de agregação:** sessão.  
**Quantidade mínima de dados:** nenhuma; retorna 0.  
**Pode retornar dados insuficientes:** não.  
**Consumidores previstos:** Resumo da sessão, Simulados e Efetividade.  
**Observações:** planejadas/apresentadas são métricas diferentes.

**NOME:** Acertos da sessão  
**Identificador técnico:** `session_correct_attempt_count`  
**Descrição:** Respostas corretas da sessão.  
**Fonte dos dados:** `tentativas_questoes`.  
**Fórmula:** `correct_attempt_count` filtrado pela sessão.  
**Unidade:** tentativas.  
**Nível de agregação:** sessão.  
**Quantidade mínima de dados:** nenhuma; retorna 0.  
**Pode retornar dados insuficientes:** não.  
**Consumidores previstos:** Resumo, Simulados e Efetividade.  
**Observações:** —

**NOME:** Erros da sessão  
**Identificador técnico:** `session_incorrect_attempt_count`  
**Descrição:** Respostas incorretas da sessão.  
**Fonte dos dados:** `tentativas_questoes`.  
**Fórmula:** `incorrect_attempt_count` filtrado pela sessão.  
**Unidade:** tentativas.  
**Nível de agregação:** sessão.  
**Quantidade mínima de dados:** nenhuma; retorna 0.  
**Pode retornar dados insuficientes:** não.  
**Consumidores previstos:** Resumo, Simulados e Efetividade.  
**Observações:** pulos permanecem separados.

**NOME:** Taxa de acerto da sessão  
**Identificador técnico:** `session_accuracy_rate`  
**Descrição:** Percentual de respostas corretas na sessão.  
**Fonte dos dados:** `tentativas_questoes`.  
**Fórmula:** `session_correct_attempt_count / session_answered_attempt_count * 100`.  
**Unidade:** percentual.  
**Nível de agregação:** sessão.  
**Quantidade mínima de dados:** 1 resposta efetiva.  
**Pode retornar dados insuficientes:** sim.  
**Consumidores previstos:** Resumo, Histórico, Simulados e Efetividade.  
**Observações:** não usar objetivo como denominador.

**NOME:** Duração ativa da sessão  
**Identificador técnico:** `session_active_duration_seconds`  
**Descrição:** Tempo medido nos itens respondidos da sessão.  
**Fonte dos dados:** `tentativas_questoes.tempo_segundos`, com conferência de itens.  
**Fórmula:** soma de tempos válidos; publicar cobertura de medição.  
**Unidade:** segundos.  
**Nível de agregação:** sessão e soma por período.  
**Quantidade mínima de dados:** 100% das respostas efetivas temporizadas para valor completo.  
**Pode retornar dados insuficientes:** sim.  
**Consumidores previstos:** Sessão, Histórico, Ritmo e Efetividade.  
**Observações:** duração de parede é outra métrica.

**NOME:** Data da última sessão  
**Identificador técnico:** `last_question_session_at`  
**Descrição:** Início da sessão mais recente.  
**Fonte dos dados:** `sessoes_questoes.iniciado_em`.  
**Fórmula:** `MAX(iniciado_em)` com desempate por ID.  
**Unidade:** timestamp.  
**Nível de agregação:** tópico quando demonstrável, disciplina, perfil e global.  
**Quantidade mínima de dados:** 1 sessão.  
**Pode retornar dados insuficientes:** sim.  
**Consumidores previstos:** Dashboard, Histórico e Fila.  
**Observações:** para tópico, exige tentativa/item atribuível.

**NOME:** Dias estudados  
**Identificador técnico:** `study_day_count`  
**Descrição:** Datas civis distintas com atividade qualificável.  
**Fonte dos dados:** tentativas, foco persistido e revisões manuais qualificadas.  
**Fórmula:** cardinalidade da união das datas.  
**Unidade:** dias.  
**Nível de agregação:** tópico, disciplina, perfil, período e global.  
**Quantidade mínima de dados:** nenhuma; retorna 0.  
**Pode retornar dados insuficientes:** não, mas pode retornar `legacy_limited`.  
**Consumidores previstos:** Dashboard, Estatísticas, Evidência e Gamificação.  
**Observações:** eventos automáticos duplicados no mesmo dia não aumentam a contagem.

**NOME:** Último dia de estudo  
**Identificador técnico:** `last_study_date`  
**Descrição:** Data civil da atividade qualificável mais recente.  
**Fonte dos dados:** mesmas fontes de `study_day_count`.  
**Fórmula:** `MAX(data civil)`.  
**Unidade:** data.  
**Nível de agregação:** tópico, disciplina, perfil e global.  
**Quantidade mínima de dados:** 1 dia qualificável.  
**Pode retornar dados insuficientes:** sim.  
**Consumidores previstos:** Dashboard, Fila, Alertas e Progresso.  
**Observações:** não inferir foco não finalizado.

**NOME:** Frequência de estudo  
**Identificador técnico:** `study_frequency_days_per_week`  
**Descrição:** Ritmo médio de dias ativos por sete dias civis.  
**Fonte dos dados:** `study_day_count` e período.  
**Fórmula:** `study_day_count / calendar_day_count * 7`.  
**Unidade:** dias por semana.  
**Nível de agregação:** tópico, disciplina, perfil e global por período.  
**Quantidade mínima de dados:** intervalo de 7 dias.  
**Pode retornar dados insuficientes:** sim.  
**Consumidores previstos:** Dashboard, Estatísticas, Tendências e Gamificação.  
**Observações:** não mede intensidade.

### 14.3 Tópico, domínio, cobertura e tendência

**NOME:** Sessões distintas respondidas  
**Identificador técnico:** `distinct_answered_session_count`  
**Descrição:** Sessões distintas com ao menos uma resposta efetiva no escopo.  
**Fonte dos dados:** `tentativas_questoes.sessao_id`.  
**Fórmula:** `COUNT(DISTINCT sessao_id)` excluindo nulos.  
**Unidade:** sessões.  
**Nível de agregação:** questão, tópico, disciplina e perfil.  
**Quantidade mínima de dados:** nenhuma; retorna 0.  
**Pode retornar dados insuficientes:** não, mas legado sem sessão limita evidência.  
**Consumidores previstos:** Evidência, Consolidação, Estatísticas e Fila.  
**Observações:** não equivale ao total de sessões iniciadas.

**NOME:** Desempenho recente  
**Identificador técnico:** `recent_performance_rate`  
**Descrição:** Taxa de acerto nas até 15 respostas efetivas mais recentes.  
**Fonte dos dados:** `tentativas_questoes`.  
**Fórmula:** `accuracy_rate` na janela mais recente de tamanho máximo 15.  
**Unidade:** percentual.  
**Nível de agregação:** tópico, disciplina, perfil e global.  
**Quantidade mínima de dados:** 5 para exibição descritiva; 10 na análise de tendência.  
**Pode retornar dados insuficientes:** sim.  
**Consumidores previstos:** Fila, Tendências, Alertas, Domínio e Mapa.  
**Observações:** deve informar o tamanho da janela.

**NOME:** Tendência de desempenho  
**Identificador técnico:** `performance_trend`  
**Descrição:** Classificação de melhora, estabilidade ou queda entre duas janelas recentes.  
**Fonte dos dados:** `tentativas_questoes`.  
**Fórmula:** seção 10; delta de duas taxas recalculadas.  
**Unidade:** enumeração e pontos percentuais.  
**Nível de agregação:** tópico, disciplina, perfil e global.  
**Quantidade mínima de dados:** 10 tentativas em cada janela, 2 dias e 2 sessões no conjunto.  
**Pode retornar dados insuficientes:** sim.  
**Consumidores previstos:** Fila, Tendências, Alertas, Mapa e Consolidação.  
**Observações:** limiares são configuráveis e versionados.

**NOME:** Domínio atual  
**Identificador técnico:** `mastery_score`  
**Descrição:** Estimativa do grau atual de conhecimento demonstrado.  
**Fonte dos dados:** tentativas efetivas, dúvidas e histórico de resultados por questão.  
**Fórmula:** `mastery_score@1`, seção 7.2.  
**Unidade:** pontos de 0 a 100.  
**Nível de agregação:** tópico e, por recálculo bruto, disciplina, perfil e global.  
**Quantidade mínima de dados:** 3 tentativas e 2 questões únicas; resultado provisório enquanto evidência for Baixa.  
**Pode retornar dados insuficientes:** sim.  
**Consumidores previstos:** Dashboard, Estatísticas, Fila, Progresso, Tendências, Mapa e futura Gamificação.  
**Observações:** sempre apresentar junto de evidência e cobertura.

**NOME:** Nível de evidência  
**Identificador técnico:** `evidence_level`  
**Descrição:** Robustez observacional da estimativa de desempenho/domínio.  
**Fonte dos dados:** tentativas, questões únicas, sessões, dias, amplitude temporal e revisões qualificadas.  
**Fórmula:** cortes de `evidence_level@1`, seção 8.  
**Unidade:** `insufficient|low|moderate|high` e ordem 0–3.  
**Nível de agregação:** tópico e, por recálculo, disciplina, perfil e global.  
**Quantidade mínima de dados:** nenhuma; sem base retorna Insuficiente.  
**Pode retornar dados insuficientes:** a própria categoria expressa insuficiência.  
**Consumidores previstos:** todos os consumidores de Domínio, Tendências e Consolidação.  
**Observações:** não é nota de conhecimento.

**NOME:** Cobertura de questões  
**Identificador técnico:** `question_coverage_rate`  
**Descrição:** Fração do banco ativo do escopo já respondida ao menos uma vez.  
**Fonte dos dados:** `questoes`, associações ativas e `tentativas_questoes`.  
**Fórmula:** seção 9.1.  
**Unidade:** percentual.  
**Nível de agregação:** tópico, disciplina, perfil e global.  
**Quantidade mínima de dados:** 1 questão ativa disponível.  
**Pode retornar dados insuficientes:** sim.  
**Consumidores previstos:** Dashboard, Progresso, Estatísticas, Fila e Mapa.  
**Observações:** fotografia do catálogo atual.

**NOME:** Cobertura de tópicos  
**Identificador técnico:** `topic_coverage_rate`  
**Descrição:** Fração dos tópicos ativos com ao menos uma resposta efetiva.  
**Fonte dos dados:** tópicos/associações ativas e tentativas.  
**Fórmula:** seção 9.2.  
**Unidade:** percentual.  
**Nível de agregação:** disciplina, perfil e global.  
**Quantidade mínima de dados:** 1 tópico ativo.  
**Pode retornar dados insuficientes:** sim.  
**Consumidores previstos:** Dashboard, Progresso, Estatísticas e Mapa.  
**Observações:** não mede qualidade nem consolidação.

**NOME:** Estado de consolidação do tópico  
**Identificador técnico:** `topic_consolidation_status`  
**Descrição:** Indica se domínio robusto e estável foi demonstrado em ocasiões distintas.  
**Fonte dos dados:** domínio, evidência, sessões, revisões, tendência, erros e recência.  
**Fórmula:** regra configurável `topic_consolidation_status@1`, seção 11.  
**Unidade:** `consolidated|not_consolidated|insufficient_data`.  
**Nível de agregação:** tópico; níveis superiores usam contagem/proporção.  
**Quantidade mínima de dados:** todos os critérios da seção 11 avaliáveis.  
**Pode retornar dados insuficientes:** sim.  
**Consumidores previstos:** Progresso, Mapa, Alertas e futura Gamificação.  
**Observações:** não implementar recompensa nesta etapa.

### 14.4 Revisões

**NOME:** Revisões previstas  
**Identificador técnico:** `scheduled_review_count`  
**Descrição:** Agendas correntes cuja próxima data pertence ao período.  
**Fonte dos dados:** `controle_topico.proxima_revisao`.  
**Fórmula:** contagem de tópicos com data corrente dentro do intervalo.  
**Unidade:** agendas/tópicos.  
**Nível de agregação:** tópico, disciplina, perfil e período.  
**Quantidade mínima de dados:** nenhuma; retorna 0.  
**Pode retornar dados insuficientes:** não para estado corrente.  
**Consumidores previstos:** Dashboard, Revisões, Fila e Alertas.  
**Observações:** não reconstrói agenda histórica.

**NOME:** Revisões realizadas  
**Identificador técnico:** `completed_review_count`  
**Descrição:** Eventos de revisão efetivamente registrados e atribuíveis.  
**Fonte dos dados:** `revisoes` e futura linhagem/perfil.  
**Fórmula:** `COUNT(DISTINCT revisao_id)` qualificado.  
**Unidade:** revisões.  
**Nível de agregação:** tópico, disciplina, perfil, período e global.  
**Quantidade mínima de dados:** nenhuma; retorna 0 quando o escopo é demonstrável.  
**Pode retornar dados insuficientes:** sim no perfil legado.  
**Consumidores previstos:** Dashboard, Estatísticas, Progresso e Evidência.  
**Observações:** revisões iniciais agregadas são métrica legado separada.

**NOME:** Revisões atrasadas  
**Identificador técnico:** `overdue_review_count`  
**Descrição:** Agendas correntes vencidas antes da data de referência.  
**Fonte dos dados:** `controle_topico.proxima_revisao`.  
**Fórmula:** contagem onde `proxima_revisao < data(as_of)`.  
**Unidade:** agendas/tópicos.  
**Nível de agregação:** disciplina, perfil e global corrente.  
**Quantidade mínima de dados:** nenhuma; retorna 0.  
**Pode retornar dados insuficientes:** não.  
**Consumidores previstos:** Dashboard, Fila, Alertas e Revisões.  
**Observações:** mede atraso atual, não histórico de atrasos.

**NOME:** Data da última revisão  
**Identificador técnico:** `last_review_at`  
**Descrição:** Momento da revisão qualificável mais recente.  
**Fonte dos dados:** `revisoes.realizada_em`, com fallback legado explícito para `data`.  
**Fórmula:** máximo do timestamp/data.  
**Unidade:** timestamp ou data legado.  
**Nível de agregação:** tópico, disciplina, perfil e global.  
**Quantidade mínima de dados:** 1 revisão qualificável.  
**Pode retornar dados insuficientes:** sim.  
**Consumidores previstos:** Revisões, Fila, Progresso e Evidência.  
**Observações:** perfil precisa de identidade/linhagem.

**NOME:** Data da próxima revisão  
**Identificador técnico:** `next_review_date`  
**Descrição:** Próxima data corrente programada.  
**Fonte dos dados:** `controle_topico.proxima_revisao`.  
**Fórmula:** valor do tópico; em agregado, mínimo das datas válidas.  
**Unidade:** data.  
**Nível de agregação:** tópico, disciplina e perfil.  
**Quantidade mínima de dados:** 1 agenda.  
**Pode retornar dados insuficientes:** sim.  
**Consumidores previstos:** Dashboard, Fila, Alertas e Revisões.  
**Observações:** ausência de data não prova que a revisão não é necessária.

**NOME:** Resultado das revisões  
**Identificador técnico:** `review_accuracy_rate`  
**Descrição:** Taxa ponderada de acertos reportados em revisões qualificadas.  
**Fonte dos dados:** `revisoes.questoes` e `revisoes.acertos`.  
**Fórmula:** `SUM(acertos) / SUM(questoes) * 100`.  
**Unidade:** percentual.  
**Nível de agregação:** revisão, tópico, disciplina, perfil e período.  
**Quantidade mínima de dados:** soma de questões maior que zero.  
**Pode retornar dados insuficientes:** sim.  
**Consumidores previstos:** Revisões e relatórios específicos de revisão.  
**Observações:** não é `accuracy_rate` de tentativas e não deve alimentar domínio diretamente.

**NOME:** Número de revisões do tópico  
**Identificador técnico:** `topic_review_count`  
**Descrição:** Eventos de revisão qualificáveis do tópico.  
**Fonte dos dados:** `revisoes`.  
**Fórmula:** `COUNT(DISTINCT revisao_id)` por tópico.  
**Unidade:** revisões.  
**Nível de agregação:** tópico.  
**Quantidade mínima de dados:** nenhuma; retorna 0 quando o escopo é demonstrável.  
**Pode retornar dados insuficientes:** sim no perfil legado.  
**Consumidores previstos:** Evidência, Consolidação, Progresso e Revisões.  
**Observações:** `revisoes_iniciais` deve ser mostrado separadamente como legado.

## 15. Identificadores auxiliares reservados

Estes nomes também ficam reservados para impedir novos sinônimos:

| Identificador | Significado |
|---|---|
| `skipped_attempt_count` | pulos (`correta IS NULL`) |
| `session_wall_duration_seconds` | tempo entre início e fim da sessão |
| `timed_attempt_coverage_rate` | percentual das respostas com tempo válido |
| `latest_review_accuracy_rate` | percentual da revisão mais recente; legado qualificado |
| `legacy_initial_review_count` | contador importado sem eventos individuais |
| `legacy_review_progress_state` | estado antigo por número de revisões/último percentual |
| `legacy_domain_v2` | score atualmente implementado em `obter_indices_dominio_topicos` |
| `critical_open_error_count` | questões em erro crítico aberto |
| `recurring_open_error_count` | questões em erro recorrente aberto |
| `recovering_question_count` | questões em recuperação |
| `recovered_question_count` | questões recuperadas por sequência recente |
| `review_reported_question_count` | soma de `revisoes.questoes`, sem chamá-la de respostas reais |

## 16. Matriz dado bruto -> métrica -> consumidor

| Dado bruto | Métricas oficiais | Consumidores previstos |
|---|---|---|
| `tentativas_questoes` | respostas, únicos, acertos, erros, taxas, sequência, recente, tendência, domínio, evidência | todos os módulos acadêmicos |
| `sessoes_questoes` + tentativas/itens | sessões, conclusão, métricas por sessão, duração e telemetria | Sessão, Histórico, Simulados, Efetividade |
| catálogo ativo + associações | cobertura de questão/tópico e denominadores | Progresso, Dashboard, Fila, Mapa |
| `revisoes` com identidade/linhagem | revisões realizadas, resultados, última revisão, evidência | Revisões, Progresso e relatórios |
| `controle_topico.proxima_revisao` | previstas, atrasadas e próxima data | Dashboard, Fila e Alertas |
| `sessoes_foco` atribuíveis | dias estudados, duração e frequência | Dashboard, Histórico e Gamificação futura |
| métricas oficiais anteriores | consolidação | Progresso, Mapa, Alertas e Gamificação futura |

## 17. Parâmetros configuráveis e versionamento

Devem ser configuração do Núcleo, não números copiados em telas:

- tamanhos das janelas 50/15/30;
- pesos de `mastery_score@1`;
- degraus de recência e penalidade de dúvida;
- regras de erro crítico, recorrente e recuperação;
- cortes de evidência;
- delta de tendência (padrão 5 p.p.);
- limiares e requisitos de consolidação;
- timezone estatístico.

Alterar qualquer fórmula, janela, filtro ou limiar que possa mudar o valor exige nova `metric_version`. Alterar apenas arredondamento visual não muda a versão do cálculo.

## 18. Sequência de adoção sem grande refatoração

1. criar casos de referência para as métricas atuais, especialmente repetição de questão, pulo, recuperação e pouca evidência;
2. implementar um catálogo de identificadores e DTOs sem retirar consumidores antigos;
3. centralizar primeiro contagens, taxas, períodos e filtros, que têm menor risco;
4. corrigir identidade de perfil e linhagem N:N das revisões antes de certificar métricas de revisão por perfil;
5. comparar `legacy_domain_v2` e `mastery_score@1` lado a lado, sem alterar fila;
6. migrar Dashboard e Estatísticas para tentativas oficiais e nomes inequívocos;
7. migrar Progresso/Mapa para cobertura, domínio, evidência e consolidação separados;
8. fazer fila e recomendador consumirem as métricas oficiais; retirar o fallback somente com cobertura completa;
9. versionar e persistir eventos futuros de agenda e consolidação, sem fabricar histórico.

Até a implementação, este documento define o significado de destino e permite identificar toda divergência existente. Nenhum dado bruto deve ser reescrito para fazê-lo parecer compatível com a especificação.
