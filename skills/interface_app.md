# Especificação e Guia da Interface Gráfica (UI/UX) — Top Training App

> **Propósito deste arquivo:** Documentar detalhadamente a arquitetura visual, o fluxo de navegação, os componentes de cada tela, os elementos de Canvas 2D, os modais e a comunicação com o back-end da interface web do **Top Training** (`app/static/`).

---

## 1. Arquitetura Geral da Interface e Identidade Visual

A interface do **Top Training** é uma **Single Page Application (SPA)** construída em **HTML5, CSS3 e JavaScript puro (Vanilla JS)** servida pelo back-end **FastAPI** (`http://127.0.0.1:8000`).

### 1.1. Arquivos da Interface
- **[`app/static/index.html`](../app/static/index.html):** Estrutura semântica da barra superior fixa, das **5 telas (`views`)** e do **Modal Popup `"Vídeo Analisado!"`**.
- **[`app/static/style.css`](../app/static/style.css):** Sistema de design em **Tema Escuro Esportivo** (*Dark Mode* inspirado no *SwingVision*), variáveis CSS, grids responsivos e trava de tela cheia (`100vh` sem barra de rolagem global).
- **[`app/static/app.js`](../app/static/app.js):** Gerenciamento de estado (`state`), renderização vetorial em HTML5 Canvas 2D (calibração, seleção de zona, mapa de calor da quadra), sintetizador de áudio via **Web Audio API**, *polling* de estado a `250 ms` (`/api/session/state`) e controle de vídeo/timeline.

### 1.2. Regra de Viewport (`100vh` Zero-Scroll Global)
A aplicação opera como um **software desktop em janela cheia**, sem rolagem vertical ou horizontal na página principal:
- `html, body { width: 100vw; height: 100vh; overflow: hidden; display: flex; flex-direction: column; }`
- **Barra Superior (`.topbar`):** Altura fixa de `54px`.
- **Container Principal (`.container`):** Altura exata de `calc(100vh - 54px)`, ocupando `100%` da largura até `1600px`.
- Listas extensas (como o log de bolas ou a lista de quiques no modal) possuem rolagem interna isolada (`overflow-y: auto`) dentro de seus próprios cards.

### 1.3. Paleta de Cores e Tokens Visuais (`:root`)
| Token CSS | Valor Hex / RGBA | Uso na Interface |
| :--- | :--- | :--- |
| `--bg-dark` | `#0b0f17` | Fundo principal da janela |
| `--bg-card` | `#131b29` | Fundo dos painéis e cards |
| `--bg-card-2` | `#192336` | Fundo secundário (inputs, KPIs, listas) |
| `--accent` | `#10b981` | Verde Esmeralda (Acertos na zona-foco, botões primários) |
| `--lime` | `#a3e635` | Verde-Limão Tênis (Destaques de marca, bola, zona selecionada) |
| `--warn` | `#f59e0b` | Âmbar (Avisos, modo de validação `UC09`) |
| `--danger` | `#ef4444` | Vermelho (Erros fora da zona-foco, botão Sair do App) |
| `--court-blue` | `#1e4b7a` | Azul interno oficial da quadra 2D |
| `--court-out` | `#1c352d` | Verde externo ao redor da quadra 2D |

---

## 2. Barra Superior Fixa (`.topbar`)

Presente em todas as telas no topo da janela (`54px` de altura), dividida em 3 áreas:
1. **Identidade (`.brand`):**
   - Ícone `🎾`, título **`TOP TRAINING`** (com `TRAINING` em verde-limão `--lime`) e badge `CV + Homografia 2D`.
2. **Navegação por Etapas (`.step-nav`):**
   - 5 botões numerados que indicam a etapa ativa (`.step-btn.active` em verde-limão):
     - `1. Perfil & Fonte` (`data-view="setup"`)
     - `2. Calibrar Quadra` (`data-view="calibrate"`)
     - `3. Zona-Foco` (`data-view="zone"`)
     - `4. Treino & Vídeo` (`data-view="training"`)
     - `5. Resumo & Ranking` (`data-view="summary"`)
3. **Ações Globais (`.topbar-actions`):**
   - **`🔊 Som: ON / 🔇 Som: OFF` (`#btn-sound-toggle`):** Ativa/desativa os efeitos sonoros sintetizados via *Web Audio API* (acorde ascendente em `587 Hz -> 880 Hz` para acerto; tom grave triangular em `200 Hz -> 140 Hz` para erro).
   - **`🚪 Sair do App` (`#btn-exit-app`):** Botão vermelho que encerra qualquer sessão ativa, dispara `POST /api/shutdown` para encerrar o servidor Python FastAPI e substitui a tela por uma mensagem de encerramento seguro.

