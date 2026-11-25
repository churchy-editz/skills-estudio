# creador-apuntes (versión portable)

<!-- Generado por tools/generar_portables.py a partir de SKILL.md, references/ y assets/. No lo edites a mano: regenéralo. -->

Estas son las instrucciones completas de la skill, en un solo texto para usarlas en un chat sin soporte de skills (un GPT, un Gem o un proyecto). Donde se habla de scripts (`scripts/…`): si puedes ejecutar código pero no tienes los scripts, o no puedes ejecutar código, aplica a mano las comprobaciones de la sección «Si no puedes ejecutar código», al final de las instrucciones. Los archivos de referencia van como anexos al final.

**Cuándo usarla:** Convierte material de estudio (PDF, DOCX, texto pegado, transcripciones de clase o fotos de apuntes) en apuntes para aprender el tema, con una estructura propia para cada contenido, tono cercano y sin aspecto de texto generado. Entrega un HTML imprimible y un DOCX con cajas de color para definiciones, ejemplos, errores frecuentes y datos clave. Usar cuando el usuario diga cosas como "hazme apuntes de este PDF", "resume este tema para estudiar", "haz un esquema de este documento", "explícame este tema para estudiarlo", "make study notes from this" o "summarize this chapter for exam", o pida apuntes, resúmenes o esquemas para estudiar, repasar o preparar exámenes y oposiciones.

**Requisitos:** Python 3.11 o posterior y python-docx para generar el DOCX. Sin ejecución de código, entrega solo el HTML.

## Creador de apuntes

Convierte un material de estudio en apuntes que sirvan para aprender el tema, no solo para repasarlo. La forma de cada sección la decide su contenido; no hay plantilla fija de apartados.

### 1. Entrada

Acepta PDF, DOCX, texto pegado, transcripciones de clase y fotos de apuntes.
- Leer el material entero antes de escribir nada y contar sus palabras (1 página ≈ 500 palabras).
- Fotos o PDF escaneados: transcribir primero. Lo ilegible se marca como `[ilegible]`, sin rellenarlo.
- Transcripciones de clase: quitar muletillas y repeticiones, pero conservar los ejemplos del profesor y los avisos del tipo "esto cae" (van a una caja Dato clave).

### 2. Nivel

Deducir el nivel por la fuente, el vocabulario y lo que diga el usuario, y ajustar el lenguaje:

| Nivel | Señales | Ajuste |
|---|---|---|
| ESO / Bachillerato | libro de texto, temario de curso | definir cada término técnico la primera vez; ejemplos cotidianos |
| Universidad | manuales, artículos, apuntes de cátedra | terminología de la disciplina sin rebajarla; definir solo lo nuevo |
| Oposiciones / normativa | leyes, temario oficial, BOE | literalidad: los artículos clave se copian tal cual, entre comillas, citados por número ("art. 14 CE"); no parafrasear plazos, cifras ni requisitos |
| Profesional | manuales técnicos, procedimientos | orientado a aplicar: pasos, criterios de decisión, excepciones |

Con dudas entre dos niveles: vocabulario del más alto, explicaciones del más bajo.

### 3. Extensión

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

### 4. Salida

Generar siempre dos archivos con el mismo contenido (`<tema>` en minúsculas, con guiones y sin tildes):

1. `apuntes-<tema>.html`: partir de el anexo `plantilla-base.html`. Autocontenido: CSS inline, sin fuentes, scripts ni imágenes externas. Ya trae `@media print` para imprimir a PDF.
2. `apuntes-<tema>.docx`: generarlo desde el HTML con
   `python scripts/html_a_docx.py apuntes-<tema>.html apuntes-<tema>.docx`
   Requiere python-docx; si falta, el script dice el comando `pip` exacto. Los títulos salen con los estilos de Word Título 1, 2 y 3, y cada caja como una tabla de una celda con fondo de color y su etiqueta.

Usar solo las clases de la plantilla y de el anexo `estructuras.md`. El conversor convierte cualquier otra cosa en texto normal: no se pierde contenido, pero sí la forma.

- Si no se puede ejecutar código: entregar solo el HTML y decir que puede abrirse con Word y usar "Guardar como" > .docx.
- Si no se pueden crear archivos: entregar Markdown con la misma estructura; cada caja como cita que empieza por su etiqueta en negrita (`> **Ojo.** …`).

### 5. Paleta y cajas

- Elegir la paleta de la asignatura en el anexo `paletas.md` (la neutra si ninguna encaja) y copiar sus valores en el `:root` de la plantilla. Todas cumplen contraste WCAG AA.
- Cuatro cajas con significado fijo: **Definición** (`.def`), **Ejemplo** (`.ejemplo`), **Ojo**, para errores frecuentes o datos que hay que verificar (`.ojo`), y **Dato clave** (`.clave`).
- Arriba, una leyenda pequeña con los tipos de caja que aparezcan en el documento.
- Cada caja lleva siempre su etiqueta de texto (`<span class="etiqueta">`) además del color, para que se entienda impresa en blanco y negro.
- Máximo 3-4 cajas por página (~500 palabras). Lo que no sea definición, ejemplo, error o dato clave va en texto normal.

