# Relatório técnico — Painel V3.1.16 / G6-B1

Data: 13/10/2026  
Base: Painel V3.1.15  
Destino: Painel V3.1.16  
Escopo: homologador independente; nenhum arquivo ou banco da instalação principal foi utilizado.

## Resultado

O G6-B1 concluiu os três cenários obrigatórios no Windows Sandbox, sem rede e
com entradas QA montadas como somente leitura. O resultado real do guest foi
`PASSOU_B1_EXECUTAVEIS_REAIS` no laboratório
`G6B_Laboratorios/G6B1_20261013_122328_291614`.

Esse resultado aprova somente o ensaio G6-B1. O Gate G6 não foi aprovado:
G6-B2 (compilação original end-to-end dentro do Sandbox) e G7 permanecem
pendentes. O M2 RC2 continua proibido para instalação no VighnaStudy principal.

## Causa raiz

O código V3.1.15 calculava o hash do `estudos.db` sintético imediatamente após
criar apenas `g6b_marker`. Em seguida, somente no cenário de sucesso, iniciava o
executável R1D. O R1D encontra o banco sintético na raiz QA por `caminhos.py` e,
na primeira abertura, `banco.criar_banco()` cria o schema completo, executa
migrações/backfills, ativa WAL e otimiza o banco. Assim, o hash comparado depois
da transação necessariamente diferia do hash anterior ao startup, embora o
motor de atualização não tivesse corrompido o banco.

A instrumentação V3.1.16 também demonstrou que a abertura posterior do RC2 (e
do R1D restaurado) altera `sqlite_sequence` por operações idempotentes de
startup. Esse estado é metadado físico de alocação do SQLite: schema, registros
das tabelas da aplicação, marcador QA, integridade e chaves estrangeiras
permaneceram idênticos. A igualdade física e lógica continua obrigatória entre
o baseline pós-R1D e o término da transação/reversão.

## Alterações implementadas

- Baseline transacional movido para depois da inicialização real do R1D em cada cenário.
- Smoke real do R1D antes dos três cenários e smoke do RC2/R1D restaurado ao final.
- Snapshots SQLite nos quatro momentos exigidos, mais snapshot do backup permanente.
- Registro de SHA-256 e tamanho de `estudos.db`, `-wal`, `-shm` e `-journal`.
- Registro de PRAGMAs, schema, colunas, contagem e hash determinístico dos registros.
- `integrity_check`, `foreign_key_check` e marcador QA verificados em cada etapa.
- Metadados `sqlite_*` registrados separadamente como estado físico.
- Primeira divergência com categoria, item e valores esperado/encontrado.
- Cenário parcial preservado no resultado mesmo quando ocorre exceção.
- `DIAGNOSTICO_SQLITE_G6B1.json` separado e protegido pelo manifesto do guest.
- Evidência do host não trunca os relatórios SQLite.
- Encerramento da instância descartável de Sandbox iniciada pelo próprio host.

## Testes executados

### Unitários e regressão do G6-B1

Comando: `python -m unittest -v test_painel_g6b.py`  
Resultado final: 21 testes executados, 21 aprovados.

Coberturas novas: snapshot físico/lógico, auxiliares WAL/SHM, primeira tabela
divergente, evidência parcial, baseline depois do R1D, classificação física de
`sqlite_sequence` e encerramento da própria instância Sandbox.

### Suíte completa do painel

Foram executados 240 testes: 226 passaram, 5 foram ignorados e 9 falharam fora
do escopo desta correção. As falhas não foram ocultadas: ambiente Tcl/Tk sem
`init.tcl`, privilégio de symlink ausente no Windows, handles de testes
históricos, expectativas legadas com mojibake e asserções antigas de versão.
Todos os testes de `test_painel_g6b.py` passaram nessa mesma execução.

### Windows Sandbox real

Laboratório aprovado: `G6B1_20261013_122328_291614`.

| Cenário | Resultado | Checkpoint | Histórico | Banco |
|---|---|---|---|---|
| atualização normal | `PASSOU_B1_TRANSACAO_REAL` | `installed` | `installed` | preservado |
| falha de compilação | `PASSOU_B1_ROLLBACK_REAL` | `pre_commit_no_snapshot` | `failed` | preservado |
| falha após commit | `PASSOU_B1_ROLLBACK_REAL` | `recovered` | `failed` | preservado |

Nos três cenários, o R1D abriu de forma estável antes da transação e o
executável final abriu de forma estável. A comparação transacional registrou
`logica_alterada=false` e `fisica_alterada=false`. O backup foi logicamente
equivalente e as diferenças físicas de startup foram registradas sem reduzir a
verificação transacional.

### Pacote incremental

O ZIP V3.1.15 → V3.1.16 foi inspecionado, aplicado e revertido pelo
`painel_atualizador.py` em
`testes/PACOTE_V3116_QA_20261013_123119_413390`. A versão avançou para 3.1.16,
voltou para 3.1.15 e todos os seis hashes originais foram restaurados.

## Evidência principal

- `G6B_Laboratorios/G6B1_20261013_122328_291614/SAIDA/G6_B1_DIAGNOSTICO_20261013_122825_301669.zip`
- `RESULTADO_G6B1.json`: SHA-256 `e9fb0ec420ac6daf36f59461c0673e0b0e67864f81ad047834248cae2956ee33`
- `DIAGNOSTICO_SQLITE_G6B1.json`: SHA-256 `1b04ea91f28d2137f0ffb9b926f9a5dee49184f219f48f357178d80fb9970bea`

Os hashes acima foram recalculados fora do guest e coincidem com
`MANIFESTO_G6B1_SHA256.json`.

## Arquivos de código/configuração alterados

- `painel_g6b_guest.py`
- `painel_g6b.py`
- `test_painel_g6b.py`
- `painel_homologacao.py`
- `PAINEL_VERSAO.json`
- `ATUALIZACOES_PAINEL_LEIA.md`

Foi preservado um backup pré-alteração em
`BACKUP_ANTES_V3_1_16_20261013`. Laboratórios anteriores não foram apagados ou
sobrescritos.
