# PASSO 8 — TENDÊNCIAS E COMPARAÇÕES TEMPORAIS V2

Use como base obrigatória:

- `ESPECIFICACAO_TECNICA_NUCLEO_ESTATISTICO.md`
- `RELATORIO_VALIDACAO_NUCLEO_ESTATISTICO.md`
- `RELATORIO_PASSO_7_PROGRESSO_EDITAL_V2.md`
- implementação atual em `statistics_core/`
- `progresso_edital.py`
- `evolucao.py`
- implementação atual das abas `Histórico` e `Tendências`
- card de tendência do Dashboard

## CONTEXTO VALIDADO

O Passo 7 foi validado no checkpoint final.

Estado confirmado:

- versão `0.23.33`;
- build `progresso-edital-v2`;
- schema 17;
- 93 testes aprovados;
- `py_compile` aprovado;
- SQLite com `integrity_check = ok`;
- nenhuma violação de foreign key;
- manifesto do checkpoint íntegro;
- Fila Inteligente V3 continua como única fila decisória;
- fila candidata continua sombra;
- gate sombra continua fechado por falta de amostra real.

Há uma pequena diferença documental no checkpoint:
o relatório registrou cobertura de questões de aproximadamente `52,12%`,
mas o banco efetivamente incluído no checkpoint atual calcula
`123 / 242 = 50,83%`.

Não fixe nenhum desses percentuais no código ou no relatório.
Considere o banco + Núcleo Estatístico como fonte de verdade e determine
apenas por que o denominador mudou entre a medição do relatório e o
checkpoint final.

Isso não bloqueia esta etapa.

---

# OBJETIVO CENTRAL

Transformar `Histórico` e `Tendências` em uma camada temporal confiável.

O usuário deve conseguir distinguir claramente:

1. O que aconteceu no período selecionado?
2. Como esse período se compara ao período anterior equivalente?
3. Existe tendência estatisticamente suficiente ou ainda faltam dados?
4. Quais disciplinas/tópicos melhoraram ou pioraram com base comparável?
5. Como cobertura, evidência e consolidação evoluem A PARTIR DE AGORA,
   sem inventar histórico retroativo?

A regra conceitual é:

EVENTOS BRUTOS
↓
PERÍODOS OFICIAIS
↓
MÉTRICAS OFICIAIS
↓
COMPARAÇÃO TEMPORAL
↓
SÉRIE HISTÓRICA CONFIÁVEL
↓
INTERFACE

---

## 1. NÃO ALTERAR A FILA

Durante todo o Passo 8:

- V3 permanece ativa;
- candidata permanece sombra;
- `used_for_queue_order = false`;
- não alterar pesos;
- não alterar recomendação;
- não alterar agenda;
- não alterar espaçamento.

Tendências são análise, não prioridade.

---

## 2. AUDITE `Histórico` E `Tendências`

Antes de editar, mapeie integralmente as duas abas.

Para cada componente, registre:

- fonte;
- fórmula;
- período;
- escopo;
- tratamento de ausência;
- se usa Núcleo Estatístico;
- se usa cálculo legado;
- se existe duplicação entre as abas.

Identifique especialmente:

- comparações primeira metade × segunda metade;
- período atual × período anterior;
- gráficos diários;
- desempenho;
- questões;
- revisões;
- foco;
- domínio;
- consistência;
- evolução por disciplina;
- evolução por tópico;
- maior evolução;
- maior queda.

Não mantenha duas definições diferentes para a mesma pergunta analítica.

---

## 3. DISTINGA DOIS CONCEITOS

### A. TENDÊNCIA OFICIAL DE DESEMPENHO

É `performance_trend@1`.

Usa duas janelas consecutivas de tentativas,
conforme a especificação oficial.

Não depende de semanas do calendário.

### B. COMPARAÇÃO ENTRE PERÍODOS

Compara, por exemplo:

- últimos 7 dias
versus
- 7 dias anteriores;

ou:

- intervalo personalizado
versus
- intervalo imediatamente anterior de mesma duração.

Não chame automaticamente essa comparação de `performance_trend@1`.

A interface deve distinguir os dois conceitos.

---

## 4. PADRONIZE OS PERÍODOS

Use `statistics_core.periods.StatisticalPeriods` como fonte normativa.

