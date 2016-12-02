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
<v t="ekr.20160122104400.1"><vh>@settings</vh>
<v t="ekr.20160122104357.1"><vh>@data history-list</vh></v>
</v>
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
<v t="ekr.20101110150056.9453"><vh> Qt only plugins</vh>
<v t="tbrown.20091029123555.5319" descendentVnodeUnknownAttributes="7d71005803000000302e3371017d710258040000007465737471037d710458050000005f6564697471057d7106580400000074686973710758120000006f6b20686f77206120626f757420746869737108737373732e"><vh>@file attrib_edit.py</vh></v>
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
<v t="ekr.20140725190808.18066"><vh>@file importers/markdown.py</vh></v>
<v t="ekr.20140723122936.18146"><vh>@file importers/org.py</vh></v>
<v t="ekr.20140723122936.18150"><vh>@file importers/otl.py</vh></v>
<v t="ekr.20140723122936.18147"><vh>@file importers/pascal.py</vh></v>
<v t="ekr.20161027100313.1"><vh>@file importers/perl.py</vh></v>
<v t="ekr.20140723122936.18148"><vh>@file importers/php.py</vh></v>
<v t="ekr.20161029103517.1"><vh>@file importers/python.py</vh></v>
<v t="ekr.20140723122936.18152"><vh>@file importers/typescript.py</vh></v>
<v t="ekr.20161121204146.2"><vh>@file importers/xml.py</vh></v>
</v>
<v t="ekr.20130927050813.13031"><vh>Obsolete</vh>
<v t="ajones.20070122160142"><vh>@file textnode.py</vh></v>
<v t="ekr.20050817132814"><vh>rst3</vh>
<v t="ekr.20090704103932.5160"><vh>@file leo_pdf.py</vh></v>
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
</v>
<v t="ekr.20121126102050.10134"><vh>Threading</vh>
<v t="ekr.20121126095734.12418"><vh>@file threadutil.py</vh></v>
</v>
<v t="ekr.20040915073259"><vh>User interface</vh>
<v t="ekr.20061023142737"><vh> UNL plugin</vh>
<v t="ekr.20061023142737.1"><vh>Tests</vh>
<v t="rogererens.20041130095659"><vh>@url 'file: ./../../plugins/leoPlugins.leo#Plugins--&gt;UNL plugin--&gt;To do'</vh></v>
<v t="ekr.20061023141638"><vh>@url 'file:./../doc/leoDocs.leo#Users Guide--&gt;Basics--&gt;Customizing Leo'</vh></v>
</v>
</v>
<v t="ekr.20060328125925"><vh>@file chapter_hoist.py</vh></v>
<v t="ville.20110115234843.8742"><vh>@file dragdropgoodies.py</vh></v>
<v t="tbrown.20090513125417.5244"><vh>@file interact.py</vh></v>
<v t="ekr.20040915073259.1"><vh>@file maximizeNewWindows.py</vh></v>
<v t="ekr.20101110093301.5818"><vh>@file mod_framesize.py</vh></v>
<v t="EKR.20040517080555.2"><vh>@file plugins_menu.py</vh></v>
<v t="peckj.20150428142633.1"><vh>@file python_terminal.py</vh></v>
<v t="ekr.20160519123329.1"><vh>@edit QNCalendarWidget.py</vh></v>
<v t="edream.110203113231.924"><vh>@file redirect_to_log.py</vh></v>
<v t="EKR.20040517080555.36"><vh>@file scripts_menu.py</vh></v>
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
<v t="ekr.20161031131716.1"><vh>Recent Code</vh>
<v t="ekr.20161129025022.1"><vh>copies</vh>
<v t="ekr.20161119083909.1"><vh>COPY py_i.findClass (legacy)</vh></v>
<v t="ekr.20161126160955.1"><vh>COPY importers/leo_rst.py</vh>
<v t="ekr.20161126160955.2"><vh>class RstScanner</vh>
<v t="ekr.20161126160955.3"><vh> __init__ (RstScanner)</vh></v>
<v t="ekr.20161126160955.4"><vh>adjustParent (RstScanner)</vh></v>
<v t="ekr.20161126160955.5"><vh>computeBody (RstScanner)</vh></v>
<v t="ekr.20161126160955.6"><vh>computeSectionLevel</vh></v>
<v t="ekr.20161126160955.7"><vh>createDeclsNode (RstScanner)</vh></v>
<v t="ekr.20161126160955.8"><vh>endGen (RstScanner)</vh></v>
<v t="ekr.20161126160955.9"><vh>isUnderLine</vh></v>
<v t="ekr.20161126160955.10"><vh>startsComment/ID/String</vh></v>
<v t="ekr.20161126160955.11"><vh>startsHelper (RstScanner)</vh></v>
<v t="ekr.20161126160955.12"><vh>startsSection &amp; helper</vh>
<v t="ekr.20161126160955.13"><vh>getLine</vh></v>
</v>
</v>
</v>
<v t="ekr.20140723122936.18083"><vh>OLD class PhpScanner</vh>
<v t="ekr.20140723122936.18084"><vh> __init__(PhpScanner)</vh></v>
<v t="ekr.20140723122936.18085"><vh>isPurePHP (not used)</vh></v>
<v t="ekr.20161126161149.1"><vh>skip_heredoc_string</vh>
<v t="ekr.20161126161323.1"><vh>&lt;&lt; skip_heredoc docstrig &gt;&gt;</vh></v>
</v>
<v t="ekr.20140723122936.18086"><vh>Overrides</vh>
<v t="ekr.20140723122936.18087"><vh>startsString skipString</vh></v>
<v t="ekr.20140723122936.18088"><vh>getSigId</vh></v>
</v>
</v>
</v>
<v t="ekr.20161126074152.1"><vh>Tests &amp; experiments</vh>
<v t="ekr.20161109111154.1"><vh>Unit tests</vh>
<v t="ekr.20161113132509.1"><vh>--- Unit tests for scanners</vh>
<v t="ekr.20161114024119.1"><vh>i.test_scan_state</vh></v>
<v t="ekr.20161113070532.1"><vh>@test coffee.scan_line</vh>
<v t="ekr.20161113070952.1"><vh>&lt;&lt; define table &gt;&gt;</vh></v>
</v>
<v t="ekr.20161113083459.1"><vh>@command test-python @key=ctrl-6</vh>
<v t="ekr.20161114011813.1"><vh>&lt;&lt; define python tests &gt;&gt;</vh></v>
</v>
</v>
<v t="ekr.20161124154123.1"><vh>dart</vh>
<v t="ekr.20161123121746.1"><vh>@test dart</vh></v>
</v>
<v t="ekr.20161125083451.1"><vh>markdown tests</vh>
<v t="ekr.20161124122450.1"><vh>@button make-md-test</vh>
<v t="ekr.20161124122613.1"><vh>&lt;&lt; define preamble &gt;&gt;</vh></v>
</v>
<v t="ekr.20161124191927.1"><vh>@test markdown importer-regex</vh></v>
<v t="ekr.20161125042407.1"><vh> COPY Tests of @auto-md</vh>
<v t="ekr.20161125042407.2"><vh>@test md-import-test</vh>
<v t="ekr.20161125042407.3"><vh>&lt;&lt; define s &gt;&gt; (md-import-test)</vh></v>
</v>
<v t="ekr.20161125042407.4"><vh>@test md-import-test-rst-style</vh>
<v t="ekr.20161125230713.1"><vh>&lt;&lt; define s &gt;&gt; (md-import-test-rst-style)</vh></v>
</v>
</v>
<v t="ekr.20161125083633.1"><vh>@test markdown importer-3</vh></v>
</v>
<v t="ekr.20161124154130.1"><vh>org</vh>
<v t="ekr.20161123202118.1"><vh>@test org_pattern</vh></v>
<v t="ekr.20161124154218.1"><vh>@test org-placeholder</vh>
<v t="ekr.20161124160431.1"><vh>@@auto-org c:/leo.repo/leo-editor/leo/plugins/org-placeholder</vh>
<v t="ekr.20161124160431.2"><vh>Section 1</vh></v>
<v t="ekr.20161124160431.3"><vh>Section 2</vh>
<v t="ekr.20161124160431.4"><vh>Section 2-1</vh>
<v t="ekr.20161124160431.5"><vh>Section 2-1-1</vh></v>
</v>
</v>
<v t="ekr.20161124160431.6"><vh>Section 3</vh>
<v t="ekr.20161124160431.7"><vh>Section 3-1-1-1-1-1</vh>
<v t="ekr.20161124160431.8"><vh>Section 3-1-1-1-1-1</vh>
<v t="ekr.20161124160431.9"><vh>Section 3-1-1-1-1-1</vh>
<v t="ekr.20161124160431.10"><vh>Section 3-1-1-1-1-1</vh>
<v t="ekr.20161124160431.11"><vh>Section 3-1-1-1-1-1</vh></v>
</v>
</v>
</v>
</v>
<v t="ekr.20161124160431.12"><vh>Section 3.1</vh></v>
</v>
</v>
<v t="ekr.20161124160840.1"><vh>@@auto-org c:/leo.repo/leo-editor/leo/plugins/org-placeholder</vh>
<v t="ekr.20161124160840.2"><vh>Section 1</vh></v>
<v t="ekr.20161124160840.3"><vh>Section 2</vh>
<v t="ekr.20161124160840.4"><vh>Section 2-1</vh>
<v t="ekr.20161124160840.5"><vh>Section 2-1-1</vh></v>
</v>
</v>
<v t="ekr.20161124160840.6"><vh>Section 3</vh>
<v t="ekr.20161124160840.7"><vh>Section 3-1-1-1-1-1</vh>
<v t="ekr.20161124160840.8"><vh>Section 3-1-1-1-1-1</vh>
<v t="ekr.20161124160840.9"><vh>Section 3-1-1-1-1-1</vh>
<v t="ekr.20161124160840.10"><vh>Section 3-1-1-1-1-1</vh>
<v t="ekr.20161124160840.11"><vh>Section 3-1-1-1-1-1</vh></v>
</v>
</v>
</v>
</v>
<v t="ekr.20161124160840.12"><vh>Section 3.1</vh></v>
</v>
</v>
<v t="ekr.20161124185724.1"><vh>@@auto-org c:/leo.repo/leo-editor/leo/plugins/org-placeholder</vh>
<v t="ekr.20161124185724.2"><vh>Section 1</vh></v>
<v t="ekr.20161124185724.3"><vh>Section 2</vh>
<v t="ekr.20161124185724.4"><vh>Section 2-1</vh>
<v t="ekr.20161124185724.5"><vh>Section 2-1-1</vh></v>
</v>
</v>
<v t="ekr.20161124185724.6"><vh>Section 3</vh>
<v t="ekr.20161124185724.7"><vh>placeholder</vh>
<v t="ekr.20161124185724.8"><vh>placeholder</vh>
<v t="ekr.20161124185724.9"><vh>placeholder</vh>
<v t="ekr.20161124185724.10"><vh>placeholder</vh>
<v t="ekr.20161124185724.11"><vh>Section 3-1-1-1-1-1</vh></v>
</v>
</v>
</v>
</v>
<v t="ekr.20161124185724.12"><vh>Section 3.1</vh></v>
</v>
</v>
<v t="ekr.20161124185947.1"><vh>@@auto-org c:/leo.repo/leo-editor/leo/plugins/org-placeholder</vh>
<v t="ekr.20161124185947.2"><vh>Section 1</vh></v>
<v t="ekr.20161124185947.3"><vh>Section 2</vh>
<v t="ekr.20161124185947.4"><vh>Section 2-1</vh>
<v t="ekr.20161124185947.5"><vh>Section 2-1-1</vh></v>
</v>
</v>
<v t="ekr.20161124185947.6"><vh>Section 3</vh>
<v t="ekr.20161124185947.7"><vh>placeholder</vh>
<v t="ekr.20161124185947.8"><vh>placeholder</vh>
<v t="ekr.20161124185947.9"><vh>placeholder</vh>
<v t="ekr.20161124185947.10"><vh>placeholder</vh>
<v t="ekr.20161124185947.11"><vh>Section 3-1-1-1-1-1</vh></v>
</v>
</v>
</v>
</v>
<v t="ekr.20161124185947.12"><vh>Section 3.1</vh></v>
</v>
</v>
<v t="ekr.20161124190118.1"><vh>@@auto-org c:/leo.repo/leo-editor/leo/plugins/org-placeholder</vh>
<v t="ekr.20161124190118.2"><vh>Section 1</vh></v>
<v t="ekr.20161124190118.3"><vh>Section 2</vh>
<v t="ekr.20161124190118.4"><vh>Section 2-1</vh>
<v t="ekr.20161124190118.5"><vh>Section 2-1-1</vh></v>
</v>
</v>
<v t="ekr.20161124190118.6"><vh>Section 3</vh>
<v t="ekr.20161124190118.7"><vh>placeholder</vh>
<v t="ekr.20161124190118.8"><vh>placeholder</vh>
<v t="ekr.20161124190118.9"><vh>placeholder</vh>
<v t="ekr.20161124190118.10"><vh>placeholder</vh>
<v t="ekr.20161124190118.11"><vh>Section 3-1-1-1-1-1</vh></v>
</v>
</v>
</v>
</v>
<v t="ekr.20161124190118.12"><vh>Section 3.1</vh></v>
</v>
</v>
<v t="ekr.20161124190228.1"><vh>@@auto-org c:/leo.repo/leo-editor/leo/plugins/org-placeholder</vh>
<v t="ekr.20161124190228.2"><vh>Section 1</vh></v>
<v t="ekr.20161124190228.3"><vh>Section 2</vh>
<v t="ekr.20161124190228.4"><vh>Section 2-1</vh>
<v t="ekr.20161124190228.5"><vh>Section 2-1-1</vh></v>
</v>
</v>
<v t="ekr.20161124190228.6"><vh>Section 3</vh>
<v t="ekr.20161124190228.7"><vh>placeholder</vh>
<v t="ekr.20161124190228.8"><vh>placeholder</vh>
<v t="ekr.20161124190228.9"><vh>placeholder</vh>
<v t="ekr.20161124190228.10"><vh>placeholder</vh>
<v t="ekr.20161124190228.11"><vh>Section 3-1-1-1-1-1</vh></v>
</v>
</v>
</v>
</v>
<v t="ekr.20161124190228.12"><vh>Section 3.1</vh></v>
</v>
</v>
<v t="ekr.20161124190243.1"><vh>@@auto-org c:/leo.repo/leo-editor/leo/plugins/org-placeholder</vh>
<v t="ekr.20161124190243.2"><vh>Section 1</vh></v>
<v t="ekr.20161124190243.3"><vh>Section 2</vh>
<v t="ekr.20161124190243.4"><vh>Section 2-1</vh>
<v t="ekr.20161124190243.5"><vh>Section 2-1-1</vh></v>
</v>
</v>
<v t="ekr.20161124190243.6"><vh>Section 3</vh>
<v t="ekr.20161124190243.7"><vh>placeholder</vh>
<v t="ekr.20161124190243.8"><vh>placeholder</vh>
<v t="ekr.20161124190243.9"><vh>placeholder</vh>
<v t="ekr.20161124190243.10"><vh>placeholder</vh>
<v t="ekr.20161124190243.11"><vh>Section 3-1-1-1-1-1</vh></v>
</v>
</v>
</v>
</v>
<v t="ekr.20161124190243.12"><vh>Section 3.1</vh></v>
</v>
</v>
<v t="ekr.20161125065549.1"><vh>@@auto-org-mode c:/leo.repo/leo-editor/leo/plugins/org-placeholder</vh>
<v t="ekr.20161125065549.2"><vh>Section 1</vh></v>
<v t="ekr.20161125065549.3"><vh>Section 2</vh>
<v t="ekr.20161125065549.4"><vh>Section 2-1</vh>
<v t="ekr.20161125065549.5"><vh>Section 2-1-1</vh></v>
</v>
</v>
<v t="ekr.20161125065549.6"><vh>Section 3</vh>
<v t="ekr.20161125065549.7"><vh>placeholder</vh>
<v t="ekr.20161125065549.8"><vh>placeholder</vh>
<v t="ekr.20161125065549.9"><vh>placeholder</vh>
<v t="ekr.20161125065549.10"><vh>placeholder</vh>
<v t="ekr.20161125065549.11"><vh>Section 3-1-1-1-1-1</vh></v>
</v>
</v>
</v>
</v>
<v t="ekr.20161125065549.12"><vh>Section 3.1</vh></v>
</v>
</v>
<v t="ekr.20161125065725.1"><vh>@@auto-org-mode c:/leo.repo/leo-editor/leo/plugins/org-placeholder</vh>
<v t="ekr.20161125065725.2"><vh>Section 1</vh></v>
<v t="ekr.20161125065725.3"><vh>Section 2</vh>
<v t="ekr.20161125065725.4"><vh>Section 2-1</vh>
<v t="ekr.20161125065725.5"><vh>Section 2-1-1</vh></v>
</v>
</v>
<v t="ekr.20161125065725.6"><vh>Section 3</vh>
<v t="ekr.20161125065725.7"><vh>placeholder</vh>
<v t="ekr.20161125065725.8"><vh>placeholder</vh>
<v t="ekr.20161125065725.9"><vh>placeholder</vh>
<v t="ekr.20161125065725.10"><vh>placeholder</vh>
<v t="ekr.20161125065725.11"><vh>Section 3-1-1-1-1-1</vh></v>
</v>
</v>
</v>
</v>
<v t="ekr.20161125065725.12"><vh>Section 3.1</vh></v>
</v>
</v>
<v t="ekr.20161125065851.1"><vh>@@auto-org-mode c:/leo.repo/leo-editor/leo/plugins/org-placeholder</vh>
<v t="ekr.20161125065851.2"><vh>Section 1</vh></v>
<v t="ekr.20161125065851.3"><vh>Section 2</vh>
<v t="ekr.20161125065851.4"><vh>Section 2-1</vh>
<v t="ekr.20161125065851.5"><vh>Section 2-1-1</vh></v>
</v>
</v>
<v t="ekr.20161125065851.6"><vh>Section 3</vh>
<v t="ekr.20161125065851.7"><vh>placeholder</vh>
<v t="ekr.20161125065851.8"><vh>placeholder</vh>
<v t="ekr.20161125065851.9"><vh>placeholder</vh>
<v t="ekr.20161125065851.10"><vh>placeholder</vh>
<v t="ekr.20161125065851.11"><vh>Section 3-1-1-1-1-1</vh></v>
</v>
</v>
</v>
</v>
<v t="ekr.20161125065851.12"><vh>Section 3.1</vh></v>
</v>
</v>
<v t="ekr.20161125070122.1"><vh>@@auto-org-mode c:/leo.repo/leo-editor/leo/plugins/org-placeholder</vh>
<v t="ekr.20161125070122.2"><vh>Section 1</vh></v>
<v t="ekr.20161125070122.3"><vh>Section 2</vh>
<v t="ekr.20161125070122.4"><vh>Section 2-1</vh>
<v t="ekr.20161125070122.5"><vh>Section 2-1-1</vh></v>
</v>
</v>
<v t="ekr.20161125070122.6"><vh>Section 3</vh>
<v t="ekr.20161125070122.7"><vh>placeholder</vh>
<v t="ekr.20161125070122.8"><vh>placeholder</vh>
<v t="ekr.20161125070122.9"><vh>placeholder</vh>
<v t="ekr.20161125070122.10"><vh>placeholder</vh>
<v t="ekr.20161125070122.11"><vh>Section 3-1-1-1-1-1</vh></v>
</v>
</v>
</v>
</v>
<v t="ekr.20161125070122.12"><vh>Section 3.1</vh></v>
</v>
</v>
<v t="ekr.20161125070244.1"><vh>@@auto-org-mode c:/leo.repo/leo-editor/leo/plugins/org-placeholder</vh>
<v t="ekr.20161125070244.2"><vh>Section 1</vh></v>
<v t="ekr.20161125070244.3"><vh>Section 2</vh>
<v t="ekr.20161125070244.4"><vh>Section 2-1</vh>
<v t="ekr.20161125070244.5"><vh>Section 2-1-1</vh></v>
</v>
</v>
<v t="ekr.20161125070244.6"><vh>Section 3</vh>
<v t="ekr.20161125070244.7"><vh>placeholder</vh>
<v t="ekr.20161125070244.8"><vh>placeholder</vh>
<v t="ekr.20161125070244.9"><vh>placeholder</vh>
<v t="ekr.20161125070244.10"><vh>placeholder</vh>
<v t="ekr.20161125070244.11"><vh>Section 3-1-1-1-1-1</vh></v>
</v>
</v>
</v>
</v>
<v t="ekr.20161125070244.12"><vh>Section 3.1</vh></v>
</v>
</v>
<v t="ekr.20161125070315.1"><vh>@@auto-org-mode c:/leo.repo/leo-editor/leo/plugins/org-placeholder</vh>
<v t="ekr.20161125070315.2"><vh>Section 1</vh></v>
<v t="ekr.20161125070315.3"><vh>Section 2</vh>
<v t="ekr.20161125070315.4"><vh>Section 2-1</vh>
<v t="ekr.20161125070315.5"><vh>Section 2-1-1</vh></v>
</v>
</v>
<v t="ekr.20161125070315.6"><vh>Section 3</vh>
<v t="ekr.20161125070315.7"><vh>placeholder</vh>
<v t="ekr.20161125070315.8"><vh>placeholder</vh>
<v t="ekr.20161125070315.9"><vh>placeholder</vh>
<v t="ekr.20161125070315.10"><vh>placeholder</vh>
<v t="ekr.20161125070315.11"><vh>Section 3-1-1-1-1-1</vh></v>
</v>
</v>
</v>
</v>
<v t="ekr.20161125070315.12"><vh>Section 3.1</vh></v>
</v>
</v>
<v t="ekr.20161125070422.1"><vh>@@auto-org-mode c:/leo.repo/leo-editor/leo/plugins/org-placeholder</vh>
<v t="ekr.20161125070422.2"><vh>Section 1</vh></v>
<v t="ekr.20161125070422.3"><vh>Section 2</vh>
<v t="ekr.20161125070422.4"><vh>Section 2-1</vh>
<v t="ekr.20161125070422.5"><vh>Section 2-1-1</vh></v>
</v>
</v>
<v t="ekr.20161125070422.6"><vh>Section 3</vh>
<v t="ekr.20161125070422.7"><vh>placeholder</vh>
<v t="ekr.20161125070422.8"><vh>placeholder</vh>
<v t="ekr.20161125070422.9"><vh>placeholder</vh>
<v t="ekr.20161125070422.10"><vh>placeholder</vh>
<v t="ekr.20161125070422.11"><vh>Section 3-1-1-1-1-1</vh></v>
</v>
</v>
</v>
</v>
<v t="ekr.20161125070422.12"><vh>Section 3.1</vh></v>
</v>
</v>
<v t="ekr.20161125070847.1"><vh>@@auto-org-mode c:/leo.repo/leo-editor/leo/plugins/org-placeholder</vh>
<v t="ekr.20161125070847.2"><vh>Section 1</vh></v>
<v t="ekr.20161125070847.3"><vh>Section 2</vh>
<v t="ekr.20161125070847.4"><vh>Section 2-1</vh>
<v t="ekr.20161125070847.5"><vh>Section 2-1-1</vh></v>
</v>
</v>
<v t="ekr.20161125070847.6"><vh>Section 3</vh>
<v t="ekr.20161125070847.7"><vh>placeholder</vh>
<v t="ekr.20161125070847.8"><vh>placeholder</vh>
<v t="ekr.20161125070847.9"><vh>placeholder</vh>
<v t="ekr.20161125070847.10"><vh>placeholder</vh>
<v t="ekr.20161125070847.11"><vh>Section 3-1-1-1-1-1</vh></v>
</v>
</v>
</v>
</v>
<v t="ekr.20161125070847.12"><vh>Section 3.1</vh></v>
</v>
</v>
<v t="ekr.20161125071301.1"><vh>@@auto-org-mode c:/leo.repo/leo-editor/leo/plugins/org-placeholder</vh>
<v t="ekr.20161125071301.2"><vh>Section 1</vh></v>
<v t="ekr.20161125071301.3"><vh>Section 2</vh>
<v t="ekr.20161125071301.4"><vh>Section 2-1</vh>
<v t="ekr.20161125071301.5"><vh>Section 2-1-1</vh></v>
</v>
</v>
<v t="ekr.20161125071301.6"><vh>Section 3</vh>
<v t="ekr.20161125071301.7"><vh>placeholder</vh>
<v t="ekr.20161125071301.8"><vh>placeholder</vh>
<v t="ekr.20161125071301.9"><vh>placeholder</vh>
<v t="ekr.20161125071301.10"><vh>placeholder</vh>
<v t="ekr.20161125071301.11"><vh>Section 3-1-1-1-1-1</vh></v>
</v>
</v>
</v>
</v>
<v t="ekr.20161125071301.12"><vh>Section 3.1</vh></v>
</v>
</v>
<v t="ekr.20161125071330.1"><vh>@@auto-org-mode c:/leo.repo/leo-editor/leo/plugins/org-placeholder</vh>
<v t="ekr.20161125071330.2"><vh>Section 1</vh></v>
<v t="ekr.20161125071330.3"><vh>Section 2</vh>
<v t="ekr.20161125071330.4"><vh>Section 2-1</vh>
<v t="ekr.20161125071330.5"><vh>Section 2-1-1</vh></v>
</v>
</v>
<v t="ekr.20161125071330.6"><vh>Section 3</vh>
<v t="ekr.20161125071330.7"><vh>placeholder</vh>
<v t="ekr.20161125071330.8"><vh>placeholder</vh>
<v t="ekr.20161125071330.9"><vh>placeholder</vh>
<v t="ekr.20161125071330.10"><vh>placeholder</vh>
<v t="ekr.20161125071330.11"><vh>Section 3-1-1-1-1-1</vh></v>
</v>
</v>
</v>
</v>
<v t="ekr.20161125071330.12"><vh>Section 3.1</vh></v>
</v>
</v>
<v t="ekr.20161125071430.1"><vh>@@auto-org-mode c:/leo.repo/leo-editor/leo/plugins/org-placeholder</vh>
<v t="ekr.20161125071430.2"><vh>Section 1</vh></v>
<v t="ekr.20161125071430.3"><vh>Section 2</vh>
<v t="ekr.20161125071430.4"><vh>Section 2-1</vh>
<v t="ekr.20161125071430.5"><vh>Section 2-1-1</vh></v>
</v>
</v>
<v t="ekr.20161125071430.6"><vh>Section 3</vh>
<v t="ekr.20161125071430.7"><vh>placeholder</vh>
<v t="ekr.20161125071430.8"><vh>placeholder</vh>
<v t="ekr.20161125071430.9"><vh>placeholder</vh>
<v t="ekr.20161125071430.10"><vh>placeholder</vh>
<v t="ekr.20161125071430.11"><vh>Section 3-1-1-1-1-1</vh></v>
</v>
</v>
</v>
</v>
<v t="ekr.20161125071430.12"><vh>Section 3.1</vh></v>
</v>
</v>
<v t="ekr.20161125073257.1"><vh>@@auto-org-mode c:/leo.repo/leo-editor/leo/plugins/org-placeholder</vh>
<v t="ekr.20161125073257.2"><vh>Section 1</vh></v>
<v t="ekr.20161125073257.3"><vh>Section 2</vh>
<v t="ekr.20161125073257.4"><vh>Section 2-1</vh>
<v t="ekr.20161125073257.5"><vh>Section 2-1-1</vh></v>
</v>
</v>
<v t="ekr.20161125073257.6"><vh>Section 3</vh>
<v t="ekr.20161125073257.7"><vh>placeholder</vh>
<v t="ekr.20161125073257.8"><vh>placeholder</vh>
<v t="ekr.20161125073257.9"><vh>placeholder</vh>
<v t="ekr.20161125073257.10"><vh>placeholder</vh>
<v t="ekr.20161125073257.11"><vh>Section 3-1-1-1-1-1</vh></v>
</v>
</v>
</v>
</v>
<v t="ekr.20161125073257.12"><vh>Section 3.1</vh></v>
</v>
</v>
<v t="ekr.20161125073426.1"><vh>@@auto-org-mode c:/leo.repo/leo-editor/leo/plugins/org-placeholder</vh>
<v t="ekr.20161125073426.2"><vh>Section 1</vh></v>
<v t="ekr.20161125073426.3"><vh>Section 2</vh>
<v t="ekr.20161125073426.4"><vh>Section 2-1</vh>
<v t="ekr.20161125073426.5"><vh>Section 2-1-1</vh></v>
</v>
</v>
<v t="ekr.20161125073426.6"><vh>Section 3</vh>
<v t="ekr.20161125073426.7"><vh>placeholder</vh>
<v t="ekr.20161125073426.8"><vh>placeholder</vh>
<v t="ekr.20161125073426.9"><vh>placeholder</vh>
<v t="ekr.20161125073426.10"><vh>placeholder</vh>
<v t="ekr.20161125073426.11"><vh>Section 3-1-1-1-1-1</vh></v>
</v>
</v>
</v>
</v>
<v t="ekr.20161125073426.12"><vh>Section 3.1</vh></v>
</v>
</v>
</v>
</v>
<v t="ekr.20161124154051.1"><vh>otl</vh>
<v t="ekr.20161124035818.1"><vh>@test otl (vim-outline) mode</vh></v>
<v t="ekr.20161124035818.1"></v>
<v t="ekr.20161124042619.1"><vh>@test otl-1</vh>
<v t="ekr.20161124083517.1"><vh>@@auto-vim-outline c:/leo.repo/leo-editor/leo/plugins/otl-1</vh>
<v t="ekr.20161124083517.2"><vh>Section 1</vh></v>
<v t="ekr.20161124083517.3"><vh>Section 2</vh>
<v t="ekr.20161124083517.4"><vh>Section 2-1</vh>
<v t="ekr.20161124083517.5"><vh>Section 2-1-1</vh></v>
</v>
</v>
<v t="ekr.20161124083517.6"><vh>Section 3</vh>
<v t="ekr.20161124083517.7"><vh>Section 3.1</vh></v>
</v>
</v>
<v t="ekr.20161124083531.1"><vh>@@auto-vim-outline c:/leo.repo/leo-editor/leo/plugins/otl-1</vh>
<v t="ekr.20161124083531.2"><vh></vh></v>
<v t="ekr.20161124083531.3"><vh>Section 1</vh></v>
<v t="ekr.20161124083531.4"><vh>Section 2</vh>
<v t="ekr.20161124083531.5"><vh>Section 2-1</vh>
<v t="ekr.20161124083531.6"><vh>Section 2-1-1</vh></v>
</v>
</v>
<v t="ekr.20161124083531.7"><vh>Section 3</vh>
<v t="ekr.20161124083531.8"><vh>Section 3.1</vh></v>
</v>
</v>
<v t="ekr.20161124083550.1"><vh>@@auto-vim-outline c:/leo.repo/leo-editor/leo/plugins/otl-1</vh>
<v t="ekr.20161124083550.2"><vh>Section 1</vh></v>
<v t="ekr.20161124083550.3"><vh>Section 2</vh>
<v t="ekr.20161124083550.4"><vh>Section 2-1</vh>
<v t="ekr.20161124083550.5"><vh>Section 2-1-1</vh></v>
</v>
</v>
<v t="ekr.20161124083550.6"><vh>Section 3</vh>
<v t="ekr.20161124083550.7"><vh>Section 3.1</vh></v>
</v>
</v>
</v>
</v>
<v t="ekr.20161127104105.1"><vh>pascal</vh>
<v t="ekr.20161126182933.1"><vh>@test pascal patterns</vh></v>
</v>
<v t="ekr.20161127104048.1"><vh>python</vh>
<v t="ekr.20161117081206.1"><vh>@test python_i.is_decorator</vh></v>
</v>
<v t="ekr.20161124154102.1"><vh>xml</vh>
<v t="ekr.20161122155335.1"><vh>@test xml.is_ws_line</vh></v>
<v t="ekr.20161122123422.1"><vh>@test xml.scan tags</vh></v>
</v>
</v>
<v t="ekr.20161110200245.1"><vh>Experiments</vh>
<v t="ekr.20161110173847.1"><vh>regex experiments</vh>
<v t="ekr.20161110192833.1"><vh>&lt;&lt; old experiments &gt;&gt;</vh></v>
</v>
<v t="ekr.20161110193124.1"><vh>experiment int(bad)</vh></v>
<v t="ekr.20161111021944.1"><vh>experiment: re.escape</vh></v>
<v t="ekr.20161112085333.1"><vh>test: under-indented docstring</vh></v>
<v t="ekr.20161124023807.1"><vh>experiment: lstrip</vh></v>
<v t="ekr.20161124122942.1"><vh>test substitution</vh></v>
<v t="ekr.20161126051659.1"><vh>test s.splitlines</vh></v>
</v>
<v t="ekr.20161129041539.1"><vh>@test leo_rst</vh></v>
</v>
<v t="ekr.20161130054748.1"><vh>----- ctext stuff</vh>
<v t="tbrown.20140804103545.29975"></v>
<v t="tbrown.20140801105909.47549"></v>
<v t="ekr.20161130053858.1"><vh>at-auto-ctext-test.txt</vh></v>
</v>
<v t="ekr.20161129115318.1"><vh>----- rst stuff</vh>
<v t="ekr.20140723122936.18099"><vh>OLD class RstScanner</vh>
<v t="ekr.20140723122936.18100"><vh> __init__ (RstScanner)</vh></v>
<v t="ekr.20140723122936.18101"><vh>adjustParent (RstScanner)</vh></v>
<v t="ekr.20140723122936.18102"><vh>computeBody (RstScanner)</vh></v>
<v t="ekr.20140723122936.18103"><vh>computeSectionLevel</vh></v>
<v t="ekr.20140723122936.18104"><vh>createDeclsNode (RstScanner)</vh></v>
<v t="ekr.20140723122936.18105"><vh>endGen (RstScanner)</vh></v>
<v t="ekr.20140723122936.18106"><vh>isUnderLine</vh></v>
<v t="ekr.20140723122936.18107"><vh>startsComment/ID/String</vh></v>
<v t="ekr.20140723122936.18108"><vh>startsHelper (RstScanner)</vh></v>
<v t="ekr.20140723122936.18109"><vh>startsSection &amp; helper</vh>
<v t="ekr.20140723122936.18110"><vh>getLine</vh></v>
</v>
</v>
<v t="ekr.20161129043705.1"><vh>OLD startsSection &amp; helper</vh>
<v t="ekr.20161129043705.2"><vh>getLine</vh></v>
</v>
<v t="ekr.20161129041436.1"><vh>COPY at-auto-rst-line-number-test.py</vh></v>
<v t="ekr.20161130060355.1"><vh>COPY @file writers/leo_rst.py</vh>
<v t="ekr.20161130060355.2"><vh>class RstWriter</vh>
<v t="ekr.20161130060355.3"><vh>rstw.underline_char</vh></v>
<v t="ekr.20161130060355.4"><vh>rstw.write</vh></v>
</v>
</v>
<v t="ekr.20161130060525.1"><vh>at-auto-rst-line-number-test.py</vh></v>
</v>
</v>
<v t="ekr.20161202063728.1"><vh>Recent files</vh>
<v t="ekr.20140723122936.18151"></v>
<v t="ekr.20140726091031.18143"></v>
<v t="ekr.20140726091031.18080"></v>
<v t="ekr.20140723122936.17925"></v>
<v t="ekr.20140726091031.18071"></v>
</v>
<v t="ekr.20161029115236.1"><vh>----- To do</vh>
<v t="ekr.20161123091527.1"><vh>Testing</vh></v>
<v t="ekr.20161123091556.1"><vh>Last</vh></v>
<v t="ekr.20161127183204.1"><vh>Post: kinds of importers</vh></v>
</v>
<v t="ekr.20161108155730.1"><vh>class Importer</vh>
<v t="ekr.20161108155925.1"><vh>i.__init__</vh></v>
<v t="ekr.20161110042512.1"><vh>i.API for setting body text</vh></v>
<v t="ekr.20161108131153.3"><vh>i.check &amp; helpers</vh>
<v t="ekr.20161108131153.4"><vh>i.clean_blank_lines</vh></v>
<v t="ekr.20161124030004.1"><vh>i.clean_last_lines</vh></v>
<v t="ekr.20161125031613.1"><vh>i.show_failure1</vh></v>
<v t="ekr.20161123210716.1"><vh>i.show_failure2</vh></v>
<v t="ekr.20161108131153.5"><vh>i.strip_*</vh></v>
<v t="ekr.20161123210335.1"><vh>i.trace_lines</vh></v>
<v t="ekr.20161108131153.6"><vh>i.trial_write</vh></v>
</v>
<v t="ekr.20161108131153.7"><vh>i.Overrides</vh>
<v t="ekr.20161108131153.8"><vh>i.adjust_parent</vh></v>
<v t="ekr.20161108131153.9"><vh>i.clean_headline</vh></v>
<v t="ekr.20161110173058.1"><vh>i.clean_nodes</vh></v>
</v>
<v t="ekr.20161120022121.1"><vh>i.Scanning &amp; scan tables</vh>
<v t="ekr.20161128190217.1"><vh>i. to be retired</vh>
<v t="ekr.20161113135037.1"><vh>i.get_table</vh></v>
<v t="ekr.20161113052225.1"><vh>i.scan_table</vh></v>
</v>
<v t="ekr.20161128025508.1"><vh>i.get_new_dict</vh></v>
<v t="ekr.20161128025444.1"><vh>i.scan_dict</vh></v>
<v t="ekr.20161114024119.1"></v>
<v t="ekr.20161108170435.1"><vh>i.scan_line</vh></v>
</v>
<v t="ekr.20161108165530.1"><vh>i.Top level</vh>
<v t="ekr.20161111024447.1"><vh>i.generate_nodes &amp; helpers</vh>
<v t="ekr.20161108160409.1"><vh>Stage 1: i.gen_lines &amp; helpers</vh>
<v t="ekr.20161127102339.1"><vh>i.ends_block</vh></v>
<v t="ekr.20161119130337.1"><vh>i.cut_stack</vh></v>
<v t="ekr.20161108160409.3"><vh>i.end_block</vh></v>
<v t="ekr.20161110041440.1"><vh>i.inject_lines_ivar</vh></v>
<v t="ekr.20161108160409.6"><vh>i.start_new_block</vh></v>
<v t="ekr.20161119124217.1"><vh>i.starts_block</vh></v>
<v t="ekr.20161119162451.1"><vh>i.trace_status</vh></v>
<v t="ekr.20161108160409.7"><vh>i.create_child_node</vh></v>
<v t="ekr.20161108160409.8"><vh>i.gen_ref</vh></v>
</v>
<v t="ekr.20161108131153.13"><vh>Stage 2: i.post_pass &amp; helpers</vh>
<v t="ekr.20161110125940.1"><vh>i.clean_all_headlines</vh></v>
<v t="ekr.20161110130157.1"><vh>i.clean_all_nodes</vh></v>
<v t="ekr.20161110130709.1"><vh>i.delete_all_empty_nodes</vh></v>
<v t="ekr.20161110131509.1"><vh>i.promote_trailing_underindented_lines</vh></v>
<v t="ekr.20161110130337.1"><vh>i.unindent_all_nodes</vh></v>
</v>
<v t="ekr.20161111023249.1"><vh>Stage 3: i.finish &amp; helpers</vh>
<v t="ekr.20161108160409.5"><vh>i.add_root_directives</vh></v>
<v t="ekr.20161110042020.1"><vh>i.finalize_ivars</vh></v>
</v>
</v>
<v t="ekr.20161108131153.10"><vh>i.run (entry point) &amp; helpers</vh>
<v t="ekr.20161108131153.11"><vh>i.check_blanks_and_tabs</vh></v>
<v t="ekr.20161108131153.12"><vh>i.insert_ignore_directive</vh></v>
<v t="ekr.20161108131153.14"><vh>i.regularize_whitespace</vh></v>
</v>
</v>
<v t="ekr.20161108131153.15"><vh>i.Utils</vh>
<v t="ekr.20161114012522.1"><vh>i.all_contexts</vh></v>
<v t="ekr.20161108155143.4"><vh>i.match</vh></v>
<v t="ekr.20161108131153.18"><vh>i.Messages</vh></v>
<v t="ekr.20161109045619.1"><vh>i.print_lines</vh></v>
<v t="ekr.20161125174423.1"><vh>i.print_stack</vh></v>
<v t="ekr.20161108131153.21"><vh>i.underindented_comment/line</vh></v>
</v>
<v t="ekr.20161109045312.1"><vh>i.Whitespace</vh>
<v t="ekr.20161108155143.3"><vh>i.get_int_lws</vh></v>
<v t="ekr.20161109053143.1"><vh>i.get_leading_indent</vh></v>
<v t="ekr.20161108131153.17"><vh>i.get_str_lws</vh></v>
<v t="ekr.20161109052011.1"><vh>i.is_ws_line</vh></v>
<v t="ekr.20161108131153.19"><vh>i.undent &amp; helper</vh>
<v t="ekr.20161108131153.20"><vh>i.common_lws</vh></v>
</v>
<v t="ekr.20161109072221.1"><vh>i.undent_body_lines &amp; helper</vh>
<v t="ekr.20161108180655.2"><vh>i.undent_by</vh></v>
</v>
</v>
</v>
<v t="ekr.20161127192007.2"><vh>class Rst_Importer</vh>
<v t="ekr.20161129040921.2"><vh>rst_i.gen_lines &amp; helpers</vh>
<v t="ekr.20161129040921.5"><vh>rst_i.find_parent</vh></v>
<v t="ekr.20161129111503.1"><vh>rst_i.is_lookahead_overline</vh></v>
<v t="ekr.20161129112703.1"><vh>rst_i.is_lookahead_underline</vh></v>
<v t="ekr.20161129040921.8"><vh>rst_i.is_underline</vh></v>
<v t="ekr.20161129040921.6"><vh>rst_i.make_dummy_node</vh></v>
<v t="ekr.20161129040921.7"><vh>rst_i.make_node</vh></v>
<v t="ekr.20161129045020.1"><vh>rst_i.ch_level</vh></v>
</v>
<v t="ekr.20161129040921.11"><vh>rst_i.post_pass</vh></v>
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
<t tx="edream.110203113231.618" _bklnk="7d71002858010000007871014b0058050000006c696e6b7371025d710358010000007971044b00580400000074797065710558080000006e6f6465526563747106752e">@language python
@tabwidth -4
@pagewidth 80

