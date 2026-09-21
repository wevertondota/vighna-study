# VighnaStudy 0.29.7 — Sessão Adaptativa V2 com recorte hierárquico

## Objetivo
Organizar a configuração da Sessão Adaptativa V2 para facilitar a escolha do conteúdo sem alterar a lógica acadêmica já estabilizada.

## Alterações de interface
- Novos escopos diretos: `Disciplina`, `Título / tópico` e `Capítulo`.
- Seletores dependentes: ao escolher uma disciplina, o Vighna carrega apenas seus títulos; ao escolher um título, carrega apenas seus capítulos ativos.
- `Tópicos selecionados` foi preservado e recebeu busca por disciplina/título e ação `Marcar visíveis`.
- Menus suspensos de título e capítulo usam popup mais largo e tooltip com o nome integral.
- O plano proposto mostra o recorte completo acima da tabela.
- A coluna `Título / tópico` recebeu mais espaço, linhas mais altas e tooltip com o texto integral.
- A janela padrão foi ampliada para 1180 × 790, mantendo mínimo de 980 × 680.

## Alterações funcionais
O recorte por capítulo agora é real, não apenas visual. As funções da Seleção Adaptativa V2 aceitam `capitulos_ids` e:
- calculam a disponibilidade somente das questões pertencentes ao capítulo escolhido;
- montam o plano somente com essa capacidade;
- selecionam a fila final somente dentro do capítulo escolhido.

A prioridade, domínio e calendário de revisão continuam no nível do **tópico/título pai**. O capítulo funciona como filtro de questões da sessão e não cria uma agenda ou domínio independente. Isso preserva a arquitetura acadêmica atual.

## Integridade
- Nenhuma migração de banco foi criada.
- Nenhuma questão, tentativa, revisão ou estatística foi alterada.
- A atualização não precisa substituir `estudos.db`.

## Validação
- `main.py`, `banco.py` e `versao.py`: compilação Python OK.
- Teste específico de recorte por capítulo: 2 testes aprovados.
- Suíte completa: **257 testes + 16 subtestes aprovados**.
