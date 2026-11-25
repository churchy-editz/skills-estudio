#!/usr/bin/env python3
"""Genera los portables de cada skill para chats sin soporte de skills.

Uso:
    python tools/generar_portables.py              # regenera los portables
    python tools/generar_portables.py --comprobar  # código 1 si alguno está desactualizado

Dos archivos por skill, en skills/<skill>/:

- prompt-portable.md: une SKILL.md, references/ y assets/ en un texto
  autocontenido. Las rutas a references/ y assets/ pasan a apuntar a su anexo,
  y se añade una sección con las comprobaciones de cada script hechas a mano.
  Se sube como archivo de conocimiento de un GPT, un Gem o un proyecto.
- prompt-portable-lite.md (máx. 7.500 caracteres): lo esencial para el campo
  de instrucciones (flujo, reglas duras, formato de salida y comprobaciones
  principales), que remite al portable completo adjunto. Su texto se escribe a
  mano en tools/lite/<skill>.md; la primera línea guarda la huella del SKILL.md
  con el que se revisó. Si el SKILL.md cambia, --comprobar falla hasta que se
  revise el lite y se actualice la huella.

No se editan a mano: se regeneran con este script cada vez que cambia la skill.
Solo librería estándar.
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
NOMBRE = "prompt-portable.md"
NOMBRE_LITE = "prompt-portable-lite.md"
LIMITE_LITE = 7500
LITE = Path(__file__).resolve().parent / "lite"
EXT_ASSETS = {".html": "html", ".css": "css", ".js": "javascript", ".md": "markdown", ".txt": "text"}

# Comprobaciones que hace cada script, para aplicarlas a mano cuando no se puede
# ejecutar código. Una entrada por skill; si una skill nueva no tiene, se usa GENERICO.
MANUAL = {
    "creador-apuntes": """\
Esta skill no tiene validador automático; su único script (`scripts/html_a_docx.py`) convierte el HTML en Word.

- **Sin ejecutar código:** entrega solo el HTML, partiendo de la plantilla del anexo `assets/plantilla-base.html`, y di que se abre con Word y se guarda como .docx con "Guardar como".
- **Sin poder crear archivos:** entrega Markdown con la misma estructura. Cada caja va como cita que empieza por su etiqueta en negrita (`> **Ojo.** …`).
- **Extensión:** cuenta a mano las palabras de los apuntes, sin la leyenda ni las etiquetas, y compáralas con el objetivo (±15 %).
- **Cajas:** como mucho 3-4 por cada ~500 palabras, y todas con su etiqueta de texto.
- **Tono:** repasa la lista de prohibiciones del anexo `tono.md` frase a frase.""",

    "creador-tests": """\
`scripts/validar.py` comprueba el test; `generar_html.py` y `exportar.py` producen los archivos. Sin código:

- **Formato de entrega:** el JSON (si se pueden crear archivos) y el test en Markdown con las soluciones y sus explicaciones al final, como dice la sección 8. Los formatos de exportación (GIFT, CSV de Kahoot…) solo se escriben a mano si el usuario los pide.
- **Errores, que hay que corregir siempre:** cada pregunta tiene `id` único, `tipo`, `nivel_cognitivo`, `enunciado`, `explicacion`, `dificultad` (1-3) y `seccion`; las de opción múltiple y casos, 4 opciones distintas y `correcta` entre 0 y 3; las de huecos, exactamente un `___`; ninguna opción es "todas/ninguna de las anteriores".
- **Variedad (límites de la tabla del anexo `variedad.md`):**
  - como mucho 2 enunciados con las mismas 3 primeras palabras;
  - la correcta es la opción más larga en el 30 % de las preguntas o menos, y en cada pregunta la opción más larga mide como mucho el doble que la más corta;
  - ninguna letra es la correcta en más del 35 % de las preguntas y no hay rachas de 3 iguales; con 8 o más preguntas de opciones, las cuatro letras tampoco pueden salir exactamente las mismas veces;
  - en verdadero/falso, entre el 40 y el 60 % son verdaderas;
  - ningún nivel cognitivo ni ninguna técnica de distractor pasa del 40 %;
  - negativas, como mucho el 10 %, con "NO" en mayúsculas;
  - "siempre/nunca/todos/ninguno" no aparecen solo en los distractores;
  - ninguna palabra del enunciado se repite solo en la correcta, y ningún enunciado termina en artículo;
  - como mucho 2 explicaciones empiezan con las mismas 3 palabras;
  - todas las secciones tienen al menos una pregunta.
- Cuenta cada límite sobre el test completo antes de entregarlo e indica en la entrega si queda alguno sin cumplir y por qué.""",

    "reescritor-estilo": """\
