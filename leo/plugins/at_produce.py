#@+leo-ver=5-thin
#@+node:ekr.20040915085351: * @file ../plugins/at_produce.py
#@+<< docstring >>
#@+node:ekr.20050311110307: ** << docstring >>
""" Executes commands in nodes whose body text starts with @produce.

WARNING: trying to execute a non-existent command will hang Leo.

To use, put in the body text of a node::

    @produce echo hi

This plugin creates two new commands: at-produce-all and at-produce-selected.

at-produce-all scans the entire tree for body text containing @produce.
at-produce-selected just scans the selected tree.

Whatever follows @produce is executed as a command.

@produce commands are executed in the order they are found, that is, in outline order.

The at-produce commands produce a log node as the last top-level node of the outline.
Any output, including error messages, should be there.

This plugin is not intended as a replacement for make or Ant, but as a
simple substitute when that machinery is overkill.

"""
#@-<< docstring >>

# 2014/09/21: EKR
# - Creates at-produce-all and at-produce-selected commands.
# - Adds the log node and redraws in the main thread after the separate thread completes.

import os
import subprocess
import threading
import time
from leo.core import leoGlobals as g

# Global vars.
pr = '@' + 'produce'

#@+others
#@+node:ekr.20040915085351.7: ** addMenu (no longer used)
def addMenu(tag, keywords):
    """Produce two new entries at the end of the Outlines menu."""

    c = keywords.get('c')
    if not c:
        return
    mc = c.frame.menu
    menu = mc.createNewMenu('Produce', parentName="outline", before=None)
    c.add_command(menu,
        label="Execute All Produce",
        command=lambda c=c: run(c, all=True))
    c.add_command(menu,
        label="Execute Tree Produce",
        command=lambda c=c: run(c, all=False))
#@+node:ekr.20140920173002.17965: ** at-produce commands
@g.command('at-produce-all')
def produce_all_f(event):
    c = event.get('c')
    if c:
        run(c, all=True)

@g.command('at-produce-selected')
def produce_selected_f(event):
    c = event.get('c')
    if c:
        run(c, all=False)
#@+node:ekr.20050311110629.1: ** init
def init():
    """Return True if the plugin has loaded successfully."""
    # g.registerHandler(('new','menu2'),addMenu)
    g.globalDirectiveList.append('produce')
    g.plugin_signon(__name__)
    return True
#@+node:ekr.20040915085351.5: ** run & helpers
def run(c, all):
    """
    Run all @produce nodes in a separate thread.
    Report progress via a timer in *this* thread.
    """
    aList = getList(c, all)
    g.app.at_produce_command = None
    def thread_target():
        # runList must not change Leo's outline or log!
        # runList uses c only to update c.at_produce_command.
        runList(c, aList)
    t = threading.Thread(target=thread_target)
    t.setDaemon(True)  # pylint: disable=deprecated-method
    t.start()
    timer = g.IdleTime(handler=None, delay=500, tag='at-produce')
    c._at_produce_max = 20
    c._at_produce_count = c._at_produce_max - 1
    def timer_callback(tag):
        timer_callback_helper(c, t, timer)
    timer.handler = timer_callback
    timer.start()
#@+node:ekr.20040915085351.2: *3* getList
def getList(c, all):
    """
    Return a list of all @produce lines in body texts in an outline.
    all = True:  scan c's entire outline.
    all = False: scan c.p and its descendants.
    """
    aList = []
    iter_ = c.all_positions if all else c.p.self_and_subtree
    for p in iter_():
        for line in p.b.split('\n'):
            if line.startswith(pr):
                aList.append(line)
    return aList
#@+node:ekr.20040915085351.6: *3* runList
def runList(c, aList):
    """
    Run all commands in aList (in a separate thread).
    Do not change Leo's outline in this thread!
    """
    f = open('produce.log', 'w+')
    PIPE = subprocess.PIPE
    try:
        for command in aList:
            if command.startswith(pr):
                c.at_produce_command = command
                command = command.lstrip(pr).lstrip()
                f.write('produce: %s\n' % command)
                # EKR: 2017/05/05
                # Replace popen3 per https://docs.python.org/2.4/lib/node245.html
                # fi, fo, fe  = os.popen3(command)
                p = subprocess.Popen(
                    command,
                    # bufsize=bufsize,
                    # close_fds=True, # Dubious to disable this.
                    stdin=PIPE, stdout=PIPE, stderr=PIPE,
                    shell=True,
                )
                fi, fo, fe = p.stdin, p.stdout, p.stderr
                while 1:
                    txt = g.toUnicode(fo.read())
                    f.write(txt)
                    if txt == '':
                        break
                while 1:
                    txt = g.toUnicode(fe.read())
                    f.write(txt)
                    if txt == '':
                        break
                fi.close()
                fo.close()
                fe.close()
                f.write('===============\n')
        f.seek(0)
        f.read()
    finally:
        f.close()
#@+node:ekr.20140920173002.17966: *3* timer_callback_helper
def timer_callback_helper(c, t, timer):
    """All drawing must be done in the main thread."""
    if t.isAlive():
        c._at_produce_count += 1
        if (c._at_produce_count % c._at_produce_max) == 0:
            g.es_print(c.at_produce_command)
    else:
        f = open('produce.log', 'r')
        s = f.read()
        f.close()
        os.remove('produce.log')
        last = c.rootPosition()
        while last and last.hasNext():
            last.moveToNext()
        p = last.insertAfter()
        p.h = 'produce.log from %s' % time.asctime()
        p.b = s
        c.redraw()
        timer.stop()
        g.es_print('at-produce: done')
#@-others
#@@language python
#@@tabwidth -4
#@-leo
