"""
Cliente para la API pública de Mercado Público (Chilecompra).

Documentación oficial: https://desarrolladores.mercadopublico.cl/

Endpoints principales utilizados:
  - /licitaciones.json           Listado por fecha o por estado
  - /licitaciones.json?codigo=X  Detalle completo de una licitación
  - /ordenesdecompra.json        Órdenes de compra (inteligencia competitiva)

Para obtener un ticket: registrarse en mercadopublico.cl y solicitarlo en
"Mis tickets" del panel de desarrolladores.
"""

from __future__ import annotations

import time
from datetime import datetime, date, timedelta
from typing import Any

import requests

BASE_URL = "https://api.mercadopublico.cl/servicios/v1/Publico"
TIMEOUT_SEGUNDOS = 30


class MercadoPublicoError(Exception):
    """Error al consultar la API de Mercado Público."""


def _request(endpoint: str, params: dict[str, Any]) -> dict[str, Any]:
    url = f"{BASE_URL}/{endpoint}"
    try:
        respuesta = requests.get(url, params=params, timeout=TIMEOUT_SEGUNDOS)
        respuesta.raise_for_status()
        return respuesta.json()
    except requests.exceptions.RequestException as exc:
        raise MercadoPublicoError(f"Fallo al consultar {endpoint}: {exc}") from exc
    except ValueError as exc:
        raise MercadoPublicoError(f"Respuesta no JSON desde {endpoint}: {exc}") from exc


def listar_licitaciones_por_fecha(
    fecha: date | datetime,
    ticket: str,
    estado: str | None = None,
) -> list[dict[str, Any]]:
    """Lista licitaciones publicadas o vigentes en una fecha específica.

    Args:
        fecha: día consultado.
        ticket: ticket de autenticación.
        estado: opcional. activas | publicadas | adjudicadas | desiertas | etc.

    Returns:
        Lista de diccionarios con campos resumidos por licitación.
    """
    params: dict[str, Any] = {
        "fecha": fecha.strftime("%d%m%Y"),
        "ticket": ticket,
    }
    if estado:
        params["estado"] = estado

    data = _request("licitaciones.json", params)
    return data.get("Listado", []) or []


def detalle_licitacion(codigo: str, ticket: str) -> dict[str, Any]:
    """Obtiene la ficha completa de una licitación por su código.

    El código tiene la forma "1658-121-LR26".
    """
    params = {"codigo": codigo, "ticket": ticket}
    data = _request("licitaciones.json", params)
    listado = data.get("Listado") or []
    if not listado:
        raise MercadoPublicoError(f"No se encontró la licitación {codigo}")
    return listado[0]


def listar_adjudicadas_rango(
    fecha_desde: date | datetime,
    fecha_hasta: date | datetime,
    ticket: str,
    pausa_segundos: float = 0.4,
) -> list[dict[str, Any]]:
    """Lista las licitaciones adjudicadas en cada día del rango [desde, hasta].

    La API de Mercado Público consulta un día a la vez, por lo que se itera
    día por día. Se aplica una pausa entre llamadas para respetar el límite
    de la API.

    Returns:
        Lista de licitaciones adjudicadas (resumen). Deduplicadas por código.
    """
    if isinstance(fecha_desde, datetime):
        fecha_desde = fecha_desde.date()
    if isinstance(fecha_hasta, datetime):
        fecha_hasta = fecha_hasta.date()
    if fecha_desde > fecha_hasta:
        fecha_desde, fecha_hasta = fecha_hasta, fecha_desde

    vistos: set[str] = set()
    resultado: list[dict[str, Any]] = []
    dia = fecha_desde
    while dia <= fecha_hasta:
        listado = listar_licitaciones_por_fecha(dia, ticket, estado="adjudicadas")
        for lic in listado:
            codigo = lic.get("CodigoExterno")
            if codigo and codigo not in vistos:
                vistos.add(codigo)
                resultado.append(lic)
        dia = dia + timedelta(days=1)
        if pausa_segundos and dia <= fecha_hasta:
            time.sleep(pausa_segundos)
    return resultado


