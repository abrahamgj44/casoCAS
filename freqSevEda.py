import polars as pl
from visualization import *

# widgets
from widgetsChubb import drop_wid, button_wid
import ipywidgets as widgets
from IPython.display import display, clear_output

# beautiful tables
from great_tables import GT, md, html, style, loc

# clustering
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns


class FreqSevEDA:

    def __init__(
        self,
        data: pl.DataFrame,
        claimNb: str = None,
        exposure: str = None,
        claimAmount: str = None,
    ):

        self.data = data
        self.claimNb = claimNb
        self.exposure = exposure
        self.claimAmount = claimAmount

        # we define expressions as attributes
        self.claimNbGrp = pl.col(claimNb).sum()
        self.exposureGrp = pl.col(exposure).sum()
        self.claimAmountGrp = pl.col(claimAmount).sum()

        # attributes based in expusre, claimnb and claimAmount
        self.marginalFreq = (
            (self.claimNbGrp / self.exposureGrp).fill_nan(0).alias("marginalFreq")
        )
        self.marginalSeve = (
            (self.claimAmountGrp / self.claimNbGrp).fill_nan(0).alias("marginalSeve")
        )
        self.marginalLossCost = (self.claimAmountGrp / self.exposureGrp).alias(
            "marginalLossCost"
        )
        self.agg_att = (
            self.claimNbGrp,
            self.exposureGrp,
            self.claimAmountGrp,
            self.marginalFreq,
            self.marginalSeve,
            self.marginalLossCost,
        )

    def portfolio_metrics(self):

        metrics = (
            self.data.with_columns(groupColumn=pl.lit("flag"))
            .group_by("groupColumn")
            .agg(self.agg_att)
            .drop("groupColumn")
        )

        return metrics

    def frequency_and_severity_summary(
        self,
        dimension: str,
        # show_portfolio_metrics: bool = True,
    ) -> pl.DataFrame:

        summary = self.data.lazy().group_by(dimension).agg(self.agg_att).collect()

        return summary

    def table_summary(self, dimension):
        summ = self.frequency_and_severity_summary(dimension).sort(
            by=self.claimNb, descending=True
        )
        max_range = summ.get_column(self.claimNb).max()
        min_range = summ.get_column(self.claimNb).min()

        # addign portfolio metrics
        summ = pl.concat([summ, self.portfolio_metrics()], how="diagonal").fill_null(
            "Portfolio_values"
        )

        # creating and styling the final value

        # formats
        table = (
            GT(summ, rowname_col=dimension)
            .fmt_number(columns=self.exposure, decimals=0)
            .fmt_number(columns=[self.claimAmount, "marginalSeve"], compact=True)
            .fmt_currency(columns=["marginalLossCost"], currency="BRL", decimals=0)
            .fmt_number("marginalFreq", decimals=4)
        )

        # header
        table = table.tab_header(
            title=md("**Frequency and Severity summary**"),
            subtitle=md(f"*{dimension}*"),
        )

        # color and style
        table = table.data_color(
            pl.col(self.claimNb),
            palette=["mediumturquoise", "white"],
            domain=[max_range, min_range],
        ).tab_style(
            style=style.fill(color="mintcream"),
            locations=loc.body(rows=[summ.shape[0] - 1, summ.shape[0]]),
        )
        return table

    def graphFreqSev(self, dimension):
        df = self.frequency_and_severity_summary(dimension).sort(by=dimension)

        fig_freq = plotly_bar_line(
            df,
            x_bar=dimension,
            y_bar=self.exposure,
            y_line="marginalFreq",
            visible=True,
        )
        bar_sev = plotly_bar(df, dimension, self.claimNb, visible=False)
        line_sev = plotly_scatter(df, dimension, "marginalSeve", visible=False)

        # graphing portfolio metrics
        portfolio_metric = self.portfolio_metrics()
        portFreqdf = df.select(dimension).with_columns(
            portFreq=pl.lit(portfolio_metric.item(0, "marginalFreq"))
        )
        portSevedf = df.select(dimension).with_columns(
            portSeve=pl.lit(portfolio_metric.item(0, "marginalSeve"))
        )
        portFreqGraph = plotly_scatter(portFreqdf, dimension, "portFreq", visible=True)
        portSeveGraph = plotly_scatter(portSevedf, dimension, "portSeve", visible=False)

        # buttons to change between the graphs
        button1 = dict(
            method="update",
            args=[
                {"visible": [True, True, True, False, False, False]},
                {
                    "yaxis2": dict(
                        title=dict(text="marginalFreq"),
                        side="right",
                        overlaying="y",
                        tickmode="sync",
                    ),
                    "yaxis": dict(title=dict(text=self.exposure, side="left")),
                    "title": dict(text="marginalFreq vs Exposure", font=dict(size=30)),
                },
            ],
            label="marginalFreq",
        )
        button2 = dict(
            method="update",
            args=[
                {"visible": [False, False, False, True, True, True]},
                {
                    "yaxis2": dict(
                        title=dict(text="marginalSeve"),
                        side="right",
                        overlaying="y",
                        tickmode="sync",
                    ),
                    "yaxis": dict(title=dict(text=self.claimNb, side="left")),
                    "title": dict(
                        text="marginalSeve vs Claim Number", font=dict(size=30)
                    ),
                },
            ],
            label="marginalSeve",
        )
        # putting all the traces together
        for graph, axis in zip(
            [portFreqGraph, bar_sev, line_sev, portSeveGraph], [True, False, True, True]
        ):
            fig_freq.add_trace(
                graph,
                secondary_y=axis,
            )

        # adding the buttons
        fig_freq.update_layout(
            title=dict(text="marginalFreq vs Exposure", font=dict(size=30)),
            updatemenus=[
                dict(type="buttons", buttons=[button1, button2], y=0.5, x=1.4)
            ],
            height=400,
            template="plotly_white",
        )

        return fig_freq

    def interactive_graph(self):
        # dropdown
        drop = drop_wid("Columns:", ["-"] + self.data.columns, value="-")
        # output
        out = widgets.Output()

        # defining controller
        def on_change_column(change):
            graph = self.graphFreqSev(change.new)
            table = self.table_summary(change.new)

            with out:
                out.clear_output()
                graph.show()
                table.show()

        drop.observe(on_change_column, names="value")
        display(drop)
        display(out)

    def interactive_table(self):
        # dropdown
        drop = drop_wid("Columns:", ["-"] + self.data.columns, value="-")
        out = widgets.Output()

        # Create a button (assuming you have a button to display)
        butt1 = widgets.Button(description="Submit")

        # Function to handle change event
        def on_change_column(change):
            # Clear output first
            with out:
                clear_output(
                    wait=True
                )  # Clear previous output before displaying new content

                # Your logic for table display
                table = self.table_summary(change.new)
                table.show("notebook")  # Simulating the table display
                display(butt1)  # Display the button again

        # Attach the observer to the dropdown
        drop.observe(on_change_column, names="value")

        # Initial display
        display(drop)
        display(out)

    def cluster_dimension(self, dimension, n_clusters, style="frequency"):
        grouped_by_dimension = self.frequency_and_severity_summary(dimension)

        if style == "severity":
            category = "marginalSeve"

        elif style == "frequency":
            category = "marginalFreq"

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
            {"cluster": f"{dimension}Gr_{style}"}
        )
        return cluster_df

    def add_clusters(self, dimension, n_clusters, style="frequency"):

        clustered = self.cluster_dimension(
            dimension, n_clusters=n_clusters, style=style
        ).select(pl.col(dimension, f"{dimension}Gr_{style}"))

        return self.data.join(clustered, on=dimension, how="left")

    def show_clusters(
        self,
        dimension,
        n_clusters,
        size=(10, 5),
        sizes=(20, 200),
        style="frequency",
        show_labels=True,
    ):
        grouped_by_dimension = self.cluster_dimension(
            dimension, n_clusters, style=style
        )

        if style == "frequency":
            x = "marginalFreq"
            size_name = "Exposicion"
        elif style == "severity":
            x = "marginalSeve"
            size_name = "Numero Siniestros"

        plt.subplots(nrows=1, ncols=2, figsize=size)
        plt.subplot(1, 2, 1)
        pre_cluster = sns.scatterplot(
            y=dimension,
            x=x,
            data=grouped_by_dimension,
            sizes=sizes,
        )

        if not show_labels:
            pre_cluster.get_yaxis().set_ticks([])

        plt.subplot(1, 2, 2)
        clustered = sns.scatterplot(
            y=dimension,
            x=x,
            data=grouped_by_dimension,
            hue=f"{dimension}Gr_{style}",
            palette="Spectral",
            sizes=sizes,
        )
        clustered.get_yaxis().set_ticks([])