@nosearch</t>
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
</t>
<t tx="ekr.20140723122936.18083">class PhpScanner(basescanner.BaseScanner):
    @others
</t>
<t tx="ekr.20140723122936.18084">def __init__(self, importCommands, atAuto):
    # Init the base class.
    basescanner.BaseScanner.__init__(self, importCommands, atAuto=atAuto, language='php')
    # Set the parser delims.
    self.blockCommentDelim1 = '/*'
    self.blockCommentDelim2 = '*/'
    self.lineCommentDelim = '//'
    self.lineCommentDelim2 = '#'
    self.blockDelim1 = '{'
    self.blockDelim2 = '}'
    self.hasClasses = True # 2010/02/19
    self.hasFunctions = True
    self.functionTags = ['function']
    # The valid characters in an id
    self.chars = list(string.ascii_letters + string.digits)
    extra = [chr(z) for z in range(127, 256)]
    self.chars.extend(extra)
</t>
<t tx="ekr.20140723122936.18085">def isPurePHP(self, s):
    '''Return True if the file begins with &lt;?php and ends with ?&gt;'''
    s = s.strip()
    return (
        s.startswith('&lt;?') and
        s[2: 3] in ('P', 'p', '=', '\n', '\r', ' ', '\t') and
        s.endswith('?&gt;'))
