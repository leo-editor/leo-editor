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
<v t="ekr.20160122104302.1"><vh>Startup</vh>
<v t="ekr.20160510132151.1"><vh>@button backup</vh></v>
<v t="ekr.20170203054655.1"><vh>@ignore unused buttons</vh>
<v t="ekr.20161122014821.1"><vh>@button make-importer</vh>
<v t="ekr.20161122020451.1"><vh>&lt;&lt; define run &amp; helpers &gt;&gt;</vh>
<v t="ekr.20161122020932.1"><vh>copy_tree</vh></v>
<v t="ekr.20161122021006.1"><vh>make_substitutions</vh></v>
<v t="ekr.20161122023427.1"><vh>run</vh></v>
<v t="ekr.20161122021342.1"><vh>substitue</vh></v>
</v>
<v t="ekr.20161122023554.1"><vh>@@file importers/{{name}}.py</vh>
<v t="ekr.20161122023554.2"><vh>class {{cap_name}}_Importer</vh>
<v t="ekr.20161122023554.3"><vh>{{name}}.Overrides</vh>
<v t="ekr.20161122023554.4"><vh>{{name}}.clean_headline</vh></v>
<v t="ekr.20161122023554.5"><vh>{{name}}.clean_nodes</vh></v>
</v>
</v>
<v t="ekr.20161122023554.6"><vh>class {{cap_name}}_ScanState</vh>
<v t="ekr.20161122023554.7"><vh>{{name}}_state.level</vh></v>
<v t="ekr.20161122023554.8"><vh>{{name}}_state.update</vh></v>
</v>
</v>
</v>
<v t="ekr.20161030154232.1"><vh>@button pep8 @key=Ctrl-5</vh>
<v t="ekr.20161031124905.1"><vh>class Pep8</vh>
<v t="ekr.20161031053537.1"><vh>change_all &amp; helpers</vh>
<v t="ekr.20161031074727.1"><vh>change_body</vh></v>
<v t="ekr.20161031075018.1"><vh>change_headline</vh></v>
</v>
<v t="ekr.20161031051319.1"><vh>get_name</vh></v>
<v t="ekr.20161031125119.1"><vh>run</vh></v>
<v t="ekr.20161031051342.1"><vh>to_pep8</vh></v>
</v>
<v t="ekr.20161031065339.1"><vh>clear</vh></v>
</v>
<v t="ekr.20160412101845.1"><vh>@button test-jup-export</vh></v>
<v t="ekr.20160412101537.1"><vh>@button test-jup-import</vh>
<v t="ekr.20160412101537.2"><vh>class Import_IPYNB</vh>
<v t="ekr.20160412101537.3"><vh>ctor</vh></v>
<v t="ekr.20160412115053.1"><vh>Entries</vh>
<v t="ekr.20160412101537.14"><vh>import_file: import-jupyter-notebook entry</vh></v>
<v t="ekr.20160412103110.1"><vh>ipynb.run</vh></v>
</v>
<v t="ekr.20160412115123.1"><vh>Scanners</vh>
<v t="ekr.20160412101537.4"><vh>do_any &amp; helpers</vh>
<v t="ekr.20160412101537.5"><vh>do_dict</vh></v>
<v t="ekr.20160412101537.6"><vh>do_other</vh></v>
<v t="ekr.20160412101537.7"><vh>do_string (test-jup-import)</vh></v>
<v t="ekr.20160412101537.8"><vh>do_list</vh></v>
<v t="ekr.20160412101537.9"><vh>do_source &amp; helpers</vh>
<v t="ekr.20160412101537.10"><vh>check_header</vh></v>
<v t="ekr.20160412101537.11"><vh>do_markdown_cell (test-jup-import)</vh></v>
</v>
</v>
<v t="ekr.20160412101537.12"><vh>do_cell</vh></v>
<v t="ekr.20160412101537.13"><vh>do_prefix</vh></v>
<v t="ekr.20160412101537.15"><vh>indent_cells &amp; helpers</vh>
<v t="ekr.20160412101537.16"><vh>move_node</vh></v>
</v>
</v>
<v t="ekr.20160412101537.17"><vh>Utils</vh>
<v t="ekr.20160412101537.18"><vh>error</vh></v>
<v t="ekr.20160412101537.19"><vh>get_code_language</vh></v>
<v t="ekr.20160412101537.20"><vh>get_file_name</vh></v>
<v t="ekr.20160412101537.21"><vh>is_dict</vh></v>
<v t="ekr.20160412101537.22"><vh>is_empty_code</vh></v>
<v t="ekr.20160412101537.23"><vh>new_node</vh></v>
<v t="ekr.20160412101537.24"><vh>parse</vh></v>
</v>
</v>
</v>
</v>
<v t="ekr.20160122104400.1"><vh>@settings</vh>
<v t="ekr.20160122104357.1"><vh>@data history-list</vh></v>
</v>
<v t="ekr.20170420085814.1"><vh>Recursive import script</vh></v>
</v>
<v t="ekr.20090430075506.4"><vh>Notes</vh>
<v t="ekr.20090430075506.3"><vh>@file leoPluginNotes.txt</vh></v>
</v>
<v t="edream.110203113231.618"><vh>Plugins</vh>
<v t="EKR.20040517090508"><vh>  Enable plugins using @enabled-plugins nodes</vh></v>
<v t="ekr.20050303051035"><vh>  Templates</vh>
<v t="ekr.20041114102139"><vh>Notes for plugin writers</vh></v>
<v t="ekr.20050306071629"><vh>Template for plugins that override commander methods</vh>
<v t="ekr.20050306071629.1"><vh>&lt;&lt; docstring &gt;&gt;</vh></v>
<v t="ekr.20050306071629.3"><vh>&lt;&lt; imports &gt;&gt;</vh></v>
<v t="ekr.20050306071629.4"><vh>init</vh></v>
<v t="ekr.20050306071540"><vh>onStart2</vh></v>
</v>
<v t="ekr.20050303051035.2"><vh>Template for plugins with per-commander controller class</vh>
<v t="ekr.20050303051035.5"><vh>&lt;&lt; imports &gt;&gt;</vh></v>
<v t="ekr.20050303051101"><vh>init</vh></v>
<v t="ekr.20050303051150"><vh>onCreate</vh></v>
<v t="ekr.20050303051222"><vh>class pluginController</vh>
<v t="ekr.20050303051222.1"><vh>__init__</vh></v>
</v>
</v>
</v>
<v t="ekr.20100103093121.5365"><vh>Auto completion</vh>
<v t="ekr.20091118065749.5261"><vh>@file ctagscompleter.py</vh></v>
<v t="ville.20091204224145.5355"><vh>@file codewisecompleter.py</vh></v>
</v>
<v t="edream.110203113231.667"><vh>Commands &amp; directives</vh>
<v t="edream.110203113231.741"><vh>@file add_directives.py</vh></v>
<v t="ekr.20101110084839.5682"><vh>@file bzr_qcommands.py</vh></v>
<v t="EKR.20040517080049.1"><vh>@file empty_leo_file.py</vh></v>
<v t="edream.110203113231.669"><vh>@file import_cisco_config.py</vh></v>
<v t="ekr.20101110092851.5812"><vh>@file initinclass.py</vh></v>
<v t="ekr.20101110091234.5700"><vh>@file leo_interface.py</vh></v>
<v t="ekr.20040419105219"><vh>@file lineNumbers.py</vh></v>
<v t="ekr.20040916084945"><vh>@file macros.py</vh></v>
<v t="edream.110203113231.724"><vh>@file mod_autosave.py</vh></v>
<v t="ekr.20050301083306"><vh>@file mod_read_dir_outline.py</vh></v>
<v t="edream.110203113231.727"><vh>@file mod_timestamp.py</vh></v>
<v t="TL.20090225102340.32"><vh>@file nodeActions.py</vh></v>
<v t="edream.110203113231.720"><vh>@file outline_export.py</vh></v>
<v t="danr7.20060912105041.1"><vh>@file paste_as_headlines.py</vh></v>
<v t="ekr.20041021120118"><vh>@file pretty_print.py</vh></v>
<v t="tbrown.20070117104409"><vh>@file quickMove.py</vh></v>
<v t="ekr.20081214160729.1"><vh>@file setHomeDirectory.py</vh></v>
<v t="danr7.20061010105952.1"><vh>@file word_count.py</vh></v>
</v>
<v t="edream.110203113231.729"><vh>Debugging</vh>
<v t="ekr.20101110091234.5689"><vh>@file debugger_pudb.py</vh></v>
<v t="edream.110203113231.730"><vh>@file dump_globals.py</vh></v>
<v t="edream.110203113231.732"><vh>@file enable_gc.py</vh></v>
<v t="edream.110203113231.734"><vh>@file quit_leo.py</vh></v>
<v t="edream.110203113231.735"><vh>@file trace_gc_plugin.py</vh></v>
<v t="edream.110203113231.736"><vh>@file trace_keys.py</vh></v>
<v t="edream.110203113231.738"><vh>@file trace_tags.py</vh></v>
</v>
<v t="ekr.20041030092101"><vh>Dyna plugins by e</vh></v>
<v t="ekr.20040722141148"><vh>Examples</vh>
<v t="edream.110203113231.916"><vh>@file examples/override_classes.py</vh></v>
<v t="edream.110203113231.919"><vh>@file examples/override_commands.py</vh></v>
<v t="edream.110203113231.921"><vh>@file examples/redefine_put.py</vh></v>
<v t="ekr.20060621123339"><vh>@file examples/print_cp.py</vh></v>
<v t="ekr.20040828105233"><vh>@file examples/chinese_menu.py</vh></v>
<v t="EKR.20040517080202.3"><vh>@file examples/french_fm.py</vh></v>
</v>
<v t="ekr.20101110150056.9457"><vh>Experimental</vh>
<v t="ekr.20090704103932.5160"><vh>@file leo_pdf.py</vh></v>
<v t="danr7.20060902083957"><vh>@file leo_to_rtf.py</vh></v>
<v t="ekr.20040205071616"><vh>@file mnplugins.py</vh></v>
<v t="ekr.20101110094759.5843"><vh>@file mod_speedups.py</vh></v>
<v t="ekr.20040910070811.1"><vh>@file run_nodes.py</vh></v>
<v t="ekr.20100103093121.5339"><vh>@file stickynotes_plus.py</vh></v>
<v t="ekr.20040331071919"><vh>Leo to AsciiDoc</vh>
<v t="ekr.20101110093449.5822"><vh>@file mod_leo2ascd.py</vh></v>
<v t="ekr.20101110150056.9445"><vh>@file mod_leo2ascd.txt</vh></v>
</v>
</v>
<v t="EKR.20040517075715"><vh>External programs</vh>
<v t="ekr.20110125103904.12504"><vh>@file gitarchive.py</vh></v>
<v t="EKR.20040517080049.4"><vh>@file open_shell.py</vh></v>
<v t="ville.20090503124249.1"><vh>@file tomboy_import.py</vh></v>
<v t="EKR.20040517075715.10"><vh>@file vim.py</vh></v>
<v t="EKR.20040517075715.12"><vh>@file xemacs.py</vh></v>
<v t="EKR.20040517075715.13"><vh>Word export</vh>
<v t="EKR.20040517075715.14"><vh>@file word_export.py</vh></v>
<v t="EKR.20040517075715.20"><vh>@file-nosent word_export.ini</vh></v>
</v>
</v>
<v t="edream.110203113231.872"><vh>Files and nodes</vh>
<v t="tbrown.20080613095157.2"><vh>@file active_path.py</vh></v>
<v t="edream.110203113231.873"><vh>@file at_folder.py</vh></v>
<v t="ekr.20040915085351"><vh>@file at_produce.py</vh></v>
<v t="ktenney.20041211072654.1"><vh>@file at_view.py</vh></v>
<v t="tbrown.20081223111325.3"><vh>@file backlink.py</vh></v>
<v t="tbrown.20070322113635"><vh>@file bookmarks.py</vh></v>
<v t="ekr.20060807103814.1"><vh>@file datenodes.py</vh></v>
<v t="ajones.20070122153625"><vh>@file expfolder.py</vh></v>
<v t="ekr.20040915105758.13"><vh>@file FileActions.py</vh></v>
<v t="ekr.20110110105526.5463"><vh>@file ftp.py</vh></v>
<v t="tbrown.20091214233510.5347"><vh>@file geotag.py</vh></v>
<v t="tbrown.20100228141752.5691"><vh>@file leocursor.py</vh></v>
<v t="ville.20120503224623.3574"><vh>@file leomylyn.py</vh></v>
<v t="ekr.20101110092851.5742"><vh>@file leoOPML.py</vh></v>
<v t="dan.20090217132953.1"><vh>@file mime.py</vh></v>
<v t="mork.20041018204908.1"><vh>@file multifile.py</vh></v>
<v t="ekr.20040331151007"><vh>@file niceNosent.py</vh></v>
<v t="edream.110203113231.876"><vh>@file read_only_nodes.py</vh></v>
<v t="ekr.20040828103325"><vh>@file startfile.py</vh></v>
<v t="ekr.20130808211520.15893"><vh>@file timestamp.py</vh></v>
<v t="tbrown.20110428144124.29061"><vh>@file xml_edit.py</vh></v>
<v t="mork.20041010095009"><vh>@file xsltWithNodes.py</vh></v>
</v>
<v t="ekr.20081121105001.2080"><vh>Gui plugins</vh>
<v t="ekr.20150107090324.1"><vh>@file cursesGui.py</vh></v>
<v t="ekr.20170419092835.1"><vh>@file cursesGui2.py</vh></v>
<v t="ekr.20170419150249.1"><vh>@file template_gui.py</vh></v>
</v>
<v t="ekr.20140723122936.17925"><vh>Importer plugins</vh>
<v t="ekr.20140723122936.18139"><vh>@file importers/__init__.py</vh></v>
<v t="ekr.20140723122936.17926"><vh>@file importers/c.py</vh></v>
<v t="ekr.20160505094722.1"><vh>@file importers/coffeescript.py</vh></v>
<v t="ekr.20140723122936.18140"><vh>@file importers/csharp.py</vh></v>
<v t="tbrown.20140801105909.47549"><vh>@file importers/ctext.py</vh></v>
<v t="ekr.20141116100154.1"><vh>@file importers/dart.py</vh></v>
<v t="ekr.20140723122936.18141"><vh>@file importers/elisp.py</vh></v>
<v t="ekr.20140723122936.18138"><vh>@file importers/html.py</vh></v>
<v t="ekr.20140723122936.18142"><vh>@file importers/ini.py</vh></v>
<v t="ekr.20160412101008.1"><vh>@file importers/ipynb.py</vh></v>
<v t="ekr.20140723122936.18143"><vh>@file importers/java.py</vh></v>
<v t="ekr.20140723122936.18144"><vh>@file importers/javascript.py</vh></v>
<v t="ekr.20160504080826.1"><vh>@file importers/json.py</vh></v>
<v t="ekr.20140723122936.18151"><vh>@file importers/leo_rst.py</vh></v>
<v t="ekr.20161108125620.1"><vh>@file importers/linescanner.py</vh></v>
<v t="ekr.20170530024520.2"
expanded="ekr.20170530024520.3,"><vh>@file importers/lua.py</vh></v>
<v t="ekr.20140725190808.18066"><vh>@file importers/markdown.py</vh></v>
<v t="ekr.20140723122936.18146"><vh>@file importers/org.py</vh></v>
<v t="ekr.20140723122936.18150"><vh>@file importers/otl.py</vh></v>
<v t="ekr.20140723122936.18147"><vh>@file importers/pascal.py</vh></v>
<v t="ekr.20161027100313.1"><vh>@file importers/perl.py</vh></v>
<v t="ekr.20140723122936.18148"><vh>@file importers/php.py</vh></v>
<v t="ekr.20140723122936.18149"><vh>@file importers/python.py</vh></v>
<v t="ekr.20140723122936.18152"><vh>@file importers/typescript.py</vh></v>
<v t="ekr.20140723122936.18137"><vh>@file importers/xml.py</vh></v>
</v>
<v t="ekr.20130927050813.13031"><vh>Obsolete</vh>
<v t="ajones.20070122160142"><vh>@file textnode.py</vh></v>
<v t="ekr.20050817132814"><vh>rst3</vh>
<v t="ekr.20050805162550"><vh>@file rst3.py</vh></v>
</v>
</v>
<v t="ekr.20041001210557"><vh>Scripting</vh>
<v t="tbrown.20100226095909.12777"><vh>@file leoscreen.py</vh></v>
<v t="tbrown.20140806084727.30174"><vh>@file livecode.py</vh></v>
<v t="ekr.20060328125248"><vh>@file mod_scripting.py</vh></v>
<v t="edream.110203113231.925"><vh>@file script_io_to_body.py</vh></v>
</v>
<v t="ekr.20120309073937.9878"><vh>Searching</vh>
<v t="ekr.20120309073748.9872"><vh>@file bigdash.py</vh></v>
<v t="peckj.20140804114520.9427"><vh>@file nodetags.py</vh></v>
<v t="peckj.20131130132659.5964"><vh>@file nodewatch.py</vh></v>
</v>
<v t="ekr.20050111122605"><vh>Servers &amp; web stuff</vh>
<v t="ville.20110206142055.10640"><vh>@file leofeeds.py</vh></v>
<v t="ville.20091009202416.10040"><vh>@file leoremote.py</vh></v>
<v t="EKR.20040517080250.1"><vh>@file mod_http.py</vh></v>
<v t="ekr.20131004162848.11444"><vh>@file rss.py</vh></v>
<v t="peckj.20140811080604.9496"><vh>@file sftp.py</vh></v>
<v t="ville.20110125222411.10536"><vh>@file leomail.py</vh></v>
</v>
<v t="ekr.20101004082701.5674"><vh>Slideshows, screencasts &amp; screenshots</vh>
<v t="ekr.20170128213103.1"><vh>@file demo.py</vh></v>
<v t="ekr.20120913110135.10579"><vh>@file screencast.py</vh></v>
<v t="ekr.20101121031443.5330"><vh>@file screenshots.py</vh></v>
<v t="ekr.20060831165821"><vh>@file slideshow.py</vh></v>
</v>
<v t="ekr.20071113084440"><vh>Testing</vh>
<v t="ekr.20080214092357"><vh>@file test/ekr_test.py</vh></v>
<v t="ekr.20050130120433"><vh>@@file test/failed_import.py</vh></v>
<v t="ekr.20071113085315"><vh>@file test/failed_to_load_plugin.py</vh></v>
<v t="ekr.20051016160700"><vh>@file testRegisterCommand.py</vh></v>
</v>
<v t="ekr.20050306081349"><vh>Text formatting</vh>
<v t="timo.20050213160555"><vh>@file bibtex.py</vh></v>
<v t="ekr.20070119094733.1"><vh>@file dtest.py</vh></v>
<v t="ville.20110409151021.5699"><vh>@file jinjarender.py</vh></v>
<v t="danr7.20060902215215.1"><vh>@file leo_to_html.py</vh></v>
<v t="tbrown.20130930160706.23451"><vh>@file markup_inline.py</vh></v>
<v t="peckj.20140113150237.7083"><vh>@file nodediff.py</vh></v>
<v t="tbrown.20130813134319.11942"><vh>@file richtext.py</vh></v>
<v t="ekr.20170217164004.1"><vh>@file tables.py</vh></v>
</v>
<v t="ekr.20121126102050.10134"><vh>Threading</vh>
<v t="ekr.20121126095734.12418"><vh>@file threadutil.py</vh></v>
</v>
<v t="ekr.20040915073259"><vh>User interface</vh>
<v t="ekr.20101110150056.9453"><vh> Qt only plugins</vh>
<v t="tbrown.20091029123555.5319"><vh>@file attrib_edit.py</vh></v>
<v t="ville.20090310191936.10"><vh>@file colorize_headlines.py</vh></v>
<v t="ekr.20090701111504.5294"><vh>@file contextmenu.py</vh></v>
<v t="tbrown.20090206153748.1"><vh>@file graphcanvas.py</vh></v>
<v t="ville.20090518182905.5419"><vh>@file nav_qt.py</vh></v>
<v t="ville.20120604212857.4215"><vh>@file notebook.py</vh></v>
<v t="ekr.20090622063842.5264"><vh>@file projectwizard.py</vh></v>
<v t="ekr.20160928073518.1"><vh>@file pyplot_backend.py</vh></v>
<v t="ville.20090314215508.4"><vh>@file quicksearch.py</vh></v>
<v t="tbrown.20130420091241.44181"><vh>@file screen_capture.py</vh></v>
<v t="ville.20090815203828.5235"><vh>@file spydershell.py</vh></v>
<v t="ekr.20100103093121.5329"><vh>@file stickynotes.py</vh></v>
<v t="tbrown.20090119215428.2"><vh>@file todo.py</vh></v>
<v t="ville.20110403115003.10348"><vh>@file valuespace.py</vh></v>
<v t="tbrown.20100318101414.5990"><vh>@file viewrendered.py</vh></v>
<v t="ekr.20140225222704.16748"><vh>@file viewrendered2.py</vh></v>
</v>
<v t="ekr.20061023142737"><vh> UNL plugin</vh>
<v t="ekr.20061023142737.1"><vh>Tests</vh>
<v t="rogererens.20041130095659"><vh>@url 'file: ./../../plugins/leoPlugins.leo#Plugins--&gt;UNL plugin--&gt;To do'</vh></v>
<v t="ekr.20061023141638"><vh>@url 'file:./../doc/leoDocs.leo#Users Guide--&gt;Basics--&gt;Customizing Leo'</vh></v>
</v>
</v>
<v t="ekr.20160519123329.1"><vh>@edit QNCalendarWidget.py</vh></v>
<v t="ekr.20060328125925"><vh>@file chapter_hoist.py</vh></v>
<v t="ville.20110115234843.8742"><vh>@file dragdropgoodies.py</vh></v>
<v t="tbrown.20090513125417.5244"><vh>@file interact.py</vh></v>
<v t="ekr.20040915073259.1"><vh>@file maximizeNewWindows.py</vh></v>
<v t="ekr.20101110093301.5818"><vh>@file mod_framesize.py</vh></v>
<v t="EKR.20040517080555.2"><vh>@file plugins_menu.py</vh></v>
<v t="peckj.20150428142633.1"><vh>@file python_terminal.py</vh></v>
<v t="edream.110203113231.924"><vh>@file redirect_to_log.py</vh></v>
<v t="EKR.20040517080555.36"><vh>@file scripts_menu.py</vh></v>
<v t="ekr.20170313020320.1"><vh>@file settings_finder.py</vh></v>
<v t="ville.20110304230157.6513"><vh>@file systray.py</vh></v>
<v t="tbrown.20141101114322.1"><vh>@file wikiview.py</vh></v>
<v t="ekr.20101110095202.5882"><vh>@file zenity_file_dialogs.py</vh></v>
</v>
<v t="ekr.20140726091031.18071"><vh>Writer plugins</vh>
<v t="ekr.20140726091031.18152"><vh>@file writers/__init__.py</vh></v>
<v t="ekr.20140726091031.18143"><vh>@file writers/basewriter.py</vh></v>
<v t="tbrown.20140804103545.29975"><vh>@file writers/ctext.py</vh></v>
<v t="ekr.20141116100154.2"><vh>@file writers/dart.py</vh></v>
<v t="ekr.20160412101901.1"><vh>@file writers/ipynb.py</vh></v>
<v t="ekr.20160504083330.1"><vh>@file writers/json.py</vh></v>
<v t="ekr.20140726091031.18080"><vh>@file writers/leo_rst.py</vh></v>
<v t="ekr.20140726091031.18073"><vh>@file writers/markdown.py</vh></v>
<v t="ekr.20140726091031.18079"><vh>@file writers/org.py</vh></v>
<v t="ekr.20140726091031.18078"><vh>@file writers/otl.py</vh></v>
</v>
</v>
</vnodes>
<tnodes>
<t tx="EKR.20040517075715"></t>
<t tx="EKR.20040517075715.13"></t>
<t tx="EKR.20040517075715.20">[Main]
use_styles = Yes
use_section_numbers = Yes
use_current_document = Yes
max_headings = 6
header_style = Heading
</t>
<t tx="EKR.20040517090508">@nocolor-node

