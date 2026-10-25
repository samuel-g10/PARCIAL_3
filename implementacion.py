from clases import GestorImagenes


def pedir_entero(mensaje, minimo, maximo):
    while True:
        texto = input(mensaje)
        if texto.lstrip("-").isdigit():
            numero = int(texto)
            if minimo <= numero <= maximo:
                return numero
        print("Valor no válido. Debe ser un entero entre", minimo, "y", maximo)