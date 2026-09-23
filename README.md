# electricity-forecast — Predicción del precio de la luz con ML

Proyecto 4 del portfolio [Portfolio backend Python](../README_v9.md): ciclo completo
de un modelo de Machine Learning (no solo consumo de IA generativa), usando como base
el histórico generado por [electricity-pipeline](../electricity-pipeline) (Proyecto 2).

## Objetivo

Predecir el precio del mercado eléctrico spot/OMIE de un día concreto (D+2) a partir
del histórico de precio, calendario y clima — demostrando el flujo completo de un
proyecto de ML aplicado: EDA, ingeniería de features, entrenamiento, evaluación y,
más adelante, servido vía API.

## Decisiones de diseño

### Tipo de problema: regresión, no clasificación

Se predice el valor numérico del precio (€/MWh), no una etiqueta barata/cara. Una vez
resuelta la regresión, derivar una clasificación aplicando un umbral sobre la
predicción numérica es casi gratis; al revés no se puede recuperar la información
perdida. Clasificación queda como extensión futura planificada, no descartada.

### Horizonte de predicción: D+2, sin fuga de información

El modelo predice el día **D+2** (pasado mañana), usando solo datos disponibles hasta
D+1. Motivo: tanto el PVPC como el spot del día siguiente (D+1) ya son públicos y
ciertos desde que REE los publica sobre las 20:15h del día anterior — un modelo que
"prediga" un valor ya publicado no demuestra capacidad predictiva real. El horizonte
D+2 encaja además con la cadencia diaria ya automatizada del Proyecto 2 (el cron
recoge el D+1 real a las 21:00h de D; el modelo predice D+2, que en ese momento aún es
desconocido). Validación natural: 24h después, cuando el cron recoge el D+2 real, se
compara contra la predicción hecha el día anterior.

### Target: precio spot/OMIE, no PVPC

El PVPC se calcula a partir del spot más términos regulados (peajes, servicios de
ajuste, bono social...) que ningún feature de clima/demanda/calendario puede
anticipar — entrenar sobre PVPC mezclaría señal de mercado con ruido administrativo.
El spot además tiene granularidad cuarto-horaria (96 valores/día vs. 24 del PVPC, x4
más filas de entrenamiento con el mismo histórico) y conecta con la visión ya
planteada del Proyecto 5 (aproximar la tarifa real del usuario como spot + margen).
Extensión futura aceptada: derivar una estimación de PVPC a partir de la predicción de
spot, no al revés.

### Variables externas desde el principio

Clima y demanda eléctrica se incluyen desde el inicio, no se difieren — el verdadero
reto técnico del proyecto es el pipeline de features (alinear temporalmente series de
fuentes distintas sin fuga de datos del futuro), no solo el algoritmo de ML.

- **Clima**: [AEMET OpenData](https://opendata.aemet.es/) (gratuita, requiere API Key
  propia). Predicción horaria por municipio (Rivas-Vaciamadrid, código INE `28123`)
  para D+2; histórico diario por estación meteorológica (Arganda del Rey, `3182Y`,
  municipio colindante) para el backfill. Ver más abajo el matiz de granularidad.
- **Demanda**: la API REData/apidatos (ya usada en el Proyecto 2) no ofrece previsión
  de demanda, solo indicadores reales/históricos. Se incorpora como feature de *lag*
  (demanda real de D o D-1), no como previsión — evita bloquear el proyecto con la API
  ESIOS (que quizá sí la tenga, pero requiere un token no explorado). Previsión real
  de demanda vía ESIOS queda como mejora futura documentada.

### Granularidad del clima: todo a nivel diario

AEMET tiene dos endpoints con distinta granularidad: predicción horaria (por
municipio) frente a histórico diario (por estación). Para garantizar consistencia
entre entrenamiento e inferencia, **toda** la señal de clima se baja a granularidad
diaria (la predicción horaria de D+2 también se agrega a un único valor diario antes
de usarla) — se sacrifica matiz horario del clima, aceptable porque la temperatura
varía mucho menos intradía que el precio de la luz, y la inconsistencia train/
inferencia es un error más grave que perder ese matiz.

### Base de datos compartida con el Proyecto 2

`electricity-forecast` reutiliza la misma instancia PostgreSQL del Proyecto 2
(`electricity_pipeline`), tanto para leer el histórico de precios como para escribir
su propia tabla `weather_records` — no se crea una base de datos separada. El mapa de
dependencias del portfolio ya asumía esta relación desde el principio; separar bases
de datos añadiría complejidad sin beneficio real. Implicación: ambos proyectos deben
coexistir en cualquier entorno donde se quiera reproducir este.

### Unidades: siempre €/MWh en el dato, €/kWh solo en presentación

Igual que en el Proyecto 2, el precio se trabaja y almacena siempre en €/MWh. La
conversión a €/kWh (más legible) se aplica únicamente en la capa de visualización
final, nunca en la fuente de datos ni en el dataset de entrenamiento.

## Stack

