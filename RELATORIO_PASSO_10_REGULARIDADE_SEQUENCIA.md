# RELATÓRIO — PASSO 10: REGULARIDADE, SEQUÊNCIA E RITMO

## 1. Estado inicial

Base: VighnaStudy 0.25.1 (`ctb-capitulos-importacao`), schema 18.

O projeto já possuía:

- `study_day_count` no Núcleo Estatístico por concurso;
- metas semanais, inclusive `meta_dias_estudo_semanal`;
- histórico temporal e sessões de foco;
- carregamento preguiçoso da área Estatísticas.

Ainda não existia uma camada única para medir o hábito global de estudo, sequência atual, melhor sequência, regularidade em relação à meta ou distribuição semanal.

## 2. Arquitetura criada

Foi criado `regularidade.py`, independente da UI, com o snapshot `RegularitySnapshot` (`regularidade_v1`).

A função central é `build_regularity_snapshot(...)`. O `banco.py` expõe `obter_snapshot_regularidade(...)` como adaptador do banco ativo e da meta semanal configurada.

O snapshot não é persistido e não altera métricas acadêmicas.

## 3. Escopo da métrica

Regularidade é deliberadamente GLOBAL. Ela mede hábito de estudo no Vighna, não domínio de um concurso específico.

Um dia é considerado ativo quando existe pelo menos uma das seguintes atividades válidas:

1. tentativa efetiva de questão;
2. revisão registrada com pelo menos uma questão;
3. sessão de foco com pelo menos 5 minutos efetivos.

Múltiplas atividades no mesmo dia contam como um único dia ativo.

Cliques, abertura de tela e refresh não contam.

## 4. Sequência atual

A sequência atual conta dias ativos consecutivos.

Se hoje ainda não possui atividade, mas ontem encerrou uma sequência, ela permanece aberta durante o dia atual (`pending_today`). Isso evita quebrar a sequência antes que o dia termine.

Estados:

- `active_today`;
- `pending_today`;
- `broken`;
- `no_history`.

## 5. Melhor sequência

Calculada sobre todos os dias ativos armazenados no banco, sem depender da meta semanal.

## 6. Regularidade

O índice de regularidade só é calculado quando `meta_dias_estudo_semanal > 0`.

Sem meta, o sistema mostra `—` / meta desativada em vez de inventar um percentual.

Quando há meta:

- considera no máximo os últimos 28 dias observáveis;
- usa a quantidade de dias efetivamente coberta pelo histórico;
- compara dias ativos contra a meta proporcional ao período observado;
- limita o resultado visual a 100%;
- enquanto houver menos de 14 dias de histórico, o resultado é marcado como `provisional`.

O índice mede aderência de hábito, não desempenho acadêmico.

## 7. Ritmo

A camada fornece:

- dias ativos em 7, 30 e 90 dias;
- dias ativos na semana atual;
- ritmo observado em dias por semana na janela recente;
- janela anterior equivalente quando existe base suficiente;
- maior intervalo completo sem estudar;
- intervalo atual completo sem estudar.

O ritmo de 4 semanas não é exibido como valor numérico enquanto houver menos de 7 dias observados.

## 8. Distribuição semanal

Foram criadas as últimas 8 semanas em formato de calendário lógico, com:

- Seg a Dom;
- dia ativo/inativo;
- dias futuros;
- semanas anteriores ao início do histórico;
- total de dias ativos;
- situação da meta, quando configurada.

Semanas anteriores ao primeiro registro não contam contra o usuário.

## 9. Aba Estatísticas > Regularidade

Foi adicionada uma aba própria com carregamento preguiçoso.

Ela contém:

- Sequência atual;
- Melhor sequência;
- Dias ativos nos últimos 30 dias;
- Índice de regularidade;
- Progresso da meta semanal de dias;
- Ritmo recente;
- Últimas 8 semanas;
- Distribuição por dia da semana;
- data de início e fim da base observada.

A aba deixa explícito que a métrica é global e não altera domínio nem prioridade.

## 10. Dashboard

Foi adicionado um resumo compacto de Regularidade com:

- sequência;
- dias ativos na semana;
- dias ativos em 30 dias;
- índice de regularidade, quando existe meta;
- botão `Ver detalhes` para abrir diretamente a aba Regularidade.

O snapshot custa aproximadamente 1,5–2,6 ms no banco atual e fica sob cache curto, evitando impacto perceptível no Dashboard.

## 11. Meta semanal

A implementação reutiliza a configuração já existente:

`meta_dias_estudo_semanal`

Nenhuma meta nova foi criada e nenhum padrão arbitrário de 5 dias foi imposto.

Ao salvar Configurações, o cache de Regularidade é invalidado.

## 12. Invalidação

A aba Regularidade é invalidada quando há:

- respostas a questões;
- revisões;
- sessões de foco;
- troca de dia;
- troca de concurso (por coerência da área Estatísticas, embora a métrica seja global);
- alteração de configurações.

A atualização continua preguiçosa.

## 13. Relação com a fila inteligente

Nenhum valor de regularidade, sequência, streak, ritmo ou meta semanal foi conectado à Fila Inteligente.

A Fila V3 continua sendo a única fila decisória.

Regularidade é comportamento/motivação e não evidência de conhecimento.

## 14. Performance

No banco real, a construção do snapshot executa 4 leituras SQL principais (incluindo inspeção de schema de revisões).

Medição local aproximada em 20 execuções:

- média: 1,65 ms;
- mínimo: 1,49 ms;
- máximo: 2,61 ms.

Não existe consulta N+1 por dia, semana ou disciplina.

## 15. Estado real do banco no momento da implementação

Referência: 18/09/2026.

- primeira atividade: 15/09/2026;
- última atividade: 17/09/2026;
- sequência atual: 3 dias, ainda aberta (`pending_today`);
- melhor sequência: 3 dias;
- dias ativos últimos 7: 3;
- dias ativos últimos 30: 3;
- dias ativos na semana atual: 3;
- meta semanal de dias: desativada;
- índice de regularidade: não calculado;
- histórico observado: 4 dias;
- ritmo de 4 semanas: base ainda curta.

Fontes registradas no histórico global:

- 129 tentativas;
- 5 revisões;
- 3.000 segundos de foco que atendem ao limiar de dia ativo;
- 1 sessão de foco que atende ao limiar de 5 minutos.

## 16. Testes

Foi criado `test_regularidade.py` cobrindo:

- histórico vazio;
- sequência aberta com hoje pendente;
- sequência estendida hoje;
- sequência quebrada;
- foco abaixo/acima de 5 minutos;
- revisão com/sem questões;
- deduplicação de fontes no mesmo dia;
- meta desativada;
- regularidade provisória;
- melhor sequência e maior intervalo;
- semanas ordenadas;
- distribuição por dia da semana.

Resultado da suíte completa:

**181 testes aprovados.**

Smoke test: aprovado.

`py_compile`: aprovado.

SQLite:

- `PRAGMA integrity_check = ok`;
- `PRAGMA foreign_key_check`: 0 violações.

O ambiente de trabalho fornecido não contém o repositório `.git`, portanto `git diff --check` não pôde ser executado aqui.

## 17. Versão final

- VighnaStudy: **0.26.0**
- build: **regularidade-sequencia-v1**
- schema: **18** (sem alteração)

## 18. Próxima etapa recomendada

Com as métricas de comportamento agora formalizadas, a próxima etapa pode ser a Gamificação, usando apenas comportamentos desejáveis e métricas consolidadas, sem premiar artificialmente acertos fáceis nem alterar a Fila Inteligente.
