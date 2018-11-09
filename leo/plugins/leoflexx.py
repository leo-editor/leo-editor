# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20181103094900.1: * @file leoflexx.py
#@@first
#@@language python
#@@tabwidth -4
'''
A Stand-alone prototype for Leo using flexx.
'''
import leo.core.leoBridge as leoBridge
from flexx import flx
import pscript
assert pscript # To suppress pyflakes complaint.
#@+others
#@+node:ekr.20181103151350.1: **  init
def init():
    # At present, leoflexx is not a true plugin.
    # I am executing leoflexx.py from an external script.
    return False
#@+node:ekr.20181107053436.1: ** Py side: flx.PyComponents
# pscript never converts flx.PyComponents to JS.
#@+node:ekr.20181107052522.1: *3* class LeoApp
class LeoApp(flx.PyComponent):
    '''
    The Leo Application.
    This is self.root for all flx.Widget objects!
    '''

    main_window = flx.ComponentProp(settable=True)
    outline = flx.ListProp(settable=True)

    # https://github.com/flexxui/flexx/issues/489
    def init(self):
        self.c, self.g = self.open_bridge()
        body = self.find_body()
        outline = self.get_outline_list()
        main_window = LeoMainWindow(body, outline)
        self._mutate('outline', outline)
        self._mutate('main_window', main_window)
        
    @flx.reaction('!ask_for_children')
    def ask_for_children(self, *events):
        print('===== app.ask_for_children')
        self.get_children({'children', 'CHILDREN'})
        
    # Emitters should return a dictionary.
    # Event type is the name of the emitter.
    @flx.emitter
    def get_children(self, d):
        print('===== app.get_children', repr(d))
        return d

    #@+others
    #@+node:ekr.20181105091545.1: *4* gui.open_bridge
    def open_bridge(self):
        '''Can't be in JS.'''
        bridge = leoBridge.controller(gui = None,
            loadPlugins = False,
            readSettings = False,
            silent = False,
            tracePlugins = False,
            verbose = False, # True: prints log messages.
        )
        if not bridge.isOpen():
            print('Error opening leoBridge')
            return
        g = bridge.globals()
        path = g.os_path_finalize_join(g.app.loadDir, '..', 'core', 'LeoPyRef.leo')
        if not g.os_path_exists(path):
            print('open_bridge: does not exist:', path)
            return
        c = bridge.openLeoFile(path)
        ### runUnitTests(c, g)
        return c, g
    #@+node:ekr.20181105160448.1: *4* gui.find_body
    def find_body(self):
        
        c = self.c
        for p in c.p.self_and_siblings():
            if p.b.strip():
                return p.b
        return ''
    #@+node:ekr.20181105095150.1: *4* gui.get_outline_list
    def get_outline_list(self):
        '''
        Return a serializable representation of the outline for the LeoTree
        class.
        '''
        c = self.c
        return [(p.archivedPosition(), p.gnx, p.h) for p in c.all_positions()]
    #@-others
#@+node:ekr.20181107052700.1: ** Js side: flx.Widgets
#@+node:ekr.20181104082144.1: *3* class LeoBody
base_url = 'https://cdnjs.cloudflare.com/ajax/libs/ace/1.2.6/'
flx.assets.associate_asset(__name__, base_url + 'ace.js')
flx.assets.associate_asset(__name__, base_url + 'mode-python.js')
flx.assets.associate_asset(__name__, base_url + 'theme-solarized_dark.js')

class LeoBody(flx.Widget):
    
    """ A CodeEditor widget based on Ace.
    """

    CSS = """
    .flx-CodeEditor > .ace {
        width: 100%;
        height: 100%;
    }
    """

    def init(self, body):
        # pylint: disable=arguments-differ
        # pylint: disable=undefined-variable
            # window
        global window
        self.ace = window.ace.edit(self.node, "editor")
        self.ace.setValue(body)
            # Trying to access global body yields:
            # JS: TypeError: e.match is not a function
        self.ace.navigateFileEnd()  # otherwise all lines highlighted
        self.ace.setTheme("ace/theme/solarized_dark")
        self.ace.getSession().setMode("ace/mode/python")

    @flx.reaction('size')
    def __on_size(self, *events):
        self.ace.resize()
#@+node:ekr.20181104082149.1: *3* class LeoLog
class LeoLog(flx.Widget):

    CSS = """
    .flx-CodeEditor > .ace {
        width: 100%;
        height: 100%;
    }
    """

    def init(self):
        # pylint: disable=undefined-variable
            # window
        global window
        self.ace = window.ace.edit(self.node, "editor")
        self.ace.navigateFileEnd()  # otherwise all lines highlighted
        # pscript.RawJS('''
            # var el = this.node;
            # var editor = el.data('ace').editor;
            # editor.blockScrolling = Infinity;
        # ''')
        self.ace.setTheme("ace/theme/solarized_dark")
        
    def put(self, s):
        self.ace.setValue(self.ace.getValue() + '\n' + s)

    @flx.reaction('size')
    def __on_size(self, *events):
        self.ace.resize()
