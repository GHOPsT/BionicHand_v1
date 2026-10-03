# 🖥️ DESKTOP_GUIDE - BionicHand Desktop Application

Guía completa para instalar, configurar y usar la aplicación desktop de BionicHand con **rastreo de mano en tiempo real por cámara**.

---

## 📋 CONTENIDO

1. [Características Principales](#-características-principales)
2. [Requisitos del Sistema](#-requisitos-del-sistema)
3. [Instalación Desktop](#-instalación-desktop)
4. [Creación de Ejecutable .exe](#-creación-de-ejecutable-exe)
5. [Uso de la Aplicación](#-uso-de-la-aplicación)
6. [Modos de Control](#-modos-de-control)
7. [Troubleshooting](#-troubleshooting)
8. [Arquitectura Técnica](#-arquitectura-técnica)

---

## ✨ Características Principales

### 🎬 Captura de Cámara en Vivo
- **MediaPipe Hand Tracking**: Detección de mano con 21 landmarks (articulaciones de dedos)
- **Velocidad**: 30 FPS en tiempo real
- **Precisión**: Acelerado por GPU (si disponible)
- **Robustez**: Funciona en iluminación variable

### 🖐️ Rastreo de Dedos Individual
- Cada dedo se mapea automáticamente a ángulos de articulación
- Flexión MCP (nudillo): 0-80°
- Flexión PIP (articulación media): 0-70°
- Acoplamiento 4-bar automático

### 🎮 3 Modos de Control

| Modo | Descripción | Caso de Uso |
|------|-------------|-----------|
| **SLIDERS** | Control manual con deslizadores | Testing, calibración |
| **CÁMARA** | Tu mano real controla la mano simulada | Control en tiempo real |
| **GESTOS** | Reconocimiento de 5 gestos predefinidos | Control rápido (puño, pinza, etc.) |

### 🎨 Interfaz Dual Panel
- **Panel Izquierdo**: Video en vivo de tu mano capturada por cámara
- **Panel Derecho**: Visualización 3D de la mano biónica con Matplotlib
- **Actualización en tiempo real**: Sincronización perfecta

### 📊 Telemetría Completa
- Valores PWM en microsegundos (1000-2000 µs)
- Ángulos de articulaciones
- Estado de detección de mano
- Gestos reconocidos

---

## 💻 Requisitos del Sistema

### Mínimos
- **OS**: Windows 7+, macOS 10.13+, Linux (Ubuntu 18.04+)
- **CPU**: Dual-core (recomendado 4+ cores)
- **RAM**: 2 GB mínimo (4 GB recomendado)
- **Cámara**: Cualquier webcam USB (resolución mínima 640×480)

### Recomendado
- **OS**: Windows 10+, macOS 11+, Ubuntu 20.04+
- **CPU**: 4+ cores, preferentemente Intel i5 o superior
- **RAM**: 8 GB
- **Cámara**: 1080p o superior
- **GPU**: NVIDIA (CUDA) o AMD (ROCm) para aceleración

### Software
- **Python**: 3.11+ (ya debería estar instalado si ejecutas desde web)
- **pip**: Gestor de paquetes de Python

---

## 🔧 Instalación Desktop

### Opción 1: Desde Python (Recomendado para Development)

#### Windows (PowerShell)
```powershell
# 1. Navega al directorio del proyecto
cd C:\Users\TuUsuario\Desktop\ManoBionica\bionic_hand

# 2. Activa el virtual environment (si existe)
.\.venv\Scripts\Activate.ps1

# 3. Instala dependencias de desktop
pip install -r requirements_desktop.txt

# 4. Ejecuta la aplicación
python app_desktop.py
```

#### macOS / Linux (Terminal)
```bash
# 1. Navega al directorio del proyecto
cd ~/Desktop/ManoBionica/bionic_hand

# 2. Activa el virtual environment (si existe)
source .venv/bin/activate

# 3. Instala dependencias de desktop
pip install -r requirements_desktop.txt

# 4. Ejecuta la aplicación
python app_desktop.py
```

### Opción 2: Descarga Rápida desde GitHub

```bash
# Clonar repositorio
git clone https://github.com/GHOPsT/BionicHand_v1.git
cd BionicHand_v1

# Instalar dependencias
pip install -r requirements_desktop.txt

# Ejecutar
python app_desktop.py
```

---

## 📦 Creación de Ejecutable .exe

### Paso 1: Instalar PyInstaller (si no lo tienes)
```powershell
pip install pyinstaller
```

### Paso 2: Ejecutar Script de Compilación

#### Windows
```powershell
# Ejecuta el script de build
.\build_exe.bat
```

#### macOS / Linux
```bash
# Dar permisos de ejecución
chmod +x build_exe.sh

# Ejecutar
./build_exe.sh
```

### Paso 3: Obtener el Ejecutable
Después de ~3-5 minutos de compilación:

- **Windows**: `dist/BionicHand.exe`
- **macOS**: `dist/BionicHand.app`
- **Linux**: `dist/BionicHand`

### Distribución

El ejecutable es **portátil y autocontendido**. Puedes:
- Copiar `dist/BionicHand.exe` a cualquier ubicación
- Ejecutar en otras máquinas Windows sin necesidad de Python
- Crear acceso directo en el Escritorio
- Distribuir a otros usuarios

---

## 🎮 Uso de la Aplicación

### Interfaz Principal

```
┌─────────────────────────────────────────────────────────────┐
│  BionicHand Desktop - Control por Cámara                   │
├────────────────────┬────────────────────────────────────────┤
│                    │                                        │
│   CÁMARA EN VIVO   │  [Modo: CÁMARA ▼]                      │
│   (Tu mano)        │                                        │
│                    │  ┌─ MANO 3D ─────────────────────┐     │
│                    │  │                                │     │
│   [Video stream]   │  │    [Visualización 3D]         │     │
│                    │  │                                │     │
│   ✓ Mano detectada │  │    (Se mueve con tu mano)     │     │
│   Gesto: NEUTRAL   │  └────────────────────────────────┘     │
│                    │                                        │
│                    │  Controles:                           │
│                    │  - Índice: 45%     [=========>  ]     │
│                    │  - Grupo:  30%     [=====>     ]       │
│                    │  - Pulgar: 50%     [===========>]      │
│                    │                                        │
│                    │  [ABIERTA] [PUÑO] [PINZA] [SEÑALAR]  │
│                    │                                        │
│                    │  Telemetría:                          │
│                    │  PWM Índice: 1450 µs                  │
│                    │  PWM Grupo: 1300 µs                   │
│                    │  Gesto: PINCH                         │
└────────────────────┴────────────────────────────────────────┘
```

### Primeros Pasos

1. **Abre la aplicación**: Ejecuta `BionicHand.exe` o `python app_desktop.py`
2. **Concede permisos de cámara**: Windows/macOS te pedirá permiso
3. **Apunta la cámara a tu mano**: La detección debe mostrar "Mano detectada" en verde
4. **Selecciona modo**: Por defecto está en "SLIDERS"
5. **Cambia a modo CÁMARA**: Elige "CÁMARA" en el dropdown
6. **Mueve tu mano**: La mano 3D debe seguir tus movimientos

---

## 🎯 Modos de Control

### Modo 1: SLIDERS (Manual)

**Uso**: Calibración, testing, demostración

- Usa los 3 deslizadores (Índice, Grupo, Pulgar)
- Cada slider controla la flexión de 0% (extendido) a 100% (cerrado)
- Los botones "ABIERTA", "PUÑO", etc. predefinen posiciones

```
Índice:  [0%  =========> 100%]  → Movimiento dedo índice
Grupo:   [0%  =========> 100%]  → Movimiento dedos 2-4
Pulgar:  [0%  =========> 100%]  → Movimiento pulgar
```

### Modo 2: CÁMARA (Rastreo de Dedos)

**Uso**: Control natural en tiempo real

**Cómo funciona**:
1. MediaPipe detecta 21 landmarks en tu mano
2. Se calculan ángulos MCP y PIP para cada dedo
3. Los ángulos se mapean a valores 0-1 para servomotores
4. La mano 3D sigue tus movimientos

**Ventajas**:
- Control intuitivo (tu mano controla la mano biónica)
- Múltiples dedos independientes
- Seguimiento suave y en tiempo real
- Sin necesidad de calibración

**Limitaciones**:
- Requiere iluminación razonable
- Mejor con fondo limpio (no blanco puro)
- Distancia óptima: 30-80 cm de la cámara

### Modo 3: GESTOS (Predefinidos)

**Uso**: Control rápido con 5 gestos

**Gestos reconocidos**:

| Gesto | Acción | Descripción |
|-------|--------|-------------|
| **FIST** | PUÑO | Todos los dedos cerrados → Postura PUÑO |
| **OPEN_PALM** | PALMA | Todos los dedos extendidos → Postura ABIERTA |
| **PINCH** | PINZA | Índice + Pulgar juntos → Postura PINZA |
| **POINTING** | SEÑALAR | Solo índice extendido → Postura SEÑALAR |
| **VICTORY** | VICTORIA | Índice + Medio extendidos | (En desarrollo) |

---

## 🎬 Ejemplos de Uso

### Ejemplo 1: Apertura y Cierre Simple

```
1. Modo: CÁMARA
2. Abre tu mano (extiende dedos)
   → La mano 3D se abre
3. Cierra tu mano (flexiona dedos)
   → La mano 3D se cierra
```

### Ejemplo 2: Pinza Selectiva

```
1. Modo: GESTOS
2. Haz pinza con índice y pulgar
   → Sistema reconoce "PINCH"
   → Mano 3D adopta postura PINZA
```

### Ejemplo 3: Calibración de Servomotor

```
1. Modo: SLIDERS
2. Ajusta manualmente cada slider
3. Observa en tiempo real cómo responde
4. Anota valores PWM en telemetría
5. Usa esos valores para configuración hardware
```

---

## 🔧 Troubleshooting

### ❌ "Mano no detectada"

**Síntomas**: Etiqueta naranja "Mano no detectada"

**Causas y soluciones**:

1. **Iluminación insuficiente**
   - Solución: Acerca más luz (lámpara, ventana)
   - Evita sombras fuertes en la mano

2. **Fondo muy blanco o muy oscuro**
   - Solución: Cambia el fondo a colores neutrales
   - MediaPipe funciona mejor sobre fondos mixtos

3. **Distancia incorrecta**
   - Solución: Coloca mano entre 30-80 cm de cámara
   - Evita muy cerca (<20 cm) o muy lejos (>150 cm)

4. **Cámara invertida o girada**
   - Solución: Comprueba que el video se ve normal
   - Rota la cámara si es necesario

### ❌ "Aplicación lenta / 5-10 FPS"

**Síntomas**: Lag notable, movimientos entrecortados

**Causas y soluciones**:

1. **Computadora lenta**
   - Cierra otras aplicaciones (Chrome, etc.)
   - Reduce calidad de cámara (baja resolución en ajustes)

2. **Cámara USB defectuosa**
   - Prueba con otra cámara
   - Cambia puerto USB (preferentemente USB 3.0)

3. **MediaPipe compilando**
   - Espera 10-20 segundos al iniciar (primera ejecución)
   - Las ejecuciones siguientes serán más rápidas

### ❌ "Error: ModuleNotFoundError: mediapipe"

**Síntomas**: Crash al iniciar con error de módulo

**Solución**:
```powershell
pip install --upgrade mediapipe opencv-python PyQt5
```

### ❌ "Error: Cámara no encontrada"

**Síntomas**: "Camera initialization failed"

**Soluciones**:

1. Comprueba permisos:
   - Windows: Ajustes → Privacidad → Cámara (verifica que la app tenga permiso)
   - macOS: Ajustes del Sistema → Privacidad → Cámara

2. Prueba con otra cámara:
   ```python
   # Edita app_desktop.py, línea ~350
   # Cambia camera_id de 0 a 1, 2, etc.
   self.camera_thread = HandTrackingThread(camera_id=1)  # 0=default, 1=2da cámara
   ```

3. Desconecta/reconecta la cámara USB

### ❌ "Error al empaquetar con PyInstaller"

**Síntomas**: Error en `build_exe.bat`

**Soluciones**:

1. Verifica PyInstaller:
   ```powershell
   pip install --upgrade pyinstaller
   ```

2. Elimina builds anteriores:
   ```powershell
   Remove-Item -Recurse dist, build
   Remove-Item BionicHand.spec
   ```

3. Vuelve a ejecutar `build_exe.bat`

---

## 🏗️ Arquitectura Técnica

### Módulos Principales

#### `control/hand_tracking.py`
- **Clase**: `HandTracker`
- **Función**: Detecta mano con MediaPipe, extrae landmarks, calcula ángulos
- **Métodos key**:
  - `process_frame()`: Procesa video en tiempo real
  - `get_finger_angles()`: Convierte landmarks a ángulos (°)
  - `detect_gesture()`: Reconoce 5 gestos predefinidos
  - `landmarks_to_servo_values()`: Mapea a valores 0-1 para servos

#### `app_desktop.py`
- **Clase**: `BionicHandDesktopApp` (PyQt5 MainWindow)
- **Función**: Interfaz gráfica principal con 2 paneles
- **Widgets**:
  - `CameraFrame`: Panel de video en vivo
  - `Hand3DCanvas`: Matplotlib 3D interactivo
  - Sliders, botones, telemetría

#### `core/hand.py`
- **Reutilizado**: Mismo modelo cinemático que web
- **Función**: Orquesta movimiento de dedos
- **Métodos**: `set_actuators()`, `get_telemetry()`

### Flujo de Datos

```
┌─────────────┐
│  CÁMARA USB │
└──────┬──────┘
       │ (640×480, 30 FPS)
       ↓
┌──────────────────────────┐
│  HandTrackingThread      │
│  (Thread en background)  │
└──────────────────────────┘
       │ process_frame()
       ↓
┌──────────────────────────┐
│  MediaPipe Hand Detector │
│  (21 landmarks)          │
└──────────────────────────┘
       │ landmarks
       ↓
┌──────────────────────────┐
│  HandTracker             │
│  - get_finger_angles()   │
│  - detect_gesture()      │
│  - landmarks_to_servo    │
└──────────────────────────┘
       │ servo_values (0-1)
       ↓
┌──────────────────────────┐
│  BionicHand Model        │
│  set_actuators()         │
└──────────────────────────┘
       │ ángulos
       ↓
┌──────────────────────────┐
│  Hand3DCanvas            │
│  (Matplotlib 3D)         │
│  Renderizado en tiempo   │
│  real                    │
└──────────────────────────┘
```

### Dependencias

| Librería | Versión | Propósito |
|----------|---------|-----------|
| **mediapipe** | 0.10+ | Detección de mano |
| **opencv-python** | 4.8+ | Captura de cámara |
| **PyQt5** | 5.15+ | Interfaz gráfica |
| **matplotlib** | 3.7+ | Visualización 3D |
| **numpy** | 1.24+ | Cálculos numéricos |
| **pyinstaller** | 5.13+ | Empaquetamiento a .exe |

### Performance

| Métrica | Valor Típico | Máximo |
|---------|-------------|--------|
| FPS | 25-30 | 60 (GPU) |
| Latencia | 50-100 ms | 200 ms |
| CPU | 15-25% | 60% (4 cores) |
| RAM | 200-300 MB | 500 MB |
| Cámara | 30 FPS | - |

---

## 📝 Notas y Tips

### 💡 Tips para Mejor Rastreo

1. **Iluminación**: Natural o LED, evita luces fluorescentes parpadeantes
2. **Fondo**: Colores neutros, evita fondos blancos puros
3. **Distancia**: Mantén mano entre 30-80 cm
4. **Ángulo**: Cámara de frente, no de lado
5. **Limpieza**: Limpia lente de cámara con paño suave

### 🔧 Personalización

Para cambiar límites de confianza de MediaPipe:
```python
# En control/hand_tracking.py, línea ~30
HandTracker(max_hands=1, confidence=0.7)  # 0.7 = 70% confianza
# Reduce a 0.5 para ambientes oscuros
# Aumenta a 0.9 para máxima precisión
```

Para cambiar ID de cámara:
```python
# En app_desktop.py, línea ~350
self.camera_thread = HandTrackingThread(camera_id=0)
# 0 = cámara principal
# 1 = 2da cámara USB (si existe)
```

### 🐛 Debugging

Modo verbose (imprime logs):
```bash
python app_desktop.py --verbose
```

Grabar video de sesión:
```bash
python app_desktop.py --record session.mp4
```

---

## 📞 Soporte

Si encontras problemas:

1. **Revisa la sección Troubleshooting** más arriba
2. **Verifica versiones de dependencias**:
   ```powershell
   pip list | grep -E "mediapipe|opencv|PyQt5|matplotlib"
   ```

3. **Reinstala todo limpio**:
   ```powershell
   pip uninstall -y mediapipe opencv-python PyQt5
   pip install -r requirements_desktop.txt
   ```

4. **Abre un issue** en GitHub con:
   - Sistema operativo
   - Versión de Python (`python --version`)
   - Mensaje de error completo
   - Captura de pantalla

---

## 🚀 Próximas Características

- [ ] Grabación de sesiones de control
- [ ] Calibración automática de cámara
- [ ] Modo Multi-usuario (mano izquierda + derecha)
- [ ] Feedback háptico (vibración)
- [ ] Integración con Arduino/RaspberryPi
- [ ] Exportar/importar secuencias de movimiento

---

**Versión**: 1.1.0 Desktop  
**Última actualización**: 2026-10-03  
**Licencia**: MIT  
**Autor**: GHOPsT
