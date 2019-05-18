# -*- coding: utf-8 -*-
# Copyright (C) 2016, the Pyzo development team
#
# Pyzo is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

""" Icons module

Defines functionality for creating icons by composing different overlays
and also by directly drawing into the pixmap. This allows making icons
that show information to the user in a very effective, yet subtle manner.

"""

from pyzo.util.qt import QtCore, QtGui, QtWidgets
import pyzo


class IconArtist:
    """ IconArtist(icon=None)
    
    Object to draw icons with. Can be instantiated with an existing icon
    or as a blank icon. Perform operations and then use finish() to
    obtain the result.
    
    """
    
    def __init__(self, icon=None):
        
        # Get pixmap from given icon (None creates empty pixmap)
        self._pm = self._getPixmap(icon)
        
        # Instantiate painter for the pixmap
        self._painter = QtGui.QPainter()
        self._painter.begin(self._pm)
    
    
    def finish(self, icon=None):
        """ finish()
        Finish the drawing and return the resulting icon.
        """
        self._painter.end()
        return QtGui.QIcon(self._pm)
    
    
    def _getPixmap(self, icon):
        
        # Get icon if given by name
        if isinstance(icon, str):
            icon = pyzo.icons[icon]
        
        # Create pixmap
        if icon is None:
            pm = QtGui.QPixmap(16, 16)
            pm.fill(QtGui.QColor(0,0,0,0))
            return pm
        elif isinstance(icon, tuple):
            pm = QtGui.QPixmap(icon[0], icon[1])
            pm.fill(QtGui.QColor(0,0,0,0))
            return pm
        elif isinstance(icon, QtGui.QPixmap):
            return icon
        elif isinstance(icon, QtGui.QIcon):
            return icon.pixmap(16, 16)
        else:
            raise ValueError('Icon for IconArtis should be icon, pixmap or name.')
    
    
    def setPenColor(self, color):
        """ setPenColor(color)
        Set the color of the pen. Color can be anything that can be passed to
        Qcolor().
        """
        pen = QtGui.QPen()
        if isinstance(color, tuple):
            pen.setColor(QtGui.QColor(*color))
        else:
            pen.setColor(QtGui.QColor(color))
        self._painter.setPen(pen)
    
    
    def addLayer(self, overlay, x=0, y=0):
        """ addOverlay(overlay, x=0, y=0)
        Add an overlay icon to the icon (add the specified position).
        """
        pm = self._getPixmap(overlay)
        self._painter.drawPixmap(x, y, pm)
    
    
    def addLine(self, x1, y1, x2, y2):
        """ addLine( x1, y1, x2, y2)
        Add a line to the icon.
        """
        self._painter.drawLine(x1, y1, x2, y2)
    
    def addPoint(self, x, y):
        """ addPoint( x, y)
        Add a point to the icon.
        """
        self._painter.drawPoint(x, y)
    
    def addMenuArrow(self, strength=100):
        """ addMenuArrow()
        Adds a menu arrow to the icon to let the user know the icon
        is clickable.
        """
        x, y = 0, 12
        a1, a2 = int(strength/2), strength
        # Zeroth line of 3+2
        self.setPenColor((0,0,0,a1))
        self.addPoint(x+0,y-1); self.addPoint(x+4,y-1)
        self.setPenColor((0,0,0,a2))
        self.addPoint(x+1,y-1); self.addPoint(x+2,y-1); self.addPoint(x+3,y-1)
        # First line of 3+2
        self.setPenColor((0,0,0,a1))
        self.addPoint(x+0,y+0); self.addPoint(x+4,y+0)
        self.setPenColor((0,0,0,a2))
        self.addPoint(x+1,y+0); self.addPoint(x+2,y+0); self.addPoint(x+3,y+0)
        # Second line of 3
        self.addPoint(x+1,y+1); self.addPoint(x+2,y+1); self.addPoint(x+3,y+1)
        # Third line of 1+2
        self.addPoint(x+2,y+2)
        self.setPenColor((0,0,0,a1))
        self.addPoint(x+1,y+2); self.addPoint(x+3,y+2)
        # Fourth line of 1
        self.setPenColor((0,0,0,a2))
        self.addPoint(x+2,y+3)


