# VighnaStudy 0.29.10 — Cobertura visível e tratamento de questões puladas

## Objetivo

Esta atualização implementa dois ajustes ligados à qualidade das revisões:

1. tornar a cobertura da revisão visível na tela da disciplina;
2. fazer uma questão pulada retornar ao fim da mesma bateria e, se for pulada novamente, tratá-la como erro efetivo pela inteligência.

## 1. Interface de cobertura

A tabela de tópicos ganhou a coluna `Cobertura`, posicionada entre `Próxima` e `% atual`.

Quando existe uma revisão vencida/aberta, o Vighna mostra, por exemplo:

- Próxima: `21/09/2026`
- Cobertura: `72/87`

Ao selecionar o tópico, o painel superior também informa:

`Revisão em andamento: 72/87 • restam 15 • próxima data após concluir a cobertura`

A data na coluna `Próxima` continua sendo a referência da rodada enquanto a revisão estiver aberta. A nova data só é calculada após cobertura integral.

No banco analisado de Habilitação, o estado real é:

- total ativo: 87;
- cobertas: 72;
- pendentes: 15;
- cobertura: 82,8%;
- referência da revisão: 21/09/2026.

## 2. Questão pulada

### Primeiro pulo
- a tentativa é registrada como `pulada`;
- não conta como resposta efetiva;
- não fecha cobertura;
- a questão é automaticamente colocada no fim da mesma bateria;
- a interface identifica o retorno como `retorno de questão pulada`.

### Segundo pulo
- não há terceira reapresentação;
- a tentativa é gravada com `correta = 0`;
- recebe origem de snapshot `pulo_reincidente`;
- passa a contar como erro para a inteligência;
- passa a contar como questão coberta na rodada de revisão;
- alimenta os mesmos mecanismos que uma resposta incorreta normal.

A alternativa marcada permanece nula, preservando que o usuário não escolheu resposta.

## 3. Pós-bateria

O número principal de `Questões` no resumo guiado continua representando o objetivo original da bateria, sem ser inflado pelas reapresentações decorrentes de pulo.

## Segurança

- Nenhum `estudos.db` acompanha esta atualização.
- Não há migração destrutiva de schema.
- O histórico existente não é alterado retroativamente.
- A nova regra vale para novas sessões após a atualização.

## Validação realizada

- `python -m py_compile banco.py main.py versao.py`: OK.
- testes do fluxo pós-bateria 0.29.9: 3/3 OK.
- teste funcional em cópia do banco atual:
  - primeiro pulo -> `correta = NULL`, item `pulada`;
  - item reagendado para o fim;
  - segundo pulo -> `correta = 0`, origem `pulo_reincidente`, item `respondida`;
  - a segunda ocorrência passa a integrar a cobertura como erro.
- conferência no banco enviado:
  - Habilitação: 72/87 cobertas, 15 pendentes.

## Versão

- VighnaStudy: 0.29.10
- Build: `revision-coverage-skip-retry-v1`
