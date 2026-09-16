@echo off
setlocal
cd /d "%~dp0"

echo.
echo ============================================
echo   GERANDO O EXECUTAVEL DO SISTEMA DE ESTUDOS
echo ============================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo ERRO: ambiente virtual .venv nao encontrado.
    echo Execute este arquivo dentro de C:\SistemaEstudos.
    pause
    exit /b 1
)

if not exist "main.py" (
    echo ERRO: main.py nao encontrado.
    pause
    exit /b 1
)

if not exist "estudos.db" (
    echo ERRO: estudos.db nao encontrado.
    echo Nao e seguro gerar o programa sem o seu banco atual.
    pause
    exit /b 1
)

call ".venv\Scripts\activate.bat"

echo Instalando/atualizando PyInstaller...
python -m pip install --upgrade pyinstaller
if errorlevel 1 (
    echo.
    echo ERRO ao instalar PyInstaller.
    pause
    exit /b 1
)

echo.
echo Gerando a pasta do aplicativo...
python -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --windowed ^
    --onedir ^
    --name SistemaEstudos ^
    main.py

if errorlevel 1 (
    echo.
    echo ERRO durante a criacao do executavel.
    pause
    exit /b 1
)

echo.
echo Copiando seu banco de dados atual...
copy /Y "estudos.db" "dist\SistemaEstudos\estudos.db" >nul

if errorlevel 1 (
    echo.
    echo ERRO ao copiar estudos.db.
    pause
    exit /b 1
)

echo.
echo ============================================
echo   PRONTO
echo ============================================
echo.
echo Seu programa esta em:
echo %CD%\dist\SistemaEstudos\SistemaEstudos.exe
echo.
echo IMPORTANTE:
echo mantenha o arquivo estudos.db na mesma pasta do EXE.
echo.
pause
