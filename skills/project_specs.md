# Especificação Técnica, Arquitetura e Avaliação de Desempenho — Top Training

> **Propósito desta Skill:** Documentar de forma completa as especificações técnicas do projeto **Top Training** (focado na análise de vídeos gravados), detalhando as linguagens e bibliotecas utilizadas em cada subsistema, o fluxograma ponta a ponta (*o que faz o quê e o que calcula o quê*), a organização da arquitetura, a avaliação quantitativa de desempenho do modelo **YOLOv8** nos vídeos de teste e o roteiro técnico de melhorias.

---

## 1. Stack Tecnológica: Linguagens e Bibliotecas por Subsistema

O projeto utiliza **Python 3** em todo o *back-end* (visão computacional, inteligência artificial, geometria projetiva, motor de pontuação e servidor web) e a tríade **HTML5 + CSS3 + JavaScript Puro (ES6+)** no *front-end*.

| Subsistema / Camada | Linguagem | Biblioteca / Tecnologia | Onde é Usada | Responsabilidade Específica |
| :--- | :--- | :--- | :--- | :--- |
| **1. Modelo de Detecção (IA)** | Python 3 | **PyTorch** + **Ultralytics YOLOv8** (`ultralytics==8.3.40`) | [`trackers/ball_tracker.py`](../trackers/ball_tracker.py), [`models/yolov8_best_2.pt`](../models/yolov8_best_2.pt) | Treinamento (via *Transfer Learning* em GPU T4 no Google Colab) e inferência em cada frame para localizar o *bounding box* `[x1, y1, x2, y2]` e a confiança `conf` da bola de tênis. |
| **2. Processamento de Vídeo e Visão Computacional** | Python 3 | **OpenCV** (`opencv-python==4.10.0.84`) | [`trackers/ball_tracker.py`](../trackers/ball_tracker.py), [`app/core/homography.py`](../app/core/homography.py), [`app/app_main.py`](../app/app_main.py) | Decodificação de vídeos (`.mp4`/`.MOV`), conversão para escala de cinza, filtro de movimento real (`cv2.absdiff`), cálculo e transformação de Homografia (`cv2.findHomography`, `cv2.perspectiveTransform`), teste de inclusão em polígono (`cv2.pointPolygonTest`), desenho de rastros/anéis e codificação MJPEG. |
| **3. Cálculos Matemáticos, Álgebra Linear e Cinemática** | Python 3 | **NumPy** (`numpy>=1.26.4`) + **Pandas** (`pandas>=2.0.0`) | [`trackers/ball_tracker.py`](../trackers/ball_tracker.py), [`app/core/homography.py`](../app/core/homography.py), [`app/core/game_engine.py`](../app/core/game_engine.py) | **NumPy:** operações matriciais $3 \times 3$, distâncias euclidianas (`np.hypot`, `np.linalg.norm`) e erro de reprojeção.<br>**Pandas:** séries temporais (`DataFrame.interpolate`) para preencher oclusões da bola e cálculo de variações $\Delta x, \Delta y$ para detectar quiques e filtrar rebatidas de raquete. |
| **4. Servidor Web, API REST e Streaming** | Python 3 | **FastAPI** (`>=0.115.0`) + **Uvicorn** (`>=0.30.0`) + **Pydantic** | [`app/app_main.py`](../app/app_main.py) | Servidor HTTP assíncrono (`127.0.0.1:8000`), validação de dados via `BaseModel`, execução da análise de vídeo em *background thread* e transmissão contínua do vídeo anotado via `StreamingResponse` (`multipart/x-mixed-replace`). |
| **5. Persistência e Cache** | Python 3 | **`json`** + **`pickle`** (Standard Library) | [`app/core/storage.py`](../app/core/storage.py), [`stubs/`](../stubs/), [`app/data/`](../app/data/) | **`json`:** salva perfis, histórico de sessões, ranking ([`profiles.json`](../app/data/profiles.json)) e matrizes de calibração por fonte ([`homografia.json`](../app/data/homografia.json)).<br>**`pickle`:** serializa as detecções brutas por vídeo em `stubs/*.pkl` para reanálise instantânea. |
| **6. Interface Gráfica (Front-End SPA)** | HTML5, CSS3, JavaScript (ES6+) | **Vanilla JS**, **HTML5 Canvas 2D API**, **Web Audio API** | [`app/static/index.html`](../app/static/index.html), [`app/static/style.css`](../app/static/style.css), [`app/static/app.js`](../app/static/app.js) | **HTML/CSS:** Interface *Stealth Dark Minimal* em tela cheia (`100vh` sem scroll).<br>**Canvas 2D:** marcação/arraste dos 4 pontos da quadra e desenho da meia-quadra vetorial 2D com mapa de calor.<br>**Web Audio API:** síntese de bipes sonoros de acerto/erro direto no navegador. |

