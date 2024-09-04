import cv2
from shape_detection import split_into_cells, detect_board_state

# Configuración de la cámara y captura de frames
def capture_frame():
    cap = cv2.VideoCapture(0)  # Usar la cámara por defecto
    if not cap.isOpened():
        print("Error: No se puede abrir la cámara")
        return None
    
    ret, frame = cap.read()
    cap.release()

    if not ret:
        print("Error: No se pudo capturar el frame")
        return None

    return frame

# Función principal para capturar y detectar el estado del tablero
def capture_and_detect():
    while True:
        frame = capture_frame()
        if frame is None:
            break
        
        # Dividir el frame en celdas (3x3)
        cells = split_into_cells(frame)

        # Detectar el estado del tablero
        board_state = detect_board_state(cells)

        # Mostrar el estado del tablero en la consola
        for i in range(3):
            print(board_state[i])

        # Mostrar el frame con las celdas detectadas (opcional)
        cv2.imshow('Tic-Tac-Toe Detection', frame)

        # Salir si se presiona la tecla 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    capture_and_detect()
