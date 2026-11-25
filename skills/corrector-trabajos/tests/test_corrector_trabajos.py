"""Tests de los scripts de corrector-trabajos.

Ejecutar desde la raíz del repo (o desde corrector-trabajos):
    python -m unittest discover -s skills/corrector-trabajos/tests -v
También funcionan con pytest. Necesitan python-docx.
"""
from __future__ import annotations

import contextlib
import copy
import importlib
import io
import json
import math
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SCRIPTS = RAIZ / "scripts"
DATOS = Path(__file__).resolve().parent / "datos"
EJEMPLOS = RAIZ / "examples"
sys.path.insert(0, str(SCRIPTS))


def cargar(nombre: str):
    # Los scripts se importan entre sí (extraer, revisar_estructura…), así que se cargan como módulos normales.
    return importlib.import_module(nombre)


extraer = cargar("extraer")
estructura = cargar("revisar_estructura")
referencias = cargar("revisar_referencias")
numeros = cargar("revisar_numeros")
calculos = cargar("calculos_lab")
comentar = cargar("comentar_docx")
validar = cargar("validar_correccion")
informe = cargar("informe_html")
versiones = cargar("comparar_versiones")

from docx import Document  # noqa: E402
from docx.oxml.ns import qn  # noqa: E402


def tipos(avisos: list[dict]) -> list[str]:
    return [a["tipo"] for a in avisos]


def silencio():
    return contextlib.redirect_stdout(io.StringIO())


# --- extraer.py ---------------------------------------------------------------------

class TestExtraer(unittest.TestCase):
    def test_markdown(self):
        doc = extraer.cargar(DATOS / "lab-errores.md")
        titulos = [b.texto for b in doc.titulos()]
        self.assertIn("Resultados", titulos)
        leyendas = [(b.clase, b.numero) for b in doc.bloques if b.tipo == "leyenda"]
        self.assertIn(("tabla", "1"), leyendas)
        self.assertIn(("figura", "1"), leyendas)
        tabla = next(b for b in doc.bloques if b.tipo == "tabla")
        self.assertEqual(tabla.filas[0][0], "Muestra")
        self.assertEqual(tabla.seccion, "Resultados")

    def test_latex(self):
        doc = extraer.cargar(DATOS / "informe.tex")
        titulos = [b.texto for b in doc.titulos()]
        self.assertEqual(titulos[:3], ["Ensayo de prueba", "Introducción", "Resultados"])
        texto = doc.texto()
        self.assertIn("Figura 1", texto)  # \ref{fig:recta} → número
        self.assertIn("Tabla 1", texto)
        self.assertIn("\\cite{bradford1976}", texto)
        self.assertIn("5 mL", texto)  # \SI{5}{\milli\litre}
        self.assertIn("R²", texto)
        claves = [b.clave for b in doc.bloques if b.clave]
        self.assertEqual(claves, ["bradford1976", "otro2020"])
        leyendas = [(b.clase, b.numero) for b in doc.bloques if b.tipo == "leyenda"]
        self.assertEqual(leyendas, [("figura", "1"), ("tabla", "1")])

    def test_docx_titulos_tablas_imagenes_superindices(self):
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp) / "t.docx"
            d = Document()
            d.add_heading("Introducción", 1)
            p = d.add_paragraph("Según la bibliografía")
            r = p.add_run("1,2")
            r.font.superscript = True
            p.add_run(" el R")
            r2 = p.add_run("2")
            r2.font.superscript = True
            p.add_run(" es alto.")
            q = d.add_paragraph()
            q.add_run("2. Métodos manuales").bold = True
            t = d.add_table(rows=2, cols=2)
            t.cell(0, 0).text = "A"
            t.cell(1, 1).text = "0,5"
            d.add_paragraph("Tabla 1. Datos.")
            d.save(ruta)
            doc = extraer.cargar(ruta)
        textos = [b.texto for b in doc.bloques]
        self.assertIn("Según la bibliografía^{1,2} el R² es alto.", textos)
        self.assertEqual([(b.texto, b.nivel) for b in doc.titulos()], [("Introducción", 1), ("2. Métodos manuales", 1)])
        self.assertEqual(next(b for b in doc.bloques if b.tipo == "tabla").filas, [["A", ""], ["", "0,5"]])
        self.assertTrue(any(b.tipo == "leyenda" and b.clase == "tabla" for b in doc.bloques))

    def test_texto_plano_y_pdf_minimo(self):
        texto = "1. INTRODUCCIÓN\n\nUn párrafo de prueba con datos.\n\n2. Resultados\n\nOtro párrafo.\n"
        bloques = extraer.cargar_md(texto, markdown=False)
        self.assertEqual([b.texto for b in bloques if b.tipo == "titulo"], ["1. INTRODUCCIÓN", "2. Resultados"])
        # PDF mínimo sin comprimir con texto en Tj y TJ
        contenido = b"BT /F1 12 Tf 72 720 Td (Hola mundo) Tj 0 -14 Td [(Segunda) -300 (linea)] TJ ET"
        pdf = (b"%PDF-1.4\n1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n"
               b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n"
               b"3 0 obj << /Type /Page /Parent 2 0 R /Contents 4 0 R >> endobj\n"
               b"4 0 obj << /Length " + str(len(contenido)).encode() + b" >>\nstream\n" + contenido
               + b"\nendstream\nendobj\ntrailer << /Root 1 0 R >>\n%%EOF")
        salida = extraer._pdf_minimo(pdf)
        self.assertIn("Hola mundo", salida)
        self.assertIn("Segunda linea", salida)

    def test_leyendas(self):
        self.assertEqual(extraer.detectar_leyenda("Figura 3. Recta de calibrado"), ("figura", "3"))
        self.assertEqual(extraer.detectar_leyenda("Table 2: Results"), ("tabla", "2"))
        self.assertEqual(extraer.detectar_leyenda("2. irudia. Kalibrazio-zuzena"), ("figura", "2"))
        self.assertIsNone(extraer.detectar_leyenda("La figura 3 muestra la recta."))


