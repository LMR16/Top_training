"""Pipeline de visao computacional: detector + tracker + court."""

from __future__ import annotations

from typing import Optional, Tuple, List

import cv2
import numpy as np

from src.cv.detector import TennisBallDetector
from src.cv.tracker import BallTracker
from src.cv.court import Court


class CVPPipeline:
    """Orquestra deteccao, rastreio e validacao de quadra."""

    def __init__(self, model_path: str = "yolov8n.pt", conf: float = 0.3) -> None:
        self.detector = TennisBallDetector(model_path=model_path, conf=conf)
        self.tracker = BallTracker()
        self.court = Court()
        self.frame_count = 0

    def process_frame(self, frame: np.ndarray) -> dict:
        """Processa um frame e retorna um dicionario com os resultados.

        Returns:
            Dict com chaves: 'ball_center', 'bounce_detected', 'detections',
            'inside_court', 'annotated_frame'.
        """
        self.frame_count += 1

        # Detecta bola
        center = self.detector.detect_center(frame)
        detections = self.detector.detect(frame)

        # Atualiza tracker
        bounce = self.tracker.update(center)

        # Verifica se esta dentro da quadra
        inside_court = False
        if center is not None:
            inside_court = self.court.contains(center)

        # Anotacao visual
        annotated = frame.copy()
        annotated = self._annotate(annotated, center, bounce, inside_court, detections)

        return {
            "frame_count": self.frame_count,
            "ball_center": center,
            "bounce_detected": bounce is True,
            "detections": detections,
            "inside_court": inside_court,
            "annotated_frame": annotated,
        }

    def _annotate(
        self,
        frame: np.ndarray,
        center: Optional[Tuple[int, int]],
        bounce: Optional[bool],
        inside_court: bool,
        detections: list,
    ) -> np.ndarray:
        """Desenha anotacoes no frame."""
        h, w = frame.shape[:2]

        # Desenha poligono da quadra se calibrado
        if self.court.calibrated and len(self.court.polygon) >= 2:
            pts = np.array(self.court.polygon, np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(frame, [pts], isClosed=True, color=(0, 255, 255), thickness=2)

        # Desenha deteccoes
        for x1, y1, x2, y2, conf in detections:
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                frame, f"Ball {conf:.2f}", (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1,
            )

        # Desenha centro da bola
        if center is not None:
            color = (0, 255, 0) if inside_court else (0, 0, 255)
            cv2.circle(frame, center, 8, color, -1)
            cv2.putText(
                frame, "BALL", (center[0] + 10, center[1]),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2,
            )

        # Indica quique
        if bounce is True:
            cv2.putText(
                frame, "QUICHE!", (w // 2 - 60, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3,
            )

        # Status da calibracao
        status = "Calibrado" if self.court.calibrated else "Nao calibrado"
        cv2.putText(
            frame, status, (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2,
        )

        return frame

    def set_court_polygon(self, polygon: list) -> None:
        """Define o poligono da quadra (vindo da calibracao da UI)."""
        self.court.polygon = [tuple(p) for p in polygon]
        self.court.finalize()

    def clear_court(self) -> None:
        self.court.clear()
        self.tracker.reset()
