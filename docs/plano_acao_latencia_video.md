# Plano de Ação: Redução de Latência e Aumento da Velocidade de Transmissão de Vídeo

Este documento estrutura o plano técnico em **4 fases práticas** para eliminar o atraso (*delay*) entre a câmera do celular (Iriun Webcam / USB / Wi-Fi), o processamento de visão computacional (YOLOv8) e a exibição no aplicativo Web (`Top_training/app/`), visando atingir as metas **RNF02 ($\ge 30\text{ FPS}$)** e **RNF03 ($\le 150\text{ ms}$)**.

---

## Diagnóstico Atual (Causas do Delay)

1. **Fila de Buffer do OpenCV (`cv2.VideoCapture`):** Por padrão, o OpenCV armazena de 3 a 5 frames antigos num buffer FIFO interno. Como a inferência YOLO demora ~60–100 ms por frame, o `cap.read()` lê frames que aconteceram entre `300 ms` e `600 ms` atrás.
2. **Loop Síncrono (Captura + YOLO + Codificação JPEG na mesma Thread):** No modelo atual, a captura da câmera fica bloqueada esperando o YOLO terminar a detecção e o `cv2.imencode('.jpg')` comprimir a imagem.
3. **Resolução Total sem Recorte de ROI (Região de Interesse):** O modelo analisa a imagem inteira ($1920 \times 1080$ reescalada para $640 \times 640$), mesmo quando a meia quadra calibrada ocupa apenas ~45% da área do frame.
4. **Transmissão MJPEG + Polling HTTP:** A codificação repetida de cada frame completo em JPEG no Python e o envio por stream multipart adicionam ~15–25 ms por frame.

---

## Fase 1 — Captura Assíncrona "Zero-Buffer" (Ganho imediato: -350 ms a -500 ms)
**Complexidade:** Baixa | **Impacto:** Muito Alto

1. **Criar a classe `CameraBufferCleanerThread` (Leitura Contínua em Background):**
   - Uma *thread* dedicada roda exclusivamente `cap.read()` na velocidade máxima da câmera (30/60 FPS) e sobrescreve apenas a variável `self.latest_frame` protegida por um `Lock` leve.
   - Quando a *thread* do YOLO pedir um frame, ela pega **sempre o frame do exato milissegundo atual**, descartando automaticamente frames atrasados.
2. **Configurar Flag DirectShow / MSMF e `CAP_PROP_BUFFERSIZE = 1`:**
   - Inicializar no Windows com `cv2.VideoCapture(cam_idx, cv2.CAP_DSHOW)` e definir:
     ```python
     cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
     cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
     cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
     cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
     cap.set(cv2.CAP_PROP_FPS, 30)
     ```
   - Reduzir a captura ao vivo de `1080p` para `720p` corta pela metade o tempo de transferência USB/Wi-Fi e de conversão de cor (`cvtColor`), sem perda para o YOLO (que já opera internamente em `640px`).

---

## Fase 2 — Desacoplamento entre Vídeo Ao Vivo e Inferência YOLO (Vídeo a 30 FPS Lisos)
**Complexidade:** Média | **Impacto:** Alto

1. **Três Threads Independentes (Arquitetura Produtor-Consumidor):**
   - **Thread A (Captura):** Lê da câmera a 30 FPS e atualiza `latest_raw_frame`.
   - **Thread B (Transmissão de Vídeo):** Lê `latest_raw_frame`, desenha a última posição conhecida da bola `(cx, cy)` e os quiques já confirmados, e envia ao navegador a **30 FPS constantes** (mesmo que o YOLO rode a 12–15 FPS). Assim, a imagem na tela nunca engasga.
   - **Thread C (Inferência YOLO + Quiques):** Consome o frame mais recente disponível, roda `tracker.detect_frame()`, calcula a parábola vertical $Y(t)$ usando o *timestamp* real (`time.perf_counter()`) em vez do índice de frame fixo, e atualiza as coordenadas da bola e dos quiques.
2. **Vantagem no Cálculo do Quique em Tempo Real:**
   - Usando o tempo real $\Delta t$ de cada detecção e ajustando uma janela curta de **5 pontos (`window=2`)** no modo ao vivo, mesmo que alguns frames sejam pulados pela câmera, o ponto de inflexão no chão é detectado com precisão.

---

## Fase 3 — Otimização do Modelo YOLOv8 (Ganho: 2x a 3x mais FPS na Inferência)
**Complexidade:** Média | **Impacto:** Alto

1. **Exportação para ONNX Runtime / OpenVINO (CPU) ou TensorRT FP16 (GPU NVIDIA):**
   - Caso o computador possua GPU NVIDIA (CUDA): rodar `model.predict(..., half=True, device=0)` com `imgsz=512` reduz o tempo de inferência de ~70 ms para **~8 a 12 ms por frame** (> 80 FPS).
   - Caso rode em CPU: exportar `yolov8_best_2.pt` para **ONNX** (`model.export(format="onnx", imgsz=512)`) ou **OpenVINO** reduz o tempo em CPU pela metade.
2. **Recorte Dinâmico da Região da Quadra (ROI Cropping):**
   - Após calibrar os 4 pontos da meia quadra, recortar um *bounding box* ao redor do polígono da quadra (com margem superior para o arco da bola) antes de passar ao YOLO. Isso aumenta o tamanho relativo da bola na imagem e evita processar arquibancadas, grades ou teto.

---

## Fase 4 — Transmissão WebSocket + Renderização via Canvas no Front-end
**Complexidade:** Média | **Impacto:** Médio-Alto

1. **Substituir Polling HTTP (`setInterval(220ms)`) por WebSocket (`ws://127.0.0.1:8000/ws/training`):**
   - Atualmente, o navegador pergunta o status a cada `220 ms`. Com WebSocket, no exato milissegundo em que o quique é detectado no Python, o servidor empurra (*push*) o evento JSON para o navegador (`< 2 ms` de latência local), disparando o bip sonoro e pintando a bolinha no mapa imediatamente.
2. **Conexão Física da Câmera (Iriun via Cabo USB + Exposição Rápida):**
   - Em treinos reais, conectar o celular ao notebook via **cabo USB com Depuração USB ativa** no Iriun Webcam elimina jitter de rede Wi-Fi (cai de ~60 ms de rede para ~5 ms via USB).
   - Em ambientes internos (menos luz), ativar o modo Esporte / alta velocidade do obturador na câmera evita o *motion blur* quando a bola atinge velocidade máxima perto do chão.

---

## Resumo do Cronograma de Implementação Recomendado

| Etapa | Ação Principal | Latência Estimada Final |
| :--- | :--- | :--- |
| **Estado Atual** | Loop síncrono + Buffer OpenCV padrão + Polling 220ms | `450 ms – 700 ms` (~10 FPS) |
| **Passo 1** | `CameraBufferCleanerThread` + `CAP_PROP_BUFFERSIZE=1` (720p) | `140 ms – 220 ms` (~18 FPS) |
| **Passo 2** | Desacoplar Thread de Vídeo (30 FPS) da Thread YOLO + WebSocket | `80 ms – 130 ms` (30 FPS vídeo) |
| **Passo 3** | Exportação ONNX / FP16 + ROI da Quadra Calibrada | `35 ms – 80 ms` (**Atende RNF03 $\le 150\text{ ms}$**) |