#@+node:ekr.20181104082130.1: *3* class LeoMainWindow
class LeoMainWindow(flx.Widget):
    
    '''
    Leo's main window, that is, root.main_window.
    
    Each property x below is accessible as root.main_window.x.
    '''
    
    body = flx.ComponentProp(settable=True)
    log = flx.ComponentProp(settable=True)
    minibuffer = flx.ComponentProp(settable=True)
    status_line = flx.ComponentProp(settable=True)
    tree = flx.ComponentProp(settable=True)

    def init(self, body, outline):
        # pylint: disable=arguments-differ
        with flx.VSplit():
            with flx.HSplit(flex=1):
                tree = LeoTree(outline, flex=1)
                log = LeoLog(flex=1)
            body = LeoBody(body, flex=1)
            minibuffer = LeoMiniBuffer()
            status_line = LeoStatusLine()
        for name, prop in (
            ('body', body), ('log', log), ('tree', tree),
            ('minibuffer', minibuffer),
            ('status_line', status_line),
        ):
            self._mutate(name, prop)
#@+node:ekr.20181104082154.1: *3* class LeoMiniBuffer
class LeoMiniBuffer(flx.Widget):
    
    widget = flx.ComponentProp(settable=True)
    
    def init(self): 
        with flx.HBox():
            flx.Label(text='Minibuffer')
            widget = flx.LineEdit(flex=1, placeholder_text='Enter command')
        widget.apply_style('background: yellow')
        self._mutate('widget', widget)
#@+node:ekr.20181104082201.1: *3* class LeoStatusLine
class LeoStatusLine(flx.Widget):
    
    widget = flx.ComponentProp(settable=True)
    
    def init(self):
        with flx.HBox():
            flx.Label(text='Status Line')
            widget = flx.LineEdit(flex=1, placeholder_text='Status')
        widget.apply_style('background: green')
        self._mutate('widget', widget)
#@+node:ekr.20181104082138.1: *3* class LeoTree
class LeoTree(flx.Widget):

    CSS = '''
    .flx-TreeWidget {
        background: #000;
        color: white;
        /* background: #ffffec; */
        /* Leo Yellow */
        /* color: #afa; */
    }
    '''
    
    def init(self, outline):
        # pylint: disable=arguments-differ
        with flx.TreeWidget(flex=1, max_selected=1) as self.tree:
            self.make_tree(outline)

    #@+others
    #@+node:ekr.20181105045657.1: *4* tree.make_tree
    def make_tree(self, outline):
        '''Populate the outline from a list of tuples.'''
        for p, gnx, h in outline:
            # p is an archived position, a list of ints.
            if len(p) == 1:
                LeoTreeItem(gnx, p, text=h, checked=None, collapsed=True)

        ### Old code.
        # stack = []
        
        # def tree_item(gnx, h, p):
            # return LeoTreeItem(gnx, p, text=h, checked=None, collapsed=True)

        # for p, gnx, h in outline:
            # n = len(p) # p is an archived position, a list of ints.
            # if n == 1:
                # stack = [tree_item(gnx, h, p)]
            # elif n in (2, 3):
                # # Fully expanding the stack takes too long.
                # stack = stack[:n-1]
                # with stack[-1]:
                    # stack.append(tree_item(gnx, h, p))
    #@+node:ekr.20181104080854.3: *4* tree.on_tree_event
    # actions: set_checked, set_collapsed, set_parent, set_selected, set_text, set_visible
    @flx.reaction(
        'tree.children**.checked',
        'tree.children**.collapsed',
        'tree.children**.visible', # Never seems to fire.
    )
    def on_tree_event(self, *events):
        for ev in events:
            self.show_event(ev)
    #@+node:ekr.20181109083659.1: *4* tree.on_selected_event
    @flx.reaction('tree.children**.selected')
    def on_selected_event(self, *events):
        main = self.root.main_window
        for ev in events:
            if ev.new_value:
                gnx = ev.source.leo_gnx
                h = ev.source.title or ev.source.text
                main.log.put('select gnx: %s %s' % (gnx.ljust(30), h))
                self.ask_for_children(gnx)
                ### flx.Component.emit('ask_for_children', {'gnx', gnx})

    # Emitters can have any number of arguments.
    # Emitters should return a dictionary, which will get emitted as an event,
    # with the event type matching the name of the emitter.
    @flx.emitter
    def ask_for_children(self, gnx):
        print('tree.ask_for_children')
        return {'gnx': gnx}

    @flx.reaction('!get_children')
    def get_children(self, *events):
        print('tree.get_children')
        for ev in events:
            print(repr(ev))
        ### main.log.put('children: %r' % children)
    #@+node:ekr.20181108232118.1: *4* tree.show_event
    def show_event(self, ev):
        '''Put a description of the event to the log.'''
        log = self.root.main_window.log
        id_ = ev.source.title or ev.source.text
        kind = '' if ev.new_value else 'un-'
        s = kind + ev.type
        log.put('%s: %s' % (s.rjust(15), id_))
    #@-others
#@+node:ekr.20181108233657.1: *3* class LeoTreeItem
class LeoTreeItem(flx.TreeItem):

    leo_gnx = flx.StringProp(settable=True)
    leo_position = flx.ListProp(settable=True)
        # Archived positions are lists of ints.
    
    def init(self, leo_gnx, leo_position):
        # pylint: disable=arguments-differ
        super().init()
        self._mutate('leo_gnx', leo_gnx)
        self._mutate('leo_position', leo_position)
#@-others
if __name__ == '__main__':
    flx.launch(LeoApp)
    print('After flx.launch')
    flx.run()
#@-leo
