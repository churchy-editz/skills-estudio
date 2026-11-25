---
name: creador-tests
description: >-
  Crea tests para aprender a partir de material de estudio (PDF, DOCX, texto, fotos
  o los apuntes de creador-apuntes en HTML, DOCX o Markdown). Cada pregunta explica
  por qué la correcta lo es y por qué falla el distractor más tentador, y las opciones
  falsas son errores reales de alumno. Mezcla opción múltiple, verdadero/falso, huecos
  y casos prácticos, y valida la variedad para que el test no tenga forma de molde.
  Entrega un HTML interactivo (nota, repaso por secciones, repetir fallos, versión
  imprimible) y el JSON, exportable a Moodle, Kahoot, Anki, Quizlet o Word. Usar
  cuando el usuario diga "hazme un test de este tema", "genera preguntas tipo test",
  "examen de prueba de estos apuntes", "quiero practicar con preguntas", "make a quiz
  from this" o "practice exam questions", o pida un test, un simulacro o preguntas
  de repaso para estudiar u opositar.
license: MIT
---

# Creador de tests

Convierte un material de estudio en un test que sirva para aprender: cada fallo explica por qué, y las opciones incorrectas son errores que un alumno cometería de verdad. El riesgo principal es el test en molde, con todas las preguntas iguales o una correcta que se adivina por su aspecto. La variedad se planifica antes de redactar y se mide con `scripts/validar.py`.

## 1. Entrada

Acepta PDF, DOCX, texto pegado, fotos de apuntes y los apuntes de creador-apuntes (HTML, DOCX o Markdown).
- Leer el material entero y contar sus palabras antes de preguntar nada.
- Fotos o PDF escaneados: transcribir primero. Lo ilegible no se pregunta.
- Apuntes de creador-apuntes: sus títulos son las secciones del test. Las cajas Dato clave y Ojo señalan lo que más conviene preguntar.
- Diapositivas: el número de preguntas se calcula con las palabras, no con las diapositivas, que traen poco texto. Las etiquetas de los diagramas salen desordenadas al extraer el texto. Si no se puede reconstruir con seguridad qué relaciona un diagrama, no se pregunta por él. Si la presentación termina con preguntas de repaso, cada una tiene que quedar cubierta por alguna pregunta del test.

## 2. Una sola pregunta inicial

Hacer UNA pregunta con los valores por defecto y omitir lo que el usuario ya haya dicho:

> ¿Cómo quieres el test? (si te vale el defecto, responde "ok")
> - Tipos: opción múltiple / verdadero-falso / huecos / casos prácticos / mezcla [defecto: opción múltiple]
> - Nº de preguntas [defecto: ~N] (1 por cada 150 palabras del material, entre 10 y 40)
> - Dificultad: fácil / media / difícil / progresiva [defecto: progresiva]
> - Penalización por fallo: ninguna / -1/3 / -1/4 [defecto: ninguna]

- N se calcula antes de preguntar y se da como número.
- Si se detecta una oposición, sugerir -1/3 en esa línea.
- Si no responde o dice "ok", se usan los valores por defecto.

## 3. Nivel

Deducirlo por la fuente, el vocabulario y lo que diga el usuario: ESO/Bachillerato, universidad, oposiciones o profesional. Con dudas entre dos niveles: vocabulario del más alto, explicaciones del más bajo.
- ESO/Bachillerato: casos cotidianos y vocabulario del libro.
- Universidad: terminología de la disciplina, más preguntas de distinguir y aplicar.
- Oposiciones/normativa: preguntas sobre la literalidad (plazos, cifras, órganos, número de artículo). Cada distractor cambia una sola pieza de la norma.
- Profesional: casos de decisión y detección de errores de procedimiento.

## 4. Planificar antes de redactar