Suporte:

- 7 dias;
- 30 dias;
- 60 dias;
- 90 dias;
- personalizado.

Para qualquer período atual com início definido, derive o anterior por:

`previous_equivalent()`

Evite lógica de datas duplicada em `main.py`.

Use o timezone oficial do Núcleo Estatístico.

---

## 5. CORRIJA O USO DE DATA LOCAL

Audite componentes temporais que ainda usam UTC diretamente ou datas locais
não normalizadas.

Toda classificação por dia civil da camada acadêmica deve seguir:

`America/Sao_Paulo`

conforme o contrato estatístico.

Não permita diferença de um dia em horários próximos à meia-noite.

---

## 6. CRIE UMA CAMADA TEMPORAL CENTRAL

Crie um módulo/serviço coerente com a arquitetura atual.

Exemplo conceitual:

`analise_temporal.py`

ou equivalente.

Ele deve montar um snapshot reutilizável, por exemplo:

`TemporalAnalyticsSnapshot`

contendo no mínimo:

- concurso_id;
- período atual;
- período anterior equivalente;
- métricas do período atual;
- métricas do período anterior;
- comparações;
- série diária;
- disciplinas;
- tópicos comparáveis;
- tendência oficial;
- estado de suficiência;
- avisos de linhagem;
- generated_at;
- versão.

A UI não deve executar fórmulas estatísticas relevantes.

---

## 7. MÉTRICAS DO PERÍODO ATUAL

Obtenha do Núcleo Estatístico, quando aplicável:

- tentativas;
- acertos;
- erros;
- taxa de acerto;
- questões únicas;
- sessões de questões;
- dias de estudo;
- revisões qualificadas;
- desempenho recente;
- tendência oficial.

Não substitua métrica oficial por consultas paralelas equivalentes.

---

## 8. MÉTRICAS DO PERÍODO ANTERIOR

Calcule o mesmo conjunto no período anterior equivalente.

A comparação precisa usar:

mesmo escopo
+
mesma duração
+
mesma semântica.

Não compare 30 dias com uma semana ou com “primeira metade”.

---

## 9. REGRAS DE SUFICIÊNCIA PARA COMPARAÇÃO

Siga a especificação oficial:

Para comparar TAXA DE ACERTO entre períodos:

- pelo menos 10 tentativas efetivas em cada período;
- pelo menos 2 dias ativos em cada período.

Se qualquer requisito não for atendido:

`Dados insuficientes para comparação`

Contagens como quantidade de questões podem ser comparadas descritivamente
mesmo sem inferência.

Não classifique uma variação de taxa como melhora/queda quando a base não
atingir o mínimo.

---

## 10. DELTAS

Para taxas, use diferença em pontos percentuais:

`delta_pp = taxa_atual - taxa_anterior`

Não use variação percentual relativa para acurácia.

Para contagens, pode existir:

- diferença absoluta;
- variação percentual relativa, somente se o denominador anterior > 0.

Quando o anterior for zero:

- informe a diferença absoluta;
- não gere percentual infinito ou artificial.

---

## 11. NÃO TRANSFORME MAIS ATIVIDADE EM “MELHOR”

Mais questões, mais sessões ou mais tempo de foco significam:

`mais atividade`

e não automaticamente:

`melhora acadêmica`.

Evite cores/linguagem que interpretem aumento de volume como ganho de
aprendizagem.

Da mesma forma, menos atividade não é automaticamente pior desempenho.

---

## 12. SÉRIE DIÁRIA

Crie série diária contínua para o período.

Para cada dia, quando houver fonte confiável:

- tentativas;
- acertos;
- taxa de acerto do dia;
- questões únicas;
- sessões;
- revisões qualificadas;
- dias/atividade;
- foco efetivo global, se mantido;
- outros campos estritamente descritivos.

Para contagens sem eventos:

`0`

Para taxa sem tentativas:

`None`

Nunca desenhe `0%` num dia sem respostas.

---

## 13. REVISÕES: RESPEITAR `concurso_id`

O código atual de `evolucao.py` ainda precisa ser auditado porque consultas
históricas de revisões podem relacionar revisões ao concurso apenas pela
associação do tópico.

Agora que `revisoes.concurso_id` existe:

