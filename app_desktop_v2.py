"""
Aplicación Desktop para BionicHand con captura de cámara y rastreo de mano.
Versión 2: UI dinámico, detección de mano mejorada, visualización 3D profesional.

Modos:
- SLIDERS: Solo controles manuales (sin cámara)
- CÁMARA: Detección automática de mano (sin sliders)
- GESTOS: Reconocimiento de gestos predefinidos

NOTA: Esta es una versión LOCAL DE DESARROLLO.
Mantiene main.py y app_streamlit.py intactos.
"""

import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QComboBox, QPushButton, QSlider, QFrame, QGridLayout
)
from PyQt5.QtGui import QImage, QPixmap, QFont, QColor
from PyQt5.QtCore import Qt, QTimer, QThread
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from core.hand import BionicHand
from control.hand_tracking import HandTrackingThread, HandTracker
from control.poses import HAND_POSES
from config.dimensions import FINGER_DIMENSIONS, JOINT_LIMITS, COUPLING_RATIO_4BAR


class Hand3DCanvas(FigureCanvas):
    """Widget de Matplotlib para visualización 3D profesional de la mano (como visualizer.py)."""
    
    def __init__(self, parent=None, width=6, height=5, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor='#1e222b')
        self.ax = self.fig.add_subplot(111, projection='3d', facecolor='#1e222b')
        super().__init__(self.fig)
        self.setParent(parent)
        
        self.hand = BionicHand()
        
        # Colores profesionales por dedo (match visualizer.py)
        self.colors = {
            "Pulgar":  {"main": "#ef4444", "joint": "#b91c1c", "pad": "#fca5a5"},
            "Índice":  {"main": "#3b82f6", "joint": "#1d4ed8", "pad": "#93c5fd"},
            "Medio":   {"main": "#10b981", "joint": "#047857", "pad": "#6ee7b7"},
            "Anular":  {"main": "#f59e0b", "joint": "#b45309", "pad": "#fde68a"},
            "Meñique": {"main": "#8b5cf6", "joint": "#6d28d9", "pad": "#c4b5fd"}
        }
        
        self.finger_names = ["Pulgar", "Índice", "Medio", "Anular", "Meñique"]
        
        # Parámetros de visualización
        self.cylinder_radius_proximal = 4.5
        self.cylinder_radius_distal = 4.0
        self.sphere_radius_base = 3.5
        self.sphere_radius_joint = 3.0
        self.sphere_radius_tip = 4.5
        self.alpha_cylinders = 0.88
        self.alpha_joints = 0.92
        self.alpha_tips = 0.85
        
        self.setup_plot()
    
    def setup_plot(self):
        """Configura la visualización 3D inicial."""
        self.ax.set_xlabel('X (mm) [Transversal]', color='#94a3b8', fontsize=8)
        self.ax.set_ylabel('Y (mm) [Longitudinal]', color='#94a3b8', fontsize=8)
        self.ax.set_zlabel('Z (mm) [Palmar]', color='#94a3b8', fontsize=8)
        self.ax.set_title('Mano Biónica 3D', fontsize=13, weight='bold', color='#e2e8f0')
        
        # Límites (similar a visualizer.py)
        self.ax.set_xlim(-45, 85)
        self.ax.set_ylim(-15, 160)
        self.ax.set_zlim(-20, 85)
        
        # Estilo oscuro
        self.ax.xaxis.pane.fill = False
        self.ax.yaxis.pane.fill = False
        self.ax.zaxis.pane.fill = False
        self.ax.grid(True, alpha=0.2)
        self.ax.tick_params(colors='#64748b', labelsize=7)
        
        self.fig.tight_layout()
    
    def update_hand_position(self, u_index, u_group, u_thumb):
        """Actualiza la posición de la mano y redibuja."""
        self.hand.set_actuators(u_index=u_index, u_group=u_group, u_thumb=u_thumb)
        self.ax.clear()
        
        # Dibujar palma 3D
        self.draw_palm_3d()
        
        # Dibujar dedos con cilindros 3D
        for i, finger_name in enumerate(self.finger_names):
            finger = self.hand.fingers[i]
            self.draw_finger_3d(finger, finger_name)
        
        self.setup_plot()
        self.draw()
    
    def draw_palm_3d(self):
        """Dibuja la palma volumétrica 3D (igual a visualizer.py)."""
        # Puntos superiores del dorso
        top_pts = [
            [-20.0, 45.0, 5],
            [-25.0, 26.0, 8],
            [-10.0, 50.0, 3],
            [0, 68, 2],
            [20.8, 72, 2],
            [41.4, 69, 2],
            [62.9, 62, 3],
            [70.0, 40.0, 4],
            [65.0, 15.0, 6],
            [30.0, -5.0, 5],
            [-15.0, -5.0, 5]
        ]

        # Puntos inferiores (lado de la palma, 12mm debajo)
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

        # Dibujar palma volumétrica
        palm_poly = Poly3DCollection(faces, alpha=0.50, facecolor='#c8bda8', 
                                    edgecolor='#6e6350', linewidths=1.5)
        self.ax.add_collection3d(palm_poly)
    
    def draw_finger_3d(self, finger, finger_name):
        """Dibuja un dedo con geometría 3D idéntica a visualizer.py."""
        from config.dimensions import (
            FINGER_DIMENSIONS, JOINT_LIMITS, COUPLING_RATIO_4BAR, PALM_SPACING
        )
        
        # Obtener dimensiones del dedo
        name_key = {
            "Pulgar": "thumb",
            "Índice": "index", 
            "Medio": "middle",
            "Anular": "ring",
            "Meñique": "pinky"
        }[finger_name]
        
        d = FINGER_DIMENSIONS[name_key]
        l1, l2 = d["l1_proximal"], d["l2_distal"]
        
        if finger_name == "Pulgar":
            # ===== PULGAR CON OPOSICIÓN 3D =====
            u = self.hand.servo_thumb.command
            mcp_max = JOINT_LIMITS["thumb_base_flexion"][1]
            pip_max = JOINT_LIMITS["thumb_pip_flexion"][1]
            t1_deg = u * mcp_max
            t2_deg = u * 0.90 * pip_max
            
            t1 = np.radians(t1_deg)
            phi = np.radians(t1_deg + t2_deg)
            origin = np.array([-12.0, 20.0, 9.0])
            
            # Vector oposición 3D
            v1 = np.array([
                -l1 * np.cos(t1) * 0.7 + 0.6 * l1 * np.sin(t1),
                 l1 * np.cos(t1) * 0.7 - 0.2 * l1 * np.sin(t1),
                 l1 * 0.2 + l1 * np.sin(t1) * 0.8
            ])
            p1 = origin + v1
            
            # Segunda falange
            v2 = np.array([
                -l2 * 0.5 * np.cos(phi) + 0.7 * l2 * np.sin(phi),
                 l2 * np.cos(phi) * 0.6 - 0.4 * l2 * np.sin(phi),
                 l2 * 0.2 + l2 * np.sin(phi) * 0.9
            ])
            p2 = p1 + v2
            
            pts = np.array([origin, p1, p2])
        
        else:
            # ===== DEDOS NORMALES (Índice, Medio, Anular, Meñique) =====
            u = self.hand.servo_index.command if finger_name == "Índice" else self.hand.servo_group.command
            mcp_max = JOINT_LIMITS["mcp_base_flexion"][1]
            pip_max = JOINT_LIMITS["pip_middle_flexion"][1]
            t1_deg = u * mcp_max
            t2_deg = u * COUPLING_RATIO_4BAR * pip_max
            
            t1 = np.radians(t1_deg)
            phi = np.radians(t1_deg + t2_deg)
            
            # Origen en la base de cada dedo en la palma
            x_offsets = {
                "Índice": 0.0,
                "Medio": PALM_SPACING["index_to_middle"],
                "Anular": PALM_SPACING["index_to_middle"] + PALM_SPACING["middle_to_ring"],
                "Meñique": PALM_SPACING["index_to_middle"] + PALM_SPACING["middle_to_ring"] + PALM_SPACING["ring_to_pinky"]
            }
            y_offsets = {"Índice": 68.0, "Medio": 72.0, "Anular": 69.0, "Meñique": 62.0}
            origin = np.array([x_offsets[finger_name], y_offsets[finger_name], 0.0])
            
            # Flexión: hacia adelante (+Z) y cierre hacia atrás (-Y)
            # p1 = origin + [0, l1*cos(t1), l1*sin(t1)]
            # p2 = p1 + [0, l2*cos(phi), l2*sin(phi)]
            p1 = origin + np.array([0.0, l1 * np.cos(t1), l1 * np.sin(t1)])
            p2 = p1 + np.array([0.0, l2 * np.cos(phi), l2 * np.sin(phi)])
            
            pts = np.array([origin, p1, p2])
        
        c = self.colors[finger_name]
        
        # Dibujar cilindros entre articulaciones
        if len(pts) >= 3:
            self._draw_cylinder(pts[0], pts[1], self.cylinder_radius_proximal, 
                              c["main"], self.alpha_cylinders)
            self._draw_cylinder(pts[1], pts[2], self.cylinder_radius_distal, 
                              c["main"], self.alpha_cylinders)
            
            # Esferas articulares
            self._draw_sphere(pts[0], self.sphere_radius_base, c["joint"], self.alpha_joints)
            self._draw_sphere(pts[1], self.sphere_radius_joint, c["joint"], self.alpha_joints)
            self._draw_sphere(pts[2], self.sphere_radius_tip, c["pad"], self.alpha_tips)

    
    def _draw_cylinder(self, p1: np.ndarray, p2: np.ndarray, radius: float, color: str, alpha: float):
        """Dibuja un cilindro volumétrico entre dos puntos."""
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
        
        # Círculos en los extremos
        angles = np.linspace(0, 2*np.pi, 12)
        circle1 = p1[:, None] + radius * (perp1[:, None] * np.cos(angles) + perp2[:, None] * np.sin(angles))
        circle2 = p2[:, None] + radius * (perp1[:, None] * np.cos(angles) + perp2[:, None] * np.sin(angles))
        
        # Crear caras laterales
        faces = []
        for i in range(len(angles)-1):
            face = [circle1[:, i].tolist(), circle1[:, i+1].tolist(), 
                   circle2[:, i+1].tolist(), circle2[:, i].tolist()]
            faces.append(face)
        
        # Tapas
        faces.append(circle1.T.tolist())
        faces.append(circle2.T.tolist())
        
        cyl = Poly3DCollection(faces, alpha=alpha, facecolor=color, edgecolor='#0f172a', linewidths=0.5)
        self.ax.add_collection3d(cyl)
    
    def _draw_sphere(self, center: np.ndarray, radius: float, color: str, alpha: float):
        """Dibuja una esfera 3D."""
        u = np.linspace(0, 2 * np.pi, 8)
        v = np.linspace(0, np.pi, 6)
        x = radius * np.outer(np.cos(u), np.sin(v)) + center[0]
        y = radius * np.outer(np.sin(u), np.sin(v)) + center[1]
        z = radius * np.outer(np.ones(np.size(u)), np.cos(v)) + center[2]
        self.ax.plot_surface(x, y, z, color=color, alpha=alpha, edgecolor='#ffffff', linewidth=0.3)


