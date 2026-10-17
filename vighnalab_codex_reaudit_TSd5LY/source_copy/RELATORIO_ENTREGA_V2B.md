# VighnaStudy — Relatório técnico V2-B

## Escopo implementado

- Histórico persistente sob `%LOCALAPPDATA%\VighnaStudy_Homologador_V2B` com SQLite separado.
- Cópia de cada ZIP importado em cofre local próprio, identificada por SHA-256.
- Validação de CRC, manifesto SHA-256 e do resumo antes da importação.
- Rejeição de arquivos duplicados e arquivos inválidos; não extrai nem executa evidências.
- Filtros de categoria: Qt, SQLite/Atualização, Segurança, PyInstaller, Integridade.
- Filtros por situação e pesquisa por nome/identificador.
- Comparação entre duas execuções, com mudanças de estado, contagem de testes,
  regressões e melhorias por etapa. Não compara código-fonte nem aprova instalações.
- Exportação verificável de backup com índice SQLite consistente e cópias das evidências.
- Registro automático no histórico dos novos ZIPs após cada bateria.
- Recuperação do histórico entre trocas de pasta/versão do painel.

## Proteção das versões existentes

V2-A preservada como referência; motor Windows V1.1 e 21 arquivos de segurança
permanecem idênticos. Em V2-B, apenas a interface principal e o teste de
regressão AST foram adaptados para o gancho do histórico. M2 RC2, M3 R35,
`banco.py` e o atualizador não foram modificados.

## Testes locais

- 24/24 testes novos do histórico, incluindo evidência real do usuário em
  laboratório e adulterações maliciosas sintéticas.
- 74/74 testes combinados de painel, contratos herdados e histórico.
- 82/82 testes do atualizador em dados sintéticos, preservados da V2-A.
- GUI Tkinter validada no Xvfb: cinco telas, filtros, dois relatórios sintéticos
  e comparação efetiva; capturas não equivalem à validação no Windows.
- Regressores M1–M3 e instalação principal permaneceram intocados.

## Restrições

A primeira execução da V2-B no Windows ainda está pendente.
Os metadados do ZIP descrevem o que o executor relatou: não equivalem a
inspeção integral de todas as rotinas do aplicativo. A classificação por
etapa não se confunde com número de testes unitários. Os dados do planejamento
M1–M9 continuam sendo checkpoint estático até uma futura V2-C.

Próxima evolução: V2-C — importar checkpoints verificados do planejamento.
