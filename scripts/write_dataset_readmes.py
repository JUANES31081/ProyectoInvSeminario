"""
Fase 1 (V2) - Generador de README.md de consumo por dataset.

Lee la metadata curada del Excel (Datasets_Unicos) + inspecciona los archivos
realmente descargados en datasets/DescargasDataManualmente/<key>/data/ para
producir un README.md que explique que es cada archivo y como se debe consumir,
segun la documentacion del autor/pagina oficial de cada dataset.

Uso:
    python scripts/write_dataset_readmes.py
    python scripts/write_dataset_readmes.py --only SisFall,UMAFall
"""
from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_DIR = ROOT / "datasets" / "DescargasDataManualmente"

# Metadata curada desde docs/Revision_Articulos_Deteccion_Caidas-v3.xlsx (hoja Datasets_Unicos)
META = {
    "SisFall": dict(
        resumen="38 sujetos (23 jovenes, 15 mayores), 19 a 75 anios, 19F/19M. ADL reales en ancianos + caidas simuladas.",
        adl="19 tipos de ADL (2,707 muestras).",
        caidas="15 tipos de caidas (1,798 muestras).",
        ensayos="1 a 5 ensayos por actividad (15 s cada uno).",
        sensores="2 acelerometros triaxiales + 1 giroscopio.",
        ubicacion="Cintura / cinturon.",
        frecuencia="200 Hz.",
        unidades="Aceleracion (g / LSB) y velocidad angular (deg/s) en 3 ejes (X,Y,Z).",
        ids="Sujeto (SA01-SA23 jovenes, SE01-SE15 mayores) y Actividad (D01-D19 ADL, F01-F15 caidas).",
        formato="Archivos .txt / CSV (dentro de SisFall.zip: una carpeta por sujeto, un .txt por ensayo).",
        consumo=(
            "1. Descomprimir `SisFall.zip` dentro de `data/`.\n"
            "2. Cada carpeta de sujeto (ej. `SA01`) contiene archivos `D01_SA01_R01.txt`, ...\n"
            "   El prefijo (D0x = ADL, F0x = Fall) indica el tipo de actividad, y R0x el numero de ensayo.\n"
            "3. Cada fila del .txt trae: AccX, AccY, AccZ (acelerometro 1), GyroX, GyroY, GyroZ, AccX2, AccY2, AccZ2 "
            "(acelerometro 2), separados por coma; no incluyen timestamp explicito (frecuencia constante 200Hz).\n"
            "4. Revisar `Readme.txt`/tabla de actividades en el paper (MDPI Sensors 17(1):198, 2017) para el "
            "significado exacto de cada codigo Dxx/Fxx."
        ),
        cita="Sucerquia, A.; Lopez, J.D.; Vargas-Bonilla, J.F. SisFall: A Fall and Movement Dataset. Sensors 2017, 17, 198.",
    ),
    "UniMiB_SHAR": dict(
        resumen="30 sujetos sanos, 18-60 anios (media 27±11), 24F/6M. Caidas simuladas sobre colchoneta.",
        adl="9 tipos de ADL (7,579 muestras / 5,314 ventanas de 1s).",
        caidas="8 tipos de caidas (4,192 muestras / 1,699 ventanas de 1s).",
        ensayos="Multiples ensayos por sujeto.",
        sensores="Smartphone Samsung Galaxy Nexus (acelerometro Bosch BMA220).",
        ubicacion="Bolsillo del pantalon (muslo izquierdo y derecho).",
        frecuencia="50 Hz (remuestreado a frecuencia constante).",
        unidades="Aceleracion en m/s^2 en 3 ejes (X,Y,Z) + magnitud.",
        ids="ID sujeto, genero, edad, peso, altura, etiqueta de actividad.",
        formato="MATLAB (.mat) y CSV (.csv), dentro de UniMiB-SHAR.zip.",
        consumo=(
            "1. Descomprimir `UniMiB-SHAR.zip` dentro de `data/`.\n"
            "2. Los archivos `.mat` principales estan en la carpeta `data/`: `acc_data.mat` (señales completas), "
            "`full_data.mat`, y archivos de etiquetas (`acc_labels.mat`, etc). Cargar con `scipy.io.loadmat`.\n"
            "3. Cada ventana es un vector de longitud fija (acelerometro remuestreado); las etiquetas indican "
            "la clase de actividad/caida y el sujeto.\n"
            "4. Ver `description.pdf`/paper para el mapeo exacto clase->indice."
        ),
        cita="Micucci, D.; Mobilio, M.; Napoletano, P. UniMiB SHAR: A Dataset for Human Activity Recognition Using "
             "Acceleration Data from Smartphones. Applied Sciences 2017, 7, 1101.",
    ),
    "KFall": dict(
        resumen="32 sujetos jovenes coreanos (100% masculino), 20-30 anios. Caidas simuladas sobre colchoneta con video 90Hz.",
        adl="21 tipos de ADL (2,729 movimientos).",
        caidas="15 tipos de caidas (2,346 movimientos; 5,075 archivos en total).",
        ensayos="5 ensayos por tarea dinamica (1 estatica).",
        sensores="IMU triaxial de 9 ejes (acelerometro, giroscopio, angulos de Euler).",
        ubicacion="Espalda baja / zona lumbar (L5).",
        frecuencia="100 Hz.",
        unidades="Acc (g), Gyro (deg/s), Euler (deg) en 3 ejes.",
        ids="Sujeto (SA01-SA32), Tarea (T01-T36), Trial (R01-R05), frame de onset/impacto de la caida.",
        formato="CSV (datos inerciales) + Excel (anotaciones de onset/impacto).",
        consumo=(
            "1. Descargado via mirror de Kaggle (`usmanabbasi2002/kfall-dataset`) en `data/`.\n"
            "2. Cada CSV corresponde a una combinacion Sujeto-Tarea-Trial; el nombre de archivo codifica SAxx/Txx/Rxx.\n"
            "3. Los archivos de anotacion en Excel marcan el frame de inicio (onset) y de impacto de cada caida; "
            "cruzar por Sujeto+Tarea+Trial.\n"
            "4. La fuente oficial (formulario Google Sites) puede tener una version mas completa/curada; "
            "solicitar acceso si se requiere trazabilidad total al paper original."
        ),
        cita="Yu, X. et al. KFall: A Comprehensive Motion Dataset to Detect Pre-Impact Falls. 2021 (ver sitio oficial).",
    ),
    "FallAllD": dict(
        resumen="15 participantes, 21-53 anios, 7F/8M. Caidas y ADL simuladas.",
        adl="44 tipos de ADL (4,883 muestras).",
        caidas="35 tipos de caidas (1,722 muestras; 26,420 archivos en total).",
        ensayos="Ensayos repetidos por sujeto.",
        sensores="3 motes inerciales RF-Track (LSM9DS1: acel/giro/mag; MS5607: barometro).",
        ubicacion="Cintura, muñeca y cuello.",
        frecuencia="238 Hz (acelerometro/giroscopio).",
        unidades="Acc (g), Gyro (deg/s), Mag (uT), Presion (hPa).",
        ids="ID sujeto, ID dispositivo (Waist/Wrist/Neck), ID actividad.",
        formato="CSV, MATLAB (.mat), HDF5 (.h5), Pickle (.pkl) + videos (segun fuente).",
        consumo=(
            "1. Descargado via mirror de Kaggle (`shusrith/fallalld`) en `data/`.\n"
            "2. El nombre de cada archivo codifica sujeto, dispositivo (Waist/Wrist/Neck) y actividad/caida.\n"
            "3. La version oficial en IEEE DataPort trae ademas los `.mat`/`.h5`/`.pkl` estructurados con metadata; "
            "el mirror de Kaggle puede variar el formato exacto - validar columnas al cargar.\n"
            "4. Requiere cuenta IEEE DataPort para la version 100% oficial (no disponible en este proyecto)."
        ),
        cita="Saleh, M.; Le Bouquin Jeannes, R. FallAllD: An Open Dataset of Human Falls and Activities of Daily "
             "Living for Classical and Deep Learning Applications. IEEE Sensors J. 2021.",
    ),
    "UP-Fall": dict(
        resumen="17 sujetos jovenes sanos (8F/9M), 18-24 anios. Caidas simuladas, 3 ensayos por actividad.",
        adl="6 tipos de ADL (304 muestras).",
        caidas="5 tipos de caidas (255 muestras; 559 ensayos en total).",
        ensayos="3 ensayos por actividad por sujeto.",
        sensores="5 IMUs (acel, giro, luz), 1 EEG MindWave, 6 sensores IR, 2 camaras HD.",
        ubicacion="Tobillo, muslo/bolsillo, cintura, cuello, muñeca izquierda.",
        frecuencia="18 Hz (IMUs).",
        unidades="Acc (g), Gyro (rad/s), luminosidad, EEG, video RGB/Optical Flow.",
        ids="Carpeta Sujeto (1-17) -> Carpeta Actividad (1-11) -> Carpeta Trial (1-3) -> CSV.",
        formato="CSV, binario e imagenes/video (segun paquete descargado).",
        consumo=(
            "1. `DataSet_complete.zip`: todos los datos sincronizados de sensores (IMUs, EEG, IR), organizados por "
            "Sujeto/Actividad/Trial (columnas descritas en el sitio oficial: Timestamp, IMU tobillo, IMU bolsillo "
            "derecho, IMU cintura, IMU cuello, IMU muñeca, EEG NeuroSky, 6 sensores infrarrojos).\n"
            "2. `Features_X_Y_complete.zip`: caracteristicas ya extraidas de los datos crudos con separacion X seg "
            "y ventana Y seg (listas para ML tabular, sin necesidad de procesar señales crudas).\n"
            "3. `CameraResizedOF_complete.csv` y `CameraOFFeatures_X_Y_complete.csv`: Optical Flow de ambas camaras "
            "ya resumido/redimensionado (20x20) o promediado como feature — utiles para vision sin descargar "
            "las imagenes crudas.\n"
            "4. Las imagenes/video crudos de cada camara (`CameraX`, `CameraX_OF` por cada una de las 561 "
            "combinaciones Sujeto-Actividad-Trial) NO se incluyeron aqui por volumen. Se pueden descargar "
            "puntualmente desde el selector en https://sites.google.com/up.edu.mx/har-up/ (seccion Downloads).\n"
            "5. Sujeto 8, actividad 11, trials 2 y 3: datos faltantes (reportado por los autores)."
        ),
        cita="Martinez-Villasenor, L. et al. UP-Fall Detection Dataset: A Multimodal Approach. Sensors 2019, 19, 1988.",
    ),
    "UMAFall": dict(
        resumen="19 sujetos, 18-68 anios, 8F/11M. Caidas simuladas.",
        adl="12 tipos de ADL (538 muestras / 7,401 ventanas de 2s).",
        caidas="3 tipos de caidas (208 muestras / 384 ventanas de 2s; 746 ensayos en total).",
        ensayos="3 a 18 ensayos por actividad.",
        sensores="Smartphone (acel, giro, mag) + 4 motes vestibles (acel, giro, mag).",
        ubicacion="Tobillo, pecho, muslo, cintura y muñeca.",
        frecuencia="20 Hz (IMUs vestibles) / 100 Hz (smartphone).",
        unidades="g, m/s^2, deg/s, uT en 3 ejes.",
        ids="Nombre de archivo: Dataset_SubjectXX_ActivityXX_TrialXX.csv.",
        formato="Texto / CSV.",
        consumo=(
            "1. Descargado directamente desde Figshare (articulo 4214283) en `data/`: incluye "
            "`UMAFall_Dataset.zip` (version original) y `UMAFall_Dataset_corrected_version.zip` (version corregida "
            "recomendada), ademas de `videos_ADL.zip` y `videos_FALL.zip`.\n"
            "2. Cada CSV trae cabecera con lineas iniciadas en `%` (metadatos del ensayo); deben ignorarse al "
            "contar filas de medicion reales.\n"
            "3. El nombre del archivo codifica sujeto/actividad/trial; usar la version 'corrected' para analisis, "
            "salvo que se necesite reproducir resultados con la version original.\n"
            "4. Los videos (`videos_ADL.zip`/`videos_FALL.zip`) son opcionales y pesados; solo se requieren para "
            "validacion visual, no para el pipeline inercial."
        ),
        cita="Casilari, E.; Santoyo-Ramon, J.A.; Cano-Garcia, J.M. UMAFall: A Multisensor Dataset for the Research "
             "on Automatic Fall Detection. Procedia Computer Science 2017.",
    ),
    "WEDA_Fall": dict(
        resumen="25 sujetos (14 jovenes, 11 mayores >80 anios). Simuladas en jovenes / ADL reales en mayores.",
        adl="11 tipos de ADL (5,921 ventanas de 2s).",
        caidas="8 tipos de caidas (1,335 ventanas de 2s).",
        ensayos="3 a 4 ensayos por actividad.",
        sensores="Smartwatch Fitbit Sense (acelerometro, giroscopio).",
        ubicacion="Exclusivamente muñeca (wrist).",
        frecuencia="50 Hz (armonizado a 18 Hz).",
        unidades="Aceleracion (g) y velocidad angular (rad/s) en 3 ejes.",
        ids="SubjectXX_ActivityXX_TrialXX.",
        formato="CSV.",
        consumo=(
            "1. Repositorio de GitHub `joaojtmarques/WEDA-FALL` (identificado por busqueda web, el Excel solo "
            "citaba la publicacion MDPI sin URL) descargado y extraido en `data/`.\n"
            "2. Revisar el `README.md` del repositorio para la estructura exacta de carpetas por sujeto/actividad.\n"
            "3. Dataset exclusivo de muñeca (wrist); ideal para comparar contra datasets de cintura/muslo (SisFall, "
            "UP-Fall) en escenarios de smartwatch."
        ),
        cita="Publicacion: Sensors 2023, 23(24), 9888 (WEDA-FALL: A Dataset of Fall and ADL Simulated Movements).",
    ),
    "TST_Fall_v1": dict(
        resumen="4 actores jovenes, 22-39 anios. Caidas simuladas frente a Kinect v1 (vista superior).",
        adl="10 tests de caminata/actividad en area monitoreada.",
        caidas="10 tests de caidas simuladas (20 tests en total).",
        ensayos="Multiples ensayos por actor.",
        sensores="Microsoft Kinect v1 (top-view).",
        ubicacion="Sensor ambiental montado en techo.",
        frecuencia="30 fps (frames de profundidad).",
        unidades="Mapas de profundidad 3D (coordenadas X,Y,Z).",
        ids="Test_1_10.zip, Test_11_20.zip.",
        formato="ZIP con archivos binarios de profundidad.",
        consumo="No descargado (requiere suscripcion IEEE DataPort). Ver `URL.txt` para la fuente oficial.",
        cita="Gasparrini, S. et al. TST Fall Detection Dataset v1. IEEE DataPort.",
    ),
    "TST_Fall_v2": dict(
        resumen="11 actores jovenes, 22-39 anios. Caidas simuladas con Kinect v2 + IMU en cintura.",
        adl="4 tipos de ADL (132 muestras).",
        caidas="4 tipos de caidas (132 muestras; 264 ensayos en total).",
        ensayos="3 ensayos por actividad.",
        sensores="Microsoft Kinect v2 (Depth + Skeleton) + IMU Shimmer en cintura.",
        ubicacion="Cintura (IMU) y sensor ambiental Kinect.",
        frecuencia="100 Hz (IMU) / 30 fps (Kinect).",
        unidades="g (acelerometro) + coordenadas articulares del esqueleto.",
        ids="Data1.zip a Data11.zip por actor.",
        formato="ZIP con archivos .txt y .csv.",
        consumo="No descargado (requiere suscripcion IEEE DataPort). Ver `URL.txt` para la fuente oficial. "
                "Alternativa publica: TST_Fall_Modificado (Zenodo).",
        cita="Gasparrini, S. et al. TST Fall Detection Dataset v2. IEEE DataPort.",
    ),
    "TST_Fall_Modificado": dict(
        resumen="4 a 11 sujetos (basado en TST original). Version modificada por Unicomfacauca.",
        adl="4 tipos de ADL.",
        caidas="4 tipos de caidas (504 archivos .avi extraidos).",
        ensayos="Procesamiento por fotogramas.",
        sensores="Imagenes de profundidad y vision preprocesadas de Kinect.",
        ubicacion="Vision por computador / profundidad.",
        frecuencia="30 fps.",
        unidades="Fotogramas procesados para CNN / video .avi.",
        ids="Carpetas etiquetadas por clase de movimiento.",
        formato="Archivos de video .avi y matrices procesadas.",
        consumo=(
            "1. Descargado desde Zenodo (record 3961894) en `data/` (repositorio "
            "`Fall-Detection-Dataset-Modification`), como `Fall-Detection-Dataset-Modification.rar`.\n"
            "2. Python no incluye soporte nativo para `.rar`; extraer con 7-Zip/WinRAR (o `pip install rarfile` "
            "+ binario `unrar`) antes de procesar.\n"
            "3. Los .avi estan organizados en carpetas por clase de movimiento (caida/ADL); usar OpenCV "
            "(`cv2.VideoCapture`) para leer frame a frame.\n"
            "4. Es una version modificada del TST original (no oficial 1:1); util para prototipos de vision, "
            "no para reproducir resultados publicados con el TST oficial."
        ),
        cita="Zenodo record 3961894 (modificacion del TST Fall Detection Dataset, Unicomfacauca).",
    ),
    "UNIVRFall": dict(
        resumen="39 participantes (29 laboratorio + 10 obra real), 20-49 anios. Caidas simuladas + reales en obra.",
        adl="24 tipos de ADL (46.05 horas totales).",
        caidas="21 tipos de caidas (incl. 6 en altura/andamios; 573 eventos).",
        ensayos="Ensayos estructurados con fotogramas etiquetados.",
        sensores="IMU en chaqueta de seguridad Protechto s.r.l. (acel, giro, orientacion).",
        ubicacion="Torso / chaqueta de seguridad.",
        frecuencia="Alta frecuencia inercial (no especificada exacta).",
        unidades="Acc (m/s^2), Gyro (rad/s), Euler (deg) en 3 ejes.",
        ids="S[ID]T[Task]R[Rep].csv (datos) + SA[ID]_label.xlsx (onset/impacto).",
        formato="CSV (sensores) + Excel (anotaciones).",
        consumo=(
            "1. Descargado desde Zenodo (record 18346755) en `data/`.\n"
            "2. Cruzar cada CSV `S[ID]T[Task]R[Rep].csv` con su archivo `SA[ID]_label.xlsx` para obtener el "
            "frame/timestamp exacto de onset e impacto de la caida.\n"
            "3. Incluye tanto caidas simuladas en laboratorio como caidas reales registradas en obra de "
            "construccion (mayor validez ecologica que datasets 100% simulados)."
        ),
        cita="Publicado en Zenodo (2026), UNIVRFall dataset.",
    ),
    "SmartFallMM": dict(
        resumen="Sujetos jovenes y adultos mayores. Multimodal: esqueleto + inercial.",
        adl="9 tipos de ADL (Drinking, Pick, Jacket, Step, Sweep, Wash, Wave, TUG, Sit/Stand).",
        caidas="5 tipos de caidas (Back, Front, Left, Right, Rotate).",
        ensayos="Multiples ensayos guiados.",
        sensores="32 articulaciones de esqueleto + acelerometro/giroscopio en smartwatch y cadera (Meta sensors).",
        ubicacion="Muñeca (watch) y cadera (Meta sensors).",
        frecuencia="50 Hz (Meta sensors) / 32 Hz (Phone/Watch) / 30 fps (esqueleto).",
        unidades="Epoch (ms), time, elapsed time (s), X, Y, Z.",
        ids="CSV por participante y actividad (ej. S51, S29, S38); nombre SID+AID+TID (ej. S01A10T05).",
        formato="CSV sin cabecera.",
        consumo=(
            "1. Repositorio de GitHub `txst-cs-smartfall/SmartFallMM-Dataset` descargado y extraido en `data/` "
            "(carpetas `young/` y `old/`, con subcarpetas Accelerometer/Gyroscope/Skeleton por dispositivo).\n"
            "2. Meta sensors: 6 columnas sin cabecera (epoch, time, elapsed, x, y, z) a 50Hz.\n"
            "3. Phone/Watch: 4 columnas sin cabecera (time, x, y, z) a 32Hz.\n"
            "4. Skeleton: 96 columnas sin cabecera (32 articulaciones x 3 coordenadas) a 30fps; el video fuente "
            "no se distribuye por privacidad.\n"
            "5. Revisar la lista de 'Multimodal-Ready Subjects' en el README del repo (sujetos con datos "
            "completos en las 3 modalidades) antes de entrenar modelos multimodales."
        ),
        cita="Alamgeer, S. et al. SmartFallMM: A Multimodal Dataset for Fall Detection Using Commodity Devices. IEEE (ver GitHub).",
    ),
    "FARSEEING": dict(
        resumen=">2,000 monitoreados (208 caidas reales verificadas / 22 publicas). 56-86 anios.",
        adl="Trazas continuas de 24h de vida cotidiana.",
        caidas="208 caidas reales procesadas y verificadas.",
        ensayos="Monitoreo continuo a largo plazo.",
        sensores="Acelerometro triaxial (100%), giroscopio y magnetometro (58%).",
        ubicacion="Zona lumbar L5 (72%) y muslo (28%).",
        frecuencia="100 Hz (73%) o 20 Hz (27%).",
        unidades="Acc (m/s^2), Gyro (deg/s), Mag (uT) en 3 ejes.",
        ids="Random ID, numero de caida, marca temporal.",
        formato="MATLAB (.mat) estandarizado.",
        consumo="No descargado: acceso exclusivamente por solicitud formal a comite cientifico FARSEEING "
                "(http://www.farseeingresearch.eu). No automatizable con las credenciales disponibles.",
        cita="Klenk, J. et al. The FARSEEING real-world fall repository. Eur Rev Aging Phys Act 2016.",
    ),
    "MobiAct": dict(
        resumen="66 sujetos, 20-47 anios, 15F/51M. ADL en vida libre + caidas simuladas.",
        adl="12 tipos de ADL (>2,500 ensayos).",
        caidas="4 tipos de caidas (647 caidas; >3,200 ensayos en total).",
        ensayos="Multiples ensayos por actividad.",
        sensores="Smartphone (acelerometro, giroscopio, orientacion).",
        ubicacion="Muslo (bolsillo delantero del pantalon).",
        frecuencia="50 Hz a 200 Hz.",
        unidades="m/s^2, rad/s, angulos en 3 ejes.",
        ids="ID de sujeto, genero, edad, peso, altura.",
        formato="CSV.",
        consumo="No descargado: el portal oficial (bmi.hmu.gr) no respondio de forma estable durante el intento "
                "automatizado. Solicitar acceso via bmi@hmu.gr o repetir el intento cuando el sitio este disponible.",
        cita="Vavoulas, G. et al. The MobiAct Dataset. ICT4AWE 2016.",
    ),
    "MobiFall": dict(
        resumen="24 sujetos, 22-47 anios, 7F/17M. Caidas simuladas.",
        adl="9 tipos de ADL (342 muestras).",
        caidas="4 tipos de caidas (288 muestras).",
        ensayos="Multiples ensayos.",
        sensores="Smartphone (acelerometro, giroscopio, orientacion).",
        ubicacion="Muslo (bolsillo).",
        frecuencia="50 Hz.",
        unidades="m/s^2, rad/s en 3 ejes.",
        ids="ID de sujeto y codigo de ensayo.",
        formato="CSV.",
        consumo="No descargado: mismo portal que MobiAct (bmi.hmu.gr), sin respuesta estable durante el intento "
                "automatizado.",
        cita="Vavoulas, G. et al. The MobiFall Dataset. IEEE BIBE 2013.",
    ),
    "Graz_UT_OL": dict(
        resumen="5 sujetos. Caidas simuladas por artistas marciales.",
        adl="10 tipos de ADL (2,240 muestras).",
        caidas="4 tipos de caidas (220 muestras; 2,460 en total).",
        ensayos="Ensayos repetidos.",
        sensores="Smartphone (acelerometro, orientacion), 5 modelos de dispositivo distintos.",
        ubicacion="Cintura (riñonera).",
        frecuencia="5 Hz (frecuencia reducida).",
        unidades="+/-2g (Acc), +/-360 deg (Orientacion).",
        ids="Sujeto y etiqueta de actividad.",
        formato="SQLite / CSV.",
        consumo=(
            "1. Descargado directamente desde Figshare (articulo 1444405) en `data/`: "
            "`dataset-falls-and-ADL.sqlite`.\n"
            "2. Abrir con `sqlite3`/`pandas.read_sql`; contiene 13 tablas: `DEVICE_ALL_ACCELERATION`, "
            "`DEVICE_ALL_ORIENTATION`, `DEVICE_{modelo}_ACCELERATION`/`_ORIENTATION` por cada uno de los 5 "
            "telefonos, y `MANUAL_LABELS` (actividades etiquetadas manualmente).\n"
            "3. Aceleracion en m/s^2 (sin gravedad) + magnitud total; orientacion en azimuth/pitch/roll (grados); "
            "timestamps en epoch ms. Cruzar por timestamp con `MANUAL_LABELS` para obtener la etiqueta de "
            "actividad/caida de cada tramo."
        ),
        cita="Wertner, A.; Pammer, V.; Czech, P. Dataset for Mobile Phone Sensing Based Fall Detection. Figshare 2015.",
    ),
    "UR_Fall_Detection": dict(
        resumen="6 sujetos, >26 anios, 0F/6M. Caidas simuladas.",
        adl="5 tipos de ADL (40 muestras).",
        caidas="4 tipos de caidas (30 muestras; 70 en total).",
        ensayos="Multiples ensayos.",
        sensores="Acelerometro inercial + 2 Kinects (RGB + Depth).",
        ubicacion="Cintura (acelerometro) y camaras de entorno.",
        frecuencia="256 Hz (acelerometro) / 30 fps (Kinect).",
        unidades="g, mapas de profundidad 3D, imagenes RGB.",
        ids="Sequence_ID, Subject_ID.",
        formato="CSV (inercial) + imagenes PNG/ZIP (vision).",
        consumo=(
            "1. Descargados automaticamente los CSV inerciales desde "
            "http://fenix.ur.edu.pl/~mkepski/ds/data/ en `data/`: `adl-XX-data.csv`, `adl-XX-acc.csv`, "
            "`fall-XX-data.csv`, `fall-XX-acc.csv` (XX = numero de secuencia) + `urfall-cam0-falls.csv` / "
            "`urfall-cam0-adls.csv` (metadatos por frame de las secuencias de camara).\n"
            "2. Los `*-data.csv` traen columnas: timestamp, actividad etiquetada, coordenadas del bounding box "
            "de la persona (segun camara), y datos inerciales sincronizados. Los `*-acc.csv` traen unicamente la "
            "señal cruda del acelerometro a 256Hz.\n"
            "3. Las imagenes RGB/Depth completas (ZIP pesados por secuencia) no se descargaron por volumen; "
            "estan disponibles en la misma ruta base para descarga puntual si se necesita el componente de vision."
        ),
        cita="Kepski, M.; Kwolek, B. UR Fall Detection Dataset. Univ. of Rzeszow.",
    ),
    "DOFDA": dict(
        resumen="8 sujetos, 22-29 anios, 2F/6M. Caidas simuladas.",
        adl="1 tipo de ADL (120 muestras).",
        caidas="5 tipos de caidas (312 muestras; 432 en total).",
        ensayos="Ensayos estructurados.",
        sensores="IMU triaxial (acel, giro, mag, orientacion).",
        ubicacion="Cintura.",
        frecuencia="33 Hz.",
        unidades="g, deg/s, uT, angulos de orientacion.",
        ids="ID de sujeto y ensayo.",
        formato="CSV.",
        consumo="No descargado: el Excel solo cita la publicacion (Data in Brief, Elsevier 2019) sin URL de "
                "datos; no se encontro repositorio publico de descarga directa.",
        cita="Data in Brief (Elsevier), 2019 (DOFDA dataset).",
    ),
    "Erciyes_University": dict(
        resumen="17 sujetos, 19-27 anios, 7F/10M. Caidas simuladas.",
        adl="16 tipos de ADL (1,476 muestras).",
        caidas="20 tipos de caidas (1,821 muestras; 3,297 en total).",
        ensayos="Ensayos multiples.",
        sensores="6 IMUs externas (acelerometro, giroscopio, magnetometro).",
        ubicacion="Cabeza, pecho, cintura, muñeca, muslo, tobillo.",
        frecuencia="25 Hz.",
        unidades="Acc (g), Gyro (deg/s), Mag (uT).",
        ids="Sujeto, movimiento y repeticion.",
        formato="Texto (.txt) / MATLAB (.mat).",
        consumo="No descargado: el Excel solo cita la publicacion (Erciyes University / MDPI Sensors 2014) sin "
                "URL de datos; no se encontro repositorio publico de descarga directa.",
        cita="Ozdemir, A.T.; Barshan, B. Detecting Falls with Wearable Sensors Using Machine Learning Techniques. "
             "Sensors 2014, 14, 10691.",
    ),
    "IMUFD": dict(
        resumen="10 sujetos, 20-30 anios. Caidas simuladas (incluye near-falls).",
        adl="13 tipos de ADL (390 muestras).",
        caidas="7 tipos de caidas (210 muestras; 600 en total).",
        ensayos="3 ensayos por actividad.",
        sensores="7 IMUs externas.",
        ubicacion="Cabeza, pecho, cintura, muslos y tobillos.",
        frecuencia="128 Hz.",
        unidades="g, deg/s, uT en 3 ejes.",
        ids="ID de sujeto y sensor.",
        formato="CSV / texto.",
        consumo="No descargado: acceso publico/por solicitud segun el Excel (Simon Fraser University IPML Lab); "
                "sin URL de descarga directa disponible.",
        cita="Simon Fraser University, Intelligent Prosthetics and Mobility Lab (IPML).",
    ),
    "DLR": dict(
        resumen="19 sujetos, 23-52 anios, 8F/11M. Caidas simuladas.",
        adl="15 tipos de ADL (961 muestras).",
        caidas="1 tipo de caida (56 muestras; 1,017 en total).",
        ensayos="Ensayos libres y guiados.",
        sensores="1 IMU triaxial externa (acel, giro, mag).",
        ubicacion="Cintura (cinturon).",
        frecuencia="100 Hz.",
        unidades="+/-5g (Acel), +/-1200 deg/s (Giro), +/-75uT (Mag).",
        ids="ID de sujeto.",
        formato="Texto / log.",
        consumo="No descargado: por solicitud / restringido segun el Excel (German Aerospace Center - DLR); "
                "sin URL de descarga directa disponible.",
        cita="German Aerospace Center (DLR), dataset de caidas de referencia en literatura.",
    ),
    "FFFStudy": dict(
        resumen="34 sujetos (25 en archivos publicos), 33-76 anios. Adultos con esclerosis multiple.",
        adl=">11,000 horas de vida diaria continua.",
        caidas="49 caidas reales con timestamp.",
        ensayos="8 semanas continuas de monitoreo libre.",
        sensores="MotioSense MotioWear tag sensors (acelerometro).",
        ubicacion="Cintura / bolsillo del pantalon.",
        frecuencia="50 Hz.",
        unidades="+/-8g en 3 ejes.",
        ids="ID de participante, marca temporal del impacto.",
        formato="Texto / CSV.",
        consumo="No descargado: el Excel no trae URL de datos (solo cita IEEE JBHI / Veterans Affairs Portland); "
                "busqueda web no encontro repositorio publico de descarga directa.",
        cita="IEEE Journal of Biomedical and Health Informatics (FFFStudy, Veterans Affairs Portland).",
    ),
    "LTMM": dict(
        resumen="71 sujetos, 65-87 anios, 46F/25M. Adultos mayores de la comunidad. SIN caidas registradas.",
        adl="4,494.68 horas de monitoreo continuo de movilidad.",
        caidas="0 caidas (dataset de marcha/movilidad, no de eventos de caida).",
        ensayos="3 dias continuos por sujeto.",
        sensores="DynaPort MiniMod (acelerometro, giroscopio).",
        ubicacion="Cintura / espalda baja.",
        frecuencia="100 Hz.",
        unidades="+/-6g, giroscopio.",
        ids="Sujeto_ID, timestamp.",
        formato="Binario (MIT/PhysioNet .dat+.hea) / CSV.",
        consumo=(
            "1. El Excel no traia URL; se identifico por busqueda web que el dataset real esta en PhysioNet: "
            "https://physionet.org/content/ltmm/1.0.0/ (documentado en `URL.txt` con provenance [web]).\n"
            "2. Aqui solo se descargaron los metadatos/indice: `ClinicalDemogData_COFL.xlsx` (datos clinicos y "
            "demograficos por sujeto), `ReportHome75h.xlsx` (bitacora de uso del sensor), `RECORDS` (indice de "
            "señales) y `SHA256SUMS.txt`.\n"
            "3. Las señales completas (.dat/.hea por sujeto, formato MIT/WFDB, ~300MB cada una, 71 sujetos, "
            "20.8GB en total) NO se descargaron dado que este dataset reporta 0 caidas (solo sirve para "
            "riesgo de caida / marcha, no para clasificar eventos de caida). Si se requieren para features de "
            "marcha, descargar con:\n"
            "   `wget -r -N -c -np https://physionet.org/files/ltmm/1.0.0/`\n"
            "   o el ZIP completo: https://physionet.org/content/ltmm/get-zip/1.0.0/\n"
            "4. Leer las señales con la libreria `wfdb` de Python (`wfdb.rdrecord('CO001')`)."
        ),
        cita="Weiss, A. et al. Does the Evaluation of Gait Quality During Daily Life Provide Insight Into Fall "
             "Risk? Neurorehabil Neural Repair 2013. Dataset: PhysioNet LTMM, DOI 10.13026/C2S59C.",
    ),
    "Smartphone_Human_Fall_Dataset": dict(
        resumen="No especificado (dataset de comunidad Kaggle). Caidas simuladas.",
        adl="9 tipos de ADL (1,017 muestras tabulares).",
        caidas="4 tipos de caidas (767 muestras tabulares; 1,784 en total).",
        ensayos="Separado en Train.csv (80%) y Test.csv (20%).",
        sensores="Smartphone (acelerometro, giroscopio).",
        ubicacion="Muslo / bolsillo.",
        frecuencia="No especificada (caracteristicas ya extraidas).",
        unidades="Aceleracion y velocidad angular tabulares (12 caracteristicas).",
        ids="Fila independiente (sin ID de sujeto).",
        formato="CSV.",
        consumo=(
            "1. Descargado via Kaggle (`saadmansakib/smartphone-human-fall-dataset`) en `data/`.\n"
            "2. Dataset ya tabular/feature-level: usar `Train.csv`/`Test.csv` directamente para clasificacion "
            "(no requiere procesamiento de señal cruda)."
        ),
        cita="Kaggle: saadmansakib/smartphone-human-fall-dataset.",
    ),
    "Falls_vs_Normal_Activities": dict(
        resumen="No especificado (dataset de comunidad Kaggle). Caidas simuladas.",
        adl="3 tipos de ADL (sit, step, walk).",
        caidas="4 tipos de caidas (fall, lfall, rfall, light).",
        ensayos="96,800 filas continuas (~242 observaciones).",
        sensores="Acelerometro y giroscopio triaxial.",
        ubicacion="Cintura / muslo.",
        frecuencia="No especificada.",
        unidades="xAcc, yAcc, zAcc, xGyro, yGyro, zGyro.",
        ids="Fila continua con label.",
        formato="CSV.",
        consumo=(
            "1. Descargado via Kaggle (`enricogrimaldi/falls-vs-normal-activities`) en `data/`.\n"
            "2. Es una serie temporal continua con columna de etiqueta por fila; segmentar por cambios de label "
            "para obtener observaciones/eventos individuales."
        ),
        cita="Kaggle: enricogrimaldi/falls-vs-normal-activities.",
    ),
    "Elderly_Fall_Detection_IoT": dict(
        resumen="Sintetico / prototipo IoT para adultos mayores.",
        adl="Non-fall: Walking, sitting, standing, bending, lying.",
        caidas="Fall: Forward, backward, sideways, slumping.",
        ensayos="Time-series sincronizadas (25,552 filas).",
        sensores="Multimodal (acelerometro, giroscopio, orientacion + sensores de suelo/presion).",
        ubicacion="Wearable + entorno IoT.",
        frecuencia="Alta frecuencia simulada.",
        unidades="accel_x/y/z, gyro_x/y/z, pitch, roll, sensores ambiente.",
        ids="sequence_id, timestep.",
        formato="CSV (CC0).",
        consumo=(
            "1. Descargado via Kaggle (`ziya07/elderly-fall-detection-iot-dataset`) en `data/`.\n"
            "2. Datos sinteticos (no de sujetos reales); util para prototipado rapido de pipelines, no para "
            "resultados clinicos/publicables sin validacion adicional."
        ),
        cita="Kaggle: ziya07/elderly-fall-detection-iot-dataset (CC0).",
    ),
    "Real_Time_Patient_Fall_Detection": dict(
        resumen="Sintetico / prototipo de paciente.",
        adl="ADLs simuladas de paciente.",
        caidas="Eventos de caida simulados (1,000 filas).",
        ensayos="1,000 observaciones.",
        sensores="Multisensor wearable + contexto (acel, giro, frecuencia cardiaca, contexto de habitacion).",
        ubicacion="Wearable + habitacion.",
        frecuencia="No especificada.",
        unidades="Acelerometria, frecuencia cardiaca, ubicacion.",
        ids="Patient_ID.",
        formato="CSV.",
        consumo=(
            "1. Descargado via Kaggle (`zara2099/real-time-patient-fall-detection-data`) en `data/`.\n"
            "2. Datos sinteticos/community; usar principalmente para pruebas de pipeline, no como fuente "
            "cientifica primaria."
        ),
        cita="Kaggle: zara2099/real-time-patient-fall-detection-data.",
    ),
    "Ultralytics_Fall_Detect": dict(
        resumen="Comunidad de vision artificial. Imagenes de personas caidas/no caidas.",
        adl="Personas de pie, sentadas, caminando.",
        caidas="Personas caidas en el suelo (3 clases anotadas).",
        ensayos="475 imagenes anotadas (Train=364, Val=111).",
        sensores="Camaras RGB (imagenes/frames).",
        ubicacion="Camara fija de vision por computador.",
        frecuencia="N/A (imagenes estaticas).",
        unidades="Bounding boxes (formato YOLO).",
        ids="Image ID / Annotation ID.",
        formato="NDJSON / imagenes + labels YOLO.",
        consumo="No descargado: la plataforma Ultralytics requiere inicio de sesion para habilitar el "
                "export/descarga de imagenes y labels; no automatizable sin credenciales.",
        cita="Ultralytics Platform, dataset comunitario fall-detect (nicolai-nielsen).",
    ),
}


