#@+leo-ver=5-thin
#@+node:ekr.20090717092906.12765: * @file leoVersion.py
'''
A module holding the following version-related info:

leoVersion.branch:  The git branch name, or ''.
leoVersion.build:   The timestamp field from commit_timestamp.json.
leoVersion.date:    The asctime field from commit_timestamp.json.
leoVersion.version: Leo's version number, set below.

'''
import leo.core.leoGlobals as g
#@+<< version dates >>
#@+node:ekr.20141117073519.12: ** << version dates >>
#@@nocolor-node
#@+at
# Leo 4.5.1 final: September 14, 2008
# Leo 4.6.1 final: July 30, 2009.
# Leo 4.7.1 final: February 26, 2010.
# Leo 4.8   final: November 26, 2010.
# Leo 4.9   final: June 21, 2011.
# Leo 4.10  final: March 29, 2012.
# Leo 4.11 final: November 6, 2013.
# Leo 5.0 final: November 24, 2014.
# Leo 5.1 final: April 17, 2015.
# Leo 5.2 final: March 18, 2016.
# Leo 5.3 final: May 2, 2016.
# Leo 5.4 final: October 22, 2016.
# Leo 5.5 final: March 23, 2017.
# Leo 5.6 final: September 27, 2017.
# Leo 5.7b1: January 27, 2018.
# Leo 5.7b2: February 12, 2018.
# Leo 5.7 final: February 27, 2018.
#@-<< version dates >>
#@+<< about install hooks >>
#@+node:ekr.20150409201910.1: ** << about install hooks >>
#@@nocolor-node
#@+at
# 
# Developers should copy commit-msg & pre-commit from leo/extensions/hooks to
# leo-editor/.git/hooks.
# 
# These hooks cause Leo to update commit_timestamp.json automatically.
# 
# The install_hooks.py script copies these two files to leo-editor/.git/hooks.
#@-<< about install hooks >>
version = "5.7 final"
date, build = g.jsonCommitInfo()
branch = g.gitBranchName()
#@@language python
#@@tabwidth -4
#@-leo
