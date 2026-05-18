"""
Análisis automático de bases de licitación con la API de Claude.

Extrae información estructurada relevante para la decisión de presentarse:
presupuesto referencial, criterios de evaluación, equipo profesional
mínimo, garantías, plazos, multas y riesgos identificados.
"""

from __future__ import annotations

import base64
import json
from typing import Any

try:
    import anthropic  # type: ignore
except ImportError:
    anthropic = None  # se valida en runtime


PROMPT_ANALISIS = """Eres un analista experto en licitaciones públicas chilenas del rubro \
construcción y restauración patrimonial. Tu trabajo es leer las bases técnicas y \
administrativas de una licitación y extraer la información clave para una empresa \
constructora que evalúa presentarse.

Devuelve EXCLUSIVAMENTE un JSON válido (sin texto adicional, sin bloques markdown) \
con esta estructura:

{
  "resumen_ejecutivo": "máximo 3 oraciones",
  "objeto_contratacion": "descripción del objeto",
  "presupuesto_referencial": {
    "monto_clp": número o null,
    "moneda": "CLP/UF/USD",
    "comentarios": "texto"
  },
  "plazo_ejecucion": {
    "duracion": "texto",
    "fecha_inicio_estimada": "texto",
    "hitos_relevantes": ["lista"]
  },
  "criterios_evaluacion": [
    {"criterio": "nombre", "ponderacion": número, "comentarios": "texto"}
  ],
  "equipo_profesional_minimo": [
    {"rol": "texto", "experiencia_requerida": "texto", "dedicacion": "texto"}
  ],
  "experiencia_oferente": "requisitos de experiencia exigidos a la empresa",
  "garantias": {
    "seriedad_oferta": "monto y vigencia",
    "fiel_cumplimiento": "porcentaje y vigencia",
    "anticipo": "si aplica"
  },
  "multas_y_sanciones": "resumen de las principales multas",
  "estructura_pagos": "cómo se realizan los pagos al contratista",
  "riesgos_identificados": [
    {"riesgo": "texto", "nivel": "alto/medio/bajo", "mitigacion": "texto"}
  ],
  "fortalezas_para_rch": "por qué RCH podría ganar esta licitación",
  "debilidades_para_rch": "qué le falta a RCH para esta licitación",
  "recomendacion": "presentarse / evaluar / no presentarse",
  "justificacion_recomendacion": "máximo 3 oraciones"
}

Si algún dato no aparece en las bases, usa null o el texto "No especificado".
NO inventes información. NO agregues texto fuera del JSON."""


class AnalisisIAError(Exception):
    """Error al analizar las bases con Claude."""


def cliente_anthropic_disponible() -> bool:
    return anthropic is not None


def analizar_bases_pdf(
    contenido_pdf: bytes,
    api_key: str,
    modelo: str = "claude-sonnet-4-5",
    nombre_archivo: str = "bases.pdf",
) -> dict[str, Any]:
    """Analiza un PDF de bases de licitación con Claude.

    Args:
        contenido_pdf: bytes del PDF.
        api_key: clave de la API de Anthropic.
        modelo: identificador del modelo a usar.
        nombre_archivo: nombre del archivo (para referencia).

    Returns:
        Dict con el análisis estructurado.

    Raises:
        AnalisisIAError: si falla la API o el JSON devuelto no es parseable.
    """
    if anthropic is None:
        raise AnalisisIAError(
            "La librería 'anthropic' no está instalada. "
            "Ejecuta: pip install anthropic"
        )

    if not api_key:
        raise AnalisisIAError("Falta la API key de Anthropic.")

    cliente = anthropic.Anthropic(api_key=api_key)

    pdf_b64 = base64.standard_b64encode(contenido_pdf).decode("utf-8")

    try:
        respuesta = cliente.messages.create(
            model=modelo,
            max_tokens=4096,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "document",
                            "source": {
                                "type": "base64",
                                "media_type": "application/pdf",
                                "data": pdf_b64,
                            },
                        },
                        {"type": "text", "text": PROMPT_ANALISIS},
                    ],
                }
            ],
        )
    except Exception as exc:  # noqa: BLE001
        raise AnalisisIAError(f"Error al llamar a la API de Claude: {exc}") from exc

    texto = ""
    for bloque in respuesta.content:
        if getattr(bloque, "type", None) == "text":
            texto += getattr(bloque, "text", "")

    texto = texto.strip()
    # Limpieza defensiva: quitar fences markdown si vienen
    if texto.startswith("```"):
        texto = texto.strip("`")
        if texto.lower().startswith("json"):
            texto = texto[4:].strip()

    try:
        return json.loads(texto)
    except json.JSONDecodeError as exc:
        raise AnalisisIAError(
            f"La respuesta de Claude no es JSON válido: {exc}\n\n"
            f"Respuesta recibida:\n{texto[:500]}..."
        ) from exc


