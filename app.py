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
NEGRO_PATRIMONIAL = "#1A1A1A"
ESTUCO = "#EDEAE5"
PIZARRA = "#3D3D3D"
CONCRETO = "#7A7A7A"
VERDE_RECUPERACION = "#2E7D5B"
AMBAR_CAUTELA = "#D89A1F"


CSS = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700;900&family=Source+Sans+3:wght@400;600&display=swap');

    html, body, [class*="css"]  {{
        font-family: 'Source Sans 3', sans-serif;
        color: {NEGRO_PATRIMONIAL};
    }}

    h1, h2, h3, h4 {{
        font-family: 'Montserrat', sans-serif !important;
        color: {NEGRO_PATRIMONIAL};
        font-weight: 700 !important;
    }}

    h1 {{
        border-bottom: 2px solid {CARMESI};
        padding-bottom: 0.5rem;
        margin-bottom: 1.5rem;
    }}

    .stButton > button {{
        background-color: {CARMESI};
        color: white;
        border: none;
        font-family: 'Montserrat', sans-serif;
        font-weight: 600;
        border-radius: 4px;
        padding: 0.5rem 1rem;
        transition: background-color 0.2s;
    }}

    .stButton > button:hover {{
        background-color: #8a1c24;
        color: white;
    }}

    .stButton > button:focus {{
        background-color: {CARMESI};
        color: white;
        box-shadow: 0 0 0 2px rgba(166, 33, 43, 0.3);
    }}

    /* Secundario para botones tipo "Ver detalle" */
    .secundario .stButton > button {{
        background-color: white;
        color: {CARMESI};
        border: 1.5px solid {CARMESI};
    }}

    section[data-testid="stSidebar"] {{
        background-color: {ESTUCO};
        border-right: 1px solid #d4d0c8;
    }}

    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {{
        color: {NEGRO_PATRIMONIAL};
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

    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
    }}

    .stTabs [data-baseweb="tab"] {{
        background-color: white;
        border: 1px solid {ESTUCO};
        border-radius: 4px 4px 0 0;
        font-family: 'Montserrat', sans-serif;
        font-weight: 600;
        color: {PIZARRA};
    }}

    .stTabs [aria-selected="true"] {{
        background-color: {CARMESI} !important;
        color: white !important;
        border-color: {CARMESI};
    }}

    /* Badges para el score y estado */
    .badge {{
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
        font-family: 'Montserrat', sans-serif;
    }}
    .badge-alto {{ background-color: {VERDE_RECUPERACION}; color: white; }}
    .badge-medio {{ background-color: {AMBAR_CAUTELA}; color: white; }}
    .badge-bajo {{ background-color: {CONCRETO}; color: white; }}

    /* Tarjeta de licitación */
    .tarjeta-lic {{
        background-color: white;
        border-left: 4px solid {CARMESI};
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
        border-radius: 4px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }}

    /* Logo header */
    .header-rch {{
        display: flex;
        align-items: center;
        gap: 0.8rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid {ESTUCO};
        margin-bottom: 1rem;
    }}

    .header-rch .isotipo {{
        width: 42px;
        height: 42px;
        background-color: {CARMESI};
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-family: 'Montserrat', sans-serif;
        font-weight: 900;
        font-size: 1.2rem;
    }}

    .header-rch .titulo {{
        font-family: 'Montserrat', sans-serif;
        font-weight: 900;
        font-size: 1.1rem;
        color: {NEGRO_PATRIMONIAL};
        line-height: 1.1;
    }}

    .header-rch .subtitulo {{
        font-family: 'Source Sans 3', sans-serif;
        font-style: italic;
        font-size: 0.78rem;
        color: {PIZARRA};
    }}

    .stAlert {{
        border-radius: 4px;
    }}

    /* Reducir padding superior */
    .block-container {{
        padding-top: 2rem;
    }}

    footer {{
        font-family: 'Source Sans 3', sans-serif;
        font-style: italic;
        color: {CONCRETO};
        text-align: center;
        padding-top: 2rem;
        border-top: 1px solid {ESTUCO};
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


def badge_score(score: float) -> str:
    if score >= 70:
        clase = "badge-alto"
    elif score >= 45:
        clase = "badge-medio"
    else:
        clase = "badge-bajo"
    return f'<span class="badge {clase}">{score}</span>'


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
                                            margin-top:0.3rem;">
                                    <b>{organismo}</b> · {region}
                                </div>
                                <div style="color:{CONCRETO}; font-size:0.85rem;
                                            margin-top:0.4rem;">
                                    Código: <code>{codigo}</code> ·
                                    Monto referencial: <b>{formato_clp(monto)}</b> ·
                                    {f'Cierra en <b>{dias_cierre}</b> días' if dias_cierre is not None else 'Sin fecha de cierre'}
                                </div>
                            </div>
                            <div style="text-align:right;">
                                {badge_score(score['total'])}
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
    cols[1].metric("Monto total agregado", formato_clp(monto_total))
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
# Routing
# ============================================================================

def main() -> None:
    pagina = render_sidebar()

    if pagina.startswith("🔍"):
        pagina_explorar()
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
