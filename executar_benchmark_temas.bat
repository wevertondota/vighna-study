@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" benchmark_startup_temas.py --runs 3
) else (
  python benchmark_startup_temas.py --runs 3
)
echo.
pause
