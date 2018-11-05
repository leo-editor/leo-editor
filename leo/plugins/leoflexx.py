# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20181103094900.1: * @file leoflexx.py
#@@first
#@@language python
#@@tabwidth -4
'''
A Stand-alone prototype for Leo using flexx.
'''
from flexx import flx
import leo.core.leoGlobals as g
assert g
#@+others
#@+node:ekr.20181104134654.1: ** class G
# class G (flx.PyComponent):

    # def trace(*args, **kwargs):
        # print('g.trace', ', '.join(args))
    
# g = G()
#@+node:ekr.20181104082144.1: ** class LeoBody
base_url = 'https://cdnjs.cloudflare.com/ajax/libs/ace/1.2.6/'
flx.assets.associate_asset(__name__, base_url + 'ace.js')
flx.assets.associate_asset(__name__, base_url + 'mode-python.js')
flx.assets.associate_asset(__name__, base_url + 'theme-solarized_dark.js')

class LeoBody(flx.PyComponent):
    
    """ A CodeEditor widget based on Ace.
    """

    CSS = """
    .flx-CodeEditor > .ace {
        width: 100%;
        height: 100%;
    }
    """
    
    if 1:

        def init(self):
            with flx.HBox():
                flx.Label(text='Body')
    else:
        def init(self):

            global window
            # https://ace.c9.io/#nav=api
            self.ace = window.ace.edit(self.node, "editor")
            self.ace.setValue("import os\n\ndirs = os.walk")
            self.ace.navigateFileEnd()  # otherwise all lines highlighted
            self.ace.setTheme("ace/theme/solarized_dark")
            self.ace.getSession().setMode("ace/mode/python")

        @flx.reaction('size')
        def __on_size(self, *events):
            self.ace.resize()
#@+node:ekr.20181104174357.1: ** class LeoGui (can't instantiate)
class LeoGui (flx.PyComponent):
    
    def runMainLoop(self):
        '''The main loop for the flexx gui.'''

        # print('LeoFlex running...')
        # c = g.app.log.c
        # assert g.app.gui.guiName() == 'browser'
        # if 0: # Run all unit tests.
            # g.app.failFast = True
            # path = g.os_path_finalize_join(
                # g.app.loadDir, '..', 'test', 'unittest.leo')
            # c = g.openWithFileName(path, gui=self)
            # c.findCommands.ftm = g.NullObject()
                # # A hack. Some other class should do this.
                # # This looks like a bug.
            # c.debugCommands.runAllUnitTestsLocally()
                # # This calls sys.exit(0)
        # print('calling sys.exit(0)')
        # sys.exit(0)
        
#@+node:ekr.20181104082149.1: ** class LeoLog
### Kinda works
    # class LeoLog(flx.Label):
        # def init(self, flex=1, style='overflow-y: scroll;'):
            # pass

class LeoLog(flx.PyComponent):

    CSS = """
    .flx-CodeEditor > .ace {
        width: 100%;
        height: 100%;
    }
    """
    
    if 1:
        def init(self):
            flx.Widget(flex=1).apply_style('background: red')
    else:
        def init(self):
            global window
            # https://ace.c9.io/#nav=api
            self.ace = window.ace.edit(self.node, "editor")
            ### self.ace.setValue("import os\n\ndirs = os.walk")
            self.ace.navigateFileEnd()  # otherwise all lines highlighted
            self.ace.setTheme("ace/theme/solarized_dark")
            ### self.ace.getSession().setMode("ace/mode/python")
            print('window', window)

        @flx.reaction('size')
        def __on_size(self, *events):
            self.ace.resize()
#@+node:ekr.20181104082130.1: ** class LeoMainWindow
class LeoMainWindow(flx.PyComponent): # flx.Widget):
    
    def init(self):
        with flx.VBox():
            with flx.HBox(flex=1):
                LeoTree()
                LeoLog()
            LeoBody()
            LeoMiniBuffer()
            LeoStatusLine()
        # print('tree', self.tree)
        # print('log', self.log)
#@+node:ekr.20181104082154.1: ** class LeoMiniBuffer
class LeoMiniBuffer(flx.PyComponent):
    
    def init(self): 
        with flx.HBox():
            flx.Label(text='Minibuffer')
            self.widget = flx.LineEdit(
                flex=1, placeholder_text='Enter command')
        self.widget.apply_style('background: yellow')

#@+node:ekr.20181104082201.1: ** class LeoStatusLine
class LeoStatusLine(flx.PyComponent):
    
    def init(self):
        with flx.HBox():
            flx.Label(text='Status Line')
            self.widget = flx.LineEdit(flex=1, placeholder_text='Status')
        self.widget.apply_style('background: green')

#@+node:ekr.20181104082138.1: ** class LeoTree
class LeoTree(flx.PyComponent):

    CSS = '''
    .flx-TreeWidget {
        background: #000;
        color: #afa;
    }
    '''
    def init(self):
        with flx.TreeWidget(flex=1, max_selected=1) as self.tree:
            self.make()

    #@+others
    #@+node:ekr.20181105045657.1: *3* tree.make
    def make(self):
        for t in ['foo', 'bar', 'spam', 'eggs']:
            with flx.TreeItem(text=t, checked=None):
                for i in range(4):
                    item2 = flx.TreeItem(text=t + ' %i' % i, checked=False)
                    if i == 2:
                        with item2:
                            flx.TreeItem(title='A', text='more info on A')
                            flx.TreeItem(title='B', text='more info on B')
    #@+node:ekr.20181104080854.3: *3* tree.on_event
    if 0:
        @flx.reaction(
            'tree.children**.checked',
            'tree.children**.selected',
            'tree.children**.collapsed',
        )
        def on_event(self, *events):
            for ev in events:
                # print(ev.source, ev.type)
                id_ = ev.source.title or ev.source.text
                kind = '' if ev.new_value else 'un-'
                text = '%10s: %s' % (id_, kind + ev.type)
                assert text
                ### self.label.set_html(text + '<br />' + self.label.html)
    #@-others
#@+node:ekr.20181103151350.1: ** init
def init():
    # At present, leoflexx is not a true plugin.
    # I am executing leoflexx.py from an external script.
    return False
#@-others
if __name__ == '__main__':
    flx.launch(LeoMainWindow, runtime='firefox-browser')
    flx.run()
        # # Runs in browser.
        # # `python -m flexx stop 49190` stops the server.
        # flx.App(LeoWapp).launch('firefox-browser')
        # flx.start()

    ### RuntimeError: Cannot instantiate a PyComponent from JS.
    ### g.app.gui = LeoGui()
#@-leo
