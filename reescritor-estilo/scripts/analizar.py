#!/usr/bin/env python3
"""Compara un texto original con su reescritura: naturalidad y fidelidad.

Uso:
    python analizar.py original.txt reescrito.txt [--idioma es|en] [--marcar salida.md]

Naturalidad (avisos sobre el reescrito; el original se mide para comparar):
  muletillas, frases hechas y tópicos de ensayo, cierre del texto (resumen de
  lo anterior, apelación final a expertos/futuro/equilibrio, tríada en el
  último párrafo), ritmo de frase, arranques repetidos, conectores, tríadas,
  párrafos y puntuación (guiones largos, exclamaciones). Muletillas, tópicos
  y cierre pesan el doble en la nota que las categorías de forma.
Fidelidad (errores): cifras, fechas, nombres propios, citas entre comillas y
  referencias (Autor, año) del original que faltan en el reescrito.

Las listas de muletillas, tópicos, conectores, cierres y apelaciones se leen de
references/patrones-ia.md, que es la única fuente de verdad.

--marcar escribe el ORIGINAL con las muletillas, tópicos y tríadas detectados entre ⟦ ⟧.

Código de salida: 1 si hay errores de fidelidad, 2 si solo hay avisos, 0 si está limpio.
Solo librería estándar.
"""
from __future__ import annotations

import argparse
import re
import statistics
import sys
import unicodedata
from collections import Counter
from pathlib import Path

PATRONES = Path(__file__).resolve().parents[1] / "references" / "patrones-ia.md"

# Límites (documentados en references/variedad.md)
MIN_CV_RITMO = 0.35
MIN_CV_PARRAFOS = 0.25
MAX_ARRANQUES = 2
MAX_CONECTOR_300 = 2
MAX_TRIADAS_200 = 1
MAX_GUIONES_100 = 1.0
MAX_EXCLAMACIONES_100 = 1.0
CORTA, LARGA = 8, 25
MIN_CONCEPTOS_RESUMEN = 3   # conceptos de párrafos previos repetidos en el cierre
MIN_LETRAS_CONCEPTO = 5

CATEGORIAS = [
    ("muletillas", "muletillas"),
    ("topicos", "frases hechas y tópicos"),
    ("cierre", "cierre del texto"),
    ("ritmo", "ritmo de frase"),
    ("arranques", "arranques de frase y párrafo"),
    ("conectores", "frecuencia de conectores"),
    ("triadas", "tríadas"),
    ("parrafos", "párrafos"),
    ("puntuacion", "guiones largos y exclamaciones"),
]
# Lo que más delata un texto en piloto automático es léxico: muletillas, tópicos
# y el cierre de manual. Pesan el doble que las categorías de forma.
PESOS = {"muletillas": 2, "topicos": 2, "cierre": 2}

ARTICULOS = {"el", "la", "los", "las", "un", "una", "unos", "unas", "lo",
             "the", "a", "an"}
ABREVIATURAS = ["et al.", "pp.", "p.", "etc.", "Dr.", "Dra.", "Sr.", "Sra.", "e.g.", "i.e.",
                "vs.", "cf.", "núm.", "n.º", "Ed.", "eds.", "vol.", "Mr.", "Mrs.", "Ms."]