### 6. Estructura según el contenido

Decidir la forma sección a sección según el tipo de contenido. El HTML, el CSS y cómo queda cada una en Word están en el anexo `estructuras.md`; al final de ese archivo hay patrones probados para combinar estructuras y cajas. Los ajustes según el formato de la fuente (por ejemplo, diapositivas) están en el anexo `patrones.md`.

| Si el contenido es… | Estructura |
|---|---|
| un proceso o procedimiento | pasos numerados (`ol.pasos`) |
| una cronología | línea de tiempo (`ol.linea-tiempo`) |
| conceptos parecidos que se confunden | tabla comparativa (`table.comparativa`) |
| una clasificación | árbol (`ul.arbol`) |
| causas y consecuencias encadenadas | cadena de flechas (`ol.cadena`) |
| teoría densa para memorizar | Cornell (`div.cornell`) |

Un tema puede mezclar varias. Si dos temas distintos acaban con el mismo esqueleto, se está aplicando una plantilla: rehacer la estructura.

### 7. Tono

Escribir como un buen compañero que explica bien. Lista de prohibiciones y ejemplos en el anexo `tono.md`.
- Frases cortas, una idea por frase.
- Cada bloque empieza con la idea en una frase sencilla; después, el detalle.
- "Por qué importa" (`p.porque`) en una o dos líneas, solo cuando aporte: para qué sirve, qué explica o por qué cae en el examen.
- Analogías cotidianas solo para conceptos abstractos, marcadas como tales (`p.analogia`, que empieza por "Analogía:").
- Conectar ideas entre secciones ("es el factor que falta en la hemofilia, más abajo").
- Prohibido: emojis, "Es importante destacar", "En resumen", "Cabe mencionar", "En conclusión" y el resto de la lista de `tono.md`. Sin introducciones ni cierres genéricos: se empieza por el contenido y se termina con la última idea útil.

### 8. Fidelidad a la fuente

- No inventar nada que no esté en la fuente: ni datos, ni fechas, ni ejemplos presentados como del temario.
- Las analogías y los ejemplos que añada el asistente se marcan como tales.
- Si la fuente tiene una errata, una contradicción o un dato dudoso: caja Ojo con la palabra "verificar" y qué hay que comprobar.

### 9. Documentos largos

Más de 30 páginas: trabajar por secciones (capítulos o bloques de 10-15 páginas) aplicando a cada una la extensión elegida. Unirlas en un solo HTML con un índice navegable al principio (`nav.indice`, con enlaces a los `id` de cada sección) y generar un único DOCX.

### 10. Autorrevisión antes de entregar

Comprobar y corregir lo que falle:
1. ¿Falta algún concepto evaluable? Recorrer los títulos, las negritas y las definiciones de la fuente.
2. ¿Hay algo inventado? Cada dato tiene que poder señalarse en la fuente.
3. ¿Se respeta la extensión? Contar las palabras (sin leyenda ni etiquetas) y compararlas con el objetivo ±15 %.
4. ¿Suena a IA? Buscar las muletillas y los patrones de el anexo `tono.md`.
5. ¿La estructura sigue al contenido o es genérica?
6. ¿Hay como mucho 3-4 cajas por página y todas llevan etiqueta?

### 11. Entrega

Dar las rutas de los dos archivos. Sin extras por defecto. Terminar con una sola línea que ofrezca más, por ejemplo:
"Si te sirve, puedo añadir un glosario, preguntas de autoevaluación, una regla mnemotécnica o un diagrama, o convertir esto en un test con creador-tests."

## Si no puedes ejecutar código

Esta skill no tiene validador automático; su único script (`scripts/html_a_docx.py`) convierte el HTML en Word.

- **Sin ejecutar código:** entrega solo el HTML, partiendo de la plantilla del anexo `assets/plantilla-base.html`, y di que se abre con Word y se guarda como .docx con "Guardar como".
- **Sin poder crear archivos:** entrega Markdown con la misma estructura. Cada caja va como cita que empieza por su etiqueta en negrita (`> **Ojo.** …`).
- **Extensión:** cuenta a mano las palabras de los apuntes, sin la leyenda ni las etiquetas, y compáralas con el objetivo (±15 %).
- **Cajas:** como mucho 3-4 por cada ~500 palabras, y todas con su etiqueta de texto.
- **Tono:** repasa la lista de prohibiciones del anexo `tono.md` frase a frase.

---

## Anexo: `estructuras.md`

### Estructuras según el contenido

Cada sección se maqueta según el tipo de contenido que tiene, no según una plantilla. Las clases y su CSS completo están en el anexo `plantilla-base.html`; aquí va el HTML mínimo, el CSS esencial y cómo queda en Word.

`scripts/html_a_docx.py` solo reconoce estas clases. Cualquier otra se convierte en texto normal (no se pierde contenido, pero sí la forma).

