import cv2
import numpy as np


class HomographyManager:
    """
    Gerencia a calibração de 4 pontos da meia quadra e a matriz de homografia H.
    Sistema de coordenadas em metros:
      - Origem (0, 0): Canto 1 (Fundo Esquerdo)
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
        self.service_line_y = round(self.length_m - 6.40, 3)
        self.pixel_points = []
        self.H = None
        self.H_inv = None
        self.reproj_error_px = 0.0
        self.source_key = ""

    def get_court_corners_meters(self) -> np.ndarray:
        return np.array([
            [0.0, 0.0],
            [self.width_m, 0.0],
            [self.width_m, self.length_m],
            [0.0, self.length_m]
        ], dtype=np.float32)

    def calibrate(
        self,
        pixel_points: list,
        width_m: float = None,
        length_m: float = None,
        source_key: str = None
    ) -> dict:
        if len(pixel_points) != 4:
            raise ValueError("São necessários exatamente 4 pontos para calibrar a meia quadra.")

        if width_m is not None:
            self.width_m = float(width_m)
        if length_m is not None:
            self.length_m = float(length_m)
            self.service_line_y = round(self.length_m - 6.40, 3)
        if source_key is not None:
            self.source_key = str(source_key)

        self.pixel_points = [[float(p[0]), float(p[1])] for p in pixel_points]
        src_pts = np.array(self.pixel_points, dtype=np.float32)
        dst_pts = self.get_court_corners_meters()

        self.H, _ = cv2.findHomography(src_pts, dst_pts)
        self.H_inv, _ = cv2.findHomography(dst_pts, src_pts)

        reproj_pts = cv2.perspectiveTransform(dst_pts.reshape(-1, 1, 2), self.H_inv).reshape(-1, 2)
        errors = np.linalg.norm(src_pts - reproj_pts, axis=1)
        self.reproj_error_px = float(np.mean(errors))

        return self.to_dict()

    def load_from_dict(self, data: dict, source_key: str = None):
        if not data:
            return False

        # Se houver calibração salva especificamente para esta fonte de vídeo/câmera, prioriza ela
        by_source = data.get("by_source", {})
        if source_key and source_key in by_source:
            src_cal = by_source[source_key]
            if "pixel_points" in src_cal and len(src_cal["pixel_points"]) == 4:
                self.calibrate(
                    src_cal["pixel_points"],
                    width_m=src_cal.get("width_m", 8.23),
                    length_m=src_cal.get("length_m", 11.885),
                    source_key=source_key
                )
                return True

        if "pixel_points" not in data or len(data["pixel_points"]) != 4:
            return False

        self.calibrate(
            data["pixel_points"],
            width_m=data.get("width_m", 8.23),
            length_m=data.get("length_m", 11.885),
            source_key=data.get("source_key", "")
        )
        return True

    def is_calibrated(self) -> bool:
        return self.H is not None and len(self.pixel_points) == 4

    def pixel_to_meters(self, u: float, v: float) -> tuple:
        if not self.is_calibrated():
            return (0.0, 0.0, False)

        # 1. Verifica rigorosamente se o pixel (u, v) está dentro do polígono de 4 pontos calibrado
        poly = np.array(self.pixel_points, dtype=np.float32)
        dist_px = float(cv2.pointPolygonTest(poly, (float(u), float(v)), True))
        if dist_px < -5.0:
            # Fora do polígono calibrado na imagem -> ignora imediatamente
            pt = np.array([[[float(u), float(v)]]], dtype=np.float32)
            mapped = cv2.perspectiveTransform(pt, self.H)[0][0]
            return (round(float(mapped[0]), 3), round(float(mapped[1]), 3), False)

        # 2. Projeta para coordenadas métricas da meia quadra via Homografia H
        pt = np.array([[[float(u), float(v)]]], dtype=np.float32)
        mapped = cv2.perspectiveTransform(pt, self.H)[0][0]
        xm, ym = float(mapped[0]), float(mapped[1])

        tol = 0.08
        inside = (-tol <= xm <= self.width_m + tol) and (-tol <= ym <= self.length_m + tol)
        if inside:
            xm = min(max(xm, 0.0), self.width_m)
            ym = min(max(ym, 0.0), self.length_m)
        return (round(xm, 3), round(ym, 3), bool(inside))

    def to_dict(self) -> dict:
        return {
            "calibrated": self.is_calibrated(),
            "source_key": self.source_key,
            "width_m": self.width_m,
            "length_m": self.length_m,
            "service_line_y": self.service_line_y,
            "pixel_points": self.pixel_points,
            "reproj_error_px": round(self.reproj_error_px, 4)
        }
