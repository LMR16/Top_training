"""Extrai frames de vídeos de entrada para anotação manual do dataset.

Uso:
    python scripts/extrair_frames.py --video src/input_videos/input_video.mp4 --saida data/tennis_ball_dataset/images/train --a cada 10

Extrai 1 frame a cada N frames do vídeo e salva como JPG para posterior anotação com LabelImg/CVAT.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import cv2


def extrair_frames(video_path: str, saida_dir: str, a_cada: int = 10, max_frames: int | None = None) -> int:
    """Extrai frames de um vídeo.

    Args:
        video_path: Caminho do vídeo de entrada.
        saida_dir: Pasta de saída para salvar os frames.
        a_cada: Extrair 1 frame a cada N frames.
        max_frames: Limite máximo de frames extraídos (None = todos).

    Returns:
        Número de frames extraídos.
    """
    Path(saida_dir).mkdir(parents=True, exist_ok=True)

    nome_base = Path(video_path).stem
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Nao foi possivel abrir o vídeo: {video_path}")

    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    contador = 0
    salvos = 0
    frame_idx = 0

    print(f"Video: {video_path}")
    print(f"Total de frames: {total}")
    print(f"Extraindo 1 frame a cada {a_cada} frames para: {saida_dir}")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_idx % a_cada == 0:
                nome_arquivo = f"{nome_base}_frame{frame_idx:06d}.jpg"
                caminho = Path(saida_dir) / nome_arquivo
                cv2.imwrite(str(caminho), frame)
                salvos += 1
                print(f"  Salvo: {nome_arquivo} ({salvos})", end="\r")

                if max_frames is not None and salvos >= max_frames:
                    break

            frame_idx += 1
            contador += 1

    finally:
        cap.release()

    print(f"\nConcluído: {salvos} frames extraídos de {contador} frames totais.")
    return salvos


def main() -> None:
    parser = argparse.ArgumentParser(description="Extrai frames de vídeo para anotação")
    parser.add_argument("--video", required=True, help="Caminho do vídeo de entrada")
    parser.add_argument("--saida", required=True, help="Pasta de saída para frames")
    parser.add_argument("--a-cada", type=int, default=10, help="Extrair 1 frame a cada N frames (padrão: 10)")
    parser.add_argument("--max", type=int, default=None, help="Limite máximo de frames extraídos")
    args = parser.parse_args()

    extrair_frames(
        video_path=args.video,
        saida_dir=args.saida,
        a_cada=args.a_cada,
        max_frames=args.max,
    )


if __name__ == "__main__":
    main()
