import math

def normalizar(a):
    return math.sqrt( a[2]**2+ a[1]**2 +  a[0]**2)

def pCruz(a, b):
    l1 = len(a)
    l2 = len(b)
    if l1 == l2 and l1 == 3:
        resultado = [a[1]*b[2] - a[2]*b[1],
                     a[2]*b[0] - a[0]*b[2],
                     a[0]*b[1] - a[1]*b[0]]
        return resultado

def pPunto(a, b):
    producto = 0
    for a,b in zip(a,b):
        producto = producto + a * b

    return producto


def dividir(vector: tuple, normal: float):
    return tuple(map(lambda item: item / normal, vector))

def restaVect(a, b):

    resultado = []

    for i in range(min(len(a), len(b))):
        resultado.append(a[i] - b[i])

    return resultado

