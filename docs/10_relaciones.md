# Relaciones en el dataset curado

Generado por `pipeline/04_analisis/10_relaciones.py` sobre `dataset_maestro_curado.csv`.

## Como leer estos numeros

**Cada fila del dataset es un grupo, no un estudiante**: una fila puede representar 29 estudiantes o 1.225. Por eso todo promedio de este informe esta **ponderado por cantidad de estudiantes**. Un promedio simple hablaria de departamentos y no de chicos.

**Las correlaciones con indicadores de la EPH se calculan a nivel provincia (24 puntos), no a nivel fila.** Los valores de la EPH se repiten identicos en todos los departamentos de una provincia, asi que las 1.174 filas no son observaciones independientes: calcular sobre ellas inflaria el n sin agregar informacion. Es la trampa mas facil de este dataset.

**Son correlaciones ecologicas.** Valen entre agregados territoriales y no autorizan a concluir nada sobre un estudiante concreto.

🔴 **Y lo mas importante: el dataset no tiene una variable de abandono.** El proxy construido en el TP1 desde la EPH correlaciona +0,16 con el desempenio, o sea que no mide lo que dice medir. Todo lo que sigue describe **desempenio y sobreedad**, que son antecedentes plausibles del abandono, no el abandono. Conseguir el target real es el problema abierto que este TP deja planteado para el TP3.

## Brecha por sector de gestion y ambito

| sector   | ambito   |   filas |   estudiantes |   desemp_matematica__por_debajo_del_nivel_basico |   desemp_lengua__por_debajo_del_nivel_basico |   sobreedad__3_anos_o_mas_de_sobreedad_20_anos_o_mas_30jun |   repitencia__repitio_1_vez |   edad__mas_de_22_anos |
|:---------|:---------|--------:|--------------:|-------------------------------------------------:|---------------------------------------------:|-----------------------------------------------------------:|----------------------------:|-----------------------:|
| Estatal  | Urbano   |     444 |  327,878.4413 |                                           0.6170 |                                       0.2660 |                                                     0.0212 |                      0.1701 |                 0.0047 |
| Privado  | Urbano   |     268 |  176,881.0032 |                                           0.3841 |                                       0.1264 |                                                     0.0062 |                      0.0537 |                 0.0041 |
| Estatal  | Rural    |     426 |   31,601.1011 |                                           0.6754 |                                       0.3373 |                                                     0.0285 |                      0.1648 |                 0.0054 |
| Privado  | Rural    |      36 |    3,679.4548 |                                           0.5108 |                                       0.2198 |                                                     0.0133 |                      0.0936 |                 0.0041 |

**Dentro del mismo ambito urbano, cambiar de sector mueve el desempenio 0.23 puntos** (estatal 0.62 contra privado 0.38). Cambiar de ambito dentro de privado lo mueve 0.13. **El sector pesa mas que el lugar.**

Este titular se apoya en las dos celdas urbanas a proposito, porque entre las dos suman 504,759 estudiantes, el 93.5% del total.

*Dato de color, con su denominador:* un estudiante de estatal urbana (0.62) esta peor que uno de privada RURAL (0.51), o sea que el campo no es lo que lo hunde. Es la comparacion mas ilustrativa y la mas fragil: privada rural son 36 filas y 3,679 estudiantes, el 0.7% del total, y es ademas la celda con mayor dispersion (ver el analisis de tamanio de grupo). Sirve para ilustrar, no para sostener el argumento sola.

En sobreedad alta la brecha va en el mismo sentido: es 4.6 veces mayor en estatal rural que en privado urbano.

**Por que importa para el proyecto:** sugiere que la variable a mirar no es donde queda la escuela sino quien la gestiona, y eso es una pregunta de politica publica, no de geografia.

## Por que los grupos chicos dan valores extremos

| _q           |   filas |   estudiantes_mediana |   desvio |   minimo |   maximo |
|:-------------|--------:|----------------------:|---------:|---------:|---------:|
| 1 mas chico  |     235 |               28.8299 |   0.2045 |   0.0000 |   1.0000 |
| 2            |     235 |               74.6653 |   0.1734 |   0.1168 |   0.9200 |
| 3            |     234 |              138.9115 |   0.1682 |   0.1411 |   0.9040 |
| 4            |     235 |              289.4872 |   0.1480 |   0.2060 |   0.8970 |
| 5 mas grande |     235 |            1,225.1631 |   0.1498 |   0.1790 |   0.8372 |

