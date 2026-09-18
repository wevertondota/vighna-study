# PASSO 5 — PARIDADE DA FILA INTELIGENTE EM MODO SOMBRA

Use como base obrigatória:

- `RELATORIO_AUDITORIA_NUCLEO_ESTATISTICO.md`
- `ESPECIFICACAO_TECNICA_NUCLEO_ESTATISTICO.md`
- `RELATORIO_IMPLEMENTACAO_NUCLEO_ESTATISTICO.md`
- `RELATORIO_VALIDACAO_NUCLEO_ESTATISTICO.md`
- implementação atual em `statistics_core/`
- implementação atual da Fila Inteligente V3 e dos recomendadores

## OBJETIVO

Esta etapa NÃO é para trocar imediatamente a Fila Inteligente atual.

O objetivo é construir e validar uma versão candidata da fila que use, quando semanticamente correto, as métricas oficiais do Núcleo Estatístico, executando-a em paralelo com a fila atual.

Arquitetura desejada:

DADOS BRUTOS
↓
NÚCLEO ESTATÍSTICO
↓
FILA CANDIDATA EM MODO SOMBRA
        ↕ comparação
FILA INTELIGENTE V3 ATUAL
↓
DECISÃO REAL CONTINUA SENDO DA V3

Até o final desta etapa:

- a fila atual continua sendo a fonte da ordem usada pelo usuário;
- nenhuma mudança de pesos deve ser ativada em produção;
- nenhuma nova fila candidata deve assumir silenciosamente o controle;
- todas as diferenças devem ser observáveis e explicáveis.

A finalidade é responder:

“Podemos migrar a Fila Inteligente para as métricas oficiais sem perder coerência, segurança e explicabilidade?”

---

## 1. PRÉ-VOO

Antes de alterar qualquer código:

1. leia integralmente os quatro documentos citados acima;
2. localize a implementação atual da Fila Inteligente V3;
3. localize todos os consumidores da fila;
4. identifique os componentes usados no score atual;
5. confirme quais partes já possuem comparação com `statistics_core`;
6. registre o comportamento atual como baseline.

Não altere ainda a ordenação real.

---

## 2. CONGELE O BASELINE DA FILA V3

Documente formalmente a fórmula, pesos e componentes atuais.

O relatório do Passo 4 indica os componentes:

- atraso;
- domínio;
- erros recentes;
- queda;
- importância;
- cobertura;
- revisões;
- espaçamento.

Confirme no código.

Registre:

- peso de cada componente;
- faixa de cada score;
- fonte de dados;
- tratamento de dados ausentes;
- regras especiais;
- desempates;
- proteção de revisões vencidas/previstas;
- qualquer bônus ou penalização;
- relação entre Fila Inteligente V3 e Motor de Recomendação V4/V5.

Esse baseline será a referência de regressão.

---

## 3. CLASSIFIQUE CADA COMPONENTE

Para cada componente da fila, classifique-o em uma destas categorias:

### A. MÉTRICA ACADÊMICA OFICIAL

Deve vir, em princípio, do Núcleo Estatístico.

Exemplos possíveis:

- domínio;
- cobertura;
- desempenho recente;
- evidência;
- controle de erros.

### B. ESTADO OPERACIONAL

Não deve ser artificialmente transformado em métrica acadêmica.

Exemplos possíveis:

- atraso da próxima revisão;
- prazo;
- espaçamento;
- revisão prevista hoje;
- revisão vencida.

### C. CONFIGURAÇÃO DO USUÁRIO

Exemplo:

- importância.

### D. DADO COM LINHAGEM INSUFICIENTE

Exemplo:

- revisão histórica sem `concurso_id` inequívoco.

Não force dados de categoria B, C ou D para dentro do Núcleo Estatístico só para centralizar tudo.

Centralização não significa misturar conceitos diferentes.

---

## 4. CRIE UMA TABELA DE MAPEAMENTO LEGADO → OFICIAL

Produza uma tabela técnica semelhante a:

| Componente V3 | Fonte atual | Métrica oficial candidata | Compatibilidade | Observação |
|---|---|---|---|---|
| domínio | Domínio V2 | mastery_score | parcial/total | ... |
| cobertura | cálculo legado | question_coverage_rate | ... | ... |
| queda | base/recente legado | performance_trend/delta oficial | ... | ... |
| erros recentes | lógica atual | componentes oficiais de erro | ... | ... |
| revisões | revisão legada | completed_review_count | ... | linhagem |
| atraso | agenda | mantém operacional | n/a | ... |
| importância | configuração | mantém configuração | n/a | ... |
| espaçamento | agenda | mantém operacional | n/a | ... |

Não assuma equivalência só porque os nomes parecem semelhantes.

---

