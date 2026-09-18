# Relatório de Auditoria do Núcleo Estatístico do VighnaStudy

**Data da auditoria:** 18/09/2026  
**Escopo:** cadeia `dados brutos → cálculos → métricas → telas → fila inteligente`  
**Banco inspecionado:** `estudos.db`  
**Natureza desta etapa:** investigação e documentação; nenhuma regra, tela, fórmula ou estrutura de banco foi alterada.

## Resumo executivo

O VighnaStudy já possui uma base estatística substancial. A resposta individual a questões é o registro bruto mais completo: cada tentativa tem identidade própria, horário, sessão, perfil de concurso, resultado, tempo, dúvida marcada e snapshots suficientes para preservar o histórico mesmo após alteração ou remoção da questão. O **Índice de Domínio V2** também é uma métrica elaborada e centralizada em uma função principal.

Ainda não existe, porém, um único significado operacional para “desempenho”, “progresso”, “domínio”, “questões estudadas” ou “urgência”. As telas combinam pelo menos quatro universos:

1. tentativas reais de questões;
2. revisões manuais/automáticas e seus totais agregados;
3. sessões de foco;
4. estados derivados atuais de tópico, agenda e fila.

As diferenças nem sempre aparecem para o usuário. O principal exemplo é o uso do **percentual da revisão mais recente** como “média atual” ou “progresso”, enquanto a fila e outras áreas usam o **Domínio V2**, cuja fórmula considera desempenho recente, cobertura, estabilidade, recência, erros e evidência.

Há dois defeitos de alto impacto que devem ser tratados antes de se considerar o núcleo consolidado:

- `revisoes` não possui `concurso_id`. Uma revisão de tópico é reaproveitada por qualquer perfil que inclua o mesmo tópico. Além disso, a consolidação automática por tópico/data não filtra o perfil ao reunir tentativas. Isso permite misturar respostas de perfis diferentes e expor a mesma revisão em vários perfis.
- o Domínio V2 filtra disciplina pausada, mas não filtra `topico_concurso_importancia.pausado`. Assim, sua média pode incluir tópicos pausados enquanto dashboard, progresso e fila normalmente os excluem.

No banco atual, a integridade estrutural está boa (`PRAGMA integrity_check = ok` e nenhuma violação de chave estrangeira), mas o histórico revela migração gradual: existem 18 sessões de questões, todas classificadas como legado; 13 foram encerradas sem tentativas; e nenhuma possui itens na fila congelada. Portanto, o conjunto de questões planejadas, apresentadas, puladas ou não alcançadas dessas sessões antigas não pode ser reconstruído.

---

## 1. Estrutura atual dos dados

### 1.1 Entidades centrais

| Entidade | Papel estatístico | Identidade e observações |
|---|---|---|
| `disciplinas` | dimensão acadêmica | `id` numérico; `nome`; `chave_estavel` nas migrações atuais |
| `topicos` | menor unidade acadêmica da agenda, domínio e fila | `id`; `disciplina_id`; `nome`; `parent_id`; `dificuldade`; `chave_estavel` |
| `questoes` | banco de itens praticáveis | `id`; `topico_id`; enunciado/gabarito/metadados; `ativa`; `excluida` |
| `concursos` | perfil de estudo | `id`; um perfil ativo por configuração |
| `disciplina_concurso_inclusao` | inclusão/pausa de disciplina por perfil | chave composta lógica por concurso e disciplina |
| `topico_concurso_importancia` | inclusão, pausa e importância do tópico por perfil | importância de 1 a 5; é a fonte da fila |
| `controle_topico` | estado corrente do tópico | revisões iniciais, percentual inicial, próxima revisão e outros campos correntes |
| `sessoes_questoes` | envelope de uma sessão de resolução | início/fim, perfil, modo, objetivo, conclusão, origem/contexto/versão do motor |
| `itens_sessao_questoes` | fila congelada e telemetria de cada item | estado planejado/apresentado/respondido/pulado/não alcançado, snapshots e tempos |
| `tentativas_questoes` | evento bruto de resposta | uma linha por resposta ou pulo, com snapshots históricos |
| `revisoes` | evento agregado/manual de revisão | tópico, data, quantidade, acertos, origem, confiança e metadados de prazo |
| `sessoes_foco` | evento de tempo de estudo | duração planejada/efetiva, início/fim, contexto e conclusão |
| `foco_questoes` | ponte opcional entre foco e sessão de questões | permite relacionar tempo de foco a respostas |
| `efetividade_sessoes` | fotografia derivada antes/depois da sessão | desempenho, tempo, domínio, cobertura e erros agregados |
| `efetividade_topicos_sessao` | fotografia derivada por tópico/sessão | domínio/cobertura/erros antes e depois |
| `simulados` | especialização de sessão de questões | relaciona simulado à sessão e ao resultado |
| `recomendacoes_estudo` | auditoria da recomendação inteligente | IDs e nomes, explicação/decisão e versão do motor |

Referências principais: `banco.py:68`, `banco.py:567`, `banco.py:603`, `banco.py:625`, `banco.py:659`, `banco.py:14197`, `banco.py:14521`, `banco.py:19122`.

### 1.2 Três tipos de dado

- **Bruto:** tentativa, sessão, item congelado, revisão registrada e sessão de foco.
- **Snapshot derivado persistido:** efetividade da sessão/tópico, cópia de nomes/enunciado/gabarito na tentativa e estado do item da sessão.
- **Derivado em tempo de leitura:** Domínio V2, fila, médias, tendências, alertas, previsões e estados de progresso.

Essa distinção é importante: um valor derivado em leitura pode mudar retroativamente quando a fórmula, o conjunto ativo de questões ou o estado pausado é alterado. Um snapshot persistido preserva o que o motor calculou naquele momento, mas não necessariamente permite recalcular exatamente o passado se faltarem versão/configuração completas.