1. Listar los conceptos evaluables del material, sección por sección.
2. Repartir las preguntas en proporción al peso de cada sección. Ninguna sección se queda sin pregunta.
3. Asignar a cada pregunta un nivel cognitivo en rotación: recordar, comprender, distinguir, aplicar, detectar un error, ordenar o relacionar. Ningún nivel pasa del 40 % del test.
4. Asignar a cada pregunta una forma de enunciado y, a cada distractor, una técnica (catálogos en `references/variedad.md`).
5. Con dificultad progresiva: recordar y comprender al principio, aplicar y detectar errores al final.

El plan no se entrega. Sirve para que la variedad salga del diseño y no de retocar el test al final.

## 5. Generar el JSON

Escribir `test-<tema>.json` según `references/esquema.md` (`<tema>` en minúsculas, con guiones y sin tildes). Con dificultad progresiva, poner `"dificultad": "progresiva"` en `meta`. Incluir siempre `meta.secciones`.

## 6. Validar

```
python scripts/validar.py test-<tema>.json
```

El objetivo es "ERRORES: ninguno", "AVISOS DE PATRÓN: ninguno" y "Variedad: 10/10". Los avisos de repetición NO se ignoran: indican que el test tiene forma de molde. El informe dice la categoría y los ids afectados.

Tope de correcciones:
1. **Hasta 3 rondas** de corregir y volver a validar. Los errores se corrigen siempre, sin tope.
2. Si tras la tercera ronda siguen los avisos, retocar no basta. Se **replanifican desde la sección 4 solo las preguntas afectadas**: nuevo concepto, nivel cognitivo, forma de enunciado y técnicas de distractor. Después se redactan de cero y se valida una vez más. El resto del test no se toca.
3. Si aun así queda algún aviso, se entrega el test diciendo qué aviso queda, en qué preguntas y por qué no se ha podido resolver. Por ejemplo: "el material solo tiene dos secciones con datos ordenables y la pregunta de orden necesita tres distractores `orden_alterado`".

## 7. Generar el HTML

```
python scripts/generar_html.py test-<tema>.json test-<tema>.html --paleta <asignatura>
```

Las paletas van dentro de `generar_html.py` y cumplen contraste WCAG AA: `neutra`, `ciencias`, `matematicas`, `historia`, `lengua`, `idiomas`, `derecho`, `economia` y `arte`. Son los mismos colores que usa creador-apuntes, para que apuntes y test combinen. También acepta el nombre de la asignatura (`biologia`, `filosofia`…). El HTML es autocontenido y funciona así:
- Una pregunta cada vez, con barra de progreso. Se maneja con teclado (`1`-`4`, `V`/`F`, `Enter`, `B` para dejar en blanco) y es accesible (ARIA, foco visible, contraste AA).
- Baraja las preguntas y las opciones en cada intento. Con dificultad progresiva, solo baraja dentro de cada nivel.
- Feedback inmediato con la explicación y la sección de origen.
- Al final: nota sobre 10 con la penalización, aciertos, fallos y en blanco, desglose por sección ("Repasa: …") y botones "Repetir solo los fallos" y "Repetir todo".
- Al imprimir: versión en papel con la hoja de soluciones en página aparte.

## 8. Sin código o sin archivos

- Sin ejecución de código: entregar el JSON y el test en Markdown, con las preguntas y, al final, las soluciones con su explicación. Aplicar a mano las comprobaciones de `variedad.md`.
- Sin archivos: solo el Markdown.

## 9. Calidad de cada pregunta

Detalle y ejemplos en `references/reglas-preguntas.md`.
- Cubrir todo el material en proporción a su peso.
- Los distractores son errores reales del tema. Nada de opciones absurdas.
- Prohibido "todas las anteriores" y "ninguna de las anteriores" (el validador lo trata como error).
- Nada que no esté en la fuente: ni datos, ni conceptos, ni casos que contradigan el material.
- Explicación de 1-2 frases: por qué la correcta lo es y por qué falla el distractor más tentador.
- Cada pregunta lleva la sección de origen en `seccion`.

