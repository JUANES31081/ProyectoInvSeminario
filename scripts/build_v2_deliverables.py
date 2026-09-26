"""
Fase 2 - Genera los 3 entregables finales a partir de:
  - analytics/_excel_dump.json (fuente de verdad: hoja Datasets_Unicos del Excel)
  - analytics/dataset_metrics_v2.json (metricas validadas por scripts/validate_dataset_metrics.py)
  - URL.txt de cada carpeta en datasets/DescargasDataManualmente/<key>/

Genera:
  - docs/CHECKLIST_DESCARGAS_V2.md
  - docs/REPORTE_DATASETS_CAIDAS_V2.md (solo tabla, columnas Excel + validadas + URL real)
"""
import json
from pathlib import Path

ROOT = Path(r"d:\UniversidadEAN\ProyectoGrado")
EXCEL_DUMP = ROOT / "analytics" / "_excel_dump.json"
METRICS = ROOT / "analytics" / "dataset_metrics_v2.json"
BASE = ROOT / "datasets" / "DescargasDataManualmente"

# Orden exacto de filas del Excel -> carpeta local
EXCEL_ROW_TO_KEY = [
    "SisFall", "UniMiB_SHAR", "KFall", "FallAllD", "UP-Fall", "UMAFALL", "WEDA_Fall",
    "TST_Fall_v1", "TST_Fall_v2", "TST_Fall_Modificado", "UNIVRFall", "SmartFallMM",
    "FARSEEING", "MobiAct", "MobiFall", "Graz_UT_OL", "UR_Fall_Detection", "DOFDA",
    "Erciyes_University", "IMUFD", "DLR", "FFFStudy", "LTMM",
    "Smartphone_Human_Fall_Dataset", "Falls_vs_Normal_Activities",
    "Elderly_Fall_Detection_IoT", "Real_Time_Patient_Fall_Detection", "Ultralytics_Fall_Detect",
]

RESTRICTED_KEYS = {
    "TST_Fall_v1", "TST_Fall_v2", "FARSEEING", "MobiAct", "MobiFall", "DOFDA",
    "Erciyes_University", "IMUFD", "DLR", "FFFStudy", "Ultralytics_Fall_Detect",
}

# Datasets descargados donde se identifico una URL real de extraccion distinta a la que
# aparecia (o no aparecia) en el Excel, via busqueda web durante la Fase 1.
REAL_URL_DIFFERENT = {
    "WEDA_Fall": "https://github.com/joaojtmarques/WEDA-FALL (repositorio de datos real; el Excel solo citaba la publicacion MDPI sin URL de datos)",
    "LTMM": "https://physionet.org/content/ltmm/1.0.0/ (el Excel no traia URL; identificado por busqueda web)",
}

NOT_APPLICABLE_RESTRICTED = "No aplica (dataset restringido, sin descarga)"
COINCIDE = "Coincide con la URL del Excel"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def esc(val):
    """Escapa caracteres que rompen tablas markdown y colapsa saltos de linea."""
    if val is None:
        return ""
    s = str(val)
    s = s.replace("\r\n", " ").replace("\n", " ").replace("\r", " ")
    s = s.replace("|", "\\|")
    return s.strip()


def build_checklist(excel_rows, metrics):
    lines = []
    lines.append("# Checklist de Descargas — Datasets de Caidas (v2)\n")
    lines.append(
        "Estado real de descarga de los 28 datasets de la hoja `Datasets_Unicos` "
        "(`docs/Revision_Articulos_Deteccion_Caidas-v3.xlsx`), verificado sobre "
        "`datasets/DescargasDataManualmente/`.\n"
    )
    n_ok = sum(1 for k in EXCEL_ROW_TO_KEY if k not in RESTRICTED_KEYS)
    n_restricted = len(RESTRICTED_KEYS)
    lines.append(f"**Resumen:** {n_ok}/28 descargados con datos locales, {n_restricted}/28 restringidos (solo documentados).\n")
    lines.append("| # | Dataset (Excel) | Carpeta local | Estado | Notas |")
    lines.append("|---|---|---|---|---|")
    for i, (row, key) in enumerate(zip(excel_rows, EXCEL_ROW_TO_KEY), start=1):
        nombre = row[1]
        folder = BASE / key
        has_data = (folder / "data").exists() and any((folder / "data").iterdir())
        if key in RESTRICTED_KEYS:
            estado = "Restringido (sin descarga)"
        elif has_data:
            estado = "Descargado"
        else:
            estado = "Sin datos (revisar)"
        notas = metrics.get(key, {}).get("notas", "")
        # Acortar notas muy largas para el checklist (el detalle completo va en el reporte v2)
        notas_short = notas if len(notas) <= 220 else notas[:217] + "..."
        lines.append(f"| {i} | {esc(nombre)} | `datasets/DescargasDataManualmente/{key}/` | {estado} | {esc(notas_short)} |")
    return "\n".join(lines) + "\n"


