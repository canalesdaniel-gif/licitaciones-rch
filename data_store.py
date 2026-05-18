"""
Persistencia local del pipeline de licitaciones.

Para el MVP se usa un archivo JSON. Para producción se recomienda
migrar a SQLite o PostgreSQL.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

ARCHIVO_PIPELINE = Path("data/pipeline.json")
ARCHIVO_CONFIG = Path("data/configuracion.json")

ESTADOS_PIPELINE = [
    "descubierta",
    "evaluada",
    "en_preparacion",
    "presentada",
    "adjudicada",
    "desierta",
    "descartada",
]


def _asegurar_directorio() -> None:
    ARCHIVO_PIPELINE.parent.mkdir(parents=True, exist_ok=True)


def cargar_pipeline() -> list[dict[str, Any]]:
    """Carga las licitaciones guardadas en el pipeline."""
    _asegurar_directorio()
    if not ARCHIVO_PIPELINE.exists():
        return []
    try:
        with ARCHIVO_PIPELINE.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def guardar_pipeline(licitaciones: list[dict[str, Any]]) -> None:
    """Reemplaza el contenido completo del pipeline."""
    _asegurar_directorio()
    with ARCHIVO_PIPELINE.open("w", encoding="utf-8") as f:
        json.dump(licitaciones, f, ensure_ascii=False, indent=2)


def agregar_a_pipeline(licitacion: dict[str, Any], estado: str = "descubierta") -> bool:
    """Agrega una licitación al pipeline si no existe ya. Devuelve True si se agregó."""
    if estado not in ESTADOS_PIPELINE:
        raise ValueError(f"Estado inválido: {estado}")

    pipeline = cargar_pipeline()
    codigo = licitacion.get("CodigoExterno")
    if not codigo:
        return False

    if any(lic.get("CodigoExterno") == codigo for lic in pipeline):
        return False

    registro = {
        **licitacion,
        "estado_pipeline": estado,
        "fecha_agregada": datetime.now().isoformat(),
        "notas_internas": "",
        "score": None,
        "analisis_ia": None,
    }
    pipeline.append(registro)
    guardar_pipeline(pipeline)
    return True


def actualizar_estado(codigo: str, nuevo_estado: str) -> bool:
    """Actualiza el estado de una licitación del pipeline."""
    if nuevo_estado not in ESTADOS_PIPELINE:
        raise ValueError(f"Estado inválido: {nuevo_estado}")

    pipeline = cargar_pipeline()
    for lic in pipeline:
        if lic.get("CodigoExterno") == codigo:
            lic["estado_pipeline"] = nuevo_estado
            lic["fecha_ultima_actualizacion"] = datetime.now().isoformat()
            guardar_pipeline(pipeline)
            return True
    return False


def actualizar_campo(codigo: str, campo: str, valor: Any) -> bool:
    """Actualiza un campo arbitrario de una licitación del pipeline."""
    pipeline = cargar_pipeline()
    for lic in pipeline:
        if lic.get("CodigoExterno") == codigo:
            lic[campo] = valor
            lic["fecha_ultima_actualizacion"] = datetime.now().isoformat()
            guardar_pipeline(pipeline)
            return True
    return False


def eliminar_de_pipeline(codigo: str) -> bool:
    pipeline = cargar_pipeline()
    nuevo = [lic for lic in pipeline if lic.get("CodigoExterno") != codigo]
    if len(nuevo) == len(pipeline):
        return False
    guardar_pipeline(nuevo)
    return True


def cargar_configuracion() -> dict[str, Any]:
    """Carga la configuración personalizada del usuario."""
    _asegurar_directorio()
    if not ARCHIVO_CONFIG.exists():
        return configuracion_por_defecto()
    try:
        with ARCHIVO_CONFIG.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return configuracion_por_defecto()


def guardar_configuracion(config: dict[str, Any]) -> None:
    _asegurar_directorio()
    with ARCHIVO_CONFIG.open("w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def configuracion_por_defecto() -> dict[str, Any]:
    return {
        "palabras_clave": [
            "construcción",
            "restauración",
            "patrimonial",
            "ITO",
            "inspección técnica",
            "reparación",
            "reforzamiento",
            "siniestro",
        ],
        "regiones_interes": [
            "Región Metropolitana",
            "V Región de Valparaíso",
            "VII Región del Maule",
            "IX Región de La Araucanía",
        ],
        "monto_minimo_clp": 100_000_000,
        "monto_maximo_clp": 5_000_000_000,
        "umbral_score_recomendado": 70,
    }
