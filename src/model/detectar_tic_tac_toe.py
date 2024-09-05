import cv2
import numpy as np

def detectar_tablero(imagen):
    # Convertir la imagen a escala de grises
    gray = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    
    # Aplicar suavizado
    blur = cv2.GaussianBlur(gray, (15, 15), 0)
    
    # Aplicar umbral adaptativo
    thresh = cv2.adaptiveThreshold(blur, 255, 1, 1, 11, 2)

    # Encontrar contornos
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    # Encontrar el contorno más grande (el tablero)
    max_contour = max(contours, key=cv2.contourArea)

    # Dibujar el contorno más grande en la imagen original
    cv2.drawContours(imagen, [max_contour], -1, (0, 255, 0), 3)

    # Obtener el rectángulo que rodea el contorno más grande
    x, y, w, h = cv2.boundingRect(max_contour)
    
    # Extraer la región del tablero de la imagen binaria
    tablero = thresh[y:y+h, x:x+w]

    return imagen, tablero, (x, y, w, h)

def extraer_matriz_tic_tac_toe(tablero, bounds):
    x, y, w, h = bounds
    
    # Tamaño de las celdas
    cell_height = h // 3
    cell_width = w // 3
    
    # Inicializar la matriz del juego
    tic_tac_toe_matrix = [['' for _ in range(3)] for _ in range(3)]

    # Funciones auxiliares para verificar si es una "X" o "O"
    def es_circulo(contorno):
        area = cv2.contourArea(contorno)
        perimetro = cv2.arcLength(contorno, True)
        if perimetro == 0:
            return False
        circularidad = (4 * np.pi * area) / (perimetro ** 2)
        return 0.7 < circularidad < 1.2

    def es_x(contorno):
        epsilon = 0.04 * cv2.arcLength(contorno, True)
        approx = cv2.approxPolyDP(contorno, epsilon, True)
        return len(approx) >= 4

    # Recorrer las celdas del tablero
    for row in range(3):
        for col in range(3):
            # Extraer cada celda
            cell = tablero[row * cell_height:(row + 1) * cell_height, col * cell_width:(col + 1) * cell_width]
            
            # Encontrar contornos dentro de la celda
            cell_contours, _ = cv2.findContours(cell, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filtrar contornos relevantes (para evitar ruido)
            relevant_contours = [c for c in cell_contours if 500 < cv2.contourArea(c) < 50000]
            
            # Determinar el contenido de la celda
            if len(relevant_contours) == 0:
                tic_tac_toe_matrix[row][col] = ''
            else:
                circulos = [es_circulo(c) for c in relevant_contours]
                if circulos.count(True) >= 1:
                    tic_tac_toe_matrix[row][col] = 'O'
                elif any(es_x(c) for c in relevant_contours):
                    tic_tac_toe_matrix[row][col] = 'X'
                else:
                    tic_tac_toe_matrix[row][col] = ''
    
    return tic_tac_toe_matrix
