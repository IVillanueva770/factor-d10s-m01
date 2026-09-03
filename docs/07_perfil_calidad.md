# Perfil de calidad del dataset maestro

Generado por `pipeline/03_curacion/07_perfilado.py`. **Mide, no corrige.**
Las decisiones de curacion se toman mirando esto y se aplican en la etapa 08.

## El dataset

- **1,174 filas x 131 columnas**
- Cada fila es un grupo *jurisdiccion x departamento x sector x ambito*, no un estudiante.
- Estudiantes representados: **540,040**

### Columnas por familia

| Familia | Columnas | Que son |
|---|---|---|
| `proporcion` | 85 | reparto de una poblacion dentro de la fila (suman 1 por bloque) |
| `cobertura` | 16 | que fraccion de la fila quedo representada en ese bloque |
| `contexto_provincial` | 16 | indicador de la EPH, **igual para toda la provincia** |
| `armonizada` | 8 | llevada a escala comparable entre Aprender y la EPH |
| `clave` | 4 | identifican la fila |
| `peso` | 1 | cuantos estudiantes representa la fila |
| `control` | 1 | bandera derivada para analisis de sensibilidad (es rara a proposito) |

## Hallazgos

Cada chequeo con su denominador. `ok` = el chequeo corrio y no encontro nada.

### [ALTA] columna constante o vacia

**1 de 110**. un solo valor (o ninguno) en las 1.174 filas: no aporta nada a ningun modelo.

- `cob__sexo`

### [MEDIA] bloque con cobertura menor al 50%

**2 de 16**. la proporcion es real pero se calculo sobre menos de la mitad de los estudiantes de esa fila: el numero existe y significa poco.

- `cob__clima_escolar (91 filas bajo 50%)`
- `cob__educ_padre (1 filas bajo 50%)`

### [BAJA] columna con valores extremos (3x IQR)

**75 de 94**. valores muy lejos del cuerpo de la distribucion. NO son necesariamente errores: pueden ser departamentos chicos.

- `edad__21_anos (138)`
- `estudiantes (101)`
- `edad__mas_de_22_anos (72)`
- `edad__16_anos (63)`
- `sobreedad__menores_de_17_anos (63)`
- `edad__20_anos (51)`
- `educ_madre__no_fue_a_la_escuela (50)`
- `asistio_jardin__no_no_fui_al_jardin (45)`
- `inasistencias__ninguna_falta (32)`
- `sobreedad__3_anos_o_mas_de_sobreedad_20_anos_o_mas_30jun (32)`
- `tamano_hogar__vivo_solo (27)`
- `tamano_hogar__10_o_mas (27)`

### [ok] clave territorial duplicada

**0 de 1174**. cada fila tiene que ser un jurisdiccion x departamento x sector x ambito unico; si se repite, el dataset cuenta el mismo grupo dos veces.

### [ok] fila completa duplicada

**0 de 1174**. filas identicas en las 131 columnas.

### [ok] proporcion fuera de [0,1]

**0 de 109**. una proporcion negativa o mayor que 1 es imposible por definicion.

### [ok] bloque de proporciones que no suma 1

**0 de 18**. cada bloque reparte el 100% de una poblacion; si no suma 1 se perdio o se duplico una categoria.

### [ok] columna con muchos faltantes

**0 de 131**. mas del 30% de las filas sin dato.

### [ok] columna casi constante

**0 de 110**. un mismo valor en mas del 99% de las filas.

### [ok] categoria con formato inconsistente

**0 de 4**. espacios al borde o valores que solo difieren en mayusculas: hacen que un join o un group by parta el mismo grupo en dos.

### [ok] fila sin ninguna variable analitica

**0 de 1174**. una fila sin ninguna proporcion no aporta al analisis.

## Lo que este perfil NO puede ver

- No sabe si un valor es **correcto**, solo si es **posible**.
- No compara contra los datos crudos: eso lo hacen los 41 invariantes de `tests/test_invariantes.py`.
- Los extremos se detectan con rango intercuartil, que asume una sola poblacion. Este dataset mezcla departamentos de tamanos muy distintos, asi que un extremo puede ser simplemente un departamento chico.
- Que una columna no tenga faltantes no significa que represente bien a los estudiantes de la fila: eso lo dicen las columnas `cob__`.