Enable plugins by creating@enabled-plugins nodes in leoSettings files,
typically myLeoSettings.leo.See the node

Users Guide-- &gt; Chapter 8: Customizing Leo-- &gt;@rst
html\customizing.html-- &gt; Specifying settings-- &gt; Complex settings nodes

in LeoDocs.leo for full details.

**Important**: Leo no longer uses pluginsManager.txt to enable or disable plugins.
</t>
<t tx="edream.110203113231.618">@language python
@tabwidth -4
@pagewidth 80
</t>
<t tx="edream.110203113231.667"></t>
<t tx="edream.110203113231.729"></t>
<t tx="edream.110203113231.872">@nocolor-node

These plugins create new kinds of nodes, some of which affect the file system.</t>
<t tx="ekr.20040331071919"></t>
<t tx="ekr.20040722141148">@nocolor-node
@

You would typically not enable any of the following "plugins".

These plugins contain example code only.
</t>
<t tx="ekr.20040915073259">@nocolor-node

These plugins add buttons and other widgets to the icon area or
affect Leo's panes and windows in various ways.

</t>
<t tx="ekr.20041001210557"></t>
<t tx="ekr.20041030092101">@Notes by EKR: The dyna plugin is a remarkable body of work by 'e'.Have fun with it.

You may download the latest version at: http: // rclick.netfirms.com / dyna_menu.py.html
</t>
<t tx="ekr.20041114102139">@nocolor