# todo: not used; remove me?
class TabCloseButton(QtWidgets.QToolButton):
    """ TabCloseButton
    
    This class implements a very compact close button to be used in tabs.
    It allows managing tab (the closing part of it) in a fast and intuitive
    fashion.
    
    """
    
    SIZE = 5,8
    
    def __init__(self):
        QtWidgets.QToolButton.__init__(self)
        
        # Init
        self.setIconSize(QtCore.QSize(*self.SIZE))
        self.setStyleSheet("QToolButton{ border:none; padding:0px; margin:0px; }")
        self.setIcon(self.getCrossIcon1())
    
    def mousePressEvent(self, event):
        # Get tabs
        tabs = self.parent().parent()
        # Get index from position
        pos = self.mapTo(tabs, event.pos())
        index = tabs.tabBar().tabAt(pos)
        # Close it
        tabs.tabCloseRequested.emit(index)
        
    def enterEvent(self, event):
        QtWidgets.QToolButton.enterEvent(self, event)
        self.setIcon(self.getCrossIcon2())
    
    def leaveEvent(self, event):
        QtWidgets.QToolButton.leaveEvent(self, event)
        self.setIcon(self.getCrossIcon1())
        
    def _createCrossPixmap(self, alpha):
        artist = IconArtist(self.SIZE)
        #
        artist.setPenColor((0,0,0,alpha))
        #
        artist.addPoint(0,0); artist.addPoint(1,1)
        artist.addPoint(2,2); artist.addPoint(3,3)
        artist.addPoint(4,4)
        artist.addPoint(0,4); artist.addPoint(1,3)
        artist.addPoint(3,1); artist.addPoint(4,0)
        #
        artist.setPenColor((0,0,0,int(0.5*alpha)))
        #
        artist.addPoint(1,0); artist.addPoint(0,1)
        artist.addPoint(2,1); artist.addPoint(1,2)
        artist.addPoint(3,2); artist.addPoint(2,3)
        artist.addPoint(4,3); artist.addPoint(3,4)
        #
        artist.addPoint(0,3); artist.addPoint(1,4)
        artist.addPoint(3,0); artist.addPoint(4,1)
        #
        return artist.finish().pixmap(*self.SIZE)
    
    def getCrossIcon1(self):
        if hasattr(self, '_cross1'):
            pm = self._cross1
        else:
            pm = self._createCrossPixmap(80)
        return QtGui.QIcon(pm)
    
    def getCrossIcon2(self):
        if hasattr(self, '_cross2'):
            pm = self._cross2
        else:
            pm = self._createCrossPixmap(240)
        # Set
        return QtGui.QIcon(pm)


# todo: not used; remove me?
class ToolButtonWithMenuIndication(QtWidgets.QToolButton):
    """ ToolButtonWithMenuIndication
    
    Tool button that wraps the icon in a slightly larger icon that
    contains a small arrow that lights up when hovering over the icon.
    
    The button itself is not drawn. If the icon is clicked, the
    customContextMenuRequested signal of the "grandparent" is emitted. In
    this way we realize a suble icon that can be clicked on to show a menu.
    
    """
    
    SIZE = 21, 16
    
    def __init__(self):
        QtWidgets.QToolButton.__init__(self)
        
        # Init
        self.setIconSize(QtCore.QSize(*self.SIZE))
        self.setStyleSheet("QToolButton{ border: none; }")
        
        # Create arrow pixmaps
        self._menuarrow1 = self._createMenuArrowPixmap(0)
        self._menuarrow2 = self._createMenuArrowPixmap(70)
        self._menuarrow = self._menuarrow1
        
        # Variable to keep icon
        self._icon = None
        
        # Variable to keep track of when the mouse was pressed, so that
        # we can allow dragging as well as clicking the menu.
        self._menuPressed = False
    
    def mousePressEvent(self, event):
        # Ignore event so that the tabbar will change to that tab
        event.ignore()
        self._menuPressed = event.pos()
    
    def mouseMoveEvent(self, event):
        QtWidgets.QToolButton.mouseMoveEvent(self, event)
        if self._menuPressed:
            dragDist = QtWidgets.QApplication.startDragDistance()
            if (event.pos()-self._menuPressed).manhattanLength() >= dragDist:
                self._menuPressed = False
    
    def mouseReleaseEvent(self, event):
        event.ignore()
        if self._menuPressed:
            tabs = self.parent().parent()
            pos = self.mapTo(tabs, event.pos())
            tabs.customContextMenuRequested.emit(pos)
        
    def enterEvent(self, event):
        QtWidgets.QToolButton.enterEvent(self, event)
        self._menuarrow = self._menuarrow2
        self.setIcon()
        self._menuPressed = False
    
    def leaveEvent(self, event):
        QtWidgets.QToolButton.leaveEvent(self, event)
        self._menuarrow = self._menuarrow1
        self.setIcon()
        self._menuPressed = False
    
    
    def setIcon(self, icon=None):
        
        # Store icon if given, otherwise use buffered version
        if icon is not None:
            self._icon = icon
        
        # Compose icon by superimposing the menuarrow pixmap
        artist = IconArtist(self.SIZE)
        if self._icon:
            artist.addLayer(self._icon, 5, 0)
        artist.addLayer(self._menuarrow, 0,0)
        icon = artist.finish()
        
        # Set icon
        QtWidgets.QToolButton.setIcon(self, icon)
    
    
    def _createMenuArrowPixmap(self, strength):
        artist = IconArtist()
        artist.addMenuArrow(strength)
        return artist.finish().pixmap(16,16)