- revisão com `concurso_id` confirmado pode entrar no perfil;
- revisão de outro concurso não pode entrar;
- revisão histórica `concurso_id IS NULL` não deve ser atribuída por inferência;
- legado sem linhagem deve permanecer `legacy_limited`.

Não reintroduza a contaminação corrigida no Passo 6.

---

## 14. FOCO: NÃO INVENTAR LINHAGEM DE CONCURSO

`sessoes_foco` ainda não possui identidade histórica inequívoca de concurso.

Enquanto isso permanecer verdadeiro:

- foco pode ser mostrado como métrica GLOBAL de hábito;
- deve ser claramente rotulado como global;
- não deve ser apresentado como tempo específico do concurso ativo;
- não deve entrar em comparação acadêmica do perfil como se tivesse linhagem.

Não faça retroatribuição por tópico ou tela aberta.

---

## 15. DOMÍNIO HISTÓRICO: NÃO USAR LEGADO COMO OFICIAL

O código atual usa registros como:

`efetividade_sessoes.dominio_medio_depois`

para desenhar “domínio observado”.

Audite a origem dessa coluna.

Se ela não representar exatamente `mastery_score@1` versionado no instante
histórico, NÃO a apresente como tendência oficial de domínio.

Opções aceitáveis:

- remover da tendência principal;
- rotular explicitamente como indicador legado;
- mantê-la apenas em diagnóstico técnico.

Não misture domínio legado com `mastery_score@1`.

---

## 16. DOMÍNIO ATUAL

O `mastery_score@1` atual pode continuar sendo mostrado como referência atual,
desde que acompanhado de:

- evidência;
- cobertura;
- estado `insufficient_data`, quando aplicável.

Não use o domínio atual como se fosse valor histórico de cada dia passado.

---

## 17. HISTÓRICO FUTURO DE PROGRESSO

Agora é apropriado iniciar uma série temporal verdadeira para:

- cobertura de tópicos;
- cobertura de questões;
- distribuição de evidência;
- evidência suficiente;
- consolidação;
- domínio global atual, quando calculável.

Crie persistência FUTURA e versionada.

Não tente reconstruir retroativamente esses valores.

---

## 18. SNAPSHOT DIÁRIO DE PROGRESSO

Crie uma tabela aditiva, por exemplo:

`progresso_snapshots_diarios`

ou nome coerente com o projeto.

Campos conceituais:

- id;
- concurso_id;
- data;
- captured_at;
- metric_version;
- snapshot_version;
- total_topics;
- started_topics;
- topic_coverage_rate;
- question_coverage_rate;
- insufficient_evidence_topics;
- low_evidence_topics;
- moderate_evidence_topics;
- high_evidence_topics;
- sufficient_evidence_rate;
- consolidated_topics;
- consolidated_rate;
- global_mastery_score;
- global_mastery_state.

Use chave lógica única por:

`concurso_id + data + versões`

ou política equivalente segura.

---

## 19. SEM BACKFILL INVENTADO

No primeiro uso após a migração:

- pode ser registrado um snapshot do estado atual;
- não criar snapshots falsos para dias anteriores;
- não inferir domínio/consolidação antigos;
- não usar datas das tentativas para fingir o estado completo do edital naquela data.

A interface deve poder informar:

`Histórico de progresso disponível a partir de DD/MM/AAAA`.

---

## 20. QUANDO CAPTURAR O SNAPSHOT

Evite gravar a cada refresh.

Capture no máximo uma versão efetiva por dia/perfil, atualizando o registro do
dia quando ocorrer evento acadêmico significativo, por exemplo:

- finalização de sessão de questões;
- revisão qualificada;
- importação/alteração relevante do catálogo que muda o denominador;
- mudança explícita de inclusão/pausa de tópico/disciplina;
- atualização de progresso após evento real.

Não conte a captura como atividade acadêmica.

---

## 21. HISTÓRICO DE CONSOLIDAÇÃO

A especificação já determina que consolidação futura deve ser persistida e não
reconstruída por suposição.

O snapshot diário atende à visualização agregada.

Se for necessário saber exatamente quando um tópico individual mudou de estado,
pode ser criada uma tabela/evento específico de transição, desde que:

- seja aditiva;
- registre somente mudanças reais futuras;
- não faça backfill;
- tenha versão da métrica.

Não implemente uma estrutura maior do que a necessária.

