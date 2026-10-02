# 🚀 Guía de Despliegue - Streamlit Cloud

**Versión**: 1.0  
**Plataforma**: Streamlit Cloud  
**Última actualización**: 2026-10-01

---

## 🌐 VERSIÓN EN VIVO (YA DESPLEGADA)

**URL Actual**: https://bionichandv1-intnm9gomkciyuqzi5hvqf.streamlit.app/

Estado: ✅ **FUNCIONANDO**

---

## 📋 REQUISITOS PREVIOS

Antes de desplegar, necesitas:

1. **GitHub account** (gratis en github.com)
2. **Proyecto en GitHub** (repositorio público o privado)
3. **Streamlit account** (gratis en streamlit.io, login con GitHub)
4. **Archivos correctos** en repositorio:
   - `app_streamlit.py` ← **ARCHIVO PRINCIPAL**
   - `requirements.txt` ← Dependencias
   - `config/`, `core/`, `control/`, `visualization/` ← Carpetas necesarias

---

## 🔀 OPCIÓN 1: HACER FORK (RECOMENDADO PARA ESTUDIANTES)

### Paso 1: Fork el repositorio
```
1. Abre: https://github.com/GHOPsT/BionicHand_v1
2. Click en "Fork" (esquina superior derecha)
3. Espera a que se complete (5-10 segundos)
4. Ahora tienes tu propia copia
```

### Paso 2: Configurar Streamlit Cloud
```
1. Abre: https://share.streamlit.io/
2. Click en "New app"
3. Selecciona tu GitHub repo (BionicHand_v1)
4. Branch: main
5. Main file path: app_streamlit.py
6. Click en "Deploy"
```

### Paso 3: Esperar despliegue
```
- Estado: "Building..."
- Espera 2-5 minutos (primera vez es más lenta)
- Status cambia a "Running" (verde) ✅
```

### Paso 4: Tu app está en vivo
```
Streamlit genera una URL automática:
https://YOUR_USERNAME-bionichand-xxxxxxx.streamlit.app/

Comparte este link
```

---

## 🔀 OPCIÓN 2: CREAR REPOSITORIO NUEVO (Máximo Control)

### Paso 1: Crear repo en GitHub
```
1. Abre: https://github.com/new
2. Repository name: BionicHand_v1 (o tu nombre)
3. Description: "3D BionicHand Simulator - Etapa 1"
4. Public (para que sea visible)
5. Inicializa sin README (lo haremos nosotros)
6. Click "Create repository"
```

### Paso 2: Subir archivos locales
```bash
# En tu terminal (en la carpeta del proyecto):
git remote add origin https://github.com/TU_USER/BionicHand_v1.git
git branch -M main
git push -u origin main
```

### Paso 3: Verificar en GitHub
```
Visita tu repo: https://github.com/TU_USER/BionicHand_v1
Deberías ver todos los archivos correctamente
```

### Paso 4: Desplegar en Streamlit
```
1. Abre: https://share.streamlit.io/
2. Click "New app"
3. Conecta tu GitHub repo
4. Main file: app_streamlit.py
5. Click "Deploy"
```

---

## 📝 ARCHIVO REQUIREMENTS.TXT (Crítico)

Para que el despliegue funcione, `requirements.txt` debe tener:

```txt
streamlit==1.28.0
plotly==7.1.0
numpy==1.24.3
matplotlib==3.7.1
pytest==7.4.0
```

**Si falta alguno, Streamlit Cloud no podrá instalar dependencias** ❌

### Verificar requirements.txt
```bash
# En tu proyecto, ejecuta:
pip freeze > requirements.txt

# Revisa que tenga todas las librerías:
cat requirements.txt  # Mac/Linux
type requirements.txt # Windows
```

---

## 🔧 CONFIGURACIÓN DE STREAMLIT CLOUD

### archivo: `.streamlit/config.toml`

Debe existir este archivo con configuración para Cloud:

```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#1e222b"
secondaryBackgroundColor = "#2a303c"
textColor = "#e2e8f0"
font = "sans serif"

[client]
showErrorDetails = false
toolbarMode = "viewer"

[logger]
level = "error"

[server]
headless = true
port = 8501
enableXsrfProtection = true
```

**Este archivo YA está incluido en el proyecto.**

---

## 📊 MONITOREAR DESPLIEGUE

### Panel de Control Streamlit
```
1. Abre: https://share.streamlit.io/
2. Encuentra tu app en la lista
3. Click en el nombre
```

### Ver Logs en Vivo
```
En tu página de app:
1. Click en menú (≡) esquina arriba derecha
2. "Manage app"
3. Pestaña "Logs"
4. Verás errores en tiempo real
```

### Estadísticas
```
En "Manage app":
- Uptime (¿cuánto tiempo lleva funcionando?)
- CPU/Memory usage
- Usuarios activos
- Últimos deploys
```

---

## 🔄 ACTUALIZAR LA APP EN PRODUCCIÓN

### Método 1: Auto-Deploy (RECOMENDADO)
```
Si cambias el código en main branch:
- Streamlit detecta cambios automáticamente
- Redeploy en 1-2 minutos
- No requiere acción manual
```

### Método 2: Manual Deploy
```
1. Abre: https://share.streamlit.io/
2. Click en tu app
3. Click en "≡" → "Reboot app"
4. Espera a que termine
```

