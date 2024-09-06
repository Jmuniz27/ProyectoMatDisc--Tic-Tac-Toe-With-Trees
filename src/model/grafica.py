import tkinter as tk
from tkinter import Button, Label, Canvas, Frame
import cv2
from PIL import Image, ImageTk
import numpy as np
from MiniMax import ai_move, player_move, print_board, check_winner, is_board_full

class TicTacToeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic Tac Toe con Computer Vision")
        self.root.geometry("1000x700")

        # Inicializar estado del juego
        self.state = [['', '', ''],
                      ['', '', ''],
                      ['', '', '']]
        self.cam = cv2.VideoCapture(0)

        # Dividimos la ventana en tres secciones: Cámara, Tablero, y Botones
        self.frame_camera = Frame(self.root)
        self.frame_camera.grid(row=0, column=0, padx=10, pady=10)

        self.frame_board = Frame(self.root)
        self.frame_board.grid(row=0, column=1, padx=10, pady=10)

        self.frame_buttons = Frame(self.root)
        self.frame_buttons.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        # Cámara
        self.label_camera = Label(self.frame_camera)
        self.label_camera.pack()

        # Tablero
        self.canvas = Canvas(self.frame_board, width=300, height=300, bg='white')
        self.canvas.pack()

        # Dibujar tablero inicial
        self.draw_board()

        # Botones de control
        self.btn_start = Button(self.frame_buttons, text="Iniciar Juego", command=self.start_game)
        self.btn_start.grid(row=0, column=0, padx=10, pady=10)

        self.btn_confirm = Button(self.frame_buttons, text="Confirmar Movimiento", command=self.confirm_move)
        self.btn_confirm.grid(row=0, column=1, padx=10, pady=10)

        self.btn_reset = Button(self.frame_buttons, text="Jugar de Nuevo", command=self.reset_game)
        self.btn_reset.grid(row=0, column=2, padx=10, pady=10)

        # Actualización de la cámara en vivo
        self.update_camera()

    def update_camera(self):
        ret, frame = self.cam.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)  # Rotar imagen para alinearla
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.label_camera.imgtk = imgtk
            self.label_camera.configure(image=imgtk)
        self.root.after(10, self.update_camera)

    def draw_board(self):
        self.canvas.delete("all")
        for i in range(1, 3):
            self.canvas.create_line(100 * i, 0, 100 * i, 300, width=2)
            self.canvas.create_line(0, 100 * i, 300, 100 * i, width=2)
        
        for i in range(3):
            for j in range(3):
                if self.state[i][j] == 'X':
                    self.canvas.create_line(100 * j + 20, 100 * i + 20, 100 * j + 80, 100 * i + 80, width=2, fill="blue")
                    self.canvas.create_line(100 * j + 80, 100 * i + 20, 100 * j + 20, 100 * i + 80, width=2, fill="blue")
                elif self.state[i][j] == 'O':
                    self.canvas.create_oval(100 * j + 20, 100 * i + 20, 100 * j + 80, 100 * i + 80, width=2, outline="red")

    def start_game(self):
        self.state = [['', '', ''],
                      ['', '', '']]
        self.draw_board()
        print("Juego iniciado")

    def confirm_move(self):
        player_move(self.state, self.cam)  # Actualizar estado con el movimiento del jugador
        self.draw_board()
        print("Movimiento confirmado")
        print_board(self.state)

        # Verificar si hay ganador o empate
        if check_winner(self.state):
            print(f"¡El jugador {check_winner(self.state)} ha ganado!")
        elif is_board_full(self.state):
            print("Es un empate.")
        else:
            self.ai_turn()

    def ai_turn(self):
        print("Turno de la IA:")
        ai_move(self.state)  # Movimiento de la IA
        self.draw_board()
        print_board(self.state)

        # Verificar si la IA ha ganado o empate
        if check_winner(self.state):
            print(f"¡El jugador {check_winner(self.state)} ha ganado!")
        elif is_board_full(self.state):
            print("Es un empate.")

    def reset_game(self):
        self.start_game()

    def close_app(self):
        self.cam.release()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = TicTacToeApp(root)
    root.protocol("WM_DELETE_WINDOW", app.close_app)
    root.mainloop()
