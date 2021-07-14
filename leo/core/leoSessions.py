#@+leo-ver=5-thin
#@+node:ekr.20120420054855.14241: * @file leoSessions.py
"""Support for sessions in Leo."""
#@+<< imports >>
#@+node:ekr.20120420054855.14344: ** <<imports>> (leoSessions.py)
import json
from typing import List
from leo.core import leoGlobals as g
#@-<< imports >>
#@+<< exception classes>>
#@+node:ekr.20120420054855.14357: ** <<exception classes>>
# class LeoNodeNotFoundException(Exception):
    # pass


class LeoSessionException(Exception):
    pass
#@-<< exception classes>>
#@+others
#@+node:ekr.20120420054855.14349: ** class SessionManager
# These were top-level nodes of leotools.py


class SessionManager:
    #@+others
    #@+node:ekr.20120420054855.14351: *3* SessionManager.ctor
    def __init__(self):
        self.path = self.get_session_path()
    #@+node:ekr.20120420054855.14246: *3* SessionManager.clear_session
    def clear_session(self, c):
        """Close all tabs except the presently selected tab."""
        for frame in g.app.windowList:
            if frame.c != c:
                frame.c.close()
    #@+node:ekr.20120420054855.14417: *3* SessionManager.error
    # def error (self,s):
        # # Do not use g.trace or g.es here.
        # print(s)
    #@+node:ekr.20120420054855.14245: *3* SessionManager.get_session
    def get_session(self):
        """Return a list of UNLs for open tabs."""
        result: List[str] = []
        # Fix #1118, part 2.
        if not getattr(g.app.gui, 'frameFactory', None):
            return result
        mf = getattr(g.app.gui.frameFactory, 'masterFrame', None)
        if mf:
            outlines = [mf.widget(i).leo_c for i in range(mf.count())]
        else:
            outlines = [i.c for i in g.app.windowList]
        for c in outlines:
            result.append(c.p.get_UNL(with_file=True, with_proto=False, with_index=True))
        return result
    #@+node:ekr.20120420054855.14416: *3* SessionManager.get_session_path
    def get_session_path(self):
        """Return the path to the session file."""
        for path in (g.app.homeLeoDir, g.app.homeDir):
            if g.os_path_exists(path):
                return g.os_path_finalize_join(path, 'leo.session')
        return None
    #@+node:ekr.20120420054855.14247: *3* SessionManager.load_session
    def load_session(self, c=None, unls=None):
        """Open a tab for each item in UNLs & select the indicated node in each."""
        if not unls:
            return
        unls = [z.strip() for z in unls or [] if z.strip()]
        for unl in unls:
            i = unl.find("#")
            if i > -1:
                fn, unl = unl[:i], unl[i:]
            else:
                fn, unl = unl, ''
            fn = fn.strip()
            exists = fn and g.os_path_exists(fn)
            if not exists:
                if 'startup' in g.app.debug:
                    g.trace('session file not found:', fn)
                continue
            if 'startup' in g.app.debug:
                g.trace('loading session file:', fn)
            g.app.loadManager.loadLocalFile(fn, gui=g.app.gui, old_c=c)
                # This selects the proper position.
    #@+node:ekr.20120420054855.14248: *3* SessionManager.load_snapshot
    def load_snapshot(self):
        """
        Load a snapshot of a session from the leo.session file.

        Called when --restore-session is in effect.
        """
        fn = self.path
        if fn and g.os_path_exists(fn):
            try:
                with open(fn) as f:
                    session = json.loads(f.read())
                return session
            except Exception:
                pass
        #
        # #1107: No need for this message.
            # print('can not load session: no leo.session file')
        return None
    #@+node:ekr.20120420054855.14249: *3* SessionManager.save_snapshot
    def save_snapshot(self, c=None):
        """
        Save a snapshot of the present session to the leo.session file.

        Called automatically during shutdown when no files were given on the command line.
        """
        if self.path:
            session = self.get_session()
            # print('save_snaphot: %s' % (len(session)))
            with open(self.path, 'w') as f:
                json.dump(session, f)
                f.close()
            # Do not use g.trace or g.es here.
            print(f"wrote {self.path}")
        else:
            print('can not save session: no leo.session file')
    #@-others
#@+node:ekr.20120420054855.14375: ** Commands (leoSession.py)
#@+node:ekr.20120420054855.14388: *3* session-clear
@g.command('session-clear')
def session_clear_command(event):
    """Close all tabs except the presently selected tab."""
    c = event.get('c')
    m = g.app.sessionManager
    if c and m:
        m.clear_session(c)
#@+node:ekr.20120420054855.14385: *3* session-create
@g.command('session-create')
def session_create_command(event):
    """Create a new @session node."""
    c = event.get('c')
    m = g.app.sessionManager
    if c and m:
        aList = m.get_session()
        p2 = c.p.insertAfter()
        p2.b = "\n".join(aList)
        p2.h = "@session"
        c.redraw()
#@+node:ekr.20120420054855.14387: *3* session-refresh
@g.command('session-refresh')
def session_refresh_command(event):
    """Refresh the current @session node."""
    c = event.get('c')
    m = g.app.sessionManager
    if c and m:
        aList = m.get_session()
        c.p.b = "\n".join(aList)
        c.redraw()
#@+node:ekr.20120420054855.14386: *3* session-restore
@g.command('session-restore')
def session_restore_command(event):
    """Open a tab for each item in the @session node & select the indicated node in each."""
    c = event.get('c')
    m = g.app.sessionManager
    if c and m:
        if c.p.h.startswith('@session'):
            aList = c.p.b.split("\n")
            m.load_session(c, aList)
        else:
            print('Please select an "@session" node')
#@+node:ekr.20120420054855.14390: *3* session-snapshot-load
@g.command('session-snapshot-load')
def session_snapshot_load_command(event):
    """Load a snapshot of a session from the leo.session file."""
    c = event.get('c')
    m = g.app.sessionManager
    if c and m:
        aList = m.load_snapshot()
        m.load_session(c, aList)
#@+node:ekr.20120420054855.14389: *3* session-snapshot-save
@g.command('session-snapshot-save')
def session_snapshot_save_command(event):
    """Save a snapshot of the present session to the leo.session file."""
    c = event.get('c')
    m = g.app.sessionManager
    if c and m:
        m.save_snapshot(c=c)
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
