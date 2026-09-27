# VighnaStudy 0.29.21 — correção de recuperação segura do banco

## Problema observado
Após uma atualização por substituição de arquivos, o VighnaStudy pode encontrar um `estudos.db` acompanhado por arquivos `estudos.db-wal` / `estudos.db-shm` incompatíveis com a cópia atual. Nessa situação o SQLite pode retornar `database disk image is malformed` e o Vighna bloqueia a abertura para evitar novas gravações.

O `estudos.db` contido no checkpoint 0.29.20 foi revalidado separadamente com `PRAGMA quick_check` e `PRAGMA integrity_check`, ambos com resultado `ok`. A correção abaixo trata o cenário de corrupção local durante/após substituição e reforça o fluxo de restauração.

## Alterações
- `recuperar_banco.bat` fecha instâncias do Vighna antes de manipular o banco.
- `recuperar_banco.py` testa primeiro uma cópia isolada do `estudos.db`, sem WAL/SHM. Se ela for íntegra, essa versão mais recente é priorizada antes de backups antigos.
- A cópia bruta do banco problemático e de seus WAL/SHM continua sendo preservada antes da restauração.
- `checkpoint.py` passou a restaurar snapshots por arquivo temporário + validação + remoção de WAL/SHM + substituição atômica.
- A restauração do banco diretamente de dentro do Vighna foi bloqueada: restaurar um banco enquanto a aplicação possui conexões abertas é inseguro.
- `main.py` informa que o banco de checkpoint deve ser restaurado externamente, com o Vighna fechado, via `recuperar_banco.bat`.
- Versão: `0.29.21`, build `banco-seguro-recuperacao-wal`.
- Schema permanece `22`.

## Novo procedimento para atualizações
Checkpoints/patches distribuídos para aplicação manual não devem substituir `estudos.db`. Alterações de conteúdo do banco devem ocorrer por migração transacional no banco local, precedida por snapshot SQLite e seguida por `PRAGMA integrity_check`.

## Validação
- `recuperar_banco.py`, `checkpoint.py`, `main.py` e `versao.py`: compilação Python OK.
- 95 arquivos Python da árvore testada: 0 erros de compilação.
- Teste de candidato isolado sem WAL/SHM: OK.
