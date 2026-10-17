# VighnaStudy — Painel V3 | Gates e sincronização manual

Checkpoint: 12/10/2026. **Aplicativo de testes independente; não instalar no VighnaStudy.**

## Novas áreas

- **Gates de liberação:** sete etapas G1–G7; G1 preflight e guardas;
  G2 Qt Windows nos três fatores de escala; G3 SQLite/rollback sintéticos;
  G4 PyInstaller em laboratório; G5 smoke EXE real isolado; G6 atualização
  final e rollback Windows; G7 auditoria e aprovação humana.
- Os quatro primeiros são classificados apenas com evidências do histórico
  importado, por candidato RC2. Nunca mescla testes Qt de execuções
  diferentes para declarar 3/3. Falha ou bloqueio do último relatório
  aplicável impede o status de "evidenciado".
- Os gates G5–G7 ficam **pendentes**: o painel atual não executa esses gates.
  Nenhum dos sete resulta em liberação automática de instalação.
- **Sincronização:** importar ZIP de planejamento com APENAS dois JSON
  (`planejamento.json`, `manifesto.json`); esquema e campos validados,
  SHA-256 integral, prévia e confirmação manual; substituição atômica no
  diretório próprio do painel; uma versão anterior é preservada.
- **Exportar status:** produz ZIP com dados do planejamento e resumo de
  gates, sem arquivo de banco pessoal; deve ser anexado manualmente à conversa.

## Proteções e limites

SHA-256 é prova de integridade de bytes, **não assinatura digital e nem
certificado de procedência**. Checkpoints devem ser importados somente de
fontes em que o usuário confia. Importação de planejamento jamais modifica
código do VighnaStudy, motor de testes, estados do Resolvedor ou autorização.

O histórico permanece no diretório próprio já utilizado pela V2-B.
O engine de homologação Windows e os arquivos de atualização QA foram
preservados byte a byte; não houve alteração em banco pessoal.

## Resultados da validação local

- 101/101 testes Python de componentes, históricos, contratos e segurança.
- 82/82 testes do motor de atualização e rollback com bancos sintéticos.
- Smoke de interface Tk em Xvfb: sete páginas, nove macrolotes, sete gates.
- Importação da última evidência real Windows do usuário: G1–G3 evidenciados;
  G4–G7 pendentes; nenhuma autorização de instalação.
- Selftest dos hashes do motor herdado, aprovado.
- Qt nativo e PyInstaller Windows da **nova V3** ainda dependem da primeira
  execução pelo usuário no Windows. Os resultados da V2-B não devem ser
  apresentados como uma validação do código visual novo.
