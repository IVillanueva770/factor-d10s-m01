# Decisiones de curacion

Generado por `pipeline/03_curacion/08_curar.py`. Cada decision de este informe sale de la misma estructura de datos que la aplica, asi que el codigo y el texto no pueden divergir.

## El criterio comun

**Ninguna decision borra filas ni modifica valores.** Las cuatro hacen lo mismo: vuelven visible un problema en vez de taparlo, para que cualquier analisis posterior lo pueda excluir con una condicion explicita y medir si excluirlo cambia el resultado.

La razon es que los tres problemas encontrados (clima escolar mal cubierto, departamentos enmascarados, valores extremos) golpean sobre todo a los grupos **chicos y rurales**, que son exactamente la poblacion con mayor riesgo de abandono. Limpiar por el camino facil habria sesgado el dataset contra su propio objeto de estudio.

**Resultado:** 1,174 x 131 -> 1,174 x 133. Mismas filas, 2 columnas nuevas, ninguna columna existente modificada (verificado por assert).

## 1. Clima escolar: se marca la calidad del dato, no se toca el dato

*columna nueva* · `clima_escolar_calidad`

**Que se encontro.** Es el unico bloque con problemas de cobertura: los otros 15 estan entre 0,98 y 1,00. Tiene 96 filas sin ningun dato y 91 con el dato calculado sobre menos de la mitad de los estudiantes de la fila. Los dos conjuntos son disjuntos, asi que son 187 filas (15,9%) y 9.808 estudiantes (1,8%).

**Por que importa.** El problema NO es aleatorio. La cobertura mediana cae de 0,921 en el quintil de grupos mas grandes a 0,722 en el mas chico, y por ambito va de 0,921 urbano a 0,744 rural: 155 de las 187 filas afectadas son rurales. Es decir que el clima escolar esta peor medido justo en las escuelas rurales chicas, que son las de mayor riesgo de abandono. Un modelo que use esta variable va a tener menos informacion precisamente donde mas la necesita, y eso hay que poder decirlo, no descubrirlo despues.

**Que se decidio.** Se conservan las tres columnas clima_escolar__* sin modificar y se agrega una columna con tres estados: 'ok', 'cobertura_baja' y 'sin_dato'. Permite repetir cualquier analisis excluyendo las filas flojas y comprobar si el resultado cambia.

**Que se descarto, y por que.** Imputar: inventaria valores justo en el segmento donde el sesgo vive, que es el peor lugar posible. Poner en NaN las 91 filas de baja cobertura: perderia dato real sin dejar rastro visible de la perdida. Sacar el bloque: tira una variable central del marco teorico por un problema que toca al 1,8% de los estudiantes.

## 2. Departamentos enmascarados: se identifican, no se borran

*columna nueva* · `es_agregado_provincial`

**Que se encontro.** 63 filas de 1.174 tienen departamento = 'Enmascarado', en 23 de las 24 jurisdicciones, con 10.444 estudiantes (1,9%). El Ministerio enmascara el nombre cuando el grupo es tan chico que identificaria a la escuela.

**Por que importa.** Rompe el significado de la clave territorial. Si el mismo texto aparece en 23 jurisdicciones, esas filas no son un departamento: son el agregado de los departamentos chicos de cada provincia. Nada avisaba: el chequeo de duplicados da 0 porque cada combinacion jurisdiccion + Enmascarado + sector + ambito es unica, y el de formato tampoco lo veia porque 'Enmascarado' esta bien escrito. Quien agrupe por departamento sin saberlo va a mezclar 23 provincias bajo un mismo nombre.

**Que se decidio.** Se conservan las 63 filas y se agrega una columna booleana que las identifica. Un analisis por departamento filtra es_agregado_provincial == False; uno por provincia usa todas, que es donde estas filas SI suman bien y donde sacarlas romperia los totales contra la fuente.

**Que se descarto, y por que.** Borrarlas: se irian 10.444 estudiantes de los departamentos mas chicos del pais, que es el perfil de mayor riesgo, y los totales por provincia dejarian de cerrar contra Aprender. Solo documentarlo: deja la trampa disponible para el que no lea el doc.

## 3. Valores extremos: no se tocan, y el chequeo se corrigio

*decision sin cambio en el dataset*

**Que se encontro.** 75 de 94 columnas numericas tienen valores a mas de 3 rangos intercuartiles del cuerpo de la distribucion. La peor, edad__21_anos, marca 138 filas.

**Por que importa.** Al traducir la proporcion a personas se ve que no son errores. En edad__21_anos el 70% de las filas vale exactamente 0, lo que aplasta el rango intercuartil a 0,0020 y deja el umbral de extremo en 0,0078; un solo estudiante de 21 anos en un grupo de 118 da 0,0085 y ya lo supera. La mediana de estudiantes detras de las 138 filas marcadas es 2,3 personas, y 84 de 138 tienen menos de 3. El chequeo estaba marcando 'aca hay un estudiante de 21 anos'. Ademas la senal es real: ponderando por estudiantes, la tasa de 21 anos va de 0,55% en estatal rural a 0,06% en privado urbano, nueve veces, la misma brecha de gestion que el TP1 encontro en sobreedad.

**Que se decidio.** No se recorta ni se winsoriza nada. Se corrigio el instrumento: el perfil ahora reporta cuantas personas hay detras de cada extremo, porque sin ese numero el chequeo mentia por omision.

**Que se descarto, y por que.** Winsorizar a los percentiles 1 y 99: modificaria datos correctos y borraria justamente los casos de sobreedad extrema, que son los que el proyecto viene a estudiar.

## 4. cob__sexo se conserva pese a tener varianza cero

*decision sin cambio en el dataset*

**Que se encontro.** cob__sexo vale exactamente 1,0 en las 1.174 filas: todos los estudiantes respondieron sexo.

**Por que importa.** Una columna constante no aporta a un modelo, pero esta no es una variable predictiva: es metadato de cobertura, de la misma familia que las otras 15 columnas cob__. Nunca iba a entrar a un modelo.

**Que se decidio.** Se conserva. Mantiene simetrica la familia cob__ (un bloque, una cobertura) y su valor constante es en si mismo una verificacion: si alguna vez deja de ser 1,0, algo cambio en la fuente o en el pipeline. La seleccion de variables para el modelo es del TP3 y ahi las de varianza cero se descartan solas.

**Que se descarto, y por que.** Sacarla del dataset: ahorra una columna de 131 y rompe la simetria de la familia por un beneficio que no existe en esta etapa.