## 5. NÃO SUBSTITUA `mastery_score = null` POR ZERO

O Passo 4 confirmou que muitos tópicos ainda possuem evidência insuficiente.

Quando:

`mastery_score = null`

isso significa:

“domínio público ainda não certificado”

e NÃO:

“domínio = 0”.

A fila candidata precisa possuir tratamento explícito para:

- evidência insuficiente;
- evidência baixa;
- evidência moderada;
- evidência alta.

Não criar prioridade artificialmente extrema apenas porque um tópico ainda não tem dados.

---

## 6. DEFINA UMA POLÍTICA DE FALLBACK

Crie e documente uma política determinística para componentes oficiais indisponíveis.

A política deve distinguir:

- ausência real de dados;
- dado legado;
- `legacy_limited`;
- dado insuficiente;
- valor válido igual a zero.

Não use expressões genéricas como:

`valor or 0`

quando zero e ausência possuem significados diferentes.

O fallback pode preservar temporariamente um valor legado, mas deve:

- ficar explicitamente marcado;
- informar a razão;
- nunca parecer um valor oficial;
- poder ser removido futuramente.

---

## 7. IMPLEMENTE A FILA CANDIDATA EM MODO SOMBRA

Crie uma implementação candidata sem alterar o comportamento real do sistema.

Exemplo conceitual:

- `fila_inteligente_v3`: fila ativa;
- `fila_inteligente_candidate`: fila sombra.

O nome real deve seguir a arquitetura existente.

A fila candidata deve:

- receber os mesmos tópicos elegíveis;
- usar os mesmos estados operacionais relevantes;
- consultar o Núcleo Estatístico em lote;
- produzir seus próprios componentes;
- calcular score candidato;
- ordenar candidatos;
- NÃO substituir a fila ativa.

---

## 8. EVITE N+1

A fila candidata deve buscar as métricas oficiais em lote.

Não faça:

- uma consulta completa por tópico;
- uma chamada de banco para cada componente;
- recálculo repetido do mesmo escopo.

A implementação do Passo 4 já demonstrou consulta em lote constante para múltiplos tópicos. Preserve esse padrão.

---

## 9. CRIE UM OBJETO DE COMPARAÇÃO EXPLÍCITO

Para cada tópico, produza estrutura equivalente a:

- posição V3;
- score V3;
- posição candidata;
- score candidato;
- delta de posição;
- componentes V3;
- componentes candidatos;
- métricas oficiais usadas;
- fallbacks usados;
- nível de evidência;
- motivo principal V3;
- motivo principal candidato;
- divergências relevantes;
- `used_for_queue_order = false`.

Preserve explicitamente:

`used_for_queue_order = false`

durante todo o Passo 5.

---

## 10. NÃO INVENTE NOVOS PESOS NESTA ETAPA

Primeiro tente preservar a filosofia e os pesos relativos da fila atual sempre que houver equivalência semântica.

Se a troca de uma métrica tornar um peso incompatível:

- documente;
- proponha opções;
- não altere silenciosamente.

Qualquer futura mudança deliberada de pesos deve ser versionada e ocorrer em etapa própria.

---

## 11. TESTE PARIDADE EXATA QUANDO ESPERADA

Para componentes que deveriam ser matematicamente equivalentes, exija paridade.

Exemplo:

se a cobertura antiga e a cobertura oficial representam exatamente o mesmo conceito e universo, os valores devem coincidir dentro de tolerância definida.

Se não coincidirem:

- encontre a causa;
- não esconda o delta;
- determine qual conceito é correto.

---

## 12. TESTE DIVERGÊNCIA INTENCIONAL

Algumas métricas NÃO precisam produzir o mesmo valor do legado.

Exemplo provável:

- Domínio V2 versus `mastery_score@1`.

Nesse caso, classifique a divergência:

- mudança de fórmula;
- tratamento de evidência;
- janela temporal;
- população diferente;
- linhagem;
- correção de bug;
- diferença de conceito.

A divergência deve ser explicável.

---

## 13. CRIE FIXTURES REPRESENTATIVAS DA FILA

Inclua cenários determinísticos para:

A. tópico nunca estudado;

B. uma única questão correta;

C. uma única questão errada;

D. evidência insuficiente com 100% de acerto;

E. baixo domínio com evidência alta;

F. domínio alto com evidência alta;

G. revisão vencida;

H. revisão prevista para hoje;

I. revisão futura;

J. tópico sem próxima revisão;

K. importância muito alta;

L. importância baixa;

M. queda recente;

N. melhora recente;

O. estabilidade;

P. erros críticos consecutivos;

Q. questão recuperada após erros;

R. cobertura muito baixa;

S. cobertura alta;

T. muitas revisões;

U. revisão `legacy_limited`;

