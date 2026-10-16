"""Detecao de bola de tenis com suporte a YOLOv8 e YOLOv5.

Deteta automaticamente o tipo do modelo com base na extensao/estrutura
e usa o backend apropriado (ultralytics para YOLOv8, torch.hub para YOLOv5).
"""

from __future__ import annotations

from typing import Optional, List, Tuple

import cv2
import numpy as np
import torch

try:
    from ultralytics import YOLO

    _ULTRALYTICS_DISPONIVEL = True
except Exception:
    _ULTRALYTICS_DISPONIVEL = False

# Classe 'sports ball' no COCO (YOLO pré-treinado)
CLASSE_BOLA_COCO = 32


class TennisBallDetector:
    """Detecta bolas de tenis em frames usando YOLOv8 ou YOLOv5."""

    def __init__(
        self,
        model_path: str = "yolov8n.pt",
        conf: float = 0.3,
        dispositivo: str | None = None,
    ) -> None:
        self.model_path = model_path
        self.conf = conf
        self.dispositivo = dispositivo or ("cuda" if torch.cuda.is_available() else "cpu")
        self.tipo: str | None = None
        self.modelo = None
        self._carregar()

    def _carregar(self) -> None:
        """Carrega o modelo detectando se eh YOLOv8 (ultralytics) ou YOLOv5."""
        import os

        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Modelo nao encontrado: {self.model_path}")

        # Tenta YOLOv8 via ultralytics primeiro
        if _ULTRALYTICS_DISPONIVEL:
            try:
                self.modelo = YOLO(self.model_path)
                self.tipo = "yolov8"
                print(f"[Detector] Modelo YOLOv8 carregado: {self.model_path}")
                return
            except Exception as e:
                print(f"[Detector] Falhou como YOLOv8: {e}")

        # Fallback: YOLOv5 via torch.hub
        try:
            self.modelo = torch.hub.load(
                "ultralytics/yolov5",
                "custom",
                path=self.model_path,
                device=self.dispositivo,
                trust_repo=True,
            )
            self.modelo.conf = self.conf
            self.tipo = "yolov5"
            print(f"[Detector] Modelo YOLOv5 carregado: {self.model_path}")
            return
        except Exception as e:
            print(f"[Detector] Falhou como YOLOv5: {e}")

        raise RuntimeError(f"Nao foi possivel carregar o modelo: {self.model_path}")

    def detect(
        self, frame: np.ndarray
    ) -> List[Tuple[int, int, int, int, float]]:
        """Detecta bolas no frame.

        Returns:
            Lista de (x1, y1, x2, y2, confianca) para cada bola detectada.
        """
        if self.tipo == "yolov8":
            return self._detect_v8(frame)
        if self.tipo == "yolov5":
            return self._detect_v5(frame)
        raise RuntimeError("Tipo de modelo nao definido.")

    # ------------------------------------------------------------------
    # Backend YOLOv8
    # ------------------------------------------------------------------
    def _detect_v8(
        self, frame: np.ndarray
    ) -> List[Tuple[int, int, int, int, float]]:
        detections: List[Tuple[int, int, int, int, float]] = []
        results = self.modelo(frame, verbose=False, conf=self.conf)
        for result in results:
            boxes = result.boxes
            if boxes is None:
                continue
            for box in boxes:
                cls = int(box.cls[0])
                # Aceita classe 'sports ball' (32) ou qualquer classe se o modelo for treinado so para tenis (classe 0)
                if cls not in (CLASSE_BOLA_COCO, 0):
                    continue
                conf = float(box.conf[0])
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                detections.append((int(x1), int(y1), int(x2), int(y2), conf))
        return detections

    # ------------------------------------------------------------------
    # Backend YOLOv5
    # ------------------------------------------------------------------
    def _detect_v5(
        self, frame: np.ndarray
    ) -> List[Tuple[int, int, int, int, float]]:
        detections: List[Tuple[int, int, int, int, float]] = []
        # YOLOv5 espera RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.modelo(frame_rgb)

        # results.xyxy e uma lista de tensores (uma por imagem no batch)
        pred = results.xyxy[0]  # tensor [n, 6]: x1, y1, x2, y2, conf, cls
        for *xyxy, conf, cls in pred:
            cls_int = int(cls)
            # YOLOv5 treinado so para tenis geralmente tem classe 0
            if cls_int not in (CLASSE_BOLA_COCO, 0):
                continue
            conf_float = float(conf)
            x1, y1, x2, y2 = [int(v) for v in xyxy]
            detections.append((x1, y1, x2, y2, conf_float))
        return detections

    def detect_center(self, frame: np.ndarray) -> Optional[Tuple[int, int]]:
        """Retorna o centro da bola mais confiante, ou None."""
        detections = self.detect(frame)
        if not detections:
            return None
        best = max(detections, key=lambda d: d[4])
        x1, y1, x2, y2, _ = best
        return (x1 + x2) // 2, (y1 + y2) // 2