def analisis_demo() -> dict[str, Any]:
    """Análisis simulado para mostrar la interfaz sin gastar API."""
    return {
        "resumen_ejecutivo": (
            "Licitación pública mayor para servicio de Inspección Técnica "
            "de Obras del Mercado Municipal de Temuco. Presupuesto "
            "referencial de $850 millones, plazo 24 meses. Criterios de "
            "evaluación favorecen experiencia previa en ITO de obras "
            "públicas similares."
        ),
        "objeto_contratacion": (
            "Servicio profesional de Inspección Técnica de Obras (ITO) "
            "para la construcción del nuevo Mercado Municipal de Temuco."
        ),
        "presupuesto_referencial": {
            "monto_clp": 850_000_000,
            "moneda": "CLP",
            "comentarios": "Incluye IVA. Pagos contra estado de pago mensual.",
        },
        "plazo_ejecucion": {
            "duracion": "24 meses",
            "fecha_inicio_estimada": "Tercer trimestre 2026",
            "hitos_relevantes": [
                "Inicio de obra",
                "Etapa de obra gruesa",
                "Etapa de terminaciones",
                "Recepción provisoria",
            ],
        },
        "criterios_evaluacion": [
            {
                "criterio": "Oferta económica",
                "ponderacion": 50,
                "comentarios": "Fórmula inversa proporcional al menor precio.",
            },
            {
                "criterio": "Experiencia del oferente",
                "ponderacion": 30,
                "comentarios": "Mínimo 3 obras similares en últimos 5 años.",
            },
            {
                "criterio": "Equipo profesional",
                "ponderacion": 18,
                "comentarios": "Pondera CV y dedicación de cada profesional.",
            },
            {
                "criterio": "Programa de integridad",
                "ponderacion": 2,
                "comentarios": "Política anti-corrupción y compliance.",
            },
        ],
        "equipo_profesional_minimo": [
            {
                "rol": "Profesional responsable",
                "experiencia_requerida": "10 años en ITO de obras públicas",
                "dedicacion": "50%",
            },
            {
                "rol": "Inspector técnico residente",
                "experiencia_requerida": "5 años en obras de edificación",
                "dedicacion": "100%",
            },
            {
                "rol": "Especialista estructural",
                "experiencia_requerida": "Ingeniero civil estructural, 8 años",
                "dedicacion": "30%",
            },
            {
                "rol": "Prevencionista de riesgos",
                "experiencia_requerida": "Certificación vigente, 5 años",
                "dedicacion": "50%",
            },
        ],
        "experiencia_oferente": (
            "Mínimo 3 contratos de ITO de obras de edificación con monto "
            "individual sobre 500 millones, ejecutados en los últimos 5 años."
        ),
        "garantias": {
            "seriedad_oferta": "$25.500.000 (3% del presupuesto), vigencia 120 días",
            "fiel_cumplimiento": "5% del monto adjudicado, vigencia plazo + 60 días",
            "anticipo": "No contempla anticipo",
        },
        "multas_y_sanciones": (
            "Atraso en informes: 5 UTM por día. Incumplimiento de "
            "obligaciones laborales: 10 UTM. Incumplimiento grave: "
            "término anticipado y ejecución de garantía."
        ),
        "estructura_pagos": (
            "Pagos mensuales contra estado de pago aprobado por la ITO. "
            "Retención del 10% liberada en recepción provisoria."
        ),
        "riesgos_identificados": [
            {
                "riesgo": "Plazo extenso (24 meses) con potencial extensión",
                "nivel": "medio",
                "mitigacion": "Modelar costos con escalamiento e inflación.",
            },
            {
                "riesgo": "Multas por atraso en informes son altas",
                "nivel": "medio",
                "mitigacion": "Definir procedimiento interno estricto de reportabilidad.",
            },
            {
                "riesgo": "Sin anticipo: requiere capital de trabajo",
                "nivel": "alto",
                "mitigacion": "Asegurar línea de crédito o flujo propio.",
            },
        ],
        "fortalezas_para_rch": (
            "Experiencia previa en ITO de obras públicas municipales. "
            "Conocimiento de la región (proyecto Lumaco). "
            "Equipo profesional disponible para asignar."
        ),
        "debilidades_para_rch": (
            "Cantidad de contratos similares de los últimos 5 años podría "
            "quedar justo en el mínimo requerido. Revisar antecedentes."
        ),
        "recomendacion": "evaluar",
        "justificacion_recomendacion": (
            "El monto y el plazo encajan con la capacidad operativa de RCH. "
            "Antes de comprometer recursos, validar que se cumplan los "
            "mínimos de experiencia exigidos y dimensionar el costo "
            "financiero por la ausencia de anticipo."
        ),
    }
