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
<v t="bob.20170829112702.1"><vh>Error Expected</vh>
<v t="bob.20170829112831.1"><vh>No Babel Parameter Script |Tests|</vh>
<v t="bob.20170829112939.1"><vh>No Script Root</vh></v>
<v t="bob.20170829112959.1"><vh>No Results Root</vh>
<v t="bob.20170829113015.1"><vh>Script</vh></v>
</v>
</v>
<v t="bob.20170829112852.1"><vh>Babel Parameter Script</vh>
<v t="bob.20180402124632.1"><vh>Early Errors |Tests|</vh>
<v t="bob.20180402124652.1"><vh>Error in Babel Parameters Script</vh></v>
</v>
<v t="bob.20180109133259.1"><vh>UNL's |Tests|</vh>
<v t="bob.20170829113927.1"><vh>No Script Root, UNL for Results Root</vh></v>
<v t="bob.20170829114120.1"><vh>No Results Root, UNL for Script Root</vh></v>
<v t="bob.20170829120657.1"><vh>Script UNL does not match any position</vh></v>
<v t="bob.20170829120707.1"><vh>Results UNL does not match any position</vh></v>
<v t="bob.20170829114937.1"><vh>Multiple Script Targets Warning</vh>
<v t="bob.20170829115251.1"><vh>Not used</vh></v>
<v t="bob.20170829115258.1"><vh>Results</vh>
<v t="bob.20180403121057.1"><vh>00:00:00 Elapsed Time. 2018-04-03 12:10:56 End Time</vh>
<v t="bob.20180403121057.2"><vh>stdout</vh></v>
<v t="bob.20180403121057.3"><vh>stderr</vh></v>
</v>
<v t="bob.20180402161615.1"><vh>00:00:00 Elapsed Time. 2018-04-02 16:16:14 End Time</vh>
<v t="bob.20180402161615.2"><vh>stdout</vh></v>
<v t="bob.20180402161615.3"><vh>stderr</vh></v>
</v>
<v t="bob.20180331115032.1"><vh>00:00:01 Elapsed Time. 2018-03-31 11:50:31 End Time</vh>
<v t="bob.20180331115032.2"><vh>stdout</vh></v>
<v t="bob.20180331115032.3"><vh>stderr</vh></v>
</v>
</v>
</v>
<v t="bob.20170829120142.1"><vh>Multiple Results Targets Warning</vh>
<v t="bob.20170829120411.1"><vh>Script</vh></v>
</v>
<v t="bob.20180331160245.1"><vh>Multiple Matches for Script and Results Targets Warning</vh>
<v t="bob.20180331160245.2"><vh>Script</vh></v>
</v>
</v>
</v>
</v>
<v t="bob.20170829113353.1"><vh>UNL Targets</vh>
<v t="bob.20170716140012.1"><vh>Scripts</vh>
<v t="bob.20170716140016.1"><vh>babel script 01</vh></v>
<v t="bob.20170829114856.1"><vh>multiple targets</vh></v>
<v t="bob.20170829114907.1"><vh>multiple targets</vh></v>
</v>
<v t="bob.20170716140024.1"><vh>Results</vh>
<v t="bob.20170716140032.1"><vh>babel results 01</vh></v>
<v t="bob.20170829114917.1"><vh>multiple targets</vh>
<v t="bob.20180403121059.1"><vh>00:00:00 Elapsed Time. 2018-04-03 12:10:58 End Time</vh>
<v t="bob.20180403121059.2"><vh>stdout</vh></v>
<v t="bob.20180403121059.3"><vh>stderr</vh></v>
</v>
<v t="bob.20180403121058.1"><vh>00:00:00 Elapsed Time. 2018-04-03 12:10:57 End Time</vh>
<v t="bob.20180403121058.2"><vh>stdout</vh></v>
<v t="bob.20180403121058.3"><vh>stderr</vh></v>
</v>
<v t="bob.20180402161618.1"><vh>00:00:00 Elapsed Time. 2018-04-02 16:16:17 End Time</vh>
<v t="bob.20180402161618.2"><vh>stdout</vh></v>
<v t="bob.20180402161618.3"><vh>stderr</vh></v>
</v>
<v t="bob.20180402161616.1"><vh>00:00:00 Elapsed Time. 2018-04-02 16:16:15 End Time</vh>
<v t="bob.20180402161616.2"><vh>stdout</vh></v>
<v t="bob.20180402161616.3"><vh>stderr</vh></v>
</v>
<v t="bob.20180331160527.1"><vh>00:00:01 Elapsed Time. 2018-03-31 16:05:26 End Time</vh>
<v t="bob.20180331160527.2"><vh>stdout</vh></v>
<v t="bob.20180331160527.3"><vh>stderr</vh></v>
</v>
<v t="bob.20180331115215.1"><vh>00:00:01 Elapsed Time. 2018-03-31 11:52:14 End Time</vh>
<v t="bob.20180331115215.2"><vh>stdout</vh></v>
<v t="bob.20180331115215.3"><vh>stderr</vh></v>
</v>
</v>
<v t="bob.20170829114918.1"><vh>multiple targets</vh></v>
</v>
</v>
</vnodes>
<tnodes>
<t tx="bob.20170716140012.1"></t>
<t tx="bob.20170716140016.1">@language shell

