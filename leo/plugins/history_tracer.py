#@+leo-ver=5-thin
#@+node:vitalije.20190928154420.1: * @file ../plugins/history_tracer.py
#@+<< docstring >>
#@+node:vitalije.20190928154420.2: ** << docstring >>
"""This plugin cooperates with leo-ver-serv utilty.

   To install leo-ver-serv visit https://crates.io/crates/leo-ver-serv
   
   In idle time, whenever user has no activity in last 5 seconds,
   this plugin will send the snapshot of Leo outline to the local
   leo-ver-serv server and it will record snapshot in sqlite3 database
   named after the Leo file by adding '.history' to file name. For example
   if you edit file /tmp/a.leo, history will be recorded in the file
   /tmp/a.leo.history.
   
   leo-ver-serv will also serve a small web application for displaying
   outline and allows user to browse all recorded versions of the file.
   
   leo-ver-serv requires as its first argument a filename of a file
   containing absolute paths to the Leo files that are tracked. A
   suitable value for this argument is ~/.leo/.leoRecentFiles.txt
   
   The second argument for leo-ver-serv is a port number. The same port
   number must be in your settings.

   @int history-tracer-port=8087
   
   Author: vitalije(at)kviziracija.net
"""

#@-<< docstring >>
#@+<< imports >>
#@+node:vitalije.20190928154420.3: ** << imports >>
import datetime
import time
import threading
from urllib.request import urlopen
from urllib.error import URLError
from leo.core import leoGlobals as g
from leo.core.leoQt import QtCore
#
# Fail fast, right after all imports.
g.assertUi('qt')  # May raise g.UiTypeException, caught by the plugins manager.
#@-<< imports >>
#@afterref
 # history_tracer.py

idle_checker = None

#@+others
#@+node:vitalije.20190928154420.4: ** init
def init():
    '''Return True if the plugin has loaded successfully.'''
    ok = g.app.gui.guiName() == "qt"
    if ok:
        g.registerHandler(['command1', 'command2'], c12_hook)
        g.registerHandler('start2', init_idle_checker)
        g.plugin_signon(__name__)
    return ok
#@+node:vitalije.20190928154420.6: ** c12_hook
def c12_hook(tag, keys):
    c = keys.get('c')
    c.user_dict['last_command_at'] = time.time()
#@+node:vitalije.20190928160510.1: ** IdleChecker
def init_idle_checker(tag, keys):
    global idle_checker
    class IdleChecker(QtCore.QObject):
        def __init__(self):
            QtCore.QObject.__init__(self)
            self._tid = self.startTimer(5000)

        def stop(self):
            self.killTimer(self._tid)

        def timerEvent(self, ev):
            t = time.time()
            for i, cx in enumerate(g.app.commanders()):
                t1 = cx.user_dict.get('last_command_at', t)
                t2 = cx.user_dict.get('last_snap_at', 0)
                if t - t1 > 5 and t1 > t2:
                    cx.user_dict['last_snap_at'] = t
                    if save_snapshot(cx):
                        g.es('snap', i, cx.mFileName.rpartition('/')[2])

    print("don't forget to launch leo-ver-serv!!!")
    idle_checker = IdleChecker()
#@+node:vitalije.20190928160520.1: ** save_snapshot
def save_snapshot(c):
    data = snap(c)
    x = data.split('\n', 2)[2]
    y = c.user_dict.get('last_snapshot_data')
    if x == y:return False
    c.user_dict['last_snapshot_data'] = x
    def pf():
        t1 = time.perf_counter()
        url = 'http://localhost:%d/add-snapshot'%c.config.getInt('history-tracer-port')
        with urlopen(url, data=data.encode('utf8')) as resp:
            try:
                txt = resp.read().decode('utf8')
            except URLError as e:
                if 'refused' in str(e):
                    g.es('it seems that leo-ver-serv is not running', color='warning')
            if txt == 'Unkown file':
                g.es(c.mFileName, 'is not tracked by history_tracer plugin\n'
                    'You have to restart leo-ver-serv to accept new files',
                    color='warning')
        ms = '%.2fms'%(1000 * (time.perf_counter() - t1))
        print("save_snapshot:", data.partition('\n')[0], txt, 'in', ms)
    threading.Thread(target=pf, name="snapshot-saver").start()
    return True
#@+node:vitalije.20190928160538.1: ** snap
def snap(c):
    dt = datetime.datetime.utcnow()
    buf = [c.mFileName, '\n', dt.strftime('%Y-%m-%dT%H:%M:%S.000000'), '\n']
    nbuf = {}
    def it(v, lev):
        if v.gnx not in nbuf:
            s = '%s\n%s'%(v.gnx,v.b)
            n = len(s.encode('utf8'))
            nbuf[v.gnx] = '%d %s'%(n, s)
        yield v, lev
        for ch in v.children:
            yield from it(ch, lev+1)
    for v, lev in it(c.hiddenRootNode, 0):
        buf.append('%d %s %s\n'%(lev, v.fileIndex, v._headString))
    buf.append('\n')
    for gnx, hb in nbuf.items():
        buf.append(hb)
    return ''.join(buf)
#@-others
#@@language python
#@@tabwidth -4
#@-leo
