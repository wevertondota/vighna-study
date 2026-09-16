@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo.
echo ============================================
echo       RECUPERACAO DO BANCO VIGHNASTUDY
echo ============================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo ERRO: .venv\Scripts\python.exe nao encontrado.
    echo Execute este arquivo a partir de C:\SistemaEstudos.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" recuperar_banco.py
set "CODIGO=%ERRORLEVEL%"

echo.
pause
exit /b %CODIGO%
