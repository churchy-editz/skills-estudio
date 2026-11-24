#!/usr/bin/env python3
"""Convierte los apuntes HTML de creador-apuntes a un .docx equivalente.

Uso:
    python html_a_docx.py entrada.html salida.docx

Única dependencia: python-docx.

Reconoce el HTML de assets/plantilla-base.html:
  - h1-h3 -> estilos de título de Word (Título 1, 2, 3)
  - p, ul, ol, table, blockquote, strong/em/code/br
  - .caja.def/.ejemplo/.ojo/.clave -> tabla de una celda con fondo y etiqueta
  - .leyenda -> fila de etiquetas de color
  - ol.pasos / ol.cadena -> lista numerada (reinicia en 1)
  - ol.linea-tiempo -> tabla Fecha | Hecho
  - ul.arbol -> lista con viñetas anidada
  - .cornell -> tabla de dos columnas con fila de síntesis
Los colores se leen de las variables CSS del :root (--fondo, --texto, --def,
--ejemplo, --ojo, --clave). Cualquier otro elemento se convierte en texto
normal, sin perder contenido.
"""
from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path

try:
    from docx import Document
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Cm, Pt, RGBColor
except ImportError:
    print(
        "Falta la librería python-docx. Instálala con:\n"
        f'    "{sys.executable}" -m pip install python-docx',
        file=sys.stderr,
    )
    sys.exit(1)


# --------------------------------------------------------------------------
# Árbol HTML mínimo
# --------------------------------------------------------------------------

VACIOS = {"br", "hr", "img", "meta", "link", "input", "col", "wbr", "source", "area", "base"}
IGNORAR = {"head", "script", "style", "title", "template", "noscript"}
INLINE = {
    "a", "abbr", "b", "strong", "i", "em", "u", "span", "code", "small", "sub", "sup",
    "mark", "q", "cite", "time", "br", "s", "kbd", "var", "dfn",
}
TIPOS_CAJA = ("def", "ejemplo", "ojo", "clave")
ETIQUETAS = {"def": "Definición", "ejemplo": "Ejemplo", "ojo": "Ojo", "clave": "Dato clave"}
PALETA_NEUTRA = {
    "fondo": "FFFFFF", "texto": "1F1F1F", "def": "1F5F8B",
    "ejemplo": "2E6B30", "ojo": "A3261B", "clave": "7A4B00",
}


class Nodo:
    def __init__(self, tag: str, attrs: dict | None = None, padre: "Nodo | None" = None):
        self.tag = tag
        self.attrs = attrs or {}
        self.padre = padre
        self.hijos: list = []  # Nodo o str

    @property
    def clases(self) -> set[str]:
        return set((self.attrs.get("class") or "").split())

    def elementos(self) -> list["Nodo"]:
        return [h for h in self.hijos if isinstance(h, Nodo)]

    def texto(self) -> str:
        partes = []
        for h in self.hijos:
            partes.append(h if isinstance(h, str) else h.texto())
        return re.sub(r"\s+", " ", "".join(partes)).strip()

    def buscar(self, pred) -> "Nodo | None":
        for h in self.elementos():
            if pred(h):
                return h
            encontrado = h.buscar(pred)
            if encontrado is not None:
                return encontrado
        return None


class _Constructor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.raiz = Nodo("#raiz")
        self.actual = self.raiz
        self.css: list[str] = []
        self.titulo = ""

    def handle_starttag(self, tag, attrs):
        nodo = Nodo(tag, {k: (v or "") for k, v in attrs}, self.actual)
        self.actual.hijos.append(nodo)
        if tag not in VACIOS:
            self.actual = nodo

    def handle_startendtag(self, tag, attrs):
        self.actual.hijos.append(Nodo(tag, {k: (v or "") for k, v in attrs}, self.actual))

    def handle_endtag(self, tag):
        nodo = self.actual
        while nodo is not self.raiz and nodo.tag != tag:
            nodo = nodo.padre
        if nodo is not self.raiz:
            self.actual = nodo.padre

    def handle_data(self, data):
        if self.actual.tag == "style":
            self.css.append(data)
        elif self.actual.tag == "title":
            self.titulo += data
        else:
            self.actual.hijos.append(data)


# --------------------------------------------------------------------------
# Colores
# --------------------------------------------------------------------------

def _hex(valor: str) -> str:
    v = valor.lstrip("#")
    if len(v) == 3:
        v = "".join(c * 2 for c in v)
    return v.upper()


