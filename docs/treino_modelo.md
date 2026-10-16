# Roteiro de Treino e Comparação de Modelos - Bola de Tênis

## Objetivo
Melhorar a detecção de bolas de tênis com YOLOv8 Nano customizado, saindo da taxa atual de ~1.4% (baseline COCO) para algo próximo de 80-90% nos vídeos de teste.

## Etapas

### 1. Extração de frames para anotação
Extrair frames dos 3 vídeos de teste para criar o dataset:
```powershell
.venv\Scripts\python.exe scripts/extrair_frames.py --video src/input_videos/input_video.mp4 --saida data/tennis_ball_dataset/images/train --a-cada 15 --max 100
.venv\Scripts\python.exe scripts/extrair_frames.py --video src/input_videos/17290112-hd_1280_720_30fps.mp4 --saida data/tennis_ball_dataset/images/train --a-cada 15 --max 100
.venv\Scripts\python.exe scripts/extrair_frames.py --video src/input_videos/8224226-hd_1280_720_30fps.mp4 --saida data/tennis_ball_dataset/images/val --a-cada 15 --max 50
```

### 2. Anotação manual
Anotar as bolas nos frames extraídos usando LabelImg, CVAT ou Roboflow.
- Formato: YOLO (.txt com `class x_center y_center width height` normalizado 0-1)
- Classe 0: `tennis_ball`
- Salvar em `data/tennis_ball_dataset/labels/train` e `labels/val`

### 3. Treino do modelo
Treinar YOLOv8n com transfer learning:
```powershell
.venv\Scripts\python.exe scripts/treinar_modelo.py --data data/tennis_ball_dataset/data.yaml --modelo yolov8n.pt --epocas 50 --saida src/models/tennis_ball_v1.pt --nome-run tenis_v1
```

### 4. Comparação de versões
Gerar vídeos anotados para cada versão do modelo:
```powershell
# Baseline (COCO pré-treinado)
.venv\Scripts\python.exe scripts/processar_videos.py --modelo yolov8n.pt --versao baseline --conf 0.3

# Modelo customizado v1
.venv\Scripts\python.exe scripts/processar_videos.py --modelo src/models/tennis_ball_v1.pt --versao v1 --conf 0.3

# Modelo customizado v2 (mais épocas/dados)
.venv\Scripts\python.exe scripts/processar_videos.py --modelo src/models/tennis_ball_v2.pt --versao v2 --conf 0.3
```

Saídas em `output_videos/`:
- `<nome>_baseline.mp4`
- `<nome>_v1.mp4`
- `<nome>_v2.mp4`

### 5. Avaliação
- Comparar `mAP50`, precisão e recall em `runs/detect/`
- Comparar taxa de detecção nos vídeos de saída
- Selecionar o melhor modelo para integrar ao `src/cv/pipeline.py`

## Estrutura de saída
```
output_videos/
  input_video_baseline.mp4
  input_video_v1.mp4
  input_video_v2.mp4
  17290112-hd_1280_720_30fps_baseline.mp4
  ...
  comparacao_baseline.csv
  comparacao_v1.csv
```

## Arquivos-chave
- `scripts/extrair_frames.py` — prepara frames para anotação
- `scripts/treinar_modelo.py` — treina YOLOv8n customizado
- `scripts/processar_videos.py` — gera comparações versionadas
- `scripts/inferir_video.py` — inferência de um único vídeo
- `data/tennis_ball_dataset/data.yaml` — config do dataset
- `src/models/*.pt` — modelos treinados