STOP = {
    "es": {"el", "la", "de", "que", "y", "los", "las", "en", "un", "una", "por", "con", "para", "es", "del", "se"},
    "en": {"the", "of", "and", "to", "is", "in", "that", "for", "with", "it", "this", "are", "be", "on"},
}
MESES = {
    "es": "enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|setiembre|octubre|noviembre|diciembre",
    "en": "january|february|march|april|may|june|july|august|september|october|november|december",
}
VACIAS = {
    "es": set("""
        además ahora algunas algunos antes aquel aquella aquellas aquellos aunque cada cierto
        cómo como contra cosas cualquier cuando cuanto debajo desde después donde dónde durante
        ellas ellos embargo entonces entre estaba estado están estar estas estos frente fuera
        había hacer hacia hasta incluso luego mayor manera mejor menor menos mientras misma mismo
        mismas mismos mucha muchas mucho muchos nadie ningún ninguna nosotros nuestra nuestro
        nunca otras otros parte pero poder porque puede pueden pues quien quienes realmente según
        sería siempre sobre sólo solo también tanto tenemos tener tiene tienen todas todavía todos
        través veces vuestra vuestro forma hacen hecho""".split()),
    "en": set("""
        about above after again against along among another anything around because before being
        below between both cannot could doing during each either every first from further having
        however into itself later least might more most much must never other others ourselves
        over perhaps quite rather really same several should since some something still such than
        that their them themselves then there these they thing things this those though through
        under until very what when where whether which while whose with within without would your
        also just like make made many even""".split()),
}
CONJ = {"es": r"(?:y|e|o|u)", "en": r"(?:and|or)"}
ADVERSATIVAS = {"pero", "sino", "aunque", "mas", "but", "yet", "although"}
# Adverbios entre comas («Los problemas, también, y…»): inciso, no elemento de lista.
INCISOS = {"también", "tampoco", "además", "incluso", "claro", "too", "also", "though", "however"}
PAL = r"[^\W\d_][\w'’-]*"


# ---------------------------------------------------------------- patrones

def cargar_patrones(ruta: Path = PATRONES) -> dict:
    """Lee las tablas '## ES · …' / '## EN · …' de patrones-ia.md.

    Devuelve {idioma: {"muletillas": [...], "topicos": [...], "conectores": [...],
    "cierres": [...], "apelaciones": [...], "entradas": n, "filas": {clase: n}}}.
    Solo se detectan las celdas escritas entre `comillas invertidas`; las filas
    sin ellas son descriptivas (estructuras que se miden con otras reglas).
    """
    datos = {i: {"muletillas": [], "topicos": [], "conectores": [], "cierres": [], "apelaciones": [],
                 "entradas": 0, "filas": Counter()} for i in ("es", "en")}
    idioma = clase = None
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^##\s+(ES|EN)\s+·\s+(.+)$", linea)
        if m:
            idioma = m.group(1).lower()
            t = m.group(2).lower()
            clase = ("topicos" if "tópico" in t else
                     "apelaciones" if "apelaci" in t else
                     "conectores" if "conector" in t else
                     "cierres" if "cierre" in t else
                     "muletillas" if "muletilla" in t else None)
            continue
        if linea.startswith("## "):
            idioma = clase = None
            continue
        if not idioma or not linea.startswith("|") or re.match(r"^\|\s*-", linea):
            continue
        celdas = [c.strip() for c in linea.strip().strip("|").split("|")]
        if not celdas or celdas[0].lower() in {"patrón", "pattern", "tic", "estructura"}:
            continue
        datos[idioma]["entradas"] += 1
        if clase:
            datos[idioma]["filas"][clase] += 1
            datos[idioma][clase].extend(re.findall(r"`([^`]+)`", celdas[0]))
    return datos


def compilar(frase: str) -> re.Pattern:
    partes = [re.escape(p.strip()) for p in re.split(r"…|\.\.\.", frase.lower()) if p.strip()]
    cuerpo = r"\b.{1,80}?\b".join(partes)
    ini = r"(?<!\w)" if re.match(r"\w", frase) else ""
    fin = r"(?!\w)" if re.search(r"\w$", frase.replace("…", "")) else ""
    return re.compile(ini + cuerpo + fin, re.IGNORECASE | re.DOTALL)


