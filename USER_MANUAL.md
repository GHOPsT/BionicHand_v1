# 👤 Manual de Usuario - BionicHand Simulador 3D

**Versión**: 1.0 (Etapa 1 - Cinemática)  
**Fecha**: 2026-10-01  
**Estado**: ✅ Completamente Funcional

---

## 🌐 Acceso Rápido

### Online (Recomendado para primera visualización)
**URL**: https://bionichandv1-intnm9gomkciyuqzi5hvqf.streamlit.app/

No requiere instalación. Abre directamente en tu navegador.

### Local (Después de instalar)
```bash
python app_streamlit.py
# O
streamlit run app_streamlit.py
```

---

## 🎮 INTERFAZ DE USUARIO

### 1️⃣ Visualización 3D (Izquierda - 77% de pantalla)

#### 📐 Navegación
- **Rotar**: Haz clic y arrastra con el ratón
- **Zoom**: Rueda del ratón hacia arriba/abajo
- **Acercar/Alejar**: Doble clic para reset
- **Botones Plotly** (esquina superior derecha):
  - 🏠 Home: vuelve a la vista inicial
  - 📷 Cámara: descarga captura PNG
  - ⬅️➡️⬆️⬇️: Herramientas de rotación

#### 🎨 Elementos Visuales
- **Cilindros de color** = Falanges (proximal + distal)
- **Esferas articulares** = Nudillos (MCP, PIP)
- **Palma beige** = Estructura ósea de la mano
- **Líneas de color** = Esqueleto (referencia)

#### 🎯 Información en hover
- Mueve el ratón sobre elementos para ver:
  - Nombre del dedo (ej: "Índice")
  - Ángulo MCP
  - Ángulo PIP

---

### 2️⃣ Panel de Control (Derecha - 23% de pantalla)

#### 🖐️ POSTURAS RÁPIDAS (4 Botones)
Click en cualquier botón = la mano adopta esa posición al instante

- **🖐️ Abierta** (Mano completamente extendida)
- **✊ Puño** (Cierre máximo de todos los dedos)
- **✌️ Pinza** (Índice y pulgar juntos, otros relajados)
- **☝️ Señalar** (Índice extendido, otros cerrados)

#### 🎚️ SLIDERS DE CONTROL (0-100%)
Controla cada servo motor de forma independiente:

- **S1: Índice** (0% = abierto, 100% = cerrado)
- **S2: Grupo** (controla Medio, Anular, Meñique)
- **S3: Pulgar** (oposición y flexión)

Mueve los sliders **lentamente** para ver la transición suave.

#### 📊 TELEMETRÍA ACTUAL

**PWM (Microsegundos)**
- S1, S2, S3: Señal de control del servo (1000-2000 µs)
- 1000 µs = Posición mínima
- 2000 µs = Posición máxima

**Ángulos Articulares**
Expande cada dedo para ver:
- MCP: Flexión de la base (0° - 80°)
- PIP: Flexión del nudillo (0° - 70°)

---

## 📖 GUÍA DE USO PASO A PASO

### Escenario 1: Ver posturas canónicas
```
1. Abre: https://bionichandv1-intnm9gomkciyuqzi5hvqf.streamlit.app/
2. Haz clic en "🖐️ Abierta" → La mano se abre
3. Haz clic en "✊ Puño" → La mano forma un puño
4. Repite con "✌️ Pinza" y "☝️ Señalar"
5. Observa la telemetría cambiar en tiempo real
```

### Escenario 2: Control manual fino
```
1. Usa los sliders S1, S2, S3
2. Mueve lentamente para ver cinemática suave
3. Mira la telemetría:
   - PWM cambia (1000-2000 µs)
   - Ángulos se actualizan (grados)
4. Navega la vista 3D:
   - Click + arrastrar = rotar
   - Rueda = zoom
```

