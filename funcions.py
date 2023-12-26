import math

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