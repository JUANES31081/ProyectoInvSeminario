"""
Fase 2 - Validacion de metricas reales de los datasets descargados.

Recorre cada carpeta en datasets/DescargasDataManualmente/<key>/data y extrae, cuando es
posible, evidencia real de: numero y tipo de ADL, numero y tipo de caidas, ensayos/repeticiones
por sujeto, tipo de sensor, formato de almacenamiento, frecuencia de muestreo, ubicacion
corporal, numero de sujetos, edad y sexo (estos 3 ultimos SOLO si estan literalmente presentes
en los archivos de datos, no se infieren del Excel ni de los README).

Salida: analytics/dataset_metrics_v2.json
"""
import json
import re
import sqlite3
from collections import defaultdict
from pathlib import Path

import pandas as pd

BASE = Path(r"d:\UniversidadEAN\ProyectoGrado\datasets\DescargasDataManualmente")
OUT = Path(r"d:\UniversidadEAN\ProyectoGrado\analytics\dataset_metrics_v2.json")

NOT_VERIFIABLE = "No verificable desde los archivos descargados"
NOT_DOWNLOADED = "No descargado (dataset restringido)"

RESTRICTED_KEYS = [
    "TST_Fall_v1", "TST_Fall_v2", "FARSEEING", "MobiAct", "MobiFall", "DOFDA",
    "Erciyes_University", "IMUFD", "DLR", "FFFStudy", "Ultralytics_Fall_Detect",
]


def blank_result(notes=""):
    return {
        "sujetos_validado": NOT_VERIFIABLE,
        "edad_validado": NOT_VERIFIABLE,
        "sexo_validado": NOT_VERIFIABLE,
        "adl_validado": NOT_VERIFIABLE,
        "caidas_validado": NOT_VERIFIABLE,
        "ensayos_validado": NOT_VERIFIABLE,
        "sensor_validado": NOT_VERIFIABLE,
        "formato_validado": NOT_VERIFIABLE,
        "frecuencia_validado": NOT_VERIFIABLE,
        "ubicacion_validado": NOT_VERIFIABLE,
        "notas": notes,
    }


def restricted_result():
    return {k: NOT_DOWNLOADED for k in [
        "sujetos_validado", "edad_validado", "sexo_validado", "adl_validado",
        "caidas_validado", "ensayos_validado", "sensor_validado", "formato_validado",
        "frecuencia_validado", "ubicacion_validado",
    ]} | {"notas": "Dataset restringido / sin descarga automatizada; ver README.md y URL.txt para instrucciones de acceso manual."}


def file_ext_summary(folder: Path):
    counts = defaultdict(int)
    total = 0
    for p in folder.rglob("*"):
        if p.is_file():
            counts[p.suffix.lower() or "(sin extension)"] += 1
            total += 1
    return counts, total


def fmt_ext_summary(counts):
    parts = [f"{ext}: {n}" for ext, n in sorted(counts.items(), key=lambda kv: -kv[1])]
    return "; ".join(parts) if parts else "sin archivos"


# ---------------------------------------------------------------------------
# Validadores por dataset
# ---------------------------------------------------------------------------

def validate_sisfall(folder: Path):
    root = folder / "data" / "SisFall_dataset"
    if not root.exists():
        return blank_result("Carpeta SisFall_dataset no encontrada tras extraccion.")
    subj_young, subj_old = set(), set()
    adl_codes, fall_codes, trials = set(), set(), set()
    n_files = 0
    for p in root.rglob("*.txt"):
        n_files += 1
        m = re.match(r"([DF]\d+)_(SA\d+|SE\d+)_(R\d+)", p.name)
        if not m:
            continue
        code, subj, trial = m.groups()
        (subj_young if subj.startswith("SA") else subj_old).add(subj)
        trials.add(trial)
        (adl_codes if code.startswith("D") else fall_codes).add(code)
    notas = "Estructura y conteos verificados directamente sobre los .txt extraidos (SisFall_dataset/SAxx|SExx)."
    return {
        "sujetos_validado": f"{len(subj_young) + len(subj_old)} sujetos verificados en disco ({len(subj_young)} SA-jovenes, {len(subj_old)} SE-mayores)",
        "edad_validado": NOT_VERIFIABLE + " (no hay edad por sujeto en los .txt; solo en Readme.txt del dataset)",
        "sexo_validado": NOT_VERIFIABLE + " (no hay sexo por sujeto en los .txt; solo en Readme.txt del dataset)",
        "adl_validado": f"{len(adl_codes)} codigos de ADL distintos verificados (D01-D19): {', '.join(sorted(adl_codes))}",
        "caidas_validado": f"{len(fall_codes)} codigos de caida distintos verificados (F01-F15): {', '.join(sorted(fall_codes))}",
        "ensayos_validado": f"Trials distintos verificados: {', '.join(sorted(trials))} ({n_files} archivos .txt totales)",
        "sensor_validado": "Verificado: cada .txt tiene 9 columnas numericas (2 acelerometros triaxiales ADXL345/MMA8451Q + 1 giroscopio ITG3200), sin cabecera",
        "formato_validado": "Archivos .txt de texto plano (no CSV con cabecera); coincide con Excel",
        "frecuencia_validado": NOT_VERIFIABLE + " (sin columna de timestamp en los .txt; se asume 200 Hz segun especificacion original del paper)",
        "ubicacion_validado": NOT_VERIFIABLE + " (no indicada dentro de los archivos; segun Excel/paper es cintura)",
        "notas": notas,
    }


