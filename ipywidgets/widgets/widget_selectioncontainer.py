# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

"""SelectionContainer class.

Represents a multipage container that can be used to group other widgets into
pages.
"""

from contextlib import contextmanager
from .widget_box import Box
from .widget_output import Output
from .widget import register
from .widget_core import CoreWidget
from traitlets import Unicode, Dict, CInt, TraitError, validate
from ipython_genutils.py3compat import unicode_type


class _SelectionContainer(Box, CoreWidget):
    """Base class used to display multiple child widgets."""
    _titles = Dict(help="Titles of the pages").tag(sync=True)
    selected_index = CInt(
        help="""The index of the selected page. This is either an integer selecting a particular sub-widget, or None to have no widgets selected.""",
        allow_none=True
    ).tag(sync=True)

    @validate('selected_index')
    def _validated_index(self, proposal):
        if proposal.value is None or 0 <= proposal.value < len(self.children):
            return proposal.value
        else:
            raise TraitError('Invalid selection: index out of bounds')

    # Public methods
    def set_title(self, index, title):
        """Sets the title of a container page.

        Parameters
        ----------
        index : int
            Index of the container page
        title : unicode
            New title
        """
        # JSON dictionaries have string keys, so we convert index to a string
        index = unicode_type(int(index))
        self._titles[index] = title
        self.send_state('_titles')

    def get_title(self, index):
        """Gets the title of a container pages.

        Parameters
        ----------
        index : int
            Index of the container page
        """
        # JSON dictionaries have string keys, so we convert index to a string
        index = unicode_type(int(index))
        if index in self._titles:
            return self._titles[index]
        else:
            return None

    @contextmanager
    def capture(self, title=None, selected=None, **kw):
        """Captures output inside a with statement and adds it as a new child.

        Parameters
        ----------
        title : str
            Title of the child.
        selected: bool
            If true, set this child as selected.
        **kw: additional keyword arguments to pass to Output.
        """
        out = Output(**kw)
        self.append_item(out, title, selected=selected)
        with out:
            yield out

    def append_item(self, child, title=None, selected=None):
        """Appends a new child.

        Parameters
        ----------
        child : Widget
            The child to add.
        title : str
            Title of the child.
        selected: bool
            If true, set this child as selected.
        """
        self.children += (child,)
        if title:
            self.set_title(len(self.children) - 1, title)
        if selected:
            self.selected_index = len(self.children) - 1

    def iter_capture(self, items, as_title=False, **kw):
        """Capture each iterable item in a new child.

        Parameters
        ----------
        as_title : bool, callable, None
            If true, set the iterable item as the title.
            If callable, call as_title with the item as an argument,
            returning the title.
            If None (default), add no title.
        **kw: additional keyword arguments to pass to self.capture.
        """
        items = (x for x in items)
        while True:
            with self.capture(**kw) as o:
                try:
                    i = next(items)
                    # any output from as_title is inside the output widget
                    title = as_title and (as_title(i) if callable(as_title) else i)
                    if title:
                        self.set_title(len(self.children) - 1, title)
                    yield i
                except StopIteration:
                    break
                except KeyboardInterrupt:
                    break

    def _repr_keys(self):
        # We also need to include _titles in repr for reproducibility
        for key in super(_SelectionContainer, self)._repr_keys():
            yield key
        if self._titles:
            yield '_titles'


@register
class Accordion(_SelectionContainer):
    """Displays children each on a separate accordion page."""
    _view_name = Unicode('AccordionView').tag(sync=True)
    _model_name = Unicode('AccordionModel').tag(sync=True)


@register
class Tab(_SelectionContainer):
    """Displays children each on a separate accordion tab."""
    _view_name = Unicode('TabView').tag(sync=True)
    _model_name = Unicode('TabModel').tag(sync=True)
