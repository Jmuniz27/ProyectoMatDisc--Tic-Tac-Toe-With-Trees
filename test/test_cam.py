import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import pytest
import numpy as np
import cv2
from interface.pruebaCam import es_circulo, es_x  # Asegúrate de importar tus funciones

class TestDeteccionFormas:
    @classmethod
    def setup_class(cls):
        """Configuración inicial para todos los tests"""
        cls.tamano_imagen = (300, 300, 3)
        cls.color_fondo = (0, 0, 0)
        cls.color_forma = (255, 255, 255)
        
        # Parámetros ajustables para los tests
        cls.radio_circulo = 50
        cls.grosor_x = 12
        cls.margen_borde = 5

    def crear_imagen_base(self):
        """Crea una imagen en blanco para los tests"""
        return np.zeros(self.tamano_imagen, dtype=np.uint8)

    def test_deteccion_circulo_perfecto(self):
        """Verifica que detecta correctamente un círculo perfecto"""
        # Configuración
        img = self.crear_imagen_base()
        centro, radio = (150, 150), 50
        cv2.circle(img, centro, radio, self.color_forma, -1)
        
        # Ejecución
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        contours, _ = cv2.findContours(gray, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        # Aserción
        assert len(contours) > 0, "No se encontraron contornos"
        assert es_circulo(contours[0]) == True, "Fallo en detección de círculo perfecto"

    def test_deteccion_x_clara(self):
        """Verifica que detecta correctamente una X bien definida"""
        # Configuración
        img = self.crear_imagen_base()
        grosor_linea = 10
        cv2.line(img, (100, 100), (200, 200), self.color_forma, grosor_linea)
        cv2.line(img, (100, 200), (200, 100), self.color_forma, grosor_linea)
        
        # Ejecución
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        contours, _ = cv2.findContours(gray, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        # Aserción
        assert len(contours) > 0, "No se encontraron contornos"
        assert es_x(contours[0]) == True, "Fallo en detección de X clara"

    def test_no_deteccion_formas(self):
        """Verifica que no detecta formas en imagen vacía"""
        img = self.crear_imagen_base()
        
        # Dibujar borde continuo (sin separación entre interior/exterior)
        cv2.rectangle(img, (1, 1), (self.tamano_imagen[1]-2, self.tamano_imagen[0]-2), 
                    self.color_forma, 1)
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
        
        # Usar RETR_EXTERNAL y simplificar contorno
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Deberíamos tener solo 1 contorno (el borde exterior)
        assert len(contours) == 1, f"Se encontraron {len(contours)} contornos. Se esperaba 1"
        
        # Verificar que no es identificado como círculo o X
        assert not es_circulo(contours[0]), "Falso positivo para círculo"
        assert not es_x(contours[0]), "Falso positivo para X"

    def test_deteccion_circulo_imperfecto(self):
        """Verifica detección con círculo ligeramente ovalado"""
        img = self.crear_imagen_base()
        # Dibujar elipse con relación de aspecto 1:1.2
        cv2.ellipse(img, (150, 150), (int(self.radio_circulo*1.1), int(self.radio_circulo*0.9)), 
                    0, 0, 360, self.color_forma, -1)
        
        # Preprocesamiento mejorado
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5,5), 0)
        _, thresh = cv2.threshold(blur, 127, 255, cv2.THRESH_BINARY_INV)
        
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contorno = max(contours, key=cv2.contourArea)
        
        assert es_circulo(contorno), "Debería detectar círculo imperfecto"

    def test_deteccion_x_con_ruido(self):
        """Verifica detección de X con ruido en la imagen"""
        img = self.crear_imagen_base()
        # Dibujar X más grande para mejor detección
        cv2.line(img, (50, 50), (250, 250), self.color_forma, self.grosor_x)
        cv2.line(img, (50, 250), (250, 50), self.color_forma, self.grosor_x)
        
        # Añadir ruido controlado
        ruido = np.random.normal(0, 20, img.shape).astype(np.uint8)
        img = cv2.add(img, ruido)
        
        # Procesamiento adaptativo
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.medianBlur(gray, 5)
        thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                    cv2.THRESH_BINARY_INV, 11, 2)
        
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contorno_x = max(contours, key=cv2.contourArea)
        
        assert es_x(contorno_x), "Debería detectar X con ruido"
