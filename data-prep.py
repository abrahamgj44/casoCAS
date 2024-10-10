import polars as pl

path1 = r"C:\Users\abrah\OneDrive\Desktop\casoCAS\archivo\data\Competencia de Casos CAS + Addactis 2024 - Datos.xlsx"
exposure = pl.read_excel(path1)

path2 = r"C:\Users\abrah\OneDrive\Desktop\casoCAS\archivo\data\geocodinginfo.xlsx"
geo_info = pl.read_excel(path2)

final_geo = geo_info.select(
    pl.col("Loc ID"),
    pl.col("city").alias("Ciudad"),
    pl.col("name").alias("Pais"),
    pl.col("alpha-3").alias("Codigo pais"),
    pl.col("continent").alias("Continente"),
    pl.col("sub-region").alias("Sub continente"),
    pl.col("intermediate-region").alias("Continente intermedio"),
)

w = exposure.join(final_geo, on="Loc ID", how="left")
w.write_excel(
    r"C:\Users\abrah\OneDrive\Desktop\casoCAS\archivo\data\final-dataset.xlsx"
)
