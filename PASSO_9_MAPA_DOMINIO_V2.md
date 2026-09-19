# PASSO 9 — MAPA DE DOMÍNIO V2

Use como base obrigatória:

- `ESPECIFICACAO_TECNICA_NUCLEO_ESTATISTICO.md`
- `RELATORIO_VALIDACAO_NUCLEO_ESTATISTICO.md`
- `RELATORIO_PASSO_7_PROGRESSO_EDITAL_V2.md`
- `RELATORIO_PASSO_8_TENDENCIAS_TEMPORAIS_V2.md`
- implementação atual em `statistics_core/`
- `progresso_edital.py`
- `analise_temporal.py`
- aba `Disciplinas`
- aba `Pontos fracos`
- aba `Progresso`
- estrutura atual de `Estatísticas`

## CONTEXTO VALIDADO

O Passo 8 terminou com:

- versão `0.24.0`;
- build `tendencias-temporais-v2`;
- schema 18;
- 116 testes unittest aprovados;
- smoke test aprovado;
- `PRAGMA integrity_check = ok`;
- nenhuma violação de foreign key;
- checkpoint nativo completo e validado;
- Fila Inteligente V3 como única fila decisória;
- fila candidata somente em modo sombra;
- `used_for_queue_order = false`.

O banco real ainda possui pouca diversidade temporal para tendências fortes.

Isso NÃO impede a construção de um mapa atual de domínio, desde que:

- domínio;
- evidência;
- cobertura;
- consolidação;

permaneçam conceitos separados.

## OBJETIVO CENTRAL

Criar uma visão denominada:

`Mapa de domínio`

dentro da área de Estatísticas.

Ela deve responder:

1. Em quais disciplinas/tópicos já existe domínio mensurável?
2. Em quais o domínio ainda é provisório?
3. Onde ainda há evidência insuficiente?
4. Quais tópicos possuem evidência suficiente e domínio baixo?
5. Quais já estão consolidados?
6. Quais áreas ainda nem foram trabalhadas?

O mapa deve ser ANALÍTICO.

Ele não deve decidir a fila de estudos.

Arquitetura desejada:

NÚCLEO ESTATÍSTICO
↓
SNAPSHOT DO MAPA DE DOMÍNIO
↓
DISCIPLINAS + TÓPICOS
↓
INTERFACE

---

## 1. NÃO ALTERAR A FILA

Durante todo o Passo 9:

- V3 permanece ativa;
- candidata permanece sombra;
- `used_for_queue_order = false`;
- não alterar pesos;
- não alterar prioridade;
- não alterar recomendação;
- não alterar agenda;
- não alterar espaçamento.

O mapa não é um algoritmo de recomendação.

---

## 2. CRIE UMA ABA PRÓPRIA

Adicione uma aba:

`Mapa de domínio`

na área Estatísticas.

Posição sugerida:

`Disciplinas` → `Mapa de domínio` → `Pontos fracos`

ou outra posição coerente com a navegação atual.

Não remova nenhuma aba existente.

---

## 3. NÃO USE UM ÚNICO PERCENTUAL COMO “VERDADE”

O mapa deve manter visíveis as quatro dimensões:

- Domínio
- Evidência
- Cobertura
- Consolidação

Nunca use um único valor para substituir as quatro.

---

## 4. DOMÍNIO E EVIDÊNCIA DEVEM ANDAR JUNTOS

Um valor alto de domínio com evidência baixa não pode parecer tão confiável quanto um valor semelhante com evidência alta.

Exemplos conceituais:

`Domínio 88 • Evidência baixa • Provisório`

versus:

`Domínio 84 • Evidência alta`

A apresentação deve deixar essa diferença evidente.

---

## 5. TRATAMENTO DE `mastery_score = None`

Quando o Núcleo Estatístico retornar domínio não calculável:

NÃO mostrar:

- 0;
- 0%;
- domínio baixo;
- vermelho;
- fraco.

Mostrar algo equivalente a:

`Dados insuficientes`

ou:

`—`

acompanhado da evidência correspondente.

---

## 6. EVIDÊNCIA `low`

Quando existir `mastery_score` calculável com evidência baixa:

- o valor pode ser exibido;
- deve ficar claramente marcado como provisório;
- não deve ser usado para classificar o tópico como forte/fraco de maneira definitiva.

Centralize essa regra.

Não espalhe decisões de evidência pela UI.

---

## 7. EVIDÊNCIA `moderate` OU `high`

Esses níveis permitem interpretação mais forte do domínio atual.

Ainda assim:

- domínio atual não é garantia futura;
- consolidação continua sendo uma métrica separada;
- não inferir tendência temporal a partir do valor atual.

