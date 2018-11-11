# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20181103094900.1: * @file leoflexx.py
#@@first
#@@language python
#@@tabwidth -4
'''
A Stand-alone prototype for Leo using flexx.
'''
# pylint: disable=logging-not-lazy
import leo.core.leoBridge as leoBridge
from flexx import flx
import re
import time
assert re and time
    # Suppress pyflakes complaints
#@+<< ace assets >>
#@+node:ekr.20181111074958.1: ** << ace assets >>
# Assets for ace, embedded in the LeoBody and LeoLog classes.
base_url = 'https://cdnjs.cloudflare.com/ajax/libs/ace/1.2.6/'
flx.assets.associate_asset(__name__, base_url + 'ace.js')
flx.assets.associate_asset(__name__, base_url + 'mode-python.js')
flx.assets.associate_asset(__name__, base_url + 'theme-solarized_dark.js')
#@-<< ace assets >>
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
    def init(self):
        self.c, self.g = self.open_bridge()
        #
        # Compute data structures. On my machine, it takes 0.15 sec.
        t1 = time.clock()
        self.outline = self.get_outline_list()
        self.ap_to_gnx = self.compute_ap_to_gnx(self.outline)
        self.gnx_to_body = self.compute_gnx_to_body(self.outline)
        self.gnx_to_node = self.compute_gnx_to_node(self.outline)
        self.gnx_to_parents = self.compute_gnx_to_parents(
            self.ap_to_gnx, self.gnx_to_node, self.outline)
        self.gnx_to_children = self.compute_gnx_to_children(
            self.gnx_to_node, self.gnx_to_parents, self.outline)
        t2 = time.clock()
        flx.logger.info('LeoApp.init: %5.2f sec.' % (t2-t1))
        #
        # Create the main window and all its components.
        first_gnx = self.outline[0][1]
        body = self.gnx_to_body[first_gnx]
        self.main_window = LeoMainWindow(body, self.outline)

    #@+others
    #@+node:ekr.20181111095640.1: *4* app.action: send_children_to_tree
    @flx.action
    def send_children_to_tree(self, gnx):
        '''Send the children of the node with the given gnx to the tree.'''
        children = self.gnx_to_children.get(gnx) or []
        self.main_window.tree.receive_children({
            'gnx': gnx,
            'parent': self.gnx_to_node[gnx],
            'children': children,
        })
        
    #@+node:ekr.20181111095637.1: *4* app.action: set_body
    @flx.action
    def set_body(self, gnx):
        '''Set the body text in LeoBody to the body text of indicated node.'''
        body = self.gnx_to_body[gnx]
        self.main_window.body.set_body(body)

    #@+node:ekr.20181111095640.2: *4* app.action: set_status_to_unl
    @flx.action
    def set_status_to_unl(self, ap, gnx):
        c, g = self.c, self.g
        unls = []
        for i in range(len(ap)):
            ap_s = self.ap_to_string(ap[:i+1])
            gnx = self.ap_to_gnx.get(ap_s)
            data = self.gnx_to_node.get(gnx, [])
            unls.append(data[2] if data else '<not found: %s>' % ap_s)
        fn = g.shortFileName(c.fileName())
        fn = fn + '#' if fn else ''
        self.main_window.status_line.set_text(fn + '->'.join(unls))
    #@+node:ekr.20181110090611.1: *4* app.ap_to_string
    def ap_to_string(self, ap):
        '''
        Convert an archived position (list of ints) to a string if necessary.
        '''
        if isinstance(ap, (list, tuple)):
            return '.'.join([str(z) for z in ap])
        assert isinstance(ap, str), repr(ap)
        return ap
    #@+node:ekr.20181110084838.1: *4* app.compute_ap_to_gnx
    def compute_ap_to_gnx (self, outline):
        '''
        Return a dict: keys are *stringized* archived positions. values are gnx's.
        '''
        return { self.ap_to_string(ap): gnx for (ap, gnx, headline) in outline }
    #@+node:ekr.20181111002718.1: *4* app.compute_gnx_to_body
    def compute_gnx_to_body(self, outline):
        '''
        Return a dict: keys are gnx's. values are body strings.
        '''
        return { v.gnx: v.b for v in self.c.all_unique_nodes() }
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
    #@+node:ekr.20181105095150.1: *4* app.get_outline_list
    def get_outline_list(self):
        '''
        Return a serializable representation of the outline for the LeoTree
        class.
        '''
        c = self.c
        return [(p.archivedPosition(), p.gnx, p.h) for p in c.all_positions()]
    #@+node:ekr.20181110101328.1: *4* app.node_tuple_to_string
    def node_tuple_to_string(self, aTuple, ljust=False):

        ap, gnx, headline = aTuple
        s = self.ap_to_string(ap)
        s = s.ljust(17) if ljust else s.rjust(17)
        return '%s %s %s' % (s, gnx.ljust(30), headline)
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
            flx.logger.error('Error opening leoBridge')
            return
        g = bridge.globals()
        path = g.os_path_finalize_join(g.app.loadDir, '..', 'core', 'LeoPyRef.leo')
        if not g.os_path_exists(path):
            flx.logger.error('open_bridge: does not exist: %r' % path)
            return
        c = bridge.openLeoFile(path)
        ### runUnitTests(c, g)
        return c, g
    #@-others
