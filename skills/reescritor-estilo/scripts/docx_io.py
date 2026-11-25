#!/usr/bin/env python3
"""Pasa un DOCX a texto editable y vuelve a escribirlo conservando los estilos.

Uso:
    python docx_io.py extraer entrada.docx texto.md
    python docx_io.py escribir original.docx reescrito.md salida.docx

Formato del texto (Markdown mínimo, un bloque por párrafo, separados por una línea en blanco):
    # Texto        → estilo Title
    ## Texto       → Heading 1   (### → Heading 2, y así hasta Heading 5)
    - Texto        → List Bullet
    1. Texto       → List Number
    Texto          → el estilo de cuerpo más usado en el original

Al escribir se parte del documento original: se conservan sus definiciones de
estilo, márgenes, cabeceras y pies, y se sustituye el cuerpo. Las tablas e
imágenes del cuerpo no se reescriben; si el original las tiene, se avisa.
Necesita python-docx.
"""
from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

try:
    from docx import Document
    from docx.oxml.ns import qn
except ImportError:
    print(
        "Falta la librería python-docx. Instálala con:\n"
        f'    "{sys.executable}" -m pip install python-docx',
        file=sys.stderr,
    )
    sys.exit(1)

MAX_NIVEL = 5


def nivel_titulo(estilo: str) -> int | None:
    """0 = Title, n = Heading n. None si no es un título."""
    nombre = estilo.lower()
    if nombre in {"title", "título", "titulo"}:
        return 0
    m = re.match(r"(?:heading|título|titulo)\s*(\d)", nombre)
    return min(int(m.group(1)), MAX_NIVEL) if m else None


def tipo_lista(estilo: str) -> str | None:
    nombre = estilo.lower()
    if "list bullet" in nombre or "viñeta" in nombre:
        return "-"
    if "list number" in nombre or "número" in nombre or "numero" in nombre:
        return "1."
    return None


def extraer(ruta: str | Path) -> str:
    doc = Document(str(ruta))
    bloques = []
    for p in doc.paragraphs:
        texto = p.text.strip()
        if not texto:
            continue
        estilo = p.style.name if p.style is not None else ""
        nivel = nivel_titulo(estilo)
        lista = tipo_lista(estilo)
        if nivel is not None:
            bloques.append("#" * (nivel + 1) + " " + texto)
        elif lista:
            bloques.append(f"{lista} {texto}")
        else:
            bloques.append(texto)
    return "\n\n".join(bloques) + "\n"


def leer_bloques(texto: str) -> list[tuple[str, str]]:
    """[(clase, texto)] con clase 'h0'..'h5', 'bullet', 'number' o 'body'."""
    bloques = []
    for crudo in re.split(r"\n\s*\n", texto.strip()):
        for linea in crudo.splitlines() if re.match(r"^\s*(?:[-*]|\d+\.)\s", crudo) else [crudo]:
            linea = linea.strip()
            if not linea:
                continue
            m = re.match(r"^(#{1,6})\s+(.*)$", linea, re.S)
            if m:
                bloques.append((f"h{min(len(m.group(1)) - 1, MAX_NIVEL)}", m.group(2).strip()))
            elif re.match(r"^[-*]\s+", linea):
                bloques.append(("bullet", re.sub(r"^[-*]\s+", "", linea)))
            elif re.match(r"^\d+\.\s+", linea):
                bloques.append(("number", re.sub(r"^\d+\.\s+", "", linea)))
            else:
                bloques.append(("body", " ".join(l.strip() for l in linea.splitlines())))
    return bloques


def estilos_del_original(doc) -> dict[str, str]:
    """Qué estilo usaba el original para cada clase de bloque."""
    usados: dict[str, Counter] = {}
    for p in doc.paragraphs:
        if not p.text.strip() or p.style is None:
            continue
        nombre = p.style.name
        nivel = nivel_titulo(nombre)
        lista = tipo_lista(nombre)
        clase = (f"h{nivel}" if nivel is not None else
                 "bullet" if lista == "-" else "number" if lista == "1." else "body")
        usados.setdefault(clase, Counter())[nombre] += 1
    return {clase: c.most_common(1)[0][0] for clase, c in usados.items()}


def estilo_para(doc, clase: str, usados: dict[str, str]) -> str | None:
    candidatos = [usados.get(clase)]
    if clase.startswith("h"):
        n = int(clase[1:])
        candidatos.append("Title" if n == 0 else f"Heading {n}")
    elif clase == "bullet":
        candidatos.append("List Bullet")
    elif clase == "number":
        candidatos.append("List Number")
    candidatos += [usados.get("body"), "Normal"]
    nombres = {s.name for s in doc.styles}
    return next((c for c in candidatos if c and c in nombres), None)


def escribir(original: str | Path, texto: str, salida: str | Path) -> list[str]:
    doc = Document(str(original))
    usados = estilos_del_original(doc)
    avisos = []
    cuerpo = doc.element.body
    if cuerpo.findall(qn("w:tbl")) or cuerpo.findall(".//" + qn("w:drawing")):
        avisos.append("El original tiene tablas o imágenes en el cuerpo: no se han copiado.")
    for hijo in list(cuerpo):
        if hijo.tag != qn("w:sectPr"):
            cuerpo.remove(hijo)
    for clase, contenido in leer_bloques(texto):
        estilo = estilo_para(doc, clase, usados)
        p = doc.add_paragraph(contenido, style=estilo)
        if estilo is None or (clase.startswith("h") and nivel_titulo(estilo) is None):
            for run in p.runs:
                run.bold = True
    doc.save(str(salida))
    return avisos


def main(argv: list[str]) -> int:
    for flujo in (sys.stdout, sys.stderr):
        try:
            flujo.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    if len(argv) == 4 and argv[1] == "extraer":
        Path(argv[3]).write_text(extraer(argv[2]), encoding="utf-8")
        print(f"Texto extraído: {argv[3]}")
        return 0
    if len(argv) == 5 and argv[1] == "escribir":
        texto = Path(argv[3]).read_text(encoding="utf-8")
        for aviso in escribir(argv[2], texto, argv[4]):
            print(f"Aviso: {aviso}")
        print(f"DOCX generado: {argv[4]}")
        return 0
    print(__doc__, file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
