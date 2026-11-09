# Especificação da Interface Gráfica (Stealth Dark Minimal) — Top Training App

> **Propósito deste arquivo:** Documentar a arquitetura visual minimalista, o fluxo de foco único por tela (sem barra de abas superior), a camada de imagem de fundo e os componentes interativos da interface web do **Top Training** (`app/static/`).

---

## 1. Filosofia Visual: *Stealth Dark Minimal*

A interface foi projetada com foco em **minimalismo tecnológico** (inspirada em produtos como Apple/Vercel/Linear), eliminando textos longos, caixas redundantes e barras de navegação superiores.

### 1.1. Paleta de Cores (`app/static/style.css`)
| Token CSS | Valor | Papel Visual |
| :--- | :--- | :--- |
| `--bg-obsidian` | `#09090b` | Preto fosco de fundo principal |
| `--bg-surface` | `rgba(18, 18, 21, 0.88)` | Superfície grafite translúcida com `backdrop-filter: blur(20px)` |
| `--bg-elevated` | `#18181b` | Controles internos, inputs e botões secundários |
| `--border-subtle` | `rgba(255, 255, 255, 0.08)` | Bordas ultrafinas (`1px`) |
| `--text-primary` | `#fafafa` | Texto principal branco puro |
| `--text-secondary` | `#a1a1aa` | Subtítulos e rótulos secundários |
| `--emerald` | `#10b981` | Verde Esmeralda (Ação principal, zona-foco, acertos) |
| `--danger` | `#ef4444` | Vermelho (Erros fora da zona) |

### 1.2. Camada de Imagem de Fundo (`#app-bg-layer`)
- Carrega automaticamente qualquer imagem salva em **`app/static/bg_tennis.jpg`** ou **`app/static/bg_tennis.png`**.
- **Modo Destaque (`body.bg-vivid`):** Ativo na **Tela Inicial de Perfil** e no **Hub do Jogador**, aplicando uma película escura suave (`rgba(9, 9, 11, 0.52) -> 0.84`) que valoriza a imagem de tênis ao fundo.
- **Modo Foco Técnico (`body.bg-dimmed`):** Ativo nas telas de **Preparação (Quadra 2D)**, **Vídeo/Treino**, **Calibração** e **Ranking**, escurecendo o fundo em `93%` com `blur(16px)` para não distrair a visualização da bola.

### 1.3. Controles Flutuantes nos Cantos (`.floating-hud-top`)
Sem barra superior (`.topbar` removida):
- **Canto Superior Esquerdo:** Botão flutuante discreto `← Voltar` (`#btn-global-back`, oculto apenas na Tela 1) e assinatura minimalista `● TOP TRAINING`.
- **Canto Superior Direito:** Pílula do jogador ativo (`#hud-player-pill`), botão `Som: ON/OFF` (`#btn-sound`) e botão `Sair` (`#btn-exit-app` -> `POST /api/shutdown`).

---

## 2. Fluxo de Telas (Foco Único por Tela)

```text
[1. Box Central: Perfil] ──► [2. Box Central: Hub do Jogador]
                                   │
         ┌─────────────────────────┼─────────────────────────┐
         ▼                         ▼                         ▼
[3. Preparar Treino]      [5. Calibrar Quadra]      [6. Ranking Geral]
(Fonte + Nível + Quadra)     (4 Cantos em px)          (Tabela por Nível)
         │
         ▼
[4. Vídeo (78%) + Mini-Quadra (22%)] + [Popup "Vídeo Analisado"]
```

### 2.1. Tela 1 — Box Central de Perfil (`#view-profile`)
- Único box centralizado (`max-width: 420px`) sobre a imagem de fundo.
- Exibe **pílulas clicáveis** (`#profile-chips-list`) para seleção imediata de perfis salvos em `app/data/profiles.json` e um campo limpo (`#input-player-name`) para criar ou editar o nome do jogador.
- Botão principal verde esmeralda **`Continuar →`** (`POST /api/profile`), que leva ao Hub.

### 2.2. Tela 2 — Hub do Jogador (`#view-hub`)
- Box central (`max-width: 420px`) com o nome do jogador ativo e dois indicadores rápidos (`Sessões` e `Recorde`).
- **3 Botões de Ação:**
  1. **`Iniciar Treino →`** (destaque esmeralda -> abre `#view-zone`)
  2. **`Calibrar Quadra`** (com badge `Calibrada` ou `Padrão` -> abre `#view-calibrate`)
  3. **`Ranking →`** (abre `#view-summary`)
- Link discreto `Trocar de perfil` na base do card.

### 2.3. Tela 3 — Preparação do Treino: Painel Único + Quadra 2D (`#view-zone`)
- Zero textos longos de regras; layout dividido em:
  - **Painel Esquerdo (`340px`):** Apenas 3 controles diretos:
    1. **Fonte de captura:** Chave segmentada `Vídeo | Câmera Ao Vivo` + seletor do arquivo/câmera.
    2. **Nível de divisão:** Pílulas segmentadas `Básico | Médio | Avançado`.
    3. **Zona-foco selecionada:** Exibe a zona ativa + botão **`Iniciar →`**.
  - **Card Direito:** Canvas interativo da meia-quadra (`#zone-canvas`, `400x540`) em estilo *Stealth Dark* para clicar na zona desejada.

### 2.4. Tela 4 — Treino & Vídeo em 2 Colunas Limpas (`#view-training`)
Eliminada a coluna lateral esquerda antiga. A tela possui apenas **2 colunas (`1fr` esquerda | `290px` direita)**:
- **Esquerda (`~78%` — Palco do Vídeo):**
  - Stream de vídeo grande (`#live-video-feed`) com rastro da bola e anéis nos quiques.
  - Overlay minimalista de processamento (`#video-analyzing-overlay`) durante a análise do vídeo.
  - Faixa inferior enxuta com botões `Pausar` / `Reiniciar`, barra de progresso clicável (`#video-seek-bar`) e **chips de salto rápido para cada quique** (`#1 (23.9s) ✓`).
- **Direita (`290px` — Painel HUD Único):**
  - **Placar Compacto:** Pontos em destaque esmeralda + `Acertos`, `Erros` e `Precisão`.
  - **Mini-Quadra 2D (`#training-court-canvas`, `260x360`):** Mapa de calor por zona (`✓ | ✗`) + bolinhas numeradas dos quiques.
  - **Resumo de Densidade:** 2 linhas compactas (`Mais acertos` / `Mais erros`).
  - **Botões:** `Ver Relatório de Quiques` (reabre o modal) e `Concluir Sessão`.

### 2.5. Popup Modal `"Vídeo Analisado"` (`#modal-video-analyzed`)
- Dispara automaticamente ao término da análise do vídeo completo.
- Exibe 4 KPIs (`Pontos`, `Acertos`, `Erros`, `Precisão`), resumo de densidade (`Mais acertos` / `Mais erros`), lista rolável clicável de quiques (`Ver →` salta o vídeo para o instante do lance) e botões `Ver Ranking` e `Assistir Vídeo & Mapa →`.

### 2.6. Telas 5 e 6 — Calibração (`#view-calibrate`) e Ranking (`#view-summary`)
- **Calibração:** Canvas grande à esquerda (`#calib-canvas`) e coluna direita enxuta (`290px`) com a ordem dos 4 cantos, botão `Salvar Calibração` e chave opcional `Inspecionar ponto em metros`.
- **Ranking & Resumo:** Coluna esquerda (`340px`) com pontuação e mapa final da última sessão + botões `Menu` e `Novo Treino`; coluna direita com a tabela limpa de Ranking filtrada por `Básico | Médio | Avançado`.
