# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.201811100000000.1: * @file leoflexx_js.py
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
#@+node:ekr.20181110170337.1: **  init
def init():
    # At present, leoflexx is not a true plugin.
    # I am executing leoflexx.py from an external script.
    return False
#@+node:ekr.20181104134654.1: ** class G
# class G (flx.PyComponent):

    # def trace(*args, **kwargs):
        # print('g.trace', ', '.join(args))
    
# g = G()
#@+node:ekr.20181110170220.1: ** class LeoBody
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

    def init(self):
        # pylint: disable=undefined-variable
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
        
#@+node:ekr.20181110170235.1: ** class LeoLog
class LeoLog(flx.Widget):

    CSS = """
    .flx-CodeEditor > .ace {
        width: 100%;
        height: 100%;
    }
    """

    def init(self):
        # pylint: disable=undefined-variable
        global window
        # https://ace.c9.io/#nav=api
        self.ace = window.ace.edit(self.node, "editor")
            # self.ace.setValue("import os\n\ndirs = os.walk")
        self.ace.navigateFileEnd()  # otherwise all lines highlighted
        self.ace.setTheme("ace/theme/solarized_dark")
            # self.ace.getSession().setMode("ace/mode/python")
        print('window', window)

    @flx.reaction('size')
    def __on_size(self, *events):
        self.ace.resize()
#@+node:ekr.20181110170304.1: ** class LeoMainWindow
class LeoMainWindow(flx.Widget):
    
    def init(self):
        with flx.VBox():
            with flx.HBox(flex=1):
                flx.Label(text='Tree')
                self.tree = LeoTree(flex=1)
                flx.Label(text='Log')
                self.log = LeoLog(flex=1)
            flx.Label(text='Body')
            LeoBody(flex=1)
            flx.Label(text='Minibuffer')
            LeoMiniBuffer()
            flx.Label(text='Status Line')
            LeoStatusLine()
        # print('tree', self.tree)
        # print('log', self.log)
#@+node:ekr.20181110170402.1: ** class LeoMiniBuffer
class LeoMiniBuffer(flx.LineEdit):
    pass
#@+node:ekr.20181110170409.1: ** class LeoStatusLine
class LeoStatusLine(flx.LineEdit):
    pass
#@+node:ekr.20181110170328.1: ** class LeoTree
class LeoTree(flx.Widget):

    CSS = '''
    .flx-TreeWidget {
        background: #000;
        color: #afa;
    }
    '''
    
    #@+others
    #@+node:ekr.20181110170328.2: *3* tree.init
    def init(self):
        with flx.HSplit():
            with flx.TreeWidget(flex=1, max_selected=1) as self.tree:
                for t in ['foo', 'bar', 'spam', 'eggs']:
                    with flx.TreeItem(text=t, checked=None):
                        for i in range(4):
                            item2 = flx.TreeItem(text=t + ' %i' % i, checked=False)
                            if i == 2:
                                with item2:
                                    flx.TreeItem(title='A', text='more info on A')
                                    flx.TreeItem(title='B', text='more info on B')

        
    #@+node:ekr.20181110170328.3: *3* tree.on_event
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
            # self.label.set_html(text + '<br />' + self.label.html)
    #@-others
#@-others
if __name__ == '__main__':
    flx.launch(LeoMainWindow)
    flx.run()
        # # Runs in browser.
        # # `python -m flexx stop 49190` stops the server.
        # flx.App(LeoWapp).launch('firefox-browser')
        # flx.start()
#@-leo
