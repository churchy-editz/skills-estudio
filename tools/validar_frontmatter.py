#!/usr/bin/env python3
"""Valida el frontmatter de cada SKILL.md contra la especificación Agent Skills.

Uso:
    python tools/validar_frontmatter.py [raíz-del-repo]

Según https://agentskills.io/specification:
- Campos permitidos: name, description (obligatorios), license, compatibility,
  metadata, allowed-tools. Cualquier otro es un error.
- name: 1-64 caracteres, solo a-z, 0-9 y guiones, sin guion al principio ni al
  final, sin "--", e igual al nombre de la carpeta.
- description: 1-1024 caracteres.
- compatibility: máx. 500 caracteres.

Código 1 si hay errores. Solo librería estándar (lee el YAML sencillo que usan
las skills: claves de primer nivel, bloques plegados >- y un mapa en metadata).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

PERMITIDOS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
OBLIGATORIOS = ("name", "description")


def leer(texto: str) -> dict[str, object] | None:
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", texto, re.S)
    if not m:
        return None
    campos: dict[str, object] = {}
    clave = None
    for linea in m.group(1).splitlines():
        if not linea.strip() or linea.lstrip().startswith("#"):
            continue
        cab = re.match(r"^([A-Za-z][\w-]*):\s*(.*)$", linea)
        if cab:
            clave, valor = cab.group(1), cab.group(2).strip()
            if valor in (">-", ">", "|", "|-", ">+", "|+"):
                campos[clave] = ""
            elif valor == "":
                campos[clave] = {}
            else:
                campos[clave] = valor.strip("\"'")
            continue
        sub = re.match(r"^\s+([\w-]+):\s*(.*)$", linea)
        if clave and isinstance(campos.get(clave), dict) and sub:
            campos[clave][sub.group(1)] = sub.group(2).strip().strip("\"'")
        elif clave and linea.startswith((" ", "\t")) and isinstance(campos.get(clave), str):
            campos[clave] = (campos[clave] + " " + linea.strip()).strip()
    return campos


def validar(skill: Path) -> list[str]:
    texto = (skill / "SKILL.md").read_text(encoding="utf-8")
    campos = leer(texto)
    if campos is None:
        return ["SKILL.md no empieza con un frontmatter entre líneas ---"]
    errores = []
    for campo in sorted(set(campos) - PERMITIDOS):
        errores.append(f"campo no estándar «{campo}» (permitidos: {', '.join(sorted(PERMITIDOS))})")
    for campo in OBLIGATORIOS:
        if not campos.get(campo):
            errores.append(f"falta el campo obligatorio «{campo}»")
    nombre = campos.get("name")
    if isinstance(nombre, str) and nombre:
        if len(nombre) > 64:
            errores.append(f"name tiene {len(nombre)} caracteres (máx. 64)")
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", nombre):
            errores.append(f"name «{nombre}»: solo a-z, 0-9 y guiones simples, sin guion al principio ni al final")
        if nombre != skill.name:
            errores.append(f"name «{nombre}» no coincide con la carpeta «{skill.name}»")
    desc = campos.get("description")
    if isinstance(desc, str) and len(desc) > 1024:
        errores.append(f"description tiene {len(desc)} caracteres (máx. 1024)")
    comp = campos.get("compatibility")
    if isinstance(comp, str) and len(comp) > 500:
        errores.append(f"compatibility tiene {len(comp)} caracteres (máx. 500)")
    if "metadata" in campos and not isinstance(campos["metadata"], dict):
        errores.append("metadata tiene que ser un mapa clave: valor")
    return errores


def main(argv: list[str]) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    raiz = Path(argv[1]) if len(argv) > 1 else Path(__file__).resolve().parents[1]
    carpeta = raiz / "skills"
    skills = sorted(d for d in carpeta.iterdir() if d.is_dir() and (d / "SKILL.md").is_file()) if carpeta.is_dir() else []
    total = 0
    for skill in skills:
        errores = validar(skill)
        total += len(errores)
        estado = "OK" if not errores else f"{len(errores)} error(es)"
        print(f"{skill.name}: {estado}")
        for e in errores:
            print(f"  - {e}")
    if not skills:
        print("No hay ninguna carpeta con SKILL.md en skills/.")
        return 1
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
