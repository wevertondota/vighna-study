# Relatório de Validação do Núcleo Estatístico

Data: 18/09/2026  
Contrato validado: `metric_version = 1`  
Etapa: Passo 4 — validação e migração controlada

> Nota documental: `ESPECIFICACAO_METRICAS_VIGHNA.md`, citado pelo roteiro, não existe no repositório. A especificação normativa encontrada e usada integralmente foi `ESPECIFICACAO_TECNICA_NUCLEO_ESTATISTICO.md` (versão 1.0), além de `RELATORIO_AUDITORIA_NUCLEO_ESTATISTICO.md` e `RELATORIO_IMPLEMENTACAO_NUCLEO_ESTATISTICO.md`.

## 1. Estado inicial encontrado

O Passo 3 havia criado `statistics_core`, com modelos versionados, períodos semiabertos, repositório SQLite e serviço para questão, tópico, disciplina, perfil e período. Dashboard, Disciplinas e Pontos fracos já consumiam parte do núcleo. Progresso ainda recalculava estados com revisões e percentual legado; Histórico ainda usava média simples dos domínios dos tópicos; a fila apenas recebia a comparação lado a lado e continuava ordenada pelo algoritmo legado.

Existiam 17 testes centrais. As limitações documentadas eram: revisões sem `concurso_id`, foco sem atribuição inequívoca ao perfil, datas locais legadas e cobertura baseada no catálogo corrente.

## 2. Métricas auditadas

Foram auditadas as contagens de tentativas, acertos, erros e questões únicas; taxas de acerto/erro; sessões com resposta e sessões totais; revisões qualificadas; última atividade; dias estudados; desempenho recente e tendência; cobertura de questões/tópicos; evidência; domínio; controle de erros; consolidação e agregações por disciplina/perfil.

Os nomes pedidos no roteiro foram mapeados aos IDs oficiais: `total_attempts` → `answered_attempt_count`, `correct_attempts` → `correct_attempt_count`, `incorrect_attempts` → `incorrect_attempt_count`, `unique_questions_answered` → `answered_unique_question_count`, `session_count` → `distinct_answered_session_count`, `review_count` → `completed_review_count`, `coverage_rate` → `question_coverage_rate` e `recent_performance` → `recent_performance_rate`/`performance_trend`.

## 3. Matriz de validação

Fixture determinística: tópico com 12 questões ativas; quatro tentativas (`erro A`, `erro B`, `acerto A`, `acerto B`) em duas sessões; uma revisão qualificada ligada à última tentativa. `T0` representa o timestamp mais recente da fixture.

| Métrica pedida | Entrada relevante | Esperado | Produzido | Status | Origem |
|---|---|---:|---:|---|---|
| `total_attempts` | 4 respostas efetivas | 4 | 4 | OK | eventos brutos |
| `correct_attempts` | 2 corretas | 2 | 2 | OK | eventos brutos |
| `incorrect_attempts` | 2 incorretas | 2 | 2 | OK | eventos brutos |
| `unique_questions_answered` | A e B repetidas | 2 | 2 | OK | `DISTINCT question_ref` |
| `accuracy_rate` | 2/4 | 50% | 50% | OK | razão de eventos |
| `session_count` | sessões 1 e 2 | 2 | 2 | OK | sessões distintas com resposta |
| `review_count` | 1 revisão atribuível | 1 | 1 | OK | linhagem comprovada |
| `mastery_score` | desempenho 50%; erro, estabilidade e recência oficiais | 60,8125 | 60,8125 | OK | fórmula `mastery_score@1` |
| `evidence_level` | N=4, U=2, S=2 | `low` | `low` | OK | cortes cumulativos |
| `coverage_rate` | 2/12 | 16,6667% | 16,6667% | OK | catálogo ativo |
| `recent_performance` | 4 tentativas, abaixo do mínimo descritivo | `insufficient_data`, estimativa 50% | igual | OK | janela recente |
| `last_activity_at` | tentativa/revisão em T0 | T0 | T0 | OK | máximo dos eventos |

