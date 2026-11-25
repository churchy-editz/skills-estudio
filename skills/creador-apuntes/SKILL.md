---
name: creador-apuntes
description: >-
  Convierte material de estudio (PDF, DOCX, texto pegado, transcripciones de clase
  o fotos de apuntes) en apuntes para aprender el tema, con una estructura propia
  para cada contenido, tono cercano y sin aspecto de texto generado. Entrega un HTML
  imprimible y un DOCX con cajas de color para definiciones, ejemplos, errores
  frecuentes y datos clave. Usar cuando el usuario diga cosas como "hazme apuntes
  de este PDF", "resume este tema para estudiar", "haz un esquema de este documento",
  "explícame este tema para estudiarlo", "make study notes from this" o "summarize
  this chapter for exam", o pida apuntes, resúmenes o esquemas para estudiar,
  repasar o preparar exámenes y oposiciones.
license: MIT
compatibility: Python 3.11 o posterior y python-docx para generar el DOCX. Sin ejecución de código, entrega solo el HTML.
---

# Creador de apuntes

Convierte un material de estudio en apuntes que sirvan para aprender el tema, no solo para repasarlo. La forma de cada sección la decide su contenido; no hay plantilla fija de apartados.

## 1. Entrada

Acepta PDF, DOCX, texto pegado, transcripciones de clase y fotos de apuntes.
- Leer el material entero antes de escribir nada y contar sus palabras (1 página ≈ 500 palabras).
- Fotos o PDF escaneados: transcribir primero. Lo ilegible se marca como `[ilegible]`, sin rellenarlo.
- Transcripciones de clase: quitar muletillas y repeticiones, pero conservar los ejemplos del profesor y los avisos del tipo "esto cae" (van a una caja Dato clave).

## 2. Nivel

Deducir el nivel por la fuente, el vocabulario y lo que diga el usuario, y ajustar el lenguaje:

| Nivel | Señales | Ajuste |
|---|---|---|
| ESO / Bachillerato | libro de texto, temario de curso | definir cada término técnico la primera vez; ejemplos cotidianos |
| Universidad | manuales, artículos, apuntes de cátedra | terminología de la disciplina sin rebajarla; definir solo lo nuevo |
| Oposiciones / normativa | leyes, temario oficial, BOE | literalidad: los artículos clave se copian tal cual, entre comillas, citados por número ("art. 14 CE"); no parafrasear plazos, cifras ni requisitos |
| Profesional | manuales técnicos, procedimientos | orientado a aplicar: pasos, criterios de decisión, excepciones |

Con dudas entre dos niveles: vocabulario del más alto, explicaciones del más bajo.

## 3. Extensión

Si el usuario no ha dicho qué extensión quiere, hacer UNA sola pregunta antes de generar, con las cifras calculadas sobre el original (N = páginas del original × porcentaje, redondeado; si sale menos de una página, darlo en palabras):

> El material tiene ~X páginas. ¿Qué extensión quieres para los apuntes?
> a) Repaso rápido (~10 %, ~N págs.)
> b) Estándar (~25 %, ~N págs.) — recomendado
> c) Detallado (~50 %, ~N págs.)
> d) Otra: dime páginas o palabras

- Si ya indicó la extensión, no preguntar.
- Si no responde o dice "da igual", usar la estándar.
- Oposiciones o normativa: añadir a la pregunta que por debajo del 25 % pueden quedar fuera artículos evaluables.
- Objetivo = palabras del original × porcentaje, con margen de ±15 %. No cuentan la leyenda, las etiquetas de las cajas ni el índice.

## 4. Salida

Generar siempre dos archivos con el mismo contenido (`<tema>` en minúsculas, con guiones y sin tildes):

1. `apuntes-<tema>.html`: partir de `assets/plantilla-base.html`. Autocontenido: CSS inline, sin fuentes, scripts ni imágenes externas. Ya trae `@media print` para imprimir a PDF.
2. `apuntes-<tema>.docx`: generarlo desde el HTML con
   `python scripts/html_a_docx.py apuntes-<tema>.html apuntes-<tema>.docx`
   Requiere python-docx; si falta, el script dice el comando `pip` exacto. Los títulos salen con los estilos de Word Título 1, 2 y 3, y cada caja como una tabla de una celda con fondo de color y su etiqueta.

Usar solo las clases de la plantilla y de `references/estructuras.md`. El conversor convierte cualquier otra cosa en texto normal: no se pierde contenido, pero sí la forma.

- Si no se puede ejecutar código: entregar solo el HTML y decir que puede abrirse con Word y usar "Guardar como" > .docx.
- Si no se pueden crear archivos: entregar Markdown con la misma estructura; cada caja como cita que empieza por su etiqueta en negrita (`> **Ojo.** …`).

