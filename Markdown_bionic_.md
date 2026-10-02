# PROYECTO BIONICHAND — ESPECIFICACIÓN TÉCNICA Y CÓDIGO FUENTE (ETAPA 1)

## 1. DESCRIPCIÓN DEL PROYECTO
El proyecto **BionicHand** consiste en el desarrollo progresivo de un prototipo computacional de prótesis de mano biónica subactuada (basada en el diseño mecánico de la plataforma HACKberry L). 
La metodología de desarrollo se divide en 3 etapas secuenciales:
- **Etapa 1 (Actual):** Modelado funcional, cinemática directa y simulación 3D interactiva en Python.
- **Etapa 2 (Siguiente):** Simulación dinámica en CoppeliaSim vinculada vía ZeroMQ API (`zmqRemoteApi`).
- **Etapa 3 (Final):** Decodificación de bioseñales sEMG (procesamiento digital, filtros Butterworth/Notch, extracción de características RMS/MAV/WL/ZC) y clasificación de intenciones motoras mediante Random Forest.

---

## 2. PARÁMETROS CINEMÁTICOS MEDIDOS DEL CAD (GROUND TRUTH)
Todos los valores corresponden a mediciones directas de centro a centro de pasador tomadas en Autodesk Fusion:

### 2.1 Eslabones de los Dedos (mm)
- **Pulgar (`L-T:1`):** $L_1 = 29.92\text{ mm}$, $L_2 = 49.14\text{ mm}$. Longitud total = $79.06\text{ mm}$. Actuador directo: Servomotor `ASV-15MG`.
- **Índice (`L-I:1`):** $L_1 = 36.54\text{ mm}$, $L_2 = 40.96\text{ mm}$, $L_{\text{biela}} = 29.03\text{ mm}$. Longitud total = $77.50\text{ mm}$. Actuador: Servo 1 (Reducción engranajes 24T / 14T).
- **Medio (`L-O:1`):** $L_1 = 41.12\text{ mm}$, $L_2 = 40.40\text{ mm}$, $L_{\text{biela}} = 28.35\text{ mm}$. Longitud total = $81.52\text{ mm}$. Actuador: Servo 2 (Barra común).
- **Anular (`L-O:2`):** $L_1 = 41.31\text{ mm}$, $L_2 = 40.40\text{ mm}$, $L_{\text{biela}} = 28.34\text{ mm}$. Longitud total = $81.71\text{ mm}$. Actuador: Servo 2 (Barra común).
- **Meñique (`L-O:3`):** $L_1 = 36.41\text{ mm}$, $L_2 = 40.40\text{ mm}$, $L_{\text{biela}} = 28.34\text{ mm}$. Longitud total = $76.81\text{ mm}$. Actuador: Servo 2 (Barra común).

### 2.2 Relación de Transmisión y Límites Articulares
- **Reducción del Índice:** Rueda motriz $N_1 = 24\text{ dientes}$, Sector conducido $N_2 = 14\text{ dientes}$ ($R = 1.714$).
- **Límites de giro físico:**
  - Articulación base metacarpofalángica (MCP): $0^\circ$ a $80^\circ$.
  - Articulación media interfalángica proximal (PIP): $0^\circ$ a $70^\circ$.
  - Articulación base del pulgar: $0^\circ$ a $75^\circ$.
  - Articulación nudillo del pulgar: $0^\circ$ a $65^\circ$.
  - Acoplamiento del mecanismo de 4 barras: $k \approx \frac{70^\circ}{80^\circ} = 0.875$.

### 2.3 Espaciado de la Palma (Pitch entre bases)
- Índice $\rightarrow$ Medio: $20.77\text{ mm}$
- Medio $\rightarrow$ Anular: $20.65\text{ mm}$
- Anular $\rightarrow$ Meñique: $21.46\text{ mm}$
- Índice $\rightarrow$ Pulgar: $40.24\text{ mm}$ (3D directo) / $37.63\text{ mm}$ (proyectado)

---

## 3. ESTRUCTURA DE ARCHIVOS DEL REPOSITORIO
```text
bionic_hand/
│
├── config/
│   ├── __init__.py
│   └── dimensions.py
│
├── core/
│   ├── __init__.py
│   ├── joint.py
│   ├── finger.py
│   ├── actuator.py
│   └── hand.py
│
├── control/
│   ├── __init__.py
│   ├── interfaces.py
│   ├── manual_provider.py
│   ├── poses.py
│   └── trajectory.py
│
├── visualization/
│   ├── __init__.py
│   └── visualizer.py
│
├── tests/
│   ├── __init__.py
│   └── test_kinematics.py
│
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── main.py