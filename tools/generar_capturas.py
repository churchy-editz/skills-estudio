#!/usr/bin/env python3
"""Genera las capturas del README en docs/img/ con Chrome (o Edge) headless.

Uso:
    python tools/generar_capturas.py [--chrome RUTA]

Capturas (1200 px de ancho, PNG optimizado con Pillow si está instalado):
  apuntes-hemostasia.png, apuntes-transicion.png  los dos HTML de ejemplo
  test-pregunta.png    una pregunta respondida, con la explicación visible
  test-resultado.png   la pantalla final con nota y desglose por sección
  reescritor-antes-despues.png  email original marcado ⟦ ⟧ frente a la reescritura

El test se captura desde una copia temporal: se fija la semilla del barajado
(siempre salen las mismas preguntas) y un script responde por el usuario.
No modifica ningún archivo de las skills.
"""
from __future__ import annotations

import argparse
import html
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
DESTINO = RAIZ / "docs" / "img"
ANCHO = 1200
MAX_BYTES = 300 * 1024

CANDIDATOS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
]

SEMILLA = """<script>
(function () {  /* barajado reproducible para las capturas */
  var s = 7;
  Math.random = function () { s = (s * 16807) % 2147483647; return (s - 1) / 2147483646; };
})();
</script>"""

# Responde por el usuario. Modo "pregunta": acierta hasta llegar a una pregunta
# de opción múltiple y la falla, para que se vean la correcta y la explicación.
# Modo "resultado": responde todo con un patrón fijo de aciertos, fallos y blancos.
CONDUCTOR = """<script>
(function () {
  var datos = JSON.parse(document.getElementById("datos-test").textContent);
  var modo = location.hash.slice(1);
  function limpio(t) { return String(t).replace(/_{3,}/g, "").replace(/\\s+/g, " ").trim(); }
  function actual() {
    var e = limpio(document.getElementById("enunciado").textContent);
    return datos.preguntas.filter(function (p) { return limpio(p.enunciado) === e; })[0];
  }
  function responder(p, bien) {
    if (p.tipo === "huecos") {
      document.getElementById("campo-hueco").value = bien ? p.correcta[0] : "no lo sé";
      document.getElementById("btn-comprobar").click();
      return;
    }
    var correcta = p.tipo === "vf" ? (p.correcta ? "Verdadero" : "Falso") : p.opciones[p.correcta];
    var botones = document.querySelectorAll("#respuestas .opcion");
    for (var i = 0; i < botones.length; i++) {
      var t = botones[i].querySelector(".texto").textContent;
      if ((t === correcta) === bien) { botones[i].click(); return; }
    }
  }
  var n = datos.preguntas.length;
  for (var i = 0; i < n; i++) {
    var p = actual();
    if (modo === "pregunta") {
      if (p.tipo === "multiple" && i > 0) { responder(p, false); break; }
      responder(p, true);
    } else {
      if (i % 5 === 2) document.getElementById("btn-blanco").click();
      else responder(p, i % 4 !== 3);
    }
    document.getElementById("btn-siguiente").click();
  }
  if (document.activeElement) document.activeElement.blur();
  window.scrollTo(0, 0);
})();
</script>"""

ANTES_DESPUES = """<!doctype html>
<html lang="es"><head><meta charset="utf-8"><title>Antes y después</title>
<style>
  body {{ margin: 0; font: 16px/1.55 "Segoe UI", system-ui, sans-serif; color: #1f2328; background: #f6f7f9; }}
  .marco {{ display: grid; grid-template-columns: 1fr 1fr; gap: 24px; padding: 28px; }}
  h2 {{ font-size: 15px; letter-spacing: .04em; text-transform: uppercase; margin: 0 0 12px; color: #57606a; }}
  .caja {{ background: #fff; border: 1px solid #d0d7de; border-radius: 10px; padding: 20px 24px; }}
  p {{ margin: 0 0 12px; }}
  mark {{ background: #ffe1a8; color: #6b3a00; border-radius: 3px; padding: 0 2px; }}
  .pie {{ grid-column: 1 / -1; font-size: 14px; color: #57606a; }}
</style></head>
<body><div class="marco">
  <section><h2>Original (tics marcados)</h2><div class="caja">{antes}</div></section>
  <section><h2>Reescritura</h2><div class="caja">{despues}</div></section>
  <p class="pie">{pie}</p>
</div></body></html>"""


