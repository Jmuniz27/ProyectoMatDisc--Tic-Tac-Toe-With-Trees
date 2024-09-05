class Node:
    def _init_(self, state, player, move=None):
        self.state = state  # El estado del tablero
        self.player = player  # El jugador que hizo el último movimiento
        self.move = move  # El movimiento que llevó a este estado
        self.children = []  # Hijos de este nodo
        self.score = None  # El puntaje evaluado por Minimax para este nodo

    def add_child(self, child_node):
        self.children.append(child_node)

def print_board(state):
    for row in state:
        print(row)
    print()

def check_winner(state):
    for row in state:
        if row[0] == row[1] == row[2] and row[0] != '':
            return row[0]

    for col in range(3):
        if state[0][col] == state[1][col] == state[2][col] and state[0][col] != '':
            return state[0][col]

    if state[0][0] == state[1][1] == state[2][2] and state[0][0] != '':
        return state[0][0]

    if state[0][2] == state[1][1] == state[2][0] and state[0][2] != '':
        return state[0][2]

    return None

def is_board_full(state):
    for row in state:
        if '' in row:
            return False
    return True

def minimax(node, is_maximizing):
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
            score = minimax(child, False)
            best_score = max(best_score, score)
    else:
        best_score = float('inf')
        for child in node.children:
            score = minimax(child, True)
            best_score = min(best_score, score)
    
    node.score = best_score
    return best_score

def build_game_tree(state, player):
    root = Node(state, player)
    if check_winner(state) or is_board_full(state):
        return root

    next_player = 'O' if player == 'X' else 'X'

    for i in range(3):
        for j in range(3):
            if state[i][j] == '':
                new_state = [row[:] for row in state]
                new_state[i][j] = player
                child_node = build_game_tree(new_state, next_player)
                child_node.move = (i, j)  # Guardar el movimiento que llevó a este estado
                root.add_child(child_node)

    return root

def ai_move(state):
    # Construye el árbol de juego para el estado actual
    game_tree = build_game_tree(state, 'O')

    # Encuentra el mejor movimiento para la IA
    best_move = None
    best_score = -float('inf')

    for child in game_tree.children:
        score = minimax(child, False)
        if score > best_score:
            best_score = score
            best_move = child.move

    # Realiza el mejor movimiento en el tablero
    if best_move:
        row, col = best_move
        state[row][col] = 'O'
        return best_move
    return None

def player_move(state):
    while True:
        try:
            row = int(input("Ingresa la fila (0, 1, 2): "))
            col = int(input("Ingresa la columna (0, 1, 2): "))
            if state[row][col] == '':
                state[row][col] = 'X'
                return
            else:
                print("La casilla ya está ocupada, intenta de nuevo.")
        except (IndexError, ValueError):
            print("Entrada no válida, intenta de nuevo.")

def play_game():
    state = [['', '', ''],
             ['', '', ''],
             ['', '', '']]
    
    print("¡Bienvenido a Tic-Tac-Toe! Eres el jugador 'X'.")
    print_board(state)
    
    while True:
        # Turno del jugador humano
        player_move(state)
        print("Tu movimiento:")
        print_board(state)
        
        # Verificar si el jugador humano ha ganado
        if check_winner(state):
            print(f"¡El jugador {check_winner(state)} ha ganado!")
            break
        elif is_board_full(state):
            print("Es un empate.")
            break

        # Turno de la IA
        print("Turno de la IA:")
        ai_move(state)
        print_board(state)

        # Verificar si la IA ha ganado
        if check_winner(state):
            print(f"¡El jugador {check_winner(state)} ha ganado!")
            break
        elif is_board_full(state):
            print("Es un empate.")
            break

# Inicia el juego
play_game()