class TabToolButton(QtWidgets.QToolButton):
    """ TabToolButton
    
    Base menu for editor and shell tabs.
    
    """
    
    SIZE = 16, 16
    
    def __init__(self, *args):
        QtWidgets.QToolButton.__init__(self, *args)
        
        # Init
        self.setIconSize(QtCore.QSize(*self.SIZE))
        self.setStyleSheet("QToolButton{ border: none; }")
    
    def mousePressEvent(self, event):
        # Ignore event so that the tabbar will change to that tab
        event.ignore()



class TabToolButtonWithCloseButton(TabToolButton):
    """ TabToolButtonWithCloseButton
    
    Tool button that wraps the icon in a slightly larger icon that
    contains a small cross that can be used to invoke a close request.
    
    """
    
    SIZE = 22, 16
    CROSS_OFFSET = 0, 2
    
    def __init__(self, *args):
        TabToolButton.__init__(self, *args)
        
        # Variable to keep icon
        self._icon = None
        self._cross = self.getCrossPixmap1()
        
        # For mouse tracking inside icon
        self.setMouseTracking(True)
        self._overCross = False
    
    
    def _isOverCross(self, pos):
        x1, x2 = self.CROSS_OFFSET[0], self.CROSS_OFFSET[0]+5+1
        y1, y2 = self.CROSS_OFFSET[1], self.CROSS_OFFSET[1]+5+1
        if pos.x()>=x1 and pos.x()<=x2 and pos.y()>=y1 and pos.y()<=y2:
            return True
        else:
            return False
        
    
    def mousePressEvent(self, event):
        if self._isOverCross(event.pos()):
            # Accept event so that the tabbar will NOT change to that tab
            event.accept()
        else:
            event.ignore()
    
    
    def mouseReleaseEvent(self, event):
        if self._isOverCross(event.pos()):
            event.accept()
            # Get tabs
            tabs = self.parent().parent()
            # Get index from position
            pos = self.mapTo(tabs, event.pos())
            index = tabs.tabBar().tabAt(pos)
            # Close it
            tabs.tabCloseRequested.emit(index)
        else:
            event.ignore()
    
    
    def mouseMoveEvent(self, event):
        QtWidgets.QToolButton.mouseMoveEvent(self, event)
        new_overCross = self._isOverCross(event.pos())
        if new_overCross != self._overCross:
            self._overCross = new_overCross
            if new_overCross:
                self._cross = self.getCrossPixmap2()
            else:
                self._cross = self.getCrossPixmap1()
            self.setIcon()
    
    def leaveEvent(self, event):
        if self._overCross:
            self._overCross =  False
            self._cross = self.getCrossPixmap1()
            self.setIcon()
    
    
    def setIcon(self, icon=None):
        
        # Store icon if given, otherwise use buffered version
        if icon is not None:
            self._icon = icon
        
        # Compose icon by superimposing the menuarrow pixmap
        artist = IconArtist(self.SIZE)
        if self._icon:
            if self.CROSS_OFFSET[0] > 8:
                artist.addLayer(self._icon, 0,0)
            else:
                artist.addLayer(self._icon, 6,0)
        artist.addLayer(self._cross, *self.CROSS_OFFSET)
        icon = artist.finish()
        
        # Set icon
        QtWidgets.QToolButton.setIcon(self, icon)
    
    
    def _createMenuArrowPixmap(self, strength):
        artist = IconArtist()
        artist.addMenuArrow(strength)
        return artist.finish().pixmap(16,16)
    
    
    def _createCrossPixmap(self, alpha):
        artist = IconArtist((5,5))
        #
        artist.setPenColor((0,0,0,alpha))
        #
        artist.addPoint(0,0); artist.addPoint(1,1)
        artist.addPoint(2,2); artist.addPoint(3,3)
        artist.addPoint(4,4)
        artist.addPoint(0,4); artist.addPoint(1,3)
        artist.addPoint(3,1); artist.addPoint(4,0)
        #
        artist.setPenColor((0,0,0,int(0.5*alpha)))
        #
        artist.addPoint(1,0); artist.addPoint(0,1)
        artist.addPoint(2,1); artist.addPoint(1,2)
        artist.addPoint(3,2); artist.addPoint(2,3)
        artist.addPoint(4,3); artist.addPoint(3,4)
        #
        artist.addPoint(0,3); artist.addPoint(1,4)
        artist.addPoint(3,0); artist.addPoint(4,1)
        #
        return artist.finish().pixmap(5,5)
    
    
    def getCrossPixmap1(self):
        if hasattr(self, '_cross1'):
            pm = self._cross1
        else:
            pm = self._createCrossPixmap(50)
        return pm
    
    def getCrossPixmap2(self):
        if hasattr(self, '_cross2'):
            pm = self._cross2
        else:
            pm = self._createCrossPixmap(240)
        # Set
        return pm



