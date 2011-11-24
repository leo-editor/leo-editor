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

if 1: # Use bzr_version.py.
    import leo.core.bzr_version as bzr_version
    d = bzr_version.version_info
    build = d.get('revno','<unknown revno>')
    date  = d.get('build_date','<unknown build date>')
else:
    build = 4669
    date = "4Q/2011"

version = "4.9.1 devel"

#@+at The following bzr command reports the build automatically.
#@-leo
