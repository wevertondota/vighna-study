@echo off
setlocal EnableExtensions
cd /d "%~dp0"

set "PY=.venv\Scripts\python.exe"
if exist "%PY%" goto :run
where py >nul 2>nul && set "PY=py -3" && goto :run
where python >nul 2>nul && set "PY=python" && goto :run

echo ERRO: Python nao encontrado.
pause
exit /b 2

:run
%PY% auditar_banco_ativo.py
echo.
pause
