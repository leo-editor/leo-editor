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
<v t="bob.20180109132747.1"><vh>Multiple Leo-Editor Files |Tests|</vh>
<v t="bob.20180109135736.1"><vh>Leo-Babel script using 3 Leo-Editor Files</vh></v>
<v t="bob.20180109165632.1"><vh>Leo-Babel script using a script in another Leo-Editor file</vh>
<v t="bob.20180109165727.1"><vh>Results</vh>
<v t="bob.20180403111032.1"><vh>00:00:01 Elapsed Time. 2018-04-03 11:10:31 End Time</vh>
<v t="bob.20180403111032.2"><vh>stdout</vh></v>
<v t="bob.20180403111032.3"><vh>stderr</vh></v>
</v>
<v t="bob.20180402160708.1"><vh>00:00:01 Elapsed Time. 2018-04-02 16:07:07 End Time</vh>
<v t="bob.20180402160708.2"><vh>stdout</vh></v>
<v t="bob.20180402160708.3"><vh>stderr</vh></v>
</v>
<v t="bob.20180402160634.1"><vh>00:00:01 Elapsed Time. 2018-04-02 16:06:33 End Time</vh>
<v t="bob.20180402160634.2"><vh>stdout</vh></v>
<v t="bob.20180402160634.3"><vh>stderr</vh></v>
</v>
<v t="bob.20180402120115.1"><vh>00:00:01 Elapsed Time. 2018-04-02 12:01:14 End Time</vh>
<v t="bob.20180402120115.2"><vh>stdout</vh></v>
<v t="bob.20180402120115.3"><vh>stderr</vh></v>
</v>
</v>
</v>
<v t="bob.20180403111449.1"><vh>Leo-Babel script using a script in another Leo-Editor file</vh>
<v t="bob.20180403112025.1"><vh>Not used</vh></v>
<v t="bob.20180403111449.2"><vh>Results</vh>
<v t="bob.20180403121618.1"><vh>00:00:01 Elapsed Time. 2018-04-03 12:16:17 End Time</vh>
<v t="bob.20180403121618.2"><vh>stdout</vh></v>
<v t="bob.20180403121618.3"><vh>stderr</vh></v>
</v>
<v t="bob.20180403112504.1"><vh>00:00:01 Elapsed Time. 2018-04-03 11:25:03 End Time</vh>
<v t="bob.20180403112504.2"><vh>stdout</vh></v>
<v t="bob.20180403112504.3"><vh>stderr</vh></v>
</v>
</v>
</v>
<v t="bob.20180109170422.1"><vh>Leo-Babel script using a Results Root in another Leo-Editor file</vh>
<v t="bob.20180109170626.1"><vh>Python - Date &amp; Time</vh>
<v t="bob.20180109170626.2"><vh>&lt;&lt; imports &gt;&gt;</vh></v>
<v t="bob.20180109170626.3"><vh>main()</vh></v>
</v>
</v>
</v>
<v t="bob.20171208140717.1"><vh>@settings</vh>
<v t="bob.20171208140725.1"><vh>@@color Leo-Babel-stdout = #ff007f</vh></v>
<v t="bob.20171208141211.1"><vh>@@color Leo-Babel-stderr = #0331ff</vh></v>
<v t="bob.20171208141254.1"><vh>@@color Leo-Babel-completion = #01ff12</vh></v>
<v t="bob.20180105111101.1"><vh>@@bool Leo-Babel-Node-Creation-Default = False</vh></v>
<v t="bob.20180108123417.1"><vh>@string Leo-Babel-Python = python2</vh></v>
<v t="bob.20180108123502.1"><vh>@@string Leo-Babel-Shell = sh</vh></v>
</v>
</vnodes>
<tnodes>
<t tx="bob.20171208140717.1"></t>
<t tx="bob.20171208140725.1"></t>
<t tx="bob.20171208141211.1"></t>
<t tx="bob.20171208141254.1"></t>
<t tx="bob.20180105111101.1"></t>
<t tx="bob.20180108123417.1"></t>
<t tx="bob.20180108123502.1"></t>
<t tx="bob.20180109132747.1"></t>
<t tx="bob.20180109135736.1">@language python

