"""Script para gerar versões comparativas de vídeos processados com diferentes modelos.

Uso:
    python scripts/processar_videos.py --modelo src/models/tennis_ball_v1.pt --versao v1

Processa todos os vídeos em src/input_videos/ e salva em output_videos/ com sufixo _vX.
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.inferir_video import processar_video


INPUT_VIDEOS_DIR = Path("src/input_videos")
OUTPUT_DIR = Path("output_videos")


def listar_videos() -> list[Path]:
    if not INPUT_VIDEOS_DIR.exists():
        return []
    return sorted(
        [p for p in INPUT_VIDEOS_DIR.iterdir() if p.suffix.lower() in (".mp4", ".avi", ".mov")]
    )


def processar_todos(modelo: str, versao: str, conf: float = 0.3) -> list[dict]:
    """Processa todos os vídeos de entrada com um modelo específico.

    Args:
        modelo: Caminho do .pt
        versao: Sufixo de versão (ex: "baseline", "v1", "v2")
        conf: Confiança mínima

    Returns:
        Lista de estatísticas por vídeo.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    videos = listar_videos()

    if not videos:
        print(f"Nenhum vídeo encontrado em {INPUT_VIDEOS_DIR}")
        return []

    print(f"Processando {len(videos)} vídeo(s) com modelo: {modelo} (versão: {versao})")

    resultados = []
    for video_path in videos:
        nome_base = video_path.stem
        saida = OUTPUT_DIR / f"{nome_base}_{versao}.mp4"
        print(f"\n--- Processando: {video_path.name} -> {saida.name} ---")

        try:
            stats = processar_video(
                video_entrada=str(video_path),
                modelo=modelo,
                video_saida=str(saida),
                conf=conf,
            )
            resultados.append(stats)
            print(f"  OK: {stats['total_detections']} detecções em {stats['total_frames']} frames "
                  f"({stats['taxa_deteccao']}% com bola)")
        except Exception as e:
            print(f"  ERRO: {e}")

    # Salva CSV consolidado
    csv_path = OUTPUT_DIR / f"comparacao_{versao}.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "video", "modelo", "total_frames", "total_detections",
            "frames_com_bola", "taxa_deteccao", "video_saida", "csv_saida"
        ])
        writer.writeheader()
        for r in resultados:
            writer.writerow(r)
    print(f"\nCSV consolidado salvo em: {csv_path}")

    return resultados


def main() -> None:
    parser = argparse.ArgumentParser(description="Processa vídeos com um modelo YOLO")
    parser.add_argument("--modelo", required=True, help="Caminho do modelo .pt")
    parser.add_argument("--versao", required=True, help="Sufixo da versão (ex: baseline, v1, v2)")
    parser.add_argument("--conf", type=float, default=0.3, help="Confiança mínima")
    args = parser.parse_args()

    processar_todos(
        modelo=args.modelo,
        versao=args.versao,
        conf=args.conf,
    )


if __name__ == "__main__":
    main()
