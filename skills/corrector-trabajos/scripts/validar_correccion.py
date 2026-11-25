#!/usr/bin/env python3
"""Valida el JSON de una corrección antes de generar el informe y los comentarios.

Uso:
    python validar_correccion.py correccion.json [--trabajo trabajo.docx]

ERRORES (se corrigen siempre; informe_html.py no genera nada con errores):
- campos obligatorios, ids repetidos, gravedad o criterio que no existen;
- un comentario de cálculo sin comprobación de calculos_lab.py que lo respalde,
  o cuya comprobación sí coincide (nunca se afirma un error de cálculo sin
  recalcularlo);
- un ejemplo de más de 2 frases o 50 palabras (la skill no reescribe el trabajo);
- pesos de la rúbrica que no suman 100, notas fuera de 0-10 o nota global que no
  es la media ponderada;
- con --trabajo: citas que no aparecen literales en el trabajo.

AVISOS (de tono y forma):
- más de 25 comentarios, menos de 2 o más de 4 puntos fuertes, prioridades ≠ 3;
- fórmulas prohibidas de references/tono.md;
- 3 o más comentarios que empiezan con las mismas 2 palabras;
- puntos fuertes genéricos.

Código: 0 sin problemas, 1 con errores, 2 solo con avisos. Solo librería estándar.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
TONO = SCRIPTS.parent / "references" / "tono.md"
sys.path.insert(0, str(SCRIPTS))

GRAVEDADES = ("critico", "importante", "menor")
TIPOS = ("laboratorio", "tecnico", "tfg", "ensayo", "bibliografico")
CAMPOS_COMENTARIO = ("id", "cita", "ubicacion", "gravedad", "categoria", "que_falla", "por_que_importa",
                     "como_arreglarlo", "criterio")
CATEGORIAS = ("estructura", "coherencia", "resultados_discusion", "figuras_tablas", "cifras_unidades", "calculo",
              "citas", "redaccion", "informatica", "contenido", "formato")
MAX_COMENTARIOS = 25
GENERICOS = re.compile(r"^(?:buen|bien|correct|adecuad|good|well|clear|claro)\w*\s+\w+\.?$|bien (?:estructurado|escrito|"
                       r"redactado|organizado)\.?$|buena (?:presentaci[oó]n|redacci[oó]n|estructura)\.?$", re.I)


def leer_prohibidas(ruta: Path = TONO) -> list[tuple[str, re.Pattern]]:
    patrones, dentro = [], False
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        if linea.startswith("## "):
            dentro = "prohibid" in linea.lower()
            continue
        if dentro and linea.startswith("|"):
            celda = linea.split("|")[1]
            for frase in re.findall(r"`([^`]+)`", celda):
                partes = [re.escape(p.strip()) for p in frase.lower().split("…")]
                patrones.append((frase, re.compile(r"(?<!\w)" + r"\b.{0,80}?\b".join(partes) + r"(?!\w)", re.I)))
    return patrones


def _frases(texto: str) -> int:
    return len([f for f in re.split(r"(?<=[.!?])\s+", texto.strip()) if f.strip()])


def _inicio(texto: str, n: int = 2) -> str:
    palabras = re.findall(r"\w+", (texto or "").lower())
    return " ".join(palabras[:n])


def nota_global(criterios: list[dict]) -> float:
    total = sum(float(c["peso"]) for c in criterios)
    return round(sum(float(c["peso"]) * float(c["nota"]) for c in criterios) / total, 1) if total else 0.0


def textos(corr: dict):
    for c in corr.get("comentarios", []):
        for campo in ("que_falla", "por_que_importa", "como_arreglarlo", "ejemplo"):
            if c.get(campo):
                yield f"{c.get('id', '?')}.{campo}", c[campo]
    for i, p in enumerate(corr.get("puntos_fuertes", []), 1):
        yield f"punto fuerte {i}", p.get("texto", "") if isinstance(p, dict) else str(p)
    for i, p in enumerate(corr.get("prioridades", []), 1):
        yield f"prioridad {i}", p.get("texto", "") if isinstance(p, dict) else str(p)
    for c in (corr.get("valoracion") or {}).get("criterios", []):
        if c.get("justificacion"):
            yield f"criterio {c.get('id', '?')}", c["justificacion"]
    if corr.get("resumen"):
        yield "resumen", corr["resumen"]


def validar(corr: dict, trabajo: str | Path | None = None) -> tuple[list[str], list[str]]:
    errores, avisos = [], []
    meta = corr.get("meta", {})
    if meta.get("tipo") not in TIPOS:
        errores.append(f"meta.tipo tiene que ser uno de {', '.join(TIPOS)} (es {meta.get('tipo')!r})")
    # Valoración
    val = corr.get("valoracion") or {}
    criterios = val.get("criterios", [])
    ids_criterio = {c.get("id") for c in criterios}
    if not criterios:
        errores.append("falta valoracion.criterios (la rúbrica con peso y nota de cada criterio)")
    else:
        for c in criterios:
            for campo in ("id", "nombre", "peso", "nota"):
                if c.get(campo) in (None, ""):
                    errores.append(f"criterio {c.get('id', '?')}: falta «{campo}»")
            if isinstance(c.get("nota"), (int, float)) and not 0 <= c["nota"] <= 10:
                errores.append(f"criterio {c.get('id')}: nota {c['nota']} fuera de 0-10")
        try:
            pesos = sum(float(c["peso"]) for c in criterios)
            if abs(pesos - 100) > 0.01:
                errores.append(f"los pesos de la rúbrica suman {pesos:g}, no 100")
            calculada = nota_global(criterios)
            if val.get("global") is not None and abs(float(val["global"]) - calculada) > 0.05:
                errores.append(f"valoracion.global es {val['global']}, pero la media ponderada da {calculada}")
        except (KeyError, TypeError, ValueError):
            pass
    # Cálculos de respaldo
    resultados = {r["id"]: r for r in ((corr.get("comprobaciones") or {}).get("calculos") or {}).get("resultados", [])}
    # Comentarios
    comentarios = corr.get("comentarios", [])
    vistos = set()
    for c in comentarios:
        cid = c.get("id", "?")
        if cid in vistos:
            errores.append(f"id repetido: {cid}")
        vistos.add(cid)
        for campo in CAMPOS_COMENTARIO:
            if not c.get(campo):
                errores.append(f"{cid}: falta «{campo}»")
        if c.get("gravedad") and c["gravedad"] not in GRAVEDADES:
            errores.append(f"{cid}: gravedad «{c['gravedad']}» (válidas: {', '.join(GRAVEDADES)})")
        if c.get("categoria") and c["categoria"] not in CATEGORIAS:
            errores.append(f"{cid}: categoría «{c['categoria']}» (válidas: {', '.join(CATEGORIAS)})")
        if criterios and c.get("criterio") and c["criterio"] not in ids_criterio:
            errores.append(f"{cid}: el criterio «{c['criterio']}» no está en la rúbrica")
        if c.get("categoria") == "calculo":
            ref = c.get("comprobacion")
            refs = ref if isinstance(ref, list) else [ref] if ref else []
            if not refs:
                errores.append(f"{cid}: comentario de cálculo sin «comprobacion»: recalcúlalo con calculos_lab.py "
                               "antes de afirmar que está mal")
            for r in refs:
                if r not in resultados:
                    errores.append(f"{cid}: la comprobación «{r}» no está en comprobaciones.calculos")
                elif resultados[r].get("coincide") is True:
                    errores.append(f"{cid}: la comprobación «{r}» coincide con el trabajo; no es un error de cálculo")
        if c.get("ejemplo"):
            if _frases(c["ejemplo"]) > 2 or len(c["ejemplo"].split()) > 50:
                errores.append(f"{cid}: el ejemplo tiene más de 2 frases o 50 palabras; la skill no reescribe el trabajo")
    if len(comentarios) > MAX_COMENTARIOS:
        avisos.append(f"{len(comentarios)} comentarios (máx. ~{MAX_COMENTARIOS}): agrupa los menores del mismo tipo")
    if comentarios and not any(c.get("gravedad") in ("critico", "importante") for c in comentarios) and \
            float(val.get("global") or 10) < 5:
        avisos.append("nota global por debajo de 5 sin ningún comentario crítico ni importante que lo explique")
    fuertes = corr.get("puntos_fuertes", [])
    if not 2 <= len(fuertes) <= 4:
        avisos.append(f"{len(fuertes)} puntos fuertes (tienen que ser 2-4, concretos)")
    for p in fuertes:
        t = p.get("texto", "") if isinstance(p, dict) else str(p)
        if GENERICOS.search(t.strip()) or len(t.split()) < 6:
            avisos.append(f"punto fuerte genérico: «{t}» (di qué está bien y dónde)")
    if len(corr.get("prioridades", [])) != 3:
        avisos.append(f"{len(corr.get('prioridades', []))} prioridades (tienen que ser los 3 cambios con más impacto)")
    # Tono
    for frase, patron in leer_prohibidas():
        for donde, t in textos(corr):
            if patron.search(t):
                avisos.append(f"{donde}: fórmula prohibida «{frase}» (references/tono.md)")
    for campo in ("que_falla", "como_arreglarlo"):
        inicios = Counter(_inicio(c.get(campo, "")) for c in comentarios if c.get(campo))
        for inicio, n in inicios.items():
            if n >= 3 and inicio:
                ids = [c["id"] for c in comentarios if _inicio(c.get(campo, "")) == inicio]
                avisos.append(f"{n} comentarios empiezan «{inicio}…» en {campo} ({', '.join(ids)}): varía el arranque")
    # Citas literales
    if trabajo:
        from extraer import cargar, normalizar
        doc = cargar(trabajo)
        texto = normalizar(re.sub(r"\^\{([^}]*)\}", r"\1", doc.texto()).replace("\t", " "))
        for c in comentarios:
            cita = normalizar(re.sub(r"\^\{([^}]*)\}", r"\1", c.get("cita", "")))
            if cita and cita not in texto:
                errores.append(f"{c.get('id', '?')}: la cita «{c['cita'][:60]}» no aparece literal en el trabajo")
    return errores, avisos


def informe(errores: list[str], avisos: list[str]) -> str:
    lineas = [f"ERRORES ({len(errores)}):" if errores else "ERRORES: ninguno"]
    lineas += [f"  - {e}" for e in errores]
    lineas.append(f"AVISOS ({len(avisos)}):" if avisos else "AVISOS: ninguno")
    lineas += [f"  - {a}" for a in avisos]
    return "\n".join(lineas)


def main(argv: list[str]) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    p = argparse.ArgumentParser(description="Valida el JSON de una corrección.")
    p.add_argument("correccion")
    p.add_argument("--trabajo")
    a = p.parse_args(argv[1:])
    corr = json.loads(Path(a.correccion).read_text(encoding="utf-8"))
    errores, avisos = validar(corr, a.trabajo)
    print(informe(errores, avisos))
    return 1 if errores else 2 if avisos else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
