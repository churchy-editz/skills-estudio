#!/usr/bin/env python3
"""Copia un DOCX y le añade los comentarios de la corrección como comentarios de Word.

Uso:
    python comentar_docx.py original.docx correccion.json salida-corregido.docx [--autor "Corrector"]

Cada comentario del JSON (references/esquema.md) se ancla al fragmento exacto
de su campo «cita». El texto del alumno no se modifica: solo se parten
ejecuciones (runs) en los bordes del fragmento, copiando su formato, y se
añaden las marcas del comentario. Si una cita no aparece literal, se intenta
sin distinguir comillas tipográficas ni espacios; si tampoco, el comentario
no se ancla y se informa (código 2).

Usa la API de comentarios de python-docx (1.2 o posterior). Con versiones
anteriores escribe el XML de comentarios directamente (word/comments.xml).
"""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import json
import re
import sys
from pathlib import Path

try:
    import docx
    from docx import Document
    from docx.opc.constants import RELATIONSHIP_TYPE as RT
    from docx.opc.packuri import PackURI
    from docx.opc.part import Part
    from docx.oxml import parse_xml
    from docx.oxml.ns import nsdecls, qn
    from docx.text.paragraph import Paragraph
    from docx.text.run import Run
except ImportError:
    print(f'Falta python-docx. Instálalo con:\n    "{sys.executable}" -m pip install python-docx', file=sys.stderr)
    sys.exit(1)

GRAVEDAD = {"critico": "CRÍTICO", "importante": "IMPORTANTE", "menor": "MENOR"}
CT_COMENTARIOS = "application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml"


def texto_comentario(c: dict) -> str:
    partes = [f"[{GRAVEDAD.get(c.get('gravedad', ''), c.get('gravedad', '').upper())}] {c.get('que_falla', '').strip()}"]
    if c.get("por_que_importa"):
        partes.append(f"Por qué importa: {c['por_que_importa'].strip()}")
    if c.get("como_arreglarlo"):
        partes.append(f"Cómo arreglarlo: {c['como_arreglarlo'].strip()}")
    if c.get("ejemplo"):
        partes.append(f"Por ejemplo: {c['ejemplo'].strip()}")
    if c.get("criterio"):
        partes.append(f"Criterio: {c['criterio']}")
    return "\n".join(partes)


# --- Texto de los runs ---------------------------------------------------------------

def texto_run(r) -> str:
    salida = []
    for hijo in r:
        if hijo.tag == qn("w:t"):
            salida.append(hijo.text or "")
        elif hijo.tag == qn("w:tab"):
            salida.append("\t")
        elif hijo.tag in (qn("w:br"), qn("w:cr")):
            salida.append("\n")
        elif hijo.tag == qn("w:noBreakHyphen"):
            salida.append("-")
    return "".join(salida)


def runs_de(p) -> list:
    return p.xpath("./w:r | ./w:hyperlink/w:r | ./w:ins/w:r | ./w:smartTag/w:r")


def texto_parrafo(p) -> str:
    return "".join(texto_run(r) for r in runs_de(p))


def parrafos(doc) -> list:
    """Todos los párrafos del cuerpo, también los de las tablas, en orden."""
    return list(doc.element.body.iter(qn("w:p")))


def _es_simple(r) -> bool:
    """Un run que solo tiene formato y un w:t se puede partir sin perder nada."""
    hijos = [h for h in r if h.tag != qn("w:rPr")]
    return len(hijos) == 1 and hijos[0].tag == qn("w:t")


def partir(r, pos: int):
    """Parte un run simple en pos; devuelve el run de la derecha (nuevo)."""
    t = r.find(qn("w:t"))
    texto = t.text or ""
    nuevo = copy.deepcopy(r)
    t.text = texto[:pos]
    nt = nuevo.find(qn("w:t"))
    nt.text = texto[pos:]
    for x in (t, nt):
        if x.text != x.text.strip():
            x.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    r.addnext(nuevo)
    return nuevo


def _variantes(cita: str) -> list[str]:
    cita = re.sub(r"\^\{([^}]*)\}", r"\1", cita).strip()
    salida = [cita]
    tipograficas = cita.replace('"', "“").replace("'", "’")
    for v in (tipograficas, cita.replace("“", '"').replace("”", '"').replace("’", "'")):
        if v not in salida:
            salida.append(v)
    return salida


def _normalizar_con_mapa(texto: str) -> tuple[str, list[int]]:
    """Texto con comillas rectas y espacios simples, y la posición original de cada carácter."""
    salida, mapa, previo_espacio = [], [], False
    tabla = {"“": '"', "”": '"', "«": '"', "»": '"', "‘": "'", "’": "'", " ": " ", "\t": " ", "\n": " "}
    for i, ch in enumerate(texto):
        ch = tabla.get(ch, ch)
        if ch == " ":
            if previo_espacio:
                continue
            previo_espacio = True
        else:
            previo_espacio = False
        salida.append(ch)
        mapa.append(i)
    return "".join(salida), mapa


def localizar(doc, cita: str, usados: set) -> tuple | None:
    """(párrafo, inicio, fin) de la primera aparición de la cita aún no usada."""
    ps = parrafos(doc)
    for variante in _variantes(cita):
        for i, p in enumerate(ps):
            t = texto_parrafo(p)
            ini = t.find(variante)
            while ini >= 0:
                if (i, ini) not in usados:
                    return p, ini, ini + len(variante), (i, ini)
                ini = t.find(variante, ini + 1)
    objetivo, _ = _normalizar_con_mapa(_variantes(cita)[0])
    for i, p in enumerate(ps):
        t = texto_parrafo(p)
        norm, mapa = _normalizar_con_mapa(t)
        ini = norm.find(objetivo)
        if ini >= 0 and (i, mapa[ini]) not in usados:
            return p, mapa[ini], mapa[ini + len(objetivo) - 1] + 1, (i, mapa[ini])
    return None


