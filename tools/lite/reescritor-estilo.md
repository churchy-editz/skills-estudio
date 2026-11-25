<!-- huella-skill: ce36f02640b2 -->
## Flujo

1. Lee el texto entero (pegado, DOCX, PDF o Markdown). Lo que no se pueda leer con seguridad no se reescribe: se avisa.
2. Deduce, sin preguntar, el tipo (académico, profesional, email, redes/blog, narrativo, técnico), el idioma y el registro actual.
3. Haz UNA sola pregunta y omite lo que el usuario ya haya dicho:
   > Lo veo como [tipo], registro [X]. ¿Cómo lo quieres? (responde "ok" para el defecto)
   > - Intensidad: ligera (solo quitar tics) / media (reescribir frases, mismo orden) / profunda (reorganizar, mismas ideas) [defecto: media]
   > - Registro: mantener / más cercano / más profesional / más académico [defecto: mantener]
   > - ¿Tienes algún texto tuyo para imitar tu voz? (opcional)
4. Si hay muestras del usuario (1-3), extrae su perfil de voz y muéstralo en 3-4 líneas antes del texto:
   - longitud de frase y cuánto varía;
   - vocabulario y conectores que usa y que NO usa;
   - persona gramatical, puntuación, formalidad y rasgos propios.
   Su voz pesa más que el registro del original, persona gramatical incluida. Lo atribuido a otros sigue atribuido a ellos. Se mantiene impersonal solo si el tipo lo exige, y se dice. No copies frases de las muestras ni sus erratas.
5. Reescribe, revisa con las comprobaciones de abajo (hasta 3 rondas) y entrega.

## Fidelidad (regla dura)

- No añadas ideas, datos, ejemplos ni opiniones. No quites ninguna idea; en intensidad profunda se reordenan, pero siguen todas.
- Conserva EXACTOS cifras, fechas, nombres propios, términos técnicos, citas textuales y referencias bibliográficas, con su formato de cita (APA, etc.).
- Si una frase es ambigua, conserva la ambigüedad o pregunta.

## Antirrepetición

- Fuera muletillas y conectores comodín: "es importante destacar", "cabe mencionar", "en el mundo actual", "en resumen", "además" en cada párrafo, "no solo… sino también", "juega un papel crucial", "sumergirse", "un viaje", "delve", "it's worth noting". La lista completa está en `patrones-ia.md` (portable completo).
- Fuera frases hechas de ensayo que valen para cualquier tema: "luces y sombras", "arma de doble filo", "herramienta valiosa", "una nueva realidad", "muchos expertos".
- El cierre aporta algo concreto o termina con la última idea. Nunca resume, ni apela a "los expertos", "el futuro" o "el equilibrio", ni lleva una tríada.
- Nada de tríadas sistemáticas, frase-resumen al final de cada párrafo, párrafos iguales, arranques repetidos, guiones largos para cada inciso, preguntas retóricas como transición ni cierres motivacionales.
- No sustituyas una muletilla por otra fija: muchas veces la mejor transición es ninguna.
- Si piden otra versión, cambia el enfoque (orden, arranque, ritmo), no solo los sinónimos.

## Registro

Académico: impersonal y preciso, sin pomposidad. Profesional: lo importante en la primera frase, verbos de acción, frases cortas. Cercano: segunda persona y frases cortas, sin entusiasmo impostado. Redes: gancho con un hecho en la primera línea y párrafos breves, sin emojis de viñeta ni moraleja.

## Comprobaciones (a mano si no puedes ejecutar el script)

- Fidelidad: repasa una por una las cifras, fechas, nombres, citas y referencias del original en la reescritura.
- Ritmo: frases de menos de 8 palabras junto a alguna de más de 25; no todas entre 15 y 25.
- Como mucho 2 frases, y 2 párrafos, empiezan por la misma palabra.
- Ningún conector más de 2 veces por cada 300 palabras. Como mucho 1 tríada por cada 200 palabras.
- Párrafos de longitudes claramente distintas. Como mucho 1 guion largo y 1 exclamación por cada 100 palabras.
- Leído en voz alta, ¿suena a una persona que sabe del tema? ¿Se nota algún truco repetido?

## Salida

El texto reescrito tal cual, listo para copiar. Debajo, como mucho 3 líneas: cambios principales y resultado de la revisión ("Fidelidad: OK; queda una tríada que es una enumeración real"). Si la entrada era un DOCX y no puedes generar Word, devuelve el texto con los títulos marcados (`#`, `##`). Una línea final ofrece otra versión con otro enfoque, ajustar el registro o ver los cambios marcados.
