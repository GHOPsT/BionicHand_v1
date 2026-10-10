"""
Constantes cinemáticas, dimensionales y mecánicas para BionicHand.
Mediciones obtenidas directamente del modelo CAD (HACKberry L).
Unidades: Milímetros (mm) y Grados sexagesimales (°).
"""

# 1. Longitudes de eslabones (mm)
FINGER_DIMENSIONS = {
    "thumb":  {"l1_proximal": 29.92, "l2_distal": 49.14, "l_biela": None,  "total_length": 79.06},
    "index":  {"l1_proximal": 36.54, "l2_distal": 40.96, "l_biela": 29.03, "total_length": 77.50},
    "middle": {"l1_proximal": 41.118, "l2_distal": 40.397, "l_biela": 28.348, "total_length": 81.515},
    "ring":   {"l1_proximal": 41.307, "l2_distal": 40.397, "l_biela": 28.342, "total_length": 81.704},
    "pinky":  {"l1_proximal": 36.413, "l2_distal": 40.397, "l_biela": 28.342, "total_length": 76.810}
}

# 2. Separación entre ejes de las bases en la palma (mm)
PALM_SPACING = {
    "index_to_middle": 20.767,
    "middle_to_ring": 20.653,
    "ring_to_pinky": 22.771,
    "index_to_thumb_3d": 40.235,
    "index_to_thumb_proj": 37.63
}

# 3. Límites angulares de giro físico (grados)
JOINT_LIMITS = {
    "mcp_base_flexion": (0.0, 80.0),    # Rotación base nudillo (Revolución 14)
    "pip_middle_flexion": (0.0, 70.0),  # Rotación nudillo medio (Revolución 12)
    "thumb_base_flexion": (0.0, 75.0),  # Flexión base pulgar
    "thumb_pip_flexion": (0.0, 65.0)    # Flexión nudillo pulgar
}

# Factor de acoplamiento del mecanismo de 4 barras (PIP / MCP)
COUPLING_RATIO_4BAR = 70.0 / 80.0  # 0.875

# 4. Transmisión mecánica del Dedo Índice
GEAR_TEETH_MOTOR = 24
GEAR_TEETH_FINGER = 14
GEAR_RATIO_INDEX = GEAR_TEETH_MOTOR / GEAR_TEETH_FINGER  # 1.714