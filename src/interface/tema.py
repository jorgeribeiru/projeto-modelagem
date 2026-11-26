"""Cores (pares claro/escuro do CustomTkinter) e fontes da interface."""
import tkinter.font
from dataclasses import dataclass

import customtkinter as ctk

from src.visualizacao import FONTES_PREFERIDAS, MODO_CLARO, MODO_ESCURO, TEMAS, cor_da_curva

_claro, _escuro = TEMAS[MODO_CLARO], TEMAS[MODO_ESCURO]

FUNDO = (_claro.fundo, _escuro.fundo)
CARTAO = (_claro.painel, _escuro.painel)
CARTAO_ELEVADO = ("#F1F3F8", "#1B2336")
BORDA = ("#E3E6EE", "#242D42")
TEXTO = (_claro.texto, _escuro.texto)
TEXTO_SUAVE = (_claro.texto_suave, _escuro.texto_suave)
DESTAQUE = (_claro.destaque, _escuro.destaque)
DESTAQUE_HOVER = ("#6D28D9", "#8B5CF6")
DESTAQUE_SUAVE = ("#EEE8FD", "#2A2350")
DESTAQUE_PULSO = ("#C4B5FD", "#6D5BD0")
PRIMARIO = ("#7C3AED", "#7C3AED")
PRIMARIO_HOVER = ("#6D28D9", "#6D28D9")
SEGMENTO_FUNDO = ("#E9ECF3", "#1E2638")
SEGMENTO_HOVER = ("#DCE0EA", "#2A3349")
SOBRE_DESTAQUE = "#FFFFFF"

MODOS_CTK = {MODO_CLARO: "light", MODO_ESCURO: "dark"}


def cor_curva(nome: str) -> tuple[str, str]:
    return cor_da_curva(nome, MODO_CLARO), cor_da_curva(nome, MODO_ESCURO)


def resolver_cor(par: tuple[str, str], modo: str) -> str:
    """Escolhe a cor do par conforme o modo (para widgets Tk puros, como o canvas do gráfico)."""
    return par[1] if modo == MODO_ESCURO else par[0]


@dataclass
class Fontes:
    titulo: ctk.CTkFont
    subtitulo: ctk.CTkFont
    secao: ctk.CTkFont
    corpo: ctk.CTkFont
    corpo_forte: ctk.CTkFont
    pequena: ctk.CTkFont
    rotulo: ctk.CTkFont
    numero: ctk.CTkFont
    numero_grande: ctk.CTkFont
    guia_titulo: ctk.CTkFont


def criar_fontes() -> Fontes:
    """Deve ser chamada depois que a janela raiz existir."""
    instaladas = set(tkinter.font.families())
    familia = next((f for f in FONTES_PREFERIDAS if f in instaladas), "TkDefaultFont")
    mono = next((f for f in ("JetBrains Mono", "Fira Mono", "DejaVu Sans Mono") if f in instaladas), "TkFixedFont")

    def fonte(tamanho: int, peso: str = "normal", fam: str = familia) -> ctk.CTkFont:
        return ctk.CTkFont(family=fam, size=tamanho, weight=peso)

    return Fontes(
        titulo=fonte(19, "bold"),
        subtitulo=fonte(13),
        secao=fonte(12, "bold"),
        corpo=fonte(13),
        corpo_forte=fonte(13, "bold"),
        pequena=fonte(11),
        rotulo=fonte(10, "bold"),
        numero=fonte(13, fam=mono),
        numero_grande=fonte(22, "bold"),
        guia_titulo=fonte(20, "bold"),
    )