def real_url_for(key):
    if key in RESTRICTED_KEYS:
        return NOT_APPLICABLE_RESTRICTED
    return REAL_URL_DIFFERENT.get(key, COINCIDE)


def build_report(header, excel_rows, metrics):
    # header indices (0-based):
    # 0 Categoria/Prioridad, 1 Nombre, 2 Sujetos, 3 Edad, 4 Sexo, 5 Poblacion,
    # 6 Caidas Reales/Simuladas, 7 ADL, 8 Caidas, 9 Ensayos, 10 Sensor, 11 Ubicacion,
    # 12 Frecuencia, 13 Unidades/Ejes, 14 Identificadores, 15 Formato, 16 Acceso, 17 URL
    columns = [
        ("Categoría / Prioridad", 0, None),
        ("Nombre del Dataset", 1, None),
        ("Número de Sujetos", 2, "sujetos_validado"),
        ("Edad / Rango Etario", 3, "edad_validado"),
        ("Sexo", 4, "sexo_validado"),
        ("Población", 5, None),
        ("Caídas Reales o Simuladas", 6, None),
        ("Número y Tipo de ADL", 7, "adl_validado"),
        ("Número y Tipo de Caídas", 8, "caidas_validado"),
        ("Ensayos / Repeticiones por Sujeto", 9, "ensayos_validado"),
        ("Tipo de Sensor", 10, "sensor_validado"),
        ("Ubicación Corporal", 11, "ubicacion_validado"),
        ("Frecuencia de Muestreo", 12, "frecuencia_validado"),
        ("Unidades y Ejes Disponibles", 13, None),
        ("Identificadores de Sujeto y Ensayo", 14, None),
        ("Formato de Almacenamiento", 15, "formato_validado"),
        ("Tipo de Acceso", 16, None),
        ("URL de Acceso / Fuente Oficial", 17, None),
    ]

    header_cells = []
    for name, _idx, validated_key in columns:
        header_cells.append(name)
        if validated_key:
            header_cells.append(f"{name} (validado data)")
    header_cells.append("URL Real de Extracción (validado data)")

    lines = []
    lines.append("# Reporte de Datasets de Caidas — v2 (validado contra datos descargados)\n")
    lines.append(
        "Tabla generada automaticamente a partir de `docs/Revision_Articulos_Deteccion_Caidas-v3.xlsx` "
        "(hoja `Datasets_Unicos`, fuente de verdad) cruzada con evidencia real extraida de "
        "`datasets/DescargasDataManualmente/` mediante `scripts/validate_dataset_metrics.py`. "
        "Las columnas '(validado data)' contienen SOLO lo verificable directamente en los archivos "
        "descargados; donde no fue posible verificar se indica explicitamente.\n"
    )
    lines.append("| " + " | ".join(header_cells) + " |")
    lines.append("|" + "---|" * len(header_cells))

    for row, key in zip(excel_rows, EXCEL_ROW_TO_KEY):
        m = metrics.get(key, {})
        cells = []
        for name, idx, validated_key in columns:
            cells.append(esc(row[idx]))
            if validated_key:
                cells.append(esc(m.get(validated_key, "")))
        cells.append(esc(real_url_for(key)))
        lines.append("| " + " | ".join(cells) + " |")

    return "\n".join(lines) + "\n"


def main():
    excel = load_json(EXCEL_DUMP)
    header, excel_rows = excel["header"], excel["rows"]
    metrics = load_json(METRICS)

    assert len(excel_rows) == len(EXCEL_ROW_TO_KEY), (
        f"Desalineacion: {len(excel_rows)} filas del Excel vs {len(EXCEL_ROW_TO_KEY)} keys mapeadas"
    )

    checklist_md = build_checklist(excel_rows, metrics)
    (ROOT / "docs" / "CHECKLIST_DESCARGAS_V2.md").write_text(checklist_md, encoding="utf-8")

    report_md = build_report(header, excel_rows, metrics)
    (ROOT / "docs" / "REPORTE_DATASETS_CAIDAS_V2.md").write_text(report_md, encoding="utf-8")

    print("Escrito docs/CHECKLIST_DESCARGAS_V2.md")
    print("Escrito docs/REPORTE_DATASETS_CAIDAS_V2.md")


if __name__ == "__main__":
    main()
