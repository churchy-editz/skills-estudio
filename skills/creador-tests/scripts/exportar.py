#!/usr/bin/env python3
"""Exporta un test de creador-tests a otros formatos.

Uso:
    python exportar.py test.json --formato gift -o salida.txt

Formatos:
    gift     Moodle (GIFT). Todos los tipos; aplica la penalización de meta.
    kahoot   CSV con las columnas de la plantilla oficial de Kahoot (pregunta
             máx. 120 caracteres, respuestas máx. 75). Sin huecos. Las preguntas
             que superan los límites se listan para reescribirlas en
             test-<tema>-kahoot.json (SKILL.md, sección 12); al final, resumen
             con el número exacto de exportadas y omitidas.
    anki     TSV para Anki: frente = pregunta; dorso = respuesta + explicación.
    quizlet  TSV para Quizlet: término = pregunta; definición = respuesta.
    docx     Word imprimible con las soluciones en página aparte (python-docx).

Solo librería estándar, salvo docx. Los avisos salen por stderr.
"""
from __future__ import annotations

import argparse
import csv
import html
import io
import json
import sys
from pathlib import Path

LETRAS = "ABCD"
EXTENSIONES = {"gift": ".gift.txt", "kahoot": ".kahoot.csv", "anki": ".anki.txt", "quizlet": ".quizlet.txt", "docx": ".docx"}
PESOS_GIFT = {"ninguna": None, "1/3": "-33.33333", "1/4": "-25"}

KAHOOT_CABECERA = [
    "Question - max 120 characters",
    "Answer 1 - max 75 characters",
    "Answer 2 - max 75 characters",
    "Answer 3 - max 75 characters",
    "Answer 4 - max 75 characters",
    "Time limit (sec) – 5, 10, 20, 30, 60, 90, 120, or 240 secs",
    "Correct answer(s) - choose at least one",
]
KAHOOT_MAX_PREGUNTA = 120
KAHOOT_MAX_RESPUESTA = 75
KAHOOT_TIEMPO = {1: 20, 2: 30, 3: 60}


def avisar(msg: str) -> None:
    print(f"Aviso: {msg}", file=sys.stderr)


def respuesta(p: dict) -> str:
    if p["tipo"] == "vf":
        return "Verdadero" if p["correcta"] else "Falso"
    if p["tipo"] == "huecos":
        return " / ".join(p["correcta"])
    return f"{LETRAS[p['correcta']]}) {p['opciones'][p['correcta']]}"


def pregunta_plana(p: dict, con_opciones: bool = True) -> str:
    partes = []
    if p.get("contexto"):
        partes.append(p["contexto"])
    partes.append(p["enunciado"].replace("___", "_____"))
    if con_opciones and p.get("opciones"):
        partes.append("  ".join(f"{LETRAS[i]}) {o}" for i, o in enumerate(p["opciones"])))
    return " ".join(partes)


def una_linea(texto: str) -> str:
    return " ".join(str(texto).replace("\t", " ").split())


# ---------------------------------------------------------------- GIFT
def gift_escapar(texto: str) -> str:
    texto = str(texto).replace("\\", "\\\\")
    for c in "~=#{}:":
        texto = texto.replace(c, "\\" + c)
    return " ".join(texto.replace("\r", " ").replace("\n", " ").split())