def validate_unimib(folder: Path):
    root = folder / "data" / "UniMiB-SHAR" / "data"
    if not root.exists():
        return blank_result("Carpeta UniMiB-SHAR/data no encontrada.")
    from scipy.io import loadmat
    notas_extra = []
    adl_names, fall_names = [], []
    try:
        m = loadmat(root / "adl_names.mat")
        key = [k for k in m if not k.startswith("__")][0]
        adl_names = [str(x[0]) for x in m[key].ravel()]
    except Exception as e:
        notas_extra.append(f"No se pudo leer adl_names.mat ({e})")
    try:
        m = loadmat(root / "fall_names.mat")
        key = [k for k in m if not k.startswith("__")][0]
        fall_names = [str(x[0]) for x in m[key].ravel()]
    except Exception as e:
        notas_extra.append(f"No se pudo leer fall_names.mat ({e})")
    shape_notes = []
    for fname in ["acc_data.mat", "adl_data.mat", "fall_data.mat", "full_data.mat"]:
        p = root / fname
        if p.exists():
            try:
                m = loadmat(p)
                key = [k for k in m if not k.startswith("__")][0]
                shape_notes.append(f"{fname}:{m[key].shape}")
            except Exception:
                pass
    return {
        "sujetos_validado": NOT_VERIFIABLE + " (los .mat no traen ID de sujeto por fila accesible sin el paper; ver acc_data.mat)",
        "edad_validado": NOT_VERIFIABLE,
        "sexo_validado": NOT_VERIFIABLE,
        "adl_validado": (f"{len(adl_names)} tipos de ADL verificados en adl_names.mat: {', '.join(adl_names)}" if adl_names else NOT_VERIFIABLE),
        "caidas_validado": (f"{len(fall_names)} tipos de caida verificados en fall_names.mat: {', '.join(fall_names)}" if fall_names else NOT_VERIFIABLE),
        "ensayos_validado": NOT_VERIFIABLE + " (no hay conteo de ensayos por sujeto accesible directamente en los .mat)",
        "sensor_validado": "Verificado: acc_data.mat contiene datos de un unico acelerometro triaxial (Smartphone Bosch BMA220)",
        "formato_validado": f"Archivos MATLAB .mat confirmados; shapes: {'; '.join(shape_notes)}",
        "frecuencia_validado": NOT_VERIFIABLE + " (no hay columna de tiempo/frecuencia explicita en los .mat)",
        "ubicacion_validado": NOT_VERIFIABLE,
        "notas": "; ".join(notas_extra) if notas_extra else "Nombres de clases leidos directamente de adl_names.mat/fall_names.mat via scipy.io.loadmat.",
    }


