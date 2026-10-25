import os
import cv2
import numpy as np
import pydicom
import matplotlib.pyplot as plt

class ImagenDicom:

    def __init__(self, carpeta, nombre):
        self.carpeta = carpeta
        self.nombre = nombre
        self.carpeta_salida = "resultados"
        os.makedirs(self.carpeta_salida, exist_ok=True)

        self.filas = None
        self.columnas = None
        self.nombre_paciente = None
        self.modalidad = None
        self.voxel_alto = None
        self.voxel_largo = None
        self.voxel_ancho = None
        self.matriz_pixeles = None

        
        self.volumen = None
        self.voxel_vol = None

    
        self.matriz_rotacion = None
        self.volumen_rotado = None
        self.angulo = None
        self.volumen_copia = None
        self.corte_ecualizado = None

        self.cargar_dicom()
        self.escalar_y_reconstruir()