# Matriz de achados F-01 a F-09

Os rótulos abaixo reconciliam os nove controles solicitados com a evidência disponível nesta entrega. “Corrigido” vale somente para o escopo ensaiado; não concede aprovação de gate ou instalação.

| ID | Controle reavaliado | Classificação | Evidência | Limite remanescente |
|---|---|---|---|---|
| F-01 | Identidade frozen vinculada à versão e ao hash exato de `PAINEL_VERSAO.json` | **CORRIGIDO** | Testes 01/02 da reconciliação e manifesto 60/60 | SHA-256 não é assinatura digital do EXE |
| F-02 | Adulteração `3.1.99`, JSON reordenado e recurso ausente | **CORRIGIDO** | Testes negativos 03, 04 e 05 falharam fechados | Teste em fonte; build real não executado |
| F-03 | Recurso redirecionado por symlink/junction | **PARCIAL** | Junction real detectada; guardas sintéticas passaram | Symlink real não testado por `WinError 1314` |
| F-04 | Execução frozen sem `_MEIPASS` | **CORRIGIDO** | Teste 06 confirmou `RuntimeError` fechado | Não houve EXE PyInstaller real |
| F-05 | G5-B/C, G6-A/B1/B2 e bateria geral pela interface frozen | **MITIGADO POR BLOQUEIO** | Todas as seis entradas retornaram antes de subprocesso | Funcionalidade não existe no EXE; gates continuam pendentes |
| F-06 | Invocação direta dos workers no modo frozen | **MITIGADO POR BLOQUEIO** | Sete workers chamados diretamente; nenhum `Popen` permitido | Bloqueio não equivale a executar os gates |
| F-07 | Configuração, pasta sem escrita, legado somente leitura e redirecionamentos | **PARCIAL** | LOCALAPPDATA, `PermissionError`, legado e junction real passaram | Symlink real permaneceu não testado |
| F-08 | Diagnósticos em TEMP, dossiê G7 persistente e nenhuma escrita em `_MEIPASS` | **CORRIGIDO** | Checks adicionais e testes 11/11a passaram | G7 formal continua fora de escopo |
| F-09 | Completude operacional, regressões dependentes e build do `.spec` | **NÃO RESOLVIDO** | 13 entradas ausentes; PyInstaller/venv isolado indisponíveis | Build e smoke do EXE: **NÃO TESTADOS** |

## Contagem por classificação

- CORRIGIDO: 4
- MITIGADO POR BLOQUEIO: 2
- PARCIAL: 2
- NÃO RESOLVIDO: 1
- NÃO TESTADO: usado explicitamente nos subitens sem evidência executável; não promovido a aprovação
