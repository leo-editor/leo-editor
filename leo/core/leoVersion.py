#@+leo-ver=5-thin
#@+node:ekr.20090717092906.12765: * @file leoVersion.py
'''A module holding version-related info.'''

# Leo 4.5.1 final: September 14, 2008
# Leo 4.6.1 final: July 30, 2009.
# Leo 4.7.1 final: February 26, 2010.
# Leo 4.8   final: November 26, 2010.

#@@language python
#@@tabwidth -4

build = 4248
date = "June 3, 2011"
version = "4.9 beta 1"

#@+at The following bzr command reports the buil automatically
#     
#     bzr version-info --custom --template="build={revno}\ndate={date}\n"
#     
# The output is::
#     
#     build=4248
#     date=2011-06-03 09:18:47 -0500
#@-leo
