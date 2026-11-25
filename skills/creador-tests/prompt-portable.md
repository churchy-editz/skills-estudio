# creador-tests (versión portable)

<!-- Generado por tools/generar_portables.py a partir de SKILL.md, references/ y assets/. No lo edites a mano: regenéralo. -->

Estas son las instrucciones completas de la skill, en un solo texto para usarlas en un chat sin soporte de skills (un GPT, un Gem o un proyecto). Donde se habla de scripts (`scripts/…`): si puedes ejecutar código pero no tienes los scripts, o no puedes ejecutar código, aplica a mano las comprobaciones de la sección «Si no puedes ejecutar código», al final de las instrucciones. Los archivos de referencia van como anexos al final.

**Cuándo usarla:** Crea tests para aprender a partir de material de estudio (PDF, DOCX, texto, fotos o los apuntes de creador-apuntes en HTML, DOCX o Markdown). Cada pregunta explica por qué la correcta lo es y por qué falla el distractor más tentador, y las opciones falsas son errores reales de alumno. Mezcla opción múltiple, verdadero/falso, huecos y casos prácticos, y valida la variedad para que el test no tenga forma de molde. Entrega un HTML interactivo (nota, repaso por secciones, repetir fallos, versión imprimible) y el JSON, exportable a Moodle, Kahoot, Anki, Quizlet o Word. Usar cuando el usuario diga "hazme un test de este tema", "genera preguntas tipo test", "examen de prueba de estos apuntes", "quiero practicar con preguntas", "make a quiz from this" o "practice exam questions", o pida un test, un simulacro o preguntas de repaso para estudiar u opositar.

## Creador de tests

Convierte un material de estudio en un test que sirva para aprender: cada fallo explica por qué, y las opciones incorrectas son errores que un alumno cometería de verdad. El riesgo principal es el test en molde, con todas las preguntas iguales o una correcta que se adivina por su aspecto. La variedad se planifica antes de redactar y se mide con `scripts/validar.py`.

### 1. Entrada

Acepta PDF, DOCX, texto pegado, fotos de apuntes y los apuntes de creador-apuntes (HTML, DOCX o Markdown).
- Leer el material entero y contar sus palabras antes de preguntar nada.
- Fotos o PDF escaneados: transcribir primero. Lo ilegible no se pregunta.
- Apuntes de creador-apuntes: sus títulos son las secciones del test. Las cajas Dato clave y Ojo señalan lo que más conviene preguntar.
- Diapositivas: el número de preguntas se calcula con las palabras, no con las diapositivas, que traen poco texto. Las etiquetas de los diagramas salen desordenadas al extraer el texto. Si no se puede reconstruir con seguridad qué relaciona un diagrama, no se pregunta por él. Si la presentación termina con preguntas de repaso, cada una tiene que quedar cubierta por alguna pregunta del test.

### 2. Una sola pregunta inicial

Hacer UNA pregunta con los valores por defecto y omitir lo que el usuario ya haya dicho:

> ¿Cómo quieres el test? (si te vale el defecto, responde "ok")
> - Tipos: opción múltiple / verdadero-falso / huecos / casos prácticos / mezcla [defecto: opción múltiple]
> - Nº de preguntas [defecto: ~N] (1 por cada 150 palabras del material, entre 10 y 40)
> - Dificultad: fácil / media / difícil / progresiva [defecto: progresiva]
> - Penalización por fallo: ninguna / -1/3 / -1/4 [defecto: ninguna]

- N se calcula antes de preguntar y se da como número.
- Si se detecta una oposición, sugerir -1/3 en esa línea.
- Si no responde o dice "ok", se usan los valores por defecto.

### 3. Nivel

Deducirlo por la fuente, el vocabulario y lo que diga el usuario: ESO/Bachillerato, universidad, oposiciones o profesional. Con dudas entre dos niveles: vocabulario del más alto, explicaciones del más bajo.
- ESO/Bachillerato: casos cotidianos y vocabulario del libro.
- Universidad: terminología de la disciplina, más preguntas de distinguir y aplicar.
- Oposiciones/normativa: preguntas sobre la literalidad (plazos, cifras, órganos, número de artículo). Cada distractor cambia una sola pieza de la norma.
- Profesional: casos de decisión y detección de errores de procedimiento.

### 4. Planificar antes de redactar

1. Listar los conceptos evaluables del material, sección por sección.
2. Repartir las preguntas en proporción al peso de cada sección. Ninguna sección se queda sin pregunta.
3. Asignar a cada pregunta un nivel cognitivo en rotación: recordar, comprender, distinguir, aplicar, detectar un error, ordenar o relacionar. Ningún nivel pasa del 40 % del test.
4. Asignar a cada pregunta una forma de enunciado y, a cada distractor, una técnica (catálogos en el anexo `variedad.md`).
5. Con dificultad progresiva: recordar y comprender al principio, aplicar y detectar errores al final.

El plan no se entrega. Sirve para que la variedad salga del diseño y no de retocar el test al final.

### 5. Generar el JSON

Escribir `test-<tema>.json` según el anexo `esquema.md` (`<tema>` en minúsculas, con guiones y sin tildes). Con dificultad progresiva, poner `"dificultad": "progresiva"` en `meta`. Incluir siempre `meta.secciones`.

### 6. Validar

```
python scripts/validar.py test-<tema>.json
```

El objetivo es "ERRORES: ninguno", "AVISOS DE PATRÓN: ninguno" y "Variedad: 10/10". Los avisos de repetición NO se ignoran: indican que el test tiene forma de molde. El informe dice la categoría y los ids afectados.

Tope de correcciones:
1. **Hasta 3 rondas** de corregir y volver a validar. Los errores se corrigen siempre, sin tope.
2. Si tras la tercera ronda siguen los avisos, retocar no basta. Se **replanifican desde la sección 4 solo las preguntas afectadas**: nuevo concepto, nivel cognitivo, forma de enunciado y técnicas de distractor. Después se redactan de cero y se valida una vez más. El resto del test no se toca.
3. Si aun así queda algún aviso, se entrega el test diciendo qué aviso queda, en qué preguntas y por qué no se ha podido resolver. Por ejemplo: "el material solo tiene dos secciones con datos ordenables y la pregunta de orden necesita tres distractores `orden_alterado`".

### 7. Generar el HTML

```
python scripts/generar_html.py test-<tema>.json test-<tema>.html --paleta <asignatura>
```

