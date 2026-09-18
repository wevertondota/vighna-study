# PASSO 4 — VALIDAÇÃO DO NÚCLEO ESTATÍSTICO E MIGRAÇÃO CONTROLADA DOS CONSUMIDORES

Use como base obrigatória:

- RELATORIO_AUDITORIA_NUCLEO_ESTATISTICO.md
- ESPECIFICACAO_METRICAS_VIGHNA.md
- RELATORIO_IMPLEMENTACAO_NUCLEO_ESTATISTICO.md

## OBJETIVO

Validar de forma independente o Núcleo Estatístico recém-implementado antes de conectá-lo definitivamente às partes críticas do VighnaStudy.

Nesta etapa, o foco é:

DADOS CONTROLADOS
↓
NÚCLEO ESTATÍSTICO
↓
RESULTADOS ESPERADOS
↓
COMPARAÇÃO COM RESULTADOS REAIS
↓
MIGRAÇÃO SEGURA DOS CONSUMIDORES

A fila inteligente ainda NÃO deve ter sua lógica alterada.

O objetivo desta etapa é poder afirmar:

“O Núcleo Estatístico produz resultados coerentes, reproduzíveis e confiáveis, e os consumidores não críticos já utilizam a mesma fonte de verdade.”

---

## 1. AUDITE O QUE FOI IMPLEMENTADO NO PASSO 3

Antes de modificar qualquer coisa, leia integralmente:

RELATORIO_IMPLEMENTACAO_NUCLEO_ESTATISTICO.md

Verifique:

- quais métricas foram realmente centralizadas;
- quais consumidores já foram migrados;
- quais continuam utilizando cálculos antigos;
- quais diferenças entre cálculo antigo e novo foram encontradas;
- quais pendências ficaram registradas;
- quais testes já existem;
- quais riscos foram identificados.

Não presuma que o Passo 3 foi executado exatamente como planejado. Confirme no código.

---

## 2. CRIE UMA MATRIZ DE VALIDAÇÃO

Monte uma matriz explícita para cada métrica oficial relevante.

Inclua no mínimo:

- total_attempts
- correct_attempts
- incorrect_attempts
- unique_questions_answered
- accuracy_rate
- session_count
- review_count
- mastery_score
- evidence_level
- coverage_rate
- recent_performance
- last_activity_at

Para cada métrica, registre:

- dados de entrada;
- resultado esperado;
- resultado produzido;
- status: OK / divergente;
- origem da divergência, se houver.

---

## 3. USE CENÁRIOS CONTROLADOS

Crie dados de teste determinísticos para validar o comportamento do núcleo.

Inclua obrigatoriamente os seguintes cenários.

### CENÁRIO A — SEM DADOS

Tópico existente, mas sem tentativas.

Verifique:

- total_attempts = 0;
- correct_attempts = 0;
- incorrect_attempts = 0;
- unique_questions_answered = 0;
- ausência de divisão por zero;
- comportamento de accuracy_rate;
- comportamento de mastery_score;
- evidence_level adequado;
- coverage_rate coerente;
- recent_performance sem inventar tendência.

### CENÁRIO B — UMA QUESTÃO CORRETA

Uma questão respondida uma única vez corretamente.

Valide todas as métricas.

Atenção especial para:

- taxa de acerto;
- domínio;
- evidência.

100% de acerto não deve automaticamente significar domínio confiável.

### CENÁRIO C — UMA QUESTÃO INCORRETA

Uma tentativa incorreta.

Valide o comportamento correspondente.

### CENÁRIO D — MESMA QUESTÃO REPETIDA

Questão A:

- tentativa 1: erro;
- tentativa 2: erro;
- tentativa 3: acerto;
- tentativa 4: acerto.

Confirme a distinção entre:

- 4 tentativas;
- 1 questão única;
- 2 acertos;
- 2 erros;
- último resultado;
- desempenho recente.

### CENÁRIO E — VÁRIAS QUESTÕES

Crie várias questões no mesmo tópico com mistura de acertos e erros.

Valide:

- contagens;
- taxa;
- domínio;
- evidência;
- cobertura.

### CENÁRIO F — VÁRIAS SESSÕES

Distribua as tentativas entre sessões diferentes.

Valide:

- session_count;
- last_activity_at;
- evidência;
- desempenho recente.

### CENÁRIO G — ALTO ACERTO, BAIXA EVIDÊNCIA

Poucas tentativas com alta taxa de acerto.

O sistema deve conseguir produzir algo conceitualmente semelhante a:

Domínio alto ou promissor
+
Evidência insuficiente/baixa

sem transformar poucos dados em certeza.

### CENÁRIO H — ALTO ACERTO, ALTA EVIDÊNCIA

Muitas tentativas, várias questões e várias sessões, com desempenho consistente.

Compare com o cenário G.

### CENÁRIO I — QUEDA RECENTE

Crie histórico antigo bom e resultados recentes ruins.

Valide recent_performance.

