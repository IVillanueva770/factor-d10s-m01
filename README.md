# El Factor D10S

Abandono escolar en la secundaria argentina, a partir de datos públicos del Ministerio de Educación y del INDEC.

Grupo M01 · Mentoría Diplodatos 2026 (FAMAF, UNC) · Mentora: Noelia Ferrero

Un solo repositorio para las tres entregas del proyecto, con el pipeline, los datos y los tests compartidos entre todas: cada entrega continúa la anterior en vez de rehacerla.

## Estado de las entregas

| Entrega | Qué es | Estado |
|---|---|---|
| **01 · Dataset maestro** | Construir el dataset analítico combinando las fuentes, con su diccionario y el proceso documentado | ✅ Entregada y aprobada |
| **02 · EDA y curación** | Exploración, decisiones de curación medidas y el informe de hallazgos | ✅ Entregada |
| **03 · Machine Learning** | Definir el problema, elegir el target, modelar y evaluar | 🔄 En diseño. Las decisiones y lo que falta verificar están en `entregas/03-machine-learning/DECISIONES-TP3.md` |

## Las fuentes, que no son lo mismo

El proyecto combina **dos relevamientos distintos del Ministerio de Educación**. Es importante no leerlos como versiones del mismo dato:

- **Pruebas Aprender 2024**: las responde **el estudiante** el día de la evaluación (base censal de 5to y 6to año de secundaria, versión agregada). Miden desempeño en lengua y matemática y describen el hogar, la trayectoria y el clima escolar.
- **Relevamiento Anual**: lo completa **la escuela**. Cuenta matrícula, promovidos, egresados y **salidas sin pase** (el indicador de abandono), y describe la infraestructura del edificio. Entra en la entrega 3.

Ninguno contiene lo que aporta el otro: Aprender no registra abandono, porque solo observa a quien se presentó a rendir, y el Relevamiento Anual no observa desempeño ni contexto familiar. Se superponen únicamente en **sobreedad y repitencia**, y con definiciones distintas (declarada por el estudiante contra registro administrativo), lo que las vuelve un control de consistencia en lugar de columnas duplicadas.

La **EPH** del INDEC se usó en las entregas 1 y 2 como contexto socioeconómico provincial. **Queda fuera de la entrega 3**: es de 2025 mientras el resto de las fuentes es de 2024, sus valores se repiten idénticos en todos los departamentos de una misma provincia y sostenía un proxy de abandono que no funcionó. El detalle, con su evidencia, está en `entregas/03-machine-learning/DECISIONES-TP3.md`.

## Empezá por acá

1. Abrí el notebook de la entrega que te interese, dentro de `entregas/`, en Google Colab y ejecutalo entero. Son autocontenidos: bajan los datos solos, fijados a un commit exacto y verificando el hash de cada archivo. Ahí está todo el razonamiento, en orden y explicado.
2. Si vas a seguir trabajando sobre esto, leé **`PARA-EL-EQUIPO.md`**: el paso a paso, por qué se decidió cada cosa y qué queda por hacer.
3. Si venís a entender el diseño de la entrega 3, empezá por **`entregas/03-machine-learning/DECISIONES-TP3.md`**.

## Estructura

```
mentoria/     Lo que viene de la mentoría: consignas, reglas, devoluciones.
entregas/
  01-dataset-maestro/    notebook entregado y el zip de la entrega
  02-eda-y-curacion/     notebook, informe en PDF y su handoff
  03-machine-learning/   decisiones de diseño, consigna leída y propuesta
docs/         Documentación transversal: pipeline, perfil de calidad,
              relaciones entre variables, decisiones de curación.
pipeline/     El pipeline paso a paso, una carpeta por etapa. COMPARTIDO entre
              las tres entregas.
data/
  processed/  dataset_maestro_inicial.csv  (1.174 filas x 131 columnas)
              diccionario_variables.csv    (una fila por columna del dataset)
              armonizacion_fuentes.csv     (correspondencia entre las fuentes)
  raw/documentacion/  Tablas de referencia que usa el pipeline, con su fuente.
figuras/      Los gráficos en PNG.
tests/        Los invariantes, la red de seguridad del proyecto.
```

## El dataset en tres líneas

Cada fila es un grupo **jurisdicción + departamento + sector de gestión + ámbito**, no un estudiante: las bases de Aprender que se publican son agregadas y no existe una versión a nivel individual. Esto condiciona todo el análisis y está explicado en el notebook.

Las columnas con `__` son **proporciones dentro de la fila** (por ejemplo `sexo__femenino`, `desemp_matematica__avanzado`). Las que empiezan con `cob__` dicen sobre qué fracción de la fila se calculó cada bloque. Las que empiezan con `eph_` son indicadores socioeconómicos **de la provincia**, iguales para todos los departamentos de esa provincia.

En total: **540.040 estudiantes representados, 24 jurisdicciones, 530 departamentos.**

## Correr el pipeline localmente

El notebook alcanza para todo. Si preferís reconstruirlo desde los scripts:

```bash
pip install -r requirements.txt

python pipeline/correr.py              # todas las etapas, en orden
python pipeline/correr.py --listar     # qué hace cada etapa, sin correr
python pipeline/correr.py --desde 4    # de la etapa 4 en adelante
python pipeline/correr.py --verificar  # corre dos veces y compara los hashes
python tests/test_invariantes.py       # la red de verificación
```

**`--verificar` es el que importa.** Corre el pipeline entero dos veces seguidas y compara los SHA-256 de las salidas. Si dan iguales, el pipeline es reproducible y se puede confiar en que un cambio en un número viene de un cambio en el código o en los datos, no del azar.

**`tests/test_invariantes.py` es la red de seguridad**: convierte en verificación cada afirmación que el análisis hace sobre los datos. Si alguien toca el pipeline y rompe algo que antes valía, falla ahí en vez de producir un dataset mal en silencio. Correrlo antes de dar cualquier cambio por bueno.

## Fuentes

- **Pruebas Aprender 2024**, base censal de secundaria (5to y 6to año), versión agregada. Secretaría de Educación, [datos.gob.ar](https://datos.gob.ar/dataset/aprender-2024).
- **Relevamiento Anual**, Ministerio de Educación. Se incorpora en la entrega 3.
- **EPH**, 3er trimestre de 2025, bases de Hogar e Individual del INDEC (entregas 1 y 2).
- **Códigos de aglomerado**: INDEC, *Diseño de Registro y Estructura para las bases de microdatos*, [PDF](https://www.indec.gob.ar/ftp/cuadros/menusuperior/eph/EPH_diseno_reg_t414.pdf).

Los datos crudos no se versionan porque pesan 45 MB y son públicos: el pipeline los baja solo.

## Referencias

- Repositorio de la mentoría: [NoeliaFerrero/Proyecto_Mentoria_FAMAF_2026](https://github.com/NoeliaFerrero/Proyecto_Mentoria_FAMAF_2026).
- [agus476/radar-trayectorias-educativas-argentinas](https://github.com/agus476/radar-trayectorias-educativas-argentinas): proyecto sobre trayectorias educativas y abandono construido con el Relevamiento Anual. Se usa como referencia para incorporar esa fuente.
