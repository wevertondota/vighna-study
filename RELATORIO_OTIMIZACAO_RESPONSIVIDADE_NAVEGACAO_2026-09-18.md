# Relatório — Otimização de Responsividade da Navegação

Data: 18/09/2026
Versão: 0.24.2
Build: `responsividade-navegacao-central`
Schema: 18

## 1. Sintomas relatados

Foram relatadas duas pausas perceptíveis adicionais:

1. retorno de outras telas para o Dashboard;
2. abertura da Central de Questões.

A etapa anterior já havia aplicado carregamento preguiçoso às abas de Estatísticas. Esta etapa estende o mesmo princípio para a navegação geral.

## 2. Causa — retorno ao Dashboard

O método `voltar_inicio()` executava `atualizar_dashboard()` de forma síncrona antes de trocar o `QStackedWidget` para `tela_inicial`.

Assim, o clique em Voltar aguardava consultas, montagem da fila, atualização de planejamento, progresso e demais widgets antes de produzir resposta visual.

Também existia atualização do Dashboard pelo barramento de `dados_alterados` mesmo quando o Dashboard não estava visível, o que podia produzir trabalho duplicado: atualizar em segundo plano e atualizar novamente no retorno.

## 3. Correção — Dashboard

Foi introduzido estado explícito de invalidação:

- `_dashboard_sujo`;
- `_dashboard_refresh_agendado`;
- `_dashboard_data_referencia`.

Novo comportamento:

- `voltar_inicio()` troca a página primeiro;
- se o Dashboard já estiver atualizado, nenhum recálculo ocorre;
- se houver dados novos, o refresh é postergado em 15 ms para permitir repaint;
- eventos acadêmicos ocorridos fora do Dashboard apenas o marcam como sujo;
- o cálculo é realizado quando o Dashboard estiver efetivamente visível;
- alterações exclusivas do Modo Foco preservam o caminho de atualização rápida;
- `Ctrl+H` usa o mesmo fluxo responsivo;
- `ir_para_secao_dashboard()` também agenda atualização sem bloquear a navegação;
- pausar/finalizar sessão passa a mostrar o Dashboard antes da atualização pesada.

## 4. Causa — Central de Questões

`abrir_questoes()` executava `carregar_questoes()` antes de navegar para a página.

Além disso, cada carga fazia duas consultas quase idênticas ao catálogo:

- questões conforme estado de arquivamento;
- novamente todas as questões para os contadores administrativos.

A montagem da `QTableWidget` também mantinha sinais e repaint ativos durante centenas de inserções. A tabela possui sinais `itemSelectionChanged` e `itemChanged` ligados a `atualizar_acoes_questao`, portanto o custo de montagem podia ser amplificado.

## 5. Correção — Central de Questões

Foi introduzido estado de invalidação:

- `_central_questoes_suja`;
- `_central_questoes_refresh_agendado`;
- `_central_questoes_concurso_id`.

Novo comportamento:

- a página é exibida antes de consultar/reconstruir a grade;
- a primeira carga é agendada para 15 ms depois;
- voltar à Central sem alterações reaproveita os dados e a tabela existentes;
- alterações de questões/tópicos invalidam a Central;
- mudança de concurso força nova carga;
- o catálogo administrativo é consultado uma única vez e a visão ativa é derivada em memória;
- durante a montagem em lote da tabela são suspensos repaint, sinais e sorting;
- ao final, o estado visual é restaurado e ocorre apenas uma atualização das ações da questão;
- foi removida uma chamada redundante de `atualizar_acoes_questao()` no fim de `carregar_questoes()`.

## 6. Medições de consultas do banco

No banco do checkpoint, antes da alteração de fluxo, as operações isoladas apresentaram aproximadamente:

- métricas globais: 5,68 ms;
- `obter_dashboard`: 0,92 ms;
- resumo de foco: 0,77 ms;
- listar questões ativas: 3,70 ms;
- listar todas as questões: 2,58 ms;
- detecção de duplicadas: 26,07 ms;
- histórico de questões: 3,56 ms;
- integridade histórica: 0,85 ms;
- disciplinas: 0,64 ms.

O maior custo percebido da Central não vinha apenas do SQLite, mas da soma de detecção de duplicidade + construção de milhares de células Qt + sinais/repaint durante essa construção.

## 7. Testes adicionados

Foi criado `test_responsividade_navegacao.py`, cobrindo:

- navegação ao Dashboard antes do refresh;
- refresh diferido e condicionado a estado sujo;
- ausência de atualização síncrona do Dashboard fora da tela;
- navegação para a Central antes da carga;
- uma única listagem base do catálogo;
- suspensão de sinais/repaint/sorting na montagem;
- reutilização do fluxo responsivo pelo atalho `Ctrl+H`.

## 8. Validação

Resultados no ambiente de validação:

- `python -m unittest discover -q`: 133 testes aprovados;
- `testes_smoke.py`: aprovado;
- `py_compile`: aprovado para os módulos principais alterados/dependentes;
- SQLite `PRAGMA integrity_check`: `ok`;
- `PRAGMA foreign_key_check`: 0 violações;
- questões ativas no banco validado: 259.

Ruff/Flake8 não estavam instalados neste ambiente.

PySide6 também não está disponível aqui, portanto a percepção visual final de latência deve ser validada no Windows do usuário.

## 9. Comportamento esperado no Windows

### Retorno ao Dashboard

Ao clicar em Voltar sem ter alterado dados desde a última visualização, a troca deve ser praticamente imediata e não deve executar um refresh completo.

Se dados tiverem mudado, o Dashboard deve aparecer primeiro e a atualização ocorrer logo depois.

### Central de Questões

Na primeira abertura, a moldura/tela deve aparecer antes da carga da grade.

Em visitas posteriores sem alteração no catálogo, a Central deve reutilizar a tabela já carregada e abrir de forma muito mais rápida.

Após cadastrar, editar, arquivar, remover ou alterar estrutura de questões/tópicos, a próxima atualização deve reconstruir os dados corretamente.

## 10. Próxima etapa

Validar a sensação real de navegação no Windows. Se os dois gargalos estiverem resolvidos, retomar o Passo 9 — Mapa de Domínio V2 sobre a base responsiva.
