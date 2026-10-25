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