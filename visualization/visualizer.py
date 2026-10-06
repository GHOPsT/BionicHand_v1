"""
Visualizador 3D Avanzado e Interactivo para BionicHand (Etapa 1).
Implementa:
- Proporción 4:1 (Área gráfica 3D a la izquierda, barra lateral de telemetría a la derecha).
- Barra inferior completa para botones de posturas canónicas y sliders de servomotores.
- Representación tridimensional volumétrica con contornos anatómicos de palma y falanges.
- Navegación orbital 3D interactiva (rotación con clic y arrastre del ratón).
"""
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.widgets import Button, Slider
from core.hand import BionicHand
from control.poses import Pose, POSE_ACTUATOR_MAP
from config.dimensions import FINGER_DIMENSIONS, PALM_SPACING, JOINT_LIMITS, COUPLING_RATIO_4BAR

class BionicHandVisualizer:
    def __init__(self, hand: BionicHand):
        self.hand = hand
        self.current_pose_name = "Mano Abierta"

        # Configuración de ventana principal (16x10 pulgadas para más espacio)
        self.fig = plt.figure(figsize=(16.0, 10.0), facecolor='#1e222b')
        self.fig.canvas.manager.set_window_title("BionicHand — Simulador Cinemático 3D (Etapa 1)")
        
        # Desactivar toolbar automática de matplotlib (que aparecía abajo)
        plt.rcParams['toolbar'] = 'none'
        
        # Remover el espacio reservado para la toolbar
        self.fig.subplots_adjust(bottom=0.0, top=1.0, left=0.0, right=1.0)

        # Paleta de colores de ingeniería para los dedos
        self.colors = {
            "Pulgar":  {"main": "#ef4444", "joint": "#b91c1c", "pad": "#fca5a5"},
            "Índice":  {"main": "#3b82f6", "joint": "#1d4ed8", "pad": "#93c5fd"},
            "Medio":   {"main": "#10b981", "joint": "#047857", "pad": "#6ee7b7"},
            "Anular":  {"main": "#f59e0b", "joint": "#b45309", "pad": "#fde68a"},
            "Meñique": {"main": "#8b5cf6", "joint": "#6d28d9", "pad": "#c4b5fd"}
        }

        # Parámetros de visualización ajustables
        self.cylinder_radius_proximal = 4.5
        self.cylinder_radius_distal = 4.0
        self.sphere_radius_base = 3.5
        self.sphere_radius_joint = 3.0
        self.sphere_radius_tip = 4.5
        self.alpha_cylinders = 0.88
        self.alpha_joints = 0.92
        self.alpha_tips = 0.85

        # LAYOUT: 4/5 (izquierda) + 1/5 (derecha telemetría)
        # 1. Barra Superior de Sliders (ARRIBA en 4/5)
        self._setup_top_sliders()

        # 2. Viewport 3D principal (MEDIO en 4/5, desde Y=0.20 a Y=0.80)
        self.ax_3d = self.fig.add_axes([0.01, 0.20, 0.72, 0.60], projection='3d', facecolor='#1e222b')
        self.ax_3d.view_init(elev=22, azim=-62)

        # 3. Barra Lateral Derecha de Telemetría (Derecha 1/5, desde Y=0.20 a Y=1.0)
        self.ax_side = self.fig.add_axes([0.74, 0.20, 0.25, 0.70], facecolor='#14171f')
        self.ax_side.axis('off')

        # 4. Panel Inferior: Botones de Poses + Controles Avanzados (ABAJO)
        self._setup_bottom_controls()

        # Render inicial
        self.update_view()

    def _setup_top_sliders(self):
        """Barra superior con sliders de servomotores en la parte superior (4/5 del ancho)."""
        # Posición superior: Y de 0.80 a 0.98
        # Ancho: 4/5 = 0.72
        slider_h = 0.045
        
        ax_s_idx = self.fig.add_axes([0.11, 0.92, 0.58, slider_h], facecolor='#2a303c')
        ax_s_grp = self.fig.add_axes([0.11, 0.86, 0.58, slider_h], facecolor='#2a303c')
        ax_s_thb = self.fig.add_axes([0.11, 0.80, 0.58, slider_h], facecolor='#2a303c')

        self.slider_idx = Slider(ax_s_idx, 'Servo 1 (Índice)', 0.0, 1.0, valinit=0.0, color='#3b82f6')
        self.slider_grp = Slider(ax_s_grp, 'Servo 2 (Grupo)', 0.0, 1.0, valinit=0.0, color='#10b981')
        self.slider_thb = Slider(ax_s_thb, 'Servo 3 (Pulgar)', 0.0, 1.0, valinit=0.0, color='#ef4444')

        for s in [self.slider_idx, self.slider_grp, self.slider_thb]:
            s.label.set_color('#e2e8f0')
            s.label.set_fontsize(9)
            s.label.set_fontweight('bold')
            s.valtext.set_color('#e2e8f0')
            s.valtext.set_fontsize(9)

        self.slider_idx.on_changed(self._on_slider)
        self.slider_grp.on_changed(self._on_slider)
        self.slider_thb.on_changed(self._on_slider)

    def _setup_bottom_controls(self):
        """Barra inferior: Botones + Controles Avanzados con padding para números."""
        
        # ===== FILA 1: BOTONES DE POSES (Y=0.11-0.18) =====
        btn_w, btn_h, btn_y = 0.17, 0.055, 0.125
        ax_open  = self.fig.add_axes([0.01 + 0 * 0.18, btn_y, btn_w, btn_h])
        ax_fist  = self.fig.add_axes([0.01 + 1 * 0.18, btn_y, btn_w, btn_h])
        ax_pinch = self.fig.add_axes([0.01 + 2 * 0.18, btn_y, btn_w, btn_h])
        ax_point = self.fig.add_axes([0.01 + 3 * 0.18, btn_y, btn_w, btn_h])

        self.btn_open  = Button(ax_open,  'Mano Abierta', color='#2563eb', hovercolor='#3b82f6')
        self.btn_fist  = Button(ax_fist,  'Puño Cerrado', color='#d97706', hovercolor='#f59e0b')
        self.btn_pinch = Button(ax_pinch, 'Pinza Fina', color='#059669', hovercolor='#10b981')
        self.btn_point = Button(ax_point, 'Señalar', color='#7c3aed', hovercolor='#8b5cf6')

        for b in [self.btn_open, self.btn_fist, self.btn_pinch, self.btn_point]:
            b.label.set_color('#ffffff')
            b.label.set_fontsize(9)
            b.label.set_fontweight('bold')

        self.btn_open.on_clicked(lambda e: self.set_pose(Pose.OPEN_HAND))
        self.btn_fist.on_clicked(lambda e: self.set_pose(Pose.POWER_GRASP))
        self.btn_pinch.on_clicked(lambda e: self.set_pose(Pose.PINCH_GRIP))
        self.btn_point.on_clicked(lambda e: self.set_pose(Pose.POINTING))

        # ===== FILA 2: RADIOS DE CILINDROS (Y=0.065-0.085) CON PADDING =====
        slider_h = 0.025
        # Padding al inicio (0.01) con espacio suficiente para labels
        ax_rad_prox = self.fig.add_axes([0.05, 0.075, 0.29, slider_h], facecolor='#2a303c')
        ax_rad_dist = self.fig.add_axes([0.42, 0.075, 0.29, slider_h], facecolor='#2a303c')
        
        self.slider_rad_prox = Slider(ax_rad_prox, 'R. Prox.', 2.0, 7.0, valinit=4.5, color='#06b6d4')
        self.slider_rad_dist = Slider(ax_rad_dist, 'R. Dist.', 2.0, 7.0, valinit=4.0, color='#06b6d4')
        
        for s in [self.slider_rad_prox, self.slider_rad_dist]:
            s.label.set_color('#e2e8f0')
            s.label.set_fontsize(8)
            s.valtext.set_color('#e2e8f0')
            s.valtext.set_fontsize(8)
        
        self.slider_rad_prox.on_changed(lambda v: setattr(self, 'cylinder_radius_proximal', v) or self.update_view())
        self.slider_rad_dist.on_changed(lambda v: setattr(self, 'cylinder_radius_distal', v) or self.update_view())

        # ===== FILA 3: TRANSPARENCIAS (Y=0.015-0.035) CON PADDING =====
        ax_alpha_cyl = self.fig.add_axes([0.05, 0.025, 0.29, slider_h], facecolor='#2a303c')
        ax_alpha_jnt = self.fig.add_axes([0.42, 0.025, 0.29, slider_h], facecolor='#2a303c')
        
        self.slider_alpha_cyl = Slider(ax_alpha_cyl, 'Α Cil.', 0.3, 1.0, valinit=0.88, color='#f97316')
        self.slider_alpha_jnt = Slider(ax_alpha_jnt, 'Α Art.', 0.3, 1.0, valinit=0.92, color='#f97316')
        
        for s in [self.slider_alpha_cyl, self.slider_alpha_jnt]:
            s.label.set_color('#e2e8f0')
            s.label.set_fontsize(8)
            s.valtext.set_color('#e2e8f0')
            s.valtext.set_fontsize(8)
        
        self.slider_alpha_cyl.on_changed(lambda v: setattr(self, 'alpha_cylinders', v) or self.update_view())
        self.slider_alpha_jnt.on_changed(lambda v: setattr(self, 'alpha_joints', v) or self.update_view())

    def _on_slider(self, val):
        self.current_pose_name = "Control Manual"
        self.hand.set_actuators(
            self.slider_idx.val,
            self.slider_grp.val,
            self.slider_thb.val
        )
        self.update_view()

    def set_pose(self, pose: Pose):
        self.current_pose_name = pose.value
        m = POSE_ACTUATOR_MAP[pose]
        self.slider_idx.set_val(m["index"])
        self.slider_grp.set_val(m["group"])
        self.slider_thb.set_val(m["thumb"])

    def _compute_finger_3d(self, name: str):
        """Calcula las coordenadas tridimensionales de las falanges del dedo."""
        d = FINGER_DIMENSIONS[
            "thumb" if name == "Pulgar" else
            "index" if name == "Índice" else
            "middle" if name == "Medio" else
            "ring" if name == "Anular" else "pinky"
        ]
        l1, l2 = d["l1_proximal"], d["l2_distal"]

        if name == "Pulgar":
            u = self.hand.servo_thumb.command
            mcp_max = JOINT_LIMITS["thumb_base_flexion"][1]
            pip_max = JOINT_LIMITS["thumb_pip_flexion"][1]
            t1_deg = u * mcp_max
            t2_deg = u * 0.90 * pip_max

            t1 = np.radians(t1_deg)
            phi = np.radians(t1_deg + t2_deg)
            origin = np.array([-12.0, 20.0, 9.0])

            # Oposición 3D mejorada hacia el índice
            # Aumentada componente X (1.0 en lugar de 0.6) para acercamiento horizontal
            # Reducida componente Z para evitar levantamiento excesivo
            v1 = np.array([
                -l1 * np.cos(t1) * 0.4 + 1.0 * l1 * np.sin(t1),
                 l1 * np.cos(t1) * 0.5 - 0.7 * l1 * np.sin(t1),
                 l1 * 0.15 + l1 * np.sin(t1) * 0.6
            ])
            p1 = origin + v1

            # Segunda falange del pulgar
            v2 = np.array([
                -l2 * 0.3 * np.cos(phi) + 1.0 * l2 * np.sin(phi),
                 l2 * np.cos(phi) * 0.8 - 0.6 * l2 * np.sin(phi),
                 l2 * 0.15 + l2 * np.sin(phi) * 0.7
            ])
            p2 = p1 + v2

            return np.array([origin, p1, p2]), t1_deg, t2_deg

        else:
            u = self.hand.servo_index.command if name == "Índice" else self.hand.servo_group.command
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
            origin = np.array([x_offsets[name], y_offsets[name], 0.0])

            # Flexión hacia el frente palmar (+Z) y cierre hacia la palma (-Y)
            p1 = origin + np.array([0.0, l1 * np.cos(t1), l1 * np.sin(t1)])
            p2 = p1 + np.array([0.0, l2 * np.cos(phi), l2 * np.sin(phi)])

            return np.array([origin, p1, p2]), t1_deg, t2_deg

    def _draw_palm_volume_3d(self):
        """Dibuja el chasis volumétrico 3D de la palma con contornos anatómicos detallados."""
        # Puntos superiores de la palma (lado del dorso)
        top_pts = [
            [-20.0, 45.0, 5],     # Base eminencia tenar (elevada)
            [-25.0, 26.0, 8],     # Inserción pulgar (elevada)
            [-10.0, 50.0, 3],     # Borde radial índice
            [0, 68, 2],           # Nudillo Índice
            [20.8, 72, 2],        # Nudillo Medio
            [41.4, 69, 2],        # Nudillo Anular
            [62.9, 62, 3],        # Nudillo Meñique
            [70.0, 40.0, 4],      # Lado hipotenar superior
            [65.0, 15.0, 6],      # Lado hipotenar inferior (elevado)
            [30.0, -5.0, 5],      # Muñeca lateral
            [-15.0, -5.0, 5]      # Muñeca medial
        ]

        # Puntos inferiores de la palma (lado de la palma)
        bot_pts = [[p[0], p[1], p[2] - 12.0] for p in top_pts]

        # Crear caras del volumen
        faces = []
        
        # Tapa superior (dorso)
        faces.append(top_pts)
        
        # Tapa inferior (palma)
        faces.append(bot_pts)
        
        # Caras laterales
        n = len(top_pts)
        for i in range(n):
            p_next = (i + 1) % n
            face = [top_pts[i], top_pts[p_next], bot_pts[p_next], bot_pts[i]]
            faces.append(face)

        # Dibujar palma volumétrica con más presencia
        palm_poly = Poly3DCollection(faces, alpha=0.50, facecolor='#c8bda8', 
                                    edgecolor='#6e6350', linewidths=1.5)
        self.ax_3d.add_collection3d(palm_poly)
        
        # Agregar detalles anatómicos: surcos de la palma
        # Línea central (surco longitudinal)
        center_x = np.linspace(-15, 40, 20)
        center_y = np.linspace(-5, 75, 20)
        center_z = np.linspace(-2, 2, 20)
        self.ax_3d.plot(center_x, center_y, center_z, '-', color='#8b7355', linewidth=0.8, alpha=0.6)

    def _draw_cylinder(self, p1: np.ndarray, p2: np.ndarray, radius: float, color: str, alpha: float = 0.85):
        """Dibuja un cilindro volumétrico entre dos puntos."""
        z = np.array([p1, p2])
        axis = p2 - p1
        axis_len = np.linalg.norm(axis)
        if axis_len == 0:
            return
        
        axis = axis / axis_len
        # Vectores perpendiculares
        if abs(axis[0]) < 0.9:
            perp1 = np.array([0, -axis[2], axis[1]])
        else:
            perp1 = np.array([-axis[1], axis[0], 0])
        perp1 = perp1 / np.linalg.norm(perp1)
        perp2 = np.cross(axis, perp1)
        
        # Círculo en el primer punto
        angles = np.linspace(0, 2*np.pi, 12)
        circle1 = p1[:, None] + radius * (perp1[:, None] * np.cos(angles) + perp2[:, None] * np.sin(angles))
        # Círculo en el segundo punto
        circle2 = p2[:, None] + radius * (perp1[:, None] * np.cos(angles) + perp2[:, None] * np.sin(angles))
        
        # Crear caras laterales del cilindro
        faces = []
        for i in range(len(angles)-1):
            face = [circle1[:, i].tolist(), circle1[:, i+1].tolist(), 
                   circle2[:, i+1].tolist(), circle2[:, i].tolist()]
            faces.append(face)
        
        # Tapas superior e inferior
        faces.append(circle1.T.tolist())
        faces.append(circle2.T.tolist())
        
        cyl = Poly3DCollection(faces, alpha=alpha, facecolor=color, edgecolor='#0f172a', linewidths=0.5)
        self.ax_3d.add_collection3d(cyl)

    def _draw_sphere(self, center: np.ndarray, radius: float, color: str, alpha: float = 0.9):
        """Dibuja una esfera volumétrica en la posición especificada."""
        u = np.linspace(0, 2 * np.pi, 8)
        v = np.linspace(0, np.pi, 6)
        x = radius * np.outer(np.cos(u), np.sin(v)) + center[0]
        y = radius * np.outer(np.sin(u), np.sin(v)) + center[1]
        z = radius * np.outer(np.ones(np.size(u)), np.cos(v)) + center[2]
        self.ax_3d.plot_surface(x, y, z, color=color, alpha=alpha, edgecolor='#ffffff', linewidth=0.3)

    def update_view(self):
        elev, azim = self.ax_3d.elev, self.ax_3d.azim

        self.ax_3d.clear()
        self.ax_3d.set_facecolor('#1e222b')
        self.ax_3d.grid(True, linestyle=':', alpha=0.25, color='#475569')

        self.ax_3d.set_xlim(-45, 85)
        self.ax_3d.set_ylim(-15, 160)
        self.ax_3d.set_zlim(-20, 85)

        self.ax_3d.set_xlabel('X (mm) [Transversal]', color='#94a3b8', fontsize=8, labelpad=6)
        self.ax_3d.set_ylabel('Y (mm) [Longitudinal]', color='#94a3b8', fontsize=8, labelpad=6)
        self.ax_3d.set_zlabel('Z (mm) [Palmar/Flexión]', color='#94a3b8', fontsize=8, labelpad=6)
        self.ax_3d.tick_params(colors='#64748b', labelsize=7)

        # 1. Dibujar volumen de la palma
        self._draw_palm_volume_3d()

        # 2. Dibujar dedos con volumen y esferas articulares
        finger_names = ["Pulgar", "Índice", "Medio", "Anular", "Meñique"]
        telemetry_angles = {}

        for name in finger_names:
            pts, mcp_deg, pip_deg = self._compute_finger_3d(name)
            telemetry_angles[name] = (mcp_deg, pip_deg, pts)
            c = self.colors[name]

            # Dibujar falanges como cilindros volumétricos con radios ajustables
            if len(pts) >= 3:
                # Falange proximal (origen a nudillo)
                self._draw_cylinder(pts[0], pts[1], radius=self.cylinder_radius_proximal, 
                                  color=c["main"], alpha=self.alpha_cylinders)
                # Falange distal (nudillo a yema)
                self._draw_cylinder(pts[1], pts[2], radius=self.cylinder_radius_distal, 
                                  color=c["main"], alpha=self.alpha_cylinders)
                
                # Articulaciones como esferas
                self._draw_sphere(pts[0], radius=self.sphere_radius_base, color=c["joint"], 
                                alpha=self.alpha_joints)  # Base
                self._draw_sphere(pts[1], radius=self.sphere_radius_joint, color=c["joint"], 
                                alpha=self.alpha_joints)  # Nudillo (MCP)
                # Yema (almohadilla de contacto) - más grande
                self._draw_sphere(pts[2], radius=self.sphere_radius_tip, color=c["pad"], 
                                alpha=self.alpha_tips)

        # Mantener ángulo de cámara que tenga el usuario
        self.ax_3d.view_init(elev=elev, azim=azim)

        # Actualizar telemetría lateral
        self._render_telemetry_sidebar(telemetry_angles)

        self.fig.canvas.draw_idle()

    def _render_telemetry_sidebar(self, angles: dict):
        self.ax_side.clear()
        self.ax_side.axis('off')

        self.ax_side.text(0.05, 0.96, "BIONICHAND TELEMETRY", color='#38bdf8', fontsize=11, fontweight='bold')
        self.ax_side.text(0.05, 0.92, f"Pose Activa: {self.current_pose_name}", color='#f8fafc', fontsize=9.5, fontweight='bold')
        self.ax_side.axhline(0.90, color='#334155', linewidth=1.2)

        # Actuadores
        self.ax_side.text(0.05, 0.85, "ACTUADORES FÍSICOS (SERVOS):", color='#94a3b8', fontsize=8, fontweight='bold')

        servos = [
            ("Servo 1 (Índice):", self.hand.servo_index.command, '#3b82f6'),
            ("Servo 2 (Grupo):",  self.hand.servo_group.command, '#10b981'),
            ("Servo 3 (Pulgar):", self.hand.servo_thumb.command, '#ef4444')
        ]
        y_pos = 0.80
        for label, val, bar_col in servos:
            pct = val * 100.0
            pwm = 1000.0 + val * 1000.0
            self.ax_side.text(0.05, y_pos, f"{label} {pct:4.1f}% ({pwm:4.0f} µs)", color='#e2e8f0', fontsize=8)
            self.ax_side.barh(y_pos - 0.022, val, height=0.015, left=0.05, color=bar_col, alpha=0.85)
            self.ax_side.barh(y_pos - 0.022, 1.0, height=0.015, left=0.05, color='#334155', alpha=0.4, zorder=0)
            y_pos -= 0.065

        self.ax_side.axhline(y_pos + 0.01, color='#334155', linewidth=1.2)
        y_pos -= 0.03

        # Articulaciones
        self.ax_side.text(0.05, y_pos, "ÁNGULOS ARTICULARES REALES:", color='#94a3b8', fontsize=8, fontweight='bold')
        y_pos -= 0.04

        for name in ["Pulgar", "Índice", "Medio", "Anular", "Meñique"]:
            mcp, pip, tip = angles[name]
            col = self.colors[name]["main"]
            self.ax_side.text(0.05, y_pos, f"• {name}:", color=col, fontsize=8.5, fontweight='bold')
            self.ax_side.text(0.38, y_pos, f"MCP: {mcp:4.1f}° | PIP: {pip:4.1f}°", color='#f1f5f9', fontsize=8)
            y_pos -= 0.045

        self.ax_side.axhline(y_pos + 0.01, color='#334155', linewidth=1.2)
        y_pos -= 0.035

        # Instrucciones
        self.ax_side.text(0.05, y_pos, "INTERACCIÓN 3D:", color='#94a3b8', fontsize=8, fontweight='bold')
        self.ax_side.text(0.05, y_pos - 0.035, "• Clic izq. + arrastrar: Orbitar 3D", color='#cbd5e1', fontsize=7.5)
        self.ax_side.text(0.05, y_pos - 0.065, "• Clic der. + arrastrar: Zoom / Escala", color='#cbd5e1', fontsize=7.5)
        self.ax_side.text(0.05, y_pos - 0.095, "• Rueda del ratón: Acercar / Alejar", color='#cbd5e1', fontsize=7.5)
        
        # Leyenda de abreviaturas
        self.ax_side.axhline(y_pos - 0.12, color='#334155', linewidth=1.0)
        y_pos -= 0.15
        self.ax_side.text(0.05, y_pos, "LEYENDA:", color='#94a3b8', fontsize=8, fontweight='bold')
        self.ax_side.text(0.05, y_pos - 0.035, "MCP: Articulación Base", color='#cbd5e1', fontsize=7.5)
        self.ax_side.text(0.05, y_pos - 0.065, "PIP: Articulación Media", color='#cbd5e1', fontsize=7.5)
        self.ax_side.text(0.05, y_pos - 0.095, "µs: Microsegundos (PWM)", color='#cbd5e1', fontsize=7.5)

    def show(self):
        plt.show()