### 1.3 Estado observado em `estudos.db`

Consulta somente leitura realizada durante a auditoria:

| Item | Quantidade/estado observado |
|---|---:|
| disciplinas | 7 |
| tópicos | 100 |
| questões | 156 |
| alternativas | 644 |
| perfis de concurso | 3 |
| linhas em `controle_topico` | 43 |
| revisões | 5 |
| sessões de questões | 18 |
| tentativas | 129 |
| itens congelados de sessão | 0 |
| efetividades de sessão | 18 |
| efetividades por tópico/sessão | 18 |
| sessões de foco | 2 |
| vínculos foco–questões | 0 |
| simulados | 1 |
| recomendações registradas | 16 |

Todas as 129 tentativas atuais possuem sessão, questão, tópico e disciplina identificáveis, `snapshot_origem = resposta` e resultado efetivo. Não há pulos no conjunto atual. As 129 respostas referem-se a 129 questões distintas; portanto o banco atual não contém um exemplo de repetição, embora o modelo suporte repetições corretamente.

### 1.4 Rastreabilidade da cadeia

| Dado bruto/estado | Cálculo principal | Métrica resultante | Consumidores atuais |
|---|---|---|---|
| `tentativas_questoes` | contagem, acertos, janelas 50/15, únicos, dias, erros | desempenho, cobertura, estabilidade, Domínio V2 | Histórico, dashboard de questões, fila, Progresso, efetividade |
| `sessoes_questoes` + itens | agregação por sessão e estado do item | respostas, acertos, tempo, abandono/pulo | resumo da sessão, simulado, efetividade, calibração |
| `revisoes` | último resultado e agregação por data/tópico | percentual atual, revisões realizadas, tendências, pontualidade | Dashboard, Disciplinas, Pontos fracos, Revisões recentes, Tendências, Progresso |
| `controle_topico.proxima_revisao` | diferença para a data atual | hoje, atraso, carga futura | Dashboard, fila, alertas, recomendador |
| `sessoes_foco` | soma de duração, sessões e dias | tempo, consistência, média, distribuição | Dashboard, Histórico, contexto do recomendador |
| associações de perfil | filtros de inclusão/pausa e importância | universo ativo e importância | todas as telas por perfil, fila |
| `efetividade_*` | média/variação antes e depois | domínio observado e efeito da sessão | Histórico e calibração |
| estados acima | fórmulas V3/V5 | prioridade e recomendação explicada | fila inteligente, “Estudar agora”, aba Algoritmo |

### 1.5 Identidade de tópicos e disciplinas

O núcleo atual possui IDs numéricos estáveis enquanto a entidade existe, `chave_estavel` e tabelas de alias para apoiar importação/renomeação. Tentativas modernas também preservam IDs e nomes em snapshots. Domínio, fila, revisão, agenda e associação de perfil trabalham predominantemente com `topico_id`/`disciplina_id`.

Persistem dependências textuais:

- `listar_topicos(nome_disciplina)` ainda recebe nome, embora o resolva pela camada de alias/chave atual;
- a evolução agrupa pela tupla `(topico_id, disciplina_snapshot, topico_snapshot)`, portanto o mesmo ID pode ser fragmentado após renomeação (`evolucao.py:230`);
- agregados por disciplina em `obter_central_minha_evolucao` conciliam snapshots textuais com nomes atuais; uma disciplina renomeada pode perder ou separar histórico;
- distribuição e rotação do Modo Foco usam `disciplina_nome`/`topico_nome` em partes do contexto;
- recomendações registram IDs e nomes, mas algumas regras contextuais de rotação comparam os textos;
- tabelas de revisão normalmente exibem o nome atual obtido por join, não necessariamente o nome histórico no dia da revisão.

Conclusão: a identidade estrutural principal já é baseada em ID, porém os agrupamentos históricos e de contexto ainda não são totalmente imunes a renomeações.

---

## 2. Fluxo de registro das tentativas

### 2.1 Cadeia operacional

1. `JanelaResolverQuestoes` abre uma sessão, salvo quando executada no modo explícito sem impacto na inteligência (`main.py:15413`).
2. `iniciar_sessao_questoes` grava o envelope da sessão (`banco.py:14197`).
3. A fila pode ser congelada em `itens_sessao_questoes`, com ordem, motivo, contexto e snapshots (`banco.py:14270`).
4. Ao confirmar a alternativa, a interface chama `registrar_tentativa_questao` (`main.py:16669`; `banco.py:14521`).
5. Ao pular, a mesma função é chamada com alternativa e resultado nulos (`main.py:16927`).
6. O item congelado correspondente é atualizado para respondido/pulado e recebe timestamps/tempo (`banco.py:14432`).
7. No encerramento, `encerrar_sessao_questoes` finaliza a sessão e classifica itens restantes (`banco.py:14788`).
8. O resumo é obtido por agregação das tentativas (`banco.py:14834`).

### 2.2 Campos registrados em cada tentativa

O registro inclui:

- `id` próprio;
- `sessao_id` e `item_sessao_id`;
- `questao_id` e `concurso_id`;
- `respondida_em`;
- `alternativa_marcada`;
- `correta` (`1`, `0` ou `NULL` para pulo);
- `marcada_duvida`;
- `tempo_segundos`;
- `revisao_id` quando a tentativa foi consolidada em revisão;
- snapshots de questão, tópico, disciplina, capítulo, enunciado, alternativas, gabarito, comentário, banca, cargo, prova, ano e origem do snapshot.

O acerto não é confiado à interface: a função de persistência valida sessão/perfil/item/questão, lê o gabarito e calcula `correta` a partir da alternativa marcada. Isso reduz divergência entre UI e banco.

