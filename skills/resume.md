# Resumo e Mapa de Referência do Projeto — Top Training

> **Propósito deste arquivo:** Servir como fonte única de referência rápida (para desenvolvedores e assistentes de IA) sobre onde estão localizados todos os códigos, modelos, vídeos, dados e documentações do projeto, diferenciando claramente o **que já existe e está funcional** do **que está planejado na documentação**.

---

## 1. Visão Geral do Projeto

O **Top Training** é um sistema de visão computacional voltado à análise de treinos de tênis.
- **Estado Atual (Implementado):** Pipeline de detecção e rastreamento de bola de tênis em vídeo usando **YOLOv8 customizado (`yolov8_best.pt`)**, filtragem de falsos positivos pela maior confiança por frame, cache de detecções via `pickle` (`stubs/`), interpolação linear de frames sem detecção via `pandas` e renderização do vídeo anotado com OpenCV.
- **Meta do Produto (Planejado em `docs/`):** Aplicação desktop com interface gráfica, captura ao vivo via câmera (Iriun Webcam), calibração manual da quadra por polígono, detecção de quiques (*bounces*) e pontuação por zonas de dificuldade (Básico, Médio, Avançado).

---

## 2. Mapa de Diretórios e Arquivos Atuais (Estado Real)

```text
Top_training/
├── main.py                         # [ATIVO] Ponto de entrada principal do pipeline de vídeo + interpolação
├── yolo_inference.py               # [ATIVO] Script simples para testar inferência bruta do YOLO
├── requirements.txt                # Dependências base do projeto
├── README.md                       # Apresentação geral do repositório
├── .gitignore                      # Arquivos e pastas ignorados pelo Git
│
├── trackers/                       # [ATIVO] Pacote de rastreamento e pós-processamento
│   ├── __init__.py
│   └── ball_tracker.py             # Classe BallTracker (detecção YOLO, cache pickle, interpolação Pandas, desenho OpenCV)
│
├── models/                         # [ATIVO] Pesos do modelo YOLOv8 treinado para bola de tênis
│   ├── yolov8_best.pt              # Melhor peso do treinamento (usado em main.py e yolo_inference.py)
│   └── yolov8_last.pt              # Último checkpoint do treinamento
│
├── stubs/                          # [ATIVO] Cache de detecções para acelerar execuções repetidas
│   └── ball_detections.pkl         # Lista serializada de detecções frame a frame do vídeo de entrada
│
├── runs/                           # [ATIVO] Saídas geradas pelo processamento de vídeo e YOLO
│   ├── output_video.mp4            # Vídeo final gerado pelo main.py (com caixa amarela e centro verde interpolado)
│   └── detect/
│       ├── predict/                # Saída do teste bruto yolo_inference.py (8224226-hd_1280_720_30fps.avi)
│       └── predict2/               # Saída do teste bruto yolo_inference.py (input_video.avi)
│
├── src/                            # Recursos de mídia e modelos base (futura raiz modular planejada)
│   ├── input_videos/               # [ATIVO] Vídeos de entrada para testes (1280x720 @ 30fps)
│   │   ├── input_video.mp4         # Vídeo padrão usado pelo main.py (214 frames)
│   │   ├── 17290112-hd_1280_720_30fps.mp4
│   │   └── 8224226-hd_1280_720_30fps.mp4
│   └── models/                     # Pesos base/legados
│       ├── yolov8n.pt              # Modelo base YOLOv8 Nano (COCO)
│       ├── yolo5_last.pt           # Modelo legado YOLOv5
│       └── .gitkeep
│
├── notebooks/                      # [ATIVO] Experimentação e preparação de Dataset
│   ├── training.ipynb              # Download do dataset Roboflow e ajuste de diretórios
│   └── tennis-ball-detection-6/    # Dataset baixado do Roboflow (formato YOLOv8, 1 classe: 'tennis ball')
│       ├── data.yaml               # Configuração do dataset
│       └── tennis-ball-detection-6/
│           ├── train/              # Imagens e labels de treino
│           ├── valid/              # Imagens e labels de validação
│           └── test/               # Imagens e labels de teste
│
├── docs/                           # Documentação de escopo, arquitetura e planejamento
│   ├── escopo.md                   # Requisitos funcionais do app e regras de negócio
│   ├── arquitetura.md              # Estrutura modular planejada (src/ui, src/cv, src/data, src/utils)
│   ├── roteiro.md                  # Roadmap de 6 fases do projeto
│   └── treino_modelo.md            # Guia planejado para extração de frames e comparação de modelos
│
├── skills/                         # Referências rápidas para contexto de desenvolvimento e IA
│   └── resume.md                   # Este arquivo de mapeamento geral do projeto
│
└── .venv/                          # Ambiente virtual Python 3.12
```

---

## 3. Onde Está Cada Lógica no Código Atual

### 3.1. Execução Principal — `main.py`
Localizado na raiz (`main.py`), executa o fluxo ponta a ponta:
1. Define os caminhos principais:
   - Vídeo de entrada: `src/input_videos/input_video.mp4`
   - Vídeo de saída: `runs/output_video.mp4`
   - Modelo: `models/yolov8_best.pt`
   - Cache (stub): `stubs/ball_detections.pkl`
