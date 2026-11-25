# Patrones de IA y sus alternativas

Las fórmulas que delatan un texto escrito en piloto automático, con lo que se hace en su lugar. Casi siempre la alternativa buena es **eliminar** y decir la cosa directamente.

`scripts/analizar.py` lee este archivo. Formato:
- Secciones `## ES · …` y `## EN · …`. Si el título contiene "Muletillas", cada aparición es un aviso. Si contiene "Conectores", se avisa por frecuencia (más de 2 por cada 300 palabras). Si contiene "Cierres", además de contar como muletilla, sirve para detectar párrafos que acaban en frase-resumen.
- Solo se detecta lo escrito entre `comillas invertidas`. Varias variantes en una celda: `a` / `b`. Un `…` dentro de la frase significa "cualquier cosa en medio" (máx. 80 caracteres).
- Si contiene "Tópicos", son frases hechas de ensayo escolar: cada aparición es un aviso de la categoría `topicos`, que pesa en la nota igual que las muletillas.
- Si contiene "Apelaciones", son las palabras que delatan un cierre de manual cuando aparecen en la ÚLTIMA frase del texto (expertos, el futuro, la opción equilibrada). Se avisan en la categoría `cierre`.
- Las secciones "Estructuras" son descriptivas: el script las mide con sus propias reglas (ritmo, tríadas, párrafos, arranques, puntuación).

Una alternativa no es un sustituto fijo. Si se quita "Además" en cinco sitios, no se pone "Asimismo" en los cinco: en tres no hace falta conector, en uno basta un punto y en otro sí conviene uno, el que pida la lógica de esa frase.

## ES · Muletillas

| Patrón | Alternativa |
|---|---|
| `es importante destacar` / `es importante señalar` | eliminar y dar el dato |
| `es importante tener en cuenta` / `es importante recordar` | eliminar; si de verdad importa, explicar por qué |
| `cabe mencionar` / `cabe destacar` / `cabe señalar` | eliminar |
| `vale la pena mencionar` / `merece la pena destacar` | eliminar |
| `en el mundo actual` / `en el mundo de hoy` | eliminar o concretar ("desde 2020", "en España") |
| `en la sociedad actual` / `en la sociedad moderna` | concretar qué sociedad y cuándo |
| `hoy en día más que nunca` | eliminar |
| `en el panorama actual` / `el panorama de` | eliminar o nombrar el sector |
| `juega un papel crucial` / `desempeña un papel crucial` | decir qué hace: "regula", "decide", "frena" |
| `juega un papel fundamental` / `desempeña un papel fundamental` | decir qué hace |
| `papel clave` / `un rol clave` | decir qué hace |
| `no solo… sino también` | dos frases, o "y" |
| `sumergirse en` / `nos sumergimos en` | "ver", "estudiar", "entrar en" |
| `embarcarse en un viaje` / `un viaje hacia` / `un viaje apasionante` | eliminar la metáfora |
| `sin lugar a dudas` / `sin duda alguna` | eliminar; si hay pruebas, darlas |
| `dicho esto` / `dicho lo anterior` | eliminar |
| `en este sentido` | eliminar o "aquí" |
| `en este contexto` / `en el contexto de` | eliminar |
| `a lo largo de la historia` / `desde tiempos inmemoriales` | dar la fecha o eliminar |
| `un amplio abanico de` / `una amplia gama de` | "muchos", o dar la cifra |
| `una gran variedad de` | "varios", o enumerar |
| `abordar los desafíos` / `desafíos y oportunidades` | nombrar el problema concreto |
| `de manera significativa` / `de forma significativa` | dar la magnitud: "un 30 %" |
| `es crucial` / `resulta crucial` | "hace falta", o eliminar |
| `es fundamental` / `resulta fundamental` | "hay que", o eliminar |
| `es esencial` / `resulta esencial` | "hay que", o eliminar |
| `un aspecto clave` / `aspectos clave` | nombrar el aspecto |
| `en constante evolución` / `en constante cambio` | eliminar o decir qué cambia |
| `revolucionar la forma en que` / `transformar la forma en que` | "cambiar cómo" |
| `navegar por la complejidad` / `navegar los retos` | "resolver", "manejar" |
| `desbloquear el potencial` / `liberar todo su potencial` | decir qué se consigue |
| `el poder de` | eliminar |
| `la clave del éxito` | decir qué funciona |
| `en un mundo cada vez más` / `cada vez más interconectado` | eliminar |
| `a medida que avanzamos` / `mirando hacia el futuro` | eliminar o dar el plazo |
| `el futuro es prometedor` / `un futuro prometedor` | eliminar o dar la previsión con su fuente |
| `un enfoque holístico` / `de manera holística` | "completo", o decir qué abarca |
| `de vanguardia` / `última generación` | decir qué tiene de nuevo |
| `fascinante` / `apasionante` | eliminar el adjetivo |
| `espero que esto te ayude` / `espero que te sea útil` | eliminar |
| `no dudes en` | "si necesitas algo, escríbeme" o eliminar |
| `espero que este mensaje te encuentre bien` / `espero que estés bien` | saludo breve o ir al asunto |
| `te escribo para` / `me pongo en contacto contigo para` | empezar por el asunto |
| `en última instancia` / `a fin de cuentas` | eliminar |
| `en un mundo donde` / `en un mundo en el que` | eliminar |
| `pieza clave` / `piedra angular` | decir qué sostiene |
| `marca la diferencia` / `marcar la diferencia` | decir en qué |
| `potenciar al máximo` / `maximizar el impacto` | dar el objetivo medible |
| `aportar valor` / `valor añadido` | decir qué aporta |
| `de cara al futuro` | dar el plazo |

