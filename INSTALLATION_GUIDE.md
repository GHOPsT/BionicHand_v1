# 🔧 Guía de Instalación - BionicHand

**Versión**: 1.0  
**Plataformas**: Windows | Mac | Linux  
**Última actualización**: 2026-10-01

---

## 📋 REQUISITOS PREVIOS

### Hardware
- Cualquier computadora moderna (2015+)
- RAM: ≥ 4GB (recomendado 8GB)
- Espacio disco: ≥ 500 MB

### Software
- **Python 3.13.2** (o superior, mínimo 3.11)
- **Git** (opcional, para clonar)
- **pip** (gestor de paquetes, viene con Python)

---

## 🚀 INSTALACIÓN RÁPIDA (5 minutos)

### Windows

#### Opción 1: Doble-click (RECOMENDADO)
```
1. Descarga el proyecto
2. Abre carpeta: Desktop\ManoBionica\bionic_hand\
3. Doble-click en: run_streamlit.bat
4. Se abrirá automáticamente en http://localhost:8501
```

#### Opción 2: Command Prompt
```powershell
# Abre Command Prompt o PowerShell
cd Desktop\ManoBionica\bionic_hand

# Crear entorno virtual
python -m venv venv

# Activar entorno
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
streamlit run app_streamlit.py
```

---

### Mac / Linux

#### Opción 1: Terminal (RECOMENDADO)
```bash
# Abre Terminal
cd ~/Desktop/ManoBionica/bionic_hand

# Crear entorno virtual
python3 -m venv venv

# Activar entorno
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
streamlit run app_streamlit.py
```

#### Opción 2: Bash Script
```bash
cd ~/Desktop/ManoBionica/bionic_hand
bash run_streamlit.sh
```

---

## ✅ VERIFICAR INSTALACIÓN

Después de ejecutar cualquier comando anterior, deberías ver:

```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

### En tu navegador:
1. Abre: **http://localhost:8501**
2. Deberías ver la visualización 3D con la mano
3. Prueba mover los sliders
4. Si todo funciona → **¡Instalación exitosa!** ✅

---

## 🐳 INSTALACIÓN VÍA DOCKER (Alternativa)

Si prefieres contenedores (recomendado para máquinas limpias):

```bash
# En la carpeta del proyecto
docker-compose up

# Espera a que se complete (2-3 minutos)
# Luego abre: http://localhost:8501
```

**Ventajas**:
- ✓ No afecta el sistema principal
- ✓ Todos los paquetes aislados
- ✓ Funciona igual en cualquier máquina

**Desventajas**:
- ✗ Requiere Docker (descarga 2GB)
- ✗ Ligeramente más lento

---

## 📦 DEPENDENCIAS (Lo que se instala)

El archivo `requirements.txt` instala:

| Paquete | Versión | Uso |
|---------|---------|-----|
| streamlit | 1.28.0+ | Interfaz web |
| plotly | 7.1.0+ | Visualización 3D |
| numpy | 1.24.0+ | Cálculos numéricos |
| matplotlib | 3.7.0+ | Visualización alternativa |
| pytest | 7.0.0+ | Testing |

**Tamaño total**: ~150 MB

---

## 🔄 ACTUALIZAR A VERSIÓN NUEVA

Cuando haya actualizaciones:

```bash
# Desactiva la versión anterior
# (Cierra Streamlit con Ctrl+C)

# Actualiza el código
git pull origin main

# Reinstala dependencias (por si hay nuevas)
pip install --upgrade -r requirements.txt

# Ejecuta de nuevo
streamlit run app_streamlit.py
```

---

## 🐛 TROUBLESHOOTING

### Error: "Python no encontrado"
```bash
# Windows: verifica que Python está en PATH
python --version

# Si no funciona, descarga desde:
# https://www.python.org/downloads/

# Asegúrate de marcar "Add Python to PATH" durante instalación
```

### Error: "No such file or directory"
```bash
# Verifica que estás en la carpeta correcta
pwd  # Mac/Linux
cd   # Windows

# Deberías ver archivos como:
# app_streamlit.py, requirements.txt, etc.

ls   # Mac/Linux
dir  # Windows
```

### Error: "Module not found"
```bash
# Activa el entorno virtual
# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate

# Verifica el prompt (debe mostrar "venv"):
# (venv) $ 

