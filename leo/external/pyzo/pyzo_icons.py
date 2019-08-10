# -*- coding: utf-8 -*-
"""
A new module containing (for now) *copies* of icon-related code.
"""
import leo.core.leoGlobals as leo_g
assert leo_g
from leo.core.leoQt import QtCore, QtGui, QtWidgets
import os

pyzo = leo_g.TracingNullObject(tag='pyzo_icons.pyzo')
ssdf = leo_g.TracingNullObject(tag='pyzo_icons.ssdf')

def loadAppIcons(): # From __main__.py
    """ loadAppIcons()
    Load the application icons.
    """
    # Get directory containing the icons
    appiconDir =  os.path.join(pyzo.pyzoDir, 'resources', 'appicons')

    # Determine template for filename of the application icon-files.
    fnameT = 'pyzologo{}.png'

    # Construct application icon. Include a range of resolutions. Note that
    # Qt somehow does not use the highest possible res on Linux/Gnome(?), even
    # the logo of qt-designer when alt-tabbing looks a bit ugly.
    pyzo.icon = QtGui.QIcon()
    for sze in [16, 32, 48, 64, 128, 256]:
        fname = os.path.join(appiconDir, fnameT.format(sze))
        if os.path.isfile(fname):
            pyzo.icon.addFile(fname, QtCore.QSize(sze, sze))

    # Set as application icon. This one is used as the default for all
    # windows of the application.
    QtWidgets.qApp.setWindowIcon(pyzo.icon)

    # Construct another icon to show when the current shell is busy
    artist = IconArtist(pyzo.icon) # extracts the 16x16 version
    artist.setPenColor('#0B0')
    for x in range(11, 16):
        d = x-11 # runs from 0 to 4
        artist.addLine(x,6+d,x,15-d)
    pm = artist.finish().pixmap(16,16)
    #
    pyzo.iconRunning = QtGui.QIcon(pyzo.icon)
    pyzo.iconRunning.addPixmap(pm) # Change only 16x16 icon
def loadIcons(): # From __main__.py
    """ loadIcons()
    Load all icons in the icon dir.
    """
    # Get directory containing the icons
    iconDir = os.path.join(pyzo.pyzoDir, 'resources', 'icons')

    # Construct other icons
    dummyIcon = IconArtist().finish()
    ### if leo_g: leo_g.trace('loadIcons: dummyIcon: %r' % dummyIcon)
    pyzo.icons = ssdf.new()
    for fname in os.listdir(iconDir):
        if fname.endswith('.png'):
            try:
                # Short and full name
                name = fname.split('.')[0]
                name = name.replace('pyzo_', '')  # discart prefix
                ffname = os.path.join(iconDir,fname)
                # Create icon
                icon = QtGui.QIcon()
                icon.addFile(ffname, QtCore.QSize(16,16))
                # Store
                pyzo.icons[name] = icon
                leo_g.trace('icon', icon)
            except Exception as err:
                pyzo.icons[name] = dummyIcon
                print('Could not load icon %s: %s' % (fname, str(err)))
def loadFonts(): # From __main__.py
    """ loadFonts()
    Load all fonts that come with Pyzo.
    """
    import pyzo.codeeditor  # we need pyzo and codeeditor namespace here

    # Get directory containing the icons
    fontDir = os.path.join(pyzo.pyzoDir, 'resources', 'fonts')

    # Get database object
    db = QtGui.QFontDatabase()

    # Set default font
    pyzo.codeeditor.Manager.setDefaultFontFamily('DejaVu Sans Mono')

    # Load fonts that are in the fonts directory
    if os.path.isdir(fontDir):
        for fname in os.listdir(fontDir):
            if 'oblique' in fname.lower():  # issue #461
                continue
            if os.path.splitext(fname)[1].lower() in ['.otf', '.ttf']:
                try:
                    db.addApplicationFont( os.path.join(fontDir, fname) )
                except Exception as err:
                    print('Could not load font %s: %s' % (fname, str(err)))
class IconArtist: # From icons.py
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
        if isinstance(icon, tuple):
            pm = QtGui.QPixmap(icon[0], icon[1])
            pm.fill(QtGui.QColor(0,0,0,0))
            return pm
        if isinstance(icon, QtGui.QPixmap):
            return icon
        if isinstance(icon, QtGui.QIcon):
            return icon.pixmap(16, 16)
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