V. dois tópicos com score empatado;

W. tópico pausado/inativo;

X. disciplina/tópico sem questões ativas.

---

## 14. TESTE INTERAÇÕES ENTRE FATORES

Não teste apenas fatores isolados.

Inclua combinações como:

- domínio alto + revisão vencida;
- domínio baixo + revisão futura;
- evidência insuficiente + importância alta;
- queda recente + cobertura alta;
- erros críticos + revisão hoje;
- tópico novo + alta importância;
- domínio baixo + evidência alta + baixa importância.

A finalidade é validar comportamento emergente da fila.

---

## 15. PRESERVE A PROTEÇÃO TEMPORAL

O sistema atual protege revisões vencidas ou previstas para hoje em partes do fluxo de recomendação.

Não remova essa proteção nesta etapa.

Teste explicitamente se a fila candidata:

- reconhece revisão vencida;
- reconhece revisão para hoje;
- não deixa uma métrica acadêmica isolada apagar uma obrigação temporal sem decisão de produto.

---

## 16. TESTE ORDEM, NÃO APENAS SCORE

Para cada fixture e cenário real, compare:

- Top 1;
- Top 3;
- Top 5;
- Top 10, quando houver;
- deslocamento médio de posição;
- maior subida;
- maior queda;
- taxa de tópicos que mantiveram posição;
- taxa de interseção entre Top N antigo e candidato.

Não transforme essas medidas em regra automática de aprovação; elas são instrumentos de diagnóstico.

---

## 17. USE O BANCO REAL SOMENTE EM LEITURA/COM CÓPIA SEGURA

Execute comparação sobre uma cópia consistente do banco atual.

Não altere o histórico real para fabricar evidência.

O Passo 4 indicou que a maior parte dos tópicos ainda possui evidência insuficiente. Preserve isso como característica real da base.

Não “complete” dados para tornar a fila candidata mais conveniente.

---

## 18. CRIE SNAPSHOT DE PARIDADE

Crie um formato reprodutível de snapshot, preferencialmente estruturado, contendo:

- data/hora;
- concurso/perfil;
- versão da fila ativa;
- versão da fila candidata;
- versão das métricas;
- tópicos avaliados;
- ordem ativa;
- ordem candidata;
- scores;
- componentes;
- fallbacks;
- nível de evidência.

Não grave esse snapshot como se fosse uma sessão de estudo.

É telemetria/auditoria.

---

## 19. OBSERVAÇÃO PARALELA

Se a arquitetura permitir sem risco, mantenha a comparação sombra disponível por um período controlado de uso real.

Ela deve:

- calcular a fila candidata;
- continuar entregando ao usuário a V3;
- registrar somente dados necessários à comparação;
- não alterar a recomendação;
- não alterar agendamento;
- não afetar estatísticas acadêmicas.

Se isso exigir persistência invasiva, implemente apenas o suporte mínimo e documente.

---

## 20. LINHAGEM DE REVISÕES

O Passo 4 apontou uma limitação:

`revisoes` ainda não possui linhagem de perfil/concurso suficiente em todos os registros.

Nesta etapa:

- não atribua retroativamente um perfil por palpite;
- identifique exatamente o impacto dessa limitação na fila candidata;
- mantenha `legacy_limited` quando aplicável;
- proponha a migração de schema necessária para registros FUTUROS.

Não faça uma migração destrutiva de histórico.

Se for indispensável adicionar `concurso_id` para dados futuros apenas para permitir a observação correta, faça isso somente com:

- migração aditiva;
- campo inicialmente anulável;
- compatibilidade com bancos antigos;
- testes;
- documentação.

Caso não seja indispensável ao modo sombra, apenas prepare o plano e deixe a alteração para o passo seguinte.

---

## 21. SESSÕES DE FOCO

O Passo 4 também registrou ausência de identidade inequívoca de perfil em `sessoes_foco`.

Não associe foco histórico a concurso por inferência.

Documente se isso afeta alguma variável da fila candidata.

Se não afetar, mantenha fora do escopo.

---

## 22. AUDITE O RECOMENDADOR V4/V5

A Fila Inteligente não existe isoladamente.

Verifique como:

- `MotorRecomendacaoV4`;
- `MotorRecomendacaoV5`;
- “Estudar agora”;
- sessão recomendada;
- proteção de revisão;
- explicação “Por que esta recomendação?”

consomem a fila.

Garanta que o modo sombra não faça a fila candidata escapar para a decisão final por algum caminho indireto.

---

## 23. EXPLICABILIDADE

A fila candidata deve conseguir explicar cada componente sem jargão interno.

Internamente, preserve:

- valor bruto;
- score normalizado;
- peso;
- contribuição;
- fonte;
- versão da métrica;
- fallback, se houver.

