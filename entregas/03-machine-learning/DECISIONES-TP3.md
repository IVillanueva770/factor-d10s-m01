# Decisiones del TP3, con su evidencia

Registro de las decisiones que cambian el dataset y el objetivo del proyecto, escrito para que dentro de tres meses nadie tenga que re-derivarlas ni dude de por qué se tomaron. **Una decisión por bloque, con lo que la sostiene, lo que se descartó y qué pasa si se revierte.**

Estado al **2026-09-23**. Cada bloque dice explícitamente quién la tomó y qué falta para cerrarla. Las que están marcadas **DECIDIDA POR IGNACIO** todavía tienen que pasar por el grupo y por la mentora: se llevan a la reunión, no se dan por acordadas.

Documentos relacionados: la consigna leída (`TP3-CONSIGNA-LEIDA.md`), el razonamiento completo (`TP3-PROPUESTA-DEFINICION.md`) y las decisiones de curación del TP2 (`08_decisiones_curacion.md`), que esta pasada **no invalida**.

---

## D0. Las tres fuentes, en una tabla, para que nadie se confunda otra vez

Esta tabla existe porque la confusión ya pasó dos veces en la misma semana, en las dos direcciones. **Va primero porque todo lo demás se apoya acá.**

| Fuente | Qué te dice | Quién contesta | Año que tenemos | Estado |
|---|---|---|---|---|
| **Pruebas Aprender** | desempeño en lengua y matemática, clima escolar, nivel socioeconómico, educación de la madre y del padre, libros en el hogar, horas de estudio, inasistencias, sobreedad, repitencia | **el estudiante**, en un cuestionario que completa el día de la prueba | **2024** (y 2022) | **SE QUEDA.** Es la fuente principal del proyecto |
| **Relevamiento Anual** | matrícula inicial, entrados, salidas con y sin pase, promovidos, no promovidos, egresados, secciones, y del edificio: electricidad, internet, equipamiento, biblioteca | **la escuela**, en un formulario administrativo anual | **2011 a 2024** | **ENTRA.** Es la fuente nueva y la que trae el abandono |
| **EPH** (Encuesta Permanente de Hogares) | pobreza, ingresos, hacinamiento, agua, educación de los adultos, **a nivel provincia** | los hogares, al encuestador del INDEC | **2025** | **SALE** |

**Aprender no tiene problema de fecha.** Es de 2024, igual que el Relevamiento Anual: los dos hablan del mismo año. La única fuente desfasada es la EPH, que es de 2025.

---

## D1. El proyecto se queda en 2024 y la EPH sale del dataset

**Estado: DECIDIDA POR IGNACIO el 2026-09-23.** Se lleva al grupo y a la mentora para confirmar, pero la dirección está tomada.

**La decisión.** Todas las fuentes del TP3 son de 2024: Aprender 2024 más Relevamiento Anual 2024. Los indicadores `eph_*` **dejan de usarse como predictores**.

**Qué la disparó.** La mentora lo marcó en la reunión del 09/09, textual en la nota del grupo: *"ver bien el desfasaje de 2024 y 2025 en el dataset"*, y pidió quedarse con una sola época. La consigna del TP3 lo refuerza desde otro lado: pide no usar como predictor información que solo podría conocerse después del resultado, y la EPH 2025 es posterior al hecho que se quiere explicar.

**Las tres razones, en orden de peso.**

1. **Es la única fuente desfasada.** La consigna original pedía Aprender 2024 más EPH del 3er trimestre de **2024**, "por ser la medición más cercana temporalmente". En el repo de la mentora solo está la de **2025** (verificado en los datos: `ANO4 = 2025`). Nunca se resolvió: se documentó y se siguió.
2. **Aporta poco y puede inflar el análisis.** MEDIDO en el TP2: sus indicadores **se repiten idénticos en todos los departamentos de una misma provincia**, o sea 24 valores distintos repartidos en 1.174 filas. Calcular a nivel fila con ellos infla el n sin agregar información. Está escrito como advertencia en `10_relaciones.md`.
3. **Sostenía un target que no medía lo que decía medir.** El proxy de abandono construido desde la EPH **correlaciona +0,16 con el desempeño**. Un proxy de abandono que no se relaciona con el principal antecedente del abandono no es débil: es un número sin contenido. Ese era el único uso que justificaba arrastrarla.

