# VighnaStudy 0.29.59 — previsão semanal no Calendário

## Objetivo
Adicionar ao setor Calendário uma visão semanal de segunda a domingo, mostrando o que já foi estudado nos dias anteriores e os tópicos/atividades que o Vighna provavelmente recomendará de hoje em diante se o estado atual de estudo não mudar.

## Interface
O antigo título **Calendário de Revisões** foi ampliado para **Calendário de Estudos** e agora possui duas visualizações:

- **Mês**: preserva integralmente o calendário de revisões existente e a lista do dia;
- **Semana prevista**: mostra **segunda a domingo** em sete colunas. Dias anteriores exibem o estudo efetivamente registrado; hoje combina o que já foi realizado com a projeção restante; os dias seguintes exibem a previsão atual.

A parte preditiva só é calculada quando o usuário abre essa visualização. Portanto, o pré-carregamento do Calendário na inicialização continua leve.

## Fonte da previsão
A nova visualização não cria um segundo algoritmo de recomendação. Ela reutiliza o **Plano de Ação Automático V2**, que já consolida:

- revisões vencidas e programadas;
- Relatório Estratégico;
- Índice de Domínio V2;
- Seleção Adaptativa V2;
- metas configuradas;
- tempo real do Modo Foco e rotação entre disciplinas.

A carga usada é a carga do plano automático ativo, quando existente; na ausência dela, usa **Moderada**.

## Realizado + previsão
Os dias já transcorridos da semana usam os registros reais de revisões/questões por tópico. No dia atual, conteúdos já estudados aparecem como **Estudado hoje** e têm precedência sobre uma recomendação equivalente, evitando duplicidade.

## Revisões por tópico
O Plano Automático agrupa revisões em alguns cenários. Para a visão semanal, esses grupos são deliberadamente desmembrados para exibir o **tópico real** em seu respectivo dia. Revisões vencidas ou previstas para hoje aparecem na coluna de hoje; revisões futuras permanecem na data já agendada.

Quando revisão e recomendação convergem para o mesmo tópico no mesmo dia, o tópico é exibido uma única vez, dando precedência à revisão fixa.

## Cards
Cada card apresenta:

- disciplina;
- tópico/atividade;
- tipo da recomendação;
- quantidade de questões, quando aplicável;
- motivo resumido;
- botão para abrir diretamente o tópico, quando há `topico_id`.

O card também possui tooltip **“Por que isso está aqui?”** com o motivo completo disponível no motor.

## Atualização
A previsão é invalidada quando mudam dados capazes de alterar a recomendação, incluindo:

- questões e tentativas;
- revisões;
- tópicos;
- sessões de foco;
- recomendações/decisões adaptativas.

Há também o botão **↻ Recalcular previsão**. A tela informa o horário da última atualização e deixa explícito que se trata de uma projeção, não de uma agenda fixa.

## Temas
Foram criados estilos específicos para:

- Claro;
- Escuro;
- Futurista.

O dia atual recebe destaque próprio; Revisão, Recomendação e Simulado usam acentos visuais distintos sem alterar os dados.

## Persistência e banco
Não houve mudança de schema nem gravação nova para o recurso. A previsão é derivada dos dados existentes e não altera automaticamente datas de revisão, sessões ou prioridades.

## Validação
- `py_compile`: aprovado para `main.py`, `banco.py`, `tema.py` e `versao.py`;
- teste específico 0.29.59: **10/10**;
- regressões funcionais da 0.29.55–0.29.58, excluindo apenas asserts de versão antiga: **21/21**;
- geração real do Plano Automático V2 no banco do checkpoint: aprovada para horizonte de 7 dias;
- `PRAGMA integrity_check`: **ok**;
- `PRAGMA foreign_key_check`: **0 violações**.

## Versão
- Versão: **0.29.59**
- Build: `calendar-week-forecast-v1`
- Schema: **25**
