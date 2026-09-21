# Correção — listagem de tópicos sobreposta nas disciplinas

## Problema
Na tela de disciplina, tópicos que possuíam capítulos internos exibiam o nome duas vezes na mesma célula, produzindo textos sobrepostos.

## Causa
A coluna `Tópico` mantinha simultaneamente:
- um `QTableWidgetItem` com o nome visível do tópico; e
- um `QWidget` sobre a mesma célula contendo botão de expansão e `QLabel` com o mesmo nome.

Com o refinamento visual que deixou a célula composta transparente, o texto do item inferior passou a ficar visível atrás do `QLabel`.

## Correção
Quando o tópico possui capítulos, o `QTableWidgetItem` permanece na célula apenas como portador de ID, estado, tipo, nome original, tooltip e suporte à seleção/navegação, porém seu texto visível passa a ser vazio. O nome é renderizado exclusivamente pelo `QLabel` da célula composta.

Tópicos sem capítulos continuam usando normalmente o texto do `QTableWidgetItem`.

## Escopo
A correção é estrutural e vale para os temas Claro, Escuro e Futurista. Não altera banco de dados, revisões, estatísticas, IDs ou histórico.
