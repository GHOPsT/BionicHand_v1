"""
Aplicación Desktop para BionicHand con captura de cámara y rastreo de mano.
Interfaz PyQt5 con 2 paneles: Cámara + Visualización 3D
"""

import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QComboBox, QPushButton, QSlider, QFrame, QGridLayout,
    QSpinBox, QCheckBox
)
from PyQt5.QtGui import QImage, QPixmap, QFont
from PyQt5.QtCore import Qt, QTimer, QThread
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D

from core.hand import BionicHand
from control.hand_tracking import HandTrackingThread, HandTracker
from control.poses import HAND_POSES


class Hand3DCanvas(FigureCanvas):
    """Widget de Matplotlib para visualización 3D de la mano."""
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = self.fig.add_subplot(111, projection='3d')
        super().__init__(self.fig)
        self.setParent(parent)
        
        self.hand = BionicHand()
        self.setup_plot()
    
    def setup_plot(self):
        """Configura la visualización 3D inicial."""
        self.ax.set_xlabel('X (mm)')
        self.ax.set_ylabel('Y (mm)')
        self.ax.set_zlabel('Z (mm)')
        self.ax.set_title('Mano Biónica 3D', fontsize=14, weight='bold')
        
        # Límites de visualización
        self.ax.set_xlim(-50, 150)
        self.ax.set_ylim(-60, 60)
        self.ax.set_zlim(-20, 100)
        
        self.fig.tight_layout()
    
    def update_hand_position(self, u_index, u_group, u_thumb):
        """Actualiza la posición de la mano y redibuja."""
        self.hand.set_actuators(u_index=u_index, u_group=u_group, u_thumb=u_thumb)
        self.ax.clear()
        
        # Dibujar palma
        self.draw_palm()
        
        # Dibujar dedos
        for finger in self.hand.fingers:
            self.draw_finger(finger)
        
        self.setup_plot()
        self.draw()
    
    def draw_finger(self, finger):
        """Dibuja un dedo como cilindro 3D."""
        pts_2d = finger.get_positions()  # Retorna (3, 2): [x, y]
        
        # Convertir a 3D agregando z=0
        pts = np.column_stack([pts_2d, np.zeros(len(pts_2d))])
        
        # Línea del dedo
        self.ax.plot(pts[:, 0], pts[:, 1], pts[:, 2], 'b-', linewidth=3)
        
        # Puntos de articulación
        self.ax.scatter(pts[:, 0], pts[:, 1], pts[:, 2], c='red', s=50)
    
    def draw_palm(self):
        """Dibuja la palma como estructura 3D."""
        # Vértices dorsales (11 puntos)
        palm_vertices = np.array([
            [0, 0, 0],        # Centro
            [20, -15, 0],     # Índice base
            [20, -5, 0],
            [20, 5, 0],
            [20, 15, 0],      # Meñique base
            [40, -15, 0],     # Dedos del medio
            [40, -5, 0],
            [40, 5, 0],
            [40, 15, 0],
            [60, -10, 0],     # Punta de dedos
            [60, 10, 0]
        ])
        
        self.ax.scatter(palm_vertices[:, 0], palm_vertices[:, 1], 
                       palm_vertices[:, 2], c='green', s=100, alpha=0.6)