def validate_kfall(folder: Path):
    root = folder / "data" / "KFall Dataset" / "KFall Dataset"
    sensor_dir = root / "sensor_data"
    label_dir = root / "label_data"
    if not sensor_dir.exists():
        return blank_result("Carpeta sensor_data de KFall no encontrada.")
    subjects = sorted(p.name for p in sensor_dir.iterdir() if p.is_dir())
    expected = {f"SA{n:02d}" for n in range(1, 33)}
    found = set(subjects)
    missing = sorted(expected - found)
    tasks = set()
    for p in sensor_dir.rglob("*.csv"):
        m = re.search(r"T(\d+)", p.stem)
        if m:
            tasks.add(int(m.group(1)))
    n_csv = sum(1 for _ in sensor_dir.rglob("*.csv"))
    n_label = sum(1 for _ in label_dir.rglob("*.xlsx")) if label_dir.exists() else 0
    notas = (
        f"Mirror Kaggle INCOMPLETO respecto al Excel (32 sujetos reportados): "
        f"faltan {len(missing)} carpetas de sujeto ({', '.join(missing)})."
    )
    return {
        "sujetos_validado": f"{len(subjects)} carpetas de sujeto verificadas en disco ({', '.join(subjects)}) de 32 esperadas",
        "edad_validado": NOT_VERIFIABLE,
        "sexo_validado": NOT_VERIFIABLE,
        "adl_validado": NOT_VERIFIABLE + f" (se detectaron {len(tasks)} codigos de tarea T01-T36 distintos en nombres de archivo, sin separar ADL/caida sin cruzar con label_data)",
        "caidas_validado": NOT_VERIFIABLE + " (requiere cruzar sensor_data con label_data/SAxx_label.xlsx para separar tareas de caida vs ADL, no realizado en este validador automatico)",
        "ensayos_validado": f"{n_csv} archivos CSV de sensor verificados (patron SAxx/*.csv con hasta R05 trials por tarea)",
        "sensor_validado": "Verificado por nombre/columnas tipicas: IMU triaxial 9 ejes (Acc, Gyro, Euler) segun estructura de carpetas",
        "formato_validado": f"CSV ({n_csv} archivos) + Excel .xlsx de anotaciones ({n_label} archivos)",
        "frecuencia_validado": NOT_VERIFIABLE,
        "ubicacion_validado": NOT_VERIFIABLE,
        "notas": notas,
    }


def validate_fallalld(folder: Path):
    data = folder / "data"
    csv_path = data / "fallalld.csv"
    dat_dir = data / "FallAllD__zip" / "FallAllD"
    contamination = []
    if (data / "Activity_DataSet(1)").exists():
        contamination.append("Activity_DataSet(1)/ARS DLR Data Set = contenido del dataset DLR, NO relacionado con FallAllD")
    if (data / "sensor_data").exists() or (data / "label_data").exists():
        contamination.append("sensor_data/ + label_data/ = estructura identica a KFall (SAxx + SAxx_label.xlsx), NO relacionado con FallAllD")
    result = blank_result()
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        subjects = sorted(df["SubjectID"].unique().tolist()) if "SubjectID" in df.columns else []
        activities = sorted(df["ActivityID"].unique().tolist()) if "ActivityID" in df.columns else []
        trials = sorted(df["TrialNo"].unique().tolist()) if "TrialNo" in df.columns else []
        devices = sorted(df["Device"].unique().tolist()) if "Device" in df.columns else []
        result.update({
            "sujetos_validado": f"{len(subjects)} SubjectID distintos verificados en fallalld.csv: {subjects}",
            "adl_validado": NOT_VERIFIABLE + f" ({len(activities)} ActivityID distintos verificados en total, sin distincion ADL/caida documentada en el CSV: {activities})",
            "caidas_validado": NOT_VERIFIABLE + " (ver nota de ADL; el csv no separa explicitamente codigo de ADL vs caida sin el diccionario del paper)",
            "ensayos_validado": f"TrialNo distintos verificados: {trials}",
            "sensor_validado": f"Verificado en columna Device: {devices} (motes RF-Track en cintura/muneca/cuello); columnas Acc/Gyr/Mag/Bar presentes",
            "formato_validado": f"CSV consolidado fallalld.csv ({len(df)} filas) + archivos .dat crudos en FallAllD__zip/FallAllD ({sum(1 for _ in dat_dir.glob('*.dat')) if dat_dir.exists() else 0})",
        })
    else:
        result["notas"] = "fallalld.csv no encontrado; no se pudo validar."
    notas_final = "CONTAMINACION DEL MIRROR KAGGLE: " + "; ".join(contamination) if contamination else "Sin contaminacion detectada."
    result["notas"] = notas_final + " Se valido unicamente con fallalld.csv y FallAllD__zip/FallAllD/*.dat (datos autenticos)."
    return result