2. Carrega todos os frames do vídeo em memória com `cv2.VideoCapture`.
3. Instancia `BallTracker(model_path)`.
4. Obtém as detecções chamando `tracker.detect_frames(frames, read_stub=True, stub_path=stub_path)`.
5. Interpola detecções ausentes com `tracker.interpolate_ball_positions(ball_detections)`.
6. Desenha as anotações visuais com `tracker.draw_boxes(frames, ball_detections)`.
7. Exporta o vídeo final em `runs/output_video.mp4` (codec `mp4v`, 30 FPS).

### 3.2. Rastreamento e Interpolação — `trackers/ball_tracker.py`
Contém a classe `BallTracker`:
- **`__init__(self, model_path)`**: Carrega o modelo `YOLO(model_path)` da biblioteca `ultralytics`.
- **`detect_frames(self, frames, read_stub=False, stub_path=None)`**:
  - Se `read_stub=True` e o arquivo `stub_path` existir (`os.path.exists`), carrega e retorna a lista de detecções via `pickle`.
  - Caso contrário, processa cada frame chamando `detect_frame(frame)` e salva o resultado em `stub_path`.
- **`detect_frame(self, frame)`**:
  - Roda `self.model.predict(frame, conf=0.15, verbose=False)[0]`.
  - Seleciona apenas a caixa com **maior nível de confiança** (`max(results.boxes, key=lambda b: b.conf[0].item())`) e armazena no dicionário com chave `1`: `{1: [x1, y1, x2, y2]}`.
- **`interpolate_ball_positions(self, ball_positions)`**:
  - Converte a lista de dicionários em um `pandas.DataFrame` com colunas `['x1', 'y1', 'x2', 'y2']`.
  - Preenche falhas de detecção usando interpolação linear seguida de `bfill()` e `ffill()`.
  - Retorna a lista reconstruída no formato `[{1: [x1, y1, x2, y2]}, ...]`.
- **`draw_boxes(self, video_frames, ball_detections)`**:
  - Calcula o centro `(center_x, center_y)` da bola e desenha um círculo verde preenchido (`(0, 255, 0)`, raio 6).
  - Desenha a caixa delimitadora amarela (`(0, 255, 255)`, espessura 2) ao redor da bola.

### 3.3. Teste Rápido de Inferência — `yolo_inference.py`
Script enxuto na raiz para testar o modelo `models/yolov8_best.pt` diretamente sobre `src/input_videos/input_video.mp4` com `conf=0.2` e `save=True`, imprimindo as *bounding boxes* do primeiro frame no terminal.

---

## 4. Pontos de Atenção (Divergências entre `docs/` e o Código Atual)

Para evitar confusões durante o desenvolvimento, observe as diferenças entre o que está escrito em `docs/` e o que existe de fato no repositório:

1. **Ponto de Entrada (`main.py` vs `src/main.py`):**
   - O `README.md` e `docs/arquitetura.md` mencionam `python src/main.py`, porém `src/main.py` **não existe** atualmente. O código funcional está em **`main.py` na raiz** e em **`trackers/ball_tracker.py`**.
2. **Módulos Planejados Ainda Não Criados:**
   - As pastas `src/ui/`, `src/cv/`, `src/data/`, `src/utils/`, `scripts/` e `tests/` descritas em `docs/arquitetura.md` e `docs/treino_modelo.md` são parte do planejamento das próximas fases e ainda não foram criadas no disco.
3. **Duas Pastas de Modelos (`models/` vs `src/models/`):**
   - **`models/` (na raiz):** Contém os pesos treinados ativos (`yolov8_best.pt` e `yolov8_last.pt`). É esta pasta que `main.py` e `yolo_inference.py` utilizam.
   - **`src/models/`:** Contém os modelos base/antigos (`yolov8n.pt` e `yolo5_last.pt`).
4. **Biblioteca de Interface Gráfica:**
   - Os documentos em `docs/` mencionam `DearPyGui`, mas o arquivo `requirements.txt` especifica `customtkinter==5.2.2`.
5. **Dependências no Ambiente Virtual (`.venv`):**
   - O código em `trackers/ball_tracker.py` utiliza `pandas` (instalado no `.venv` junto ao `ultralytics`), embora `pandas` não esteja listado explicitamente no `requirements.txt`.

---

## 5. Comandos Úteis de Referência

```powershell
# Executar o pipeline principal (usando o Python do ambiente virtual)
.\.venv\Scripts\python.exe main.py

# Executar teste simples de inferência do YOLO
.\.venv\Scripts\python.exe yolo_inference.py
```
&gt; **Dica sobre o Cache (`stubs/`):** Se você trocar o vídeo em `main.py` ou alterar o modelo/confiança em `ball_tracker.py`, apague o arquivo `stubs/ball_detections.pkl` (ou passe `read_stub=False`) para forçar uma nova detecção pelo YOLO.