# --- revisar_estructura.py ---------------------------------------------------------------

class TestEstructura(unittest.TestCase):
    def test_detecta_errores(self):
        r = estructura.revisar(DATOS / "lab-errores.md", "laboratorio")
        t = tipos(r["avisos"])
        self.assertIn("seccion_falta", t)  # sin discusión ni bibliografía
        faltan = [a["detalle"] for a in r["avisos"] if a["tipo"] == "seccion_falta"]
        self.assertTrue(any("Discusión" in f for f in faltan))
        self.assertIn("sin_citar", t)  # Figura 1 no se cita
        self.assertIn("cita_inexistente", t)  # se cita la Figura 3
        self.assertIn("numeracion", t)  # salta de la Tabla 1 a la 3
        self.assertIn("objetivo_no_evaluado", t)

    def test_trabajo_limpio(self):
        r = estructura.revisar(DATOS / "lab-limpio.md", "laboratorio")
        self.assertEqual(r["avisos"], [], r["avisos"])

    def test_pruebas_sin_resultados_y_con_resultados(self):
        base = ("# Memoria\n\n## Objetivos\n\n- O1. Implementar el login de usuarios.\n\n## Análisis\n\nTexto.\n\n"
                "## Diseño\n\nTexto.\n\n## Implementación\n\nTexto.\n\n## Pruebas\n\n{pruebas}\n\n"
                "## Conclusiones\n\nEl objetivo O1 se cumple: el login de usuarios funciona.\n")
        with tempfile.TemporaryDirectory() as tmp:
            mal = Path(tmp) / "mal.md"
            mal.write_text(base.format(pruebas="Se hicieron pruebas unitarias con pytest del login."), encoding="utf-8")
            bien = Path(tmp) / "bien.md"
            bien.write_text(base.format(pruebas="Se ejecutaron 42 pruebas del login: 41 superadas y 1 fallada; "
                                               "cobertura del 87 %."), encoding="utf-8")
            self.assertIn("pruebas_sin_resultados", tipos(estructura.revisar(mal, "tecnico")["avisos"]))
            # Sin introducción ni bibliografía solo quedan avisos de secciones recomendadas.
            self.assertEqual({a["tipo"] for a in estructura.revisar(bien, "tecnico")["avisos"]}, {"seccion_recomendada"})

    def test_sinonimos_y_euskera(self):
        self.assertEqual(estructura.canonica("3. Material y Métodos"), "metodos")
        self.assertEqual(estructura.canonica("Emaitzak eta eztabaida"), "resultados_discusion")
        self.assertEqual(estructura.canonica("Results and Discussion"), "resultados_discusion")
        self.assertEqual(estructura.canonica("Ondorioak"), "conclusiones")
        self.assertIsNone(estructura.canonica("El ciclo de Krebs"))


