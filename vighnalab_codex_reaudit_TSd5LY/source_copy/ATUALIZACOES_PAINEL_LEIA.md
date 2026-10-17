# VighnaStudy — Painel V3.1.11

**Atualização incremental exclusivamente da V3.1.10 para a V3.1.11**. Acesse Atualizações e selecione o ZIP entregue, sem extrair. O painel deve reabrir após aplicação bem-sucedida. Se falhar, preserve a versão anterior e envie o diagnóstico.

## Novos recursos

1. Em Gates, botão **Registrar ZIP G5-C**: registra somente metadados e hashes da evidência G5-C selecionada manualmente. Exige quatro imagens PNG e registros de navegação, reinicialização e SQLite coerentes. **Não autentica a origem nem analisa semanticamente o conteúdo das imagens**. O gate G7 e a aprovação humana continuam obrigatórios.
2. Em Executar testes, botão **G6-A — Atualizador original**: testa o `vighna_update_engine.py` da base R1D sobre instalações 100% sintéticas, usando o pacote RC2 protegido. Verifica sucesso, falha na compilação simulada e falha após commit com rollback. Usa somente executáveis FICTÍCIOS, sem instalar ou iniciar programa.
3. O G6-A gera um ZIP compacto contendo o relatório e hashes; nenhum banco ou executável é enviado.

## Limites da homologação

**G6-A não equivale a G6 aprovado.** Não testa compilação real, instalador com executável Windows, atualização real no Sandbox nem restauração operacional de dados em um release. Essas verificações compõem o futuro G6-B. Mesmo G5 documentado e G6-A aprovado não autorizam instalar o M2 RC2. A instalação principal do VighnaStudy não deve ser alterada.

## Correção V3.1.11 — G6-A

O diagnóstico Windows `DIAGNOSTICO_PAINEL_HOMOLOGACAO_20261013_025844_668941.zip` indicou WinError 32 no `estudos.db` **sintético** durante o G6-A. A V3.1.11 fecha explicitamente as duas conexões SQLite do laboratório antes da limpeza, e preserva a exceção original caso também ocorra falha ao remover os arquivos temporários. Foi incluído teste de regressão que mantém todas as conexões vivas e exige `close()` para cada uma. Executar o G6-A novamente no Windows; resultados locais não bastam para liberar G6-B.

## V3.1.13 — G6-B1, motor original com executáveis reais no Sandbox

Atualizar somente o Painel V3.1.12 para V3.1.13. Em **Executar testes** há
um novo botão G6-B1. Ele compila duas versões reais em cópias QA e um executor
isolado. No Windows Sandbox sem rede, troca os executáveis reais com o motor
original e verifica os cenários de sucesso, falha de compilação induzida e
falha pós-commit. O SQLite é exclusivamente sintético. O callback de compilação
usa binário RC2 pré-compilado; compilação original end-to-end (G6-B2), auditoria
G7 e autorização de instalação permanecem pendentes.


## V3.1.14 — Correção dirigida do G6-B1 (WindowsPath + string)

Após `G6_B1_DIAGNOSTICO_20261013_034706_871556.zip`, constatou-se que os três EXEs
foram compilados, mas o agente Sandbox não iniciou os cenários: `TypeError:
unsupported operand type(s) for +: 'WindowsPath' and 'str'`. A V3.1.14
corrige somente a montagem do caminho temporário do agente, adiciona testes
de regressão para caminhos Windows, e evita declarar o motor original exercitado
quando nenhum cenário foi completado. O banco pessoal e o VighnaStudy principal
permanecem intocados. G6-B1 deve ser repetido em Windows Sandbox; G6-B2 e G7
não estão aprovados. Use pacote incremental exclusivamente da V3.1.13.


## V3.1.15 — G6-B1 PyInstaller: dependencias do motor carregado dinamicamente

O diagnostico Windows `G6_B1_DIAGNOSTICO_20261013_035956_332306.zip`
mostrou compilacoes R1D, RC2 e agente concluidas, mas o modulo
`vighna_update_engine.py` falhou ao importar `uuid` no Sandbox.
Esta atualizacao corrige a analise de dependencias da compilacao do agente:
coleta importacoes estaticas do motor QA previamente verificado, exige
dependencias somente da biblioteca padrao, passa `--hidden-import` para
PyInstaller e **executa o GUEST compilado em um preflight de importacao**
antes de iniciar o Sandbox. Resultado do preflight fica em `PROBE_GUEST.log.txt`.
O preflight nao comprova transacao; os tres cenarios seguem obrigatorios.
Atualizar apenas o Painel V3.1.14. Nao altera o VighnaStudy nem bancos pessoais.

## V3.1.16 — G6-B1: baseline após R1D e diagnóstico SQLite autônomo

