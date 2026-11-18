import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image

# Ensure output directory exists
os.makedirs("docs", exist_ok=True)
os.makedirs("docs/Entrega_2/img", exist_ok=True)

# Set common style
plt.rcParams['font.sans-serif'] = 'Segoe UI', 'DejaVu Sans', 'Arial'
plt.rcParams['font.family'] = 'sans-serif'

def draw_rounded_box(ax, x, y, w, h, box_color, border_color, lw=1.5, radius=0.03, alpha=1.0):
    rect = patches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad={radius},rounding_size={radius*1.5}",
        linewidth=lw,
        edgecolor=border_color,
        facecolor=box_color,
        alpha=alpha,
        zorder=2
    )
    ax.add_patch(rect)
    return rect

def draw_arrow(ax, x1, y1, x2, y2, color="#38BDF8", lw=2, style="->", rad=0.0):
    connectionstyle = f"arc3,rad={rad}" if rad != 0 else "arc3"
    ax.annotate(
        "",
        xy=(x2, y2),
        xytext=(x1, y1),
        arrowprops=dict(
            arrowstyle=style,
            color=color,
            lw=lw,
            shrinkA=4,
            shrinkB=4,
            connectionstyle=connectionstyle
        ),
        zorder=5
    )

# ==============================================================================
# 1. DIAGRAMA GERAL (MACRO-ARQUITETURA: FRONT-END, API, BACK-END, DADOS)
# ==============================================================================
def create_general_architecture_diagram():
    fig, ax = plt.subplots(figsize=(16, 9), dpi=300)
    fig.patch.set_facecolor('#090D16')
    ax.set_facecolor('#090D16')
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9)
    ax.axis('off')

    # Title Banner
    ax.text(8.0, 8.45, "ARQUITETURA GERAL DO SISTEMA — TOP TRAINING", 
            ha='center', va='center', color='#FFFFFF', fontsize=18, weight='bold')
    ax.text(8.0, 8.12, "Visão Macro: Camadas de Entrada, Servidor Web (FastAPI), Núcleo de Processamento (Python) e Interface SPA (JS/HTML/CSS)", 
            ha='center', va='center', color='#94A3B8', fontsize=10.5)

    # 4 Main Vertical Columns / Layers
    # Col 1: Entrada / Vídeo
    # Col 2: Back-End / Servidor API
    # Col 3: Núcleo de IA & Geometria
    # Col 4: Front-End / Interface do Usuário

    # -------------------------------------------------------------
    # CAMADA 1: ENTRADA & FONTES DE DADOS (Left: x=0.8, w=2.8)
    # -------------------------------------------------------------
    draw_rounded_box(ax, 0.8, 1.2, 2.8, 6.3, '#101726', '#1E293B', lw=1.8)
    ax.text(2.2, 7.2, "1. ENTRADA DE DADOS", ha='center', va='center', color='#38BDF8', fontsize=11, weight='bold')
    
    # Subcard 1.1: Videos
    draw_rounded_box(ax, 1.0, 4.4, 2.4, 2.4, '#172236', '#0284C7', lw=1.2)
    ax.text(2.2, 6.4, "Vídeos Gravados", ha='center', va='center', color='#FFFFFF', fontsize=10, weight='bold')
    ax.text(2.2, 5.85, "• Arquivos .mp4 e .MOV\n• Pasta: src/input_videos/\n• Resoluções: 720p / 1080p\n• 30 FPS / Full HD", 
            ha='center', va='center', color='#94A3B8', fontsize=8.5, linespacing=1.4)
    ax.text(2.2, 4.8, "[treino_1, quadra_2...]", ha='center', va='center', color='#38BDF8', fontsize=8, weight='bold')

    # Subcard 1.2: Cache / Stubs
    draw_rounded_box(ax, 1.0, 1.6, 2.4, 2.4, '#172236', '#6366F1', lw=1.2)
    ax.text(2.2, 3.6, "Cache Binário (Stubs)", ha='center', va='center', color='#FFFFFF', fontsize=10, weight='bold')
    ax.text(2.2, 3.0, "• Serialização em Pickle (.pkl)\n• Pasta: stubs/\n• Evita reprocessar IA\n• Carregamento em < 0.2s", 
            ha='center', va='center', color='#94A3B8', fontsize=8.5, linespacing=1.4)
    ax.text(2.2, 2.0, "[detections_cache.pkl]", ha='center', va='center', color='#818CF8', fontsize=8, weight='bold')

    # -------------------------------------------------------------
    # CAMADA 2: BACK-END / SERVIDOR FASTAPI (Middle-Left: x=4.3, w=3.4)
    # -------------------------------------------------------------
    draw_rounded_box(ax, 4.3, 1.2, 3.4, 6.3, '#121C2B', '#1E3A5F', lw=1.8)
    ax.text(6.0, 7.2, "2. SERVIDOR BACK-END (FastAPI)", ha='center', va='center', color='#F59E0B', fontsize=11, weight='bold')

    # Subcard 2.1: FastAPI App & Endpoints
    draw_rounded_box(ax, 4.55, 4.6, 2.9, 2.2, '#1A293E', '#F59E0B', lw=1.2)
    ax.text(6.0, 6.45, "FastAPI + Uvicorn", ha='center', va='center', color='#FFFFFF', fontsize=10, weight='bold')
    ax.text(6.0, 5.65, "• Host: 127.0.0.1:8000\n• Rotas REST (JSON / Pydantic)\n• /api/init, /api/calibrate\n• /api/training/start, /status", 
            ha='center', va='center', color='#CBD5E1', fontsize=8.2, linespacing=1.35)

    # Subcard 2.2: Streaming Engine MJPEG
    draw_rounded_box(ax, 4.55, 3.1, 2.9, 1.3, '#1A293E', '#10B981', lw=1.2)
    ax.text(6.0, 3.95, "Motor de Streaming MJPEG", ha='center', va='center', color='#10B981', fontsize=9.5, weight='bold')
    ax.text(6.0, 3.45, "• GET /api/training/video_feed\n• StreamingResponse multipart/x-mixed", 
            ha='center', va='center', color='#94A3B8', fontsize=8, linespacing=1.3)

    # Subcard 2.3: Storage JSON
    draw_rounded_box(ax, 4.55, 1.5, 2.9, 1.35, '#1A293E', '#818CF8', lw=1.2)
    ax.text(6.0, 2.45, "Storage & Persistência JSON", ha='center', va='center', color='#A5B4FC', fontsize=9.5, weight='bold')
    ax.text(6.0, 1.9, "• app/data/profiles.json (Ranking)\n• app/data/homografia.json (4 cantos)", 
            ha='center', va='center', color='#94A3B8', fontsize=8, linespacing=1.3)

    # -------------------------------------------------------------
    # CAMADA 3: NÚCLEO DE CV & IA (Middle-Right: x=8.3, w=3.4)
    # -------------------------------------------------------------
    draw_rounded_box(ax, 8.3, 1.2, 3.4, 6.3, '#141828', '#2D224C', lw=1.8)
    ax.text(10.0, 7.2, "3. PROCESSAMENTO IA & CV", ha='center', va='center', color='#A855F7', fontsize=11, weight='bold')

    # Subcard 3.1: YOLOv8 Tracking
    draw_rounded_box(ax, 8.55, 5.0, 2.9, 1.8, '#1F1B38', '#A855F7', lw=1.2)
    ax.text(10.0, 6.45, "YOLOv8 Ball Tracker", ha='center', va='center', color='#E9D5FF', fontsize=10, weight='bold')
    ax.text(10.0, 5.7, "• yolov8_best_2.pt (mAP50=86.1%)\n• cv2.absdiff (filtro movimento real)\n• Pandas (interpolação de oclusão)", 
            ha='center', va='center', color='#CBD5E1', fontsize=8.2, linespacing=1.35)

    # Subcard 3.2: Homografia 2D
    draw_rounded_box(ax, 8.55, 3.25, 2.9, 1.55, '#1F1B38', '#38BDF8', lw=1.2)
    ax.text(10.0, 4.4, "Homografia 2D (Metros)", ha='center', va='center', color='#7DD3FC', fontsize=9.5, weight='bold')
    ax.text(10.0, 3.75, "• Matriz H 3x3 (Pixel -> Metros)\n• Dimensões ITF: 8.23m x 11.89m\n• cv2.pointPolygonTest (bloqueio fora)", 
            ha='center', va='center', color='#94A3B8', fontsize=8, linespacing=1.3)

    # Subcard 3.3: Game Engine
    draw_rounded_box(ax, 8.55, 1.5, 2.9, 1.55, '#1F1B38', '#10B981', lw=1.2)
    ax.text(10.0, 2.65, "Game Engine & Placar", ha='center', va='center', color='#6EE7B7', fontsize=9.5, weight='bold')
    ax.text(10.0, 2.0, "• Detecção de Quiques em Y\n• Filtro Anti-Rebatida de Raquete\n• +10 Acerto / -5 Erro / Mapa de Calor", 
            ha='center', va='center', color='#94A3B8', fontsize=8, linespacing=1.3)

    # -------------------------------------------------------------
    # CAMADA 4: FRONT-END / CLIENTE SPA (Right: x=12.3, w=2.9)
    # -------------------------------------------------------------
    draw_rounded_box(ax, 12.3, 1.2, 2.9, 6.3, '#0E1724', '#1E293B', lw=1.8)
    ax.text(13.75, 7.2, "4. FRONT-END (SPA WEB)", ha='center', va='center', color='#10B981', fontsize=11, weight='bold')

    # Subcard 4.1: HTML5 & CSS3
    draw_rounded_box(ax, 12.5, 5.0, 2.5, 1.8, '#132032', '#38BDF8', lw=1.2)
    ax.text(13.75, 6.45, "HTML5 + CSS3", ha='center', va='center', color='#FFFFFF', fontsize=10, weight='bold')
    ax.text(13.75, 5.7, "• Stealth Dark Minimal\n• Janela 100vh Zero-Scroll\n• Layout 2 Colunas (78% / 22%)\n• Modal 'Vídeo Analisado'", 
            ha='center', va='center', color='#94A3B8', fontsize=8.2, linespacing=1.35)

    # Subcard 4.2: JS Canvas 2D
    draw_rounded_box(ax, 12.5, 3.25, 2.5, 1.55, '#132032', '#10B981', lw=1.2)
    ax.text(13.75, 4.4, "Canvas 2D Interativo", ha='center', va='center', color='#A7F3D0', fontsize=9.5, weight='bold')
    ax.text(13.75, 3.75, "• Arraste dos 4 cantos na imagem\n• Mini-quadra 2D com heatmap\n• Pílulas clicáveis de quiques", 
            ha='center', va='center', color='#94A3B8', fontsize=8, linespacing=1.3)

    # Subcard 4.3: Áudio & Polling
    draw_rounded_box(ax, 12.5, 1.5, 2.5, 1.55, '#132032', '#F59E0B', lw=1.2)
    ax.text(13.75, 2.65, "Web Audio & Polling", ha='center', va='center', color='#FDE68A', fontsize=9.5, weight='bold')
    ax.text(13.75, 2.0, "• Web Audio API (Bipes 880/220Hz)\n• Polling a 200ms (/session/state)\n• Botão Sair (/api/shutdown)", 
            ha='center', va='center', color='#94A3B8', fontsize=8, linespacing=1.3)

    # -------------------------------------------------------------
    # ARROWS & DATAFLOWS
    # -------------------------------------------------------------
    # Col 1 -> Col 2 (Vídeo / Stubs para FastAPI)
    draw_arrow(ax, 3.4, 5.6, 4.3, 5.6, color='#38BDF8', lw=2)
    draw_arrow(ax, 3.4, 2.8, 4.3, 2.8, color='#818CF8', lw=2)

    # Col 2 <-> Col 3 (FastAPI <-> CV/IA Engine)
    draw_arrow(ax, 7.7, 5.8, 8.3, 5.8, color='#A855F7', lw=2)
    draw_arrow(ax, 8.3, 5.3, 7.7, 5.3, color='#F59E0B', lw=2)
    draw_arrow(ax, 7.7, 4.0, 8.3, 4.0, color='#38BDF8', lw=2)
    draw_arrow(ax, 8.3, 2.2, 7.7, 2.2, color='#10B981', lw=2)

    # Col 2 <-> Col 4 (FastAPI <-> Front-End)
    draw_arrow(ax, 7.7, 5.0, 12.3, 5.0, color='#10B981', lw=2, rad=0.08)
    draw_arrow(ax, 12.3, 4.7, 7.7, 4.7, color='#38BDF8', lw=2, rad=-0.08)
    draw_arrow(ax, 7.7, 3.5, 12.3, 3.5, color='#F59E0B', lw=2.2)

    # Footer note
    ax.text(8.0, 0.45, "Top Training — Engenharia de Software & Visão Computacional Aplicada ao Esporte (UFSC)", 
            ha='center', va='center', color='#64748B', fontsize=9)

    plt.tight_layout()
    plt.savefig("docs/arquitetura_geral.png", dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.savefig("docs/Entrega_2/img/arquitetura_geral.png", dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close()
    print("Salvo: docs/arquitetura_geral.png")

# ==============================================================================
# 2. DIAGRAMA APROFUNDADO (SUBSISTEMAS: PYTORCH, OPENCV, NUMPY/PANDAS, FASTAPI)
# ==============================================================================
def create_detailed_architecture_diagram():
    fig, ax = plt.subplots(figsize=(18, 10.5), dpi=300)
    fig.patch.set_facecolor('#070A12')
    ax.set_facecolor('#070A12')
    ax.set_xlim(0, 18)
    ax.set_ylim(0, 10.5)
    ax.axis('off')

    # Title Banner
    ax.text(9.0, 9.9, "ARQUITETURA DETALHADA E FLUXO TÉCNICO DE PROCESSAMENTO", 
            ha='center', va='center', color='#FFFFFF', fontsize=18, weight='bold')
    ax.text(9.0, 9.5, "Mapeamento minucioso dos componentes: PyTorch, YOLOv8, OpenCV, NumPy, Pandas, Homografia e GameEngine", 
            ha='center', va='center', color='#94A3B8', fontsize=10.5)

    # 6 Specialized Functional Modules
    # Mod 1: Decodificação & Pré-Processamento (OpenCV)
    # Mod 2: Rede Neural & Detecção (PyTorch / YOLOv8)
    # Mod 3: Rastreamento & Cinemática (NumPy / Pandas)
    # Mod 4: Geometria Projetiva (Homografia 2D)
    # Mod 5: Regras Esportivas & Pontuação (Game Engine)
    # Mod 6: API REST & Pipeline de Saída (FastAPI + Front-End)

    # -------------------------------------------------------------
    # MÓDULO 1: ENTRADA & PRÉ-PROCESSAMENTO OPENCV (x=0.6, y=5.2, w=5.2, h=3.8)
    # -------------------------------------------------------------
    draw_rounded_box(ax, 0.6, 5.2, 5.2, 3.8, '#0F172A', '#0284C7', lw=1.6)
    ax.text(3.2, 8.65, "MÓDULO 1: OPENCV (cv2) — ENTRADA & FILTRAGEM", ha='center', va='center', color='#38BDF8', fontsize=11, weight='bold')

    draw_rounded_box(ax, 0.85, 7.3, 4.7, 1.0, '#1E293B', '#38BDF8', lw=1)
    ax.text(3.2, 7.95, "cv2.VideoCapture & Decodificação", ha='center', va='center', color='#FFFFFF', fontsize=9.5, weight='bold')
    ax.text(3.2, 7.55, "Leitura frame a frame de vídeos MP4/MOV em BGR nativo (1080p / 720p @ 30 FPS)", ha='center', va='center', color='#94A3B8', fontsize=7.8)

    draw_rounded_box(ax, 0.85, 6.15, 4.7, 1.0, '#1E293B', '#10B981', lw=1)
    ax.text(3.2, 6.8, "cv2.absdiff (Filtro de Movimento Real)", ha='center', va='center', color='#A7F3D0', fontsize=9.5, weight='bold')
    ax.text(3.2, 6.4, "ΔI = mean(|I_t - I_t-1|) >= 5.5 em escala de cinza: descarta bolas paradas no solo", ha='center', va='center', color='#CBD5E1', fontsize=7.8)

    draw_rounded_box(ax, 0.85, 5.4, 4.7, 0.65, '#1E293B', '#64748B', lw=1)
    ax.text(3.2, 5.72, "Redimensionamento para imgsz=640 e geração de histórico de frames", ha='center', va='center', color='#94A3B8', fontsize=8)

    # -------------------------------------------------------------
    # MÓDULO 2: DEEP LEARNING (PYTORCH + YOLOV8) (x=6.4, y=5.2, w=5.2, h=3.8)
    # -------------------------------------------------------------
    draw_rounded_box(ax, 6.4, 5.2, 5.2, 3.8, '#16122C', '#7C3AED', lw=1.6)
    ax.text(9.0, 8.65, "MÓDULO 2: PYTORCH & ULTRALYTICS YOLOV8", ha='center', va='center', color='#C084FC', fontsize=11, weight='bold')

    draw_rounded_box(ax, 6.65, 7.3, 4.7, 1.0, '#241B45', '#A855F7', lw=1)
    ax.text(9.0, 7.95, "Modelo Customizado: yolov8_best_2.pt", ha='center', va='center', color='#FFFFFF', fontsize=9.5, weight='bold')
    ax.text(9.0, 7.55, "Transfer Learning em GPU T4 (Colab) | mAP50=86.1% | Precision=91.5% | Recall=81.8%", ha='center', va='center', color='#E9D5FF', fontsize=7.8)

    draw_rounded_box(ax, 6.65, 6.15, 4.7, 1.0, '#241B45', '#C084FC', lw=1)
    ax.text(9.0, 6.8, "Inferência Convolucional (conf >= 0.15)", ha='center', va='center', color='#F3E8FF', fontsize=9.5, weight='bold')
    ax.text(9.0, 6.4, "Extração de Bounding Boxes [x1, y1, x2, y2] e Centroide cx=(x1+x2)/2, cy=(y1+y2)/2", ha='center', va='center', color='#CBD5E1', fontsize=7.8)

    draw_rounded_box(ax, 6.65, 5.4, 4.7, 0.65, '#241B45', '#64748B', lw=1)
    ax.text(9.0, 5.72, "Score com Continuidade Espacial: bônus se d <= 160 * Δf frames da bola ativa", ha='center', va='center', color='#A78BFA', fontsize=8)

    # -------------------------------------------------------------
    # MÓDULO 3: PANDAS & NUMPY — CINEMÁTICA DO QUIQUE (x=12.2, y=5.2, w=5.2, h=3.8)
    # -------------------------------------------------------------
    draw_rounded_box(ax, 12.2, 5.2, 5.2, 3.8, '#1C1322', '#BE123C', lw=1.6)
    ax.text(14.8, 8.65, "MÓDULO 3: NUMPY & PANDAS (CINEMÁTICA)", ha='center', va='center', color='#FB7185', fontsize=11, weight='bold')

    draw_rounded_box(ax, 12.45, 7.3, 4.7, 1.0, '#2E192D', '#F43F5E', lw=1)
    ax.text(14.8, 7.95, "Interpolação de Trajetória (Pandas)", ha='center', va='center', color='#FFFFFF', fontsize=9.5, weight='bold')
    ax.text(14.8, 7.55, "df.interpolate(method='linear', limit=12): recupera até 0.4s de oclusão/blur", ha='center', va='center', color='#FECDD3', fontsize=7.8)

    draw_rounded_box(ax, 12.45, 6.15, 4.7, 1.0, '#2E192D', '#FB7185', lw=1)
    ax.text(14.8, 6.8, "Detecção de Quiques em Y (detect_bounces)", ha='center', va='center', color='#FFE4E6', fontsize=9.5, weight='bold')
    ax.text(14.8, 6.4, "Máximo local de Y: Queda prévia (Δy >= 6px) + Subida posterior (Δy >= 5px)", ha='center', va='center', color='#CBD5E1', fontsize=7.8)

    draw_rounded_box(ax, 12.45, 5.4, 4.7, 0.65, '#2E192D', '#E11D48', lw=1)
    ax.text(14.8, 5.72, "Filtro Anti-Rebatida: descarta se subida > 1.32 * queda ou inversão brusca em X", ha='center', va='center', color='#FDA4AF', fontsize=7.8, weight='bold')

    # -------------------------------------------------------------
    # MÓDULO 4: HOMOGRAFIA 2D & PROJEÇÃO (x=0.6, y=0.9, w=5.2, h=3.7)
    # -------------------------------------------------------------
    draw_rounded_box(ax, 0.6, 0.9, 5.2, 3.7, '#0B1A24', '#0284C7', lw=1.6)
    ax.text(3.2, 4.25, "MÓDULO 4: HOMOGRAFIA 2D (PIXEL -> METROS)", ha='center', va='center', color='#38BDF8', fontsize=11, weight='bold')

    draw_rounded_box(ax, 0.85, 3.0, 4.7, 0.95, '#132838', '#0284C7', lw=1)
    ax.text(3.2, 3.65, "cv2.findHomography (Matriz H 3x3)", ha='center', va='center', color='#FFFFFF', fontsize=9.5, weight='bold')
    ax.text(3.2, 3.25, "Mapeia 4 cantos da quadra da imagem para dimensões ITF: 8.23m x 11.89m", ha='center', va='center', color='#94A3B8', fontsize=7.8)

    draw_rounded_box(ax, 0.85, 1.95, 4.7, 0.95, '#132838', '#10B981', lw=1)
    ax.text(3.2, 2.6, "Validação de Limites (cv2.pointPolygonTest)", ha='center', va='center', color='#A7F3D0', fontsize=9.5, weight='bold')
    ax.text(3.2, 2.2, "Descarta qualquer impacto com dist < -5px fora dos 4 cantos (outro lado da rede)", ha='center', va='center', color='#CBD5E1', fontsize=7.8)

    draw_rounded_box(ax, 0.85, 1.1, 4.7, 0.75, '#132838', '#38BDF8', lw=1)
    ax.text(3.2, 1.58, "cv2.perspectiveTransform & Erro de Reprojeção", ha='center', va='center', color='#BAE6FD', fontsize=8.5, weight='bold')
    ax.text(3.2, 1.25, "Converte (u, v) px -> (x_m, y_m) m em tempo real (validação UC09 / RNF04)", ha='center', va='center', color='#94A3B8', fontsize=7.6)

    # -------------------------------------------------------------
    # MÓDULO 5: GAME ENGINE & PONTUAÇÃO (x=6.4, y=0.9, w=5.2, h=3.7)
    # -------------------------------------------------------------
    draw_rounded_box(ax, 6.4, 0.9, 5.2, 3.7, '#0C1C1B', '#059669', lw=1.6)
    ax.text(9.0, 4.25, "MÓDULO 5: GAME ENGINE & GAMIFICAÇÃO", ha='center', va='center', color='#34D399', fontsize=11, weight='bold')

    draw_rounded_box(ax, 6.65, 3.0, 4.7, 0.95, '#132E2C', '#10B981', lw=1)
    ax.text(9.0, 3.65, "Subdivisão Dinâmica de Zonas", ha='center', va='center', color='#FFFFFF', fontsize=9.5, weight='bold')
    ax.text(9.0, 3.25, "• Básico: 2 Zonas | Médio: 3 Colunas | Avançado: Grade 3x2 (Fundo/Saque)", ha='center', va='center', color='#D1FAE5', fontsize=7.8)

    draw_rounded_box(ax, 6.65, 1.95, 4.7, 0.95, '#132E2C', '#F59E0B', lw=1)
    ax.text(9.0, 2.6, "Filtro de 1º Quique & Pontuação", ha='center', va='center', color='#FDE68A', fontsize=9.5, weight='bold')
    ax.text(9.0, 2.2, "Cooldown 0.95s para ignorar 2º quique | +10 pts Zona-Foco | -5 pts Outra Zona", ha='center', va='center', color='#CBD5E1', fontsize=7.8)

    draw_rounded_box(ax, 6.65, 1.1, 4.7, 0.75, '#132E2C', '#34D399', lw=1)
    ax.text(9.0, 1.58, "Estatísticas Espaciais & Mapa de Calor", ha='center', va='center', color='#A7F3D0', fontsize=8.5, weight='bold')
    ax.text(9.0, 1.25, "zone_stats: contagem de Acertos/Erros por zona e cálculo de Precisão (%)", ha='center', va='center', color='#94A3B8', fontsize=7.6)

    # -------------------------------------------------------------
    # MÓDULO 6: FASTAPI SERVER & FRONT-END SPA (x=12.2, y=0.9, w=5.2, h=3.7)
    # -------------------------------------------------------------
    draw_rounded_box(ax, 12.2, 0.9, 5.2, 3.7, '#151726', '#4F46E5', lw=1.6)
    ax.text(14.8, 4.25, "MÓDULO 6: FASTAPI, STREAMING & FRONT-END", ha='center', va='center', color='#818CF8', fontsize=11, weight='bold')

    draw_rounded_box(ax, 12.45, 3.0, 4.7, 0.95, '#1E213D', '#6366F1', lw=1)
    ax.text(14.8, 3.65, "Streaming MJPEG Anotado (960x540)", ha='center', va='center', color='#FFFFFF', fontsize=9.5, weight='bold')
    ax.text(14.8, 3.25, "cv2.polylines (quadra) + Rastro dinâmico 18 frames + Anéis de impacto com ripple", ha='center', va='center', color='#C7D2FE', fontsize=7.8)

    draw_rounded_box(ax, 12.45, 1.95, 4.7, 0.95, '#1E213D', '#10B981', lw=1)
    ax.text(14.8, 2.6, "HTML5 Canvas 2D & Web Audio API", ha='center', va='center', color='#A7F3D0', fontsize=9.5, weight='bold')
    ax.text(14.8, 2.2, "Renderização vetorial da quadra 2D com mapa de calor + Bipes de 880Hz / 220Hz", ha='center', va='center', color='#CBD5E1', fontsize=7.8)

    draw_rounded_box(ax, 12.45, 1.1, 4.7, 0.75, '#1E213D', '#F59E0B', lw=1)
    ax.text(14.8, 1.58, "Timeline Interativa & Popup de Quiques", ha='center', va='center', color='#FDE68A', fontsize=8.5, weight='bold')
    ax.text(14.8, 1.25, "Barra seek clicável e chips #N para saltar no vídeo até o instante do lance", ha='center', va='center', color='#94A3B8', fontsize=7.6)

    # -------------------------------------------------------------
    # INTER-MODULE ARROWS (DETAILED FLOW)
    # -------------------------------------------------------------
    # Mod 1 -> Mod 2 (Frames pré-processados -> YOLOv8)
    draw_arrow(ax, 5.8, 7.1, 6.4, 7.1, color='#A855F7', lw=2.2)
    ax.text(6.1, 7.3, "Frames BGR", ha='center', va='bottom', color='#A855F7', fontsize=7.2, weight='bold')

    # Mod 2 -> Mod 3 (Bounding Boxes -> Trajetória Pandas)
    draw_arrow(ax, 11.6, 7.1, 12.2, 7.1, color='#FB7185', lw=2.2)
    ax.text(11.9, 7.3, "Detecções [x,y]", ha='center', va='bottom', color='#FB7185', fontsize=7.2, weight='bold')

    # Mod 3 -> Mod 4 & 5 (Quiques Detectados -> Homografia e GameEngine)
    draw_arrow(ax, 13.5, 5.2, 4.5, 4.6, color='#38BDF8', lw=2, rad=-0.15)
    draw_arrow(ax, 14.5, 5.2, 10.2, 4.6, color='#10B981', lw=2, rad=-0.12)
    ax.text(12.0, 4.75, "Quiques Brutos (frame, x, y)", ha='center', va='bottom', color='#38BDF8', fontsize=7.5, weight='bold')

    # Mod 4 -> Mod 5 (Coordenadas em Metros (xm, ym) -> GameEngine)
    draw_arrow(ax, 5.8, 2.7, 6.4, 2.7, color='#34D399', lw=2.2)
    ax.text(6.1, 2.9, "(x_m, y_m) + inside", ha='center', va='bottom', color='#34D399', fontsize=7.2, weight='bold')

    # Mod 5 -> Mod 6 (Eventos, Placar & ZoneStats -> FastAPI/Front)
    draw_arrow(ax, 11.6, 2.7, 12.2, 2.7, color='#818CF8', lw=2.2)
    ax.text(11.9, 2.9, "Score, Hits & ZoneStats", ha='center', va='bottom', color='#818CF8', fontsize=7.2, weight='bold')

    # Footer note
    ax.text(9.0, 0.35, "Engenharia de Detecção & Pipeline Cinemático — Projeto Integrador Top Training", 
            ha='center', va='center', color='#64748B', fontsize=9)

    plt.tight_layout()
    plt.savefig("docs/arquitetura_detalhada.png", dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.savefig("docs/Entrega_2/img/arquitetura_detalhada.png", dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close()
    print("Salvo: docs/arquitetura_detalhada.png")

# ==============================================================================
# 3. IMAGEM CONSOLIDADA (AMBOS OS DIAGRAMAS EM UM PAINEL DE APRESENTAÇÃO ÚNICO)
# ==============================================================================
def combine_diagrams_into_poster():
    img1 = Image.open("docs/arquitetura_geral.png")
    img2 = Image.open("docs/arquitetura_detalhada.png")

    w1, h1 = img1.size
    w2, h2 = img2.size

    target_w = max(w1, w2)
    # Scale both to target_w preserving aspect ratio
    scale1 = target_w / float(w1)
    scale2 = target_w / float(w2)

    new_h1 = int(h1 * scale1)
    new_h2 = int(h2 * scale2)

    img1_resized = img1.resize((target_w, new_h1), Image.Resampling.LANCZOS)
    img2_resized = img2.resize((target_w, new_h2), Image.Resampling.LANCZOS)

    sep_h = 30
    total_h = new_h1 + new_h2 + sep_h
    combined = Image.new("RGB", (target_w, total_h), (9, 13, 22))

    combined.paste(img1_resized, (0, 0))
    combined.paste(img2_resized, (0, new_h1 + sep_h))

    combined.save("docs/arquitetura_completa.png", quality=95)
    combined.save("docs/Entrega_2/img/arquitetura_completa.png", quality=95)
    print("Salvo: docs/arquitetura_completa.png")

if __name__ == "__main__":
    create_general_architecture_diagram()
    create_detailed_architecture_diagram()
    combine_diagrams_into_poster()
