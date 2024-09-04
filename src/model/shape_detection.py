import cv2
import numpy as np

# Dividir el frame en 9 celdas (3x3)
def split_into_cells(frame):
    height, width = frame.shape[:2]
    cell_height = height // 3
    cell_width = width // 3
    
    cells = []  # Lista para almacenar las 9 celdas
    
    for i in range(3):
        row = []
        for j in range(3):
            # Extraer cada celda (subimagen)
            x1 = j * cell_width
            y1 = i * cell_height
            x2 = x1 + cell_width
            y2 = y1 + cell_height
            cell = frame[y1:y2, x1:x2]  # Extrae la subimagen de cada celda
            row.append(cell)  # Agrega la celda a la fila
        cells.append(row)  # Agrega la fila completa a la lista de celdas
    
    return cells  # Retorna las 9 celdas

# Detectar las formas "X", "O" o celda vacía
def detect_shape(cell):
    gray = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY_INV)
    
    # Detectar contornos en la celda
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        approx = cv2.approxPolyDP(contour, 0.02 * cv2.arcLength(contour, True), True)
        
        # Si tiene 12 vértices es una "X", si tiene más de 10 y es circular, es una "O"
        if len(approx) == 12:
            return "X"
        elif len(approx) > 10:
            return "O"
    
    return None  # Si no detecta nada

# Detectar el estado del tablero (X, O o vacío)
def detect_board_state(cells):
    board_state = np.full((3, 3), '')  # Inicializa una matriz 3x3 vacía
    
    for i in range(3):
        for j in range(3):
            cell = cells[i][j]
            
            # Detectar si la celda contiene una "X", "O", o está vacía
            shape = detect_shape(cell)
            
            if shape == "X":
                board_state[i][j] = "X"
            elif shape == "O":
                board_state[i][j] = "O"
            else:
                board_state[i][j] = ""  # Celda vacía
    
    return board_state  # Retorna la matriz 3x3 con el estado del tablero
