# BionicHand Desktop v2 - Versión Local de Desarrollo

**VERSIÓN LOCAL DE PRUEBAS - NO AFECTA main.py ni app_streamlit.py**

## Descripción

Esta es una versión mejorada de la aplicación desktop con:
- ✅ UI dinámico (Modo SLIDERS sin cámara, Modo CÁMARA sin sliders)
- ✅ Detección de mano MEJORADA (múltiples rangos HSV, CLAHE, morfología avanzada)
- ✅ Gestos de mano (FIST, OPEN, PINCH, POINTING)
- ✅ Visualización 3D en tiempo real

## Cómo Ejecutar

```bash
# Terminal en: C:\Users\GHOPsT\Desktop\ManoBionica\bionic_hand

python app_desktop_v2.py
```

## Estructura de Modos

### Modo SLIDERS (Por Defecto)
- **Panel Izquierdo**: 3 sliders para controlar cada servo
  - Servo 1 (Índice): 0-100%
  - Servo 2 (Grupo: Medio, Anular, Meñique): 0-100%
  - Servo 3 (Pulgar): 0-100%
- **Botones de Postura**: ABIERTA, PUÑO, PINZA, SEÑALAR
- **Panel Derecho**: Visualización 3D de la mano en tiempo real
- **Sin Cámara**: No se captura video

### Modo CÁMARA (Nuevo)
- **Panel Izquierdo**: Feed de cámara en vivo con detección automática
- **Indicador**: Muestra "✓ Mano detectada" o "✗ Mano no detectada"
- **Panel Derecho**: Visualización 3D sincronizada con movimientos detectados
- **Sin Sliders**: Desaparecen los controles manuales
- **Automático**: La mano se controla por la cámara

### Modo GESTOS
- Igual que CÁMARA pero con reconocimiento de gestos
- Muestra el gesto detectado

## Mejoras en Detección de Mano

### HSV Mejorado
Se usan **3 rangos HSV diferentes** para capturar más tonos de piel:
```python
# Rango 1: Tonos cálidos claros (rojo/naranja)
Rango 1: H(0-20), S(10-255), V(40-255)

# Rango 2: Tonos rojo oscuro
Rango 2: H(170-180), S(10-255), V(40-255)

# Rango 3: Tonos más desaturados/naturales
Rango 3: H(5-25), S(20-240), V(50-210)
```

### Procesamiento Avanzado
1. **CLAHE** (Contrast Limited Adaptive Histogram Equalization)
   - Mejora contraste en iluminación desigual
   
2. **Morfología Agresiva**
   - Cierre 2x + Apertura 1x con kernel (7,7)
   - Dilatación con kernel (5,5)
   - Elimina ruido pequeño
   
3. **Detección de Contornos**
   - Encuentra el contorno más grande
   - Valida tamaño (1%-80% del frame)
   - Calcula propiedades: área, perímetro, solidity, aspect ratio
   
4. **Estimación de Dedos**
   - Usa aproximación de contorno (Ramer-Douglas-Peucker)
   - Cuenta vértices ÷ 3 = número de dedos
   - Rango: 1-5 dedos

## Mejoras en Visualización 3D Profesional (Commit ddf6d3e)

La visualización 3D ahora es **idéntica a visualizer.py** (main.py):

### Cilindros Volumétricos
- Cada falange se dibuja como un cilindro 3D con radio variable
- Falange proximal: radio 4.5 mm (más gruesa)
- Falange distal: radio 4.0 mm (más fina)
- Superficies suaves con 12 lados (círculo discretizado)

### Esferas Articulares
- **Base (origen)**: esfera 3.5 mm, color articulación
- **Nudillo (MCP)**: esfera 3.0 mm, color articulación
- **Yema (fingertip)**: esfera 4.5 mm, color almohadilla

### Colores por Dedo
```
Pulgar   → Rojo (#ef4444, articulaciones #b91c1c, pads #fca5a5)
Índice   → Azul (#3b82f6, articulaciones #1d4ed8, pads #93c5fd)
Medio    → Verde (#10b981, articulaciones #047857, pads #6ee7b7)
Anular   → Naranja (#f59e0b, articulaciones #b45309, pads #fde68a)
Meñique  → Púrpura (#8b5cf6, articulaciones #6d28d9, pads #c4b5fd)
```