---

## 8. CRIE UM SNAPSHOT CENTRAL DO MAPA

Crie um módulo/helper coerente com a arquitetura.

Exemplo conceitual:

`mapa_dominio.py`

com estrutura como:

`DomainMapSnapshot`

Campos sugeridos:

- concurso_id;
- total_topics;
- unstarted_topics;
- insufficient_topics;
- low_evidence_topics;
- moderate_evidence_topics;
- high_evidence_topics;
- measurable_topics;
- consolidated_topics;
- disciplines;
- topics;
- generated_at;
- metric_version;
- snapshot_version.

Não persista esse snapshot nesta etapa.

Ele pode ser calculado sob demanda.

---

## 9. DADOS POR TÓPICO

Cada item de tópico deve conter, no mínimo:

- topic_id;
- subject_id;
- disciplina;
- tópico;
- mastery_score;
- mastery_state;
- evidence_level;
- coverage_rate;
- consolidation_status;
- total_attempts;
- unique_questions_answered;
- available_questions;
- review_count;
- last_activity_at;
- recent_performance;
- display_state.

Use os nomes reais da API oficial quando diferirem.

Não recalcule métricas acadêmicas no módulo do mapa.

---

## 10. ESTADO DE APRESENTAÇÃO

Crie um estado de APRESENTAÇÃO, separado das métricas oficiais.

Sugestão:

### Não iniciado
Sem tentativas efetivas.

### Dados insuficientes
Iniciado, mas sem domínio calculável ou sem evidência mínima.

### Provisório
Domínio calculável + evidência baixa.

### Mensurável
Domínio calculável + evidência moderada/alta.

### Consolidado
Somente quando `topic_consolidation_status == consolidated`.

Esse estado serve para UX.

Não substitui `evidence_level`, `mastery_score` ou `topic_consolidation_status`.

---

## 11. FAIXAS VISUAIS DE DOMÍNIO

Para tópicos MENSURÁVEIS, crie faixas visuais configuráveis.

Exemplo inicial:

- 0–49: domínio baixo;
- 50–69: domínio intermediário;
- 70–84: domínio bom;
- 85–100: domínio alto.

Essas faixas são apenas linguagem visual.

Não alteram a fórmula oficial.

Não use essas faixas para tópicos com evidência insuficiente.

Para evidência baixa, se houver faixa, marque-a explicitamente como provisória.

Centralize os limites em configuração/constantes do módulo do mapa.

---

## 12. CORES NÃO DEVEM ESCONDER INCERTEZA

Evite um heatmap em que um tópico com 100% em 1 questão fique verde intenso.

A intensidade visual deve considerar a confiabilidade.

Sugestão:

- `insufficient`: neutro/cinza;
- `low`: faixa visual suave + selo “Provisório”;
- `moderate/high`: cor da faixa de domínio completa;
- `consolidated`: badge/ícone separado.

Não altere globalmente o tema.

Use os padrões visuais existentes.

---

## 13. RESUMO SUPERIOR

No topo da aba, apresente cards compactos:

### Tópicos mensuráveis
Quantidade/percentual com domínio interpretável.

### Evidência suficiente
Moderada + Alta.

### Consolidados
Estado oficial.

### Sem base suficiente
Insuficiente + eventualmente não iniciados, deixando clara a composição.

Evite repetir o card completo de Progresso.

O objetivo aqui é leitura de domínio.

---

## 14. MAPA POR DISCIPLINA

Crie uma visão resumida por disciplina.

Para cada disciplina, mostrar quando disponível:

- domínio oficial da disciplina;
- evidência da disciplina;
- cobertura de tópicos;
- cobertura de questões;
- tópicos mensuráveis;
- tópicos consolidados;
- tópicos sem base.

Use `get_subject_metrics_batch`.

Não faça média simples dos tópicos.

---

## 15. MAPA POR TÓPICO

A visão principal deve permitir inspecionar tópicos.

Pode ser:

- tabela enriquecida;
- cards compactos;
- matriz por disciplina;

desde que continue legível com dezenas de tópicos.

Priorize precisão e navegação sobre efeitos visuais.

---

## 16. CAMPOS DA TABELA/MATRIZ

No mínimo:

- Disciplina;
- Tópico;
- Domínio;
- Evidência;
- Cobertura;
- Consolidação;
- Estado.

Quando útil:

- Tentativas;
- Questões únicas;
- Revisões;
- Última atividade.

Não sobrecarregue a primeira visualização.

Informações secundárias podem aparecer em tooltip/detalhe.

---

## 17. FILTROS

Adicionar filtros úteis:

