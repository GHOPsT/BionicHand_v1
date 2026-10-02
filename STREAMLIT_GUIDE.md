# 🎬 STREAMLIT — GUÍA RÁPIDA DE INICIO

## ✨ ¿QUÉ ES STREAMLIT?

- 🌐 **Interfaz web** (en navegador, no requiere X11)
- ⚡ **Tiempo real** (actualizaciones instantáneas)
- 📱 **Responsive** (funciona en móvil también)
- ☁️ **Publicable** (Streamlit Cloud con link público)
- 🔧 **Simple** (sin configuración extra)

---

## 🚀 EJECUCIÓN RÁPIDA

### En tu máquina (Windows/Mac/Linux)

```bash
# Terminal en carpeta bionic_hand:
streamlit run app_streamlit.py
```

**Resultado**: Se abre navegador en `http://localhost:8501`

**Tiempo**: ~2-3 segundos

---

## 🎮 CONTROLES

### Panel Izquierdo: Visualización 3D
- 🖱️ Rotar: Click + arrastrar
- 🔍 Zoom: Scroll del ratón
- 👁️ Interactivo en tiempo real

### Panel Derecho: Controles
- 🖐️ **Botones rápidos**: Abierta, Puño, Pinza, Señalar
- 🎚️ **Sliders**: Control fino de cada servo (0-100%)
- 📊 **Telemetría**: PWM + Ángulos en tiempo real

---

## 📦 INSTALACIÓN (Primera vez)

Si streamlit no está instalado:

```bash
pip install streamlit plotly
```

**O** si tienes requirements.txt:

```bash
pip install -r requirements.txt
```

---

## 🌍 PUBLICAR EN INTERNET (Opcional)

### 1. Subir a GitHub
```bash
git add app_streamlit.py requirements.txt
git commit -m "Streamlit app"
git push
```

### 2. Conectar a Streamlit Cloud
- Ir a: https://share.streamlit.io
- Conectar tu GitHub
- Seleccionar repo → branch → `app_streamlit.py`
- Click "Deploy"

### 3. ✨ Listo
- Tienes un link público: `https://tu-usuario-bionichand.streamlit.app`
- Compartir con clientes sin instalar nada

---

## 📊 CARACTERÍSTICAS ACTUALES

| Feature | Status | Detalles |
|---------|--------|---------|
| Visualización 3D | ✅ Plotly | Interactiva, rotatoria |
| Posturas rápidas | ✅ 4 botones | Open, Power, Pinch, Point |
| Sliders servo | ✅ 3 controles | Control fino en tiempo real |
| Telemetría PWM | ✅ Real-time | 1000-2000 µs |
| Ángulos articulares | ✅ Real-time | MCP + PIP grados |
| Información técnica | ✅ Expandible | Especificaciones CAD |

---

## 🔧 TROUBLESHOOTING

| Problema | Solución |
|----------|----------|
| "streamlit not found" | `pip install streamlit` |
| Port 8501 en uso | `streamlit run app.py --logger.level=debug --server.port 8502` |
| Lentitud 3D | Reducir resolución o actualizar gráfica |
| No muestra cambios | Refrescar página (F5) o activar "Always rerun" |

---

## 📁 ARCHIVOS RELACIONADOS

- `app_streamlit.py` - Aplicación principal
- `requirements.txt` - Dependencias (incluye plotly)
- `core/hand.py` - Lógica de la mano
- `config/dimensions.py` - Medidas CAD

---

## ✅ SIGUIENTE

Después de Streamlit, puedes:

1. **Publicar en Streamlit Cloud** (con link público)
2. **Agregar más visualizaciones** (telemetría avanzada)
3. **Integrar EMG** (control por electromiografía)
4. **Conectar con CoppeliaSim** (simulación dinámica)

---

**¿Ejecutar ahora?** 🚀

```bash
streamlit run app_streamlit.py
```
