# 🎾 Top Training — Sistema de Visão Computacional e Treinamento Gamificado de Tênis

O **Top Training** é uma plataforma de análise de treinos de tênis baseada em Visão Computacional (**YOLOv8 + OpenCV**) e Geometria Projetiva (**Homografia Planar 2D**). O sistema rastreia a trajetória da bola, identifica automaticamente os quiques no piso da quadra e avalia a precisão dos golpes do atleta em relação a zonas-alvo.

---

## 📌 Visão Geral: Os 2 Subprojetos do Repositório

Este repositório foi estruturado contendo **duas frentes de execução complementares** que compartilham o mesmo motor de detecção (`trackers/` e `models/`):

1. **🖥️ Subprojeto 1 — Aplicativo Interativo Gamificado (`app/`)**
   - Aplicação completa com interface gráfica moderna (Backend em **Python/FastAPI** + Frontend em **JavaScript Vanilla / HTML5 Canvas**).
   - Permite cadastrar perfis de jogadores, calibrar os **4 cantos da meia quadra oposta** (conversão de pixels para metros via Matriz de Homografia $H$), escolher níveis de dificuldade (**Básico**: 2 zonas, **Médio**: 3 zonas, **Avançado**: 6 zonas $3\times 2$) e selecionar a **Zona-Foco**.
   - Opera em dois modos:
     - **Análise Completa de Vídeo Gravado:** Processa o vídeo como um todo, exibe uma popup **"Vídeo Analisado"** com o detalhamento dos pontos, reproduz o vídeo em destaque na tela com os quiques marcados (e atalhos clicáveis para cada quique) e mostra uma **mini-quadra no canto** com o mapa de onde ocorreram mais acertos e erros.
     - **Câmera Ao Vivo (Iriun Webcam):** Conecta-se à câmera do smartphone via USB ou Wi-Fi para feedback em tempo real.
   - Mantém persistência automática de sessões e **Ranking Geral de Jogadores** em JSON.

2. **🎬 Subprojeto 2 — Pipeline Offline de Rastreamento e Exportação (`main.py`)**
   - Script direto em linha de comando focado em validação de visão computacional e geração de vídeos anotados.
   - Carrega um vídeo de `src/input_videos/`, executa o modelo customizado `yolov8_best_2.pt` com filtro de bolas estáticas (`cv2.absdiff`), interpola oclusões curtas, detecta o frame exato de cada quique pela inversão da trajetória vertical ($Y$) e salva automaticamente o vídeo renderizado em sequência (`runs/Ball_Tracker/out_video_1.mp4`, `out_video_2.mp4`, etc.).

---

## 📂 Estrutura do Projeto

```text
Top_training/
├── app/                          # Subprojeto 1: Aplicativo Web/Desktop Gamificado
│   ├── app_main.py               # Servidor FastAPI, rotas REST, streaming e controle de sessão
│   ├── core/
│   │   ├── homography.py         # Calibração de 4 pontos, matriz H e conversão pixel <-> metros
│   │   ├── game_engine.py        # Regras de zonas (2, 3 e 6 zonas), pontuação (+10/-5) e estatísticas
│   │   └── storage.py            # Persistência em JSON (perfis, histórico de treinos e ranking)
│   ├── data/                     # Dados salvos automaticamente (homografia.json, profiles.json)
│   └── static/                   # Interface Front-end (index.html, style.css, app.js)
│
├── trackers/                     # Motor de Visão Computacional compartilhado
│   ├── ball_tracker.py           # Detecção YOLOv8, filtro de movimento, interpolação e quiques
│   └── __init__.py
│
├── models/                       # Pesos treinados do modelo YOLO (.pt)
│   ├── yolov8_best_2.pt          # Modelo principal ajustado para detecção de bola de tênis
│   └── yolov8_best.pt
│
├── src/
│   └── input_videos/             # Vídeos de entrada (.MOV, .mp4) para testes e análises
│
├── stubs/                        # Cache (.pkl) das detecções YOLO para análise instantânea de vídeos
├── runs/
│   └── Ball_Tracker/             # Vídeos exportados pelo main.py (out_video_1.mp4, out_video_2.mp4...)
├── docs/                         # Documentação acadêmica, arquitetura, relatórios e planos de ação
│
├── main.py                       # Subprojeto 2: Script CLI para processar e exportar vídeos anotados
├── yolo_inference.py             # Script rápido de teste de inferência YOLO
└── requirements.txt              # Dependências Python do projeto
```

---

## ⚙️ Passo a Passo de Configuração no PC (Windows e Linux)

### 1. Pré-requisitos
- **Python 3.10 ou superior** instalado.
- **Git** (opcional, para clonar o repositório).
- *(Opcional para modo ao vivo)* Aplicativo **Iriun Webcam** instalado no computador e no celular (conectado via cabo USB ou na mesma rede Wi-Fi).

---

### 2. Configurando no Windows (PowerShell ou CMD)

Abra o terminal na pasta raiz `Top_training` e execute:

```powershell
# 1. Criar o ambiente virtual (.venv)
python -m venv .venv

# 2. Ativar o ambiente virtual (PowerShell)
.\.venv\Scripts\Activate.ps1
# (Caso use o CMD tradicional, execute: .\.venv\Scripts\activate.bat)

# 3. Atualizar o pip e instalar as dependências
python -m pip install --upgrade pip
pip install -r requirements.txt
```