- disciplina;
- estado de apresentação;
- evidência;
- faixa de domínio;
- consolidação;
- busca textual.

Filtros sugeridos:

### Evidência
- Todas
- Insuficiente
- Baixa
- Moderada
- Alta

### Estado
- Todos
- Não iniciado
- Dados insuficientes
- Provisório
- Mensurável
- Consolidado

### Domínio
- Todos
- Baixo
- Intermediário
- Bom
- Alto

A filtragem de domínio deve excluir silenciosamente tópicos sem domínio, salvo opção explícita.

---

## 18. ORDENAÇÃO

A ordem padrão deve ser curricular:

`Disciplina → Tópico`

Permita ordenação opcional por:

- domínio;
- evidência;
- cobertura;
- última atividade.

Não usar a ordem da Fila Inteligente como padrão.

---

## 19. “PONTOS FRACOS” NÃO É O MESMO QUE MAPA

Não duplique semanticamente a aba `Pontos fracos`.

O Mapa de Domínio deve mostrar TODO o universo.

A aba Pontos fracos pode continuar sendo uma visão filtrada/operacional.

Se houver lógica duplicada entre Pontos fracos e o novo snapshot, migre Pontos fracos para consumir o mesmo snapshot ou as mesmas métricas oficiais quando seguro.

Não altere seu comportamento deliberadamente sem documentar.

---

## 20. CRITÉRIO DE “DOMÍNIO BAIXO”

Somente classifique um tópico como domínio baixo quando:

- houver `mastery_score`;
- evidência for suficiente para interpretação forte, preferencialmente `moderate` ou `high`.

Com evidência `low`, use:

`domínio provisório baixo`

se precisar descrever.

Com `insufficient`, não classifique.

---

## 21. DISCIPLINA SEM BASE

Se uma disciplina não possuir base suficiente:

- não mostrar 0;
- não pintar como ruim;
- mostrar `Dados insuficientes`.

Se alguns tópicos tiverem dados e outros não, mostrar distribuição.

---

## 22. CONSOLIDAÇÃO

Consolidação deve vir somente do estado oficial.

Não inferir consolidado por:

- domínio alto isolado;
- 100% de acerto;
- grande número de questões;
- evidência alta isolada.

Mostrar consolidação como badge independente.

---

## 23. COBERTURA

Cobertura permanece separada de domínio.

Um tópico pode ter:

- cobertura alta + domínio baixo;
- cobertura baixa + domínio alto provisório;
- cobertura alta + evidência insuficiente;
- domínio alto + não consolidado.

A UI deve suportar essas combinações sem contradição.

---

## 24. ÚLTIMA ATIVIDADE

Use `last_activity_at` oficial.

Se não existir:

`Nunca estudado`

ou equivalente.

Não inferir data por revisão antiga sem linhagem quando o escopo for concurso.

---

## 25. HISTÓRICO TEMPORAL NO MAPA

Não crie ainda mini-gráficos de tendência por tópico.

O Passo 8 iniciou os snapshots futuros, mas ainda existe apenas uma base temporal inicial.

Se quiser mostrar evolução, só habilite quando houver pelo menos dois snapshots reais relevantes.

Nesta etapa, o Mapa de Domínio é principalmente um retrato atual confiável.

---

## 26. INTERAÇÃO

Duplo clique/click em tópico pode abrir a tela existente do tópico.

Não crie uma nova tela redundante de estudo.

Se já houver padrão de navegação usado em Disciplinas/Pontos fracos, reutilize-o.

---

## 27. PERFORMANCE

O mapa pode ter muitos tópicos.

Obrigatório:

- `get_topic_metrics_batch`;
- `get_subject_metrics_batch`;
- sem consulta individual por tópico;
- sem cálculo repetido por célula.

Meça SELECTs em fixture com muitos tópicos.

O crescimento não pode ser N+1 relevante.

---

## 28. CACHE

Pode reutilizar o cache analítico curto já existente na UI.

Não introduza cache persistente de domínio nesta etapa.

Dados oficiais continuam sendo derivados do Núcleo Estatístico.

---

## 29. DADOS REAIS ATUAIS

No checkpoint do Passo 8, o concurso ativo possui aproximadamente:

- 88 tópicos ativos;
- 259 questões ativas;
- 123 questões únicas respondidas;
- 1 tópico iniciado;
- evidência suficiente ainda muito limitada.

Recalcule esses valores no início.

Não os fixe.

É esperado que grande parte do mapa apareça como:

`Não iniciado`

ou:

`Dados insuficientes`.

Isso é comportamento correto.

---

## 30. ESTADO VAZIO

Se nenhum tópico tiver domínio mensurável:

NÃO mostrar mapa vazio como erro.

