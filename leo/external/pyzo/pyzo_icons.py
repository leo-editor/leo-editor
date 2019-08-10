# -*- coding: utf-8 -*-
"""
A new module containing (for now) *copies* of icon-related code.
"""
import leo.core.leoGlobals as leo_g
assert leo_g
from leo.core.leoQt import QtCore, QtGui #, QtWidgets
import os
import sys

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
            icon = pyzo_icons[icon]

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
class PyzoIcons(dict): # From zon.py

    '''
    A dict that allows attribute access.
    A simplified version of the Dict class in zon.py.
    '''
    
    def __getattribute__(self, key):
        try:
            return object.__getattribute__(self, key)
        except AttributeError:
            if key in self:
                return self[key]
            else:
                raise

    def __setattr__(self, key, val):
        self[key] = val
def loadIcons(): # From __main__.py
    """ Load all icons in the icon dir."""
    # Get directory containing the icons
    # EKR:change
        # iconDir = os.path.join(pyzo.pyzoDir, 'resources', 'icons')
    iconDir = leo_g.os_path_finalize_join(leo_g.app.loadDir, '..',
        'external', 'pyzo', 'resources', 'icons')

    # Construct other icons
    dummyIcon = IconArtist().finish()
    ### pyzo.icons = ssdf.new()
    pyzo_icons = PyzoIcons() # EKR:change.
        
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
                pyzo_icons[name] = icon
            except Exception as err:
                pyzo_icons[name] = dummyIcon
                print('Could not load icon %s: %s' % (fname, str(err)))
    return pyzo_icons # EKR:change
def appdata_dir(appname=None, roaming=False, macAsLinux=False):
    """ appdata_dir(appname=None, roaming=False,  macAsLinux=False)
    Get the path to the application directory, where applications are allowed
    to write user specific files (e.g. configurations). For non-user specific
    data, consider using common_appdata_dir().
    If appname is given, a subdir is appended (and created if necessary).
    If roaming is True, will prefer a roaming directory (Windows Vista/7).
    If macAsLinux is True, will return the Linux-like location on Mac.
    """

    # Define default user directory
    userDir = os.path.expanduser('~')

    # Get system app data dir
    path = None
    if sys.platform.startswith('win'):
        path1, path2 = os.getenv('LOCALAPPDATA'), os.getenv('APPDATA')
        path = (path2 or path1) if roaming else (path1 or path2)
    elif sys.platform.startswith('darwin') and not macAsLinux:
        path = os.path.join(userDir, 'Library', 'Application Support')
    # On Linux and as fallback
    if not (path and os.path.isdir(path)):
        path = userDir

    # Maybe we should store things local to the executable (in case of a
    # portable distro or a frozen application that wants to be portable)
    prefix = sys.prefix
    if getattr(sys, 'frozen', None): # See application_dir() function
        prefix = os.path.abspath(os.path.dirname(sys.executable))
    for reldir in ('settings', '../settings'):
        localpath = os.path.abspath(os.path.join(prefix, reldir))
        if os.path.isdir(localpath):
            try:
                open(os.path.join(localpath, 'test.write'), 'wb').close()
                os.remove(os.path.join(localpath, 'test.write'))
            except IOError:
                pass # We cannot write in this directory
            else:
                path = localpath
                break

    # Get path specific for this app
    if appname:
        if path == userDir:
            appname = '.' + appname.lstrip('.') # Make it a hidden directory
        path = os.path.join(path, appname)
        if not os.path.isdir(path):
            os.mkdir(path)

    # Done
    return path
def getResourceDirs(): # From pyzo.__init__.py
    """ getResourceDirs()
    Get the directories to the resources: (pyzoDir, appDataDir).
    Also makes sure that the appDataDir has a "tools" directory and
    a style file.
    """

    ### Always commented out.
        #     # Get root of the Pyzo code. If frozen its in a subdir of the app dir
        #     pyzoDir = paths.application_dir()
        #     if paths.is_frozen():
        #         pyzoDir = os.path.join(pyzoDir, 'source')

    ###
        # pyzoDir = os.path.abspath(os.path.dirname(__file__))
        # if '.zip' in pyzoDir:
            # raise RuntimeError('The Pyzo package cannot be run from a zipfile.')
    pyzoDir = leo_g.os_path_finalize_join(leo_g.app.loadDir, '..', 'external')

    # Get where the application data is stored (use old behavior on Mac)
    appDataDir = appdata_dir('pyzo', roaming=True, macAsLinux=True)

    ###
        # # Create tooldir if necessary
        # toolDir = os.path.join(appDataDir, 'tools')
        # if not os.path.isdir(toolDir):
            # os.mkdir(toolDir)
    return pyzoDir, appDataDir

# Compute standard places.
pyzoDir, appDataDir = getResourceDirs()

# Load all icons.
pyzo_icons = loadIcons()