`scripts/analizar.py` mide naturalidad y fidelidad; `scripts/docx_io.py` lee y escribe Word. Sin código, compara el original con la reescritura así:

- **Fidelidad (errores, se corrigen siempre):** cada cifra, fecha, nombre propio, cita entre comillas y referencia (Autor, año) del original aparece igual en la reescritura. Repásalo elemento por elemento, no de memoria.
- **Muletillas y tópicos:** ninguna frase de las listas del anexo `patrones-ia.md` (secciones de muletillas, frases hechas y cierres).
- **Cierre:** el último párrafo no resume lo anterior ni termina apelando a los expertos, al futuro o a "un equilibrio".
- **Ritmo:** con 5 frases o más, las longitudes tienen que variar de verdad. Debe haber frases de menos de 8 palabras y alguna de más de 25, y no todas en la franja de 15-25.
- **Arranques:** como mucho 2 frases, y 2 párrafos, empiezan por la misma palabra (o por el mismo artículo + palabra).
- **Conectores:** ninguno de la lista de conectores aparece más de 2 veces por cada 300 palabras.
- **Tríadas:** como mucho 1 enumeración de exactamente tres elementos por cada 200 palabras.
- **Párrafos:** de longitudes claramente distintas, y como mucho la mitad acaba en frase-resumen.
- **Puntuación:** como mucho 1 guion largo y 1 exclamación por cada 100 palabras.
- **Word:** sin código, devuelve el texto con los títulos marcados (`#`, `##`) para pegarlo en el documento original.
- En la entrega, una línea con el resultado de esta revisión ("Fidelidad: OK; queda una tríada, que es la enumeración real de la norma").""",
}

GENERICO = "Esta skill usa scripts. Si no puedes ejecutar código, aplica a mano las comprobaciones que describe cada sección."


def leer_frontmatter(texto: str) -> tuple[dict[str, str], str]:
    m = re.match(r"^---\n(.*?)\n---\n", texto, re.S)
    if not m:
        return {}, texto
    campos, clave = {}, None
    for linea in m.group(1).splitlines():
        cab = re.match(r"^([\w-]+):\s*(.*)$", linea)
        if cab:
            clave, valor = cab.group(1), cab.group(2).strip()
            campos[clave] = "" if valor in (">-", ">", "|", "|-") else valor
        elif clave and linea.startswith(" "):
            campos[clave] = (campos[clave] + " " + linea.strip()).strip()
    return campos, texto[m.end():]


def bajar_titulos(texto: str) -> str:
    """Baja un nivel los títulos Markdown (fuera de bloques de código)."""
    salida, en_codigo = [], False
    for linea in texto.splitlines():
        if linea.lstrip().startswith("```"):
            en_codigo = not en_codigo
        if not en_codigo and re.match(r"^#{1,5} ", linea):
            linea = "#" + linea
        salida.append(linea)
    return "\n".join(salida)


def apuntar_a_anexos(texto: str) -> str:
    texto = re.sub(r"`(references|assets)/([\w./-]+)`", r"el anexo `\2`", texto)
    return re.sub(r"(?<![`\w/])(references|assets)/([\w-]+\.\w+)", r"el anexo `\2`", texto)


def generar(skill: Path) -> str:
    campos, cuerpo = leer_frontmatter((skill / "SKILL.md").read_text(encoding="utf-8"))
    nombre = campos.get("name", skill.name)
    # La sección «Ejemplos» remite a examples/, que no viaja con el portable.
    cuerpo = re.sub(r"\n## Ejemplos?\b.*?(?=\n## |\Z)", "\n", cuerpo, flags=re.S)
    partes = [
        f"# {nombre} (versión portable)",
        "",
        "<!-- Generado por tools/generar_portables.py a partir de SKILL.md, references/ y assets/. "
        "No lo edites a mano: regenéralo. -->",
        "",
        "Estas son las instrucciones completas de la skill, en un solo texto para usarlas en un chat "
        "sin soporte de skills (un GPT, un Gem o un proyecto). Donde se habla de scripts (`scripts/…`): "
        "si puedes ejecutar código pero no tienes los scripts, o no puedes ejecutar código, aplica a mano "
        "las comprobaciones de la sección «Si no puedes ejecutar código», al final de las instrucciones. "
        "Los archivos de referencia van como anexos al final.",
        "",
        f"**Cuándo usarla:** {campos.get('description', '')}",
        "",
        apuntar_a_anexos(bajar_titulos(cuerpo.strip())),
        "",
        "## Si no puedes ejecutar código",
        "",
        MANUAL.get(nombre, GENERICO),
    ]
    for carpeta in ("references", "assets"):
        directorio = skill / carpeta
        if not directorio.is_dir():
            continue
        for f in sorted(directorio.iterdir()):
            if not f.is_file() or f.suffix.lower() not in EXT_ASSETS:
                continue
            contenido = f.read_text(encoding="utf-8").strip()
            partes += ["", "---", "", f"## Anexo: `{f.name}`", ""]
            if f.suffix.lower() == ".md":
                partes.append(apuntar_a_anexos(bajar_titulos(bajar_titulos(contenido))))
            else:
                valla = "````" if "```" in contenido else "```"
                partes += [f"{valla}{EXT_ASSETS[f.suffix.lower()]}", contenido, valla]
    return "\n".join(partes).rstrip() + "\n"


def huella(skill: Path) -> str:
    """SHA-256 abreviado del SKILL.md, con finales de línea normalizados."""
    return hashlib.sha256((skill / "SKILL.md").read_bytes().replace(b"\r\n", b"\n")).hexdigest()[:12]


def leer_lite(skill: Path) -> tuple[str | None, str]:
    """Devuelve (huella revisada, texto) de tools/lite/<skill>.md."""
    ruta = LITE / f"{skill.name}.md"
    if not ruta.is_file():
        raise FileNotFoundError(f"falta tools/lite/{skill.name}.md con el texto del portable lite")
    texto = ruta.read_text(encoding="utf-8")
    m = re.match(r"<!-- huella-skill: (\w+) -->\n", texto)
    return (m.group(1) if m else None), texto[m.end():].strip() if m else texto.strip()


def generar_lite(skill: Path) -> str:
    campos, _ = leer_frontmatter((skill / "SKILL.md").read_text(encoding="utf-8"))
    nombre = campos.get("name", skill.name)
    _, cuerpo = leer_lite(skill)
    partes = [
        f"# {nombre} (instrucciones esenciales)",
        "",
        "<!-- Generado por tools/generar_portables.py a partir de tools/lite/. No lo edites a mano. -->",
        "",
        "Versión corta de la skill, para el campo de instrucciones. Las reglas completas, las listas y "
        f"las plantillas están en el archivo adjunto `{NOMBRE}`: consúltalo siempre que una regla de aquí "
        "remita a él o necesites un detalle que aquí no aparece. Si este texto y el adjunto discrepan, manda el adjunto.",
        "",
        f"**Cuándo usarla:** {campos.get('description', '')}",
        "",
        cuerpo,
    ]
    return "\n".join(partes).rstrip() + "\n"


def problemas_lite(skill: Path) -> list[str]:
    revisada, _ = leer_lite(skill)
    problemas = []
    if revisada != huella(skill):
        problemas.append(f"{skill.name}: el SKILL.md ha cambiado desde que se revisó el lite "
                         f"(huella {revisada} → {huella(skill)}). Revisa tools/lite/{skill.name}.md "
                         "y actualiza su primera línea.")
    largo = len(generar_lite(skill))
    if largo > LIMITE_LITE:
        problemas.append(f"{skill.name}: el portable lite tiene {largo} caracteres (máx. {LIMITE_LITE}).")
    return problemas


def skills() -> list[Path]:
    return sorted(d for d in (RAIZ / "skills").iterdir() if d.is_dir() and (d / "SKILL.md").is_file())


def escribir(destino: Path, texto: str) -> None:
    with open(destino, "w", encoding="utf-8", newline="\n") as f:  # write_text(newline=) es 3.10+
        f.write(texto)
    print(f"{destino.relative_to(RAIZ).as_posix()}: {len(texto):,} caracteres".replace(",", "."))


def main(argv: list[str]) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    comprobar = "--comprobar" in argv[1:]
    desfasados, avisos = [], []
    for skill in skills():
        avisos += problemas_lite(skill)
        for nombre, nuevo in ((NOMBRE, generar(skill)), (NOMBRE_LITE, generar_lite(skill))):
            destino = skill / nombre
            if comprobar:
                actual = destino.read_text(encoding="utf-8") if destino.is_file() else None
                if actual != nuevo:
                    desfasados.append(f"{skill.name}/{nombre}")
            else:
                escribir(destino, nuevo)
    for a in avisos:
        print(f"Revisar: {a}")
    if comprobar:
        if desfasados:
            print("Portables desactualizados: " + ", ".join(desfasados))
            print("Regenéralos con: python tools/generar_portables.py")
        if desfasados or avisos:
            return 1
        print(f"Portables al día: {len(skills())} skills (completo y lite).")
    return 1 if avisos else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
