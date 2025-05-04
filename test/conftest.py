import pytest

@pytest.fixture
def empty_board():
    """Tablero vacío de 3x3."""
    return [[" " for _ in range(3)] for _ in range(3)]

@pytest.fixture
def sample_boards():
    """Diccionario con tableros de ejemplo para pruebas."""
    return {
        'x_wins': [["X", "X", "X"], [" ", "O", " "], ["O", " ", " "]],  # X gana en fila 0
        'o_wins': [["O", "X", " "], ["O", "X", " "], ["O", " ", "X"]],   # O gana en columna 0
        'draw':   [["X", "O", "X"], ["X", "X", "O"], ["O", "X", "O"]],   # Empate
    }