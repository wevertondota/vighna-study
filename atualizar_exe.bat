@echo off
setlocal EnableExtensions
cd /d "%~dp0"

set "PYINSTALLER_ESPERADO=6.22.3"
set "QTA_ESPERADO=1.4.2"
set "APP_ATUAL=%CD%\dist\SistemaEstudos"
set "TEMP_DADOS=%CD%\_dados_antes_atualizacao"
set "DIST_NOVA=%CD%\dist_nova"
set "BUILD_CACHE=%CD%\build_pyinstaller"
set "SAIDA_NOVA=%DIST_NOVA%\VighnaStudy"
set "EXE_FINAL=%CD%\dist\SistemaEstudos\VighnaStudy.exe"

echo.
echo ============================================
echo       ATUALIZANDO O VIGHNASTUDY
echo ============================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo ERRO: ambiente virtual .venv nao encontrado.
    pause
    exit /b 1
)

if not exist "main.py" (
    echo ERRO: main.py nao encontrado.
    pause
    exit /b 1
)

if not exist "VighnaStudy.spec" (
    echo ERRO: VighnaStudy.spec nao encontrado.
    pause
    exit /b 1
)

if not exist "vighnastudy.ico" (
    echo ERRO: vighnastudy.ico nao encontrado em:
    echo %CD%
    pause
    exit /b 1
)

echo Fechando processos antigos, se ainda estiverem abertos...
taskkill /IM SistemaEstudos.exe /F >nul 2>nul
taskkill /IM VighnaStudy.exe /F >nul 2>nul

if exist "%TEMP_DADOS%" rmdir /S /Q "%TEMP_DADOS%"
mkdir "%TEMP_DADOS%"

echo.
echo Preservando o banco unico da pasta principal...

