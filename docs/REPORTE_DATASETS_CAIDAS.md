# Reporte de Datasets de Caidas (Wearables y Multimodal)

Fecha de corte: 2026-08-28

## Alcance y criterio

Este reporte consolida datasets con acceso actual verificado (fuente oficial o mirror publico), priorizando los datasets de la tabla inicial y agregando opciones adicionales utiles para investigacion y prototipado.

Actualizacion importante:
- Se validaron shapes reales para datasets locales y Kaggle descargables.
- Se agregaron referencias de carpeta local para los datasets descargados.
- La columna "Tamano aprox." se reemplazo por "Registros (filas/cols)".

Escala usada:
- Calidad estimada: Alta, Media-Alta, Media, Baja-Media.
- Riesgo de mirror: Bajo, Medio, Alto.

## Tabla comparativa reorganizada

### 1) Datasets descargados (ordenados por completitud de columnas)

| Dataset | ADL/Caidas (tipos) | Muestras (ADL/Caidas) | Registros (filas/cols) | Sensores/modalidad | Fuente principal | Enlace fuente | Acceso actual | Carpeta local (referencia) | Calidad estimada | Riesgo de mirror |
|---|---:|---:|---|---|---|---|---|---|---|---|
| UR Fall Detection | 5/4 | 40/30 (70 total) | CSV locales descargados automaticamente: 142; total filas CSV: 45814; incluye fall/adl data+acc y urfall-cam0-falls/adls | A + camaras RGB/Depth | Sitio oficial UR | http://fenix.ur.edu.pl/~mkepski/ds/uf.html | Publico (automatizable para CSV tabular) | datasets/dataset_downloads/UR_Fall_Detection/ | Alta (dataset academico clasico) | Bajo |
| UP-Fall | 6/5 | 304/255 (559 total) | Ver detalle local: 8 CSV; ejemplo CompleteDataSet.csv = (294679, 47), CameraResizedOF.csv = (17378, 805) | Multimodal: A, G, luz, IR, EEG, camaras | Sitio oficial HAR-UP | https://sites.google.com/up.edu.mx/har-up/ | Publico | datasets/UP-Fall/ | Alta | Bajo |
| SisFall | 19/15 | 2707/1798 (4505 total) | CSV detectados: 4275; total filas CSV: 6907663; muestra: (5401, 10) | A, G (inercial) | Mirror Kaggle | https://www.kaggle.com/datasets/thevman/sisfall-dataset | Publico (mirror) | datasets/dataset_downloads/thevman__sisfall-dataset/ | Alta (muy usado en literatura) | Medio |
| UMAFall | 8/3 | 322/209 (531 total) | CSV detectados: 1492; total filas CSV: 9376668; columnas: 7 fijas; muestra: (6562, 7) | A, G, M | Figshare oficial | https://figshare.com/articles/dataset/UMA_ADL_FALL_Dataset_zip/4214283 | Publico | datasets/dataset_downloads/UMAFall_Figshare/ | Alta | Bajo |
| UniMiB SHAR | 9/8 | 5314/1699 (7013 total) | CSV detectados: 3; total filas CSV: 1777421; muestra: (177727, 7) | A (smartphone) | Mirror Kaggle | https://www.kaggle.com/datasets/wangboluo/unimib-shar-dataset | Publico (mirror) | datasets/dataset_downloads/UniMiB_SHAR/ | Alta-Media | Medio |
| Graz (Mobile Phone Sensing Based Fall Detection) | 10/4 | 2240/220 (2460 total) | SQLite descargado: total filas (sumando tablas) = 637892; muestra tabla DEVICE_ALL_ACCELERATION = (159300, 6) | A, O | Figshare oficial | https://figshare.com/articles/dataset/Dataset_for_Mobile_Phone_Sensing_Based_Fall_Detection/1444405 | Publico | datasets/dataset_downloads/Graz_Figshare/ | Media-Alta | Bajo |
| Smartphone Human Fall Dataset | 9/4 (13 clases totales) | Balanceado reportado: 1017 no-caida / 767 caida | CSV detectados: 2; total filas CSV: 1784; muestra: (356, 12) | A, G (features tabulares) | Kaggle | https://www.kaggle.com/datasets/saadmansakib/smartphone-human-fall-dataset | Publico | datasets/dataset_downloads/saadmansakib__smartphone-human-fall-dataset/ | Media | Medio-Alto |
| Falls vs Normal Activities | 3 ADL + 4 caidas (7 clases) | ~242 observaciones (reportado por autor) | CSV detectados: 1; total filas CSV: 96800; muestra: (96800, 7) | A, G (6 ejes) | Kaggle | https://www.kaggle.com/datasets/enricogrimaldi/falls-vs-normal-activities | Publico | datasets/dataset_downloads/enricogrimaldi__falls-vs-normal-activities/ | Media | Medio-Alto |
| TST Fall detection (modificado) | 4/4 | 132/132 (264 total) | Extraido localmente: 504 archivos .avi en 9 carpetas de clase; no aplica shape tabular CSV | Principalmente vision (segun version) | Zenodo (modificado Unicomfacauca) | https://zenodo.org/records/3961894 | Publico | datasets/dataset_downloads/TST_Fall_Modified_Zenodo/ | Media (no siempre version original) | Medio |
| KFall (mirror Kaggle) | N/D | N/D | CSV detectados: 5075; total filas CSV: 3995100; muestra: (3072, 11) | A, G, M (reportado por mirror) | Kaggle | https://www.kaggle.com/datasets/usmanabbasi2002/kfall-dataset | Publico (mirror) | datasets/dataset_downloads/usmanabbasi2002__kfall-dataset/ | Media | Medio-Alto |
| FallAllD (mirror Kaggle) | N/D | N/D | CSV detectados: 5078; total filas CSV: 4101091; muestra: (6605, 9) | Inercial (segun mirror) | Kaggle | https://www.kaggle.com/datasets/shusrith/fallalld | Publico (mirror) | datasets/dataset_downloads/shusrith__fallalld/ | Media | Medio-Alto |
| Elderly Fall Detection IoT | N/D | N/D | CSV detectados: 2; total filas CSV: 25552; muestra: (552, 5) | Wearable + ambiente IoT (A, G, orientacion, sensores de entorno) | Kaggle | https://www.kaggle.com/datasets/ziya07/elderly-fall-detection-iot-dataset | Publico | datasets/dataset_downloads/ziya07__elderly-fall-detection-iot-dataset/ | Media | Alto |
| Real-Time Patient Fall Detection | N/D | N/D | CSV detectados: 1; total filas CSV: 1000; muestra: (1000, 15) | Multisensor wearable + contexto (A, G, FC, room context) | Kaggle | https://www.kaggle.com/datasets/zara2099/real-time-patient-fall-detection-data | Publico | datasets/dataset_downloads/zara2099__real-time-patient-fall-detection-data/ | Baja-Media (mas community dataset) | Alto |

