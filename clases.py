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

    def cargar_dicom(self):
        
        datasets = []
        for archivo in os.listdir(self.carpeta):
            if archivo.lower().endswith(".dcm"):
                ruta = os.path.join(self.carpeta, archivo)
                datasets.append(pydicom.dcmread(ruta))

        if len(datasets) == 0:
            raise ValueError("No se encontraron archivos .dcm en " + self.carpeta)

        datasets.sort(key=lambda ds: ds.InstanceNumber)

        primero = datasets[0]
        self.filas = int(primero.Rows)
        self.columnas = int(primero.Columns)
        self.nombre_paciente = str(primero.PatientName)
        self.modalidad = str(primero.Modality)
        self.voxel_alto = float(primero.PixelSpacing[0])
        self.voxel_largo = float(primero.PixelSpacing[1])
        self.voxel_ancho = float(primero.SliceThickness)

        cortes = []
        for ds in datasets:
            cortes.append(ds.pixel_array)
        self.matriz_pixeles = np.stack(cortes, axis=0)
