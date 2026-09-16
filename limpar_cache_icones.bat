@echo off
echo Limpando cache visual de icones do Windows...
taskkill /IM explorer.exe /F >nul 2>nul
timeout /t 2 /nobreak >nul
del /A /Q "%localappdata%\IconCache.db" >nul 2>nul
del /A /F /Q "%localappdata%\Microsoft\Windows\Explorer\iconcache*" >nul 2>nul
start explorer.exe
echo.
echo Cache de icones renovado.
echo.
pause
