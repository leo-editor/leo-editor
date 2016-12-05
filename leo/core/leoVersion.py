#@+leo-ver=5-thin
#@+node:tbrown.20161128214642.2: * @file leoVersion.py
'''
A module for computing version-related info.

Leo's core uses leoVersion.commit, leoVersion.date and leoVersion.version.
'''
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
# Leo 5.4b1: October 17, 2016.
#@-<< version dates >>
import leo.core.leoGlobals as g
import json
import shlex
import subprocess
import sys
testing = False
static_date = 'October 22, 2016' # Emergency fallback.
version = "5.4" # Always used.
#@+others
#@+node:ekr.20161017040256.1: ** create_commit_timestamp_json
def create_commit_timestamp_json(after=False):
    '''
    Create leo/core/commit_timestamp.json.

    This is called from @button make-leo in leoDist.leo,
    so get_version_from_git should always succeed.
    '''
    trace = False and not g.unitTesting
    commit, date = get_version_from_git(short=False)
    if commit:
        base = g.app.loadDir if g.app else g.os_path_dirname(__file__)
        path = g.os_path_finalize_join(
            base, '..', 'core', 'commit_timestamp.json')
        f = open(path, 'w')
        if after: commit = 'after ' + commit
        d = {'date': date, 'hash': commit}
        json.dump(d, f)
        f.write('\n')
        if trace:
            g.trace()
            g.print_dict(d)
        f.flush()
        f.close()
        # Add commit_timestamp.json so it doesn't appear dirty.
        out = git_output('git add leo/core/commit_timestamp.json')
        if trace: g.trace(out)
    else:
        g.trace('can not create commit_timestamp.json')
#@+node:tbrown.20161128220334.1: ** git_output
def git_output(cmd):
    """return output from a git command"""
    trace = False
    return g.toUnicode(subprocess.Popen(
        shlex.split(cmd),
        stdout=subprocess.PIPE,
        stderr=None if trace else subprocess.PIPE,
            # subprocess.DEVNULL is Python 3 only.
        shell=sys.platform.startswith('win'),
    ).communicate()[0])
#@+node:ekr.20161016063005.1: ** get_version_from_git
def get_version_from_git(short=True):
    trace = False
    try:
        is_windows = sys.platform.startswith('win')
        commit = git_output('git rev-parse HEAD')
        date = git_output('git show -s --format="%cD" '+commit)
        commit = g.toUnicode(commit)
        if trace: g.trace(commit)
        if commit and short:
            commit = commit[:8]
        if trace: g.trace(commit, date)
        return commit, date
    except Exception:
        # We are using a non .git release.
        # g.es_exception()
        return None, None
#@+node:ekr.20161016063719.1: ** get_version_from_json
def get_version_from_json(short=True):
    '''Return the commit hash and date from leo/core/commit_timestamp.json.'''
    trace = False
    path = g.os_path_finalize_join(
        g.app.loadDir, '..', 'core', 'commit_timestamp.json')
    if g.os_path_exists(path):
        try:
            d = json.load(open(path))
            if trace: g.trace(d)
            commit = d.get('hash')
            # The legacy pre-commit bash file writes 'asctime' and 'timestamp' keys.
            date = d.get('date') or d.get('asctime')
            if commit and short:
                commit = commit[:8 + (6 if commit.startswith('after ') else 0)]
            return commit, date
        except Exception:
            g.es_exception()
            g.trace('Error decoding', path)
            return None, None
    else:
        g.trace('not found:', path)
        return None, None
#@-others
if testing:
    commit, date = None, None
else:
    commit, date = get_version_from_git(short=True)
if not date:
    commit, date = get_version_from_json(short=True)
if not date:
    date = static_date
#@@language python
#@@tabwidth -4
#@-leo