---

## 3. Detalhamento das 5 Telas (`views`)

### 3.1. Tela 1 — Perfil do Jogador & Fonte de Vídeo (`#view-setup`)
Layout em **2 colunas iguais (`.grid-2`)**:

- **Coluna Esquerda — Card `👤 Perfil do Jogador & Fonte de Vídeo`:**
  - **Seletor de Perfil (`#profile-select`):** Lista perfis salvos em `app/data/profiles.json` (ex.: `Lukas (3 sessões — Recorde: 60 pts)`) ou permite criar novo.
  - **Campo Nome (`#player-name`):** Input textual para nome do tenista.
  - **Seletor de Fonte (`.radio-cards`):**
    - `🎬 Vídeo Gravado` (`value="video"`): Exibe o seletor `#video-select` com os vídeos de `src/input_videos/` (`treino_1.mp4`, `treino_2.mp4`, `treino_3.mp4`, `quadra_1.MOV`, etc.).
    - `📱 Câmera Ao Vivo (Iriun / USB)` (`value="camera"`): Exibe o seletor `#camera-index` (`Índice 0`, `Índice 1`, `Índice 2`) com dica para conexão USB.

- **Coluna Direita — Card `🎚️ Nível de Dificuldade`:**
  - **3 Cards de Nível (`.level-cards`):**
    - **`Básico` (`2 Zonas`):** *Fundo de Quadra* ($y \in [5.485, 11.885]\text{ m}$) vs. *Área de Saque / Curta* ($y \in [0, 5.485]\text{ m}$).
    - **`Médio` (`3 Zonas`):** *Esquerda*, *Centro* e *Direita* ($8.23\text{ m}$ divididos em 3 faixas verticais de $2.743\text{ m}$).
    - **`Avançado` (`6 Zonas`):** Grade $3 \times 2$ combinando profundidade (Curta/Fundo) e direção (Esquerda/Centro/Direita).
  - **Status de Calibração (`#calib-status-box`):** Mostra se `app/data/homografia.json` já está calibrado (com o erro médio em metros e o vídeo de referência) ou pendente.
  - **Botões de Ação:**
    - `📐 Calibrar Quadra (4 Pontos)` (`#btn-go-calibrate`)
    - `🎯 Escolher Zona-Foco →` (`#btn-go-zone`)

---

### 3.2. Tela 2 — Calibração da Quadra por 4 Pontos (`#view-calibrate`)
Layout em **2 colunas assimétricas (`.calib-layout`: `1fr` esquerda + `340px` direita)**:

- **Área Principal Esquerda (`.calib-canvas-wrap`):**
  - **Canvas Interativo (`#calib-canvas`, `960x540`):** Renderiza um frame real extraído da fonte escolhida (`/api/video-frame`).
  - Permite **clicar para adicionar** até 4 pontos ou **arrastar pontos existentes** (raio de captura de `26px`) para ajuste fino.
  - Desenha o polígono verde translúcido conectando os 4 cantos, linhas pontilhadas amarelas das subdivisões internas e marcadores numerados (`1` a `4`).
  - **Barra de Rodapé do Canvas (`.calib-hint`):** Botões `🔄 Recarregar Frame` (`#btn-reload-frame`), `🗑️ Limpar 4 Pontos` (`#btn-reset-points`) e `🔍 Testar Ponto na Quadra (UC09)` (`#btn-toggle-inspect`).

- **Barra Lateral Direita (`340px`, `.calib-sidebar`):**
  - **Guia de Ordem dos 4 Cantos (`.corner-guide`):**
    1. **1 — Rede Esquerda** $(0.00\text{ m},\ 0.00\text{ m})$
    2. **2 — Rede Direita** $(8.23\text{ m},\ 0.00\text{ m})$
    3. **3 — Fundo Direito** $(8.23\text{ m},\ 11.885\text{ m})$
    4. **4 — Fundo Esquerdo** $(0.00\text{ m},\ 11.885\text{ m})$
  - **Lista de Coordenadas (`#points-coord-list`):** Exibe em tempo real o par `(u, v) px` de cada um dos 4 pontos.
  - **Painel de Validação `UC09` (`#inspect-result-box`):** Quando o modo de inspeção está ativo, qualquer clique na imagem mostra o pixel clicado `(u, v)`, a coordenada real transformada por $H$ em metros `(x m, y m)` e se está `✅ DENTRO DA MEIA-QUADRA` ou `⚠️ FORA DOS LIMITES`.
  - **Botões:** `✅ Calcular Homografia H e Salvar` (`#btn-save-calib`) e `Continuar para Zona-Foco →` (`#btn-calib-next`).

