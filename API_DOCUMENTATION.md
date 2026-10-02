# 📖 Documentación de API - BionicHand

**Versión**: 1.0  
**Módulos**: core, control, config  
**Última actualización**: 2026-10-01

---

## 📦 ARQUITECTURA DE MÓDULOS

```
bionic_hand/
├── config/
│   └── dimensions.py        ← Base de datos CAD
├── core/
│   ├── hand.py             ← MÓDULO PRINCIPAL (orquestador)
│   ├── finger.py           ← Cinemática de dedos
│   ├── joint.py            ← Articulaciones individuales
│   └── actuator.py         ← Control de servos
├── control/
│   └── poses.py            ← Posturas canónicas
└── visualization/
    └── visualizer.py       ← Renderizado 3D (Matplotlib)
```

---

## 🎯 PUNTO DE ENTRADA: `core.hand.BionicHand`

### Instanciar
```python
from core.hand import BionicHand

hand = BionicHand()
```

### Propiedades principales
```python
# Dedos individuales
hand.fingers  # Lista: [Pulgar, Índice, Medio, Anular, Meñique]

# Servos
hand.servo_index  # Servo 1 (Índice)
hand.servo_group  # Servo 2 (Grupo: Medio, Anular, Meñique)
hand.servo_thumb  # Servo 3 (Pulgar)

# Telemetría
hand.telemetry  # Dict con estado actual
```

---

## 🎮 MÉTODOS PRINCIPALES

### 1. `set_actuators(u_index, u_group, u_thumb)`

Establece comandos de los tres servos.

**Parámetros**:
- `u_index` (float): 0.0 a 1.0 → Servo 1 (Índice)
- `u_group` (float): 0.0 a 1.0 → Servo 2 (Grupo)
- `u_thumb` (float): 0.0 a 1.0 → Servo 3 (Pulgar)

**Ejemplo**:
```python
# Mano abierta
hand.set_actuators(0.0, 0.0, 0.0)

# Puño cerrado
hand.set_actuators(1.0, 1.0, 1.0)

# Postura mixta
hand.set_actuators(0.75, 0.0, 0.85)
```

**Nota**: Los valores se normalizan automáticamente al rango 0-1.

---

### 2. `get_telemetry()`

Obtiene estado completo de la mano en tiempo real.

**Retorno**: Dict con estructura:
```python
{
    "actuators": {
        "servo_index": {
            "pwm_us": 1500,        # Microsegundos (1000-2000)
            "command": 0.5,        # Valor normalizado (0-1)
            "percent": 50          # Porcentaje (0-100%)
        },
        "servo_group": {...},
        "servo_thumb": {...}
    },
    "joints": {
        "Pulgar": {
            "mcp_deg": 30.5,       # Ángulo MCP
            "pip_deg": 28.0        # Ángulo PIP (acoplado)
        },
        "Índice": {...},
        "Medio": {...},
        "Anular": {...},
        "Meñique": {...}
    }
}
```

**Ejemplo**:
```python
telemetry = hand.get_telemetry()

# Acceder datos
pwm_index = telemetry["actuators"]["servo_index"]["pwm_us"]
mcp_indice = telemetry["joints"]["Índice"]["mcp_deg"]

print(f"Servo Index PWM: {pwm_index} µs")
print(f"Índice MCP: {mcp_indice}°")
```

---

## 🖐️ CLASE: `core.finger.Finger`

Representa un dedo individual (base para cinemática).

### Acceso
```python
hand = BionicHand()
indice = hand.fingers[1]  # Índice
pulgar = hand.fingers[0]  # Pulgar
```

### Propiedades
```python
finger.name           # "Índice", "Pulgar", etc.
finger.mcp            # Objeto Joint (articulación MCP)
finger.pip            # Objeto Joint (articulación PIP)
```

### Métodos
```python
# Establecer flexión (0-1)
finger.set_flexion(0.5)

# Obtener posiciones 3D
positions = finger.get_positions()  # shape (3, 2): [base, nudillo, yema]
# Solo X,Y (sin Z). Para Z, usar visualizer.py

# Ángulos actuales
finger.mcp.angle  # Grados MCP
finger.pip.angle  # Grados PIP
```

---

## 🔩 CLASE: `core.actuator.Actuator`

Control de servo motor individual.

### Acceso
```python
servo_index = hand.servo_index
servo_group = hand.servo_group
servo_thumb = hand.servo_thumb
```

### Propiedades
```python
servo.command           # Valor normalizado (0-1)
servo.pwm_us           # Señal PWM en microsegundos (1000-2000)
servo.angle_deg        # Ángulo de posición (si es aplicable)
```

### Métodos
```python
# Establecer comando normalizado
servo.set_command(0.5)

# Convertir a PWM
pwm_value = servo.command_to_pwm(0.5)  # Retorna 1500

# Limites
print(servo.pwm_min)   # 1000
print(servo.pwm_max)   # 2000
```

---

## 🎭 POSTURAS: `control.poses`

Posturas canónicas predefinidas.

