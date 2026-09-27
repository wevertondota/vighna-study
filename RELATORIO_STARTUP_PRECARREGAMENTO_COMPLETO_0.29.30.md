# VighnaStudy 0.29.30 — startup com pré-carregamento completo

## Objetivo

Concentrar o custo da primeira carga antes da entrada no Dashboard, exibindo uma tela de inicialização com progresso real por etapas. O objetivo é evitar que a primeira visita a Central de Questões, Estatísticas, Relatórios, Calendário, Resumo do dia e disciplinas pague novamente o custo de construção/carregamento inicial.

## Estratégia

A janela principal é criada oculta. Uma tela de inicialização é exibida primeiro e informa a etapa corrente. Antes de mostrar o Dashboard, o Vighna prepara:

- Dashboard, planejamento, progresso e recomendação;
- estrutura das disciplinas e cache dos tópicos do perfil ativo;
- Central de Questões, catálogo, contadores e duplicidades;
- Resumo do dia;
- Calendário do mês atual;
- tela de sessão de estudo e, se houver sessão ativa, seu estado atual;
- todas as abas de Estatísticas;
- resumo e todas as abas de Relatórios no período padrão.

Somente depois dessa sequência a janela principal é exibida.

## Tela de inicialização

A nova `JanelaInicializacao` mostra:

- identidade VighnaStudy;
- indicador animado discreto;
- nome da etapa atual;
- descrição do trabalho em andamento;
- barra de progresso por etapas reais.

O carregamento não possui atraso artificial: se o computador terminar cedo, o Dashboard abre imediatamente.

## Reaproveitamento após o startup

- a Central reutiliza o catálogo já carregado enquanto não houver invalidação;
- Estatísticas e Relatórios entram com as abas padrão já preenchidas e estados limpos;
- Resumo do dia e Calendário reutilizam a primeira carga enquanto a data/dados não mudarem;
- disciplinas reutilizam os tópicos aquecidos no startup;
- a sessão de estudo não recalcula o Dashboard se ele continuar limpo.

## Invalidação

A otimização não congela os dados. Alterações acadêmicas continuam invalidando os caches afetados. Depois de responder/importar/arquivar questões, registrar revisões ou mudar estruturas acadêmicas, as áreas pertinentes podem recalcular normalmente. Isso é necessário para não exibir informação antiga.

Portanto, a mudança elimina principalmente os carregamentos da primeira navegação; ela não tenta pré-calcular ações futuras ou filtros que ainda não foram escolhidos pelo usuário.

## Responsividade da tela de startup

O pré-carregamento foi dividido em etapas menores e chama o event loop entre elas para manter a tela de inicialização repintando e atualizando mensagens. Operações individuais muito pesadas e ainda síncronas podem interromper a animação por um curto período; eliminar isso completamente exigiria separar consultas e montagem de widgets em workers/threads, uma alteração arquitetural maior.

## Banco e schema

- `VIGHNA_VERSION = 0.29.30`
- `VIGHNA_BUILD = startup-precarregamento-completo-v1`
- `VIGHNA_SCHEMA = 23`
- nenhuma migração de schema;
- `estudos.db` não foi modificado.

## Validações neste ambiente

- `python -m py_compile main.py versao.py banco.py backup.py`: OK
- `test_startup_precarregamento_completo_0_29_30.py`: 7/7 OK
- `test_startup_integridade_rapida_0_29_22.py`: 3/3 OK
- `PRAGMA integrity_check`: `ok`
- `PRAGMA foreign_key_check`: 0 violações
- SHA-256 do `estudos.db` antes/depois: idêntico

## Limitação de validação

O ambiente de empacotamento desta resposta não possui PySide6 instalado. Por isso, a confirmação visual do splash e a medição real de tempo no Windows devem ser feitas executando o projeto em `C:\SistemaEstudos`.