---

### 3.3. Tela 3 — Seleção de Zona-Foco (`#view-zone`)
Layout em **2 colunas (`420px` esquerda + `1fr` direita)**:

- **Coluna Esquerda — Card `🎯 Selecione sua Zona-Foco`:**
  - Mostra o resumo da configuração atual (`Jogador`, `Nível`, `Fonte`).
  - **Card de Destaque da Zona Selecionada (`.selected-zone-card`):** Exibe o nome da zona-foco ativa (ex.: `Fundo Esquerdo`) e suas dimensões em metros.
  - **Regras de Pontuação (`.rules-box`):**
    - **Acerto na Zona-Foco:** `+10 pontos` (som agudo + marcador verde)
    - **Erro (outra zona ou fora):** `-5 pontos` (mínimo `0`, marcador vermelho)
    - **Filtro de 1º Quique:** Apenas o primeiro impacto de cada trajetória na quadra pontua (cooldown de `42 frames`).
  - **Botões:** `← Voltar` e `🚀 Iniciar Análise / Treino` (`#btn-start-training`).

- **Coluna Direita — Representação Vetorial 2D (`#zone-canvas`, `420x580`):**
  - Desenha a meia-quadra oficial em orientação vertical com corredores de duplas, linha de saque, linha central (`T`), rede no topo (`REDE (y = 0.00 m)`) e linha de base na base (`LINHA DE BASE (y = 11.89 m)`).
  - Divide a quadra nas zonas do nível escolhido (`2`, `3` ou `6` zonas).
  - Suporta *hover* com o mouse e clique direto em qualquer zona para selecioná-la (destaque em verde `#10b981` + borda verde-limão `#a3e635` e selo `🎯 ZONA-FOCO`).

---

### 3.4. Tela 4 — Treino & Análise de Vídeo (`#view-training`)
Projetada especificamente para priorizar a **visualização ampla do vídeo** e o **mapa espacial de acertos/erros**, dividida em **3 colunas (`.training-layout-v2`: `265px` esquerda | `1fr` centro | `295px` direita)**:

```text
+--------------------+---------------------------------------------+-----------------------+
| COLUNA ESQUERDA    |              CENTRO PRINCIPAL               |    CANTO DIREITO      |
| (265px)            |              (1fr - Vídeo Grande)           |    (295px - Quadra)   |
|                    |                                             |                       |
| - Info da Sessão   |  +---------------------------------------+  | - Mini-Quadra 2D      |
| - Placar Grande    |  |                                       |  |   (Mapa de Calor c/   |
| - KPIs (✓/✗/%)     |  |     STREAM DE VÍDEO HD (960x540)      |  |    ✓ Acertos / ✗ Erros|
| - Botões Rápidos:  |  |   c/ rastro da bola, polígonos da     |  |    em cada zona)      |
|   * Ver Popup      |  |   quadra e anéis nos quiques          |  |                       |
|   * Resumo/Ranking |  |                                       |  | - Card 🔥 Mais Acertos|
|   * Trocar Zona    |  +---------------------------------------+  | - Card ⚠️ Mais Erros  |
|   * Trocar Vídeo   |  [⏸️ Pausar] [🔄 Reiniciar] [Barra Seek]    |                       |
| - Log Clicável     |  [Pular p/ Quique: 🎯 #1 (23.9s) ...]       |                       |
+--------------------+---------------------------------------------+-----------------------+
```

