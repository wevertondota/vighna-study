# PASSO 7 — PROGRESSO DO EDITAL V2: COBERTURA, EVIDÊNCIA E CONSOLIDAÇÃO

Use como base obrigatória:

- `ESPECIFICACAO_TECNICA_NUCLEO_ESTATISTICO.md`
- `RELATORIO_VALIDACAO_NUCLEO_ESTATISTICO.md`
- `RELATORIO_PARIDADE_FILA_INTELIGENTE.md`
- `RELATORIO_PASSO_6_BLOQUEADORES_FILA.md`
- implementação atual em `statistics_core/`
- implementação atual da aba `Progresso`
- card `Progresso do edital` do Dashboard

## CONTEXTO VALIDADO

O Núcleo Estatístico já é a fonte oficial das métricas centrais.

A infraestrutura sombra da fila está pronta, mas o gate real ainda deve permanecer fechado enquanto faltar amostra.

A Fila Inteligente V3 continua sendo a única fila decisória.

O restante do desenvolvimento analítico pode avançar sem esperar a ativação da fila candidata, desde que respeite:

- `dados insuficientes`;
- nível de evidência;
- linhagem;
- separação entre cobertura, domínio e consolidação.

## OBSERVAÇÃO DE CONSISTÊNCIA DO CHECKPOINT

Antes de iniciar esta etapa, verifique uma divergência documental:

`RELATORIO_PASSO_6_BLOQUEADORES_FILA.md` registra 1 observação sombra real (`manual_audit`), porém o `estudos.db` incluído no checkpoint final contém 0 linhas em:

- `fila_shadow_execucoes`;
- `fila_shadow_itens`;
- `fila_shadow_fallbacks`.

Não fabrique a observação.

Determine apenas a causa.

Se a observação de auditoria foi removida intencionalmente antes do checkpoint, documente que o checkpoint inicia a coleta real em zero.

Se ela deveria ter sido preservada, corrija o processo responsável sem inserir dados artificiais.

Isso não deve alterar a fila ativa nem bloquear o restante deste passo.

---

## OBJETIVO CENTRAL

Transformar a aba `Progresso` em uma representação estatisticamente correta do estado do edital.

O usuário deve conseguir responder quatro perguntas diferentes:

1. Quanto do edital eu já comecei?
2. Quanto do edital já possui evidência suficiente para ser avaliado?
3. Quanto do edital está realmente consolidado?
4. Onde estão as maiores lacunas?

Essas perguntas NÃO devem ser condensadas em um único percentual.

Arquitetura conceitual:

EDITAL
↓
COBERTURA
↓
EVIDÊNCIA
↓
DOMÍNIO
↓
CONSOLIDAÇÃO

Cada dimensão deve permanecer semanticamente independente.

---

## 1. NÃO ALTERAR A FILA

Durante todo o Passo 7:

- V3 permanece ativa;
- candidata permanece sombra;
- `used_for_queue_order = false`;
- não alterar pesos;
- não alterar recomendação;
- não alterar espaçamento;
- não alterar agenda.

A observação sombra deve continuar acumulando normalmente durante o uso real.

---

## 2. AUDITE A ABA PROGRESSO ATUAL

Antes de editar, mapeie:

- cards existentes;
- tabela por disciplina;
- tabela por tópico;
- previsões existentes;
- filtros;
- fontes de cada valor;
- fórmulas ainda feitas diretamente na UI;
- textos que ainda descrevem conceitos antigos.

Identifique especialmente qualquer uso de:

- histórico de revisão como sinônimo de cobertura;
- média simples de percentuais;
- domínio sem evidência;
- consolidação inferida por regra visual;
- previsão produzida com base insuficiente.

---

## 3. CORRIJA A SEMÂNTICA DE COBERTURA

A especificação oficial define:

### Cobertura de tópicos

`topic_coverage_rate`

Representa a proporção de tópicos ativos com pelo menos uma tentativa efetiva.

### Cobertura de questões

`question_coverage_rate`

Representa a proporção de questões ativas já respondidas ao menos uma vez.

Não descreva cobertura como:

“tópicos com histórico de revisão”

se a métrica oficial utiliza tentativas efetivas.

Atualize textos, tooltips e descrições para refletir o conceito real.

---

## 4. INTRODUZA A DIMENSÃO “EVIDÊNCIA”

A aba Progresso deve exibir de forma clara quantos tópicos possuem:

- Insuficiente;
- Baixa;
- Moderada;
- Alta.

Crie também uma métrica derivada de apresentação:

`percentual_com_evidencia_suficiente`

onde “evidência suficiente para decisões fortes” significa:

`Moderada` ou `Alta`.

Essa métrica é de apresentação e deve ser calculada a partir dos estados oficiais por tópico.

Não altere `evidence_level@1`.

---

## 5. SEPARAÇÃO VISUAL PRINCIPAL

No topo da aba Progresso, priorize quatro indicadores:

### COBERTURA DO EDITAL
Percentual de tópicos iniciados conforme `topic_coverage_rate`.

### EVIDÊNCIA SUFICIENTE
Percentual de tópicos com evidência Moderada ou Alta.