def aislar(p, ini: int, fin: int) -> list:
    """Parte los runs para que [ini, fin) quede en runs completos; devuelve esos runs."""
    pos = 0
    for r in list(runs_de(p)):
        largo = len(texto_run(r))
        if pos < ini < pos + largo and _es_simple(r):
            partir(r, ini - pos)
            return aislar(p, ini, fin)
        if pos < fin < pos + largo and _es_simple(r):
            partir(r, fin - pos)
            return aislar(p, ini, fin)
        pos += largo
    seleccion, pos = [], 0
    for r in runs_de(p):
        largo = len(texto_run(r))
        if largo and pos + largo > ini and pos < fin:
            seleccion.append(r)
        pos += largo
    return seleccion


# --- Comentarios sin la API (python-docx < 1.2) -------------------------------------------

class ComentariosXML:
    def __init__(self, doc):
        self.doc = doc
        self.raiz = parse_xml(f"<w:comments {nsdecls('w')}/>")
        self.siguiente = 0

    def anadir(self, runs: list, texto: str, autor: str, iniciales: str) -> None:
        cid = str(self.siguiente)
        self.siguiente += 1
        fecha = dt.datetime.now().replace(microsecond=0).isoformat() + "Z"
        com = parse_xml(f'<w:comment {nsdecls("w")} w:id="{cid}" w:author="" w:initials="" w:date="{fecha}"/>')
        com.set(qn("w:author"), autor)
        com.set(qn("w:initials"), iniciales)
        for linea in texto.split("\n"):
            p = parse_xml(f'<w:p {nsdecls("w")}><w:r><w:t xml:space="preserve"></w:t></w:r></w:p>')
            p.find(qn("w:r")).find(qn("w:t")).text = linea
            com.append(p)
        self.raiz.append(com)
        inicio = parse_xml(f'<w:commentRangeStart {nsdecls("w")} w:id="{cid}"/>')
        fin = parse_xml(f'<w:commentRangeEnd {nsdecls("w")} w:id="{cid}"/>')
        ref = parse_xml(f'<w:r {nsdecls("w")}>'
                        f'<w:commentReference w:id="{cid}"/></w:r>')
        runs[0].addprevious(inicio)
        runs[-1].addnext(fin)
        fin.addnext(ref)

    def guardar_en_paquete(self) -> None:
        from lxml import etree
        blob = etree.tostring(self.raiz, xml_declaration=True, encoding="UTF-8", standalone=True)
        parte = Part(PackURI("/word/comments.xml"), CT_COMENTARIOS, blob, self.doc.part.package)
        self.doc.part.relate_to(parte, RT.COMMENTS)


def comentar(original: str | Path, correccion: dict, salida: str | Path, autor: str = "Corrector",
             iniciales: str = "CT", usar_api: bool | None = None) -> dict:
    doc = Document(str(original))
    if usar_api is None:
        usar_api = hasattr(doc, "add_comment")
    xml = None if usar_api else ComentariosXML(doc)
    if xml is not None and any(r.reltype == RT.COMMENTS for r in doc.part.rels.values()):
        raise SystemExit("El DOCX ya tiene comentarios y esta versión de python-docx no puede añadir más: "
                         "actualízala con pip install -U python-docx")
    anclados, sin_anclar, usados = [], [], set()
    for c in correccion.get("comentarios", []):
        cita = (c.get("cita") or "").strip()
        hallado = localizar(doc, cita, usados) if cita else None
        if not hallado:
            sin_anclar.append(c.get("id", "?"))
            continue
        p, ini, fin, clave = hallado
        usados.add(clave)
        runs = aislar(p, ini, fin)
        if not runs:
            sin_anclar.append(c.get("id", "?"))
            continue
        texto = texto_comentario(c)
        if usar_api:
            parrafo_obj = Paragraph(p, doc.part)
            doc.add_comment([Run(runs[0], parrafo_obj), Run(runs[-1], parrafo_obj)], text=texto, author=autor,
                            initials=iniciales)
        else:
            xml.anadir(runs, texto, autor, iniciales)
        anclados.append(c.get("id", "?"))
    if xml is not None and anclados:
        xml.guardar_en_paquete()
    doc.save(str(salida))
    return {"anclados": anclados, "sin_anclar": sin_anclar, "metodo": "api" if usar_api else "xml"}


def main(argv: list[str]) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    p = argparse.ArgumentParser(description="Añade la corrección como comentarios de Word.")
    p.add_argument("original")
    p.add_argument("correccion")
    p.add_argument("salida")
    p.add_argument("--autor", default="Corrector")
    p.add_argument("--iniciales", default="CT")
    p.add_argument("--xml", action="store_true", help="escribir el XML a mano aunque python-docx tenga la API")
    a = p.parse_args(argv[1:])
    if Path(a.salida).resolve() == Path(a.original).resolve():
        print("La salida no puede ser el original: el trabajo del alumno no se sobrescribe.", file=sys.stderr)
        return 1
    correccion = json.loads(Path(a.correccion).read_text(encoding="utf-8"))
    r = comentar(a.original, correccion, a.salida, a.autor, a.iniciales, usar_api=False if a.xml else None)
    print(f"{a.salida}: {len(r['anclados'])} comentarios anclados (python-docx {docx.__version__ if hasattr(docx, '__version__') else '?'}, "
          f"método {r['metodo']})")
    if r["sin_anclar"]:
        print(f"Sin anclar (la cita no aparece literal en el documento): {', '.join(r['sin_anclar'])}")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