## ES · Conectores sobreusados

| Patrón | Alternativa |
|---|---|
| `además` | casi siempre nada; un punto basta |
| `asimismo` | nada, o "también" una vez |
| `por otro lado` / `por otra parte` | nada si no hay contraste real |
| `sin embargo` | "pero", o reordenar para que el contraste se vea solo |
| `no obstante` | "pero", "aun así" |
| `por lo tanto` / `por tanto` | "así que", o nada si la consecuencia es obvia |
| `por consiguiente` / `en consecuencia` | "así que", "por eso" |
| `de igual manera` / `de igual forma` / `del mismo modo` | "también", o nada |
| `por ende` | "por eso" |
| `en primer lugar` / `en segundo lugar` | lista numerada o nada |
| `finalmente` / `por último` | nada si es claramente lo último |
| `igualmente` | "también", o nada |
| `cabe añadir` | eliminar |
| `a su vez` | nada, o explicar la relación |
| `en efecto` / `efectivamente` | eliminar |
| `de hecho` | eliminar salvo que corrija algo dicho antes |
| `es decir` | una vez está bien; si se repite, reescribir la idea más clara la primera vez |
| `en cuanto a` / `en lo que respecta a` | empezar por el tema directamente |

## ES · Cierres de párrafo

| Patrón | Alternativa |
|---|---|
| `en resumen` / `en suma` | eliminar el cierre; el párrafo ya lo ha dicho |
| `en conclusión` / `a modo de conclusión` | solo en la conclusión real del texto, y sin la fórmula |
| `en definitiva` | eliminar |
| `en pocas palabras` | eliminar |
| `así pues` | eliminar o "así que" dentro de otra frase |
| `todo esto demuestra` / `esto demuestra que` | dejar que lo demuestren los datos |
| `todo ello pone de manifiesto` / `esto pone de manifiesto` | eliminar |
| `en última instancia, esto` | eliminar |

## ES · Frases hechas y tópicos de ensayo

Suenan a redacción de bachillerato o a texto generado: valen para cualquier tema y por eso no dicen nada del tuyo. Son frases correctas, así que no están entre las muletillas: tienen su propia categoría, `topicos`.

