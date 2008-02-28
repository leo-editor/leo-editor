#!/usr/bin/python
#@+leo-ver=4-thin
#@+node:bob.20080111200056:@thin gtkOutlineDemo.py
#@@first
import sys, os



import pygtk
pygtk.require('2.0')
import gtk

import pango
import cairo

#@+others
#@+node:bob.20080111194559:GtkLeoTreeDemo
#@@first


class GtkLeoTreeDemo(object):


    #@    @+others
    #@+node:bob.20080113184034:__init__
    def __init__(self):

        #for n in c.allNodes_iter():
        #    print n.headString()


        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.set_title("gtkLeo Outline Widget Demo")
        window.connect("destroy", lambda w: gtk.main_quit())
        window.set_size_request(10, 10)
        window.resize(400, 300)

        loadIcons()

        self.panel = OutlineCanvasPanel(window, c, 'canvas')

        self.canvas = canvas = self.panel._canvas
        g.trace(canvas)

        canvas.set_events(gtk.gdk.ALL_EVENTS_MASK)
        canvas.connect('button_press_event', self.onButtonPress)
        #canvas.connect('button_release_event', self.onButtonPress)

        window.show_all()



    #@-node:bob.20080113184034:__init__
    #@+node:bob.20080113183321:onButtonPress
    def onButtonPress(self, w, event, *args):

        codes = {
            gtk.gdk.BUTTON_PRESS: 'click',
            gtk.gdk._2BUTTON_PRESS: 'double_click',
            gtk.gdk._3BUTTON_PRESS: 'triple_click',
            gtk.gdk.BUTTON_RELEASE: 'release'
        }


        sp, item = self.canvas.hitTest(event.x, event.y)
        print codes[event.type], '%s[%s]: %s'%(
            g.choose(isinstance(item, int), 'headStringIcon[%s]'%item, item),
            'button-%s'%event.button,
            sp.headString()
        )

        if item == 'ClickBox' and event.button == 1:
            if sp.isExpanded():
                sp.contract()
            else:
                sp.expand()

            self.canvas.update()
    #@-node:bob.20080113183321:onButtonPress
    #@+node:bob.20080113183321.1:onButtonRelease
    #@-node:bob.20080113183321.1:onButtonRelease
    #@-others
#@nonl
#@-node:bob.20080111194559:GtkLeoTreeDemo
#@+node:bob.20080113170657:loadIcon
def loadIcon(fname):

    try:
        icon = gtk.gdk.pixbuf_new_from_file(fname)
    except:
        icon = None

    if icon and icon.get_width()>0:
        return icon

    print 'Can not load icon from', fname
#@-node:bob.20080113170657:loadIcon
#@+node:bob.20080113133525:loadIcons
def loadIcons():

    global icons, plusBoxIcon, minusBoxIcon, appIcon, namedIcons, globalImages

    import cStringIO



    icons = []
    namedIcons = {}


    path = g.os_path_abspath(g.os_path_join(g.app.loadDir, '..', 'Icons'))
    if g.os_path_exists(g.os_path_join(path, 'box01.GIF')):
        ext = '.GIF'
    else:
        ext = '.gif'

    for i in range(16):
        icon = loadIcon(g.os_path_join(path, 'box%02d'%i + ext))
        icons.append(icon)



    for name in (
        'lt_arrow_enabled',
        'rt_arrow_enabled',
        'lt_arrow_disabled',
        'rt_arrow_disabled',
        'plusnode',
        'minusnode'
    ):
        icon = loadIcon(g.os_path_join(path, name + '.gif'))
        if icon:
            namedIcons[name] = icon

    plusBoxIcon = namedIcons['plusnode']
    minusBoxIcon = namedIcons['minusnode']

    globalImages = {}

#@-node:bob.20080113133525:loadIcons
#@+node:bob.20080113141134:name2Color


def name2color(name, default=None, cairo=False):




    if isinstance(name, cls ):
        return name

    color = colors.getColorRGB(name)

    if color is None:
        if default:
            return name2color(default)
        else:
            return None

    r, g, b = color

    #trace(print r, g, b)

    if cairo:
        return r/255.0, g/255.0, b/255.0 


    return gtk.gdk.Color(r,g,b)
