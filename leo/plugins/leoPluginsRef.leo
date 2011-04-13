<?xml version="1.0" encoding="utf-8"?>
<?xml-stylesheet ekr_test?>
<leo_file>
<leo_header file_format="2" tnodes="0" max_tnode_index="0" clone_windows="0"/>
<globals body_outline_ratio="0.5" body_secondary_ratio="0.5">
	<global_window_position top="50" left="50" height="500" width="700"/>
	<global_log_window_position top="0" left="0" height="0" width="0"/>
</globals>
<preferences/>
<find_panel_settings/>
<vnodes>
<v t="ekr.20041211035618"><vh>Startup</vh>
<v t="ekr.20050217093214"><vh>@settings</vh>
<v t="ekr.20050328101812"><vh>@page http plugin</vh>
<v t="ekr.20050328101812.1"><vh>@bool http_active = False</vh></v>
<v t="ekr.20050328101812.2"><vh>@int  port = 8080</vh></v>
<v t="ekr.20050328101812.3"><vh>@string rst_http_attributename = rst_http_attribute</vh></v>
</v>
<v t="ekr.20100910115903.5597"><vh>screenshot settings</vh>
<v t="ekr.20100910115903.5599"><vh>@string screenshot-bin = "c:\Program Files (x86)\Inkscape\inkscape.exe"</vh></v>
</v>
</v>
<v t="ekr.20060924180348"><vh>buttons</vh>
<v t="ekr.20080519084304.2"><vh>@@button change leo imports</vh></v>
<v t="ekr.20101112124740.5432"><vh>@button preview</vh></v>
</v>
<v t="ekr.20080515173014.1"><vh>regex: replace w.bind by c.bind(w...)</vh></v>
<v t="ekr.20100102164842.5328"><vh>Script: count pages</vh></v>
<v t="ekr.20101110084839.5680"><vh>Script: plugins not in this file</vh></v>
</v>
<v t="ekr.20090430075506.4"><vh>Notes &amp; to-do</vh>
<v t="ekr.20090430075506.3"><vh>@file leoPluginNotes.txt</vh></v>
</v>
<v t="ekr.20100909111553.5583"><vh>Unit tests</vh>
<v t="ekr.20100909121239.5797"><vh>@ignore</vh>
<v t="ekr.20100909121239.5670"><vh>@test get_directive_path</vh></v>
<v t="ekr.20100909121239.5951"><vh>@test find_at_screenshot_tree_node</vh></v>
<v t="ekr.20100909193419.5596"><vh>set g.app.unitTestGui</vh></v>
</v>
<v t="ekr.20100909111553.5588"><vh>@mark-for-unit-tests</vh></v>
</v>
<v t="ekr.20080707101341.1"><vh>@file ../modes/forth.py</vh></v>
<v t="edream.110203113231.618" a="E"><vh>Plugins</vh>
<v t="EKR.20040517090508"><vh>  Enable plugins using @enabled-plugins nodes</vh></v>
<v t="ekr.20050303051035"><vh>  Templates</vh>
<v t="ekr.20041114102139"><vh>Notes for plugin writers</vh></v>
<v t="ekr.20050306071629"><vh>Template for plugins that override commander methods</vh>
<v t="ekr.20050306071629.1"><vh>&lt;&lt; docstring &gt;&gt;</vh></v>
<v t="ekr.20050306071629.2"><vh>&lt;&lt; version history &gt;&gt;</vh></v>
<v t="ekr.20050306071629.3"><vh>&lt;&lt; imports &gt;&gt;</vh></v>
<v t="ekr.20050306071629.4"><vh>init</vh></v>
<v t="ekr.20050306071540"><vh>onStart2</vh></v>
</v>
<v t="ekr.20050303051035.2"><vh>Template for Tk plugin with per-commander controller class</vh>
<v t="ekr.20050303051035.3"><vh>&lt;&lt; docstring &gt;&gt;</vh></v>
<v t="ekr.20050303051035.4"><vh>&lt;&lt; version history &gt;&gt;</vh></v>
<v t="ekr.20050303051035.5"><vh>&lt;&lt; imports &gt;&gt;</vh></v>
<v t="ekr.20050303051101"><vh>init</vh></v>
<v t="ekr.20050303051150"><vh>onCreate</vh></v>
<v t="ekr.20050303051222"><vh>class pluginController</vh>
<v t="ekr.20050303051222.1"><vh>__init__</vh></v>
</v>
</v>
</v>
<v t="ekr.20101110150056.9453" a="E"><vh> Qt only plugins</vh>
<v t="tbrown.20091029123555.5319" descendentVnodeUnknownAttributes="7d71005503302e3571017d710258040000007465737471037d710458050000005f6564697471057d7106580400000074686973710758120000006f6b20686f77206120626f757420746869737108737373732e"><vh>@file attrib_edit.py</vh></v>
<v t="ville.20090310191936.10"><vh>@file colorize_headlines.py</vh></v>
<v t="ekr.20090701111504.5294"><vh>@file contextmenu.py</vh></v>
<v t="ville.20090518182905.5419"><vh>@file nav_qt.py</vh></v>
<v t="ekr.20090622063842.5264"><vh>@file projectwizard.py</vh></v>
<v t="ville.20090314215508.4"><vh>@file quicksearch.py</vh></v>
<v t="ekr.20101104190737.5629"><vh>@file scrolledmessage.py</vh></v>
<v t="ville.20090815203828.5235"><vh>@file spydershell.py</vh></v>
<v t="ekr.20100103093121.5329"><vh>@file stickynotes.py</vh></v>
<v t="tbrown.20090119215428.2"><vh>@file todo.py</vh></v>
<v t="tbrown.20100318101414.5990" a="E"
expanded="ekr.20110317024548.14375,ekr.20110317080650.14380,ekr.20101112195628.5426,"><vh>@file viewrendered.py</vh></v>
<v t="tbrown.20090206153748.1" a="E" descendentVnodeUnknownAttributes="7d7100285503302e3971017d710255065f626b6c6e6b71037d710428550179710547406d40000000000055017871064b0a550474797065710755086e6f646552656374710855056c696e6b7371095d710a75735503302e38710b7d710c68037d710d28680547406a00000000000068064b0a6807680868095d710e75735504302e3134710f7d711068037d711128680547407040000000000068064b0a6807680868095d711275735503302e3171137d711468037d711528680547404a00000000000068064b0a6807680868095d711675735503302e3071177d711868037d711928680547403a00000000000068064b0a6807680868095d711a75735503302e33711b7d711c68037d711d28680547405a00000000000068064b0a6807680868095d711e75735503302e32711f7d712068037d712128680547405380000000000068064b0a6807680868095d712275735503302e3571237d712468037d712528680547406380000000000068064b0a6807680868095d712675735503302e3471277d712868037d712928680547406040000000000068064b0a6807680868095d712a75735503302e36712b7d712c68037d712d286805474066c0000000000068064b0a6807680868095d712e7573550130712f7d713068037d71312868054b0068064b00680755096e6f64655461626c65713268095d713375735504302e313771347d713568037d713628680547407380000000000068064b0a6807680868095d713775735504302e313671387d713968037d713a286805474071e0000000000068064b0a6807680868095d713b75735504302e3131713c7d713d58060000005f626b6c6e6b713e7d713f28680547406ec00000000000680647406240000000000055047479706571404b0468095d714175735504302e313071427d714358060000005f626b6c6e6b71447d714528680547406d40000000000068064b0a550474797065714655086e6f646552656374714755056c696e6b7371485d714975735504302e3133714a7d714b68037d714c28680547407380000000000068064b0a6807680868095d714d75735504302e3132714e7d714f58060000005f626b6c6e6b71507d715128680547406d40000000000068064b0a5504747970657152680868095d71537573752e"
expanded="bob.20110119123023.7395,bob.20110119123023.7400,bob.20110119123023.7408,bob.20110120111825.3352,bob.20110121113659.3413,"><vh>@file graphcanvas.py</vh></v>
<v t="tbrown.20110203111907.5519"><vh>@file free_layout.py</vh></v>
<v t="ville.20110403115003.10348"
expanded="ekr.20110408065137.14221,ville.20110403115003.10355,ekr.20110408065137.14219,ekr.20110408065137.14226,ekr.20110407174428.5781,ekr.20110407174428.5780,"><vh>@file valuespace.py</vh></v>
<v t="ville.20110409151021.5691"><vh>newHeadline</vh></v>
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
<v t="edream.110203113231.916"><vh>@file examples/__overrideClasses.py</vh></v>
<v t="edream.110203113231.919"><vh>@file examples/override_commands.py</vh></v>
<v t="edream.110203113231.921"><vh>@file examples/redefine_put.py</vh></v>
<v t="ekr.20060621123339"><vh>@file examples/print_cp.py</vh></v>
<v t="ekr.20040828105233"><vh>@file examples/chinese_menu.py</vh></v>
<v t="EKR.20040517080202.3"><vh>@file examples/french_fm.py</vh></v>
</v>
<v t="ekr.20101110150056.9457"><vh>Experimental</vh>
<v t="ekr.20050402080206.8"><vh>@file LeoN.py</vh></v>
<v t="ekr.20101110092851.5742"><vh>@file leoOPML.py</vh></v>
<v t="ekr.20040205071616"><vh>@file mnplugins.py</vh></v>
<v t="ekr.20101110094759.5843"><vh>@file mod_speedups.py</vh></v>
<v t="ekr.20100103093121.5339"><vh>@file stickynotes_plus.py</vh></v>
<v t="ajones.20070122160142"><vh>@file textnode.py</vh></v>
<v t="ekr.20040331071919"><vh>Leo to AsciiDoc</vh>
<v t="ekr.20101110093449.5822"><vh>@file mod_leo2ascd.py</vh></v>
<v t="ekr.20101110150056.9445"><vh>@file mod_leo2ascd.txt</vh></v>
</v>
</v>
<v t="EKR.20040517075715" a="E"><vh>External programs</vh>
<v t="ekr.20110125103904.12504"><vh>@file gitarchive.py</vh></v>
<v t="ekr.20080201143145"><vh>@file ipython.py</vh></v>
<v t="EKR.20040517075715.1"><vh>@file mod_tempfname.py</vh></v>
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
<v t="tbrown.20080613095157.2" a="E"><vh>@file active_path.py</vh></v>
<v t="edream.110203113231.873"><vh>@file at_folder.py</vh></v>
<v t="ekr.20040915085351"><vh>@file at_produce.py</vh></v>
<v t="ktenney.20041211072654.1"><vh>@file at_view.py</vh></v>
<v t="tbrown.20081223111325.3" a="E"
expanded="ekr.20090616105756.3942,"><vh>@file backlink.py</vh></v>
<v t="tbrown.20070322113635"><vh>@file bookmarks.py</vh></v>
<v t="ekr.20060807103814.1"><vh>@file datenodes.py</vh></v>
<v t="ajones.20070122153625"><vh>@file expfolder.py</vh></v>
<v t="ekr.20040915105758.13"><vh>@file FileActions.py</vh></v>
<v t="ekr.20110110105526.5463"><vh>@file ftp.py</vh></v>
<v t="tbrown.20091214233510.5347"><vh>@file geotag.py</vh></v>
<v t="tbrown.20100228141752.5691"><vh>@file leocursor.py</vh></v>
<v t="dan.20090217132953.1"><vh>@file mime.py</vh></v>
<v t="mork.20041018204908.1"><vh>@file multifile.py</vh></v>
<v t="ekr.20040331151007"><vh>@file niceNosent.py</vh></v>
<v t="edream.110203113231.876"><vh>@file read_only_nodes.py</vh></v>
<v t="ekr.20040910070811.1"><vh>@file run_nodes.py</vh></v>
<v t="ekr.20040828103325"><vh>@file startfile.py</vh></v>
<v t="mork.20041010095009"><vh>@file xsltWithNodes.py</vh></v>
</v>
<v t="ekr.20081121105001.2080"><vh>Gui plugins</vh></v>
<v t="ekr.20041001210557" a="E"><vh>Scripting</vh>
<v t="tbrown.20100226095909.12777" a="E"
expanded="tbrown.20100226095909.12783,"><vh>@file leoscreen.py</vh></v>
<v t="ekr.20060328125248"><vh>@file mod_scripting.py</vh></v>
<v t="edream.110203113231.925"><vh>@file script_io_to_body.py</vh></v>
</v>
<v t="ekr.20050111122605"><vh>Servers</vh>
<v t="ville.20091009202416.10040"><vh>@file leoremote.py</vh></v>
<v t="EKR.20040517080250.1"><vh>@file mod_http.py</vh></v>
</v>
<v t="ekr.20101004082701.5674"><vh>Slideshows and screenshots</vh>
<v t="ekr.20060831165821"><vh>@file slideshow.py</vh></v>
<v t="ekr.20101121031443.5330"><vh>@file screenshots.py</vh></v>
</v>
<v t="ekr.20071113084440"><vh>Testing</vh>
<v t="ekr.20080214092357"><vh>@file test/ekr_test.py</vh></v>
<v t="ekr.20050130120433"><vh>@file test/failed_import.py</vh></v>
<v t="ekr.20071113085315"><vh>@file test/failed_to_load_plugin.py</vh></v>
<v t="ekr.20071113084440.1"><vh>@file test/syntax_error_plugin.py</vh></v>
<v t="ekr.20051016160700"><vh>@file testRegisterCommand.py</vh></v>
</v>
<v t="ekr.20050306081349" a="E"><vh>Text formatting</vh>
<v t="timo.20050213160555"><vh>@file bibtex.py</vh></v>
<v t="ekr.20070119094733.1"><vh>@file dtest.py</vh></v>
<v t="danr7.20060902215215.1"><vh>@file leo_to_html.py</vh></v>
<v t="danr7.20060902083957"><vh>@file leo_to_rtf.py</vh></v>
<v t="ville.20110409151021.5699" a="E"><vh>@file jinjarender.py</vh></v>
<v t="ekr.20050817132814"><vh>rst3</vh>
<v t="ekr.20090704103932.5160" a="E"><vh>@file leo_pdf.py</vh></v>
<v t="ekr.20050805162550"><vh>@file rst3.py</vh></v>
</v>
</v>
<v t="ekr.20040915073259"><vh>User interface</vh>
<v t="ekr.20061023142737"><vh> UNL plugin</vh>
<v t="ekr.20061023142737.1"><vh>Tests</vh>
<v t="rogererens.20041130095659"><vh>@url 'file: ./../../plugins/leoPlugins.leo#Plugins--&gt;UNL plugin--&gt;To do'</vh></v>
<v t="ekr.20061023141638"><vh>@url 'file:./../doc/leoDocs.leo#Users Guide--&gt;Basics--&gt;Customizing Leo'</vh></v>
<v t="ekr.20061023141459"><vh>@url 'Plugins--&gt;UNL plugin--&gt;@file UNL.py'</vh></v>
</v>
<v t="rogererens.20041013082304"><vh>@file UNL.py</vh></v>
</v>
<v t="ekr.20060328125925"><vh>@file chapter_hoist.py</vh></v>
<v t="ekr.20060506070443.1"><vh>@file detect_urls.py</vh></v>
<v t="mork.20041018162155.1"><vh>@file EditAttributes.py</vh></v>
<v t="tbrown.20090513125417.5244"><vh>@file interact.py</vh></v>
<v t="ekr.20040915073259.1"><vh>@file maximizeNewWindows.py</vh></v>
<v t="ekr.20101110093301.5818"><vh>@file mod_framesize.py</vh></v>
<v t="EKR.20040517080555.2"><vh>@file plugins_menu.py</vh></v>
<v t="ekr.20110304185833.14141"><vh>@file qt_plugin_manager.py</vh></v>
<v t="edream.110203113231.924"><vh>@file redirect_to_log.py</vh></v>
<v t="EKR.20040517080555.36"><vh>@file scripts_menu.py</vh></v>
<v t="ekr.20101110095202.5882"><vh>@file zenity_file_dialogs.py</vh></v>
</v>
<v t="ekr.20101110150056.9447"><vh>zz Tk only plugins</vh>
<v t="ekr.20101110150056.9469"><vh>Require plugins manager</vh>
<v t="pap.20041006184225"><vh>@file old_plugin_manager.py</vh></v>
<v t="ekr.20050329082101"><vh> AutoTrees</vh>
<v t="ekr.20050329082101.1"><vh>AutoTrees plugin</vh>
<v t="ekr.20050329082101.2"><vh>Introduction</vh></v>
<v t="ekr.20050329082101.3"><vh>Why use this?</vh></v>
<v t="ekr.20050329082101.4"><vh>Details</vh></v>
<v t="ekr.20050329082101.5"><vh>How do I create my own handlers?</vh></v>
</v>
<v t="ekr.20050329082101.6"><vh>Example handlers</vh>
<v t="ekr.20050329082101.7"><vh>Testing</vh>
<v t="ekr.20050329082101.8"><vh>@auto-test something</vh>
<v t="ekr.20050329082101.9"><vh>one</vh></v>
<v t="ekr.20050329082101.10"><vh>two</vh></v>
<v t="ekr.20050329082101.11"><vh>three</vh>
<v t="ekr.20050329082101.12"><vh>three-one</vh></v>
<v t="ekr.20050329082101.13"><vh>three-two</vh></v>
<v t="ekr.20050329082101.14"><vh>three-three</vh></v>
</v>
</v>
</v>
<v t="ekr.20050329082101.15"><vh>RSS</vh>
<v t="ekr.20050329082101.16"><vh>@auto-rss http://news.bbc.co.uk/rss/newsonline_uk_edition/world/rss091.xml</vh>
<v t="ekr.20050329092553"><vh>Hundreds die in Indonesia quake</vh></v>
<v t="ekr.20050329092553.1"><vh>Ousted Kyrgyz president defiant</vh></v>
<v t="ekr.20050329092553.2"><vh>Hair 'good source of stem cells'</vh></v>
<v t="ekr.20050329092553.3"><vh>Ashdown sacks top Bosnian Croat</vh></v>
<v t="ekr.20050329092553.4"><vh>Splits paralyse Iraqi parliament</vh></v>
<v t="ekr.20050329092553.5"><vh>Mongolians protest for new poll</vh></v>
<v t="ekr.20050329092553.6"><vh>Libya's Bulgarian medics appeal</vh></v>
<v t="ekr.20050329092553.7"><vh>Schiavo rivals 'agree to autopsy'</vh></v>
<v t="ekr.20050329092553.8"><vh>Would-be sex tourist, 87, jailed</vh></v>
<v t="ekr.20050329092553.9"><vh>Golf: Funk claims Players title</vh></v>
<v t="ekr.20050329092553.10"><vh>Cricket: Series win for Aussies</vh></v>
<v t="ekr.20050329092553.11"><vh>Angola says virus 'under control'</vh></v>
<v t="ekr.20050329092553.12"><vh>Mugabe criticises MDC 'traitors'</vh></v>
<v t="ekr.20050329092553.13"><vh>Ex-US diplomats round on Bolton</vh></v>
<v t="ekr.20050329092553.14"><vh>Brazil quits loan accord with IMF</vh></v>
<v t="ekr.20050329092553.15"><vh>Japanese economy hit by weak data</vh></v>
<v t="ekr.20050329092553.16"><vh>Donors pledge $40m for KR trials</vh></v>
<v t="ekr.20050329092553.17"><vh>Three Romanians missing in Iraq</vh></v>
<v t="ekr.20050329092553.18"><vh>Wolfowitz 'to meet EU officials'</vh></v>
<v t="ekr.20050329092553.19"><vh>Knesset rejects Gaza referendum</vh></v>
<v t="ekr.20050329092553.20"><vh>Militants to attend PLO meeting</vh></v>
<v t="ekr.20050329092553.21"><vh>South Asia cancels tsunami alerts</vh></v>
<v t="ekr.20050329092553.22"><vh>Devastation as Afghan dam bursts</vh></v>
<v t="ekr.20050329092553.23"><vh>Kyrgyzstan's friendly revolution</vh></v>
</v>
<v t="ekr.20050329082101.40"><vh>@auto-rss http://slashdot.org/index.rss</vh>
<v t="ekr.20050329092553.24"><vh>Followup on MS and Brazil in NY Times</vh></v>
<v t="ekr.20050329092553.25"><vh>A9.com with Syndicated Search</vh></v>
<v t="ekr.20050329092553.26"><vh>What's Next At Apple</vh></v>
<v t="ekr.20050329092553.27"><vh>Berkeley Grads' Identity Data Stolen</vh></v>
<v t="ekr.20050329092553.28"><vh>South Korean Gov't. Advocates Linux</vh></v>
<v t="ekr.20050329092553.29"><vh>MS, EU Agree on Name for Windows Sans Media Player</vh></v>
<v t="ekr.20050329092553.30"><vh>Blackbox (Finally) Updated</vh></v>
<v t="ekr.20050329092553.31"><vh>Your Face On the Big Screen</vh></v>
<v t="ekr.20050329092553.32"><vh>Ars Technica Builds Make Magazine's Steadicam</vh></v>
<v t="ekr.20050329092553.33"><vh>New Photovoltaics Made with Titanium Foil</vh></v>
</v>
<v t="ekr.20050329082101.51"><vh>@auto-rss http://www.python.org/channews.rdf</vh>
<v t="ekr.20050329082101.52"><vh>Python 2.4.1 (release candidate 1)</vh></v>
<v t="ekr.20050329082101.53"><vh>Greg Stein, of Google and Apache Software Foundation, to deliver keynote at PyCon</vh></v>
<v t="ekr.20050329082101.54"><vh>New RSS feed for python-dev summaries</vh></v>
<v t="ekr.20050329082101.55"><vh>Guido van Rossum speaking in Palo Alto</vh></v>
<v t="ekr.20050329082101.56"><vh>Python 2.3.5 (final)</vh></v>
<v t="ekr.20050329082101.57"><vh>Security advisory for SimpleXMLRPCServer.py.</vh></v>
<v t="ekr.20050329082101.58"><vh>Deadline for OSCON proposals</vh></v>
<v t="ekr.20050329082101.59"><vh>PyCon abstracts now available</vh></v>
<v t="ekr.20050329082101.60"><vh>PyCon preliminary schedule now available</vh></v>
<v t="ekr.20050329082101.61"><vh>PSF has awarded three grants</vh></v>
<v t="ekr.20050329082101.62"><vh>Python for Nokia Series 60 now available</vh></v>
<v t="ekr.20050329082101.63"><vh>Python 2.4 (final)</vh></v>
<v t="ekr.20050329082101.64"><vh>PyZine issue 7</vh></v>
<v t="ekr.20050329082101.65"><vh>PyCon 2005 Call for Proposals</vh></v>
<v t="ekr.20050329082101.66"><vh>Cameron Laird receives the Frank Willison Award</vh></v>
</v>
</v>
<v t="ekr.20050329082101.67"><vh>Remote</vh>
<v t="ekr.20050329082101.68"><vh>@auto-remote http://www.bbc.co.uk/news.html</vh></v>
</v>
<v t="ekr.20050329082101.69"><vh>Documentation</vh>
<v t="ekr.20050329082101.70"><vh>@auto-doc docutils.core</vh>
<v t="ekr.20050329082101.71"><vh>Component</vh>
<v t="ekr.20050329082101.72"><vh>component_type</vh></v>
<v t="ekr.20050329082101.73"><vh>default_transforms</vh></v>
<v t="ekr.20050329082101.74"><vh>supports</vh></v>
</v>
<v t="ekr.20050329082101.75"><vh>ConfigParser</vh>
<v t="ekr.20050329082101.76"><vh>OPTCRE</vh></v>
<v t="ekr.20050329082101.77"><vh>SECTCRE</vh></v>
<v t="ekr.20050329082101.78"><vh>add_section</vh></v>
<v t="ekr.20050329082101.79"><vh>standard_config_files</vh></v>
<v t="ekr.20050329082101.80"><vh>validation</vh></v>
</v>
<v t="ekr.20050329082101.81"><vh>OptionParser</vh>
<v t="ekr.20050329082101.82"><vh>default_error_encoding_error_handler</vh></v>
<v t="ekr.20050329082101.83"><vh>relative_path_settings</vh></v>
<v t="ekr.20050329082101.84"><vh>settings_defaults</vh></v>
<v t="ekr.20050329082101.85"><vh>settings_spec</vh></v>
<v t="ekr.20050329082101.86"><vh>standard_option_list</vh></v>
<v t="ekr.20050329082101.87"><vh>threshold_choices</vh></v>
<v t="ekr.20050329082101.88"><vh>thresholds</vh></v>
<v t="ekr.20050329082101.89"><vh>version_template</vh></v>
</v>
<v t="ekr.20050329082101.90"><vh>Publisher</vh></v>
<v t="ekr.20050329082101.91"><vh>default_description</vh></v>
<v t="ekr.20050329082101.92"><vh>default_usage</vh></v>
<v t="ekr.20050329082101.93"><vh>frontend</vh></v>
<v t="ekr.20050329082101.94"><vh>io</vh></v>
<v t="ekr.20050329082101.95"><vh>parsers</vh></v>
<v t="ekr.20050329082101.96"><vh>publish_cmdline</vh></v>
<v t="ekr.20050329082101.97"><vh>publish_file</vh></v>
<v t="ekr.20050329082101.98"><vh>publish_string</vh></v>
<v t="ekr.20050329082101.99"><vh>readers</vh></v>
<v t="ekr.20050329082101.100"><vh>sys</vh></v>
<v t="ekr.20050329082101.101"><vh>writers</vh></v>
</v>
</v>
<v t="ekr.20050329082101.102"><vh>News Reader</vh>
<v t="ekr.20050329082101.103"><vh>@auto-news news-server.houston.rr.com/comp.lang.python</vh>
<v t="ekr.20050329082101.104"><vh>@auto-newsitem 356970 - Easy way to check modules for python version compatibility?</vh></v>
<v t="ekr.20050329082101.105"><vh>@auto-newsitem 356972 - Q: Module Shared Data</vh></v>
<v t="ekr.20050329082101.106"><vh>@auto-newsitem 356978 - Re: __contains__ inconsistencies between Python 2.2 and 2.3</vh></v>
<v t="ekr.20050329082101.107"><vh>@auto-newsitem 356979 - Re: [Numeric] column vector faster than row vector in mat multiply?</vh></v>
<v t="ekr.20050329082101.108"><vh>@auto-newsitem 356986 - Python 2.4 removes None data type?</vh></v>
<v t="ekr.20050329082101.109"><vh>@auto-newsitem 356987 - Re: Integer From A Float List?!?</vh></v>
<v t="ekr.20050329082101.110"><vh>@auto-newsitem 356988 - Suspicious header</vh></v>
<v t="ekr.20050329082101.111"><vh>@auto-newsitem 356991 - Re: Suspicious header</vh></v>
<v t="ekr.20050329082101.112"><vh>@auto-newsitem 356992 - survey</vh></v>
<v t="ekr.20050329082101.113"><vh>@auto-newsitem 356993 - Re: Python 2.4 removes None data type?</vh></v>
</v>
</v>
</v>
<v t="ekr.20050329082101.114"><vh>AutoTrees Code</vh>
<v t="ekr.20050329082101.115"><vh>@file autotrees.py</vh></v>
<v t="ekr.20050329082101.145"><vh>@file trees\pluginsManager.txt</vh></v>
<v t="ekr.20050329082101.146"><vh>Example tree handlers</vh>
<v t="ekr.20050329082101.147"><vh>@file trees\test.py</vh></v>
<v t="ekr.20050329082101.150"><vh>@file trees\rss.py</vh></v>
<v t="ekr.20050329082101.153"><vh>@file trees\news.py</vh></v>
<v t="ekr.20050329082101.162"><vh>@file trees\remote.py</vh></v>
<v t="ekr.20050329082101.165"><vh>@file trees\doc.py</vh></v>
</v>
</v>
</v>
<v t="pap.20050605183206"><vh>@file leoupdate.py</vh></v>
</v>
<v t="ekr.20101110150056.9467"><vh>Require Tk</vh>
<v t="ekr.20050303080042"><vh> footprints</vh>
<v t="ekr.20050303080042.1"><vh>@nosent footprints.ini</vh></v>
<v t="pap.20041020001240"><vh>@file footprints.py</vh></v>
</v>
<v t="ekr.20080619090226.4"><vh> rClick plugin</vh>
<v t="bobjack.20080321133958.6"><vh>@file rClick.py</vh></v>
<v t="bobjack.20080619110105.2"><vh>@file rClickBasePluginClasses.py</vh></v>
</v>
<v t="ekr.20060513122613"><vh> xcc plugin</vh>
<v t="ekr.20060513122613.1"><vh>Examples</vh>
<v t="ekr.20060513122613.2"><vh>@xcc OpenGl.h</vh>
<v t="ekr.20060513122613.3"><vh>USE_OPENGL</vh></v>
<v t="ekr.20060513122613.4"><vh>Data Types</vh></v>
<v t="ekr.20060513122613.5"><vh>1.1</vh>
<v t="ekr.20060513122613.6"><vh>Defs</vh></v>
<v t="ekr.20060513122613.7"><vh>Procs</vh></v>
</v>
<v t="ekr.20060513122613.8"><vh>1.2</vh>
<v t="ekr.20060513122613.9"><vh>Defs</vh></v>
<v t="ekr.20060513122613.10"><vh>Procs</vh></v>
</v>
<v t="ekr.20060513122613.11"><vh>1.3</vh>
<v t="ekr.20060513122613.12"><vh>Defs</vh></v>
<v t="ekr.20060513122613.13"><vh>Procs</vh></v>
</v>
<v t="ekr.20060513122613.14"><vh>1.4</vh>
<v t="ekr.20060513122613.15"><vh>Defs</vh></v>
<v t="ekr.20060513122613.16"><vh>Procs</vh></v>
</v>
<v t="ekr.20060513122613.17"><vh>1.5</vh>
<v t="ekr.20060513122613.18"><vh>Defs</vh></v>
<v t="ekr.20060513122613.19"><vh>Procs</vh></v>
</v>
<v t="ekr.20060513122613.20"><vh>WGL</vh></v>
</v>
<v t="ekr.20060513122613.21"><vh>@xcc cltest\testprog</vh>
<v t="ekr.20060513122613.22"><vh>program</vh>
<v t="ekr.20060513122613.23"><vh>Header Directives</vh></v>
<v t="ekr.20060513122613.24"><vh>int WINAPI WinMain(HINSTANCE hinstance,HINSTANCE hprevinstance,LPSTR lpcmdline,int ncmdshow);!</vh></v>
</v>
</v>
<v t="ekr.20060513122613.25"><vh>@xcc gcctest\testprog</vh>
<v t="ekr.20060513122613.22"></v>
</v>
</v>
<v t="ekr.20060513122450"><vh>@file xcc_nodes.py</vh></v>
</v>
<v t="mork.20041020082242.1"><vh>@file base64Packager.py</vh></v>
<v t="tbrown.20060828111141"><vh>@file cleo.py</vh></v>
<v t="edream.110403140857.8"><vh>@file color_markup.py</vh></v>
<v t="ekr.20040916073636"><vh>@file ConceptualSort.py</vh></v>
<v t="mork.20041018091414.1"><vh>@file fastGotoNode.py</vh></v>
<v t="ekr.20071004090250"><vh>@file graphed.py</vh></v>
<v t="mork.20041018131258.1"><vh>@file groupOperations.py</vh></v>
<v t="ekr.20040331072607"><vh>@file hoist.py</vh></v>
<v t="edream.110203113231.753"><vh>@file image.py</vh></v>
<v t="ekr.20050328092641.4"><vh>@file Library.py</vh></v>
<v t="ekr.20050301095332"><vh>@file mod_labels.py</vh></v>
<v t="edream.110203113231.758"><vh>@file nav_buttons.py</vh></v>
<v t="pap.20051010170720"><vh>@file newButtons.py</vh></v>
<v t="mork.20041022155742.1"><vh>@file nodebar.py</vh></v>
<v t="ekr.20040108062655"><vh>@file nodenavigator.py</vh></v>
<v t="bob.20071218121513"><vh>@file open_with.py</vh></v>
<v t="ekr.20040828122150"><vh>@file pie_menus.py</vh></v>
<v t="ekr.20040108095351"><vh>@file rowcol.py</vh></v>
<v t="ekr.20040331153923"><vh>@file scheduler.py</vh></v>
<v t="ekr.20101110095202.5852"><vh>@file searchbar.py</vh></v>
<v t="ekr.20040107092135.2"><vh>@file searchbox.py</vh></v>
<v t="ekr.20060601151845"><vh>@file shortcut_button.py</vh></v>
<v t="ekr.20041017035937"><vh>@file table.py</vh></v>
<v t="mork.20041022090036.1"><vh>@file templates.py</vh></v>
<v t="ekr.20071010193720"><vh>@file threading_colorizer.py	</vh></v>
<v t="bobjack.20080424190315.2"><vh>@file toolbar.py</vh></v>
<v t="ekr.20040915075530"><vh>@file UASearch.py</vh></v>
<v t="ekr.20040831122004"><vh>@file UniversalScrolling.py</vh></v>
<v t="ekr.20040831115238"><vh>@file URLloader.py</vh></v>
</v>
</v>
</v>
<v t="ekr.20110308220444.14251"><vh>@@button test completer @key = Alt-8</vh>
<v t="ville.20091204224145.5355"></v>
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

