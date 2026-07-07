"""
Datos de demostración para usar el MVP sin un ticket activo de Mercado Público.

Contiene licitaciones ficticias pero realistas del rubro construcción,
restauración patrimonial e ITO, basadas en estructuras reales del sistema
Chilecompra.
"""

from __future__ import annotations

from datetime import datetime, timedelta


def licitaciones_demo() -> list[dict]:
    hoy = datetime.now()

    return [
        {
            "CodigoExterno": "1658-121-LR26",
            "Nombre": "Inspección Técnica de Obras Mercado Municipal de Temuco",
            "Descripcion": (
                "Servicio de Inspección Técnica de Obras (ITO) para la "
                "construcción del nuevo Mercado Municipal de Temuco. "
                "Incluye supervisión de cumplimiento técnico, plazos, "
                "presupuesto y normativa. Duración estimada 24 meses."
            ),
            "NombreOrganismo": "Ilustre Municipalidad de Temuco",
            "CodigoOrganismo": "6964",
            "Region": "IX Región de La Araucanía",
            "MontoEstimado": 850_000_000,
            "Moneda": "CLP",
            "FechaPublicacion": (hoy - timedelta(days=5)).isoformat(),
            "FechaCierre": (hoy + timedelta(days=25)).isoformat(),
            "Estado": "publicada",
            "CodigoTipo": "LR",
            "CodigoProductoONU": "81101500",
            "RubroPrincipal": "Servicios de ingeniería",
            "TipoLicitacion": "LR",
        },
        {
            "CodigoExterno": "2345-67-LP26",
            "Nombre": "Restauración Iglesia San Francisco de Castro",
            "Descripcion": (
                "Restauración patrimonial integral de la Iglesia San "
                "Francisco de Castro, declarada Monumento Nacional. "
                "Incluye refuerzo estructural, tratamiento de maderas, "
                "techumbre, vitrales y obras menores. Plazo 18 meses."
            ),
            "NombreOrganismo": "Consejo de Monumentos Nacionales",
            "CodigoOrganismo": "1502",
            "Region": "X Región de Los Lagos",
            "MontoEstimado": 1_200_000_000,
            "Moneda": "CLP",
            "FechaPublicacion": (hoy - timedelta(days=2)).isoformat(),
            "FechaCierre": (hoy + timedelta(days=40)).isoformat(),
            "Estado": "publicada",
            "CodigoTipo": "LP",
            "CodigoProductoONU": "72101500",
            "RubroPrincipal": "Construcción y restauración",
            "TipoLicitacion": "LP",
        },
        {
            "CodigoExterno": "3489-15-LE26",
            "Nombre": "Reparación post-sismo Escuela Rural de Curepto",
            "Descripcion": (
                "Reparación de daños estructurales y no estructurales en "
                "Escuela Rural de Curepto producto del sismo de 2025. "
                "Reforzamiento sísmico, reposición de cielos, pintura y "
                "habilitación de servicios."
            ),
            "NombreOrganismo": "DAEM Curepto",
            "CodigoOrganismo": "5421",
            "Region": "VII Región del Maule",
            "MontoEstimado": 320_000_000,
            "Moneda": "CLP",
            "FechaPublicacion": (hoy - timedelta(days=8)).isoformat(),
            "FechaCierre": (hoy + timedelta(days=12)).isoformat(),
            "Estado": "publicada",
            "CodigoTipo": "LE",
            "CodigoProductoONU": "72101511",
            "RubroPrincipal": "Construcción educacional",
            "TipoLicitacion": "LE",
        },
        {
            "CodigoExterno": "4521-89-LP26",
            "Nombre": "Conservación Casa Patronal Hacienda San José",
            "Descripcion": (
                "Conservación y puesta en valor de Casa Patronal de la "
                "Hacienda San José, inmueble de conservación histórica. "
                "Tratamientos de adobe, tejados de teja artesanal, "
                "carpinterías y restauración de muros perimetrales."
            ),
            "NombreOrganismo": "Servicio Nacional del Patrimonio Cultural",
            "CodigoOrganismo": "1501",
            "Region": "VI Región del Libertador",
            "MontoEstimado": 680_000_000,
            "Moneda": "CLP",
            "FechaPublicacion": (hoy - timedelta(days=1)).isoformat(),
            "FechaCierre": (hoy + timedelta(days=45)).isoformat(),
            "Estado": "publicada",
            "CodigoTipo": "LP",
            "CodigoProductoONU": "72101501",
            "RubroPrincipal": "Restauración patrimonial",
            "TipoLicitacion": "LP",
        },
        {
            "CodigoExterno": "5012-44-LE26",
            "Nombre": "Inspección Técnica Centro Cultural Valdivia",
            "Descripcion": (
                "Servicio de ITO para construcción del Centro Cultural de "
                "Valdivia. Edificio de 4500 m2 con auditorio, salas de "
                "exposición y cafetería. Plazo de inspección 20 meses."
            ),
            "NombreOrganismo": "Gobierno Regional de Los Ríos",
            "CodigoOrganismo": "7521",
            "Region": "XIV Región de Los Ríos",
            "MontoEstimado": 540_000_000,
            "Moneda": "CLP",
            "FechaPublicacion": (hoy - timedelta(days=10)).isoformat(),
            "FechaCierre": (hoy + timedelta(days=18)).isoformat(),
            "Estado": "publicada",
            "CodigoTipo": "LE",
            "CodigoProductoONU": "81101500",
            "RubroPrincipal": "Servicios de ingeniería",
            "TipoLicitacion": "LE",
        },
        {
            "CodigoExterno": "6789-12-LP26",
            "Nombre": "Reconstrucción Hospital Comunitario de Quintero",
            "Descripcion": (
                "Reconstrucción parcial del Hospital Comunitario de "
                "Quintero tras siniestro de incendio. Incluye demolición "
                "selectiva, obra gruesa, instalaciones y terminaciones. "
                "Superficie afectada 1200 m2."
            ),
            "NombreOrganismo": "Servicio de Salud Viña del Mar - Quillota",
            "CodigoOrganismo": "3401",
            "Region": "V Región de Valparaíso",
            "MontoEstimado": 2_400_000_000,
            "Moneda": "CLP",
            "FechaPublicacion": (hoy - timedelta(days=15)).isoformat(),
            "FechaCierre": (hoy + timedelta(days=5)).isoformat(),
            "Estado": "publicada",
            "CodigoTipo": "LP",
            "CodigoProductoONU": "72101502",
            "RubroPrincipal": "Construcción hospitalaria",
            "TipoLicitacion": "LP",
        },
        {
            "CodigoExterno": "7234-56-LE26",
            "Nombre": "Mejoramiento fachadas Barrio Yungay",
            "Descripcion": (
                "Mejoramiento de fachadas patrimoniales en Barrio Yungay, "
                "zona típica. Incluye restitución de estucos, pintura "
                "acorde a paleta autorizada y trabajos menores de "
                "carpintería en ventanas."
            ),
            "NombreOrganismo": "Ilustre Municipalidad de Santiago",
            "CodigoOrganismo": "6101",
            "Region": "Región Metropolitana",
            "MontoEstimado": 180_000_000,
            "Moneda": "CLP",
            "FechaPublicacion": (hoy - timedelta(days=3)).isoformat(),
            "FechaCierre": (hoy + timedelta(days=22)).isoformat(),
            "Estado": "publicada",
            "CodigoTipo": "LE",
            "CodigoProductoONU": "72101501",
            "RubroPrincipal": "Restauración patrimonial",
            "TipoLicitacion": "LE",
        },
        {
            "CodigoExterno": "8901-23-LP26",
            "Nombre": "Construcción Edificio Consistorial Lumaco",
            "Descripcion": (
                "Construcción del nuevo Edificio Consistorial de la "
                "comuna de Lumaco. Edificio de dos pisos, 1800 m2, con "
                "estructura mixta hormigón armado y madera. Plazo 14 meses."
            ),
            "NombreOrganismo": "Ilustre Municipalidad de Lumaco",
            "CodigoOrganismo": "6925",
            "Region": "IX Región de La Araucanía",
            "MontoEstimado": 1_650_000_000,
            "Moneda": "CLP",
            "FechaPublicacion": (hoy - timedelta(days=7)).isoformat(),
            "FechaCierre": (hoy + timedelta(days=30)).isoformat(),
            "Estado": "publicada",
            "CodigoTipo": "LP",
            "CodigoProductoONU": "72101502",
            "RubroPrincipal": "Edificación pública",
            "TipoLicitacion": "LP",
        },
    ]


