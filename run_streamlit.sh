#!/bin/bash

# Script para iniciar Streamlit en Mac/Linux

echo ""
echo "========================================"
echo "   BionicHand - Streamlit App"
echo "========================================"
echo ""

# Verificar si Python está disponible
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 no está instalado"
    echo "Instalarlo con: brew install python3 (Mac) o apt install python3 (Linux)"
    exit 1
fi

echo "[OK] Python detectado"
python3 --version
echo ""

# Verificar dependencias
echo "[PASO] Verificando dependencias..."
pip3 install -q streamlit plotly

if [ $? -ne 0 ]; then
    echo "[ERROR] No se pudieron instalar dependencias"
    exit 1
fi

echo "[OK] Dependencias listas"
echo ""

# Ejecutar Streamlit
echo "========================================"
echo "   Iniciando BionicHand Streamlit"
echo "========================================"
echo ""
echo "🌐 Abriendo navegador en: http://localhost:8501"
echo ""
echo "Para detener: Presionar Ctrl+C"
echo ""

streamlit run app_streamlit.py
