# Inventario de datos: qué tenemos realmente para el TP1

> Medido el 2026-08-07 bajando y abriendo cada archivo del repo `NoeliaFerrero/Proyecto_Mentoria_FAMAF_2026` (rama `main`). Nada de esto sale del README ni de la consigna: sale de contar filas y columnas.

## Resumen en una línea

Tenemos **Aprender 2022 y 2024 en su versión AGREGADA** (1.175 filas = departamento x sector x ámbito, ~1.030 columnas) y **la EPH de 2025 (T1, T2 y T3)** a nivel hogar y persona. Ni la unidad de análisis ni el año coinciden con lo que pide la consigna, y eso condiciona todo el diseño del entregable.

---

## 1. Pruebas Aprender (fuente principal)

Ubicación: `data/raw/`. Seis archivos CSV, tres por año.

| Año | Archivo | Filas de datos | Columnas |
|---|---|---|---|
| 2024 | `Agregada - Desempeños de Lengua(in).csv` | 1.175 | 1.035 |
| 2024 | `Agregada - Desempeños de Matematica(in).csv` | 1.175 | 1.035 |
| 2024 | `Agregada - Solo CC(in).csv` | 1.175 | 1.031 |
| 2022 | los mismos tres, misma estructura | | |

**Formato**: separador `;`, encoding `latin-1`, decimales con coma. Hay que declararlo en el `read_csv` o pandas devuelve una sola columna de texto.

**Unidad de análisis real**: las cuatro primeras columnas son `jurisdiccion`, `departamento`, `sector`, `ambito`. Las 1.175 filas son combinaciones únicas de esas cuatro (verificado: 1.175 combos distintos sobre 1.175 filas). Cobertura: **24 jurisdicciones, 530 departamentos**; 871 filas estatales y 304 privadas; 712 urbanas y 463 rurales.

**Qué hay en las ~1.030 columnas restantes**: cada columna es una categoría de respuesta de una pregunta del cuestionario, y el valor es un **conteo expandido por peso muestral** (números decimales tipo `144,2798953`), no una respuesta individual. Es decir: `ap03_Femenino` no dice "esta persona es mujer", dice "en este departamento-sector-ámbito hay ~144 estudiantes mujeres".

**Variables que la consigna pide y que sí están** (como bloques de columnas):
- Territorio: `jurisdiccion`, `departamento`, `sector`, `ambito`
- Estudiante: `edadA_junio2024_*` (11 categorías), `ap03_*` (sexo), `sobreedad_*` (6 categorías)
- Rendimiento: `ldesemp_*` y `mdesemp_*` (Por debajo del nivel básico / Básico / Satisfactorio / Avanzado)
- Contexto: `NSE_nivel_Q1..Q5`, `clima_Bajo/Medio/Alto`, `Nivel_Ed_Madre_*`, `Nivel_Ed_Padre_*`, `Nivel_Ed_Persona_Resp_*`, `repitencia_*`, `migracion_*`
- Del cuestionario, según el diccionario: `ap08` tamaño del hogar, `ap15` cantidad de libros, `ap22` horas de estudio, `ap26` inasistencias

O sea: **las doce variables que pide el enunciado existen todas**, pero como distribuciones agregadas, no como valores por estudiante.

**Diccionarios disponibles**:
- `data/raw/2011 - 2024 - Diccionario bases aprender anonimizadas(2022 Estudiantes - APRENDER).csv` (206 KB): el diccionario oficial, pero es el del microdato **a nivel estudiante de 2022**, que no está en el repo.
- `data/raw/Que representa en simple ... .txt`: tabla legible que traduce cada bloque `apXX` a lenguaje humano. Es lo más útil para elegir variables rápido.
- `data/cleaned/diccionario_para_cruce_eph.csv`: mapeo de variable a `variable_estandar` + `dimension`. **Cuidado: tiene errores de mapeo evidentes.** Ejemplos medidos: `ap29j` (impacto de la pandemia en los aprendizajes) está etiquetada como `edad`, y `apa34h` (proyectos al terminar el secundario) como `trabaja`. Sirve como punto de partida, no como fuente de verdad.
- `data/cleaned/diccionario_reducido_final.csv`: solo 7 filas, con columnas `keep` y `concepto`. Alguien empezó a filtrar y quedó a mitad de camino.

---

## 2. Encuesta Permanente de Hogares (fuente de contexto)

