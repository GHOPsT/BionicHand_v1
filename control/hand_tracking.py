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
        Inicializa el rastreador de mano con rangos HSV mejorados.
        
        Args:
            max_hands: Número máximo de manos a detectar
            confidence: Umbral de confianza
        """
        self.confidence = confidence
        
        # RANGOS HSV CALIBRADOS para tu iluminación específica
        # Valores optimizados mediante calibrate_hsv.py
        
        # Rango Calibrado Principal: H(0-23), S(45-158), V(127-211)
        self.lower_skin_1 = np.array([0, 45, 127], dtype=np.uint8)
        self.upper_skin_1 = np.array([23, 158, 211], dtype=np.uint8)
        
        # Rango 2: Variación +/- 2 en H para capturar bordes
        self.lower_skin_2 = np.array([0, 40, 120], dtype=np.uint8)
        self.upper_skin_2 = np.array([25, 165, 220], dtype=np.uint8)
        
        # Rango 3: Sensibilidad extra en S (más permisivo)
        self.lower_skin_3 = np.array([0, 35, 115], dtype=np.uint8)
        self.upper_skin_3 = np.array([25, 170, 225], dtype=np.uint8)
        
        # Rango 4: Más permisivo en V (capturar sombras)
        self.lower_skin_4 = np.array([0, 45, 100], dtype=np.uint8)
        self.upper_skin_4 = np.array([25, 160, 230], dtype=np.uint8)

    def process_frame(self, frame: np.ndarray) -> Tuple[Optional[Dict], np.ndarray]:
        """
        Procesa un fotograma para detectar la mano.
        
        Args:
            frame: Imagen de OpenCV (BGR)
            
        Returns:
            (hand_data, annotated_frame)
        """
        # Aplicar CLAHE para mejorar contraste
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        gray = clahe.apply(gray)
        
        # Convertir a HSV
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Detectar piel con MÚLTIPLES rangos (4 en total)
        mask1 = cv2.inRange(hsv_frame, self.lower_skin_1, self.upper_skin_1)
        mask2 = cv2.inRange(hsv_frame, self.lower_skin_2, self.upper_skin_2)
        mask3 = cv2.inRange(hsv_frame, self.lower_skin_3, self.upper_skin_3)
        mask4 = cv2.inRange(hsv_frame, self.lower_skin_4, self.upper_skin_4)
        
        # Combinar todas las máscaras
        mask = cv2.bitwise_or(mask1, mask2)
        mask = cv2.bitwise_or(mask, mask3)
        mask = cv2.bitwise_or(mask, mask4)
        
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
            min_area = (w * h) * 0.01  # Mínimo 1% del frame
            max_area = (w * h) * 0.9   # Máximo 90% del frame
            
            if min_area < area < max_area:
                hand_data["detected"] = True
                hand_data["landmarks"] = {}
                hand_data["frame_size"] = (w, h)
                
                # Calcular hull
                hull = cv2.convexHull(largest_contour)
                hull_area = cv2.contourArea(hull)
                
                # Solidity (compactness)
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
                
                # Contour approximation para contar dedos
                epsilon = 0.02 * perimeter  # Tolerancia más pequeña
                approx = cv2.approxPolyDP(largest_contour, epsilon, True)
                
                # Número de vértices ÷ 2.5 ≈ número de dedos (base)
                vertex_count = len(approx)
                finger_count_approx = max(1, min(int(vertex_count / 2.5), 5))
                
                # ===== INFERIR DEDOS OCULTOS =====
                # Si la solidity es muy alta (forma compacta) y el área es grande,
                # probablemente hay dedos ocultos que no se ven en el contorno
                
                # Calcular ratio de circularidad
                # Una forma más circular = más cerrada = más dedos ocultos
                area_ratio = area / hull_area if hull_area > 0 else 0  # Solidity
                
                # Si solidity > 0.70, la mano está muy cerrada
                # Aumentar finger_count porque hay dedos ocultos
                if solidity > 0.72:  # Mano muy cerrada (puño)
                    finger_count = max(1, finger_count_approx - 2)  # Reducir conteo (hay menos vértices visibles)
                elif solidity > 0.65:  # Mano moderadamente cerrada
                    finger_count = finger_count_approx  # Mantener estimación
                elif solidity > 0.55:  # Mano intermedia
                    finger_count = finger_count_approx + 1  # Probablemente hay dedos apenas no detectados
                else:  # Mano abierta (solidity < 0.55)
                    finger_count = max(finger_count_approx, 4)  # Al menos 4 dedos
                
                # Clamp entre 1 y 5
                finger_count = max(1, min(int(finger_count), 5))
                
                hand_data["finger_count"] = finger_count
                hand_data["finger_count_approx"] = finger_count_approx  # Mantener el valor original
                hand_data["hand_area"] = area
                hand_data["solidity"] = solidity
                hand_data["perimeter"] = perimeter
        
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
        Mapea datos de mano a valores de servomotor con transiciones suaves.
        
        Args:
            landmarks: Diccionario de datos de mano con finger_count y solidity
            
        Returns:
            Valores normalizados suavizados: {u_index, u_group, u_thumb} (0.0-1.0)
        """
        finger_count = landmarks.get("finger_count", 0)
        solidity = landmarks.get("solidity", 0.5)
        perimeter = landmarks.get("perimeter", 0)
        
        # Mapeo continuo basado en finger_count y solidity
        # Idea: 
        # - finger_count=0 (puño) → cerrado (0.9)
        # - finger_count=5 (abierto) → abierto (0.0)
        # - solidity > 0.65 → más cerrado
        # - solidity < 0.55 → más abierto
        
        # Mapa lineal: finger_count → cierre relativo
        # 0 dedos -> muy cerrado (0.95)
        # 1 dedo -> cerrado (0.75)
        # 2-3 dedos -> intermedio (0.5)
        # 4-5 dedos -> abierto (0.1)
        
        finger_ratio = finger_count / 5.0  # Normalizar a 0-1
        
        # Base: mapeo inverso de finger_count
        # Más dedos = más abierto (menos cierre)
        base_closure = 1.0 - (finger_ratio * 0.95)  # Rango: 0.05 - 1.0
        
        # Ajustar por solidity
        # Si solidity es muy alta (puño) -> más cierre
        # Si solidity es muy baja (abierto) -> menos cierre
        solidity_factor = (solidity - 0.4) / 0.3  # Normalizar solidity 0.4-0.7 a 0-1
        solidity_factor = max(0.0, min(1.0, solidity_factor))  # Clamp 0-1
        
        # Combinar: base_closure ajustada por solidity
        # Si solidity está alta, refuerza el cierre
        # Si solidity está baja, refuerza la apertura
        adjusted_closure = base_closure + (solidity_factor - 0.5) * 0.3
        adjusted_closure = max(0.0, min(1.0, adjusted_closure))  # Clamp 0-1
        
        # Mapeo de dedos a servos específicos:
        # Índice: sigue finger_count directamente
        # Grupo (Medio, Anular, Meñique): similar pero con offset
        # Pulgar: busca oposición (generalmente más cerrado)
        
        u_index = adjusted_closure  # 0-1 (0=abierto, 1=cerrado)
        
        # Grupo: similar al índice pero con un poco más de independencia
        u_group = adjusted_closure * 0.95  # Ligeramente menos que índice
        
        # Pulgar: oposición constante con el índice
        # Cuando índice está abierto (u_index=0) -> pulgar cerrado (0.9)
        # Cuando índice está cerrado (u_index=1) -> pulgar abierto (0.2)
        u_thumb = 0.9 - (u_index * 0.7)  # Rango: 0.2-0.9
        
        return {
            "u_index": round(u_index, 2),
            "u_group": round(u_group, 2),
            "u_thumb": round(u_thumb, 2)
        }


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
