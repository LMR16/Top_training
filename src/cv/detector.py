"""Detecção de bola de tênis via YOLOv8 Nano."""

from ultralytics import YOLO


class TennisBallDetector:
    def __init__(self, model_path: str = "yolov8n.pt") -> None:
        self.model = YOLO(model_path)

    def detect(self, frame):
        results = self.model(frame, verbose=False)
        return results
