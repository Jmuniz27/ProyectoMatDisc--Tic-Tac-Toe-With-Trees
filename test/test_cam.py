import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import pytest
import numpy as np
import cv2
from interface.pruebaCam import es_circulo, es_x, procesar_imagen

class TestDeteccionFormas:
    @classmethod
    def setup_class(cls):
        """Configuración inicial para tests"""
        cls.tamano_imagen = (400, 400, 3)  # Imagen más grande para mejor detección
        cls.color_fondo = (0, 0, 0)
        cls.color_forma = (255, 255, 255)
        cls.radio_circulo = 60  # Radio aumentado
        cls.grosor_x = 12  # Grosor aumentado

    def crear_imagen_base(self):
        """Crea imagen de prueba base"""
        return np.zeros(self.tamano_imagen, dtype=np.uint8)

    def test_deteccion_circulo_perfecto(self):
        """Test para círculo perfecto"""
        img = self.crear_imagen_base()
        cv2.circle(img, (200, 200), self.radio_circulo, self.color_forma, -1)
        
        # Preprocesamiento mejorado
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5,5), 0)
        _, thresh = cv2.threshold(blur, 127, 255, cv2.THRESH_BINARY_INV)
        
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        assert len(contours) > 0, "No se encontraron contornos"
        assert es_circulo(contours[0]), "Debería detectar círculo perfecto"

    def test_deteccion_x_clara(self):
        """Test mejorado para X"""
        img = self.crear_imagen_base()
        
        # Dibujar X más grande y definida
        cv2.line(img, (100, 100), (300, 300), self.color_forma, self.grosor_x)
        cv2.line(img, (100, 300), (300, 100), self.color_forma, self.grosor_x)
        
        # Preprocesamiento
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.medianBlur(gray, 5)
        _, thresh = cv2.threshold(blur, 127, 255, cv2.THRESH_BINARY_INV)
        
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contorno_x = max(contours, key=cv2.contourArea)
        assert es_x(contorno_x), "Debería detectar X clara"

    def test_no_deteccion_formas(self):
        """Test para imagen vacía"""
        img = self.crear_imagen_base()
        cv2.rectangle(img, (5, 5), 
                     (self.tamano_imagen[1]-6, self.tamano_imagen[0]-6), 
                     self.color_forma, 2)
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        assert len(contours) == 1, "Debería encontrar solo el borde"
        assert not es_circulo(contours[0]), "Falso positivo para círculo"
        assert not es_x(contours[0]), "Falso positivo para X"

    def test_deteccion_circulo_imperfecto(self):
        """Test para círculo ovalado"""
        img = self.crear_imagen_base()
        
        # Dibujar elipse más pronunciada
        cv2.ellipse(img, (200, 200), 
                   (int(self.radio_circulo*1.3), int(self.radio_circulo*0.7)), 
                   45, 0, 360, self.color_forma, -1)
        
        # Preprocesamiento
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5,5), 0)
        _, thresh = cv2.threshold(blur, 127, 255, cv2.THRESH_BINARY_INV)
        
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contorno = max(contours, key=cv2.contourArea)
        assert es_circulo(contorno), "Debería detectar círculo imperfecto"

    def test_deteccion_x_con_ruido(self):
        """Test para X con ruido"""
        img = self.crear_imagen_base()
        
        # Dibujar X grande
        cv2.line(img, (80, 80), (320, 320), self.color_forma, self.grosor_x)
        cv2.line(img, (80, 320), (320, 80), self.color_forma, self.grosor_x)
        
        # Añadir ruido controlado
        ruido = np.random.normal(0, 25, img.shape).astype(np.uint8)
        img = cv2.add(img, ruido)
        
        # Procesamiento adaptativo
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.medianBlur(gray, 5)
        thresh = cv2.adaptiveThreshold(
            blur, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contorno_x = max(contours, key=cv2.contourArea)
        assert es_x(contorno_x), "Debería detectar X con ruido"