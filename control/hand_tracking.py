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
            max_hands: Número máximo de manos a detectar
            confidence: Umbral de confianza
        """
        self.confidence = confidence
        
        # Rango HSV MEJORADO para detectar piel en diferentes iluminaciones
        # H: 0-20 (rojo oscuro) y 170-180 (rojo) para tonos cálidos
        # S: 10-255 (desde muy desaturado a muy saturado)
        # V: 40-255 (desde oscuro a brillante)
        self.lower_skin_1 = np.array([0, 10, 40], dtype=np.uint8)
        self.upper_skin_1 = np.array([20, 255, 255], dtype=np.uint8)
        
        self.lower_skin_2 = np.array([170, 10, 40], dtype=np.uint8)
        self.upper_skin_2 = np.array([180, 255, 255], dtype=np.uint8)
        
        # Para más compatibilidad: agregar rango de tonos más oscuros/claros
        self.lower_skin_3 = np.array([5, 20, 50], dtype=np.uint8)
        self.upper_skin_3 = np.array([25, 240, 210], dtype=np.uint8)

    def process_frame(self, frame: np.ndarray) -> Tuple[Optional[Dict], np.ndarray]:
        """
        Procesa un fotograma para detectar la mano.
        
        Args:
            frame: Imagen de OpenCV (BGR)
            
        Returns:
            (hand_data, annotated_frame)
        """
        # Aplicar CLAHE (Contrast Limited Adaptive Histogram Equalization)
        # para mejorar contraste en diferentes iluminaciones
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        gray = clahe.apply(gray)
        
        # Convertir a HSV
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Detectar piel con MÚLTIPLES rangos
        mask1 = cv2.inRange(hsv_frame, self.lower_skin_1, self.upper_skin_1)
        mask2 = cv2.inRange(hsv_frame, self.lower_skin_2, self.upper_skin_2)
        mask3 = cv2.inRange(hsv_frame, self.lower_skin_3, self.upper_skin_3)
        
        # Combinar máscaras
        mask = cv2.bitwise_or(mask1, mask2)
        mask = cv2.bitwise_or(mask, mask3)
        
        # Morfología agresiva para limpiar ruido
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
        
        # Dilatar para conectar componentes
        kernel2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.dilate(mask, kernel2, iterations=1)
        
        # Encontrar contornos
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        annotated_frame = frame.copy()
        hand_data = {"detected": False}
        
        if contours:
            # Encontrar el contorno más grande (la mano)
            largest_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest_contour)
            
            h, w = frame.shape[:2]
            min_area = (w * h) * 0.01  # Mínimo 1% del frame (menos restrictivo)
            max_area = (w * h) * 0.8   # Máximo 80% del frame
            
            if min_area < area < max_area:
                hand_data["detected"] = True
                hand_data["landmarks"] = {}
                hand_data["frame_size"] = (w, h)
                
                # Calcular hull
                hull = cv2.convexHull(largest_contour)
                hull_area = cv2.contourArea(hull)
                
                # Solidity (compactness) - qué tan "sólida" es la forma
                solidity = area / hull_area if hull_area > 0 else 0
                
                # Perímetro
                perimeter = cv2.arcLength(largest_contour, True)
                
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
                
                # Dibujar contorno en imagen anotada
                cv2.drawContours(annotated_frame, [largest_contour], 0, (0, 255, 0), 2)
                cv2.drawContours(annotated_frame, [hull], 0, (255, 0, 0), 2)
                
                # Estimar dedos por proporciones del contorno
                # Un dedo "puro" tiene perímetro-a-área ratio característico
                aspect_ratio = perimeter ** 2 / (4 * np.pi * area) if area > 0 else 0
                
                # Contour approximation para ver vértices
                epsilon = 0.03 * perimeter
                approx = cv2.approxPolyDP(largest_contour, epsilon, True)
                
                # Número de vértices ≈ número de dedos
                finger_count = len(approx)
                
                # Normalizar a rango 0-5
                finger_count = max(1, min(finger_count // 3, 5))
                
                hand_data["finger_count"] = finger_count
                hand_data["hand_area"] = area
                hand_data["solidity"] = solidity
                hand_data["perimeter"] = perimeter
                hand_data["aspect_ratio"] = aspect_ratio
        
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
        Detecta gestos basado en propiedades de contorno de mano.
        
        Args:
            landmarks: Diccionario de datos de mano
            
        Returns:
            Nombre del gesto detectado
        """
        if not landmarks or not landmarks.get("detected"):
            return "NEUTRAL"
        
        hand_area = landmarks.get("hand_area", 0)
        finger_count = landmarks.get("finger_count", 0)
        solidity = landmarks.get("solidity", 0.5)
        perimeter = landmarks.get("perimeter", 0)
        
        # Lógica mejorada de detección de gestos
        
        # PUÑO: Área grande, solidity alta (forma compacta), pocos dedos visibles
        if solidity > 0.65 and finger_count <= 1:
            return "FIST"
        
        # MANO ABIERTA: Muchos dedos separados, perímetro grande, solidity media
        if finger_count >= 4 and solidity < 0.55:
            return "OPEN_PALM"
        
        # PINZA: 2-3 dedos, solidity media-alta
        if 2 <= finger_count <= 3 and solidity > 0.60:
            return "PINCH"
        
        # SEÑALAR: 1 dedo extendido, perímetro pequeño relativo
        if finger_count == 1 and solidity > 0.70:
            return "POINTING"
        
        # Por defecto
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
