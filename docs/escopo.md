# Escopo do Projeto - Top Training

## Resumo

Top Training é um aplicativo desktop leve e moderno para análise de treino de tênis. O sistema utiliza a câmera do celular (transmitida via Iriun Webcam) posicionada do lado oposto ao jogador para rastrear a bola de tênis, detectar quiques e pontuar o treino com base em alvos (zonas da quadra) definidos por diferentes níveis de dificuldade.

## Funcionalidades

1. **Menu Inicial**
   - Criação e seleção de Perfil de Jogador (nome salvo localmente para histórico).
   - Botão para Iniciar Treino ou Recalibrar a Quadra.

2. **Mapeamento da Quadra (Calibração)**
   - Abre o feed da câmera.
   - O usuário seleciona pontos manualmente na tela para criar um polígono que representa o lado oposto da quadra (da rede até a linha de fundo).
   - Apenas bolas que passam por dentro deste polígono são analisadas.

3. **Seleção de Dificuldade**
   - Básico, Médio ou Avançado.
   - Cada dificuldade divide a quadra mapeada em quadrantes/alvos diferentes.
   - Bola quicando dentro da zona alvo = ponto; fora = perde ponto.

4. **Interface de Treino (DearPyGui)**
   - Visual moderno com esquema de cores baseado em imagem de referência.
   - Mapa 2D da quadra na vertical (apenas linhas de marcação).
   - Feedback visual: pontos verdes (acertos) e vermelhos (erros) plotados em tempo real no mapa 2D no local exato do quique.
   - Painel direito: contador de bolas certas, erradas e pontuação total.
   - Painel esquerdo/superior: botões Voltar, Salvar Treino e Trocar Dificuldade.

## Stack Tecnológica

- Linguagem: Python 3
- Interface: DearPyGui
- Visão Computacional: OpenCV + YOLOv8 Nano (Ultralytics)
- Modelo: pré-treinado consolidado para bolas de tênis (treino via Colab futuro)

## Repositório de Inspiração

- https://github.com/abdullahtarek/tennis_analysis

## Referências Visuais / Tracking

- https://www.youtube.com/watch?v=lXhAkXBjyAc
- https://www.youtube.com/watch?v=L23oIHZE14w&t=690s
- https://www.youtube.com/shorts/SHO8jeI6gB4
- https://www.youtube.com/watch?v=oIvehDV_C30&t=2385s

## Fora de Escopo (Primeira Entrega)

- Treino customizado de modelo YOLO (usar pré-treinado).
- Salvamento em nuvem / sincronização de perfis.
- Análise de vídeo gravado (apenas feed ao vivo da câmera).
- Múltiplas câmeras / visão estéreo.
