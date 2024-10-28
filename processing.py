from sklearn.cluster import KMeans
import polars as pl
import plotly.express as px

path2 = r"C:\Users\abrah\OneDrive\Desktop\final-dataset_rangos_V4.xlsx"
df = pl.read_excel(path2, sheet_name="Sheet 1")


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


f = df.group_by("Ciudad").agg(pl.col("Suma Asegurada").sum(), pl.col("Prima").sum())
f
h = cluster_dimension(f, "Ciudad", ["Suma Asegurada", "Prima"], n_clusters=4)

px.scatter(h, y="Prima", x="Ciudad", color="CiudadClustered", size="Suma Asegurada")

graph = px.scatter(
    h,
    y="Prima",
    x="Ciudad",
    color="CiudadClustered",
    size="Suma Asegurada",
    marginal_y="box",
    template="ggplot2",
)

graph.write_html(r"C:\Users\abrah\OneDrive\Desktop\image.html")
