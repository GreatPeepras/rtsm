"""
RTSM configuration loader.

Config YAML files live in this package directory (rtsm/cfg/) and ship with
pip install. For dev checkouts, a `config/` symlink at repo root points here.

Usage:
    from rtsm.cfg import load_config, cfg_path

    cfg = load_config()                     # loads rtsm.yaml
    cfg = load_config("demo_config.yaml")   # loads demo_config.yaml
    path = cfg_path("clip/vocab.yaml")      # resolves to file path
"""

from __future__ import annotations

from importlib import resources
from pathlib import Path
from typing import Any, Dict


def cfg_path(name: str = "rtsm.yaml") -> Path:
    """Resolve a config file path.

    Lookup order:
      1. importlib.resources (works for pip-installed package)
      2. CWD-relative ``config/<name>`` (legacy dev path via symlink)

    Args:
        name: Relative path within the cfg package, e.g. ``"rtsm.yaml"``
              or ``"clip/vocab.yaml"``.

    Returns:
        Resolved :class:`Path` to the config file.

    Raises:
        FileNotFoundError: If the config file cannot be found.
    """
    # 1. Package resource (canonical — ships in wheel)
    pkg_path = resources.files("rtsm.cfg").joinpath(name)
    resolved = Path(str(pkg_path))
    if resolved.is_file():
        return resolved

    # 2. CWD-relative fallback (symlink or old layout)
    cwd_path = Path("config") / name
    if cwd_path.is_file():
        return cwd_path

    raise FileNotFoundError(
        f"Config file not found: {name!r}. "
        f"Searched: {resolved}, {cwd_path.resolve()}"
    )


def load_config(name: str = "rtsm.yaml") -> Dict[str, Any]:
    """Load and parse a YAML config file.

    Args:
        name: Config filename (default ``"rtsm.yaml"``).

    Returns:
        Parsed config dict.
    """
    import yaml

    path = cfg_path(name)
    return yaml.safe_load(path.read_text(encoding="utf-8"))
