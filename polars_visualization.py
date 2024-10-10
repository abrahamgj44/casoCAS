import polars as pl


def pl_config(
    all_columns=True,
    all_rows=False,
    number_of_rows=None,
    width_chars=1000,
    float_precision=3,
    hide_datatype=True,
    hide_shape=False,
):
    """Returns polars configuration

    Args:
        df (_type_): _description_
        all_columns (bool, optional): _description_. Defaults to True.
        all_rows (bool, optional): _description_. Defaults to False.
        number_of_rows (_type_, optional): _description_. Defaults to None.
    """
    if all_columns:
        tbl_cols = -1
    else:
        tbl_cols = None
    if all_rows:
        tbl_rows = -1
    elif number_of_rows != None:
        tbl_rows = number_of_rows
    else:
        tbl_rows = None

    return pl.Config(
        set_fmt_float="full",
        thousands_separator=",",
        decimal_separator=".",
        float_precision=float_precision,
        tbl_rows=tbl_rows,
        tbl_cols=tbl_cols,
        tbl_width_chars=width_chars,
        tbl_formatting="ASCII_MARKDOWN",
        tbl_hide_column_data_types=hide_datatype,
        tbl_hide_dataframe_shape=hide_shape,
    )