| Patrón | Alternativa |
|---|---|
| `luces y sombras` / `sus luces y sus sombras` | eliminar; nombrar la ventaja y el problema concretos |
| `no… pasar por alto` / `no… pasarse por alto` | eliminar y dar el dato |
| `herramienta valiosa` / `herramienta muy valiosa` / `herramienta tan valiosa` | decir para qué sirve |
| `lo mejor de ambos mundos` / `lo mejor de los dos mundos` / `lo mejor de los dos` | decir qué se aprovecha de cada parte |
| `una nueva realidad` / `la nueva realidad` / `la nueva normalidad` | decir qué ha cambiado y desde cuándo |
| `un antes y un después` | decir qué cambió |
| `cada vez más` | dar la cifra o el periodo, o eliminar |
| `en la era digital` / `en la era de la información` | eliminar |
| `no es oro todo lo que reluce` / `no todo lo que reluce es oro` | decir el problema |
| `arma de doble filo` | decir qué ayuda y qué perjudica |
| `a día de hoy` / `hoy en día` | eliminar o dar la fecha |
| `muchos expertos` / `numerosos expertos` / `según los expertos` / `los expertos coinciden` / `los expertos señalan` | nombrar al experto y la fuente, o eliminar |
| `en definitiva` | eliminar |
| `abrir un debate` / `abre un debate` / `abre el debate` / `el debate está servido` | eliminar o plantear la pregunta concreta |
| `a la orden del día` / `un tema de actualidad` | eliminar o dar la fecha |
| `sin precedentes` | comparar con el caso anterior más parecido |
| `una realidad innegable` / `es innegable que` / `nadie puede negar que` | afirmarlo, con el dato |
| `un tema candente` / `un tema muy debatido` | decir quién lo discute |
| `la otra cara de la moneda` / `las dos caras de la moneda` / `toda moneda tiene dos caras` | decir el inconveniente |
| `pros y contras` | nombrarlos |
| `tanto un reto como una oportunidad` / `un reto y una oportunidad` | nombrar el reto o la oportunidad |
| `el justo equilibrio` / `encontrar el equilibrio` / `la opción más equilibrada` / `la alternativa más equilibrada` | decir qué se combina y por qué |
| `ha venido para quedarse` / `ha llegado para quedarse` / `llegó para quedarse` | decir desde cuándo y con qué datos |
| `un giro de 180 grados` | decir qué cambió |
| `la punta del iceberg` | dar la magnitud |
| `el quid de la cuestión` | decirlo |
| `un mundo globalizado` / `la sociedad globalizada` | concretar el ámbito |
| `cambiar las reglas del juego` / `cambia las reglas del juego` | decir qué regla cambia |
| `a pasos agigantados` | dar el ritmo con un dato |
| `un sinfín de` / `un sinnúmero de` | "muchos", o la cifra |
| `en boca de todos` | eliminar |
| `ha revolucionado` / `ha supuesto una revolución` | "ha cambiado", y decir qué |
| `no cabe duda de que` / `no hay duda de que` | afirmarlo |
| `en los tiempos que corren` / `de un tiempo a esta parte` | dar el periodo |
| `en pleno siglo xxi` | eliminar |
| `queda mucho camino por recorrer` / `un largo camino por recorrer` | decir qué falta |
| `el tiempo dirá` / `solo el tiempo lo dirá` | eliminar |
| `dejar huella` / `marcar un hito` / `marca un hito` | decir qué consecuencia tuvo |
| `las nuevas tecnologías` | nombrar la tecnología |
| `una cuestión compleja` / `un tema complejo` | explicar qué lo complica |
| `aprovechar al máximo` / `sacar el máximo partido` | decir qué se aprovecha |
| `un factor a tener en cuenta` / `un aspecto a tener en cuenta` | decir por qué cuenta |

## ES · Apelaciones finales

Se buscan solo en la última frase del texto. Un cierre que delega en "los expertos", mira "al futuro" o elige "la opción equilibrada" es de manual: no añade nada.

| Patrón | Alternativa |
|---|---|
| `expertos` / `expertas` / `especialistas` | cerrar con la última idea propia, o citar a alguien concreto con su fuente |
| `futuro` | cerrar con una consecuencia concreta |
| `equilibrada` / `equilibrado` / `equilibrio` | tomar postura o terminar en el último dato |

## ES · Estructuras y tics

| Estructura | Alternativa |
|---|---|
| Tríada sistemática: "rápido, eficiente y seguro" | quedarse con el elemento que importa, o usar dos o cuatro |
| Frase-resumen al final de cada párrafo | cortar el párrafo en la última idea nueva |
| Todos los párrafos de la misma longitud | uno de dos líneas al lado de uno largo |
| Varios párrafos que empiezan igual | arrancar por el sujeto, por un dato, por una pregunta concreta |
| Guion largo para cada inciso | comas, paréntesis o dos frases |
| Pregunta retórica como transición ("¿Y qué significa esto?") | decirlo |
| Falso suspense: "¿El resultado? Un éxito." | "Funcionó: …" |
| "No es X, es Y" para todo | afirmar Y |
| Cierre motivacional ("¡El futuro está en tus manos!") | terminar en el último dato útil |
| Negrita como etiqueta al inicio de cada párrafo | prosa normal, o títulos de verdad |
| Lista con viñetas para lo que es un razonamiento | prosa con sus conectores |
| Cautela en cada frase ("podría decirse que", "en cierta medida") | una sola matización donde haga falta |
| Sinónimos rotatorios para no repetir el sujeto | repetir el término técnico: es más claro |
| Adjetivo doble ("claro y conciso", "sólido y robusto") | un adjetivo, o ninguno |
| Emojis como viñetas | quitarlos fuera de redes |
| Frases de 15-25 palabras una detrás de otra | mezclar frases de 4 palabras con otras de 35 |