def buscar_navegador(explicito: str | None) -> str:
    for c in [explicito, os.environ.get("CHROME")] + CANDIDATOS:
        if c and Path(c).is_file():
            return c
    for nombre in ("google-chrome", "chromium", "chromium-browser", "chrome", "msedge"):
        ruta = shutil.which(nombre)
        if ruta:
            return ruta
    sys.exit("No encuentro Chrome, Chromium ni Edge. Pásalo con --chrome RUTA o la variable CHROME.")


def capturar(navegador: str, pagina: Path, salida: Path, alto: int, ancla: str = "") -> None:
    with tempfile.TemporaryDirectory() as perfil:
        subprocess.run([
            navegador, "--headless=new", "--disable-gpu", "--hide-scrollbars",
            "--force-device-scale-factor=1", f"--window-size={ANCHO},{alto}",
            "--virtual-time-budget=4000", f"--user-data-dir={perfil}",
            f"--screenshot={salida}", pagina.resolve().as_uri() + ancla,
        ], check=True, capture_output=True, timeout=120)


def optimizar(png: Path) -> None:
    try:
        from PIL import Image
    except ImportError:
        print("  (sin Pillow: PNG sin optimizar; pip install pillow)")
        return
    with Image.open(png) as img:
        reducida = img.convert("RGB").quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    reducida.save(png, optimize=True)


def parrafos_html(texto: str, marcado: bool) -> str:
    bloques = []
    for bloque in re.split(r"\n\s*\n", texto.strip()):
        t = html.escape(bloque).replace("\n", "<br>")
        if marcado:
            t = re.sub(r"⟦(.+?)⟧", r"<mark>⟦\1⟧</mark>", t, flags=re.S)
        bloques.append(f"<p>{t}</p>")
    return "\n".join(bloques)


def main(argv: list[str]) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--chrome")
    a = ap.parse_args(argv[1:])
    navegador = buscar_navegador(a.chrome)
    DESTINO.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        trabajos = [
            (RAIZ / "skills/creador-apuntes/examples/apuntes-hemostasia.html", "apuntes-hemostasia.png", 1300, ""),
            (RAIZ / "skills/creador-apuntes/examples/apuntes-transicion.html", "apuntes-transicion.png", 1300, ""),
        ]

        fuente = (RAIZ / "skills/creador-tests/examples/test-hemostasia.html").read_text(encoding="utf-8")
        test = fuente.replace("<head>", "<head>\n" + SEMILLA, 1)
        cierre = test.rfind("</body>")
        test = test[:cierre] + CONDUCTOR + "\n" + test[cierre:]
        pagina_test = tmp / "test.html"
        pagina_test.write_text(test, encoding="utf-8")
        trabajos += [(pagina_test, "test-pregunta.png", 860, "#pregunta"),
                     (pagina_test, "test-resultado.png", 780, "#resultado")]

        ej = RAIZ / "skills/reescritor-estilo/examples"
        informe = (ej / "email-informe.txt").read_text(encoding="utf-8")
        nat = re.search(r"Naturalidad: ([\d,]+)/10 \(original: ([\d,]+)/10\)", informe)
        fid = re.search(r"^FIDELIDAD: (.+)$", informe, re.M)
        pie = " · ".join(x for x in (
            "Informe de analizar.py",
            f"naturalidad {nat.group(2)} → {nat.group(1)} sobre 10" if nat else "",
            f"fidelidad {fid.group(1)}" if fid else "") if x)
        comparacion = tmp / "antes-despues.html"
        comparacion.write_text(ANTES_DESPUES.format(
            antes=parrafos_html((ej / "email-original-marcado.md").read_text(encoding="utf-8"), True),
            despues=parrafos_html((ej / "email-reescrito.md").read_text(encoding="utf-8"), False),
            pie=html.escape(pie)), encoding="utf-8")
        trabajos.append((comparacion, "reescritor-antes-despues.png", 680, ""))

        for pagina, nombre, alto, ancla in trabajos:
            salida = DESTINO / nombre
            capturar(navegador, pagina, salida, alto, ancla)
            optimizar(salida)
            kb = salida.stat().st_size / 1024
            aviso = "" if salida.stat().st_size <= MAX_BYTES else "  ← más de 300 KB"
            print(f"{salida.relative_to(RAIZ).as_posix()}: {kb:.0f} KB{aviso}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