### CONSOLIDADOS
Percentual de tópicos com `topic_consolidation_status = consolidated`.

### DOMÍNIO
Mostrar domínio global/oficial somente quando calculável.

Se o domínio não for calculável:

`Dados insuficientes`

ou apresentação equivalente já coerente com o design.

Não transformar `None` em `0`.

---

## 6. MOSTRE TAMBÉM COBERTURA DE QUESTÕES

A cobertura de tópicos e a cobertura de questões respondem perguntas diferentes.

Exemplo:

- 80% dos tópicos iniciados;
- apenas 34% das questões disponíveis já vistas.

Exiba ambas sem confundi-las.

Não use a quantidade absoluta de questões para dar peso curricular ao tópico.

---

## 7. ESTADOS DE TÓPICO

Preserve uma classificação operacional clara.

Sugestão:

### Não iniciado
Nenhuma tentativa efetiva.

### Em andamento
Já iniciado, mas ainda sem critérios suficientes para consolidação.

### Em consolidação
Estado visual intermediário, desde que explicitamente tratado como estado de acompanhamento e NÃO como métrica oficial de consolidação.

### Consolidado
Somente quando:

`topic_consolidation_status == consolidated`

### Dados insuficientes

Não precisa necessariamente ser um quinto “estado de progresso” se isso prejudicar a UX.

Porém a interface deve deixar claro quando domínio/consolidação ainda não podem ser certificados por falta de evidência.

Não trate `insufficient_data` como `not_consolidated`.

---

## 8. DEFINA FORMALMENTE “EM CONSOLIDAÇÃO”

A implementação atual usa uma regra intermediária para “Consolidando”.

Audite essa regra.

Se ela for mantida:

- documente-a;
- dê nome interno estável;
- deixe claro que é um estado de apresentação;
- não permita que ela seja confundida com `topic_consolidation_status@1`.

Não crie uma segunda fórmula de domínio.

Use somente dados oficiais do núcleo.

---

## 9. TABELA POR TÓPICO

Reorganize a tabela para que as informações mais úteis apareçam juntas.

Ela deve permitir visualizar, no mínimo:

- Disciplina;
- Tópico;
- Estado;
- Cobertura de questões;
- Evidência;
- Domínio;
- Revisões;
- Próxima revisão.

A importância pode continuar disponível se houver espaço e utilidade.

Se o domínio não for calculável, mostre `—`/`Dados insuficientes`, não `0`.

Se evidência for `low`, sinalize que o domínio é provisório quando aplicável.

---

## 10. FILTROS

Além dos filtros atuais, permitir quando adequado:

- estado;
- disciplina;
- evidência;
- busca textual.

Considere opções:

- Evidência insuficiente;
- Evidência baixa;
- Evidência moderada;
- Evidência alta.

O objetivo é permitir localizar rapidamente conteúdos que precisam de mais amostra.

---

## 11. PROGRESSO POR DISCIPLINA

A tabela por disciplina deve deixar de depender de simples contagens manuais quando existir métrica oficial de disciplina.

Para cada disciplina, calcule/obtenha corretamente:

- quantidade de tópicos;
- cobertura de tópicos;
- cobertura de questões;
- percentual de tópicos com evidência suficiente;
- tópicos consolidados;
- domínio da disciplina, quando calculável.

Nunca faça:

`média simples dos domínios dos tópicos`

ou:

`média simples das taxas de acerto`.

Use o escopo de disciplina do `StatisticsService`.

---

## 12. AGREGAÇÃO CORRETA

Quando uma métrica existir oficialmente em nível de disciplina/perfil, use-a.

Quando for uma distribuição de estados de tópicos, agregue estados por tópico.

Não crie fórmulas duplicadas dentro de `main.py`.

Se faltar uma estrutura agregada de apresentação, crie um serviço/helper de progresso fora da UI, reutilizando o Núcleo Estatístico.

---

## 13. CRIE UM SNAPSHOT DE PROGRESSO

Crie uma estrutura interna única, conceitualmente semelhante a:

`SyllabusProgressSnapshot`

com:

- concurso_id;
- total_topics;
- started_topics;
- topic_coverage_rate;
- question_coverage_rate;
- insufficient_evidence_topics;
- low_evidence_topics;
- moderate_evidence_topics;
- high_evidence_topics;
- sufficient_evidence_topics;
- sufficient_evidence_rate;
- consolidated_topics;
- consolidated_rate;
- global_mastery_score;
- disciplinas;
- topicos;
- generated_at.

O nome e formato devem respeitar a arquitetura do projeto.

Dashboard e aba Progresso devem consumir o mesmo snapshot sempre que possível.

---

## 14. NÃO PERSISTIR SNAPSHOT SEM NECESSIDADE

Esse snapshot pode ser calculado sob demanda.

Não crie uma tabela histórica de progresso nesta etapa.

Histórico/séries temporais serão tratados posteriormente.

---

## 15. CARD DO DASHBOARD

O card `Progresso do edital` deve permanecer compacto.

Ele não precisa mostrar todos os detalhes da aba.

Priorize algo como:

- cobertura;
- consolidados;
- evidência suficiente;
- acesso para “Ver progresso”.

Não sobrecarregue o Dashboard.

Preserve a identidade visual atual dos cards.

---

## 16. PREVISÃO DO EDITAL

A aba atual possui previsões de ritmo.

Essas previsões NÃO podem apresentar falsa precisão.

Audite:

- “100% iniciado”;
- “80% consolidado”;
- “100% consolidado”;
- cenários por semana.

Para cada previsão, defina base mínima de dados confiáveis.

Quando a base não for suficiente, mostre:

`Dados insuficientes para previsão`

em vez de estimar uma data.

Não projete consolidação a partir de registros cuja data/linhagem não seja comprovável.

---

## 17. NÃO TRATE UMA PREVISÃO COMO META OU GARANTIA

Qualquer previsão deve informar:

- janela utilizada;
- quantidade de eventos válidos;
- período observado;
- que é uma extrapolação.

Não exiba casas decimais ou datas precisas se a base estatística não justificar isso.

---

## 18. LACUNAS DO EDITAL

Crie uma seção ou visão compacta de lacunas baseada em critérios objetivos.

Exemplos:

- não iniciado;
- iniciado com evidência insuficiente;
- evidência baixa;
- não consolidado com evidência suficiente;
- revisão vencida.

Não transforme isso em um novo algoritmo de prioridade.

É análise, não recomendação.

---

## 19. ORDEM DOS TÓPICOS

A ordem padrão da tabela de progresso pode priorizar legibilidade curricular, por exemplo:

Disciplina → Tópico

ou estado/lacuna quando o usuário selecionar um filtro.

Não reutilize a ordem da Fila Inteligente como se fosse “progresso”.

---

## 20. DADOS INSUFICIENTES

Revise todos os componentes da aba.

Ausência de dados não deve aparecer como:

- domínio 0;
- evidência 0;
- consolidação 0 por certeza;
- previsão de data;
- queda;
- estabilidade.

Use estados explícitos de insuficiência.

---

## 21. PERFORMANCE

A aba pode possuir muitos tópicos.

Evite N+1.

Obtenha métricas em lote para:

- tópicos;
- disciplinas;
- resumo global.

O número de SELECTs deve crescer pouco ou idealmente permanecer aproximadamente constante com o número de tópicos.

---

## 22. TESTES

Crie testes para, no mínimo:

A. edital sem tentativas;

B. tópico iniciado com 1 resposta;

C. tópico com evidência baixa;

D. tópico com evidência moderada;

E. tópico com evidência alta;

F. tópico oficialmente consolidado;

G. `insufficient_data` sem virar `not_consolidated`;

H. disciplina com tópicos de volumes muito diferentes;

I. cobertura de tópicos diferente de cobertura de questões;

J. domínio `None`;

K. disciplina sem domínio calculável;

L. previsão sem base suficiente;

M. previsão com base suficiente em fixture controlada;

N. tópicos sem questões ativas;

O. tópicos pausados/inativos fora do universo;

P. mesmo snapshot usado por Dashboard e aba Progresso;

Q. ausência de N+1 relevante.

---

## 23. VERIFICAÇÃO DA FILA SOMBRA

Ao final do trabalho, confirme novamente:

- V3 continua ativa;
- candidata continua sombra;
- `used_for_queue_order = false`;
- telemetria continua separada;
- nenhuma mudança de Progresso alterou ordem/recomendação.

Informe também o gate real atual, sem fabricar observações.

---

## 24. RELATÓRIO

Crie:

`RELATORIO_PASSO_7_PROGRESSO_EDITAL_V2.md`

Inclua:

1. estado inicial;
2. divergência documental da observação sombra e causa encontrada;
3. arquitetura do snapshot de progresso;
4. definição de cobertura usada;
5. cobertura de tópicos;
6. cobertura de questões;
7. evidência;
8. consolidação;
9. domínio;
10. regra de “Em consolidação”;
11. agregação por disciplina;
12. mudanças no Dashboard;
13. mudanças na aba Progresso;
14. filtros;
15. tratamento de dados insuficientes;
16. auditoria das previsões;
17. critérios mínimos de previsão;
18. lacunas do edital;
19. performance/consultas;
20. testes;
21. status da fila sombra;
22. status atual do gate;
23. pendências;
24. recomendação para o próximo passo.

---

## 25. VALIDAÇÕES FINAIS

Execute:

- testes novos do progresso;
- `test_statistics_core.py`;
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

## 26. CHECKPOINT

Ao concluir:

- incremente versão/build/schema somente se realmente necessário;
- gere checkpoint completo;
- valide com `checkpoint.py`;
- confirme banco incluído;
- informe número total de testes aprovados;
- informe o gate atual da fila sombra.

---

# REGRA PRINCIPAL

O Passo 7 deve tornar o progresso do edital informativo sem fingir certeza.

O usuário precisa enxergar separadamente:

COBERTURA
≠
EVIDÊNCIA
≠
DOMÍNIO
≠
CONSOLIDAÇÃO

Nenhum percentual único deve esconder essas diferenças.

A Fila Inteligente V3 permanece a única fila decisória.
