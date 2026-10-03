@echo off
REM Script para empaquetar BionicHand Desktop como ejecutable .exe
REM Requiere: PyInstaller instalado

echo ========================================
echo Empaquetando BionicHand Desktop ...
echo ========================================

REM Directorio base
cd /d "%~dp0"

REM Limpiar builds anteriores
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist BionicHand.spec del BionicHand.spec

REM Crear ejecutable con PyInstaller
pyinstaller --onefile ^
    --windowed ^
    --name="BionicHand" ^
    --icon=assets/bionic_hand_icon.ico ^
    --add-data "config:config" ^
    --add-data "core:core" ^
    --add-data "control:control" ^
    --add-data "visualization:visualization" ^
    --hidden-import=mediapipe ^
    --hidden-import=cv2 ^
    --hidden-import=pyqtgraph ^
    --collect-all mediapipe ^
    --collect-all opencv-python ^
    app_desktop.py

echo.
echo ========================================
echo Empaquetamiento completado!
echo ========================================
echo.
echo El ejecutable se encuentra en: dist/BionicHand.exe
echo.
pause