def contar_frases(texto: str, grupos: list[tuple[str, list[str]]]) -> dict[str, Counter]:
    """Cuenta apariciones de cada frase por clase, sin contar dos veces el mismo tramo.

    Si dos patrones se solapan («cada vez más» dentro de «en un mundo cada vez
    más»), cuenta el más largo; a igual tramo, la clase que va antes en `grupos`.
    """
    candidatos = []
    for orden, (clase, frases) in enumerate(grupos):
        for frase in dict.fromkeys(frases):
            for m in compilar(frase).finditer(texto):
                candidatos.append((-(m.end() - m.start()), orden, m.start(), m.end(), clase, frase))
    candidatos.sort()
    ocupado: list[tuple[int, int]] = []
    cuentas = {clase: Counter() for clase, _ in grupos}
    for _, _, a, b, clase, frase in candidatos:
        if any(a < y and x < b for x, y in ocupado):
            continue
        ocupado.append((a, b))
        cuentas[clase][frase] += 1
    return cuentas


# ---------------------------------------------------------------- texto

def detectar_idioma(texto: str) -> str:
    pal = Counter(re.findall(r"\w+", texto.lower()))
    puntos = {i: sum(pal[w] for w in s) for i, s in STOP.items()}
    return max(puntos, key=puntos.get)


def palabras(texto: str) -> list[str]:
    return re.findall(r"[\w'’-]+", texto)


def proteger(texto: str) -> str:
    for a in ABREVIATURAS:
        texto = texto.replace(a, a.replace(".", "§"))
    return re.sub(r"(\d)\.(\d)", r"\1§\2", texto)


def frases_de(parrafo: str) -> list[str]:
    trozos = re.split(r"(?<=[.!?…:])\s+(?=[\"«“¿¡(]?[A-ZÁÉÍÓÚÑÜ0-9])|\n", proteger(parrafo))
    return [t.replace("§", ".").strip() for t in trozos if re.search(r"\w", t)]


def parrafos_de(texto: str) -> list[str]:
    bloques = [b.strip() for b in re.split(r"\n\s*\n", texto) if b.strip()]
    if len(bloques) == 1 and texto.count("\n") >= 2:
        bloques = [l.strip() for l in texto.splitlines() if l.strip()]
    return bloques


def es_titulo(parrafo: str) -> bool:
    return parrafo.lstrip().startswith("#")


def limpiar_md(t: str) -> str:
    t = re.sub(r"^#+\s*", "", t, flags=re.M)
    t = re.sub(r"^\s*[-*]\s+", "", t, flags=re.M)
    return t.replace("**", "").replace("__", "")


def raiz(palabra: str) -> str:
    """Raíz tosca para comparar conceptos: minúsculas, sin tildes, 5 letras."""
    sin = "".join(c for c in unicodedata.normalize("NFD", palabra.lower()) if unicodedata.category(c) != "Mn")
    return sin[:MIN_LETRAS_CONCEPTO]


def conceptos(texto: str, idioma: str) -> set[str]:
    return {raiz(p) for p in re.findall(PAL, texto)
            if len(p) >= MIN_LETRAS_CONCEPTO and p.lower() not in VACIAS[idioma]}


