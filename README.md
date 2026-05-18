# Sistema de Análisis de Licitaciones · RCH

MVP en Streamlit para descubrir, evaluar y dar seguimiento a licitaciones públicas chilenas del rubro construcción y restauración patrimonial.

## ¿Qué hace?

1. **Explorar** licitaciones publicadas en Mercado Público con filtros por palabras clave, monto, región y fecha.
2. **Scorear** automáticamente cada licitación contra el perfil RCH (rubro, monto, región, palabras clave, plazo).
3. **Pipeline** de seguimiento con estados: descubierta → evaluada → en preparación → presentada → adjudicada / desierta.
4. **Análisis con IA**: subir el PDF de las bases y obtener un análisis estructurado con la API de Claude (presupuesto, criterios, equipo profesional, garantías, multas, riesgos y recomendación).
5. **Dashboard** con KPIs, distribución por estado y región, y cierres próximos.
6. **Configuración** de criterios de scoring personalizables.

## Estructura del proyecto

```
licitaciones_mvp/
├── app.py                      Aplicación Streamlit (navegación + páginas)
├── api_mercado_publico.py      Cliente de la API de Chilecompra
├── analisis_ia.py              Integración con Claude API
├── data_store.py               Persistencia en JSON (pipeline y configuración)
├── demo_data.py                Datos de demostración (licitaciones ficticias)
├── scoring.py                  Cálculo del score de pertinencia
├── requirements.txt            Dependencias Python
├── .streamlit/config.toml      Tema visual RCH
└── data/                       Datos del usuario (generado en tiempo de ejecución)
    ├── pipeline.json
    └── configuracion.json
```

## Instalación local

Requiere Python 3.10 o superior.

```bash
# 1. Crear y activar entorno virtual
python -m venv venv
source venv/bin/activate          # Linux/Mac
venv\Scripts\activate             # Windows

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar la app
streamlit run app.py
```

La aplicación queda disponible en `http://localhost:8501`.

## Credenciales (opcionales)

### Ticket de Mercado Público

- Solo necesario para consultar licitaciones reales en vivo.
- Sin ticket, el sistema funciona en **modo demostración** con datos ficticios.
- Obtención: registro en [mercadopublico.cl](https://www.mercadopublico.cl) → Mis tickets en el panel de desarrolladores.

### API key de Claude (Anthropic)

- Solo necesaria para el análisis automático de bases en PDF.
- Sin API key, el módulo de análisis muestra un resultado demostrativo.
- Obtención: [console.anthropic.com](https://console.anthropic.com) → API Keys.

Ambas credenciales se ingresan en la barra lateral de la app. **No se guardan en disco**; se mantienen solo en la sesión activa del navegador.

## Despliegue

### Opción 1: Streamlit Community Cloud (gratis)

1. Subir el proyecto a un repositorio de GitHub.
2. Conectar la cuenta en [share.streamlit.io](https://share.streamlit.io).
3. Seleccionar el repositorio y `app.py` como entry point.

### Opción 2: Railway

1. Crear proyecto en [railway.app](https://railway.app) → New Project → Deploy from GitHub.
2. Railway detecta `requirements.txt` automáticamente.
3. Variables de entorno (opcional): no se requieren porque las credenciales se ingresan en la UI.
4. En *Settings → Networking* generar dominio público.

### Opción 3: Render

1. Crear servicio web en [render.com](https://render.com) → New → Web Service.
2. Build command: `pip install -r requirements.txt`
3. Start command: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`

## Flujo de uso recomendado

1. **Primera vez:** ir a *Configuración* y definir palabras clave, rangos de monto y regiones de interés.
2. **Rutina diaria:** abrir *Explorar Licitaciones*, hacer clic en *Buscar*, revisar las licitaciones con score sobre 70 y agregar las relevantes al pipeline.
3. **Análisis profundo:** para cada licitación priorizada, descargar las bases desde Mercado Público y subirlas a *Análisis con IA*. El resultado queda asociado a la licitación en el pipeline.
4. **Seguimiento:** mover licitaciones por los estados del pipeline a medida que avanzan en el proceso interno.
5. **Reportes mensuales:** revisar *Dashboard* para tasas de adjudicación y montos en gestión.

## Roadmap sugerido

- Migrar persistencia a SQLite o PostgreSQL para multiusuario.
- Notificaciones automáticas (email o WhatsApp) cuando se publican licitaciones con score alto.
- Crawler programado diario (Celery + Redis) para precargar licitaciones del día.
- Integración con módulos internos RCH (planilla de itemizado, APU, propuestas).
- Comparador de competencia (qué empresas ganan licitaciones similares).
- Exportación a Word/PDF de informes de pertinencia (con formato RCH).

## Notas técnicas

- La persistencia en JSON es adecuada para un MVP de un solo usuario. Para producción con varios usuarios concurrentes, migrar a una base relacional.
- La API de Mercado Público es pública pero requiere ticket y tiene límites de uso. Para uso intensivo, considerar consumir los datasets diarios disponibles en el portal de datos abiertos.
- Los costos de la API de Claude por análisis de un PDF de bases típico (30–80 páginas) están en el orden de USD 0,15 a 0,40 según modelo.

---

RCH · Construcción & Restauración Patrimonial