---

## 2. Fluxograma Completo do Projeto (O Que Faz o Quê e O Que Calcula o Quê)

### 2.1. Diagrama de Fluxo de Dados e Processamento (Mermaid)

```mermaid
flowchart TD
    subgraph FRONT["Camada 1: Interface Web (HTML5 / CSS3 / JS Canvas 2D)"]
        UI_PROF["1. Tela de Perfil & Hub<br/>(app.js -> /api/profile)"]
        UI_CAL["2. Tela de Calibração<br/>Arraste dos 4 Cantos (u, v) px<br/>(Canvas 2D -> /api/calibrate)"]
        UI_PREP["3. Tela de Preparação<br/>Escolha de Vídeo + Nível (2, 3, 6 zonas)<br/>+ Clique na Zona-Foco na Quadra 2D"]
        UI_PLAY["4. Tela de Vídeo & Mapa 2D<br/>Player MJPEG (78%) + Barra Seek<br/>+ Mini-Quadra de Calor (22%)"]
        UI_POP["5. Popup 'Vídeo Analisado'<br/>KPIs + Lista de Quiques c/ Salto Rápido"]
    end

    subgraph API["Camada 2: Servidor FastAPI (app/app_main.py)"]
        EP_SNAP["GET /api/frame_snapshot<br/>Extrai frame JPEG da fonte escolhida"]
        EP_CAL["POST /api/calibrate<br/>Salva calibração por fonte"]
        EP_START["POST /api/training/start<br/>Inicia Thread _run_video_session()"]
        EP_STREAM["GET /api/training/video_feed<br/>Stream MJPEG anotado (960x540)"]
    end

    subgraph CV["Camada 3: Visão Computacional & Cinemática (trackers/ball_tracker.py)"]
        CACHE{"Existe cache .pkl<br/>em stubs/?"}
        YOLO["1. Inferência YOLOv8 (yolov8_best_2.pt)<br/>Predição conf >= 0.15 em imgsz=640"]
        ABSDIFF["2. Filtro de Movimento + Continuidade<br/>cv2.absdiff >= 5.5 (ignora bolas paradas)<br/>+ Bônus de proximidade espacial"]
        SPIKE["3. Filtro Anti-Ruído (_remove_isolated_spikes)<br/>Remove detecções isoladas > 220 px/frame"]
        INTERP["4. Interpolação Temporal (Pandas)<br/>df.interpolate(linear, max_gap=12 frames)"]
        BOUNCE["5. Detecção de Quiques & Filtro Anti-Rebatida<br/>Inversão/Freada em Y + Restituição Física (e < 1)<br/>Descarta golpes de raquete (rise_4 > 1.32 * drop_4)"]
    end

    subgraph CORE["Camada 4: Geometria Projetiva & Regras (app/core/)"]
        HOMOG["HomographyManager (homography.py)<br/>1. cv2.findHomography -> Matriz H (3x3)<br/>2. cv2.pointPolygonTest (bloqueia fora da zona)<br/>3. cv2.perspectiveTransform: (u,v) px -> (x_m, y_m) m"]
        ENGINE["GameEngine (game_engine.py)<br/>1. Filtro de 1º Quique (cooldown 0.95s)<br/>2. Mapeia (x_m, y_m) na Zona (Básico/Médio/Avançado)<br/>3. Pontuação (+10 Acerto / -5 Erro) + Estatísticas por Zona"]
        STORE["StorageManager (storage.py)<br/>Persiste em app/data/profiles.json<br/>e app/data/homografia.json"]
    end

    UI_PROF --> UI_CAL
    UI_CAL -->|Seleciona Vídeo| EP_SNAP
    UI_CAL -->|Envia 4 pontos px| EP_CAL
    EP_CAL --> HOMOG
    HOMOG --> STORE

    UI_PROF --> UI_PREP
    UI_PREP -->|Inicia Análise| EP_START
    EP_START --> CACHE
    CACHE -->|Não| YOLO
    YOLO --> ABSDIFF --> SPIKE --> INTERP
    CACHE -->|Sim (Carrega .pkl)| INTERP
    INTERP --> BOUNCE
    BOUNCE -->|Lista de Quiques (frame, u, v)| ENGINE
    HOMOG -->|Converte (u,v) -> (x_m, y_m) e valida polígono| ENGINE
    ENGINE -->|Score, Eventos, ZoneStats| STORE
    ENGINE -->|Dispara analysis_done = True| UI_POP
    EP_STREAM -->| Vídeo c/ Rastro + Círculos nos Quiques | UI_PLAY
    UI_POP -->|Clique em 'Ver ->'| UI_PLAY
```

