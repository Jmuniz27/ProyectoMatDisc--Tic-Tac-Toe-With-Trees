class Node:
    def __init__(self, state, player, move=None):
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
                root.add_child(child_node)

    return root

def get_best_move(root):
    best_move = None
    best_score = -float('inf')

    for child in root.children:
        score = minimax(child, False)
        if score > best_score:
            best_score = score
            best_move = child.move

    return best_move

# Uso
initial_state = [['', '', ''],
                 ['', '', ''],
                 ['', '', '']]

# Construye el árbol de juego a partir del estado inicial
game_tree = build_game_tree(initial_state, 'O')

# Encuentra el mejor movimiento usando el árbol
best_move = None
best_score = -float('inf')

for child in game_tree.children:
    score = minimax(child, False)
    if score > best_score:
        best_score = score
        best_move = child.move

print(f"El mejor movimiento para 'O' es: {best_move}")
