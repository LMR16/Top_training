"""Treino de YOLOv8 Nano customizado para deteccao de bola de tenis.

Uso:
    python scripts/treinar_modelo.py --data data/tennis_ball_dataset/data.yaml --modelo yolov8n.pt --epocas 50 --saida src/models/tennis_ball_v1.pt

Requisitos:
    - Dataset já anotado em formato YOLO (imagens + labels .txt)
    - Arquivo data.yaml configurado
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ultralytics import YOLO


def treinar(
    data_yaml: str,
    modelo_base: str = "yolov8n.pt",
    epocas: int = 50,
    imgsz: int = 640,
    batch: int = 16,
    saida: str = "src/models/tennis_ball_custom.pt",
    nome_run: str = "tenis_ball",
) -> str:
    """Treina um YOLOv8 Nano para bola de tenis.

    Returns:
        Caminho do melhor modelo salvo (.pt).
    """
    print("=" * 60)
    print("TREINO YOLOv8 Nano - Bola de Tenis")
    print("=" * 60)
    print(f"Dataset:      {data_yaml}")
    print(f"Modelo base:  {modelo_base}")
    print(f"Epochas:      {epocas}")
    print(f"Tamanho img:  {imgsz}")
    print(f"Batch:        {batch}")
    print(f"Saida:        {saida}")
    print("=" * 60)

    # Carrega modelo base (pré-treinado COCO) para transfer learning
    model = YOLO(modelo_base)

    # Treino
    results = model.train(
        data=data_yaml,
        epochs=epocas,
        imgsz=imgsz,
        batch=batch,
        name=nome_run,
        project="runs/detect",
        patience=10,       # early stopping
        save=True,
        cache=False,
        device="auto",     # usa GPU se disponível, senão CPU
    )

    # Caminho do melhor modelo
    melhor_modelo = Path("runs/detect") / nome_run / "weights" / "best.pt"
    print(f"\nMelhor modelo salvo em: {melhor_modelo}")

    # Copia para o destino final se solicitado
    if saida:
        Path(saida).parent.mkdir(parents=True, exist_ok=True)
        import shutil
        if melhor_modelo.exists():
            shutil.copy2(str(melhor_modelo), saida)
            print(f"Modelo copiado para: {saida}")
        else:
            print("AVISO: melhor modelo não encontrado após treino.")

    # Métricas de validação
    print("\n--- Métricas de Validação ---")
    metrics = model.val()
    print(f"mAP50:  {metrics.box.map50:.4f}")
    print(f"mAP50-95: {metrics.box.map:.4f}")
    print(f"Precisão: {metrics.box.mp:.4f}")
    print(f"Recall:   {metrics.box.mr:.4f}")

    return str(saida) if saida else str(melhor_modelo)


def main() -> None:
    parser = argparse.ArgumentParser(description="Treino YOLOv8 para bola de tenis")
    parser.add_argument("--data", required=True, help="Caminho do data.yaml do dataset")
    parser.add_argument("--modelo", default="yolov8n.pt", help="Modelo base (yolov8n.pt)")
    parser.add_argument("--epocas", type=int, default=50, help="Numero de épocas")
    parser.add_argument("--imgsz", type=int, default=640, help="Tamanho da imagem")
    parser.add_argument("--batch", type=int, default=16, help="Tamanho do batch")
    parser.add_argument("--saida", default="src/models/tennis_ball_custom.pt", help="Caminho do modelo de saída")
    parser.add_argument("--nome-run", default="tenis_ball", help="Nome da execução no runs/")
    args = parser.parse_args()

    treinar(
        data_yaml=args.data,
        modelo_base=args.modelo,
        epocas=args.epocas,
        imgsz=args.imgsz,
        batch=args.batch,
        saida=args.saida,
        nome_run=args.nome_run,
    )


if __name__ == "__main__":
    main()
