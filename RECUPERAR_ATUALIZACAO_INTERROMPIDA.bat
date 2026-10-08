@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo ERRO: ambiente virtual do Vighna nao encontrado.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" vighna_recuperar_atualizacao.py
if errorlevel 1 (
  echo AVISO: nao foi possivel recuperar automaticamente. Preserve a pasta backups.
)
pause
