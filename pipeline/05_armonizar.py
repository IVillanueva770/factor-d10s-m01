"""Paso 8: armonizar de verdad las categorias equivalentes entre fuentes.

Criterio de aceptacion de la consigna: "Se armonicen los nombres y categorias
equivalentes entre ambas fuentes".

Aprender y la EPH miden el nivel educativo de los adultos con escalas
distintas (7 categorias contra 7 codigos, con cortes en lugares distintos).
Este script las lleva a una escala comun de 4 niveles de MAXIMO NIVEL
COMPLETADO, y agrega esas columnas al dataset maestro.

El valor de hacerlo: habilita un contraste que antes era imposible. El nivel
educativo de las madres segun Aprender y el de los adultos segun la EPH miden
poblaciones distintas, pero de la misma provincia. Si dieran numeros
disparatados entre si, seria señal de que algo del cruce esta mal.
"""

from pathlib import Path

import pandas as pd

from comun import clave_provincia

BASE_DIR = Path(__file__).resolve().parent.parent
INTERIM = BASE_DIR / "data" / "interim"
PROCESADO = BASE_DIR / "data" / "processed"

NIVELES = ["sin_primaria", "primaria", "secundaria", "superior"]

# Aprender: categoria del bloque -> nivel comun.
APRENDER_A_COMUN = {
    "no_fue_a_la_escuela": "sin_primaria",
    "primaria_incompleto": "sin_primaria",
    "primaria_completo": "primaria",
    "secundaria_incompleto": "primaria",
    "secundaria_completo": "secundaria",
    "terciariouniversitarioposgrado_incompleto": "secundaria",
    "terciariouniversitarioposgrado_completo": "superior",
}

# EPH: codigo de NIVEL_ED -> nivel comun. Codigos verificados en
# data/raw/documentacion/EPH_diseno_reg_t414.pdf
EPH_A_COMUN = {
    7: "sin_primaria",   # Sin instruccion
    1: "sin_primaria",   # Primaria incompleta
    2: "primaria",       # Primaria completa
    3: "primaria",       # Secundaria incompleta
    4: "secundaria",     # Secundaria completa
    5: "secundaria",     # Superior universitaria incompleta
    6: "superior",       # Superior universitaria completa
}


def armonizar_aprender(maestro, bloque, prefijo_salida):
    """Colapsa las 7 categorias de un bloque educativo a los 4 niveles."""
    salida = pd.DataFrame(index=maestro.index)
    usadas = []
    for nivel in NIVELES:
        cols = [f"{bloque}__{cat}" for cat, n in APRENDER_A_COMUN.items()
                if n == nivel and f"{bloque}__{cat}" in maestro.columns]
        usadas += cols
        salida[f"{prefijo_salida}__{nivel}"] = maestro[cols].sum(axis=1)

    esperadas = {f"{bloque}__{c}" for c in APRENDER_A_COMUN}
    presentes = {c for c in maestro.columns if c.startswith(f"{bloque}__")}
    faltan = esperadas - presentes
    sobran = presentes - esperadas
    assert not faltan, f"{bloque}: faltan categorias {faltan}"
    assert not sobran, f"{bloque}: categorias no mapeadas {sobran}"
    return salida


def armonizar_eph():
    """Distribucion de adultos 25+ por nivel comun, ponderada, por provincia."""
    eph = pd.read_parquet(INTERIM / "eph_3t2025_unida.parquet")
    puente = pd.read_csv(BASE_DIR / "data" / "raw" / "documentacion" /
                         "aglomerado_provincia.csv")
    eph = eph.merge(puente[["aglomerado", "provincia"]],
                    left_on="AGLOMERADO", right_on="aglomerado", how="left",
                    validate="many_to_one")

    adultos = eph[(eph["CH06"] >= 25) & eph["NIVEL_ED"].isin(EPH_A_COMUN)].copy()
    adultos["nivel"] = adultos["NIVEL_ED"].map(EPH_A_COMUN)

    pesos = (adultos.groupby(["provincia", "nivel"])["PONDERA"].sum()
             .unstack(fill_value=0))
    proporciones = pesos.div(pesos.sum(axis=1), axis=0)
    proporciones = proporciones.reindex(columns=NIVELES, fill_value=0.0)
    proporciones.columns = [f"eph_educ_adultos__{n}" for n in NIVELES]

    descartados = eph[(eph["CH06"] >= 25) & ~eph["NIVEL_ED"].isin(EPH_A_COMUN)]
    return proporciones.reset_index(), len(descartados), len(eph[eph["CH06"] >= 25])