Não houve divergência na matriz final.

## 4. Cenários controlados executados

- A: zero dados retorna contagens zero e taxas/domínio/tendência como `insufficient_data`.
- B e C: uma resposta correta ou incorreta produz taxa correta, sem promover o domínio público.
- D: quatro tentativas da mesma questão resultam em 4 tentativas, 1 questão única, 2 acertos, 2 erros e último resultado correto; tendência permanece insuficiente.
- E e F: várias questões e sessões validam contagens, cobertura, atividade, evidência e domínio.
- G: oito acertos na mesma questão mantêm evidência insuficiente e `mastery_score` público indefinido, apesar de estimativa alta.
- H: 40 tentativas, 10 questões, cinco sessões/dias e duas revisões atingem evidência alta.
- I e J: queda recente e recuperação posterior são reconhecidas.
- K, L e M: arquivar, enviar à lixeira e restaurar preservam o histórico; restauração não duplica eventos.
- N: 1 tentativa a 100% mais 99 tentativas a aproximadamente 50% produzem 51%, nunca 75%.
- O: hoje, limites exatos de 7/30 dias, período anterior adjacente e eventos fora da janela foram validados.
- Casos adicionais: exclusão permanente com snapshots, sessão vazia, erros críticos consecutivos, cobertura por erro, repetição sem inflar cobertura, tópico sem questões e revisão legada sem linhagem.

## 5. Divergências encontradas

1. A recência usava a data de `period.end_exclusive`, isto é, o primeiro instante fora do período. Isso deslocava a idade em um dia.
2. O controle de erros interrompia a leitura no primeiro erro recente e nunca contabilizava corretamente três erros consecutivos iniciais.
3. Progresso misturava revisões, último percentual e domínio legado; Histórico calculava domínio agregado pela média simples de scores de tópicos.
4. O Dashboard ainda possuía consultas redundantes para somar questões/revisões manuais e tirar média de percentuais recentes.
5. A visão Histórico acionava um N+1 do caderno de erros (uma consulta por questão errada).

## 6. Correções realizadas

- Recência passou a usar o último microssegundo incluído no intervalo semiaberto.
- A sequência inicial de erros/acertos agora é percorrida até a primeira mudança de resultado.
- Foram publicados `critical_open_error_count`, `study_day_count`, `last_study_date` e `topic_consolidation_status` com estados e avisos explícitos.
- `mastery_score` passou a informar também a faixa descritiva oficial; sem evidência, a faixa é `Dados insuficientes`.
- Progresso e Histórico passaram a consumir lotes oficiais. A data de última revisão foi normalizada somente para apresentação.
- O N+1 do caderno de erros foi substituído pelos componentes de controle de erros já calculados no lote oficial.

Cada um dos dois bugs de fórmula recebeu teste que falharia antes da correção.

## 7. Consumidores migrados

- Dashboard: tentativas, erros, taxa de acerto, revisões qualificadas, cobertura de tópicos, domínio, períodos diário/semanal e comparação recente.
- Estatísticas/Disciplinas: contagens e taxa recalculadas pelo lote de disciplinas.
- Estatísticas/Pontos fracos: domínio oficial com evidência ao menos baixa; uma única resposta não entra no ranking.
- Estatísticas/Progresso: cobertura, domínio, evidência e consolidação independentes.
- Estatísticas/Histórico: domínio atual global, por disciplina e por tópico via núcleo; a série temporal descritiva continua nos eventos brutos porque o contrato não fornece série diária pronta.

As abas Algoritmo, Revisões recentes e Tendências foram auditadas e preservadas: Algoritmo pertence ao decisor/fila; Revisões recentes mostra eventos de revisão explicitamente rotulados; Tendências mantém a representação existente quando não há base oficial suficiente para substituição integral.

## 8. Cálculos duplicados removidos

- helper de UI `classificar_progresso_topico`;
- média simples de domínio no Histórico;
- estado de consolidação por `revisões >= 4` e percentual;
- consultas do Dashboard que somavam `revisoes.questoes`, contavam revisões e calculavam `AVG` dos percentuais por tópico;
- cálculos por tópico/disciplina repetidos na tela Progresso;
- consulta N+1 ao caderno de erros no Histórico;
- variável SQL obsoleta deixada no ranking de pontos fracos.

