<!-- huella-skill: caf9f220311b -->
## Flujo

1. Lee el material entero y cuenta sus palabras. Fotos o escaneos: transcribe primero; lo ilegible no se pregunta. Si son apuntes con cajas "Dato clave" u "Ojo", eso es lo que más conviene preguntar.
2. Haz UNA sola pregunta con los valores por defecto y omite lo que el usuario ya haya dicho:
   - tipos: opción múltiple / verdadero-falso / huecos / casos prácticos / mezcla [defecto: opción múltiple];
   - número de preguntas [defecto: 1 por cada 150 palabras, entre 10 y 40; da el número calculado];
   - dificultad: fácil / media / difícil / progresiva [defecto: progresiva];
   - penalización: ninguna / -1/3 / -1/4 [defecto: ninguna; sugiere -1/3 si es una oposición].
3. Deduce el nivel (ESO/Bachillerato, universidad, oposiciones, profesional). En oposiciones, cada distractor cambia una sola pieza de la norma: plazo, cifra, órgano o artículo.
4. Planifica antes de redactar (el plan no se entrega): reparte las preguntas por secciones en proporción a su peso, sin dejar ninguna sin pregunta. Rota los niveles cognitivos (recordar, comprender, distinguir, aplicar, detectar un error, ordenar). Asigna a cada distractor una técnica (concepto vecino, inversión causa-efecto, dato parcial, generalización, error de cálculo, cifra cercana, orden alterado, intercambio, función opuesta). Con dificultad progresiva, lo fácil al principio.
5. Redacta, comprueba los límites de abajo y corrige. Si tras tres rondas sigue fallando algo, rehaz desde el plan solo esas preguntas.

## Reglas de cada pregunta

- Una sola respuesta defendible con la fuente en la mano. Nada que no esté en la fuente.
- Distractores que son errores reales del tema, nunca opciones absurdas. Prohibido "todas las anteriores" y "ninguna de las anteriores".
- Explicación de 1-2 frases: por qué la correcta lo es y por qué falla el distractor más tentador. Cada explicación empieza distinto; nada de "La respuesta correcta es…".
- Cada pregunta indica la sección del material de la que sale.
- Ninguna pregunta se responde con el enunciado o las opciones de otra.

## Límites antimolde (cuéntalos sobre el test completo)

- Como mucho 2 enunciados con las mismas 3 primeras palabras. Alterna pregunta directa, frase incompleta, situación, comparación, causa-efecto y orden.
- La correcta es la opción más larga en el 30 % de las preguntas o menos. En cada pregunta, la opción más larga mide como mucho el doble que la más corta.
- Ninguna letra es la correcta en más del 35 % de las preguntas, sin rachas de 3 iguales. Con 8 o más preguntas de opciones, el reparto tampoco puede ser perfectamente uniforme.
- En verdadero/falso, entre el 40 y el 60 % son verdaderas.
- Ningún nivel cognitivo ni técnica de distractor pasa del 40 %. Negativas como mucho el 10 %, con "NO" en mayúsculas.
- Sin pistas: "siempre/nunca/todos/ninguno" no aparecen solo en distractores; ninguna palabra del enunciado se repite solo en la correcta; ningún enunciado termina en artículo.

## Formato de salida

- **Con archivos:** `test-<tema>.json` con `meta` (titulo, asignatura, nivel, penalizacion, fuente, dificultad, secciones) y `preguntas`. Cada pregunta lleva id, tipo (multiple, vf, huecos, caso), nivel_cognitivo, tecnica_distractor, enunciado, opciones (4, en multiple y caso), correcta (índice 0-3, true/false o lista de respuestas válidas en huecos), explicacion, dificultad (1-3) y seccion. Los huecos llevan exactamente un `___`. El esquema completo está en `esquema.md`, en el portable completo.
- **HTML interactivo:** solo si puedes ejecutar los scripts de la skill.
- **Siempre, también sin archivos:** el test en Markdown con las preguntas y, al final y aparte, las soluciones con su explicación.
- Entrega con una línea sobre la variedad (qué límites se cumplen y cuál queda, si queda alguno). Termina ofreciendo, en una sola línea, exportarlo a Moodle (GIFT), Kahoot, Anki, Quizlet o Word.
- Si piden otro test del mismo material, cambia el ángulo: otras secciones protagonistas, más casos donde antes hubo datos, otros distractores.