**Qué reemplaza lo que daba.** Daba contexto socioeconómico provincial. Lo reemplazan las **características del establecimiento** del Relevamiento Anual, que son del mismo año, de la misma unidad de análisis y varían entre departamentos en vez de repetirse por provincia. Mejora en las tres dimensiones; no es un recorte por comodidad.

**Qué se descartó y por qué no.**

- *Bajar la EPH 2024 del INDEC y mantener las tres fuentes.* Se podría, pero es trabajo para recuperar una fuente que aporta 24 valores distintos y cuyo mejor uso ya quedó cubierto por una fuente mejor. Si el grupo igual la quiere como contexto, entra **a nivel provincia y declarada como tal**, nunca como una columna más a nivel fila.
- *Dejar todo como está y explicar el desfasaje en una nota.* Es lo que hicimos en el TP1 y es justo lo que la mentora pidió resolver.

**Consecuencias.**

- Los resultados del TP1 y el TP2 que usan `eph_*` **no se borran ni se corrigen**: valen para lo que decían, con su advertencia de correlación ecológica a nivel provincia. Lo que cambia es que el TP3 no construye sobre ellos.
- La correlación más fuerte del trabajo hasta hoy (ingreso per cápita familiar mediano contra desempeño en matemática, r = -0,82 sobre 24 jurisdicciones, que sobrevivió las tres pruebas de robustez) **queda como hallazgo del TP2 y deja de ser insumo del TP3**. Sigue siendo citable.
- Si alguien revierte esta decisión, vuelven el desfasaje y el n inflado. La reversión tiene que decir qué hace con las dos cosas.

---

## D2. El target es la tasa de salidas sin pase de los últimos años del secundario

**Estado: DECIDIDA POR IGNACIO el 2026-09-23**, pendiente de confirmar con la mentora (es la pregunta principal que se le lleva).

**La decisión.** El proyecto pasa a explicar abandono **medido**, no un proxy:

> salidas sin pase de los últimos años del secundario, dividido por la matrícula inicial de esos mismos años, en ese departamento, sector y ámbito, en 2024.

**La fuente es el Relevamiento Anual del Ministerio de Educación, que es público.** El repo `agus476/radar-trayectorias-educativas-argentinas` es **una guía, no la fuente**: él ya lo bajó, concatenó y limpió de 2011 a 2024, y sirve como referencia para no tropezar con lo que ya resolvió. Los datos los bajamos nosotros y a él se lo cita como guía.

**Qué trae** (MEDIDO el 23/09 leyendo las cabeceras de los tres consolidados):

| Lo que trae | Columnas | Para qué |
|---|---|---|
| Salidas **sin** pase | `ssp_1` a `ssp_12`, `ssp_1314` | El numerador. Es el indicador estándar de abandono: el estudiante deja la escuela y no se inscribe en otra |
| Salidas **con** pase | `scp_*` | Traslado, NO abandono. Tenerlas separadas es lo que evita confundir una cosa con la otra |
| Matrícula inicial | `inicial_*` | El denominador |
| No promovidos | `nopromo_*` | Repitencia administrativa |
| Las mismas, solo mujeres | prefijo `m_*` | Habilita la pregunta por sexo, imposible con Aprender |

**La llave es la misma que la nuestra.** Sus archivos están partidos por `anio, provincia, departamento, sector, ambito`; los nuestros por `jurisdiccion, departamento, sector, ambito`. **Es la misma partición del país**, así que el cruce no cambia la granularidad de nada.

⚠️ **Corrección de una nota del grupo, para que no se propague.** La nota de la reunión del 09/09 dice que ese repo tiene "info a nivel individuo". **No la tiene**: sus datos son agregados, igual que los nuestros. La confusión no cambia la conclusión, pero si alguien planifica creyendo que va a poder trabajar a nivel estudiante, diseña sobre algo que no existe.

