"""Componentes reutilizáveis da interface DearPyGui."""

import dearpygui.dearpygui as dpg
from typing import Callable

# Paleta de cores (tons de azul para a quadra)
COR_FUNDO = [24, 30, 44]
COR_QUADRA = [30, 80, 120]
COR_LINHA = [230, 230, 230]
COR_ACERTO = [0, 220, 120]
COR_ERRO = [240, 60, 60]
COR_TEXTO = [235, 235, 235]
COR_DESTAQUE = [60, 140, 200]
COR_BOTAO = [50, 110, 170]
COR_BOTAO_HOVER = [70, 150, 220]


def aplicar_tema_global() -> None:
    with dpg.theme() as tema_global:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, COR_FUNDO, category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, COR_FUNDO, category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_PopupBg, [40, 48, 64], category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_Border, COR_LINHA, category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_Button, COR_BOTAO, category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, COR_BOTAO_HOVER, category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, [40, 80, 130], category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_Text, COR_TEXTO, category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, [40, 48, 64], category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_Header, COR_DESTAQUE, category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, [80, 160, 230], category=dpg.mvThemeCat_Core)
    dpg.bind_theme(tema_global)


def estilo_fonte_titulo() -> int:
    with dpg.font_registry():
        fonte = dpg.add_font("ProggyClean.ttf", 24)
    return fonte


def painel_titulo(texto: str, largura: int) -> None:
    dpg.add_text(texto, color=[200, 220, 255])
    dpg.add_separator()


def texto_placar(rotulo: str, valor: int, cor: list[int]) -> None:
    with dpg.group(horizontal=True):
        dpg.add_text(rotulo + ": ")
        dpg.add_text(str(valor), color=cor)
