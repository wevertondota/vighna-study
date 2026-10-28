@echo off
setlocal EnableExtensions DisableDelayedExpansion
title VighnaStudy - Correcao de Inicializacao E4R2
echo.
echo ===============================================
echo  VighnaStudy - Recuperacao Externa Foco E4R2
echo ===============================================
echo.
set "ROOT=%~dp0.."
if not exist "%ROOT%\main.py" (
  echo A pasta CORRECAO_FOCO_E4 nao esta dentro da raiz do VighnaStudy.
  echo Informe a pasta que contem main.py, versao.py e estudos.db.
  set /p "ROOT=Pasta raiz do VighnaStudy: "
)
if not exist "%ROOT%\main.py" (
  echo.
  echo Pasta invalida. Nenhuma alteracao foi realizada.
  pause
  exit /b 1
)
if not exist "%ROOT%\.venv\Scripts\python.exe" (
  echo.
  echo Python da .venv nao encontrado. Nenhuma alteracao foi realizada.
  pause
  exit /b 1
)
"%ROOT%\.venv\Scripts\python.exe" "%~dp0executar_recuperacao.py" "%ROOT%"
set "CODE=%ERRORLEVEL%"
echo.
if "%CODE%"=="0" (
  echo Correcao concluida. Abra o VighnaStudy normalmente.
) else (
  echo Nao foi possivel concluir com seguranca. Veja a mensagem acima.
)
echo.
pause
exit /b %CODE%
