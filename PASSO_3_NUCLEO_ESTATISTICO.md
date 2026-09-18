# PASSO 3 — IMPLEMENTAÇÃO DO NÚCLEO ESTATÍSTICO CENTRAL

Com base nos documentos:

- RELATORIO_AUDITORIA_NUCLEO_ESTATISTICO.md
- ESPECIFICACAO_METRICAS_VIGHNA.md

vamos iniciar a implementação do Núcleo Estatístico Central do VighnaStudy.

## OBJETIVO

Criar uma única camada responsável pelos cálculos estatísticos oficiais do sistema.

A arquitetura desejada é:

DADOS BRUTOS
↓
NÚCLEO ESTATÍSTICO
↓
Dashboard / Estatísticas / Fila Inteligente / Revisões / Progresso / futuras funcionalidades

O objetivo principal desta etapa é eliminar progressivamente cálculos duplicados e garantir que todas as partes do programa utilizem as mesmas definições.

## IMPORTANTE

Não redesenhe nenhuma tela nesta etapa.
Não implemente gamificação.
Não crie gráficos novos.
Não faça alterações estéticas.
Não altere ainda os pesos ou a filosofia da fila inteligente.
Priorize arquitetura, consistência, testes e compatibilidade.

## 1. CRIE A CAMADA CENTRAL DE MÉTRICAS

Com base na arquitetura atual do projeto, crie o módulo ou serviço central mais adequado.
O nome pode seguir a estrutura existente do projeto.
Exemplos conceituais:
- metrics_service.py
- statistics_service.py
- study_metrics.py

Escolha o local que melhor respeite a arquitetura atual.
Evite criar um arquivo monolítico gigantesco.
Se necessário, divida responsabilidades entre módulos coerentes.

## 2. IMPLEMENTE PRIMEIRO AS MÉTRICAS FUNDAMENTAIS

Centralize inicialmente:
- total de tentativas;
- total de acertos;
- total de erros;
- taxa de acerto;
- questões únicas respondidas;
- número de sessões;
- última atividade;
- número de revisões;
- desempenho recente;
- cobertura;
- domínio;
- nível de evidência.

Use rigorosamente as definições estabelecidas em ESPECIFICACAO_METRICAS_VIGHNA.md.
Não crie novas fórmulas diferentes das aprovadas sem justificar tecnicamente.

## 3. CRIE UMA API INTERNA CLARA

As demais partes do programa não devem precisar conhecer os detalhes do banco para calcular estatísticas.
Quero uma interface conceitualmente semelhante a:
- get_topic_metrics(topic_id)
- get_subject_metrics(subject_id)
- get_global_metrics()
- get_period_metrics(start_date, end_date)
- get_question_metrics(question_id)
- get_recent_performance(topic_id)
- get_mastery_score(topic_id)
- get_evidence_level(topic_id)
- get_coverage(topic_id ou subject_id)

Os nomes exatos devem respeitar os padrões existentes do projeto.
O importante é existir uma interface estável e previsível.

## 4. PRIORIZE IDs ESTÁVEIS

Todos os cálculos devem preferencialmente trabalhar com:
- discipline_id
- topic_id
- question_id
- session_id

Nunca utilize o texto do nome do tópico ou da disciplina como identidade quando existir ID estável.
Caso ainda existam pontos que dependam de nomes textuais, documente-os.

## 5. NÃO DUPLIQUE CONSULTAS DESNECESSARIAMENTE

Analise o impacto das consultas.
Evite situações em que uma tela com 30 tópicos execute dezenas ou centenas de consultas redundantes.
Quando adequado, implemente:
- agregações;
- consultas em lote;
- reutilização de resultados;
- funções específicas para múltiplos tópicos.

Não introduza cache persistente prematuramente.
Priorize primeiro consultas corretas e eficientes.

## 6. PRESERVE O HISTÓRICO

Nenhuma alteração desta etapa pode apagar ou reconstruir arbitrariamente:
- tentativas;
- sessões;
- revisões;
- histórico;
- resultados anteriores.

Se alguma migração de banco for necessária, ela deve ser:
- segura;
- reversível quando possível;
- compatível com bancos existentes;
- testada.

Não redefina dados históricos com base no estado atual das questões.

## 7. TRATE QUESTÕES ARQUIVADAS OU EXCLUÍDAS

Verifique cuidadosamente como as métricas se comportam quando uma questão:
- é arquivada;
- é enviada para a lixeira;
- é restaurada;
- é removida definitivamente.

O histórico de uma tentativa realizada anteriormente não deve desaparecer simplesmente porque a questão foi posteriormente arquivada.
Se esse comportamento ainda não estiver garantido, trate-o ou documente claramente a limitação.

## 8. IMPLEMENTE DOMÍNIO COMO MÉTRICA CENTRAL

O cálculo de domínio definido na especificação deve existir em apenas um ponto principal.
Outros módulos devem CONSULTAR esse cálculo.
Não copie a fórmula para:
- Dashboard;
- fila inteligente;
- Estatísticas;
- tela de tópicos;
- progresso.

Esses consumidores devem receber o valor calculado pelo Núcleo Estatístico.

## 9. IMPLEMENTE NÍVEL DE EVIDÊNCIA

Implemente evidence_level conforme especificado.
O resultado deve permitir distinguir situações como:

Domínio: 90
Evidência: Insuficiente

de:

Domínio: 82
Evidência: Alta

Não esconda essa diferença internamente.
O domínio e a evidência devem continuar sendo métricas distintas.

## 10. IMPLEMENTE COBERTURA

