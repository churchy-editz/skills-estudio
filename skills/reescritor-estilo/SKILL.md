---
name: reescritor-estilo
description: >-
  Reescribe textos (pegados, DOCX, PDF o Markdown) para que suenen naturales y
  escritos por una persona con criterio: ritmo variado, sin muletillas ni fórmulas
  de relleno y con el registro adecuado (académico, profesional, cercano o redes).
  Puede imitar la voz del usuario a partir de textos suyos. Conserva todas las
  ideas, cifras, fechas, nombres, citas y referencias, y mide naturalidad y
  fidelidad con un script. Usar cuando el usuario diga "haz que esto suene más
  natural", "reescribe este texto", "que no suene a IA", "humaniza este texto",
  "mejora la redacción", "ponlo en un tono más cercano", "más profesional", "más
  académico", "make this sound more natural" o "rewrite this in my style", o pida
  mejorar el estilo o la naturalidad de un texto.
license: MIT
---

# Reescritor de estilo

El asistente reescribe un texto para que suene escrito por una persona concreta: natural, variado y adecuado a su registro. Dice lo mismo, con todos sus datos.

El riesgo principal es la repetición. Una reescritura que cambia unas muletillas por otras, o que aplica siempre los mismos trucos, sigue sonando a plantilla. Por eso la variedad se exige al redactar y se mide después con `scripts/analizar.py`.

## 1. Entrada

- Texto pegado, DOCX, PDF o Markdown. Se lee entero antes de nada.
- DOCX: `python scripts/docx_io.py extraer entrada.docx original.md`. Los títulos salen como `#`, `##`… y se conservan al volver a escribir.
- PDF: el asistente extrae el texto y lo guarda en `original.md`. Lo que no se pueda leer con seguridad no se reescribe: se avisa.
- Opcional: de 1 a 3 textos del propio usuario como muestra de su voz.

## 2. Detectar antes de preguntar

Antes de preguntar nada, el asistente deduce:
- **Tipo:** académico, profesional, email, redes/blog, narrativo o técnico.
- **Idioma.** El análisis admite español e inglés.
- **Registro actual:** formal, neutro o cercano, y si es impersonal o en primera persona.

## 3. Una sola pregunta

Se hace UNA pregunta y se omite lo que el usuario ya haya dicho:

> Lo veo como [tipo detectado], registro [X]. ¿Cómo lo quieres? (responde "ok" para el defecto)
> - Intensidad: ligera (solo quitar tics, misma estructura) / media (reescribir frases, mismo orden de ideas) / profunda (reorganizar libremente, mismas ideas) [defecto: media]
> - Registro: mantener / más cercano / más profesional / más académico [defecto: mantener]
> - ¿Tienes algún texto tuyo para imitar tu voz? (opcional)

Si responde "ok" o no responde a algo, se usa el defecto.

## 4. Voz del usuario

Solo si da muestras. Se extrae un perfil según `references/voz.md`:
- longitud media de frase y cuánto varía;
- vocabulario recurrente;
- conectores que usa y conectores que NO usa;
- primera persona, puntuación, nivel de formalidad y rasgos propios.

El perfil se muestra en 3-4 líneas antes del texto y se aplica a toda la reescritura. No se copian frases de las muestras.

Si el usuario da una muestra, **su voz pesa más que el registro del original**. Con registro "mantener" se aplica de la voz:
- **Persona gramatical.** Si escribe en primera persona y el tipo de texto lo admite (opinión, ensayo, email, post), el texto pasa a primera persona. Lo que el original atribuye a otros sigue atribuido a ellos: "los expertos señalan" no se convierte en "yo creo".
- Longitud de frase, nexos, vocabulario y rasgos propios.

Solo se mantiene impersonal si el tipo lo exige (académico formal, informe técnico), y se avisa en la línea del perfil: "Mantengo impersonal porque es un texto académico; si lo quieres en primera persona, dímelo".

Si el usuario pide un registro distinto ("más académico"), manda ese registro en formalidad y vocabulario, y el perfil ajusta el resto (ritmo, nexos, puntuación). Los errores de la muestra (tildes, comas que faltan) no se imitan.

## 5. Fidelidad (regla dura)

- No se añaden ideas, datos, ejemplos ni opiniones que no estén en el original.
- No se quita ninguna idea. En intensidad profunda se reordenan, pero siguen todas.
- Se conservan EXACTOS las cifras, fechas, nombres propios, términos técnicos, citas textuales y referencias bibliográficas.
- Académico: se mantiene el formato de cita (APA, Vancouver, etc.) tal como venía.
- Si una frase del original es ambigua, se conserva la ambigüedad o se pregunta. No se decide por el autor.

## 6. Proceso

