@echo off
setlocal
cd /d "%~dp0"
title VighnaStudy - Retirar questoes Titulos IV a VIII

echo ================================================================
echo  VIGHNASTUDY - RETIRADA SEGURA DAS QUESTOES DOS TITULOS IV-VIII
echo ================================================================
echo.
echo O VighnaStudy deve estar FECHADO.
echo Esta operacao NAO apaga historico nem inteligencia.
echo.

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" "retirar_questoes_titulos_iv_viii.py"
) else (
    python "retirar_questoes_titulos_iv_viii.py"
)

set "RC=%ERRORLEVEL%"
echo.
if not "%RC%"=="0" (
    echo A operacao terminou com erro. Nao abra o Vighna antes de conferir a mensagem acima.
) else (
    echo Operacao finalizada.
)
echo.
pause
exit /b %RC%