As remoções foram precedidas por busca global de referências.

## 9. Cálculos ainda existentes fora do núcleo

- Domínio V2, pesos e componentes da Fila Inteligente V3, usados pela fila e por snapshots de efetividade.
- Relatório estratégico legado (`obter_relatorio_estrategico`) ainda usa Domínio V2 e médias antigas; não pertence aos quatro consumidores prioritários desta etapa.
- Séries diárias, foco e telemetria de sessão permanecem nos módulos especializados. Foco por perfil não pode ser oficializado sem identidade de perfil.
- Agenda (`proxima_revisao`, atrasadas/hoje) continua em `controle_topico`; é estado operacional, não taxa acadêmica.
- Revisões recentes e tendência de revisões permanecem como tal, sem serem renomeadas para desempenho acadêmico.

## 10. Resultado da validação de domínio

A fórmula confere com o contrato: `0,55*performance + 0,25*error_control + 0,15*temporal_stability + 0,05*recency - doubt_penalty`, limitada a 0–100. As janelas 50/15, neutralidade temporal com poucos dias e faixas descritivas foram verificadas. Cobertura e evidência não entram no score. Evidência insuficiente conserva apenas a estimativa diagnóstica e retorna `mastery_score = null`.

## 11. Resultado da validação de evidência

Os cortes N/U/S/D/T/R foram validados nos níveis insuficiente, baixa, moderada e alta. Foram aprovadas as combinações domínio alto + evidência insuficiente, domínio baixo + evidência alta, domínio médio + evidência alta e domínio indefinido + evidência insuficiente. Assim, evidência não é sinônimo nem teto aritmético de domínio.

## 12. Resultado da validação de cobertura

Uma resposta incorreta conta como exposição; repetir a mesma questão não aumenta questões únicas; sem questões ativas a cobertura é `insufficient_data`. Tentativas de itens arquivados/lixeira permanecem no histórico, mas saem do denominador e do numerador da fotografia do catálogo ativo, conforme contrato.

## 13. Resultado da validação de desempenho recente

As janelas não sobrepostas 1–15 e 16–30, mínimo de 10 tentativas por janela, dois dias e duas sessões foram testadas. Deltas de pelo menos +5 p.p. indicam melhora, no máximo -5 p.p. indicam queda e o intervalo interno indica estabilidade. Uma amostra isolada retorna dados insuficientes.

## 14. Resultado das agregações

Disciplina, perfil e global são recalculados da união de eventos, sem média simples. O caso 1×100% + 99×aproximadamente 50% produziu 51%. Questões únicas e dias são uniões, e domínio/evidência são reaplicados aos eventos do escopo.

## 15. Resultado dos períodos temporais

Os intervalos são semiabertos no timezone `America/Sao_Paulo`: hoje; últimos 7 dias (hoje e seis datas anteriores); últimos 30 dias; e anterior equivalente, adjacente. Eventos nos dias 0/6 entram em 7 dias, 7/13 entram no anterior equivalente, 29 entra em 30 dias e 30 fica fora. A correção de recência removeu o deslocamento do fim exclusivo.

## 16. Resultado dos testes de dados insuficientes

Contagens retornam zero. Taxas, cobertura sem denominador, tendência, domínio e consolidação retornam estado explícito, valor nulo ou enumeração `insufficient_data`, com `missing_requirements`. A interface de Progresso exibe travessão e “Dados insuficientes”, não 0% de domínio. Revisões sem linhagem ficam `legacy_limited` e são excluídas das estatísticas por perfil.

## 17. Impacto de arquivamento/lixeira/restauração

O histórico usa snapshots e sobrevive a arquivamento, lixeira e exclusão permanente. Restaurar não cria nova tentativa. A cobertura muda apenas porque é uma fotografia do catálogo ativo: 12 questões antes, 11 durante arquivamento/lixeira e 12 após restauração.

