"""Traceable input/output helpers shared by the five plotting scripts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def source_path(relative_path: str) -> Path:
    path = PROJECT_ROOT / relative_path
    if not path.exists():
        raise FileNotFoundError(f"Required source data not found: {relative_path}")
    return path


def read_csv(relative_path: str, **kwargs) -> pd.DataFrame:
    return pd.read_csv(source_path(relative_path), **kwargs)


def sha256(relative_path: str) -> str:
    digest = hashlib.sha256()
    with source_path(relative_path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_manifest(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
