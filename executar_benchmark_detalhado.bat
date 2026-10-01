@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo  VighnaStudy - Benchmark detalhado de Startup
echo ============================================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo ERRO: .venv\Scripts\python.exe nao encontrado.
    echo Coloque estes arquivos na raiz do VighnaStudy, por exemplo C:\SistemaEstudos.
    pause
    exit /b 2
)

.venv\Scripts\python.exe benchmark_startup_detalhado.py --runs 2
set ERR=%ERRORLEVEL%

echo.
if not "%ERR%"=="0" (
    echo Benchmark terminou com erro %ERR%.
) else (
    echo Benchmark concluido.
    echo Envie o arquivo benchmark_detalhado_resumo_*.csv para analise.
)
echo.
pause
exit /b %ERR%
