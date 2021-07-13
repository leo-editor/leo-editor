#@+leo-ver=5-thin
#@+node:ekr.20160928073518.1: * @file ../plugins/pyplot_backend.py
'''
    A helper for the viewrendered plugin.
    This is *NOT* a real plugin.
'''
#@+<< pyplot_backend imports >>
#@+node:ekr.20160928074801.1: ** << pyplot_backend imports >>
from leo.core import leoGlobals as g
from leo.plugins import viewrendered as vr
from leo.core.leoQt import isQt5, isQt6, QtWidgets
from leo.core.leoQt import FocusPolicy
try:
    if isQt5 or isQt6:
        import matplotlib.backends.backend_qt5agg as backend_qt5agg
        FigureCanvasQTAgg = backend_qt5agg.FigureCanvasQTAgg
    else:
        import matplotlib.backends.backend_qt4agg as backend_qt4agg
        FigureCanvasQTAgg = backend_qt4agg.FigureCanvasQTAgg
    # Common imports
    import matplotlib.backends.backend_qt5 as backend_qt5
    import matplotlib.backend_bases as backend_bases
    from matplotlib.figure import Figure
    FigureManagerBase = backend_bases.FigureManagerBase

except ImportError:
    g.es_exception()
#@-<< pyplot_backend imports >>
#@+others
#@+node:ekr.20160928073605.1: ** init
def init():
    '''Return True if the plugin has loaded successfully.'''
    g.trace('pyplot_backend.py is not a plugin.')
    return False
#@+node:ekr.20160928082006.1: ** Leo backend
#@+node:ekr.20160928074615.2: *3* new_figure_manager
def new_figure_manager(num, *args, **kwargs):
    """
    Create a new figure manager instance
    """
    FigureClass = kwargs.pop('FigureClass', Figure)
    thisFig = FigureClass(*args, **kwargs)
    return new_figure_manager_given_figure(num, thisFig)
#@+node:ekr.20160928074615.3: *3* new_figure_manager_given_figure
def new_figure_manager_given_figure(num, figure):
    """
    Create a new figure manager instance for the given figure.
    """
    canvas = FigureCanvasQTAgg(figure)
    return LeoFigureManagerQT(canvas, num)
#@+node:ekr.20160929050151.1: *3* class LeoFigureManagerQT
# From backend_qt5.py

# pylint: disable=no-member
    # matplotlib.backends.backend_qt5.FigureManager probably does exist. See:
    # https://github.com/matplotlib/matplotlib/blob/master/lib/matplotlib/backends/backend_qt5.py

class LeoFigureManagerQT(backend_qt5.FigureManager):
    """
    Public attributes

    canvas      : The FigureCanvas instance
    num         : The Figure number
    toolbar     : The qt.QToolBar
    window      : The qt.QMainWindow (not set)
    """

    #@+others
    #@+node:ekr.20160929050151.2: *4* __init__ (LeoFigureManagerQt)
    # Do NOT call the base class ctor. It creates a Qt MainWindow.
        # pylint: disable=super-init-not-called
        # pylint: disable=non-parent-init-called

    def __init__(self, canvas, num):
        '''Ctor for the LeoFigureManagerQt class.'''
        self.c = c = g.app.log.c
        super().__init__(canvas, num)
        self.canvas = canvas

        # New code for Leo: embed the canvas in the viewrendered area.
        self.vr_controller = vc = vr.controllers.get(c.hash())
        self.splitter = c.free_layout.get_top_splitter()
        self.frame = w = QtWidgets.QFrame()
        w.setLayout(QtWidgets.QVBoxLayout())
        w.layout().addWidget(self.canvas)
        if vc:
            vc.embed_widget(w)

        class DummyWindow:

            def __init__(self, c):
                self.c = c
                self._destroying = None

            def windowTitle(self):
                return self.c.p.h

        self.window = DummyWindow(c)

        # See comments in the base class ctor, in backend_qt5.py.
        self.canvas.setFocusPolicy(FocusPolicy.StrongFocus)
        self.canvas.setFocus()
        self.canvas._destroying = False

        self.toolbar = self._get_toolbar(self.canvas, self.frame)
        if self.toolbar is not None:
            # The toolbar is a backend_qt5.NavigationToolbar2QT.
            layout = self.frame.layout()
            layout.addWidget(self.toolbar)
            # add text label to status bar
            self.statusbar_label = QtWidgets.QLabel()
            layout.addWidget(self.statusbar_label)
            # pylint: disable=no-member
            if isQt5 or isQt6:
                pass # The status bar doesn't work yet.
            else:
                self.toolbar.message.connect(self._show_message)

        self.canvas.draw_idle()

        def notify_axes_change(fig):
            # This will be called whenever the current axes is changed
            if self.toolbar is not None:
                self.toolbar.update()

        self.canvas.figure.add_axobserver(notify_axes_change)
    #@+node:ekr.20160929083114.1: *4* destroy
    def destroy(self, *args):
        # Causes problems.
        # self.frame.deleteLater()
        self.frame = None
    #@-others
#@-others
#@@language python
#@-leo
