"""Resource helpers for loading and saving game data."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parent.parent.parent
SAVE_DIR = ROOT / "saves"
SAVE_DIR.mkdir(exist_ok=True)


def load_config(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing config file: {path}")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: Dict[str, Any]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_json(path: Path, default: Dict[str, Any] | None = None) -> Dict[str, Any]:
    if not path.exists():
        return default or {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_world(name: str, data: Dict[str, Any]):
    save_path = SAVE_DIR / f"{name}.json"
    save_json(save_path, data)


def load_world(name: str) -> Dict[str, Any]:
    return load_json(SAVE_DIR / f"{name}.json", {})


def data_path(*parts: str) -> Path:
    return ROOT.joinpath(*parts)