Las paletas van dentro de `generar_html.py` y cumplen contraste WCAG AA: `neutra`, `ciencias`, `matematicas`, `historia`, `lengua`, `idiomas`, `derecho`, `economia` y `arte`. Son los mismos colores que usa creador-apuntes, para que apuntes y test combinen. También acepta el nombre de la asignatura (`biologia`, `filosofia`…). El HTML es autocontenido y funciona así:
- Una pregunta cada vez, con barra de progreso. Se maneja con teclado (`1`-`4`, `V`/`F`, `Enter`, `B` para dejar en blanco) y es accesible (ARIA, foco visible, contraste AA).
- Baraja las preguntas y las opciones en cada intento. Con dificultad progresiva, solo baraja dentro de cada nivel.
- Feedback inmediato con la explicación y la sección de origen.
- Al final: nota sobre 10 con la penalización, aciertos, fallos y en blanco, desglose por sección ("Repasa: …") y botones "Repetir solo los fallos" y "Repetir todo".
- Al imprimir: versión en papel con la hoja de soluciones en página aparte.

### 8. Sin código o sin archivos

- Sin ejecución de código: entregar el JSON y el test en Markdown, con las preguntas y, al final, las soluciones con su explicación. Aplicar a mano las comprobaciones de `variedad.md`.
- Sin archivos: solo el Markdown.

### 9. Calidad de cada pregunta

Detalle y ejemplos en el anexo `reglas-preguntas.md`.
- Cubrir todo el material en proporción a su peso.
- Los distractores son errores reales del tema. Nada de opciones absurdas.
- Prohibido "todas las anteriores" y "ninguna de las anteriores" (el validador lo trata como error).
- Nada que no esté en la fuente: ni datos, ni conceptos, ni casos que contradigan el material.
- Explicación de 1-2 frases: por qué la correcta lo es y por qué falla el distractor más tentador.
- Cada pregunta lleva la sección de origen en `seccion`.

### 10. Antirrepetición

Detalle, límites y ejemplos en el anexo `variedad.md`.
- **Enunciados:** no más de 2 preguntas pueden empezar con las mismas 3 palabras. Alternar entre pregunta directa, afirmación incompleta, situación ("Un técnico observa que…"), comparación ("¿Qué diferencia a X de Y?"), causa-efecto y orden. Las negativas son como máximo el 10 %, con "NO" en mayúsculas.
- **Opciones:** variar cómo se construyen de una pregunta a otra (cifras, términos, frases, consecuencias). Usar técnicas de distractor distintas: concepto vecino, inversión causa-efecto, dato parcialmente cierto, generalización excesiva, error de cálculo típico, etc.
- **Longitud:** la correcta no es la más larga en más del 30 % de las preguntas, y las opciones de una misma pregunta tienen longitud parecida.
- **Posición:** repartir las correctas entre A y D, sin que ninguna letra pase del 35 % ni haya rachas de 3. Reparto irregular, no uniforme: ninguna letra >35%, pero tampoco todas iguales. En V/F, entre el 40 y el 60 % verdaderas.
- **Pistas:** sin concordancias que delaten (género, número, "un/una" al final del enunciado). Sin "siempre", "nunca", "todos" o "ninguno" solo en los distractores. Sin una palabra del enunciado que solo se repita en la correcta.
- **Explicaciones:** cada una empieza distinto. Nada de "Esto es así porque…" en todas.
- **Entre tests:** si el usuario pide otro test del mismo material, no repetir enunciados ni el plan cognitivo. Cambiar el ángulo: más casos donde antes hubo datos, otras secciones como protagonistas, otros distractores.

### 11. Autorrevisión

Además del validador:
1. ¿Cada pregunta tiene una sola respuesta defendible con la fuente en la mano?
2. ¿Alguna se responde con el enunciado o las opciones de otra?
3. Leídas seguidas, ¿suenan a molde?
4. ¿Los enunciados o las explicaciones suenan a IA? Revisarlos con la lista de el anexo `tono.md`.

### 12. Entrega

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

## Si no puedes ejecutar código

`scripts/validar.py` comprueba el test; `generar_html.py` y `exportar.py` producen los archivos. Sin código:

- **Formato de entrega:** el JSON (si se pueden crear archivos) y el test en Markdown con las soluciones y sus explicaciones al final, como dice la sección 8. Los formatos de exportación (GIFT, CSV de Kahoot…) solo se escriben a mano si el usuario los pide.
- **Errores, que hay que corregir siempre:** cada pregunta tiene `id` único, `tipo`, `nivel_cognitivo`, `enunciado`, `explicacion`, `dificultad` (1-3) y `seccion`; las de opción múltiple y casos, 4 opciones distintas y `correcta` entre 0 y 3; las de huecos, exactamente un `___`; ninguna opción es "todas/ninguna de las anteriores".
- **Variedad (límites de la tabla del anexo `variedad.md`):**
  - como mucho 2 enunciados con las mismas 3 primeras palabras;
  - la correcta es la opción más larga en el 30 % de las preguntas o menos, y en cada pregunta la opción más larga mide como mucho el doble que la más corta;
  - ninguna letra es la correcta en más del 35 % de las preguntas y no hay rachas de 3 iguales; con 8 o más preguntas de opciones, las cuatro letras tampoco pueden salir exactamente las mismas veces;
  - en verdadero/falso, entre el 40 y el 60 % son verdaderas;
  - ningún nivel cognitivo ni ninguna técnica de distractor pasa del 40 %;
  - negativas, como mucho el 10 %, con "NO" en mayúsculas;
  - "siempre/nunca/todos/ninguno" no aparecen solo en los distractores;
  - ninguna palabra del enunciado se repite solo en la correcta, y ningún enunciado termina en artículo;
  - como mucho 2 explicaciones empiezan con las mismas 3 palabras;
  - todas las secciones tienen al menos una pregunta.
- Cuenta cada límite sobre el test completo antes de entregarlo e indica en la entrega si queda alguno sin cumplir y por qué.

---

## Anexo: `esquema.md`

### Esquema del JSON

Un test es un archivo `test-<tema>.json` con dos claves: `meta` y `preguntas`. `scripts/validar.py` comprueba todo lo que aparece aquí. Lo marcado como error impide generar el HTML.

#### meta

| Clave | Tipo | Obligatoria | Valores |
|---|---|---|---|
| `titulo` | texto | sí | Título del test |
| `asignatura` | texto | sí | Nombre de la asignatura ("Biología") |
| `nivel` | texto | sí | `eso`, `bachillerato`, `universidad`, `oposiciones`, `profesional` |
| `penalizacion` | texto | sí | `ninguna`, `1/3` o `1/4` |
| `fuente` | texto | sí | Archivo o material del que salen las preguntas |
| `dificultad` | texto | no | `facil`, `media`, `dificil` o `progresiva`. Con `progresiva`, el HTML baraja solo dentro de cada nivel de dificultad para que el orden siga subiendo |
| `secciones` | lista de textos | no | Secciones del material. Si está, el validador avisa de las secciones sin preguntas |

#### preguntas[]