echo Babel Script 01
</t>
<t tx="bob.20170716140024.1"></t>
<t tx="bob.20170716140032.1"></t>
<t tx="bob.20170829112702.1"></t>
<t tx="bob.20170829112831.1"></t>
<t tx="bob.20170829112852.1"></t>
<t tx="bob.20170829112939.1">@language python

expected_error = 'leo_babel.babel_api.BABEL_ROOT: First child of current node must be the script root.'</t>
<t tx="bob.20170829112959.1">@language python

babel_node_creation = True
expected_error = 'leo_babel.babel_api.BABEL_ROOT: Second child of current node must be the results root.'</t>
<t tx="bob.20170829113015.1"></t>
<t tx="bob.20170829113353.1"></t>
<t tx="bob.20170829113927.1">@language python

babel_results = "unl:///pri/git/leo_babel/examples.leo#Targets%20for%20UNL's--&gt;Results--&gt;babel%20results%2001"

expected_error = 'leo_babel.babel_api.BABEL_ROOT: First child of current node must be the script root.'</t>
<t tx="bob.20170829114120.1">@language python

babel_script = "unl:///pri/git/leo_babel/examples/examples_error.leo#UNL%20Targets--&gt;Scripts--&gt;babel%20script%2001"

expected_error = 'leo_babel.babel_api.BABEL_ROOT: Second child of current node must be the results root.'

babel_node_creation = True
</t>
<t tx="bob.20170829114856.1">@language shell

echo Correct target chosen</t>
<t tx="bob.20170829114907.1">@language shell

echo Incorrect target chosen
exit 1</t>
<t tx="bob.20170829114917.1"></t>
<t tx="bob.20170829114918.1"></t>
<t tx="bob.20170829114937.1">@language python

babel_script = "unl:///pri/git/leo_babel/examples/examples_error.leo#UNL%20Targets--&gt;Scripts--&gt;multiple%20targets"
babel_node_creation = True

expected_warning = 'Script Root UNL satisfies 2 positions.'</t>
<t tx="bob.20170829115251.1"></t>
<t tx="bob.20170829115258.1"></t>
<t tx="bob.20170829120142.1">@language python

babel_results = "unl:///pri/git/leo_babel/examples/examples_error.leo#UNL%20Targets--&gt;Results--&gt;multiple%20targets"
babel_node_creation = True

expected_warning = 'Results Root UNL satisfies 2 positions.'

check = 'Was the first in tree order target chosen?'</t>
<t tx="bob.20170829120411.1">@language shell

echo Was the first results target root in tree order target chosen?</t>
<t tx="bob.20170829120657.1">@language python

babel_script = "unl:///pri/git/leo_babel/examples/examples_error.leo#UNL%20Targets--&gt;Scripts--&gt;babel%20script%2001x"

