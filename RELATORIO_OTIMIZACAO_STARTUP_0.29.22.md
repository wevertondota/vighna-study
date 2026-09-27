# VighnaStudy 0.29.22 — otimização do startup após recuperação do banco

## Diagnóstico

A proteção contra banco corrompido executava `PRAGMA integrity_check` de forma síncrona dentro de `SistemaEstudos.__init__`, antes da abertura normal da interface. Em máquinas Windows esse exame completo pode custar vários segundos e passou a integrar o caminho crítico da inicialização após a correção de recuperação do banco.

Além disso, o backup automático de abertura era disparado apenas 700 ms após o início do event loop. O snapshot é consistente e sua validação completa deve permanecer, mas disputar I/O com a primeira atualização do Dashboard piora o tempo percebido de abertura.

## Alterações

- verificação preventiva do startup usa `PRAGMA quick_check(1)` em modo somente leitura;
- `PRAGMA integrity_check` completo continua disponível por `verificar_integridade_banco(..., completo=True)` e continua sendo usado nas rotinas que validam snapshots/backups;
- backup automático de abertura foi adiado de 700 ms para 15 s, fora do caminho crítico inicial;
- primeira atualização pesada do Dashboard passa de 15 ms para 120 ms, deixando o Qt processar o primeiro repaint antes das consultas;
- nenhuma alteração no schema do banco (`VIGHNA_SCHEMA = 22`);
- nenhum `estudos.db` é distribuído neste patch.

## Segurança

O `quick_check(1)` continua bloqueando bancos SQLite estruturalmente malformados na abertura. A auditoria completa não foi removida das rotinas de backup/recuperação; ela apenas deixou de ser executada sincronicamente em toda inicialização normal.
