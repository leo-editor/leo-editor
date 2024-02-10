<?xml version="1.0" encoding="utf-8"?>
<!-- Created by Leo: https://leo-editor.github.io/leo-editor/leo_toc.html -->
<leo_file xmlns:leo="https://leo-editor.github.io/leo-editor/namespaces/leo-python-editor/1.1" >
<leo_header file_format="2"/>
<globals/>
<preferences/>
<find_panel_settings/>
<vnodes>
<v t="ekr.20051031040240"><vh>Startup</vh>
<v t="ekr.20080412053100.5"><vh>@settings</vh>
<v t="ekr.20221129012213.1"><vh>@bool run-flake8-on-write = False</vh></v>
<v t="ekr.20140902155015.18674"><vh>@bool qt-use-scintilla = False</vh></v>
<v t="ekr.20210530065000.2"><vh>@data exec-script-commands</vh></v>
<v t="ekr.20210530065000.3"><vh>@data exec-script-patterns</vh></v>
<v t="ekr.20150425145248.1"><vh>@data history-list</vh></v>
<v t="ekr.20240107154430.1"><vh>@int max-find-long-lines-length = 90</vh></v>
<v t="ekr.20220904210247.1"><vh>@enabled-plugins</vh></v>
<v t="ekr.20140916101314.19538"><vh>@string target_language = python</vh></v>
<v t="ekr.20200212095937.1"><vh>Beautify command settings</vh>
<v t="ekr.20200212095937.2"><vh>@bool beautify-allow-joined-strings = False</vh></v>
<v t="ekr.20200212095937.3"><vh>@bool beautify-keep-comment-indentation = True</vh></v>
<v t="ekr.20200212095937.5"><vh>@int beautify-max-join-line-length = 0</vh></v>
<v t="ekr.20200212095937.6"><vh>@int beautify-max-split-line-length = 0</vh></v>
</v>
<v t="ekr.20160122104332.1"><vh>Buttons &amp; commands</vh>
<v t="ekr.20150502050609.1"><vh>@button backup</vh></v>
<v t="ekr.20170811173924.1"><vh>@button backup-repo</vh></v>
<v t="ekr.20231107062256.1"><vh>@button check-leoPy.leo</vh></v>
<v t="ekr.20230508145335.1"><vh>@command slow-tests</vh></v>
<v t="ekr.20220306092217.1"><vh>@command test-one @key=F5</vh>
<v t="ekr.20230511074046.1"><vh>&lt;&lt; prefixes &gt;&gt;</vh></v>
</v>
<v t="ekr.20201013034659.1"><vh>@ignore Unused buttons and commands</vh>
<v t="ekr.20211020091540.1"><vh>@@command b</vh></v>
<v t="ekr.20220527065937.1"><vh>@command json-to-outline</vh></v>
<v t="ekr.20150413091056.1"><vh>@@button check-clones</vh></v>
<v t="ekr.20180324065741.1"><vh>@@button copy-to-next</vh></v>
<v t="ekr.20150507170849.1"><vh>@@button create decorators</vh>
<v t="ekr.20150508063538.1"><vh>create_d</vh></v>
<v t="ekr.20150508071622.1"><vh>create_decorator (@button)</vh></v>
<v t="ekr.20150508063412.1"><vh>create_decorators</vh></v>
<v t="ekr.20150508074623.1"><vh>create_fixups</vh></v>
<v t="ekr.20150508063926.1"><vh>find_class</vh></v>
<v t="ekr.20150507174711.1"><vh>find_next_clone</vh></v>
<v t="ekr.20150507175246.1"><vh>munge_lines</vh></v>
<v t="ekr.20150508062944.1"><vh>run</vh></v>
</v>
<v t="ekr.20211011090013.1"><vh>@@button cvt-comments</vh>
<v t="ekr.20220425184232.1"><vh>compute_lws</vh></v>
<v t="ekr.20220425052306.1"><vh>convert</vh></v>
</v>
<v t="ekr.20150509183433.1"><vh>@@button make-decorators2</vh>
<v t="ekr.20150509183433.2"><vh>create_d</vh></v>
<v t="ekr.20150509183433.3"><vh>create_decorator (@button)</vh></v>
<v t="ekr.20150509183433.4"><vh>create_decorators V2</vh></v>
<v t="ekr.20150509183433.8"><vh>munge_lines</vh></v>
<v t="ekr.20150509183433.9"><vh>run V2</vh></v>
</v>
<v t="ekr.20201013034742.2"><vh>@@button make-importer</vh>
<v t="ekr.20201013034742.3"><vh>&lt;&lt; define run &amp; helpers &gt;&gt;</vh>
<v t="ekr.20201013034742.4"><vh>copy_tree (make-importer)</vh></v>
<v t="ekr.20201013034742.5"><vh>make_substitutions</vh></v>
<v t="ekr.20201013034742.6"><vh>run</vh></v>
<v t="ekr.20201013034742.7"><vh>substitue</vh></v>
</v>
<v t="ekr.20201013034742.8"><vh>@@file importers/{{name}}.py</vh>
<v t="ekr.20201013034742.9"><vh>class {{cap_name}}_Importer</vh>
<v t="ekr.20201013034742.10"><vh>{{name}}.Overrides</vh>
<v t="ekr.20201013034742.11"><vh>{{name}}.clean_headline</vh></v>
<v t="ekr.20201013034742.12"><vh>{{name}}.clean_nodes</vh></v>
</v>
</v>
<v t="ekr.20201013034742.13"><vh>class {{cap_name}}_ScanState</vh></v>
</v>
</v>
<v t="ekr.20190406154306.1"><vh>@@button open-pyzo</vh></v>
<v t="ekr.20201013034742.16"><vh>@@button pep8 @key=Ctrl-5</vh>
<v t="ekr.20201013034742.17"><vh>class Pep8</vh>
<v t="ekr.20201013034742.18"><vh>change_all &amp; helpers</vh>
<v t="ekr.20201013034742.19"><vh>change_body</vh></v>
<v t="ekr.20201013034742.20"><vh>change_headline</vh></v>
</v>
<v t="ekr.20201013034742.21"><vh>get_name</vh></v>
<v t="ekr.20201013034742.22"><vh>run</vh></v>
<v t="ekr.20201013034742.23"><vh>to_pep8</vh></v>
</v>
<v t="ekr.20201013034742.24"><vh>clear</vh></v>
</v>
<v t="ekr.20150703061709.1"><vh>@@button run-pylint</vh></v>
<v t="ekr.20180824065751.1"><vh>@@button show-gnx</vh></v>
<v t="ekr.20131121084830.16362"><vh>@@button toggle-debug</vh></v>
<v t="ekr.20201018062305.1"><vh>@@button write-leoPyRef</vh>
<v t="ekr.20201018065757.1"><vh>check_file_names</vh></v>
<v t="ekr.20201018065921.1"><vh>check_nodes</vh></v>
<v t="ekr.20201018070822.1"><vh>main</vh></v>
<v t="ekr.20201018072911.1"><vh>oops</vh></v>
<v t="ekr.20201018063747.1"><vh>put_content</vh></v>
<v t="ekr.20210510071427.1"><vh>put_prolog</vh></v>
<v t="ekr.20210510071812.1"><vh>put_tnodes</vh></v>
</v>
</v>
</v>
<v t="ekr.20210110092457.1"><vh>leojs buttons</vh>
<v t="ekr.20210110092457.5"><vh>@@@button cov @key=ctrl-6</vh></v>
<v t="ekr.20210110092457.6"><vh>@@@button moz @key=ctrl-7</vh></v>
<v t="ekr.20210110092457.7"><vh>@@@button unit</vh></v>
</v>
</v>
<v t="ekr.20170427114412.1"><vh>scripts</vh>
<v t="ekr.20170427112302.1"><vh>check leoPy.leo</vh></v>
<v t="ekr.20170428084123.1"><vh>Recursive import script</vh></v>
<v t="ekr.20201222095250.1"><vh>script: check for duplicate settings in theme files</vh></v>
<v t="ekr.20200308193719.1"><vh>script: check gnx's</vh></v>
<v t="ekr.20210429045101.1"><vh>script: check gnxDict</vh></v>
<v t="ekr.20210118013157.1"><vh>script: convert-LeoFind</vh>
<v t="ekr.20210118024739.1"><vh>convert</vh></v>
<v t="ekr.20210118013807.1"><vh>main</vh></v>
<v t="ekr.20210118020530.1"><vh>new_name</vh></v>
<v t="ekr.20210118021337.1"><vh>exists</vh></v>
</v>
<v t="ekr.20210829132319.1"><vh>script: cvt-tests</vh></v>
<v t="ekr.20190402091335.1"><vh>script: diff-branches/revs (all files)</vh></v>
<v t="ekr.20180816105258.1"><vh>script: diff-branches/revs (one file)</vh></v>
<v t="ekr.20201208114843.1"><vh>script: diff-pr</vh></v>
<v t="ekr.20220319145807.1"><vh>script: diff-two-revs-wo-comments</vh>
<v t="ekr.20220319151900.1"><vh>function: make_diff_outlines_ignoring_comments</vh></v>
<v t="ekr.20220319152417.1"><vh>function: strip_comments</vh></v>
</v>
<v t="ekr.20220318085657.1"><vh>script: find trailing comments</vh></v>
<v t="ekr.20220503081113.1"><vh>script: find-non-calls</vh>
<v t="ekr.20220503193901.1"><vh>old suppressions</vh></v>
<v t="ekr.20220503084900.1"><vh>&lt;&lt; init core_p, command_p and globals_p &gt;&gt;</vh></v>
<v t="ekr.20220503084230.1"><vh>function: check</vh></v>
<v t="ekr.20220503084045.1"><vh>function: scan</vh></v>
</v>
<v t="ekr.20201015145257.1"><vh>script: import legacy file</vh></v>
<v t="ekr.20230720115916.1"><vh>script: node-history</vh></v>
<v t="ekr.20210630070717.1"><vh>script: restore gnxs in leoserver.py (full version)</vh>
<v t="ekr.20210701044426.1"><vh>&lt;&lt; setup &gt;&gt;</vh></v>
<v t="ekr.20210701044513.1"><vh>&lt;&lt; read into a1_s, b1_s &gt;&gt;</vh></v>
</v>
<v t="ekr.20210630103405.1"><vh>script: restore gnxs in leoserver.py (simple version)</vh></v>
<v t="ekr.20200222083959.1"><vh>script: start loggin</vh></v>
<v t="ekr.20211014103433.1"><vh>script: web-to-outline</vh>
<v t="ekr.20211014112513.1"><vh>Handlers</vh></v>
<v t="ekr.20211014120710.1"><vh>new_node</vh></v>
</v>
<v t="ekr.20200222151754.1"><vh>script: yoton "other end"</vh></v>
</v>
</v>
<v t="EKR.20040430162943"><vh>Notes</vh>
<v t="ekr.20170302123956.1"><vh>@file ../doc/leoAttic.txt</vh></v>
</v>
<v t="ekr.20031218072017.2406"><vh>Code</vh>
<v t="ekr.20140902032918.18591"><vh>About this file</vh>
<v t="ekr.20140831085423.18639"><vh>About widgets and wrappers</vh></v>
<v t="ekr.20140831085423.18630"><vh>Terminology</vh></v>
<v t="ekr.20140831085423.18631"><vh>Official ivars</vh></v>
</v>
<v t="ekr.20031218072017.2604"><vh>Core classes</vh>
<v t="ekr.20031218072017.2608"><vh>@file leoApp.py</vh></v>
<v t="ekr.20141012064706.18389"><vh>@file leoAst.py</vh></v>
<v t="ekr.20150323150718.1"><vh>@file leoAtFile.py</vh></v>
<v t="ekr.20161026193447.1"><vh>@file leoBackground.py</vh></v>
<v t="ekr.20150521115018.1"><vh>@file leoBeautify.py</vh></v>
<v t="ekr.20070227091955.1"><vh>@file leoBridge.py</vh></v>
<v t="ekr.20100208065621.5894"><vh>@file leoCache.py</vh></v>
<v t="ekr.20070317085508.1"><vh>@file leoChapters.py</vh></v>
<v t="ekr.20031218072017.2794"><vh>@file leoColor.py</vh></v>
<v t="ekr.20140827092102.18574"><vh>@file leoColorizer.py</vh></v>
<v t="ekr.20031218072017.2810"><vh>@file leoCommands.py</vh></v>
<v t="ekr.20180212072657.2"><vh>@file leoCompare.py</vh></v>
<v t="ekr.20130925160837.11429"><vh>@file leoConfig.py</vh></v>
<v t="ekr.20130302121602.10208"><vh>@file leoDebugger.py</vh></v>
<v t="ekr.20160306114544.1"><vh>@file leoExternalFiles.py</vh></v>
<v t="ekr.20181202062518.1"><vh>@file leoFastRedraw.py</vh></v>
<v t="ekr.20031218072017.3018"><vh>@file leoFileCommands.py</vh></v>
<v t="ekr.20031218072017.3093"><vh>@file leoGlobals.py</vh></v>
<v t="ekr.20150514154159.1"><vh>@file leoHistory.py</vh></v>
<v t="ekr.20031218072017.3206"><vh>@file leoImport.py</vh></v>
<v t="ekr.20120401063816.10072"><vh>@file leoIPython.py</vh></v>
<v t="ekr.20190515070742.1"><vh>@file leoMarkup.py</vh></v>
<v t="ekr.20031218072017.3320"><vh>@file leoNodes.py</vh></v>
<v t="ekr.20140821055201.18331"><vh>@file leoPersistence.py</vh></v>
<v t="ekr.20031218072017.3439"><vh>@file leoPlugins.py</vh></v>
<v t="ekr.20150419124739.1"><vh>@file leoPrinting.py</vh></v>
<v t="ekr.20061024060248.1"><vh>@file leoPymacs.py</vh></v>
<v t="ekr.20140810053602.18074"><vh>@file leoQt.py</vh></v>
<v t="ekr.20210407010914.1"><vh>@file leoQt5.py</vh></v>
<v t="ekr.20210407011013.1"><vh>@file leoQt6.py</vh></v>
<v t="ekr.20140526082700.18440"><vh>@file leoRope.py</vh></v>
<v t="ekr.20090502071837.3"><vh>@file leoRst.py</vh></v>
<v t="ekr.20120420054855.14241"><vh>@file leoSessions.py</vh></v>
<v t="ekr.20080708094444.1"><vh>@file leoShadow.py</vh></v>
<v t="ekr.20180121041003.1"><vh>@file leoTips.py</vh></v>
<v t="ekr.20240105140814.1"><vh>@file leoTokens.py</vh></v>
<v t="ekr.20031218072017.3603"><vh>@file leoUndo.py</vh></v>
<v t="ekr.20131109170017.16504"><vh>@file leoVim.py</vh></v>
</v>
<v t="ekr.20150514035207.1"><vh>Command classes</vh>
<v t="ekr.20150514035236.1"><vh>@file ../commands/abbrevCommands.py</vh></v>
<v t="ekr.20150514035943.1"><vh>@file ../commands/baseCommands.py</vh></v>
<v t="ekr.20150514035559.1"><vh>@file ../commands/bufferCommands.py</vh></v>
<v t="ekr.20161021090740.1"><vh>@file ../commands/checkerCommands.py</vh></v>
<v t="ekr.20171123135539.1"><vh>@file ../commands/commanderEditCommands.py</vh></v>
<v t="ekr.20171123095353.1"><vh>@file ../commands/commanderFileCommands.py</vh></v>
<v t="ekr.20171124073126.1"><vh>@file ../commands/commanderHelpCommands.py</vh></v>
<v t="ekr.20171124080430.1"><vh>@file ../commands/commanderOutlineCommands.py</vh></v>
<v t="ekr.20150514040100.1"><vh>@file ../commands/controlCommands.py</vh></v>
<v t="ekr.20160316095222.1"><vh>@file ../commands/convertCommands.py</vh></v>
<v t="ekr.20150514040118.1"><vh>@file ../commands/debugCommands.py</vh></v>
<v t="ekr.20150514035813.1"><vh>@file ../commands/editCommands.py</vh></v>
<v t="ekr.20150514041209.1"><vh>@file ../commands/editFileCommands.py</vh></v>
<v t="ekr.20150624112334.1"><vh>@file ../commands/gotoCommands.py</vh></v>
<v t="ekr.20150514040138.1"><vh>@file ../commands/helpCommands.py</vh></v>
<v t="ekr.20150514040140.1"><vh>@file ../commands/keyCommands.py</vh></v>
<v t="ekr.20150514040142.1"><vh>@file ../commands/killBufferCommands.py</vh></v>
<v t="ekr.20150514040146.1"><vh>@file ../commands/rectangleCommands.py</vh></v>
<v t="ekr.20150514040239.1"><vh>@file ../commands/spellCommands.py</vh></v>
</v>
<v t="ekr.20031218072017.3625"><vh>Gui base classes</vh>
<v t="ekr.20050721093241"><vh>&lt;&lt; about gui classes and gui plugins &gt;&gt;</vh></v>
<v t="ekr.20060123151617"><vh>@file leoFind.py</vh></v>
<v t="ekr.20031218072017.3655"><vh>@file leoFrame.py</vh></v>
<v t="ekr.20031218072017.3719"><vh>@file leoGui.py</vh></v>
<v t="ekr.20061031131434"><vh>@file leoKeys.py</vh></v>
<v t="ekr.20031218072017.3749"><vh>@file leoMenu.py</vh></v>
</v>
<v t="ekr.20180225010644.1"><vh>Other files</vh>
<v t="ekr.20180225010707.1"><vh>In leo-editor directory</vh>
<v t="ekr.20230702120645.1"><vh>@@edit ../../.dmypy.ini</vh></v>
<v t="ekr.20240201175949.1"><vh>@@file ../../requirements.txt</vh></v>
<v t="ekr.20220222130955.1"><vh>@edit ../../.mypy.ini</vh></v>
<v t="ekr.20231108150521.1"><vh>@edit ../../CONTRIBUTING.md</vh></v>
<v t="ekr.20210302164046.1"><vh>@edit ../../launchLeo.py</vh></v>
<v t="ekr.20240206163135.1"><vh>@edit ../../manifest.in</vh></v>
<v t="ekr.20240206153029.1"><vh>@edit ../../readme.md</vh></v>
<v t="ekr.20240206161713.1"><vh>@edit ../../setup.cfg </vh></v>
<v t="ekr.20150304125314.4"><vh>@file ../../leo_to_html.xsl</vh></v>
<v t="ekr.20181014073705.1"><vh>@file ../../run_pytest_tests.py</vh></v>
<v t="ekr.20181009072707.1"><vh>@file ../../run_travis_unit_tests.py</vh></v>
<v t="ekr.20150304130753.4"><vh>leo-viewer/leo_to_html.xsl</vh></v>
</v>
<v t="ekr.20230717210524.1"><vh>In leo/docs</vh>
<v t="ekr.20230716154653.1"><vh>@edit ../../docs/load-leo.html</vh></v>
</v>
<v t="ekr.20180225010913.1"><vh>In leo/core</vh>
<v t="ekr.20210202110241.1"><vh>@file leoclient.py</vh></v>
<v t="ekr.20031218072017.2605"><vh>@file runLeo.py</vh></v>
<v t="felix.20210621233316.1"><vh>@file leoserver.py</vh></v>
<v t="ekr.20230203163544.1"><vh>@file tracing_utils.py</vh></v>
</v>
<v t="ekr.20180225010743.1"><vh>In leo/external</vh>
<v t="ekr.20190607124533.1"><vh>@nopylint</vh>
<v t="ekr.20220823195205.1"><vh>@clean ../external/leoftsindex.py</vh></v>
<v t="ekr.20160123142722.1"><vh>@clean ../external/make_stub_files.cfg</vh></v>
<v t="ekr.20180708145905.1"><vh>@clean ../external/py2cs_theory.md</vh>
<v t="ekr.20180708152000.1"><vh>The problem</vh></v>
<v t="ekr.20180708152018.1"><vh>Design</vh></v>
<v t="ekr.20180708145905.6"><vh>Using TokenSync class</vh></v>
<v t="ekr.20180708145905.7"><vh>Summary</vh></v>
</v>
<v t="ekr.20110310091639.14254"><vh>@file ../external/codewise.py</vh></v>
<v t="ekr.20130805134749.12436"><vh>@file ../external/edb.py</vh></v>
<v t="ekr.20120519121124.9919"><vh>@file ../external/leosax.py</vh></v>
<v t="ekr.20170429161422.1"><vh>@file ../external/log_broadcast.py</vh></v>
<v t="ekr.20170429153135.1"><vh>@file ../external/log_listener.py</vh></v>
<v t="ville.20091010232339.6117"><vh>@file ../external/lproto.py</vh></v>
<v t="ekr.20160317054700.1"><vh>@file ../external/make_stub_files.py</vh></v>
<v t="ekr.20180628055640.1"><vh>@file ../external/pdb_listener.py</vh></v>
<v t="ekr.20160316091132.1"><vh>@file ../external/py2cs.py</vh></v>
<v t="ekr.20220823195753.1"><vh>@file ../external/stringlist.py</vh></v>
<v t="ekr.20170428085201.1"><vh>npyscreen</vh>
<v t="ekr.20170428084207.3"><vh>@file ../external/npyscreen/apNPSApplication.py</vh></v>
<v t="ekr.20170428084207.11"><vh>@file ../external/npyscreen/apNPSApplicationAdvanced.py</vh></v>
<v t="ekr.20170428084207.15"><vh>@file ../external/npyscreen/apNPSApplicationEvents.py</vh></v>
<v t="ekr.20170428084207.29"><vh>@file ../external/npyscreen/apNPSApplicationManaged.py</vh></v>
<v t="ekr.20170428084207.50"><vh>@file ../external/npyscreen/apOptions.py</vh></v>
<v t="ekr.20170428084207.111"><vh>@file ../external/npyscreen/eveventhandler.py</vh></v>
<v t="ekr.20170428084207.121"><vh>@file ../external/npyscreen/fmActionForm.py</vh></v>
<v t="ekr.20170428084207.131"><vh>@file ../external/npyscreen/fmActionFormV2.py</vh></v>
<v t="ekr.20170428084207.153"><vh>@file ../external/npyscreen/fmFileSelector.py</vh></v>
<v t="ekr.20170428084207.174"><vh>@file ../external/npyscreen/fmForm.py</vh></v>
<v t="ekr.20170428084207.223"><vh>@file ../external/npyscreen/fmFormMultiPage.py</vh></v>
<v t="ekr.20170428084207.248"><vh>@file ../external/npyscreen/fmFormMutt.py</vh></v>
<v t="ekr.20170428084207.258"><vh>@file ../external/npyscreen/fmFormMuttActive.py</vh></v>
<v t="ekr.20170428084207.285"><vh>@file ../external/npyscreen/fmFormWithMenus.py</vh></v>
<v t="ekr.20170428084207.303"><vh>@file ../external/npyscreen/fmPopup.py</vh></v>
<v t="ekr.20170428084207.311"><vh>@file ../external/npyscreen/fm_form_edit_loop.py</vh></v>
<v t="ekr.20170428084207.322"><vh>@file ../external/npyscreen/globals.py</vh></v>
<v t="ekr.20170428084207.324"><vh>@file ../external/npyscreen/muMenu.py</vh></v>
<v t="ekr.20170428084207.332"><vh>@file ../external/npyscreen/muNewMenu.py</vh></v>
<v t="ekr.20170428084207.351"><vh>@file ../external/npyscreen/npysGlobalOptions.py</vh></v>
<v t="ekr.20170428084207.353"><vh>@file ../external/npyscreen/npysNPSFilteredData.py</vh></v>
<v t="ekr.20170428084207.364"><vh>@file ../external/npyscreen/npyspmfuncs.py</vh></v>
<v t="ekr.20170428084207.370"><vh>@file ../external/npyscreen/npyssafewrapper.py</vh></v>
<v t="ekr.20170428084207.377"><vh>@file ../external/npyscreen/npysThemeManagers.py</vh></v>
<v t="ekr.20170428084207.390"><vh>@file ../external/npyscreen/npysThemes.py</vh></v>
<v t="ekr.20170428084207.399"><vh>@file ../external/npyscreen/npysTree.py</vh></v>
<v t="ekr.20170428084207.422"><vh>@file ../external/npyscreen/proto_fm_screen_area.py</vh></v>
<v t="ekr.20170428084207.434"><vh>@file ../external/npyscreen/stdfmemail.py</vh></v>
<v t="ekr.20170428084207.464"><vh>@file ../external/npyscreen/utilNotify.py</vh></v>
<v t="ekr.20170428084207.477"><vh>@file ../external/npyscreen/util_viewhelp.py</vh></v>
<v t="ekr.20170428084207.480"><vh>@file ../external/npyscreen/wgannotatetextbox.py</vh></v>
<v t="ekr.20170428084207.494"><vh>@file ../external/npyscreen/wgautocomplete.py</vh></v>
<v t="ekr.20170428084207.503"><vh>@file ../external/npyscreen/wgboxwidget.py</vh></v>
<v t="ekr.20170428084207.524"><vh>@file ../external/npyscreen/wgbutton.py</vh></v>
<v t="ekr.20170428084207.536"><vh>@file ../external/npyscreen/wgcheckbox.py</vh></v>
<v t="ekr.20170428084207.561"><vh>@file ../external/npyscreen/wgcombobox.py</vh></v>
<v t="ekr.20170428084207.575"><vh>@file ../external/npyscreen/wgdatecombo.py</vh></v>
<v t="ekr.20170428084207.586"><vh>@file ../external/npyscreen/wgeditmultiline.py</vh></v>
<v t="ekr.20170428084207.611"><vh>@file ../external/npyscreen/wgfilenamecombo.py</vh></v>
<v t="ekr.20170428084207.618"><vh>@file ../external/npyscreen/wgFormControlCheckbox.py</vh></v>
<v t="ekr.20170428084208.1"><vh>@file ../external/npyscreen/wggrid.py</vh></v>
<v t="ekr.20170428084208.36"><vh>@file ../external/npyscreen/wggridcoltitles.py</vh></v>
<v t="ekr.20170428084208.43"><vh>@file ../external/npyscreen/wgmonthbox.py</vh></v>
<v t="ekr.20170428084208.68"><vh>@file ../external/npyscreen/wgmultiline.py</vh></v>
<v t="ekr.20170428084208.157"><vh>@file ../external/npyscreen/wgmultilineeditable.py</vh></v>
<v t="ekr.20170428084208.173"><vh>@file ../external/npyscreen/wgmultilinetree.py</vh></v>
<v t="ekr.20170428084208.213"><vh>@file ../external/npyscreen/wgmultilinetreeselectable.py</vh></v>
<v t="ekr.20170428084208.225"><vh>@file ../external/npyscreen/wgmultiselect.py</vh></v>
<v t="ekr.20170428084208.245"><vh>@file ../external/npyscreen/wgmultiselecttree.py</vh></v>
<v t="ekr.20170428084208.253"><vh>@file ../external/npyscreen/wgNMenuDisplay.py</vh></v>
<v t="ekr.20170428084208.285"><vh>@file ../external/npyscreen/wgpassword.py</vh></v>
<v t="ekr.20170428084208.290"><vh>@file ../external/npyscreen/wgselectone.py</vh></v>
<v t="ekr.20170428084208.297"><vh>@file ../external/npyscreen/wgslider.py</vh></v>
<v t="ekr.20170428084208.318"><vh>@file ../external/npyscreen/wgtextbox.py</vh></v>
<v t="ekr.20170428084208.354"><vh>@file ../external/npyscreen/wgtextboxunicode.py</vh></v>
<v t="ekr.20170428084208.359"><vh>@file ../external/npyscreen/wgtextbox_controlchrs.py</vh></v>
<v t="ekr.20170428084208.366"><vh>@file ../external/npyscreen/wgtexttokens.py</vh></v>
<v t="ekr.20170428084208.381"><vh>@file ../external/npyscreen/wgtitlefield.py</vh></v>
<v t="ekr.20170428084208.398"><vh>@file ../external/npyscreen/wgwidget.py</vh></v>
<v t="ekr.20170428084208.436"><vh>@file ../external/npyscreen/wgwidget_proto.py</vh></v>
<v t="ekr.20170428084208.443"><vh>@@file ../external/npyscreen/__init__.py</vh>
<v t="ekr.20170428084208.444"><vh>Declarations</vh></v>
</v>
</v>
</v>
</v>
<v t="ekr.20180225010850.1"><vh>In leo/modes</vh>
<v t="ekr.20221129095254.1"><vh>@file ../modes/batch.py</vh></v>
<v t="ekr.20150326145530.1"><vh>@file ../modes/forth.py</vh></v>
<v t="ekr.20230419050031.1"><vh>@file ../modes/html.py</vh></v>
<v t="ekr.20230419052236.1"><vh>@file ../modes/javascript.py</vh></v>
<v t="ekr.20210223151922.1"><vh>@file ../modes/julia.py</vh></v>
<v t="ekr.20240202211600.1"><vh>@file ../modes/nim.py</vh></v>
<v t="ekr.20210219115553.109"><vh>@file ../modes/python.py</vh></v>
<v t="ekr.20231103124615.1"><vh>@file ../modes/rust.py</vh></v>
<v t="ekr.20231012163843.1"><vh>@file ../modes/scheme.py</vh></v>
</v>
<v t="ekr.20231218084214.1"><vh>In leo/rust</vh>
<v t="ekr.20231218084134.2"><vh>Transliterated leoBeautify.rs</vh>
<v t="ekr.20231218084134.3"><vh>&lt;&lt; leoBeautify imports &amp; annotations &gt;&gt;</vh></v>
<v t="ekr.20231218084134.4"><vh>  Top-level functions (leoBeautify.py)</vh>
<v t="ekr.20231218084134.5"><vh>Beautify:commands</vh>
<v t="ekr.20231218084134.6"><vh>beautify-c</vh></v>
<v t="ekr.20231218084134.7"><vh>beautify-file-diff</vh></v>
<v t="ekr.20231218084134.8"><vh>beautify-files</vh></v>
<v t="ekr.20231218084134.9"><vh>blacken-files</vh></v>
<v t="ekr.20231218084134.10"><vh>blacken-files-diff</vh></v>
<v t="ekr.20231218084134.11"><vh>fstringify-files</vh></v>
<v t="ekr.20231218084134.12"><vh>fstringify-files-diff</vh></v>
<v t="ekr.20231218084134.13"><vh>fstringify-files-silent</vh></v>
<v t="ekr.20231218084134.14"><vh>orange_settings</vh></v>
</v>
<v t="ekr.20231218084134.15"><vh>Beautify:test functions</vh>
<v t="ekr.20231218084134.16"><vh>function: show</vh></v>
</v>
<v t="ekr.20231218084134.17"><vh>function: should_beautify</vh></v>
<v t="ekr.20231218084134.18"><vh>function: should_kill_beautify</vh></v>
</v>
<v t="ekr.20231218084134.19"><vh>class CPrettyPrinter</vh>
<v t="ekr.20231218084134.20"><vh>cpp.__init__</vh></v>
<v t="ekr.20231218084134.21"><vh>cpp.pretty_print_tree</vh></v>
<v t="ekr.20231218084134.22"><vh>cpp.indent &amp; helpers</vh>
<v t="ekr.20231218084134.23"><vh>cpp.add_statement_braces</vh>
<v t="ekr.20231218084134.24"><vh>cpp.skip_ws</vh></v>
<v t="ekr.20231218084134.25"><vh>cpp.skip_ws_and_comments</vh></v>
<v t="ekr.20231218084134.26"><vh>cpp.skip_parens</vh></v>
<v t="ekr.20231218084134.27"><vh>cpp.skip_statement</vh></v>
</v>
<v t="ekr.20231218084134.28"><vh>cpp.put_token &amp; helpers</vh>
<v t="ekr.20231218084134.29"><vh>prev_token</vh></v>
<v t="ekr.20231218084134.30"><vh>reformat_block_comment</vh></v>
<v t="ekr.20231218084134.31"><vh>remove_indent</vh></v>
</v>
</v>
<v t="ekr.20231218084134.32"><vh>cpp.match</vh></v>
<v t="ekr.20231218084134.33"><vh>cpp.tokenize &amp; helper</vh>
<v t="ekr.20231218084134.34"><vh>cpp.skip_block_comment</vh></v>
</v>
</v>
</v>
<v t="ekr.20231218084055.2"><vh>Transliterated leoAst.rs</vh>
<v t="ekr.20231218084055.3"><vh>&lt;&lt; leoAst docstring &gt;&gt;</vh></v>
<v t="ekr.20231218084055.4"><vh>&lt;&lt; leoAst imports &amp; annotations &gt;&gt;</vh></v>
<v t="ekr.20231218084055.5"><vh> leoAst.py: top-level commands</vh>
<v t="ekr.20231218084055.6"><vh>command: fstringify_command</vh></v>
<v t="ekr.20231218084055.7"><vh>command: fstringify_diff_command</vh></v>
<v t="ekr.20231218084055.8"><vh>command: orange_command</vh></v>
<v t="ekr.20231218084055.9"><vh>command: orange_diff_command</vh></v>
</v>
<v t="ekr.20231218084055.10"><vh> leoAst.py: top-level utils</vh>
<v t="ekr.20231218084055.11"><vh>function: check_g</vh></v>
<v t="ekr.20231218084055.12"><vh>function: get_modified_files</vh></v>
<v t="ekr.20231218084055.13"><vh>function: scan_ast_args</vh></v>
<v t="ekr.20231218084055.14"><vh>functions: reading &amp; writing files</vh>
<v t="ekr.20231218084055.15"><vh>function: regularize_nls</vh></v>
<v t="ekr.20231218084055.16"><vh>function: get_encoding_directive</vh></v>
<v t="ekr.20231218084055.17"><vh>function: read_file</vh></v>
<v t="ekr.20231218084055.18"><vh>function: read_file_with_encoding</vh></v>
<v t="ekr.20231218084055.19"><vh>function: strip_BOM</vh></v>
<v t="ekr.20231218084055.20"><vh>function: write_file</vh></v>
</v>
<v t="ekr.20231218084055.21"><vh>functions: tokens</vh>
<v t="ekr.20231218084055.22"><vh>function: find_anchor_token</vh></v>
<v t="ekr.20231218084055.23"><vh>function: find_paren_token</vh></v>
<v t="ekr.20231218084055.24"><vh>function: get_node_tokens_list</vh></v>
<v t="ekr.20231218084055.25"><vh>function: is_significant &amp; is_significant_token</vh></v>
<v t="ekr.20231218084055.26"><vh>function: match_parens</vh></v>
<v t="ekr.20231218084055.27"><vh>function: tokens_for_node</vh></v>
<v t="ekr.20231218084055.28"><vh>function: tokens_to_string</vh></v>
</v>
<v t="ekr.20231218084055.29"><vh>node/token nodes...</vh>
<v t="ekr.20231218084055.30"><vh>function: find_statement_node</vh></v>
<v t="ekr.20231218084055.31"><vh>function: is_ancestor</vh></v>
<v t="ekr.20231218084055.32"><vh>function: is_long_statement</vh></v>
<v t="ekr.20231218084055.33"><vh>function: is_statement_node</vh></v>
<v t="ekr.20231218084055.34"><vh>function: nearest_common_ancestor</vh></v>
</v>
<v t="ekr.20231218084055.35"><vh>functions: utils...</vh>
<v t="ekr.20231218084055.36"><vh>function: obj_id</vh></v>
<v t="ekr.20231218084055.37"><vh>function: op_name</vh></v>
</v>
<v t="ekr.20231218084055.38"><vh>node/token creators...</vh>
<v t="ekr.20231218084055.39"><vh>function: make_tokens</vh></v>
<v t="ekr.20231218084055.40"><vh>function: parse_ast</vh></v>
</v>
<v t="ekr.20231218084055.41"><vh>node/token dumpers...</vh>
<v t="ekr.20231218084055.42"><vh>function: dump_ast</vh></v>
<v t="ekr.20231218084055.43"><vh>function: dump_contents</vh></v>
<v t="ekr.20231218084055.44"><vh>function: dump_lines</vh></v>
<v t="ekr.20231218084055.45"><vh>function: dump_results</vh></v>
<v t="ekr.20231218084055.46"><vh>function: dump_tokens</vh></v>
<v t="ekr.20231218084055.47"><vh>function: dump_tree</vh></v>
<v t="ekr.20231218084055.48"><vh>function: show_diffs</vh></v>
</v>
<v t="ekr.20231218084055.49"><vh>node/token replacers...</vh>
<v t="ekr.20231218084055.50"><vh>function: add_token_to_token_list</vh></v>
<v t="ekr.20231218084055.51"><vh>function: replace_node</vh></v>
<v t="ekr.20231218084055.52"><vh>function: replace_token</vh></v>
</v>
</v>
<v t="ekr.20231218084055.53"><vh>Exception classes</vh></v>
<v t="ekr.20231218084055.54"><vh>Classes</vh>
<v t="ekr.20231218084055.55"><vh>class AstDumper</vh>
<v t="ekr.20231218084055.56"><vh>dumper.dump_tree &amp; helper</vh>
<v t="ekr.20231218084055.57"><vh>dumper.dump_tree_and_links_helper</vh></v>
</v>
<v t="ekr.20231218084055.58"><vh>dumper.compute_node_string &amp; helpers</vh>
<v t="ekr.20231218084055.59"><vh>dumper.show_fields</vh></v>
<v t="ekr.20231218084055.60"><vh>dumper.show_line_range</vh></v>
<v t="ekr.20231218084055.61"><vh>dumper.show_tokens</vh></v>
</v>
<v t="ekr.20231218084055.62"><vh>dumper.show_header</vh></v>
<v t="ekr.20231218084055.63"><vh>dumper.dump_ast &amp; helper</vh>
<v t="ekr.20231218084055.64"><vh>dumper.get_fields</vh></v>
</v>
</v>
<v t="ekr.20231218084055.65"><vh>class Fstringify</vh>
<v t="ekr.20231218084055.66"><vh>fs.fstringify</vh></v>
<v t="ekr.20231218084055.67"><vh>fs.fstringify_file (entry)</vh></v>
<v t="ekr.20231218084055.68"><vh>fs.fstringify_file_diff (entry)</vh></v>
<v t="ekr.20231218084055.69"><vh>fs.fstringify_file_silent (entry)</vh></v>
<v t="ekr.20231218084055.70"><vh>fs.make_fstring &amp; helpers</vh>
<v t="ekr.20231218084055.71"><vh>fs.clean_ws</vh></v>
<v t="ekr.20231218084055.72"><vh>fs.compute_result &amp; helpers</vh>
<v t="ekr.20231218084055.73"><vh>fs.check_back_slashes</vh></v>
<v t="ekr.20231218084055.74"><vh>fs.change_quotes</vh></v>
</v>
<v t="ekr.20231218084055.75"><vh>fs.munge_spec</vh></v>
<v t="ekr.20231218084055.76"><vh>fs.scan_format_string</vh></v>
<v t="ekr.20231218084055.77"><vh>fs.scan_rhs</vh></v>
<v t="ekr.20231218084055.78"><vh>fs.substitute_values</vh></v>
</v>
<v t="ekr.20231218084055.79"><vh>fs.message</vh></v>
<v t="ekr.20231218084055.80"><vh>fs.replace</vh></v>
</v>
<v t="ekr.20231218084055.81"><vh>class Orange</vh>
<v t="ekr.20231218084055.82"><vh>orange.ctor</vh></v>
<v t="ekr.20231218084055.83"><vh>orange.push_state</vh></v>
<v t="ekr.20231218084055.84"><vh>orange: Entries</vh>
<v t="ekr.20231218084055.85"><vh>orange.beautify (main token loop)</vh></v>
<v t="ekr.20231218084055.86"><vh>orange.beautify_file (entry)</vh></v>
<v t="ekr.20231218084055.87"><vh>orange.beautify_file_diff (entry)</vh></v>
</v>
<v t="ekr.20231218084055.88"><vh>orange: Input token handlers</vh>
<v t="ekr.20231218084055.89"><vh>orange.do_comment</vh></v>
<v t="ekr.20231218084055.90"><vh>orange.do_encoding</vh></v>
<v t="ekr.20231218084055.91"><vh>orange.do_endmarker</vh></v>
<v t="ekr.20231218084055.92"><vh>orange.do_fstring_start &amp; continue_fstring</vh></v>
<v t="ekr.20231218084055.93"><vh>orange.do_indent &amp; do_dedent &amp; helper</vh>
<v t="ekr.20231218084055.94"><vh>orange.handle_dedent_after_class_or_def</vh></v>
</v>
<v t="ekr.20231218084055.95"><vh>orange.do_name</vh></v>
<v t="ekr.20231218084055.96"><vh>orange.do_newline &amp; do_nl</vh></v>
<v t="ekr.20231218084055.97"><vh>orange.do_number</vh></v>
<v t="ekr.20231218084055.98"><vh>orange.do_op &amp; helper</vh>
<v t="ekr.20231218084055.99"><vh>orange.do_equal_op</vh></v>
</v>
<v t="ekr.20231218084055.100"><vh>orange.do_string</vh></v>
<v t="ekr.20231218084055.101"><vh>orange.do_verbatim</vh></v>
<v t="ekr.20231218084055.102"><vh>orange.do_ws</vh></v>
</v>
<v t="ekr.20231218084055.103"><vh>orange: Output token generators</vh>
<v t="ekr.20231218084055.104"><vh>orange.add_line_end</vh></v>
<v t="ekr.20231218084055.105"><vh>orange.add_token</vh></v>
<v t="ekr.20231218084055.106"><vh>orange.blank</vh></v>
<v t="ekr.20231218084055.107"><vh>orange.blank_lines (black only)</vh></v>
<v t="ekr.20231218084055.108"><vh>orange.clean</vh></v>
<v t="ekr.20231218084055.109"><vh>orange.clean_blank_lines</vh></v>
<v t="ekr.20231218084055.110"><vh>orange.colon</vh></v>
<v t="ekr.20231218084055.111"><vh>orange.line_end</vh></v>
<v t="ekr.20231218084055.112"><vh>orange.line_indent</vh></v>
<v t="ekr.20231218084055.113"><vh>orange.lt &amp; rt</vh>
<v t="ekr.20231218084055.114"><vh>orange.lt</vh></v>
<v t="ekr.20231218084055.115"><vh>orange.rt</vh></v>
</v>
<v t="ekr.20231218084055.116"><vh>orange.possible_unary_op &amp; unary_op</vh></v>
<v t="ekr.20231218084055.117"><vh>orange.star_op</vh></v>
<v t="ekr.20231218084055.118"><vh>orange.star_star_op</vh></v>
<v t="ekr.20231218084055.119"><vh>orange.word &amp; word_op</vh></v>
</v>
<v t="ekr.20231218084055.120"><vh>orange: Split/join</vh>
<v t="ekr.20231218084055.121"><vh>orange.split_line &amp; helpers</vh>
<v t="ekr.20231218084055.122"><vh>orange.append_tail</vh></v>
<v t="ekr.20231218084055.123"><vh>orange.find_prev_line</vh></v>
<v t="ekr.20231218084055.124"><vh>orange.find_line_prefix</vh></v>
</v>
<v t="ekr.20231218084055.125"><vh>orange.join_lines</vh></v>
</v>
</v>
<v t="ekr.20231218084055.126"><vh>class ParseState</vh></v>
<v t="ekr.20231218084055.127"><vh>class ReassignTokens</vh>
<v t="ekr.20231218084055.128"><vh>reassign.reassign</vh></v>
<v t="ekr.20231218084055.129"><vh>reassign.visit_call</vh></v>
</v>
<v t="ekr.20231218084055.130"><vh>class Token</vh>
<v t="ekr.20231218084055.131"><vh>token.brief_dump</vh></v>
<v t="ekr.20231218084055.132"><vh>token.dump</vh></v>
<v t="ekr.20231218084055.133"><vh>token.dump_header</vh></v>
<v t="ekr.20231218084055.134"><vh>token.error_dump</vh></v>
<v t="ekr.20231218084055.135"><vh>token.show_val</vh></v>
</v>
<v t="ekr.20231218084055.136"><vh>class Tokenizer</vh>
<v t="ekr.20231218084055.137"><vh>tokenizer.add_token</vh></v>
<v t="ekr.20231218084055.138"><vh>tokenizer.check_results</vh></v>
<v t="ekr.20231218084055.139"><vh>tokenizer.create_input_tokens</vh></v>
<v t="ekr.20231218084055.140"><vh>tokenizer.do_token (the gem)</vh></v>
</v>
<v t="ekr.20231218084055.141"><vh>class TokenOrderGenerator</vh>
<v t="ekr.20231218084055.142"><vh>tog: Init...</vh>
<v t="ekr.20231218084055.143"><vh>tog.balance_tokens</vh></v>
<v t="ekr.20231218084055.144"><vh>tog.create_links (inits all ivars)</vh></v>
<v t="ekr.20231218084055.145"><vh>tog.init_from_file</vh></v>
<v t="ekr.20231218084055.146"><vh>tog.init_from_string</vh></v>
</v>
<v t="ekr.20231218084055.147"><vh>tog: synchronizer...</vh>
<v t="ekr.20231218084055.148"><vh>tog.find_next_significant_token</vh></v>
<v t="ekr.20231218084055.149"><vh>tog.set_links</vh></v>
<v t="ekr.20231218084055.150"><vh>tog.name</vh></v>
<v t="ekr.20231218084055.151"><vh>tog.op</vh></v>
<v t="ekr.20231218084055.152"><vh>tog.token</vh></v>
<v t="ekr.20231218084055.153"><vh>tog.string_helper &amp; helpers</vh>
<v t="ekr.20231218084055.154"><vh>tog.sync_to_kind</vh></v>
<v t="ekr.20231218084055.155"><vh>tog.find_next_non_ws_token</vh></v>
</v>
</v>
<v t="ekr.20231218084055.156"><vh>tog: Traversal...</vh>
<v t="ekr.20231218084055.157"><vh>tog.enter_node</vh></v>
<v t="ekr.20231218084055.158"><vh>tog.leave_node</vh></v>
<v t="ekr.20231218084055.159"><vh>tog.visit</vh></v>
</v>
<v t="ekr.20231218084055.160"><vh>tog: Visitors...</vh>
<v t="ekr.20231218084055.161"><vh> tog.keyword: not called!</vh></v>
<v t="ekr.20231218084055.162"><vh>tog: Contexts</vh>
<v t="ekr.20231218084055.163"><vh> tog.arg</vh></v>
<v t="ekr.20231218084055.164"><vh> tog.arguments</vh></v>
<v t="ekr.20231218084055.165"><vh>tog.AsyncFunctionDef</vh></v>
<v t="ekr.20231218084055.166"><vh>tog.ClassDef</vh></v>
<v t="ekr.20231218084055.167"><vh>tog.FunctionDef</vh></v>
<v t="ekr.20231218084055.168"><vh>tog.Interactive</vh></v>
<v t="ekr.20231218084055.169"><vh>tog.Lambda</vh></v>
<v t="ekr.20231218084055.170"><vh>tog.Module</vh></v>
</v>
<v t="ekr.20231218084055.171"><vh>tog: Expressions</vh>
<v t="ekr.20231218084055.172"><vh>tog.Expr</vh></v>
<v t="ekr.20231218084055.173"><vh>tog.Expression</vh></v>
<v t="ekr.20231218084055.174"><vh>tog.GeneratorExp</vh></v>
<v t="ekr.20231218084055.175"><vh>tog.NamedExpr</vh></v>
</v>
<v t="ekr.20231218084055.176"><vh>tog: Operands</vh>
<v t="ekr.20231218084055.177"><vh>tog.Attribute</vh></v>
<v t="ekr.20231218084055.178"><vh>tog.Bytes</vh></v>
<v t="ekr.20231218084055.179"><vh>tog.comprehension</vh></v>
<v t="ekr.20231218084055.180"><vh>tog.Constant</vh></v>
<v t="ekr.20231218084055.181"><vh>tog.Dict</vh></v>
<v t="ekr.20231218084055.182"><vh>tog.DictComp</vh></v>
<v t="ekr.20231218084055.183"><vh>tog.Ellipsis</vh></v>
<v t="ekr.20231218084055.184"><vh>tog.ExtSlice</vh></v>
<v t="ekr.20231218084055.185"><vh>tog.FormattedValue</vh></v>
<v t="ekr.20231218084055.186"><vh>tog.Index</vh></v>
<v t="ekr.20231218084055.187"><vh>tog.JoinedStr</vh></v>
<v t="ekr.20231218084055.188"><vh>tog.List</vh></v>
<v t="ekr.20231218084055.189"><vh>tog.ListComp</vh></v>
<v t="ekr.20231218084055.190"><vh>tog.Name</vh></v>
<v t="ekr.20231218084055.191"><vh>tog.Set</vh></v>
<v t="ekr.20231218084055.192"><vh>tog.SetComp</vh></v>
<v t="ekr.20231218084055.193"><vh>tog.Slice</vh></v>
<v t="ekr.20231218084055.194"><vh>tog.Str (deprecated)</vh></v>
<v t="ekr.20231218084055.195"><vh>tog.Subscript</vh></v>
<v t="ekr.20231218084055.196"><vh>tog.Tuple</vh></v>
</v>
<v t="ekr.20231218084055.197"><vh>tog: Operators</vh>
<v t="ekr.20231218084055.198"><vh>tog.BinOp</vh></v>
<v t="ekr.20231218084055.199"><vh>tog.BoolOp</vh></v>
<v t="ekr.20231218084055.200"><vh>tog.Compare</vh></v>
<v t="ekr.20231218084055.201"><vh>tog.UnaryOp</vh></v>
<v t="ekr.20231218084055.202"><vh>tog.IfExp (ternary operator)</vh></v>
</v>
<v t="ekr.20231218084055.203"><vh>tog: Statements</vh>
<v t="ekr.20231218084055.204"><vh> tog.Starred</vh></v>
<v t="ekr.20231218084055.205"><vh>tog.AnnAssign</vh></v>
<v t="ekr.20231218084055.206"><vh>tog.Assert</vh></v>
<v t="ekr.20231218084055.207"><vh>tog.Assign</vh></v>
<v t="ekr.20231218084055.208"><vh>tog.AsyncFor</vh></v>
<v t="ekr.20231218084055.209"><vh>tog.AsyncWith</vh></v>
<v t="ekr.20231218084055.210"><vh>tog.AugAssign</vh></v>
<v t="ekr.20231218084055.211"><vh>tog.Await</vh></v>
<v t="ekr.20231218084055.212"><vh>tog.Break</vh></v>
<v t="ekr.20231218084055.213"><vh>tog.Call &amp; helpers</vh>
<v t="ekr.20231218084055.214"><vh>tog.arg_helper</vh></v>
<v t="ekr.20231218084055.215"><vh>tog.handle_call_arguments</vh></v>
</v>
<v t="ekr.20231218084055.216"><vh>tog.Continue</vh></v>
<v t="ekr.20231218084055.217"><vh>tog.Delete</vh></v>
<v t="ekr.20231218084055.218"><vh>tog.ExceptHandler</vh></v>
<v t="ekr.20231218084055.219"><vh>tog.For</vh></v>
<v t="ekr.20231218084055.220"><vh>tog.Global</vh></v>
<v t="ekr.20231218084055.221"><vh>tog.If &amp; helpers</vh>
<v t="ekr.20231218084055.222"><vh>&lt;&lt; do_If docstring &gt;&gt;</vh></v>
</v>
<v t="ekr.20231218084055.223"><vh>tog.Import &amp; helper</vh></v>
<v t="ekr.20231218084055.224"><vh>tog.ImportFrom</vh></v>
<v t="ekr.20231218084055.225"><vh>tog.Match* (Python 3.10+)</vh>
<v t="ekr.20231218084055.226"><vh>tog.match_case</vh></v>
<v t="ekr.20231218084055.227"><vh>tog.MatchAs</vh></v>
<v t="ekr.20231218084055.228"><vh>tog.MatchClass</vh></v>
<v t="ekr.20231218084055.229"><vh>tog.MatchMapping</vh></v>
<v t="ekr.20231218084055.230"><vh>tog.MatchOr</vh></v>
<v t="ekr.20231218084055.231"><vh>tog.MatchSequence</vh></v>
<v t="ekr.20231218084055.232"><vh>tog.MatchSingleton</vh></v>
<v t="ekr.20231218084055.233"><vh>tog.MatchStar</vh></v>
<v t="ekr.20231218084055.234"><vh>tog.MatchValue</vh></v>
</v>
<v t="ekr.20231218084055.235"><vh>tog.Nonlocal</vh></v>
<v t="ekr.20231218084055.236"><vh>tog.Pass</vh></v>
<v t="ekr.20231218084055.237"><vh>tog.Raise</vh></v>
<v t="ekr.20231218084055.238"><vh>tog.Return</vh></v>
<v t="ekr.20231218084055.239"><vh>tog.Try</vh></v>
<v t="ekr.20231218084055.240"><vh>tog.TryStar</vh></v>
<v t="ekr.20231218084055.241"><vh>tog.While</vh></v>
<v t="ekr.20231218084055.242"><vh>tog.With</vh></v>
<v t="ekr.20231218084055.243"><vh>tog.Yield</vh></v>
<v t="ekr.20231218084055.244"><vh>tog.YieldFrom</vh></v>
</v>
<v t="ekr.20231218084055.245"><vh>tog: Types</vh>
<v t="ekr.20231218084055.246"><vh>tog.ParamSpec</vh></v>
<v t="ekr.20231218084055.247"><vh>tog.TypeAlias</vh></v>
<v t="ekr.20231218084055.248"><vh>tog.TypeVar</vh></v>
<v t="ekr.20231218084055.249"><vh>tog.TypeVarTuple</vh></v>
</v>
</v>
</v>
</v>
<v t="ekr.20231218084055.250"><vh>function: main (leoAst.py)</vh></v>
</v>
<v t="ekr.20231218142937.1"><vh>@@edit ../rust/orange/cargo.toml</vh></v>
<v t="ekr.20231120070819.1"><vh>@@edit ../rust/orange/src/main.rs</vh></v>
<v t="ekr.20231226055415.1"><vh>@@file ../rust/orange/src/settings.rs</vh></v>
</v>
</v>
<v t="ekr.20201012111545.1"><vh>Plugins</vh>
<v t="ekr.20090430075506.3"><vh>@file ../plugins/leoPluginNotes.txt</vh></v>
<v t="EKR.20040517090508"><vh>Enable plugins using @enabled-plugins nodes</vh></v>
<v t="ekr.20050303051035"><vh>Templates</vh>
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
<v t="ekr.20091118065749.5261"><vh>@file ../plugins/ctagscompleter.py</vh></v>
</v>
<v t="edream.110203113231.667"><vh>Commands &amp; directives</vh>
<v t="edream.110203113231.741"><vh>@file ../plugins/add_directives.py</vh></v>
<v t="ekr.20101110084839.5682"><vh>@file ../plugins/bzr_qcommands.py</vh></v>
<v t="EKR.20040517080049.1"><vh>@file ../plugins/empty_leo_file.py</vh></v>
<v t="edream.110203113231.669"><vh>@file ../plugins/import_cisco_config.py</vh></v>
<v t="ekr.20101110092851.5812"><vh>@file ../plugins/initinclass.py</vh></v>
<v t="ekr.20101110091234.5700"><vh>@file ../plugins/leo_interface.py</vh></v>
<v t="ekr.20040419105219"><vh>@file ../plugins/lineNumbers.py</vh></v>
<v t="ekr.20040916084945"><vh>@file ../plugins/macros.py</vh></v>
<v t="edream.110203113231.724"><vh>@file ../plugins/mod_autosave.py</vh></v>
<v t="ekr.20050301083306"><vh>@file ../plugins/mod_read_dir_outline.py</vh></v>
<v t="edream.110203113231.727"><vh>@file ../plugins/mod_timestamp.py</vh></v>
<v t="TL.20090225102340.32"><vh>@file ../plugins/nodeActions.py</vh></v>
<v t="edream.110203113231.720"><vh>@file ../plugins/outline_export.py</vh></v>
<v t="danr7.20060912105041.1"><vh>@file ../plugins/paste_as_headlines.py</vh></v>
<v t="ekr.20081214160729.1"><vh>@file ../plugins/setHomeDirectory.py</vh></v>
<v t="ajones.20070122160142"><vh>@file ../plugins/textnode.py</vh></v>
<v t="danr7.20061010105952.1"><vh>@file ../plugins/word_count.py</vh></v>
</v>
<v t="edream.110203113231.729"><vh>Debugging</vh>
<v t="ekr.20101110091234.5689"><vh>@file ../plugins/debugger_pudb.py</vh></v>
<v t="edream.110203113231.730"><vh>@file ../plugins/dump_globals.py</vh></v>
<v t="edream.110203113231.732"><vh>@file ../plugins/enable_gc.py</vh></v>
<v t="edream.110203113231.734"><vh>@file ../plugins/quit_leo.py</vh></v>
<v t="edream.110203113231.735"><vh>@file ../plugins/trace_gc_plugin.py</vh></v>
<v t="edream.110203113231.738"><vh>@file ../plugins/trace_tags.py</vh></v>
</v>
<v t="ekr.20041030092101"><vh>Dyna plugins by e</vh></v>
<v t="ekr.20040722141148"><vh>Examples</vh>
<v t="ekr.20040828105233"><vh>@file ../plugins/examples/chinese_menu.py</vh></v>
<v t="EKR.20040517080202.3"><vh>@file ../plugins/examples/french_fm.py</vh></v>
<v t="edream.110203113231.916"><vh>@file ../plugins/examples/override_classes.py</vh></v>
<v t="edream.110203113231.919"><vh>@file ../plugins/examples/override_commands.py</vh></v>
<v t="ekr.20060621123339"><vh>@file ../plugins/examples/print_cp.py</vh></v>
<v t="edream.110203113231.921"><vh>@file ../plugins/examples/redefine_put.py</vh></v>
<v t="ekr.20180119164431.1"><vh>@file ../plugins/patch_python_colorizer.py</vh></v>
<v t="ekr.20210329114352.1"><vh>@file ../plugins/example_rst_filter.py</vh></v>
</v>
<v t="ekr.20101110150056.9457"><vh>Experimental/Obsolete</vh>
<v t="tbrown.20081223111325.3"><vh>@file ../plugins/backlink.py</vh></v>
<v t="ekr.20090704103932.5160"><vh>@file ../plugins/leo_pdf.py</vh></v>
<v t="danr7.20060902083957"><vh>@file ../plugins/leo_to_rtf.py</vh></v>
<v t="ekr.20040205071616"><vh>@file ../plugins/mnplugins.py</vh></v>
<v t="ekr.20101110094759.5843"><vh>@file ../plugins/mod_speedups.py</vh></v>
<v t="tbrown.20070117104409"><vh>@file ../plugins/quickMove.py</vh></v>
<v t="ekr.20040910070811.1"><vh>@file ../plugins/run_nodes.py</vh></v>
<v t="ekr.20100103093121.5339"><vh>@file ../plugins/stickynotes_plus.py</vh></v>
<v t="ekr.20040331071919"><vh>Leo to AsciiDoc</vh>
<v t="ekr.20101110093449.5822"><vh>@file ../plugins/mod_leo2ascd.py</vh></v>
<v t="ekr.20101110150056.9445"><vh>@file ../plugins/mod_leo2ascd.txt</vh></v>
</v>
</v>
<v t="EKR.20040517075715"><vh>External programs</vh>
<v t="ekr.20110125103904.12504"><vh>@file ../plugins/gitarchive.py</vh></v>
<v t="EKR.20040517080049.4"><vh>@file ../plugins/open_shell.py</vh></v>
<v t="ville.20090503124249.1"><vh>@file ../plugins/tomboy_import.py</vh></v>
<v t="EKR.20040517075715.10"><vh>@file ../plugins/vim.py</vh></v>
<v t="EKR.20040517075715.12"><vh>@file ../plugins/xemacs.py</vh></v>
<v t="EKR.20040517075715.13"><vh>Word export</vh>
<v t="EKR.20040517075715.14"><vh>@file ../plugins/word_export.py</vh></v>
<v t="EKR.20040517075715.20"><vh>@file-nosent ../plugins/word_export.ini</vh></v>
</v>
</v>
<v t="edream.110203113231.872"><vh>Files and nodes</vh>
<v t="tbrown.20080613095157.2"><vh>@file ../plugins/active_path.py</vh></v>
<v t="edream.110203113231.873"><vh>@file ../plugins/at_folder.py</vh></v>
<v t="ekr.20040915085351"><vh>@file ../plugins/at_produce.py</vh></v>
<v t="ktenney.20041211072654.1"><vh>@file ../plugins/at_view.py</vh></v>
<v t="ekr.20170619151859.2"><vh>@file ../plugins/auto_colorize2_0.py</vh></v>
<v t="tbrown.20070322113635"><vh>@file ../plugins/bookmarks.py</vh></v>
<v t="ekr.20060807103814.1"><vh>@file ../plugins/datenodes.py</vh></v>
<v t="ajones.20070122153625"><vh>@file ../plugins/expfolder.py</vh></v>
<v t="ekr.20040915105758.13"><vh>@file ../plugins/FileActions.py</vh></v>
<v t="ekr.20110110105526.5463"><vh>@file ../plugins/ftp.py</vh></v>
<v t="tbrown.20091214233510.5347"><vh>@file ../plugins/geotag.py</vh></v>
<v t="tbrown.20100228141752.5691"><vh>@file ../plugins/leocursor.py</vh></v>
<v t="ville.20120503224623.3574"><vh>@file ../plugins/leomylyn.py</vh></v>
<v t="ekr.20101110092851.5742"><vh>@file ../plugins/leoOPML.py</vh></v>
<v t="dan.20090217132953.1"><vh>@file ../plugins/mime.py</vh></v>
<v t="mork.20041018204908.1"><vh>@file ../plugins/multifile.py</vh></v>
<v t="ekr.20040331151007"><vh>@file ../plugins/niceNosent.py</vh></v>
<v t="edream.110203113231.876"><vh>@file ../plugins/read_only_nodes.py</vh></v>
<v t="ekr.20040828103325"><vh>@file ../plugins/startfile.py</vh></v>
<v t="ekr.20130808211520.15893"><vh>@file ../plugins/timestamp.py</vh></v>
<v t="tbrown.20110428144124.29061"><vh>@file ../plugins/xml_edit.py</vh></v>
<v t="mork.20041010095009"><vh>@file ../plugins/xsltWithNodes.py</vh></v>
</v>
<v t="ekr.20181030041436.1"><vh>Gui</vh>
<v t="ekr.20150107090324.1"><vh>@file ../plugins/cursesGui.py</vh></v>
<v t="ekr.20170419092835.1"><vh>@file ../plugins/cursesGui2.py</vh></v>
<v t="ekr.20181103094900.1"><vh>@file ../plugins/leoflexx.py</vh></v>
<v t="peckj.20150428142633.1"><vh>@file ../plugins/python_terminal.py</vh></v>
</v>
<v t="ekr.20140723122936.17925"><vh>Importer plugins</vh>
<v t="ekr.20140723122936.18139"><vh>@file ../plugins/importers/__init__.py</vh></v>
<v t="ekr.20230529075138.1"><vh>@file ../plugins/importers/base_importer.py</vh></v>
<v t="ekr.20140723122936.17926"><vh>@file ../plugins/importers/c.py</vh></v>
<v t="ekr.20160505094722.1"><vh>@file ../plugins/importers/coffeescript.py</vh></v>
<v t="ekr.20140723122936.18140"><vh>@file ../plugins/importers/csharp.py</vh></v>
<v t="ekr.20200619141135.1"><vh>@file ../plugins/importers/cython.py</vh></v>
<v t="ekr.20141116100154.1"><vh>@file ../plugins/importers/dart.py</vh></v>
<v t="ekr.20140723122936.18141"><vh>@file ../plugins/importers/elisp.py</vh></v>
<v t="ekr.20140723122936.18138"><vh>@file ../plugins/importers/html.py</vh></v>
<v t="ekr.20140723122936.18142"><vh>@file ../plugins/importers/ini.py</vh></v>
<v t="ekr.20140723122936.18143"><vh>@file ../plugins/importers/java.py</vh></v>
<v t="ekr.20140723122936.18144"><vh>@file ../plugins/importers/javascript.py</vh></v>
<v t="ekr.20140723122936.18151"><vh>@file ../plugins/importers/leo_rst.py</vh></v>
<v t="ekr.20170530024520.2"><vh>@file ../plugins/importers/lua.py</vh></v>
<v t="ekr.20140725190808.18066"><vh>@file ../plugins/importers/markdown.py</vh></v>
<v t="ekr.20140723122936.18146"><vh>@file ../plugins/importers/org.py</vh></v>
<v t="ekr.20140723122936.18150"><vh>@file ../plugins/importers/otl.py</vh></v>
<v t="ekr.20140723122936.18147"><vh>@file ../plugins/importers/pascal.py</vh></v>
<v t="ekr.20161027100313.1"><vh>@file ../plugins/importers/perl.py</vh></v>
<v t="ekr.20140723122936.18148"><vh>@file ../plugins/importers/php.py</vh></v>
<v t="ekr.20211209153303.1"><vh>@file ../plugins/importers/python.py</vh></v>
<v t="ekr.20200316100818.1"><vh>@file ../plugins/importers/rust.py</vh></v>
<v t="ekr.20231012140553.1"><vh>@file ../plugins/importers/scheme.py</vh></v>
<v t="ekr.20170615153639.2"><vh>@file ../plugins/importers/tcl.py</vh></v>
<v t="ekr.20180201203240.2"><vh>@file ../plugins/importers/treepad.py</vh></v>
<v t="ekr.20140723122936.18152"><vh>@file ../plugins/importers/typescript.py</vh></v>
<v t="ekr.20140723122936.18137"><vh>@file ../plugins/importers/xml.py</vh></v>
</v>
<v t="ekr.20180504192522.1"><vh>leo_babel</vh>
<v t="ekr.20230624114517.1"><vh>@clean ../plugins/leo_babel/__init__.py</vh></v>
<v t="ekr.20180504191650.36"><vh>examples</vh>
<v t="bob.20170716135108.2"><vh>@file ../plugins/leo_babel/examples/slowOut.py</vh></v>
<v t="bob.20170716135108.3"><vh>@file ../plugins/leo_babel/examples/slowOutNoFlush.py</vh></v>
</v>
<v t="ekr.20180504191650.42"><vh>tests</vh>
<v t="ekr.20180504191650.68"><vh>@clean ../plugins/leo_babel/tests/__init__.py</vh></v>
<v t="bob.20180206123613.1"><vh>@file ../plugins/leo_babel/tests/idle_time.py</vh></v>
<v t="bob.20180205135005.1"><vh>@file ../plugins/leo_babel/tests/lib_test.py</vh></v>
<v t="bob.20180125160225.1"><vh>@file ../plugins/leo_babel/tests/tests.py</vh></v>
</v>
</v>
<v t="ekr.20041001210557"><vh>Scripting</vh>
<v t="tbrown.20100226095909.12777"><vh>@file ../plugins/leoscreen.py</vh></v>
<v t="tbrown.20140806084727.30174"><vh>@file ../plugins/livecode.py</vh></v>
<v t="ekr.20060328125248"><vh>@file ../plugins/mod_scripting.py</vh></v>
<v t="edream.110203113231.925"><vh>@file ../plugins/script_io_to_body.py</vh></v>
</v>
<v t="ekr.20120309073937.9878"><vh>Searching</vh>
<v t="ekr.20220823200700.1"><vh>@file ../plugins/leofts.py</vh></v>
<v t="ekr.20120309073748.9872"><vh>@file ../plugins/bigdash.py</vh></v>
<v t="peckj.20140804114520.9427"><vh>@file ../plugins/nodetags.py</vh></v>
<v t="peckj.20131130132659.5964"><vh>@file ../plugins/nodewatch.py</vh></v>
</v>
<v t="ekr.20050111122605"><vh>Servers &amp; web stuff</vh>
<v t="ekr.20170925083314.1"><vh>@file ../plugins/leo_cloud.py</vh></v>
<v t="ekr.20170925083853.1"><vh>@file ../plugins/leo_cloud_server.py</vh></v>
<v t="ville.20110206142055.10640"><vh>@file ../plugins/leofeeds.py</vh></v>
<v t="ville.20110125222411.10536"><vh>@file ../plugins/leomail.py</vh></v>
<v t="ville.20091009202416.10040"><vh>@file ../plugins/leoremote.py</vh></v>
<v t="EKR.20040517080250.1"><vh>@file ../plugins/mod_http.py</vh></v>
<v t="ekr.20131004162848.11444"><vh>@file ../plugins/rss.py</vh></v>
<v t="peckj.20140811080604.9496"><vh>@file ../plugins/sftp.py</vh></v>
<v t="ekr.20210223152423.1"><vh>@file ../plugins/anki.py</vh></v>
</v>
<v t="ekr.20101004082701.5674"><vh>Slideshows, screencasts &amp; screenshots</vh>
<v t="ekr.20170128213103.1"><vh>@file ../plugins/demo.py</vh></v>
<v t="ekr.20211021200745.1"><vh>@file ../scripts/picture_viewer.py</vh></v>
<v t="ekr.20220126054240.1"><vh>@file ../scripts/remove_duplicate_pictures.py</vh></v>
<v t="ekr.20120913110135.10579"><vh>@file ../plugins/screencast.py</vh></v>
<v t="ekr.20101121031443.5330"><vh>@file ../plugins/screenshots.py</vh></v>
<v t="ekr.20060831165821"><vh>@file ../plugins/slideshow.py</vh></v>
</v>
<v t="ekr.20071113084440"><vh>Testing</vh>
<v t="ekr.20080214092357"><vh>@file ../plugins/test/ekr_test.py</vh></v>
<v t="ekr.20050130120433"><vh>@@file ../plugins/test/failed_import.py</vh></v>
<v t="ekr.20071113085315"><vh>@file ../plugins/test/failed_to_load_plugin.py</vh></v>
<v t="ekr.20051016160700"><vh>@file ../plugins/testRegisterCommand.py</vh></v>
</v>
<v t="ekr.20050306081349"><vh>Text formatting</vh>
<v t="timo.20050213160555"><vh>@file ../plugins/bibtex.py</vh></v>
<v t="ekr.20070119094733.1"><vh>@file ../plugins/dtest.py</vh></v>
<v t="ville.20110409151021.5699"><vh>@file ../plugins/jinjarender.py</vh></v>
<v t="danr7.20060902215215.1"><vh>@file ../plugins/leo_to_html.py</vh></v>
<v t="tbrown.20130930160706.23451"><vh>@file ../plugins/markup_inline.py</vh></v>
<v t="vitalije.20180804172140.1"><vh>@file ../plugins/md_docer.py</vh></v>
<v t="peckj.20140113150237.7083"><vh>@file ../plugins/nodediff.py</vh></v>
<v t="tbrown.20130813134319.11942"><vh>@file ../plugins/richtext.py</vh></v>
<v t="ekr.20170217164004.1"><vh>@file ../plugins/tables.py</vh></v>
</v>
<v t="ekr.20121126102050.10134"><vh>Threading</vh>
<v t="ekr.20121126095734.12418"><vh>@file ../plugins/threadutil.py</vh></v>
</v>
<v t="ekr.20040915073259"><vh>User interface</vh>
<v t="ekr.20101110150056.9453"><vh>Qt only plugins</vh>
<v t="tbrown.20091029123555.5319"><vh>@file ../plugins/attrib_edit.py</vh></v>
<v t="ville.20090310191936.10"><vh>@file ../plugins/colorize_headlines.py</vh></v>
<v t="ekr.20090701111504.5294"><vh>@file ../plugins/contextmenu.py</vh></v>
<v t="tom.20210613135525.1"><vh>@file ../plugins/freewin.py</vh></v>
<v t="tbrown.20090206153748.1"><vh>@file ../plugins/graphcanvas.py</vh></v>
<v t="ville.20090518182905.5419"><vh>@file ../plugins/nav_qt.py</vh></v>
<v t="ville.20120604212857.4215"><vh>@file ../plugins/notebook.py</vh></v>
<v t="ekr.20090622063842.5264"><vh>@file ../plugins/projectwizard.py</vh></v>
<v t="ekr.20160928073518.1"><vh>@file ../plugins/pyplot_backend.py</vh></v>
<v t="ville.20090314215508.4"><vh>@file ../plugins/quicksearch.py</vh></v>
<v t="tbrown.20130420091241.44181"><vh>@file ../plugins/screen_capture.py</vh></v>
<v t="ville.20090815203828.5235"><vh>@file ../plugins/spydershell.py</vh></v>
<v t="ekr.20100103093121.5329"><vh>@file ../plugins/stickynotes.py</vh></v>
<v t="tbrown.20090119215428.2"><vh>@file ../plugins/todo.py</vh></v>
<v t="ville.20110403115003.10348"><vh>@file ../plugins/valuespace.py</vh></v>
<v t="tbrown.20100318101414.5990"><vh>@file ../plugins/viewrendered.py</vh></v>
<v t="TomP.20191215195433.1"><vh>@file ../plugins/viewrendered3.py</vh></v>
</v>
<v t="ekr.20060328125925"><vh>@file ../plugins/chapter_hoist.py</vh></v>
<v t="ville.20110115234843.8742"><vh>@file ../plugins/dragdropgoodies.py</vh></v>
<v t="vitalije.20190928154420.1"><vh>@file ../plugins/history_tracer.py</vh></v>
<v t="tbrown.20090513125417.5244"><vh>@file ../plugins/interact.py</vh></v>
<v t="vitalije.20170727201534.1"><vh>@file ../plugins/line_numbering.py</vh></v>
<v t="ekr.20040915073259.1"><vh>@file ../plugins/maximizeNewWindows.py</vh></v>
<v t="ekr.20101110093301.5818"><vh>@file ../plugins/mod_framesize.py</vh></v>
<v t="EKR.20040517080555.2"><vh>@file ../plugins/plugins_menu.py</vh></v>
<v t="ekr.20160519123329.1"><vh>@file ../plugins/QNCalendarWidget.py</vh></v>
<v t="edream.110203113231.924"><vh>@file ../plugins/redirect_to_log.py</vh></v>
<v t="tom.20230424140347.1"><vh>@file ../plugins/rpcalc.py</vh></v>
<v t="ville.20110304230157.6513"><vh>@file ../plugins/systray.py</vh></v>
<v t="tbrown.20141101114322.1"><vh>@file ../plugins/wikiview.py</vh></v>
<v t="ekr.20181004143535.1"><vh>@file ../plugins/xdb_pane.py</vh></v>
<v t="ekr.20101110095202.5882"><vh>@file ../plugins/zenity_file_dialogs.py</vh></v>
</v>
<v t="ekr.20140726091031.18071"><vh>Writer plugins</vh>
<v t="ekr.20140726091031.18152"><vh>@file ../plugins/writers/__init__.py</vh></v>
<v t="ekr.20140726091031.18143"><vh>@file ../plugins/writers/basewriter.py</vh></v>
<v t="ekr.20141116100154.2"><vh>@file ../plugins/writers/dart.py</vh></v>
<v t="ekr.20140726091031.18080"><vh>@file ../plugins/writers/leo_rst.py</vh></v>
<v t="ekr.20140726091031.18073"><vh>@file ../plugins/writers/markdown.py</vh></v>
<v t="ekr.20140726091031.18079"><vh>@file ../plugins/writers/org.py</vh></v>
<v t="ekr.20140726091031.18078"><vh>@file ../plugins/writers/otl.py</vh></v>
<v t="ekr.20180202053206.1"><vh>@file ../plugins/writers/treepad.py</vh></v>
</v>
</v>
<v t="ekr.20110605121601.17862"><vh>Qt gui</vh>
<v t="ekr.20171031111403.1"><vh>Leo Edit Pane</vh>
<v t="tbrown.20171029210211.1"><vh>@file ../plugins/editpane/clicky_splitter.py</vh></v>
<v t="ekr.20211210102459.1"><vh>@file ../plugins/editpane/csvedit.py</vh></v>
<v t="tbrown.20171028115144.6"><vh>@file ../plugins/editpane/editpane.py</vh></v>
<v t="tbrown.20171028115144.5"><vh>@file ../plugins/editpane/leotextedit.py</vh></v>
<v t="tbrown.20171028115144.4"><vh>@file ../plugins/editpane/markdownview.py</vh></v>
<v t="tbrown.20171028115144.3"><vh>@file ../plugins/editpane/pandownview.py</vh></v>
<v t="tbrown.20171028115144.2"><vh>@file ../plugins/editpane/plaintextedit.py</vh></v>
<v t="tbrown.20171028115144.1"><vh>@file ../plugins/editpane/plaintextview.py</vh></v>
<v t="tbrown.20171028115143.3"><vh>@file ../plugins/editpane/vanillascintilla.py</vh></v>
<v t="tbrown.20171028115143.2"><vh>@file ../plugins/editpane/webengineview.py</vh></v>
<v t="tbrown.20171028115143.1"><vh>@file ../plugins/editpane/webkitview.py</vh></v>
<v t="tbrown.20171028115144.8"><vh>@file ../plugins/editpane/__init__.py</vh></v>
<v t="tbrown.20171028115541.1"><vh>@file signal_manager.py</vh></v>
</v>
<v t="ekr.20120419093256.10048"><vh>@file ../plugins/free_layout.py</vh></v>
<v t="ekr.20110605121601.17954"><vh>@file ../plugins/nested_splitter.py</vh></v>
<v t="ekr.20221019064053.1"><vh>@file ../plugins/pane_commands.py</vh></v>
<v t="ekr.20110605121601.17996"><vh>@file ../plugins/qt_commands.py</vh></v>
<v t="ekr.20140907103315.18766"><vh>@file ../plugins/qt_events.py</vh></v>
<v t="ekr.20140907123524.18774"><vh>@file ../plugins/qt_frame.py</vh></v>
<v t="ekr.20140907085654.18699"><vh>@file ../plugins/qt_gui.py</vh></v>
<v t="ekr.20140907103315.18777"><vh>@file ../plugins/qt_idle_time.py</vh></v>
<v t="ekr.20140907123524.18777"><vh>@file ../plugins/qt_quickheadlines.py</vh></v>
<v t="ekr.20140831085423.18598"><vh>@file ../plugins/qt_text.py</vh></v>
<v t="ekr.20140907131341.18707"><vh>@file ../plugins/qt_tree.py</vh></v>
<v t="ekr.20110605121601.18002"><vh>@file ../plugins/qtGui.py</vh></v>
<v t="ekr.20161223152017.1"><vh>@edit ../plugins/qt_quicksearch.py</vh></v>
<v t="ekr.20161223152353.1"><vh>@edit ../plugins/qt_quicksearch_sub.py</vh></v>
</v>
<v t="ekr.20221204070905.1"><vh>Script files</vh>
<v t="ekr.20221204072456.1"><vh>@clean ../scripts/beautify-leo.cmd</vh></v>
<v t="ekr.20231114224211.1"><vh>@clean ../scripts/beautify-leo-force.cmd</vh></v>
<v t="ekr.20230115020533.1"><vh>@clean ../scripts/blacken-leo.cmd</vh></v>
<v t="ekr.20221204074235.1"><vh>@clean ../scripts/flake8-leo.cmd</vh></v>
<v t="ekr.20221204071554.1"><vh>@clean ../scripts/full-test-leo.cmd</vh></v>
<v t="ekr.20230206004301.1"><vh>@clean ../scripts/make-leo.cmd</vh></v>
<v t="ekr.20221204071146.1"><vh>@clean ../scripts/mypy-leo.cmd</vh></v>
<v t="ekr.20221204071056.1"><vh>@clean ../scripts/pylint-leo.cmd</vh></v>
<v t="ekr.20221204072154.1"><vh>@clean ../scripts/reindent-leo.cmd</vh></v>
<v t="ekr.20230628105236.1"><vh>@clean ../scripts/ruff-leo.cmd</vh></v>
<v t="ekr.20221201043917.1"><vh>@clean ../scripts/test-leo.cmd</vh></v>
<v t="ekr.20221204071220.1"><vh>@clean ../scripts/test-one-leo.cmd</vh></v>
<v t="ekr.20240119060724.1"><vh>@clean ../scripts/tbo.cmd</vh></v>
</v>
<v t="ekr.20080730161153.8"><vh>Testing</vh>
<v t="ekr.20201129023817.1"><vh>@file leoTest2.py</vh></v>
</v>
<v t="ekr.20201202144529.1"><vh>leo/unittests</vh>
<v t="ekr.20210912064148.1"><vh>in unittests/commands</vh>
<v t="ekr.20210904022712.2"><vh>@file ../unittests/commands/test_checkerCommands.py</vh></v>
<v t="ekr.20230710105542.1"><vh>@file ../unittests/commands/test_commanderFileCommands.py</vh></v>
<v t="ekr.20211013081056.1"><vh>@file ../unittests/commands/test_convertCommands.py</vh></v>
<v t="ekr.20201202144422.1"><vh>@file ../unittests/commands/test_editCommands.py</vh></v>
<v t="ekr.20230705083159.1"><vh>@file ../unittests/commands/test_editFileCommands.py</vh></v>
<v t="ekr.20230802060212.1"><vh>@file ../unittests/commands/test_gotoCommands.py</vh></v>
<v t="ekr.20221113062857.1"><vh>@file ../unittests/commands/test_outlineCommands.py</vh></v>
<v t="ekr.20230916141635.1"><vh>@file ../unittests/commands/test_spellCommands.py</vh></v>
</v>
<v t="ekr.20210912064205.1"><vh>in unittests/core</vh>
<v t="ekr.20210901170451.1"><vh>@file ../unittests/core/test_leoApp.py</vh></v>
<v t="ekr.20210902073413.1"><vh>@file ../unittests/core/test_leoAst.py</vh></v>
<v t="ekr.20210901172411.1"><vh>@file ../unittests/core/test_leoAtFile.py</vh></v>
<v t="ekr.20210903153138.1"><vh>@file ../unittests/core/test_leoBridge.py</vh></v>
<v t="ekr.20210905151702.1"><vh>@file ../unittests/core/test_leoColorizer.py</vh></v>
<v t="ekr.20210903162431.1"><vh>@file ../unittests/core/test_leoCommands.py</vh></v>
<v t="ekr.20230714131540.1"><vh>@file ../unittests/core/test_leoCompare.py</vh></v>
<v t="ekr.20210910073303.1"><vh>@file ../unittests/core/test_leoConfig.py</vh></v>
<v t="ekr.20210911052754.1"><vh>@file ../unittests/core/test_leoExternalFiles.py</vh></v>
<v t="ekr.20210910065135.1"><vh>@file ../unittests/core/test_leoFileCommands.py</vh></v>
<v t="ekr.20210829124658.1"><vh>@file ../unittests/core/test_leoFind.py</vh></v>
<v t="ekr.20210903161742.1"><vh>@file ../unittests/core/test_leoFrame.py</vh></v>
<v t="ekr.20210902164946.1"><vh>@file ../unittests/core/test_leoGlobals.py</vh></v>
<v t="ekr.20220822082042.1"><vh>@file ../unittests/core/test_leoImport.py</vh></v>
<v t="ekr.20210903155556.1"><vh>@file ../unittests/core/test_leoKeys.py</vh></v>
<v t="ekr.20201203042030.1"><vh>@file ../unittests/core/test_leoNodes.py</vh></v>
<v t="ekr.20210908171733.1"><vh>@file ../unittests/core/test_leoPersistence.py</vh></v>
<v t="ekr.20220911163718.1"><vh>@file ../unittests/core/test_leoQt6.py</vh></v>
<v t="ekr.20210902055206.1"><vh>@file ../unittests/core/test_leoRst.py</vh></v>
<v t="ekr.20210820203000.1"><vh>@file ../unittests/core/test_leoserver.py</vh></v>
<v t="ekr.20210902092024.1"><vh>@file ../unittests/core/test_leoShadow.py</vh></v>
<v t="ekr.20230722095455.1"><vh>@file ../unittests/core/test_leoTest2.py</vh></v>
<v t="ekr.20240105151507.1"><vh>@file ../unittests/core/test_leoTokens.py</vh></v>
<v t="ekr.20210906141410.1"><vh>@file ../unittests/core/test_leoUndo.py</vh></v>
<v t="ekr.20210910072917.1"><vh>@file ../unittests/core/test_leoVim.py</vh></v>
</v>
<v t="ekr.20240204082420.1"><vh>in unittests/misc_tests</vh>
<v t="ekr.20230506095312.1"><vh>@file ../unittests/misc_tests/test_design.py</vh></v>
<v t="ekr.20210926044012.1"><vh>@file ../unittests/misc_tests/test_doctests.py</vh></v>
<v t="ekr.20210901140718.1"><vh>@file ../unittests/misc_tests/test_syntax.py</vh></v>
</v>
<v t="ekr.20240204082924.1"><vh>in unittests/plugins</vh>
<v t="ekr.20220812224747.1"><vh>@file ../unittests/plugins/test_writers.py</vh></v>
<v t="ekr.20210907081548.1"><vh>@file ../unittests/plugins/test_plugins.py</vh></v>
<v t="ekr.20210904064440.2"><vh>@file ../unittests/plugins/test_importers.py</vh></v>
<v t="ekr.20210910084607.1"><vh>@file ../unittests/plugins/test_gui.py</vh></v>
</v>
</v>
<v t="ekr.20090802181029.5988"><vh>Version</vh>
<v t="ekr.20090717092906.12765"><vh>@file leoVersion.py</vh></v>
</v>
</v>
</vnodes>
<tnodes>
<t tx="EKR.20040430162943"></t>
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
<t tx="edream.110203113231.667"></t>
<t tx="edream.110203113231.729"></t>
<t tx="edream.110203113231.872">@nocolor-node

These plugins create new kinds of nodes, some of which affect the file system.</t>
<t tx="ekr.20031218072017.2406"># This file contains almost all of Leo's sources.

# See the "About this file" node for important notes.
</t>
<t tx="ekr.20031218072017.2604"></t>
<t tx="ekr.20031218072017.3625">&lt;&lt; about gui classes and gui plugins &gt;&gt;
</t>
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
<t tx="ekr.20041030092101">@Notes by EKR: The dyna plugin is a remarkable body of work by 'e'. Have fun with it.

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

      #
      # Fail fast, right after all imports.
      g.assertUi('qt')  # May raise g.UiTypeException, caught by the plugins manager.

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
<t tx="ekr.20050130120433">"""A plugin to test import problems."""

from leo.core import leoGlobals as g

def onStart(tag,keywords):
    pass

# pylint: disable=unused-import
try:
    import xyzzy
except ImportError:
    g.cantImport('xyzzy',pluginName='failed_import')

def init():
    """Return True if the plugin has loaded successfully."""
    g.registerHandler("start2", onStart)
    g.plugin_signon(__name__)
    return True
</t>
<t tx="ekr.20050303051035">@nocolor-node

The following nodes show recommended style when writing plugins.</t>
<t tx="ekr.20050303051035.2">"""
A docstring describing your plugin and how to use it.
If it's long, you might put it in a separate section.
"""
&lt;&lt; imports &gt;&gt;
@others
@language python
@tabwidth-4
</t>
<t tx="ekr.20050303051035.5">from leo.core import leoGlobals as g

# Whatever other imports your plugins uses.
</t>
<t tx="ekr.20050303051101">def init():
    """Return True if the plugin has loaded successfully."""
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
<t tx="ekr.20050303051222">class pluginController:

    @others</t>
<t tx="ekr.20050303051222.1">def __init__(self,c):

    self.c=c
    # Warning: hook handlers must use keywords.get('c'), NOT self.c.
</t>
<t tx="ekr.20050306071540">def onStart2(tag, keywords):
    """
    A global hook that affects all commanders.
    """

    log=c.frame.log.__class__

    # Replace frame.put with newPut (not shown).
    g.funcToMethod(newPut,log,"put")</t>
<t tx="ekr.20050306071629">"""
A docstring describing your plugin and how to use it.
If it's long, you might put it in a separate section.
"""
&lt;&lt; imports &gt;&gt;
@others
@language python
@tabwidth-4</t>
<t tx="ekr.20050306071629.1">"""
This docstring should be a clear, concise description of what the plugin does
and how to use it.
"""
</t>
<t tx="ekr.20050306071629.3">from leo.core import leoGlobals as g

# Whatever other imports your plugins uses.
</t>
<t tx="ekr.20050306071629.4">def init():
    """Return True if the plugin has loaded successfully."""
    ok=True # This might depend on imports, etc.
    if ok:
        g.registerHandler('start2',onStart2)
    return ok</t>
<t tx="ekr.20050306081349"></t>
<t tx="ekr.20050721093241">@nobeautify
@nocolor

The following are notes for anyone who is interested in writing
alternate gui's for Leo.

Rule 1: Leo's core is (or should be) free of gui-specific code.

Core code calls 'gui wrapper methods' defined by gui-specific classes.
The base classes for these gui-specific classes are in the node
Code--&gt;Gui Base classes.

Rule 2: Gui-specific code should be localized.

The @file nodes contained in the node 'Code--&gt;Gui Tkinter classes' in
leoPy.leo contain all of Leo's Tkinter-specific code. Gui plugins
would typically put all similar code in a single file.

Rule 3: Gui-specific code can call gui methods directly.

There are no restrictions about the code in the gui-specific classes.

Rule 4: Gui-specific classes must implement the 'gui wrapper methods'
specified in the gui base classes.

This is the way that gui-specific classes provide gui-specific
services to Leo's core.

The alternative would be to implement all gui-specific commands
directly in the gui-specific code.  But this would be much more work
than needed.  For example, only a few gui-specific wrappers are needed
to implement all commands that deal with body text.  Implementing each
of these commands 'from scratch' would duplicate a lot of code
unnecessarily.

Using the gui wrapper methods is a bit messy for two reasons:

1. It requires defining enough wrappers (both in the base gui classes
   and subclasses) so that all gui-specific services needed by Leo's
   core are available.  Adding a wrapper to a gui base class involves
   adding it to all gui-specific subclasses.  It's easy to forget to
   add a wrapper.  The gui base class defines all wrappers as a
   function that just calls oops().  This prints a warning that the
   wrapper should be defined in a subclass.

2. The original wrappers assumed Tkinter-like indices.  Wrappers that
   were defined later assume Python indices (see Rule 5 below).  The
   newer style wrappers that use Python indices have 'Python' in their
   name.  Having two sets of wrappers is one of the ugliest features
   of the present code.  I find it hard to remember which wrappers
   exist and what exactly they do :-)

Rule 5: Leo's core should use Python indices, not gui-specific
indices.

Leo's core mostly follows this rule: there may be a few exceptions.

A Python index is an int that runs from 0 (beginning of text) to
len(s) (end of text s).  That is, there are exactly len(s) + 1 valid
indices.  In contrast, Tkinter indices run from "1.0" to "x.y" where
text s has x lines and where the length of the last line is y-1.

Two (recently written) functions in leoGlobals.py support conversions
from Python indices to the row/column indices used by Tkinter.

- g.convertPythonIndexToRowCol converts a Python index to a row/column
  index used by Tkinter.

- g.convertRowColToPythonIndex does the reverse.

Important: the first Tkinter index is '1.0', not '0.0', but the row
returned by g.convertPythonIndexToRowCol is zero based, so the code
that actually creates Tkinter indices from row/col must add 1 to the
row.  Similar remarks apply when going in the reverse direction.
</t>
<t tx="ekr.20051031040240"></t>
<t tx="ekr.20071113084440"># These plugins are for testing Leo's own plugin loading logic.
# There is no reason ever to enable these plugins.</t>
<t tx="ekr.20080412053100.5">@language rest
</t>
<t tx="ekr.20080730161153.8"></t>
<t tx="ekr.20090802181029.5988"></t>
<t tx="ekr.20100103093121.5365"># These are experimental plugins.
</t>
<t tx="ekr.20101004082701.5674"></t>
<t tx="ekr.20101110150056.9453"># Some of the most important recent plugins work only with the Qt gui.
</t>
<t tx="ekr.20101110150056.9457"></t>
<t tx="ekr.20110605121601.17862"># These files are true plugins, but it is more convenient to put them here.
</t>
<t tx="ekr.20120309073937.9878"></t>
<t tx="ekr.20121126102050.10134"></t>
<t tx="ekr.20131121084830.16362">@language python

# Toggle the settings.
g.app.debug_app = not g.app.debug_app
g.app.debug_widgets = not g.app.debug_widgets
# Report the new settings.
print('g.app.debug_app: %s' % g.app.debug_app)
print('g.app.debug_widgets: %s' % g.app.debug_widgets)
</t>
<t tx="ekr.20140723122936.17925"># Leo loads these plugins automatically.  Do not add them to @enabled-plugins nodes.

# These plugins now contain the importer code for all kinds of @auto nodes.
# Each plugin must define a top-level importer_dict dictionary describing the plugin.
@language python
</t>
<t tx="ekr.20140726091031.18071"># Leo loads these plugins automatically.  Do not add them to @enabled-plugins nodes.

# These plugins contain the write code for all kinds of special @auto nodes.
# Each plugin must define a top-level writer_dict dictionary describing the plugin.
@language python
</t>
<t tx="ekr.20140831085423.18630">This outline contains all of Leo's core source code.

Leo's code uses the following conventions throughout:

c:  a commander.
ch: a character.
d:  a dict.
f:  an open file.
fn: a file name.
g:  the leoGlobals module.
i, j, k: indices into a string.
p:  a Position.
s:  a string.
t:  a text widget.
u:  an undoer.
w:  a gui widget.
v:  a Vnode
z:  a local temp.

In more limited contexts, the following conventions apply:

si:     a g.ShortcutInfo object.
ks:     a g.KeyStroke object
stroke: a KeyStroke object.

btw:    leoFrame.BaseTextWrapper
stw:    leoFrame.StringTextWrapper

bqtw:   qt_text.BaseQTextWrapper
lqtb:   qt_text.LeoQTextBrowser
qhlw:   qt_text.QHeadlineWrapper
qmbw:   qt_text.QMinibufferWrapper
qlew:   qt_text.QLineEditWrapper
qsciw:  qt_text.QScintiallaWrapper
qtew:   qt_text.QTextEditWrapper</t>
<t tx="ekr.20140831085423.18631">The following 'official' ivars will always exist:

c.frame                 The frame containing the log,body,tree, etc.
c.frame.body            The body pane.
c.frame.body.widget     The gui widget for the body pane.
c.frame.body.wrapper    The high level interface for the body widget.
c.frame.iconBar         The icon bar.
c.frame.log             The log pane.
c.frame.log.widget      The gui widget for the log pane.
c.frame.log.wrapper     The high-level interface for the log pane.
c.frame.tree            The tree pane.

The following were official ivars that no longer exist:

c.frame.body.bodyCtrl   Use c.frame.body.wrapper instead.
c.frame.log.logCtrl     Use c.frame.log.wrapper instead.
</t>
<t tx="ekr.20140831085423.18639">Here is what you *must know* to understand Leo's core:

1. A **widget** is an actual Qt widget.

Leo's core seldom accesses widgets directly.  Instead...

2. A **wrapper class** defines a standard api that hides the details
   of the underlying gui **text** widgets.

Leo's core uses this api almost exclusively. That is, Leo's core code treats wrappers *as if* they were only text widgets there are!

There is, however, a back door for (hopefully rare!) special cases. All wrapper classes define an official ``widget`` ivar, so core or plugin code can gain access to the real Qt widget using wrapper.widget. Searching for wrapper.widget will find all gui-dependent snippets of code in Leo's core.
</t>
<t tx="ekr.20140902032918.18591">@language rest
@wrap

Leo uses a model/view/controller architecture.

- Controller: The Commands class and its helpers in leoCommands.py and leoEditCommands.py.

- Model: The VNode and Position classes in leoNodes.py.

- View: The gui-independent base classes are in the node "Gui Base Classes". The Qt-Specific subclasses are in the node "Qt gui".

**Important**: The general organization of these classes have changed hardly at all in Leo's 20+ year history.  The reason is that what each class does is fairly obvious.  How the gets the job done may have changed drastically, but *that's an internal implementation detail of the class itself*.  This is the crucial design principle that allows Leo's code to remain stable.  *Classes do not know or meddle in the internal details of other classes*.  As a result, nobody, including EKR, needs to remember internal details.

</t>
<t tx="ekr.20140902155015.18674"></t>
<t tx="ekr.20140916101314.19538">The default language if no @language or @comment is in effect.

Valid values are (case is ignored):

actionscript,c,csharp,css,cweb,elisp,html,java,latex,
pascal,perl,perlpod,php,plain,plsql,python,rapidq,rebol,shell,tcltk.</t>
<t tx="ekr.20150304130753.4">@language xml
&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform"&gt;

&lt;xsl:output method="html" version="1.0" encoding="UTF-8" indent="yes"/&gt;

&lt;!-- The default setting. Not needed unless there is a strip-space element. --&gt;
  &lt;!-- &lt;xsl:preserve-space elements='leo_file nodes t'/&gt; --&gt;

&lt;xsl:template match ='leo_file'&gt;
&lt;html&gt;
  &lt;head&gt;
    &lt;&lt;style&gt;&gt;
    &lt;&lt;scripts&gt;&gt;
  &lt;/head&gt;
  &lt;body&gt;
    &lt;xsl:apply-templates select='tnodes'/&gt;
    &lt;div class="outlinepane"&gt;
      &lt;xsl:apply-templates select='vnodes'/&gt;
    &lt;/div&gt;
    &lt;div class="bodypane"&gt;
      &lt;h1&gt;Body Pane&lt;/h1&gt;
      &lt;pre class="body-text"&gt;body&lt;/pre&gt;
    &lt;/div&gt;
  &lt;/body&gt;
&lt;/html&gt;
&lt;/xsl:template&gt;

&lt;xsl:template match = 'tnodes'&gt;
&lt;div class="tnodes"&gt;
  &lt;xsl:for-each select = 't'&gt;
    &lt;div class="tnode"&gt;
      &lt;xsl:attribute name="id"&gt;&lt;xsl:value-of select='@tx'/&gt;&lt;/xsl:attribute&gt;
      &lt;xsl:value-of select='.'/&gt;
    &lt;/div&gt;
  &lt;/xsl:for-each&gt;
&lt;/div&gt;
&lt;/xsl:template&gt;

&lt;xsl:template match = 'vnodes'&gt;
  &lt;xsl:for-each select = 'v'&gt;
    &lt;xsl:apply-templates select ='.'/&gt;
  &lt;/xsl:for-each&gt;
&lt;/xsl:template&gt;

&lt;xsl:template match='v'&gt;
  &lt;div class="node"&gt;
    &lt;xsl:attribute name="id"&gt;&lt;xsl:value-of select='@t'/&gt;&lt;/xsl:attribute&gt;
    &lt;h1&gt;&lt;xsl:value-of select='vh'/&gt;&lt;/h1&gt;
    &lt;xsl:if test ='./v' &gt;
      &lt;xsl:apply-templates select = 'v'/&gt;
    &lt;/xsl:if&gt;
  &lt;/div&gt;
&lt;/xsl:template&gt;

&lt;/xsl:stylesheet&gt;
</t>
<t tx="ekr.20150413091056.1">"""Warn if leoProjects.txt or leoToDo.txt contain any clones."""

clones,nodes,seen = 0,0,set()
table = (
  '@file ../doc/leoProjects.txt',
  '@file ../doc/leoToDo.txt',
)

def check_clone(c,p0,root):
    """Warn if p appears in any @&lt;file&gt; node outside of root's tree."""
    global nodes,seen
    v = p0.v
    for p in c.all_positions():
        nodes += 1
        if p.v == v:
            # Check *all* ancestors, not just the nearest one.
            for parent in p.self_and_parents():
                nodes += 1
                if parent.isAnyAtFileNode() and parent.v != root.v:
                    if parent.v not in seen:
                        seen.add(parent.v)
                        g.es_print('%s and %s contain clone: %s' % (
                            root.h,parent.h,p0.h))

for h in table:
    root = g.findNodeAnywhere(c,h)
    if root:
        for p in root.self_and_subtree():
            nodes += 1
            if p.isCloned():
                clones += 1
                check_clone(c,p,root)
    else:
        g.es_print('not found',h,color='red')
print('done: %s nodes, %s clones' % (nodes,clones))

@tabwidth -4
@language python
</t>
<t tx="ekr.20150425145248.1">test-one
ctrl-click-at-cursor
execute-script

# python-to-rust
# goto-prev-history-node
# goto-next-history-node
# beautify-files
# expand-all-subheads
# pylint
# backup
# show-commands
# show-bindings
</t>
<t tx="ekr.20150502050609.1">"""
Back up this .leo file.

os.environ['LEO_BACKUP'] must be the path to an existing (writable) directory.
"""
c.backup_helper(sub_dir='leoPy')
</t>
<t tx="ekr.20150507170849.1">g.cls()

print('===== Start =====')

class CreateDecorators:
    """
    A class to create decorators from tables in getPublicCommands.
    
    Note: the node "Found: getPublicCommands" must exist.
    """
    def __init__(self,c,make_changes):
        self.c = c
        self.fixups = self.create_fixups()
        self.n = 0
        self.n_fail = 0
        self.make_changes=make_changes
        self.suppress = [
            'c.frame.body and c.frame.body.addEditor',
            'cls','cloneFindParents','cycleTabFocus',
            'k and k.keyboardQuit',
            'menuShortcutPlaceHolder','removeBlankLines',
            'saveBuffersKillLeo',
        ]
    @others

CreateDecorators(c,make_changes=False).run()
</t>
<t tx="ekr.20150507174711.1">def find_next_clone(self,p):
    v = p.v
    p = p.copy()
    p.moveToThreadNext()
    wrapped = False
    while 1:
        # g.trace(p.v,p.h)
        if p and p.v == v:
            break
        elif p:
            p.moveToThreadNext()
        elif wrapped:
            break
        else:
            wrapped = True
            p = c.rootPosition()
    return p
</t>
<t tx="ekr.20150507175246.1">def munge_lines(self,root,publicCommands):
    """Return munged lines of """
    s = publicCommands.b
    i,j = s.find('{'),s.find('}')
    s = s[i+1:j]
    lines = sorted([z.strip() for z in g.splitLines(s) if z.strip()])
    lines = [z for z in lines if not z.startswith('#')]
    lines = [z[:z.find('#')] if z.find('#') &gt; -1 else z for z in lines]
    lines = [z.rstrip().rstrip(',') for z in lines]
    lines = [z[1:] for z in lines]
    lines = [z.replace("':",' ') for z in lines]
    self.n += len(lines)
    return lines
</t>
<t tx="ekr.20150508062944.1">def run(self):
    """Top-level code."""
    self.n = 0
    found = g.findNodeAnywhere(c,'Found: getPublicCommands')
    assert found
    for child in found.children():
        publicCommands = self.find_next_clone(child)
        root = self.find_class(publicCommands)
        if root:
            lines = self.munge_lines(root,publicCommands)
            d = self.create_d(lines,publicCommands)
            self.create_decorators(d,root)
    print('\n%s commands %s failed' % (self.n,self.n_fail))
</t>
<t tx="ekr.20150508063412.1">def create_decorators(self,d,root):
    """Create decorators for all items in d in root's tree."""
    # print('***** %s' % root.h)
    if root.h in self.fixups:
        roots = []
        aList = self.fixups.get(root.h)
        for root2_h in aList:
            root2 = g.findNodeAnywhere(self.c,root2_h)
            if root2:
                # g.trace(root.h,'=====&gt;',root2.h)
                roots.append(root2)
            else:
                g.trace('===== not found',root2_h)
    else:
        roots = [root]
    for f_name in sorted(d.keys()):
        found = False
        for root in roots:
            c_name = d.get(f_name)
            found = self.create_decorator(c_name,f_name,root)
            if found: break
        if not found and f_name not in self.suppress:
            print('===== not found: %30s %s' % (root.h,f_name))
            self.n_fail += 1
</t>
<t tx="ekr.20150508063538.1">def create_d(self,lines,publicCommands):
    """Create a dict. keys are method names; values are command names."""
    trace = False
    if trace:
        g.trace('\n', publicCommands.h)
    d = {}
    for s in lines:
        aList = s.split()
        if len(aList) &gt; 2:
            aList = [alist[0],' '.join(alist[1:])]
        c_name,f_name = alist[0].strip(),alist[1].strip()
        if ' ' not in f_name:
            f_name = f_name.split('.')[-1]
        # if '(' in f_name:
            # f_name = f_name[:f_name.find('(')]
        if trace: g.trace('%45s %s' % (c_name,f_name))
        d [f_name] = c_name
    return d
</t>
<t tx="ekr.20150508063926.1">def find_class(self,p):
    """Return the position of the class enclosing p."""
    for p2 in p.parents():
        if p2.h.lower().find('class') &gt; -1 and p2.b.find('class') &gt; -1:
            return p2
    else:
        g.trace('*** no class for p.h')
        return None
</t>
<t tx="ekr.20150508071622.1">def create_decorator(self,c_name,f_name,root):
    """
    Search root for a definition of f_name.
    If found, insert @cmd(f_name) before the definition.
    """
    # g.trace('%45s %s' % (c_name,f_name))
    trace = False
    found = False
    decorator = "@cmd('%s')\n" % (c_name)
    for p in root.self_and_subtree(copy=False):
        changed,result = False,[]
        for s in g.splitLines(p.b):
            if g.match_word(s,0,'def ' + f_name):
                if found:
                    if f_name not in self.suppress:
                        g.trace('duplicate def',f_name)
                else:
                    changed,found = True,True
                    result.append(decorator)
                    # print('%s%s' % (decorator,s))
            result.append(s)
        # if changed and self.make_changes:
            # new_body = ''.join(result)
            # # use git as our undo :-)
            # p.b = new_body
    return found
</t>
<t tx="ekr.20150508074623.1">def create_fixups(self):
    """
    Return a fixup dict.
    Keys are headlines for classes.
    Values are new headlines of nodes containing the actual class.
    """
    return {
        'ChapterCommandsClass': ['class ChapterController'],
        'EditCommandsClass': [
            'EditCommandsClass',
            'class Commands',
            'class LeoQtFrame',
            'class LeoBody',
        ],
        'class SearchCommandsClass': ['class LeoFind (LeoFind.py)'],
        'KeyHandlerCommandsClass (add docstrings)': [
            'class KeyHandlerClass',
            'class AutoCompleterClass',
        ]
    }
</t>
<t tx="ekr.20150509183433.1">g.cls()

# Changed files:
# leoApp.py
# leoAtFile.py
# leoCommands.py
# leoFileCommands.py
# leoFrame.py
# leoUndo.py
# qt_frame.py

make_changes = True  # True, actually make the change

class CreateDecorators:
    """
    A class to create decorators from tables in getPublicCommands.
    
    Note: the node "Found: getPublicCommands" must exist.
    """
    def __init__(self):
        self.n = 0
        self.n_fail = 0
        self.s = self.define_s()
    @others

CreateDecorators().run()
</t>
<t tx="ekr.20150509183433.2">def create_d(self,lines):
    """Create a dict. keys are method names; values are command names."""
    trace = False
    d = {}
    for s in lines:
        aList = s.split()
        if len(aList) &gt; 2:
            aList = [alist[0],' '.join(alist[1:])]
        c_name,f_name = alist[0].strip(),alist[1].strip()
        if ' ' not in f_name:
            f_name = f_name.split('.')[-1]
        if trace:
            g.trace('%45s %s' % (c_name,f_name))
        d [f_name] = c_name
    return d
</t>
<t tx="ekr.20150509183433.3">def create_decorator(self,c_name,f_name,root):
    """
    Search root for a definition of f_name.
    If found, insert @cmd(f_name) before the definition.
    """
    trace = True
    found = False
    decorator = "@cmd('%s')\n" % (c_name)
    for p in root.self_and_subtree(copy=False):
        changed,result = False,[]
        for s in g.splitLines(p.b):
            if g.match_word(s,0,'def ' + f_name):
                if found:
                    if f_name not in self.suppress:
                        g.trace('duplicate def',f_name)
                else:
                    changed,found = True,True
                    result.append(decorator)
            result.append(s)
        if changed and make_changes:
            new_body = ''.join(result)
            print('%40s %s' % (p.h[:40],decorator.rstrip()))
    return found
</t>
<t tx="ekr.20150509183433.4">def create_decorators(self,d):
    """Create decorators for all items in d in root's tree."""
    table = (
        'class Commands', # c.
        'class LeoQtFrame', # f.
        'class LeoFrame', # f.
        'class LeoApp', # g.app.
        '@file leoAtFile.py', # c.atFileCommands
        '@file leoFileCommands.py', # c.fileCommands
        'class Undoer', # c.undoer
    )
    roots = []
    for h in table:
        root = g.findNodeAnywhere(c,h)
        assert root,h
        roots.append(root)
    for f_name in sorted(d.keys()):
        found = False
        for root in roots:
            c_name = d.get(f_name)
            found = self.create_decorator(c_name,f_name,root)
            if found: break
        if not found and f_name not in self.suppress:
            print(f"===== not found: {f_name!r}")
            self.n_fail += 1
</t>
<t tx="ekr.20150509183433.8">def munge_lines(self,s):
    """Return munged lines of s. """
    lines = sorted([z.strip() for z in g.splitLines(s) if z.strip()])
    lines = [z for z in lines if not z.startswith('#')]
    lines = [z[:z.find('#')] if z.find('#') &gt; -1 else z for z in lines]
    lines = [z.rstrip().rstrip(',') for z in lines]
    lines = [z[1:] for z in lines]
    lines = [z.replace("':",' ') for z in lines]
    self.n += len(lines)
    return lines
</t>
<t tx="ekr.20150509183433.9">def run(self):
    """Top-level code."""
    lines = self.munge_lines(self.s)
    d = self.create_d(lines)
    self.create_decorators(d)
    print('%s commands %s failed' % (self.n,self.n_fail))
</t>
<t tx="ekr.20150514035207.1"></t>
<t tx="ekr.20150703061709.1">@language python

"""myLeoSettings.py: save the outline and run the pylint command"""

# print('@button run-pylint: %s' % c.shortFileName())
if c.isChanged():
    c.save()
c.k.simulateCommand('pylint')
</t>
<t tx="ekr.20160122104332.1">@language python
</t>
<t tx="ekr.20160123142722.1"># An example configuration file for make_stub_files.py.
# By default, this is ~/stubs/make_stub_files.cfg.
# Can be changed using the --config=path command-line option.

[Global]

files:

    # Files to be used *only* if no files are given on the command line.
    # glob.glob wildcards are supported.

    # c:/Repos/leo-editor/leo/core/leoAst.py
    # c:/Repos/leo-editor/leo/core/*.py
    # c:/Repos/leo-editor/plugins/*.py

output_directory: ~/stubs

prefix_lines:
    # Lines to be inserted at the start of each stub file.
    from typing import TypeVar, Iterable
    T = TypeVar('T', int, float, complex)

[Def Name Patterns]

[General Patterns]
</t>
<t tx="ekr.20170427112302.1">g.cls()
import glob
files = glob.glob(g.os_path_join(g.app.loadDir, '*.py'))
files = [z for z in files if g.os_path_basename(z).startswith('leo')]
if 0:
    g.printList(files)
found = set()
for p in c.all_unique_positions():
    name = p.isAnyAtFileNode()
    if name and name.startswith('leo'):
        path = g.os_path_join(g.app.loadDir, name)
        found.add(path)
if 0:
    print('found')
    g.printList(list(found))
else:
    missing = set(files) - found
    if missing:
        print('not found...')
        g.printList(list(sorted(missing)))
    else:
        print('done')
        </t>
<t tx="ekr.20170427114412.1"></t>
<t tx="ekr.20170428084123.1">@language python
"""Recursively import all python files in a directory and clean the result."""
@tabwidth -4 # For a better match.
g.cls()
dir_ = g.os_path_finalize_join(g.app.loadDir, '..', 'modes')
c.recursiveImport(
    dir_=dir_,
    kind = '@clean', # '@auto', '@clean', '@nosent','@file',
    recursive = True,
    safe_at_file = False,
    theTypes = ['.py'],
    verbose = False,
)
if 1:
    last = c.lastTopLevel()
    last.expand()
    if last.hasChildren():
        last.firstChild().expand()
    c.redraw(last)
print('Done')</t>
<t tx="ekr.20170428084208.443">#!/usr/bin/python
# This file generates pyflakes warnings for *all* imported symbols.
@others
@language python
@tabwidth -4
</t>
<t tx="ekr.20170428084208.444">from .globals                   import DEBUG, DISABLE_RESIZE_SYSTEM

from .wgwidget                  import TEST_SETTINGS, ExhaustedTestInput, add_test_input_from_iterable, add_test_input_ch

from .npyssafewrapper           import wrapper, wrapper_basic

from   .npysThemeManagers       import ThemeManager, disableColor, enableColor
from   . import npysThemes      as     Themes
from   .apNPSApplication        import NPSApp
from   .apNPSApplicationManaged import NPSAppManaged
from   .proto_fm_screen_area    import setTheme
from   .fmForm                  import FormBaseNew, Form, TitleForm, TitleFooterForm, SplitForm, FormExpanded, FormBaseNewExpanded, blank_terminal
from   .fmActionForm            import ActionForm, ActionFormExpanded
from   .fmActionFormV2          import ActionFormV2, ActionFormExpandedV2, ActionFormMinimal
from   .fmFormWithMenus         import FormWithMenus, ActionFormWithMenus, \
                                       FormBaseNewWithMenus, SplitFormWithMenus, \
                                       ActionFormV2WithMenus
from   .fmPopup                 import Popup, MessagePopup, ActionPopup, PopupWide, ActionPopupWide
from   .fmFormMutt              import FormMutt, FormMuttWithMenus
from   .fmFileSelector          import FileSelector, selectFile

from .fmFormMuttActive          import ActionControllerSimple, TextCommandBox, \
                                       FormMuttActive, FormMuttActiveWithMenus
from .fmFormMuttActive          import FormMuttActiveTraditional, FormMuttActiveTraditionalWithMenus


from .fmFormMultiPage           import FormMultiPage, FormMultiPageAction,\
                                       FormMultiPageActionWithMenus, FormMultiPageWithMenus

from .npysNPSFilteredData       import NPSFilteredDataBase, NPSFilteredDataList

from .wgbutton                  import MiniButton
from .wgbutton                  import MiniButtonPress
from .wgbutton                  import MiniButton      as Button
from .wgbutton                  import MiniButtonPress as ButtonPress

from .wgtextbox                 import Textfield, FixedText
from .wgtitlefield              import TitleText, TitleFixedText
from .wgpassword                import PasswordEntry, TitlePassword
from .wgannotatetextbox         import AnnotateTextboxBase
from .wgannotatetextbox         import AnnotateTextboxBaseRight

from .wgslider                  import Slider, TitleSlider
from .wgslider                  import SliderNoLabel, TitleSliderNoLabel
from .wgslider                  import SliderPercent, TitleSliderPercent

from .wgwidget                  import DummyWidget, NotEnoughSpaceForWidget
from . import wgwidget as widget

from .wgmultiline               import MultiLine, Pager, TitleMultiLine, TitlePager, MultiLineAction, BufferPager, TitleBufferPager
from .wgmultiselect             import MultiSelect, TitleMultiSelect, MultiSelectFixed, \
                                       TitleMultiSelectFixed, MultiSelectAction
from .wgeditmultiline           import MultiLineEdit
from .wgcombobox                import ComboBox, TitleCombo
from .wgcheckbox                import Checkbox, RoundCheckBox, CheckBoxMultiline, RoundCheckBoxMultiline, CheckBox, CheckboxBare
from .wgFormControlCheckbox     import FormControlCheckbox
from .wgautocomplete            import TitleFilename, Filename, Autocomplete
from .muMenu                    import Menu
from .wgselectone               import SelectOne, TitleSelectOne
from .wgdatecombo               import DateCombo, TitleDateCombo

from .npysTree import TreeData
from .wgmultilinetree           import MLTree, MLTreeAnnotated, MLTreeAction, MLTreeAnnotatedAction
from .wgmultilinetreeselectable import MLTreeMultiSelect, TreeLineSelectable
from .wgmultilinetreeselectable import MLTreeMultiSelectAnnotated, TreeLineSelectableAnnotated


# The following are maintained for compatibility with old code only. ##########################################

from .compatibility_code.oldtreeclasses import MultiLineTree, SelectOneTree
from .compatibility_code.oldtreeclasses import MultiLineTreeNew, MultiLineTreeNewAction, TreeLine, TreeLineAnnotated # Experimental
from .compatibility_code.oldtreeclasses import MultiLineTreeNewAnnotatedAction, MultiLineTreeNewAnnotated # Experimental
from .compatibility_code.npysNPSTree import NPSTreeData

# End compatibility. ###########################################################################################

from .wgfilenamecombo           import FilenameCombo, TitleFilenameCombo
from .wgboxwidget               import BoxBasic, BoxTitle
from .wgmultiline               import MultiLineActionWithShortcuts
from .wgmultilineeditable       import MultiLineEditable, MultiLineEditableTitle, MultiLineEditableBoxed

from .wgmonthbox                import MonthBox
from .wggrid                    import SimpleGrid
from .wggridcoltitles           import GridColTitles

from .muNewMenu                 import NewMenu, MenuItem
from .wgNMenuDisplay            import MenuDisplay, MenuDisplayScreen

from .npyspmfuncs               import CallSubShell

from .utilNotify                 import notify, notify_confirm, notify_wait, notify_ok_cancel, notify_yes_no

# Base classes for overriding:

# Standard Forms:
from . import stdfmemail

# Experimental Only
from .wgtextboxunicode import TextfieldUnicode
from .wgtexttokens     import TextTokens, TitleTextTokens

# Very experimental. Don't use for anything serious
from .apOptions import SimpleOptionForm
from .apOptions import OptionListDisplay, OptionChanger, OptionList, OptionLimitedChoices, OptionListDisplayLine
from .apOptions import OptionFreeText, OptionSingleChoice, OptionMultiChoice, OptionMultiFreeList, \
                       OptionBoolean, OptionFilename, OptionDate, OptionMultiFreeText


# This really is about as experimental as it gets
from .apNPSApplicationEvents import StandardApp
from .eveventhandler import Event


</t>
<t tx="ekr.20170428085201.1">@nosearch
@nobeautify</t>
<t tx="ekr.20170811173924.1">@language python
import os
import subprocess
import sys
import time
win = sys.platform.startswith('win')
old_dir = os.getcwd()
if win:
    new_dir = r'C:\Repos\leo-editor'
    path = r'C:\Users\Edward~1\Backup'
else:
    new_dir = '/home/edward/Repos/leo-editor'
    path = '/home/edward/Backup'
assert g.os_path_exists(new_dir), repr(new_dir)
assert g.os_path_exists(path), repr(path)
stamp = time.strftime("%Y%m%d-%H%M%S")
fn = g.finalize_join(path, f"leo-bundle-all-{stamp}")
bundle_command = 'git bundle create %s --all' % fn
print(bundle_command)
os.chdir(new_dir)
proc = subprocess.Popen(bundle_command, shell=True)
proc.wait()
os.chdir(old_dir)
print('done! wrote %s' % fn)
</t>
<t tx="ekr.20171031111403.1"></t>
<t tx="ekr.20180225010644.1">@nobeautify</t>
<t tx="ekr.20180225010707.1"></t>
<t tx="ekr.20180225010743.1">@nosearch</t>
<t tx="ekr.20180225010850.1"></t>
<t tx="ekr.20180225010913.1"></t>
<t tx="ekr.20180324065741.1">"""Copy the selected text to the next node."""
w = c.frame.body.wrapper
s = w.getSelectedText()
if s.strip():
    w.deleteTextSelection()
    c.p.b = w.getAllText()
    w.setInsertPoint(0)
    p = c.insertHeadline()
    c.selectPosition(p)
    p.b = s
    c.editHeadline()
else:
    g.es_print('no text selected')
</t>
<t tx="ekr.20180504191650.36"></t>
<t tx="ekr.20180504191650.42"></t>
<t tx="ekr.20180504191650.68"></t>
<t tx="ekr.20180504192522.1"></t>
<t tx="ekr.20180708145905.1">@language rest
@wrap

This is the theory of operation document for py2cs.py. The most interesting aspect of this script is the TokenSync class. This class provides a reliable way of associating tokenizer tokens with ast nodes.

@others
</t>
<t tx="ekr.20180708145905.6">
### Using the TokenSync class

The present code is driven by ast trees, but each visitor of the CoffeeScriptTraverser class takes care to preserve **otherwise-ignored tokens**. These are tokens that would otherwise be ignored: namely blank lines and comments, both entire-line comments and trailing comments.

The visitor for each statement intersperses otherwise ignored tokens using calls to the TokenSync class.  The simplest cases are like this:

    def do_Break(self, node):
        head = self.leading_string(node)
        tail = self.trailing_comment(node)
        return head + self.indent('break') + tail

The leading_string and trailing_comment methods simply redirect to the corresponding methods in the TokenSync class.  Saves a bit of typing. Compound statements are a bit more bother, but not overly so. For example:

    def do_If(self, node):

        result = self.leading_lines(node)
        tail = self.trailing_comment(node)
        s = 'if %s:%s' % (self.visit(node.test), tail)
        result.append(self.indent(s))
        for z in node.body:
            self.level += 1
            result.append(self.visit(z))
            self.level -= 1
        if node.orelse:
            tail = self.tail_after_body(node.body, node.orelse, result)
            result.append(self.indent('else:' + tail))
            for z in node.orelse:
                self.level += 1
                result.append(self.visit(z))
                self.level -= 1
        return ''.join(result)

The line:

        tail = self.tail_after_body(node.body, node.orelse, result)

is a hack needed to compensate for the lack of an actual ast.Else node.
</t>
<t tx="ekr.20180708145905.7">
### Summary

The TokenSync class is, a new, elegant, unexpected and happy development. It is a relatively easy-to-use helper that allows parser-based code to preserve data that is not easily accessible in parse trees.

The TokenSync class avoids [problems with the col_offset field](
http://stackoverflow.com/questions/16748029/how-to-get-source-corresponding-to-a-python-ast-node) in ast nodes. The TokenSync class depends only on the ast.lineno field and the tokenize module. We can expect it to be rock solid.

Edward K. Ream
February 20 to 25, 2016



</t>
<t tx="ekr.20180708152000.1">
### The problem

The initial version of py2cs.py (the script) used only tokens. This solved all token-related problems, but made parsing difficult. Alas, it is [difficult](http://stackoverflow.com/questions/16748029/how-to-get-source-corresponding-to-a-python-ast-node) to associate tokens with ast nodes.

The script needs the following token-related data:

- The **ignored lines** (comment lines and blank lines) that precede any statement.

- The **trailing comment** strings that might follow any line.

- Optionally, the **line breaks** occurring within lines. At present, this script does not preserve such breaks, and it's probably not worth doing. Indeed, automatically breaking long lines seems more useful, especially considering that coffeescript lines may be substantially shorter than the corresponding python lines.

- The **exact spelling** of all strings.

The [ast_utils module](
https://bitbucket.org/plas/thonny/src/3b71fda7ac0b66d5c475f7a668ffbdc7ae48c2b5/thonny/ast_utils.py?at=master) purports to solve this problem with convoluted adjustments to the col_offset field. This approach is subject to subtle Python bugs, and subtle differences between Python 2 and Python 3. There is a better way...
</t>
<t tx="ekr.20180708152018.1">
### Design

The main idea is to use *only* the ast.lineno fields and the tokenizer module to recreate token data. The design assumes only that both the ast.lineno field and Python's tokenizer module are solid. This is a much more reasonable assumption than assuming that the col_offset field always tells the truth. In short, this design *ignores* the ast.col_offset field.

At startup, the TokenSync ctor assigns all the incoming tokens to various lists.  These lists are indexed by lineno:

    ts.line_tokens[i]: all the tokens on line i
    ts.string_tokens[i]: all string tokens on line i
    st.ignored_lines: the blank or comment line on line i

It is very easy to create these lists. The code does not depend on any arcane details.

#### Recovering the exact spelling of stings.

ts.synch_string returns the *next* string on the line. Here it is, stripped of defensive code:

    def sync_string(self, node):
        '''Return the spelling of the string at the given node.'''
        tokens = self.string_tokens[node.lineno-1]
        token = tokens.pop(0)
        self.string_tokens[node.lineno-1] = tokens
        return self.token_val(token)

Stripped of defensive code, the do_Str visitor is just:

    def do_Str(self, node):
        '''A string constant, including docstrings.'''
        return self.sync_string(node)

#### Recovering otherwise ignored nodes

**ts.leading_lines(node)** returns a list of otherwise ignored lines that
precede the node's line that have not already been returned.
**ts.leading_string(node)** is a convenience method that returns ''.join(ts.leading_lines(node)). The visitors of the CoffeeScriptTraverser class show how to use these methods.
</t>
<t tx="ekr.20180816105258.1">g.cls()
import os
import leo.commands.editFileCommands as efc
path = g.finalize_join(g.app.loadDir, '..', '..')
# print(f"os.chdir({path})")
os.chdir(path)

# Any revspec is valid as an argument to the "branch1" and "branch2" args.
# See https://git-scm.com/book/en/v2/Git-Tools-Revision-Selection

efc.GitDiffController(c).diff_two_branches(
    branch1='master', # old branch/rev
    branch2='ekr-3702-scan_lines-warnings', # new branch/rev
    fn='leo/core/leoAtFile.py',  # Don't use back slashes.
)
</t>
<t tx="ekr.20180824065751.1">print(p.gnx)</t>
<t tx="ekr.20181030041436.1"></t>
<t tx="ekr.20190402091335.1">from leo.commands import editFileCommands as efc

efc.GitDiffController(c).diff_two_revs(
    rev1='ekr-3744-pr3-token-based-orange',  # Old
    rev2='tbo-test',   # New
)
</t>
<t tx="ekr.20190406154306.1">g.openWithFileName(r'C:\apps\pyzo\pyzo.leo')</t>
<t tx="ekr.20190607124533.1"></t>
<t tx="ekr.20200212095937.1"></t>
<t tx="ekr.20200212095937.2">True:  allow joined lines to contain strings.
False: (Recommended by EKR): Retain alignment of strings.</t>
<t tx="ekr.20200212095937.3">True: Retain indentation of overindented stand-alone comment lines.</t>
<t tx="ekr.20200212095937.5"># At present I am of the opinion that joining lines is usually a bad idea.

Should be &lt;= beautify-max-split-line-length.
Zero suppresses all line joining.</t>
<t tx="ekr.20200212095937.6">Zero suppresses all line splitting.</t>
<t tx="ekr.20200222083959.1">import logging
rootLogger = logging.getLogger('')
rootLogger.setLevel(logging.DEBUG)
socketHandler = logging.handlers.SocketHandler(
    'localhost',
    logging.handlers.DEFAULT_TCP_LOGGING_PORT,
)
rootLogger.addHandler(socketHandler)
logging.info('-' * 20)
</t>
<t tx="ekr.20200222151754.1">import yoton

# Create another context and a sub channel
ct2 = yoton.Context()
sub = yoton.SubChannel(ct2, 'chat')

# Connect
ct2.connect('publichost:test')

# Receive
while True:
    i = int(sub.recv())
    print(i)
    if i == 10:
        break
</t>
<t tx="ekr.20200308193719.1">d = {}  # Keys are gnxs, values is a list of vnodes with that gnx.
for v in c.all_unique_nodes():
    gnx = v.gnx
    aList = d.get(gnx, [])
    if v not in aList:
        aList.append(v)
        d [gnx] = aList
        if len(aList) &gt; 1:
            print(f"gnx clash: {gnx}")
            g.printObj(aList)
print('done')</t>
<t tx="ekr.20201012111545.1">@language python
@tabwidth -4
@pagewidth 80
</t>
<t tx="ekr.20201013034659.1"></t>
<t tx="ekr.20201013034742.10"># These can be overridden in subclasses.
</t>
<t tx="ekr.20201013034742.11"># Define an override if desired...

if 0: # The base class
    def clean_headline(self, s):
        """Return a cleaned up headline s."""
        return s.strip()
        
if 0: # A more complex example, for the C language.
    def clean_headline(self, s):
        """Return a cleaned up headline s."""
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
<t tx="ekr.20201013034742.12">def clean_nodes(self, parent):
    """
    Clean all nodes in parent's tree.
    Subclasses override this as desired.
    See perl_i.clean_nodes for an examplle.
    """
    pass
</t>
<t tx="ekr.20201013034742.13">class {{cap_name}}_ScanState:
    """A class representing the state of the {{name}} line-oriented scan."""
    
    def __init__(self, d=None):
        """{{cap_name}}_ScanState.__init__"""
        if d:
            prev = d.get('prev')
            self.context = prev.context
            # Adjust these by hand.
            self.curlies = prev.curlies
        else:
            self.context = ''
            # Adjust these by hand.
            self.curlies = 0

    def __repr__(self):
        """{{cap_name}}_ScanState.__repr__"""
        # Adjust these by hand.
        return "{{cap_name}}_ScanState context: %r curlies: %s" % (
            self.context, self.curlies)

    __str__ = __repr__

    @others
</t>
<t tx="ekr.20201013034742.16">"""Converts the word at the cursor to pep8 style throughout a given tree."""
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
<t tx="ekr.20201013034742.17">class Pep8:
    """
    Convert the word under the cursor to pep8 style in all subtrees in
    table.
    """
    
    def __init__ (self, table, change=False):
        """Ctor for Pep8 class."""
        self.change = change
        self.table = table
        
    @others
</t>
<t tx="ekr.20201013034742.18">def change_all(self, name, new_name, root):
    """Change name to new_name throughout root's tree."""
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
<t tx="ekr.20201013034742.19">def change_body(self, name, new_name, p):
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
<t tx="ekr.20201013034742.2">g.cls()
# define constants that describe the new language.
name = 'php'  # The name of the file, and the prefix for classes.
language = 'php'  # The name of the language, case doesn't matter.
extensions = ['.php',]  # A list of file extensions supported by this importer.
strict = False  # True if leading whitespace is particularly significant.
state_ivar = 'self.curlies'
    # 'self.indent' for python, coffeescript.
    # 'self.curlies' for many other languages
    # '(self, curlies, self.parens)' for more complex comparisons
&lt;&lt; define run &amp; helpers &gt;&gt;
run(extensions, language, name, state_ivar)
</t>
<t tx="ekr.20201013034742.20">def change_headline(self, name, new_name, p):
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
<t tx="ekr.20201013034742.21">def get_name(self):
    i, j = c.editCommands.extendToWord(event=None, select=False)
    w = c.frame.body.wrapper
    s = w.getAllText()
    name = s[i:j]
    return name
</t>
<t tx="ekr.20201013034742.22">def run(self):
    # self.clear()
    name = self.get_name()
    new_name = self.to_pep8(name)
    if len(name) &lt; 2:
        g.es_print('name too short:', name)
    elif new_name == name:
        g.es_print('already pep8:', name)
    else:
        g.es_print('%s -&gt; %s' % (name, new_name))
        # Preload the replacement text.
        c.findCommands.ftm.set_find_text(new_name)
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
<t tx="ekr.20201013034742.23">def to_pep8(self, s):
    
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
<t tx="ekr.20201013034742.24">def clear():
    g.cls()
    c.k.simulateCommand('clear-log')
</t>
<t tx="ekr.20201013034742.3">@others</t>
<t tx="ekr.20201013034742.4">def copy_tree(source, root, h):
    """Copy the source tree to the node after p, with headline h."""
    p2 = root.insertAfter()
    source.copyTreeFromSelfTo(p2)
    p2.h = h
    return p2
 </t>
<t tx="ekr.20201013034742.5">def make_substitutions(destination, patterns):
    """Make all substitutions in the destination tree."""
    for p in destination.self_and_subtree():
        h = substitute(p.h, patterns)
        if p.h != h:
            p.h = h
        b = substitute(p.b, patterns)
        if p.b != b:
            p.b = b
</t>
<t tx="ekr.20201013034742.6">def run(extensions, language, name, state_ivar):
    """The driver for this script."""
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
<t tx="ekr.20201013034742.7">def substitute(s, patterns):
    """Make all substitutions in s."""
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
<t tx="ekr.20201013034742.8">"""The @auto importer for the {{name}} language."""
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
<t tx="ekr.20201013034742.9">class {{cap_name}}_Importer(Importer):
    """The importer for the {{name}} lanuage."""

    def __init__(self, c):
        """{{cap_name}}_Importer.__init__"""
        # Init the base class.
        Importer.__init__(self,
            c,
            language = '{{language}}',
        )
        
    @others
</t>
<t tx="ekr.20201015145257.1">import leo.core.leoImport as leoImport
import importlib
importlib.reload(leoImport)
g.cls()
# Change path as necessary.
path = r'c:\users\edreamleo\lsa.py'
assert g.os_path_exists(path)
x = leoImport.LegacyExternalFileImporter(c)
x.import_file(path)
</t>
<t tx="ekr.20201018062305.1">"""
Overwrite LeoPyRef.leo from the given list of nodes.

This script will delete any nodes that are in LeoPyRef.leo but not in
leoPy.leo.

"""
# Do not use this script—it creates huge diffs.
import io
import os
@others
main(node_list = ['Startup', 'Notes', 'Script files', 'Code'])
</t>
<t tx="ekr.20201018063747.1">def put_content(positions_list):
    """
    Return the desired contents of leoPyRef.leo.
    
    Based on code by Виталије Милошевић.
    """
    fc = c.fileCommands
    # Make only a few copies.
    p = c.rootPosition().copy()
    fc.currentPosition = p.copy()
    fc.rootPosition = p.copy()
    old_vnodesDict = fc.vnodesDict  # Save.
    fc.vnodesDict = {}
    try:
        # Put the file
        fc.outputFile = io.StringIO()
        put_prolog()  # Put prolog w/o the stylesheet.
        fc.putHeader()
        fc.putGlobals()
        fc.putPrefs()
        fc.putFindSettings()
        fc.put("&lt;vnodes&gt;\n")
        for p in positions_list:
            # An optimization: Write the next top-level node.
            fc.put_v_element(p, isIgnore=p.isAtIgnoreNode())
        fc.put("&lt;/vnodes&gt;\n")
        put_tnodes(positions_list)  # Put only *required* tnodes.
        fc.putPostlog()
        s = fc.outputFile.getvalue()
    finally:
        fc.outputFile = None
        fc.vnodesDict = old_vnodesDict  # Restore!
    return s
</t>
<t tx="ekr.20201018065757.1">def check_file_names():
    """Return True if leoPyRef exists and we are running from leoPy.leo."""
    if not 'leoPy.leo' in c.shortFileName():
        oops('Run this script only from leoPy.leo')
        return None
    fileName = g.finalize_join(g.app.loadDir, '..', 'core', 'leoPyRef.leo')
    if not os.path.exists(fileName):
        oops(f"Not found: {fileName}")
        return None
    return fileName</t>
<t tx="ekr.20201018065921.1">def check_nodes(node_list):
    """Return True if all nodes are found."""
    result = []
    for node in node_list:
        p = g.findTopLevelNode(c, node, exact=True)
        if p:
            result.append(p.copy())
        else:
            oops(f"Top-level node {node} not found")
            return []
    return result</t>
<t tx="ekr.20201018070822.1">def main(node_list):
    """The main line."""
    c.endEditing()
    fileName = check_file_names()
    if not fileName:
        return  # Error.
    positions_list = check_nodes(node_list)
    if not positions_list:
        return  # Error.
    content = put_content(positions_list)
    if not content:
        return  # Error.
    with open(fileName, 'w', encoding="utf-8", newline='\n') as f:
        f.write(content)
    print('')
    g.es_print(f"Updated {g.shortFileName(fileName)}")
</t>
<t tx="ekr.20201018072911.1">def oops(message):
    """Print an error message"""
    print('')
    g.es_print(message)
    print('')</t>
<t tx="ekr.20201202144529.1"></t>
<t tx="ekr.20201208114843.1"># No longer needed. Use the git-diff-pr command.
import leo.commands.editFileCommands as efc
x = efc.GitDiffController(c)
x.diff_pull_request()
</t>
<t tx="ekr.20201222095250.1">g.cls()
import glob
import os
theme_dir = os.path.join(g.app.loadDir, '..', 'themes')
assert os.path.exists(theme_dir), repr(theme_dir)
paths = glob.glob(f"{theme_dir}{os.sep}*.leo")

def clean(s):
    return s.strip().replace('-','').replace('_','').replace(' ','')
    
for path in paths:
    d = {}
    c = g.createHiddenCommander(path)
    if not c:
        print('Not a .leo file:', path)
        continue
    sfn = c.shortFileName()
    if sfn == 'old_themes.leo':
        continue
    print('checking ', sfn)
    for p in c.all_unique_positions():
        h = clean(p.h)
        if h.startswith('@'):
            if h in d:
                print(f"  {sfn:20}: duplicate {h}")
            else:
                d [h] = True
print('done')</t>
<t tx="ekr.20210110092457.1">@language python
@nosearch
</t>
<t tx="ekr.20210110092457.5">g.cls()
import os
os.chdir(os.path.join(g.app.loadDir, '..', '..'))
# os.system('py-cov-find')
command = r'pytest --cov-report html --cov-report term-missing --cov leo.core.leoFind leo\core\leoFind.py'
os.system(command)
g.es_print('done')</t>
<t tx="ekr.20210110092457.6">import os
# os.system('moz htmlcov/leo_core_leoFind_py.html')
os.chdir(os.path.join(g.app.loadDir, '..', '..'))
os.system('moz htmlcov/leo_core_leoFind_py.html')</t>
<t tx="ekr.20210110092457.7">g.cls()
import os
os.system('python -m unittest leoFind.py')
g.es_print('done')</t>
<t tx="ekr.20210118013157.1">"""
Convert defs in LeoFind to pep8 names.
- Don't change defs containing underscores.
- Check for existing target.
"""
g.cls()
import re
h = 'class LeoFind (LeoFind.py)'
root = g.findNodeAnywhere(c, h)
@others
if root:
    main(root)
else:
    print('not found:', root)</t>
<t tx="ekr.20210118013807.1">def main(root):
    pattern = re.compile(r'^def\s+(\w+)', re.MULTILINE)
    for pass_n in (0, 1):
        n = 0
        for p in root.subtree():
            for m in re.finditer(pattern, p.b):
                target = m.group(0)
                old_func = m.group(1)
                if '_' in target:
                    continue
                if target.islower():
                    continue
                if old_func == 'finishCreate':  # Special case.
                    return
                new_func = new_name(old_func)
                if new_func == old_func:
                    continue
                if pass_n == 0:
                    if exists(new_func, root):
                        g.trace(f"already exists: {old_func} {new_func}")
                        g.trace('aborting')
                        return
                else:
                    n += 1
                    convert(old_func, new_func, root)
    g.trace(f"converted {n} function names")
    c.redraw()
            </t>
<t tx="ekr.20210118020530.1">def new_name(s):
    """Return the new name of s."""
    assert ' ' not in s
    # Convert s to underscore style.
    result = []
    for i, ch in enumerate(s):
        if i &gt; 0 and ch.isupper():
            result.append('_')
        result.append(ch.lower())
    return ''.join(result).replace('i_search', 'isearch')
</t>
<t tx="ekr.20210118021337.1">def exists(s, root):
    """Return True if s exists in any of root's nodes."""
    for p in root.self_and_subtree():
        if s in p.b:
            return True
    return False</t>
<t tx="ekr.20210118024739.1">def convert(old_func, new_func, root):
    print(f"{old_func} =&gt; {new_func}\n")
    for p in root.subtree():
        pattern = rf"\b{old_func}\b"
        p.h = re.sub(pattern, new_func, p.h)
        p.b = re.sub(pattern, new_func, p.b)
        # g.printObj(g.splitLines(s2), tag='p.h')
    print('')</t>
<t tx="ekr.20210429045101.1">g.cls()
fc = c.fileCommands
d = fc.gnxDict
for key in sorted(d.keys()):
    v = d.get(key)
    if v.h.lower() == 'newheadline':
        print('in dict', key, v)
        for p in c.all_positions():
            if p.v == v:
                print(p)
        else:
            print('no position for', v)
print('done')</t>
<t tx="ekr.20210510071427.1">def put_prolog():
    """Same as fc.putProlog, without the stylysheet."""
    fc = c.fileCommands
    tag = 'http://leoeditor.com/namespaces/leo-python-editor/1.1'
    #
    # Put the xml line.
    fc.putXMLLine()
    #
    # Put the "created by Leo" line.
    fc.put('&lt;!-- Created by Leo: http://leoeditor.com/leo_toc.html --&gt;\n')
    #
    # Do *not* put the stylesheet line.
        # fc.putStyleSheetLine()
    #
    # Put the namespace
    fc.put(f'&lt;leo_file xmlns:leo="{tag}" &gt;\n')
</t>
<t tx="ekr.20210510071812.1">def put_tnodes(positions_list):
    """
    Write all tnodes except those for vnodes appearing in @file, @edit or @auto nodes.
    """
        
    def should_suppress(p):
        return any(z.isAtFileNode() or z.isAtEditNode() or z.isAtAutoNode()
            for z in p.self_and_parents())

    fc = c.fileCommands
    fc.put("&lt;tnodes&gt;\n")
    suppress = {}
    for p in c.all_positions(copy=False):
        if should_suppress(p):
            suppress[p.v] = True
    # Write tnodes in *outline* order.
    written = {}
    for root in positions_list:
        for p in root.self_and_subtree():
            if p.v not in suppress and p.v not in written:
                written[p.v] = True
                fc.put_t_element(p.v)
    fc.put("&lt;/tnodes&gt;\n")
</t>
<t tx="ekr.20210530065000.2"># This node contains the commands needed to execute a program in a particular language.
# Format: language-name: command

#
# execute-general-script always creates a temporary file.
# Just before executing the command, execute-general-script
# Replaces &lt;FILE&gt; by the name of the temporary file.

# This does work.
# python: python -v &lt;FILE&gt;

go: go run .
python: python
rust: rustc
</t>
<t tx="ekr.20210530065000.3"># This node contains the regex pattern to determine the line number in error messages.
# Format: language-name: regex pattern
#
# Patterns must define two groups, in either order:
# One group, containing only digits, defines the line number.
# The other group defines the file name.


go: ^\s*(.*):([0-9]+):([0-9]+):.+$
python: ^\s*File "(.+)", line ([0-9]+), in .+$
rust: ^\s*--&gt; (.+):([0-9]+):([0-9]+)\s*$</t>
<t tx="ekr.20210630070717.1">"""
See #2025: https://github.com/leo-editor/leo-editor/issues/2025

Note: I have chosen *not* to update the gnx's. Félix deserves the credit for the changes.

A script to restore gnx's in sentinels in leoserver.py from the devel branch to the felix-server2 branch.

devel-leoserver.py: the version of leoserver.py from devel
felix_server.py:    The version of leoserver.py from felix-server-2
new_server.py:      leoserver.py, with updated gnx's.

After running this script, `kdiff3 devel-leoserver.py new-leoserver.py` shows *only*
the expected changes to sentinel lines.
"""

g.cls()
import difflib
import os
verbose = True
ekr_server = r'c:\diffs\devel-leoserver.py'
felix_server = r'c:\diffs\felix-server2-leoserver.py'
new_server = r'c:\diffs\new-leoserver.py'
assert os.path.exists(ekr_server), ekr_server
assert os.path.exists(felix_server), felix_server
#
# The target (new!) version should be the ekr_server code.
# With this convention:
#   all '-' opcodes will refer to felix gnx's!
#   These lines refer to lines that Félix *inserted* or *changed*
with open(felix_server) as f:
    a1_s = f.read()
with open(ekr_server) as f:
    b1_s = f.read()
print('len ekr', len(b1_s), 'len felix', len(a1_s))
# ndiff compares *lists* of strings.
# a and b are lists of @+node sentinels.
a_list = [z for z in g.splitLines(a1_s) if z.strip().startswith('#@+node:')]
b_list = [z for z in g.splitLines(b1_s) if z.strip().startswith('#@+node:')]
changed, deleted, inserted = [], [], []
diff = list(difflib.ndiff(a_list, b_list))
i = 0
while i &lt; len(diff):
    progress = i
    s = diff[i]
    code = s[0]
    line1 = s[2:]
    if code == '-':  # Félix inserted or changed the node.
        line2_s = diff[i+1] if i+1 &lt; len(diff) else ''
        line3_s = diff[i+2] if i+2 &lt; len(diff) else ''
        line2_code = line2_s[0] if line2_s else ''
        line3 = line3_s[2:]
        assert 'felix' in line1, s
        if line2_code == '?':  # The line changed. Remember the first and third lines.
            assert line2_s
            assert line3_s
            changed.append((line1, line3))
            i += 4
        else: # Félix inserted the node.
            inserted.append(line1)
            i += 1
    elif code == '+':  # Félix deleted the node.
        assert 'ekr' in line1, s
        deleted.append(line1)
        i += 1
    else:
        print(f"{i:&gt;3}: UNKNOWN CODE")
        print(f"{i:&gt;3}: {s!r}")
        print('')
        for j, s in enumerate(diff[:i+1]):
            print(f"{j:&gt;3}: {s!r}")
        break
    assert i &gt; progress
#
# Print the results.
print('')
print(f"Inserted {len(inserted)} nodes")
if verbose:
    print('')
    for i, z in enumerate(inserted):
        print(f"{i:&gt;3}: {z!r}")
    print('')
print(f" Deleted {len(deleted)} nodes")
if verbose:
    print('')
    for i, z in enumerate(deleted):
        print(f"{i:&gt;3}: {z!r}")
    print('')
print(f" Changed {len(changed)} nodes")
if verbose:
    print('')
    for i, z in enumerate(changed):
        a, b = z
        print(f"{i:&gt;3}: felix: {a!r}")
        print(f"{i:&gt;3}:   ekr: {b!r}")
        print('')
#
# Change the leoserver.py, *not* the ekr file.
result = a1_s
for z in changed:
    a, b = z
    assert '#@+node:felix' not in b, repr(b)
    result = result.replace(a, b)
if 0:
    g.printObj(g.splitLines(result), tag=result)
if 0:
    i, n = 0, 0
    tag = '#@+node:felix'
    while True:
        i = result.find(tag, i)
        if i == -1:
            break
        print(n, repr(result[i: i+50]))
        i += len(tag)
        n += 1
if 1:
    # Write the file.
    with open(new_server, 'w') as f:
        f.write(result)
    print(f"wrote {new_server}")
    
</t>
<t tx="ekr.20210630103405.1">g.cls()
import difflib, os, re
ekr_server = r'c:\diffs\devel-leoserver.py'
felix_server = r'c:\diffs\felix-server2-leoserver.py'
with open(ekr_server) as f:
    a1_s = f.read()
with open(felix_server) as f:
    b1_s = f.read()
# a and b are lists of @+node sentinel lines.
a_list = [z.lstrip() for z in g.splitLines(a1_s) if z.strip().startswith('#@+node:')]
b_list = [z.lstrip() for z in g.splitLines(b1_s) if z.strip().startswith('#@+node:')]
# Show the diffs.
diff = difflib.ndiff(a_list, b_list)
for i, s in enumerate(diff):
    print(f"{i:&lt;3}: {s.rstrip()}")
</t>
<t tx="ekr.20210701044426.1"></t>
<t tx="ekr.20210701044513.1"></t>
<t tx="ekr.20210829132319.1">"""Convert old-style tests to new-style tests"""
g.cls()
import importlib
from leo.commands import convertCommands
importlib.reload(convertCommands)

root_h = '--- To be converted'
root = g.findNodeAnywhere(c, root_h)
converter = convertCommands.ConvertAtTests()
# converter = convertCommands.ConvertShadowTests()
# converter = convertCommands.ConvertUndoTests()
# converter = convertCommands.ConvertColorizerTests()
convertCommands.convert_at_test_nodes(c, converter, root, copy_tree=True)</t>
<t tx="ekr.20210912064148.1"></t>
<t tx="ekr.20210912064205.1"></t>
<t tx="ekr.20211011090013.1">"""
Find and convert hanging comments.

Warning: do not run this script on unit testing files.
"""
# https://github.com/leo-editor/leo-editor/pull/2622
g.cls()
import re
from typing import Any, List

trace = True  # It's useful to trace even when also replacing.
replace = True  # Replace body text.
max_line_length = 70  # Maximum line length for lines containing trailing comments.

@others

for p in c.p.self_and_subtree():
    convert(p)
print('done')
</t>
<t tx="ekr.20211014103433.1">"""
Convert the TeX sources, assumed to be in ~/tex.web, to an outline.

https://mirror.las.iastate.edu/tex-archive/systems/knuth/dist/tex/tex.web

"""
g.cls()
import os
import re
# Read
path = os.path.expanduser('~/tex.web')
with open(path) as f:
    contents = f.read()
# Create root.
last = c.lastTopLevel()
if last.h == 'tex.web':
    last.doDelete()
last = c.lastTopLevel()
root = last.insertAfter()
root.h = 'tex.web'
root.b = '@language tex'
prefix = root.insertAsLastChild()
prefix.h = 'prefix'
# Patterns
at_star_pat = re.compile(r'^@\*(.*?)$')
at_space_pat = re.compile(r'^@ (.*?)$')
at_p_pat = re.compile(r'^@p (.*?)$')
at_sec_pat = re.compile(r'^@&lt;(.*?)@&gt;=(.*?)$')
@others  # Define handlers and helpers.
table = (
    (at_star_pat, do_at_star),
    (at_space_pat, do_at_space),
    (at_p_pat, do_p),
    (at_sec_pat, do_sec),
)
count = 0
parents = [('prefix', prefix)]  # Tuples: (kind, p)
for i, s in enumerate(g.splitLines(contents)):
    for pattern, helper in table:
        if m := pattern.match(s):
            helper(i, m, s)  # m not used at present.
            count += 1
    else:
        parent = parents[-1][1]
        parent.b += s
# Finish
root.expand()
c.redraw(root)
print(f"done: {count} pattern{g.plural(count)}")</t>
<t tx="ekr.20211014112513.1">def do_at_star(i, m, s):
    global parents
    print(s.rstrip())  # A good progress indicator.
    parent = root.insertAsLastChild()
    parent.h = s.strip()
    parents = [('@*', parent)]  # Always prune the stack.

def do_at_space(i, m, s):
    new_node('@ ', s)
    
def do_p(i, m, s):
    new_node('@p', s)

def do_sec(i, m, s):
    new_node('@&lt;', s)
</t>
<t tx="ekr.20211014120710.1">def new_node(kind, h):
    """Create a new node as the last child of an '@*' node."""
    global parents
    kind = parents[-1][0]
    if kind == '@*':
        parent = parents[-1][1]
    else:
        # Prune the stack back to the '@*' entry.
        parent_tuple = parents[0]
        assert parent_tuple[0] == '@*', parents
        parents = [parent_tuple]
        parent = parent_tuple[1]
    child = parent.insertAsLastChild()
    child.h = h.strip()
    parents.append(('@ ', child))
</t>
<t tx="ekr.20211020091540.1">c.backup_helper(sub_dir='leoPy')
</t>
<t tx="ekr.20220306092217.1">g.cls()
if c.isChanged():
    c.save()
&lt;&lt; prefixes &gt;&gt;
if 0:  # run.cmd runs Nim tests.
    g.execute_shell_commands('run')
else:  # Leo unit test.
    commands = (
        # All commands must start with .test_.
        
        # f"{core}.test_leoUndo",
        f"{core}.test_leoColorizer",
    )
    verbose_flag = ''  # -v
    commands_s = f"python -m unittest {verbose_flag} {' '.join(commands)}"
    g.execute_shell_commands(commands_s)
</t>
<t tx="ekr.20220318085657.1">"""
Find and mark all nodes containing underindented trailing comments in c's outline.

Such comments have the form:
    
    .. some code ..
        A trailing, overindented comment.
"""
g.cls()
import re
pattern = re.compile(r'\w+\s*=\s\w+')

def do_node(p):
    global count
    prev_assign = False
    old_lws = 0
    lines = g.splitLines(p.b)
    for i, line in enumerate(lines):
        lws = g.computeLeadingWhitespaceWidth(line, tab_width=-4)
        if line.strip().startswith('#'):
            if prev_assign and lws &gt; old_lws:
                # Found a likely trailing comment.
                p.setMarked()
                count += 1
                return True
            prev_assign = False
        else:
            old_lws = lws
            prev_assign = pattern.search(line)
    return False
    
count = 0
c.clearAllMarked()
for p in c.all_unique_positions():
    do_node(p)
print(f"found {count} nodes.")
</t>
<t tx="ekr.20220319145807.1">g.cls()

# Monkey-patched git-diff-pr command.
import leo.commands.editFileCommands as efc

rev1 = 'master'  
rev2 = 'ekr-walk-special-case'
x = efc.GitDiffController(c)

@others

# Monkey-patch, with x bound.
x.make_diff_outlines = make_diff_outlines_ignoring_comments
x.diff_two_revs(rev1, rev2)
</t>
<t tx="ekr.20220319151900.1">def make_diff_outlines_ignoring_comments(c1, c2, fn, rev1='', rev2=''):
    """Create an outline-oriented diff from the *hidden* outlines c1 and c2."""
    self = x
    added, deleted, changed = self.compute_dicts(c1, c2)
    table = (
        (added, 'Added'),
        (deleted, 'Deleted'),
        (changed, 'Changed'))
    for d, kind in table:
        if kind.lower() == 'changed':
            for key in d:
                v1, v2 = d.get(key)
                v1.b = strip_comments(v1.b)
                v2.b = strip_comments(v2.b)
        self.create_compare_node(c1, c2, d, kind, rev1, rev2)
</t>
<t tx="ekr.20220319152417.1">def strip_comments(aString):
    """
    Strip everything that looks like a comment from aString.
    It's fine, for now, to ignore strings and docstrings.
    """
    result = []
    lines = g.splitLines(aString)
    for s in lines:
        if s.strip().startswith('#@'):
            # Retain everything that looks like a sentinel.
            result.append(s)
        else:
            # Strip the comment, ignoring the end of the line.
            i = s.find('#')
            if i == -1:
                result.append(s)
            else:
                tail = s[:i]
                if tail.strip():
                    result.append(tail.rstrip() + '\n')
    return ''.join(result)
</t>
<t tx="ekr.20220425052306.1">compound_statement = (
    # Leo doesn't use 'match'
    'async ', 'class ', 'def ', 'else:', 'elif ', 'except',
    'finally:', 'for ', 'if ', 'try:', 'while ', 'with ',
)
pat = re.compile(r'\)\s*-&gt;.*:\s*$')  # End of multiline def.

def convert(p: Any) -&gt; None:
    """Convert all hanging comments in p.b."""
    if p.isAnyAtFileNode():
        print('   Scan:', p.h)
    changed, last, result = False, '', []
    i, lines = 0, p.b.split('\n')
    sep = '-' * 40
    while i &lt; len(lines):
        progress = i
        more_lines = []
        s = lines[i]
        s_s = s.lstrip()
        last_s = last.lstrip()
        lws_s = compute_lws(s)
        lws_last = compute_lws(last)
        if (
            last_s and s_s.startswith('#')
            and not pat.match(last_s)
            and not last_s.startswith(('#', '"""', "'''"))
            and not last_s.endswith(('[', '(', '{', '):'))
            and not last_s.startswith(compound_statement)
            and lws_last &lt; lws_s
        ):
            changed = True
            result.pop()  # Discard the last line!
            j = i + 1  # Look for more indented lines.
            while j &lt; len(lines):
                s2 = lines[j]
                s2_s = s2.strip()
                lws_s2 = compute_lws(s2)
                if lws_s2 &gt;= lws_s and s2_s.startswith('#'):
                    more_lines.append(s2)
                    j += 1
                else:
                    break
            if not more_lines and len(last_s) + len(s_s) &lt; max_line_length:
                # Emit one line.
                result.append(f"{last}  {s_s}")
                if trace:
                    g.printObj([last, s, sep, f"{last}  {s_s}\n"], tag=p.h)
            else:
                # Emit the first comment line.
                result.append(f"{lws_last}{s_s}")
                # Emit any additional comment lines.
                for z in more_lines:
                    result.append(f"{lws_last}{z.lstrip()}")
                # Emit the last (non-comment) line.
                result.append(last)
                if trace:
                    added_lines = [f"{lws_last}{z.lstrip()}" for z in more_lines]
                    g.printObj(
                        [last, s] + more_lines + [sep] +
                        [f"{lws_last}{s_s}"] + added_lines + [last], tag=p.h)
            i += 1 + len(more_lines)
            last = lines[i]
        else:
            result.append(s)
            last = s
            i += 1
        assert progress &lt; i
    if changed:
        print('Changed:', p.h)
        if replace:
            p.b = '\n'.join(result)
</t>
<t tx="ekr.20220425184232.1">def compute_lws(s: str) -&gt; int:
    """Return the leading whitespace of s."""
    n = len(s) - len(s.lstrip())
    return s[:n]
</t>
<t tx="ekr.20220503081113.1">g.cls()
import re
&lt;&lt; init core_p, command_p and globals_p &gt;&gt;
d = {}  # Dict[func-name, True]
# If I were going to do more work I would do the following:
# exclusions: Dict[str, list[str]] = {}
exclusions = set()  # Set[func-name]
@others
# Create d...
scan(core_p)
scan(command_p)
scan(globals_p)
suppress = ('c',)  # 'g', 'p',
count = 0
words = list(sorted(z for z in d.keys() if z not in suppress))
functions_pat = re.compile(fr".*\b({'|'.join(words)})\b\s*[^(]")
# Check functions...
check(core_p)
check(command_p)
check(globals_p)
print('Found', count)
g.printObj(list(sorted(exclusions)), tag='Function appearing in special contexts')
</t>
<t tx="ekr.20220503084045.1">def_pat = re.compile(r'^\s*def ([\w_]+)\s*\(')

def scan(root: "Position") -&gt; None:
    """Add entries in d for all function/method definitions."""
    for p in root.subtree():
        for s in p.b.split('\n'):
            if m := def_pat.match(s):
                name = m.group(1)
                if not name.startswith('__'):
                    d [m.group(1)] = True</t>
<t tx="ekr.20220503084230.1">def check(root: "Position") -&gt; None:
    """Print any functions in d that don't look like a function call."""
    global count
    print('Check:', root.h)
    skipping = None
    for p in root.subtree():
        skipping = False
        if '@language rest' in p.b:
            continue
        for s in p.b.split('\n'):
            ss = s.strip()
            # Handle skipping modes...
            if skipping == '@':
                if ss.startswith('@c'):
                    skipping = None
                continue
            if skipping:
                for skipping in ('"""', "'''"):
                    if skipping in ss:
                        skipping = None
                        continue
                continue
            # Not skipping strings. Ignore comments.
            assert not skipping, repr(skipping)
            i = ss.find('#')
            if i &gt; -1:
                ss = ss[:i].strip()
            if not ss:
                continue
            # Start skipping modes.
            if ss.startswith('@ ') or ss=='@':
                skipping = '@'
                continue
            if ss.count('"""') == 1:
                skipping = '"""'
                continue
            if ss.count("'''") == 1:
                skipping = "'''"
                continue
            if '"' in ss or "'" in ss:  # Ignore lines containing strings.
                continue
            # Skip special cases.
            if ss.startswith((
                '&lt;&lt;', '@cmd', '@g.command',
                'def', 'from', 'import', 'print',
            )):
                continue
            m = functions_pat.match(ss)
            if not m:
                continue
            # The function is in the line.
            # Ignore if it is within any kind of special context.
            h = g.truncate(p.h, 25)
            func = m.group(1)
            args_pat = re.compile(rf".*?[\w_]+\s*\(.*?\b{func}\b.*?\)")
            array_pat = re.compile(rf".*?\b{func}\b\s*(\[|\])")
            op_pat = re.compile(
                rf".*?\b{func}\b\s*(\=|\&lt;|\&gt;|\+|\-|\,|\)|\:|\!|\%|"
                rf"in\b|is\b|and\b|or\b|else\b|if\b|not\b)"
            )
            attr_pat = re.compile(rf".*\b{func}\.")
            if args_pat.match(ss):
                if 0: print(f"  Arg: {h:30} {func:20} {ss}")
                exclusions.add(func)
            elif array_pat.match(ss):
                if 0: print(f"Array: {h:30} {func:20} {ss}")
                exclusions.add(func)
            elif op_pat.match(ss):
                if 0: print(f"   OP: {h:30} {func:20} {ss}")
                exclusions.add(func)
            elif attr_pat.match(ss):
                if 0: print(f" Attr: {h:30} {func:20} {ss}")
                exclusions.add(func)
            else:
                count += 1
                print(f"Found: {h:30} {func:20} {ss}")</t>
<t tx="ekr.20220503084900.1">core_p = g.findNodeAnywhere(c, 'Core classes')
command_p = g.findNodeAnywhere(c, 'Command classes')
globals_p = g.findNodeAnywhere(c, '@file leoGlobals.py')
assert core_p and command_p and globals_p
</t>
<t tx="ekr.20220503193901.1"># 'exception',
# Imports...
    # 'commands', 'cmd', 'core', 'external', 'gui_plugins', 'import_module',
    # 'modes', 'modules',
    # 'os', 'pickle', 'plugins', 'rst3', 'test', 'tests',
# Functions/methods...
# 'caller', 'callers', 'copy', 'count', 'end', 'fileName',
# 'ivars', 'key', 'kind', 'level', 'match', 'remove', 'trace',
    # 'add', 'add_to_dot', 'backup', 'blank',
    # 'caller', 'callers', 'children', 'clone', 'cls', 'command_name', 'commanders',
    # 'commit', 'convert', 'copy', 'count',
    # 'delegate', 'do', 'done', 'dump', 'encode', 'end', 'error', 'es', 'exists', 'expand',
    # 'filename', 'fileName', 'find', 'flush', 'get',
    # 'handler', 'handler1', 'handler2', 'hash',
    # 'IdleTime', 'ignore', 'indent', 'it', 'items', 'ivars', 'join', 'key', 'keys', 'kind',
    # 'level', 'lt', 'lower', 'lws', 'match', 'message', 'name', 'new', 'next', 'nodes', 'note',
    # 'on_idle', 'open', 'parents', 'path', 'predicate', 'put',
    # 'read', 'readline', 'red', 'redoHelper', 'remove', 'replace', 'report', 'rt',
    # 'scan', 'select', 'set', 'show', 'start', 'stop',
    # 'toString', 'toUnicode', 'trace', 'translateString',
    # 'underline', 'undoHelper', 'unl', 'values', 'visit',
    # 'warn', 'warning', 'word',</t>
<t tx="ekr.20220527065937.1">g.cls()
import json
import os
import textwrap
path = r'C:\Repos\leo-editor\mypy_stubs\3.9\leo\core\leoApp.data.json'
with open(path, 'r') as f:
    d = json.load(f)

def make_outline(d, p, topFlag):
    """Set p.b from dict d. Generate child nodes for inner dicts.."""
    result = []
    for key, value in d.items():
        if isinstance(value, dict):
            h2 = 'top' if topFlag else p.h[2:-2].strip()
            section_name = g.angleBrackets(f" {h2}.{key} ")
            result.append(f'"{key}": {{\n')
            result.append(f"    {section_name}\n")
            result.append('}\n')
            child = p.insertAsLastChild()
            child.h = section_name
            make_outline(value, child, topFlag=False)
        elif isinstance(value, str):
            result.append(f'"{key}": "{value}"\n')
        else:
            result.append(f'"{key}": {value}\n')
    p.b = ''.join(result)

# Recursively make the outline.
top = c.lastTopLevel().insertAfter()
top.h = os.path.basename(path)
make_outline(d, top, topFlag=True)
# Adjust top.b.
top.b = f"{{\n{textwrap.indent(top.b.strip(),' '*4)}\n}}\n"
c.redraw(top)
    </t>
<t tx="ekr.20220823195205.1">"""
Stand alone GUI free index builder for Leo's full text search system::

  python leoftsindex.py &lt;file1&gt; &lt;file2&gt; &lt;file3&gt;...

If the file name starts with @ it's a assumed to be a simple
text file listing files to be indexed.

If &lt;file&gt; does not contain '#' it's assumed to be a .leo file
to index, and is indexed.

If &lt;file&gt; does contain '#' it's assumed to be a .leo file
containing a list of .leo files to index, with the list in
the node indicated by the UNL after the #, e.g.::

   path/to/myfile.leo#Lists--&gt;List of outlines

In the latter case, if the node identified by the UNL has children,
the list of files to scan is built from the first line of the body
of each child node of the identified node (works well with bookmarks.py).
If the node identified by the UNL does not have children, the
node's body is assumed to be a simple text listing of paths to .leo files).

.. note::

    It may be necessary to quote the "file" on the command line,
    as the '#' may be interpreted as a comment delimiter::

        python leoftsindex.py "workbook.leo#Links"


"""

import sys
# add folder containing 'leo' folder to path
# sys.path.append("/home/tbrown/Package/leo/bzr/leo.repo/trunk")
import leo.core.leoBridge as leoBridge
import leo.plugins.leofts as leofts

controller = leoBridge.controller(
    gui='nullGui',
    loadPlugins=False,  # True: attempt to load plugins.
    readSettings=False,  # True: read standard settings files.
    silent=False,  # True: don't print signon messages.
    verbose=False
)
g = controller.globals()

# list of "files" to process
files = sys.argv[1:]

# set up leofts
leofts.set_leo(g)
g._gnxcache = leofts.GnxCache()
fts = leofts.get_fts()

fn2c = {}  # cache to avoid loading same outline twice
done = set()  # outlines scanned, to avoid repetition repetition

todo = list(files)

while todo:

    item = todo.pop(0)

    print("INDEX: %s" % item)

    if '#' in item:
        fn, node = item.split('#', 1)
    else:
        fn, node = item, None

    if node:
        c = fn2c.setdefault(fn, controller.openLeoFile(fn))
        found, dummy, p = g.recursiveUNLSearch(node.split('--&gt;'), c)
        if not found:
            print("Could not find '%s'" % item)
            break
        if not p:
            p = c.p
        if p.hasChildren():
            # use file named in first node of each child
            files = [chl.b.strip().split('\n', 1)[0].strip() for chl in p.children()]
        else:
            # use all files listed in body
            files = [i.strip() for i in p.b.strip().split('\n')]

    elif fn.startswith('@'):
        todo.extend(open(fn[1:]).read().strip().split('\n'))
        files = []

    else:
        files = [fn]

    for fn in files:

        # file names may still have '#' if taken from a node list
        real_name = fn.split('#', 1)[0]
        if real_name in done:
            continue
        done.add(real_name)

        if len(files) != 1:
            print(" FILE: %s" % real_name)

        c = fn2c.setdefault(real_name, controller.openLeoFile(fn))
        fts.drop_document(real_name)
        fts.index_nodes(c)
@language python
@tabwidth -4
</t>
<t tx="ekr.20220904210247.1"># This is a copy of the @enabled-plugins node from leoSettings.leo,
# ensuring that the @enabled-plugins node in myLeoSettings.leo has no effect.

# Standard plugins...

plugins_menu.py     # Adds 'Plugins' menu.
mod_scripting.py
contextmenu.py      # Required by the vim.py and xemacs.py plugins.
nav_qt.py           # Forward/back buttons &amp; goto-next/prev-history-node
viewrendered.py     # (Or viewrendered3.py) Plugins menu support.

# Disabled standard menus...

# mod_autosave.py   # Creates .bak files.
# nodetags.py       # Supports tags via uA's.
# quicksearch.py      # Nav pane.
# todo.py             # Task pane.
</t>
<t tx="ekr.20221129012213.1"># See flake8 settings in setup.cfg.</t>
<t tx="ekr.20221201043917.1">@language batch
@echo off
cd %~dp0..\..

call reindent-leo.cmd

echo test-leo
py -m unittest %*
</t>
<t tx="ekr.20221204070905.1"></t>
<t tx="ekr.20221204071056.1">@language batch
@echo off
cd %~dp0..\..

echo pylint-leo
time /T
call py -m pylint leo --extension-pkg-allow-list=PyQt6.QtCore,PyQt6.QtGui,PyQt6.QtWidgets %*
time /T
</t>
<t tx="ekr.20221204071146.1">@language batch
@echo off
cd %~dp0..\..

rem See leo-editor/.mypy.ini for exclusions!
rem Always use the fast (official) version of mypy.

echo mypy-leo
py -m mypy --debug-cache leo %*
</t>
<t tx="ekr.20221204071220.1">@language batch
@echo off
cls
cd %~dp0..\..

echo test-one-leo
call py -m unittest leo.unittests.core.test_leoGlobals.TestGlobals.test_g_handleScriptException
</t>
<t tx="ekr.20221204071554.1">@language batch
@echo off
cls
cd %~dp0..\..

rem Run all of Leo's pre-commit tests.

call tbo.cmd --force
call python312 -m unittest
call ruff-leo.cmd
call mypy-leo.cmd
echo Done!</t>
<t tx="ekr.20221204072154.1">@language batch
@echo off
cd %~dp0..\..

:: Save path to reindent.py to a file .leo\reindent-path.txt
call py %~dp0\find-reindent.py

set PATH_FILE=%USERPROFILE%\.leo\reindent-path.txt
set /P "REINDENT_PATH="&lt; %PATH_FILE%

:: echo %REINDENT_PATH%

if "%REINDENT_PATH%"=="" goto no_reindent

echo reindent-leo

rem echo reindent leo/core
call py %REINDENT_PATH% -r leo\core
rem echo reindent leo/commands
call py %REINDENT_PATH% -r leo\commands
rem echo reindent leo/plugins/importers
call py %REINDENT_PATH% -r leo\plugins\importers
rem echo reindent leo/plugins/commands
call py %REINDENT_PATH% leo\plugins\qt_commands.py
call py %REINDENT_PATH% leo\plugins\qt_events.py
call py %REINDENT_PATH% leo\plugins\qt_frame.py
call py %REINDENT_PATH% leo\plugins\qt_gui.py
call py %REINDENT_PATH% leo\plugins\qt_idle_time.py
call py %REINDENT_PATH% leo\plugins\qt_text.py
call py %REINDENT_PATH% leo\plugins\qt_tree.py
rem echo reindent leo/plugins/writers
call py %REINDENT_PATH% -r leo\plugins\writers
rem echo reindent leo/unittests
call py %REINDENT_PATH% -r leo\unittests
rem echo reindent official plugins.
call py %REINDENT_PATH% leo\plugins\indented_languages.py
goto done

:no_reindent
echo Cannot find reindent.py, skipping reindentation

:done
</t>
<t tx="ekr.20221204072456.1">@language batch
@echo off
cd %~dp0..\..

echo beautify-leo

call py -m leo.core.leoAst --orange --verbose leo\core
call py -m leo.core.leoAst --orange --verbose leo\commands
call py -m leo.core.leoAst --orange --verbose leo\plugins
call py -m leo.core.leoAst --orange --verbose leo\modes
</t>
<t tx="ekr.20221204074235.1">@language batch
@echo off
cd %~dp0..\..

rem: See leo-editor/setup.cfg for defaults.

echo flake8-leo
py -m flake8 %*
</t>
<t tx="ekr.20230115020533.1">@language batch
@echo off
cd %~dp0..\..

rem not recommended!
echo black leo.core
call py -m black --skip-string-normalization leo\core
</t>
<t tx="ekr.20230206004301.1">@language batch
@echo off
cls
rem -a: write all files  (make clean)
cd %~dp0..\..
cd leo\doc\html

echo.
echo sphinx-build -a (make clean)
echo.
sphinx-build -M html . _build -a
</t>
<t tx="ekr.20230508145335.1"># These tests load (once) all files in leo/core, leo/commands and leo/plugins/qt_*.py.
g.cls()
g.execute_shell_commands(
    'python -m unittest '
    # 'leo.unittests.test_design.TestAnnotations.slow_test_all_paths '
    # 'leo.unittests.test_design.TestChains.slow_test_all_paths'
    # 'leo.unittests.core.test_leoImport.TestLeoImport.slow_test_ric_run',
    # 'leo.unittests.commands.test_editFileCommands.TestEditFileCommands.verbose_test_git_diff',
    # f" {commands}.test_editFileCommands.TestEditFileCommands.slow_test_gdc_node_history",

)
</t>
<t tx="ekr.20230511074046.1">commands = 'leo.unittests.commands'
core = 'leo.unittests.core'
gui = 'leo.unittests.test_gui'
importers = 'leo.unittests.plugins.test_importers'
misc = 'leo.unittests.misc_tests'
plugins = 'leo.unittests.plugins'
syntax = 'leo.unittests.plugins.test_syntax'
writers = 'leo.unittests.plugins.test_writers'

# f"{core}.test_leoAst",
# f"{core}.test_leoGlobals",
# f"{core}.test_leoTokens",

# f"{misc}.test_design",
# f"{misc}.test_doctests",
# f"{misc}.test_syntax",

# f"{plugins}.test_gui",
# f"{plugins}.test_importers",
# f"{plugins}.test_plugins",
# f"{plugins}.test_writers",
</t>
<t tx="ekr.20230624114517.1"></t>
<t tx="ekr.20230628105236.1">@language batch
@echo off
cd %~dp0..\..

rem qt_main.py is auto generated.
rem call py -m ruff leo/plugins/qt*.py

echo ruff leo/core, leo/commands, leo/plugins/qt...
call py -m ruff leo/core
call py -m ruff leo/commands
call py -m ruff leo/plugins/qt_gui.py
call py -m ruff leo/plugins/qt_text.py
call py -m ruff leo/plugins/qt_tree.py
</t>
<t tx="ekr.20230702120645.1"></t>
<t tx="ekr.20230717210524.1"></t>
<t tx="ekr.20230720115916.1">g.cls()
import leo.commands.editFileCommands as efc

x = efc.GitDiffController(c=c)
path = g.os_path_finalize_join(g.app.loadDir, 'leoGlobals.py')
gnxs = (
    'ekr.20230626064652.1',  # EKR's replacement gnx
    'tbrown.20140311095634.15188',  # Terry's original node.
)
x.node_history(path, gnxs, limit=60)
</t>
<t tx="ekr.20231107062256.1">"""Ensure that all expected @&lt;file&gt; nodes exist."""
g.cls()
import glob
import os
join, sep = os.path.join, os.sep

def norm(path):
    return os.path.normpath(path).lower()

# Compute the directories.
leo_dir = norm(join(g.app.loadDir, '..'))  ### '..'))
core_dir = join(leo_dir, 'core')
commands_dir = join(leo_dir, 'commands')
external_dir = join(leo_dir, 'external')
importers_dir = join(leo_dir, 'plugins', 'importers')
plugins_dir = join(leo_dir, 'plugins')
unittests_dir = join(leo_dir, '..', 'unittests')
writers_dir = join(leo_dir, 'plugins', 'writers')

def make_list(pattern):
    return [norm(z) for z in glob.glob(pattern) if '__init__' not in z]

# Find paths on disk.
core_files = make_list(f"{core_dir}{sep}*.py")
commands_files = make_list(f"{commands_dir}{sep}*.py")
external_files = make_list(f"{external_dir}{sep}*.py")
importer_files = make_list(f"{importers_dir}{sep}*.py")
# plugin_files = make_list(f"{plugins_dir}{sep}*.py")
qt_files = make_list(f"{plugins_dir}{sep}qt*.py")
unittests_files = make_list(f"{unittests_dir}{sep}*.py")
writer_files = make_list(f"{writers_dir}{sep}*.py")

# Compute paths from @&lt;file&gt; nodes.
at_file_paths = sorted([
    norm(c.fullPath(z))
        for z in c.all_unique_positions()
            if z.isAnyAtFileNode()
])

excluded_files = (
    r'plugins\qt_main.py',  # Generated automatically.
    r'plugins\baseNativeTree.py',  # No longer used.
)

def is_excluded(path):
    return any(z in path for z in excluded_files)
    
if 0:
    for files, kind in (
        (at_file_paths, 'all known paths'),
        (core_files, 'core_files'),
        (qt_files, 'qt_files'),
        (importer_files, 'importer_files'),
        (writer_files, 'writer_files'),
    ):
        g.printObj(files, tag=f"{kind}")

# Ensure that @&lt;file&gt; nodes exist for every file on disk.
missing = []
for z in core_files + external_files + qt_files + importer_files + writer_files:
    if z not in at_file_paths and not is_excluded(z):
        missing.append(z)
if missing:
    g.printObj(missing, tag='missing @&lt;file&gt; nodes')
else:
    print('No missing files!')
print('done')</t>
<t tx="ekr.20231114224211.1">@language batch
@echo off
cd %~dp0..\..

echo beautify-leo

call py -m leo.core.leoAst --orange --force --verbose leo\core
call py -m leo.core.leoAst --orange --force --verbose leo\commands

rem It's ok to beautify everything:

call py -m leo.core.leoAst --orange --verbose leo\plugins
call py -m leo.core.leoAst --orange --verbose leo\modes

rem call py -m leo.core.leoAst --orange --force --verbose leo\plugins\importers
rem call py -m leo.core.leoAst --orange --force --verbose leo\plugins\writers
</t>
<t tx="ekr.20231120070819.1"></t>
<t tx="ekr.20231218084055.10">if 1 { // # pragma: no cover;
    @others
}
</t>
<t tx="ekr.20231218084055.100">fn do_string(self) -&gt; None {
    /// Handle a 'string' token.
    # Careful: continued strings may contain "\r"
    let val = regularize_nls(self.val);
    self.add_token("string", val);
    self.blank();
}
</t>
<t tx="ekr.20231218084055.101">beautify_pat = re.compile(
    r"#\s*pragma:\s*beautify\b|#\s*@@beautify|#\s*@\+node|#\s*@[+-]others|;  // \s*@[+-]&lt;&lt;")

fn do_verbatim(self) -&gt; None {
    /// Handle one token in verbatim mode.
    /// End verbatim mode when the appropriate comment is seen.
    let kind = self.kind;

    // Careful: tokens may contain '\r'
    let val = regularize_nls(self.val);
    if kind == "comment" {
        if self.beautify_pat.match(val) {
            let self.verbatim = false;
        }
        let val = val.rstrip();
        self.add_token("comment", val);
        None
    }
    if kind == "indent" {
        self.level += 1;
        let self.lws = self.level * self.tab_width * " ";
    }
    if kind == "dedent" {
        self.level -= 1;
        let self.lws = self.level * self.tab_width * " ";
    }
    self.add_token("verbatim", val);
}
</t>
<t tx="ekr.20231218084055.102">fn do_ws(self) -&gt; None {
    /// Handle the "ws" pseudo-token.
    ///
    /// Put the whitespace only if if ends with backslash-newline.
    let val = self.val;
    // Handle backslash-newline.
    if "\\\n" in val {
        self.clean("blank");
        self.add_token("op-no-blanks", val);
        None
    }
    // Handle start-of-line whitespace.
    let prev = self.code_list[-1];
    let inner = self.paren_level || self.square_brackets_stack || self.curly_brackets_level;
    if prev.kind == "line-indent" &amp;&amp; inner {
        // Retain the indent that won't be cleaned away.
        self.clean("line-indent");
        self.add_token("hard-blank", val);
    }
}
</t>
<t tx="ekr.20231218084055.103"></t>
<t tx="ekr.20231218084055.104">fn add_line_end(self) -&gt; Token {
    /// Add a line-end request to the code list.
    # This may be called from do_name as well as do_newline and do_nl.
    // assert self.token.kind in ('newline', 'nl'), self.token.kind;
    self.clean("blank")  // Important!
    self.clean("line-indent");
    let t = self.add_token("line-end", "\n");
    // Distinguish between kinds of 'line-end' tokens.
    let t.newline_kind = self.token.kind;
    t
}
</t>
<t tx="ekr.20231218084055.105">fn add_token(self, kind: String:, value: Any) -&gt; Token {
    /// Add an output token to the code list.
    let tok = Token(kind, value)
    let tok.index = len(self.code_list);
    self.code_list.append(tok);
    tok
}
</t>
<t tx="ekr.20231218084055.106">fn blank(self) -&gt; None {
    /// Add a blank request to the code list.
    let prev = self.code_list[-1]
    if prev.kind ! in (
        "blank",
        "blank-lines",
        "file-start",
        "hard-blank",;  // Unique to orange.
        "line-end",
        "line-indent",
        "lt",
        "op-no-blanks",
        "unary-op",
    ):
        self.add_token("blank", " ");
}
</t>
<t tx="ekr.20231218084055.107">fn blank_lines(self, n: i32) -&gt; None {
    /// Add a request for n blank lines to the code list.
    /// Multiple blank-lines request yield at least the maximum of all requests.
    self.clean_blank_lines();
    let prev = self.code_list[-1];
    if prev.kind == "file-start" {
        self.add_token("blank-lines", n);
        None
    }
    for (_i in range(0, n + 1)) {
        self.add_token("line-end", "\n");
    }
    // Retain the token (intention) for debugging.
    self.add_token("blank-lines", n);
    self.line_indent();
}
</t>
<t tx="ekr.20231218084055.108">fn clean(self, kind: String:) -&gt; None {
    /// Remove the last item of token list if it has the given kind.
    let prev = self.code_list[-1]
    if prev.kind == kind {
        self.code_list.pop();
    }
}
</t>
<t tx="ekr.20231218084055.109">fn clean_blank_lines(self) -&gt; bool {
    /// Remove all vestiges of previous blank lines.
    ///
    /// Return True if any of the cleaned 'line-end' tokens represented "hard" newlines.
    let cleaned_newline = false;
    let table = ("blank-lines", "line-end", "line-indent");
    while (self.code_list[-1].kind in table) {
        let t = self.code_list.pop();
        if t.kind == "line-end" &amp;&amp; getattr(t, "newline_kind", None) != "nl" {
            let cleaned_newline = true;
        }
    }
    cleaned_newline
}
</t>
<t tx="ekr.20231218084055.11">fn check_g() -&gt; bool {
    /// print an error message if g is None
    if not g:
        print("This statement failed: `from leo.core import leoGlobals as g`");
        print("Please adjust your Python path accordingly");
    bool(g)
}
</t>
<t tx="ekr.20231218084055.110">fn colon(self, val: String:) -&gt; None {
    /// Handle a colon.

    fn is_expr(node: Node) -&gt; bool {
        /// True if node is any expression other than += number.
        if isinstance(node, (ast.BinOp, ast.Call, ast.IfExp)):
            True
        // num_node = ast.Num if g.python_version_tuple &lt; (3, 12, 0) else ast.Constant;
        let num_node = if g.python_version_tuple &lt; (3, 12, 0) {ast.Num} else {ast.Constant};
        (
            isinstance(node, ast.UnaryOp);
            &amp;&amp; ! isinstance(node.operand, num_node);
        );
    }

    let node = self.token.node;
    self.clean("blank");
    if ! isinstance(node, ast.Slice) {
        self.add_token("op", val);
        self.blank();
        None
    }
    // A slice.
    let lower = getattr(node, "lower", None);
    let upper = getattr(node, "upper", None);
    let step = getattr(node, "step", None);
    if any(is_expr(z) for z in (lower, upper, step)) {
        let prev = self.code_list[-1];
        if prev.value ! in "[ { // ":
            self.blank();
        }
        self.add_token("op", val);
        self.blank();
    }
    else {
        self.add_token("op-no-blanks", val);
    }
}
</t>
<t tx="ekr.20231218084055.111">fn line_end(self) -&gt; None {
    /// Add a line-end request to the code list.
    # This should be called only be do_newline and do_nl.
    node, token = self.token.statement_node, self.token;
    // assert token.kind in ('newline', 'nl'), (token.kind, g.callers());
    // Create the 'line-end' output token.
    self.add_line_end();
    // Attempt to split the line.
    let was_split = self.split_line(node, token);
    // Attempt to join the line only if it has not just been split.
    if ! was_split &amp;&amp; self.max_join_line_length &gt; 0 {
        self.join_lines(node, token);
    }
    // Add the indentation for all lines
    // until the next indent or unindent token.
    self.line_indent();
}
</t>
<t tx="ekr.20231218084055.112">fn line_indent(self) -&gt; None {
    /// Add a line-indent token.
    self.clean("line-indent")  # Defensive. Should never happen.
    self.add_token("line-indent", self.lws);
}
</t>
<t tx="ekr.20231218084055.113"></t>
<t tx="ekr.20231218084055.114">fn lt(self, val: String:) -&gt; None {
    /// Generate code for a left paren or curly/square bracket.
    assert val in "([{", repr(val)
    if val == "(" {
        self.paren_level += 1;
    }
    else if (val == "[") {
        self.square_brackets_stack.append(false);
    }
    else {
        self.curly_brackets_level += 1;
    }
    self.clean("blank");
    let prev = self.code_list[-1];
    if prev.kind in ("op", "word-op") {
        self.blank();
        self.add_token("lt", val);
    }
    else if (prev.kind == "word") {
        // Only suppress blanks before '(' or '[' for non-keywords.
        if val == "{" || prev.value in ("if", "else", "return", "for") {
            self.blank();
        }
        else if (val == "(") {
            self.in_arg_list += 1;
        }
        self.add_token("lt", val);
    }
    else {
        self.clean("blank");
        self.add_token("op-no-blanks", val);
    }
}
</t>
<t tx="ekr.20231218084055.115">fn rt(self, val: String:) -&gt; None {
    /// Generate code for a right paren or curly/square bracket.
    assert val in ")]}", repr(val)
    if val == ")" {
        self.paren_level -= 1;
        let self.in_arg_list = max(0, self.in_arg_list - 1);
    }
    else if (val == "]") {
        self.square_brackets_stack.pop();
    }
    else {
        self.curly_brackets_level -= 1;
    }
    self.clean("blank");
    self.add_token("rt", val);
}
</t>
<t tx="ekr.20231218084055.116">fn possible_unary_op(self, s: String:) -&gt; None {
    /// Add a unary or binary op to the token list.
    let node = self.token.node
    self.clean("blank");
    if isinstance(node, ast.UnaryOp) {
        self.unary_op(s);
    }
    else {
        self.blank();
        self.add_token("op", s);
        self.blank();
    }
}

fn unary_op(self, s: String:) -&gt; None {
    /// Add an operator request to the code list.
    assert s and isinstance(s, str), repr(s)
    self.clean("blank");
    let prev = self.code_list[-1];
    if prev.kind == "lt" {
        self.add_token("unary-op", s);
    }
    else {
        self.blank();
        self.add_token("unary-op", s);
    }
}
</t>
<t tx="ekr.20231218084055.117">fn star_op(self) -&gt; None {
    /// Put a '*' op, with special cases for *args.
    let val = "*"
    let node = self.token.node;
    self.clean("blank");
    if isinstance(node, ast.arguments) {
        self.blank();
        self.add_token("op", val);
        # #2533
    }
    if self.paren_level &gt; 0 {
        let prev = self.code_list[-1];
        if prev.kind == "lt" || (prev.kind, prev.value) == ("op", ",") {
            self.blank();
            self.add_token("op", val);
            None
        }
    }
    self.blank();
    self.add_token("op", val);
    self.blank();
}
</t>
<t tx="ekr.20231218084055.118">fn star_star_op(self) -&gt; None {
    /// Put a ** operator, with a special case for **kwargs.
    let val = "**"
    let node = self.token.node;
    self.clean("blank");
    if isinstance(node, ast.arguments) {
        self.blank();
        self.add_token("op", val);
        # #2533
    }
    if self.paren_level &gt; 0 {
        let prev = self.code_list[-1];
        if prev.kind == "lt" || (prev.kind, prev.value) == ("op", ",") {
            self.blank();
            self.add_token("op", val);
            None
        }
    }
    self.blank();
    self.add_token("op", val);
    self.blank();
}
</t>
<t tx="ekr.20231218084055.119">fn word(self, s: String:) -&gt; None {
    /// Add a word request to the code list.
    assert s and isinstance(s, str), repr(s)
    let node = self.token.node;
    if isinstance(node, ast.ImportFrom) &amp;&amp; s == "import" { // # #2533;
        self.clean("blank");
        self.add_token("blank", " ");
        self.add_token("word", s);
    }
    else if (self.square_brackets_stack) {
        // A previous 'op-no-blanks' token may cancel this blank.
        self.blank();
        self.add_token("word", s);
    }
    else if (self.in_arg_list &gt; 0) {
        self.add_token("word", s);
        self.blank();
    }
    else {
        self.blank();
        self.add_token("word", s);
        self.blank();
    }
}

fn word_op(self, s: String:) -&gt; None {
    /// Add a word-op request to the code list.
    assert s and isinstance(s, str), repr(s)
    self.blank();
    self.add_token("word-op", s);
    self.blank();
}
</t>
<t tx="ekr.20231218084055.12">fn get_modified_files(repo_path: String:) -&gt; list[String:] {
    /// Return the modified files in the given repo.
    if not repo_path:
        []
    let old_cwd = os.getcwd();
    os.chdir(repo_path);
    try {
        // We are not checking the return code here, so:
        // pylint: disable=subprocess-run-check
        let result = subprocess.run(["git", "status", "--porcelain"], capture_output=true, text=true);
        if result.returncode != 0 {
            print("Error running git command");
            []
        }
        modified_files = [];
        for (line in result.stdout.split("\n")) {
            if line.startswith((" M", "M ", "A ", " A")) {
                modified_files.append(line[3:]);
            }
        }
        [os.path.abspath(z) for z in modified_files]
    }
    finally {
        os.chdir(old_cwd);
    }
}
</t>
<t tx="ekr.20231218084055.120"></t>
<t tx="ekr.20231218084055.121">fn split_line(self, node: Node, token: Token) -&gt; bool {
    /// Split token's line, if possible and enabled.
    ///
    /// Return True if the line was broken into two or more lines.
    // assert token.kind in ('newline', 'nl'), repr(token);
    // Return if splitting is disabled:
    if self.max_split_line_length &lt;= 0 { // # pragma: no cover (user option);
        False
    }
    // Return if the node can't be split.
    if ! is_long_statement(node) {
        False
    }
    // Find the *output* tokens of the previous lines.
    let line_tokens = self.find_prev_line();
    let line_s = "".join([z.to_string() for z in line_tokens]);
    // Do nothing for short lines.
    if len(line_s) &lt; self.max_split_line_length {
        False
    }
    // Return if the previous line has no opening delim: (, [ or {.
    if ! any(z.kind == "lt" for z in line_tokens) { // # pragma: no cover (defensive);
        False
    }
    let prefix = self.find_line_prefix(line_tokens);
    // Calculate the tail before cleaning the prefix.
    let tail = line_tokens[len(prefix) :];
    // Cut back the token list: subtract 1 for the trailing line-end.
    let self.code_list = self.code_list[: len(self.code_list) - len(line_tokens) - 1];
    // Append the tail, splitting it further, as needed.
    self.append_tail(prefix, tail);
    // Add the line-end token deleted by find_line_prefix.
    self.add_token("line-end", "\n");
    True
}
</t>
<t tx="ekr.20231218084055.122">fn append_tail(self, prefix: list[Token], tail: list[Token]) -&gt; None {
    /// Append the tail tokens, splitting the line further as necessary.
    let tail_s = "".join([z.to_string() for z in tail])
    if len(tail_s) &lt; self.max_split_line_length {
        // Add the prefix.
        self.code_list.extend(prefix);
        // Start a new line and increase the indentation.
        self.add_token("line-end", "\n");
        self.add_token("line-indent", self.lws + " " * 4);
        self.code_list.extend(tail);
        None
    }
    // Still too long.  Split the line at commas.
    self.code_list.extend(prefix);
    // Start a new line and increase the indentation.
    self.add_token("line-end", "\n");
    self.add_token("line-indent", self.lws + " " * 4);
    let open_delim = Token(kind="lt", value=prefix[-1].value);
    let value = open_delim.value.replace("(", ")").replace("[", "]").replace("{", "}");
    let close_delim = Token(kind="rt", value=value);
    let delim_count = 1;
    let lws = self.lws + " " * 4;
    for (i, t in enumerate(tail)) {
        if t.kind == "op" &amp;&amp; t.value == "," {
            if delim_count == 1 {
                // Start a new line.
                self.add_token("op-no-blanks", ",");
                self.add_token("line-end", "\n");
                self.add_token("line-indent", lws);
                // Kill a following blank.
                if i + 1 &lt; len(tail) {
                    let next_t = tail[i + 1];
                    if next_t.kind == "blank" {
                        let next_t.kind = "no-op";
                        let next_t.value = "";
                    }
                }
            }
            else {
                self.code_list.append(t);
            }
        }
        else if (t.kind == close_delim.kind &amp;&amp; t.value == close_delim.value) {
            // Done if the delims match.
            delim_count -= 1;
            if delim_count == 0 {
                // Start a new line
                self.add_token("op-no-blanks", ",");
                self.add_token("line-end", "\n");
                self.add_token("line-indent", self.lws);
                self.code_list.extend(tail[i:]);
                None
            }
            let lws = lws[:-4];
            self.code_list.append(t);
        }
        else if (t.kind == open_delim.kind &amp;&amp; t.value == open_delim.value) {
            delim_count += 1;
            let lws = lws + " " * 4;
            self.code_list.append(t);
        }
        else {
            self.code_list.append(t);
        }
    }
    g.trace("BAD DELIMS", delim_count);  // pragma: no cover
}
</t>
<t tx="ekr.20231218084055.123">fn find_prev_line(self) -&gt; list[Token] {
    /// Return the previous line, as a list of tokens.
    let line = []
    for (t in reversed(self.code_list[:-1])) {
        if t.kind in ("hard-newline", "line-end") {
            break;
        }
        line.append(t);
    }
    list(reversed(line))
}
</t>
<t tx="ekr.20231218084055.124">fn find_line_prefix(self, token_list: list[Token]) -&gt; list[Token] {
    /// Return all tokens up to and including the first lt token.
    /// Also add all lt tokens directly following the first lt token.
    let result = [];
    for (t in token_list) {
        result.append(t);
        if t.kind == "lt" {
            break;
        }
    }
    result
}
</t>
<t tx="ekr.20231218084055.125">fn join_lines(self, node: Node, token: Token) -&gt; None {
    /// Join preceding lines, if possible and enabled.
    /// token is a line_end token. node is the corresponding ast node.
    if self.max_join_line_length &lt;= 0 { // # pragma: no cover (user option);
        None
    }
    // assert token.kind in ('newline', 'nl'), repr(token);
    if token.kind == "nl" {
        None
    }
    // Scan backward in the *code* list,
    // looking for 'line-end' tokens with tok.newline_kind == 'nl'
    let nls = 0;
    let i = len(self.code_list) - 1;
    let t = self.code_list[i];
    // assert t.kind == 'line-end', repr(t);
    // Not all tokens have a newline_kind ivar.
    // assert t.newline_kind == 'newline';
    i -= 1;
    while (i &gt;= 0) {
        let t = self.code_list[i];
        if t.kind == "comment" {
            // Can't join.
            None
        }
        if t.kind == "string" &amp;&amp; ! self.allow_joined_strings {
            // An EKR preference: don't join strings, no matter what black does.
            // This allows "short" f-strings to be aligned.
            None
        }
        if t.kind == "line-end" {
            if getattr(t, "newline_kind", None) == "nl" {
                nls += 1;
            }
            else {
                break;  // pragma: no cover
            }
        }
        i -= 1;
    }
    // Retain at the file-start token.
    if i &lt;= 0 {
        let i = 1;
    }
    if nls &lt;= 0 { // # pragma: no cover (rare);
        None
    }
    // Retain line-end and and any following line-indent.
    // Required, so that the regex below won't eat too much.
    while (true) {
        let t = self.code_list[i];
        if t.kind == "line-end" {
            if getattr(t, "newline_kind", None) == "nl" { // # pragma: no cover (rare);
                nls -= 1;
            }
            i += 1;
        }
        else if (self.code_list[i].kind == "line-indent") {
            i += 1;
        }
        else {
            break;  // pragma: no cover (defensive)
        }
    }
    if nls &lt;= 0 { // # pragma: no cover (defensive);
        None
    }
    // Calculate the joined line.
    let tail = self.code_list[i:];
    let tail_s = tokens_to_string(tail);
    let tail_s = re.sub(r"\n\s*", " ", tail_s);
    let tail_s = tail_s.replace("( ", "(").replace(" )", ")");
    let tail_s = tail_s.rstrip();
    // Don't join the lines if they would be too long.
    if len(tail_s) &gt; self.max_join_line_length { // # pragma: no cover (defensive);
        None
    }
    // Cut back the code list.
    let self.code_list = self.code_list[:i];
    // Add the new output tokens.
    self.add_token("string", tail_s);
    self.add_token("line-end", "\n");
}
</t>
<t tx="ekr.20231218084055.126">struct ParseState {
    /// A class representing items in the parse state stack.
    ///
    /// The present states:
    ///
    /// 'file-start': Ensures the stack stack is never empty.
    ///
    /// 'decorator': The last '@' was a decorator.
    ///
    /// do_op():    push_state('decorator')
    /// do_name():  pops the stack if state.kind == 'decorator'.
    ///
    /// 'indent': The indentation level for 'class' and 'def' names.
    ///
    /// do_name():      push_state('indent', self.level)
    /// do_dendent():   pops the stack once or twice if state.value == self.level.
    ///

    fn __init__(self, kind: String:, value: Union[i32, String:]) -&gt; None {
        let self.kind = kind;
        let self.value = value;
    }

    fn __repr__(self) -&gt; String: {
        f!"State: {self.kind} {self.value!r}"  # pragma: no cover
    }

    let __str__ = __repr__;
}
</t>
<t tx="ekr.20231218084055.127">struct ReassignTokens {
    /// A class that reassigns tokens to more appropriate ast nodes.
    @others
}
</t>
<t tx="ekr.20231218084055.128">fn reassign(self, filename: String:, tokens: list[Token], tree: Node) -&gt; None {
    /// The main entry point.
    let self.filename = filename
    let self.tokens = tokens;
    // Just handle Call nodes.
    for (node in ast.walk(tree)) {
        if isinstance(node, ast.Call) {
            self.visit_call(node);
        }
    }
}
</t>
<t tx="ekr.20231218084055.129">fn visit_call(self, node: Node) -&gt; None {
    /// ReassignTokens.visit_call
    let tokens = tokens_for_node(self.filename, node, self.tokens)
    node0, node9 = tokens[0].node, tokens[-1].node;
    let nca = nearest_common_ancestor(node0, node9);
    if ! nca {
        None
    }
    // Associate () with the call node.
    let i = tokens[-1].index;
    let j = find_paren_token(i + 1, self.tokens);
    if j == None {
        # pragma: no cover
    }
    let k = find_paren_token(j + 1, self.tokens);
    if k == None {
        # pragma: no cover
    }
    let self.tokens[j].node = nca;
    let self.tokens[k].node = nca;
    add_token_to_token_list(self.tokens[j], nca);
    add_token_to_token_list(self.tokens[k], nca);
}
</t>
<t tx="ekr.20231218084055.13">fn scan_ast_args() -&gt; tuple[Any, dict[String:, Any], list[String:]] {
    let description = textwrap.dedent("""\;
        Execute fstringify || beautify commands contained in leoAst.py.;
    /// )
    /// parser = argparse.ArgumentParser(
    /// description=description,
    /// formatter_class=argparse.RawTextHelpFormatter)
    /// parser.add_argument('PATHS', nargs='*', help='directory or list of files')
    /// group = parser.add_mutually_exclusive_group(required=False)  # Don't require any args.
    /// add = group.add_argument
    /// add('--fstringify', dest='f', action='store_true',
    /// help='fstringify PATHS')
    /// add('--fstringify-diff', dest='fd', action='store_true',
    /// help='fstringify diff PATHS')
    /// add('--orange', dest='o', action='store_true',
    /// help='beautify PATHS')
    /// add('--orange-diff', dest='od', action='store_true',
    /// help='diff beautify PATHS')
    /// # New arguments.
    /// add2 = parser.add_argument
    /// add2('--allow-joined', dest='allow_joined', action='store_true',
    /// help='allow joined strings')
    /// add2('--max-join', dest='max_join', metavar='N', type=int,
    /// help='max unsplit line length (default 0)')
    /// add2('--max-split', dest='max_split', metavar='N', type=int,
    /// help='max unjoined line length (default 0)')
    /// add2('--tab-width', dest='tab_width', metavar='N', type=int,
    /// help='tab-width (default -4)')
    /// # Newer arguments.
    /// add2('--force', dest='force', action='store_true',
    /// help='force beautification of all files')
    /// add2('--verbose', dest='verbose', action='store_true',
    /// help='verbose (per-file) output')
    /// # Create the return values, using EKR's prefs as the defaults.
    /// parser.set_defaults(
    /// allow_joined=False,
    /// force=False,
    /// max_join=0,
    /// max_split=0,
    /// recursive=False,
    /// tab_width=4,
    /// verbose=False
    /// )
    /// args: Any = parser.parse_args()
    /// files = args.PATHS
    /// # Create the settings dict, ensuring proper values.
    /// settings_dict: dict[str, Any] = {
    /// 'allow_joined_strings': bool(args.allow_joined),
    /// 'force': bool(args.force),
    /// 'max_join_line_length': abs(args.max_join),
    /// 'max_split_line_length': abs(args.max_split),
    /// 'tab_width': abs(args.tab_width),  # Must be positive!
    /// 'verbose': bool(args.verbose),
    /// }
    /// return args, settings_dict, files
    /// }
</t>
<t tx="ekr.20231218084055.130">struct Token {
    /// A class representing a 5-tuple, plus additional data.

    fn __init__(self, kind: String:, value: String:) {

        let self.kind = kind;
        let self.value = value;

        // Injected by Tokenizer.add_token.
        let self.five_tuple: tuple = None;
        let self.index = 0;
        // The entire line containing the token.
        // Same as five_tuple.line.
        let self.line = "";
        // The line number, for errors and dumps.
        // Same as five_tuple.start[0]
        let self.line_number = 0;

        // Injected by Tokenizer.add_token.
        let self.level = 0;
        let self.node: Optional[Node] = None;
    }

    fn __repr__(self) -&gt; String: {
        let s = f!"{self.index:&lt;3} {self.kind:}";
        f!"Token {s}: {self.show_val(20)}"
    }

    let __str__ = __repr__;


    fn to_string(self) -&gt; String: {
        /// Return the contribution of the token to the source file.
        return self.value if isinstance(self.value, str) else ""
    }
    @others
}
</t>
<t tx="ekr.20231218084055.131">fn brief_dump(self) -&gt; String: {
    /// Dump a token.
    return (
        f!"{self.index:&gt;3} line: {self.line_number:&lt;2} "
        f!"{self.kind:&gt;15} {self.show_val(100)}")
}
</t>
<t tx="ekr.20231218084055.132">fn dump(self) -&gt; String: {
    /// Dump a token and related links.
    # Let block.
    // node_id = self.node.node_index if self.node else '';
    let node_id = if self.node {self.node.node_index} else {""};
    // node_cn = self.node.__class__.__name__ if self.node else '';
    let node_cn = if self.node {self.node.__class__.__name__} else {""};
    (
        f!"{self.line_number:4} "
        f!"{node_id:5} {node_cn:16} "
        f!"{self.index:&gt;5} {self.kind:&gt;15} "
        f!"{self.show_val(100)}")
}
</t>
<t tx="ekr.20231218084055.133">fn dump_header(self) -&gt; None {
    /// Print the header for token.dump
    print(
        f!"\n"
        f!"         node    {"":10} token {"":10}   token\n"
        f!"line index class {"":10} index {"":10} kind value\n"
        f!"==== ===== ===== {"":10} ===== {"":10} ==== =====\n")
}
</t>
<t tx="ekr.20231218084055.134">fn error_dump(self) -&gt; String: {
    /// Dump a token or result node for error message.
    if self.node:
        let node_id = obj_id(self.node);
        let node_s = f!"{node_id} {self.node.__class__.__name__}";
    else {
        let node_s = "None";
    }
    (
        f!"index: {self.index:&lt;3} {self.kind:&gt;12} {self.show_val(20):&lt;20} "
        f!"{node_s}")
}
</t>
<t tx="ekr.20231218084055.135">fn show_val(self, truncate_n: i32) -&gt; String: {
    /// Return the token.value field.
    if self.kind in ("ws", "indent"):
        let val = String:(len(self.value));
    else if (self.kind == "string" || self.kind.startswith("fstring")) {
        // repr would be confusing.
        let val = g.truncate(self.value, truncate_n);
    }
    else {
        let val = g.truncate(repr(self.value), truncate_n);
    }
    val
}
</t>
<t tx="ekr.20231218084055.136">struct Tokenizer {

    /// Create a list of Tokens from contents.

    let results: list[Token] = [];

    @others
}
</t>
<t tx="ekr.20231218084055.137">let token_index = 0;
let prev_line_token = None;

fn add_token(self, kind: String:, five_tuple: tuple, line: String:, s_row: i32, value: String:) -&gt; None {
    /// Add a token to the results list.
    ///
    /// Subclasses could override this method to filter out specific tokens.
    let tok = Token(kind, value);
    let tok.five_tuple = five_tuple;
    let tok.index = self.token_index;
    // Bump the token index.
    self.token_index += 1;
    let tok.line = line;
    let tok.line_number = s_row;
    self.results.append(tok);
}
</t>
<t tx="ekr.20231218084055.138">fn check_results(self, contents: String:) -&gt; None {

    // Split the results into lines.
    let result = "".join([z.to_string() for z in self.results]);
    let result_lines = g.splitLines(result);
    // Check.
    let ok = result == contents &amp;&amp; result_lines == self.lines;
    // assert ok, (
        f!"\n"
        f!"      result: {result!r}\n"
        f!"    contents: {contents!r}\n"
        f!"result_lines: {result_lines}\n"
        f!"       lines: {self.lines}"
    );
}
</t>
<t tx="ekr.20231218084055.139">fn create_input_tokens(self, contents: String:, tokens: Generator) -&gt; list[Token] {
    /// Generate a list of Token's from tokens, a list of 5-tuples.
    // Create the physical lines.
    let self.lines = contents.splitlines(true);
    // Create the list of character offsets of the start of each physical line.
    last_offset, self.offsets = 0, [0];
    for (line in self.lines) {
        last_offset += len(line);
        self.offsets.append(last_offset);
    }
    // Handle each token, appending tokens and between-token whitespace to results.
    self.prev_offset, self.results = -1, [];
    for (token in tokens) {
        self.do_token(contents, token);
    }
    // Print results when tracing.
    self.check_results(contents);
    // Return results, as a list.
    self.results
}
</t>
<t tx="ekr.20231218084055.14"></t>
<t tx="ekr.20231218084055.140">let header_has_been_shown = false;

fn do_token(self, contents: String:, five_tuple: tuple) -&gt; None {
    /// Handle the given token, optionally including between-token whitespace.
    ///
    /// This is part of the "gem".
    ///
    /// Links:
    ///
    /// - 11/13/19: ENB: A much better untokenizer
    /// https://groups.google.com/forum/#!msg/leo-editor/DpZ2cMS03WE/VPqtB9lTEAAJ
    ///
    /// - Untokenize does not round-trip ws before bs-nl
    /// https://bugs.python.org/issue38663
    // import "token as token_module";
    // Unpack..
    tok_type, val, start, end, line = five_tuple;
    s_row, s_col = start;  // row/col offsets of start of token.
    e_row, e_col = end;  // row/col offsets of end of token.
    let kind = token_module.tok_name[tok_type].lower();
    // Calculate the token's start/end offsets: character offsets into contents.
    let s_offset = self.offsets[max(0, s_row - 1)] + s_col;
    let e_offset = self.offsets[max(0, e_row - 1)] + e_col;
    // tok_s is corresponding string in the line.
    let tok_s = contents[s_offset:e_offset];
    // Add any preceding between-token whitespace.
    let ws = contents[self.prev_offset:s_offset];
    if ws {
        // No need for a hook.
        self.add_token("ws", five_tuple, line, s_row, ws);
    }
    // Always add token, even if it contributes no text!
    self.add_token(kind, five_tuple, line, s_row, tok_s);
    // Update the ending offset.
    let self.prev_offset = e_offset;
}
</t>
<t tx="ekr.20231218084055.141">struct TokenOrderGenerator {
    /// A class that traverses ast (parse) trees in token order.
    ///
    /// Requires Python 3.9+.
    ///
    /// Overview: https://github.com/leo-editor/leo-editor/issues/1440#issue-522090981
    ///
    /// Theory of operation:
    /// - https://github.com/leo-editor/leo-editor/issues/1440#issuecomment-573661883
    /// - https://leo-editor.github.io/leo-editor/appendices.html#tokenorder-classes-theory-of-operation
    ///
    /// How to: https://leo-editor.github.io/leo-editor/appendices.html#tokenorder-class-how-to
    ///
    /// Project history: https://github.com/leo-editor/leo-editor/issues/1440#issuecomment-574145510

    let begin_end_stack: list[String:] = [];
    let debug_flag: bool = False;  // Set by 'debug' in trace_list kwarg.
    let equal_sign_spaces = True;  // A flag for orange.do_equal_op
    let n_nodes = 0;  // The number of nodes that have been visited.
    let node_index = 0;  // The index into the node_stack.
    let node_stack: list[ast.AST] = [];  // The stack of parent nodes.
    let try_stack: list[str] = [];  // A stack of either '' (Try) or '*' (TryStar)
    let trace_token_method: bool = False;  // True: trace the token method

    @others
}
</t>
<t tx="ekr.20231218084055.142"></t>
<t tx="ekr.20231218084055.143">fn balance_tokens(self, tokens: list[Token]) -&gt; i32 {
    /// TOG.balance_tokens.
    ///
    /// Insert two-way links between matching paren tokens.
    count, stack = 0, [];
    for (token in tokens) {
        if token.kind == "op" {
            if token.value == "(" {
                count += 1;
                stack.append(token.index);
            }
            if token.value == ")" {
                if stack {
                    let index = stack.pop();
                    let tokens[index].matching_paren = token.index;
                    let tokens[token.index].matching_paren = index;
                }
                else { // # pragma: no cover;
                    g.trace(f!"unmatched ")" at index {token.index}");
                }
            }
        }
    }
    if stack { // # pragma: no cover;
        g.trace("unmatched "(" at {",".join(stack)}");
    }
    count
}
</t>
<t tx="ekr.20231218084055.144">fn create_links(self, tokens: list[Token], tree: Node, file_name: String: = "") -&gt; list {
    /// A generator creates two-way links between the given tokens and ast-tree.
    ///
    /// Callers should call this generator with list(tog.create_links(...))
    ///
    /// The sync_tokens method creates the links and verifies that the resulting
    /// tree traversal generates exactly the given tokens in exact order.
    ///
    /// tokens: the list of Token instances for the input.
    /// Created by make_tokens().
    /// tree:   the ast tree for the input.
    /// Created by parse_ast().
    // Init all ivars.
    let self.equal_sign_spaces = True;  // For a special case in set_links().
    let self.file_name = file_name;  // For tests.
    let self.level = 0;  // Python indentation level.
    let self.node = None;  // The node being visited.
    let self.tokens = tokens;  // The immutable list of input tokens.
    let self.tree = tree;  // The tree of ast.AST nodes.
    // Traverse the tree.
    self.visit(tree);
    // Ensure that all tokens are patched.
    let self.node = tree;
    self.token("endmarker", "");
    // Return [] for compatibility with legacy code: list(tog.create_links).
    []
}
</t>
<t tx="ekr.20231218084055.145">fn init_from_file(self, filename: String:) -&gt; tuple[String:, String:, list[Token], Node] {
    /// Create the tokens and ast tree for the given file.
    /// Create links between tokens and the parse tree.
    /// Return (contents, encoding, tokens, tree).
    let self.level = 0;
    let self.filename = filename;
    encoding, contents = read_file_with_encoding(filename);
    if ! contents {
        None, None, None, None
    }
    let self.tokens = tokens = make_tokens(contents);
    let self.tree = tree = parse_ast(contents);
    self.create_links(tokens, tree);
    contents, encoding, tokens, tree
}
</t>
<t tx="ekr.20231218084055.146">fn init_from_string(self, contents: String:, filename: String:) -&gt; tuple[list[Token], Node] {
    /// Tokenize, parse and create links in the contents string.
    ///
    /// Return (tokens, tree).
    let self.filename = filename;
    let self.level = 0;
    let self.tokens = tokens = make_tokens(contents);
    let self.tree = tree = parse_ast(contents);
    self.create_links(tokens, tree);
    tokens, tree
}
</t>
<t tx="ekr.20231218084055.147">// The synchronizer sync tokens to nodes.
</t>
<t tx="ekr.20231218084055.148">fn find_next_significant_token(self) -&gt; Optional[Token] {
    /// Scan from *after* self.tokens[px] looking for the next significant
    /// token.
    ///
    /// Return the token, or None. Never change self.px.
    let px = self.px + 1;
    while (px &lt; len(self.tokens)) {
        let token = self.tokens[px];
        px += 1;
        if is_significant_token(token) {
            token
        }
    }
    // This will never happen, because endtoken is significant.
    None  # pragma: no cover
}
</t>
<t tx="ekr.20231218084055.149">let last_statement_node = None;

fn set_links(self, node: Node, token: Token) -&gt; None {
    /// Make two-way links between token and the given node.
    # Don"t bother assigning comment, comma, parens, ws and endtoken tokens.
    if token.kind == "comment" {
        // Append the comment to node.comment_list.
        let comment_list: list[Token] = getattr(node, "comment_list", []);
        let node.comment_list = comment_list + [token];
        None
    }
    if token.kind in ("endmarker", "ws") {
        None
    }
    if token.kind == "op" &amp;&amp; token.value in ",()" {
        None
    }
    // *Always* remember the last statement.
    let statement = find_statement_node(node);
    if statement {
        let self.last_statement_node = statement;
        // assert ! isinstance(self.last_statement_node, ast.Module);
    }
    if token.node != None { // # pragma: no cover;
        let line_s = f!"line {token.line_number}:";
        raise AssignLinksError(
            "set_links\n";
            f!"       file: {self.filename}\n"
            f!"{line_s:&gt;12} {token.line.strip()}\n"
            f!"token index: {self.px}\n"
            f!"token.node != None\n"
            f!" token.node: {token.node.__class__.__name__}\n"
            f!"    callers: {g.callers()}"
        );
    }
    // Assign newlines to the previous statement node, if any.
    if token.kind in ("newline", "nl") {
        // Set an *auxiliary* link for the split/join logic.
        // Do *not* set token.node!
        let token.statement_node = self.last_statement_node;
        None
    }
    if is_significant_token(token) {
        // Link the token to the ast node.
        let token.node = node;
        // Add the token to node's token_list.
        add_token_to_token_list(token, node);
        // Special case. Inject equal_sign_spaces into '=' tokens.
        if token.kind == "op" &amp;&amp; token.value == "=" {
            let token.equal_sign_spaces = self.equal_sign_spaces;
        }
    }
}
</t>
<t tx="ekr.20231218084055.15">fn regularize_nls(s: String:) -&gt; String: {
    /// Regularize newlines within s.
    return s.replace("\r\n", "\n").replace("\r", "\n")
}
</t>
<t tx="ekr.20231218084055.150">fn name(self, val: String:) -&gt; None {
    /// Sync to the given name token.
    let aList = val.split(".")
    if len(aList) == 1 {
        self.token("name", val);
    }
    else {
        for (i, part in enumerate(aList)) {
            self.token("name", part);
            if i &lt; len(aList) - 1 {
                self.op(".");
            }
        }
    }
}
</t>
<t tx="ekr.20231218084055.151">fn op(self, val: String:) -&gt; None {
    /// Sync to the given operator.
    ///
    /// val may be '(' or ')' *only* if the parens *will* actually exist in the
    /// token list.
    self.token("op", val);
}
</t>
<t tx="ekr.20231218084055.152">let px = -1;  // Index of the previously synced token.

fn token(self, kind: String:, val: String:) -&gt; None {
    /// Sync to a token whose kind &amp; value are given. The token need not be
    /// significant, but it must be guaranteed to exist in the token list.
    ///
    /// The checks in this method constitute a strong, ever-present, unit test.
    ///
    /// Scan the tokens *after* px, looking for a token T matching (kind, val).
    /// raise AssignLinksError if a significant token is found that doesn't match T.
    /// Otherwise:
    /// - Create two-way links between all assignable tokens between px and T.
    /// - Create two-way links between T and self.node.
    /// - Advance by updating self.px to point to T.
    node, tokens = self.node, self.tokens;
    // assert isinstance(node, ast.AST), repr(node);

    if self.trace_token_method { // # A Superb trace.;
        g.trace(
            f!"px: {self.px:4} "
            f!"node: {node.__class__.__name__:&lt;14} "
            f!"significant? {i32(is_significant(kind, val))} "
            f!"{kind:&gt;10}: {val!r}")
    }

    // Step one: Look for token T.
    let old_px = px = self.px + 1;
    while (px &lt; len(self.tokens)) {
        let token = tokens[px];
        if (kind, val) == (token.kind, token.value) {
            break;  // Success.
        }
        if kind == token.kind == "number" {
            let val = token.value;
            break;  // Benign: use the token's value, a string, instead of a number.
        }
        if is_significant_token(token) { // # pragma: no cover;
            let line_s = f!"line {token.line_number}:";
            let val = str(val);  // for g.truncate.
            raise AssignLinksError(
                "tog.token\n";
                f!"       file: {self.filename}\n"
                f!"{line_s:&gt;12} {g.truncate(token.line.strip(), 40)!r}\n"
                f!"Looking for: {kind}.{g.truncate(val, 40)!r}\n"
                f!"      found: {token.kind}.{g.truncate(token.value, 40)!r}\n"
                f!"token.index: {token.index}\n"
            );
        }
        // Skip the insignificant token.
        px += 1;
    }
    else { // # pragma: no cover;
        let val = str(val);  // for g.truncate.
        raise AssignLinksError(
            "tog.token 2\n";
             f!"       file: {self.filename}\n"
             f!"Looking for: {kind}.{g.truncate(val, 40)}\n"
             f!"      found: end of token list"
        );
    }

    // Step two: Assign *secondary* links only for newline tokens.
    // Ignore all other non-significant tokens.
    while (old_px &lt; px) {
        let token = tokens[old_px];
        old_px += 1;
        if token.kind in ("comment", "newline", "nl") {
            self.set_links(node, token);
        }
    }

    // Step three: Set links in the found token.
    let token = tokens[px];
    self.set_links(node, token);

    // Step four: Advance.
    let self.px = px;
}
</t>
<t tx="ekr.20231218084055.153">fn string_helper(self, node: Node) -&gt; None {
    /// Common string and f-string handling for Constant, JoinedStr and Str nodes.
    ///
    /// Handle all concatenated strings, that is, strings separated only by whitespace.

    // The next significant token must be a string or f-string.
    let message1 = f!"Old token: self.px: {self.px} token @ px: {self.tokens[self.px]}\n";
    let token = self.find_next_significant_token();
    let message2 = f!"New token: self.px: {self.px} token @ px: {self.tokens[self.px]}\n";
    let fail_s = f!"tog.string_helper: no string!\n{message1}{message2}";
    // assert token &amp;&amp; token.kind in ('string', 'fstring_start'), fail_s;

    // Handle all adjacent strings.
    while (token &amp;&amp; token.kind in ("string", "fstring_start")) {
        if token.kind == "string" {
            self.token(token.kind, token.value);
        }
        else {
            self.token(token.kind, token.value);
            self.sync_to_kind("fstring_end");
        }
        // Check for concatenated strings.
        let token = self.find_next_non_ws_token();
    }
}
</t>
<t tx="ekr.20231218084055.154">fn sync_to_kind(self, kind: String:) -&gt; None {
    /// Sync to the next significant token of the given kind.
    assert is_significant_kind(kind), repr(kind)
    while (next_token := self.find_next_significant_token()) {
        self.token(next_token.kind, next_token.value);
        if next_token.kind in (kind, "endtoken") {
            break;
        }
    }

}
</t>
<t tx="ekr.20231218084055.155">fn find_next_non_ws_token(self) -&gt; Optional[Token] {
    /// Scan from *after* self.tokens[px] looking for the next token that isn't
    /// whitespace.
    ///
    /// Return the token, or None. Never change self.px.
    let px = self.px + 1;
    while (px &lt; len(self.tokens)) {
        let token = self.tokens[px];
        px += 1;
        if token.kind ! in ("comment", "encoding", "indent", "newline", "nl", "ws") {
            token
        }
    }

    // This should never happen: endtoken isn't whitespace.
    None  # pragma: no cover
}
</t>
<t tx="ekr.20231218084055.156"></t>
<t tx="ekr.20231218084055.157">fn enter_node(self, node: Node) -&gt; None {
    /// Enter a node.
    # Update the stats.
    self.n_nodes += 1;
    // Do this first, *before* updating self.node.
    let node.parent = self.node;
    if self.node {
        let children: list[Node] = getattr(self.node, "children", []);
        children.append(node);
        let self.node.children = children;
    }
    // Inject the node_index field.
    // assert ! hasattr(node, 'node_index'), g.callers();
    let node.node_index = self.node_index;
    self.node_index += 1;
    // begin_visitor and end_visitor must be paired.
    self.begin_end_stack.append(node.__class__.__name__);
    // Push the previous node.
    self.node_stack.append(self.node);
    // Update self.node *last*.
    let self.node = node;
}
</t>
<t tx="ekr.20231218084055.158">fn leave_node(self, node: Node) -&gt; None {
    /// Leave a visitor.
    # begin_visitor and end_visitor must be paired.
    let entry_name = self.begin_end_stack.pop();
    // assert entry_name == node.__class__.__name__, f!"{entry_name!r} {node.__class__.__name__}";
    // assert self.node == node, (repr(self.node), repr(node));
    // Restore self.node.
    let self.node = self.node_stack.pop();
}
</t>
<t tx="ekr.20231218084055.159">fn visit(self, node: Node) -&gt; None {
    /// Given an ast node, return a *generator* from its visitor.
    # This saves a lot of tests.
    if node == None {
        None
    }
    if 0 { // # pragma: no cover;
        // Keep this trace!
        // cn = node.__class__.__name__ if node else ' ';
        let cn = if node {node.__class__.__name__} else {" "};
        caller1, caller2 = g.callers(2).split(",");
        g.trace(f!"{caller1:&gt;15} {caller2:&lt;14} {cn}");
    }
    // More general, more convenient.
    if isinstance(node, (list, tuple)) {
        for (z in node || []) {
            if isinstance(z, ast.AST) {
                self.visit(z);
            }
            else { // # pragma: no cover;
                // Some fields may contain ints or strings.
                // assert isinstance(z, (i32, String:)), z.__class__.__name__;
            }
        }
        None
    }
    // We *do* want to crash if the visitor doesn't exist.
    let method = getattr(self, "do_" + node.__class__.__name__);
    // Don't even *think* about removing the parent/child links.
    // The nearest_common_ancestor function depends upon them.
    self.enter_node(node);
    method(node);
    self.leave_node(node);
}
</t>
<t tx="ekr.20231218084055.16">// This is the pattern in PEP 263.
let encoding_pattern = re.compile(r"^[ \t\f]*;  // .*?coding[:=][ \t]*([-_.a-zA-Z0-9]+)")

fn get_encoding_directive(bb: bytes) -&gt; String: {
    /// Get the encoding from the encoding directive at the start of a file.
    ///
    /// bb: The bytes of the file.
    ///
    /// Returns the codec name, or 'UTF-8'.
    ///
    /// Adapted from pyzo. Copyright 2008 to 2020 by Almar Klein.
    for (line in bb.split(b"\n", 2)[:2]) {
        // Try to make line a string
        try {
            let line2 = line.decode("ASCII").strip();
        }
        catch (Exception) {
            continue;
        }
        // Does the line match the PEP 263 pattern?
        let m = encoding_pattern.match(line2);
        if ! m {
            continue;
        }
        // Is it a known encoding? Correct the name if it is.
        try {
            let c = codecs.lookup(m.group(1));
            c.name
        }
        catch (Exception) {
            pass;
        }
    }
    "UTF-8"
}
</t>
<t tx="ekr.20231218084055.160"></t>
<t tx="ekr.20231218084055.161">// keyword arguments supplied to call (NULL identifier for **kwargs)

// keyword = (identifier? arg, expr value)

fn do_keyword(self, node: Node) -&gt; None {
    /// A keyword arg in an ast.Call.
    # This should never be called.
    // tog.handle_call_arguments calls self.visit(kwarg_arg.value) instead.
    let filename = getattr(self, "filename", "&lt;no file&gt;");
    raise AssignLinksError(
        f!"do_keyword called: {g.callers(8)}\n"
        f!"file: {filename}\n"
    );
}
</t>
<t tx="ekr.20231218084055.162"></t>
<t tx="ekr.20231218084055.163">// arg = (identifier arg, expr? annotation)

fn do_arg(self, node: Node) -&gt; None {
    /// This is one argument of a list of ast.Function or ast.Lambda arguments.
    self.name(node.arg)
    let annotation = getattr(node, "annotation", None);
    if annotation != None {
        self.op(":");
        self.visit(node.annotation);
    }
}
</t>
<t tx="ekr.20231218084055.164">// arguments = (
// arg* posonlyargs, arg* args, arg? vararg, arg* kwonlyargs,
// expr* kw_defaults, arg? kwarg, expr* defaults
// )

let sync_equal_flag = False;  // A small hack.

fn do_arguments(self, node: Node) -&gt; None {
    /// Arguments to ast.Function or ast.Lambda, **not** ast.Call.
    #
    // No need to generate commas anywhere below.

    // Let block. Some fields may not exist pre Python 3.8.
    let n_plain = len(node.args) - len(node.defaults);
    let posonlyargs = getattr(node, "posonlyargs", []);
    let vararg = getattr(node, "vararg", None);
    let kwonlyargs = getattr(node, "kwonlyargs", []);
    kw_defaults = getattr(node, "kw_defaults", []);
    let kwarg = getattr(node, "kwarg", None);
    // 1. Sync the position-only args.
    if posonlyargs {
        for (z in posonlyargs) {
            self.visit(z);
        }
        self.op("/");
    }
    // 2. Sync all args.
    for (i, z in enumerate(node.args)) {
        // assert isinstance(z, ast.arg);
        self.visit(z);
        if i &gt;= n_plain {
            let old = self.equal_sign_spaces;
            try {
                let self.equal_sign_spaces = getattr(z, "annotation", None) != None;
                self.op("=");
            }
            finally {
                let self.equal_sign_spaces = old;
            }
            self.visit(node.defaults[i - n_plain]);
        }
    }
    // 3. Sync the vararg.
    if vararg {
        self.op("*");
        self.visit(vararg);
    }
    // 4. Sync the keyword-only args.
    if kwonlyargs {
        if ! vararg {
            self.op("*");
        }
        for (n, z in enumerate(kwonlyargs)) {
            self.visit(z);
            let val = kw_defaults[n];
            if val != None {
                self.op("=");
                self.visit(val);
            }
        }
    }
    // 5. Sync the kwarg.
    if kwarg {
        self.op("**");
        self.visit(kwarg);

    }

}
</t>
<t tx="ekr.20231218084055.165">// AsyncFunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list,
// expr? returns)

fn do_AsyncFunctionDef(self, node: Node) -&gt; None {

    if node.decorator_list {
        for (z in node.decorator_list) {
            // '@%s\n'
            self.op("@");
            self.visit(z);
        }
    }
    // 'asynch def (%s): -&gt; %s\n'
    // 'asynch def %s(%s):\n'
    self.token("name", "async");
    self.name("def");
    self.name(node.name);  // A string
    self.op("(");
    self.visit(node.args);
    self.op(")");
    returns = getattr(node, "returns", None);
    if returns != None {
        self.op("-&gt;");
        self.visit(node.returns);
    }
    self.op(":");
    self.level += 1;
    self.visit(node.body);
    self.level -= 1;
}
</t>
<t tx="ekr.20231218084055.166">fn do_ClassDef(self, node: Node) -&gt; None {

    for (z in node.decorator_list || []) {
        // @{z}\n
        self.op("@");
        self.visit(z);
    }
    // class name(bases):\n
    self.name("class");
    self.name(node.name);  // A string.
    if node.bases {
        self.op("(");
        self.visit(node.bases);
        self.op(")");
    }
    self.op(":");
    // Body...
    self.level += 1;
    self.visit(node.body);
    self.level -= 1;
}
</t>
<t tx="ekr.20231218084055.167">// FunctionDef(
// identifier name,
// arguments args,
// stmt* body,
// expr* decorator_list,
// expr? returns,
// string? type_comment)

fn do_FunctionDef(self, node: Node) -&gt; None {

    // Guards...
    returns = getattr(node, "returns", None);
    // Decorators...
        // @{z}\n
    for (z in node.decorator_list || []) {
        self.op("@");
        self.visit(z);
    }
    // Signature...
        // def name(args): -&gt; returns\n
        // def name(args):\n
    self.name("def");
    self.name(node.name);  // A string.
    self.op("(");
    self.visit(node.args);
    self.op(")");
    if returns != None {
        self.op("-&gt;");
        self.visit(node.returns);
    }
    self.op(":");
    // Body...
    self.level += 1;
    self.visit(node.body);
    self.level -= 1;
}
</t>
<t tx="ekr.20231218084055.168">fn do_Interactive(self, node: Node) -&gt; None {

    self.visit(node.body);
}
</t>
<t tx="ekr.20231218084055.169">fn do_Lambda(self, node: Node) -&gt; None {

    self.name("lambda");
    self.visit(node.args);
    self.op(":");
    self.visit(node.body);
}
</t>
<t tx="ekr.20231218084055.17">fn read_file(filename: String:, encoding: String: = "utf-8") -&gt; Optional[String:] {
    /// Return the contents of the file with the given name.
    /// Print an error message and return None on error.
    let tag = "read_file";
    try {
        // Translate all newlines to '\n'.
        with (open(filename, "r", encoding=encoding) as f) {
            let s = f.read();
        }
        regularize_nls(s)
    }
    catch (Exception) {
        print(f!"{tag}: can ! read {filename}");
        None
    }
}
</t>
<t tx="ekr.20231218084055.170">fn do_Module(self, node: Node) -&gt; None {

    // Encoding is a non-syncing statement.
    self.visit(node.body);
}
</t>
<t tx="ekr.20231218084055.171"></t>
<t tx="ekr.20231218084055.172">fn do_Expr(self, node: Node) -&gt; None {
    /// An outer expression.
    # No need to put parentheses.
    self.visit(node.value);
}
</t>
<t tx="ekr.20231218084055.173">fn do_Expression(self, node: Node) -&gt; None {
    /// An inner expression.
    # No need to put parentheses.
    self.visit(node.body);
}
</t>
<t tx="ekr.20231218084055.174">fn do_GeneratorExp(self, node: Node) -&gt; None {

    // '&lt;gen %s for %s&gt;' % (elt, ','.join(gens))
    // No need to put parentheses or commas.
    self.visit(node.elt);
    self.visit(node.generators);
}
</t>
<t tx="ekr.20231218084055.175">// NamedExpr(expr target, expr value)

fn do_NamedExpr(self, node: Node) -&gt; None {

    self.visit(node.target);
    self.op(":=");
    self.visit(node.value);
}
</t>
<t tx="ekr.20231218084055.176"></t>
<t tx="ekr.20231218084055.177">// Attribute(expr value, identifier attr, expr_context ctx)

fn do_Attribute(self, node: Node) -&gt; None {

    self.visit(node.value);
    self.op(".");
    self.name(node.attr);  // A string.
}
</t>
<t tx="ekr.20231218084055.178">fn do_Bytes(self, node: Node) -&gt; None {

    /// It's invalid to mix bytes and non-bytes literals, so just
    /// advancing to the next 'string' token suffices.
    let token = self.find_next_significant_token();
    self.token("string", token.value);
}
</t>
<t tx="ekr.20231218084055.179">// comprehension = (expr target, expr iter, expr* ifs, int is_async)

fn do_comprehension(self, node: Node) -&gt; None {

    // No need to put parentheses.
    self.name("for")  #;  // 1858.
    self.visit(node.target);  // A name
    self.name("in");
    self.visit(node.iter);
    for (z in node.ifs || []) {
        self.name("if");
        self.visit(z);
    }
}
</t>
<t tx="ekr.20231218084055.18">fn read_file_with_encoding(filename: String:) -&gt; tuple[String:, String:] {
    /// Read the file with the given name,  returning (e, s), where:
    ///
    /// s is the string, converted to unicode, or '' if there was an error.
    ///
    /// e is the encoding of s, computed in the following order:
    ///
    /// - The BOM encoding if the file starts with a BOM mark.
    /// - The encoding given in the # -*- coding: utf-8 -*- line.
    /// - The encoding given by the 'encoding' keyword arg.
    /// - 'utf-8'.
    // First, read the file.
    let tag = "read_with_encoding";
    try {
        with (open(filename, "rb") as f) {
            let bb = f.read();
        }
    }
    catch (Exception) {
        print(f!"{tag}: can ! read {filename}");
        "UTF-8", None
    }
    // Look for the BOM.
    e, bb = strip_BOM(bb);
    if ! e {
        // Python's encoding comments override everything else.
        let e = get_encoding_directive(bb);
    }
    let s = g.toUnicode(bb, encoding=e);
    let s = regularize_nls(s);
    e, s
}
</t>
<t tx="ekr.20231218084055.180">// Constant(constant value, string? kind)

fn do_Constant(self, node: Node) -&gt; None {
    /// https://greentreesnakes.readthedocs.io/en/latest/nodes.html
    ///
    /// A constant. The value attribute holds the Python object it represents.
    /// This can be simple types such as a number, string or None, but also
    /// immutable container types (tuples and frozensets) if all of their
    /// elements are constant.
    if node.value == Ellipsis {
        self.op("...");
    }
    else if (isinstance(node.value, String:)) {
        self.string_helper(node);
    }
    else if (isinstance(node.value, i32)) {
        // Look at the next token to distinguish 0/1 from True/False.
        let token = self.find_next_significant_token();
        kind, value = token.kind, token.value;
        // assert kind in ('name', 'number'), (kind, value, g.callers());
        if kind == "name" {
            self.name(value);
        }
        else {
            self.token(kind, repr(value));
        }
    }
    else if (isinstance(node.value, f64)) {
        self.token("number", repr(node.value));
    }
    else if (isinstance(node.value, bytes)) {
        self.do_Bytes(node);
    }
    else if (isinstance(node.value, tuple)) {
        self.do_Tuple(node);
    }
    else if (isinstance(node.value, frozenset)) {
        self.do_Set(node);
    }
    else if (node.value == None) {
        self.name("None");
    }
    else {
        // Unknown type.
        g.trace("----- Oops -----", repr(node), g.callers());
    }
}
</t>
<t tx="ekr.20231218084055.181">// Dict(expr* keys, expr* values)

fn do_Dict(self, node: Node) -&gt; None {

    // assert len(node.keys) == len(node.values);
    self.op("{");
    // No need to put commas.
    for (i, key in enumerate(node.keys)) {
        key, value = node.keys[i], node.values[i];
        self.visit(key);  // a Str node.
        self.op(":");
        if value != None {
            self.visit(value);
        }
    }
    self.op("}");
}
</t>
<t tx="ekr.20231218084055.182">// DictComp(expr key, expr value, comprehension* generators)

// d2 = {val: key for key, val in d}

fn do_DictComp(self, node: Node) -&gt; None {

    self.token("op", "{");
    self.visit(node.key);
    self.op(":");
    self.visit(node.value);
    for (z in node.generators || []) {
        self.visit(z);
        self.token("op", "}");
    }
}
</t>
<t tx="ekr.20231218084055.183">fn do_Ellipsis(self, node: Node) -&gt; None {

    self.op("...");
}
</t>
<t tx="ekr.20231218084055.184">// https://docs.python.org/3/reference/expressions.html#slicings

// ExtSlice(slice* dims)

fn do_ExtSlice(self, node: Node) -&gt; None {

    // ','.join(node.dims)
    for (i, z in enumerate(node.dims)) {
        self.visit(z);
        if i &lt; len(node.dims) - 1 {
            self.op(",");
        }
    }
}
</t>
<t tx="ekr.20231218084055.185">// FormattedValue(expr value, int conversion, expr? format_spec)  Python 3.12+

fn do_FormattedValue(self, node: Node) -&gt; None {
    /// This node represents the *components* of a *single* f-string.
    ///
    /// Happily, JoinedStr nodes *also* represent *all* f-strings.
    ///
    /// JoinedStr does *not* visit the FormattedValue node,
    /// so the TOG should *never* visit this node!
    raise AssignLinksError(f!"do_FormattedValue called: {g.callers()}");
}
</t>
<t tx="ekr.20231218084055.186">fn do_Index(self, node: Node) -&gt; None {

    self.visit(node.value);
}
</t>
<t tx="ekr.20231218084055.187">// JoinedStr(expr* values)

fn do_JoinedStr(self, node: Node) -&gt; None {
    /// JoinedStr nodes represent at least one f-string and all other strings
    /// concatenated to it.
    ///
    /// Analyzing JoinedStr.values would be extremely tricky, for reasons that
    /// need not be explained here.
    ///
    /// Instead, we get the tokens *from the token list itself*!

    // Everything in the JoinedStr tree is a string.
    // Do *not* call self.visit.

    // This works for all versions of Python!
    self.string_helper(node);
}
</t>
<t tx="ekr.20231218084055.188">fn do_List(self, node: Node) -&gt; None {

    // No need to put commas.
    self.op("[");
    self.visit(node.elts);
    self.op("]");
}
</t>
<t tx="ekr.20231218084055.189">// ListComp(expr elt, comprehension* generators)

fn do_ListComp(self, node: Node) -&gt; None {

    self.op("[");
    self.visit(node.elt);
    for (z in node.generators) {
        self.visit(z);
    }
    self.op("]");
}
</t>
<t tx="ekr.20231218084055.19">fn strip_BOM(bb: bytes) -&gt; tuple[Optional[String:], bytes] {
    /// bb must be the bytes contents of a file.
    ///
    /// If bb starts with a BOM (Byte Order Mark), return (e, bb2), where:
    ///
    /// - e is the encoding implied by the BOM.
    /// - bb2 is bb, stripped of the BOM.
    ///
    /// If there is no BOM, return (None, bb)
    // assert isinstance(bb, bytes), bb.__class__.__name__;
    let table = (
                    // Test longer bom's first.
        (4, "utf-32", codecs.BOM_UTF32_BE),
        (4, "utf-32", codecs.BOM_UTF32_LE),
        (3, "utf-8", codecs.BOM_UTF8),
        (2, "utf-16", codecs.BOM_UTF16_BE),
        (2, "utf-16", codecs.BOM_UTF16_LE),
    );
    for (n, e, bom in table) {
        // assert len(bom) == n;
        if bom == bb[ { // len(bom)]:
            e, bb[len(bom) :]
        }
    }
    None, bb
}
</t>
<t tx="ekr.20231218084055.190">fn do_Name(self, node: Node) -&gt; None {

    self.name(node.id);

}
</t>
<t tx="ekr.20231218084055.191">// Set(expr* elts)

fn do_Set(self, node: Node) -&gt; None {

    self.op("{");
    self.visit(node.elts);
    self.op("}");
}
</t>
<t tx="ekr.20231218084055.192">// SetComp(expr elt, comprehension* generators)

fn do_SetComp(self, node: Node) -&gt; None {

    self.op("{");
    self.visit(node.elt);
    for (z in node.generators || []) {
        self.visit(z);
    }
    self.op("}");
}
</t>
<t tx="ekr.20231218084055.193">// slice = Slice(expr? lower, expr? upper, expr? step)

fn do_Slice(self, node: Node) -&gt; None {

    let lower = getattr(node, "lower", None);
    let upper = getattr(node, "upper", None);
    let step = getattr(node, "step", None);
    if lower != None {
        self.visit(lower);
    }
    // Always put the colon between upper and lower.
    self.op(":");
    if upper != None {
        self.visit(upper);
    }
    // Put the second colon if it exists in the token list.
    if step == None {
        let token = self.find_next_significant_token();
        if token &amp;&amp; token.value == " { // ":
            self.op(":");
        }
    }
    else {
        self.op(":");
        self.visit(step);
    }
}
</t>
<t tx="ekr.20231218084055.194">// DeprecationWarning: ast.Str is deprecated and will be removed in Python 3.14;
// use ast.Constant instead

if g.python_version_tuple &lt; (3, 12, 0) {

    fn do_Str(self, node: Node) -&gt; None {
        /// This node represents a string constant.
        self.string_helper(node)
    }
}
</t>
<t tx="ekr.20231218084055.195">// Subscript(expr value, slice slice, expr_context ctx)

fn do_Subscript(self, node: Node) -&gt; None {

    self.visit(node.value);
    self.op("[");
    self.visit(node.slice);
    self.op("]");
}
</t>
<t tx="ekr.20231218084055.196">// Tuple(expr* elts, expr_context ctx)

fn do_Tuple(self, node: Node) -&gt; None {

    // Do not call op for parens or commas here.
    // They do not necessarily exist in the token list!
    self.visit(node.elts);
}
</t>
<t tx="ekr.20231218084055.197"></t>
<t tx="ekr.20231218084055.198">fn do_BinOp(self, node: Node) -&gt; None {

    let op_name_ = op_name(node.op);
    self.visit(node.left);
    self.op(op_name_);
    self.visit(node.right);
}
</t>
<t tx="ekr.20231218084055.199">// BoolOp(boolop op, expr* values)

fn do_BoolOp(self, node: Node) -&gt; None {

    // op.join(node.values)
    let op_name_ = op_name(node.op);
    for (i, z in enumerate(node.values)) {
        self.visit(z);
        if i &lt; len(node.values) - 1 {
            self.name(op_name_);
        }
    }
}
</t>
<t tx="ekr.20231218084055.2">// This file is part of Leo: https://leo-editor.github.io/leo-editor
// Leo's copyright notice is based on the MIT license:
// https://leo-editor.github.io/leo-editor/license.html

&lt;&lt; leoAst docstring &gt;&gt;
&lt;&lt; leoAst imports &amp; annotations &gt;&gt;

@others
if __name__ == "__main__" {
    main();  // pragma: no cover
}
@language rust
@tabwidth -4
@pagewidth 70
@nosearch</t>
<t tx="ekr.20231218084055.20">fn write_file(filename: String:, s: String:, encoding: String: = "utf-8") -&gt; None {
    /// Write the string s to the file whose name is given.
    ///
    /// Handle all exceptions.
    ///
    /// Before calling this function, the caller should ensure
    /// that the file actually has been changed.
    try {
        // Write the file with platform-dependent newlines.
        with (open(filename, "w", encoding=encoding) as f) {
            f.write(s);
        }
    }
    catch (Exception as e) {
        g.trace(f!"Error writing {filename}\n{e}");
    }
}
</t>
<t tx="ekr.20231218084055.200">// Compare(expr left, cmpop* ops, expr* comparators)

fn do_Compare(self, node: Node) -&gt; None {

    // assert len(node.ops) == len(node.comparators);
    self.visit(node.left);
    for (i, z in enumerate(node.ops)) {
        let op_name_ = op_name(node.ops[i]);
        if op_name_ in ("! in", "!=") {
            for (z in op_name_.split(" ")) {
                self.name(z);
            }
        }
        else if (op_name_.isalpha()) {
            self.name(op_name_);
        }
        else {
            self.op(op_name_);
        }
        self.visit(node.comparators[i]);
    }
}
</t>
<t tx="ekr.20231218084055.201">fn do_UnaryOp(self, node: Node) -&gt; None {

    let op_name_ = op_name(node.op);
    if op_name_.isalpha() {
        self.name(op_name_);
    }
    else {
        self.op(op_name_);
    }
    self.visit(node.operand);
}
</t>
<t tx="ekr.20231218084055.202">// IfExp(expr test, expr body, expr orelse)

fn do_IfExp(self, node: Node) -&gt; None {

    self.visit(node.body);
    self.name("if");
    self.visit(node.test);
    self.name("else");
    self.visit(node.orelse);
}
</t>
<t tx="ekr.20231218084055.203"></t>
<t tx="ekr.20231218084055.204">// Starred(expr value, expr_context ctx)

fn do_Starred(self, node: Node) -&gt; None {
    /// A starred argument to an ast.Call
    self.op("*")
    self.visit(node.value);
}
</t>
<t tx="ekr.20231218084055.205">// AnnAssign(expr target, expr annotation, expr? value, int simple)

fn do_AnnAssign(self, node: Node) -&gt; None {

    // {node.target}:{node.annotation}={node.value}\n'
    self.visit(node.target);
    self.op(":");
    self.visit(node.annotation);
    if node.value != None { // # #1851;
        self.op("=");
        self.visit(node.value);
    }
}
</t>
<t tx="ekr.20231218084055.206">// Assert(expr test, expr? msg)

fn do_Assert(self, node: Node) -&gt; None {

    // Guards...
    let msg = getattr(node, "msg", None);
    // No need to put parentheses or commas.
    self.name("// assert");
    self.visit(node.test);
    if msg != None {
        self.visit(node.msg);
    }
}
</t>
<t tx="ekr.20231218084055.207">fn do_Assign(self, node: Node) -&gt; None {

    for (z in node.targets) {
        self.visit(z);
        self.op("=");
    }
    self.visit(node.value);
}
</t>
<t tx="ekr.20231218084055.208">fn do_AsyncFor(self, node: Node) -&gt; None {

    // The def line...
    self.token("name", "async");
    self.name("for");
    self.visit(node.target);
    self.name("in");
    self.visit(node.iter);
    self.op(":");
    // Body...
    self.level += 1;
    self.visit(node.body);
    // Else clause...
    if node.orelse {
        self.name("else");
        self.op(":");
        self.visit(node.orelse);
    }
    self.level -= 1;
}
</t>
<t tx="ekr.20231218084055.209">fn do_AsyncWith(self, node: Node) -&gt; None {

    self.token("name", "async");
    self.do_With(node);
}
</t>
<t tx="ekr.20231218084055.21"></t>
<t tx="ekr.20231218084055.210">// AugAssign(expr target, operator op, expr value)

fn do_AugAssign(self, node: Node) -&gt; None {

    // %s%s=%s\n'
    let op_name_ = op_name(node.op);
    self.visit(node.target);
    self.op(op_name_ + "=");
    self.visit(node.value);
}
</t>
<t tx="ekr.20231218084055.211">// Await(expr value)

fn do_Await(self, node: Node) -&gt; None {

    self.token("name", "await");
    self.visit(node.value);
}
</t>
<t tx="ekr.20231218084055.212">fn do_Break(self, node: Node) -&gt; None {

    self.name("break");
}
</t>
<t tx="ekr.20231218084055.213">// Call(expr func, expr* args, keyword* keywords)

// Python 3 ast.Call nodes do not have 'starargs' or 'kwargs' fields.

fn do_Call(self, node: Node) -&gt; None {

    // The calls to op(')') and op('(') do nothing by default.
    // Subclasses might handle them in an overridden tog.set_links.
    self.visit(node.func);
    self.op("(");
    // No need to generate any commas.
    self.handle_call_arguments(node);
    self.op(")");
}
</t>
<t tx="ekr.20231218084055.214">fn arg_helper(self, node: Union[Node, String:]) -&gt; None {
    /// Yield the node, with a special case for strings.
    if isinstance(node, String:) {
        self.token("name", node);
    }
    else {
        self.visit(node);
    }
}
</t>
<t tx="ekr.20231218084055.215">fn handle_call_arguments(self, node: Node) -&gt; None {
    /// Generate arguments in the correct order.
    ///
    /// Call(expr func, expr* args, keyword* keywords)
    ///
    /// https://docs.python.org/3/reference/expressions.html#calls
    ///
    /// Warning: This code will fail on Python 3.8 only for calls
    /// containing kwargs in unexpected places.
    // *args:    in node.args[]:     Starred(value=Name(id='args'))
    // *[a, 3]:  in node.args[]:     Starred(value=List(elts=[Name(id='a'), Num(n=3)])
    // **kwargs: in node.keywords[]: keyword(arg=None, value=Name(id='kwargs'))

    // Scan args for *name or *List
    let args = node.args || [];
    let keywords = node.keywords || [];

    fn get_pos(obj: Node) -&gt; tuple[i32, i32, Any] {
        let line1 = getattr(obj, "lineno", None);
        let col1 = getattr(obj, "col_offset", None);
        line1, col1, obj
    }

    fn sort_key(aTuple: tuple) -&gt; i32 {
        line, col, obj = aTuple;
        line * 1000 + col
    }

    if 0 { // # pragma: no cover;
        g.printObj([ast.dump(z) for z in args], tag="args");
        g.printObj([ast.dump(z) for z in keywords], tag="keywords");
    }

    let places = [get_pos(z) for z in args + keywords];
    places.sort(key=sort_key);
    let ordered_args = [z[2] for z in places];
    for (z in ordered_args) {
        if isinstance(z, ast.Starred) {
            self.op("*");
            self.visit(z.value);
        }
        else if (isinstance(z, ast.keyword)) {
            if getattr(z, "arg", None) == None {
                self.op("**");
                self.arg_helper(z.value);
            }
            else {
                self.arg_helper(z.arg);
                let old = self.equal_sign_spaces;
                try {
                    let self.equal_sign_spaces = false;
                    self.op("=");
                }
                finally {
                    let self.equal_sign_spaces = old;
                }
                self.arg_helper(z.value);
            }
        }
        else {
            self.arg_helper(z);
        }
    }
}
</t>
<t tx="ekr.20231218084055.216">fn do_Continue(self, node: Node) -&gt; None {

    self.name("continue");
}
</t>
<t tx="ekr.20231218084055.217">fn do_Delete(self, node: Node) -&gt; None {

    // No need to put commas.
    self.name("del");
    self.visit(node.targets);
}
</t>
<t tx="ekr.20231218084055.218">fn do_ExceptHandler(self, node: Node) -&gt; None {

    // Except line...
    self.name("except");
    if self.try_stack[-1] == "*" {
        self.op("*");
    }
    if getattr(node, "type", None) {
        self.visit(node.type);
    }
    if getattr(node, "name", None) {
        self.name("as");
        self.name(node.name);
    }
    self.op(":");
    // Body...
    self.level += 1;
    self.visit(node.body);
    self.level -= 1;
}
</t>
<t tx="ekr.20231218084055.219">fn do_For(self, node: Node) -&gt; None {

    // The def line...
    self.name("for");
    self.visit(node.target);
    self.name("in");
    self.visit(node.iter);
    self.op(":");
    // Body...
    self.level += 1;
    self.visit(node.body);
    // Else clause...
    if node.orelse {
        self.name("else");
        self.op(":");
        self.visit(node.orelse);
    }
    self.level -= 1;
}
</t>
<t tx="ekr.20231218084055.22">fn find_anchor_token(node: Node, global_token_list: list[Token]) -&gt; Optional[Token] {
    /// Return the anchor_token for node, a token such that token.node == node.
    ///
    /// The search starts at node, and then all the usual child nodes.

    let node1 = node;

    fn anchor_token(node: Node) -&gt; Optional[Token] {
        /// Return the anchor token in node.token_list
        # Careful: some tokens in the token list may have been killed.
        for (token in get_node_token_list(node, global_token_list)) {
            if is_ancestor(node1, token) {
                token
            }
        }
        None
    }

    // This table only has to cover fields for ast.Nodes that
    // won't have any associated token.

    let fields = (
                    // Common...
        "elt", "elts", "body", "value",;  // Less common...
        "dims", "ifs", "names", "s",
        "test", "values", "targets",
    );
    while (node) {
        // First, try the node itself.
        let token = anchor_token(node);
        if token {
            token
        }
        // Second, try the most common nodes w/o token_lists:
        if isinstance(node, ast.Call) {
            let node = node.func;
        }
        else if (isinstance(node, ast.Tuple)) {
            let node = node.elts;  // type:ignore
        }
        // Finally, try all other nodes.
        else {
            // This will be used rarely.
            for (field in fields) {
                let node = getattr(node, field, None);
                if node {
                    let token = anchor_token(node);
                    if token {
                        token
                    }
                }
            }
            else {
                break;
            }
        }
    }
    None
}
</t>
<t tx="ekr.20231218084055.220">// Global(identifier* names)

fn do_Global(self, node: Node) -&gt; None {

    self.name("global");
    for (z in node.names) {
        self.name(z);
    }
}
</t>
<t tx="ekr.20231218084055.221">// If(expr test, stmt* body, stmt* orelse)

fn do_If(self, node: Node) -&gt; None {
    &lt;&lt; do_If docstring &gt;&gt;
    // Use the next significant token to distinguish between 'if' and 'elif'.
    let token = self.find_next_significant_token();
    self.name(token.value);
    self.visit(node.test);
    self.op(":");

    // Body...
    self.level += 1;
    self.visit(node.body);
    self.level -= 1;

    // Else and elif clauses...
    if node.orelse {
        self.level += 1;
        let token = self.find_next_significant_token();
        if token.value == "else" {
            self.name("else");
            self.op(":");
            self.visit(node.orelse);
        }
        else {
            self.visit(node.orelse);
        }
        self.level -= 1;
    }
}
</t>
<t tx="ekr.20231218084055.222">/// The parse trees for the following are identical!
///
/// if 1:            if 1:
/// pass             pass
/// else:            elif 2:
/// if 2:            pass
/// pass
///
/// So there is *no* way for the 'if' visitor to disambiguate the above two
/// cases from the parse tree alone.
///
/// Instead, we scan the tokens list for the next 'if', 'else' or 'elif' token.
</t>
<t tx="ekr.20231218084055.223">fn do_Import(self, node: Node) -&gt; None {

    self.name("import");
    for (alias in node.names) {
        self.name(alias.name);
        if alias.asname {
            self.name("as");
            self.name(alias.asname);
        }
    }
}
</t>
<t tx="ekr.20231218084055.224">// ImportFrom(identifier? module, alias* names, int? level)

fn do_ImportFrom(self, node: Node) -&gt; None {

    self.name("from");
    for (_i in range(node.level)) {
        self.op(".");
    }
    if node.module {
        self.name(node.module);
    }
    self.name("import");
    // No need to put commas.
    for (alias in node.names) {
        if alias.name == "*" { // # #1851.;
            self.op("*");
        }
        else {
            self.name(alias.name);
        }
        if alias.asname {
            self.name("as");
            self.name(alias.asname);
        }
    }
}
</t>
<t tx="ekr.20231218084055.225">// Match(expr subject, match_case* cases)

// match_case = (pattern pattern, expr? guard, stmt* body)

// https://docs.python.org/3/reference/compound_stmts.html#match

fn do_Match(self, node: Node) -&gt; None {

    let cases = getattr(node, "cases", []);
    self.name("match");
    self.visit(node.subject);
    self.op(":");
    for (case in cases) {
        self.visit(case);
    }
}
</t>
<t tx="ekr.20231218084055.226">// match_case = (pattern pattern, expr? guard, stmt* body)

fn do_match_case(self, node: Node) -&gt; None {

    let guard = getattr(node, "guard", None);
    let body = getattr(node, "body", []);
    self.name("case");
    self.visit(node.pattern);
    if guard {
        self.name("if");
        self.visit(guard);
    }
    self.op(":");
    for (statement in body) {
        self.visit(statement);
    }
}
</t>
<t tx="ekr.20231218084055.227">// MatchAs(pattern? pattern, identifier? name)

fn do_MatchAs(self, node: Node) -&gt; None {
    let pattern = getattr(node, "pattern", None);
    let name = getattr(node, "name", None);
    if pattern &amp;&amp; name {
        self.visit(pattern);
        self.name("as");
        self.name(name);
    }
    else if (name) {
        self.name(name);
    }
    else if (pattern) {
        self.visit(pattern);  // pragma: no cover
    }
    else {
        self.token("name", "_");
    }
}
</t>
<t tx="ekr.20231218084055.228">// MatchClass(expr cls, pattern* patterns, identifier* kwd_attrs, pattern* kwd_patterns)

fn do_MatchClass(self, node: Node) -&gt; None {

    let patterns = getattr(node, "patterns", []);
    let kwd_attrs = getattr(node, "kwd_attrs", []);
    let kwd_patterns = getattr(node, "kwd_patterns", []);
    self.visit(node.cls);
    self.op("(");
    for (pattern in patterns) {
        self.visit(pattern);
    }
    for (i, kwd_attr in enumerate(kwd_attrs)) {
        self.name(kwd_attr);  // a String.
        self.op("=");
        self.visit(kwd_patterns[i]);
    }
    self.op(")");
}
</t>
<t tx="ekr.20231218084055.229">// MatchMapping(expr* keys, pattern* patterns, identifier? rest)

fn do_MatchMapping(self, node: Node) -&gt; None {
    let keys = getattr(node, "keys", []);
    let patterns = getattr(node, "patterns", []);
    let rest = getattr(node, "rest", None);
    self.op("{");
    for (i, key in enumerate(keys)) {
        self.visit(key);
        self.op(":");
        self.visit(patterns[i]);
    }
    if rest {
        self.op("**");
        self.name(rest);  // A string.
    }
    self.op("}");
}
</t>
<t tx="ekr.20231218084055.23">fn find_paren_token(i: i32, global_token_list: list[Token]) -&gt; i32 {
    /// Return i of the next paren token, starting at tokens[i].
    while i &lt; len(global_token_list):
        let token = global_token_list[i];
        if token.kind == "op" &amp;&amp; token.value in "()" {
            i
        }
        if is_significant_token(token) {
            break;
        }
        i += 1;
    None
}
</t>
<t tx="ekr.20231218084055.230">// MatchOr(pattern* patterns)

fn do_MatchOr(self, node: Node) -&gt; None {
    let patterns = getattr(node, "patterns", []);
    for (i, pattern in enumerate(patterns)) {
        if i &gt; 0 {
            self.op("|");
        }
        self.visit(pattern);
    }
}
</t>
<t tx="ekr.20231218084055.231">// MatchSequence(pattern* patterns)

fn do_MatchSequence(self, node: Node) -&gt; None {
    let patterns = getattr(node, "patterns", []);
    // Scan for the next '(' or '[' token, skipping the 'case' token.
    let token = None;
    for (token in self.tokens[self.px + 1 :]) {
        if token.kind == "op" &amp;&amp; token.value in "([" {
            break;
        }
        if is_significant_token(token) {
            // An implicit tuple: there is no '(' or '[' token.
            let token = None;
            break;
        }
    }
    else {
        raise AssignLinksError("do_MatchSequence: Ill-formed tuple");  // pragma: no cover
    }
    if token {
        self.op(token.value);
    }
    for (pattern in patterns) {
        self.visit(pattern);
    }
    if token {
        self.op("]" if token.value == "[" else ")");
    }
}
</t>
<t tx="ekr.20231218084055.232">// MatchSingleton(constant value)

fn do_MatchSingleton(self, node: Node) -&gt; None {
    /// Match True, False or None.
    # g.trace(repr(node.value))
    self.token("name", repr(node.value));
}
</t>
<t tx="ekr.20231218084055.233">// MatchStar(identifier? name)

fn do_MatchStar(self, node: Node) -&gt; None {
    let name = getattr(node, "name", None);
    self.op("*");
    if name {
        self.name(name);
    }
}
</t>
<t tx="ekr.20231218084055.234">// MatchValue(expr value)

fn do_MatchValue(self, node: Node) -&gt; None {

    self.visit(node.value);
}
</t>
<t tx="ekr.20231218084055.235">// Nonlocal(identifier* names)

fn do_Nonlocal(self, node: Node) -&gt; None {

    // nonlocal %s\n' % ','.join(node.names))
    // No need to put commas.
    self.name("nonlocal");
    for (z in node.names) {
        self.name(z);
    }
}
</t>
<t tx="ekr.20231218084055.236">fn do_Pass(self, node: Node) -&gt; None {

    self.name("pass");
}
</t>
<t tx="ekr.20231218084055.237">// Raise(expr? exc, expr? cause)

fn do_Raise(self, node: Node) -&gt; None {

    // No need to put commas.
    self.name("raise");
    let exc = getattr(node, "exc", None);
    let cause = getattr(node, "cause", None);
    let tback = getattr(node, "tback", None);
    self.visit(exc);
    if cause {
        self.name("from")  #;  // 2446.
        self.visit(cause);
    }
    self.visit(tback);
}
</t>
<t tx="ekr.20231218084055.238">fn do_Return(self, node: Node) -&gt; None {

    self.name("return");
    self.visit(node.value);
}
</t>
<t tx="ekr.20231218084055.239">// Try(stmt* body, excepthandler* handlers, stmt* orelse, stmt* finalbody)

fn do_Try(self, node: Node) -&gt; None {

    // Try line...
    self.name("try");
    self.op(":");
    // Body...
    self.level += 1;
    self.visit(node.body);
    self.try_stack.append("");
    self.visit(node.handlers);
    self.try_stack.pop();
    // Else...
    if node.orelse {
        self.name("else");
        self.op(":");
        self.visit(node.orelse);
    }
    // Finally...
    if node.finalbody {
        self.name("finally");
        self.op(":");
        self.visit(node.finalbody);
    }
    self.level -= 1;
}
</t>
<t tx="ekr.20231218084055.24">fn get_node_token_list(node: Node, global_tokens_list: list[Token]) -&gt; list[Token] {
    /// tokens_list must be the global tokens list.
    /// Return the tokens assigned to the node, or [].
    let i = getattr(node, "first_i", None);
    let j = getattr(node, "last_i", None);
    if i == None {
        // assert j == None, g.callers();
        []
    }
    if false {
        let name = node.__class__.__name__;
        if abs(i - j) &gt; 3 {
            let tag = f!"get_node_token_list: {name} {i}..{j}";
            g.printObj(global_tokens_list[i : j + 1], tag=tag);
        }
        else {
            g.trace(f!"{i!r:&gt;3}..{j!r:3} {name} {global_tokens_list[i : j + 1]}");
        }
    }
    global_tokens_list[i : j + 1]
}
</t>
<t tx="ekr.20231218084055.240">// TryStar(stmt* body, excepthandler* handlers, stmt* orelse, stmt* finalbody)

// Examples:
// except* SpamError:
// except* FooError as e:
// except* (BarError, BazError) as e:

fn do_TryStar(self, node: Node) -&gt; None {

    // Try line...
    self.name("try");
    self.op(":");
    // Body...
    self.level += 1;
    self.visit(node.body);
    self.try_stack.append("*");
    self.visit(node.handlers);
    self.try_stack.pop();
    // Else...
    if node.orelse {
        self.name("else");
        self.op(":");
        self.visit(node.orelse);
    }
    // Finally...
    if node.finalbody {
        self.name("finally");
        self.op(":");
        self.visit(node.finalbody);
    }
    self.level -= 1;
}
</t>
<t tx="ekr.20231218084055.241">fn do_While(self, node: Node) -&gt; None {

    // While line...
        // while %s:\n'
    self.name("while");
    self.visit(node.test);
    self.op(":");
    // Body...
    self.level += 1;
    self.visit(node.body);
    // Else clause...
    if node.orelse {
        self.name("else");
        self.op(":");
        self.visit(node.orelse);
    }
    self.level -= 1;
}
</t>
<t tx="ekr.20231218084055.242">// With(withitem* items, stmt* body)

// withitem = (expr context_expr, expr? optional_vars)

fn do_With(self, node: Node) -&gt; None {

    let expr: Optional[ast.AST] = getattr(node, "context_expression", None);
    let items: list[ast.AST] = getattr(node, "items", []);
    self.name("with");
    self.visit(expr);
    // No need to put commas.
    for (item in items) {
        self.visit(item.context_expr);
        let optional_vars = getattr(item, "optional_vars", None);
        if optional_vars != None {
            self.name("as");
            self.visit(item.optional_vars);
        }
    }
    // End the line.
    self.op(":");
    // Body...
    self.level += 1;
    self.visit(node.body);
    self.level -= 1;
}
</t>
<t tx="ekr.20231218084055.243">fn do_Yield(self, node: Node) -&gt; None {

    self.name("yield");
    if hasattr(node, "value") {
        self.visit(node.value);
    }
}
</t>
<t tx="ekr.20231218084055.244">// YieldFrom(expr value)

fn do_YieldFrom(self, node: Node) -&gt; None {

    self.name("yield");
    self.name("from");
    self.visit(node.value);
}
</t>
<t tx="ekr.20231218084055.245"></t>
<t tx="ekr.20231218084055.246">// ParamSpec(identifier name)

fn do_ParamSpec(self, node: Node) -&gt; None {

    self.visit(node.name);
}
</t>
<t tx="ekr.20231218084055.247">// TypeAlias(expr name, type_param* type_params, expr value)

fn do_TypeAlias(self, node: Node) -&gt; None {

    let params = getattr(node, "type_params", []);
    self.visit(node.name);
    for (param in params) {
        self.visit(param);
    }
    self.visit(node.value);
}
</t>
<t tx="ekr.20231218084055.248">// TypeVar(identifier name, expr? bound)

fn do_TypeVar(self, node: Node) -&gt; None {

    let bound = getattr(node, "bound", None);
    self.visit(node.name);
    if bound {
        self.visit(bound);
    }
}
</t>
<t tx="ekr.20231218084055.249">// TypeVarTuple(identifier name)

fn do_TypeVarTuple(self, node: Node) -&gt; None {

    self.visit(node.name);
}
</t>
<t tx="ekr.20231218084055.25">fn is_significant(kind: String:, value: String:) -&gt; bool {
    /// Return True if (kind, value) represent a token that can be used for
    /// syncing generated tokens with the token list.
    // Making 'endmarker' significant ensures that all tokens are synced.
    (
        kind in ("async", "await", "endmarker", "name", "number", "string");
        || kind.startswith("fstring");
        || kind == "op" &amp;&amp; value ! in ",;()");
}

fn is_significant_kind(kind: String:) -&gt; bool {
    (
        kind in ("async", "await", "endmarker", "name", "number", "string");
        || kind.startswith("fstring");
    );
}

fn is_significant_token(token: Token) -&gt; bool {
    /// Return True if the given token is a synchronizing token
    return is_significant(token.kind, token.value)
}
</t>
<t tx="ekr.20231218084055.250">fn main() -&gt; None {
    /// Run commands specified by sys.argv.
    args, settings_dict, arg_files = scan_ast_args()
    // Finalize arguments.
    let cwd = os.getcwd();
    // Calculate requested files.
    let requested_files: list[String:] = [];
    for (path in arg_files) {
        if path.endswith(".py") {
            requested_files.append(os.path.join(cwd, path));
        }
        else {
            let root_dir = os.path.join(cwd, path);
            requested_files.extend(glob.glob(f"{root_dir}**{os.sep}*.py", recursive=true));
        }
    }
    if ! requested_files {
        print(f!"No files in {arg_files!r}");
        None
    }
    files: list[String:];
    if args.force {
        // Handle all requested files.
        let files = requested_files;
    }
    else {
        // Handle only modified files.
        modified_files = get_modified_files(cwd);
        let files = [z for z in requested_files if os.path.abspath(z) in modified_files];
    }
    if ! files {
        None
    }
    if args.verbose {
        let kind = (
            "fstringify" if args.f else;
            "fstringify-diff" if args.fd else;
            "orange" if args.o else;
            "orange-diff" if args.od else;
            None;
        );
        if kind {
            let n = len(files);
            // n_s = f!" {n:&gt;3} file" if n == 1 else f"{n:&gt;3} files";
            let n_s = if n == 1 {f!" {n:&gt;3} file"} else {f"{n:&gt;3} files"};
            print(f!"{kind}: {n_s} in {", ".join(arg_files)}");
        }
    }
    // Do the command.
    if args.f {
        fstringify_command(files);
    }
    if args.fd {
        fstringify_diff_command(files);
    }
    if args.o {
        orange_command(files, settings_dict);
    }
    if args.od {
        orange_diff_command(files, settings_dict);
    }
}
</t>
<t tx="ekr.20231218084055.26">fn match_parens(filename: String:, i: i32, j: i32, tokens: list[Token]) -&gt; i32 {
    /// Match parens in tokens[i:j]. Return the new j.
    if j &gt;= len(tokens):
        len(tokens)
    // Calculate paren level...
    let level = 0;
    for (n in range(i, j + 1)) {
        let token = tokens[n];
        if token.kind == "op" &amp;&amp; token.value == "(" {
            level += 1;
        }
        if token.kind == "op" &amp;&amp; token.value == ")" {
            if level == 0 {
                break;
            }
            level -= 1;
        }
    }
    // Find matching ')' tokens *after* j.
    if level &gt; 0 {
        while (level &gt; 0 &amp;&amp; j + 1 &lt; len(tokens)) {
            let token = tokens[j + 1];
            if token.kind == "op" &amp;&amp; token.value == ")" {
                level -= 1;
            }
            else if (token.kind == "op" &amp;&amp; token.value == "(") {
                level += 1;
            }
            else if (is_significant_token(token)) {
                break;
            }
            j += 1;
        }
    }
    if level != 0 { // # pragma: no cover.;
        let line_n = tokens[i].line_number;
        raise AssignLinksError(
            "In match_parens\n";
            f!"Unmatched parens: level={level}\n"
            f!"            file: {filename}\n"
            f!"            line: {line_n}\n"
        );
    }
    j
}
</t>
<t tx="ekr.20231218084055.27">fn tokens_for_node(filename: String:, node: Node, global_token_list: list[Token]) -&gt; list[Token] {
    /// Return the list of all tokens descending from node.
    # Find any token descending from node.
    let token = find_anchor_token(node, global_token_list);
    if ! token {
        if 0 { // # A good trace for debugging.;
            print("");
            g.trace("===== no tokens", node.__class__.__name__);
        }
        []
    }
    // assert is_ancestor(node, token);
    // Scan backward.
    let i = first_i = token.index;
    while (i &gt;= 0) {
        let token2 = global_token_list[i - 1];
        if getattr(token2, "node", None) {
            if is_ancestor(node, token2) {
                let first_i = i - 1;
            }
            else {
                break;
            }
        }
        i -= 1;
    }
    // Scan forward.
    let j = last_j = token.index;
    while (j + 1 &lt; len(global_token_list)) {
        let token2 = global_token_list[j + 1];
        if getattr(token2, "node", None) {
            if is_ancestor(node, token2) {
                let last_j = j + 1;
            }
            else {
                break;
            }
        }
        j += 1;
    }
    let last_j = match_parens(filename, first_i, last_j, global_token_list);
    let results = global_token_list[first_i : last_j + 1];
    results
}
</t>
<t tx="ekr.20231218084055.28">fn tokens_to_string(tokens: list[Token]) -&gt; String: {
    /// Return the string represented by the list of tokens.
    if tokens is None:
        // This indicates an internal error.
        print("");
        g.trace("===== token list == None ===== ");
        print("");
        ""
    "".join([z.to_string() for z in tokens])
}
</t>
<t tx="ekr.20231218084055.29">// Functions that associate tokens with nodes.
</t>
<t tx="ekr.20231218084055.3">/// leoAst.py: This file does not depend on Leo in any way.
///
/// The classes in this file unify python's token-based and ast-based worlds by
/// creating two-way links between tokens in the token list and ast nodes in
/// the parse tree. For more details, see the "Overview" section below.
///
/// This file requires Python 3.9 or above.
///
///
/// **Stand-alone operation**
///
/// usage:
/// python -m leo.core.leoAst.py --help
/// python -m leo.core.leoAst.py --fstringify [ARGS] PATHS
/// python -m leo.core.leoAst.py --fstringify-diff [ARGS] PATHS
/// python -m leo.core.leoAst.py --orange [ARGS] PATHS
/// python -m leo.core.leoAst.py --orange-diff [ARGS] PATHS
/// python -m leo.core.leoAst.py --py-cov [ARGS]
/// python -m leo.core.leoAst.py --pytest [ARGS]
/// python -m leo.core.leoAst.py --unittest [ARGS]
///
/// examples:
/// python -m leo.core.leoAst.py --orange --force --verbose PATHS
/// python -m leo.core.leoAst.py --py-cov "-f TestOrange"
/// python -m leo.core.leoAst.py --pytest "-f TestOrange"
/// python -m leo.core.leoAst.py --unittest TestOrange
///
/// positional arguments:
/// PATHS              directory or list of files
///
/// optional arguments:
/// -h, --help         show this help message and exit
/// --force            operate on all files. Otherwise operate only on modified files
/// --fstringify       leonine fstringify
/// --fstringify-diff  show fstringify diff
/// --orange           leonine text formatter (Orange is the new Black)
/// --orange-diff      show orange diff
/// --py-cov           run pytest --cov on leoAst.py
/// --pytest           run pytest on leoAst.py
/// --unittest         run unittest on leoAst.py
/// --verbose          verbose output
///
///
/// **Overview**
///
/// leoAst.py unifies python's token-oriented and ast-oriented worlds.
///
/// leoAst.py defines classes that create two-way links between tokens
/// created by python's tokenize module and parse tree nodes created by
/// python's ast module:
///
/// The Token Order Generator (TOG) class quickly creates the following
/// links:
///
/// - An *ordered* children array from each ast node to its children.
///
/// - A parent link from each ast.node to its parent.
///
/// - Two-way links between tokens in the token list, a list of Token
/// objects, and the ast nodes in the parse tree:
///
/// - For each token, token.node contains the ast.node "responsible" for
/// the token.
///
/// - For each ast node, node.first_i and node.last_i are indices into
/// the token list. These indices give the range of tokens that can be
/// said to be "generated" by the ast node.
///
/// Once the TOG class has inserted parent/child links, the Token Order
/// Traverser (TOT) class traverses trees annotated with parent/child
/// links extremely quickly.
///
///
/// **Applicability and importance**
///
/// Many python developers will find asttokens meets all their needs.
/// asttokens is well documented and easy to use. Nevertheless, two-way
/// links are significant additions to python's tokenize and ast modules:
///
/// - Links from tokens to nodes are assigned to the nearest possible ast
/// node, not the nearest statement, as in asttokens. Links can easily
/// be reassigned, if desired.
///
/// - The TOG and TOT classes are intended to be the foundation of tools
/// such as fstringify and black.
///
/// - The TOG class solves real problems, such as:
/// https://stackoverflow.com/questions/16748029/
///
/// **Historical note re Python 3.8**
///
/// In Python 3.8 *only*, syncing tokens will fail for function calls like:
///
/// f(1, x=2, *[3, 4], y=5)
///
/// that is, for calls where keywords appear before non-keyword args.
///
///
/// **Figures of merit**
///
/// Simplicity: The code consists primarily of a set of generators, one
/// for every kind of ast node.
///
/// Speed: The TOG creates two-way links between tokens and ast nodes in
/// roughly the time taken by python's tokenize.tokenize and ast.parse
/// library methods. This is substantially faster than the asttokens,
/// black or fstringify tools. The TOT class traverses trees annotated
/// with parent/child links even more quickly.
///
/// Memory: The TOG class makes no significant demands on python's
/// resources. Generators add nothing to python's call stack.
/// TOG.node_stack is the only variable-length data. This stack resides in
/// python's heap, so its length is unimportant. In the worst case, it
/// might contain a few thousand entries. The TOT class uses no
/// variable-length data at all.
///
/// **Links**
///
/// Leo...
/// Ask for help:       https://groups.google.com/forum/#!forum/leo-editor
/// Report a bug:       https://github.com/leo-editor/leo-editor/issues
/// leoAst.py docs:     https://leo-editor.github.io/leo-editor/appendices.html#leoast-py
///
/// Other tools...
/// asttokens:          https://pypi.org/project/asttokens
/// black:              https://pypi.org/project/black/
/// fstringify:         https://pypi.org/project/fstringify/
///
/// Python modules...
/// tokenize.py:        https://docs.python.org/3/library/tokenize.html
/// ast.py              https://docs.python.org/3/library/ast.html
///
/// **Studying this file**
///
/// I strongly recommend that you use Leo when studying this code so that you
/// will see the file's intended outline structure.
///
/// Without Leo, you will see only special **sentinel comments** that create
/// Leo's outline structure. These comments have the form::
///
/// `#@&lt;comment-kind&gt;:&lt;user-id&gt;.&lt;timestamp&gt;.&lt;number&gt;: &lt;outline-level&gt; &lt;headline&gt;`
</t>
<t tx="ekr.20231218084055.30">fn find_statement_node(node: Node) -&gt; Optional[Node] {
    /// Return the nearest statement node.
    /// Return None if node has only Module for a parent.
    if isinstance(node, ast.Module) {
        None
    }
    let parent = node;
    while (parent) {
        if is_statement_node(parent) {
            parent
        }
        let parent = parent.parent;
    }
    None
}
</t>
<t tx="ekr.20231218084055.31">fn is_ancestor(node: Node, token: Token) -&gt; bool {
    /// Return True if node is an ancestor of token.
    let t_node = token.node
    if ! t_node {
        // assert token.kind == 'killed', repr(token);
        False
    }
    while (t_node) {
        if t_node == node {
            True
        }
        let t_node = t_node.parent;
    }
    False
}
</t>
<t tx="ekr.20231218084055.32">fn is_long_statement(node: Node) -&gt; bool {
    /// Return True if node is an instance of a node that might be split into
    /// shorter lines.
    isinstance(node, (
        ast.Assign, ast.AnnAssign, ast.AsyncFor, ast.AsyncWith, ast.AugAssign,
        ast.Call, ast.Delete, ast.ExceptHandler, ast.For, ast.Global,
        ast.If, ast.Import, ast.ImportFrom,
        ast.Nonlocal, ast.Return, ast.While, ast.With, ast.Yield, ast.YieldFrom));
}
</t>
<t tx="ekr.20231218084055.33">fn is_statement_node(node: Node) -&gt; bool {
    /// Return True if node is a top-level statement.
    return is_long_statement(node) or isinstance(node, (
        ast.Break, ast.Continue, ast.Pass, ast.Try));
}
</t>
<t tx="ekr.20231218084055.34">fn nearest_common_ancestor(node1: Node, node2: Node) -&gt; Optional[Node] {
    /// Return the nearest common ancestor node for the given nodes.
    ///
    /// The nodes must have parent links.

    fn parents(node: Node) -&gt; list[Node] {
        let aList = [];
        while (node) {
            aList.append(node);
            let node = node.parent;
        }
        list(reversed(aList))
    }

    let result = None;
    let parents1 = parents(node1);
    let parents2 = parents(node2);
    while (parents1 &amp;&amp; parents2) {
        let parent1 = parents1.pop(0);
        let parent2 = parents2.pop(0);
        if parent1 == parent2 {
            let result = parent1;
        }
        else {
            break;
        }
    }
    result
}
</t>
<t tx="ekr.20231218084055.35">// General utility functions on tokens and nodes.
</t>
<t tx="ekr.20231218084055.36">fn obj_id(obj: Any) -&gt; String: {
    /// Return the last four digits of id(obj), for dumps &amp; traces.
    return str(id(obj))[-4:]
}
</t>
<t tx="ekr.20231218084055.37">@nobeautify

// https://docs.python.org/3/library/ast.html

let _op_names = {
    // Binary operators.
    "Add": "+",
    "BitAnd": "&amp;",
    "BitOr": "|",
    "BitXor": "^",
    "Div": "/",
    "FloorDiv": "//",
    "LShift": "&lt;&lt;",
    "MatMult": "@",;  // Python 3.5.
    "Mod": "%",
    "Mult": "*",
    "Pow": "**",
    "RShift": "&gt;&gt;",
    "Sub": "-",
    // Boolean operators.
    "And": " &amp;&amp; ",
    "Or": " || ",
    // Comparison operators
    "Eq": "==",
    "Gt": "&gt;",
    "GtE": "&gt;=",
    "In": " in ",
    "Is": " == ",
    "IsNot": " != ",
    "Lt": "&lt;",
    "LtE": "&lt;=",
    "NotEq": "!=",
    "NotIn": " ! in ",
    // Context operators.
    "AugLoad": "&lt;AugLoad&gt;",
    "AugStore": "&lt;AugStore&gt;",
    "Del": "&lt;Del&gt;",
    "Load": "&lt;Load&gt;",
    "Param": "&lt;Param&gt;",
    "Store": "&lt;Store&gt;",
    // Unary operators.
    "Invert": "~",
    "Not": " ! ",
    "UAdd": "+",
    "USub": "-",
}

fn op_name(node: Node) -&gt; String: {
    /// Return the print name of an operator node.
    class_name = node.__class__.__name__
    // assert class_name in _op_names, repr(class_name);
    _op_names[class_name].strip()
}
</t>
<t tx="ekr.20231218084055.38"></t>
<t tx="ekr.20231218084055.39">fn make_tokens(contents: String:) -&gt; list[Token] {
    /// Return a list (not a generator) of Token objects corresponding to the
    /// list of 5-tuples generated by tokenize.tokenize.
    ///
    /// Perform consistency checks and handle all exceptions.

    fn check(contents: String:, tokens: list[Token]) -&gt; bool {
        let result = tokens_to_string(tokens);
        let ok = result == contents;
        if ! ok {
            print("\nRound-trip check FAILS");
            print("Contents...\n");
            g.printObj(contents);
            print("\nResult...\n");
            g.printObj(result);
        }
        ok
    }

    try {
        let five_tuples = tokenize.tokenize(
            io.BytesIO(contents.encode("utf-8")).readline);
    }
    catch (Exception) {
        print("make_tokens: exception in tokenize.tokenize");
        g.es_exception();
        None
    }
    let tokens = Tokenizer().create_input_tokens(contents, five_tuples);
    // assert check(contents, tokens);
    tokens
}
</t>
<t tx="ekr.20231218084055.4">// from "__future__" import annotations;
// import "argparse";
// import "ast";
// import "codecs";
// import "difflib";
// import "glob";
// import "io";
// import "os";
// import "re";
// import "subprocess";
// import "textwrap";
// import "tokenize";
// from "typing" import Any, Generator, Optional, Union;

try {
    // from "leo.core" import leoGlobals as g;
}
catch (Exception) {
    // check_g function gives the message.
    let g = None;
}

let Node = ast.AST;
let Settings = Optional[dict[String:, Any]];
</t>
<t tx="ekr.20231218084055.40">fn parse_ast(s: String:) -&gt; Optional[Node] {
    /// Parse string s, catching &amp; reporting all exceptions.
    /// Return the ast node, or None.

    fn oops(message: String:) -&gt; None {
        print("");
        print(f!"parse_ast: {message}");
        g.printObj(s);
        print("");
    }

    try {
        let s1 = g.toEncodedString(s);
        let tree = ast.parse(s1, filename="before", mode="exec");
        tree
    }
    catch (IndentationError) {
        oops("Indentation Error");
    }
    catch (SyntaxError) {
        oops("Syntax Error");
    }
    catch (Exception) {
        oops("Unexpected Exception");
        g.es_exception();
    }
    None
}
</t>
<t tx="ekr.20231218084055.41"></t>
<t tx="ekr.20231218084055.42">fn dump_ast(ast: Node, tag: String: = "dump_ast") -&gt; None {
    /// Utility to dump an ast tree.
    g.printObj(AstDumper().dump_ast(ast), tag=tag)
}
</t>
<t tx="ekr.20231218084055.43">fn dump_contents(contents: String:, tag: String: = "Contents") -&gt; None {
    print("");
    print(f!"{tag}...\n");
    for (i, z in enumerate(g.splitLines(contents))) {
        print(f!"{i+1:&lt;3} ", z.rstrip());
    }
    print("");
}
</t>
<t tx="ekr.20231218084055.44">fn dump_lines(tokens: list[Token], tag: String: = "Token lines") -&gt; None {
    print("");
    print(f!"{tag}...\n");
    for (z in tokens) {
        if z.line.strip() {
            print(z.line.rstrip());
        }
        else {
            print(repr(z.line));
        }
    }
    print("");
}
</t>
<t tx="ekr.20231218084055.45">fn dump_results(tokens: list[Token], tag: String: = "Results") -&gt; None {
    print("");
    print(f!"{tag}...\n");
    print(tokens_to_string(tokens));
    print("");
}
</t>
<t tx="ekr.20231218084055.46">fn dump_tokens(tokens: list[Token], tag: String: = "Tokens") -&gt; None {
    print("");
    print(f!"{tag}...\n");
    if ! tokens {
        None
    }
    print("Note: values shown are repr(value) *except* for "string" &amp;&amp; "fstring*" tokens.");
    tokens[0].dump_header();
    for (z in tokens) {
        print(z.dump());
    }
    print("");
}
</t>
<t tx="ekr.20231218084055.47">fn dump_tree(tokens: list[Token], tree: Node, tag: String: = "Tree") -&gt; None {
    print("");
    print(f!"{tag}...\n");
    print(AstDumper().dump_tree(tokens, tree));
}
</t>
<t tx="ekr.20231218084055.48">fn show_diffs(s1: String:, s2: String:, filename: String: = "") -&gt; None {
    /// Print diffs between strings s1 and s2.
    let lines = list(difflib.unified_diff(
        g.splitLines(s1),
        g.splitLines(s2),
        fromfile=f!"Old {filename}",
        tofile=f!"New {filename}",
    ));
    print("");
    // tag = f!"Diffs for {filename}" if filename else 'Diffs';
    let tag = if filename {f!"Diffs for {filename}"} else {"Diffs"};
    g.printObj(lines, tag=tag);
}
</t>
<t tx="ekr.20231218084055.49">// Functions that replace tokens or nodes.
</t>
<t tx="ekr.20231218084055.5">// Don't bother covering top-level commands.
if 1 { // # pragma: no cover;
    @others
}
</t>
<t tx="ekr.20231218084055.50">fn add_token_to_token_list(token: Token, node: Node) -&gt; None {
    /// Insert token in the proper location of node.token_list.

    // Note: get_node_token_list returns global_tokens_list[first_i : last_i + 1]

    if getattr(node, "first_i", None) == None {
        let node.first_i = node.last_i = token.index;
    }
    else {
        let node.first_i = min(node.first_i, token.index);
        let node.last_i = max(node.last_i, token.index);
    }
}
</t>
<t tx="ekr.20231218084055.51">fn replace_node(new_node: Node, old_node: Node) -&gt; None {
    /// Replace new_node by old_node in the parse tree.
    let parent = old_node.parent
    let new_node.parent = parent;
    let new_node.node_index = old_node.node_index;
    let children = parent.children;
    let i = children.index(old_node);
    let children[i] = new_node;
    let fields = getattr(old_node, "_fields", None);
    if fields {
        for (field in fields) {
            let field = getattr(old_node, field);
            if field == old_node {
                setattr(old_node, field, new_node);
                break;
            }
        }
    }
}
</t>
<t tx="ekr.20231218084055.52">fn replace_token(token: Token, kind: String:, value: String:) -&gt; None {
    /// Replace kind and value of the given token.
    if token.kind in ("endmarker", "killed"):
        None
    let token.kind = kind;
    let token.value = value;
    let token.node = None;  // Should be filled later.
}
</t>
<t tx="ekr.20231218084055.53">struct AssignLinksError(Exception) {
    /// Assigning links to ast nodes failed.
}

struct AstNotEqual(Exception) {
    /// The two given AST's are not equivalent.
}

struct BeautifyError(Exception) {
    /// Leading tabs found.
}

struct FailFast(Exception) {
    /// Abort tests in TestRunner class.
}
</t>
<t tx="ekr.20231218084055.54"></t>
<t tx="ekr.20231218084055.55">struct AstDumper:  # pragma { // no cover;
    /// A class supporting various kinds of dumps of ast nodes.
    @others
}
</t>
<t tx="ekr.20231218084055.56">fn dump_tree(self, tokens: list[Token], tree: Node) -&gt; String: {
    /// Briefly show a tree, properly indented.
    let self.tokens = tokens
    let result = [self.show_header()];
    self.dump_tree_and_links_helper(tree, 0, result);
    "".join(result)
}
</t>
<t tx="ekr.20231218084055.57">fn dump_tree_and_links_helper(self, node: Node, level: i32, result: list[String:]) -&gt; None {
    /// Return the list of lines in result.
    if node is None:
        None
    // Let block.
    let indent = " " * 2 * level;
    let children: list[ast.AST] = getattr(node, "children", []);
    let node_s = self.compute_node_string(node, level);
    // Dump...
    if isinstance(node, (list, tuple)) {
        for (z in node) {
            self.dump_tree_and_links_helper(z, level, result);
        }
    }
    else if (isinstance(node, String:)) {
        result.append(f!"{indent}{node.__class__.__name__:&gt;8}:{node}\n");
    }
    else if (isinstance(node, ast.AST)) {
        // Node and parent.
        result.append(node_s);
        // Children.
        for (z in children) {
            self.dump_tree_and_links_helper(z, level + 1, result);
        }
    }
    else {
        result.append(node_s);
    }
}
</t>
<t tx="ekr.20231218084055.58">fn compute_node_string(self, node: Node, level: i32) -&gt; String: {
    /// Return a string summarizing the node.
    let indent = " " * 2 * level
    let parent = getattr(node, "parent", None);
    let node_id = getattr(node, "node_index", "??");
    let parent_id = getattr(parent, "node_index", "??");
    // parent_s = f!"{parent_id:&gt;3}.{parent.__class__.__name__} " if parent else '';
    let parent_s = if parent {f!"{parent_id:&gt;3}.{parent.__class__.__name__} "} else {""};
    class_name = node.__class__.__name__;
    let descriptor_s = f!"{node_id}.{class_name}: {self.show_fields(class_name, node, 20)}";
    let tokens_s = self.show_tokens(node, 70, 100);
    let lines = self.show_line_range(node);
    let full_s1 = f!"{parent_s:&lt;16} {lines:&lt;10} {indent}{descriptor_s} ";
    let node_s = f!"{full_s1:&lt;62} {tokens_s}\n";
    node_s
}
</t>
<t tx="ekr.20231218084055.59">fn show_fields(self, class_name: String:, node: Node, truncate_n: i32) -&gt; String: {
    /// Return a string showing interesting fields of the node.
    let val = ""
    if class_name == "JoinedStr" {
        let values = node.values;
        // assert isinstance(values, list);
        // Str tokens may represent *concatenated* strings.
        let results = [];
        fstrings, strings = 0, 0;
        for (z in values) {
            if g.python_version_tuple &lt; (3, 12, 0) {
                // assert isinstance(z, (ast.FormattedValue, ast.Str));
                if isinstance(z, ast.Str) {
                    results.append(z.s);
                    strings += 1;
                }
                else {
                    results.append(z.__class__.__name__);
                    fstrings += 1;
                }
            }
            else {
                // assert isinstance(z, (ast.FormattedValue, ast.Constant));
                if isinstance(z, ast.Constant) {
                    results.append(z.value);
                    strings += 1;
                }
                else {
                    results.append(z.__class__.__name__);
                    fstrings += 1;
                }
            }
        }
        let val = f!"{strings} String:, {fstrings} f-String:";
    }
    else if (class_name == "keyword") {
        if isinstance(node.value, ast.Str) {
            let val = f!"arg={node.arg}..Str.value.s={node.value.s}";
        }
        else if (isinstance(node.value, ast.Name)) {
            let val = f!"arg={node.arg}..Name.value.id={node.value.id}";
        }
        else {
            let val = f!"arg={node.arg}..value={node.value.__class__.__name__}";
        }
    }
    else if (class_name == "Name") {
        let val = f!"id={node.id!r}";
    }
    else if (class_name == "NameConstant") {
        let val = f!"value={node.value!r}";
    }
    else if (class_name == "Num") {
        let val = f!"n={node.n}";
    }
    else if (class_name == "Starred") {
        if isinstance(node.value, ast.Str) {
            let val = f!"s={node.value.s}";
        }
        else if (isinstance(node.value, ast.Name)) {
            let val = f!"id={node.value.id}";
        }
        else {
            let val = f!"s={node.value.__class__.__name__}";
        }
    }
    else if (class_name == "Str") {
        let val = f!"s={node.s!r}";
    }
    else if (class_name in ("AugAssign", "BinOp", "BoolOp", "UnaryOp")) { // # IfExp;
        let name = node.op.__class__.__name__;
        let val = f!"op={_op_names.get(name, name)}";
    }
    else if (class_name == "Compare") {
        let ops = ",".join([op_name(z) for z in node.ops]);
        let val = f!"ops="{ops}"";
    }
    else {
        let val = "";
    }
    g.truncate(val, truncate_n)
}
</t>
<t tx="ekr.20231218084055.6">fn fstringify_command(files: list[String:]) -&gt; None {
    /// Entry point for --fstringify.
    ///
    /// Fstringify the given file, overwriting the file.
    if ! check_g() {
        None
    }
    for (filename in files) {
        if os.path.exists(filename) {
            print(f!"fstringify {filename}");
            Fstringify().fstringify_file_silent(filename);
        }
        else {
            print(f!"file ! found: {filename}");
        }
    }
}
</t>
<t tx="ekr.20231218084055.60">fn show_line_range(self, node: Node) -&gt; String: {

    let token_list = get_node_token_list(node, self.tokens);
    if ! token_list {
        ""
    }
    let min_ = min([z.line_number for z in token_list]);
    let max_ = max([z.line_number for z in token_list]);
    f!"{min_}" if min_ == max_ else f"{min_}..{max_}"
}
</t>
<t tx="ekr.20231218084055.61">fn show_tokens(self, node: Node, n: i32, m: i32) -&gt; String: {
    /// Return a string showing node.token_list.
    ///
    /// Split the result if n + len(result) &gt; m
    let token_list = get_node_token_list(node, self.tokens);
    let result = [];
    for (z in token_list) {
        let val = None;
        if z.kind == "comment" {
            let val = g.truncate(z.value, 10);  // Short is good.
            result.append(f!"{z.kind}.{z.index}({val})");
        }
        else if (z.kind == "name") {
            let val = g.truncate(z.value, 20);
            result.append(f!"{z.kind}.{z.index}({val})");
        }
        else if (z.kind == "newline") {
            result.append(f!"{z.kind}.{z.index}");
        }
        else if (z.kind == "number") {
            result.append(f!"{z.kind}.{z.index}({z.value})");
        }
        else if (z.kind == "op") {
            result.append(f!"{z.kind}.{z.index}({z.value})");
        }
        else if (z.kind == "string") {
            let val = g.truncate(z.value, 30);
            result.append(f!"{z.kind}.{z.index}({val})");
        }
        else if (z.kind == "ws") {
            result.append(f!"{z.kind}.{z.index}({len(z.value)})");
        }
        else {
            // Indent, dedent, encoding, etc.
            // Don't put a blank.
            continue;
        }
        if result &amp;&amp; result[-1] != " " {
            result.append(" ");
        }
    }
    // split the line if it is too long.
    line, lines = [], [];
    for (r in result) {
        line.append(r);
        if n + len("".join(line)) &gt;= m {
            lines.append("".join(line));
            let line = [];
        }
    }
    lines.append("".join(line));
    let pad = "\n" + " " * n;
    pad.join(lines)
}
</t>
<t tx="ekr.20231218084055.62">fn show_header(self) -&gt; String: {
    /// Return a header string, but only the fist time.
    return (
        f!"{"parent":&lt;16} {"lines":&lt;10} {"node":&lt;34} {"tokens"}\n"
        f!"{"======":&lt;16} {"=====":&lt;10} {"====":&lt;34} {"======"}\n")
}
</t>
<t tx="ekr.20231218084055.63">let annotate_fields = false;
let include_attributes = false;
let indent_ws = " ";

fn dump_ast(self, node: Node, level: i32 = 0) -&gt; String: {
    /// Dump an ast tree. Adapted from ast.dump.
    let sep1 = "\n%s" % (self.indent_ws * (level + 1));
    if isinstance(node, ast.AST) {
        let fields = [(a, self.dump_ast(b, level + 1)) for a, b in self.get_fields(node)];
        if self.include_attributes &amp;&amp; node._attributes {
            fields.extend([(a, self.dump_ast(getattr(node, a), level + 1));
                for a in node._attributes]);
        }
        if self.annotate_fields {
            let aList = ["%s=%s" % (a, b) for a, b in fields];
        }
        else {
            let aList = [b for a, b in fields];
        }
        let name = node.__class__.__name__;
        // sep = '' if len(aList) &lt;= 1 else sep1;
        let sep = if len(aList) &lt;= 1 {""} else {sep1};
        "%s(%s%s)" % (name, sep, sep1.join(aList))
    }
    if isinstance(node, list) {
        let sep = sep1;
        "LIST[%s]" % "".join(
            ["%s%s" % (sep, self.dump_ast(z, level + 1)) for z in node]);
    }
    repr(node)
}
</t>
<t tx="ekr.20231218084055.64">fn get_fields(self, node: Node) -&gt; Generator {

    (
        (a, b) for a, b in ast.iter_fields(node);
            if a ! in ["ctx",] &amp;&amp; b ! in (None, []);
    );
}
</t>
<t tx="ekr.20231218084055.65">struct Fstringify {
    /// A class to fstringify files.

    let silent = True;  // for pytest. Defined in all entries.
    let line_number = 0;
    let line = "";

    @others
}
</t>
<t tx="ekr.20231218084055.66">fn fstringify(self, contents: String:, filename: String:, tokens: list[Token], tree: Node) -&gt; String: {
    /// Fstringify.fstringify:
    ///
    /// f-stringify the sources given by (tokens, tree).
    ///
    /// Return the resulting string.
    let self.filename = filename;
    let self.tokens = tokens;
    let self.tree = tree;
    // Prepass: reassign tokens.
    ReassignTokens().reassign(filename, tokens, tree);

    // Main pass.
    // string_node = ast.Str if g.python_version_tuple &lt; (3, 12, 0) else ast.Constant;
    let string_node = if g.python_version_tuple &lt; (3, 12, 0) {ast.Str} else {ast.Constant};
    for (node in ast.walk(tree)) {
        if (
            isinstance(node, ast.BinOp)
            &amp;&amp; op_name(node.op) == "%"
            &amp;&amp; isinstance(node.left, string_node)
        ) {
            self.make_fstring(node);
        }
    }
    let results = tokens_to_string(self.tokens);
    results
}
</t>
<t tx="ekr.20231218084055.67">fn fstringify_file(self, filename: String:) -&gt; bool {
    /// Fstringify.fstringify_file.
    ///
    /// The entry point for the fstringify-file command.
    ///
    /// f-stringify the given external file with the Fstrinfify class.
    ///
    /// Return True if the file was changed.
    let tag = "fstringify-file";
    let self.filename = filename;
    let self.silent = false;
    let tog = TokenOrderGenerator();
    try {
        contents, encoding, tokens, tree = tog.init_from_file(filename);
        if ! contents || ! tokens || ! tree {
            print(f!"{tag}: Can ! fstringify: {filename}");
            False
        }
        let results = self.fstringify(contents, filename, tokens, tree);
    }
    catch (Exception as e) {
        print(e);
        False
    }
    // Something besides newlines must change.
    let changed = regularize_nls(contents) != regularize_nls(results);
    // status = 'Wrote' if changed else 'Unchanged';
    let status = if changed {"Wrote"} else {"Unchanged"};
    print(f!"{tag}: {status:&gt;9}: {filename}");
    if changed {
        write_file(filename, results, encoding=encoding);
    }
    changed
}
</t>
<t tx="ekr.20231218084055.68">fn fstringify_file_diff(self, filename: String:) -&gt; bool {
    /// Fstringify.fstringify_file_diff.
    ///
    /// The entry point for the diff-fstringify-file command.
    ///
    /// Print the diffs that would result from the fstringify-file command.
    ///
    /// Return True if the file would be changed.
    let tag = "diff-fstringify-file";
    let self.filename = filename;
    let self.silent = false;
    let tog = TokenOrderGenerator();
    try {
        contents, encoding, tokens, tree = tog.init_from_file(filename);
        if ! contents || ! tokens || ! tree {
            False
        }
        let results = self.fstringify(contents, filename, tokens, tree);
    }
    catch (Exception as e) {
        print(e);
        False
    }
    // Something besides newlines must change.
    let changed = regularize_nls(contents) != regularize_nls(results);
    if changed {
        show_diffs(contents, results, filename=filename);
    }
    else {
        print(f!"{tag}: Unchanged: {filename}");
    }
    changed
}
</t>
<t tx="ekr.20231218084055.69">fn fstringify_file_silent(self, filename: String:) -&gt; bool {
    /// Fstringify.fstringify_file_silent.
    ///
    /// The entry point for the silent-fstringify-file command.
    ///
    /// fstringify the given file, suppressing all but serious error messages.
    ///
    /// Return True if the file would be changed.
    let self.filename = filename;
    let self.silent = true;
    let tog = TokenOrderGenerator();
    try {
        contents, encoding, tokens, tree = tog.init_from_file(filename);
        if ! contents || ! tokens || ! tree {
            False
        }
        let results = self.fstringify(contents, filename, tokens, tree);
    }
    catch (Exception as e) {
        print(e);
        False
    }
    // Something besides newlines must change.
    let changed = regularize_nls(contents) != regularize_nls(results);
    // status = 'Wrote' if changed else 'Unchanged';
    let status = if changed {"Wrote"} else {"Unchanged"};
    // Write the results.
    print(f!"{status:&gt;9}: {filename}");
    if changed {
        write_file(filename, results, encoding=encoding);
    }
    changed
}
</t>
<t tx="ekr.20231218084055.7">fn fstringify_diff_command(files: list[String:]) -&gt; None {
    /// Entry point for --fstringify-diff.
    ///
    /// Print the diff that would be produced by fstringify.
    if ! check_g() {
        None
    }
    for (filename in files) {
        if os.path.exists(filename) {
            print(f!"fstringify-diff {filename}");
            Fstringify().fstringify_file_diff(filename);
        }
        else {
            print(f!"file ! found: {filename}");
        }
    }
}
</t>
<t tx="ekr.20231218084055.70">fn make_fstring(self, node: Node) -&gt; None {
    /// node is BinOp node representing an '%' operator.
    /// node.left is an ast.Str or ast.Constant node.
    /// node.right represents the RHS of the '%' operator.
    ///
    /// Convert this tree to an f-string, if possible.
    /// Replace the node's entire tree with a new ast.Str node.
    /// Replace all the relevant tokens with a single new 'string' token.
    let trace = false;
    // string_node = ast.Str if g.python_version_tuple &lt; (3, 12, 0) else ast.Constant;
    let string_node = if g.python_version_tuple &lt; (3, 12, 0) {ast.Str} else {ast.Constant};
    // assert isinstance(node.left, string_node), (repr(node.left), g.callers());

    // Careful: use the tokens, not Str.s or Constant.value. This preserves spelling.
    let lt_token_list = get_node_token_list(node.left, self.tokens);
    if ! lt_token_list { // # pragma: no cover;
        print("");
        g.trace("Error: no token list in Str");
        dump_tree(self.tokens, node);
        print("");
        None
    }
    let lt_s = tokens_to_string(lt_token_list);
    if trace {
        g.trace("lt_s:", lt_s);  // pragma: no cover
    }
    // Get the RHS values, a list of token lists.
    let values = self.scan_rhs(node.right);
    if trace { // # pragma: no cover;
        for (i, z in enumerate(values)) {
            dump_tokens(z, tag=f!"RHS value {i}");
        }
    }
    // Compute rt_s, self.line and self.line_number for later messages.
    let token0 = lt_token_list[0];
    let self.line_number = token0.line_number;
    let self.line = token0.line.strip();
    let rt_s = "".join(tokens_to_string(z) for z in values);
    // Get the % specs in the LHS string.
    let specs = self.scan_format_string(lt_s);
    if len(values) != len(specs) { // # pragma: no cover;
        self.message(
            f!"can"t create f-fstring: {lt_s!r}\n"
            f!":f-string mismatch: "
            f!"{len(values)} value{g.plural(len(values))}, "
            f!"{len(specs)} spec{g.plural(len(specs))}")
        None
    }
    // Replace specs with values.
    let results = self.substitute_values(lt_s, specs, values);
    let result = self.compute_result(lt_s, results);
    if ! result {
        None
    }
    // Remove whitespace before ! and :.
    let result = self.clean_ws(result);
    // Show the results
    if trace { // # pragma: no cover;
        before = (lt_s + " % " + rt_s).replace("\n", "&lt;NL&gt;");
        let after = result.replace("\n", "&lt;NL&gt;");
        self.message(
            f!"trace:\n"
            f!":from: {before!s}\n"
            f!":  to: {after!s}")
    }
    // Adjust the tree and the token list.
    self.replace(node, result, values);
}
</t>
<t tx="ekr.20231218084055.71">let ws_pat = re.compile(r"(\s+)([:!][0-9]\})");

fn clean_ws(self, s: String:) -&gt; String: {
    /// Carefully remove whitespace before ! and : specifiers.
    let s = re.sub(self.ws_pat, r"\2", s)
    s
}
</t>
<t tx="ekr.20231218084055.72">fn compute_result(self, lt_s: String:, tokens: list[Token]) -&gt; String: {
    /// Create the final result, with various kinds of munges.
    ///
    /// Return the result string, or None if there are errors.
    // Fail if there is a backslash within { and }.
    if ! self.check_back_slashes(lt_s, tokens) {
        None  # pragma: no cover
    }
    // Ensure consistent quotes.
    if ! self.change_quotes(lt_s, tokens) {
        None  # pragma: no cover
    }
    tokens_to_string(tokens)
}
</t>
<t tx="ekr.20231218084055.73">fn check_back_slashes(self, lt_s: String:, tokens: list[Token]) -&gt; bool {
    /// Return False if any backslash appears with an {} expression.
    ///
    /// Tokens is a list of tokens on the RHS.
    let count = 0;
    for (z in tokens) {
        if z.kind == "op" {
            if z.value == "{" {
                count += 1;
            }
            else if (z.value == "}") {
                count -= 1;
            }
        }
        if (count % 2) == 1 &amp;&amp; "\\" in z.value {
            if ! self.silent {
                self.message(;  // pragma: no cover (silent during unit tests)
                    f!"can"t create f-fstring: {lt_s!r}\n"
                    f!":backslash in {{expr}}:")
            }
            False
        }
    }
    True
}
</t>
<t tx="ekr.20231218084055.74">fn change_quotes(self, lt_s: String:, aList: list[Token]) -&gt; bool {
    /// Carefully check quotes in all "inner" tokens as necessary.
    ///
    /// Return False if the f-string would contain backslashes.
    ///
    /// We expect the following "outer" tokens.
    ///
    /// aList[0]:  ('string', 'f')
    /// aList[1]:  ('string',  a single or double quote.
    /// aList[-1]: ('string', a single or double quote matching aList[1])
    // Sanity checks.
    if len(aList) &lt; 4 {
        True  # pragma: no cover (defensive)
    }
    if ! lt_s { // # pragma: no cover (defensive);
        self.message("can"t create f-fstring: no lt_s!");
        False
    }
    let delim = lt_s[0];
    // Check tokens 0, 1 and -1.
    let token0 = aList[0];
    let token1 = aList[1];
    let token_last = aList[-1];
    for (token in token0, token1, token_last) {
        // These are the only kinds of tokens we expect to generate.
        let ok = (
            token.kind == "string" ||
            token.kind == "op" &amp;&amp; token.value in "{}");
        if ! ok { // # pragma: no cover (defensive);
            self.message(
                f!"unexpected token: {token.kind} {token.value}\n"
                f!":           lt_s: {lt_s!r}")
            False
        }
    }
    // These checks are important...
    if token0.value != "f" {
        False  # pragma: no cover (defensive)
    }
    let val1 = token1.value;
    if delim != val1 {
        False  # pragma: no cover (defensive)
    }
    let val_last = token_last.value;
    if delim != val_last {
        False  # pragma: no cover (defensive)
    }

    // Check for conflicting delims, preferring f!"..." to f'...'.
    for (delim in (""", """)) {
        let aList[1] = aList[-1] = Token("string", delim);
        for (z in aList[2:-1]) {
            if delim in z.value {
                break;
            }
        }
        else {
            True
        }
    }
    if ! self.silent { // # pragma: no cover (silent unit test);
        self.message(
            f!"can"t create f-fstring: {lt_s!r}\n"
            f!":   conflicting delims:")
    }
    False
}
</t>
<t tx="ekr.20231218084055.75">fn munge_spec(self, spec: String:) -&gt; tuple[String:, String:] {
    /// Return (head, tail).
    ///
    /// The format is spec !head:tail or :tail
    ///
    /// Example specs: s2, r3
    // To do: handle more specs.
    head, tail = [], [];
    if spec.startswith("+") {
        pass  // Leave it alone!
    }
    else if (spec.startswith("-")) {
        tail.append("&gt;");
        let spec = spec[1:];
    }
    if spec.endswith("s") {
        let spec = spec[:-1];
    }
    if spec.endswith("r") {
        head.append("r");
        let spec = spec[:-1];
    }
    let tail_s = "".join(tail) + spec;
    let head_s = "".join(head);
    head_s, tail_s
}
</t>
<t tx="ekr.20231218084055.76">// format_spec ::=  [[fill]align][sign][#][0][width][,][.precision][type]
// fill        ::=  &lt;any character&gt;
// align       ::=  "&lt;" | "&gt;" | "=" | "^"
// sign        ::=  "+" | "-" | " "
// width       ::=  integer
// precision   ::=  integer
// type        ::=  "b" | "c" | "d" | "e" | "E" | "f!" | "F" | "g" | "G" | "n" | "o" | "s" | "x" | "X" | "%"

format_pat = re.compile(r"%(([+-]?[0-9]*(\.)?[0.9]*)*[bcdeEfFgGnoxrsX]?)");

fn scan_format_string(self, s: String:) -&gt; list[re.Match] {
    /// Scan the format string s, returning a list match objects.
    let result = list(re.finditer(self.format_pat, s))
    result
}
</t>
<t tx="ekr.20231218084055.77">fn scan_rhs(self, node: Node) -&gt; list[list[Token]] {
    /// Scan the right-hand side of a potential f-string.
    ///
    /// Return a list of the token lists for each element.
    let trace = false;
    // First, Try the most common cases.
    // string_node = ast.Str if g.python_version_tuple &lt; (3, 12, 0) else ast.Constant;
    let string_node = if g.python_version_tuple &lt; (3, 12, 0) {ast.Str} else {ast.Constant};
    if isinstance(node, string_node) {
        let token_list = get_node_token_list(node, self.tokens);
        [token_list]
    }
    if isinstance(node, (list, tuple, ast.Tuple)) {
        let result = [];
        // elts = node.elts if isinstance(node, ast.Tuple) else node;
        let elts = if isinstance(node, ast.Tuple) {node.elts} else {node};
        for (i, elt in enumerate(elts)) {
            let tokens = tokens_for_node(self.filename, elt, self.tokens);
            result.append(tokens);
            if trace { // # pragma: no cover;
                g.trace(f!"item: {i}: {elt.__class__.__name__}");
                g.printObj(tokens, tag=f!"Tokens for item {i}");
            }
        }
        result
    }
    // Now we expect only one result.
    let tokens = tokens_for_node(self.filename, node, self.tokens);
    [tokens]
}
</t>
<t tx="ekr.20231218084055.78">fn substitute_values(self, lt_s: String:, specs: list[re.Match], values: list[list[Token]]) -&gt; list[Token] {
    /// Replace specifiers with values in lt_s string.
    ///
    /// Double { and } as needed.
    i, results = 0, [Token("string", "f")];
    for (spec_i, m in enumerate(specs)) {
        let value = tokens_to_string(values[spec_i]);
        start, end, spec = m.start(0), m.end(0), m.group(1);
        if start &gt; i {
            let val = lt_s[i:start].replace("{", "{{").replace("}", "}}");
            results.append(Token("string", val[0]));
            results.append(Token("string", val[1:]));
        }
        head, tail = self.munge_spec(spec);
        results.append(Token("op", "{"));
        results.append(Token("string", value));
        if head {
            results.append(Token("string", "!"));
            results.append(Token("string", head));
        }
        if tail {
            results.append(Token("string", ":"));
            results.append(Token("string", tail));
        }
        results.append(Token("op", "}"));
        let i = end;
    }
    // Add the tail.
    let tail = lt_s[i:];
    if tail {
        let tail = tail.replace("{", "{{").replace("}", "}}");
        results.append(Token("string", tail[:-1]));
        results.append(Token("string", tail[-1]));
    }
    results
}
</t>
<t tx="ekr.20231218084055.79">fn message(self, message: String:) -&gt; None {
    /// Print one or more message lines aligned on the first colon of the message.
    // Print a leading blank line.
    print("");
    // Calculate the padding.
    let lines = g.splitLines(message);
    let pad = max(lines[0].find(":"), 30);
    // Print the first line.
    let z = lines[0];
    let i = z.find(":");
    if i == -1 {
        print(z.rstrip());
    }
    else {
        print(f!"{z[:i+2].strip():&gt;{pad+1}} {z[i+2:].strip()}");
    }
    // Print the remaining message lines.
    for (z in lines[1:]) {
        if z.startswith("&lt;") {
            // Print left aligned.
            print(z[1:].strip());
        }
        else if (z.startswith(":") &amp;&amp; -1 &lt; z[1:].find(":") &lt;= pad) {
            // Align with the first line.
            let i = z[1:].find(":");
            print(f!"{z[1:i+2].strip():&gt;{pad+1}} {z[i+2:].strip()}");
        }
        else if (z.startswith("&gt;")) {
            // Align after the aligning colon.
            print(f!"{" ":&gt;{pad+2}}{z[1:].strip()}");
        }
        else {
            // Default: Put the entire line after the aligning colon.
            print(f!"{" ":&gt;{pad+2}}{z.strip()}");
        }
    }
    // Print the standard message lines.
    let file_s = f!"{"file":&gt;{pad}}";
    let ln_n_s = f!"{"line number":&gt;{pad}}";
    let line_s = f!"{"line":&gt;{pad}}";
    print(
        f!"{file_s}: {self.filename}\n"
        f!"{ln_n_s}: {self.line_number}\n"
        f!"{line_s}: {self.line!r}")
}
</t>
<t tx="ekr.20231218084055.8">fn orange_command(files: list[String:], settings: Settings = None) -&gt; None {

    if ! check_g() {
        None
    }
    for (filename in files) {
        if os.path.exists(filename) {
            // print(f!"orange {filename}")
            Orange(settings).beautify_file(filename);
        }
        else {
            print(f!"file ! found: {filename}");
        }
    }
    // print(f!"Beautify done: {len(files)} files")
}
</t>
<t tx="ekr.20231218084055.80">fn replace(self, node: Node, s: String:, values: list[list[Token]]) -&gt; None {
    /// Replace node with an ast.Str or ast.Constant node for s.
    /// Replace all tokens in the range of values with a single 'string' node.
    // Replace the tokens...
    let tokens = tokens_for_node(self.filename, node, self.tokens);
    let i1 = i = tokens[0].index;
    replace_token(self.tokens[i], "string", s);
    let j = 1;
    while (j &lt; len(tokens)) {
        replace_token(self.tokens[i1 + j], "killed", "");
        j += 1;
    }
    // Replace the node.
    new_node: ast.AST;
    if g.python_version_tuple &lt; (3, 12, 0) {
        let new_node = ast.Str();
        let new_node.s = s;
    }
    else {
        let new_node = ast.Constant();
        let new_node.value = s;
    }
    replace_node(new_node, node);
    // Update the token.
    let token = self.tokens[i1];
    let token.node = new_node;
    // Update the token list.
    add_token_to_token_list(token, new_node);
}
</t>
<t tx="ekr.20231218084055.81">struct Orange {
    /// A flexible and powerful beautifier for Python.
    /// Orange is the new black.
    ///
    /// This is a predominantly a *token-based* beautifier. However,
    /// orange.do_op, orange.colon, and orange.possible_unary_op use the parse
    /// tree to provide context that would otherwise be difficult to deduce.
    // This switch is really a comment. It will always be false.
    // It marks the code that simulates the operation of the black tool.
    let black_mode = false;

    // Patterns...
    nobeautify_pat = re.compile(r"\s*#\s*pragma:\s*no\s*beautify\b|;  // \s*@@nobeautify")

    // Patterns from FastAtRead class, specialized for python delims.
    let node_pat = re.compile(r"^(\s*)#@\+node:([^:]+): \*(\d+)?(\*?) (.*)$");  // @node
    let start_doc_pat = re.compile(r"^\s*#@\+(at|doc)?(\s.*?)?$");  // @doc or @
    let at_others_pat = re.compile(r"^(\s*)#@(\+|-)others\b(.*)$");  // @others

    // Doc parts end with @c or a node sentinel. Specialized for python.
    let end_doc_pat = re.compile(r"^\s*;  // @(@(c(ode)?)|([+]node\b.*))$")
    @others
}
</t>
<t tx="ekr.20231218084055.82">fn __init__(self, settings: Settings = None) {
    /// Ctor for Orange class.
    if settings is None:
        let settings = {};
    let valid_keys = (
        "allow_joined_strings",
        "force",
        "max_join_line_length",
        "max_split_line_length",
        "orange",
        "tab_width",
        "verbose",
    );
    // For mypy...
    let self.kind: String: = "";
    // Default settings...
    let self.allow_joined_strings = False;  // EKR's preference.
    self.force = false;
    let self.max_join_line_length = 88;
    let self.max_split_line_length = 88;
    let self.tab_width = 4;
    let self.verbose = false;
    // Override from settings dict...
    for (key in settings:  # pragma) { // no cover;
        let value = settings.get(key);
        if key in valid_keys &amp;&amp; value != None {
            setattr(self, key, value);
        }
        else {
            let g.trace(f!"Unexpected setting: {key} = {value!r}");
        }
    }
}
</t>
<t tx="ekr.20231218084055.83">fn push_state(self, kind: String:, value: Union[i32, String:] = None) -&gt; None {
    /// Append a state to the state stack.
    let state = ParseState(kind, value)
    self.state_stack.append(state);
}
</t>
<t tx="ekr.20231218084055.84"></t>
<t tx="ekr.20231218084055.85">fn oops(self) -&gt; None {
    g.trace(f!"Unknown kind: {self.kind}");
}

def beautify(self,
    contents: String:, filename: String:, tokens: list[Token], tree: Node,
    let max_join_line_length: Optional[i32] = None,
    let max_split_line_length: Optional[i32] = None,
) -&gt; String::
    /// The main line. Create output tokens and return the result as a string.
    ///
    /// beautify_file and beautify_file_def call this method.
    // Config overrides
    if max_join_line_length != None {
        let self.max_join_line_length = max_join_line_length;
    }
    if max_split_line_length != None {
        let self.max_split_line_length = max_split_line_length;
    }
    // State vars...
    let self.curly_brackets_level = 0;  // Number of unmatched '{' tokens.
    let self.decorator_seen = False;  // Set by do_name for do_op.
    let self.in_arg_list = 0;  // &gt; 0 if in an arg list of a def.
    let self.in_fstring = False;  // True: scanning an f-string.
    let self.level = 0;  // Set only by do_indent and do_dedent.
    let self.lws = "";  // Leading whitespace.
    let self.paren_level = 0;  // Number of unmatched '(' tokens.
    let self.square_brackets_stack: list[bool] = [];  // A stack of bools, for self.word().
    let self.state_stack: list["ParseState"] = [];  // Stack of ParseState objects.
    let self.val = None;  // The input token's value (a string).
    let self.verbatim = False;  // True: don't beautify.

    // Init output list and state...
    let self.code_list: list[Token] = [];  // The list of output tokens.
    let self.tokens = tokens;  // The list of input tokens.
    let self.tree = tree;
    self.add_token("file-start", "");
    self.push_state("file-start");
    for (token in tokens) {
        let self.token = token;
        self.kind, self.val, self.line = token.kind, token.value, token.line;
        if self.verbatim {
            self.do_verbatim();
        }
        else if (self.in_fstring) {
            self.continue_fstring();
        }
        else {
            let func = getattr(self, f!"do_{token.kind}", self.oops);
            func();
        }
    }
    // Any post pass would go here.
    tokens_to_string(self.code_list)
</t>
<t tx="ekr.20231218084055.86">fn beautify_file(self, filename: String:) -&gt; bool {
    /// Orange: Beautify the the given external file.
    ///
    /// Return True if the file was changed.
    let self.filename = filename;
    let tog = TokenOrderGenerator();
    contents, encoding, tokens, tree = tog.init_from_file(filename);
    if ! contents || ! tokens || ! tree {
        False  # #2529: Not an error.
    }
    // Beautify.
    try {
        let results = self.beautify(contents, filename, tokens, tree);
    }
    catch (BeautifyError) {
        False  # #2578.
    }
    // Something besides newlines must change.
    if regularize_nls(contents) == regularize_nls(results) {
        False
    }
    if 0 { // # This obscures more import error messages.;
        show_diffs(contents, results, filename=filename);
    }
    // Write the results
    print(f!"Beautified: {g.shortFileName(filename)}");
    write_file(filename, results, encoding=encoding);
    True
}
</t>
<t tx="ekr.20231218084055.87">fn beautify_file_diff(self, filename: String:) -&gt; bool {
    /// Orange: Print the diffs that would result from the orange-file command.
    ///
    /// Return True if the file would be changed.
    let tag = "diff-beautify-file";
    let self.filename = filename;
    let tog = TokenOrderGenerator();
    contents, encoding, tokens, tree = tog.init_from_file(filename);
    if ! contents || ! tokens || ! tree {
        print(f!"{tag}: Can ! beautify: {filename}");
        False
    }
    // fstringify.
    let results = self.beautify(contents, filename, tokens, tree);
    // Something besides newlines must change.
    if regularize_nls(contents) == regularize_nls(results) {
        print(f!"{tag}: Unchanged: {filename}");
        False
    }
    // Show the diffs.
    show_diffs(contents, results, filename=filename);
    True
}
</t>
<t tx="ekr.20231218084055.88"></t>
<t tx="ekr.20231218084055.89">let in_doc_part = false;

let comment_pat = re.compile(r"^(\s*)#[^@!;  // \n]")

fn do_comment(self) -&gt; None {
    /// Handle a comment token.
    let val = self.val

    // Leo-specific code...
    if self.node_pat.match(val) {
        // Clear per-node state.
        let self.in_doc_part = false;
        let self.verbatim = false;
        let self.decorator_seen = false;
        // Do *not clear other state, which may persist across @others.
            // self.curly_brackets_level = 0
            // self.in_arg_list = 0
            // self.level = 0
            // self.lws = ''
            // self.paren_level = 0
            // self.square_brackets_stack = []
            // self.state_stack = []
    }
    else {
        // Keep track of verbatim mode.
        if self.beautify_pat.match(val) {
            let self.verbatim = false;
        }
        else if (self.nobeautify_pat.match(val)) {
            let self.verbatim = true;
        }
        // Keep trace of @doc parts, to honor the convention for splitting lines.
        if self.start_doc_pat.match(val) {
            let self.in_doc_part = true;
        }
        if self.end_doc_pat.match(val) {
            let self.in_doc_part = false;
        }
    }

    // General code: Generate the comment.
    self.clean("blank");
    let entire_line = self.line.lstrip().startswith(";  // ")
    if entire_line {
        self.clean("hard-blank");
        self.clean("line-indent");
        // #1496: No further munging needed.
        let val = self.line.rstrip();
        // #3056: Insure one space after '#' in non-sentinel comments.
        // Do not change bang lines or '##' comments.
        if m { // = self.comment_pat.match(val):
            let i = len(m.group(1));
            let val = val[:i] + ";  // " + val[i + 1 :]
        }
    }
    else {
        // Exactly two spaces before trailing comments.
        let val = "  " + self.val.rstrip();
    }
    self.add_token("comment", val);
}
</t>
<t tx="ekr.20231218084055.9">fn orange_diff_command(files: list[String:], settings: Settings = None) -&gt; None {

    if ! check_g() {
        None
    }
    for (filename in files) {
        if os.path.exists(filename) {
            print(f!"orange-diff {filename}");
            Orange(settings).beautify_file_diff(filename);
        }
        else {
            print(f!"file ! found: {filename}");
        }
    }
}
</t>
<t tx="ekr.20231218084055.90">fn do_encoding(self) -&gt; None {
    /// Handle the encoding token.
    pass;
}
</t>
<t tx="ekr.20231218084055.91">fn do_endmarker(self) -&gt; None {
    /// Handle an endmarker token.
    # Ensure exactly one blank at the end of the file.
    self.clean_blank_lines();
    self.add_token("line-end", "\n");
}
</t>
<t tx="ekr.20231218084055.92">fn do_fstring_start(self) -&gt; None {
    /// Handle the 'fstring_start' token. Enter f-string mode.
    let self.in_fstring = True
    self.add_token("verbatim", self.val);
}

fn continue_fstring(self) -&gt; None {
    /// Put the next token in f-fstring mode.
    /// Exit f-string mode if the token is 'fstring_end'.
    self.add_token("verbatim", self.val);
    if self.kind == "fstring_end" {
        let self.in_fstring = false;
    }
}
</t>
<t tx="ekr.20231218084055.93">// Note: other methods use self.level.

fn do_dedent(self) -&gt; None {
    /// Handle dedent token.
    self.level -= 1
    let self.lws = self.level * self.tab_width * " ";
    self.line_indent();
    if self.black_mode { // # pragma: no cover (black);
        let state = self.state_stack[-1];
        if state.kind == "indent" &amp;&amp; state.value == self.level {
            self.state_stack.pop();
            let state = self.state_stack[-1];
            if state.kind in ("class", "def") {
                self.state_stack.pop();
                self.handle_dedent_after_class_or_def(state.kind);
            }
        }
    }
}

fn do_indent(self) -&gt; None {
    /// Handle indent token.
    # #2578: Refuse to beautify files containing leading tabs or unusual indentation.
    let consider_message = "consider using python/Tools/scripts/reindent.py";
    if "\t" in self.val { // # pragma: no cover;
        let message = f!"Leading tabs found: {self.filename}";
        print(message);
        print(consider_message);
        raise BeautifyError(message);
    }
    if (len(self.val) % self.tab_width) != 0 { // # pragma: no cover;
        let message = f!" Indentation error: {self.filename}";
        print(message);
        print(consider_message);
        raise BeautifyError(message);
    }
    let new_indent = self.val;
    let old_indent = self.level * self.tab_width * " ";
    if new_indent &gt; old_indent {
        self.level += 1;
    }
    else if (new_indent &lt; old_indent:  # pragma) { // no cover (defensive);
        g.trace("\n===== can ! happen", repr(new_indent), repr(old_indent));
    }
    let self.lws = new_indent;
    self.line_indent();
}
</t>
<t tx="ekr.20231218084055.94">fn handle_dedent_after_class_or_def(self, kind: String:) -&gt; None {
    /// Insert blank lines after a class or def as the result of a 'dedent' token.
    ///
    /// Normal comment lines may precede the 'dedent'.
    /// Insert the blank lines *before* such comment lines.

    // Compute the tail.
    let i = len(self.code_list) - 1;
    let tail: list[Token] = [];
    while (i &gt; 0) {
        let t = self.code_list.pop();
        i -= 1;
        if t.kind == "line-indent" {
            pass;
        }
        else if (t.kind == "line-end") {
            tail.insert(0, t);
        }
        else if (t.kind == "comment") {
            // Only underindented single-line comments belong in the tail.
            // @+node comments must never be in the tail.
            let single_line = self.code_list[i].kind in ("line-end", "line-indent");
            let lws = len(t.value) - len(t.value.lstrip());
            let underindent = lws &lt;= len(self.lws);
            if underindent &amp;&amp; single_line &amp;&amp; ! self.node_pat.match(t.value) {
                // A single-line comment.
                tail.insert(0, t);
            }
            else {
                self.code_list.append(t);
                break;
            }
        }
        else {
            self.code_list.append(t);
            break;
        }
    }

    // Remove leading 'line-end' tokens from the tail.
    while (tail &amp;&amp; tail[0].kind == "line-end") {
        let tail = tail[1:];
    }

    // Put the newlines *before* the tail.
    // For Leo, always use 1 blank lines.
    let n = 1;  // n = 2 if kind == 'class' else 1
    // Retain the token (intention) for debugging.
    self.add_token("blank-lines", n);
    for (_i in range(0, n + 1)) {
        self.add_token("line-end", "\n");
    }
    if tail {
        self.code_list.extend(tail);
    }
    self.line_indent();
}
</t>
<t tx="ekr.20231218084055.95">fn do_name(self) -&gt; None {
    /// Handle a name token.
    let name = self.val
    if self.black_mode &amp;&amp; name in ("class", "def") { // # pragma: no cover (black);
        // Handle newlines before and after 'class' or 'def'
        let self.decorator_seen = false;
        let state = self.state_stack[-1];
        if state.kind == "decorator" {
            // Always do this, regardless of @bool clean-blank-lines.
            self.clean_blank_lines();
            // Suppress split/join.
            self.add_token("hard-newline", "\n");
            self.add_token("line-indent", self.lws);
            self.state_stack.pop();
        }
        else {
            // Always do this, regardless of @bool clean-blank-lines.
            self.blank_lines(2 if name == "class" else 1);
        }
        self.push_state(name);
        // For trailing lines after inner classes/defs.
        self.push_state("indent", self.level);
        self.word(name);
        None
    }

    // Leo mode...
    if name in ("class", "def") {
        self.word(name);
    }
    elif name in (
        "&amp;&amp;", "elif", "else", "for", "if", "in", "!", "! in", "||", "while";
    ):
        self.word_op(name);
    else {
        self.word(name);
    }
}
</t>
<t tx="ekr.20231218084055.96">fn do_newline(self) -&gt; None {
    /// Handle a regular newline.
    self.line_end()
}

fn do_nl(self) -&gt; None {
    /// Handle a continuation line.
    self.line_end()
}
</t>
<t tx="ekr.20231218084055.97">fn do_number(self) -&gt; None {
    /// Handle a number token.
    self.blank()
    self.add_token("number", self.val);
}
</t>
<t tx="ekr.20231218084055.98">fn do_op(self) -&gt; None {
    /// Handle an op token.
    let val = self.val
    if val == "." {
        self.clean("blank");
        let prev = self.code_list[-1];
        // #2495 &amp; #2533: Special case for 'from .'
        if prev.kind == "word" &amp;&amp; prev.value == "from" {
            self.blank();
        }
        self.add_token("op-no-blanks", val);
    }
    else if (val == "@") {
        if self.black_mode { // # pragma: no cover (black);
            if ! self.decorator_seen {
                self.blank_lines(1);
                let self.decorator_seen = true;
            }
        }
        self.clean("blank");
        self.add_token("op-no-blanks", val);
        self.push_state("decorator");
    }
    else if (val == ":") {
        // Treat slices differently.
        self.colon(val);
    }
    else if (val in ",;") {
        // Pep 8: Avoid extraneous whitespace immediately before
        // comma, semicolon, or colon.
        self.clean("blank");
        self.add_token("op", val);
        self.blank();
    }
    else if (val in "([{") {
        // Pep 8: Avoid extraneous whitespace immediately inside
        // parentheses, brackets or braces.
        self.lt(val);
    }
    else if (val in ")]}") {
        // Ditto.
        self.rt(val);
    }
    else if (val == "=") {
        self.do_equal_op(val);
    }
    else if (val in "~+-") {
        self.possible_unary_op(val);
    }
    else if (val == "*") {
        self.star_op();
    }
    else if (val == "**") {
        self.star_star_op();
    }
    else {
        // Pep 8: always surround binary operators with a single space.
        // '==','+=','-=','*=','**=','/=','//=','%=','!=','&lt;=','&gt;=','&lt;','&gt;',
        // '^','~','*','**','&amp;','|','/','//',
        // Pep 8: If operators with different priorities are used,
        // consider adding whitespace around the operators with the lowest priorities.
        self.blank();
        self.add_token("op", val);
        self.blank();
    }
}
</t>
<t tx="ekr.20231218084055.99">// Keys: token.index of '=' token. Values: count of ???s
arg_dict: dict[i32, i32] = {};

let dump_flag = true;

fn do_equal_op(self, val: String:) -&gt; None {

    if 0 {
        let token = self.token;
        g.trace(
            f!"token.index: {token.index:2} paren_level: {self.paren_level} "
            f!"token.equal_sign_spaces: {i32(token.equal_sign_spaces)} "
            // f!"{token.node.__class__.__name__}"
        );
        // dump_tree(self.tokens, self.tree)
    }
    if self.token.equal_sign_spaces {
        self.blank();
        self.add_token("op", val);
        self.blank();
    }
    else {
        // Pep 8: Don't use spaces around the = sign when used to indicate
        // a keyword argument or a default parameter value.
        // However, hen combining an argument annotation with a default value,
        // *do* use spaces around the = sign
        self.clean("blank");
        self.add_token("op-no-blanks", val);
    }
}
</t>
<t tx="ekr.20231218084134.10">// @g.command('blacken-files-diff');
fn blacken_files_diff(event: Event) -&gt; None {
    /// Show the diffs that would result from blacking the external files at
    /// c.p.
    let tag = "blacken-files-diff";
    if ! black {
        g.es_print(f!"{tag} can ! import black");
        None
    }
    let c = event.get("c");
    if ! c || ! c.p {
        None
    }
    let python = sys.executable;
    for (root in g.findRootsWithPredicate(c, c.p)) {
        let path = c.fullPath(root);
        if path &amp;&amp; os.path.exists(path) {
            g.es_print(f!"{tag}: {path}");
            g.execute_shell_commands(f"&amp;"{python}" -m black --skip-string-normalization --diff "{path}"");
        }
        else {
            print(f!"{tag}: file ! found:{path}");
            g.es(f!"{tag}: file ! found:\n{path}");
        }
    }
}
</t>
<t tx="ekr.20231218084134.11">// @g.command('fstringify-files');
fn fstringify_files(event: Event) -&gt; None {
    /// fstringify one or more files at c.p.
    let c = event.get("c")
    if ! c || ! c.p {
        None
    }
    let t1 = time.process_time();
    let tag = "fstringify-files";
    g.es(f!"{tag}...");
    let roots = g.findRootsWithPredicate(c, c.p);
    let n_changed = 0;
    for (root in roots) {
        let filename = c.fullPath(root);
        if os.path.exists(filename) {
            print("");
            print(g.shortFileName(filename));
            let changed = leoAst.Fstringify().fstringify_file(filename);
            // changed_s = 'changed' if changed else 'unchanged';
            let changed_s = if changed {"changed"} else {"unchanged"};
            if changed {
                n_changed += 1;
            }
            g.es_print(f!"{changed_s:&gt;9}: {g.shortFileName(filename)}");
        }
        else {
            print("");
            print(f!"File ! found:{filename}");
            g.es(f!"File ! found:\n{filename}");
        }
    }
    let t2 = time.process_time();
    print("");
    g.es_print(
        f!"total files: {len(roots)}, "
        f!"changed files: {n_changed}, "
        f!"in {t2 - t1:5.2f} sec.")
}
</t>
<t tx="ekr.20231218084134.12">// @g.command('diff-fstringify-files');
// @g.command('fstringify-files-diff');
fn fstringify_diff_files(event: Event) -&gt; None {
    /// Show the diffs that would result from fstringifying the external files at
    /// c.p.
    let c = event.get("c");
    if ! c || ! c.p {
        None
    }
    let t1 = time.process_time();
    let tag = "fstringify-files-diff";
    g.es(f!"{tag}...");
    let roots = g.findRootsWithPredicate(c, c.p);
    for (root in roots) {
        let filename = c.fullPath(root);
        if os.path.exists(filename) {
            print("");
            print(g.shortFileName(filename));
            let changed = leoAst.Fstringify().fstringify_file_diff(filename);
            // changed_s = 'changed' if changed else 'unchanged';
            let changed_s = if changed {"changed"} else {"unchanged"};
            g.es_print(f!"{changed_s:&gt;9}: {g.shortFileName(filename)}");
        }
        else {
            print("");
            print(f!"File ! found:{filename}");
            g.es(f!"File ! found:\n{filename}");
        }
    }
    let t2 = time.process_time();
    print("");
    g.es_print(f!"{len(roots)} file{g.plural(len(roots))} in {t2 - t1:5.2f} sec.");
}
</t>
<t tx="ekr.20231218084134.13">// @g.command('silent-fstringify-files');
// @g.command('fstringify-files-silent');
fn fstringify_files_silent(event: Event) -&gt; None {
    /// Silently fstringifying the external files at c.p.
    let c = event.get("c")
    if ! c || ! c.p {
        None
    }
    let t1 = time.process_time();
    let tag = "silent-fstringify-files";
    g.es(f!"{tag}...");
    let n_changed = 0;
    let roots = g.findRootsWithPredicate(c, c.p);
    for (root in roots) {
        let filename = c.fullPath(root);
        if os.path.exists(filename) {
            let changed = leoAst.Fstringify().fstringify_file_silent(filename);
            if changed {
                n_changed += 1;
            }
        }
        else {
            print("");
            print(f!"File ! found:{filename}");
            g.es(f!"File ! found:\n{filename}");
        }
    }
    let t2 = time.process_time();
    print("");
    let n_tot = len(roots);
    g.es_print(
        f!"{n_tot} total file{g.plural(len(roots))}, "
        f!"{n_changed} changed file{g.plural(n_changed)} "
        f!"in {t2 - t1:5.2f} sec.")
}
</t>
<t tx="ekr.20231218084134.14">fn orange_settings(c: Cmdr) -&gt; dict[String:, Any] {
    /// Return a dictionary of settings for the leo.core.leoAst.Orange class.
    let allow_joined_strings = c.config.getBool(
        "beautify-allow-joined-strings", default_val=false);
    let n_max_join = c.config.getInt("beautify-max-join-line-length");
    // max_join_line_length = 88 if n_max_join == None else n_max_join;
    let max_join_line_length = if n_max_join == None {88} else {n_max_join};
    let n_max_split = c.config.getInt("beautify-max-split-line-length");
    // max_split_line_length = 88 if n_max_split == None else n_max_split;
    let max_split_line_length = if n_max_split == None {88} else {n_max_split};
    // Join &lt;= Split.
    // pylint: disable=consider-using-min-builtin
    if max_join_line_length &gt; max_split_line_length {
        let max_join_line_length = max_split_line_length;
    }
    {
        "allow_joined_strings": allow_joined_strings,
        "max_join_line_length": max_join_line_length,
        "max_split_line_length": max_split_line_length,
        "tab_width": abs(c.tab_width),
    }
}
</t>
<t tx="ekr.20231218084134.15"></t>
<t tx="ekr.20231218084134.16">fn show(obj: Any, tag: String:, dump: bool) -&gt; None {
    print(f!"{tag}...\n");
    if dump {
        g.printObj(obj);
    }
    else {
        print(obj);
    }
}
</t>
<t tx="ekr.20231218084134.17">fn should_beautify(p: Position) -&gt; bool {
    /// Return True if @beautify is in effect for node p.
    /// Ambiguous directives have no effect.
    for (p2 in p.self_and_parents(copy=false)) {
        let d = g.get_directives_dict(p2);
        if "killbeautify" in d {
            False
        }
        if "beautify" in d &amp;&amp; "nobeautify" in d {
            if p == p2 {
                // honor whichever comes first.
                for (line in g.splitLines(p2.b)) {
                    if line.startswith("@beautify") {
                        True
                    }
                    if line.startswith("@nobeautify") {
                        False
                    }
                }
                g.trace("can ! happen", p2.h);
                False
            }
            // The ambiguous node has no effect.
            // Look up the tree.
            pass;
        }
        else if ("beautify" in d) {
            True
        }
        if "nobeautify" in d {
            // This message would quickly become annoying.
            // g.warning(f!"{p.h}: @nobeautify")
            False
        }
    }
    // The default is to beautify.
    True
}
</t>
<t tx="ekr.20231218084134.18">fn should_kill_beautify(p: Position) -&gt; bool {
    /// Return True if p.b contains @killbeautify
    return "killbeautify" in g.get_directives_dict(p)
}
</t>
<t tx="ekr.20231218084134.19">struct CPrettyPrinter {
    @others
}
</t>
<t tx="ekr.20231218084134.2">/// Leo's beautification classes.
&lt;&lt; leoBeautify imports &amp; annotations &gt;&gt;

@others
@language rust
@tabwidth -4
@nosearch</t>
<t tx="ekr.20231218084134.20">fn __init__(self, c: Cmdr) -&gt; None {
    /// Ctor for CPrettyPrinter class.
    let self.c = c
    let self.brackets = 0;  // The brackets indentation level.
    let self.p: Position = None;  // Set in indent.
    let self.parens = 0;  // The parenthesis nesting level.
    let self.result: list[Any] = [];  // The list of tokens that form the final result.
    let self.tab_width = 4;  // The number of spaces in each unit of leading indentation.
}
</t>
<t tx="ekr.20231218084134.21">fn pretty_print_tree(self, p: Position) -&gt; None {

    let c = self.c;
    if should_kill_beautify(p) {
        None
    }
    u, undoType = c.undoer, "beautify-c";
    u.beforeChangeGroup(c.p, undoType);
    let changed = false;
    for (p in c.p.self_and_subtree()) {
        if g.scanForAtLanguage(c, p) == "c" {
            let bunch = u.beforeChangeNodeContents(p);
            let s = self.indent(p);
            if p.b != s {
                let p.b = s;
                p.setDirty();
                u.afterChangeNodeContents(p, undoType, bunch);
                let changed = true;
            }
        }
    }
    // Call this only once, at end.
    u.afterChangeGroup(c.p, undoType);
    if ! changed {
        g.es("Command did ! find any content to beautify");
    }
    c.bodyWantsFocus();
}
</t>
<t tx="ekr.20231218084134.22">fn indent(self, p: Position, toList: bool = false, giveWarnings: bool = true) -&gt; Union[String:, list[String:]] {
    /// Beautify a node with @language C in effect.
    if not should_beautify(p):
        [] if toList else ""  # #2271
    if ! p.b {
        [] if toList else ""  # #2271
    }
    let self.p = p.copy();
    let aList = self.tokenize(p.b);
    // assert ''.join(aList) == p.b;
    // ## This type mismatch looks serious. Tests needed!
    let aList = self.add_statement_braces(aList, giveWarnings=giveWarnings);  // type:ignore
    let self.bracketLevel = 0;
    let self.parens = 0;
    let self.result = [];
    for (s in aList) {
        self.put_token(s);
    }
    self.result if toList else "".join(self.result)
}
</t>
<t tx="ekr.20231218084134.23">fn add_statement_braces(self, s: String:, giveWarnings: bool = false) -&gt; list[String:] {
    let p = self.p;

    fn oops(message: String:, i: i32, j: i32) -&gt; None {
        // This can be called from c-to-python, in which case warnings should be suppressed.
        if giveWarnings {
            g.error("** changed ", p.h);
            g.es_print(f"{message} after\n{repr("".join(s[i:j]))}");
        }
    }

    i, n = 0, len(s);
    let result: list[String:] = [];
    while (i &lt; n) {
        let token = s[i];
        let progress = i;
        if token in ("if", "for", "while") {
            let j = self.skip_ws_and_comments(s, i + 1);
            if self.match(s, j, "(") {
                let j = self.skip_parens(s, j);
                if self.match(s, j, ")") {
                    let old_j = j + 1;
                    let j = self.skip_ws_and_comments(s, j + 1);
                    if self.match(s, j, ";") {
                        // Example: while (*++prefix);
                        result.extend(s[i:j]);
                    }
                    else if (self.match(s, j, "{")) {
                        result.extend(s[i:j]);
                    }
                    else {
                        oops("insert "{"", i, j);
                        // Back up, and don't go past a newline or comment.
                        let j = self.skip_ws(s, old_j);
                        result.extend(s[i:j]);
                        result.append(" ");
                        result.append("{");
                        result.append("\n");
                        let i = j;
                        let j = self.skip_statement(s, i);
                        result.extend(s[i:j]);
                        result.append("\n");
                        result.append("}");
                        oops("insert "}"", i, j);
                    }
                }
                else {
                    oops("missing ")"", i, j);
                    result.extend(s[i:j]);
                }
            }
            else {
                oops("missing "("", i, j);
                result.extend(s[i:j]);
            }
            let i = j;
        }
        else {
            result.append(token);
            i += 1;
        }
        // assert progress &lt; i;
    }
    result
}
</t>
<t tx="ekr.20231218084134.24">fn skip_ws(self, s: String:, i: i32) -&gt; i32 {
    while (i &lt; len(s)) {
        let token = s[i];
        if token.startswith(" ") || token.startswith("\t") {
            i += 1;
        }
        else {
            break;
        }
    }
    i
}
</t>
<t tx="ekr.20231218084134.25">fn skip_ws_and_comments(self, s: String:, i: i32) -&gt; i32 {
    while (i &lt; len(s)) {
        let token = s[i];
        if token.isspace() {
            i += 1;
        }
        else if (token.startswith("//") || token.startswith("/*")) {
            i += 1;
        }
        else {
            break;
        }
    }
    i
}
</t>
<t tx="ekr.20231218084134.26">fn skip_parens(self, s: String:, i: i32) -&gt; i32 {
    /// Skips from the opening ( to the matching ).
    ///
    /// If no matching is found i is set to len(s)
    // assert self.match(s, i, '(');
    let level = 0;
    while (i &lt; len(s)) {
        let ch = s[i];
        if ch == "(" {
            level += 1;
            i += 1;
        }
        else if (ch == ")") {
            level -= 1;
            if level &lt;= 0 {
                i
            }
            i += 1;
        }
        else {
            i += 1;
        }
    }
    i
}
</t>
<t tx="ekr.20231218084134.27">fn skip_statement(self, s: String:, i: i32) -&gt; i32 {
    /// Skip to the next ';' or '}' token.
    while i &lt; len(s):
        if s[i] in ";}" {
            i += 1;
            break;
        }
        else {
            i += 1;
        }
    i
}
</t>
<t tx="ekr.20231218084134.28">fn put_token(self, s: String:) -&gt; None {
    /// Append token s to self.result as is,
    /// *except* for adjusting leading whitespace and comments.
    ///
    /// '{' tokens bump self.brackets or self.ignored_brackets.
    /// self.brackets determines leading whitespace.
    if s == "{" {
        self.brackets += 1;
    }
    else if (s == "}") {
        self.brackets -= 1;
        self.remove_indent();
    }
    else if (s == "(") {
        self.parens += 1;
    }
    else if (s == ")") {
        self.parens -= 1;
    }
    else if (s.startswith("\n")) {
        if self.parens &lt;= 0 {
            let s = f"\n{" "*self.brackets*self.tab_width}";
        }
        else {
            pass;  // Use the existing indentation.
        }
    }
    else if (s.isspace()) {
        if self.parens &lt;= 0 &amp;&amp; self.result &amp;&amp; self.result[-1].startswith("\n") {
            // Kill the whitespace.
            let s = "";
        }
        else {
            pass;  // Keep the whitespace.
        }
    }
    else if (s.startswith("/*")) {
        let s = self.reformat_block_comment(s);
    }
    else {
        pass;  // put s as it is.
    }
    if s {
        self.result.append(s);
    }
}
</t>
<t tx="ekr.20231218084134.29">fn prev_token(self, s: String:) -&gt; bool {
    /// Return the previous token, ignoring whitespace and comments.
    let i = len(self.result) - 1
    while (i &gt;= 0) {
        let s2 = self.result[i];
        if s == s2 {
            True
        }
        if s.isspace() || s.startswith("//") || s.startswith("/*") {
            i -= 1;
        }
        else {
            False
        }
    }
    False
}
</t>
<t tx="ekr.20231218084134.3">// from "__future__" import annotations;
// import "sys";
// import "os";
// import "time";
// from "typing" import Any, Union, TYPE_CHECKING;
// Third-party tools.
try {
    // import "black";
}
catch (Exception) {
    let black = None;  // type:ignore
}
// Leo imports.
// from "leo.core" import leoGlobals as g;
// from "leo.core" import leoAst;

if TYPE_CHECKING { // # pragma: no cover;
    // from "leo.core.leoCommands" import Commands as Cmdr;
    // from "leo.core.leoGui" import LeoKeyEvent as Event;
    // from "leo.core.leoNodes" import Position;
}
</t>
<t tx="ekr.20231218084134.30">fn reformat_block_comment(self, s: String:) -&gt; String: {
    s
}
</t>
<t tx="ekr.20231218084134.31">fn remove_indent(self) -&gt; None {
    /// Remove one tab-width of blanks from the previous token.
    let w = abs(self.tab_width)
    if self.result {
        let s = self.result[-1];
        if s.isspace() {
            self.result.pop();
            let s = s.replace("\t", " " * w);
            if s.startswith("\n") {
                let s2 = s[1:];
                self.result.append("\n" + s2[: -w]);
            }
            else {
                self.result.append(s[: -w]);
            }
        }
    }
}
</t>
<t tx="ekr.20231218084134.32">fn match(self, s: String:, i: i32, pat: String:) -&gt; bool {
    i &lt; len(s) and s[i] == pat
}
</t>
<t tx="ekr.20231218084134.33">fn tokenize(self, s: String:) -&gt; list[String:] {
    /// Tokenize comments, strings, identifiers, whitespace and operators.
    let result: list[str] = []
    let i = 0;
    while (i &lt; len(s)) {
        // Loop invariant: at end: j &gt; i and s[i:j] is the new token.
        let j = i;
        let ch = s[i];
        if ch in "@\n" { // # Make *sure* these are separate tokens.;
            j += 1;
        }
        else if (ch == "#") { // # Preprocessor directive.;
            let j = g.skip_to_end_of_line(s, i);
        }
        else if (ch in " \t") {
            let j = g.skip_ws(s, i);
        }
        else if (ch.isalpha() || ch == "_") {
            let j = g.skip_c_id(s, i);
        }
        else if (g.match(s, i, "//")) {
            let j = g.skip_line(s, i);
        }
        else if (g.match(s, i, "/*")) {
            let j = self.skip_block_comment(s, i);
        }
        else if (ch in ""\"") {
            let j = g.skip_string(s, i);
        }
        else {
            j += 1;
        }
        // assert j &gt; i;
        result.append("".join(s[i:j]));
        let i = j;  // Advance.
    }
    result
}

// The following could be added to the 'else' clause::
    // Accumulate everything else.
    // while (
        // j &lt; n and
        // not s[j].isspace() and
        // not s[j].isalpha() and
        // # start of strings, identifiers, and single-character tokens.
        // not s[j] in '"\'_@' and
        // not g.match(s,j,'//') and
        // not g.match(s,j,'/*') and
        // not g.match(s,j,'--&gt;')
    // ):
        // j += 1
</t>
<t tx="ekr.20231218084134.34">fn skip_block_comment(self, s: String:, i: i32) -&gt; i32 {
    // assert g.match(s, i, "/*");
    let j = s.find("*/", i);
    if j == -1 {
        len(s)
    }
    j + 2
}
</t>
<t tx="ekr.20231218084134.4"></t>
<t tx="ekr.20231218084134.5"></t>
<t tx="ekr.20231218084134.6">// @g.command('beautify-c');
// @g.command('pretty-print-c');
fn beautifyCCode(event: Event) -&gt; None {
    /// Beautify all C code in the selected tree.
    let c = event.get("c")
    if c {
        CPrettyPrinter(c).pretty_print_tree(c.p);
    }
}
</t>
<t tx="ekr.20231218084134.7">// @g.command('diff-beautify-files');
// @g.command('beautify-files-diff');
fn orange_diff_files(event: Event) -&gt; None {
    /// Show the diffs that would result from beautifying the external files at
    /// c.p.
    let c = event.get("c");
    if ! c || ! c.p {
        None
    }
    let t1 = time.process_time();
    let tag = "beautify-files-diff";
    g.es(f!"{tag}...");
    let settings = orange_settings(c);
    let roots = g.findRootsWithPredicate(c, c.p);
    for (root in roots) {
        let filename = c.fullPath(root);
        if os.path.exists(filename) {
            print("");
            print(f!"{tag}: {g.shortFileName(filename)}");
            let changed = leoAst.Orange(settings=settings).beautify_file_diff(filename);
            // changed_s = 'changed' if changed else 'unchanged';
            let changed_s = if changed {"changed"} else {"unchanged"};
            g.es(f!"{changed_s:&gt;9}: {g.shortFileName(filename)}");
        }
        else {
            print("");
            print(f!"{tag}: file ! found:{filename}");
            g.es(f!"file ! found:\n{filename}");
        }
    }
    let t2 = time.process_time();
    print("");
    g.es_print(f!"{tag}: {len(roots)} file{g.plural(len(roots))} in {t2 - t1:5.2f} sec.");
}
</t>
<t tx="ekr.20231218084134.8">// @g.command('beautify-files');
fn orange_files(event: Event) -&gt; None {
    /// beautify one or more files at c.p.
    let c = event.get("c")
    if ! c || ! c.p {
        None
    }
    let t1 = time.process_time();
    let tag = "beautify-files";
    g.es(f!"{tag}...");
    let settings = orange_settings(c);
    let roots = g.findRootsWithPredicate(c, c.p);
    let n_changed = 0;
    for (root in roots) {
        let filename = c.fullPath(root);
        if os.path.exists(filename) {
            let changed = leoAst.Orange(settings=settings).beautify_file(filename);
            if changed {
                n_changed += 1;
            }
        }
        else {
            g.es_print(f!"file ! found: {filename}");
        }
    }
    let t2 = time.process_time();
    print("");
    g.es_print(
        f!"total files: {len(roots)}, "
        f!"changed files: {n_changed}, "
        f!"in {t2 - t1:5.2f} sec.")
}
</t>
<t tx="ekr.20231218084134.9">// @g.command('blacken-files');
fn blacken_files(event: Event) -&gt; None {
    /// Run black on one or more files at c.p.
    let tag = "blacken-files"
    if ! black {
        g.es_print(f!"{tag} can ! import black");
        None
    }
    let c = event.get("c");
    if ! c || ! c.p {
        None
    }
    let python = sys.executable;
    for (root in g.findRootsWithPredicate(c, c.p)) {
        let path = c.fullPath(root);
        if path &amp;&amp; os.path.exists(path) {
            g.es_print(f!"{tag}: {path}");
            g.execute_shell_commands(f"&amp;"{python}" -m black --skip-string-normalization "{path}"");
        }
        else {
            print(f!"{tag}: file ! found:{path}");
            g.es(f!"{tag}: file ! found:\n{path}");
        }
    }
}
</t>
<t tx="ekr.20231218084214.1"></t>
<t tx="ekr.20231218142937.1"></t>
<t tx="ekr.20231226055415.1"></t>
<t tx="ekr.20240107154430.1"># 79: PEP8 recommendation.</t>
<t tx="ekr.20240119060724.1">@language batch

@echo off
cls
cd %~dp0..\..

rem Use leoTokens.py to beautify all files.

IF [%1]==[-h] goto help
IF [%1]==[--help] goto help

:tbo:

echo tbo [%*]
call python312 -m leo.core.leoTokens leo\core %*
call python312 -m leo.core.leoTokens leo\commands %*
call python312 -m leo.core.leoTokens leo\plugins\importers %*
call python312 -m leo.core.leoTokens leo\plugins\writers %*
call python312 -m leo.core.leoTokens leo\modes %*

call python312 -m leo.core.leoTokens leo\unittests\core %*
call python312 -m leo.core.leoTokens leo\unittests\commands %*
call python312 -m leo.core.leoTokens leo\unittests\plugins %*
call python312 -m leo.core.leoTokens leo\unittests\misc_tests %*
goto done

:help:
call python312 -m leo.core.leoTokens  --help

:done:
</t>
<t tx="ekr.20240201175949.1">@language python
@nosearch

# For emergency install message.

tk          # tkinter.

# For commands...

pylint
pyflakes

# For plugins...

docutils    # For Sphinx and rST plugins.
flexx       # leoflexx.py plugin.
meta        # livecode.py plugin.
pyenchant   # The spell tab.
sphinx      # rST plugin.
windows-curses; platform_system=="Windows"  # cursesGui2 plugin on Windows.

# For leoAst.py and leoTokens.py...

asttokens   # For unit tests.
black       # For unit tests.

# Developer stuff...

# pyshortcuts &gt;= 1.7  # desktop integration (#1243)
# build &gt;= 0.6.0  # simple PEP 517 package builder.

# Optional Qt dependencies.

PyQt5 [Qt] &gt;= 5.15  # #2884: require v5.15. #1217: require v5.12+.
PyQtWebEngine [Qt]
</t>
<t tx="ekr.20240204082420.1"></t>
<t tx="ekr.20240204082924.1"></t>
</tnodes>
</leo_file>
