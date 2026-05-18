"""
Calcula un score de pertinencia para una licitación según el perfil RCH.

El score va de 0 a 100. Se construye con cinco dimensiones ponderadas.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any


PESOS = {
    "rubro": 25,
    "monto": 20,
    "region": 15,
    "palabras_clave": 25,
    "plazo": 15,
}


def _normalizar(texto: str) -> str:
    if not texto:
        return ""
    equivalencias = str.maketrans("áéíóúÁÉÍÓÚñÑ", "aeiouAEIOUnN")
    return texto.translate(equivalencias).lower()


def _score_rubro(lic: dict[str, Any]) -> int:
    """Da puntaje según rubro/CodigoProductoONU. Construcción y restauración pesan más."""
    codigo = str(lic.get("CodigoProductoONU", ""))
    rubro_principal = _normalizar(str(lic.get("RubroPrincipal", "")))

    if codigo.startswith("72") or "construccion" in rubro_principal or "restauracion" in rubro_principal:
        return 100
    if codigo.startswith("81") or "ingenieria" in rubro_principal or "arquitectura" in rubro_principal:
        return 85
    if "patrimonial" in rubro_principal:
        return 100
    return 30


def _score_monto(lic: dict[str, Any], config: dict[str, Any]) -> int:
    monto = lic.get("MontoEstimado", 0) or 0
    minimo = config.get("monto_minimo_clp", 100_000_000)
    maximo = config.get("monto_maximo_clp", 5_000_000_000)

    if monto == 0:
        return 50  # no informado, neutro
    if monto < minimo:
        return 20
    if monto > maximo:
        return 40
    # Dentro del rango óptimo, premio cercanía al centro
    rango = maximo - minimo
    centro = minimo + rango / 2
    distancia_relativa = abs(monto - centro) / (rango / 2)
    return max(60, int(100 - distancia_relativa * 30))


def _score_region(lic: dict[str, Any], config: dict[str, Any]) -> int:
    region = lic.get("Region", "")
    regiones_interes = config.get("regiones_interes", [])
    if any(_normalizar(r) in _normalizar(region) for r in regiones_interes):
        return 100
    return 40


def _score_palabras_clave(lic: dict[str, Any], config: dict[str, Any]) -> int:
    palabras = config.get("palabras_clave", [])
    if not palabras:
        return 60

    campos = " ".join(
        [
            str(lic.get("Nombre", "")),
            str(lic.get("Descripcion", "")),
        ]
    )
    campos_norm = _normalizar(campos)
    coincidencias = sum(1 for p in palabras if _normalizar(p) in campos_norm)

    proporcion = coincidencias / len(palabras)
    return int(min(100, 40 + proporcion * 120))


def _score_plazo(lic: dict[str, Any]) -> int:
    """Premia plazos razonables de presentación (no muy cortos ni muy largos)."""
    fecha_cierre_str = lic.get("FechaCierre", "")
    if not fecha_cierre_str:
        return 50

    try:
        fecha_cierre = datetime.fromisoformat(fecha_cierre_str.replace("Z", ""))
    except (ValueError, TypeError):
        return 50

    dias_restantes = (fecha_cierre - datetime.now()).days

    if dias_restantes < 5:
        return 20  # muy poco tiempo
    if dias_restantes < 10:
        return 50
    if dias_restantes < 45:
        return 100  # rango ideal
    if dias_restantes < 90:
        return 80
    return 60


def calcular_score(lic: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    """Calcula el score total y el desglose por dimensión.

    Returns:
        Dict con campos:
          - total: score total de 0 a 100
          - desglose: dict con score parcial por dimensión
          - recomendacion: texto cualitativo
    """
    desglose = {
        "rubro": _score_rubro(lic),
        "monto": _score_monto(lic, config),
        "region": _score_region(lic, config),
        "palabras_clave": _score_palabras_clave(lic, config),
        "plazo": _score_plazo(lic),
    }

    total = sum(desglose[k] * PESOS[k] / 100 for k in desglose)
    total = round(total, 1)

    if total >= 80:
        recomendacion = "Altamente recomendada. Priorizar análisis profundo."
    elif total >= 65:
        recomendacion = "Recomendada. Evaluar antes de descartar."
    elif total >= 45:
        recomendacion = "Pertinencia media. Solo si hay capacidad disponible."
    else:
        recomendacion = "Baja pertinencia. Descartar salvo razón estratégica."

    return {
        "total": total,
        "desglose": desglose,
        "recomendacion": recomendacion,
    }
