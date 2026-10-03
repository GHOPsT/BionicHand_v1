"""
Módulo de rastreo de mano en tiempo real usando MediaPipe y OpenCV.
Detecta landmarks de dedos y los mapea a ángulos de servomotor.
"""

import cv2
import numpy as np
import mediapipe as mp
from typing import Tuple, Dict, List, Optional
import threading
from queue import Queue


class HandTracker:
    """
    Rastreador de mano en tiempo real con MediaPipe.
    Detecta 21 landmarks (nudillos, articulaciones, yema).
    """

    def __init__(self, max_hands=1, confidence=0.7):
        """
        Inicializa MediaPipe Hands.
        
        Args:
            max_hands: Número máximo de manos a detectar
            confidence: Umbral de confianza para detección (0.0-1.0)
        """
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            min_detection_confidence=confidence,
            min_tracking_confidence=confidence
        )
        
        # Indices de landmarks importantes
        self.LANDMARK_NAMES = {
            0: "WRIST",
            5: "INDEX_MCP", 6: "INDEX_PIP", 7: "INDEX_TIP",
            9: "MIDDLE_MCP", 10: "MIDDLE_PIP", 11: "MIDDLE_TIP",
            13: "RING_MCP", 14: "RING_PIP", 15: "RING_TIP",
            17: "PINKY_MCP", 18: "PINKY_PIP", 19: "PINKY_TIP",
            1: "THUMB_CMC", 2: "THUMB_MCP", 3: "THUMB_IP", 4: "THUMB_TIP"
        }
        
        # Mapeo de dedos a sus índices de landmarks
        self.FINGER_INDICES = {
            "INDEX": [5, 6, 7],
            "MIDDLE": [9, 10, 11],
            "RING": [13, 14, 15],
            "PINKY": [17, 18, 19],
            "THUMB": [1, 2, 3, 4]
        }

    def process_frame(self, frame: np.ndarray) -> Tuple[Optional[Dict], np.ndarray]:
        """
        Procesa un fotograma para detectar la mano.
        
        Args:
            frame: Imagen de OpenCV (BGR)
            
        Returns:
            (hand_data, annotated_frame): Hand data con landmarks o None si no detecta
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        hand_data = None
        annotated_frame = frame.copy()
        
        if results.multi_hand_landmarks and results.multi_handedness:
            # Tomar la primera mano detectada
            hand_landmarks = results.multi_hand_landmarks[0]
            handedness = results.multi_handedness[0]
            
            h, w, c = frame.shape
            
            # Extraer posiciones de landmarks
            landmarks = {}
            for idx, landmark in enumerate(hand_landmarks.landmark):
                landmarks[idx] = {
                    "x": landmark.x,
                    "y": landmark.y,
                    "z": landmark.z,
                    "pixel_x": int(landmark.x * w),
                    "pixel_y": int(landmark.y * h)
                }
            
            hand_data = {
                "detected": True,
                "handedness": handedness.classification[0].label,  # 'Left' o 'Right'
                "confidence": handedness.classification[0].score,
                "landmarks": landmarks,
                "frame_size": (w, h)
            }
            
            # Dibujar landmarks en la imagen
            self.mp_drawing.draw_landmarks(
                annotated_frame,
                hand_landmarks,
                self.mp_hands.HAND_CONNECTIONS
            )
        else:
            hand_data = {"detected": False}
        
        return hand_data, annotated_frame

    def get_finger_angles(self, landmarks: Dict) -> Dict[str, float]:
        """
        Calcula los ángulos de flexión de cada dedo basado en landmarks.
        
        Args:
            landmarks: Diccionario de landmarks de MediaPipe
            
        Returns:
            Ángulos en grados {finger_name: angle}
        """
        angles = {}
        
        # Función auxiliar para calcular ángulo entre 3 puntos
        def angle_between_points(p1, p2, p3):
            """Calcula ángulo en p2 entre p1-p2-p3"""
            v1 = np.array([p1["x"] - p2["x"], p1["y"] - p2["y"]])
            v2 = np.array([p3["x"] - p2["x"], p3["y"] - p2["y"]])
            
            cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)
            cos_angle = np.clip(cos_angle, -1, 1)
            angle_rad = np.arccos(cos_angle)
            angle_deg = np.degrees(angle_rad)
            
            return angle_deg
        
        # Índices de dedos: [MCP, PIP, TIP]
        finger_configs = {
            "INDEX": [5, 6, 7],
            "MIDDLE": [9, 10, 11],
            "RING": [13, 14, 15],
            "PINKY": [17, 18, 19],
            "THUMB": [2, 3, 4]  # Usa IP en lugar de PIP para pulgar
        }
        
        for finger_name, (mcp_idx, pip_idx, tip_idx) in finger_configs.items():
            if all(idx in landmarks for idx in [mcp_idx, pip_idx, tip_idx]):
                # MCP flexión (ángulo entre WRIST-MCP-PIP)
                mcp_angle = angle_between_points(
                    landmarks[0],      # Muñeca
                    landmarks[mcp_idx],
                    landmarks[pip_idx]
                )
                
                # PIP flexión (ángulo entre MCP-PIP-TIP)
                pip_angle = angle_between_points(
                    landmarks[mcp_idx],
                    landmarks[pip_idx],
                    landmarks[tip_idx]
                )
                
                # Normalizar: 0° = extendido, 180° = flexionado completamente
                # Mapear a rango más realista (0-80° para MCP, 0-70° para PIP)
                mcp_normalized = np.clip((180 - mcp_angle) / 180, 0, 1)
                pip_normalized = np.clip(pip_angle / 180, 0, 1)
                
                angles[finger_name] = {
                    "mcp_angle": mcp_angle,
                    "pip_angle": pip_angle,
                    "mcp_normalized": mcp_normalized,
                    "pip_normalized": pip_normalized
                }
        
        return angles

    def detect_gesture(self, landmarks: Dict) -> str:
        """
        Detecta gestos predefinidos basado en landmarks.
        
        Args:
            landmarks: Diccionario de landmarks
            
        Returns:
            Nombre del gesto detectado
        """
        if not landmarks:
            return "UNKNOWN"
        
        # Función para medir distancia entre dos puntos
        def distance(p1_idx, p2_idx):
            if p1_idx not in landmarks or p2_idx not in landmarks:
                return 0
            p1 = landmarks[p1_idx]
            p2 = landmarks[p2_idx]
            return np.sqrt((p1["x"] - p2["x"])**2 + (p1["y"] - p2["y"])**2)
        
        # Distancias útiles
        wrist = np.array([landmarks[0]["x"], landmarks[0]["y"]])
        
        # Puntas de dedos
        thumb_tip = np.array([landmarks[4]["x"], landmarks[4]["y"]])
        index_tip = np.array([landmarks[8]["x"], landmarks[8]["y"]])
        middle_tip = np.array([landmarks[12]["x"], landmarks[12]["y"]])
        ring_tip = np.array([landmarks[16]["x"], landmarks[16]["y"]])
        pinky_tip = np.array([landmarks[20]["x"], landmarks[20]["y"]])
        
        tips = [index_tip, middle_tip, ring_tip, pinky_tip]
        
        # Detectar PUÑO (todos los dedos cerrados)
        tips_to_wrist = [np.linalg.norm(tip - wrist) for tip in tips]
        if all(d < 0.15 for d in tips_to_wrist):
            return "FIST"
        
        # Detectar PALMA ABIERTA (todos los dedos extendidos)
        if all(d > 0.25 for d in tips_to_wrist):
            return "OPEN_PALM"
        
        # Detectar PINZA (Index + Thumb juntos, otros extendidos)
        thumb_index_dist = distance(4, 8)
        if thumb_index_dist < 0.05 and np.linalg.norm(middle_tip - wrist) > 0.2:
            return "PINCH"
        
        # Detectar VICTORY (Index + Middle extendidos, otros cerrados)
        if (tips_to_wrist[0] > 0.2 and tips_to_wrist[1] > 0.2 and
            tips_to_wrist[2] < 0.15 and tips_to_wrist[3] < 0.15):
            # Verificar que index y middle estén separados
            index_middle_dist = np.linalg.norm(index_tip - middle_tip)
            if index_middle_dist > 0.08:
                return "VICTORY"
        
        # Detectar POINTING (Solo index extendido)
        if (tips_to_wrist[0] > 0.25 and all(d < 0.15 for d in tips_to_wrist[1:])):
            return "POINTING"
        
        return "NEUTRAL"

    def landmarks_to_servo_values(self, landmarks: Dict) -> Dict[str, float]:
        """
        Mapea landmarks de mano a valores de servomotor (0.0-1.0).
        
        Args:
            landmarks: Diccionario de landmarks
            
        Returns:
            Valores normalizados: {u_index, u_group, u_thumb}
        """
        angles = self.get_finger_angles(landmarks)
        
        # Mapear dedos a servomotores
        servo_values = {
            "u_index": 0.0,
            "u_group": 0.0,  # Middle, Ring, Pinky
            "u_thumb": 0.0
        }
        
        if "INDEX" in angles:
            # Índice: promedio de MCP y PIP normalizados
            servo_values["u_index"] = (
                angles["INDEX"]["mcp_normalized"] + 
                angles["INDEX"]["pip_normalized"]
            ) / 2
        
        if "THUMB" in angles:
            servo_values["u_thumb"] = angles["THUMB"]["mcp_normalized"]
        
        # Grupo: promedio de Middle, Ring, Pinky
        group_values = []
        for finger in ["MIDDLE", "RING", "PINKY"]:
            if finger in angles:
                group_values.append(
                    (angles[finger]["mcp_normalized"] + 
                     angles[finger]["pip_normalized"]) / 2
                )
        
        if group_values:
            servo_values["u_group"] = np.mean(group_values)
        
        return servo_values

    def release(self):
        """Libera recursos de MediaPipe."""
        self.hands.close()


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
