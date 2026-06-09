from pathlib import Path
from typing import Iterable, List
import pandas as pd


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_all_csv_names(folder_path: Path) -> List[str]:
    ensure_dir(folder_path)
    return [p.name for p in folder_path.iterdir() if p.is_file() and p.suffix.lower() == ".csv"]


def get_finished_indices(folder_path: Path, max_id: int) -> List[int]:
    csv_names = load_all_csv_names(folder_path)
    idxs = []
    for name in csv_names:
        try:
            idx = int(name.split("_")[0])
        except Exception:
            continue
        if idx < max_id:
            idxs.append(idx)
    return idxs


def append_summary_row(summary_csv: Path, row: dict) -> None:
    summary_csv.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame([row])
    if summary_csv.exists():
        df.to_csv(summary_csv, mode="a", header=False, index=False, encoding="utf-8-sig")
    else:
        df.to_csv(summary_csv, index=False, encoding="utf-8-sig")