def list_data_files(folder: Path) -> str:
    data_dir = folder / "data"
    if not data_dir.exists():
        return "_(sin archivos descargados; ver seccion de consumo/URL.txt)_"

    all_files = [p for p in data_dir.rglob("*") if p.is_file()]
    if not all_files:
        return "_(sin archivos descargados; ver seccion de consumo/URL.txt)_"

    total_size_mb = sum(p.stat().st_size for p in all_files) / (1024 * 1024)

    # Resumen por sub-carpeta directa de data/ (o "." si el archivo esta en la raiz)
    by_top: dict[str, list[Path]] = {}
    for p in all_files:
        rel = p.relative_to(data_dir)
        top = rel.parts[0] if len(rel.parts) > 1 else "."
        by_top.setdefault(top, []).append(p)

    lines = [f"Total: {len(all_files)} archivos, {total_size_mb:.1f} MB.\n"]
    for top, files in sorted(by_top.items()):
        size_mb = sum(p.stat().st_size for p in files) / (1024 * 1024)
        if top == ".":
            for p in sorted(files):
                lines.append(f"- `{p.name}` ({p.stat().st_size / (1024*1024):.1f} MB)")
        elif len(files) <= 8:
            lines.append(f"- `{top}/` ({len(files)} archivos, {size_mb:.1f} MB)")
            for p in sorted(files):
                lines.append(f"  - `{p.relative_to(data_dir)}` ({p.stat().st_size / (1024*1024):.1f} MB)")
        else:
            examples = ", ".join(f"`{p.name}`" for p in sorted(files)[:3])
            lines.append(f"- `{top}/` ({len(files)} archivos, {size_mb:.1f} MB) - ej: {examples}, ...")
    return "\n".join(lines)