Comments
--------

Most of the comments in the style guide are comments*about*the style guide.
You would replace these comments with your own, or eliminate them entirely in
your plugin.

Docstrings
----------

Several plugins show the docstring, so please take care to do a good job of
describing what the plugin does and how to use it.

Directives
----------

Please put the following at the end of the plugin's top-level node.

    @language python
    @tabwidth-4

Imports
-------

-Do* not*assume that modules like Qt are always available.

-Do* not*use from m import*

-Your code should test whether modules have been imported only if those modules
  may not be available on all platforms.

-To fail gracefully if the Qt gui is not in effect, put the following at
  the top level::

      g.assertUi('qt')

Exceptions
----------

It is usually best* not*to catch exceptions in plugins: doHook catches all
exceptions and disables further calls to plugins.

If a plugin catches exceptions during startup it should do either raise the
exception again or provide an init function at the top level that reports the
failure by returning False.

Use separate nodes
------------------

**Please**define each class, function or method in a separate node!To
make this work, just put@others in the root of your plugin as shown.Note
that@others may be nested, as shown in class myClass.
</t>
<t tx="ekr.20050111122605"></t>
<t tx="ekr.20050130120433">'''A plugin to test import problems.'''

import leo.core.leoGlobals as g

def onStart(tag,keywords):
    pass