def leer_paleta(css: str) -> dict[str, str]:
    """Lee las variables de color del primer bloque :root del CSS."""
    paleta = dict(PALETA_NEUTRA)
    bloque = re.search(r":root\s*\{([^}]*)\}", css)
    if bloque:
        for nombre, valor in re.findall(r"--([\w-]+)\s*:\s*(#[0-9a-fA-F]{3,6})\b", bloque.group(1)):
            if nombre in paleta:
                paleta[nombre] = _hex(valor)
    fuente = re.search(r"--fuente\s*:\s*([^;]+);", bloque.group(1) if bloque else "")
    paleta["fuente"] = _fuente_word(fuente.group(1) if fuente else "")
    return paleta


FUENTES_SERIF_WORD = ("Georgia", "Cambria", "Times New Roman", "Garamond", "Book Antiqua")


def _fuente_word(familias: str) -> str:
    """Elige una fuente que Word tenga casi seguro: serif si el CSS es serif, si no Calibri."""
    nombres = [f.strip().strip("\"'") for f in familias.split(",") if f.strip()]
    if nombres and nombres[-1] == "serif":
        return next((n for n in nombres if n in FUENTES_SERIF_WORD), "Cambria")
    return "Calibri"


def mezcla(color: str, fondo: str, proporcion: float = 0.10) -> str:
    """Equivale a color-mix(in srgb, color 10%, fondo)."""
    a = [int(color[i:i + 2], 16) for i in (0, 2, 4)]
    b = [int(fondo[i:i + 2], 16) for i in (0, 2, 4)]
    return "".join(f"{round(x * proporcion + y * (1 - proporcion)):02X}" for x, y in zip(a, b))


# --------------------------------------------------------------------------
# Utilidades de Word
# --------------------------------------------------------------------------

def _sombrear(celda, color: str) -> None:
    tc_pr = celda._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), color)
    tc_pr.append(shd)


def _bordes(celda, izquierda: str | None = None, grosor: int = 24) -> None:
    """Quita los bordes de la celda y, si se indica, pone uno a la izquierda."""
    tc_pr = celda._tc.get_or_add_tcPr()
    bordes = OxmlElement("w:tcBorders")
    for lado in ("top", "left", "bottom", "right"):
        el = OxmlElement(f"w:{lado}")
        if lado == "left" and izquierda:
            el.set(qn("w:val"), "single")
            el.set(qn("w:sz"), str(grosor))
            el.set(qn("w:color"), izquierda)
        else:
            el.set(qn("w:val"), "nil")
        bordes.append(el)
    tc_pr.append(bordes)


def _separador(cont) -> None:
    """Párrafo mínimo tras una tabla: evita que Word una tablas seguidas."""
    formato = cont.add_paragraph().paragraph_format
    formato.space_before = Pt(0)
    formato.space_after = Pt(2)
    formato.line_spacing = Pt(6)


def _vaciar_primer_parrafo(celda) -> None:
    """Quita el párrafo vacío inicial de una celda si hay más contenido."""
    pars = celda.paragraphs
    if len(celda._tc.xpath("./w:p|./w:tbl")) > 1 and pars and not pars[0].text and not pars[0].runs:
        pars[0]._p.getparent().remove(pars[0]._p)


def _num_nuevo(doc, estilo: str) -> int | None:
    """Crea una numeración nueva que empieza en 1 para el estilo de lista dado."""
    try:
        numbering = doc.part.numbering_part.numbering_definitions._numbering
        num_id_estilo = doc.styles[estilo].element.pPr.numPr.numId.val
        abstract_id = numbering.num_having_numId(num_id_estilo).abstractNumId.val
        num = numbering.add_num(abstract_id)
        num.add_lvlOverride(ilvl=0).add_startOverride(1)
        return num.numId
    except Exception:  # plantillas sin numeración: se usa la del estilo tal cual
        return None


def _aplicar_num(par, num_id: int) -> None:
    num_pr = par._p.get_or_add_pPr().get_or_add_numPr()
    num_pr.get_or_add_ilvl().val = 0
    num_pr.get_or_add_numId().val = num_id


# --------------------------------------------------------------------------
# Conversión
# --------------------------------------------------------------------------