</t>
<t tx="ekr.20140723122936.18086"># Does not create @first/@last nodes
</t>
<t tx="ekr.20140723122936.18087">def startsString(self, s, i):
    return g.match(s, i, '"') or g.match(s, i, "'") or g.match(s, i, '&lt;&lt;&lt;')

def skipString(self, s, i):
    if g.match(s, i, '"') or g.match(s, i, "'"):
        return g.skip_string(s, i)
    else:
        return g.skip_heredoc_string(s, i)
</t>
<t tx="ekr.20140723122936.18088">def getSigId(self, ids):
    '''Return the signature's id.

    By default, this is the last id in the ids list.

    For Php, the first id is better.'''
    return ids and ids[1]
</t>
<t tx="ekr.20140723122936.18099">class RstScanner(basescanner.BaseScanner):
    @others
</t>
<t tx="ekr.20140723122936.18100">def __init__(self, importCommands, atAuto):
    # Init the base class.
    basescanner.BaseScanner.__init__(self, importCommands, atAuto=atAuto, language='rest')
    # Scanner overrides
    self.atAutoWarnsAboutLeadingWhitespace = True
    self.blockDelim1 = self.blockDelim2 = None
    self.classTags = []
    self.escapeSectionRefs = False
    self.functionSpelling = 'section'
    self.functionTags = []
    self.hasClasses = False
    self.ignoreBlankLines = True
    self.isRst = True
    self.lineCommentDelim = '..'
    self.outerBlockDelim1 = None
    self.sigFailTokens = []
    self.strict = False # Mismatches in leading whitespace are irrelevant.
    # Ivars unique to rst scanning &amp; code generation.
    self.lastParent = None # The previous parent.
    self.lastSectionLevel = 0 # The section level of previous section.
    self.sectionLevel = 0 # The section level of the just-parsed section.
    self.underlineCh = '' # The underlining character of the last-parsed section.
    self.underlines = "!\"#$%&amp;'()*+,-./:;&lt;=&gt;?@[\\]^_`{|}~" # valid rst underlines.
    self.underlines1 = [] # Underlining characters for underlines.
    self.underlines2 = [] # Underlining characters for over/underlines.
</t>
<t tx="ekr.20140723122936.18101">def adjustParent(self, parent, headline):
    '''Return the proper parent of the new node.'''
    trace = False and not g.unitTesting
    level, lastLevel = self.sectionLevel, self.lastSectionLevel
    lastParent = self.lastParent
    if trace: g.trace('**entry level: %s lastLevel: %s lastParent: %s' % (
        level, lastLevel, lastParent and lastParent.h or '&lt;none&gt;'))
    if self.lastParent:
        if level &lt;= lastLevel:
            parent = lastParent.parent()
            while level &lt; lastLevel:
                level += 1
                parent = parent.parent()
        else: # level &gt; lastLevel.
            level -= 1
            parent = lastParent
            while level &gt; lastLevel:
                level -= 1
                h2 = '@rst-no-head %s' % headline
                body = ''
                parent = self.createFunctionNode(h2, body, parent)
    else:
        assert self.root
        self.lastParent = self.root
    if not parent:
        parent = self.root
    if trace: g.trace('level %s lastLevel %s %s returns %s' % (
        level, lastLevel, headline, parent.h))
    #self.lastSectionLevel = self.sectionLevel
    self.lastParent = parent.copy()
    return parent.copy()
</t>
<t tx="ekr.20140723122936.18102">def computeBody(self, s, start, sigStart, codeEnd):
    '''Compute the body of an rst node.'''
    trace = False and not g.unitTesting
    body1 = s[start: sigStart]
    # Adjust start backwards to get a better undent.
    if body1.strip():
        while start &gt; 0 and s[start - 1] in (' ', '\t'):
            start -= 1
    # Never indent any text; discard the entire signature.
    body1 = s[start: sigStart]
    body2 = s[self.sigEnd + 1: codeEnd]
    body2 = g.removeLeadingBlankLines(body2) # 2009/12/28
    body = body1 + body2
    # Don't warn about missing tail newlines: they will be added.
    if trace: g.trace('body: %s' % repr(body))
    return body1, body2
</t>
<t tx="ekr.20140723122936.18103">def computeSectionLevel(self, ch, kind):
    '''Return the section level of the underlining character ch.'''
    if kind == 'over':
        assert ch in self.underlines2
        level = 0
    else:
        level = 1 + self.underlines1.index(ch)
    if 0:
        g.trace('level: %s kind: %s ch: %s under2: %s under1: %s' % (
            level, kind, ch, self.underlines2, self.underlines1))
    return level
</t>
<t tx="ekr.20140723122936.18104">def createDeclsNode(self, parent, s):
    '''Create a child node of parent containing s.'''
    # Create the node for the decls.
    headline = '@rst-no-head %s declarations' % self.methodName
    body = self.undentBody(s)
    self.createHeadline(parent, body, headline)
</t>
<t tx="ekr.20140723122936.18105">def endGen(self, s):
    '''Remember the underlining characters in the root's uA.'''
    trace = False and not g.unitTesting
    p = self.root
    if p:
        tag = 'rst-import'
        d = p.v.u.get(tag, {})
        underlines1 = ''.join([str(z) for z in self.underlines1])
        underlines2 = ''.join([str(z) for z in self.underlines2])
        d['underlines1'] = underlines1
        d['underlines2'] = underlines2
        self.underlines1 = underlines1
        self.underlines2 = underlines2
        if trace: g.trace(repr(underlines1), repr(underlines2), g.callers(4))
        p.v.u[tag] = d
    # Append a warning to the root node.
    warningLines = (
        'Warning: this node is ignored when writing this file.',
        'However, @ @rst-options are recognized in this node.',
    )
    lines = ['.. %s' % (z) for z in warningLines]
    warning = '\n%s\n' % '\n'.join(lines)
    self.root.b = self.root.b + warning
</t>
<t tx="ekr.20140723122936.18106">def isUnderLine(self, s):
    '''Return True if s consists of only the same rST underline character.'''
    if not s: return False
    ch1 = s[0]
    if ch1 not in self.underlines:
        return False
    for ch in s:
        if ch != ch1:
            return False
    return True
</t>
<t tx="ekr.20140723122936.18107"># These do not affect parsing.

def startsComment(self, s, i):
    return False

def startsID(self, s, i):
    return False

def startsString(self, s, i):
    return False
</t>
<t tx="ekr.20140723122936.18108">def startsHelper(self, s, i, kind, tags, tag=None):
    '''return True if s[i:] starts an rST section.
    Sets sigStart, sigEnd, sigId and codeEnd ivars.'''
    trace = False and not g.unitTesting
    verbose = True
    kind, name, next, ch = self.startsSection(s, i)
    if kind == 'plain': return False
    self.underlineCh = ch
    self.lastSectionLevel = self.sectionLevel
    self.sectionLevel = self.computeSectionLevel(ch, kind)
    self.sigStart = g.find_line_start(s, i)
    self.sigEnd = next
    self.sigId = name
    i = next + 1
    if trace: g.trace('sigId', self.sigId, 'next', next)
    while i &lt; len(s):
        progress = i
        i, j = g.getLine(s, i)
        kind, name, next, ch = self.startsSection(s, i)
        if trace and verbose: g.trace(kind, repr(s[i: j]))
        if kind in ('over', 'under'):
            break
        else:
            i = j
        assert i &gt; progress
    self.codeEnd = i
    if trace:
        if verbose:
            g.trace('found...\n%s' % s[self.sigStart: self.codeEnd])
        else:
            g.trace('level %s %s' % (self.sectionLevel, self.sigId))
    return True
</t>
<t tx="ekr.20140723122936.18109">def startsSection(self, s, i):
    '''Scan a line and possible one or two other lines,
    looking for an underlined or overlined/underlined name.

    Return (kind,name,i):
        kind: in ('under','over','plain')
        name: the name of the underlined or overlined line.
        i: the following character if kind is not 'plain'
        ch: the underlining and possibly overlining character.
    '''
    trace = False and not g.unitTesting
    verbose = False
    # Under/overlines can not begin with whitespace.
    i1, j, nows, line = self.getLine(s, i)
    ch, kind = '', 'plain' # defaults.
    if nows and self.isUnderLine(line): # an overline.
        name_i = g.skip_line(s, i1)
        name_i, name_j = g.getLine(s, name_i)
        name = s[name_i: name_j].strip()
        next_i = g.skip_line(s, name_i)
        i, j, nows, line2 = self.getLine(s, next_i)
        n1, n2, n3 = len(line), len(name), len(line2)
        ch1, ch3 = line[0], line2 and line2[0]
        ok = (nows and self.isUnderLine(line2) and
            n1 &gt;= n2 and n2 &gt; 0 and n3 &gt;= n2 and ch1 == ch3)
        if ok:
            i += n3
            ch, kind = ch1, 'over'
            if ch1 not in self.underlines2:
                self.underlines2.append(ch1)
                if trace: g.trace('*** underlines2', self.underlines2, name)
            if trace and verbose:
                g.trace('\nline  %s\nname  %s\nline2 %s' % (
                    repr(line), repr(name), repr(line2))) #,'\n',g.callers(4))
    else:
        name = line.strip()
        i = g.skip_line(s, i1)
        i, j, nows2, line2 = self.getLine(s, i)
        n1, n2 = len(name), len(line2)
        # look ahead two lines.
        i3, j3 = g.getLine(s, j)
        name2 = s[i3: j3].strip()
        i4, j4, nows4, line4 = self.getLine(s, j3)
        n3, n4 = len(name2), len(line4)
        overline = (
            nows2 and self.isUnderLine(line2) and
            nows4 and self.isUnderLine(line4) and
            n3 &gt; 0 and n2 &gt;= n3 and n4 &gt;= n3)
        ok = (not overline and nows2 and self.isUnderLine(line2) and
            n1 &gt; 0 and n2 &gt;= n1)
        if ok:
            i += n2
            ch, kind = line2[0], 'under'
            if ch not in self.underlines1:
                self.underlines1.append(ch)
                if trace: g.trace('*** underlines1', self.underlines1, name)
            if trace and verbose: g.trace('\nname  %s\nline2 %s' % (
                repr(name), repr(line2)))
    return kind, name, i, ch
</t>
<t tx="ekr.20140723122936.18110">def getLine(self, s, i):
    i, j = g.getLine(s, i)
    line = s[i: j]
    nows = i == g.skip_ws(s, i)
    line = line.strip()
    return i, j, nows, line
</t>
<t tx="ekr.20140726091031.18071"># These plugins now contain the write code for all kinds special @auto nodes.
# Each plugin must define a top-level writer_dict dictionary describing the plugin.
</t>
<t tx="ekr.20160122104302.1">@nosearch</t>
<t tx="ekr.20160122104357.1">run-pylint
beautify-node
beautify-tree
cfa-code
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
<t tx="ekr.20160412101537.3">def __init__(self, c=None, importCommands=None, atAuto=None):
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
<t tx="ekr.20160412103110.1">def run(self, s, parent, parse_body=False, prepass=False):
    '''
    @auto entry point. Called by code in leoImport.py.
    '''
    c = self.c
    fn = parent.atAutoNodeName()
    # g.trace(prepass, fn)
    if c and fn and not prepass:
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
c.backup(path, useTimeStamp=True)
    # Dropbox can show previous versions!
    # But this depends on proxy/firewall settings.
</t>
<t tx="ekr.20161029115236.1">@language rest
@wrap
@nosearch

** When done, remove all v2_ prefixes!
    
Unit tests: Safely delete all but the last test:
- Don't delete any nodes children that look like section references.

C and Java:
- Backtrack to find start of signature line!
  Some headlines are/were None None

Python:
- Rewrite python.findClass.

Later:   see child.
Testing: see child.
Last:    see child.

@language python
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
<t tx="ekr.20161031131716.1">@nosearch</t>
<t tx="ekr.20161108131153.10">def run(self, s, parent, parse_body=False, prepass=False):
    '''The common top-level code for all scanners.'''
    trace = False and g.unitTesting
    if trace: g.trace('='*20, self.name)
    if trace: g.trace('=' * 10, parent.h)
    c = self.c
    if prepass:
        g.trace('(Importer) Can not happen, prepass is True')
        return True, [] # Don't split any nodes.
    self.root = root = parent.copy()
    self.file_s = s
    # Init the error/status info.
    self.errors = 0
    self.parse_body = parse_body
    # Check for intermixed blanks and tabs.
    self.tab_width = c.getTabWidth(p=root)
    ws_ok = self.check_blanks_and_tabs(s) # Only issues warnings.
    # Regularize leading whitespace
    if not ws_ok:
        s = self.regularize_whitespace(s)
    # Generate the nodes, including directives and section references.
    changed = c.isChanged()
    # Completely generate all nodes.
    self.generate_nodes(s, parent)
    # Check the generated nodes.
    # Return True if the result is equivalent to the original file.
    ok = self.errors == 0 and self.check(s, parent)
    g.app.unitTestDict['result'] = ok
    # Insert an @ignore directive if there were any serious problems.
    if not ok:
        self.insert_ignore_directive(parent)
    # It's always useless for an an import to dirty the outline.
    for p in root.self_and_subtree():
        p.clearDirty()
    c.setChanged(changed)
    if trace: g.trace('-' * 10, parent.h)
    return ok
</t>
<t tx="ekr.20161108131153.11">def check_blanks_and_tabs(self, lines):
    '''Check for intermixed blank &amp; tabs.'''
    # Do a quick check for mixed leading tabs/blanks.
    trace = False and not g.unitTesting
    fn = g.shortFileName(self.root.h)
    w = self.tab_width
    blanks = tabs = 0
    for s in g.splitLines(lines):
        lws = self.get_str_lws(s)
        blanks += lws.count(' ')
        tabs += lws.count('\t')
    # Make sure whitespace matches @tabwidth directive.
    if w &lt; 0:
        ok = tabs == 0
        message = 'tabs found with @tabwidth %s in %s' % (w, fn)
    elif w &gt; 0:
        ok = blanks == 0
        message = 'blanks found with @tabwidth %s in %s' % (w, fn)
    if ok:
        ok = blanks == 0 or tabs == 0
        message = 'intermixed blanks and tabs in: %s' % (fn)
    if ok:
        if trace: g.trace('=====', len(lines), blanks, tabs)
    else:
        if g.unitTesting:
            self.report(message)
        else:
            g.es_print(message)
    return ok
</t>
<t tx="ekr.20161108131153.12">def insert_ignore_directive(self, parent):
    c = self.c
    parent.b = parent.b.rstrip() + '\n@ignore\n'
    if g.unitTesting:
        g.app.unitTestDict['fail'] = g.callers()
    elif parent.isAnyAtFileNode() and not parent.isAtAutoNode():
        g.warning('inserting @ignore')
        c.import_error_nodes.append(parent.h)
</t>
<t tx="ekr.20161108131153.13">def post_pass(self, parent):
    '''
    Optional Stage 2 of the importer pipeline, consisting of zero or more
    substages. Each substage alters nodes in various ways.
    
    Subclasses may freely override this method, **provided** that all
    substages use the API for setting body text. Changing p.b directly will
    cause asserts to fail later in i.finish().
    '''
    # g.trace('='*40)
    self.clean_all_headlines(parent)
    self.clean_all_nodes(parent)
    self.unindent_all_nodes(parent)
    #
    # This sub-pass must follow unindent_all_nodes.
    self.promote_trailing_underindented_lines(parent)
    #
    # This probably should be the last sub-pass.
    self.delete_all_empty_nodes(parent)
    
</t>
<t tx="ekr.20161108131153.14">def regularize_whitespace(self, s):
    '''
    Regularize leading whitespace in s:
    Convert tabs to blanks or vice versa depending on the @tabwidth in effect.
    '''
    trace = False and not g.unitTesting
    trace_lines = False
    kind = 'tabs' if self.tab_width &gt; 0 else 'blanks'
    kind2 = 'blanks' if self.tab_width &gt; 0 else 'tabs'
    fn = g.shortFileName(self.root.h)
    lines = g.splitLines(s)
    count, result, tab_width = 0, [], self.tab_width
    self.ws_error = False ### 2016/11/23
    if tab_width &lt; 0: # Convert tabs to blanks.
        for n, line in enumerate(lines):
            i, w = g.skip_leading_ws_with_indent(line, 0, tab_width)
            s = g.computeLeadingWhitespace(w, -abs(tab_width)) + line[i:]
                # Use negative width.
            if s != line:
                count += 1
                if trace and trace_lines:
                    g.es_print('%s: %r\n%s: %r' % (n+1, line, n+1, s))
            result.append(s)
    elif tab_width &gt; 0: # Convert blanks to tabs.
        for n, line in enumerate(lines):
            s = g.optimizeLeadingWhitespace(line, abs(tab_width))
                # Use positive width.
            if s != line:
                count += 1
                if trace and trace_lines:
                    g.es_print('%s: %r\n%s: %r' % (n+1, line, n+1, s))
            result.append(s)
    if count:
        self.ws_error = True # A flag to check.
        if not g.unitTesting:
            # g.es_print('Warning: Intermixed tabs and blanks in', fn)
            # g.es_print('Perfect import test will ignoring leading whitespace.')
            g.es_print('changed leading %s to %s in %s line%s in %s' % (
                kind2, kind, count, g.plural(count), fn))
        if g.unitTesting: # Sets flag for unit tests.
            self.report('changed %s lines' % count) 
    return ''.join(result)
