"""Tests de scripts/html_a_docx.py con los dos ejemplos de examples/.

Ejecutar desde la carpeta creador-apuntes (o la raíz del repo):
    python -m unittest discover -s creador-apuntes/tests -v
También funcionan con pytest.
"""
from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from docx import Document

RAIZ = Path(__file__).resolve().parents[1]
SCRIPT = RAIZ / "scripts" / "html_a_docx.py"
EJEMPLOS = sorted((RAIZ / "examples").glob("apuntes-*.html"))
ETIQUETAS = {"DEFINICIÓN": "def", "EJEMPLO": "ejemplo", "OJO": "ojo", "DATO CLAVE": "clave"}

_spec = importlib.util.spec_from_file_location("html_a_docx", SCRIPT)
html_a_docx = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(html_a_docx)


def _relleno(celda) -> str | None:
    valores = celda._tc.xpath("./w:tcPr/w:shd/@w:fill")
    return valores[0].upper() if valores else None


def _cajas(doc) -> list:
    """Tablas de una celda cuya primera línea es una etiqueta de caja."""
    cajas = []
    for tabla in doc.tables:
        if len(tabla.rows) == 1 and len(tabla.columns) == 1:
            celda = tabla.cell(0, 0)
            etiqueta = celda.paragraphs[0].text.strip()
            if etiqueta in ETIQUETAS:
                cajas.append((ETIQUETAS[etiqueta], celda))
    return cajas


class TestEjemplos(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.docs = {}
        cls.htmls = {}
        for html in EJEMPLOS:
            salida = Path(cls.tmp.name) / f"{html.stem}.docx"
            html_a_docx.convertir(html, salida)
            cls.docs[html.stem] = Document(str(salida))
            cls.htmls[html.stem] = html.read_text(encoding="utf-8")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_hay_dos_ejemplos(self):
        self.assertEqual(len(EJEMPLOS), 2, EJEMPLOS)

    def test_titulos_con_estilo_de_word(self):
        for nombre, doc in self.docs.items():
            with self.subTest(ejemplo=nombre):
                estilos = [p.style.name for p in doc.paragraphs if p.text.strip()]
                self.assertEqual(estilos.count("Heading 1"), 1)
                self.assertGreaterEqual(estilos.count("Heading 2"), 1)
                h2_html = len(re.findall(r"<h2\b", self.htmls[nombre]))
                self.assertEqual(estilos.count("Heading 2"), h2_html)

    def test_hay_tablas_de_contenido(self):
        for nombre, doc in self.docs.items():
            with self.subTest(ejemplo=nombre):
                multicelda = [t for t in doc.tables if len(t.rows) * len(t.columns) > 1]
                self.assertGreaterEqual(len(multicelda), 1)

    def test_cajas_con_etiqueta_y_color_de_la_paleta(self):
        for nombre, doc in self.docs.items():
            with self.subTest(ejemplo=nombre):
                html = self.htmls[nombre]
                cajas_html = re.findall(r'class="caja (def|ejemplo|ojo|clave)"', html)
                cajas_docx = _cajas(doc)
                self.assertEqual(sorted(t for t, _ in cajas_docx), sorted(cajas_html))
                paleta = html_a_docx.leer_paleta(html)
                for tipo, celda in cajas_docx:
                    esperado = html_a_docx.mezcla(paleta[tipo], paleta["fondo"])
                    self.assertEqual(_relleno(celda), esperado, f"caja {tipo}")
                    self.assertGreater(len(celda.paragraphs), 1, f"caja {tipo} sin contenido")

    def test_no_se_pierde_texto(self):
        for nombre, doc in self.docs.items():
            with self.subTest(ejemplo=nombre):
                texto = " ".join(p.text for p in doc.paragraphs)
                for tabla in doc.tables:
                    for fila in tabla.rows:
                        texto += " " + " ".join(c.text for c in fila.cells)
                texto = re.sub(r"\s+", " ", texto)
                for frase in re.findall(r"<p>([^<]{20,})</p>", self.htmls[nombre]):
                    self.assertIn(re.sub(r"\s+", " ", frase.strip()), texto)

    def test_listas_numeradas_reinician(self):
        doc = self.docs["apuntes-hemostasia"]
        num_ids = {
            p._p.xpath("./w:pPr/w:numPr/w:numId/@w:val")[0]
            for p in doc.paragraphs
            if p.style.name == "List Number" and p._p.xpath("./w:pPr/w:numPr/w:numId/@w:val")
        }
        self.assertEqual(len(num_ids), 2, "pasos y cadena deben numerarse por separado")

    def test_linea_de_tiempo_es_tabla(self):
        doc = self.docs["apuntes-transicion"]
        hitos = len(re.findall(r'class="fecha"', self.htmls["apuntes-transicion"]))
        tablas = [t for t in doc.tables if t.cell(0, 0).text == "Fecha"]
        self.assertEqual(len(tablas), 1)
        self.assertEqual(len(tablas[0].rows), hitos + 1)

    def test_ejemplos_con_paleta_y_estructura_distintas(self):
        a, b = (html_a_docx.leer_paleta(h) for h in self.htmls.values())
        self.assertNotEqual(a["def"], b["def"])
        self.assertNotEqual(a["fuente"], b["fuente"])
        self.assertIn('class="pasos"', self.htmls["apuntes-hemostasia"])
        self.assertIn('class="linea-tiempo"', self.htmls["apuntes-transicion"])


class TestLineaDeComandos(unittest.TestCase):
    def test_sin_argumentos_muestra_uso(self):
        r = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 2)
        self.assertIn("Uso:", r.stderr)

    def test_convierte_por_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            salida = Path(tmp) / "salida.docx"
            r = subprocess.run([sys.executable, str(SCRIPT), str(EJEMPLOS[0]), str(salida)],
                               capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertTrue(salida.is_file())


if __name__ == "__main__":
    unittest.main()
