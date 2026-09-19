# RELATÓRIO — PASSO 11 — GAMIFICAÇÃO V1

## 1. Objetivo

Foi implementada a primeira camada de gamificação do VighnaStudy sobre métricas já consolidadas de estudo. A gamificação foi mantida deliberadamente separada das métricas acadêmicas e da Fila Inteligente.

A regra central é simples: o sistema recompensa comportamentos de estudo úteis e verificáveis, e não acertos isolados.

## 2. Versão

- VighnaStudy: `0.27.0`
- Build: `gamificacao-v1`
- Schema: `19`
- Versão interna da gamificação: `gamificacao_v1`

## 3. O que gera XP

A política inicial foi centralizada em `gamificacao.py`:

| Evento | XP base |
|---|---:|
| Dia de estudo válido | 20 |
| Revisão qualificada | 15 |
| Recuperação de erro | 30 |
| Tópico consolidado | 80 |

Não existe XP por acerto individual. Isso evita incentivar repetição de questões fáceis apenas para aumentar pontuação.

Um dia de estudo válido reutiliza exatamente a definição oficial de `regularidade.py`: tentativa efetiva, revisão com questões ou sessão de foco válida com pelo menos 5 minutos.

## 4. Marcos e conquistas

Foram definidos marcos progressivos e persistentes nas categorias:

- sequência de estudo;
- cobertura de questões;
- revisões;
- erros recuperados;
- tópicos consolidados.

Os marcos já conquistados não desaparecem se o catálogo de questões crescer ou se uma métrica acadêmica oscilar posteriormente.

Os limiares e bônus estão centralizados em `gamificacao.py`, permitindo ajuste futuro sem espalhar regras pela interface.

## 5. Níveis

A V1 usa progressão transparente:

- cada nível corresponde a 250 XP;
- `nível = floor(XP total / 250) + 1`;
- a interface mostra o XP acumulado dentro do nível e o progresso até o próximo nível.

Nenhum nível altera prioridade, domínio, revisão ou recomendação.

## 6. Persistência e idempotência

Foi criada a tabela:

`gamificacao_eventos`

Cada evento possui uma `chave` única. A sincronização usa `INSERT OR IGNORE`, de forma que reabrir Dashboard ou Estatísticas não gera XP duplicado.

A tabela registra, entre outros campos:

- tipo do evento;
- concurso quando houver linhagem confiável;
- tópico quando aplicável;
- origem;
- pontos;
- título/detalhe;
- data do evento;
- metadados;
- versão da regra.

A gamificação possui persistência própria e não altera tabelas de tentativas, revisões, domínio ou fila.

## 7. Recuperação de erros

Uma recuperação ocorre quando uma questão que já teve resposta incorreta recebe posteriormente uma resposta correta.

A recompensa é concedida uma única vez por questão na V1.

Isso premia correção de uma dificuldade real sem oferecer XP contínuo por repetir a mesma questão já recuperada.

## 8. Revisões legadas

Revisões qualificadas históricas sem `concurso_id` podem contribuir para a jornada global de gamificação, mas permanecem identificadas nos metadados como `legacy_limited`.

Isso não significa reatribuição acadêmica ao concurso atual. O tratamento acadêmico de linhagem permanece inalterado.

## 9. Consolidação

Tópicos oficialmente consolidados podem gerar evento persistente de consolidação.

A gamificação não possui fórmula própria de consolidação. Ela apenas consome `consolidacao_certificada` do núcleo oficial de progresso.

## 10. Interface — Dashboard

Foi adicionado um resumo compacto de `Conquistas` ao Dashboard com:

- nível atual;
- XP total;
- quantidade de marcos conquistados;
- progresso até o próximo nível;
- botão `Ver conquistas`.

O Dashboard reutiliza os snapshots de Progresso e Regularidade já calculados durante a própria atualização. No banco atual, montar a gamificação com esses snapshots pré-calculados levou em média aproximadamente 2,4 ms nos testes locais.

