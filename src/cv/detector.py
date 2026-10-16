"""Detecao de bola de tenis via YOLOv8 Nano."""

from __future__ import annotations

from typing import Optional, List, Tuple

import cv2
import numpy as np
from ultralytics import YOLO

# Classe 'sports ball' no COCO (YOLOv8n pre-treinado)
CLASSE_BOLA = 32


class TennisBallDetector:
    """Detecta bolas de tenis em frames usando YOLOv8 Nano."""

    def __init__(self, model_path: str = "yolov8n.pt", conf: float = 0.3) -> None:
        self.model = YOLO(model_path)
        self.conf = conf

    def detect(self, frame: np.ndarray) -> List[Tuple[int, int, int, int, float]]:
        """Detecta bolas no frame.

        Returns:
            Lista de (x1, y1, x2, y2, confianca) para cada bola detectada.
        """
        results = self.model(frame, verbose=False, conf=self.conf)
        detections: List[Tuple[int, int, int, int, float]] = []

        for result in results:
            boxes = result.boxes
            if boxes is None:
                continue
            for box in boxes:
                cls = int(box.cls[0])
                if cls != CLASSE_BOLA:
                    continue
                conf = float(box.conf[0])
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                detections.append((int(x1), int(y1), int(x2), int(y2), conf))

        return detections

    def detect_center(self, frame: np.ndarray) -> Optional[Tuple[int, int]]:
        """Retorna o centro da bola mais confiante, ou None."""
        detections = self.detect(frame)
        if not detections:
            return None
        # Escolhe a deteccao com maior confianca
        best = max(detections, key=lambda d: d[4])
        x1, y1, x2, y2, _ = best
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        return cx, cy
