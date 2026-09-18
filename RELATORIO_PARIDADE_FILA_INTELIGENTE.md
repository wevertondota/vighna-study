# Relatório de Paridade da Fila Inteligente — Passo 5

Data da validação: 18/09/2026
Fila ativa: `fila_inteligente_v3`
Fila candidata: `fila_candidate_shadow_v1`
Versão das métricas oficiais: `1`
Classificação: **PRONTO COM BLOQUEADORES ESPECÍFICOS**

## 1. Arquitetura atual da fila

`banco.obter_prioridades_sessao_adaptativa()` continua calculando, ordenando e devolvendo a Fila Inteligente V3. A ordenação ativa ocorre antes da comparação sombra e preserva o desempate por score, importância, disciplina e tópico.

O módulo puro `fila_candidata.py` recebe os itens V3 já ordenados e os DTOs oficiais carregados em lote. Ele calcula componentes e ordem candidatos, mas devolve somente telemetria anexada em `comparacao_fila_sombra`. Todo objeto produzido mantém `used_for_queue_order = false`.

Nenhum caminho normal da fila grava snapshot, sessão, agendamento ou estatística. A persistência em JSON existe apenas na chamada explícita de auditoria `salvar_snapshot_paridade_fila()`.

## 2. Baseline V3

Baseline real congelado antes da implementação, perfil/concurso 40:

| Posição | Tópico | Score V3 | Motivo principal |
|---:|---:|---:|---|
| 1 | 27 | 67,0 | atraso |
| 2 | 51 | 63,8 | domínio |
| 3 | 31 | 57,7 | domínio |
| 4 | 32 | 57,7 | domínio |
| 5 | 74 | 43,0 | domínio |
| 6 | 23 | 24,4 | importância |

O baseline executou 18 SELECTs em aproximadamente 614,775 ms. A medição é diagnóstica e depende do estado local, do sistema operacional e do cache do SQLite.

## 3. Componentes e pesos

Os pesos foram preservados integralmente; nenhum peso novo foi criado.

| Componente | Peso |
|---|---:|
| atraso | 18% |
| domínio | 18% |
| erros recentes | 15% |
| queda | 12% |
| importância | 12% |
| cobertura | 9% |
| revisões | 7% |
| espaçamento | 9% |

Cada componente e o score final ficam na faixa de 0 a 100. A fórmula ativa é:

`score_fila = clamp(sum(componente_i * peso_i / 100), 0, 100)`

Regras especiais do baseline:

- domínio é `100 - Domínio V2`; ausência legada resulta no tratamento já existente do Domínio V2;
- erros recentes usam o maior valor entre perda de controle e pressão dos estados crítico, recorrente e em recuperação;
- atraso vencido começa em 75 e cresce 2,5 por dia até 100; hoje vale 70; futuro vale zero; sem prazo vale 40 no primeiro contato ou 15 depois dele;
- queda só penaliza a partir de cinco tentativas e usa os limites moderado/forte da configuração de espaçamento;
- importância 1–5 é normalizada linearmente para 0–100;
- cobertura é `100 - cobertura`; revisões usam 100, 78, 58, 40, 24 e 12 para zero, uma, duas, três, quatro e cinco ou mais revisões;
- espaçamento compara dias desde a prática com o intervalo-alvo; sem histórico suficiente vale 50;
- se `usar_importancia_fila` estiver desativado, o peso de importância vira zero e os outros pesos são renormalizados. A candidata copia os pesos efetivamente usados no item, sem inventar distribuição nova;
- não existe bônus adicional fora dos oito componentes nem penalização oculta;
- motivo principal é a maior contribuição, com desempate pelo maior peso;
- a ordem usa score decrescente, importância decrescente, disciplina e tópico em ordem alfabética sem diferenciar maiúsculas.

## 4. Mapeamento legado para oficial

