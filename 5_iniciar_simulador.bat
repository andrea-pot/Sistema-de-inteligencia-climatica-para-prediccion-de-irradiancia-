@echo off
title Simulador Solar - Inteligencia Climatica

:: 1. Posicionarse automaticamente en la carpeta donde esta este archivo .bat
cd /d "%~dp0"

:: 2. Buscar el activador de Anaconda en las rutas por defecto de Windows
set "CONDA_ACTIVATE="
if exist "%USERPROFILE%\anaconda3\Scripts\activate.bat" set "CONDA_ACTIVATE=%USERPROFILE%\anaconda3\Scripts\activate.bat"
if exist "%USERPROFILE%\miniconda3\Scripts\activate.bat" set "CONDA_ACTIVATE=%USERPROFILE%\miniconda3\Scripts\activate.bat"
if exist "C:\ProgramData\anaconda3\Scripts\activate.bat" set "CONDA_ACTIVATE=C:\ProgramData\anaconda3\Scripts\activate.bat"

:: 3. Activar el entorno "andrea"
if defined CONDA_ACTIVATE (
    call "%CONDA_ACTIVATE%" andrea
) else (
    call conda activate andrea
)

:: 4. Ejecutar Streamlit
streamlit run 3_scripts\9-dashboard_interactivo.py

:: 5. Evitar que la consola se cierre sola en caso de error
pause


