| Clave | Tipo | Tipos que la usan | Notas |
|---|---|---|---|
| `id` | texto | todos | Único: `p01`, `p02`… |
| `tipo` | texto | todos | `multiple`, `vf`, `huecos`, `caso` |
| `nivel_cognitivo` | texto | todos | `recordar`, `comprender`, `distinguir`, `aplicar`, `detectar_error`, `ordenar` |
| `tecnica_distractor` | lista, texto o null | todos | Ver abajo |
| `enunciado` | texto | todos | En huecos, con exactamente un `___` |
| `contexto` | texto | solo `caso` | La situación. Prohibido en los demás tipos |
| `opciones` | lista de 4 textos | `multiple`, `caso` | Sin repetidas y sin "todas/ninguna de las anteriores" |
| `correcta` | según tipo | todos | `multiple`/`caso`: índice 0-3. `vf`: `true`/`false`. `huecos`: lista de respuestas aceptadas |
| `explicacion` | texto | todos | 1-2 frases: por qué la correcta lo es y por qué falla el distractor más tentador |
| `dificultad` | entero | todos | 1, 2 o 3 |
| `seccion` | texto | todos | Sección del material de la que sale. Si `meta.secciones` existe, tiene que coincidir con una de ellas |

##### tecnica_distractor

Dice con qué técnica se construyó cada opción falsa (catálogo en `variedad.md`).

- `multiple` y `caso`: lista de 4 elementos alineada con `opciones`, con `null` en la posición de la correcta.
- `vf`: si el enunciado es falso, la técnica de la trampa que contiene (texto). Si es verdadero, `null`.
- `huecos`: `null`.

Técnicas válidas: `concepto_vecino`, `inversion_causa_efecto`, `dato_parcial`, `generalizacion`, `error_calculo`, `cifra_cercana`, `orden_alterado`, `intercambio`, `funcion_opuesta`.

##### Huecos

La comparación del HTML no distingue tildes ni mayúsculas, e ignora la puntuación de los extremos. Hay que incluir todas las formas válidas: sinónimos aceptados por la fuente, cifra y número escrito, número romano y arábigo.

#### Un ejemplo de cada tipo

Contenido genérico, solo para mostrar la forma.

```json
{
  "meta": {
    "titulo": "El ciclo del agua",
    "asignatura": "Ciencias naturales",
    "nivel": "eso",
    "penalizacion": "ninguna",
    "dificultad": "progresiva",
    "fuente": "tema-5-ciclo-agua.pdf",
    "secciones": ["Evaporación y condensación", "Precipitación", "Agua en el suelo"]
  },
  "preguntas": [
    {
      "id": "p01",
      "tipo": "multiple",
      "nivel_cognitivo": "recordar",
      "tecnica_distractor": ["inversion_causa_efecto", null, "concepto_vecino", "dato_parcial"],
      "enunciado": "¿Cómo se llama el paso del agua de líquido a vapor?",
      "opciones": ["Condensación", "Evaporación", "Precipitación", "Sublimación"],
      "correcta": 1,
      "explicacion": "Pasar de líquido a vapor es evaporarse. La condensación es justo el camino contrario.",
      "dificultad": 1,
      "seccion": "Evaporación y condensación"
    },
    {
      "id": "p02",
      "tipo": "vf",
      "nivel_cognitivo": "detectar_error",
      "tecnica_distractor": "concepto_vecino",
      "enunciado": "La precipitación devuelve el agua del suelo a la atmósfera en forma de vapor.",
      "correcta": false,
      "explicacion": "Falso: eso describe la evaporación. La precipitación hace el viaje inverso, de las nubes al suelo.",
      "dificultad": 2,
      "seccion": "Precipitación"
    },
    {
      "id": "p03",
      "tipo": "huecos",
      "nivel_cognitivo": "ordenar",
      "tecnica_distractor": null,
      "enunciado": "Tras evaporarse y condensarse, el agua vuelve a la superficie mediante la ___.",
      "correcta": ["precipitación", "lluvia"],
      "explicacion": "Cierra el ciclo: evaporación, condensación y, por último, precipitación.",
      "dificultad": 2,
      "seccion": "Precipitación"
    },
    {
      "id": "p04",
      "tipo": "caso",
      "nivel_cognitivo": "aplicar",
      "tecnica_distractor": [null, "generalizacion", "orden_alterado", "concepto_vecino"],
      "contexto": "En un día caluroso, un vaso con hielo se moja por fuera aunque no gotea.",
      "enunciado": "¿De dónde sale esa agua?",
      "opciones": [
        "Del aire, cuyo vapor se condensa al enfriarse",
        "Del hielo, que atraviesa el cristal al fundirse",
        "Del interior, que se evapora y vuelve a caer",
        "Del cristal, que suda cuando cambia de temperatura"
      ],
      "correcta": 0,
      "explicacion": "El aire húmedo toca el cristal frío y su vapor se condensa. El hielo no puede atravesar el vidrio.",
      "dificultad": 3,
      "seccion": "Evaporación y condensación"
    }
  ]
}
```

---

## Anexo: `reglas-preguntas.md`

### Reglas para escribir preguntas

Un test sirve para aprender si cada fallo enseña algo. Para eso, la pregunta tiene que medir el concepto y no la habilidad de adivinar. Las opciones falsas tienen que ser errores que un alumno cometería de verdad.

#### Enunciados

- **Una sola idea por pregunta.** Si para responder hay que saber dos cosas, el fallo no dice cuál de las dos falta.
- **La pregunta se entiende sin leer las opciones.** Tapando las opciones, alguien que se sabe el tema debería poder decir la respuesta.
- **Lo importante, no lo anecdótico.** Se pregunta lo que el material trata como central: definiciones, causas, diferencias, pasos, cifras evaluables. Nada de detalles de relleno ("¿en qué párrafo…?").
- **Sin pistas de forma.** El enunciado no termina en "un"/"una"/"el"/"la" si solo una opción concuerda con el artículo. Sin palabras del enunciado que solo se repitan en la correcta.
- **Negativas solo cuando aporten.** Máximo el 10 % del test, con "NO" en mayúsculas. Una negativa sirve para comprobar que el alumno descarta bien, no para despistar.
- **Casos prácticos cortos.** Dos o tres frases con los datos justos para decidir. Si el caso trae datos que no se usan, es para entrenar a descartar, y la explicación lo dice.
- **Oposiciones y normativa:** se pregunta por la literalidad (plazos, cifras, órganos, número de artículo). Los distractores cambian una sola pieza de la norma: el plazo, el órgano o el requisito.

#### Distractores

Cada opción falsa tiene que responder a la pregunta "¿qué error concreto me haría elegir esto?". Si no hay respuesta, la opción es relleno y se cambia.

