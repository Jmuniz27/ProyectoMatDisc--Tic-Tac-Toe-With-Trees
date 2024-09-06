import cv2
import numpy as np

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

def es_borde_de_celda(contorno, cell_width, cell_height, margen=5):
    x, y, w, h = cv2.boundingRect(contorno)
    if x < margen or y < margen or x + w > cell_width - margen or y + h > cell_height - margen:
        return True
    return False

def procesar_imagen(imagen):
    gray = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (15, 15), 0)
    thresh = cv2.adaptiveThreshold(blur, 255, 1, 1, 11, 2)

    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    max_contour = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(max_contour)
    tablero = thresh[y:y+h, x:x+w]

    cell_height = h // 3
    cell_width = w // 3

    tic_tac_toe_matrix = [['' for _ in range(3)] for _ in range(3)]

    for row in range(3):
        for col in range(3):
            cell = tablero[row * cell_height:(row + 1) * cell_height, col * cell_width:(col + 1) * cell_width]
            cell_contours, _ = cv2.findContours(cell, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            relevant_contours = [c for c in cell_contours if 500 < cv2.contourArea(c) < 50000 and not es_borde_de_celda(c, cell_width, cell_height)]

            if len(relevant_contours) > 0:
                circulos = [es_circulo(c) for c in relevant_contours]
                if circulos.count(True) >= 1:
                    tic_tac_toe_matrix[row][col] = 'O'
                elif any(es_x(c) for c in relevant_contours):
                    tic_tac_toe_matrix[row][col] = 'X'

    return tablero, tic_tac_toe_matrix

def main(state, cam):
    ret, frame = cam.read()
    if not ret:
        print("No se pudo capturar la imagen")
        return

    frame = cv2.flip(frame, 1)
    frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)

    tablero, matriz_actual = procesar_imagen(frame)

    if matriz_actual is not None and len(matriz_actual) == 3 and all(len(row) == 3 for row in matriz_actual):
        for i in range(3):
            for j in range(3):
                if isinstance(matriz_actual[i][j], str) and matriz_actual[i][j] == 'X' and state[i][j] == '':
                    state[i][j] = 'X'
    else:
        print("No se detectó un tablero 3x3 correctamente. Intenta nuevamente.")
