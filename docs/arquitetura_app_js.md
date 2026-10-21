# Especificação e Arquitetura do Aplicativo — Top Training (`app/`)

> Documento gerado a partir do alinhamento de requisitos (`/grill-me` — 20 decisões de produto e engenharia) para a construção da interface em **HTML5 / CSS3 / JavaScript Puro** integrada ao motor **Python (FastAPI + YOLOv8 + OpenCV)**.

---

## 1. Resumo das 20 Decisões de Projeto

| # | Tópico | Decisão Definida |
| :-: | :--- | :--- |
| **1** | **Arquitetura JS + Python** | Front-end em HTML5/CSS3/JS Vanilla (sem build complexo) + Back-end Python em **FastAPI** na pasta `Top_training/app/`. |
| **2** | **Modo de Exibição** | Abre automaticamente no navegador padrão (`http://127.0.0.1:8000`) ao iniciar o servidor Python. |
| **3** | **Identidade Visual** | **Tema Escuro Esportivo (Dark Mode)** inspirado no SwingVision: fundo escuro (`#0B1622`), azul-quadra (`#1F4E79` / `#2C5F8A`), verde neon (`#00E676`) para acertos e vermelho (`#FF3B30`) para erros. |
| **4** | **Fonte de Vídeo** | Seletor na própria tela entre **Câmera Ao Vivo (Iriun Webcam / UVC)** e **Vídeo Gravado** (listando automaticamente os vídeos de `src/input_videos/`). |
| **5** | **Calibração da Quadra** | Congela um frame da câmera/vídeo no `<canvas>`, permite clicar nos **4 cantos da meia quadra** e **arrastar qualquer ponto com o mouse** para ajuste fino em tempo real. |
| **6** | **Medidas e Persistência** | Inicia com calibração manual de 4 pontos nas medidas oficiais de simples ($8,23 \times 11,885\text{ m}$), salvando em `app/data/homografia.json`. *(Evolução futura: usar YOLO para detectar cantos da quadra automaticamente).* |
| **7** | **Nível Médio (3 Zonas)** | Dividido em **3 colunas verticais**: Esquerda (Cruzada), Centro (Meio) e Direita (Paralela). |
| **8** | **Nível Avançado (6 Zonas)** | Dividido em **Grade $3 \times 2$ (6 zonas)**: 3 colunas (Esquerda / Centro / Direita) $\times$ 2 profundidades (Curta na área de saque / Funda até a linha de base). |
| **9** | **Seleção de Zona-Foco** | Escolha de **1 zona-foco por sessão** clicando diretamente no Mapa 2D vertical com realce ao passar o mouse (*hover*) e restante da quadra translúcido. |
| **10** | **Regra de Pontuação** | Apenas quiques **dentro da meia quadra mapeada** são contabilizados: na zona-foco = **Acerto (`+10 pts`)**; em outra zona da quadra = **Erro (`-5 pts`, mín. `0`)**; fora da quadra = **ignorado**. |
| **11** | **Tela de Treino** | Exibe Menu à esquerda, Mapa 2D ao centro, Placar à direita + miniatura do vídeo ao vivo; ao encerrar, abre o **Relatório Final de Acertos e Erros**. |
| **12** | **Filtro de 1º vs 2º Quique** | Contabiliza **apenas o 1º quique de cada bola lançada**, aplicando janela de bloqueio (~1,8s / ~50 frames) para ignorar o 2º e 3º quiques menores da mesma bola. |
| **13** | **Encerramento do Treino** | Botão manual **"Encerrar e Salvar Treino"** (e encerramento automático ao terminar um vídeo gravado). |
| **14** | **Tela de Feedback Final** | Cards com Pontuação Total, Acertos, Erros e % de Precisão + Mapa 2D final com todos os quiques da sessão (verdes e vermelhos) + botões "Novo Treino" e "Ver Ranking". |
| **15** | **Feedback Instantâneo** | Pulso visual verde/vermelho no Mapa 2D + efeito sonoro sintetizado via *Web Audio API* (bipe agudo para acerto e grave para erro, com botão de *Mute*). |
| **16** | **Perfis e Ranking** | Sessões salvas em JSON por jogador; Ranking separado por abas de nível (`Básico`, `Médio`, `Avançado`) exibindo a melhor marca de cada perfil ordenada por Pontuação (e % de Precisão como desempate). |
| **17** | **Conexão Iriun Webcam** | Lista os índices de câmera (`0`, `1`, `2`) com *preview* de imagem na interface para identificar facilmente o Iriun Webcam antes de iniciar. |
| **18** | **Ideia do Smartwatch** | Documentada na seção de **Trabalhos Futuros** (vibração no relógio smart ao acertar a zona-foco). |
| **19** | **Validação da Homografia (UC09)** | Painel na tela de Calibração que exibe o erro de reprojeção e permite clicar em qualquer ponto da imagem para conferir a coordenada convertida em metros $(x, y)$. |
| **20** | **Estrutura em `Top_training/app/`** | Código da aplicação isolado em `Top_training/app/`, preservando `main.py` e `trackers/ball_tracker.py` na raiz para testes diretos de visão computacional. |

---

## 2. Estrutura de Pastas de `Top_training/app/`

```text
Top_training/
├── main.py                        # Script CLI isolado para testes de vídeo do YOLO
├── trackers/
│   └── ball_tracker.py            # Motor de detecção YOLO + filtro de movimento + quiques
└── app/                           # Aplicação Web/Desktop (FastAPI + HTML/CSS/JS)
    ├── __init__.py
    ├── app_main.py                # Servidor FastAPI + WebSocket/SSE + abertura automática do navegador
    ├── core/
    │   ├── __init__.py
    │   ├── homography.py          # Cálculo da matriz H (pixel <-> metros), validação e zonas da quadra
    │   ├── game_engine.py         # Regras de níveis (2, 3, 6 zonas), pontuação (+10/-5) e filtro de 1º quique
    │   └── storage.py             # Persistência JSON de perfis, sessões, ranking e homografia
    ├── data/
    │   ├── homografia.json        # Última calibração de 4 pontos salva
    │   └── profiles.json          # Perfis de jogadores e histórico de sessões
    └── static/
        ├── index.html             # Interface SPA (Single Page Application) com todas as telas
        ├── style.css              # Tema Escuro Esportivo (SwingVision style)
        └── app.js                 # Lógica de Canvas 2D, calibração arrastável, som WebAudio e tempo real
```

---

## 3. Trabalhos Futuros Registrados (Roadmap Pós-Entrega)

1. **Integração com Smartwatch (Feedback Háptico no Pulso):**
   - Enviar notificação via Bluetooth Low Energy (Web Bluetooth API) ou WebSocket local para um *companion app* em Smartwatch (Wear OS / Apple Watch / Garmin) que **vibra no pulso do jogador** no exato instante em que a bola quica dentro da **zona-foco**, permitindo que o atleta saiba que acertou sem precisar olhar para a tela do computador.
2. **Calibração Automática da Quadra via YOLO-Pose / Keypoints:**
   - Treinar um modelo detector de interseções das linhas da quadra de tênis (4 cantos da meia quadra + linha de saque) para preencher os 4 pontos da homografia automaticamente sem intervenção manual.

