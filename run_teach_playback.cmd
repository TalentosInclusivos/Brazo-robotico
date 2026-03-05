@echo off
setlocal EnableExtensions

cd /d "%~dp0"

set "VENV_DIR=.venv"
set "VENV_PY=%VENV_DIR%\Scripts\python.exe"
set "PORT=%~1"
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"

if "%PORT%"=="" set "PORT=COM3"

where py >nul 2>nul
if %ERRORLEVEL%==0 (
    set "PYTHON=py -3"
) else (
    set "PYTHON=python"
)

if not exist "%VENV_PY%" (
    echo [1/4] Creando entorno virtual en "%VENV_DIR%"...
    %PYTHON% -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo Error: no se pudo crear el entorno virtual.
        exit /b 1
    )
)

echo [2/4] Verificando Python del entorno virtual...
if not exist "%VENV_PY%" (
    echo Error: no existe "%VENV_PY%".
    exit /b 1
)

echo [3/4] Instalando dependencias...
"%VENV_PY%" -m pip install --upgrade pip >nul
"%VENV_PY%" -m pip install pyserial
if errorlevel 1 (
    echo Error: fallo instalando pyserial.
    exit /b 1
)

echo [4/4] Ejecutando teach_playback en puerto %PORT%...
"%VENV_PY%" teach_playback.py --port "%PORT%"

endlocal
