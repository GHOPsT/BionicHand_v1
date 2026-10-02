@echo off
REM Script para iniciar Streamlit en Windows

echo.
echo ========================================
echo   BionicHand - Streamlit App
echo ========================================
echo.

REM Verificar si pip está disponible
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python no está instalado
    echo Descargar: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python detectado
python --version
echo.

REM Verificar dependencias
echo [PASO] Verificando dependencias...
pip install -q streamlit plotly

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] No se pudieron instalar dependencias
    pause
    exit /b 1
)

echo [OK] Dependencias listas
echo.

REM Ejecutar Streamlit
echo ========================================
echo   Iniciando BionicHand Streamlit
echo ========================================
echo.
echo 🌐 Abriendo navegador en: http://localhost:8501
echo.
echo Para detener: Presionar Ctrl+C
echo.

streamlit run app_streamlit.py

pause
