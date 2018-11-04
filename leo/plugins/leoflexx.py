# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20181103094900.1: * @file leoflexx.py
#@@first
#@@language python
#@@tabwidth -4
'''
A Stand-alone prototype for Leo using flexx.

Flexx docs: testers, demos, howtos
https://flexx.readthedocs.io/en/stable/examples/
'''
import leo.core.leoGlobals as g
assert g
from flexx import flx
#@+others
#@+node:ekr.20181103151350.1: ** init
def init():
    # At present, leoflexx is not a true plugin.
    # I am executing leoflexx.py from an external script.
    return False
#@+node:ekr.20181104082130.1: ** class LeoMainWindow
class LeoMainWindow(flx.Widget):
    
    def init(self):
        with flx.VBox():
            with flx.HBox(flex=1):
                flx.Label(text='Tree')
                LeoTree(flex=1)
                flx.Label(text='Log')
                LeoLog(flex=1)
            flx.Label(text='Body')
            LeoBody(flex=1)
            flx.Label(text='Minibuffer')
            LeoMiniBuffer()
            flx.Label(text='Status Line')
            LeoStatusLine()
#@+node:ekr.20181104082138.1: ** class LeoTree
class LeoTree(flx.Widget):

    CSS = '''
    .flx-TreeWidget {
        background: #000;
        color: #afa;
    }
    '''
    
    #@+others
    #@+node:ekr.20181104080854.2: *3* tree.init
    def init(self):
        with flx.HSplit():
            ### self.label = flx.Label(flex=1, style='overflow-y: scroll;')
            with flx.TreeWidget(flex=1, max_selected=1) as self.tree:
                for t in ['foo', 'bar', 'spam', 'eggs']:
                    with flx.TreeItem(text=t, checked=None):
                        for i in range(4):
                            item2 = flx.TreeItem(text=t + ' %i' % i, checked=False)
                            if i == 2:
                                with item2:
                                    flx.TreeItem(title='A', text='more info on A')
                                    flx.TreeItem(title='B', text='more info on B')

        
    #@+node:ekr.20181104080854.3: *3* tree.on_event
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
#@+node:ekr.20181104082144.1: ** class LeoBody
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
#@+node:ekr.20181104082149.1: ** class LeoLog
### Kinda works
    # class LeoLog(flx.Label):
        # def init(self, flex=1, style='overflow-y: scroll;'):
            # pass

class LeoLog(flx.Widget):

    # CSS = """
    # .flx-CodeEditor > .ace {
        # width: 100%;
        # height: 100%;
    # }
    # """

    def init(self):
        global window
        # https://ace.c9.io/#nav=api
        self.ace = window.ace.edit(self.node, "editor")
        ### self.ace.setValue("import os\n\ndirs = os.walk")
        self.ace.navigateFileEnd()  # otherwise all lines highlighted
        self.ace.setTheme("ace/theme/solarized_dark")
        ### self.ace.getSession().setMode("ace/mode/python")

    @flx.reaction('size')
    def __on_size(self, *events):
        self.ace.resize()
#@+node:ekr.20181104082154.1: ** class LeoMiniBuffer
class LeoMiniBuffer(flx.LineEdit):
    pass
#@+node:ekr.20181104082201.1: ** class LeoStatusLine
class LeoStatusLine(flx.LineEdit):
    pass
#@-others
if __name__ == '__main__':
    # Use `--flexx-webruntime=browser` to run in browser.
    flx.launch(LeoMainWindow)
    flx.run()
    ###
        # # Runs in browser.
        # # `python -m flexx stop 49190` stops the server.
        # flx.App(LeoWapp).launch('firefox-browser')
        # flx.start()
#@-leo
