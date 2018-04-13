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
<v t="bob.20170830131905.1"><vh>External Files |Tests|</vh>
<v t="bob.20180403110427.1"><vh>Script in a file and Results in this Leo file</vh>
<v t="bob.20180403110444.1"><vh>@file shell_name.sh</vh></v>
<v t="bob.20180403110534.1"><vh>Results</vh>
<v t="bob.20180403121321.1"><vh>00:00:01 Elapsed Time. 2018-04-03 12:13:20 End Time</vh>
<v t="bob.20180403121321.2"><vh>stdout</vh></v>
<v t="bob.20180403121321.3"><vh>stderr</vh></v>
</v>
<v t="bob.20180403110622.1"><vh>00:00:01 Elapsed Time. 2018-04-03 11:06:21 End Time</vh>
<v t="bob.20180403110622.2"><vh>stdout</vh></v>
<v t="bob.20180403110622.3"><vh>stderr</vh></v>
</v>
</v>
</v>
<v t="bob.20170830131910.1"><vh>Script in a file and Results in a separate file</vh>
<v t="bob.20170830131933.1"><vh>@file md5.sh</vh></v>
<v t="bob.20170830132009.1"
expanded="bob.20180403121323.1,bob.20180402161319.1,bob.20180331162138.1,"><vh>@file md5.txt</vh></v>
</v>
<v t="bob.20171220112005.1"><vh>Section used to root script subtree at third child</vh>
<v t="bob.20171220112144.1"><vh>Babel Script Root</vh></v>
<v t="bob.20171220112401.1"><vh>Results Root</vh>
<v t="bob.20180403121325.1"><vh>00:00:01 Elapsed Time. 2018-04-03 12:13:24 End Time</vh>
<v t="bob.20180403121325.2"><vh>stdout</vh></v>
<v t="bob.20180403121325.3"><vh>stderr</vh></v>
</v>
<v t="bob.20180402161321.1"><vh>00:00:01 Elapsed Time. 2018-04-02 16:13:20 End Time</vh>
<v t="bob.20180402161321.2"><vh>stdout</vh></v>
<v t="bob.20180402161321.3"><vh>stderr</vh></v>
</v>
<v t="bob.20180331162453.1"><vh>00:00:01 Elapsed Time. 2018-03-31 16:24:52 End Time</vh>
<v t="bob.20180331162453.2"><vh>stdout</vh></v>
<v t="bob.20180331162453.3"><vh>stderr</vh></v>
</v>
</v>
<v t="bob.20171220112315.1"><vh>&lt;&lt; Babel-Parameters-Script-Root &gt;&gt;</vh>
<v t="bob.20171220115613.1"><vh>babel_script_args</vh></v>
<v t="bob.20180108155028.1"><vh>babel_node_creation</vh></v>
</v>
</v>
</v>
<v t="bob.20171220112538.1"
expanded="bob.20180331162720.1,bob.20171220112506.8,bob.20171220112506.10,bob.20180403121328.1,bob.20180402161323.1,"><vh>@file externalExamples.txt</vh></v>
<v t="bob.20171208140717.1"><vh>@settings</vh>
<v t="bob.20171208140725.1"><vh>@@color Leo-Babel-stdout = #ff007f</vh></v>
<v t="bob.20171208141211.1"><vh>@@color Leo-Babel-stderr = #0331ff</vh></v>
<v t="bob.20171208141254.1"><vh>@@color Leo-Babel-completion = #01ff12</vh></v>
<v t="bob.20180105111101.1"><vh>@bool Leo-Babel-Node-Creation-Default = True</vh></v>
<v t="bob.20180108123417.1"><vh>@@string Leo-Babel-Python = python2</vh></v>
<v t="bob.20180108123502.1"><vh>@@string Leo-Babel-Shell = sh</vh></v>
</v>
</vnodes>
<tnodes>
<t tx="bob.20170830131905.1"></t>
<t tx="bob.20170830131910.1">@language python

babel_script_args = ['/tmp/*', '/boot/*']

@ These arguments cause md5.sh to checksum all files in /tmp and then all files in /boot.
@code

babel_node_creation = True
</t>
<t tx="bob.20171208140717.1"></t>
<t tx="bob.20171208140725.1"></t>
<t tx="bob.20171208141211.1"></t>
<t tx="bob.20171208141254.1"></t>
<t tx="bob.20171220112005.1">@doc
This example shows one way of putting a Babel Parameters script in a subtree.  This scheme does NOT work if this subtree is in an external file because the section reference is encountered first, so the section node is moved to the first child whenever the external file is read from disk.

@code
&lt;&lt; Babel-Parameters-Script-Root &gt;&gt;
@
This is another comment section
@c</t>
<t tx="bob.20171220112144.1">@language shell

for num in $@
do
    sum=$(expr $sum + $num)
done
echo $sum</t>
<t tx="bob.20171220112315.1">@language python
@others
</t>
<t tx="bob.20171220112401.1"></t>
<t tx="bob.20171220115613.1">babel_script_args = ['1', '2', '3', '4', '5', '6']</t>
<t tx="bob.20180105111101.1"></t>
<t tx="bob.20180108123417.1"></t>
<t tx="bob.20180108123502.1"></t>
<t tx="bob.20180108155028.1">babel_node_creation = True</t>
<t tx="bob.20180331162453.1">0 Subprocess Termination Code</t>
<t tx="bob.20180331162453.2">21
</t>
<t tx="bob.20180331162453.3"></t>
<t tx="bob.20180402161321.1">0 Subprocess Termination Code</t>
<t tx="bob.20180402161321.2">21
</t>
<t tx="bob.20180402161321.3"></t>
<t tx="bob.20180403110427.1"></t>
<t tx="bob.20180403110534.1"></t>
<t tx="bob.20180403110622.1">0 Subprocess Termination Code</t>
<t tx="bob.20180403110622.2">bob       4883  4879  0 11:06 ?        00:00:00 bash /sec/tmp/leoScript.py
bob       4884  4883  0 11:06 ?        00:00:00 ps -ef
bob       4887  4879  0 11:06 ?        00:00:00 /usr/bin/python3 /pri/git/leo-editor/leo/plugins/leo_babel/babel_kill.py 4883
</t>
<t tx="bob.20180403110622.3"></t>
<t tx="bob.20180403121321.1">0 Subprocess Termination Code</t>
<t tx="bob.20180403121321.2">bob       8690  8689  0 12:13 pts/0    00:00:00 bash /sec/tmp/leoScript.py
bob       8691  8690  0 12:13 pts/0    00:00:00 ps -ef
bob       8692  8689  0 12:13 pts/0    00:00:00 /usr/bin/python3 /pri/git/leo-editor/leo/plugins/leo_babel/babel_kill.py 8690
</t>
<t tx="bob.20180403121321.3"></t>
<t tx="bob.20180403121325.1">0 Subprocess Termination Code</t>
<t tx="bob.20180403121325.2">21
</t>
<t tx="bob.20180403121325.3"></t>
</tnodes>
</leo_file>
