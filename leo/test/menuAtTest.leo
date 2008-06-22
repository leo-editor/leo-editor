<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet ekr_test?>
<leo_file>
<leo_header file_format="2" tnodes="0" max_tnode_index="0" clone_windows="0"/>
<globals body_outline_ratio="0.5">
	<global_window_position top="20" left="10" height="959" width="1678"/>
	<global_log_window_position top="0" left="0" height="0" width="0"/>
</globals>
<preferences/>
<find_panel_settings/>
<vnodes>
<v t="tbrown.20080604133537.9" str_leo_pos="1,7"><vh>@chapters</vh></v>
<v t="tbrown.20080604133537.35" a="E"><vh>@settings</vh>
<v t="tbrown.20080604152005.1"><vh>Create Test1 menu before Window menu</vh></v>
<v t="tbrown.20080604133537.36" a="E"><vh>@menuat /window before</vh>
<v t="tbrown.20080604133537.37"><vh>@menu Test1</vh>
<v t="tbrown.20080604133537.38"><vh>@item *contract-&amp;body-pane</vh></v>
<v t="tbrown.20080604133537.39"><vh>@item *contract-&amp;body-pane</vh></v>
</v>
</v>
<v t="tbrown.20080604152005.4"><vh>Create Test2 menu after Window menu</vh></v>
<v t="tbrown.20080604133537.40" a="E"><vh>@menuat /window after</vh>
<v t="tbrown.20080604133537.41" a="E"><vh>@menu Test2</vh>
<v t="tbrown.20080604133537.42"><vh>@item *contract-&amp;body-pane</vh></v>
<v t="tbrown.20080604133537.43"><vh>@item *contract-&amp;body-pane</vh></v>
</v>
</v>
<v t="tbrown.20080604152005.5"><vh>Replace Window-&gt;Expand Log Pane item with Test3 menu</vh></v>
<v t="tbrown.20080604142725.1" a="E"><vh>@menuat /window/expandlogpane replace</vh>
<v t="tbrown.20080604142725.2" a="E"><vh>@menu Test3</vh>
<v t="tbrown.20080604142725.3"><vh>@item *contract-&amp;body-pane</vh></v>
<v t="tbrown.20080604142725.4"><vh>@item *contract-&amp;body-pane</vh></v>
</v>
</v>
<v t="tbrown.20080604152005.6"><vh>Append two items to Window menu (must target item in that menu, e.g. fullyexpandpane)</vh></v>
<v t="tbrown.20080604142833.1" a="E"><vh>@menuat /window/fullyexpandpane append</vh>
<v t="tbrown.20080604142833.2"><vh>@item *contract-&amp;body-pane</vh></v>
<v t="tbrown.20080604144216.1"><vh>@item *contract-&amp;body-pane</vh></v>
</v>
<v t="tbrown.20080604152005.7"><vh>Copy the Cmds-&gt;Body Editors-&gt;Add Editor item</vh></v>
<v t="tbrown.20080604150649.1"><vh>@menuat /cmds/bodyeditors/addeditor copy</vh></v>
<v t="tbrown.20080604152005.8"><vh>Paste it to the end of the Window menu (must target item in that menu, e.g. fullyexpandpane)</vh></v>
<v t="tbrown.20080604151032.1"><vh>@menuat /window/fullyexpandpane append clipboard</vh></v>
<v t="tbrown.20080604152005.9"><vh>Cut the Cmds-&gt;Bodyeditors menu</vh></v>
<v t="tbrown.20080604151853.1"><vh>@menuat /cmds/bodyeditors cut</vh></v>
<v t="tbrown.20080604152005.3"><vh>Paste it to the end of the Window menu (must target item in that menu, e.g. fullyexpandpane)</vh></v>
<v t="tbrown.20080604151853.2"><vh>@menuat /window/fullyexpandpane append clipboard</vh></v>
</v>
</vnodes>
<tnodes>
<t tx="tbrown.20080604133537.9"></t>
<t tx="tbrown.20080604133537.35"></t>
<t tx="tbrown.20080604133537.36"></t>
<t tx="tbrown.20080604133537.37"></t>
<t tx="tbrown.20080604133537.38"></t>
<t tx="tbrown.20080604133537.39"></t>
<t tx="tbrown.20080604133537.40"></t>
<t tx="tbrown.20080604133537.41"></t>
<t tx="tbrown.20080604133537.42"></t>
<t tx="tbrown.20080604133537.43"></t>
<t tx="tbrown.20080604142725.1"></t>
<t tx="tbrown.20080604142725.2"></t>
<t tx="tbrown.20080604142725.3"></t>
<t tx="tbrown.20080604142725.4"></t>
<t tx="tbrown.20080604142833.1"></t>
<t tx="tbrown.20080604142833.2"></t>
<t tx="tbrown.20080604144216.1"></t>
<t tx="tbrown.20080604150649.1"></t>
<t tx="tbrown.20080604151032.1"></t>
<t tx="tbrown.20080604151853.1"></t>
<t tx="tbrown.20080604151853.2"></t>
<t tx="tbrown.20080604152005.1"></t>
<t tx="tbrown.20080604152005.3"></t>
<t tx="tbrown.20080604152005.4"></t>
<t tx="tbrown.20080604152005.5"></t>
<t tx="tbrown.20080604152005.6"></t>
<t tx="tbrown.20080604152005.7"></t>
<t tx="tbrown.20080604152005.8"></t>
<t tx="tbrown.20080604152005.9"></t>
</tnodes>
</leo_file>
