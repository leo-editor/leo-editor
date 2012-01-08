#@+leo-ver=5-thin
#@+node:ekr.20090717092906.12765: * @file leoVersion.py
'''A module holding version-related info.'''

# Leo 4.5.1 final: September 14, 2008
# Leo 4.6.1 final: July 30, 2009.
# Leo 4.7.1 final: February 26, 2010.
# Leo 4.8   final: November 26, 2010.
# Leo 4.9   final: June 21, 2011

#@@language python
#@@tabwidth -4

static_version = 4900
static_date = "2012-01-08"
version = "4.9.1 devel"

if 1:
    import os
    import time
    # Get the version from the .bzr/branch/last-revision.
    theDir = os.path.basename(__file__)
    path = os.path.join(theDir,'..','.bzr','branch','last-revision')
    path = os.path.normpath(path)
    path = os.path.abspath(path)
    if os.path.exists(path):
        s = open(path,'r').read()
        # print('leoVersion.py: %s: %s' % (path,s))
        secs = os.path.getmtime(path)
        t = time.localtime(secs)
        # date = time.asctime(t)
        date = time.strftime('%Y-%m-%d %H:%M:%S',t)
        i = s.find(' ')
        build = static_version if i == -1 else s[:i]
    else:
        print('leoVersion.py: %s does not exist' % (path))
        build = static_version
        date = static_date
    
else: # old code
    if 1: # Use bzr_version.py.
        import leo.core.bzr_version as bzr_version
        d = bzr_version.version_info
        build = d.get('revno','<unknown revno>')
        date  = d.get('build_date','<unknown build date>')
    else:
        build = 4669
        date = "4Q/2011"
    
#@-leo
