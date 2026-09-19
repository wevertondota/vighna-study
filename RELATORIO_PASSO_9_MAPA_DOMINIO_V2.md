# RELATÓRIO — PASSO 9 — MAPA DE DOMÍNIO V2

Data: 2026-09-18
Versão final: `0.25.0`
Build: `mapa-dominio-v2`
Schema: `18`

## 1. Estado inicial

A base estatística dos Passos 3–8 já estava consolidada: Núcleo Estatístico oficial, Progresso do Edital V2, análise temporal e carregamento preguiçoso da área de Estatísticas. A estrutura inicial do módulo `mapa_dominio.py` e a aba correspondente já estavam presentes no checkpoint de trabalho, mas a integração ainda precisava ser finalizada e validada como funcionalidade oficial.

O concurso ativo encontrado no banco foi `GCM Toledo` (id 40).

## 2. Arquitetura criada/consolidada

O Mapa de Domínio usa a cadeia:

`statistics_core -> snapshot oficial de progresso -> DomainMapSnapshot -> UI`

O módulo `mapa_dominio.py` não consulta SQLite e não recalcula métricas acadêmicas. Ele transforma o snapshot oficial de `progresso_edital.py` em estados e faixas exclusivamente de apresentação.

O arquivo `mapa_dominio.py` também passou a integrar o conjunto de fontes essenciais do checkpoint nativo.

## 3. Definição do mapa

O mapa é uma visão analítica atual. Ele não é uma fila de estudos e não participa do score de recomendação.

As dimensões permanecem separadas:

- domínio;
- evidência;
- cobertura;
- consolidação.

## 4. Estado de apresentação

Foi consolidado o seguinte estado de UX:

- `Não iniciado`: nenhuma tentativa efetiva;
- `Dados insuficientes`: iniciado, mas sem domínio interpretável;
- `Provisório`: domínio calculável com evidência baixa;
- `Mensurável`: domínio calculável com evidência moderada/alta;
- `Consolidado`: somente quando a consolidação oficial é `consolidated`.

Esses estados não substituem as métricas oficiais.

## 5. Tratamento de domínio `None`

`mastery_score = None` permanece ausência de domínio calculável. Ele nunca é convertido para zero e não recebe faixa visual de domínio baixo.

Na interface, o valor é apresentado como `—`/dados insuficientes.

## 6. Política de evidência baixa

Quando existe domínio calculável com `evidence_level = low`:

- o domínio é exibido;
- o estado é `Provisório`;
- a UI acrescenta indicação visual de provisoriedade;
- o tópico não é tratado como forte/fraco definitivo.

A aba Pontos fracos também foi ajustada para marcar resultados com evidência baixa como `prov.` e usar destaque de atenção, em vez de tratá-los como fraqueza definitiva.

## 7. Faixas visuais

Faixas configuradas no módulo de apresentação:

- 0–49: Baixo;
- 50–69: Intermediário;
- 70–84: Bom;
- 85–100: Alto.

As faixas não alteram `mastery_score` e não são usadas para evidência insuficiente.

## 8. Disciplinas

A visão por disciplina usa as métricas oficiais já agregadas no escopo da disciplina. Não existe média simples dos domínios dos tópicos.

São exibidos:

- domínio da disciplina;
- evidência;
- cobertura de tópicos;
- cobertura de questões;
- quantidade de tópicos mensuráveis;
- consolidados.

## 9. Tópicos

A tabela principal exibe:

- Disciplina;
- Tópico;
- Domínio;
- Evidência;
- Cobertura;
- Consolidação;
- Estado.

O duplo clique reutiliza a janela existente do tópico.

## 10. Filtros

A aba possui filtros por:

- disciplina;
- evidência;
- estado;
- faixa de domínio;
- consolidação;
- busca textual.

O filtro de consolidação foi finalizado nesta etapa e trabalha diretamente com os estados oficiais `insufficient_data`, `not_consolidated` e `consolidated`.

## 11. Ordenação

A ordem padrão é curricular (`Disciplina -> Tópico`).

Também existem ordenações opcionais por:

- domínio crescente/decrescente;
- evidência;
- cobertura;
- atividade recente.

Nenhuma usa a ordem da Fila Inteligente.

## 12. Consolidação

Somente `topic_consolidation_status == consolidated` gera o estado `Consolidado`.

Domínio alto, evidência alta ou grande volume de questões isoladamente não consolidam o tópico.

## 13. Cobertura

