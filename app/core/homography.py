import cv2
import numpy as np


class HomographyManager:
    """
    Gerencia a calibração de 4 pontos da meia quadra oposta e a matriz de homografia H.
    Sistema de coordenadas em metros (conforme relatório):
      - Origem (0, 0): Canto inferior esquerdo (linha de fundo esquerda)
      - Eixo X: Largura da quadra de simples (0 a 8,23 m)
      - Eixo Y: Profundidade em direção à rede (0 na linha de fundo até 11,885 m na rede)
      - Linha de saque: a 6,40 m da rede -> y = 11,885 - 6,40 = 5,485 m
    Ordem dos 4 pontos clicados na imagem:
      0: Fundo Esquerdo  -> (0.0, 0.0)
      1: Fundo Direito   -> (width_m, 0.0)
      2: Rede Direita    -> (width_m, length_m)
      3: Rede Esquerda   -> (0.0, length_m)
    """

    def __init__(self, width_m: float = 8.23, length_m: float = 11.885):
        self.width_m = float(width_m)
        self.length_m = float(length_m)
        self.service_line_y = round(self.length_m - 6.40, 3)  # 5.485 m a partir da linha de fundo
        self.pixel_points = []
        self.H = None
        self.H_inv = None
        self.reproj_error_px = 0.0

    def get_court_corners_meters(self) -> np.ndarray:
        return np.array([
            [0.0, 0.0],
            [self.width_m, 0.0],
            [self.width_m, self.length_m],
            [0.0, self.length_m]
        ], dtype=np.float32)

    def calibrate(self, pixel_points: list, width_m: float = None, length_m: float = None) -> dict:
        if len(pixel_points) != 4:
            raise ValueError("São necessários exatamente 4 pontos para calibrar a meia quadra.")

        if width_m is not None:
            self.width_m = float(width_m)
        if length_m is not None:
            self.length_m = float(length_m)
            self.service_line_y = round(self.length_m - 6.40, 3)

        self.pixel_points = [[float(p[0]), float(p[1])] for p in pixel_points]
        src_pts = np.array(self.pixel_points, dtype=np.float32)
        dst_pts = self.get_court_corners_meters()

        self.H, _ = cv2.findHomography(src_pts, dst_pts)
        self.H_inv, _ = cv2.findHomography(dst_pts, src_pts)

        # Calcula erro de reprojeção em pixels (validação UC09 / RNF04)
        reproj_pts = cv2.perspectiveTransform(dst_pts.reshape(-1, 1, 2), self.H_inv).reshape(-1, 2)
        errors = np.linalg.norm(src_pts - reproj_pts, axis=1)
        self.reproj_error_px = float(np.mean(errors))

        return self.to_dict()

    def load_from_dict(self, data: dict):
        if not data or "pixel_points" not in data or len(data["pixel_points"]) != 4:
            return False
        self.calibrate(
            data["pixel_points"],
            width_m=data.get("width_m", 8.23),
            length_m=data.get("length_m", 11.885)
        )
        return True

    def is_calibrated(self) -> bool:
        return self.H is not None and len(self.pixel_points) == 4

    def pixel_to_meters(self, u: float, v: float) -> tuple:
        if not self.is_calibrated():
            return (0.0, 0.0, False)

        pt = np.array([[[float(u), float(v)]]], dtype=np.float32)
        mapped = cv2.perspectiveTransform(pt, self.H)[0][0]
        xm, ym = float(mapped[0]), float(mapped[1])

        # Verifica se caiu dentro dos limites da meia quadra (com pequena tolerância de linha de 5 cm)
        tol = 0.05
        inside = (-tol <= xm <= self.width_m + tol) and (-tol <= ym <= self.length_m + tol)
        return (round(xm, 3), round(ym, 3), bool(inside))

    def to_dict(self) -> dict:
        return {
            "calibrated": self.is_calibrated(),
            "width_m": self.width_m,
            "length_m": self.length_m,
            "service_line_y": self.service_line_y,
            "pixel_points": self.pixel_points,
            "reproj_error_px": round(self.reproj_error_px, 4)
        }

