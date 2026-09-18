# PASSO 6 — RESOLUÇÃO DOS BLOQUEADORES DA FILA E OBSERVAÇÃO SOMBRA CONTROLADA

Use como base obrigatória:

- `RELATORIO_AUDITORIA_NUCLEO_ESTATISTICO.md`
- `ESPECIFICACAO_TECNICA_NUCLEO_ESTATISTICO.md`
- `RELATORIO_IMPLEMENTACAO_NUCLEO_ESTATISTICO.md`
- `RELATORIO_VALIDACAO_NUCLEO_ESTATISTICO.md`
- `RELATORIO_PARIDADE_FILA_INTELIGENTE.md`
- `PASSO5_SNAPSHOT_PARIDADE.json`
- implementação atual em `statistics_core/`
- `fila_candidata.py`
- Fila Inteligente V3 ativa
- Motor de Recomendação V4/V5

## CONTEXTO VALIDADO DO PASSO 5

O Passo 5 terminou classificado como:

`PRONTO COM BLOQUEADORES ESPECÍFICOS`

A Fila Inteligente V3 continua sendo a fila decisória.

A candidata `fila_candidate_shadow_v1` permanece em modo sombra.

Na amostra real validada:

- 6 tópicos elegíveis foram comparados;
- 6/6 mantiveram a mesma posição;
- Top 1, Top 3 e Top 5 tiveram 100% de interseção;
- 5 tópicos possuíam evidência `insufficient`;
- 1 tópico possuía evidência `low`;
- não havia tópicos elegíveis com evidência `moderate` ou `high`;
- ocorreu uma divergência esperada de score no tópico 23;
- não ocorreu divergência inesperada;
- foram utilizados fallbacks por insuficiência de domínio, tendência e linhagem de revisões.

Os bloqueadores identificados foram:

1. pouca amostra real com evidência moderada/alta;
2. revisões históricas sem linhagem inequívoca de concurso/perfil;
3. necessidade de uma janela controlada maior de observação sombra;
4. necessidade de política explícita para `mastery_score` com evidência `low`.

## OBJETIVO

Resolver os bloqueadores técnicos que podem ser resolvidos agora e preparar uma observação sombra real, segura e acumulável.

Esta etapa NÃO ativa a fila candidata.

Arquitetura desejada:

FILA V3 ATIVA
        ↓ decisão real

NÚCLEO ESTATÍSTICO
        ↓
FILA CANDIDATA SOMBRA
        ↓
TELEMETRIA DE PARIDADE
        ↓
GATE DE PRONTIDÃO
        ↓
FUTURA DECISÃO DE MIGRAÇÃO

A regra permanece:

`used_for_queue_order = false`

para toda a candidata.

---

## 1. PRÉ-VOO

Antes de alterar o código:

1. leia integralmente `RELATORIO_PARIDADE_FILA_INTELIGENTE.md`;
2. confirme no código que a V3 continua decidindo;
3. confirme que V4/V5 não consomem `score_candidate`;
4. confirme os quatro bloqueadores acima;
5. registre o estado atual dos testes;
6. crie um baseline do schema de `revisoes`.

Não faça nenhuma alteração visual nesta etapa.

---

## 2. MIGRAÇÃO ADITIVA DE LINHAGEM EM `revisoes`

Adicionar à tabela `revisoes`:

`concurso_id INTEGER NULL`

A migração deve ser:

- aditiva;
- compatível com bancos antigos;
- idempotente;
- segura;
- sem retropreenchimento por inferência;
- sem alterar registros históricos existentes.

Registros históricos sem linhagem devem permanecer:

`concurso_id = NULL`

e continuar semanticamente tratados como:

`legacy_limited`

quando o cálculo depender do perfil/concurso.

---

## 3. CHAVE E ÍNDICE

Se a arquitetura atual permitir com segurança:

- adicionar referência lógica/foreign key para `concursos(id)` em bancos novos;
- criar índice para `revisoes(concurso_id, topico_id, data)` ou equivalente adequado;
- preservar compatibilidade com bancos SQLite existentes.

Não recrie a tabela de forma destrutiva apenas para adicionar uma foreign key.

Se SQLite impedir uma FK retroativa segura por `ALTER TABLE`, documente e mantenha o vínculo validado por aplicação + índice nesta versão.

---

## 4. TODA NOVA REVISÃO DEVE TENTAR REGISTRAR LINHAGEM

Mapeie todos os caminhos que criam ou consolidam revisões, incluindo no mínimo:

- revisão manual;
- revisão automática por questões internas;
- sessão de estudo/revisão;
- fluxos do Dashboard;
- fluxos do recomendador;
- qualquer importação ou rotina auxiliar que grave `revisoes`.

Quando o contexto possuir concurso/perfil inequívoco, grave:

`concurso_id`