def a_gift(datos: dict) -> str:
    peso = PESOS_GIFT.get(datos["meta"].get("penalizacion", "ninguna"))
    mal = f"~%{peso}%" if peso else "~"
    bloques = [f"// {una_linea(datos['meta']['titulo'])}", ""]
    for p in datos["preguntas"]:
        titulo = f"::{gift_escapar(p['id'])}::"
        fb = f"####{gift_escapar(p['explicacion'])} (Sección\\: {gift_escapar(p['seccion'])})"
        bloques.append(f"// {una_linea(p['seccion'])}")
        if p["tipo"] == "vf":
            bloques.append(f"{titulo}{gift_escapar(p['enunciado'])} {{{'TRUE' if p['correcta'] else 'FALSE'}{fb}}}")
        elif p["tipo"] == "huecos":
            antes, despues = p["enunciado"].split("___", 1)
            despues = despues.lstrip("_")
            aceptadas = " ".join(f"={gift_escapar(r)}" for r in p["correcta"])
            antes_g = gift_escapar(antes) + (" " if antes[-1:].isspace() else "")
            despues_g = (" " if despues[:1].isspace() else "") + gift_escapar(despues)
            bloques.append(f"{titulo}{antes_g}{{{aceptadas}{fb}}}{despues_g}")
        else:
            if p["tipo"] == "caso":
                texto = (f"[html]{gift_escapar(html.escape(p['contexto']))}<br><br>"
                         f"{gift_escapar(html.escape(p['enunciado']))}")
            else:
                texto = gift_escapar(p["enunciado"])
            lineas = [f"{titulo}{texto} {{"]
            for i, o in enumerate(p["opciones"]):
                lineas.append(f"\t{'=' if i == p['correcta'] else mal}{gift_escapar(o)}")
            lineas.append(f"\t{fb}")
            lineas.append("}")
            bloques.append("\n".join(lineas))
        bloques.append("")
    return "\n".join(bloques)


# ---------------------------------------------------------------- Kahoot
def a_kahoot(datos: dict) -> str:
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\r\n")
    w.writerow(KAHOOT_CABECERA)
    huecos, largas = [], []
    for p in datos["preguntas"]:
        if p["tipo"] == "huecos":
            huecos.append(p["id"])
            continue
        texto = una_linea(pregunta_plana(p, con_opciones=False))
        opciones = ["Verdadero", "Falso"] if p["tipo"] == "vf" else [una_linea(o) for o in p["opciones"]]
        motivos = []
        if len(texto) > KAHOOT_MAX_PREGUNTA:
            motivos.append(f"pregunta de {len(texto)} caracteres (máx. {KAHOOT_MAX_PREGUNTA})")
        for i, o in enumerate(opciones):
            if len(o) > KAHOOT_MAX_RESPUESTA:
                motivos.append(f"opción {LETRAS[i]} de {len(o)} caracteres (máx. {KAHOOT_MAX_RESPUESTA})")
        if motivos:
            largas.append(p["id"])
            avisar(f"{p['id']}: {'; '.join(motivos)}. Reescríbela más corta en test-<tema>-kahoot.json.")
            continue
        correcta = (1 if p["correcta"] else 2) if p["tipo"] == "vf" else p["correcta"] + 1
        opciones += [""] * (4 - len(opciones))
        w.writerow([texto, *opciones, KAHOOT_TIEMPO.get(p["dificultad"], 30), correcta])
    total = len(datos["preguntas"])
    resumen = f"Kahoot: exportadas {total - len(huecos) - len(largas)} de {total}"
    if huecos:
        resumen += f"; omitidas {len(huecos)} de huecos, que Kahoot no admite ({', '.join(huecos)})"
    if largas:
        resumen += f"; omitidas {len(largas)} por superar los límites ({', '.join(largas)})"
    avisar(resumen + ".")
    return buf.getvalue()


# ---------------------------------------------------------------- Anki / Quizlet
def a_anki(datos: dict) -> str:
    lineas = ["#separator:tab", "#html:true", "#columns:Frente\tDorso"]
    for p in datos["preguntas"]:
        frente = []
        if p.get("contexto"):
            frente.append(f"<i>{html.escape(una_linea(p['contexto']))}</i>")
        frente.append(html.escape(una_linea(p["enunciado"])))
        if p.get("opciones"):
            frente.append("<br>".join(f"{LETRAS[i]}) {html.escape(una_linea(o))}" for i, o in enumerate(p["opciones"])))
        dorso = (f"<b>{html.escape(una_linea(respuesta(p)))}</b><br><br>{html.escape(una_linea(p['explicacion']))}"
                 f"<br><small>Sección: {html.escape(una_linea(p['seccion']))}</small>")
        lineas.append("<br><br>".join(frente) + "\t" + dorso)
    return "\n".join(lineas) + "\n"


