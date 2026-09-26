"""
Fase 1 (V2) de descarga de datasets de caidas.

Descarga y organiza datasets en datasets/DescargasDataManualmente/<Dataset>/
con la estructura:
    URL.txt        -> fuente(s) oficial(es) usada(s), tomadas del Excel
                       Revision_Articulos_Deteccion_Caidas-v3.xlsx (hoja Datasets_Unicos)
                       salvo que se indique "[web]" (URL encontrada por busqueda,
                       documentada explicitamente).
    data/          -> archivos descargados (cuando el acceso es publico/automatizable)
    README.md      -> como consumir el dataset (generado en un paso posterior)

Uso:
    python scripts/download_manual_v2.py            # descarga todo lo automatizable
    python scripts/download_manual_v2.py --only SisFall,UMAFall
    python scripts/download_manual_v2.py --list
"""
from __future__ import annotations

import argparse
import io
import os
import sys
import time
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

import requests

ROOT = Path(__file__).resolve().parents[1]
BASE_DIR = ROOT / "datasets" / "DescargasDataManualmente"
LOG_PATH = ROOT / "analytics" / "manual_downloads_v2_log.csv"

UA = {"User-Agent": "Mozilla/5.0 (compatible; ProyectoGradoBot/1.0; +research use)"}


def load_env_tokens() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if not value:
            continue
        if key == "KAGGLE_API":
            os.environ.setdefault("KAGGLE_API_TOKEN", value)
        else:
            os.environ.setdefault(key, value)


@dataclass
class Dataset:
    key: str  # standardized folder name
    title: str
    category: str  # "1. Oficial / Validado" | "2. Comunidad / Kaggle" | "2. Comunidad / Vision"
    access: str  # "public_auto" | "kaggle_mirror" | "restricted"
    urls: list  # list[(label, url, provenance)]  provenance: "excel" | "web"
    downloader: Optional[str] = None  # key into DOWNLOADERS
    download_kwargs: dict = field(default_factory=dict)
    notes: str = ""


def dest_dir(ds: Dataset) -> Path:
    return BASE_DIR / ds.key