Centralize o cálculo de cobertura conforme definido na especificação.
Garanta que COBERTURA ≠ DOMÍNIO.
Cobertura representa contato/abrangência do conteúdo.
Domínio representa desempenho/conhecimento demonstrado.

## 11. IMPLEMENTE DESEMPENHO RECENTE

Crie o cálculo central utilizado futuramente para identificar:
- melhora;
- estabilidade;
- queda.

Não faça ainda alterações visuais.
Disponibilize somente a métrica ou estrutura necessária para que outros componentes possam utilizá-la posteriormente.

## 12. PADRONIZE PERÍODOS

Crie funções reutilizáveis para:
- hoje;
- últimos 7 dias;
- últimos 30 dias;
- período anterior equivalente;
- histórico completo.

Evite que cada tela calcule datas independentemente.

## 13. CRIE OBJETOS DE RETORNO CONSISTENTES

Quando adequado à arquitetura existente, utilize estruturas claras para representar métricas.

Exemplo conceitual:

TopicMetrics
- total_attempts
- unique_questions_answered
- correct_attempts
- incorrect_attempts
- accuracy_rate
- session_count
- review_count
- mastery_score
- evidence_level
- coverage_rate
- recent_performance
- last_activity_at

Pode ser dataclass, DTO, TypedDict ou estrutura equivalente já utilizada no projeto.
Não force uma tecnologia incompatível com a arquitetura atual.

## 14. MIGRAÇÃO CONTROLADA DOS CONSUMIDORES

Depois que o núcleo estiver funcionando, migre inicialmente SOMENTE consumidores de baixo risco.
Prioridade sugerida:
1. Tela Estatísticas
2. Dashboard
3. Pontos fracos
4. Progresso

A FILA INTELIGENTE deve ser migrada apenas depois que os resultados antigos e novos forem comparados.
Não altere ainda o comportamento da fila.

## 15. CRIE MODO DE COMPARAÇÃO

Antes de substituir cálculos críticos, compare:
VALOR ANTIGO
versus
VALOR DO NÚCLEO ESTATÍSTICO

Principalmente para:
- domínio;
- taxa de acerto;
- cobertura;
- desempenho recente;
- revisões.

Se houver diferença, descubra a origem antes de remover a implementação antiga.
Não simplesmente escolha um dos resultados.

## 16. FILA INTELIGENTE: NÃO ALTERAR COMPORTAMENTO AINDA

A fila inteligente é crítica.
Nesta etapa:
- identifique os pontos onde ela consulta métricas;
- prepare interfaces para utilização futura do Núcleo Estatístico;
- compare valores;
- NÃO altere pesos;
- NÃO altere prioridade;
- NÃO altere critérios;
- NÃO mude a ordem final dos tópicos sem necessidade.

A migração efetiva da fila será uma etapa separada.

## 17. TESTES

Crie testes específicos para o Núcleo Estatístico.
Inclua cenários como:
A. Nenhuma tentativa.
B. Uma única tentativa correta.
C. Uma única tentativa incorreta.
D. Mesma questão respondida várias vezes.
E. Várias questões do mesmo tópico.
F. Várias sessões.
G. Tópico com 100% de acerto e evidência insuficiente.
H. Tópico com desempenho alto e evidência alta.
I. Queda recente de desempenho.
J. Recuperação após erros anteriores.
K. Questões arquivadas com histórico existente.
L. Diferentes tópicos dentro da mesma disciplina.
M. Disciplina com tópicos de volumes muito diferentes.
N. Períodos de 7 e 30 dias.
O. Banco sem dados históricos suficientes.

## 18. TESTE AGREGAÇÕES

Verifique especificamente se métricas de disciplina são calculadas corretamente.
Evite média simples das taxas de acerto dos tópicos.

Exemplo:
Tópico A: 1 tentativa, 100%
Tópico B: 99 tentativas, 50%

A disciplina não pode apresentar 75% por simples média entre 100% e 50%.
Ela deve ser recalculada a partir dos dados adequados conforme a especificação oficial.

## 19. COMPATIBILIDADE

Garanta que:
- bancos antigos continuem abrindo;
- backups existentes continuem válidos;
- importação de questões continue funcionando;
- sessões continuem funcionando;
- revisões continuem funcionando;
- Central de Questões continue funcionando;
- perfis continuem funcionando.

## 20. DOCUMENTAÇÃO

Crie RELATORIO_IMPLEMENTACAO_NUCLEO_ESTATISTICO.md.
Inclua:
1. Arquitetura criada
2. Arquivos adicionados
3. Arquivos alterados
4. Métricas implementadas
5. Fórmulas utilizadas
6. Consultas criadas
7. Consumidores já migrados
8. Consumidores ainda não migrados
9. Diferenças encontradas entre cálculos antigos e novos
10. Tratamento de dados históricos
11. Tratamento de questões arquivadas/excluídas
12. Testes criados
13. Resultado dos testes
14. Riscos ou pendências
15. Próxima etapa recomendada

## 21. CHECKPOINT

Ao concluir e validar a implementação:
- execute a suíte de testes;
- execute lint/verificações utilizadas pelo projeto;
- confirme que o programa inicia normalmente;
- não deixe alterações temporárias ou código de diagnóstico ativo;
- gere um novo checkpoint funcional do projeto.

## REGRA PRINCIPAL

Ao final desta etapa, quero poder afirmar:

“Existe uma fonte central e testada para as principais métricas do VighnaStudy.”

Ainda NÃO precisamos afirmar:

“Todas as telas já usam exclusivamente essa fonte.”

A migração deve ser progressiva e segura.
