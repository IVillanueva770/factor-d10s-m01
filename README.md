# El Factor D10S: entregable 1

Dataset maestro que combina las Pruebas Aprender 2024 con la Encuesta
Permanente de Hogares, más el diccionario de variables y el proceso documentado
para rehacerlo.

Grupo M01 · Mentoría Diplodatos 2026 (FAMAF, UNC) · Mentora: Noelia Ferrero

## Empezá por acá

1. Abrí **`notebooks/TP1_dataset_maestro_El_Factor_D10S.ipynb`** en Google Colab
   y ejecutalo entero. Se baja los datos solo y tarda unos minutos. Ahí está
   todo el razonamiento, en orden y explicado.
2. Si vas a seguir trabajando sobre esto, leé **`PARA-EL-EQUIPO.md`**: tiene el
   paso a paso, por qué se decidió cada cosa y qué queda por hacer.

## Qué hay en cada carpeta

```
notebooks/    El entregable. Autocontenido: no hay que subir ni montar nada.
data/
  processed/  dataset_maestro_inicial.csv  (1.174 filas x 131 columnas)
              diccionario_variables.csv    (una fila por columna del dataset)
              armonizacion_fuentes.csv     (correspondencia entre las fuentes)
  raw/
    documentacion/  Las tablas de referencia que usa el pipeline, con su fuente
figuras/      Los tres gráficos en PNG
src/          El pipeline paso a paso, un script por etapa
```

## El dataset en tres líneas

Cada fila es un grupo **jurisdicción + departamento + sector de gestión +
ámbito**, no un estudiante: las bases de Aprender que se publican son agregadas
y no existe una versión a nivel individual (está explicado en el notebook).

Las columnas con `__` son **proporciones dentro de la fila** (por ejemplo
`sexo__femenino`, `desemp_matematica__avanzado`). Las que empiezan con `cob__`
dicen sobre qué fracción de la fila se calculó cada bloque. Las que empiezan con
`eph_` son indicadores socioeconómicos **de la provincia**, iguales para todos
los departamentos de esa provincia.

En total, 540.040 estudiantes representados, 24 jurisdicciones, 530
departamentos.

## Correr el pipeline localmente

El notebook alcanza para todo. Si preferís los scripts sueltos:

```bash
pip install -r requirements.txt
python src/06_construir_aprender.py    # tabla de Aprender
python src/09_explorar_eph.py          # une hogares y personas
python src/12_indicadores_eph.py       # indicadores por provincia
python src/13_dataset_maestro.py       # el cruce
python src/15_armonizar.py             # escala común entre fuentes
python src/14_diccionario.py           # diccionario
python src/16_graficos.py              # figuras
python src/test_invariantes.py         # verifica las 41 propiedades
```

Los scripts numerados del 01 al 05, el 07 y el 08 son las exploraciones que
llevaron a las decisiones. No hace falta correrlos para reconstruir el dataset,
pero están porque contienen las mediciones que justifican cada elección.

`src/test_invariantes.py` es la red de seguridad: convierte en verificación
cada afirmación que el análisis hace sobre los datos. Si tocás el pipeline y
rompés algo que antes valía, falla ahí en vez de producir un dataset mal en
silencio. Corré eso antes de dar cualquier cambio por bueno.

## Fuentes

- **Pruebas Aprender 2024**, base censal de secundaria 5to y 6to año, versión
  agregada. Publicadas por la Secretaría de Educación en
  [datos.gob.ar](https://datos.gob.ar/dataset/aprender-2024).
- **EPH**, 3er trimestre de 2025, bases de Hogar e Individual del INDEC.
- **Códigos de aglomerado**: INDEC, *Diseño de Registro y Estructura para las
  bases de microdatos*,
  [PDF](https://www.indec.gob.ar/ftp/cuadros/menusuperior/eph/EPH_diseno_reg_t414.pdf).

Los datos crudos no viajan en este paquete porque pesan 45 MB y son públicos: el
notebook los baja del repositorio de la mentoría, fijados a un commit exacto y
verificando el hash de cada archivo.
