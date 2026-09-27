# VighnaStudy 0.29.28 — Dashboard: Planejamento protagonista

## Objetivo
Reorganizar apenas os quatro cards principais da primeira dobra do Dashboard para dar mais espaço ao Planejamento de hoje, sem alterar a lógica acadêmica, banco de dados, schema ou mecanismos de recomendação.

## Alterações visuais

### Primeira linha
Antes:
- Foco
- Seu progresso

Agora:
- Foco
- Planejamento de hoje

O Planejamento passa a ocupar metade da largura da primeira linha e deixa de ser um card estreito.

### Segunda linha
Antes:
- Recomendação do algoritmo (3 partes)
- Planejamento de hoje (1 parte)

Agora:
- Recomendação do algoritmo (3 partes)
- Seu progresso (1 parte)

O card Seu progresso mantém Nível, XP, barra de progresso, conquistas, próximo marco e acesso às conquistas, mas com descrição mais curta para funcionar melhor na coluna compacta.

## Novo Planejamento de hoje
O card amplo passou a funcionar como painel operacional do dia, exibindo:

- status geral: EM ANDAMENTO, ATENÇÃO, META CONCLUÍDA ou CONCLUÍDO;
- meta diária de questões com valor, progresso e barra;
- revisões pendentes, separando atrasadas e previstas para hoje;
- bloco “Para concluir o dia”, somando carga restante de questões e revisões pendentes;
- situação geral da semana;
- situação individual de Questões, Revisões e Dias de estudo: Não definida, No ritmo, Atenção ou Concluída;
- botão “VER PLANEJAMENTO COMPLETO →”.

A informação “Próximos 7 dias” continua fora do card compacto e permanece disponível no Planejamento completo.

## Regras de estado

### Dia
- CONCLUÍDO: meta diária atingida e nenhuma revisão pendente;
- ATENÇÃO: existem revisões atrasadas;
- META CONCLUÍDA: meta diária atingida, mas ainda existem revisões pendentes;
- EM ANDAMENTO: demais casos.

### Semana
Cada meta semanal é avaliada individualmente com a mesma tolerância de ritmo já usada pelo Planejamento completo:
- Não definida;
- No ritmo;
- Atenção;
- Concluída.

## Compatibilidade
- Schema: 23, inalterado.
- estudos.db: inalterado.
- Fila Inteligente / Motor de recomendação: inalterados.
- Modo Foco: inalterado.
- Central de Questões 0.29.27: preservada.
- Planejamento completo: preservado.

## Validação
- `python -m py_compile main.py versao.py`: OK
- `test_dashboard_inteligencia.py`: 7/7 OK
- `test_dashboard_planejamento_protagonista_0_29_28.py`: 7/7 OK
- Total direcionado: 14/14 OK
- `PRAGMA integrity_check`: ok
- `PRAGMA foreign_key_check`: 0 violações
- SHA-256 do `estudos.db` antes/depois da validação: idêntico.

## Versão
- VighnaStudy: 0.29.28
- Build: `dashboard-planejamento-protagonista-v1`
- Schema: 23