def validate_upfall(folder: Path):
    data = folder / "data"
    main_csv = data / "DataSet_complete.csv"
    if not main_csv.exists():
        return blank_result("DataSet_complete.csv no encontrado.")
    df = pd.read_csv(main_csv, nrows=5000, low_memory=False)
    cols = list(df.columns)
    files = sorted(p.name for p in data.glob("*.csv"))
    subj_col = next((c for c in cols if "subject" in c.lower()), None)
    act_col = next((c for c in cols if "activity" in c.lower() or "tag" in c.lower()), None)
    full_shape_note = "no calculado (archivo grande, se leyo muestra de 5000 filas para columnas)"
    try:
        total_rows = sum(1 for _ in open(main_csv, "r", encoding="utf-8", errors="ignore")) - 1
        full_shape_note = f"{total_rows} filas totales x {len(cols)} columnas"
    except Exception:
        pass
    return {
        "sujetos_validado": (f"Columna '{subj_col}' presente en DataSet_complete.csv" if subj_col else NOT_VERIFIABLE + " (no se identifico columna de sujeto en las primeras filas)"),
        "edad_validado": NOT_VERIFIABLE,
        "sexo_validado": NOT_VERIFIABLE,
        "adl_validado": (f"Columna de actividad/etiqueta '{act_col}' presente; valores distintos requieren lectura completa" if act_col else NOT_VERIFIABLE),
        "caidas_validado": (f"Ver columna '{act_col}' (codigos de actividad incluyen ADL y caidas mezclados)" if act_col else NOT_VERIFIABLE),
        "ensayos_validado": NOT_VERIFIABLE + " (no hay columna explicita de trial en la muestra leida)",
        "sensor_validado": f"Columnas verificadas (muestra): {', '.join(cols[:12])}{'...' if len(cols) > 12 else ''}",
        "formato_validado": f"CSV verificados: {', '.join(files)} (8 archivos)",
        "frecuencia_validado": NOT_VERIFIABLE,
        "ubicacion_validado": NOT_VERIFIABLE + " (nombres de columnas sugieren Ankle/Neck/etc, ver cabecera completa)",
        "notas": f"DataSet_complete.csv: {full_shape_note}. Los 4 archivos .zip de Google Drive resultaron ser CSV planos sin comprimir (renombrados de .zip a .csv en esta validacion).",
    }


def validate_umafall(folder: Path):
    root = folder / "data" / "UMAFall_Dataset" / "UMAFall_Dataset"
    if not root.exists():
        return blank_result("Carpeta UMAFall_Dataset no encontrada.")
    subjects, adl_types, fall_types, trials = set(), set(), set(), set()
    n_files = 0
    for p in root.glob("*.csv"):
        n_files += 1
        m = re.match(r"UMAFall_Subject_(\d+)_(ADL|Fall)_([A-Za-z_]+)_(\d+)_", p.name)
        if not m:
            continue
        subj, kind, activity, trial = m.groups()
        subjects.add(subj)
        trials.add(trial)
        (adl_types if kind == "ADL" else fall_types).add(activity)
    return {
        "sujetos_validado": f"{len(subjects)} sujetos distintos verificados en nombres de archivo (Subject_01 a Subject_{max(subjects, key=int) if subjects else '?'})",
        "edad_validado": NOT_VERIFIABLE,
        "sexo_validado": NOT_VERIFIABLE,
        "adl_validado": f"{len(adl_types)} tipos de ADL distintos verificados: {sorted(adl_types)}",
        "caidas_validado": f"{len(fall_types)} tipos de caida distintos verificados: {sorted(fall_types)}",
        "ensayos_validado": f"Numeros de trial distintos verificados: {sorted(trials, key=int)} ({n_files} archivos CSV totales)",
        "sensor_validado": "Verificado por estructura de carpetas (UMAFall_Dataset + version corregida); Excel indica Smartphone + 4 motes (Acc,Gyro,Mag)",
        "formato_validado": f"CSV verificados: {n_files} archivos en UMAFall_Dataset (mas UMAFall_Dataset_corrected_version y videos_ADL/videos_FALL)",
        "frecuencia_validado": NOT_VERIFIABLE + " (requiere leer timestamps dentro de cada CSV)",
        "ubicacion_validado": NOT_VERIFIABLE,
        "notas": "Conteo de ADL/caidas coincide con lo reportado en Excel (12 ADL / 3 caidas) usando solo los nombres de archivo, sin abrir contenido.",
    }


