@echo off
setlocal
cd /d "%~dp0"
title VighnaStudy - Painel de Homologacao
py -3.13 -B "%~dp0painel_homologacao.py"
if not "%ERRORLEVEL%"=="0" (
  echo.
  echo Nao foi possivel abrir o painel com o Python 3.13.
  echo O painel usa tkinter, que acompanha a instalacao comum do Python.
  echo Confirme se o Python 3.13 esta instalado e execute novamente.
  echo.
  pause
)