### CENÁRIO J — RECUPERAÇÃO

Crie histórico ruim seguido de desempenho recente melhor.

Valide recent_performance e mastery_score conforme a especificação.

### CENÁRIO K — QUESTÃO ARQUIVADA

Registre tentativas e depois arquive a questão.

Verifique se o histórico estatístico que deve ser preservado continua existindo.

### CENÁRIO L — QUESTÃO NA LIXEIRA

Repita a validação considerando o comportamento definido pelo projeto para lixeira.

### CENÁRIO M — QUESTÃO RESTAURADA

Verifique se restaurar uma questão não duplica histórico ou altera indevidamente contagens.

### CENÁRIO N — DISCIPLINA COM VOLUMES DIFERENTES

Tópico A:
- 1 tentativa
- 100% de acerto

Tópico B:
- 99 tentativas
- 50% de acerto

Confirme que a disciplina NÃO apresenta 75% por média simples das taxas dos tópicos.

A agregação deve seguir a especificação oficial.

### CENÁRIO O — PERÍODOS

Crie dados em:

- hoje;
- últimos 7 dias;
- últimos 30 dias;
- período anterior equivalente;
- fora desses períodos.

Confirme os limites temporais exatamente.

---

## 4. VERIFIQUE AS FÓRMULAS

Para cada métrica derivada, valide matematicamente os resultados.

Em especial:

- accuracy_rate;
- mastery_score;
- evidence_level;
- coverage_rate;
- recent_performance.

Se o valor calculado divergir da especificação:

1. identifique se o erro está no código ou na especificação;
2. não altere silenciosamente a fórmula;
3. documente a decisão;
4. corrija somente após determinar a fonte da divergência.

---

## 5. VERIFIQUE DADOS INSUFICIENTES

Garanta que o núcleo saiba diferenciar:

- zero dados;
- poucos dados;
- dados suficientes.

Não permita que ausência de dados seja apresentada como:

- 0% de domínio;
- 0% de desempenho;
- queda;
- estabilidade;
- consolidação;

quando semanticamente o resultado correto for “dados insuficientes”.

---

## 6. VALIDE DOMÍNIO E EVIDÊNCIA SEPARADAMENTE

Confirme que:

mastery_score

e

evidence_level

são métricas independentes.

O código não deve usar evidência como mero nome alternativo para domínio.

Teste combinações como:

- domínio alto + evidência baixa;
- domínio baixo + evidência alta;
- domínio médio + evidência alta;
- domínio indefinido + evidência insuficiente.

---

## 7. VALIDE COBERTURA

Confirme que cobertura mede exposição/abrangência e não desempenho.

Verifique especificamente se:

- uma questão respondida incorretamente ainda pode contar como conteúdo trabalhado;
- responder várias vezes a mesma questão não infla artificialmente questões únicas;
- tópicos sem questões disponíveis são tratados de forma coerente;
- questões arquivadas seguem a regra definida na especificação.

---

## 8. VALIDE DESEMPENHO RECENTE

Teste as classificações definidas pela especificação, por exemplo:

- melhora;
- estabilidade;
- queda;
- dados insuficientes.

Evite decisões baseadas em uma única tentativa isolada, salvo se a especificação definir isso explicitamente.

---

## 9. MIGRE CONSUMIDORES NÃO CRÍTICOS

Somente depois que os testes controlados estiverem aprovados, conclua a migração dos consumidores não críticos.

Prioridade:

1. Tela Estatísticas
2. Dashboard
3. Pontos fracos
4. Progresso

Se algum deles já tiver sido migrado no Passo 3, audite em vez de duplicar trabalho.

O objetivo é que esses consumidores deixem de recalcular métricas que já pertencem ao Núcleo Estatístico.

---

## 10. REMOVA DUPLICAÇÕES SOMENTE QUANDO SEGURO

Após confirmar equivalência ou justificar a nova regra:

- remova fórmulas duplicadas;
- remova consultas redundantes;
- remova helpers estatísticos obsoletos;
- mantenha compatibilidade quando ainda houver consumidores antigos.

Não remova código se ainda existir chamada ativa.

Antes de excluir qualquer função, faça busca global por referências.

---

## 11. DASHBOARD

Audite cada valor estatístico exibido no Dashboard.

Para cada card ou indicador, registre:

- métrica exibida;
- função atual;
- fonte de dados;
- função do Núcleo Estatístico que passou a fornecer o valor.

Não altere o design visual.

O objetivo é trocar a fonte, não a aparência.

---

## 12. TELA ESTATÍSTICAS

Audite todas as abas existentes:

- Histórico;
- Algoritmo;
- Disciplinas;
- Pontos fracos;
- Revisões recentes;
- Tendências;
- Progresso.

Nesta etapa:

- migre somente cálculos já definidos e validados;
- não invente novas métricas;
- não crie gráficos sofisticados;
- não altere layout por estética.

