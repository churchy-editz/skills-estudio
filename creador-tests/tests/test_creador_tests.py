"""Tests de los scripts de creador-tests.

Ejecutar desde la raíz del repo (o desde creador-tests):
    python -m unittest discover -s creador-tests/tests -v
También funcionan con pytest.
"""
from __future__ import annotations

import contextlib
import copy
import csv
import importlib.util
import io
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SCRIPTS = RAIZ / "scripts"
DATOS = Path(__file__).resolve().parent / "datos"
MOLDE = DATOS / "molde.json"
CORRECTO = DATOS / "correcto.json"
EJEMPLO = RAIZ / "examples" / "test-hemostasia.json"


def cargar_modulo(nombre: str):
    spec = importlib.util.spec_from_file_location(nombre, SCRIPTS / f"{nombre}.py")
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


validar = cargar_modulo("validar")
generar_html = cargar_modulo("generar_html")
exportar = cargar_modulo("exportar")


def leer(ruta: Path) -> dict:
    return json.loads(ruta.read_text(encoding="utf-8"))


def ejecutar(script: str, *args) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script), *map(str, args)],
        capture_output=True, text=True, encoding="utf-8",
    )


class TestValidar(unittest.TestCase):
    def test_molde_dispara_todos_los_avisos(self):
        errores, avisos, nota, _ = validar.analizar(leer(MOLDE))
        self.assertEqual(errores, [])
        todas = {c for c, _ in validar.CATEGORIAS}
        self.assertEqual(set(avisos), todas, f"faltan: {todas - set(avisos)}")
        self.assertEqual(nota, 0)

    def test_molde_identifica_ids(self):
        _, avisos, _, _ = validar.analizar(leer(MOLDE))
        self.assertIn("m01, m02, m03", avisos["inicio_enunciado"][0])
        self.assertIn("m01 y m03", avisos["similitud"][0])
        self.assertTrue(any("m06" in a for a in avisos["pista_gramatical"]))
        self.assertTrue(any("m05" in a and "mayúsculas" in a for a in avisos["negativas"]))

    def test_correcto_sin_avisos(self):
        errores, avisos, nota, _ = validar.analizar(leer(CORRECTO))
        self.assertEqual((errores, avisos, nota), ([], {}, 10.0))

    def test_ejemplo_sin_avisos(self):
        errores, avisos, nota, _ = validar.analizar(leer(EJEMPLO))
        self.assertEqual((errores, avisos, nota), ([], {}, 10.0))

    def _errores_con(self, cambio) -> list[str]:
        datos = copy.deepcopy(leer(CORRECTO))
        cambio(datos["preguntas"])
        return validar.errores_esquema(datos)

    def test_error_todas_las_anteriores(self):
        err = self._errores_con(lambda ps: ps[0]["opciones"].__setitem__(3, "Todas las anteriores"))
        self.assertTrue(any("prohibida" in e for e in err))

    def test_error_ninguna_de_las_anteriores(self):
        err = self._errores_con(lambda ps: ps[0]["opciones"].__setitem__(0, "Ninguna de las anteriores"))
        self.assertTrue(any("prohibida" in e for e in err))

    def test_error_numero_de_opciones(self):
        err = self._errores_con(lambda ps: ps[0]["opciones"].pop())
        self.assertTrue(any("exactamente 4" in e for e in err))

    def test_error_opciones_repetidas(self):
        err = self._errores_con(lambda ps: ps[0]["opciones"].__setitem__(3, "condensación"))
        self.assertTrue(any("repetidas" in e for e in err))

    def test_error_mas_de_una_correcta(self):
        err = self._errores_con(lambda ps: ps[0].__setitem__("correcta", [0, 1]))
        self.assertTrue(any("UN índice" in e for e in err))

    def test_error_esquema(self):
        def romper(ps):
            del ps[1]["explicacion"]
            ps[2]["tipo"] = "abierta"
            ps[4].pop("contexto")
        err = self._errores_con(romper)
        self.assertTrue(any("explicacion" in e for e in err))
        self.assertTrue(any("'tipo'" in e for e in err))
        self.assertTrue(any("contexto" in e for e in err))

    def test_codigos_de_salida(self):
        self.assertEqual(ejecutar("validar.py", CORRECTO).returncode, 0)
        r = ejecutar("validar.py", MOLDE)
        self.assertEqual(r.returncode, 2)
        self.assertIn("Variedad: 0/10", r.stdout)
        with tempfile.TemporaryDirectory() as tmp:
            malo = Path(tmp) / "malo.json"
            datos = leer(CORRECTO)
            datos["preguntas"][0]["opciones"][2] = "Ninguna de las anteriores"
            malo.write_text(json.dumps(datos), encoding="utf-8")
            self.assertEqual(ejecutar("validar.py", malo).returncode, 1)


def datos_incrustados(html_texto: str) -> dict:
    m = re.search(r'<script type="application/json" id="datos-test">(.*?)</script>', html_texto, re.S)
    return json.loads(m.group(1))