# --- revisar_referencias.py ----------------------------------------------------------------

class TestReferencias(unittest.TestCase):
    def test_detecta_errores_autor_anio(self):
        r = referencias.revisar(DATOS / "lab-errores.md")
        t = tipos(r["avisos"])
        self.assertIn("cita_sin_entrada", t)  # (Pérez, 2015)
        self.assertIn("entrada_sin_citar", t)  # Gómez
        self.assertIn("anio_distinto", t)  # Bradford 1977 frente a 1976
        self.assertIn("mezcla_sistemas", t)  # también hay [2]
        sin = [a["detalle"] for a in r["avisos"] if a["tipo"] == "cita_sin_entrada"]
        self.assertTrue(any("Pérez" in s for s in sin))

    def test_limpio(self):
        r = referencias.revisar(DATOS / "lab-limpio.md")
        self.assertEqual(r["avisos"], [], r["avisos"])
        self.assertEqual(r["estilo"], "APA")

    def test_numericas_y_superindices(self):
        texto = ("# T\n\n## Introducción\n\nDato [1]. Otro dato [2-3]. Y uno más^4^.\n\n## Bibliografía\n\n"
                 "[1] A. Pérez, \"Uno,\" 2020.\n\n[2] B. López, \"Dos,\" 2021.\n\n[3] C. Ruiz, \"Tres,\" 2019.\n")
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp) / "n.md"
            ruta.write_text(texto, encoding="utf-8")
            r = referencias.revisar(ruta)
        detalles = " ".join(a["detalle"] for a in r["avisos"])
        self.assertIn("referencia 4", detalles)
        self.assertEqual(r["citas"]["numericas"], 4)
        self.assertEqual(r["estilo"], "IEEE")

    def test_latex(self):
        r = referencias.revisar(DATOS / "informe.tex")
        t = tipos(r["avisos"])
        self.assertIn("cita_sin_entrada", t)  # \cite{fantasma}
        self.assertIn("entrada_sin_citar", t)  # otro2020
        self.assertEqual(r["citas"]["latex"], 2)

    def test_clave_autor(self):
        self.assertEqual(referencias.clave_autor("de la Fuente"), "fuente")
        self.assertEqual(referencias.clave_autor("García-López, M."), "garcia-lopez")


# --- revisar_numeros.py ------------------------------------------------------------------------

class TestNumeros(unittest.TestCase):
    def test_detecta_errores(self):
        r = numeros.revisar(DATOS / "lab-errores.md")
        t = tipos(r["avisos"])
        for esperado in ("valor_inconsistente", "texto_tabla", "posible_error_copia", "unidad_mal_escrita",
                         "unidad_sin_espacio", "unidad_variantes", "decimales_irregulares", "cabecera_sin_unidad",
                         "separador_decimal"):
            self.assertIn(esperado, t)
        mal = " ".join(a["detalle"] for a in r["avisos"] if a["tipo"] == "unidad_mal_escrita")
        self.assertIn("ºC", mal)
        self.assertIn("mins", mal)

    def test_limpio(self):
        r = numeros.revisar(DATOS / "lab-limpio.md")
        self.assertEqual(r["avisos"], [], r["avisos"])

    def test_valor_y_redondeo(self):
        self.assertEqual(numeros.valor("0,452", ","), (0.452, 3, ","))
        self.assertEqual(numeros.valor("1.250.000"), (1250000.0, 0, ""))
        self.assertIsNone(numeros.valor("1,250"))  # ambiguo sin separador conocido
        self.assertTrue(numeros.iguales("0,99", "0,987", ","))
        self.assertFalse(numeros.iguales("0,9987", "0,987", ","))
        self.assertTrue(numeros.casi_iguales("0,9943", "0,9934"))  # traspuestos
        self.assertTrue(numeros.casi_iguales("0,9987", "0,987"))  # un dígito de más
        self.assertFalse(numeros.casi_iguales("0,452", "0,458"))  # solo cambia el último


