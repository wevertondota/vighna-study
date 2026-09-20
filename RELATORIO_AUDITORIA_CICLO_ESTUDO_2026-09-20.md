# VighnaStudy — Auditoria do ciclo principal de estudo

Data da intervenção: 20/09/2026  
Versão: 0.29.3  
Build: `study-cycle-audited`

## Objetivo

Entrar em uma fase de estabilização: em vez de adicionar novas funções ao VighnaStudy, verificar se o ciclo principal funciona de ponta a ponta e se cada sessão realmente alimenta corretamente o histórico, as revisões, as métricas e a próxima recomendação.

Cadeia auditada:

`Recomendação -> Sessão -> Fila congelada -> Tentativas -> Resultado -> Revisão automática -> Próximo agendamento -> Núcleo estatístico -> Nova recomendação`

## Alterações estruturais

### 1. Núcleo puro do ciclo acadêmico

Foi criado `ciclo_estudo.py` e a regra de integração `sessão de questões -> revisão automática` foi retirada da dependência direta da interface Qt. `main.py` agora delega a integração para esse núcleo.

Isto permite testar a regra acadêmica isoladamente, sem abrir a interface, e reduz o risco de uma mudança visual alterar o comportamento do estudo.

Regras preservadas:

- 1–4 questões em tópico já conhecido: registra atividade, sem criar nova revisão;
- 5–9 questões: revisão de baixa confiança, preservando o agendamento anterior;
- 10+ questões: revisão normal, recalculando a próxima revisão;
- primeiro contato: qualquer resolução efetiva cria a primeira revisão, com intervalo conservador em amostras pequenas.

### 2. Auditoria não destrutiva do ciclo

Foi criado `auditoria_ciclo_estudo.py`. A auditoria somente lê o banco e verifica, entre outros pontos:

- perfil da tentativa x perfil da sessão;
- tentativa x item real da fila congelada;
- sessão concluída sem encerramento;
- quantidade planejada x fila realmente congelada;
- linhagem de perfil das revisões novas;
- tentativa apontando para revisão inexistente;
- sessões elegíveis que terminaram sem consolidação em revisão;
- datas inválidas de próxima revisão;
- contagens brutas de respostas/acertos x Núcleo Estatístico.

A janela já existente de Diagnóstico ganhou o botão **Auditar ciclo de estudo**. Quando aberta pela janela principal, a auditoria também tenta exibir a recomendação atual do Motor V5 e seu ranking/evidências para inspeção.

### 3. Preservação da origem da recomendação ao usar Modo Foco

Foi corrigida a rastreabilidade do caminho:

`Recomendação do Motor V5 -> Modo Foco -> questões`

Antes, ao passar pelo Foco, a bateria podia ser registrada apenas com origem `foco`, perdendo a informação de que havia nascido de uma recomendação do algoritmo. Agora a origem `algoritmo_v5` acompanha a preparação do Foco e chega à sessão de questões.

Isso melhora a auditoria futura do comportamento do motor sem mudar a experiência de estudo.

### 4. Testes de horário oficial

Os testes do Núcleo Estatístico e do smoke histórico foram alinhados ao timezone oficial `America/Sao_Paulo`. O problema observado no ambiente de teste ocorria na virada de data entre UTC e horário brasileiro; não foi alterada a semântica estatística de produção.

## Teste novo de ciclo completo

Foi adicionado `test_ciclo_estudo.py`, cobrindo:

1. bateria de 10 questões recomendada pelo Motor V5;
2. registro de 8 acertos / 2 erros;
3. encerramento da sessão;
4. criação da revisão automática;
5. preservação do `concurso_id`;
6. ligação das tentativas à revisão;
7. geração da próxima revisão;
8. conferência das métricas oficiais;
9. auditoria estrutural sem erro;
10. bateria curta posterior em tópico conhecido sem revisão forçada;
11. preparação do Modo Foco preservando `origem_sessao = algoritmo_v5`.

## Resultado da suíte automatizada

- 247 testes automatizados executados com sucesso;
- `testes_smoke.py`: OK;
- compilação Python do projeto: OK.

Há avisos de `ResourceWarning` em alguns testes antigos devido a conexões SQLite abertas por rotinas legadas; eles não causaram falha e não foram tratados nesta intervenção para não ampliar o escopo.

## Auditoria do banco real do checkpoint

Perfil auditado: **GCM Toledo (id 40)**  
Data de referência: **19/09/2026**

Resultado: **ATENÇÃO, sem erro estrutural novo**.

Métricas encontradas:

- respostas brutas do perfil: 123;
- acertos brutos: 100;
- Núcleo Estatístico: 123 respostas / 100 acertos;
- revisões com linhagem explícita desse perfil: 0;
- revisões históricas sem linhagem explícita: 4;
- revisões vencidas/para hoje no universo ativo: 5.

A única atenção é histórica: existem quatro revisões antigas sem `concurso_id`. Elas são anteriores ao marco de migração de linhagem e, por segurança, continuam sem atribuição automática a um perfil. Não foram alteradas nem “adivinhadas”.

Não foram encontradas divergências estruturais novas entre sessões, tentativas, revisões e métricas.

## Próxima fase recomendada

Usar o VighnaStudy normalmente por alguns dias e, quando houver sessões novas do Motor V5, executar **Configurações/Diagnóstico -> Auditar ciclo de estudo**. O objetivo agora é observar com dados reais se:

- a recomendação escolhida é coerente;
- a origem da sessão permanece auditável;
- o desempenho altera domínio e revisão como esperado;
- a próxima recomendação reage corretamente ao estudo concluído.

Nesta fase, novas funcionalidades devem permanecer em segundo plano até que o comportamento real da fila esteja suficientemente validado.
