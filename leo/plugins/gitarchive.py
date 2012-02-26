#@+leo-ver=5-thin
#@+node:ekr.20110125103904.12504: * @file gitarchive.py
#@+<< docstring >>
#@+node:ville.20110121075405.6320: ** << docstring >>
''' Store snapshots of outline in git


'''
#@-<< docstring >>

__version__ = '0.0'
#@+<< version history >>
#@+node:ville.20110121075405.6321: ** << version history >>
#@@killcolor
#@+at
# 
# Put notes about each version here.
#@-<< version history >>

#@+<< imports >>
#@+node:ville.20110121075405.6322: ** << imports >>
import leo.core.leoGlobals as g

#@-<< imports >>

#@+others
#@+node:ville.20110121075405.6323: ** init
def init ():
    ok = True

    if ok:
        g.plugin_signon(__name__)

    return ok
#@+node:ville.20110121191106.6335: ** contfile
def contfile(c, p):
    fn = os.path.expanduser('~/.leo/dump/' + p.gnx)

    return fn
#@+node:ville.20110121075405.6324: ** g.command('git-dump')
import os, codecs, hashlib, shutil

@g.command('git-dump')
def git_dump_f(event):
    c = event['c']
    hl = []

    def dump_nodes():
        for p in c.all_unique_positions():
            #name, date, num = p.v.fileIndex
            fname = contfile(c,p)
            #gnx = '%s%s%s' % (name, date, num)
            gnx = p.gnx
            hl.append('<a href="%s">%s%s</a><br/>' % (gnx, '-' * p.level(), p.h))
            fname = gnx
            codecs.open(fname,'w', encoding='utf-8').write(p.b)
            print("wrote",fname)

    flatroot = g.os_path_finalize('~/.leo/dump')
    if not os.path.isdir(flatroot):
        g.es("Initializing git repo at " + flatroot)
        os.makedirs(flatroot)
        os.chdir(flatroot)
        os.system('git init')

    assert os.path.isdir(flatroot)

    comment = g.app.gui.runAskOkCancelStringDialog(c,"Checkin comment","Comment")
    if not comment:
        comment = "Leo dump"
    wb = c.config.getString(setting='default_leo_file')
    wb = g.os_path_finalize(wb)
    shutil.copy2(wb, flatroot)
    
    os.chdir(flatroot)

    dump_nodes()
    lis = "\n".join(hl)

    html = "<body>\n<tt>\n" + lis + "\n</tt></body>"

    #titlename = c.frame.getTitle() + '.html'
    pth, bname = os.path.split(c.mFileName)
    
    

    if pth and bname:
        dbdirname = bname + "_" + hashlib.md5(c.mFileName).hexdigest()    

    titlename = dbdirname + '.html'
    codecs.open(titlename,'w', encoding='utf-8').write(html)

    g.es("committing to " + flatroot)

    os.system('git add *')
    out = os.popen('git commit -m "%s"' % comment).read()
    g.es("committed")
    g.es(out)
    g.es('Outline in ' + os.path.abspath(titlename))
#@+node:ville.20110121191854.6337: ** g.command('git-log')
import os, codecs, hashlib

@g.command('git-log')
def git_log_f(event):
    c = event['c']
    p = c.p
    os.chdir

    inf = contfile(c,p)
    print("f", inf)
    os.system("gitk %s" % inf)
#@-others
#@-leo
