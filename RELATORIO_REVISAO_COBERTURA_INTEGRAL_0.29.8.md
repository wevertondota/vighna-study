# VighnaStudy 0.29.8 — Revisão por Cobertura Integral

## Problema corrigido
Uma revisão podia ser encerrada e reagendada após uma bateria parcial. Exemplo: tópico com 80 questões, bateria de 40; as 40 restantes continuavam no banco, porém a próxima revisão do tópico já podia ser empurrada para o futuro.

## Nova regra
Enquanto uma revisão estiver vencida ou prevista para hoje, todas as questões ativas do tópico formam uma **rodada de cobertura**.

- Questão coberta = recebeu resposta efetiva desde a data prevista da revisão.
- Questão pulada não conta como coberta.
- Enquanto houver pendentes, a próxima data de revisão é preservada.
- A Revisão Inteligente prioriza somente as questões ainda não cobertas, sem repetir as já vistas na rodada.
- Se a bateria tiver menos itens do que o banco, a próxima bateria continua do saldo.
- Quando a cobertura chega a 100%, o Vighna registra uma única revisão consolidada e calcula a próxima data.
- O resultado consolidado usa a tentativa efetiva mais recente de cada questão, evitando que repetições pesem artificialmente no percentual.
- Questões novas adicionadas enquanto a rodada está aberta entram automaticamente na cobertura; questões desativadas deixam o denominador.

## Compatibilidade com Treino Adaptativo
Tentativas acadêmicas válidas feitas depois da data prevista também contam como cobertura. Entretanto, um treino parcial não empurra a revisão para frente: a agenda só avança quando a cobertura do tópico chega a 100%.

## Compatibilidade com capítulos
O calendário atual continua no nível do título/tópico. Se o tópico possui capítulos, a cobertura integral engloba as questões ativas de todos os capítulos desse tópico. Não foi criado calendário independente por capítulo nesta versão.

## Recuperação de revisões recentes incompletas
Na abertura da versão 0.29.8, o programa verifica revisões deliberadas dos últimos 2 dias que tenham sido reagendadas antes da cobertura completa. Nesses casos, preserva as tentativas, remove apenas o registro prematuro de revisão e restaura a data prevista anterior para continuar a rodada.

## Interface
- A janela de revisão informa `cobertas/total` e quantidade restante.
- O limite da próxima bateria passa a ser o saldo pendente.
- O Dashboard pode mostrar `Cobertura da revisão: X/Y • N restante(s)` para o tópico prioritário.

## Validação
- Compilação de `main.py`, `banco.py`, `ciclo_estudo.py` e `versao.py`: OK.
- Testes unitários: **258 aprovados**.
- Smoke test: **OK**.
- Teste específico 80 questões em duas baterias de 40: primeira bateria não reagenda; segunda contém somente as 40 restantes; ao final é criada uma revisão única de 80 questões.
- Teste de recuperação de revisão recente reagendada prematuramente: aprovado.
- Em uma cópia do banco de referência de 2.551 questões, a rotina identificou um caso real em `Português > Hífen`: 36 questões ativas, 15 cobertas e 21 pendentes, com revisão que havia sido reagendada prematuramente. A rotina reabriu essa rodada na cópia de teste, preservando as tentativas.

## Arquivos alterados
- `banco.py`
- `ciclo_estudo.py`
- `main.py`
- `versao.py`
- `test_revisao_cobertura_integral.py`

Nenhum `estudos.db` faz parte desta atualização.