| Contenido | Estructura | Clase |
|---|---|---|
| Proceso, procedimiento, algoritmo | Pasos numerados | `ol.pasos` |
| Hechos con fecha, evolución | Línea de tiempo | `ol.linea-tiempo` |
| Conceptos parecidos que se confunden | Tabla comparativa | `table.comparativa` |
| Clasificación, tipos, jerarquía | Árbol | `ul.arbol` |
| Causas y consecuencias, mecanismo | Cadena de flechas | `ol.cadena` |
| Teoría densa para memorizar | Cornell | `div.cornell` |

#### Pasos numerados

Cuándo: hay un orden y saltarse un paso cambia el resultado (fases de un proceso biológico, procedimiento administrativo, resolución de un problema tipo).

```html
<ol class="pasos">
  <li><span class="paso-titulo">Vasoconstricción.</span> El vaso se contrae.</li>
  <li><span class="paso-titulo">Tapón plaquetario.</span> Las plaquetas se pegan al colágeno.</li>
</ol>
```

```css
ol.pasos { list-style: none; counter-reset: paso; padding: 0; }
ol.pasos > li { counter-increment: paso; position: relative; padding: 0 0 .9rem 2.6rem; }
ol.pasos > li::before { content: counter(paso); position: absolute; left: 0;
  width: 1.8rem; height: 1.8rem; border-radius: 50%; background: var(--def); color: var(--fondo); }
```

En Word: lista numerada (estilo "Lista con números"), que empieza en 1 en cada bloque. El título del paso va en negrita y el detalle en la línea siguiente.

#### Línea de tiempo

Cuándo: lo que importa es el orden en el tiempo y las fechas son evaluables. Máximo una idea por hito; si un hito necesita un párrafo, va después en una sección propia.

```html
<ol class="linea-tiempo">
  <li><span class="fecha">20 nov 1975</span> Muere Franco.</li>
  <li><span class="fecha">15 jun 1977</span> Primeras elecciones libres desde 1936.</li>
</ol>
```

```css
ol.linea-tiempo { list-style: none; padding-left: 1.2rem; border-left: 3px solid var(--def); }
ol.linea-tiempo > li::before { /* punto sobre la línea */ }
.fecha { display: block; font-weight: 700; color: var(--def); }
```

En Word: tabla de dos columnas (Fecha | Hecho) con la fila de cabecera sombreada. La línea vertical y los puntos se pierden; el orden y las fechas no.

#### Tabla comparativa

Cuándo: dos o más conceptos que el alumno suele mezclar (mitosis y meiosis, dolo y culpa, ser y estar). Las filas son los criterios de comparación; las columnas, los conceptos. Si solo hay un criterio, sobra la tabla: basta una frase.

```html
<table class="comparativa">
  <thead><tr><th></th><th>Primaria</th><th>Secundaria</th></tr></thead>
  <tbody>
    <tr><th>Qué forma</th><td>Tapón de plaquetas</td><td>Red de fibrina</td></tr>
  </tbody>
</table>
```

```css
table { width: 100%; border-collapse: collapse; }
th, td { padding: .45rem .6rem; border: 1px solid color-mix(in srgb, var(--texto) 20%, var(--fondo)); }
thead th { background: color-mix(in srgb, var(--def) 10%, var(--fondo)); }
```

En Word: tabla con bordes y la cabecera sombreada y en negrita. Se mantiene igual.

#### Árbol (clasificación)

Cuándo: hay categorías y subcategorías (tipos de tejidos, clases de contratos, géneros literarios). Más de tres niveles se lee mal: partir en dos árboles.

```html
<ul class="arbol">
  <li><strong>Tejidos</strong>
    <ul>
      <li>Epitelial</li>
      <li>Conectivo
        <ul><li>Óseo</li><li>Sanguíneo</li></ul>
      </li>
    </ul>
  </li>
</ul>
```

```css
ul.arbol, ul.arbol ul { list-style: none; padding: 0; }
ul.arbol ul { margin-left: .5rem; padding-left: 1rem; border-left: 2px solid color-mix(in srgb, var(--def) 30%, var(--fondo)); }
ul.arbol ul > li::before { content: "— "; color: var(--def); }
```

En Word: lista con viñetas anidada (niveles 1, 2 y 3). Se pierden las líneas verticales; la jerarquía se ve por la sangría.

#### Cadena causa → efecto

Cuándo: cada elemento provoca el siguiente (cascada de la coagulación, causas de una guerra, efecto de una subida de tipos de interés). Si las causas no están encadenadas sino en paralelo, usar una lista normal.

```html
<ol class="cadena">
  <li>Factor X activado</li>
  <li>Protrombina → trombina</li>
  <li>Fibrinógeno → fibrina</li>
</ol>
```

```css
ol.cadena { list-style: none; padding: 0; }
ol.cadena > li { position: relative; padding: .45rem .8rem; border: 1px solid var(--def); text-align: center; }
ol.cadena > li:not(:last-child) { margin-bottom: 1.5rem; }
ol.cadena > li:not(:last-child)::after { content: "↓"; position: absolute; left: 50%; bottom: -1.45rem; }
```

