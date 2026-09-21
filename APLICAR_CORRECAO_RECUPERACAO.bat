@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo.
echo ============================================
echo  RECUPERACAO SEGURA - VIGHNASTUDY 0.29.6
echo ============================================
echo.
echo Este processo NAO substitui o seu banco por uma copia antiga.
echo Ele apenas adiciona as questoes historicamente recuperadas que ainda faltarem.
echo.

if not exist "estudos.db" (
    echo ERRO: estudos.db nao encontrado na raiz do projeto.
    pause
    exit /b 1
)
if not exist "questoes_recuperadas_42.json" (
    echo ERRO: questoes_recuperadas_42.json nao encontrado.
    pause
    exit /b 1
)

set "PY=.venv\Scripts\python.exe"
if exist "%PY%" goto :run
where py >nul 2>nul && set "PY=py -3" && goto :run
where python >nul 2>nul && set "PY=python" && goto :run

echo ERRO: Python nao encontrado.
pause
exit /b 2

:run
taskkill /IM VighnaStudy.exe /F >nul 2>nul
taskkill /IM SistemaEstudos.exe /F >nul 2>nul
if not exist "backups" mkdir "backups"

%PY% mesclar_questoes_recuperadas.py --target "%CD%\estudos.db" --data "%CD%\questoes_recuperadas_42.json" --backup-dir "%CD%\backups"
if errorlevel 1 (
    echo.
    echo ERRO: a recuperacao nao foi concluida.
    echo O backup criado antes da tentativa foi preservado.
    pause
    exit /b 1
)

echo.
%PY% auditar_banco_ativo.py
if errorlevel 1 (
    echo.
    echo ATENCAO: a auditoria ainda nao encontrou as contagens esperadas.
    pause
    exit /b 1
)

echo.
echo RECUPERACAO VALIDADA.
echo Agora teste com: python main.py
pause