**Qué se descartó y por qué no.**

- *Seguir con el proxy de la EPH.* Correlaciona 0,16. No mide abandono.
- *Reemplazar el abandono por desempeño en matemática.* Fue la propuesta de la mañana del 23/09, escrita antes de abrir el Relevamiento Anual. Era la mejor decisión con los datos de entonces y dejó de serlo con una fuente más. El desempeño pasa de target a **predictor legítimo**, porque mide algo distinto del abandono.
- *Usar Aprender 2022 para predecir el abandono de 2023 o 2024.* Se evaluó y **se descartó el 23/09 por decisión de Ignacio**: esquivaba un detalle metodológico fino a cambio de mucho trabajo extra. El problema que esquivaba se resuelve declarándolo (ver abajo).

**Lo que hay que resolver midiendo, antes de escribir el target** (no se asume ninguna):

1. **Qué índices son los últimos años del secundario** en su numeración de 1 a 12, y qué representa `_1314`. Está en `01_raw_data/Diccionario_BD_Anominizadas.xlsx` y en `docs/data_dictionary.xlsx` del repo.
2. **Si `ssp` está completo en 2024** o hay jurisdicciones que no reportan. Ya vimos un caso así en otro frente: las filas no estaban vacías, no existían.
3. **Qué hacer con los grupos chicos**, donde una sola salida mueve la tasa entera. MEDIDO en el TP2: el quintil más chico tiene mediana de 29 estudiantes y 1,4 veces la dispersión del grande, con valores que llegan a 0,000 y 1,000.

**La limitación que se declara en vez de esquivarse (y va en el informe, no en una charla).** Aprender y el abandono son del **mismo ciclo lectivo**, así que el trabajo habla de **perfiles asociados al abandono**, no de una predicción del futuro. Y hay un sesgo de selección real: **Aprender evalúa a quien fue a rendir ese día**, así que el que ya abandonó no está en la prueba. Esto no es teórico: en el TP2 las inasistencias dieron el signo invertido y la explicación fue exactamente esta.

---

## D3. Toda integración por nombre de departamento se reporta con su denominador

**Estado: DECIDIDA POR IGNACIO el 2026-09-23.** Es una regla de control, no una tarea.

**La decisión.** Cada vez que se peguen dos fuentes por nombre de departamento, el script imprime cuántas filas encontraron par. Vale para el cruce con el Relevamiento Anual y vale para los cruces que ya hicimos.

**Por qué es una decisión y no una obviedad.** Un cruce que no encuentra el par **no da error**: la fila se queda sin datos nuevos o desaparece. El resultado es un dataset que corre, grafica y tiene la misma pinta que uno completo. **Un cruce al 40% y uno al 98% se ven idénticos en pantalla.** La única forma de distinguirlos es contando. Y el motivo es tonto: para la computadora, "GENERAL GUEMES" y "General Güemes" no son el mismo texto.

**Qué imprime, pegado al resultado y no en un comentario.**

- filas nuestras totales y cuántas matchearon, en número y en porcentaje;
- **cuántos estudiantes** representan las que no matchearon (perder una fila de 1.225 no es lo mismo que perder una de 29);
- la lista de las que fallaron, para ver si es un patrón (una provincia entera, los acentos, las abreviaturas tipo "Gral.") o ruido disperso.

**El umbral.** Si el match no alcanza al **95% de los estudiantes**, no se sigue: se normalizan los nombres y se vuelve a medir. Si ni así llega, se reporta como limitación y el análisis se acota a las jurisdicciones que sí cruzan, diciéndolo. No se completa con supuestos ni se deja correr en silencio.

---

## D4. Las dos fuentes no son la misma, y eso es el diferencial del proyecto

**Estado: DECIDIDA POR IGNACIO el 2026-09-23**, con pedido explícito suyo de que quede claro **en el proyecto y en el entregable**.

