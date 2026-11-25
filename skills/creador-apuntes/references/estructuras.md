# Estructuras según el contenido

Cada sección se maqueta según el tipo de contenido que tiene, no según una plantilla. Las clases y su CSS completo están en `assets/plantilla-base.html`; aquí va el HTML mínimo, el CSS esencial y cómo queda en Word.

`scripts/html_a_docx.py` solo reconoce estas clases. Cualquier otra se convierte en texto normal (no se pierde contenido, pero sí la forma).

| Contenido | Estructura | Clase |
|---|---|---|
| Proceso, procedimiento, algoritmo | Pasos numerados | `ol.pasos` |
| Hechos con fecha, evolución | Línea de tiempo | `ol.linea-tiempo` |
| Conceptos parecidos que se confunden | Tabla comparativa | `table.comparativa` |
| Clasificación, tipos, jerarquía | Árbol | `ul.arbol` |
| Causas y consecuencias, mecanismo | Cadena de flechas | `ol.cadena` |
| Teoría densa para memorizar | Cornell | `div.cornell` |

## Pasos numerados

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

## Línea de tiempo

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

## Tabla comparativa

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

## Árbol (clasificación)

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

## Cadena causa → efecto

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

## Cornell

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

## Índice navegable (documentos de más de 30 páginas)

```html
<nav class="indice">
  <h2>Índice</h2>
  <ol><li><a href="#tema-1">Tema 1. …</a></li></ol>
</nav>
<section id="tema-1"><h2>Tema 1. …</h2> …</section>
```

En Word: lista numerada con los títulos (sin enlaces). Los títulos usan estilos de título, así que Word puede generar un índice automático con Referencias > Tabla de contenido.

## Patrones de uso probados

Decisiones que funcionaron en apuntes reales. Combinan las estructuras de arriba con las cajas.

### Ejemplo con valores de la fuente → tabla dentro de la caja Ejemplo

Cuándo: la fuente trae un caso concreto con datos (un diagrama con valores, una traza, un antes y un después).
- Pasar el caso a una tabla pequeña dentro de `.caja.ejemplo`: una fila por caso y una columna por cada valor que se compara (por ejemplo, "antes" y "después"). Las celdas sin valor se marcan con "(vacío)", no se dejan en blanco.
- Debajo de la tabla, una frase sobre qué se hace con cada columna. Sin ella, la tabla es un dibujo y no se entiende para qué sirve.
- Si esas columnas se usan después en otras secciones, cerrar con un `p.porque` que diga qué sección usa cada columna.

### Pares de conceptos que se confunden → tabla con filas de criterio

Cuándo: la fuente presenta dos variantes de lo mismo (dos clases, dos técnicas, dos niveles).
- Filas de criterio ordenadas de la situación a la acción, elegidas según la asignatura. Ejemplos: técnico → qué es / cuándo se usa / cómo funciona / qué pasa si falla; historia → cuándo / quién / causas / consecuencias; lengua → definición / rasgos / ejemplo / con qué se confunde.
- Celdas de una frase corta. Si una celda necesita un párrafo, ese criterio va en texto debajo de la tabla.
- No repetir en la tabla una fila que ya se desarrolla en su propia sección más abajo. Se queda en la sección.
- Un mismo tema puede tener varias tablas así, una por par.

### Clasificación de dos o tres elementos → árbol corto como mapa

Cuándo: la fuente enumera las piezas que se explican en las secciones siguientes ("instrumentos", "tipos", "fases").
- Un `ul.arbol` de un solo nivel, con la categoría en negrita y sus elementos debajo. Hace de mapa: el lector sabe qué viene.
- Las definiciones no van en el árbol, sino en cada sección.

### Procedimiento con alternativas dentro de un paso → paso único con "de dos maneras"

Cuándo: un paso de un proceso se puede hacer de varias formas.
- Mantener `ol.pasos` con los pasos reales. Las alternativas van dentro del mismo paso, en una frase ("de dos maneras: A o B"), sin sublistas. Si fueran subpasos, parecería que hay que hacer las dos.

### Lista de campos o atributos → lista simple, sin caja

Cuándo: la fuente enumera lo que contiene algo (campos de un registro, partes de un documento, requisitos).
- Lista normal con un elemento por línea. Las abreviaturas que se van a usar después se definen aquí, entre paréntesis.
- No va en caja: no es una definición ni un dato suelto, y una caja con seis viñetas pesa demasiado.
