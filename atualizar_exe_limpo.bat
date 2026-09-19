@echo off
setlocal
cd /d "%~dp0"

echo.
echo ============================================
echo       BUILD LIMPO DO VIGHNASTUDY
echo ============================================
echo.
echo Este modo apaga o cache do PyInstaller antes de gerar o EXE.
echo Use apenas quando o build incremental falhar, apos trocar versoes
echo importantes de dependencias ou para diagnostico.
echo.

set "VIGHNA_CLEAN_BUILD=1"
call "%~dp0atualizar_exe.bat"
exit /b %errorlevel%
