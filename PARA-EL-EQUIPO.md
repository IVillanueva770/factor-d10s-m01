# Para el equipo: cómo está armado esto y cómo seguir

Este documento es para que puedan retomar el trabajo sin tener que reconstruir
el razonamiento. Está el paso a paso, por qué se decidió cada cosa, y qué queda
por hacer.

Si solo tenés diez minutos, leé "Las cinco cosas que hay que saber" y saltá al
final, a "Qué falta".

---

## Las cinco cosas que hay que saber

**1. Una fila no es un estudiante.** Buscamos el microdato individual de
Aprender y no existe publicado: los cinco años del portal traen únicamente
bases agregadas, porque la agregación es el método de anonimización del
Ministerio. La unidad mínima que tenemos es
`jurisdicción + departamento + sector + ámbito`. Esto contradice lo que dice la
consigna y la matriz de integración, y es lo primero que hay que conversar con
Noelia.

**2. Los números vienen expandidos.** Cada valor es la suma de los pesos de
varios estudiantes, no un conteo. Por eso tienen decimales. Y como cada base de
Aprender trae su propio factor de expansión, los conteos de un archivo y otro no
son comparables: por eso todo está convertido a proporciones.

**3. El único punto de contacto entre las fuentes es la provincia.** Aprender
llega a departamento (530), la EPH llega a aglomerado (32), y no hay ninguna
clave común. Todos los departamentos de una provincia comparten el mismo
contexto socioeconómico. La mediana nacional es de 79 estudiantes de Aprender
por cada adolescente encuestado en la EPH, y en CABA son 306.

**4. Aprender no puede ver el abandono.** A la evaluación solo va quien está
escolarizado. El fenómeno que el proyecto quiere predecir es, por construcción,
invisible en la fuente principal. Los predictores están en Aprender y la
variable objetivo tiene que venir de otro lado.

**5. Un vacío casi nunca es un cero.** Es el error que más veces cometimos.
Está explicado en detalle más abajo.

---

## El pipeline, paso a paso

Cada paso es un script en `src/`. Los que están marcados con asterisco son
exploraciones: no construyen nada, pero contienen las mediciones que
justifican las decisiones.

| # | Script | Qué hace |
|---|---|---|
| 01* | `01_explorar_aprender.py` | Compara las tres bases de Aprender entre sí |
| 02* | `02_test_poblaciones.py` | Mide por qué difieren en las mismas celdas |
| 03* | `03_cerrar_aprender.py` | Verifica que desempeño y cuestionario compartan población |
| 04* | `04_lengua_vs_matematica.py` | Cuantifica la discrepancia del par que sí unimos |
| 05* | `05_inventario_bloques.py` | Reconstruye el cuestionario desde los nombres de columna |
| 06 | `06_construir_aprender.py` | **Tabla de Aprender en proporciones** |
| 07* | `07_auditar_nan.py` | Determina qué significan los valores vacíos |
| 08* | `08_test_condicionadas.py` | Mide la cobertura real de cada bloque |
| 09 | `09_explorar_eph.py` | **Une hogares con personas** |
| 10 | `10_extraer_aglomerados.py` | Extrae los aglomerados del PDF del INDEC |
| 11 | `11_puente_geografico.py` | **Construye y mide el puente a provincia** |
| 12 | `12_indicadores_eph.py` | **Indicadores socioeconómicos por provincia** |
| 13 | `13_dataset_maestro.py` | **El cruce** |
| 14 | `14_diccionario.py` | Genera el diccionario leyendo el dataset |
| 15 | `15_armonizar.py` | Escala común de nivel educativo entre fuentes |
| 16 | `16_graficos.py` | Las tres figuras |
| 17 | `17_generar_notebook.py` | Genera el notebook de entrega |
| test | `test_invariantes.py` | **Verifica las 41 propiedades del pipeline** |

---

## Las decisiones, y por qué

### De las tres bases de Aprender usamos dos

Las tres traen las mismas 1.175 filas, pero **537 de las 1.027 columnas
compartidas tienen valores distintos** según el archivo. Primero pensamos que
eran poblaciones anidadas; lo medimos y no era (si lo fuera, "Solo CC" sería
siempre la base más grande, y lo es en 495 filas de 1.175).

La respuesta está en el documento metodológico del Ministerio: cada base está
ponderada por el factor de expansión de **su** cuestionario, y el propio
Ministerio dice que hay que usar la base que corresponda al análisis.

