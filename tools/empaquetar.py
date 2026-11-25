#!/usr/bin/env python3
"""Empaqueta cada skill en dist/<skill>.zip, listo para subir a una Release.

Uso:
    python tools/empaquetar.py [skill ...]               # sin argumentos, todas las skills
    python tools/empaquetar.py --claude-ai [skill ...]   # variante para Claude.ai

El zip lleva la carpeta de la skill como raíz (<skill>/SKILL.md, scripts/,
references/, assets/), que es lo que pide la subida de skills de Claude.ai.
Se dejan fuera tests/, examples/, __pycache__, los .pyc, README.md (sus
imágenes apuntan al repo), los portables (son para chats sin skills) y
claude-ai.txt.

--claude-ai genera dist/claude-ai/<skill>.zip: igual que el normal, pero la
description del SKILL.md que va dentro del zip se sustituye por el texto de
skills/<skill>/claude-ai.txt (máx. 200 caracteres), por si la subida a
Claude.ai limita la descripción a esa longitud. El SKILL.md del repo no cambia
y no se añade ningún campo al frontmatter.
Solo librería estándar.
"""
from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
DIST = RAIZ / "dist"
CLAUDE_AI = "claude-ai.txt"
LIMITE_CLAUDE_AI = 200
EXCLUIR_CARPETAS = {"tests", "examples", "__pycache__", ".pytest_cache"}
EXCLUIR_ARCHIVOS = {"README.md", "prompt-portable.md", "prompt-portable-lite.md", CLAUDE_AI,
                    ".DS_Store", "Thumbs.db"}
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


def descripcion_corta(skill: Path) -> str:
    """Lee claude-ai.txt y comprueba que cabe en el límite de Claude.ai."""
    ruta = skill / CLAUDE_AI
    if not ruta.is_file():
        raise ValueError(f"{skill.name}: falta {CLAUDE_AI}")
    texto = ruta.read_text(encoding="utf-8").strip()
    if not texto or "\n" in texto:
        raise ValueError(f"{skill.name}/{CLAUDE_AI}: tiene que ser una sola línea, no vacía")
    if len(texto) > LIMITE_CLAUDE_AI:
        raise ValueError(f"{skill.name}/{CLAUDE_AI}: {len(texto)} caracteres (máx. {LIMITE_CLAUDE_AI})")
    return texto


def inyectar_descripcion(skill_md: str, descripcion: str) -> str:
    """Sustituye la description del frontmatter (de una línea o en bloque >-) por otra."""
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", skill_md, re.S)
    if not m:
        raise ValueError("SKILL.md sin frontmatter")
    frontmatter = m.group(1)
    nuevo, n = re.subn(r"^description:.*?(?=^\S|\Z)", lambda _: f"description: >-\n  {descripcion}\n",
                       frontmatter + "\n", count=1, flags=re.S | re.M)
    if n != 1:
        raise ValueError("SKILL.md sin campo description")
    return f"---\n{nuevo.rstrip()}\n---\n" + skill_md[m.end():]


def empaquetar(skill: Path, destino: Path = DIST, claude_ai: bool = False) -> Path:
    destino.mkdir(parents=True, exist_ok=True)
    corta = descripcion_corta(skill) if claude_ai else None
    zip_path = destino / f"{skill.name}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for f in archivos(skill):
            datos = f.read_bytes()
            if corta and f == skill / "SKILL.md":
                datos = inyectar_descripcion(datos.decode("utf-8"), corta).encode("utf-8")
            info = zipfile.ZipInfo(f"{skill.name}/{f.relative_to(skill).as_posix()}", FECHA_FIJA)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o755 if f.suffix == ".py" else 0o644) << 16
            z.writestr(info, datos)
    return zip_path


def main(argv: list[str]) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    args = argv[1:]
    claude_ai = "--claude-ai" in args
    pedidas = [a for a in args if a != "--claude-ai"]
    todas = {s.name: s for s in skills()}
    pedidas = pedidas or list(todas)
    desconocidas = [p for p in pedidas if p not in todas]
    if desconocidas:
        print(f"Skills desconocidas: {', '.join(desconocidas)}. Disponibles: {', '.join(todas)}", file=sys.stderr)
        return 1
    destino = DIST / "claude-ai" if claude_ai else DIST
    for nombre in pedidas:
        try:
            zip_path = empaquetar(todas[nombre], destino, claude_ai)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        with zipfile.ZipFile(zip_path) as z:
            n = len(z.namelist())
        print(f"{zip_path.relative_to(RAIZ).as_posix()}: {n} archivos, {zip_path.stat().st_size / 1024:.0f} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
