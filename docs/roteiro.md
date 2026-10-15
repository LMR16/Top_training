# Roteiro de Desenvolvimento

Todo prompt futuro deverá consultar `docs/escopo.md` e `docs/arquitetura.md` para manter a organização do projeto.

## Fase 1 - Fundação (Entrega Atual) ✅

- [x] Estrutura de pastas profissional (arquitetura modular).
- [x] Documentação de contexto (`docs/escopo.md`, `docs/arquitetura.md`, `docs/roteiro.md`).
- [x] `requirements.txt` com dependências iniciais.
- [x] `.gitignore` padrão para Python/YOLO.
- [x] Inicialização do repositório Git.

## Fase 2 - Configuração e Utilitários

- [ ] `src/utils/config.py`: carregamento de configurações YAML (cores, resolução, zonas).
- [ ] `src/utils/logger.py`: logging da aplicação.
- [ ] `src/cv/geometry.py`: utilitários de geometria (ponto dentro polígono, zonas por dificuldade).
- [ ] `src/data/__init__.py` e utilitários de leitura/escrita JSON para perfis e sessões.

## Fase 3 - Visão Computacional

- [ ] `src/cv/detector.py`: detecção de bola de tênis com YOLOv8 Nano (modelo pré-treinado).
- [ ] `src/cv/tracker.py`: rastreio da bola e detecção de quiques (bounce).
- [ ] `src/cv/court.py`: calibração da quadra via polígono definido pelo usuário.
- [ ] Testes de detecção com feed da câmera (Iriun Webcam).

## Fase 4 - Interface DearPyGui

- [ ] `src/ui/components.py`: componentes reutilizáveis (botões, painéis, mapa 2D).
- [ ] `src/ui/main_window.py`: menu inicial, perfis, iniciar/recaliibrar.
- [ ] `src/ui/calibration_window.py`: feed da câmera + seleção de pontos do polígono.
- [ ] `src/ui/training_window.py`: mapa 2D, feedback visual (verde/vermelho), painel de contadores.
- [ ] `src/main.py`: ponto de entrada e orquestrador de telas.

## Fase 5 - Integração e Refinamento

- [ ] Integração UI <-> CV <-> Dados.
- [ ] Seleção de dificuldade (Básico/Médio/Avançado) com zonas diferentes.
- [ ] Salvamento de treino e histórico de perfis.
- *Nesta etapa será definido o esquema de cores baseado na imagem de referência enviada pelo usuário.*

## Fase 6 - Testes e Documentação Final

- [ ] Testes unitários em `tests/`.
- [ ] README atualizado com instruções de uso.
- [ ] Notebook em `notebooks/` para treino futuro de modelo YOLO via Colab (opcional).

## Comandos de Referência

```powershell
# Criar e ativar virtualenv
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Instalar dependências
pip install -r requirements.txt

# Executar aplicação
python src/main.py

# Inicializar git
git init
git add .
git commit -m "chore: estrutura inicial do projeto"
```
