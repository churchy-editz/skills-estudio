#!/usr/bin/env python3
"""Extrae el texto de un trabajo con sus secciones, tablas y leyendas identificadas.

Uso:
    python extraer.py trabajo.docx|.pdf|.md|.tex|.txt [salida.md] [--json salida.json]

Salida en Markdown sencillo, un bloque por párrafo:
    ## 2. Resultados                  título (con su nivel)
    [Figura 1] Figura 1. Recta…        leyenda de figura (también [Tabla n])
    [imagen]                           imagen sin texto (DOCX y Markdown)
    | a | b |                          tabla
    texto ^{1,2}                       superíndices numéricos (citas Vancouver)
    <!-- p. 3 -->                      cambio de página (solo PDF)

Los demás scripts de la skill importan `cargar()` para trabajar con los mismos
bloques. DOCX necesita python-docx. PDF: usa pdftotext o pypdf si están
instalados y, si no, un lector mínimo de librería estándar que solo entiende
PDF con texto (no escaneados). Lo demás, solo librería estándar.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import unicodedata
import zlib
from dataclasses import asdict, dataclass, field
from pathlib import Path

# --- Modelo -----------------------------------------------------------------


@dataclass
class Bloque:
    tipo: str  # titulo | parrafo | lista | tabla | leyenda | imagen | codigo
    texto: str = ""
    nivel: int = 0  # solo títulos (1 = sección principal)
    filas: list[list[str]] = field(default_factory=list)  # solo tablas
    pagina: int | None = None
    clase: str = ""  # leyendas: figura | tabla
    numero: str = ""  # leyendas: número de figura o tabla
    seccion: str = ""  # título de la sección en la que está el bloque
    clave: str = ""  # entradas de bibliografía de LaTeX (\bibitem{clave})


@dataclass
class Documento:
    archivo: str
    formato: str
    bloques: list[Bloque]

    def texto(self, incluir_tablas: bool = True) -> str:
        partes = []
        for b in self.bloques:
            if b.tipo == "tabla":
                if incluir_tablas:
                    partes.extend(" | ".join(f) for f in b.filas)
            elif b.texto:
                partes.append(b.texto)
        return "\n".join(partes)

    def titulos(self) -> list[Bloque]:
        return [b for b in self.bloques if b.tipo == "titulo"]

    def a_dict(self) -> dict:
        return {"archivo": self.archivo, "formato": self.formato,
                "bloques": [{k: v for k, v in asdict(b).items() if v not in ("", [], None, 0) or k == "tipo"}
                            for b in self.bloques]}


# --- Utilidades de texto -----------------------------------------------------

def sin_tildes(texto: str) -> str:
    texto = unicodedata.normalize("NFD", texto)
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")


def normalizar(texto: str) -> str:
    """Minúsculas, sin tildes, comillas y espacios unificados (para comparar)."""
    texto = sin_tildes(texto.lower())
    texto = texto.replace("\u00a0", " ").replace("\u202f", " ")
    texto = re.sub(r"[“”«»„]", '"', texto)
    texto = re.sub(r"[‘’‚]", "'", texto)
    return re.sub(r"\s+", " ", texto).strip()


_FIG = r"figura|fig\.?|figure|gr[aá]fic[oa]|imagen|esquema|diagrama|ilustraci[oó]n"
_TAB = r"tabla|table|cuadro"
RE_LEYENDA = re.compile(rf"^\s*(?:\*\*)?(?P<tipo>{_FIG}|{_TAB})\s*(?P<num>\d+(?:\.\d+)?)\s*(?:\*\*)?\s*[.:\-–—|]", re.I)
RE_LEYENDA_EU = re.compile(r"^\s*(?P<num>\d+(?:\.\d+)?)\.?\s*(?P<tipo>irudia|taula|grafikoa)\b", re.I)


def detectar_leyenda(texto: str) -> tuple[str, str] | None:
    """('figura'|'tabla', número) si el párrafo es una leyenda («Figura 2. …»)."""
    if len(texto) > 600:
        return None
    m = RE_LEYENDA.match(texto) or RE_LEYENDA_EU.match(texto)
    if not m:
        return None
    tipo = m.group("tipo").lower()
    clase = "tabla" if re.match(rf"(?:{_TAB}|taula)$", tipo, re.I) else "figura"
    return clase, m.group("num")


RE_TITULO_NUMERADO = re.compile(r"^(?P<num>\d+(?:\.\d+){0,3})\.?\s+(?P<resto>[A-ZÁÉÍÓÚÑÜ¿¡].*)$")
RE_ANEXO = re.compile(r"^(anexo|ap[eé]ndice|appendix|eranskina)\b", re.I)


def parece_titulo(texto: str, negrita: bool = False) -> int | None:
    """Nivel si una línea suelta parece un título hecho a mano; si no, None."""
    texto = texto.strip()
    palabras = texto.split()
    if not texto or len(palabras) > 12 or texto.endswith((".", ",", ";", ":")) or detectar_leyenda(texto):
        return None
    m = RE_TITULO_NUMERADO.match(texto)
    if m and len(palabras) <= 10:
        return m.group("num").count(".") + 1
    if RE_ANEXO.match(texto) and len(palabras) <= 8:
        return 1
    if negrita and len(palabras) <= 8:
        return 1
    letras = [c for c in texto if c.isalpha()]
    if len(letras) >= 4 and all(c.isupper() for c in letras) and len(palabras) <= 6:
        return 1
    return None


def asignar_secciones(bloques: list[Bloque]) -> list[Bloque]:
    pila: list[tuple[int, str]] = []
    for b in bloques:
        if b.tipo == "titulo":
            while pila and pila[-1][0] >= b.nivel:
                pila.pop()
            pila.append((b.nivel, b.texto))
            b.seccion = b.texto
        else:
            b.seccion = pila[-1][1] if pila else ""
    return bloques


def marcar_leyendas(bloques: list[Bloque]) -> list[Bloque]:
    for b in bloques:
        if b.tipo in ("parrafo", "lista"):
            ley = detectar_leyenda(b.texto)
            if ley:
                b.tipo, (b.clase, b.numero) = "leyenda", ley
    return bloques


# --- DOCX --------------------------------------------------------------------

def _texto_run_docx(r, qn) -> str:
    partes = []
    for hijo in r:
        if hijo.tag == qn("w:t"):
            partes.append(hijo.text or "")
        elif hijo.tag == qn("w:tab"):
            partes.append("\t")
        elif hijo.tag in (qn("w:br"), qn("w:cr")):
            partes.append("\n")
    texto = "".join(partes)
    rpr = r.find(qn("w:rPr"))
    if rpr is not None and texto.strip():
        va = rpr.find(qn("w:vertAlign"))
        if va is not None and va.get(qn("w:val")) == "superscript" and re.fullmatch(r"[\d,\s–\-]+", texto):
            return "^{" + texto.strip() + "}"
    return texto


def _es_negrita(r, qn) -> bool:
    rpr = r.find(qn("w:rPr"))
    if rpr is None:
        return False
    b = rpr.find(qn("w:b"))
    return b is not None and b.get(qn("w:val")) not in ("0", "false")


def _parrafo_docx(p, qn) -> tuple[str, bool, bool]:
    """(texto, todo en negrita, tiene imagen)."""
    runs = p.xpath("./w:r | ./w:hyperlink/w:r | ./w:ins/w:r | ./w:smartTag/w:r")
    texto, negritas, imagen = [], [], False
    for r in runs:
        t = _texto_run_docx(r, qn)
        if t.startswith("^{"):
            # Superíndice detrás de una variable o unidad corta (R², cm⁻¹): es un exponente.
            antes = "".join(texto)
            if re.fullmatch(r"-?\d", t[2:-1].strip()) and re.search(EXPONENTE + r"\s*$", antes):
                t = t[2:-1].strip().translate(SUPER)
        if r.xpath(".//w:drawing | .//w:pict"):
            imagen = True
        if t.strip():
            negritas.append(_es_negrita(r, qn))
        texto.append(t)
    return "".join(texto), bool(negritas) and all(negritas), imagen


def _nivel_estilo(nombre: str) -> int | None:
    nombre = sin_tildes(nombre.lower())
    if nombre in {"title", "titulo"}:
        return 0
    m = re.match(r"(?:heading|titulo|encabezado)\s*(\d)", nombre)
    return int(m.group(1)) if m else None


def cargar_docx(ruta: Path) -> list[Bloque]:
    try:
        from docx import Document
        from docx.oxml.ns import qn
    except ImportError:
        sys.exit(f'Falta python-docx. Instálalo con:\n    "{sys.executable}" -m pip install python-docx')
    doc = Document(str(ruta))
    estilos = {s.style_id: s.name for s in doc.styles}
    bloques: list[Bloque] = []
    for hijo in doc.element.body.iterchildren():
        if hijo.tag == qn("w:p"):
            texto, negrita, imagen = _parrafo_docx(hijo, qn)
            ppr = hijo.find(qn("w:pPr"))
            estilo_id = ""
            lista = False
            if ppr is not None:
                ps = ppr.find(qn("w:pStyle"))
                estilo_id = ps.get(qn("w:val")) if ps is not None else ""
                lista = ppr.find(qn("w:numPr")) is not None
            estilo = estilos.get(estilo_id, estilo_id)
            if imagen:
                bloques.append(Bloque("imagen"))
            texto = texto.strip()
            if not texto:
                continue
            nivel = _nivel_estilo(estilo)
            if nivel is not None:
                bloques.append(Bloque("titulo", texto, nivel=max(nivel, 1) if nivel else 0))
            elif lista or "list" in estilo.lower() or "lista" in estilo.lower():
                bloques.append(Bloque("lista", texto))
            else:
                n = parece_titulo(texto, negrita)
                bloques.append(Bloque("titulo", texto, nivel=n) if n else Bloque("parrafo", texto))
        elif hijo.tag == qn("w:tbl"):
            filas = []
            for tr in hijo.iter(qn("w:tr")):
                celdas = []
                for tc in tr.iter(qn("w:tc")):
                    celdas.append(" ".join(_parrafo_docx(p, qn)[0].strip() for p in tc.iter(qn("w:p"))).strip())
                filas.append(celdas)
            bloques.append(Bloque("tabla", filas=filas))
    return bloques


# --- Markdown y texto plano ---------------------------------------------------

def _limpiar_md(texto: str) -> str:
    texto = re.sub(r"<sup>\s*([\d,\s–-]+)\s*</sup>", r"^{\1}", texto)
    texto = re.sub(r"\^([\d,–-]+)\^", r"^{\1}", texto)
    texto = re.sub(r"(\*\*|__)(.+?)\1", r"\2", texto)
    texto = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?!\w)", r"\1", texto)
    texto = re.sub(r"\[([^\]]+)\]\((?:[^)]+)\)", r"\1", texto)
    texto = re.sub(EXPONENTE.replace("(?:", "(", 1) + r"\^\{(-?\d)\}", lambda m: m.group(1) + m.group(2).translate(SUPER), texto)
    return texto.strip()


def _fila_tabla(linea: str) -> list[str] | None:
    linea = linea.strip()
    if linea.count("|") >= 2 and linea.startswith("|"):
        celdas = [c.strip() for c in linea.strip("|").split("|")]
        if all(re.fullmatch(r":?-{2,}:?", c) for c in celdas if c):
            return []
        return celdas
    return None


def cargar_md(texto: str, markdown: bool = True) -> list[Bloque]:
    bloques: list[Bloque] = []
    lineas = texto.replace("\r\n", "\n").split("\n")
    parrafo: list[str] = []
    tabla: list[list[str]] = []
    pagina: int | None = None
    en_codigo = False
    codigo: list[str] = []

    def cerrar_parrafo():
        if parrafo:
            t = _limpiar_md(" ".join(s.strip() for s in parrafo)) if markdown else " ".join(s.strip() for s in parrafo)
            if t:
                n = None if markdown else parece_titulo(t)
                bloques.append(Bloque("titulo", t, nivel=n, pagina=pagina) if n else Bloque("parrafo", t, pagina=pagina))
            parrafo.clear()

    def cerrar_tabla():
        if tabla:
            bloques.append(Bloque("tabla", filas=[f for f in tabla if f], pagina=pagina))
            tabla.clear()

    for linea in lineas:
        if "\f" in linea:
            cerrar_parrafo(); cerrar_tabla()
            pagina = (pagina or 1) + linea.count("\f")
            linea = linea.replace("\f", "")
        m_pag = re.match(r"^\s*<!--\s*p\.\s*(\d+)\s*-->\s*$", linea)
        if m_pag:
            cerrar_parrafo(); cerrar_tabla()
            pagina = int(m_pag.group(1))
            continue
        if markdown and linea.strip().startswith("```"):
            cerrar_parrafo(); cerrar_tabla()
            if en_codigo:
                bloques.append(Bloque("codigo", "\n".join(codigo), pagina=pagina))
                codigo.clear()
            en_codigo = not en_codigo
            continue
        if en_codigo:
            codigo.append(linea)
            continue
        fila = _fila_tabla(linea) if markdown else None
        if fila is None and not markdown and "\t" in linea.strip():
            fila = [c.strip() for c in linea.strip().split("\t")]
        if fila is not None:
            cerrar_parrafo()
            tabla.append(fila)
            continue
        cerrar_tabla()
        s = linea.strip()
        if not s:
            cerrar_parrafo()
            continue
        if markdown:
            m = re.match(r"^(#{1,6})\s+(.*?)\s*#*$", s)
            if m:
                cerrar_parrafo()
                bloques.append(Bloque("titulo", _limpiar_md(m.group(2)), nivel=len(m.group(1)), pagina=pagina))
                continue
            m = re.match(r"^!\[([^\]]*)\]\([^)]*\)$", s)
            if m:
                cerrar_parrafo()
                bloques.append(Bloque("imagen", m.group(1), pagina=pagina))
                continue
            m = re.match(r"^(?:[-*+]|\d+[.)])\s+(.*)$", s)
            if m and not detectar_leyenda(s):
                cerrar_parrafo()
                bloques.append(Bloque("lista", _limpiar_md(m.group(1)), pagina=pagina))
                continue
        elif parece_titulo(s) and not parrafo:
            bloques.append(Bloque("titulo", s, nivel=parece_titulo(s), pagina=pagina))
            continue
        parrafo.append(s)
    cerrar_parrafo(); cerrar_tabla()
    if en_codigo and codigo:
        bloques.append(Bloque("codigo", "\n".join(codigo), pagina=pagina))
    # Markdown: si hay un solo «#» (el título del trabajo), las secciones son «##».
    if markdown:
        niveles = [b.nivel for b in bloques if b.tipo == "titulo"]
        if niveles.count(1) == 1 and min(niveles, default=1) == 1 and len(niveles) > 1:
            for b in bloques:
                if b.tipo == "titulo":
                    b.nivel = 0 if b.nivel == 1 else b.nivel - 1
    return bloques


# --- LaTeX --------------------------------------------------------------------

UNIDADES_SIUNITX = {
    "litre": "L", "liter": "L", "gram": "g", "metre": "m", "meter": "m", "second": "s", "minute": "min",
    "hour": "h", "mole": "mol", "molar": "M", "kelvin": "K", "degreeCelsius": "°C", "percent": "%",
    "milli": "m", "micro": "µ", "nano": "n", "kilo": "k", "centi": "c", "pascal": "Pa", "joule": "J",
    "volt": "V", "ampere": "A", "hertz": "Hz", "watt": "W", "per": "/", "byte": "B", "dalton": "Da",
}


def _unidad_siunitx(u: str) -> str:
    if "\\" not in u:
        return u
    salida = ""
    for nombre in re.findall(r"\\(\w+)", u):
        salida += UNIDADES_SIUNITX.get(nombre, nombre)
    return salida


def _argumento(texto: str, inicio: int) -> tuple[str, int]:
    """Contenido entre llaves que empiezan en texto[inicio] == '{'."""
    nivel, i = 0, inicio
    while i < len(texto):
        if texto[i] == "{" and (i == 0 or texto[i - 1] != "\\"):
            nivel += 1
        elif texto[i] == "}" and texto[i - 1] != "\\":
            nivel -= 1
            if nivel == 0:
                return texto[inicio + 1:i], i + 1
        i += 1
    return texto[inicio + 1:], len(texto)


# Base de un exponente (R², cm⁻¹, x³): una letra suelta o una unidad de longitud. Una palabra
# como «más» seguida de un superíndice es una cita, no un exponente.
EXPONENTE = r"(?<![^\W\d_])(?:[A-Za-z]|[cmnkdµ]m|µ?[mk]?s)"
SUPER = str.maketrans("0123456789-+", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺")


def exponentes(t: str) -> str:
    """R^2 → R², cm^{-1} → cm⁻¹ (exponentes, no citas)."""
    return re.sub(r"\^\{?(-?\d{1,2})\}?", lambda m: m.group(1).translate(SUPER), t)


def _limpiar_tex(t: str, etiquetas: dict[str, tuple[str, str]]) -> str:
    def ref(m):
        clase, num = etiquetas.get(m.group(1), ("", "?"))
        antes = t[max(0, m.start() - 14):m.start()].lower()
        if re.search(r"(fig\w*|tabla|table|cuadro)[\s~.]*$", antes) or not clase:
            return num
        return ("Figura " if clase == "figura" else "Tabla ") + num

    t = re.sub(r"\\(?:auto|c|eq|page)?ref\{([^}]*)\}", ref, t)
    t = re.sub(r"\\SI\{([^}]*)\}\{([^}]*)\}", lambda m: f"{m.group(1)} {_unidad_siunitx(m.group(2))}", t)
    t = re.sub(r"\\(?:num)\{([^}]*)\}", r"\1", t)
    t = re.sub(r"\\(?:si|unit)\{([^}]*)\}", lambda m: _unidad_siunitx(m.group(1)), t)
    t = re.sub(r"\\(?:cite[tp]?|parencite|textcite|autocite)\*?(?:\[[^\]]*\])*\{([^}]*)\}", r"\\cite{\1}", t)
    t = re.sub(r"\\textsuperscript\{([\d,\s–-]+)\}", r"^{\1}", t)
    t = re.sub(r"\\(?:textbf|textit|emph|underline|texttt|textrm|mathrm|text|mbox)\{([^{}]*)\}", r"\1", t)
    t = re.sub(r"\\(?:label|index|footnote)\{[^{}]*\}", "", t)
    t = t.replace("~", " ").replace("\\%", "%").replace("\\&", "&").replace("\\_", "_")
    t = t.replace("``", "“").replace("''", "”").replace("---", "—").replace("--", "–")
    t = re.sub(r"\$([^$]*)\$", lambda m: exponentes(m.group(1)), t)
    t = re.sub(r"\\(?:,|;|:|!| )", " ", t)
    citas = []
    t = re.sub(r"\\cite\{([^}]*)\}", lambda m: citas.append(m.group(1)) or f"\x00{len(citas) - 1}\x00", t)
    t = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?", "", t)
    t = t.replace("{", "").replace("}", "")
    t = re.sub(r"\^([\d,–-]+)", r"^{\1}", t)
    t = re.sub(r"\x00(\d+)\x00", lambda m: "\\cite{" + citas[int(m.group(1))] + "}", t)
    return re.sub(r"\s+", " ", t).strip()


def _leer_bib(ruta: Path) -> list[Bloque]:
    if not ruta.is_file():
        return []
    texto = ruta.read_text(encoding="utf-8", errors="replace")
    salida = []
    for m in re.finditer(r"@\w+\s*\{\s*([^,\s]+)\s*,(.*?)\n\}", texto, re.S):
        campos = dict((k.lower(), re.sub(r"[{}\s]+", " ", v).strip())
                      for k, v in re.findall(r"(\w+)\s*=\s*[{\"](.*?)[}\"]\s*,?\s*\n", m.group(2) + "\n", re.S))
        texto_e = f"{campos.get('author', '?')} ({campos.get('year', 's. f.')}). {campos.get('title', '')}."
        salida.append(Bloque("lista", texto_e, clave=m.group(1)))
    return salida


def cargar_tex(texto: str, carpeta: Path) -> list[Bloque]:
    texto = re.sub(r"(?<!\\)%.*", "", texto)
    m = re.search(r"\\begin\{document\}(.*?)(\\end\{document\}|$)", texto, re.S)
    cuerpo = m.group(1) if m else texto
    # Numeración de figuras y tablas, como la hace LaTeX.
    etiquetas: dict[str, tuple[str, str]] = {}
    contadores = {"figura": 0, "tabla": 0}
    for entorno in re.finditer(r"\\begin\{(figure|table)\*?\}(.*?)\\end\{\1\*?\}", cuerpo, re.S):
        clase = "figura" if entorno.group(1) == "figure" else "tabla"
        contadores[clase] += 1
        for lbl in re.findall(r"\\label\{([^}]*)\}", entorno.group(2)):
            etiquetas[lbl] = (clase, str(contadores[clase]))
    bloques: list[Bloque] = []
    titulo = re.search(r"\\title\{", texto)
    if titulo:
        bloques.append(Bloque("titulo", _limpiar_tex(_argumento(texto, titulo.end() - 1)[0], etiquetas), nivel=0))
    contadores = {"figura": 0, "tabla": 0}
    patron = re.compile(r"\\(chapter|section|subsection|subsubsection|paragraph)\*?\s*(?:\[[^\]]*\])?\{"
                        r"|\\begin\{(figure|table|itemize|enumerate|thebibliography|abstract|lstlisting|verbatim|minted)\*?\}"
                        r"|\n\s*\n")
    pos = 0
    niveles = {"chapter": 1, "section": 1, "subsection": 2, "subsubsection": 3, "paragraph": 4}
    if "\\chapter" in cuerpo:
        niveles = {"chapter": 1, "section": 2, "subsection": 3, "subsubsection": 4, "paragraph": 5}

    def parrafo(trozo: str):
        t = _limpiar_tex(trozo, etiquetas)
        if t:
            bloques.append(Bloque("parrafo", t))

    while True:
        m = patron.search(cuerpo, pos)
        if not m:
            parrafo(cuerpo[pos:])
            break
        parrafo(cuerpo[pos:m.start()])
        if m.group(1):
            arg, pos = _argumento(cuerpo, m.end() - 1)
            bloques.append(Bloque("titulo", _limpiar_tex(arg, etiquetas), nivel=niveles[m.group(1)]))
            continue
        if not m.group(2):
            pos = m.end()
            continue
        entorno = m.group(2)
        fin = re.search(rf"\\end\{{{entorno}\*?\}}", cuerpo[m.end():])
        dentro = cuerpo[m.end():m.end() + fin.start()] if fin else cuerpo[m.end():]
        pos = m.end() + (fin.end() if fin else len(dentro))
        if entorno in ("figure", "table"):
            clase = "figura" if entorno == "figure" else "tabla"
            contadores[clase] += 1
            if clase == "figura" and re.search(r"\\includegraphics|\\begin\{tikzpicture\}", dentro):
                bloques.append(Bloque("imagen"))
            tab = re.search(r"\\begin\{tabular\*?\}(?:\{[^}]*\})+(.*?)\\end\{tabular\*?\}", dentro, re.S)
            cap = re.search(r"\\caption(?:\[[^\]]*\])?\{", dentro)
            leyenda = None
            if cap:
                arg = _argumento(dentro, cap.end() - 1)[0]
                nombre = "Figura" if clase == "figura" else "Tabla"
                leyenda = Bloque("leyenda", f"{nombre} {contadores[clase]}. {_limpiar_tex(arg, etiquetas)}",
                                 clase=clase, numero=str(contadores[clase]))
            if leyenda and clase == "tabla":
                bloques.append(leyenda)
            if tab:
                filas = []
                for fila in re.split(r"\\\\", tab.group(1)):
                    fila = re.sub(r"\\(?:hline|toprule|midrule|bottomrule|cline\{[^}]*\})", "", fila).strip()
                    if fila:
                        filas.append([_limpiar_tex(c, etiquetas) for c in fila.split("&")])
                bloques.append(Bloque("tabla", filas=filas))
            if leyenda and clase == "figura":
                bloques.append(leyenda)
        elif entorno in ("itemize", "enumerate"):
            for item in re.split(r"\\item\b", dentro)[1:]:
                t = _limpiar_tex(item, etiquetas)
                if t:
                    bloques.append(Bloque("lista", t))
        elif entorno == "thebibliography":
            bloques.append(Bloque("titulo", "Bibliografía", nivel=1))
            for item in re.finditer(r"\\bibitem(?:\[[^\]]*\])?\{([^}]*)\}(.*?)(?=\\bibitem|$)", dentro, re.S):
                bloques.append(Bloque("lista", _limpiar_tex(item.group(2), etiquetas), clave=item.group(1)))
        elif entorno == "abstract":
            bloques.append(Bloque("titulo", "Resumen", nivel=1))
            parrafo(dentro)
        else:
            bloques.append(Bloque("codigo", dentro.strip("\n")))
    bib = re.search(r"\\(?:bibliography|addbibresource)\{([^}]*)\}", texto)
    if bib and not any(b.clave for b in bloques):
        entradas = []
        for nombre in bib.group(1).split(","):
            nombre = nombre.strip()
            entradas += _leer_bib(carpeta / (nombre if nombre.endswith(".bib") else nombre + ".bib"))
        if entradas:
            bloques.append(Bloque("titulo", "Bibliografía", nivel=1))
            bloques += entradas
    return bloques


# --- PDF ------------------------------------------------------------------------

def _pdf_minimo(datos: bytes) -> str:
    """Lector mínimo: flujos FlateDecode, operadores Tj/TJ y mapas ToUnicode.

    Sirve para PDF sencillos con texto. Los escaneados no tienen texto: hay que
    transcribirlos antes.
    """
    objetos = {}
    for m in re.finditer(rb"(\d+)\s+(\d+)\s+obj(.*?)endobj", datos, re.S):
        objetos[int(m.group(1))] = m.group(3)

    def flujo(cuerpo: bytes) -> bytes | None:
        m = re.search(rb"stream\r?\n(.*?)\r?\nendstream", cuerpo, re.S)
        if not m:
            return None
        crudo = m.group(1)
        if b"FlateDecode" in cuerpo[:m.start()]:
            try:
                return zlib.decompress(crudo)
            except zlib.error:
                try:
                    return zlib.decompressobj().decompress(crudo)
                except zlib.error:
                    return None
        return crudo

    def mapa_unicode(cmap: bytes) -> dict[int, str]:
        mapa = {}
        for bloque in re.findall(rb"beginbfchar(.*?)endbfchar", cmap, re.S):
            for a, b in re.findall(rb"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", bloque):
                mapa[int(a, 16)] = bytes.fromhex(b.decode()).decode("utf-16-be", "replace")
        for bloque in re.findall(rb"beginbfrange(.*?)endbfrange", cmap, re.S):
            for a, b, c in re.findall(rb"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", bloque):
                ini = int(c, 16)
                for i, cod in enumerate(range(int(a, 16), int(b, 16) + 1)):
                    mapa[cod] = chr(ini + i)
        return mapa

    # Fuentes con ToUnicode, por nombre de recurso (/F1…)
    fuentes: dict[bytes, dict[int, str]] = {}
    for num, cuerpo in objetos.items():
        m = re.search(rb"/ToUnicode\s+(\d+)\s+0\s+R", cuerpo)
        if m and int(m.group(1)) in objetos:
            datos_cmap = flujo(objetos[int(m.group(1))]) or b""
            for nombre, ref in re.findall(rb"/(\w+)\s+(\d+)\s+0\s+R", b" ".join(objetos.values())):
                if int(ref) == num:
                    fuentes[nombre] = mapa_unicode(datos_cmap)

    def cadena(lit: bytes) -> bytes:
        lit = re.sub(rb"\\([nrtbf()\\])", lambda m: {b"n": b"\n", b"r": b"\r", b"t": b"\t", b"b": b"\b",
                                                      b"f": b"\f"}.get(m.group(1), m.group(1)), lit)
        return re.sub(rb"\\([0-7]{1,3})", lambda m: bytes([int(m.group(1), 8) & 255]), lit)

    def decodificar(crudo: bytes, mapa: dict[int, str] | None) -> str:
        if mapa:
            ancho = 2 if max(mapa, default=0) > 255 else 1
            return "".join(mapa.get(int.from_bytes(crudo[i:i + ancho], "big"), "")
                           for i in range(0, len(crudo) - ancho + 1, ancho))
        return crudo.decode("cp1252", "replace")

    paginas = []
    tokens = re.compile(rb"\((?:\\.|[^\\)])*\)|<[0-9A-Fa-f\s]*>|\[|\]|/\w+|-?\d*\.?\d+|[A-Za-z'\"*]+")
    for num in sorted(objetos):
        cuerpo = objetos[num]
        if not re.search(rb"/Type\s*/Page\b", cuerpo):
            continue
        refs = re.search(rb"/Contents\s*(\[[^\]]*\]|\d+\s+0\s+R)", cuerpo)
        if not refs:
            continue
        contenido = b"".join(flujo(objetos.get(int(r), b"")) or b"" for r in re.findall(rb"(\d+)\s+0\s+R", refs.group(1)))
        texto, fuente, pila = [], None, []
        for tok in tokens.findall(contenido):
            if tok.startswith(b"(") or tok.startswith(b"<") or tok in (b"[", b"]") or re.fullmatch(rb"/\w+|-?\d*\.?\d+", tok):
                pila.append(tok)
                continue
            if tok == b"Tf":
                nombres = [t for t in pila if t.startswith(b"/")]
                fuente = fuentes.get(nombres[-1][1:]) if nombres else None
            elif tok in (b"Tj", b"TJ", b"'", b'"'):
                if tok in (b"'", b'"'):
                    texto.append("\n")
                for t in pila:
                    if t.startswith(b"("):
                        texto.append(decodificar(cadena(t[1:-1]), fuente))
                    elif t.startswith(b"<"):
                        texto.append(decodificar(bytes.fromhex(re.sub(rb"\s", b"", t[1:-1]).decode() or ""), fuente))
                    elif re.fullmatch(rb"-?\d*\.?\d+", t) and float(t) < -200:
                        texto.append(" ")
            elif tok in (b"Td", b"TD", b"T*", b"Tm"):
                nums = [float(t) for t in pila if re.fullmatch(rb"-?\d*\.?\d+", t)]
                if tok == b"T*" or (len(nums) >= 2 and abs(nums[-1]) > 1e-6 and tok != b"Tm"):
                    texto.append("\n")
                elif tok == b"Tm":
                    texto.append("\n")
            pila = []
        paginas.append(re.sub(r"\n{2,}", "\n", "".join(texto)))
    return "\f".join(paginas)


def texto_pdf(ruta: Path) -> str:
    if shutil.which("pdftotext"):
        r = subprocess.run(["pdftotext", "-enc", "UTF-8", str(ruta), "-"], capture_output=True)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.decode("utf-8", "replace")
    try:
        from pypdf import PdfReader  # opcional
        return "\f".join((p.extract_text() or "") for p in PdfReader(str(ruta)).pages)
    except ImportError:
        pass
    return _pdf_minimo(ruta.read_bytes())


def cargar_pdf(ruta: Path) -> list[Bloque]:
    texto = texto_pdf(ruta)
    if not texto.strip():
        sys.exit("El PDF no tiene texto extraíble (¿escaneado?). Transcríbelo y pásalo como .txt o .md.")
    # Une líneas partidas del mismo párrafo: pdftotext deja una línea por renglón.
    salida = []
    for pagina in texto.split("\f"):
        lineas = [l.rstrip() for l in pagina.split("\n")]
        salida.append("\n".join(lineas))
    bloques = cargar_md("\f".join(salida), markdown=False)
    if bloques and bloques[0].pagina is None:
        for b in bloques:
            b.pagina = b.pagina or 1
    return bloques


# --- Entrada principal --------------------------------------------------------

def cargar(ruta: str | Path) -> Documento:
    ruta = Path(ruta)
    ext = ruta.suffix.lower()
    if ext == ".docx":
        bloques, formato = cargar_docx(ruta), "docx"
    elif ext == ".pdf":
        bloques, formato = cargar_pdf(ruta), "pdf"
    elif ext in (".tex", ".latex"):
        bloques, formato = cargar_tex(ruta.read_text(encoding="utf-8", errors="replace"), ruta.parent), "tex"
    elif ext in (".md", ".markdown"):
        bloques, formato = cargar_md(ruta.read_text(encoding="utf-8", errors="replace")), "md"
    else:
        bloques, formato = cargar_md(ruta.read_text(encoding="utf-8", errors="replace"), markdown=False), "txt"
    return Documento(str(ruta), formato, asignar_secciones(marcar_leyendas(bloques)))


def a_markdown(doc: Documento) -> str:
    partes, pagina = [], None
    for b in doc.bloques:
        if b.pagina and b.pagina != pagina and doc.formato == "pdf":
            pagina = b.pagina
            partes.append(f"<!-- p. {pagina} -->")
        if b.tipo == "titulo":
            partes.append("#" * (b.nivel + 1) + " " + b.texto)
        elif b.tipo == "leyenda":
            partes.append(f"[{b.clase.capitalize()} {b.numero}] {b.texto}")
        elif b.tipo == "imagen":
            partes.append(f"[imagen{': ' + b.texto if b.texto else ''}]")
        elif b.tipo == "lista":
            partes.append(f"- {'[' + b.clave + '] ' if b.clave else ''}{b.texto}")
        elif b.tipo == "tabla":
            if b.filas:
                ancho = max(len(f) for f in b.filas)
                filas = [f + [""] * (ancho - len(f)) for f in b.filas]
                partes.append("\n".join(["| " + " | ".join(filas[0]) + " |", "|" + "---|" * ancho]
                                        + ["| " + " | ".join(f) + " |" for f in filas[1:]]))
        elif b.tipo == "codigo":
            partes.append("```\n" + b.texto + "\n```")
        else:
            partes.append(b.texto)
    return "\n\n".join(partes) + "\n"


def contar_palabras(doc: Documento) -> int:
    return len(re.findall(r"\w+", doc.texto(incluir_tablas=False)))


def main(argv: list[str]) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    args = [a for a in argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 1
    salida_json = None
    if "--json" in argv:
        i = argv.index("--json")
        salida_json = argv[i + 1] if i + 1 < len(argv) else None
        if salida_json in args:
            args.remove(salida_json)
    doc = cargar(args[0])
    md = a_markdown(doc)
    if len(args) > 1:
        Path(args[1]).write_text(md, encoding="utf-8")
        figuras = sum(1 for b in doc.bloques if b.tipo == "leyenda" and b.clase == "figura")
        tablas = sum(1 for b in doc.bloques if b.tipo == "tabla")
        print(f"{args[1]}: {contar_palabras(doc)} palabras, {len(doc.titulos())} títulos, "
              f"{tablas} tablas, {figuras} leyendas de figura")
    else:
        print(md)
    if salida_json:
        Path(salida_json).write_text(json.dumps(doc.a_dict(), ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
