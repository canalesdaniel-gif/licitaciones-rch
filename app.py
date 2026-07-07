"""
Sistema de Análisis de Licitaciones - RCH
==========================================

MVP en Streamlit para descubrir, evaluar y dar seguimiento a licitaciones
públicas chilenas del rubro construcción y restauración patrimonial.

Ejecución local:
    streamlit run app.py

Despliegue en Railway / Render / Streamlit Cloud:
    Apuntar al comando anterior, exponer puerto 8501.
"""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from typing import Any

import pandas as pd
import streamlit as st

import analisis_ia
import api_mercado_publico as mp
import data_store as ds
import demo_data
import scoring


# ============================================================================
# Configuración general
# ============================================================================

st.set_page_config(
    page_title="RCH | Análisis de Licitaciones",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Paleta RCH
CARMESI = "#A6212B"
CARMESI_OSCURO = "#8A1C24"
NEGRO_PATRIMONIAL = "#1A1A1A"
ESTUCO = "#EDEAE5"
ESTUCO_CLARO = "#F5F3EF"
PIZARRA = "#3D3D3D"
CONCRETO = "#7A7A7A"
VERDE_RECUPERACION = "#2E7D5B"
AMBAR_CAUTELA = "#D89A1F"
LIENZO = "#FAF9F7"
BORDE = "#E3DFD8"

# Nombre de la propia empresa, para distinguir en qué adjudicaciones participó
# o ganó RCH frente a la competencia.
RCH_EMPRESA = "RCH Construcción & Restauración"


CSS = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700;800;900&family=Source+Sans+3:wght@400;500;600;700&display=swap');

    :root {{
        --carmesi: {CARMESI};
        --carmesi-oscuro: {CARMESI_OSCURO};
        --borde: {BORDE};
        --sombra-sm: 0 1px 2px rgba(26,26,26,0.04), 0 1px 3px rgba(26,26,26,0.06);
        --sombra-md: 0 2px 4px rgba(26,26,26,0.05), 0 4px 12px rgba(26,26,26,0.08);
        --sombra-lg: 0 6px 16px rgba(26,26,26,0.10), 0 2px 6px rgba(26,26,26,0.06);
    }}

    html, body, [class*="css"]  {{
        font-family: 'Source Sans 3', sans-serif;
        color: {NEGRO_PATRIMONIAL};
    }}

    /* Lienzo general con un tinte cálido para que las tarjetas blancas resalten */
    .stApp {{
        background-color: {LIENZO};
    }}

    h1, h2, h3, h4 {{
        font-family: 'Montserrat', sans-serif !important;
        color: {NEGRO_PATRIMONIAL};
        font-weight: 700 !important;
        letter-spacing: -0.01em;
    }}

    h1 {{
        position: relative;
        padding-bottom: 0.6rem;
        margin-bottom: 1.5rem;
        font-weight: 800 !important;
    }}

    h1::after {{
        content: "";
        position: absolute;
        left: 0;
        bottom: 0;
        width: 64px;
        height: 3px;
        background: linear-gradient(90deg, {CARMESI}, {AMBAR_CAUTELA});
        border-radius: 3px;
    }}

    h3 {{
        margin-top: 0.4rem;
    }}

    /* ---- Botones ---- */
    .stButton > button {{
        background-color: {CARMESI};
        color: white;
        border: none;
        font-family: 'Montserrat', sans-serif;
        font-weight: 600;
        border-radius: 6px;
        padding: 0.5rem 1.1rem;
        box-shadow: var(--sombra-sm);
        transition: transform 0.12s ease, box-shadow 0.12s ease, background-color 0.18s ease;
    }}

    .stButton > button:hover {{
        background-color: {CARMESI_OSCURO};
        color: white;
        transform: translateY(-1px);
        box-shadow: var(--sombra-md);
    }}

    .stButton > button:active {{
        transform: translateY(0);
        box-shadow: var(--sombra-sm);
    }}

    .stButton > button:focus {{
        background-color: {CARMESI};
        color: white;
        box-shadow: 0 0 0 3px rgba(166, 33, 43, 0.25);
    }}

    /* Botones secundarios (kind="secondary") con look de contorno */
    .stButton > button[kind="secondary"] {{
        background-color: white;
        color: {CARMESI};
        border: 1.5px solid {BORDE};
        box-shadow: none;
    }}
    .stButton > button[kind="secondary"]:hover {{
        background-color: {ESTUCO_CLARO};
        border-color: {CARMESI};
        color: {CARMESI};
    }}

    /* Clase manual de respaldo */
    .secundario .stButton > button {{
        background-color: white;
        color: {CARMESI};
        border: 1.5px solid {CARMESI};
    }}

    /* ---- Sidebar ---- */
    section[data-testid="stSidebar"] {{
        background-color: {ESTUCO};
        border-right: 1px solid {BORDE};
    }}

    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {{
        color: {NEGRO_PATRIMONIAL};
    }}

    /* Navegación tipo "nav items" con el radio del sidebar */
    section[data-testid="stSidebar"] div[role="radiogroup"] label {{
        display: flex;
        align-items: center;
        padding: 0.5rem 0.7rem;
        margin-bottom: 0.25rem;
        border-radius: 8px;
        font-family: 'Montserrat', sans-serif;
        font-weight: 600;
        font-size: 0.92rem;
        color: {PIZARRA};
        cursor: pointer;
        transition: background-color 0.15s ease, color 0.15s ease;
    }}
    section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {{
        background-color: rgba(166, 33, 43, 0.07);
        color: {CARMESI};
    }}
    /* Oculta el círculo del radio para un look de menú */
    section[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child {{
        display: none;
    }}
    /* Estado seleccionado: la opción marcada */
    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {{
        background-color: {CARMESI};
        color: white;
        box-shadow: var(--sombra-sm);
    }}

    /* ---- Métricas como tarjetas ---- */
    div[data-testid="stMetric"] {{
        background-color: white;
        border: 1px solid {BORDE};
        border-radius: 10px;
        padding: 0.9rem 1.1rem;
        box-shadow: var(--sombra-sm);
        transition: transform 0.12s ease, box-shadow 0.12s ease;
    }}
    div[data-testid="stMetric"]:hover {{
        transform: translateY(-2px);
        box-shadow: var(--sombra-md);
    }}

    div[data-testid="stMetricValue"] {{
        font-family: 'Montserrat', sans-serif;
        font-weight: 900;
        color: {CARMESI};
    }}

    div[data-testid="stMetricLabel"] {{
        font-family: 'Source Sans 3', sans-serif;
        color: {PIZARRA};
        font-weight: 600;
    }}

    /* ---- Tabs ---- */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        border-bottom: 1px solid {BORDE};
    }}

    .stTabs [data-baseweb="tab"] {{
        background-color: white;
        border: 1px solid {BORDE};
        border-bottom: none;
        border-radius: 8px 8px 0 0;
        font-family: 'Montserrat', sans-serif;
        font-weight: 600;
        color: {PIZARRA};
        transition: background-color 0.15s ease, color 0.15s ease;
    }}
    .stTabs [data-baseweb="tab"]:hover {{
        background-color: {ESTUCO_CLARO};
        color: {CARMESI};
    }}

    .stTabs [aria-selected="true"] {{
        background-color: {CARMESI} !important;
        color: white !important;
        border-color: {CARMESI};
    }}

    /* ---- Inputs / expanders ---- */
    div[data-testid="stExpander"] {{
        border: 1px solid {BORDE};
        border-radius: 10px;
        box-shadow: var(--sombra-sm);
        overflow: hidden;
        background-color: white;
    }}

    .stTextInput input:focus,
    .stNumberInput input:focus,
    .stTextArea textarea:focus {{
        border-color: {CARMESI} !important;
        box-shadow: 0 0 0 2px rgba(166, 33, 43, 0.15) !important;
    }}

    /* ---- Badges para el score y estado ---- */
    .badge {{
        display: inline-block;
        padding: 0.25rem 0.7rem;
        border-radius: 999px;
        font-size: 0.85rem;
        font-weight: 700;
        font-family: 'Montserrat', sans-serif;
        box-shadow: var(--sombra-sm);
    }}
    .badge-alto {{ background-color: {VERDE_RECUPERACION}; color: white; }}
    .badge-medio {{ background-color: {AMBAR_CAUTELA}; color: white; }}
    .badge-bajo {{ background-color: {CONCRETO}; color: white; }}

    /* Score grande para la tarjeta */
    .score-anillo {{
        display: inline-flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: 58px;
        height: 58px;
        border-radius: 50%;
        font-family: 'Montserrat', sans-serif;
        color: white;
        line-height: 1;
        box-shadow: var(--sombra-md);
    }}
    .score-anillo .num {{ font-size: 1.35rem; font-weight: 900; }}
    .score-anillo .lbl {{ font-size: 0.55rem; font-weight: 600; opacity: 0.85; letter-spacing: 0.05em; }}
    .score-alto {{ background: linear-gradient(135deg, {VERDE_RECUPERACION}, #246b4b); }}
    .score-medio {{ background: linear-gradient(135deg, {AMBAR_CAUTELA}, #b8830f); }}
    .score-bajo {{ background: linear-gradient(135deg, {CONCRETO}, #5f5f5f); }}

    /* Chip de urgencia para días al cierre */
    .chip {{
        display: inline-block;
        padding: 0.1rem 0.55rem;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 700;
        font-family: 'Montserrat', sans-serif;
    }}
    .chip-urgente {{ background: rgba(166,33,43,0.12); color: {CARMESI}; }}
    .chip-pronto {{ background: rgba(216,154,31,0.16); color: #9a6c0c; }}
    .chip-ok {{ background: rgba(46,125,91,0.14); color: {VERDE_RECUPERACION}; }}
    .chip-neutro {{ background: {ESTUCO}; color: {CONCRETO}; }}

    /* ---- Tarjeta de licitación ---- */
    .tarjeta-lic {{
        background-color: white;
        border: 1px solid {BORDE};
        border-left: 4px solid {CARMESI};
        padding: 1.1rem 1.3rem;
        margin-bottom: 0.8rem;
        border-radius: 10px;
        box-shadow: var(--sombra-sm);
        transition: transform 0.12s ease, box-shadow 0.12s ease, border-left-color 0.12s ease;
    }}
    .tarjeta-lic:hover {{
        transform: translateY(-2px);
        box-shadow: var(--sombra-lg);
        border-left-color: {AMBAR_CAUTELA};
    }}

    /* ---- Logo header ---- */
    .header-rch {{
        display: flex;
        align-items: center;
        gap: 0.8rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid {BORDE};
        margin-bottom: 1.2rem;
    }}

    .header-rch .isotipo {{
        width: 44px;
        height: 44px;
        background: linear-gradient(135deg, {CARMESI}, {CARMESI_OSCURO});
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-family: 'Montserrat', sans-serif;
        font-weight: 900;
        font-size: 1.2rem;
        box-shadow: var(--sombra-md);
    }}

    .header-rch .titulo {{
        font-family: 'Montserrat', sans-serif;
        font-weight: 900;
        font-size: 1.12rem;
        color: {NEGRO_PATRIMONIAL};
        line-height: 1.1;
    }}

    .header-rch .subtitulo {{
        font-family: 'Source Sans 3', sans-serif;
        font-style: italic;
        font-size: 0.78rem;
        color: {PIZARRA};
    }}

    /* ---- Adjudicadas ---- */
    /* Tarjeta cuando gana RCH: acento verde y fondo sutil */
    .tarjeta-lic.gano-rch {{
        border-left-color: {VERDE_RECUPERACION};
        background: linear-gradient(90deg, rgba(46,125,91,0.05), white 40%);
    }}
    .tarjeta-lic.gano-rch:hover {{
        border-left-color: {VERDE_RECUPERACION};
    }}

    .empresa-pill {{
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.15rem 0.6rem;
        border-radius: 999px;
        font-family: 'Montserrat', sans-serif;
        font-weight: 700;
        font-size: 0.82rem;
        background: {ESTUCO};
        color: {PIZARRA};
    }}
    .empresa-pill.es-rch {{
        background: rgba(46,125,91,0.15);
        color: {VERDE_RECUPERACION};
    }}

    /* Ranking de competencia */
    .rank-row {{
        display: flex;
        align-items: center;
        gap: 0.7rem;
        margin-bottom: 0.55rem;
    }}
    .rank-pos {{
        flex: 0 0 22px;
        font-family: 'Montserrat', sans-serif;
        font-weight: 900;
        font-size: 0.95rem;
        color: {CONCRETO};
        text-align: center;
    }}
    .rank-body {{ flex: 1; min-width: 0; }}
    .rank-head {{
        display: flex;
        justify-content: space-between;
        gap: 0.5rem;
        font-size: 0.88rem;
        margin-bottom: 0.2rem;
    }}
    .rank-name {{
        font-weight: 600;
        color: {NEGRO_PATRIMONIAL};
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}
    .rank-name.es-rch {{ color: {VERDE_RECUPERACION}; font-weight: 700; }}
    .rank-val {{ color: {PIZARRA}; font-weight: 700; font-family: 'Montserrat', sans-serif; }}
    .rank-track {{
        height: 8px;
        background: {ESTUCO};
        border-radius: 999px;
        overflow: hidden;
    }}
    .rank-fill {{
        height: 100%;
        border-radius: 999px;
        background: linear-gradient(90deg, {CARMESI}, {AMBAR_CAUTELA});
    }}
    .rank-fill.es-rch {{
        background: linear-gradient(90deg, {VERDE_RECUPERACION}, #4fb083);
    }}

    /* Tabla de oferentes en la ficha */
    .oferente-row {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 0.8rem;
        padding: 0.5rem 0.8rem;
        border: 1px solid {BORDE};
        border-radius: 8px;
        margin-bottom: 0.4rem;
        background: white;
        font-size: 0.9rem;
    }}
    .oferente-row.ganador {{
        border-color: {VERDE_RECUPERACION};
        background: rgba(46,125,91,0.06);
        font-weight: 600;
    }}
    .oferente-row.es-rch:not(.ganador) {{
        border-color: {AMBAR_CAUTELA};
        background: rgba(216,154,31,0.06);
    }}

    .stAlert {{
        border-radius: 8px;
    }}

    /* Reducir padding superior */
    .block-container {{
        padding-top: 2rem;
        max-width: 1200px;
    }}

    footer {{
        font-family: 'Source Sans 3', sans-serif;
        font-style: italic;
        color: {CONCRETO};
        text-align: center;
        padding-top: 2rem;
        border-top: 1px solid {BORDE};
        margin-top: 3rem;
        font-size: 0.85rem;
    }}
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)


# ============================================================================
# Estado de sesión
# ============================================================================

if "ticket" not in st.session_state:
    st.session_state.ticket = ""
if "claude_api_key" not in st.session_state:
    st.session_state.claude_api_key = ""
if "modo_demo" not in st.session_state:
    st.session_state.modo_demo = True
if "licitaciones_cache" not in st.session_state:
    st.session_state.licitaciones_cache = []


# ============================================================================
# Componentes auxiliares
# ============================================================================

def formato_clp(monto: float | int | None) -> str:
    if not monto:
        return "—"
    return f"${monto:,.0f}".replace(",", ".")


def formato_clp_compacto(monto: float | int | None) -> str:
    """Monto abreviado para KPIs, en notación chilena de millones (MM$).

    Ej.: 6_913_200_000 -> "MM$ 6.913". Evita que las métricas se trunquen.
    """
    if not monto:
        return "—"
    if monto >= 1_000_000:
        millones = monto / 1_000_000
        return f"MM$ {millones:,.0f}".replace(",", ".")
    return formato_clp(monto)


def badge_score(score: float) -> str:
    if score >= 70:
        clase = "badge-alto"
    elif score >= 45:
        clase = "badge-medio"
    else:
        clase = "badge-bajo"
    return f'<span class="badge {clase}">{score}</span>'


def score_anillo(score: float) -> str:
    """Anillo circular con el score, coloreado según el nivel de pertinencia."""
    if score >= 70:
        clase = "score-alto"
    elif score >= 45:
        clase = "score-medio"
    else:
        clase = "score-bajo"
    return (
        f'<div class="score-anillo {clase}">'
        f'<span class="num">{int(round(score))}</span>'
        f'<span class="lbl">SCORE</span>'
        f'</div>'
    )


def chip_cierre(dias: int | None) -> str:
    """Chip con la urgencia del cierre según los días restantes."""
    if dias is None:
        return '<span class="chip chip-neutro">Sin fecha de cierre</span>'
    if dias < 0:
        return '<span class="chip chip-neutro">Cerrada</span>'
    if dias <= 3:
        clase = "chip-urgente"
    elif dias <= 10:
        clase = "chip-pronto"
    else:
        clase = "chip-ok"
    etiqueta = "Cierra hoy" if dias == 0 else f"Cierra en {dias} día{'s' if dias != 1 else ''}"
    return f'<span class="chip {clase}">{etiqueta}</span>'


def dias_para_cierre(fecha_str: str) -> int | None:
    if not fecha_str:
        return None
    try:
        fecha = datetime.fromisoformat(fecha_str.replace("Z", ""))
        return (fecha - datetime.now()).days
    except (ValueError, TypeError):
        return None


def header_rch() -> None:
    st.markdown(
        f"""
        <div class="header-rch">
            <div class="isotipo">R</div>
            <div>
                <div class="titulo">RCH · Análisis de Licitaciones</div>
                <div class="subtitulo">Construcción & Restauración Patrimonial</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================================
# Sidebar
# ============================================================================

def render_sidebar() -> str:
    with st.sidebar:
        st.markdown(
            f"""
            <div style='text-align:center; padding: 1rem 0;'>
                <div style='display:inline-flex; align-items:center; gap:0.6rem;'>
                    <div style='width:36px; height:36px; background-color:{CARMESI};
                                border-radius:50%; display:flex; align-items:center;
                                justify-content:center; color:white;
                                font-family:Montserrat; font-weight:900;'>R</div>
                    <div style='font-family:Montserrat; font-weight:900;
                                font-size:1.2rem; color:{NEGRO_PATRIMONIAL};'>RCH</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")

        pagina = st.radio(
            "Navegación",
            [
                "🔍 Explorar Licitaciones",
                "🏆 Adjudicadas",
                "📋 Pipeline",
                "🤖 Análisis con IA",
                "📊 Dashboard",
                "⚙️ Configuración",
            ],
            label_visibility="collapsed",
        )

        st.markdown("---")
        st.markdown("**Credenciales**")

        modo_demo = st.toggle(
            "Modo demostración",
            value=st.session_state.modo_demo,
            help="Usa datos ficticios. Desactívalo para conectar a Mercado Público.",
        )
        st.session_state.modo_demo = modo_demo

        if not modo_demo:
            ticket = st.text_input(
                "Ticket Mercado Público",
                value=st.session_state.ticket,
                type="password",
                help="Solicítalo en mercadopublico.cl → Mis tickets",
            )
            st.session_state.ticket = ticket

        api_key = st.text_input(
            "API key de Claude (opcional)",
            value=st.session_state.claude_api_key,
            type="password",
            help="Para análisis automático de bases PDF. console.anthropic.com",
        )
        st.session_state.claude_api_key = api_key

        st.markdown("---")
        st.caption(
            f"<i style='color:{CONCRETO}; font-size:0.75rem;'>"
            "v0.1 · MVP RCH"
            "</i>",
            unsafe_allow_html=True,
        )

    return pagina


# ============================================================================
# Página 1: Explorar licitaciones
# ============================================================================

def pagina_explorar() -> None:
    header_rch()
    st.markdown("# Explorar licitaciones")
    st.markdown(
        f"<p style='color:{PIZARRA};'>Busca y filtra licitaciones publicadas. "
        "Las que te interesen agrégalas al pipeline para hacerles seguimiento.</p>",
        unsafe_allow_html=True,
    )

    config = ds.cargar_configuracion()

    # Filtros
    with st.expander("🎛️ Filtros", expanded=True):
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            palabras_input = st.text_input(
                "Palabras clave (separadas por coma)",
                value=", ".join(config.get("palabras_clave", [])[:4]),
            )
            palabras = [p.strip() for p in palabras_input.split(",") if p.strip()]

        with col2:
            monto_min = st.number_input(
                "Monto mínimo (CLP)",
                min_value=0,
                value=config.get("monto_minimo_clp", 100_000_000),
                step=50_000_000,
                format="%d",
            )

        with col3:
            monto_max = st.number_input(
                "Monto máximo (CLP)",
                min_value=0,
                value=config.get("monto_maximo_clp", 5_000_000_000),
                step=100_000_000,
                format="%d",
            )

        col4, col5 = st.columns([2, 1])
        with col4:
            regiones = st.multiselect(
                "Regiones de interés",
                options=[
                    "XV Región de Arica y Parinacota",
                    "I Región de Tarapacá",
                    "II Región de Antofagasta",
                    "III Región de Atacama",
                    "IV Región de Coquimbo",
                    "V Región de Valparaíso",
                    "Región Metropolitana",
                    "VI Región del Libertador",
                    "VII Región del Maule",
                    "Región de Ñuble",
                    "VIII Región del Biobío",
                    "IX Región de La Araucanía",
                    "XIV Región de Los Ríos",
                    "X Región de Los Lagos",
                    "XI Región de Aysén",
                    "XII Región de Magallanes",
                ],
                default=config.get("regiones_interes", []),
            )

        with col5:
            fecha_consulta = st.date_input(
                "Fecha de publicación",
                value=date.today(),
                help="Solo aplica al consultar Mercado Público en vivo.",
            )

    # Cargar licitaciones
    if st.button("🔎 Buscar licitaciones", type="primary"):
        with st.spinner("Consultando licitaciones..."):
            if st.session_state.modo_demo:
                licitaciones = demo_data.licitaciones_demo()
            else:
                if not st.session_state.ticket:
                    st.error(
                        "Falta el ticket de Mercado Público. "
                        "Actívalo en la barra lateral o vuelve al modo demostración."
                    )
                    return
                try:
                    licitaciones = mp.listar_licitaciones_por_fecha(
                        fecha_consulta, st.session_state.ticket
                    )
                except mp.MercadoPublicoError as exc:
                    st.error(f"Error al consultar Mercado Público: {exc}")
                    return

            # Aplicar filtros locales
            if palabras:
                licitaciones = mp.buscar_por_palabras_clave(licitaciones, palabras)

            licitaciones = [
                lic
                for lic in licitaciones
                if monto_min <= (lic.get("MontoEstimado") or 0) <= monto_max
            ]

            if regiones:
                licitaciones = [
                    lic for lic in licitaciones if lic.get("Region") in regiones
                ]

            st.session_state.licitaciones_cache = licitaciones

    licitaciones = st.session_state.licitaciones_cache

    if not licitaciones:
        st.info(
            "No hay licitaciones cargadas todavía. Ajusta los filtros y "
            "haz clic en *Buscar licitaciones*."
        )
        return

    st.markdown(f"### {len(licitaciones)} licitaciones encontradas")

    # Calcular score y ordenar
    config_actual = {
        "palabras_clave": palabras or config.get("palabras_clave", []),
        "monto_minimo_clp": monto_min,
        "monto_maximo_clp": monto_max,
        "regiones_interes": regiones or config.get("regiones_interes", []),
    }

    licitaciones_con_score = []
    for lic in licitaciones:
        score = scoring.calcular_score(lic, config_actual)
        licitaciones_con_score.append((lic, score))

    licitaciones_con_score.sort(key=lambda x: x[1]["total"], reverse=True)

    # Listar
    pipeline_codigos = {
        lic.get("CodigoExterno") for lic in ds.cargar_pipeline()
    }

    for idx, (lic, score) in enumerate(licitaciones_con_score):
        codigo = lic.get("CodigoExterno", "")
        nombre = lic.get("Nombre", "Sin nombre")
        organismo = lic.get("NombreOrganismo", "—")
        region = lic.get("Region", "—")
        monto = lic.get("MontoEstimado", 0)
        cierre = lic.get("FechaCierre", "")
        dias_cierre = dias_para_cierre(cierre)
        en_pipeline = codigo in pipeline_codigos

        with st.container():
            col1, col2 = st.columns([5, 1])

            with col1:
                st.markdown(
                    f"""
                    <div class="tarjeta-lic">
                        <div style="display:flex; justify-content:space-between;
                                    align-items:flex-start; gap:1rem;">
                            <div style="flex:1;">
                                <div style="font-family:Montserrat; font-weight:700;
                                            font-size:1.05rem; color:{NEGRO_PATRIMONIAL};">
                                    {nombre}
                                </div>
                                <div style="color:{PIZARRA}; font-size:0.9rem;
                                            margin-top:0.35rem;">
                                    <b>{organismo}</b> · {region}
                                </div>
                                <div style="display:flex; align-items:center; flex-wrap:wrap;
                                            gap:0.5rem; margin-top:0.6rem;">
                                    {chip_cierre(dias_cierre)}
                                    <span style="color:{NEGRO_PATRIMONIAL}; font-size:0.9rem;
                                                 font-weight:600;">{formato_clp(monto)}</span>
                                    <span style="color:{CONCRETO}; font-size:0.8rem;">
                                        Código <code>{codigo}</code></span>
                                </div>
                            </div>
                            <div style="text-align:right;">
                                {score_anillo(score['total'])}
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with col2:
                key_detalle = f"detalle_{codigo}_{idx}"
                key_agregar = f"agregar_{codigo}_{idx}"

                if st.button("Ver detalle", key=key_detalle, use_container_width=True):
                    st.session_state["licitacion_detalle"] = lic
                    st.session_state["score_detalle"] = score

                if en_pipeline:
                    st.markdown(
                        f"<div style='text-align:center; color:{VERDE_RECUPERACION}; "
                        "font-weight:600; font-size:0.85rem; padding-top:0.4rem;'>"
                        "✓ En pipeline</div>",
                        unsafe_allow_html=True,
                    )
                else:
                    if st.button(
                        "+ Pipeline", key=key_agregar, use_container_width=True
                    ):
                        ds.agregar_a_pipeline(lic)
                        ds.actualizar_campo(
                            codigo, "score", score
                        )
                        st.success(f"Agregada {codigo} al pipeline.")
                        st.rerun()

    # Detalle expandible
    if "licitacion_detalle" in st.session_state:
        st.markdown("---")
        mostrar_detalle_licitacion(
            st.session_state["licitacion_detalle"],
            st.session_state.get("score_detalle"),
        )


def mostrar_detalle_licitacion(lic: dict[str, Any], score: dict[str, Any] | None) -> None:
    codigo = lic.get("CodigoExterno", "")
    st.markdown(f"## Detalle · {codigo}")

    if st.session_state.modo_demo:
        detalle_completo = demo_data.detalle_demo(codigo)
    else:
        try:
            detalle_completo = mp.detalle_licitacion(codigo, st.session_state.ticket)
        except mp.MercadoPublicoError as exc:
            st.warning(f"No se pudo obtener detalle ampliado: {exc}")
            detalle_completo = lic

    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown(f"**{detalle_completo.get('Nombre', '')}**")
        st.markdown(
            f"<div style='color:{PIZARRA};'>{detalle_completo.get('Descripcion', '')}</div>",
            unsafe_allow_html=True,
        )

        st.markdown("### Información clave")
        info_items = {
            "Organismo": detalle_completo.get("NombreOrganismo", "—"),
            "Región": detalle_completo.get("Region", "—"),
            "Monto referencial": formato_clp(detalle_completo.get("MontoEstimado", 0)),
            "Tipo de licitación": detalle_completo.get("TipoLicitacion", "—"),
            "Fecha publicación": detalle_completo.get("FechaPublicacion", "—")[:10],
            "Fecha cierre": detalle_completo.get("FechaCierre", "—")[:10],
        }
        for k, v in info_items.items():
            st.markdown(f"- **{k}:** {v}")

        if "CriteriosEvaluacion" in detalle_completo:
            st.markdown("### Criterios de evaluación")
            df_criterios = pd.DataFrame(detalle_completo["CriteriosEvaluacion"])
            st.dataframe(df_criterios, use_container_width=True, hide_index=True)

        if "EquipoProfesionalMinimo" in detalle_completo:
            st.markdown("### Equipo profesional mínimo")
            for prof in detalle_completo["EquipoProfesionalMinimo"]:
                st.markdown(f"- {prof}")

        if "GarantiaSeriedad" in detalle_completo:
            st.markdown("### Garantías")
            gs = detalle_completo["GarantiaSeriedad"]
            gfc = detalle_completo.get("GarantiaFielCumplimiento", {})
            st.markdown(
                f"- **Seriedad de la oferta:** {gs.get('Tipo', '')} · "
                f"Monto {formato_clp(gs.get('Monto', 0))} · "
                f"Vigencia {gs.get('Vigencia', '')}"
            )
            st.markdown(
                f"- **Fiel cumplimiento:** {gfc.get('Porcentaje', '')} · "
                f"Vigencia {gfc.get('Vigencia', '')}"
            )

        if "UrlMercadoPublico" in detalle_completo:
            st.markdown(
                f"[Ver en Mercado Público ↗]({detalle_completo['UrlMercadoPublico']})"
            )

    with col2:
        if score:
            st.markdown("### Score RCH")
            st.markdown(
                badge_score(score["total"]) + f" / 100", unsafe_allow_html=True
            )
            st.caption(score["recomendacion"])
            st.markdown("**Desglose**")
            for dim, valor in score["desglose"].items():
                st.markdown(f"- {dim.replace('_', ' ').title()}: **{valor}**")

        st.markdown("---")
        if st.button("✕ Cerrar detalle", use_container_width=True):
            st.session_state.pop("licitacion_detalle", None)
            st.session_state.pop("score_detalle", None)
            st.rerun()


# ============================================================================
# Página 2: Pipeline
# ============================================================================

def pagina_pipeline() -> None:
    header_rch()
    st.markdown("# Pipeline de licitaciones")
    st.markdown(
        f"<p style='color:{PIZARRA};'>Seguimiento de las licitaciones que estás "
        "evaluando o preparando.</p>",
        unsafe_allow_html=True,
    )

    pipeline = ds.cargar_pipeline()

    if not pipeline:
        st.info(
            "Tu pipeline está vacío. Ve a *Explorar Licitaciones* y agrega "
            "las que te interesen."
        )
        return

    # Métricas por estado
    estados_count = {est: 0 for est in ds.ESTADOS_PIPELINE}
    monto_total = 0
    for lic in pipeline:
        estado = lic.get("estado_pipeline", "descubierta")
        estados_count[estado] = estados_count.get(estado, 0) + 1
        if estado in ("evaluada", "en_preparacion", "presentada"):
            monto_total += lic.get("MontoEstimado", 0) or 0

    cols = st.columns(5)
    cols[0].metric("Total", len(pipeline))
    cols[1].metric("Por evaluar", estados_count.get("descubierta", 0))
    cols[2].metric("En preparación", estados_count.get("en_preparacion", 0))
    cols[3].metric("Presentadas", estados_count.get("presentada", 0))
    cols[4].metric("Adjudicadas", estados_count.get("adjudicada", 0))

    st.markdown(
        f"<p style='color:{PIZARRA};'>Monto en gestión activa: "
        f"<b>{formato_clp(monto_total)}</b></p>",
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # Filtro por estado
    estado_filtro = st.selectbox(
        "Filtrar por estado",
        ["Todos"] + ds.ESTADOS_PIPELINE,
    )

    pipeline_filtrado = [
        lic
        for lic in pipeline
        if estado_filtro == "Todos" or lic.get("estado_pipeline") == estado_filtro
    ]

    pipeline_filtrado.sort(
        key=lambda lic: (lic.get("score") or {}).get("total", 0), reverse=True
    )

    for lic in pipeline_filtrado:
        codigo = lic.get("CodigoExterno", "")
        score = lic.get("score") or {}
        score_total = score.get("total", "—")

        with st.expander(
            f"{codigo} · {lic.get('Nombre', '')[:80]}  "
            f"(Score: {score_total} · Estado: {lic.get('estado_pipeline', '—')})"
        ):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"**{lic.get('NombreOrganismo', '—')}** · {lic.get('Region', '—')}")
                st.markdown(f"Monto referencial: **{formato_clp(lic.get('MontoEstimado', 0))}**")
                st.markdown(f"Cierre: **{lic.get('FechaCierre', '—')[:10]}**")

                notas_actuales = lic.get("notas_internas", "")
                notas_nuevas = st.text_area(
                    "Notas internas",
                    value=notas_actuales,
                    key=f"notas_{codigo}",
                    height=80,
                )
                if notas_nuevas != notas_actuales:
                    if st.button("💾 Guardar notas", key=f"guardar_{codigo}"):
                        ds.actualizar_campo(codigo, "notas_internas", notas_nuevas)
                        st.success("Notas guardadas.")
                        st.rerun()

            with col2:
                nuevo_estado = st.selectbox(
                    "Cambiar estado",
                    ds.ESTADOS_PIPELINE,
                    index=ds.ESTADOS_PIPELINE.index(
                        lic.get("estado_pipeline", "descubierta")
                    ),
                    key=f"estado_{codigo}",
                )
                if nuevo_estado != lic.get("estado_pipeline"):
                    if st.button("Actualizar", key=f"upd_{codigo}", use_container_width=True):
                        ds.actualizar_estado(codigo, nuevo_estado)
                        st.success(f"Estado actualizado a {nuevo_estado}.")
                        st.rerun()

                if st.button("🗑️ Eliminar", key=f"del_{codigo}", use_container_width=True):
                    ds.eliminar_de_pipeline(codigo)
                    st.rerun()


# ============================================================================
# Página 3: Análisis con IA
# ============================================================================

def pagina_analisis_ia() -> None:
    header_rch()
    st.markdown("# Análisis con IA")
    st.markdown(
        f"<p style='color:{PIZARRA};'>Sube el PDF de las bases de una licitación "
        "y Claude las analiza automáticamente: presupuesto, criterios, equipo "
        "exigido, garantías, riesgos y recomendación de presentación.</p>",
        unsafe_allow_html=True,
    )

    pipeline = ds.cargar_pipeline()
    codigos_pipeline = [lic.get("CodigoExterno", "") for lic in pipeline]

    col1, col2 = st.columns([2, 1])

    with col1:
        codigo_lic = st.selectbox(
            "Asociar análisis a licitación del pipeline (opcional)",
            ["— Ninguna —"] + codigos_pipeline,
        )

        archivo_pdf = st.file_uploader(
            "PDF de bases de licitación",
            type=["pdf"],
            accept_multiple_files=False,
        )

    with col2:
        st.markdown("### Modo")
        usar_demo = st.toggle(
            "Análisis demostrativo",
            value=not bool(st.session_state.claude_api_key),
            help="Muestra un análisis simulado sin llamar a la API de Claude.",
        )

    if st.button("🤖 Analizar bases", type="primary"):
        if usar_demo:
            with st.spinner("Generando análisis demostrativo..."):
                resultado = analisis_ia.analisis_demo()
                st.session_state["ultimo_analisis"] = resultado
        else:
            if not archivo_pdf:
                st.error("Sube un PDF para analizar.")
                return
            if not st.session_state.claude_api_key:
                st.error(
                    "Falta la API key de Claude. Configúrala en la barra lateral."
                )
                return

            with st.spinner("Analizando bases con Claude..."):
                try:
                    resultado = analisis_ia.analizar_bases_pdf(
                        archivo_pdf.read(),
                        st.session_state.claude_api_key,
                    )
                    st.session_state["ultimo_analisis"] = resultado

                    if codigo_lic != "— Ninguna —":
                        ds.actualizar_campo(codigo_lic, "analisis_ia", resultado)
                        st.success(f"Análisis guardado en el pipeline para {codigo_lic}.")
                except analisis_ia.AnalisisIAError as exc:
                    st.error(f"Error en el análisis: {exc}")
                    return

    if "ultimo_analisis" in st.session_state:
        st.markdown("---")
        mostrar_analisis(st.session_state["ultimo_analisis"])


def mostrar_analisis(analisis: dict[str, Any]) -> None:
    st.markdown("## Resultado del análisis")

    # Resumen ejecutivo
    st.markdown("### Resumen ejecutivo")
    st.info(analisis.get("resumen_ejecutivo", "—"))

    # Recomendación
    rec = analisis.get("recomendacion", "evaluar").lower()
    color_rec = {
        "presentarse": VERDE_RECUPERACION,
        "evaluar": AMBAR_CAUTELA,
        "no presentarse": CARMESI,
    }.get(rec, PIZARRA)

    st.markdown(
        f"""
        <div style="padding: 1rem; background-color:{ESTUCO};
                    border-left: 4px solid {color_rec}; border-radius: 4px;">
            <div style="font-family:Montserrat; font-weight:900;
                        color:{color_rec}; text-transform:uppercase;">
                Recomendación: {rec}
            </div>
            <div style="margin-top:0.4rem; color:{PIZARRA};">
                {analisis.get("justificacion_recomendacion", "")}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Tabs con secciones
    tabs = st.tabs(
        ["📋 Generales", "💰 Económicas", "👥 Equipo", "⚠️ Riesgos", "📑 JSON"]
    )

    with tabs[0]:
        st.markdown(f"**Objeto:** {analisis.get('objeto_contratacion', '—')}")
        plazo = analisis.get("plazo_ejecucion", {})
        st.markdown(f"**Duración:** {plazo.get('duracion', '—')}")
        st.markdown(f"**Inicio estimado:** {plazo.get('fecha_inicio_estimada', '—')}")
        if plazo.get("hitos_relevantes"):
            st.markdown("**Hitos:**")
            for h in plazo["hitos_relevantes"]:
                st.markdown(f"- {h}")

    with tabs[1]:
        presup = analisis.get("presupuesto_referencial", {})
        monto = presup.get("monto_clp")
        st.metric(
            "Presupuesto referencial",
            formato_clp(monto) if monto else "No especificado",
        )
        st.caption(presup.get("comentarios", ""))

        st.markdown("**Criterios de evaluación**")
        criterios = analisis.get("criterios_evaluacion", [])
        if criterios:
            df_c = pd.DataFrame(criterios)
            st.dataframe(df_c, use_container_width=True, hide_index=True)

        st.markdown("**Garantías**")
        g = analisis.get("garantias", {})
        st.markdown(f"- Seriedad: {g.get('seriedad_oferta', '—')}")
        st.markdown(f"- Fiel cumplimiento: {g.get('fiel_cumplimiento', '—')}")
        st.markdown(f"- Anticipo: {g.get('anticipo', '—')}")

        st.markdown(f"**Estructura de pagos:** {analisis.get('estructura_pagos', '—')}")
        st.markdown(f"**Multas:** {analisis.get('multas_y_sanciones', '—')}")

    with tabs[2]:
        equipo = analisis.get("equipo_profesional_minimo", [])
        if equipo:
            df_e = pd.DataFrame(equipo)
            st.dataframe(df_e, use_container_width=True, hide_index=True)
        st.markdown(f"**Experiencia requerida al oferente:** {analisis.get('experiencia_oferente', '—')}")

    with tabs[3]:
        riesgos = analisis.get("riesgos_identificados", [])
        for r in riesgos:
            nivel = r.get("nivel", "medio").lower()
            color_nivel = {
                "alto": CARMESI,
                "medio": AMBAR_CAUTELA,
                "bajo": CONCRETO,
            }.get(nivel, CONCRETO)
            st.markdown(
                f"""
                <div style="border-left: 3px solid {color_nivel};
                            padding: 0.6rem 1rem; margin-bottom:0.5rem;
                            background-color:#fafafa;">
                    <b style='color:{color_nivel};'>{nivel.upper()}</b> — {r.get('riesgo', '')}
                    <br><i style='color:{PIZARRA};'>Mitigación: {r.get('mitigacion', '')}</i>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("---")
        st.markdown("**Fortalezas para RCH**")
        st.success(analisis.get("fortalezas_para_rch", "—"))
        st.markdown("**Debilidades / brechas**")
        st.warning(analisis.get("debilidades_para_rch", "—"))

    with tabs[4]:
        st.code(json.dumps(analisis, ensure_ascii=False, indent=2), language="json")


# ============================================================================
# Página 4: Dashboard
# ============================================================================

def pagina_dashboard() -> None:
    header_rch()
    st.markdown("# Dashboard")

    pipeline = ds.cargar_pipeline()

    if not pipeline:
        st.info("Aún no hay datos en el pipeline para mostrar.")
        return

    # KPIs
    total = len(pipeline)
    monto_total = sum(lic.get("MontoEstimado", 0) or 0 for lic in pipeline)
    presentadas = sum(
        1 for lic in pipeline if lic.get("estado_pipeline") == "presentada"
    )
    adjudicadas = sum(
        1 for lic in pipeline if lic.get("estado_pipeline") == "adjudicada"
    )
    tasa_adjudicacion = (
        (adjudicadas / presentadas * 100) if presentadas > 0 else 0
    )

    cols = st.columns(4)
    cols[0].metric("Licitaciones en pipeline", total)
    cols[1].metric("Monto total agregado", formato_clp_compacto(monto_total))
    cols[2].metric("Presentadas", presentadas)
    cols[3].metric("Tasa adjudicación", f"{tasa_adjudicacion:.1f}%")

    st.markdown("---")

    # Distribución por estado
    df = pd.DataFrame(pipeline)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Por estado")
        if "estado_pipeline" in df.columns:
            estado_counts = df["estado_pipeline"].value_counts()
            st.bar_chart(estado_counts)

    with col2:
        st.markdown("### Por región")
        if "Region" in df.columns:
            region_counts = df["Region"].value_counts().head(8)
            st.bar_chart(region_counts)

    # Distribución de scores
    st.markdown("### Distribución de scores")
    scores = [
        (lic.get("score") or {}).get("total", 0)
        for lic in pipeline
        if lic.get("score")
    ]
    if scores:
        df_scores = pd.DataFrame({"score": scores})
        st.bar_chart(df_scores["score"].value_counts(bins=10).sort_index())

    # Tabla resumen
    st.markdown("### Licitaciones próximas a cerrar")
    proximos = []
    for lic in pipeline:
        dias = dias_para_cierre(lic.get("FechaCierre", ""))
        if dias is not None and 0 <= dias <= 30:
            proximos.append(
                {
                    "Código": lic.get("CodigoExterno", ""),
                    "Nombre": lic.get("Nombre", "")[:60],
                    "Monto": formato_clp(lic.get("MontoEstimado", 0)),
                    "Días al cierre": dias,
                    "Estado": lic.get("estado_pipeline", "—"),
                }
            )
    proximos.sort(key=lambda x: x["Días al cierre"])
    if proximos:
        st.dataframe(pd.DataFrame(proximos), use_container_width=True, hide_index=True)
    else:
        st.caption("Ninguna licitación del pipeline cierra en los próximos 30 días.")


# ============================================================================
# Página 5: Configuración
# ============================================================================

def pagina_configuracion() -> None:
    header_rch()
    st.markdown("# Configuración")
    st.markdown(
        f"<p style='color:{PIZARRA};'>Personaliza los criterios que el sistema "
        "usa para calcular el score de pertinencia.</p>",
        unsafe_allow_html=True,
    )

    config = ds.cargar_configuracion()

    with st.form("form_config"):
        palabras = st.text_area(
            "Palabras clave (una por línea)",
            value="\n".join(config.get("palabras_clave", [])),
            height=160,
        )

        col1, col2 = st.columns(2)
        with col1:
            monto_min = st.number_input(
                "Monto mínimo (CLP)",
                min_value=0,
                value=config.get("monto_minimo_clp", 100_000_000),
                step=50_000_000,
            )
        with col2:
            monto_max = st.number_input(
                "Monto máximo (CLP)",
                min_value=0,
                value=config.get("monto_maximo_clp", 5_000_000_000),
                step=100_000_000,
            )

        regiones = st.multiselect(
            "Regiones de interés",
            options=[
                "XV Región de Arica y Parinacota",
                "I Región de Tarapacá",
                "II Región de Antofagasta",
                "III Región de Atacama",
                "IV Región de Coquimbo",
                "V Región de Valparaíso",
                "Región Metropolitana",
                "VI Región del Libertador",
                "VII Región del Maule",
                "Región de Ñuble",
                "VIII Región del Biobío",
                "IX Región de La Araucanía",
                "XIV Región de Los Ríos",
                "X Región de Los Lagos",
                "XI Región de Aysén",
                "XII Región de Magallanes",
            ],
            default=config.get("regiones_interes", []),
        )

        umbral = st.slider(
            "Umbral mínimo de score para recomendación automática",
            0, 100,
            value=config.get("umbral_score_recomendado", 70),
        )

        guardar = st.form_submit_button("💾 Guardar configuración")

    if guardar:
        nueva_config = {
            "palabras_clave": [
                p.strip() for p in palabras.split("\n") if p.strip()
            ],
            "monto_minimo_clp": int(monto_min),
            "monto_maximo_clp": int(monto_max),
            "regiones_interes": regiones,
            "umbral_score_recomendado": umbral,
        }
        ds.guardar_configuracion(nueva_config)
        st.success("Configuración guardada.")

    st.markdown("---")
    st.markdown("### Pesos del score (informativo)")
    st.markdown(
        "El score se calcula con esta ponderación. Para modificarla, "
        "edita `scoring.py`."
    )
    df_pesos = pd.DataFrame(
        [
            {"Dimensión": k.replace("_", " ").title(), "Peso (%)": v}
            for k, v in scoring.PESOS.items()
        ]
    )
    st.dataframe(df_pesos, use_container_width=True, hide_index=True)


# ============================================================================
# Página 6: Licitaciones adjudicadas (inteligencia competitiva)
# ============================================================================

def _es_rch(nombre: str) -> bool:
    return (nombre or "").strip().lower() == RCH_EMPRESA.lower()


def _ahorro_pct(referencial: float | int | None, adjudicado: float | int | None) -> float | None:
    """% de diferencia del monto adjudicado respecto al referencial.

    Positivo = se adjudicó por debajo del referencial (ahorro para el mandante).
    """
    if not referencial or not adjudicado:
        return None
    return (referencial - adjudicado) / referencial * 100


def chip_ahorro(pct: float | None) -> str:
    if pct is None:
        return '<span class="chip chip-neutro">Sin referencia</span>'
    if pct >= 0:
        return f'<span class="chip chip-ok">−{pct:.1f}% vs. referencial</span>'
    return f'<span class="chip chip-urgente">+{abs(pct):.1f}% sobre referencial</span>'


def ranking_competencia(adjudicadas: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Agrega adjudicaciones por empresa ganadora: nº de adjudicaciones y monto."""
    agg: dict[str, dict[str, Any]] = {}
    for lic in adjudicadas:
        adj = lic.get("Adjudicacion") or {}
        empresa = adj.get("EmpresaGanadora")
        if not empresa:
            continue
        registro = agg.setdefault(empresa, {"empresa": empresa, "ganadas": 0, "monto": 0})
        registro["ganadas"] += 1
        registro["monto"] += adj.get("MontoAdjudicado") or 0
    ranking = list(agg.values())
    ranking.sort(key=lambda r: (r["ganadas"], r["monto"]), reverse=True)
    return ranking


def pagina_adjudicadas() -> None:
    header_rch()
    st.markdown("# Licitaciones adjudicadas")
    st.markdown(
        f"<p style='color:{PIZARRA};'>Inteligencia competitiva: qué licitaciones "
        "cerraron, quién las ganó, a qué monto respecto al referencial y contra "
        "quiénes compitió RCH.</p>",
        unsafe_allow_html=True,
    )

    # Cargar adjudicadas (demo o API real)
    if st.session_state.modo_demo:
        adjudicadas = demo_data.adjudicadas_demo()
    else:
        if not st.session_state.ticket:
            st.error(
                "Falta el ticket de Mercado Público. Actívalo en la barra "
                "lateral o vuelve al modo demostración."
            )
            return
        try:
            adjudicadas = mp.listar_licitaciones_por_fecha(
                st.session_state.get("fecha_adj", date.today()),
                st.session_state.ticket,
                estado="adjudicadas",
            )
        except mp.MercadoPublicoError as exc:
            st.error(f"Error al consultar adjudicadas: {exc}")
            return
        if not adjudicadas:
            st.info("No se encontraron licitaciones adjudicadas para esa fecha.")
            return

    # ---- Franja de KPIs ----
    total = len(adjudicadas)
    monto_total = sum((lic.get("Adjudicacion") or {}).get("MontoAdjudicado", 0) or 0 for lic in adjudicadas)
    ganadas_rch = sum(
        1 for lic in adjudicadas if _es_rch((lic.get("Adjudicacion") or {}).get("EmpresaGanadora", ""))
    )
    ahorros = [
        p for lic in adjudicadas
        if (p := _ahorro_pct(lic.get("MontoEstimado"), (lic.get("Adjudicacion") or {}).get("MontoAdjudicado"))) is not None
    ]
    ahorro_prom = sum(ahorros) / len(ahorros) if ahorros else 0
    tasa_rch = (ganadas_rch / total * 100) if total else 0

    cols = st.columns(4)
    cols[0].metric("Adjudicadas", total)
    cols[1].metric("Monto adjudicado", formato_clp_compacto(monto_total))
    cols[2].metric("Ganadas por RCH", f"{ganadas_rch}", f"{tasa_rch:.0f}% del total")
    cols[3].metric("Baja promedio", f"{ahorro_prom:.1f}%", help="Monto adjudicado bajo el referencial, en promedio.")

    st.markdown("---")

    # ---- Ranking de competencia + participación de RCH ----
    col_rank, col_part = st.columns([3, 2])

    with col_rank:
        st.markdown("### Ranking de competencia")
        ranking = ranking_competencia(adjudicadas)
        max_monto = max((r["monto"] for r in ranking), default=1) or 1
        for i, r in enumerate(ranking, start=1):
            es_rch = _es_rch(r["empresa"])
            cls = "es-rch" if es_rch else ""
            pct_barra = r["monto"] / max_monto * 100
            st.markdown(
                f"""
                <div class="rank-row">
                    <div class="rank-pos">{i}</div>
                    <div class="rank-body">
                        <div class="rank-head">
                            <span class="rank-name {cls}">
                                {'★ ' if es_rch else ''}{r['empresa']}
                            </span>
                            <span class="rank-val">{r['ganadas']} · {formato_clp(r['monto'])}</span>
                        </div>
                        <div class="rank-track">
                            <div class="rank-fill {cls}" style="width:{pct_barra:.0f}%;"></div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with col_part:
        st.markdown("### Participación de RCH")
        participo = sum(
            1 for lic in adjudicadas
            if any(_es_rch(o.get("Empresa", "")) for o in (lic.get("Adjudicacion") or {}).get("Oferentes", []))
        )
        perdidas = participo - ganadas_rch
        st.markdown(
            f"<div style='color:{PIZARRA}; line-height:1.9;'>"
            f"Participó en <b>{participo}</b> de {total} adjudicadas<br>"
            f"<span style='color:{VERDE_RECUPERACION}; font-weight:700;'>● Ganadas: {ganadas_rch}</span><br>"
            f"<span style='color:{AMBAR_CAUTELA}; font-weight:700;'>● Segundo/otros: {perdidas}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )
        if participo:
            tasa_exito = ganadas_rch / participo * 100
            st.progress(min(int(tasa_exito), 100), text=f"Tasa de éxito: {tasa_exito:.0f}%")

    st.markdown("---")

    # ---- Filtros ----
    with st.expander("🎛️ Filtros", expanded=False):
        c1, c2, c3 = st.columns([2, 2, 1])
        with c1:
            palabras_adj = st.text_input("Buscar (nombre, organismo o empresa)", key="q_adj")
        with c2:
            empresas = sorted({(lic.get("Adjudicacion") or {}).get("EmpresaGanadora", "") for lic in adjudicadas} - {""})
            empresa_sel = st.selectbox("Empresa ganadora", ["Todas"] + empresas, key="emp_adj")
        with c3:
            solo_rch = st.toggle("Solo con RCH", key="solo_rch", help="Adjudicaciones donde RCH participó.")

    def _coincide(lic: dict[str, Any]) -> bool:
        adj = lic.get("Adjudicacion") or {}
        if empresa_sel != "Todas" and adj.get("EmpresaGanadora") != empresa_sel:
            return False
        if solo_rch and not any(_es_rch(o.get("Empresa", "")) for o in adj.get("Oferentes", [])):
            return False
        if palabras_adj:
            blob = " ".join([
                lic.get("Nombre", ""), lic.get("NombreOrganismo", ""),
                adj.get("EmpresaGanadora", ""),
            ]).lower()
            if palabras_adj.lower() not in blob:
                return False
        return True

    filtradas = [lic for lic in adjudicadas if _coincide(lic)]
    # Más recientes primero
    filtradas.sort(key=lambda l: l.get("FechaAdjudicacion", ""), reverse=True)

    st.markdown(f"### {len(filtradas)} adjudicaciones")

    for idx, lic in enumerate(filtradas):
        adj = lic.get("Adjudicacion") or {}
        codigo = lic.get("CodigoExterno", "")
        empresa = adj.get("EmpresaGanadora", "—")
        gano_rch = _es_rch(empresa)
        monto_adj = adj.get("MontoAdjudicado")
        pct = _ahorro_pct(lic.get("MontoEstimado"), monto_adj)
        n_oferentes = adj.get("NumeroOferentes", len(adj.get("Oferentes", [])))
        fecha_adj = (lic.get("FechaAdjudicacion", "") or "")[:10]

        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(
                f"""
                <div class="tarjeta-lic {'gano-rch' if gano_rch else ''}">
                    <div style="display:flex; justify-content:space-between;
                                align-items:flex-start; gap:1rem;">
                        <div style="flex:1;">
                            <div style="font-family:Montserrat; font-weight:700;
                                        font-size:1.05rem; color:{NEGRO_PATRIMONIAL};">
                                {lic.get('Nombre', 'Sin nombre')}
                            </div>
                            <div style="color:{PIZARRA}; font-size:0.9rem; margin-top:0.35rem;">
                                <b>{lic.get('NombreOrganismo', '—')}</b> · {lic.get('Region', '—')}
                            </div>
                            <div style="display:flex; align-items:center; flex-wrap:wrap;
                                        gap:0.5rem; margin-top:0.6rem;">
                                <span class="empresa-pill {'es-rch' if gano_rch else ''}">
                                    {'★' if gano_rch else '🏆'} {empresa}
                                </span>
                                {chip_ahorro(pct)}
                            </div>
                            <div style="color:{CONCRETO}; font-size:0.82rem; margin-top:0.5rem;">
                                Adjudicado <b style="color:{NEGRO_PATRIMONIAL};">{formato_clp(monto_adj)}</b>
                                · referencial {formato_clp(lic.get('MontoEstimado'))}
                                · {n_oferentes} oferentes
                                · {('adjudicada el ' + fecha_adj) if fecha_adj else 'fecha s/i'}
                            </div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col2:
            if st.button("Ver oferentes", key=f"adj_det_{codigo}_{idx}", use_container_width=True):
                st.session_state["adjudicada_detalle"] = lic

    if "adjudicada_detalle" in st.session_state:
        st.markdown("---")
        mostrar_detalle_adjudicada(st.session_state["adjudicada_detalle"])


def mostrar_detalle_adjudicada(lic: dict[str, Any]) -> None:
    adj = lic.get("Adjudicacion") or {}
    codigo = lic.get("CodigoExterno", "")
    st.markdown(f"## Comparativa de oferentes · {codigo}")
    st.markdown(f"**{lic.get('Nombre', '')}**")
    st.markdown(
        f"<div style='color:{PIZARRA};'>{lic.get('NombreOrganismo', '—')} · "
        f"{lic.get('Region', '—')} · Referencial {formato_clp(lic.get('MontoEstimado'))}</div>",
        unsafe_allow_html=True,
    )
    st.markdown("")

    oferentes = sorted(
        adj.get("Oferentes", []),
        key=lambda o: o.get("Monto", 0) or 0,
    )
    referencial = lic.get("MontoEstimado") or 0
    for pos, of in enumerate(oferentes, start=1):
        es_rch = _es_rch(of.get("Empresa", ""))
        es_ganador = of.get("Ganador", False)
        clases = "oferente-row"
        if es_ganador:
            clases += " ganador"
        if es_rch:
            clases += " es-rch"
        etiqueta = []
        if es_ganador:
            etiqueta.append(f"<span style='color:{VERDE_RECUPERACION}; font-weight:700;'>ADJUDICADO</span>")
        if es_rch and not es_ganador:
            etiqueta.append(f"<span style='color:{AMBAR_CAUTELA}; font-weight:700;'>RCH</span>")
        pct_ref = _ahorro_pct(referencial, of.get("Monto"))
        ref_txt = f"−{pct_ref:.1f}%" if pct_ref is not None and pct_ref >= 0 else (f"+{abs(pct_ref):.1f}%" if pct_ref is not None else "")
        st.markdown(
            f"""
            <div class="{clases}">
                <div><span style="color:{CONCRETO}; font-weight:700;">#{pos}</span>
                     &nbsp;{'★ ' if es_rch else ''}{of.get('Empresa', '—')}
                     &nbsp;{' · '.join(etiqueta)}</div>
                <div style="font-family:Montserrat; font-weight:700; color:{NEGRO_PATRIMONIAL};">
                    {formato_clp(of.get('Monto'))}
                    <span style="color:{CONCRETO}; font-weight:400; font-size:0.8rem;">{ref_txt}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Posición de RCH
    rch_of = next((o for o in oferentes if _es_rch(o.get("Empresa", ""))), None)
    if rch_of:
        pos_rch = oferentes.index(rch_of) + 1
        ganador_monto = next((o.get("Monto") for o in oferentes if o.get("Ganador")), None)
        if rch_of.get("Ganador"):
            st.success(f"RCH ganó esta licitación (posición 1 de {len(oferentes)}).")
        elif ganador_monto:
            brecha = (rch_of.get("Monto", 0) - ganador_monto) / ganador_monto * 100
            st.warning(
                f"RCH quedó en posición {pos_rch} de {len(oferentes)}. "
                f"Su oferta estuvo {brecha:.1f}% por sobre la ganadora "
                f"({formato_clp(rch_of.get('Monto', 0) - ganador_monto)} de diferencia)."
            )
    else:
        st.info("RCH no participó en esta licitación.")

    if st.button("✕ Cerrar comparativa", use_container_width=True):
        st.session_state.pop("adjudicada_detalle", None)
        st.rerun()


# ============================================================================
# Routing
# ============================================================================

def main() -> None:
    pagina = render_sidebar()

    if pagina.startswith("🔍"):
        pagina_explorar()
    elif pagina.startswith("🏆"):
        pagina_adjudicadas()
    elif pagina.startswith("📋"):
        pagina_pipeline()
    elif pagina.startswith("🤖"):
        pagina_analisis_ia()
    elif pagina.startswith("📊"):
        pagina_dashboard()
    elif pagina.startswith("⚙️"):
        pagina_configuracion()

    st.markdown(
        f"""
        <footer>
            RCH · Construcción & Restauración Patrimonial<br>
            Sistema de Análisis de Licitaciones · v0.1 MVP
        </footer>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
