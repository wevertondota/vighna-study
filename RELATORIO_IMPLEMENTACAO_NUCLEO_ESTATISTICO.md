# Relatório de Implementação do Núcleo Estatístico Central

**Data:** 18/09/2026  
**Contrato implementado:** `mastery_score@1`, `evidence_level@1` e métricas fundamentais da `ESPECIFICACAO_TECNICA_NUCLEO_ESTATISTICO.md`  
**Resultado:** existe uma fonte central, versionada e testada para as principais métricas do VighnaStudy.

Observação de rastreabilidade: o passo de implementação cita `ESPECIFICACAO_METRICAS_VIGHNA.md`, arquivo que não está presente nesta pasta. A `ESPECIFICACAO_TECNICA_NUCLEO_ESTATISTICO.md` declara-se normativa, contém integralmente definições, fórmulas, mínimos, agregações, estados e dicionário técnico, e foi usada como contrato de implementação. Nenhuma fórmula foi inventada para suprir uma lacuna documental.

## 1. Arquitetura criada

A cadeia implementada é:

```text
SQLite (eventos brutos e catálogo atual)
    -> MetricsRepository (leituras normalizadas e em lote)
    -> StatisticsService (fórmulas oficiais versionadas)
    -> MetricResult / ScopeMetrics (DTOs consistentes)
    -> adaptadores de compatibilidade em banco.py
    -> Dashboard / Estatísticas / comparação da fila
```

O núcleo é somente leitura. Ele não reescreve tentativas, revisões, sessões, snapshots nem catálogo. Cada `MetricResult` informa `metric_id`, `metric_version`, escopo por IDs, período semiaberto, timezone, instante de cálculo, estado, denominador, parâmetros, avisos e requisitos ausentes.

Os períodos oficiais ficam em uma unidade separada e reutilizável: hoje, últimos 7 dias, últimos 30 dias, período anterior equivalente, histórico completo e intervalo customizado. O identificador normativo é `America/Sao_Paulo`. Em instalações Windows sem base IANA, há fallback UTC−03:00, mantido explicitamente como limitação de ambiente.

## 2. Arquivos adicionados

- `statistics_core/__init__.py`: API pública do pacote.
- `statistics_core/models.py`: DTOs `MetricResult` e `ScopeMetrics`.
- `statistics_core/periods.py`: períodos civis oficiais semiabertos.
- `statistics_core/repository.py`: repositório normalizado e consultas em lote.
- `statistics_core/service.py`: serviço e fórmulas centrais.
- `test_statistics_core.py`: 17 testes unitários/de integração SQLite do núcleo.
- `RELATORIO_IMPLEMENTACAO_NUCLEO_ESTATISTICO.md`: este relatório.

## 3. Arquivos alterados

- `banco.py`: fachadas do núcleo, migração inicial de consumidores e comparação lado a lado na fila.
- `main.py`: cards acadêmicos do Dashboard e resumo geral de Estatísticas passam a consumir o núcleo.
- `checkpoint.py`: passa a inventariar, proteger e restaurar o pacote `statistics_core` completo.
- `testar_vighna.bat`: compila os novos módulos e executa a suíte específica antes do smoke test.

O núcleo não introduziu migração nem escrita de métricas no `estudos.db`. A validação de inicialização normal consolidou o estado físico SQLite/WAL no arquivo principal, sem apagar ou reconstruir histórico. Não houve mudança no importador, nos pesos, nos critérios ou na ordenação da fila.

## 4. Métricas implementadas

- `answered_attempt_count`;
- `correct_attempt_count`;
- `incorrect_attempt_count`;
- `accuracy_rate` e `error_rate`;
- `answered_unique_question_count`;
- `question_attempt_count`, `last_attempt_at`, `last_attempt_result` e `recent_result_sequence`;
- `question_session_count` e `distinct_answered_session_count`;
- `last_activity_at`;
- `completed_review_count` e `last_review_at`, com limitação legada explícita;
- `recent_performance_rate` e `performance_trend`;
- `question_coverage_rate` e `topic_coverage_rate`;
- `evidence_level`;
- `mastery_score` e estimativa diagnóstica quando o valor público é insuficiente.

APIs públicas principais:

- `get_topic_metrics` e `get_topic_metrics_batch`;
- `get_subject_metrics` e `get_subject_metrics_batch`;
- `get_global_metrics`;
- `get_period_metrics`;
- `get_question_metrics`;
- `get_recent_performance`;
- `get_mastery_score`;
- `get_evidence_level`;
- `get_coverage`.

## 5. Fórmulas utilizadas

Contagens e taxas usam somente tentativas efetivas (`correta IN (0, 1)`). Questão histórica é identificada por `COALESCE(questao_id_snapshot, questao_id)`; tópico e disciplina usam primeiro os IDs de snapshot.

