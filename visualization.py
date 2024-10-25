import plotly.graph_objects as go
from plotly.subplots import make_subplots


# %%
def plotly_bar(df, x: str, y: str, visible=True):
    bar = go.Bar(
        x=df.get_column(x),
        y=df.get_column(y),
        name=y,
        visible=visible,
    )
    return bar


# %%
def plotly_scatter(df, x: str, y: str, visible=True):
    scatter_line = go.Scatter(
        x=df.get_column(x),
        y=df.get_column(y),
        name=y,
        visible=visible,
    )
    return scatter_line


# %%
def plotly_bar_line(df, x_bar: str, y_bar: str, y_line, visible=True):
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    bar = plotly_bar(df, x_bar, y_bar, visible)
    line = plotly_scatter(df, x_bar, y_line, visible)
    fig.add_traces([bar, line], secondary_ys=[False, True])

    # layout
    fig.update_layout(
        yaxis=dict(
            title=dict(text=y_bar),
            side="left",
        ),
        yaxis2=dict(
            title=dict(text=y_line),
            side="right",
        ),
    )

    return fig


# %%
# def table(df, autofit: bool = True, char_width=10, title=None):
#     """This function takes a polars dataframe and displays a plotly basic

#     Args:
#         df (pl.DataFrame): A polars dataframe

#     Returns:
#         Figure: plotly.graph_objs._figure.Figure
#     """
#     columns = df.columns

#     # setting up column names as the header
#     header = dict(values=columns)

#     # defining the cells values
#     cells = []
#     for col in columns:
#         cells.append(df.get_column(col).to_list())
#     cells = dict(values=cells)

#     # autofit
#     if autofit:
#         widths_header = [len(col) * char_width for col in df.columns]
#         widths_cols = (
#             df.with_columns(pl.all().cast(pl.String).str.len_chars())
#             .max()
#             .transpose()
#             .to_series()
#             .to_list()
#         )
#         widths = [
#             max(i) for i in zip(widths_header, [w * char_width for w in widths_cols])
#         ]

#         # layout
#         l_width = sum(widths) + 100
#         l_height = 100 + (df.shape[0] * 25)

#         layout = go.Layout(
#             height=l_height,
#             width=l_width,
#         )

#     table = go.Table(header=header, cells=cells, columnwidth=widths)

#     return go.Figure(data=[table], layout=layout)
