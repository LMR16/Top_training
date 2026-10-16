"""Script de validacao do modelo YOLOv8 com videos de teste.

Uso:
    python scripts/validar_modelo.py

Este script e INDEPENDENTE do app principal (src/main.py).
Carrega um vídeo de src/input_videos/, roda o YOLOv8 frame a frame e exibe
as detecções sobrepostas para validar se o modelo está detectando as bolas.
"""

from __future__ import annotations

import os
import sys
import cv2

# Garante que o pacote src seja encontrável
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.cv.detector import TennisBallDetector


INPUT_VIDEOS_DIR = os.path.join(os.path.dirname(__file__), "..", "src", "input_videos")


def listar_videos() -> list:
    if not os.path.isdir(INPUT_VIDEOS_DIR):
        return []
    return [
        f for f in os.listdir(INPUT_VIDEOS_DIR)
        if f.lower().endswith((".mp4", ".avi", ".mov"))
    ]


def main() -> None:
    videos = listar_videos()
    if not videos:
        print(f"Nenhum vídeo encontrado em: {INPUT_VIDEOS_DIR}")
        return

    print("Vídeos disponíveis para validação:")
    for i, v in enumerate(videos, 1):
        print(f"  {i}. {v}")

    escolha = input("\nEscolha o número do vídeo (ou Enter para o primeiro): ").strip()
    if not escolha:
        escolha = "1"

    try:
        idx = int(escolha) - 1
        video_path = os.path.join(INPUT_VIDEOS_DIR, videos[idx])
    except (ValueError, IndexError):
        print("Escolha inválida. Usando o primeiro vídeo.")
        video_path = os.path.join(INPUT_VIDEOS_DIR, videos[0])

    print(f"\nCarregando modelo YOLOv8 Nano...")
    detector = TennisBallDetector(model_path="yolov8n.pt", conf=0.3)

    print(f"Abrindo vídeo: {video_path}")
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Erro ao abrir o vídeo.")
        return

    total_frames = 0
    total_detections = 0
    frames_com_bola = 0

    print("\nPressione 'q' para sair, 'p' para pausar/despausar.")
    print("=" * 60)

    playing = True
    while True:
        if playing:
            ret, frame = cap.read()
            if not ret:
                print("\nFim do vídeo. Reiniciando...")
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            total_frames += 1

            # Detecção YOLO
            detections = detector.detect(frame)
            total_detections += len(detections)
            if len(detections) > 0:
                frames_com_bola += 1

            # Anotação
            annotated = frame.copy()
            h, w = annotated.shape[:2]

            for x1, y1, x2, y2, conf in detections:
                cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(
                    annotated, f"Ball {conf:.2f}",
                    (x1, max(y1 - 10, 15)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1,
                )
                cx = (x1 + x2) // 2
                cy = (y1 + y2) // 2
                cv2.circle(annotated, (cx, cy), 6, (0, 255, 0), -1)

            # Overlay de estatísticas
            cv2.putText(
                annotated, f"Frame: {total_frames}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2,
            )
            cv2.putText(
                annotated, f"Bolas neste frame: {len(detections)}", (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2,
            )
            cv2.putText(
                annotated, f"Total detecções: {total_detections}", (10, 90),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2,
            )

            cv2.imshow("Validacao YOLOv8 - Bola de Tenis", annotated)

        key = cv2.waitKey(33) & 0xFF  # ~30 fps
        if key == ord("q"):
            break
        elif key == ord("p"):
            playing = not playing
            print(f"{'Pausado' if not playing else 'Reproduzindo'}")

    cap.release()
    cv2.destroyAllWindows()

    print("\n" + "=" * 60)
    print("RESUMO DA VALIDAÇÃO:")
    print(f"  Frames processados: {total_frames}")
    print(f"  Frames com bola detectada: {frames_com_bola}")
    print(f"  Total de detecções (bounding boxes): {total_detections}")
    if total_frames > 0:
        print(f"  Taxa de detecção: {100 * frames_com_bola / total_frames:.1f}% dos frames")
    print("=" * 60)


if __name__ == "__main__":
    main()