### 2.3 Identificação de questão, tópico, disciplina, data e sessão

- **Questão:** `questao_id`, reforçado por `questao_id_snapshot`.
- **Tópico:** `topico_id_snapshot`, com fallback para o tópico atual da questão.
- **Disciplina:** snapshot de ID/nome e, quando necessário, relação atual do tópico.
- **Data/hora:** `respondida_em`, texto em horário local.
- **Sessão:** `sessao_id`; dentro da fila congelada, `item_sessao_id`.
- **Perfil:** `concurso_id` diretamente na tentativa.

### 2.4 Respostas repetidas à mesma questão

São distinguíveis. Cada resposta gera uma nova linha com `id`, data e sessão próprios; não existe restrição de unicidade que colapse `(questao_id, usuario/perfil)`. O Domínio V2 contabiliza todas as tentativas e, separadamente, a quantidade de questões únicas. Isso é correto para medir tanto volume quanto diversidade.

Ressalva: algumas análises de erro classificam o estado atual da questão usando a sequência de tentativas recentes, enquanto cobertura usa unicidade. Portanto “129 tentativas” e “129 questões únicas” coincidem apenas acidentalmente no banco atual.

### 2.5 Exclusão e arquivamento

- A exclusão comum de questão com histórico tende a arquivar, mantendo tentativas e snapshots.
- A exclusão permanente da lixeira pode remover a questão; a FK da tentativa vira `NULL`, mas snapshots preservam o evento.
- O Domínio V2 continua usando respostas históricas na parcela de desempenho, porém cobertura e classificação de erros usam o universo de questões atualmente ativas. Arquivar/excluir uma questão pode, portanto, mudar o domínio atual sem mudar nenhuma tentativa.
- Excluir tópico ou disciplina em cascata remove revisões, controle e questões; tentativas sobrevivem por snapshot/FK nula, mas deixam de participar de várias métricas atuais baseadas na dimensão existente.

---

## 3. Fluxo das sessões

### 3.1 Sessões de questões

**Criação:** `iniciar_sessao_questoes` registra perfil, início, modo, objetivo, origem, contexto JSON e versão do motor.  
**Encerramento:** `encerrar_sessao_questoes` grava fim e conclusão; os itens não respondidos são finalizados conforme tenham sido apresentados ou alcançados.  
**Conteúdo:** a sessão não armazena uma única disciplina/tópico, pois pode abranger vários. O escopo é reconstruído pelas tentativas ou pelos itens congelados e seus snapshots.  
**Quantidade, acertos e erros:** são agregados de `tentativas_questoes`; pulos têm `correta IS NULL` e não entram como acerto/erro efetivo.  
**Tempo:** cada tentativa/item pode ter `tempo_segundos`. `efetividade_sessoes` persiste a soma efetiva. A duração de parede pode ser derivada de início/fim, mas não é uma medida canônica de estudo e pode incluir interrupções. Não há pausa formal no envelope de questões.

No banco atual, 18 sessões estão encerradas, mas só 5 têm tentativas; 13 são sessões incompletas/sem resposta. Todas estão marcadas como `origem = legado` e `versao_motor = sessao_legacy`. Como `itens_sessao_questoes` está vazio, não se consegue reconstruir, para esse passado, quais itens foram planejados, apresentados, pulados ou não alcançados.

### 3.2 Efetividade antes/depois

Ao iniciar e finalizar sessões compatíveis, o sistema grava:

- respostas, acertos, desempenho e tempo;
- domínio e cobertura médios antes/depois;
- erros recorrentes e críticos antes/depois;
- estratégia e versão do cálculo;
- detalhamento equivalente por tópico.

Esses dados são **snapshots derivados**, úteis para evolução observada. Eles não são tentativas brutas e não devem ser somados como eventos independentes.

### 3.3 Sessões de foco

O Modo Foco mede tempo com relógio monotônico em memória; pausas não entram na duração efetiva. Só ao finalizar é criado o registro em `sessoes_foco` (`foco.py:826`; `foco.py:1068`; `banco.py:19122`). São persistidos:

- início e fim;
- duração planejada e efetiva;
- disciplina/tópico por ID e snapshot de nome, quando informados;
- atividade, conclusão/interrupção, observação, meta de questões, origem e chave do plano.

Consequências:

- encerramento abrupto antes de `finalizar` perde a sessão ativa;
- foco livre pode legitimamente ficar sem disciplina/tópico;
- acertos/erros não ficam em `sessoes_foco`; só podem ser associados por `foco_questoes` e pelas sessões de questões vinculadas;
- `sessoes_foco` não possui `concurso_id`, logo os resumos são globais ao usuário, não ao perfil.

No banco atual há 2 sessões positivas: uma contextualizada e concluída, outra curta, livre e interrompida. Não há nenhum vínculo em `foco_questoes`.

---

## 4. Métricas existentes

### 4.1 Métricas baseadas em tentativas

- total de respostas efetivas;
- acertos, erros e taxa de acerto;
- questões únicas;
- dias ativos;
- desempenho total, base, recente e por dia/período;
- dúvidas marcadas;
- tempo por resposta/sessão;
- cobertura de questões ativas;
- sequência e recorrência de erros por questão;
- evolução por disciplina/tópico;
- Domínio V2 e seus componentes;
- efetividade antes/depois de sessões.

### 4.2 Métricas baseadas em revisões

- quantidade de revisões realizadas;
- questões/acertos e percentual por revisão;
- percentual atual do tópico, entendido como percentual da revisão mais recente;
- próxima revisão, atrasadas e previstas para hoje;
- pontualidade quando existe metadado histórico válido;
- progresso por número de revisões e percentual mais recente;
- tendências diárias e metas de questões/revisões no dashboard.