En Word: lista numerada. Las flechas se pierden; el número marca el orden de la cadena. Dentro de un elemento se puede escribir "→" como texto y sí se conserva.

#### Cornell

Cuándo: teoría densa sin un orden claro (un tema de filosofía, un bloque de derecho) que hay que memorizar y luego poder recitar. La columna izquierda son preguntas que el propio alumno se haría; la derecha, la respuesta breve. Abajo, una síntesis de dos o tres frases.

```html
<div class="cornell">
  <div class="fila">
    <div class="pregunta">¿Qué es el imperativo categórico?</div>
    <div class="notas">Un mandato moral que vale sin condiciones.</div>
  </div>
  <div class="sintesis"><strong>Síntesis:</strong> …</div>
</div>
```

```css
.cornell .fila { display: grid; grid-template-columns: 30% 1fr; }
.cornell .pregunta { font-weight: 600; background: color-mix(in srgb, var(--clave) 10%, var(--fondo)); }
```

En Word: tabla de dos columnas, preguntas a la izquierda con fondo de color, y una última fila a todo el ancho con la síntesis.

#### Índice navegable (documentos de más de 30 páginas)

```html
<nav class="indice">
  <h2>Índice</h2>
  <ol><li><a href="#tema-1">Tema 1. …</a></li></ol>
</nav>
<section id="tema-1"><h2>Tema 1. …</h2> …</section>
```

En Word: lista numerada con los títulos (sin enlaces). Los títulos usan estilos de título, así que Word puede generar un índice automático con Referencias > Tabla de contenido.

#### Patrones de uso probados

Decisiones que funcionaron en apuntes reales. Combinan las estructuras de arriba con las cajas.

##### Ejemplo con valores de la fuente → tabla dentro de la caja Ejemplo

Cuándo: la fuente trae un caso concreto con datos (un diagrama con valores, una traza, un antes y un después).
- Pasar el caso a una tabla pequeña dentro de `.caja.ejemplo`: una fila por caso y una columna por cada valor que se compara (por ejemplo, "antes" y "después"). Las celdas sin valor se marcan con "(vacío)", no se dejan en blanco.
- Debajo de la tabla, una frase sobre qué se hace con cada columna. Sin ella, la tabla es un dibujo y no se entiende para qué sirve.
- Si esas columnas se usan después en otras secciones, cerrar con un `p.porque` que diga qué sección usa cada columna.

##### Pares de conceptos que se confunden → tabla con filas de criterio

Cuándo: la fuente presenta dos variantes de lo mismo (dos clases, dos técnicas, dos niveles).
- Filas de criterio ordenadas de la situación a la acción, elegidas según la asignatura. Ejemplos: técnico → qué es / cuándo se usa / cómo funciona / qué pasa si falla; historia → cuándo / quién / causas / consecuencias; lengua → definición / rasgos / ejemplo / con qué se confunde.
- Celdas de una frase corta. Si una celda necesita un párrafo, ese criterio va en texto debajo de la tabla.
- No repetir en la tabla una fila que ya se desarrolla en su propia sección más abajo. Se queda en la sección.
- Un mismo tema puede tener varias tablas así, una por par.

##### Clasificación de dos o tres elementos → árbol corto como mapa

Cuándo: la fuente enumera las piezas que se explican en las secciones siguientes ("instrumentos", "tipos", "fases").
- Un `ul.arbol` de un solo nivel, con la categoría en negrita y sus elementos debajo. Hace de mapa: el lector sabe qué viene.
- Las definiciones no van en el árbol, sino en cada sección.

##### Procedimiento con alternativas dentro de un paso → paso único con "de dos maneras"

Cuándo: un paso de un proceso se puede hacer de varias formas.
- Mantener `ol.pasos` con los pasos reales. Las alternativas van dentro del mismo paso, en una frase ("de dos maneras: A o B"), sin sublistas. Si fueran subpasos, parecería que hay que hacer las dos.

##### Lista de campos o atributos → lista simple, sin caja

Cuándo: la fuente enumera lo que contiene algo (campos de un registro, partes de un documento, requisitos).
- Lista normal con un elemento por línea. Las abreviaturas que se van a usar después se definen aquí, entre paréntesis.
- No va en caja: no es una definición ni un dato suelto, y una caja con seis viñetas pesa demasiado.

---

## Anexo: `paletas.md`

### Paletas por asignatura

Cada paleta tiene 6 valores: 4 colores semánticos, fondo y texto. Se copian tal cual en el `:root` de el anexo `plantilla-base.html`.

#### Significado fijo de los colores

| Variable    | Caja        | Etiqueta impresa | Para qué                                        |
|-------------|-------------|------------------|-------------------------------------------------|
| `--def`     | `.def`      | DEFINICIÓN       | Qué es algo. También colorea los títulos.       |
| `--ejemplo` | `.ejemplo`  | EJEMPLO          | Un caso concreto de la fuente.                  |
| `--ojo`     | `.ojo`      | OJO              | Error frecuente, confusión típica o "verificar". |
| `--clave`   | `.clave`    | DATO CLAVE       | Lo que hay que saberse sí o sí.                 |

