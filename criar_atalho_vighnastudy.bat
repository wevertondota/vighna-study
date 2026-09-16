@echo off
setlocal EnableExtensions
cd /d "%~dp0"

set "EXE=%CD%\dist\SistemaEstudos\VighnaStudy.exe"
set "ICO=%CD%\dist\SistemaEstudos\vighnastudy.ico"

if not exist "%EXE%" (
    echo ERRO: VighnaStudy.exe nao encontrado:
    echo %EXE%
    pause
    exit /b 1
)

if not exist "%ICO%" (
    if exist "%CD%\vighnastudy.ico" (
        copy /Y "%CD%\vighnastudy.ico" "%ICO%" >nul
    )
)

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ws = New-Object -ComObject WScript.Shell; " ^
  "$desktop = $ws.SpecialFolders.Item('Desktop'); " ^
  "$link = Join-Path $desktop 'VighnaStudy.lnk'; " ^
  "if (Test-Path $link) { Remove-Item $link -Force }; " ^
  "$s = $ws.CreateShortcut($link); " ^
  "$s.TargetPath = '%EXE%'; " ^
  "$s.WorkingDirectory = '%CD%\dist\SistemaEstudos'; " ^
  "$s.IconLocation = '%ICO%,0'; " ^
  "$s.Description = 'VighnaStudy'; " ^
  "$s.Save()"

ie4uinit.exe -show >nul 2>nul

echo.
echo Atalho VighnaStudy recriado.
echo Se o Windows ainda mostrar o icone antigo, pressione F5 na Area de Trabalho.
echo.
pause