1. **Coluna Esquerda (`265px`, `.training-left-panel`):**
   - **Metadados Compactos:** Jogador, Nível e Zona-Foco ativa.
   - **Placar Principal (`.big-score-box.compact`):** Pontuação total em destaque (`#live-score`, fonte `2.2rem` verde-limão).
   - **3 Mini-KPIs (`.mini-kpis`):** `Acertos` (verde), `Erros` (vermelho) e `Precisão (%)`.
   - **Botões de Ação e Navegação Rápida:**
     - `📊 Ver Popup "Vídeo Analisado"` (`#btn-reopen-analysis-modal`): Reabre o relatório completo do vídeo a qualquer momento.
     - `🏆 Ir para Resumo & Ranking` (`#btn-stop-training`): Finaliza a sessão, persiste os dados em `profiles.json` e abre a Tela 5.
     - `🎯 Trocar Zona / Nível` (`#btn-quick-change-zone`): Interrompe a sessão atual e retorna direto para a Tela 3.
     - `⚙️ Trocar Vídeo / Fonte` (`#btn-quick-change-source`): Interrompe a sessão atual e retorna para a Tela 1.
   - **Histórico de Quiques (`#live-shot-log`):** Lista rolável com cada bola detectada (`#1 🎯 Zona (+10 pts) 23.9s — ▶️ Ver`). Clicar em qualquer item salta o vídeo diretamente para o momento daquele quique.

2. **Centro Principal (`1fr`, `.big-video-stage`):**
   - **Palco do Vídeo (`.video-frame-container.big-stage`):**
     - Exibe o stream MJPEG (`#live-video-stream`, `960x540`) anotado pelo OpenCV com:
       - Polígono verde da quadra calibrada e subdivisões tracejadas;
       - Bounding box amarela e centroide verde na bola em movimento;
       - **Rastro Dinâmico (18 frames):** Linha contínua ciano/amarela ligando as posições recentes da bola;
       - **Anéis de Impacto no Quique:** Círculo duplo verde (`ACERTOK!`) ou vermelho (`FORA DA ZONA`) com efeito de onda (*ripple*) que permanece visível por 18 frames após o impacto.
     - **Overlay de Análise em Lote (`#video-analyzing-overlay`):** Enquanto um vídeo gravado está sendo processado pelo YOLOv8, exibe um *spinner* animado, barra de progresso (`#analyzing-progress-fill`) e porcentagem/frames concluídos.
     - **Banner de Último Evento (`#last-shot-banner`):** Badge flutuante no topo esquerdo do vídeo indicando o resultado do último quique.
   - **Barra de Controles e Timeline (`.video-controls-bar`):**
     - Botões `⏸️ Pausar / ▶️ Continuar` (`#btn-pause-resume`) e `🔄 Reiniciar` (`#btn-restart-session`).
     - **Barra de Progresso Clicável (`#video-seek-bar`):** Mostra o tempo atual / total (`00:23 / 00:26`) e permite clicar em qualquer ponto para saltar (`POST /api/session/seek`).
     - **Chips de Salto Rápido para Quiques (`#bounce-jump-chips`):** Botões pílula gerados automaticamente para cada quique detectado no vídeo (ex.: `🎯 #1 (23.9s)`). Ao clicar, o vídeo posiciona-se alguns frames antes do quique (`frame - 12`) para o jogador rever a trajetória completa e o impacto.

3. **Canto Direito (`295px`, `.training-corner-court-card`):**
   - **Mini-Quadra 2D com Mapa de Calor (`#training-court-canvas`, `300x420`):**
     - Desenha a quadra vertical no canto direito com **coloração de densidade (*heatmap*)** por zona (verde proporcional aos acertos na zona-foco; vermelho proporcional aos erros nas demais zonas).
     - Exibe dentro de cada zona o contador **`✓ X  |  ✗ Y`** (quantidade de acertos e erros que caíram naquela região específica).
     - Plota todos os quiques da sessão como **círculos numerados** (`#1`, `#2`...) na coordenada exata $(x, y)$ em metros, com anel pulsante no último quique.
   - **Cards de Densidade Espacial (`.court-heatmap-summary`):**
     - `🔥 Mais Acertos` (`#corner-most-hits-zone`): Nome da zona com maior volume de acertos e contagem.
     - `⚠️ Mais Erros` (`#corner-most-errors-zone`): Nome da zona (ou `Fora da Quadra`) onde mais ocorreram erros.

---

### 3.5. Popup Modal `"Vídeo Analisado!"` (`#modal-video-analyzed`)
Assim que a análise completa de um vídeo gravado termina (`analysis_done: true`), este modal *glassmorphism* abre automaticamente sobre a Tela 4:
- **Cabeçalho:** Badge `ANÁLISE COMPLETA CONCLUÍDA`, título **`✅ Vídeo Analisado!`** e subtítulo com nome do arquivo e total de frames processados.
- **4 KPIs Principais (`.modal-kpi-grid`):**
  - `Pontuação Total` (`#modal-kpi-score`)
  - `Total de Quiques` (`#modal-kpi-total`)
  - `Acertos na Zona` (`#modal-kpi-hits`)
  - `Erros / Fora` (`#modal-kpi-misses`)
