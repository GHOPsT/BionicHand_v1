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

# ============ LAYOUT PRINCIPAL ============
col_left, col_right = st.columns([2.5, 1])

# ============ COLUMNA IZQUIERDA: VISTA 3D ============
with col_left:
    st.subheader("📊 Visualización 3D Interactiva", divider="blue")
    
    # Crear instancia de mano
    hand = BionicHand()
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
    
    # Función para generar cilindro 3D real en Plotly
    def create_cylinder_mesh(p1, p2, radius, color, num_segments=12):
        """Genera un cilindro volumétrico con mesh3d entre dos puntos"""
        try:
            p1 = np.asarray(p1, dtype=np.float64).flatten()
            p2 = np.asarray(p2, dtype=np.float64).flatten()
            
            # Asegurar que tenemos exactamente 3 dimensiones
            if len(p1) != 3 or len(p2) != 3:
                return None
            
            # Vector del eje
            axis = p2 - p1
            axis_len = np.linalg.norm(axis)
            
            if axis_len < 0.1:  # Si los puntos son muy cercanos
                return None
            
            axis_norm = axis / axis_len
            
            # Encontrar un vector perpendicular al eje
            # Usando la estrategia de Gram-Schmidt
            if abs(axis_norm[0]) < 0.9:
                temp = np.array([1.0, 0.0, 0.0], dtype=np.float64)
            else:
                temp = np.array([0.0, 1.0, 0.0], dtype=np.float64)
            
            perp1 = temp - np.dot(temp, axis_norm) * axis_norm
            perp1 = perp1 / np.linalg.norm(perp1)
            
            # Segundo vector perpendicular (producto cruz)
            perp2 = np.cross(axis_norm, perp1)
            perp2 = perp2 / np.linalg.norm(perp2)
            
            # Generar vértices del cilindro
            angles = np.linspace(0, 2*np.pi, num_segments, endpoint=False)
            
            # Círculo en punto 1
            vertices_p1 = []
            for angle in angles:
                v = p1 + radius * (np.cos(angle) * perp1 + np.sin(angle) * perp2)
                vertices_p1.append(v)
            
            # Círculo en punto 2
            vertices_p2 = []
            for angle in angles:
                v = p2 + radius * (np.cos(angle) * perp1 + np.sin(angle) * perp2)
                vertices_p2.append(v)
            
            vertices = vertices_p1 + vertices_p2
            x_coords = [float(v[0]) for v in vertices]
            y_coords = [float(v[1]) for v in vertices]
            z_coords = [float(v[2]) for v in vertices]
            
            # Generar caras
            faces_i, faces_j, faces_k = [], [], []
            
            # Caras laterales
            for i in range(num_segments):
                i_next = (i + 1) % num_segments
                # Triángulo 1
                faces_i.append(i)
                faces_j.append(i_next)
                faces_k.append(i + num_segments)
                
                # Triángulo 2
                faces_i.append(i_next)
                faces_j.append(i_next + num_segments)
                faces_k.append(i + num_segments)
            
            return go.Mesh3d(
                x=x_coords, y=y_coords, z=z_coords,
                i=faces_i, j=faces_j, k=faces_k,
                opacity=0.75,
                color=color,
                name="",
                showlegend=False,
                hoverinfo='skip'
            )
        except Exception as e:
            return None
    
    # Dibujar dedos con cilindros volumétricos
    for finger in hand.fingers:
        pts_2d = finger.get_positions()  # Retorna (3, 2): [P0_Base, P1_Nudillo, P2_Yema] en 2D
        
        # Convertir a 3D agregando Z=0
        pts = np.column_stack([pts_2d, np.zeros(len(pts_2d))])
        color = colors_map[finger.name]
        
        # Falange proximal (segmento 1)
        cylinder1 = create_cylinder_mesh(pts[0], pts[1], 4.5, color)
        if cylinder1:
            fig_3d.add_trace(cylinder1)
        
        # Falange distal (segmento 2)
        cylinder2 = create_cylinder_mesh(pts[1], pts[2], 4.0, color)
        if cylinder2:
            fig_3d.add_trace(cylinder2)
        
        # Línea esquelética (para referencia)
        fig_3d.add_trace(go.Scatter3d(
            x=pts[:, 0], 
            y=pts[:, 1], 
            z=pts[:, 2],
            mode='lines',
            name=f"{finger.name} ({finger.mcp.angle:.1f}°)",
            line=dict(color=color, width=4),
            hovertemplate=f"{finger.name}<br>MCP: {finger.mcp.angle:.1f}°<br>PIP: {finger.pip.angle:.1f}°<extra></extra>"
        ))
        
        # Esferas en articulaciones
        fig_3d.add_trace(go.Scatter3d(
            x=pts[:, 0], 
            y=pts[:, 1], 
            z=pts[:, 2],
            mode='markers',
            marker=dict(size=6, color=color, symbol='circle'),
            showlegend=False,
            hoverinfo='skip'
        ))
    
    # Palma simplificada
    palm_origin = [0, 50, 0]
    fig_3d.add_trace(go.Scatter3d(
        x=[palm_origin[0]], y=[palm_origin[1]], z=[palm_origin[2]],
        mode='markers',
        name="Palma",
        marker=dict(size=14, color='#c8bda8', symbol='diamond'),
        hovertemplate="Palma<extra></extra>"
    ))
    
    # Configuración de la vista 3D
    fig_3d.update_layout(
        title="🤖 Mano Biónica — Visualización 3D Volumétrica",
        scene=dict(
            xaxis=dict(title="X (mm)", range=[-60, 100], backgroundcolor="rgb(20,20,20)", gridcolor="rgb(40,40,40)"),
            yaxis=dict(title="Y (mm)", range=[-20, 100], backgroundcolor="rgb(20,20,20)", gridcolor="rgb(40,40,40)"),
            zaxis=dict(title="Z (mm)", range=[-30, 30], backgroundcolor="rgb(20,20,20)", gridcolor="rgb(40,40,40)"),
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
    
    u_idx_new = st.slider("S1: Índice", 0.0, 1.0, st.session_state.u_idx, 0.01, key="slider_idx")
    u_grp_new = st.slider("S2: Grupo", 0.0, 1.0, st.session_state.u_grp, 0.01, key="slider_grp")
    u_thb_new = st.slider("S3: Pulgar", 0.0, 1.0, st.session_state.u_thb, 0.01, key="slider_thb")
    
    # Actualizar estado
    st.session_state.u_idx = u_idx_new
    st.session_state.u_grp = u_grp_new
    st.session_state.u_thb = u_thb_new
    
    st.divider()
    
    # === TELEMETRÍA EN TIEMPO REAL ===
    st.write("**📊 Telemetría Actual:**")
    
    hand_telemetry = hand.get_telemetry()
    
    # PWM Servos
    col_pwm1, col_pwm2 = st.columns(2)
    
    with col_pwm1:
        pwm_idx = hand_telemetry["actuators"]["servo_index"]["pwm_us"]
        st.metric("PWM S1", f"{pwm_idx:.0f} µs", 
                 delta=f"{(pwm_idx - 1000):.0f} offset" if pwm_idx != 1000 else "MIN")
    
    with col_pwm2:
        pwm_grp = hand_telemetry["actuators"]["servo_group"]["pwm_us"]
        st.metric("PWM S2", f"{pwm_grp:.0f} µs",
                 delta=f"{(pwm_grp - 1000):.0f} offset" if pwm_grp != 1000 else "MIN")
    
    pwm_thb = hand_telemetry["actuators"]["servo_thumb"]["pwm_us"]
    st.metric("PWM S3", f"{pwm_thb:.0f} µs",
             delta=f"{(pwm_thb - 1000):.0f} offset" if pwm_thb != 1000 else "MIN")
    
    st.divider()
    
    # Ángulos articulares
    st.write("**🔄 Ángulos Articulares (grados):**")
    
    for finger_name, angles in hand_telemetry["joints"].items():
        with st.expander(f"📍 {finger_name}", expanded=(finger_name=="Índice")):
            col1, col2 = st.columns(2)
            with col1:
                st.metric("MCP Base", f"{angles['mcp_deg']:.1f}°")
            with col2:
                st.metric("PIP Medio", f"{angles['pip_deg']:.1f}°")

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