El fondo de cada caja no es un color aparte: es el 10 % del color semántico mezclado con `--fondo` (`color-mix` en CSS; el conversor a DOCX hace la misma cuenta).

#### Paletas

| Paleta | `--fondo` | `--texto` | `--def` | `--ejemplo` | `--ojo` | `--clave` | Fuente sugerida |
|---|---|---|---|---|---|---|---|
| **Neutra (por defecto)** | `#ffffff` | `#1f1f1f` | `#1f5f8b` | `#2e6b30` | `#a3261b` | `#7a4b00` | sans |
| **Ciencias** (biología, química, física) | `#fbfdfb` | `#18261f` | `#0b6e69` | `#3d6b1f` | `#b02a1f` | `#6b3fa0` | sans |
| **Matemáticas** (y estadística) | `#fdfdfd` | `#1a1c24` | `#1d4e89` | `#2f6b4f` | `#b3261e` | `#8a4b00` | sans |
| **Historia** (y geografía) | `#fcf9f2` | `#2b2118` | `#7a3e12` | `#4f6228` | `#9e1c1c` | `#23527c` | serif |
| **Lengua y literatura** | `#fffdf9` | `#241b26` | `#6a2c70` | `#1f6f6b` | `#a8321e` | `#8a5a00` | serif |
| **Idiomas** | `#fafcff` | `#1a2230` | `#1560a0` | `#1b7340` | `#b4261a` | `#7b3f98` | sans |
| **Derecho / oposiciones** | `#ffffff` | `#1b1b1b` | `#1c3d6e` | `#3f5f3a` | `#8f1d1d` | `#6b4e16` | serif |
| **Economía** (y empresa) | `#fbfcfd` | `#1c2329` | `#0f5c6e` | `#2f6b2f` | `#b03a12` | `#5b3d99` | sans |
| **Arte y humanidades** (filosofía, música) | `#fdfbf8` | `#2a2226` | `#8a2f4c` | `#2d6a5e` | `#a32d1a` | `#5a4a8a` | serif |

Fuentes (sin descargas, solo fuentes del sistema):
- sans: `--fuente: system-ui, "Segoe UI", Roboto, Arial, sans-serif;`
- serif: `--fuente: Georgia, Cambria, "Times New Roman", serif;`

Si la asignatura no encaja en ninguna, usar la neutra. Si el tema mezcla dos (historia del derecho, por ejemplo), elegir la del examen para el que se estudia.

#### Contraste verificado (WCAG 2.1 AA, mínimo 4,5:1)

Se comprobaron tres combinaciones por cada color semántico: color sobre `--fondo` (títulos y leyenda), color sobre el fondo de su caja (etiqueta) y `--texto` sobre el fondo de la caja (cuerpo). La tabla da el peor de esos valores por color.

| Paleta | texto/fondo | def | ejemplo | ojo | clave | Peor caso |
|---|---|---|---|---|---|---|
| Neutra | 16,48 | 5,90 | 5,56 | 6,22 | 6,36 | 5,56 |
| Ciencias | 15,38 | 5,17 | 5,36 | 5,48 | 6,21 | 5,17 |
| Matemáticas | 16,71 | 7,06 | 5,36 | 5,48 | 5,76 | 5,36 |
| Historia | 14,98 | 6,74 | 5,58 | 6,39 | 6,64 | 5,58 |
| Lengua y literatura | 16,41 | 7,91 | 5,08 | 5,63 | 5,08 | 5,08 |
| Idiomas | 15,53 | 5,48 | 4,97 | 5,38 | 5,85 | 4,97 |
| Derecho / oposiciones | 17,22 | 9,11 | 6,23 | 7,43 | 6,60 | 6,23 |
| Economía | 15,47 | 6,31 | 5,45 | 5,10 | 6,80 | 5,10 |
| Arte y humanidades | 15,00 | 6,70 | 5,28 | 5,86 | 6,28 | 5,28 |

Los números de `ol.pasos` usan `--fondo` sobre `--def`: es el mismo par que "def sobre fondo", así que también pasa.

Si se cambia un color, volver a medir las tres combinaciones antes de usarlo.

---

## Anexo: `patrones.md`

### Patrones según el tipo de fuente

Ajustes que dependen de cómo viene el material, no del contenido.

#### Fuente en diapositivas

- **Contar las palabras, no las páginas.** Una presentación de 15-20 diapositivas puede tener unas 1.500 palabras (unas 3 páginas de texto). La extensión se calcula con las palabras.
- **Avisar en la pregunta de extensión.** Las diapositivas ya están resumidas: con el 25 % salen apuntes muy escuetos. Decirlo en la opción estándar para que el usuario pueda elegir la detallada.
- **Diagramas con texto suelto.** Al extraer el texto de un diagrama, las etiquetas salen desordenadas (columnas, flechas, leyendas mezcladas). Reconstruir qué relaciona el diagrama y llevarlo a una tabla (ver "Ejemplo con valores de la fuente" en `estructuras.md`). Lo que no se pueda reconstruir con seguridad va en una caja Ojo.
- **Numeración saltada.** Si las diapositivas saltan números, es que faltan páginas en el PDF o hay diapositivas ocultas. No se menciona en los apuntes salvo que falte contenido que la propia fuente da por visto.
- **Preguntas de repaso de la fuente.** Si la presentación termina con preguntas de repaso, sirven como lista de comprobación en la autorrevisión: cada pregunta tiene que poder responderse con los apuntes. No se copian en los apuntes, salvo que el usuario lo pida.
- **Referencias a un libro.** Si la fuente remite a un libro o una página ("libro de apuntes, pág. N"), esa es la referencia que se da en las cajas Ojo de "verificar".