**La pregunta que lo originó**, de Ignacio: con los mismos datos, cómo sabemos que no terminamos haciendo el mismo proyecto dos veces.

**La respuesta, MEDIDA el 23/09** comparando las columnas de los dos datasets, no por lectura de sus README:

| | Nuestro dataset (Aprender) | El Relevamiento Anual |
|---|---|---|
| Quién contesta | **el estudiante** | **la escuela** |
| Qué mide | cómo le fue y cómo vive | cuántos entraron y cuántos se fueron |
| Desempeño | **sí** | no |
| Abandono | no | **sí** |
| Edificio e infraestructura | no | **sí** |
| Hogar (libros, educación de la madre, NSE) | **sí** | no |

**Se tocan en dos variables y ni ahí son lo mismo**: sobreedad y repitencia. La nuestra es **lo que el chico declara** en la prueba; la de ellos es **el conteo administrativo de la escuela**. Tener las dos versiones no es duplicado: es la oportunidad de contrastar lo que la escuela reporta contra lo que los estudiantes dicen, que es un chequeo de consistencia que pocos trabajos hacen.

**De ahí sale el diferencial, y no depende de comparar nuestro trabajo con el de nadie**: el Relevamiento Anual tiene **el resultado** (cuántos se fueron) y el edificio; Aprender tiene **el contexto de los chicos** (casa, aprendizaje, trayectoria declarada). Le ponemos al resultado un contexto que la fuente administrativa no ve. Un proyecto hecho solo con el Relevamiento Anual no puede hacer esto, porque no tiene Aprender.

**El riesgo, dicho de frente:** si el modelo final termina usando solo variables del Relevamiento Anual, el diferencial desaparece. **Aprender tiene que estar en el análisis**, y si midiendo resulta que no aporta, eso se reporta como hallazgo, no se disimula sacándolo.

### 📄 Texto para el entregable

Esto va en el notebook y en el informe, donde se presentan las fuentes. Que no quede solo acá:

> El proyecto combina dos relevamientos distintos del Ministerio de Educación, que no son versiones del mismo dato. Las **Pruebas Aprender** las responde el estudiante el día de la evaluación: miden su desempeño y describen su hogar, su trayectoria y el clima de su escuela. El **Relevamiento Anual** lo completa la institución: cuenta cuántos alumnos se matricularon, cuántos promovieron y cuántos se fueron sin pase, y describe la infraestructura del edificio.
>
> Ninguno de los dos contiene lo que aporta el otro. Aprender no registra abandono, porque solo observa a quien se presentó a rendir; el Relevamiento Anual no observa desempeño ni contexto familiar. Se superponen únicamente en sobreedad y repitencia, y con definiciones distintas: una es declarada por el estudiante y la otra es el registro administrativo de la escuela, lo que permite usarlas como control de consistencia en lugar de como columnas duplicadas.
>
> Esa complementariedad es lo que habilita la pregunta de este trabajo: describir qué características de los estudiantes y de sus hogares acompañan a las tasas de abandono que registra el sistema educativo.

---

## Lo que esta pasada NO decide

Para que quede claro qué sigue abierto y no parezca cerrado por omisión:

- **Regresión, clasificación o clusterización.** Hay una recomendación en `TP3-PROPUESTA-DEFINICION.md` (regresión, más clusterización como pieza de narrativa), pero la elección es del grupo.
- **Si se releva el pipeline de limpieza de Agustín antes de escribir el nuestro.** Ignacio lo propuso el 23/09 y tiene sentido: leer sus cuatro notebooks, anotar qué haríamos distinto y por qué, para que las diferencias sean deliberadas y no accidentales. Falta decidir quién y cuándo.
- **Quién hace qué**, y la fecha de la videollamada de organización que propuso una compañera el 17/09.
- **Nada de esto está construido.** Al 23/09 no se bajó un solo archivo del Relevamiento Anual ni se corrió el cruce: lo medido son las cabeceras de los datasets, la lista de años y las columnas de nuestro propio dataset.