def extraer_adjudicatarios(detalle: dict[str, Any]) -> dict[str, Any]:
    """Extrae del detalle de una licitación adjudicada quién ganó y por cuánto.

    La API expone la adjudicación de dos formas posibles (varía por versión):
      - un objeto "Adjudicacion" a nivel de licitación, y/o
      - un objeto "Adjudicacion" dentro de cada ítem de "Items".

    Se recorre lo disponible de forma tolerante y se agrega por proveedor.

    Returns:
        Dict con:
          - adjudicatarios: lista de {proveedor, rut, monto}
          - monto_adjudicado: suma total adjudicada (o None si no hay dato)
          - fecha_adjudicacion: fecha informada (o "")
    """
    por_proveedor: dict[str, dict[str, Any]] = {}

    def _acumular(nombre: Any, rut: Any, monto: Any) -> None:
        nombre = str(nombre).strip() if nombre else ""
        if not nombre:
            return
        clave = str(rut).strip() or nombre
        try:
            monto_num = float(monto) if monto not in (None, "") else 0.0
        except (ValueError, TypeError):
            monto_num = 0.0
        registro = por_proveedor.setdefault(
            clave, {"proveedor": nombre, "rut": str(rut).strip() if rut else "", "monto": 0.0}
        )
        registro["monto"] += monto_num

    # Ítems adjudicados
    items = detalle.get("Items") or {}
    lista_items = items.get("Listado") if isinstance(items, dict) else items
    for item in lista_items or []:
        adj = item.get("Adjudicacion") if isinstance(item, dict) else None
        if not adj:
            continue
        cantidad = adj.get("Cantidad") or item.get("Cantidad") or 0
        monto_unit = adj.get("MontoUnitario") or 0
        try:
            monto_item = float(monto_unit) * float(cantidad or 0)
        except (ValueError, TypeError):
            monto_item = adj.get("MontoUnitario") or 0
        _acumular(
            adj.get("NombreOferente") or adj.get("RazonSocial"),
            adj.get("RutProveedor") or adj.get("RutOferente"),
            monto_item,
        )

    # Adjudicación a nivel de licitación (respaldo)
    adj_top = detalle.get("Adjudicacion")
    fecha_adj = ""
    if isinstance(adj_top, dict):
        fecha_adj = adj_top.get("Fecha") or adj_top.get("FechaAdjudicacion") or ""
        if not por_proveedor:
            _acumular(
                adj_top.get("NombreOferente") or adj_top.get("Proveedor"),
                adj_top.get("RutProveedor"),
                adj_top.get("MontoAdjudicado") or adj_top.get("Monto"),
            )

    adjudicatarios = [
        {"proveedor": v["proveedor"], "rut": v["rut"], "monto": int(v["monto"]) if v["monto"] else None}
        for v in por_proveedor.values()
    ]
    monto_total = sum(v["monto"] for v in por_proveedor.values())

    return {
        "adjudicatarios": adjudicatarios,
        "monto_adjudicado": int(monto_total) if monto_total else None,
        "fecha_adjudicacion": fecha_adj,
    }


def filtrar_por_rubro(
    licitaciones: list[dict[str, Any]],
    rubros_codigo: list[int],
) -> list[dict[str, Any]]:
    """Filtra licitaciones cuyo rubro principal coincida con alguno entregado.

    Los códigos de rubro corresponden al clasificador UNSPSC usado por
    Mercado Público. Ejemplos relevantes para RCH:
      - 72  Servicios de construcción de edificaciones y mantención
      - 81  Servicios de ingeniería y arquitectura
      - 95  Edificios y estructuras prefabricadas
    """
    resultado = []
    for lic in licitaciones:
        # Mercado Público anida ítems en "Items"; en el listado resumido
        # algunas licitaciones traen "CodigoProductoONU"
        codigo_rubro = lic.get("CodigoProductoONU") or 0
        try:
            rubro_int = int(str(codigo_rubro)[:2])
        except (ValueError, TypeError):
            rubro_int = 0
        if rubro_int in rubros_codigo:
            resultado.append(lic)
    return resultado


def buscar_por_palabras_clave(
    licitaciones: list[dict[str, Any]],
    palabras: list[str],
) -> list[dict[str, Any]]:
    """Filtro local por coincidencia de palabras en el nombre o descripción.

    Las palabras se buscan sin distinguir mayúsculas ni tildes.
    """
    def normalizar(texto: str) -> str:
        if not texto:
            return ""
        equivalencias = str.maketrans("áéíóúÁÉÍÓÚñÑ", "aeiouAEIOUnN")
        return texto.translate(equivalencias).lower()

    palabras_norm = [normalizar(p) for p in palabras if p.strip()]
    if not palabras_norm:
        return licitaciones

    resultado = []
    for lic in licitaciones:
        campos = " ".join(
            [
                str(lic.get("Nombre", "")),
                str(lic.get("Descripcion", "")),
                str(lic.get("NombreOrganismo", "")),
            ]
        )
        campos_norm = normalizar(campos)
        if any(p in campos_norm for p in palabras_norm):
            resultado.append(lic)
    return resultado
