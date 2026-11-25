#!/usr/bin/env python3
"""Compara una versión nueva del trabajo con la corrección anterior.

Uso:
    python comparar_versiones.py correccion-anterior.json trabajo-v2.(docx|pdf|md|tex|txt) [--json salida.json]

Para cada comentario anterior busca su cita en la versión nueva:
- «sigue»: el fragmento está igual, así que el problema sigue ahí;
- «cambiado»: el fragmento ya no aparece literal. Puede estar arreglado o
  reescrito con el mismo fallo: el asistente lo comprueba leyendo la versión
  nueva antes de darlo por arreglado.

La salida JSON (con --json) sirve de base para el campo «version_anterior» de la
corrección nueva, que añade «nuevos» con los comentarios que no estaban antes.
Solo librería estándar (python-docx para leer DOCX).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from extraer import cargar, normalizar  # noqa: E402


def comparar(anterior: dict, ruta_nueva: str | Path) -> dict:
    doc = cargar(ruta_nueva)
    texto = normalizar(re.sub(r"\^\{([^}]*)\}", r"\1", doc.texto()).replace("\t", " "))
    siguen, cambiados = [], []
    for c in anterior.get("comentarios", []):
        cita = normalizar(re.sub(r"\^\{([^}]*)\}", r"\1", c.get("cita", "")))
        item = {"id": c.get("id"), "gravedad": c.get("gravedad"), "cita": c.get("cita"),
                "texto": f"{c.get('id')}: {c.get('que_falla', '')}"}
        (siguen if cita and cita in texto else cambiados).append(item)
    return {"siguen": siguen, "cambiados": cambiados,
            "nota": "«cambiados» no es lo mismo que «arreglados»: hay que leer cada uno en la versión nueva."}


def main(argv: list[str]) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    p = argparse.ArgumentParser(description="Compara una versión nueva con la corrección anterior.")
    p.add_argument("anterior")
    p.add_argument("nueva")
    p.add_argument("--json", dest="salida_json")
    a = p.parse_args(argv[1:])
    anterior = json.loads(Path(a.anterior).read_text(encoding="utf-8"))
    r = comparar(anterior, a.nueva)
    print(f"Siguen igual ({len(r['siguen'])}): {', '.join(x['id'] for x in r['siguen']) or '—'}")
    print(f"Cambiados, a revisar ({len(r['cambiados'])}): {', '.join(x['id'] for x in r['cambiados']) or '—'}")
    print(r["nota"])
    if a.salida_json:
        Path(a.salida_json).write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
