from flask import Flask, render_template, Response, redirect, url_for
import cv2
import time
from MiniMax import ai_move, check_winner, is_board_full
from interface.pruebaCam import procesar_imagen

app = Flask(__name__)

state = [['', '', ''], ['', '', ''], ['', '', '']]  # Estado inicial del juego
cam = None  # La cámara será inicializada al iniciar el juego


def open_camera_with_retries(max_retries=5, wait_time=2):
    """
    Intenta abrir la cámara con un número máximo de reintentos.
    Si no puede abrirla, espera y vuelve a intentarlo.
    """
    global cam
    retries = 0
    while retries < max_retries:
        cam = cv2.VideoCapture(0)
        if cam.isOpened():
            return True  # La cámara se abrió correctamente
        else:
            retries += 1
            print(f"Intento {retries}/{max_retries} para abrir la cámara fallido. Reintentando en {wait_time} segundos...")
            time.sleep(wait_time)  # Espera antes de volver a intentar
    return False  # No se pudo abrir la cámara después de todos los intentos


# Generar frames para la cámara
def gen_frames():
    global cam
    if cam is None or not cam.isOpened():
        if not open_camera_with_retries():
            return b''  # No pudo abrir la cámara, devuelve vacío

    while True:
        success, frame = cam.read()
        if not success:
            break
        else:
            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
            frame = cv2.flip(frame, 1)
            frame = cv2.flip(frame, 1)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/')
def index():
    return render_template('index.html', matrix=state)


@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


# Ruta para empezar el juego
@app.route('/start_game')
def start_game():
    global state, cam
    state = [['', '', ''], ['', '', ''], ['', '', '']]  # Reiniciar el estado
    if cam is not None:
        cam.release()  # Liberar la cámara si ya estaba en uso
    cam = None  # Reiniciar la cámara
    return redirect(url_for('index'))


# Ruta para realizar la jugada (simula el turno del jugador y del bot)
@app.route('/next_round')
def next_round():
    global state, cam
    if cam is None or not cam.isOpened():
        if not open_camera_with_retries():
            return redirect(url_for('index'))  # No pudo abrir la cámara, recarga la página
    # Toma una foto
    ret, frame = cam.read()
    if not ret:
        return redirect(url_for('index'))  # Si no se puede leer la cámara, recarga la página
    frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    frame = cv2.flip(frame, 1)
    frame = cv2.flip(frame, 1)
    # Procesar la imagen capturada para obtener la matriz
    _, player_matrix = procesar_imagen(frame)

    if player_matrix is not None:
        # Actualiza el estado con la jugada del jugador
        for i in range(3):
            for j in range(3):
                if state[i][j] == '' and player_matrix[i][j] == 'X':
                    state[i][j] = 'X'
        for fila in state:
            print(fila)

    # Verificar si el jugador ha ganado
    winner = check_winner(state)
    if winner:
        return render_template('index.html', matrix=state, message=f"¡El jugador {winner} ha ganado!")
    
    # Si no hay ganador, hacer el movimiento de la IA
    ai_move(state)

    # Verificar si la IA ha ganado
    winner = check_winner(state)
    if winner:
        return render_template('index.html', matrix=state, message=f"¡El jugador {winner} ha ganado!")
    
    # Verificar si es un empate
    if is_board_full(state):
        return render_template('index.html', matrix=state, message="Es un empate.")
    
    return redirect(url_for('index'))


if __name__ == '__main__':
    try:
        app.run(debug=True)
    finally:
        # Liberar la cámara y recursos de OpenCV cuando la aplicación se cierra
        if cam is not None:
            cam.release()
        cv2.destroyAllWindows()
