# Top Training - Analisador de Treino de Tênis

Aplicativo leve e moderno para análise de treino de tênis que utiliza a câmera do celular (via Iriun Webcam) para rastrear quiques da bola e analisar se foram dentro ou fora de zonas específicas da quadra.

## Stack

- Python 3
- DearPyGui (UI desktop)
- OpenCV (visão computacional)
- YOLOv8 Nano via Ultralytics (detecção de bola de tênis)

## Estrutura

```
docs/             # Documentação de escopo, arquitetura e roteiro
src/              # Código fonte da aplicação
  main.py         # Ponto de entrada
  ui/             # Interface DearPyGui
  cv/             # Visão computacional (detecção, rastreio, calibração)
  models/         # Modelos YOLO (.pt)
  data/           # Perfis e sessões de treino (JSON)
  utils/          # Utilitários (config, logger)
  assets/         # Recursos estáticos
tests/            # Testes automatizados
notebooks/        # Notebooks (Colab / treino de modelo)
scripts/          # Scripts auxiliares
```

## Instalação

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Execução

```powershell
python src/main.py
```

## Licença

Projeto acadêmico - UFSC 2026-2
