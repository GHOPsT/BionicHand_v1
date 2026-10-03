# Explicación Detallada: Cómo Funciona la Detección de Mano

## 🎯 Flujo General

```
Frame de Cámara (BGR)
        ↓
Aplicar CLAHE (mejora contraste)
        ↓
Convertir BGR → HSV
        ↓
Crear 4 máscaras HSV (rangos de piel)
        ↓
Combinar máscaras con OR lógico
        ↓
Operaciones morfológicas (limpiar ruido)
        ↓
Encontrar contornos
        ↓
Filtrar por tamaño (área)
        ↓
Calcular propiedades (solidity, dedos, etc.)
        ↓
Retornar hand_data
```

---

## 📊 Paso 1: Pre-procesamiento de Imagen

### CLAHE (Contrast Limited Adaptive Histogram Equalization)

**Qué hace**: Normaliza el brillo y contraste de forma local (no global)

```python
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
gray = clahe.apply(gray)
```

- Divide la imagen en 8x8 tiles
- Mejora el contraste dentro de cada tile
- Evita amplificar ruido demasiado (clipLimit=2.0)
- **Propósito**: Funciona bien con iluminación desigual

⚠️ **PROBLEMA ACTUAL**: El CLAHE se calcula pero NO se usa directamente. Se aplicaría mejor en la detección HSV.

---

## 🎨 Paso 2: Conversión a HSV y Detección de Rangos

### ¿Por qué HSV en lugar de BGR?

- **BGR (RGB)**: Depende mucho de la iluminación
- **HSV**: Separa color (H), saturación (S) e intensidad (V)
  - **H (Hue)**: Color puro (0-180°) - naranja/rojo de piel
  - **S (Saturation)**: Intensidad del color (0-255) - cuán puro es el color
  - **V (Value)**: Brillo (0-255) - cuán claro/oscuro

### 4 Rangos HSV para Detectar Piel

```python
# Rango 1: Tonos cálidos claros
Lower:  [0,   15,  60]   → H: rojo puro, S: poco saturado, V: oscuro
Upper:  [20,  170, 255]  → H: naranja, S: muy saturado, V: muy brillante

# Rango 2: Tonos rojo oscuro (H en los extremos)
Lower:  [170, 15,  40]   → H: rojo oscuro, S: poco, V: muy oscuro
Upper:  [180, 170, 255]  → H: rojo puro, S: saturado, V: brillante

# Rango 3: Tonos naturales/desaturados
Lower:  [5,   20,  50]   → H: rojo, S: muy desaturado, V: oscuro
Upper:  [25,  180, 220]  → H: naranja, S: saturado, V: muy claro

# Rango 4: Tonos saturados (bronceado)
Lower:  [0,   30,  50]   → H: rojo, S: saturado, V: oscuro
Upper:  [30,  255, 255]  → H: amarillo, S: muy saturado, V: brillante
```

**Lógica**: Combinar muchos rangos para capturar:
- Piel clara bajo luz fría
- Piel oscura 
- Piel bronceada
- Diferentes iluminaciones

### Crear Máscaras

```python
mask1 = cv2.inRange(hsv_frame, [0,15,60], [20,170,255])
mask2 = cv2.inRange(hsv_frame, [170,15,40], [180,170,255])
mask3 = cv2.inRange(hsv_frame, [5,20,50], [25,180,220])
mask4 = cv2.inRange(hsv_frame, [0,30,50], [30,255,255])

mask = mask1 | mask2 | mask3 | mask4  # Combinar con OR
```

**Resultado**: `mask` es una imagen binaria donde:
- Píxeles blancos (255) = probablemente piel
- Píxeles negros (0) = no piel

---

## 🧹 Paso 3: Operaciones Morfológicas (Limpiar Ruido)

### Problema: La máscara tiene mucho ruido

Ruido típico:
- Objetos pequeños detectados como "piel" (botones, ropa, etc.)
- Agujeros dentro de la mano (dedos separados)
- Bordes fragmentados

### Solución: Operaciones Morfológicas

