# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20181103094900.1: * @file leoflexx.py
#@@first
'''A Stand-alone prototype of flexx.'''
#@@language python
#@@tabwidth -4
from flexx import flx
#@+others
#@+node:ekr.20181103151350.1: ** init
def init():
    # At present, leoflexx is not a true plugin.
    # I am executing leoflexx.py from an external script.
    return False
#@+node:ekr.20181103102131.1: ** class TreeExample
"""
An example with a tree widget, demonstrating e.g. theming, checkable items,
sub items.
"""
# https://flexx.readthedocs.io/en/stable/examples/tree_src.html#tree-py

class TreeExample(flx.Widget):

    CSS = '''
    .flx-TreeWidget {
        background: #000;
        color: #afa;
    }
    '''
    
    #@+others
    #@+node:ekr.20181103102306.1: *3* te.init
    def init(self):
        with flx.HSplit():
            self.label = flx.Label(flex=1, style='overflow-y: scroll;')
            with flx.TreeWidget(flex=1, max_selected=1) as self.tree:
                for t in ['foo', 'bar', 'spam', 'eggs']:
                    with flx.TreeItem(text=t, checked=None):
                        for i in range(4):
                            item2 = flx.TreeItem(text=t + ' %i' % i, checked=False)
                            if i == 2:
                                with item2:
                                    flx.TreeItem(title='A', text='more info on A')
                                    flx.TreeItem(title='B', text='more info on B')

        
    #@+node:ekr.20181103102309.1: *3* te.on_event
    @flx.reaction(
        'tree.children**.checked',
        'tree.children**.selected',
        'tree.children**.collapsed',
    )
    def on_event(self, *events):
        for ev in events:
            id = ev.source.title or ev.source.text
            kind = '' if ev.new_value else 'un-'
            text = '%10s: %s' % (id, kind + ev.type)
            print(repr(text))
            self.label.set_html(text + '<br />' + self.label.html)
    #@-others
#@+node:ekr.20181103095416.1: ** class Drawing
# https://flexx.readthedocs.io/en/stable/examples/drawing_src.html#drawing-py

class Drawing(flx.CanvasWidget):
    
    CSS = """
    .flx-Drawing {background: #fff; border: 5px solid #000;}
    """

    def init(self):
        super().init()
        self.ctx = self.node.getContext('2d')
        self._last_pos = {}
        self.set_capture_mouse(1)
        self.label = flx.Label()

    #@+others
    #@+node:ekr.20181103095629.1: *3* show_event
    def show_event(self, ev):
        if -1 in ev.touches:  # Mouse
            t = 'mouse pos: {:.0f} {:.0f}  buttons: {}'
            self.label.set_text(t.format(ev.pos[0], ev.pos[1], ev.buttons))
        else:  # Touch
            self.label.set_text('Touch ids: {}'.format(ev.touches.keys()))
    #@+node:ekr.20181103095629.2: *3* @flx.reaction('pointer_move')
    @flx.reaction('pointer_move')
    def on_move(self, *events):
        for ev in events:
            self.show_event(ev)
            # Effective way to only draw if mouse is down, but disabled for
            # sake of example. Not necessary if capture_mouse == 1.
            # if 1 not in ev.buttons:
            #     return

            # One can simply use ev.pos, but let's support multi-touch here!
            # Mouse events also have touches, with a touch_id of -1.
            for touch_id in ev.touches:
                x, y, force = ev.touches[touch_id]
                self.ctx.beginPath()
                self.ctx.strokeStyle = '#080'
                self.ctx.lineWidth = 3
                self.ctx.lineCap = 'round'
                self.ctx.moveTo(*self._last_pos[touch_id])
                self.ctx.lineTo(x, y)
                self.ctx.stroke()
                self._last_pos[touch_id] = x, y

    #@+node:ekr.20181103095630.1: *3* @flx.reaction('pointer_down')
    @flx.reaction('pointer_down')
    def on_down(self, *events):
        for ev in events:
            self.show_event(ev)
            for touch_id in ev.touches:
                x, y, force = ev.touches[touch_id]
                self.ctx.beginPath()
                self.ctx.fillStyle = '#f00'
                self.ctx.arc(x, y, 3, 0, 6.2831)
                self.ctx.fill()
                self._last_pos[touch_id] = x, y
    #@+node:ekr.20181103095656.1: *3* @flx.reaction('pointer_up')
    @flx.reaction('pointer_up')
    def on_up(self, *events):
        for ev in events:
            self.show_event(ev)
            for touch_id in ev.touches:
                x, y, force = ev.touches[touch_id]
                self.ctx.beginPath()
                self.ctx.fillStyle = '#00f'
                self.ctx.arc(x, y, 3, 0, 6.2831)
                self.ctx.fill()
    #@-others
#@+node:ekr.20181103095521.1: ** class Main
class Main(flx.Widget):
    """ Embed in larger widget to test offset.
    """

    CSS = """
    .flx-Main {background: #eee;}
    """

    def init(self):
        with flx.VFix():
            flx.Widget(flex=1)
            with flx.HFix(flex=2):
                flx.Widget(flex=1)
                Drawing(flex=2)
                flx.Widget(flex=1)
            flx.Widget(flex=1)
#@-others
if __name__ == '__main__':
    if 1: # tree
        # Server exits when browser closes.
        flx.launch(TreeExample)
        flx.run()
    else: # drawing
        # Server never exits.
        flx.App(Main).launch('firefox-browser')
        flx.start()
#@-leo