| Componente V3 | Fonte atual | Fonte candidata | Compatibilidade | Decisão do modo sombra |
|---|---|---|---|---|
| domínio | Domínio V2 | `mastery_score@1` | parcial | Usa oficial quando certificado; caso contrário preserva o legado com fallback explícito. |
| cobertura | cobertura do Domínio V2 | `question_coverage_rate@1` | total quando o catálogo ativo é o mesmo | Exige paridade; delta é inesperado e requer investigação. |
| queda | base/recente legado | `performance_trend@1` e `trend_delta_pp` | parcial | Usa a janela oficial quando suficiente; preserva a queda V3 se a janela for insuficiente. |
| erros recentes | estado de erros do Domínio V2 | `mastery_score.error_control@1` | parcial | Usa controle e estados oficiais; ausência cai explicitamente para V3. |
| revisões | iniciais + histórico global | `completed_review_count@1` | parcial | Só usa o valor oficial se estado e contagem forem compatíveis; demais casos mantêm legado marcado. |
| atraso | agenda V3 | agenda V3 | idêntica/operacional | Mantido exatamente. |
| importância | configuração do usuário | mesma configuração | idêntica | Mantida exatamente. |
| espaçamento | agenda/algoritmo V3 | mesmo valor V3 | idêntica/operacional | Mantido exatamente. |

## 5. Componentes que permaneceram operacionais

`atraso` e `espacamento` continuam sendo estados operacionais V3. A candidata não recalcula datas, não sugere novo agendamento e não altera o algoritmo de espaçamento. `importancia` continua sendo configuração do usuário, não métrica acadêmica.

## 6. Política de dados insuficientes

`mastery_score = null` significa domínio público não certificado. Nunca é convertido em zero. A candidata preserva temporariamente o componente V3 e registra `official_mastery_insufficient_evidence`.

Os níveis `insufficient`, `low`, `moderate` e `high` são transportados para a comparação. Domínio oficial com evidência `low` é aceito apenas como valor provisório e recebe o aviso `provisional_mastery_low_evidence`. Zero oficial válido continua sendo zero e não dispara fallback.

## 7. Política de fallback

Cada fallback contém componente, razão, fonte e valor legado. As razões diferenciam:

- métrica indisponível;
- evidência ou janela insuficiente;
- valor oficial ausente apesar de estado diferente;
- parâmetros de controle de erros ausentes;
- revisão `legacy_limited`;
- revisões iniciais ou contagem sem qualificação de perfil;
- valor oficial válido igual a zero.

Nenhum fallback é apresentado como oficial. A fonte sempre começa por `fallback.` e a remoção futura é localizada por componente.

## 8. Arquitetura da fila candidata

A candidata:

1. recebe exatamente os itens elegíveis que sobreviveram aos filtros V3;
2. reutiliza o lote oficial retornado por `get_topic_metrics_batch()`;
3. preserva os pesos V3;
4. calcula valor bruto, score normalizado, peso, contribuição, fonte, versão, estado e fallback de cada componente;
5. ordena uma cópia independente com o mesmo desempate estável;
6. compara scores e posições;
7. nunca substitui nem reordena a lista ativa.

## 9. Fixtures executadas

As fixtures A–X foram automatizadas em `test_fila_candidata.py`:

- A: nunca estudado;
- B: uma correta;
- C: uma errada;
- D: evidência insuficiente com 100%;
- E: baixo domínio/evidência alta;
- F: alto domínio/evidência alta;
- G: revisão vencida;
- H: revisão hoje;
- I: revisão futura;
- J: sem próxima revisão;
- K/L: importância muito alta/baixa;
- M/N/O: queda, melhora e estabilidade;
- P: erros críticos consecutivos;
- Q: erro recuperado;
- R/S: cobertura muito baixa/alta;
- T: muitas revisões;
- U: revisão `legacy_limited`;
- V: empate e desempate estável;
- W: tópico pausado;
- X: tópico sem questões ativas.

W e X usam banco temporário completo e confirmam que a candidata não inventa elegibilidade.

## 10. Interações entre fatores

Foram cobertas as combinações exigidas: domínio alto + revisão vencida; domínio baixo + revisão futura; evidência insuficiente + importância alta; queda + cobertura alta; erros críticos + revisão hoje; tópico novo + importância alta; domínio baixo + evidência alta + importância baixa.

Os testes confirmam que atraso e vencimento permanecem presentes e com a mesma contribuição mesmo quando uma métrica acadêmica aponta na direção oposta.