Nunca derive concurso apenas a partir do tópico se o mesmo tópico puder participar de múltiplos concursos.

---

## 5. COMPATIBILIDADE DAS ASSINATURAS

Funções existentes, como conceitualmente:

`registrar_revisao(...)`

e

`salvar_revisao_automatica_questoes(...)`

podem receber `concurso_id=None` de forma compatível.

Não quebre chamadas antigas.

Quando `concurso_id` não estiver disponível de forma inequívoca:

- grave `NULL`;
- não invente;
- mantenha o estado limitado explicitamente.

---

## 6. LEITURA DAS REVISÕES PELO NÚCLEO ESTATÍSTICO

Atualize o `statistics_core` para diferenciar:

### A. REVISÃO COM LINHAGEM CONFIRMADA

`revisoes.concurso_id = concurso_id analisado`

Pode participar normalmente de métricas por perfil/concurso.

### B. REVISÃO HISTÓRICA SEM LINHAGEM

`revisoes.concurso_id IS NULL`

Não deve ser atribuída silenciosamente ao concurso atual.

Pode ser exposta como:

`legacy_limited`

quando necessário para compatibilidade/diagnóstico.

### C. REVISÃO DE OUTRO CONCURSO

Não pode contaminar métricas específicas do concurso atual.

---

## 7. TESTE O HISTÓRICO MISTO

Crie fixture com:

- revisões antigas `concurso_id = NULL`;
- revisões novas do concurso A;
- revisões novas do concurso B;
- mesmo tópico associado a mais de um concurso.

Valide que:

- concurso A vê somente o que possui linhagem A como oficial;
- concurso B vê somente o que possui linhagem B como oficial;
- registros NULL permanecem limitados;
- nenhum registro antigo é reatribuído.

---

## 8. POLÍTICA OFICIAL PARA EVIDÊNCIA `low`

Adote, para qualquer futura ativação da fila candidata, a política conservadora:

### `insufficient`

`mastery_score` não participa como valor ativo certificado.

Usar fallback seguro.

### `low`

O valor oficial pode ser calculado e observado em sombra, mas NÃO deve substituir sozinho o domínio legado em uma futura fila ativa.

Marcar como:

`provisional_low_evidence`

### `moderate`

O `mastery_score` passa a ser elegível para uso ativo.

### `high`

O `mastery_score` é elegível para uso ativo.

Essa política deve ficar centralizada/configurável e testável.

Não espalhe `if evidence == ...` por múltiplos arquivos.

---

## 9. PRESERVE UMA VISÃO EXPLORATÓRIA E UMA VISÃO ELEGÍVEL

A observação sombra deve poder registrar:

### CANDIDATO EXPLORATÓRIO

Usa `mastery_score` low conforme o Passo 5 para observar impacto potencial.

### CANDIDATO ELEGÍVEL PARA ATIVAÇÃO

Aplica a política conservadora:

- `insufficient` → fallback;
- `low` → fallback/provisório;
- `moderate/high` → oficial.

Isso permite comparar o efeito da fórmula nova sem confundir experimentação com prontidão para produção.

Nenhuma das duas versões decide a fila real nesta etapa.

---

## 10. CRIE UM GATE DE PRONTIDÃO

Implemente um objeto/função central que avalie se a candidata está tecnicamente elegível para futura migração.

Exemplo conceitual:

`evaluate_queue_activation_readiness(...)`

O retorno deve incluir:

- `ready: bool`;
- bloqueadores;
- avisos;
- quantidade de observações;
- quantidade de dias distintos;
- tópicos distintos;
- quantidade de observações com evidência moderate/high;
- divergências inesperadas;
- fallbacks por tipo;
- integridade de linhagem das novas revisões;
- versão da fila;
- versão das métricas.

Esse gate NÃO ativa nada.

Ele apenas informa prontidão.

---

## 11. CRITÉRIOS MÍNIMOS INICIAIS DE OBSERVAÇÃO

Use critérios conservadores e configuráveis.

Sugestão inicial:

- pelo menos 20 observações sombra significativas;
- distribuídas por pelo menos 5 dias distintos;
- pelo menos 5 tópicos distintos;
- pelo menos 10 observações de tópico com evidência `moderate` ou `high`;
- zero divergência inesperada não resolvida no Top 3;
- zero violação da proteção temporal;
- zero caso em que a candidata alteraria elegibilidade de tópico pausado/inativo;
- novas revisões com contexto conhecido registrando corretamente `concurso_id`.

Esses números são parâmetros de segurança da primeira versão, não verdades estatísticas universais.

Centralize-os em configuração/teste.

---

## 12. O QUE É UMA OBSERVAÇÃO SOMBRA SIGNIFICATIVA

Não grave telemetria toda vez que uma tela apenas redesenhar ou atualizar.

Considere significativa uma avaliação associada a um evento real, por exemplo:

- usuário iniciou uma sessão recomendada;
- usuário acionou explicitamente “Estudar agora”;
- auditoria manual explícita;
- snapshot técnico explicitamente solicitado.

Evite gerar dezenas de snapshots idênticos por refresh de interface.

---

## 13. PERSISTÊNCIA DE TELEMETRIA

Implemente persistência mínima e separada das estatísticas acadêmicas.

Preferencialmente crie tabelas próprias de auditoria, por exemplo:

### `fila_shadow_execucoes`

Campos conceituais:

- id;
- concurso_id;
- criada_em;
- evento_origem;
- active_queue_version;
- candidate_queue_version;
- metric_version;
- topics_evaluated;
- same_position_rate;
- top1_match;
- top3_intersection_rate;
- top5_intersection_rate;
- mean_absolute_position_delta;
- unexpected_divergence_count;
- fallback_component_count;
- moderate_high_topic_count;
- used_for_queue_order.

### `fila_shadow_itens`

Campos conceituais:

- execucao_id;
- topico_id;
- active_position;
- candidate_position;
- active_score;
- candidate_score;
- eligible_candidate_score;
- evidence_level;
- fallback_count;
- unexpected_divergence;
- principal_difference;
- active_main_reason;
- candidate_main_reason.

Adapte à arquitetura real.

Não salve estruturas JSON gigantes se campos relacionais simples forem suficientes.

---

## 14. TELEMETRIA NÃO É HISTÓRICO ACADÊMICO

As tabelas de sombra:

- não contam como sessão;
- não contam como tentativa;
- não contam como revisão;
- não afetam domínio;
- não afetam cobertura;
- não afetam sequência;
- não afetam gamificação;
- não afetam próxima revisão.

O `statistics_core` deve ignorá-las para métricas acadêmicas.

---

## 15. DEDUPLICAÇÃO

Evite duplicação de observações equivalentes.

Quando adequado, use assinatura baseada em:

- concurso;
- evento;
- conjunto/ordem dos tópicos;
- versões;
- janela temporal curta.

Não descarte observações genuinamente diferentes.

Documente a regra.

---

## 16. FALHAS DE TELEMETRIA NÃO PODEM QUEBRAR O ESTUDO

Se a gravação sombra falhar:

- a fila V3 continua funcionando;
- a sessão continua;
- o usuário não perde a ação;
- registrar erro técnico de forma apropriada;
- não alterar score nem fallback da fila ativa.

Telemetria é secundária à operação principal.

---

## 17. SUMÁRIO DE OBSERVAÇÃO

Crie função de leitura/agregação para responder:

- quantas observações existem;
- período coberto;
- dias distintos;
- tópicos distintos;
- níveis de evidência observados;
- proporção de posições iguais;
- interseção Top 1/3/5;
- divergências esperadas;
- divergências inesperadas;
- fallbacks mais frequentes;
- quantas novas revisões possuem linhagem completa;
- status do gate de prontidão.

Não crie ainda dashboard visual para isso.

Pode ser relatório técnico/estrutura de dados.

---

## 18. DIVERGÊNCIA INESPERADA

Centralize a definição de divergência inesperada.

No mínimo, trate como bloqueadora:

- diferença de cobertura quando o universo é equivalente;
- mudança em atraso operacional;
- mudança em importância;
- mudança em espaçamento sem alteração de regra;
- inclusão de tópico inelegível;
- exclusão de tópico elegível sem regra documentada;
- violação da proteção de revisão vencida/hoje;
- diferença não classificada no Top 3.

Não considere automaticamente divergência de fórmula de domínio como erro se estiver classificada e esperada.

---

## 19. PROTEÇÃO TEMPORAL

Reexecute fixtures de:

- revisão vencida;
- revisão hoje;
- revisão futura;
- sem próxima revisão.

Confirme que nenhuma política nova de evidência reduz ou apaga a urgência operacional.

---

## 20. TESTE DE LINHAGEM EM NOVAS REVISÕES

Crie testes que confirmem:

- nova revisão manual com concurso conhecido grava concurso;
- nova revisão automática com concurso conhecido grava concurso;
- revisão sem contexto inequívoco permanece NULL;
- atualização/consolidação não troca concurso existente por outro;
- concursos diferentes não compartilham revisão oficial indevidamente.

---

## 21. BANCO ANTIGO

Teste abertura de banco anterior à coluna `concurso_id`.

A inicialização deve:

- adicionar a coluna sem perder dados;
- preservar revisões existentes;
- manter integridade;
- continuar permitindo backup/restauração.

---

## 22. CHECKPOINT E BACKUP

Confirme que:

- checkpoint inclui o schema atualizado;
- restauração continua válida;
- `checkpoint_manifest.json` continua sendo autoridade;
- nenhuma tabela de telemetria é necessária para reconstruir métricas acadêmicas.