## EN · Muletillas

| Pattern | Alternative |
|---|---|
| `it's worth noting` / `it is worth noting` | delete and state the fact |
| `it's important to note` / `it is important to note` | delete |
| `it's important to remember` / `it is important to remember` | delete or say why it matters |
| `in today's fast-paced world` / `in today's world` | delete or give a date |
| `ever-evolving` / `ever-changing` | delete or say what changes |
| `the landscape of` / `in the landscape` | name the field |
| `delve` / `delves` / `delving` | "look at", "cover" |
| `tapestry` | delete the metaphor |
| `a testament to` / `stands as a testament` | "shows" |
| `plays a crucial role` / `plays a pivotal role` / `plays a vital role` | say what it does |
| `plays a key role` / `plays an important role` | say what it does |
| `not only… but also` | two sentences, or "and" |
| `navigate the complexities` / `navigating the complexities` | "handle", "work through" |
| `unlock the potential` / `unlock the full potential` | say what you get |
| `unleash` | delete |
| `harness the power` / `the power of` | delete |
| `revolutionize` / `revolutionise` | "change" |
| `cutting-edge` / `state-of-the-art` | say what is new |
| `seamless` / `seamlessly` | "smooth", or delete |
| `a holistic approach` / `holistic` | say what it covers |
| `a myriad of` / `myriad` | "many", or the number |
| `a plethora of` | "many" |
| `a wide range of` / `a wide array of` | "many", or list them |
| `embark on a journey` / `on a journey` | delete the metaphor |
| `in the realm of` / `realm` | "in" |
| `foster` / `fostering` | "build", "encourage" |
| `leverage` / `leveraging` | "use" |
| `synergy` / `synergies` | say who does what together |
| `paradigm shift` | say what changed |
| `at the end of the day` | delete |
| `when it comes to` | start with the subject |
| `needless to say` / `it goes without saying` | delete |
| `without a doubt` / `undoubtedly` | delete or give the evidence |
| `i hope this email finds you well` / `i hope you're doing well` | short greeting or straight to the point |
| `feel free to` / `don't hesitate to` | "let me know if…" or delete |
| `i hope this helps` | delete |
| `let's dive in` / `dive into` / `deep dive` | delete or "look at" |
| `buckle up` | delete |
| `serves as a` / `stands as a` | "is" |
| `underscores the importance` / `highlights the importance` | say why it matters |
| `it is crucial` / `it's crucial` | "you need to", or delete |
| `it is essential` / `it's essential` | "you need to", or delete |
| `key takeaway` / `key takeaways` | state the point |
| `moving forward` / `going forward` | give the time frame or delete |
| `in an increasingly` / `increasingly interconnected` | delete |
| `a rich history` / `rich and diverse` | give one concrete fact |
| `robust` | say what makes it strong |
| `vibrant` | delete the adjective |
| `elevate` / `elevating` | "improve", with what and by how much |
| `empower` / `empowering` | "let", "help" |
| `streamline` / `streamlining` | "simplify", say what step goes |
| `crucial` / `pivotal` | delete or say why |
| `excited to share` / `thrilled to announce` | state the news |
| `the future is bright` / `the future of… is bright` | delete or give the forecast and its source |

## EN · Conectores sobreusados

| Pattern | Alternative |
|---|---|
| `moreover` | nothing; a full stop works |
| `furthermore` | nothing, or "also" once |
| `additionally` / `in addition` | nothing, or "also" |
| `however` | "but", or reorder so the contrast shows |
| `therefore` | "so", or nothing if the result is obvious |
| `consequently` / `as a result` | "so" |
| `thus` / `hence` | "so" |
| `on the other hand` | nothing unless there is a real contrast |
| `similarly` / `likewise` | "also", or nothing |
| `firstly` / `secondly` / `lastly` | a numbered list, or nothing |
| `notably` / `importantly` | delete |
| `nevertheless` / `nonetheless` | "still", "but" |
| `indeed` | delete |
| `in fact` | delete unless it corrects something |
| `that said` / `with that said` | delete |
| `essentially` / `basically` | delete |
| `in terms of` | rephrase around the subject |
| `as such` | "so" |