> **Dica (Windows PowerShell):** Caso apareça um aviso de permissão de execução de scripts ao ativar o `.venv`, rode antes:
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

---

### 3. Configurando no Linux (Ubuntu / Debian / Fedora)

Abra o terminal na pasta raiz `Top_training` e execute:

```bash
# 1. Instalar pacotes básicos do Python e bibliotecas gráficas do OpenCV (Ubuntu/Debian)
sudo apt update
sudo apt install -y python3 python3-venv python3-pip libgl1 libglib2.0-0

# 2. Criar o ambiente virtual (.venv)
python3 -m venv .venv

# 3. Ativar o ambiente virtual
source .venv/bin/activate

# 4. Atualizar o pip e instalar as dependências
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🚀 Como Rodar o Projeto

Com o ambiente virtual (`.venv`) ativado no terminal, escolha qual dos dois subprojetos deseja executar:

### Opção A: Rodar o Aplicativo Interativo Gamificado (`app/`)

**No Windows:**
```powershell
python app/app_main.py
```

**No Linux:**
```bash
python3 app/app_main.py
```

- O aplicativo iniciará o servidor local na porta `8000` e abrirá automaticamente o navegador padrão em:
  👉 **`http://127.0.0.1:8000`**
- **Fluxo de uso dentro do App:**
  1. **Perfil & Fonte:** Informe seu nome, escolha entre **Vídeo Gravado** (arquivos da pasta `src/input_videos/`) ou **Câmera Ao Vivo (Iriun)** e selecione o nível (**Básico**, **Médio** ou **Avançado**).
  2. **Calibrar Quadra:** Clique nos **4 cantos da meia quadra oposta** na imagem e salve a homografia $H$ (você também pode validar clicando em qualquer ponto para ver as coordenadas em metros).
  3. **Zona-Foco:** Clique na região da quadra vertical onde deseja mirar seus golpes e inicie o treino.
  4. **Treino & Vídeo:** Visualize o vídeo analisado em destaque com todos os quiques, a popup de resumo dos pontos e a mini-quadra lateral mostrando o mapa de acertos e erros.
  5. **Sair:** Utilize o botão vermelho **`🚪 Sair do App`** no canto superior direito para encerrar o servidor com segurança.

---

### Opção B: Rodar o Pipeline Offline de Exportação de Vídeo (`main.py`)

Para processar diretamente um vídeo de treino e gerar um arquivo `.mp4` com as caixas delimitadoras da bola e marcações visuais de cada quique:

**No Windows:**
```powershell
python main.py
```

**No Linux:**
```bash
python3 main.py
```

- O progresso e a lista detalhada de quiques (frame, instante em segundos e coordenadas $x, y$) serão exibidos no terminal.
- O vídeo final processado será salvo automaticamente na pasta:
  📁 **`runs/Ball_Tracker/out_video_N.mp4`** (com numeração sequencial automática para não sobrescrever testes anteriores).

---

## 🛠️ Tecnologias Utilizadas

- **Python 3** — Linguagem base de visão computacional e backend
- **Ultralytics YOLOv8** — Rede neural treinada (`yolov8_best_2.pt`) para detecção da bola de tênis
- **OpenCV (`cv2`) & NumPy / Pandas** — Processamento de vídeo, filtragem temporal, interpolação e cálculo de homografia (`cv2.findHomography` / `cv2.perspectiveTransform`)
- **FastAPI & Uvicorn** — Servidor backend assíncrono e streaming de vídeo
- **HTML5 Canvas, CSS3 & JavaScript (ES6+)** — Interface gráfica interativa, quadra 2D em escala real e síntese sonora (*Web Audio API*)

---

## 📄 Licença

Projeto acadêmico desenvolvido na **Universidade Federal de Santa Catarina (UFSC)** — *Projeto Integrador (2026-2)*.

---

### Opção B: Rodar o Pipeline Offline de Exportação de Vídeo (`main.py`)

Para processar diretamente um vídeo de treino e gerar um arquivo `.mp4` com as caixas delimitadoras da bola e marcações visuais de cada quique:

**No Windows:**
```powershell
python main.py
```

**No Linux:**
```bash
python3 main.py
```

- O progresso e a lista detalhada de quiques (frame, instante em segundos e coordenadas $x, y$) serão exibidos no terminal.
- O vídeo final processado será salvo automaticamente na pasta:
  📁 **`runs/Ball_Tracker/out_video_N.mp4`** (com numeração sequencial automática para não sobrescrever testes anteriores).

---

## 🛠️ Tecnologias Utilizadas

- **Python 3** — Linguagem base de visão computacional e backend
- **Ultralytics YOLOv8** — Rede neural treinada (`yolov8_best_2.pt`) para detecção da bola de tênis
- **OpenCV (`cv2`) & NumPy / Pandas** — Processamento de vídeo, filtragem temporal, interpolação e cálculo de homografia (`cv2.findHomography` / `cv2.perspectiveTransform`)
- **FastAPI & Uvicorn** — Servidor backend assíncrono e streaming de vídeo
- **HTML5 Canvas, CSS3 & JavaScript (ES6+)** — Interface gráfica interativa, quadra 2D em escala real e síntese sonora (*Web Audio API*)

---

## 📄 Licença

Projeto acadêmico desenvolvido na **Universidade Federal de Santa Catarina (UFSC)** — *Projeto Integrador (2026-2)*.