class EditorTabToolButton(TabToolButtonWithCloseButton):
    """ Button for the tabs of the editors. This is just a
    tight wrapper for the icon.
    """
    
    def updateIcon(self, isDirty, isMain, isPinned, nBlocks=10001):
        
        # Init drawing
        artist = IconArtist()
        
        # Create base
        if isDirty:
            artist.addLayer('page_white_dirty')
            artist.setPenColor('#f00')
        else:
            artist.addLayer('page_white')
            artist.setPenColor('#444')
        
        # Paint lines
        if not nBlocks:
            nLines = 0
        elif nBlocks <= 10: nLines = 1
        elif nBlocks <= 100: nLines = 2
        elif nBlocks <= 1000: nLines = 3
        elif nBlocks <= 10000: nLines = 4
        else: nLines = 5
        #
        fraction = float(nBlocks) / 10**nLines
        fraction = min(fraction, 1.0)
        #
        for i in range(nLines):
            y = 4 + 2 * i
            n = 5
            if y>6: n = 8
            #if i == nLines-1:
            #    n = int(fraction * n)
            artist.addLine(4,y,4+n,y)
        
        # Overlays
        if isMain:
            artist.addLayer('overlay_star')
        if isPinned:
            artist.addLayer('overlay_thumbnail')
        if isDirty:
            artist.addLayer('overlay_disk')
        
        # Apply
        self.setIcon(artist.finish())