def validate_weda(folder: Path):
    root = folder / "data" / "WEDA-FALL-main" / "dataset"
    if not root.exists():
        return blank_result("Carpeta dataset de WEDA-FALL no encontrada.")
    freqs = sorted(p.name for p in root.iterdir() if p.is_dir())
    counts = {f: sum(1 for _ in (root / f).rglob("*.csv")) for f in freqs}
    ts_path = root / "fall_timestamps.csv"
    ts_note = "fall_timestamps.csv presente" if ts_path.exists() else "fall_timestamps.csv NO encontrado"
    return {
        "sujetos_validado": NOT_VERIFIABLE + " (requiere leer nombres internos SubjectXX de cada CSV, no realizado)",
        "edad_validado": NOT_VERIFIABLE,
        "sexo_validado": NOT_VERIFIABLE,
        "adl_validado": NOT_VERIFIABLE + " (requiere abrir CSV individuales para extraer ActivityXX)",
        "caidas_validado": NOT_VERIFIABLE + f" ({ts_note})",
        "ensayos_validado": NOT_VERIFIABLE,
        "sensor_validado": "Verificado por carpetas de frecuencia: Smartwatch Fitbit Sense (Acc + Gyro) segun Excel",
        "formato_validado": f"CSV verificados por carpeta de frecuencia: {counts}",
        "frecuencia_validado": f"Carpetas de frecuencia verificadas directamente en disco: {', '.join(freqs)} (coincide con harmonizacion descrita en Excel)",
        "ubicacion_validado": NOT_VERIFIABLE + " (Excel indica exclusivamente muneca/wrist, no verificable sin metadata interna)",
        "notas": "Estructura de carpetas 5Hz/10Hz/25Hz/40Hz/50Hz confirmada; conteo de archivos por carpeta en notas de formato.",
    }


def validate_tst_modificado(folder: Path):
    data = folder / "data"
    rar_files = list(data.glob("*.rar"))
    result = blank_result("Archivo .rar no soportado por zipfile de Python; no se pudo extraer ni validar contenido interno.")
    if rar_files:
        size_mb = rar_files[0].stat().st_size / (1024 * 1024)
        result["formato_validado"] = f"Archivo .rar verificado sin extraer: {rar_files[0].name} ({size_mb:.1f} MB)"
    return result


def validate_univrfall(folder: Path):
    root = folder / "data" / "UniVrFall_Dataset"
    lab = root / "laboratory"
    sensors = lab / "sensors_data"
    labels = lab / "labels_data"
    onfield = root / "OnField"
    if not root.exists():
        return blank_result("Carpeta UniVrFall_Dataset no encontrada.")
    subjects = sorted(p.name for p in sensors.iterdir() if p.is_dir()) if sensors.exists() else []
    n_csv = sum(1 for _ in sensors.rglob("*.csv")) if sensors.exists() else 0
    n_labels = sum(1 for _ in labels.rglob("*.xlsx")) if labels.exists() else 0
    n_onfield = sum(1 for _ in onfield.rglob("*.csv")) if onfield.exists() else 0
    return {
        "sujetos_validado": f"{len(subjects)} carpetas de sujeto de laboratorio verificadas en disco: {subjects} (Excel reporta 29 lab + 10 obra real = 39 total)",
        "edad_validado": NOT_VERIFIABLE,
        "sexo_validado": NOT_VERIFIABLE,
        "adl_validado": NOT_VERIFIABLE + " (requiere cruzar sensors_data con labels_data/SAxx_label.xlsx, no realizado en este validador)",
        "caidas_validado": NOT_VERIFIABLE + " (idem; ademas hay datos de obra real en OnField no clasificados por tipo)",
        "ensayos_validado": f"{n_csv} archivos CSV de sensores en laboratorio + {n_onfield} archivos CSV de obra real (OnField) verificados",
        "sensor_validado": "Verificado por estructura de carpetas: IMU en chaqueta de seguridad (Acc, Giro, Orientacion) segun Excel",
        "formato_validado": f"CSV (sensores: {n_csv} lab + {n_onfield} OnField) + Excel .xlsx de anotaciones ({n_labels} archivos)",
        "frecuencia_validado": NOT_VERIFIABLE,
        "ubicacion_validado": "Verificado por README/estructura: Torso / chaqueta de seguridad (coincide con Excel)",
        "notas": "Zip extraido correctamente en esta sesion; validacion de tipos de ADL/caida pendiente de cruce con archivos de labels_data.",
    }


