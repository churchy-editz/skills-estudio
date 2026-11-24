"""Tests de tools/comprobar_independencia.py.

Ejecutar desde la raíz del repo:
    python -m unittest discover -s tools/tests -v
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
REPO = TOOLS.parent
SCRIPT = TOOLS / "comprobar_independencia.py"

_spec = importlib.util.spec_from_file_location("comprobar_independencia", SCRIPT)
ci = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ci)


def crear_repo(tmp: Path, archivos: dict[str, str]) -> Path:
    for ruta, texto in archivos.items():
        f = tmp / ruta
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(texto, encoding="utf-8")
    return tmp


class TestIndependencia(unittest.TestCase):
    def test_repo_real_independiente(self):
        r = subprocess.run([sys.executable, str(SCRIPT), str(REPO)], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("creador-tests", r.stdout)

    def test_detecta_rutas_a_otra_skill(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = crear_repo(Path(tmp), {
                "skill-a/SKILL.md": "Lee `skill-b/references/tono.md`.\n",
                "skill-a/scripts/x.py": "RUTA = '../skill-b/assets/p.html'\n",
                "skill-a/references/r.md": "Ver skill-b\\scripts\\y.py\n",
                "skill-b/SKILL.md": "Nada.\n",
            })
            problemas = ci.comprobar(raiz)
        self.assertEqual(len(problemas), 3, problemas)
        self.assertTrue(problemas[0].startswith("skill-a/SKILL.md:1:"))

    def test_permite_nombrar_otra_skill_sin_ruta(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = crear_repo(Path(tmp), {
                "skill-a/SKILL.md": "Acepta los apuntes de skill-b. Ver mi-skill-b/ (otra cosa).\n",
                "skill-a/examples/e.json": "{\"fuente\": \"skill-b/examples/f.md\"}\n",
                "skill-b/SKILL.md": "Nada.\n",
            })
            self.assertEqual(ci.comprobar(raiz), [])

    def test_codigo_de_salida_con_problemas(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = crear_repo(Path(tmp), {
                "skill-a/SKILL.md": "Usa skill-b/scripts/z.py\n",
                "skill-b/SKILL.md": "Nada.\n",
            })
            r = subprocess.run([sys.executable, str(SCRIPT), str(raiz)], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 1)
        self.assertIn("skill-a/SKILL.md:1", r.stdout)


if __name__ == "__main__":
    unittest.main()
