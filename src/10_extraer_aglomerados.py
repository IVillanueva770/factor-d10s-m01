"""Paso 4a: extraer la lista oficial de aglomerados del documento del INDEC.

No se tipea ningun codigo a mano. Se parsea el texto del PDF oficial que quedo
guardado en data/raw/documentacion/, y el resultado se contrasta contra los
aglomerados que realmente aparecen en la base descargada.

Fuente: INDEC, "Encuesta Permanente de Hogares. Diseño de Registro y Estructura
para las bases de microdatos", 4to trimestre 2014.
https://www.indec.gob.ar/ftp/cuadros/menusuperior/eph/EPH_diseno_reg_t414.pdf
"""

import re
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DOCS = BASE_DIR / "data" / "raw" / "documentacion"
INTERIM = BASE_DIR / "data" / "interim"

FUENTE_TXT = DOCS / "EPH_diseno_reg_t414.txt"
FUENTE_URL = ("https://www.indec.gob.ar/ftp/cuadros/menusuperior/eph/"
              "EPH_diseno_reg_t414.pdf")


def extraer_aglomerados(texto):
    """Toma el bloque que arranca en 'AGLOMERADO' y corta al llegar a PONDERA."""
    inicio = texto.index("AGLOMERADO N(2)")
    fin = texto.index("PONDERA", inicio)
    bloque = texto[inicio:fin]

    filas = []
    for linea in bloque.splitlines():
        m = re.match(r"\s*(\d{1,2})\s*=\s*(.+?)\s*$", linea)
        if m:
            filas.append({"aglomerado": int(m.group(1)),
                          "nombre_indec": m.group(2).strip()})
    return pd.DataFrame(filas)


def main():
    texto = FUENTE_TXT.read_text(encoding="latin-1")
    aglomerados = extraer_aglomerados(texto)

    print("=" * 74)
    print("AGLOMERADOS EXTRAIDOS DEL DOCUMENTO OFICIAL")
    print("=" * 74)
    print(f"  fuente: {FUENTE_URL}")
    print(f"  extraidos: {len(aglomerados)}")
    print(f"  codigos duplicados: {aglomerados['aglomerado'].duplicated().sum()}")

    # Contraste contra la base real: el documento es de 2014 y la base es de
    # 2025, asi que la lista podria haber cambiado.
    eph = pd.read_parquet(INTERIM / "eph_3t2025_unida.parquet")
    en_base = set(eph["AGLOMERADO"].unique())
    en_doc = set(aglomerados["aglomerado"])

    print()
    print("  Contraste documento (2014) vs base descargada (3T 2025):")
    print(f"    en la base y no en el doc: {sorted(en_base - en_doc) or 'ninguno'}")
    print(f"    en el doc y no en la base: {sorted(en_doc - en_base) or 'ninguno'}")
    if en_base != en_doc:
        raise SystemExit("La lista del documento no cubre la base: revisar")

    destino = DOCS / "aglomerados_indec.csv"
    aglomerados.sort_values("aglomerado").to_csv(destino, index=False,
                                                 encoding="utf-8")
    print(f"\n  guardado: {destino.relative_to(BASE_DIR)}")
    print()
    print(aglomerados.sort_values("aglomerado").to_string(index=False))


if __name__ == "__main__":
    main()