Atualização incremental exclusivamente da V3.1.15 para a V3.1.16. O hash do
SQLite sintético era capturado antes da primeira abertura do R1D, mas esse
executável inicializa o schema, executa migrações/backfills e ativa WAL. A
V3.1.16 registra snapshots físicos e lógicos após criar o banco, após abrir o
R1D, após a atualização/reversão e após abrir o executável final. A preservação
durante a transação continua exigindo igualdade física e lógica exata.

O relatório do GUEST passa a incluir hashes do banco e dos auxiliares `-wal`,
`-shm` e `-journal`, schema, contagem e hash de registros por tabela, PRAGMAs,
integridade, chaves estrangeiras e a primeira divergência. Evidências parciais
são gravadas mesmo quando um cenário lança exceção. Metadados internos como
`sqlite_sequence` são registrados como mudança física de startup, mas não são
confundidos com alteração dos registros da aplicação; continuam estritos dentro
da transação. O host também encerra somente a instância descartável do Windows
Sandbox que ele próprio iniciou, depois de coletar o relatório.

Em 13/10/2026, o laboratório `G6B1_20261013_122328_291614` executou no Windows
Sandbox os cenários de atualização normal, falha de compilação e falha após
commit. Resultado: `PASSOU_B1_EXECUTAVEIS_REAIS`. Isso conclui o ensaio G6-B1,
mas **não aprova o Gate G6**: G6-B2 e G7 continuam pendentes e o M2 RC2 permanece
proibido para instalação no VighnaStudy principal.

## V3.1.17 — Ponte conservadora para G6-B2

Permite os arquivos exclusivos G6-B2 no atualizador do painel. Ainda não instala
nem executa G6-B2. Preserva G6-B1, versão principal e banco pessoal.
Aplicar sobre V3.1.16, validando o resultado, ANTES da V3.1.18.

## V3.1.18 — G6-B2: PyInstaller original em Sandbox (experimental)

Instalar somente depois da V3.1.17. Novo botão G6-B2 em Executar testes.
O host compila R1D e GUEST em QA; o Windows Sandbox recebe Python base
e site-packages do Ambiente_Qt_Homologador via pastas SOMENTE LEITURA.
O motor original invoca o PyInstaller sem runner substituto; valida sucesso,
falha real de especificacao de build e falha pos-commit com rollback.
As transacoes utilizam banco 100% sintetico, sem tocar o VighnaStudy principal.

**IMPORTANTE**: testes Python locais nao comprovam o funcionamento do runtime
Windows mapeado nem do PyInstaller real dentro do Sandbox. Ate obter ZIP de
evidencias real contendo tres cenarios aprovados, G6-B2 e experimental/bloqueado.
G6/G7 e instalacao principal nao autorizados. Preserve os ZIPs anteriores.

## V3.1.19 — G6-B2: recurso de ícone verificado no Windows Sandbox

O G6-B2 V3.1.18 foi bloqueado antes de concluir o build original: a base QA
R1D contém apenas fontes, mas `VighnaStudy.spec` faz referência obrigatória ao
arquivo binário `vighnastudy.ico`. O host já usava o ícone da referência RC2
verificada na compilação do R1D, mas não o encaminhava ao Sandbox.

Nesta versão, o host envia o MESMO ícone QA de referência, assinado pelo
manifesto SHA-256 de entrada; o executor valida seus bytes e o copia para a
raiz sintética antes da atualização. O motor original e a especificação de
compilação não foram alterados. Não consulta nem altera instalação pessoal.
Retestar G6-B2 no Windows Sandbox; G6-B2, Gate G6 e G7 seguem pendentes até
novo diagnóstico autenticado. Não instalar M2 RC2 no aplicativo principal.

## V3.1.20 — Encerramento não destrutivo do Windows Sandbox e consolidação G6

Sobre a base V3.1.19, o painel passa a **solicitar** WM_CLOSE somente a uma janela do
PID que ele iniciou, sem terminate() ou kill() como fallback. Se o processo
do Sandbox hospedar a interface em outro PID ou não responder, a sessão permanece
aberta para fechamento manual; essa situação fica registrada em
`encerramento_sandbox` sem apagar os diagnósticos nem mudar o mérito dos testes.
A API Windows real desta mudança ainda precisa ser observada no próximo uso.

O G6-A, G6-B1 e G6-B2 possuem evidências anteriores satisfatórias. Isso permite
um parecer técnico de consolidação, mas o Gate G6 histórico é informativo e
não se altera automaticamente. G7, aceite humano e instalação principal seguem
**pendentes / não autorizados**.

## V3.1.21 — Ponte de allowlist para G7

Versão intermediária que autoriza apenas os nomes dos dois módulos G7 no atualizador do painel. Não inicia auditorias nem altera os Gates. Exige V3.1.20.

## V3.1.22 — G7: auditoria documental PRELIMINAR