```python
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))

# CIERRE (Close): Rellenar agujeros
mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

# APERTURA (Open): Eliminar objetos pequeños
mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)

# DILATACIÓN: Expandir la región
kernel2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
mask = cv2.dilate(mask, kernel2, iterations=1)
```

**Efectos**:
1. **Close**: Llena pequeños agujeros negros (dedos que aparecen separados)
2. **Open**: Elimina pequeños puntos blancos (ruido aleatorio)
3. **Dilate**: Expande la región blanca para conectar componentes

---

## 🔍 Paso 4: Encontrar Contornos

```python
contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

# Encontrar el contorno más grande (asumimos que es la mano)
largest_contour = max(contours, key=cv2.contourArea)
area = cv2.contourArea(largest_contour)
```

**¿Por qué el más grande?**: Asumimos que la mano es lo más grande que detectamos. Si hay fondo mal detectado, será problema.

---

## 📏 Paso 5: Filtrado por Tamaño

```python
h, w = frame.shape[:2]  # altura, ancho del frame
min_area = (w * h) * 0.01  # Mínimo 1% del frame
max_area = (w * h) * 0.9   # Máximo 90% del frame

if min_area < area < max_area:
    # ✓ Tamaño válido de mano
else:
    # ✗ Demasiado pequeño o grande - no es mano
```

**Ejemplo con frame 640x480 = 307,200 píxeles**:
- Min: ~3,072 píxeles (área pequeña)
- Max: ~276,480 píxeles (la mayoría del frame)

⚠️ **PROBLEMA**: Si la mano está lejos (pocas píxeles), NO se detecta.

---

## 👆 Paso 6: Contar Dedos

### Método: Contour Approximation (Ramer-Douglas-Peucker)

```python
perimeter = cv2.arcLength(largest_contour, True)
epsilon = 0.02 * perimeter  # Tolerancia: 2% del perímetro
approx = cv2.approxPolyDP(largest_contour, epsilon, True)

finger_count = len(approx)  # Número de vértices
finger_count = max(1, min(int(finger_count / 2.5), 5))
```

**¿Qué hace?**
- Simplifica el contorno encontrando sus "esquinas" principales
- Cada dedo extendido ≈ 2-3 vértices
- Divide entre 2.5 para estimar número de dedos

**Ejemplo**:
- Mano abierta: ~12 vértices → 12/2.5 = 4.8 → 4 dedos ✓
- Puño: ~4 vértices → 4/2.5 = 1.6 → 1 dedo ✓
- Pinza: ~6 vértices → 6/2.5 = 2.4 → 2 dedos ✓

---

## 📊 Paso 7: Calcular Propiedades

```python
# Convex Hull (envolvente convexa)
hull = cv2.convexHull(largest_contour)
hull_area = cv2.contourArea(hull)

# Solidity: Cuán "sólida" es la forma
# Solidity = área_contorno / área_hull
# Rango: 0-1
# - 1.0 = círculo perfecto (puño)
# - 0.5 = forma muy dispersa (mano abierta)
solidity = area / hull_area if hull_area > 0 else 0

# Centroide (centro de masa)
M = cv2.moments(largest_contour)
cx = M["m10"] / M["m00"]
cy = M["m01"] / M["m00"]
```

---

## 🎬 Paso 8: Mapeo a Servo (Gesture Recognition)

```python
def detect_gesture(landmarks):
    finger_count = landmarks.get("finger_count", 0)
    solidity = landmarks.get("solidity", 0.5)
    
    if solidity > 0.65 and finger_count <= 1:
        return "FIST"  # Puño
    elif finger_count >= 4 and solidity < 0.55:
        return "OPEN_PALM"  # Mano abierta
    elif 2 <= finger_count <= 3 and solidity > 0.60:
        return "PINCH"  # Pinza
    elif finger_count == 1 and solidity > 0.70:
        return "POINTING"  # Señalar
    else:
        return "NEUTRAL"
```

