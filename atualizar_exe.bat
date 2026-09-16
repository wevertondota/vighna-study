@echo off
setlocal EnableExtensions
cd /d "%~dp0"

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

if not exist "vighnastudy.ico" (
    echo ERRO: vighnastudy.ico nao encontrado em:
    echo %CD%
    pause
    exit /b 1
)

set "APP_ATUAL=%CD%\dist\SistemaEstudos"
set "TEMP_DADOS=%CD%\_dados_antes_atualizacao"
set "DIST_NOVA=%CD%\dist_nova"
set "BUILD_NOVO=%CD%\build_novo"
set "SAIDA_NOVA=%DIST_NOVA%\VighnaStudy"
set "EXE_FINAL=%CD%\dist\SistemaEstudos\VighnaStudy.exe"

echo Fechando processos antigos, se ainda estiverem abertos...
taskkill /IM SistemaEstudos.exe /F >nul 2>nul
taskkill /IM VighnaStudy.exe /F >nul 2>nul

if exist "%TEMP_DADOS%" rmdir /S /Q "%TEMP_DADOS%"
mkdir "%TEMP_DADOS%"

echo.
echo Preservando banco e backups...

if exist "%APP_ATUAL%\estudos.db" (
    ".venv\Scripts\python.exe" copiar_banco_consistente.py "%APP_ATUAL%\estudos.db" "%TEMP_DADOS%\estudos.db"
    if errorlevel 1 (
        echo ERRO: o banco ativo nao passou pela copia consistente do SQLite.
        echo A atualizacao foi cancelada para proteger seus dados.
        pause
        exit /b 1
    )
    copy /Y "%TEMP_DADOS%\estudos.db" "%CD%\estudos.db" >nul
    echo Banco ativo preservado por snapshot SQLite consistente.
) else (
    if exist "%CD%\estudos.db" (
        ".venv\Scripts\python.exe" copiar_banco_consistente.py "%CD%\estudos.db" "%TEMP_DADOS%\estudos.db"
        if errorlevel 1 (
            echo ERRO: o banco da pasta principal nao passou pela verificacao de integridade.
            echo Execute recuperar_banco.bat antes de atualizar.
            pause
            exit /b 1
        )
        echo Usando snapshot consistente do banco da pasta principal.
    ) else (
        echo ERRO: nenhum estudos.db foi encontrado.
        pause
        exit /b 1
    )
)

if exist "%APP_ATUAL%\backups" (
    xcopy "%APP_ATUAL%\backups" "%TEMP_DADOS%\backups\" /E /I /Y >nul
)

call ".venv\Scripts\activate.bat"

echo.
echo Verificando PyInstaller...
python -m pip install --upgrade pyinstaller
if errorlevel 1 (
    echo ERRO ao instalar/atualizar PyInstaller.
    pause
    exit /b 1
)

if exist "%DIST_NOVA%" rmdir /S /Q "%DIST_NOVA%"
if exist "%BUILD_NOVO%" rmdir /S /Q "%BUILD_NOVO%"

echo.
echo Gerando VighnaStudy.exe com o novo icone...

python -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --windowed ^
    --onedir ^
    --icon="%CD%\vighnastudy.ico" ^
    --name VighnaStudy ^
    --distpath "%DIST_NOVA%" ^
    --workpath "%BUILD_NOVO%" ^
    main.py

if errorlevel 1 (
    echo.
    echo ERRO durante a geracao da nova versao.
    echo A versao anterior continua preservada.
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
echo Restaurando banco e backups na nova versao...

copy /Y "%TEMP_DADOS%\estudos.db" "%SAIDA_NOVA%\estudos.db" >nul

if exist "%TEMP_DADOS%\backups" (
    xcopy "%TEMP_DADOS%\backups" "%SAIDA_NOVA%\backups\" /E /I /Y >nul
)

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
    echo Verifique C:\SistemaEstudos\dist_nova.
    pause
    exit /b 1
)

if exist "%DIST_NOVA%" rmdir /S /Q "%DIST_NOVA%"
if exist "%BUILD_NOVO%" rmdir /S /Q "%BUILD_NOVO%"
if exist "%TEMP_DADOS%" rmdir /S /Q "%TEMP_DADOS%"

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
echo Atalho:
echo VighnaStudy
echo.
echo IMPORTANTE:
echo O executavel antigo SistemaEstudos.exe foi substituido por VighnaStudy.exe.
echo.
pause