#@-node:bob.20080113141134:name2Color
#@+node:bob.20080113170041:getImage
def getImage (relPath, force=False):


    if not force and relPath in globalImages:
        image = globalImages[relPath]
        g.es('cach ', image, image.get_height(), getColor('magenta'))
        return image, image.get_height()

    try:
        path = g.os_path_normpath(g.os_path_join(g.app.loadDir,"..","Icons", relPath))
        globalImages[relPath] = image = loadIcon(path)
        return image

    except Exception:
        pass

    try:
        path = g.os_path_normpath(relPath)
        localImages[relPath] =  image = loadIcon(path)
        return image
    except Exception:
        pass

    return None
#@-node:bob.20080113170041:getImage
#@+node:bob.20080114060133:getHeadlineFont
#@-node:bob.20080114060133:getHeadlineFont
#@+node:bob.20080111201957.77:class OutlineCanvasPanel

class OutlineCanvasPanel(object):
    """A class to mimic a scrolled window to contain an OutlineCanvas."""

    #@    @+others
    #@+node:bob.20080111201957.78:__init__

    def __init__(self, parent, leoTree, name):
        """Create an OutlineCanvasPanel instance."""

        #g.trace('OutlineCanvasPanel')

        #self._leoTree = leoTree
        #self.c = leoTree.c
        self.c = c

        self._x = 0
        self._y = 0

        self._canvas = canvas = OutlineCanvas(self)
        #canvas.resize(400, 300)

        self._table = gtk.Table(2,2)

        self._hscrollbar = gtk.HScrollbar()
        self._vscrollbar = gtk.VScrollbar()

        self._hadj = h = self._hscrollbar.get_adjustment()
        self._vadj = v = self._vscrollbar.get_adjustment()

        self._hscrollbar.set_range(0, 10)
        self._vscrollbar.set_range(0, 20)


        v.connect('value-changed', self.onScrollVertical)
        h.connect('value-changed', self.onScrollHorizontal)

        self._table.attach(self._hscrollbar, 0, 1, 1, 2, yoptions=0)
        self._table.attach(self._vscrollbar, 1, 2, 0, 1, xoptions=0)


        options = gtk.SHRINK | gtk.FILL | gtk.EXPAND
        self._table.attach(self._canvas, 0, 1, 0, 1, options, options)

        parent.add(self._table)

        self._canvas.set_events(
            gtk.gdk.POINTER_MOTION_MASK |
                    gtk.gdk.POINTER_MOTION_HINT_MASK
        )


        #self._entry = wx.TextCtrl(self._canvas,
        #    style = wx.SIMPLE_BORDER | wx.WANTS_CHARS
        #)

        #self._entry._virtualTop = -1000
        #self._entry.Hide()
        #self._canvas._widgets.append(self._entry)

        #self._canvas.update()


        # self.Bind(wx.EVT_SIZE, self.onSize)


        #self.SetBackgroundColour(self._leoTree.outline_pane_background_color)

        #self.Bind(wx.EVT_CHAR,
        #    lambda event, self=self._leoTree: onGlobalChar(self, event)
        #)

        #self.onScroll(wx.HORIZONTAL, 0)

    #@-node:bob.20080111201957.78:__init__
    #@+node:bob.20080111201957.79:showEntry
    showcount = 0
    def showEntry(self):

        # self.showcount +=1

        # print
        # g.trace(self.showcount, g.callers(20))
        # print

        entry = self._entry
        canvas = self._canvas

        ep = self._leoTree.editPosition()

        if not ep:
            return self.hideEntry()


        for sp in canvas._positions:
            if ep == sp:
                break
        else:
            return self.hideEntry()

        x, y, width, height = sp._textBoxRect
        #print '\t', x, y, width , height

        entry._virtualTop = canvas._virtualTop + y -2

        entry.MoveXY(x - 2, y -2)
        entry.SetSize((max(width + 4, 100), -1))

        tw = self._leoTree.headlineTextWidget

        range = tw.getSelectionRange()
        tw.setInsertPoint(0)
        #tw.setInsertPoint(len(sp.headString()))
        tw.setSelectionRange(*range)
        entry.Show()
    #@-node:bob.20080111201957.79:showEntry
    #@+node:bob.20080111201957.80:hideEntry

    def hideEntry(self):

        entry = self._entry
        entry._virtualTop = -1000
        entry.MoveXY(0, -1000)

        entry.Hide()
    #@-node:bob.20080111201957.80:hideEntry
    #@+node:bob.20080111201957.81:getPositions

    def getPositions(self):
        return self._canvas._positions
    #@nonl
    #@-node:bob.20080111201957.81:getPositions
    #@+node:bob.20080111201957.87:onScrollVertical
    def onScrollVertical(self, adjustment):
        """Scroll the outline vertically to a new position."""

        self._canvas.vscrollTo(int(adjustment.value))
    #@nonl
    #@-node:bob.20080111201957.87:onScrollVertical
    #@+node:bob.20080113090336:onScrollHorizontal
    def onScrollHorizontal(self, adjustment):
        """Scroll the outline horizontally to a new position.

        """
        self._canvas.hscrollTo(int(adjustment.value))
    #@-node:bob.20080113090336:onScrollHorizontal
    #@+node:bob.20080111201957.88:onScrollRelative

    def onScrollRelative(self, orient, value):

        return self.onScroll(orient, self.GetScrollPos(orient) + value)
    #@-node:bob.20080111201957.88:onScrollRelative
    #@+node:bob.20080111201957.90:vscrollUpdate

    def vscrollUpdate(self):
        """Set the vertical scroll bar to match current conditions."""

        canvas = self._canvas

        oldtop = top = canvas._virtualTop
        canvasHeight = canvas.get_allocation().height
        treeHeight = canvas._treeHeight

        if (treeHeight - top) < canvasHeight:
            top = treeHeight - canvasHeight

        if top < 0 :
            top = 0

        if oldtop != top:
            canvas._virtualTop = top
            canvas.redraw()
            top = canvas._virtualTop

        #self.showEntry()

        self._vadj.set_all(
            top, #value
            0, #lower
            treeHeight, #upper
            canvasHeight * 0.1, #step_increment
            canvasHeight * 0.9, #page_increment
            canvasHeight #page-size
        )


    #@-node:bob.20080111201957.90:vscrollUpdate
    #@+node:bob.20080111201957.91:hscrollUpdate

    def hscrollUpdate(self):
        """Set the vertical scroll bar to match current conditions."""

        canvas = self._canvas

        oldleft = left = canvas._virtualLeft
        canvasWidth = canvas.get_allocation().width
        treeWidth = canvas._treeWidth

        if (treeWidth - left) < canvasWidth:
            left = treeWidth - canvasWidth

        if left < 0 :
            left = 0

        if oldleft != left:
            canvas._virtualLeft = left
            canvas.redraw()
            left = canvas._virtualLeft

        #self.showEntry()

        self._hadj.set_all(
            left, #value
            0, #lower
            treeWidth, #upper
            canvasWidth * 0.1, #step_increment
            canvasWidth * 0.9, #page_increment
            canvasWidth #page-size
        )

    #@-node:bob.20080111201957.91:hscrollUpdate
    #@+node:bob.20080111201957.92:update

    def update(self):
        self._canvas.update()


    #@-node:bob.20080111201957.92:update
    #@+node:bob.20080111201957.93:redraw

    def redraw(self):
        self._canvas.redraw()
    #@nonl
    #@-node:bob.20080111201957.93:redraw
    #@+node:bob.20080111201957.94:refresh
    def refresh(self):
        self._canvas.refresh()
    #@nonl
    #@-node:bob.20080111201957.94:refresh
    #@+node:bob.20080111201957.95:GetName
    def GetName(self):
        return 'canvas'

    getName = GetName
    #@nonl
    #@-node:bob.20080111201957.95:GetName
    #@-others