A telemetria pode ser preservada no backup/checkpoint, mas deve continuar conceitualmente separada.

---

## 23. NÃO ATIVAR A FILA CANDIDATA

Durante todo o Passo 6:

NÃO:

- trocar `score_fila` por `score_candidate`;
- usar `candidate_position` na interface;
- alterar Top 1;
- alterar “Estudar agora”;
- alterar recomendação final;
- alterar pesos ativos;
- alterar agenda;
- alterar espaçamento;
- remover V3;
- chamar a candidata de fila oficial.

Preserve:

`used_for_queue_order = false`

---

## 24. NÃO ESPERE ARTIFICIALMENTE DADOS MODERATE/HIGH

Não fabrique histórico no banco real para satisfazer o gate.

Fixtures podem simular os estados para testes.

Dados reais moderate/high devem surgir do uso real do sistema.

Se ao final do Passo 6 o gate real continuar `ready = false` por pouca amostra, isso é resultado correto.

---

## 25. NÃO BLOQUEIE O RESTANTE DO DESENVOLVIMENTO

A falta de amostra suficiente impede apenas a ATIVAÇÃO da fila candidata.

Ela não deve impedir o desenvolvimento posterior de:

- progresso do edital;
- tendências;
- mapa de domínio;
- comparações temporais;

desde que essas telas respeitem `dados insuficientes` e consumam o Núcleo Estatístico oficial.

---

## 26. TESTES

Amplie os testes para cobrir:

- migração aditiva de `revisoes.concurso_id`;
- banco legado;
- histórico misto;
- concursos A/B;
- política `insufficient`;
- política `low`;
- política `moderate`;
- política `high`;
- candidato exploratório;
- candidato elegível;
- gate ready false por pouca amostra;
- gate bloqueado por divergência inesperada;
- gate bloqueado por proteção temporal;
- gate pronto em fixture suficiente;
- persistência de telemetria;
- deduplicação;
- falha de persistência sem afetar V3;
- nenhum efeito acadêmico das tabelas sombra;
- V4/V5 continuam sem consumir candidata;
- `used_for_queue_order = false`.

---

## 27. VALIDAÇÕES FINAIS

Execute:

- suíte completa de testes;
- `test_fila_candidata.py`;
- `test_statistics_core.py`;
- `testes_smoke.py`;
- `py_compile`;
- lint direcionado;
- `git diff --check`;
- `PRAGMA integrity_check`;
- `PRAGMA foreign_key_check`;
- inicialização do programa;
- validação do checkpoint nativo.

---

## 28. RELATÓRIO

Crie:

`RELATORIO_PASSO_6_BLOQUEADORES_FILA.md`

Inclua:

1. estado inicial;
2. bloqueadores vindos do Passo 5;
3. migração de `revisoes.concurso_id`;
4. caminhos de gravação atualizados;
5. tratamento do histórico legado;
6. política oficial de evidência low;
7. candidato exploratório;
8. candidato elegível;
9. arquitetura da telemetria;
10. regra de observação significativa;
11. deduplicação;
12. gate de prontidão;
13. critérios configurados;
14. fixtures;
15. testes de linhagem;
16. testes de evidência;
17. proteção temporal;
18. integração V4/V5;
19. resultado no banco real;
20. quantidade real atual de observações;
21. distribuição de evidência real;
22. divergências inesperadas;
23. fallbacks;
24. status real do gate;
25. riscos restantes;
26. recomendação de continuidade.

---

## 29. CLASSIFICAÇÃO FINAL

Ao final, classifique:

### A. INFRAESTRUTURA PRONTA / AMOSTRA AINDA INSUFICIENTE

Esperado caso os bloqueadores técnicos tenham sido resolvidos, mas ainda faltem dados reais.

### B. PRONTO PARA PROPOR MIGRAÇÃO CONTROLADA

Somente se o gate real estiver satisfeito.

### C. BLOQUEADORES TÉCNICOS RESTANTES

Liste exatamente quais.

Não ative a fila em nenhuma dessas categorias neste passo.

---

## 30. CHECKPOINT

Ao concluir:

- gere novo checkpoint completo;
- valide-o por `checkpoint.py`;
- confirme banco incluído;
- confirme integridade;
- informe versão do VighnaStudy;
- informe status do gate de prontidão;
- informe explicitamente que a V3 permanece ativa.

---

# REGRA PRINCIPAL

O objetivo do Passo 6 é transformar os bloqueadores do Passo 5 em condições observáveis, seguras e mensuráveis.

Não force o sistema a parecer pronto.

Se faltarem dados reais, o resultado correto é:

`INFRAESTRUTURA PRONTA / AMOSTRA AINDA INSUFICIENTE`

A Fila Inteligente V3 deve continuar decidindo o que o usuário estudará.
