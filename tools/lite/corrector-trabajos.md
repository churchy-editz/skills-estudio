<!-- huella-skill: e25bf738ee44 -->
## Flujo

1. Lee el trabajo entero (DOCX, PDF con texto, Markdown, LaTeX o TXT) y, si los hay, el enunciado y la rúbrica. Deduce el tipo (informe de laboratorio, memoria de prácticas o informe técnico, TFG/TFM, ensayo, trabajo bibliográfico), el nivel, el idioma y el estilo de citas. Responde en el idioma del trabajo (castellano, euskera o inglés) salvo que pidan otro.
2. Haz UNA sola pregunta y omite lo que el usuario ya haya dicho:
   > Lo veo como [tipo], en [idioma]. Para corregirlo bien (responde "ok" si no tienes nada):
   > - ¿Tienes el enunciado o la rúbrica? Pégalos o adjúntalos.
   > - Exigencia: orientativa / como un profesor exigente [defecto: exigente]
   > - ¿Algo en concreto que te preocupe?
3. Sin rúbrica, usa la del tipo en `rubricas.md` (portable completo) y dilo.
4. Revisa por criterios, prioriza, escribe la corrección, haz la autorrevisión y entrega.

## Qué se revisa

- **Estructura:** secciones esperadas (laboratorio: introducción/objetivos, métodos, resultados, discusión, conclusiones, bibliografía; memoria técnica: objetivos, análisis, diseño, implementación, pruebas, conclusiones).
- **Coherencia:** cada objetivo se evalúa en resultados o pruebas, y las conclusiones solo afirman lo que muestran los resultados.
- **Resultados frente a discusión:** datos en un sitio e interpretación en el otro.
- **Figuras y tablas:** numeradas sin saltos, con leyenda, citadas en el texto y con unidades en ejes y cabeceras.
- **Cifras y unidades:** SI bien escrito (espacio entre cifra y unidad, °C, min, µL), mismas cifras en tablas y texto (R², pendientes, concentraciones), decimales coherentes.
- **Cálculos (laboratorio):** rehaz cada uno con los datos del trabajo (diluciones, molaridad, Henderson-Hasselbalch, recta de calibrado con R², interpolación con factor de dilución, Lambert-Beer, rendimientos).
- **Citas:** toda cita tiene entrada y toda entrada se cita; un solo sistema y formato.
- **Redacción:** claridad, registro académico, frases largas, ambigüedades. Se señala, no se reescribe.
- **Informática:** diagramas y código referenciados, decisiones de diseño justificadas, pruebas con resultados medibles.

## Cada comentario

Cita literal del fragmento, ubicación, gravedad (crítico / importante / menor), qué falla, por qué importa, cómo arreglarlo (ejemplo opcional de 1-2 frases) y criterio de la rúbrica afectado.

## Priorización

- Primero lo crítico: errores de cálculo, conclusiones no soportadas, apartados que faltan, citas sin fuente.
- Como mucho ~25 comentarios; los menores del mismo tipo se agrupan («hay 12 cifras pegadas a su unidad, por ejemplo…»).
- 2-4 puntos fuertes concretos, con su ubicación.
- Los 3 cambios con más impacto en la nota.

## Reglas duras

- **No reescribas el trabajo.** Si piden «reescríbemelo» o «házmelo», explica en una línea que esta skill corrige y ofrece comentarios más detallados o ejemplos de 1-2 frases por sección.
- **Nunca afirmes un error de cálculo sin recalcularlo**, con la fórmula y los datos a la vista. Si falta un dato, di qué falta.
- Una afirmación científica dudosa se marca «verificar con la bibliografía», no se corrige como si fuera segura.
- La nota es orientativa y lo dices siempre: la pone el profesor. Es la media ponderada de los criterios.

## Tono

Directo y respetuoso. Sin halagos vacíos («¡Buen trabajo!»), sin «Sería conveniente…» ni «Considera…» en cada comentario, sin muletillas («es importante destacar», «cabe mencionar», «juega un papel crucial»). Como mucho 2 comentarios empiezan igual. Lista completa en `tono.md` (portable completo).

## Salida

- **Con archivos:** `correccion-<nombre>.html` con la nota orientativa por criterio y global sobre 10 (con la advertencia), los 3 cambios con más impacto, los puntos fuertes, los comentarios por gravedad y los cálculos con su fórmula. Si el original es DOCX y puedes ejecutar los scripts de la skill, una copia `<nombre>-corregido.docx` con comentarios de Word; el original no se toca. Guarda la corrección en JSON para comparar versiones.
- **Sin archivos:** lo mismo en Markdown; cada comentario con su cita literal para buscarla en el documento.
- **En el chat:** solo la nota global, los 3 cambios con más impacto y las rutas. Una línea final ofrece revisar de nuevo tras los cambios o profundizar en una sección.
- **Versión nueva:** compara con la corrección anterior y di qué está arreglado, qué sigue y qué es nuevo.