Acesse **Gates de liberação → Gerar dossiê G7** e selecione uma pasta que contenha exatamente as três cópias dos ZIPs G6 já evidenciados (G6-A, G6-B1 e G6-B2, sem extrair). O G7 compara os ZIPs com os hashes de referência documentados no G6, verifica os manifestos internos, os três cenários, contratos de rollback, preservação SQLite e as evidências do histórico G1–G5, sem executar scripts ou ler banco pessoal.

O ZIP `G7_DOSSIE_PRELIMINAR_*.zip` será salvo em `G7_Dossies` dentro da pasta do PAINEL. Ele contém somente metadados e pendências. Os ZIPs de origem não são copiados, editados nem incluídos no dossiê.

**Não é um aprovador automático.** G7 e autorização de instalação permanecem `false`. Falhas históricas da suíte, aceite humano dos gates e outros itens ainda precisam de relatório/revisão separados. Instale somente após a ponte V3.1.21.


## V3.1.23 — Ponte de autorização G7
Permite ao atualizador atualizar `painel_core.py`, `test_painel_core.py`,
`test_painel_v3.py` e `test_historico_v2b.py`. Nenhum desses módulos é
alterado por esta ponte. Não aprova Gate G7 nem autoriza instalação RC2.


## V3.1.24 — Saneamento G7 dirigido
- Busca determinística de ZIP por mtime_ns, ctime_ns e caminho; empate não prova
  ordem cronológica real.
- Testes de leitura UTF-8 e fechamento explícito de conexões SQLite.
- Versão esperada no G5-C consultada em PAINEL_VERSAO.json.
- Verificação de symlink/junction mesmo quando Path.exists() é falso.
- Testes com symlink real continuam SKIP se o Windows não permitir sua criação;
  testes sintéticos adicionais não substituem ensaio real.
- Sem alterações do VighnaStudy principal, motor original, banco pessoal ou
  autorização de liberação. G7 permanece pendente.


## V3.1.25 — Fechamento controlado do cliente Windows Sandbox (G7)

- Após evidência verificada por manifesto SHA-256 do guest e ausência de sessões anteriores, identifica uma única nova janela visível de `WindowsSandboxClient.exe` associada à sessão QA iniciada.
- Revalida processos e HWND/PID antes de enviar um único `WM_CLOSE`; não usa `terminate()`, `kill()`, árvore de processos ou fechamento global.
- Na ausência de evidência, em caso de janela/processo ambíguo ou mudança concorrente, exige fechamento manual.
- Atualização exclusiva do **VighnaLab**, reversível e sem tocar no VighnaStudy principal ou seu SQLite pessoal.
- G5/G6/G7 e M2 RC2 permanecem sem aprovação automática. A ausência do aviso visual `0x80072746` requer confirmação manual.


## V3.1.26 — Confirmação automática de encerramento do Sandbox QA

Somente após confirmação da evidência G6, inventário inicial vazio, um único
WindowsSandboxClient.exe novo e uma única janela pertencente a ele, o painel
pode enviar WM_CLOSE. Se a caixa NATIVA de descarte (português brasileiro ou
inglês) for identificada de forma exata e associada à janela da própria sessão,
o botão OK identificado por IDOK será confirmado pelo Windows.

Não há click por coordenadas, OCR, encerramento forçado, busca de avisos de
outros programas ou interação com Sandboxes preexistentes. Qualquer dúvida,
novo PID, múltiplos diálogos, texto desconhecido ou botão não reconhecido
mantém a confirmação MANUAL. G5, G6, G7 e instalação M2 RC2 não são aprovados.
A API nativa do Windows ainda precisa de homologação operacional.

## V3.1.27 — Diálogo de confirmação independente (G7)

- A confirmação de descarte do Windows Sandbox pode ser uma segunda janela `#32770` sem `GW_OWNER`, no mesmo cliente QA. Exigir janela principal conhecida + um único diálogo separado, texto completo, IDs dos controles e verificação do PID.
- Continuar recusando avisos desconhecidos, múltiplos diálogos, janelas externas e falta de evidência; sem clique por coordenadas.
- Alteração restrita ao VighnaLab; G7 e instalação M2 RC2 permanecem pendentes.


## V3.1.28 — Proteção contra junctions no rollback

Bloqueio de links simbólicos, junctions NTFS e pontos de reanálise nas pastas de backup, checkpoints, metadados e arquivos de recuperação. A verificação recusa o redirecionamento antes de qualquer atualização. Não autoriza M2 RC2.

## V3.1.29 — G7: proteção de gravações de status e marcadores

- Corrigida a gravação de `ultima_execucao.tmp`/`ultima_execucao.json` e `ultima_atualizacao.json` para não seguir symlinks NTFS externos, inclusive em rotinas de erro.
- Arquivos de estado e registros de checkpoints passam a usar arquivos temporários exclusivos e substituição atômica com bloqueio de reparse points.
- Nenhuma alteração do motor de atualização do VighnaStudy, dos dados pessoais ou dos Gates; M2 RC2 não autorizado.
