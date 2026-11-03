@echo off
setlocal
cd /d "%~dp0"
title VighnaStudy - Reparo Externo Home V9 R2
if not exist ".venv\Scripts\python.exe" (
  echo ERRO: Ambiente .venv nao encontrado nesta pasta.
  echo Extraia os arquivos diretamente em C:\SistemaEstudos ou na raiz real do VighnaStudy.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" "APLICAR_REPARO_HOME_V9.py"
set "RESULTADO=%errorlevel%"
echo.
if "%RESULTADO%"=="0" (echo Processo encerrado.) else (echo O reparo nao foi concluido. Verifique a mensagem acima.)
pause
exit /b %RESULTADO%