### Usar posturas
```python
from control.poses import Pose, POSE_ACTUATOR_MAP

# Ver posturas disponibles
print(Pose.OPEN_HAND)      # Mano abierta
print(Pose.POWER_GRASP)    # Puño
print(Pose.PINCH_GRIP)     # Pinza
print(Pose.POINTING)       # Señalar

# Aplicar postura
pose_data = POSE_ACTUATOR_MAP[Pose.POWER_GRASP]
hand.set_actuators(
    pose_data["index"],
    pose_data["group"],
    pose_data["thumb"]
)
```

### Valores de posturas
```python
POSE_ACTUATOR_MAP = {
    Pose.OPEN_HAND: {"index": 0.0, "group": 0.0, "thumb": 0.0},
    Pose.POWER_GRASP: {"index": 0.95, "group": 0.95, "thumb": 0.90},
    Pose.PINCH_GRIP: {"index": 0.75, "group": 0.0, "thumb": 0.85},
    Pose.POINTING: {"index": 0.0, "group": 1.0, "thumb": 0.90}
}
```

---

## 📐 CONFIGURACIÓN: `config.dimensions`

Base de datos CAD con todas las medidas.

### Acceso
```python
from config.dimensions import (
    FINGER_DIMENSIONS,
    PALM_SPACING,
    JOINT_LIMITS,
    COUPLING_RATIO_4BAR
)
```

### Dimensiones de dedos
```python
# Estructura
FINGER_DIMENSIONS = {
    "thumb": {
        "l1_proximal": 40.0,     # mm, falange proximal
        "l2_distal": 32.0,       # mm, falange distal
        "l_biela": 25.0          # mm, eslabón
    },
    "index": {
        "l1_proximal": 31.5,
        "l2_distal": 25.0,
        "l_biela": 20.0
    },
    # ... (medio, anular, meñique)
}

# Acceder
index_l1 = FINGER_DIMENSIONS["index"]["l1_proximal"]
print(f"Falange proximal Índice: {index_l1} mm")
```

### Espaciado de palma
```python
PALM_SPACING = {
    "index_to_middle": 20.771,  # mm
    "middle_to_ring": 20.625,
    "ring_to_pinky": 22.771
}

spacing = PALM_SPACING["index_to_middle"]
print(f"Espaciado Índice-Medio: {spacing} mm")
```

### Límites articulares
```python
JOINT_LIMITS = {
    "mcp_base_flexion": (0, 80),           # 0-80 grados
    "pip_middle_flexion": (0, 70),         # 0-70 grados
    "thumb_base_flexion": (0, 75),         # 0-75 grados (especial 3D)
    "thumb_pip_flexion": (0, 70)
}

mcp_max = JOINT_LIMITS["mcp_base_flexion"][1]
print(f"MCP máximo: {mcp_max}°")
```

### Acoplamiento 4-bar
```python
COUPLING_RATIO_4BAR = 0.875  # PIP = 0.875 × MCP

# Ejemplo:
mcp_angle = 80.0
pip_angle = 80.0 * 0.875  # = 70.0 grados
```

---

## 🎨 VISUALIZACIÓN: `visualization.visualizer.BionicHandVisualizer`

Renderizado 3D con Matplotlib (para desktop).

### Instanciar
```python
from visualization.visualizer import BionicHandVisualizer
from core.hand import BionicHand

hand = BionicHand()
visualizer = BionicHandVisualizer(hand)
visualizer.show()  # Abre ventana de Matplotlib
```

### Métodos
```python
# Actualizar visualización
visualizer.update_view()

# Cambiar ángulo de cámara
visualizer.ax_3d.view_init(elev=20, azim=-60)

# Guardar captura
visualizer.fig.savefig("hand_capture.png")
```

---

## 💻 EJEMPLO COMPLETO DE USO

```python
from core.hand import BionicHand
from control.poses import Pose, POSE_ACTUATOR_MAP
import time

# 1. Crear mano
hand = BionicHand()
print("✓ Mano creada")

# 2. Postura 1: Mano abierta
pose_open = POSE_ACTUATOR_MAP[Pose.OPEN_HAND]
hand.set_actuators(
    pose_open["index"],
    pose_open["group"],
    pose_open["thumb"]
)
print("✓ Postura: Mano abierta")

# 3. Leer telemetría
telemetry = hand.get_telemetry()
pwm_index = telemetry["actuators"]["servo_index"]["pwm_us"]
print(f"  PWM Índice: {pwm_index} µs")

# 4. Esperar 2 segundos
time.sleep(2)

# 5. Postura 2: Puño
pose_fist = POSE_ACTUATOR_MAP[Pose.POWER_GRASP]
hand.set_actuators(
    pose_fist["index"],
    pose_fist["group"],
    pose_fist["thumb"]
)
print("✓ Postura: Puño")

# 6. Mostrar ángulos
telemetry = hand.get_telemetry()
for finger_name, angles in telemetry["joints"].items():
    mcp = angles["mcp_deg"]
    pip = angles["pip_deg"]
    print(f"  {finger_name}: MCP={mcp:.1f}°, PIP={pip:.1f}°")

# 7. Control gradual
print("✓ Control gradual:")
for u in [0.0, 0.25, 0.5, 0.75, 1.0]:
    hand.set_actuators(u, u, u)  # Todos iguales
    telemetry = hand.get_telemetry()
    pwm = telemetry["actuators"]["servo_index"]["pwm_us"]
    print(f"  Comando {u*100:5.0f}% → PWM {pwm:5.0f} µs")
    time.sleep(0.5)

print("✓ Demo completado")
```

