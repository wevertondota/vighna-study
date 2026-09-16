@echo off
setlocal
cd /d "%~dp0"

set "EXE=%CD%\dist\SistemaEstudos\SistemaEstudos.exe"

if not exist "%EXE%" (
    echo ERRO: o executavel ainda nao existe.
    echo Rode primeiro criar_exe.bat.
    pause
    exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ws = New-Object -ComObject WScript.Shell; " ^
  "$desktop = [Environment]::GetFolderPath('Desktop'); " ^
  "$s = $ws.CreateShortcut((Join-Path $desktop 'Sistema de Estudos.lnk')); " ^
  "$s.TargetPath = '%EXE%'; " ^
  "$s.WorkingDirectory = Split-Path '%EXE%'; " ^
  "$s.Description = 'Sistema de Estudos'; " ^
  "$s.Save()"

if errorlevel 1 (
    echo ERRO ao criar o atalho.
    pause
    exit /b 1
)

echo.
echo Atalho criado na Area de Trabalho:
echo Sistema de Estudos
echo.
pause