### Escenario 3: Inspeccionar articulaciones
```
1. Pon la mano en posición deseada (postura o slider)
2. Haz clic en "Ángulos" en la derecha
3. Expande cada dedo (Pulgar, Índice, Medio, Anular, Meñique)
4. Ve los ángulos exactos MCP y PIP
5. Compara con los límites (MCP: 0-80°, PIP: 0-70°)
```

---

## 🔍 INTERPRETACIÓN DE LA TELEMETRÍA

### Tabla de Referencia PWM
| PWM (µs) | Posición | Visualización |
|----------|----------|---------------|
| 1000 | Mínimo (abierto) | Color vivo |
| 1500 | Centro (50%) | Medio |
| 2000 | Máximo (cerrado) | Colapsado |

### Ángulos Articulares
| Articulación | Mín | Máx | Acoplamiento |
|-------------|-----|-----|-------------|
| MCP | 0° | 80° | Directo |
| PIP | 0° | 70° | 0.875× MCP |
| Pulgar | 0° | 75° | Especial 3D |

**Nota**: El PIP se acopla al MCP automáticamente (acoplamiento 4-bar).

---

## 🎯 CONSEJOS AVANZADOS

### 1. Velocidad de Respuesta
- **En Cloud**: ~1-2 segundos (normal, es latencia de red)
- **Local**: Instantáneo (< 100 ms)

### 2. Mejor Vista 3D
- Ángulo óptimo: **Frente-arriba** (para ver cinemática)
- Para anatomía: Girar **90°** (vista lateral)
- Para inspeccionar: Zoom **adentro**

### 3. Comparar Posturas
```
1. Abre dos navegadores lado a lado
2. Postura 1 en ventana izquierda
3. Postura 2 en ventana derecha
4. Compara diferencias visuales
```

### 4. Exportar Captura
- Click en 📷 (ícono cámara en Plotly)
- Se descarga PNG de la vista actual

---

## ⚠️ SOLUCIÓN DE PROBLEMAS

### La mano no se mueve
- ✓ Confirma que los sliders están realmente moviéndose
- ✓ Si está muy rápido, espera 2-3 segundos
- ✓ Recarga la página (F5)

### 3D se ve plano
- ✓ Gira la vista haciendo click + arrastrar
- ✓ La cinemática es 2D en planta + flexión en Z
- ✓ Aumenta el zoom para ver mejor

### Telemetría no actualiza
- ✓ Espera 1-2 segundos (latencia de red)
- ✓ Mueve el slider de nuevo
- ✓ Recarga si no cambia

### App cargada muy lenta
- ✓ Está en Streamlit Cloud (USA), hay latencia
- ✓ Instala localmente para velocidad máxima (ver INSTALLATION_GUIDE.md)
- ✓ Cierra otros navegadores

### Errores en consola
- ✓ Click derecho → "Inspeccionar" → "Consola"
- ✓ Captura el error y envía a desarrollador

---

## 📱 COMPATIBILIDAD

| Navegador | Windows | Mac | Linux | Mobile |
|-----------|---------|-----|-------|--------|
| Chrome | ✅ | ✅ | ✅ | ✅ |
| Firefox | ✅ | ✅ | ✅ | ✅ |
| Safari | ✅ | ✅ | ❌ | ⚠️ |
| Edge | ✅ | ✅ | ✅ | ✅ |

**Mobile**: Funciona pero mejor en desktop para 3D interactivo.

---

## 🔗 PRÓXIMOS PASOS

1. **Entendiste la interfaz web** ✅
2. **Quieres ejecutar localmente** → Ver `INSTALLATION_GUIDE.md`
3. **Quieres personalizar** → Ver `API_DOCUMENTATION.md`
4. **Quieres desplegar tu versión** → Ver `DEPLOYMENT_GUIDE.md`

---

## 📞 SOPORTE

**Reportar bug**: Captura pantalla + describe qué hiciste  
**Sugerir feature**: Describe el uso deseado  
**Contacto**: GHOPsT (GitHub)

---

**Versión**: 1.0  
**Última actualización**: 2026-10-01  
**Estado**: ✅ Producción