# pylint: disable=unused-import
try:
    import xyzzy
except ImportError:
    g.cantImport('xyzzy',pluginName='failed_import')

def init():
    '''Return True if the plugin has loaded successfully.'''
    g.registerHandler("start2", onStart)
    g.plugin_signon(__name__)
    return True
</t>
<t tx="ekr.20050303051035">@nocolor-node

The following nodes show recommended style when writing plugins.</t>
<t tx="ekr.20050303051035.2">'''
A docstring describing your plugin and how to use it.
If it's long, you might put it in a separate section.
'''
&lt;&lt; imports &gt;&gt;
@others
@language python
@tabwidth-4
</t>
<t tx="ekr.20050303051035.5">import leo.core.leoGlobals as g

# Whatever other imports your plugins uses.
</t>
<t tx="ekr.20050303051101">def init():
    '''Return True if the plugin has loaded successfully.'''
    ok=g.app.gui.guiName() in('qt','qttabs')
    if ok:
        if 1: # Use this if you want to create the commander class before the frame is fully created.
            g.registerHandler('before-create-leo-frame',onCreate)
        else: # Use this if you want to create the commander class after the frame is fully created.
            g.registerHandler('after-create-leo-frame',onCreate)
    return ok</t>
<t tx="ekr.20050303051150">def onCreate(tag, keys):

    c=keys.get('c')
    if not c: return

    thePluginController=pluginController(c)