</t>
<t tx="ekr.20161108131153.15"></t>
<t tx="ekr.20161108131153.17">def get_str_lws(self, s):
    '''Return the characters of the lws of s.'''
    m = re.match(r'([ \t]*)', s)
    return m.group(0) if m else ''
</t>
<t tx="ekr.20161108131153.18">def error(self, s):
    '''Issue an error and cause a unit test to fail.'''
    trace = False
    self.errors += 1
    self.importCommands.errors += 1
    if trace or not g.unitTesting:
        g.error('Error:', s)
    # if g.unitTesting:
        # if self.errors == 1:
            # g.app.unitTestDict['actualErrorMessage'] = s
        # g.app.unitTestDict['actualErrors'] = self.errors
    # else:
        # g.error('Error:', s)

def report(self, message):
    if self.strict:
        self.error(message)
    else:
        self.warning(message)

def warning(self, s):
    if not g.unitTesting:
        g.warning('Warning:', s)
</t>
<t tx="ekr.20161108131153.19">def undent(self, p):
    '''Remove maximal leading whitespace from the start of all lines.'''
    trace = False and g.unitTesting
    if self.is_rst:
        return p.b # Never unindent rst code.
    lines = self.get_lines(p)
    ws = self.common_lws(lines)
    if trace:
        g.trace('common_lws:', repr(ws))
        print('===== lines...')
        for z in lines:
            print(repr(z))
    result = []
    for s in lines:
        if s.startswith(ws):
            result.append(s[len(ws):])
        elif s.isspace():
            # Never change blank lines.
            result.append(s)
        else:
            # Indicate that the line is underindented.
            result.append("%s%s.%s" % (
                self.c.atFileCommands.underindentEscapeString,
                g.computeWidth(ws, self.tab_width),
                s.lstrip()))
    if trace:
        print('----- result...')
        for z in result:
            print(repr(z))
    return result
</t>
<t tx="ekr.20161108131153.20">def common_lws(self, lines):
    '''Return the lws (a string) common to all lines.'''
    trace = False and not g.unitTesting # and self.root.h.endswith('.c')
    if not lines:
        return ''
    lws = self.get_str_lws(lines[0])
    for s in lines:
        if not self.is_ws_line(s):
            lws2 = self.get_str_lws(s)
            if lws2.startswith(lws):
                pass
            elif lws.startswith(lws2):
                lws = lws2
            else:
                lws = '' # Nothing in common.
                break
    if trace:
        g.trace(repr(lws))
        self.print_lines(lines)
    return lws
</t>
<t tx="ekr.20161108131153.21">def underindented_comment(self, line):
    if self.at_auto_warns_about_leading_whitespace:
        self.warning(
            'underindented python comments.\n' +
            'Extra leading whitespace will be added\n' + line)

def underindented_line(self, line):
    if self.warn_about_underindented_lines:
        self.error(
            'underindented line.\n'
            'Extra leading whitespace will be added\n' + line)
</t>
<t tx="ekr.20161108131153.3">def check(self, unused_s, parent):
    '''True if perfect import checks pass.'''
    trace = False and g.unitTesting
    trace_all = True
    trace_lines = True
    trace_status = True
    if g.app.suppressImportChecks:
        if trace and trace_status:
            g.trace('===== skipping all checks', parent.h)
        g.app.suppressImportChecks = False
        return True
    c = self.c
    t1 = time.clock()
    sfn = g.shortFileName(self.root.h)
    s1 = g.toUnicode(self.file_s, self.encoding)
    s2 = self.trial_write()
    lines1, lines2 = g.splitLines(s1), g.splitLines(s2)
    if trace and trace_all:
        g.trace('===== entry')
        self.trace_lines(lines1, lines2, parent)
    if self.ws_error:
        if trace and trace_status: g.trace('===== ws_error: cleaning lws')
        lines1, lines2 = self.strip_lws(lines1), self.strip_lws(lines2)
    else:
        lines1, lines2 = self.clean_blank_lines(lines1), self.clean_blank_lines(lines2)
    # Forgive trailing whitespace problems in the last line:
    if True:
        lines1, lines2 = self.clean_last_lines(lines1), self.clean_last_lines(lines2)
    ok = lines1 == lines2
    if not ok and not self.strict:
        if trace:
            self.show_failure1(lines1, lines2, parent, trace_all, trace_status)
        # Issue an error only if something *other than* lws is amiss.
        lines1, lines2 = self.strip_lws(lines1), self.strip_lws(lines2)
        ok = lines1 == lines2
        if ok and not g.unitTesting:
            print('warning: leading whitespace changed in:', self.root.h)
    if not ok:
        self.show_failure2(lines1, lines2, sfn)
    if trace and trace_all or (not ok and trace_lines):
        self.trace_lines(lines1, lines2, parent)
    # Ensure that the unit tests fail when they should.
    # Unit tests do not generate errors unless the mismatch line does not match.
    if g.app.unitTesting:
        d = g.app.unitTestDict
        d['result'] = ok
        if not ok:
            d['fail'] = g.callers()
            # Used in a unit test.
            c.importCommands.errors += 1
    t2 = time.clock()
    if t2 - t1 &gt; 0.1:
        print('')
        g.trace('Excessive i.check time: %5.2f sec. in %s' % (t2-t1, sfn))
    return ok
</t>
<t tx="ekr.20161108131153.4">def clean_blank_lines(self, lines):
    '''Remove all blanks and tabs in all blank lines.'''
    return [self.lstrip_line(z) if z.isspace() else z for z in lines]
</t>
<t tx="ekr.20161108131153.5">def lstrip_line(self, s):
    '''Delete leading whitespace, *without* deleting the trailing newline!'''
    # This fixes a major bug in strip_lws.
    assert s, g.callers()
    return '\n' if s.isspace() else s.lstrip()

def strip_all(self, lines):
    '''Strip blank lines and leading whitespace from all lines of s.'''
    return self.strip_lws(self.strip_blank_lines(lines))

def strip_blank_lines(self, lines):
    '''Strip all blank lines from s.'''
    return [z for z in lines if not z.isspace()]
    
def strip_lws(self, lines):
    '''Strip leading whitespace from all lines.'''
    return [self.lstrip_line(z) for z in lines]
    # This also works, but I prefer the "extra" call to lstrip().
    # return ['\n' if z.isspace() else z.lstrip() for z in lines].

    
</t>
<t tx="ekr.20161108131153.6">def trial_write(self):
    '''Return the trial write for self.root.'''
    at = self.c.atFileCommands
    if self.gen_refs:
        # Alas, the *actual* @auto write code refuses to write section references!!
        at.write(self.root,
                nosentinels=True,           # was False,
                perfectImportFlag=False,    # was True,
                scriptWrite=True,           # was False,
                thinFile=True,
                toString=True,
            )
    else:
        at.writeOneAtAutoNode(
            self.root,
            toString=True,
            force=True,
            trialWrite=True,
        )
    return g.toUnicode(at.stringOutput, self.encoding)
</t>
<t tx="ekr.20161108131153.7"># These can be overridden in subclasses.
</t>
<t tx="ekr.20161108131153.8">def adjust_parent(self, parent, headline):
    '''Return the effective parent.

    This is overridden by the RstScanner class.'''
    return parent
</t>
<t tx="ekr.20161108131153.9">def clean_headline(self, s):
    '''
    Return the cleaned version headline s.
    Will typically be overridden in subclasses.
    '''
    return s.strip()
</t>
<t tx="ekr.20161108155143.3">def get_int_lws(self, s):
    '''Return the the lws (a number) of line s.'''
    # Important: use self.tab_width, *not* c.tab_width.
    return g.computeLeadingWhitespaceWidth(s, self.tab_width)
</t>
<t tx="ekr.20161108155143.4">def match(self, s, i, pattern):
    '''Return True if the pattern matches at s[i:]'''
    return s[i:i+len(pattern)] == pattern
</t>
<t tx="ekr.20161108155730.1">class Importer(object):
    '''
    The new, unified, simplified, interface to Leo's importer code.
    
    Eventually, all importers will create use this class.
    '''
    
    @others
</t>
<t tx="ekr.20161108155925.1">@nobeautify

def __init__(self,
    importCommands, 
    atAuto, # True when called from @auto logic.
    language = None, # For @language directive.
    name = None, # The kind of importer, usually the same as language
    state_class = None, # For i.scan_line
    strict = False,
):
    '''Importer.__init__.'''
    # Copies of args...
    self.importCommands = ic = importCommands
    self.atAuto = atAuto
    self.c = c = ic.c
    self.encoding = ic.encoding
    self.language = language or name
        # For the @language directive.
    self.name = name or language
    language = self.language
    name = self.name
    assert language and name
    assert self.language and self.name
    self.state_class = state_class
    self.strict = strict
        # True: leading whitespace is significant.

    # Set from ivars...
    self.has_decls = name not in ('xml', 'org-mode', 'vimoutliner')
    self.is_rst = name in ('rst',)
    self.tree_type = ic.treeType # '@root', '@file', etc.

    # Constants...
    data = g.set_delims_from_language(self.name)
    self.single_comment, self.block1, self.block2 = data
    self.escape = c.atFileCommands.underindentEscapeString
    self.escape_string = r'%s([0-9]+)\.' % re.escape(self.escape)
        # m.group(1) is the unindent value.
    self.escape_pattern = re.compile(self.escape_string)
    self.gen_refs = name in ('javascript',)
    self.ScanState = ScanState
        # Must be set by subclasses that use general_scan_line.
    self.tab_width = 0 # Must be set in run, using self.root.
    self.ws_pattern = re.compile(r'^\s*$|^\s*%s' % (self.single_comment or ''))

    # Settings...
    self.at_auto_warns_about_leading_whitespace = c.config.getBool(
        'at_auto_warns_about_leading_whitespace')
    self.warn_about_underindented_lines = True
    # self.at_auto_separate_non_def_nodes = False

    # State vars.
    self.errors = 0
    ic.errors = 0 # Required.
    self.parse_body = False
    self.ws_error = False
    self.root = None
</t>
<t tx="ekr.20161108160409.1">def gen_lines(self, s, parent):
    '''
    Non-recursively parse all lines of s into parent, creating descendant
    nodes as needed.
    '''
    trace = False and g.unitTesting
    tail_p = None
    prev_state = self.state_class()
    target = Target(parent, prev_state)
    stack = [target, target]
    self.inject_lines_ivar(parent)
    for line in g.splitLines(s):
        new_state = self.scan_line(line, prev_state)
        top = stack[-1]
        if trace: self.trace_status(line, new_state, prev_state, stack, top)
        if self.is_ws_line(line):
            p = tail_p or top.p
            self.add_line(p, line)
        elif self.starts_block(line, new_state, prev_state):
            tail_p = None
            self.start_new_block(line, new_state, prev_state, stack)
        elif self.ends_block(line, new_state, prev_state, stack):
            tail_p = self.end_block(line, new_state, stack)
        else:
            p = tail_p or top.p
            self.add_line(p, line)
        prev_state = new_state
</t>
<t tx="ekr.20161108160409.3">def end_block(self, line, new_state, stack):
    # The block is ending. Add tail lines until the start of the next block.
    p = stack[-1].p
    self.add_line(p, line)
    self.cut_stack(new_state, stack)
    tail_p = None if self.gen_refs else p
    return tail_p
</t>
<t tx="ekr.20161108160409.5">def add_root_directives(self, parent):
    '''Return the proper directives for the root node p.'''
    table = [
        '@language %s\n' % self.language,
        '@tabwidth %d\n' % self.tab_width,
    ]
    if self.parse_body:
        pass
    else:
        self.extend_lines(parent, table)
</t>
<t tx="ekr.20161108160409.6">def start_new_block(self, line, new_state, prev_state, stack):
    '''Create a child node and update the stack.'''
    trace = False and g.unitTesting
    if hasattr(new_state, 'in_context'):
        assert not new_state.in_context(), ('start_new_block', new_state)
    target=stack[-1]
    # Insert the reference in *this* node.
    h = self.gen_ref(line, target.p, target)
    # Create a new child and associated target.
    child = self.create_child_node(target.p, line, h)
    stack.append(Target(child, new_state))
    if trace:
        g.trace('=====', repr(line))
        g.printList(stack)
</t>
<t tx="ekr.20161108160409.7">def create_child_node(self, parent, body, headline):
    '''Create a child node of parent.'''
    child = parent.insertAsLastChild()
    self.inject_lines_ivar(child)
    if body:
        self.add_line(child, body)
    assert g.isString(headline), repr(headline)
    child.h = headline.strip()
    return child
</t>
<t tx="ekr.20161108160409.8">def gen_ref(self, line, parent, target):
    '''
    Generate the ref line and a flag telling this method whether a previous
    @others
    '''
    trace = False and g.unitTesting
    indent_ws = self.get_str_lws(line)
    h = self.clean_headline(line) 
    if self.is_rst and not self.atAuto:
        return None, None
    elif self.gen_refs:
        headline = g.angleBrackets(' %s ' % h)
        ref = '%s%s\n' % (
            indent_ws,
            g.angleBrackets(' %s ' % h))
    else:
        if target.ref_flag:
            ref = None
        else:
            ref = '%s@others\n' % indent_ws
            target.at_others_flag = True
        target.ref_flag = True
            # Don't generate another @others in this target.
        headline = h
    if ref:
        if trace:
            g.trace('%s indent_ws: %r line: %r parent: %s' % (
            '*' * 20, indent_ws, line, parent.h))
            g.printList(parent.v._import_lines)
        self.add_line(parent,ref)
    return headline
</t>
<t tx="ekr.20161108165530.1"></t>
<t tx="ekr.20161108170435.1">def scan_line(self, s, prev_state):
    '''
    A generalized scan-line method.
    
    SCAN STATE PROTOCOL:
    
    The Importer class should have a state_class ivar that references a
    **state class**. This class probably should *not* be subclass of the
    ScanState class, but it should observe the following protocol:
    
    1. The state class's ctor must have the following signature:
        
        def __init__(self, d)
        
    2. The state class must have an update method.
    '''
    trace = False and g.unitTesting
    # This dict allows new data to be added without changing ScanState signatures.
    d = {
        'indent': self.get_int_lws(s),
        'is_ws_line': self.is_ws_line(s),
        'prev':prev_state,
        's':s,
    }
    new_state = self.state_class(d)
    i = 0
    while i &lt; len(s):
        progress = i
        context = new_state.context
        table = self.get_table(context)
        data = self.scan_dict(context, i, s, table)
        i = new_state.update(data)
        assert progress &lt; i
    if trace: g.trace('\n\n%r\n\n%s\n' % (s, new_state))
    return new_state
</t>
<t tx="ekr.20161108180655.2">def undent_by(self, s, undent_val):
    '''
    Remove leading whitespace equivalent to undent_val from each line.
    
    Strict languages: prepend the underindent escape for underindented lines.
    '''
    trace = False and not g.app.unitTesting
    if self.is_rst:
        return s # Never unindent rst code.
    result = []
    for line in g.splitlines(s):
        lws_s = self.get_str_lws(line)
        lws = g.computeWidth(lws_s, self.tab_width)
        # Add underindentEscapeString only for strict languages.
        if self.strict and not line.isspace() and lws &lt; undent_val:
            if trace: g.trace('undent_val: %s, lws: %s, %r' % (
                undent_val, lws, line))
            # End the underindent count with a period to
            # protect against lines that start with a digit!
            result.append("%s%s.%s" % (
                self.escape, undent_val-lws, line.lstrip()))
        else:
            if trace: g.trace(undent_val, repr(line))
            s = g.removeLeadingWhitespace(line, undent_val, self.tab_width)
            result.append(s)
    return ''.join(result)
</t>
<t tx="ekr.20161109045312.1"></t>
<t tx="ekr.20161109045619.1">def print_lines(self, lines):
    '''Print lines for debugging.'''
    print('[')
    for line in lines:
        print(repr(line))
    print(']')

print_list = print_lines
</t>
<t tx="ekr.20161109052011.1">def is_ws_line(self, s):
    '''Return True if s is nothing but whitespace and single-line comments.'''
    # g.trace('(Importer)', bool(self.ws_pattern.match(s)), repr(s))
    return bool(self.ws_pattern.match(s))
</t>
<t tx="ekr.20161109053143.1">def get_leading_indent(self, lines, i, ignoreComments=True):
    '''
    Return the leading whitespace (an int) of the first significant line.
    Ignore blank and comment lines if ignoreComments is True
    '''
    if ignoreComments:
        while i &lt; len(lines):
            if self.is_ws_line(lines[i]):
                i += 1
            else:
                break
    return self.get_int_lws(lines[i]) if i &lt; len(lines) else 0
</t>
<t tx="ekr.20161109072221.1">def undent_body_lines(self, lines, ignoreComments=True):
    '''
    Remove the first line's leading indentation from all lines.
    Return the resulting string.
    '''
    trace = False and not g.unitTesting
    if trace:
        g.trace('='*20)
        self.print_lines(lines)
    s = ''.join(lines)
    if self.is_rst:
        return s # Never unindent rst code.
    # Calculate the amount to be removed from each line.
    undent_val = self.get_leading_indent(lines, 0, ignoreComments=ignoreComments)
    if trace: g.trace(undent_val, repr(lines[0]))
    if undent_val == 0:
        return s
    else:
        result = self.undent_by(s, undent_val)
        if trace:
            g.trace('-'*209)
            self.print_lines(g.splitLines(result))
        return result
</t>
<t tx="ekr.20161109111154.1"></t>
<t tx="ekr.20161110041440.1">def inject_lines_ivar(self, p):
    '''Inject _import_lines into p.v.'''
    assert not p.v._bodyString, repr(p.v._bodyString)
    p.v._import_lines = []
</t>
<t tx="ekr.20161110042020.1">def finalize_ivars(self, parent):
    '''
    Update the body text of all nodes in parent's tree using the injected
    v._import_lines lists.
    '''
    trace = False and g.unitTesting
    for p in parent.self_and_subtree():
        v = p.v
        # Make sure that no code in x.post_pass has mistakenly set p.b.
        assert not v._bodyString, repr(v._bodyString)
        lines = v._import_lines
        if lines:
            if not lines[-1].endswith('\n'):
                if trace: g.trace('===== add newline', repr(lines[-1]), p.h)
                lines[-1] += '\n'
        if trace:
            g.trace('=====', repr(p.h))
            self.print_lines(lines)
        v._bodyString = ''.join(lines)
        delattr(v, '_import_lines')
</t>
<t tx="ekr.20161110042512.1"># All code in passes 1 and 2 *must* use this API to change body text.
def add_line(self, p, s):
    '''Append the line s to p.v._import_lines.'''
    assert not p.b, repr(p.b)
    assert hasattr(p.v, '_import_lines'), repr(p)
    assert s, g.callers()
    assert g.isString(s), repr(s)
    p.v._import_lines.append(s)

def clear_lines(self, p):
    p.v._import_lines = []

def extend_lines(self, p, lines):
    p.v._import_lines.extend(list(lines))

def get_lines(self, p):
    return  p.v._import_lines
    
def has_lines(self, p):
    return hasattr(p.v, '_import_lines')
    
def prepend_lines(self, p, lines):
    p.v._import_lines = list(lines) + p.v._import_lines

def set_lines(self, p, lines):
    p.v._import_lines = list(lines)