### 2) Datasets que requieren descarga manual

| Dataset | ADL/Caidas (tipos) | Muestras (ADL/Caidas) | Registros (filas/cols) | Sensores/modalidad | Fuente principal | Enlace fuente | Acceso actual | Carpeta local (referencia) | Calidad estimada | Riesgo de mirror |
|---|---:|---:|---|---|---|---|---|---|---|---|
| tFall | 7/8 | 9883/1026 (10909 total) | NDJSON local detectado: 475 imagenes anotadas (train=364, val=111), task=detect, 3 clases (class0/class1/class2); faltan activos completos por export/login | Vision (imagenes) | Ultralytics community | https://platform.ultralytics.com/nicolai-nielsen/datasets/fall-detect | Publico (community, export con login) | datasets/dataset_downloads/tFall_Ultralytics/ | Media | Alto |

### 3) Datasets que requieren acceso por solicitud

| Dataset | ADL/Caidas (tipos) | Muestras (ADL/Caidas) | Registros (filas/cols) | Sensores/modalidad | Fuente principal | Enlace fuente | Acceso actual | Carpeta local (referencia) | Calidad estimada | Riesgo de mirror |
|---|---:|---:|---|---|---|---|---|---|---|---|
| MobiAct | 9/4 (tabla original) | 1879/647 (tabla original) | N/D (acceso por solicitud) | A, G, O | Grupo BMI (HMU) | mailto:bmi@hmu.gr | Solicitud | N/D | Alta-Media | Bajo |
| DLR | 15/1 (tabla original) | 1017/56 (tabla original) | N/D (sin descarga publica automatizada) | A, G, M | Referencia en literatura | N/D | Solicitud/uso restringido | N/D | Media | Bajo |
| Cogent Labs | 8/6 (tabla original) | 1520/448 (tabla original) | N/D (acceso por solicitud a autores/publicacion) | A, G | Publicacion / ResearchGate | https://www.researchgate.net/ | Solicitud | N/D | Media | Medio |
| Gravity Project | 7/12 (tabla original) | 45/72 (tabla original) | N/D (sin repositorio publico estable) | A | Referencia en literatura | N/D | Solicitud | N/D | Media | Medio |