A interface visual não precisa ser alterada neste passo.

---

## 24. PERFORMANCE

Compare o custo da fila ativa e da candidata.

Registre:

- quantidade de SELECTs;
- tempo aproximado em fixture controlada;
- tempo no banco real;
- quantidade de tópicos processados.

Não introduza cache persistente complexo.

Prefira carregamento em lote e reuso dentro da mesma avaliação.

---

## 25. TESTES DE REGRESSÃO

Crie testes automatizados para:

- baseline da V3;
- fila candidata;
- `used_for_queue_order = false`;
- fallback de dados insuficientes;
- não conversão de `None` em zero;
- revisão `legacy_limited`;
- estabilidade de desempates;
- proteção temporal;
- consulta em lote;
- comportamento com tópico inativo;
- comportamento sem questões;
- ausência de efeitos colaterais no banco.

---

## 26. NÃO ALTERE A FILA ATIVA

Durante todo o Passo 5:

NÃO:

- troque a V3 pela candidata;
- altere os pesos ativos;
- altere critérios ativos;
- altere o Top 1 mostrado ao usuário por causa da candidata;
- altere o agendamento de revisões;
- altere o algoritmo de espaçamento;
- altere gamificação;
- crie novos gráficos;
- redesenhe Dashboard ou Estatísticas.

---

## 27. HOUSEKEEPING DO CHECKPOINT

O checkpoint anterior possui o manifesto nativo `checkpoint_manifest.json`, que é a autoridade atual de restauração e integridade.

Existe também um arquivo legado `MANIFEST_SHA256.txt`.

Antes de concluir esta etapa:

- confirme se `MANIFEST_SHA256.txt` ainda possui consumidor real no código;
- se estiver obsoleto, documente isso e deixe de tratá-lo como fonte de integridade;
- não permita que um manifesto legado desatualizado gere falsa conclusão de corrupção;
- não remova o arquivo sem confirmar que não existe dependência externa conhecida.

Também trate arquivos temporários de status/diff como artefatos de desenvolvimento, não como fonte normativa do estado atual.

---

## 28. CRITÉRIOS PARA PROPOR MIGRAÇÃO NO PASSO SEGUINTE

Ao final, classifique a situação em uma destas categorias:

### PRONTO PARA MIGRAÇÃO CONTROLADA

Quando:

- não há divergências inexplicadas relevantes;
- fallbacks estão definidos;
- dados insuficientes são seguros;
- proteção temporal está preservada;
- testes cobrem cenários críticos;
- desempenho é aceitável.

### PRONTO COM BLOQUEADORES ESPECÍFICOS

Liste exatamente quais bloqueadores precisam ser resolvidos antes da migração.

### NÃO PRONTO

Explique objetivamente por quê.

Não ative a candidata mesmo que seja classificada como pronta.

---

## 29. RELATÓRIO FINAL

Crie:

`RELATORIO_PARIDADE_FILA_INTELIGENTE.md`

Inclua:

1. arquitetura atual da fila;
2. baseline V3;
3. componentes e pesos;
4. mapeamento legado → oficial;
5. componentes que permaneceram operacionais;
6. política de dados insuficientes;
7. política de fallback;
8. arquitetura da fila candidata;
9. fixtures executadas;
10. interações entre fatores;
11. resultados da comparação de scores;
12. resultados da comparação de posições;
13. Top N comparado;
14. divergências esperadas;
15. divergências inesperadas;
16. impacto da evidência;
17. impacto de `legacy_limited`;
18. impacto da linhagem de revisões;
19. integração com Motor V4/V5;
20. performance;
21. testes automatizados;
22. riscos;
23. bloqueadores;
24. classificação final de prontidão;
25. recomendação para o Passo 6.

---

## 30. CHECKPOINT

Ao concluir:

- execute os testes da fila;
- execute `test_statistics_core.py`;
- execute a suíte smoke;
- execute `py_compile`;
- execute lint direcionado nos arquivos alterados;
- execute `git diff --check`;
- valide integridade do SQLite;
- confirme que o programa inicia;
- confirme que a fila exibida ao usuário continua sendo a V3;
- gere novo checkpoint completo.

Valide o novo checkpoint com o mecanismo nativo de `checkpoint.py`.

---

# REGRA PRINCIPAL

O Passo 5 é uma etapa de OBSERVAÇÃO E PARIDADE.

A fila candidata pode calcular, comparar, registrar e explicar.

Ela NÃO pode decidir o que o usuário estudará enquanto esta etapa estiver em andamento.

Ao final, queremos evidência suficiente para decidir conscientemente se o Passo 6 será:

- migração controlada da fila para as métricas oficiais; ou
- correção de bloqueadores antes da migração.
