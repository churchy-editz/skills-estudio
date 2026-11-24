# Variedad: cómo evitar el test en molde

Un test en el que todas las preguntas tienen la misma forma se responde por reconocimiento de patrones, no por conocimiento. Este archivo da el repertorio para variar y los límites que mide `scripts/validar.py`.

## Límites que mide el validador

| Qué | Límite | Categoría en el informe |
|---|---|---|
| Enunciados con las mismas 3 primeras palabras | máx. 2 | `inicio_enunciado` |
| Similitud de palabras entre dos enunciados (Jaccard) | ≤ 0,6 | `similitud` |
| Correcta más larga que todas las demás | ≤ 30 % de las preguntas | `longitud_correcta` |
| Opción más larga / más corta en una pregunta | ≤ 2 | `longitud_opciones` |
| Correcta en una misma letra | ≤ 35 % (o ⌈n/4⌉ si hay pocas) | `posicion` |
| Racha de correctas en la misma letra | máx. 2 seguidas | `posicion` |
| Verdaderas en V/F | 40-60 % | `vf_equilibrio` |
| Un mismo nivel cognitivo | ≤ 40 % | `nivel_cognitivo` |
| Una misma técnica de distractor | ≤ 40 % de los distractores | `tecnica_distractor` |
| Preguntas negativas | ≤ 10 %, con "NO" en mayúsculas | `negativas` |
| "siempre/nunca/todos/ninguno" solo en distractores | 0 | `absolutas` |
| Palabra del enunciado que solo aparece en la correcta | 0 | `literal` |
| Enunciado que termina en artículo | 0 | `pista_gramatical` |
| Explicaciones con las mismas 3 primeras palabras | máx. 2 | `explicaciones` |
| Secciones de `meta.secciones` sin preguntas | 0 | `secciones` |

La puntuación "Variedad: X/10" es la proporción de categorías sin avisos. Se entrega con 10/10: los avisos no se ignoran.

## Formas de enunciado

Rotar entre estas formas. Ninguna debería ocupar más de un tercio del test.

| Forma | Ejemplo genérico |
|---|---|
| Pregunta directa | ¿Qué órgano produce la bilis? |
| Afirmación incompleta | Cuando la demanda supera a la oferta, el precio tiende a… |
| Situación | Una técnica de laboratorio observa que la muestra se vuelve turbia al enfriarse. ¿Qué ha pasado? |
| Negativa (máx. 10 %) | ¿Cuál de estos factores NO influye en la velocidad de reacción? |
| Comparación | ¿Qué diferencia a un virus de una bacteria? |
| Causa-efecto | ¿Por qué el hielo flota en el agua líquida? |
| Consecuencia | Si se elimina el depredador de un ecosistema, ¿qué es lo más probable a corto plazo? |
| Orden | ¿En qué orden se suceden las fases de la mitosis? |
| Detectar el error | Un compañero resume así el proceso. ¿En qué paso se equivoca? |
| Dato literal (oposiciones) | ¿Qué plazo fija el art. 21 para resolver el procedimiento? |

Variar también la forma de las opciones entre preguntas: términos sueltos, cifras, frases cortas, consecuencias, secuencias con flechas, pares "X; Y".

## Técnicas de distractor

| Técnica (`tecnica_distractor`) | Qué error imita | Ejemplo genérico (correcta → distractor) |
|---|---|---|
| `concepto_vecino` | Confundir con un concepto cercano del mismo tema | mitocondria → cloroplasto |
| `inversion_causa_efecto` | Poner el efecto como causa, o el proceso al revés | "la condensación forma nubes" → "las nubes provocan la condensación" |
| `dato_parcial` | Algo cierto que no responde a la pregunta | "porque no tienen núcleo" (cierto, pero no es la razón) |
| `generalizacion` | Extender a todos los casos lo que vale para algunos | "algunos metales" → "todos los metales" |
| `error_calculo` | El resultado de un fallo típico en la operación | olvidar dividir entre 2, sumar en vez de restar |
| `cifra_cercana` | Un número parecido al correcto | 21 días → 30 días; factor XIII → factor XII |
| `orden_alterado` | Los pasos correctos en otro orden | A → B → C → D frente a A → C → B → D |
| `intercambio` | Los atributos de dos conceptos cambiados entre sí | "X hace P e Y hace Q" → "X hace Q e Y hace P" |
| `funcion_opuesta` | Lo que hace justo lo contrario | un activador en lugar de un inhibidor |