### 4.3 Métricas baseadas em foco

- segundos/minutos efetivos;
- sessões, concluídas e interrompidas;
- dias ativos e consistência;
- média por sessão;
- distribuição por disciplina/atividade;
- calibração de duração e ritmo diário/semanal.

### 4.4 Métricas de estado e decisão

- importância por perfil;
- prioridade da fila V3;
- score adaptativo V2 preservado para auditoria;
- urgência/necessidade/momento do motor de recomendação;
- alertas de progresso;
- previsões lineares de início e consolidação;
- estados “não iniciado”, “em andamento”, “consolidando” e “consolidado”.

---

## 5. Fórmulas encontradas

### 5.1 Índice de Domínio V2

Fonte central: `obter_indices_dominio_topicos` (`banco.py:6831`).

#### Janelas

- histórico completo: evidência, dias e alguns totais;
- últimas 50 tentativas do tópico: desempenho-base e diversidade operacional;
- últimas 15: desempenho recente;
- últimos 6 dias distintos de atividade: estabilidade;
- últimas 30 tentativas: taxa de dúvidas.

Se houver mais de 15 tentativas consideradas:

`desempenho = 0,65 × desempenho_recente + 0,35 × desempenho_base`

Caso contrário, usa apenas o desempenho-base.

#### Componentes

`dominio_bruto = 0,30×desempenho + 0,20×variedade + 0,15×estabilidade + 0,10×recência + 0,15×controle_erros + 0,10×evidência - penalidade_dúvida`

- **Variedade:** `55% cobertura histórica das questões ativas + 45% diversidade recente`; sem questões ativas, usa diversidade.
- **Cobertura:** questões ativas únicas já respondidas / questões ativas do tópico.
- **Diversidade recente:** questões ativas distintas nas últimas 50 / `min(12, questões ativas)`.
- **Estabilidade:** evidência temporal multiplicada por fator de consistência calculado com desvio-padrão dos percentuais dos últimos 6 dias.
- **Recência:** 100 até 7 dias; 90 até 14; 75 até 30; 60 até 45; 45 até 60; 25 até 90; 10 depois disso (`banco.py:6659`).
- **Controle de erros:** parte de 100, desconta erros críticos, recorrentes, em recuperação e isolados; aplica penalidade proporcional e bônus de recuperação.
- **Evidência:** 35% volume, 30% questões únicas, 20% dias históricos e 15% revisões ponderadas.
- **Revisões na evidência:** confiança muito baixa pesa 0,25; baixa, 0,5; demais, 1,0; revisões iniciais importadas, até quatro, pesam 0,4 cada.
- **Dúvida:** desconto de até 8 pontos proporcional à taxa nas últimas 30 respostas.

#### Erros por questão

- três acertos recentes: recuperada/dominada;
- um ou dois acertos recentes após erro: em recuperação;
- pelo menos três erros consecutivos, ou pelo menos três erros com taxa da questão abaixo de 50%: crítica;
- pelo menos dois consecutivos, ou pelo menos dois com taxa abaixo de 70%: recorrente;
- demais: isolada.

#### Limites de evidência

O score final recebe tetos progressivos:

- menos de 3 tentativas ou 2 questões únicas: máximo 49;
- menos de 7 tentativas ou 2 dias: máximo 59;
- menos de 12 tentativas ou 3 questões únicas: máximo 69;
- menos de 20 tentativas, 4 questões únicas ou 3 dias: máximo 84;
- níveis 85+ e 95+ têm requisitos adicionais de robustez.

Classificação (`banco.py:6703`): sem tentativas = sem evidência; `<30` crítico; `<50` frágil; `<70` em desenvolvimento; `<85` consolidando; `<95` dominado; `≥95` domínio forte.

### 5.2 “Percentual atual” e progresso

Esta não é a fórmula de domínio. O percentual atual é essencialmente o desempenho da revisão mais recente do tópico. Ele alimenta a média do dashboard, estatísticas por disciplina, ranking de pontos fracos e vários alertas.

O estado de progresso também é independente do Domínio V2:

- sem revisões: não iniciado;
- pelo menos 4 revisões e percentual mais recente ≥85%: consolidado;
- pelo menos 3 revisões e percentual ≥70%: consolidando;
- demais: em andamento.

Assim, um tópico pode ter Domínio V2 “consolidando” e progresso “consolidado”, ou o inverso.

### 5.3 Espaçamento de revisões

`espacamento.py` usa uma matriz configurável por número da revisão (1 a 5+) e faixa de desempenho, interpolando entre limites mínimo/máximo. Queda moderada ou forte pode reduzir o intervalo. Primeiro contato de confiança muito baixa/baixa recebe limite conservador de 7/14 dias. A integração automática distingue:

- 1–4 questões: registra atividade, mas normalmente não agenda;
- 5–9: baixa confiança e preservação cautelosa da agenda;
- 10 ou mais: reagendamento normal;
- primeiro contato: sempre cria revisão e aplica limite conservador.

Referências: `main.py:8501`, `banco.py:14929`, `banco.py:15191`, `espacamento.py:305`.

### 5.4 Pontualidade

Uma revisão só é classificável historicamente se tiver `prevista_para`, `realizada_em` e `prazo_historico_valido = 1`. Registros anteriores à introdução desses campos não são inferidos. Isso é correto: evita inventar pontualidade passada.

### 5.5 Tendências e variações

- Histórico compara a taxa de acerto das tentativas do período com período anterior; variação de foco é percentual sobre segundos.
- Tendências da aba específica usa `revisoes`, agregadas por dia, e compara metades do intervalo.
- Domínio observado é média do snapshot `dominio_medio_depois` das sessões por dia; não é uma reconstrução do Domínio V2 em cada data (`evolucao.py:144`).
- Previsões de edital extrapolam linearmente o ritmo observado de início/consolidação. São projeções, não compromissos do agendador.

