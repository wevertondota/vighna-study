@echo off
setlocal
cd /d "%~dp0"
title VighnaStudy - Restaurar questoes Titulos IV a VIII

echo ================================================================
echo  VIGHNASTUDY - RESTAURAR QUESTOES RETIRADAS DOS TITULOS IV-VIII
echo ================================================================
echo.
echo Use este arquivo somente se quiser desfazer a retirada.
echo O VighnaStudy deve estar FECHADO.
echo.

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" "restaurar_questoes_titulos_iv_viii.py"
) else (
    python "restaurar_questoes_titulos_iv_viii.py"
)

set "RC=%ERRORLEVEL%"
echo.
pause
exit /b %RC%
