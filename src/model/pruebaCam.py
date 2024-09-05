import cv2
import numpy as np
import time

# Función para capturar una imagen desde la cámara y esperar 2 segundos
def capturar_imagen():
    cam = cv2.VideoCapture(0)  # Usar la cámara (índice 0)
    time.sleep(1)  # Esperar 2 segundos para que la cámara se estabilice
    ret, frame = cam.read()  # Capturar un frame
    cam.release()  # Liberar la cámara
    if not ret:
        print("No se pudo capturar la imagen")
        return None
    return frame

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

# Procesar la imagen capturada
def procesar_imagen(imagen):
    gray = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (15, 15), 0)
    thresh = cv2.adaptiveThreshold(blur, 255, 1, 1, 11, 2)

    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for cont in contours:
        area = cv2.contourArea(cont)
        if area > 1700:
            cv2.drawContours(imagen, [cont], -1, (0, 255, 0), 3)

    max_contour = max(contours, key=cv2.contourArea)
    cv2.drawContours(imagen, [max_contour], -1, (0, 255, 0), 3)
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

    return imagen, tablero, tic_tac_toe_matrix

# Capturar y procesar la imagen en un bucle
def main():
    while True:
        imagen = capturar_imagen()

        if imagen is not None:
            imagen_procesada, tablero, matriz = procesar_imagen(imagen)

            # Mostrar el frame capturado
            print("Frame capturado:")
            cv2.imshow("Imagen Procesada", imagen_procesada)

            # Mostrar el tablero detectado
            print("Tablero detectado:")
            cv2.imshow("Tablero", tablero)

            # Imprimir la matriz del juego
            print("Matriz Tic-Tac-Toe:")
            for fila in matriz:
                print(fila)

            # Esperar 2 segundos y permitir que se presione 'q' para salir
            if cv2.waitKey(2000) & 0xFF == ord('q'):
                break

    cv2.destroyAllWindows()  # Cerrar todas las ventanas

if __name__ == "__main__":
    main()
