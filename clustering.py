import polars as pl
import matplotlib.pyplot as plt
import seaborn as sns

# clustering
from sklearn.cluster import KMeans
from sklearn.preprocessing import KBinsDiscretizer
import sklearn.cluster as cluster


def cluster_dimension(data, dimension, n_clusters, group_number=1, style="frequency"):
    grouped_by_dimension = freq_sev_summary(data, dimension)

    if style == "severity":
        category = "MarginalSeve"

    elif style == "frequency":
        category = "MarginalFreq"

    # onehot enconding
    encoded_df = pl.concat(
        [
            grouped_by_dimension.select(category),
            grouped_by_dimension.select(dimension).to_dummies(),
        ],
        how="horizontal",
    )

    # kmeans
    kmeans = KMeans(n_clusters=n_clusters, init="k-means++", random_state=0)
    kmeans.fit(encoded_df)

    cluster_df = grouped_by_dimension.with_columns(cluster=kmeans.labels_).rename(
        {"cluster": f"{dimension}Gr{group_number}_{style}"}
    )
    return cluster_df


def add_clusters(data, dimension, n_clusters, style="frequency"):

    clustered = cluster_dimension(
        data, dimension, n_clusters=n_clusters, style=style
    ).select(pl.col(dimension, f"{dimension}Gr1_{style}"))

    return data.join(clustered, on=dimension, how="left")


def show_clusters(
    data,
    dimension,
    n_clusters,
    size=(10, 5),
    sizes=(20, 200),
    style="frequency",
    show_labels=True,
):
    grouped_by_dimension = cluster_dimension(df, dimension, n_clusters, style=style)

    if style == "frequency":
        x = "MarginalFreq"
        size_name = "ExposureGrp"
    elif style == "severity":
        x = "MarginalSeve"
        size_name = "AvgIl"

    plt.subplots(nrows=1, ncols=2, figsize=size)
    plt.subplot(1, 2, 1)
    pre_cluster = sns.scatterplot(
        y=dimension,
        x=x,
        data=grouped_by_dimension,
        size="ClaimNbGrp",
        sizes=sizes,
    )

    if not show_labels:
        pre_cluster.get_yaxis().set_ticks([])

    plt.subplot(1, 2, 2)
    clustered = sns.scatterplot(
        y=dimension,
        x=x,
        data=grouped_by_dimension,
        hue=f"{dimension}Gr1_{style}",
        palette="Spectral",
        size=size_name,
        sizes=sizes,
    )
    clustered.get_yaxis().set_ticks([])
