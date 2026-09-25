# VighnaStudy 0.29.18 — Ajuste visual de Rotação & Espelho

## Objetivo
Corrigir o enquadramento do minijogo **Rotação visual** em **Pausa & Desafios**, aproximando a forma original do centro visual do painel e garantindo que as seis alternativas sejam desenhadas integralmente dentro dos respectivos cartões.

## Ajustes realizados
- O bloco **Forma original** deixou de usar uma coluna estreita e passou a receber 1/3 da largura do cabeçalho do tabuleiro.
- A pergunta ocupa os 2/3 restantes, preservando o layout horizontal e evitando aumento desnecessário de altura.
- O canvas da forma original passou de `130×86` para mínimo de `180×88`, com expansão horizontal e altura controlada.
- As duas linhas de alternativas agora reservam no mínimo `98 px` de altura por linha.
- Cada botão de alternativa possui mínimo de `150×98` e o canvas interno mínimo de `110×78`.
- Os três temas (claro, escuro e futurista) receberam uma regra específica para `rotationOptionButton` com `min-height: 98px`, impedindo que a regra genérica dos demais minijogos comprima os cartões.
- O desenho vetorial agora usa margem proporcional ao canvas e não força mais uma célula mínima de 5 px. Isso garante que matrizes maiores sejam reduzidas quando necessário em vez de ultrapassar a área disponível.
- Colunas e linhas da grade receberam `stretch` uniforme para manter centralização e distribuição simétrica.

## Persistência
Nenhum dado, tabela ou regra do motor de estudo foi alterado. `VIGHNA_SCHEMA` permanece em `22`.

## Versão
- `VIGHNA_VERSION = 0.29.18`
- `VIGHNA_BUILD = pausa-rotacao-visual-layout-v2`
- `VIGHNA_SCHEMA = 22`

## Validação
- Compilação estática dos fontes Python: prevista nesta entrega.
- Teste estrutural adicionado em `test_rotacao_visual_layout_0_29_18.py` para validar dimensões, temas, canvas responsivo e versão.
- A abertura visual real depende do runtime Windows/PySide6 do projeto.