Mostrar mensagem equivalente:

`O mapa ficará mais detalhado conforme você acumular evidência em diferentes tópicos.`

Mas continue exibindo o universo de tópicos e seus estados.

---

## 31. TESTES

Crie:

`test_mapa_dominio.py`

Cobrir no mínimo:

A. edital sem tentativas;

B. tópico não iniciado;

C. tentativa única correta;

D. evidência insuficiente;

E. evidência baixa + domínio calculável;

F. evidência moderada;

G. evidência alta;

H. domínio `None`;

I. domínio igual a zero válido;

J. domínio baixo com evidência suficiente;

K. domínio alto com evidência baixa continua provisório;

L. consolidado oficial;

M. domínio alto não consolidado;

N. cobertura alta com domínio baixo;

O. cobertura baixa com domínio alto;

P. disciplina sem base;

Q. disciplina com volumes muito diferentes;

R. tópico sem questões ativas;

S. tópico pausado fora do universo;

T. última atividade ausente;

U. filtros por evidência;

V. filtros por estado;

W. filtros por domínio;

X. ordenação curricular;

Y. snapshot batch sem N+1;

Z. Fila V3 continua ativa.

---

## 32. INTEGRAÇÃO COM PONTOS FRACOS

Audite `Pontos fracos`.

Se ele classifica como fraco um tópico com evidência insuficiente, corrija.

Regra:

- evidência insuficiente → não classificar como fraco por domínio;
- evidência baixa → marcar provisório;
- moderate/high → classificação interpretável.

Não transforme esta etapa em redesenho completo de Pontos fracos.

---

## 33. INTEGRAÇÃO COM DISCIPLINAS

A aba Disciplinas deve continuar funcional.

Se existirem métricas duplicadas de domínio/evidência, faça-a consumir a mesma fonte oficial.

Não remova informações úteis.

---

## 34. DASHBOARD

Não adicione um grande mapa ao Dashboard.

Se houver necessidade de um acesso, no máximo:

- link/botão “Ver mapa de domínio”;
- pequeno resumo confiável.

Preserve o Dashboard compacto.

---

## 35. FILA SOMBRA

Ao final, confirme:

- V3 continua ativa;
- candidata continua sombra;
- `used_for_queue_order = false`;
- mapa não grava observação sombra por refresh;
- mapa não altera score;
- mapa não altera recomendação.

Informe o gate real atual.

---

## 36. VALIDAÇÕES

Execute:

- `test_mapa_dominio.py`;
- `test_analise_temporal.py`;
- `test_progresso_edital.py`;
- `test_statistics_core.py`;
- `test_fila_candidata.py`;
- `test_fila_observacao.py`;
- suíte unittest completa;
- smoke test;
- `py_compile`;
- lint direcionado disponível no ambiente;
- `git diff --check`;
- `PRAGMA integrity_check`;
- `PRAGMA foreign_key_check`;
- inicialização do programa;
- validação do checkpoint nativo.

Se alguma ferramenta não estiver disponível, documente explicitamente.

---

## 37. RELATÓRIO

Crie:

`RELATORIO_PASSO_9_MAPA_DOMINIO_V2.md`

Inclua:

1. estado inicial;
2. arquitetura criada;
3. definição do mapa;
4. estado de apresentação;
5. tratamento de domínio `None`;
6. política de evidência low;
7. faixas visuais;
8. disciplinas;
9. tópicos;
10. filtros;
11. ordenação;
12. consolidação;
13. cobertura;
14. última atividade;
15. integração com Pontos fracos;
16. integração com Disciplinas;
17. performance/SELECTs;
18. testes;
19. resultados no banco real;
20. distribuição de estados;
21. distribuição de evidência;
22. tópicos mensuráveis;
23. tópicos consolidados;
24. status da fila sombra;
25. pendências;
26. recomendação para o Passo 10.

---

## 38. CHECKPOINT

Ao concluir:

- incremente versão/build/schema somente se necessário;
- gere checkpoint completo;
- valide com `checkpoint.py`;
- confirme banco incluído;
- informe número de testes aprovados;
- informe status do gate sombra;
- informe explicitamente que V3 continua decidindo.

---

# REGRA PRINCIPAL

O Mapa de Domínio deve mostrar conhecimento e incerteza ao mesmo tempo.

Um número de domínio sem evidência não é informação suficiente.

Portanto:

`DOMÍNIO` nunca deve ser interpretado sem `EVIDÊNCIA`.

O VighnaStudy deve preferir mostrar:

`Dados insuficientes`

a pintar um tópico como fraco ou forte sem base.

A Fila Inteligente V3 permanece a única fila decisória.
