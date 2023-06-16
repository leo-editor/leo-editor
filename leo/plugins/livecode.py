#@+leo-ver=5-thin
#@+node:tbrown.20140806084727.30174: * @file ../plugins/livecode.py
"""
Show results of code in another pane as it's edited.

livecode-show opens the livecode pane on c.p.

Thereafter, pressing return in that body pane re-evaluates the code.

The livecode pane shows the results of each line.
"""

# By TNB

import ast
from collections import namedtuple
try:
    from meta import asttools
except ImportError:
    asttools = None
from leo.core import leoGlobals as g
from leo.core.leoQt import QtWidgets
#
# Fail fast, right after all imports.
g.assertUi('qt')  # May raise g.UiTypeException, caught by the plugins manager.

#@+others
#@+node:tbrown.20140806084727.30178: ** init
warning_given = False

def init():
    """Return True if the plugin has loaded successfully."""
    global warning_given
    if g.unitTesting:
        return False
    if not asttools:
        if not warning_given:
            warning_given = True
            g.es_print('livecode.py: can not import meta')
            g.es_print('you can install meta with `pip install meta`')
        return False
    g.registerHandler('after-create-leo-frame', onCreate)
    g.plugin_signon(__name__)
    return True
#@+node:tbrown.20140806084727.30179: ** onCreate
def onCreate(tag, keys):

    c = keys.get('c')

    LiveCodeDisplayProvider(c)
#@+node:tbrown.20140806084727.31749: ** livecode-show
@g.command('livecode-show')
def cmd_show(event):
    c = event.get('c')
    splitter = c.free_layout.get_top_splitter()
    if splitter:
        w = splitter.get_provided('_leo_livecode_show')
        splitter.add_adjacent(w, 'bodyFrame')