---

## 22. COMPARAÇÃO POR DISCIPLINA

Para cada disciplina, compare período atual e anterior usando eventos brutos do
próprio escopo.

Inclua quando houver base:

- tentativas;
- taxa de acerto;
- delta de taxa em p.p.;
- dias ativos;
- questões únicas;
- tendência oficial atual;
- domínio atual apenas como referência, não como delta histórico.

Não calcule média de tendências dos tópicos.

---

## 23. COMPARAÇÃO POR TÓPICO

Um tópico só pode aparecer como “melhorou” ou “piorou” em comparação temporal
quando os dois períodos possuem a base mínima oficial.

Caso contrário, classifique como:

`Não comparável ainda`

Pode continuar mostrando volume e desempenho descritivo do período.

Não escolha “maior queda” entre tópicos sem base suficiente.

---

## 24. MAIOR EVOLUÇÃO E PONTO DE ATENÇÃO

Revise os cards existentes.

“Maior evolução” exige comparação válida.

“Maior queda” exige comparação válida.

Quando não existir amostra suficiente:

`Ainda não há base suficiente para comparar tópicos.`

Não faça fallback para domínio baixo sob o título “maior queda”.

Se quiser mostrar domínio baixo, use outro título semântico.

---

## 25. HISTÓRICO × TENDÊNCIAS

Evite duplicidade entre as abas.

Sugestão de responsabilidade:

### Histórico
Responder:
“O que fiz ao longo do período?”

Priorizar:
- atividade;
- foco global;
- questões;
- sessões;
- revisões;
- dias ativos;
- série cronológica.

### Tendências
Responder:
“O desempenho está mudando?”

Priorizar:
- comparação atual × anterior;
- taxa de acerto;
- tendência oficial;
- disciplinas comparáveis;
- tópicos comparáveis;
- evolução de progresso somente quando existirem snapshots históricos reais.

Se a arquitetura atual justificar outra divisão, documente-a, mas elimine
sobreposição conceitual.

---

## 26. CARDS DA ABA TENDÊNCIAS

Priorize indicadores como:

- desempenho atual;
- comparação com período anterior;
- tendência oficial;
- tentativas no período;
- dias ativos;
- base estatística.

Não exiba “melhora” sem suficiência.

Mostre os requisitos faltantes quando possível, por exemplo:

`Faltam 7 tentativas no período anterior para comparação.`

---

## 27. GRÁFICOS

Não crie gráficos por estética.

Cada gráfico deve responder uma pergunta.

Sugestões:

### Desempenho diário
Taxa nos dias com respostas.

### Volume diário
Tentativas/questões por dia.

### Comparação atual × anterior
Quando houver base.

### Progresso do edital ao longo do tempo
Somente depois de existir mais de um snapshot diário real.

Se houver apenas um snapshot:

`Coleta histórica iniciada — ainda sem série suficiente.`

---

## 28. SUAVIZAÇÃO

Não aplique média móvel ou suavização que esconda os dados sem explicação.

Se futuramente houver média móvel:

- manter pontos brutos disponíveis;
- documentar janela;
- não usar suavização para classificação oficial.

Nesta etapa, prefira dados brutos ou agregação semanal explícita.

---

## 29. PERÍODOS LONGOS

Para 60/90 dias, evite gráfico diário ilegível.

A camada de dados pode fornecer todos os dias, mas a UI pode agrupar visualmente
por semana quando necessário.

Se agrupar:

- somar contagens;
- recalcular taxas a partir de acertos/tentativas;
- nunca tirar média simples das taxas diárias.

---

## 30. PERÍODO PERSONALIZADO

Período personalizado deve usar:

- início inclusivo;
- fim da UI inclusivo;
- conversão interna para `end_exclusive` no dia seguinte;
- período anterior equivalente de mesma duração.

Documente essa conversão.

---

## 31. PERFORMANCE

Evite N+1 por disciplina/tópico.

Use:

- `get_subject_metrics_batch`;
- `get_topic_metrics_batch`;
- consultas temporais agregadas;
- uma leitura em lote dos eventos necessários.

Meça o número de SELECTs em cenário com muitos tópicos.

---

## 32. TESTES

Crie testes cobrindo no mínimo:

A. período atual sem dados;

B. período anterior sem dados;

