---
name: corrector-trabajos
description: >-
  Corrige trabajos universitarios (informes de laboratorio, memorias de prácticas,
  informes técnicos, TFG/TFM, ensayos y trabajos bibliográficos) como un profesor
  con tiempo: señala errores concretos con la cita exacta, explica por qué lo son y
  cómo arreglarlos, recalcula los cálculos de laboratorio, contrasta citas y
  bibliografía, revisa figuras, tablas y unidades, y da una valoración orientativa
  por criterios. Entrega un informe HTML y, si el trabajo es un DOCX, una copia con
  comentarios de Word. No reescribe el trabajo. Usar cuando el usuario diga
  "corrígeme este trabajo", "revisa mi informe de prácticas", "revisa mi informe de
  laboratorio", "qué nota sacaría esto", "revisa mi TFG", "review my lab report" o
  "proofread my essay", o pida corregir, revisar o valorar un trabajo académico.
license: MIT
compatibility: Python 3.11 o posterior para las comprobaciones; python-docx para leer DOCX y escribir los comentarios de Word.
---

# Corrector de trabajos

El asistente corrige como un profesor que tiene tiempo. Para cada error señala el sitio exacto, dice por qué es un error y explica cómo arreglarlo. Al final da una valoración orientativa. El trabajo es del alumno: el asistente **no lo reescribe**, y como mucho añade a un comentario un ejemplo de 1-2 frases que muestre la forma.

## 1. Entrada

- El trabajo, en DOCX, PDF con texto, Markdown, LaTeX o TXT. `python scripts/extraer.py trabajo.docx trabajo.md` lo pasa a texto con sus secciones, tablas y leyendas. Un PDF escaneado se transcribe antes.
- Opcional: el enunciado, la rúbrica o la guía de la asignatura. Si existen, mandan sobre los valores por defecto.
- Se lee el trabajo entero antes de comentar nada.

## 2. Detectar antes de preguntar

- **Tipo:** informe de laboratorio (`laboratorio`), memoria de prácticas o informe técnico (`tecnico`), TFG/TFM (`tfg`), ensayo o trabajo teórico (`ensayo`) o trabajo bibliográfico (`bibliografico`).
- **Nivel:** curso y titulación, si se deducen.
- **Idioma:** castellano, euskera o inglés. Se responde en el idioma del trabajo salvo que el usuario pida otro.
- **Estilo de citas:** APA, Vancouver, IEEE u otro (`revisar_referencias.py` lo detecta).

## 3. Una sola pregunta

Se hace UNA pregunta y se omite lo que el usuario ya haya dicho:

> Lo veo como [tipo], en [idioma]. Para corregirlo bien (responde "ok" si no tienes nada):
> - ¿Tienes el enunciado o la rúbrica? Pégalos o adjúntalos.
> - Exigencia: orientativa / como un profesor exigente [defecto: exigente]
> - ¿Algo en concreto que te preocupe?

Sin rúbrica se usa la del tipo detectado en `references/rubricas.md`, y se dice en el informe.

## 4. Proceso

1. **Lectura completa.** Se anota el objetivo de cada sección y los datos clave.
2. **Scripts** (punto 6), siempre todos los que apliquen.
3. **Revisión por criterios de la rúbrica**, con `references/criterios.md` y `references/errores-frecuentes.md`. Cada aviso de un script se confirma leyendo el trabajo; los falsos positivos se descartan.
4. **Priorizar** (punto 8).
5. **Escribir `correccion-<nombre>.json`** según `references/esquema.md` y validarlo con `python scripts/validar_correccion.py correccion-<nombre>.json --trabajo <trabajo>`. Los errores se corrigen siempre. Los avisos de tono, en un máximo de 3 rondas.
6. **Autorrevisión** (punto 11) y entrega (punto 9).

## 5. Qué se revisa

Detalle, gravedades y ejemplos en `references/criterios.md`.
- **Estructura:** secciones esperadas según el tipo (laboratorio: introducción y objetivos, materiales y métodos, resultados, discusión, conclusiones, bibliografía; memoria técnica: objetivos, análisis, diseño, implementación, pruebas, conclusiones).
- **Coherencia:** objetivos ↔ resultados ↔ conclusiones. Las conclusiones solo afirman lo que muestran los resultados.
- **Resultados frente a discusión:** datos en resultados e interpretación en discusión, sin mezclarlos.
- **Figuras y tablas:** numeradas, con leyenda, citadas en el texto y con unidades en ejes y cabeceras.
- **Cifras y unidades:** unidades del SI bien escritas, cifras significativas coherentes, las mismas cifras en tablas y texto.
- **Cálculos (laboratorio):** se recalculan con el script y se comparan.
- **Citas y bibliografía:** toda cita tiene entrada y toda entrada se cita, con un formato consistente.
- **Redacción:** claridad, registro académico, voz impersonal donde toque, frases demasiado largas y ambigüedades. Se señalan sin reescribir párrafos.
- **Informática:** diagramas y código referenciados, decisiones de diseño justificadas, pruebas descritas con resultados y terminología correcta.

## 6. Scripts

Todos son de librería estándar; python-docx solo hace falta para DOCX. Cada uno acepta `--json salida.json` para pegar su resultado en `comprobaciones`.