expected_error = 'leo_babel.babel_api.BABEL_UNL_NO_POS: Script Root UNL does not match any position.'</t>
<t tx="bob.20170829120707.1">@language python

babel_script = "unl:///pri/git/leo_babel/examples/examples_error.leo#UNL%20Targets--&gt;Scripts--&gt;babel%20script%2001"

babel_results = "unl:///pri/git/leo_babel/examples/examples_error.leo#UNL%20Targets--&gt;Results--&gt;babel%20results%2001x"
babel_node_creation = True

expected_error = 'leo_babel.babel_api.BABEL_UNL_NO_POS: Results Root UNL does not match any position.'</t>
<t tx="bob.20180109133259.1"></t>
<t tx="bob.20180331115032.1">0 Subprocess Termination Code</t>
<t tx="bob.20180331115032.2">Correct target chosen
</t>
<t tx="bob.20180331115032.3"></t>
<t tx="bob.20180331115215.1">0 Subprocess Termination Code</t>
<t tx="bob.20180331115215.2">Was the first results target root in tree order target chosen?
</t>
<t tx="bob.20180331115215.3"></t>
<t tx="bob.20180331160245.1">@language python

babel_script = "unl:///pri/git/leo_babel/examples/examples_error.leo#UNL%20Targets--&gt;Scripts--&gt;multiple%20targets"
babel_results = "unl:///pri/git/leo_babel/examples/examples_error.leo#UNL%20Targets--&gt;Results--&gt;multiple%20targets"
babel_node_creation = True

expected_warning = 'Results Root UNL satisfies 2 positions.'

check = 'Was the first in tree order target chosen?'</t>
<t tx="bob.20180331160245.2">@language shell

echo Was the first results target root in tree order target chosen?</t>
<t tx="bob.20180331160527.1">0 Subprocess Termination Code</t>
<t tx="bob.20180331160527.2">Correct target chosen
</t>
<t tx="bob.20180331160527.3"></t>
<t tx="bob.20180402124632.1"></t>
<t tx="bob.20180402124652.1">@language python


babel_results = 'unl:///pri/git/leo_babel/examples.leo#Targets%20for%20UNL's--&gt;Results--&gt;babel%20results%2001'

expected_error = """Traceback (most recent call last):

  File "/pri/git/leo-editor/leo/core/leoCommands.py", line 2011, in executeAnyCommand
    return command(event)

  File "/pri/git/leo-editor/leo/plugins/leo_babel/babel_lib.py", line 633, in babelExec
    code = compile(script, 'Babel Parameter Script', 'exec')

  File "Babel Parameter Script", line 5

    babel_results = 'unl:///pri/git/leo_babel/examples.leo#Targets%20for%20UNL's--&gt;Results--&gt;babel%20results%2001'

                                                                               ^

SyntaxError: invalid syntax
"""</t>
<t tx="bob.20180402161615.1">0 Subprocess Termination Code</t>
<t tx="bob.20180402161615.2">Correct target chosen
</t>
<t tx="bob.20180402161615.3"></t>
<t tx="bob.20180402161616.1">0 Subprocess Termination Code</t>
<t tx="bob.20180402161616.2">Was the first results target root in tree order target chosen?
</t>
<t tx="bob.20180402161616.3"></t>
<t tx="bob.20180402161618.1">0 Subprocess Termination Code</t>
<t tx="bob.20180402161618.2">Correct target chosen
</t>
<t tx="bob.20180402161618.3"></t>
<t tx="bob.20180403121057.1">0 Subprocess Termination Code</t>
<t tx="bob.20180403121057.2">Correct target chosen
</t>
<t tx="bob.20180403121057.3"></t>
<t tx="bob.20180403121058.1">0 Subprocess Termination Code</t>
<t tx="bob.20180403121058.2">Was the first results target root in tree order target chosen?
</t>
<t tx="bob.20180403121058.3"></t>
<t tx="bob.20180403121059.1">0 Subprocess Termination Code</t>
<t tx="bob.20180403121059.2">Correct target chosen
</t>
<t tx="bob.20180403121059.3"></t>
</tnodes>
</leo_file>