---

## Anexo: `tono.md`

### Tono: un compañero que explica bien

La referencia es el compañero de clase que te explica el tema la víspera del examen. Va al grano, usa frases cortas, te dice qué suele caer y en qué se equivoca todo el mundo. No adorna ni hace introducciones, y tampoco se despide con una moraleja.

#### Muletillas prohibidas

Si aparece alguna, se reescribe la frase entera; no basta con cambiar el conector por un sinónimo.

##### Español

- "Es importante destacar / señalar / mencionar que…"
- "Cabe mencionar / destacar / señalar que…"
- "En resumen…", "En conclusión…", "En definitiva…", "Para concluir…"
- "En este tema exploraremos / veremos / abordaremos…"
- "A lo largo de este documento…"
- "Juega un papel fundamental / crucial / clave"
- "Desempeña un papel…"
- "Es fundamental / crucial / esencial comprender…"
- "No solo… sino también…" (como fórmula repetida)
- "Sumérgete en…", "Adentrémonos en…", "Vamos a desglosar…"
- "Un fascinante / apasionante mundo de…"
- "Sin lugar a dudas…", "Cabe destacar que…"
- "Esto nos lleva a…", "Dicho esto…"
- "En el vasto / amplio panorama de…"
- "Ni más ni menos que…"
- "¿Alguna vez te has preguntado…?" como arranque
- "Espero que estos apuntes te sean de ayuda" y cualquier despedida

##### Inglés

- "It's important to note / worth noting that…"
- "In summary", "In conclusion", "To sum up", "Overall"
- "Let's dive into…", "Let's delve into…", "Let's break it down"
- "In this section we will explore…"
- "Plays a crucial / pivotal / vital role"
- "A testament to…", "Navigating the landscape of…"
- "Not only… but also…" (como fórmula repetida)
- "Unlock", "harness", "leverage", "seamless", "robust" fuera de contexto técnico
- "In today's fast-paced world…"
- "Whether you're a student or…"
- "I hope this helps", "Happy studying!"

##### Patrones (en cualquier idioma)

- Emojis, en cualquier sitio.
- Tríadas de adjetivos por inercia: "claro, conciso y eficaz".
- Abrir cada sección con una frase que anuncia lo que viene en vez de decirlo.
- Cerrar cada sección con una frase redonda que repite lo dicho.
- Negrita en media frase de cada párrafo. La negrita es para términos que hay que memorizar, uno o dos por bloque.
- Guiones largos (—) para meter incisos en cada frase.
- Todas las secciones con el mismo esqueleto: definición, lista de 3 puntos, ejemplo, resumen.
- Preguntas retóricas que el texto responde justo después.
- Párrafos de longitud idéntica y frases de ritmo idéntico.

#### Pares de ejemplo (mismo contenido)

##### 1. Abrir un tema (biología)

**Robótica:**
> En este tema exploraremos el fascinante proceso de la hemostasia, un mecanismo fundamental que desempeña un papel crucial en la supervivencia del organismo. Es importante destacar que se trata de un proceso complejo, preciso y altamente regulado.

**Humana:**
> La hemostasia es lo que hace que un corte deje de sangrar. Tiene dos trabajos: tapar el vaso roto y, cuando ya está curado, quitar el tapón.

Qué cambia: empieza por la idea, no por el anuncio. Fuera "fascinante", "fundamental", "crucial" y la tríada final, que no dicen nada que se pueda estudiar.

##### 2. Explicar una causa (historia)

**Robótica:**
> Cabe mencionar que la legalización del Partido Comunista de España no solo supuso un hito en el proceso de democratización, sino que también generó tensiones significativas con determinados sectores del Ejército. En definitiva, se trató de una decisión clave.

**Humana:**
> El Gobierno legalizó el PCE en abril de 1977, en pleno Sábado Santo. Sin él no había elecciones creíbles. Al Ejército le sentó muy mal.

Qué cambia: frases cortas, la fecha concreta, la consecuencia dicha con sus palabras. Sin "hito", sin "no solo… sino también", sin cierre.

##### 3. Un error frecuente (matemáticas)

**Robótica:**
> Es esencial comprender que la derivada de un producto no es igual al producto de las derivadas. Este es un error común que muchos estudiantes cometen, por lo que resulta fundamental prestar especial atención a este aspecto.

**Humana:**
> Ojo: (f·g)' no es f'·g'. Es f'·g + f·g'. Si te sale más corto de lo que esperabas, probablemente lo has hecho mal.

