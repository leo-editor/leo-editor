#@+leo-ver=5-thin
#@+node:ekr.20090717092906.12765: * @file leoVersion.py
'''A module holding version-related info.'''
trace = False
import os
import json
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
#@-<< version dates >>
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
# get info from leo/core/commit_timestamp.json
try:
    leo_core_path = os.path.dirname(os.path.realpath(__file__))
        # leoVersion.py is in leo/core
    commit_path = os.path.join(leo_core_path, 'commit_timestamp.json')
    commit_info = json.load(open(commit_path))
    if trace:
        print('commit_path: %s' % commit_path)
        print('commit_info: %s' % commit_info)
    commit_timestamp = commit_info['timestamp']
    commit_asctime = commit_info['asctime']
except Exception:
    # Continue if commit_timestamp.json does not exist.
    print('Warning: leo/core/commit_timestamp.json does not exist')
    commit_timestamp = ''
    commit_asctime = ''
version = "5.5" # Always used.
# attempt to grab commit + branch info from git, else ignore it
git_info = {}
theDir = os.path.dirname(__file__)
git_dir = os.path.join(theDir, '..', '..', '.git')
path = os.path.join(git_dir, 'HEAD')
if trace: print('leoVersion.py: %s exists: %s' % (path, os.path.exists(path)))
try:
    if os.path.exists(path):
        s = open(path, 'r').read()
        if s.startswith('ref'):
            # on a proper branch
            pointer = s.split()[1]
            dirs = pointer.split('/')
            branch = dirs[-1]
            path = os.path.join(git_dir, pointer)
            try:
                s = open(path, 'r').read().strip()[0: 12]
                # shorten the hash to a unique shortname
            except IOError:
                try:
                    path = os.path.join(git_dir, 'packed-refs')
                    for line in open(path):
                        if line.strip().endswith(' '+pointer):
                            s = line.split()[0][0: 12]
                            break
                except IOError:
                    branch = 'None'
                    s = s[0: 12]
        else:
            branch = 'None'
            s = s[0: 12]
        git_info['branch'] = branch
        git_info['commit'] = s
except Exception as e:
    # don't crash Leo, this info. not essential
    print(e)
build = commit_timestamp
date = commit_asctime
#@@language python
#@@tabwidth -4
#@-leo