#@-node:bob.20080111201957.77:class OutlineCanvasPanel
#@+node:bob.20080111201957.96:class OutlineCanvas
class OutlineCanvas(gtk.DrawingArea):
    """Implements a virtual view of a leo outline tree.

    The class uses an off-screen buffer for drawing which it
    blits to the window during paint calls for expose events, etc,

    A redraw is only required when the size of the canvas changes,
    a scroll event occurs, or if the outline changes.

    """
    #@    @+others
    #@+node:bob.20080111201957.97:__init__
    def __init__(self, parent):
        """Create an OutlineCanvas instance."""

        #g.trace('OutlineCanvas')

        self.c = c = parent.c

        self._parent = parent
        #self.leoTree = parent.leoTree


        #@    << define ivars >>
        #@+node:bob.20080111201957.98:<< define ivars >>
        #self._icons = icons

        self._widgets = []

        self.drag_p = None

        self._size =  [1000, 1000]

        self._virtualTop = 0
        self._virtualLeft = 0

        self._textIndent = 30

        self._xPad = 30
        self._yPad = 2

        self._treeHeight = 500
        self._treeWidth = 500

        self._positions = []

        self._fontHeight = None
        self._iconSize = [20, 11]

        self._clickBoxSize = None
        self._lineHeight =  10
        self._requestedLineHeight = 10

        self._yTextOffset = None
        self._yIconOffset = None

        self._clickBoxCenterOffset = None

        self._clickBoxOffset = None


        #@-node:bob.20080111201957.98:<< define ivars >>
        #@nl

        gtk.DrawingArea.__init__(self)
        self._pangoLayout = self.create_pango_layout("Wq")


        # g.trace()


        self._font = pango.FontDescription(outlineFont)

        self._pangoLayout.set_font_description(self._font)


        self._buffer = None

        self.contextChanged()

        #self.Bind(wx.EVT_PAINT, self.onPaint)

        self.connect('map-event', self.onMap)


        #for o in (self, parent):
        #    
        #@nonl
        #@<< create  bindings >>
        #@+node:bob.20080111201957.99:<< create bindings >>
        # onmouse = self._leoTree.onMouse

        # for e, s in (
           # ( wx.EVT_LEFT_DOWN,     'LeftDown'),
           # ( wx.EVT_LEFT_UP,       'LeftUp'),
           # ( wx.EVT_LEFT_DCLICK,   'LeftDoubleClick'),
           # ( wx.EVT_MIDDLE_DOWN,   'MiddleDown'),
           # ( wx.EVT_MIDDLE_UP,     'MiddleUp'),
           # ( wx.EVT_MIDDLE_DCLICK, 'MiddleDoubleClick'),
           # ( wx.EVT_RIGHT_DOWN,    'RightDown'),
           # ( wx.EVT_RIGHT_UP,      'RightUp'),
           # ( wx.EVT_RIGHT_DCLICK,  'RightDoubleClick'),
           # ( wx.EVT_MOTION,        'Motion')
        # ):
            # o.Bind(e, lambda event, type=s: onmouse(event, type))



        # #self.Bind(wx.EVT_KEY_UP, self._leoTree.onChar)
        # #self.Bind(wx.EVT_KEY_DOWN, lambda event: self._leoTree.onKeyDown(event))

        # self.Bind(wx.EVT_CHAR,
            # lambda event, self=self._leoTree: onGlobalChar(self, event)
        # )

        #@-node:bob.20080111201957.99:<< create bindings >>
        #@nl

    #@+at
    # self.box_padding = 5 # extra padding between box and icon
    # self.box_width = 9 + self.box_padding
    # self.icon_width = 20
    # self.text_indent = 4 # extra padding between icon and tex
    # 
    # self.hline_y = 7 # Vertical offset of horizontal line
    # self.root_left = 7 + self.box_width
    # self.root_top = 2
    # 
    # self.default_line_height = 17 + 2 # default if can't set line_height 
    # from font.
    # self.line_height = self.default_line_height
    # 
    #@-at
    #@-node:bob.20080111201957.97:__init__
    #@+node:bob.20080111201957.101:hitTest
    def hitTest(self, x, y):
        result = self._hitTest(point)
        g.trace(result)
        return result

    def hitTest(self, xx, yy):

        for sp in self._positions:

            if yy < (sp._top + self._lineHeight):

                x, y, w, h = sp._clickBoxRect
                if xx > x  and xx < (x + w) and yy > y and yy < (y + h):
                    return sp, 'ClickBox'

                x, y, w, h = sp._iconBoxRect
                if xx > x  and xx < (x + w) and yy > y and yy < (y + h):
                    return sp, 'IconBox'

                x, y, w, h = sp._textBoxRect
                if xx > x  and xx < (x + w) and yy > y and yy < (y + h): 
                    return sp, 'TextBox'

                i = -1  
                for x, y, w, h in sp._headStringIcons:
                    i += 1
                    if xx > x  and xx < (x + w) and yy > y and yy <(y + h):
                       return sp, i

                return sp, 'Headline'

        return None, 'Canvas'

    #@-node:bob.20080111201957.101:hitTest
    #@+node:bob.20080111201957.102:_createNewBuffer
    def _createNewBuffer(self):
        """Create a new buffer for drawing."""


        if not self.window:
            g.trace('no window !!!!!!!!!!!!!!!!')
            g.trace(g.callers())
            return


        w, h = self.window.get_size()
        #g.trace(g.callers())


        if self._buffer:
            bw, bh = self._buffer.get_size()
            if bw >= w and bh >= h:
                return

        self._buffer = gtk.gdk.Pixmap(self.window, w, h)





    #@-node:bob.20080111201957.102:_createNewBuffer
    #@+node:bob.20080111201957.103:vscrollTo

    def vscrollTo(self, pos):
        """Scroll the canvas vertically to the specified position."""

        canvasHeight = self.get_allocation().height
        if (self._treeHeight - canvasHeight) < pos :
            pos = self._treeHeight - canvasHeight

        pos = max(0, pos)

        self._virtualTop = pos

        self.redraw()
    #@-node:bob.20080111201957.103:vscrollTo
    #@+node:bob.20080113073006:hscrollTo
    def hscrollTo(self, pos):
        """Scroll the canvas vertically to the specified position."""

        canvasWidth = self.get_allocation().width

        #g.trace(pos)

        if (self._treeWidth - canvasWidth) < pos :
            pos = min(0, self._treeWidth - canvasWidth)

        pos = max( 0, pos)

        self._virtualLeft = pos

        self.redraw()
    #@-node:bob.20080113073006:hscrollTo
    #@+node:bob.20080111201957.104:resize

    def resize(self):
        """Resize the outline canvas and, if required, create and draw on a new buffer."""

        c = self.c

        #c.beginUpdate()     #lock out events
        if 1: #try:

            self._createNewBuffer()

            #self._parent.hscrollUpdate()


            self.draw()
            self.refresh()


        #finally:
        #    c.endUpdate(False)


        return True





    #@-node:bob.20080111201957.104:resize
    #@+node:bob.20080112173505:redraw
    def redraw(self):
        self.draw()
        self.refresh()
    #@-node:bob.20080112173505:redraw
    #@+node:bob.20080111201957.106:update

    def update(self):
        """Do a full update assuming the tree has been changed."""

        c = self.c

        canvasHeight = self.get_allocation().height

        hoistFlag = bool(self.c.hoistStack)

        if hoistFlag:
            stk = [self.c.hoistStack[-1].p]
        else:
            stk = [self.c.rootPosition()]

        #@    << find height of tree and position of currentNode >>
        #@+node:bob.20080111201957.107:<< find height of tree and position of currentNode >>

        # Find the number of visible nodes in the outline.

        cp = c.currentPosition().copy()
        cpCount = None

        count = 0
        while stk:

            p = stk.pop()

            while p:


                if stk or not hoistFlag:
                    newp = p.next()
                else:
                    newp = None

                if cp and cp == p:
                    cpCount = count
                    cp = False

                count += 1

                #@        << if p.isExpanded() and p.hasFirstChild():>>
                #@+node:bob.20080111201957.108:<< if p.isExpanded() and p.hasFirstChild():>>
                ## if p.isExpanded() and p.hasFirstChild():

                v=p.v
                if v.statusBits & v.expandedBit and v.t._firstChild:
                #@nonl
                #@-node:bob.20080111201957.108:<< if p.isExpanded() and p.hasFirstChild():>>
                #@nl
                    stk.append(newp)
                    p = p.firstChild()
                    continue

                p = newp

        lineHeight = self._lineHeight

        self._treeHeight = count * lineHeight
        g.trace( 'treeheight ', self._treeHeight)

        if cpCount is not None:
            cpTop = cpCount * lineHeight

            if cpTop < self._virtualTop:
                self._virtualTop = cpTop

            elif cpTop + lineHeight > self._virtualTop + canvasHeight:
                self._virtualTop += (cpTop + lineHeight) - (self._virtualTop + canvasHeight)



        #@-node:bob.20080111201957.107:<< find height of tree and position of currentNode >>
        #@nl

        if (self._treeHeight - self._virtualTop) < canvasHeight:
            self._virtualTop = self._treeHeight - canvasHeight

        # if (self._treeHeight - self._virtualTop) < canvasHeight:
            # self._virtualTop = self._treeHeight - canvasHeight

        self.contextChanged()

        self.redraw()
        self._parent.vscrollUpdate()
        self._parent.hscrollUpdate()


    #@-node:bob.20080111201957.106:update
    #@+node:bob.20080111201957.109:onPaint

    def onPaint(self, *args):
        """Renders the off-screen buffer to the outline canvas."""

        # w, h are needed because the buffer may be bigger than the window.

        w, h = self.window.get_size()

        # We use self.style.black_gc only because we need a gc, it has no relavence.

        self.window.draw_drawable(self.style.black_gc ,self._buffer, 0, 0, 0, 0, w, h)
    #@-node:bob.20080111201957.109:onPaint
    #@+node:bob.20080112090335:onMap
    def onMap(self, *args):
        self._createNewBuffer()
        self.update()
        self.connect('expose-event', self.onPaint)
        self.connect("size-allocate", self.onSize)
    #@-node:bob.20080112090335:onMap
    #@+node:bob.20080112224841:onSize
    def onSize(self, *args):
        """React to changes in the size of the outlines display area."""


        c = self.c
        c.beginUpdate()
        try:
            self.resize()
            self._parent.vscrollUpdate()
            self._parent.hscrollUpdate()
        finally:
            c.endUpdate(False)


    #@-node:bob.20080112224841:onSize
    #@+node:bob.20080111201957.105:refresh

    #def refresh(self):
        # """Renders the offscreen buffer to the outline canvas."""
        # return

        # #print 'refresh'
        # wx.ClientDC(self).BlitPointSize((0,0), self._size, self._buffer, (0, 0))

    refresh = onPaint
    #@nonl
    #@-node:bob.20080111201957.105:refresh
    #@+node:bob.20080111201957.110:contextChanged
    def contextChanged(self):
        """Adjust canvas attributes after a change in context.

        This should be called after setting or changing fonts or icon size or
        anything that effects the tree display.

        """

        self._pangoLayout.set_text('Wy')
        self._fontHeight = self._pangoLayout.get_pixel_size()[1]
        self._iconSize = (20, 11) #(icons[0].GetWidth(), icons[0].GetHeight())

        self._clickBoxSize = (9, 9) #(plusBoxIcon.GetWidth(), plusBoxIcon.GetHeight())

        self._lineHeight = max(
            self._fontHeight,
            self._iconSize[1],
            self._requestedLineHeight
        ) + 2 * self._yPad

        # y offsets

        self._yTextOffset = (self._lineHeight - self._fontHeight)//2

        self._yIconOffset = (self._lineHeight - self._iconSize[1])//2

        self._clickBoxCenterOffset = (
            -self._textIndent*2 + self._iconSize[0]//2,
            self._lineHeight//2
        )

        self._clickBoxOffset = (
            self._clickBoxCenterOffset[0] - self._clickBoxSize[0]//2,
            (self._lineHeight  - self._clickBoxSize[1])//2
        )


    #@-node:bob.20080111201957.110:contextChanged
    #@+node:bob.20080111201957.111:requestLineHeight
    def requestLineHeight(height):
        """Request a minimum height for lines."""

        assert int(height) and height < 200
        self.requestedHeight = height
        self.beginUpdate()
        self.endUpdate()
    #@-node:bob.20080111201957.111:requestLineHeight
    #@+node:bob.20080111201957.112:def draw

    def draw(self, *args):
        """Draw the outline on the off-screen buffer."""

        r, g, b = colors.getColorRGB('leoyellow')
        r, g, b = r/255.0, g/255.0, b/255.0

        x, y, canvasWidth, canvasHeight = self.get_allocation()


        pangoLayout = self._pangoLayout


        cr = self._buffer.cairo_create()


        cr.set_source_rgb(r, g, b)
        cr.rectangle(x, y, canvasWidth, canvasHeight)
        cr.fill()

        c = self.c


        top = self._virtualTop
        if top < 0:
            self._virtualTop = top = 0

        left = self._virtualLeft
        if left < 0:
            self._virtualLeft = left = 0   


        bottom = top + canvasHeight


        textIndent = self._textIndent
        treeWidth = self._treeWidth

        yPad = self._yPad
        xPad = self._xPad - left

        yIconOffset = self._yIconOffset

        yTextOffset = self._yTextOffset

        clickBoxOffset_x, clickBoxOffset_y = self._clickBoxOffset

        clickBoxCenterOffset_x, clickBoxCenterOffset_y = \
            self._clickBoxCenterOffset

        clickBoxSize_w, clickBoxSize_h = self._clickBoxSize

        iconSize_w, iconSize_h = self._iconSize

        lineHeight = self._lineHeight
        halfLineHeight = lineHeight//2

        #@    << draw tree >>
        #@+node:bob.20080111201957.113:<< draw tree >>
        y = 0

        hoistFlag = bool(c.hoistStack)

        if hoistFlag:
            stk = [c.hoistStack[-1].p]
        else:
            stk = [c.rootPosition()]

        self._positions = positions = []

        #@+at
        # My original reason for writing the loop this way was to make it as 
        # fast as
        # possible. Perhaps I was being a bit too paranoid and we should 
        # change back to
        # more conventional iterations, on the other hand if it ain't broke 
        # don't fix it.
        #@-at
        #@@c


        while stk:

            p = stk.pop()

            while p:

                if stk or not hoistFlag:
                    newp = p.next()
                else:
                    newp = None

                mytop = y
                y = y + lineHeight

                if mytop > bottom:
                    stk = []
                    p = None
                    break

                if y > top:

                    sp = p.copy()

                    #@            << setup object >>
                    #@+node:bob.20080111201957.114:<< set up object >>
                    # depth: the depth of indentation relative to the current hoist.
                    sp._depth = len(stk)

                    # virtualTop: top of the line in virtual canvas coordinates
                    sp._virtualTop =  mytop

                    # top: top of the line in real canvas coordinates
                    sp._top = mytop - top


                    pangoLayout.set_text(sp.headString())

                    textSize_w, textSize_h = pangoLayout.get_pixel_size()

                    xTextOffset = ((sp._depth +1) * textIndent) + xPad

                    textPos_x = xTextOffset # - self._hadj.value
                    textPos_y =  sp._top + yTextOffset

                    iconPos_x = textPos_x - textIndent
                    iconPos_y = textPos_y + yIconOffset

                    clickBoxPos_x = textPos_x + clickBoxOffset_x
                    clickBoxPos_y = textPos_y + clickBoxOffset_y

                    sp._clickBoxCenter_x = clickBoxPos_x + clickBoxCenterOffset_x
                    sp._clickBoxCenter_y = clickBoxPos_y + clickBoxCenterOffset_y

                    sp._textBoxRect = [textPos_x, textPos_y, textSize_w, textSize_h]
                    sp._iconBoxRect = [iconPos_x, iconPos_y, iconSize_w, iconSize_h]
                    sp._clickBoxRect = [clickBoxPos_x, clickBoxPos_y, clickBoxSize_w, clickBoxSize_h]

                    sp._icon = icons[p.v.computeIcon()]


                    if sp.hasFirstChild():
                        sp._clickBoxIcon = plusBoxIcon
                        if sp.isExpanded():
                            sp._clickBoxIcon = minusBoxIcon
                    else:
                        sp._clickBoxIcon = None

                    sp._clickRegions = []

                    #@-node:bob.20080111201957.114:<< set up object >>
                    #@nl

                    positions.append(sp)

                    treeWidth = max(
                        treeWidth,
                        textSize_w + xTextOffset + left
                    )

                #@        << if p.isExpanded() and p.hasFirstChild():>>
                #@+node:bob.20080111201957.108:<< if p.isExpanded() and p.hasFirstChild():>>
                ## if p.isExpanded() and p.hasFirstChild():

                v=p.v
                if v.statusBits & v.expandedBit and v.t._firstChild:
                #@nonl
                #@-node:bob.20080111201957.108:<< if p.isExpanded() and p.hasFirstChild():>>
                #@nl
                    stk.append(newp)
                    p = p.firstChild()
                    continue

                p = newp

        if treeWidth > self._treeWidth:
            # theoretically this could be recursive
            # but its unlikely ...
            self._treeWidth = treeWidth
            self._parent.hscrollUpdate()

        if not positions:
            #g.trace('No positions!')
            return

        self._virtualTop =  positions[0]._virtualTop


        # try:
            # result = self._leoTree.drawTreeHook(self)
            # print 'result =', result
        # except:
            # result = False
            # print 'result is False'

        # if hasattr(self._leoTree, 'drawTreeHook'):
            # try:
                # result = self._leoTree.drawTreeHook(self)
            # except:
                # result = False
        # else:
            # #print 'drawTreeHook not known'
            # result = None

        # if not result:
        if 1:
            #@    << draw text >>
            #@+node:bob.20080111201957.115:<< draw text >>

            current = c.currentPosition()



            for sp in positions:

                #@    << draw user icons >>
                #@+node:bob.20080111201957.116:<< draw user icons >>


                try:
                    headStringIcons = sp.v.t.unknownAttributes.get('icons', [])
                except:
                    headStringIcons = None

                sp._headStringIcons = hsi = []

                if headStringIcons:

                    for headStringIcon in headStringIcons:
                        try:
                            image = globalImages[headStringIcon['relPath']]
                        except KeyError:
                            path = headStringIcon['relPath']
                            image = getImage(path)
                            if image is None:
                                return


                        x, y, w, h = sp._textBoxRect

                        hsi.append((x, y, image.get_width(), image.get_height()))       

                        cr.set_source_pixbuf(image, x, y)
                        cr.paint()

                        sp._textBoxRect[0] = x + image.get_width() + 5

                #@-node:bob.20080111201957.116:<< draw user icons >>
                #@nl

                # if current and current == sp:
                    # dc.SetBrush(wx.LIGHT_GREY_BRUSH)
                    # dc.SetPen(wx.LIGHT_GREY_PEN)
                    # dc.DrawRectangleRect(
                        # wx.Rect(*sp._textBoxRect).Inflate(3, 3)
                    # )
                    # current = False
                    # #dc.SetBrush(wx.TRANSPARENT_BRUSH)
                    # #dc.SetPen(wx.BLACK_PEN)


                pangoLayout.set_text(sp.headString())
                x, y, w, h = sp._textBoxRect
                cr.set_source_rgb(0, 0, 0)
                cr.move_to(x, y)
                #cr.update_layout(pangoLayout)
                cr.show_layout(pangoLayout)


            #@-node:bob.20080111201957.115:<< draw text >>
            #@nl
            #@    << draw lines >>
            #@+node:bob.20080111201957.117:<< draw lines >>
            #@-node:bob.20080111201957.117:<< draw lines >>
            #@nl
            #@    << draw bitmaps >>
            #@+node:bob.20080111201957.118:<< draw bitmaps >>

            for sp in positions:

                x, y, w, h = sp._iconBoxRect

                cr.set_source_pixbuf(sp._icon,x,y)
                cr.paint()
                #cr.stroke()

                if sp._clickBoxIcon:
                    x, y, w, h = sp._clickBoxRect
                    cr.set_source_pixbuf(sp._clickBoxIcon, x, y)
                    cr.paint()

            #@+at
            #   ctx = da.window.cairo_create()
            #   # You can put ctx.scale(..) or ctx.rotate(..) here, if you 
            # need some
            #   ct = gtk.gdk.CairoContext(ctx)
            #   ct.set_source_pixbuf(pixbuf,0,0)
            #   ctx.paint()
            #   ctx.stroke()
            # 
            # 
            # 
            # 
            #@-at
            #@-node:bob.20080111201957.118:<< draw bitmaps >>
            #@nl

            #@    << draw focus >>
            #@+node:bob.20080111201957.119:<< draw focus >>
            if 0:
                dc.SetBrush(wx.TRANSPARENT_BRUSH)
                if self._leoTree.hasFocus():
                    dc.SetPen(wx.BLACK_PEN)
                #else:
                #    dc.SetPen(wx.GREEN_PEN)
                    dc.DrawRectanglePointSize( (0,0), self.GetSize())
            #@nonl
            #@-node:bob.20080111201957.119:<< draw focus >>
            #@nl




        #@-node:bob.20080111201957.113:<< draw tree >>
        #@nl

        #self._parent.showEntry()

        return True






    #@-node:bob.20080111201957.112:def draw
    #@-others
#@-node:bob.20080111201957.96:class OutlineCanvas
#@-others

def abspath(*args):
    return os.path.abspath(os.path.join(*args))



if __name__ == "__main__": 

    leoDir = abspath(sys.path[0],'..')

    sys.path.insert(0, abspath(leoDir, 'src'))

    import leoBridge

    controller = leoBridge.controller(gui='nullGui')
    g = controller.globals()
    c = controller.openLeoFile(abspath(leoDir, 'test', 'unitTest.leo'))

    outlineFont = ''

    colors = g.importExtension('colors')

    GtkLeoTreeDemo()

    gtk.main()


#@-node:bob.20080111200056:@thin gtkOutlineDemo.py
#@-leo