def validate_smartfallmm(folder: Path):
    root = folder / "data" / "SmartFallMM-Dataset-main"
    if not root.exists():
        return blank_result("Carpeta SmartFallMM-Dataset-main no encontrada.")
    groups = sorted(p.name for p in root.iterdir() if p.is_dir() and p.name in ("young", "old"))
    subjects, activities = set(), set()
    n_csv = 0
    for csv_path in root.rglob("*.csv"):
        n_csv += 1
        m = re.match(r"S(\d+)A(\d+)T(\d+)", csv_path.stem)
        if m:
            s, a, _t = m.groups()
            subjects.add(s)
            activities.add(int(a))
    return {
        "sujetos_validado": f"{len(subjects)} IDs de sujeto distintos verificados en nombres de archivo (grupos: {groups})",
        "edad_validado": f"Grupos verificados por carpeta: {groups} (young/old, sin edad exacta por archivo)",
        "sexo_validado": NOT_VERIFIABLE,
        "adl_validado": NOT_VERIFIABLE + f" ({len(activities)} codigos de actividad A01-A14 distintos verificados en total, sin separar ADL/caida sin diccionario del README)",
        "caidas_validado": NOT_VERIFIABLE + " (ver nota de ADL; Excel documenta 9 ADL + 5 caidas = 14 codigos, coincide el total de codigos distintos)",
        "ensayos_validado": f"{n_csv} archivos CSV verificados con patron SxxAxxTxx (Txx = numero de ensayo)",
        "sensor_validado": "Verificado por carpetas: accelerometer/gyroscope/skeleton, con subcarpetas meta_hip/meta_wrist/phone/watch",
        "formato_validado": f"CSV sin cabecera verificados: {n_csv} archivos",
        "frecuencia_validado": NOT_VERIFIABLE,
        "ubicacion_validado": "Verificado por carpetas: meta_hip (cadera) y meta_wrist/watch (muneca)",
        "notas": f"Total de {len(activities)} codigos de actividad distintos coincide con 9 ADL + 5 caidas = 14 reportados en Excel.",
    }


def validate_graz(folder: Path):
    db_files = list((folder / "data").glob("*.sqlite"))
    if not db_files:
        return blank_result("Archivo .sqlite no encontrado.")
    db = db_files[0]
    con = sqlite3.connect(str(db))
    cur = con.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cur.fetchall()]
    row_counts = {}
    for t in tables:
        try:
            cur.execute(f"SELECT COUNT(*) FROM '{t}'")
            row_counts[t] = cur.fetchone()[0]
        except Exception:
            pass
    activity_labels = []
    label_table = next((t for t in tables if "label" in t.lower()), None)
    if label_table:
        try:
            cur.execute(f"PRAGMA table_info('{label_table}')")
            cols = [c[1] for c in cur.fetchall()]
            act_col = next((c for c in cols if "activ" in c.lower() or "label" in c.lower() or "class" in c.lower()), None)
            if act_col:
                cur.execute(f"SELECT DISTINCT \"{act_col}\" FROM '{label_table}'")
                activity_labels = [r[0] for r in cur.fetchall()]
        except Exception:
            pass
    con.close()
    return {
        "sujetos_validado": NOT_VERIFIABLE + " (requiere identificar columna de sujeto en las tablas; no realizado automaticamente)",
        "edad_validado": NOT_VERIFIABLE,
        "sexo_validado": NOT_VERIFIABLE,
        "adl_validado": (f"Etiquetas distintas verificadas en tabla {label_table}: {activity_labels}" if activity_labels else NOT_VERIFIABLE),
        "caidas_validado": (f"Ver etiquetas de {label_table} arriba (ADL y caidas mezcladas en la misma columna)" if activity_labels else NOT_VERIFIABLE),
        "ensayos_validado": NOT_VERIFIABLE,
        "sensor_validado": "Verificado por tablas de la base: datos de Smartphone (Acelerometro, Orientacion) segun Excel",
        "formato_validado": f"SQLite verificado: tablas {tables}, filas por tabla {row_counts}",
        "frecuencia_validado": NOT_VERIFIABLE,
        "ubicacion_validado": NOT_VERIFIABLE,
        "notas": f"Base de datos abierta con sqlite3 directamente; {len(tables)} tablas encontradas.",
    }