def adjudicadas_demo() -> list[dict]:
    """Licitaciones ya cerradas y adjudicadas del rubro RCH.

    Incluye la empresa ganadora, el monto adjudicado (que puede diferir del
    referencial), la cantidad de oferentes y la lista de competidores. Sirve
    como inteligencia competitiva: quién gana, a qué precio y contra quiénes.
    """
    hoy = datetime.now()

    return [
        {
            "CodigoExterno": "1658-98-LP25",
            "Nombre": "Restauración Teatro Municipal de Chillán",
            "NombreOrganismo": "Ilustre Municipalidad de Chillán",
            "Region": "Región de Ñuble",
            "MontoEstimado": 1_450_000_000,
            "Moneda": "CLP",
            "Estado": "adjudicada",
            "TipoLicitacion": "LP",
            "FechaPublicacion": (hoy - timedelta(days=120)).isoformat(),
            "FechaCierre": (hoy - timedelta(days=85)).isoformat(),
            "FechaAdjudicacion": (hoy - timedelta(days=40)).isoformat(),
            "Adjudicacion": {
                "EmpresaGanadora": "Restauraciones Patrimoniales del Sur SpA",
                "RutGanador": "76.812.334-5",
                "MontoAdjudicado": 1_398_500_000,
                "NumeroOferentes": 4,
                "Oferentes": [
                    {"Empresa": "Restauraciones Patrimoniales del Sur SpA", "Monto": 1_398_500_000, "Ganador": True},
                    {"Empresa": "Constructora Aconcagua Ltda.", "Monto": 1_442_000_000, "Ganador": False},
                    {"Empresa": "RCH Construcción & Restauración", "Monto": 1_455_900_000, "Ganador": False},
                    {"Empresa": "Ingeniería Patrimonial Andina SA", "Monto": 1_501_000_000, "Ganador": False},
                ],
            },
        },
        {
            "CodigoExterno": "2201-45-LP25",
            "Nombre": "Reconstrucción Casona Colonial de Vichuquén",
            "NombreOrganismo": "Servicio Nacional del Patrimonio Cultural",
            "Region": "VII Región del Maule",
            "MontoEstimado": 890_000_000,
            "Moneda": "CLP",
            "Estado": "adjudicada",
            "TipoLicitacion": "LP",
            "FechaPublicacion": (hoy - timedelta(days=140)).isoformat(),
            "FechaCierre": (hoy - timedelta(days=100)).isoformat(),
            "FechaAdjudicacion": (hoy - timedelta(days=62)).isoformat(),
            "Adjudicacion": {
                "EmpresaGanadora": "RCH Construcción & Restauración",
                "RutGanador": "77.201.556-9",
                "MontoAdjudicado": 861_300_000,
                "NumeroOferentes": 3,
                "Oferentes": [
                    {"Empresa": "RCH Construcción & Restauración", "Monto": 861_300_000, "Ganador": True},
                    {"Empresa": "Restauraciones Patrimoniales del Sur SpA", "Monto": 878_400_000, "Ganador": False},
                    {"Empresa": "Constructora Aconcagua Ltda.", "Monto": 905_000_000, "Ganador": False},
                ],
            },
        },
        {
            "CodigoExterno": "3390-77-LR25",
            "Nombre": "ITO Construcción Biblioteca Regional de Rancagua",
            "NombreOrganismo": "Gobierno Regional del Libertador B. O'Higgins",
            "Region": "VI Región del Libertador",
            "MontoEstimado": 620_000_000,
            "Moneda": "CLP",
            "Estado": "adjudicada",
            "TipoLicitacion": "LR",
            "FechaPublicacion": (hoy - timedelta(days=110)).isoformat(),
            "FechaCierre": (hoy - timedelta(days=78)).isoformat(),
            "FechaAdjudicacion": (hoy - timedelta(days=35)).isoformat(),
            "Adjudicacion": {
                "EmpresaGanadora": "Ingeniería Patrimonial Andina SA",
                "RutGanador": "76.550.912-1",
                "MontoAdjudicado": 611_900_000,
                "NumeroOferentes": 5,
                "Oferentes": [
                    {"Empresa": "Ingeniería Patrimonial Andina SA", "Monto": 611_900_000, "Ganador": True},
                    {"Empresa": "RCH Construcción & Restauración", "Monto": 618_000_000, "Ganador": False},
                    {"Empresa": "Inspecciones Técnicas Centro SpA", "Monto": 625_500_000, "Ganador": False},
                    {"Empresa": "Constructora Aconcagua Ltda.", "Monto": 629_000_000, "Ganador": False},
                    {"Empresa": "Gestión de Obras del Maule Ltda.", "Monto": 640_200_000, "Ganador": False},
                ],
            },
        },
        {
            "CodigoExterno": "4102-30-LP25",
            "Nombre": "Conservación Muros Coloniales Convento San Agustín",
            "NombreOrganismo": "Consejo de Monumentos Nacionales",
            "Region": "Región Metropolitana",
            "MontoEstimado": 415_000_000,
            "Moneda": "CLP",
            "Estado": "adjudicada",
            "TipoLicitacion": "LE",
            "FechaPublicacion": (hoy - timedelta(days=95)).isoformat(),
            "FechaCierre": (hoy - timedelta(days=64)).isoformat(),
            "FechaAdjudicacion": (hoy - timedelta(days=28)).isoformat(),
            "Adjudicacion": {
                "EmpresaGanadora": "RCH Construcción & Restauración",
                "RutGanador": "77.201.556-9",
                "MontoAdjudicado": 402_800_000,
                "NumeroOferentes": 4,
                "Oferentes": [
                    {"Empresa": "RCH Construcción & Restauración", "Monto": 402_800_000, "Ganador": True},
                    {"Empresa": "Restauraciones Patrimoniales del Sur SpA", "Monto": 410_000_000, "Ganador": False},
                    {"Empresa": "Taller de Conservación Histórica Ltda.", "Monto": 418_500_000, "Ganador": False},
                    {"Empresa": "Ingeniería Patrimonial Andina SA", "Monto": 421_000_000, "Ganador": False},
                ],
            },
        },
        {
            "CodigoExterno": "5561-19-LP25",
            "Nombre": "Restauración Estación de Ferrocarriles de Talca",
            "NombreOrganismo": "Ilustre Municipalidad de Talca",
            "Region": "VII Región del Maule",
            "MontoEstimado": 1_120_000_000,
            "Moneda": "CLP",
            "Estado": "adjudicada",
            "TipoLicitacion": "LP",
            "FechaPublicacion": (hoy - timedelta(days=160)).isoformat(),
            "FechaCierre": (hoy - timedelta(days=125)).isoformat(),
            "FechaAdjudicacion": (hoy - timedelta(days=80)).isoformat(),
            "Adjudicacion": {
                "EmpresaGanadora": "Constructora Aconcagua Ltda.",
                "RutGanador": "76.104.780-3",
                "MontoAdjudicado": 1_089_000_000,
                "NumeroOferentes": 6,
                "Oferentes": [
                    {"Empresa": "Constructora Aconcagua Ltda.", "Monto": 1_089_000_000, "Ganador": True},
                    {"Empresa": "RCH Construcción & Restauración", "Monto": 1_098_500_000, "Ganador": False},
                    {"Empresa": "Restauraciones Patrimoniales del Sur SpA", "Monto": 1_110_000_000, "Ganador": False},
                    {"Empresa": "Ingeniería Patrimonial Andina SA", "Monto": 1_125_000_000, "Ganador": False},
                    {"Empresa": "Gestión de Obras del Maule Ltda.", "Monto": 1_140_000_000, "Ganador": False},
                    {"Empresa": "Constructora del Pacífico SA", "Monto": 1_162_000_000, "Ganador": False},
                ],
            },
        },
        {
            "CodigoExterno": "6720-52-LE25",
            "Nombre": "Reparación Techumbre Iglesia de Achao",
            "NombreOrganismo": "Consejo de Monumentos Nacionales",
            "Region": "X Región de Los Lagos",
            "MontoEstimado": 350_000_000,
            "Moneda": "CLP",
            "Estado": "adjudicada",
            "TipoLicitacion": "LE",
            "FechaPublicacion": (hoy - timedelta(days=88)).isoformat(),
            "FechaCierre": (hoy - timedelta(days=58)).isoformat(),
            "FechaAdjudicacion": (hoy - timedelta(days=21)).isoformat(),
            "Adjudicacion": {
                "EmpresaGanadora": "Restauraciones Patrimoniales del Sur SpA",
                "RutGanador": "76.812.334-5",
                "MontoAdjudicado": 344_200_000,
                "NumeroOferentes": 3,
                "Oferentes": [
                    {"Empresa": "Restauraciones Patrimoniales del Sur SpA", "Monto": 344_200_000, "Ganador": True},
                    {"Empresa": "Taller de Conservación Histórica Ltda.", "Monto": 349_000_000, "Ganador": False},
                    {"Empresa": "RCH Construcción & Restauración", "Monto": 352_800_000, "Ganador": False},
                ],
            },
        },
        {
            "CodigoExterno": "7810-08-LR25",
            "Nombre": "ITO Reposición Escuela Patrimonial de Lota",
            "NombreOrganismo": "DAEM Lota",
            "Region": "VIII Región del Biobío",
            "MontoEstimado": 480_000_000,
            "Moneda": "CLP",
            "Estado": "adjudicada",
            "TipoLicitacion": "LR",
            "FechaPublicacion": (hoy - timedelta(days=76)).isoformat(),
            "FechaCierre": (hoy - timedelta(days=48)).isoformat(),
            "FechaAdjudicacion": (hoy - timedelta(days=15)).isoformat(),
            "Adjudicacion": {
                "EmpresaGanadora": "RCH Construcción & Restauración",
                "RutGanador": "77.201.556-9",
                "MontoAdjudicado": 471_500_000,
                "NumeroOferentes": 4,
                "Oferentes": [
                    {"Empresa": "RCH Construcción & Restauración", "Monto": 471_500_000, "Ganador": True},
                    {"Empresa": "Inspecciones Técnicas Centro SpA", "Monto": 476_000_000, "Ganador": False},
                    {"Empresa": "Ingeniería Patrimonial Andina SA", "Monto": 482_300_000, "Ganador": False},
                    {"Empresa": "Gestión de Obras del Maule Ltda.", "Monto": 490_000_000, "Ganador": False},
                ],
            },
        },
        {
            "CodigoExterno": "8934-61-LP25",
            "Nombre": "Puesta en Valor Palacio Rioja de Viña del Mar",
            "NombreOrganismo": "Ilustre Municipalidad de Viña del Mar",
            "Region": "V Región de Valparaíso",
            "MontoEstimado": 1_780_000_000,
            "Moneda": "CLP",
            "Estado": "adjudicada",
            "TipoLicitacion": "LP",
            "FechaPublicacion": (hoy - timedelta(days=175)).isoformat(),
            "FechaCierre": (hoy - timedelta(days=138)).isoformat(),
            "FechaAdjudicacion": (hoy - timedelta(days=92)).isoformat(),
            "Adjudicacion": {
                "EmpresaGanadora": "Ingeniería Patrimonial Andina SA",
                "RutGanador": "76.550.912-1",
                "MontoAdjudicado": 1_734_000_000,
                "NumeroOferentes": 5,
                "Oferentes": [
                    {"Empresa": "Ingeniería Patrimonial Andina SA", "Monto": 1_734_000_000, "Ganador": True},
                    {"Empresa": "Constructora Aconcagua Ltda.", "Monto": 1_755_000_000, "Ganador": False},
                    {"Empresa": "RCH Construcción & Restauración", "Monto": 1_768_500_000, "Ganador": False},
                    {"Empresa": "Restauraciones Patrimoniales del Sur SpA", "Monto": 1_782_000_000, "Ganador": False},
                    {"Empresa": "Constructora del Pacífico SA", "Monto": 1_810_000_000, "Ganador": False},
                ],
            },
        },
    ]