# Reinstala:
pip install -r requirements.txt
```

### Puerto 8501 ya en uso
```bash
# Si el puerto está ocupado:
streamlit run app_streamlit.py --server.port 8502

# O
streamlit run app_streamlit.py --server.port 8503
```

### App muy lenta
```bash
# Limpia cache
streamlit cache clear

# O elimina carpeta .streamlit
rm -rf .streamlit/

# O reinicia en local (no Cloud)
```

### Visualización 3D no funciona
```bash
# Actualiza navegador
# Presiona Ctrl+F5 (fuerza reload)

# Verifica que tienes WebGL:
# https://get.webgl.org/

# Si falla WebGL, cambia a navegador moderno
# (Chrome, Firefox, Edge - no IE)
```

---

## 🎯 CONFIGURACIÓN INICIAL (Opcional)

### Personalizar puerto
Edita `.streamlit/config.toml`:
```toml
[server]
port = 8501  # Cambia a 8502, 8503, etc.
```

### Cambiar modo oscuro/claro
Edita `.streamlit/config.toml`:
```toml
[theme]
base = "dark"  # O "light"
```

### Aumento de memoria para cálculos pesados
```bash
# En Mac/Linux:
export OMP_NUM_THREADS=4
streamlit run app_streamlit.py

# En Windows:
set OMP_NUM_THREADS=4
streamlit run app_streamlit.py
```

---

## 📚 VERIFICACIÓN DE ESTRUCTURA

Después de instalar, la carpeta debe tener:

```
bionic_hand/
├── app_streamlit.py          ← App web
├── main.py                   ← App desktop
├── requirements.txt          ← Dependencias
├── docker-compose.yml        ← Docker
├── run_streamlit.bat         ← Ejecutable Windows
├── run_streamlit.sh          ← Ejecutable Mac/Linux
├── config/
│   └── dimensions.py         ← Base de datos CAD
├── core/
│   ├── hand.py              ← Orquestador
│   ├── finger.py            ← Cinemática
│   ├── joint.py
│   └── actuator.py
├── control/
│   └── poses.py             ← Posturas
├── visualization/
│   └── visualizer.py        ← Renderizado Matplotlib
├── tests/
│   └── test_kinematics.py   ← Pruebas
└── .streamlit/
    └── config.toml          ← Configuración
```

Si falta algo, descarga nuevamente del repositorio.

---

## 🚨 PROBLEMAS AVANZADOS

### Virtual Environment corrompido
```bash
# Elimina y recreates
rm -rf venv  # Mac/Linux
rmdir /s venv  # Windows

python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

### Git clone no funciona
```bash
# Descarga manualmente:
# GitHub → Code → Download ZIP

# Extrae la carpeta
# Sigue pasos de instalación normal
```

### Importaciones fallas (ModuleNotFoundError)
```bash
# Verifica que Python importa correctamente
python -c "import sys; print(sys.path)"

# Reinicia terminal/IDE
# Reactiva entorno virtual
```

---

## ✅ CHECKLIST DE INSTALACIÓN

- [ ] Python 3.13+ instalado (`python --version`)
- [ ] Clonado/descargado proyecto
- [ ] Entorno virtual creado (`venv` carpeta existe)
- [ ] Entorno activado (prompt muestra `(venv)`)
- [ ] Dependencias instaladas (`pip list` muestra paquetes)
- [ ] App abierta (`streamlit run app_streamlit.py`)
- [ ] Navegador muestra visualización 3D
- [ ] Sliders se mueven suavemente
- [ ] Telemetría actualiza

Si todas están ✓ → **¡Listo para usar!**

---

## 🔗 SIGUIENTES PASOS

1. **Lee USER_MANUAL.md** - Aprende a usar la app
2. **Lee API_DOCUMENTATION.md** - Referencia técnica
3. **Lee DEPLOYMENT_GUIDE.md** - Despliega tu versión
4. **Personaliza** - Modifica código según necesites

---

## 📞 SOPORTE INSTALACIÓN

Si tienes problemas:

1. **Verifica Python**: `python --version` (debe ser 3.11+)
2. **Verifica pip**: `pip --version`
3. **Verifica entorno**: Prompt debe mostrar `(venv)`
4. **Reinicia terminal/IDE**
5. **Borra todo y comienza de nuevo** (cleanest solution)

---

**Versión**: 1.0  
**Última actualización**: 2026-10-01  
**Estado**: ✅ Verificado en Windows/Mac/Linux
