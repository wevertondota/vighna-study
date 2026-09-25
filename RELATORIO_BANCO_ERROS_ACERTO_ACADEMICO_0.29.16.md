# VighnaStudy 0.29.16 — Banco de Erros: acerto acadêmico resolve pendência

## Objetivo
Fazer o Banco de Erros representar o estado operacional atual da questão. Uma questão entra ou permanece na fila quando ocorre erro acadêmico real e sai da fila quando ocorre acerto posterior, seja dentro do próprio Banco de Erros ou em qualquer sessão acadêmica normal.

## Regra consolidada
- Erro acadêmico real: cria ou mantém a pendência.
- Acerto acadêmico posterior: remove somente a pendência temporária do Banco de Erros.
- Acerto dentro do Banco de Erros: remove a pendência, sem criar tentativa acadêmica.
- Erro dentro do Banco de Erros: mantém a pendência, sem criar tentativa acadêmica.
- Pulo sem resultado acadêmico: não altera a pendência já existente.
- Novo erro acadêmico depois de uma recuperação: reinsere a questão na fila.

## Preservação acadêmica
A remoção da pendência não apaga nem reescreve:
- tentativas anteriores;
- snapshots históricos;
- Caderno de Erros;
- domínio;
- revisões;
- estatísticas;
- gamificação;
- recomendações.

O acerto feito em revisão, treino adaptativo, simulado ou outra sessão acadêmica continua sendo uma tentativa normal e produz os efeitos acadêmicos já existentes. A única nova consequência é a remoção da pendência operacional do Banco de Erros para aquele perfil e questão.

## Implementação
A regra foi centralizada em `registrar_tentativa_questao()` em `banco.py`, que já é o registrador canônico das respostas acadêmicas. Assim, não foi necessário duplicar lógica na interface ou em cada modo de sessão.

Após inserir a tentativa:
- `resultado == 0`: `_inserir_pendencia_banco_erros(...)`;
- `resultado == 1`: `DELETE FROM banco_erros_pendentes WHERE concurso_id = ? AND questao_id = ?`;
- `resultado is None`: nenhuma alteração na fila.

A remoção é específica do perfil (`concurso_id`) e da questão, preservando pendências do mesmo item em outros perfis.

## Banco de dados
- Schema: 22 (inalterado)
- Nenhuma migração necessária.
- `estudos.db` não é alterado pelo patch de código.

## Validação
- `py_compile`: OK
- Testes direcionados Banco de Erros + regressão do resolvedor: 41/41 OK
- `testes_smoke.py`: OK (`VighnaStudy 0.29.16: testes smoke OK`)
- Descoberta completa da suíte foi iniciada; 76 testes haviam passado sem falhas antes de atingir o limite de tempo do ambiente. Nenhuma falha foi registrada no trecho executado.
- Banco temporário: `PRAGMA integrity_check = ok` e `PRAGMA foreign_key_check = []` nos testes.

## Casos novos cobertos
1. acerto acadêmico posterior remove a pendência;
2. remoção ocorre somente no perfil que acertou;
3. pulo acadêmico não remove pendência;
4. novo erro acadêmico reinsere após recuperação;
5. histórico de tentativas permanece com erro anterior e acerto posterior.

## Versão
- VighnaStudy: 0.29.16
- Build: `banco-erros-acerto-academico-v1`
- Schema: 22
