#!/usr/bin/env python3
"""Recalcula los cálculos de un informe de laboratorio y los compara con los del trabajo.

Uso:
    python calculos_lab.py calculos.json [--json salida.json]

El asistente escribe calculos.json con los datos que da el trabajo (no con los
que deberían ser). Formato completo y ejemplos en references/esquema.md:

{
  "tolerancia": 0.02,                      # relativa, por defecto 2 %
  "comprobaciones": [
    {"id": "c1", "tipo": "molaridad", "masa_g": 0.585, "pm_g_mol": 58.44, "volumen_mL": 100,
     "declarado": 0.1, "ubicacion": "Materiales y métodos, párr. 2"},
    {"id": "c2", "tipo": "dilucion", "c1": 2, "v1": null, "c2": 0.1, "v2": 10, "declarado": 0.2},
    {"id": "c3", "tipo": "dilucion_seriada", "c0": 1, "factor": 10, "pasos": 4, "declarado": [0.1, 0.01, 0.001, 0.0001]},
    {"id": "c4", "tipo": "henderson_hasselbalch", "pka": 7.21, "base": 0.06, "acido": 0.04, "declarado": 7.39},
    {"id": "c5", "tipo": "calibrado", "x": [...], "y": [...],
     "declarado": {"pendiente": 0.9, "ordenada": 0.01, "r2": 0.998},
     "muestras": [{"nombre": "A", "y": 0.45, "factor_dilucion": 10, "declarado": 4.9}]},
    {"id": "c6", "tipo": "lambert_beer", "absorbancia": 0.5, "epsilon": 6220, "l_cm": 1, "c": null, "declarado": 8.04e-5},
    {"id": "c7", "tipo": "rendimiento", "obtenido": 1.2, "teorico": 1.5, "declarado": 80},
    {"id": "c8", "tipo": "porcentaje", "parte": 3, "total": 12, "declarado": 25}
  ]
}

En «dilucion» y «lambert_beer», el dato que falta va como null y es lo que se
calcula. «declarado» es lo que dice el trabajo; puede ir como texto ("0,20")
para respetar sus decimales. Un valor coincide si la diferencia relativa no
supera la tolerancia o si es solo un redondeo del valor exacto a los decimales
que da el trabajo.

Código de salida: 0 si todo coincide, 2 si algo no coincide, 1 si el JSON está mal.
Solo librería estándar (sin numpy).
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path


class ErrorDatos(ValueError):
    pass


def numero(v, campo: str = "") -> float:
    if isinstance(v, bool) or v is None:
        raise ErrorDatos(f"falta el valor de «{campo}»")
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        t = v.strip().replace(" ", "").replace("−", "-")
        if t.count(",") == 1 and "." not in t:
            t = t.replace(",", ".")
        try:
            return float(t)
        except ValueError:
            pass
    raise ErrorDatos(f"«{campo}» no es un número: {v!r}")


def decimales(v) -> int | None:
    if isinstance(v, str):
        t = v.strip().replace(",", ".")
        if "e" in t.lower():
            return None
        return len(t.split(".")[1]) if "." in t else 0
    return None


def coincide(calculado: float, declarado, tolerancia: float) -> tuple[bool, float]:
    d = numero(declarado, "declarado")
    if calculado == 0:
        return abs(d) <= tolerancia, abs(d)
    rel = abs(d - calculado) / abs(calculado)
    dec = decimales(declarado)
    if dec is not None and round(calculado, dec) == round(d, dec):
        return True, rel
    if dec is not None and abs(d - calculado) <= 0.5 * 10 ** (-dec) + 1e-12:
        return True, rel
    return rel <= tolerancia, rel


def fmt(x: float, cifras: int = 4) -> str:
    if x == 0:
        return "0"
    if abs(x) >= 1e5 or abs(x) < 1e-3:
        return f"{x:.{cifras - 1}e}"
    dec = max(0, cifras - 1 - int(math.floor(math.log10(abs(x)))))
    return f"{x:.{dec}f}"


def resultado(c: dict, formula: str, valores: str, calculado: float, unidad: str, tolerancia: float, nota: str = "") -> dict:
    r = {"id": c.get("id", ""), "tipo": c["tipo"], "ubicacion": c.get("ubicacion", ""), "formula": formula,
         "valores": valores, "resultado": calculado, "resultado_texto": f"{fmt(calculado)} {unidad}".strip(),
         "unidad": unidad, "declarado": c.get("declarado"), "coincide": None, "diferencia_rel": None, "nota": nota}
    if c.get("declarado") is not None:
        ok, rel = coincide(calculado, c["declarado"], tolerancia)
        r["coincide"], r["diferencia_rel"] = ok, round(rel, 6)
    return r


# --- Tipos de cálculo ------------------------------------------------------------------------

def molaridad(c: dict, tol: float) -> list[dict]:
    masa = numero(c.get("masa_g", c.get("masa_mg", 0) / 1000 if "masa_mg" in c else None), "masa_g")
    pm = numero(c.get("pm_g_mol"), "pm_g_mol")
    if "volumen_L" in c:
        vol = numero(c["volumen_L"], "volumen_L")
    else:
        vol = numero(c.get("volumen_mL"), "volumen_mL") / 1000
    if pm <= 0 or vol <= 0:
        raise ErrorDatos("el peso molecular y el volumen tienen que ser positivos")
    m = masa / (pm * vol)
    return [resultado(c, "M = masa / (PM · V)", f"{fmt(masa)} g / ({fmt(pm)} g/mol · {fmt(vol)} L)", m, "M", tol)]


def dilucion(c: dict, tol: float) -> list[dict]:
    datos = {k: c.get(k) for k in ("c1", "v1", "c2", "v2")}
    falta = [k for k, v in datos.items() if v is None]
    if len(falta) != 1:
        raise ErrorDatos("en «dilucion» tiene que faltar exactamente uno de c1, v1, c2, v2 (como null)")
    k = falta[0]
    v = {x: numero(y, x) for x, y in datos.items() if y is not None}
    calc = {"c1": lambda: v["c2"] * v["v2"] / v["v1"], "v1": lambda: v["c2"] * v["v2"] / v["c1"],
            "c2": lambda: v["c1"] * v["v1"] / v["v2"], "v2": lambda: v["c1"] * v["v1"] / v["c2"]}[k]()
    despeje = {"c1": "C1 = C2·V2 / V1", "v1": "V1 = C2·V2 / C1", "c2": "C2 = C1·V1 / V2", "v2": "V2 = C1·V1 / C2"}[k]
    valores = ", ".join(f"{x.upper()} = {fmt(y)}" for x, y in v.items())
    unidad = c.get("unidad_v" if k.startswith("v") else "unidad_c", "")
    nota = ""
    if k == "v2" and c.get("declarado") is not None:
        # Error típico: dar el volumen de disolvente añadido (V2 − V1) en lugar del volumen final.
        if abs(numero(c["declarado"]) - (calc - v["v1"])) <= tol * calc:
            nota = "el valor del trabajo coincide con V2 − V1: parece el volumen de disolvente añadido, no el final"
    return [resultado(c, f"C1·V1 = C2·V2 → {despeje}", valores, calc, unidad, tol, nota)]


def dilucion_seriada(c: dict, tol: float) -> list[dict]:
    c0 = numero(c.get("c0"), "c0")
    factor = numero(c.get("factor"), "factor")
    pasos = int(numero(c.get("pasos", len(c.get("declarado") or [])), "pasos"))
    declarados = c.get("declarado") or [None] * pasos
    unidad = c.get("unidad", "")
    salida = []
    for n in range(1, pasos + 1):
        sub = dict(c, id=f"{c.get('id', '')}.{n}", declarado=declarados[n - 1] if n - 1 < len(declarados) else None)
        salida.append(resultado(sub, "Cn = C0 / factor^n", f"C0 = {fmt(c0)}, factor = {fmt(factor)}, n = {n}",
                                c0 / factor ** n, unidad, tol))
    return salida


def henderson(c: dict, tol: float) -> list[dict]:
    pka = numero(c.get("pka"), "pka")
    if c.get("ph_objetivo") is not None:
        ph = numero(c["ph_objetivo"], "ph_objetivo")
        cociente = 10 ** (ph - pka)
        return [resultado(c, "[A⁻]/[HA] = 10^(pH − pKa)", f"pH = {fmt(ph)}, pKa = {fmt(pka)}", cociente, "", tol)]
    base, acido = numero(c.get("base"), "base"), numero(c.get("acido"), "acido")
    if base <= 0 or acido <= 0:
        raise ErrorDatos("las concentraciones de base y ácido tienen que ser positivas")
    ph = pka + math.log10(base / acido)
    # El pH se compara en unidades absolutas: 0,02 unidades de tolerancia por defecto.
    r = resultado(c, "pH = pKa + log([A⁻]/[HA])", f"pKa = {fmt(pka)}, [A⁻] = {fmt(base)}, [HA] = {fmt(acido)}",
                  ph, "", tol)
    if c.get("declarado") is not None:
        d = numero(c["declarado"])
        dec = decimales(c["declarado"])
        tol_abs = c.get("tolerancia_ph", 0.02)
        r["coincide"] = abs(d - ph) <= tol_abs or (dec is not None and round(ph, dec) == round(d, dec))
        if not r["coincide"] and abs(d - (pka + math.log10(acido / base))) <= tol_abs:
            r["nota"] = "el valor del trabajo sale al invertir el cociente: usó [HA]/[A⁻] en vez de [A⁻]/[HA]"
    return [r]


def regresion(x: list[float], y: list[float]) -> tuple[float, float, float]:
    n = len(x)
    if n < 3 or n != len(y):
        raise ErrorDatos("la recta de calibrado necesita al menos 3 puntos y tantas x como y")
    mx, my = sum(x) / n, sum(y) / n
    sxx = sum((a - mx) ** 2 for a in x)
    if sxx == 0:
        raise ErrorDatos("todas las x son iguales")
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    m = sxy / sxx
    b = my - m * mx
    ss_tot = sum((v - my) ** 2 for v in y)
    ss_res = sum((v - (m * a + b)) ** 2 for a, v in zip(x, y))
    r2 = 1 - ss_res / ss_tot if ss_tot else 1.0
    return m, b, r2


def calibrado(c: dict, tol: float) -> list[dict]:
    x = [numero(v, "x") for v in c.get("x") or []]
    y = [numero(v, "y") for v in c.get("y") or []]
    m, b, r2 = regresion(x, y)
    dec = c.get("declarado") or {}
    ux, uy = c.get("unidad_x", ""), c.get("unidad_y", "")
    puntos = f"{len(x)} puntos, x de {fmt(min(x))} a {fmt(max(x))}"
    salida = []
    for clave, formula, calc, unidad in (
            ("pendiente", "m = Sxy / Sxx (mínimos cuadrados)", m,
             (f"{uy}/({ux})" if "/" in ux else f"{uy}/{ux}") if ux else ""),
            ("ordenada", "b = ȳ − m·x̄", b, uy),
            ("r2", "R² = 1 − SSres / SStot", r2, "")):
        sub = dict(c, id=f"{c.get('id', '')}.{clave}", declarado=dec.get(clave))
        r = resultado(sub, formula, puntos, calc, unidad, tol)
        if clave == "r2" and dec.get("r2") is not None:
            d = numero(dec["r2"])
            ndec = decimales(dec["r2"])
            ndec = ndec if ndec is not None else max(3, len(repr(d).split(".")[-1]))
            r["coincide"] = round(r2, ndec) == round(d, ndec) or abs(d - r2) <= 0.5 * 10 ** (-ndec) + 1e-12
            r["resultado_texto"] = f"{r2:.{max(4, ndec)}f}"
            if not r["coincide"] and abs(d - math.sqrt(r2)) <= 0.5 * 10 ** (-ndec) + 1e-12:
                r["nota"] = "el valor del trabajo coincide con r (correlación), no con R²"
        salida.append(r)
    for mu in c.get("muestras") or []:
        yy = numero(mu.get("y"), "muestras.y")
        f = numero(mu.get("factor_dilucion", 1), "factor_dilucion")
        xx = (yy - b) / m * f
        sub = dict(c, id=f"{c.get('id', '')}.{mu.get('nombre', '')}", declarado=mu.get("declarado"),
                   ubicacion=mu.get("ubicacion", c.get("ubicacion", "")))
        nota = ""
        if not min(y) <= yy <= max(y):
            nota = f"la señal ({fmt(yy)}) queda fuera del intervalo de la recta ({fmt(min(y))}-{fmt(max(y))}): es una extrapolación"
        r = resultado(sub, "x = (y − b) / m · factor de dilución",
                      f"muestra {mu.get('nombre', '')}: y = {fmt(yy)}, m = {fmt(m)}, b = {fmt(b)}, factor = {fmt(f)}",
                      xx, ux, tol, nota)
        if r["coincide"] is False and mu.get("declarado") is not None and f != 1:
            if coincide((yy - b) / m, mu["declarado"], tol)[0]:
                r["nota"] = "el valor del trabajo coincide con el resultado sin multiplicar por el factor de dilución"
        salida.append(r)
    return salida


def lambert_beer(c: dict, tol: float) -> list[dict]:
    datos = {"absorbancia": c.get("absorbancia"), "epsilon": c.get("epsilon"), "l_cm": c.get("l_cm", 1), "c": c.get("c")}
    falta = [k for k, v in datos.items() if v is None]
    if len(falta) != 1:
        raise ErrorDatos("en «lambert_beer» tiene que faltar exactamente uno de absorbancia, epsilon, l_cm, c (como null)")
    v = {k: numero(x, k) for k, x in datos.items() if x is not None}
    k = falta[0]
    calc = {"absorbancia": lambda: v["epsilon"] * v["l_cm"] * v["c"],
            "epsilon": lambda: v["absorbancia"] / (v["l_cm"] * v["c"]),
            "l_cm": lambda: v["absorbancia"] / (v["epsilon"] * v["c"]),
            "c": lambda: v["absorbancia"] / (v["epsilon"] * v["l_cm"])}[k]()
    despeje = {"absorbancia": "A = ε·l·c", "epsilon": "ε = A / (l·c)", "l_cm": "l = A / (ε·c)", "c": "c = A / (ε·l)"}[k]
    unidad = {"absorbancia": "", "epsilon": "M⁻¹·cm⁻¹", "l_cm": "cm", "c": "M"}[k]
    valores = ", ".join(f"{x} = {fmt(y)}" for x, y in v.items())
    nota = ""
    if k != "absorbancia" and v.get("absorbancia", 0) > 1.5:
        nota = "absorbancia > 1,5: fuera del intervalo lineal habitual de un espectrofotómetro"
    return [resultado(c, f"A = ε·l·c → {despeje}", valores, calc, c.get("unidad", unidad), tol, nota)]


def rendimiento(c: dict, tol: float) -> list[dict]:
    ob, te = numero(c.get("obtenido"), "obtenido"), numero(c.get("teorico"), "teorico")
    if te == 0:
        raise ErrorDatos("el valor teórico no puede ser 0")
    nota = "rendimiento > 100 %: revisar pureza, humedad o el cálculo del teórico" if ob > te else ""
    return [resultado(c, "rendimiento = obtenido / teórico · 100", f"{fmt(ob)} / {fmt(te)} · 100", ob / te * 100, "%",
                      tol, nota)]


def porcentaje(c: dict, tol: float) -> list[dict]:
    parte, total = numero(c.get("parte"), "parte"), numero(c.get("total"), "total")
    if total == 0:
        raise ErrorDatos("el total no puede ser 0")
    return [resultado(c, "% = parte / total · 100", f"{fmt(parte)} / {fmt(total)} · 100", parte / total * 100, "%", tol)]


CALCULOS = {"molaridad": molaridad, "dilucion": dilucion, "dilucion_seriada": dilucion_seriada,
            "henderson_hasselbalch": henderson, "calibrado": calibrado, "lambert_beer": lambert_beer,
            "rendimiento": rendimiento, "porcentaje": porcentaje}


def calcular(datos: dict) -> dict:
    tol = float(datos.get("tolerancia", 0.02))
    resultados, errores = [], []
    for c in datos.get("comprobaciones", []):
        tipo = c.get("tipo")
        if tipo not in CALCULOS:
            errores.append(f"{c.get('id', '?')}: tipo desconocido «{tipo}» (válidos: {', '.join(CALCULOS)})")
            continue
        try:
            resultados += CALCULOS[tipo](c, float(c.get("tolerancia", tol)))
        except ErrorDatos as e:
            errores.append(f"{c.get('id', '?')} ({tipo}): {e}")
    return {"tolerancia": tol, "resultados": resultados, "errores": errores,
            "no_coinciden": [r["id"] for r in resultados if r["coincide"] is False]}


def informe(r: dict) -> str:
    lineas = [f"Cálculos (tolerancia {r['tolerancia']:.0%}):"]
    for x in r["resultados"]:
        estado = {True: "OK", False: "NO COINCIDE", None: "sin valor del trabajo"}[x["coincide"]]
        decl = f"; el trabajo da {x['declarado']}" if x["declarado"] is not None else ""
        lineas.append(f"  [{estado}] {x['id']} {x['tipo']}: {x['formula']}")
        lineas.append(f"      {x['valores']} → {x['resultado_texto']}{decl}")
        if x["nota"]:
            lineas.append(f"      nota: {x['nota']}")
    for e in r["errores"]:
        lineas.append(f"  ERROR DE DATOS: {e}")
    lineas.append(f"No coinciden: {', '.join(r['no_coinciden']) or 'ninguno'}")
    return "\n".join(lineas)


def main(argv: list[str]) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    p = argparse.ArgumentParser(description="Recalcula los cálculos de un informe de laboratorio.")
    p.add_argument("calculos")
    p.add_argument("--json", dest="salida_json")
    a = p.parse_args(argv[1:])
    try:
        datos = json.loads(Path(a.calculos).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"No se puede leer {a.calculos}: {e}", file=sys.stderr)
        return 1
    r = calcular(datos)
    print(informe(r))
    if a.salida_json:
        Path(a.salida_json).write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    if r["errores"]:
        return 1
    return 2 if r["no_coinciden"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
