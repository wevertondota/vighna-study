# Relatório do Passo 7 — Progresso do Edital V2

Data: 18/09/2026

Versão: VighnaStudy 0.23.33 (`progresso-edital-v2`), schema 17.

## 1. Estado inicial

A aba Progresso misturava contagens de revisões, domínio legado, estados visuais
e previsões em `main.py`. O texto da disciplina descrevia cobertura como
histórico de revisão, a agregação por disciplina era manual e Dashboard e aba
recalculavam partes diferentes da apresentação.

## 2. Divergência documental da observação sombra e causa encontrada

A divergência não foi causada pelo gerador nativo de checkpoint. A inspeção
direta demonstrou que o commit `1b6e13b` e os checkpoints nativos do Passo 6 de
13:12:13 e 13:17:34 contêm exatamente 1 execução, 6 itens e 15 fallbacks sombra.

Depois do checkpoint, o `estudos.db` do workspace foi substituído por uma cópia
anterior ao schema sombra, com 1.142.784 bytes e sem as três tabelas. O banco da
distribuição era outra cópia: possuía as tabelas, mas com zero linhas. Portanto,
a leitura de zero veio de um banco substituído/independente, não do snapshot
SQLite incluído pelo `checkpoint.py`.

O banco atual foi preservado em
`backups/estudos_2026-09-18_13-54-43_antes_passo7_progresso_v2.db` e migrado de
forma idempotente. Nenhuma observação foi recriada. A coleta real reinicia em
zero no estado atual.

## 3. Arquitetura do snapshot de progresso

Foi criado `SyllabusProgressSnapshot` em `progresso_edital.py`. Ele reúne, sob
demanda, concurso, totais, coberturas, distribuição de evidência, consolidação,
domínio global, disciplinas, tópicos, lacunas, versão e instante de geração.
Não foi criada tabela histórica. Dashboard e aba Progresso usam o mesmo snapshot
em cache curto por concurso.

## 4. Definição de cobertura usada

Cobertura passou a significar exclusivamente as métricas oficiais do Núcleo
Estatístico baseadas em tentativas efetivas. Revisões não são usadas como
sinônimo de cobertura.

## 5. Cobertura de tópicos

`topic_coverage_rate@1` representa tópicos ativos que possuem ao menos uma
tentativa efetiva. No banco real atual: 1 de 88 tópicos, ou aproximadamente
1,14%.

## 6. Cobertura de questões

`question_coverage_rate@1` é exibida separadamente e mede questões ativas já
respondidas ao menos uma vez. No banco real atual: aproximadamente 52,12%.
Quantidade de questões não é usada como peso curricular de tópico.

## 7. Evidência

A aba mostra evidência Insuficiente, Baixa, Moderada e Alta. A métrica de
apresentação “Evidência suficiente” conta somente Moderada ou Alta. No banco
real: 87 tópicos insuficientes, 1 baixo, 0 moderados e 0 altos; portanto 0%
possui evidência suficiente para decisões fortes.

## 8. Consolidação

Somente `topic_consolidation_status@1 == consolidated` produz o estado
“Consolidado”. `insufficient_data` é preservado e nunca convertido em
`not_consolidated`. O banco real possui 0 tópicos oficialmente consolidados.

## 9. Domínio

Domínio global, de disciplina e de tópico vem diretamente de `mastery_score@1`.
Não há média simples de domínios. Valores `None` aparecem como “Dados
insuficientes”, nunca como zero. Evidência baixa sinaliza domínio provisório.

## 10. Regra de “Em consolidação”

A regra visual recebeu o identificador estável
`presentation_consolidating_v1`: tópico iniciado, evidência moderada/alta,
domínio oficial pelo menos 70 e consolidação oficial ainda não atingida. Ela é
explicitamente informativa e não substitui `topic_consolidation_status@1`.

## 11. Agregação por disciplina

Coberturas e domínio usam o escopo de disciplina do `StatisticsService`.
Distribuições de evidência e consolidação são contagens dos estados oficiais por
tópico. Disciplinas com volumes muito diferentes não são combinadas por média
simples.

## 12. Mudanças no Dashboard

