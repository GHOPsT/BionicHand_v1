# 📝 CHANGELOG - BionicHand

Historial completo de cambios, features, y bugfixes.

---

## [1.0.0] - 2026-10-01 ✅ RELEASE

### 🎉 LANZAMIENTO OFICIAL - Etapa 1 (Cinemática)

#### ✨ Features Principales
- **3D Visualización Volumétrica**
  - Cilindros 3D para falanges (Surface3d)
  - Palma anatómica con 11 vértices (Mesh3d)
  - Articulaciones como esferas (navegación orbital)
  - Interactividad: rotación, zoom, pan

- **Control Interactivo en Tiempo Real**
  - 3 servos independientes (Índice, Grupo, Pulgar)
  - 4 posturas canónicas (Abierta, Puño, Pinza, Señalar)
  - Sliders suave 0-100%
  - Caching de cálculos para performance

- **Telemetría Completa**
  - PWM en microsegundos (1000-2000 µs)
  - Ángulos articulares (MCP, PIP)
  - 5 dedos con datos independientes
  - Actualización en tiempo real

- **Cinemática Precisa**
  - Forward kinematics 2D + flexión 3D
  - Acoplamiento 4-bar (PIP = 0.875 × MCP)
  - Pulgar con oposición 3D especial
  - Todos los límites verificados

- **Base de Datos CAD**
  - 5 dedos con medidas Fusion 360
  - Espaciado palmario verificado
  - Límites articulares realistas
  - Preciso al 0.01 mm

- **Web + Desktop**
  - **Streamlit Cloud**: URL en vivo (sin instalación)
  - **Local**: Python app con Matplotlib 3D
  - **Docker**: Containerizado para cualquier SO

#### 🔧 Implementación Técnica
- **Backend**: Python 3.13.2
- **Frontend Web**: Streamlit 1.28.0
- **Visualización 3D**: Plotly 7.1.0 (web), Matplotlib 3D (desktop)
- **Computación**: NumPy 1.24+
- **Arquitectura**: Modular (config, core, control, visualization)

#### 📚 Documentación
- USER_MANUAL.md - Guía de usuario
- INSTALLATION_GUIDE.md - Instalación local
- DEPLOYMENT_GUIDE.md - Streamlit Cloud
- API_DOCUMENTATION.md - Referencia técnica
- ARCHITECTURE.md - Diagrama de módulos
- VERIFICATION_REPORT.md - Auditoría completa

#### ✅ Verificación
- [x] Cinemática forward sin errores
- [x] Telemetría coherente
- [x] Visualización 3D funcional
- [x] Posturas canónicas correctas
- [x] CAD verificado contra Fusion 360
- [x] Tests pass (pytest)
- [x] Despliegue en Streamlit Cloud exitoso
- [x] Código limpio y documentado

#### 📊 Performance
- **Streamlit Cloud**: ~1-2s por update (latencia de red)
- **Local**: <100ms por update
- **Memoria**: ~150MB (venv)
- **Conectividad**: Streaming continuo sin lag

#### 🎯 URL en Vivo
https://bionichandv1-intnm9gomkciyuqzi5hvqf.streamlit.app/

---

## [0.9.0] - 2026-09-28 (Pre-release)

### 🔨 Trabajo en Curso
- [x] Visualización 3D con Surface3d (cilindros)
- [x] Palma volumétrica con Mesh3d
- [x] Cinemática 3D del pulgar
- [x] Acoplamiento 4-bar correctamente implementado
- [x] Telemetría PWM y ángulos
- [x] Optimizaciones de caching
- [ ] Interfaz pulida (en progreso)

---

## [0.8.5] - 2026-09-27

### 🐛 Bugfixes
- **Fix**: Reemplazar discos con cilindros Surface3d más visibles
- **Fix**: Z=0 ahora es Z=sin(flexión) para cinemática 3D real
- **Fix**: Palma agregada con tapas superiores e inferiores
- **Fix**: Líneas de dedos más gruesas (width=8)
- **Fix**: Telemetría compactada (3 columnas en lugar de 2)

### ⚡ Optimizaciones
- **Feature**: Caching de cálculos 3D con @st.cache_data
- **Feature**: Sliders con callbacks para updates más rápidos
- **Improvement**: Ratio columnas 3.5:1 (más espacio 3D)
- **Improvement**: Panel técnico debajo de la visualización

---

## [0.8.0] - 2026-09-26

### ✨ Features
- **Feature**: Postura Pinza (Index + Thumb opuesto)
- **Feature**: Telemetría en tiempo real (PWM + ángulos)
- **Feature**: 4 posturas canónicas funcionales
- **Feature**: Sliders para control fino de servos
- **Improvement**: Layout 2.5:1 (derecha para telemetría)

### 🐛 Bugfixes
- **Fix**: Import de Plotly en Streamlit (from plotly import graph_objects)
- **Fix**: __pycache__ eliminado de GitHub
- **Fix**: Cinemática de grupos (Medio, Anular, Meñique)

---

## [0.7.0] - 2026-09-25

### ✨ Features
- **Feature**: Visualización 3D básica con Scatter3d
- **Feature**: Posturas Abierta y Puño
- **Feature**: Botones de posturas rápidas
- **Feature**: Palma como punto diamante
- **Feature**: Panel derecho con controles