def detalle_demo(codigo: str) -> dict:
    """Devuelve un detalle ampliado para una licitación demo."""
    base = next(
        (lic for lic in licitaciones_demo() if lic["CodigoExterno"] == codigo),
        None,
    )
    if not base:
        return {}

    base = dict(base)
    base.update(
        {
            "Etapas": {
                "FechaInicio": base["FechaPublicacion"],
                "FechaCierre": base["FechaCierre"],
                "FechaPublicacionRespuestas": "Por definir",
                "FechaActoApertura": base["FechaCierre"],
                "FechaEstimadaAdjudicacion": "Por definir",
            },
            "GarantiaSeriedad": {
                "Tipo": "Boleta bancaria, póliza o vale vista",
                "Monto": int(base["MontoEstimado"] * 0.03),
                "Vigencia": "120 días",
                "Beneficiario": base["NombreOrganismo"],
            },
            "GarantiaFielCumplimiento": {
                "Porcentaje": "5% del monto adjudicado",
                "Vigencia": "Plazo de obra + 60 días",
            },
            "CriteriosEvaluacion": [
                {"Nombre": "Oferta económica", "Ponderacion": 50},
                {"Nombre": "Experiencia del oferente", "Ponderacion": 30},
                {"Nombre": "Equipo profesional", "Ponderacion": 18},
                {"Nombre": "Programa de integridad", "Ponderacion": 2},
            ],
            "EquipoProfesionalMinimo": [
                "Profesional responsable (ingeniero civil o arquitecto)",
                "Inspector técnico residente",
                "Especialista estructural",
                "Prevencionista de riesgos",
            ],
            "ContactoOrganismo": {
                "Nombre": "Por definir",
                "Email": f"contacto@{base['NombreOrganismo'].lower().replace(' ', '')}.cl",
                "Telefono": "Por definir",
            },
            "UrlMercadoPublico": (
                f"https://www.mercadopublico.cl/Procurement/Modules/RFB/"
                f"DetailsAcquisition.aspx?idlicitacion={base['CodigoExterno']}"
            ),
        }
    )
    return base