C. contagens atuais com anterior zero;

D. taxa atual com <10 tentativas;

E. taxa anterior com <10 tentativas;

F. ambos com >=10 tentativas e >=2 dias;

G. delta em pontos percentuais;

H. tendência oficial diferente de comparação temporal;

I. dia sem respostas gera taxa `None`;

J. revisão de outro concurso não entra;

K. revisão `concurso_id = NULL` permanece `legacy_limited`;

L. foco sem concurso é global;

M. domínio legado não vira domínio oficial histórico;

N. primeiro snapshot diário sem backfill;

O. atualização do mesmo snapshot diário;

P. dois dias reais produzem dois snapshots;

Q. mudança de catálogo atualiza snapshot do dia;

R. disciplina com volumes diferentes;

S. tópico não comparável não vira “queda”;

T. período personalizado e anterior equivalente;

U. timezone America/Sao_Paulo;

V. ausência de N+1 relevante;

W. fila V3 continua ativa.

---

## 33. DADOS REAIS DO CHECKPOINT

Registre no relatório o estado real encontrado.

No checkpoint recebido há aproximadamente:

- 129 tentativas;
- apenas 3 dias civis com tentativas;
- 18 sessões de questões;
- 2 sessões de foco concentradas em 1 dia;
- 5 revisões históricas sem `concurso_id`;
- nenhuma revisão com linhagem nova;
- zero observações sombra persistidas no banco final.

Esses números devem ser recalculados no início da execução.

Não os trate como constantes.

É esperado que várias comparações temporais reais permaneçam
`Dados insuficientes`.

Isso é comportamento correto.

---

## 34. NÃO FABRICAR TENDÊNCIAS

Não:

- criar dados históricos;
- copiar o valor atual para dias anteriores;
- transformar ausência em zero;
- inferir consolidação passada;
- atribuir revisão legada ao perfil;
- atribuir foco ao concurso;
- chamar variação de 1 ou 2 respostas de tendência.

Fixtures podem simular cenários ricos apenas nos testes.

---

## 35. RELATÓRIO

Crie:

`RELATORIO_PASSO_8_TENDENCIAS_TEMPORAIS_V2.md`

Inclua:

1. estado inicial;
2. causa da diferença documental 52,12% × valor atual;
3. auditoria de Histórico;
4. auditoria de Tendências;
5. duplicações encontradas;
6. responsabilidades finais de cada aba;
7. arquitetura temporal criada;
8. períodos oficiais;
9. comparação atual × anterior;
10. critérios de suficiência;
11. tendência oficial;
12. séries diárias;
13. revisões e linhagem;
14. foco global;
15. domínio legado;
16. domínio atual oficial;
17. persistência histórica futura;
18. schema do snapshot diário;
19. política de captura;
20. ausência de backfill;
21. disciplinas;
22. tópicos;
23. maior evolução/queda;
24. gráficos;
25. performance/SELECTs;
26. testes;
27. resultados no banco real;
28. status da fila sombra;
29. pendências;
30. recomendação para o Passo 9.

---

## 36. VALIDAÇÕES FINAIS

Execute:

- testes novos de tendências;
- `test_statistics_core.py`;
- `test_progresso_edital.py`;
- `test_fila_candidata.py`;
- `test_fila_observacao.py`;
- smoke tests;
- `py_compile`;
- lint direcionado;
- `git diff --check`;
- `PRAGMA integrity_check`;
- `PRAGMA foreign_key_check`;
- inicialização do programa;
- validação do checkpoint nativo.

---

## 37. CHECKPOINT

Ao concluir:

- incremente versão/build/schema somente se necessário;
- gere checkpoint completo;
- valide com `checkpoint.py`;
- confirme banco incluído;
- informe número total de testes aprovados;
- informe quantos snapshots temporais reais existem;
- informe quais comparações reais já são válidas;
- informe o gate atual da fila sombra.

---

# REGRA PRINCIPAL

Tendência não é decoração.

Uma seta para cima ou para baixo só pode existir quando a pergunta, o período,
a população e a amostra forem definidos e suficientes.

O VighnaStudy deve preferir:

`Dados insuficientes`

a apresentar uma conclusão temporal que os dados ainda não sustentam.

A Fila Inteligente V3 permanece a única fila decisória.