- **2 Cards de Densidade Espacial (`.modal-heatmap-zones`):**
  - `🔥 Região com Mais Acertos` (`#modal-best-zone`)
  - `⚠️ Região com Mais Erros` (`#modal-worst-zone`)
- **Lista Detalhada de Quiques (`#modal-shots-list`):** Lista todos os quiques detectados com número, zona atingida, coordenadas em metros $(x, y)$, instante em segundos + frame exato, pontuação (`+10 pts` / `-5 pts`) e botão **`▶️ Ver no vídeo`** (que fecha o modal e salta o vídeo para aquele lance).
- **Rodapé de Ações:**
  - `🎬 Rever Vídeo & Mapa de Calor` (`#btn-close-modal-watch`): Fecha o popup para assistir ao vídeo grande na Tela 4 e usar os botões de salto rápido.
  - `🏆 Finalizar e Ver Ranking` (`#btn-modal-go-summary`): Salva a sessão e avança para a Tela 5.

---

### 3.6. Tela 5 — Resumo da Sessão & Ranking (`#view-summary`)
Apresenta o fechamento consolidado do treino:
- **Linha Superior com 4 KPIs (`.summary-top-kpis`):**
  - `Pontuação Final` (`#sum-score`)
  - `Precisão na Zona-Foco` (`#sum-accuracy`)
  - `Acertos / Total de Bolas` (`#sum-hits-total`)
  - `Nível & Zona` (`#sum-level-zone`)
- **Grid Principal (`.summary-grid`):**
  - **Esquerda — `🗺️ Mapa Final de Quiques na Quadra`:** Canvas `#summary-court-canvas` (`360x500`) com todos os impactos numerados e estatísticas por zona, acompanhado dos botões `🔁 Novo Treino (Mesma Config)` (`#btn-play-again`) e `⚙️ Mudar Jogador / Vídeo / Nível` (`#btn-back-setup`).
  - **Direita — `🥇 Ranking Local por Nível`:** Tabela `#leaderboard-body` com abas de filtro para `Nível Básico`, `Nível Médio` e `Nível Avançado`, listando posição (`🥇 1º`, `🥈 2º`, `🥉 3º`), jogador, zona-foco, pontuação, precisão e data/hora salvos em `app/data/profiles.json`.

---

## 4. Endpoints da API Consumidos pela Interface (`app.js` ↔ `app_main.py`)

| Método e Rota | Uso na Interface (`app.js`) |
| :--- | :--- |
| `GET /api/init` | Carrega vídeos disponíveis, perfis salvos, calibração `H` atual e definições de níveis/zonas ao abrir o app. |
| `GET /api/video-frame` | Extrai um frame (`JPEG`) de um vídeo ou câmera para desenhar no Canvas da Tela 2 (Calibração). |
| `POST /api/calibrate` | Envia os 4 pontos `(u, v)` em pixels, calcula a matriz $H$ ($3\times 3$) e salva em `app/data/homografia.json`. |
| `POST /api/homography/pixel-to-meter` | Valida em tempo real (`UC09`) qualquer clique no Canvas de calibração, retornando `(x_m, y_m)` e se está dentro da quadra. |
| `POST /api/session/start` | Inicia uma sessão de análise de vídeo em lote ou câmera ao vivo. |
| `GET /api/session/state` | Consultado a cada `250 ms` para atualizar placar, progresso da análise, lista de quiques (`shots`), `zone_stats` e disparo do modal. |
| `GET /api/stream` | Stream MJPEG contínuo exibido na tag `<img id="live-video-stream">` da Tela 4. |
| `POST /api/session/control` | Pausa (`pause`), retoma (`resume`), reinicia (`restart`) ou encerra (`stop`) a sessão. |
| `POST /api/session/seek` | Posiciona o vídeo analisado em um frame específico (usado na barra de progresso e nos botões `🎯 #1 (23.9s)`). |
| `POST /api/session/finish` | Persiste o resultado da sessão no perfil do jogador em `app/data/profiles.json`. |
| `GET /api/leaderboard/{level}` | Carrega o ranking ordenado por pontuação para a aba selecionada na Tela 5. |
| `POST /api/shutdown` | Acionado pelo botão `🚪 Sair do App` para encerrar o servidor Python com segurança. |