def a_quizlet(datos: dict) -> str:
    lineas = []
    for p in datos["preguntas"]:
        termino = una_linea(pregunta_plana(p))
        definicion = una_linea(f"{respuesta(p)}. {p['explicacion']}")
        lineas.append(f"{termino}\t{definicion}")
    return "\n".join(lineas) + "\n"


# ---------------------------------------------------------------- DOCX
def a_docx(datos: dict, salida: Path) -> None:
    try:
        from docx import Document
        from docx.enum.text import WD_BREAK
        from docx.shared import Pt
    except ImportError:
        print(
            "Falta la librería python-docx. Instálala con:\n"
            f'    "{sys.executable}" -m pip install python-docx',
            file=sys.stderr,
        )
        raise SystemExit(1)
    meta = datos["meta"]
    doc = Document()
    doc.styles["Normal"].font.size = Pt(11)
    doc.add_heading(meta["titulo"], level=1)
    penal = {"ninguna": "Los fallos no restan.", "1/3": "Cada fallo resta 1/3 de acierto.",
             "1/4": "Cada fallo resta 1/4 de acierto."}.get(meta.get("penalizacion"), "")
    doc.add_paragraph(f"{meta['asignatura']} · {len(datos['preguntas'])} preguntas. {penal}")
    doc.add_paragraph("Nombre: ______________________________    Fecha: ____________")
    for n, p in enumerate(datos["preguntas"], 1):
        if p.get("contexto"):
            caso = doc.add_paragraph()
            caso.add_run("Caso. ").bold = True
            caso.add_run(p["contexto"]).italic = True
        par = doc.add_paragraph()
        par.add_run(f"{n}. ").bold = True
        par.add_run(p["enunciado"].replace("___", "______________"))
        if p.get("opciones"):
            for i, o in enumerate(p["opciones"]):
                doc.add_paragraph(f"{LETRAS[i]}) {o}").paragraph_format.left_indent = Pt(18)
        elif p["tipo"] == "vf":
            doc.add_paragraph("(   ) Verdadero        (   ) Falso").paragraph_format.left_indent = Pt(18)
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
    doc.add_heading("Soluciones", level=1)
    for n, p in enumerate(datos["preguntas"], 1):
        par = doc.add_paragraph()
        par.add_run(f"{n}. {respuesta(p)}. ").bold = True
        par.add_run(f"{p['explicacion']} ")
        par.add_run(f"(Sección: {p['seccion']})").italic = True
    salida.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(salida))


FORMATOS = {"gift": a_gift, "kahoot": a_kahoot, "anki": a_anki, "quizlet": a_quizlet}


def exportar(entrada: Path, formato: str, salida: Path | None = None) -> Path:
    datos = json.loads(Path(entrada).read_text(encoding="utf-8"))
    if salida is None:
        nombre = Path(entrada).name
        base = nombre[:-5] if nombre.endswith(".json") else nombre
        salida = Path(entrada).with_name(base + EXTENSIONES[formato])
    salida = Path(salida)
    if formato == "docx":
        a_docx(datos, salida)
    else:
        texto = FORMATOS[formato](datos)
        salida.parent.mkdir(parents=True, exist_ok=True)
        # Kahoot y Excel leen mejor el CSV con BOM
        # open() en lugar de write_text(newline=…), que no existe hasta Python 3.10
        with open(salida, "w", encoding="utf-8-sig" if formato == "kahoot" else "utf-8", newline="") as f:
            f.write(texto)
    return salida


def main(argv: list[str] | None = None) -> int:
    for flujo in (sys.stdout, sys.stderr):
        try:
            flujo.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description="Exporta un test a GIFT, Kahoot, Anki, Quizlet o DOCX.")
    ap.add_argument("entrada", type=Path)
    ap.add_argument("--formato", required=True, choices=[*FORMATOS, "docx"])
    ap.add_argument("-o", "--salida", type=Path)
    args = ap.parse_args(argv)
    if not args.entrada.is_file():
        print(f"No existe el archivo de entrada: {args.entrada}", file=sys.stderr)
        return 2
    salida = exportar(args.entrada, args.formato, args.salida)
    print(f"Exportado ({args.formato}): {salida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