O card compacto mantém a cobertura principal e agora destaca cobertura de
questões, evidência suficiente, consolidados e domínio oficial. O acesso “Ver
progresso” e a identidade visual foram preservados. O card consome o mesmo
snapshot da aba.

## 13. Mudanças na aba Progresso

Os indicadores superiores agora separam Cobertura do edital, Evidência
suficiente, Consolidados, Cobertura de questões e Domínio oficial. A tabela de
disciplinas mostra as duas coberturas, evidência suficiente, consolidados e
domínio. A tabela de tópicos mostra Disciplina, Tópico, Estado, Cobertura de
questões, Evidência, Domínio, Revisões e Próxima revisão.

## 14. Filtros

Foram preservados busca textual, disciplina e estado, com adição do filtro por
evidência: insuficiente, baixa, moderada e alta. A ordenação padrão do snapshot
é curricular, Disciplina → Tópico, e não reutiliza a ordem da fila.

## 15. Tratamento de dados insuficientes

Domínio ausente, cobertura sem questões ativas, consolidação não certificável e
previsão sem base usam estados explícitos. Não são mostrados como zero, queda,
estabilidade ou data estimada. Evidência baixa permanece provisória.

## 16. Auditoria das previsões

As fórmulas foram extraídas da UI para uma função pura. O início de tópico usa
a primeira tentativa efetiva com `concurso_id` confirmado. Não existe histórico
versionado capaz de datar retrospectivamente
`topic_consolidation_status@1`; por isso nenhum evento de consolidação é
inventado e a previsão real de consolidação permanece indisponível.

## 17. Critérios mínimos de previsão

Uma janela precisa ter ao menos 4 eventos, 3 dias distintos e amplitude mínima
de 7 dias. A interface informa janela, eventos, dias, período observado e o
caráter de extrapolação. Com 1 evento de início em 1 dia e 0 eventos oficiais de
consolidação, o banco real mostra “Dados insuficientes para previsão”.

## 18. Lacunas do edital

Foi adicionada visão compacta e objetiva para: não iniciado, iniciado com
evidência insuficiente, evidência baixa, evidência suficiente ainda não
consolidada e revisão vencida. No estado real: 87 não iniciados, 0 iniciados
insuficientes, 1 com evidência baixa, 0 suficientes não consolidados e 3
revisões vencidas. Essa visão é analítica e não prioriza conteúdo.

## 19. Performance e consultas

O snapshot usa `get_topic_metrics_batch`, `get_subject_metrics_batch` e
`get_global_metrics`; não executa consulta por tópico. A medição real processou
88 tópicos e 6 disciplinas com 16 SELECTs, quantidade aproximadamente constante
em relação ao número de tópicos.

## 20. Testes

Foram adicionados 17 testes cobrindo integralmente a matriz A–Q: edital vazio,
um evento, quatro níveis de evidência, consolidação oficial, insuficiência,
volumes distintos, duas coberturas, domínio `None`, previsões, tópicos sem
questões, universo ativo, snapshot compartilhado e ausência de N+1. A suíte
unificada contém 93 testes e foi aprovada, além do smoke test da versão 0.23.33.

## 21. Status da fila sombra

A V3 continua como única fila decisória. A candidata permanece sombra,
`used_for_queue_order = false`, e a telemetria continua separada do histórico
acadêmico. Nenhuma alteração de Progresso consome score ou posição candidata.

## 22. Status atual do gate

`ready = false`, classificação
`INFRAESTRUTURA PRONTA / AMOSTRA AINDA INSUFICIENTE`. Existem 0 observações, 0
dias, 0 tópicos observados e 0 itens moderados/altos. Os limiares continuam 20
observações, 5 dias, 5 tópicos e 10 itens moderados/altos. A integridade de
linhagem está verdadeira e nenhuma observação foi fabricada.

## 23. Pendências

É necessário acumular uso real para o gate sombra e para previsões temporais.
Uma série histórica versionada de consolidação poderá permitir previsão desse
estado em etapa futura. As mudanças de distribuição existentes no workspace
permanecem independentes desta implementação.

## 24. Recomendação para o próximo passo

Coletar dados reais sem alterar a V3, observar a evolução das quatro dimensões e
avaliar futuramente uma série temporal de progresso. Não reduzir o progresso a
um percentual único e não liberar a fila candidata enquanto o gate estiver
fechado.
