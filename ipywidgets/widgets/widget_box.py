# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

"""Box widgets.

These widgets are containers that can be used to
group other widgets together and control their
relative layouts.
"""

from contextlib import contextmanager
from .widget import register, widget_serialization, Widget
from .domwidget import DOMWidget
from .widget_core import CoreWidget
from .widget_output import Output
from .docutils import doc_subst
from .trait_types import TypedTuple
from traitlets import Unicode, CaselessStrEnum, Instance


_doc_snippets = {}
_doc_snippets['box_params'] = """
    children: iterable of Widget instances
        list of widgets to display

    box_style: str
        one of 'success', 'info', 'warning' or 'danger', or ''.
        Applies a predefined style to the box. Defaults to '',
        which applies no pre-defined style.
"""


@register
@doc_subst(_doc_snippets)
class Box(DOMWidget, CoreWidget):
    """ Displays multiple widgets in a group.

    The widgets are laid out horizontally.

    Parameters
    ----------
    {box_params}

    Examples
    --------
    >>> import ipywidgets as widgets
    >>> title_widget = widgets.HTML('<em>Box Example</em>')
    >>> slider = widgets.IntSlider()
    >>> widgets.Box([title_widget, slider])
    """
    _model_name = Unicode('BoxModel').tag(sync=True)
    _view_name = Unicode('BoxView').tag(sync=True)

    # Child widgets in the container.
    # Using a tuple here to force reassignment to update the list.
    # When a proper notifying-list trait exists, use that instead.
    children = TypedTuple(trait=Instance(Widget), help="List of widget children").tag(
        sync=True, **widget_serialization)

    box_style = CaselessStrEnum(
        values=['success', 'info', 'warning', 'danger', ''], default_value='',
        help="""Use a predefined styling for the box.""").tag(sync=True)

    def __init__(self, children=(), **kwargs):
        kwargs['children'] = children
        super(Box, self).__init__(**kwargs)
        self.on_displayed(Box._fire_children_displayed)

    def _fire_children_displayed(self):
        for child in self.children:
            child._handle_displayed()


@register
@doc_subst(_doc_snippets)
class VBox(Box):
    """ Displays multiple widgets vertically using the flexible box model.

    Parameters
    ----------
    {box_params}

    Examples
    --------
    >>> import ipywidgets as widgets
    >>> title_widget = widgets.HTML('<em>Vertical Box Example</em>')
    >>> slider = widgets.IntSlider()
    >>> widgets.VBox([title_widget, slider])
    """
    _model_name = Unicode('VBoxModel').tag(sync=True)
    _view_name = Unicode('VBoxView').tag(sync=True)


@register
@doc_subst(_doc_snippets)
class HBox(Box):
    """ Displays multiple widgets horizontally using the flexible box model.

    Parameters
    ----------
    {box_params}

    Examples
    --------
    >>> import ipywidgets as widgets
    >>> title_widget = widgets.HTML('<em>Horizontal Box Example</em>')
    >>> slider = widgets.IntSlider()
    >>> widgets.HBox([title_widget, slider])
    """
    _model_name = Unicode('HBoxModel').tag(sync=True)
    _view_name = Unicode('HBoxView').tag(sync=True)


@register
class GridBox(Box):
    """ Displays multiple widgets in rows and columns using the grid box model.

    Parameters
    ----------
    {box_params}

    Examples
    --------
    >>> import ipywidgets as widgets
    >>> title_widget = widgets.HTML('<em>Grid Box Example</em>')
    >>> slider = widgets.IntSlider()
    >>> button1 = widgets.Button(description='1')
    >>> button2 = widgets.Button(description='2')
    >>> # Create a grid with two columns, splitting space equally
    >>> layout = widgets.Layout(grid_template_columns='1fr 1fr')
    >>> widgets.GridBox([title_widget, slider, button1, button2], layout=layout)
    """
    _model_name = Unicode('GridBoxModel').tag(sync=True)
    _view_name = Unicode('GridBoxView').tag(sync=True)

@register
class Carousel(Box):
    """ Displays multiple widgets in columns in a Carousel layout.

    Parameters
    ----------
    {box_params}

    Examples
    --------
    >>> import numpy as np
    >>> import matplotlib.pyplot as plt
    >>> import ipywidgets as widgets
    >>>
    >>> carousel = widgets.Carousel()
    >>>
    >>> x = np.arange(20)
    >>> for mean in np.linspace(1, 20, 5):
    >>>     with carousel.capture():
    >>>         plt.plot(x, np.random.randn(len(x)) + mean)
    >>>         plt.show()
    >>>
    >>> carousel
    """
    layout = w.Layout(
        flex_flow='row nowrap',
        overflow_x='auto',
        max_width='100%',
    )
    output_layout = w.Layout()

    @contextmanager
    def capture(self, **kw):
        """Captures output inside a with statement and adds it as a new child.

        Parameters
        ----------
        **kw: additional keyword arguments to pass to Output.
        """
        kw.setdefault('layout', self.output_layout)
        out = Output(**kw)
        self.append_item(out)
        with out:
            yield out

    def append_item(self, child):
        """Appends a new child.

        Parameters
        ----------
        child : Widget
            The child to add.
        """
        self.children += (child,)
