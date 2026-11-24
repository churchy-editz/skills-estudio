# Patrones de IA y sus alternativas

Las fórmulas que delatan un texto escrito en piloto automático, con lo que se hace en su lugar. Casi siempre la alternativa buena es **eliminar** y decir la cosa directamente.

`scripts/analizar.py` lee este archivo. Formato:
- Secciones `## ES · …` y `## EN · …`. Si el título contiene "Muletillas", cada aparición es un aviso. Si contiene "Conectores", se avisa por frecuencia (más de 2 por cada 300 palabras). Si contiene "Cierres", además de contar como muletilla, sirve para detectar párrafos que acaban en frase-resumen.
- Solo se detecta lo escrito entre `comillas invertidas`. Varias variantes en una celda: `a` / `b`. Un `…` dentro de la frase significa "cualquier cosa en medio" (máx. 80 caracteres).
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
| `en la era digital` / `en la era de la información` | eliminar |
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
| `un antes y un después` | decir qué cambió |
| `marca la diferencia` / `marcar la diferencia` | decir en qué |
| `potenciar al máximo` / `maximizar el impacto` | dar el objetivo medible |
| `aportar valor` / `valor añadido` | decir qué aporta |
| `de cara al futuro` | dar el plazo |
| `ha llegado para quedarse` / `llegó para quedarse` | decir desde cuándo y con qué datos |

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
| `in today's digital age` / `in the digital age` | delete |
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
| `game-changer` / `game changer` | say what changed |
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
