#!/usr/bin/env python3
"""Revisa cifras y unidades: coherencia entre tablas y texto, unidades y decimales.

Uso:
    python revisar_numeros.py trabajo.(docx|pdf|md|tex|txt) [--json salida.json]

Detecta:
- la misma magnitud única (R², pendiente, ordenada, pKa, Km, Vmax…) con valores
  distintos en distintos sitios del trabajo;
- cifras del texto que no coinciden con la fila de la tabla de la que hablan;
- cifras del texto que se parecen a una de la tabla salvo un dígito cambiado,
  traspuesto, de más o de menos (posible error al copiar);
- unidades mal escritas (ºC, mins, grs, Kg, ul, cc…), sin espacio entre cifra y
  unidad (595nm), variantes mezcladas (ml y mL) y unidades fuera del SI (rpm);
- cabeceras de tabla con magnitudes sin unidades;
- separador decimal mezclado (0,5 y 0.5) y número de decimales irregular dentro
  de una misma columna o magnitud.

Código de salida: 0 si no hay avisos, 2 si los hay. Solo librería estándar.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from extraer import Bloque, Documento, cargar, normalizar  # noqa: E402

# --- Números -----------------------------------------------------------------------

RE_NUM = re.compile(r"(?<![\w.,/^{])(?P<num>[-−]?\d+(?:[.,]\d+)*)(?P<esp>[   ]?)"
                    r"(?P<uni>[a-zA-ZµμΩ°º%][\w°º/·µμ²³⁻¹\-]*)?")


def valor(texto: str, decimal: str | None = None) -> tuple[float, int, str] | None:
    """(valor, decimales, separador decimal) de un número escrito; None si es ambiguo o no es un número."""
    t = texto.replace("−", "-")
    if t.count(".") + t.count(",") > 1:
        partes = re.split(r"[.,]", t)
        if len(set(re.findall(r"[.,]", t))) == 1 and all(len(p) == 3 for p in partes[1:]):
            return float("".join(partes)), 0, ""  # 1.000.000
        if re.fullmatch(r"-?\d{1,3}(?:\.\d{3})+,\d+", t):
            return float(t.replace(".", "").replace(",", ".")), len(t.split(",")[1]), ","
        if re.fullmatch(r"-?\d{1,3}(?:,\d{3})+\.\d+", t):
            return float(t.replace(",", "")), len(t.split(".")[1]), "."
        return None
    m = re.fullmatch(r"(-?\d+)(?:([.,])(\d+))?", t)
    if not m:
        return None
    entero, sep, dec = m.groups()
    if not sep:
        return float(entero), 0, ""
    if len(dec) == 3 and entero.lstrip("-") != "0" and decimal != sep:
        # «1.250» o «1,250»: puede ser millar o decimal. Solo se interpreta si se conoce el separador.
        return None if decimal is None else (float(entero + dec), 0, "")
    return float(f"{entero}.{dec}"), len(dec), sep


def cifras_significativas(texto: str) -> int:
    d = re.sub(r"\D", "", texto).lstrip("0")
    return len(d)


def iguales(a: str, b: str, decimal: str | None) -> bool:
    """¿Son el mismo número, quizá redondeado? «0,99» y «0,987» sí; «0,9987» y «0,987» no."""
    va, vb = valor(a, decimal), valor(b, decimal)
    if not va or not vb:
        return False
    if va[0] == vb[0]:
        return True
    corto, largo = (va, vb) if va[1] <= vb[1] else (vb, va)
    if corto[1] == 0:  # un entero no «redondea» a un decimal: 1 y 0,612 son números distintos
        return False
    return round(largo[0], corto[1]) == corto[0]


# --- Unidades --------------------------------------------------------------------------

PREFIJOS = ["", "k", "c", "m", "µ", "μ", "n", "p", "d", "M", "G", "T"]
BASE = ["m", "g", "L", "l", "s", "M", "mol", "Pa", "J", "W", "V", "A", "Hz", "B", "Da", "N", "K", "cal", "bar", "eq"]
VALIDAS = {p + b for p in PREFIJOS for b in BASE} | {
    "min", "h", "d", "°C", "%", "U", "UI", "IU", "ppm", "ppb", "rpm", "atm", "bit", "bits", "kb", "Kb", "KB", "pb",
    "bp", "kbp", "x", "×", "g", "nt", "aa", "Ω", "kΩ", "lux", "rad", "sr", "dB", "ms", "µs", "ns", "fps", "ops", "req"}
ERRONEAS = {
    "ºC": "°C (con el símbolo de grado °, no el ordinal º)", "ºc": "°C", "°c": "°C", "grs": "g", "gr": "g",
    "gs": "g", "grm": "g", "seg": "s", "segs": "s", "sg": "s", "sec": "s", "secs": "s", "mins": "min", "hrs": "h",
    "hr": "h", "Kg": "kg", "KG": "kg", "Km": "km", "KM": "km", "mts": "m", "mt": "m", "lts": "L", "lt": "L",
    "cc": "mL (o cm³)", "ul": "µL", "uL": "µL", "ug": "µg", "um": "µm", "uM": "µM", "umol": "µmol", "Ml": "mL",
    "ML": "mL", "Mg": "mg (Mg es megagramo)", "mgr": "mg", "mgs": "mg", "mseg": "ms", "Lts": "L",
    "Gr": "g", "Seg": "s", "Hz.": "Hz", "KHz": "kHz", "Mhz": "MHz", "Ghz": "GHz", "mm.": "mm"}
FUERA_SI = {"rpm": "rpm no indica la fuerza aplicada: en centrifugación se da en × g (o ambas)",
            "cc": "cc no es una unidad del SI: mL o cm³"}
MAGNITUDES = ("concentracion", "conc.", "volumen", "masa", "peso", "tiempo", "temperatura", "longitud", "velocidad",
              "actividad", "densidad", "presion", "energia", "latencia", "tiempo de respuesta", "tamano", "memoria",
              "cantidad de proteina", "proteina", "duracion", "distancia", "frecuencia", "concentration", "volume",
              "mass", "time", "temperature", "latency", "size")
RE_UNIDAD_CABECERA = re.compile(r"[(\[][^)\]]*[)\]]|/\s*\S+|\b(?:mg|g|ml|l|ul|µl|µg|m|mm|nm|s|ms|min|h|°c|k|kb|mb|gb|%|"
                                r"mol|mm|µm|um|m|kda|u)\b", re.I)


def _unidad_limpia(u: str) -> str:
    u = u.rstrip(".,;:)")
    return re.split(r"[)\]]", u)[0]


def _partes_unidad(u: str) -> list[str]:
    return [p for p in re.split(r"[/·]", u) if p]


# --- Revisión ------------------------------------------------------------------------------

def _separador_dominante(doc: Documento) -> str | None:
    comas = puntos = 0
    for b in doc.bloques:
        textos = [b.texto] if b.tipo != "tabla" else [c for f in b.filas for c in f]
        for t in textos:
            comas += len(re.findall(r"(?<![\d.,])0,\d+|\d,\d{1,2}(?!\d)|\d,\d{4,}", t))
            puntos += len(re.findall(r"(?<![\d.,])0\.\d+|\d\.\d{1,2}(?!\d)|\d\.\d{4,}", t))
    if comas == puntos == 0:
        return None
    return "," if comas >= puntos else "."


def _contexto(texto: str, ini: int, fin: int, margen: int = 40) -> str:
    a = max(0, ini - margen)
    b = min(len(texto), fin + margen)
    return ("…" if a else "") + texto[a:b].strip() + ("…" if b < len(texto) else "")


def revisar_unidades(doc: Documento, decimal: str | None) -> list[dict]:
    avisos, variantes, mal, sin_espacio, fuera = [], {}, {}, [], {}
    porcentaje = {"con": 0, "sin": 0}
    seps: dict[str, list[str]] = {",": [], ".": []}
    for b in doc.bloques:
        if b.tipo in ("codigo", "imagen"):
            continue
        textos = [b.texto] if b.tipo != "tabla" else [c for f in b.filas for c in f]
        for t in textos:
            for m in re.finditer(r"\d\s*º\s*C\b", t):
                mal.setdefault("ºC", []).append((b.seccion, _contexto(t, m.start(), m.end())))
            for m in RE_NUM.finditer(t):
                uni = _unidad_limpia(m.group("uni") or "")
                num = m.group("num")
                if uni == "%":
                    porcentaje["con" if m.group("esp") else "sin"] += 1
                v = valor(num, decimal)
                if v and v[2] and (uni or b.tipo == "tabla"):
                    seps[v[2]].append(f"{num}{m.group('esp')}{uni}".strip())
                if not uni or uni.startswith(("º", "°")) and uni not in ("°C", "ºC"):
                    continue
                partes = _partes_unidad(uni)
                if not partes:
                    continue
                if uni in ERRONEAS or any(p in ERRONEAS for p in partes):
                    clave = uni if uni in ERRONEAS else next(p for p in partes if p in ERRONEAS)
                    if clave != "ºC":
                        mal.setdefault(clave, []).append((b.seccion, _contexto(t, m.start(), m.end())))
                    continue
                if not all(p in VALIDAS or p.rstrip("⁻¹²³") in VALIDAS for p in partes):
                    continue
                for p in partes:
                    if p in FUERA_SI:
                        fuera.setdefault(p, []).append((b.seccion, _contexto(t, m.start(), m.end())))
                    if p.lower() in ("ml", "l", "µl", "ul", "dl"):
                        variantes.setdefault(p.lower(), set()).add(p)
                if not m.group("esp") and uni not in ("%", "x", "×") and not uni.startswith("°"):
                    sin_espacio.append((b.seccion, _contexto(t, m.start(), m.end()), f"{num}{uni}"))
                elif not m.group("esp") and uni == "°C":
                    sin_espacio.append((b.seccion, _contexto(t, m.start(), m.end()), f"{num}{uni}"))
    for clave, casos in mal.items():
        avisos.append({"tipo": "unidad_mal_escrita", "gravedad": "menor", "seccion": casos[0][0],
                       "detalle": f"«{clave}» → {ERRONEAS.get(clave, clave)} ({len(casos)} caso{'s' if len(casos) > 1 else ''})",
                       "casos": [c for _, c in casos[:5]]})
    if sin_espacio:
        avisos.append({"tipo": "unidad_sin_espacio", "gravedad": "menor", "seccion": sin_espacio[0][0],
                       "detalle": f"{len(sin_espacio)} cifra(s) pegada(s) a la unidad: "
                                  + ", ".join(dict.fromkeys(c for _, _, c in sin_espacio[:6]))
                                  + " (entre la cifra y la unidad va un espacio)",
                       "casos": [c for _, c, _ in sin_espacio[:5]]})
    for familia, formas in variantes.items():
        if len(formas) > 1:
            avisos.append({"tipo": "unidad_variantes", "gravedad": "menor", "seccion": "",
                           "detalle": f"la misma unidad escrita de varias formas: {', '.join(sorted(formas))}; "
                                      "elige una (mejor con L mayúscula)"})
    for p, casos in fuera.items():
        avisos.append({"tipo": "unidad_fuera_si", "gravedad": "menor", "seccion": casos[0][0],
                       "detalle": FUERA_SI[p], "casos": [c for _, c in casos[:3]]})
    if porcentaje["con"] and porcentaje["sin"]:
        avisos.append({"tipo": "porcentaje_mixto", "gravedad": "menor", "seccion": "",
                       "detalle": f"el signo % va unas veces separado ({porcentaje['con']}) y otras pegado "
                                  f"({porcentaje['sin']}); hay que elegir una forma"})
    if seps[","] and seps["."]:
        menos = "." if len(seps[","]) >= len(seps["."]) else ","
        avisos.append({"tipo": "separador_decimal", "gravedad": "menor", "seccion": "",
                       "detalle": f"se mezclan coma y punto decimal ({len(seps[','])} con coma, {len(seps['.'])} con punto); "
                                  f"ejemplos con «{menos}»: {', '.join(dict.fromkeys(seps[menos][:4]))}"})
    return avisos


def _leyenda_de_tabla(doc: Documento, i: int) -> str:
    for j in (i - 1, i + 1, i - 2, i + 2):
        if 0 <= j < len(doc.bloques) and doc.bloques[j].tipo == "leyenda" and doc.bloques[j].clase == "tabla":
            return f"Tabla {doc.bloques[j].numero}"
    return "una tabla sin leyenda"


def revisar_tablas(doc: Documento, decimal: str | None) -> list[dict]:
    avisos = []
    for i, b in enumerate(doc.bloques):
        if b.tipo != "tabla" or len(b.filas) < 2:
            continue
        nombre = _leyenda_de_tabla(doc, i)
        cab = b.filas[0]
        for c in cab:
            n = normalizar(c)
            if any(n.startswith(m) or f" {m}" in f" {n}" for m in MAGNITUDES) and not RE_UNIDAD_CABECERA.search(n):
                avisos.append({"tipo": "cabecera_sin_unidad", "gravedad": "importante", "seccion": b.seccion,
                               "detalle": f"{nombre}: la columna «{c}» no indica sus unidades"})
        for j in range(len(cab)):
            celdas = [f[j] for f in b.filas[1:] if j < len(f)]
            decs = []
            for c in celdas:
                v = valor(c.strip().split(" ")[0], decimal) if re.fullmatch(r"[-−]?\d+(?:[.,]\d+)?(?:\s*\S+)?", c.strip()) else None
                if v and v[0] != 0:
                    decs.append((v[1], c.strip()))
            if len(decs) >= 3 and max(d for d, _ in decs) - min(d for d, _ in decs) >= 2:
                ejemplos = [min(decs)[1], max(decs)[1]]
                avisos.append({"tipo": "decimales_irregulares", "gravedad": "menor", "seccion": b.seccion,
                               "detalle": f"{nombre}, columna «{cab[j]}»: número de decimales irregular "
                                          f"({' / '.join(ejemplos)}); misma magnitud, mismos decimales"})
    return avisos


# Magnitudes que solo tienen un valor en un trabajo.
SINGULARES = {
    "r2": r"R\s*\^?\s*2|R²|r²|r\^2|coeficiente de determinaci[oó]n",
    "pendiente": r"pendiente|slope",
    "ordenada": r"ordenada(?: en el origen)?|intercept|t[eé]rmino independiente",
    "pka": r"pK[aₐ]",
    "km": r"K[mM](?![a-zA-Z])|constante de Michaelis",
    "vmax": r"V\s*max|Vmáx|velocidad m[aá]xima",
    "epsilon": r"ε|coeficiente de extinci[oó]n(?: molar)?|absortividad molar",
}
NUM = r"(?<![\w.,])[-−]?\d+(?:[.,]\d+)?"


def valores_singulares(doc: Documento) -> dict[str, list[tuple[str, str, str]]]:
    hallados: dict[str, list[tuple[str, str, str]]] = {}
    for b in doc.bloques:
        textos = [b.texto] if b.tipo != "tabla" else [" ".join(f) for f in b.filas]
        for t in textos:
            for clave, patron in SINGULARES.items():
                for m in re.finditer(rf"(?:{patron})\s*(?:\([^)]{{0,20}}\)\s*)?(?:=|:|≈|de|es de|fue de|igual a|of|was)\s*({NUM})",
                                     t):
                    hallados.setdefault(clave, []).append((m.group(1), b.seccion, _contexto(t, m.start(), m.end(), 25)))
            for m in re.finditer(rf"\by\s*=\s*({NUM})\s*[·*]?\s*x\s*([+\-−])\s*({NUM})", t):
                hallados.setdefault("pendiente", []).append((m.group(1), b.seccion, m.group(0)))
                signo = "-" if m.group(2) in "-−" else ""
                hallados.setdefault("ordenada", []).append((signo + m.group(3), b.seccion, m.group(0)))
    return hallados


NOMBRE_SINGULAR = {"r2": "R²", "pendiente": "la pendiente", "ordenada": "la ordenada en el origen", "pka": "el pKa",
                   "km": "Km", "vmax": "Vmax", "epsilon": "el coeficiente de extinción"}


def revisar_singulares(doc: Documento, decimal: str | None) -> list[dict]:
    avisos = []
    for clave, lista in valores_singulares(doc).items():
        distintos: list[tuple[str, str, str]] = []
        for v in lista:
            if not any(iguales(v[0], d[0], decimal) for d in distintos):
                distintos.append(v)
        if len(distintos) > 1:
            avisos.append({"tipo": "valor_inconsistente", "gravedad": "importante", "seccion": distintos[1][1],
                           "detalle": f"{NOMBRE_SINGULAR[clave]} aparece con valores distintos: "
                                      + "; ".join(f"{v} en «{s}»" for v, s, _ in distintos),
                           "casos": [c for _, _, c in distintos]})
    return avisos


def _digitos(t: str) -> str:
    return re.sub(r"\D", "", t).lstrip("0")


def casi_iguales(a: str, b: str) -> bool:
    """Un dígito traspuesto, uno de más o de menos, o uno cambiado que no es el último."""
    x, y = _digitos(a), _digitos(b)
    if x == y or min(len(x), len(y)) < 3:
        return False
    if len(x) == len(y):
        dif = [i for i in range(len(x)) if x[i] != y[i]]
        if len(dif) == 2 and dif[1] == dif[0] + 1 and x[dif[0]] == y[dif[1]] and x[dif[1]] == y[dif[0]]:
            return True
        return len(dif) == 1 and dif[0] < len(x) - 1 and dif[0] > 0
    if abs(len(x) - len(y)) == 1:
        largo, corto = (x, y) if len(x) > len(y) else (y, x)
        return any(largo[:i] + largo[i + 1:] == corto for i in range(len(largo)))
    return False


def revisar_tabla_texto(doc: Documento, decimal: str | None) -> list[dict]:
    avisos = []
    tablas = [(i, b) for i, b in enumerate(doc.bloques) if b.tipo == "tabla" and len(b.filas) >= 2]
    numeros_tabla: list[tuple[str, str, str]] = []  # (número, tabla, fila)
    filas_por_etiqueta: list[tuple[str, str, list[str]]] = []
    for i, b in tablas:
        nombre = _leyenda_de_tabla(doc, i)
        for fila in b.filas[1:]:
            nums = [m.group(0) for c in fila for m in re.finditer(NUM, c)]
            numeros_tabla += [(n, nombre, fila[0]) for n in nums]
            etiqueta = fila[0].strip()
            if etiqueta and not re.fullmatch(r"[\d.,\s%-]+", etiqueta) and len(etiqueta) >= 3:
                filas_por_etiqueta.append((etiqueta, nombre, [m.group(0) for c in fila[1:] for m in re.finditer(NUM, c)]))
    if not tablas:
        return avisos
    todos_tabla = [n for n, _, _ in numeros_tabla]
    vistos = set()
    for b in doc.bloques:
        if b.tipo not in ("parrafo", "lista"):
            continue
        for frase in re.split(r"(?<=[.;])\s+(?=[A-ZÁÉÍÓÚ(])", b.texto):
            nums = [m for m in RE_NUM.finditer(frase) if valor(m.group("num"), decimal)
                    and (valor(m.group("num"), decimal)[1] > 0)]
            if not nums:
                continue
            fn = normalizar(frase)
            # 1) La frase nombra una fila de la tabla: sus cifras tienen que estar en esa fila.
            for etiqueta, tabla, valores in filas_por_etiqueta:
                if not valores or not re.search(rf"(?<!\w){re.escape(normalizar(etiqueta))}(?!\w)", fn):
                    continue
                for m in nums:
                    n = m.group("num")
                    if any(iguales(n, v, decimal) for v in valores) or any(iguales(n, v, decimal) for v in todos_tabla):
                        continue
                    clave = (tabla, etiqueta, n)
                    if clave in vistos:
                        continue
                    vistos.add(clave)
                    avisos.append({"tipo": "texto_tabla", "gravedad": "importante", "seccion": b.seccion,
                                   "detalle": f"el texto da {n} para «{etiqueta}», pero en {tabla} esa fila tiene "
                                              f"{', '.join(valores)}",
                                   "casos": [_contexto(frase, m.start(), m.end())]})
            # 2) Cifra casi igual a una de las tablas (error al copiar).
            for m in nums:
                n = m.group("num")
                if cifras_significativas(n) < 3 or any(iguales(n, v, decimal) for v in todos_tabla):
                    continue
                for v, tabla, fila in numeros_tabla:
                    if casi_iguales(n, v) and (n, v) not in vistos:
                        vistos.add((n, v))
                        avisos.append({"tipo": "posible_error_copia", "gravedad": "importante", "seccion": b.seccion,
                                       "detalle": f"el texto dice {n} y {tabla} (fila «{fila}») tiene {v}: "
                                                  "¿error al copiar?",
                                       "casos": [_contexto(frase, m.start(), m.end())]})
                        break
    return avisos


def revisar(ruta: str | Path) -> dict:
    doc = cargar(ruta)
    decimal = _separador_dominante(doc)
    avisos = (revisar_singulares(doc, decimal) + revisar_tabla_texto(doc, decimal)
              + revisar_tablas(doc, decimal) + revisar_unidades(doc, decimal))
    return {"archivo": str(ruta), "separador_decimal": decimal or "—", "avisos": avisos}


def informe(r: dict) -> str:
    lineas = [f"Cifras y unidades: {Path(r['archivo']).name} (separador decimal dominante: «{r['separador_decimal']}»)"]
    if r["avisos"]:
        lineas.append(f"AVISOS ({len(r['avisos'])}):")
        for a in r["avisos"]:
            donde = f" [{a['seccion']}]" if a.get("seccion") else ""
            lineas.append(f"  - ({a['gravedad']}) {a['detalle']}{donde}")
            for c in a.get("casos", [])[:3]:
                lineas.append(f"      «{c}»")
    else:
        lineas.append("AVISOS: ninguno")
    return "\n".join(lineas)


def main(argv: list[str]) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    p = argparse.ArgumentParser(description="Revisa cifras y unidades de un trabajo.")
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
