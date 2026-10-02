# 🤖 BionicHand - Simulador 3D Interactivo (Etapa 1)

**Visualización cinemática de mano prostética biónica con control interactivo en tiempo real.**

## 📊 Características

✨ **Visualización 3D Realista**
- Representación volumétrica de falanges (cilindros + esferas)
- Articulaciones animadas (MCP, PIP)
- Palma anatómica con detalles 3D
- Navegación orbital con ratón

🎮 **Control Interactivo**
- 3 sliders de servomotores (Índice, Grupo, Pulgar)
- 4 posturas canónicas (Mano Abierta, Puño, Pinza, Señalar)
- Ajustes de radio de falanges (2.0 a 7.0 mm)
- Control de transparencia (0.3 a 1.0)

📡 **Telemetría en Vivo**
- Señales PWM de servos (1000-2000 µs)
- Ángulos de articulaciones (MCP/PIP en grados)
- Instrucciones de navegación 3D
- Leyenda técnica (MCP, PIP, µs)

🔧 **Base de Datos CAD Verificada**
- Medidas exactas de Fusion 360
- 5 dedos con eslabones precisos
- Espaciado palmario verificado
- Límites articulares realistas

---

## 🚀 Inicio Rápido

### Windows
```bash
# Doble-click en:
start.bat
```

### Mac / Linux
```bash
# Ejecutar en Terminal desde esta carpeta:
bash start.sh
```

### Alternativa Manual
```bash
docker-compose up
```

---

## 📋 Requisitos del Sistema

- **Docker Desktop** instalado
  - Mac: https://www.docker.com/products/docker-desktop
  - Windows: https://www.docker.com/products/docker-desktop
  - Linux: `sudo apt install docker.io docker-compose`

- Espacio en disco: ~2.5 GB (primera compilación)
- RAM: 2 GB mínimo
- Pantalla: 1920x1080 recomendado

---

## 📁 Estructura del Proyecto

```
bionic_hand/
├── main.py                 # Punto de entrada
├── requirements.txt        # Dependencias Python
├── Dockerfile             # Configuración Docker
├── docker-compose.yml     # Orquestación
├── start.sh               # Script inicio Mac/Linux
├── start.bat              # Script inicio Windows
├── DEPLOYMENT_GUIDE.md    # Guía para clientes
│
├── config/
│   └── dimensions.py      # Datos CAD (eslabones, límites, espaciado)
│
├── core/
│   ├── hand.py            # Modelo de mano (5 dedos)
│   ├── finger.py          # Cinemática de dedo 2-DOF
│   ├── joint.py           # Modelo articular
│   └── actuator.py        # Modelo de servomotor
│
├── control/
│   └── poses.py           # Posturas canónicas
│
├── visualization/
│   └── visualizer.py      # Motor 3D con Matplotlib
│
└── tests/
    └── test_kinematics.py # Tests unitarios
```

---

## 🎮 Cómo Usar

1. **Ejecutar** el script (`start.bat` o `start.sh`)
2. **Esperar** a que se abra la ventana (primera vez: 1-2 min)
3. **Interactuar**:
   - 🖱️ **Ratón**: Rotar vista 3D (clic + arrastrar)
   - 🎚️ **Sliders arriba**: Control de servos
   - 🔘 **Botones medio**: Posturas predefinidas
   - ⚙️ **Sliders abajo**: Radio & transparencia

---

## 📊 Especificaciones Técnicas

### Kinematics
- **Dedos 1-4**: 2-DOF (MCP: 0-80°, PIP: 0-70°)
- **Pulgar**: 2-DOF con oposición 3D (Base: 0-75°, PIP: 0-65°)
- **Acoplamiento 4-bar**: Ratio 0.875 (PIP/MCP)

### Actuación
- **3 Servomotores**: PWM 1000-2000 µs
- **Servo 1**: Índice (transmisión directa)
- **Servo 2**: Grupo (Medio, Anular, Meñique)
- **Servo 3**: Pulgar (oposición 3D)

### Medidas
- Todos los valores en mm (precisión de Fusion 360)
- Longitud total: 76-81 mm por dedo
- Peso simulado: 155g

---

## 🔧 Configuración Avanzada

### Variables de Entorno
```bash
# Dentro del contenedor:
export PYTHONPATH=/app
export PYTHONUNBUFFERED=1
```

### Modificar Parámetros Visuales
Editar `visualization/visualizer.py`:
```python
self.cylinder_radius_proximal = 4.5  # mm
self.cylinder_radius_distal = 4.0    # mm
self.alpha_cylinders = 0.88           # transparencia
```

### Actualizar Medidas CAD
Editar `config/dimensions.py`:
```python
FINGER_DIMENSIONS["index"] = {
    "l1_proximal": 36.54,
    "l2_distal": 40.96,
    "l_biela": 29.03,
    "total_length": 77.50
}
```
---

## 📈 Roadmap (Etapas Futuras)

- **Etapa 2**: Simulación dinámica (CoppeliaSim)
- **Etapa 3**: Feedback electromiográfico (EMG)

---

## 👥 Equipo Técnico

**Desarrollado por**: GHOPsT
**Versión**: 1.0  
**Última actualización**: 2026-10-01  

---

**¡Disfruta del simulador! 🚀**
