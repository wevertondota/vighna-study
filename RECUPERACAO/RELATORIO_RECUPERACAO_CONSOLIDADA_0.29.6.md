# Recuperação consolidada — VighnaStudy 0.29.6

Base utilizada: pasta `SistemaEstudos` enviada pelo usuário em 20/09/2026, após a adição das 14 novas questões de Direito Penal.

## Estado encontrado

- registros físicos em `questoes`: 2.522;
- questões ativas: 2.509;
- Direito Penal: 270 questões ativas;
- Título VI — Crimes contra a Dignidade Sexual: 18 questões ativas;
- lixeira: 13 questões.

Não havia nenhum backup com nome `estudos_antes_merge_recuperacao_*`, o que demonstra que o merge anterior não chegou à etapa de gravação/backup na pasta enviada.

## Correção aplicada diretamente no banco atual

O banco da raiz foi preservado e recebeu apenas as 42 questões recuperadas ausentes. Nenhum registro pré-existente de `questoes` ou `alternativas_questoes` foi alterado.

Resultado:

- registros físicos: 2.564;
- questões ativas: 2.551;
- Direito Penal: 312 questões ativas;
- Crimes contra a Dignidade Sexual: 54 questões ativas;
- lixeira: 13 questões;
- `PRAGMA integrity_check`: `ok`;
- `PRAGMA foreign_key_check`: 0 problemas.

### Distribuição das 42 recuperadas

- Título VI / sem capítulo: 5;
- Título VI / Capítulo I — Liberdade Sexual: 7;
- Título VI / Capítulo II — Crimes Sexuais contra Vulnerável: 18;
- Título VI / Capítulo IV — Ultraje Público ao Pudor: 6;
- Título XII / Capítulo II — Crimes contra Instituições Democráticas: 6.

## Hardening aplicado

1. `estudos.db` da raiz permanece como única fonte de dados.
2. `atualizar_exe.bat` não copia banco de `dist` de volta para a raiz.
3. Os dois BATs de recuperação agora executam merge idempotente, nunca substituição total do banco.
4. Foi criado `VERIFICAR_BANCO_ATIVO.bat` / `auditar_banco_ativo.py` para mostrar o caminho real e as contagens do banco usado.
5. O Diagnóstico do Vighna passa a exibir questões ativas, registros físicos, lixeira e total de Dignidade Sexual.
6. Versão elevada para 0.29.6 (`database-recovery-verified-root-v2`).

## Observação sobre o RAR recebido

A extração encontrou erros de checksum em dois arquivos antigos de backup (`dist/SistemaEstudos ANTIGO/...` e `estudos_backup_antes_backup_automatico.db`). O `estudos.db` ativo, os fontes e os arquivos de recuperação foram extraídos normalmente e passaram na verificação SQLite.
