import math
import numpy as np

"""
Funcions pel fitxer dades_posturograf.py
"""
def quadrant_vector(vector):
    """
    Retorna el quadrant al que pertany un vector.
    
    Args:
    vector: Vector a calcular(en graus).
    
    Return: 
    El quadrant del vector.
    """
    quadrants = []
    if vector[0] > 0:
        if vector[1] > 0:
            return 1
        else:
            return 4
    else:
        if vector[1] > 0:
            return 2
        else:
            return 3

def quadrant_angle(angle):
    """
    Retorna el quadrant de l'angle especificat.

    Args:
    angle: L'angle a calcular(en graus).

    Returns:
    El quadrant de l'angle.
    """
    if angle < 0:
        angle += 360

    if 0 <= angle < 90:
        return 1
    elif 90 <= angle < 180:
        return 2
    elif 180 <= angle < 270:
        return 3
    else:
        return 4
    
def canvi_quadrant(angle, quad_from, quad_to):
    """
    Rota un angle per passar-lo d'un quadrant a un altre
    
    Args:
    angle: L'angle a rotar(en graus).
    quad_from: Quadrant al que pertany l'angle originalment.
    quad_to: Quadrant al que es vol portar l'angle.
    
    Returns:
    L'angle rotat en graus.
    """
    angle_rad = math.radians(angle)

    rotacio = ((quad_to - quad_from) * (2 * math.pi / 4)) % (2 * math.pi)

    nou_angle_rad = angle_rad + rotacio

    nou_angle_deg = math.degrees(nou_angle_rad)

    if nou_angle_deg < 0:
        nou_angle_deg += 360

    return nou_angle_deg

"""
Funcions pel fitxer carregar_dades_IMU.py
"""
def convertData(data, column, leftShift):
    """
    Converteix dades hexagessimals a decimals i aplica un backshift     
    Args:
    data: DataFrame amb les dades a convertir.
    column: Índex de la columna que es vol convertir.
    leftShift: Shift a aplicar a les dades.
    
    Returns:
    El DataFrame amb les dades de la columna actualitzades.    
    """
    for i in range(len(data)):
        temp = data.loc[i, column]
        unsigned = int(temp,16)

        if unsigned & (1 << 15) !=0:
            unsigned = -1*((1<<15)-(unsigned &((1<<15)-1)))
        
        data.loc[i,column] = unsigned / (1<< leftShift)
    return data

def convertDataHex(data, column):
    """
    Converteix dades hexagessimals a decimals.   
    Args:
    data: DataFrame amb les dades a convertir.
    column: Índex de la columna que es vol convertir.
    
    Returns:
    El DataFrame amb les dades de la columna actualitzades.    
    """
    for i in range(len(data)):
        temp = data.loc[i, column]
        if not temp.isnumeric():
            unsigned = int(temp,16)
        else:
            unsigned = int(temp)
 
        data.loc[i,column] = unsigned
    return data

def all_non_consecutive(arr):
    ans = []
    start = arr[0]
    index = 0
    for number in arr:
        if start == number:
            start += 1
            index += 1
            continue

        ans.append({'i': index, 'n': number})
        start = number + 1
        index += 1

    return ans

def grafica(llista, balance_test):
    temp = all_non_consecutive(llista)
    llista_resultat=[]
    aux_llista=[]
    aux_llista.append(llista[0])
    for i in temp:
        aux_llista.append(llista[i["i"]-1])
        aux_llista.append(i["n"])
    aux_llista.append(llista[-1])

    i=0
    while i < len(aux_llista):
        new_df = balance_test.loc[aux_llista[i]:aux_llista[i+1]]
        new_df.reset_index(inplace=True, drop=True)
        llista_resultat.append(new_df)
        i=i+2
    return llista_resultat

def find_discontinuity(lst):
    """
    Troba índex del primer valor on hi hagi una discontinuitat a la llista.
    Args:
    lst: Llista a on trobar la discontinuitat.

    Returns:
    Índex de la discontinuitat i llista fins la posició.
    """
    for i in range(1, len(lst)):
        if lst[i] != lst[i - 1] + 1:
            return i, lst[i - 1] + 1

    return len(lst), lst[len(lst)-1]

def obtenir_x_valors(llista, valor):
    """
    Obté tots els primers valors d'una llista de llistes amb dos valors.
    
    Args:
    lista_de_listas: La llista de llistes amb dos valors.

    Returns:
    Una llista amb tots els primers valors.
    """

    valors = []
    for l in llista:
        valors.append(l[valor])

    return valors
"""
Funcions pel fitxer carregar_dades_Postu.py
"""
def find_last_string_with_text(text, llista):
    for string in llista[::-1]:
        if text in string:
            return string
    return None

def dist_lim_normalitat(punt, conjunt_de_punts):
    """
    Calcula la distància al límit de la normalitat d'un punt de dos dimensions respecte d'un conjunt de punts de dos dimensions.

    Args:
    punt: El punt que del qual es vol calcular la distància.
    conjunto_de_puntos: El conjunto de puntos respecto del que se quiere calcular la distancia.

    Returns:
    La distancia al límite de la normalidad del punto respecto del conjunto de puntos.
    """

    media = np.mean(conjunt_de_punts, axis=0)
    desviacion_estandar = np.std(conjunt_de_punts, axis=0)
    distanciax = punt[0] - media[0]
    distanciay = punt[1] - media[1]
    #print(distanciax)
    #print(distanciay)
    #print(desviacion_estandar[0])
    #print(desviacion_estandar[1])
    return np.sqrt((distanciax / desviacion_estandar[0])**2 + (distanciay / desviacion_estandar[1])**2)