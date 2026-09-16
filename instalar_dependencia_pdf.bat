@echo off
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo.
    echo ERRO: ambiente .venv nao encontrado nesta pasta.
    echo Copie este arquivo para C:\SistemaEstudos e execute novamente.
    echo.
    pause
    exit /b 1
)

echo.
echo Instalando suporte de leitura de PDF no VighnaStudy...
echo.

".venv\Scripts\python.exe" -m pip install --upgrade pypdf

echo.
echo Concluido.
echo Agora teste com:
echo.
echo .venv\Scripts\python.exe main.py
echo.
pause
