# Errores frecuentes

Lo que más aparece al corregir. Sirve para saber dónde mirar primero y para explicar el porqué de un error cuando el recálculo no coincide.

## Informes de laboratorio

### Cálculos

| Error | Cómo se reconoce | Script |
|---|---|---|
| Dilución con el factor al revés o con un orden de magnitud de diferencia | El V1 sale 10 veces mayor o menor que el recalculado | `calculos_lab.py` (`dilucion`) |
| Volumen de disolvente dado como volumen final | V2 del trabajo = V2 − V1 recalculado | `dilucion` (lo indica en «nota») |
| Olvidar el factor de dilución al interpolar | La concentración coincide con la de la muestra diluida | `calibrado` (lo indica en «nota») |
| Cociente invertido en Henderson-Hasselbalch | El pH sale con el signo del logaritmo cambiado respecto al pKa | `henderson_hasselbalch` (lo indica en «nota») |
| Dar r en vez de R² | El valor declarado es la raíz del R² recalculado | `calibrado` (lo indica en «nota») |
| R², pendiente u ordenada copiados mal | Valores distintos en texto, figura y tabla | `revisar_numeros.py` + `calibrado` |
| Extrapolar fuera de la recta | Absorbancia de la muestra fuera del intervalo de los patrones | `calibrado` (lo indica en «nota») |
| Molaridad con el volumen en mL sin pasar a L | Resultado 1000 veces menor | `molaridad` |
| Rendimiento por encima del 100 % sin comentario | Producto húmedo o impuro, o teórico mal calculado | `rendimiento` |
| Lambert-Beer con ε en otras unidades | Concentración desfasada en potencias de 10 | `lambert_beer` |

### Presentación

- Unidades: «ml» y «mL» mezclados, «ºC» con el ordinal, «mins», «seg», «ul» por µL, cifra pegada a la unidad («595nm»), «rpm» sin la fuerza en × g.
- Cifras significativas: resultados con 4 decimales a partir de datos con 2; misma columna con decimales distintos.
- Ejes sin unidad o con «Concentración» sin decir de qué.
- Recta de calibrado sin ecuación ni R² en la figura.
- Tablas con media, pero sin desviación estándar ni número de réplicas.

### Contenido

- Resultados que interpretan («lo que confirma…») y discusión que solo repite números.
- Fuentes de error genéricas («errores humanos», «de pipeteo») sin relacionarlas con un dato concreto.
- Conclusiones que comparan con métodos o condiciones que no se probaron.
- Objetivos que no se retoman en las conclusiones.
- Valor de referencia (etiqueta, bibliografía) sin fuente o sin comparar con el obtenido.
- Métodos copiados del guion en futuro («se añadirán») o en imperativo («añadir 2 mL»): se cuenta lo que se hizo, en pasado.

## Memorias de prácticas e informes técnicos

### Objetivos y pruebas

- Objetivos no medibles («hacer una aplicación eficiente») o medibles que nunca se miden (tiempos, usuarios concurrentes, cobertura).
- Pruebas descritas («se hicieron pruebas unitarias») sin decir cuántas, cuáles pasaron y qué cubren.
- «Funciona correctamente» como única evidencia.
- Conclusiones que dan objetivos por cumplidos sin remitir a la prueba que lo demuestra.

### Diseño

- Elección de tecnología sin porqué («se usó MongoDB»), o con un porqué que no se relaciona con los requisitos («es muy popular»).
- Diagramas que no se citan ni se explican, o que no coinciden con el código descrito (clases que no existen, relaciones distintas).
- Arquitectura descrita como lista de capas sin decir qué hace cada una.

### Implementación y redacción

- Pegar código largo sin explicar lo que no es obvio. El código va en un anexo o repositorio; en el texto, el fragmento clave y su explicación.
- Mezclar términos: «librería» y «framework», «test» y «prueba» y «validación» como sinónimos.
- Capturas de pantalla sin leyenda ni referencia.
- Repositorio o enlaces sin fecha de consulta.

## Ensayos y trabajos bibliográficos

- Tesis implícita: hay que llegar al final para saber qué se defiende.
- Resumir fuentes una tras otra («Según A… Según B…») en vez de relacionarlas.
- Citas de segunda mano presentadas como directas.
- Conclusión que introduce argumentos nuevos.
- Fuentes no académicas (webs sin autor, blogs) como apoyo de afirmaciones centrales.