</t>
<t tx="ekr.20161110125940.1">def clean_all_headlines(self, parent):
    '''
    Clean all headlines in parent's tree by calling the language-specific
    clean_headline method.
    '''
    for p in parent.subtree():
        h = self.clean_headline(p.h)
        if h:
            if h != p.h: p.h = h
        else:
            pass
            # g.trace('empty headline', p, 'parent', parent.h)
</t>
<t tx="ekr.20161110130157.1">def clean_all_nodes(self, parent):
    '''Clean the nodes in parent's tree, in a language-dependent way.'''
    # i.clean_nodes does nothing.
    # Subclasses may override as desired.
    # See perl_i.clean_nodes for an example.
    self.clean_nodes(parent)
</t>
<t tx="ekr.20161110130337.1">def unindent_all_nodes(self, parent):
    '''Unindent all nodes in parent's tree.'''
    for p in parent.subtree():
        lines = self.get_lines(p)
        if all([z.isspace() for z in lines]):
            # Somewhat dubious, but i.check covers for us.
            self.clear_lines(p)
        else:
            self.set_lines(p, self.undent(p))
</t>
<t tx="ekr.20161110130709.1">def delete_all_empty_nodes(self, parent):
    '''
    Delete nodes consisting of nothing but whitespace.
    Move the whitespace to the preceding node.
    '''
    c = self.c
    aList = []
    for p in parent.subtree():
        back = p.threadBack()
        if back != parent and not p.isCloned():
            lines = self.get_lines(p)
            # Move the whitespace from p to back.
            if all([z.isspace() for z in lines]):
                self.extend_lines(back, lines)
                aList.append(p.copy())
    c.deletePositionsInList(aList)
</t>
<t tx="ekr.20161110131509.1">def promote_trailing_underindented_lines(self, parent):
    '''
    Promote all trailing underindent lines to the node's parent node,
    deleting one tab's worth of indentation. Typically, this will remove
    the underindent escape.
    '''
    pattern = self.escape_pattern # A compiled regex pattern
    for p in parent.subtree():
        lines = self.get_lines(p)
        tail = []
        while lines:
            line = lines[-1]
            m = pattern.match(line)
            if m:
                lines.pop()
                n_str = m.group(1)
                try:
                    n = int(n_str)
                except ValueError:
                    break
                if n == abs(self.tab_width):
                    new_line = line[len(m.group(0)):]
                    tail.append(new_line)
                else:
                    g.trace('unexpected unindent value', n)
                    break
            else:
                break
        if tail:
            parent = p.parent()
            if parent.parent() == self.root:
                parent = parent.parent()
            self.set_lines(p, lines)
            self.extend_lines(parent, reversed(tail))
            
</t>
<t tx="ekr.20161110173058.1">def clean_nodes(self, parent):
    '''
    Clean all nodes in parent's tree.
    Subclasses override this as desired.
    See perl_i.clean_nodes for an examplle.
    '''
    pass
</t>
<t tx="ekr.20161110173847.1">g.cls()
import imp
import re
import leo.plugins.importers.linescanner as linescanner
imp.reload(linescanner)
i = linescanner.Importer(
    c.importCommands, 
    atAuto = True, # True when called from @auto logic.
    language = 'python', # For @language directive.
)
escape = c.atFileCommands.underindentEscapeString
line = r'\\-4.# last line'
pattern = i.escape_pattern
m = pattern.match(line)
&lt;&lt; old experiments &gt;&gt;
if 1:
    print('       line', line)
    print('    pattern', pattern)
    print('     escape', escape)
    # print(' startswith', line.startswith(pattern))
    print(' m.group(0)', m and m.group(0))
</t>
<t tx="ekr.20161110192833.1">if 0:
    if 0:
        pattern = r'\\-' # line.startswith(pattern)
        pattern = repr('\\-') # no
        pattern = '\\\\-' # line.startswith(pattern)
        pattern = 'r"%s"' % escape # no
        pattern = r'%s([0-9]+)\.' % escape # no
    pattern = r'\\-' # line.startswith(pattern)
    m = re.match(pattern, line)
    # m = re.match(r'\\-([0-9]+)\.', line)
    m = re.match(r'\\\\-([0-9]+)\.', line) #### works.
    pattern = r'%s-([0-9]+)\.' % r'\\\\' ### works
    pattern = r'%s([0-9]+)\.' % r'\\\\-'
    pattern = r'%s([0-9]+)\.' % escape.replace(r'\\', r'\\\\') ## works
    m = re.match(pattern, line)</t>
<t tx="ekr.20161110193124.1">g.cls()
print(int('123'))
print(int('xyz'))</t>
<t tx="ekr.20161110200245.1"></t>
<t tx="ekr.20161111021944.1">g.cls()
import re
e = c.atFileCommands.underindentEscapeString
print(re.escape(e))
print(r'%s([0-9]+)\.' % re.escape(e))</t>
<t tx="ekr.20161111023249.1">def finish(self, parent):
    '''
    Stage 3 (the last) stage of the importer pipeline.

    Subclasses should never need to override this method.
    '''
    # Put directives at the end, so as not to interfere with shebang lines, etc.
    self.add_root_directives(parent)
    #
    # Finally, remove all v._import_list temporaries.
    self.finalize_ivars(parent)
</t>
<t tx="ekr.20161111024447.1">def generate_nodes(self, s, parent):
    '''
    A three-stage pipeline to generate all imported nodes.
    '''
    # Stage 1: generate nodes.
    # After this stage, the p.v._import_lines list contains p's future body text.
    self.gen_lines(s, parent)
    #
    # Optional Stage 2, consisting of zero or more sub-stages.
    # Subclasses may freely override this method, **provided**
    # that all substages use the API for setting body text.
    # Changing p.b directly will cause asserts to fail in i.finish(). 
    self.post_pass(parent)
    #
    # Stage 3: Put directives in the root node and set p.b for all nodes.
    #
    # Subclasses should never need to override this stage.
    self.finish(parent)
</t>
<t tx="ekr.20161112085333.1">if 1:
    def f():
        '''
        This
is a valid
        docstring.
        '''
        g.trace(f.__doc__)
        
f()
</t>
<t tx="ekr.20161113052225.1">def scan_table(self, context, i, s, table):
    '''
    i.scan_table: Scan at position i of s with the give context and table.
    Return the 6-tuple: (new_context, i, delta_c, delta_p, delta_s, bs_nl)
    '''
    trace = False and g.unitTesting
    if trace: g.trace('='*20, repr(context))
    # kind,   pattern, out-ctx,     in-ctx,     delta{}, delta(), delta[]
    for kind, pattern, out_context, in_context, delta_c, delta_p, delta_s in table:
        # pattern may be None in the general table,
        # because not all languages have all comment delims.
        if pattern and self.match(s, i, pattern):
            if not kind.startswith('end'):
                assert kind in ('all', 'len', 'len+1'), kind
            # Backslash patterns must match in all contexts!
            if pattern.startswith('\\'):
                ok = True
                if trace: g.trace(
                    '----- context: %r in_context: %r out_context: %r' % (
                        context, in_context, out_context))
                new_context = out_context
            elif context == '':
                ok = True
                new_context = out_context
            elif kind.startswith('end'):
                tail = kind[3:]
                ok = tail and context == tail
                new_context = in_context
            else:
                ok = context == pattern
                new_context = in_context
            if ok:
                assert new_context is not None, (pattern, repr(s))
                if trace: g.trace(
                    '   MATCH: i: %s ch: %4r kind: %5s pattern: %5r '
                    'context: %5r new_context: %5r line: %r' % (
                    i, s[i], kind, pattern, context, new_context, s))
                if kind == 'all':
                    i = len(s)
                elif kind == 'len+1':
                    i += (len(pattern) + 1)
                else:
                    assert kind.startswith('end') or kind == 'len', (kind, self.name)
                    i += len(pattern)
                bs_nl = pattern == '\\\n'
                return new_context, i, delta_c, delta_p, delta_s, bs_nl
    # No match: stay in present state. All deltas are zero.
    if trace: g.trace('NO MATCH: i: %s ch: %4r context: %5r line: %r' % (i, s[i], context, s))
    return context, i+1, 0, 0, 0, False
</t>
<t tx="ekr.20161113070532.1"># g.cls()
import imp
import leo.plugins.importers.coffeescript as cs
imp.reload(cs)
&lt;&lt; define table &gt;&gt;
x = cs.CS_Importer(c.importCommands, atAuto=True)
assert x.single_comment == '#', x.single_comment
for new_state, line in table:
    print('%5s %r' % (new_state, line))
if 0:
    for line in lines_table:
        lines = [line]
        n = importer.get_leading_indent(lines, 0)
        # print('%s %r' % (n, line))</t>
<t tx="ekr.20161113070952.1">table = [
    # State after line, line

]</t>
<t tx="ekr.20161113083459.1">g.cls()
if c.isChanged(): c.save()
import imp
import leo.plugins.importers.linescanner as linescanner
import leo.plugins.importers.python as py
imp.reload(linescanner)
imp.reload(py)
State = py.Python_State
&lt;&lt; define python tests &gt;&gt;
if 1:
    importer = py.Py_Importer(c.importCommands, atAuto=True)
    importer.test_scan_state(tests, State)
</t>
<t tx="ekr.20161113132509.1"></t>
<t tx="ekr.20161113135037.1">@nobeautify
cached_scan_tables = {}

def get_table(self, context):
    '''
    Return the state table for the given context.
    
    This method handles caching.  x.get_new_table returns the actual table.
    '''
    key = '%s.%s' % (self.name, context)
        # Bug fix: must keep tables separate.
    table = self.cached_scan_tables.get(key)
    if table:
        return table
    else:
        table = self.get_new_dict(context)
        self.cached_scan_tables[key] = table
        return table
</t>
<t tx="ekr.20161114011813.1"># A list of dictionaries.
if 0:
    tests = [
        g.Bunch(line='s = "\\""', ctx=('', '')),
    ]
else:
    tests = [
        g.Bunch(line='\n'),
        g.Bunch(line='\\\n'),
        g.Bunch(line='s = "\\""', ctx=('', '')),
        g.Bunch(line="s = '\\''", ctx=('', '')),
        g.Bunch(line='# comment'),
        g.Bunch(line='  # comment'),
        g.Bunch(line='    # comment'),
        g.Bunch(line='a = "string"'),
        g.Bunch(line='a = "Continued string', ctx=('', '"')),
        g.Bunch(line='end of continued string"', ctx=('"', '')),
        g.Bunch(line='a = """Continued docstring', ctx=('', '"""')),
        g.Bunch(line='a = """#', ctx=('', '"""')),
        g.Bunch(line='end of continued string"""', ctx=('"""', '')),
        g.Bunch(line="a = '''Continued docstring", ctx=('', "'''")),
        g.Bunch(line="end of continued string'''", ctx=("'''", '')),
        g.Bunch(line='a = {[(')
    ]</t>
<t tx="ekr.20161114012522.1">def all_contexts(self, table):
    '''
    Return a list of all contexts contained in the third column of the given table.
    
    This is a support method for unit tests.
    '''
    contexts = set()
    d = table
    for key in d:
        aList = d.get(key)
        for data in aList:
            if len(data) == 4:
                # It's an out-of-context entry.
                contexts.add(data[2])
    # Order must not matter, so sorting is ok.
    return sorted(contexts)
</t>
<t tx="ekr.20161114024119.1">def test_scan_state(self, tests, State):
    '''
    Test x.scan_line or i.scan_line.

    `tests` is a list of g.Bunches with 'line' and 'ctx' fields.
    
    A typical @command test:
        
        if c.isChanged(): c.save()
        &lt; &lt; imp.reload importers.linescanner and importers.python &gt; &gt;
        importer = py.Py_Importer(c.importCommands, atAuto=True)
        importer.test_scan_state(tests, Python_ScanState)
    '''
    trace = False and g.unitTesting
    assert self.single_comment == '#', self.single_comment
    trace_contexts = True
    trace_states = True
    table = self.get_table(context='')
    contexts = self.all_contexts(table)
    if trace and trace_contexts:
        print('\ncontexts:'+' '.join([repr(z) for z in contexts]))
    for bunch in tests:
        assert bunch.line is not None
        line = bunch.line
        ctx = getattr(bunch, 'ctx', None)
        if trace: g.trace('===== ctx: %r line: %r' % (ctx, line))
        if ctx: # Test one transition.
            ctx_in, ctx_out = ctx
            prev_state =  State()
            prev_state.context = ctx_in
            new_state = self.scan_line(line, prev_state)
            new_context = new_state.context
            if trace and trace_states: g.trace(
                '\nprev: %s\n new: %s' % (prev_state, new_state))
            assert new_context == ctx_out, (
                'FAIL1:\nline: %r\ncontext: %r new_context: %r ctx_out: %r\n%s\n%s' % (
                    line, ctx_in, new_context, ctx_out, prev_state, new_state))
        else: # Test all transitions.
            for context in contexts:
                prev_state =  State()
                prev_state.context = context
                new_state = self.scan_line(line, prev_state)
                if trace and trace_states: g.trace(
                    '\nprev: %s\n new: %s' % (prev_state, new_state))
                assert new_state.context == context, (
                    'FAIL2:\nline: %r\ncontext: %r new_context: %r\n%s\n%s' % (
                        line, context, new_state.context, prev_state, new_state))
</t>
<t tx="ekr.20161117081206.1"># g.cls()
import re
import imp
import leo.plugins.importers.python as python
imp.reload(python)

table = [
    "@cmd('abc')",
    "   @cmd('abc')",
]

x = python.Py_Importer(c.importCommands, atAuto=True)

for s in g.globalDirectiveList:
    assert not x.is_decorator(s), repr(s)
    assert not x.is_decorator('@' + s), repr('@' + s)
for s in table:
    assert x.is_decorator(s), repr(s)
    assert x.is_decorator(s + '\n'), repr(s + '\n')

</t>
<t tx="ekr.20161119083909.1">def findClass(self, p):
    '''Return the index end of the class or def in a node, or -1.'''
    s, i = p.b, 0
    while i &lt; len(s):
        progress = i
        if s[i] in (' ', '\t', '\n'):
            i += 1
        elif self.startsComment(s, i):
            i = self.skipComment(s, i)
        elif self.startsString(s, i):
            i = self.skipString(s, i)
        elif self.startsClass(s, i):
            return 'class', self.sigStart, self.codeEnd
        elif self.startsFunction(s, i):
            return 'def', self.sigStart, self.codeEnd
        elif self.startsId(s, i):
            i = self.skipId(s, i)
        else:
            i += 1
        assert progress &lt; i, 'i: %d, ch: %s' % (i, repr(s[i]))
    return None, -1, -1
</t>
<t tx="ekr.20161119124217.1">def starts_block(self, line, new_state, prev_state):
    '''True if the new state starts a block.'''
    return new_state.level() &gt; prev_state.level()
</t>
<t tx="ekr.20161119130337.1">def cut_stack(self, new_state, stack):
    '''Cut back the stack until stack[-1] matches new_state.'''
    trace = False and g.unitTesting
    if trace:
        g.trace(new_state)
        g.printList(stack)
    assert len(stack) &gt; 1 # Fail on entry.
    while stack:
        top_state = stack[-1].state
        if new_state.level() &lt; top_state.level():
            if trace: g.trace('new_state &lt; top_state', top_state)
            assert len(stack) &gt; 1, stack # &lt;
            stack.pop()
        elif top_state.level() == new_state.level():
            if trace: g.trace('new_state == top_state', top_state)
            assert len(stack) &gt; 1, stack # ==
            # This is the only difference between i.cut_stack and python/cs.cut_stack
            # stack.pop()
            break
        else:
            # This happens often in valid Python programs.
            if trace: g.trace('new_state &gt; top_state', top_state)
            break
    # Restore the guard entry if necessary.
    if len(stack) == 1:
        if trace: g.trace('RECOPY:', stack)
        stack.append(stack[-1])
    assert len(stack) &gt; 1 # Fail on exit.
    if trace: g.trace('new target.p:', stack[-1].p.h)
</t>
<t tx="ekr.20161119162451.1">def trace_status(self, line, new_state, prev_state, stack, top):
    '''Print everything important in the i.gen_lines loop.'''
    print('')
    try:
        g.trace('===== %r' % line)
    except Exception:
        g.trace('     top.p: %s' % g.toEncodedString(top.p.h))
    print('len(stack): %s' % len(stack))
    print(' new_state: %s' % new_state)
    print('prev_state: %s' % prev_state)
    # print(' top.state: %s' % top.state)
    g.printList(stack)
</t>
<t tx="ekr.20161120022121.1"></t>
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
<t tx="ekr.20161122123422.1"># g.cls()
if c.isChanged(): c.save()
import imp
import leo.plugins.importers.linescanner as linescanner
import leo.plugins.importers.xml as xml
imp.reload(linescanner)
imp.reload(xml)
x = xml.Xml_Importer(importCommands = c.importCommands, atAuto = False)
table = (
    (0, '&lt;tag&gt;'),
    (0, '&lt;tag&gt;&lt;/tag'),
    (1, '&lt;html'),
    (1, '&lt;html attrib="&lt;"&gt;'),
    (0, '&lt;html attrib="&lt;" /&gt;'),
    (0, '&lt;html&gt;x&lt;/html&gt;'),
    (0, '&lt;/br&gt;'), # Tag underflow
    (0, '&lt;br /&gt;'),
    (0, '&lt;br/&gt;'),
)
for level, line in table:
    prev_state = x.state_class()
    assert prev_state.tag_level == 0
    new_state = x.v2_scan_line(line, prev_state)
    assert new_state.tag_level == level, (new_state, repr(line))</t>
<t tx="ekr.20161122155335.1"># g.cls()
if c.isChanged(): c.save()
import imp
import leo.plugins.importers.linescanner as linescanner
import leo.plugins.importers.xml as xml
imp.reload(linescanner)
imp.reload(xml)
x = xml.Xml_Importer(importCommands = c.importCommands, atAuto = False)
# print(x.xml_ws_pattern)
table = (
   (1, ' \n'),
   (1, '\n'),
   (1, ' '),
   (1, '&lt;!-- comment --&gt;'),
   (0, '  &lt;!-- comment --&gt; Help'),
   (0, 'x &lt;!-- comment --&gt;'),
   (0, 'Help'),
)
for expected, line in table:
    got = x.is_ws_line(line)
    assert expected == got, (expected, int(got), repr(line))
</t>
<t tx="ekr.20161123091527.1">@language rest
@wrap

- Add unit test for coffeescript, perl, and i.general_scan_line (i.get_table)
- Add unit tests for failing coffeescript imports.
* Unit tests for all ScanState classes.
    - unitTest.leo contains *only* @test importers.javascript.scan_line
    - There is an unfinished test for coffeescript in this file.
</t>
<t tx="ekr.20161123091556.1">@language rest
@wrap

Scan ahead in i.scan_dict for comments and strings.
- Investigate how to do this with regex's.
    - Handle escapes.
    - Make sure that the regex stops at the first delim.
    - Unit tests for the regex.

Coffeescript:
- Get move_trailing_lines working, or abandon it.

Python:
- Unit test for all of Leo's core files.
</t>
<t tx="ekr.20161123121746.1">g.cls()
if c.isChanged(): c.save()
import imp
import leo.plugins.importers.dart as dart
imp.reload(dart)
x = dart.Dart_Importer(c.importCommands, atAuto=False)    
# pattern = x.dart_pattern
# print(pattern)
table = (
    'func(abc) {',
    'void foo() {',
)
for s in table:
    print('%20s ==&gt; %s' % (s, x.clean_headline(s)))
</t>
<t tx="ekr.20161123202118.1">g.cls()
if c.isChanged(): c.save()
import imp
import leo.plugins.importers.org as org
imp.reload(org)
x = org.Org_Importer(c.importCommands, atAuto=False)    
pattern = x.org_pattern
print(pattern)
table = (
    'body * line',
    '* line 1',
    '** level 2',
)
for line in table:
    m = pattern.match(line)
    print('%20s ==&gt; (%r)(%r)' % (
        line, m and m.group(1), m and m.group(2)))
