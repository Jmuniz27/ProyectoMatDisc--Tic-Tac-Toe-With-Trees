import cv2
import numpy as np

def es_circulo(contorno):
    if len(contorno) < 5:
        return False
    
    try:
        # Calcular circularidad
        area = cv2.contourArea(contorno)
        perimeter = cv2.arcLength(contorno, True)
        if perimeter == 0 or area < 50:
            return False
        
        circularity = (4 * np.pi * area) / (perimeter ** 2)
        
        # Ajustar elipse y verificar relación de ejes
        ellipse = cv2.fitEllipse(contorno)
        (_, _), (MA, ma), _ = ellipse
        eccentricity = np.sqrt(1 - (ma/MA)**2)
        
        # Criterios combinados
        return (0.7 < circularity < 1.3 and 
                eccentricity < 0.75 and 
                area > 50)
    except:
        return False

def es_x(contorno):
    if len(contorno) < 10 or cv2.contourArea(contorno) < 100:
        return False
    
    # Crear imagen binaria del contorno
    x, y, w, h = cv2.boundingRect(contorno)
    mask = np.zeros((h, w), dtype=np.uint8)
    offset_contour = contorno - [x, y]
    cv2.drawContours(mask, [offset_contour], -1, 255, 1)
    
    # Detectar líneas con Hough
    lines = cv2.HoughLinesP(mask, 1, np.pi/180, threshold=20, 
                          minLineLength=max(w,h)*0.3, 
                          maxLineGap=5)
    
    if lines is None or len(lines) < 2:
        return False
    
    # Calcular ángulos entre líneas
    angles = []
    for line in lines[:2]:  # Analizar las 2 líneas principales
        x1, y1, x2, y2 = line[0]
        angle = np.arctan2(y2-y1, x2-x1)
        angles.append(angle)
    
    if len(angles) == 2:
        angle_diff = np.abs(angles[0] - angles[1])
        # Verificar si los ángulos son aproximadamente perpendiculares
        return np.pi/4 < angle_diff % (np.pi/2) < 3*np.pi/4
    
    return False

def es_x(contorno):
    if len(contorno) < 10 or cv2.contourArea(contorno) < 150:
        return False
    
    # Mejor aproximación de polígono
    epsilon = 0.03 * cv2.arcLength(contorno, True)
    approx = cv2.approxPolyDP(contorno, epsilon, True)
    
    if len(approx) < 6:
        return False
    
    # Verificar relación de aspecto y convexidad
    x, y, w, h = cv2.boundingRect(contorno)
    aspect_ratio = w / float(h)
    
    if not 0.5 < aspect_ratio < 2.0:
        return False
    
    if cv2.isContourConvex(approx):
        return False
    
    # Análisis de líneas mediante transformada de Hough
    mask = np.zeros((h, w), dtype=np.uint8)
    offset_contour = contorno - np.array([x,y])
    cv2.drawContours(mask, [offset_contour], -1, 255, 1)
    
    lines = cv2.HoughLinesP(mask, 1, np.pi/180, threshold=15, 
                           minLineLength=20, maxLineGap=5)
    
    if lines is None or len(lines) < 2:
        return False
    
    # Verificar ángulos entre líneas
    angles = []
    for i in range(min(2, len(lines))):
        x1, y1, x2, y2 = lines[i][0]
        angle = np.arctan2(y2-y1, x2-x1)
        angles.append(angle)
    
    if len(angles) >= 2:
        angle_diff = np.abs(angles[0] - angles[1])
        return np.pi/4 < angle_diff % (np.pi/2) < 3*np.pi/4
    
    return False

def es_borde_de_celda(contorno, cell_width, cell_height, margen=5):
    x, y, w, h = cv2.boundingRect(contorno)
    # Añadir tolerancia para bordes irregulares
    margen_ajustado = max(margen, cell_width * 0.05)
    return (x < margen_ajustado or y < margen_ajustado or 
            x + w > cell_width - margen_ajustado or 
            y + h > cell_height - margen_ajustado)

def procesar_imagen(imagen):
    # Preprocesamiento mejorado
    gray = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (15, 15), 0)
    
    # Threshold adaptativo con parámetros optimizados
    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                  cv2.THRESH_BINARY_INV, 11, 2)
    
    # Operaciones morfológicas para mejorar las formas
    kernel = np.ones((3,3), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    
    # Encontrar contornos con jerarquía
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    # Si no encontramos contornos, retornar matriz vacía
    if not contours:
        return None, [[' ' for _ in range(3)] for _ in range(3)]
    
    # Filtrar por área y obtener el tablero
    max_contour = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(max_contour)
    
    # Verificar que sea un tablero válido (relación de aspecto aproximada 1:1)
    aspect_ratio = w / float(h)
    if not 0.8 < aspect_ratio < 1.2:
        return None, [[' ' for _ in range(3)] for _ in range(3)]
    
    tablero = thresh[y:y+h, x:x+w]
    cell_height = h // 3
    cell_width = w // 3
    
    tic_tac_toe_matrix = [[' ' for _ in range(3)] for _ in range(3)]
    
    for row in range(3):
        for col in range(3):
            cell = tablero[row*cell_height:(row+1)*cell_height, 
                          col*cell_width:(col+1)*cell_width]
            
            cell_contours, _ = cv2.findContours(cell.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filtrar contornos pequeños y bordes
            relevant_contours = [
                c for c in cell_contours 
                if 300 < cv2.contourArea(c) < (cell_width * cell_height * 0.8)
                and not es_borde_de_celda(c, cell_width, cell_height)
            ]
            
            if relevant_contours:
                # Verificar círculos
                circulos = sum(1 for c in relevant_contours if es_circulo(c))
                
                # Verificar Xs
                x_count = sum(1 for c in relevant_contours if es_x(c))
                
                if circulos >= 1:
                    tic_tac_toe_matrix[row][col] = 'O'
                elif x_count >= 1:
                    tic_tac_toe_matrix[row][col] = 'X'
    
    return tablero, tic_tac_toe_matrix

def main(state, cam):
    ret, frame = cam.read()
    if not ret:
        print("Error: No se pudo capturar imagen de la cámara")
        return
    
    # Preprocesamiento de la imagen
    frame = cv2.flip(frame, 1)
    frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    
    # Procesamiento mejorado
    _, matriz_actual = procesar_imagen(frame)
    
    # Validación estricta del resultado
    if (isinstance(matriz_actual, list) and len(matriz_actual) == 3 and all(len(row) == 3 for row in matriz_actual)):
        for i in range(3):
            for j in range(3):
                if matriz_actual[i][j] == 'X' and state[i][j] == ' ':
                    state[i][j] = 'X'
    else:
        print("Advertencia: No se pudo detectar un tablero válido")