---

### 2.2. Matriz Detalhada: "Quem Calcula o Quê" (Equações e Regras Internas)

#### A. `trackers/ball_tracker.py` — Detecção, Rastreamento e Cinemática do Quique
1. **Detecção Bruta (`YOLO.predict`):**
   - Recebe o frame BGR do OpenCV e executa a rede neural convolucional [`models/yolov8_best_2.pt`](../models/yolov8_best_2.pt) com `conf=0.15` e `imgsz=640`, gerando caixas candidatas $[x_1, y_1, x_2, y_2]$ e centroide $(c_x, c_y) = \left(\frac{x_1+x_2}{2}, \frac{y_1+y_2}{2}\right)$.
2. **Filtro de Bola Parada (`cv2.absdiff`):**
   - Recorta a região da bola no frame atual ($I_t$) e no frame anterior ($I_{t-1}$) em escala de cinza e calcula a diferença média de intensidade:
     $$\Delta I = \frac{1}{W \cdot H}\sum |I_t(x,y) - I_{t-1}(x,y)|$$
   - Se $\Delta I < 5{,}5$, a detecção é **descartada** (elimina bolas paradas no chão, marcas na quadra ou logos estáticos).
3. **Score de Continuidade Espacial:**
   - Calcula a distância euclidiana até a última posição conhecida da bola há $\Delta f$ frames: $d = \sqrt{(c_x - x_{\text{ant}})^2 + (c_y - y_{\text{ant}})^2}$.
   - Se $d \le 160 \cdot \Delta f$, soma um bônus de até $+0{,}25$ na confiança da caixa para manter o foco na bola em jogo.
4. **Remoção de Picos Isolados (`_remove_isolated_spikes`):**
   - Verifica uma janela de $\pm 3$ frames vizinhos. Se uma detecção está a uma velocidade aparente $> 220\text{ px/frame}$ de todos os vizinhos, é removida como falso positivo isolado.
5. **Interpolação de Oclusões (`interpolate_ball_positions`):**
   - Converte a lista de coordenadas em um `pandas.DataFrame` com colunas `['x1', 'y1', 'x2', 'y2']` e aplica interpolação linear apenas em lacunas internas de até `12 frames` (`0,4s` a 30 FPS), reconstruindo a trajetória quando a bola passa atrás do jogador ou sofre *motion blur*.
6. **Detecção do Quique e Filtro Anti-Rebatida (`detect_bounces`):**
   - Analisa a série temporal $(x_i, y_i)$ numa janela deslizante $[i-3, i+3]$:
     - **Quique Clássico:** $y_i$ é máximo local na janela, com queda prévia $\Delta y_{\text{queda}} = y_i - y_{i-3} \ge 6\text{ px}$ e subida posterior $\Delta y_{\text{subida}} = y_i - \min(y_{i+1..i+3}) \ge 5\text{ px}$.
     - **Quique em Perspectiva:** Quando a bola vem rápido na direção da câmera ($\Delta y_{\text{queda}} \ge 28\text{ px}$ em 3 frames) e freia bruscamente ao tocar o solo ($\Delta y_{\text{subida}} \ge 0{,}5\text{ px}$ e derivada $\le 0$).
     - **Filtro Físico Anti-Rebatida (Restituição $e < 1$):** Descarta o candidato se a subida nos 4 frames seguintes for energeticamente incompatível com um quique passivo no chão ($\Delta y_{\text{subida,4}} > 95\text{ px}$ e $\Delta y_{\text{subida,4}} > 1{,}32 \cdot \Delta y_{\text{queda,4}}$) ou se houver inversão brusca do sentido horizontal $\Delta x_{\text{antes}} \cdot \Delta x_{\text{depois}} < 0$ combinada com disparo para o outro lado da quadra.

---

