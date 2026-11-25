#!/usr/bin/env python3
"""Empaqueta cada skill en dist/<skill>.zip, listo para subir a una Release.

Uso:
    python tools/empaquetar.py [skill ...]   # sin argumentos, todas las skills

El zip lleva la carpeta de la skill como raíz (<skill>/SKILL.md, scripts/,
references/, assets/), que es lo que pide la subida de skills de Claude.ai.
Se dejan fuera tests/, examples/, __pycache__, los .pyc, README.md (sus
imágenes apuntan al repo) y los portables (son para chats sin skills).
Solo librería estándar.
"""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
DIST = RAIZ / "dist"
EXCLUIR_CARPETAS = {"tests", "examples", "__pycache__", ".pytest_cache"}
EXCLUIR_ARCHIVOS = {"README.md", "prompt-portable.md", "prompt-portable-lite.md", ".DS_Store", "Thumbs.db"}
EXCLUIR_EXT = {".pyc", ".pyo"}
FECHA_FIJA = (2026, 1, 1, 0, 0, 0)  # zips reproducibles: mismo contenido, mismos bytes


def skills() -> list[Path]:
    return sorted(d for d in (RAIZ / "skills").iterdir() if d.is_dir() and (d / "SKILL.md").is_file())


def archivos(skill: Path) -> list[Path]:
    incluidos = []
    for f in sorted(skill.rglob("*")):
        relativo = f.relative_to(skill)
        if not f.is_file() or set(relativo.parts[:-1]) & EXCLUIR_CARPETAS:
            continue
        if relativo.parts[0] in EXCLUIR_CARPETAS or f.name in EXCLUIR_ARCHIVOS or f.suffix in EXCLUIR_EXT:
            continue
        incluidos.append(f)
    return incluidos


def empaquetar(skill: Path, destino: Path = DIST) -> Path:
    destino.mkdir(parents=True, exist_ok=True)
    zip_path = destino / f"{skill.name}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for f in archivos(skill):
            info = zipfile.ZipInfo(f"{skill.name}/{f.relative_to(skill).as_posix()}", FECHA_FIJA)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o755 if f.suffix == ".py" else 0o644) << 16
            z.writestr(info, f.read_bytes())
    return zip_path


def main(argv: list[str]) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    todas = {s.name: s for s in skills()}
    pedidas = argv[1:] or list(todas)
    desconocidas = [p for p in pedidas if p not in todas]
    if desconocidas:
        print(f"Skills desconocidas: {', '.join(desconocidas)}. Disponibles: {', '.join(todas)}", file=sys.stderr)
        return 1
    for nombre in pedidas:
        zip_path = empaquetar(todas[nombre])
        with zipfile.ZipFile(zip_path) as z:
            n = len(z.namelist())
        print(f"{zip_path.relative_to(RAIZ).as_posix()}: {n} archivos, {zip_path.stat().st_size / 1024:.0f} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
