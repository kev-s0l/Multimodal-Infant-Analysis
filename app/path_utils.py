from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType


if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    REPO_ROOT = Path(sys._MEIPASS)
else:
    REPO_ROOT = Path(__file__).resolve().parents[1]


def load_module(module_name: str, relative_path: str) -> ModuleType:
    """Load a repo module by file path under a unique app-local name."""
    module_path = REPO_ROOT / relative_path
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module from {module_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def require_path(path: str, label: str) -> Path:
    candidate = Path(path).expanduser()
    if not candidate.exists():
        raise FileNotFoundError(f"{label} not found: {candidate}")
    return candidate
