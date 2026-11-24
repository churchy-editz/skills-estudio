# Voz del usuario

Cuando el usuario da textos suyos, el objetivo es que la reescritura suene a él. Una voz no se imita copiando frases. Se imita reproduciendo sus decisiones: cuánto alarga las frases, qué palabras usa, qué conectores evita y cómo puntúa.

## Cuántas muestras

- 1 muestra: perfil provisional, sobre todo de puntuación y longitud de frase.
- 2-3 muestras: perfil fiable. Lo que se repite entre muestras es voz. Lo que sale en una sola puede ser del tema.
- Las muestras deben ser del mismo registro que el texto a reescribir, si es posible. Un WhatsApp no sirve de modelo para un trabajo académico.

## Qué se mide

| Rasgo | Cómo se mide | Ejemplo de anotación |
|---|---|---|
| Longitud media de frase | contar palabras por frase (`analizar.py muestra.txt muestra.txt` da media y CV) | media 14, CV 0,6: muy variable |
| Variación | CV del ritmo y si alterna o agrupa frases cortas | mete frases de 3-4 palabras para cerrar ideas |
| Vocabulario recurrente | palabras o giros que aparecen en más de una muestra | "la verdad", "en plan", "ojo" |
| Conectores que usa | lista con frecuencia | "pero", "así que", "o sea" |
| Conectores que NO usa | los de `patrones-ia.md` que no aparecen nunca | nunca "asimismo", "no obstante" |
| Persona | yo / nosotros / impersonal | primera persona del singular |
| Puntuación | punto y coma, paréntesis, dos puntos, guiones, exclamaciones | muchos paréntesis, ningún punto y coma |
| Formalidad | tuteo, coloquialismos, tecnicismos | tutea, coloquial suave |
| Rasgos propios | lo que lo distingue | empieza párrafos con una pregunta concreta; usa cifras en número |

## Cómo se presenta

Antes del texto reescrito, 3-4 líneas, sin tabla:

> Tu voz, según las muestras: frases cortas (media 12 palabras) con alguna larga para explicar; primera persona y tuteo; usas "pero" y "así que" y nunca "asimismo" ni "por consiguiente"; muchos paréntesis para aclarar y casi ningún punto y coma.

## Cómo se aplica

1. Ritmo: ajustar la media y la variación de frase a las del perfil, no al defecto general.
2. Conectores: usar los suyos, con su frecuencia. Los que nunca usa no aparecen.
3. Puntuación: reproducir su costumbre (paréntesis, dos puntos, etc.), sin exagerarla.
4. Vocabulario: incorporar sus giros solo donde encajan con naturalidad. Si una muletilla suya sale en una de cada tres muestras, en el texto aparece como mucho una vez.
5. Regla de fidelidad intacta: el perfil cambia cómo se dice, nunca qué se dice.

Límites:
- No se copian frases de las muestras, ni siquiera cambiando una palabra.
- Si el perfil incluye un tic de `patrones-ia.md` (por ejemplo, usa mucho "además"), se respeta su frecuencia real, pero sin pasar los límites del analizador.
- Si el registro pedido choca con la voz (muestras coloquiales, texto académico), se toman ritmo, puntuación y persona del perfil, y vocabulario y formalidad del registro.

## Ejemplo

Usuario ficticio, Dani, técnico de mantenimiento que escribe informes breves.

**Muestra 1:**
> Revisé la bomba 2 el martes. Hacía ruido al arrancar (no siempre, una de cada cuatro veces más o menos), así que cambié el rodamiento. Ahora va fina. Si vuelve a hacerlo, el siguiente paso es mirar el eje.

**Muestra 2:**
> El compresor de la nave B sigue perdiendo presión. No es la válvula: la cambié en enero y el problema sigue igual. Mi apuesta es una fuga en el circuito, pero para encontrarla hace falta parar la línea medio día. Lo dejo propuesto para el próximo paro.

**Perfil:**
> Frases cortas (media 11 palabras) con alguna larga cuando explica una causa; primera persona del singular; conectores "así que" y "pero", nunca "además" ni "por lo tanto"; paréntesis para precisar y dos puntos antes de la explicación; cierra con el siguiente paso.

**Texto a reescribir (redactado de forma genérica):**
> Se ha llevado a cabo la inspección de la cinta transportadora 3. Cabe destacar que se ha detectado un desgaste significativo en la banda. Por lo tanto, se recomienda proceder a su sustitución. Además, es importante señalar que los rodillos se encuentran en buen estado.

**Reescrito en la voz de Dani:**
> Inspeccioné la cinta 3. La banda está bastante gastada, así que hay que cambiarla. Los rodillos están bien. El siguiente paso: pedir la banda nueva y cuadrar el cambio con el próximo paro.

Ojo: el último paso ("pedir la banda nueva y cuadrar el cambio…") añade una acción que el original no tenía. Esto incumple la regla de fidelidad. La versión correcta termina en "Los rodillos están bien." y deja el cierre típico de Dani solo si el original da el dato. El ejemplo lo incluye a propósito, porque es el error más fácil de cometer al imitar una voz: copiar también el *contenido* habitual del autor.