class Conversor:
    def __init__(self, paleta: dict[str, str]):
        self.p = paleta
        self.doc = Document()
        self._configurar()

    def _configurar(self) -> None:
        normal = self.doc.styles["Normal"]
        normal.font.name = self.p["fuente"]
        normal.font.size = Pt(11)
        normal.font.color.rgb = RGBColor.from_string(self.p["texto"])
        for nivel in (1, 2, 3):
            estilo = self.doc.styles[f"Heading {nivel}"]
            estilo.font.name = self.p["fuente"]
            estilo.font.color.rgb = RGBColor.from_string(self.p["def"] if nivel < 3 else self.p["texto"])
        for seccion in self.doc.sections:
            seccion.left_margin = seccion.right_margin = Cm(2)
            seccion.top_margin = seccion.bottom_margin = Cm(2)

    # ---- texto en línea -------------------------------------------------

    def _runs(self, nodo: Nodo, fmt: dict, salida: list, saltar: set) -> None:
        for h in nodo.hijos:
            if isinstance(h, str):
                salida.append((h, fmt))
                continue
            if id(h) in saltar or h.tag in IGNORAR:
                continue
            if h.tag == "br":
                salida.append(("\n", fmt))
                continue
            f = dict(fmt)
            if h.tag in ("b", "strong") or "paso-titulo" in h.clases or "fecha" in h.clases:
                f["b"] = True
            if h.tag in ("i", "em", "cite", "dfn"):
                f["i"] = True
            if h.tag in ("code", "kbd", "var"):
                f["code"] = True
            if h.tag == "sub":
                f["sub"] = True
            if h.tag == "sup":
                f["sup"] = True
            if h.tag == "q":
                salida.append(("«", fmt))
            self._runs(h, f, salida, saltar)
            if h.tag == "q":
                salida.append(("»", fmt))
            if "paso-titulo" in h.clases or "fecha" in h.clases:
                salida.append(("\n", fmt))

    def _escribir(self, par, runs: list) -> None:
        limpio: list = []
        espacio_previo = True
        for txt, f in runs:
            if txt == "\n":
                if limpio and limpio[-1][0] != "\n":
                    limpio[-1] = (limpio[-1][0].rstrip(" "), limpio[-1][1])
                limpio.append(("\n", f))
                espacio_previo = True
                continue
            t = re.sub(r"\s+", " ", txt)
            if espacio_previo:
                t = t.lstrip(" ")
            if not t:
                continue
            espacio_previo = t.endswith(" ")
            limpio.append((t, f))
        while limpio and limpio[-1][0] == "\n":
            limpio.pop()
        while limpio and limpio[0][0] == "\n":
            limpio.pop(0)
        if limpio:
            limpio[-1] = (limpio[-1][0].rstrip(" "), limpio[-1][1])
        for t, f in limpio:
            if t == "\n":
                par.add_run().add_break()
                continue
            run = par.add_run(t)
            run.bold = f.get("b") or None
            run.italic = f.get("i") or None
            if f.get("code"):
                run.font.name = "Consolas"
            if f.get("sub"):
                run.font.subscript = True
            if f.get("sup"):
                run.font.superscript = True
            if f.get("color"):
                run.font.color.rgb = RGBColor.from_string(f["color"])
            if f.get("tam"):
                run.font.size = Pt(f["tam"])

    def _parrafo(self, cont, nodo: Nodo, fmt: dict | None = None, estilo: str | None = None,
                 saltar: set | None = None):
        par = cont.add_paragraph(style=estilo) if estilo else cont.add_paragraph()
        runs: list = []
        self._runs(nodo, fmt or {}, runs, saltar or set())
        self._escribir(par, runs)
        return par

    # ---- bloques ----------------------------------------------------------

    def bloques(self, cont, nodo: Nodo, fmt: dict | None = None, saltar: set | None = None) -> None:
        """Recorre los hijos de un nodo; agrupa el texto suelto en párrafos."""
        fmt = fmt or {}
        saltar = saltar or set()
        pendientes: list = []

        def vaciar():
            if not pendientes:
                return
            runs: list = []
            tmp = Nodo("#tmp")
            tmp.hijos = list(pendientes)
            self._runs(tmp, fmt, runs, saltar)
            if "".join(t for t, _ in runs).strip():
                par = cont.add_paragraph()
                self._escribir(par, runs)
            pendientes.clear()

        for h in nodo.hijos:
            if isinstance(h, Nodo) and id(h) in saltar:
                continue
            if isinstance(h, str) or h.tag in INLINE:
                pendientes.append(h)
                continue
            vaciar()
            self.bloque(cont, h, fmt)
        vaciar()

    def bloque(self, cont, n: Nodo, fmt: dict) -> None:
        t, c = n.tag, n.clases
        if t in IGNORAR or t == "hr":
            return
        if t in ("h1", "h2", "h3", "h4", "h5", "h6"):
            nivel = min(int(t[1]), 4)
            self._parrafo(cont, n, fmt, estilo=f"Heading {nivel}")
        elif t == "p":
            par = self._parrafo(cont, n, {**fmt, "i": True} if "analogia" in c else fmt)
            if "porque" in c:
                par.paragraph_format.left_indent = Cm(0.5)
        elif t == "div" and "caja" in c:
            self.caja(cont, n)
        elif "leyenda" in c:
            self.leyenda(cont, n)
        elif "cornell" in c:
            self.cornell(cont, n)
        elif t == "ol" and "linea-tiempo" in c:
            self.linea_tiempo(cont, n)
        elif t in ("ul", "ol"):
            self.lista(cont, n, nivel=0, numerada=(t == "ol"), fmt=fmt)
        elif t == "table":
            self.tabla(cont, n)
        elif t == "blockquote":
            self._parrafo(cont, n, {**fmt, "i": True}).paragraph_format.left_indent = Cm(1)
        elif t in ("dl",):
            for h in n.elementos():
                self._parrafo(cont, h, {**fmt, "b": h.tag == "dt"})
        else:  # contenedores: main, header, section, article, nav, div, figure...
            self.bloques(cont, n, fmt)

    def lista(self, cont, n: Nodo, nivel: int, numerada: bool, fmt: dict) -> None:
        base = "List Number" if numerada else "List Bullet"
        estilo = base if nivel == 0 else f"{base} {min(nivel + 1, 3)}"
        num_id = _num_nuevo(self.doc, estilo) if numerada else None
        for li in n.elementos():
            if li.tag != "li":
                continue
            par = cont.add_paragraph(style=estilo)
            if num_id is not None:
                _aplicar_num(par, num_id)
            runs: list = []
            for h in li.hijos:
                if isinstance(h, Nodo) and h.tag in ("ul", "ol"):
                    self._escribir(par, runs)
                    runs = []
                    self.lista(cont, h, nivel + 1, h.tag == "ol", fmt)
                    par = None
                    continue
                if par is None:  # texto después de una sublista
                    par = cont.add_paragraph(style=estilo)
                tmp = Nodo("#tmp")
                tmp.hijos = [h]
                if runs and isinstance(h, Nodo) and h.tag not in INLINE:
                    runs.append(("\n", fmt))
                self._runs(tmp if isinstance(h, str) or h.tag in INLINE else h, fmt, runs, set())
            if par is not None:
                self._escribir(par, runs)

    def tabla(self, cont, n: Nodo) -> None:
        filas: list[Nodo] = []

        def recoger(nodo: Nodo):
            for h in nodo.elementos():
                if h.tag == "tr":
                    filas.append(h)
                elif h.tag in ("thead", "tbody", "tfoot"):
                    recoger(h)

        recoger(n)
        if not filas:
            return
        caption = n.buscar(lambda x: x.tag == "caption")
        if caption is not None:
            self._parrafo(cont, caption, {"i": True})

        def span(celda: Nodo) -> int:
            try:
                return max(1, int(celda.attrs.get("colspan", "1")))
            except ValueError:
                return 1

        ncols = max(sum(span(c) for c in f.elementos() if c.tag in ("td", "th")) for f in filas)
        tabla = cont.add_table(rows=len(filas), cols=ncols)
        tabla.style = "Table Grid"
        cabecera = mezcla(self.p["def"], self.p["fondo"])
        for i, tr in enumerate(filas):
            en_thead = tr.padre is not None and tr.padre.tag == "thead"
            j = 0
            for celda_html in tr.elementos():
                if celda_html.tag not in ("td", "th") or j >= ncols:
                    continue
                s = span(celda_html)
                celda = tabla.cell(i, j)
                if s > 1:
                    celda = celda.merge(tabla.cell(i, min(j + s - 1, ncols - 1)))
                es_th = celda_html.tag == "th"
                self.bloques(celda, celda_html, {"b": True} if es_th else {})
                _vaciar_primer_parrafo(celda)
                if en_thead or (i == 0 and es_th):
                    _sombrear(celda, cabecera)
                j += s
        _separador(cont)

    def caja(self, cont, n: Nodo) -> None:
        tipo = next((t for t in TIPOS_CAJA if t in n.clases), "def")
        acento = self.p[tipo]
        tabla = cont.add_table(rows=1, cols=1)
        celda = tabla.cell(0, 0)
        _sombrear(celda, mezcla(acento, self.p["fondo"]))
        _bordes(celda, izquierda=acento)
        etiqueta = n.buscar(lambda x: "etiqueta" in x.clases)
        texto = etiqueta.texto() if etiqueta is not None else ETIQUETAS[tipo]
        run = celda.paragraphs[0].add_run(texto.upper())
        run.bold = True
        run.font.size = Pt(8.5)
        run.font.color.rgb = RGBColor.from_string(acento)
        celda.paragraphs[0].paragraph_format.space_after = Pt(2)
        self.bloques(celda, n, saltar={id(etiqueta)} if etiqueta is not None else set())
        _separador(cont)

    def leyenda(self, cont, n: Nodo) -> None:
        items = [h for h in n.elementos() if any(t in h.clases for t in TIPOS_CAJA)]
        if not items:
            return
        tabla = cont.add_table(rows=1, cols=len(items))
        for j, item in enumerate(items):
            tipo = next(t for t in TIPOS_CAJA if t in item.clases)
            celda = tabla.cell(0, j)
            _sombrear(celda, mezcla(self.p[tipo], self.p["fondo"]))
            _bordes(celda, izquierda=self.p[tipo], grosor=18)
            run = celda.paragraphs[0].add_run(item.texto() or ETIQUETAS[tipo])
            run.bold = True
            run.font.size = Pt(8)
            run.font.color.rgb = RGBColor.from_string(self.p[tipo])
        _separador(cont)

    def linea_tiempo(self, cont, n: Nodo) -> None:
        items = [h for h in n.elementos() if h.tag == "li"]
        tabla = cont.add_table(rows=len(items) + 1, cols=2)
        tabla.style = "Table Grid"
        cabecera = mezcla(self.p["def"], self.p["fondo"])
        for j, titulo in enumerate(("Fecha", "Hecho")):
            celda = tabla.cell(0, j)
            celda.paragraphs[0].add_run(titulo).bold = True
            _sombrear(celda, cabecera)
        for i, li in enumerate(items, start=1):
            fecha = li.buscar(lambda x: "fecha" in x.clases)
            celda_fecha = tabla.cell(i, 0)
            run = celda_fecha.paragraphs[0].add_run(fecha.texto() if fecha is not None else "")
            run.bold = True
            run.font.color.rgb = RGBColor.from_string(self.p["def"])
            celda_hecho = tabla.cell(i, 1)
            self.bloques(celda_hecho, li, saltar={id(fecha)} if fecha is not None else set())
            _vaciar_primer_parrafo(celda_hecho)
        for fila in tabla.rows:
            fila.cells[0].width = Cm(3.4)
            fila.cells[1].width = Cm(13.6)
        _separador(cont)

    def cornell(self, cont, n: Nodo) -> None:
        filas = [h for h in n.elementos() if "fila" in h.clases]
        sintesis = n.buscar(lambda x: "sintesis" in x.clases)
        tabla = cont.add_table(rows=len(filas) + (1 if sintesis is not None else 0), cols=2)
        tabla.style = "Table Grid"
        fondo_preg = mezcla(self.p["clave"], self.p["fondo"])
        for i, fila in enumerate(filas):
            pregunta = fila.buscar(lambda x: "pregunta" in x.clases)
            notas = fila.buscar(lambda x: "notas" in x.clases)
            celda_p, celda_n = tabla.cell(i, 0), tabla.cell(i, 1)
            if pregunta is not None:
                self.bloques(celda_p, pregunta, {"b": True})
                _vaciar_primer_parrafo(celda_p)
            _sombrear(celda_p, fondo_preg)
            if notas is not None:
                self.bloques(celda_n, notas)
                _vaciar_primer_parrafo(celda_n)
            celda_p.width, celda_n.width = Cm(5), Cm(12)
        if sintesis is not None:
            celda = tabla.cell(len(filas), 0).merge(tabla.cell(len(filas), 1))
            self.bloques(celda, sintesis)
            _vaciar_primer_parrafo(celda)
        _separador(cont)


def convertir(entrada: str | Path, salida: str | Path) -> Path:
    entrada, salida = Path(entrada), Path(salida)
    constructor = _Constructor()
    constructor.feed(entrada.read_text(encoding="utf-8"))
    constructor.close()
    conversor = Conversor(leer_paleta("\n".join(constructor.css)))
    if constructor.titulo.strip():
        conversor.doc.core_properties.title = constructor.titulo.strip()
    cuerpo = constructor.raiz.buscar(lambda x: x.tag == "body") or constructor.raiz
    conversor.bloques(conversor.doc, cuerpo)
    salida.parent.mkdir(parents=True, exist_ok=True)
    conversor.doc.save(str(salida))
    return salida


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("Uso: python html_a_docx.py entrada.html salida.docx", file=sys.stderr)
        return 2
    entrada = Path(argv[1])
    if not entrada.is_file():
        print(f"No existe el archivo de entrada: {entrada}", file=sys.stderr)
        return 2
    salida = convertir(entrada, argv[2])
    print(f"DOCX generado: {salida}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
