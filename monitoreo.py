"""
Monitoreo de obras adjudicadas en Mercado Público para el rubro RCH.

Flujo:
  1. Barrer las licitaciones adjudicadas en un rango de fechas.
  2. Prefiltrar por palabras clave (barato, sobre el resumen).
  3. Traer el detalle de cada candidata y quedarse con las del rubro objetivo
     (códigos UNSPSC de construcción / ingeniería / prefabricados).
  4. Enriquecer con el/los proveedor(es) adjudicado(s) y el monto.
  5. Devolver registros listos para guardar, mostrar o notificar.

El resultado se combina con `data_store.registrar_adjudicadas()` para detectar
solo las adjudicaciones NUEVAS respecto de barridos anteriores.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any, Callable

import api_mercado_publico as mp


def _normalizar(texto: str) -> str:
    if not texto:
        return ""
    equivalencias = str.maketrans("áéíóúÁÉÍÓÚñÑ", "aeiouAEIOUnN")
    return texto.translate(equivalencias).lower()


def _rubro_dos_digitos(codigo_onu: Any) -> int:
    try:
        return int(str(codigo_onu)[:2])
    except (ValueError, TypeError):
        return 0


def _coincide_palabras(texto: str, palabras_norm: list[str]) -> bool:
    if not palabras_norm:
        return True
    texto_norm = _normalizar(texto)
    return any(p in texto_norm for p in palabras_norm)


def construir_registro(
    resumen: dict[str, Any],
    detalle: dict[str, Any],
) -> dict[str, Any]:
    """Fusiona resumen + detalle en un registro de adjudicación uniforme."""
    info_adj = mp.extraer_adjudicatarios(detalle)

    codigo_onu = (
        detalle.get("CodigoProductoONU")
        or resumen.get("CodigoProductoONU")
        or ""
    )
    # Si el detalle trae ítems, tomar el ONU del primer ítem como referencia.
    items = detalle.get("Items") or {}
    lista_items = items.get("Listado") if isinstance(items, dict) else items
    if not codigo_onu and lista_items:
        codigo_onu = (lista_items[0] or {}).get("CodigoProductoONU", "")

    url = detalle.get("UrlMercadoPublico") or (
        "https://www.mercadopublico.cl/Procurement/Modules/RFB/"
        f"DetailsAcquisition.aspx?idlicitacion={resumen.get('CodigoExterno', '')}"
    )

    return {
        "CodigoExterno": resumen.get("CodigoExterno") or detalle.get("CodigoExterno"),
        "Nombre": detalle.get("Nombre") or resumen.get("Nombre", ""),
        "NombreOrganismo": detalle.get("NombreOrganismo")
        or resumen.get("NombreOrganismo", ""),
        "Region": detalle.get("Region") or resumen.get("Region", ""),
        "CodigoProductoONU": codigo_onu,
        "RubroPrincipal": detalle.get("RubroPrincipal", ""),
        "FechaAdjudicacion": info_adj["fecha_adjudicacion"]
        or detalle.get("FechaCierre", ""),
        "MontoAdjudicado": info_adj["monto_adjudicado"]
        or detalle.get("MontoEstimado"),
        "Adjudicatarios": info_adj["adjudicatarios"],
        "UrlMercadoPublico": url,
        "fecha_detectada": datetime.now().isoformat(),
    }


def buscar_adjudicadas(
    ticket: str,
    config: dict[str, Any],
    dias_atras: int = 1,
    fecha_referencia: date | None = None,
    max_detalles: int = 200,
    on_progress: Callable[[str], None] | None = None,
) -> list[dict[str, Any]]:
    """Barre y filtra las adjudicaciones del rubro en los últimos N días.

    Args:
        ticket: ticket de Mercado Público.
        config: configuración RCH (palabras_clave, rubros_codigo, montos, regiones).
        dias_atras: cuántos días hacia atrás barrer (incluye el día de referencia).
        fecha_referencia: día final del rango (por defecto, hoy).
        max_detalles: tope de llamadas de detalle para no exceder la cuota.
        on_progress: callback opcional para reportar avance (mensaje str).

    Returns:
        Lista de registros de adjudicación enriquecidos y filtrados por rubro.
    """
    def avisar(msg: str) -> None:
        if on_progress:
            on_progress(msg)

    fecha_hasta = fecha_referencia or date.today()
    fecha_desde = fecha_hasta - timedelta(days=max(0, dias_atras - 1))

    palabras_norm = [_normalizar(p) for p in config.get("palabras_clave", []) if p.strip()]
    rubros = set(config.get("rubros_codigo", [72, 81, 95]))
    regiones_interes = config.get("regiones_interes", [])
    regiones_norm = [_normalizar(r) for r in regiones_interes]

    avisar(f"Consultando adjudicadas del {fecha_desde} al {fecha_hasta}...")
    resumenes = mp.listar_adjudicadas_rango(fecha_desde, fecha_hasta, ticket)
    avisar(f"{len(resumenes)} adjudicaciones brutas. Prefiltrando por palabras clave...")

    # Prefiltro barato por nombre para reducir llamadas de detalle.
    candidatas = [
        r for r in resumenes
        if _coincide_palabras(str(r.get("Nombre", "")), palabras_norm)
    ]
    if len(candidatas) > max_detalles:
        avisar(
            f"{len(candidatas)} candidatas exceden el tope de {max_detalles} "
            "detalles; se procesan las primeras."
        )
        candidatas = candidatas[:max_detalles]

    registros: list[dict[str, Any]] = []
    for i, resumen in enumerate(candidatas, start=1):
        codigo = resumen.get("CodigoExterno")
        if not codigo:
            continue
        avisar(f"[{i}/{len(candidatas)}] Detalle {codigo}...")
        try:
            detalle = mp.detalle_licitacion(codigo, ticket)
        except mp.MercadoPublicoError:
            # Si el detalle falla, usar el resumen como respaldo.
            detalle = dict(resumen)

        registro = construir_registro(resumen, detalle)

        # Filtro por rubro: aceptar si el código ONU cae en el rubro objetivo
        # o si igual coincidió por palabra clave (rubro suele venir en el nombre).
        rubro_ok = _rubro_dos_digitos(registro["CodigoProductoONU"]) in rubros
        palabra_ok = _coincide_palabras(registro["Nombre"], palabras_norm)
        if not (rubro_ok or palabra_ok):
            continue

        # Filtro opcional por región de interés.
        if regiones_norm:
            region_norm = _normalizar(str(registro.get("Region", "")))
            if region_norm and not any(r in region_norm for r in regiones_norm):
                continue

        registros.append(registro)

    avisar(f"{len(registros)} adjudicaciones del rubro tras filtrar.")
    return registros


def buscar_adjudicadas_demo(config: dict[str, Any]) -> list[dict[str, Any]]:
    """Versión demostrativa: usa datos ficticios y respeta el filtro de rubro."""
    import demo_data

    rubros = set(config.get("rubros_codigo", [72, 81, 95]))
    palabras_norm = [_normalizar(p) for p in config.get("palabras_clave", []) if p.strip()]

    resultado = []
    for reg in demo_data.adjudicadas_demo():
        rubro_ok = _rubro_dos_digitos(reg.get("CodigoProductoONU")) in rubros
        palabra_ok = _coincide_palabras(reg.get("Nombre", ""), palabras_norm)
        if rubro_ok or palabra_ok:
            resultado.append(dict(reg))
    return resultado
