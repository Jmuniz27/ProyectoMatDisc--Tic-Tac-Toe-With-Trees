import pygame
import cv2
from MiniMax import ai_move, check_winner, is_board_full
from interface.pruebaCam import procesar_imagen

# Inicializar Pygame y cámara
pygame.init()
WIDTH, HEIGHT = 300, 300
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tic Tac Toe Cam")
font = pygame.font.SysFont(None, 60)

# Estado del juego
state = [["" for _ in range(3)] for _ in range(3)]
current_player = "X"
cam = cv2.VideoCapture(0)

def draw_board():
    screen.fill((255, 255, 255))
    # Dibujar líneas
    for i in range(1, 3):
        pygame.draw.line(screen, (0,0,0), (0, i*100), (WIDTH, i*100), 2)
        pygame.draw.line(screen, (0,0,0), (i*100, 0), (i*100, HEIGHT), 2)
    # Dibujar fichas
    for i in range(3):
        for j in range(3):
            if state[i][j] != "":
                label = font.render(state[i][j], True, (0,0,0))
                screen.blit(label, (j*100 + 30, i*100 + 20))

def capturar_jugada_con_camara():
    global state
    ret, frame = cam.read()
    if not ret:
        return
    frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    frame = cv2.flip(frame, 1)
    _, player_matrix = procesar_imagen(frame)
    if player_matrix:
        for i in range(3):
            for j in range(3):
                if state[i][j] == '' and player_matrix[i][j] == 'X':
                    state[i][j] = 'X'

# Bucle principal
running = True
while running:
    draw_board()
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Presionar espacio para hacer siguiente jugada
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            capturar_jugada_con_camara()

            # Revisar ganador
            winner = check_winner(state)
            if not winner:
                ai_move(state)
                winner = check_winner(state)

            if winner or is_board_full(state):
                print("Ganador:", winner if winner else "Empate")
                pygame.time.wait(2000)
                state = [["" for _ in range(3)] for _ in range(3)]  # Reiniciar

cam.release()
pygame.quit()
