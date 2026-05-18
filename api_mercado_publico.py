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
from datetime import datetime, date
from typing import Any

import requests

BASE_URL = "https://api.mercadopublico.cl/servicios/v1/publico"
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