---

## 6. Dependências da fila inteligente

### 6.1 Fila Inteligente V3

Pesos centrais (`banco.py:8902`):

| Fator | Peso | Origem/cálculo |
|---|---:|---|
| atraso | 18 | `proxima_revisao` contra hoje |
| baixo domínio | 18 | `100 - Domínio V2` |
| erros recentes | 15 | controle de erros + contagem crítica/recorrente/recuperação |
| queda | 12 | diferença positiva entre desempenho-base e recente |
| importância | 12 | importância 1–5 normalizada para 0–100 |
| falta de cobertura | 9 | `100 - cobertura` |
| poucas revisões | 7 | degrau por total de revisões |
| espaçamento | 9 | tempo desde última resposta / intervalo sugerido |

`score_final = soma(fator × peso) / soma_dos_pesos_ativos`

Classificação: `≥80` muito alta; `≥60` alta; `≥40` média; abaixo de 40, baixa.

Detalhes relevantes:

- sem próxima revisão: primeiro contato recebe 40; tópico já revisado, 15;
- atrasada: `min(100, 75 + 2,5×dias)`; hoje: 70; futura: 0;
- queda só penaliza após 5 tentativas e começa a partir de 5 pontos percentuais;
- revisão 0/1/2/3/4/5+ recebe necessidade 100/78/58/40/24/12;
- importância pode ser desativada, com renormalização dos pesos restantes;
- o intervalo sugerido vem da mesma configuração de espaçamento das revisões.

### 6.2 Adaptativo V2 preservado

Há um score paralelo com pesos domínio 20, erros 18, evidência 15, variedade 12, estabilidade 10, recência 8, urgência 10 e importância 7 (`banco.py:8890`). O campo corrente `score_adaptativo` é substituído pelo V3 para os consumidores atuais; `score_adaptativo_v2` fica para auditoria/compatibilidade.

### 6.3 Motor de recomendação

O motor em `inteligencia.py` volta a decompor a escolha em três eixos configuráveis:

- urgência temporal: 45;
- necessidade acadêmica: 40;
- momento/contexto: 15.

A urgência combina aproximadamente 65% atraso e 35% espaçamento. A necessidade repondera domínio, erros, queda, importância, cobertura e revisões. O momento acrescenta rotação de disciplina/tópico/atividade, concentração semanal do foco, repetição/fadiga, sessão anterior concluída/interrompida e tempo restante no ritmo diário. Histórico de duração e decisões aceitas ajusta principalmente a duração recomendada, não a prioridade acadêmica.

### 6.4 Filtros e fallback

`obter_prioridades_sessao_adaptativa` exige perfil ativo, tópico não pausado e questão ativa. Uma pendência sem questão praticável não entra nessa lista. O dashboard tenta casar cada pendência com o V3 e, se não encontrar, usa a fórmula legada `calcular_prioridade` (`main.py:654`): pressão por data, déficit em relação a 80%, bônus por poucas revisões e ajuste de importância.

No banco auditado havia 8 pendências para hoje/atrasadas, mas somente 4 prioridades adaptativas. Portanto a fórmula legada ainda é um caminho ativo, não apenas código morto.

---

## 7. Dependências do dashboard

| Métrica exibida | Fonte | Natureza |
|---|---|---|
| banco de questões: total, disciplinas e tópicos | questões ativas e relações atuais | real/agregada |
| respostas, acertos, erros e taxa histórica | `tentativas_questoes` efetivas do perfil | real + taxa derivada |
| foco hoje/semana, sessões, média e distribuição | `sessoes_foco` | real + derivada; global, não por perfil |
| revisões atrasadas/hoje/próximas | `controle_topico.proxima_revisao` | estado corrente derivado |
| média atual | média não ponderada do percentual da revisão mais recente por tópico | derivada; não é Domínio V2 |
| meta diária/semanal de questões e desempenho | agregados de `revisoes.questoes/acertos` | real agregado; não é contagem direta de tentativas |
| questões “de hoje” | total de questões das revisões do dia | agregado de revisão |
| tendências de 7 dias | revisões do período contra 7 dias anteriores | derivada |
| cobertura e estados de progresso | tópico iniciado/consolidado pelas regras de revisão | derivada |
| domínio médio | média dos scores atuais do Domínio V2 | derivada em leitura |
| alertas | importância, revisões, percentual, última/próxima data | derivada |
| previsão do edital | eventos de início/consolidação e ritmo linear | projeção |
| fila inteligente | V3, com fallback legado por tópico | derivada; fórmula pode variar por linha |
| simulados | sessões concluídas vinculadas, com respostas | real + percentuais derivados |
| “Estudar agora” | V3/adaptativo + foco/contexto/decisões | recomendação derivada |

Fonte de montagem principal: `main.py:36702` e funções de agregação em `banco.py`.

Ponto importante: o número de “questões” do banco, o número de tentativas e o número de questões somadas em revisões são grandezas distintas. No perfil ativo do banco auditado havia 123 tentativas efetivas, enquanto os agregados de revisão reportavam 184 questões. A diferença pode resultar de revisões manuais/importadas, consolidação e compartilhamento de revisões entre perfis; esses números não devem receber o mesmo rótulo sem qualificador.

---

## 8. Dependências da tela Estatísticas

### 8.1 Histórico

Fonte: `evolucao.obter_evolucao_historica` e `banco.obter_central_minha_evolucao` (`evolucao.py:58`).

