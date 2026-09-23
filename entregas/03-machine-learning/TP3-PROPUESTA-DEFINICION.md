# TP3: propuesta de definición del problema, para discutir con el grupo

Versión 2, escrita el 2026-09-23. **La v1 (de esta misma mañana) quedó superada**: se escribió antes de incorporar el feedback de la reunión del 09/09 y antes de abrir el repo de Agustín, y su conclusión central (que el abandono no se puede medir y hay que reemplazarlo por desempeño) **ya no se sostiene**. Lo que sigue explica por qué.

Todo lo que dice MEDIDO sale de un artefacto abierto: nuestro pipeline del TP2 (`docs/10_relaciones.md`, `INVENTARIO-DATOS.md`) o el repo `agus476/radar-trayectorias-educativas-argentinas`, leído el 23/09 (último cambio suyo: 03/09).

> 📌 **Las decisiones que este documento propone (sacar la EPH y quedarse en 2024, el target de salidas sin pase, el denominador del join) quedaron asentadas por separado, con su evidencia y lo que se descartó, en `DECISIONES-TP3.md`.** Ese archivo es la fuente de verdad de las decisiones; este es el razonamiento completo que lleva a ellas.

---

## 1. El hallazgo que cambia el TP3

En la reunión del 09/09 se planteó mirar el repositorio de referencia para ver si sus datos podían cruzarse con los nuestros. **Abriéndolo, la granularidad no es a nivel individuo, y el resultado es incluso mejor para lo que necesitamos.**

MEDIDO, leyendo las cabeceras de sus tres datasets consolidados: sus datos son del **Relevamiento Anual** y están agregados exactamente por `anio, provincia, departamento, sector, ambito`. O sea, **la misma llave que nuestro dataset de Aprender**, año por medio. No hay que bajar de granularidad ni inventar un cruce: se hace un join directo por esas cuatro columnas más el año.

Y lo más importante: **ahí está la variable de abandono que a nosotros nos falta.** Sus columnas incluyen, por año de estudio (`_1` a `_12` y `_1314`):

| Bloque | Qué es | Por qué importa |
|---|---|---|
| `ssp_*` | **salidas sin pase** | Es el indicador estándar de abandono: el estudiante deja la escuela y no se inscribe en otra |
| `scp_*` | salidas con pase | Es traslado, no abandono. Sirve para no confundir una cosa con la otra |
| `nopromo_*` | no promovidos | Repitencia, antecedente del abandono |
| `promovidos_*`, `inicial_*`, `entrados_*` | matrícula y promoción | Dan el **denominador** para convertir los conteos en tasas |

Además tienen `Matricula_Secciones_Final.csv` (matrícula y secciones por año de estudio) y `Establecimiento_Caracteristicas_Final.csv` (conectividad, equipamiento, biblioteca, laboratorio), los dos con la misma llave.

**Y el año 2024 existe**: sus datos crudos van de **2011 a 2024**, uno por año.

## 2. Qué resuelve esto, punto por punto del feedback del 09/09

**"Ver bien el desfasaje de 2024 y 2025, quedarnos con uno solo."** Resuelto y la decisión se vuelve obvia: **nos quedamos en 2024** (Aprender 2024 más Relevamiento Anual 2024) y **la EPH 2025 sale del dataset**. Era la fuente que traía el desfasaje, la que menos aporta (24 valores distintos repetidos en 1.174 filas) y la que sostenía el proxy de abandono que no funcionaba. Con el Relevamiento Anual el contexto socioeconómico se puede reemplazar por infraestructura institucional real, que además es del mismo año y de la misma unidad.

**"Con eso definir cuál va a ser el indicador."** El indicador propuesto es la **tasa de salidas sin pase en los últimos años del secundario**: `ssp` de los años de estudio que corresponden a 5to y 6to, dividido por la matrícula inicial de esos mismos años. Es un target **observado**, no construido a partir de un supuesto, que es justo lo que el punto 3 de la consigna premia. Hay que verificar con el diccionario a qué índices corresponden 5to y 6to (los suyos van de 1 a 12 en una numeración continua, y `_1314` es un caso aparte): **eso se mide antes de escribir el target, no se asume.**

**"Elegir supervisado, no supervisado o combinar; regresión o clusterización."** Con un target real, las tres opciones quedan abiertas de verdad, y la de abajo es mi recomendación.

**"Muy bien técnicamente, mejorar storytelling; lo de alto impacto en la primera hoja; la última sección al comienzo; pensar que se lo planteamos a un stakeholder."** Aplica al entregable, no al análisis, y se resuelve escribiendo el informe al revés: conclusión y recomendación primero, método después, limitaciones al final pero cortas. **Cero código en el video final.**

## 3. Las cinco preguntas del punto 2 de la consigna, respondidas

**¿Qué representa una fila?** Un grupo territorial: departamento x sector x ámbito, en un año. MEDIDO en lo nuestro: 1.175 filas, 1.175 combos únicos, y cada valor es un conteo expandido por peso muestral. La unidad de Agustín es la misma, así que el join no cambia la granularidad.

**¿Qué queremos predecir?** La tasa de salidas sin pase de los últimos años del secundario en ese grupo, en 2024. Es abandono medido, no un proxy.