# --- calculos_lab.py --------------------------------------------------------------------------------

def uno(c: dict) -> dict:
    r = calculos.calcular({"comprobaciones": [c]})
    assert not r["errores"], r["errores"]
    return r["resultados"][0]


class TestCalculos(unittest.TestCase):
    def test_molaridad(self):
        r = uno({"id": "a", "tipo": "molaridad", "masa_g": 0.5844, "pm_g_mol": 58.44, "volumen_mL": 100, "declarado": "0,1"})
        self.assertAlmostEqual(r["resultado"], 0.1)
        self.assertTrue(r["coincide"])
        r = uno({"id": "b", "tipo": "molaridad", "masa_g": 0.5844, "pm_g_mol": 58.44, "volumen_mL": 100, "declarado": 100})
        self.assertFalse(r["coincide"])  # olvidó pasar mL a L

    def test_dilucion(self):
        r = uno({"id": "d", "tipo": "dilucion", "c1": 2, "v1": None, "c2": 0.5, "v2": 10, "declarado": "0,25"})
        self.assertAlmostEqual(r["resultado"], 2.5)
        self.assertFalse(r["coincide"])
        r = uno({"id": "d", "tipo": "dilucion", "c1": 1, "v1": 2, "c2": 0.1, "v2": None, "declarado": "18"})
        self.assertAlmostEqual(r["resultado"], 20)
        self.assertIn("disolvente", r["nota"])

    def test_dilucion_seriada(self):
        res = calculos.calcular({"comprobaciones": [{"id": "s", "tipo": "dilucion_seriada", "c0": 1, "factor": 10,
                                                      "pasos": 3, "declarado": ["0,1", "0,01", "0,01"]}]})["resultados"]
        self.assertEqual([r["coincide"] for r in res], [True, True, False])
        self.assertAlmostEqual(res[2]["resultado"], 0.001)

    def test_henderson_hasselbalch(self):
        r = uno({"id": "h", "tipo": "henderson_hasselbalch", "pka": 7.21, "base": 0.06, "acido": 0.04, "declarado": "7,39"})
        self.assertAlmostEqual(r["resultado"], 7.21 + math.log10(1.5))
        self.assertTrue(r["coincide"])
        r = uno({"id": "h", "tipo": "henderson_hasselbalch", "pka": 7.21, "base": 0.06, "acido": 0.04, "declarado": "7,03"})
        self.assertFalse(r["coincide"])
        self.assertIn("invertir", r["nota"])
        r = uno({"id": "h", "tipo": "henderson_hasselbalch", "pka": 4.76, "ph_objetivo": 4.76})
        self.assertAlmostEqual(r["resultado"], 1.0)

    def test_calibrado_r2_conocido(self):
        # Ejemplo hecho a mano: m = 0,6; b = 2,2; R² = 0,6.
        res = calculos.calcular({"comprobaciones": [{"id": "k", "tipo": "calibrado", "x": [1, 2, 3, 4, 5],
                                                      "y": [2, 4, 5, 4, 5],
                                                      "declarado": {"pendiente": "0,6", "ordenada": "2,2", "r2": "0,6"}}]})
        d = {r["id"]: r for r in res["resultados"]}
        self.assertAlmostEqual(d["k.pendiente"]["resultado"], 0.6)
        self.assertAlmostEqual(d["k.ordenada"]["resultado"], 2.2)
        self.assertAlmostEqual(d["k.r2"]["resultado"], 0.6)
        self.assertTrue(all(r["coincide"] for r in res["resultados"]))

    def test_calibrado_errores_tipicos(self):
        x, y = [0, 0.1, 0.2, 0.3, 0.4, 0.5], [0.000, 0.071, 0.118, 0.196, 0.231, 0.305]
        res = calculos.calcular({"comprobaciones": [{
            "id": "k", "tipo": "calibrado", "x": x, "y": y, "declarado": {"r2": "0,9943"},
            "muestras": [{"nombre": "A", "y": 0.162, "factor_dilucion": 100, "declarado": "0,264"},
                         {"nombre": "Z", "y": 0.9, "declarado": "1,5"}]}]})
        d = {r["id"]: r for r in res["resultados"]}
        self.assertAlmostEqual(d["k.r2"]["resultado"], 0.99344, places=5)
        self.assertFalse(d["k.r2"]["coincide"])
        self.assertFalse(d["k.A"]["coincide"])
        self.assertIn("factor de dilución", d["k.A"]["nota"])
        self.assertIn("extrapolación", d["k.Z"]["nota"])
        r2 = calculos.calcular({"comprobaciones": [{"id": "k", "tipo": "calibrado", "x": x, "y": y,
                                                    "declarado": {"r2": "0,9967"}}]})["resultados"][2]
        self.assertIn("correlación", r2["nota"])

    def test_lambert_beer_rendimiento_porcentaje(self):
        r = uno({"id": "l", "tipo": "lambert_beer", "absorbancia": 0.5, "epsilon": 6220, "l_cm": 1, "c": None,
                 "declarado": "8,04e-5"})
        self.assertAlmostEqual(r["resultado"], 0.5 / 6220)
        self.assertTrue(r["coincide"])
        self.assertAlmostEqual(uno({"id": "r", "tipo": "rendimiento", "obtenido": 1.2, "teorico": 1.5})["resultado"], 80)
        self.assertAlmostEqual(uno({"id": "p", "tipo": "porcentaje", "parte": 3, "total": 12})["resultado"], 25)
        self.assertIn("100 %", uno({"id": "r", "tipo": "rendimiento", "obtenido": 2, "teorico": 1.5})["nota"])

    def test_datos_incorrectos(self):
        r = calculos.calcular({"comprobaciones": [{"id": "x", "tipo": "dilucion", "c1": 1, "v1": None, "c2": None, "v2": 1},
                                                  {"id": "y", "tipo": "magia"}]})
        self.assertEqual(len(r["errores"]), 2)