- **Del mismo tipo que la correcta.** Si la correcta es una cifra, las cuatro son cifras. Si es una consecuencia, las cuatro son consecuencias.
- **Longitud parecida.** Ninguna opción mide más del doble que otra, y la correcta no es la más larga en más del 30 % de las preguntas. Si la correcta necesita un matiz, los distractores también llevan el suyo.
- **Técnicas variadas.** Confundir con un concepto vecino, invertir causa y efecto, dato parcialmente cierto, generalizar de más, error de cálculo típico, cifra cercana, orden alterado, intercambio de atributos, función opuesta. Catálogo con ejemplos en `variedad.md`.
- **Prohibido** "todas las anteriores", "ninguna de las anteriores", "ambas son correctas" y equivalentes. Una opción así no mide nada concreto, y el validador la trata como error.
- **Nada inventado.** Los distractores pueden ser falsos para la pregunta, pero los conceptos que nombran salen del material: un concepto vecino real del tema, no un término que no aparece en él.
- **Absolutos repartidos.** "Siempre", "nunca", "todos" y "ninguno" no pueden aparecer solo en los distractores. Si la correcta es una afirmación matizada y las falsas son absolutas, el alumno acierta sin saber.

#### Explicaciones

- Una o dos frases. La primera dice por qué la correcta lo es. La segunda, por qué falla el distractor más tentador, nombrándolo.
- Cada explicación empieza distinto. Prohibidos los arranques fijos ("Esto es así porque…", "La respuesta correcta es…"). El validador avisa si más de dos explicaciones empiezan con las mismas tres palabras.
- Tono de compañero que explica bien: frases cortas, sin muletillas, sin emojis y sin cierres del tipo "¡Sigue así!". Lista completa en `tono.md`.
- La sección de origen va en `seccion`, no dentro de la explicación.

#### Errores típicos de los tests generados por IA

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

#### Pares de ejemplo (mala → buena)

Contenido genérico, solo para mostrar la técnica.

##### 1. La correcta se delata por la longitud y el artículo

**Mala:**
> El orgánulo donde se produce la mayor parte del ATP de la célula es una…
> A) ribosoma · B) mitocondria, que realiza la respiración celular aerobia · C) núcleo · D) aparato de Golgi

**Buena:**
> ¿En qué orgánulo se produce la mayor parte del ATP de la célula?
> A) En el ribosoma · B) En la mitocondria · C) En el cloroplasto · D) En el núcleo

Qué cambia: el enunciado ya no condiciona el género y las cuatro opciones miden lo mismo. El cloroplasto sustituye al aparato de Golgi porque es el error real: también produce ATP, pero en las células vegetales y para la fotosíntesis.

##### 2. Distractores de relleno

**Mala:**
> ¿Qué provoca la subida de los tipos de interés?
> A) Abarata los créditos · B) Encarece los créditos · C) Aumenta la población · D) Cambia el clima

**Buena:**
> Si el banco central sube los tipos de interés, ¿qué es lo más probable a corto plazo?
> A) Que los créditos se abaraten y suba el consumo · B) Que los créditos se encarezcan y baje el consumo · C) Que suba la inflación porque hay más dinero en circulación · D) Que bajen los precios de inmediato en todos los sectores

Qué cambia: C invierte causa y efecto, A es la confusión de sentido y D generaliza de más. Cada distractor es un error de alumno; en la versión mala, C y D no los elegiría nadie.

##### 3. Se responde copiando una palabra

**Mala:**
> ¿Cómo se llama el proceso por el que las plantas fabrican materia orgánica a partir de la luz?
> A) Respiración · B) Fotosíntesis, proceso que usa la luz · C) Transpiración · D) Fermentación

**Buena:**
> Una planta pasa una semana en total oscuridad con agua y CO₂ de sobra. ¿Qué proceso deja de hacer?
> A) La respiración celular · B) La fotosíntesis · C) La transpiración · D) La absorción de agua

Qué cambia: en la mala, "luz" aparece en el enunciado y solo en la correcta. La buena obliga a aplicar el concepto a un caso, y la respiración es un distractor tentador porque también intercambia gases.

---

## Anexo: `tono.md`

### Tono de enunciados y explicaciones

La referencia es el compañero que te pregunta el tema la víspera del examen y te corrige al momento. Va al grano, usa frases cortas y dice en qué te has equivocado. No adorna ni anima.

#### Muletillas prohibidas

Si aparece alguna, se reescribe la frase entera; no basta con cambiar el conector por un sinónimo.

##### En las explicaciones

- "Esto es así porque…", "La respuesta correcta es… porque…", "La opción correcta es…" como arranque fijo
- "Es importante destacar / señalar / recordar que…"
- "Cabe mencionar / destacar que…"
- "Es fundamental / crucial / esencial comprender…"
- "Juega / desempeña un papel fundamental / crucial / clave"
- "No solo… sino también…" como fórmula repetida
- "En resumen…", "En definitiva…", "En conclusión…"
- "Sin lugar a dudas…", "Dicho esto…"
- Cierres de ánimo: "¡Sigue así!", "¡Muy bien!", "¡No te preocupes!", "¡Ánimo!"
- Inglés: "It's important to note…", "Plays a crucial role", "In summary", "Great job!"

##### En los enunciados

- "¿Cuál de las siguientes afirmaciones es correcta?" como forma por defecto. Se pregunta por el concepto, no por "las afirmaciones".
- "Según el texto…" / "De acuerdo con lo estudiado…" en todas las preguntas. Solo cuando la respuesta dependa de la fuente concreta.
- "Señale la opción correcta", "Indique cuál…": fórmula de examen antiguo que no aporta nada.
- Preguntas que empiezan por un rodeo ("En el contexto de la hemostasia, en relación con…"). La pregunta empieza por lo que se pregunta.

#### Patrones

- Emojis, en cualquier sitio.
- Tríadas de adjetivos por inercia: "claro, conciso y eficaz".
- Guiones largos (—) para meter incisos en cada frase.
- Negrita dentro de los enunciados para señalar la clave. Solo se permite "NO" en mayúsculas en las negativas.
- Explicaciones con la misma longitud y el mismo ritmo, una detrás de otra.

#### Pares de ejemplo (mismo contenido)

**Explicación robótica:**
> La respuesta correcta es la B. Es importante destacar que la mitocondria desempeña un papel fundamental en la producción de energía celular. ¡Sigue así!

**Explicación humana:**
> La mitocondria fabrica casi todo el ATP. El cloroplasto también produce ATP, pero solo en células vegetales y para la fotosíntesis: por eso tienta.

Qué cambia: empieza por el dato y nombra el distractor tentador diciendo por qué engaña. Sin "papel fundamental" y sin ánimo final.

**Enunciado robótico:**
> En relación con los orgánulos celulares estudiados, señale cuál de las siguientes afirmaciones es correcta respecto a la producción de ATP.

**Enunciado humano:**
> ¿En qué orgánulo se produce la mayor parte del ATP de la célula?

