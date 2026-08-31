"""Utilities to curate and validate wearable fall-detection datasets."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Iterable, List, Optional

import pandas as pd
import requests


@dataclass
class DatasetEntry:
    name: str
    source_type: str  # official, mirror, article, community
    access_type: str  # public, request, restricted, unknown
    modalities: str
    sensors: str
    base_url: str
    mirror_url: str = ""
    kaggle_slug: str = ""
    notes: str = ""


CORE_DATASETS: List[DatasetEntry] = [
    DatasetEntry(
        name="DLR",
        source_type="article",
        access_type="request",
        modalities="inertial",
        sensors="A,G,M",
        base_url="",
        notes="No official public landing page found in current references.",
    ),
    DatasetEntry(
        name="MobiAct",
        source_type="official",
        access_type="request",
        modalities="inertial",
        sensors="A,G,O",
        base_url="mailto:bmi@hmu.gr",
        notes="Access is commonly granted after contact with maintainers.",
    ),
    DatasetEntry(
        name="TST Fall detection",
        source_type="mirror",
        access_type="public",
        modalities="vision",
        sensors="A",
        base_url="https://zenodo.org/records/3961894",
        notes="This is a modified community version hosted on Zenodo.",
    ),
    DatasetEntry(
        name="tFall",
        source_type="community",
        access_type="public",
        modalities="vision",
        sensors="A",
        base_url="https://platform.ultralytics.com/nicolai-nielsen/datasets/fall-detect",
        notes="Community mirror focused on image/object-detection workflows.",
    ),
    DatasetEntry(
        name="UR Fall Detection",
        source_type="official",
        access_type="public",
        modalities="vision+inertial",
        sensors="A",
        base_url="http://fenix.ur.edu.pl/~mkepski/ds/uf.html",
        notes="Official page lists downloadable sequence files.",
    ),
    DatasetEntry(
        name="Cogent Labs",
        source_type="article",
        access_type="request",
        modalities="inertial",
        sensors="A,G",
        base_url="https://www.researchgate.net/",
        notes="Typically requested through paper authors/ResearchGate.",
    ),
    DatasetEntry(
        name="Gravity Project",
        source_type="article",
        access_type="request",
        modalities="inertial",
        sensors="A",
        base_url="",
        notes="No centralized public repository identified in current references.",
    ),
    DatasetEntry(
        name="Graz",
        source_type="official",
        access_type="public",
        modalities="inertial",
        sensors="A,O",
        base_url="https://figshare.com/articles/dataset/Dataset_for_Mobile_Phone_Sensing_Based_Fall_Detection/1444405",
        notes="Figshare page may require manual browser verification.",
    ),
    DatasetEntry(
        name="UMAFall",
        source_type="official",
        access_type="public",
        modalities="inertial",
        sensors="A,G,M",
        base_url="https://figshare.com/articles/dataset/UMA_ADL_FALL_Dataset_zip/4214283",
        notes="Figshare page may require manual browser verification.",
    ),
    DatasetEntry(
        name="SisFall",
        source_type="mirror",
        access_type="public",
        modalities="inertial",
        sensors="A,G",
        base_url="https://www.kaggle.com/datasets/thevman/sisfall-dataset",
        mirror_url="https://www.kaggle.com/datasets/adityavvvn/sisfall",
        kaggle_slug="thevman/sisfall-dataset",
        notes="Original university link is often unavailable; mirrors are common.",
    ),
    DatasetEntry(
        name="UniMiB SHAR",
        source_type="community",
        access_type="public",
        modalities="inertial",
        sensors="A",
        base_url="https://www.kaggle.com/datasets?search=unimib+shar",
        notes="Official source can be unstable; community mirrors are frequent.",
    ),
    DatasetEntry(
        name="UP-Fall",
        source_type="official",
        access_type="public",
        modalities="multimodal",
        sensors="A,G,light,IR,EEG,camera",
        base_url="https://sites.google.com/up.edu.mx/har-up/",
        notes="Large multimodal dataset with CSV subsets and feature files.",
    ),
]


ADDITIONAL_DATASETS: List[DatasetEntry] = [
    DatasetEntry(
        name="KFall Dataset (Kaggle mirror)",
        source_type="mirror",
        access_type="public",
        modalities="inertial",
        sensors="A,G,M",
        base_url="https://www.kaggle.com/datasets/usmanabbasi2002/kfall-dataset",
        mirror_url="https://www.kaggle.com/datasets/kushajmallick/kfall-fulldata",
        kaggle_slug="usmanabbasi2002/kfall-dataset",
    ),
    DatasetEntry(
        name="FallAllD (Kaggle mirror)",
        source_type="mirror",
        access_type="public",
        modalities="inertial",
        sensors="A,G,M",
        base_url="https://www.kaggle.com/datasets/shusrith/fallalld",
        mirror_url="https://www.kaggle.com/datasets/kofischolar/fallalld-dataset",
        kaggle_slug="shusrith/fallalld",
    ),
    DatasetEntry(
        name="Real-Time Patient Fall Detection",
        source_type="community",
        access_type="public",
        modalities="multimodal",
        sensors="A,G,heart_rate,room_context",
        base_url="https://www.kaggle.com/datasets/zara2099/real-time-patient-fall-detection-data",
        kaggle_slug="zara2099/real-time-patient-fall-detection-data",
    ),
    DatasetEntry(
        name="Elderly Fall Detection IoT",
        source_type="community",
        access_type="public",
        modalities="multimodal",
        sensors="A,G,orientation,ambient",
        base_url="https://www.kaggle.com/datasets/ziya07/elderly-fall-detection-iot-dataset",
    ),
    DatasetEntry(
        name="Smartphone Human Fall Dataset",
        source_type="community",
        access_type="public",
        modalities="inertial-features",
        sensors="A,G",
        base_url="https://www.kaggle.com/datasets/saadmansakib/smartphone-human-fall-dataset",
    ),
    DatasetEntry(
        name="Falls vs Normal Activities",
        source_type="community",
        access_type="public",
        modalities="inertial",
        sensors="A,G",
        base_url="https://www.kaggle.com/datasets/enricogrimaldi/falls-vs-normal-activities",
    ),
]


def to_dataframe(entries: Iterable[DatasetEntry]) -> pd.DataFrame:
    return pd.DataFrame([asdict(item) for item in entries])


def _http_status(url: str, timeout: int = 20) -> Optional[int]:
    if not url or not url.startswith(("http://", "https://")):
        return None

    try:
        response = requests.get(url, timeout=timeout, allow_redirects=True)
        return int(response.status_code)
    except requests.RequestException:
        return None


def validate_catalog(entries: Iterable[DatasetEntry], timeout: int = 20) -> pd.DataFrame:
    rows = []
    for item in entries:
        status = _http_status(item.base_url, timeout=timeout)
        mirror_status = _http_status(item.mirror_url, timeout=timeout) if item.mirror_url else None

        if status is not None and 200 <= status < 400:
            availability = "reachable"
        elif mirror_status is not None and 200 <= mirror_status < 400:
            availability = "reachable_via_mirror"
        elif item.access_type == "request":
            availability = "request_required"
        elif not item.base_url:
            availability = "no_public_url"
        else:
            availability = "not_reachable"

        rows.append(
            {
                "name": item.name,
                "source_type": item.source_type,
                "access_type": item.access_type,
                "base_url": item.base_url,
                "base_status": status,
                "mirror_url": item.mirror_url,
                "mirror_status": mirror_status,
                "availability": availability,
                "modalities": item.modalities,
                "sensors": item.sensors,
                "kaggle_slug": item.kaggle_slug,
                "notes": item.notes,
            }
        )

    return pd.DataFrame(rows)


def availability_summary(validation_df: pd.DataFrame) -> pd.DataFrame:
    if validation_df.empty:
        return pd.DataFrame(columns=["availability", "count"])

    summary = (
        validation_df["availability"]
        .value_counts(dropna=False)
        .rename_axis("availability")
        .reset_index(name="count")
    )
    return summary
