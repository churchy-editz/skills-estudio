#!/usr/bin/env python3
"""Genera el informe de corrección (HTML autocontenido) a partir del JSON.

Uso:
    python informe_html.py correccion-<nombre>.json correccion-<nombre>.html [--paleta ciencias]

Antes valida el JSON con validar_correccion.py: con errores no genera nada; los
avisos se muestran pero no bloquean. El HTML incluye la valoración orientativa
por criterio y global, los 3 cambios con más impacto, los puntos fuertes, los
comentarios por gravedad (filtrables), las comprobaciones de los scripts (los
cálculos con su fórmula) y, si existe, la comparación con la versión anterior.
Se imprime bien en papel. Solo librería estándar.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validar_correccion import informe as informe_validacion, nota_global, validar  # noqa: E402

SANS = 'system-ui, "Segoe UI", Roboto, Arial, sans-serif'
SERIF = 'Georgia, Cambria, "Times New Roman", serif'
# fondo, texto, def (menor), ejemplo (fuerte), ojo (crítico), clave (importante), fuente. Contraste WCAG AA verificado.
PALETAS = {
    "neutra":      ("#ffffff", "#1f1f1f", "#1f5f8b", "#2e6b30", "#a3261b", "#7a4b00", SANS),
    "ciencias":    ("#fbfdfb", "#18261f", "#0b6e69", "#3d6b1f", "#b02a1f", "#6b3fa0", SANS),
    "matematicas": ("#fdfdfd", "#1a1c24", "#1d4e89", "#2f6b4f", "#b3261e", "#8a4b00", SANS),
    "historia":    ("#fcf9f2", "#2b2118", "#7a3e12", "#4f6228", "#9e1c1c", "#23527c", SERIF),
    "lengua":      ("#fffdf9", "#241b26", "#6a2c70", "#1f6f6b", "#a8321e", "#8a5a00", SERIF),
    "idiomas":     ("#fafcff", "#1a2230", "#1560a0", "#1b7340", "#b4261a", "#7b3f98", SANS),
    "derecho":     ("#ffffff", "#1b1b1b", "#1c3d6e", "#3f5f3a", "#8f1d1d", "#6b4e16", SERIF),
    "economia":    ("#fbfcfd", "#1c2329", "#0f5c6e", "#2f6b2f", "#b03a12", "#5b3d99", SANS),
    "arte":        ("#fdfbf8", "#2a2226", "#8a2f4c", "#2d6a5e", "#a32d1a", "#5a4a8a", SERIF),
}
ALIAS = {"biologia": "ciencias", "bioquimica": "ciencias", "quimica": "ciencias", "fisica": "ciencias",
         "informatica": "matematicas", "ingenieria": "matematicas", "estadistica": "matematicas"}

TXT = {
    "es": {"orientativa": "Valoración orientativa. La nota real la pone tu profesor con su rúbrica; esta sirve para "
                          "saber dónde se pierden puntos.", "global": "Nota orientativa", "criterio": "Criterio",
           "peso": "Peso", "nota": "Nota", "por_que": "Por qué", "prioridades": "Los 3 cambios que más suben la nota",
           "fuertes": "Puntos fuertes", "comentarios": "Comentarios", "todos": "Todos", "critico": "Crítico",
           "importante": "Importante", "menor": "Menor", "criticos": "críticos", "importantes": "importantes", "menores": "menores", "que_falla": "Qué falla", "por_que_importa": "Por qué importa",
           "como": "Cómo arreglarlo", "ejemplo": "Por ejemplo", "comprobaciones": "Comprobaciones automáticas",
           "calculos": "Cálculos recalculados", "estructura": "Estructura", "referencias": "Citas y bibliografía",
           "numeros": "Cifras y unidades", "formula": "Fórmula", "valores": "Datos", "resultado": "Resultado",
           "trabajo": "En el trabajo", "estado": "Estado", "coincide": "Coincide", "no_coincide": "No coincide",
           "sin_dato": "Sin dato", "ninguno": "Sin avisos.", "version": "Respecto a la versión anterior",
           "arreglados": "Arreglado", "siguen": "Sigue igual", "nuevos": "Nuevo", "verificar": "Verificar con la bibliografía",
           "casos": "casos", "pie": "Corrección hecha con la skill corrector-trabajos. Los comentarios señalan qué "
                                   "cambiar; la redacción sigue siendo tuya.", "rubrica": "Rúbrica",
           "tipo": {"laboratorio": "Informe de laboratorio", "tecnico": "Memoria de prácticas / informe técnico",
                    "tfg": "TFG / TFM", "ensayo": "Ensayo / trabajo teórico", "bibliografico": "Trabajo bibliográfico"}},
    "en": {"orientativa": "Indicative grade. Your lecturer sets the real mark with their own rubric; this one shows "
                          "where marks are lost.", "global": "Indicative grade", "criterio": "Criterion",
           "peso": "Weight", "nota": "Grade", "por_que": "Why", "prioridades": "The 3 changes that raise the grade most",
           "fuertes": "Strengths", "comentarios": "Comments", "todos": "All", "critico": "Critical",
           "importante": "Major", "menor": "Minor", "criticos": "critical", "importantes": "major", "menores": "minor", "que_falla": "What is wrong", "por_que_importa": "Why it matters",
           "como": "How to fix it", "ejemplo": "For example", "comprobaciones": "Automatic checks",
           "calculos": "Recalculated values", "estructura": "Structure", "referencias": "Citations and references",
           "numeros": "Numbers and units", "formula": "Formula", "valores": "Data", "resultado": "Result",
           "trabajo": "In the work", "estado": "Status", "coincide": "Matches", "no_coincide": "Does not match",
           "sin_dato": "No value", "ninguno": "No warnings.", "version": "Compared with the previous version",
           "arreglados": "Fixed", "siguen": "Unchanged", "nuevos": "New", "verificar": "Check against the literature",
           "casos": "cases", "pie": "Feedback produced with the corrector-trabajos skill. The comments say what to "
                                   "change; the writing is still yours.", "rubrica": "Rubric",
           "tipo": {"laboratorio": "Lab report", "tecnico": "Technical report", "tfg": "Final-year project",
                    "ensayo": "Essay", "bibliografico": "Literature review"}},
}
ORDEN = ("critico", "importante", "menor")
PLURAL = {"critico": "criticos", "importante": "importantes", "menor": "menores"}


def e(t) -> str:
    return html.escape(str(t if t is not None else ""))


def paleta_css(nombre: str) -> str:
    clave = ALIAS.get(nombre, nombre)
    fondo, texto, menor, fuerte, critico, importante, fuente = PALETAS.get(clave, PALETAS["neutra"])
    return (f"--fondo:{fondo};--texto:{texto};--menor:{menor};--fuerte:{fuerte};--critico:{critico};"
            f"--importante:{importante};--fuente:{fuente};")


def decimal(texto: str, idioma: str) -> str:
    """Coma decimal en los resultados de los scripts si el trabajo no está en inglés."""
    return texto if idioma == "en" else re.sub(r"(?<=\d)\.(?=\d)", ",", texto)


def num(x, idioma: str, dec: int = 1) -> str:
    t = f"{float(x):.{dec}f}"
    return t.replace(".", ",") if idioma != "en" else t


CSS = """
*{box-sizing:border-box}
body{margin:0;background:var(--fondo);color:var(--texto);font:16px/1.55 var(--fuente)}
main{max-width:920px;margin:0 auto;padding:28px 18px 60px}
h1{font-size:1.6rem;margin:0 0 4px;line-height:1.25}
h2{font-size:1.2rem;margin:36px 0 12px;padding-bottom:4px;border-bottom:2px solid color-mix(in srgb,var(--texto) 15%,var(--fondo))}
h3{font-size:1rem;margin:20px 0 8px}
.meta{color:color-mix(in srgb,var(--texto) 72%,var(--fondo));font-size:.92rem;margin:0}
.aviso{border-left:4px solid var(--importante);background:color-mix(in srgb,var(--importante) 9%,var(--fondo));padding:10px 14px;margin:18px 0;font-size:.93rem}
.nota{display:flex;gap:22px;align-items:center;flex-wrap:wrap;margin:18px 0}
.nota .cifra{font-size:2.6rem;font-weight:700;line-height:1}
.nota .cifra small{font-size:1rem;font-weight:400}
.recuento{display:flex;gap:8px;flex-wrap:wrap}
.chip{border:1.5px solid currentColor;border-radius:999px;padding:2px 10px;font-size:.85rem;font-weight:600}
.critico{color:var(--critico)}.importante{color:var(--importante)}.menor{color:var(--menor)}.fuerte{color:var(--fuerte)}
table{border-collapse:collapse;width:100%;font-size:.92rem;margin:8px 0}
th,td{border-bottom:1px solid color-mix(in srgb,var(--texto) 14%,var(--fondo));padding:7px 8px;text-align:left;vertical-align:top}
th{font-weight:600}
td.n{text-align:right;white-space:nowrap}
.barra{height:8px;background:color-mix(in srgb,var(--texto) 10%,var(--fondo));border-radius:4px;min-width:80px}
.barra span{display:block;height:100%;border-radius:4px;background:var(--menor)}
ol.prioridades{padding-left:1.3em}ol.prioridades li{margin:6px 0}
ul.fuertes{list-style:none;padding:0}
ul.fuertes li{border-left:4px solid var(--fuerte);background:color-mix(in srgb,var(--fuerte) 8%,var(--fondo));padding:8px 12px;margin:8px 0}
ul.fuertes li b{color:var(--fuerte)}
.filtros{display:flex;gap:8px;flex-wrap:wrap;margin:10px 0 4px}
.filtros button{font:inherit;font-size:.88rem;padding:4px 12px;border-radius:999px;border:1.5px solid color-mix(in srgb,var(--texto) 35%,var(--fondo));background:var(--fondo);color:var(--texto);cursor:pointer}
.filtros button[aria-pressed=true]{background:var(--texto);color:var(--fondo);border-color:var(--texto)}
.filtros button:focus-visible{outline:3px solid var(--menor);outline-offset:2px}
article.c{border:1px solid color-mix(in srgb,var(--texto) 16%,var(--fondo));border-left:5px solid var(--g);border-radius:6px;padding:12px 16px;margin:14px 0;break-inside:avoid}
article.c[data-g=critico]{--g:var(--critico)}article.c[data-g=importante]{--g:var(--importante)}article.c[data-g=menor]{--g:var(--menor)}
.cab{display:flex;gap:10px;align-items:baseline;flex-wrap:wrap;font-size:.86rem}
.cab .g{font-weight:700;text-transform:uppercase;letter-spacing:.04em;color:var(--g)}
.cab .donde{color:color-mix(in srgb,var(--texto) 70%,var(--fondo))}
blockquote{margin:8px 0;padding:6px 12px;border-left:3px solid color-mix(in srgb,var(--texto) 25%,var(--fondo));background:color-mix(in srgb,var(--texto) 4%,var(--fondo));font-style:italic}
dl{margin:6px 0 0;display:grid;grid-template-columns:max-content 1fr;gap:4px 12px}
dt{font-weight:600}dd{margin:0}
.ej{font-style:italic}
.ok{color:var(--fuerte);font-weight:600}.mal{color:var(--critico);font-weight:600}.nd{color:color-mix(in srgb,var(--texto) 60%,var(--fondo))}
code{font-size:.88em;background:color-mix(in srgb,var(--texto) 6%,var(--fondo));padding:1px 4px;border-radius:3px}
footer{margin-top:40px;font-size:.85rem;color:color-mix(in srgb,var(--texto) 65%,var(--fondo))}
@media (max-width:620px){dl{grid-template-columns:1fr}.nota .cifra{font-size:2.1rem}table{font-size:.85rem}}
@media print{.filtros{display:none}article.c{display:block!important}main{padding:0}body{font-size:11pt}h2{break-after:avoid}}
"""

JS = """
document.querySelectorAll('.filtros button').forEach(function(b){b.addEventListener('click',function(){
var g=b.dataset.g;document.querySelectorAll('.filtros button').forEach(function(x){x.setAttribute('aria-pressed',x===b?'true':'false')});
document.querySelectorAll('article.c').forEach(function(a){a.style.display=(g==='todos'||a.dataset.g===g)?'':'none'});});});
"""


def _ubicacion(u) -> str:
    if isinstance(u, dict):
        partes = [u.get("seccion", "")]
        if u.get("pagina"):
            partes.append(f"p. {u['pagina']}")
        if u.get("parrafo"):
            partes.append(f"párr. {u['parrafo']}")
        return ", ".join(p for p in partes if p)
    return str(u or "")


def _avisos_script(r: dict | None, t: dict) -> str:
    if not r:
        return ""
    avisos = r.get("avisos", [])
    if not avisos:
        return f"<p>{e(t['ninguno'])}</p>"
    items = []
    for a in avisos:
        g = a.get("gravedad", "menor")
        items.append(f'<li><span class="{e(g)}">[{e(t.get(g, g))}]</span> {e(a.get("detalle", ""))}'
                     + (f' <span class="nd">({e(a["seccion"])})</span>' if a.get("seccion") else "") + "</li>")
    return "<ul>" + "".join(items) + "</ul>"


def generar(corr: dict, paleta: str = "neutra") -> str:
    meta = corr.get("meta", {})
    idioma = "en" if str(meta.get("idioma", "es")).lower().startswith("en") else "es"
    t = TXT[idioma]
    val = corr.get("valoracion", {})
    criterios = val.get("criterios", [])
    global_ = val.get("global") if val.get("global") is not None else nota_global(criterios)
    comentarios = sorted(corr.get("comentarios", []), key=lambda c: (ORDEN.index(c.get("gravedad", "menor"))
                                                                       if c.get("gravedad") in ORDEN else 3))
    nombres_criterio = {c["id"]: c["nombre"] for c in criterios}
    cuenta = {g: sum(1 for c in comentarios if c.get("gravedad") == g) for g in ORDEN}
    h = [f'<!doctype html><html lang="{idioma}"><head><meta charset="utf-8">'
         '<meta name="viewport" content="width=device-width,initial-scale=1">'
         f'<title>{e(meta.get("titulo", "Corrección"))}</title>'
         f'<style>:root{{{paleta_css(paleta)}}}{CSS}</style></head><body><main>']
    h.append(f'<h1>{e(meta.get("titulo", ""))}</h1>')
    detalles = [t["tipo"].get(meta.get("tipo", ""), meta.get("tipo", "")), meta.get("asignatura", ""),
                meta.get("nivel", ""), meta.get("fecha", "")]
    h.append(f'<p class="meta">{e(" · ".join(d for d in detalles if d))}</p>')
    if meta.get("rubrica"):
        h.append(f'<p class="meta">{e(t["rubrica"])}: {e(meta["rubrica"])}'
                 + (f' · {e(meta["exigencia"])}' if meta.get("exigencia") else "") + "</p>")
    # Valoración
    h.append(f'<div class="nota"><div><div class="cifra">{num(global_, idioma)}<small> / 10</small></div>'
             f'<div class="meta">{e(t["global"])}</div></div><div class="recuento">'
             + "".join(f'<span class="chip {g}">{cuenta[g]} {e(t[g].lower() if cuenta[g] == 1 else t[PLURAL[g]])}</span>'
                       for g in ORDEN if cuenta[g])
             + "</div></div>")
    h.append(f'<p class="aviso">{e(t["orientativa"])}</p>')
    if corr.get("resumen"):
        h.append(f"<p>{e(corr['resumen'])}</p>")
    h.append(f'<table><thead><tr><th>{e(t["criterio"])}</th><th class="n">{e(t["peso"])}</th><th class="n">{e(t["nota"])}</th>'
             f'<th aria-hidden="true"></th><th>{e(t["por_que"])}</th></tr></thead><tbody>')
    for c in criterios:
        h.append(f'<tr><td>{e(c["nombre"])}</td><td class="n">{e(c["peso"])} %</td><td class="n">{num(c["nota"], idioma)}</td>'
                 f'<td><div class="barra"><span style="width:{float(c["nota"]) * 10:.0f}%"></span></div></td>'
                 f'<td>{e(c.get("justificacion", ""))}</td></tr>')
    h.append("</tbody></table>")
    # Prioridades y puntos fuertes
    if corr.get("prioridades"):
        h.append(f'<h2>{e(t["prioridades"])}</h2><ol class="prioridades">')
        for p in corr["prioridades"]:
            texto = p.get("texto", "") if isinstance(p, dict) else str(p)
            refs = p.get("comentarios", []) if isinstance(p, dict) else []
            enlaces = " ".join(f'<a href="#{e(r)}">{e(r)}</a>' for r in refs)
            h.append(f"<li>{e(texto)}{' (' + enlaces + ')' if enlaces else ''}</li>")
        h.append("</ol>")
    if corr.get("puntos_fuertes"):
        h.append(f'<h2>{e(t["fuertes"])}</h2><ul class="fuertes">')
        for p in corr["puntos_fuertes"]:
            texto = p.get("texto", "") if isinstance(p, dict) else str(p)
            donde = p.get("ubicacion", "") if isinstance(p, dict) else ""
            sitio = f' <span class="nd">({e(_ubicacion(donde))})</span>' if donde else ""
            h.append(f"<li>{e(texto)}{sitio}</li>")
        h.append("</ul>")
    # Comentarios
    h.append(f'<h2>{e(t["comentarios"])} ({len(comentarios)})</h2>')
    h.append(f'<div class="filtros" role="group" aria-label="{e(t["comentarios"])}">'
             f'<button type="button" data-g="todos" aria-pressed="true">{e(t["todos"])}</button>'
             + "".join(f'<button type="button" data-g="{g}" aria-pressed="false">{e(t[g])} ({cuenta[g]})</button>'
                       for g in ORDEN if cuenta[g]) + "</div>")
    for c in comentarios:
        g = c.get("gravedad", "menor")
        criterio = c.get("criterio", "")
        criterio_txt = f"{criterio} · {nombres_criterio.get(criterio, '')}" if criterio in nombres_criterio else criterio
        extra = []
        if c.get("casos"):
            extra.append(f'{c["casos"]} {t["casos"]}')
        if c.get("verificar"):
            extra.append(t["verificar"])
        h.append(f'<article class="c" id="{e(c.get("id"))}" data-g="{e(g)}"><div class="cab">'
                 f'<span class="g">{e(t.get(g, g))}</span><span>{e(c.get("id"))}</span>'
                 f'<span class="donde">{e(_ubicacion(c.get("ubicacion")))}</span>'
                 f'<span class="donde">{e(criterio_txt)}</span>'
                 + "".join(f'<span class="chip {g}">{e(x)}</span>' for x in extra) + "</div>")
        h.append(f'<blockquote>{e(c.get("cita"))}</blockquote><dl>')
        h.append(f'<dt>{e(t["que_falla"])}</dt><dd>{e(c.get("que_falla"))}</dd>')
        if c.get("por_que_importa"):
            h.append(f'<dt>{e(t["por_que_importa"])}</dt><dd>{e(c["por_que_importa"])}</dd>')
        h.append(f'<dt>{e(t["como"])}</dt><dd>{e(c.get("como_arreglarlo"))}</dd>')
        if c.get("ejemplo"):
            h.append(f'<dt>{e(t["ejemplo"])}</dt><dd class="ej">{e(c["ejemplo"])}</dd>')
        h.append("</dl></article>")
    # Versión anterior
    va = corr.get("version_anterior")
    if va:
        h.append(f'<h2>{e(t["version"])}</h2><table><tbody>')
        for clave in ("arreglados", "siguen", "nuevos"):
            items = va.get(clave, [])
            h.append(f'<tr><th>{e(t[clave])} ({len(items)})</th><td>'
                     + "<br>".join(e(i.get("texto", i) if isinstance(i, dict) else i) for i in items) + "</td></tr>")
        h.append("</tbody></table>")
    # Comprobaciones de los scripts
    comp = corr.get("comprobaciones") or {}
    if comp:
        h.append(f'<h2>{e(t["comprobaciones"])}</h2>')
        calc = comp.get("calculos")
        if calc and calc.get("resultados"):
            h.append(f'<h3>{e(t["calculos"])}</h3><table><thead><tr><th>Id</th><th>{e(t["formula"])}</th>'
                     f'<th>{e(t["valores"])}</th><th class="n">{e(t["resultado"])}</th><th class="n">{e(t["trabajo"])}</th>'
                     f'<th>{e(t["estado"])}</th></tr></thead><tbody>')
            for r in calc["resultados"]:
                estado = {True: f'<span class="ok">{e(t["coincide"])}</span>',
                          False: f'<span class="mal">{e(t["no_coincide"])}</span>',
                          None: f'<span class="nd">{e(t["sin_dato"])}</span>'}[r.get("coincide")]
                nota = f'<br><span class="nd">{e(r["nota"])}</span>' if r.get("nota") else ""
                ubic = f'<br><span class="nd">{e(r["ubicacion"])}</span>' if r.get("ubicacion") else ""
                h.append(f'<tr><td>{e(r["id"])}</td><td><code>{e(r["formula"])}</code>{ubic}</td>'
                         f'<td>{e(decimal(r["valores"], idioma))}</td>'
                         f'<td class="n">{e(decimal(r["resultado_texto"], idioma))}</td>'
                         f'<td class="n">{e(r["declarado"] if r.get("declarado") is not None else "—")}</td>'
                         f'<td>{estado}{nota}</td></tr>')
            h.append("</tbody></table>")
        for clave in ("estructura", "referencias", "numeros"):
            if comp.get(clave):
                h.append(f'<h3>{e(t[clave])}</h3>' + _avisos_script(comp[clave], t))
    h.append(f'<footer>{e(t["pie"])}</footer></main><script>{JS}</script></body></html>')
    return "\n".join(h)


def main(argv: list[str]) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    p = argparse.ArgumentParser(description="Genera el informe HTML de una corrección.")
    p.add_argument("correccion")
    p.add_argument("salida")
    p.add_argument("--paleta", default="neutra")
    a = p.parse_args(argv[1:])
    corr = json.loads(Path(a.correccion).read_text(encoding="utf-8"))
    errores, avisos = validar(corr)
    if errores or avisos:
        print(informe_validacion(errores, avisos))
    if errores:
        print("No se genera el HTML: corrige los errores del JSON.", file=sys.stderr)
        return 1
    Path(a.salida).write_text(generar(corr, a.paleta), encoding="utf-8")
    print(f"{a.salida}: {len(corr.get('comentarios', []))} comentarios")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
