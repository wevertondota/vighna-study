# VighnaStudy 0.29.59 — Central de Atualizações e Segurança

**Data:** 2026-10-08
**Base:** `VighnaStudy_0.29.59_DesignSystem_Central_Questoes_Piloto_Inventario_COMPLETO.zip`
**Build da cópia alterada:** `updates-center-v1` (schema permanece em 25).
**Natureza:** implementação em código; validação em Windows pendente.
**Banco real:** não alterado.

## 1. Entrega

Foi implementada a primeira versão operacional da **Central de Atualizações e Segurança**, acessível na janela atual de Configurações. Possui seleção local de pacote ZIP, pré-validação, descrição do conteúdo, confirmação explícita, histórico de instalações e integração com um processo auxiliar independente.

**O processo auxiliar utiliza `.venv\\Scripts\\pythonw.exe` no Windows**, mantendo sua própria janela PySide6 após o fechamento do aplicativo principal. Não é, nesta etapa, um `VighnaUpdater.exe` independente da `.venv`. O próprio processo auxiliar compila versões posteriores por meio do PyInstaller, sem chamar o `atualizar_exe.bat`. A versão inicial desta funcionalidade ainda precisa ser compilada uma vez com o procedimento existente.

A janela auxiliar tenta reutilizar o tema Claro, Escuro ou Futurista salvo pelo Vighna (leitura SQLite somente leitura), e usa a aparência nativa como fallback. Utiliza botões normais de janela e um botão **Minimizar**. Clicar no X enquanto o trabalho está em andamento apenas minimiza a janela: não cancela o build nem a instalação. A interface permanece responsiva pois a instalação é executada em `QThread`. A barra apresenta atividade indeterminada na compilação, sem inventar porcentagens; as demais fases são apresentadas nominalmente. Ao concluir, o auxiliar reabre o Vighna atualizado e oferece histórico e botão de abertura.

## 2. Regras de proteção

1. Nenhuma atualização é iniciada sem seleção manual e confirmação explícita do usuário.
2. O atualizador exige o encerramento completo do processo principal antes de alterar arquivos.
3. Antes de compilar, gera backup transacional do `estudos.db` via SQLite; verifica `integrity_check` e `foreign_key_check` do banco e do backup.
4. O backup fica fora das pastas substituídas, em `backups/atualizacoes/<identificador>/estudos.db`.
5. Pacotes **não podem** conter `estudos.db`, arquivos executáveis ou caminhos fora dos módulos/fontes autorizados.
6. Mudanças no schema são bloqueadas nesta versão; alterações em conteúdo de questões devem ter fluxo de migração próprio em projeto futuro.
7. O pacote utiliza manifesto com hashes SHA-256 por arquivo, versão/build de origem, versão/build de destino e schema.
8. Novos fontes e executável são compilados em pasta isolada. O executável anterior é retido para rollback.
9. Em falha detectada, ocorre tentativa de restauração dos arquivos anteriores. Um registro transacional também permite recuperar uma troca interrompida.
10. O caminho do executável utilizado pelo atalho permanece `dist\\SistemaEstudos\\VighnaStudy.exe`.

**Limite de segurança:** SHA-256 detecta corrupção e adulteração em relação ao manifesto, mas **não autentica a origem** do ZIP. A instalação executa código Python fornecido pelo pacote; o usuário deve importar apenas pacotes de origem confiável. Uma instalação maliciosa poderia danificar dados no primeiro uso, apesar das proteções do atualizador. Proteção contra falhas elétricas/antivírus/condições extremas exige validação real no Windows.

## 3. Pacotes aceitos

O novo importador **não aceita ZIPs completos legados**. Um ZIP completo pode conter um banco antigo ou arquivos desnecessários; por isso, será recusado. Pacotes futuros serão gerados pelo módulo `gerar_pacote_atualizacao.py`, que cria `manifest.json` e inclui somente fontes autorizadas. É obrigatória a atualização de `versao.py` em cada pacote com novo build/versão. Em futuras atualizações o `schema` deve continuar igual a 25 até termos suporte explícito a migrações.

## 4. Arquivos modificados e adicionados

**Modificados:** `main.py` (Configurações; seção, busca e histórico), `versao.py` (build `updates-center-v1`).