Enable plugins by creating @enabled-plugins nodes in leoSettings files,
typically myLeoSettings.leo. See the node

Users Guide--&gt;Chapter 8: Customizing Leo--&gt;@rst
html\customizing.html--&gt;Specifying settings--&gt;Complex settings nodes

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

These plugins contain example code only.</t>
<t tx="ekr.20040915073259">@nocolor-node

These plugins add buttons and other widgets to the icon area or
affect Leo's panes and windows in various ways.

</t>
<t tx="ekr.20041001210557"></t>
<t tx="ekr.20041030092101">@ Notes by EKR:  The dyna plugin is a remarkable body of work by 'e'.  Have fun with it.

You may download the latest version at: http://rclick.netfirms.com/dyna_menu.py.html
</t>
<t tx="ekr.20041114102139">@nocolor

Comments
--------

Most of the comments in the style guide are comments *about* the style guide.
You would replace these comments with your own, or eliminate them entirely in
your plugin.

Docstrings
----------

Several plugins show the docstring, so please take care to do a good job of
describing what the plugin does and how to use it.

Directives
----------

Please put the following immediately following the plugin's docstring::

    @language python
    @tabwidth -4

Imports
-------
    
- Do *not* assume that modules like Tkinter, Pmw, etc. are always available. Use
  g.importExtension.

- Do *not* use either of the following kinds of imports::

    from m import *
    from m import x,y,z

- Your code should test whether modules have been imported only if those modules
  may not be available on all platforms.

Use the following lines only if your plugin uses a gui::

    if g.app.gui.guiName() == "tkinter":
        ...
        
Exceptions
----------

It is usually best *not* to catch exceptions in plugins: doHook catches all
exceptions and disables further calls to plugins.

If a plugin catches exceptions during startup it should do either raise the
exception again or provide an init function at the top level that reports the
failure by returning False.
        
Use separate nodes
------------------

**Please** define each function or method in a separate node! To make this work,
just put @others in the root of your plugin as shown. Note that @others may be
nested, as shown in class myClass.
</t>
<t tx="ekr.20041211035618"></t>
<t tx="ekr.20050111122605"></t>
<t tx="ekr.20050217093214">@nocolor</t>
<t tx="ekr.20050303051035">@nocolor-node

The following nodes show recommended style when writing plugins.</t>
<t tx="ekr.20050303051035.2">&lt;&lt; docstring &gt;&gt;

__version__ = '0.0'
&lt;&lt; version history &gt;&gt;

&lt;&lt; imports &gt;&gt;

@others</t>
<t tx="ekr.20050303051035.3">'''This docstring should be a clear, concise description of
what the plugin does and how to use it.
'''
</t>
<t tx="ekr.20050303051035.4">@

Put notes about each version here.</t>
<t tx="ekr.20050303051035.5">import leo.core.leoGlobals as g

Pmw = g.importExtension('Pmw',    pluginName=__name__,verbose=True,required=True)
Tk  = g.importExtension('Tkinter',pluginName=__name__,verbose=True,required=True)

# Whatever other imports your plugins uses.</t>
<t tx="ekr.20050303051101">def init ():
        
    ok = Pmw and Tk and g.app.gui.guiName() == "tkinter"

    if ok:
        if 1: # Use this if you want to create the commander class before the frame is fully created.
            g.registerHandler('before-create-leo-frame',onCreate)
        else: # Use this if you want to create the commander class after the frame is fully created.
            g.registerHandler('after-create-leo-frame',onCreate)
        g.plugin_signon(__name__)
        
    return ok</t>
<t tx="ekr.20050303051150">def onCreate (tag, keys):
    
    c = keys.get('c')
    if not c: return
    
    thePluginController = pluginController(c)
</t>
<t tx="ekr.20050303051222">class pluginController:
    
    @others</t>
<t tx="ekr.20050303051222.1">def __init__ (self,c):
    
    self.c = c
    # Warning: hook handlers must use keywords.get('c'), NOT self.c.</t>
<t tx="ekr.20050303080042"></t>
<t tx="ekr.20050303080042.1">[Main]

RefreshInterval = 60
ColdColour = blue
HotColour = red
HitsToHeatUp = 2
</t>
<t tx="ekr.20050306071540">def onStart2 (tag, keywords):
    
    """
    Showing how to define a global hook that affects all commanders.
    """

    import leo.core.leoTkinterFrame as leoTkinterFrame
    log = leoTkinterFrame.leoTkinterLog
    
    # Replace frame.put with newPut (not shown).
    g.funcToMethod(newPut,log,"put")</t>
<t tx="ekr.20050306071629">&lt;&lt; docstring &gt;&gt;

__version__ = '0.0'
&lt;&lt; version history &gt;&gt;

&lt;&lt; imports &gt;&gt;

@others</t>
<t tx="ekr.20050306071629.1">'''This docstring should be a clear, concise description of
what the plugin does and how to use it.
'''
</t>
<t tx="ekr.20050306071629.2">@

Put notes about each version here.</t>
<t tx="ekr.20050306071629.3">import leo.core.leoGlobals as g

# Whatever other imports your plugins uses.
</t>
<t tx="ekr.20050306071629.4">def init ():
    
    ok = True # This might depend on imports, etc.
    
    if ok:
        g.registerHandler('start2',onStart2)
        g.plugin_signon(__name__)
        
    return ok</t>
<t tx="ekr.20050306081349"></t>
<t tx="ekr.20050328101812"> 
        
        
        </t>
<t tx="ekr.20050328101812.1"></t>
<t tx="ekr.20050328101812.2"></t>
<t tx="ekr.20050328101812.3"></t>
<t tx="ekr.20050329082101"></t>
<t tx="ekr.20050329082101.1">@nocolor</t>
<t tx="ekr.20050329082101.10">this is two !!!</t>
<t tx="ekr.20050329082101.100">This module provides access to some objects used or maintained by the
interpreter and to functions that interact strongly with the interpreter.

Dynamic objects:

argv -- command line arguments; argv[0] is the script pathname if known
path -- module search path; path[0] is the script directory, else ''
modules -- dictionary of loaded modules

displayhook -- called to show results in an interactive session
excepthook -- called to handle any uncaught exception other than SystemExit
  To customize printing in an interactive session or to install a custom
  top-level exception handler, assign other functions to replace these.

exitfunc -- if sys.exitfunc exists, this routine is called when Python exits
  Assigning to sys.exitfunc is deprecated; use the atexit module instead.

stdin -- standard input file object; used by raw_input() and input()
stdout -- standard output file object; used by the print statement
stderr -- standard error object; used for error messages
  By assigning other file objects (or objects that behave like files)
  to these, it is possible to redirect all of the interpreter's I/O.

last_type -- type of last uncaught exception
last_value -- value of last uncaught exception
last_traceback -- traceback of last uncaught exception
  These three are only available in an interactive session after a
  traceback has been printed.

exc_type -- type of exception currently being handled
exc_value -- value of exception currently being handled
exc_traceback -- traceback of exception currently being handled
  The function exc_info() should be used instead of these three,
  because it is thread-safe.

Static objects:

maxint -- the largest supported integer (the smallest is -maxint-1)
maxunicode -- the largest supported character
builtin_module_names -- tuple of module names built into this interpreter
version -- the version of this interpreter as a string
version_info -- version information as a tuple
hexversion -- version information encoded as a single integer
copyright -- copyright notice pertaining to this interpreter
platform -- platform identifier
executable -- pathname of this Python interpreter
prefix -- prefix used to find the Python library
exec_prefix -- prefix used to find the machine-specific Python library
dllhandle -- [Windows only] integer handle of the Python DLL
winver -- [Windows only] version number of the Python DLL
__stdin__ -- the original stdin; don't touch!
__stdout__ -- the original stdout; don't touch!
__stderr__ -- the original stderr; don't touch!
__displayhook__ -- the original displayhook; don't touch!
__excepthook__ -- the original excepthook; don't touch!

Functions:

displayhook() -- print an object to the screen, and save it in __builtin__._
excepthook() -- print an exception and its traceback to sys.stderr
exc_info() -- return thread-safe information about the current exception
exc_clear() -- clear the exception state for the current thread
exit() -- exit the interpreter by raising SystemExit
getdlopenflags() -- returns flags to be used for dlopen() calls
getrefcount() -- return the reference count for an object (plus one :-)
getrecursionlimit() -- return the max recursion depth for the interpreter
setcheckinterval() -- control how often the interpreter checks for events
setdlopenflags() -- set the flags to be used for dlopen() calls
setprofile() -- set the global profiling function
setrecursionlimit() -- set the max recursion depth for the interpreter
settrace() -- set the global debug tracing function
</t>
<t tx="ekr.20050329082101.101">
This package contains Docutils Writer modules.
</t>
<t tx="ekr.20050329082101.102"></t>
<t tx="ekr.20050329082101.103">Reads messages from a news server. Only does the last 10 as this is very slow ... it is only meant as an example. 

@auto-news &lt;news server name&gt;/&lt;news group name&gt;

</t>
<t tx="ekr.20050329082101.104">

Given some Python source, is there any tool which can tell the mimimum 
level of Python required to run that source? If I distribute some code, 
I need to be able to say which level of Python users require to run it.

-- 
Steve Toledo-Brown
Speaking for myself only.
Humans please use domain uk.ibm.com</t>
<t tx="ekr.20050329082101.105">

Disclaimer #1: I am a Python newbie, and I appreciate the vast
documentation at python.org -- some of which I expect has the answer to
my question if I can find it.

I am working on a custom computational fluid dynamics code.  I will
create one or more compiled Python modules in C/C++ to provide new
types and functions for manipulating those types.  I have a *lot* of
data.  Efficiency requires that the new data structures be shared
freely within the scope of the module, without directly exposing the
data to the standard Python runtime environment.

Stated another way, I need the data to persist in virtual memory across
seprate invocations of functions in the module(s) and to be accessible
only through methods explicitly provided by the module(s).

How can I do this?  What are some good examples to study?

Disclaimer #2: I am a aware that strong opinions exist about closing
off data from users.  But it's a requirement for this application.  I
don't like it, but I need the job!

Thanks for your time
CatManDo
</t>
<t tx="ekr.20050329082101.106">

Anand S Bisen wrote:
&gt; Hello
&gt; 
&gt; I have been developing a code that works pretty well on my python 2.3 
&gt; and now when i am running it on my server where it is programmed to run 
&gt; it's giving me errors. I have been using __contains__ method and it 
&gt; fails on python 2.2
&gt; 
&gt; For example
&gt; 
&gt; (Python 2.3)
&gt;  &gt;&gt; x="Hello World"
&gt;  &gt;&gt; print x.__contains__("Hello")
&gt; True
&gt; 
&gt; (Python 2.2)
&gt; 
&gt;  &gt;&gt;&gt; x="Hello world"
&gt;  &gt;&gt;&gt; print x.__contains__("Hello")
&gt; 
&gt; Traceback (most recent call last):
&gt;  File "&lt;stdin&gt;", line 1, in ?
&gt; TypeError: 'in &lt;string&gt;' requires character as left operand
&gt; 
&gt; 
&gt; Is there any woraround for this or what am i doing wrong in 2.2 ?
&gt; 
&gt; Thanks
&gt; 
Any use of double-underscores is an indication that magic is at work. In 
this case the __contains__ method is intended to be called by the 
interpreter when you write

     x in s

The __contains__ method was extended for strings in 2.3 so that 
construct could be used as a test to see whether s contained x as a 
substring. Before that, as the error message explains, it will only test 
to see whether a single character is contained in the string (by analogy 
with

     1 in [3, 4, 5, 2]

in case you are interested).

So you'll need to use the .find() string method and say

     if x.find("Hello") != -1:
         ... you found "Hello"

because your ISP appears to be using an older version of Python than you.

regards
  Steve
-- 
Meet the Python developers and your c.l.py favorites March 23-25
Come to PyCon DC 2005                      http://www.pycon.org/
Steve Holden                           http://www.holdenweb.com/</t>
<t tx="ekr.20050329082101.107">


"Zhang Le" &lt;sigu4wa02@sneakemail.com&gt; wrote in message 
news:1109952846.225378.136210@o13g2000cwo.googlegroups.com...
&gt; Hi,
&gt;  I did a small benchmark of matrix-vector multiply operation using
&gt; Numeric module. I'm a bit suprised to find matrix*col-vector is much
&gt; faster than row-vector*matrix. I wonder whether other people have
&gt; observed this fact too,

Yes, common knowledge in numerical analysis community.  Using the faster 
direction for a particular system as much as possible is part of tuning 
linear algebra software.

&gt; and why?

I presume that Numeric, like Python, stores matrices by row.  So M*v 
multiplies contiguous rows by a contiguous vector.  Multiplying a vector by 
non-contiguous columns requires requires skipping thru the matrix, which 
may require more computation and generate more cache misses and page 
faults.

Terry  J. Reedy


</t>
<t tx="ekr.20050329082101.108">

I just ೾蓗肇　 in the 'What's New in Python 2.4' document that the None
data type was converted to a constant:
http://python.org/doc/2.4/whatsnew/node15.html

"""
# None is now a constant; code that binds a new value to the name
"None" is now a syntax error.
"""

So, what's the implications of this?  I find the lack of explanation a
little puzzling, since I've written code that compares a variable's
type with the 'None' type.  For example, a variable would be
initialized to 'None' and if it went through a loop unchanged, I could
determine this at the end by using a conditional type(var) ==
type(None).  What will type(None) return now?
</t>
<t tx="ekr.20050329082101.109">

On Fri, 4 Mar 2005 22:35:48 +0100, andrea_gavana@tin.it
&lt;andrea_gavana@tin.it&gt; wrote:
&gt; Hello NG,
&gt; 
&gt;     I was wondering if there is a way to obtain, from a list of floats,
&gt; a list of integers without loops. Probably is a basic question, but I can't
&gt; find an answer... I have had my eyes blinded by Matlab for years, but now
&gt; that I discovered Python+wxPython there seems to be no limit on what one
&gt; can do with these 2 tools. Anyway, following the Matlab style, I would like
&gt; to do something like this:
&gt; 
&gt; matrix = [1.5, 4.3, 5.5]
&gt; integer_matrix = int(matrix)       (float for Matlab)

You're going to have to use loops. I don't know how Matlab can do it
without them, unless it maintains the matrix as a list of floats and
simply *views* it as a list of ints. More likely, it simply hides the
loop away from you. Anyway, here's some ways to do it:

preferable: int_matrix = [int(x) for x in matrix]
old way: int_matrix = map(int, matrix)
explicit:
int_matrix = []
for x in matrix:
    int_matrix.append(int(x))

Any of these methods should be neither really slow nor really fast,
but the list comprehension should be the fastest (I think). Anyway, if
you're going to be doing lots of large matrices, and want some of your
old matlab stuff, check out numpy and numarray at
http://numeric.scipy.org/ .

Also, somebody was recently posting on here about a python &lt;-&gt; matlab
bridge that they developed; you should search the archives for that
(it was in february, I think).