### 🐛 Bugfixes
- **Fix**: Imports relativos en core/hand.py
- **Fix**: Posiciones 3D corregidas (agregado Z)

---

## [0.6.0] - 2026-09-24

### 🌐 Streamlit Cloud
- **Feature**: App web desplegada en Streamlit Cloud
- **Feature**: URL pública sin instalación
- **Feature**: Auto-redeploy en push a GitHub

### 🐛 Bugfixes
- **Fix**: Dockerfile actualizado
- **Fix**: requirements.txt completo
- **Fix**: .streamlit/config.toml para Cloud

---

## [0.5.0] - 2026-09-20

### 🔧 Arquitectura Base
- **Feature**: Módulo core.hand (orquestador)
- **Feature**: Módulo core.finger (cinemática 2D)
- **Feature**: Módulo core.actuator (control de servo)
- **Feature**: Módulo core.joint (articulaciones)
- **Feature**: Módulo config.dimensions (base CAD)
- **Feature**: Módulo control.poses (posturas)

### ✅ Verificación
- [x] CAD dimensions verificadas (Fusion 360)
- [x] Forward kinematics testada
- [x] Acoplamiento 4-bar funcionando

---

## [0.4.0] - 2026-09-18

### 🎨 Visualización Desktop
- **Feature**: BionicHandVisualizer (Matplotlib 3D)
- **Feature**: Cilindros volumétricos Poly3DCollection
- **Feature**: Esferas articulares (plot_surface)
- **Feature**: Palma anatómica con 11 vértices

### ⚡ Performance
- **Improvement**: Renderizado en vivo
- **Improvement**: Rotación orbital con mouse

---

## [0.3.0] - 2026-09-16

### 🔨 Estructura Inicial
- **Feature**: Proyecto Python con estructura modular
- **Feature**: Virtual environment setup
- **Feature**: Git repository en GitHub
- **Feature**: Primeros tests con pytest

---

## [0.2.0] - 2026-09-15

### 📐 Cinemática
- **Feature**: Forward kinematics 2D base
- **Feature**: Límites articulares (0-80° MCP, 0-70° PIP)
- **Feature**: 5 dedos parametrizados

---

## [0.1.0] - 2026-09-14

### 🎯 Concepto Inicial
- **Idea**: Simulador 3D interactivo de mano prostética
- **Decisión**: Framework Streamlit + Plotly
- **Decisión**: Python como lenguaje base

---

## 📊 ROADMAP FUTURO

### Etapa 2: Simulación Dinámica (Plazo: 2026-12)
- [ ] Física 3D (gravedad, inercia)
- [ ] Dinámicas de contacto
- [ ] Simulación de fuerza
- [ ] Motor de física (Bullet3D o Pybullet)

### Etapa 3: Control EMG (Plazo: 2027-03)
- [ ] Interfaz de electromiografía
- [ ] Clasificación de gestos
- [ ] Control en tiempo real desde músculos
- [ ] Feedback háptico

### Etapa 4: Hardware Integration (Plazo: 2027-06)
- [ ] Comunicación con servo reales
- [ ] Firmware de microcontrolador
- [ ] Sensores de presión
- [ ] Calibración automática

---

## 🏆 HITOS ALCANZADOS

| Hito | Fecha | Estado |
|------|-------|--------|
| Concepto | 2026-09-14 | ✅ |
| Cinemática 2D | 2026-09-18 | ✅ |
| Visualización desktop | 2026-09-20 | ✅ |
| Arquitectura modular | 2026-09-24 | ✅ |
| Streamlit Cloud | 2026-09-26 | ✅ |
| **v1.0 Release** | **2026-10-01** | **✅** |

---

## 📈 ESTADÍSTICAS

### Código
- **Líneas de código**: ~2500 (Python)
- **Módulos**: 8 principales
- **Funciones**: 60+
- **Tests**: 10+
- **Documentación**: 5000+ líneas

### Repositorio
- **Commits**: 50+
- **Branches**: 2 (main, dev)
- **GitHub Stars**: ⭐ (invita al tuyo)
- **Tamaño**: ~5 MB (sin .git)

### Performance
- **Tiempo de carga local**: <1 segundo
- **Actualización 3D**: <100ms
- **Memoria RAM**: 150 MB
- **Latencia Streamlit Cloud**: 1-2 segundos

---

## 🙏 AGRADECIMIENTOS

- **Hardware ref**: HACKberry L (open-source prosthetic)
- **Framework**: Streamlit (por tooling web tan simple)
- **Visualización**: Plotly (3D interactivo de calidad)
- **CAD**: Fusion 360 (diseño de referencia)

---

## 📝 NOTA SOBRE VERSIONES

**Semantic Versioning**: MAJOR.MINOR.PATCH

- **MAJOR (1.x.x)**: Cambios fundamentales (Etapas)
- **MINOR (x.1.x)**: Nuevas features (manteniendo compatibilidad)
- **PATCH (x.x.1)**: Bugfixes (sin cambios de API)

**Versión Actual**: 1.0.0 (primera etapa, feature-complete)

---

**Última actualización**: 2026-10-01  
**Maintainer**: GHOPsT  
**Licencia**: MIT (pendiente)
