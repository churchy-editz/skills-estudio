# Reglas para escribir preguntas

Un test sirve para aprender si cada fallo enseña algo. Para eso, la pregunta tiene que medir el concepto y no la habilidad de adivinar. Las opciones falsas tienen que ser errores que un alumno cometería de verdad.

## Enunciados

- **Una sola idea por pregunta.** Si para responder hay que saber dos cosas, el fallo no dice cuál de las dos falta.
- **La pregunta se entiende sin leer las opciones.** Tapando las opciones, alguien que se sabe el tema debería poder decir la respuesta.
- **Lo importante, no lo anecdótico.** Se pregunta lo que el material trata como central: definiciones, causas, diferencias, pasos, cifras evaluables. Nada de detalles de relleno ("¿en qué párrafo…?").
- **Sin pistas de forma.** El enunciado no termina en "un"/"una"/"el"/"la" si solo una opción concuerda con el artículo. Sin palabras del enunciado que solo se repitan en la correcta.
- **Negativas solo cuando aporten.** Máximo el 10 % del test, con "NO" en mayúsculas. Una negativa sirve para comprobar que el alumno descarta bien, no para despistar.
- **Casos prácticos cortos.** Dos o tres frases con los datos justos para decidir. Si el caso trae datos que no se usan, es para entrenar a descartar, y la explicación lo dice.
- **Oposiciones y normativa:** se pregunta por la literalidad (plazos, cifras, órganos, número de artículo). Los distractores cambian una sola pieza de la norma: el plazo, el órgano o el requisito.

## Distractores

Cada opción falsa tiene que responder a la pregunta "¿qué error concreto me haría elegir esto?". Si no hay respuesta, la opción es relleno y se cambia.

- **Del mismo tipo que la correcta.** Si la correcta es una cifra, las cuatro son cifras. Si es una consecuencia, las cuatro son consecuencias.
- **Longitud parecida.** Ninguna opción mide más del doble que otra, y la correcta no es la más larga en más del 30 % de las preguntas. Si la correcta necesita un matiz, los distractores también llevan el suyo.
- **Técnicas variadas.** Confundir con un concepto vecino, invertir causa y efecto, dato parcialmente cierto, generalizar de más, error de cálculo típico, cifra cercana, orden alterado, intercambio de atributos, función opuesta. Catálogo con ejemplos en `variedad.md`.
- **Prohibido** "todas las anteriores", "ninguna de las anteriores", "ambas son correctas" y equivalentes. Una opción así no mide nada concreto, y el validador la trata como error.
- **Nada inventado.** Los distractores pueden ser falsos para la pregunta, pero los conceptos que nombran salen del material: un concepto vecino real del tema, no un término que no aparece en él.
- **Absolutos repartidos.** "Siempre", "nunca", "todos" y "ninguno" no pueden aparecer solo en los distractores. Si la correcta es una afirmación matizada y las falsas son absolutas, el alumno acierta sin saber.

## Explicaciones

- Una o dos frases. La primera dice por qué la correcta lo es. La segunda, por qué falla el distractor más tentador, nombrándolo.
- Cada explicación empieza distinto. Prohibidos los arranques fijos ("Esto es así porque…", "La respuesta correcta es…"). El validador avisa si más de dos explicaciones empiezan con las mismas tres palabras.
- Tono de compañero que explica bien: frases cortas, sin muletillas, sin emojis y sin cierres del tipo "¡Sigue así!". Lista completa en `tono.md`.
- La sección de origen va en `seccion`, no dentro de la explicación.

## Errores típicos de los tests generados por IA

| Error | Cómo se nota | Arreglo |
|---|---|---|
| Correcta más larga | La opción con más matices es casi siempre la buena | Igualar longitudes; dar matices también a los distractores |
| Opciones absurdas | Un distractor que nadie elegiría ("La fotosíntesis" en una pregunta de derecho) | Sustituirlo por un error real del tema |
| Pistas gramaticales | "Es una…" y solo una opción es femenina | Enunciado que no condicione el género ni el número |
| Preguntas triviales | Se responde con sentido común o copiando una palabra del enunciado | Preguntar por la relación o la diferencia, no por la palabra |
| Molde | Todas empiezan por "¿Cuál es…?" y tienen la misma forma | Rotar formas de enunciado (`variedad.md`) |
| Correcta siempre en B o C | La posición se repite | Repartir A-D; el validador lo mide |
| Explicaciones idénticas | "Esto es así porque…" en todas | Empezar cada una por lo que la hace única |
| Una pregunta responde otra | El enunciado de la 8 contiene la respuesta de la 3 | Leer el test seguido antes de entregarlo |

## Pares de ejemplo (mala → buena)

Contenido genérico, solo para mostrar la técnica.

### 1. La correcta se delata por la longitud y el artículo

**Mala:**
> El orgánulo donde se produce la mayor parte del ATP de la célula es una…
> A) ribosoma · B) mitocondria, que realiza la respiración celular aerobia · C) núcleo · D) aparato de Golgi

**Buena:**
> ¿En qué orgánulo se produce la mayor parte del ATP de la célula?
> A) En el ribosoma · B) En la mitocondria · C) En el cloroplasto · D) En el núcleo

Qué cambia: el enunciado ya no condiciona el género y las cuatro opciones miden lo mismo. El cloroplasto sustituye al aparato de Golgi porque es el error real: también produce ATP, pero en las células vegetales y para la fotosíntesis.

### 2. Distractores de relleno

**Mala:**
> ¿Qué provoca la subida de los tipos de interés?
> A) Abarata los créditos · B) Encarece los créditos · C) Aumenta la población · D) Cambia el clima

**Buena:**
> Si el banco central sube los tipos de interés, ¿qué es lo más probable a corto plazo?
> A) Que los créditos se abaraten y suba el consumo · B) Que los créditos se encarezcan y baje el consumo · C) Que suba la inflación porque hay más dinero en circulación · D) Que bajen los precios de inmediato en todos los sectores

Qué cambia: C invierte causa y efecto, A es la confusión de sentido y D generaliza de más. Cada distractor es un error de alumno; en la versión mala, C y D no los elegiría nadie.

### 3. Se responde copiando una palabra

**Mala:**
> ¿Cómo se llama el proceso por el que las plantas fabrican materia orgánica a partir de la luz?
> A) Respiración · B) Fotosíntesis, proceso que usa la luz · C) Transpiración · D) Fermentación

**Buena:**
> Una planta pasa una semana en total oscuridad con agua y CO₂ de sobra. ¿Qué proceso deja de hacer?
> A) La respiración celular · B) La fotosíntesis · C) La transpiración · D) La absorción de agua

Qué cambia: en la mala, "luz" aparece en el enunciado y solo en la correcta. La buena obliga a aplicar el concepto a un caso, y la respiración es un distractor tentador porque también intercambia gases.
