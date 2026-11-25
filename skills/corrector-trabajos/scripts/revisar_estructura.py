#!/usr/bin/env python3
"""Revisa la estructura de un trabajo: secciones, figuras, tablas y objetivos.

Uso:
    python revisar_estructura.py trabajo.(docx|pdf|md|tex|txt) --tipo TIPO [--json salida.json]

TIPO: laboratorio | tecnico | tfg | ensayo | bibliografico

Comprueba:
- secciones obligatorias y recomendadas del tipo (en castellano, inglés o euskera)
  y su orden;
- figuras y tablas: numeración sin saltos ni repeticiones, leyenda con texto,
  citadas en el texto, imágenes y tablas sin leyenda, citas a figuras que no existen;
- objetivos que no vuelven a aparecer en resultados, pruebas o conclusiones;
- memorias técnicas y TFG: sección de pruebas sin resultados medibles.

Código de salida: 0 si no hay avisos, 2 si los hay. Solo librería estándar
(python-docx para leer DOCX).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from extraer import Bloque, Documento, cargar, normalizar  # noqa: E402

# Sinónimos de cada sección (normalizados: minúsculas y sin tildes). Los más largos primero.
SECCIONES = {
    "resultados_discusion": ["resultados y discusion", "results and discussion", "emaitzak eta eztabaida",
                             "analisis y discusion de resultados"],
    "resumen": ["resumen", "abstract", "laburpena", "summary", "sinopsis"],
    "objetivos": ["objetivos", "objetivo", "objectives", "objective", "aims", "goals", "helburuak", "helburua",
                  "objetivos del proyecto", "objetivos de la practica"],
    "introduccion": ["introduccion", "introduction", "sarrera", "antecedentes", "marco teorico", "fundamento teorico",
                     "fundamentos teoricos", "background", "estado del arte", "estado de la cuestion"],
    "metodos": ["materiales y metodos", "material y metodos", "materiales y metodo", "metodos", "metodologia",
                "procedimiento experimental", "procedimiento", "parte experimental", "metodo experimental",
                "materials and methods", "methods", "methodology", "materialak eta metodoak", "metodoak",
                "prozedura", "busqueda bibliografica", "estrategia de busqueda"],
    "resultados": ["resultados", "results", "emaitzak"],
    "discusion": ["discusion de resultados", "discusion", "discussion", "eztabaida", "analisis de resultados"],
    "conclusiones": ["conclusiones y trabajo futuro", "conclusiones", "conclusion", "conclusions", "ondorioak",
                     "ondorioa", "consideraciones finales"],
    "bibliografia": ["referencias bibliograficas", "bibliografia", "referencias", "references", "bibliography",
                     "erreferentziak", "webgrafia", "fuentes"],
    "analisis": ["analisis de requisitos", "requisitos", "especificacion", "analisis", "requirements", "analysis",
                 "eskakizunak", "analisia"],
    "diseno": ["diseno del sistema", "diseno", "arquitectura", "design", "architecture", "diseinua"],
    "implementacion": ["implementacion", "desarrollo del sistema", "implementation", "inplementazioa", "garapena"],
    "pruebas": ["pruebas y resultados", "pruebas", "validacion", "evaluacion", "testing", "tests", "evaluation",
                "probak", "ebaluazioa", "experimentos"],
    "planificacion": ["planificacion", "gestion del proyecto", "planning", "plangintza"],
    "anexos": ["anexos", "anexo", "apendice", "appendix", "eranskinak", "eranskina"],
}
NOMBRES = {
    "resumen": "Resumen", "introduccion": "Introducción", "objetivos": "Objetivos", "metodos": "Materiales y métodos",
    "resultados": "Resultados", "discusion": "Discusión", "conclusiones": "Conclusiones",
    "bibliografia": "Bibliografía", "analisis": "Análisis / requisitos", "diseno": "Diseño",
    "implementacion": "Implementación", "pruebas": "Pruebas", "planificacion": "Planificación",
    "resultados_discusion": "Resultados y discusión", "anexos": "Anexos", "desarrollo": "Desarrollo",
}

# Cada requisito es un grupo de alternativas: basta con una de ellas.
# (grupo, obligatoria)
TIPOS = {
    "laboratorio": [(("introduccion",), True), (("objetivos",), True), (("metodos",), True),
                    (("resultados", "resultados_discusion"), True), (("discusion", "resultados_discusion"), True),
                    (("conclusiones",), True), (("bibliografia",), True)],
    "tecnico": [(("objetivos",), True), (("analisis",), True), (("diseno",), True), (("implementacion",), True),
                (("pruebas",), True), (("conclusiones",), True), (("introduccion",), False),
                (("bibliografia",), False)],
    "tfg": [(("resumen",), True), (("introduccion",), True), (("objetivos",), True),
            (("metodos", "analisis", "diseno"), True), (("resultados", "pruebas", "resultados_discusion"), True),
            (("discusion", "resultados_discusion"), False), (("conclusiones",), True), (("bibliografia",), True),
            (("planificacion",), False)],
    "ensayo": [(("introduccion",), True), (("desarrollo",), True), (("conclusiones",), True),
               (("bibliografia",), False)],
    "bibliografico": [(("introduccion",), True), (("objetivos",), False), (("metodos",), False),
                      (("desarrollo",), True), (("conclusiones",), True), (("bibliografia",), True)],
}
ORDEN = ["resumen", "introduccion", "objetivos", "metodos", "analisis", "planificacion", "diseno", "implementacion",
         "resultados", "resultados_discusion", "pruebas", "discusion", "conclusiones", "bibliografia", "anexos"]

PALABRAS_VACIAS = set("""
el la los las un una unos unas de del al a en por para con sin sobre entre que se su sus y o u e ni como mas
menos muy este esta estos estas ese esa eso lo le les ha han ser sera seran es son fue estar debe deben poder puede
pueden cada todo toda todos todas otro otra otros otras mismo misma tambien mediante segun desde hasta cuando donde
the of and to in for with on by from that this these is are be will can should must which as at an or
eta da dira bat ere edo
objetivo objetivos alumno alumna practica trabajo proyecto realizar conseguir lograr permitir desarrollar llevar cabo
""".split())


def canonica(titulo: str) -> str | None:
    t = normalizar(titulo)
    t = re.sub(r"^(?:\d+(?:\.\d+)*\.?|[ivxlc]+\.|[a-z]\))\s*", "", t)
    t = re.sub(r"^(?:capitulo|chapter|atala)\s+\d+\.?\s*[:.\-–]?\s*", "", t)
    mejor = None
    for clave, sinonimos in SECCIONES.items():
        for s in sinonimos:
            if t == s or t.startswith(s + " ") or t.startswith(s + ":") or t.startswith(s + ","):
                if mejor is None or len(s) > mejor[1]:
                    mejor = (clave, len(s))
    return mejor[0] if mejor else None


def mapa_secciones(doc: Documento) -> list[tuple[Bloque, str | None]]:
    """(título, sección canónica) para cada título, heredando la del padre si no tiene."""
    salida, pila = [], []
    for b in doc.titulos():
        if b.nivel == 0:
            continue
        while pila and pila[-1][0] >= b.nivel:
            pila.pop()
        propia = canonica(b.texto)
        heredada = next((c for _, c in reversed(pila) if c), None)
        pila.append((b.nivel, propia))
        salida.append((b, propia or heredada))
    return salida


def bloques_por_seccion(doc: Documento) -> dict[str, list[Bloque]]:
    secciones: dict[str, list[Bloque]] = {}
    actual = None
    mapa = {id(b): c for b, c in mapa_secciones(doc)}
    for b in doc.bloques:
        if b.tipo == "titulo":
            if b.nivel == 0:
                continue
            actual = mapa.get(id(b)) or "desarrollo"
            secciones.setdefault(actual, [])
        elif actual:
            secciones[actual].append(b)
    return secciones


def revisar_secciones(doc: Documento, tipo: str) -> dict:
    mapa = mapa_secciones(doc)
    principales = [(b, c) for b, c in mapa if b.nivel == min((x.nivel for x, _ in mapa), default=1)]
    presentes = []
    for b, c in mapa:
        if c and c not in presentes:
            presentes.append(c)
    hay_desarrollo = any(c is None for _, c in principales)
    if hay_desarrollo:
        presentes.append("desarrollo")
    faltan, recomendadas = [], []
    for grupo, obligatoria in TIPOS[tipo]:
        if any(g in presentes for g in grupo):
            continue
        # Objetivos dentro de la introducción cuentan, pero se avisa.
        if grupo == ("objetivos",):
            intro = [b.texto for b in bloques_por_seccion(doc).get("introduccion", [])]
            if any(re.search(r"\b(objetivo|helburu|aim|objective)", normalizar(t)) for t in intro):
                recomendadas.append({"seccion": "Objetivos", "detalle": "están dentro de la introducción; "
                                     "un apartado propio facilita comprobar si se cumplen"})
                continue
        nombre = " o ".join(NOMBRES.get(g, g) for g in grupo)
        (faltan if obligatoria else recomendadas).append({"seccion": nombre})
    orden = [c for c in presentes if c in ORDEN]
    desordenadas = [(a, b) for i, a in enumerate(orden) for b in orden[i + 1:] if ORDEN.index(a) > ORDEN.index(b)
                    and not {a, b} <= {"resultados", "discusion", "pruebas", "resultados_discusion"}]
    return {
        "titulos": [{"texto": b.texto, "nivel": b.nivel, "seccion": c} for b, c in mapa],
        "presentes": [NOMBRES.get(c, c) for c in presentes],
        "faltan": faltan,
        "recomendadas": recomendadas,
        "orden": [f"«{NOMBRES.get(a, a)}» aparece antes que «{NOMBRES.get(b, b)}»" for a, b in desordenadas[:3]],
    }


# --- Figuras y tablas -------------------------------------------------------------

def _numeros(lista: str) -> list[str]:
    salida = []
    for a, b in re.findall(r"(\d+(?:\.\d+)?)(?:\s*[-–]\s*(\d+))?", lista):
        if b and "." not in a and int(b) > int(a) and int(b) - int(a) < 30:
            salida += [str(i) for i in range(int(a), int(b) + 1)]
        else:
            salida.append(a)
    return salida


_LISTA = r"(\d+(?:\.\d+)?(?:\s*(?:,|y|e|and|eta|[-–])\s*\d+(?:\.\d+)?)*)"
RE_CITA_FIG = re.compile(r"\b(?:fig(?:ura)?s?|figures?|gr[aá]fic[oa]s?|esquemas?|diagramas?|imagen(?:es)?)\.?\s*"
                         + _LISTA, re.I)
RE_CITA_TAB = re.compile(r"\b(?:tablas?|tables?|cuadros?)\.?\s*" + _LISTA, re.I)
RE_CITA_EU = re.compile(r"\b(\d+)\.?\s*(irudi|taula|grafiko)\w*", re.I)


def citas_figuras(doc: Documento) -> dict[str, dict[str, list[str]]]:
    """{clase: {número: [secciones donde se cita]}}, sin contar las propias leyendas."""
    citas: dict[str, dict[str, list[str]]] = {"figura": {}, "tabla": {}}
    for b in doc.bloques:
        if b.tipo in ("leyenda", "titulo", "tabla", "codigo", "imagen"):
            continue
        for clase, patron in (("figura", RE_CITA_FIG), ("tabla", RE_CITA_TAB)):
            for m in patron.finditer(b.texto):
                for n in _numeros(m.group(1)):
                    citas[clase].setdefault(n, []).append(b.seccion)
        for m in RE_CITA_EU.finditer(b.texto):
            clase = "tabla" if m.group(2).lower().startswith("taula") else "figura"
            citas[clase].setdefault(m.group(1), []).append(b.seccion)
    return citas


def revisar_figuras(doc: Documento) -> dict:
    leyendas = [b for b in doc.bloques if b.tipo == "leyenda"]
    citas = citas_figuras(doc)
    avisos = []
    resumen = {}
    for clase in ("figura", "tabla"):
        propias = [b for b in leyendas if b.clase == clase]
        nombre = "Figura" if clase == "figura" else "Tabla"
        numeros = [b.numero for b in propias]
        # Numeración: sin repetidos ni saltos (solo numeración simple, no «2.1»).
        vistos = set()
        for n in numeros:
            if n in vistos:
                avisos.append({"tipo": "numeracion", "gravedad": "importante",
                               "detalle": f"{nombre} {n} está repetida", "seccion": ""})
            vistos.add(n)
        simples = sorted(int(n) for n in vistos if n.isdigit())
        if simples:
            faltan = [i for i in range(1, simples[-1] + 1) if i not in simples]
            if faltan:
                avisos.append({"tipo": "numeracion", "gravedad": "menor",
                               "detalle": f"la numeración de {nombre.lower()}s salta: falta"
                                          f"{'n' if len(faltan) > 1 else ''} {', '.join(map(str, faltan))}",
                               "seccion": ""})
            if [int(n) for n in numeros if n.isdigit()] != sorted(int(n) for n in numeros if n.isdigit()):
                avisos.append({"tipo": "numeracion", "gravedad": "menor",
                               "detalle": f"las {nombre.lower()}s no aparecen en orden numérico", "seccion": ""})
        for b in propias:
            resto = re.sub(r"^\W*\w+\.?\s*\d+(?:\.\d+)?\s*[.:\-–—|]?\s*", "", b.texto).strip()
            if len(resto.split()) < 3:
                avisos.append({"tipo": "leyenda_vacia", "gravedad": "menor", "seccion": b.seccion,
                               "detalle": f"{nombre} {b.numero} tiene una leyenda sin contenido («{b.texto}»): "
                                          "tiene que decir qué muestra"})
            if b.numero not in citas[clase]:
                avisos.append({"tipo": "sin_citar", "gravedad": "importante", "seccion": b.seccion,
                               "detalle": f"{nombre} {b.numero} no se cita en el texto", "leyenda": b.texto})
        for n, secciones in citas[clase].items():
            if n not in vistos and propias:
                avisos.append({"tipo": "cita_inexistente", "gravedad": "importante",
                               "seccion": secciones[0],
                               "detalle": f"el texto cita la {nombre} {n}, que no existe"})
            elif n not in vistos and not propias:
                avisos.append({"tipo": "cita_inexistente", "gravedad": "importante", "seccion": secciones[0],
                               "detalle": f"el texto cita la {nombre} {n}, pero no hay ninguna "
                                          f"leyenda «{nombre} {n}. …»"})
        resumen[clase] = {"leyendas": numeros, "citadas": sorted(citas[clase], key=lambda x: float(x))}
    imagenes = sum(1 for b in doc.bloques if b.tipo == "imagen")
    tablas = sum(1 for b in doc.bloques if b.tipo == "tabla")
    n_fig = sum(1 for b in leyendas if b.clase == "figura")
    n_tab = sum(1 for b in leyendas if b.clase == "tabla")
    if imagenes > n_fig:
        avisos.append({"tipo": "sin_leyenda", "gravedad": "importante", "seccion": "",
                       "detalle": f"hay {imagenes} imágenes y solo {n_fig} leyendas de figura: "
                                  f"{imagenes - n_fig} imagen(es) sin «Figura n. …»"})
    if tablas > n_tab:
        avisos.append({"tipo": "sin_leyenda", "gravedad": "importante", "seccion": "",
                       "detalle": f"hay {tablas} tablas y solo {n_tab} leyendas de tabla: "
                                  f"{tablas - n_tab} tabla(s) sin «Tabla n. …»"})
    resumen.update({"imagenes": imagenes, "tablas": tablas})
    return {"resumen": resumen, "avisos": avisos}


# --- Objetivos y pruebas --------------------------------------------------------------

def _raices(texto: str) -> set[str]:
    palabras = re.findall(r"[a-zñ]{5,}", normalizar(texto))
    return {p[:5] for p in palabras if p not in PALABRAS_VACIAS}


RE_CIFRA_UNIDAD = re.compile(r"\d+(?:[.,]\d+)?\s*(?:%|ms|s|min|h|mg|g|ml|l|m|mm|nm|°c|usuarios|peticiones)\b", re.I)


def revisar_objetivos(doc: Documento) -> list[dict]:
    secciones = bloques_por_seccion(doc)
    bloques = [b for b in secciones.get("objetivos", []) if b.tipo in ("lista", "parrafo")]
    if not bloques:
        return []
    items = [b for b in bloques if b.tipo == "lista"]
    if not items:  # objetivos en prosa: una frase por objetivo
        items = [Bloque("parrafo", f.strip(), seccion=b.seccion) for b in bloques
                 for f in re.split(r"(?<=[.;])\s+", b.texto) if len(f.split()) >= 5]
    despues = []
    for clave in ("resultados", "resultados_discusion", "pruebas", "discusion", "conclusiones"):
        despues += [b.texto if b.tipo != "tabla" else " ".join(" ".join(f) for f in b.filas)
                    for b in secciones.get(clave, [])]
    texto_despues = " ".join(despues)
    if not texto_despues.strip():
        return []
    raices_despues = _raices(texto_despues)
    norm_despues = normalizar(texto_despues)
    avisos = []
    for b in items:
        raices = _raices(b.texto)
        if len(raices) < 2:
            continue
        cubiertas = len(raices & raices_despues) / len(raices)
        cifras = [normalizar(c) for c in RE_CIFRA_UNIDAD.findall(b.texto)]
        cifras_ausentes = [c for c in cifras if c.replace(" ", "") not in norm_despues.replace(" ", "")]
        # Un objetivo con identificador («O3», «OE2», «Objetivo 1») que se nombra después cuenta como evaluado
        # si no tiene una cifra que falte.
        ident = re.match(r"^\s*((?:O[EG]?|H)\d+|objetivo\s+\d+)\b", b.texto, re.I)
        if ident and re.search(rf"(?<!\w){re.escape(normalizar(ident.group(1)))}(?!\w)", norm_despues) \
                and not cifras_ausentes:
            continue
        if cubiertas < 0.4 or cifras_ausentes:
            motivo = (f"la cifra objetivo ({', '.join(cifras_ausentes)}) no vuelve a aparecer"
                      if cifras_ausentes else f"solo {cubiertas:.0%} de sus términos aparecen después")
            avisos.append({"tipo": "objetivo_no_evaluado", "gravedad": "importante", "seccion": b.seccion,
                           "objetivo": b.texto,
                           "detalle": f"objetivo que no parece evaluarse en resultados, pruebas o conclusiones: {motivo}"})
    return avisos


RE_RESULTADO = re.compile(r"\d+\s*(?:%|/\s*\d+|de\s+\d+|of\s+\d+|ms\b|s\b|segundos|seconds)|\b\d+\s+(?:pruebas|tests|casos)"
                          r"\s+(?:superad|pasad|fallad|passed|failed|correct)|\b(?:passed|failed|superad[oa]s|fallad[oa]s)\b",
                          re.I)


def revisar_pruebas(doc: Documento, tipo: str) -> list[dict]:
    if tipo not in ("tecnico", "tfg"):
        return []
    bloques = bloques_por_seccion(doc).get("pruebas", [])
    if not bloques:
        return []
    if any(b.tipo == "tabla" for b in bloques):
        return []
    texto = " ".join(b.texto for b in bloques)
    if RE_RESULTADO.search(texto):
        return []
    return [{"tipo": "pruebas_sin_resultados", "gravedad": "importante", "seccion": bloques[0].seccion,
             "detalle": "la sección de pruebas describe qué se probó, pero no da resultados medibles "
                        "(casos superados/fallidos, tiempos, cobertura o una tabla)"}]


def revisar(ruta: str | Path, tipo: str) -> dict:
    doc = cargar(ruta)
    secciones = revisar_secciones(doc, tipo)
    figuras = revisar_figuras(doc)
    avisos = []
    for s in secciones["faltan"]:
        avisos.append({"tipo": "seccion_falta", "gravedad": "critico", "seccion": s["seccion"],
                       "detalle": f"falta la sección «{s['seccion']}»"})
    for s in secciones["recomendadas"]:
        avisos.append({"tipo": "seccion_recomendada", "gravedad": "menor", "seccion": s["seccion"],
                       "detalle": f"«{s['seccion']}»: " + s.get("detalle", "no aparece (recomendable en este tipo)")})
    for o in secciones["orden"]:
        avisos.append({"tipo": "orden", "gravedad": "menor", "seccion": "", "detalle": o})
    avisos += figuras["avisos"] + revisar_objetivos(doc) + revisar_pruebas(doc, tipo)
    return {"archivo": str(ruta), "tipo": tipo, "secciones": secciones, "figuras_tablas": figuras["resumen"],
            "avisos": avisos}


def informe(r: dict) -> str:
    s = r["secciones"]
    lineas = [f"Estructura ({r['tipo']}): {Path(r['archivo']).name}",
              f"Secciones presentes: {', '.join(s['presentes']) or 'ninguna reconocida'}"]
    ft = r["figuras_tablas"]
    lineas.append(f"Figuras: leyendas {', '.join(ft['figura']['leyendas']) or '—'}; citadas en el texto "
                  f"{', '.join(ft['figura']['citadas']) or '—'}; imágenes {ft['imagenes']}")
    lineas.append(f"Tablas: leyendas {', '.join(ft['tabla']['leyendas']) or '—'}; citadas en el texto "
                  f"{', '.join(ft['tabla']['citadas']) or '—'}; tablas {ft['tablas']}")
    if r["avisos"]:
        lineas.append(f"AVISOS ({len(r['avisos'])}):")
        for a in r["avisos"]:
            donde = f" [{a['seccion']}]" if a.get("seccion") else ""
            lineas.append(f"  - ({a['gravedad']}) {a['detalle']}{donde}")
            if a.get("objetivo"):
                lineas.append(f"      objetivo: «{a['objetivo']}»")
    else:
        lineas.append("AVISOS: ninguno")
    return "\n".join(lineas)


def main(argv: list[str]) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    p = argparse.ArgumentParser(description="Revisa la estructura de un trabajo.")
    p.add_argument("trabajo")
    p.add_argument("--tipo", required=True, choices=sorted(TIPOS))
    p.add_argument("--json", dest="salida_json")
    a = p.parse_args(argv[1:])
    r = revisar(a.trabajo, a.tipo)
    print(informe(r))
    if a.salida_json:
        Path(a.salida_json).write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    return 2 if r["avisos"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