## EN · Cierres de párrafo

| Pattern | Alternative |
|---|---|
| `in conclusion` | only in the real conclusion, without the formula |
| `in summary` / `to sum up` | delete the closer |
| `all in all` | delete |
| `ultimately` | delete |
| `overall` | delete |
| `in short` / `in essence` | delete |
| `this shows that` / `this highlights` | let the facts show it |
| `the bottom line is` | state it |

## EN · Frases hechas y tópicos de ensayo

| Pattern | Alternative |
|---|---|
| `double-edged sword` | say what helps and what hurts |
| `game changer` / `game-changer` | say what changed |
| `best of both worlds` | say what each side brings |
| `in this day and age` | delete or give a date |
| `experts agree` / `many experts` / `experts say` / `according to experts` | name the expert and the source, or delete |
| `in the digital age` / `in today's digital age` / `in the digital era` | delete |
| `a new reality` / `the new normal` | say what changed and when |
| `pros and cons` | name them |
| `lights and shadows` / `light and shadow` | name the upside and the problem |
| `cannot be overlooked` / `can't be overlooked` / `should not be overlooked` / `cannot be ignored` | delete and state the fact |
| `a valuable tool` / `an invaluable tool` | say what it is for |
| `more and more` | give the number or the period |
| `here to stay` | say since when, with data |
| `a turning point` / `a watershed moment` | say what changed |
| `the tip of the iceberg` | give the scale |
| `the heart of the matter` / `at the heart of` | say it |
| `all that glitters is not gold` | name the problem |
| `two sides of the same coin` / `the other side of the coin` | name the downside |
| `strike a balance` / `the right balance` / `a healthy balance` / `the most balanced` | say what is combined and why |
| `the jury is still out` | say what is still unknown |
| `only time will tell` / `time will tell` | delete |
| `a long way to go` | say what is missing |
| `sparks a debate` / `opens a debate` / `opens up a debate` | state the actual question |
| `a hot topic` / `hotly debated` | say who disagrees about what |
| `unprecedented` | compare with the closest previous case |
| `there is no doubt that` / `there's no doubt that` | state it |
| `it is undeniable` / `undeniably` | state it, with the fact |
| `in the 21st century` / `in the twenty-first century` | delete |
| `a globalized world` / `a globalised world` / `global village` | name the scope |
| `rapidly changing world` / `fast-changing world` | delete |
| `by leaps and bounds` | give the rate |
| `a wake-up call` | say what should change |
| `food for thought` | delete |
| `a perfect storm` | name the causes |
| `win-win` | say who gains what |
| `the elephant in the room` | name it |
| `think outside the box` | say what to do differently |
| `on the rise` | give the trend with a number |
| `a must-have` | say why it is needed |
| `at a crossroads` | name the choice |
| `it remains to be seen` | say what is unknown |
| `new technologies` | name the technology |
| `make the most of` / `get the most out of` | say what is used |

## EN · Apelaciones finales

Checked only in the last sentence of the text.

| Pattern | Alternative |
|---|---|
| `experts` / `expert` / `specialists` | end on your own last point, or cite someone concrete with a source |
| `future` | end on a concrete consequence |
| `balanced` / `balance` | take a position or end on the last fact |

## EN · Estructuras y tics

| Structure | Alternative |
|---|---|
| Rule of three everywhere: "fast, efficient and secure" | keep the item that matters, or use two or four |
| Summary sentence closing every paragraph | end on the last new idea |
| Paragraphs all the same length | put a two-line paragraph next to a long one |
| Several paragraphs opening the same way | open with the subject, a number, a concrete question |
| Em dash for every aside | commas, brackets or two sentences |
| Rhetorical question as a transition ("So what does this mean?") | say it |
| Fake suspense: "The result? A huge success." | "It worked: …" |
| "It's not X, it's Y" for everything | say Y |
| Motivational closer ("The future is yours!") | end on the last useful fact |
| Bold label at the start of each paragraph | plain prose, or real headings |
| Bullets for what is really an argument | prose with its connectors |
| Hedging in every sentence ("arguably", "to some extent") | one caveat where it is needed |
| Rotating synonyms to avoid repeating the subject | repeat the technical term |
| Paired adjectives ("clear and concise", "robust and scalable") | one adjective, or none |
| Emojis as bullet points | drop them outside social media |
| Sentence after sentence of 15-25 words | mix 4-word sentences with 35-word ones |