</t>
<t tx="ekr.20161123210335.1">def trace_lines(self, lines1, lines2, parent):
    '''Show both s1 and s2.'''
    print('===== s1: %s' % parent.h)
    for i, s in enumerate(lines1):
        print('%3s %r' % (i+1, s))
    print('===== s2')
    for i, s in enumerate(lines2):
        print('%3s %r' % (i+1, s))
</t>
<t tx="ekr.20161123210716.1">def show_failure2(self, lines1, lines2, sfn):
    '''Print the failing lines.'''
    if not g.unitTesting:
        g.es('@auto failed:', sfn, color='red')
    n1, n2 = len(lines1), len(lines2)
    print('\n===== PERFECT IMPORT FAILED =====', sfn)
    print('len(s1): %s len(s2): %s' % (n1, n2))
    for i in range(min(n1, n2)):
        line1, line2 = lines1[i], lines2[i]
        if line1 != line2:
             print('first mismatched line: %s' % (i+1))
             print(repr(line1))
             print(repr(line2))
             break
    else:
        print('all common lines match')
</t>
<t tx="ekr.20161124023807.1">g.cls()
table = (
    '\n',
    '  \n',
    '  abc\n',
)
for s in table:
    print('s.isspace(): %5s %10r s.lstrip(): %r' % (s.isspace(), s, s.lstrip()))</t>
<t tx="ekr.20161124030004.1">def clean_last_lines(self, lines):
    '''Remove blank lines from the end of lines.'''
    while lines and lines[-1].isspace():
        lines.pop()
    return lines
</t>
<t tx="ekr.20161124035818.1">g.cls()
if c.isChanged(): c.save()
import imp
import leo.plugins.importers.otl as otl
imp.reload(otl)
x = otl.Otl_Importer(c.importCommands, atAuto=False)    
pattern = x.otl_pattern
print(pattern)
table = (
    'body line',
    '\tline 1',
    '  \tlevel 2',
)
for line in table:
    m = pattern.match(line)
    print('%20r ==&gt; (%r)(%r)' % (
        line, m and m.group(1), m and m.group(2)))
</t>
<t tx="ekr.20161124042619.1">@tabwidth 4
if 1:
    g.cls()
    if c.isChanged(): c.save()
    import imp
    import leo.plugins.importers.linescanner as linescanner
    import leo.plugins.importers.otl as otl
    imp.reload(linescanner)
    imp.reload(otl)    
s = '''\
Section 1
: Sec 1.
Section 2
: Sec 2.
\tSection 2-1
: Sec 2-1
\t\tSection 2-1-1
: Sect 2-1-1
Section 3
: Sec 3
\tSection 3.1
: Sec 3.1
'''
table = (
    'Section 1',
    'Section 2', 'Section 2-1', 'Section 2-1-1',
    'Section 3', 'Section 3.1',
)
try:
    c.importCommands.otlUnitTest(p,s=s,showTree=True)
    if 0:
        root = c.p.firstChild()
        p2 = root.firstChild()
        for h in table:
            assert p2.h == h, (p2.h, h)
            p2.moveToThreadNext()
        assert not root.isAncestorOf(p2), p2.h # Extra nodes
finally:
    if 0:
        p.deleteAllChildren()
</t>
<t tx="ekr.20161124083517.1">@others

Warning: this node is ignored when writing this file.

@language plain
@tabwidth 4
</t>
<t tx="ekr.20161124083517.2">Sec 1.</t>
<t tx="ekr.20161124083517.3">Sec 2.</t>
<t tx="ekr.20161124083517.4">Sec 2-1</t>
<t tx="ekr.20161124083517.5">Sect 2-1-1</t>
<t tx="ekr.20161124083517.6">Sec 3</t>
<t tx="ekr.20161124083517.7">Sec 3.1</t>
<t tx="ekr.20161124083531.1"></t>
<t tx="ekr.20161124083531.2"></t>
<t tx="ekr.20161124083531.3"></t>
<t tx="ekr.20161124083531.4"></t>
<t tx="ekr.20161124083531.5"></t>
<t tx="ekr.20161124083531.6"></t>
<t tx="ekr.20161124083531.7"></t>
<t tx="ekr.20161124083531.8"></t>
<t tx="ekr.20161124083550.1">@others

Warning: this node is ignored when writing this file.

@language plain
@tabwidth 4
</t>
<t tx="ekr.20161124083550.2">Sec 1.</t>
<t tx="ekr.20161124083550.3">Sec 2.</t>
<t tx="ekr.20161124083550.4">Sec 2-1</t>
<t tx="ekr.20161124083550.5">Sect 2-1-1</t>
<t tx="ekr.20161124083550.6">Sec 3</t>
<t tx="ekr.20161124083550.7">Sec 3.1</t>
<t tx="ekr.20161124122450.1">'''Make an @test node for the importer whose name is given.'''
name = 'markdown'
d = g.app.permanentScriptDict
tag = 'make_test_%s_n' % name
n = d.get(tag, 0) + 1
d [tag] = n
d = {'cap_name': name.capitalize(), 'n': n, 'name': name}
&lt;&lt; define preamble &gt;&gt;
p = c.lastTopLevel().insertAfter()
p.b = preamble
p.h = '@test %(name)s importer-%(n)s' % d
c.redraw()
c.selectPosition(p)
c.bodyWantsFocusNow()
c.frame.body.wrapper.setInsertPoint(len(p.b))
</t>
<t tx="ekr.20161124122613.1">preamble = '''\
if 1:
    # The preamble...
    g.cls()
    if c.isChanged(): c.save()
    import leo.plugins.importers.linescanner as linescanner
    import leo.core.leoImport as leoImport
    import leo.plugins.importers.markdown as markdown
    # Reload all.
    import imp
    imp.reload(linescanner)
    imp.reload(markdown)
    imp.reload(leoImport)
    ic = leoImport.LeoImportCommands(c)
    x = markdown.Markdown_Importer(ic, atAuto=False)   
# insert test for %(name)s here.
''' % d
</t>
<t tx="ekr.20161124122942.1">g.cls()
name = 'otl'
s = '''\
if 1:
    g.cls()
    if c.isChanged(): c.save()
    import imp
    import leo.plugins.importers.linescanner as linescanner
    import leo.plugins.importers.%(name)s as %(name)s
    imp.reload(linescanner)
    imp.reload(%(name)s)
''' % {'name': name}
print(s)</t>
<t tx="ekr.20161124154051.1"></t>
<t tx="ekr.20161124154102.1"></t>
<t tx="ekr.20161124154123.1"></t>
<t tx="ekr.20161124154130.1"></t>
<t tx="ekr.20161124154218.1">if 1:
    # The preamble...
    g.cls()
    if c.isChanged(): c.save()
    # import leo.core.leoCommands as leoCommands
    import leo.plugins.importers.linescanner as linescanner
    # imp.reload(leoCommands)
    import leo.core.leoImport as leoImport
    import leo.plugins.importers.org as org
    # Reload all.
    import imp
    imp.reload(linescanner)
    imp.reload(org)
    imp.reload(leoImport)
    ic = leoImport.LeoImportCommands(c)
    x = org.Org_Importer(ic, atAuto=False)
# insert test for org here.
s = '''\
* Section 1
Sec 1.
* Section 2
Sec 2.
** Section 2-1
Sec 2.1
*** Section 2-1-1
Sec 2.1.1
* Section 3
****** Section 3-1-1-1-1-1
: Sec 3-1-1-1-1-1
** Section 3.1
Sec 3.1
'''
table = (
    'Section 1',
    'Section 2', 'Section 2-1', 'Section 2-1-1',
    'Section 3', 'Section 3.1',
)
try:
    if 1:
        g.app.suppressImportChecks = True
        ic.orgUnitTest(p,s=s,showTree=True)
    else:
        c.importCommands.orgUnitTest(p,s=s,showTree=True)
            # Uses old Org_Importer...
    if 0:
        root = c.p.firstChild()
        p2 = root.firstChild()
        for h in table:
            assert p2.h == h, (p2.h, h)
            p2.moveToThreadNext()
        assert not root.isAncestorOf(p2), p2.h # Extra nodes
finally:
    if 0:
        p.deleteAllChildren()

</t>
<t tx="ekr.20161124160431.1">@others

Warning: this node is ignored when writing this file.

@language plain
@tabwidth -4
@ignore
</t>
<t tx="ekr.20161124160431.10"></t>
<t tx="ekr.20161124160431.11">: Sec 3-1-1-1-1-1
</t>
<t tx="ekr.20161124160431.12">Sec 3.1
</t>
<t tx="ekr.20161124160431.2">Sec 1.
</t>
<t tx="ekr.20161124160431.3">Sec 2.
</t>
<t tx="ekr.20161124160431.4">Sec 2.1
</t>
<t tx="ekr.20161124160431.5">Sec 2.1.1
</t>
<t tx="ekr.20161124160431.6"></t>
<t tx="ekr.20161124160431.7"></t>
<t tx="ekr.20161124160431.8"></t>
<t tx="ekr.20161124160431.9"></t>
<t tx="ekr.20161124160840.1">@others

Warning: this node is ignored when writing this file.

@language plain
@tabwidth -4
@ignore
</t>
<t tx="ekr.20161124160840.10"></t>
<t tx="ekr.20161124160840.11">: Sec 3-1-1-1-1-1
</t>
<t tx="ekr.20161124160840.12">Sec 3.1
</t>
<t tx="ekr.20161124160840.2">Sec 1.
</t>
<t tx="ekr.20161124160840.3">Sec 2.
</t>
<t tx="ekr.20161124160840.4">Sec 2.1
</t>
<t tx="ekr.20161124160840.5">Sec 2.1.1
</t>
<t tx="ekr.20161124160840.6"></t>
<t tx="ekr.20161124160840.7"></t>
<t tx="ekr.20161124160840.8"></t>
<t tx="ekr.20161124160840.9"></t>
<t tx="ekr.20161124185724.1">@others

Warning: this node is ignored when writing this file.

@language plain
@tabwidth -4
@ignore
</t>
<t tx="ekr.20161124185724.10"></t>
<t tx="ekr.20161124185724.11">: Sec 3-1-1-1-1-1
</t>
<t tx="ekr.20161124185724.12">Sec 3.1
</t>
<t tx="ekr.20161124185724.2">Sec 1.
</t>
<t tx="ekr.20161124185724.3">Sec 2.
</t>
<t tx="ekr.20161124185724.4">Sec 2.1
</t>
<t tx="ekr.20161124185724.5">Sec 2.1.1
</t>
<t tx="ekr.20161124185724.6"></t>
<t tx="ekr.20161124185724.7"></t>
<t tx="ekr.20161124185724.8"></t>
<t tx="ekr.20161124185724.9"></t>
<t tx="ekr.20161124185947.1">@others

Warning: this node is ignored when writing this file.

@language plain
@tabwidth -4
@ignore
</t>
<t tx="ekr.20161124185947.10"></t>
<t tx="ekr.20161124185947.11">: Sec 3-1-1-1-1-1
</t>
<t tx="ekr.20161124185947.12">Sec 3.1
</t>
<t tx="ekr.20161124185947.2">Sec 1.
</t>
<t tx="ekr.20161124185947.3">Sec 2.
</t>
<t tx="ekr.20161124185947.4">Sec 2.1
</t>
<t tx="ekr.20161124185947.5">Sec 2.1.1
</t>
<t tx="ekr.20161124185947.6"></t>
<t tx="ekr.20161124185947.7"></t>
<t tx="ekr.20161124185947.8"></t>
<t tx="ekr.20161124185947.9"></t>
<t tx="ekr.20161124190118.1">@others

Warning: this node is ignored when writing this file.

@language plain
@tabwidth -4
@ignore
</t>
<t tx="ekr.20161124190118.10"></t>
<t tx="ekr.20161124190118.11">: Sec 3-1-1-1-1-1
</t>
<t tx="ekr.20161124190118.12">Sec 3.1
</t>
<t tx="ekr.20161124190118.2">Sec 1.
</t>
<t tx="ekr.20161124190118.3">Sec 2.
</t>
<t tx="ekr.20161124190118.4">Sec 2.1
</t>
<t tx="ekr.20161124190118.5">Sec 2.1.1
</t>
<t tx="ekr.20161124190118.6"></t>
<t tx="ekr.20161124190118.7"></t>
<t tx="ekr.20161124190118.8"></t>
<t tx="ekr.20161124190118.9"></t>
<t tx="ekr.20161124190228.1">@others

Warning: this node is ignored when writing this file.

@language plain
@tabwidth -4
@ignore
</t>
<t tx="ekr.20161124190228.10"></t>
<t tx="ekr.20161124190228.11">: Sec 3-1-1-1-1-1
</t>
<t tx="ekr.20161124190228.12">Sec 3.1
</t>
<t tx="ekr.20161124190228.2">Sec 1.
</t>
<t tx="ekr.20161124190228.3">Sec 2.
</t>
<t tx="ekr.20161124190228.4">Sec 2.1
</t>
<t tx="ekr.20161124190228.5">Sec 2.1.1
</t>
<t tx="ekr.20161124190228.6"></t>
<t tx="ekr.20161124190228.7"></t>
<t tx="ekr.20161124190228.8"></t>
<t tx="ekr.20161124190228.9"></t>
<t tx="ekr.20161124190243.1">@others

Warning: this node is ignored when writing this file.

@language plain
@tabwidth -4
@ignore
</t>
<t tx="ekr.20161124190243.10"></t>
<t tx="ekr.20161124190243.11">: Sec 3-1-1-1-1-1
</t>
<t tx="ekr.20161124190243.12">Sec 3.1
</t>
<t tx="ekr.20161124190243.2">Sec 1.
</t>
<t tx="ekr.20161124190243.3">Sec 2.
</t>
<t tx="ekr.20161124190243.4">Sec 2.1
</t>
<t tx="ekr.20161124190243.5">Sec 2.1.1
</t>
<t tx="ekr.20161124190243.6"></t>
<t tx="ekr.20161124190243.7"></t>
<t tx="ekr.20161124190243.8"></t>
<t tx="ekr.20161124190243.9"></t>
<t tx="ekr.20161124191927.1">if 1:
    # The preamble...
    g.cls()
    if c.isChanged(): c.save()
    import leo
    import leo.core.leoImport as leoImport
    import leo.plugins.importers.markdown as markdown
    # Reload all.
    import imp
    imp.reload(markdown)
    imp.reload(leoImport)
    ic = leo.core.leoImport.LeoImportCommands(c)
    x = markdown.Markdown_Importer(ic, atAuto=False)   
# insert test for markdown here.
assert x.md_pattern_table
# g.printList(x.md_pattern_table)
hashes_table = (
    (None,  None,   None,       '-- help'),
    ('#',   1,      'name',     '# name\n'),
    ('#',   2,      'a test',   '## a test\n'),
    ('#',   3,      'a test',   '### a test\n'),
)
for data in hashes_table:
    kind, level, name, line = data
    kind2, level2, name2 = x.starts_section(line)
    assert kind == kind2, (kind, kind2, repr(line))
    assert level == level2, (level, level2, repr(line))
    assert name == name2, (name, name2, repr(line))
underline_table = (
    (None,  '--\n'),
    (None,  '---\n'),
    ('-',   '----\n'),
    ('-',   '-----\n'),
    #
    (None,  '==\n'),
    (None,  '===\n'),
    ('=',   '====\n'),
    ('=',   '====-\n'),
)
for data in underline_table:
    kind, line = data
    kind2, level2, name2 = x.starts_section(line)
    assert kind == kind2, (kind, kind2, repr(line))
    assert level2 == 1 if kind == '#' else 2, (level2, repr(line))
    assert name2 is None, (name2, repr(line))
</t>
<t tx="ekr.20161125031613.1">def show_failure1(self, lines1, lines2, parent, trace_all, trace_status):
    '''Print traces when first checks fail.'''
    if trace_status:
        g.trace('===== %s NOT OK cleaning LWS' % self.name)
    if trace_all:
        self.trace_lines(lines1, lines2, parent)
</t>
<t tx="ekr.20161125042407.1"></t>
<t tx="ekr.20161125042407.2">&lt;&lt; define s &gt;&gt;

try:
    root = None
    c.importCommands.markdownUnitTest(p,s=s,showTree=True) # Must be true.
    table = (
        (1, 'Top'),
        (2, 'Section 1#'),
        (2, 'Section 2'),
        (3, 'Section 2.1'),
        (4, 'Section 2.1.1'),
        (3, 'Section 2.2'),
        (2, 'Section 3'),
    )
    after = p.nodeAfterTree()
    root = p.firstChild().next()
    assert root.h.startswith('@@auto-m'), root.h
    p = root.firstChild()
    for n, h in table:
        n2 = p.level() - root.level()
        assert h == p.h, (h, p.h)
        assert n == n2, (n, n2, p.h)
        p.moveToThreadNext()
    assert p == after, p.h
finally:
    if 1:
        root = p.firstChild().next()
        if root:
            root.doDelete()
            c.redraw()
</t>
<t tx="ekr.20161125042407.3">s = '''\
#Top
The top section

##Section 1#
section 1, line 1
section 1, line 2

##Section 2
section 2, line 1

###Section 2.1
section 2.1, line 1

####Section 2.1.1
section 2.2.1 line 1

###Section 2.2

##Section 3
Section 3, line 1

'''
</t>
<t tx="ekr.20161125042407.4">&lt;&lt; define s &gt;&gt;

try:
    c.importCommands.markdownUnitTest(p,s=s,showTree=True) # Must be True.
    table = (
        (1, 'Top'),
        (2, 'Section 1'),
        (2, 'Section 2'),
        (3, 'Section 2.1'),
        (4, 'Section 2.1.1'),
        (3, 'Section 2.2'),
        (2, 'Section 3'),
    )
    after = p.nodeAfterTree()
    root = p.firstChild().next()
    assert root.h.startswith('@@auto-m'), root.h
    p = root.firstChild()
    for n, h in table:
        n2 = p.level() - root.level()
        assert h == p.h, (h, p.h)
        assert n == n2, (n, n2, p.h)
        p.moveToThreadNext()
    assert p == after, p.h
finally:
    if 1:
        root = p.firstChild().next()
        if root:
            root.doDelete()
            c.redraw()
</t>
<t tx="ekr.20161125065549.1">@others

Warning: this node is ignored when writing this file.

@language plain
@tabwidth -4
@ignore
</t>
<t tx="ekr.20161125065549.10"></t>
<t tx="ekr.20161125065549.11">: Sec 3-1-1-1-1-1
</t>
<t tx="ekr.20161125065549.12">Sec 3.1
</t>
<t tx="ekr.20161125065549.2">Sec 1.
</t>
<t tx="ekr.20161125065549.3">Sec 2.
</t>
<t tx="ekr.20161125065549.4">Sec 2.1
</t>
<t tx="ekr.20161125065549.5">Sec 2.1.1
</t>
<t tx="ekr.20161125065549.6"></t>
<t tx="ekr.20161125065549.7"></t>
<t tx="ekr.20161125065549.8"></t>
<t tx="ekr.20161125065549.9"></t>
<t tx="ekr.20161125065725.1">@others

Warning: this node is ignored when writing this file.

@language plain
@tabwidth -4
@ignore
</t>
<t tx="ekr.20161125065725.10"></t>
<t tx="ekr.20161125065725.11">: Sec 3-1-1-1-1-1
</t>
<t tx="ekr.20161125065725.12">Sec 3.1
</t>
<t tx="ekr.20161125065725.2">Sec 1.
</t>
<t tx="ekr.20161125065725.3">Sec 2.
</t>
<t tx="ekr.20161125065725.4">Sec 2.1
</t>
<t tx="ekr.20161125065725.5">Sec 2.1.1
</t>
<t tx="ekr.20161125065725.6"></t>
<t tx="ekr.20161125065725.7"></t>
<t tx="ekr.20161125065725.8"></t>
<t tx="ekr.20161125065725.9"></t>
<t tx="ekr.20161125065851.1">@others

Warning: this node is ignored when writing this file.

