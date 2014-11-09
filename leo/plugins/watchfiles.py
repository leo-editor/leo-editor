# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20141109053526.9: * @file watchfiles.py
#@@first
'''
A plugin to update Leo nodes when corresponding external files change.

This implements the following wishlit items:
    
https://bugs.launchpad.net/leo-editor/+bug/1259974
Leo should watch @ node contents for external updates

https://bugs.launchpad.net/leo-editor/+bug/1259755
Leo should keep the external editor's temp file up to date

'''
# This plugin might be moved to Leo's core.
#@+others
#@+node:ekr.20141109072407.7: ** notes 1259974: Leo should watch @ node contents for external updates
#@@nocolor-node
#@+at
# https://bugs.launchpad.net/leo-editor/+bug/1259974
# 
# Most editors provide a function where they watch a file on disk for edits
# external to that editor itself, and inform the user of them. Examples are
# gedit, geany, editra (written in python, so perhaps some code could be
# cribbed?), sublime, kate, and many others. Similar behavior may be found in
# FileZilla when using the interface it provides for editing remote files.
# 
# This could be implemented in Leo as an idle hook. The general procedure is as follows:
# 
# - When loading an @<file>, store a timestamp somewhere in Leo.
#   I imagine the caching mechanism already does this.
#   
# - When saving an @<file>, update the timestamp.
#   Again, I imagine the caching mechanism does this.
#   
# - In an idle hook, scan all loaded @<file>s on disk (not within Leo) for
#   modification times that are later than the stored modification time in
#   Leo. If the file on disk has been modified more recently than the file in
#   Leo, prompt the user if they'd like to reload the file.
# 
# This approach has many benefits:
# 
# - Reduce data loss by making it an explicit user choice: when they get the
#   prompt, they have the option of keeping Leo's loaded version (outdated)
#   or the on-disk version (newer). It should be the user's *choice* to lose
#   data, and it shouldn't be unexpected.
# 
# - Similarity with other editors makes this an expected feature. This would
#   lessen cognitive burden on users who currently have to maintain state in
#   their head and be *very* careful with external edits.
#@+node:ekr.20141109072407.8: ** notes 1259755: Leo should keep the external editor's temp file up to date
#@@nocolor-node
#@+at
# https://bugs.launchpad.net/leo-editor/+bug/1259755
# 
# Here is the tricky scenario:
# 
# 1) I edit a Leo node in Sublime; then save it without closing the temp file
#    window in Sublime. I come back to Leo and save: all changes from Sublime
#    are saved. Good so far.
# 
# 2) Now I edit the same node in Leo, which is still open in Sublime as a
#    temp file. Sublime does not know that things have changed, since Leo
#    does not update the temp file, even though Leo should know that the temp
#    file is still around. I then edit the temp file in Sublime. Now if I
#    save from Sublime, I will lose my Leo edits.
# 
# This could be remedied if Leo kept track of the state of the temp file and
# kept it up to date. Sublime does that; it will update the window with the
# newest disk version. Gedit asks: "file has changed on the disk; do you want
# to update?".
#@+node:ekr.20141109072407.5: ** Top-level
#@+node:ekr.20141109072407.4: *3* init (watchfiles.py)
def init ():
    '''Return True if the plugin has loaded successfully.'''
    ok = True
    if ok:
        g.registerHandler('start2',onStart2)
    return ok
#@+node:ekr.20141109072407.6: *3* onStart2
def onStart2(tag,**keys):
    g.trace(tag,keys)
#@-others
#@@language python
#@@tabwidth -4
#@-leo
