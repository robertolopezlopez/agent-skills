#!/usr/bin/env python3
"""Shared runtime config home resolution for Python skill helpers."""
from __future__ import annotations

import os
from pathlib import Path


def detect_runtime(infer_from: Path | None = None) -> str:
    override = (os.environ.get("AGENT_SKILLS_RUNTIME") or "").strip().lower()
    if override in {"cursor", "codex"}:
        return override

    if infer_from is not None:
        parts = infer_from.resolve().parts
        for idx, part in enumerate(parts):
            if part in {".cursor", ".codex"} and idx + 1 < len(parts) and parts[idx + 1] == "skills":
                return "cursor" if part == ".cursor" else "codex"

    if (Path.home() / ".cursor" / "skills").is_dir():
        return "cursor"
    if (Path.home() / ".codex" / "skills").is_dir():
        return "codex"
    return "cursor"


def config_home(runtime: str | None = None, infer_from: Path | None = None) -> Path:
    resolved = runtime or detect_runtime(infer_from)
    return Path.home() / (".cursor" if resolved == "cursor" else ".codex")


def env_file_path(basename: str, infer_from: Path | None = None) -> Path:
    return config_home(infer_from=infer_from) / basename


def read_env_var(name: str, basename: str, infer_from: Path | None = None) -> str | None:
    path = env_file_path(basename, infer_from=infer_from)
    if not path.is_file():
        return None
    prefix = f"{name}="
    for line in path.read_text().splitlines():
        if line.startswith("#") or not line.startswith(prefix):
            continue
        value = line.split("=", 1)[1].strip()
        if value:
            return value
    return None


def resolve_installed_script(name: str, infer_from: Path | None = None) -> Path | None:
    infer_from = infer_from or Path(__file__)
    candidates = [
        infer_from.resolve().parents[4] / "scripts" / name,
        config_home(infer_from=infer_from) / "skills" / "scripts" / name,
    ]
    seen: set[Path] = set()
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        if resolved.is_file():
            return resolved
    return None
