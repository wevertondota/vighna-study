# Relatório — ajuste do tema futurista na tela Resolver questões

## Problema observado
No tema **Futurista**, a tela **Resolver questões** apresentava faixas internas muito escuras nas alternativas e no enunciado, gerando uma estrutura visual estranha e fragmentada.

## Causa provável
O tema Futurista aplica um background genérico a `QWidget`, o que acabava aparecendo em widgets internos (`QLabel`, `QRadioButton` e `QToolButton`) dentro dos cards de alternativas.

## Ajuste aplicado
- criação de overrides específicos para **enunciado** e **alternativas** em `questionSolver...`;
- cards com gradiente escuro coerente ao tema futurista;
- widgets internos configurados com `background: transparent`;
- refinamento visual de correta/errada e do botão de eliminar alternativa.

## Resultado esperado
As alternativas passam a aparecer como cards únicos, sem retângulos escuros internos, com leitura mais limpa e coerência visual com o restante do tema futurista.