def main():
    # Lee la salida de la etapa 04 y escribe a un archivo DISTINTO. Antes leia
    # y escribia sobre dataset_maestro_inicial.csv, o sea que mutaba su propia
    # entrada: correrla dos veces sin rehacer la 04 apilaba las columnas
    # armonizadas encima de las que ya estaban (131 -> 155 columnas), sin error
    # y sin aviso. Ver pipeline/contrato.py, regla 1.
    maestro = pd.read_csv(PROCESADO / "dataset_maestro_base.csv")

    print("=" * 74)
    print("ARMONIZACION DEL NIVEL EDUCATIVO A UNA ESCALA COMUN")
    print("=" * 74)
    print(f"  escala: {' < '.join(NIVELES)}")

    nuevas = []
    for bloque, salida in [("educ_madre", "educ_madre_arm"),
                           ("educ_padre", "educ_padre_arm")]:
        arm = armonizar_aprender(maestro, bloque, salida)
        suma = arm.sum(axis=1)
        sin_dato = arm.isna().all(axis=1)
        raras = ~(suma.between(0.999, 1.001) | sin_dato)
        print(f"  {bloque:12s} -> {salida}: suman 1 en "
              f"{suma.between(0.999, 1.001).sum():,}/{len(arm):,} filas | "
              f"raras: {raras.sum()}")
        assert raras.sum() == 0
        nuevas.append(arm)

    eph_arm, descartados, total_adultos = armonizar_eph()
    print(f"  EPH NIVEL_ED -> eph_educ_adultos: {len(eph_arm)} provincias")
    print(f"    adultos 25+ con nivel sin codificar (9 = Ns/Nr): "
          f"{descartados:,} de {total_adultos:,} "
          f"({descartados / total_adultos:.2%}) -> excluidos del denominador")

    maestro = pd.concat([maestro] + nuevas, axis=1)
    # El join va por la clave normalizada: los nombres crudos difieren en
    # tildes entre las dos fuentes.
    maestro["_clave"] = maestro["jurisdiccion"].map(clave_provincia)
    eph_arm["_clave"] = eph_arm["provincia"].map(clave_provincia)
    maestro = maestro.merge(eph_arm.drop(columns=["provincia"]), on="_clave",
                            how="left", validate="many_to_one"
                            ).drop(columns=["_clave"])
    cols_arm = [c for c in maestro.columns if c.startswith("eph_educ_adultos__")]
    assert maestro[cols_arm].notna().all().all(), \
        "Quedaron provincias sin nivel educativo armonizado de la EPH"

    maestro.to_csv(PROCESADO / "dataset_maestro_inicial.csv", index=False,
                   encoding="utf-8")

    print()
    print("=" * 74)
    print("EL CONTRASTE QUE HABILITA (secundaria completa o mas)")
    print("=" * 74)
    comparacion = maestro.groupby("jurisdiccion").apply(
        lambda g: pd.Series({
            "madres_Aprender": (
                (g["educ_madre_arm__secundaria"] + g["educ_madre_arm__superior"])
                * g["estudiantes"]).sum() / g["estudiantes"].sum(),
            "padres_Aprender": (
                (g["educ_padre_arm__secundaria"] + g["educ_padre_arm__superior"])
                * g["estudiantes"]).sum() / g["estudiantes"].sum(),
            "adultos_EPH": g["eph_educ_adultos__secundaria"].iloc[0]
                           + g["eph_educ_adultos__superior"].iloc[0],
        }), include_groups=False)
    comparacion["dif_madres_vs_eph"] = (comparacion["madres_Aprender"]
                                        - comparacion["adultos_EPH"])
    print(comparacion.sort_values("adultos_EPH", ascending=False)
          .to_string(float_format=lambda x: f"{x:,.3f}"))
    print()
    print(f"  correlacion madres (Aprender) vs adultos (EPH): "
          f"{comparacion['madres_Aprender'].corr(comparacion['adultos_EPH']):.3f}")
    print(f"  dataset maestro: {len(maestro):,} filas x {maestro.shape[1]:,} columnas")


if __name__ == "__main__":
    main()
