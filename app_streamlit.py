"""
BionicHand Simulator — Aplicación Streamlit 3D
Interfaz web interactiva para visualización y control de prótesis biónica
"""
import sys
import os
from pathlib import Path

# Asegurar que el path está correcto para importaciones relativas
current_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(current_dir))

import streamlit as st
import numpy as np
from plotly import graph_objects as go

# Importar módulos locales con manejo de errores
try:
    from core.hand import BionicHand
    from control.poses import Pose, POSE_ACTUATOR_MAP
    from config.dimensions import FINGER_DIMENSIONS, PALM_SPACING, JOINT_LIMITS, COUPLING_RATIO_4BAR
except ImportError as e:
    st.error(f"❌ Error importando módulos: {e}")
    st.stop()

# ============ CACHING PARA OPTIMIZACIÓN ============
@st.cache_resource
def get_hand_instance():
    """Cachea la instancia de BionicHand para evitar recálculos"""
    return BionicHand()

@st.cache_data
def compute_finger_positions_cached(u_idx, u_grp, u_thb, finger_name):
    """Cachea el cálculo de posiciones 3D para cada dedo"""
    from config.dimensions import FINGER_DIMENSIONS, PALM_SPACING, JOINT_LIMITS
    
    d = FINGER_DIMENSIONS[
        "thumb" if finger_name == "Pulgar" else
        "index" if finger_name == "Índice" else
        "middle" if finger_name == "Medio" else
        "ring" if finger_name == "Anular" else "pinky"
    ]
    l1, l2 = d["l1_proximal"], d["l2_distal"]
    
    if finger_name == "Pulgar":
        mcp_max = JOINT_LIMITS["thumb_base_flexion"][1]
        pip_max = JOINT_LIMITS["thumb_pip_flexion"][1]
        t1_deg = u_thb * mcp_max
        t2_deg = u_thb * 0.90 * pip_max
        
        t1 = np.radians(t1_deg)
        phi = np.radians(t1_deg + t2_deg)
        origin = np.array([-12.0, 20.0, 9.0])
        
        v1 = np.array([
            -l1 * np.cos(t1) * 0.5 + 0.4 * l1 * np.sin(t1),
             l1 * np.cos(t1) * 0.6 - 0.15 * l1 * np.sin(t1),
             l1 * 0.15 + l1 * np.sin(t1) * 0.6
        ])
        p1 = origin + v1
        
        v2 = np.array([
            -l2 * 0.4 * np.cos(phi) + 0.5 * l2 * np.sin(phi),
             l2 * np.cos(phi) * 0.5 - 0.3 * l2 * np.sin(phi),
             l2 * 0.15 + l2 * np.sin(phi) * 0.7
        ])
        p2 = p1 + v2
        
        return np.array([origin, p1, p2]), t1_deg, t2_deg
    
    else:
        u = u_idx if finger_name == "Índice" else u_grp
        mcp_max = JOINT_LIMITS["mcp_base_flexion"][1]
        pip_max = JOINT_LIMITS["pip_middle_flexion"][1]
        t1_deg = u * mcp_max
        t2_deg = u * COUPLING_RATIO_4BAR * pip_max
        
        t1 = np.radians(t1_deg)
        phi = np.radians(t1_deg + t2_deg)
        
        x_offsets = {
            "Índice": 0.0,
            "Medio": PALM_SPACING["index_to_middle"],
            "Anular": PALM_SPACING["index_to_middle"] + PALM_SPACING["middle_to_ring"],
            "Meñique": PALM_SPACING["index_to_middle"] + PALM_SPACING["middle_to_ring"] + PALM_SPACING["ring_to_pinky"]
        }
        y_offsets = {"Índice": 68.0, "Medio": 72.0, "Anular": 69.0, "Meñique": 62.0}
        origin = np.array([x_offsets[finger_name], y_offsets[finger_name], 0.0])
        
        p1 = origin + np.array([0.0, l1 * np.cos(t1), l1 * np.sin(t1)])
        p2 = p1 + np.array([0.0, l2 * np.cos(phi), l2 * np.sin(phi)])
        
        return np.array([origin, p1, p2]), t1_deg, t2_deg

