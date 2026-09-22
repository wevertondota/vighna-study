@echo off
setlocal
title VighnaStudy - Verificar Crimes de Transito
cd /d "%~dp0"
set "PY=C:\SistemaEstudos\.venv\Scripts\python.exe"
if not exist "%PY%" set "PY=python"
"%PY%" "%~dp0verificar_crimes_transito.py" --db "C:\SistemaEstudos\estudos.db"
echo.
pause