Qué cambia: va en una caja Ojo, da la fórmula correcta y un truco para detectar el fallo. Las tres frases de advertencia sobraban: la caja ya avisa.

#### Comprobación rápida

Antes de entregar, leer en voz alta (mentalmente) el primer párrafo de cada sección. Si podría pegarse en apuntes de otro tema cambiando solo el nombre, es relleno: reescribirlo con algo que solo sea verdad para este tema.

#### Decisiones de redacción probadas

- **Títulos de sección propios.** No copiar el título de la diapositiva o del epígrafe. El título dice de qué va la sección ("Por qué se estropea…", "Clases de… e instrumentos"). Las diapositivas que llevan el mismo título con (1), (2), (3) se funden en una sola sección.
- **Viñetas telegráficas → frases.** Las viñetas de una diapositiva se reescriben como frases completas y cortas. Las listas de la fuente se mantienen como listas, con el término en negrita, dos puntos y una frase.
- **Introducción de lista mínima.** Antes de una lista basta "Causas de…:" o "Factores a considerar:". Frases como "Para medirlo se tienen en cuenta tres factores" no aportan nada.
- **Abreviaturas.** Se definen una vez, entre paréntesis, en el sitio donde aparecen por primera vez, y desde ahí se usan sin repetir la forma larga.
- **Conexiones con número de apartado.** Cuando una sección usa algo de otra, se cita como "(apartado N)". Es más corto que "como veremos más adelante" y se puede comprobar.
- **El Dato clave es lo que comparten las variantes.** Después de una tabla comparativa, la caja Dato clave no repite una fila. Dice qué tienen en común las dos columnas y por qué importa.
- **Ojo de "verificar" con cuatro partes.** Una cita literal de la fuente entre comillas, qué parte de ella es segura, qué hay que comprobar y dónde (libro, página, apartado). Sin la ubicación, el aviso no se puede resolver.
- **Recortar sin perder contenido.** Si los apuntes se pasan de extensión, recortar en este orden: frases de transición e introducciones de lista, después `p.porque` que repiten algo ya dicho, después filas de tabla que se desarrollan en otra sección. Las definiciones, las listas de la fuente y las cajas Ojo se recortan las últimas.

---

## Anexo: `plantilla-base.html`

