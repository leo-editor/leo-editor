#@+leo-ver=5-thin
#@+node:ekr.20120420054855.14241: * @file leoSessions.py
"""Support for sessions in Leo."""
from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from leo.core import leoGlobals as g

if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoGui import LeoKeyEvent as Event

#@+others
#@+node:ekr.20120420054855.14349: ** class SessionManager
class SessionManager:
    """A class managing session data and related commands."""
    #@+others
    #@+node:ekr.20120420054855.14246: *3* SessionManager.clear_session
    def clear_session(self, c: Cmdr) -> None:
        """Close all tabs except the presently selected tab."""
        for frame in g.app.windowList:
            if frame.c != c:
                frame.c.close()
    #@+node:ekr.20120420054855.14417: *3* SessionManager.error
    # def error (self,s):
        # # Do not use g.trace or g.es here.
        # print(s)
    #@+node:ekr.20120420054855.14245: *3* SessionManager.get_session
    def get_session(self) -> list[str]:
        """Return a list of UNLs for open tabs."""
        result: list[str] = []
        # Fix #1118, part 2.
        if not getattr(g.app.gui, 'frameFactory', None):
            return result
        mf = getattr(g.app.gui.frameFactory, 'masterFrame', None)
        if mf:
            outlines = [mf.widget(i).leo_c for i in range(mf.count())]
        else:
            outlines = [i.c for i in g.app.windowList]
        for c in outlines:
            result.append(c.p.get_full_gnx_UNL())
        return result
    #@+node:ekr.20120420054855.14416: *3* SessionManager.get_session_path
    def get_session_path(self) -> Optional[str]:
        """Return the path to the session file."""
        for path in (g.app.homeLeoDir, g.app.homeDir):
            if g.os_path_exists(path):
                return g.finalize_join(path, 'leo.session')
        return None
    #@+node:ekr.20120420054855.14247: *3* SessionManager.load_session
    def load_session(self, c: Cmdr = None, unls: list[str] = None) -> None:
        """
        Open a tab for each item in UNLs & select the indicated node in each.

        unls is the list returned by SessionManager.load_snapshot()
        """
        if not unls:
            return
        unls = [z.strip() for z in unls or [] if z.strip()]
        for unl in unls:
            if not g.isValidUnl(unl):
                g.trace(f"Ignoring invalid session {'unl'}: {unl!r}")
                continue
            fn = g.getUNLFilePart(unl)
            exists = fn and g.os_path_exists(fn)
            if not exists:
                g.trace('File part does not exist', repr(fn))
                g.trace(f"Bad unl: {unl!r}")
                continue
            if 'startup' in g.app.debug:
                g.trace('loading session file:', fn)
            # This selects the proper position.
            g.app.loadManager.loadLocalFile(fn, gui=g.app.gui, old_c=c)
    #@+node:ekr.20120420054855.14248: *3* SessionManager.load_snapshot
    def load_snapshot(self) -> str:
        """
        Load a snapshot of a session from the leo.session file.
        """
        try:
            session = g.app.db['session']
            if 'startup' in g.app.debug:
                g.printObj(session, tag='load_snapshot: session data')
            return session
        except KeyError:
            print('SessionManager.load_snapshot: no previous session')
        except Exception:
            g.trace('Unexpected exception in SessionManager.load_snapshot')
            g.es_exception()
        return None
    #@+node:ekr.20120420054855.14249: *3* SessionManager.save_snapshot
    def save_snapshot(self) -> None:
        """
        Save a snapshot of the present session to the leo.session file.

        Called automatically during shutdown.
        """
        if g.app.batchMode or g.app.inBridge or g.unitTesting:
            return
        try:
            session = self.get_session()
            if 'shutdown' in g.app.debug:
                g.printObj(session, tag='save_snapshot: session data')
            if not session:
                return  # #2433: don't save an empty session.
            g.app.db['session'] = session
        except Exception:
            g.trace('Unexpected exception in SessionManager.save_snapshot')
            g.es_exception()
    #@-others
#@+node:ekr.20120420054855.14375: ** Commands (leoSession.py)
#@+node:ekr.20120420054855.14388: *3* session-clear
@g.command('session-clear')
def session_clear_command(event: Event) -> None:
    """Close all tabs except the presently selected tab."""
    c = event.get('c')
    m = g.app.sessionManager
    if c and m:
        m.clear_session(c)
#@+node:ekr.20120420054855.14385: *3* session-create
@g.command('session-create')
def session_create_command(event: Event) -> None:
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
def session_refresh_command(event: Event) -> None:
    """Refresh the current @session node."""
    c = event.get('c')
    m = g.app.sessionManager
    if c and m:
        aList = m.get_session()
        c.p.b = "\n".join(aList)
        c.redraw()
#@+node:ekr.20120420054855.14386: *3* session-restore
@g.command('session-restore')
def session_restore_command(event: Event) -> None:
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
def session_snapshot_load_command(event: Event) -> None:
    """Load a snapshot of a session from the leo.session file."""
    c = event.get('c')
    m = g.app.sessionManager
    if c and m:
        aList = m.load_snapshot()
        m.load_session(c, aList)
#@+node:ekr.20120420054855.14389: *3* session-snapshot-save
@g.command('session-snapshot-save')
def session_snapshot_save_command(event: Event) -> None:
    """Save a snapshot of the present session to the leo.session file."""
    m = g.app.sessionManager
    if m:
        m.save_snapshot()
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
