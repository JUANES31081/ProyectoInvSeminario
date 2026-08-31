# ProyectoGrado - Datasets de Caidas

Repositorio para inventario, validacion y analitica de datasets de deteccion de caidas (wearables y multimodal).

## Estructura

- `datasets/`
  - `UP-Fall/`: subconjunto local UP-Fall en CSV.
  - `dataset_downloads/`: descargas y mirrors de datasets.
- `analytics/`: salidas CSV/JSON generadas por notebook/scripts.
- `docs/`: documentacion y reportes.
- `datasets_caidas_mejorado.ipynb`: notebook principal.
- `dataset_catalog_utils.py`: utilidades para catalogo y validacion.

## Archivos clave

- Reporte principal: `docs/REPORTE_DATASETS_CAIDAS.md`
- Referencias y notas: `docs/Helper.md`
- Evidencias analiticas: carpeta `analytics/`

## Puesta en marcha

1. Crear/activar entorno virtual Python.
2. Instalar dependencias: `pip install -r requirements.txt`.
3. Copiar `.env_example` a `.env` y completar si aplica.
4. Abrir y ejecutar `datasets_caidas_mejorado.ipynb` (la primera celda crea la estructura de carpetas).

Los datos no se versionan en Git: al clonar el repo, las carpetas `datasets/` y
`analytics/` se regeneran ejecutando el notebook.

## Convenciones

- Toda data cruda o descargada va en `datasets/`.
- Todo resultado de analitica va en `analytics/`.
- Toda documentacion en Markdown va en `docs/`.

## Notas

- UR Fall Detection se puede descargar automaticamente en CSV desde `https://fenix.ur.edu.pl/~mkepski/ds/data/`.
- Para tFall (Ultralytics), el archivo `fall-detect.ndjson` contiene metadatos + registros de imagen; la exportacion completa requiere login.

## Licencia y uso academico

Este repositorio se distribuye bajo **CC BY-NC-SA 4.0** (ver `LICENSE`).

- Se permite usarlo como base para otras investigaciones, citando la fuente.
- No se permite el uso comercial sin autorizacion previa.
- Las obras derivadas deben mantener la misma licencia.
- Investigacion **en curso**: los resultados son preliminares y pueden cambiar.

Los datasets de terceros conservan sus propias licencias: ver `docs/DATA_LICENSES.md`.

## Como citar

Ver `CITATION.cff`. Cita sugerida:

> Juan E. (JUANES31081). "Proyecto de Investigacion - Datasets de Deteccion de Caidas
> (Wearables y Multimodal)". Universidad EAN, 2026.
> https://github.com/JUANES31081/ProyectoInvSeminario
