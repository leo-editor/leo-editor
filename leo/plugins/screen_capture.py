#@+leo-ver=5-thin
#@+node:tbrown.20130420091241.44181: * @file ../plugins/screen_capture.py
#@+<< docstring >>
#@+node:ekr.20140910173844.17823: ** << docstring >> (screen_capture.py)
"""
screen_capture.py
=================

Capture screen shots - single frames are useful.  The
`Recorder` class can also capture frames continuously but that's not
really useful, it doesn't handle audio or video encoding, and can't maintain
a 30 fps frame rate.  The code for doing so is not hooked up in this plugin.

Screen captures are saved in ``~/.leo/screen_captures`` with
timestamps in the filenames.

Commands
--------

``screen-capture-5sec``
  Wait five seconds, then take a screen shot.
``screen-capture-now``
  Take a screen shot.

Settings
--------

``@string screen-capture-save-path``
  Save screen shots here instead of ~/.leo/screen_captures

Terry Brown, Terry_N_Brown@yahoo.com, Fri Apr 19 16:33:45 2013
"""
#@-<< docstring >>
import os
import time
from leo.core import leoGlobals as g
from leo.core.leoQt import QtCore, QtGui
#
# Fail fast, right after all imports.
g.assertUi('qt')  # May raise g.UiTypeException, caught by the plugins manager.
#@+others
#@+node:tbrown.20130419143128.29676: ** init
def init():
    """Return True if the plugin has loaded successfully."""
    if g.unitTesting:
        return False
    ok = g.app.gui.guiName() == 'qt'
    g.plugin_signon(__name__)
    return ok
#@+node:tbrown.20130419143128.29669: ** class Recorder
class Recorder:
    """Recorder - record video of Leo

    These shell commands convert saved frames to video

    ls /tmp/image*.ppm |
        xargs -IFILE -n1 -P4 mogrify -format png FILE
    mencoder mf:///tmp/image*.png -mf
        fps=12:type=png -ovc lavc -lavcopts
        vcodec=mpeg4:mbd=2:trell -oac copy -o output.avi
    rm -k /tmp/image*.ppm /tmp/image*.png
    """
    #@+others
    #@+node:tbrown.20130419143128.29670: *3* __init__
    def __init__(self):
        """Ctor for Recorder class."""
        self.recording = False
        self.frame = 0
        self.pointer_pmap = self.make_pointer()
        self.pointer_img = self.pointer_pmap.toImage()
        self.last_time: float = 0.0
        c = g.app.commanders()[0]
        w = c.frame.body.wrapper.widget
        while w.parent():
            w = w.parent()
        self.widget = w
        self.winId = w.winId()
        # re-enable this to restore video function
            # self.timer = QtCore.QTimer()
            # self.timer.setInterval(25)
            # self.timer.timeout.connect(self.grab_frame)
        # performance testing
        self.times = []

    #@+node:tbrown.20130419143128.29671: *3* grab_frame
    def grab_frame(self, filename=None):
        """Grab one frame."""
        if not self.recording and not filename:
            return
        screen = g.app.gui.qtApp.primaryScreen()
        pm = screen.grabWindow(self.winId)
        if False:
            # don't remove this code - all during dev. the above did
            # not capture the pointer in the image, which is quite
            # typical for screen captures - this code draws a pointer
            # in the right place, and may be need to be enabled by a
            #@verbatim
            # @setting in future, if pointer capture does not occur in
            # all environments - pointer is captured in
            # Leo Log Window
            # Leo 4.11 devel, build 5727, 2013-04-19 10:16:15
            # Python 2.7.4, qt version 4.8.4
            # linux2
            # Xubuntu Xfce4 desktop
            cursor = self.widget.cursor()
            pos = self.widget.mapFromGlobal(cursor.pos())
            painter = QtGui.QPainter()
            painter.begin(pm)
            painter.drawImage(
                pos,
                self.pointer_img,
            )
            painter.end()

        if not filename:
            filename = "/tmp/image%04d.bmp" % self.frame
            # save .bmp in video mode because .png is too slow

        pm.save(filename)
        self.frame += 1
    #@+node:tbrown.20130419143128.29672: *3* make_pointer
    def make_pointer(self):
        """Return a pixmap for a pointer."""
        path = g.computeLeoDir()
        path = g.os_path_join(path, 'Icons', 'recorder', 'pointer.png')
        return QtGui.QPixmap(path)
    #@+node:tbrown.20130419143128.29673: *3* run
    def run(self):
        """Start recording."""
        self.recording = True
        self.last_time = time.time()
        # self.timer.start()
    #@+node:tbrown.20130419143128.29674: *3* stop
    def stop(self):
        """Stop recording"""
        # self.timer.stop()
        mean = sum(self.times) / float(len(self.times))
        print("\nMean seconds: %0.3f = %0.3f fps" % (mean, 1. / mean))
        self.times = []
    #@-others

#@+node:tbrown.20130419143128.29677: ** screen_capture_now
@g.command('screen-capture-now')
def screen_capture_now(kwargs=None):
    """screen_capture_now - save a screenshot

    :Parameters:
    - `kwargs`: g.command arguments
    """
    if kwargs is None:
        kwargs = {}
    if not hasattr(g, '_recorder'):
        g._recorder = Recorder()
    c = g.app.commanders()[0]
    dirname = c.config.getString("screen-capture-save-path")
    if not dirname:
        dirname = g.os_path_join(
            g.computeHomeDir(),
            '.leo',
            'screen_captures'
        )
    dirname = g.finalize(dirname)
    if not g.os_path_isdir(dirname):
        os.makedirs(dirname)
    filename = g.os_path_join(
        dirname,
        time.strftime('%Y-%m-%dT%H-%M-%S') + '.png'
    )
    g._recorder.grab_frame(filename=filename)
    # *only* print, don't want output messing up log view in screen shots
    print("Screenshot: %s" % filename)
#@+node:tbrown.20130419143128.29679: ** screen_capture_5sec
@g.command('screen-capture-5sec')
def screen_capture_5sec(kwargs):
    """screen_capture_5sec - save a screenshot in 5 seconds

    :Parameters:
    - `kwargs`: g.command arguments
    """

    QtCore.QTimer.singleShot(5000, screen_capture_now)
#@-others
#@@language python
#@@tabwidth -4

#@-leo
