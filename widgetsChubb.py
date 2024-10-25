# Widgets
import ipywidgets as widgets  # widgets
from IPython.display import display  # tool to display the widgets


# Text box construction
def text_box(description, placeholder):
    return widgets.Text(
        description=description,
        placeholder=placeholder,
        continuous_update=False,
        disabled=False,
        style={"description_width": "initial"},
    )


# Dropdown constructor
def drop_wid(description, options, value):
    return widgets.Dropdown(
        options=options,
        value=value,
        description=description,
        disabled=False,
    )


# button constructor
def button_wid(description, style):
    return widgets.Button(
        value=False,
        description=description,
        disabled=False,
        button_style=style,  # 'success', 'info', 'warning', 'danger' or ''
        tooltip="Description",
        icon="check",
    )  # (FontAwesome names without the `fa-` prefix)
