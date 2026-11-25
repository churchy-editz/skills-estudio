"""Tests de los scripts de reescritor-estilo.

Ejecutar desde la raíz del repo (o desde reescritor-estilo):
    python -m unittest discover -s reescritor-estilo/tests -v
También funcionan con pytest.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SCRIPTS = RAIZ / "scripts"
DATOS = Path(__file__).resolve().parent / "datos"
EJEMPLOS = RAIZ / "examples"


def cargar_modulo(nombre: str):
    spec = importlib.util.spec_from_file_location(nombre, SCRIPTS / f"{nombre}.py")
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


analizar = cargar_modulo("analizar")
HAY_DOCX = importlib.util.find_spec("docx") is not None


def leer(nombre: str) -> str:
    return (DATOS / nombre).read_text(encoding="utf-8")


def ejecutar(script: str, *args) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script), *map(str, args)],
        capture_output=True, text=True, encoding="utf-8",
    )


class TestPatrones(unittest.TestCase):
    def test_al_menos_60_entradas_por_idioma(self):
        pat = analizar.cargar_patrones()
        for idioma in ("es", "en"):
            self.assertGreaterEqual(pat[idioma]["entradas"], 60, idioma)
            for clase in ("muletillas", "conectores", "cierres"):
                self.assertTrue(pat[idioma][clase], f"{idioma}: {clase} vacío")

    def test_al_menos_40_topicos_por_idioma(self):
        pat = analizar.cargar_patrones()
        for idioma in ("es", "en"):
            self.assertGreaterEqual(pat[idioma]["filas"]["topicos"], 40, idioma)
            self.assertTrue(pat[idioma]["apelaciones"], f"{idioma}: apelaciones vacío")
        for frase in ("luces y sombras", "herramienta valiosa", "lo mejor de ambos mundos", "una nueva realidad",
                      "un antes y un después", "cada vez más", "en la era digital", "no es oro todo lo que reluce",
                      "arma de doble filo", "a día de hoy", "muchos expertos", "en definitiva", "abrir un debate"):
            self.assertIn(frase, pat["es"]["topicos"])
        for frase in ("double-edged sword", "game changer", "best of both worlds", "in this day and age", "experts agree"):
            self.assertIn(frase, pat["en"]["topicos"])

    def test_solapes_cuentan_una_vez(self):
        pat = analizar.cargar_patrones()["es"]
        m = analizar.medir("Vivimos en un mundo cada vez más rápido. Y cada vez más caro.", "es", pat)
        self.assertEqual(m["muletillas"], {"en un mundo cada vez más": 1})
        self.assertEqual(m["topicos"], {"cada vez más": 1})

    def test_patron_con_hueco(self):
        r = analizar.compilar("no solo… sino también")
        self.assertTrue(r.search("no solo mejora la conciliación, sino también la productividad"))
        self.assertFalse(r.search("no solo eso"))


class TestNaturalidad(unittest.TestCase):
    def setUp(self):
        self.r = analizar.analizar(leer("texto-natural.md"), leer("texto-ia.md"), idioma="es")
        self.av = self.r["avisos"]

    def test_texto_ia_dispara_todas_las_categorias(self):
        todas = {c for c, _ in analizar.CATEGORIAS}
        self.assertEqual(set(self.av), todas, f"faltan: {todas - set(self.av)}")
        self.assertEqual(self.r["naturalidad"], 0.0)

    def test_detalle_de_cada_patron(self):
        def unido(categoria):
            return " | ".join(self.av[categoria])
        self.assertIn("juega un papel crucial", unido("muletillas"))
        self.assertIn("es importante destacar", unido("muletillas"))
        self.assertIn("en resumen", unido("muletillas"))
        self.assertIn("ritmo plano", unido("ritmo"))
        self.assertIn("«además»", unido("arranques"))
        self.assertIn("«el sistema»", unido("arranques"))
        self.assertIn("«además» ×3", unido("conectores"))
        self.assertIn("3 enumeraciones de 3", unido("triadas"))
        self.assertIn("longitud parecida", unido("parrafos"))
        self.assertIn("3 de 3 párrafos acaban en frase-resumen", unido("parrafos"))
        self.assertIn("guiones largos", unido("puntuacion"))
        self.assertIn("exclamaciones", unido("puntuacion"))

    def test_texto_natural_sin_avisos(self):
        r = analizar.analizar(leer("texto-natural.md"), leer("texto-natural.md"), idioma="es")
        self.assertEqual((r["avisos"], r["naturalidad"], r["errores"]), ({}, 10.0, []))

    def test_ingles(self):
        texto = ("It's worth noting that our team plays a crucial role here. Moreover, we delve into "
                 "the data. Moreover, the results are seamless. Moreover, it works.")
        r = analizar.analizar(texto, texto, idioma="en")
        self.assertIn("muletillas", r["avisos"])
        self.assertTrue(any("moreover" in a for a in r["avisos"]["conectores"]))

    def test_lista_de_cuatro_no_es_triada(self):
        frase = "Mejora la conciliación, la productividad, la satisfacción y el compromiso."
        self.assertEqual(analizar.triadas(frase, "es"), [])
        self.assertEqual(len(analizar.triadas("Compró pan, leche y huevos.", "es")), 1)
        self.assertEqual(analizar.triadas("Tiene ventajas, pero también costes y riesgos.", "es"), [])
        self.assertEqual(analizar.triadas("Los problemas pendientes, también, y piden una respuesta.", "es"), [])

    def test_detecta_idioma(self):
        self.assertEqual(analizar.detectar_idioma(leer("texto-natural.md")), "es")
        self.assertEqual(analizar.detectar_idioma("The cat is on the table and it is happy."), "en")

    def test_marcar(self):
        marcado = analizar.marcar(leer("texto-ia.md"), "es", analizar.cargar_patrones()["es"])
        self.assertIn("⟦juega un papel crucial⟧", marcado)
        self.assertIn("⟦sencilla, rápida y barata", marcado)


class TestTopicosYCierre(unittest.TestCase):
    """Caso real: un ensayo sin muletillas, pero lleno de tópicos y con cierre de manual."""

    def setUp(self):
        texto = leer("ensayo-topicos.md")
        self.r = analizar.analizar(texto, texto, idioma="es")
        self.av = self.r["avisos"]

    def test_sin_muletillas_pero_con_topicos(self):
        self.assertNotIn("muletillas", self.av)
        topicos = " | ".join(self.av["topicos"])
        for frase in ("luces y sombras", "herramienta valiosa", "muchos expertos", "la opción más equilibrada"):
            self.assertIn(f"«{frase}»", topicos)

    def test_cierre_de_manual(self):
        self.assertIn("apela a «expertos»", " | ".join(self.av["cierre"]))

    def test_nota_por_debajo_de_8(self):
        self.assertLess(self.r["naturalidad"], 8.0)

    def test_cierre_que_resume(self):
        texto = ("La biblioteca abre ahora los domingos por la mañana.\n\n"
                 "Los estudiantes de bachillerato la llenan en época de exámenes.\n\n"
                 "Los jubilados vienen a leer la prensa y a usar los ordenadores.\n\n"
                 "Las familias aprovechan los talleres infantiles de los sábados.\n\n"
                 "Al final, estudiantes, jubilados y familias encuentran en la biblioteca un sitio con "
                 "prensa, ordenadores y talleres.")
        r = analizar.analizar(texto, texto, idioma="es")
        cierre = " | ".join(r["avisos"].get("cierre", []))
        self.assertIn("resume lo anterior", cierre)
        self.assertIn("tríada en el último párrafo", " | ".join(r["avisos"]["triadas"]))

    def test_cierre_con_idea_nueva_no_avisa(self):
        r = analizar.analizar(leer("texto-natural.md"), leer("texto-natural.md"), idioma="es")
        self.assertTrue(r["reescrito"]["cierre"]["aplica"])
        self.assertNotIn("cierre", r["avisos"])

    def test_ingles(self):
        texto = ("Remote work: a double-edged sword\n\nCommuting time drops to zero and rent gets cheaper.\n\n"
                 "Loneliness grows, and meetings stretch into the evening.\n\n"
                 "Hybrid schedules offer the best of both worlds, which is why experts agree they are the way forward.")
        r = analizar.analizar(texto, texto, idioma="en")
        topicos = " | ".join(r["avisos"]["topicos"])
        for frase in ("double-edged sword", "best of both worlds", "experts agree"):
            self.assertIn(frase, topicos)
        self.assertIn("cierre", r["avisos"])


class TestFidelidad(unittest.TestCase):
    ORIGINAL = ("El 3 de mayo de 2024, la doctora Elena Sanz presentó en Valencia un estudio con "
                "1.250 pacientes (García y López, 2019). Según Pérez (2021), el resultado fue "
                "«muy prometedor».")

    def errores(self, reescrito: str) -> str:
        errores, _ = analizar.fidelidad(self.ORIGINAL, reescrito, "es")
        return " | ".join(errores)

    def test_completo_sin_errores(self):
        reescrito = ("Elena Sanz presentó en Valencia, el 3 de mayo de 2024, un estudio con 1.250 pacientes "
                     "(García y López, 2019). Pérez (2021) lo calificó de «muy prometedor».")
        self.assertEqual(self.errores(reescrito), "")

    def test_cita_narrativa_pasada_a_parentetica(self):
        reescrito = ("Elena Sanz presentó en Valencia, el 3 de mayo de 2024, un estudio con 1.250 pacientes "
                     "(García y López, 2019). El resultado fue «muy prometedor» (Pérez, 2021).")
        self.assertEqual(self.errores(reescrito), "")

    def test_detecta_cada_perdida(self):
        casos = {
            "cifra «1.250»": self.ORIGINAL.replace("1.250", "más de mil"),
            "fecha «3 de mayo de 2024»": self.ORIGINAL.replace("3 de mayo de 2024", "3 de junio de 2024"),
            "nombre propio «Valencia»": self.ORIGINAL.replace("en Valencia ", ""),
            "nombre propio «Sanz»": self.ORIGINAL.replace(" Sanz", ""),
            "cita «muy prometedor»": self.ORIGINAL.replace("«muy prometedor»", "muy bueno"),
            "referencia «García y López, 2019»": self.ORIGINAL.replace("(García y López, 2019)", "(García, 2019)"),
            "referencia «Pérez (2021)»": self.ORIGINAL.replace("Según Pérez (2021)", "Según otros autores"),
        }
        for esperado, reescrito in casos.items():
            with self.subTest(esperado):
                self.assertIn(esperado, self.errores(reescrito))

    def test_codigos_de_salida(self):
        natural = leer("texto-natural.md")
        with tempfile.TemporaryDirectory() as tmp:
            o, r, ia = (Path(tmp) / n for n in ("o.md", "r.md", "ia.md"))
            o.write_text(natural, encoding="utf-8")
            r.write_text(natural, encoding="utf-8")
            ia.write_text(leer("texto-ia.md"), encoding="utf-8")
            self.assertEqual(ejecutar("analizar.py", o, r).returncode, 0)
            self.assertEqual(ejecutar("analizar.py", ia, ia).returncode, 2)

            o.write_text(natural.replace("tres o cuatro", "3 o 4").replace("pueblo", "Teruel"), encoding="utf-8")
            r.write_text(natural.replace("pueblo", "su pueblo"), encoding="utf-8")
            res = ejecutar("analizar.py", o, r)
            self.assertEqual(res.returncode, 1, res.stdout)
            self.assertIn("Fidelidad: 3 problemas", res.stdout)


class TestEjemplos(unittest.TestCase):
    def test_reescrituras_de_ejemplo_limpias(self):
        for original in sorted(EJEMPLOS.glob("*-original.md")):
            reescrito = original.with_name(original.name.replace("-original", "-reescrito"))
            with self.subTest(original.name):
                r = analizar.analizar(original.read_text(encoding="utf-8"), reescrito.read_text(encoding="utf-8"))
                self.assertEqual((r["errores"], r["avisos"]), ([], {}))
                self.assertGreater(sum(r["original"]["muletillas"].values()), 3)


@unittest.skipUnless(HAY_DOCX, "python-docx no instalado")
class TestDocxIO(unittest.TestCase):
    def test_conserva_titulos_y_estilos(self):
        from docx import Document
        docx_io = cargar_modulo("docx_io")
        with tempfile.TemporaryDirectory() as tmp:
            original, salida = Path(tmp) / "o.docx", Path(tmp) / "s.docx"
            doc = Document()
            doc.add_paragraph("Informe anual", style="Title")
            doc.add_paragraph("Resultados", style="Heading 1")
            doc.add_paragraph("Además, es importante destacar que las ventas subieron.")
            doc.add_paragraph("Por regiones", style="Heading 2")
            doc.add_paragraph("Norte", style="List Bullet")
            doc.add_paragraph("Sur", style="List Bullet")
            doc.save(original)

            texto = docx_io.extraer(original)
            self.assertEqual(texto.split("\n\n")[:4],
                             ["# Informe anual", "## Resultados",
                              "Además, es importante destacar que las ventas subieron.", "### Por regiones"])
            self.assertIn("- Norte\n\n- Sur", texto)

            nuevo = texto.replace("Además, es importante destacar que las ventas subieron.",
                                  "Las ventas subieron.\n\nSobre todo en el norte.")
            docx_io.escribir(original, nuevo, salida)
            parrafos = [(p.style.name, p.text) for p in Document(salida).paragraphs]
            self.assertEqual(parrafos, [
                ("Title", "Informe anual"), ("Heading 1", "Resultados"),
                ("Normal", "Las ventas subieron."), ("Normal", "Sobre todo en el norte."),
                ("Heading 2", "Por regiones"), ("List Bullet", "Norte"), ("List Bullet", "Sur"),
            ])

    def test_cli_sin_argumentos(self):
        r = ejecutar("docx_io.py")
        self.assertEqual(r.returncode, 1)
        self.assertIn("extraer", r.stderr)


if __name__ == "__main__":
    unittest.main()