En las preguntas de orden es normal que los tres distractores sean `orden_alterado`. El resto del test compensa.

## Niveles cognitivos

Repartir las preguntas entre los seis niveles. Ninguno pasa del 40 %. Si hay que elegir, quitar preguntas de "recordar".

| Nivel (`nivel_cognitivo`) | Verbos asociados | Qué comprueba |
|---|---|---|
| `recordar` | nombrar, identificar, citar | Que el dato está en la memoria |
| `comprender` | explicar, justificar, interpretar | Que se sabe por qué |
| `distinguir` | diferenciar, comparar, clasificar | Que no se mezclan conceptos parecidos |
| `aplicar` | resolver, predecir, diagnosticar | Que se usa el concepto en un caso nuevo |
| `detectar_error` | corregir, revisar, encontrar el fallo | Que se reconoce una versión incorrecta |
| `ordenar` | secuenciar, relacionar, encadenar | Que se conoce el orden o la relación entre piezas |

## Antes y después: cinco preguntas en molde

Contenido genérico (fotosíntesis), solo para mostrar el cambio.

### En molde

1. ¿Cuál es el orgánulo donde ocurre la fotosíntesis? A) **El cloroplasto, orgánulo de la fotosíntesis** · B) Núcleo · C) Ribosoma · D) Vacuola
2. ¿Cuál es el gas que se libera en la fotosíntesis? A) **El oxígeno, que se libera a la atmósfera** · B) CO₂ · C) Nitrógeno · D) Metano
3. ¿Cuál es el pigmento que capta la luz? A) **La clorofila, pigmento verde que capta la luz** · B) Caroteno siempre · C) Melanina · D) Hemoglobina
4. ¿Cuál es la fuente de energía de la fotosíntesis? A) **La luz solar, fuente de energía** · B) El calor · C) El suelo · D) El agua
5. ¿Cuál es el producto principal de la fotosíntesis? A) **La glucosa, producto principal** · B) Proteínas · C) Grasas · D) Vitaminas

Fallos: las cinco empiezan por "¿Cuál es el/la…", la correcta siempre es la A y la más larga, y repite palabras del enunciado ("orgánulo", "libera", "capta la luz"). "Siempre" solo aparece en un distractor. Todas son de "recordar" y los distractores no corresponden a errores reales: nadie piensa que la fotosíntesis produzca metano.

### Con variedad

1. **(situación, aplicar)** Una planta se deja una semana a oscuras con agua y CO₂ de sobra. ¿Qué deja de producir? A) Agua por transpiración · B) CO₂ por respiración · **C) Oxígeno por fotosíntesis** · D) Raíces nuevas
2. **(comparación, distinguir)** ¿Qué diferencia a la fase luminosa de la fase oscura? **A) La luminosa capta energía; la oscura fija el CO₂** · B) La luminosa fija el CO₂; la oscura capta energía · C) La luminosa ocurre de día; la oscura, solo de noche · D) La luminosa produce glucosa; la oscura, oxígeno
3. **(huecos, recordar)** El pigmento que capta la luz en los cloroplastos es la ___. → clorofila
4. **(causa-efecto, comprender)** ¿Por qué las hojas de muchas plantas se ven verdes? A) Porque absorben sobre todo la luz verde · **B) Porque la clorofila refleja la luz verde** · C) Porque la clorofila emite luz verde al trabajar · D) Porque las hojas contienen glucosa verde
5. **(V/F, detectar error)** "En la fotosíntesis la planta consume oxígeno y libera CO₂." → Falso (`inversion_causa_efecto`: es lo que ocurre en la respiración).

Qué cambia: cinco formas de enunciado y cinco niveles, con la correcta en posiciones distintas. Las opciones tienen longitudes parecidas y cada distractor corresponde a un error real. En la 2, B es un intercambio de atributos y C generaliza de más ("solo de noche"). En la 4, A es el error clásico de confundir absorber con reflejar.
