# Resumo e Mapa de Referência do Projeto — Top Training

> **Propósito deste arquivo:** Servir como fonte única de referência rápida (para desenvolvedores e assistentes de IA) sobre onde estão localizados todos os códigos, modelos, vídeos, dados e documentações do projeto.

---

## 1. Visão Geral do Projeto

O **Top Training** é um sistema de treinamento gamificado de tênis por visão computacional.
- **Motor de Visão Computacional (`trackers/` + `main.py`):** Detecção de bolas de tênis em movimento usando **YOLOv8 (`yolov8_best_2.pt`)**, filtro de movimento real (`cv2.absdiff`) para ignorar bolas paradas no chão, continuidade espacial, interpolação controlada via `pandas` e detecção automática do instante do quique (*bounce*) pela inversão da trajetória vertical $Y$.
- **Aplicação Web/Desktop (`app/`):** Interface em **HTML5 / CSS3 / JavaScript Puro** (Tema Escuro Esportivo estilo SwingVision) conectada ao back-end Python (**FastAPI**), com suporte a vídeos gravados e câmera ao vivo (**Iriun Webcam**), calibração interativa de 4 pontos com homografia $H$ (pixel $\rightarrow$ metros), validação de homografia (`UC09`), níveis de dificuldade (Básico 2 zonas, Médio 3 colunas, Avançado grade $3\times 2$), seleção de zona-foco, placar em tempo real com filtro de 1º quique, feedback sonoro/visual e ranking por nível salvo em JSON.

---

## 2. Mapa Completo de Diretórios e Arquivos

```text
Top_training/
├── main.py                         # [CLI] Script isolado para processar vídeos e salvar em runs/Ball_Tracker/
├── yolo_inference.py               # [CLI] Script de teste rápido de inferência/tracking do YOLO
├── video_to_frame.py               # [CLI] Extrator de frames de vídeos para anotação no Roboflow
├── requirements.txt                # Dependências do projeto (OpenCV, Ultralytics, Pandas, FastAPI, Uvicorn)
├── README.md                       # Apresentação geral do repositório
│
├── app/                            # [APP] Aplicativo completo (Front-end JS + Back-end Python FastAPI)
│   ├── __init__.py
│   ├── app_main.py                 # Servidor FastAPI (porta 8000), streaming MJPEG e abertura automática no navegador
│   ├── core/
│   │   ├── __init__.py
│   │   ├── homography.py           # Calibração de 4 pontos, matriz H (pixel <-> metros) e erro de reprojeção
│   │   ├── game_engine.py          # Zonas (Básico=2, Médio=3, Avançado=6), pontuação (+10/-5) e filtro de 1º quique
│   │   └── storage.py              # Persistência JSON de perfis, histórico de sessões, ranking e homografia
│   ├── data/
│   │   ├── homografia.json         # Calibração de 4 pontos persistida
│   │   └── profiles.json           # Perfis de jogadores e sessões salvas
│   └── static/
│       ├── index.html              # SPA com as 5 telas (Perfil/Fonte, Calibração, Zona-Foco, Treino, Resumo/Ranking)
│       ├── style.css               # Estilização Dark Mode Esportivo
│       └── app.js                  # Canvas 2D interativo, arraste de 4 pontos, WebAudio API e atualização ao vivo
│
├── trackers/                       # [CV] Pacote central de rastreamento e detecção de quiques
│   ├── __init__.py
│   └── ball_tracker.py             # Classe BallTracker (detect_frames, detect_frame c/ absdiff, interpolate, detect_bounces, draw_boxes)
│
├── models/                         # [MODELOS] Pesos treinados do YOLOv8
│   ├── yolov8_best_2.pt            # [PADRÃO ATUAL] Melhor modelo (mAP50=86.1%, Recall=81.8%, mAP50-95=62.4%)
│   ├── yolov8_best.pt              # 1ª versão treinada
│   ├── yolov8_best_3.pt            # 3ª versão treinada
│   └── yolov8_last*.pt             # Checkpoints finais de cada treino
│
├── src/
│   ├── input_videos/               # [VÍDEOS] Vídeos de entrada (.mp4 e .MOV) para testes e calibração
│   │   ├── treino_1.mp4, treino_2.mp4, treino_3.mp4
│   │   └── quadra_1.MOV, quadra_2.MOV, quadra_3.MOV
│   └── models/                     # Pesos base (yolov8n.pt, yolo5_last.pt)
│
├── stubs/                          # [CACHE] Detecções serializadas (.pkl) por vídeo e modelo
├── runs/
│   ├── Ball_Tracker/               # Vídeos numerados gerados pelo main.py (out_video_1.mp4, out_video_2.mp4...)
│   ├── saves_good_videos/          # Vídeos validados salvos pelo usuário
│   └── detect/                     # Saídas brutas de testes do YOLO
│
├── docs/                           # Documentação do projeto
│   ├── arquitetura_app_js.md       # Especificação das 20 decisões do App JS + FastAPI e Trabalhos Futuros (Smartwatch)
│   ├── Entrega_2/
│   │   ├── Projeto_integrador_rel_1 (1).tex
│   │   ├── Projeto_integrador_rel_1 (1).pdf
│   │   ├── Projeto_integrador_rel_1.md      # Transcrição completa do relatório em Markdown
│   │   └── requisitos_status.png            # Imagem 16:9 de status dos requisitos para apresentação no Canva
│   ├── escopo.md, arquitetura.md, roteiro.md, treino_modelo.md
│
└── skills/
    └── resume.md                   # Este arquivo de referência rápida
```

---

## 3. Como Executar

### 3.1. Abrir o Aplicativo Completo (Interface JS + FastAPI)
```powershell
.\.venv\Scripts\python.exe app/app_main.py
```
* Abre automaticamente o navegador em `http://127.0.0.1:8000`.

### 3.2. Rodar Apenas o Processamento de Vídeo em Lote (CLI)
```powershell
.\.venv\Scripts\python.exe main.py
```
* Processa o vídeo definido em `main.py` e salva sequencialmente em `runs/Ball_Tracker/out_video_N.mp4`.