</t>
<t tx="ekr.20050303051222">class pluginController(object):

    @others</t>
<t tx="ekr.20050303051222.1">def __init__(self,c):

    self.c=c
    # Warning: hook handlers must use keywords.get('c'), NOT self.c.
</t>
<t tx="ekr.20050306071540">def onStart2(tag, keywords):

    """
    Showing how to define a global hook that affects all commanders.
    """

    log=c.frame.log.__class__

    # Replace frame.put with newPut (not shown).
    g.funcToMethod(newPut,log,"put")</t>
<t tx="ekr.20050306071629">'''
A docstring describing your plugin and how to use it.
If it's long, you might put it in a separate section.
'''
&lt;&lt; imports &gt;&gt;
@others
@language python
@tabwidth-4</t>
<t tx="ekr.20050306071629.1">'''This docstring should be a clear, concise description of
what the plugin does and how to use it.
'''
</t>
<t tx="ekr.20050306071629.3">import leo.core.leoGlobals as g

# Whatever other imports your plugins uses.
</t>
<t tx="ekr.20050306071629.4">def init():
    '''Return True if the plugin has loaded successfully.'''
    ok=True # This might depend on imports, etc.
    if ok:
        g.registerHandler('start2',onStart2)
    return ok</t>
<t tx="ekr.20050306081349"></t>
<t tx="ekr.20050817132814">@nocolor-node

Important: the rst3 plugin has largely been superceded by similar
commands built into Leo's core.

To activate the rst3 plugin, do the following:

1. Go to http://silvercity.sourceforge.net/.
- Follow the link 'SilverCity Releases'.
- Download the release that fits to your Python version.
- Double-klick on the downloaded file.

2. Go to http://docutils.sourceforge.net/.
- Have a look for item 'Download'
- Get, as the editor says, the latest snapshot by following the link
  'docutils-snapshot.tgz'.
- Make sure you have a application that can handle this format. 7zip is doing this great.
- Unpack it to a temporary folder.
- Open a console window, go to the temporary folder and type 'setup.py install'
  or '&lt;path_to_python.exe&gt;\python setup.py install'.

3. Start up Leo
- Check in the menu 'Edit' for item 'Write-Restructured-Text'.
</t>
<t tx="ekr.20061023141638"></t>
<t tx="ekr.20061023142737"></t>
<t tx="ekr.20061023142737.1"></t>
<t tx="ekr.20071113084440"># These plugins are for testing Leo's own plugin loading logic.
# There is no reason ever to enable these plugins.</t>
<t tx="ekr.20081121105001.2080"># Most other gui plugins are now in leoGuiPluginsRef.leo</t>
<t tx="ekr.20090430075506.4">@nosearch</t>
<t tx="ekr.20100103093121.5365"># These are experimental plugins.
</t>
<t tx="ekr.20101004082701.5674"></t>
<t tx="ekr.20101110150056.9453"># Some of the most important recent plugins work only with the Qt gui.
</t>
<t tx="ekr.20101110150056.9457"></t>
<t tx="ekr.20120309073937.9878"></t>
<t tx="ekr.20121126102050.10134"></t>
<t tx="ekr.20130927050813.13031"></t>
<t tx="ekr.20140723122936.17925"># These plugins now contain the importer code for all kinds of @auto nodes.
# Each plugin must define a top-level importer_dict dictionary describing the plugin.
@language python
</t>
<t tx="ekr.20140726091031.18071"># These plugins now contain the write code for all kinds special @auto nodes.
# Each plugin must define a top-level writer_dict dictionary describing the plugin.
@language python
</t>
<t tx="ekr.20160122104302.1">@nosearch</t>
<t tx="ekr.20160122104357.1">pylint
beautify-node
beautify-tree
</t>
<t tx="ekr.20160122104400.1"></t>
<t tx="ekr.20160412101537.1">'''Imports c:\prog\Julia.ipynb to the node import-Julia.ipynb'''
import nbformat
@others
g.cls()
if 0:
    # fn = r'c:\test\Julia.ipynb'
    fn = r'c:\test\export-neural-networds.ipynb'
    h = 'import-Julia.ipynb'
else:
    h = fn = r'c:\test\04_Neural_Networks.ipynb'
root = g.findTopLevelNode(c, h)
if root:
    while root.hasChildren():
        root.lastChild().doDelete()
else:
    p = c.lastTopLevel()
    root = p.insertAfter()
    root.h = h
x = Import_IPYNB(c)
x.import_file(fn, root)
if not g.unitTesting:
    # These don't work when running unit tests.
    c.selectPosition(root)
    # c.expandAllSubheads()
    c.redraw() 
    g.es_print('done')
</t>
<t tx="ekr.20160412101537.10">def check_header(self, m):
    '''Return (n, name) or (None, None) on error.'''
    val = (None, None)
    if m:
        n1, name, n2 = m.group(1), m.group(2), m.group(3)
        try:
            if int(n1) == int(n2):
                val = int(n1), name
        except Exception:
            pass
        if val == (None, None):
            g.trace('malformed header:', m.group(0))
    return val
</t>
<t tx="ekr.20160412101537.11">def do_markdown_cell(self, p, s):
    '''Split the markdown cell p if it contains one or more html headers.'''
    trace = False and not g.unitTesting
    SPLIT = False
        # Perhaps this should be a user option, 
        # but splitting adds signifincant whitespace.
        # The user can always split nodes manually if desired.
    i0, last = 0, p.copy()
    if not s.strip():
        return
    lines = g.splitLines(s)
    if SPLIT:
        for i, s in enumerate(lines):
            m = self.re_header.search(s)
            n, name = self.check_header(m)
            if n is None: continue
            h = '&lt;h%s&gt; %s &lt;/h%s&gt;' % (n, name.strip(), n)
            prefix = ''.join(lines[i0: i])
            suffix = ''.join(lines[i+1:]) # i+1: skip the heading.
            if trace: g.trace('%2s %2s %s' % (i-i0, len(lines)-i, h))
            if prefix.strip():
                p2 = last.insertAfter()
                p2.h = h
                p2.b = suffix
                last.b = '@language md\n\n' + prefix
                last = p2
                i0 = i
            else:
                last.h = h
                last.b = '@language md\n\n' + suffix
    else:
        for i, s in enumerate(lines):
            m = self.re_header.search(s)
            n, name = self.check_header(m)
            if n is not None:
                h = '&lt;h%s&gt; %s &lt;/h%s&gt;' % (n, name.strip(), n)
                p.h = h
                break
        p.b = '@language md\n\n' + ''.join(lines)
</t>
<t tx="ekr.20160412101537.12">def do_cell(self, cell, n):

    trace = False and not g.unitTesting
    self.cell_n = n
    if self.is_empty_code(cell):
        if trace: g.trace('skipping empty cell', n)
    else:
        # Careful: don't use self.new_node here.
        self.parent = self.cell = self.root.insertAsLastChild()
        self.parent.h = 'cell %s' % (n + 1)
        # Pre-compute the cell_type.
        self.cell_type = cell.get('cell_type')
        for key in sorted(cell):
            val = cell.get(key)
            self.do_any(key, val)
