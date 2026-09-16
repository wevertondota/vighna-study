@echo off
setlocal EnableExtensions
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo ERRO: ambiente virtual .venv nao encontrado.
    pause
    exit /b 1
)

call ".venv\Scripts\activate.bat"

python -m py_compile main.py banco.py tema.py foco.py jogos.py checkpoint.py inteligencia.py diagnostico.py navegacao.py jornada.py evolucao.py laboratorio.py versao.py
if errorlevel 1 (
    echo.
    echo ERRO na verificacao de sintaxe.
    pause
    exit /b 1
)

python testes_smoke.py
if errorlevel 1 (
    echo.
    echo ERRO nos testes smoke.
    pause
    exit /b 1
)

python main.py