Entonces: el cuestionario y el desempeño en Lengua salen de la base de Lengua,
el desempeño en Matemática sale de la suya, y **"Solo CC" se descarta** (no
aporta ninguna columna propia y es la que se comporta distinto). Entre Lengua y
Matemática la discrepancia mediana es 0,16% y solo 5 filas superan el 10%: esas
quedan marcadas con `flag_discrepancia_bases`.

### Todo en proporciones, con su cobertura al lado

Como los conteos no son comparables entre bases, cada bloque de preguntas se
convierte a proporciones que suman 1 dentro de la fila. El denominador son
quienes respondieron esa pregunta, y ese denominador queda guardado en las
columnas `cob__*`.

Vale la pena mirarlas: ocho bloques tienen cobertura del 100% en todas las
filas, pero `clima_escolar` tiene 87,3% de mediana y 96 filas sin ningún dato.

**No pusimos un flag binario de "fila poco confiable"** a propósito. Probamos
umbrales del 90% al 50% y la cantidad de filas marcadas baja de forma continua
(68%, 51%, 39%, 31%, 25%, 14%, 8%) sin ningún escalón: no hay una cola separable
de filas malas. Cualquier corte sería arbitrario y se lo estaríamos imponiendo,
invisible, a quien use la tabla. Quedan las columnas continuas y cada análisis
elige su corte y lo justifica.

### Sacamos la educación del referente

`Nivel_Ed_Persona_Resp` es **condicional**: solo aplica cuando el referente del
estudiante no es la madre ni el padre. Cubre el 16,6% de los casos (mediana) y
baja al 1,7% en el peor departamento. Sus proporciones no describen a la
población sino a un subconjunto muy particular.

Se puede recuperar en el TP2, pero leyéndola al revés: como indicador de "no
convive con sus padres", que es su sentido útil.

### La clave de la EPH es CODUSU + NRO_HOGAR

La consigna dice unir por `CODUSU`. `CODUSU` identifica la **vivienda**, y hay
**77 viviendas con más de un hogar** adentro. Uniendo solo por ahí, esas filas
se multiplican.

En el código está `validate="many_to_one"` en el merge, que hace que pandas tire
error si el join multiplicara filas. Dejen esa guarda puesta.

### Los ingresos se ponderan distinto

`PONDERA` expande personas. Para ingresos hay que usar **`PONDIH`**.

El 27,5% de las personas figura con ingreso per cápita en 0, y de esas el 98,8%
tiene `PONDIH = 0`: el INDEC ya las marcó como "no usar para ingresos". Con
`PONDERA`, esas personas entran con peso completo y un cero que no es un ingreso
sino una no respuesta, y Buenos Aires aparecía como la provincia de menor
ingreso del país (140.250 en vez de 445.000).

La columna `eph_sin_dato_ingreso` está para que nadie lea la mediana sin ver
sobre qué fracción se calculó: en Chaco y Misiones más de la mitad de la muestra
no declara ingresos.

### Los dos aglomerados que cruzan provincia

`38 San Nicolás - Villa Constitución` (Buenos Aires y Santa Fe) y
`93 Viedma - Carmen de Patagones` (Río Negro y Buenos Aires) se asignaron a la
provincia de su localidad principal. Pesan juntos el 0,96% de la muestra.

El caso de Viedma importa más de lo que su tamaño sugiere: es el **único**
aglomerado de Río Negro, así que excluirlo borraría la provincia del dataset.

La tabla está en `data/raw/documentacion/aglomerado_provincia.csv`. Si quieren
cambiar el criterio, editan esa fila y vuelven a correr: no hay que tocar código.

---

## El error que más veces cometimos

Los valores ausentes, tratados como ceros. Nos pasó tres veces de formas
distintas y vale la pena tenerlo presente:

1. **En Aprender**, un vacío sí es un cero, pero eso hubo que demostrarlo. El
   valor mínimo de toda la matriz es 1,0000 y hay 2.140 valores por debajo de 2,
   así que el Ministerio no suprime celdas chicas; y los bloques censales cierran
   exacto aun con celdas vacías, lo que solo puede pasar si valen cero.

2. **En las comparaciones**, `NaN == NaN` da `False` en pandas. Tres pares de
   variables de la EPH parecían coincidir solo en el 48% de las filas y estuvimos
   por reportar que el INDEC publica datos inconsistentes. Contando los vacíos
   como coincidencia, dan 100%.

