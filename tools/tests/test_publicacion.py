"""Tests de las herramientas de publicación: portables, frontmatter y empaquetado.

Ejecutar desde la raíz del repo:
    python -m unittest discover -s tools/tests -v
"""
from __future__ import annotations

import importlib.util
import re
import shutil
import tempfile
import unittest
import zipfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
REPO = TOOLS.parent


def cargar(nombre: str):
    spec = importlib.util.spec_from_file_location(nombre, TOOLS / f"{nombre}.py")
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


portables = cargar("generar_portables")
frontmatter = cargar("validar_frontmatter")
empaquetar = cargar("empaquetar")

SKILLS = sorted(d for d in (REPO / "skills").iterdir() if d.is_dir() and (d / "SKILL.md").is_file())


class TestPortables(unittest.TestCase):
    def test_portables_al_dia(self):
        """Falla si alguien cambia una skill y no regenera su prompt-portable.md."""
        for skill in SKILLS:
            with self.subTest(skill.name):
                archivo = skill / portables.NOMBRE
                self.assertTrue(archivo.is_file(), f"falta {archivo.name}: python tools/generar_portables.py")
                self.assertEqual(archivo.read_text(encoding="utf-8"), portables.generar(skill),
                                 f"{skill.name}/{portables.NOMBRE} está desactualizado: "
                                 "python tools/generar_portables.py")

    def test_cada_skill_tiene_comprobaciones_manuales(self):
        for skill in SKILLS:
            with self.subTest(skill.name):
                self.assertIn(skill.name, portables.MANUAL)

    def test_contenido_autocontenido(self):
        for skill in SKILLS:
            with self.subTest(skill.name):
                texto = portables.generar(skill)
                self.assertIn("## Si no puedes ejecutar código", texto)
                self.assertNotIn("examples/", texto)
                # las rutas a references/ apuntan a su anexo, que va dentro. Los assets
                # (plantillas) se copian tal cual, así que su código no se revisa.
                cuerpo = re.sub(r"(`{3,})\w*\n.*?\n\1", "", texto.split("-->", 1)[1], flags=re.S)
                self.assertNotRegex(cuerpo, r"(?<![\w/])references/[\w-]+\.md")
                for ref in sorted((skill / "references").glob("*.md")):
                    self.assertIn(f"## Anexo: `{ref.name}`", texto)

    def test_detecta_portable_desactualizado(self):
        with tempfile.TemporaryDirectory() as tmp:
            copia = Path(tmp) / "reescritor-estilo"
            shutil.copytree(REPO / "skills" / "reescritor-estilo", copia, ignore=shutil.ignore_patterns("tests", "examples"))
            antes = portables.generar(copia)
            skill_md = copia / "SKILL.md"
            texto = skill_md.read_text(encoding="utf-8").replace("\n## 1.", "\nLínea nueva.\n\n## 1.", 1)
            skill_md.write_text(texto, encoding="utf-8")
            self.assertNotEqual(antes, portables.generar(copia))

    def test_titulos_dentro_de_codigo_no_cambian(self):
        texto = "# Título\n```\n# comentario\n```\n## Sub"
        self.assertEqual(portables.bajar_titulos(texto), "## Título\n```\n# comentario\n```\n### Sub")