Qué cambia: va directo a lo que se pregunta.

---

## Anexo: `variedad.md`

### Variedad: cómo evitar el test en molde

Un test en el que todas las preguntas tienen la misma forma se responde por reconocimiento de patrones, no por conocimiento. Este archivo da el repertorio para variar y los límites que mide `scripts/validar.py`.

#### Límites que mide el validador

| Qué | Límite | Categoría en el informe |
|---|---|---|
| Enunciados con las mismas 3 primeras palabras | máx. 2 | `inicio_enunciado` |
| Similitud de palabras entre dos enunciados (Jaccard) | ≤ 0,6 | `similitud` |
| Correcta más larga que todas las demás | ≤ 30 % de las preguntas | `longitud_correcta` |
| Opción más larga / más corta en una pregunta | ≤ 2 | `longitud_opciones` |
| Correcta en una misma letra | ≤ 35 % (o ⌈n/4⌉ si hay pocas) | `posicion` |
| Racha de correctas en la misma letra | máx. 2 seguidas | `posicion` |
| Todas las letras con la misma frecuencia (≥ 8 preguntas de opciones) | prohibido | `posicion` |
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

#### Formas de enunciado

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

#### Técnicas de distractor

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

#### Niveles cognitivos

Repartir las preguntas entre los seis niveles. Ninguno pasa del 40 %. Si hay que elegir, quitar preguntas de "recordar".

| Nivel (`nivel_cognitivo`) | Verbos asociados | Qué comprueba |
|---|---|---|
| `recordar` | nombrar, identificar, citar | Que el dato está en la memoria |
| `comprender` | explicar, justificar, interpretar | Que se sabe por qué |
| `distinguir` | diferenciar, comparar, clasificar | Que no se mezclan conceptos parecidos |
| `aplicar` | resolver, predecir, diagnosticar | Que se usa el concepto en un caso nuevo |
| `detectar_error` | corregir, revisar, encontrar el fallo | Que se reconoce una versión incorrecta |
| `ordenar` | secuenciar, relacionar, encadenar | Que se conoce el orden o la relación entre piezas |

#### Antes y después: cinco preguntas en molde

Contenido genérico (fotosíntesis), solo para mostrar el cambio.

##### En molde

1. ¿Cuál es el orgánulo donde ocurre la fotosíntesis? A) **El cloroplasto, orgánulo de la fotosíntesis** · B) Núcleo · C) Ribosoma · D) Vacuola
2. ¿Cuál es el gas que se libera en la fotosíntesis? A) **El oxígeno, que se libera a la atmósfera** · B) CO₂ · C) Nitrógeno · D) Metano
3. ¿Cuál es el pigmento que capta la luz? A) **La clorofila, pigmento verde que capta la luz** · B) Caroteno siempre · C) Melanina · D) Hemoglobina
4. ¿Cuál es la fuente de energía de la fotosíntesis? A) **La luz solar, fuente de energía** · B) El calor · C) El suelo · D) El agua
5. ¿Cuál es el producto principal de la fotosíntesis? A) **La glucosa, producto principal** · B) Proteínas · C) Grasas · D) Vitaminas

Fallos: las cinco empiezan por "¿Cuál es el/la…", la correcta siempre es la A y la más larga, y repite palabras del enunciado ("orgánulo", "libera", "capta la luz"). "Siempre" solo aparece en un distractor. Todas son de "recordar" y los distractores no corresponden a errores reales: nadie piensa que la fotosíntesis produzca metano.

##### Con variedad

1. **(situación, aplicar)** Una planta se deja una semana a oscuras con agua y CO₂ de sobra. ¿Qué deja de producir? A) Agua por transpiración · B) CO₂ por respiración · **C) Oxígeno por fotosíntesis** · D) Raíces nuevas
2. **(comparación, distinguir)** ¿Qué diferencia a la fase luminosa de la fase oscura? **A) La luminosa capta energía; la oscura fija el CO₂** · B) La luminosa fija el CO₂; la oscura capta energía · C) La luminosa ocurre de día; la oscura, solo de noche · D) La luminosa produce glucosa; la oscura, oxígeno
3. **(huecos, recordar)** El pigmento que capta la luz en los cloroplastos es la ___. → clorofila
4. **(causa-efecto, comprender)** ¿Por qué las hojas de muchas plantas se ven verdes? A) Porque absorben sobre todo la luz verde · **B) Porque la clorofila refleja la luz verde** · C) Porque la clorofila emite luz verde al trabajar · D) Porque las hojas contienen glucosa verde
5. **(V/F, detectar error)** "En la fotosíntesis la planta consume oxígeno y libera CO₂." → Falso (`inversion_causa_efecto`: es lo que ocurre en la respiración).

Qué cambia: cinco formas de enunciado y cinco niveles, con la correcta en posiciones distintas. Las opciones tienen longitudes parecidas y cada distractor corresponde a un error real. En la 2, B es un intercambio de atributos y C generaliza de más ("solo de noche"). En la 4, A es el error clásico de confundir absorber con reflejar.

---

## Anexo: `plantilla-test.html`