- Python 3.12+, `uv` como gestor de dependencias
- `pandas`, `numpy` para transformación de datos
- `scikit-learn` para el modelo (pendiente)
- `SQLAlchemy` + `psycopg[binary]` para persistencia en PostgreSQL (compartida con el Proyecto 2)
- `pydantic` / `pydantic-settings` para validación y configuración
- `requests` para las integraciones con AEMET y REData
- `jupyter`, `matplotlib`, `seaborn` (dependencias de desarrollo) para EDA

## Estructura del proyecto

```
electricity-forecast/
├── src/electricity_forecast/
│   ├── config.py          # Settings (DB, API keys AEMET)
│   ├── features.py        # Lags de precio + calendario cíclico (seno/coseno)
│   ├── weather_client.py  # Cliente AEMET (predicción horaria + histórico diario)
│   ├── schemas.py         # Modelos Pydantic (WeatherRecord)
│   ├── models.py          # Modelos ORM SQLAlchemy (WeatherRecordModel)
│   ├── transform.py       # Parseo/limpieza de la respuesta de AEMET
│   └── load.py            # Persistencia (upsert) en PostgreSQL
├── notebooks/
│   └── 01_eda_precios.ipynb
├── .env.example
└── pyproject.toml
```

## Configuración

Copia `.env.example` a `.env` y rellena:

```dotenv
DATABASE_URL=postgresql+psycopg://usuario:password@localhost:5432/electricity_pipeline
AEMET_API_KEY=tu-api-key-de-aemet-opendata
AEMET_MUNICIPIO_ID=28123
```

La API Key de AEMET se solicita gratis en
https://opendata.aemet.es/centrodedescargas/altaUsuario — llega por email.

**Requisito previo:** este proyecto necesita la base de datos PostgreSQL del Proyecto
2 (`electricity-pipeline`) levantada y con histórico de precios cargado.

## Estado actual (sept. 2026): EN DESARROLLO

- ✅ EDA completo sobre PVPC (~20 días de histórico): patrón horario con doble pico
  asimétrico (pico suave 6h-8h, pico dominante 18h-22h) y valle solar 11h-17h; 9 de
  480 horas con precio negativo real; diferencia laborable/fin de semana (~198 vs.
  ~145 €/MWh)
- ✅ `features.py`: lags de precio (24h/48h/168h, indexados por tiempo real con
  `reindex`, no por posición, para ser robustos ante huecos/cambios de hora) y
  codificación cíclica seno/coseno de hora del día y día de la semana
- ✅ `weather_client.py`: predicción horaria por municipio y valores climatológicos
  diarios por estación, ambos endpoints de AEMET (doble llamada: la primera petición
  devuelve una URL con los datos reales)
- ✅ `schemas.py` / `models.py` / `transform.py` / `load.py`: pipeline completo de
  clima histórico validado extremo a extremo con datos reales — parseo de decimales en
  formato español, manejo de campos ausentes por retraso de consolidación de AEMET
  (temperatura tiene su propio retraso, más largo que viento/precipitación), upsert
  idempotente en `weather_records`
- ✅ Backfill de clima histórico cargado (20 de 23 días — los 3 más recientes se
  recuperarán en una próxima ejecución, cuando AEMET los consolide)
- ⬜ Predicción horaria de AEMET agregada a diario (`is_real=False`) para D+2
- ⬜ Ensamblado de la tabla de entrenamiento final (precio + calendario + clima +
  demanda)
- ⬜ Split cronológico train/test (nunca aleatorio, en series temporales)
- ⬜ Baseline ingenuo (persistencia: precio de D+2 = precio de la misma hora en D+1) y
  modelo real (`RandomForestRegressor`/`GradientBoostingRegressor`)
- ⬜ Evaluación (MAE, RMSE) contra el baseline
- ⬜ API para servir el modelo (FastAPI, mismo patrón que el Proyecto 3)

## Lecciones técnicas destacadas

- **AEMET aplica rate limiting** (HTTP 429) si se hacen varias peticiones seguidas en
  poco tiempo — el endpoint de histórico diario confirma 50 peticiones/minuto.
- **AEMET publica con retraso de consolidación**, no al instante: tanto días
  completos (los últimos días recientes pueden faltar por completo) como campos
  individuales dentro de un día (`tmed`/`tmin`/`tmax` se consolidan más tarde que
  viento/precipitación). El diseño usa upsert como mecanismo de "reintento diferido":
  re-ejecutar el mismo backfill más adelante rellena los huecos sin duplicar filas.
- **`Base.metadata.create_all()` no altera tablas ya existentes** — un cambio de
  modelo (p. ej. añadir `nullable=True`) requiere recrear la tabla en desarrollo
  (`drop_all()` + `create_all()`) o una migración explícita en producción.
- Los lags de precio se calculan indexando por fecha real (`reindex` sobre el índice
  desplazado), no por posición (`shift()`), para ser robustos ante huecos en los datos
  y ante el cambio de hora español (días de 23/25 horas).

## Notas para el Proyecto 5

La base de datos de clima (`weather_records`) y el propio modelo entrenado servirán
como piezas reutilizables para la app integradora final, junto con el histórico de
precios del Proyecto 2 y el RAG del Proyecto 3.
