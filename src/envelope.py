import json
import random
from pathlib import Path


def load_random_envelope(construction_dir: Path) -> dict:
    json_files = [p for p in construction_dir.iterdir() if p.is_file() and p.suffix.lower() == ".json"]
    if not json_files:
        raise RuntimeError(f"❌ construction 文件夹中未找到任何 json 文件: {construction_dir}")

    json_path = random.choice(json_files)
    with open(json_path, "r", encoding="utf-8") as f:
        envelope = json.load(f)

    return envelope