class TestFrontmatter(unittest.TestCase):
    def crear(self, tmp: Path, carpeta: str, frontmatter_texto: str) -> Path:
        skill = tmp / carpeta
        skill.mkdir()
        (skill / "SKILL.md").write_text(f"---\n{frontmatter_texto}\n---\n\n# Cuerpo\n", encoding="utf-8")
        return skill

    def test_skills_del_repo_validas(self):
        for skill in SKILLS:
            with self.subTest(skill.name):
                self.assertEqual(frontmatter.validar(skill), [])

    def test_errores(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            casos = {
                "campo no estándar «version»": ("mi-skill", "name: mi-skill\ndescription: Hace algo.\nversion: 2"),
                "no coincide con la carpeta": ("otra", "name: mi-skill\ndescription: Hace algo."),
                "solo a-z": ("Mi--Skill", "name: Mi--Skill\ndescription: Hace algo."),
                "falta el campo obligatorio «description»": ("sin-desc", "name: sin-desc"),
                "máx. 1024": ("larga", "name: larga\ndescription: >-\n  " + "x" * 1100),
            }
            for esperado, (carpeta, fm) in casos.items():
                with self.subTest(esperado):
                    errores = " | ".join(frontmatter.validar(self.crear(tmp, carpeta, fm)))
                    self.assertIn(esperado, errores)

    def test_metadata_y_campos_opcionales(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = self.crear(Path(tmp), "ok-skill",
                               "name: ok-skill\ndescription: Hace algo.\nlicense: MIT\n"
                               "compatibility: Python 3.10+\nmetadata:\n  autor: alguien\n  version: \"1.0\"")
            self.assertEqual(frontmatter.validar(skill), [])


class TestEmpaquetar(unittest.TestCase):
    def test_zip_sin_tests_ni_ejemplos(self):
        with tempfile.TemporaryDirectory() as tmp:
            for skill in SKILLS:
                with self.subTest(skill.name):
                    zip_path = empaquetar.empaquetar(skill, Path(tmp))
                    with zipfile.ZipFile(zip_path) as z:
                        nombres = z.namelist()
                    self.assertIn(f"{skill.name}/SKILL.md", nombres)
                    self.assertTrue(all(n.startswith(f"{skill.name}/") for n in nombres))
                    for prohibido in ("/tests/", "/examples/", "__pycache__", ".pyc",
                                      "/README.md", "/prompt-portable.md"):
                        self.assertFalse(any(prohibido in n for n in nombres), prohibido)
                    for ref in (skill / "references").glob("*.md"):
                        self.assertIn(f"{skill.name}/references/{ref.name}", nombres)

    def test_zip_reproducible(self):
        skill = REPO / "skills" / "creador-tests"
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            self.assertEqual(empaquetar.empaquetar(skill, Path(a)).read_bytes(),
                             empaquetar.empaquetar(skill, Path(b)).read_bytes())


class TestPortableLite(unittest.TestCase):
    def test_lite_existe_al_dia_y_bajo_el_limite(self):
        for skill in SKILLS:
            with self.subTest(skill.name):
                archivo = skill / portables.NOMBRE_LITE
                self.assertTrue(archivo.is_file(), f"falta {archivo.name}: python tools/generar_portables.py")
                texto = archivo.read_text(encoding="utf-8")
                self.assertLessEqual(len(texto), portables.LIMITE_LITE,
                                     f"{skill.name}: {len(texto)} caracteres (máx. {portables.LIMITE_LITE})")
                self.assertEqual(texto, portables.generar_lite(skill),
                                 f"{skill.name}/{portables.NOMBRE_LITE} desactualizado")
                self.assertIn(portables.NOMBRE, texto)  # remite al portable completo

    def test_lite_revisado_para_el_skill_md_actual(self):
        """Falla si cambia un SKILL.md y nadie revisa su texto lite (tools/lite/<skill>.md)."""
        for skill in SKILLS:
            with self.subTest(skill.name):
                self.assertEqual(portables.problemas_lite(skill), [])

    def test_detecta_skill_md_cambiado(self):
        with tempfile.TemporaryDirectory() as tmp:
            copia = Path(tmp) / "creador-tests"
            shutil.copytree(REPO / "skills" / "creador-tests", copia,
                            ignore=shutil.ignore_patterns("tests", "examples"))
            self.assertEqual(portables.problemas_lite(copia), [])
            skill_md = copia / "SKILL.md"
            skill_md.write_text(skill_md.read_text(encoding="utf-8") + "\nRegla nueva.\n", encoding="utf-8")
            self.assertTrue(any("ha cambiado" in p for p in portables.problemas_lite(copia)))


class TestClaudeAI(unittest.TestCase):
    def test_descripcion_corta_existe_y_cabe(self):
        for skill in SKILLS:
            with self.subTest(skill.name):
                ruta = skill / empaquetar.CLAUDE_AI
                self.assertTrue(ruta.is_file(), f"falta {skill.name}/{empaquetar.CLAUDE_AI}")
                texto = ruta.read_text(encoding="utf-8").strip()
                self.assertTrue(texto)
                self.assertNotIn("\n", texto)
                self.assertLessEqual(len(texto), 200, f"{skill.name}: {len(texto)} caracteres")

    def test_zip_claude_ai_inyecta_la_descripcion(self):
        with tempfile.TemporaryDirectory() as normal, tempfile.TemporaryDirectory() as corta:
            for skill in SKILLS:
                with self.subTest(skill.name):
                    z1 = zipfile.ZipFile(empaquetar.empaquetar(skill, Path(normal)))
                    z2 = zipfile.ZipFile(empaquetar.empaquetar(skill, Path(corta), claude_ai=True))
                    with z1, z2:
                        self.assertEqual(z1.namelist(), z2.namelist())
                        self.assertFalse(any(n.endswith(("claude-ai.txt", "prompt-portable-lite.md"))
                                             for n in z2.namelist()))
                        md = z2.read(f"{skill.name}/SKILL.md").decode("utf-8")
                        campos = frontmatter.leer(md)
                        self.assertEqual(campos["description"], empaquetar.descripcion_corta(skill))
                        self.assertEqual(campos["name"], skill.name)
                        self.assertTrue(set(campos) <= frontmatter.PERMITIDOS)
                        # el cuerpo del SKILL.md no cambia; el resto de archivos, tampoco
                        original = (skill / "SKILL.md").read_text(encoding="utf-8")
                        self.assertEqual(md.split("\n---\n", 1)[1], original.split("\n---\n", 1)[1])
                        for n in z1.namelist():
                            if not n.endswith("/SKILL.md"):
                                self.assertEqual(z1.read(n), z2.read(n), n)

    def test_inyectar_descripcion_de_una_linea(self):
        md = "---\nname: x\ndescription: Larga, larga.\nlicense: MIT\n---\n\n# X\n"
        nuevo = empaquetar.inyectar_descripcion(md, "Corta.")
        self.assertEqual(frontmatter.leer(nuevo), {"name": "x", "description": "Corta.", "license": "MIT"})
        self.assertTrue(nuevo.endswith("\n# X\n"))


if __name__ == "__main__":
    unittest.main()
