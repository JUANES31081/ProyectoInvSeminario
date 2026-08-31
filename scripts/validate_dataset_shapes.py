from __future__ import annotations

import csv
import json
import os
from pathlib import Path
from typing import Any

import pandas as pd


def load_env_token(project_root: Path) -> None:
    env_path = project_root / ".env"
    if not env_path.exists():
        return
    try:
        for line in env_path.read_text(encoding="utf-8").splitlines():
            if "=" not in line:
                continue
            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if k == "KAGGLE_API" and v and not os.environ.get("KAGGLE_API_TOKEN"):
                os.environ["KAGGLE_API_TOKEN"] = v
            elif k in {"KAGGLE_USERNAME", "KAGGLE_KEY", "KAGGLE_API_TOKEN"} and v and not os.environ.get(k):
                os.environ[k] = v
    except Exception:
        pass


def has_kaggle_auth() -> bool:
    legacy = bool(os.environ.get("KAGGLE_USERNAME") and os.environ.get("KAGGLE_KEY"))
    token = bool(os.environ.get("KAGGLE_API_TOKEN"))
    return legacy or token


def sniff_delimiter(file_path: Path) -> str:
    try:
        with file_path.open("r", encoding="utf-8", errors="replace") as f:
            sample = f.read(4096)
        dialect = csv.Sniffer().sniff(sample, delimiters=[",", ";", "\t", "|"])
        return dialect.delimiter
    except Exception:
        return ","


def count_rows_cols(file_path: Path) -> dict[str, Any]:
    delim = sniff_delimiter(file_path)
    rows = 0
    cols = None
    has_header = False
    try:
        with file_path.open("r", encoding="utf-8", errors="replace", newline="") as f:
            reader = csv.reader(f, delimiter=delim)
            for i, row in enumerate(reader):
                if i == 0:
                    cols = len(row)
                    # Heuristica simple para detectar header
                    has_header = any(not c.replace(".", "", 1).replace("-", "", 1).isdigit() for c in row if c != "")
                rows += 1
        if rows > 0 and has_header:
            rows -= 1
        return {
            "rows": int(rows),
            "cols": int(cols or 0),
            "delimiter": delim,
            "ok": True,
            "error": "",
        }
    except Exception as e:
        return {
            "rows": None,
            "cols": None,
            "delimiter": delim,
            "ok": False,
            "error": str(e)[:300],
        }


def summarize_csv_tree(root: Path) -> dict[str, Any]:
    csv_files = sorted(root.rglob("*.csv"))
    if not csv_files:
        return {
            "csv_files": 0,
            "total_rows": None,
            "min_cols": None,
            "max_cols": None,
            "sample_file": "",
            "sample_shape": "N/D",
            "errors": [],
        }

    total_rows = 0
    min_cols = None
    max_cols = None
    errors: list[str] = []

    sample_file = csv_files[0]
    sample_shape = "N/D"

    for i, fp in enumerate(csv_files):
        stats = count_rows_cols(fp)
        if not stats["ok"]:
            errors.append(f"{fp.name}: {stats['error']}")
            continue

        rows = stats["rows"]
        cols = stats["cols"]
        total_rows += int(rows)

        if min_cols is None or cols < min_cols:
            min_cols = cols
        if max_cols is None or cols > max_cols:
            max_cols = cols

        if i == 0:
            sample_shape = f"({rows}, {cols})"

    return {
        "csv_files": len(csv_files),
        "total_rows": int(total_rows),
        "min_cols": min_cols,
        "max_cols": max_cols,
        "sample_file": str(sample_file.relative_to(root)).replace("\\", "/"),
        "sample_shape": sample_shape,
        "errors": errors[:10],
    }