## 11. Interface — Estatísticas

Foi criada a aba lazy `Estatísticas → Conquistas`.

Ela contém:

- Nível;
- XP total;
- Conquistas;
- Erros recuperados;
- barra de progresso do nível;
- próxima conquista;
- detalhamento da origem do XP;
- tabela completa de conquistas;
- histórico recente de eventos de XP.

A aba participa do mecanismo lazy já existente. Ela não precisa ser calculada apenas por abrir outras áreas de Estatísticas.

## 12. Estado real no banco atual

Após a sincronização idempotente inicial:

- XP total: **255**;
- nível: **2**;
- progresso no nível: **5 / 250 XP**;
- conquistas obtidas: **4 / 24**;
- sequência atual: **3 dias**;
- melhor sequência: **3 dias**;
- dias válidos de estudo: **3**;
- revisões qualificadas: **5**;
- erros recuperados: **0**;
- tópicos consolidados: **0**;
- cobertura atual de questões no concurso ativo: aproximadamente **47,49%**.

Distribuição atual do XP:

- Dias de estudo: 60 XP;
- Revisões: 75 XP;
- Recuperações: 0 XP;
- Consolidações: 0 XP;
- Marcos: 120 XP.

Marcos já obtidos:

- 3 dias em sequência;
- 10% das questões exploradas;
- 25% das questões exploradas;
- 1 revisão.

## 13. Separação da Fila Inteligente

Foi verificado que `fila_candidata.py` e `inteligencia.py` não possuem referência à gamificação.

A gamificação:

- não altera `score_fila`;
- não altera pesos;
- não altera domínio;
- não altera evidência;
- não altera cobertura;
- não altera agendamento;
- não altera espaçamento;
- não escolhe o tópico recomendado.

A Fila Inteligente V3 permanece a única fila decisória.

## 14. Performance

Medições no banco atual:

- com snapshots de Progresso + Regularidade já disponíveis: média aproximada de **2,4 ms**;
- execução totalmente independente, incluindo a obtenção desses snapshots: aproximadamente **35–43 ms** na maioria das medições, com uma amostra isolada maior durante o teste.

Por isso, o Dashboard reutiliza os snapshots já carregados e a aba Conquistas usa o cache analítico/lazy existente.

## 15. Testes

Foi criado `test_gamificacao.py` cobrindo:

- ausência de XP por acerto isolado;
- sincronização idempotente;
- recuperação de erro uma única vez;
- revisão qualificada e marco correspondente;
- persistência de marco de cobertura após crescimento do catálogo;
- consolidação;
- foco inferior a 5 minutos sem gerar dia válido;
- foco igual/superior a 5 minutos gerando dia válido;
- progressão de níveis por faixas de 250 XP.

Validação final:

- **199 testes unittest aprovados**;
- smoke test aprovado;
- `py_compile` aprovado;
- `PRAGMA integrity_check = ok`;
- `PRAGMA foreign_key_check`: 0 violações;
- 12 eventos persistidos no ledger atual de gamificação.

A suíte ainda emite `ResourceWarning` já existente em caminhos de teste de `fila_candidata.py` por conexões SQLite não fechadas. Não houve falha de teste e esse aviso não foi introduzido pela gamificação.

## 16. Limitação de validação visual

O ambiente de execução usado nesta implementação não possui `PySide6` instalado. Por isso, a compilação estática de `main.py` foi validada, mas a inspeção visual real da nova aba e do card do Dashboard deve ser feita no Windows do usuário.

## 17. Próxima etapa sugerida

Após a conferência visual, recomenda-se primeiro observar a gamificação durante uso real antes de acrescentar mais sistemas de XP.

A próxima evolução pode incluir notificações discretas de conquista e pequenos refinamentos visuais, desde que não criem interrupções nem transformem a sequência de estudo em mecanismo punitivo.

A infraestrutura principal da Gamificação V1 está concluída.