- tentativas alimentam desempenho, questões, questões únicas, dias e tendência por tópico;
- foco alimenta tempo, sessões, conclusão, média e consistência;
- revisões alimentam volume e pontualidade;
- Domínio V2 atual alimenta domínio por tópico/média atual;
- `efetividade_sessoes` alimenta domínio observado por dia.

É uma mistura explícita de dados reais e derivados. A série de domínio não reconstrói o domínio histórico: mostra snapshots de sessões existentes. Tópicos são agrupados pela tupla `(topico_id, nome da disciplina, nome do tópico)` (`evolucao.py:230`); uma renomeação pode fragmentar o mesmo ID em duas linhas históricas.

### 8.2 Algoritmo

Fonte: fila/adaptativo, contexto de foco, histórico de decisões e `laboratorio.py`.

Não é uma estatística histórica consolidada. É uma explicação/simulação do estado atual do motor, com eixos, pesos, ranking e impacto da configuração. Os valores são derivados. A aba pode aplicar configuração, mas isso é uma ação administrativa da UI e não altera a origem dos dados auditados.

### 8.3 Disciplinas

Fonte: `obter_estatisticas_disciplinas`.

Para cada disciplina são calculados tópicos, revisões totais (iniciais + registradas), média não ponderada do percentual mais recente dos tópicos, soma de questões em revisões e atrasadas/hoje. O resumo geral faz média das médias das disciplinas, também sem ponderação por tópicos ou questões. Logo uma disciplina pequena pesa tanto quanto uma grande.

Dados brutos: tópicos, revisões e agenda. Métricas derivadas: médias, atrasos e totais. A “média” não é comparável diretamente à taxa de acerto das tentativas nem ao Domínio V2.

### 8.4 Pontos fracos

Fonte: `listar_ranking_topicos`.

O ranking usa principalmente o menor `percentual_atual` da revisão mais recente. Não usa o Domínio V2, recorrência de erros, cobertura ou estabilidade, embora a terminologia da tela possa sugerir uma análise mais abrangente. Tópicos sem percentual/revisão podem ficar fora justamente quando não possuem evidência. Esta métrica deve ser considerada **provisória/incompleta**.

### 8.5 Revisões recentes

Fonte: últimas 40 linhas de `revisoes`, ordenadas por data/ID.

Exibe data, tópico/disciplina, quantidade, acertos, percentual, origem/confiança conforme disponível. Quantidade e acertos são persistidos; percentual é derivado. Mistura revisão manual, automática e outros legados na mesma lista.

### 8.6 Tendências

Fonte: `obter_relatorio_periodo`, baseada em `revisoes`.

Agrega por dia e disciplina: percentual, questões e quantidade de revisões; gráficos e comparação entre metades do período são derivados. Não usa diretamente tentativas, foco nem Domínio V2. Por isso pode divergir da aba Histórico no mesmo intervalo sem que uma delas esteja aritmeticamente errada: as bases são diferentes.

### 8.7 Progresso

Fontes: controle do tópico, revisões, importância, agenda, Domínio V2 e eventos derivados.

- estado do tópico usa número de revisões + percentual mais recente;
- cobertura do edital usa tópicos trabalhados/total;
- Domínio V2 aparece como eixo separado;
- alertas somam pontos por importância, atraso, baixo percentual, ausência de agenda e abandono;
- previsões extrapolam datas de início/consolidação.

A classificação é derivada e não equivale a domínio. Dados importados em `revisoes_iniciais` não possuem eventos individuais; por isso a data histórica de início/consolidação pode ser desconhecida, e o código evita inventá-la em parte das projeções.

---

## 9. Cálculos duplicados

### 9.1 Mapa de duplicidades e divergências

| Conceito | Implementações encontradas | Divergência |
|---|---|---|
| taxa de acerto/desempenho | todas as tentativas; últimas 50/15 no domínio; revisões por período; última revisão; simulado | janela e fonte diferentes |
| “média atual” | média dos últimos percentuais por tópico; média das médias por disciplina; média de Domínio V2 | ponderações e semânticas diferentes |
| questões estudadas | tentativas; questões únicas; soma de `revisoes.questoes`; itens planejados/respondidos | podem diferir legitimamente |
| domínio/progresso | Domínio V2; percentual atual; estado consolidado por revisões; domínio observado persistido | quatro conceitos sob rótulos próximos |
| urgência/atraso | `_score_atraso_fila`; urgência adaptativa V2; urgência temporal do motor; `calcular_prioridade` legado; alertas de progresso | escalas, pesos e faixas diferentes |
| erros | classificação detalhada do Domínio V2; caderno/rankings de erros; contagens de período | janelas e regras de recuperação diferentes |
| tendência | tentativas no Histórico; revisões em Tendências/dashboard; snapshots de domínio | bases não intercambiáveis |
| média de disciplina | média não ponderada dos tópicos; resumo geral como média de disciplinas | dupla não ponderação |
| tópicos ativos | vários filtros de inclusão/pausa | Domínio V2 não exclui tópico pausado |

### 9.2 Duplicidades mais perigosas

1. **Fila V3 x fallback legado.** A mesma tabela do dashboard pode conter prioridades calculadas por fórmulas diferentes, porque tópicos sem questão adaptativa caem no método antigo.
2. **Histórico x Tendências.** Ambos parecem mostrar desempenho temporal, mas o primeiro lê respostas e o segundo, revisões agregadas.
3. **Média atual x Domínio.** O dashboard e a aba Disciplinas usam último percentual de revisão; fila e Histórico podem usar Domínio V2.
4. **Progresso x Domínio.** Consolidação depende de quatro revisões e 85%, não do score de domínio.
5. **Atraso.** Fila, recomendador, alertas e função legada têm curvas distintas para a mesma data.

