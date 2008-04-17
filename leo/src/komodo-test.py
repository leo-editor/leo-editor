# Most imports happen after addKomodoPaths has been defined.
import os
import sys

baseKomodoDir = r'C:\Program Files\Komodo Edit 4.3\lib\mozilla\python'

def addKomodoPaths ():

    '''Add paths to sys.path so Komodo imports will work.'''
    paths = (
        r'komodo', # For ciElementree.pyd
        r'komodo\codeintel2',
        r'komodo\codeintel2\catalogs',
        r'komodo\codeintel2\database',
        r'komodo\codeintel2\stdlibs',
        # r'C:\Python25\Lib\site-packages\SilverCity',
        r'komodo\SilverCity',
    )

    trace = False

    if trace: print 'sys.path...'
    for path in paths:
        path = os.path.join(baseKomodoDir,path)
        if os.path.exists(path):
            if path in sys.path:
                if trace: print('in sys.path',path)
            else:
                if trace: print('added',path)
                sys.path.append(path)
        else:
            print('Does not exist: %s' % path)

# Don't change the order of these imports.
addKomodoPaths()

import logging
from codeintel2.indexer import BatchUpdater
from codeintel2.manager import Manager
from codeintel2.common import EvalController

def doLog():

    log_level = logging.ERROR
        # DEBUG, INFO, WARN, ERROR, NOTSET

    log = logging.getLogger('codeintel')

    rootLogger = logging.getLogger('')
    rootLogger.setLevel(log_level)

    if not log.handlers:

        # Create handler for codeintel logger.
        formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
        console = logging.StreamHandler()
        console.setLevel(log_level)
        console.setFormatter(formatter)
        log.addHandler(console)

    if 0:
        log.debug('debug msg.')
        log.info('info msg.')
        log.warning('warning msg.')
        log.error('error msg.')

prev_trigger = None

def doTrigger (s,i,trigger,buf,ctlr):

    # See also Buffer.async_eval_at_trg()
    print 'trigger at %3d' % (i),'%33s' % (
        trigger.name),'%9s' % (repr(s[i: i+5])),

    completions = buf.cplns_from_trg(trigger,timeout=None,ctlr=ctlr)
    print 'completions %3s' % (completions and len(completions) or 0),

    calltips = buf.calltips_from_trg(trigger,timeout=None,ctlr=ctlr)
    print 'calltips %s' % (calltips and len(calltips) or 0),

    if completions:
        modules = [b for (a,b) in completions if a == 'module']
        print 'modules',len(modules),

        directories = [b for (a,b) in completions if a == 'directory']
        print 'directories',len(directories)

    if 0: # print all modules and directories.
        global prev_trigger
        if prev_trigger is None:
            prev_trigger = trigger
            print '\n***** %s modules...' % len(modules)
            for z in modules: print z
            print '\n***** %s directories...' % len(directories)
            for z in directories: print z

def main ():

    doLog()

    mgr = Manager(on_scan_complete=scanComplete)
    mgr.upgrade() # Can use mgr.db.upgrade methods for finer control.
    mgr.initialize()

    try:
        scan(mgr)
    finally:
        mgr.finalize()
        print 'done'

# From example code in codeintel2.__init__.py

def scan(mgr):

    trace = True
    # path = os.path.normpath(os.path.join(os.curdir,'..','test','komodo-test-data.py'))
    path = 'komodo-test-data.py'

    buf = mgr.buf_from_path(path) # Can also get Buffer from content.
        # Buf is a PythonBuffer (see lang_python), a subclass of CitadelBuffer: see citadel.py
    buf.scan()
    buf.load()

    ctlr = EvalController() # Use a common controller.
    ### tree = buf.tree # A property: scans if necessary.

    # Print the data.
    s = file(path).read()
    if trace:
        print '%s...' % path
        print '\n%s\n' % s
        print ; print 'end %s' % path ; print

    # Find all trigger points.
    for i in xrange(1,len(s)):
        trigger = buf.trg_from_pos(i,implicit=False)
        if trigger:
            doTrigger(s,i,trigger,buf,ctlr)

def scanComplete(request):
    '''An event handler, called by the mgr when the scan is complete.'''
    print ('scanComplete','*'*10,request)

if __name__ == '__main__':
    print '=' * 40
    main()
    print '-' * 40
