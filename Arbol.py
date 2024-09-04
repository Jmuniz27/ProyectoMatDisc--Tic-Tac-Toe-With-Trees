# No se guíen de esto, solo es una forma general
#Falta implementar correctamente, sólo es una idea ;)

#                                                                           LEER COMENTARIOS

tablero_inicial = [' ' for _ in range(9)]

def mostrar_tablero(tablero):
    for i in range(3):
        print(tablero[3*i:3*(i+1)])

def hay_ganador(tablero, jugador):
    combinaciones_ganadoras = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8], 
        [0, 4, 8], [2, 4, 6] 
    ]
    for combinacion in combinaciones_ganadoras:
        if all(tablero[i] == jugador for i in combinacion):
            return True
    return False

def es_empate(tablero):
    return ' ' not in tablero

def es_fin_del_juego(tablero):
    return hay_ganador(tablero, 'X') or hay_ganador(tablero, 'O') or es_empate(tablero)

def minimax(tablero, profundidad, es_maximizar):
    if hay_ganador(tablero, 'X'):
        return -1
    elif hay_ganador(tablero, 'O'):
        return 1
    elif es_empate(tablero):
        return 0

    if es_maximizar:
        mejor_valor = -float('inf')
        for i in range(9):
            if tablero[i] == ' ':
                tablero[i] = 'O'
                valor = minimax(tablero, profundidad + 1, False)
                tablero[i] = ' '
                mejor_valor = max(mejor_valor, valor)
        return mejor_valor
    else:
        mejor_valor = float('inf')
        for i in range(9):
            if tablero[i] == ' ':
                tablero[i] = 'X'
                valor = minimax(tablero, profundidad + 1, True)
                tablero[i] = ' '
                mejor_valor = min(mejor_valor, valor)
        return mejor_valor

def encontrar_mejor_movimiento(tablero):
    mejor_valor = -float('inf')
    mejor_movimiento = -1
    for i in range(9):
        if tablero[i] == ' ':
            tablero[i] = 'O'
            valor = minimax(tablero, 0, False)
            tablero[i] = ' '
            if valor > mejor_valor:
                mejor_valor = valor
                mejor_movimiento = i
    return mejor_movimiento

def jugar_tic_tac_toe():
    tablero = [' ' for _ in range(9)]
    jugador_actual = 'X'

    while not es_fin_del_juego(tablero):
        if jugador_actual == 'X':
            movimiento = int(input("Selecciona una posición (1-9): ")) - 1
            if tablero[movimiento] != ' ':
                print("Posición inválida. Intenta de nuevo.")
                continue
            tablero[movimiento] = 'X'
        else:
            movimiento = encontrar_mejor_movimiento(tablero)
            tablero[movimiento] = 'O'

        mostrar_tablero(tablero)
        jugador_actual = 'O' if jugador_actual == 'X' else 'X'

    if hay_ganador(tablero, 'X'):
        print("¡Has ganado!")
    elif hay_ganador(tablero, 'O'):
        print("¡La computadora ha ganado!")
    else:
        print("Es un empate.")

jugar_tic_tac_toe()