Caso Tendências ou Progresso ainda não tenham dados suficientes para uma representação confiável, preserve a funcionalidade atual ou utilize estado explícito de dados insuficientes.

---

## 13. PONTOS FRACOS

Garanta que a identificação de pontos fracos use métricas oficiais.

Não considere automaticamente fraco um tópico com:

- uma única questão errada;
- evidência insuficiente;
- amostra mínima.

A classificação deve respeitar o contrato estatístico definido no Passo 2.

---

## 14. PROGRESSO

Confirme a separação entre:

- cobertura;
- domínio;
- evidência;
- consolidação.

Nesta etapa, não é necessário criar a interface final avançada de Progresso do Edital.

Apenas garanta que qualquer cálculo existente não misture esses conceitos.

---

## 15. NÃO MIGRE A FILA INTELIGENTE AINDA

A fila inteligente deve permanecer funcionalmente equivalente ao comportamento anterior.

Nesta etapa, faça apenas:

- comparação entre valores que ela usa atualmente e os valores equivalentes do Núcleo Estatístico;
- registro das divergências;
- preparação da próxima migração.

NÃO altere:

- pesos;
- critérios;
- ordem de prioridade;
- penalizações;
- bônus;
- espaçamento;
- regra de queda acentuada.

Se o núcleo já estiver sendo consultado pela fila por alguma alteração do Passo 3, valide que isso não alterou inadvertidamente sua ordenação.

---

## 16. TESTE DE REGRESSÃO DA FILA

Capture um conjunto de tópicos reais ou fixtures representativas e registre:

ORDEM ANTES
versus
ORDEM ATUAL

Se houver diferença causada apenas pela implantação do núcleo, documente-a.

Não normalize a diferença sem entender sua causa.

---

## 17. TESTE DE PERFORMANCE

Verifique se Dashboard e Estatísticas não passaram a gerar consultas excessivas.

Observe principalmente:

- N+1 queries;
- uma consulta por tópico desnecessariamente;
- recálculo repetido da mesma métrica;
- leituras completas do histórico em loops.

Faça otimizações somente quando forem claras e seguras.

Não introduza cache persistente complexo nesta etapa.

---

## 18. TESTE COM BANCO EXISTENTE

Além de fixtures, valide com uma cópia segura de um banco real/existente do projeto.

Não altere dados reais de forma destrutiva.

Verifique:

- abertura do banco;
- carregamento do Dashboard;
- tela Estatísticas;
- sessões;
- revisões;
- Central de Questões;
- perfis;
- histórico.

---

## 19. TESTES AUTOMATIZADOS

Amplie a suíte para proteger o contrato estatístico.

Cada métrica oficial importante deve possuir testes de regressão.

Quando houver bug corrigido nesta etapa, crie um teste que falharia antes da correção.

---

## 20. RELATÓRIO FINAL

Crie:

RELATORIO_VALIDACAO_NUCLEO_ESTATISTICO.md

Inclua:

1. Estado inicial encontrado
2. Métricas auditadas
3. Matriz de validação
4. Cenários controlados executados
5. Divergências encontradas
6. Correções realizadas
7. Consumidores migrados
8. Cálculos duplicados removidos
9. Cálculos ainda existentes fora do núcleo
10. Resultado da validação de domínio
11. Resultado da validação de evidência
12. Resultado da validação de cobertura
13. Resultado da validação de desempenho recente
14. Resultado das agregações
15. Resultado dos períodos temporais
16. Resultado dos testes de dados insuficientes
17. Impacto de arquivamento/lixeira/restauração
18. Comparação da fila inteligente
19. Performance/consultas
20. Testes automatizados executados
21. Pendências
22. Recomendação para o próximo passo

---

## 21. CRITÉRIOS DE APROVAÇÃO

Esta etapa só deve ser considerada concluída se:

- as métricas fundamentais tiverem resultados determinísticos;
- as fórmulas coincidirem com a especificação oficial;
- dados insuficientes forem tratados corretamente;
- domínio e evidência forem independentes;
- cobertura não estiver sendo confundida com domínio;
- agregações não utilizarem médias incorretas;
- períodos temporais forem consistentes;
- histórico não desaparecer por simples arquivamento;
- consumidores não críticos utilizarem o núcleo quando aplicável;
- testes passarem;
- fila inteligente não tiver sido deliberadamente modificada.

---

## 22. CHECKPOINT

Ao concluir:

- execute a suíte completa de testes;
- execute lint/verificações do projeto;
- confirme que o programa inicia;
- faça uma verificação manual básica das telas afetadas;
- remova código temporário de diagnóstico;
- gere um novo checkpoint funcional.

---

## REGRA PRINCIPAL

Não avance para gamificação, novos gráficos ou mudanças na fila inteligente enquanto houver dúvida sobre a correção das métricas centrais.

Ao final desta etapa, devemos conseguir confiar no Núcleo Estatístico como fonte oficial dos dados utilizados pelo restante do VighnaStudy.