#@+node:tbrown.20140806084727.30187: ** class LiveCodeDisplay
class LiveCodeDisplay:
    """Manage a pane showing livecode"""

    CodeBlock = namedtuple('CodeBlock', 'code, result')

    #@+others
    #@+node:tbrown.20140806084727.30188: *3* __init__ (livecode.py)
    def __init__(self, c):

        self.c = c
        c._livecode = self
        self.v = c.p.v

        self.active = True
        self.codeblocks = []
        self.scope = {'c': c, 'g': g}
        self.dump = False

        self._build_gui()


        g.registerHandler('idle', self.update)
    #@+node:tbrown.20140806084727.39166: *3* _build_gui
    def _build_gui(self):
        self.w = w = QtWidgets.QWidget()

        w.setObjectName('show_livecode')
        w.setLayout(QtWidgets.QVBoxLayout())
        self.status = QtWidgets.QLabel()
        w.layout().addWidget(self.status)
        self.text = QtWidgets.QTextBrowser()
        w.layout().addWidget(self.text)
        h = QtWidgets.QHBoxLayout()
        w.layout().addLayout(h)
        self.activate = QtWidgets.QPushButton("Stop")
        self.activate.setToolTip("Start / stop live code display")
        h.addWidget(self.activate)
        self.activate.clicked.connect(lambda checked: self.toggle_active())
        b = QtWidgets.QPushButton("Run here")
        b.setToolTip("Show live code for this node")
        h.addWidget(b)
        b.clicked.connect(lambda checked: self.run_here())
        b = QtWidgets.QPushButton("Go to node")
        b.setToolTip("Jump to node where live code is shown")
        h.addWidget(b)
        b.clicked.connect(lambda checked: self.goto_node())
        b = QtWidgets.QPushButton("Dump")
        b.setToolTip("AST dump to stdout (devel. option)")
        h.addWidget(b)
        b.clicked.connect(lambda checked, self=self:
                          setattr(self, 'dump', True))
    #@+node:tbrown.20140806084727.31745: *3* goto_node
    def goto_node(self):

        self.c.selectPosition(self.c.vnode2position(self.v))

    #@+node:tbrown.20140806084727.31747: *3* run_here
    def run_here(self):

        self.codeblocks = []
        self.v = self.c.p.v
        self.active = True

    #@+node:tbrown.20140806084727.31744: *3* toggle_active
    def toggle_active(self):

        self.active = not self.active
        self.status.setText("ACTIVE" if self.active else "(paused)")
        self.activate.setText("STOP" if self.active else "START")
    #@+node:tbrown.20140806084727.31743: *3* update
    def update(self, tag, kwargs):
        """update - Return
        """
        c = self.c
        if kwargs['c'] != c:
            return
        if not self.w.isVisible():
            return
        if c.p.v != self.v:
            self.status.setText("(paused - different node)")
            return
        if not self.active:
            return
        self.status.setText("ACTIVE")
        source = c.p.b
        lines = source.split('\n')
        try:
            top_level = ast.parse(source)
        except SyntaxError:
            self.status.setText("ACTIVE - INCOMPLETE CODE")
            return
        if self.dump:
            self.dump = False
            print(ast.dump(top_level))
        block = []  # blocks (strings) of source code
        nodes = list(ast.iter_child_nodes(top_level))
        self.scope['p'] = c.p
        run_count = 0
        # break source up into blocks corresponding to top level nodes
        for n, node in enumerate(nodes):
            if n == len(nodes) - 1:
                next_node = len(lines)
            else:
                next_node = nodes[n + 1].lineno
            block.append("".join(lines[node.lineno - 1 : next_node - 1]))
        result = []
        for n, node in enumerate(nodes):
            node_result = None
            if (n < len(self.codeblocks) and
                self.codeblocks[n].code == block[n]
            ):
                # same code, assume same result
                node_result = self.codeblocks[n].result
            else:
                run_count += 1
                # drop all remaining stored results (maybe none)
                del self.codeblocks[n:]
                try:
                    if isinstance(node, ast.Expr):
                        # pylint: disable=eval-used
                        node_result = repr(eval(block[n], self.scope))
                    else:
                        # exec block[n] in self.scope
                        # EKR: Python 3 compatibility.
                        exec(block[n], self.scope)
                except Exception:
                    self.status.setText("ACTIVE: fail at %s" %
                        block[n].split('\n')[0])
                    break
                if isinstance(node, ast.Expr):
                    pass  # already handled above
                elif isinstance(node, (ast.Assign, ast.AugAssign)):
                    node_result = []
                    if isinstance(node, ast.AugAssign):
                        todo = [node.target]
                    else:
                        todo = list(node.targets)  # type:ignore
                    while todo:
                        target = todo.pop(0)
                        if isinstance(target, ast.Tuple):
                            todo.extend(target.elts)  # type:ignore
                            continue
                        code = asttools.dump_python_source(target)
                        # pylint: disable=eval-used
                        node_result.append("%s = %r" %
                            (code.strip(), eval(code, self.scope)))
                    node_result = ''.join(node_result)  # was '\n'.join
            assert node_result is None or isinstance(node_result, str)
            if node_result is None:
                self.codeblocks.append(self.CodeBlock(block[n], None))
            else:
                self.codeblocks.append(self.CodeBlock(block[n], node_result))
                result.append(node_result)
        self.text.setText('\n'.join(result))
        if run_count:
            self.status.setText("ACTIVE: %d blocks" % run_count)
    #@-others
#@+node:tbrown.20140806084727.30203: ** class LiveCodeDisplayProvider
class LiveCodeDisplayProvider:
    #@+others
    #@+node:tbrown.20140806084727.30204: *3* __init__
    def __init__(self, c):
        self.c = c

        splitter = c.free_layout.get_top_splitter()
        if splitter:
            splitter.register_provider(self)
    #@+node:tbrown.20140806084727.30205: *3* ns_provides
    def ns_provides(self):
        return [('Live Code', '_leo_livecode_show')]
    #@+node:tbrown.20140806084727.30206: *3* ns_provide
    def ns_provide(self, id_):
        if id_.startswith('_leo_livecode_show'):
            c = self.c
            if not hasattr(c, '_livecode'):
                c._livecode = LiveCodeDisplay(self.c)
            return c._livecode.w
        return None
    #@-others
#@-others
#@@language python
#@@tabwidth -4

#@-leo
