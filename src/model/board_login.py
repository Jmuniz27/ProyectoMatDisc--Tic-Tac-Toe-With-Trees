import numpy as np

# Verifica si hay un ganador en el tablero
def check_winner(board_state):
    for i in range(3):
        # Verificar filas
        if board_state[i][0] == board_state[i][1] == board_state[i][2] and board_state[i][0] != "":
            return board_state[i][0]
        # Verificar columnas
        if board_state[0][i] == board_state[1][i] == board_state[2][i] and board_state[0][i] != "":
            return board_state[0][i]
    
    # Verificar diagonales
    if board_state[0][0] == board_state[1][1] == board_state[2][2] and board_state[0][0] != "":
        return board_state[0][0]
    if board_state[0][2] == board_state[1][1] == board_state[2][0] and board_state[0][2] != "":
        return board_state[0][2]
    
    # Si no hay ganador, retorna None
    return None

# Verifica si el tablero está lleno
def is_board_full(board_state):
    return not np.any(board_state == "")