if not exist "%CD%\estudos.db" (
    echo ERRO: estudos.db nao foi encontrado na raiz do projeto.
    echo A atualizacao foi cancelada para proteger seus dados.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" copiar_banco_consistente.py "%CD%\estudos.db" "%TEMP_DADOS%\estudos.db"
if errorlevel 1 (
    echo ERRO: o banco principal nao passou pela copia consistente do SQLite.
    echo Execute recuperar_banco.bat antes de atualizar.
    pause
    exit /b 1
)
echo Banco principal preservado por snapshot SQLite consistente.

REM Versoes antigas do Vighna mantinham outro estudos.db dentro de dist.
REM Ele nunca volta a sobrescrever o banco principal. Antes de remover a
REM versao antiga, guardamos essa copia apenas como contingencia historica.
if exist "%APP_ATUAL%\estudos.db" (
    if not exist "%CD%\backups" mkdir "%CD%\backups"
    ".venv\Scripts\python.exe" copiar_banco_consistente.py "%APP_ATUAL%\estudos.db" "%CD%\backups\estudos_legado_dist_antes_unificacao.db" >nul
    echo Banco legado de dist arquivado em backups; ele nao sera usado como banco ativo.
)

if exist "%CD%\backups" (
    xcopy "%CD%\backups" "%TEMP_DADOS%\backups\" /E /I /Y >nul
)

call ".venv\Scripts\activate.bat"

echo.
echo Verificando PyInstaller...
set "PYI_VERSION="
for /f "usebackq delims=" %%V in (`python -c "import PyInstaller; print(PyInstaller.__version__)" 2^>nul`) do set "PYI_VERSION=%%V"

if not "%PYI_VERSION%"=="%PYINSTALLER_ESPERADO%" (
    if defined PYI_VERSION (
        echo PyInstaller %PYI_VERSION% encontrado; ajustando para %PYINSTALLER_ESPERADO%...
    ) else (
        echo PyInstaller nao encontrado; instalando %PYINSTALLER_ESPERADO%...
    )
    python -m pip install "PyInstaller==%PYINSTALLER_ESPERADO%"
    if errorlevel 1 (
        echo ERRO ao preparar PyInstaller.
        pause
        exit /b 1
    )
) else (
    echo PyInstaller %PYI_VERSION% ja esta pronto. Nenhuma instalacao necessaria.
)


echo.
echo Verificando QtAwesome...
set "QTA_VERSION="
for /f "usebackq delims=" %%V in (`python -c "import qtawesome; print(qtawesome.__version__)" 2^>nul`) do set "QTA_VERSION=%%V"

if not "%QTA_VERSION%"=="%QTA_ESPERADO%" (
    if defined QTA_VERSION (
        echo QtAwesome %QTA_VERSION% encontrado; ajustando para %QTA_ESPERADO%...
    ) else (
        echo QtAwesome nao encontrado; instalando %QTA_ESPERADO%...
    )
    python -m pip install "QtAwesome==%QTA_ESPERADO%"
    if errorlevel 1 (
        echo ERRO ao preparar QtAwesome.
        pause
        exit /b 1
    )
) else (
    echo QtAwesome %QTA_VERSION% ja esta pronto.
)

if exist "%DIST_NOVA%" rmdir /S /Q "%DIST_NOVA%"

if /I "%VIGHNA_CLEAN_BUILD%"=="1" (
    echo.
    echo Build LIMPO solicitado: descartando cache do PyInstaller...
    if exist "%BUILD_CACHE%" rmdir /S /Q "%BUILD_CACHE%"
) else (
    echo.
    echo Build INCREMENTAL: reutilizando cache em:
    echo %BUILD_CACHE%
    echo Para um build totalmente limpo, use atualizar_exe_limpo.bat.
)

echo.
echo Gerando VighnaStudy.exe...

if /I "%VIGHNA_CLEAN_BUILD%"=="1" (
    python -m PyInstaller ^
        --noconfirm ^
        --clean ^
        --distpath "%DIST_NOVA%" ^
        --workpath "%BUILD_CACHE%" ^
        VighnaStudy.spec
) else (
    python -m PyInstaller ^
        --noconfirm ^
        --distpath "%DIST_NOVA%" ^
        --workpath "%BUILD_CACHE%" ^
        VighnaStudy.spec
)

if errorlevel 1 (
    echo.
    echo ERRO durante a geracao da nova versao.
    echo A versao anterior continua preservada.
    echo Se suspeitar de cache inconsistente, execute atualizar_exe_limpo.bat.
    pause
    exit /b 1
)

if not exist "%SAIDA_NOVA%\VighnaStudy.exe" (
    echo.
    echo ERRO: VighnaStudy.exe nao foi gerado.
    echo A versao anterior continua preservada.
    pause
    exit /b 1
)

echo.
echo Validando novamente o banco principal...

".venv\Scripts\python.exe" copiar_banco_consistente.py "%TEMP_DADOS%\estudos.db" "%TEMP_DADOS%\estudos_validado.db"
if errorlevel 1 (
    echo ERRO: a copia protegida do banco falhou na validacao final.
    echo A versao anterior continua preservada.
    pause
    exit /b 1
)

REM O executavel nao recebe mais uma segunda copia operacional do banco.
REM Tanto python main.py quanto VighnaStudy.exe usam %CD%\estudos.db.
copy /Y "%CD%\vighnastudy.ico" "%SAIDA_NOVA%\vighnastudy.ico" >nul

echo.
echo Substituindo a versao anterior...

if exist "%APP_ATUAL%" (
    rmdir /S /Q "%APP_ATUAL%"
)

if not exist "%CD%\dist" mkdir "%CD%\dist"

move "%SAIDA_NOVA%" "%CD%\dist\SistemaEstudos" >nul

if errorlevel 1 (
    echo.
    echo ERRO ao mover a nova versao para a pasta final.
    echo Verifique %DIST_NOVA%.
    pause
    exit /b 1
)

if exist "%DIST_NOVA%" rmdir /S /Q "%DIST_NOVA%"
if exist "%TEMP_DADOS%" rmdir /S /Q "%TEMP_DADOS%"

REM IMPORTANTE: BUILD_CACHE NAO E APAGADO.
REM Ele acelera builds seguintes do PyInstaller.

echo.
echo Criando atalho VighnaStudy...

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ws = New-Object -ComObject WScript.Shell; " ^
  "$desktop = $ws.SpecialFolders.Item('Desktop'); " ^
  "$old = Join-Path $desktop 'VighnaStudy.lnk'; " ^
  "if (Test-Path $old) { Remove-Item $old -Force }; " ^
  "$shortcut = $ws.CreateShortcut($old); " ^
  "$shortcut.TargetPath = '%EXE_FINAL%'; " ^
  "$shortcut.WorkingDirectory = '%CD%\dist\SistemaEstudos'; " ^
  "$shortcut.IconLocation = '%CD%\dist\SistemaEstudos\vighnastudy.ico,0'; " ^
  "$shortcut.Description = 'VighnaStudy'; " ^
  "$shortcut.Save()"

if errorlevel 1 (
    echo.
    echo AVISO: o VighnaStudy foi atualizado, mas o atalho nao foi criado.
    echo Execute criar_atalho_vighnastudy.bat depois.
) else (
    echo Atalho VighnaStudy criado/atualizado.
)

echo.
echo Atualizando o Explorer para renovar os icones...
ie4uinit.exe -show >nul 2>nul

echo.
echo ============================================
echo          ATUALIZACAO CONCLUIDA
echo ============================================
echo.
echo Executavel:
echo %EXE_FINAL%
echo.
echo Cache incremental preservado em:
echo %BUILD_CACHE%
echo.
echo Atalho:
echo VighnaStudy
echo.
echo IMPORTANTE:
echo Se um build incremental apresentar comportamento estranho,
echo use atualizar_exe_limpo.bat uma vez.
echo.
pause