def render_readme(key: str, meta: dict, folder: Path) -> str:
    files_section = list_data_files(folder)
    return f"""# {key}

## Resumen
{meta['resumen']}

## Composicion
- ADL: {meta['adl']}
- Caidas: {meta['caidas']}
- Ensayos/repeticiones: {meta['ensayos']}

## Sensores
- Tipo: {meta['sensores']}
- Ubicacion corporal: {meta['ubicacion']}
- Frecuencia de muestreo: {meta['frecuencia']}
- Unidades/ejes: {meta['unidades']}
- Identificadores: {meta['ids']}
- Formato de almacenamiento: {meta['formato']}

## Archivos en `data/`
{files_section}

## Como consumir este dataset
{meta['consumo']}

## Cita
{meta['cita']}

## Fuente
Ver `URL.txt` en esta misma carpeta.
"""


def main(only: list | None = None) -> None:
    targets = only or list(META.keys())
    for key in targets:
        if key not in META:
            print(f"[skip] sin metadata: {key}")
            continue
        folder = BASE_DIR / key
        folder.mkdir(parents=True, exist_ok=True)
        content = render_readme(key, META[key], folder)
        (folder / "README.md").write_text(content, encoding="utf-8")
        print(f"[ok] README.md escrito para {key}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", help="lista separada por comas de keys de datasets")
    args = parser.parse_args()
    only = [s.strip() for s in args.only.split(",")] if args.only else None
    main(only)
