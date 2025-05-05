import cv2
import numpy as np

# Parámetros configurables
MIN_CONTOUR_AREA = 80
CIRCLE_CIRCULARITY_MIN = 0.6
CIRCLE_CIRCULARITY_MAX = 1.4
CIRCLE_ASPECT_RATIO_MIN = 0.6
X_ANGLE_TOLERANCE = np.pi/4  # 45 grados de tolerancia
X_LINE_THRESHOLD = 15
X_MIN_LINE_LENGTH_RATIO = 0.25

def es_circulo(contorno):
    """Detección robusta de círculos que acepta imperfecciones"""
    if len(contorno) < 5:
        return False
    
    try:
        area = cv2.contourArea(contorno)
        perimeter = cv2.arcLength(contorno, True)
        
        if perimeter == 0 or area < MIN_CONTOUR_AREA:
            return False
        
        circularity = (4 * np.pi * area) / (perimeter ** 2)
        if not (CIRCLE_CIRCULARITY_MIN < circularity < CIRCLE_CIRCULARITY_MAX):
            return False
        
        (_, _), (MA, ma), _ = cv2.fitEllipse(contorno)
        aspect_ratio = min(MA, ma) / max(MA, ma)
        
        return aspect_ratio > CIRCLE_ASPECT_RATIO_MIN
    
    except Exception as e:
        print(f"Error en detección de círculo: {e}")
        return False

def es_x(contorno):
    """Detección mejorada de X usando análisis de líneas"""
    if len(contorno) < 5 or cv2.contourArea(contorno) < MIN_CONTOUR_AREA:
        return False
    
    # Crear máscara del contorno
    x, y, w, h = cv2.boundingRect(contorno)
    mask = np.zeros((h+2, w+2), dtype=np.uint8)  # +2 para bordes
    offset_contour = contorno - [x, y]
    cv2.drawContours(mask, [offset_contour], -1, 255, 1)
    
    # Detección de bordes con Canny
    edges = cv2.Canny(mask, 50, 150)
    
    # Detección de líneas con Hough
    lines = cv2.HoughLinesP(
        edges,
        rho=1,
        theta=np.pi/180,
        threshold=X_LINE_THRESHOLD,
        minLineLength=int(max(w,h)*X_MIN_LINE_LENGTH_RATIO),
        maxLineGap=5
    )
    
    if lines is None or len(lines) < 2:
        return False
    
    # Análisis de ángulos
    angles = []
    for line in lines[:2]:  # Tomar las 2 líneas principales
        x1, y1, x2, y2 = line[0]
        angle = np.arctan2(y2-y1, x2-x1) % np.pi
        angles.append(angle)
    
    if len(angles) == 2:
        angle_diff = min(
            np.abs(angles[0]-angles[1]),
            np.pi - np.abs(angles[0]-angles[1])
        )
        return (np.pi/2 - X_ANGLE_TOLERANCE) < angle_diff < (np.pi/2 + X_ANGLE_TOLERANCE)
    
    return False

def procesar_imagen(imagen):
    """Pipeline completo de procesamiento de imagen"""
    # Convertir a escala de grises y mejorar contraste
    gray = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    
    # Threshold adaptativo
    thresh = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 11, 2
    )
    
    # Operaciones morfológicas
    kernel = np.ones((3,3), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    
    # Encontrar contornos
    contours, _ = cv2.findContours(
        thresh,
        cv2.RETR_TREE,
        cv2.CHAIN_APPROX_SIMPLE
    )
    
    if not contours:
        return None, [[' ']*3 for _ in range(3)]
    
    # Encontrar tablero principal
    max_contour = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(max_contour)
    
    # Validar relación de aspecto
    if not 0.7 < (w/h) < 1.3:
        return None, [[' ']*3 for _ in range(3)]
    
    # Procesar cada celda
    board = thresh[y:y+h, x:x+w]
    cell_h, cell_w = h//3, w//3
    matrix = [[' ']*3 for _ in range(3)]
    
    for row in range(3):
        for col in range(3):
            cell = board[row*cell_h:(row+1)*cell_h, col*cell_w:(col+1)*cell_w]
            cell_contours, _ = cv2.findContours(
                cell.copy(),
                cv2.RETR_TREE,
                cv2.CHAIN_APPROX_SIMPLE
            )
            
            # Filtrar contornos relevantes
            relevant = [
                c for c in cell_contours
                if MIN_CONTOUR_AREA < cv2.contourArea(c) < cell_w*cell_h*0.8
            ]
            
            if relevant:
                if any(es_circulo(c) for c in relevant):
                    matrix[row][col] = 'O'
                elif any(es_x(c) for c in relevant):
                    matrix[row][col] = 'X'
    
    return board, matrix