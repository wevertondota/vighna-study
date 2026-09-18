# Relatório do Passo 6 — Bloqueadores da fila e observação sombra

Data da validação: 18/09/2026

Versão: VighnaStudy 0.23.32 (`fila-sombra-observacao-v1`)

Schema: 17

## 1. Estado inicial

O Passo 6 começou sobre o checkpoint final validado do Passo 5, com a Fila
Inteligente V3 como única fila decisória. A candidata existia apenas para
comparação sombra, sempre com `used_for_queue_order = false`. O banco real
possuía 5 revisões e ainda não tinha `revisoes.concurso_id`.

## 2. Bloqueadores vindos do Passo 5

Os bloqueadores eram: ausência de linhagem direta de concurso nas revisões,
política ainda não definitiva para evidência `low`, inexistência de telemetria
relacional de observações reais, falta de deduplicação e ausência de um gate
objetivo de prontidão. Havia também pouca evidência oficial no banco real.

## 3. Migração de `revisoes.concurso_id`

Foi aplicada migração aditiva e idempotente, acrescentando
`revisoes.concurso_id INTEGER NULL`. Bancos novos recebem chave estrangeira
para `concursos(id) ON DELETE SET NULL`; bancos antigos recebem a coluna sem
reescrever o histórico. Foi criado o índice
`idx_revisoes_concurso_topico_data(concurso_id, topico_id, data DESC)`.

Antes da migração foi criado e validado o backup
`backups/estudos_2026-09-18_13-05-18_antes_passo6_linhagem.db`.

## 4. Caminhos de gravação atualizados

As revisões manuais registram o concurso capturado quando o diálogo é aberto.
As revisões automáticas registram o concurso explícito da sessão de questões.
A resolução de linhagem aceita apenas contexto explícito ou a sessão informada;
nunca infere concurso a partir do tópico. As assinaturas anteriores permanecem
compatíveis por meio de parâmetros opcionais.

## 5. Tratamento do histórico legado

As 5 revisões históricas foram preservadas com `concurso_id = NULL`. Elas são
tratadas como `legacy_limited`, não são atribuídas artificialmente ao concurso
ativo e continuam disponíveis para a compatibilidade limitada prevista. Um
marcador de migração distingue esse legado de novas gravações que indevidamente
ficassem sem linhagem conhecida.

## 6. Política oficial de evidência `low`

A política foi centralizada. Evidência `insufficient` nunca é elegível e usa
fallback; `low` pode participar somente da visão exploratória e recebe a
certificação `provisional_low_evidence`; `moderate` e `high` são elegíveis para
a visão de ativação. Essa política não muda a fila ativa.

## 7. Candidato exploratório

O candidato exploratório aceita domínio oficial com evidência `low` para medir
o possível efeito futuro. Evidência `insufficient` continua em fallback. A
saída contém versão, componentes, fontes, fallbacks, posição e score, sempre com
`used_for_queue_order = false`.

## 8. Candidato elegível

A visão elegível usa domínio oficial somente com evidência `moderate` ou
`high`. Em `low`, aplica o fallback explícito
`official_mastery_low_evidence_not_activation_eligible`; em `insufficient`,
mantém o fallback de evidência insuficiente. Ela também permanece estritamente
sombra e não é apresentada ao usuário.

## 9. Arquitetura da telemetria

Foram criadas tabelas separadas do histórico acadêmico:

- `fila_shadow_execucoes`: contexto, versões, taxas, contagens e salvaguardas;
- `fila_shadow_itens`: posições, scores, evidência e classificação por tópico;
- `fila_shadow_fallbacks`: fallback por componente e item.

As tabelas têm índices, relações e restrições que exigem
`used_for_queue_order = 0`. Elas não são fonte do núcleo estatístico, da V4, da
V5 ou da fila V3.

## 10. Regra de observação significativa

Somente eventos explícitos e operacionalmente relevantes são persistidos:
auditoria manual, início de sessão recomendada, confirmação de “Estudar agora”
e snapshot técnico explícito. Apenas consultar a fila ou montar um snapshot em
memória não grava telemetria.

## 11. Deduplicação

A assinatura combina concurso, evento, versões e ordens comparadas. Eventos
iguais dentro da janela de 10 minutos não criam nova execução, item ou fallback.
O teste de integração confirmou a deduplicação relacional.

## 12. Gate de prontidão

O gate puro centraliza suficiência de amostra, divergências Top 3, proteção
temporal, universo elegível e integridade da linhagem. Ele apenas classifica e
lista bloqueadores; não ativa a candidata nem escreve em tabelas acadêmicas.

## 13. Critérios configurados

Os limiares iniciais são: 20 observações, 5 dias distintos, 5 tópicos distintos,
10 observações de itens com evidência `moderate/high`, zero divergência Top 3
inesperada não resolvida, zero violação temporal, zero item inelegível, zero
nova revisão com contexto conhecido sem linhagem e zero conflito de linhagem.

