#@+leo-ver=5-thin
#@+node:ekr.20090717092906.12765: * @file leoVersion.py
'''A module holding version-related info.'''

# Important: this code eliminates the need for the v.bat hack.

# Leo 4.5.1 final: September 14, 2008
# Leo 4.6.1 final: July 30, 2009.
# Leo 4.7.1 final: February 26, 2010.
# Leo 4.8   final: November 26, 2010.
# Leo 4.9   final: June 21, 2011.
# Leo 4.10  final: March 29, 2012.
# Leo 4.11 a1: August 18, 2013
# Leo 4.11 a2: August 19, 2013
# Leo 4.11 b1: October 31, 2013
# Leo 4.11 final: November 6, 2013
trace = False

#@@language python
#@@tabwidth -4

#@+<< imports >>
#@+node:ekr.20120109111947.9961: ** << imports >> (leoVersion)
import os
import time

# bzr_version.py should always exist: it is part of the bzr repository.
if 0: # The bzr_version stuff just causes problems.
    try:
        import leo.core.bzr_version as bzr_version
    except ImportError:
        bzr_version = None
#@-<< imports >>

static_version = 6240
static_date = "2013-11-06"
version = "4.11 final"

use_git = True # False = bzr

theDir = os.path.dirname(__file__)

if use_git:
    path = os.path.join(theDir,'..','..','.git','HEAD')
else:
    path = os.path.join(theDir,'..','..','.bzr','branch','last-revision') 

path = os.path.normpath(path)
path = os.path.abspath(path)

# First, try to get the version from the .bzr/branch/last-revision or .git/HEAD
if os.path.exists(path):
    if trace: print('leoVersion.py: %s' % (path))
    s = open(path,'r').read()
    if not use_git:
        i = s.find(' ')
        build = static_version if i == -1 else s[:i]
    else:
        if trace: print('leoVersion.py: %s' % (s))
        if s.startswith('ref'):
            # on a proper branch
            pointer = s.split()[1]
            dirs = pointer.split('/')
            branch = dirs[-1]
            path = os.path.join(theDir, '..', '..', '.git', pointer)
            s = open(path, 'r').read().strip()[0:12] # shorten the hash to a unique shortname 
                                                 # (12 characters should be enough until the end of time, for Leo...)
            build = '%s (branch: %s)' % (s, branch)
        else:
            branch = 'None'
            build = '%s (branch: %s)' % (s, branch)
    secs = os.path.getmtime(path)
    t = time.localtime(secs)
    date = time.strftime('%Y-%m-%d %H:%M:%S',t)
# elif bzr_version:
    # # Next use bzr_version_info.
    # if trace: print('leoVersion.py: bzr_version_info',bzr_version)
    # d = bzr_version.version_info
    # build = d.get('revno','<unknown revno>')
    # date  = d.get('build_date','<unknown build date>')
else:
    # Fall back to hard-coded values.
    if trace: print('leoVersion.py: %s does not exist' % (path))
    build = static_version
    date = static_date
#@-leo
