# Relatório — Otimização do build PyInstaller

Data: 2026-09-18  
Versão resultante: 0.24.3  
Build: `build-pyinstaller-incremental`  
Schema: 18 (sem alteração)

## 1. Problema observado

O fluxo de geração do executável estava forçando um build praticamente do zero em toda atualização. O arquivo `atualizar_exe.bat`:

- executava `pip install --upgrade pyinstaller` em toda atualização;
- apagava o diretório de trabalho do PyInstaller;
- utilizava `--clean` em toda execução;
- não utilizava o `VighnaStudy.spec` como contrato estável do build.

Isso eliminava a maior parte do benefício de cache entre builds e fazia a análise de dependências do PySide6/Qt ser repetida de forma mais cara.

## 2. Estratégia adotada

O fluxo passou a distinguir dois modos.

### Build incremental — padrão

Executado por:

`atualizar_exe.bat`

Características:

- preserva `build_pyinstaller` entre atualizações;
- não usa `--clean` por padrão;
- reaproveita os arquivos `.toc` e demais artefatos que o PyInstaller considerar válidos;
- continua gerando a distribuição nova em uma pasta temporária antes de substituir a versão instalada;
- preserva banco e backups da mesma forma que o fluxo anterior.

### Build limpo — recuperação/diagnóstico

Executado por:

`atualizar_exe_limpo.bat`

Características:

- define `VIGHNA_CLEAN_BUILD=1`;
- apaga `build_pyinstaller`;
- executa PyInstaller com `--clean`;
- deve ser usado quando houver suspeita de cache inconsistente, mudança relevante de dependências ou diagnóstico.

## 3. PyInstaller

A versão continua fixada em `6.22.3`.

O atualizador agora consulta a versão instalada. Ele somente chama `pip install PyInstaller==6.22.3` quando:

- PyInstaller não está instalado; ou
- a versão instalada é diferente da versão esperada.

Foi removido o `pip install --upgrade pyinstaller` incondicional de cada build.

## 4. Contrato de build em `VighnaStudy.spec`

O atualizador passou a gerar o executável a partir de `VighnaStudy.spec`.

Módulos essenciais preservados:

- `PySide6.QtCore`;
- `PySide6.QtGui`;
- `PySide6.QtWidgets`.

Componentes Qt não utilizados pelo código atual foram explicitamente excluídos, incluindo:

- QtNetwork;
- QtQml/QtQuick;
- QtWebEngine/WebChannel;
- QtMultimedia;
- QtBluetooth/Nfc;
- QtPositioning/Location;
- QtSql;
- QtTest;
- QtOpenGL;
- QtPrintSupport;
- QtSvg;
- QtPdf.

Também foram excluídos pacotes pesados não utilizados pelo projeto (`tkinter`, `matplotlib`, `numpy`, `pandas`) para impedir coleta acidental futura por dependências opcionais.

Um teste automático verifica que nenhum componente Qt excluído passou a ser importado pelo código de produção. Se o Vighna começar a utilizar um deles futuramente, o contrato de build deverá ser atualizado antes de gerar o EXE.

## 5. UPX

O `.spec` passou a usar `upx=False`.

O Vighna é distribuído em modo `--onedir`; para este projeto, a prioridade desta etapa é reduzir trabalho de empacotamento e manter o build previsível. Essa escolha pode aumentar modestamente o tamanho da distribuição caso UPX esteja instalado no computador, mas evita trabalho de compressão adicional.

## 6. Comportamento esperado

O primeiro build após esta atualização ainda pode ser demorado, pois o cache incremental ainda não existe e QtCore/QtGui/QtWidgets são dependências reais e grandes.

Os maiores ganhos devem aparecer a partir dos builds seguintes, especialmente quando não houver mudança nas dependências ou no ambiente Python.

Alterações frequentes em `main.py` ainda podem obrigar o PyInstaller a refazer parte da análise. A otimização reduz trabalho desnecessário, mas não elimina o custo legítimo de analisar PySide6.

## 7. Arquivos alterados

- `VighnaStudy.spec`
- `atualizar_exe.bat`
- `criar_exe.bat`
- `versao.py`

## 8. Arquivos adicionados

- `atualizar_exe_limpo.bat`
- `test_build_pyinstaller.py`
- `RELATORIO_OTIMIZACAO_BUILD_PYINSTALLER_2026-09-18.md`

## 9. Validações executadas neste ambiente

- suíte unittest: 137 testes aprovados;
- `testes_smoke.py`: aprovado;
- sintaxe Python do `VighnaStudy.spec`: aprovada;
- `py_compile` nos arquivos Python alterados: aprovado;
- SQLite `PRAGMA integrity_check`: `ok`;
- SQLite `PRAGMA foreign_key_check`: 0 violações.

Não foi possível executar o PyInstaller Windows neste ambiente. A validação final do executável deve ser feita no Windows com o `.venv` real do projeto.

## 10. Teste recomendado no Windows

Executar duas atualizações consecutivas com `atualizar_exe.bat` e comparar os tempos.

Na primeira execução, é esperado que a fase Qt continue perceptível.

Na segunda, o terminal deve informar:

`Build INCREMENTAL: reutilizando cache`

Não deve ocorrer instalação do PyInstaller se a versão 6.22.3 já estiver instalada.

Após o build, validar pelo menos:

- abertura do VighnaStudy.exe;
- Dashboard;
- Central de Questões;
- Estatísticas;
- importação de PDF;
- ícone/atalho;
- banco e backups preservados.

Se ocorrer problema atribuível ao cache, executar uma vez:

`atualizar_exe_limpo.bat`

## 11. Resultado

A geração do EXE agora possui um modo incremental seguro como caminho padrão e um modo limpo explícito para recuperação.

A otimização não altera banco, schema, métricas acadêmicas, fila inteligente ou comportamento funcional do VighnaStudy.
