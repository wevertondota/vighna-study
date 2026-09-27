# VighnaStudy 0.29.27 — Seleção integral do resultado na Central de Questões

Build: `central-selecao-resultado-v1`  
Schema: `23` (inalterado)

## Objetivo
Permitir selecionar de uma só vez todas as questões retornadas pelos filtros atuais da Central de Questões.

## Alterações
- adicionada caixa de seleção no cabeçalho da primeira coluna da tabela;
- o controle existente passou a se chamar `Selecionar todo o resultado · N`;
- ambos os controles selecionam todas as linhas do resultado filtrado, não apenas a parte atualmente visível no viewport;
- seleção parcial é representada no checkbox do cabeçalho;
- ao mudar busca/filtros, a seleção global é limpa junto com a reconstrução do resultado;
- ações em lote continuam usando os mesmos IDs selecionados e preservam as confirmações existentes;
- consulta de estado ativo/arquivado para os botões foi otimizada para usar o catálogo já carregado, evitando uma consulta ao banco por questão selecionada;
- ajuda da Central foi atualizada.

## Segurança
Nenhuma alteração de schema ou de dados foi necessária. `estudos.db` permaneceu byte a byte inalterado durante a implementação.

## Validação no ambiente de desenvolvimento
- `python -m py_compile main.py versao.py`: OK
- teste estático direcionado `test_central_selecao_resultado_0_29_27.py`: 7/7 OK
- `PRAGMA integrity_check`: `ok`
- `PRAGMA foreign_key_check`: 0 violações

## Validação visual recomendada no Windows
1. Filtrar um tópico com várias questões.
2. Marcar a caixa no cabeçalho da primeira coluna.
3. Confirmar que todas as questões do resultado recebem marcação.
4. Confirmar que os botões passam a mostrar `Arquivar N` / `Excluir N`.
5. Desmarcar uma questão individual e verificar o estado parcial do checkbox do cabeçalho.
6. Alterar qualquer filtro e confirmar que a seleção anterior é limpa.