3. **En los ingresos**, un cero significa "no contestó" y no "no tiene". Está
   explicado arriba.

Hay un cuarto caso, que no es de vacíos pero es del mismo tipo. Construimos un
indicador de no respuesta sumando las columnas `Blanco`, `No_disponible` y
`Multimarca`. Daba **0,00% en los diecisiete bloques**, o sea calidad perfecta.
Esas columnas están vacías en el 100% de sus 10.575 celdas: el indicador no
podía dar otra cosa. Un verificador que da verde por construcción es peor que no
tener ninguno, porque su verde se lee como garantía. Lo reemplazamos por la
cobertura, que sí varía y sí puede fallar.

---

## Qué falta

### Para cerrar esta entrega

Nada bloqueante. El dataset, el diccionario y el notebook están. Lo que
convendría revisar entre todos antes de mandarlo:

- **Preguntarle a Noelia por los dos desfasajes**: que el microdato a nivel
  estudiante no existe (y que por eso la unidad de análisis cambió), y que la
  EPH del repositorio es de 2025 cuando la consigna pide la de 2024.
- Leer las conclusiones del notebook y ver si están de acuerdo con cómo quedó
  contado.

### Para el TP2, en orden de valor

**1. Traer la variable objetivo oficial.** El Ministerio publica un dataset
llamado `Indicadores Educativos` con las tasas de Promoción Efectiva,
Repitencia, **Abandono Interanual**, Sobreedad y Escolarización, por nivel de
enseñanza y jurisdicción, de 2012 a 2025. Es exactamente el target que el
proyecto necesita, al mismo nivel geográfico que ya estamos usando y calculado
por la fuente oficial en vez de derivado por nosotros. El archivo baja bien
(235 KB, formato RAR). También existe `Base de Datos por Escuela`, con abandono
a nivel establecimiento, que permitiría bajar de provincia a escuela.

**2. Conseguir el diccionario 2024 de Aprender.** El que está en el repositorio
es de 2022 y usa otra numeración. Con el correcto se pueden identificar dos
bloques que hoy quedaron afuera:
   - `ap21` y `ap22`: horas semanales dedicadas a distintas actividades. Una de
     las diez subpreguntas es trabajar fuera del hogar, que probablemente sea el
     mejor predictor individual de abandono que tienen estos datos.
   - `ap11`: tiene las mismas categorías que el tamaño del hogar pero sin la
     opción "Vivo solo". Puede ser hermanos o habitaciones.

**3. Validar las cuatro variables que agregamos por criterio.** `repitencia`,
`clima_escolar`, `migracion` y `asistio_jardin` no las pide la consigna: las
incorporamos porque nos parecieron relevantes, y eso está declarado como tal en
el diccionario. Cuando haya variable objetivo se puede medir si predicen algo.
Si no, se sacan.

**4. Decidir qué hacer con la agregación provincial.** Es la limitación más
fuerte del dataset. Dos caminos posibles: bajar de nivel usando la Base de Datos
por Escuela, o aceptar la provincia como unidad y trabajar con menos de 24
observaciones, que para modelar es muy poco.

---

## Lo que ya está medido y no hace falta rehacer

Por si sirve para el informe final, estos números salieron de correr el
pipeline y están todos reproducidos en el notebook:

- 1.174 filas, 131 columnas, 540.040 estudiantes representados
- 24 jurisdicciones, 530 departamentos
- Ingreso mediano provincial contra desempeño por debajo del básico en
  Matemática: **r = -0,82**. Robusto: -0,73 sin CABA, -0,73 sin CABA ni Buenos
  Aires, -0,71 excluyendo las provincias con más de 20% sin dato de ingreso, y
  -0,85 por Spearman
- El proxy de abandono contra ese mismo desempeño: **r = +0,16**, o sea nada
- Sobreedad: 23% en estatal urbano, 22% en estatal rural, 12% en privado rural,
  **7% en privado urbano**. La brecha es de gestión, no de ámbito
- Nivel educativo de las madres según Aprender contra el de los adultos según la
  EPH, por provincia: **r = 0,674**. Dos encuestas independientes sobre
  poblaciones distintas ordenan las provincias casi igual, y es la única
  validación empírica que tenemos de que el puente geográfico funciona