And, finally, when doing scientific stuff, I found IPython
(http://ipython.scipy.org/) to be an invaluable tool. It's a much
improved Python interpreter.

Peace
Bill Mill
bill.mill at gmail.com

&gt; 
&gt; (In Matlab, "integer_matrix" is always a double anyway, here I would like
&gt; only to show the vector-matrix operation).
&gt; 
&gt; Obviously, Python complains about:
&gt; 
&gt; Traceback (most recent call last):
&gt;   File "&lt;interactive input&gt;", line 1, in ?
&gt; TypeError: int() argument must be a string or a number
&gt; 
&gt; I would like to avoid loops because, having been blinded by Matlab vector-matrix
&gt; abilities (and corresponding SLOW for-while loops operations), I tend to
&gt; think that also Python will be slow if I use loops.
&gt; 
&gt; Does anyone have a suggestion (or maybe could anyone show me that I'm wrong
&gt; about loops?)
&gt; 
&gt; Thanks you a lot.
&gt; 
&gt; Andrea.
&gt; 
&gt; --
&gt; http://mail.python.org/mailman/listinfo/python-list
&gt;</t>
<t tx="ekr.20050329082101.11">this is three</t>
<t tx="ekr.20050329082101.110">news-server.houston.rr.com/comp.lang.python</t>
<t tx="ekr.20050329082101.111">

This was happening to me for a while but stopped. I think it has to do with 
your mail server. Perhaps you could find another. If you are at a company, 
you might want to talk to your sysadmin and see if he can change the mail 
program. How did you get this latest message through? You know, with the 
proper email client you can have identities and such that have "from" and 
"return addresses" that are completely unrelated to the mail server you are 
using, if you would rather the mail list did not know about your most favored 
address.

James

On Friday 04 March 2005 01:56 pm, phil wrote:
&gt; everything I post to this list bounces awaiting moderator
&gt; approval, due to suspicious header.
&gt; COuld someone tell me what's wrong.  I'm on lots of list
&gt; with no problem.

-- 
James Stroud, Ph.D.
UCLA-DOE Institute for Genomics and Proteomics
Box 951570
Los Angeles, CA 90095</t>
<t tx="ekr.20050329082101.112">news-server.houston.rr.com/comp.lang.python</t>
<t tx="ekr.20050329082101.113">news-server.houston.rr.com/comp.lang.python</t>
<t tx="ekr.20050329082101.114"></t>
<t tx="ekr.20050329082101.12"></t>
<t tx="ekr.20050329082101.13"></t>
<t tx="ekr.20050329082101.14"></t>
<t tx="ekr.20050329082101.146"></t>
<t tx="ekr.20050329082101.15">Reads a remote news service.

@auto-rss &lt;url to news service&gt;

Requires feedparser installed:
    http://sourceforge.net/projects/feedparser/</t>
<t tx="ekr.20050329082101.16">title

summary_detail</t>
<t tx="ekr.20050329082101.2">The AutoTrees plugin is a helper plugin designed to make it very easy to write "hanlder" plugins to manage dynamic content in Leo outlines. 

AutoTrees provides 

- convenient handler base classes which can be specialized for particular uses
- a manager to turn handlers on and off
- a set of example handlers to show the kinds of things that are possible

AutoTrees doesn't do anything that you cannot do in other ways, but it does provide a consistent way of adding dynamic content. This means that individual plugin writers don't have to rewrite all the same kinds of code each time and also makes it easier to maintain Leo, since it standardizes the way that certain classes of plugin interact with the Leo core.

</t>
<t tx="ekr.20050329082101.3">I'm a plugin writer and I want to write a plugin to display dynamic content - ie content not directly contained in the .leo or derived files, eg

- email messages 
- news feeds
- news groups
- documentation
- remote files
- statistics
- file system data
- data base records

You can do this as a standard plugin, but as an AutoTrees handler you,

- don't need to write code that interacts with the tree (this is done for you)
- get centralized management
- can still do everything else you could as a normal plugin

</t>
<t tx="ekr.20050329082101.4">AutoTrees is itself a plugin. When it starts it,

1. Scans the leo\plugins\trees folder to find handlers
2. Activates specific handlers (this is managed via a plugin manager type window)
3. Waits for clicks and double-clicks on special nodes

To create an AutoTree node, you add a node with @auto-my_handler. The @auto tells the plugin to go and look for the "my_handler" handler, if it is enabled. The handler is then called and this is then used to populate the node body and child nodes below this node.

eg, for an @auto-rss node, the node headline is "@auto-rss http://myurl/news.xml". The handler goes to the URL mentioned and downloads the news stories. It then creates child nodes for each story and populates the bodies. 

The handler doesn't have to worry about interacting with the Leo tree view, it just returns a tree object. 

</t>
<t tx="ekr.20050329082101.40" annotate="7d71002e">title (slash_section, category)

summary_detail

link</t>
<t tx="ekr.20050329082101.5">The best way is to use the existing examples as templates. Look at the "test" handler first as this is the "Hello world" of trees.

</t>
<t tx="ekr.20050329082101.51">title (modified)

link</t>
<t tx="ekr.20050329082101.52">Python 2.4.1 (release candhttp://www.python.org/2.4.1/index.htmlate 1) (2005-03-10)

http://www.python.org/2.4.1/index.html</t>
<t tx="ekr.20050329082101.53">Greg Stein, of Google and Apache Software Foundation, to deliver keynote at PyCon (2005-03-06)

http://www.python.org/pycon/2005/keynotes.html</t>
<t tx="ekr.20050329082101.54">New RSS feed for python-dev summaries (2005-02-24)

http://www.python.org/dev/summary/channews.rdf</t>
<t tx="ekr.20050329082101.55">Guhttp://www.sdforum.org/SDForum/Templates/CalendarEvent.aspx?CID=1547&amp;mo=2&amp;yr=2005o van Rossum speaking in Palo Alto (2005-02-17)

http://www.sdforum.org/SDForum/Templates/CalendarEvent.aspx?CID=1547&amp;mo=2&amp;yr=2005</t>
<t tx="ekr.20050329082101.56">Python 2.3.5 (final) (2005-02-08)

http://www.python.org/2.3.5/index.html</t>
<t tx="ekr.20050329082101.57">Security advisory for SimpleXMLRPCServer.py. (2005-02-03)

http://python.org/security/PSF-2005-001/</t>
<t tx="ekr.20050329082101.58">Deadline for OSCON proposals (2005-02-01)

http://mail.python.org/pipermail/python-announce-list/2005-January/003683.html</t>
<t tx="ekr.20050329082101.59">PyCon abstracts now available (2005-01-23)

http://www.python.org/moin/PyConDC2005/Presentations</t>
<t tx="ekr.20050329082101.6" annotate="7d71002e">@nocolor</t>
<t tx="ekr.20050329082101.60">PyCon preliminary schedule now available (2005-01-20)

http://www.python.org/pycon/2005/schedule.html</t>
<t tx="ekr.20050329082101.61">PSF has awarded three grants (2004-12-30)

http://www.python.org/psf/grants/index.html</t>
<t tx="ekr.20050329082101.62">Python for Nokia Series 60 now available (2004-12-23)

http://www.forum.nokia.com/main/0,,034-821,00.html</t>
<t tx="ekr.20050329082101.63">Python 2.4 (final) (2004-11-30)

http://www.python.org/2.4/index.html</t>
<t tx="ekr.20050329082101.64">PyZine issue 7 (2004-11-23)

http://www.pyzine.com/Issue007/</t>
<t tx="ekr.20050329082101.65">PyCon 2005 Call for Proposals (2004-10-23)

http://www.python.org/pycon/2005/cfp.html</t>
<t tx="ekr.20050329082101.66">Cameron Laird receives the Frank Willison Award (2004-10-18)

http://press.oreilly.com/pub/pr/1237</t>
<t tx="ekr.20050329082101.67">Reads a remote file

@auto-remote &lt;url to file&gt;

Requires pyCurl:
    http://pycurl.sourceforge.net/</t>
<t tx="ekr.20050329082101.68">&lt;!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"&gt;
&lt;html&gt;
&lt;head&gt;
&lt;title&gt;BBC - Error 404: Page not found&lt;/title&gt;
&lt;meta name="description" content="Error 404 - page not found" /&gt;
&lt;meta name="keywords" content="" /&gt;
&lt;meta name="created" content="20040506" /&gt;
&lt;meta name="updated" content="20040506" /&gt;
&lt;base href="http://www.bbc.co.uk" /&gt;
&lt;style&gt;
body {margin:0; padding:0;}
em {color:#900;}
p, ul {font-size:80%}
h4,h3,h2,h1,p, ul {font-family: verdana,arial,helvetica,sans-serif;}
h4,h3 {font-size:100%}
h4,h1 {margin:0}
div.main {padding:8px;margin:0px;width:770;}
form {margin:0;padding:0;}
&lt;/style&gt;
&lt;/head&gt;
&lt;body bgcolor="#ffffff" link="#333366" text="#000000" vlink="#333366" alink="#000000" marginheight="0" marginwidth="0"&gt;

&lt;!-- toolbar 1.4 toolbar.page 770 666666 --&gt;&lt;table width="100%" cellpadding="0" cellspacing="0" border="0"&gt;&lt;tr&gt;&lt;td colspan="2" style="background-color:#828282;" &gt;&lt;a name="top"&gt;&lt;img src="/f/t.gif" width="590" height="2" alt="" /&gt;&lt;/a&gt;&lt;/td&gt;&lt;td style="background-color:#828282;"&gt;&lt;img src="/f/t.gif" width="1" height="2" alt="" /&gt;&lt;/td&gt;&lt;/tr&gt;&lt;form action="http://www.bbc.co.uk/cgi-bin/search/results.pl"&gt;&lt;tr&gt;&lt;td style="border-left:2px solid #828282;background-color:#999999;" width="54"&gt;&lt;a href="http://www.bbc.co.uk/go/toolbar/-/"&gt;&lt;img src="/images/logo04.gif" width="50" height="20" alt="BBC" border="0" hspace="2" vspace="5" /&gt;&lt;/a&gt;&lt;/td&gt;&lt;td style="background:#999999;" align="right"&gt;&lt;table cellpadding="0" cellspacing="0" border="0" style="float:right;"&gt;&lt;tr&gt;&lt;td style="background:#999999;"&gt;&lt;font size="1"&gt;&lt;b&gt;&lt;a href="http://www.bbc.co.uk/go/toolbar/text/-/" style="color:#ffffff;text-decoration:none;font-family:verdana,arial,helvetica,sans-serif;padding:1px 4px;"&gt;Home&lt;/a&gt;&lt;/b&gt;&lt;/font&gt;&lt;/td&gt;&lt;td style="background:#999999 url(/images/v.gif) repeat-y;" width="6"&gt;&lt;br /&gt;&lt;/td&gt;&lt;td&gt;&lt;font size="1"&gt;&lt;b&gt;&lt;a href="/go/toolbar/-/tv/" style="color:#ffffff;text-decoration:none;font-family:verdana,arial,helvetica,sans-serif;padding:1px 4px;"&gt;TV&lt;/a&gt;&lt;/b&gt;&lt;/font&gt;&lt;/td&gt;&lt;td style="background:#999999 url(/images/v.gif) repeat-y;" width="6"&gt;&lt;br /&gt;&lt;/td&gt;&lt;td&gt;&lt;font size="1"&gt;&lt;b&gt;&lt;a href="/go/toolbar/-/radio/" style="color:#ffffff;text-decoration:none;font-family:verdana,arial,helvetica,sans-serif;padding:1px 4px;"&gt;Radio&lt;/a&gt;&lt;/b&gt;&lt;/font&gt;&lt;/td&gt;&lt;td style="background:#999999 url(/images/v.gif) repeat-y;" width="6"&gt;&lt;br /&gt;&lt;/td&gt;&lt;td&gt;&lt;font size="1"&gt;&lt;b&gt;&lt;a href="/go/toolbar/-/talk/" style="color:#ffffff;text-decoration:none;font-family:verdana,arial,helvetica,sans-serif;padding:1px 4px;"&gt;Talk&lt;/a&gt;&lt;/b&gt;&lt;/font&gt;&lt;/td&gt;&lt;td style="background:#999999 url(/images/v.gif) repeat-y;" width="6"&gt;&lt;br /&gt;&lt;/td&gt;&lt;td&gt;&lt;font size="1"&gt;&lt;b&gt;&lt;a href="/go/toolbar/-/whereilive/" style="color:#ffffff;text-decoration:none;font-family:verdana,arial,helvetica,sans-serif;padding:1px 4px;"&gt;Where&amp;nbsp;I&amp;nbsp;Live&lt;/a&gt;&lt;/b&gt;&lt;/font&gt;&lt;/td&gt;&lt;td style="background:#999999 url(/images/v.gif) repeat-y;" width="6"&gt;&lt;br /&gt;&lt;/td&gt;&lt;td&gt;&lt;nobr&gt;&lt;font size="1"&gt;&lt;b&gt;&lt;a href="/go/toolbar/-/a-z/" style="color:#ffffff;text-decoration:none;font-family:verdana,arial,helvetica,sans-serif;padding:1px 4px;"&gt;A-Z&amp;nbsp;Index&lt;/a&gt;&lt;/b&gt;&lt;/font&gt;&lt;/nobr&gt;&lt;/td&gt;&lt;td style="background:#666666 url(/images/sl3.gif) no-repeat;" width="8"&gt;&lt;br /&gt;&lt;/td&gt;&lt;td style="background:#666666 url(/images/st.gif) repeat-x 0 0;"&gt;&lt;input type="text" id="bbcpageSearchbox" name="q" size="6" style="margin:3px 0 0;font-family:arial,helvetica,sans-serif;width:100px;" title="BBC Search" /&gt;&lt;/td&gt;&lt;td style="background:#666666 url(/images/st.gif) repeat-x;"&gt;&lt;input type="image" src="/images/srchb.gif" name="go" value="go" alt="Search" width="64" height="25" border="0" /&gt;&lt;/td&gt;&lt;td style="background:#999999 url(/images/sra.gif) no-repeat;" width="1"&gt;&lt;img src="/f/t.gif" width="1" height="30" alt="" /&gt;&lt;/td&gt;&lt;/tr&gt;&lt;/table&gt;&lt;/td&gt;&lt;td style="background:#999999 url(/images/srb.gif) no-repeat;"&gt;&lt;img src="/f/t.gif" width="1" height="1" alt="" /&gt;&lt;input type="hidden" name="uri" value="/news.html" /&gt;&lt;/td&gt;&lt;/tr&gt;&lt;/form&gt;&lt;tr&gt;&lt;td colspan="2" style="background-color:#000000;"&gt;&lt;img src="/f/t.gif" width="770" height="1" alt="" /&gt;&lt;/td&gt;&lt;td width="100%" style="background-color:#000000;"&gt;&lt;img src="/f/t.gif" width="1" height="1" alt="" /&gt;&lt;/td&gt;&lt;/tr&gt;&lt;/table&gt;&lt;!-- end toolbar 1.4 --&gt;

&lt;table cellspacing="0" cellpadding="8" border="0" width="770" bgcolor="#cccccc"&gt;&lt;tr&gt;&lt;td width="335"&gt;&lt;font size="-2" face="arial,helvetica"&gt;TUESDAY&lt;br /&gt;29th March 2005&lt;br /&gt;&lt;a href="/cgi-bin/education/betsie/parser.pl"&gt;Text only&lt;/a&gt; &lt;/font&gt;&lt;/td&gt;&lt;td width="435"&gt;&lt;h1&gt;404&lt;/h1&gt;&lt;/td&gt;&lt;/tr&gt;&lt;/table&gt;
&lt;div class="main"&gt;
&lt;div align="center"&gt;
&lt;h2&gt;Page not found&lt;/h2&gt;
&lt;p&gt;Unfortunately the following page was not available:&lt;br /&gt;
&lt;em&gt;http://www.bbc.co.uk/news.html&lt;/em&gt;&lt;/p&gt;
&lt;/div&gt;
&lt;h3&gt;This might be because:&lt;/h3&gt;
&lt;ul&gt;&lt;li&gt;You may have typed the web address incorrectly. Please check the address and spelling ensuring that it does &lt;b&gt;not&lt;/b&gt; contain capital letters or spaces&lt;/li&gt;
&lt;li&gt;It is possible that the page you were looking for may have been moved, updated or deleted.&lt;/li&gt;&lt;/ul&gt;

&lt;h3&gt;Please try the following options instead:&lt;/h3&gt;

&lt;form action="/cgi-bin/search/results.pl"&gt;
&lt;table cellpadding="4" cellspacing="2" border="0" align="center" bgcolor="#000000"&gt;
&lt;tr&gt;&lt;td bgcolor="#99ccff"&gt;&lt;h4&gt;Search bbc.co.uk&lt;/h4&gt;&lt;/td&gt;&lt;/tr&gt;
&lt;tr&gt;&lt;td bgcolor="#ffffcc"&gt;&lt;input type="text" name="q" size="45" /&gt;&amp;nbsp;&lt;input type="submit" value="Go" /&gt;&lt;/td&gt;&lt;/tr&gt;
&lt;/table&gt;
&lt;/form&gt;

&lt;ul&gt;
&lt;li&gt;Return to the &lt;a href="/"&gt;bbc.co.uk Home Page&lt;/a&gt;&lt;/li&gt;
&lt;li&gt;Use our &lt;a href="/a-z/"&gt;site index&lt;/a&gt;&lt;/li&gt;
&lt;li&gt;If you still encounter problems then please try the &lt;a href="/help/"&gt;help&lt;/a&gt; section.&lt;/li&gt;
&lt;/ul&gt;

&lt;/div&gt;
&lt;!-- inc.footer.page --&gt;&lt;br clear="all" /&gt;&lt;table width="770" cellpadding="0" cellspacing="0" border="0"&gt;&lt;tr&gt;&lt;td width="110"&gt;&lt;img src="/furniture/tiny.gif" alt="" width="110" height="1"&gt;&lt;/td&gt;&lt;td width="10"&gt;&lt;img src="/furniture/tiny.gif" alt="" width="10" height="1"&gt;&lt;/td&gt;&lt;td align="center" width="100%"&gt;&lt;font face="arial, helvetica, sans-serif" size="1"&gt;&lt;a href="/terms/"&gt;Terms of Use&lt;/a&gt; | &lt;a href="/privacy/"&gt;Privacy&lt;/a&gt;&lt;/font&gt;&lt;/td&gt;&lt;/tr&gt;&lt;/table&gt;&lt;!-- end inc.footer.page --&gt;

&lt;/body&gt;
&lt;/html&gt;
</t>
<t tx="ekr.20050329082101.69">Produces documentation for a module

@auto-doc &lt;module name&gt;</t>
<t tx="ekr.20050329082101.7">Just some simple testing nodes</t>
<t tx="ekr.20050329082101.70"></t>
<t tx="ekr.20050329082101.71">Base class for Docutils components.</t>
<t tx="ekr.20050329082101.72"></t>
<t tx="ekr.20050329082101.73">tuple() -&gt; an empty tuple
tuple(sequence) -&gt; tuple initialized from sequence's items

If the argument is a tuple, the return value is the same object.</t>
<t tx="ekr.20050329082101.74">
        Is `format` supported by this component?

        To be used by transforms to ask the dependent component if it supports
        a certain input context or output format.
        </t>
<t tx="ekr.20050329082101.75"></t>
<t tx="ekr.20050329082101.76">No documentation for OPTCRE</t>
<t tx="ekr.20050329082101.77">No documentation for SECTCRE</t>
<t tx="ekr.20050329082101.78">Create a new section in the configuration.

        Raise DuplicateSectionError if a section by the specified name
        already exists.
        </t>
<t tx="ekr.20050329082101.79">tuple() -&gt; an empty tuple
tuple(sequence) -&gt; tuple initialized from sequence's items

If the argument is a tuple, the return value is the same object.</t>
<t tx="ekr.20050329082101.8" annotate="7d71002e"></t>
<t tx="ekr.20050329082101.80">dict() -&gt; new empty dictionary.
dict(mapping) -&gt; new dictionary initialized from a mapping object's
    (key, value) pairs.
dict(seq) -&gt; new dictionary initialized as if via:
    d = {}
    for k, v in seq:
        d[k] = v
dict(**kwargs) -&gt; new dictionary initialized with the name=value pairs
    in the keyword argument list.  For example:  dict(one=1, two=2)</t>
<t tx="ekr.20050329082101.81">
    Parser for command-line and library use.  The `settings_spec`
    specification here and in other Docutils components are merged to build
    the set of command-line options and runtime settings for this process.

    Common settings (defined below) and component-specific settings must not
    conflict.  Short options are reserved for common settings, and components
    are restrict to using long options.
    </t>
<t tx="ekr.20050329082101.82">str(object) -&gt; string

Return a nice string representation of the object.
If the argument is a string, the return value is the same object.</t>
<t tx="ekr.20050329082101.83">tuple() -&gt; an empty tuple
tuple(sequence) -&gt; tuple initialized from sequence's items

If the argument is a tuple, the return value is the same object.</t>
<t tx="ekr.20050329082101.84">dict() -&gt; new empty dictionary.
dict(mapping) -&gt; new dictionary initialized from a mapping object's
    (key, value) pairs.
dict(seq) -&gt; new dictionary initialized as if via:
    d = {}
    for k, v in seq:
        d[k] = v
dict(**kwargs) -&gt; new dictionary initialized with the name=value pairs
    in the keyword argument list.  For example:  dict(one=1, two=2)</t>
<t tx="ekr.20050329082101.85">tuple() -&gt; an empty tuple
tuple(sequence) -&gt; tuple initialized from sequence's items

If the argument is a tuple, the return value is the same object.</t>
<t tx="ekr.20050329082101.86">list() -&gt; new list
list(sequence) -&gt; new list initialized from sequence's items</t>
<t tx="ekr.20050329082101.87">list() -&gt; new list
list(sequence) -&gt; new list initialized from sequence's items</t>
<t tx="ekr.20050329082101.88">dict() -&gt; new empty dictionary.
dict(mapping) -&gt; new dictionary initialized from a mapping object's
    (key, value) pairs.
dict(seq) -&gt; new dictionary initialized as if via:
    d = {}
    for k, v in seq:
        d[k] = v
dict(**kwargs) -&gt; new dictionary initialized with the name=value pairs
    in the keyword argument list.  For example:  dict(one=1, two=2)</t>
<t tx="ekr.20050329082101.89">str(object) -&gt; string

Return a nice string representation of the object.
If the argument is a string, the return value is the same object.</t>
<t tx="ekr.20050329082101.9">this is one</t>
<t tx="ekr.20050329082101.90">
    A facade encapsulating the high-level logic of a Docutils system.
    </t>
<t tx="ekr.20050329082101.91">str(object) -&gt; string

Return a nice string representation of the object.
If the argument is a string, the return value is the same object.</t>
<t tx="ekr.20050329082101.92">str(object) -&gt; string

Return a nice string representation of the object.
If the argument is a string, the return value is the same object.</t>
<t tx="ekr.20050329082101.93">
Command-line and common processing for Docutils front-end tools.

Exports the following classes:

- `OptionParser`: Standard Docutils command-line processing.
- `Values`: Runtime settings; objects are simple structs
  (``object.attribute``).
- `ConfigParser`: Standard Docutils config file processing.
</t>
<t tx="ekr.20050329082101.94">
I/O classes provide a uniform API for low-level input and output.  Subclasses
will exist for a variety of input/output mechanisms.
</t>
<t tx="ekr.20050329082101.95">
This package contains Docutils parser modules.
</t>
<t tx="ekr.20050329082101.96">
    Set up &amp; run a `Publisher`.  For command-line front ends.

    Parameters:

    - `reader`: A `docutils.readers.Reader` object.
    - `reader_name`: Name or alias of the Reader class to be instantiated if
      no `reader` supplied.
    - `parser`: A `docutils.parsers.Parser` object.
    - `parser_name`: Name or alias of the Parser class to be instantiated if
      no `parser` supplied.
    - `writer`: A `docutils.writers.Writer` object.
    - `writer_name`: Name or alias of the Writer class to be instantiated if
      no `writer` supplied.
    - `settings`: Runtime settings object.
    - `settings_spec`: Extra settings specification; a `docutils.SettingsSpec`
      subclass.  Used only if no `settings` specified.
    - `settings_overrides`: A dictionary containing program-specific overrides
      of component settings.
    - `enable_exit`: Boolean; enable exit status at end of processing?
    - `argv`: Command-line argument list to use instead of ``sys.argv[1:]``.
    - `usage`: Usage string, output if there's a problem parsing the command
      line.
    - `description`: Program description, output for the "--help" option
      (along with command-line option descriptions).
    </t>
<t tx="ekr.20050329082101.97">
    Set up &amp; run a `Publisher`.  For programmatic use with file-like I/O.

    Parameters:

    - `source`: A file-like object (must have "read" and "close" methods).
    - `source_path`: Path to the input file.  Opened if no `source` supplied.
      If neither `source` nor `source_path` are supplied, `sys.stdin` is used.
    - `destination`: A file-like object (must have "write" and "close"
      methods).
    - `destination_path`: Path to the input file.  Opened if no `destination`
      supplied.  If neither `destination` nor `destination_path` are supplied,
      `sys.stdout` is used.
    - `reader`: A `docutils.readers.Reader` object.
    - `reader_name`: Name or alias of the Reader class to be instantiated if
      no `reader` supplied.
    - `parser`: A `docutils.parsers.Parser` object.
    - `parser_name`: Name or alias of the Parser class to be instantiated if
      no `parser` supplied.
    - `writer`: A `docutils.writers.Writer` object.
    - `writer_name`: Name or alias of the Writer class to be instantiated if
      no `writer` supplied.
    - `settings`: Runtime settings object.
    - `settings_spec`: Extra settings specification; a `docutils.SettingsSpec`
      subclass.  Used only if no `settings` specified.
    - `settings_overrides`: A dictionary containing program-specific overrides
      of component settings.
    - `enable_exit`: Boolean; enable exit status at end of processing?
    </t>
<t tx="ekr.20050329082101.98">
    Set up &amp; run a `Publisher`, and return the string output.
    For programmatic use with string I/O.

    For encoded string output, be sure to set the "output_encoding" setting to
    the desired encoding.  Set it to "unicode" for unencoded Unicode string
    output.  Here's how::

        publish_string(..., settings_overrides={'output_encoding': 'unicode'})

    Similarly for Unicode string input (`source`)::

        publish_string(..., settings_overrides={'input_encoding': 'unicode'})

    Parameters:

    - `source`: An input string; required.  This can be an encoded 8-bit
      string (set the "input_encoding" setting to the correct encoding) or a
      Unicode string (set the "input_encoding" setting to "unicode").
    - `source_path`: Path to the file or object that produced `source`;
      optional.  Only used for diagnostic output.
    - `destination_path`: Path to the file or object which will receive the
      output; optional.  Used for determining relative paths (stylesheets,
      source links, etc.).
    - `reader`: A `docutils.readers.Reader` object.
    - `reader_name`: Name or alias of the Reader class to be instantiated if
      no `reader` supplied.
    - `parser`: A `docutils.parsers.Parser` object.
    - `parser_name`: Name or alias of the Parser class to be instantiated if
      no `parser` supplied.
    - `writer`: A `docutils.writers.Writer` object.
    - `writer_name`: Name or alias of the Writer class to be instantiated if
      no `writer` supplied.
    - `settings`: Runtime settings object.
    - `settings_spec`: Extra settings specification; a `docutils.SettingsSpec`
      subclass.  Used only if no `settings` specified.
    - `settings_overrides`: A dictionary containing program-specific overrides
      of component settings.
    - `enable_exit`: Boolean; enable exit status at end of processing?
    </t>
<t tx="ekr.20050329082101.99">
This package contains Docutils Reader modules.
</t>
<t tx="ekr.20050329092553">Hundreds die in Indonesia quake

Hundreds are believed to have died in Indonesia after a strong earthquake which sparked fears of a tsunami.</t>
<t tx="ekr.20050329092553.1">Ousted Kyrgyz preshttp://news.bbc.co.uk/1/hi/world/asia-pacific/4391139.stment defiant

Ousted Kyrgyz leader Askar Akayev says he remains the "sole legitimate preshttp://news.bbc.co.uk/1/hi/world/asia-pacific/4391139.stment" of his country.</t>
<t tx="ekr.20050329092553.10">Cricket: Series win for Aussies

Australia beat New Zealand by nine wickets in the third Test to wrap up a 2-0 series win.</t>
<t tx="ekr.20050329092553.11">Angola says virus 'under control'

Angola says an outbreak of the deadly Marburg virus is under control as DR Congo takes precautions.</t>
<t tx="ekr.20050329092553.12">Mugabe criticises MDC 'traitors'

Preshttp://news.bbc.co.uk/1/hi/world/africa/4391087.stment Mugabe condemns opposition supporters as traitors, as parliamentary elections draw near.</t>
<t tx="ekr.20050329092553.13">Ex-US diplomats round on Bolton

Dozens of former US diplomats urge Congress to block the appointment of John Bolton as UN ambassador.</t>
<t tx="ekr.20050329092553.14">Brazil quits loan accord with IMF

Brazil announces it will not renew a $41.75bn loan accord with the International Monetary Fund.</t>
<t tx="ekr.20050329092553.15">Japanese economy hit by weak data

An unexpected rise in Japan's jobless rate and falls in household spending and retail sales hit Japanese stocks.</t>
<t tx="ekr.20050329092553.16">Donors pledge $40m for KR trials

A UN-supported Khmer Rouge tribunal, due to try Cambodia's rulers from the 1970s, could open soon.</t>
<t tx="ekr.20050329092553.17">Three Romanians missing in Iraq

Three Romanian journalists are missing, feared khttp://news.bbc.co.uk/1/hi/world/middle_east/4389391.stmnapped, in Iraq after one called on a mobile.</t>
<t tx="ekr.20050329092553.18">Wolfowitz 'to meet EU officials'

Paul Wolfowitz, the US's controversial nomination to head the World Bank, is expected to meet with EU officials on Wednesday, reports say.</t>
<t tx="ekr.20050329092553.19">Knesset rejects Gaza referendum

Israel's parliament rejects an attempt by opponents of the planned Gaza pullout to force a referendum.</t>
<t tx="ekr.20050329092553.2">Hair 'good source of stem cells'

Scientists have found hair follicles are a plentiful source of stem cells, which can become body tissue.</t>
<t tx="ekr.20050329092553.20">Militants to attend PLO meeting

Islamic Jihad is to sit in on a meeting of the top Palestinian decision-making body for the first time.</t>
<t tx="ekr.20050329092553.21">South Asia cancels tsunami alerts

India and Sri Lanka withdraw the tsunami alerts issued after an earthquake hit the coast of Indonesia.</t>
<t tx="ekr.20050329092553.22">Devastation as Afghan dam bursts

A dam has burst in south-eastern Afghanistan killing at least six people and causing whttp://news.bbc.co.uk/1/hi/world/south_asia/4391251.stmespread devastation, officials say.</t>
<t tx="ekr.20050329092553.23">Kyrgyzstan's friendly revolution

The BBC's Ian MacWilliam reports from Kyrgyzstan on an unusual people's revolution.</t>
<t tx="ekr.20050329092553.24">Followup on MS and Brazil in NY Times (mainpage, microsoft)

putko was one of dozens to submit a story running on the NY Times about Open Source and Brazil. The choice quote is "We're not going to spend taxpayers' money on a program so that Microsoft can further consolhttp://slashdot.org/article.pl?sid=05/03/29/1359253&amp;from=rssate its monopoly..."

http://slashdot.org/article.pl?shttp://slashdot.org/article.pl?sid=05/03/29/1359253&amp;from=rss=05/03/29/1359253&amp;from=rss</t>
<t tx="ekr.20050329092553.25">A9.com with Syndicated Search (mainpage, internet)

joeykiller writes "Search Engine Watch reports that Amazon now lets you add your own search to their A9 search engine. Users can opt-in to use additional search engines in addition to A9.com's own when searching. Amazon has chosen to use an extension of RSS 2.0 for this, and hopes that this format will enable search syndication in the same way RSS dhttp://slashdot.org/article.pl?sid=05/03/29/1337250&amp;from=rss for content. Several add-on searches are available already, among them New York Times, Wikipedia and NASA."

http://slashdot.org/article.pl?shttp://slashdot.org/article.pl?sid=05/03/29/1337250&amp;from=rss=05/03/29/1337250&amp;from=rss</t>
<t tx="ekr.20050329092553.26">What's Next At Apple (apple, apple)

pinqkandi writes "Business 2.0 is running a fascinating article on what might be coming up in Apple's future. Beshttp://apple.slashdot.org/article.pl?sid=05/03/29/132202&amp;from=rsses speculation, some interesting statistics are included, such as how the iPod should create equal revenue to the Mac for Apple in 2006, if not surpassing it. A good read for the Apple lover or loather."

http://apple.slashdot.org/article.pl?shttp://apple.slashdot.org/article.pl?sid=05/03/29/132202&amp;from=rss=05/03/29/132202&amp;from=rss</t>
<t tx="ekr.20050329092553.27">Berkeley Grads' Identity Data Stolen (yro, privacy)

yali writes "Dhttp://yro.slashdot.org/article.pl?sid=05/03/29/036237&amp;from=rss you get a graduate degree from Berkeley? Or maybe you just applied but dhttp://yro.slashdot.org/article.pl?sid=05/03/29/036237&amp;from=rssn't go there? If so, your http://yro.slashdot.org/article.pl?sid=05/03/29/036237&amp;from=rssentity may have been stolen. A laptop was stolen containing names, social security numbers, birthdates, and addresses of grad students, alumni, and applicants. University police suspect that the thief just wanted the laptop, but the irony of California's mandatory notification law is that the thief may now know they have something even more valuable. Berkeley has set up a website with information on the breach."

http://yro.slashdot.org/article.pl?shttp://yro.slashdot.org/article.pl?sid=05/03/29/036237&amp;from=rss=05/03/29/036237&amp;from=rss</t>
<t tx="ekr.20050329092553.28">South Korean Gov't. Advocates Linux (linux, linuxbiz)

Anonymous Coward writes "Korea has now taken the plunge on the Linux operating system, and is now starting to advocate Linux for use in government and public sector applications. South Korea's Ministry of Information and Communications announced the move today, which will result in decreased Microsoft market share in the region." According to the article, Korea's Ministry of Information and Communication "will provhttp://linux.slashdot.org/article.pl?sid=05/03/29/0322248&amp;from=rsse a total of 3 billion won (US$2.95 million) for government agencies which want to use the Linux and other open-source computer programs this year."

http://linux.slashdot.org/article.pl?shttp://linux.slashdot.org/article.pl?sid=05/03/29/0322248&amp;from=rss=05/03/29/0322248&amp;from=rss</t>
<t tx="ekr.20050329092553.29">MS, EU Agree on Name for Windows Sans Media Player (mainpage, windows)

An anonymous reader writes "Microsoft has agreed with European Union antitrust regulators on a new name for Windows software sold in Europe. Officials at the U.S. software giant sahttp://slashdot.org/article.pl?sid=05/03/28/1951251&amp;from=rss they had accepted the European Union's offer to call the European version of Windows sold without Media Player "Windows XP Home Edition N" - with "N" standing for "not with media player." Microsoft's "XP Professional Edition" will also include the "N" for versions sold without the media player. The prior nme for the OS was Windows XP Reduced Media Edition." News.com also mentions the choice.

http://slashdot.org/article.pl?shttp://slashdot.org/article.pl?sid=05/03/28/1951251&amp;from=rss=05/03/28/1951251&amp;from=rss</t>
<t tx="ekr.20050329092553.3">Ashdown sacks top Bosnian Croat

The top administrator in Bosnia, Lord Ashdown, sacks the Croat member of Bosnia's joint preshttp://news.bbc.co.uk/1/hi/world/europe/4390635.stmency.</t>
<t tx="ekr.20050329092553.30">Blackbox (Finally) Updated (mainpage, gui)

mpeg4codec writes "OSNews reported earlier this month that the lightweight Blackbox window manager has been updated to 0.70. Among the new features are EWMH compliance, anti-aliased fonts, unicode support, and backwards compatibility with previous versions' styles. Of course, it brings you all these new features (well, some are optional) while retaining its small binary size, small memory footprint, and short list of dependencies. I for one think it's about time."

http://slashdot.org/article.pl?shttp://slashdot.org/article.pl?sid=05/03/29/0253245&amp;from=rss=05/03/29/0253245&amp;from=rss</t>
<t tx="ekr.20050329092553.31">Your Face On the Big Screen (mainpage, ent)

blamanj writes "In another case of SciFi becoming reality, you can now star in an animated film as your FutureCast (tm) face-scan is edited into the picture in real-time. John Brunner, in his Hugo-winning novel, Stand on Zanzibar predicted a similar development in television, lampooning people sitting at home while watching travologues of themselves 'on vacation.' Brunner, in addition to being an excellent writer, had some spot-on predictions of a virus-laden Internet in Shockwave Rhttp://slashdot.org/article.pl?sid=05/03/29/0123247&amp;from=rsser. Fortunately, the predictions of his eco-dystopia The Sheep Look Up have not come to pass. Yet."

http://slashdot.org/article.pl?shttp://slashdot.org/article.pl?sid=05/03/29/0123247&amp;from=rss=05/03/29/0123247&amp;from=rss</t>
<t tx="ekr.20050329092553.32">Ars Technica Builds Make Magazine's Steadicam (hardware, hardhack)

An anonymous reader writes "Make magazine has been out for a little over a month now and was given high marks in a Slashdot review. Ars Technica has taken their review one step further by building the $14 steadicam project and testing it out. (be sure to check out the QuickTime vhttp://hardware.slashdot.org/article.pl?sid=05/03/29/0056206&amp;from=rsseo at the end to see their results...)"

http://hardware.slashdot.org/article.pl?shttp://hardware.slashdot.org/article.pl?sid=05/03/29/0056206&amp;from=rss=05/03/29/0056206&amp;from=rss</t>
<t tx="ekr.20050329092553.33">New Photovoltaics Made with Titanium Foil (science, tech)

Memorize writes "A company called Daystartech has released a new type of photovoltaic cell which, unlike almost all the cells currently in use, does not silicon. This is based on a thin titanium film. Given the current shortage of solar-grade silicon, and all-time high oil prices, maybe titanium solar panels are here at the right time. The questions are, will they release it as a consumer solar product, and what will be the price per kilowatt hour?"

http://science.slashdot.org/article.pl?shttp://science.slashdot.org/article.pl?sid=05/03/28/2320211&amp;from=rss=05/03/28/2320211&amp;from=rss</t>
<t tx="ekr.20050329092553.4">Splits paralyse Iraqi parliament

Iraq's parliament reconvenes, but remains deadlocked over the formation of a new government.</t>
<t tx="ekr.20050329092553.5">Mongolians protest for new poll

Activists in Mongolia call for fresh elections, 
in an action apparently inspired by the situation in Kyrgyzstan.</t>
<t tx="ekr.20050329092553.6">Libya's Bulgarian medics appeal

Six medics appeal against the death sentence imposed in Libya for deliberately infecting children with HIV.</t>
<t tx="ekr.20050329092553.7">Schiavo rivals 'agree to autopsy'

Terri Schiavo's husband and parents seek to discover the extent of her brain-damage after her death.</t>
<t tx="ekr.20050329092553.8">Would-be sex tourist, 87, jailed

An octogenarian US man is jailed for 20 years for trying to travel to the Philippines for sex with young girls.</t>
<t tx="ekr.20050329092553.9">Golf: Funk claims Players title

Fred Funk's final-round 70 gives him victory in the lucrative Players Championship at Sawgrass.</t>
<t tx="ekr.20050817132814">@nocolor

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

@color</t>
<t tx="ekr.20060513122613"></t>
<t tx="ekr.20060513122613.1">@
opengl.h is just a test for long files
cltest\testprog is an xcc project to test functionality under win32 compile env, with it's gcc equivalent underneath.

no plugin conflicts detected with core plugins, read-only nodes, unl or linecol plugin.
should work with most plugins...
</t>
<t tx="ekr.20060513122613.10">#ifndef GL_DEFS
GL_EXT(void,glBlendColor,(GLclampf, GLclampf, GLclampf, GLclampf))
GL_EXT(void,glBlendEquation,(GLenum))
GL_EXT(void,glDrawRangeElements,(GLenum, GLuint, GLuint, GLsizei, GLenum, const GLvoid *))
GL_EXT(void,glColorTable,(GLenum, GLenum, GLsizei, GLenum, GLenum, const GLvoid *))
GL_EXT(void,glColorTableParameterfv,(GLenum, GLenum, const GLfloat *))
GL_EXT(void,glColorTableParameteriv,(GLenum, GLenum, const GLint *))
GL_EXT(void,glCopyColorTable,(GLenum, GLenum, GLint, GLint, GLsizei))
GL_EXT(void,glGetColorTable,(GLenum, GLenum, GLenum, GLvoid *))
GL_EXT(void,glGetColorTableParameterfv,(GLenum, GLenum, GLfloat *))
GL_EXT(void,glGetColorTableParameteriv,(GLenum, GLenum, GLint *))
GL_EXT(void,glColorSubTable,(GLenum, GLsizei, GLsizei, GLenum, GLenum, const GLvoid *))
GL_EXT(void,glCopyColorSubTable,(GLenum, GLsizei, GLint, GLint, GLsizei))
GL_EXT(void,glConvolutionFilter1D,(GLenum, GLenum, GLsizei, GLenum, GLenum, const GLvoid *))
GL_EXT(void,glConvolutionFilter2D,(GLenum, GLenum, GLsizei, GLsizei, GLenum, GLenum, const GLvoid *))
GL_EXT(void,glConvolutionParameterf,(GLenum, GLenum, GLfloat))
GL_EXT(void,glConvolutionParameterfv,(GLenum, GLenum, const GLfloat *))
GL_EXT(void,glConvolutionParameteri,(GLenum, GLenum, GLint))
GL_EXT(void,glConvolutionParameteriv,(GLenum, GLenum, const GLint *))
GL_EXT(void,glCopyConvolutionFilter1D,(GLenum, GLenum, GLint, GLint, GLsizei))
GL_EXT(void,glCopyConvolutionFilter2D,(GLenum, GLenum, GLint, GLint, GLsizei, GLsizei))
GL_EXT(void,glGetConvolutionFilter,(GLenum, GLenum, GLenum, GLvoid *))
GL_EXT(void,glGetConvolutionParameterfv,(GLenum, GLenum, GLfloat *))
GL_EXT(void,glGetConvolutionParameteriv,(GLenum, GLenum, GLint *))
GL_EXT(void,glGetSeparableFilter,(GLenum, GLenum, GLenum, GLvoid *, GLvoid *, GLvoid *))
GL_EXT(void,glSeparableFilter2D,(GLenum, GLenum, GLsizei, GLsizei, GLenum, GLenum, const GLvoid *, const GLvoid *))
GL_EXT(void,glGetHistogram,(GLenum, GLboolean, GLenum, GLenum, GLvoid *))
GL_EXT(void,glGetHistogramParameterfv,(GLenum, GLenum, GLfloat *))
GL_EXT(void,glGetHistogramParameteriv,(GLenum, GLenum, GLint *))
GL_EXT(void,glGetMinmax,(GLenum, GLboolean, GLenum, GLenum, GLvoid *))
GL_EXT(void,glGetMinmaxParameterfv,(GLenum, GLenum, GLfloat *))
GL_EXT(void,glGetMinmaxParameteriv,(GLenum, GLenum, GLint *))
GL_EXT(void,glHistogram,(GLenum, GLsizei, GLenum, GLboolean))
GL_EXT(void,glMinmax,(GLenum, GLenum, GLboolean))
GL_EXT(void,glResetHistogram,(GLenum))
GL_EXT(void,glResetMinmax,(GLenum))
GL_EXT(void,glTexImage3D,(GLenum, GLint, GLint, GLsizei, GLsizei, GLsizei, GLint, GLenum, GLenum, const GLvoid *))
GL_EXT(void,glTexSubImage3D,(GLenum, GLint, GLint, GLint, GLint, GLsizei, GLsizei, GLsizei, GLenum, GLenum, const GLvoid *))
GL_EXT(void,glCopyTexSubImage3D,(GLenum, GLint, GLint, GLint, GLint, GLint, GLint, GLsizei, GLsizei))
#endif</t>
<t tx="ekr.20060513122613.11">#if USE_OPENGL &gt;= 3
	@others
#endif</t>
<t tx="ekr.20060513122613.12">#ifdef GL_DEFS
#define GL_TEXTURE0                       0x84C0
#define GL_TEXTURE1                       0x84C1
#define GL_TEXTURE2                       0x84C2
#define GL_TEXTURE3                       0x84C3
#define GL_TEXTURE4                       0x84C4
#define GL_TEXTURE5                       0x84C5
#define GL_TEXTURE6                       0x84C6
#define GL_TEXTURE7                       0x84C7
#define GL_TEXTURE8                       0x84C8
#define GL_TEXTURE9                       0x84C9
#define GL_TEXTURE10                      0x84CA
#define GL_TEXTURE11                      0x84CB
#define GL_TEXTURE12                      0x84CC
#define GL_TEXTURE13                      0x84CD
#define GL_TEXTURE14                      0x84CE
#define GL_TEXTURE15                      0x84CF
#define GL_TEXTURE16                      0x84D0
#define GL_TEXTURE17                      0x84D1
#define GL_TEXTURE18                      0x84D2
#define GL_TEXTURE19                      0x84D3
#define GL_TEXTURE20                      0x84D4
#define GL_TEXTURE21                      0x84D5
#define GL_TEXTURE22                      0x84D6
#define GL_TEXTURE23                      0x84D7
#define GL_TEXTURE24                      0x84D8
#define GL_TEXTURE25                      0x84D9
#define GL_TEXTURE26                      0x84DA
#define GL_TEXTURE27                      0x84DB
#define GL_TEXTURE28                      0x84DC
#define GL_TEXTURE29                      0x84DD
#define GL_TEXTURE30                      0x84DE
#define GL_TEXTURE31                      0x84DF
#define GL_ACTIVE_TEXTURE                 0x84E0
#define GL_CLIENT_ACTIVE_TEXTURE          0x84E1
#define GL_MAX_TEXTURE_UNITS              0x84E2
#define GL_TRANSPOSE_MODELVIEW_MATRIX     0x84E3
#define GL_TRANSPOSE_PROJECTION_MATRIX    0x84E4
#define GL_TRANSPOSE_TEXTURE_MATRIX       0x84E5
#define GL_TRANSPOSE_COLOR_MATRIX         0x84E6
#define GL_MULTISAMPLE                    0x809D
#define GL_SAMPLE_ALPHA_TO_COVERAGE       0x809E
#define GL_SAMPLE_ALPHA_TO_ONE            0x809F
#define GL_SAMPLE_COVERAGE                0x80A0
#define GL_SAMPLE_BUFFERS                 0x80A8
#define GL_SAMPLES                        0x80A9
#define GL_SAMPLE_COVERAGE_VALUE          0x80AA
#define GL_SAMPLE_COVERAGE_INVERT         0x80AB
#define GL_MULTISAMPLE_BIT                0x20000000
#define GL_NORMAL_MAP                     0x8511
#define GL_REFLECTION_MAP                 0x8512
#define GL_TEXTURE_CUBE_MAP               0x8513
#define GL_TEXTURE_BINDING_CUBE_MAP       0x8514
#define GL_TEXTURE_CUBE_MAP_POSITIVE_X    0x8515
#define GL_TEXTURE_CUBE_MAP_NEGATIVE_X    0x8516
#define GL_TEXTURE_CUBE_MAP_POSITIVE_Y    0x8517
#define GL_TEXTURE_CUBE_MAP_NEGATIVE_Y    0x8518
#define GL_TEXTURE_CUBE_MAP_POSITIVE_Z    0x8519
#define GL_TEXTURE_CUBE_MAP_NEGATIVE_Z    0x851A
#define GL_PROXY_TEXTURE_CUBE_MAP         0x851B
#define GL_MAX_CUBE_MAP_TEXTURE_SIZE      0x851C
#define GL_COMPRESSED_ALPHA               0x84E9
#define GL_COMPRESSED_LUMINANCE           0x84EA
#define GL_COMPRESSED_LUMINANCE_ALPHA     0x84EB
#define GL_COMPRESSED_INTENSITY           0x84EC
#define GL_COMPRESSED_RGB                 0x84ED
#define GL_COMPRESSED_RGBA                0x84EE
#define GL_TEXTURE_COMPRESSION_HINT       0x84EF
#define GL_TEXTURE_COMPRESSED_IMAGE_SIZE  0x86A0
#define GL_TEXTURE_COMPRESSED             0x86A1
#define GL_NUM_COMPRESSED_TEXTURE_FORMATS 0x86A2
#define GL_COMPRESSED_TEXTURE_FORMATS     0x86A3
#define GL_CLAMP_TO_BORDER                0x812D
#define GL_CLAMP_TO_BORDER_SGIS           0x812D
#define GL_COMBINE                        0x8570
#define GL_COMBINE_RGB                    0x8571
#define GL_COMBINE_ALPHA                  0x8572
#define GL_SOURCE0_RGB                    0x8580
#define GL_SOURCE1_RGB                    0x8581
#define GL_SOURCE2_RGB                    0x8582
#define GL_SOURCE0_ALPHA                  0x8588
#define GL_SOURCE1_ALPHA                  0x8589
#define GL_SOURCE2_ALPHA                  0x858A
#define GL_OPERAND0_RGB                   0x8590
#define GL_OPERAND1_RGB                   0x8591
#define GL_OPERAND2_RGB                   0x8592
#define GL_OPERAND0_ALPHA                 0x8598
#define GL_OPERAND1_ALPHA                 0x8599
#define GL_OPERAND2_ALPHA                 0x859A
#define GL_RGB_SCALE                      0x8573
#define GL_ADD_SIGNED                     0x8574
#define GL_INTERPOLATE                    0x8575
#define GL_SUBTRACT                       0x84E7
#define GL_CONSTANT                       0x8576
#define GL_PRIMARY_COLOR                  0x8577
#define GL_PREVIOUS                       0x8578
#define GL_DOT3_RGB                       0x86AE
#define GL_DOT3_RGBA                      0x86AF
#endif
</t>
<t tx="ekr.20060513122613.13">#ifndef GL_DEFS
GL_EXT(void,glActiveTexture,(GLenum))
GL_EXT(void,glClientActiveTexture,(GLenum))
GL_EXT(void,glMultiTexCoord1d,(GLenum,GLdouble))
GL_EXT(void,glMultiTexCoord1dv,(GLenum,const GLdouble *))
GL_EXT(void,glMultiTexCoord1f,(GLenum,GLfloat))
GL_EXT(void,glMultiTexCoord1fv,(GLenum,const GLfloat *))
GL_EXT(void,glMultiTexCoord1i,(GLenum,GLint))
GL_EXT(void,glMultiTexCoord1iv,(GLenum,const GLint*))
GL_EXT(void,glMultiTexCoord1s,(GLenum,GLshort))
GL_EXT(void,glMultiTexCoord1sv,(GLenum,const GLshort*))
GL_EXT(void,glMultiTexCoord2d,(GLenum,GLdouble,GLdouble))
GL_EXT(void,glMultiTexCoord2dv,(GLenum,const GLdouble*))
GL_EXT(void,glMultiTexCoord2f,(GLenum,GLfloat,GLfloat))
GL_EXT(void,glMultiTexCoord2fv,(GLenum,const GLfloat*))
GL_EXT(void,glMultiTexCoord2i,(GLenum,GLint,GLint))
GL_EXT(void,glMultiTexCoord2iv,(GLenum,const GLint*))
GL_EXT(void,glMultiTexCoord2s,(GLenum,GLshort,GLshort))
GL_EXT(void,glMultiTexCoord2sv,(GLenum,const GLshort*))
GL_EXT(void,glMultiTexCoord3d,(GLenum,GLdouble,GLdouble,GLdouble))
GL_EXT(void,glMultiTexCoord3dv,(GLenum,const GLdouble*))
GL_EXT(void,glMultiTexCoord3f,(GLenum,GLfloat,GLfloat,GLfloat))
GL_EXT(void,glMultiTexCoord3fv,(GLenum,const GLfloat*))
GL_EXT(void,glMultiTexCoord3i,(GLenum,GLint,GLint,GLint))
GL_EXT(void,glMultiTexCoord3iv,(GLenum,const GLint*))
GL_EXT(void,glMultiTexCoord3s,(GLenum,GLshort,GLshort,GLshort))
GL_EXT(void,glMultiTexCoord3sv,(GLenum,const GLshort*))
GL_EXT(void,glMultiTexCoord4d,(GLenum,GLdouble,GLdouble,GLdouble,GLdouble))
GL_EXT(void,glMultiTexCoord4dv,(GLenum,const GLdouble *))
GL_EXT(void,glMultiTexCoord4f,(GLenum,GLfloat,GLfloat,GLfloat,GLfloat))
GL_EXT(void,glMultiTexCoord4fv,(GLenum,const GLfloat *))
GL_EXT(void,glMultiTexCoord4i,(GLenum,GLint,GLint,GLint,GLint))
GL_EXT(void,glMultiTexCoord4iv,(GLenum,const GLint *))
GL_EXT(void,glMultiTexCoord4s,(GLenum,GLshort,GLshort,GLshort,GLshort))
GL_EXT(void,glMultiTexCoord4sv,(GLenum,const GLshort *))
GL_EXT(void,glLoadTransposeMatrixf,(const GLfloat *))
GL_EXT(void,glLoadTransposeMatrixd,(const GLdouble *))
GL_EXT(void,glMultTransposeMatrixf,(const GLfloat *))
GL_EXT(void,glMultTransposeMatrixd,(const GLdouble *))
GL_EXT(void,glSampleCoverage,(GLclampf,GLboolean))
GL_EXT(void,glCompressedTexImage3D,(GLenum,GLint,GLenum,GLsizei,GLsizei,GLsizei,GLint,GLsizei,const GLvoid *))
GL_EXT(void,glCompressedTexImage2D,(GLenum,GLint,GLenum,GLsizei,GLsizei,GLint,GLsizei,const GLvoid *))
GL_EXT(void,glCompressedTexImage1D,(GLenum,GLint,GLenum,GLsizei,GLint,GLsizei,const GLvoid *))
GL_EXT(void,glCompressedTexSubImage3D,(GLenum,GLint,GLint,GLint,GLint,GLsizei,GLsizei,GLsizei,GLenum,GLsizei,const GLvoid *))
GL_EXT(void,glCompressedTexSubImage2D,(GLenum,GLint,GLint,GLint,GLsizei,GLsizei,GLenum,GLsizei,const GLvoid *))
GL_EXT(void,glCompressedTexSubImage1D,(GLenum,GLint,GLint,GLsizei,GLenum,GLsizei,const GLvoid *))
GL_EXT(void,glGetCompressedTexImage,(GLenum,GLint,GLvoid *))
#endif</t>
<t tx="ekr.20060513122613.14">#if USE_OPENGL &gt;= 4
	@others
#endif</t>
<t tx="ekr.20060513122613.15">#ifdef GL_DEFS
#define GL_BLEND_DST_RGB                  0x80C8
#define GL_BLEND_SRC_RGB                  0x80C9
#define GL_BLEND_DST_ALPHA                0x80CA
#define GL_BLEND_SRC_ALPHA                0x80CB
#define GL_POINT_SIZE_MIN                 0x8126
#define GL_POINT_SIZE_MAX                 0x8127
#define GL_POINT_FADE_THRESHOLD_SIZE      0x8128
#define GL_POINT_DISTANCE_ATTENUATION     0x8129
#define GL_GENERATE_MIPMAP                0x8191
#define GL_GENERATE_MIPMAP_HINT           0x8192
#define GL_DEPTH_COMPONENT16              0x81A5
#define GL_DEPTH_COMPONENT24              0x81A6
#define GL_DEPTH_COMPONENT32              0x81A7
#define GL_MIRRORED_REPEAT                0x8370
#define GL_FOG_COORDINATE_SOURCE          0x8450
#define GL_FOG_COORDINATE                 0x8451
#define GL_FRAGMENT_DEPTH                 0x8452
#define GL_CURRENT_FOG_COORDINATE         0x8453
#define GL_FOG_COORDINATE_ARRAY_TYPE      0x8454
#define GL_FOG_COORDINATE_ARRAY_STRIDE    0x8455
#define GL_FOG_COORDINATE_ARRAY_POINTER   0x8456
#define GL_FOG_COORDINATE_ARRAY           0x8457
#define GL_COLOR_SUM                      0x8458
#define GL_CURRENT_SECONDARY_COLOR        0x8459
#define GL_SECONDARY_COLOR_ARRAY_SIZE     0x845A
#define GL_SECONDARY_COLOR_ARRAY_TYPE     0x845B
#define GL_SECONDARY_COLOR_ARRAY_STRIDE   0x845C
#define GL_SECONDARY_COLOR_ARRAY_POINTER  0x845D
#define GL_SECONDARY_COLOR_ARRAY          0x845E
#define GL_MAX_TEXTURE_LOD_BIAS           0x84FD
#define GL_TEXTURE_FILTER_CONTROL         0x8500
#define GL_TEXTURE_LOD_BIAS               0x8501
#define GL_INCR_WRAP                      0x8507
#define GL_DECR_WRAP                      0x8508
#define GL_TEXTURE_DEPTH_SIZE             0x884A
#define GL_DEPTH_TEXTURE_MODE             0x884B
#define GL_TEXTURE_COMPARE_MODE           0x884C
#define GL_TEXTURE_COMPARE_FUNC           0x884D
#define GL_COMPARE_R_TO_TEXTURE           0x884E
#endif</t>
<t tx="ekr.20060513122613.16">#ifndef GL_DEFS
GL_EXT(void,glBlendFuncSeparate,(GLenum,GLenum,GLenum,GLenum))
GL_EXT(void,glFogCoordf,(GLfloat))
GL_EXT(void,glFogCoordfv,(const GLfloat *))
GL_EXT(void,glFogCoordd,(GLdouble))
GL_EXT(void,glFogCoorddv,(const GLdouble *))
GL_EXT(void,glFogCoordPointer,(GLenum,GLsizei,const GLvoid *))
GL_EXT(void,glMultiDrawArrays,(GLenum,GLint *,GLsizei *,GLsizei))
GL_EXT(void,glMultiDrawElements,(GLenum,const GLsizei *,GLenum,const GLvoid* *,GLsizei))
GL_EXT(void,glPointParameterf,(GLenum,GLfloat))
GL_EXT(void,glPointParameterfv,(GLenum,const GLfloat *))
GL_EXT(void,glPointParameteri,(GLenum,GLint))
GL_EXT(void,glPointParameteriv,(GLenum,const GLint *))
GL_EXT(void,glSecondaryColor3b,(GLbyte,GLbyte,GLbyte))
GL_EXT(void,glSecondaryColor3bv,(const GLbyte *))
GL_EXT(void,glSecondaryColor3d,(GLdouble,GLdouble,GLdouble))
GL_EXT(void,glSecondaryColor3dv,(const GLdouble *))
GL_EXT(void,glSecondaryColor3f,(GLfloat,GLfloat,GLfloat))
GL_EXT(void,glSecondaryColor3fv,(const GLfloat *))
GL_EXT(void,glSecondaryColor3i,(GLint,GLint,GLint))
GL_EXT(void,glSecondaryColor3iv,(const GLint *))
GL_EXT(void,glSecondaryColor3s,(GLshort,GLshort,GLshort))
GL_EXT(void,glSecondaryColor3sv,(const GLshort *))
GL_EXT(void,glSecondaryColor3ub,(GLubyte,GLubyte,GLubyte))
GL_EXT(void,glSecondaryColor3ubv,(const GLubyte *))
GL_EXT(void,glSecondaryColor3ui,(GLuint,GLuint,GLuint))
GL_EXT(void,glSecondaryColor3uiv,(const GLuint *))
GL_EXT(void,glSecondaryColor3us,(GLushort,GLushort,GLushort))
GL_EXT(void,glSecondaryColor3usv,(const GLushort *))
GL_EXT(void,glSecondaryColorPointer,(GLint,GLenum,GLsizei,const GLvoid *))
GL_EXT(void,glWindowPos2d,(GLdouble,GLdouble))
GL_EXT(void,glWindowPos2dv,(const GLdouble *))
GL_EXT(void,glWindowPos2f,(GLfloat,GLfloat))
GL_EXT(void,glWindowPos2fv,(const GLfloat *))
GL_EXT(void,glWindowPos2i,(GLint,GLint))
GL_EXT(void,glWindowPos2iv,(const GLint *))
GL_EXT(void,glWindowPos2s,(GLshort,GLshort))
GL_EXT(void,glWindowPos2sv,(const GLshort *))
GL_EXT(void,glWindowPos3d,(GLdouble,GLdouble,GLdouble))
GL_EXT(void,glWindowPos3dv,(const GLdouble *))
GL_EXT(void,glWindowPos3f,(GLfloat,GLfloat,GLfloat))
GL_EXT(void,glWindowPos3fv,(const GLfloat *))
GL_EXT(void,glWindowPos3i,(GLint,GLint,GLint))
GL_EXT(void,glWindowPos3iv,(const GLint *))
GL_EXT(void,glWindowPos3s,(GLshort,GLshort,GLshort))
GL_EXT(void,glWindowPos3sv,(const GLshort *))
#endif</t>
<t tx="ekr.20060513122613.17" xcc_child_cfg="7d7100580b000000427265616b506f696e747371017d7102732e">#if USE_OPENGL &gt;= 5
	@others
#endif</t>
<t tx="ekr.20060513122613.18" xcc_child_cfg="7d7100580b000000427265616b506f696e747371017d7102732e">#ifdef GL_DEFS
#define GL_BUFFER_SIZE                    0x8764
#define GL_BUFFER_USAGE                   0x8765
#define GL_QUERY_COUNTER_BITS             0x8864
#define GL_CURRENT_QUERY                  0x8865
#define GL_QUERY_RESULT                   0x8866
#define GL_QUERY_RESULT_AVAILABLE         0x8867
#define GL_ARRAY_BUFFER                   0x8892
#define GL_ELEMENT_ARRAY_BUFFER           0x8893
#define GL_ARRAY_BUFFER_BINDING           0x8894
#define GL_ELEMENT_ARRAY_BUFFER_BINDING   0x8895
#define GL_VERTEX_ARRAY_BUFFER_BINDING    0x8896
#define GL_NORMAL_ARRAY_BUFFER_BINDING    0x8897
#define GL_COLOR_ARRAY_BUFFER_BINDING     0x8898
#define GL_INDEX_ARRAY_BUFFER_BINDING     0x8899
#define GL_TEXTURE_COORD_ARRAY_BUFFER_BINDING 0x889A
#define GL_EDGE_FLAG_ARRAY_BUFFER_BINDING 0x889B
#define GL_SECONDARY_COLOR_ARRAY_BUFFER_BINDING 0x889C
#define GL_FOG_COORDINATE_ARRAY_BUFFER_BINDING 0x889D
#define GL_WEIGHT_ARRAY_BUFFER_BINDING    0x889E
#define GL_VERTEX_ATTRIB_ARRAY_BUFFER_BINDING 0x889F
#define GL_READ_ONLY                      0x88B8
#define GL_WRITE_ONLY                     0x88B9
#define GL_READ_WRITE                     0x88BA
#define GL_BUFFER_ACCESS                  0x88BB
#define GL_BUFFER_MAPPED                  0x88BC
#define GL_BUFFER_MAP_POINTER             0x88BD
#define GL_STREAM_DRAW                    0x88E0
#define GL_STREAM_READ                    0x88E1
#define GL_STREAM_COPY                    0x88E2
#define GL_STATIC_DRAW                    0x88E4
#define GL_STATIC_READ                    0x88E5
#define GL_STATIC_COPY                    0x88E6
#define GL_DYNAMIC_DRAW                   0x88E8
#define GL_DYNAMIC_READ                   0x88E9
#define GL_DYNAMIC_COPY                   0x88EA
#define GL_SAMPLES_PASSED                 0x8914
#define GL_FOG_COORD_SOURCE               GL_FOG_COORDINATE_SOURCE
#define GL_FOG_COORD                      GL_FOG_COORDINATE
#define GL_CURRENT_FOG_COORD              GL_CURRENT_FOG_COORDINATE
#define GL_FOG_COORD_ARRAY_TYPE           GL_FOG_COORDINATE_ARRAY_TYPE
#define GL_FOG_COORD_ARRAY_STRIDE         GL_FOG_COORDINATE_ARRAY_STRIDE
#define GL_FOG_COORD_ARRAY_POINTER        GL_FOG_COORDINATE_ARRAY_POINTER
#define GL_FOG_COORD_ARRAY                GL_FOG_COORDINATE_ARRAY
#define GL_FOG_COORD_ARRAY_BUFFER_BINDING GL_FOG_COORDINATE_ARRAY_BUFFER_BINDING
#define GL_SRC0_RGB                       GL_SOURCE0_RGB
#define GL_SRC1_RGB                       GL_SOURCE1_RGB
#define GL_SRC2_RGB                       GL_SOURCE2_RGB
#define GL_SRC0_ALPHA                     GL_SOURCE0_ALPHA
#define GL_SRC1_ALPHA                     GL_SOURCE1_ALPHA
#define GL_SRC2_ALPHA                     GL_SOURCE2_ALPHA
#endif</t>
<t tx="ekr.20060513122613.19" xcc_child_cfg="7d7100580b000000427265616b506f696e747371017d7102732e">#ifndef GL_DEFS
GL_EXT(void,glGenQueries,(GLsizei,GLuint *))
GL_EXT(void,glDeleteQueries,(GLsizei,const GLuint *))
GL_EXT(GLboolean,glIsQuery,(GLuint))
GL_EXT(void,glBeginQuery,(GLenum,GLuint))
GL_EXT(void,glEndQuery,(GLenum))
GL_EXT(void,glGetQueryiv,(GLenum,GLenum,GLint *))
GL_EXT(void,glGetQueryObjectiv,(GLuint,GLenum,GLint *))
GL_EXT(void,glGetQueryObjectuiv,(GLuint,GLenum,GLuint *))
GL_EXT(void,glBindBuffer,(GLenum,GLuint))
GL_EXT(void,glDeleteBuffers,(GLsizei,const GLuint *))
GL_EXT(void,glGenBuffers,(GLsizei,GLuint *))
GL_EXT(GLboolean,glIsBuffer,(GLuint))
GL_EXT(void,glBufferData,(GLenum,GLsizeiptr,const GLvoid *,GLenum))
GL_EXT(void,glBufferSubData,(GLenum,GLintptr,GLsizeiptr,const GLvoid *))
GL_EXT(void,glGetBufferSubData,(GLenum,GLintptr,GLsizeiptr,GLvoid *))
GL_EXT(GLvoid*,glMapBuffer,(GLenum,GLenum))
GL_EXT(GLboolean,glUnmapBuffer,(GLenum))
GL_EXT(void,glGetBufferParameteriv,(GLenum,GLenum,GLint *))
GL_EXT(void,glGetBufferPointerv,(GLenum,GLenum,GLvoid* *))
#endif</t>
<t tx="ekr.20060513122613.2" xcc_cfg="7d710028580a00000045786563757461626c6571017d710228580a000000446c6c2063616c6c65727103580000000071045813000000457865637574696f6e20617267756d656e747371056804755804000000436f64657106680458070000004144445f4c4f477107680458050000005469746c657108680458070000005345545f4c4f47710968045806000000494e49544544710a580400000054727565710b5808000000436f6d70696c6572710c7d710d285814000000496e636c75646520736561726368207061746873710e6804580f0000004572726f7220646574656374696f6e710f6804680c6804580b000000557365206c69627261727971106804580e00000055736564206c696272617269657371116804580f000000446562756720617267756d656e747371126804580d000000436865636b2073796e7461786571136804580c0000004c6962726172792070617468711468045809000000417267756d656e7473711568045807000000557365207063687116680458090000004275696c64206578657117680458140000004c6962726172792073656172636820706174687371186804580c000000496e636c756465207061746871196804580b000000436f6d70696c6520706368711a680458090000004275696c6420646c6c711b68047558070000004f7074696f6e73711c7d711d28580700000045786563757465711e580500000046616c7365711f580c0000004372656174652066696c65737120580400000054727565712158130000004175746f20696e636c756465206865616465727122580500000046616c7365712358100000005365656b20627265616b706f696e74737124580500000046616c73657125580f000000436f6e6e65637420746f20706970657126580500000046616c736571275807000000436f6d70696c657128580500000046616c7365712958050000004465627567712a580500000046616c7365712b580b00000058636320766572626f7365712c580500000046616c7365712d580d00000046696c746572206f7574707574712e580500000046616c7365712f58100000005365656b206669727374206572726f727130580500000046616c73657131580c000000436f6c6f72697a65206c6f677132580500000046616c73657133755808000000446562756767657271347d713528580e0000004964656e7469667920627265616b71366804580400000053746f707137680458080000005069706520656f6c7138680468156804580e00000050726f6d7074207061747465726e71396804580e0000005175657279206c6f636174696f6e713a6804580800000046696e6420706964713b6804580b000000436c65617220627265616b713c680458080000004576616c75617465713d6804580f00000054617267657420706964207461736b713e6804580400000053746570713f6804580b0000004c69737420627265616b737140680458040000005461736b714168045808000000436f6e74696e756571426804580800000053746570206f757471436804580900000053657420627265616b71446804580d00000046696e64206c6f636174696f6e7145680458070000005374657020696e71466804683468045812000000526567756c61722065787072657373696f6e71476804580f000000427265616b20646574656374696f6e714868045802000000476f71496804580c00000053746172747570207461736b714a6804580900000053746570206f766572714b58040000006e657874714c75752e">@language c++

</t>
<t tx="ekr.20060513122613.20" xcc_child_cfg="7d7100580b000000427265616b506f696e747371017d7102732e">#ifndef GL_DEFS
WGL_PROC(BOOL,wglCopyContext,(HGLRC,HGLRC,UINT))
WGL_PROC(HGLRC,wglCreateContext,(HDC))
WGL_PROC(HGLRC,wglCreateLayerContext,(HDC,int))
WGL_PROC(BOOL,wglDeleteContext,(HGLRC))
WGL_PROC(HGLRC,wglGetCurrentContext,(VOID))
WGL_PROC(HDC,wglGetCurrentDC,(VOID))
WGL_PROC(PROC,wglGetProcAddress,(LPCSTR))
WGL_PROC(BOOL,wglMakeCurrent,(HDC,HGLRC))
WGL_PROC(BOOL,wglShareLists,(HGLRC,HGLRC))
WGL_PROC(BOOL,wglUseFontBitmapsA,(HDC,DWORD,DWORD,DWORD))
WGL_PROC(BOOL,wglUseFontBitmapsW,(HDC,DWORD,DWORD,DWORD))
WGL_PROC(BOOL,wglSwapBuffers,(HDC))
WGL_PROC(BOOL,wglUseFontOutlinesA,(HDC,DWORD,DWORD,DWORD,FLOAT,FLOAT,int,LPGLYPHMETRICSFLOAT))
WGL_PROC(BOOL,wglUseFontOutlinesW,(HDC,DWORD,DWORD,DWORD,FLOAT,FLOAT,int,LPGLYPHMETRICSFLOAT))
WGL_PROC(BOOL,wglDescribeLayerPlane,(HDC,int,int,UINT,LPLAYERPLANEDESCRIPTOR))
WGL_PROC(int,wglSetLayerPaletteEntries,(HDC,int,int,int,CONST COLORREF *))
WGL_PROC(int,wglGetLayerPaletteEntries,(HDC,int,int,int,COLORREF *))
WGL_PROC(BOOL,wglRealizeLayerPalette,(HDC,int,BOOL))
WGL_PROC(BOOL,wglSwapLayerBuffers,(HDC,UINT))
#if (WINVER &gt;= 0x0500)
	WGL_PROC(DWORD,SwapMultipleBuffers,(UINT,CONST WGLSWAP *))
#endif
#endif
</t>
<t tx="ekr.20060513122613.21" xcc_cfg="7d7100285808000000436f6d70696c657271017d7102285814000000496e636c7564652073656172636820706174687371035832000000433a5c53444b5c437573746f6d33325c696e636c7564650a433a5c53444b5c437573746f6d33325c696e636c75646533320a7104580f0000004572726f7220646574656374696f6e71055849000000283f503c46494c453e5b5e5c5c5d2b295c28283f503c4c494e453e5b302d395d2b295c29203a206572726f7220283f503c49443e435b302d395d2b293a20283f503c4445463e2e2b29710668015816000000433a5c53444b5c437573746f6d33325c636c2e6578657107580b000000557365206c6962726172797108580c0000002f44454641554c544c49423a7109580e00000055736564206c6962726172696573710a580b0000007573657233322e6c69620a710b580f000000446562756720617267756d656e7473710c58a5000000225f414253504154485f5c5f4e414d455f2e5f5352434558545f220a2f4665225f414253504154485f5c5f4e414d455f2e5f4558545f220a2f466f225f414253504154485f5c5f4e414d455f2e6f626a220a2f4664225f414253504154485f5c5f4e414d455f220a5f494e4350415448535f0a5f4255494c445f640a2f6e6f6c6f676f0a2f5a690a2f6c696e6b0a5f4c494250415448535f0a5f4c49425241524945535f0a710d580d000000436865636b2073796e74617865710e58030000002f5a73710f580c0000004c6962726172792070617468711058090000002f4c4942504154483a71115809000000417267756d656e74737112588a000000225f414253504154485f5c5f4e414d455f2e5f5352434558545f220a2f4665225f414253504154485f5c5f4e414d455f2e5f4558545f220a2f466f225f414253504154485f5c5f4e414d455f2e6f626a220a5f494e4350415448535f0a5f4255494c445f0a2f6e6f6c6f676f0a2f6c696e6b0a5f4c494250415448535f0a5f4c49425241524945535f0a7113580700000055736520706368711458030000002f5975711558090000004275696c6420657865711658030000002f4d4c711758140000004c696272617279207365617263682070617468737118582a000000433a5c53444b5c437573746f6d33325c6c69620a433a5c53444b5c437573746f6d33325c6c696233320a7119580c000000496e636c7564652070617468711a58020000002f49711b580b000000436f6d70696c6520706368711c58030000002f5963711d58090000004275696c6420646c6c711e58030000002f4c44711f75580a00000045786563757461626c6571207d712128580a000000446c6c2063616c6c65727122580000000071235813000000457865637574696f6e20617267756d656e747371246823755804000000436f64657125682358070000004144445f4c4f477126682358050000005469746c6571275810000000636c5f6364625f77696e33325f65786571285805000000576174636871295d712a580100000061712b61580b000000427265616b706f696e7473712c7d712d2858050000006370703a38712e5807000000456e61626c6564712f58060000006370703a31387130682f7558070000005345545f4c4f47713168235806000000494e4954454471325804000000547275657133580b000000427265616b506f696e747371347d71352858060000006370703a313571365807000000456e61626c6564713758060000006370703a313371385807000000456e61626c656471397558070000004f7074696f6e73713a7d713b28580700000045786563757465713c580500000046616c7365713d580c0000004372656174652066696c6573713e580400000054727565713f58130000004175746f20696e636c756465206865616465727140580400000054727565714158100000005365656b20627265616b706f696e747371425804000000547275657143580f000000436f6e6e65637420746f2070697065714468235807000000436f6d70696c65714558040000005472756571465805000000446562756771475804000000547275657148580b00000058636320766572626f73657149580400000054727565714a580d00000046696c746572206f7574707574714b580500000046616c7365714c58100000005365656b206669727374206572726f72714d580500000046616c7365714e7558080000004465627567676572714f7d715028580e0000004964656e7469667920627265616b7151582700000020283f503c49443e5b302d395d2b29202e2b5f46494c455f282040207c3a295f4c494e455f2e2b7152580400000053746f707153580100000071715458080000005069706520656f6c715558040000005c6e5c7271566812585c0000002d6c696e6573202d47202d320a2d7372637061746820225f414253504154485f220a2d7920227372762a5f414253504154485f220a2d6920225f414253504154485f220a225f414253504154485f5c5c5f4e414d455f2e657865220a7157580e00000050726f6d7074207061747465726e715858010000003e7159580e0000005175657279206c6f636174696f6e715a58090000006c732e203b206c7363715b580800000046696e6420706964715c5821000000306e283f503c5049443e5b302d395d2b29202e2a5f4e414d455f5c2e5f4558545f715d580b000000436c65617220627265616b715e58070000006263205f49445f715f58080000004576616c75617465716058020000003f3f7161580f00000054617267657420706964207461736b716258090000002e746c697374202d63716358040000005374657071645801000000707165580b0000004c69737420627265616b7371665802000000626c716758040000005461736b716868235808000000436f6e74696e75657169580100000067716a580800000053746570206f7574716b58020000006775716c580900000053657420627265616b716d5812000000627020605f46494c455f3a5f4c494e455f60716e580d00000046696e64206c6f636174696f6e716f583200000043757272656e743a202e2a5f4e414d455f5c2e283f503c4558543e2e2b295c28283f503c4c494e453e5b302d395d2b295c29717058070000005374657020696e71715801000000747172684f581e000000433a5c53444b5c437573746f6d33325c77696e6462675c6364622e65786571735812000000526567756c61722065787072657373696f6e7174580c000000507265737320454e5445520a7175580f000000427265616b20646574656374696f6e71765816000000427265616b706f696e74205b302d395d2b206869740a71775802000000476f7178686a580c00000053746172747570207461736b7179582b0000007371653b6c2b2a3b206c7370202d61203120303b206c737020303b2062702077696e6d61696e3b2020670a717a580900000053746570206f766572717b58040000006e657874717c75752e">@language c++
</t>
<t tx="ekr.20060513122613.22" xcc_child_cfg="7d7100580b000000427265616b506f696e747371017d7102732e"></t>
<t tx="ekr.20060513122613.23" xcc_child_cfg="7d71002858100000004865616465724c696e654e756d626572710158010000003071025810000000536f757263654c696e654e756d62657271036802580b000000427265616b506f696e747371047d7105752e">#define WIN32_LEAN_AND_MEAN
#include &lt;windows.h&gt; // the main windows headers
#include &lt;windowsx.h&gt; // a lot of cool macros</t>
<t tx="ekr.20060513122613.24" xcc_child_cfg="7d71002858100000004865616465724c696e654e756d626572710158010000003571025810000000536f757263654c696e654e756d62657271035801000000347104580b000000427265616b506f696e747371057d71062858010000003171075807000000456e61626c65647108580200000031317109680875752e">char* a ="allo";
// call message box api with NULL for parent window handle
MessageBox(NULL, "THERE CAN BE ONLY ONE!!!",
"MY FIRST WINDOWS PROGRAM",
MB_OK | MB_ICONEXCLAMATION);
a="salut";
a="jean";
a="pierre";
a="pierre";
// exit program
return(0);

</t>
<t tx="ekr.20060513122613.25" xcc_cfg="7d7100285808000000436f6d70696c657271017d7102285814000000496e636c7564652073656172636820706174687371035815000000433a5c53444b5c4d696e47575c696e636c7564650a7104580f0000004572726f7220646574656374696f6e71055849000000283f503c46494c453e5b5e5c5c5d2b295c28283f503c4c494e453e5b302d395d2b295c29203a206572726f7220283f503c49443e435b302d395d2b293a20283f503c4445463e2e2b29710668015818000000433a5c53444b5c4d696e47575c62696e5c6763632e6578657107580b000000557365206c696272617279710858020000002d6c7109580e00000055736564206c6962726172696573710a5800000000710b580f000000446562756720617267756d656e7473710c585c000000225f414253504154485f5c5f4e414d455f2e5f5352434558545f220a2d6f225f414253504154485f5c5f4e414d455f2e5f4558545f220a5f494e4350415448535f0a2d670a5f4c494250415448535f0a5f4c49425241524945535f0a710d580d000000436865636b2073796e74617865710e58030000002f5a73710f580c0000004c6962726172792070617468711058020000002d4c71115809000000417267756d656e747371125859000000225f414253504154485f5c5f4e414d455f2e5f5352434558545f220a2d6f225f414253504154485f5c5f4e414d455f2e5f4558545f220a5f494e4350415448535f0a5f4c494250415448535f0a5f4c49425241524945535f0a7113580700000055736520706368711458030000002f5975711558090000004275696c6420657865711658030000002f4d4c711758140000004c6962726172792073656172636820706174687371185811000000433a5c53444b5c4d696e47575c6c69620a7119580c000000496e636c7564652070617468711a58020000002d49711b580b000000436f6d70696c6520706368711c58030000002f5963711d58090000004275696c6420646c6c711e58030000002f4c44711f75580a00000045786563757461626c6571207d712128580a000000446c6c2063616c6c65727122680b5813000000457865637574696f6e20617267756d656e74737123680b755804000000436f64657124680b58070000004144445f4c4f477125680b58050000005469746c657126580b0000006763635f6764625f65786571275805000000576174636871285d7129580100000061712a61580b000000427265616b706f696e7473712b7d712c2858050000006370703a38712d5807000000456e61626c6564712e58060000006370703a3138712f682e7558070000005345545f4c4f4771305811000000406c616e677561676520632b2b0a20430a71315806000000494e4954454471325804000000547275657133580b000000427265616b506f696e747371347d71352858060000006370703a313271365807000000456e61626c6564713758060000006370703a313571385807000000456e61626c6564713958050000006370703a38713a5807000000456e61626c6564713b7558070000004f7074696f6e73713c7d713d28580700000045786563757465713e580500000046616c7365713f580c0000004372656174652066696c65737140580400000054727565714158130000004175746f20696e636c756465206865616465727142580400000054727565714358100000005365656b20627265616b706f696e747371445804000000547275657145580f000000436f6e6e65637420746f20706970657146680b5807000000436f6d70696c6571475804000000547275657148580500000044656275677149580400000054727565714a580b00000058636320766572626f7365714b580400000054727565714c580d00000046696c746572206f7574707574714d580500000046616c7365714e58100000005365656b206669727374206572726f72714f5804000000547275657150755808000000446562756767657271517d715228580e0000004964656e7469667920627265616b7153680b580400000053746f707154580100000071715558080000005069706520656f6c715658020000005c6e715768125819000000225f414253504154485f5c5c5f4e414d455f2e65786522200a7158580e00000050726f6d7074207061747465726e715958030000005b295d715a580e0000005175657279206c6f636174696f6e715b580100000066715c580800000046696e6420706964715d58210000005f4e414d455f5c2e5f4558545f202b283f503c5049443e5b302d395d2b29202e2b715e580b000000436c65617220627265616b715f5813000000636c656172205f46494c455f3a5f4c494e455f716058080000004576616c75617465716158060000007072696e74207162580f00000054617267657420706964207461736b716358320000007368656c6c207461736b6c697374202f6e68202f66692022494d4147454e414d45206571205f4e414d455f2e5f4558545f22716458040000005374657071655804000000737465707166580b0000004c69737420627265616b737167680b58040000005461736b71685802000000710a71695808000000436f6e74696e7565716a5808000000636f6e74696e7565716b580800000053746570206f7574716c580600000066696e697368716d580900000053657420627265616b716e5813000000627265616b205f46494c455f3a5f4c494e455f716f580d00000046696e64206c6f636174696f6e7170582800000061742e2b5f4e414d455f5c2e283f503c4558543e2e2b293a283f503c4c494e453e5b302d395d2b29717158070000005374657020696e7172580400000073746570717368515818000000433a5c53444b5c4d696e47575c62696e5c6764622e65786571745812000000526567756c61722065787072657373696f6e7175580f00000050726f6772616d206578697465640a7176580f000000427265616b20646574656374696f6e71775816000000427265616b706f696e74205b302d395d2b2c202e2b0a71785802000000476f7179580300000072756e717a580c00000053746172747570207461736b717b582e000000627265616b206d61696e0a736574206c69737473697a6520310a73657420636f6e6669726d206f66660a72756e0a717c580900000053746570206f766572717d58040000006e657874717e75752e">@language c++
</t>
<t tx="ekr.20060513122613.3" xcc_child_cfg="7d7100580b000000427265616b506f696e747371017d7102732e">#ifndef USE_OPENGL
	#define USE_OPENGL 1
#endif</t>
<t tx="ekr.20060513122613.4" xcc_child_cfg="7d7100580b000000427265616b506f696e747371017d7102732e">#ifdef GL_DEFS
typedef unsigned int GLenum;
typedef unsigned char GLboolean;
typedef unsigned int GLbitfield;
typedef signed char GLbyte;
typedef short GLshort;
typedef int GLint;
typedef int GLsizei;
typedef unsigned char GLubyte;
typedef unsigned short GLushort;
typedef unsigned int GLuint;
typedef float GLfloat;
typedef float GLclampf;
typedef double GLdouble;
typedef double GLclampd;
typedef void GLvoid;
typedef unsigned int GLintptr;
typedef unsigned int GLsizeiptr;
#endif</t>
<t tx="ekr.20060513122613.5" xcc_child_cfg="7d7100580b000000427265616b506f696e747371017d7102732e">#if USE_OPENGL &gt;= 1
	@others
#endif</t>
<t tx="ekr.20060513122613.6" xcc_child_cfg="7d7100580b000000427265616b506f696e747371017d7102732e">#ifdef GL_DEFS
#define GL_VERSION_1_1                    1
#define GL_ACCUM                          0x0100
#define GL_LOAD                           0x0101
#define GL_RETURN                         0x0102
#define GL_MULT                           0x0103
#define GL_ADD                            0x0104
#define GL_NEVER                          0x0200
#define GL_LESS                           0x0201
#define GL_EQUAL                          0x0202
#define GL_LEQUAL                         0x0203
#define GL_GREATER                        0x0204
#define GL_NOTEQUAL                       0x0205
#define GL_GEQUAL                         0x0206
#define GL_ALWAYS                         0x0207
#define GL_CURRENT_BIT                    0x00000001
#define GL_POINT_BIT                      0x00000002
#define GL_LINE_BIT                       0x00000004
#define GL_POLYGON_BIT                    0x00000008
#define GL_POLYGON_STIPPLE_BIT            0x00000010
#define GL_PIXEL_MODE_BIT                 0x00000020
#define GL_LIGHTING_BIT                   0x00000040
#define GL_FOG_BIT                        0x00000080
#define GL_DEPTH_BUFFER_BIT               0x00000100
#define GL_ACCUM_BUFFER_BIT               0x00000200
#define GL_STENCIL_BUFFER_BIT             0x00000400
#define GL_VIEWPORT_BIT                   0x00000800
#define GL_TRANSFORM_BIT                  0x00001000
#define GL_ENABLE_BIT                     0x00002000
#define GL_COLOR_BUFFER_BIT               0x00004000
#define GL_HINT_BIT                       0x00008000
#define GL_EVAL_BIT                       0x00010000
#define GL_LIST_BIT                       0x00020000
#define GL_TEXTURE_BIT                    0x00040000
#define GL_SCISSOR_BIT                    0x00080000
#define GL_ALL_ATTRIB_BITS                0x000fffff
#define GL_POINTS                         0x0000
#define GL_LINES                          0x0001
#define GL_LINE_LOOP                      0x0002
#define GL_LINE_STRIP                     0x0003
#define GL_TRIANGLES                      0x0004
#define GL_TRIANGLE_STRIP                 0x0005
#define GL_TRIANGLE_FAN                   0x0006
#define GL_QUADS                          0x0007
#define GL_QUAD_STRIP                     0x0008
#define GL_POLYGON                        0x0009
#define GL_ZERO                           0
#define GL_ONE                            1
#define GL_SRC_COLOR                      0x0300
#define GL_ONE_MINUS_SRC_COLOR            0x0301
#define GL_SRC_ALPHA                      0x0302
#define GL_ONE_MINUS_SRC_ALPHA            0x0303
#define GL_DST_ALPHA                      0x0304
#define GL_ONE_MINUS_DST_ALPHA            0x0305
#define GL_DST_COLOR                      0x0306
#define GL_ONE_MINUS_DST_COLOR            0x0307
#define GL_SRC_ALPHA_SATURATE             0x0308
#define GL_TRUE                           1
#define GL_FALSE                          0
#define GL_CLIP_PLANE0                    0x3000
#define GL_CLIP_PLANE1                    0x3001
#define GL_CLIP_PLANE2                    0x3002
#define GL_CLIP_PLANE3                    0x3003
#define GL_CLIP_PLANE4                    0x3004
#define GL_CLIP_PLANE5                    0x3005
#define GL_BYTE                           0x1400
#define GL_UNSIGNED_BYTE                  0x1401
#define GL_SHORT                          0x1402
#define GL_UNSIGNED_SHORT                 0x1403
#define GL_INT                            0x1404
#define GL_UNSIGNED_INT                   0x1405
#define GL_FLOAT                          0x1406
#define GL_2_BYTES                        0x1407
#define GL_3_BYTES                        0x1408
#define GL_4_BYTES                        0x1409
#define GL_DOUBLE                         0x140A
#define GL_NONE                           0
#define GL_FRONT_LEFT                     0x0400
#define GL_FRONT_RIGHT                    0x0401
#define GL_BACK_LEFT                      0x0402
#define GL_BACK_RIGHT                     0x0403
#define GL_FRONT                          0x0404
#define GL_BACK                           0x0405
#define GL_LEFT                           0x0406
#define GL_RIGHT                          0x0407
#define GL_FRONT_AND_BACK                 0x0408
#define GL_AUX0                           0x0409
#define GL_AUX1                           0x040A
#define GL_AUX2                           0x040B
#define GL_AUX3                           0x040C
#define GL_NO_ERROR                       0
#define GL_INVALID_ENUM                   0x0500
#define GL_INVALID_VALUE                  0x0501
#define GL_INVALID_OPERATION              0x0502
#define GL_STACK_OVERFLOW                 0x0503
#define GL_STACK_UNDERFLOW                0x0504
#define GL_OUT_OF_MEMORY                  0x0505
#define GL_2D                             0x0600
#define GL_3D                             0x0601
#define GL_3D_COLOR                       0x0602
#define GL_3D_COLOR_TEXTURE               0x0603
#define GL_4D_COLOR_TEXTURE               0x0604
#define GL_PASS_THROUGH_TOKEN             0x0700
#define GL_POINT_TOKEN                    0x0701
#define GL_LINE_TOKEN                     0x0702
#define GL_POLYGON_TOKEN                  0x0703
#define GL_BITMAP_TOKEN                   0x0704
#define GL_DRAW_PIXEL_TOKEN               0x0705
#define GL_COPY_PIXEL_TOKEN               0x0706
#define GL_LINE_RESET_TOKEN               0x0707
#define GL_EXP                            0x0800
#define GL_EXP2                           0x0801
#define GL_CW                             0x0900
#define GL_CCW                            0x0901
#define GL_COEFF                          0x0A00
#define GL_ORDER                          0x0A01
#define GL_DOMAIN                         0x0A02
#define GL_CURRENT_COLOR                  0x0B00
#define GL_CURRENT_INDEX                  0x0B01
#define GL_CURRENT_NORMAL                 0x0B02
#define GL_CURRENT_TEXTURE_COORDS         0x0B03
#define GL_CURRENT_RASTER_COLOR           0x0B04
#define GL_CURRENT_RASTER_INDEX           0x0B05
#define GL_CURRENT_RASTER_TEXTURE_COORDS  0x0B06
#define GL_CURRENT_RASTER_POSITION        0x0B07
#define GL_CURRENT_RASTER_POSITION_VALID  0x0B08
#define GL_CURRENT_RASTER_DISTANCE        0x0B09
#define GL_POINT_SMOOTH                   0x0B10
#define GL_POINT_SIZE                     0x0B11
#define GL_POINT_SIZE_RANGE               0x0B12
#define GL_POINT_SIZE_GRANULARITY         0x0B13
#define GL_LINE_SMOOTH                    0x0B20
#define GL_LINE_WIDTH                     0x0B21
#define GL_LINE_WIDTH_RANGE               0x0B22
#define GL_LINE_WIDTH_GRANULARITY         0x0B23
#define GL_LINE_STIPPLE                   0x0B24
#define GL_LINE_STIPPLE_PATTERN           0x0B25
#define GL_LINE_STIPPLE_REPEAT            0x0B26
#define GL_LIST_MODE                      0x0B30
#define GL_MAX_LIST_NESTING               0x0B31
#define GL_LIST_BASE                      0x0B32
#define GL_LIST_INDEX                     0x0B33
#define GL_POLYGON_MODE                   0x0B40
#define GL_POLYGON_SMOOTH                 0x0B41
#define GL_POLYGON_STIPPLE                0x0B42
#define GL_EDGE_FLAG                      0x0B43
#define GL_CULL_FACE                      0x0B44
#define GL_CULL_FACE_MODE                 0x0B45
#define GL_FRONT_FACE                     0x0B46
#define GL_LIGHTING                       0x0B50
#define GL_LIGHT_MODEL_LOCAL_VIEWER       0x0B51
#define GL_LIGHT_MODEL_TWO_SIDE           0x0B52
#define GL_LIGHT_MODEL_AMBIENT            0x0B53
#define GL_SHADE_MODEL                    0x0B54
#define GL_COLOR_MATERIAL_FACE            0x0B55
#define GL_COLOR_MATERIAL_PARAMETER       0x0B56
#define GL_COLOR_MATERIAL                 0x0B57
#define GL_FOG                            0x0B60
#define GL_FOG_INDEX                      0x0B61
#define GL_FOG_DENSITY                    0x0B62
#define GL_FOG_START                      0x0B63
#define GL_FOG_END                        0x0B64
#define GL_FOG_MODE                       0x0B65
#define GL_FOG_COLOR                      0x0B66
#define GL_DEPTH_RANGE                    0x0B70
#define GL_DEPTH_TEST                     0x0B71
#define GL_DEPTH_WRITEMASK                0x0B72
#define GL_DEPTH_CLEAR_VALUE              0x0B73
#define GL_DEPTH_FUNC                     0x0B74
#define GL_ACCUM_CLEAR_VALUE              0x0B80
#define GL_STENCIL_TEST                   0x0B90
#define GL_STENCIL_CLEAR_VALUE            0x0B91
#define GL_STENCIL_FUNC                   0x0B92
#define GL_STENCIL_VALUE_MASK             0x0B93
#define GL_STENCIL_FAIL                   0x0B94
#define GL_STENCIL_PASS_DEPTH_FAIL        0x0B95
#define GL_STENCIL_PASS_DEPTH_PASS        0x0B96
#define GL_STENCIL_REF                    0x0B97
#define GL_STENCIL_WRITEMASK              0x0B98
#define GL_MATRIX_MODE                    0x0BA0
#define GL_NORMALIZE                      0x0BA1
#define GL_VIEWPORT                       0x0BA2
#define GL_MODELVIEW_STACK_DEPTH          0x0BA3
#define GL_PROJECTION_STACK_DEPTH         0x0BA4
#define GL_TEXTURE_STACK_DEPTH            0x0BA5
#define GL_MODELVIEW_MATRIX               0x0BA6
#define GL_PROJECTION_MATRIX              0x0BA7
#define GL_TEXTURE_MATRIX                 0x0BA8
#define GL_ATTRIB_STACK_DEPTH             0x0BB0
#define GL_CLIENT_ATTRIB_STACK_DEPTH      0x0BB1
#define GL_ALPHA_TEST                     0x0BC0
#define GL_ALPHA_TEST_FUNC                0x0BC1
#define GL_ALPHA_TEST_REF                 0x0BC2
#define GL_DITHER                         0x0BD0
#define GL_BLEND_DST                      0x0BE0
#define GL_BLEND_SRC                      0x0BE1
#define GL_BLEND                          0x0BE2
#define GL_LOGIC_OP_MODE                  0x0BF0
#define GL_INDEX_LOGIC_OP                 0x0BF1
#define GL_COLOR_LOGIC_OP                 0x0BF2
#define GL_AUX_BUFFERS                    0x0C00
#define GL_DRAW_BUFFER                    0x0C01
#define GL_READ_BUFFER                    0x0C02
#define GL_SCISSOR_BOX                    0x0C10
#define GL_SCISSOR_TEST                   0x0C11
#define GL_INDEX_CLEAR_VALUE              0x0C20
#define GL_INDEX_WRITEMASK                0x0C21
#define GL_COLOR_CLEAR_VALUE              0x0C22
#define GL_COLOR_WRITEMASK                0x0C23
#define GL_INDEX_MODE                     0x0C30
#define GL_RGBA_MODE                      0x0C31
#define GL_DOUBLEBUFFER                   0x0C32
#define GL_STEREO                         0x0C33
#define GL_RENDER_MODE                    0x0C40
#define GL_PERSPECTIVE_CORRECTION_HINT    0x0C50
#define GL_POINT_SMOOTH_HINT              0x0C51
#define GL_LINE_SMOOTH_HINT               0x0C52
#define GL_POLYGON_SMOOTH_HINT            0x0C53
#define GL_FOG_HINT                       0x0C54
#define GL_TEXTURE_GEN_S                  0x0C60
#define GL_TEXTURE_GEN_T                  0x0C61
#define GL_TEXTURE_GEN_R                  0x0C62
#define GL_TEXTURE_GEN_Q                  0x0C63
#define GL_PIXEL_MAP_I_TO_I               0x0C70
#define GL_PIXEL_MAP_S_TO_S               0x0C71
#define GL_PIXEL_MAP_I_TO_R               0x0C72
#define GL_PIXEL_MAP_I_TO_G               0x0C73
#define GL_PIXEL_MAP_I_TO_B               0x0C74
#define GL_PIXEL_MAP_I_TO_A               0x0C75
#define GL_PIXEL_MAP_R_TO_R               0x0C76
#define GL_PIXEL_MAP_G_TO_G               0x0C77
#define GL_PIXEL_MAP_B_TO_B               0x0C78
#define GL_PIXEL_MAP_A_TO_A               0x0C79
#define GL_PIXEL_MAP_I_TO_I_SIZE          0x0CB0
#define GL_PIXEL_MAP_S_TO_S_SIZE          0x0CB1
#define GL_PIXEL_MAP_I_TO_R_SIZE          0x0CB2
#define GL_PIXEL_MAP_I_TO_G_SIZE          0x0CB3
#define GL_PIXEL_MAP_I_TO_B_SIZE          0x0CB4
#define GL_PIXEL_MAP_I_TO_A_SIZE          0x0CB5
#define GL_PIXEL_MAP_R_TO_R_SIZE          0x0CB6
#define GL_PIXEL_MAP_G_TO_G_SIZE          0x0CB7
#define GL_PIXEL_MAP_B_TO_B_SIZE          0x0CB8
#define GL_PIXEL_MAP_A_TO_A_SIZE          0x0CB9
#define GL_UNPACK_SWAP_BYTES              0x0CF0
#define GL_UNPACK_LSB_FIRST               0x0CF1
#define GL_UNPACK_ROW_LENGTH              0x0CF2
#define GL_UNPACK_SKIP_ROWS               0x0CF3
#define GL_UNPACK_SKIP_PIXELS             0x0CF4
#define GL_UNPACK_ALIGNMENT               0x0CF5
#define GL_PACK_SWAP_BYTES                0x0D00
#define GL_PACK_LSB_FIRST                 0x0D01
#define GL_PACK_ROW_LENGTH                0x0D02
#define GL_PACK_SKIP_ROWS                 0x0D03
#define GL_PACK_SKIP_PIXELS               0x0D04
#define GL_PACK_ALIGNMENT                 0x0D05
#define GL_MAP_COLOR                      0x0D10
#define GL_MAP_STENCIL                    0x0D11
#define GL_INDEX_SHIFT                    0x0D12
#define GL_INDEX_OFFSET                   0x0D13
#define GL_RED_SCALE                      0x0D14
#define GL_RED_BIAS                       0x0D15
#define GL_ZOOM_X                         0x0D16
#define GL_ZOOM_Y                         0x0D17
#define GL_GREEN_SCALE                    0x0D18
#define GL_GREEN_BIAS                     0x0D19
#define GL_BLUE_SCALE                     0x0D1A
#define GL_BLUE_BIAS                      0x0D1B
#define GL_ALPHA_SCALE                    0x0D1C
#define GL_ALPHA_BIAS                     0x0D1D
#define GL_DEPTH_SCALE                    0x0D1E
#define GL_DEPTH_BIAS                     0x0D1F
#define GL_MAX_EVAL_ORDER                 0x0D30
#define GL_MAX_LIGHTS                     0x0D31
#define GL_MAX_CLIP_PLANES                0x0D32
#define GL_MAX_TEXTURE_SIZE               0x0D33
#define GL_MAX_PIXEL_MAP_TABLE            0x0D34
#define GL_MAX_ATTRIB_STACK_DEPTH         0x0D35
#define GL_MAX_MODELVIEW_STACK_DEPTH      0x0D36
#define GL_MAX_NAME_STACK_DEPTH           0x0D37
#define GL_MAX_PROJECTION_STACK_DEPTH     0x0D38
#define GL_MAX_TEXTURE_STACK_DEPTH        0x0D39
#define GL_MAX_VIEWPORT_DIMS              0x0D3A
#define GL_MAX_CLIENT_ATTRIB_STACK_DEPTH  0x0D3B
#define GL_SUBPIXEL_BITS                  0x0D50
#define GL_INDEX_BITS                     0x0D51
#define GL_RED_BITS                       0x0D52
#define GL_GREEN_BITS                     0x0D53
#define GL_BLUE_BITS                      0x0D54
#define GL_ALPHA_BITS                     0x0D55
#define GL_DEPTH_BITS                     0x0D56
#define GL_STENCIL_BITS                   0x0D57
#define GL_ACCUM_RED_BITS                 0x0D58
#define GL_ACCUM_GREEN_BITS               0x0D59
#define GL_ACCUM_BLUE_BITS                0x0D5A
#define GL_ACCUM_ALPHA_BITS               0x0D5B
#define GL_NAME_STACK_DEPTH               0x0D70
#define GL_AUTO_NORMAL                    0x0D80
#define GL_MAP1_COLOR_4                   0x0D90
#define GL_MAP1_INDEX                     0x0D91
#define GL_MAP1_NORMAL                    0x0D92
#define GL_MAP1_TEXTURE_COORD_1           0x0D93
#define GL_MAP1_TEXTURE_COORD_2           0x0D94
#define GL_MAP1_TEXTURE_COORD_3           0x0D95
#define GL_MAP1_TEXTURE_COORD_4           0x0D96
#define GL_MAP1_VERTEX_3                  0x0D97
#define GL_MAP1_VERTEX_4                  0x0D98
#define GL_MAP2_COLOR_4                   0x0DB0
#define GL_MAP2_INDEX                     0x0DB1
#define GL_MAP2_NORMAL                    0x0DB2
#define GL_MAP2_TEXTURE_COORD_1           0x0DB3
#define GL_MAP2_TEXTURE_COORD_2           0x0DB4
#define GL_MAP2_TEXTURE_COORD_3           0x0DB5
#define GL_MAP2_TEXTURE_COORD_4           0x0DB6
#define GL_MAP2_VERTEX_3                  0x0DB7
#define GL_MAP2_VERTEX_4                  0x0DB8
#define GL_MAP1_GRID_DOMAIN               0x0DD0
#define GL_MAP1_GRID_SEGMENTS             0x0DD1
#define GL_MAP2_GRID_DOMAIN               0x0DD2
#define GL_MAP2_GRID_SEGMENTS             0x0DD3
#define GL_TEXTURE_1D                     0x0DE0
#define GL_TEXTURE_2D                     0x0DE1
#define GL_FEEDBACK_BUFFER_POINTER        0x0DF0
#define GL_FEEDBACK_BUFFER_SIZE           0x0DF1
#define GL_FEEDBACK_BUFFER_TYPE           0x0DF2
#define GL_SELECTION_BUFFER_POINTER       0x0DF3
#define GL_SELECTION_BUFFER_SIZE          0x0DF4
#define GL_TEXTURE_WIDTH                  0x1000
#define GL_TEXTURE_HEIGHT                 0x1001
#define GL_TEXTURE_INTERNAL_FORMAT        0x1003
#define GL_TEXTURE_BORDER_COLOR           0x1004
#define GL_TEXTURE_BORDER                 0x1005
#define GL_DONT_CARE                      0x1100
#define GL_FASTEST                        0x1101
#define GL_NICEST                         0x1102
#define GL_LIGHT0                         0x4000
#define GL_LIGHT1                         0x4001
#define GL_LIGHT2                         0x4002
#define GL_LIGHT3                         0x4003
#define GL_LIGHT4                         0x4004
#define GL_LIGHT5                         0x4005
#define GL_LIGHT6                         0x4006
#define GL_LIGHT7                         0x4007
#define GL_AMBIENT                        0x1200
#define GL_DIFFUSE                        0x1201
#define GL_SPECULAR                       0x1202
#define GL_POSITION                       0x1203
#define GL_SPOT_DIRECTION                 0x1204
#define GL_SPOT_EXPONENT                  0x1205
#define GL_SPOT_CUTOFF                    0x1206
#define GL_CONSTANT_ATTENUATION           0x1207
#define GL_LINEAR_ATTENUATION             0x1208
#define GL_QUADRATIC_ATTENUATION          0x1209
#define GL_COMPILE                        0x1300
#define GL_COMPILE_AND_EXECUTE            0x1301
#define GL_CLEAR                          0x1500
#define GL_AND                            0x1501
#define GL_AND_REVERSE                    0x1502
#define GL_COPY                           0x1503
#define GL_AND_INVERTED                   0x1504
#define GL_NOOP                           0x1505
#define GL_XOR                            0x1506
#define GL_OR                             0x1507
#define GL_NOR                            0x1508
#define GL_EQUIV                          0x1509
#define GL_INVERT                         0x150A
#define GL_OR_REVERSE                     0x150B
#define GL_COPY_INVERTED                  0x150C
#define GL_OR_INVERTED                    0x150D
#define GL_NAND                           0x150E
#define GL_SET                            0x150F
#define GL_EMISSION                       0x1600
#define GL_SHININESS                      0x1601
#define GL_AMBIENT_AND_DIFFUSE            0x1602
#define GL_COLOR_INDEXES                  0x1603
#define GL_MODELVIEW                      0x1700
#define GL_PROJECTION                     0x1701
#define GL_TEXTURE                        0x1702
#define GL_COLOR                          0x1800
#define GL_DEPTH                          0x1801
#define GL_STENCIL                        0x1802
#define GL_COLOR_INDEX                    0x1900
#define GL_STENCIL_INDEX                  0x1901
#define GL_DEPTH_COMPONENT                0x1902
#define GL_RED                            0x1903
#define GL_GREEN                          0x1904
#define GL_BLUE                           0x1905
#define GL_ALPHA                          0x1906
#define GL_RGB                            0x1907
#define GL_RGBA                           0x1908
#define GL_LUMINANCE                      0x1909
#define GL_LUMINANCE_ALPHA                0x190A
#define GL_BITMAP                         0x1A00
#define GL_POINT                          0x1B00
#define GL_LINE                           0x1B01
#define GL_FILL                           0x1B02
#define GL_RENDER                         0x1C00
#define GL_FEEDBACK                       0x1C01
#define GL_SELECT                         0x1C02
#define GL_FLAT                           0x1D00
#define GL_SMOOTH                         0x1D01
#define GL_KEEP                           0x1E00
#define GL_REPLACE                        0x1E01
#define GL_INCR                           0x1E02
#define GL_DECR                           0x1E03
#define GL_VENDOR                         0x1F00
#define GL_RENDERER                       0x1F01
#define GL_VERSION                        0x1F02
#define GL_EXTENSIONS                     0x1F03
#define GL_S                              0x2000
#define GL_T                              0x2001
#define GL_R                              0x2002
#define GL_Q                              0x2003
#define GL_MODULATE                       0x2100
#define GL_DECAL                          0x2101
#define GL_TEXTURE_ENV_MODE               0x2200
#define GL_TEXTURE_ENV_COLOR              0x2201
#define GL_TEXTURE_ENV                    0x2300
#define GL_EYE_LINEAR                     0x2400
#define GL_OBJECT_LINEAR                  0x2401
#define GL_SPHERE_MAP                     0x2402
#define GL_TEXTURE_GEN_MODE               0x2500
#define GL_OBJECT_PLANE                   0x2501
#define GL_EYE_PLANE                      0x2502
#define GL_NEAREST                        0x2600
#define GL_LINEAR                         0x2601
#define GL_NEAREST_MIPMAP_NEAREST         0x2700
#define GL_LINEAR_MIPMAP_NEAREST          0x2701
#define GL_NEAREST_MIPMAP_LINEAR          0x2702
#define GL_LINEAR_MIPMAP_LINEAR           0x2703
#define GL_TEXTURE_MAG_FILTER             0x2800
#define GL_TEXTURE_MIN_FILTER             0x2801
#define GL_TEXTURE_WRAP_S                 0x2802
#define GL_TEXTURE_WRAP_T                 0x2803
#define GL_CLAMP                          0x2900
#define GL_REPEAT                         0x2901
#define GL_CLIENT_PIXEL_STORE_BIT         0x00000001
#define GL_CLIENT_VERTEX_ARRAY_BIT        0x00000002
#define GL_CLIENT_ALL_ATTRIB_BITS         0xffffffff
#define GL_POLYGON_OFFSET_FACTOR          0x8038
#define GL_POLYGON_OFFSET_UNITS           0x2A00
#define GL_POLYGON_OFFSET_POINT           0x2A01
#define GL_POLYGON_OFFSET_LINE            0x2A02
#define GL_POLYGON_OFFSET_FILL            0x8037
#define GL_ALPHA4                         0x803B
#define GL_ALPHA8                         0x803C
#define GL_ALPHA12                        0x803D
#define GL_ALPHA16                        0x803E
#define GL_LUMINANCE4                     0x803F
#define GL_LUMINANCE8                     0x8040
#define GL_LUMINANCE12                    0x8041
#define GL_LUMINANCE16                    0x8042
#define GL_LUMINANCE4_ALPHA4              0x8043
#define GL_LUMINANCE6_ALPHA2              0x8044
#define GL_LUMINANCE8_ALPHA8              0x8045
#define GL_LUMINANCE12_ALPHA4             0x8046
#define GL_LUMINANCE12_ALPHA12            0x8047
#define GL_LUMINANCE16_ALPHA16            0x8048
#define GL_INTENSITY                      0x8049
#define GL_INTENSITY4                     0x804A
#define GL_INTENSITY8                     0x804B
#define GL_INTENSITY12                    0x804C
#define GL_INTENSITY16                    0x804D
#define GL_R3_G3_B2                       0x2A10
#define GL_RGB4                           0x804F
#define GL_RGB5                           0x8050
#define GL_RGB8                           0x8051
#define GL_RGB10                          0x8052
#define GL_RGB12                          0x8053
#define GL_RGB16                          0x8054
#define GL_RGBA2                          0x8055
#define GL_RGBA4                          0x8056
#define GL_RGB5_A1                        0x8057
#define GL_RGBA8                          0x8058
#define GL_RGB10_A2                       0x8059
#define GL_RGBA12                         0x805A
#define GL_RGBA16                         0x805B
#define GL_TEXTURE_RED_SIZE               0x805C
#define GL_TEXTURE_GREEN_SIZE             0x805D
#define GL_TEXTURE_BLUE_SIZE              0x805E
#define GL_TEXTURE_ALPHA_SIZE             0x805F
#define GL_TEXTURE_LUMINANCE_SIZE         0x8060
#define GL_TEXTURE_INTENSITY_SIZE         0x8061
#define GL_PROXY_TEXTURE_1D               0x8063
#define GL_PROXY_TEXTURE_2D               0x8064
#define GL_TEXTURE_PRIORITY               0x8066
#define GL_TEXTURE_RESIDENT               0x8067
#define GL_TEXTURE_BINDING_1D             0x8068
#define GL_TEXTURE_BINDING_2D             0x8069
#define GL_VERTEX_ARRAY                   0x8074
#define GL_NORMAL_ARRAY                   0x8075
#define GL_COLOR_ARRAY                    0x8076
#define GL_INDEX_ARRAY                    0x8077
#define GL_TEXTURE_COORD_ARRAY            0x8078
#define GL_EDGE_FLAG_ARRAY                0x8079
#define GL_VERTEX_ARRAY_SIZE              0x807A
#define GL_VERTEX_ARRAY_TYPE              0x807B
#define GL_VERTEX_ARRAY_STRIDE            0x807C
#define GL_NORMAL_ARRAY_TYPE              0x807E
#define GL_NORMAL_ARRAY_STRIDE            0x807F
#define GL_COLOR_ARRAY_SIZE               0x8081
#define GL_COLOR_ARRAY_TYPE               0x8082
#define GL_COLOR_ARRAY_STRIDE             0x8083
#define GL_INDEX_ARRAY_TYPE               0x8085
#define GL_INDEX_ARRAY_STRIDE             0x8086
#define GL_TEXTURE_COORD_ARRAY_SIZE       0x8088
#define GL_TEXTURE_COORD_ARRAY_TYPE       0x8089
#define GL_TEXTURE_COORD_ARRAY_STRIDE     0x808A
#define GL_EDGE_FLAG_ARRAY_STRIDE         0x808C
#define GL_VERTEX_ARRAY_POINTER           0x808E
#define GL_NORMAL_ARRAY_POINTER           0x808F
#define GL_COLOR_ARRAY_POINTER            0x8090
#define GL_INDEX_ARRAY_POINTER            0x8091
#define GL_TEXTURE_COORD_ARRAY_POINTER    0x8092
#define GL_EDGE_FLAG_ARRAY_POINTER        0x8093
#define GL_V2F                            0x2A20
#define GL_V3F                            0x2A21
#define GL_C4UB_V2F                       0x2A22
#define GL_C4UB_V3F                       0x2A23
#define GL_C3F_V3F                        0x2A24
#define GL_N3F_V3F                        0x2A25
#define GL_C4F_N3F_V3F                    0x2A26
#define GL_T2F_V3F                        0x2A27
#define GL_T4F_V4F                        0x2A28
#define GL_T2F_C4UB_V3F                   0x2A29
#define GL_T2F_C3F_V3F                    0x2A2A
#define GL_T2F_N3F_V3F                    0x2A2B
#define GL_T2F_C4F_N3F_V3F                0x2A2C
#define GL_T4F_C4F_N3F_V4F                0x2A2D
#endif</t>
<t tx="ekr.20060513122613.7" xcc_child_cfg="7d7100580b000000427265616b506f696e747371017d7102732e">#ifndef GL_DEFS
GL_PROC(void,glAccum,(GLenum op, GLfloat value))
GL_PROC(void,glAlphaFunc,(GLenum func, GLclampf ref))
GL_PROC(GLboolean,glAreTexturesResident,(GLsizei n, const GLuint *textures, GLboolean *residences))
GL_PROC(void,glArrayElement,(GLint i))
GL_PROC(void,glBegin,(GLenum mode))
GL_PROC(void,glBindTexture,(GLenum target, GLuint texture))
GL_PROC(void,glBitmap,(GLsizei width, GLsizei height, GLfloat xorig, GLfloat yorig, GLfloat xmove, GLfloat ymove, const GLubyte *bitmap))
GL_PROC(void,glBlendFunc,(GLenum sfactor, GLenum dfactor))
GL_PROC(void,glCallList,(GLuint list))
GL_PROC(void,glCallLists,(GLsizei n, GLenum type, const GLvoid *lists))
GL_PROC(void,glClear,(GLbitfield mask))
GL_PROC(void,glClearAccum,(GLfloat red, GLfloat green, GLfloat blue, GLfloat alpha))
GL_PROC(void,glClearColor,(GLclampf red, GLclampf green, GLclampf blue, GLclampf alpha))
GL_PROC(void,glClearDepth,(GLclampd depth))
GL_PROC(void,glClearIndex,(GLfloat c))
GL_PROC(void,glClearStencil,(GLint s))
GL_PROC(void,glClipPlane,(GLenum plane, const GLdouble *equation))
GL_PROC(void,glColor3b,(GLbyte red, GLbyte green, GLbyte blue))
GL_PROC(void,glColor3bv,(const GLbyte *v))
GL_PROC(void,glColor3d,(GLdouble red, GLdouble green, GLdouble blue))
GL_PROC(void,glColor3dv,(const GLdouble *v))
GL_PROC(void,glColor3f,(GLfloat red, GLfloat green, GLfloat blue))
GL_PROC(void,glColor3fv,(const GLfloat *v))
GL_PROC(void,glColor3i,(GLint red, GLint green, GLint blue))
GL_PROC(void,glColor3iv,(const GLint *v))
GL_PROC(void,glColor3s,(GLshort red, GLshort green, GLshort blue))
GL_PROC(void,glColor3sv,(const GLshort *v))
GL_PROC(void,glColor3ub,(GLubyte red, GLubyte green, GLubyte blue))
GL_PROC(void,glColor3ubv,(const GLubyte *v))
GL_PROC(void,glColor3ui,(GLuint red, GLuint green, GLuint blue))
GL_PROC(void,glColor3uiv,(const GLuint *v))
GL_PROC(void,glColor3us,(GLushort red, GLushort green, GLushort blue))
GL_PROC(void,glColor3usv,(const GLushort *v))
GL_PROC(void,glColor4b,(GLbyte red, GLbyte green, GLbyte blue, GLbyte alpha))
GL_PROC(void,glColor4bv,(const GLbyte *v))
GL_PROC(void,glColor4d,(GLdouble red, GLdouble green, GLdouble blue, GLdouble alpha))
GL_PROC(void,glColor4dv,(const GLdouble *v))
GL_PROC(void,glColor4f,(GLfloat red, GLfloat green, GLfloat blue, GLfloat alpha))
GL_PROC(void,glColor4fv,(const GLfloat *v))
GL_PROC(void,glColor4i,(GLint red, GLint green, GLint blue, GLint alpha))
GL_PROC(void,glColor4iv,(const GLint *v))
GL_PROC(void,glColor4s,(GLshort red, GLshort green, GLshort blue, GLshort alpha))
GL_PROC(void,glColor4sv,(const GLshort *v))
GL_PROC(void,glColor4ub,(GLubyte red, GLubyte green, GLubyte blue, GLubyte alpha))
GL_PROC(void,glColor4ubv,(const GLubyte *v))
GL_PROC(void,glColor4ui,(GLuint red, GLuint green, GLuint blue, GLuint alpha))
GL_PROC(void,glColor4uiv,(const GLuint *v))
GL_PROC(void,glColor4us,(GLushort red, GLushort green, GLushort blue, GLushort alpha))
GL_PROC(void,glColor4usv,(const GLushort *v))
GL_PROC(void,glColorMask,(GLboolean red, GLboolean green, GLboolean blue, GLboolean alpha))
GL_PROC(void,glColorMaterial,(GLenum face, GLenum mode))
GL_PROC(void,glColorPointer,(GLint size, GLenum type, GLsizei stride, const GLvoid *pointer))
GL_PROC(void,glCopyPixels,(GLint x, GLint y, GLsizei width, GLsizei height, GLenum type))
GL_PROC(void,glCopyTexImage1D,(GLenum target, GLint level, GLenum internalFormat, GLint x, GLint y, GLsizei width, GLint border))
GL_PROC(void,glCopyTexImage2D,(GLenum target, GLint level, GLenum internalFormat, GLint x, GLint y, GLsizei width, GLsizei height, GLint border))
GL_PROC(void,glCopyTexSubImage1D,(GLenum target, GLint level, GLint xoffset, GLint x, GLint y, GLsizei width))
GL_PROC(void,glCopyTexSubImage2D,(GLenum target, GLint level, GLint xoffset, GLint yoffset, GLint x, GLint y, GLsizei width, GLsizei height))
GL_PROC(void,glCullFace,(GLenum mode))
GL_PROC(void,glDeleteLists,(GLuint list, GLsizei range))
GL_PROC(void,glDeleteTextures,(GLsizei n, const GLuint *textures))
GL_PROC(void,glDepthFunc,(GLenum func))
GL_PROC(void,glDepthMask,(GLboolean flag))
GL_PROC(void,glDepthRange,(GLclampd zNear, GLclampd zFar))
GL_PROC(void,glDisable,(GLenum cap))
GL_PROC(void,glDisableClientState,(GLenum array))
GL_PROC(void,glDrawArrays,(GLenum mode, GLint first, GLsizei count))
GL_PROC(void,glDrawBuffer,(GLenum mode))
GL_PROC(void,glDrawElements,(GLenum mode, GLsizei count, GLenum type, const GLvoid *indices))
GL_PROC(void,glDrawPixels,(GLsizei width, GLsizei height, GLenum format, GLenum type, const GLvoid *pixels))
GL_PROC(void,glEdgeFlag,(GLboolean flag))
GL_PROC(void,glEdgeFlagPointer,(GLsizei stride, const GLvoid *pointer))
GL_PROC(void,glEdgeFlagv,(const GLboolean *flag))
GL_PROC(void,glEnable,(GLenum cap))
GL_PROC(void,glEnableClientState,(GLenum array))
GL_PROC(void,glEnd,(void))
GL_PROC(void,glEndList,(void))
GL_PROC(void,glEvalCoord1d,(GLdouble u))
GL_PROC(void,glEvalCoord1dv,(const GLdouble *u))
GL_PROC(void,glEvalCoord1f,(GLfloat u))
GL_PROC(void,glEvalCoord1fv,(const GLfloat *u))
GL_PROC(void,glEvalCoord2d,(GLdouble u, GLdouble v))
GL_PROC(void,glEvalCoord2dv,(const GLdouble *u))
GL_PROC(void,glEvalCoord2f,(GLfloat u, GLfloat v))
GL_PROC(void,glEvalCoord2fv,(const GLfloat *u))
GL_PROC(void,glEvalMesh1,(GLenum mode, GLint i1, GLint i2))
GL_PROC(void,glEvalMesh2,(GLenum mode, GLint i1, GLint i2, GLint j1, GLint j2))
GL_PROC(void,glEvalPoint1,(GLint i))
GL_PROC(void,glEvalPoint2,(GLint i, GLint j))
GL_PROC(void,glFeedbackBuffer,(GLsizei size, GLenum type, GLfloat *buffer))
GL_PROC(void,glFinish,(void))
GL_PROC(void,glFlush,(void))
GL_PROC(void,glFogf,(GLenum pname, GLfloat param))
GL_PROC(void,glFogfv,(GLenum pname, const GLfloat *params))
GL_PROC(void,glFogi,(GLenum pname, GLint param))
GL_PROC(void,glFogiv,(GLenum pname, const GLint *params))
GL_PROC(void,glFrontFace,(GLenum mode))
GL_PROC(void,glFrustum,(GLdouble left, GLdouble right, GLdouble bottom, GLdouble top, GLdouble zNear, GLdouble zFar))
GL_PROC(GLuint,glGenLists,(GLsizei range))
GL_PROC(void,glGenTextures,(GLsizei n, GLuint *textures))
GL_PROC(void,glGetBooleanv,(GLenum pname, GLboolean *params))
GL_PROC(void,glGetClipPlane,(GLenum plane, GLdouble *equation))
GL_PROC(void,glGetDoublev,(GLenum pname, GLdouble *params))
GL_PROC(GLenum,glGetError,(void))
GL_PROC(void,glGetFloatv,(GLenum pname, GLfloat *params))
GL_PROC(void,glGetIntegerv,(GLenum pname, GLint *params))
GL_PROC(void,glGetLightfv,(GLenum light, GLenum pname, GLfloat *params))
GL_PROC(void,glGetLightiv,(GLenum light, GLenum pname, GLint *params))
GL_PROC(void,glGetMapdv,(GLenum target, GLenum query, GLdouble *v))
GL_PROC(void,glGetMapfv,(GLenum target, GLenum query, GLfloat *v))
GL_PROC(void,glGetMapiv,(GLenum target, GLenum query, GLint *v))
GL_PROC(void,glGetMaterialfv,(GLenum face, GLenum pname, GLfloat *params))
GL_PROC(void,glGetMaterialiv,(GLenum face, GLenum pname, GLint *params))
GL_PROC(void,glGetPixelMapfv,(GLenum map, GLfloat *values))
GL_PROC(void,glGetPixelMapuiv,(GLenum map, GLuint *values))
GL_PROC(void,glGetPixelMapusv,(GLenum map, GLushort *values))
GL_PROC(void,glGetPointerv,(GLenum pname, GLvoid* *params))
GL_PROC(void,glGetPolygonStipple,(GLubyte *mask))
GL_PROC(const GLubyte *,glGetString,(GLenum name))
GL_PROC(void,glGetTexEnvfv,(GLenum target, GLenum pname, GLfloat *params))
GL_PROC(void,glGetTexEnviv,(GLenum target, GLenum pname, GLint *params))
GL_PROC(void,glGetTexGendv,(GLenum coord, GLenum pname, GLdouble *params))
GL_PROC(void,glGetTexGenfv,(GLenum coord, GLenum pname, GLfloat *params))
GL_PROC(void,glGetTexGeniv,(GLenum coord, GLenum pname, GLint *params))
GL_PROC(void,glGetTexImage,(GLenum target, GLint level, GLenum format, GLenum type, GLvoid *pixels))
GL_PROC(void,glGetTexLevelParameterfv,(GLenum target, GLint level, GLenum pname, GLfloat *params))
GL_PROC(void,glGetTexLevelParameteriv,(GLenum target, GLint level, GLenum pname, GLint *params))
GL_PROC(void,glGetTexParameterfv,(GLenum target, GLenum pname, GLfloat *params))
GL_PROC(void,glGetTexParameteriv,(GLenum target, GLenum pname, GLint *params))
GL_PROC(void,glHint,(GLenum target, GLenum mode))
GL_PROC(void,glIndexMask,(GLuint mask))
GL_PROC(void,glIndexPointer,(GLenum type, GLsizei stride, const GLvoid *pointer))
GL_PROC(void,glIndexd,(GLdouble c))
GL_PROC(void,glIndexdv,(const GLdouble *c))
GL_PROC(void,glIndexf,(GLfloat c))
GL_PROC(void,glIndexfv,(const GLfloat *c))
GL_PROC(void,glIndexi,(GLint c))
GL_PROC(void,glIndexiv,(const GLint *c))
GL_PROC(void,glIndexs,(GLshort c))
GL_PROC(void,glIndexsv,(const GLshort *c))
GL_PROC(void,glIndexub,(GLubyte c))
GL_PROC(void,glIndexubv,(const GLubyte *c))
GL_PROC(void,glInitNames,(void))
GL_PROC(void,glInterleavedArrays,(GLenum format, GLsizei stride, const GLvoid *pointer))
GL_PROC(GLboolean,glIsEnabled,(GLenum cap))
GL_PROC(GLboolean,glIsList,(GLuint list))
GL_PROC(GLboolean,glIsTexture,(GLuint texture))
GL_PROC(void,glLightModelf,(GLenum pname, GLfloat param))
GL_PROC(void,glLightModelfv,(GLenum pname, const GLfloat *params))
GL_PROC(void,glLightModeli,(GLenum pname, GLint param))
GL_PROC(void,glLightModeliv,(GLenum pname, const GLint *params))
GL_PROC(void,glLightf,(GLenum light, GLenum pname, GLfloat param))
GL_PROC(void,glLightfv,(GLenum light, GLenum pname, const GLfloat *params))
GL_PROC(void,glLighti,(GLenum light, GLenum pname, GLint param))
GL_PROC(void,glLightiv,(GLenum light, GLenum pname, const GLint *params))
GL_PROC(void,glLineStipple,(GLint factor, GLushort pattern))
GL_PROC(void,glLineWidth,(GLfloat width))
GL_PROC(void,glListBase,(GLuint base))
GL_PROC(void,glLoadIdentity,(void))
GL_PROC(void,glLoadMatrixd,(const GLdouble *m))
GL_PROC(void,glLoadMatrixf,(const GLfloat *m))
GL_PROC(void,glLoadName,(GLuint name))
GL_PROC(void,glLogicOp,(GLenum opcode))
GL_PROC(void,glMap1d,(GLenum target, GLdouble u1, GLdouble u2, GLint stride, GLint order, const GLdouble *points))
GL_PROC(void,glMap1f,(GLenum target, GLfloat u1, GLfloat u2, GLint stride, GLint order, const GLfloat *points))
GL_PROC(void,glMap2d,(GLenum target, GLdouble u1, GLdouble u2, GLint ustride, GLint uorder, GLdouble v1, GLdouble v2, GLint vstride, GLint vorder, const GLdouble *points))
GL_PROC(void,glMap2f,(GLenum target, GLfloat u1, GLfloat u2, GLint ustride, GLint uorder, GLfloat v1, GLfloat v2, GLint vstride, GLint vorder, const GLfloat *points))
GL_PROC(void,glMapGrid1d,(GLint un, GLdouble u1, GLdouble u2))
GL_PROC(void,glMapGrid1f,(GLint un, GLfloat u1, GLfloat u2))
GL_PROC(void,glMapGrid2d,(GLint un, GLdouble u1, GLdouble u2, GLint vn, GLdouble v1, GLdouble v2))
GL_PROC(void,glMapGrid2f,(GLint un, GLfloat u1, GLfloat u2, GLint vn, GLfloat v1, GLfloat v2))
GL_PROC(void,glMaterialf,(GLenum face, GLenum pname, GLfloat param))
GL_PROC(void,glMaterialfv,(GLenum face, GLenum pname, const GLfloat *params))
GL_PROC(void,glMateriali,(GLenum face, GLenum pname, GLint param))
GL_PROC(void,glMaterialiv,(GLenum face, GLenum pname, const GLint *params))
GL_PROC(void,glMatrixMode,(GLenum mode))
GL_PROC(void,glMultMatrixd,(const GLdouble *m))
GL_PROC(void,glMultMatrixf,(const GLfloat *m))
GL_PROC(void,glNewList,(GLuint list, GLenum mode))
GL_PROC(void,glNormal3b,(GLbyte nx, GLbyte ny, GLbyte nz))
GL_PROC(void,glNormal3bv,(const GLbyte *v))
GL_PROC(void,glNormal3d,(GLdouble nx, GLdouble ny, GLdouble nz))
GL_PROC(void,glNormal3dv,(const GLdouble *v))
GL_PROC(void,glNormal3f,(GLfloat nx, GLfloat ny, GLfloat nz))
GL_PROC(void,glNormal3fv,(const GLfloat *v))
GL_PROC(void,glNormal3i,(GLint nx, GLint ny, GLint nz))
GL_PROC(void,glNormal3iv,(const GLint *v))
GL_PROC(void,glNormal3s,(GLshort nx, GLshort ny, GLshort nz))
GL_PROC(void,glNormal3sv,(const GLshort *v))
GL_PROC(void,glNormalPointer,(GLenum type, GLsizei stride, const GLvoid *pointer))
GL_PROC(void,glOrtho,(GLdouble left, GLdouble right, GLdouble bottom, GLdouble top, GLdouble zNear, GLdouble zFar))
GL_PROC(void,glPassThrough,(GLfloat token))
GL_PROC(void,glPixelMapfv,(GLenum map, GLsizei mapsize, const GLfloat *values))
GL_PROC(void,glPixelMapuiv,(GLenum map, GLsizei mapsize, const GLuint *values))
GL_PROC(void,glPixelMapusv,(GLenum map, GLsizei mapsize, const GLushort *values))
GL_PROC(void,glPixelStoref,(GLenum pname, GLfloat param))
GL_PROC(void,glPixelStorei,(GLenum pname, GLint param))
GL_PROC(void,glPixelTransferf,(GLenum pname, GLfloat param))
GL_PROC(void,glPixelTransferi,(GLenum pname, GLint param))
GL_PROC(void,glPixelZoom,(GLfloat xfactor, GLfloat yfactor))
GL_PROC(void,glPointSize,(GLfloat size))
GL_PROC(void,glPolygonMode,(GLenum face, GLenum mode))
GL_PROC(void,glPolygonOffset,(GLfloat factor, GLfloat units))
GL_PROC(void,glPolygonStipple,(const GLubyte *mask))
GL_PROC(void,glPopAttrib,(void))
GL_PROC(void,glPopClientAttrib,(void))
GL_PROC(void,glPopMatrix,(void))
GL_PROC(void,glPopName,(void))
GL_PROC(void,glPrioritizeTextures,(GLsizei n, const GLuint *textures, const GLclampf *priorities))
GL_PROC(void,glPushAttrib,(GLbitfield mask))
GL_PROC(void,glPushClientAttrib,(GLbitfield mask))
GL_PROC(void,glPushMatrix,(void))
GL_PROC(void,glPushName,(GLuint name))
GL_PROC(void,glRasterPos2d,(GLdouble x, GLdouble y))
GL_PROC(void,glRasterPos2dv,(const GLdouble *v))
GL_PROC(void,glRasterPos2f,(GLfloat x, GLfloat y))
GL_PROC(void,glRasterPos2fv,(const GLfloat *v))
GL_PROC(void,glRasterPos2i,(GLint x, GLint y))
GL_PROC(void,glRasterPos2iv,(const GLint *v))
GL_PROC(void,glRasterPos2s,(GLshort x, GLshort y))
GL_PROC(void,glRasterPos2sv,(const GLshort *v))
GL_PROC(void,glRasterPos3d,(GLdouble x, GLdouble y, GLdouble z))
GL_PROC(void,glRasterPos3dv,(const GLdouble *v))
GL_PROC(void,glRasterPos3f,(GLfloat x, GLfloat y, GLfloat z))
GL_PROC(void,glRasterPos3fv,(const GLfloat *v))
GL_PROC(void,glRasterPos3i,(GLint x, GLint y, GLint z))
GL_PROC(void,glRasterPos3iv,(const GLint *v))
GL_PROC(void,glRasterPos3s,(GLshort x, GLshort y, GLshort z))
GL_PROC(void,glRasterPos3sv,(const GLshort *v))
GL_PROC(void,glRasterPos4d,(GLdouble x, GLdouble y, GLdouble z, GLdouble w))
GL_PROC(void,glRasterPos4dv,(const GLdouble *v))
GL_PROC(void,glRasterPos4f,(GLfloat x, GLfloat y, GLfloat z, GLfloat w))
GL_PROC(void,glRasterPos4fv,(const GLfloat *v))
GL_PROC(void,glRasterPos4i,(GLint x, GLint y, GLint z, GLint w))
GL_PROC(void,glRasterPos4iv,(const GLint *v))
GL_PROC(void,glRasterPos4s,(GLshort x, GLshort y, GLshort z, GLshort w))
GL_PROC(void,glRasterPos4sv,(const GLshort *v))
GL_PROC(void,glReadBuffer,(GLenum mode))
GL_PROC(void,glReadPixels,(GLint x, GLint y, GLsizei width, GLsizei height, GLenum format, GLenum type, GLvoid *pixels))
GL_PROC(void,glRectd,(GLdouble x1, GLdouble y1, GLdouble x2, GLdouble y2))
GL_PROC(void,glRectdv,(const GLdouble *v1, const GLdouble *v2))
GL_PROC(void,glRectf,(GLfloat x1, GLfloat y1, GLfloat x2, GLfloat y2))
GL_PROC(void,glRectfv,(const GLfloat *v1, const GLfloat *v2))
GL_PROC(void,glRecti,(GLint x1, GLint y1, GLint x2, GLint y2))
GL_PROC(void,glRectiv,(const GLint *v1, const GLint *v2))
GL_PROC(void,glRects,(GLshort x1, GLshort y1, GLshort x2, GLshort y2))
GL_PROC(void,glRectsv,(const GLshort *v1, const GLshort *v2))
GL_PROC(GLint,glRenderMode,(GLenum mode))
GL_PROC(void,glRotated,(GLdouble angle, GLdouble x, GLdouble y, GLdouble z))
GL_PROC(void,glRotatef,(GLfloat angle, GLfloat x, GLfloat y, GLfloat z))
GL_PROC(void,glScaled,(GLdouble x, GLdouble y, GLdouble z))
GL_PROC(void,glScalef,(GLfloat x, GLfloat y, GLfloat z))
GL_PROC(void,glScissor,(GLint x, GLint y, GLsizei width, GLsizei height))
GL_PROC(void,glSelectBuffer,(GLsizei size, GLuint *buffer))
GL_PROC(void,glShadeModel,(GLenum mode))
GL_PROC(void,glStencilFunc,(GLenum func, GLint ref, GLuint mask))
GL_PROC(void,glStencilMask,(GLuint mask))
GL_PROC(void,glStencilOp,(GLenum fail, GLenum zfail, GLenum zpass))
GL_PROC(void,glTexCoord1d,(GLdouble s))
GL_PROC(void,glTexCoord1dv,(const GLdouble *v))
GL_PROC(void,glTexCoord1f,(GLfloat s))
GL_PROC(void,glTexCoord1fv,(const GLfloat *v))
GL_PROC(void,glTexCoord1i,(GLint s))
GL_PROC(void,glTexCoord1iv,(const GLint *v))
GL_PROC(void,glTexCoord1s,(GLshort s))
GL_PROC(void,glTexCoord1sv,(const GLshort *v))
GL_PROC(void,glTexCoord2d,(GLdouble s, GLdouble t))
GL_PROC(void,glTexCoord2dv,(const GLdouble *v))
GL_PROC(void,glTexCoord2f,(GLfloat s, GLfloat t))
GL_PROC(void,glTexCoord2fv,(const GLfloat *v))
GL_PROC(void,glTexCoord2i,(GLint s, GLint t))
GL_PROC(void,glTexCoord2iv,(const GLint *v))
GL_PROC(void,glTexCoord2s,(GLshort s, GLshort t))
GL_PROC(void,glTexCoord2sv,(const GLshort *v))
GL_PROC(void,glTexCoord3d,(GLdouble s, GLdouble t, GLdouble r))
GL_PROC(void,glTexCoord3dv,(const GLdouble *v))
GL_PROC(void,glTexCoord3f,(GLfloat s, GLfloat t, GLfloat r))
GL_PROC(void,glTexCoord3fv,(const GLfloat *v))
GL_PROC(void,glTexCoord3i,(GLint s, GLint t, GLint r))
GL_PROC(void,glTexCoord3iv,(const GLint *v))
GL_PROC(void,glTexCoord3s,(GLshort s, GLshort t, GLshort r))
GL_PROC(void,glTexCoord3sv,(const GLshort *v))
GL_PROC(void,glTexCoord4d,(GLdouble s, GLdouble t, GLdouble r, GLdouble q))
GL_PROC(void,glTexCoord4dv,(const GLdouble *v))
GL_PROC(void,glTexCoord4f,(GLfloat s, GLfloat t, GLfloat r, GLfloat q))
GL_PROC(void,glTexCoord4fv,(const GLfloat *v))
GL_PROC(void,glTexCoord4i,(GLint s, GLint t, GLint r, GLint q))
GL_PROC(void,glTexCoord4iv,(const GLint *v))
GL_PROC(void,glTexCoord4s,(GLshort s, GLshort t, GLshort r, GLshort q))
GL_PROC(void,glTexCoord4sv,(const GLshort *v))
GL_PROC(void,glTexCoordPointer,(GLint size, GLenum type, GLsizei stride, const GLvoid *pointer))
GL_PROC(void,glTexEnvf,(GLenum target, GLenum pname, GLfloat param))
GL_PROC(void,glTexEnvfv,(GLenum target, GLenum pname, const GLfloat *params))
GL_PROC(void,glTexEnvi,(GLenum target, GLenum pname, GLint param))
GL_PROC(void,glTexEnviv,(GLenum target, GLenum pname, const GLint *params))
GL_PROC(void,glTexGend,(GLenum coord, GLenum pname, GLdouble param))
GL_PROC(void,glTexGendv,(GLenum coord, GLenum pname, const GLdouble *params))
GL_PROC(void,glTexGenf,(GLenum coord, GLenum pname, GLfloat param))
GL_PROC(void,glTexGenfv,(GLenum coord, GLenum pname, const GLfloat *params))
GL_PROC(void,glTexGeni,(GLenum coord, GLenum pname, GLint param))
GL_PROC(void,glTexGeniv,(GLenum coord, GLenum pname, const GLint *params))
GL_PROC(void,glTexImage1D,(GLenum target, GLint level, GLint internalformat, GLsizei width, GLint border, GLenum format, GLenum type, const GLvoid *pixels))
GL_PROC(void,glTexImage2D,(GLenum target, GLint level, GLint internalformat, GLsizei width, GLsizei height, GLint border, GLenum format, GLenum type, const GLvoid *pixels))
GL_PROC(void,glTexParameterf,(GLenum target, GLenum pname, GLfloat param))
GL_PROC(void,glTexParameterfv,(GLenum target, GLenum pname, const GLfloat *params))
GL_PROC(void,glTexParameteri,(GLenum target, GLenum pname, GLint param))
GL_PROC(void,glTexParameteriv,(GLenum target, GLenum pname, const GLint *params))
GL_PROC(void,glTexSubImage1D,(GLenum target, GLint level, GLint xoffset, GLsizei width, GLenum format, GLenum type, const GLvoid *pixels))
GL_PROC(void,glTexSubImage2D,(GLenum target, GLint level, GLint xoffset, GLint yoffset, GLsizei width, GLsizei height, GLenum format, GLenum type, const GLvoid *pixels))
GL_PROC(void,glTranslated,(GLdouble x, GLdouble y, GLdouble z))
GL_PROC(void,glTranslatef,(GLfloat x, GLfloat y, GLfloat z))
GL_PROC(void,glVertex2d,(GLdouble x, GLdouble y))
GL_PROC(void,glVertex2dv,(const GLdouble *v))
GL_PROC(void,glVertex2f,(GLfloat x, GLfloat y))
GL_PROC(void,glVertex2fv,(const GLfloat *v))
GL_PROC(void,glVertex2i,(GLint x, GLint y))
GL_PROC(void,glVertex2iv,(const GLint *v))
GL_PROC(void,glVertex2s,(GLshort x, GLshort y))
GL_PROC(void,glVertex2sv,(const GLshort *v))
GL_PROC(void,glVertex3d,(GLdouble x, GLdouble y, GLdouble z))
GL_PROC(void,glVertex3dv,(const GLdouble *v))
GL_PROC(void,glVertex3f,(GLfloat x, GLfloat y, GLfloat z))
GL_PROC(void,glVertex3fv,(const GLfloat *v))
GL_PROC(void,glVertex3i,(GLint x, GLint y, GLint z))
GL_PROC(void,glVertex3iv,(const GLint *v))
GL_PROC(void,glVertex3s,(GLshort x, GLshort y, GLshort z))
GL_PROC(void,glVertex3sv,(const GLshort *v))
GL_PROC(void,glVertex4d,(GLdouble x, GLdouble y, GLdouble z, GLdouble w))
GL_PROC(void,glVertex4dv,(const GLdouble *v))
GL_PROC(void,glVertex4f,(GLfloat x, GLfloat y, GLfloat z, GLfloat w))
GL_PROC(void,glVertex4fv,(const GLfloat *v))
GL_PROC(void,glVertex4i,(GLint x, GLint y, GLint z, GLint w))
GL_PROC(void,glVertex4iv,(const GLint *v))
GL_PROC(void,glVertex4s,(GLshort x, GLshort y, GLshort z, GLshort w))
GL_PROC(void,glVertex4sv,(const GLshort *v))
GL_PROC(void,glVertexPointer,(GLint size, GLenum type, GLsizei stride, const GLvoid *pointer))
GL_PROC(void,glViewport,(GLint x, GLint y, GLsizei width, GLsizei height))
#endif</t>
<t tx="ekr.20060513122613.8" xcc_child_cfg="7d7100580b000000427265616b506f696e747371017d7102732e">#if USE_OPENGL &gt;= 2
	@others
#endif</t>
<t tx="ekr.20060513122613.9">#ifdef GL_DEFS
#define GL_UNSIGNED_BYTE_3_3_2            0x8032
#define GL_UNSIGNED_SHORT_4_4_4_4         0x8033
#define GL_UNSIGNED_SHORT_5_5_5_1         0x8034
#define GL_UNSIGNED_INT_8_8_8_8           0x8035
#define GL_UNSIGNED_INT_10_10_10_2        0x8036
#define GL_RESCALE_NORMAL                 0x803A
#define GL_TEXTURE_BINDING_3D             0x806A
#define GL_PACK_SKIP_IMAGES               0x806B
#define GL_PACK_IMAGE_HEIGHT              0x806C
#define GL_UNPACK_SKIP_IMAGES             0x806D
#define GL_UNPACK_IMAGE_HEIGHT            0x806E
#define GL_TEXTURE_3D                     0x806F
#define GL_PROXY_TEXTURE_3D               0x8070
#define GL_TEXTURE_DEPTH                  0x8071
#define GL_TEXTURE_WRAP_R                 0x8072
#define GL_MAX_3D_TEXTURE_SIZE            0x8073
#define GL_UNSIGNED_BYTE_2_3_3_REV        0x8362
#define GL_UNSIGNED_SHORT_5_6_5           0x8363
#define GL_UNSIGNED_SHORT_5_6_5_REV       0x8364
#define GL_UNSIGNED_SHORT_4_4_4_4_REV     0x8365
#define GL_UNSIGNED_SHORT_1_5_5_5_REV     0x8366
#define GL_UNSIGNED_INT_8_8_8_8_REV       0x8367
#define GL_UNSIGNED_INT_2_10_10_10_REV    0x8368
#define GL_BGR                            0x80E0
#define GL_BGRA                           0x80E1
#define GL_MAX_ELEMENTS_VERTICES          0x80E8
#define GL_MAX_ELEMENTS_INDICES           0x80E9
#define GL_CLAMP_TO_EDGE                  0x812F
#define GL_TEXTURE_MIN_LOD                0x813A
#define GL_TEXTURE_MAX_LOD                0x813B
#define GL_TEXTURE_BASE_LEVEL             0x813C
#define GL_TEXTURE_MAX_LEVEL              0x813D
#define GL_LIGHT_MODEL_COLOR_CONTROL      0x81F8
#define GL_SINGLE_COLOR                   0x81F9
#define GL_SEPARATE_SPECULAR_COLOR        0x81FA
#define GL_SMOOTH_POINT_SIZE_RANGE        0x0B12
#define GL_SMOOTH_POINT_SIZE_GRANULARITY  0x0B13
#define GL_SMOOTH_LINE_WIDTH_RANGE        0x0B22
#define GL_SMOOTH_LINE_WIDTH_GRANULARITY  0x0B23
#define GL_ALIASED_POINT_SIZE_RANGE       0x846D
#define GL_ALIASED_LINE_WIDTH_RANGE       0x846E
#endif</t>
<t tx="ekr.20060924180348"></t>
<t tx="ekr.20061023141459"></t>
<t tx="ekr.20061023141638"></t>
<t tx="ekr.20061023142737"></t>
<t tx="ekr.20061023142737.1"></t>
<t tx="ekr.20071113084440"># These plugins are for testing Leo's own plugin loading logic.
# There is no reason ever to enable these plugins.</t>
<t tx="ekr.20080515173014.1">([a-zA-Z_.]+)\.bind\((.*)\)(.*)$
c.bind(\1,\2)\3

[a-zA-Z_.]+

(\w)+(\.\w+)*

abc.xyz.pdq

# Bind w.bind with more than two args (none found)

w.bind\(.*,.*,.*$

[-w]\.bind\(</t>
<t tx="ekr.20080519084304.2">change = True # True: actually make the changes.
trace = True

print '-' * 40

tag = 'import leo' ; n = len('import ')

for p in p.self_and_subtree_iter():
    result = []
    for s in g.splitlines(p.bodyString()):
        i = s.find(tag,0)
        if i &gt; -1:
            # Do nothing if we have already done the translation.
            i2 = s.find('&lt;&lt;') ; i3 = s.find('import leo.core')
            if i2 == -1 and i3 == -1:
                i += n
                j = g.skip_c_id(s,i)
                word = s[i:j]
                rest = s[j:]
                if rest.strip().startswith('as'):
                    s = s[:i] + 'leo.core.' + word + rest
                else:
                    s = s[:i] + 'leo.core.' + word + ' as ' + word + rest
                if trace:
                    print p.headString()
                    j,k=g.getLine(s,i) ; print s[j:k]
        result.append(s)
    result = ''.join(result)

    if change and result != p.bodyString():
        c.setBodyString(p,result)

</t>
<t tx="ekr.20080619090226.4"></t>
<t tx="ekr.20081121105001.2080"># All gui plugins are now in leoGuiPluginsRef.leo</t>
<t tx="ekr.20090430075506.4"></t>
<t tx="ekr.20100102164842.5328">nodes = 0 ; lines = 0
for p in c.all_unique_positions():
    nodes += 1
    lines += len(g.splitLines(p.b))

pages = ((nodes * 10) + lines) / 50
s = "%d nodes,  %d lines, %d pages" % (nodes,lines,pages)
print(s); g.es(s)</t>
<t tx="ekr.20100103093121.5365"># These are experimental plugins.</t>
<t tx="ekr.20100909111553.5583"></t>
<t tx="ekr.20100909111553.5588"># Add the tree to the external unit test</t>
<t tx="ekr.20100909121239.5670"># Works in external unit tests.
g.loadOnePlugin(c,'screenshots')
sc = c.screenshotController
assert sc

fn = sc.get_directive_path(p)
assert fn</t>
<t tx="ekr.20100909121239.5797"></t>
<t tx="ekr.20100909121239.5951">g.loadOnePlugin(c,'screenshots')
sc = c.screenshotController

h = 'Headline and body text'
p2 = g.findNodeAnywhere(c,h)
assert p2

root,h = sc.find_at_screenshot_tree_node(p2)
assert root
assert h == 'Urgent'

</t>
<t tx="ekr.20100909193419.5596">if 0: # Doesn't work well.
    g.app.unitTestGui = 'qt'</t>
<t tx="ekr.20100910115903.5597"></t>
<t tx="ekr.20100910115903.5599"></t>
<t tx="ekr.20101004082701.5674"></t>
<t tx="ekr.20101110084839.5680">'''Print all plugins not in this file.'''

import glob

suppress = (
    '__init__.py',
    # Gui's
    'baseNativeTree.py','cursesGui.py','gtkDialogs.py','gtkGui.py',
    'ironPythonGui.py',
    'qtframecommands.py','qtGui.py','qt_main.py','qt_quicksearch.py',
    'swing_gui.py','tkGui.py','wxGui.py',
    # LeoUser stuff...
    'exampleTemacsExtension.py','temacs.py','usetemacs.py',
    # Ancient rst stuff...
    'rst.py','rst2.py',
)

all = glob.glob(g.os_path_finalize_join(
    g.app.loadDir,'..','plugins','*.py'))
all = [g.shortFileName(z) for z in all]
all.sort()

here = [v.anyAtFileNodeName() for v in c.all_unique_nodes()
    if v.isAnyAtFileNode()]

missing = [s for s in all if s not in here and s not in suppress]

if missing:
    print('='*20)
    print('missing plugins...\n')
    for s in missing:
        print(s)
else:
    g.es_print('no_missing plugins')
</t>
<t tx="ekr.20101110150056.9447"></t>
<t tx="ekr.20101110150056.9453"># Some of the most important recent plugins work only with the Qt gui.</t>
<t tx="ekr.20101110150056.9457"></t>
<t tx="ekr.20101110150056.9467"># These plugins would have to be substantially rewritten to be made gui-independent.</t>
<t tx="ekr.20101110150056.9469"></t>
<t tx="ekr.20101112124740.5432">g.app.gui.runScrolledMessageDialog(c=c, msg = g.u('rst:') + p.b + '\n\n')
</t>
<t tx="ekr.20110308220444.14251">print('*'*10)

@others

# exec(g.findTestScript(c,'@file codewisecompleter.py'))

tagLines = read_tags_file()
cc = CodewiseController(c)

# g.pdb()
for pattern in (
    'g.os_pa',
    'os.path.a',
    'os',
):
    print('\n','-'*10,pattern)
    cc.suggest(pattern=pattern)
</t>
<t tx="rogererens.20041130095659">@ It is possible to link to nodes within the same file.  However clones might be better.
</t>
<t tx="ville.20110409151021.5691"></t>
</tnodes>
</leo_file>
