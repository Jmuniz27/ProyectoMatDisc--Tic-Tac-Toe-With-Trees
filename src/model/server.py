import av
import streamlit as st
import cv2
import numpy as np
from streamlit_webrtc import webrtc_streamer
import matplotlib.pyplot as plt
import time

#from model.interface.pruebaCam import procesar_imagen

st.title("Tic-Tac-Toe")
col1, col2 = st.columns(2)
col1.title("Camara")
col2.title("Matriz")

# Crear una matriz inicial
matriz_inicial = np.array([[0, 1, 0], [1, -1, 1], [0, 1, 0]])

# Crear una segunda matriz como ejemplo de siguiente jugada
matriz_siguiente = np.array([[1, 1, 0], [1, -1, 1], [0, -1, 1]])

# def transform(frame: av.VideoFrame):
#     imagen = frame.to_ndarray(format="bgr24")
#     tablero, matriz_actual = procesar_imagen(frame)
#     return matriz_actual

# Función para dibujar la matriz sin etiquetas
def dibujar_matriz(matriz):
    fig, ax = plt.subplots()
    ax.matshow(matriz, cmap='coolwarm')

    # Añadir "X" y "O" en la matriz
    for i in range(3):
        for j in range(3):
            c = matriz[j, i]
            if c == 1:
                ax.text(i, j, 'X', va='center', ha='center', color='white', fontsize=20)
            elif c == -1:
                ax.text(i, j, 'O', va='center', ha='center', color='white', fontsize=20)

    # Ocultar las etiquetas de fila y columna
    ax.set_xticks([])
    ax.set_yticks([])

    return fig

# Mostrar la cámara en la columna 1
with col1:
    webrtc_streamer(key="streamer", sendback_audio=False)

# Crear un espacio vacío en la columna 2 para actualizar la imagen de la matriz
matriz_placeholder = col2.empty()

# Dibujar la matriz inicial al principio
matriz_placeholder.pyplot(dibujar_matriz(matriz_inicial))

# Crear un botón de "Siguiente Jugada"
if col2.button("Siguiente Jugada"):
    # Hacer una transición entre la matriz inicial y la siguiente
    for alpha in np.linspace(0, 1, 20):
        matriz_transicion = (1 - alpha) * matriz_inicial + alpha * matriz_siguiente
        matriz_placeholder.pyplot(dibujar_matriz(np.round(matriz_transicion).astype(int)))
        time.sleep(0.01)  # Pausa para mostrar la transición

# Botón para reiniciar el juego
if col2.button("Reiniciar"):
    matriz_placeholder.pyplot(dibujar_matriz(matriz_inicial))
