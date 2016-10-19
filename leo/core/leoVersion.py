#@+leo-ver=5-thin
#@+node:ekr.20090717092906.12765: * @file leoVersion.py
'''
A module for computing version-related info.

Leo's core uses leoVersion.commit, leoVersion.date and leoVersion.version'
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
testing = False
static_date = 'October 17, 2016' # Emergency fallback.
version = "5.4-b1" # Always used.
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
        if trace:
            g.trace()
            g.print_dict(d)
    else:
        g.trace('can not create commit_timestamp.json')
#@+node:ekr.20161016063005.1: ** get_version_from_git
def get_version_from_git(short=True):
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
            stderr=None if trace else subprocess.PIPE,
                # subprocess.DEVNULL is Python 3 only.
            shell=is_windows,
        )
        out, err = p.communicate()
        out = g.toUnicode(out)
        if trace: g.trace(out)
        m = re.search('commit (.*)\n', out)
        commit = m.group(1).strip() if m else ''
        if commit and short:
            commit = commit[:8]
        m = re.search('Date: (.*)\n', out)
        date = m.group(1).strip() if m else ''
        if trace: g.trace(commit, date)
        return commit, date
    except Exception:
        # We are using an official release.
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
                commit = commit[:8]
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
