"""
Calibrador Interactivo de HSV para Detección de Mano
Uso: python calibrate_hsv.py

Este script permite ajustar los rangos HSV en tiempo real usando sliders.
"""

import cv2
import numpy as np

def nothing(x):
    """Callback dummy para trackbars."""
    pass

def main():
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ No se puede abrir la cámara")
        return
    
    cv2.namedWindow('Frame')
    cv2.namedWindow('Mask')
    
    # Crear trackbars para HSV
    cv2.createTrackbar('H_Min', 'Frame', 0, 180, nothing)
    cv2.createTrackbar('H_Max', 'Frame', 20, 180, nothing)
    cv2.createTrackbar('S_Min', 'Frame', 15, 255, nothing)
    cv2.createTrackbar('S_Max', 'Frame', 170, 255, nothing)
    cv2.createTrackbar('V_Min', 'Frame', 60, 255, nothing)
    cv2.createTrackbar('V_Max', 'Frame', 255, 255, nothing)
    
    print("=" * 60)
    print("CALIBRADOR HSV INTERACTIVO")
    print("=" * 60)
    print("\n📋 INSTRUCCIONES:")
    print("1. Muestra tu mano en el video")
    print("2. Ajusta los sliders hasta que tu mano sea BLANCA en 'Mask'")
    print("3. El fondo debe ser NEGRO en 'Mask'")
    print("4. Cuando esté bien, presiona SPACE para guardar valores")
    print("5. Presiona 'q' para salir\n")
    
    saved_ranges = []
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Error leyendo frame")
            break
        
        # Reducir tamaño para mejor visualización
        frame = cv2.resize(frame, (640, 480))
        
        # Convertir a HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Obtener valores de trackbars
        h_min = cv2.getTrackbarPos('H_Min', 'Frame')
        h_max = cv2.getTrackbarPos('H_Max', 'Frame')
        s_min = cv2.getTrackbarPos('S_Min', 'Frame')
        s_max = cv2.getTrackbarPos('S_Max', 'Frame')
        v_min = cv2.getTrackbarPos('V_Min', 'Frame')
        v_max = cv2.getTrackbarPos('V_Max', 'Frame')
        
        # Crear máscara
        lower = np.array([h_min, s_min, v_min])
        upper = np.array([h_max, s_max, v_max])
        mask = cv2.inRange(hsv, lower, upper)
        
        # Aplicar morfología
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        # Mostrar frame con info
        display_frame = frame.copy()
        cv2.putText(display_frame, f'H: {h_min}-{h_max} | S: {s_min}-{s_max} | V: {v_min}-{v_max}',
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(display_frame, f'Detectados: {cv2.countNonZero(mask)} pixeles blancos',
                   (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Mostrar contornos en la máscara
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            largest = max(contours, key=cv2.contourArea)
            cv2.drawContours(display_frame, [largest], 0, (0, 255, 0), 2)
            area = cv2.contourArea(largest)
            cv2.putText(display_frame, f'Area: {int(area)} px', (10, 110),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.imshow('Frame', display_frame)
        cv2.imshow('Mask', mask)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            break
        elif key == ord(' '):
            # Guardar rango
            range_dict = {
                'lower': [h_min, s_min, v_min],
                'upper': [h_max, s_max, v_max]
            }
            saved_ranges.append(range_dict)
            print(f"\n✅ RANGO GUARDADO #{len(saved_ranges)}:")
            print(f"   Lower: [{h_min}, {s_min}, {v_min}]")
            print(f"   Upper: [{h_max}, {s_max}, {v_max}]\n")
    
    cap.release()
    cv2.destroyAllWindows()
    
    # Mostrar rangos guardados
    if saved_ranges:
        print("\n" + "=" * 60)
        print("📊 RANGOS GUARDADOS:")
        print("=" * 60)
        
        for i, r in enumerate(saved_ranges, 1):
            print(f"\n# Rango {i} (copiar a control/hand_tracking.py):")
            print(f"self.lower_skin_{i} = np.array({r['lower']}, dtype=np.uint8)")
            print(f"self.upper_skin_{i} = np.array({r['upper']}, dtype=np.uint8)")
        
        print("\n" + "=" * 60)
        print("💡 CÓMO USAR LOS VALORES:")
        print("=" * 60)
        print("\n1. Abre: control/hand_tracking.py")
        print("2. Busca el método __init__()")
        print("3. Reemplaza los valores de lower/upper_skin con los de arriba")
        print("4. Ejecuta: python app_desktop_v2.py")
        print("5. ¡Prueba modo CÁMARA!\n")

if __name__ == "__main__":
    main()