## 11. Comparação de scores

Na base real copiada, cinco tópicos tiveram paridade exata de score. O tópico 23 passou de 24,4 para 25,0 na sombra: o componente de domínio passou de 24,7 para 28,0 porque `mastery_score@1 = 71,9736`, com evidência baixa. O delta de componente foi +3,3 e o delta final +0,6.

Essa divergência é esperada e classificada como `formula_change`. Ela não alterou a posição.

## 12. Comparação de posições

- tópicos avaliados: 6;
- posições preservadas: 6 (100%);
- deslocamento absoluto médio: 0,0;
- maior subida: 0;
- maior queda: 0;
- ordem ativa: 27, 51, 31, 32, 74, 23;
- ordem candidata: 27, 51, 31, 32, 74, 23.

## 13. Top N comparado

| Corte | Interseção | Taxa |
|---|---:|---:|
| Top 1 | 1/1 | 100% |
| Top 3 | 3/3 | 100% |
| Top 5 | 5/5 | 100% |
| Top 10 | 6/6 efetivos | 100% |

As taxas são diagnósticas e não constituem regra automática de aprovação.

## 14. Divergências esperadas

Foi observada uma divergência esperada: Domínio V2 versus `mastery_score@1` no tópico 23. A causa é mudança de fórmula e tratamento explícito de evidência, não bug de ordenação.

Queda pode divergir por janela temporal e fórmula. Revisões podem divergir por linhagem. Esses deltas são classificados separadamente se aparecerem durante observação futura.

## 15. Divergências inesperadas

Nenhuma divergência inesperada apareceu na cópia real. Cobertura e controle de erros mantiveram paridade onde comparáveis. Qualquer delta futuro em cobertura, estados operacionais ou configuração do usuário é marcado como `expected = false` e exige investigação.

## 16. Impacto da evidência

Entre os seis tópicos reais elegíveis, cinco possuem evidência `insufficient` e um possui evidência `low`. Não há tópico elegível com evidência moderada ou alta na amostra atual.

Consequência: a segurança dos fallbacks foi validada, mas a paridade real da fórmula oficial de domínio ainda tem baixa representatividade. Isso bloqueia ativação, não o modo sombra.

## 17. Impacto de `legacy_limited`

Fixtures confirmam que `legacy_limited` nunca é tratado como valor oficial completo. O valor V3 é preservado e a razão `review_lineage_legacy_limited` fica registrada.

Na amostra real, 15 fallbacks foram usados em seis tópicos: cinco de domínio insuficiente, seis de janela de tendência insuficiente e quatro de contagem de revisões iniciais/não qualificadas.

## 18. Linhagem de revisões

O histórico de `revisoes` não possui perfil/concurso inequívoco em todos os registros. Nenhum perfil foi inferido retroativamente.

Plano recomendado para o Passo 6:

1. adicionar `concurso_id` anulável por migração aditiva;
2. preencher o campo obrigatoriamente nos registros futuros criados em contexto de perfil;
3. manter registros antigos como `NULL`/`legacy_limited`;
4. adicionar índice e chave estrangeira compatíveis com bancos antigos;
5. testar bancos novos, migrados e histórico misto;
6. não retropreencher concurso por palpite.

A migração não é indispensável para observação sombra e, por isso, não foi executada neste passo.

## 19. Integração com Motor V4/V5 e interface

`MotorRecomendacaoV4` e `MotorRecomendacaoV5` não leem `comparacao_fila_sombra` nem `score_candidate`; continuam consumindo `score_fila` e os campos V3. O teste automatizado inspeciona ambos os consumidores.

Os caminhos de “Estudar agora”, sessão recomendada, proteção temporal e “Por que esta recomendação?” continuam recebendo a lista V3. A interface ainda mostra explicitamente “Fila Inteligente V3”. Não houve alteração visual.

## 20. Performance

| Cenário | SELECTs | Tópicos | Tempo aproximado |
|---|---:|---:|---:|
| baseline V3 real, antes da alteração | 18 | 6 | 614,775 ms |
| V3 + sombra real sobre cópia consistente | 18 | 6 | 577,956 ms |
| comparação pura, fixture controlada | 0 | 100 | média 3,931 ms (20 execuções) |

