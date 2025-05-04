import pytest
from src.model.MinMax import check_winner, is_board_full, ai_move

def test_check_winner_horizontal(sample_boards):
    assert check_winner(sample_boards['x_wins']) == 'X'
    assert check_winner(sample_boards['o_wins']) == 'O'

def test_check_winner_none(empty_board):
    assert check_winner(empty_board) is None

def test_is_board_full(sample_boards, empty_board):
    assert is_board_full(sample_boards['draw']) is True
    assert is_board_full(empty_board) is False

def test_ai_move(empty_board):
    ai_move(empty_board)
    # Verifica que la IA hizo exactamente un movimiento
    assert sum(cell == 'O' for row in empty_board for cell in row) == 1