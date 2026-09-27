# VighnaStudy 0.29.29 — Meta de questões protagonista

Build: `dashboard-planejamento-meta-protagonista-v1`  
Schema: `23` (inalterado)

## Objetivo

Refinar o card **Planejamento de hoje** da primeira dobra sem alterar sua lógica acadêmica, tornando a **Meta de questões** o elemento visual dominante e reduzindo a fragmentação causada por vários mini-cards internos.

## Alterações

- A meta diária deixou de ser um mini-card com o mesmo peso dos demais elementos.
- O valor `respondidas / meta` passou a ser o número dominante do card, centralizado e com tipografia maior.
- O detalhe da meta passa a usar linguagem direta, por exemplo: `72% concluído • faltam 42`.
- A barra de progresso foi ampliada discretamente para reforçar a leitura da meta.
- **Revisões pendentes** e **Para concluir o dia** foram reunidos em um único bloco operacional, reduzindo bordas internas.
- A seção **Semana** deixou de usar três mini-cards; agora é uma única faixa com os estados de Questões, Revisões e Dias.
- O status geral do dia no cabeçalho e o botão `VER PLANEJAMENTO COMPLETO →` foram preservados.
- O restante do Dashboard não foi reorganizado nesta atualização.

## Arquivos alterados

- `main.py`
- `tema.py`
- `versao.py`

## Validação

- `python -m py_compile main.py tema.py versao.py`: OK
- `test_dashboard_inteligencia.py`: OK
- `test_dashboard_planejamento_meta_protagonista_0_29_29.py`: OK
- Testes direcionados: 13/13 OK
- `PRAGMA integrity_check`: `ok`
- `PRAGMA foreign_key_check`: 0 violações
- `estudos.db`: SHA-256 idêntico ao checkpoint 0.29.28

## Banco de dados

Nenhuma alteração de schema ou de dados foi necessária.