```text
accuracy_rate = correct_attempt_count / answered_attempt_count * 100
error_rate = incorrect_attempt_count / answered_attempt_count * 100

question_coverage_rate = questões ativas respondidas / questões ativas disponíveis * 100
topic_coverage_rate = tópicos ativos respondidos / tópicos ativos * 100
```

O desempenho recente usa até 15 tentativas. A tendência compara janelas consecutivas 1–15 e 16–30, exigindo ao menos 10 elementos em cada janela, duas datas e duas sessões comprováveis. Delta de ±5 p.p. classifica melhora/queda; o intervalo interno é estabilidade.

```text
current_performance =
    accuracy(last 50), se N <= 15
    0,65 * accuracy(last 15) + 0,35 * accuracy(last 50), se N > 15

mastery_raw =
    0,55 * current_performance
  + 0,25 * error_control
  + 0,15 * temporal_stability
  + 0,05 * recency
  - doubt_penalty
```

Cobertura e evidência não entram no domínio. Evidência usa os cortes normativos por tentativas, questões únicas, sessões, dias, amplitude e revisões qualificadas. Domínio público retorna `insufficient_data` quando `N < 3` ou `U < 2`; a estimativa fica disponível apenas nos parâmetros diagnósticos. Evidência Baixa recebe aviso de valor provisório.

Disciplina, perfil e global são recalculados sobre a união dos eventos brutos. Não há média de percentuais, média de tópicos ou média de disciplinas.

## 6. Consultas criadas

O repositório possui consultas centralizadas para:

1. tentativas efetivas normalizadas por snapshots e IDs;
2. catálogo atual de questões ativas, com disciplina e tópico incluídos/não pausados;
3. tópicos ativos;
4. revisões com análise de linhagem por `tentativas_questoes.revisao_id`;
5. sessões de questões por perfil e período.

As APIs em lote carregam tentativas, catálogo, tópicos e revisões uma vez e particionam os eventos em memória por ID. A tela de disciplinas usa cinco consultas totais (uma de metadados e quatro do lote), em vez de abrir consultas repetidas para cada disciplina. Não foi criado cache persistente.

## 7. Consumidores já migrados

- **Dashboard:** os cards de respostas, erros, desempenho e tópicos trabalhados usam `get_global_metrics`.
- **Estatísticas — Disciplinas:** taxa e volume vêm de tentativas oficiais; a taxa geral é recalculada dos eventos globais, não pela média das disciplinas.
- **Estatísticas — Pontos fracos:** ranking usa `mastery_score` e exclui “insuficiente” da classificação de fraqueza. Tópicos sem evidência permanecem não avaliados, em vez de serem tratados como nota zero.
- **Fila Inteligente:** somente modo de comparação. Cada item recebe domínio, acurácia, cobertura, desempenho recente e evidência do núcleo com `used_for_queue_order = false`.

## 8. Consumidores ainda não migrados

- score, pesos, critérios, fallback e ordem final da Fila Inteligente;
- demais cards legados do Dashboard baseados em revisões;
- abas Tendências e Revisões recentes, que continuam explicitamente baseadas em `revisoes`;
- Progresso e seus estados legados por quantidade de revisões;
- Minha Evolução/Histórico nas partes que ainda usam Domínio V2 ou snapshots observados;
- alertas, previsão de edital, recomendador, efetividade, simulados e futuras funcionalidades.

Essa permanência é intencional: resultados antigos e novos devem ser observados antes da migração de consumidores críticos.

## 9. Diferenças encontradas entre cálculos antigos e novos

Comparação no banco real do perfil ativo em 18/09/2026:

| Métrica | Comparáveis | Diferentes | Resultado observado |
|---|---:|---:|---|
| domínio | 1 | 1 | núcleo 3,3264 p.p. abaixo do `legacy_domain_v2` |
| taxa acumulada | 1 | 1 | núcleo 2,6992 p.p. abaixo da janela-base legada |
| cobertura | 4 | 0 | paridade nos casos comparáveis |
| desempenho recente | 1 | 0 | paridade no caso comparável |
| revisões | 94 | 3 | núcleo exclui uma revisão não atribuível em três tópicos afetados |

Origem das diferenças:

- `mastery_score@1` não mistura cobertura/evidência com conhecimento e não aplica os tetos do V2 ao score;
- `accuracy_rate` oficial usa todo o período selecionado, enquanto `desempenho_base` legado usa janela de até 50;
- revisões sem perfil/linhagem inequívoca retornam `legacy_limited` e são excluídas da contagem certificada por perfil;
- o universo do núcleo possui 94 tópicos ativos; o Domínio V2 legado retornou 100 porque ainda inclui seis tópicos pausados.

Distribuição atual de evidência nos 94 tópicos ativos: 93 `insufficient`, 1 `low`, 0 `moderate`, 0 `high`. Isso não é convertido em desempenho zero.

## 10. Tratamento de dados históricos

