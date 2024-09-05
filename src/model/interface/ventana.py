import cv2
import numpy as np

# Variables globales para almacenar las esquinas seleccionadas
corner1, corner2, corner3, corner4 = None, None, None, None
click_count = 0
points = []

# Función para manejar los clics del ratón
def click_event(event, x, y, flags, param):
    global click_count, points, corner1, corner2, corner3, corner4

    # Si se hace clic izquierdo
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append((x, y))
        click_count += 1

        if click_count == 1:
            corner1 = (x, y)
        elif click_count == 2:
            corner2 = (x, y)
        elif click_count == 3:
            corner3 = (x, y)
        elif click_count == 4:
            corner4 = (x, y)

        # Dibujar un círculo en la esquina seleccionada
        cv2.circle(image, (x, y), 5, (0, 255, 0), -1)
        cv2.imshow("Imagen", image)

        # Si ya se han seleccionado las 4 esquinas, dividir la imagen en una cuadrícula
        if click_count == 4:
            define_grid_and_detect()

# Función para dividir el área seleccionada en una cuadrícula y detectar X y O
def define_grid_and_detect():
    # Crear un array con las esquinas seleccionadas
    pts1 = np.float32([corner1, corner2, corner3, corner4])

    # Definir el tamaño de la cuadrícula (suponemos un tamaño arbitrario)
    grid_width, grid_height = 300, 300
    pts2 = np.float32([[0, 0], [grid_width, 0], [grid_width, grid_height], [0, grid_height]])

    # Calcular la transformación de perspectiva
    matrix = cv2.getPerspectiveTransform(pts1, pts2)

    # Aplicar la transformación de perspectiva para obtener una imagen "plana" del tablero
    warped = cv2.warpPerspective(original_image, matrix, (grid_width, grid_height))

    # Dividir la imagen transformada en una cuadrícula de 3x3
    cell_width = grid_width // 3
    cell_height = grid_height // 3

    for row in range(3):
        for col in range(3):
            # Extraer cada celda de la cuadrícula
            x_start, y_start = col * cell_width, row * cell_height
            cell = warped[y_start:y_start + cell_height, x_start:x_start + cell_width]

            # Mostrar cada celda (para depuración)
            cv2.imshow(f"Celda {row * 3 + col + 1}", cell)

            # Detectar X u O en la celda
            detect_shape_in_cell(cell, row * 3 + col + 1)

    cv2.imshow("Tablero", warped)
    cv2.waitKey(0)

# Función para detectar formas (X u O) en cada celda
def detect_shape_in_cell(cell, cell_number):
    gray_cell = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY)
    _, thresh_cell = cv2.threshold(gray_cell, 127, 255, cv2.THRESH_BINARY_INV)

    # Detectar contornos dentro de la celda
    contours, _ = cv2.findContours(thresh_cell, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) > 0:
        contour = max(contours, key=cv2.contourArea)
        approx = cv2.approxPolyDP(contour, 0.02 * cv2.arcLength(contour, True), True)

        if len(approx) == 4:
            print(f"Celda {cell_number}: Detectada una X")
        elif len(approx) > 8:
            print(f"Celda {cell_number}: Detectada una O")
        else:
            print(f"Celda {cell_number}: Celda vacía")
    else:
        print(f"Celda {cell_number}: No se detectaron formas")

# Cargar la imagen
image = cv2.imread('./prueba.jpeg')
original_image = image.copy()

# Mostrar la imagen y esperar a que el usuario haga clic en las 4 esquinas
cv2.imshow("Imagen", image)
cv2.setMouseCallback("Imagen", click_event)

cv2.waitKey(0)
cv2.destroyAllWindows()