**El quintil de grupos mas chicos tiene 1.4 veces la dispersion del mas grande**, y sus valores llegan a 0,000 y a 1,000, o sea los extremos posibles, mientras el quintil grande queda entre 0,18 y 0,84. No es que los grupos chicos sean mejores ni peores: con pocos casos, un estudiante mas o menos mueve mucho el porcentaje.

**Consecuencia practica para leer todo este informe:** cualquier numero de una celda chica se cita con su denominador al lado. La celda privada rural son 36 filas y 3.679 estudiantes, el 0,7% del total, y es ademas la de mayor dispersion de las cuatro.

## Contexto socioeconomico y rendimiento (nivel provincia)

| indicador_eph                  |   r_con_matematica_bajo_basico |   r_con_sobreedad_alta |   provincias |
|:-------------------------------|-------------------------------:|-----------------------:|-------------:|
| eph_ipcf_mediano               |                        -0.8171 |                -0.3362 |           24 |
| eph_educ_adultos__superior     |                        -0.7179 |                -0.1506 |           24 |
| eph_adultos_sin_secundaria     |                         0.5227 |                 0.1693 |           24 |
| eph_agua_fuera_vivienda        |                         0.5225 |                 0.2965 |           24 |
| eph_educ_adultos__primaria     |                         0.4848 |                 0.1157 |           24 |
| eph_educ_adultos__sin_primaria |                         0.4511 |                 0.2674 |           24 |
| eph_hacinamiento_critico       |                         0.3293 |                 0.1586 |           24 |
| eph_casos_hogares              |                        -0.2177 |                -0.1137 |           24 |
| eph_aglomerados                |                        -0.2165 |                -0.0926 |           24 |
| eph_no_asiste_12_18            |                         0.1597 |                 0.1751 |           24 |
| eph_casos_personas             |                        -0.1544 |                -0.0768 |           24 |
| eph_sin_dato_ingreso           |                        -0.1324 |                -0.2055 |           24 |
| eph_educ_adultos__secundaria   |                         0.0678 |                -0.0598 |           24 |
| eph_adolescentes_ocupados      |                        -0.0615 |                -0.1242 |           24 |
| eph_desocupacion               |                         0.0168 |                -0.1974 |           24 |

Calculado a nivel PROVINCIA (24 puntos), no a nivel fila. Hacerlo sobre las 1.174 filas habria inflado el n sin agregar informacion, porque los indicadores de la EPH se repiten identicos en todos los departamentos de una misma provincia y por lo tanto las filas no son observaciones independientes. Con 24 puntos, un |r| cercano a 0,8 es fuerte pero descansa en pocas observaciones: conviene mirarlo junto con la version sin CABA, que es el outlier estructural del pais.

## Robustez de la correlacion mas fuerte del trabajo

| prueba                         |   n |       r |
|:-------------------------------|----:|--------:|
| Pearson, las 24 jurisdicciones |  24 | -0.8171 |
| Pearson, sin CABA              |  23 | -0.7290 |
| Spearman, las 24               |  24 | -0.8497 |
| Spearman, sin CABA             |  23 | -0.8293 |

**Por que estas tres pruebas y no otras.** Una correlacion de Pearson falla de dos maneras conocidas, y cada prueba ataca una.

*Que la sostenga un solo caso raro.* CABA es el sospechoso natural: es la jurisdiccion mas rica y la de mejor desempenio, y esta sola en ese rincon. Si la relacion fuera solo ella, sacarla la derrumbaria. Se saco y la relacion se mantiene.

*Que la relacion sea fuerte pero curva.* Pearson solo ve lineas rectas; Spearman ignora la forma y mira solo el orden. Spearman da mas fuerte que Pearson, lo que sugiere que la relacion es algo curva: el salto entre las provincias mas pobres pesa mas que entre las mas ricas.

**La relacion sobrevive las tres pruebas**, asi que no depende de un outlier ni es un artefacto de suponer linealidad.

**Y el n es parte del dato.** Son 24 puntos, uno por jurisdiccion, no 1.174. Con 24 observaciones, mover dos o tres cambia bastante el resultado. Por eso el numero se cita siempre como *r = -0,82 sobre 24 jurisdicciones* y nunca como *r = -0,82* a secas.

