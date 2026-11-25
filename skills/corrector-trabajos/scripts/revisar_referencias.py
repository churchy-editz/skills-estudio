#!/usr/bin/env python3
"""Contrasta las citas del texto con la bibliografía.

Uso:
    python revisar_referencias.py trabajo.(docx|pdf|md|tex|txt) [--json salida.json]

Reconoce:
- autor-año: (García, 2019), (García y López, 2018; Smith et al., 2020a),
  García (2019), Smith et al. (2020);
- numéricas: [1], [2, 5], [3-6], superíndices ^{1,2} y, si la bibliografía está
  numerada y no hay corchetes, (1) o (1, 3) al estilo Vancouver;
- LaTeX: \\cite{clave} contra \\bibitem o el .bib.

Detecta citas sin entrada en la bibliografía, entradas que nadie cita, años
que no coinciden, mezcla de sistemas de cita en el texto y mezcla de formatos
(APA, Vancouver, IEEE) en la bibliografía.

Código de salida: 0 si no hay avisos, 2 si los hay. Solo librería estándar.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from extraer import Bloque, Documento, cargar, normalizar, sin_tildes  # noqa: E402
from revisar_estructura import canonica  # noqa: E402

ANIO = r"(?:1[6-9]\d{2}|20\d{2})[a-z]?|s\.\s?f\.|n\.d\.|en prensa|in press"
APELLIDO = r"[A-ZÁÉÍÓÚÑÜ][\wáéíóúñüàèç'’\-]+"
PARTICULAS = {"de", "del", "la", "las", "los", "van", "der", "von", "di", "da", "le", "y", "and", "et", "al", "e"}
NO_AUTORES = {"figura", "fig", "tabla", "table", "cuadro", "ecuacion", "anexo", "seccion", "apartado", "capitulo",
              "pagina", "real", "decreto", "ley", "orden", "norma", "iso", "une", "en", "enero", "febrero", "marzo",
              "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"}


def clave_autor(texto: str) -> str:
    """Apellido principal normalizado: «de la Fuente» → «fuente», «García-López» → «garcia-lopez»."""
    palabras = [p for p in re.findall(r"[\w'’\-]+", sin_tildes(texto.lower())) if p not in PARTICULAS]
    return palabras[0] if palabras else ""


def _anio(t: str) -> str:
    t = t.strip().lower()
    return "sf" if re.match(r"s\.\s?f\.|n\.d\.", t) else t


# --- Bibliografía --------------------------------------------------------------

def entradas_bibliografia(doc: Documento) -> tuple[list[dict], int | None]:
    """Entradas de la (última) sección de bibliografía y el índice del bloque donde empieza."""
    inicio, nivel = None, None
    for i, b in enumerate(doc.bloques):
        if b.tipo == "titulo" and canonica(b.texto) == "bibliografia":
            inicio, nivel = i, b.nivel
    if inicio is None:
        return [], None
    entradas = []
    for b in doc.bloques[inicio + 1:]:
        if b.tipo == "titulo" and b.nivel <= nivel:
            break
        if b.tipo not in ("parrafo", "lista") or len(b.texto) < 15:
            continue
        entradas.append(analizar_entrada(b, len(entradas) + 1))
    return entradas, inicio


def analizar_entrada(b: Bloque, posicion: int) -> dict:
    t = b.texto.strip()
    e = {"texto": t, "numero": None, "autor": "", "anio": "", "estilo": "otro", "clave": b.clave}
    m = re.match(r"^\[(\d+)\]\s*", t) or re.match(r"^(\d+)[.)]\s+", t)
    if m:
        e["numero"] = int(m.group(1))
        t = t[m.end():]
    elif b.tipo == "lista" and not b.clave:
        e["posicion"] = posicion
    anios = re.findall(rf"\b({ANIO})", t)
    e["anio"] = _anio(anios[0]) if anios else ""
    # Estilo
    if re.match(rf"^{APELLIDO}(?:\s+{APELLIDO})*,\s*(?:[A-ZÁÉÍÓÚ]\.\s*-?\s*)+.*?\(\s*({ANIO})\s*\)", t):
        e["estilo"] = "APA"
        e["anio"] = _anio(re.search(rf"\(\s*({ANIO})\s*\)", t).group(1))
    elif re.match(rf"^[^()]{{3,150}}?\.\s*\(\s*({ANIO})\s*\)\.", t):
        e["estilo"] = "APA"  # autor institucional: «Departamento de… (2025).»
        e["anio"] = _anio(re.search(rf"\(\s*({ANIO})\s*\)", t).group(1))
    elif (re.match(r"^(?:[A-Z]\.\s*)+(?:-[A-Z]\.\s*)?" + APELLIDO, t) or re.match(r"^\[\d+\]", b.texto.strip())) \
            and re.search(r"[“\"].+?,?[”\"]", t):
        e["estilo"] = "IEEE"
    elif re.match(rf"^{APELLIDO}(?:\s+{APELLIDO})*\s+[A-Z]{{1,3}}[,.]", t) and re.search(r"\b(?:19|20)\d{2}\s*[;:.]", t):
        e["estilo"] = "Vancouver"
    elif re.match(rf"^{APELLIDO}.*\b({ANIO})\b", t):
        e["estilo"] = "autor-año (sin formato reconocible)"
    # Primer autor
    if e["estilo"] == "IEEE":
        m = re.match(r"^(?:[A-Z]\.\s*)+(?:-[A-Z]\.\s*)?(" + APELLIDO + r"(?:\s+" + APELLIDO + r")?)", t)
        e["autor"] = clave_autor(m.group(1)) if m else ""
    else:
        e["autor"] = clave_autor(re.split(r"[,(]|\s[A-Z]{1,3}[,.\s]", t, maxsplit=1)[0])
    return e


# --- Citas en el texto ----------------------------------------------------------

RE_PAREN = re.compile(r"\(([^()]{2,250}?)\)")
RE_PARTE_AY = re.compile(rf"^(?:(?:v[ée]ase|cf\.|see|e\.g\.,?|p\. ej\.,?)\s+)?(?P<autores>{APELLIDO}.*?),?\s+(?P<anio>{ANIO})"
                         rf"(?:\s*,\s*(?:{ANIO}))*(?:\s*,\s*(?:p|pp|pág|págs)\.\s*[\d–-]+)?$")
RE_NARRATIVA = re.compile(rf"\b(?P<autores>{APELLIDO}(?:\s+(?:et\s+al\.|y|e|and|&|eta)\s*(?:{APELLIDO})?)?)\s*\((?P<anio>{ANIO})"
                          rf"(?:,\s*(?:p|pp)\.\s*[\d–-]+)?\)")
RE_CORCHETE = re.compile(r"\[(\d+(?:\s*[-–,]\s*\d+)*)\]")
RE_SUPER = re.compile(r"\^\{([\d,\s–-]+)\}")
RE_PAREN_NUM = re.compile(r"\((\d{1,3}(?:\s*[-–,]\s*\d{1,3})*)\)")
RE_CITE = re.compile(r"\\cite\{([^}]*)\}")


def _expandir(lista: str) -> list[int]:
    salida = []
    for trozo in re.split(r",", lista):
        a = re.split(r"[-–]", trozo.strip())
        if len(a) == 2 and a[0].strip().isdigit() and a[1].strip().isdigit() and int(a[1]) - int(a[0]) < 50:
            salida += list(range(int(a[0]), int(a[1]) + 1))
        elif a[0].strip().isdigit():
            salida.append(int(a[0]))
    return salida


def citas_texto(doc: Documento, fin: int | None, numerada: bool) -> dict:
    autor_anio, numericas, claves = [], [], []
    bloques = doc.bloques[:fin] if fin is not None else doc.bloques
    hay_corchetes = any(RE_CORCHETE.search(b.texto) for b in bloques if b.tipo not in ("tabla", "codigo"))
    for b in bloques:
        if b.tipo in ("titulo", "tabla", "codigo", "imagen"):
            continue
        t = b.texto
        for m in RE_PAREN.finditer(t):
            for parte in m.group(1).split(";"):
                pm = RE_PARTE_AY.match(parte.strip())
                if pm and clave_autor(pm.group("autores")) not in NO_AUTORES:
                    for anio in re.findall(rf"\b({ANIO})", parte):
                        autor_anio.append({"cita": f"({m.group(1).strip()})", "autor": clave_autor(pm.group("autores")),
                                           "anio": _anio(anio), "seccion": b.seccion,
                                           "autores": pm.group("autores").strip()})
        for m in RE_NARRATIVA.finditer(t):
            if clave_autor(m.group("autores")) in NO_AUTORES:
                continue
            autor_anio.append({"cita": m.group(0), "autor": clave_autor(m.group("autores")), "anio": _anio(m.group("anio")),
                               "seccion": b.seccion, "autores": m.group("autores")})
        for patron in (RE_CORCHETE, RE_SUPER) + ((RE_PAREN_NUM,) if numerada and not hay_corchetes else ()):
            for m in patron.finditer(t):
                for n in _expandir(m.group(1)):
                    numericas.append({"cita": m.group(0), "numero": n, "seccion": b.seccion})
        for m in RE_CITE.finditer(t):
            for k in m.group(1).split(","):
                claves.append({"cita": m.group(0), "clave": k.strip(), "seccion": b.seccion})
    return {"autor_anio": autor_anio, "numericas": numericas, "claves": claves}


def revisar(ruta: str | Path) -> dict:
    doc = cargar(ruta)
    entradas, inicio = entradas_bibliografia(doc)
    numerada = sum(1 for e in entradas if e["numero"] or e.get("posicion")) > len(entradas) / 2 if entradas else False
    numeradas_explicitas = any(e["numero"] for e in entradas)
    citas = citas_texto(doc, inicio, numerada)
    avisos = []
    if inicio is None:
        if citas["autor_anio"] or citas["numericas"] or citas["claves"]:
            avisos.append({"tipo": "sin_bibliografia", "gravedad": "critico",
                           "detalle": "el texto tiene citas, pero no hay sección de bibliografía"})
    sistemas = [s for s, lista in (("autor-año", citas["autor_anio"]), ("numérico", citas["numericas"]))
                if lista]
    if len(sistemas) > 1:
        avisos.append({"tipo": "mezcla_sistemas", "gravedad": "importante",
                       "detalle": f"el texto mezcla citas autor-año ({len(citas['autor_anio'])}) y numéricas "
                                  f"({len(citas['numericas'])}); hay que elegir un sistema",
                       "ejemplos": [citas["autor_anio"][0]["cita"], citas["numericas"][0]["cita"]]})
    usadas = set()
    # Autor-año
    for c in citas["autor_anio"]:
        candidatas = [i for i, e in enumerate(entradas) if e["autor"] and
                      (e["autor"] == c["autor"] or e["autor"].endswith(c["autor"]) or c["autor"].endswith(e["autor"]))]
        exactas = [i for i in candidatas if entradas[i]["anio"] == c["anio"]]
        if exactas:
            usadas.update(exactas)
        elif candidatas:
            usadas.update(candidatas)
            anios = sorted({entradas[i]["anio"] for i in candidatas})
            avisos.append({"tipo": "anio_distinto", "gravedad": "importante", "seccion": c["seccion"], "cita": c["cita"],
                           "detalle": f"{c['cita']}: en la bibliografía, {c['autores'].split(' ')[0]} aparece con "
                                      f"año {', '.join(anios)}"})
        elif inicio is not None:
            avisos.append({"tipo": "cita_sin_entrada", "gravedad": "critico", "seccion": c["seccion"], "cita": c["cita"],
                           "detalle": f"{c['cita']} no está en la bibliografía"})
    # Numéricas
    total = len(entradas)
    for c in citas["numericas"]:
        i = next((i for i, e in enumerate(entradas) if (e["numero"] or e.get("posicion")) == c["numero"]), None)
        if i is None and not numeradas_explicitas and 1 <= c["numero"] <= total:
            i = c["numero"] - 1
        if i is None:
            if inicio is not None:
                avisos.append({"tipo": "cita_sin_entrada", "gravedad": "critico", "seccion": c["seccion"],
                               "cita": c["cita"], "detalle": f"la cita {c['cita']} remite a la referencia {c['numero']}, "
                                                             f"que no existe (la bibliografía tiene {total})"})
        else:
            usadas.add(i)
    vistos: list[int] = []
    for c in citas["numericas"]:
        if c["numero"] not in vistos:
            vistos.append(c["numero"])
    if vistos and vistos != sorted(vistos) and numerada:
        avisos.append({"tipo": "orden_numerico", "gravedad": "menor",
                       "detalle": "en Vancouver e IEEE se numeran las referencias por orden de primera aparición; "
                                  f"aquí aparecen en el orden {', '.join(map(str, vistos[:8]))}"})
    # LaTeX
    for c in citas["claves"]:
        i = next((i for i, e in enumerate(entradas) if e["clave"] == c["clave"]), None)
        if i is None:
            avisos.append({"tipo": "cita_sin_entrada", "gravedad": "critico", "seccion": c["seccion"], "cita": c["cita"],
                           "detalle": f"\\cite{{{c['clave']}}} no tiene entrada en la bibliografía"})
        else:
            usadas.add(i)
    hay_citas = citas["autor_anio"] or citas["numericas"] or citas["claves"]
    for i, e in enumerate(entradas):
        if i not in usadas and hay_citas:
            avisos.append({"tipo": "entrada_sin_citar", "gravedad": "importante", "entrada": e["texto"],
                           "detalle": f"la entrada «{e['texto'][:90]}{'…' if len(e['texto']) > 90 else ''}» "
                                      "no se cita en el texto"})
    estilos: dict[str, int] = {}
    for e in entradas:
        estilos[e["estilo"]] = estilos.get(e["estilo"], 0) + 1
    reconocidos = {k: v for k, v in estilos.items() if k in ("APA", "Vancouver", "IEEE")}
    if len(reconocidos) > 1 or (reconocidos and len(estilos) > 1 and estilos.get("otro", 0) + estilos.get(
            "autor-año (sin formato reconocible)", 0) >= 1 and len(entradas) >= 3):
        avisos.append({"tipo": "mezcla_formatos", "gravedad": "menor",
                       "detalle": "la bibliografía mezcla formatos: " + ", ".join(f"{k} {v}" for k, v in estilos.items())})
    principal = max(reconocidos, key=reconocidos.get) if reconocidos else (
        "autor-año" if citas["autor_anio"] else "numérico" if citas["numericas"] else "—")
    return {"archivo": str(ruta), "estilo": principal, "entradas": len(entradas), "estilos_bibliografia": estilos,
            "citas": {"autor_anio": len(citas["autor_anio"]), "numericas": len(citas["numericas"]),
                      "latex": len(citas["claves"])},
            "avisos": avisos}


def informe(r: dict) -> str:
    c = r["citas"]
    lineas = [f"Referencias: {Path(r['archivo']).name}",
              f"Estilo principal: {r['estilo']}. Bibliografía: {r['entradas']} entradas "
              f"({', '.join(f'{k} {v}' for k, v in r['estilos_bibliografia'].items()) or '—'}). "
              f"Citas en el texto: {c['autor_anio']} autor-año, {c['numericas']} numéricas, {c['latex']} \\cite."]
    if r["avisos"]:
        lineas.append(f"AVISOS ({len(r['avisos'])}):")
        for a in r["avisos"]:
            donde = f" [{a['seccion']}]" if a.get("seccion") else ""
            lineas.append(f"  - ({a['gravedad']}) {a['detalle']}{donde}")
    else:
        lineas.append("AVISOS: ninguno")
    return "\n".join(lineas)


def main(argv: list[str]) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    p = argparse.ArgumentParser(description="Contrasta las citas del texto con la bibliografía.")
    p.add_argument("trabajo")
    p.add_argument("--json", dest="salida_json")
    a = p.parse_args(argv[1:])
    r = revisar(a.trabajo)
    print(informe(r))
    if a.salida_json:
        Path(a.salida_json).write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    return 2 if r["avisos"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