</t>
<t tx="ekr.20160412101537.13">def do_prefix(self, d):
    '''
    Handle the top-level non-cell data:
    metadata (dict)
    nbformat (int)
    nbformat_minor (int)
    '''
    if d:
        self.parent = self.new_node('# {prefix}')
        for key in sorted(d):
            if key != 'cells':
                val = d.get(key)
                self.do_any(key, val)
</t>
<t tx="ekr.20160412101537.14">def import_file(self, fn, root):
    '''
    Import the given .ipynb file.
    https://nbformat.readthedocs.org/en/latest/format_description.html
    '''
    c = self.c
    self.fn = fn
    self.parent = None
    self.root = root.copy()
    d = self.parse(fn)
    self.do_prefix(d)
    self.code_language = self.get_code_language(d)
    cells = d.get('cells', [])
    for n, cell in enumerate(cells):
        self.do_cell(cell, n)
    self.indent_cells()
    c.selectPosition(self.root)
    c.redraw()
</t>
<t tx="ekr.20160412101537.15">def indent_cells(self):
    '''
    Indent md nodes in self.root.children().
    &lt;h1&gt; nodes and non-md nodes stay where they are,
    &lt;h2&gt; nodes become children of &lt;h1&gt; nodes, etc.
    '''
    # Careful: links change during this loop.
    p = self.root.firstChild()
    stack = []
    after = self.root.nodeAfterTree()
    while p and p != self.root and p != after:
        m = self.re_header.search(p.h)
        n, name = self.check_header(m)
        if n is None: n = 1
        assert p.level() == 1, (p.level(), p.h)
        # g.trace('n', n, 'stack', len(stack), p.h)
        stack = self.move_node(n, p, stack)
        p.moveToNodeAfterTree()
        # g.trace('=====', p and p.h)
</t>
<t tx="ekr.20160412101537.16">def move_node(self, n, p, stack):
    '''Move node to level n'''
    # Cut back the stack so that p will be at level n (if possible).
    if stack:
        stack = stack[:n]
        if len(stack) == n:
            prev = stack.pop()
            p.moveAfter(prev)
        else:
            # p will be under-indented if len(stack) &lt; n-1
            # This depends on user markup, so it can't be helped.
            parent = stack[-1]
            n2 = parent.numberOfChildren()
            p.moveToNthChildOf(parent, n2)
    # Push p *after* moving p.
    stack.append(p.copy())
    # g.trace('   n', n, 'stack', len(stack), p.h)
    return stack
</t>
<t tx="ekr.20160412101537.17"></t>
<t tx="ekr.20160412101537.18">def error(self, s):

    g.es_print('error: %s' % (s), color='red')
</t>
<t tx="ekr.20160412101537.19">def get_code_language(self, d):
    '''Return the language specified by the top-level metadata.'''
    name = None
    m = d.get('metadata')
    if m:
        info = m.get('language_info')
        if info:
            name = info.get('name')
    return name
</t>
<t tx="ekr.20160412101537.2">class Import_IPYNB(object):
    '''A class to import .ipynb files.'''

    @others
</t>
<t tx="ekr.20160412101537.20">def get_file_name(self):
    '''Open a dialog to get a Jupyter (.ipynb) file.'''
    c = self.c
    fn = g.app.gui.runOpenFileDialog(
        c,
        title="Open Jupyter File",
        filetypes=[
            ("All files", "*"),
            ("Jupyter files", "*.ipynb"),
        ],
        defaultextension=".ipynb",
    )
    c.bringToFront()
    return fn
</t>
<t tx="ekr.20160412101537.21">def is_dict(self, obj):

    return isinstance(obj, (dict, nbformat.NotebookNode))
</t>
<t tx="ekr.20160412101537.22">def is_empty_code(self, cell):
    '''Return True if cell is an empty code cell.'''
    if cell.get('cell_type') == 'code':
        source = cell.get('source','')
        metadata = cell.get('metadata')
        keys = sorted(metadata.keys())
        if 'collapsed' in metadata:
            keys.remove('collapsed')
        outputs = cell.get('outputs')
        # g.trace(len(source), self.parent.h, sorted(cell))
        return not source and not keys and not outputs
    return False
</t>
<t tx="ekr.20160412101537.23">def new_node(self, h):

    parent = self.parent or self.root
    p = parent.insertAsLastChild()
    p.h = h
    return p
</t>
<t tx="ekr.20160412101537.24">def parse(self, fn):

    if g.os_path_exists(fn):
        with open(fn) as f:
            # payload_source = f.name
            payload = f.read()
        nb = nbformat.reads(payload, as_version=4)
            # nbformat.NO_CONVERT: no conversion
            # as_version=4: Require IPython 4.
        return nb
    else:
        g.es_print('not found', fn)
        return None
</t>
<t tx="ekr.20160412101537.3">def __init__(self, c=None, importCommands=None):
    '''Ctor for Import_IPYNB class.'''
    self.c = importCommands.c if importCommands else c
        # Commander of present outline.
    # g.trace('(Import_IPYNB)', self.c)
    self.cell = None
        # The present cell node.
    self.cell_n = None
        # The number of the top-level node being scanned.
    self.code_language = None
        # The language in effect for code cells.
    self.cell_type = None
        # The pre-computed cell type of the node.
    self.in_data = False
        # True if in range of any dict.
    self.parent = None
        # The parent for the next created node.
    self.re_header = re.compile(r'^.*&lt;[hH]([123456])&gt;(.*)&lt;/[hH]([123456])&gt;')
        # A regex matching html headers.
    self.root = None
        # The root of the to-be-created outline.
</t>
<t tx="ekr.20160412101537.4">def do_any(self, key, val):

    # if key == 'output_type': g.trace(val.__class__.__name__)
    if key == 'source':
        self.do_source(key, val)
    elif g.isString(val):
        self.do_string(key, val)
    elif isinstance(val, (list, tuple)):
        self.do_list(key, val)
    elif self.is_dict(val):
        self.do_dict(key, val)
    else:
        # Can be ints, None, etc.
        self.do_other(key, val)
</t>
<t tx="ekr.20160412101537.5">def do_dict(self, key, d):

    assert self.is_dict(d), d.__class__.__name__
    keys = list(d.keys())
    is_cell = self.parent == self.cell
    if key == 'metadata' and is_cell:
        if 'collapsed' in keys:
            if d.get('collapsed') in (False, 'false'):
                self.cell.expand()
            keys.remove('collapsed')
        if 'leo_headline' in keys:
            h = d.get('leo_headline')
            if h:
                self.cell.h = h
            keys.remove('leo_headline')
    # g.trace(key, is_cell, keys)
    if is_cell and key == 'metadata' and not keys:
        return # experimental
    old_parent = self.parent
    self.parent = self.new_node('# dict:%s' % key)
    old_in_dict = self.in_data
    self.in_data = key == 'data'
    for key2 in sorted(keys):
        val2 = d.get(key2)
        self.do_any(key2, val2)
    self.in_data = old_in_dict
    self.parent = old_parent
</t>
<t tx="ekr.20160412101537.6">def do_other(self, key, val):

    if key == 'execution_count' and val is None:
        pass # The exporter will create the proper value.
    else:
        name = 'null' if val is None else val.__class__.__name__
        p = self.new_node('# %s:%s' % (name, key))
        if val is None:
            p.b = '' # Exporter will translate to 'null'
        else:
            p.b = repr(val)