#### B. `app/core/homography.py` — Geometria Projetiva e Transformação Pixel $\rightarrow$ Metros
1. **Cálculo da Matriz de Homografia $H$ (`calibrate`):**
   - Relaciona os 4 cantos clicados pelo usuário na imagem $\mathbf{p}_i = (u_i, v_i)$ com as dimensões oficiais da meia-quadra de simples da ITF ($W = 8{,}23\text{ m}$ de largura $\times$ $L = 11{,}885\text{ m}$ de profundidade):
     $$\begin{bmatrix} s \cdot x_m \\ s \cdot y_m \\ s \end{bmatrix} = H_{3\times 3} \begin{bmatrix} u \\ v \\ 1 \end{bmatrix}$$
   - Calcula também a matriz inversa $H^{-1}$ e o **erro médio de reprojeção** em pixels:
     $$E_{\text{reproj}} = \frac{1}{4}\sum_{i=1}^{4} \left\| \mathbf{p}_i - \pi\left(H^{-1}\mathbf{P}_i\right) \right\|_2$$
2. **Validação de Polígono e Conversão (`pixel_to_meters`):**
   - Executa primeiro `cv2.pointPolygonTest(poly_px, (u, v), True)`. Se o ponto estiver a mais de $5\text{ px}$ fora do quadrilátero calibrado, retorna imediatamente `inside = False` (impedindo que quiques do outro lado da rede sejam contabilizados).
   - Caso esteja dentro do polígono, aplica `cv2.perspectiveTransform` com $H$ para obter $(x_m, y_m)$ em metros e verifica $0 \le x_m \le 8{,}23\text{ m}$ e $0 \le y_m \le 11{,}885\text{ m}$.

---

#### C. `app/core/game_engine.py` — Divisão de Zonas, Filtro de 1º Quique e Gamificação
1. **Geometria das Zonas (`get_zones`):**
   - **Básico (2 zonas):** Divide $W = 8{,}23\text{ m}$ ao meio ($[0;\ 4{,}115\text{ m}]$ Esquerda e $[4{,}115;\ 8{,}23\text{ m}]$ Direita).
   - **Médio (3 zonas):** Três colunas de $2{,}743\text{ m}$ de largura cada (Esquerda, Centro, Direita).
   - **Avançado (6 zonas — Matriz $3\times 2$):** Combina as 3 colunas com a linha de saque ($S = 5{,}485\text{ m}$ a partir da linha de fundo), separando bolas **Fundas** ($y \in [0;\ 5{,}485\text{ m}]$) e **Curtas / Saque** ($y \in [5{,}485;\ 11{,}885\text{ m}]$).
2. **Regras de Avaliação (`evaluate_bounces`):**
   - **Filtro de 1º Quique:** Aplica *cooldown* de `0,95s` após um quique válido para ignorar o 2º/3º quique da mesma bola.
   - **Pontuação:**
     - Quique na `target_zone`: **`+10 pontos`** (`hits += 1`)
     - Quique em outra zona dentro da área calibrada: **`-5 pontos`** (limitado ao mínimo `0`, `misses += 1`)
   - Calcula a precisão $\text{Accuracy} = \frac{\text{hits}}{\text{hits} + \text{misses}} \times 100\%$ e agrega o mapa de calor por zona (`zone_stats`).

---

## 3. Organização da Arquitetura de Pastas

```text
Top_training/
├── app/                            # Aplicação Web Completa (SPA + FastAPI)
│   ├── app_main.py                 # Orquestrador FastAPI, rotas REST, thread de vídeo e stream MJPEG
│   ├── core/
│   │   ├── homography.py           # Matriz H (3x3), pointPolygonTest e conversão pixel <-> metros
│   │   ├── game_engine.py          # Zonas (2, 3, 6), filtro de 1º quique, placar e mapa de calor
│   │   └── storage.py              # Leitura/escrita de profiles.json e homografia.json (por fonte)
│   ├── data/
│   │   ├── homografia.json         # Pontos calibrados globais e dicionário "by_source"
│   │   └── profiles.json           # Histórico de sessões por jogador e ranking por nível
│   └── static/
│       ├── index.html              # 6 views de foco único + Modal "Vídeo Analisado"
│       ├── style.css               # Design System Stealth Dark Minimal (100vh zero-scroll)
│       └── app.js                  # Estado, Canvas 2D (Calibração e Quadra 2D), Seek e WebAudio
│
├── trackers/
│   └── ball_tracker.py             # Classe BallTracker (YOLOv8, absdiff, interpolação Pandas, detect_bounces)
│
├── models/
│   ├── yolov8_best_2.pt            # Modelo principal em produção (mAP50 = 86.1%)
│   ├── yolov8_best.pt              # 1ª geração treinada
│   └── yolov8_best_3.pt            # 3ª geração experimental
│
├── src/input_videos/               # Vídeos gravados (.mp4 e .MOV) para análise
├── stubs/                          # Cache binário (.pkl) das detecções de cada vídeo
└── main.py                         # Script CLI independente para exportação em runs/Ball_Tracker/
```

