# Esquema de la corrección

La corrección se guarda en `correccion-<nombre>.json`. De ese archivo salen el informe HTML (`informe_html.py`) y los comentarios de Word (`comentar_docx.py`), y es el que se compara si el alumno entrega otra versión (`comparar_versiones.py`). Se valida con `validar_correccion.py`.

## Estructura

```json
{
  "meta": {
    "titulo": "Práctica 3. Determinación de proteínas por Bradford",
    "archivo": "informe-bradford.docx",
    "tipo": "laboratorio",
    "asignatura": "Bioquímica I",
    "nivel": "grado, 2.º curso",
    "idioma": "es",
    "estilo_citas": "APA",
    "rubrica": "por defecto (informe de laboratorio)",
    "exigencia": "exigente",
    "fecha": "2026-11-25",
    "version": 1
  },
  "resumen": "Una o dos frases con lo esencial de la corrección.",
  "valoracion": {
    "criterios": [
      {"id": "C1", "nombre": "Estructura y presentación", "peso": 10, "nota": 7.5,
       "justificacion": "Por qué esa nota, con lo concreto que la sube o la baja."}
    ],
    "global": 6.4
  },
  "prioridades": [
    {"texto": "El cambio que más sube la nota, en una frase.", "comentarios": ["k01", "k04"]}
  ],
  "puntos_fuertes": [
    {"texto": "Algo concreto que está bien y conviene mantener.", "ubicacion": "Tabla 2"}
  ],
  "comentarios": [
    {
      "id": "k01",
      "cita": "se tomaron 0,25 mL de la disolución madre",
      "ubicacion": {"seccion": "3.2. Recta de calibrado", "pagina": 2, "parrafo": 1},
      "gravedad": "critico",
      "categoria": "calculo",
      "que_falla": "Qué está mal, en una frase.",
      "por_que_importa": "Qué consecuencia tiene.",
      "como_arreglarlo": "Qué hacer, sin redactarlo por el alumno.",
      "ejemplo": "Opcional: 1-2 frases que muestran la forma.",
      "criterio": "C3",
      "comprobacion": "c1",
      "casos": 3,
      "verificar": false
    }
  ],
  "comprobaciones": {
    "estructura": {},
    "referencias": {},
    "numeros": {},
    "calculos": {}
  },
  "version_anterior": {
    "arreglados": [{"id": "k02", "texto": "…"}],
    "siguen": [{"id": "k05", "texto": "…"}],
    "nuevos": [{"id": "k14", "texto": "…"}]
  }
}
```

## Campos

**meta.tipo:** `laboratorio`, `tecnico`, `tfg`, `ensayo` o `bibliografico`. **meta.idioma:** `es`, `eu` o `en`. El HTML sale en inglés si es `en` y en castellano en los demás casos. Los comentarios se escriben en el idioma del trabajo. **meta.version:** 1 en la primera corrección; sube con cada versión nueva.

**valoracion.criterios:** los de la rúbrica del usuario o los de `references/rubricas.md`, con el mismo `id`. Notas de 0 a 10 con un decimal; los pesos suman 100. `global` es la media ponderada redondeada a un decimal. Si no se pone, la calcula el script, y si no coincide, es un error.

**prioridades:** exactamente 3, ordenadas por lo que suben la nota. Cada una enlaza los comentarios que la explican.

**puntos_fuertes:** de 2 a 4, concretos y con ubicación.

