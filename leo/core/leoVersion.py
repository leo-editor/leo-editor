#@+leo-ver=5-thin
#@+node:ekr.20090717092906.12765: * @file leoVersion.py
'''A module holding version-related info.'''
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
#@-<< version dates >>
import leo.core.leoGlobals as g
static_date = 'October 15, 2016' # Used only if no dynamic version.
version = "5.4-b1" # Always used.
#@+others
#@+node:ekr.20161016063005.1: ** git_version_from_git
def get_version_from_git():
    trace = False
    import shlex
    import re
    import subprocess
    import sys
    try:
        is_windows = sys.platform.startswith('win')
        p = subprocess.Popen(
            shlex.split('git log -1 --date=default-local'),
            stdout=subprocess.PIPE,
            stderr=None if trace else subprocess.DEVNULL,
            shell=is_windows,
        )
        out, err = p.communicate()
        out = g.toUnicode(out)
        if trace: g.trace(out)
        m = re.search('commit (.*)\n', out)
        commit = m.group(1).strip()[:8] if m else ''
        m = re.search('Date: (.*)\n', out)
        date = m.group(1).strip() if m else ''
        if trace: g.trace(commit, date)
        return commit, date
    except Exception:
        # We are using an official release.
        # g.es_exception()
        return None, None
#@+node:ekr.20161016063719.1: ** get_version_from_json
def get_version_from_json():
    '''
    Return version info parsed from leo/core/commit_timestamp.json.
    
    This suffers from two *serious* problems:
    1. The dates don't get updated if the developer (me)
       forgets to install the git hooks.
    2. Always committing commit_timestamp.json creates merge conflicts.
    '''
    trace = False
    import os
    import json
    date = None
    try:
        leo_core_path = os.path.dirname(os.path.realpath(__file__))
            # leoVersion.py is in leo/core
        commit_path = os.path.join(leo_core_path, 'commit_timestamp.json')
        commit_info = json.load(open(commit_path))
        if trace:
            print('commit_path: %s' % commit_path)
            print('commit_info: %s' % commit_info)
        # build = commit_info['timestamp']
        date = commit_info['asctime']
    except Exception:
        print('Warning: leo/core/commit_timestamp.json does not exist')
    # attempt to grab commit + branch info from git, else ignore it
    theDir = os.path.dirname(__file__)
    path = os.path.join(theDir, '..', '..', '.git', 'HEAD')
    if trace: print('leoVersion.py: %s exists: %s' % (path, os.path.exists(path)))
    if os.path.exists(path):
        s = open(path, 'r').read()
        if s.startswith('ref'):
            # on a proper branch
            pointer = s.split()[1]
            path = os.path.join(theDir, '..', '..', '.git', pointer)
            try:
                s = open(path, 'r').read().strip()[0: 12]
            except Exception:
                s = s[0: 12]
        else:
            s = s[0: 12]
    else:
        s = None
    commit = s
    return commit, date
#@-others
if 1:
    # No install hooks needed!
    commit, date = get_version_from_git()
else:
    #@+<< about install hooks >>
    #@+node:ekr.20150409201910.1: ** << about install hooks >>
    #@@nocolor-node
    #@+at
    # 
    # Developers should copy commit-msg & pre-commit from leo/extentions/hooks to
    # leo-editor/.git/hooks.
    # 
    # These hooks cause Leo to update commit_timestamp.json automatically.
    # 
    # The install_hooks.py script copies these two files to leo-editor/.git/hooks.
    #@-<< about install hooks >>
    commit, date = get_version_from_json()
if not date:
    date = static_date
#@@language python
#@@tabwidth -4
#@-leo
