<?xml version="1.0" encoding="utf-8"?>
<!-- Created by Leo: http://leoeditor.com/leo_toc.html -->
<leo_file xmlns:leo="http://leoeditor.com/namespaces/leo-python-editor/1.1" >
<leo_header file_format="2" tnodes="0" max_tnode_index="0" clone_windows="0"/>
<globals body_outline_ratio="0.5" body_secondary_ratio="0.5">
	<global_window_position top="50" left="50" height="500" width="700"/>
	<global_log_window_position top="0" left="0" height="0" width="0"/>
</globals>
<preferences/>
<find_panel_settings/>
<vnodes>
<v t="bob.20180413130654.1"><vh>Automated tests</vh></v>
<v t="bob.20180115163052.3"><vh>Python</vh>
<v t="bob.20180205134933.1"><vh>Scripts executed by Ctrl-B</vh>
<v t="bob.20180115164119.1"><vh>One example file, one results file</vh>
<v t="bob.20180116151824.1"><vh>imports</vh></v>
</v>
</v>
<v t="bob.20180205134946.1"><vh>Programs</vh>
<v t="bob.20180125160225.1"><vh>@file tests.py</vh></v>
</v>
<v t="bob.20180205134900.1"><vh>Libraries</vh>
<v t="bob.20180205135005.1"><vh>@file lib_test.py</vh></v>
<v t="bob.20180206123613.1"><vh>@file idle_time.py</vh></v>
</v>
<v t="bob.20180220112341.1"><vh>Packaging</vh>
<v t="bob.20180220112438.1"><vh>@nosent __init__.py</vh></v>
</v>
</v>
</vnodes>
<tnodes>
<t tx="bob.20180115163052.3">@language python</t>
<t tx="bob.20180115164119.1">@others

while True:
    fpnTests, _ = QtWidgets.QFileDialog.getOpenFileName(parent=None, caption='Leo-Editor File containing tests',
        directory=os.path.abspath(os.path.join(os.getcwd(), '..', 'examples')), filter='Leo-Editor (*.leo)')
    if fpnTests: break
while True:
    fpnResults, ok = QtWidgets.QFileDialog.getSaveFileName(parent=None, caption='Text File for results',
        directory=os.path.abspath(os.getcwd()), filter='Text (*.txt)')
    if fpnResults: break
if os.path.exists(fpnResults):
    os.remove(fpnResults)
cmdrT= g.openWithFileName(fpnTests)
fdR = codecs.open(fpnResults, 'w', encoding='utf-8')
testCmdr = lib_test.TestCmdr(cmdrT, fdR)
genFindTests = lib_test.findTests(cmdrT)
itPoll = leoG.IdleTime((lambda itRunTests: lib_test.runTests(itRunTests, cmdrT, fdR, testCmdr, genFindTests)), delay=10)
itPoll.start()
</t>
<t tx="bob.20180116151824.1">import codecs
import os

from PyQt5 import QtWidgets

import leo.core.leoGlobals as leoG

from leo_babel.tests import lib_test</t>
<t tx="bob.20180205134900.1"></t>
<t tx="bob.20180205134933.1"></t>
<t tx="bob.20180205134946.1"></t>
<t tx="bob.20180220112341.1"></t>
<t tx="bob.20180220112438.1"></t>
<t tx="bob.20180413130654.1">Run in the tests sub-directory:

./tests.py ../examples/examples_error.leo ../results/error.txt
./tests.py ../examples/examples_external.leo ../results/external.txt
./tests.py ../examples/examples_multi_leo.leo ../results/multi_leo.txt
./tests.py ../examples/examples_no_error.leo ../results/no_error.txt
./tests.py ../examples/examples_unl.leo ../results/unl.txt
</t>
</tnodes>
</leo_file>
