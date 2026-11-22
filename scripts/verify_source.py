#!/usr/bin/env python3
from pathlib import Path
import ast
import sys

ROOT = Path(__file__).resolve().parents[1]
errors = []

for path in ROOT.glob("**/*.py"):
    if any(part in {".venv", "__pycache__", ".git", ".pytest_cache", ".mypy_cache", ".ruff_cache"} for part in path.parts):
        continue
    try:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except Exception as exc:
        errors.append(f"{path}: {exc}")

for forbidden in ("VertexERP-" + "AI-main", "Music/VertexERP" + "-AI"):
    for path in ROOT.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".py",".toml",".yml",".yaml",".ts",".tsx",".json",".conf",".ini"}:
            if any(part in {".venv","node_modules",".git","__pycache__"} for part in path.parts):
                continue
            try:
                if forbidden in path.read_text(encoding="utf-8", errors="ignore"):
                    errors.append(f"forbidden reference '{forbidden}' in {path}")
            except OSError:
                pass

if errors:
    print("SOURCE VERIFICATION FAILED")
    print("\n".join(errors))
    sys.exit(1)

print("SOURCE VERIFICATION PASSED")
