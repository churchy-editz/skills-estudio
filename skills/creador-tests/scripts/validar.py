#!/usr/bin/env python3
"""Valida un test de creador-tests: esquema y patrones de repetición.

Uso:
    python validar.py test-<tema>.json

Solo librería estándar. Códigos de salida:
    0  sin errores ni avisos
    1  hay errores (esquema, respuestas, opciones prohibidas)
    2  sin errores, pero con avisos de patrón (también hay que corregirlos)

El esquema está en references/esquema.md y los umbrales en references/variedad.md.
"""
from __future__ import annotations

import json
import math
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

TIPOS = {"multiple", "vf", "huecos", "caso"}
NIVELES = {"recordar", "comprender", "distinguir", "aplicar", "detectar_error", "ordenar"}
TECNICAS = {
    "concepto_vecino", "inversion_causa_efecto", "dato_parcial", "generalizacion",
    "error_calculo", "cifra_cercana", "orden_alterado", "intercambio", "funcion_opuesta",
}
PENALIZACIONES = {"ninguna", "1/3", "1/4"}
CON_OPCIONES = {"multiple", "caso"}

PROHIBIDAS = re.compile(
    r"\b(todas|ninguna) (de )?las (anteriores|opciones|respuestas)\b"
    r"|\b(todo|nada) (de )?lo anterior\b"
    r"|\b(all|none) of the above\b"
)
ABSOLUTAS = {"siempre", "nunca", "jamas", "todos", "todas", "ninguno", "ninguna"}
ARTICULOS = {"un", "una", "unos", "unas", "el", "la", "los", "las"}
HUECO = re.compile(r"_{3,}")
STOP = {
    "a", "al", "ante", "con", "de", "del", "el", "la", "las", "los", "lo", "en", "y", "o", "u",
    "e", "que", "se", "su", "sus", "un", "una", "unos", "unas", "por", "para", "es", "son",
    "como", "mas", "pero", "sin", "sobre", "entre", "tras", "le", "les", "ya", "si", "no",
    "cual", "cuales", "que", "esta", "este", "estos", "estas", "esa", "ese", "eso", "the",
    "of", "and", "to", "in", "is", "what", "which",
}

# Límites (ver references/variedad.md)
MAX_MISMO_INICIO = 2          # más de 2 preguntas con las mismas 3 palabras -> aviso
UMBRAL_SIMILITUD = 0.6        # Jaccard de palabras de contenido
MAX_CORRECTA_LARGA = 0.30
MAX_RATIO_LONGITUD = 2.0
LONGITUD_MINIMA = 8           # las opciones muy cortas cuentan como 8 caracteres
MAX_LETRA = 0.35
MIN_UNIFORME = 8         # con >= 8 preguntas de opciones, todas las letras igual = aviso
MAX_RACHA = 2
VF_MIN, VF_MAX = 0.40, 0.60
MAX_NIVEL = 0.40
MAX_TECNICA = 0.40
MAX_NEGATIVAS = 0.10

CATEGORIAS = [
    ("inicio_enunciado", "inicio de los enunciados"),
    ("similitud", "enunciados casi idénticos"),
    ("longitud_correcta", "la correcta no es siempre la más larga"),
    ("longitud_opciones", "longitud parecida entre opciones"),
    ("posicion", "posición de la correcta"),
    ("vf_equilibrio", "equilibrio verdadero/falso"),
    ("nivel_cognitivo", "variedad de niveles cognitivos"),
    ("tecnica_distractor", "variedad de técnicas de distractor"),
    ("negativas", "preguntas negativas"),
    ("absolutas", "palabras absolutas"),
    ("literal", "palabra del enunciado solo en la correcta"),
    ("pista_gramatical", "pistas gramaticales"),
    ("explicaciones", "inicio de las explicaciones"),
    ("secciones", "cobertura de secciones"),
]
LETRAS = "ABCD"


def normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFD", str(texto).lower())
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")


