"""
Barrido diario de adjudicaciones para la automatización (GitHub Actions o cron).

Uso:
    python monitor_diario.py

Variables de entorno:
    MP_TICKET       Ticket de Mercado Público (obligatorio en modo real).
    DIAS_ATRAS      Días hacia atrás a barrer (por defecto 2, cubre fines de semana).
    MODO_DEMO       "1" para usar datos ficticios (pruebas sin ticket).
    SMTP_USER / SMTP_PASSWORD / EMAIL_TO ...  (ver notificaciones.py) para el correo.

Comportamiento:
    1. Carga la configuración RCH (data/configuracion.json o valores por defecto).
    2. Barre las adjudicaciones del rubro en el rango indicado.
    3. Registra solo las nuevas en data/adjudicadas.json.
    4. Si hay nuevas y SMTP está configurado, envía un correo resumen.
    5. Imprime un resumen y termina con código 0 (o 1 ante error de datos).

El histórico (data/adjudicadas.json) debe persistirse entre ejecuciones; el
workflow de GitHub Actions lo commitea de vuelta al repositorio.
"""

from __future__ import annotations

import os
import sys

import data_store as ds
import monitoreo
import notificaciones


def main() -> int:
    modo_demo = os.environ.get("MODO_DEMO", "").strip() in ("1", "true", "True")
    ticket = os.environ.get("MP_TICKET", "").strip()
    try:
        dias_atras = int(os.environ.get("DIAS_ATRAS", "2"))
    except ValueError:
        dias_atras = 2

    config = ds.cargar_configuracion()

    print(f"[monitor] Modo {'DEMO' if modo_demo else 'REAL'} · últimos {dias_atras} día(s)")

    if modo_demo:
        registros = monitoreo.buscar_adjudicadas_demo(config)
    else:
        if not ticket:
            print("[monitor] ERROR: falta MP_TICKET. Aborta.", file=sys.stderr)
            return 1
        try:
            registros = monitoreo.buscar_adjudicadas(
                ticket=ticket,
                config=config,
                dias_atras=dias_atras,
                on_progress=lambda m: print(f"[monitor] {m}"),
            )
        except monitoreo.mp.MercadoPublicoError as exc:
            print(f"[monitor] ERROR consultando Mercado Público: {exc}", file=sys.stderr)
            return 1

    nuevas = ds.registrar_adjudicadas(registros)
    print(f"[monitor] {len(registros)} adjudicaciones del rubro · {len(nuevas)} nuevas.")

    if nuevas:
        for r in nuevas:
            proveedores = " · ".join(
                a.get("proveedor", "") for a in (r.get("Adjudicatarios") or [])
            )
            print(
                f"[monitor]  + {r.get('CodigoExterno')} · {r.get('Nombre', '')[:60]} "
                f"→ {proveedores or 'sin proveedor'} "
                f"({notificaciones.formato_clp(r.get('MontoAdjudicado'))})"
            )

        if notificaciones.smtp_configurado():
            try:
                notificaciones.enviar_email_resumen(nuevas)
                print(f"[monitor] Correo enviado a {os.environ.get('EMAIL_TO')}")
            except notificaciones.NotificacionError as exc:
                print(f"[monitor] AVISO: no se pudo enviar el correo: {exc}", file=sys.stderr)
        else:
            print("[monitor] SMTP no configurado; se omite el correo.")
    else:
        print("[monitor] Sin adjudicaciones nuevas; no se envía correo.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