## Sobreedad, repitencia y desempenio (nivel fila)

| variable                                                 | contra                                         |   r_pearson |   r_spearman |   filas_con_dato |   estudiantes |
|:---------------------------------------------------------|:-----------------------------------------------|------------:|-------------:|-----------------:|--------------:|
| libros_hogar__no_hay_libros_en_formato_papel             | desemp_matematica__por_debajo_del_nivel_basico |      0.6219 |       0.6440 |             1174 |  540,040.0004 |
| educ_madre__terciariouniversitarioposgrado_completo      | desemp_matematica__por_debajo_del_nivel_basico |     -0.6190 |      -0.5936 |             1174 |  540,040.0004 |
| repitencia__repitio_1_vez                                | desemp_matematica__por_debajo_del_nivel_basico |      0.3494 |       0.3885 |             1174 |  540,040.0004 |
| sobreedad__3_anos_o_mas_de_sobreedad_20_anos_o_mas_30jun | desemp_lengua__por_debajo_del_nivel_basico     |      0.2281 |       0.2528 |             1174 |  540,040.0004 |
| sobreedad__3_anos_o_mas_de_sobreedad_20_anos_o_mas_30jun | desemp_matematica__por_debajo_del_nivel_basico |      0.2123 |       0.2037 |             1174 |  540,040.0004 |
| inasistencias__30_o_mas_faltas                           | desemp_matematica__por_debajo_del_nivel_basico |      0.0003 |      -0.0339 |             1174 |  540,040.0004 |

Estas SI se calculan a nivel fila, porque las dos variables de cada par vienen de Aprender y varian entre departamentos. Se reporta Pearson y Spearman juntos a proposito: si difieren mucho, la relacion no es lineal y el Pearson solo estaria enganiando.

## Inasistencias: el acumulado, no la cola

| medida                         |   r_con_matematica_bajo |   valor_medio_ponderado |
|:-------------------------------|------------------------:|------------------------:|
| ninguna falta                  |                  0.3109 |                  0.0255 |
| 5 o mas faltas                 |                 -0.4859 |                  0.8484 |
| 15 o mas faltas                |                 -0.3658 |                  0.5104 |
| 30 o mas faltas (solo la cola) |                  0.0003 |                  0.1002 |
| 5+ faltas, solo Estatal Rural  |                 -0.3370 |                  0.6870 |
| 5+ faltas, solo Estatal Urbano |                 -0.3650 |                  0.8307 |
| 5+ faltas, solo Privado Rural  |                 -0.5930 |                  0.7058 |
| 5+ faltas, solo Privado Urbano |                 -0.4937 |                  0.9132 |

**El hallazgo mas raro del trabajo, y queda como pregunta abierta, no como conclusion.** Cuantos mas chicos de un grupo reportan faltas, MENOS chicos de ese grupo estan por debajo del basico. Y los grupos donde mas chicos dicen no faltar nunca son los de peor desempenio.

**Como aparecio, porque el metodo importa.** La primera medicion uso solo la categoria mas extrema (30 faltas o mas) y dio r = +0,000: la conclusion habria sido que las inasistencias no se relacionan con nada. El error fue mirar la cola de la distribucion en vez del acumulado. Casi nadie cae en la categoria extrema, asi que esa columna casi no varia y no puede correlacionar con nada.

**No es la paradoja de Simpson.** Se calculo el mismo r dentro de cada combinacion de sector y ambito (las cuatro ultimas filas de la tabla): la relacion negativa se mantiene en las cuatro, asi que no la produce mezclar poblaciones distintas.

**Quien contesta esto, VERIFICADO en la fuente.** El Manual del Aplicador de Aprender 2024 dice que *al finalizar ambas pruebas, los estudiantes contestaran un cuestionario complementario*, y que cada alumno recibe un Cuadernillo del Estudiante con las hojas para registrar sus respuestas. Hay un cuestionario aparte para directores, que no es este. O sea que el dato es **lo que el estudiante dice que falto**, no un registro administrativo de asistencia.

