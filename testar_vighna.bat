@echo off
setlocal EnableExtensions
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo ERRO: ambiente virtual .venv nao encontrado.
    pause
    exit /b 1
)

call ".venv\Scripts\activate.bat"

python -m py_compile main.py banco.py tema.py foco.py jogos.py checkpoint.py inteligencia.py diagnostico.py navegacao.py jornada.py evolucao.py laboratorio.py versao.py statistics_core\__init__.py statistics_core\models.py statistics_core\periods.py statistics_core\repository.py statistics_core\service.py test_statistics_core.py
if errorlevel 1 (
    echo.
    echo ERRO na verificacao de sintaxe.
    pause
    exit /b 1
)

python -m unittest -v test_statistics_core.py
if errorlevel 1 (
    echo.
    echo ERRO nos testes do Nucleo Estatistico.
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
