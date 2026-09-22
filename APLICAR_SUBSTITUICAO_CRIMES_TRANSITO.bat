@echo off
setlocal
title VighnaStudy - Substituir Crimes de Transito
cd /d "%~dp0"

echo ============================================================
echo VighnaStudy - Substituicao das 72 questoes de Crimes de Transito
echo ============================================================
echo.
echo Feche o VighnaStudy antes de continuar.
echo O banco usado sera:
echo C:\SistemaEstudos\estudos.db
echo.
pause

set "PY=C:\SistemaEstudos\.venv\Scripts\python.exe"
if not exist "%PY%" set "PY=python"

"%PY%" "%~dp0migrar_crimes_transito_vpq.py" --db "C:\SistemaEstudos\estudos.db"
if errorlevel 1 (
    echo.
    echo A SUBSTITUICAO NAO FOI CONCLUIDA.
    echo Nenhuma alteracao parcial foi mantida.
    pause
    exit /b 1
)

echo.
echo Executando verificacao final...
"%PY%" "%~dp0verificar_crimes_transito.py" --db "C:\SistemaEstudos\estudos.db"
echo.
pause
