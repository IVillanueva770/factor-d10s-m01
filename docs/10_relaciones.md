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

La sobreedad alta (3 anios o mas, o sea 20 anios cumplidos o mas) es **4.6 veces mayor en estatal rural que en privado urbano**. La brecha mas grande no esta entre urbano y rural sino entre sectores de gestion: dentro de un mismo ambito, la diferencia por sector es mayor que la diferencia por ambito dentro de un mismo sector. Eso importa para el proyecto porque sugiere que la variable a mirar no es donde queda la escuela sino quien la gestiona, que es una pregunta de politica publica y no de geografia.

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

