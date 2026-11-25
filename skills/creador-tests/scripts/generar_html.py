#!/usr/bin/env python3
"""Genera el test interactivo (HTML autocontenido) a partir del JSON.

Uso:
    python generar_html.py test-<tema>.json test-<tema>.html [--paleta ciencias]

Solo librería estándar. Inyecta el JSON en assets/plantilla-test.html y copia
los valores de la paleta elegida (tabla PALETAS, más abajo; son los mismos
colores que usa creador-apuntes). Antes comprueba el esquema con validar.py: si hay errores, no
genera nada. Los avisos de patrón no bloquean aquí; se corrigen con validar.py.
"""
from __future__ import annotations

import argparse
import html
import importlib.util
import json
import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
PLANTILLA = RAIZ / "assets" / "plantilla-test.html"

SANS = 'system-ui, "Segoe UI", Roboto, Arial, sans-serif'
SERIF = 'Georgia, Cambria, "Times New Roman", serif'
# fondo, texto, def, ejemplo, ojo, clave, fuente  (contraste WCAG AA verificado)
PALETAS = {
    "neutra":      ("#ffffff", "#1f1f1f", "#1f5f8b", "#2e6b30", "#a3261b", "#7a4b00", SANS),
    "ciencias":    ("#fbfdfb", "#18261f", "#0b6e69", "#3d6b1f", "#b02a1f", "#6b3fa0", SANS),
    "matematicas": ("#fdfdfd", "#1a1c24", "#1d4e89", "#2f6b4f", "#b3261e", "#8a4b00", SANS),
    "historia":    ("#fcf9f2", "#2b2118", "#7a3e12", "#4f6228", "#9e1c1c", "#23527c", SERIF),
    "lengua":      ("#fffdf9", "#241b26", "#6a2c70", "#1f6f6b", "#a8321e", "#8a5a00", SERIF),
    "idiomas":     ("#fafcff", "#1a2230", "#1560a0", "#1b7340", "#b4261a", "#7b3f98", SANS),
    "derecho":     ("#ffffff", "#1b1b1b", "#1c3d6e", "#3f5f3a", "#8f1d1d", "#6b4e16", SERIF),
    "economia":    ("#fbfcfd", "#1c2329", "#0f5c6e", "#2f6b2f", "#b03a12", "#5b3d99", SANS),
    "arte":        ("#fdfbf8", "#2a2226", "#8a2f4c", "#2d6a5e", "#a32d1a", "#5a4a8a", SERIF),
}
ALIAS = {
    "biologia": "ciencias", "quimica": "ciencias", "fisica": "ciencias",
    "estadistica": "matematicas", "geografia": "historia", "literatura": "lengua",
    "oposiciones": "derecho", "empresa": "economia", "humanidades": "arte",
    "filosofia": "arte", "musica": "arte",
}


def _clave(nombre: str) -> str:
    nombre = unicodedata.normalize("NFD", nombre.strip().lower())
    return "".join(c for c in nombre if unicodedata.category(c) != "Mn")


def paleta_css(nombre: str) -> str:
    clave = _clave(nombre)
    clave = ALIAS.get(clave, clave)
    if clave not in PALETAS:
        raise KeyError(nombre)
    fondo, texto, d, ej, ojo, clave_c, fuente = PALETAS[clave]
    return (
        f"  --fondo: {fondo};\n  --texto: {texto};\n  --def: {d};\n  --ejemplo: {ej};\n"
        f"  --ojo: {ojo};\n  --clave: {clave_c};\n  --fuente: {fuente};"
    )


def _validar():
    spec = importlib.util.spec_from_file_location("validar", Path(__file__).with_name("validar.py"))
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def generar(entrada: Path, salida: Path, paleta: str = "neutra") -> Path:
    datos = json.loads(Path(entrada).read_text(encoding="utf-8"))
    errores = _validar().errores_esquema(datos)
    if errores:
        raise ValueError("El JSON tiene errores; corrígelos con validar.py:\n  - " + "\n  - ".join(errores))
    plantilla = PLANTILLA.read_text(encoding="utf-8")
    # "<" se escapa para que ningún texto pueda cerrar la etiqueta <script>.
    bloque = json.dumps(datos, ensure_ascii=False, indent=1).replace("<", "\\u003c")
    resultado = (
        plantilla.replace("/*PALETA*/", paleta_css(paleta))
        .replace("<!--TITULO-->", html.escape(datos["meta"]["titulo"]))
        .replace("/*DATOS*/", bloque)
    )
    salida = Path(salida)
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(resultado, encoding="utf-8")
    return salida


def main(argv: list[str] | None = None) -> int:
    for flujo in (sys.stdout, sys.stderr):
        try:
            flujo.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description="Genera el test interactivo en HTML.")
    ap.add_argument("entrada", type=Path)
    ap.add_argument("salida", type=Path)
    ap.add_argument("--paleta", default="neutra",
                    help="neutra, ciencias, matematicas, historia, lengua, idiomas, derecho, economia, arte "
                         "(también vale el nombre de la asignatura: biologia, filosofia…)")
    args = ap.parse_args(argv)
    if not args.entrada.is_file():
        print(f"No existe el archivo de entrada: {args.entrada}", file=sys.stderr)
        return 2
    try:
        salida = generar(args.entrada, args.salida, args.paleta)
    except KeyError:
        print(f"Paleta desconocida: {args.paleta}. Opciones: {', '.join(PALETAS)}", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 1
    print(f"HTML generado: {salida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