# --- comentar_docx.py -------------------------------------------------------------------------------

def docx_de_prueba(ruta: Path) -> None:
    d = Document()
    d.add_heading("Resultados", 1)
    p = d.add_paragraph()
    p.add_run("La recta tiene ")
    p.add_run("R² = 0,9943").bold = True
    p.add_run(", lo que confirma la linealidad.")
    d.add_paragraph("Se tomaron 0,25 mL de la disolución madre.")
    t = d.add_table(rows=1, cols=1)
    t.cell(0, 0).text = "Valor en tabla 0,452"
    d.save(ruta)


def anclas(ruta: Path) -> dict[str, str]:
    d = Document(str(ruta))
    salida = {}
    for p in comentar.parrafos(d):
        abiertos: dict[str, list[str]] = {}
        for el in p.iter():
            if el.tag == qn("w:commentRangeStart"):
                abiertos[el.get(qn("w:id"))] = []
            elif el.tag == qn("w:commentRangeEnd"):
                salida[el.get(qn("w:id"))] = "".join(abiertos.pop(el.get(qn("w:id")), []))
            elif el.tag == qn("w:r"):
                for k in abiertos:
                    abiertos[k].append(comentar.texto_run(el))
    return salida


class TestComentarDocx(unittest.TestCase):
    CORR = {"comentarios": [
        {"id": "k1", "cita": "0,9943, lo que confirma", "gravedad": "importante", "que_falla": "No coincide.",
         "como_arreglarlo": "Corrige."},
        {"id": "k2", "cita": "0,25 mL", "gravedad": "critico", "que_falla": "Mal calculado.", "como_arreglarlo": "2,5 mL."},
        {"id": "k3", "cita": "Valor en tabla", "gravedad": "menor", "que_falla": "x", "como_arreglarlo": "y"},
        {"id": "k4", "cita": "esto no está", "gravedad": "menor", "que_falla": "x", "como_arreglarlo": "y"}]}

    def _probar(self, usar_api: bool):
        with tempfile.TemporaryDirectory() as tmp:
            original, salida = Path(tmp) / "o.docx", Path(tmp) / "s.docx"
            docx_de_prueba(original)
            r = comentar.comentar(original, self.CORR, salida, usar_api=usar_api)
            self.assertEqual(r["anclados"], ["k1", "k2", "k3"])
            self.assertEqual(r["sin_anclar"], ["k4"])
            # Texto original intacto, párrafo a párrafo.
            antes = [comentar.texto_parrafo(p) for p in comentar.parrafos(Document(str(original)))]
            despues = [comentar.texto_parrafo(p) for p in comentar.parrafos(Document(str(salida)))]
            self.assertEqual(antes, despues)
            # Cada comentario anclado al fragmento exacto, aunque cruce runs con formato distinto.
            self.assertEqual(sorted(anclas(salida).values()), sorted(["0,9943, lo que confirma", "0,25 mL", "Valor en tabla"]))
            with zipfile.ZipFile(salida) as z:
                xml = z.read("word/comments.xml").decode("utf-8")
            self.assertEqual(xml.count("<w:comment "), 3)
            self.assertIn("[CRÍTICO] Mal calculado.", xml)
            # La negrita del fragmento partido se conserva.
            d = Document(str(salida))
            negritas = "".join(r.text for r in d.paragraphs[1].runs if r.bold)
            self.assertEqual(negritas, "R² = 0,9943")

    def test_con_api(self):
        if not hasattr(Document(), "add_comment"):
            self.skipTest("python-docx < 1.2")
        self._probar(True)

    def test_xml_directo(self):
        self._probar(False)

    def test_no_sobrescribe_el_original(self):
        with tempfile.TemporaryDirectory() as tmp:
            original = Path(tmp) / "o.docx"
            docx_de_prueba(original)
            corr = Path(tmp) / "c.json"
            corr.write_text(json.dumps(self.CORR), encoding="utf-8")
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(comentar.main(["x", str(original), str(corr), str(original)]), 1)