## 5. Paleta y cajas

- Elegir la paleta de la asignatura en `references/paletas.md` (la neutra si ninguna encaja) y copiar sus valores en el `:root` de la plantilla. Todas cumplen contraste WCAG AA.
- Cuatro cajas con significado fijo: **Definición** (`.def`), **Ejemplo** (`.ejemplo`), **Ojo**, para errores frecuentes o datos que hay que verificar (`.ojo`), y **Dato clave** (`.clave`).
- Arriba, una leyenda pequeña con los tipos de caja que aparezcan en el documento.
- Cada caja lleva siempre su etiqueta de texto (`<span class="etiqueta">`) además del color, para que se entienda impresa en blanco y negro.
- Máximo 3-4 cajas por página (~500 palabras). Lo que no sea definición, ejemplo, error o dato clave va en texto normal.

## 6. Estructura según el contenido

Decidir la forma sección a sección según el tipo de contenido. El HTML, el CSS y cómo queda cada una en Word están en `references/estructuras.md`; al final de ese archivo hay patrones probados para combinar estructuras y cajas. Los ajustes según el formato de la fuente (por ejemplo, diapositivas) están en `references/patrones.md`.

| Si el contenido es… | Estructura |
|---|---|
| un proceso o procedimiento | pasos numerados (`ol.pasos`) |
| una cronología | línea de tiempo (`ol.linea-tiempo`) |
| conceptos parecidos que se confunden | tabla comparativa (`table.comparativa`) |
| una clasificación | árbol (`ul.arbol`) |
| causas y consecuencias encadenadas | cadena de flechas (`ol.cadena`) |
| teoría densa para memorizar | Cornell (`div.cornell`) |

Un tema puede mezclar varias. Si dos temas distintos acaban con el mismo esqueleto, se está aplicando una plantilla: rehacer la estructura.

## 7. Tono

Escribir como un buen compañero que explica bien. Lista de prohibiciones y ejemplos en `references/tono.md`.
- Frases cortas, una idea por frase.
- Cada bloque empieza con la idea en una frase sencilla; después, el detalle.
- "Por qué importa" (`p.porque`) en una o dos líneas, solo cuando aporte: para qué sirve, qué explica o por qué cae en el examen.
- Analogías cotidianas solo para conceptos abstractos, marcadas como tales (`p.analogia`, que empieza por "Analogía:").
- Conectar ideas entre secciones ("es el factor que falta en la hemofilia, más abajo").
- Prohibido: emojis, "Es importante destacar", "En resumen", "Cabe mencionar", "En conclusión" y el resto de la lista de `tono.md`. Sin introducciones ni cierres genéricos: se empieza por el contenido y se termina con la última idea útil.

## 8. Fidelidad a la fuente

- No inventar nada que no esté en la fuente: ni datos, ni fechas, ni ejemplos presentados como del temario.
- Las analogías y los ejemplos que añada el asistente se marcan como tales.
- Si la fuente tiene una errata, una contradicción o un dato dudoso: caja Ojo con la palabra "verificar" y qué hay que comprobar.

## 9. Documentos largos

Más de 30 páginas: trabajar por secciones (capítulos o bloques de 10-15 páginas) aplicando a cada una la extensión elegida. Unirlas en un solo HTML con un índice navegable al principio (`nav.indice`, con enlaces a los `id` de cada sección) y generar un único DOCX.

## 10. Autorrevisión antes de entregar

Comprobar y corregir lo que falle:
1. ¿Falta algún concepto evaluable? Recorrer los títulos, las negritas y las definiciones de la fuente.
2. ¿Hay algo inventado? Cada dato tiene que poder señalarse en la fuente.
3. ¿Se respeta la extensión? Contar las palabras (sin leyenda ni etiquetas) y compararlas con el objetivo ±15 %.
4. ¿Suena a IA? Buscar las muletillas y los patrones de `references/tono.md`.
5. ¿La estructura sigue al contenido o es genérica?
6. ¿Hay como mucho 3-4 cajas por página y todas llevan etiqueta?

## 11. Entrega

Dar las rutas de los dos archivos. Sin extras por defecto. Terminar con una sola línea que ofrezca más, por ejemplo:
"Si te sirve, puedo añadir un glosario, preguntas de autoevaluación, una regla mnemotécnica o un diagrama, o convertir esto en un test con creador-tests."

## Ejemplos

`examples/` contiene dos fuentes sintéticas (`fuente-*.md`) y sus apuntes en extensión estándar (`apuntes-*.html` y `.docx`):
- Hemostasia (biología, un proceso): paleta de ciencias, pasos numerados y cadena causa-efecto.
- La Transición (historia, una cronología): paleta de historia, fuente serif y línea de tiempo.