Cobertura continua independente de domínio. O mapa consome `question_coverage_rate` já produzido pelo snapshot oficial.

## 14. Última atividade

O snapshot preserva `last_activity_at` oficial (`ultima_atividade` na estrutura de apresentação). Não é inferida data de revisão histórica sem linhagem.

## 15. Integração com Pontos fracos

`listar_ranking_topicos()` já excluía evidência insuficiente. Nesta etapa, a evidência baixa passou a ser carregada junto com cada item do ranking para permitir rotulagem provisória na UI.

Assim:

- `insufficient`: não entra como fraqueza por domínio;
- `low`: pode aparecer, mas claramente como provisório;
- `moderate/high`: interpretação forte disponível.

## 16. Integração com Disciplinas

O mapa reaproveita o snapshot oficial que, por sua vez, usa `get_subject_metrics_batch`. Não foi criada uma segunda fórmula de disciplina.

## 17. Performance / SELECTs

A construção real do snapshot completo do concurso ativo, incluindo todas as métricas necessárias para Progresso/Mapa, executou 16 comandos `SELECT` no banco de teste real com 88 tópicos.

Depois de obtido o snapshot de progresso, `build_domain_map_snapshot()` executa zero consultas SQL.

A aba também foi incluída formalmente em `EstadoEstatisticasLazy`. Assim, ela é carregada somente quando aberta e volta a ser marcada como suja após eventos acadêmicos relevantes, preservando as otimizações de responsividade implementadas anteriormente.

Não existe consulta individual por célula/tópico na UI do mapa.

## 18. Testes

A suíte completa terminou com:

`163 testes aprovados`

Também passaram:

- `test_mapa_dominio.py`;
- `test_analise_temporal.py`;
- `test_progresso_edital.py`;
- `test_statistics_core.py`;
- `test_fila_candidata.py`;
- `test_fila_observacao.py`;
- testes de responsividade;
- testes de build PyInstaller;
- smoke test.

`py_compile` passou em `mapa_dominio.py`, `estatisticas_lazy.py`, `banco.py`, `main.py`, `checkpoint.py` e `versao.py`.

Ruff/Flake8 não estavam disponíveis neste ambiente. O diretório extraído também não contém `.git`, então `git diff --check` não pode ser executado aqui.

PySide6 não está instalado no ambiente de execução, portanto a abertura visual real da janela Qt precisa ser conferida no Windows do usuário. O código de `main.py` compilou normalmente.

## 19. Resultados no banco real

Estado recalculado no banco incluído:

- concurso ativo: GCM Toledo (40);
- 88 tópicos no universo ativo;
- 1 tópico iniciado;
- cobertura de tópicos: aproximadamente 1,14%;
- cobertura de questões: aproximadamente 47,49%;
- domínio global atual: aproximadamente 71,97/100, com evidência global ainda limitada pelo conjunto real de dados.

## 20. Distribuição de estados

No mapa atual:

- Não iniciado: 87;
- Dados insuficientes: 0;
- Provisório: 1;
- Mensurável: 0;
- Consolidado: 0.

O único tópico iniciado no momento aparece corretamente como `Provisório`.

## 21. Distribuição de evidência

- Insuficiente: 87;
- Baixa: 1;
- Moderada: 0;
- Alta: 0;
- Evidência suficiente (Moderada + Alta): 0.

## 22. Tópicos mensuráveis

No banco atual: 0 tópicos com domínio interpretável em evidência moderada/alta.

Isso não é erro; reflete a amostra real existente.

## 23. Tópicos consolidados

No banco atual: 0.

## 24. Status da fila sombra

Nenhuma mudança foi feita na fila decisória.

A Fila Inteligente V3 permanece como única fonte de ordenação/recomendação. O Mapa de Domínio não escreve telemetria sombra por refresh, não altera scores e não altera agendamento.

## 25. Pendências

- validar visualmente no Windows a distribuição de largura dos novos filtros e tabelas;
- manter coleta real de evidência antes de habilitar interpretações mais fortes;
- mini-gráficos por tópico continuam deliberadamente fora do escopo enquanto a série temporal real ainda é curta.

## 26. Recomendação para o Passo 10

Com o Mapa de Domínio concluído, o próximo bloco recomendado é `Regularidade e sequência de estudo`: dias ativos, consistência, frequência, ritmo e sequência. Essa camada deve ser construída sobre eventos reais já consolidados e permanecer separada da gamificação propriamente dita.