@language plain
@tabwidth -4
@ignore
</t>
<t tx="ekr.20161125065851.10"></t>
<t tx="ekr.20161125065851.11">: Sec 3-1-1-1-1-1
</t>
<t tx="ekr.20161125065851.12">Sec 3.1
</t>
<t tx="ekr.20161125065851.2">Sec 1.
</t>
<t tx="ekr.20161125065851.3">Sec 2.
</t>
<t tx="ekr.20161125065851.4">Sec 2.1
</t>
<t tx="ekr.20161125065851.5">Sec 2.1.1
</t>
<t tx="ekr.20161125065851.6"></t>
<t tx="ekr.20161125065851.7"></t>
<t tx="ekr.20161125065851.8"></t>
<t tx="ekr.20161125065851.9"></t>
<t tx="ekr.20161125070122.1">@others

Warning: this node is ignored when writing this file.

@language plain
@tabwidth -4
@ignore
</t>
<t tx="ekr.20161125070122.10"></t>
<t tx="ekr.20161125070122.11">: Sec 3-1-1-1-1-1
</t>
<t tx="ekr.20161125070122.12">Sec 3.1
</t>
<t tx="ekr.20161125070122.2">Sec 1.
</t>
<t tx="ekr.20161125070122.3">Sec 2.
</t>
<t tx="ekr.20161125070122.4">Sec 2.1
</t>
<t tx="ekr.20161125070122.5">Sec 2.1.1
</t>
<t tx="ekr.20161125070122.6"></t>
<t tx="ekr.20161125070122.7"></t>
<t tx="ekr.20161125070122.8"></t>
<t tx="ekr.20161125070122.9"></t>
<t tx="ekr.20161125070244.1">@others

Warning: this node is ignored when writing this file.

@language plain
@tabwidth -4
@ignore
</t>
<t tx="ekr.20161125070244.10"></t>
<t tx="ekr.20161125070244.11">: Sec 3-1-1-1-1-1
</t>
<t tx="ekr.20161125070244.12">Sec 3.1
</t>
<t tx="ekr.20161125070244.2">Sec 1.
</t>
<t tx="ekr.20161125070244.3">Sec 2.
</t>
<t tx="ekr.20161125070244.4">Sec 2.1
</t>
<t tx="ekr.20161125070244.5">Sec 2.1.1
</t>
<t tx="ekr.20161125070244.6"></t>
<t tx="ekr.20161125070244.7"></t>
<t tx="ekr.20161125070244.8"></t>
<t tx="ekr.20161125070244.9"></t>
<t tx="ekr.20161125070315.1">@others

Warning: this node is ignored when writing this file.

@language plain
@tabwidth -4
@ignore
</t>
<t tx="ekr.20161125070315.10"></t>
<t tx="ekr.20161125070315.11">: Sec 3-1-1-1-1-1
</t>
<t tx="ekr.20161125070315.12">Sec 3.1
</t>
<t tx="ekr.20161125070315.2">Sec 1.
</t>
<t tx="ekr.20161125070315.3">Sec 2.
</t>
<t tx="ekr.20161125070315.4">Sec 2.1
</t>
<t tx="ekr.20161125070315.5">Sec 2.1.1
</t>
<t tx="ekr.20161125070315.6"></t>
<t tx="ekr.20161125070315.7"></t>
<t tx="ekr.20161125070315.8"></t>
<t tx="ekr.20161125070315.9"></t>
<t tx="ekr.20161125070422.1">@others

Warning: this node is ignored when writing this file.

@language plain
@tabwidth -4
@ignore
</t>
<t tx="ekr.20161125070422.10"></t>
<t tx="ekr.20161125070422.11">: Sec 3-1-1-1-1-1
</t>
<t tx="ekr.20161125070422.12">Sec 3.1
</t>
<t tx="ekr.20161125070422.2">Sec 1.
</t>
<t tx="ekr.20161125070422.3">Sec 2.
</t>
<t tx="ekr.20161125070422.4">Sec 2.1
</t>
<t tx="ekr.20161125070422.5">Sec 2.1.1
</t>
<t tx="ekr.20161125070422.6"></t>
<t tx="ekr.20161125070422.7"></t>
<t tx="ekr.20161125070422.8"></t>
<t tx="ekr.20161125070422.9"></t>
<t tx="ekr.20161125070847.1">@others

Warning: this node is ignored when writing this file.

@language plain
@tabwidth -4
@ignore
</t>
<t tx="ekr.20161125070847.10"></t>
<t tx="ekr.20161125070847.11">: Sec 3-1-1-1-1-1
</t>
<t tx="ekr.20161125070847.12">Sec 3.1
</t>
<t tx="ekr.20161125070847.2">Sec 1.
</t>
<t tx="ekr.20161125070847.3">Sec 2.
</t>
<t tx="ekr.20161125070847.4">Sec 2.1
</t>
<t tx="ekr.20161125070847.5">Sec 2.1.1
</t>
<t tx="ekr.20161125070847.6"></t>
<t tx="ekr.20161125070847.7"></t>
<t tx="ekr.20161125070847.8"></t>
<t tx="ekr.20161125070847.9"></t>
<t tx="ekr.20161125071301.1">@others

Warning: this node is ignored when writing this file.

@language plain
@tabwidth -4
@ignore
</t>
<t tx="ekr.20161125071301.10"></t>
<t tx="ekr.20161125071301.11">: Sec 3-1-1-1-1-1
</t>
<t tx="ekr.20161125071301.12">Sec 3.1
</t>
<t tx="ekr.20161125071301.2">Sec 1.
</t>
<t tx="ekr.20161125071301.3">Sec 2.
</t>
<t tx="ekr.20161125071301.4">Sec 2.1
</t>
<t tx="ekr.20161125071301.5">Sec 2.1.1
</t>
<t tx="ekr.20161125071301.6"></t>
<t tx="ekr.20161125071301.7"></t>
<t tx="ekr.20161125071301.8"></t>
<t tx="ekr.20161125071301.9"></t>
<t tx="ekr.20161125071330.1">@others

Warning: this node is ignored when writing this file.

@language plain
@tabwidth -4
@ignore
</t>
<t tx="ekr.20161125071330.10"></t>
<t tx="ekr.20161125071330.11">: Sec 3-1-1-1-1-1
</t>
<t tx="ekr.20161125071330.12">Sec 3.1
</t>
<t tx="ekr.20161125071330.2">Sec 1.
</t>
<t tx="ekr.20161125071330.3">Sec 2.
</t>
<t tx="ekr.20161125071330.4">Sec 2.1
</t>
<t tx="ekr.20161125071330.5">Sec 2.1.1
</t>
<t tx="ekr.20161125071330.6"></t>
<t tx="ekr.20161125071330.7"></t>
<t tx="ekr.20161125071330.8"></t>
<t tx="ekr.20161125071330.9"></t>
<t tx="ekr.20161125071430.1">@others

Warning: this node is ignored when writing this file.

@language plain
@tabwidth -4
@ignore
</t>
<t tx="ekr.20161125071430.10"></t>
<t tx="ekr.20161125071430.11">: Sec 3-1-1-1-1-1
</t>
<t tx="ekr.20161125071430.12">Sec 3.1
</t>
<t tx="ekr.20161125071430.2">Sec 1.
</t>
<t tx="ekr.20161125071430.3">Sec 2.
</t>
<t tx="ekr.20161125071430.4">Sec 2.1
</t>
<t tx="ekr.20161125071430.5">Sec 2.1.1
</t>
<t tx="ekr.20161125071430.6"></t>
<t tx="ekr.20161125071430.7"></t>
<t tx="ekr.20161125071430.8"></t>
<t tx="ekr.20161125071430.9"></t>
<t tx="ekr.20161125073257.1">@others

Warning: this node is ignored when writing this file.

@language plain
@tabwidth -4
</t>
<t tx="ekr.20161125073257.10"></t>
<t tx="ekr.20161125073257.11">: Sec 3-1-1-1-1-1
</t>
<t tx="ekr.20161125073257.12">Sec 3.1
</t>
<t tx="ekr.20161125073257.2">Sec 1.
</t>
<t tx="ekr.20161125073257.3">Sec 2.
</t>
<t tx="ekr.20161125073257.4">Sec 2.1
</t>
<t tx="ekr.20161125073257.5">Sec 2.1.1
</t>
<t tx="ekr.20161125073257.6"></t>
<t tx="ekr.20161125073257.7"></t>
<t tx="ekr.20161125073257.8"></t>
<t tx="ekr.20161125073257.9"></t>
<t tx="ekr.20161125073426.1">@others

Warning: this node is ignored when writing this file.

@language plain
@tabwidth -4
</t>
<t tx="ekr.20161125073426.10"></t>
<t tx="ekr.20161125073426.11">: Sec 3-1-1-1-1-1
</t>
<t tx="ekr.20161125073426.12">Sec 3.1
</t>
<t tx="ekr.20161125073426.2">Sec 1.
</t>
<t tx="ekr.20161125073426.3">Sec 2.
</t>
<t tx="ekr.20161125073426.4">Sec 2.1
</t>
<t tx="ekr.20161125073426.5">Sec 2.1.1
</t>
<t tx="ekr.20161125073426.6"></t>
<t tx="ekr.20161125073426.7"></t>
<t tx="ekr.20161125073426.8"></t>
<t tx="ekr.20161125073426.9"></t>
<t tx="ekr.20161125083451.1"></t>
<t tx="ekr.20161125083633.1">if 1:
    # The preamble...
    g.cls()
    if c.isChanged(): c.save()
    # import leo
    import leo.core.leoImport as leoImport
    import leo.plugins.importers.linescanner as linescanner
    import leo.plugins.importers.markdown
    import leo.plugins.writers.markdown
    # Reload all.
    import imp
    imp.reload(leo.plugins.importers.linescanner)
    imp.reload(leo.plugins.importers.markdown)
    imp.reload(leo.plugins.writers.markdown)
    imp.reload(leoImport)
    markdown = leo.plugins.importers.markdown
    ic = leoImport.LeoImportCommands(c)
    x = markdown.Markdown_Importer(ic, atAuto=False)   
# insert test for markdown here.
s = '''\
Decl line.
# Header

After header text

## Subheader

After subheader text
'''

table = ('Header', 'Subheader')
try:
    ic.markdownUnitTest(p,s=s,showTree=True)
    if 1:
        root = c.p.firstChild()
        p2 = root.firstChild()
        for h in table:
            assert p2.h == h, (p2.h, h)
            p2.moveToThreadNext()
        assert not root.isAncestorOf(p2), p2.h # Extra nodes
finally:
    if 0:
        p.deleteAllChildren()
</t>
<t tx="ekr.20161125174423.1">def print_stack(self, stack):
    '''Print a stack of positions.'''
    g.printList([p.h for p in stack])
</t>
<t tx="ekr.20161125230713.1">s = '''\
=Top
====

The top section

-Section 1
----------

section 1, line 1
-- Not an underline
selction 1, line 2

-Section 2
----------

section 2, line 1

###Section 2.1

section 2.1, line 1

####Section 2.1.1

section 2.2.1 line 1

###Section 2.2
section 2.2, line 1.

-Section 3
----------

section 3, line 1

'''
</t>
<t tx="ekr.20161126051659.1">table = (
    '',
    ' ',
    '\n',
    'abc\nxyz',
)
for i, s in enumerate(table):
    if s.splitlines(True) != g.splitLines(s):
        print('%5r s.splitlines(): %s g.splitlines(s): %s' % (
            s, s.splitLines(True), g.splitLines(s)))
print('ran %s tests' % (i+1))</t>
<t tx="ekr.20161126074152.1">@nosearch
</t>
<t tx="ekr.20161126160955.1">'''
The @auto importer for restructured text.

This module must **not** be named rst, so as not to conflict with docutils.
'''
import leo.core.leoGlobals as g
import leo.plugins.importers.basescanner as basescanner
@others
importer_dict = {
    '@auto': ['@auto-rst',],
    'class': RstScanner,
    'extensions': ['.rst', '.rest',],
}
</t>
<t tx="ekr.20161126160955.10"># These do not affect parsing.

def startsComment(self, s, i):
    return False

def startsID(self, s, i):
    return False

def startsString(self, s, i):
    return False
</t>
<t tx="ekr.20161126160955.11">def startsHelper(self, s, i, kind, tags, tag=None):
    '''return True if s[i:] starts an rST section.
    Sets sigStart, sigEnd, sigId and codeEnd ivars.'''
    trace = False and not g.unitTesting
    verbose = True
    kind, name, next, ch = self.startsSection(s, i)
    if kind == 'plain': return False
    self.underlineCh = ch
    self.lastSectionLevel = self.sectionLevel
    self.sectionLevel = self.computeSectionLevel(ch, kind)
    self.sigStart = g.find_line_start(s, i)
    self.sigEnd = next
    self.sigId = name
    i = next + 1
    if trace: g.trace('sigId', self.sigId, 'next', next)
    while i &lt; len(s):
        progress = i
        i, j = g.getLine(s, i)
        kind, name, next, ch = self.startsSection(s, i)
        if trace and verbose: g.trace(kind, repr(s[i: j]))
        if kind in ('over', 'under'):
            break
        else:
            i = j
        assert i &gt; progress
    self.codeEnd = i
    if trace:
        if verbose:
            g.trace('found...\n%s' % s[self.sigStart: self.codeEnd])
        else:
            g.trace('level %s %s' % (self.sectionLevel, self.sigId))
    return True
</t>
<t tx="ekr.20161126160955.12">def startsSection(self, s, i):
    '''Scan a line and possible one or two other lines,
    looking for an underlined or overlined/underlined name.

    Return (kind,name,i):
        kind: in ('under','over','plain')
        name: the name of the underlined or overlined line.
        i: the following character if kind is not 'plain'
        ch: the underlining and possibly overlining character.
    '''
    trace = False and not g.unitTesting
    verbose = False
    # Under/overlines can not begin with whitespace.
    i1, j, nows, line = self.getLine(s, i)
    ch, kind = '', 'plain' # defaults.
    if nows and self.isUnderLine(line): # an overline.
        name_i = g.skip_line(s, i1)
        name_i, name_j = g.getLine(s, name_i)
        name = s[name_i: name_j].strip()
        next_i = g.skip_line(s, name_i)
        i, j, nows, line2 = self.getLine(s, next_i)
        n1, n2, n3 = len(line), len(name), len(line2)
        ch1, ch3 = line[0], line2 and line2[0]
        ok = (nows and self.isUnderLine(line2) and
            n1 &gt;= n2 and n2 &gt; 0 and n3 &gt;= n2 and ch1 == ch3)
        if ok:
            i += n3
            ch, kind = ch1, 'over'
            if ch1 not in self.underlines2:
                self.underlines2.append(ch1)
                if trace: g.trace('*** underlines2', self.underlines2, name)
            if trace and verbose:
                g.trace('\nline  %s\nname  %s\nline2 %s' % (
                    repr(line), repr(name), repr(line2))) #,'\n',g.callers(4))
    else:
        name = line.strip()
        i = g.skip_line(s, i1)
        i, j, nows2, line2 = self.getLine(s, i)
        n1, n2 = len(name), len(line2)
        # look ahead two lines.
        i3, j3 = g.getLine(s, j)
        name2 = s[i3: j3].strip()
        i4, j4, nows4, line4 = self.getLine(s, j3)
        n3, n4 = len(name2), len(line4)
        overline = (
            nows2 and self.isUnderLine(line2) and
            nows4 and self.isUnderLine(line4) and
            n3 &gt; 0 and n2 &gt;= n3 and n4 &gt;= n3)
        ok = (not overline and nows2 and self.isUnderLine(line2) and
            n1 &gt; 0 and n2 &gt;= n1)
        if ok:
            i += n2
            ch, kind = line2[0], 'under'
            if ch not in self.underlines1:
                self.underlines1.append(ch)
                if trace: g.trace('*** underlines1', self.underlines1, name)
            if trace and verbose: g.trace('\nname  %s\nline2 %s' % (
                repr(name), repr(line2)))
    return kind, name, i, ch
</t>
<t tx="ekr.20161126160955.13">def getLine(self, s, i):
    i, j = g.getLine(s, i)
    line = s[i: j]
    nows = i == g.skip_ws(s, i)
    line = line.strip()
    return i, j, nows, line
</t>
<t tx="ekr.20161126160955.2">class RstScanner(basescanner.BaseScanner):
    @others
</t>
<t tx="ekr.20161126160955.3">def __init__(self, importCommands, atAuto):
    # Init the base class.
    basescanner.BaseScanner.__init__(self, importCommands, atAuto=atAuto, language='rest')
    # Scanner overrides
    self.atAutoWarnsAboutLeadingWhitespace = True
    self.blockDelim1 = self.blockDelim2 = None
    self.classTags = []
    self.escapeSectionRefs = False
    self.functionSpelling = 'section'
    self.functionTags = []
    self.hasClasses = False
    self.ignoreBlankLines = True
    self.isRst = True
    self.lineCommentDelim = '..'
    self.outerBlockDelim1 = None
    self.sigFailTokens = []
    self.strict = False # Mismatches in leading whitespace are irrelevant.
    # Ivars unique to rst scanning &amp; code generation.
    self.lastParent = None # The previous parent.
    self.lastSectionLevel = 0 # The section level of previous section.
    self.sectionLevel = 0 # The section level of the just-parsed section.
    self.underlineCh = '' # The underlining character of the last-parsed section.
    self.underlines = "!\"#$%&amp;'()*+,-./:;&lt;=&gt;?@[\\]^_`{|}~" # valid rst underlines.
    self.underlines1 = [] # Underlining characters for underlines.
    self.underlines2 = [] # Underlining characters for over/underlines.
</t>
<t tx="ekr.20161126160955.4">def adjustParent(self, parent, headline):
    '''Return the proper parent of the new node.'''
    trace = False and not g.unitTesting
    level, lastLevel = self.sectionLevel, self.lastSectionLevel
    lastParent = self.lastParent
    if trace: g.trace('**entry level: %s lastLevel: %s lastParent: %s' % (
        level, lastLevel, lastParent and lastParent.h or '&lt;none&gt;'))
    if self.lastParent:
        if level &lt;= lastLevel:
            parent = lastParent.parent()
            while level &lt; lastLevel:
                level += 1
                parent = parent.parent()
        else: # level &gt; lastLevel.
            level -= 1
            parent = lastParent
            while level &gt; lastLevel:
                level -= 1
                h2 = '@rst-no-head %s' % headline
                body = ''
                parent = self.createFunctionNode(h2, body, parent)
    else:
        assert self.root
        self.lastParent = self.root
    if not parent:
        parent = self.root
    if trace: g.trace('level %s lastLevel %s %s returns %s' % (
        level, lastLevel, headline, parent.h))
    #self.lastSectionLevel = self.sectionLevel
    self.lastParent = parent.copy()
    return parent.copy()
</t>
<t tx="ekr.20161126160955.5">def computeBody(self, s, start, sigStart, codeEnd):
    '''Compute the body of an rst node.'''
    trace = False and not g.unitTesting
    body1 = s[start: sigStart]
    # Adjust start backwards to get a better undent.
    if body1.strip():
        while start &gt; 0 and s[start - 1] in (' ', '\t'):
            start -= 1
    # Never indent any text; discard the entire signature.
    body1 = s[start: sigStart]
    body2 = s[self.sigEnd + 1: codeEnd]
    body2 = g.removeLeadingBlankLines(body2) # 2009/12/28
    body = body1 + body2
    # Don't warn about missing tail newlines: they will be added.
    if trace: g.trace('body: %s' % repr(body))
    return body1, body2
</t>
<t tx="ekr.20161126160955.6">def computeSectionLevel(self, ch, kind):
    '''Return the section level of the underlining character ch.'''
    if kind == 'over':
        assert ch in self.underlines2
        level = 0
    else:
        level = 1 + self.underlines1.index(ch)
    if 0:
        g.trace('level: %s kind: %s ch: %s under2: %s under1: %s' % (
            level, kind, ch, self.underlines2, self.underlines1))
    return level
</t>
<t tx="ekr.20161126160955.7">def createDeclsNode(self, parent, s):
    '''Create a child node of parent containing s.'''
    # Create the node for the decls.
    headline = '@rst-no-head %s declarations' % self.methodName
    body = self.undentBody(s)
    self.createHeadline(parent, body, headline)