Nem toda duplicidade deve ser eliminada: desempenho recente e acumulado são métricas diferentes. O problema é a ausência de nomes/contratos que expressem fonte, janela e ponderação.

---

## 10. Problemas encontrados

### 10.1 Gravidade alta

#### A. Revisões não são isoladas por perfil

`revisoes` possui `topico_id`, mas não `concurso_id`. Consultas filtram o perfil verificando se o tópico pertence ao perfil, não se a revisão foi produzida nele. Um mesmo tópico compartilhado torna a revisão visível e contabilizável em vários perfis.

No banco atual há uma revisão automática originada por sessão de um perfil que é visível em três perfis associados ao tópico. Isso afeta percentual atual, totais, tendências, agenda, progresso e evidência do domínio.

#### B. Consolidação automática pode misturar tentativas de perfis

`obter_contextos_revisao_automatica_sessao` identifica tópico/data a partir da sessão, mas a consulta que consolida todas as tentativas do tópico/data não aplica `concurso_id`. `salvar_revisao_automatica_questoes` repete o padrão ao atualizar/vincular. Se dois perfis responderem o mesmo tópico no mesmo dia, os resultados podem virar uma única revisão.

#### C. Linhagem da revisão automática é incompleta

Uma revisão pode reunir tentativas de mais de uma sessão, mas `revisoes.sessao_questoes_id` armazena só um ID e pode ser sobrescrito pela última consolidação. No banco atual, uma revisão automática reúne 95 tentativas de 2 sessões, mas aponta para apenas uma sessão. `tentativas_questoes.revisao_id` preserva os membros; o cabeçalho da revisão, isoladamente, não.

### 10.2 Gravidade média

- **Tópicos pausados no Domínio V2:** os joins exigem disciplina não pausada, mas não `tc.pausado = 0` (`banco.py:6885`, `banco.py:6916`, `banco.py:6987`). No perfil ativo há 6 tópicos pausados; domínio retorna 100 tópicos enquanto dashboard/progresso trabalham com 94.
- **Sessões legadas sem itens:** não é possível reconstruir abandono/pulo/não alcance das 18 sessões atuais; 13 encerradas sem tentativas não têm causa distinguível.
- **Foco global:** ausência de `concurso_id` faz os mesmos minutos aparecerem em qualquer perfil.
- **Histórico inicial resumido:** 45 revisões iniciais estão representadas apenas como contadores em 43 controles. Não há evento, data, questões ou acertos por revisão; tendências históricas não podem ser reconstruídas.
- **Agenda sem histórico completo:** `controle_topico` guarda apenas a próxima data corrente. Reagendamentos anteriores se perdem. `prevista_para` em revisão existe apenas quando capturada ao realizar e é válida em 2 das 5 revisões atuais.
- **Dependência textual residual:** renomear disciplina/tópico pode fragmentar evolução e distribuição de foco; ver seção 3 e 8.
- **Média não ponderada:** tópicos/disciplinas com pouca evidência têm o mesmo peso de conjuntos grandes em vários cards.
- **Sessão de foco só ao final:** falha/fechamento abrupto perde tempo não finalizado.
- **Tempo de sessão de questões ambíguo:** há soma de tempo por tentativa e duração de parede, mas não um campo canônico de tempo ativo com pausas.
- **Datas em texto e horário local:** dificulta normalização de fuso e comparações se o banco for movido entre ambientes.

### 10.3 Gravidade baixa ou dívida semântica

- pontos fracos ignora tópicos sem evidência e não usa os sinais ricos já existentes;
- gráficos/abas com o termo “desempenho” usam bases diferentes sem qualificador visível;
- “questões hoje” pode significar soma registrada em revisões, não respostas individuais;
- snapshots mantêm nomes históricos, mas alguns agrupamentos usam o nome junto com o ID e fragmentam renomeações;
- exclusão/arquivamento altera o universo ativo e pode recalcular domínio retroativamente;
- exclusão de tópico/disciplina remove revisões e controle em cascata, reduzindo estatísticas correntes apesar de snapshots de tentativas sobreviverem;
- não há restrição de unicidade para uma revisão automática por `(perfil, tópico, data, origem)`; além de faltar perfil, a prevenção atual depende de consulta/aplicação.

### 10.4 Qualidade observada do banco atual

- integridade SQLite: OK;
- violações de FK: 0;
- tentativas sem tópico/disciplina/sessão/questão no conjunto atual: 0;
- tentativas sem snapshot: 0;
- questões inativas/excluídas no conjunto atual: 0;
- revisões com quantidade/acertos inválidos: 0;
- revisões duplicadas no mesmo tópico/data/origem: 0;
- sessões de questões sem respostas: 13 de 18;
- itens de sessão históricos: 0;
- revisões com prazo histórico válido: 2 de 5;
- revisões com prazo não reconstruível: 3 de 5;
- vínculos foco–questões: 0;

---

## 11. Dados que já podem ser considerados confiáveis

### 11.1 Confiáveis como eventos brutos

- cada tentativa atual, seu resultado, momento, sessão, perfil e snapshots;
- distinção entre tentativas repetidas à mesma questão;
- total/acertos/erros de uma sessão que possui tentativas;
- inventário atual de questões ativas por ID/tópico;
- duração efetiva das sessões de foco que foram finalizadas e persistidas;
- revisões registradas como eventos, quanto a data, quantidade e acertos armazenados;
- associação tentativa→revisão pelo `revisao_id` existente;
- efetividade persistida como fotografia do cálculo executado na sessão.

### 11.2 Confiáveis com qualificador obrigatório

