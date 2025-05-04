import cv2
import numpy as np
from interface.pruebaCam import main as process_camera_input

class Node:
    def __init__(self, state, player, move=None):
        self.state = [row[:] for row in state]  # Deep copy
        self.player = player
        self.move = move
        self.children = []
        self.score = None

    def add_child(self, child_node):
        self.children.append(child_node)

def print_board(state):
    print("\nTablero Actual:")
    for i, row in enumerate(state):
        print(f" {row[0]} | {row[1]} | {row[2]} ")
        if i < 2:
            print("-----------")
    print()

def check_winner(state):
    # Verificar filas y columnas
    for i in range(3):
        if state[i][0] == state[i][1] == state[i][2] != ' ':
            return state[i][0]
        if state[0][i] == state[1][i] == state[2][i] != ' ':
            return state[0][i]
    
    # Verificar diagonales
    if state[0][0] == state[1][1] == state[2][2] != ' ':
        return state[0][0]
    if state[0][2] == state[1][1] == state[2][0] != ' ':
        return state[0][2]
    
    return None

def is_board_full(state):
    return all(cell != ' ' for row in state for cell in row)

def minimax(node, is_maximizing, alpha=-float('inf'), beta=float('inf')):
    winner = check_winner(node.state)
    if winner == 'O':
        return 10
    elif winner == 'X':
        return -10
    elif is_board_full(node.state):
        return 0

    if is_maximizing:
        best_score = -float('inf')
        for child in node.children:
            score = minimax(child, False, alpha, beta)
            best_score = max(best_score, score)
            alpha = max(alpha, best_score)
            if beta <= alpha:
                break
        return best_score
    else:
        best_score = float('inf')
        for child in node.children:
            score = minimax(child, True, alpha, beta)
            best_score = min(best_score, score)
            beta = min(beta, best_score)
            if beta <= alpha:
                break
        return best_score

def build_game_tree(state, player):
    root = Node(state, player)
    if check_winner(state) or is_board_full(state):
        return root

    next_player = 'O' if player == 'X' else 'X'
    
    for i in range(3):
        for j in range(3):
            if state[i][j] == ' ':
                new_state = [row[:] for row in state]
                new_state[i][j] = player
                child_node = build_game_tree(new_state, next_player)
                child_node.move = (i, j)
                root.add_child(child_node)
    
    return root

def ai_move(state):
    if is_board_full(state):
        return None

    game_tree = build_game_tree(state, 'O')
    best_move = None
    best_score = -float('inf')

    for child in game_tree.children:
        score = minimax(child, False)
        if score > best_score:
            best_score = score
            best_move = child.move

    if best_move:
        row, col = best_move
        state[row][col] = 'O'
        return best_move
    return None

def player_move(state, cam):
    while True:
        print("Mostrando tu tablero físico en la cámara...")
        print("Por favor, coloca tu ficha 'X' y presiona 'q' para confirmar")
        
        # Procesar entrada de la cámara
        process_camera_input(state, cam)
        
        # Mostrar estado actual después del movimiento
        print_board(state)
        
        # Verificar si el movimiento fue válido
        move_made = any(state[i][j] == 'X' for i in range(3) for j in range(3))
        if move_made:
            break
        else:
            print("Movimiento no detectado. Intenta nuevamente.")

def initialize_board():
    return [[' ' for _ in range(3)] for _ in range(3)]

def play_game():
    board = initialize_board()
    cam = cv2.VideoCapture(0)
    
    try:
        while True:
            print_board(board)
            
            # Turno del jugador (X)
            print("Tu turno (X) - Usa la cámara para colocar tu ficha")
            player_move(board, cam)
            
            # Verificar estado del juego
            winner = check_winner(board)
            if winner == 'X':
                print_board(board)
                print("¡Ganaste! 🎉")
                break
                
            if is_board_full(board):
                print_board(board)
                print("¡Empate! 🤝")
                break
                
            # Turno de la IA (O)
            print("Turno de la IA (O)...")
            ai_move_result = ai_move(board)
            
            if ai_move_result:
                print(f"IA movió a: {ai_move_result}")
            else:
                print("IA no pudo mover (tablero lleno?)")
            
            # Verificar estado del juego
            winner = check_winner(board)
            if winner == 'O':
                print_board(board)
                print("¡La IA ganó! 🤖")
                break
                
            if is_board_full(board):
                print_board(board)
                print("¡Empate! 🤝")
                break
                
    finally:
        cam.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    print("Bienvenido a Tic-Tac-Toe con IA (Minimax) y Detección por Cámara")
    print("Instrucciones:")
    print("1. Coloca tu ficha 'X' en el tablero físico")
    print("2. Muestra el tablero a la cámara")
    print("3. Presiona 'q' cuando hayas colocado tu ficha")
    print("\nIniciando juego...")
    play_game()