**Adicionados:** `vighna_update_engine.py` (validação, backup, compilação, transação/rollback), `vighna_update_ui.py` (autorização), `vighna_updater.py` (janela auxiliar minimizável), `gerar_pacote_atualizacao.py` (empacotamento futuro), `vighna_recuperar_atualizacao.py`, `RECUPERAR_ATUALIZACAO_INTERROMPIDA.bat` (recuperação excepcional), `test_vighna_atualizador.py` (testes).

**Preservados:** `estudos.db`, `foco.py`, `tema.py`, `ui/design/*`, conteúdos e contratos cromáticos da Central de Questões do checkpoint de origem.

## 5. Testes executados neste ambiente

- 13/13 testes isolados de instalação/rollback aprovados: backup consistente, pacote válido, banco preservado, rejeição de DB no ZIP, path traversal e nomes de módulo inválidos, schema incompatível, build de origem incompatível, hashes e versões divergentes, falha de compilação, Python inválido, falha após troca e recuperação de instalação interrompida.
- Compilação sintática aprovada para arquivos modificados e novos.
- 69 fontes de produção utilizadas no staging passaram na compilação sintática.
- Testes do piloto da Central anteriores: 11/12 aprovados. O teste restante exige que `main.py` continue com o hash do checkpoint anterior e falha **esperadamente**, porque a Central de Atualizações altera `main.py`.
- Testes estáticos de build PyInstaller: 4/4 aprovados.
- Banco `estudos.db` comparado bit a bit com o ZIP de origem: SHA-256 inalterado.

**Não executados neste ambiente:** compilação de executável Windows, inicialização real com PySide6, minimização visual no Windows, instalação de pacote real por meio da interface, antivírus/permissões Windows e reabertura pós-instalação. O PySide6 não está instalado neste ambiente Linux. Estes testes são **obrigatórios antes de substituir definitivamente a instalação de estudos**.

## 6. Instalação inicial (uma única vez)

1. **Feche** o VighnaStudy e faça uma cópia de segurança externa do `estudos.db` atual e da pasta `backups` (recomenda-se também utilizar o backup do próprio aplicativo).
2. Extraia **somente** o pacote inicial `VighnaStudy_Central_Atualizacoes_BOOTSTRAP_SEM_DADOS.zip` sobre `C:\\SistemaEstudos`, substituindo os arquivos de código correspondentes. Ele **não contém `estudos.db`** nem backups.
3. Na pasta de instalação, execute o atual `atualizar_exe.bat` **uma última vez** para incorporar a Central ao `VighnaStudy.exe`. A presença da `.venv` e do PyInstaller continua necessária.
4. Abra o Vighna pelo **mesmo atalho** e confira Configurações > Atualizações e segurança.
5. Antes de confiar na atualização automática, realize uma instalação de teste controlada no Windows, de preferência numa **cópia separada** do projeto com banco de teste, e confirme minimização, reabertura, histórico, proteção de dados e rollback.

Após o bootstrap, os pacotes novos no formato `vighna-source-update-v1` são instalados pelo Vighna, sem abrir o BAT de compilação. A `.venv` continua necessária. Não substitua o banco nem extraia pacotes completos sobre a instalação de estudos durante os testes.

## 7. Procedimento excepcional de recuperação

Se uma falha elétrica interromper o swap de arquivos, feche o Vighna e use `RECUPERAR_ATUALIZACAO_INTERROMPIDA.bat`, **somente para recuperação**. O script procura registros `state.json` marcados como transação em andamento e tenta restaurar código e executável anteriores; não altera nem substitui o banco SQLite. Conserve o backup gerado e os registros para análise caso a recuperação não funcione.

## 8. Próximas validações

- Verificar que o processo principal fecha completamente após a autorização, mesmo com sessão de questões ou Modo Foco abertos.
- Testar a janela auxiliar minimizada durante compilação e retorno à Área de Trabalho.
- Validar um pacote real assinado/autenticado por mecanismo de confiança futuro, se necessário.
- Validar rollback Windows sob falha de compilação, permissão negada, arquivo bloqueado e recuperação após interrupção.
- Conferir banco, respostas, estatísticas, atalho e aparência nos três temas após a instalação.
- Só então formalizar a Central de Atualizações como infraestrutura validada e retomar a migração cromática da Central de Questões.