**Hipotesis, explicitamente NO VERIFICADA.** Aprender evalua a quien esta presente el dia de la prueba, asi que en una escuela con ausentismo real alto los mas ausentes no entran a la muestra. Entre los que si rindieron, reportar faltas seria marcador de un alumno presente y conectado con la escuela, no de riesgo. Se suma que el dato es autorreporte: son dos capas de ruido en la misma variable. Verificarlo requiere datos de asistencia administrativa, que este dataset no tiene.

## Diferencias por sexo: por que no se puede responder

| columna         | que_mide                                     |   r_con_matematica_bajo |
|:----------------|:---------------------------------------------|------------------------:|
| sexo__masculino | proporcion de esa categoria DENTRO del grupo |                 -0.0494 |
| sexo__femenino  | proporcion de esa categoria DENTRO del grupo |                  0.0307 |
| sexo__x         | proporcion de esa categoria DENTRO del grupo |                  0.0988 |

**La consigna pregunta si hay diferencias segun sexo, y con esta base no se puede responder.** Las columnas `sexo__*` dicen que porcentaje del grupo son varones o mujeres; **no** dicen como le fue a cada sexo. Para eso haria falta el desempenio desagregado por sexo, que la base agregada de Aprender no publica.

Lo unico calculable es si los grupos con mas mujeres rinden distinto, y da practicamente cero. Ese numero responde una pregunta diferente de la que se hizo, asi que se reporta el limite y no el numero.

**Es la misma pared que el TP1 ya habia declarado:** la unidad de analisis es el grupo territorial y no el estudiante, asi que toda pregunta que necesite abrir por atributo individual queda fuera de alcance con las bases publicadas.

## Efecto de cada decision de curacion

| escenario                    |   filas |   estudiantes |   matematica_bajo_basico |   sobreedad_alta |   clima_escolar_bajo |
|:-----------------------------|--------:|--------------:|-------------------------:|-----------------:|---------------------:|
| todo el dataset              |    1174 |  540,040.0004 |                   0.5434 |           0.0166 |               0.2039 |
| sin agregados provinciales   |    1111 |  529,595.9285 |                   0.5432 |           0.0168 |               0.2030 |
| solo clima escolar 'ok'      |     987 |  530,231.5821 |                   0.5418 |           0.0164 |               0.2036 |
| sin discrepancia entre bases |    1169 |  539,253.9246 |                   0.5434 |           0.0166 |               0.2038 |

Movimientos por encima del 1%: solo clima escolar 'ok' mueve sobreedad_alta un -1.3%. Eso NO significa que las decisiones sobraran: significa que los problemas estaban acotados y que ahora estan acotados **y medidos**. La diferencia entre las dos situaciones es que antes nadie podia afirmarlo. Y para el TP3 el valor es otro: cuando un modelo de al excluir estas filas un resultado distinto, va a haber una columna que lo explique en vez de un misterio.

## Provincias: los dos extremos

| jurisdiccion                    |   estudiantes |   matematica_bajo_basico |   sobreedad_alta |   eph_ipcf_mediano |
|:--------------------------------|--------------:|-------------------------:|-----------------:|-------------------:|
| Ciudad Autónoma de Buenos Aires |   33,711.9999 |                   0.3469 |           0.0197 |       825,000.0000 |
| Córdoba                         |   42,254.9985 |                   0.4412 |           0.0083 |       527,084.0000 |
| Entre Ríos                      |   13,579.0000 |                   0.4994 |           0.0274 |       405,000.0000 |
| Santa Fe                        |   36,087.0013 |                   0.5101 |           0.0141 |       500,000.0000 |
| Neuquén                         |    9,024.9998 |                   0.5110 |           0.0189 |       666,666.6700 |
| La Rioja                        |    5,311.0001 |                   0.6513 |           0.0070 |       304,500.0000 |
| Formosa                         |    6,868.0001 |                   0.6529 |           0.0325 |       325,000.0000 |
| Catamarca                       |    5,466.0002 |                   0.6710 |           0.0131 |       322,500.0000 |
| Santiago del Estero             |   11,125.0003 |                   0.6803 |           0.0222 |       350,000.0000 |
| Chaco                           |   13,487.0004 |                   0.7026 |           0.0318 |       310,000.0000 |

Ordenado por proporcion de estudiantes por debajo del basico en matematica, ponderada. Las cinco primeras y las cinco ultimas. La distancia entre los extremos es el tamanio del problema que el proyecto quiere explicar.

