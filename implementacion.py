from clases import GestorImagenes


def pedir_entero(mensaje, minimo, maximo):
    while True:
        texto = input(mensaje)
        if texto.lstrip("-").isdigit():
            numero = int(texto)
            if minimo <= numero <= maximo:
                return numero
        print("Valor no válido. Debe ser un entero entre", minimo, "y", maximo)

def pedir_decimal(mensaje):
    while True:
        try:
            return float(input(mensaje))
        except ValueError:
            print("Escribe un numero.")

def elegir_objeto(gestor):
    if len(gestor.imagenes) == 0:
        print("Primero debes cargar alguna carpeta (opcion 1 o 2).")
        return None
    nombres = gestor.listar()
    numero = pedir_entero("Elige el numero del objeto: ", 1, len(nombres))
    return gestor.imagenes[nombres[numero - 1]]

def main():
    gestor = GestorImagenes()

    while True:
        print()
        print("========== MENU DICOM ==========")
        print("1. Cargar una carpeta DICOM")
        print("2. Cargar las carpetas de clase (PPMI, Sarcoma y T2)")
        print("3. Ver informacion de los objetos cargados")
        print("4. Corregir angulo")
        print("5. Normalizar y ecualizar un corte")
        print("6. Segmentar, medir area y dibujar circulo")
        print("0. Salir")
        opcion = input("Opcion: ")

        if opcion == "1":
            ruta = input("Ruta de la carpeta con los .dcm: ")
            try:
                gestor.cargar_carpeta(ruta)
            except Exception as error:
                print("No se pudo cargar:", error)

        elif opcion == "2":
            ruta = input("Ruta de la carpeta que contiene PPMI, Sarcoma y T2 (Enter = datos): ")
            if ruta == "":
                ruta = "datos"
            gestor.cargar_carpetas_clase(ruta)

        elif opcion == "3":
            if len(gestor.imagenes) == 0:
                print("No hay nada cargado.")
            for nombre in gestor.imagenes:
                print()
                gestor.imagenes[nombre].mostrar_info()

        elif opcion == "4":
            obj = elegir_objeto(gestor)
            if obj is not None:
                angulo = pedir_decimal("Angulo de inclinacion en grados: ")
                obj.corregirAngulo(angulo)

        elif opcion == "5":
            obj = elegir_objeto(gestor)
            if obj is not None:
                total = obj.volumen.shape[0]
                indice = pedir_entero("Numero de corte (0 a " + str(total - 1) + "): ", 0, total - 1)
                obj.normalizar_y_ecualizar(indice)

        elif opcion == "6":
            obj = elegir_objeto(gestor)
            if obj is not None:
                print("Planos: 1. transversal  2. coronal  3. sagital")
                p = pedir_entero("Plano: ", 1, 3)
                if p == 1:
                    plano = "transversal"
                    maximo = obj.volumen.shape[0] - 1
                elif p == 2:
                    plano = "coronal"
                    maximo = obj.volumen.shape[1] - 1
                else:
                    plano = "sagital"
                    maximo = obj.volumen.shape[2] - 1
                indice = pedir_entero("Numero de corte (0 a " + str(maximo) + "): ", 0, maximo)
                umbral = pedir_entero("Umbral (1 a 254, 0 = automatico con Otsu): ", 0, 254)
                kernel = pedir_entero("Tamano del kernel (ej. 3, 5, 7): ", 1, 51)
                iteraciones = pedir_entero("Iteraciones de la apertura: ", 1, 20)
                zona = pedir_entero("Zona de interes (1 = la mas grande, 2 = la siguiente...): ", 1, 50)
                obj.segmentar(plano, indice, umbral, kernel, iteraciones, zona)

        elif opcion == "0":
            print("Hasta luego.")
            break

        else:
            print("Opcion no valida.")


main()