class CameraFrame(QFrame):
    """Widget para mostrar video de cámara."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("border: 2px solid gray; background-color: black;")
        
        layout = QVBoxLayout()
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setMinimumSize(400, 300)
        layout.addWidget(self.label)
        self.setLayout(layout)
    
    def update_frame(self, frame_array):
        """Actualiza el frame mostrado."""
        if frame_array is None:
            return
        
        # Convertir a RGB
        frame_rgb = cv2.cvtColor(frame_array, cv2.COLOR_BGR2RGB)
        
        # Redimensionar a tamaño de widget
        h, w, ch = frame_rgb.shape
        frame_rgb = cv2.resize(frame_rgb, (400, 300))
        
        # Convertir a QImage
        bytes_per_line = 3 * 400
        q_image = QImage(frame_rgb.data, 400, 300, bytes_per_line, QImage.Format_RGB888)
        
        # Mostrar
        pixmap = QPixmap.fromImage(q_image)
        self.label.setPixmap(pixmap)


class BionicHandDesktopApp(QMainWindow):
    """Aplicación principal de escritorio para BionicHand."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BionicHand Desktop - Control por Cámara")
        self.setGeometry(100, 100, 1400, 700)
        
        # Variables de estado
        self.mode = "SLIDERS"  # SLIDERS, CAMERA, GESTURE
        self.u_index = 0.0
        self.u_group = 0.0
        self.u_thumb = 0.0
        
        # Inicializar hand y tracker
        self.hand = BionicHand()
        self.tracker = HandTracker()
        
        # Thread de captura de cámara
        self.camera_thread = HandTrackingThread(camera_id=0)
        self.camera_thread.start()
        
        # Timer para actualizar UI
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(30)  # 30ms = ~33 FPS
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz de usuario."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout()
        
        # === PANEL IZQUIERDO: CÁMARA ===
        left_layout = QVBoxLayout()
        
        camera_label = QLabel("CÁMARA EN VIVO")
        camera_label.setFont(QFont("Arial", 12, QFont.Bold))
        left_layout.addWidget(camera_label)
        
        self.camera_frame = CameraFrame()
        left_layout.addWidget(self.camera_frame)
        
        # Info de mano detectada
        self.hand_info_label = QLabel("Mano no detectada")
        self.hand_info_label.setStyleSheet("color: red;")
        left_layout.addWidget(self.hand_info_label)
        
        left_frame = QFrame()
        left_frame.setLayout(left_layout)
        
        # === PANEL DERECHO: MANO 3D + CONTROLES ===
        right_layout = QVBoxLayout()
        
        # Selector de modo
        mode_layout = QHBoxLayout()
        mode_label = QLabel("Modo Control:")
        mode_label.setFont(QFont("Arial", 11, QFont.Bold))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["SLIDERS", "CÁMARA", "GESTOS"])
        self.mode_combo.currentTextChanged.connect(self.on_mode_changed)
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.mode_combo)
        right_layout.addLayout(mode_layout)
        
        # Visualización 3D
        self.hand_3d = Hand3DCanvas(width=4.5, height=4, dpi=100)
        right_layout.addWidget(self.hand_3d)
        
        # === PANEL DE CONTROLES ===
        control_layout = QGridLayout()
        control_layout.setSpacing(10)
        
        # Sliders (visibles solo en modo SLIDERS)
        self.slider_index_label = QLabel("Índice: 0%")
        self.slider_index = QSlider(Qt.Horizontal)
        self.slider_index.setMinimum(0)
        self.slider_index.setMaximum(100)
        self.slider_index.sliderMoved.connect(self.on_slider_index_changed)
        self.slider_index.setValue(0)
        control_layout.addWidget(self.slider_index_label, 0, 0)
        control_layout.addWidget(self.slider_index, 0, 1)
        
        self.slider_group_label = QLabel("Grupo: 0%")
        self.slider_group = QSlider(Qt.Horizontal)
        self.slider_group.setMinimum(0)
        self.slider_group.setMaximum(100)
        self.slider_group.sliderMoved.connect(self.on_slider_group_changed)
        self.slider_group.setValue(0)
        control_layout.addWidget(self.slider_group_label, 1, 0)
        control_layout.addWidget(self.slider_group, 1, 1)
        
        self.slider_thumb_label = QLabel("Pulgar: 0%")
        self.slider_thumb = QSlider(Qt.Horizontal)
        self.slider_thumb.setMinimum(0)
        self.slider_thumb.setMaximum(100)
        self.slider_thumb.sliderMoved.connect(self.on_slider_thumb_changed)
        self.slider_thumb.setValue(0)
        control_layout.addWidget(self.slider_thumb_label, 2, 0)
        control_layout.addWidget(self.slider_thumb, 2, 1)
        
        # Botones de postura rápida
        posture_label = QLabel("Posturas Rápidas:")
        posture_label.setFont(QFont("Arial", 10, QFont.Bold))
        control_layout.addWidget(posture_label, 3, 0, 1, 2)
        
        postura_buttons = [
            ("ABIERTA", "OPEN"),
            ("PUÑO", "FIST"),
            ("PINZA", "PINCH"),
            ("SEÑALAR", "POINTING")
        ]
        
        for idx, (label, pose_name) in enumerate(postura_buttons):
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked, p=pose_name: self.set_posture(p))
            control_layout.addWidget(btn, 4 + idx // 2, idx % 2)
        
        # Telemetría
        telemetry_label = QLabel("TELEMETRÍA")
        telemetry_label.setFont(QFont("Arial", 10, QFont.Bold))
        control_layout.addWidget(telemetry_label, 6, 0, 1, 2)
        
        self.telemetry_text = QLabel(
            "PWM Índice: - µs\n"
            "PWM Grupo: - µs\n"
            "PWM Pulgar: - µs\n"
            "Gesto: NINGUNO"
        )
        self.telemetry_text.setStyleSheet("background-color: #f0f0f0; padding: 5px;")
        control_layout.addWidget(self.telemetry_text, 7, 0, 2, 2)
        
        right_layout.addLayout(control_layout)
        
        right_frame = QFrame()
        right_frame.setLayout(right_layout)
        
        # Agregar paneles a layout principal
        main_layout.addWidget(left_frame, 2)
        main_layout.addWidget(right_frame, 2)
        
        central_widget.setLayout(main_layout)
    
    def on_mode_changed(self, mode_text):
        """Cambia el modo de control."""
        self.mode = mode_text.replace(" ", "_").upper()
        
        # Mostrar/ocultar sliders según modo
        show_sliders = (self.mode == "SLIDERS")
        self.slider_index.setVisible(show_sliders)
        self.slider_index_label.setVisible(show_sliders)
        self.slider_group.setVisible(show_sliders)
        self.slider_group_label.setVisible(show_sliders)
        self.slider_thumb.setVisible(show_sliders)
        self.slider_thumb_label.setVisible(show_sliders)
    
    def on_slider_index_changed(self, value):
        """Callback del slider de índice."""
        self.u_index = value / 100.0
        self.slider_index_label.setText(f"Índice: {value}%")
        self.update_hand_visualization()
    
    def on_slider_group_changed(self, value):
        """Callback del slider de grupo."""
        self.u_group = value / 100.0
        self.slider_group_label.setText(f"Grupo: {value}%")
        self.update_hand_visualization()
    
    def on_slider_thumb_changed(self, value):
        """Callback del slider de pulgar."""
        self.u_thumb = value / 100.0
        self.slider_thumb_label.setText(f"Pulgar: {value}%")
        self.update_hand_visualization()
    
    def set_posture(self, pose_name):
        """Aplica una postura rápida."""
        if pose_name in HAND_POSES:
            u_idx, u_grp, u_thb = HAND_POSES[pose_name]
            self.u_index = u_idx
            self.u_group = u_grp
            self.u_thumb = u_thb
            
            # Actualizar sliders
            self.slider_index.setValue(int(u_idx * 100))
            self.slider_group.setValue(int(u_grp * 100))
            self.slider_thumb.setValue(int(u_thb * 100))
            
            self.update_hand_visualization()
    
    def update_ui(self):
        """Actualiza la UI principal."""
        # Obtener frame de cámara
        frame = self.camera_thread.get_frame()
        if frame is not None:
            self.camera_frame.update_frame(frame)
        
        # Obtener datos de mano
        hand_data = self.camera_thread.get_hand_data()
        
        if self.mode == "CÁMARA" and hand_data and hand_data.get("detected"):
            # Modo cámara: controlar mano por dedos
            landmarks = hand_data.get("landmarks")
            if landmarks:
                servo_vals = self.tracker.landmarks_to_servo_values(landmarks)
                self.u_index = np.clip(servo_vals["u_index"], 0, 1)
                self.u_group = np.clip(servo_vals["u_group"], 0, 1)
                self.u_thumb = np.clip(servo_vals["u_thumb"], 0, 1)
                
                # Actualizar sliders visualmente (sin activar callbacks)
                self.slider_index.blockSignals(True)
                self.slider_group.blockSignals(True)
                self.slider_thumb.blockSignals(True)
                
                self.slider_index.setValue(int(self.u_index * 100))
                self.slider_group.setValue(int(self.u_group * 100))
                self.slider_thumb.setValue(int(self.u_thumb * 100))
                
                self.slider_index.blockSignals(False)
                self.slider_group.blockSignals(False)
                self.slider_thumb.blockSignals(False)
                
                # Mostrar gesto
                gesture = self.tracker.detect_gesture(landmarks)
                
                self.hand_info_label.setText(
                    f"✓ Mano detectada ({hand_data['handedness']}) "
                    f"| Gesto: {gesture}"
                )
                self.hand_info_label.setStyleSheet("color: green;")
                
                self.update_hand_visualization()
                self.update_telemetry(gesture)
        
        elif self.mode == "GESTOS" and hand_data and hand_data.get("detected"):
            # Modo gestos: aplicar postura según gesto
            landmarks = hand_data.get("landmarks")
            if landmarks:
                gesture = self.tracker.detect_gesture(landmarks)
                
                # Mapear gestos a posturas
                gesture_to_posture = {
                    "FIST": "FIST",
                    "OPEN_PALM": "OPEN",
                    "PINCH": "PINCH",
                    "POINTING": "POINTING"
                }
                
                if gesture in gesture_to_posture:
                    self.set_posture(gesture_to_posture[gesture])
                
                self.hand_info_label.setText(
                    f"✓ Mano detectada | Gesto: {gesture}"
                )
                self.hand_info_label.setStyleSheet("color: green;")
        
        else:
            if hand_data and not hand_data.get("detected"):
                self.hand_info_label.setText("Mano no detectada - Apunta la cámara")
                self.hand_info_label.setStyleSheet("color: orange;")
            self.update_hand_visualization()
    
    def update_hand_visualization(self):
        """Actualiza la visualización 3D de la mano."""
        self.hand_3d.update_hand_position(self.u_index, self.u_group, self.u_thumb)
    
    def update_telemetry(self, gesture="NINGUNO"):
        """Actualiza la telemetría mostrada."""
        # Calcular PWM (1000-2000 µs)
        pwm_index = 1000 + self.u_index * 1000
        pwm_group = 1000 + self.u_group * 1000
        pwm_thumb = 1000 + self.u_thumb * 1000
        
        self.telemetry_text.setText(
            f"PWM Índice: {pwm_index:.0f} µs\n"
            f"PWM Grupo: {pwm_group:.0f} µs\n"
            f"PWM Pulgar: {pwm_thumb:.0f} µs\n"
            f"Gesto: {gesture}"
        )
    
    def closeEvent(self, event):
        """Limpia recursos al cerrar."""
        self.timer.stop()
        self.camera_thread.stop()
        self.camera_thread.join()
        super().closeEvent(event)


def main():
    app = QApplication(sys.argv)
    window = BionicHandDesktopApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