---

## 4. Avaliação de Desempenho da Análise de Vídeos Gravados

### 4.1. Evolução e Métricas do Modelo YOLOv8 (`yolov8_best_2.pt`)
O modelo base original (`yolov8n.pt` pré-treinado no dataset genérico COCO) apresentava taxa de detecção de apenas **~1,4%** em vídeos de tênis devido ao tamanho diminuto da bola e ao *motion blur*. Após anotação no Roboflow e treinamento via *Transfer Learning* em GPU NVIDIA Tesla T4 no Google Colab, o modelo de produção atual (**`models/yolov8_best_2.pt`**) atingiu:

| Métrica de Validação | Valor Alcançado (`yolov8_best_2.pt`) | Interpretação Prática |
| :--- | :---: | :--- |
| **Precision (Precisão)** | **91,5%** | Baixíssima taxa de falsos positivos (raramente confunde linhas ou pés com a bola). |
| **Recall (Revocação)** | **81,8%** | Detecta diretamente mais de 4 em cada 5 frames onde a bola está visível. |
| **mAP@50** | **86,1%** | Excelente localização espacial do centro da bola. |
| **mAP@50-95** | **62,4%** | Alta aderência da caixa delimitadora ao contorno da bola. |

### 4.2. Desempenho Empírico nos 5 Vídeos Gravados do Projeto (`stubs/`)
A tabela abaixo apresenta os números reais medidos nos vídeos do repositório combinando a detecção bruta do `yolov8_best_2.pt` com a etapa de interpolação temporal do Pandas (`max_gap=12`):

| Vídeo Gravado | Resolução / FPS | Total de Frames | Detecção Bruta YOLOv8 | Cobertura Pós-Interpolação | Quiques Detectados | Perfil do Vídeo |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **`treino_3.mp4`** | `1920x1080` @ 30 FPS | 214 | 177 (`82,7%`) | **214 (`100,0%`)** | 3 (2 na zona calibrada) | Rally de transmissão oficial (câmera alta estável). |
| **`treino_1.mp4`** | `1280x720` @ 30 FPS | 316 | 254 (`80,4%`) | **310 (`98,1%`)** | 5 | Treino controlado com lançamentos repetidos. |
| **`treino_2.mp4`** | `1280x720` @ 30 FPS | 1453 | 369 (`25,4%`) | **998 (`68,7%`)** | 5 | Vídeo longo com intervalos entre bolas e ralis rápidos. |
| **`quadra_2.MOV`** | `1920x1080` @ 30 FPS | 396 | 166 (`41,9%`) | **243 (`61,4%`)** | 7 | Câmera em quadra real; bola quicando e se afastando até a rede. |
| **`quadra_3.MOV`** | `1920x1080` @ 30 FPS | 1215 | 158 (`13,0%`) | **203 (`16,7%`)** | 2 | Longo tempo sem bola em jogo (frames `0–700`) + lançamentos curtos. |

### 4.3. Diagnóstico dos Gargalos Atuais em Vídeos Gravados
1. **Problema de Objetos Muito Pequenos (*Small Object Degradation*) no Fundo da Quadra:**
   - Quando um frame `1920x1080` é redimensionado internamente pelo YOLO para `imgsz=640`, o fator de redução é de $3\times$. Uma bola próxima à rede ou no lado oposto da quadra que media $9 \times 9\text{ px}$ no vídeo original passa a ter apenas **$3 \times 3\text{ px}$** na entrada da rede neural, perdendo contraste nos mapas de características (*feature maps* de *stride* 8/16).
2. **Desfoque de Movimento (*Motion Blur*) em Golpes Rápidos:**
   - Em vídeos gravados a `30 FPS` com velocidade de obturador comum, bolas rápidas (> $120\text{ km/h}$) aparecem como um rastro translúcido alongado em vez de uma esfera amarela definida, reduzindo a confiança do detector abaixo de `conf=0.15`.