## 18. Comparação da fila inteligente

Perfil real ativo: concurso 40.

| Posição | Antes (tópico, score) | Atual (tópico, score) |
|---:|---|---|
| 1 | 27, 67,0 | 27, 67,0 |
| 2 | 51, 57,8 | 51, 57,8 |
| 3 | 74, 43,0 | 74, 43,0 |
| 4 | 23, 24,4 | 23, 24,4 |

Resultado: ordem e scores idênticos. `comparacao_nucleo_estatistico.used_for_queue_order` permaneceu `False` em todos os itens. Pesos, critérios, bônus, penalizações, espaçamento e regra de queda não foram alterados.

## 19. Performance/consultas

Contagem de comandos `SELECT` no banco real, sem cache persistente:

| Fluxo | SELECTs | Observação |
|---|---:|---|
| métrica global | 5 | constante |
| lote central de tópicos | 4 | constante para 1 ou N tópicos |
| adaptador de Progresso (94 tópicos) | 5 | 1 metadados + lote de 4 |
| Dashboard, incluindo carga global | 8 | 5 núcleo + 3 agenda |
| Estatísticas/Disciplinas | 7 | constante, sem consulta por disciplina |
| Histórico central | 16 | era 63 antes da remoção do N+1 |
| Histórico expandido | 28 | era 75 antes da remoção do N+1 |

Não foi introduzido cache persistente. Os lotes carregam tentativas, catálogo, tópicos e revisões uma vez e particionam em memória.

## 20. Testes automatizados executados

- `python -m unittest -v test_statistics_core.py`: 32 testes, todos aprovados.
- `python testes_smoke.py`: `VighnaStudy 0.23.31: testes smoke OK`.
- `python -m py_compile` dos módulos do projeto e do núcleo: aprovado.
- `ruff check statistics_core test_statistics_core.py evolucao.py`: aprovado.
- `git diff --check`: aprovado; apenas avisos de conversão LF/CRLF do Git.
- Banco existente em cópia segura: `PRAGMA integrity_check = ok`, `foreign_key_check = 0`; 3 perfis, 156 questões, 123 tentativas históricas, 18 sessões e 5 revisões recentes carregadas.
- UI offscreen sobre a cópia: janela iniciou; sete abas (`Histórico`, `Algoritmo`, `Disciplinas`, `Pontos fracos`, `Revisões recentes`, `Tendências`, `Progresso`) abriram; tabelas exibiram 94 tópicos, 6 disciplinas e 1 ponto fraco.

O lint global também foi inspecionado e ainda aponta dívida técnica histórica nos monólitos `main.py`, `banco.py` e `checkpoint.py`; não foi feita uma reformatação ampla fora do escopo. Os arquivos novos e o módulo histórico alterado passam no lint direcionado.

## 21. Pendências

- Adicionar `concurso_id`/linhagem explícita a revisões e sessões de foco; até lá, os estados `legacy_limited` são obrigatórios.
- Implementar no núcleo métricas ainda previstas, mas não necessárias aos consumidores migrados: pulos, sessões concluídas, durações, taxa agregada de revisão e agenda completa.
- Migrar o relatório estratégico legado e snapshots de efetividade somente após definir compatibilidade.
- Persistir histórico futuro de consolidação se o produto precisar de série temporal desse estado.
- Preservar a fila em observação paralela até um passo específico de paridade e migração.

## 22. Recomendação para o próximo passo

O Núcleo Estatístico pode ser tratado como fonte oficial dos consumidores não críticos migrados. O próximo passo deve ser uma etapa exclusiva de paridade da Fila Inteligente: ampliar fixtures representativas, comparar decisões por um período controlado e somente então propor uma versão nova da fila. Não avançar para gamificação, novos gráficos ou troca dos pesos enquanto as pendências de linhagem e paridade não estiverem explicitamente resolvidas.

Após a execução final da suíte, será gerado um checkpoint completo com fontes, recursos e snapshot SQLite íntegro; o nome do arquivo é informado na entrega desta etapa.
