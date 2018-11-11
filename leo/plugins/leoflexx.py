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
import time
assert time
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
    # The main_window component must exist, because other components use it.
    main_window = flx.ComponentProp(settable=True)
    #
    # These components are not needed.
        # ap_to_gnx = flx.DictProp(settable=True)
        # gnx_to_children = flx.DictProp(settable=True)
        # gnx_to_node = flx.DictProp(settable=True)
        # gnx_to_parents = flx.DictProp(settable=True)
        # outline = flx.ListProp(settable=True)

    def init(self):
        self.c, self.g = self.open_bridge()
        #
        # Compute data structures. On my machine, it takes 0.15 sec.
        outline = self.get_outline_list()
        body = self.find_body(gnx=outline[0][1])
            # Get the body text of the first outline node.
        ap_to_gnx = self.compute_archived_position_to_gnx(outline)
        gnx_to_node = self.compute_gnx_to_node(outline)
        gnx_to_parents = self.compute_gnx_to_parents(
            ap_to_gnx, gnx_to_node, outline)
        gnx_to_children = self.compute_gnx_to_children(
            gnx_to_node, gnx_to_parents, outline)
        #
        # Create the main window and all its components.
        main_window = LeoMainWindow(body, outline)
        #
        # Set ivars immediately (and explicitly, for pylint).
        self.ap_to_gnx = ap_to_gnx
        self.gnx_to_children = gnx_to_children
        self.gnx_to_node = gnx_to_node
        self.gnx_to_parents = gnx_to_parents
        self.outline = outline
        #
        # Set properties.
        for name, prop in (
            ('main_window', main_window),
        ):
            self._mutate(name, prop)

    #@+others
    #@+node:ekr.20181110175039.1: *4* app.actions
    @flx.action
    def set_body(self, gnx):
        '''Set the body text in LeoBody to the body text of indicated node.'''
        body = self.find_body(gnx)
        self.main_window.body.set_body(body)
        
    @flx.action
    def send_children_to_tree(self, gnx):
        '''Send the children of the node with the given gnx to the tree.'''
        self.main_window.tree.receive_children({
            'gnx': gnx,
            'parent': self.gnx_to_node[gnx],
            'children': self.gnx_to_children[gnx],
        })
    #@+node:ekr.20181110090611.1: *4* app.ap_to_string
    def ap_to_string(self, ap):
        '''
        Convert an archived position (list of ints) to a string if necessary.
        '''
        if isinstance(ap, (list, tuple)):
            return '.'.join([str(z) for z in ap])
        assert isinstance(ap, str), repr(ap)
        return ap
    #@+node:ekr.20181110101328.1: *4* app.node_tuple_to_string
    def node_tuple_to_string(self, aTuple, ljust=False):

        ap, gnx, headline = aTuple
        s = self.ap_to_string(ap)
        s = s.ljust(17) if ljust else s.rjust(17)
        return '%s %s %s' % (s, gnx.ljust(30), headline)
    #@+node:ekr.20181110084838.1: *4* app.compute_archived_position_to_gnx
    def compute_archived_position_to_gnx (self, outline):
        '''
        Return a dict: keys are *stringized* archived positions. values are gnx's.
        '''
        return { self.ap_to_string(ap): gnx for (ap, gnx, headline) in outline }
    #@+node:ekr.20181110064454.1: *4* app.compute_gnx_to_children
    def compute_gnx_to_children(self, gnx_to_node, gnx_to_parents, outline):
        '''
        Return a dictionary whose keys are gnx's and whose values
        are lists of tuples (archived_position, gnx, headline) of all children.
        '''
        d = {}
        for data in outline:
            ap, gnx, headline = data
            aList = gnx_to_parents.get(gnx, [])
            for parent_data in aList:
                # Add the node to the parents list.
                ap2, gnx2, headline2 = parent_data
                children = d.get(gnx2, [])
                children.append(data)
                d [gnx2] = children
        if 0: # Debugging.
            for data in outline[:20]:
                ap, gnx, headline = data
                # Print the parent.
                print(self.node_tuple_to_string(data, ljust=True))
                # Print the children.
                children = d.get(gnx)
                if children:
                    print('children...')
                    for data2 in children:
                        print(' ' + self.node_tuple_to_string(data2, ljust=False))
                else:
                    print('no children')
                print('-----')
        return d
    #@+node:ekr.20181110063009.1: *4* app.compute_gnx_to_node
    def compute_gnx_to_node (self, outline):
        '''
        Return a dict whose keys are gnx's and values are
        tuples (archived_position, gnx, headline).
        '''
        return { gnx: (archived_position, gnx, headline)
            for archived_position, gnx, headline in outline
        }
    #@+node:ekr.20181110084346.1: *4* app.compute_gnx_to_parents
    def compute_gnx_to_parents(self, ap_to_gnx, gnx_to_node, outline):
        '''
        Return a dictionary whose keys are gnx's and whose values are lists of
        tuples (archived_position, gnx, headline) of all parents.
        '''
        d = {}
        for ap, gnx, headline in outline:
            aList = d.get(gnx, [])
            parent_ap = ap[:-1]
            if parent_ap:
                parent_gnx = ap_to_gnx.get(self.ap_to_string(parent_ap))
                assert parent_gnx, repr(parent_ap)
                parent_data = gnx_to_node.get(parent_gnx)
                assert parent_data, gnx
                aList.append(parent_data)
            d [gnx] = aList
        if 0: # Debugging.
            for ap, gnx, headline in outline[:20]:
                aList = d.get(gnx)
                # Print the node.
                data = gnx_to_node.get(gnx)
                assert data, gnx
                ap, gnx, h = data
                print(self.ap_to_string(ap).ljust(17), gnx.ljust(15), h)
                # Print the parents.
                if aList:
                    print(len(aList), 'parent%s...' % self.g.plural(len(aList)))
                    for ap, gnx, h in aList:
                        print(self.ap_to_string(ap).rjust(17), gnx.ljust(15), h)
                else:
                    print('no parents')
                print('-----')
        return d
    #@+node:ekr.20181105160448.1: *4* app.find_body
    def find_body(self, gnx):
        
        c = self.c
        for v in c.all_nodes():
            if v.gnx == gnx:
                return v.b
        return 'app.find_body: NOT FOUND: %r' % (gnx)
    #@+node:ekr.20181105095150.1: *4* app.get_outline_list
    def get_outline_list(self):
        '''
        Return a serializable representation of the outline for the LeoTree
        class.
        '''
        c = self.c
        return [(p.archivedPosition(), p.gnx, p.h) for p in c.all_positions()]
    #@+node:ekr.20181105091545.1: *4* app.open_bridge
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
        
    @flx.action
    def set_body(self, body):
        # print('LeoBody.set_body', repr(body))
        self.ace.setValue(body)
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
            
    #@+others
    #@+node:ekr.20181110125347.1: *4* LeoMainWindow.format_node_tuple
    def format_node_tuple(self, node_tuple):
        assert isinstance(node_tuple, (list, tuple)), repr(node_tuple)
        ap, gnx, headline = node_tuple
        s = '.'.join([str(z) for z in ap])
        return 'p: %s %s %s' % (s.ljust(15), gnx.ljust(30), headline)
    #@-others
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
    #@+node:ekr.20181110175222.1: *4* tree.actions
    @flx.action
    def receive_children(self, d):
        format_node_tuple = self.root.main_window.format_node_tuple
        ap, gnx, headline = d.get('parent')
        assert gnx == d.get('gnx'), (repr(gnx), repr(d.get('gnx')))
        if 0: # Debugging.
            print('tree.receive_children: parent...')
            print(format_node_tuple(d.get('parent')))
        if 1:
            print('tree.receive_children: children...')
            for node_tuple in d.get('children'):
                print(format_node_tuple(node_tuple))
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
        '''
        Update the tree and body text when the user selects a new tree node.
        '''
        main = self.root.main_window
        for ev in events:
            if ev.new_value:
                # We are selecting a node, not de-selecting it.
                gnx = ev.source.leo_gnx
                headline = ev.source.title or ev.source.text
                main.log.put('select %s %s' % (gnx.ljust(25), headline))
                self.root.set_body(gnx)
                    # Set the body text directly.
                self.root.send_children_to_tree(gnx)
                    # Send the children back to us so.
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
    
    def init(self, leo_gnx, leo_position):
        # pylint: disable=arguments-differ
        super().init()
        # These will probably never need to be properties.
        self.leo_gnx = leo_gnx
        self.leo_position = leo_position
#@-others
if __name__ == '__main__':
    flx.launch(LeoApp)
    print('After flx.launch')
    flx.run()
#@-leo