</t>
<t tx="ekr.20160412101537.7">def do_string(self, key, val):

    assert g.isString(val)
    is_cell = self.parent == self.cell
    if is_cell and key == 'cell_type':
        # Do *not* create a cell_type child.
        pass
    else:
        # Do create all other nodes.
        if self.in_data or len(g.splitLines(val.strip())) &gt; 1:
            key = 'list:' + key
        else:
            key = 'str:' + key
        p = self.new_node('# ' + key)
        if key.startswith('list:'):
            if key.endswith('html'):
                val = '@language html\n\n' + val
            elif key.endswith('xml'):
                val = '@language html\n\n' + val
            else:
                val = '@nocolor-node\n\n' + val
        # g.trace(key, g.splitLines(val)[:5])
        p.b = val
</t>
<t tx="ekr.20160412101537.8">def do_list(self, key, aList):

    assert isinstance(aList, (list, tuple)), aList.__class__.__name__
    is_cell = self.parent == self.cell
    if is_cell and not aList:
        return # Experimental.
    old_parent = self.parent
    self.parent = self.new_node('# list:%s' % key)
    for z in aList:
        if self.is_dict(z):
            for key in sorted(z):
                val = z.get(key)
                self.do_any(key, val)
        else:
            self.error('unexpected item in list: %r' % z)
    self.parent = old_parent
</t>
<t tx="ekr.20160412101537.9">def do_source(self, key, val):
    '''Set the cell's body text, or create a 'source' node.'''
    assert key == 'source', (key, val)
    is_cell = self.parent == self.cell
    if is_cell:
        # Set the body's text, splitting markdown nodes as needed.
        if self.cell_type == 'markdown':
            self.do_markdown_cell(self.cell, val)
        elif self.cell_type == 'raw':
            self.cell.b = '@nocolor\n\n' + val
        else:
            ### Is this correct???
            self.cell.b = '@language python\n\n' + val
    else:
        # Do create a new node.
        p = self.new_node('# list:%s' % key)
        p.b = val
</t>
<t tx="ekr.20160412101845.1"># g.cls()
import re
import sys
if 1:
    h = 'import-neural-networks.ipynb'
    fn = r'c:\test\export-neural-networds.ipynb'
else:
    h = 'import-Julia.ipynb'
    fn = r'c:\test\export-julia.ipynb'
p = g.findTopLevelNode(c, h)
assert p, h
@others
Export_IPYNB(c).export_outline(p, fn=fn)
</t>
<t tx="ekr.20160412103110.1">def run(self, s, parent, parse_body=False):
    '''
    @auto entry point. Called by code in leoImport.py.
    '''
    c = self.c
    fn = parent.atAutoNodeName()
    if c and fn:
        changed = c.isChanged()
        self.import_file(fn, parent)
        # Similar to Importer.run.
        parent.b = (
            '@nocolor-node\n\n' +
            'Note: This node\'s body text is ignored when writing this file.\n\n' +
            'The @others directive is not required\n'
        )
        for p in parent.self_and_subtree():
            p.clearDirty()
        c.setChanged(changed)
    elif not c or not fn:
        g.trace('can not happen', c, fn)
</t>
<t tx="ekr.20160412115053.1"></t>
<t tx="ekr.20160412115123.1"></t>
<t tx="ekr.20160510132151.1">@language python
'''Save a copy of this file to the Backup directory.'''
theDir,base = g.os_path_split(c.fileName())
path = g.os_path_join('~/Dropbox/','backups','leoPlugins',base)
branch = g.gitBranchName()
prefix = None if branch is 'None' else branch
c.backup(path, prefix=prefix, useTimeStamp=True)
    # Dropbox can show previous versions!
    # But this depends on proxy/firewall settings.
</t>
<t tx="ekr.20161030154232.1">'''Converts the word at the cursor to pep8 style throughout a given tree.'''
# aTestExample notFoundExample.
import re
# clear()
table = (
    # 'BLS.new_scan',
    # 'BLS.Code generation',
    # 'class Importer',
)
@others
Pep8(table, change=True).run()
</t>
<t tx="ekr.20161031051319.1">def get_name(self):
    i, j = c.editCommands.extendToWord(event=None, select=False)
    w = c.frame.body.wrapper
    s = w.getAllText()
    name = s[i:j]
    return name
</t>
<t tx="ekr.20161031051342.1">def to_pep8(self, s):
    
    if len(s) &gt; 1 and s[0].islower() and s.lower() != s:
        result = []
        for ch in s:
            result.append(ch)
            if ch.isupper():
                result.pop()
                result.append('_%s' % (ch.lower()))
        return ''.join(result)
    else:
        return name</t>
<t tx="ekr.20161031053537.1">def change_all(self, name, new_name, root):
    '''Change name to new_name throughout root's tree.'''
    u = c.undoer
    bunch = u.beforeChangeTree(root)
    found = False
    self.pattern = re.compile(r'\b%s\b' % name)
    for p in root.self_and_subtree():
        found = self.change_headline(name, new_name, p) or found
        found = self.change_body(name, new_name, p) or found
    if found:
        u.afterChangeTree(root, 'pep8', bunch)
    return found
</t>
<t tx="ekr.20161031065339.1">def clear():
    g.cls()
    c.k.simulateCommand('clear-log')
</t>
<t tx="ekr.20161031074727.1">def change_body(self, name, new_name, p):
    indices = []
    for m in self.pattern.finditer(p.b):
        indices.append(str(m.start()))
    if indices:
        n = len(indices)
        g.es_print('%s change%s: %s' % (n, g.plural(n), p.h))
        s = p.b
        for i in reversed(indices):
            i = int(i)
            s = s[:i] + new_name + s[i+len(name):]
        if self.change:
            p.b = s
            p.setDirty()
        else:
            g.es_print(s)
    return bool(indices)</t>
<t tx="ekr.20161031075018.1">def change_headline(self, name, new_name, p):
    m = self.pattern.search(p.h)
    if m:
        i = m.start()
        s = p.h
        s = s[:i] + new_name + s[i+len(name):]
        if self.change:
            p.h = s
            p.setDirty()
            g.es_print('changed headline', s)
        else:
            g.es_print('headline', s)
    return bool(m)
</t>
<t tx="ekr.20161031124905.1">class Pep8:
    '''
    Convert the word under the cursor to pep8 style in all subtrees in
    table.
    '''
    
    def __init__ (self, table, change=False):
        '''Ctor for Pep8 class.'''
        self.change = change
        self.table = table
        
    @others
</t>
<t tx="ekr.20161031125119.1">def run(self):
    # self.clear()
    name = self.get_name()
    new_name = self.to_pep8(name)
    if len(name) &lt; 2:
        g.es_print('name too short:', name)
    elif new_name == name:
        g.es_print('already pep8:', name)
    else:
        g.es_print('%s -&gt; %s' % (name, new_name))
        c.findCommands.ftm.setFindText(new_name)
            # Preload the replacement text.
        found = False
        for target in table:
            root = g.findNodeAnywhere(c, target)
            if root:
                found = self.change_all(name, new_name, root) or found
            else:
                g.es_print('not found: %s' % target)
        if found:
            c.redraw()
        else:
            g.es_print('not found:', name)
