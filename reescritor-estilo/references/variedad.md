# Variedad: ritmo, arranques y párrafos

Un texto suena a plantilla cuando todo tiene la misma forma: frases de longitud parecida, párrafos iguales, el mismo conector abriendo cada idea. Este archivo da técnicas para romper esa forma y los límites que mide `scripts/analizar.py`.

## Límites que mide el script

| Qué | Límite | Categoría |
|---|---|---|
| Muletillas de `patrones-ia.md` | 0 | `muletillas` |
| Frases hechas y tópicos de ensayo de `patrones-ia.md` | 0 | `topicos` |
| Último párrafo que repite conceptos de los anteriores | menos de 3 (o todos del párrafo anterior) | `cierre` |
| Última frase que apela a expertos, al futuro o a la opción equilibrada | 0 | `cierre` |
| Tríada en el último párrafo | 0 | `triadas` |
| Coeficiente de variación (CV) de la longitud de frase | ≥ 0,35 (con 5 frases o más) | `ritmo` |
| Frases o párrafos que empiezan por la misma palabra | máx. 2 (si la primera es un artículo, cuentan las dos primeras) | `arranques` |
| Un mismo conector de la lista | máx. 2 por cada 300 palabras | `conectores` |
| Enumeraciones de exactamente 3 elementos | máx. 1 por cada 200 palabras | `triadas` |
| CV de la longitud de párrafo | ≥ 0,25 (con 3 párrafos o más) | `parrafos` |
| Párrafos que acaban en frase-resumen | máx. la mitad | `parrafos` |
| Guiones largos / exclamaciones | máx. 1 por cada 100 palabras | `puntuacion` |

La nota de naturalidad es la proporción de categorías sin avisos. Muletillas, tópicos y cierre pesan el doble que el resto, porque son lo que más delata un texto en piloto automático.

El CV es la desviación típica dividida por la media. Un CV de 0,2 significa que casi todas las frases miden lo mismo. A partir de 0,4 ya hay contraste de verdad. El informe también da la proporción de frases cortas (menos de 8 palabras) y largas (más de 25). Un texto natural suele tener de las dos.

## Ritmo de frase

- **Frase corta después de una larga.** Una explicación de 30 palabras gana fuerza si la siguiente tiene cuatro: "No funcionó."
- **Una frase larga que encadena de verdad.** Si dos ideas van juntas (causa y efecto, condición y resultado), se pueden unir en una frase de 35 palabras bien puntuada en lugar de partirlas en dos frases medianas.
- **La frase corta no siempre al final.** Si cada párrafo termina con una frase breve y rotunda, eso también es un patrón. Se puede abrir con ella, ponerla en medio o no usarla.
- **Ojo con el punto y seguido sistemático.** Partir todo en frases de 10 palabras da un ritmo entrecortado igual de mecánico.
- **Incisos.** Un paréntesis o una aposición entre comas cambia la respiración sin alargar el párrafo.

## Arranques de frase

Rotar entre estas formas sin seguir un orden fijo:

| Arranque | Ejemplo |
|---|---|
| Sujeto directo | "El servidor tardó tres horas en volver." |
| Dato o cifra | "Tres de cada diez pedidos llegaron tarde." |
| Complemento de tiempo o lugar | "En marzo cambiamos de proveedor." |
| Subordinada | "Como el plazo era corto, se priorizó…" |
| Verbo | "Falta revisar el anexo." |
| Objeto adelantado | "Ese error ya lo habíamos visto en enero." |
| Pregunta concreta, no retórica | "¿Quién firma el acta?" |
| Conector, solo si hace falta | "Pero el informe no lo dice." |

Lo que se evita: tres frases seguidas que empiezan por el sujeto, o por "Este/Esta", o por un conector.

## Arranques de párrafo