def analizar_cierre(parrafos: list[str], idioma: str, pat: dict) -> dict:
    """Mira el último párrafo: si resume lo anterior, cómo termina y si trae tríadas.

    Un concepto clave de un párrafo previo es una raíz que sale en pocos párrafos
    (como mucho en la mitad menos uno de los previos, mínimo 1): así no cuenta el
    tema general del texto, que aparece en todas partes. El cierre «resume» si
    repite al menos MIN_CONCEPTOS_RESUMEN conceptos clave venidos de dos párrafos
    distintos o más (si solo vienen del anterior, es continuidad, no resumen).
    """
    vacio = {"aplica": False, "resumen": [], "apelacion": None, "triadas": []}
    if len(parrafos) < 2:
        return vacio
    previos = [conceptos(p, idioma) for p in parrafos[:-1]]
    ultimo = parrafos[-1]
    frecuencia = Counter(c for cs in previos for c in cs)
    tope = max(1, (len(previos) - 1) // 2)
    repetidos, origen = [], set()
    palabra_de = {}
    for p in re.findall(PAL, ultimo):
        palabra_de.setdefault(raiz(p), p.lower())
    if len(previos) >= 2:
        for c in sorted(conceptos(ultimo, idioma), key=lambda c: ultimo.lower().find(palabra_de[c])):
            if 0 < frecuencia[c] <= tope:
                repetidos.append(palabra_de[c])
                origen |= {i for i, cs in enumerate(previos) if c in cs}
    resumen = repetidos if len(repetidos) >= MIN_CONCEPTOS_RESUMEN and len(origen) >= 2 else []

    frases = frases_de(ultimo)
    apelacion = None
    if frases:
        final = frases[-1].lower()
        for palabra in pat["apelaciones"]:
            if compilar(palabra).search(final):
                apelacion = palabra
                break
    return {"aplica": True, "resumen": resumen, "apelacion": apelacion,
            "triadas": [t for _, _, t in triadas(ultimo, idioma)]}


def cv(valores: list[float]) -> float:
    if len(valores) < 2 or statistics.mean(valores) == 0:
        return 0.0
    return statistics.pstdev(valores) / statistics.mean(valores)


def clave_arranque(frase: str) -> str:
    pal = [p.lower() for p in re.findall(PAL, frase)]
    if not pal:
        return ""
    return " ".join(pal[:2]) if pal[0] in ARTICULOS and len(pal) > 1 else pal[0]


def triadas(texto: str, idioma: str) -> list[tuple[int, int, str]]:
    """Enumeraciones de exactamente 3 elementos: «a, b y c», «a, b, and c».

    Devuelve (inicio, fin, texto) con posiciones en `texto`. El primer elemento
    es la palabra anterior a la primera coma; se descartan las listas de 4 o más
    y los falsos positivos con «pero/sino/but» («X, pero también Y y Z»).
    """
    otro = rf"{PAL}(?:\s+{PAL}){{0,3}}"
    patron = re.compile(rf"({PAL}),\s+({otro}),?\s+{CONJ[idioma]}\s+({PAL}(?:\s+{PAL}){{0,2}})")
    encontradas = []
    for frase in re.finditer(r"[^.!?;:\n]+", texto):
        f = frase.group(0)
        for m in patron.finditer(f):
            if re.search(r",\s*(?:[\w'’-]+\s+){0,3}$", f[:m.start()]):
                continue  # enumeración de 4 o más («a, en la b, en la c y d»)
            if m.group(2).split()[0].lower() in ADVERSATIVAS:
                continue
            if m.group(2).lower() in INCISOS:
                continue
            ini = frase.start() + m.start()
            encontradas.append((ini, ini + len(m.group(0)), m.group(0)))
    return encontradas


# ---------------------------------------------------------------- métricas

def medir(texto: str, idioma: str, pat: dict) -> dict:
    parrafos = [p for p in parrafos_de(texto) if not es_titulo(p)]
    cuerpo = limpiar_md("\n\n".join(parrafos))
    n_pal = len(palabras(cuerpo))
    frases = [f for p in parrafos for f in frases_de(limpiar_md(p))]
    largos = [len(palabras(f)) for f in frases]
    bajo = cuerpo.lower()

    cuentas = contar_frases(bajo, [("topicos", pat["topicos"]), ("muletillas", pat["muletillas"] + pat["cierres"])])
    muletillas, topicos = cuentas["muletillas"], cuentas["topicos"]
    conectores = Counter()
    for frase in pat["conectores"]:
        n = len(compilar(frase).findall(bajo))
        if n:
            conectores[frase] += n

    cierres_re = [compilar(c) for c in pat["cierres"]]
    con_cierre = 0
    for p in parrafos:
        fs = frases_de(limpiar_md(p))
        if len(fs) >= 2 and any(r.match(fs[-1].lower().lstrip("¿¡\"«“")) for r in cierres_re):
            con_cierre += 1

    return {
        "palabras": n_pal,
        "frases": len(frases),
        "media": statistics.mean(largos) if largos else 0.0,
        "desv": statistics.pstdev(largos) if len(largos) > 1 else 0.0,
        "cv": cv(largos),
        "cortas": sum(l < CORTA for l in largos) / len(largos) if largos else 0.0,
        "largas": sum(l > LARGA for l in largos) / len(largos) if largos else 0.0,
        "arr_frases": Counter(clave_arranque(f) for f in frases if clave_arranque(f)),
        "arr_parrafos": Counter(clave_arranque(p) for p in (limpiar_md(x) for x in parrafos) if clave_arranque(p)),
        "muletillas": muletillas,
        "topicos": topicos,
        "cierre": analizar_cierre([limpiar_md(p) for p in parrafos], idioma, pat),
        "conectores": conectores,
        "triadas": [t for _, _, t in triadas(cuerpo, idioma)],
        "parrafos": len(parrafos),
        "cv_parrafos": cv([len(palabras(limpiar_md(p))) for p in parrafos]),
        "con_cierre": con_cierre,
        "guiones": cuerpo.count("—") * 100 / max(n_pal, 1),
        "exclamaciones": cuerpo.count("!") * 100 / max(n_pal, 1),
    }


def avisos(m: dict) -> tuple[dict[str, list[str]], list[str]]:
    av: dict[str, list[str]] = {c: [] for c, _ in CATEGORIAS}
    aplicables = ["muletillas", "topicos", "arranques", "conectores", "triadas", "puntuacion"]

    for frase, n in m["muletillas"].most_common():
        av["muletillas"].append(f"«{frase}» ×{n}")
    for frase, n in m["topicos"].most_common():
        av["topicos"].append(f"«{frase}» ×{n}")

    ci = m["cierre"]
    if ci["aplica"]:
        aplicables.append("cierre")
        if ci["resumen"]:
            av["cierre"].append(
                f"el último párrafo resume lo anterior: repite {len(ci['resumen'])} conceptos de párrafos previos "
                f"({', '.join(ci['resumen'][:6])}…). Cierra con algo concreto o termina en la última idea")
        if ci["apelacion"]:
            av["cierre"].append(
                f"la última frase apela a «{ci['apelacion']}»: cierre de manual (expertos, el futuro, la opción equilibrada)")

    if m["frases"] >= 5:
        aplicables.append("ritmo")
        if m["cv"] < MIN_CV_RITMO:
            av["ritmo"].append(
                f"ritmo plano: CV {num(m['cv'], 2)} < {num(MIN_CV_RITMO, 2)} (media {num(m['media'])} palabras, "
                f"desviación {num(m['desv'])}). Alterna frases cortas y largas de verdad"
            )

    for nombre, cuenta in (("frases", m["arr_frases"]), ("párrafos", m["arr_parrafos"])):
        for clave, n in cuenta.most_common():
            if n > MAX_ARRANQUES:
                av["arranques"].append(f"{n} {nombre} empiezan por «{clave}» (máx. {MAX_ARRANQUES})")

    tope = MAX_CONECTOR_300 * max(1.0, m["palabras"] / 300)
    for frase, n in m["conectores"].most_common():
        if n > tope:
            av["conectores"].append(f"«{frase}» ×{n} (máx. {tope:.0f} para {m['palabras']} palabras)")

    tope_t = MAX_TRIADAS_200 * max(1.0, m["palabras"] / 200)
    if len(m["triadas"]) > tope_t:
        ejemplos = "; ".join(f"«{t}»" for t in m["triadas"][:4])
        av["triadas"].append(f"{len(m['triadas'])} enumeraciones de 3 (máx. {tope_t:.0f}): {ejemplos}")
    for tri in ci["triadas"]:
        av["triadas"].append(f"tríada en el último párrafo: «{tri}» (en el cierre se nota aunque sea una)")

    if m["parrafos"] >= 2:
        aplicables.append("parrafos")
        if m["parrafos"] >= 3 and m["cv_parrafos"] < MIN_CV_PARRAFOS:
            av["parrafos"].append(f"párrafos de longitud parecida: CV {num(m['cv_parrafos'], 2)} < {num(MIN_CV_PARRAFOS, 2)}")
        if m["con_cierre"] * 2 > m["parrafos"]:
            av["parrafos"].append(f"{m['con_cierre']} de {m['parrafos']} párrafos acaban en frase-resumen")

    if m["guiones"] > MAX_GUIONES_100:
        av["puntuacion"].append(f"{num(m['guiones'])} guiones largos por 100 palabras (máx. {MAX_GUIONES_100:.0f})")
    if m["exclamaciones"] > MAX_EXCLAMACIONES_100:
        av["puntuacion"].append(f"{num(m['exclamaciones'])} exclamaciones por 100 palabras (máx. {MAX_EXCLAMACIONES_100:.0f})")

    return {c: v for c, v in av.items() if v}, aplicables


def nota(av: dict, aplicables: list[str]) -> float:
    total = sum(PESOS.get(c, 1) for c in aplicables)
    ok = sum(PESOS.get(c, 1) for c in aplicables if c not in av)
    return round(10 * ok / total, 1) if total else 10.0


# ---------------------------------------------------------------- fidelidad

def norm(t: str) -> str:
    return re.sub(r"\s+", " ", t.replace("’", "'")).strip()


def elementos_fijos(texto: str, idioma: str) -> dict[str, list[str]]:
    t = norm(texto)
    citas = [norm(next(g for g in grupos if g))
             for grupos in re.findall(r"«([^»]+)»|“([^”]+)”|\"([^\"]+)\"", t)]
    refs = [norm(r) for r in re.findall(r"\(([^()]*?[A-ZÁÉÍÓÚÑ][^()]*?\b(?:1[5-9]|20)\d{2}[a-z]?(?:[^()]*))\)", t)]
    narr = re.findall(r"([A-ZÁÉÍÓÚÑ][\w'-]+(?:\s+et\s+al\.)?)\s+\(((?:1[5-9]|20)\d{2}[a-z]?)\)", t)
    fechas = [f for f in re.findall(
        rf"\b\d{{1,2}}\s+de\s+(?:{MESES['es']})(?:\s+de\s+\d{{4}})?|\b(?:{MESES['es']})\s+de\s+\d{{4}}"
        rf"|\b(?:{MESES['en']})\s+\d{{1,2}}(?:,\s*\d{{4}})?|\b\d{{1,2}}\s+(?:{MESES['en']})(?:\s+\d{{4}})?",
        t, re.IGNORECASE)]
    cifras = re.findall(r"(?<![\w.,])\d+(?:[.,:/-]\d+)*", t)

    nombres = []
    for linea in texto.splitlines():
        for frase in frases_de(limpiar_md(linea)):
            toks = re.findall(rf"{PAL}", frase)
            for tok in toks[1:]:
                if tok[0].isupper() and tok != "I" and not tok.startswith("§"):
                    nombres.append(tok)
    unicos = lambda xs: list(dict.fromkeys(xs))
    return {
        "cifras": unicos(cifras), "fechas": unicos(fechas), "nombres": unicos(nombres),
        "citas": unicos(citas), "referencias": unicos(refs + [f"{a} ({y})" for a, y in narr]),
    }


def fidelidad(original: str, reescrito: str, idioma: str) -> tuple[list[str], dict[str, int]]:
    fijos = elementos_fijos(original, idioma)
    r = norm(reescrito)
    rl = r.lower()
    errores = []
    for cifra in fijos["cifras"]:
        if not re.search(rf"(?<![\d]){re.escape(cifra)}(?![\d])", r):
            errores.append(f"cifra «{cifra}» no aparece en el reescrito")
    for fecha in fijos["fechas"]:
        if norm(fecha).lower() not in rl:
            errores.append(f"fecha «{fecha}» no aparece en el reescrito")
    for nombre in fijos["nombres"]:
        if not re.search(rf"(?<![\w]){re.escape(nombre)}(?![\w])", r):
            errores.append(f"nombre propio «{nombre}» no aparece en el reescrito")
    for cita in fijos["citas"]:
        if cita not in r:
            errores.append(f"cita «{cita[:60]}» no aparece literal en el reescrito")
    for ref in fijos["referencias"]:
        m = re.match(r"(.+) \((\d{4}[a-z]?)\)$", ref)
        alternativa = f"({m.group(1)}, {m.group(2)})" if m else None
        if ref not in r and not (alternativa and alternativa in r):
            errores.append(f"referencia «{ref}» no aparece en el reescrito")
    return errores, {k: len(v) for k, v in fijos.items()}


# ---------------------------------------------------------------- informe

def marcar(texto: str, idioma: str, pat: dict) -> str:
    tramos = []
    for frase in pat["muletillas"] + pat["topicos"] + pat["cierres"] + pat["conectores"]:
        tramos += [(m.start(), m.end()) for m in compilar(frase).finditer(texto)]
    tramos += [(a, b) for a, b, _ in triadas(texto, idioma)]
    tramos.sort()
    fusion = []
    for a, b in tramos:
        if fusion and a <= fusion[-1][1]:
            fusion[-1] = (fusion[-1][0], max(b, fusion[-1][1]))
        else:
            fusion.append((a, b))
    salida, ult = [], 0
    for a, b in fusion:
        salida += [texto[ult:a], "⟦", texto[a:b], "⟧"]
        ult = b
    return "".join(salida + [texto[ult:]])


def fila(nombre: str, a, b) -> str:
    return f"  {nombre:<30}{a:>10}{b:>12}"


def num(x: float, dec: int = 1) -> str:
    return f"{x:.{dec}f}".replace(".", ",")


def informe(ruta_o: str, ruta_r: str, idioma: str, mo: dict, mr: dict, av_o, av_r, ap_o, ap_r,
            errores: list[str], cuentas: dict[str, int]) -> str:
    l = [f"Análisis de estilo · {Path(ruta_o).name} → {Path(ruta_r).name} · idioma: {idioma}", ""]
    l.append(fila("", "Original", "Reescrito"))
    l.append(fila("Palabras", mo["palabras"], mr["palabras"]))
    l.append(fila("Muletillas", sum(mo["muletillas"].values()), sum(mr["muletillas"].values())))
    l.append(fila("Tópicos de ensayo", sum(mo["topicos"].values()), sum(mr["topicos"].values())))
    l.append(fila("Frase media (palabras)", num(mo["media"]), num(mr["media"])))
    l.append(fila("Desviación", num(mo["desv"]), num(mr["desv"])))
    l.append(fila("CV del ritmo", num(mo["cv"], 2), num(mr["cv"], 2)))
    l.append(fila(f"Frases cortas (<{CORTA})", f"{mo['cortas']:.0%}", f"{mr['cortas']:.0%}"))
    l.append(fila(f"Frases largas (>{LARGA})", f"{mo['largas']:.0%}", f"{mr['largas']:.0%}"))
    l.append(fila("Conectores sobreusados", sum(mo["conectores"].values()), sum(mr["conectores"].values())))
    l.append(fila("Tríadas", len(mo["triadas"]), len(mr["triadas"])))
    l.append(fila("CV de párrafos", num(mo["cv_parrafos"], 2), num(mr["cv_parrafos"], 2)))
    l.append(fila("Párrafos con cierre-resumen", f"{mo['con_cierre']}/{mo['parrafos']}", f"{mr['con_cierre']}/{mr['parrafos']}"))
    l.append(fila("Cierre que resume (conceptos)", len(mo["cierre"]["resumen"]), len(mr["cierre"]["resumen"])))
    l.append(fila("Guiones largos /100 pal.", num(mo["guiones"]), num(mr["guiones"])))
    l.append(fila("Exclamaciones /100 pal.", num(mo["exclamaciones"]), num(mr["exclamaciones"])))
    if mr["conectores"]:
        l.append("  Conectores en el reescrito: " + ", ".join(f"{c} ×{n}" for c, n in mr["conectores"].most_common()))
    l.append("")

    if errores:
        l.append(f"FIDELIDAD: {len(errores)} problema(s)")
        l += [f"  - {e}" for e in errores]
    else:
        partes = ", ".join(f"{k}: {v}" for k, v in cuentas.items() if v)
        l.append(f"FIDELIDAD: OK ({partes or 'sin datos fijos que comprobar'})")
    l.append("")

    if av_r:
        total = sum(len(v) for v in av_r.values())
        l.append(f"AVISOS EN EL REESCRITO ({total}):")
        for c, lista in av_r.items():
            l += [f"  - [{c}] {a}" for a in lista]
    else:
        l.append("AVISOS EN EL REESCRITO: ninguno")
    l.append("")
    l.append(f"Naturalidad: {num(nota(av_r, ap_r))}/10 (original: {num(nota(av_o, ap_o))}/10)")
    for c, desc in CATEGORIAS:
        estado = "--" if c not in ap_r else ("FALLA" if c in av_r else " OK ")
        l.append(f"  [{estado}] {desc}")
    l.append(f"Fidelidad: {'OK' if not errores else f'{len(errores)} problemas'}")
    return "\n".join(l)


def analizar(original: str, reescrito: str, idioma: str | None = None, patrones: dict | None = None) -> dict:
    idioma = idioma or detectar_idioma(original)
    pat = (patrones or cargar_patrones())[idioma]
    mo, mr = medir(original, idioma, pat), medir(reescrito, idioma, pat)
    av_o, ap_o = avisos(mo)
    av_r, ap_r = avisos(mr)
    errores, cuentas = fidelidad(original, reescrito, idioma)
    return {"idioma": idioma, "original": mo, "reescrito": mr, "avisos_original": av_o,
            "aplicables_original": ap_o, "avisos": av_r, "aplicables": ap_r,
            "naturalidad": nota(av_r, ap_r), "errores": errores, "cuentas": cuentas}


def main(argv: list[str]) -> int:
    for flujo in (sys.stdout, sys.stderr):
        try:
            flujo.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description="Naturalidad y fidelidad de una reescritura.")
    ap.add_argument("original")
    ap.add_argument("reescrito")
    ap.add_argument("--idioma", choices=["es", "en"])
    ap.add_argument("--marcar", metavar="SALIDA", help="escribe el original con los patrones marcados ⟦ ⟧")
    a = ap.parse_args(argv[1:])
    textos = []
    for ruta in (a.original, a.reescrito):
        try:
            textos.append(Path(ruta).read_text(encoding="utf-8"))
        except OSError as e:
            print(f"No se puede leer {ruta}: {e}", file=sys.stderr)
            return 1
    r = analizar(*textos, idioma=a.idioma)
    print(informe(a.original, a.reescrito, r["idioma"], r["original"], r["reescrito"],
                  r["avisos_original"], r["avisos"], r["aplicables_original"], r["aplicables"],
                  r["errores"], r["cuentas"]))
    if a.marcar:
        Path(a.marcar).write_text(marcar(textos[0], r["idioma"], cargar_patrones()[r["idioma"]]), encoding="utf-8")
    if r["errores"]:
        return 1
    return 2 if r["avisos"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