# --- validar_correccion.py e informe_html.py ----------------------------------------------------------

def correccion_valida() -> dict:
    return json.loads((EJEMPLOS / "correccion-informe-bradford.json").read_text(encoding="utf-8"))


class TestValidar(unittest.TestCase):
    def test_ejemplos_validos(self):
        for nombre in ("informe-bradford", "memoria-reservas"):
            with self.subTest(nombre):
                corr = json.loads((EJEMPLOS / f"correccion-{nombre}.json").read_text(encoding="utf-8"))
                self.assertEqual(validar.validar(corr, EJEMPLOS / f"{nombre}.docx"), ([], []))

    def test_errores(self):
        casos = {
            "sin «comprobacion»": lambda c: c["comentarios"][0].pop("comprobacion"),
            "coincide con el trabajo": lambda c: c["comentarios"][0].update(comprobacion="c2"),
            "más de 2 frases": lambda c: c["comentarios"][1].update(
                ejemplo="Una frase. Otra frase. Y una tercera que ya reescribe el párrafo."),
            "suman 90": lambda c: c["valoracion"]["criterios"][0].update(peso=0),
            "media ponderada": lambda c: c["valoracion"].update({"global": 9.9}),
            "no está en la rúbrica": lambda c: c["comentarios"][2].update(criterio="C99"),
            "gravedad «grave»": lambda c: c["comentarios"][2].update(gravedad="grave"),
        }
        for esperado, cambio in casos.items():
            with self.subTest(esperado):
                corr = correccion_valida()
                cambio(corr)
                errores, _ = validar.validar(corr)
                self.assertTrue(any(esperado in e for e in errores), errores)

    def test_cita_no_literal(self):
        corr = correccion_valida()
        corr["comentarios"][3]["cita"] = "R² = 0,9999 inventado"
        errores, _ = validar.validar(corr, EJEMPLOS / "informe-bradford.docx")
        self.assertTrue(any("no aparece literal" in e for e in errores))

    def test_avisos_de_tono(self):
        corr = correccion_valida()
        for c in corr["comentarios"][:3]:
            c["como_arreglarlo"] = "Sería conveniente revisar esto."
        corr["puntos_fuertes"] = [{"texto": "Buen trabajo."}]
        corr["comentarios"] += [dict(copy.deepcopy(corr["comentarios"][-1]), id=f"z{i}") for i in range(20)]
        _, avisos = validar.validar(corr)
        texto = " | ".join(avisos)
        self.assertIn("sería conveniente", texto)
        self.assertIn("empiezan «sería conveniente…»", texto)
        self.assertIn("puntos fuertes", texto)
        self.assertIn("genérico", texto)
        self.assertIn("comentarios (máx.", texto)

    def test_informe_html(self):
        corr = correccion_valida()
        html = informe.generar(corr, "ciencias")
        for fragmento in ("Nota orientativa", "Valoración orientativa", "Los 3 cambios que más suben la nota",
                          "Puntos fuertes", "Cálculos recalculados", "C1·V1 = C2·V2", "No coincide", "6,7",
                          'id="k01"', "Verificar con la bibliografía"):
            self.assertIn(fragmento, html)
        self.assertLess(html.index('id="k01"'), html.index('id="k10"'))  # críticos antes que menores

    def test_informe_no_se_genera_con_errores(self):
        corr = correccion_valida()
        corr["comentarios"][0].pop("comprobacion")
        with tempfile.TemporaryDirectory() as tmp:
            entrada, salida = Path(tmp) / "c.json", Path(tmp) / "c.html"
            entrada.write_text(json.dumps(corr), encoding="utf-8")
            with silencio(), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(informe.main(["x", str(entrada), str(salida)]), 1)
            self.assertFalse(salida.exists())