### Transparencias
- Cilindros: 0.88 alpha (traslúcidos)
- Articulaciones: 0.92 alpha (más opacos)
- Yemas: 0.85 alpha (almohadillas de contacto)

### FIST (Puño)
- Solidity > 0.65 (forma compacta)
- Dedos visibles ≤ 1
- Interpretación: Todos los dedos doblados

### OPEN_PALM (Mano Abierta)
- Dedos ≥ 4 (muchos vértices)
- Solidity < 0.55 (forma dispersa)
- Interpretación: Todos los dedos extendidos

### PINCH (Pinza)
- Dedos 2-3
- Solidity > 0.60
- Interpretación: Pulgar + Índice juntos

### POINTING (Señalar)
- Dedos = 1
- Solidity > 0.70
- Interpretación: Solo índice extendido

### NEUTRAL (Posición Neutra)
- Cualquier otra combinación

## Mapeo Gesto → Servo

| Gesto | u_index | u_group | u_thumb | Descripción |
|-------|---------|---------|---------|-------------|
| OPEN | 0.0 | 0.0 | 0.0 | Todos extendidos |
| FIST | 0.95 | 0.95 | 0.90 | Todos doblados |
| PINCH | 0.75 | 0.0 | 0.85 | Pulgar + Índice |
| POINTING | 0.0 | 1.0 | 0.90 | Solo índice |
| NEUTRAL | 0.4 | 0.3 | 0.3 | Posición media |

## Iluminación Recomendada

Para mejor detección:
- ✅ Luz natural frontal (mejor)
- ✅ Luz artificial pero no sombras duras
- ⚠️ Evitar contraluz
- ⚠️ Evitar sombras sobre la mano

## Troubleshooting

### La cámara no detecta mi mano
1. **Iluminación**: Asegura que la mano esté bien iluminada
2. **Distancia**: Mano a 20-50 cm de la cámara
3. **Fondo**: Fondo uniforme (no muy similar al tono de piel)
4. **Rotación**: Intenta diferentes ángulos

### Los gestos no se reconocen correctamente
1. Los gestos usan estimaciones simples (no AI)
2. Son aproximaciones basadas en propiedades de contorno
3. Mejor funciona con gestos "puros" (bien definidos)

### La visualización 3D está lenta
- Reduce la resolución de cámara (modificar en HandTrackingThread)
- O ejecuta sin cámara (modo SLIDERS)

## Archivos Involucrados

```
app_desktop_v2.py          ← NUEVO: Aplicación principal mejorada
control/hand_tracking.py   ← MODIFICADO: Detección mejorada
control/poses.py           ← Sin cambios
core/hand.py               ← Sin cambios
core/finger.py             ← Sin cambios
core/joint.py              ← Sin cambios
```

## Diferencias con app_desktop.py (original)

| Aspecto | v1 | v2 |
|--------|----|----|
| **UI Layout** | Estático (siempre ambos paneles) | Dinámico (cambia por modo) |
| **Modo SLIDERS** | Muestra sliders + cámara | Solo sliders (limpio) |
| **Modo CÁMARA** | Muestra cámara + sliders | Solo cámara (limpio) |
| **Detección HSV** | 1 rango (muy restrictivo) | 3 rangos (flexible) |
| **Preprocesamiento** | Básico | CLAHE + morfología |
| **Dedos** | Perímetro simple | Contour approximation |
| **Gestos** | Lógica simple | Mejorada con aspect ratio |

## Notas de Desarrollo

- Esta versión es **LOCAL ONLY** - no afecta a main.py ni app_streamlit.py
- main.py y app_streamlit.py siguen siendo las versiones funcionales de producción
- Una vez que v2 sea estable, se puede integrar con main.py
- Para producción, se necesita:
  - Entrenar con más manos/iluminaciones
  - Usar ML/AI para reconocimiento más preciso
  - Calibración per-usuario

## Próximas Mejoras (TODO)

- [ ] Agregar calibración de HSV por usuario
- [ ] Usar AprilTags o markers para posición 3D real
- [ ] Agregar tracking temporal (Kalman filter)
- [ ] Entrenar NN para gestos (en lugar de heurística)
- [ ] Multi-hand support
- [ ] Grabación de sesiones
- [ ] Exportar data para análisis

---
**Versión**: 2.0 (Local Dev)  
**Commit**: c7bb0c1  
**Última actualización**: 2026-10-03