class ShellIconMaker:
    """ Object that can make an icon for the shells
    """
    
    POSITION = (6,7) # absolute position of center of wheel.
    
    # Relative position for the wheel at two levels. Center is at (3,,3)
    POSITIONS1 = [(2,2), (3,2), (4,2), (4,3), (4,4), (3,4), (2,4), (2,3)]
    POSITIONS2 = [  (2,1), (3,1), (4,1), (5,2), (5,3), (5,4),
                    (4,5), (3,5), (2,5), (1,4), (1,3), (1,2) ]
    
    # Maps to make transitions between levels more natural
    MAP1to2 = [1,2, 4,5, 7,8, 10,11]
    MAP2to1 = [1,2,3,  3,4,5, 5,6,7, 7,0,1]
    
    MAX_ITERS_IN_LEVEL_1 = 2
    
    
    def __init__(self, objectWithIcon):
        
        self._objectWithIcon = objectWithIcon
        
        # Motion properties
        self._index = 0
        self._level = 0
        self._count = 0  #  to count number of iters in level 1
        
        # Prepare blob pixmap
        self._blob = self._createBlobPixmap()
        self._legs = self._createLegsPixmap()
        
        # Create timer
        self._timer = QtCore.QTimer(None)
        self._timer.setInterval(150)
        self._timer.setSingleShot(False)
        self._timer.timeout.connect(self.onTimer)
    
    
    def setIcon(self, icon):
        self._objectWithIcon.setIcon(icon)
    
    
    def _createBlobPixmap(self):
        
        artist = IconArtist()
        artist.setPenColor((0,150,0,255))
        artist.addPoint(1,1)
        artist.setPenColor((0,150,0, 200))
        artist.addPoint(1,0); artist.addPoint(1,2)
        artist.addPoint(0,1); artist.addPoint(2,1)
        artist.setPenColor((0,150,0, 100))
        artist.addPoint(0,0); artist.addPoint(2,0)
        artist.addPoint(0,2); artist.addPoint(2,2)
        return artist.finish().pixmap(16,16)
    
    
    def _createLegsPixmap(self):
        artist = IconArtist()
        x,y = self.POSITION
        artist.setPenColor((0,50,0,150))
        artist.addPoint(x+1,y-1); artist.addPoint(x+1,y-2); artist.addPoint(x+0,y-2)
        artist.addPoint(x+3,y+1); artist.addPoint(x+4,y+1); artist.addPoint(x+4,y+2)
        artist.addPoint(x+2,y+3); artist.addPoint(x+2,y+4)
        artist.addPoint(x+0,y+3); artist.addPoint(x+0,y+4)
        artist.addPoint(x-1,y+2); artist.addPoint(x-2,y+2)
        artist.addPoint(x-1,y+0); artist.addPoint(x-2,y+0)
        return artist.finish().pixmap(16,16)
    
    
    def updateIcon(self, status='Ready'):
        """ updateIcon(status)
        Public method to set what state the icon must show.
        """
        
        # Normalize and store
        if isinstance(status, str):
            status = status.lower()
        self._status = status
        
        # Handle
        if status == 'busy':
            self._index = 0
            if self._level == 2:
                self._index = self.MAP2to1[self._index]
            self._level = 1
            
        elif status == 'very busy':
            self._index = 0
            if self._level == 1:
                self._index = self.MAP1to2[self._index]
            self._level = 2
        
        else:
            self._level = 0
        
        # At least one timer iteration
        self._timer.start()
    
    
    def _nextIndex(self):
        self._index += 1
        if self._level == 1 and self._index >= 8:
            self._index = 0
        elif self._level == 2 and self._index >= 12:
            self._index = 0
    
    def _index1(self):
        return self._index
    
    
    def _index2(self):
        n = [0, 8, 12][self._level]
        index = self._index + n/2
        if index >= n:
            index -= n
        return int(index)
    
    
    def onTimer(self):
        """ onTimer()
        Invoked on each timer iteration. Will call the static drawing
        methods if in level 0. Otherwise will invoke drawInMotion().
        This method also checks if we should change levels and calculates
        how this is best achieved.
        """
        if self._level == 0:
            # Turn of timer
            self._timer.stop()
            # Draw
            if self._status in ['ready', 'more']:
                self.drawReady()
            elif self._status == 'debug':
                self.drawDebug()
            elif self._status == 'dead':
                self.drawDead()
            else:
                self.drawDead()
        
        elif self._level == 1:
            # Draw
            self.drawInMotion()
            # Next, this is always intermediate
            self._nextIndex()
            self._count += 1
        
        elif self._level == 2:
            # Draw
            self.drawInMotion()
            # Next
            self._nextIndex()
    
    
    def drawReady(self):
        """ drawReady()
        Draw static icon for when in ready mode.
        """
        artist = IconArtist("application")
        artist.addLayer(self._blob, *self.POSITION)
        self.setIcon(artist.finish())
    
    
    def drawDebug(self):
        """ drawDebug()
        Draw static icon for when in debug mode.
        """
        artist = IconArtist("application")
        artist.addLayer(self._blob, *self.POSITION)
        artist.addLayer(self._legs)
        self.setIcon(artist.finish())
    
    
    def drawDead(self):
        """ drawDead()
        Draw static empty icon for when the kernel is dead.
        """
        artist = IconArtist("application")
        self.setIcon(artist.finish())
    
    
    def drawInMotion(self):
        """ drawInMotion()
        Draw one frame of the icon in motion. Position of the blobs
        is determined from the index and the list of locations.
        """
        
        # Init drawing
        artist = IconArtist("application")
        
        # Define params
        dx, dy = self.POSITION[0]-3, self.POSITION[1]-3
        blob = self._blob
        #
        if self._level == 1:
            positions = self.POSITIONS1
        elif self._level == 2:
            positions = self.POSITIONS2
        
        # Draw
        pos1 = positions[self._index1()]
        pos2 = positions[self._index2()]
        artist.addLayer(blob, pos1[0]+dx, pos1[1]+dy)
        artist.addLayer(blob, pos2[0]+dx, pos2[1]+dy)
        
        # Done
        self.setIcon(artist.finish())

