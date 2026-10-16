"""Inferencia de um único vídeo com YOLOv8 para deteccao de bola de tenis.

Uso:
    python scripts/inferir_video.py --video <entrada.mp4> --model <modelo.pt> --output <saida.mp4> [--conf 0.3]

Gera:
    - Vídeo anotado com bounding boxes, centro e confiança
    - CSV com detecções por frame (frame, x1, y1, x2, y2, conf)
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
from pathlib import Path

import cv2

# Garante import do pacote src
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.cv.detector import TennisBallDetector


def processar_video(
    video_entrada: str,
    modelo: str,
    video_saida: str,
    conf: float = 0.3,
    mostrar: bool = False,
) -> dict:
    """Processa um vídeo inteiro com deteccao YOLOv8.

    Returns:
        Dict com estatísticas: total_frames, total_detections, frames_com_bola.
    """
    detector = TennisBallDetector(model_path=modelo, conf=conf)

    cap = cv2.VideoCapture(video_entrada)
    if not cap.isOpened():
        raise RuntimeError(f"Nao foi possivel abrir o vídeo: {video_entrada}")

    largura = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    altura = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Preparar writer de saída
    Path(video_saida).parent.mkdir(parents=True, exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(video_saida, fourcc, fps, (largura, altura))

    # CSV de detecções
    csv_path = str(Path(video_saida).with_suffix(".csv"))
    csv_file = open(csv_path, "w", newline="", encoding="utf-8")
    writer = csv.writer(csv_file)
    writer.writerow(["frame", "x1", "y1", "x2", "y2", "conf"])

    total_detections = 0
    frames_com_bola = 0
    frame_idx = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_idx += 1

            # Deteccao
            detections = detector.detect(frame)

            # Anotacao
            annotated = frame.copy()
            for x1, y1, x2, y2, c in detections:
                cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(
                    annotated, f"Ball {c:.2f}",
                    (x1, max(y1 - 10, 15)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1,
                )
                cx = (x1 + x2) // 2
                cy = (y1 + y2) // 2
                cv2.circle(annotated, (cx, cy), 6, (0, 255, 0), -1)
                writer.writerow([frame_idx, x1, y1, x2, y2, round(c, 4)])

            total_detections += len(detections)
            if len(detections) > 0:
                frames_com_bola += 1

            # Overlay de info
            cv2.putText(
                annotated, f"Frame: {frame_idx}/{total_frames}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2,
            )
            cv2.putText(
                annotated, f"Bolas: {len(detections)}", (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2,
            )

            out.write(annotated)

            if mostrar:
                cv2.imshow("Inferencia YOLOv8", annotated)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

    finally:
        cap.release()
        out.release()
        csv_file.close()
        if mostrar:
            cv2.destroyAllWindows()

    stats = {
        "video": video_entrada,
        "modelo": modelo,
        "total_frames": frame_idx,
        "total_detections": total_detections,
        "frames_com_bola": frames_com_bola,
        "taxa_deteccao": round(100 * frames_com_bola / frame_idx, 2) if frame_idx > 0 else 0.0,
        "video_saida": video_saida,
        "csv_saida": csv_path,
    }
    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description="Inferencia YOLOv8 em vídeo de tenis")
    parser.add_argument("--video", required=True, help="Caminho do vídeo de entrada")
    parser.add_argument("--model", default="yolov8n.pt", help="Caminho do modelo .pt")
    parser.add_argument("--output", required=True, help="Caminho do vídeo de saída")
    parser.add_argument("--conf", type=float, default=0.3, help="Confiança mínima (0-1)")
    parser.add_argument("--mostrar", action="store_true", help="Mostrar vídeo durante o processamento")
    args = parser.parse_args()

    print(f"Entrada:  {args.video}")
    print(f"Modelo:   {args.model}")
    print(f"Saída:    {args.output}")
    print(f"Conf:     {args.conf}")
    print("-" * 50)

    stats = processar_video(
        video_entrada=args.video,
        modelo=args.model,
        video_saida=args.output,
        conf=args.conf,
        mostrar=args.mostrar,
    )

    print("-" * 50)
    print("Resultado:")
    for k, v in stats.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
