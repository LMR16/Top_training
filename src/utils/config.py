"""Configuracoes padrao da aplicacao."""

DEFAULT_CONFIG = {
    "camera": {"indice": 0, "largura": 640, "altura": 480},
    "yolo": {"modelo": "yolov8n.pt", "confianca": 0.3},
    "dificuldades": ["Basico", "Medio", "Avancado"],
    "cores": {
        "fundo_quadra": [30, 80, 120],
        "linha_quadra": [255, 255, 255],
        "acerto": [0, 255, 0],
        "erro": [255, 0, 0],
        "poligono_calibracao": [0, 255, 255],
    },
    "tamanho_ponto_mapa": 6,
}
