# Ejemplos de reescritor-estilo

Todos los textos están escritos para esta skill. Personas, empresas, proyectos, cifras y citas son **ficticios**. En particular, las referencias APA del ejemplo académico (Martínez y Ruiz, 2021; Gómez, 2022; Ortega et al., 2023) son inventadas y no corresponden a ninguna publicación real. Solo están para comprobar que la reescritura conserva el formato de cita.

| Ejemplo | Original | Original con tics marcados ⟦ ⟧ | Reescritura (intensidad media) | Informe de `analizar.py` |
|---|---|---|---|---|
| Párrafo académico (ES) | `academico-original.md` | `academico-original-marcado.md` | `academico-reescrito.md` | `academico-informe.txt` |
| Email profesional (ES) | `email-original.md` | `email-original-marcado.md` | `email-reescrito.md` | `email-informe.txt` |
| Post de LinkedIn (EN) | `linkedin-original.md` | `linkedin-original-marcado.md` | `linkedin-reescrito.md` | `linkedin-informe.txt` |
| Voz de un usuario (ES) | `voz-original.md` | `voz-original-marcado.md` | `voz-reescrito.md` | `voz-informe.txt` |

El ejemplo de voz parte de dos muestras de una usuaria ficticia (`voz-muestra-1.md`, `voz-muestra-2.md`). El perfil que se extrae de ellas está en `voz-perfil.md`.

Los marcados los genera `analizar.py --marcar`. Señalan muletillas, tópicos de ensayo, conectores de la lista y tríadas. Las estructuras que dependen del conjunto (ritmo, longitud de párrafos, cierres, el último párrafo) aparecen en el informe, no en el marcado.

Para regenerar un informe:

    python ../scripts/analizar.py academico-original.md academico-reescrito.md
