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


class Hand3DCanvas(FigureCanvas):
    """Widget de Matplotlib para visualización 3D profesional de la mano."""
    
    def __init__(self, parent=None, width=6, height=5, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor='#1e222b')
        self.ax = self.fig.add_subplot(111, projection='3d', facecolor='#1e222b')
        super().__init__(self.fig)
        self.setParent(parent)
        
        self.hand = BionicHand()
        
        # Colores por dedo (similar a main.py)
        self.colors = {
            "Pulgar":  "#ef4444",
            "Índice":  "#3b82f6",
            "Medio":   "#10b981",
            "Anular":  "#f59e0b",
            "Meñique": "#8b5cf6"
        }
        
        self.finger_names = ["Índice", "Medio", "Anular", "Meñique", "Pulgar"]
        self.setup_plot()
    
    def setup_plot(self):
        """Configura la visualización 3D inicial."""
        self.ax.set_xlabel('X (mm)', color='#e2e8f0', fontsize=9)
        self.ax.set_ylabel('Y (mm)', color='#e2e8f0', fontsize=9)
        self.ax.set_zlabel('Z (mm)', color='#e2e8f0', fontsize=9)
        self.ax.set_title('Mano Biónica 3D', fontsize=13, weight='bold', color='#e2e8f0')
        
        # Límites de visualización
        self.ax.set_xlim(-80, 120)
        self.ax.set_ylim(-70, 70)
        self.ax.set_zlim(-20, 100)
        
        # Estilo oscuro
        self.ax.xaxis.pane.fill = False
        self.ax.yaxis.pane.fill = False
        self.ax.zaxis.pane.fill = False
        self.ax.grid(True, alpha=0.2)
        
        self.fig.tight_layout()
    
    def update_hand_position(self, u_index, u_group, u_thumb):
        """Actualiza la posición de la mano y redibuja."""
        self.hand.set_actuators(u_index=u_index, u_group=u_group, u_thumb=u_thumb)
        self.ax.clear()
        
        # Dibujar dedos con líneas y puntos
        for i, finger in enumerate(self.hand.fingers):
            self.draw_finger(finger, self.finger_names[i])
        
        self.setup_plot()
        self.draw()
    
    def draw_finger(self, finger, finger_name):
        """Dibuja un dedo como línea 3D con puntos de articulación."""
        pts_2d = finger.get_positions()  # (3, 2): P0, P1, P2
        
        # Convertir a 3D con z pequeño
        pts = np.column_stack([pts_2d, np.zeros(len(pts_2d))])
        
        # Línea del dedo con color
        color = self.colors.get(finger_name, "#cccccc")
        self.ax.plot(pts[:, 0], pts[:, 1], pts[:, 2], 
                    color=color, linewidth=4, alpha=0.8)
        
        # Puntos de articulación
        self.ax.scatter(pts[:, 0], pts[:, 1], pts[:, 2], 
                       color=color, s=80, alpha=0.9, edgecolors='white', linewidth=1)
    
    def draw_palm(self):
        """Dibuja la palma (opcional)."""
        # Centro de palma
        palm_center = np.array([0, 0, 0])
        self.ax.scatter(*palm_center, color='#14b8a6', s=200, alpha=0.6, 
                       edgecolors='white', linewidth=1)


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
        """Loop principal de actualización."""
        # Obtener frame de cámara
        frame = self.camera_thread.get_frame()
        hand_data = self.camera_thread.get_hand_data()
        
        if frame is not None and self.mode in ["CÁMARA", "GESTOS"]:
            # Mostrar frame
            self.camera_display.update_frame(frame)
            
            # Procesar datos de mano
            if hand_data and hand_data.get("detected"):
                self.hand_status_label.setText("✓ Mano detectada")
                self.hand_status_label.setStyleSheet("color: #51cf66; font-weight: bold;")
                
                # En modo CÁMARA: mapear hand_data a servo values
                if self.mode == "CÁMARA":
                    servo_vals = self.tracker.landmarks_to_servo_values(hand_data)
                    self.u_index = servo_vals.get("u_index", 0.0)
                    self.u_group = servo_vals.get("u_group", 0.0)
                    self.u_thumb = servo_vals.get("u_thumb", 0.0)
                    
                    # Mostrar gesture detectado
                    gesture = self.tracker.detect_gesture(hand_data)
                    self.hand_info_label.setText(f"Gesto: {gesture}")
                    
                    self.update_hand_visualization()
            else:
                self.hand_status_label.setText("✗ Mano no detectada")
                self.hand_status_label.setStyleSheet("color: #ff6b6b; font-weight: bold;")
                self.hand_info_label.setText("")


def main():
    app = QApplication(sys.argv)
    window = BionicHandDesktopApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
