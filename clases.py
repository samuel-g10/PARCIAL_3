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

    def escalar_y_reconstruir(self):
            
            cortes_grandes = []
            for corte in self.matriz_pixeles:
                grande = cv2.resize(corte, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
                cortes_grandes.append(grande)
            self.volumen = np.stack(cortes_grandes, axis=0)

            self.voxel_vol = (self.voxel_alto / 2, self.voxel_largo / 2, self.voxel_ancho)

    def volumen_a_usar(self):
        if self.volumen_rotado is not None:
            return self.volumen_rotado
        return self.volumen
 
    def normalizar_uint8(self, imagen):
        imagen = imagen.astype(np.float32)
        imagen = cv2.normalize(imagen, None, 0, 255, cv2.NORM_MINMAX)
        return imagen.astype(np.uint8)

    def corregirAngulo(self, angulo):
            cortes, filas, columnas = self.volumen.shape
            centro = (columnas / 2, filas / 2)

            self.matriz_rotacion = cv2.getRotationMatrix2D(centro, angulo, 1.0)

            rotados = []
            for i in range(cortes):
                corte_rotado = cv2.warpAffine(self.volumen[i], self.matriz_rotacion, (columnas, filas))
                rotados.append(corte_rotado)

            self.volumen_rotado = np.stack(rotados, axis=0)
            self.angulo = angulo
            print("Volumen rotado", angulo, "grados. Guardado en volumen_rotado.")

    def normalizar_y_ecualizar(self, indice):
    
        self.volumen_copia = self.volumen_a_usar().copy()

        corte = self.volumen_copia[indice]
        corte8 = self.normalizar_uint8(corte)
        ecualizado = cv2.equalizeHist(corte8)
        self.corte_ecualizado = ecualizado

        figura, ejes = plt.subplots(1, 3, figsize=(15, 4))
        ejes[0].hist(corte8.ravel(), bins=256, range=(0, 256))
        ejes[0].set_title("Histograma antes de ecualizar")
        ejes[1].hist(ecualizado.ravel(), bins=256, range=(0, 256))
        ejes[1].set_title("Histograma después de ecualizar")
        ejes[2].imshow(ecualizado, cmap="gray")
        ejes[2].set_title("Imagen ecualizada (corte " + str(indice) + ")")
        plt.tight_layout()

        base = os.path.join(self.carpeta_salida, self.nombre + "_ecualizado_corte" + str(indice))
        plt.savefig(base + "_grafico.png")
        cv2.imwrite(base + "_imagen.png", ecualizado)
        print("Guardado:", base + "_grafico.png")
        print("Guardado:", base + "_imagen.png")
        plt.show()
        plt.close()

    def segmentar(self, plano, indice, umbral, tam_kernel, iteraciones, numero_zona=1):
        volumen = self.volumen_a_usar()
        if plano == "transversal":
            corte = volumen[indice, :, :]
            mm_vertical = self.voxel_vol[0]
            mm_horizontal = self.voxel_vol[1]
        elif plano == "coronal":
            corte = volumen[:, indice, :]
            mm_vertical = self.voxel_vol[2]
            mm_horizontal = self.voxel_vol[1]
        else:  # sagital
            corte = volumen[:, :, indice]
            mm_vertical = self.voxel_vol[2]
            mm_horizontal = self.voxel_vol[0]

        aspecto = mm_vertical / mm_horizontal
        corte = cv2.resize(corte, None, fx=1, fy=aspecto, interpolation=cv2.INTER_LINEAR)
        mm_pixel = mm_horizontal
        imagen = self.normalizar_uint8(corte)
        
        if umbral == 0:
            umbral, binaria = cv2.threshold(imagen, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        else:
            umbral, binaria = cv2.threshold(imagen, umbral, 255, cv2.THRESH_BINARY_INV)
        print("Umbral usado:", umbral)

        kernel = np.ones((tam_kernel, tam_kernel), np.uint8)
        abierta = cv2.morphologyEx(binaria, cv2.MORPH_OPEN, kernel, iterations=iteraciones)