- Evitar que cada párrafo abra con una frase-tema que anuncie lo que viene ("En cuanto a la metodología…"). A veces el párrafo puede empezar directamente con el primer dato.
- Si dos párrafos seguidos empiezan por el mismo sujeto ("El estudio…", "El estudio…"), se cambia uno: se empieza por el dato o por la consecuencia.
- Un párrafo puede empezar retomando la última palabra del anterior. Enlaza sin conector.

## Longitud de párrafo

- Mezclar a propósito: uno de 2 líneas al lado de uno de 8.
- Un párrafo de una sola frase sirve para destacar algo, pero solo una vez por texto.
- Se corta donde termina la idea, no cuando "ya toca".

## Transiciones

La mejor transición suele ser el orden de las ideas. Si la segunda idea sigue lógicamente a la primera, no necesita "Además". Cuando hace falta conector:
- se elige el que pide la relación (contraste, causa, consecuencia, ejemplo);
- se varía entre conectores, pero también entre poner y no poner;
- "pero" y "así que" suenan más naturales que "sin embargo" y "por consiguiente" fuera del registro académico.

## Pares de ejemplo

Textos inventados para esta guía.

### Académico

**Con tics de IA:**
> En el mundo actual, la gestión del agua juega un papel crucial en la planificación urbana. Es importante destacar que las ciudades mediterráneas afrontan sequías cada vez más largas, más intensas y más frecuentes. Además, el crecimiento de la población aumenta la demanda. Asimismo, las infraestructuras antiguas pierden una parte relevante del agua tratada. En resumen, la gestión hídrica es un desafío clave para el futuro de estas ciudades.

**Reescritura natural:**
> Las ciudades mediterráneas tienen sequías cada vez más largas e intensas, y su población no deja de crecer. Con esa presión, cada litro perdido cuenta. Muchas redes de distribución antiguas pierden por el camino una parte relevante del agua ya tratada, y por eso la gestión del agua es uno de los problemas centrales de su planificación urbana, hoy y en los próximos años.

Qué cambia: desaparecen el arranque genérico, "juega un papel crucial", "es importante destacar", la tríada, "además/asimismo" y el cierre-resumen. La segunda frase es corta y la tercera larga. Todas las ideas siguen (sequías, población, pérdidas en la red, planificación).

### Email profesional

**Con tics de IA:**
> Espero que este mensaje te encuentre bien. Te escribo para informarte de que el informe trimestral estará listo el viernes. Es importante tener en cuenta que todavía faltan los datos de ventas de la zona norte. No dudes en contactarme si tienes cualquier duda. ¡Muchas gracias por tu comprensión!

**Reescritura natural:**
> Hola, Lucía:
>
> El informe trimestral estará el viernes. Ojo: aún me faltan las ventas de la zona norte.
>
> Si tienes alguna duda, me dices. Gracias por la paciencia.

Qué cambia: el asunto va en la primera frase. Se quitan el saludo de plantilla, "es importante tener en cuenta" y el cierre con exclamación. El dato que faltaba sigue ahí, y el agradecimiento también, pero sin fórmula. No se añade nada que el original no dijera, como cuándo llegarán los datos.

### Post para redes

**Con tics de IA:**
> 🚀 ¡Emocionado de compartir que hoy comienzo un nuevo viaje profesional! Después de cinco años increíbles, dejo mi puesto para embarcarme en un viaje apasionante. He aprendido muchísimo, he crecido como persona y he conocido a gente maravillosa. ¡El futuro es prometedor! 💪

**Reescritura natural:**
> Hoy dejo mi puesto, después de cinco años.
>
> He aprendido muchísimo, también como persona. Y me llevo a gente muy buena.
>
> Empiezo una etapa profesional nueva y tengo ganas.

Qué cambia: sin emojis, sin "viaje" repetido y sin cierre motivacional. El gancho es un hecho. La tríada "he aprendido, he crecido, he conocido" se reparte en dos frases de distinta longitud y conserva las tres ideas. "Tengo ganas" recoge el "emocionado" y "el futuro es prometedor" sin inflarlo.