</t>
<t tx="ekr.20161126160955.8">def endGen(self, s):
    '''Remember the underlining characters in the root's uA.'''
    trace = False and not g.unitTesting
    p = self.root
    if p:
        tag = 'rst-import'
        d = p.v.u.get(tag, {})
        underlines1 = ''.join([str(z) for z in self.underlines1])
        underlines2 = ''.join([str(z) for z in self.underlines2])
        d['underlines1'] = underlines1
        d['underlines2'] = underlines2
        self.underlines1 = underlines1
        self.underlines2 = underlines2
        if trace: g.trace(repr(underlines1), repr(underlines2), g.callers(4))
        p.v.u[tag] = d
    # Append a warning to the root node.
    warningLines = (
        'Warning: this node is ignored when writing this file.',
        'However, @ @rst-options are recognized in this node.',
    )
    lines = ['.. %s' % (z) for z in warningLines]
    warning = '\n%s\n' % '\n'.join(lines)
    self.root.b = self.root.b + warning
</t>
<t tx="ekr.20161126160955.9">def isUnderLine(self, s):
    '''Return True if s consists of only the same rST underline character.'''
    if not s: return False
    ch1 = s[0]
    if ch1 not in self.underlines:
        return False
    for ch in s:
        if ch != ch1:
            return False
    return True
</t>
<t tx="ekr.20161126161149.1">def skip_heredoc_string(self, s, i):
    &lt;&lt; skip_heredoc docstrig &gt;&gt;
    j = i
    assert(g.match(s, i, "&lt;&lt;&lt;"))
    # pylint: disable=anomalous-backslash-in-string
    m = re.match("\&lt;\&lt;\&lt;([a-zA-Z_\x7f-\xff][a-zA-Z0-9_\x7f-\xff]*)", s[i:])
    if m is None:
        i += 3
        return i
    # 14-SEP-2002 DTHEIN: needed to add \n to find word, not just string
    delim = m.group(1) + '\n'
    i = g.skip_line(s, i) # 14-SEP-2002 DTHEIN: look after \n, not before
    n = len(s)
    while i &lt; n and not g.match(s, i, delim):
        i = g.skip_line(s, i) # 14-SEP-2002 DTHEIN: move past \n
    if i &gt;= n:
        g.scanError("Run on string: " + s[j: i])
    elif g.match(s, i, delim):
        i += len(delim)
    return i
</t>
<t tx="ekr.20161126161323.1">@nocolor-node
'''
08-SEP-2002 DTHEIN:  added function skip_heredoc_string
A heredoc string in PHP looks like:

  &lt;&lt;&lt;EOS
  This is my string.
  It is mine. I own it.
  No one else has it.
  EOS

It begins with &lt;&lt;&lt; plus a token (naming same as PHP variable names).
It ends with the token on a line by itself (must start in first position.
'''
</t>
<t tx="ekr.20161126182933.1">g.cls()
if c.isChanged(): c.save()
import imp
import leo.plugins.importers.pascal as pascal
imp.reload(pascal)
x = pascal.Pascal_Importer(c.importCommands, atAuto=False)    
block_pattern = x.pascal_block_pattern
clean_pattern = x.pascal_clean_pattern
table = (
    'procedure TForm1.FormCreate(Sender: TObject);\n',
)
state = g.Bunch(context='')
for line in table:
    print(line)
    print('block: %s' % x.starts_block(line, state, state))
    print('clean: %s' % x.clean_headline(line))
    print('')
</t>
<t tx="ekr.20161127102339.1">def ends_block(self, line, new_state, prev_state, stack):
    '''True if line does not end the block.'''
    # Comparing new_state against prev_state does not work for python.
    top = stack[-1]
    return new_state.level() &lt; top.state.level()
</t>
<t tx="ekr.20161127104048.1"></t>
<t tx="ekr.20161127104105.1"></t>
<t tx="ekr.20161127183204.1">@language rest
@wrap

Post: Simple importers: ini, otl, org, leo_rst?, markdown,
- Don't need separate ScanState classes,
  but we *do* need all the data in the 6-tuple.
- The Importer class could define x.level(standard_state).
  It would return 0 or 1 components of standard_state, or a tuple of components.
- All override v2_gen_lines in similar ways.</t>
<t tx="ekr.20161127192007.2">class Rst_Importer(Importer):
    '''The importer for the rst lanuage.'''

    def __init__(self, importCommands, atAuto):
        '''Rst_Importer.__init__'''
        # Init the base class.
        Importer.__init__(self,
            importCommands,
            atAuto = atAuto,
            language = 'rest',
            state_class = Rst_ScanState,
            strict = False,
        )
        # self.underlines = "!\"#$%&amp;'()*+,-./:;&lt;=&gt;?@[\\]^_`{|}~"
            # valid rst underlines.
        self.underlines = '=+*^~"\'`-:&gt;&lt;_'
            # writers.leo_rst.py genenerates only these underlines.
            # '#' is reserved for level 1.
        
    @others
</t>
<t tx="ekr.20161128025444.1">def scan_dict(self, context, i, s, d):
    '''
    i.scan_dict: Scan at position i of s with the give context and dict.
    Return the 6-tuple: (new_context, i, delta_c, delta_p, delta_s, bs_nl)
    '''
    trace = False and g.unitTesting
    trace_fail = False
    if trace and trace_fail: g.trace('='*20, repr(context))
    found = False
    delta_c = delta_p = delta_s = 0
    ch = s[i] # For traces.
    aList = d.get(ch)
    if aList and context:
        # In context.
        for data in aList:
            kind, pattern, ends = data
            if self.match(s, i, pattern):
                if ends == None:
                    found = True
                    new_context = context
                    break
                elif ends:
                    found = True
                    new_context = ''
                    break
                else:
                    pass # Ignore this match.
    elif aList:
        # Not in context.
        for data in aList:
            kind, pattern, new_context, deltas = data
            # try:
                # kind, pattern, new_context, deltas = data
            # except ValueError:
                # g.trace(data)
                # break
            if self.match(s, i, pattern):
                found = True
                if deltas:
                    delta_c, delta_p, delta_s = deltas
                break
    if found:
        if kind == 'all':
            i = len(s)
        elif kind == 'len+1':
            i += (len(pattern) + 1)
        else:
            assert kind == 'len', (kind, self.name)
            i += len(pattern)
        bs_nl = pattern == '\\\n'
        if trace:
            g.trace(
                '   MATCH: i: %s ch: %r kind: %r pattern: %r '
                'context: %r new_context: %r line: %r' % (
                    i, ch, kind, pattern, context, new_context, s))
            g.trace('deltas', delta_c, delta_p, delta_s)
            g.trace('data', data)
        return new_context, i, delta_c, delta_p, delta_s, bs_nl
    else:
        # No match: stay in present state. All deltas are zero.
        new_context = context
        if trace and trace_fail: g.trace(
            'NO MATCH: i: %s ch: %r context: %r line: %r' % (
                i, ch, context, s))
    return new_context, i+1, 0, 0, 0, False
</t>
<t tx="ekr.20161128025508.1">@nobeautify

def get_new_dict(self, context):
    '''
    Return a *general* state dictionary for the given context.
    Subclasses may override...
    '''
    trace = False and g.unitTesting
    comment, block1, block2 = self.single_comment, self.block1, self.block2
    
    def add_key(d, key, data):
        aList = d.get(key,[])
        aList.append(data)
        d[key] = aList

    if context:
        d = {
            # key    kind   pattern  ends?
            '\\':   [('len+1', '\\', None),],
            '"':    [('len', '"',    context == '"'),],
            "'":    [('len', "'",    context == "'"),],
        }
        if block1 and block2:
            add_key(d, block2[0], ('len', block1, True))
    else:
        # Not in any context.
        d = {
            # key    kind pattern new-ctx  deltas
            '\\':[('len+1', '\\', context, None),],
            '"':    [('len', '"', '"',     None),],
            "'":    [('len', "'", "'",     None),],
            '{':    [('len', '{', context, (1,0,0)),],
            '}':    [('len', '}', context, (-1,0,0)),],
            '(':    [('len', '(', context, (0,1,0)),],
            ')':    [('len', ')', context, (0,-1,0)),],
            '[':    [('len', '[', context, (0,0,1)),],
            ']':    [('len', ']', context, (0,0,-1)),],
        }
        if comment:
            add_key(d, comment[0], ('all', comment, '', None))
        if block1 and block2:
            add_key(d, block1[0], ('len', block1, block1, None))
    if trace: g.trace('created %s dict for %r state ' % (self.name, context))
    return d
</t>
<t tx="ekr.20161128190217.1"></t>
<t tx="ekr.20161129025022.1"></t>
<t tx="ekr.20161129040921.11">def post_pass(self, parent):
    '''A do-nothing post-pass for markdown.'''
</t>
<t tx="ekr.20161129040921.2">def gen_lines(self, s, parent):
    '''Node generator for markdown importer.'''
    trace = False and g.unitTesting
    if not s or s.isspace():
        return
    self.inject_lines_ivar(parent)
    # We may as well do this first.  See warning below.
    self.add_line(parent, '@others\n')
    self.stack = [parent]
    skip = 0
    lines = g.splitLines(s)
    for i, line in enumerate(lines):
        if trace: g.trace('%2s %r' % (i+1, line))
        if skip &gt; 0:
            skip -= 1
        elif self.is_lookahead_overline(i, lines):
            level = self.ch_level(line[0])
            self.make_node(level, lines[i+1])
            skip = 2
        elif self.is_lookahead_underline(i, lines):
            level = self.ch_level(lines[i+1][0])
            self.make_node(level, line)
            skip = 1
        elif i == 0:
            p = self.make_dummy_node('!Dummy chapter')
            self.add_line(p, line)
        else:
            p = self.stack[-1]
            self.add_line(p, line)
    warning = '\nWarning: this node is ignored when writing this file.\n\n'
    self.add_line(parent, warning)
</t>
<t tx="ekr.20161129040921.5">def find_parent(self, level, h):
    '''
    Return the parent at the indicated level, allocating
    place-holder nodes as necessary.
    '''
    trace = False and g.unitTesting
    trace_stack = True
    assert level &gt; 0
    if trace: g.trace('===== level: %s len(stack): %s h: %s' % (
        level, len(self.stack), h))
    while level &lt; len(self.stack):
        p = self.stack.pop()
        if trace:
            g.trace('POP', len(self.get_lines(p)), p.h)
            if trace and trace_stack:
                self.print_list(self.get_lines(p))
    top = self.stack[-1]
    if trace: g.trace('TOP', top.h)
    child = self.create_child_node(
        parent = top,
        body = None,
        headline = h, # Leave the headline alone
    )
    self.stack.append(child)
    if trace and trace_stack: self.print_stack(self.stack)
    return self.stack[level]
</t>
<t tx="ekr.20161129040921.6">def make_dummy_node(self, headline):
    '''Make a decls node.'''
    parent = self.stack[-1]
    assert parent == self.root, repr(parent)
    child = self.create_child_node(
        parent = self.stack[-1],
        body = None,
        headline = headline,
    )
    self.stack.append(child)
    return child
</t>
<t tx="ekr.20161129040921.7">def make_node(self, level, headline):
    '''Create a new node, with the given headline.'''
    self.find_parent(level=level, h=headline)
</t>
<t tx="ekr.20161129040921.8">def is_underline(self, line, extra=None):
    '''True if the line consists of nothing but the same underlining characters.'''
    trace = False and g.unitTesting
    if trace: g.trace(repr(line))
    if line.isspace():
        return None
    chars = self.underlines
    if extra: chars = chars + extra
    ch1 = line[0]
    if ch1 not in chars:
        return None
    for ch in line.rstrip():
        if ch != ch1:
            return None
    return ch1

</t>
<t tx="ekr.20161129041436.1">section 1
+++++++++

Sec 1.
section 2
+++++++++

Sec 2.
@language python
@tabwidth -4
@ignore
</t>
<t tx="ekr.20161129041539.1">if 1:
    # The preamble...
    g.cls()
    if c.isChanged(): c.save()
    import leo
    import leo.core.leoImport as leoImport
    import leo.plugins.importers.linescanner as linescanner
    import leo.plugins.importers.leo_rst as leo_rst
    # Reload all.
    import imp
    imp.reload(leo.plugins.importers.linescanner)
    imp.reload(leo.plugins.importers.leo_rst)
    imp.reload(leoImport)
    ic = leoImport.LeoImportCommands(c)
else:
    ic = c.importCommands

s = '''\
#########
Chapter 1
#########

It was a dark and stormy night.

section 1
+++++++++

Sec 1.
section 2
+++++++++

Sec 2.
'''

table = (
    'Chapter 1',
    'section 1',
    'section 2',
)
try:
    ic.rstUnitTest(p,s=s,showTree=True)
    if 0:
        root = c.p.lastChild()
        assert root.h.startswith('@@'), root.h
        p2 = root.firstChild()
        for h in table:
            assert p2.h == h, (p2.h, h)
            p2.moveToThreadNext()
        assert not root.isAncestorOf(p2), p2.h # Extra nodes
finally:
    if 0:
        p.deleteAllChildren()
</t>
<t tx="ekr.20161129043705.1">def startsSection(self, s, i):
    '''Scan a line and possible one or two other lines,
    looking for an underlined or overlined/underlined name.

    Return (kind,name,i):
        kind: in ('under','over','plain')
        name: the name of the underlined or overlined line.
        i: the following character if kind is not 'plain'
        ch: the underlining and possibly overlining character.
    '''
    trace = False and not g.unitTesting
    verbose = False
    # Under/overlines can not begin with whitespace.
    i1, j, nows, line = self.getLine(s, i)
    ch, kind = '', 'plain' # defaults.
    if nows and self.isUnderLine(line): # an overline.
        name_i = g.skip_line(s, i1)
        name_i, name_j = g.getLine(s, name_i)
        name = s[name_i: name_j].strip()
        next_i = g.skip_line(s, name_i)
        i, j, nows, line2 = self.getLine(s, next_i)
        n1, n2, n3 = len(line), len(name), len(line2)
        ch1, ch3 = line[0], line2 and line2[0]
        ok = (nows and self.isUnderLine(line2) and
            n1 &gt;= n2 and n2 &gt; 0 and n3 &gt;= n2 and ch1 == ch3)
        if ok:
            i += n3
            ch, kind = ch1, 'over'
            if ch1 not in self.underlines2:
                self.underlines2.append(ch1)
                if trace: g.trace('*** underlines2', self.underlines2, name)
            if trace and verbose:
                g.trace('\nline  %s\nname  %s\nline2 %s' % (
                    repr(line), repr(name), repr(line2))) #,'\n',g.callers(4))
    else:
        name = line.strip()
        i = g.skip_line(s, i1)
        i, j, nows2, line2 = self.getLine(s, i)
        n1, n2 = len(name), len(line2)
        # look ahead two lines.
        i3, j3 = g.getLine(s, j)
        name2 = s[i3: j3].strip()
        i4, j4, nows4, line4 = self.getLine(s, j3)
        n3, n4 = len(name2), len(line4)
        overline = (
            nows2 and self.isUnderLine(line2) and
            nows4 and self.isUnderLine(line4) and
            n3 &gt; 0 and n2 &gt;= n3 and n4 &gt;= n3)
        ok = (not overline and nows2 and self.isUnderLine(line2) and
            n1 &gt; 0 and n2 &gt;= n1)
        if ok:
            i += n2
            ch, kind = line2[0], 'under'
            if ch not in self.underlines1:
                self.underlines1.append(ch)
                if trace: g.trace('*** underlines1', self.underlines1, name)
            if trace and verbose: g.trace('\nname  %s\nline2 %s' % (
                repr(name), repr(line2)))
    return kind, name, i, ch
</t>
<t tx="ekr.20161129043705.2">def getLine(self, s, i):
    i, j = g.getLine(s, i)
    line = s[i: j]
    nows = i == g.skip_ws(s, i)
    line = line.strip()
    return i, j, nows, line
</t>
<t tx="ekr.20161129045020.1">rst_seen = {'#': 1,}
rst_level = 0 # A trick.

def ch_level(self, ch):
    '''Return the underlining level associated with ch.'''
    assert ch == '#' or ch in self.underlines, (repr(ch), g.callers())
    d = self.rst_seen
    if ch in d:
        return d.get(ch)
    else:
        self.rst_level += 1
        d[ch] = self.rst_level
        return self.rst_level
</t>
<t tx="ekr.20161129111503.1">def is_lookahead_overline(self, i, lines):
    '''True if lines[i:i+2] form an overlined/underlined line.'''
    if i + 2 &lt; len(lines):
        line0 = lines[i]
        line1 = lines[i+1]
        line2 = lines[i+2]
        ch0 = self.is_underline(line0, extra='#')
        ch1 = self.is_underline(line1)
        ch2 = self.is_underline(line2, extra='#')
        return (
            ch0 and ch2 and ch0 == ch2 and 
            not ch1 and
            len(line1) &gt;= 4 and
            len(line0) &gt;= len(line1) and
            len(line2) &gt;= len(line1)
        )
    else:
        return False
</t>
<t tx="ekr.20161129112703.1">def is_lookahead_underline(self, i, lines):
    '''True if lines[i:i+1] form an underlined line.'''
    if i + 1 &lt; len(lines):
        line0 = lines[i]
        line1 = lines[i+1]
        ch0 = self.is_underline(line0)
        ch1 = self.is_underline(line1)
        return not ch0 and ch1 and 4 &lt;= len(line1) &lt;= len(line0)
    else:
        return False
</t>
<t tx="ekr.20161129115318.1"></t>
<t tx="ekr.20161130053858.1">Leading text in root node of subtree

Etc. etc.

### A level one node ######################################################

This would be the text in this level one node.

And this.

### Another level one node ################################################

Another one

#### A level 2 node #######################################################

See what we did there - one more '#' - this is a subnode.

</t>
<t tx="ekr.20161130054748.1"></t>
<t tx="ekr.20161130060355.1">'''
The write code for @auto-rst and other reStructuredText nodes.
This is very different from rst3's write code.

This module must **not** be named rst, so as not to conflict with docutils.
'''
# pylint: disable=unused-import
import leo.core.leoGlobals as g
import leo.plugins.writers.basewriter as basewriter
@others
writer_dict = {
    '@auto': ['@auto-rst',],
    'class': RstWriter,
    'extensions': ['.rst', '.rest',],
}
</t>
<t tx="ekr.20161130060355.2">class RstWriter(basewriter.BaseWriter):
    '''
    The writer class for @auto-rst and other reStructuredText nodes.
    This is *very* different from rst3 command's write code.
    '''
    # def __init__(self,c):
        # basewriter.BaseWriter.__init__(self,c)
    @others
</t>
<t tx="ekr.20161130060355.3">def underline_char(self, p, root_level):
    '''Return the underlining character for position p.'''
    underlines = '=+*^~"\'`-:&gt;&lt;_'
    i = p.level() - root_level
    return underlines[min(i, len(underlines) - 1)]
</t>
<t tx="ekr.20161130060355.4">def write(self, root, forceSentinels=False):
    '''Write an @auto tree containing imported rST code.'''
    trace = True # and g.unitTesting
    if trace:
        g.trace('=' * 40, root.h)
    root_level = root.level()
    for p in root.subtree():
        if forceSentinels:
            self.put_node_sentinel(p, '.. ')
        ch = self.underline_char(p, root_level)
        # Put the underlined headline
        if p.h.startswith('!'):
            pass # New in Leo 5.5.
        else:
            self.put(p.h)
            # Fix #242: @auto-rst open/save error.
            n = max(4, len(g.toEncodedString(p.h, reportErrors=False)))
            self.put(ch * n)
        if 0: # The old way: just put the line:
            # Fix bug 122: @auto-rst` should add an empty line after a heading.
            self.put('\n')
            for s in p.b.splitlines(False):
                self.put(s)
        else:
            lines = p.b.splitlines(False)
            if trace: g.printList(lines)
            if lines and lines[0].strip():
                self.put('')
            # Put the body.
            for s in lines: ### p.b.splitlines(False):
                self.put(s)
    root.setVisited()
    return True
</t>
<t tx="ekr.20161130060525.1">section 1
+++++++++

Sec 1.
section 2
+++++++++

Sec 2.
</t>
<t tx="ekr.20161202063728.1"></t>
<t tx="rogererens.20041130095659">@ It is possible to link to nodes within the same file.  However clones might be better.
</t>
</tnodes>
</leo_file>