#@+node:ekr.20181107052700.1: ** Js side: flx.Widgets
#@+node:ekr.20181104082144.1: *3* class LeoBody

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
        self.ace.navigateFileEnd()  # otherwise all lines highlighted
        self.ace.setTheme("ace/theme/solarized_dark")
        self.ace.getSession().setMode("ace/mode/python")
        # RawJS('''
        # var el = this.node;
            # var editor = el.data('ace').editor;
            # editor.blockScrolling = Infinity;
        # ''')
        self.set_body(body)

    @flx.reaction('size')
    def __on_size(self, *events):
        self.ace.resize()
        
    @flx.action
    def set_body(self, body):
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
    # These properties *are* needed.
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
    #@+node:ekr.20181111001813.1: *4* JS versions of LeoApp utils
    #@+node:ekr.20181111001833.1: *5* LeoMainWindow.ap_to_string
    def ap_to_string(self, ap):
        '''
        Convert an archived position (list of ints) to a string if necessary.
        '''
        if isinstance(ap, (list, tuple)):
            return '.'.join([str(z) for z in ap])
        assert isinstance(ap, str), repr(ap)
        return ap
    #@+node:ekr.20181110125347.1: *5* LeoMainWindow.format_node_tuple
    def format_node_tuple(self, node_tuple):
        assert isinstance(node_tuple, (list, tuple)), repr(node_tuple)
        ap, gnx, headline = node_tuple
        s = '.'.join([str(z) for z in ap])
        return 'p: %s %s %s' % (s.ljust(15), gnx.ljust(30), headline)
    #@-others
#@+node:ekr.20181104082154.1: *3* class LeoMiniBuffer
class LeoMiniBuffer(flx.Widget):

    def init(self): 
        with flx.HBox():
            flx.Label(text='Minibuffer')
            self.widget = flx.LineEdit(flex=1, placeholder_text='Enter command')
        self.widget.apply_style('background: yellow')
    
    @flx.action
    def set_text(self, s):
        self.widget.set_text(s)
#@+node:ekr.20181104082201.1: *3* class LeoStatusLine
class LeoStatusLine(flx.Widget):
    
    def init(self):
        with flx.HBox():
            flx.Label(text='Status Line')
            self.widget = flx.LineEdit(flex=1, placeholder_text='Status')
        self.widget.apply_style('background: green')

    @flx.action
    def set_text(self, s):
        self.widget.set_text(s)
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
        self.leo_items = {}
            # Keys are gnx's, values are LeoTreeItems.
        self.leo_populated_dict = {}
            # Keys are gnx's, values are True.
        self.leo_selected_gnx = outline[0][1]
            # The gnx of the selected tree item.
        with flx.TreeWidget(flex=1, max_selected=1) as self.tree:
            self.make_tree(outline)

    #@+others
    #@+node:ekr.20181111011928.1: *4* tree.populate_children
    def populate_children(self, children, parent_gnx):
        '''Populate parent with the children if necessary.'''
        if parent_gnx in self.leo_populated_dict:
            return
        self.leo_populated_dict [parent_gnx] = True
        assert parent_gnx in self.leo_items, (parent_gnx, repr(self.leo_items))
        with self.leo_items[parent_gnx]:
            for ap, gnx, headline in children:
                item = LeoTreeItem(gnx, ap, text=headline, checked=None, collapsed=True)
                self.leo_items [gnx] = item
    #@+node:ekr.20181110175222.1: *4* tree.receive_children
    @flx.action
    def receive_children(self, d):
        parent_ap, parent_gnx, parent_headline = d.get('parent')
        assert parent_gnx == d.get('gnx'), (repr(parent_gnx), repr(d.get('gnx')))
        children = d.get('children', [])
        self.populate_children(children, parent_gnx)
    #@+node:ekr.20181105045657.1: *4* tree.make_tree
    def make_tree(self, outline):
        '''Populate the outline from a list of tuples.'''
        for ap, gnx, h in outline:
            # ap is an archived position, a list of ints.
            if len(ap) == 1:
                item = LeoTreeItem(gnx, ap, text=h, checked=None, collapsed=True)
                self.leo_items [gnx] = item
    #@+node:ekr.20181104080854.3: *4* tree.on_tree_event
    # actions: set_checked, set_collapsed, set_parent, set_selected, set_text, set_visible
    @flx.reaction(
        'tree.children**.checked',
        'tree.children**.collapsed',
        'tree.children**.visible', # Never seems to fire.
    )
    def on_tree_event(self, *events):
        for ev in events:
            if 0: # Debugging only.
                self.show_event(ev)
    #@+node:ekr.20181109083659.1: *4* tree.on_selected_event
    @flx.reaction('tree.children**.selected')
    def on_selected_event(self, *events):
        '''
        Update the tree and body text when the user selects a new tree node.
        '''
        for ev in events:
            if ev.new_value:
                # We are selecting a node, not de-selecting it.
                gnx = ev.source.leo_gnx
                self.leo_selected_gnx = gnx
                    # Track the change.
                self.root.set_body(gnx)
                    # Set the body text directly.
                ap = ev.source.leo_position
                self.root.set_status_to_unl(ap, gnx)
                    # Set the status line directly.
                self.root.send_children_to_tree(gnx)
                    # Send the children back to us.
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
        # These will probably never need to be properties.
        self.leo_gnx = leo_gnx
        self.leo_position = leo_position
#@-others
if __name__ == '__main__':
    flx.launch(LeoApp)
    # A hack: suppress the "Automatically scrolling cursor into view" messages
    # Be careful to allow most important messages.
    if 1:
        pattern = re.compile(r'(Error|Leo|[Ss]ession|Starting|Stopping)')
        flx.set_log_level('INFO', pattern)
        flx.logger.info('LeoApp: after flx.launch')
    flx.run()
#@-leo