**¿Existe la variable o hay que construirla?** Existe (`ssp`). Lo único que se construye es la **tasa**, y su regla es explícita y aplicable igual a todas las filas: salidas sin pase sobre matrícula inicial de los mismos años de estudio. Esa es la diferencia entre construir un target y forzarlo.

**¿Qué información estaba disponible antes del resultado?** Acá hay dos trampas de leakage, y las dos son nuestras por construcción:
- **Del mismo Relevamiento**: `nopromo`, `scp` y `egresados` del mismo año describen el mismo cierre de ciclo que las salidas sin pase. Usarlas es leer la respuesta de al lado. Lo limpio es **predecir el abandono de 2024 con las características de 2023** (matrícula, infraestructura, repitencia del año anterior), que además es lo que haría un sistema de alerta temprana de verdad. Los datos están: hay catorce años.
- **De Aprender**: lengua y matemática salen de la misma prueba. Si el target es abandono, el desempeño de Aprender **sí** es un predictor legítimo, porque mide otra cosa.

**¿Qué podemos y qué no podemos afirmar?** Podemos hablar de grupos territoriales, no de estudiantes: siguen siendo correlaciones ecológicas. No podemos responder por sexo desde Aprender (MEDIDO: las columnas `sexo__*` dicen qué porcentaje del grupo es de cada sexo, no cómo le fue a cada uno), **pero el dataset de Agustín trae trayectoria desagregada por sexo** (`m_*` es el subconjunto mujeres), así que la pregunta por sexo se vuelve contestable sobre el abandono aunque no sobre el desempeño. Y no podemos hablar de causas.

## 4. Mi recomendación sobre la pregunta que hay que contestar

**Supervisado, regresión sobre la tasa, más una clusterización como pieza de storytelling.** El razonamiento:

- La **regresión** es lo que corresponde: el target es una proporción continua y no hay ningún umbral natural de "abandono alto". Meter un corte arbitrario para poder decir "clasificación" es agregar una decisión que hay que defender sin necesidad.
- Si el grupo prefiere clasificación por las métricas del punto 7 (matriz de confusión, precision, recall, PR-AUC), se puede hacer **además**, con el corte en el percentil que se declare, mostrando que el resultado aguanta dos o tres cortes distintos.
- La **clusterización** no compite con eso: sirve para el punto que la mentora marcó como flojo. Agrupar los departamentos en perfiles y ponerles nombre ("estatal rural sin conectividad con alta repitencia") es lo que un stakeholder entiende y recuerda, y es material de primera hoja. Como análisis vale poco sola; como manera de contar el resultado, vale mucho.

**El baseline** (punto 5, obligatorio): la mediana de la tasa de abandono por celda sector x ámbito. MEDIDO en desempeño, esas cuatro celdas se separan fuerte (0,62 estatal urbano contra 0,38 privado urbano), así que es una regla simple que ya captura señal. Si el modelo con todas las variables no le gana, **eso es el hallazgo** y hay que decirlo.

**El análisis de errores** (punto 7): partir el error por quintil de tamaño de grupo. MEDIDO: la mediana del quintil más chico son 29 estudiantes y la del más grande 1.225, y el chico tiene 1,4 veces la dispersión, con valores que llegan a 0,000 y 1,000. Es previsible que el error se concentre ahí, y mostrarlo con números es mejor que descubrirlo.

**La separación entrenamiento/evaluación**: por provincia si se usan variables provinciales; y si se predice 2024 con 2023, también sirve separar por año, que es lo más honesto para un problema temporal.

## 5. Lo que hay que verificar antes de construir (y no dar por hecho)

1. **Que los nombres de departamento coincidan.** Los suyos vienen en mayúsculas ("25 DE MAYO") y los nuestros no necesariamente. **Un join que matchea poco se ve igual que un join que anda, si nadie cuenta las filas**: hay que reportar cuántas de las 1.175 filas encuentran par, y decir el número.
2. **Qué índice es 5to y 6to de secundario** en su numeración de 1 a 12, y qué es `_1314`. Está en `01_raw_data/Diccionario_BD_Anominizadas.xlsx` y en `docs/data_dictionary.xlsx`.
3. **Si `ssp` está completo en 2024** o hay provincias sin reportar, como ya nos pasó con Corrientes-Chaco en el GAO.
4. **Cuánto pesa bajarlo**: el repo son ~100 MB y los consolidados grandes (`Trayectoria_Sexo_Final.csv` son 12 MB). Conviene traer solo los tres archivos de `02_data_formatting`, no el repo entero.

## 6. Lo que hay que decidir con el grupo

1. ¿Nos quedamos en 2024 y **sacamos la EPH**? (mi propuesta: sí, y es lo que pidió la mentora al hablar del desfasaje)
2. ¿El target es la tasa de salidas sin pase de 5to y 6to? ¿Regresión, clasificación o las dos?
3. ¿Predecimos 2024 con variables de 2023, que es lo que evita el leakage y convierte el trabajo en una alerta temprana?
4. ¿La clusterización entra como pieza de narrativa, además del modelo?
5. ¿Quién baja el Relevamiento Anual y valida el cruce, quién arma el baseline y quién escribe el informe al revés (impacto primero)?
