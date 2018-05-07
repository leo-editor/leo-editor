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
# 4.5.1:  September 14, 2008
# 4.6.1:  July 30, 2009.
# 4.7.1:  February 26, 2010.
# 4.8:    November 26, 2010.
# 4.9:    June 21, 2011.
# 4.10:   March 29, 2012.
# 4.11:   November 6, 2013.
# 5.0:    November 24, 2014.
# 5.1:    April 17, 2015.
# 5.2:    March 18, 2016.
# 5.3:    May 2, 2016.
# 5.4:    October 22, 2016.
# 5.5:    March 23, 2017.
# 5.6:    September 27, 2017.
# 5.7b1:  January 27, 2018.
# 5.7b2:  February 12, 2018.
# 5.7:    February 27, 2018.
# 5.7.1:  April 6, 2018.
# 5.7.2:  May 7, 2018.
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
version = "5.7.2"
date, build = g.jsonCommitInfo()
branch = g.gitBranchName()
#@@language python
#@@tabwidth -4
#@-leo
