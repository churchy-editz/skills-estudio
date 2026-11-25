# Tono de los comentarios

La referencia es un profesor con tiempo que corrige a mano: señala el sitio exacto, dice qué falla y por qué, y deja al alumno el arreglo. Es directo y respetuoso. No hay halagos vacíos ni sermones, y tampoco se ablanda con fórmulas de cortesía.

`scripts/validar_correccion.py` lee este archivo. Las frases entre `comillas invertidas` de las secciones «Prohibidas» se buscan en todos los textos de la corrección (comentarios, puntos fuertes, prioridades y justificaciones). Un `…` dentro de la frase significa «cualquier cosa en medio».

## Cómo es un buen comentario

- **Señala el sitio.** Cita literal del fragmento y su ubicación. «La discusión es floja» no ayuda; «el segundo párrafo de la discusión repite los datos de la Tabla 2 sin interpretarlos» sí.
- **Dice qué falla en una frase.** Sin preámbulo: «La pendiente del texto (0,45) no es la de la Figura 1 (0,54)».
- **Explica por qué importa.** Con lo que pasa si no se arregla: «quien lea el informe no puede saber cuál usaste para calcular las concentraciones».
- **Da el arreglo, no el texto.** «Sustituye el valor y recalcula las muestras A-C con el correcto.» Si hace falta un ejemplo, 1-2 frases, y solo para mostrar la forma.
- **Cada comentario empieza distinto.** Si tres comentarios empiezan por «Falta», se reescriben dos.
- **Las dudas se dicen como dudas.** Lo que el asistente no puede comprobar se marca «verificar con la bibliografía» o «no he podido comprobarlo porque…». Nunca se corrige como si fuera seguro.

## Puntos fuertes

Concretos y comprobables, como los comentarios. «La Tabla 2 da cada absorbancia con su desviación estándar y el número de réplicas» es un punto fuerte. «Buen trabajo en general» no lo es: no dice qué conviene mantener.

## Prohibidas en comentarios · ES

| Fórmula | Qué hacer |
|---|---|
| `buen trabajo` / `excelente trabajo` / `gran trabajo` | decir qué está bien en concreto, o nada |
| `en general, el trabajo` / `en líneas generales` | ir al punto concreto |
| `sería conveniente` / `sería recomendable` / `sería interesante` | decir qué hacer: «añade», «cita», «quita» |
| `considera la posibilidad de` / `podrías considerar` | instrucción directa |
| `te animo a` / `te recomiendo encarecidamente` | instrucción directa |
| `es importante destacar` / `es importante señalar` / `es importante tener en cuenta` | eliminar y dar el dato |
| `cabe mencionar` / `cabe destacar` / `cabe señalar` | eliminar |
| `juega un papel crucial` / `juega un papel fundamental` / `desempeña un papel` | decir qué hace |
| `no solo… sino también` | dos frases, o «y» |
| `en resumen` / `en conclusión` / `en definitiva` | eliminar |
| `sin lugar a dudas` / `sin duda alguna` | eliminar o dar la prueba |
| `de manera significativa` / `de forma significativa` | dar la magnitud o el sitio |
| `un aspecto clave` / `aspectos clave` | nombrar el aspecto |
| `sigue así` / `vas por buen camino` / `ánimo` | eliminar |
| `mejorar la calidad del trabajo` / `enriquecer el trabajo` | decir qué cambia |
| `aportar valor` / `valor añadido` | decir qué aporta |
| `de cara al futuro` | eliminar |
| `espero que estos comentarios` / `espero que te sea útil` | eliminar |

## Prohibidas en comentarios · EN

| Formula | Instead |
|---|---|
| `great job` / `good job` / `excellent work` / `well done` | name what works, or nothing |
| `overall, the` / `in general, the` | go to the point |
| `it would be beneficial` / `it might be worth` / `you may want to consider` | direct instruction |
| `consider adding` / `consider revising` | «add», «revise» |
| `it's important to note` / `it is important to note` / `it's worth noting` | remove and give the fact |
| `plays a crucial role` / `plays a pivotal role` / `plays a vital role` | say what it does |
| `in conclusion` / `in summary` / `to sum up` | remove |
| `delve into` / `dive into` | «look at», «explain» |
| `enhance the quality` / `strengthen your work` | say what changes |
| `keep up the good work` / `i hope this helps` | remove |

## Euskera

Mismas reglas de forma: sitio exacto, qué falla, por qué, cómo se arregla y arranques distintos. El script no tiene lista de fórmulas en euskera; las equivalentes («lan bikaina», «kontuan hartu beharko litzateke» en cada comentario…) se revisan a mano.

## Variedad entre comentarios

- Como mucho 2 comentarios empiezan con las mismas 2 palabras en «qué falla» o en «cómo arreglarlo». El script avisa a partir de 3.
- Alternar formas de dar el arreglo: instrucción («Añade la unidad en la cabecera»), condición («Si la dilución fue 1:10, el resultado es…»), pregunta que obliga a decidir («¿Qué volumen final usaste: 10 o 20 mL?»), referencia a otra parte del trabajo («Haz como en la Tabla 1, que sí la tiene»).
- Los errores menores del mismo tipo van en un solo comentario con el número de casos y uno o dos ejemplos: «hay 9 cifras pegadas a su unidad (595nm, 10mL…)».

## Pares de ejemplo

**Mal:**
> Sería conveniente revisar la sección de resultados, ya que es importante destacar que los datos juegan un papel crucial en el informe. ¡Buen trabajo en general!

**Bien:**
> «R² = 0,9987» (Resultados, párr. 2): la Figura 1 da 0,987 y el recálculo con los datos de la Tabla 1 da 0,9871. Como el R² justifica que la recta sirve para interpolar, un valor inflado hace parecer el ajuste mejor de lo que es. Copia el de la figura.

**Mal:**
> Considera la posibilidad de justificar la elección de la base de datos.

**Bien:**
> «Se eligió MongoDB como base de datos» (Diseño): no se dice por qué. Las reservas, los usuarios y los laboratorios están relacionados entre sí, que es justo el caso donde una base relacional suele encajar mejor. Explica qué ganabas con MongoDB (esquema flexible, experiencia previa, requisito de la asignatura) o cambia la decisión.
