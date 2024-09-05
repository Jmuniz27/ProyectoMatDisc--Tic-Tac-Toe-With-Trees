import cv2
import numpy as np
import time

# Función auxiliar para determinar si un contorno es circular (O)
def es_circulo(contorno):
    area = cv2.contourArea(contorno)
    perimetro = cv2.arcLength(contorno, True)
    if perimetro == 0:
        return False  # Evitar división por cero
    circularidad = (4 * np.pi * area) / (perimetro ** 2)
    return 0.7 < circularidad < 1.2

# Función para verificar si es una "X"
def es_x(contorno):
    epsilon = 0.04 * cv2.arcLength(contorno, True)
    approx = cv2.approxPolyDP(contorno, epsilon, True)
    return len(approx) >= 4

# Función para verificar si un contorno está en el borde de la celda
def es_borde_de_celda(contorno, cell_width, cell_height, margen=5):
    x, y, w, h = cv2.boundingRect(contorno)
    if x < margen or y < margen or x + w > cell_width - margen or y + h > cell_height - margen:
        return True
    return False

# Procesar la imagen capturada y detectar el tablero
def procesar_imagen(imagen):
    # Convertir a escala de grises
    gray = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (15, 15), 0)
    
    # Aplicar umbral adaptativo para resaltar el tablero
    thresh = cv2.adaptiveThreshold(blur, 255, 1, 1, 11, 2)

    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    max_contour = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(max_contour)
    tablero = thresh[y:y+h, x:x+w]

    # Definir dimensiones de las celdas para una matriz 3x3
    cell_height = h // 3
    cell_width = w // 3

    tic_tac_toe_matrix = [['' for _ in range(3)] for _ in range(3)]

    # Iterar sobre las celdas y detectar si hay "X" o "O"
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

# Función principal que mantiene la matriz constante hasta que hay un cambio y toma una captura cada 1.5 segundos
def main(state,cam):
    while True:
        ret, frame = cam.read()  # Leer el frame de la cámara
        if not ret:
            print("No se pudo capturar la imagen")
            continue

        # Efecto espejo y rotación de 90 grados a la derecha
        frame = cv2.flip(frame, 1)
        frame = cv2.flip(frame, 1)
        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)

        # Mostrar la cámara en vivo
        cv2.imshow("Cámara en Vivo - Presiona 'c' para confirmar el movimiento", frame)

        # Esperar que el usuario confirme el movimiento presionando 'c'
        key = cv2.waitKey(1) & 0xFF
        if key == ord('c'):
            # Procesar la imagen para detectar la matriz del tablero
            tablero, matriz_actual = procesar_imagen(frame)

            # Asegurarse de que la matriz detectada es 3x3
            if matriz_actual is not None and len(matriz_actual) == 3 and all(len(row) == 3 for row in matriz_actual):
                # Asegurarse de que la matriz contiene solo valores simples
                for i in range(3):
                    for j in range(3):
                        # Verificar que matriz_actual sea válida antes de acceder a sus elementos
                        if isinstance(matriz_actual[i][j], str):  # Solo compara si es un string
                            if matriz_actual[i][j] == 'X' and state[i][j] == '':
                                state[i][j] = 'X'
                break
            else:
                print("No se detectó un tablero 3x3 correctamente. Intenta nuevamente.")
                continue  # Vuelve a solicitar la confirmación del movimiento

        elif key == ord('q'):
            break

