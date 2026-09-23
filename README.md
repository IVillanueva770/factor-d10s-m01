# El Factor D10S

Proyecto de la mentoría M01: abandono escolar en la escuela secundaria argentina,
a partir de datos públicos del Ministerio de Educación. Un solo repositorio para
las tres entregas, con el pipeline y los datos compartidos entre todas.

Grupo M01 · Mentoría Diplodatos 2026 (FAMAF, UNC) · Mentora: Noelia Ferrero

## Empezá por acá

1. Abrí el notebook de la entrega que te interese, dentro de `entregas/`, en
   Google Colab y ejecutalo entero. Se baja los datos solo y tarda unos minutos. Ahí está
   todo el razonamiento, en orden y explicado.
2. Si vas a seguir trabajando sobre esto, leé **`PARA-EL-EQUIPO.md`**: tiene el
   paso a paso, por qué se decidió cada cosa y qué queda por hacer.

## Las fuentes del proyecto (leer antes de tocar el dataset)

El proyecto combina **dos relevamientos distintos del Ministerio de Educación**, que no son versiones del mismo dato:

- **Pruebas Aprender 2024**: las responde **el estudiante** el día de la evaluación. Miden desempeño y describen hogar, trayectoria y clima escolar.
- **Relevamiento Anual 2024**: lo completa **la escuela**. Cuenta matrícula, promovidos, egresados y **salidas sin pase** (el indicador de abandono), y describe la infraestructura del edificio.

Ninguno contiene lo que aporta el otro: Aprender no registra abandono (solo ve a quien se presentó a rendir) y el Relevamiento Anual no ve desempeño ni contexto familiar. Se superponen solo en **sobreedad y repitencia**, y con definiciones distintas (declarada por el estudiante contra registro administrativo), lo que las vuelve un control de consistencia y no columnas duplicadas.

La **EPH** que usó el TP1 quedó fuera del TP3: es de 2025 mientras el resto es de 2024, sus valores son por provincia y sostenía un proxy de abandono que no funcionaba. El detalle, con su evidencia, está en **`docs/DECISIONES-TP3.md`**.

## Qué hay en cada carpeta

```
mentoria/     Lo que viene de la mentora: consignas, reglas, devoluciones.
entregas/
  01-dataset-maestro/    TP1: notebook entregado y el zip de la entrega
  02-eda-y-curacion/     TP2: notebook, informe en PDF y su handoff
  03-machine-learning/   TP3: decisiones de diseño, consigna leída y propuesta
docs/         Documentación transversal: pipeline, calidad, relaciones, curación.
data/
  processed/  dataset_maestro_inicial.csv  (1.174 filas x 131 columnas)
              diccionario_variables.csv    (una fila por columna del dataset)
              armonizacion_fuentes.csv     (correspondencia entre las fuentes)
  raw/
    documentacion/  Las tablas de referencia que usa el pipeline, con su fuente
figuras/      Los gráficos en PNG
pipeline/     El pipeline paso a paso, un script por etapa. COMPARTIDO entre
              las tres entregas: el TP3 no lo rehace, lo continúa.
tests/        Los invariantes que se corren antes de entregar
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
