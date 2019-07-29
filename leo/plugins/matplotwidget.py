from leo.core.leoQt import QtCore, QtGui, QtWidgets
import leo.core.leoGlobals as g
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT
from matplotlib.figure import Figure
import matplotlib


class Matplot_Widget(QtWidgets.QWidget):
    def __init__(self, parent=None, leo_com=None):
        super(Matplot_Widget, self).__init__(parent)
        c = leo_com
        c._matplot = self
        self.c = c
        self.layout = QtWidgets.QVBoxLayout()
        self.message = QtWidgets.QLabel(
            "How to use this:\n1. After ax creating call \"c._matplot.connect_ax_to_widget(plt)\"\n2. Use plt.draw() instead of plt.show()", self
        )
        self.layout.addWidget(self.message)        
        self.figure = Figure()
        self.figure.set_tight_layout(True)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.toolBar = NavigationToolbar2QT(self.canvas, self)
        self.toolBar.setStyleSheet(
            """
        QWidget{
            background-color: white;
            }
        """
        )

        self.layout.addWidget(self.canvas)
        self.layout.addWidget(self.toolBar)
        self.setLayout(self.layout)

    def connect_ax_to_widget(self, active_plt):
        self.message.hide()
        cloned_axes = []
        active_plt.gcf().set_size_inches(self.figure.get_size_inches(), forward=True)
        
        for ax in active_plt.gcf().axes:
            ax.remove()
            cloned_axes.append(ax)

        active_plt.close("all")
        active_plt.ioff()
        plt_fig = active_plt.gcf()
        plt_manager = plt_fig.canvas.manager
        plt_manager.canvas = self.canvas
        plt_fig.set_canvas(plt_manager.canvas)
        matplotlib.use("Agg")
        active_plt.clf()

        self.figure.set_tight_layout(True)
        for ax in cloned_axes:
            ax.figure = self.figure
            self.figure.add_axes(ax)
        self.figure.canvas.draw()

def init():
    g.plugin_signon(__name__)
    g.registerHandler("after-create-leo-frame", onCreate)
    return True


def onCreate(tag, keys):
    c = keys.get("c")
    if not c:
        return

    dw = c.frame.top
    dock = dw.createDockWidget(
        closeable=True, moveable=True, height=150, name="Matplot"
    )
    dw.leo_docks.append(dock)
    dock.setWidget(Matplot_Widget(leo_com=c))
    dw.splitDockWidget(dw.body_dock, dock, QtCore.Qt.Horizontal)
    dock.show()