def palabras(texto: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", normalizar(texto))


def contenido(texto: str, minimo: int = 3) -> set[str]:
    return {p for p in palabras(texto) if len(p) >= minimo and p not in STOP}


def longitud(texto: str) -> int:
    return max(len(str(texto).strip()), LONGITUD_MINIMA)


def ids(lista) -> str:
    return ", ".join(str(x) for x in lista)


# --------------------------------------------------------------------------
# Errores de esquema
# --------------------------------------------------------------------------

def errores_esquema(datos) -> list[str]:
    err: list[str] = []
    if not isinstance(datos, dict):
        return ["El archivo debe ser un objeto JSON con 'meta' y 'preguntas'."]
    meta = datos.get("meta")
    if not isinstance(meta, dict):
        err.append("Falta 'meta' o no es un objeto.")
    else:
        for clave in ("titulo", "asignatura", "nivel", "penalizacion", "fuente"):
            if not isinstance(meta.get(clave), str) or not meta.get(clave, "").strip():
                err.append(f"meta.{clave}: falta o no es un texto.")
        if isinstance(meta.get("penalizacion"), str) and meta["penalizacion"] not in PENALIZACIONES:
            err.append(f"meta.penalizacion debe ser una de {sorted(PENALIZACIONES)}.")
        if "secciones" in meta and (
            not isinstance(meta["secciones"], list)
            or not all(isinstance(s, str) and s.strip() for s in meta["secciones"])
        ):
            err.append("meta.secciones debe ser una lista de textos.")
    preguntas = datos.get("preguntas")
    if not isinstance(preguntas, list) or not preguntas:
        err.append("Falta 'preguntas' o está vacía.")
        return err

    vistos: set = set()
    for n, p in enumerate(preguntas, 1):
        if not isinstance(p, dict):
            err.append(f"[#{n}] La pregunta no es un objeto.")
            continue
        pid = p.get("id", f"#{n}")
        e = lambda msg: err.append(f"[{pid}] {msg}")  # noqa: E731
        if not isinstance(p.get("id"), str) or not p["id"].strip():
            e("'id' falta o no es un texto.")
        elif p["id"] in vistos:
            e("'id' repetido.")
        vistos.add(p.get("id"))
        tipo = p.get("tipo")
        if tipo not in TIPOS:
            e(f"'tipo' debe ser uno de {sorted(TIPOS)}.")
            continue
        if p.get("nivel_cognitivo") not in NIVELES:
            e(f"'nivel_cognitivo' debe ser uno de {sorted(NIVELES)}.")
        for clave in ("enunciado", "explicacion", "seccion"):
            if not isinstance(p.get(clave), str) or not p[clave].strip():
                e(f"'{clave}' falta o está vacío.")
        dif = p.get("dificultad")
        if isinstance(dif, bool) or dif not in (1, 2, 3):
            e("'dificultad' debe ser 1, 2 o 3.")
        if tipo == "caso":
            if not isinstance(p.get("contexto"), str) or not p["contexto"].strip():
                e("Los casos prácticos necesitan 'contexto'.")
        elif "contexto" in p:
            e("'contexto' solo se usa en preguntas de tipo 'caso'.")

        correcta = p.get("correcta")
        tecnica = p.get("tecnica_distractor")
        if tipo in CON_OPCIONES:
            opciones = p.get("opciones")
            if not isinstance(opciones, list) or len(opciones) != 4:
                e("Debe tener exactamente 4 opciones.")
                continue
            if not all(isinstance(o, str) and o.strip() for o in opciones):
                e("Todas las opciones deben ser textos no vacíos.")
                continue
            normal = [" ".join(palabras(o)) for o in opciones]
            if len(set(normal)) != 4:
                e("Hay opciones repetidas.")
            for o in opciones:
                if PROHIBIDAS.search(normalizar(o)):
                    e(f"Opción prohibida: \"{o}\" (todas/ninguna de las anteriores).")
            if isinstance(correcta, bool) or not isinstance(correcta, int) or not 0 <= correcta <= 3:
                e("'correcta' debe ser UN índice entre 0 y 3 (una sola respuesta correcta).")
                continue
            if not isinstance(tecnica, list) or len(tecnica) != 4:
                e("'tecnica_distractor' debe ser una lista de 4 (null en la posición de la correcta).")
            else:
                for i, t in enumerate(tecnica):
                    if i == correcta and t is not None:
                        e("'tecnica_distractor' debe ser null en la posición de la correcta.")
                    elif i != correcta and t not in TECNICAS:
                        e(f"'tecnica_distractor[{i}]' debe ser una de {sorted(TECNICAS)}.")
        else:
            if "opciones" in p:
                e(f"Las preguntas '{tipo}' no llevan 'opciones'.")
            if tipo == "vf":
                if not isinstance(correcta, bool):
                    e("En verdadero/falso, 'correcta' debe ser true o false.")
                elif correcta is False and tecnica not in TECNICAS:
                    e("Un enunciado falso necesita 'tecnica_distractor' (la trampa que contiene).")
                elif correcta is True and tecnica not in (None,):
                    e("Un enunciado verdadero lleva 'tecnica_distractor': null.")
            else:  # huecos
                if len(HUECO.findall(p.get("enunciado", ""))) != 1:
                    e("Los huecos llevan exactamente un hueco marcado con ___ en el enunciado.")
                if (
                    not isinstance(correcta, list) or not correcta
                    or not all(isinstance(r, str) and r.strip() for r in correcta)
                ):
                    e("En huecos, 'correcta' es una lista no vacía de respuestas aceptadas.")
                if tecnica is not None:
                    e("Los huecos llevan 'tecnica_distractor': null.")
    return err


# --------------------------------------------------------------------------
# Avisos de patrón
# --------------------------------------------------------------------------

def avisos_patron(datos) -> dict[str, list[str]]:
    meta = datos["meta"]
    preguntas = datos["preguntas"]
    total = len(preguntas)
    av: dict[str, list[str]] = defaultdict(list)
    con_opc = [p for p in preguntas if p["tipo"] in CON_OPCIONES]
    vfs = [p for p in preguntas if p["tipo"] == "vf"]

    # 1. Mismo inicio de enunciado
    inicios = defaultdict(list)
    for p in preguntas:
        clave = " ".join(palabras(p["enunciado"])[:3])
        inicios[clave].append(p["id"])
    for clave, grupo in inicios.items():
        if len(grupo) > MAX_MISMO_INICIO:
            av["inicio_enunciado"].append(
                f"{len(grupo)} enunciados empiezan por \"{clave}\" (máx. {MAX_MISMO_INICIO}): {ids(grupo)}"
            )

    # 2. Enunciados casi idénticos
    conjuntos = [(p["id"], contenido(p.get("contexto", "") + " " + p["enunciado"])) for p in preguntas]
    for (ida, a), (idb, b) in combinations(conjuntos, 2):
        if a and b:
            sim = len(a & b) / len(a | b)
            if sim > UMBRAL_SIMILITUD:
                av["similitud"].append(f"{ida} y {idb} se parecen demasiado (similitud {sim:.2f} > {UMBRAL_SIMILITUD})")

    # 3 y 4. Longitud de las opciones
    larga = []
    for p in con_opc:
        lon = [longitud(o) for o in p["opciones"]]
        c = p["correcta"]
        if all(lon[c] > l for i, l in enumerate(lon) if i != c):
            larga.append(p["id"])
        if max(lon) / min(lon) > MAX_RATIO_LONGITUD:
            av["longitud_opciones"].append(
                f"{p['id']}: la opción más larga mide {max(lon) / min(lon):.1f} veces la más corta (máx. {MAX_RATIO_LONGITUD:.0f}x)"
            )
    if con_opc and len(larga) / len(con_opc) > MAX_CORRECTA_LARGA:
        av["longitud_correcta"].append(
            f"La correcta es la más larga en {len(larga)} de {len(con_opc)} preguntas "
            f"({len(larga) / len(con_opc):.0%} > {MAX_CORRECTA_LARGA:.0%}): {ids(larga)}"
        )

    # 5. Posición de la correcta
    if con_opc:
        n = len(con_opc)
        maximo = max(math.ceil(n / 4), math.floor(MAX_LETRA * n))
        cuenta = Counter(p["correcta"] for p in con_opc)
        for indice, veces in sorted(cuenta.items()):
            if veces > maximo:
                grupo = [p["id"] for p in con_opc if p["correcta"] == indice]
                av["posicion"].append(
                    f"La letra {LETRAS[indice]} es la correcta en {veces} de {n} preguntas "
                    f"(máx. {maximo}, {MAX_LETRA:.0%}): {ids(grupo)}"
                )
        if n >= MIN_UNIFORME and len(cuenta) == len(LETRAS) and len(set(cuenta.values())) == 1:
            av["posicion"].append(
                f"Reparto perfectamente uniforme: cada letra es la correcta en {n // len(LETRAS)} "
                f"de {n} preguntas. En papel se explota contando; hazlo irregular"
            )
        racha = [con_opc[0]]
        for p in con_opc[1:] + [None]:
            if p is not None and p["correcta"] == racha[-1]["correcta"]:
                racha.append(p)
                continue
            if len(racha) > MAX_RACHA:
                av["posicion"].append(
                    f"Racha de {len(racha)} preguntas seguidas con la correcta en "
                    f"{LETRAS[racha[0]['correcta']]}: {ids(q['id'] for q in racha)}"
                )
            racha = [p] if p is not None else []

    # 6. Verdadero / falso
    if vfs:
        n = len(vfs)
        verdaderas = sum(1 for p in vfs if p["correcta"] is True)
        minimo, maximo = math.floor(VF_MIN * n), math.ceil(VF_MAX * n)
        if not minimo <= verdaderas <= maximo:
            av["vf_equilibrio"].append(
                f"{verdaderas} de {n} enunciados V/F son verdaderos "
                f"(deben ser entre {minimo} y {maximo}, {VF_MIN:.0%}-{VF_MAX:.0%}): {ids(p['id'] for p in vfs)}"
            )

    # 7. Niveles cognitivos
    niveles = Counter(p["nivel_cognitivo"] for p in preguntas)
    for nivel, veces in niveles.items():
        if veces / total > MAX_NIVEL:
            grupo = [p["id"] for p in preguntas if p["nivel_cognitivo"] == nivel]
            av["nivel_cognitivo"].append(
                f"Nivel \"{nivel}\" en {veces} de {total} preguntas ({veces / total:.0%} > {MAX_NIVEL:.0%}): {ids(grupo)}"
            )

    # 8. Técnicas de distractor
    usos = defaultdict(list)
    for p in preguntas:
        t = p.get("tecnica_distractor")
        for tec in (t if isinstance(t, list) else [t]):
            if tec:
                usos[tec].append(p["id"])
    n_tec = sum(len(v) for v in usos.values())
    for tec, grupo in usos.items():
        if n_tec and len(grupo) / n_tec > MAX_TECNICA:
            av["tecnica_distractor"].append(
                f"Técnica \"{tec}\" en {len(grupo)} de {n_tec} distractores "
                f"({len(grupo) / n_tec:.0%} > {MAX_TECNICA:.0%}): {ids(dict.fromkeys(grupo))}"
            )

    # 9. Negativas
    negativas, minusculas = [], []
    for p in preguntas:
        if p["tipo"] == "vf":
            continue
        texto = p["enunciado"]
        if re.search(r"\b(NO|EXCEPTO|SALVO|INCORRECTA|FALSA)\b", texto):
            negativas.append(p["id"])
        elif re.search(r"^\W*(cu[aá]l|qu[eé])\b[^?]*\b(no|excepto|salvo)\b", texto, re.I):
            minusculas.append(p["id"])
            negativas.append(p["id"])
    limite = math.floor(MAX_NEGATIVAS * total)
    if len(negativas) > limite:
        av["negativas"].append(
            f"{len(negativas)} preguntas negativas de {total} (máx. {limite}, {MAX_NEGATIVAS:.0%}): {ids(negativas)}"
        )
    if minusculas:
        av["negativas"].append(f"Negativa sin \"NO\" en mayúsculas: {ids(minusculas)}")

    # 10, 11 y 12. Pistas dentro de la pregunta
    for p in con_opc:
        c = p["correcta"]
        distractores = [o for i, o in enumerate(p["opciones"]) if i != c]
        pal_correcta = set(palabras(p["opciones"][c]))
        pal_distr = set().union(*(set(palabras(o)) for o in distractores))
        abs_distr = (pal_distr & ABSOLUTAS) - pal_correcta
        if abs_distr:
            av["absolutas"].append(
                f"{p['id']}: \"{', '.join(sorted(abs_distr))}\" solo aparece en los distractores"
            )
        enun = contenido(p.get("contexto", "") + " " + p["enunciado"], minimo=4)
        delatoras = (enun & contenido(p["opciones"][c], minimo=4)) - pal_distr
        if delatoras:
            av["literal"].append(
                f"{p['id']}: \"{', '.join(sorted(delatoras))}\" está en el enunciado y solo en la opción correcta"
            )
        ultimas = palabras(p["enunciado"])
        if ultimas and ultimas[-1] in ARTICULOS:
            av["pista_gramatical"].append(
                f"{p['id']}: el enunciado termina en \"{ultimas[-1]}\"; el artículo puede delatar la correcta"
            )

    # 13. Inicio de las explicaciones
    exp = defaultdict(list)
    for p in preguntas:
        exp[" ".join(palabras(p["explicacion"])[:3])].append(p["id"])
    for clave, grupo in exp.items():
        if len(grupo) > MAX_MISMO_INICIO:
            av["explicaciones"].append(
                f"{len(grupo)} explicaciones empiezan por \"{clave}\" (máx. {MAX_MISMO_INICIO}): {ids(grupo)}"
            )

    # 14. Secciones sin preguntas
    if meta.get("secciones"):
        usadas = {normalizar(p["seccion"]).strip() for p in preguntas}
        for s in meta["secciones"]:
            if normalizar(s).strip() not in usadas:
                av["secciones"].append(f"La sección \"{s}\" no tiene ninguna pregunta")
        declaradas = {normalizar(s).strip() for s in meta["secciones"]}
        for p in preguntas:
            if normalizar(p["seccion"]).strip() not in declaradas:
                av["secciones"].append(f"{p['id']}: la sección \"{p['seccion']}\" no está en meta.secciones")
    return dict(av)


def aplicables(datos) -> list[str]:
    preguntas = datos["preguntas"]
    cats = [c for c, _ in CATEGORIAS]
    if not any(p["tipo"] in CON_OPCIONES for p in preguntas):
        cats = [c for c in cats if c not in
                {"longitud_correcta", "longitud_opciones", "posicion", "absolutas", "literal", "pista_gramatical"}]
    if not any(p["tipo"] == "vf" for p in preguntas):
        cats.remove("vf_equilibrio")
    if not datos["meta"].get("secciones"):
        cats.remove("secciones")
    return cats


def analizar(datos) -> tuple[list[str], dict[str, list[str]], float | None, list[str]]:
    """Devuelve (errores, avisos por categoría, puntuación de variedad, categorías aplicables)."""
    errores = errores_esquema(datos)
    if errores:
        return errores, {}, None, []
    avisos = avisos_patron(datos)
    cats = aplicables(datos)
    ok = sum(1 for c in cats if c not in avisos)
    return [], avisos, round(10 * ok / len(cats), 1), cats


def informe(nombre: str, datos, errores, avisos, nota, cats) -> str:
    n = len(datos.get("preguntas", [])) if isinstance(datos, dict) else 0
    lineas = [f"Validando {nombre} ({n} preguntas)", ""]
    if errores:
        lineas.append(f"ERRORES ({len(errores)}):")
        lineas += [f"  - {e}" for e in errores]
        lineas += ["", "Corrige los errores y vuelve a validar (los avisos de patrón se calculan después)."]
        return "\n".join(lineas)
    lineas.append("ERRORES: ninguno")
    total_av = sum(len(v) for v in avisos.values())
    if total_av:
        lineas.append(f"AVISOS DE PATRÓN ({total_av}): también hay que corregirlos")
        for cat, _ in CATEGORIAS:
            for a in avisos.get(cat, []):
                lineas.append(f"  - [{cat}] {a}")
    else:
        lineas.append("AVISOS DE PATRÓN: ninguno")
    lineas += ["", f"Variedad: {nota:g}/10"]
    for cat, texto in CATEGORIAS:
        if cat not in cats:
            lineas.append(f"  [ -- ] {texto} (no aplica)")
        elif cat in avisos:
            lineas.append(f"  [FALLA] {texto} ({len(avisos[cat])} aviso{'s' if len(avisos[cat]) > 1 else ''})")
        else:
            lineas.append(f"  [ OK ] {texto}")
    return "\n".join(lineas)


def main(argv: list[str]) -> int:
    for flujo in (sys.stdout, sys.stderr):
        try:
            flujo.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    if len(argv) != 2:
        print("Uso: python validar.py test.json", file=sys.stderr)
        return 1
    ruta = Path(argv[1])
    try:
        datos = json.loads(ruta.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"No existe el archivo: {ruta}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"JSON mal formado en {ruta}: {exc}", file=sys.stderr)
        return 1
    errores, avisos, nota, cats = analizar(datos)
    print(informe(ruta.name, datos, errores, avisos, nota, cats))
    if errores:
        return 1
    return 2 if avisos else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
