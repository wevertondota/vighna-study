@echo off
setlocal
cd /d "%~dp0"
echo.
echo =====================================================
echo  VIGHNASTUDY - HOMOLOGACAO EM LABORATORIO
echo  NENHUMA ALTERACAO NO VIGHNASTUDY INSTALADO
echo =====================================================
echo.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0executar_homologacao.ps1" -Modo build
echo.
echo Pressione uma tecla para fechar. Envie o ZIP de resultados ao ChatGPT.
pause >nul