```html
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title><!--TITULO--></title>
<style>
/* Paleta: la rellena generar_html.py con los valores de --paleta
   (tabla PALETAS de ese script, contraste WCAG AA verificado). */
:root {
/*PALETA*/
}

* { box-sizing: border-box; }
body { margin: 0; background: var(--fondo); color: var(--texto); font: 17px/1.55 var(--fuente); }
main { max-width: 44rem; margin: 0 auto; padding: 1.6rem 1rem 3rem; }
h1 { font-size: 1.7rem; line-height: 1.2; margin: 0 0 .3rem; color: var(--def); }
.subtitulo { margin: 0 0 1.2rem; font-size: .95rem; }
button { font: inherit; color: inherit; cursor: pointer; }
:focus-visible { outline: 3px solid var(--def); outline-offset: 2px; }
[hidden] { display: none !important; }

/* Progreso */
.progreso { height: .55rem; border-radius: 99px; overflow: hidden;
            background: color-mix(in srgb, var(--def) 15%, var(--fondo)); }
.progreso .barra { height: 100%; width: 0; background: var(--def); transition: width .2s; }
.contador { margin: .4rem 0 1rem; font-size: .9rem; }

/* Pregunta */
.contexto { margin: 0 0 .8rem; padding: .7rem 1rem; border-left: 5px solid var(--clave);
            background: color-mix(in srgb, var(--clave) 10%, var(--fondo)); border-radius: 0 6px 6px 0; }
.contexto::before { content: "Caso práctico"; display: block; font-size: .75rem; font-weight: 700;
                    letter-spacing: .06em; text-transform: uppercase; color: var(--clave); }
#enunciado { font-size: 1.2rem; line-height: 1.4; margin: 0 0 1rem; }
.hueco { display: inline-block; min-width: 4.5rem; border-bottom: 2px solid var(--texto); }
.opciones { display: grid; gap: .55rem; margin: 0 0 1rem; padding: 0; list-style: none; }
.opcion { display: flex; gap: .7rem; align-items: flex-start; width: 100%; text-align: left;
          padding: .65rem .8rem; border-radius: 8px; background: var(--fondo);
          border: 2px solid color-mix(in srgb, var(--texto) 25%, var(--fondo)); }
.opcion:hover:not(:disabled) { border-color: var(--def); }
.opcion:disabled { cursor: default; }
.opcion .letra { flex: none; width: 1.7rem; height: 1.7rem; border-radius: 50%; text-align: center;
                 line-height: 1.7rem; font-weight: 700; background: var(--def); color: var(--fondo); }
.opcion .marca { margin-left: auto; font-weight: 700; font-size: .85rem; white-space: nowrap; }
.opcion.es-correcta { border-color: var(--ejemplo); background: color-mix(in srgb, var(--ejemplo) 10%, var(--fondo)); }
.opcion.es-fallo { border-color: var(--ojo); background: color-mix(in srgb, var(--ojo) 10%, var(--fondo)); }
.opcion.es-correcta .marca { color: var(--ejemplo); }
.opcion.es-fallo .marca { color: var(--ojo); }
.huecos { display: flex; flex-wrap: wrap; gap: .5rem; align-items: center; margin: 0 0 1rem; }
.huecos input { font: inherit; padding: .5rem .7rem; min-width: 14rem; border-radius: 8px; color: var(--texto);
                background: var(--fondo); border: 2px solid color-mix(in srgb, var(--texto) 35%, var(--fondo)); }

/* Feedback */
.feedback { margin: 0 0 1rem; padding: .7rem 1rem; border-left: 5px solid var(--c); border-radius: 0 6px 6px 0;
            background: color-mix(in srgb, var(--c) 10%, var(--fondo)); }
.feedback:empty { display: none; }
.feedback.acierto { --c: var(--ejemplo); }
.feedback.fallo { --c: var(--ojo); }
.feedback.blanco { --c: var(--clave); }
.feedback .veredicto { display: block; font-weight: 700; color: var(--c); }
.feedback .origen { display: block; margin-top: .3rem; font-size: .88rem; }
.feedback p { margin: .3rem 0 0; }

.acciones { display: flex; flex-wrap: wrap; gap: .6rem; }
.boton { padding: .55rem 1rem; border-radius: 8px; border: 2px solid var(--def); background: var(--fondo); color: var(--def); font-weight: 600; }
.boton.principal { background: var(--def); color: var(--fondo); }
.boton:disabled { opacity: .55; cursor: default; }
.ayuda { margin-top: 1.4rem; font-size: .85rem; }
kbd { font: .8rem/1 ui-monospace, Consolas, monospace; padding: .1rem .35rem; border-radius: 4px;
      border: 1px solid color-mix(in srgb, var(--texto) 35%, var(--fondo)); }

/* Resultado */
.nota { font-size: 2.6rem; font-weight: 700; color: var(--def); margin: .2rem 0; }
.recuento { display: flex; flex-wrap: wrap; gap: .4rem 1.2rem; margin: 0 0 1rem; padding: 0; list-style: none; }
table { width: 100%; margin: 1rem 0; border-collapse: collapse; font-size: .95rem; }
th, td { padding: .45rem .6rem; text-align: left; vertical-align: top;
         border: 1px solid color-mix(in srgb, var(--texto) 20%, var(--fondo)); }
thead th { background: color-mix(in srgb, var(--def) 10%, var(--fondo)); }
.repasa { padding: .7rem 1rem; border-left: 5px solid var(--ojo); border-radius: 0 6px 6px 0;
          background: color-mix(in srgb, var(--ojo) 10%, var(--fondo)); }
.repasa strong { color: var(--ojo); }

/* Versión papel: solo al imprimir */
.solo-papel { display: none; }
.papel-pregunta { margin: 0 0 1rem; break-inside: avoid; }
.papel-pregunta ol { margin: .3rem 0 0; padding-left: 1.6rem; list-style: upper-alpha; }
.papel-linea { display: inline-block; min-width: 10rem; border-bottom: 1px solid var(--texto); }
.soluciones { break-before: page; }
.soluciones li { margin-bottom: .5rem; }

@media print {
  @page { size: A4; margin: 1.8cm 1.6cm; }
  * { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  body { font-size: 11pt; }
  main { max-width: none; padding: 0; }
  .solo-pantalla { display: none !important; }
  .solo-papel { display: block; }
}
</style>
</head>
<body>
<main>
<header>
  <h1 id="titulo"><!--TITULO--></h1>
  <p class="subtitulo" id="subtitulo"></p>
</header>

<section id="pantalla-test" class="solo-pantalla" aria-label="Test">
  <div class="progreso" id="progreso" role="progressbar" aria-label="Progreso del test" aria-valuemin="0" aria-valuemax="1" aria-valuenow="0">
    <div class="barra" id="barra"></div>
  </div>
  <p class="contador" id="contador"></p>
  <p class="contexto" id="contexto" hidden></p>
  <h2 id="enunciado" tabindex="-1"></h2>
  <div id="respuestas"></div>
  <div class="feedback" id="feedback" role="status" aria-live="polite"></div>
  <div class="acciones">
    <button type="button" class="boton" id="btn-blanco">Dejar en blanco <kbd>B</kbd></button>
    <button type="button" class="boton principal" id="btn-siguiente" hidden>Siguiente <kbd>Enter</kbd></button>
  </div>
  <p class="ayuda">Teclado: <kbd>1</kbd>-<kbd>4</kbd> eligen opción, <kbd>V</kbd>/<kbd>F</kbd> en verdadero o falso,
    <kbd>Enter</kbd> comprueba un hueco o pasa a la siguiente, <kbd>B</kbd> deja en blanco.</p>
</section>

<section id="pantalla-final" class="solo-pantalla" aria-labelledby="titulo-final" hidden>
  <h2 id="titulo-final" tabindex="-1">Resultado</h2>
  <p class="nota" id="nota"></p>
  <ul class="recuento" id="recuento"></ul>
  <p id="nota-penalizacion"></p>
  <table>
    <thead><tr><th scope="col">Sección</th><th scope="col">Aciertos</th></tr></thead>
    <tbody id="por-seccion"></tbody>
  </table>
  <div class="repasa" id="repasa" hidden></div>
  <div class="acciones" style="margin-top:1rem">
    <button type="button" class="boton principal" id="btn-fallos">Repetir solo los fallos</button>
    <button type="button" class="boton" id="btn-todo">Repetir todo</button>
  </div>
</section>

<section id="version-papel" class="solo-papel" aria-hidden="true"></section>
</main>

<script type="application/json" id="datos-test">/*DATOS*/</script>
<script>
(function () {
  "use strict";
  var datos = JSON.parse(document.getElementById("datos-test").textContent);
  var meta = datos.meta;
  var todas = datos.preguntas;
  var PENAL = { "ninguna": 0, "1/3": 1 / 3, "1/4": 1 / 4 };
  var LETRAS = "ABCD";
  var $ = function (id) { return document.getElementById(id); };

  var lista = [], pos = 0, resultados = {}, respondida = false;

  function el(tag, clase, texto) {
    var n = document.createElement(tag);
    if (clase) n.className = clase;
    if (texto !== undefined) n.textContent = texto;
    return n;
  }
  function barajar(a) {
    a = a.slice();
    for (var i = a.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var t = a[i]; a[i] = a[j]; a[j] = t;
    }
    return a;
  }
  function normal(s) {
    return String(s).normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase()
      .replace(/[.,;:!?¡¿"'()]/g, " ").replace(/\s+/g, " ").trim();
  }
  function textoCorrecta(p) {
    if (p.tipo === "vf") return p.correcta ? "Verdadero" : "Falso";
    if (p.tipo === "huecos") return p.correcta[0];
    return p.opciones[p.correcta];
  }
  function ponerEnunciado(nodo, texto) {
    nodo.textContent = "";
    var partes = String(texto).split(/_{3,}/);
    partes.forEach(function (parte, i) {
      nodo.appendChild(document.createTextNode(parte));
      if (i < partes.length - 1) {
        var h = el("span", "hueco");
        h.setAttribute("aria-label", "hueco");
        nodo.appendChild(h);
      }
    });
  }

  // Orden de un intento: si la dificultad es progresiva, se baraja dentro de cada nivel.
  function ordenar(preguntas) {
    if (meta.dificultad !== "progresiva") return barajar(preguntas);
    var grupos = {};
    preguntas.forEach(function (p) { (grupos[p.dificultad] = grupos[p.dificultad] || []).push(p); });
    return Object.keys(grupos).sort().reduce(function (acc, k) { return acc.concat(barajar(grupos[k])); }, []);
  }

  function empezar(preguntas) {
    lista = ordenar(preguntas).map(function (p) {
      var orden = p.opciones ? barajar([0, 1, 2, 3]) : null;
      return { p: p, orden: orden };
    });
    pos = 0; resultados = {};
    $("pantalla-final").hidden = true;
    $("pantalla-test").hidden = false;
    $("progreso").setAttribute("aria-valuemax", String(lista.length));
    mostrar();
  }

  function mostrar() {
    var item = lista[pos], p = item.p;
    respondida = false;
    $("barra").style.width = (100 * pos / lista.length) + "%";
    $("progreso").setAttribute("aria-valuenow", String(pos));
    $("contador").textContent = "Pregunta " + (pos + 1) + " de " + lista.length;
    $("contexto").hidden = !p.contexto;
    $("contexto").textContent = p.contexto || "";
    ponerEnunciado($("enunciado"), p.enunciado);
    $("feedback").className = "feedback";
    $("feedback").textContent = "";
    $("btn-siguiente").hidden = true;
    $("btn-blanco").disabled = false;
    var zona = $("respuestas");
    zona.textContent = "";

    if (p.tipo === "huecos") {
      var caja = el("div", "huecos");
      var etiqueta = el("label", "", "Tu respuesta:");
      etiqueta.setAttribute("for", "campo-hueco");
      var campo = el("input");
      campo.id = "campo-hueco"; campo.type = "text"; campo.autocomplete = "off";
      var comprobar = el("button", "boton", "Comprobar");
      comprobar.type = "button"; comprobar.id = "btn-comprobar";
      comprobar.addEventListener("click", function () { responderHueco(campo.value); });
      campo.addEventListener("keydown", function (e) {
        if (e.key === "Enter") { e.preventDefault(); if (!respondida) responderHueco(campo.value); else siguiente(); }
      });
      caja.appendChild(etiqueta); caja.appendChild(campo); caja.appendChild(comprobar);
      zona.appendChild(caja);
    } else {
      var ul = el("ul", "opciones");
      ul.setAttribute("aria-labelledby", "enunciado");
      var textos = p.tipo === "vf" ? ["Verdadero", "Falso"] : item.orden.map(function (i) { return p.opciones[i]; });
      textos.forEach(function (t, k) {
        var li = el("li");
        var b = el("button", "opcion");
        b.type = "button";
        b.dataset.k = String(k);
        var tecla = p.tipo === "vf" ? (k === 0 ? "V" : "F") : LETRAS[k];
        b.appendChild(el("span", "letra", tecla));
        b.appendChild(el("span", "texto", t));
        b.appendChild(el("span", "marca", ""));
        b.setAttribute("aria-keyshortcuts", p.tipo === "vf" ? tecla : String(k + 1));
        b.addEventListener("click", function () { responderOpcion(k); });
        li.appendChild(b); ul.appendChild(li);
      });
      zona.appendChild(ul);
    }
    $("enunciado").focus();
  }

  function indiceCorrecto(item) {
    var p = item.p;
    if (p.tipo === "vf") return p.correcta ? 0 : 1;
    return item.orden.indexOf(p.correcta);
  }

  function responderOpcion(k) {
    if (respondida) return;
    var item = lista[pos];
    var ok = indiceCorrecto(item);
    marcarOpciones(ok, k);
    cerrar(k === ok ? "acierto" : "fallo");
  }
  function marcarOpciones(ok, elegida) {
    var botones = $("respuestas").querySelectorAll(".opcion");
    for (var i = 0; i < botones.length; i++) {
      botones[i].disabled = true;
      if (i === ok) {
        botones[i].classList.add("es-correcta");
        botones[i].querySelector(".marca").textContent = i === elegida ? "Tu respuesta: correcta" : "Correcta";
      } else if (i === elegida) {
        botones[i].classList.add("es-fallo");
        botones[i].querySelector(".marca").textContent = "Tu respuesta";
      }
    }
  }
  function responderHueco(valor) {
    if (respondida) return;
    if (!String(valor).trim()) { $("campo-hueco").focus(); return; }
    var p = lista[pos].p;
    var acierto = p.correcta.some(function (r) { return normal(r) === normal(valor); });
    $("campo-hueco").disabled = true;
    $("btn-comprobar").disabled = true;
    cerrar(acierto ? "acierto" : "fallo");
  }
  function blanco() {
    if (respondida) return;
    var item = lista[pos];
    if (item.p.tipo === "huecos") {
      $("campo-hueco").disabled = true; $("btn-comprobar").disabled = true;
    } else {
      marcarOpciones(indiceCorrecto(item), -1);
    }
    cerrar("blanco");
  }

  function cerrar(estado) {
    respondida = true;
    var p = lista[pos].p;
    resultados[p.id] = estado;
    var fb = $("feedback");
    fb.className = "feedback " + estado;
    fb.textContent = "";
    var veredicto = { acierto: "Correcto.", fallo: "Incorrecto.", blanco: "En blanco." }[estado];
    fb.appendChild(el("span", "veredicto", veredicto));
    if (estado !== "acierto") fb.appendChild(el("p", "", "Respuesta correcta: " + textoCorrecta(p)));
    fb.appendChild(el("p", "", p.explicacion));
    fb.appendChild(el("span", "origen", "Sección: " + p.seccion));
    $("btn-blanco").disabled = true;
    $("btn-siguiente").hidden = false;
    $("btn-siguiente").focus();
  }

  function siguiente() {
    if (!respondida) return;
    pos++;
    if (pos < lista.length) mostrar(); else final();
  }

  function formatoNota(n) {
    return (Math.round(n * 100) / 100).toLocaleString("es-ES", { maximumFractionDigits: 2 });
  }

  function final() {
    $("pantalla-test").hidden = true;
    $("pantalla-final").hidden = false;
    $("barra").style.width = "100%";
    var n = lista.length, cuenta = { acierto: 0, fallo: 0, blanco: 0 };
    var secciones = {}, ordenSecciones = [];
    lista.forEach(function (item) {
      var p = item.p, r = resultados[p.id];
      cuenta[r]++;
      if (!secciones[p.seccion]) { secciones[p.seccion] = { ok: 0, total: 0 }; ordenSecciones.push(p.seccion); }
      secciones[p.seccion].total++;
      if (r === "acierto") secciones[p.seccion].ok++;
    });
    var factor = PENAL[meta.penalizacion] || 0;
    var nota = Math.max(0, (cuenta.acierto - factor * cuenta.fallo) / n * 10);
    $("nota").textContent = formatoNota(nota) + " / 10";
    var rec = $("recuento"); rec.textContent = "";
    rec.appendChild(el("li", "", "Aciertos: " + cuenta.acierto));
    rec.appendChild(el("li", "", "Fallos: " + cuenta.fallo));
    rec.appendChild(el("li", "", "En blanco: " + cuenta.blanco));
    $("nota-penalizacion").textContent = factor
      ? "Cada fallo resta " + meta.penalizacion + " de acierto; las preguntas en blanco no restan."
      : "Los fallos no restan.";
    var cuerpo = $("por-seccion"); cuerpo.textContent = "";
    var flojas = [];
    ordenSecciones.forEach(function (s) {
      var tr = el("tr");
      tr.appendChild(el("td", "", s));
      tr.appendChild(el("td", "", secciones[s].ok + " de " + secciones[s].total));
      cuerpo.appendChild(tr);
      if (secciones[s].ok < secciones[s].total) flojas.push(s);
    });
    var repasa = $("repasa"); repasa.textContent = "";
    repasa.hidden = !flojas.length;
    if (flojas.length) {
      repasa.appendChild(el("strong", "", "Repasa: "));
      repasa.appendChild(document.createTextNode(flojas.join(", ") + "."));
    }
    var hayFallos = cuenta.fallo + cuenta.blanco > 0;
    $("btn-fallos").disabled = !hayFallos;
    $("btn-fallos").title = hayFallos ? "Incluye las que dejaste en blanco" : "No hay fallos que repetir";
    $("titulo-final").focus();
  }

  function repetirFallos() {
    var fallidas = lista.map(function (i) { return i.p; }).filter(function (p) { return resultados[p.id] !== "acierto"; });
    if (fallidas.length) empezar(fallidas);
  }

  // Versión en papel (en el orden del archivo, con hoja de soluciones aparte)
  function papel() {
    var cont = $("version-papel");
    var preg = el("ol");
    var sol = el("ol");
    todas.forEach(function (p) {
      var li = el("li", "papel-pregunta");
      if (p.contexto) li.appendChild(el("p", "", "Caso: " + p.contexto));
      var e = el("p");
      String(p.enunciado).split(/_{3,}/).forEach(function (parte, i, arr) {
        e.appendChild(document.createTextNode(parte));
        if (i < arr.length - 1) e.appendChild(el("span", "papel-linea", " "));
      });
      li.appendChild(e);
      if (p.opciones) {
        var ops = el("ol");
        p.opciones.forEach(function (o) { ops.appendChild(el("li", "", o)); });
        li.appendChild(ops);
      } else if (p.tipo === "vf") {
        li.appendChild(el("p", "", "(  ) Verdadero     (  ) Falso"));
      }
      preg.appendChild(li);
      var r = p.tipo === "vf" ? (p.correcta ? "Verdadero" : "Falso")
        : p.tipo === "huecos" ? p.correcta.join(" / ")
        : LETRAS[p.correcta] + ") " + p.opciones[p.correcta];
      var s = el("li");
      s.appendChild(el("strong", "", r + ". "));
      s.appendChild(document.createTextNode(p.explicacion + " (Sección: " + p.seccion + ")"));
      sol.appendChild(s);
    });
    cont.appendChild(preg);
    var hoja = el("div", "soluciones");
    hoja.appendChild(el("h2", "", "Soluciones"));
    hoja.appendChild(sol);
    cont.appendChild(hoja);
  }

  document.addEventListener("keydown", function (e) {
    if (e.ctrlKey || e.metaKey || e.altKey) return;
    if ($("pantalla-test").hidden) return;
    var t = e.target;
    if (t && t.tagName === "INPUT") return;              // el campo de huecos gestiona su Enter
    if (e.key === "Enter") {
      if (t && t.tagName === "BUTTON") return;           // el botón enfocado ya se activa solo
      if (respondida) { e.preventDefault(); siguiente(); }
      return;
    }
    if (respondida) return;
    var p = lista[pos].p, tecla = e.key.toLowerCase();
    if (tecla === "b") { e.preventDefault(); blanco(); return; }
    if (p.tipo === "vf") {
      if (tecla === "v") responderOpcion(0);
      else if (tecla === "f") responderOpcion(1);
    } else if (p.opciones && /^[1-4]$/.test(tecla)) {
      responderOpcion(Number(tecla) - 1);
    }
  });

  $("btn-siguiente").addEventListener("click", siguiente);
  $("btn-blanco").addEventListener("click", blanco);
  $("btn-fallos").addEventListener("click", repetirFallos);
  $("btn-todo").addEventListener("click", function () { empezar(todas); });

  var penal = { "ninguna": "sin penalización", "1/3": "cada fallo resta 1/3", "1/4": "cada fallo resta 1/4" };
  $("subtitulo").textContent = meta.asignatura + " · " + todas.length + " preguntas · " + (penal[meta.penalizacion] || "");
  papel();
  empezar(todas);
})();
</script>
</body>
</html>
```
