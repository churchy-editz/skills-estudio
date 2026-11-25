# Paletas por asignatura

Cada paleta tiene 6 valores: 4 colores semánticos, fondo y texto. Se copian tal cual en el `:root` de `assets/plantilla-base.html`.

## Significado fijo de los colores

| Variable    | Caja        | Etiqueta impresa | Para qué                                        |
|-------------|-------------|------------------|-------------------------------------------------|
| `--def`     | `.def`      | DEFINICIÓN       | Qué es algo. También colorea los títulos.       |
| `--ejemplo` | `.ejemplo`  | EJEMPLO          | Un caso concreto de la fuente.                  |
| `--ojo`     | `.ojo`      | OJO              | Error frecuente, confusión típica o "verificar". |
| `--clave`   | `.clave`    | DATO CLAVE       | Lo que hay que saberse sí o sí.                 |

El fondo de cada caja no es un color aparte: es el 10 % del color semántico mezclado con `--fondo` (`color-mix` en CSS; el conversor a DOCX hace la misma cuenta).

## Paletas

| Paleta | `--fondo` | `--texto` | `--def` | `--ejemplo` | `--ojo` | `--clave` | Fuente sugerida |
|---|---|---|---|---|---|---|---|
| **Neutra (por defecto)** | `#ffffff` | `#1f1f1f` | `#1f5f8b` | `#2e6b30` | `#a3261b` | `#7a4b00` | sans |
| **Ciencias** (biología, química, física) | `#fbfdfb` | `#18261f` | `#0b6e69` | `#3d6b1f` | `#b02a1f` | `#6b3fa0` | sans |
| **Matemáticas** (y estadística) | `#fdfdfd` | `#1a1c24` | `#1d4e89` | `#2f6b4f` | `#b3261e` | `#8a4b00` | sans |
| **Historia** (y geografía) | `#fcf9f2` | `#2b2118` | `#7a3e12` | `#4f6228` | `#9e1c1c` | `#23527c` | serif |
| **Lengua y literatura** | `#fffdf9` | `#241b26` | `#6a2c70` | `#1f6f6b` | `#a8321e` | `#8a5a00` | serif |
| **Idiomas** | `#fafcff` | `#1a2230` | `#1560a0` | `#1b7340` | `#b4261a` | `#7b3f98` | sans |
| **Derecho / oposiciones** | `#ffffff` | `#1b1b1b` | `#1c3d6e` | `#3f5f3a` | `#8f1d1d` | `#6b4e16` | serif |
| **Economía** (y empresa) | `#fbfcfd` | `#1c2329` | `#0f5c6e` | `#2f6b2f` | `#b03a12` | `#5b3d99` | sans |
| **Arte y humanidades** (filosofía, música) | `#fdfbf8` | `#2a2226` | `#8a2f4c` | `#2d6a5e` | `#a32d1a` | `#5a4a8a` | serif |

Fuentes (sin descargas, solo fuentes del sistema):
- sans: `--fuente: system-ui, "Segoe UI", Roboto, Arial, sans-serif;`
- serif: `--fuente: Georgia, Cambria, "Times New Roman", serif;`

Si la asignatura no encaja en ninguna, usar la neutra. Si el tema mezcla dos (historia del derecho, por ejemplo), elegir la del examen para el que se estudia.

## Contraste verificado (WCAG 2.1 AA, mínimo 4,5:1)

Se comprobaron tres combinaciones por cada color semántico: color sobre `--fondo` (títulos y leyenda), color sobre el fondo de su caja (etiqueta) y `--texto` sobre el fondo de la caja (cuerpo). La tabla da el peor de esos valores por color.

| Paleta | texto/fondo | def | ejemplo | ojo | clave | Peor caso |
|---|---|---|---|---|---|---|
| Neutra | 16,48 | 5,90 | 5,56 | 6,22 | 6,36 | 5,56 |
| Ciencias | 15,38 | 5,17 | 5,36 | 5,48 | 6,21 | 5,17 |
| Matemáticas | 16,71 | 7,06 | 5,36 | 5,48 | 5,76 | 5,36 |
| Historia | 14,98 | 6,74 | 5,58 | 6,39 | 6,64 | 5,58 |
| Lengua y literatura | 16,41 | 7,91 | 5,08 | 5,63 | 5,08 | 5,08 |
| Idiomas | 15,53 | 5,48 | 4,97 | 5,38 | 5,85 | 4,97 |
| Derecho / oposiciones | 17,22 | 9,11 | 6,23 | 7,43 | 6,60 | 6,23 |
| Economía | 15,47 | 6,31 | 5,45 | 5,10 | 6,80 | 5,10 |
| Arte y humanidades | 15,00 | 6,70 | 5,28 | 5,86 | 6,28 | 5,28 |

Los números de `ol.pasos` usan `--fondo` sobre `--def`: es el mismo par que "def sobre fondo", así que también pasa.

Si se cambia un color, volver a medir las tres combinaciones antes de usarlo.
