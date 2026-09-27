@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo.
echo ============================================
echo       RECUPERACAO DO BANCO VIGHNASTUDY
echo ============================================
echo.

echo Fechando qualquer instancia do VighnaStudy antes de tocar no banco...
taskkill /IM SistemaEstudos.exe /F >nul 2>nul
taskkill /IM VighnaStudy.exe /F >nul 2>nul

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