# --- comparar_versiones.py ---------------------------------------------------------------------------

class TestVersiones(unittest.TestCase):
    def test_sigue_y_cambiado(self):
        corr = correccion_valida()
        texto = extraer.a_markdown(extraer.cargar(EJEMPLOS / "informe-bradford.docx"))
        texto = texto.replace("se tomaron 0,25 mL de la disolución madre", "se tomaron 2,5 mL de la disolución madre")
        with tempfile.TemporaryDirectory() as tmp:
            nueva = Path(tmp) / "v2.md"
            nueva.write_text(texto, encoding="utf-8")
            r = versiones.comparar(corr, nueva)
        self.assertEqual([x["id"] for x in r["cambiados"]], ["k01"])
        self.assertEqual(len(r["siguen"]), len(corr["comentarios"]) - 1)


# --- Errores plantados en los ejemplos ------------------------------------------------------------------

class TestEjemplos(unittest.TestCase):
    """Los errores plantados que tienen que encontrar los scripts (tabla del README)."""

    def test_bradford(self):
        ruta = EJEMPLOS / "informe-bradford.docx"
        est = estructura.revisar(ruta, "laboratorio")["avisos"]
        self.assertTrue(any(a["tipo"] == "sin_citar" and "Figura 2" in a["detalle"] for a in est))
        ref = referencias.revisar(ruta)["avisos"]
        self.assertTrue(any(a["tipo"] == "cita_sin_entrada" and "Compton" in a["detalle"] for a in ref))
        num = numeros.revisar(ruta)["avisos"]
        self.assertTrue(any(a["tipo"] == "valor_inconsistente" and "0,9943" in a["detalle"] for a in num))
        unidades = " ".join(a["detalle"] for a in num if a["tipo"].startswith("unidad"))
        for u in ("595nm", "ul", "mins"):
            self.assertIn(u, unidades)
        calc = calculos.calcular(json.loads((EJEMPLOS / "calculos-bradford.json").read_text(encoding="utf-8")))
        self.assertEqual(calc["no_coinciden"], ["c1", "c3.r2"])
        # Sin falsos positivos en lo que está bien.
        self.assertEqual(len(est), 1)
        self.assertEqual(len(ref), 1)

    def test_memoria(self):
        ruta = EJEMPLOS / "memoria-reservas.docx"
        est = estructura.revisar(ruta, "tecnico")["avisos"]
        self.assertTrue(any(a["tipo"] == "sin_citar" and "Figura 1" in a["detalle"] for a in est))
        self.assertTrue(any(a["tipo"] == "objetivo_no_evaluado" and a["objetivo"].startswith("O3") for a in est))
        self.assertIn("pruebas_sin_resultados", tipos(est))
        self.assertEqual(len(est), 3)
        self.assertEqual(referencias.revisar(ruta)["avisos"], [])
        self.assertEqual(numeros.revisar(ruta)["avisos"], [])


if __name__ == "__main__":
    unittest.main()