## 14. Fixtures

As fixtures cobrem pouca amostra, amostra suficiente, divergência inesperada no
Top 3, violação de proteção temporal, falha de persistência, histórico misto,
concursos A/B, banco legado e os quatro níveis de evidência. Nenhuma fixture de
sucesso foi misturada aos números reais do banco.

## 15. Testes de linhagem

Foram validados: coluna e índice em banco novo; migração aditiva, idempotente e
sem perda em banco antigo; revisão manual com concurso conhecido; revisão sem
contexto permanecendo `NULL`; revisão automática herdando o concurso da sessão;
consolidação sem trocar A por B; isolamento A/B/legado; e bloqueio do gate em
caso de conflito de linhagem.

## 16. Testes de evidência

Foram testados `insufficient`, `low`, `moderate` e `high`. Os testes confirmam
que `insufficient` usa fallback nas duas visões, `low` é apenas exploratório e
`moderate/high` são elegíveis. Todos preservam
`used_for_queue_order = false`.

## 17. Proteção temporal

O resumo de segurança mede violações em que a candidata contrariaria restrições
operacionais de revisão e recência. O gate bloqueia qualquer ocorrência. A
fixture específica foi bloqueada e a observação real teve zero violações.

## 18. Integração V4/V5

V4 e V5 continuam sem consumir `candidate_position`, `candidate_score` ou a
telemetria sombra. A recomendação e a ordem exibidas continuam sendo produzidas
pelos caminhos existentes, com a V3 como única fila decisória.

## 19. Resultado no banco real

A migração preservou 5 de 5 revisões. Todas as 5 revisões anteriores ficaram
com linhagem `NULL`, como exigido. `PRAGMA integrity_check` retornou `ok` e
`PRAGMA foreign_key_check` retornou lista vazia. A observação real não alterou
tabelas ou métricas acadêmicas.

## 20. Quantidade real atual de observações

Há 1 observação sombra real (`manual_audit`), em 1 dia distinto, contendo 6
tópicos. Existem 6 linhas de itens sombra. A execução registra
`used_for_queue_order = 0`.

## 21. Distribuição de evidência real

A distribuição observada é:

- `insufficient`: 5 itens;
- `low`: 1 item;
- `moderate`: 0 itens;
- `high`: 0 itens.

Não foram fabricados dados `moderate/high` para satisfazer o gate.

## 22. Divergências inesperadas

A observação real teve 0 divergências inesperadas e 0 divergências inesperadas
no Top 3. As taxas Top 1, interseção Top 3 e interseção Top 5 foram 100%. Houve
1 divergência classificada como esperada e explicável por fallback/política.

## 23. Fallbacks

Foram observadas 15 ocorrências de fallback:

- `official_trend_insufficient_window`: 6;
- `official_mastery_insufficient_evidence`: 5;
- `legacy_initial_or_unqualified_review_count`: 2;
- `review_lineage_legacy_limited`: 2.

Esses números são sinais de maturação da amostra, não autorização para ativação.

## 24. Status real do gate

`ready = false`.

Classificação: **A. INFRAESTRUTURA PRONTA / AMOSTRA AINDA INSUFICIENTE**.

Bloqueadores atuais do gate:

- 1 observação de 20 necessárias;
- 1 dia distinto de 5 necessários;
- 0 observações `moderate/high` de 10 necessárias.

O critério de 5 tópicos já foi superado (6). Não há bloqueador técnico de
divergência inesperada, proteção temporal, item inelegível ou linhagem nova.

## 25. Riscos restantes

Restam risco estatístico por amostra curta, ausência atual de evidência
`moderate/high` e uso frequente de fallbacks. As 5 revisões antigas permanecem
sem concurso por decisão de segurança e devem ser consideradas legado limitado.
A coleta deve continuar em uso real e ser reavaliada somente após os limiares.

## 26. Recomendação de continuidade

Manter a Fila Inteligente V3 como única fila decisória e continuar coletando
observações significativas, deduplicadas e sem interferência acadêmica. Não
propor migração enquanto `ready` permanecer falso. O restante do desenvolvimento
pode prosseguir, preservando o gate e revisando periodicamente seus dados reais.

## Validação executada

- suíte completa: 76 testes, todos aprovados;
- `test_fila_candidata.py`: 23 testes aprovados;
- `test_fila_observacao.py`: 21 testes aprovados;
- `test_statistics_core.py`: 32 testes aprovados;
- compilação Python: aprovada;
- lint direcionado dos módulos do Passo 6: aprovado;
- integridade SQLite: aprovada;
- chave estrangeira SQLite: aprovada;
- smoke, inicialização, `git diff --check` e checkpoint: registrados após a
  rodada final de validação.

Conclusão: a infraestrutura técnica de observação está pronta, mas a amostra
real ainda é insuficiente. A Fila Inteligente V3 permanece ativa e é a única
que decide o que o usuário estudará.