Não houve SELECT adicional por tópico: a candidata reutiliza o lote oficial. A diferença de tempo real está dentro da variação de uma medição local e não deve ser interpretada como ganho de performance. Nenhum cache persistente foi criado.

## 21. Testes automatizados

Resultados:

- `test_fila_candidata.py`: 23 testes, todos aprovados;
- `test_statistics_core.py`: 32 testes, todos aprovados;
- `testes_smoke.py`: aprovado, VighnaStudy 0.23.31;
- `py_compile`: aprovado nos arquivos do projeto;
- lint completo dos arquivos novos: aprovado;
- lint crítico direcionado nos arquivos legados alterados: aprovado;
- `git diff --check`: aprovado;
- SQLite `PRAGMA integrity_check`: aprovado;
- inicialização Qt offscreen contra cópia do banco: confirmada; encerramento controlado por timeout, código 124, sem erro de inicialização.

O teste de consulta em lote verifica que o custo não cresce por tópico. O teste de efeitos colaterais compara contagens de todas as tabelas antes e depois da fila e do snapshot.

## 22. Riscos

- amostra real pequena e dominada por evidência insuficiente;
- baixa observação real de domínio oficial certificado;
- revisões antigas sem perfil inequívoco;
- mudanças futuras no universo do catálogo podem gerar delta de cobertura;
- snapshots contêm telemetria detalhada e devem continuar sendo gerados apenas por auditoria explícita;
- uma janela de observação curta não exercita todos os estados temporais reais.

`sessoes_foco` também não tem perfil inequívoco no histórico, mas nenhuma variável da candidata usa foco. Portanto, permanece fora do escopo e não é bloqueador desta fila.

## 23. Bloqueadores

Antes de migrar a decisão ativa para a candidata:

1. acumular amostra real com evidência moderada/alta suficiente para observar domínio e tendência oficiais;
2. resolver a linhagem de concurso para revisões futuras por migração aditiva;
3. executar um período controlado de observação sombra com mais estados temporais e registrar divergências inesperadas;
4. definir critério de produto para uso de `mastery_score` com evidência `low`, hoje marcado como provisório.

Não há bloqueador para manter o modo sombra atual.

## 24. Classificação final de prontidão

**PRONTO COM BLOQUEADORES ESPECÍFICOS.**

A candidata está pronta para observação controlada: fallbacks são determinísticos, `None` é seguro, a proteção temporal foi preservada, a carga é em lote, os consumidores V4/V5 continuam na V3 e todos os testes críticos passaram.

Ela **não está pronta para substituir a V3** enquanto os quatro bloqueadores acima permanecerem. A classificação não autoriza ativação.

## 25. Recomendação para o Passo 6

Manter `fila_inteligente_v3` como única fila decisória. Continuar a sombra por janela controlada, adicionar linhagem apenas para revisões futuras e repetir o snapshot quando houver uma população representativa com evidência moderada/alta.

O Passo 6 deve primeiro corrigir os bloqueadores e definir o tratamento de evidência baixa. Somente depois deve propor migração gradual, versionada, reversível e com a V3 disponível como fallback.

## Artefatos de auditoria e checkpoint

- `PASSO5_SNAPSHOT_PARIDADE.json` é o snapshot estruturado reprodutível desta execução.
- `checkpoint_manifest.json`, dentro do ZIP nativo, é a autoridade de integridade e restauração.
- `MANIFEST_SHA256.txt` não possui consumidor no código atual. É legado, foi mantido por cautela com dependências externas desconhecidas, excluído do novo inventário nativo e não deve indicar corrupção do checkpoint atual.
- `PASSO4_STATUS_ATUAL.txt` e `PASSO4_DIFF_ATUAL.patch` são artefatos temporários de desenvolvimento, excluídos do inventário e não fontes normativas do estado atual.

O checkpoint final deve ser gerado e validado exclusivamente por `checkpoint.py`, com fontes, recursos e snapshot consistente de `estudos.db`.
