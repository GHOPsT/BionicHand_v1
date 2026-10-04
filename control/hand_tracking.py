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
                
                # ===== LANDMARK DETECTION: Extraer nodos de la mano =====
                defects = None
                hull_indices = cv2.convexHull(largest_contour, returnPoints=False)
                if len(hull_indices) > 3:
                    defects = cv2.convexityDefects(largest_contour, hull_indices)
                
                landmarks_2d = self._extract_landmarks(largest_contour, hull, defects, largest_contour)
                
                # Dibujar landmarks en la imagen
                for i, (x, y) in enumerate(landmarks_2d):
                    # Color diferente para la base
                    color = (255, 0, 255) if i == 0 else (0, 255, 255)
                    cv2.circle(annotated_frame, (int(x), int(y)), 8, color, -1)
                    cv2.putText(annotated_frame, f"N{i}", (int(x)+10, int(y)-10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                # Contar dedos = número de landmarks - 1 (la base)
                finger_count = max(1, min(len(landmarks_2d) - 1, 5))
                
                hand_data["landmarks_2d"] = landmarks_2d
                hand_data["finger_count"] = finger_count
        
        return hand_data, annotated_frame

    def _extract_landmarks(self, contour, hull, defects, largest_contour):
        """
        Extrae landmarks (nodos) de la mano basado en convex hull defects.
        Retorna lista de (x, y) coordenadas de puntos clave.
        """
        landmarks = []
        
        # Centroide (base/palma)
        M = cv2.moments(largest_contour)
        if M["m00"] > 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            landmarks.append((cx, cy))  # Primer landmark = base
        
        # Extraer puntos desde convex hull defects
        if defects is not None:
            defect_points = []
            for i in range(defects.shape[0]):
                s, e, f, d = defects[i, 0]
                far = tuple(contour[f][0])
                defect_points.append(far)
            
            # Ordenar por ángulo desde el centroide
            if landmarks:
                center = landmarks[0]
                defect_points.sort(
                    key=lambda p: np.arctan2(p[1] - center[1], p[0] - center[0])
                )
            
            # Limitar a 5 puntos de defects (máximo 5 dedos)
            defect_points = defect_points[:5]
            landmarks.extend(defect_points)
        
        # Si no hay suficientes landmarks, agregar puntos extremos
        if len(landmarks) < 4:
            extremes = []
            # Punto más arriba
            top = contour[contour[:, :, 1].argmin()][0]
            extremes.append(tuple(top))
            
            # Punto más a la derecha
            right = contour[contour[:, :, 0].argmax()][0]
            extremes.append(tuple(right))
            
            # Punto más abajo
            bottom = contour[contour[:, :, 1].argmax()][0]
            extremes.append(tuple(bottom))
            
            # Punto más a la izquierda
            left = contour[contour[:, :, 0].argmin()][0]
            extremes.append(tuple(left))
            
            landmarks.extend(extremes)
        
        return landmarks[:6]  # Máximo 6 landmarks (base + 5 dedos)

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
        Mapea landmarks 2D a valores de servo usando distancias desde la base.
        
        Los landmarks son: [base, punto_dedo1, punto_dedo2, ...]
        Calculamos distancia de cada punta a la base para inferir flexión.
        
        Args:
            landmarks: Diccionario con landmarks_2d (lista de (x,y))
            
        Returns:
            Valores normalizados: {u_index, u_group, u_thumb}
        """
        landmarks_2d = landmarks.get("landmarks_2d", [])
        
        if len(landmarks_2d) < 2:
            # Si no hay suficientes landmarks, usar finger_count como fallback
            finger_count = landmarks.get("finger_count", 0)
            finger_ratio = finger_count / 5.0
            base_closure = 1.0 - (finger_ratio * 0.95)
            solidity = landmarks.get("solidity", 0.5)
            solidity_factor = (solidity - 0.4) / 0.3
            solidity_factor = max(0.0, min(1.0, solidity_factor))
            adjusted_closure = base_closure + (solidity_factor - 0.5) * 0.3
            adjusted_closure = max(0.0, min(1.0, adjusted_closure))
            
            u_index = adjusted_closure
            u_group = adjusted_closure * 0.95
            u_thumb = 0.9 - (u_index * 0.7)
            
            return {
                "u_index": round(u_index, 2),
                "u_group": round(u_group, 2),
                "u_thumb": round(u_thumb, 2)
            }
        
        # Usar landmarks detectados
        base = np.array(landmarks_2d[0])  # Centro/base de la palma
        fingertip_distances = []
        
        # Calcular distancia de cada punta de dedo a la base
        for i in range(1, len(landmarks_2d)):
            fingertip = np.array(landmarks_2d[i])
            distance = np.linalg.norm(fingertip - base)
            fingertip_distances.append(distance)
        
        # Si no hay suficientes puntas de dedo
        if not fingertip_distances:
            # Fallback: usar finger_count
            u_index = 0.3
            u_group = 0.3
            u_thumb = 0.6
            return {
                "u_index": round(u_index, 2),
                "u_group": round(u_group, 2),
                "u_thumb": round(u_thumb, 2)
            }
        
        # Normalizar distancias
        max_distance = max(fingertip_distances) if fingertip_distances else 1.0
        min_distance = min(fingertip_distances) if fingertip_distances else 0.0
        distance_range = max_distance - min_distance if max_distance > min_distance else 1.0
        
        # Mapear distancias a cierre (inverso: distancia corta = cerrado)
        # Si distancia = máxima (dedo extendido) → cierre = 0.0 (abierto)
        # Si distancia = mínima (dedo doblado) → cierre = 1.0 (cerrado)
        normalized_distances = []
        for d in fingertip_distances:
            norm = (max_distance - d) / distance_range if distance_range > 0 else 0.5
            norm = max(0.0, min(1.0, norm))
            normalized_distances.append(norm)
        
        # Mapear dedos a servos (asumiendo orden: pulgar, índice, medio, anular, meñique)
        # Aproximadamente: [base, pulgar, índice, medio, anular, meñique]
        
        # Caso: 5 dedos detectados
        if len(normalized_distances) >= 5:
            u_thumb = normalized_distances[0]  # Pulgar (primer dedo)
            u_index = normalized_distances[1]  # Índice (segundo dedo)
            u_middle = normalized_distances[2]  # Medio
            u_ring = normalized_distances[3]   # Anular
            u_pinky = normalized_distances[4]  # Meñique
            
            # Grupo = promedio de medio, anular, meñique
            u_group = (u_middle + u_ring + u_pinky) / 3.0
            
        # Caso: 4 dedos detectados (posiblemente sin pulgar o sin meñique)
        elif len(normalized_distances) >= 4:
            u_index = normalized_distances[0]
            u_middle = normalized_distances[1]
            u_ring = normalized_distances[2]
            u_pinky = normalized_distances[3]
            u_thumb = u_index * 0.8  # Pulgar sigue al índice pero menos
            u_group = (u_middle + u_ring + u_pinky) / 3.0
            
        # Caso: 3 dedos detectados
        elif len(normalized_distances) >= 3:
            u_index = normalized_distances[0]
            u_middle = normalized_distances[1]
            u_ring = normalized_distances[2]
            u_pinky = u_ring * 0.9
            u_thumb = u_index * 0.7
            u_group = (u_middle + u_ring) / 2.0
            
        # Caso: 2 dedos detectados
        elif len(normalized_distances) >= 2:
            u_index = normalized_distances[0]
            u_middle = normalized_distances[1]
            u_ring = u_middle
            u_pinky = u_middle
            u_thumb = u_index * 0.9
            u_group = u_middle
            
        # Caso: 1 dedo detectado
        else:
            u_index = normalized_distances[0]
            u_middle = u_index * 0.8
            u_ring = u_middle
            u_pinky = u_middle
            u_thumb = u_index * 0.7
            u_group = u_middle
        
        # Clamp todos los valores a 0-1
        u_index = max(0.0, min(1.0, u_index))
        u_group = max(0.0, min(1.0, u_group))
        u_thumb = max(0.0, min(1.0, u_thumb))
        
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