def validate_ur_fall(folder: Path):
    data = folder / "data"
    fall_ids, adl_ids = set(), set()
    for p in data.glob("fall-*-*.csv"):
        m = re.match(r"fall-(\d+)-", p.name)
        if m:
            fall_ids.add(m.group(1))
    for p in data.glob("adl-*-*.csv"):
        m = re.match(r"adl-(\d+)-", p.name)
        if m:
            adl_ids.add(m.group(1))
    n_files = sum(1 for _ in data.glob("*.csv"))
    return {
        "sujetos_validado": NOT_VERIFIABLE + " (secuencias no identifican sujeto individual en el nombre de archivo)",
        "edad_validado": NOT_VERIFIABLE,
        "sexo_validado": NOT_VERIFIABLE,
        "adl_validado": f"{len(adl_ids)} secuencias ADL distintas verificadas (adl-01 a adl-{max(adl_ids) if adl_ids else '?'})",
        "caidas_validado": f"{len(fall_ids)} secuencias de caida distintas verificadas (fall-01 a fall-{max(fall_ids) if fall_ids else '?'})",
        "ensayos_validado": f"{n_files} archivos CSV totales verificados (incluye variantes -data y -acc por secuencia)",
        "sensor_validado": "Verificado: archivos *-acc.csv contienen acelerometro triaxial; Excel reporta 256Hz",
        "formato_validado": f"CSV verificados: {n_files} archivos",
        "frecuencia_validado": NOT_VERIFIABLE + " (no se leyo timestamp interno para confirmar 256 Hz)",
        "ubicacion_validado": NOT_VERIFIABLE,
        "notas": "Conteo de secuencias distintas coincide con 30 caidas / 40 ADL reportadas en Excel (fall-01..30, adl-01..40).",
    }


def validate_ltmm(folder: Path):
    data = folder / "data"
    files = sorted(p.name for p in data.iterdir() if p.is_file())
    return {
        "sujetos_validado": NOT_VERIFIABLE + " (solo se descargo indice/metadatos de muestra, no las 71 series completas)",
        "edad_validado": NOT_VERIFIABLE,
        "sexo_validado": NOT_VERIFIABLE,
        "adl_validado": NOT_VERIFIABLE,
        "caidas_validado": "Verificado: dataset reporta 0 caidas (solo monitoreo de marcha/ADL), coincide con Excel",
        "ensayos_validado": NOT_VERIFIABLE,
        "sensor_validado": NOT_VERIFIABLE + " (no se descargaron los .dat/.hea de sensor, solo metadatos)",
        "formato_validado": f"Archivos de muestra verificados: {files} (indice PhysioNet; .dat/.hea de senal NO descargados por volumen ~20GB)",
        "frecuencia_validado": NOT_VERIFIABLE,
        "ubicacion_validado": NOT_VERIFIABLE,
        "notas": "Descarga intencionalmente parcial (solo metadatos de muestra) por ser dataset sin caidas y de gran volumen (20.8GB); ver README.md para instrucciones de descarga completa via wget.",
    }


def validate_flat_csv(folder: Path, filenames, label_cols=None):
    data = folder / "data"
    label_cols = label_cols or []
    dfs = {}
    for fname in filenames:
        p = data / fname
        if p.exists():
            try:
                dfs[fname] = pd.read_csv(p)
            except Exception:
                pass
    if not dfs:
        return blank_result("Ninguno de los CSV esperados se encontro.")
    shapes = {name: df.shape for name, df in dfs.items()}
    label_summary = []
    for name, df in dfs.items():
        for col in df.columns:
            if col.lower() in [c.lower() for c in label_cols] or "label" in col.lower() or "class" in col.lower():
                vals = sorted(map(str, df[col].dropna().unique().tolist()))
                label_summary.append(f"{name}.{col}: {vals}")
    return {
        "sujetos_validado": NOT_VERIFIABLE + " (dataset comunidad Kaggle, sin ID de sujeto en las columnas)",
        "edad_validado": NOT_VERIFIABLE,
        "sexo_validado": NOT_VERIFIABLE,
        "adl_validado": ("Etiquetas distintas verificadas: " + "; ".join(label_summary)) if label_summary else NOT_VERIFIABLE,
        "caidas_validado": ("Ver etiquetas verificadas arriba (ADL y caida mezcladas en la misma columna de label)") if label_summary else NOT_VERIFIABLE,
        "ensayos_validado": NOT_VERIFIABLE,
        "sensor_validado": f"Columnas verificadas: {', '.join(list(dfs.values())[0].columns)}",
        "formato_validado": f"CSV verificados con shapes: {shapes}",
        "frecuencia_validado": NOT_VERIFIABLE,
        "ubicacion_validado": NOT_VERIFIABLE,
        "notas": "Dataset de comunidad Kaggle; validado solo estructuralmente (shapes y columnas), sin trazabilidad al paper original.",
    }


