# Qué se revisa y cómo

Para cada aspecto: qué se busca, qué script ayuda y cuándo es crítico, importante o menor. Los scripts señalan candidatos; el asistente los confirma leyendo el trabajo antes de comentar nada.

## Gravedad

- **Crítico:** invalida un resultado o una conclusión, o falta algo que la rúbrica exige. Errores de cálculo que cambian un resultado, conclusiones que los datos no sostienen, secciones obligatorias que faltan, citas sin fuente, datos que se contradicen en algo central.
- **Importante:** resta claramente nota, pero no invalida el trabajo. Figuras sin citar o sin unidades, decisiones sin justificar, pruebas sin resultados, discusión que repite resultados, objetivos sin evaluar.
- **Menor:** forma. Unidades mal escritas, decimales irregulares, formato de cita inconsistente, frases largas. Los del mismo tipo van juntos en un comentario.

## 1. Estructura

- Secciones esperadas según el tipo (tabla en `scripts/revisar_estructura.py`, con sinónimos en castellano, inglés y euskera).
  - Laboratorio: introducción, objetivos, materiales y métodos, resultados, discusión, conclusiones y bibliografía.
  - Memoria técnica: objetivos, análisis, diseño, implementación, pruebas y conclusiones.
  - TFG: resumen, introducción, objetivos, metodología o diseño, resultados, conclusiones y bibliografía.
- Que una sección se llame distinto no es un error. Lo que cuenta es que su contenido esté.
- Si el enunciado pide secciones propias, mandan las del enunciado.

## 2. Coherencia objetivos ↔ resultados ↔ conclusiones

- Cada objetivo tiene que poder seguirse hasta un resultado y una conclusión. `revisar_estructura.py` avisa de los objetivos cuyas palabras o cifras no reaparecen después; el asistente confirma leyendo.
- Las conclusiones solo afirman lo que los resultados muestran. Señales de alarma:
  - comparaciones con algo que no se midió («más preciso que Lowry» sin medir Lowry);
  - generalizaciones desde una sola muestra o un solo ensayo;
  - «demuestra» donde los datos solo son compatibles;
  - causas que no se han puesto a prueba.
- Una conclusión no sostenida es **crítica**.

## 3. Resultados frente a discusión

- Resultados: datos, cálculos, figuras y tablas, descritos sin interpretar.
- Discusión: qué significan, comparación con valores de referencia o bibliografía, fuentes de error y su efecto.
- Fallos típicos: interpretar en resultados («lo que confirma que…»), repetir los números en la discusión sin decir qué significan, discutir errores genéricos («errores de pipeteo») sin relacionarlos con un dato concreto.

## 4. Figuras y tablas

- Numeradas sin saltos, con leyenda que dice qué muestran, citadas en el texto antes de aparecer o junto a ellas (`revisar_estructura.py`).
- Ejes con magnitud y unidad; cabeceras de tabla con unidad (`revisar_numeros.py` revisa las cabeceras; los ejes de una imagen, el asistente si puede verla).
- La leyenda de una tabla va encima; la de una figura, debajo (convención habitual; menor).
- Una figura que repite exactamente una tabla sobra (menor).

## 5. Cifras y unidades

- Unidades del SI y bien escritas: «mL», «µL», «°C», «min», «s», «h», «g». Espacio entre cifra y unidad («595 nm»). Lista de formas incorrectas en `scripts/revisar_numeros.py`.
- Cifras significativas coherentes: misma magnitud, mismos decimales; un resultado no puede tener más precisión que sus datos.
- Mismas cifras en tablas, figuras y texto. `revisar_numeros.py` avisa de magnitudes únicas con valores distintos (R², pendiente…) y de cifras casi iguales (un dígito cambiado o traspuesto).
- Separador decimal: coma en castellano y euskera, punto en inglés, siempre el mismo.

## 6. Cálculos (laboratorio)

- Todo cálculo que el trabajo da (molaridad, diluciones, pH de tampones, recta de calibrado, interpolación, Lambert-Beer, rendimientos, porcentajes) se rehace con `scripts/calculos_lab.py` con los datos del propio trabajo.
- **Nunca se afirma un error de cálculo sin el recálculo.** Si faltan datos para rehacerlo, se dice: «no puedo comprobar la molaridad porque no se da la masa pesada».
- Si el resultado no coincide, se busca el error típico que lo explica (ver `references/errores-frecuentes.md`); el script detecta algunos (cociente invertido, factor de dilución olvidado, r en vez de R²).
- Un error de cálculo que se arrastra a los resultados es crítico; uno aislado en un dato auxiliar, importante.

## 7. Citas y bibliografía

- Cada cita del texto tiene su entrada, y cada entrada se cita (`scripts/revisar_referencias.py`).
- Un solo sistema de cita (autor-año o numérico) y un solo formato (APA, Vancouver, IEEE…) en todo el trabajo. Si la guía de la asignatura fija uno, ese.
- Año y autor iguales en la cita y en la entrada.
- Afirmaciones que necesitan fuente y no la tienen (cifras de referencia, mecanismos, «se sabe que…»): importante.
- No se comprueba si la fuente dice lo que el trabajo le atribuye; si algo parece dudoso, «verificar con la bibliografía».

## 8. Redacción

- Claridad: una idea por frase; frases de más de ~40 palabras se señalan si dificultan entender.
- Registro académico: impersonal en informes de laboratorio («se midió»), primera persona del plural aceptable en memorias técnicas si es consistente.
- Ambigüedades: pronombres sin referente claro, «esto», «lo anterior»; términos usados con dos sentidos.
- Terminología precisa: «concentración» no es «cantidad», «exactitud» no es «precisión».
- Se señala con la cita y se explica el problema. **No se reescriben párrafos.** Como mucho, un ejemplo de 1-2 frases para mostrar la forma.

## 9. Informática (memorias técnicas y TFG)

- Diagramas (clases, secuencia, arquitectura, E-R) y fragmentos de código referenciados en el texto y explicados.
- Cada decisión de diseño importante (lenguaje, framework, base de datos, arquitectura) con su porqué frente a alguna alternativa. Una decisión sin justificar es importante.
- Pruebas: qué tipo (unitarias, integración, rendimiento, usabilidad), cómo se hicieron y **qué salió** (casos superados y fallidos, cobertura, tiempos). Sin resultados no hay evaluación: importante, y crítico si un objetivo depende de ellas.
- Requisitos trazables: cada objetivo y requisito con su prueba.
- Terminología: API, endpoint, transacción, concurrencia, test unitario o de integración usados con su sentido.

## 10. Afirmaciones científicas dudosas

Si una afirmación del trabajo parece incorrecta, pero el asistente no puede comprobarla con el material disponible, se marca con `"verificar": true` y se redacta como duda: «Esto contradice lo que suele darse para…; verifícalo con la bibliografía». Nunca se corrige como si fuera seguro.
