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
<v t="bob.20170816141740.3"><vh>Test Scripts</vh>
<v t="bob.20170816141833.1"><vh>Python - Date &amp; Time</vh>
<v t="bob.20170816141940.1"><vh>&lt;&lt; imports &gt;&gt;</vh></v>
<v t="bob.20170816142009.1"><vh>main()</vh></v>
</v>
<v t="bob.20180403111518.1"><vh>Python version</vh></v>
<v t="bob.20180110165114.1"><vh>Shell - System Version</vh></v>
<v t="bob.20180111145752.1"><vh>Shell - Disk Usage</vh></v>
</v>
</vnodes>
<tnodes>
<t tx="bob.20170816141740.3"></t>
<t tx="bob.20170816141833.1">@language python

&lt;&lt; imports &gt;&gt;

@others

main()</t>
<t tx="bob.20170816141940.1">import time
import datetime
</t>
<t tx="bob.20170816142009.1">def main():
    print("Today is day", time.localtime()[7], "of the current year")
    # Today is day 218 of the current year

    today = datetime.date.today()
    print("Today is day", today.timetuple()[7], "of ", today.year)
    # Today is day 218 of 2003

    print("Today is day", today.strftime("%j"), "of the current year")
    # Today is day 218 of the current year
</t>
<t tx="bob.20180110165114.1">@language shell

uname -a</t>
<t tx="bob.20180111145752.1">@language shell

du -h</t>
<t tx="bob.20180403111518.1">@language python

import sys

print(sys.version)</t>
</tnodes>
</leo_file>
