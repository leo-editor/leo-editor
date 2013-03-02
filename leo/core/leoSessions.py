#@+leo-ver=5-thin
#@+node:ekr.20120420054855.14241: * @file leoSessions.py
#@@language python
#@@tabwidth -4

#@+<< imports >>
#@+node:ekr.20120420054855.14344: ** <<imports>> (leoSessions.py)
import leo.core.leoGlobals as g

#import config
#import dnode
import json
# import os
# import sys
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
    #@+node:ekr.20120420054855.14351: *3*  ctor (LeoSessionController)
    def __init__ (self):

        self.path = self.get_session_path()
    #@+node:ekr.20120420054855.14246: *3* clear_session
    def clear_session(self,c):

        '''Close all tabs except the presently selected tab.'''

        for frame in g.app.windowList:
            if frame.c != c:
                frame.c.close()
    #@+node:ekr.20120420054855.14417: *3* error
    # def error (self,s):

        # # Do not use g.trace or g.es here.
        # print(s)
    #@+node:ekr.20120420054855.14245: *3* get_session
    def get_session(self):

        '''Return a list of UNLs for open tabs.'''

        result = []
        for frame in g.app.windowList:
            result.append(frame.c.p.get_UNL())
        return result
    #@+node:ekr.20120420054855.14416: *3* get_session_path
    def get_session_path (self):

        '''Return the path to the session file.'''

        for path in (g.app.homeLeoDir,g.app.homeDir):
            if g.os_path_exists(path):
                return g.os_path_finalize_join(path,'leo.session')

        return None
    #@+node:ekr.20120420054855.14247: *3* load_session
    def load_session(self,c=None,unls=None):

        '''Open a tab for each item in UNLs & select the indicated node in each.'''

        if unls is None: unls = []

        for unl in unls:
            if unl.strip():
                fn,unl = unl.split("#")
                if g.os_path_exists(fn):
                    # g.trace(fn)
                    c2 = g.app.loadManager.loadLocalFile(fn,gui=g.app.gui,old_c=c)
                    for p in c2.all_positions():
                        if p.get_UNL() == unl:
                            c2.setCurrentPosition(p)
                            c2.redraw()
                            break
    #@+node:ekr.20120420054855.14248: *3* load_snapshot
    def load_snapshot(self):

        '''Load a snapshot of a session from the leo.session file.'''

        fn = self.path

        if fn and g.os_path_exists(fn):
            with open(fn) as f:
                session = json.loads(f.read())
            return session
        else:
            print('can not load session: no leo.session file')  
            return None
    #@+node:ekr.20120420054855.14249: *3* save_snapshot
    def save_snapshot(self,c=None):

        '''Save a snapshot of the present session to the leo.session file.'''

        if self.path:
            session = self.get_session()
            # print('save_snaphot: %s' % (len(session)))
            with open(self.path,'w') as f:
                json.dump(session,f)
                f.close()
            # Do not use g.trace or g.es here.
            print('wrote %s' % (self.path))
        else:
            print('can not save session: no leo.session file')  
    #@-others
#@+node:ekr.20120420054855.14375: ** Commands
#@+node:ekr.20120420054855.14388: *3* session-clear
@g.command('session-clear')
def session_clear_command(event):

    c = event.get('c')
    m = g.app.sessionManager
    if c and m:
        m.clear_session(c)
#@+node:ekr.20120420054855.14385: *3* session-create
@g.command('session-create')
def session_create_command(event):

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

    c = event.get('c')
    m = g.app.sessionManager
    if c and m:
        aList = m.get_session()
        c.p.b = "\n".join(aList)
        c.redraw()
#@+node:ekr.20120420054855.14386: *3* session-restore
@g.command('session-restore')
def session_restore_command(event):

    c = event.get('c')
    m = g.app.sessionManager
    if c and m:
        if c.p.h.startswith('@session'):
            aList = c.p.b.split("\n")
            m.load_session(c,aList)
        else:
            print('Please select an "@session" node')
#@+node:ekr.20120420054855.14390: *3* session-snapshot-load
@g.command('session-snapshot-load')
def session_snapshot_load_command(event):

    c = event.get('c')
    m = g.app.sessionManager
    if c and m:
        aList = m.load_snapshot()
        m.load_session(c,aList)
#@+node:ekr.20120420054855.14389: *3* session-snapshot-save
@g.command('session-snapshot-save')
def session_snapshot_save_command(event):

    c = event.get('c')
    m = g.app.sessionManager
    if c and m:
        m.save_snapshot(c=c)
#@-others
#@-leo