**Output esperado**:
```
✓ Mano creada
✓ Postura: Mano abierta
  PWM Índice: 1000 µs
✓ Postura: Puño
  Pulgar: MCP=67.5°, PIP=60.8°
  Índice: MCP=76.0°, PIP=66.5°
  Medio: MCP=76.0°, PIP=66.5°
  Anular: MCP=76.0°, PIP=66.5°
  Meñique: MCP=76.0°, PIP=66.5°
✓ Control gradual:
  Comando   0% → PWM  1000 µs
  Comando  25% → PWM  1250 µs
  Comando  50% → PWM  1500 µs
  Comando  75% → PWM  1750 µs
  Comando 100% → PWM  2000 µs
✓ Demo completado
```

---

## 🧪 TESTING

### Ejecutar tests
```bash
pytest tests/test_kinematics.py -v
```

### Estructura de tests
```python
# tests/test_kinematics.py
def test_finger_positions():
    """Verifica que las posiciones de dedos sean correctas"""
    hand = BionicHand()
    # ... assertions

def test_servo_pwm_range():
    """Verifica que PWM está en rango 1000-2000"""
    hand = BionicHand()
    # ... assertions
```

---

## 📊 RANGOS Y LÍMITES

### PWM (Servo Control)
| Valor | Significado |
|-------|------------|
| 1000 µs | Posición mínima (abierto) |
| 1500 µs | Centro (50%) |
| 2000 µs | Posición máxima (cerrado) |

### Ángulos Articulares
| Articulación | Mín | Máx | Rango | Notas |
|------------|-----|-----|-------|-------|
| MCP | 0° | 80° | 80° | Base de dedo |
| PIP | 0° | 70° | 70° | Nudillo |
| Pulgar | 0° | 75° | 75° | Flexión especial 3D |

### Acoplamiento
| Finger | Ratio PIP/MCP | Fórmula |
|--------|-----------------|---------|
| Índice | 0.875 | PIP = 0.875 × MCP |
| Medio | 0.875 | PIP = 0.875 × MCP |
| Anular | 0.875 | PIP = 0.875 × MCP |
| Meñique | 0.875 | PIP = 0.875 × MCP |
| Pulgar | 0.90 | PIP = 0.90 × MCP |

---

## ⚠️ CASOS ESPECIALES

### Pulgar
```python
# El pulgar tiene cinemática 3D especial (oposición)
# No es plano como los otros dedos

# Rango más pequeño:
mcp_max_thumb = JOINT_LIMITS["thumb_base_flexion"][1]  # 75° (no 80°)

# Acoplamiento diferente:
pip_thumb = command * 0.90 * pip_max  # 90%, no 87.5%
```

### Acoplamiento 4-Bar (Dedos 2-5)
```python
# El mecanismo de 4-barras acopla MCP ↔ PIP
# No se pueden controlar independientemente

# Si estableces:
hand.set_actuators(0.5, 0.0, 0.0)

# Automáticamente:
# - Índice MCP = 40° (0.5 × 80°)
# - Índice PIP = 35° (0.5 × 80° × 0.875)
```

---

## 🔗 FLUJO DE DATOS

```
set_actuators(u_idx, u_grp, u_thb)
    ↓
Servo.set_command()
    ↓
PWM = command * 1000 + 1000
    ↓
Finger.set_flexion(command)
    ↓
Joint.set_angle(command * angle_max)
    ↓
get_telemetry() retorna estado actualizado
```

---

## 📚 REFERENCIAS

- **Fusion 360 CAD**: Archivo de diseño (no incluido)
- **HACKberry Docs**: Especificaciones de hardware
- **Streamlit API**: https://docs.streamlit.io/
- **Plotly 3D**: https://plotly.com/python/3d-scatter/

---

## ✅ CHECKLIST DE INTEGRACIÓN

Si integras BionicHand en tu proyecto:

- [ ] Importa `from core.hand import BionicHand`
- [ ] Crea instancia `hand = BionicHand()`
- [ ] Llama `hand.set_actuators(u_idx, u_grp, u_thb)`
- [ ] Lee `hand.get_telemetry()` según necesites
- [ ] Para 3D, usa `visualization.visualizer.BionicHandVisualizer`
- [ ] Maneja excepciones de rango (0.0-1.0)

---

**Versión**: 1.0  
**Última actualización**: 2026-10-01  
**Estado**: ✅ Verificado