def summarize_upfall_local(project_root: Path) -> list[dict[str, Any]]:
    up_dir = project_root / "datasets" / "UP-Fall"
    rows: list[dict[str, Any]] = []
    if not up_dir.exists():
        return rows

    for p in sorted(up_dir.glob("*.csv")):
        try:
            df = pd.read_csv(p, low_memory=False)
            rows.append({
                "dataset": "UP-Fall (local)",
                "file": p.name,
                "rows": int(df.shape[0]),
                "cols": int(df.shape[1]),
                "shape": f"({int(df.shape[0])}, {int(df.shape[1])})",
            })
        except Exception as e:
            rows.append({
                "dataset": "UP-Fall (local)",
                "file": p.name,
                "rows": None,
                "cols": None,
                "shape": "N/D",
                "error": str(e)[:240],
            })
    return rows


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    out_dir = project_root / "datasets" / "dataset_downloads"
    out_dir.mkdir(parents=True, exist_ok=True)
    analytics_dir = project_root / "analytics"
    analytics_dir.mkdir(parents=True, exist_ok=True)

    load_env_token(project_root)

    kaggle_targets = {
        "SisFall (mirror Kaggle)": ["thevman/sisfall-dataset", "adityavvvn/sisfall"],
        "KFall (mirror Kaggle)": ["usmanabbasi2002/kfall-dataset", "kushajmallick/kfall-fulldata"],
        "FallAllD (mirror Kaggle)": ["shusrith/fallalld", "kofischolar/fallalld-dataset"],
        "Real-Time Patient Fall": ["zara2099/real-time-patient-fall-detection-data"],
        "Elderly Fall Detection IoT": ["ziya07/elderly-fall-detection-iot-dataset"],
        "Smartphone Human Fall Dataset": ["saadmansakib/smartphone-human-fall-dataset"],
        "Falls vs Normal Activities": ["enricogrimaldi/falls-vs-normal-activities"],
    }

    download_summary: list[dict[str, Any]] = []

    kaggle_ok = has_kaggle_auth()
    if kaggle_ok:
        import kagglehub  # type: ignore

        short_cache = Path("C:/khcache")
        short_cache.mkdir(parents=True, exist_ok=True)
        os.environ["KAGGLEHUB_CACHE"] = str(short_cache)

        for dataset_name, slugs in kaggle_targets.items():
            dataset_result: dict[str, Any] = {
                "dataset": dataset_name,
                "downloaded": False,
                "slug_used": None,
                "path": None,
                "shape_summary": None,
                "errors": [],
            }

            for slug in slugs:
                try:
                    path = Path(kagglehub.dataset_download(slug))
                    dataset_result["downloaded"] = True
                    dataset_result["slug_used"] = slug
                    dataset_result["path"] = str(path)
                    dataset_result["shape_summary"] = summarize_csv_tree(path)
                    break
                except Exception as e:
                    dataset_result["errors"].append(f"{slug}: {str(e)[:220]}")

            download_summary.append(dataset_result)
    else:
        for dataset_name in kaggle_targets:
            download_summary.append(
                {
                    "dataset": dataset_name,
                    "downloaded": False,
                    "slug_used": None,
                    "path": None,
                    "shape_summary": None,
                    "errors": ["No Kaggle credentials detected"],
                }
            )

    upfall_local = summarize_upfall_local(project_root)

    out_json = {
        "kaggle_auth_detected": kaggle_ok,
        "download_summary": download_summary,
        "upfall_local_files": upfall_local,
    }

    (analytics_dir / "dataset_shapes_validation.json").write_text(
        json.dumps(out_json, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    # Flatten CSV for quick reading
    rows_flat: list[dict[str, Any]] = []
    for item in download_summary:
        base = {
            "dataset": item["dataset"],
            "downloaded": item["downloaded"],
            "slug_used": item["slug_used"],
            "path": item["path"],
        }
        ss = item.get("shape_summary") or {}
        row = {
            **base,
            "csv_files": ss.get("csv_files"),
            "total_rows": ss.get("total_rows"),
            "min_cols": ss.get("min_cols"),
            "max_cols": ss.get("max_cols"),
            "sample_file": ss.get("sample_file"),
            "sample_shape": ss.get("sample_shape"),
            "errors": " | ".join(item.get("errors", [])[:3]),
        }
        rows_flat.append(row)

    pd.DataFrame(rows_flat).to_csv(analytics_dir / "dataset_shapes_validation.csv", index=False)
    pd.DataFrame(upfall_local).to_csv(analytics_dir / "upfall_local_shapes.csv", index=False)

    print("Validation completed")
    print(f"Kaggle auth detected: {kaggle_ok}")
    print(f"Report JSON: {analytics_dir / 'dataset_shapes_validation.json'}")
    print(f"Report CSV: {analytics_dir / 'dataset_shapes_validation.csv'}")
    print(f"UP-Fall local CSV shapes: {analytics_dir / 'upfall_local_shapes.csv'}")


if __name__ == "__main__":
    main()
