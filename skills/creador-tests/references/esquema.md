# Esquema del JSON

Un test es un archivo `test-<tema>.json` con dos claves: `meta` y `preguntas`. `scripts/validar.py` comprueba todo lo que aparece aquí. Lo marcado como error impide generar el HTML.

## meta

| Clave | Tipo | Obligatoria | Valores |
|---|---|---|---|
| `titulo` | texto | sí | Título del test |
| `asignatura` | texto | sí | Nombre de la asignatura ("Biología") |
| `nivel` | texto | sí | `eso`, `bachillerato`, `universidad`, `oposiciones`, `profesional` |
| `penalizacion` | texto | sí | `ninguna`, `1/3` o `1/4` |
| `fuente` | texto | sí | Archivo o material del que salen las preguntas |
| `dificultad` | texto | no | `facil`, `media`, `dificil` o `progresiva`. Con `progresiva`, el HTML baraja solo dentro de cada nivel de dificultad para que el orden siga subiendo |
| `secciones` | lista de textos | no | Secciones del material. Si está, el validador avisa de las secciones sin preguntas |

## preguntas[]

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

### tecnica_distractor

Dice con qué técnica se construyó cada opción falsa (catálogo en `variedad.md`).

- `multiple` y `caso`: lista de 4 elementos alineada con `opciones`, con `null` en la posición de la correcta.
- `vf`: si el enunciado es falso, la técnica de la trampa que contiene (texto). Si es verdadero, `null`.
- `huecos`: `null`.

Técnicas válidas: `concepto_vecino`, `inversion_causa_efecto`, `dato_parcial`, `generalizacion`, `error_calculo`, `cifra_cercana`, `orden_alterado`, `intercambio`, `funcion_opuesta`.

### Huecos

La comparación del HTML no distingue tildes ni mayúsculas, e ignora la puntuación de los extremos. Hay que incluir todas las formas válidas: sinónimos aceptados por la fuente, cifra y número escrito, número romano y arábigo.

## Un ejemplo de cada tipo

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
