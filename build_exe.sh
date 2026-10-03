#!/bin/bash
# Script para empaquetar BionicHand Desktop como ejecutable
# Soporta: macOS, Linux

echo "========================================"
echo "Empaquetando BionicHand Desktop ..."
echo "========================================"

# Directorio base
cd "$(dirname "$0")"

# Limpiar builds anteriores
rm -rf dist build BionicHand.spec

# Crear ejecutable con PyInstaller
pyinstaller --onefile \
    --windowed \
    --name="BionicHand" \
    --icon=assets/bionic_hand_icon.icns \
    --add-data "config:config" \
    --add-data "core:core" \
    --add-data "control:control" \
    --add-data "visualization:visualization" \
    --hidden-import=mediapipe \
    --hidden-import=cv2 \
    --collect-all mediapipe \
    --collect-all opencv-python \
    app_desktop.py

echo ""
echo "========================================"
echo "Empaquetamiento completado!"
echo "========================================"
echo ""
echo "El ejecutable se encuentra en: dist/BionicHand"
echo ""
