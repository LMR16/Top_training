"""Utilitários de geometria: ponto dentro polígono, zonas por dificuldade."""


def point_in_polygon(point, polygon):
    x, y = point
    inside = False
    n = len(polygon)
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def divide_zones(dificuldade):
    zones = {
        "Basico": [
            {"nome": "Esquerda", "polygon": [(0, 0), (0.33, 0), (0.33, 1), (0, 1)]},
            {"nome": "Centro", "polygon": [(0.33, 0), (0.66, 0), (0.66, 1), (0.33, 1)]},
            {"nome": "Direita", "polygon": [(0.66, 0), (1, 0), (1, 1), (0.66, 1)]},
        ],
        "Medio": [
            {"nome": "Esquerda Profunda", "polygon": [(0, 0), (0.25, 0), (0.25, 0.6), (0, 0.6)]},
            {"nome": "Centro", "polygon": [(0.25, 0), (0.75, 0), (0.75, 1), (0.25, 1)]},
            {"nome": "Direita Profunda", "polygon": [(0.75, 0), (1, 0), (1, 0.6), (0.75, 0.6)]},
        ],
        "Avancado": [
            {"nome": "Esquerda Curta", "polygon": [(0, 0), (0.2, 0), (0.2, 0.4), (0, 0.4)]},
            {"nome": "Centro Curto", "polygon": [(0.4, 0), (0.6, 0), (0.6, 0.4), (0.4, 0.4)]},
            {"nome": "Direita Curta", "polygon": [(0.8, 0), (1, 0), (1, 0.4), (0.8, 0.4)]},
            {"nome": "Esquerda Longa", "polygon": [(0, 0.6), (0.2, 0.6), (0.2, 1), (0, 1)]},
            {"nome": "Centro Longo", "polygon": [(0.4, 0.6), (0.6, 0.6), (0.6, 1), (0.4, 1)]},
            {"nome": "Direita Longa", "polygon": [(0.8, 0.6), (1, 0.6), (1, 1), (0.8, 1)]},
        ],
    }
    return zones.get(dificuldade, zones["Basico"])


def normalizar_ponto(ponto, min_x, max_x, min_y, max_y):
    x, y = ponto
    nx = (x - min_x) / (max_x - min_x) if max_x != min_x else 0
    ny = (y - min_y) / (max_y - min_y) if max_y != min_y else 0
    return nx, ny


def mapear_para_mapa(ponto_frame, bounds_polygon):
    xs = [p[0] for p in bounds_polygon]
    ys = [p[1] for p in bounds_polygon]
    return normalizar_ponto(ponto_frame, min(xs), max(xs), min(ys), max(ys))