| Archivo | Contenido | Filas | Columnas |
|---|---|---|---|
| `EPH_usu_3_Trim_2025_xls.zip` | `usu_hogar_T325.xlsx` | 15.860 hogares | 98 |
| | `usu_individual_T325.xlsx` | 44.946 personas | 235 |
| `usu_individual_T225.xlsx` | individual 2do trim 2025 | 46.086 personas | 235 |
| `usu_individual_T125.xlsx` | individual 1er trim 2025 | (mismo formato) | 235 |

Verificado en los datos: `ANO4 = 2025`, `TRIMESTRE = 3` (y 2 para el T225). **No hay ningún archivo de 2024 en el repo.**

**Claves y geografía**: `CODUSU` + `NRO_HOGAR` unen hogar con personas; `COMPONENTE` identifica a la persona dentro del hogar. La geografía disponible es `REGION` y `AGLOMERADO`: **32 aglomerados**, no departamentos ni provincias directamente.

**Variables útiles ya identificadas**: `CH06` (edad), `CH04` (sexo), `NIVEL_ED`, `ESTADO` (condición de actividad), `CAT_OCUP`, `PONDERA` (peso), más todo el bloque `IV*`/`II*` de vivienda y hacinamiento en la base de hogar, y los ingresos en la de personas.

**Población objetivo medida**: en el 3T-2025 hay **5.025 personas de 12 a 18 años** sobre 44.946 filas.

---

## 3. Las tres paredes, y por qué importan antes de escribir código

### Pared 1: la consigna pide nivel estudiante y los datos son agregados

El enunciado dice "construir un dataset analítico **a nivel estudiante**" y la matriz de integración del `deliverable_1_data_pipeline/README.md` dice explícitamente "¿Qué representa una fila? Un estudiante evaluado". **Los archivos que están en el repo no permiten eso**: la fila mínima es departamento x sector x ámbito. No es un problema de limpieza, es la granularidad del archivo.

Dos salidas posibles:
- **(a)** Bajar el microdato de Aprender a nivel estudiante desde datos.gob.ar (existe, el diccionario del repo es justamente el de esa base para 2022) y trabajar como pide el enunciado.
- **(b)** Aceptar que la unidad de análisis del proyecto es el **departamento x sector x ámbito** y redefinir el objetivo en esos términos.

Esto lo decide el equipo con la mentora, no se resuelve en el notebook.

### Pared 2: los años no coinciden

La consigna es explícita: Aprender 2024 (aplicada en octubre) + **EPH 3er trimestre de 2024**, "por ser la medición más cercana temporalmente". En el repo está la **EPH 2025**. O bien se baja la de 2024 del INDEC, o bien se documenta y justifica el cambio. La segunda opción debilita justo el argumento que el propio enunciado usa para elegir el trimestre.

### Pared 3: el nivel geográfico común es la provincia, y hay que construirlo

Aprender llega a departamento (530). La EPH llega a aglomerado (32) y región (6). **No hay ninguna clave común**: hay que mapear aglomerado a provincia a mano, y ahí aparece el caso feo del Gran Buenos Aires, que cruza CABA y provincia de Buenos Aires. Además, con 32 aglomerados sobre 24 jurisdicciones, **varias provincias van a quedar con un solo aglomerado representándolas y algunas con ninguno**: el indicador socioeconómico contextual va a ser mucho más grueso de lo que la consigna sugiere.

### Bonus: dónde está la variable objetivo

`data/README.md` dice que el objetivo `abandono_escolar` se crea filtrando **12 a 18 años** y consolidando por trimestre, o sea **sobre la EPH, no sobre Aprender**. Eso es coherente (Aprender solo ve a quien rindió, no a quien se fue), pero tiene una consecuencia grande: **el target vive en una base y los predictores en otra, y no se pueden unir a nivel individuo.** Es la tensión central del proyecto y conviene decirla en la conclusión del TP1 en vez de descubrirla en el TP3.

---

## 4. Lo que ya está resuelto y no hay que rehacer

- La estrategia de integración conceptual está escrita por la mentora en `deliverables/deliverable_1_data_pipeline/README.md`: Aprender es la fuente principal, la EPH aporta indicadores contextuales agregados, no hay merge a nivel individuo.
- `requirements.txt` fija el stack: pandas, numpy, matplotlib, seaborn, scikit-learn, jupyter, xgboost, lightgbm.
- La estructura de carpetas del repo ya está armada (`data/raw`, `data/processed`, `data/cleaned`, `notebooks`, `src`, `deliverables`). `notebooks/` y `src/` están vacíos.
- Hay un repo de referencia con el mismo objetivo y otros datos que pasó la mentora: `github.com/agus476/radar-trayectorias-educativas-argentinas`. Uno de sus autores se ofreció a sumarse a los encuentros.
