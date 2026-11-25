#!/usr/bin/env python3
"""Comprueba que cada skill del repo funciona sola.

Uso:
    python tools/comprobar_independencia.py [raíz-del-repo]

Una skill es una carpeta de skills/ con SKILL.md. Falla (código 1) si el
SKILL.md, los scripts, las referencias o los assets de una skill nombran la
CARPETA de otra: "otra-skill/…", "../otra-skill", "otra-skill\\…". Nombrar otra
skill sin ruta ("acepta los apuntes de creador-apuntes") está permitido, porque
no hace falta que esté instalada.

Los examples/ y tests/ no se revisan: no se cargan al usar la skill.
Solo librería estándar.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REVISAR = ("SKILL.md", "scripts", "references", "assets")
EXTENSIONES = {".md", ".py", ".html", ".css", ".js", ".json", ".txt", ".sh", ".ps1"}


def skills(raiz: Path) -> list[Path]:
    carpeta = raiz / "skills"
    if not carpeta.is_dir():
        return []
    return sorted(d for d in carpeta.iterdir() if d.is_dir() and (d / "SKILL.md").is_file())


def archivos(skill: Path):
    for nombre in REVISAR:
        ruta = skill / nombre
        if ruta.is_file():
            yield ruta
        elif ruta.is_dir():
            for f in sorted(ruta.rglob("*")):
                if f.is_file() and f.suffix.lower() in EXTENSIONES and "__pycache__" not in f.parts:
                    yield f


def comprobar(raiz: Path) -> list[str]:
    raiz = Path(raiz).resolve()
    todas = skills(raiz)
    problemas = []
    for skill in todas:
        otras = [s.name for s in todas if s != skill]
        if not otras:
            continue
        patron = re.compile(r"(?<![\w-])(?:\.\.[/\\])?(" + "|".join(map(re.escape, otras)) + r")[/\\]")
        for f in archivos(skill):
            texto = f.read_text(encoding="utf-8", errors="replace")
            for n, linea in enumerate(texto.splitlines(), 1):
                for m in patron.finditer(linea):
                    problemas.append(
                        f"{f.relative_to(raiz).as_posix()}:{n}: referencia a la carpeta de "
                        f"{m.group(1)} (\"{m.group(0)}\")"
                    )
    return problemas


def main(argv: list[str]) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    raiz = Path(argv[1]) if len(argv) > 1 else Path(__file__).resolve().parents[1]
    encontradas = skills(raiz)
    problemas = comprobar(raiz)
    if problemas:
        print(f"Dependencias entre skills ({len(problemas)}):")
        for p in problemas:
            print(f"  - {p}")
        print("Cada skill tiene que funcionar sola: copia lo necesario dentro de su carpeta.")
        return 1
    print(f"Independencia OK: {len(encontradas)} skills ({', '.join(s.name for s in encontradas)}), "
          "ninguna referencia a la carpeta de otra.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
