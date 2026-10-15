# Arquitetura e Responsabilidades de Cada Pasta

## Visão Geral

A aplicação segue uma arquitetura modular separando interface (UI), lógica de visão computacional (CV), modelos, dados e utilitários. O ponto de entrada é `src/main.py`.

## Estrutura de Pastas

```
docs/             Documentação (escopo, arquitetura, roteiro)
src/              Código fonte
  main.py         Ponto de entrada e orquestrador da aplicação
  ui/             Interface gráfica DearPyGui
    main_window.py    Menu inicial, perfis, iniciar/recaliibrar
    calibration_window.py  Feed da câmera + seleção de pontos do polígono
    training_window.py   Mapa 2D, feedback visual, painel de contadores
    components.py   Componentes reutilizáveis (botões, painéis, mapas)
  cv/             Visão computacional
    detector.py   Detecção de bola de tênis via YOLOv8
    tracker.py    Rastreio da bola e detecção de quiques (bounce)
    court.py      Mapeamento/calibração da quadra (polígono)
    geometry.py   Utilitários de geometria (ponto dentro polígono, zonas)
  models/         Modelos YOLO (.pt) - não versionados
  data/           Armazenamento local de dados
    profiles/     Perfis de jogadores (JSON)
    sessions/     Sessões de treino (JSON)
  utils/          Utilitários
    config.py     Carregamento de configurações (YAML)
    logger.py     Log da aplicação
  assets/         Recursos estáticos (ícones, imagens)
tests/            Testes automatizados
notebooks/        Notebooks (Colab / treino futuro de modelo)
scripts/          Scripts auxiliares
```

## Responsabilidades por Módulo

### src/main.py
- Inicializa o contexto DearPyGui.
- Gerencia o ciclo de vida das telas (menu -> calibração -> treino).
- Orquestra a troca de dificuldade e salvamento de treino.

### src/ui/
- Renderiza todos os elementos visuais com DearPyGui.
- Captura interações do usuário (cliques, seleção de pontos na calibração).
- Não contém lógica de CV; delega para os módulos de `src/cv/`.

### src/cv/detector.py
- Carrega o modelo YOLOv8 Nano.
- Recebe frames da câmera e retorna bounding boxes da bola de tênis.

### src/cv/tracker.py
- Rastreia a bola entre frames.
- Detecta quiques (bounce) com base na trajetória vertical.
- Emite eventos de quique com coordenadas no frame.

### src/cv/court.py
- Gerencia a calibração da quadra (polígono definido pelo usuário).
- Valida se um ponto está dentro do polígono da quadra.

### src/cv/geometry.py
- Cálculo de ponto dentro de polígono.
- Divisão da quadra em zonas/quadrantes por dificuldade.
- Mapeamento de coordenadas do frame para coordenadas do mapa 2D.

### src/data/
- Leitura/escrita de perfis de jogador (JSON).
- Leitura/escrita de sessões de treino (JSON).

### src/utils/
- `config.py`: parâmetros da aplicação (cores, resoluções, zonas).
- `logger.py`: logging padronizado.

## Fluxo de Dados

1. Câmera (Iriun Webcam) -> OpenCV captura frame.
2. `cv/detector.py` -> detecta bola no frame (YOLOv8).
3. `cv/tracker.py` -> rastreia bola e detecta quiques.
4. `cv/court.py` + `cv/geometry.py` -> valida se quique está dentro do polígono e qual zona.
5. `ui/training_window.py` -> plota ponto verde/vermelho no mapa 2D e atualiza contadores.
6. `data/sessions/` -> persiste resultado da sessão ao salvar.

## Regras de Negócio

- Apenas quiques dentro do polígono da quadra são contabilizados.
- Pontuação: acerto na zona alvo = +1 ponto; fora da zona alvo (mas dentro do polígono) = -1 ponto.
- Dificuldades determinam o número e tamanho das zonas alvo.
- Histórico de perfis é salvo localmente em JSON.
