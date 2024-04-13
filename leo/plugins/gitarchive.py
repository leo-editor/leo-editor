#@+leo-ver=5-thin
#@+node:ekr.20110125103904.12504: * @file ../plugins/gitarchive.py
""" Store snapshots of outline in git."""

import codecs
import hashlib
import os
import shutil
from leo.core import leoGlobals as g

#@+others
#@+node:ville.20110121075405.6323: ** init
def init():
    """Return True if the plugin has loaded successfully."""
    g.plugin_signon(__name__)
    return True
#@+node:ville.20110121191106.6335: ** contfile
def contfile(c, p):
    return os.path.expanduser('~/.leo/dump/' + p.gnx)
#@+node:ville.20110121075405.6324: ** g.command('git-dump')
@g.command('git-dump')
def git_dump_f(event):
    c = event['c']
    hl = []

    def dump_nodes():
        for p in c.all_unique_positions():
            fname = contfile(c, p)
            gnx = p.gnx
            hl.append('<a href="%s">%s%s</a><br/>' % (gnx, '-' * p.level(), p.h))
            fname = gnx
            codecs.open(fname, 'w', encoding='utf-8').write(p.b)
            print("wrote", fname)

    flatroot = g.finalize('~/.leo/dump')
    if not os.path.isdir(flatroot):
        g.es("Initializing git repo at " + flatroot)
        os.makedirs(flatroot)
        os.chdir(flatroot)
        os.system('git init')
    assert os.path.isdir(flatroot)
    comment = g.app.gui.runAskOkCancelStringDialog(c, "Checkin comment", "Comment")
    if not comment:
        comment = "Leo dump"
    wb = c.config.getString(setting='default_leo_file')
    wb = g.finalize(wb)
    shutil.copy2(wb, flatroot)
    os.chdir(flatroot)
    dump_nodes()
    lis = "\n".join(hl)
    html = "<body>\n<tt>\n" + lis + "\n</tt></body>"
    pth, bname = os.path.split(c.mFileName)
    if pth and bname:
        dbdirname = bname + "_" + hashlib.md5(c.mFileName).hexdigest()
    titlename = dbdirname + '.html'
    codecs.open(titlename, 'w', encoding='utf-8').write(html)
    g.es("committing to " + flatroot)
    os.system('git add *')
    out = os.popen('git commit -m "%s"' % comment).read()
    g.es("committed")
    g.es(out)
    g.es('Outline in ' + os.path.abspath(titlename))
#@+node:ville.20110121191854.6337: ** g.command('git-log')
@g.command('git-log')
def git_log_f(event):
    c = event['c']
    p = c.p
    # os.chdir ??
    inf = contfile(c, p)
    print("f", inf)
    os.system("gitk %s" % inf)
#@-others
#@@language python
#@@tabwidth -4
#@-leo
