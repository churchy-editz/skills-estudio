# Rúbricas por defecto

Se usan cuando el usuario no da la rúbrica de su asignatura. Si la da, manda la suya: sus criterios, sus pesos y su escala, aunque falte alguno de los de aquí. Lo que la rúbrica del usuario no cubra (por ejemplo, las unidades) se comenta igual, con el criterio más cercano.

Cada criterio lleva un `id` (C1, C2…) que los comentarios citan en su campo `criterio`. Los pesos suman 100. La nota global es la media ponderada y la calcula `validar_correccion.py`.

## Bandas de nota de cada criterio

| Nota | Qué significa |
|---|---|
| 9-10 | Nada que corregir o solo detalles menores |
| 7-8,9 | Cumple, con fallos importantes aislados o varios menores |
| 5-6,9 | Cumple lo básico, con fallos importantes repetidos o un crítico que no invalida el resto |
| 3-4,9 | Fallos críticos que afectan al criterio entero (cálculo central mal, sección clave que falta) |
| 0-2,9 | No está o no se puede evaluar |

**Exigencia.** Con «como un profesor exigente» (por defecto), cada fallo importante baja al menos 1 punto el criterio y cada crítico lo deja en 6,9 como máximo. Con «orientativa», los menores no restan y el foco está en lo que más cambia la nota. En los dos casos se dice cuál se ha usado.

## Informe de laboratorio (`laboratorio`)

| id | Criterio | Peso | Qué se mira |
|---|---|---|---|
| C1 | Estructura y presentación | 10 | Secciones completas y en orden; figuras y tablas numeradas, con leyenda y citadas |
| C2 | Introducción y objetivos | 10 | Fundamento del método con fuentes; objetivos concretos y evaluables |
| C3 | Materiales y métodos | 15 | Reproducible: concentraciones, volúmenes, tiempos, equipos; cálculos de preparación correctos |
| C4 | Resultados | 25 | Datos completos, cálculos correctos, unidades y cifras significativas, figuras y tablas coherentes con el texto |
| C5 | Discusión | 20 | Interpreta los resultados, compara con valores de referencia, analiza fuentes de error con criterio |
| C6 | Conclusiones | 10 | Responden a los objetivos y solo afirman lo que muestran los resultados |
| C7 | Citas y bibliografía | 5 | Toda cita tiene entrada y viceversa; formato consistente |
| C8 | Redacción | 5 | Clara, impersonal, precisa; sin ambigüedades |

## Memoria de prácticas o informe técnico (`tecnico`)

| id | Criterio | Peso | Qué se mira |
|---|---|---|---|
| C1 | Estructura y presentación | 10 | Secciones esperadas; diagramas, tablas y código numerados y referenciados |
| C2 | Objetivos y análisis | 15 | Objetivos medibles; requisitos claros y trazables a los objetivos |
| C3 | Diseño | 20 | Arquitectura y modelo explicados; cada decisión importante justificada frente a alternativas |
| C4 | Implementación | 15 | Describe lo que no es obvio (algoritmos, concurrencia, seguridad); terminología correcta |
| C5 | Pruebas y resultados | 20 | Qué se probó, cómo y con qué resultado (cifras, casos superados, cobertura); cada objetivo evaluado |
| C6 | Conclusiones | 10 | Cumplimiento de cada objetivo con evidencia; limitaciones honestas |
| C7 | Redacción y fuentes | 10 | Clara y precisa; fuentes citadas; figuras legibles |

## TFG o TFM (`tfg`)

| id | Criterio | Peso | Qué se mira |
|---|---|---|---|
| C1 | Estructura y presentación | 5 | Secciones completas; índice, numeración, figuras y tablas |
| C2 | Resumen e introducción | 10 | Resumen autosuficiente; contexto y motivación con fuentes |
| C3 | Objetivos | 10 | Concretos, medibles, alcanzables; general y específicos |
| C4 | Metodología o diseño | 15 | Reproducible o justificado; alternativas consideradas |
| C5 | Desarrollo y resultados | 25 | Completos, correctos y presentados con rigor |
| C6 | Discusión y conclusiones | 15 | Interpretación, comparación con la literatura, cumplimiento de objetivos, limitaciones |
| C7 | Bibliografía | 10 | Suficiente, pertinente, actual y bien citada |
| C8 | Redacción | 10 | Registro académico, claridad, corrección |

## Ensayo o trabajo teórico (`ensayo`)

| id | Criterio | Peso | Qué se mira |
|---|---|---|---|
| C1 | Tesis y planteamiento | 20 | Pregunta o tesis explícita al principio; alcance definido |
| C2 | Argumentación | 30 | Cada argumento apoyado en pruebas o fuentes; contraargumentos tratados; sin saltos lógicos |
| C3 | Uso de fuentes | 15 | Fuentes pertinentes y fiables, citadas; distingue lo propio de lo ajeno |
| C4 | Estructura | 10 | Progresión clara; cada párrafo con una función |
| C5 | Conclusión | 10 | Responde a la tesis; no introduce ideas nuevas sin apoyo |
| C6 | Redacción | 15 | Registro, claridad, corrección |

## Trabajo bibliográfico o revisión (`bibliografico`)

| id | Criterio | Peso | Qué se mira |
|---|---|---|---|
| C1 | Planteamiento y alcance | 10 | Pregunta de revisión y límites claros |
| C2 | Búsqueda y método | 15 | Bases de datos, términos, criterios de inclusión y exclusión |
| C3 | Selección y calidad de fuentes | 15 | Fuentes primarias, recientes y pertinentes |
| C4 | Síntesis crítica | 25 | Compara y relaciona fuentes, no las resume una tras otra; señala contradicciones y huecos |
| C5 | Estructura | 10 | Organizada por temas o preguntas, no por autor |
| C6 | Conclusiones | 10 | Responden a la pregunta; estado de la cuestión y lo que falta por saber |
| C7 | Citas y bibliografía | 10 | Toda cita con entrada; formato consistente |
| C8 | Redacción | 5 | Clara y precisa |