babel_script = 'unl:///pri/git/leo_babel/examples/test_scripts.leo#Test%20Scripts--&gt;Python%20-%20Date%20&amp;%20Time'

babel_results = 'unl:///pri/git/leo_babel/examples/test_results.leo#Test%20Results--&gt;Python%20-%20Date%20&amp;%20Time'

babel_node_creation = True</t>
<t tx="bob.20180109165632.1">@language python

babel_script = 'unl:///pri/git/leo_babel/examples/test_scripts.leo#Test%20Scripts--&gt;Python%20-%20Date%20&amp;%20Time'

babel_results = 'unl:///pri/git/leo_babel/examples/examples_multi_leo.leo#Multiple%20Leo-Editor%20Files%20|Tests|--&gt;Leo-Babel%20script%20using%20a%20script%20in%20another%20Leo-Editor%20file--&gt;Results'

babel_node_creation = True</t>
<t tx="bob.20180109165727.1"></t>
<t tx="bob.20180109170422.1">@language python

babel_results = 'unl:///pri/git/leo_babel/examples/test_results.leo#Test%20Results--&gt;Python%20-%20Date%20&amp;%20Time'

babel_node_creation = True</t>
<t tx="bob.20180109170626.1">@language python

&lt;&lt; imports &gt;&gt;

@others

main()</t>
<t tx="bob.20180109170626.2">import time
import datetime
</t>
<t tx="bob.20180109170626.3">def main():
    print("Today is day", time.localtime()[7], "of the current year")
    # Today is day 218 of the current year

    today = datetime.date.today()
    print("Today is day", today.timetuple()[7], "of ", today.year)
    # Today is day 218 of 2003

    print("Today is day", today.strftime("%Y-%m-%d"))
    # Today is day 218 of the current year
</t>
<t tx="bob.20180402120115.1">0 Subprocess Termination Code</t>
<t tx="bob.20180402120115.2">Today is day 92 of the current year
Today is day 92 of  2018
Today is day 092 of the current year
</t>
<t tx="bob.20180402120115.3"></t>
<t tx="bob.20180402160634.1">0 Subprocess Termination Code</t>
<t tx="bob.20180402160634.2">Today is day 92 of the current year
Today is day 92 of  2018
Today is day 092 of the current year
</t>
<t tx="bob.20180402160634.3"></t>
<t tx="bob.20180402160708.1">0 Subprocess Termination Code</t>
<t tx="bob.20180402160708.2">Today is day 92 of the current year
Today is day 92 of  2018
Today is day 092 of the current year
</t>
<t tx="bob.20180402160708.3"></t>
<t tx="bob.20180403111032.1">0 Subprocess Termination Code</t>
<t tx="bob.20180403111032.2">Today is day 93 of the current year
Today is day 93 of  2018
Today is day 093 of the current year
</t>
<t tx="bob.20180403111032.3"></t>
<t tx="bob.20180403111449.1">@language python

babel_script = 'unl:///pri/git/leo_babel/examples/test_scripts.leo#Test%20Scripts--&gt;Python%20version'

babel_node_creation = True</t>
<t tx="bob.20180403111449.2"></t>
<t tx="bob.20180403112025.1"></t>
<t tx="bob.20180403112504.1">0 Subprocess Termination Code</t>
<t tx="bob.20180403112504.2">2.7.12 (default, Dec  4 2017, 14:50:18) 
[GCC 5.4.0 20160609]
</t>
<t tx="bob.20180403112504.3"></t>
<t tx="bob.20180403121618.1">0 Subprocess Termination Code</t>
<t tx="bob.20180403121618.2">2.7.12 (default, Dec  4 2017, 14:50:18) 
[GCC 5.4.0 20160609]
</t>
<t tx="bob.20180403121618.3"></t>
</tnodes>
</leo_file>