</t>
<t tx="ekr.20161122014821.1">g.cls()
# define constants that describe the new language.
name = 'php'
    # The name of the file, and the prefix for classes.
language = 'php'
    # The name of the language, case doesn't matter.
extensions = ['.php',]
    # A list of file extensions supported by this importer.
strict = False
    # True if leading whitespace is particularly significant.
state_ivar = 'self.curlies'
    # 'self.indent' for python, coffeescript.
    # 'self.curlies' for many other languages
    # '(self, curlies, self.parens)' for more complex comparisons
&lt;&lt; define run &amp; helpers &gt;&gt;
run(extensions, language, name, state_ivar)
</t>
<t tx="ekr.20161122020451.1">@others</t>
<t tx="ekr.20161122020932.1">def copy_tree(source, root, h):
    '''Copy the source tree to the node after p, with headline h.'''
    p2 = root.insertAfter()
    source.copyTreeFromSelfTo(p2)
    p2.h = h
    return p2
 </t>
<t tx="ekr.20161122021006.1">def make_substitutions(destination, patterns):
    '''Make all substitutions in the destination tree.'''
    for p in destination.self_and_subtree():
        h = substitute(p.h, patterns)
        if p.h != h:
            # g.trace('CHANGED:', p.h, '==&gt;', h)
            p.h = h
        b = substitute(p.b, patterns)
        if p.b != b:
            # g.trace('CHANGED:', p.b, '==&gt;', b)
            p.b = b
</t>
<t tx="ekr.20161122021342.1">def substitute(s, patterns):
    '''Make all substitutions in s.'''
    for pattern in patterns:
        find = '{{%s}}' % pattern
        replace = patterns.get(pattern)
        i = 0
        while i &lt; len(s):
            progress = i
            j = s.find(find, i)
            if j == -1: break
            s = s[:j] + replace + s[j+len(find):]
            i = j+len(replace)
            assert progress &lt; i
    return s
</t>
<t tx="ekr.20161122023427.1">def run(extensions, language, name, state_ivar):
    '''The driver for this script.'''
    patterns = {
        'cap_name': name.capitalize(),
        'extensions': '[%s]' % ', '.join(["'%s'" % (z) for z in extensions]),
        'language': language.lower(),
        'name': name.lower(),
        'strict': 'True' if strict else 'False',
        'state_ivar': state_ivar,
    }
    h = '@button make-importer'
    root = g.findNodeAnywhere(c, h)
    assert root, h
    h = '@@file importers/{{name}}.py'
    source = g.findNodeInTree(c, root, h)
    assert source, h
    destination = copy_tree(source, root, h)
    make_substitutions(destination, patterns)
    c.contractAllHeadlines()
    c.redraw()</t>
<t tx="ekr.20161122023554.1">'''The @auto importer for the {{name}} language.'''
import leo.plugins.importers.linescanner as linescanner
Importer = linescanner.Importer
@others
importer_dict = {
    'class': {{cap_name}}_Importer,
    'extensions': {{extensions}},
}
@language python
@tabwidth -4


</t>
<t tx="ekr.20161122023554.2">class {{cap_name}}_Importer(Importer):
    '''The importer for the {{name}} lanuage.'''

    def __init__(self, importCommands, atAuto):
        '''{{cap_name}}_Importer.__init__'''
        # Init the base class.
        Importer.__init__(self,
            importCommands,
            atAuto = atAuto,
            language = '{{language}}',
            state_class = {{cap_name}}_ScanState,
            strict = {{strict}},
        )
        
    @others
</t>
<t tx="ekr.20161122023554.3"># These can be overridden in subclasses.
</t>
<t tx="ekr.20161122023554.4">### Define an override if desired...

if 0: # The base class
    def clean_headline(self, s):
        '''Return a cleaned up headline s.'''
        return s.strip()
        
if 0: # A more complex example, for the C language.
    def clean_headline(self, s):
        '''Return a cleaned up headline s.'''
        import re
        type1 = r'(static|extern)*'
        type2 = r'(void|int|float|double|char)*'
        class_pattern = r'\s*(%s)\s*class\s+(\w+)' % (type1)
        pattern = r'\s*(%s)\s*(%s)\s*(\w+)' % (type1, type2)
        m = re.match(class_pattern, s)
        if m:
            prefix1 = '%s ' % (m.group(1)) if m.group(1) else ''
            return '%sclass %s' % (prefix1, m.group(2))
        m = re.match(pattern, s)
        if m:
            prefix1 = '%s ' % (m.group(1)) if m.group(1) else ''
            prefix2 = '%s ' % (m.group(2)) if m.group(2) else ''
            h = m.group(3) or '&lt;no c function name&gt;'
            return '%s%s%s' % (prefix1, prefix2, h)
        else:
            return s
</t>
<t tx="ekr.20161122023554.5">def clean_nodes(self, parent):
    '''
    Clean all nodes in parent's tree.
    Subclasses override this as desired.
    See perl_i.clean_nodes for an examplle.
    '''
    pass
</t>
<t tx="ekr.20161122023554.6">class {{cap_name}}_ScanState:
    '''A class representing the state of the {{name}} line-oriented scan.'''
    
    def __init__(self, d=None):
        '''{{cap_name}}_ScanState.__init__'''
        if d:
            prev = d.get('prev')
            self.context = prev.context
            ### Adjust these by hand.
            self.curlies = prev.curlies
        else:
            self.context = ''
            ### Adjust these by hand.
            self.curlies = 0

    def __repr__(self):
        '''{{cap_name}}_ScanState.__repr__'''
        ### Adjust these by hand.
        return "{{cap_name}}_ScanState context: %r curlies: %s" % (
            self.context, self.curlies)

    __str__ = __repr__

    @others
</t>
<t tx="ekr.20161122023554.7">def level(self):
    '''{{cap_name}}_ScanState.level.'''
    return {{state_ivar}}

</t>
<t tx="ekr.20161122023554.8">def update(self, data):
    '''
    {{cap_name}}_ScanState.update

    Update the state using the 6-tuple returned by v2_scan_line.
    Return i = data[1]
    '''
    context, i, delta_c, delta_p, delta_s, bs_nl = data
    # All ScanState classes must have a context ivar.
    self.context = context
    self.curlies += delta_c  
    ### Update {{cap_name}}_ScanState ivars
    # self.bs_nl = bs_nl
    # self.parens += delta_p
    # self.squares += delta_s
    return i
</t>
<t tx="ekr.20170203054655.1"></t>
<t tx="ekr.20170420085814.1">'''Recursively import all python files in a directory and clean the result.'''
dir_ = r'C:\leo.repo\leo-editor\leo\external\npyscreen'
g.cls()
c.recursiveImport(
    dir_ = dir_,
    kind = '@file', # '@clean', #'@nosent','@auto','@file',
    recursive = True,
    safe_at_file = True,
    theTypes = ['.py',],
)
</t>
<t tx="rogererens.20041130095659">@ It is possible to link to nodes within the same file.  However clones might be better.
</t>
</tnodes>
</leo_file>
