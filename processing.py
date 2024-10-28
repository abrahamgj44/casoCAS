from sklearn.cluster import KMeans
import polars as pl
import plotly.express as px

path2 = r"C:\Users\abrah\OneDrive\Desktop\casoCAS\archivo\data\final-dataset_V.5.5.xlsx"
df = pl.read_excel(path2, sheet_name="Sheet1")


def cluster_dimension(
    df: pl.DataFrame, dimension: str, categories: list[str], n_clusters: int
) -> pl.DataFrame:
    """This function clusters one categorical function of a polars dataframe using
    several dimensions

    Args:
        df: This must be a grouped dataframe by dimension, with the categories we want to use
        n_clusters (_type_): _description_
        style (str, optional): _description_. Defaults to "frequency".

    Returns:
        _type_: _description_
    """

    # onehot enconding
    encoded_df = pl.concat(
        [
            df.select(categories),
            df.select(dimension).to_dummies(),
        ],
        how="horizontal",
    )

    # kmeans
    kmeans = KMeans(n_clusters, init="k-means++", random_state=0)
    kmeans.fit(encoded_df)

    cluster_df = (
        df.with_columns(cluster=kmeans.labels_)
        .with_columns(pl.col("cluster").cast(pl.String))
        .rename({"cluster": f"{dimension}Clustered"})
    )
    return cluster_df


f = (
    df.group_by("Ciudad")
    .agg(
        pl.col("Exposicion").sum().alias("Exposicion"),
        pl.col("Suma Asegurada").sum(),
        pl.col("Prima").sum().alias("Prima Ganada"),
        pl.col("Evento ID").drop_nulls().n_unique().alias("Número Eventos"),
        pl.col("Numero Siniestros").sum(),
        pl.col("Duración de la inundación (días)").mean().alias("Duración Promedio"),
        pl.col("Severidad de la inundación (escala 1-5)")
        .mean()
        .alias("Magnitud Inundaciones Promedio"),
        pl.col("Precipitación (mm)").mean().alias("Precipitación Promedio"),
        pl.col("Incremento del Nivel del Río (m)").mean().alias("Incremento Promedio"),
        pl.col("Monto de siniestro").sum().alias("Incurrido"),
    )
    .with_columns(
        (pl.col("Incurrido") / pl.col("Prima Ganada")).alias(
            "Indice de Siniestralidad"
        ),
        (pl.col("Prima Ganada") / pl.col("Suma Asegurada") * 1000).alias(
            "Tasa por Mil"
        ),
        (pl.col("Incurrido") / pl.col("Suma Asegurada")).alias("TPR"),
        (pl.col("Numero Siniestros") / pl.col("Exposicion")).alias("Frecuencia"),
        (pl.col("Incurrido") / pl.col("Numero Siniestros")).alias("Severidad"),
    )
    .with_columns((pl.col("Frecuencia") * pl.col("Severidad")).alias("Prima Pura"))
    .with_columns((pl.col("Prima Pura") / pl.col("Prima Ganada")).alias("proportion"))
    .with_columns(
        (pl.col("Suma Asegurada") / pl.col("Exposicion")).alias(
            "Suma Asegurada Promedio"
        )
    )
    .with_columns(
        (pl.col("Prima Pura") / pl.col("Suma Asegurada") * 1000).alias(
            "Tasa por mil inundación"
        )
    )
    .sort(by="Indice de Siniestralidad", descending=False)
)

f
h = cluster_dimension(f, "Ciudad", ["Severidad"], n_clusters=4)

px.scatter(
    h, y="Severidad", x="Ciudad", color="CiudadClustered", size="Numero Siniestros"
)

graph = px.scatter(
    h,
    y="Severidad",
    x="Ciudad",
    color="SeveridadClustered",
    size="Numero Siniestros",
    marginal_y="box",
    template="plotly_white",
)
graph

graph.write_html(
    r"C:\Users\abrah\OneDrive\Desktop\casoCAS\docs\images\clustersCiudad.html"
)