class TestGenerarHtml(unittest.TestCase):
    def test_incluye_todas_las_preguntas(self):
        for fuente in (EJEMPLO, CORRECTO, MOLDE):
            with self.subTest(fuente=fuente.name), tempfile.TemporaryDirectory() as tmp:
                salida = generar_html.generar(fuente, Path(tmp) / "t.html", "ciencias")
                texto = salida.read_text(encoding="utf-8")
                original = leer(fuente)
                incrustado = datos_incrustados(texto)
                self.assertEqual(incrustado, original)
                self.assertEqual([p["id"] for p in incrustado["preguntas"]], [p["id"] for p in original["preguntas"]])

    def test_paleta_y_autocontenido(self):
        with tempfile.TemporaryDirectory() as tmp:
            texto = generar_html.generar(EJEMPLO, Path(tmp) / "t.html", "Biología").read_text(encoding="utf-8")
        self.assertIn("--def: #0b6e69;", texto)
        self.assertNotIn("/*PALETA*/", texto)
        self.assertNotIn("/*DATOS*/", texto)
        self.assertIsNone(re.search(r'(src|href)="https?:', texto))
        self.assertIn("@media print", texto)

    def test_no_rompe_script_con_etiquetas(self):
        datos = leer(CORRECTO)
        datos["preguntas"][0]["explicacion"] = "Ojo con </script><b>esto</b>."
        with tempfile.TemporaryDirectory() as tmp:
            entrada = Path(tmp) / "x.json"
            entrada.write_text(json.dumps(datos, ensure_ascii=False), encoding="utf-8")
            texto = generar_html.generar(entrada, Path(tmp) / "x.html").read_text(encoding="utf-8")
        self.assertEqual(datos_incrustados(texto)["preguntas"][0]["explicacion"], "Ojo con </script><b>esto</b>.")

    def test_paleta_desconocida_y_json_con_errores(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(ejecutar("generar_html.py", EJEMPLO, Path(tmp) / "t.html", "--paleta", "neon").returncode, 2)
            datos = leer(CORRECTO)
            datos["preguntas"][0]["opciones"].pop()
            malo = Path(tmp) / "malo.json"
            malo.write_text(json.dumps(datos), encoding="utf-8")
            self.assertEqual(ejecutar("generar_html.py", malo, Path(tmp) / "m.html").returncode, 1)


class TestExportar(unittest.TestCase):
    def test_cada_formato(self):
        formatos = ["gift", "kahoot", "anki", "quizlet"]
        try:
            import docx  # noqa: F401
            formatos.append("docx")
        except ImportError:
            pass
        with tempfile.TemporaryDirectory() as tmp:
            for formato in formatos:
                with self.subTest(formato=formato):
                    salida = Path(tmp) / f"t.{formato}"
                    r = ejecutar("exportar.py", EJEMPLO, "--formato", formato, "-o", salida)
                    self.assertEqual(r.returncode, 0, r.stderr)
                    self.assertGreater(salida.stat().st_size, 0)

    def test_gift_escapa_caracteres_especiales(self):
        self.assertEqual(exportar.gift_escapar("a~b=c#d{e}f:g\\h"), "a\\~b\\=c\\#d\\{e\\}f\\:g\\\\h")
        datos = leer(CORRECTO)
        datos["preguntas"][0]["enunciado"] = "¿Cuánto es 2+2=? {nota: #1 ~ aprox}"
        gift = exportar.a_gift(datos)
        self.assertIn("2+2\\=? \\{nota\\: \\#1 \\~ aprox\\}", gift)
        self.assertIn("~%-33.33333%Condensación", gift)  # penalización 1/3
        self.assertIn("{=precipitación =lluvia", gift)
        self.assertIn("{TRUE####", gift)

    def test_gift_todas_las_preguntas(self):
        gift = exportar.a_gift(leer(EJEMPLO))
        for p in leer(EJEMPLO)["preguntas"]:
            self.assertIn(f"::{p['id']}::", gift)

    def test_kahoot_respeta_plantilla_y_limites(self):
        avisos = io.StringIO()
        with contextlib.redirect_stderr(avisos):
            texto = exportar.a_kahoot(leer(EJEMPLO))
        self.assertIn("p11: pregunta de", avisos.getvalue())
        self.assertIn("p06: opción A de", avisos.getvalue())
        self.assertIn("Kahoot: exportadas 7 de 12; omitidas 2 de huecos, que Kahoot no admite (p03, p08); "
                      "omitidas 3 por superar los límites (p06, p10, p11).", avisos.getvalue())
        filas = list(csv.reader(io.StringIO(texto)))
        self.assertEqual(filas[0], exportar.KAHOOT_CABECERA)
        for fila in filas[1:]:
            self.assertLessEqual(len(fila[0]), 120)
            self.assertTrue(all(len(c) <= 75 for c in fila[1:5]))
            self.assertIn(fila[6], {"1", "2", "3", "4"})
        self.assertNotIn("___", texto)  # los huecos se omiten

    def test_anki_y_quizlet_una_linea_por_pregunta(self):
        datos = leer(EJEMPLO)
        anki = [l for l in exportar.a_anki(datos).splitlines() if not l.startswith("#")]
        quizlet = exportar.a_quizlet(datos).splitlines()
        for lineas in (anki, quizlet):
            self.assertEqual(len(lineas), len(datos["preguntas"]))
            self.assertTrue(all(l.count("\t") == 1 for l in lineas))

    @unittest.skipUnless(importlib.util.find_spec("docx"), "python-docx no instalado")
    def test_docx_con_soluciones(self):
        from docx import Document
        with tempfile.TemporaryDirectory() as tmp:
            salida = exportar.exportar(EJEMPLO, "docx", Path(tmp) / "t.docx")
            texto = "\n".join(p.text for p in Document(str(salida)).paragraphs)
        self.assertIn("Soluciones", texto)
        self.assertIn("von Willebrand", texto)


if __name__ == "__main__":
    unittest.main()