| Script | Para qué |
|---|---|
| `scripts/extraer.py trabajo [salida.md]` | Texto con secciones, tablas y leyendas identificadas |
| `scripts/revisar_estructura.py trabajo --tipo T` | Secciones presentes y que faltan, orden, figuras y tablas (numeración, leyenda, citadas), objetivos sin evaluar, pruebas sin resultados |
| `scripts/revisar_referencias.py trabajo` | Citas (autor-año, [n], superíndices, `\cite`) frente a la bibliografía: sin entrada, sin citar, años distintos, mezcla de estilos |
| `scripts/revisar_numeros.py trabajo` | Cifras distintas entre tablas y texto, unidades mal escritas o fuera del SI, decimales irregulares, separador mezclado |
| `scripts/calculos_lab.py calculos.json` | Molaridad, diluciones simples y seriadas, Henderson-Hasselbalch, recta de calibrado (pendiente, ordenada, R², interpolación), Lambert-Beer, rendimiento y porcentajes |
| `scripts/validar_correccion.py correccion.json --trabajo T` | Esquema, citas literales, cálculos respaldados, ejemplos cortos, nota ponderada y tono |
| `scripts/informe_html.py correccion.json salida.html` | Informe HTML |
| `scripts/comentar_docx.py original.docx correccion.json salida.docx` | Copia del DOCX con comentarios de Word anclados al fragmento exacto; el texto del alumno no cambia |
| `scripts/comparar_versiones.py anterior.json trabajo-v2` | Qué comentarios siguen igual y cuáles hay que revisar en la versión nueva |

`calculos.json` lo escribe el asistente con los datos tal como los da el trabajo (formato en `references/esquema.md`).

## 7. Cada comentario

Esquema en `references/esquema.md`. Lleva:
- la cita literal del fragmento;
- la ubicación (sección, página o párrafo);
- la gravedad: crítico, importante o menor;
- qué falla, por qué importa y cómo arreglarlo, con un ejemplo opcional de 1-2 frases;
- el criterio de la rúbrica afectado.

## 8. Priorización

- Primero lo crítico: errores de cálculo, conclusiones no soportadas, apartados que faltan y citas sin fuente.
- Como mucho ~25 comentarios. Los menores del mismo tipo se agrupan en uno con el número de casos y un ejemplo («hay 12 cifras pegadas a su unidad, por ejemplo 595nm»).
- 2-4 puntos fuertes concretos, que digan qué conviene mantener y dónde. Nada genérico.
- Los 3 cambios con más impacto en la nota, enlazados a sus comentarios.

## 9. Salida

- **`correccion-<nombre>.html`** (`informe_html.py`). Incluye:
  - la valoración orientativa por criterio y global sobre 10, con la advertencia de que es orientativa;
  - los 3 cambios con más impacto y los puntos fuertes;
  - todos los comentarios por gravedad;
  - los resultados de los scripts, con los cálculos y su fórmula.
- **Si era DOCX:** `<nombre>-corregido.docx`, con los comentarios de Word (`comentar_docx.py`). Nunca se sobrescribe el original.
- **El JSON** se guarda junto al informe: sirve para comparar versiones.
- **En el chat**, solo la valoración global, los 3 cambios con más impacto y las rutas. Una línea final ofrece revisar de nuevo tras los cambios (comparando versiones) o profundizar en una sección.

## 10. Versiones

Si el usuario trae una versión nueva:
1. Ejecutar `comparar_versiones.py` con la corrección anterior y repetir los scripts.
2. Leer cada comentario «cambiado» antes de darlo por arreglado.
3. En `version_anterior`, separar lo que está arreglado, lo que sigue y lo que es nuevo.
4. En el chat, primero lo arreglado, después lo que sigue y lo nuevo, y la nota antes y después.

## 11. Tono y antirrepetición

Detalle y lista de fórmulas prohibidas en `references/tono.md`.
- Directo y respetuoso. Sin halagos vacíos («¡Buen trabajo!») ni rodeos de cortesía.
- Cada comentario es concreto y distinto de los demás. No se repite la misma fórmula («Considera…», «Sería conveniente…») en todos. Como mucho 2 comentarios empiezan igual.
- Fuera las muletillas de IA («es importante destacar», «cabe mencionar», «juega un papel crucial»…).

Autorrevisión antes de entregar:
1. ¿Cada comentario apunta a un sitio exacto y dice cómo arreglarlo?
2. ¿Algún ejemplo reescribe más de lo necesario?
3. ¿La nota de cada criterio se explica con los comentarios?
4. ¿Leídos seguidos, suenan a plantilla?

## 12. Fidelidad

- Nunca se afirma un error de cálculo sin recalcularlo con `calculos_lab.py`. `validar_correccion.py` lo trata como error.
- Si un dato no se puede comprobar, se dice: «no puedo comprobar X porque falta Y».
- Si una afirmación científica parece dudosa, se marca «verificar con la bibliografía» (`"verificar": true`). No se corrige como si fuera seguro.
- La nota es orientativa y lo dice siempre. La pone el profesor.

## 13. Integridad académica

Si el usuario pide «reescríbemelo», «házmelo» o «redáctame la discusión», el asistente explica en una línea que esta skill corrige y no redacta. Después ofrece comentarios más detallados de esa sección o ejemplos de 1-2 frases por punto. No redacta secciones completas.

## Ejemplos

En `examples/`, dos trabajos inventados con errores plantados: un informe de laboratorio de bioquímica (Bradford) y una memoria de prácticas de informática (API REST). Cada uno trae su corrección en HTML, el DOCX comentado y el JSON. La tabla de errores plantados y detectados está en el README de la skill.