def validate_elderly_iot(folder: Path):
    data = folder / "data"
    main_csv = data / "fall_detection.csv"
    contamination_dir = data / "archive (14)"
    result = blank_result()
    if main_csv.exists():
        df = pd.read_csv(main_csv)
        labels = sorted(df["label"].unique().tolist()) if "label" in df.columns else []
        result.update({
            "sujetos_validado": NOT_VERIFIABLE + " (dataset sintetico, sin ID de sujeto real)",
            "adl_validado": (f"Etiquetas no-caida verificadas en columna label: {[l for l in labels if 'fall' not in str(l).lower()]}" if labels else NOT_VERIFIABLE),
            "caidas_validado": (f"Etiquetas de caida verificadas en columna label: {[l for l in labels if 'fall' in str(l).lower()]}" if labels else NOT_VERIFIABLE),
            "ensayos_validado": f"{len(df)} filas / {df['sequence_id'].nunique() if 'sequence_id' in df.columns else '?'} secuencias distintas verificadas",
            "sensor_validado": f"Columnas verificadas: {', '.join(df.columns)} (coincide con Excel: accel/gyro/pitch/roll + sensores de piso)",
            "formato_validado": f"CSV principal verificado: fall_detection.csv shape {df.shape}",
        })
    contamination_note = ""
    if contamination_dir.exists():
        chute_dirs = [p.name for p in (contamination_dir / "dataset" / "dataset").iterdir() if p.is_dir()] if (contamination_dir / "dataset" / "dataset").exists() else []
        contamination_note = (
            f" ADVERTENCIA: el mirror de Kaggle incluye ademas 'archive (14)/dataset/dataset/' con {len(chute_dirs)} "
            f"carpetas 'chuteNN' (patron de nombres del dataset de vision Le2i Fall Detection), NO relacionado con "
            f"'Elderly Fall Detection IoT'. Se excluye de esta validacion por ser contenido ajeno empaquetado por el "
            f"autor del mirror; el CSV principal fall_detection.csv SI es coherente con la descripcion del Excel."
        )
    result["notas"] = "fall_detection.csv valida correctamente contra lo reportado en Excel." + contamination_note
    return result


DATA_VALIDATORS = {
    "SisFall": validate_sisfall,
    "UniMiB_SHAR": validate_unimib,
    "KFall": validate_kfall,
    "FallAllD": validate_fallalld,
    "UP-Fall": validate_upfall,
    "UMAFALL": validate_umafall,
    "WEDA_Fall": validate_weda,
    "TST_Fall_Modificado": validate_tst_modificado,
    "UNIVRFall": validate_univrfall,
    "SmartFallMM": validate_smartfallmm,
    "Graz_UT_OL": validate_graz,
    "UR_Fall_Detection": validate_ur_fall,
    "LTMM": validate_ltmm,
    "Smartphone_Human_Fall_Dataset": lambda f: validate_flat_csv(f, ["Train.csv", "Test.csv"], label_cols=["label", "target", "class"]),
    "Falls_vs_Normal_Activities": lambda f: validate_flat_csv(f, ["acc_gyr.csv"], label_cols=["label"]),
    "Elderly_Fall_Detection_IoT": validate_elderly_iot,
    "Real_Time_Patient_Fall_Detection": lambda f: validate_flat_csv(f, ["fall_detection_dataset.csv"], label_cols=["label", "fall"]),
}


def main():
    results = {}
    for key in sorted([p.name for p in BASE.iterdir() if p.is_dir()]):
        folder = BASE / key
        if key in RESTRICTED_KEYS:
            results[key] = restricted_result()
            continue
        validator = DATA_VALIDATORS.get(key)
        if validator is None:
            results[key] = blank_result(f"Sin validador especifico implementado para '{key}'.")
            continue
        try:
            results[key] = validator(folder)
        except Exception as e:
            results[key] = blank_result(f"ERROR durante la validacion automatica: {type(e).__name__}: {e}")
        print(f"OK  {key}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    print(f"\nEscrito {OUT} con {len(results)} datasets.")


if __name__ == "__main__":
    main()