- Domínio V2: confiável como aplicação da fórmula atual ao universo corrente, mas sensível a pausa/arquivo e contaminação de revisão entre perfis;
- percentual atual: confiável como “percentual da revisão mais recente”, não como domínio geral;
- atraso: confiável como comparação da `proxima_revisao` corrente com hoje, não como histórico completo de atrasos;
- foco: confiável como tempo global persistido, não como tempo por perfil nem como captura de sessões interrompidas por falha;
- tendências de revisão: confiáveis sobre as linhas existentes em `revisoes`, não como histórico completo de todas as respostas;
- desempenho histórico por tentativa: confiável por perfil para o período coberto pelas tentativas registradas.

---

## 12. Dados que ainda precisam ser consolidados

1. **Escopo de perfil das revisões:** adicionar no futuro identidade inequívoca de perfil e migrar/qualificar legados.
2. **Contrato de cada métrica:** nome, fonte, janela, filtros, unidade, ponderação e versão.
3. **Vocabulário:** separar formalmente taxa de acerto, percentual da última revisão, domínio, progresso curricular e prioridade.
4. **Histórico de agenda:** preservar criação, alteração, cancelamento, vencimento e realização de cada previsão.
5. **Linhagem N:N revisão–sessão:** uma revisão consolidada deve apontar para todas as sessões/tentativas que a compõem.
6. **Escopo do foco:** decidir se o foco é global ou por perfil e persistir isso explicitamente.
7. **Tempo ativo de questões:** definir uma métrica canônica que trate pausas, foco e tempo por item.
8. **Dimensões históricas:** agrupar por ID/chave estável e usar nome snapshot apenas para exibição histórica.
9. **Sessões legadas:** marcá-las explicitamente como cobertura telemétrica incompleta; não inferir itens ausentes.
10. **Revisões iniciais importadas:** manter o agregado legado, mas não apresentá-lo como série histórica detalhada.
11. **Política de arquivo/exclusão:** decidir se domínio histórico congela o universo da época ou recalcula contra o catálogo ativo.
12. **Filtros uniformes:** perfil, disciplina pausada, tópico pausado, questão ativa/excluída e eventos nulos.

---

## 13. Recomendações para criação futura de uma camada central de métricas

### 13.1 Arquitetura proposta

Sem implementação nesta etapa, a arquitetura recomendada é uma camada única entre persistência e UI:

```text
eventos brutos
  ├─ tentativas / itens / sessões de questões
  ├─ revisões e agenda
  └─ sessões de foco
          ↓
repositórios de leitura normalizados
  ├─ filtro de perfil e estado
  ├─ resolução por IDs/chaves estáveis
  └─ contrato de períodos e timezone
          ↓
serviço central de métricas versionadas
  ├─ desempenho
  ├─ domínio
  ├─ cobertura e progresso
  ├─ revisão/pontualidade
  ├─ foco/tempo
  └─ prioridade explicável
          ↓
DTOs de consumo
  ├─ Dashboard
  ├─ Estatísticas
  ├─ Fila inteligente
  └─ Histórico/relatórios
```

### 13.2 Contrato mínimo de uma métrica

Cada métrica deveria declarar:

- `codigo` estável, por exemplo `desempenho_tentativas_pct`;
- versão da fórmula;
- fonte bruta;
- escopo (`concurso_id`, disciplina, tópico, sessão);
- janela temporal e timezone;
- filtros de inclusão/pausa/arquivo/nulos;
- unidade e arredondamento;
- regra de ponderação;
- nível de evidência/cobertura;
- data de cálculo;
- componentes explicáveis.

### 13.3 Serviços sugeridos

- `RepositorioTentativas`: eventos efetivos, pulos, únicos, sessões e snapshots.
- `RepositorioRevisoes`: eventos, agenda e pontualidade com escopo de perfil.
- `RepositorioFoco`: tempo efetivo e vínculos com questões/perfil.
- `ServicoDesempenho`: taxas acumulada, recente, por período e por sessão.
- `ServicoDominio`: única implementação versionada do Domínio V2/V3.
- `ServicoProgresso`: cobertura curricular e estados, sem usar “domínio” como sinônimo.
- `ServicoPrioridade`: consome componentes canônicos e produz score + explicação.
- `CatalogoMetricas`: metadados/contratos para que UI e relatórios usem o mesmo significado.

### 13.4 Ordem segura para uma etapa futura

1. criar testes de caracterização das fórmulas atuais, sem mudar resultados;
2. corrigir o escopo de perfil e a linhagem das revisões, com migração auditável;
3. definir contratos e nomes das métricas existentes;
4. extrair consultas para repositórios centrais mantendo compatibilidade;
5. fazer Dashboard e Estatísticas consumirem os mesmos DTOs;
6. retirar fallbacks somente depois de comparar resultados em paralelo;
7. versionar mudanças de fórmula e preservar explicação do score histórico.

### 13.5 Restrições recomendadas para a consolidação

- não recalcular nem preencher retrospectivamente informação que o banco nunca registrou;
- não transformar revisões iniciais agregadas em eventos fictícios;
- não misturar snapshots históricos com nomes correntes na chave de agrupamento;
- não alterar fila/domínio sem uma suíte de casos de referência;
- expor ao usuário a diferença entre “sem evidência” e “desempenho baixo”;
- manter os dados brutos imutáveis e derivar novas versões ao lado das antigas durante a transição.

---

## Conclusão

O núcleo atual não precisa ser descartado. `tentativas_questoes`, seus snapshots, as sessões modernas, a telemetria de efetividade e o Domínio V2 formam uma base útil. A consolidação deve começar pela **semântica e pelo escopo**, não por novos gráficos: isolar revisões por perfil, unificar filtros, nomear corretamente as métricas e fazer dashboard, estatísticas e fila consumirem contratos centrais.

Nenhuma correção foi aplicada nesta auditoria. Os defeitos graves foram documentados antes de qualquer intervenção, conforme solicitado.