## 10. Antirrepetición

Detalle, límites y ejemplos en `references/variedad.md`.
- **Enunciados:** no más de 2 preguntas pueden empezar con las mismas 3 palabras. Alternar entre pregunta directa, afirmación incompleta, situación ("Un técnico observa que…"), comparación ("¿Qué diferencia a X de Y?"), causa-efecto y orden. Las negativas son como máximo el 10 %, con "NO" en mayúsculas.
- **Opciones:** variar cómo se construyen de una pregunta a otra (cifras, términos, frases, consecuencias). Usar técnicas de distractor distintas: concepto vecino, inversión causa-efecto, dato parcialmente cierto, generalización excesiva, error de cálculo típico, etc.
- **Longitud:** la correcta no es la más larga en más del 30 % de las preguntas, y las opciones de una misma pregunta tienen longitud parecida.
- **Posición:** repartir las correctas entre A y D, sin que ninguna letra pase del 35 % ni haya rachas de 3. Reparto irregular, no uniforme: ninguna letra >35%, pero tampoco todas iguales. En V/F, entre el 40 y el 60 % verdaderas.
- **Pistas:** sin concordancias que delaten (género, número, "un/una" al final del enunciado). Sin "siempre", "nunca", "todos" o "ninguno" solo en los distractores. Sin una palabra del enunciado que solo se repita en la correcta.
- **Explicaciones:** cada una empieza distinto. Nada de "Esto es así porque…" en todas.
- **Entre tests:** si el usuario pide otro test del mismo material, no repetir enunciados ni el plan cognitivo. Cambiar el ángulo: más casos donde antes hubo datos, otras secciones como protagonistas, otros distractores.

## 11. Autorrevisión

Además del validador:
1. ¿Cada pregunta tiene una sola respuesta defendible con la fuente en la mano?
2. ¿Alguna se responde con el enunciado o las opciones de otra?
3. Leídas seguidas, ¿suenan a molde?
4. ¿Los enunciados o las explicaciones suenan a IA? Revisarlos con la lista de `references/tono.md`.

## 12. Entrega

Dar las rutas del HTML y del JSON y el informe de variedad en una línea. Terminar con una sola línea que ofrezca exportar:
"Si te sirve, lo exporto a Moodle (GIFT), Kahoot (CSV), Anki, Quizlet o a un Word imprimible con las soluciones aparte."

Exportar solo lo que se pida:

```
python scripts/exportar.py test-<tema>.json --formato gift|kahoot|anki|quizlet|docx -o salida
```

Word necesita python-docx; si falta, el script da el comando `pip` exacto.

**Kahoot** limita la pregunta (contexto incluido) a 120 caracteres y cada respuesta a 75, y no admite huecos. Antes de omitir nada:
1. Exportar una primera vez. El script lista las preguntas que no caben y su longitud.
2. Copiar el test a `test-<tema>-kahoot.json` y reescribir solo esas preguntas para que quepan sin cambiar el sentido. Se quitan rodeos y datos que no deciden la respuesta, se resume el contexto de los casos y las opciones pasan a formato "X: …". La correcta y las técnicas de distractor no cambian.
3. Validar `test-<tema>-kahoot.json` con `validar.py`, con el tope de la sección 6. Acortar no puede delatar la correcta.
4. Exportar desde `test-<tema>-kahoot.json`. Solo se omiten las de huecos, que Kahoot no admite. Al usuario se le dice el número exacto: "Exportadas 10 de 12; omitidas 2 de huecos (p03, p08)".

## Ejemplo

`examples/test-hemostasia.json` y `.html`: 12 preguntas de tipo mezcla y dificultad progresiva, sobre el texto sintético de hemostasia que también usa de ejemplo creador-apuntes. Tiene 6 secciones y los 6 niveles cognitivos, y pasa `validar.py` con 10/10.