### Método 3: Cambiar Versión de Rama
```
1. Manage app → Settings
2. Advanced settings
3. Branch: cambia a otra rama (dev, testing, etc)
4. Redeploy
```

---

## 🚨 SOLUCIÓN DE PROBLEMAS EN CLOUD

### App no carga (Loading infinito)
```
1. Abre Manage app → Logs
2. Busca error en rojo
3. Problemas comunes:
   - Missing dependency en requirements.txt
   - Python version mismatch
   - Archivo app_streamlit.py corrupto
4. Solución: Fix el error, push a GitHub, Streamlit redeploy automático
```

### Error: "No module named 'X'"
```
Significa que falta en requirements.txt

Solución:
1. En local: pip install X
2. Actualiza: pip freeze > requirements.txt
3. Commit y push
4. Streamlit redeploy automático
```

### App muy lenta en Cloud
```
1. Es normal: Streamlit Cloud usa servidores compartidos
2. Recomendación: Descarga local (python app_streamlit.py)
3. O: Paga plan premium de Streamlit ($11/mes)
```

### Visualización 3D no funciona
```
1. Verifica navegador moderno (Chrome, Firefox, Edge)
2. Habilita WebGL: https://get.webgl.org/
3. En Safari: Puede no funcionar 100% WebGL
4. Si persiste: Reporta en GitHub Issues
```

### Conexión rechazada
```
1. Verifica URL es correcta
2. App puede estar en hibernación (gratis = auto-sleep)
3. Espera 20 segundos, recarga
4. Si persiste: Página de estado de Streamlit
```

---

## 🛡️ SEGURIDAD Y LÍMITES

### Plan Gratuito (Actual)
| Feature | Límite |
|---------|--------|
| Apps activas | 3 |
| Storage | 1 GB |
| CPU | Compartido |
| RAM | 1 GB |
| Conexiones simultáneas | Limitadas |
| Auto-sleep | Sí (después 7 días inactivo) |
| SSL/HTTPS | Automático ✅ |

### Cómo evitar problemas
```
1. No subas datos sensibles (contraseñas, API keys)
2. Usa variables de entorno para secrets:
   - Manage app → Secrets
3. No guardes datos permanentes (son efímeros)
4. Limpiar caché regularmente
```

---

## 🔑 VARIABLES DE ENTORNO (Secrets)

Si tu app necesita API keys o contraseñas:

### Paso 1: Crear Secret
```
1. Manage app → Settings → Secrets
2. Agregar:
   OPENAI_API_KEY = "sk-xxxxxxx"
   DATABASE_URL = "postgresql://..."
3. Save
```

### Paso 2: Usar en código
```python
import streamlit as st
import os

api_key = st.secrets["OPENAI_API_KEY"]
# O
api_key = os.getenv("OPENAI_API_KEY")
```

**Nota**: BionicHand NO requiere secrets (no usa APIs externas).

---

## 📈 ESCALAR A VERSIÓN DE PAGO

Si necesitas más poder:

### Plan Premium ($11/mes)
```
✓ CPU dedicado
✓ RAM 2-4 GB
✓ Sin auto-sleep
✓ Mejor uptime
✓ Prioridad soporte
```

### Cambiar plan
```
1. Abre: https://share.streamlit.io/
2. Click en tu app
3. "≡" → "Upgrade app"
4. Elige plan → Paga
```

---

## 🔗 COMPARTIR CON OTROS

### Opción 1: Link directo (más fácil)
```
Simplemente comparte:
https://bionichandv1-intnm9gomkciyuqzi5hvqf.streamlit.app/

No requiere login
```

### Opción 2: GitHub + Fork
```
Si quieren su propia versión:
1. Haz fork de tu repo
2. Comparte enlace del fork
3. Ellos despliegan su propia instancia
```

### Opción 3: QR Code
```
Generar QR de tu URL:
https://qr-code-generator.com/

Imprime y comparte
```

---

## 📚 DOCUMENTACIÓN ADICIONAL

- [Streamlit Docs](https://docs.streamlit.io/)
- [Streamlit Cloud Docs](https://docs.streamlit.io/streamlit-cloud/)
- [GitHub Actions](https://github.com/features/actions) (para CI/CD avanzado)
- [Docker Hub](https://hub.docker.com/) (alternativa a Streamlit Cloud)

---

## 🎯 PRÓXIMOS PASOS

1. **Tienes app en Cloud** ✅
2. **Quieres personalizar** → Ver `API_DOCUMENTATION.md`
3. **Quieres CI/CD automático** → Configura GitHub Actions
4. **Quieres dominio personalizado** → Compra en registrador (namecheap.com, etc) + DNS

---

## ✅ CHECKLIST DE DESPLIEGUE

- [ ] GitHub repo existe y es público
- [ ] Todos los archivos subidos (git push)
- [ ] `requirements.txt` completo y correcto
- [ ] `app_streamlit.py` es el archivo principal
- [ ] `.streamlit/config.toml` existe
- [ ] Streamlit Cloud account creado
- [ ] App desplegado sin errores
- [ ] URL funciona en navegador
- [ ] 3D visualization se carga
- [ ] Sliders responden rápido

Si todas están ✓ → **¡Despliegue exitoso!**

---

**Versión**: 1.0  
**Última actualización**: 2026-10-01  
**Estado**: ✅ Verificado