- nenhuma tentativa, sessão, revisão, snapshot ou efetividade foi alterada;
- eventos são agrupados por IDs estáveis, não por nomes;
- tentativas repetidas permanecem eventos separados, enquanto questões únicas são deduplicadas;
- timestamps legados sem offset são lidos como horário local e sinalizados por `legacy_local_time`;
- sessões nulas não são inventadas e geram aviso de cobertura legada;
- revisão sem linhagem de perfil não é compartilhada silenciosamente;
- foco sem `concurso_id` não é atribuído a métricas acadêmicas certificadas por perfil;
- não houve migração de banco nem reconstrução retroativa.

## 11. Tratamento de questões arquivadas/excluídas

Desempenho usa snapshots históricos e preserva a tentativa mesmo quando a questão é arquivada, enviada à lixeira ou removida definitivamente. O teste remove fisicamente a linha de `questoes` após a tentativa e confirma que resposta, acerto e questão única continuam presentes.

Cobertura é deliberadamente uma fotografia do catálogo atual: questões inativas/excluídas saem do denominador e do numerador ativo. O payload inclui `current_catalog_snapshot`. O sistema ainda não possui denominador histórico suficiente para reconstruir cobertura passada; essa limitação não é mascarada.

## 12. Testes criados

A suíte `test_statistics_core.py` cobre:

- A–C: ausência de tentativa, única correta e única incorreta;
- D–F: repetição, múltiplas questões e múltiplas sessões;
- G–H: 100% com evidência insuficiente e desempenho alto com evidência alta;
- I–J: queda recente e recuperação após erros;
- K: histórico preservado após arquivo/exclusão definitiva;
- L–M: vários tópicos/disciplinas e agregação ponderada por eventos;
- N: períodos oficiais de 7 e 30 dias e anterior equivalente;
- O: histórico insuficiente/legado;
- API por questão e metadados consistentes;
- revisão sem perfil retornando `legacy_limited`.

O smoke test existente continua cobrindo banco, importação, sessões, revisões, Central de Questões, perfis, fila, foco, simulados, checkpoint e demais integrações do projeto.

## 13. Resultado dos testes

- `python -m unittest -v test_statistics_core`: **17 testes, OK**.
- `QT_QPA_PLATFORM=offscreen python testes_smoke.py`: **VighnaStudy 0.23.31: testes smoke OK**.
- `python -m py_compile ...`: **OK** para aplicação, núcleo, checkpoint e testes.
- `ruff check statistics_core test_statistics_core.py`: **All checks passed**.
- `git diff --check`: **OK**; apenas avisos informativos de conversão LF/CRLF do Git.
- `PRAGMA integrity_check`: **ok**.
- `PRAGMA foreign_key_check`: **0 violações**.
- inicialização `QT_QPA_PLATFORM=offscreen` por 8 segundos: aplicação permaneceu ativa sem exceção e foi encerrada somente pelo timeout esperado.
- checkpoint completo: manifesto/hashes válidos, 68 arquivos protegidos e snapshot SQLite incluído; a auditoria retornou `completo = true`.

A varredura Ruff ampla dos monólitos encontrou 465 ocorrências preexistentes e sem configuração de baseline. Elas não foram alteradas fora do escopo; os arquivos novos estão limpos.

## 14. Riscos ou pendências

1. `revisoes` ainda não possui `concurso_id`; dados sem linhagem ficam `legacy_limited`.
2. `sessoes_foco` não possui perfil e não pode compor métricas oficiais por concurso.
3. o catálogo histórico não preserva denominadores de cobertura passados.
4. muitos tópicos atuais não têm evidência mínima; a interface precisa preservar “não avaliado”.
5. a fila ainda usa Domínio V2 por decisão de segurança; retirar o legado agora mudaria comportamento.
6. Progresso, Tendências e partes do Dashboard ainda têm semântica legada de revisão.
7. o fallback UTC−03:00 cobre os dados brasileiros atuais, mas instalar `tzdata` será necessário se o produto precisar interpretar corretamente períodos históricos sujeitos a horário de verão.
8. `ESPECIFICACAO_METRICAS_VIGHNA.md` não existe nesta cópia; convém renomear ou criar um apontador formal para a especificação técnica normativa.

## 15. Próxima etapa recomendada

1. adicionar identidade explícita de perfil e linhagem N:N às revisões futuras, com migração não destrutiva;
2. observar comparações do núcleo contra V2 em uma base com mais tópicos avaliáveis;
3. migrar Progresso para domínio, cobertura, evidência e consolidação separados;
4. migrar Tendências de desempenho para tentativas, mantendo tendências de revisão com nome próprio;
5. migrar fila e recomendador somente após testes de paridade da ordem e decisão explícita sobre as diferenças;
6. versionar qualquer alteração posterior de pesos, janelas, filtros ou limiares.

Regra preservada: a fonte central existe e está testada, mas a adoção não foi forçada em todos os consumidores. A migração deve permanecer progressiva e segura.
