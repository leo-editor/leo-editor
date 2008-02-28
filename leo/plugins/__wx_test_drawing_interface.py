#@+leo-ver=4-thin
#@+node:bob.20070910154126.1:@thin __wx_test_drawing_interface.py
#@<< docstring >>
#@+node:bob.20070909152633.1:<< docstring >>
'''This is a test plugin to show how to use the prototype
     tree drawing interface for __wx__alt_gui.

It is only for developers and testers, not for general use.

Hopefully this will expand to include full documentation and
a tutorial. Please remember it is a prototype and can be easily
changed .

This is a low level interface, we can write a higher level interface
when it becomes clear exactly what people want to do.


When I want to draw the canvas I will call tree.drawCanvasHook with
an OutlineCanvas instance 'canvas' as data.

In the canvas you will find the following:
       ------
_buffer:  A wx.MemoryDc that will be used for drawing.

          You should start your code with:  dc = canvas._buffer


_positions: a python list of (enhanced) leo positions indicating the nodes
            to be drawn.


_lineHeight: The height of each node.

_size: A wx.Size - the size of the canvas you have to draw on.



Each position in positions will come pre_loaded with information as to how
     --------
I intend to draw the tree unless you say different.


_depth: The depth of nesting of this node relative to the root node for this hoist.


_virtualTop: The vertical position ths node would have on an imaginary canvas
             on which all the nodes above it were drawn.


_top: The position of the top of the node on our real canvas.
        This may be negative for the first node, indicating it is only partly visible.

_textBoxRect: A wx.Rect - where the text will be placed on the canvas
_iconBoxRect: A wx.Rect - where the icon box will be placed.
_clickBoxRect: A wx.Rect - same for the click box

                You can move these areas around eg, move the text area to
                the right to make room for icons.


_clickBoxCenter: A wx.Point - the point where the center of the clickbox would be
                 drawn if the node had one.  The vertical component always indicates
                 the center of the line.


_icon: The image that I intend drawing for the icon.
_clickBoxIcon: The image I intend drawing for the click box, or None if no click box.


_clickRegions: A python list (initially empty) to which you must add tupples
               indicating any hotspots for which you wish to recieve mouse events. 

                Each item in the list  must be a tuple of the form
                    ('AreaName', wx.Rect)

                The rect must be the size and position of the hot spot (an image
                maybe) relative to the top left of the canvas, which is (0, 0).

                The same name can be used for many areas. The first item in the list
                that contains the position of the event will recieve the event. So
                order is important.

                When I recieve a mouse event in these regions I will call a method
                on tree such as onMouseAreaNameLeftDown.  These reciever methods
                need not exist or all the methods may be set to the same function.

                Your method prototypes should look like

                    def onMouseAreaNameLeftDown(sp, event, area, action):

                where sp is the leo position hit, area is the AreaName you supplied,
                and action is 'LeftUp', 'LeftDown', 'RightUp', 'RightDown'
                'RightDoubleClick', 'LeftDoubleClick' etc. Event is the raw system
                event.

'''
#@-node:bob.20070909152633.1:<< docstring >>
#@nl

__version__ = '0.1'
#@<< version history >>
#@+node:bob.20070909152633.2:<< version history >>
#@@killcolor
#@+at
# 
# 0.1 plumloco: Initial Version
#@-at
#@nonl
#@-node:bob.20070909152633.2:<< version history >>
#@nl

#@<< imports >>
#@+node:bob.20070909152932:<< imports >>
import leoGlobals as g
import leoPlugins

import os
import string
import sys
import traceback

try:
    import wx
    import wx.lib
    import wx.lib.colourdb
except ImportError:
    wx = None
    g.es_print('can not import wxWidgets')

#print '1=================================================== ***************'
#@nonl
#@-node:bob.20070909152932:<< imports >>
#@nl

#@+others
#@+node:bob.20070909152910: init
def init():

    ok = True

    if not wx:
        return False

    if g.unitTesting:
        return False

    if not g.app.gui.guiName() == 'wxPython':
        return False

    if ok:
        leoPlugins.registerHandler('start2',onStart2)

        g.plugin_signon(__name__)

    print '2=================================================== ***************'
    return ok
#@-node:bob.20070909152910: init
#@+node:bob.20070909152633.5:onStart2
def onStart2 (tag, keywords):

    """
    Showing how to define a global hook that affects all commanders.
    """
    print '[[[[[ onStart2 ]]]]'
    import __wx_alt_gui as wxLeo    

    g.funcToMethod(drawTreeHook, wxLeo.wxLeoTree)
    g.funcToMethod(onMouseMyIconLeftDown, wxLeo.wxLeoTree)
    print '3=================================================== ***************'
#@nonl
#@-node:bob.20070909152633.5:onStart2
#@+node:bob.20070909163209:drawTreeHook
def drawTreeHook(self, canvas):

    dc = canvas._buffer

    for sp in canvas._positions:

        if sp.headString().startswith('@thin'):
            #@            << add another icon between icon and text >>
            #@+node:bob.20070909174306:<< add another icon between icon and text >>

            # we need to move the text to the right to make room for 
            #  our icon which is 24 pixels wide and allow 6 pixels padding.

            textRect = sp._textBoxRect

            # find the x position of the text box and save it
            x = textRect.x

            # move the text box 30 pixels to the right
            textRect.Offset(( 30, 0))

            # find the mid point of the line
            midpoint = sp._top + canvas._lineHeight//2

            # find where the top of the icon needs to be to put
            #  its center it on the line

            y = midpoint - 12

            # render the bitmap
            dc.DrawBitmap(canvas._icons[17], x, y, True )





            #@-node:bob.20070909174306:<< add another icon between icon and text >>
            #@nl

            # add the area of the icon to the list
            sp._clickRegions.append(('MyIcon', wx.Rect(x, y, 24, 24))) 

        # ask the canvas to render the rest of the tree
        #canvas.renderAll()

    # If you return False the canvas will finish drawing the
    # tree for you. If you return True it will assume that you
    # have drawn the whole tree and do nothing except blit
    # the canvas you have drawn onto the screen.


    #let the canvas finish the rendering.
    return False
#@-node:bob.20070909163209:drawTreeHook
#@+node:bob.20070909163711:onMouseMyIconLeftDown
def onMouseMyIconLeftDown(self, sp, event, area, type):
    g.trace('\n\tarea:', area, '\n\ttype:', type, '\n\t', '\n\tPosition:', sp)
#@-node:bob.20070909163711:onMouseMyIconLeftDown
#@-others
#@nonl
#@-node:bob.20070910154126.1:@thin __wx_test_drawing_interface.py
#@-leo