class CameraFrame(QFrame):
    """Widget para mostrar video de cámara con detección de mano."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("border: 2px solid #666; background-color: #000;")
        
        layout = QVBoxLayout()
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setMinimumSize(500, 375)  # 4:3 ratio
        self.label.setStyleSheet("background-color: #000;")
        layout.addWidget(self.label)
        self.setLayout(layout)
    
    def update_frame(self, frame_array, hand_detected=False):
        """Actualiza el frame mostrado."""
        if frame_array is None:
            return
        
        # Convertir a RGB
        frame_rgb = cv2.cvtColor(frame_array, cv2.COLOR_BGR2RGB)
        frame_rgb = cv2.resize(frame_rgb, (500, 375))
        
        # Convertir a QImage
        bytes_per_line = 3 * 500
        q_image = QImage(frame_rgb.data, 500, 375, bytes_per_line, QImage.Format_RGB888)
        
        # Mostrar
        pixmap = QPixmap.fromImage(q_image)
        self.label.setPixmap(pixmap)


class BionicHandDesktopApp(QMainWindow):
    """Aplicación principal de escritorio para BionicHand (Versión 2 - LOCAL)."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BionicHand Desktop - Control Local (DEV)")
        self.setGeometry(100, 100, 1500, 750)
        
        # Variables de estado
        self.mode = "SLIDERS"
        self.u_index = 0.0
        self.u_group = 0.0
        self.u_thumb = 0.0
        
        # Inicializar componentes
        self.hand = BionicHand()
        self.tracker = HandTracker()
        
        # Thread de cámara
        self.camera_thread = HandTrackingThread(camera_id=0)
        self.camera_thread.start()
        
        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(30)  # 30ms = ~33 FPS
        
        # Central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz de usuario."""
        main_layout = QVBoxLayout()
        
        # === BARRA SUPERIOR: Selector de Modo ===
        top_layout = QHBoxLayout()
        mode_label = QLabel("Modo Control:")
        mode_label.setFont(QFont("Arial", 11, QFont.Bold))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["SLIDERS", "CÁMARA", "GESTOS"])
        self.mode_combo.currentTextChanged.connect(self.on_mode_changed)
        self.mode_combo.setMaximumWidth(150)
        top_layout.addWidget(mode_label)
        top_layout.addWidget(self.mode_combo)
        top_layout.addStretch()
        main_layout.addLayout(top_layout)
        
        # === CONTENEDOR PRINCIPAL (cambiará según modo) ===
        self.content_layout = QHBoxLayout()
        main_layout.addLayout(self.content_layout)
        
        # Crear widgets de cada modo
        self._create_sliders_view()
        self._create_camera_view()
        self._create_hand_visualization()
        
        # Mostrar vista inicial (SLIDERS)
        self.show_sliders_mode()
        
        self.central_widget.setLayout(main_layout)
    
    def _create_sliders_view(self):
        """Crea el panel de sliders (solo para modo SLIDERS)."""
        self.sliders_frame = QFrame()
        layout = QVBoxLayout()
        
        # Título
        title = QLabel("Control Manual de Servomotores")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)
        
        # Slider Índice
        label_idx = QLabel("Servo 1 - Índice:")
        label_idx.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(label_idx)
        self.slider_index = QSlider(Qt.Horizontal)
        self.slider_index.setMinimum(0)
        self.slider_index.setMaximum(100)
        self.slider_index.sliderMoved.connect(self.on_slider_index_changed)
        self.slider_index_label = QLabel("0%")
        layout.addWidget(self.slider_index)
        layout.addWidget(self.slider_index_label)
        
        # Slider Grupo
        label_grp = QLabel("Servo 2 - Grupo (Med, Anu, Meñ):")
        label_grp.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(label_grp)
        self.slider_group = QSlider(Qt.Horizontal)
        self.slider_group.setMinimum(0)
        self.slider_group.setMaximum(100)
        self.slider_group.sliderMoved.connect(self.on_slider_group_changed)
        self.slider_group_label = QLabel("0%")
        layout.addWidget(self.slider_group)
        layout.addWidget(self.slider_group_label)
        
        # Slider Pulgar
        label_thb = QLabel("Servo 3 - Pulgar:")
        label_thb.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(label_thb)
        self.slider_thumb = QSlider(Qt.Horizontal)
        self.slider_thumb.setMinimum(0)
        self.slider_thumb.setMaximum(100)
        self.slider_thumb.sliderMoved.connect(self.on_slider_thumb_changed)
        self.slider_thumb_label = QLabel("0%")
        layout.addWidget(self.slider_thumb)
        layout.addWidget(self.slider_thumb_label)
        
        layout.addSpacing(20)
        
        # Botones de postura
        label_postura = QLabel("Posturas Rápidas:")
        label_postura.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(label_postura)
        
        postures = [("🖐️ ABIERTA", "OPEN"), ("✊ PUÑO", "FIST"), 
                    ("🤏 PINZA", "PINCH"), ("☝️ SEÑALAR", "POINTING")]
        
        for label, pose in postures:
            btn = QPushButton(label)
            btn.setMinimumHeight(40)
            btn.setFont(QFont("Arial", 10, QFont.Bold))
            btn.clicked.connect(lambda checked, p=pose: self.set_posture(p))
            layout.addWidget(btn)
        
        layout.addStretch()
        self.sliders_frame.setLayout(layout)
    
    def _create_camera_view(self):
        """Crea el panel de cámara (para modo CÁMARA y GESTOS)."""
        self.camera_frame = QFrame()
        layout = QVBoxLayout()
        
        # Título
        title = QLabel("Detección de Mano en Vivo")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)
        
        # Video
        self.camera_display = CameraFrame()
        layout.addWidget(self.camera_display)
        
        # Status
        self.hand_status_label = QLabel("Mano no detectada")
        self.hand_status_label.setStyleSheet("color: #ff6b6b; font-weight: bold;")
        layout.addWidget(self.hand_status_label)
        
        # Info de mano
        self.hand_info_label = QLabel("")
        self.hand_info_label.setStyleSheet("color: #e2e8f0; font-size: 10px;")
        layout.addWidget(self.hand_info_label)
        
        self.camera_frame.setLayout(layout)
    
    def _create_hand_visualization(self):
        """Crea el panel de visualización 3D."""
        self.hand_3d = Hand3DCanvas(width=6, height=5, dpi=100)
    
    def show_sliders_mode(self):
        """Muestra solo sliders + mano 3D."""
        # Limpiar layout
        while self.content_layout.count():
            self.content_layout.takeAt(0).widget().setParent(None)
        
        # Agregar sliders a la izquierda
        self.content_layout.addWidget(self.sliders_frame, 1)
        
        # Agregar mano 3D a la derecha
        self.content_layout.addWidget(self.hand_3d, 2)
    
    def show_camera_mode(self):
        """Muestra solo cámara + mano 3D."""
        # Limpiar layout
        while self.content_layout.count():
            self.content_layout.takeAt(0).widget().setParent(None)
        
        # Agregar cámara a la izquierda
        self.content_layout.addWidget(self.camera_frame, 1)
        
        # Agregar mano 3D a la derecha
        self.content_layout.addWidget(self.hand_3d, 2)
    
    def on_mode_changed(self, mode_text):
        """Cambia entre modos."""
        self.mode = mode_text.strip()
        
        if self.mode == "SLIDERS":
            self.show_sliders_mode()
        elif self.mode == "CÁMARA":
            self.show_camera_mode()
        elif self.mode == "GESTOS":
            self.show_camera_mode()
    
    def on_slider_index_changed(self, value):
        self.u_index = value / 100.0
        self.slider_index_label.setText(f"{value}%")
        self.update_hand_visualization()
    
    def on_slider_group_changed(self, value):
        self.u_group = value / 100.0
        self.slider_group_label.setText(f"{value}%")
        self.update_hand_visualization()
    
    def on_slider_thumb_changed(self, value):
        self.u_thumb = value / 100.0
        self.slider_thumb_label.setText(f"{value}%")
        self.update_hand_visualization()
    
    def set_posture(self, posture_name):
        """Aplica una postura predefinida."""
        if posture_name in HAND_POSES:
            u_idx, u_grp, u_thb = HAND_POSES[posture_name]
            
            self.u_index = u_idx
            self.u_group = u_grp
            self.u_thumb = u_thb
            
            self.slider_index.setValue(int(u_idx * 100))
            self.slider_group.setValue(int(u_grp * 100))
            self.slider_thumb.setValue(int(u_thb * 100))
            
            self.update_hand_visualization()
    
    def update_hand_visualization(self):
        """Actualiza la visualización 3D de la mano."""
        self.hand_3d.update_hand_position(self.u_index, self.u_group, self.u_thumb)
    
    def update_ui(self):
        """Loop principal de actualización cada 30ms."""
        # Obtener frame de cámara
        frame = self.camera_thread.get_frame()
        hand_data = self.camera_thread.get_hand_data()
        
        if frame is not None and self.mode in ["CÁMARA", "GESTOS"]:
            # Mostrar frame de cámara
            self.camera_display.update_frame(frame)
            
            # Procesar datos de mano
            if hand_data and hand_data.get("detected"):
                self.hand_status_label.setText("✓ Mano detectada")
                self.hand_status_label.setStyleSheet("color: #51cf66; font-weight: bold;")
                
                # En modo CÁMARA: mapear hand_data a servo values continuamente
                if self.mode == "CÁMARA":
                    servo_vals = self.tracker.landmarks_to_servo_values(hand_data)
                    self.u_index = servo_vals.get("u_index", 0.0)
                    self.u_group = servo_vals.get("u_group", 0.0)
                    self.u_thumb = servo_vals.get("u_thumb", 0.0)
                    
                    # Mostrar gesture detectado
                    gesture = self.tracker.detect_gesture(hand_data)
                    self.hand_info_label.setText(f"Gesto: {gesture}")
            else:
                self.hand_status_label.setText("✗ Mano no detectada")
                self.hand_status_label.setStyleSheet("color: #ff6b6b; font-weight: bold;")
                self.hand_info_label.setText("")
        
        # Actualizar visualización 3D SIEMPRE (modo CÁMARA y SLIDERS)
        if self.mode in ["CÁMARA", "GESTOS"]:
            self.update_hand_visualization()


def main():
    app = QApplication(sys.argv)
    window = BionicHandDesktopApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
