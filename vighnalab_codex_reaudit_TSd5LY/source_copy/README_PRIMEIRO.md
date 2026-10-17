# VighnaStudy — Homologador Windows V1.1

**NÃO É UMA ATUALIZAÇÃO. NÃO INSTALAR O RC2 NA CÓPIA PRINCIPAL.**

## Execução simples (sem Codex)

1. Extraia o ZIP completo para uma pasta comum do Windows (por exemplo, `Documentos\VighnaStudy_Teste`).
2. Abra essa pasta e execute com duplo clique **`1_INICIAR_TESTES_WINDOWS.cmd`**.
3. Aguarde o término. Serão usados arquivos de código que estão *dentro do próprio pacote*, não os arquivos da sua instalação.
4. Procure na mesma pasta por **`RESULTADOS_HOMOLOGACAO_WINDOWS_AAAAMMDD_HHMMSS.zip`**.
5. Envie **somente esse ZIP de resultados** nesta conversa para análise. Não instale nada.

Para testar *também* a compilação do executável, utilize depois
**`2_COMPILAR_APENAS_EM_LABORATORIO.cmd`**. Esse segundo modo é opcional:
ele tenta compilar o código RC2 em uma pasta temporária, usando o
`VighnaStudy.spec` original da R1D. **Nunca abre o executável gerado.**

## Requisitos

- Windows 10 ou 11, Python 3.11+ (preferência por Python 3.13).
- Para os testes de interface: PySide6 no Python utilizado, com QtTest.
- Para o teste opcional de compilação: PyInstaller e qtawesome.
- Não precisa de Codex, não exige administrador e não instala pacotes da internet.

**Se faltar alguma dependência, a etapa será marcada BLOQUEADA**, não aprovada.

## Segurança e isolamento

- Cria diretório novo sob a pasta TEMP do Windows, com prefixo `Vighna_Homologacao_QA_`.
- Reconstitui a base QA R1D e aplica o RC2 apenas em arquivos sintéticos.
- Testa o atualizador com banco SQLite sintético e EXE **fictício**, nunca o executável real.
- Extrai apenas uma cópia de código RC2 conhecida, após verificar checksums e nomes dos arquivos.
- O Qt compila isoladamente por AST somente `JanelaConfiguracoes`; não importa `main.py` ou `banco.py`.
- O validador testa Claro, Escuro, Futurista em 700×590, 840×700 e 1100×800,
  nas escalas simuladas 100%, 125% e 150%; verifica Enter na pesquisa.
- Se solicitado, PyInstaller usa a configuração R1D em uma cópia temporária e não inicia o aplicativo.
- Limpa a pasta QA criada por esta execução ao final; o ZIP de resultados fica na pasta extraída.
- Não solicita nem reconhece caminhos da instalação do usuário.
- Não faz backup, leitura nem modificação do banco pessoal.
- Não altera a configuração global de PowerShell ou Python (a política Bypass se aplica apenas a este processo).
- Não executa instalador, update real ou rollback real sobre a instalação.

## Limitações honestas

Este pacote foi produzido e testado sintaticamente em ambiente Linux.
**Os launchers PowerShell, Qt nativo e PyInstaller Windows ainda NÃO foram
executados e aprovados em um Windows neste ciclo.** Os primeiros resultados
Windows devem voltar para auditoria; eventuais problemas do harness serão
corrigidos antes de qualquer homologação.

O teste de escala por `QT_SCALE_FACTOR` não equivale a alterar DPI real no Windows.
Não se executa o EXE real, porque essa etapa exige isolamento adicional
do perfil de dados. A homologação integral requer revisão das evidências e
smoke de instalação/atualização em Windows isolado, antes de autorizar instalação.

Mesmo quando todos os testes passam, o resultado continua **NÃO HOMOLOGADO
AUTOMATICAMENTE** até auditoria cruzada explícita.

## Situação da arquitetura

M2: RC2 candidato, base R1D, versão 0.29.59, schema 25, não instalado.
M3: experimental até R35, preservado no arquivo histórico, não integrado.

A pasta `HISTORICO_DE_DESENVOLVIMENTO` contém o checkpoint anterior (não executar).

## Correção da V1.1 — quando a V1 termina sem gerar ZIP

A V1 encerrava sem evidência se o preflight falhasse antes da criação do
diretório de laboratório. A V1.1 grava um ZIP de diagnóstico também nesse caso.
O PowerShell possui um segundo mecanismo de emergência: se o Python terminar
sem gerar resultados, compacta o registro da execução em um ZIP.

A tela imprime progresso por etapa e o caminho exato do ZIP, inclusive quando
a pasta de extração não pode receber arquivos (nesse caso, utiliza Documentos
ou a pasta temporária como destino alternativo).

**IMPORTANTE:** não reaproveite os scripts antigos da V1. Extraia o ZIP V1.1
inteiro em uma pasta NOVA e execute normalmente (não como administrador).
Envie o ZIP novo, mesmo que o status seja de erro/bloqueio.