3. **Achatamento do Vértice na Interpolação Linear:**
   - Se o YOLO perde a detecção exatamente nos 2 ou 3 frames do impacto no solo (devido ao *blur* ou passagem próxima à linha branca), o `df.interpolate(method='linear')` liga o ponto antes do quique ao ponto depois do quique em linha reta, podendo suavizar ou deslocar o pico máximo de $Y$ em alguns pixels.
4. **Tempo de Inferência em CPU na 1ª Execução:**
   - Sem GPU NVIDIA local (CUDA), a inferência do YOLOv8 em PyTorch puro na CPU leva entre **80 ms e 150 ms por frame** (~7 a 12 FPS). Assim, na primeira vez que um vídeo inédito de 300 frames é aberto, o processamento leva ~30 segundos (nas vezes seguintes é instantâneo, `< 0,2s`, graças ao arquivo `.pkl` salvo em `stubs/`).

---

## 5. Como Podemos Melhorar a Análise de Vídeos Gravados? (Plano de Evolução)

Como o foco está em **vídeos gravados** (onde não há a restrição rígida de < 33 ms por frame do modo ao vivo), podemos aplicar técnicas muito mais precisas tanto na **visão computacional** quanto na **física da trajetória**:

### 5.1. Melhorias de Precisão na Detecção da Bola (Sem precisar re-treinar o modelo)
1. **Recorte Inteligente da Quadra (ROI Cropping) + Inferência em `imgsz=960` ou `1280`:**
   - **Como funciona:** Como já temos os 4 pontos da quadra calibrada, podemos recortar uma caixa delimitadora ao redor da quadra (descartando arquibancadas e placares laterais) e passar para o YOLO com `imgsz=960` ou `1280`.
   - **Ganho:** A bola no fundo da quadra passa a ter o **dobro de pixels** na entrada da rede neural, aumentando drasticamente a detecção de bolas distantes sem alterar os pesos do `yolov8_best_2.pt`.
2. **Inferência com *SAHI (Slicing Aided Hyper Inference)* ou Janela Guiada pela Última Posição:**
   - **Como funciona:** Quando a bola já está sendo rastreada em $(c_x, c_y)$, podemos extrair um *patch* de $640 \times 640\text{ px}$ em resolução nativa `1080p` centrado na posição prevista da bola.
   - **Ganho:** Resolução nativa 1:1 (zero perda por *downscaling*), capaz de detectar bolas de apenas $5 \times 5\text{ px}$ no fundo da quadra.

### 5.2. Melhorias na Detecção de Quiques vs. Rebatidas (Pós-Processamento Cinemático)
1. **Substituir Interpolação Linear por Ajuste Parabólico Gravitacional (Spline / Polinômio de 2º Grau):**
   - **Como funciona:** Entre dois quiques/rebatidas, a bola em voo livre obedece à parábola da gravidade $y(t) = a t^2 + b t + c$ e $x(t) = v_x t + x_0$. Ajustar arcos parabólicos por mínimos quadrados (`np.polyfit` de grau 2) nos trechos de descida e subida encontra a **interseção exata das duas parábolas**, determinando o ponto do quique mesmo que o frame exato do impacto no chão tenha falhado!
2. **Análise de Velocidade no Plano Métrico da Quadra $(v_{xm}, v_{ym})$:**
   - **Como funciona:** Projetar toda a trajetória para metros via Homografia $H$ e calcular a desaceleração no referencial da quadra, combinado com o filtro de restituição vertical.

### 5.3. Melhorias de Velocidade no Processamento do Vídeo Gravado
1. **Processamento em Lote (*Batch Inference*):**
   - **Como funciona:** Em vez de chamar `model.predict(frame)` frame a frame dentro do loop `while`, ler blocos de `8` ou `16` frames e chamar `model.predict(batch_frames, batch=8)`.
   - **Ganho:** Reduz o *overhead* de chamadas do PyTorch e acelera o processamento do vídeo completo em **30% a 45%** na CPU (e até **4x** em GPU).
2. **Exportação do Modelo para ONNX Runtime ou OpenVINO (`yolov8_best_2.onnx`):**
   - **Como funciona:** Exportar o `.pt` com `model.export(format="onnx")` ou `format="openvino"`.
   - **Ganho:** Reduz o tempo de análise de um vídeo inédito em processadores Intel/AMD em **2x a 3x** mantendo exatamente a mesma precisão matemática.
