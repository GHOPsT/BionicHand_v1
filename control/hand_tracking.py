"""
Módulo de rastreo de mano en tiempo real usando OpenCV.
Detecta mano por contorno de piel y mapea a gestos simples.
"""

import cv2
import numpy as np
from typing import Tuple, Dict, List, Optional
import threading
from queue import Queue


class HandTracker:
    """
    Rastreador de mano simplificado usando OpenCV.
    Detecta mano por contorno de piel y mapea a ángulos de servomotor.
    """

    def __init__(self, max_hands=1, confidence=0.7):
        """
        Inicializa el rastreador de mano.
        
        Args:
            max_hands: Número máximo de manos a detectar (no usado en esta versión)
            confidence: Umbral de confianza (no usado en esta versión)
        """
        self.confidence = confidence
        
        # Rango HSV para detectar piel
        self.lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        self.upper_skin = np.array([20, 255, 255], dtype=np.uint8)

    def process_frame(self, frame: np.ndarray) -> Tuple[Optional[Dict], np.ndarray]:
        """
        Procesa un fotograma para detectar la mano.
        
        Args:
            frame: Imagen de OpenCV (BGR)
            
        Returns:
            (hand_data, annotated_frame)
        """
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Detectar piel
        mask = cv2.inRange(hsv_frame, self.lower_skin, self.upper_skin)
        
        # Morfología para limpiar
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        # Encontrar contornos
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        annotated_frame = frame.copy()
        hand_data = {"detected": False}
        
        if contours:
            # Encontrar el contorno más grande (la mano)
            largest_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest_contour)
            
            h, w = frame.shape[:2]
            min_area = (w * h) * 0.02  # Mínimo 2% del frame
            
            if area > min_area:
                hand_data["detected"] = True
                hand_data["landmarks"] = {}
                hand_data["frame_size"] = (w, h)
                
                # Calcular convex hull
                hull = cv2.convexHull(largest_contour)
                hull_area = cv2.contourArea(hull)
                
                # Solidity (compactness)
                solidity = area / hull_area if hull_area > 0 else 0
                
                # Momentos para centroide
                M = cv2.moments(largest_contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    hand_data["landmarks"][0] = {
                        "x": cx / w,
                        "y": cy / h,
                        "z": 0.5,
                        "pixel_x": cx,
                        "pixel_y": cy
                    }
                
                # Dibujar contorno
                cv2.drawContours(annotated_frame, [largest_contour], 0, (0, 255, 0), 2)
                cv2.drawContours(annotated_frame, [hull], 0, (255, 0, 0), 2)
                
                # Estimar cantidad de dedos por área del contorno
                perimeter = cv2.arcLength(largest_contour, True)
                finger_count = max(1, int((perimeter / 50)))  # Estimación simple
                
                hand_data["finger_count"] = min(finger_count, 5)  # Máximo 5 dedos
                hand_data["hand_area"] = area
                hand_data["solidity"] = solidity
        
        return hand_data, annotated_frame

    def get_finger_angles(self, landmarks: Dict) -> Dict[str, float]:
        """Retorna ángulos de flexión simulados (no usa landmarks reales)."""
        # Para versión simplificada, retornar valores por defecto
        return {
            "INDEX": {"mcp_normalized": 0.5, "pip_normalized": 0.4},
            "MIDDLE": {"mcp_normalized": 0.4, "pip_normalized": 0.3},
            "RING": {"mcp_normalized": 0.4, "pip_normalized": 0.3},
            "PINKY": {"mcp_normalized": 0.3, "pip_normalized": 0.2},
            "THUMB": {"mcp_normalized": 0.3}
        }

    def detect_gesture(self, landmarks: Dict) -> str:
        """
        Detecta gestos basado en área de mano.
        
        Args:
            landmarks: Diccionario de datos de mano
            
        Returns:
            Nombre del gesto detectado
        """
        hand_area = landmarks.get("hand_area", 0)
        finger_count = landmarks.get("finger_count", 0)
        solidity = landmarks.get("solidity", 0)
        
        # Lógica simple de detección de gestos
        if finger_count <= 1 and solidity > 0.7:
            return "FIST"
        elif finger_count >= 4 and solidity < 0.6:
            return "OPEN_PALM"
        elif finger_count == 2 and solidity > 0.65:
            return "PINCH"
        elif finger_count == 1:
            return "POINTING"
        else:
            return "NEUTRAL"

    def landmarks_to_servo_values(self, landmarks: Dict) -> Dict[str, float]:
        """
        Mapea datos de mano a valores de servomotor.
        
        Args:
            landmarks: Diccionario de datos de mano
            
        Returns:
            Valores normalizados: {u_index, u_group, u_thumb}
        """
        gesture = self.detect_gesture(landmarks)
        
        # Mapear gestos a valores servo
        gesture_servo_map = {
            "FIST": {"u_index": 0.95, "u_group": 0.95, "u_thumb": 0.90},
            "OPEN_PALM": {"u_index": 0.0, "u_group": 0.0, "u_thumb": 0.0},
            "PINCH": {"u_index": 0.75, "u_group": 0.0, "u_thumb": 0.85},
            "POINTING": {"u_index": 0.0, "u_group": 1.0, "u_thumb": 0.90},
            "NEUTRAL": {"u_index": 0.4, "u_group": 0.3, "u_thumb": 0.3}
        }
        
        return gesture_servo_map.get(gesture, {"u_index": 0.0, "u_group": 0.0, "u_thumb": 0.0})

    def release(self):
        """Libera recursos."""
        pass


class HandTrackingThread(threading.Thread):
    """
    Thread para captura y procesamiento de video en tiempo real.
    Evita bloquear la GUI.
    """
    
    def __init__(self, camera_id=0):
        super().__init__(daemon=True)
        self.camera_id = camera_id
        self.tracker = HandTracker()
        self.cap = None
        self.running = False
        self.frame_queue = Queue(maxsize=1)
        self.hand_data_queue = Queue(maxsize=1)
        
    def run(self):
        """Loop principal de captura."""
        self.cap = cv2.VideoCapture(self.camera_id)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        self.running = True
        
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            # Procesar frame
            hand_data, annotated_frame = self.tracker.process_frame(frame)
            
            # Enviar a colas (descartar si están llenas)
            try:
                self.frame_queue.put_nowait(annotated_frame)
            except:
                pass
            
            try:
                self.hand_data_queue.put_nowait(hand_data)
            except:
                pass
    
    def stop(self):
        """Detiene el thread."""
        self.running = False
        if self.cap:
            self.cap.release()
        self.tracker.release()
    
    def get_frame(self) -> Optional[np.ndarray]:
        """Obtiene el último frame procesado."""
        try:
            return self.frame_queue.get_nowait()
        except:
            return None
    
    def get_hand_data(self) -> Optional[Dict]:
        """Obtiene los últimos datos de mano."""
        try:
            return self.hand_data_queue.get_nowait()
        except:
            return None