1. Reescribir con la intensidad y el registro elegidos.
2. Guardar el original y el reescrito como texto y ejecutar `python scripts/analizar.py original.md reescrito.md`. Añadir `--idioma es|en` si el texto mezcla idiomas.
3. Corregir lo que marque. Los errores de fidelidad se corrigen siempre. Los avisos tienen un tope de 3 rondas. Si sigue alguno, se entrega diciendo cuál queda y por qué. Por ejemplo: "dos tríadas son la enumeración real de tres requisitos de la norma".

El objetivo es "Fidelidad: OK" y "Naturalidad: 10/10". Un aviso puede ser legítimo: un texto técnico corto puede tener un ritmo bastante regular. Se puede aceptar, pero hay que decirlo en la entrega.

## 7. Antirrepetición

Detalle en `references/patrones-ia.md` y `references/variedad.md`.
- **Muletillas prohibidas (ES/EN):** la lista completa está en `patrones-ia.md`. Por ejemplo: "es importante destacar", "cabe mencionar", "en el mundo actual", "en resumen", "además" como comodín, "no solo… sino también", "juega un papel crucial", "sumergirse", "un viaje", "delve", "tapestry", "it's worth noting", "in today's fast-paced world".
- **Frases hechas y tópicos de ensayo:** "luces y sombras", "herramienta valiosa", "no se puede pasar por alto", "lo mejor de ambos mundos", "una nueva realidad", "arma de doble filo", "muchos expertos", "double-edged sword", "best of both worlds"… Son correctas, pero valen para cualquier tema. Lista completa en `patrones-ia.md`. Pesan en la nota tanto como las muletillas.
- **Cierre:** el cierre aporta algo concreto (una consecuencia, un matiz, una postura) o simplemente termina con la última idea; nunca resume. Tampoco termina apelando a "los expertos", "el futuro" o "la opción más equilibrada", ni mete una tríada en el último párrafo. `analizar.py` avisa de las tres cosas.
- **Estructuras:** tríadas sistemáticas ("rápido, eficiente y seguro"), frase-resumen al final de cada párrafo, párrafos todos de la misma longitud, varios párrafos que empiezan igual, abuso de guiones largos, preguntas retóricas como transición y cierres motivacionales.
- **Ritmo:** frases cortas y largas alternadas de verdad, con variación medible. No todas de 15-25 palabras.
- **Sin sustituto fijo:** si se quita "Además", no se pone "Asimismo" en todas partes. Muchas veces la mejor transición es ninguna.
- **Entre versiones:** si el usuario pide otra versión, cambia el enfoque (orden, arranque, ritmo), no solo los sinónimos. La nueva versión no puede empezar como la anterior.

## 8. Registro

Detalle en `references/registros.md`. Cada registro tiene sus propios tics.
- **Académico:** impersonal y preciso. Sin coloquialismos, pero tampoco pomposo.
- **Profesional:** directo, con verbos de acción y frases cortas.
- **Cercano:** segunda persona, frases cortas y contracciones naturales del idioma.
- **Redes:** gancho en la primera línea y párrafos breves.

## 9. Salida

- El texto reescrito tal cual, listo para copiar, sin comentarios intercalados.
- Si la entrada era un archivo, se devuelve en el mismo formato. Para DOCX: `python scripts/docx_io.py escribir original.docx reescrito.md salida.docx`, que conserva los estilos de título y de párrafo. PDF se devuelve como DOCX o Markdown, a elección del usuario.
- Debajo, como mucho 3 líneas: los cambios principales y el resultado de `analizar.py` (naturalidad y fidelidad).
- Una línea final ofrece otra versión con otro enfoque, ajustar el registro o ver los cambios marcados.

Para ver los cambios marcados, `--marcar marcado.md` escribe el original con los patrones detectados entre ⟦ ⟧.

## 10. Autorrevisión

Antes de entregar:
1. ¿Se ha perdido o añadido alguna idea? Comprobarlo párrafo a párrafo con el original.
2. ¿Están intactos los datos, aunque el script no los vea? Por ejemplo, términos técnicos en minúscula.
3. Leído en voz alta, ¿suena a una persona que sabe del tema?
4. ¿El último párrafo dice algo nuevo o termina en la última idea? Si repasa lo dicho o se apoya en "los expertos", se reescribe aunque el script no avise.
5. ¿Se nota algún truco repetido? Por ejemplo, todas las frases cortas al final del párrafo, o el mismo tipo de arranque.

## Ejemplos

En `examples/`, textos originales inventados para la skill:
- Un párrafo académico con citas APA ficticias, un email profesional y un post de LinkedIn. Cada uno tiene el original con los tics marcados, la reescritura en intensidad media y el informe de `analizar.py`.
- Una muestra de voz: dos textos de un usuario ficticio y un texto reescrito con su perfil.