**comentarios:** como mucho ~25, ordenados de más a menos grave.
- `cita`: copia **literal** del trabajo, de 3 a 25 palabras, dentro de un solo párrafo. Es el ancla del comentario en Word. Para un comentario sobre algo que falta (una sección, una cita), se cita el sitio donde debería estar, por ejemplo el título de la sección anterior. `validar_correccion.py --trabajo` comprueba que aparezca.
- `gravedad`: `critico`, `importante` o `menor` (criterios en `references/criterios.md`).
- `categoria`: `estructura`, `coherencia`, `resultados_discusion`, `figuras_tablas`, `cifras_unidades`, `calculo`, `citas`, `redaccion`, `informatica`, `contenido` o `formato`.
- `comprobacion`: obligatorio si `categoria` es `calculo`. Es el id (o la lista de ids) del resultado de `calculos_lab.py` que no coincide. Sin recálculo no hay comentario de cálculo.
- `ejemplo`: como mucho 2 frases y 50 palabras. Muestra la forma, no sustituye el párrafo del alumno.
- `casos`: en los comentarios que agrupan errores menores repetidos, cuántos hay.
- `verificar`: `true` si el comentario es una duda que el alumno debe contrastar con la bibliografía.

**comprobaciones:** se pega tal cual la salida `--json` de cada script: `revisar_estructura.py`, `revisar_referencias.py`, `revisar_numeros.py` y `calculos_lab.py`.

**version_anterior:** solo en correcciones de una versión nueva. Parte de la salida de `comparar_versiones.py`: lo que el script da como `cambiados` pasa a `arreglados` después de comprobarlo leyendo.

## Entrada de `calculos_lab.py`

Se rellena con los datos **tal como los da el trabajo**: las masas, los volúmenes y las lecturas del alumno, y en `declarado` el resultado que él obtuvo. Puede ir como texto (`"0,25"`) para conservar sus decimales.

```json
{
  "tolerancia": 0.02,
  "comprobaciones": [
    {"id": "c1", "tipo": "molaridad", "masa_g": 0.585, "pm_g_mol": 58.44, "volumen_mL": 100, "declarado": "0,1"},
    {"id": "c2", "tipo": "dilucion", "c1": 2, "v1": null, "c2": 0.5, "v2": 10, "unidad_v": "mL", "declarado": "0,25"},
    {"id": "c3", "tipo": "dilucion_seriada", "c0": 1, "factor": 10, "pasos": 3, "unidad": "mg/mL",
     "declarado": ["0,1", "0,01", "0,001"]},
    {"id": "c4", "tipo": "henderson_hasselbalch", "pka": 7.21, "base": 0.06, "acido": 0.04, "declarado": "7,39"},
    {"id": "c5", "tipo": "henderson_hasselbalch", "pka": 4.76, "ph_objetivo": 5.0, "declarado": "1,74"},
    {"id": "c6", "tipo": "calibrado", "x": [0, 0.1, 0.2], "y": [0.0, 0.11, 0.21], "unidad_x": "mg/mL",
     "unidad_y": "A595", "declarado": {"pendiente": "1,05", "ordenada": "0,002", "r2": "0,999"},
     "muestras": [{"nombre": "A", "y": 0.15, "factor_dilucion": 10, "declarado": "1,4"}]},
    {"id": "c7", "tipo": "lambert_beer", "absorbancia": 0.5, "epsilon": 6220, "l_cm": 1, "c": null, "declarado": "8,0e-5"},
    {"id": "c8", "tipo": "rendimiento", "obtenido": 1.2, "teorico": 1.5, "declarado": "80"},
    {"id": "c9", "tipo": "porcentaje", "parte": 3, "total": 12, "declarado": "25"}
  ]
}
```

- `dilucion` y `lambert_beer`: el dato que se calcula va como `null`. Las unidades de c1/c2 y de v1/v2 tienen que ser las mismas.
- `henderson_hasselbalch`: con `base` y `acido` calcula el pH; con `ph_objetivo`, el cociente [A⁻]/[HA]. El pH se compara con 0,02 unidades de margen (`tolerancia_ph`).
- `calibrado`: devuelve pendiente, ordenada y R², y la concentración de cada muestra (multiplicada por su `factor_dilucion`). Sus ids son `c6.pendiente`, `c6.ordenada`, `c6.r2` y `c6.<muestra>`, que son los que cita `comprobacion`.
- Un resultado «coincide» si la diferencia relativa no pasa de la tolerancia (2 % por defecto) o si es el valor exacto redondeado a los decimales que da el trabajo. El R² se compara siempre a los decimales del trabajo.
