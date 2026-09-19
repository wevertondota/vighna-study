@echo off
setlocal EnableExtensions
cd /d "%~dp0"

set "PYINSTALLER_ESPERADO=6.22.3"
set "QTA_ESPERADO=1.4.2"
set "DIST_NOVA=%CD%\dist_criacao"
set "BUILD_CACHE=%CD%\build_pyinstaller"

echo.
echo ============================================
echo   GERANDO O EXECUTAVEL DO VIGHNASTUDY
echo ============================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo ERRO: ambiente virtual .venv nao encontrado.
    echo Execute este arquivo dentro de C:\SistemaEstudos.
    pause
    exit /b 1
)

if not exist "main.py" (
    echo ERRO: main.py nao encontrado.
    pause
    exit /b 1
)

if not exist "VighnaStudy.spec" (
    echo ERRO: VighnaStudy.spec nao encontrado.
    pause
    exit /b 1
)

if not exist "estudos.db" (
    echo ERRO: estudos.db nao encontrado.
    echo Nao e seguro gerar o programa sem o seu banco atual.
    pause
    exit /b 1
)

call ".venv\Scripts\activate.bat"

set "PYI_VERSION="
for /f "usebackq delims=" %%V in (`python -c "import PyInstaller; print(PyInstaller.__version__)" 2^>nul`) do set "PYI_VERSION=%%V"

if not "%PYI_VERSION%"=="%PYINSTALLER_ESPERADO%" (
    echo Preparando PyInstaller %PYINSTALLER_ESPERADO%...
    python -m pip install "PyInstaller==%PYINSTALLER_ESPERADO%"
    if errorlevel 1 (
        echo ERRO ao preparar PyInstaller.
        pause
        exit /b 1
    )
) else (
    echo PyInstaller %PYI_VERSION% ja esta pronto.
)


echo.
echo Verificando QtAwesome...
set "QTA_VERSION="
for /f "usebackq delims=" %%V in (`python -c "import qtawesome; print(qtawesome.__version__)" 2^>nul`) do set "QTA_VERSION=%%V"

if not "%QTA_VERSION%"=="%QTA_ESPERADO%" (
    if defined QTA_VERSION (
        echo QtAwesome %QTA_VERSION% encontrado; ajustando para %QTA_ESPERADO%...
    ) else (
        echo QtAwesome nao encontrado; instalando %QTA_ESPERADO%...
    )
    python -m pip install "QtAwesome==%QTA_ESPERADO%"
    if errorlevel 1 (
        echo ERRO ao preparar QtAwesome.
        pause
        exit /b 1
    )
) else (
    echo QtAwesome %QTA_VERSION% ja esta pronto.
)

if exist "%DIST_NOVA%" rmdir /S /Q "%DIST_NOVA%"

echo.
echo Gerando a pasta do aplicativo com cache incremental...
python -m PyInstaller ^
    --noconfirm ^
    --distpath "%DIST_NOVA%" ^
    --workpath "%BUILD_CACHE%" ^
    VighnaStudy.spec

if errorlevel 1 (
    echo.
    echo ERRO durante a criacao do executavel.
    pause
    exit /b 1
)

if not exist "%DIST_NOVA%\VighnaStudy\VighnaStudy.exe" (
    echo ERRO: VighnaStudy.exe nao foi gerado.
    pause
    exit /b 1
)

if exist "%CD%\dist\SistemaEstudos" rmdir /S /Q "%CD%\dist\SistemaEstudos"
if not exist "%CD%\dist" mkdir "%CD%\dist"
move "%DIST_NOVA%\VighnaStudy" "%CD%\dist\SistemaEstudos" >nul
if exist "%DIST_NOVA%" rmdir /S /Q "%DIST_NOVA%"

copy /Y "estudos.db" "dist\SistemaEstudos\estudos.db" >nul
copy /Y "vighnastudy.ico" "dist\SistemaEstudos\vighnastudy.ico" >nul

echo.
echo ============================================
echo   PRONTO
echo ============================================
echo.
echo Seu programa esta em:
echo %CD%\dist\SistemaEstudos\VighnaStudy.exe
echo.
echo O cache foi preservado em:
echo %BUILD_CACHE%
echo.
pause
