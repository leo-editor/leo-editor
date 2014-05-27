# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20140527083058.16707: * @file ../test/stc_unit_tests.py
#@@first
#@+others
#@+node:ekr.20140527073639.16704: ** @testsetup
# Common setup code for all unit tests.
# **Note**: Only included for "all" and "marked" *local* runs.
trace = False
do_gc = True
    # Takes about 0.5 sec. per test.
    # Can be done at end of test.
if c.isChanged():
    c.save()
import ast
import gc
import leo.core.leoSTC as stc
import time
import imp
imp.reload(stc) # Takes about 0.003 sec.
u = stc.Utils()
u.update_run_count(verbose=True)
t2 = time.clock()
if do_gc:
    gc.collect()
if trace:
    print('@testsetup gc.collect: %s %s' % (
        (do_gc,g.timeSince(t2))))
#@+node:ekr.20140527073639.16706: ** @test DataTraverser
#@+others
#@+node:ekr.20140527083058.16708: *3* report
def report():
    '''Report ambiguous symbols.'''
    n = 0
    for s in sorted(defs_d.keys()):
        aSet = defs_d.get(s)
        aList = sorted(aSet)
        if len(aList) > 1:
            n += 1
            # g.trace('multiple defs',s)
    return n
#@-others
project_name = 'leo'
flags = (
    'print',
    'report',
    # 'skip',
)
files = [
    # r'c:\leo.repo\leo-editor\leo\core\leoApp.py',
    # r'c:\leo.repo\leo-editor\leo\core\leoFileCommands.py',
] or u.project_files(project_name)
if g.app.runningAllUnitTests and (len(files) > 1 or 'skip' in flags):
    self.skipTest('slow test')
# Pass 0
t = time.time()
root_d = u.p0(files,project_name,False)
p0_time = u.diff_time(t)
# DataTraverser
t = time.time()
defs_d, refs_d = {},{}
dt = stc.DataTraverser(defs_d,refs_d)
for fn in sorted(files):
    dt(fn,root_d.get(fn))
dt_time = u.diff_time(t)
if 'print' in flags:
    print('parse: %s' % p0_time)
    print('   DT: %s' % dt_time)
    print('defs: %s refs: %s: ambiguous: %s' % (
        len(sorted(defs_d.keys())),
        len(sorted(refs_d.keys())),
        report(),
    ))
#@-others
#@@language python
#@@tabwidth -4
#@-leo