Luego mapea a servo:
```python
gesture_servo_map = {
    "FIST": {"u_index": 0.95, "u_group": 0.95, "u_thumb": 0.90},
    "OPEN_PALM": {"u_index": 0.0, "u_group": 0.0, "u_thumb": 0.0},
    "PINCH": {"u_index": 0.75, "u_group": 0.0, "u_thumb": 0.85},
    "POINTING": {"u_index": 0.0, "u_group": 1.0, "u_thumb": 0.90},
}
```

---

## ⚠️ PROBLEMAS ACTUALES - Por Qué NO Detecta Bien

### Problema 1: Rangos HSV Demasiado Restrictivos

Los 4 rangos están hechos para "piel genérica" pero:
- Tu tono de piel puede estar fuera de estos rangos
- La iluminación en tu cuarto es diferente
- Ropa roja/naranja (como tu camisa) interfiere

**Solución**: Calibrar los rangos HSV específicamente para tu iluminación y piel

### Problema 2: Tamaño Mínimo

Si la mano está a más de 30-40 cm, el área será < 1% del frame y NO se detecta

**Solución**: Poner la mano más cerca de la cámara (20-30 cm)

### Problema 3: Fondo Similar a Piel

Si el fondo es similar al tono de piel, se confunde

**Solución**: Usar un fondo diferente (blanco, azul, negro)

### Problema 4: Rangos HSV Solapados

Los 4 rangos son muy generales y pueden capturar cosas que no son mano

**Solución**: Afinar tolerancias de S y V

### Problema 5: Dedos Muy Abiertos

Si los dedos están muy separados, se detectan como múltiples contornos pequeños en lugar de un contorno grande

**Solución**: Mantener dedos más juntos o ajustar morfología

---

## 🔧 Cómo Mejorar la Detección

### Opción A: Calibración Manual (Rápida)

1. Abre `control/hand_tracking.py`
2. Busca `self.lower_skin_1`, `self.upper_skin_1`, etc.
3. Modifica los valores según tu iluminación:

```python
# Prueba con valores más permisivos:
self.lower_skin_1 = np.array([0, 5, 30], dtype=np.uint8)    # Más sensible
self.upper_skin_1 = np.array([25, 200, 255], dtype=np.uint8) # Más amplio
```

4. Ejecuta `app_desktop_v2.py` modo CÁMARA
5. Si detecta mejor, ¡usa esos valores!

### Opción B: Usar HSV Trackbars (Interactivo)

Crear un script que te permita ajustar HSV en tiempo real con sliders:

```python
# Pseudocódigo
cv2.createTrackbar("H_Min", ...)
cv2.createTrackbar("H_Max", ...)
cv2.createTrackbar("S_Min", ...)
...
```

### Opción C: ML/AI (Futuro)

Usar una red neuronal entrenada (MediaPipe, YOLO, etc.) pero requiere GPU

---

## 📋 Checklist para Diagnóstico

Cuando pruebes la detección:

- [ ] ¿La mano está a 20-30 cm de la cámara?
- [ ] ¿Hay buena iluminación frontal?
- [ ] ¿El fondo es diferente al tono de tu piel?
- [ ] ¿La app dice "✓ Mano detectada"?
- [ ] ¿El contorno (verde) rodea tu mano?
- [ ] ¿El hull (azul) circunscribe la mano?
- [ ] ¿El contador de dedos es aproximado (1-5)?

Si responde "no" a alguno, ese es el problema a resolver.

---

## 🎯 Resumen

| Etapa | Función | Parámetro |
|-------|---------|-----------|
| **CLAHE** | Normalizar contraste | clipLimit=2.0 |
| **HSV Mask** | Detectar piel | 4 rangos combinados |
| **Morph** | Limpiar ruido | kernel 7x7, 2 cierres |
| **Contour** | Encontrar mano | Área máxima |
| **Filter** | Validar tamaño | 1%-90% del frame |
| **Approx** | Contar dedos | Ramer-Douglas-Peucker |
| **Solidity** | Forma | area/hull_area |
| **Gesture** | Clasificar | reglas heurísticas |
| **Servo Map** | Actuar | diccionario gesto→servo |

Cada etapa puede fallar → no detecta mano.