## Como intentar descargar los manuales

1. tFall
	- URL: https://platform.ultralytics.com/nicolai-nielsen/datasets/fall-detect
	- Accion: iniciar sesion en Ultralytics, abrir el dataset y usar la opcion Export/Download en el formato disponible (YOLO/imagenes/labels).
	- Nota: sin autenticacion no habilita descarga automatizada.

2. Recomendacion de organizacion para manuales
	- Guardar cada descarga en su carpeta dedicada dentro de dataset_downloads.
	- Mantener un SOURCE_PATH.txt con la URL exacta y fecha de descarga.
	- Si el dataset es video/imagen y no CSV, registrar metrica por cantidad de archivos y clases (como ya se hizo con TST).

## Descarga automatizada recomendada para UR (ya validada)

- Base util confirmada: https://fenix.ur.edu.pl/~mkepski/ds/data/
- Archivos descargables por script: fall-XX-data.csv, fall-XX-acc.csv, adl-XX-data.csv, adl-XX-acc.csv y urfall-cam0-falls.csv / urfall-cam0-adls.csv.
- Resultado local actual: 142 CSV descargados automaticamente (sin bajar todavia los ZIP pesados de imagen/depth).

## Observaciones importantes

1. En varios mirrors, los conteos de ADL/caidas y el formato pueden cambiar por preprocesamientos del autor que subio el mirror.
2. Para entrenamiento final en tesis/publicacion, se recomienda priorizar fuentes oficiales o mirrors con trazabilidad clara al paper original.
3. Datasets con riesgo alto son utiles para exploracion y prototipos, pero conviene auditar su procedencia antes de resultados concluyentes.
4. Sobre UP-Fall: lo que tienes localmente corresponde a un subconjunto tabular/feature-level (8 CSV). No representa automaticamente el universo completo del sitio oficial (imagenes completas por camara y otros paquetes multimodales de gran volumen).

## Evidencia generada en este proyecto

- Validacion local UP-Fall (shapes por archivo): analytics/upfall_local_shapes.csv
- Validacion de datasets Kaggle descargados y shapes consolidados: analytics/dataset_shapes_validation.csv
- Resolucion de faltantes publicos (ronda 1): analytics/missing_public_datasets_downloads.csv
- Resolucion de faltantes publicos (ronda 2): analytics/missing_public_datasets_downloads_round2.csv
- Intento espejo UR via GitHub: analytics/ur_mirror_attempt.csv
- Metricas post-descompresion (UMAFall/TST/UR): analytics/post_unzip_metrics.csv
- Prueba de rutas automatizables UR: analytics/ur_download_probe.csv
- Log de descarga automatica UR (CSV): analytics/ur_csv_download_log.csv
- Shapes de CSV descargados de UR: analytics/ur_csv_shapes.csv
- Referencias locales de descarga: carpeta datasets/dataset_downloads/ (cada dataset contiene SOURCE_PATH.txt apuntando al cache real)

## Enlaces principales usados

- UP-Fall oficial: https://sites.google.com/up.edu.mx/har-up/
- UR Fall Detection oficial: http://fenix.ur.edu.pl/~mkepski/ds/uf.html
- TST modificado en Zenodo: https://zenodo.org/records/3961894
- SisFall mirror: https://www.kaggle.com/datasets/thevman/sisfall-dataset
- KFall mirror: https://www.kaggle.com/datasets/usmanabbasi2002/kfall-dataset
- FallAllD mirror: https://www.kaggle.com/datasets/shusrith/fallalld
- Real-Time Patient Fall: https://www.kaggle.com/datasets/zara2099/real-time-patient-fall-detection-data
- Elderly Fall Detection IoT: https://www.kaggle.com/datasets/ziya07/elderly-fall-detection-iot-dataset
- Smartphone Human Fall Dataset: https://www.kaggle.com/datasets/saadmansakib/smartphone-human-fall-dataset
- Falls vs Normal Activities: https://www.kaggle.com/datasets/enricogrimaldi/falls-vs-normal-activities

## Campos recomendados para extender este reporte

- Licencia exacta.
- DOI o cita canonical.
- URL de respaldo (fuente alternativa).
- Split sugerido (train/val/test) y si trae etiquetas limpias.
- Prioridad de uso (Alta, Media, Baja) segun tu objetivo experimental.