```html
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Apuntes: TEMA</title>
<style>
/* Paleta: copiar aquí los 6 valores de references/paletas.md (y la fuente). */
:root {
  --fondo: #ffffff;
  --texto: #1f1f1f;
  --def: #1f5f8b;
  --ejemplo: #2e6b30;
  --ojo: #a3261b;
  --clave: #7a4b00;
  --fuente: system-ui, "Segoe UI", Roboto, Arial, sans-serif;
}

* { box-sizing: border-box; }
body { margin: 0; background: var(--fondo); color: var(--texto); font: 16px/1.55 var(--fuente); }
main { max-width: 46rem; margin: 0 auto; padding: 2rem 1rem 3rem; }
h1 { font-size: 1.9rem; line-height: 1.2; margin: 0 0 .3rem; color: var(--def); }
h2 { font-size: 1.35rem; margin: 2rem 0 .6rem; padding-bottom: .2rem; color: var(--def);
     border-bottom: 2px solid color-mix(in srgb, var(--def) 30%, var(--fondo)); }
h3 { font-size: 1.1rem; margin: 1.4rem 0 .4rem; }
p { margin: .5rem 0; }
.subtitulo { margin: 0 0 1rem; font-size: .95rem; }

/* Color de cada tipo: lo usan cajas, leyenda y etiquetas */
.def { --c: var(--def); }
.ejemplo { --c: var(--ejemplo); }
.ojo { --c: var(--ojo); }
.clave { --c: var(--clave); }

/* Leyenda: solo con los tipos de caja que aparezcan */
.leyenda { display: flex; flex-wrap: wrap; gap: .4rem .8rem; margin: .4rem 0 1.6rem; font-size: .8rem; }
.leyenda span { padding: .05rem .5rem; border-left: 4px solid var(--c); color: var(--c); font-weight: 600;
                background: color-mix(in srgb, var(--c) 10%, var(--fondo)); }

/* Cajas semánticas: siempre con <span class="etiqueta"> */
.caja { margin: 1rem 0; padding: .7rem 1rem; border-left: 5px solid var(--c); border-radius: 0 6px 6px 0;
        background: color-mix(in srgb, var(--c) 10%, var(--fondo)); }
.caja > :last-child { margin-bottom: 0; }
.etiqueta { display: block; margin-bottom: .2rem; font-size: .75rem; font-weight: 700;
            letter-spacing: .06em; text-transform: uppercase; color: var(--c); }

.porque { margin: .6rem 0; padding-left: .8rem; border-left: 2px dotted var(--clave); font-size: .95rem; }
.analogia { font-style: italic; }

/* Pasos numerados */
ol.pasos { list-style: none; counter-reset: paso; margin: 1rem 0; padding: 0; }
ol.pasos > li { counter-increment: paso; position: relative; padding: 0 0 .9rem 2.6rem; }
ol.pasos > li::before { content: counter(paso); position: absolute; left: 0; top: 0; width: 1.8rem; height: 1.8rem;
                        border-radius: 50%; background: var(--def); color: var(--fondo); font-weight: 700;
                        text-align: center; line-height: 1.8rem; }
ol.pasos > li:not(:last-child)::after { content: ""; position: absolute; left: .85rem; top: 2rem; bottom: .2rem;
                                        border-left: 2px solid color-mix(in srgb, var(--def) 30%, var(--fondo)); }
.paso-titulo { display: block; font-weight: 700; }

/* Línea de tiempo */
ol.linea-tiempo { list-style: none; margin: 1rem 0; padding: 0 0 0 1.2rem;
                  border-left: 3px solid color-mix(in srgb, var(--def) 45%, var(--fondo)); }
ol.linea-tiempo > li { position: relative; margin: 0 0 1rem; padding-left: .9rem; }
ol.linea-tiempo > li::before { content: ""; position: absolute; left: -1.75rem; top: .35rem; width: .8rem; height: .8rem;
                               border-radius: 50%; background: var(--fondo); border: 3px solid var(--def); }
.fecha { display: block; font-size: .85rem; font-weight: 700; letter-spacing: .03em; color: var(--def); }

/* Tabla comparativa */
table { width: 100%; margin: 1rem 0; border-collapse: collapse; font-size: .95rem; }
th, td { padding: .45rem .6rem; border: 1px solid color-mix(in srgb, var(--texto) 20%, var(--fondo)); text-align: left; vertical-align: top; }
thead th { background: color-mix(in srgb, var(--def) 10%, var(--fondo)); }
tbody th { font-weight: 600; }

/* Árbol / clasificación */
ul.arbol, ul.arbol ul { list-style: none; margin: 0; padding: 0; }
ul.arbol { margin: 1rem 0; }
ul.arbol ul { margin-left: .5rem; padding-left: 1rem; border-left: 2px solid color-mix(in srgb, var(--def) 30%, var(--fondo)); }
ul.arbol li { margin: .2rem 0; }
ul.arbol ul > li::before { content: "— "; color: var(--def); }
ul.arbol > li > strong:first-child { color: var(--def); }

/* Cadena causa → efecto */
ol.cadena { list-style: none; margin: 1rem 0; padding: 0; }
ol.cadena > li { position: relative; padding: .45rem .8rem; border-radius: 6px; text-align: center;
                 border: 1px solid color-mix(in srgb, var(--def) 40%, var(--fondo)); }
ol.cadena > li:not(:last-child) { margin-bottom: 1.5rem; }
ol.cadena > li:not(:last-child)::after { content: "↓"; position: absolute; left: 50%; bottom: -1.45rem;
                                         transform: translateX(-50%); color: var(--def); font-weight: 700; }

/* Método Cornell */
.cornell { margin: 1rem 0; border: 1px solid color-mix(in srgb, var(--texto) 20%, var(--fondo)); }
.cornell .fila { display: grid; grid-template-columns: 30% 1fr; border-bottom: 1px solid color-mix(in srgb, var(--texto) 20%, var(--fondo)); }
.cornell .pregunta { padding: .5rem .7rem; font-weight: 600; background: color-mix(in srgb, var(--clave) 10%, var(--fondo)); }
.cornell .notas { padding: .5rem .7rem; }
.cornell .sintesis { padding: .6rem .7rem; }

/* Índice para documentos largos */
nav.indice { margin: 1rem 0 2rem; font-size: .95rem; }
nav.indice a { color: var(--def); }

@media (max-width: 34rem) {
  .cornell .fila { grid-template-columns: 1fr; }
}

@media print {
  @page { size: A4; margin: 1.8cm 1.6cm; }
  * { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  body { font-size: 11pt; }
  main { max-width: none; padding: 0; }
  h2, h3 { break-after: avoid; }
  .caja, table, ol.pasos > li, ol.linea-tiempo > li, ol.cadena > li, .cornell .fila { break-inside: avoid; }
  a { color: inherit; text-decoration: none; }
}
</style>
</head>
<body>
<main>
<header>
  <h1>TÍTULO DEL TEMA</h1>
  <p class="subtitulo">Asignatura · extensión elegida</p>
  <div class="leyenda">
    <span class="def">Definición</span>
    <span class="ejemplo">Ejemplo</span>
    <span class="ojo">Ojo</span>
    <span class="clave">Dato clave</span>
  </div>
</header>

<!-- Contenido. Cajas disponibles:
<div class="caja def"><span class="etiqueta">Definición</span><p>…</p></div>
<div class="caja ejemplo"><span class="etiqueta">Ejemplo</span><p>…</p></div>
<div class="caja ojo"><span class="etiqueta">Ojo</span><p>…</p></div>
<div class="caja clave"><span class="etiqueta">Dato clave</span><p>…</p></div>
Estructuras: ver references/estructuras.md -->

</main>
</body>
</html>
```