def write_url_file(ds: Dataset) -> None:
    folder = dest_dir(ds)
    folder.mkdir(parents=True, exist_ok=True)
    lines = []
    for label, url, provenance in ds.urls:
        tag = "" if provenance == "excel" else " [web]"
        lines.append(f"{label}{tag}: {url}")
    if ds.notes:
        lines.append("")
        lines.append(f"Nota: {ds.notes}")
    (folder / "URL.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def stream_download(url: str, dest: Path, headers: Optional[dict] = None, allow_redirects: bool = True) -> int:
    dest.parent.mkdir(parents=True, exist_ok=True)
    h = dict(UA)
    if headers:
        h.update(headers)
    last_err = None
    for attempt in range(3):
        try:
            with requests.get(url, headers=h, stream=True, allow_redirects=allow_redirects, timeout=(15, 30)) as r:
                r.raise_for_status()
                total = 0
                with open(dest, "wb") as f:
                    for chunk in r.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            f.write(chunk)
                            total += len(chunk)
            return total
        except Exception as e:  # noqa: BLE001
            last_err = e
    raise last_err


# ---------------------------------------------------------------------------
# Downloaders
# ---------------------------------------------------------------------------

def dl_figshare(ds: Dataset, article_id: str, extract_zip: bool = False, **_):
    out = dest_dir(ds) / "data"
    out.mkdir(parents=True, exist_ok=True)
    r = requests.get(f"https://api.figshare.com/v2/articles/{article_id}", headers=UA, timeout=60)
    r.raise_for_status()
    meta = r.json()
    results = []
    for f in meta.get("files", []):
        name = f["name"]
        url = f["download_url"]
        dest = out / name
        if dest.exists() and dest.stat().st_size == f.get("size", -1):
            results.append((name, "skip-exists", dest.stat().st_size))
            continue
        try:
            size = stream_download(url, dest)
            if extract_zip and name.lower().endswith(".zip"):
                try:
                    with zipfile.ZipFile(dest) as zf:
                        zf.extractall(out)
                    dest.unlink()
                    results.append((name, "ok-extracted", size))
                    continue
                except Exception as e:  # noqa: BLE001
                    results.append((name, f"downloaded-but-extract-error:{e}", size))
                    continue
            results.append((name, "ok", size))
        except Exception as e:  # noqa: BLE001
            results.append((name, f"error:{e}", 0))
    return results


def dl_zenodo(ds: Dataset, record_id: str, **_):
    out = dest_dir(ds) / "data"
    out.mkdir(parents=True, exist_ok=True)
    r = requests.get(f"https://zenodo.org/api/records/{record_id}", headers=UA, timeout=60)
    r.raise_for_status()
    meta = r.json()
    results = []
    for f in meta.get("files", []):
        name = f.get("key") or f.get("filename")
        url = f["links"]["self"]
        dest = out / name
        try:
            size = stream_download(url, dest)
            results.append((name, "ok", size))
        except Exception as e:  # noqa: BLE001
            results.append((name, f"error:{e}", 0))
    return results


def dl_github_release_asset(ds: Dataset, browser_download_url: str, filename: str, **_):
    out = dest_dir(ds) / "data"
    dest = out / filename
    try:
        size = stream_download(browser_download_url, dest)
    except Exception as e:  # noqa: BLE001
        return [(filename, f"error:{e}", 0)]
    if filename.lower().endswith(".zip"):
        try:
            with zipfile.ZipFile(dest) as zf:
                zf.extractall(out)
            dest.unlink()
            return [(filename, "ok-extracted", size)]
        except Exception as e:  # noqa: BLE001
            return [(filename, f"downloaded-but-extract-error:{e}", size)]
    return [(filename, "ok", size)]


def dl_github_repo_zip(ds: Dataset, owner: str, repo: str, branch: str = "main", **_):
    out = dest_dir(ds) / "data"
    out.mkdir(parents=True, exist_ok=True)
    url = f"https://codeload.github.com/{owner}/{repo}/zip/refs/heads/{branch}"
    zip_path = out / f"{repo}-{branch}.zip"
    try:
        stream_download(url, zip_path)
    except Exception as e:  # noqa: BLE001
        return [(zip_path.name, f"error:{e}", 0)]
    try:
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(out)
        zip_path.unlink(missing_ok=True)
        return [(f"{repo}-{branch}/*", "ok-extracted", 0)]
    except Exception as e:  # noqa: BLE001
        return [(zip_path.name, f"downloaded-but-extract-error:{e}", zip_path.stat().st_size)]


def dl_dropbox(ds: Dataset, url: str, filename: str, **_):
    out = dest_dir(ds) / "data"
    dest = out / filename
    direct = url.replace("dl=0", "dl=1")
    if "dl=1" not in direct:
        direct = direct + ("&dl=1" if "?" in direct else "?dl=1")
    try:
        size = stream_download(direct, dest)
    except Exception as e:  # noqa: BLE001
        return [(filename, f"error:{e}", 0)]
    if filename.lower().endswith(".zip"):
        try:
            with zipfile.ZipFile(dest) as zf:
                zf.extractall(out)
            dest.unlink()
            return [(filename, "ok-extracted", size)]
        except Exception as e:  # noqa: BLE001
            return [(filename, f"downloaded-but-extract-error:{e}", size)]
    return [(filename, "ok", size)]


def dl_gdrive_files(ds: Dataset, files: list, **_):
    """files: list of (file_id, filename)"""
    import gdown  # local import: heavy optional dependency

    out = dest_dir(ds) / "data"
    out.mkdir(parents=True, exist_ok=True)
    results = []
    for file_id, filename in files:
        dest = out / filename
        try:
            gdown.download(id=file_id, output=str(dest), quiet=False)
            size = dest.stat().st_size if dest.exists() else 0
            results.append((filename, "ok" if size else "error:empty", size))
        except Exception as e:  # noqa: BLE001
            results.append((filename, f"error:{e}", 0))
    return results


def dl_ur_fall(ds: Dataset, **_):
    out = dest_dir(ds) / "data"
    out.mkdir(parents=True, exist_ok=True)
    base = "https://fenix.ur.edu.pl/~mkepski/ds/data/"
    results = []
    kinds = ["data", "acc"]
    for prefix, count in (("adl", 40), ("fall", 30)):
        for i in range(1, count + 1):
            for kind in kinds:
                name = f"{prefix}-{i:02d}-{kind}.csv"
                dest = out / name
                if dest.exists():
                    results.append((name, "skip-exists", dest.stat().st_size))
                    continue
                try:
                    size = stream_download(base + name, dest)
                    results.append((name, "ok", size))
                except Exception as e:  # noqa: BLE001
                    results.append((name, f"error:{e}", 0))
    for name in ("urfall-cam0-falls.csv", "urfall-cam0-adls.csv"):
        dest = out / name
        try:
            size = stream_download(base + name, dest)
            results.append((name, "ok", size))
        except Exception as e:  # noqa: BLE001
            results.append((name, f"error:{e}", 0))
    return results


def dl_physionet_sample(ds: Dataset, project: str, version: str, files: list, **_):
    """Descarga solo un subconjunto representativo (dataset sin caidas, muy pesado: 20.8GB total)."""
    out = dest_dir(ds) / "data"
    out.mkdir(parents=True, exist_ok=True)
    base = f"https://physionet.org/files/{project}/{version}/"
    results = []
    for name in files:
        dest = out / name
        try:
            size = stream_download(base + name, dest)
            results.append((name, "ok", size))
        except Exception as e:  # noqa: BLE001
            results.append((name, f"error:{e}", 0))
    return results


def _long_path(p: Path) -> Path:
    """Prefix with \\\\?\\ on Windows to bypass the 260-char MAX_PATH limit."""
    s = str(p.resolve())
    if os.name == "nt" and not s.startswith("\\\\?\\"):
        return Path("\\\\?\\" + s)
    return p


def dl_kaggle(ds: Dataset, slug: str, **_):
    load_env_tokens()
    out = dest_dir(ds) / "data"
    out.mkdir(parents=True, exist_ok=True)
    try:
        import kagglehub
    except ImportError:
        return [(slug, "error:kagglehub not installed", 0)]
    if not (os.environ.get("KAGGLE_API_TOKEN") or (os.environ.get("KAGGLE_USERNAME") and os.environ.get("KAGGLE_KEY"))):
        return [(slug, "error:no kaggle credentials", 0)]
    import shutil
    import uuid

    # Usar una ruta de cache MUY corta cerca de la raiz del disco: algunos datasets de Kaggle
    # (ej. FallAllD) traen archivos con rutas internas extremadamente largas que exceden el
    # limite MAX_PATH (260) de Windows si el cache queda dentro de %TEMP%.
    cache_dir = Path(f"D:/_kh_{uuid.uuid4().hex[:8]}")
    cache_dir.mkdir(parents=True, exist_ok=True)
    os.environ["KAGGLEHUB_CACHE"] = str(cache_dir)
    try:
        path = Path(kagglehub.dataset_download(slug))
    except Exception as e:  # noqa: BLE001
        shutil.rmtree(cache_dir, ignore_errors=True)
        return [(slug, f"error:{e}", 0)]
    count = 0
    errors = 0
    total_size = 0
    for p in path.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(path)
        target = out / rel
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
        except Exception:  # noqa: BLE001
            target = _long_path(out) / rel
            _long_path(target.parent).mkdir(parents=True, exist_ok=True)
        try:
            if not target.exists():
                shutil.copyfile(_long_path(p), _long_path(target))
            count += 1
            total_size += target.stat().st_size
        except Exception:  # noqa: BLE001
            errors += 1
    shutil.rmtree(cache_dir, ignore_errors=True)
    status = f"ok-{count}-files" if errors == 0 else f"ok-{count}-files-{errors}-skipped"
    return [(slug, status, total_size)]


DOWNLOADERS: dict[str, Callable] = {
    "figshare": dl_figshare,
    "zenodo": dl_zenodo,
    "github_release_asset": dl_github_release_asset,
    "github_repo_zip": dl_github_repo_zip,
    "dropbox": dl_dropbox,
    "gdrive_files": dl_gdrive_files,
    "ur_fall": dl_ur_fall,
    "physionet_sample": dl_physionet_sample,
    "kaggle": dl_kaggle,
}


# ---------------------------------------------------------------------------
# Dataset registry (metadata sourced from docs/Revision_Articulos_Deteccion_Caidas-v3.xlsx,
# hoja "Datasets_Unicos", salvo lo marcado con provenance="web")
# ---------------------------------------------------------------------------

DATASETS: list[Dataset] = [
    Dataset(
        key="SisFall",
        title="SisFall",
        category="1. Oficial / Validado",
        access="public_auto",
        urls=[
            ("Mirror GitHub (respaldo, dataset original)", "https://github.com/BIng2325/SisFall", "excel"),
            ("Paper original (MDPI Sensors 2017)", "https://www.mdpi.com/1424-8220/17/1/198", "excel"),
            ("Mirror Kaggle (fallback)", "https://www.kaggle.com/datasets/thevman/sisfall-dataset", "excel"),
        ],
        downloader="github_release_asset",
        download_kwargs={
            "browser_download_url": "https://github.com/BIng2325/SisFall/releases/download/dataset/SisFall.zip",
            "filename": "SisFall.zip",
        },
        notes="Fuente original (sistemic.udea.edu.co) inactiva; se usa el respaldo en GitHub (release 'dataset', SisFall.zip, ~213MB).",
    ),
    Dataset(
        key="UniMiB_SHAR",
        title="UniMiB SHAR",
        category="1. Oficial / Validado",
        access="public_auto",
        urls=[
            ("Oficial", "http://www.sal.disco.unimib.it/technologies/unimib-shar/", "excel"),
            ("Descarga directa (Dropbox)", "https://www.dropbox.com/s/x2fpfqj0bpf8ep6/UniMiB-SHAR.zip?dl=0", "excel"),
            ("Mirror Kaggle (fallback)", "https://www.kaggle.com/datasets/wangboluo/unimib-shar-dataset", "excel"),
        ],
        downloader="dropbox",
        download_kwargs={
            "url": "https://www.dropbox.com/s/x2fpfqj0bpf8ep6/UniMiB-SHAR.zip?dl=0",
            "filename": "UniMiB-SHAR.zip",
        },
    ),
    Dataset(
        key="KFall",
        title="KFall",
        category="1. Oficial / Validado",
        access="kaggle_mirror",
        urls=[
            ("Oficial (formulario, requiere solicitud)", "https://sites.google.com/view/kfalldataset", "excel"),
            ("Mirror Kaggle", "https://www.kaggle.com/datasets/usmanabbasi2002/kfall-dataset", "excel"),
        ],
        downloader="kaggle",
        download_kwargs={"slug": "usmanabbasi2002/kfall-dataset"},
        notes="Fuente oficial requiere formulario en Google Sites (sin credenciales disponibles); se descarga el mirror publico de Kaggle.",
    ),
    Dataset(
        key="FallAllD",
        title="FallAllD",
        category="1. Oficial / Validado",
        access="kaggle_mirror",
        urls=[
            ("Oficial (IEEE DataPort, requiere suscripcion)",
             "https://ieee-dataport.org/open-access/fallalld-comprehensive-dataset-human-falls-and-activities-daily-living",
             "excel"),
            ("Mirror Kaggle", "https://www.kaggle.com/datasets/shusrith/fallalld", "excel"),
        ],
        downloader="kaggle",
        download_kwargs={"slug": "shusrith/fallalld"},
        notes="Fuente oficial requiere cuenta/suscripcion IEEE DataPort (sin credenciales disponibles); se descarga el mirror publico de Kaggle.",
    ),
    Dataset(
        key="UP-Fall",
        title="UP-Fall (HAR-UP)",
        category="1. Oficial / Validado",
        access="public_auto",
        urls=[
            ("Oficial (Google Sites)", "https://sites.google.com/up.edu.mx/har-up/", "excel"),
        ],
        downloader="gdrive_files",
        download_kwargs={
            "files": [
                ("1JBGU5W2uq9rl8h7bJNt2lN4SjfZnFxmQ", "DataSet_complete.csv"),
                ("18YHXLEZsvz4_9E_maWS3lCDMp2cbzXk0", "Features_1_0.5_complete.csv"),
                ("1ANpVZM7RcspnUNh3gUKclOxLy3nNU45n", "Features_2_1_complete.csv"),
                ("1OTwjR_FxqNy6xlkqDsymr4p8n8hcL-ee", "Features_3_1.5_complete.csv"),
                ("1ODKuWLRgC8Vxbp9gkhWr6zYs7Ifg3M8v", "CameraResizedOF_complete.csv"),
                ("1de9pSwlvOk5Od1qC61fg7Btl-OfFrSNK", "CameraOFFeatures_1_0.5_complete.csv"),
                ("1Shis-PVnRy45LMU0imsLyjtX-CNScW42", "CameraOFFeatures_2_1_complete.csv"),
                ("1FUEttXncJTSO3v10P8rIWuSDN_2jGazH", "CameraOFFeatures_3_1.5_complete.csv"),
            ]
        },
        notes="Links 'Complete Downloads' extraidos del widget embebido en la pagina oficial (Google Drive). "
              "Las imagenes/video completos por cada camara (CameraX / CameraX_OF por sujeto-actividad-ensayo, "
              "561 combinaciones) no se descargan aqui por volumen; quedan documentadas en el README para descarga puntual.",
    ),
    Dataset(
        key="UMAFall",
        title="UMAFall",
        category="1. Oficial / Validado",
        access="public_auto",
        urls=[("Oficial en Figshare", "https://figshare.com/articles/dataset/UMA_ADL_FALL_Dataset_zip/4214283", "excel")],
        downloader="figshare",
        download_kwargs={"article_id": "4214283"},
    ),
    Dataset(
        key="WEDA_Fall",
        title="WEDA Fall",
        category="1. Oficial / Validado",
        access="public_auto",
        urls=[
            ("Publicacion oficial (MDPI Sensors 2023)", "https://www.mdpi.com/1424-8220/23/24/9888", "excel"),
            ("Repositorio de datos (GitHub)", "https://github.com/joaojtmarques/WEDA-FALL", "web"),
        ],
        downloader="github_repo_zip",
        download_kwargs={"owner": "joaojtmarques", "repo": "WEDA-FALL", "branch": "main"},
        notes="El Excel solo citaba la publicacion MDPI sin URL de datos; el repositorio de GitHub se identifico "
              "mediante busqueda web (no proviene del Excel).",
    ),
    Dataset(
        key="TST_Fall_v1",
        title="TST Fall Detection v1 (Original)",
        category="1. Oficial / Validado",
        access="restricted",
        urls=[("Oficial (IEEE DataPort, requiere suscripcion)", "https://ieee-dataport.org/documents/tst-fall-detection-dataset-v1", "excel")],
        notes="Requiere cuenta/suscripcion IEEE DataPort; sin credenciales disponibles en este proyecto. Ver version modificada (TST_Fall_Modificado) como alternativa publica.",
    ),
    Dataset(
        key="TST_Fall_v2",
        title="TST Fall Detection v2 (Original)",
        category="1. Oficial / Validado",
        access="restricted",
        urls=[("Oficial (IEEE DataPort, requiere suscripcion)", "https://ieee-dataport.org/documents/tst-fall-detection-dataset-v2", "excel")],
        notes="Requiere cuenta/suscripcion IEEE DataPort; sin credenciales disponibles en este proyecto. Ver version modificada (TST_Fall_Modificado) como alternativa publica.",
    ),
    Dataset(
        key="TST_Fall_Modificado",
        title="TST Fall Detection Modificado (Unicomfacauca)",
        category="1. Oficial / Validado",
        access="public_auto",
        urls=[("Mirror modificado en Zenodo", "https://zenodo.org/records/3961894", "excel")],
        downloader="zenodo",
        download_kwargs={"record_id": "3961894"},
    ),
    Dataset(
        key="UNIVRFall",
        title="UNIVRFall",
        category="1. Oficial / Validado",
        access="public_auto",
        urls=[("Oficial en Zenodo (2026)", "https://zenodo.org/records/18346755", "excel")],
        downloader="zenodo",
        download_kwargs={"record_id": "18346755"},
    ),
    Dataset(
        key="SmartFallMM",
        title="SmartFallMM",
        category="1. Oficial / Validado",
        access="public_auto",
        urls=[("Oficial en GitHub", "https://github.com/txst-cs-smartfall/SmartFallMM-Dataset", "excel")],
        downloader="github_repo_zip",
        download_kwargs={"owner": "txst-cs-smartfall", "repo": "SmartFallMM-Dataset", "branch": "main"},
    ),
    Dataset(
        key="FARSEEING",
        title="FARSEEING",
        category="1. Oficial / Validado",
        access="restricted",
        urls=[("Sitio del consorcio (solicitud a comite cientifico)", "http://www.farseeingresearch.eu", "excel")],
        notes="Acceso por solicitud formal a comite cientifico; no automatizable.",
    ),
    Dataset(
        key="MobiAct",
        title="MobiAct (Version 2 Oficial)",
        category="1. Oficial / Validado",
        access="restricted",
        urls=[
            ("Sitio del grupo BMI (HMU)", "http://www.bmi.hmu.gr/", "excel"),
            ("Contacto para solicitud", "mailto:bmi@hmu.gr", "excel"),
        ],
        notes="Sitio oficial no respondio de forma estable al intentar el acceso automatizado; acceso publico/por solicitud segun el grupo BMI.",
    ),
    Dataset(
        key="MobiFall",
        title="MobiFall",
        category="1. Oficial / Validado",
        access="restricted",
        urls=[("Sitio del grupo BMI (HMU)", "http://www.bmi.hmu.gr/", "excel")],
        notes="Mismo portal que MobiAct; sitio no respondio de forma estable al intentar el acceso automatizado.",
    ),
    Dataset(
        key="Graz_UT_OL",
        title="Graz UT OL",
        category="1. Oficial / Validado",
        access="public_auto",
        urls=[("Oficial en Figshare",
               "https://figshare.com/articles/dataset/Dataset_for_Mobile_Phone_Sensing_Based_Fall_Detection/1444405",
               "excel")],
        downloader="figshare",
        download_kwargs={"article_id": "1444405"},
    ),
    Dataset(
        key="UR_Fall_Detection",
        title="UR Fall Detection",
        category="1. Oficial / Validado",
        access="public_auto",
        urls=[("Oficial", "http://fenix.ur.edu.pl/~mkepski/ds/uf.html", "excel")],
        downloader="ur_fall",
        notes="Se descargan los CSV inerciales (fall/adl data+acc y urfall-cam0-*); las imagenes RGB/Depth (ZIP pesados) no se incluyen por volumen.",
    ),
    Dataset(
        key="DOFDA",
        title="DOFDA",
        category="1. Oficial / Validado",
        access="restricted",
        urls=[("Publicacion (Data in Brief, Elsevier 2019)", "Data in Brief (Elsevier) 2019", "excel")],
        notes="El Excel no trae URL de descarga (solo cita la publicacion); no se encontro repositorio publico de datos accesible.",
    ),
    Dataset(
        key="Erciyes_University",
        title="Erciyes University",
        category="1. Oficial / Validado",
        access="restricted",
        urls=[("Publicacion (Erciyes University / MDPI Sensors 2014)", "Erciyes University / MDPI Sensors 2014", "excel")],
        notes="El Excel no trae URL de descarga (solo cita la publicacion); no se encontro repositorio publico de datos accesible.",
    ),
    Dataset(
        key="IMUFD",
        title="IMUFD",
        category="1. Oficial / Validado",
        access="restricted",
        urls=[("Grupo de investigacion", "Simon Fraser University IPML Lab", "excel")],
        notes="Acceso publico/por solicitud segun el Excel; sin URL de descarga directa disponible.",
    ),
    Dataset(
        key="DLR",
        title="DLR",
        category="1. Oficial / Validado",
        access="restricted",
        urls=[("Institucion", "German Aerospace Center (DLR)", "excel")],
        notes="Por solicitud / restringido segun el Excel; sin URL de descarga directa disponible.",
    ),
    Dataset(
        key="FFFStudy",
        title="FFFStudy",
        category="1. Oficial / Validado",
        access="restricted",
        urls=[("Publicacion / institucion", "IEEE JBHI / Veterans Affairs Portland", "excel")],
        notes="El Excel no trae URL de descarga; busqueda web no encontro repositorio publico de datos accesible.",
    ),
    Dataset(
        key="LTMM",
        title="LTMM",
        category="1. Oficial / Validado",
        access="public_auto",
        urls=[
            ("Institucion (segun Excel)", "Tel Aviv Sourasky Medical Center", "excel"),
            ("Repositorio real de datos: PhysioNet", "https://physionet.org/content/ltmm/1.0.0/", "web"),
        ],
        downloader="physionet_sample",
        download_kwargs={
            "project": "ltmm",
            "version": "1.0.0",
            "files": ["ClinicalDemogData_COFL.xlsx", "ReportHome75h.xlsx", "RECORDS", "SHA256SUMS.txt"],
        },
        notes="El Excel no traia URL; se identifico mediante busqueda web que el dataset esta publicado en PhysioNet "
              "(20.8GB en total, wget -r -N -c -np https://physionet.org/files/ltmm/1.0.0/). Dado que este dataset "
              "reporta 0 caidas (solo monitoreo de marcha/ADL en adultos mayores), aqui solo se descargan los archivos "
              "de metadatos/indice como muestra; la descarga completa de las señales .dat/.hea (~300MB cada uno, 71 "
              "sujetos) queda documentada para ejecutarse bajo demanda si se requiere.",
    ),
    Dataset(
        key="Smartphone_Human_Fall_Dataset",
        title="Smartphone Human Fall Dataset",
        category="2. Comunidad / Kaggle",
        access="kaggle_mirror",
        urls=[("Kaggle", "https://www.kaggle.com/datasets/saadmansakib/smartphone-human-fall-dataset", "excel")],
        downloader="kaggle",
        download_kwargs={"slug": "saadmansakib/smartphone-human-fall-dataset"},
    ),
    Dataset(
        key="Falls_vs_Normal_Activities",
        title="Falls vs Normal Activities",
        category="2. Comunidad / Kaggle",
        access="kaggle_mirror",
        urls=[("Kaggle", "https://www.kaggle.com/datasets/enricogrimaldi/falls-vs-normal-activities", "excel")],
        downloader="kaggle",
        download_kwargs={"slug": "enricogrimaldi/falls-vs-normal-activities"},
    ),
    Dataset(
        key="Elderly_Fall_Detection_IoT",
        title="Elderly Fall Detection IoT Dataset",
        category="2. Comunidad / Kaggle",
        access="kaggle_mirror",
        urls=[("Kaggle", "https://www.kaggle.com/datasets/ziya07/elderly-fall-detection-iot-dataset", "excel")],
        downloader="kaggle",
        download_kwargs={"slug": "ziya07/elderly-fall-detection-iot-dataset"},
    ),
    Dataset(
        key="Real_Time_Patient_Fall_Detection",
        title="Real-Time Patient Fall Detection Data",
        category="2. Comunidad / Kaggle",
        access="kaggle_mirror",
        urls=[("Kaggle", "https://www.kaggle.com/datasets/zara2099/real-time-patient-fall-detection-data", "excel")],
        downloader="kaggle",
        download_kwargs={"slug": "zara2099/real-time-patient-fall-detection-data"},
    ),
    Dataset(
        key="Ultralytics_Fall_Detect",
        title="Ultralytics Fall-Detect Community Dataset (Imagenes)",
        category="2. Comunidad / Vision",
        access="restricted",
        urls=[("Ultralytics Platform (requiere login para export)",
               "https://platform.ultralytics.com/nicolai-nielsen/datasets/fall-detect", "excel")],
        notes="Requiere iniciar sesion en la plataforma Ultralytics para habilitar el export/descarga; no automatizable sin credenciales.",
    ),
]


def find_dataset(key: str) -> Dataset:
    for ds in DATASETS:
        if ds.key.lower() == key.lower():
            return ds
    raise KeyError(key)


def run(only: Optional[list] = None) -> None:
    load_env_tokens()
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    log_lines = ["dataset,access,status,file,detail,size_bytes,timestamp"]
    targets = DATASETS if not only else [find_dataset(k) for k in only]
    for ds in targets:
        print(f"\n=== {ds.key} ({ds.access}) ===", flush=True)
        write_url_file(ds)
        if ds.access == "restricted" or ds.downloader is None:
            print("  [restringido] solo se documenta URL de acceso, sin descarga.", flush=True)
            log_lines.append(f"{ds.key},{ds.access},restricted,,,0,{time.time()}")
            continue
        fn = DOWNLOADERS[ds.downloader]
        try:
            results = fn(ds, **ds.download_kwargs)
        except Exception as e:  # noqa: BLE001
            print(f"  [error general] {e}", flush=True)
            log_lines.append(f"{ds.key},{ds.access},error,,{e},0,{time.time()}")
            continue
        for name, status, size in results:
            print(f"  - {name}: {status} ({size} bytes)", flush=True)
            log_lines.append(f"{ds.key},{ds.access},{status},{name},,{size},{time.time()}")
        LOG_PATH.write_text("\n".join(log_lines) + "\n", encoding="utf-8")
    LOG_PATH.write_text("\n".join(log_lines) + "\n", encoding="utf-8")
    print(f"\nLog guardado en {LOG_PATH}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", help="lista separada por comas de keys de datasets")
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()
    if args.list:
        for ds in DATASETS:
            print(f"{ds.key:35s} {ds.access:15s} {ds.title}")
        sys.exit(0)
    only = [s.strip() for s in args.only.split(",")] if args.only else None
    run(only)
