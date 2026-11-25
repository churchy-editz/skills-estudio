# corrector-trabajos

Corrige trabajos universitarios igual que un profesor con tiempo. Señala cada error con la cita exacta, explica por qué lo es y cómo arreglarlo, y da una nota orientativa por criterios. Sirve para informes de laboratorio, memorias de prácticas, informes técnicos, TFG y TFM, ensayos y trabajos bibliográficos, en castellano, euskera o inglés. El trabajo no se reescribe: como mucho, un comentario lleva un ejemplo de una o dos frases.

Los scripts rehacen los cálculos de laboratorio, contrastan las citas con la bibliografía y comprueban la estructura, las figuras, las tablas, las cifras y las unidades. Lo demás (coherencia, discusión, decisiones de diseño, redacción) sale de la lectura del asistente con una rúbrica.

## Ejemplo de uso

> «Revisa mi informe de laboratorio, que lo entrego el viernes.»

El agente detecta el tipo de trabajo y su idioma. Después pregunta una sola vez por la rúbrica, la exigencia y lo que más te preocupa, pasa los scripts y escribe la corrección. Entrega tres cosas:
- `correccion-<nombre>.html`: nota orientativa, los 3 cambios que más la suben, puntos fuertes, comentarios por gravedad y los cálculos con su fórmula;
- si el trabajo era un DOCX, una copia con los comentarios de Word anclados a cada frase;
- el JSON de la corrección, que sirve para comparar con la siguiente versión.

## Archivos

| Archivo | Para qué |
|---|---|
| `SKILL.md` | Instrucciones de la skill |
| `references/rubricas.md` | Rúbrica por defecto de cada tipo de trabajo, con criterios y pesos |
| `references/criterios.md` | Qué se revisa en cada aspecto y cuándo es crítico, importante o menor |
| `references/esquema.md` | Formato del JSON de la corrección y de la entrada de `calculos_lab.py` |
| `references/tono.md` | Cómo se escribe un comentario y fórmulas prohibidas (las lee el validador) |
| `references/errores-frecuentes.md` | Errores típicos de informes de laboratorio, memorias técnicas y ensayos |
| `scripts/extraer.py` | DOCX, PDF, Markdown, LaTeX o TXT a texto con secciones, tablas y leyendas |
| `scripts/revisar_estructura.py` | Secciones, figuras y tablas, objetivos sin evaluar, pruebas sin resultados |
| `scripts/revisar_referencias.py` | Citas del texto frente a la bibliografía (APA, Vancouver, IEEE, `\cite`) |
| `scripts/revisar_numeros.py` | Cifras distintas entre tablas y texto, unidades, decimales |
| `scripts/calculos_lab.py` | Molaridad, diluciones, Henderson-Hasselbalch, recta de calibrado, Lambert-Beer, rendimientos |
| `scripts/validar_correccion.py` | Comprueba el JSON: citas literales, cálculos respaldados, nota ponderada y tono |
| `scripts/informe_html.py` | Informe HTML de la corrección |
| `scripts/comentar_docx.py` | Copia del DOCX con comentarios de Word (necesita python-docx) |
| `scripts/comparar_versiones.py` | Qué comentarios siguen y cuáles hay que revisar en una versión nueva |
| `prompt-portable.md` | Todo lo anterior en un solo texto, para subir como archivo de conocimiento en chats sin skills |
| `prompt-portable-lite.md` | Lo esencial en menos de 7.500 caracteres, para el campo de instrucciones de un GPT o un Gem |
| `examples/` | Dos trabajos inventados con errores plantados, con su corrección en HTML, DOCX comentado y JSON |
| `tests/` | Tests de los scripts |

## Ejemplos: errores plantados y detectados

En `examples/` hay dos trabajos sintéticos escritos para la skill. Los textos y los datos son inventados; las pocas referencias bibliográficas son obras reales citadas solo con su ficha. Se plantaron errores a propósito y se ejecutó la skill sobre los dos. La columna «Quién lo detecta» separa lo que encuentran los scripts por sí solos de lo que depende de la lectura del asistente.

Los errores plantados y la corrección los escribió la misma sesión, así que la lectura no es una prueba a ciegas. Lo que sí es independiente es la parte de los scripts: `tests/test_corrector_trabajos.py` (clase `TestEjemplos`) comprueba que siguen detectando sus errores y que no dan falsos positivos en el resto.

### Informe de laboratorio: Bradford (`informe-bradford.docx`, ~1.150 palabras)

| Error plantado | Quién lo detecta | Comentario |
|---|---|---|
| Dilución mal calculada: 0,25 mL de madre de 2 mg/mL para 10 mL a 0,5 mg/mL (son 2,5 mL) | `calculos_lab.py` (c1, no coincide) | k01, crítico |
| R² mal copiado: 0,9943 en el texto y 0,9934 en la figura | `revisar_numeros.py` (valores distintos) y `calculos_lab.py` (c3.r2: el bueno es 0,9934) | k04, importante |
| Figura 2 sin citar en el texto | `revisar_estructura.py` | k06, importante |
| Cita sin entrada en la bibliografía: (Compton y Jones, 1985) | `revisar_referencias.py` | k03, crítico |
| Conclusión que no se sigue de los datos: «más preciso que el de Lowry» | Lectura (coherencia) | k02, crítico |
| Unidades mal escritas: «595nm», «20 ul», «5 mins» | `revisar_numeros.py` (los 3 casos) | k10, menor |

**Detectados: 6 de 6.** Además, la corrección señala cuatro cosas que no se plantaron:
- interpretación dentro de Resultados;
- tablas sin desviación estándar;
- una explicación de la discusión sin fuente, marcada «verificar con la bibliografía»;
- una conclusión que omite la salvedad de la discusión.

Nota orientativa: 6,7.

### Memoria de prácticas: API REST de reservas (`memoria-reservas.docx`, ~930 palabras)

| Error plantado | Quién lo detecta | Comentario |
|---|---|---|
| Objetivo que no se evalúa: O3, tiempo de respuesta con 50 usuarios | `revisar_estructura.py` (la cifra no vuelve a aparecer) | m01, crítico |
| Pruebas descritas sin resultados | `revisar_estructura.py` | m02, crítico |
| Diagrama de clases (Figura 1) no referenciado | `revisar_estructura.py` | m04, importante |
| Decisión de diseño sin justificar: MongoDB | Lectura (diseño) | m03, importante |

**Detectados: 4 de 4.** Además señala tres cosas que no se plantaron:
- la transacción depende de cómo esté desplegado MongoDB (marcada para verificar);
- un JSON presentado como figura;
- una referencia web sin fecha de consulta.

Nota orientativa: 6,4.

Los dos informes, los DOCX comentados y los JSON están en `examples/` (`correccion-*.html`, `*-corregido.docx`, `correccion-*.json`). La entrada de los cálculos del informe de Bradford es `calculos-bradford.json`.

## Límites

- Los scripts señalan candidatos; el asistente confirma cada uno leyendo el trabajo. La coherencia de las conclusiones, la calidad de la discusión y las decisiones de diseño dependen de esa lectura.
- Los PDF escaneados no tienen texto: hay que transcribirlos antes. De un PDF se extrae el texto, pero las tablas no se reconocen como tales.
- No comprueba que una fuente diga lo que el trabajo le atribuye. Lo dudoso se marca para verificar.
- La nota es orientativa: la pone el profesor con su rúbrica.

Instalación y requisitos: [README del repositorio](../../README.md#instalación).