# ============ CONFIGURACIÓN STREAMLIT ============
st.set_page_config(
    page_title="BionicHand 3D Simulator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS
st.markdown("""
<style>
    .main-title {
        text-align: center;
        font-size: 2.5em;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 10px;
    }
    .subtitle {
        text-align: center;
        font-size: 1.1em;
        color: #666;
        margin-bottom: 30px;
    }
    .metric-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🤖 BionicHand — Simulador 3D Interactivo</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Etapa 1: Control Cinemático en Tiempo Real</div>', unsafe_allow_html=True)

# ============ INICIALIZAR ESTADO ============
if "u_idx" not in st.session_state:
    st.session_state.u_idx = 0.0
    st.session_state.u_grp = 0.0
    st.session_state.u_thb = 0.0
    st.session_state._last_fig_update = None
    st.session_state._cached_fig = None

# ============ LAYOUT PRINCIPAL ============
col_left, col_right = st.columns([3.5, 1])

# ============ COLUMNA IZQUIERDA: VISTA 3D ============
with col_left:
    st.subheader("📊 Visualización 3D Interactiva", divider="blue")
    
    # Usar instancia cacheada de mano
    hand = get_hand_instance()
    hand.set_actuators(st.session_state.u_idx, st.session_state.u_grp, st.session_state.u_thb)
    
    # Crear figura 3D con Plotly
    fig_3d = go.Figure()
    
    # Paleta de colores
    colors_map = {
        "Pulgar": "#ef4444",
        "Índice": "#3b82f6",
        "Medio": "#10b981",
        "Anular": "#f59e0b",
        "Meñique": "#8b5cf6"
    }
    
    # Función para generar cilindro 3D como superficie real
    def draw_cylinder_surface3d(p1, p2, radius, color):
        """Dibuja un cilindro como superficie 3D real usando Surface3d"""
        try:
            p1 = np.asarray(p1, dtype=np.float64).flatten()
            p2 = np.asarray(p2, dtype=np.float64).flatten()
            
            if len(p1) != 3 or len(p2) != 3:
                return None
            
            # Vector del eje
            axis = p2 - p1
            axis_len = np.linalg.norm(axis)
            
            if axis_len < 0.1:
                return None
            
            axis_norm = axis / axis_len
            
            # Vectores perpendiculares usando Gram-Schmidt
            if abs(axis_norm[0]) < 0.9:
                temp = np.array([1.0, 0.0, 0.0], dtype=np.float64)
            else:
                temp = np.array([0.0, 1.0, 0.0], dtype=np.float64)
            
            perp1 = temp - np.dot(temp, axis_norm) * axis_norm
            perp1 = perp1 / (np.linalg.norm(perp1) + 1e-8)
            
            perp2 = np.cross(axis_norm, perp1)
            perp2 = perp2 / (np.linalg.norm(perp2) + 1e-8)
            
            # Generar malla cilíndrica
            u = np.linspace(0, 2*np.pi, 16)  # ángulo
            v = np.linspace(0, 1, 8)  # longitud del cilindro
            
            x_grid = []
            y_grid = []
            z_grid = []
            
            for v_val in v:
                row_x = []
                row_y = []
                row_z = []
                
                for u_val in u:
                    # Posición a lo largo del eje
                    center = p1 + v_val * axis
                    # Punto en el círculo
                    pt = center + radius * (np.cos(u_val) * perp1 + np.sin(u_val) * perp2)
                    row_x.append(pt[0])
                    row_y.append(pt[1])
                    row_z.append(pt[2])
                
                x_grid.append(row_x)
                y_grid.append(row_y)
                z_grid.append(row_z)
            
            x_grid = np.array(x_grid)
            y_grid = np.array(y_grid)
            z_grid = np.array(z_grid)
            
            trace = go.Surface3d(
                x=x_grid,
                y=y_grid,
                z=z_grid,
                surfacecolor=np.ones_like(x_grid),
                colorscale=[[0, color], [1, color]],
                showscale=False,
                hoverinfo='skip',
                opacity=0.9,
                showlegend=False
            )
            
            return trace
        except Exception as e:
            return None
    
    # Dibujar dedos con cilindros volumétricos 3D reales
    finger_names = ["Pulgar", "Índice", "Medio", "Anular", "Meñique"]
    for i, finger in enumerate(hand.fingers):
        name = finger_names[i]
        # Usar función cacheada para evitar recálculos
        pts, mcp_deg, pip_deg = compute_finger_positions_cached(
            st.session_state.u_idx, 
            st.session_state.u_grp, 
            st.session_state.u_thb, 
            name
        )
        color = colors_map[name]
        
        # Falange proximal (segmento 1) - cilindro Surface3d
        trace_prox = draw_cylinder_surface3d(pts[0], pts[1], 4.5, color)
        if trace_prox is not None:
            fig_3d.add_trace(trace_prox)
        
        # Falange distal (segmento 2) - cilindro Surface3d
        trace_dist = draw_cylinder_surface3d(pts[1], pts[2], 4.0, color)
        if trace_dist is not None:
            fig_3d.add_trace(trace_dist)
        
        # Línea esquelética central (para referencia) - más gruesa
        fig_3d.add_trace(go.Scatter3d(
            x=pts[:, 0], 
            y=pts[:, 1], 
            z=pts[:, 2],
            mode='lines',
            name=f"{finger.name} ({finger.mcp.angle:.1f}°)",
            line=dict(color=color, width=8),
            hovertemplate=f"{finger.name}<br>MCP: {finger.mcp.angle:.1f}°<br>PIP: {finger.pip.angle:.1f}°<extra></extra>"
        ))
        
        # Esferas en articulaciones
        fig_3d.add_trace(go.Scatter3d(
            x=pts[:, 0], 
            y=pts[:, 1], 
            z=pts[:, 2],
            mode='markers',
            marker=dict(size=7, color=color, symbol='circle'),
            showlegend=False,
            hoverinfo='skip'
        ))
    
    # Palma volumétrica 3D - Malla Mesh3d
    palm_top_pts = [
        [-20.0, 45.0, 5],     # Base eminencia tenar
        [-25.0, 26.0, 8],     # Inserción pulgar
        [-10.0, 50.0, 3],     # Borde radial índice
        [0, 68, 2],           # Nudillo Índice
        [20.8, 72, 2],        # Nudillo Medio
        [41.4, 69, 2],        # Nudillo Anular
        [62.9, 62, 3],        # Nudillo Meñique
        [70.0, 40.0, 4],      # Lado hipotenar superior
        [65.0, 15.0, 6],      # Lado hipotenar inferior
        [30.0, -5.0, 5],      # Muñeca lateral
        [-15.0, -5.0, 5]      # Muñeca medial
    ]
    
    palm_top = np.array(palm_top_pts)
    palm_bot = palm_top.copy()
    palm_bot[:, 2] -= 12.0  # Profundidad palmar
    
    # Vértices combinados
    palm_verts = np.vstack([palm_top, palm_bot])
    n_palm = len(palm_top)
    
    # Generar índices de caras
    i_idx = []
    j_idx = []
    k_idx = []
    
    # Tapa superior (dorso) - polígono cerrado
    for idx in range(n_palm - 2):
        i_idx.append(0)
        j_idx.append(idx + 1)
        k_idx.append(idx + 2)
    
    # Tapa inferior (palma) - polígono cerrado
    for idx in range(n_palm - 2):
        i_idx.append(n_palm)
        j_idx.append(n_palm + idx + 2)
        k_idx.append(n_palm + idx + 1)
    
    # Caras laterales conectando dorso con palma
    for idx in range(n_palm - 1):
        next_idx = idx + 1
        # Triángulo 1: dorso superior
        i_idx.append(idx)
        j_idx.append(next_idx)
        k_idx.append(n_palm + idx)
        # Triángulo 2: palma inferior
        i_idx.append(next_idx)
        j_idx.append(n_palm + next_idx)
        k_idx.append(n_palm + idx)
    
    # Cerrar anillo (último con primero)
    i_idx.append(n_palm - 1)
    j_idx.append(0)
    k_idx.append(n_palm)
    
    i_idx.append(n_palm - 1)
    j_idx.append(n_palm)
    k_idx.append(2 * n_palm - 1)
    
    palm_mesh = go.Mesh3d(
        x=palm_verts[:, 0],
        y=palm_verts[:, 1],
        z=palm_verts[:, 2],
        i=i_idx,
        j=j_idx,
        k=k_idx,
        color='#d4c5b0',
        opacity=0.75,
        name="Palma",
        showlegend=True,
        hovertemplate="Palma<extra></extra>"
    )
    fig_3d.add_trace(palm_mesh)
    
    # Configuración de la vista 3D
    fig_3d.update_layout(
        title="🤖 Mano Biónica — Visualización 3D Volumétrica",
        scene=dict(
            xaxis=dict(title="X (mm)", range=[-45, 85], backgroundcolor="rgb(20,20,20)", gridcolor="rgb(40,40,40)"),
            yaxis=dict(title="Y (mm)", range=[-15, 160], backgroundcolor="rgb(20,20,20)", gridcolor="rgb(40,40,40)"),
            zaxis=dict(title="Z (mm) [Flexión]", range=[-20, 85], backgroundcolor="rgb(20,20,20)", gridcolor="rgb(40,40,40)"),
            camera=dict(
                eye=dict(x=1.2, y=1.2, z=0.9),
                center=dict(x=0, y=0, z=0),
                up=dict(x=0, y=0, z=1)
            ),
            aspectmode='data'
        ),
        hovermode='closest',
        height=700,
        width=None,
        showlegend=True,
        template="plotly_dark",
        font=dict(size=10, family="Arial"),
        margin=dict(l=0, r=0, b=0, t=50),
        paper_bgcolor="#1e222b",
        plot_bgcolor="#1e222b"
    )
    
    st.plotly_chart(fig_3d, use_container_width=True)

# ============ COLUMNA DERECHA: CONTROLES ============
with col_right:
    st.subheader("🎮 Panel de Control", divider="green")
    
    # === POSTURAS CANÓNICAS ===
    st.write("**Posturas Rápidas:**")
    
    pose_cols = st.columns(2, gap="small")
    
    with pose_cols[0]:
        if st.button("🖐️ Abierta", use_container_width=True, key="pose_open"):
            p = POSE_ACTUATOR_MAP[Pose.OPEN_HAND]
            st.session_state.u_idx = p["index"]
            st.session_state.u_grp = p["group"]
            st.session_state.u_thb = p["thumb"]
            st.rerun()
    
    with pose_cols[1]:
        if st.button("✊ Puño", use_container_width=True, key="pose_power"):
            p = POSE_ACTUATOR_MAP[Pose.POWER_GRASP]
            st.session_state.u_idx = p["index"]
            st.session_state.u_grp = p["group"]
            st.session_state.u_thb = p["thumb"]
            st.rerun()
    
    pose_cols2 = st.columns(2, gap="small")
    
    with pose_cols2[0]:
        if st.button("✌️ Pinza", use_container_width=True, key="pose_pinch"):
            p = POSE_ACTUATOR_MAP[Pose.PINCH_GRIP]
            st.session_state.u_idx = p["index"]
            st.session_state.u_grp = p["group"]
            st.session_state.u_thb = p["thumb"]
            st.rerun()
    
    with pose_cols2[1]:
        if st.button("☝️ Señalar", use_container_width=True, key="pose_point"):
            p = POSE_ACTUATOR_MAP[Pose.POINTING]
            st.session_state.u_idx = p["index"]
            st.session_state.u_grp = p["group"]
            st.session_state.u_thb = p["thumb"]
            st.rerun()
    
    st.divider()
    
    # === SLIDERS DE CONTROL ===
    st.write("**Control Manual (0-100%):**")
    
    # Usar callbacks para actualizacion inmediata
    def update_slider_idx():
        st.session_state.u_idx = st.session_state.slider_idx_input
    def update_slider_grp():
        st.session_state.u_grp = st.session_state.slider_grp_input
    def update_slider_thb():
        st.session_state.u_thb = st.session_state.slider_thb_input
    
    st.slider("S1: Índice", 0.0, 1.0, st.session_state.u_idx, 0.01, 
              key="slider_idx_input", on_change=update_slider_idx)
    st.slider("S2: Grupo", 0.0, 1.0, st.session_state.u_grp, 0.01, 
              key="slider_grp_input", on_change=update_slider_grp)
    st.slider("S3: Pulgar", 0.0, 1.0, st.session_state.u_thb, 0.01, 
              key="slider_thb_input", on_change=update_slider_thb)
    
    st.divider()
    
    # === TELEMETRÍA EN TIEMPO REAL ===
    st.write("**📊 Telemetría**")
    st.caption("Estado actual de servos y articulaciones")
    
    hand_telemetry = hand.get_telemetry()
    
    # PWM Servos - Compacto
    pwm_idx = hand_telemetry["actuators"]["servo_index"]["pwm_us"]
    pwm_grp = hand_telemetry["actuators"]["servo_group"]["pwm_us"]
    pwm_thb = hand_telemetry["actuators"]["servo_thumb"]["pwm_us"]
    
    col_pwm1, col_pwm2, col_pwm3 = st.columns(3)
    with col_pwm1:
        st.metric("S1", f"{pwm_idx:.0f}µs", label_visibility="collapsed")
    with col_pwm2:
        st.metric("S2", f"{pwm_grp:.0f}µs", label_visibility="collapsed")
    with col_pwm3:
        st.metric("S3", f"{pwm_thb:.0f}µs", label_visibility="collapsed")
    
    st.divider()
    
    # Ángulos articulares - Formato compacto
    st.write("**🔄 Ángulos**")
    st.caption("MCP y PIP por dedo")
    
    for finger_name, angles in hand_telemetry["joints"].items():
        with st.expander(f"{finger_name}: {angles['mcp_deg']:.1f}° / {angles['pip_deg']:.1f}°", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.metric("MCP", f"{angles['mcp_deg']:.1f}°", label_visibility="collapsed")
            with col2:
                st.metric("PIP", f"{angles['pip_deg']:.1f}°", label_visibility="collapsed")

# ============ SECCIÓN INFERIOR: INFORMACIÓN ============
st.divider()

with st.expander("ℹ️ Información Técnica", expanded=False):
    info_cols = st.columns(3)
    
    with info_cols[0]:
        st.write("**Especificaciones:**")
        st.write(f"- Dedos: 5 (Pulgar + 4 dedos)")
        st.write(f"- DOF por dedo: 2 (MCP + PIP)")
        st.write(f"- Servos: 3 (independientes)")
        st.write(f"- Rango PWM: 1000-2000 µs")
    
    with info_cols[1]:
        st.write("**Límites Articulares:**")
        st.write(f"- MCP: 0° - 80°")
        st.write(f"- PIP: 0° - 70°")
        st.write(f"- Pulgar: 0° - 75° (base)")
        st.write(f"- Acoplamiento 4-bar: 0.875")
    
    with info_cols[2]:
        st.write("**Medidas CAD (mm):**")
        st.write(f"- Índice total: 77.50 mm")
        st.write(f"- Medio total: 81.52 mm")
        st.write(f"- Pulgar total: 79.06 mm")
        st.write(f"- Precisión: 2 decimales")

st.write("---")
st.write("🔄 **Etapa 1 (Cinemática)** | 📈 Etapa 2 (Simulación Dinámica) | 🧠 Etapa 3 (EMG Control)")