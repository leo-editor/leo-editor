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
<v t="ekr.20260526171943.1"><vh>@bool minibuffer-find-mode = True</vh></v>
<v t="ekr.20220904210247.1"><vh>@@@enabled-plugins</vh></v>
<v t="ekr.20251214042454.1"><vh>@bool body-pane-wraps = False</vh></v>
<v t="ekr.20140902155015.18674"><vh>@bool qt-use-scintilla = False</vh></v>
<v t="ekr.20250715195948.1"><vh>@bool report-changed-at-clean-nodes = False</vh></v>
<v t="ekr.20221129012213.1"><vh>@bool run-flake8-on-write = False</vh></v>
<v t="ekr.20210530065000.2"><vh>@data exec-script-commands</vh></v>
<v t="ekr.20210530065000.3"><vh>@data exec-script-patterns</vh></v>
<v t="ekr.20150425145248.1"><vh>@data history-list</vh></v>
<v t="ekr.20240107154430.1"><vh>@int max-find-long-lines-length = 100</vh></v>
<v t="ekr.20140916101314.19538"><vh>@string target_language = python</vh></v>
<v t="ekr.20260111055821.1"><vh>Beautifying files</vh>
<v t="ekr.20260111055821.2"><vh>@bool beautify-python-code-on-write = True</vh></v>
<v t="ekr.20260111055821.4"><vh>@int black-line-length = 100</vh></v>
<v t="ekr.20260111055821.5"><vh>@string black-toml = None</vh></v>
</v>
<v t="ekr.20160122104332.1"><vh>Buttons &amp; commands</vh>
<v t="ekr.20260113153148.1"><vh>@@@button test bed</vh>
<v t="ekr.20260114092617.1"><vh>&lt;&lt; define test_s &gt;&gt;</vh></v>
</v>
<v t="ekr.20150502050609.1"><vh>@button backup</vh></v>
<v t="ekr.20170811173924.1"><vh>@button backup-repo</vh></v>
<v t="ekr.20231107062256.1"><vh>@button check-leoPy.leo</vh></v>
<v t="ekr.20230508145335.1"><vh>@command slow-tests</vh></v>
<v t="ekr.20240714075119.1"><vh>@command sync-reqs</vh></v>
<v t="ekr.20220306092217.1"><vh>@command test-one</vh>
<v t="ekr.20240608035218.1"><vh>&lt;&lt; test-one: test kind &gt;&gt;</vh></v>
<v t="ekr.20240528034319.1"><vh>&lt;&lt; test the beautifier &gt;&gt;</vh></v>
<v t="ekr.20240417150035.1"><vh>&lt;&lt; old commands &gt;&gt;</vh></v>
<v t="ekr.20230511074046.1"><vh>&lt;&lt; prefixes &gt;&gt;</vh></v>
</v>
</v>
</v>
<v t="ekr.20170427114412.1"><vh>scripts</vh>
<v t="ekr.20170428084123.1"><vh>Recursive import script</vh></v>
<v t="ekr.20260503063616.1"><vh>--- diff scripts</vh>
<v t="ekr.20260508180923.1"><vh>script: diff 6.8.8/devel </vh></v>
<v t="ekr.20260503063747.1"><vh>script: diff master/6.8.9</vh></v>
<v t="ekr.20260503052547.1"><vh>script: diff master/devel</vh></v>
<v t="ekr.20190402091335.1"><vh>script: diff-branches/revs (master, 6.8.8, leo/core)</vh></v>
<v t="ekr.20180816105258.1"><vh>script: diff-branches/revs (one file)</vh></v>
<v t="ekr.20201208114843.1"><vh>script: diff-pr</vh></v>
<v t="ekr.20220319145807.1"><vh>script: diff-two-revs-wo-comments</vh>
<v t="ekr.20220319151900.1"><vh>function: make_diff_outlines_ignoring_comments</vh></v>
<v t="ekr.20220319152417.1"><vh>function: strip_comments</vh></v>
</v>
<v t="ekr.20260116001413.1"><vh>script: summary-diff (master, 6.8.8, leo/commands)</vh></v>
<v t="ekr.20260112121427.1"><vh>script: summary-diff (master, 6.8.8, leo/core)</vh></v>
</v>
<v t="ekr.20260503063649.1"><vh>--- other scripts</vh>
<v t="ekr.20240403111007.1"><vh>script: add toolbar buttons</vh></v>
<v t="ekr.20201222095250.1"><vh>script: check for duplicate settings in theme files</vh></v>
<v t="ekr.20200308193719.1"><vh>script: check gnx's</vh></v>
<v t="ekr.20210429045101.1"><vh>script: check gnxDict</vh></v>
<v t="ekr.20260112054444.1"><vh>script: clean diffs</vh></v>
<v t="ekr.20210118013157.1"><vh>script: convert-LeoFind</vh>
<v t="ekr.20210118024739.1"><vh>convert</vh></v>
<v t="ekr.20210118013807.1"><vh>main</vh></v>
<v t="ekr.20210118020530.1"><vh>new_name</vh></v>
<v t="ekr.20210118021337.1"><vh>exists</vh></v>
</v>
<v t="ekr.20240707233742.1"><vh>script: cvt-ast-names</vh>
<v t="ekr.20240708062242.1"><vh>&lt;&lt; define table &gt;&gt;</vh></v>
<v t="ekr.20240708072327.1"><vh>&lt;&lt; check table &gt;&gt;</vh></v>
</v>
<v t="ekr.20210829132319.1"><vh>script: cvt-tests</vh></v>
<v t="ekr.20240403090451.1"><vh>script: expand-toolbar</vh></v>
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
</v>
<v t="EKR.20040430162943"><vh>The attic</vh>
<v t="ekr.20170302123956.1"><vh>@file ../doc/leoAttic.txt</vh></v>
</v>
<v t="ekr.20031218072017.2406"><vh>Code</vh>
<v t="ekr.20140902032918.18591"><vh>About this file</vh>
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
<v t="ekr.20070317085508.1"><vh>@file leoChapters.py</vh></v>
<v t="ekr.20100208065621.5894"><vh>@file leoCache.py</vh></v>
<v t="ekr.20031218072017.2794"><vh>@file leoColor.py</vh></v>
<v t="ekr.20140827092102.18574"><vh>@file leoColorizer.py</vh></v>
<v t="vv.20260806220000.1"><vh>@file leoTreeSitter.py</vh></v>
<v t="ekr.20031218072017.2810"><vh>@file leoCommands.py</vh></v>
<v t="ekr.20180212072657.2"><vh>@file leoCompare.py</vh></v>
<v t="ekr.20130925160837.11429"><vh>@file leoConfig.py</vh></v>
<v t="ekr.20130302121602.10208"><vh>@file leoDebugger.py</vh></v>
<v t="ekr.20160306114544.1"><vh>@file leoExternalFiles.py</vh></v>
<v t="ekr.20031218072017.3018"><vh>@file leoFileCommands.py</vh></v>
<v t="ekr.20031218072017.3093"><vh>@file leoGlobals.py</vh></v>
<v t="ekr.20150514154159.1"><vh>@file leoHistory.py</vh></v>
<v t="ekr.20031218072017.3206"><vh>@file leoImport.py</vh></v>
<v t="ekr.20241022090855.1"><vh>@file leoJupytext.py</vh></v>
<v t="ekr.20190515070742.1"><vh>@file leoMarkup.py</vh></v>
<v t="ekr.20031218072017.3320"><vh>@file leoNodes.py</vh></v>
<v t="ekr.20140821055201.18331"><vh>@file leoPersistence.py</vh></v>
<v t="ekr.20031218072017.3439"><vh>@file leoPlugins.py</vh></v>
<v t="ekr.20150419124739.1"><vh>@file leoPrinting.py</vh></v>
<v t="ekr.20061024060248.1"><vh>@file leoPymacs.py</vh></v>
<v t="ekr.20140810053602.18074"><vh>@file leoQt.py</vh></v>
<v t="ekr.20140526082700.18440"><vh>@file leoRope.py</vh></v>
<v t="ekr.20090502071837.3"><vh>@file leoRst.py</vh></v>
<v t="ekr.20120420054855.14241"><vh>@file leoSessions.py</vh></v>
<v t="ekr.20080708094444.1"><vh>@file leoShadow.py</vh></v>
<v t="ekr.20180121041003.1"><vh>@file leoTips.py</vh></v>
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
<v t="ekr.20250329033400.1"><vh>@file leoAPI.py</vh></v>
<v t="ekr.20060123151617"><vh>@file leoFind.py</vh></v>
<v t="ekr.20031218072017.3655"><vh>@file leoFrame.py</vh></v>
<v t="ekr.20031218072017.3719"><vh>@file leoGui.py</vh></v>
<v t="ekr.20061031131434"><vh>@file leoKeys.py</vh></v>
<v t="ekr.20031218072017.3749"><vh>@file leoMenu.py</vh></v>
</v>
<v t="ekr.20180225010644.1"><vh>Other files</vh>
<v t="ekr.20180225010707.1"><vh>In leo-editor directory</vh>
<v t="ekr.20240317061516.1"><vh>@clean ../../MANIFEST.in</vh></v>
<v t="ekr.20220222130955.1"><vh>@edit ../../.mypy.ini</vh></v>
<v t="ekr.20231108150521.1"><vh>@edit ../../CONTRIBUTING.md</vh></v>
<v t="ekr.20210302164046.1"><vh>@edit ../../launchLeo.py</vh></v>
<v t="ekr.20240319094534.1"><vh>@edit ../../PKG-INFO.TXT</vh></v>
<v t="ekr.20240206153029.1"><vh>@edit ../../README.md</vh></v>
<v t="ekr.20240206161713.1"><vh>@clean ../../setup.cfg </vh></v>
<v t="ekr.20150304125314.4"><vh>@file ../../leo_to_html.xsl</vh></v>
<v t="ekr.20240227064614.1"><vh>@file ../../pyproject.toml</vh></v>
<v t="ekr.20240406013108.1"><vh>@file ../../ruff.toml</vh></v>
<v t="ekr.20240201175949.1"><vh>@file ../../requirements.txt</vh></v>
<v t="axk.20260702120000.1"><vh>@file ../../make_macos_application.py</vh></v>
<v t="ekr.20181014073705.1"><vh>@file ../../run_pytest_tests.py</vh></v>
<v t="ekr.20181009072707.1"><vh>@file ../../run_travis_unit_tests.py</vh></v>
<v t="ekr.20150304130753.4"><vh>leo-viewer/leo_to_html.xsl</vh></v>
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
</v>
</v>
<v t="ekr.20180225010850.1"><vh>In leo/modes</vh>
<v t="ekr.20250330145834.1"><vh>@edit ../modes/tex.py</vh></v>
<v t="ekr.20221129095254.1"><vh>@file ../modes/batch.py</vh></v>
<v t="ekr.20250330150257.1"><vh>@file ../modes/c.py</vh></v>
<v t="ekr.20250121105007.1"><vh>@file ../modes/cweb.py</vh></v>
<v t="ekr.20250110042632.1"><vh>@file ../modes/doxygen.py</vh></v>
<v t="ekr.20150326145530.1"><vh>@file ../modes/forth.py</vh></v>
<v t="ekr.20230419050031.1"><vh>@file ../modes/html.py</vh></v>
<v t="ekr.20240227082119.1"><vh>@file ../modes/ini.py</vh></v>
<v t="ekr.20230419052236.1"><vh>@file ../modes/javascript.py</vh></v>
<v t="ekr.20210223151922.1"><vh>@file ../modes/julia.py</vh></v>
<v t="ekr.20241030151621.1"><vh>@file ../modes/jupytext.py</vh></v>
<v t="ekr.20241030152835.1"><vh>@file ../modes/md.py</vh></v>
<v t="ekr.20240202211600.1"><vh>@file ../modes/nim.py</vh></v>
<v t="ekr.20210219115553.109"><vh>@file ../modes/python.py</vh></v>
<v t="swot.20260501212006.1"><vh>@file ../modes/pug.py</vh></v>
<v t="ekr.20231103124615.1"><vh>@file ../modes/rust.py</vh></v>
<v t="ekr.20231012163843.1"><vh>@file ../modes/scheme.py</vh></v>
</v>
<v t="ekr.20221204070905.1"><vh>In leo/scripts</vh>
<v t="ekr.20240321122705.1"><vh>--- build scripts</vh>
<v t="mhw.20190808083008.1"><vh>@file ../scripts/add-desktop-links.leox</vh></v>
<v t="ekr.20240321122822.1"><vh>@file ../scripts/build_leo.py</vh></v>
<v t="ekr.20240321122917.1"><vh>@file ../scripts/inspect_wheel.py</vh></v>
<v t="ekr.20240321123226.1"><vh>@file ../scripts/install_leo_from_pypi.py</vh></v>
<v t="ekr.20240321123225.3"><vh>@file ../scripts/install_leo_from_testpypi.py</vh></v>
<v t="ekr.20240321123214.1"><vh>@file ../scripts/install_leo_locally.py</vh></v>
<v t="ekr.20240322173704.1"><vh>@file ../scripts/pip_install_r.py</vh></v>
<v t="ekr.20240322173731.1"><vh>@file ../scripts/pip_uninstall_all.py</vh></v>
<v t="ekr.20240321123224.1"><vh>@file ../scripts/run_installed_leo.py</vh></v>
<v t="ekr.20240321123225.1"><vh>@file ../scripts/uninstall_leo.py</vh></v>
<v t="ekr.20260414092941.1"><vh>@file ../scripts/update_leo_tools.py</vh></v>
<v t="ekr.20240321123225.4"><vh>@file ../scripts/upload_leo_to_pypi.py</vh></v>
<v t="ekr.20240321123225.2"><vh>@file ../scripts/upload_leo_to_testpypi.py</vh></v>
</v>
<v t="ekr.20240321122614.1"><vh>--- test scripts</vh>
<v t="ekr.20240323050520.1"><vh>@file ../scripts/beautify_all_leo.py</vh></v>
<v t="ekr.20251129060454.1"><vh>@file ../scripts/check_leo.py</vh></v>
<v t="ekr.20240322084902.1"><vh>@file ../scripts/flake8_leo.py</vh></v>
<v t="ekr.20240323051724.1"><vh>@file ../scripts/full_test_leo.py</vh></v>
<v t="ekr.20240321122413.8"><vh>@file ../scripts/mypy_leo.py</vh></v>
<v t="ekr.20250227032644.1"><vh>@file ../scripts/pyflakes_leo.py</vh></v>
<v t="ekr.20240321122413.9"><vh>@file ../scripts/pylint_leo.py</vh></v>
<v t="ekr.20240406061929.1"><vh>@file ../scripts/ruff_leo.py</vh></v>
<v t="ekr.20240322162616.1"><vh>@file ../scripts/run_test_leo.py</vh></v>
</v>
</v>
</v>
<v t="ekr.20110605121601.17862"><vh>Qt gui</vh>
<v t="ekr.20161223152017.1"><vh>@edit ../plugins/qt_quicksearch.py</vh></v>
<v t="ekr.20161223152353.1"><vh>@edit ../plugins/qt_quicksearch_sub.py</vh></v>
<v t="ekr.20120419093256.10048"><vh>@file ../plugins/free_layout.py</vh></v>
<v t="ekr.20110605121601.17954"><vh>@file ../plugins/nested_splitter.py</vh></v>
<v t="ekr.20221019064053.1"><vh>@file ../plugins/pane_commands.py</vh></v>
<v t="ekr.20110605121601.17996"><vh>@file ../plugins/qt_commands.py</vh></v>
<v t="ekr.20140907103315.18766"><vh>@file ../plugins/qt_events.py</vh></v>
<v t="ekr.20140907123524.18774"><vh>@file ../plugins/qt_frame.py</vh></v>
<v t="ekr.20140907085654.18699"><vh>@file ../plugins/qt_gui.py</vh></v>
<v t="ekr.20140907103315.18777"><vh>@file ../plugins/qt_idle_time.py</vh></v>
<v t="tom.20240923194438.1"><vh>@file ../plugins/qt_layout.py</vh></v>
<v t="ekr.20140907123524.18777"><vh>@file ../plugins/qt_quickheadlines.py</vh></v>
<v t="ekr.20140831085423.18598"><vh>@file ../plugins/qt_text.py</vh></v>
<v t="ekr.20140907131341.18707"><vh>@file ../plugins/qt_tree.py</vh></v>
<v t="ekr.20110605121601.18002"><vh>@file ../plugins/qtGui.py</vh></v>
<v t="ekr.20171031111403.1"><vh>Leo Edit Pane</vh>
<v t="tbrown.20171028115144.8"><vh>@file ../plugins/editpane/__init__.py</vh></v>
<v t="tbrown.20171029210211.1"><vh>@file ../plugins/editpane/clicky_splitter.py</vh></v>
<v t="ekr.20211210102459.1"><vh>@file ../plugins/editpane/csvedit.py</vh></v>
<v t="tbrown.20171028115144.6"><vh>@file ../plugins/editpane/editpane.py</vh></v>
<v t="tbrown.20171028115144.5"><vh>@file ../plugins/editpane/leotextedit.py</vh></v>
<v t="tbrown.20171028115144.4"><vh>@file ../plugins/editpane/markdownview.py</vh></v>
<v t="tbrown.20171028115144.2"><vh>@file ../plugins/editpane/plaintextedit.py</vh></v>
<v t="tbrown.20171028115144.1"><vh>@file ../plugins/editpane/plaintextview.py</vh></v>
<v t="tbrown.20171028115143.3"><vh>@file ../plugins/editpane/vanillascintilla.py</vh></v>
<v t="tbrown.20171028115541.1"><vh>@file signal_manager.py</vh></v>
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
<v t="tbrown.20130813134319.11942"><vh>@file ../plugins/richtext.py</vh></v>
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
<v t="EKR.20040517075715.20"><vh>@edit ../plugins/word_export.ini</vh></v>
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
<v t="ekr.20250501.100"><vh>@file ../plugins/importers/pug.py</vh></v>
<v t="ekr.20211209153303.1"><vh>@file ../plugins/importers/python.py</vh></v>
<v t="vv.20260807090000.1"><vh>@file ../plugins/importers/python_ts.py</vh></v>
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
<v t="danr7.20060902215215.1"><vh>@file ../plugins/leo_to_html.py</vh></v>
<v t="tbrown.20130930160706.23451"><vh>@file ../plugins/markup_inline.py</vh></v>
<v t="vitalije.20180804172140.1"><vh>@file ../plugins/md_docer.py</vh></v>
<v t="peckj.20140113150237.7083"><vh>@file ../plugins/nodediff.py</vh></v>
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
<v t="ekr.20090622063842.5264"><vh>@file ../plugins/projectwizard.py</vh></v>
<v t="ekr.20160928073518.1"><vh>@file ../plugins/pyplot_backend.py</vh></v>
<v t="ville.20090314215508.4"><vh>@file ../plugins/quicksearch.py</vh></v>
<v t="tbrown.20130420091241.44181"><vh>@file ../plugins/screen_capture.py</vh></v>
<v t="ville.20090815203828.5235"><vh>@file ../plugins/spydershell.py</vh></v>
<v t="ekr.20100103093121.5329"><vh>@file ../plugins/stickynotes.py</vh></v>
<v t="tbrown.20090119215428.2"><vh>leo/plugins/todo.py</vh>
<v t="tbrown.20090119215428.3"><vh>&lt;&lt; todo docstring &gt;&gt;</vh></v>
<v t="tbrown.20090119215428.4"><vh>&lt;&lt; todo imports &amp; annotations &gt;&gt;</vh></v>
<v t="tbrown.20090119215428.6"><vh>init (todo.py)</vh></v>
<v t="tbrown.20090119215428.7"><vh>onCreate (todo.py)</vh></v>
<v t="tbrown.20090630144958.5318"><vh>popup_entry (todo.py)</vh></v>
<v t="tbrown.20090119215428.8"><vh>class todoQtUI(QWidget)</vh>
<v t="ekr.20111118104929.10204"><vh>ctor (todoQtUI(QWidget))</vh></v>
<v t="ekr.20111118104929.10203"><vh>make_func</vh></v>
<v t="ekr.20111118104929.10205"><vh>populateMenu</vh></v>
<v t="ekr.20111118104929.10207"><vh>setProgress</vh></v>
<v t="ekr.20111118104929.10208"><vh>setTime</vh></v>
</v>
<v t="tbrown.20090119215428.9"><vh>class todoController</vh>
<v t="tbrown.20090119215428.10"><vh>&lt;&lt; todoController data &gt;&gt;</vh></v>
<v t="tbrown.20090119215428.11"><vh>todoController.__init__ &amp; helpers</vh>
<v t="tbrown.20090119215428.12"><vh>todoController.reloadSettings</vh></v>
<v t="ekr.20201111052557.1"><vh>todoController.todo_c.patch_1591</vh></v>
</v>
<v t="tbnorth.20170925093004.1"><vh>todoController._date &amp; _time</vh></v>
<v t="tbrown.20090630144958.5319"><vh>todoController.addPopupMenu</vh></v>
<v t="tbrown.20090630144958.5320"><vh>todoController.menuicon</vh></v>
<v t="tbrown.20090119215428.13"><vh>todoController.redrawer</vh></v>
<v t="tbrown.20090119215428.14"><vh>todoController.projectChanger</vh></v>
<v t="tbrown.20090119215428.15"><vh>todoController.loadAllIcons</vh></v>
<v t="tbrown.20090119215428.16"><vh>todoController.loadIcons</vh></v>
<v t="tbrown.20090119215428.17"><vh>todoController.close</vh></v>
<v t="tbrown.20090119215428.18"><vh>todoController.showHelp</vh></v>
<v t="tbrown.20090119215428.19"><vh>todoController:attributes...</vh>
<v t="tbrown.20090119215428.20"><vh>todoController.delUD</vh></v>
<v t="tbrown.20090119215428.21"><vh>todoController.hasUD</vh></v>
<v t="tbrown.20090119215428.22"><vh>todoController.getat</vh></v>
<v t="tbrown.20090119215428.23"><vh>todoController.testDefault</vh></v>
<v t="tbrown.20090119215428.24"><vh>todoController.setat</vh></v>
<v t="tbrown.20090119215428.25"><vh>todoController.dropEmpty</vh></v>
</v>
<v t="tbrown.20090119215428.27"><vh>todoController:drawing...</vh>
<v t="tbrown.20090119215428.29"><vh>todoController.clear_*</vh></v>
</v>
<v t="tbrown.20090119215428.30"><vh>todoController:Progress/time/project...</vh>
<v t="tbrown.20090119215428.31"><vh>todoController.progress_clear</vh></v>
<v t="tbrown.20090119215428.32"><vh>todoController.set_progress</vh></v>
<v t="tbrown.20090119215428.33"><vh>todoController.set_time_req</vh></v>
<v t="tbrown.20090119215428.34"><vh>todoController.show_times</vh></v>
<v t="tbrown.20090119215428.35"><vh>todoController.recalc_time</vh></v>
<v t="tbrown.20090119215428.36"><vh>todoController.clear_time_req</vh></v>
<v t="tbrown.20090119215428.37"><vh>todoController.update_project</vh></v>
<v t="tbrown.20090119215428.38"><vh>todoController.local_recalc</vh></v>
<v t="tbrown.20090119215428.39"><vh>todoController.local_clear</vh></v>
<v t="tbrown.20110213091328.16233"><vh>todoController.set_due_date</vh></v>
<v t="tbrown.20110213091328.16235"><vh>todoController.set_due_time</vh></v>
<v t="tbrown.20121204084515.60965"><vh>todoController.set_date_offset</vh></v>
</v>
<v t="tbrown.20090119215428.40"><vh>todoController:ToDo icon related...</vh>
<v t="tbrown.20090119215428.41"><vh>todoController.childrenTodo</vh></v>
<v t="tbrown.20130207095125.20463"><vh>todoController.dueClear</vh></v>
<v t="tbrown.20130207103126.28498"><vh>todoController.needs_doing</vh></v>
<v t="tbrown.20090119215428.42"><vh>todoController.find_todo</vh></v>
<v t="tbrown.20090119215428.43"><vh>todoController.prikey</vh></v>
<v t="tbrown.20110213153425.16373"><vh>todoController.duekey</vh></v>
<v t="tbrown.20110213153425.16377"><vh>todoController.dueSort</vh></v>
<v t="tbrown.20090119215428.44"><vh>todoController.priority_clear</vh></v>
<v t="tbrown.20090119215428.45"><vh>todoController.priSort</vh></v>
<v t="tbrown.20090119215428.46"><vh>todoController.reclassify</vh></v>
<v t="tbrown.20090119215428.47"><vh>todoController.setPri</vh></v>
<v t="tbrown.20090119215428.48"><vh>todoController.showDist</vh></v>
</v>
<v t="tbrown.20150605111428.1"><vh>todoController.updateStyle</vh></v>
<v t="tbrown.20090119215428.49"><vh>todoController.updateUI</vh></v>
<v t="tbrown.20121129095833.39490"><vh>todoController.unl_to_pos</vh></v>
</v>
<v t="tbrown.20170928065405.1"><vh>command fix datetime</vh></v>
<v t="tbrown.20100701093750.13800"><vh>command inc/dec priority</vh></v>
<v t="ekr.20260803125533.1"><vh>command find-todo</vh></v>
</v>
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
<v t="ekr.20260512145309.1"><vh>@file ../unittests/commands/test_leoAbbrev.py</vh></v>
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
<v t="ekr.20210906141410.1"><vh>@file ../unittests/core/test_leoUndo.py</vh></v>
<v t="ekr.20210910072917.1"><vh>@file ../unittests/core/test_leoVim.py</vh></v>
</v>
<v t="ekr.20240204082420.1"><vh>in unittests/misc_tests</vh>
<v t="ekr.20210926044012.1"><vh>@file ../unittests/misc_tests/test_doctests.py</vh></v>
<v t="ekr.20210901140718.1"><vh>@file ../unittests/misc_tests/test_syntax.py</vh></v>
<v t="ekr.20250109055422.1"><vh>@file ../unittests/misc_tests/test_modes.py</vh></v>
<v t="ekr.20230506095312.1"><vh>@file ../unittests/misc_tests/test_design.py</vh></v>
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
<t tx="ekr.20031218072017.2604">
</t>
<t tx="ekr.20031218072017.3625">See info issue #1585
https://github.com/leo-editor/leo-editor/issues/1585
@language python
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
<t tx="ekr.20051031040240"></t>
<t tx="ekr.20071113084440"># These plugins are for testing Leo's own plugin loading logic.
# There is no reason ever to enable these plugins.</t>
<t tx="ekr.20080412053100.5">
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
<t tx="ekr.20111118104929.10203">def make_func(self, edit: Any, toggle: Any, method: Any, default: Any) -&gt; Callable:
    def func(
        value: Any,
        edit: Any = edit,
        toggle: Any = toggle,
        method: Any = method,
        default: Any = default,
        self: Any = self,
    ) -&gt; None:
        edit.blockSignals(True)
        toggle.blockSignals(True)
        if value:
            getattr(edit, method)(value)  # pragma: no cover
            # edit.setEnabled(True)
            toggle.setChecked(True)  # pragma: no cover
        else:
            getattr(edit, method)(default)
            toggle.setChecked(False)
        edit.blockSignals(False)
        toggle.blockSignals(False)

    return func

</t>
<t tx="ekr.20111118104929.10204">def __init__(self, owner: todoController, logTab: bool = True) -&gt; None:
    self.owner = owner
    super().__init__()
    uiPath = g.os_path_join(g.app.leoDir, 'plugins', 'ToDo.ui')

    # change dir to get themed icons, needed for uic resources
    # These are icons for todo UI, not the tree.
    theme = g.app.config.getString('color-theme')
    if theme:
        testPath = g.os_path_join(g.app.homeLeoDir, 'themes', theme, 'Icons', 'cleo')
        if g.os_path_exists(testPath):
            iconPath = g.os_path_dirname(testPath)  # pragma: no cover
        else:
            testPath = g.os_path_join(g.app.loadDir, '..', 'themes', theme, 'Icons', 'cleo')
            if g.os_path_exists(testPath):
                iconPath = g.os_path_dirname(testPath)  # pragma: no cover
            else:
                iconPath = g.os_path_join(g.app.leoDir, 'Icons')
    else:
        iconPath = g.os_path_join(g.app.leoDir, 'Icons')
    os.chdir(iconPath)
    form_class, base_class = uic.loadUiType(uiPath)
    if logTab:
        self.owner.c.frame.log.createTab('Task', widget=self)
    self.UI = form_class()
    self.UI.setupUi(self)
    u = self.UI
    o = self.owner
    self.menu = QtWidgets.QMenu()
    self.populateMenu(self.menu, o)
    u.butMenu.setMenu(self.menu)

    u.butHelp.clicked.connect(lambda checked: o.showHelp())
    u.butClrProg.clicked.connect(lambda checked: o.progress_clear())
    u.butClrTime.clicked.connect(lambda checked: o.clear_time_req())
    u.butPriClr.clicked.connect(lambda checked: o.priority_clear())
    # if live update is too slow change valueChanged(*) to editingFinished()
    u.spinTime.valueChanged.connect(lambda v: o.set_time_req(val=u.spinTime.value()))
    u.spinProg.valueChanged.connect(lambda v: o.set_progress(val=u.spinProg.value()))

    u.dueDateEdit.dateChanged.connect(lambda v: o.set_due_date(val=u.dueDateEdit.date()))
    u.dueTimeEdit.timeChanged.connect(lambda v: o.set_due_time(val=u.dueTimeEdit.time()))

    u.nxtwkDateEdit.dateChanged.connect(
        lambda v: o.set_due_date(val=u.nxtwkDateEdit.date(), field='nextworkdate')
    )
    u.nxtwkTimeEdit.timeChanged.connect(
        lambda v: o.set_due_time(val=u.nxtwkTimeEdit.time(), field='nextworktime')
    )

    u.dueDateToggle.stateChanged.connect(
        lambda v: o.set_due_date(val=u.dueDateEdit.date(), mode='check')
    )
    u.dueTimeToggle.stateChanged.connect(
        lambda v: o.set_due_time(val=u.dueTimeEdit.time(), mode='check')
    )
    u.nxtwkDateToggle.stateChanged.connect(
        lambda v: o.set_due_date(
            val=u.nxtwkDateEdit.date(), mode='check', field='nextworkdate'
        )
    )
    u.nxtwkTimeToggle.stateChanged.connect(
        lambda v: o.set_due_time(
            val=u.nxtwkTimeEdit.time(), mode='check', field='nextworktime'
        )
    )

    for but in [
        "butPri1",
        "butPri6",
        "butPriChk",
        "butPri2",
        "butPri4",
        "butPri5",
        "butPri8",
        "butPri9",
        "butPri0",
        "butPriToDo",
        "butPriXgry",
        "butPriBang",
        "butPriX",
        "butPriQuery",
        "butPriBullet",
        "butPri7",
        "butPri3",
    ]:
        w = getattr(u, but)
        # w.property() seems to give QVariant in python 2.x and int in 3.x!?
        try:
            priority = int(w.property('priority'))
        except (TypeError, ValueError):  # pragma: no cover
            try:
                priority, ok = w.property('priority').toInt()
            except (TypeError, ValueError):
                priority = -1

        def setter(priority: int = priority) -&gt; None:  # pragma: no cover
            o.setPri(priority)

        w.clicked.connect(lambda checked, setter=setter: setter())

    offsets = self.owner.c.config.getData('todo_due_date_offsets')
    if not offsets:
        offsets = (
            '+7 +0 +1 +2 +3 +4 +5 +6 +10 +14 +21 +28 +42 +60 +90 +120 +150 &gt;7 &lt;7 &lt;14 &gt;14 &lt;28 &gt;28'
        ).split()
    self.date_offset_default = int(offsets[0].strip('&gt;').replace('&lt;', '-'))
    offsets = sorted(
        set(offsets), key=lambda x: (x[0], int(x[1:].strip('&gt;').replace('&lt;', '-')))
    )
    u.dueDateOffset.addItems(offsets)
    u.dueDateOffset.setCurrentIndex(self.date_offset_default)

    self.UI.dueDateOffset.activated.connect(lambda v: o.set_date_offset(field='duedate'))

    u.nxtwkDateOffset.addItems(offsets)
    u.nxtwkDateOffset.setCurrentIndex(self.date_offset_default)

    self.UI.nxtwkDateOffset.activated.connect(
        lambda v: o.set_date_offset(field='nextworkdate')
    )

    self.setDueDate = self.make_func(
        self.UI.dueDateEdit,
        self.UI.dueDateToggle,
        'setDate',
        dt.datetime.now(tz=dt.timezone.utc) + dt.timedelta(self.date_offset_default),
    )

    self.setDueTime = self.make_func(
        self.UI.dueTimeEdit,
        self.UI.dueTimeToggle,
        'setTime',
        dt.datetime.now(tz=dt.timezone.utc).time(),
    )

    self.setNextWorkDate = self.make_func(
        self.UI.nxtwkDateEdit,
        self.UI.nxtwkDateToggle,
        'setDate',
        dt.datetime.now(tz=dt.timezone.utc) + dt.timedelta(self.date_offset_default),
    )

    self.setNextWorkTime = self.make_func(
        self.UI.nxtwkTimeEdit,
        self.UI.nxtwkTimeToggle,
        'setTime',
        dt.datetime.now(tz=dt.timezone.utc).time(),
    )

    self.UI.butDetails.clicked.connect(
        lambda checked: self.UI.frmDetails.setVisible(not self.UI.frmDetails.isVisible())
    )

    if self.owner.c.config.getBool("todo-compact-interface"):
        self.UI.frmDetails.setVisible(False)  # pragma: no cover

    self.UI.butNext.clicked.connect(lambda checked: self.owner.c.selectVisNext())
    self.UI.butNextTodo.clicked.connect(lambda checked: self.owner.find_todo())
    self.UI.butApplyDueOffset.clicked.connect(
        lambda checked: o.set_date_offset(field='duedate')
    )
    self.UI.butApplyOffset.clicked.connect(
        lambda checked: o.set_date_offset(field='nextworkdate')
    )

    n = g.app.config.getInt("todo-calendar-n")
    cols = g.app.config.getInt("todo-calendar-cols")
    if n or cols:
        self.UI.dueDateEdit.calendarWidget().build(n or 3, cols or 3)
        self.UI.nxtwkDateEdit.calendarWidget().build(n or 3, cols or 3)

</t>
<t tx="ekr.20111118104929.10205">@staticmethod
def populateMenu(menu: QtWidgets.QMenu, o: Any) -&gt; None:
    menu.addAction('Find next ToDo', o.find_todo)
    m = menu.addMenu("Priority")
    m.addAction('Priority Sort', o.priSort)
    m.addAction('Due Date Sort', o.dueSort)
    m.addAction('Next Work Date Sort', lambda: o.dueSort(field='nextwork'))
    m.addAction('Clear Descendant Due Dates', o.dueClear)
    m.addAction('Mark children todo', o.childrenTodo)
    m.addAction('Show distribution', o.showDist)
    m.addAction('Redistribute', o.reclassify)
    m = menu.addMenu("Time")
    m.addAction('Show times', lambda: o.show_times(show=True))
    m.addAction('Hide times', lambda: o.show_times(show=False))
    m.addAction('Re-calc. derived times', o.local_recalc)
    m.addAction('Clear derived times', o.local_clear)
    m = menu.addMenu("Misc.")
    m.addAction('Hide all Todo icons', lambda: o.loadAllIcons(clear=True))
    m.addAction('Show all Todo icons', o.loadAllIcons)
    m.addAction('Delete Todo from node', o.clear_node)
    m.addAction('Delete Todo from subtree', lambda: o.clear_subtree)
    m.addAction('Delete Todo from all', lambda: o.clear_all)

</t>
<t tx="ekr.20111118104929.10207">def setProgress(self, prgr: Any) -&gt; None:
    try:
        self.UI.spinProg.blockSignals(True)
        self.UI.spinProg.setValue(prgr)
    finally:
        self.UI.spinProg.blockSignals(False)

</t>
<t tx="ekr.20111118104929.10208">def setTime(self, timeReq: Any) -&gt; None:
    self.UI.spinTime.blockSignals(True)
    self.UI.spinTime.setValue(timeReq)
    self.UI.spinTime.blockSignals(False)

</t>
<t tx="ekr.20120309073937.9878"></t>
<t tx="ekr.20121126102050.10134"></t>
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
stw:    leoAPI.StringTextWrapper

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
</t>
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
<t tx="ekr.20150425145248.1">pylint
execute-script

# check-leo
# patch-pyflakes

# restart-leo
# ctrl-click-at-cursor

# test-pylint
# test-one
# mypy-modes
# pyflakes
# test1-pyflakes
# test-pyflakes
# cover-pyflakes
# proto-pyflakes

# ctrl-click-at-cursor
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
<t tx="ekr.20150514035207.1"></t>
<t tx="ekr.20160122104332.1">@language python
</t>
<t tx="ekr.20160123142722.1" _mod_time="4741da9d31854271d22e"># An example configuration file for make_stub_files.py.
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
    from collections.abc import Iterable
    from typing import TypeVar
    T = TypeVar('T', int, float, complex)

[Def Name Patterns]

[General Patterns]
</t>
<t tx="ekr.20170427114412.1"></t>
<t tx="ekr.20170428084123.1">@language python
"""Recursively import all python files in a directory and clean the result."""
@tabwidth - 4  # For a better match.
g.cls()
# dir_ = g.os_path_finalize_join(g.app.loadDir, '..', 'modes')
# dir_ = g.os_path_finalize_join(g.app.loadDir, '..', '..', 'setup.py')
# dir_ = r'C:\Python\Python3.13\Lib\pdb.py'
dir_ = r'C:\Python\Python3.14\Lib\site-packages\mypy'
c.recursiveImport(
    dir_=dir_,
    kind= '@clean',  # '@auto', '@clean', '@nosent','@file',
    recursive=True,
    safe_at_file=False,
    theTypes=['.py'],
    verbose=True,
)
if 1:
    last = c.lastTopLevel()
    last.expand()
    if last.hasChildren():
        last.firstChild().expand()
    c.redraw(last)
print('Done')
</t>
<t tx="ekr.20170811173924.1">@language python
import os
import subprocess
import sys
import time
old_dir = os.getcwd()
if g.isWindows:
    new_dir = r'C:\Repos\leo-editor'
    path = r'C:\Users\Edward~1\Backup\backup-repo'
else:
    new_dir = '/home/edward/Repos/leo-editor'
    path = '/home/edward/Backup'
assert g.os_path_exists(new_dir), repr(new_dir)
assert g.os_path_exists(path), repr(path)
stamp = time.strftime("%Y%m%d-%H%M%S")
fn = g.finalize_join(path, f"leo-bundle-all-{stamp}")
bundle_command = f"git bundle create {fn} --all"
print(bundle_command)
os.chdir(new_dir)
proc = subprocess.Popen(bundle_command)
proc.wait()
os.chdir(old_dir)
print('done! wrote %s' % fn)
</t>
<t tx="ekr.20171031111403.1"></t>
<t tx="ekr.20180225010644.1"></t>
<t tx="ekr.20180225010707.1"></t>
<t tx="ekr.20180225010743.1">@nosearch</t>
<t tx="ekr.20180225010850.1"></t>
<t tx="ekr.20180225010913.1"></t>
<t tx="ekr.20180504191650.36"></t>
<t tx="ekr.20180504191650.42"></t>
<t tx="ekr.20180504191650.68" _mod_time="4741da9d31854421032e"></t>
<t tx="ekr.20180504192522.1"></t>
<t tx="ekr.20180708145905.1" _mod_time="4741da9d31854271d22e">@language rest
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
    branch1='devel',  # old branch/rev
    branch2='ekr-generalize-g.stat',  # new branch/rev
    fn='leo/core/leoGlobals.py',  # Don't use back slashes.
)
</t>
<t tx="ekr.20181030041436.1"></t>
<t tx="ekr.20190402091335.1">from leo.commands import editFileCommands as efc

efc.GitDiffController(c).diff_two_revs(
    rev1='main',  # Old
    rev2='6.8.8',  # New
    path='leo/core',  # Optional path, relative to the git directory.
)
</t>
<t tx="ekr.20190607124533.1"></t>
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
<t tx="ekr.20201111052557.1">def patch_1591(self) -&gt; None:
    """
    A workaround for #1591.

    Add labels and tooltips for all buttons.
    """
    ui = self.ui.UI
    size = QtCore.QSize(16, 16)
    for i in range(10):
        button = getattr(ui, f"butPri{i}")
        path = g.finalize_join(g.app.loadDir, '..', 'Icons', "cleo", f"pri{i}.png")
        button.setIcon(QtGui.QIcon(path))
        button.setIconSize(size)
        button.setToolTip(f"Priority {i}")

    table = (
        # Alternate priorities...
        ('butPriChk', 'chkblk.png', 'Check Mark'),
        ('butPriToDo', 'chkboxblk.png', 'Box Mark'),
        ('butPriX', 'xblk.png', 'Black X'),
        ('butPriXgry', 'xgry.png', 'Gray X'),
        ('butPriBang', 'bngblk.png', 'Exclamation Point'),
        ('butPriQuery', 'qryblk.png', 'Question Mark'),
        ('butPriBullet', 'bullet.png', 'Bullet'),
        ('butPriClr', 'edit-clear.png', 'Clear Priority'),
        # Other labels...
        ('butDetails', 'document-save.png', 'Toggle Details'),
        ('butNext', 'down.png', 'Next Node'),
        ('butNextTodo', 'bottom.png', 'Next To Do'),
        ('butClrTime', 'edit-clear.png', 'Clear Required Time'),
        ('butClrProg', 'edit-clear.png', 'Clear Progress'),
    )

    for attr, icon, tooltip in table:
        button = getattr(ui, attr)
        path = g.finalize_join(g.app.loadDir, '..', 'Icons', "cleo", icon)
        button.setIcon(QtGui.QIcon(path))
        button.setIconSize(size)
        button.setToolTip(tooltip)

</t>
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
<t tx="ekr.20220306092217.1">"""Invoke EKR's private test-one.cmd script."""

import os

if c.isChanged():
    print('Saved!')
    c.save()

os.system('test-one.cmd')
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

rev1 = 'main'  
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
<t tx="ekr.20220823195205.1" _mod_time="4741da9d318542633b2e">"""
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
    verbose=False,
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
quicksearch.py      # Nav pane.
viewrendered.py     # (Or viewrendered3.py) Plugins menu support.

# Disabled standard menus...

# mod_autosave.py   # Creates .bak files.
# nodetags.py       # Supports tags via uA's.
# todo.py             # Task pane.
</t>
<t tx="ekr.20221129012213.1"># See flake8 settings in setup.cfg.</t>
<t tx="ekr.20221204070905.1"></t>
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
<t tx="ekr.20230624114517.1" _mod_time="4741da9d318543cb102e"></t>
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
scripts_dir = join(leo_dir, 'scripts')
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
script_files = make_list(f"{scripts_dir}{sep}*.py")
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
    g.es_print(f"{n} missing file{g.plural(n)}")
    g.printObj(missing, tag='missing @&lt;file&gt; nodes')
else:
    g.es_print('No missing files!')
print('done')</t>
<t tx="ekr.20240107154430.1"></t>
<t tx="ekr.20240204082420.1"></t>
<t tx="ekr.20240204082924.1"></t>
<t tx="ekr.20240206161713.1" _mod_time="4741da9d318547277e2e">@language ini

[bdist_wheel]

# Leo only supports Python 3, so universal should be zero.
universal=0

[metadata]

# Becomes the home-page in `pip show leo`.
url = https://leo-editor.github.io/leo-editor/

[flake8]

exclude =
    .git,
    __pycache__,
    leo/build,
    leo/dist,
    leo/doc,
    leo/extensions,
    leo/external,
    leo/modes,
    leo/plugins,
    leo/scripts,
    leo/test,
    leo/unittests/py3_test_grammar.py,

extend-ignore =

    # Don't check B020. It conflicts with Leo idioms like `for p in p.children():
    # Found for loop that reassigns the iterable it is iterating with each iterable value.
    # B020

    # blank line contains whitespace
    # W293

    # Comments and continuation lines...

    # expected an indented block (comment)
    # E115

    # unexpected indentation (comment)
    E116

    # over-indented (comment)
    E117

    # continuation line over-indented for visual indent
    E127

    # continuation line missing indentation or outdented.
    E122

    # closing bracket does not match visual indentation.
    E124

    # continuation line with same indent as next logical line
    E125

    # continuation line under-indented for visual indent.
    E128

    # visually indented line with same indent as next logical line
    E129

    # continuation line unaligned for hanging indent.
    E131

    # whitespace before ':'
    # Conflict between black and flake8.
    E203

    # whitespace before '['
    # E211

    # multiple spaces before operator
    # Conflicts with extra spacing in @nobeautify nodes.
    E221

    # multiple spaces after operator
    # Conflicts with extra spacing in @nobeautify nodes.
    E222

    # missing whitespace around operator
    # Conflicts with extra spacing in @nobeautify nodes.
    # E225

    # missing whitespace after ','
    # E231

    # unexpected spaces around keyword / parameter equals
    # Conflicts with extra spacing in @nobeautify nodes.
    E251

    # at least two spaces before inline comment
    # E261

    # missing whitespace around parameter equals.
    # E252

    # inline comment should start with '# '
    E262

    # block comment should start with '# '.
    E265

    # too many leading '#' for block comment
    # Prohibits ### comments.
    E266

    # multiple spaces before keyword
    # Interferes with @nobeautify
    E272

    # missing whitespace after keyword.
    # Interferes with @nobeautify. Also warns about assert(whatever) and except(list).
    E275

    # trailing whitespace
    # E293

    # expected 1 blank line, found 0.
    E301

    # expected 2 blank lines, found 1.
    E302

    # whitespace before ':'
    # E203

    # too many blank lines (2)
    E303

    # expected 2 blank lines after class or function definition, found 0.
    # E305

    # expected 1 blank line before a nested definition, found 0.
    E306

    # Line too long.
    E501

    # global `whatever` is unused: name is never assigned in scope.
    # F824
</t>
<t tx="ekr.20240317061516.1" _mod_time="4741da9d31853186802e">@language python

# Order matters!

# Include *everything* in the leo folder.
graft leo

global-exclude *.py[cod] *.__pycache__ *.so
global-exclude *mypy_cache *.mypy_cache, *.mypy_stubs, *.gitattributes, *.htmlcov

# Add files in the top-level leo-editor folder.

include *.py
include *.TXT

# No longer required.
# obscure pip bug fix https://github.com/pypa/setuptools/issues/1694
#include pyproject.toml

# Tweaks

prune leo/unittests/htmlcov
prune leo/doc/html
include leo/doc/html/conf.py

# #3853.
include leo/doc/_static
</t>
<t tx="ekr.20240321122614.1"># These are Leo's test scripts.

# Run these scripts from the leo-editor folder.

# Info item #3867 describes these scripts:
# https://github.com/leo-editor/leo-editor/issues/2867
</t>
<t tx="ekr.20240321122705.1"># Here are Leo's distribution-related scripts.

# Info item #3837 contains full documentation for all these scripts.
# https://github.com/leo-editor/leo-editor/issues/3837</t>
<t tx="ekr.20240403090451.1">"""
Expand button bar.

Clicking this button does nothing if all buttons are already visible.
Otherwise, this button shows all buttons, using separate lines if necessary.
"""

# https://doc.qt.io/qt-6/qtoolbar.html

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import QApplication

pos = QPointF(0, 0)
button = Qt.MouseButton.LeftButton
btns = Qt.MouseButton(0)
mods = Qt.KeyboardModifier(0)

# Define the event types directly without accessing them through Qt
e1 = QMouseEvent(QMouseEvent.Type.MouseButtonPress, pos, button, btns, mods)
e2 = QMouseEvent(QMouseEvent.Type.MouseButtonRelease, pos, button, btns, mods)

iconBar = c.frame.iconBar.w
# print(iconBar)

for i in range(20):
    iconBar.addAction(str(i))
    
if 0:
    # Assuming 'c' and 'w' are already defined
    for w in c.frame.iconBar.w.children():
        print(repr(w.objectName()))
        if w.objectName() == 'qt_toolbar_ext_button':
            QApplication.sendEvent(w, e1)
            QApplication.sendEvent(w, e2)
            break
        
print('Done!')

@language python
</t>
<t tx="ekr.20240403111007.1">"""Add toolbar buttons, centered in new rows."""

g.cls()

# https://doc.qt.io/qt-6/qtoolbar.html
from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import QApplication, QSizePolicy, QWidget

pos = QPointF(0, 0)
button = Qt.MouseButton.LeftButton
btns = Qt.MouseButton(0)
mods = Qt.KeyboardModifier(0)

# Define the event types directly without accessing them through Qt
e1 = QMouseEvent(QMouseEvent.Type.MouseButtonPress, pos, button, btns, mods)
e2 = QMouseEvent(QMouseEvent.Type.MouseButtonRelease, pos, button, btns, mods)

iconBar = c.frame.iconBar.w
# print(iconBar)

def addSpacer():
    w = QWidget()
    policy = QSizePolicy()
    w.setSizePolicy(policy.Policy.Expanding, policy.Policy.Preferred)
    iconBar.addWidget(w)
    
for i in range(20):
    iconBar.addAction(str(i))
    if i in (4, 8, 12, 16):
        addSpacer()

print('Done!')

@language python
</t>
<t tx="ekr.20240417150035.1"># 'python c:/test/mypy_test.py',
# 'python -m mypy c:/test/mypy_test.py',
# 'python -m ruff check c:/test/mypy_test.py',
# 'python -m pyflakes c:/test/mypy_test.py',

# f"{misc}.test_check_leo.TestCheckLeo",
# f"{core}.test_leoserver.TestLeoServer.test_find_commands",
# f"{core}.test_leoFind.TestFind.test_find_var",
# f"{core}.test_leoTokens.TestTokenBasedOrange",
# f"{core}.test_leoTokens.TestTokens",
# f"{core}.test_leoTokens.TestTokenBasedOrange.test_blank_lines_after_function",
# f"{core}.test_leoAtFile.TestAtFile.test_putBody_unterminated_at_doc_part",
</t>
<t tx="ekr.20240528034319.1"># Can be run from the command line as follows:
# python -c "import leo.core.leoTokens" --all --report --write leo/core/leoAst.py
args = '--all --report --write'  # --beautified --diff --write'
for command in (
    # f'python -c "import leo.core.leoTokens" {args} leoAst.py',
    f'python -c "import leo.core.leoTokens" {args} leo/core',
    'echo done!',
):
    print(command)
    g.execute_shell_commands(command)
</t>
<t tx="ekr.20240608035218.1"># Last one wins.
kind = 'beautify'
kind = 'test'  # Run unit test.
</t>
<t tx="ekr.20240707233742.1">"""
Convert the names of Ast visitors from all caps to the names of the corresponding Ast node.
Saved in PR #4: https://github.com/edreamleo/ekr-fork-pyflakes/pull/4
"""
g.cls()
c.save()
import ast
# import re
h = 'class Checker'
root = g.findNodeAnywhere(c, h)
# pattern = re.compile(r'([A-Z]{3,})')
&lt;&lt; define table &gt;&gt;
&lt;&lt; check table &gt;&gt;
suppress = ('_MAGIC', 'PYFLAKES', 'FOR_TYPES', '.STRING')
for p in root.self_and_subtree():
    changed, results = False, []
    for s in g.splitLines(p.b):
        if s.strip().startswith(('#', '"""')):
            results.append(s)
            continue
        if any(z in s for z in suppress):
            results.append(s)
            continue
        found = []
        for data in table:
            s1, s2 = data
            if s1 in s and s1 not in suppress:
                if s1.lower() not in found:
                    # if 'name' in s1.lower():
                        # print(s1)
                        # print(s.rstrip())
                    s = s.replace(s1, s2)
                    changed = True
                    found.append(s1.lower())
        if found:
            print(s.rstrip())
        results.append(s)
    if changed:
        if 1:
            p.b = ''.join(results)
        # g.printObj(results) #, tag=p.h)
        
if 1:
    print('')
    print('Remember to update handleNode')

c.save()
print('Done')
    </t>
<t tx="ekr.20240708062242.1">
# Longest prefixes first.
table = (

    ('ANNASSIGN', 'AnnAssign'),
    ('ARGUMENTS', 'arguments'),  # all lower.
    ('ASSERT', 'Assert'),
    ('ASYNCFOR', 'AsyncFor'),
    ('ASYNCFUNCTIONDEF', 'AsyncFunctionDef'),
    ('ASYNCWITH', 'AsyncWith'),
    ('ATTRIBUTE', 'Attribute'),
    ('AUGASSIGN', 'AugAssign'),
    ('AUGLOAD', 'AugLoad'),
    ('AUGSTORE', 'AugStore'),
    ('AWAIT', 'Await'),
    ('BINOP', 'BinOp'),
    ('BITAND', 'BitAnd'),
    ('BITOR', 'BitOr'),
    ('BITXOR', 'BitXor'),
    ('BOOLOP', 'BoolOp'),
    ('BREAK', 'Break'),
    ('CALL', 'Call'),
    ('CLASSDEF', 'ClassDef'),
    ('COMPARE', 'Compare'),
    ('COMPREHENSION', 'comprehension'),
    ('CONTINUE', 'Continue'),
    ('DELETE', 'Delete'),
    ('DICTCOMP', 'DictComp'),    
    ('EXCEPTHANDLER', 'ExceptHandler'),
    ('EXTSLICE', 'ExtSlice'),
    ('FLOORDIV', 'FloorDiv'),
    ('FORMATTEDVALUE', 'FormattedValue'),
    ('FUNCTIONDEF', 'FunctionDef'),
    ('GENERATOREXP', 'GeneratorExp'),
    ('GLOBAL', 'Global'),
    ('IFEXP', 'IfExp'),
    ('IMPORTFROM', 'ImportFrom'),
    ('INDEX', 'Index'),
    ('INVERT', 'Invert'),
    ('ISNOT', 'IsNot'),
    ('JOINEDSTR', 'JoinedStr'),
    ('KEYWORD', 'keyword'),
    ('LAMBDA', 'Lambda'),
    ('LISTCOMP', 'ListComp'),
    ('LOAD', 'Load'),
    ('LSHIFT', 'LShift'),
    ('MATCHAS', 'MatchAs'),
    ('MATCHCLASS', 'MatchClass'),
    ('MATCHMAPPING', 'MatchMapping'),
    ('MATCHOR', 'MatchOr'),
    ('MATCHSEQUENCE', 'MatchSequence'),
    ('MATCHSINGLETON', 'MatchSingleton'),
    ('MATCHSTAR', 'MatchStar'),
    ('MATCHVALUE', 'MatchValue'),
    ('MATCH_CASE', 'match_case'),
    ('MATMULT', 'MatMult'),
    ('MODULE', 'Module'),
    ('MULT', 'Mult'),
    ('NONLOCAL', 'Nonlocal'),
    ('NOTEQ', 'NotEq'),
    ('NOTIN', 'NotIn'),
    ('PARAMSPEC', 'ParamSpec'),
    ('PARAM', 'Param'),
    ('PASS', 'Pass'),
    ('RAISE', 'Raise'),
    ('RETURN', 'Return'),
    ('RSHIFT', 'RShift'),
    ('SETCOMP', 'SetComp'),
    ('SLICE', 'Slice'),
    ('STARRED', 'Starred'),
    ('STORE', 'Store'),
    ('SUBSCRIPT', 'Subscript'),
    ('TRYSTAR', 'TryStar'),
    ('TUPLE', 'Tuple'),
    ('TYPEALIAS', 'TypeAlias'),
    ('TYPEVARTUPLE', 'TypeVarTuple'),
    ('TYPEVAR', 'TypeVar'),
    ('UADD', 'UAdd'),
    ('UNARYOP', 'UnaryOp'),
    ('USUB', 'USub'),
    ('WHILE', 'While'),
    ('WITHITEM', 'withitem'),
    ('YIELDFROM', 'YieldFrom'),
    
    # Prefixes last, by length.
    ('NAMECONSTANT', 'NameConstant'),
    ('NAMEDEXPR', 'NamedExpr'),
    ('CONSTANT', 'Constant'),
    ('ASSIGN', 'Assign'),
    ('IMPORT', 'Import'),
    ('MATCH', 'Match'),
    ('YIELD', 'Yield'),

    ('DICT', 'Dict'),
    ('EXPR', 'Expr'),
    ('LIST', 'List'),
    ('NAME', 'Name'),
    ('WITH', 'With'),

    ('ARG', 'arg'),
    ('ADD', 'Add'),
    ('AND', 'And'),
    ('DEL', 'Del'),
    ('DIV', 'Div'),
    ('FOR', 'For'),
    ('GTE', 'GtE'),
    ('LTE', 'LtE'),
    ('MOD', 'Mod'),
    ('NOT', 'Not'),
    ('POW', 'Pow'),
    ('SET', 'Set'),
    ('SUB', 'Sub'),
    ('TRY', 'Try'),

    ('EQ', 'Eq'),
    ('IF', 'If'),
    ('IN', 'In'),
    ('IS', 'Is'),
    ('GT', 'Gt'),
    ('LT', 'Lt'),
    ('OR', 'Or'),
)
</t>
<t tx="ekr.20240708072327.1">for data in table:
    s1, s2 = data
    visitor = getattr(ast, s2, None)
    if not visitor:
        print('Missing', s2)
</t>
<t tx="ekr.20240714075119.1">"""Update the section `pyproject.toml: dependencies` from requirements.txt."""
g.cls()
req_h = '@file ../../requirements.txt'
req_p = g.findNodeAnywhere(c, req_h)
assert req_p, req_h
proj_h = g.angleBrackets(' pyproject.toml: dependencies ')
proj_p = g.findNodeAnywhere(c, proj_h)
assert proj_p, proj_h

# Indent all non-blank lines with 2-blanks.
results = ['dependencies = [']
for s in g.splitLines(req_p.b):
    ss = s.strip()
    if not ss:
        results.append('')
    elif ss.startswith('@'):
        continue  # Don't change directives.
    elif ss.startswith('#'):
        results.append(f"  {ss}")
    else:
        i = ss.find('#')
        if i &gt; -1:
            s2 = ss[:i].strip().replace('"', "'")
            # Ensure spaces around '=='.
            if '==' in s2 and ' == ' not in s2:
                s2 = s2.replace('==', ' == ')
                s3 = f'  {ss[len(s2):]}'
            else:
                s3 = ss[len(s2):]
            results.append(f'  "{s2}",{s3}')
        else:
            results.append(f'  "{ss}",')
results.append(']\n\n')
# Print the changes.
for s in results:
    print(s)
# Make the changes!
new_b = '\n'.join(results)
if new_b != proj_p.b:
    print('Saving:', proj_p.h)
    proj_p.b = new_b
    c.redraw()
    c.save()</t>
<t tx="ekr.20250715195948.1"></t>
<t tx="ekr.20251214042454.1">True: Wrap body text.

</t>
<t tx="ekr.20260111055821.1"># These settings control ruff format, which is compatible with black.</t>
<t tx="ekr.20260111055821.2"># True: beautify all @&lt;file&gt; nodes in the outline using Leo's token-based beautifier.
# True can result in much slower writes.</t>
<t tx="ekr.20260111055821.4"># This setting overrides any value in pyproject.toml or ruff.toml
# Leo uses 120 for its own files.</t>
<t tx="ekr.20260111055821.5"># If given, this argument should be a full, absolute path to pyproject.toml or ruff.toml.
# If not given, Leo's beautifier uses Leo's pyproject.toml file.
</t>
<t tx="ekr.20260112054444.1">g.cls()
root = g.findTopLevelNode(c, 'git diff revs: master 6.8.8')
results = g.findTopLevelNode(c, 'diff: results')
if results:
    results.deleteAllChildren()
else:
    results = c.lastTopLevel().insertAsLastChild()
    results.h = 'diff: results'
changed = 0


def report(p):
    global changed
    changed += 1
    child = results.insertAsLastChild()
    child.h = p.h
    for s in g.splitLines(p.b):
        if s.startswith(('+ ', '- ')):
            tail = s[2:].strip()
            if tail and not tail.startswith(('#@', '# @')):
                child.b += s


for p in root.subtree():
    if p.h.startswith('diff:'):
        if p.h == 'diff: Changed':
            pass
        elif p.h.endswith('.py'):
            report(p)

print(f"changed: {changed}")
results.expand()
c.redraw()
</t>
<t tx="ekr.20260112121427.1">g.cls()
from leo.commands import editFileCommands as efc

# Any branch or rev is valid.
efc.GitDiffController(c).summary_diff_two_revs(
    rev1='main',    # Old
    rev2='6.8.8',     # New
    path='leo/core',  # Limit diffs to this directory, relative to the nearest git repo.
)  # fmt: skip
</t>
<t tx="ekr.20260113153148.1">"""Generic test bed for scripts and other development"""
g.cls()
# g.app.log.clearLog()
import textwrap

results_p = g.findTopLevelNode(c, 'TestResults')
if not results_p:
    results_p = c.lastTopLevel().insertAfter()
    results_p.h = 'TestResults'

&lt;&lt; define test_s &gt;&gt;
@others

results = remove_cruft(self=None, diff_list=g.splitLines(test_s))
results_p.b = results
c.redraw(results_p)

@language python
</t>
<t tx="ekr.20260114092617.1">@language diff

test_s = textwrap.dedent('''

@nosearch
@language patch
--- master
+++ devel
@@ -1,8 +1,9 @@
-#@+leo-ver=5-thin
-#@+node:ekr.20150514035236.1: * @file ../commands/abbrevCommands.py
+# @+leo-ver=5-thin
+# @+node:ekr.20150514035236.1: * @file ../commands/abbrevCommands.py
 """Leo's abbreviations commands."""
-#@+&lt;&lt; abbrevCommands imports &amp; abbreviations &gt;&gt;
-#@+node:ekr.20150514045700.1: ** &lt;&lt; abbrevCommands imports &amp; abbreviations &gt;&gt;
+
+# @+&lt;&lt; abbrevCommands imports &amp; abbreviations &gt;&gt;
+# @+node:ekr.20150514045700.1: ** &lt;&lt; abbrevCommands imports &amp; abbreviations &gt;&gt;
 from __future__ import annotations
 from collections.abc import Callable
 import functools
@@ -18,22 +19,31 @@
     from leo.core.leoGui import LeoKeyEvent
     from leo.core.leoNodes import Position
     from leo.plugins.qt_text import QTextEditWrapper as Wrapper
-#@-&lt;&lt; abbrevCommands imports &amp; abbreviations &gt;&gt;
+# @-&lt;&lt; abbrevCommands imports &amp; abbreviations &gt;&gt;
+
 
 def cmd(name: str) -&gt; Callable:
     """Command decorator for the abbrevCommands class."""
-    return g.new_cmd_decorator(name, ['c', 'abbrevCommands',])
-
-#@+others
-#@+node:ekr.20160514095531.1: ** class AbbrevCommands
+    return g.new_cmd_decorator(
+        name,
+        [
+            'c',
+            'abbrevCommands',
+        ],
+    )
+
+
+# @+others
+# @+node:ekr.20160514095531.1: ** class AbbrevCommands
 class AbbrevCommandsClass(BaseEditCommandsClass):
     """
     A class to handle user-defined abbreviations.
     See apropos-abbreviations for details.
     """
-    #@+others
-    #@+node:ekr.20150514043850.2: *3* abbrev.Birth
-    #@+node:ekr.20150514043850.3: *4* abbrev.ctor
+
+    # @+others
+    # @+node:ekr.20150514043850.2: *3* abbrev.Birth
+    # @+node:ekr.20150514043850.3: *4* abbrev.ctor
     def __init__(self, c: Cmdr) -&gt; None:
         """Ctor for AbbrevCommandsClass class."""
         # pylint: disable=super-init-not-called
@@ -41,8 +51,9 @@
         # Set local ivars.
         self.abbrevs: dict[str, tuple[str, str]] = {}  # Keys are names, values are (abbrev,tag).
         self.dynaregex = re.compile(  # For dynamic abbreviations
-            r'[%s%s\-_]+' % (string.ascii_letters, string.digits))
-            # Not a unicode problem.
+            r'[%s%s\-_]+' % (string.ascii_letters, string.digits)
+        )
+        # Not a unicode problem.
         self.n_regex = re.compile(r'(?&lt;!\\)\\n')  # to replace \\n but not \\\\n
         self.enabled = False
         self.expanding = False  # True: expanding abbreviations.
@@ -54,11 +65,13 @@
         self.store = {'rlist': [], 'stext': ''}  # For dynamic expansion.
         self.tree_abbrevs_d: dict[str, str] = {}  # Keys are names, values are (tree,tag).
         self.w = None
-    #@+node:ekr.20150514043850.5: *4* abbrev.finishCreate &amp; helpers
+
+    # @+node:ekr.20150514043850.5: *4* abbrev.finishCreate &amp; helpers
     def finishCreate(self) -&gt; None:
         """AbbrevCommandsClass.finishCreate."""
         self.reload_settings()
-    #@+node:ekr.20170221035644.1: *5* abbrev.reload_settings &amp; helpers
+
+    # @+node:ekr.20170221035644.1: *5* abbrev.reload_settings &amp; helpers
     def reload_settings(self) -&gt; None:
         """Reload all abbreviation settings."""
         self.abbrevs = {}
@@ -68,7 +81,8 @@
         self.init_env()
 
     reloadSettings = reload_settings
-    #@+node:ekr.20150514043850.6: *6* abbrev.init_abbrev
+
+    # @+node:ekr.20150514043850.6: *6* abbrev.init_abbrev
     def init_abbrev(self) -&gt; None:
         """
         Init the user abbreviations from @data global-abbreviations
@@ -77,8 +91,8 @@
         c = self.c
         table = (
             ('global-abbreviations', 'global'),
-            ('abbreviations', 'local'),
-        )
+            ('abbreviations',       'local'),
+        )  # fmt: skip
         for source, tag in table:
             aList = c.config.getData(source, strip_data=False) or []
             abbrev, result = [], []
@@ -103,10 +117,11 @@
         # fake the next placeholder abbreviation
         if c.config.getString("abbreviations-next-placeholder"):
             self.addAbbrevHelper(
-                f'{c.config.getString("abbreviations-next-placeholder")}'
-                f'=__NEXT_PLACEHOLDER',
-                'global')
-    #@+node:ekr.20150514043850.7: *6* abbrev.init_env
+                f'{c.config.getString("abbreviations-next-placeholder")}=__NEXT_PLACEHOLDER',
+                'global',
+            )
+
+    # @+node:ekr.20150514043850.7: *6* abbrev.init_env
     def init_env(self) -&gt; None:
         """
         Init c.abbrev_subst_env by executing the contents of the
@@ -134,11 +149,7 @@
                 v = leoNodes.VNode(context=c)
                 root = leoNodes.Position(v)
             # Similar to g.getScript.
-            script = at.stringToString(
-                root=root,
-                s=script,
-                forcePythonSentinels=True,
-                sentinels=False)
+            script = at.stringToString(root=root, s=script, forcePythonSentinels=True, sentinels=False)
             script = script.replace("\r\n", "\n")
             try:
                 exec(script, c.abbrev_subst_env, c.abbrev_subst_env)  # type:ignore
@@ -147,7 +158,8 @@
                 g.es_exception()
         else:
             c.abbrev_subst_start = ''  # Was False.
-    #@+node:ekr.20150514043850.8: *6* abbrev.init_settings (called from reload_settings)
+
+    # @+node:ekr.20150514043850.8: *6* abbrev.init_settings (called from reload_settings)
     def init_settings(self) -&gt; None:
         """Called from AbbrevCommands.reload_settings aka reloadSettings."""
         c = self.c
@@ -157,14 +169,16 @@
         c.abbrev_subst_end = c.config.getString('abbreviations-subst-end')
         # The environment for all substitutions.
         # May be augmented in init_env.
-        c.abbrev_subst_env = {'c': c, 'g': g, '_values': {}, }
+        c.abbrev_subst_env = {
+            'c': c,
+            'g': g,
+            '_values': {},
+        }
         c.abbrev_subst_start = c.config.getString('abbreviations-subst-start') or ''
         # Local settings.
-        self.enabled = (
-            c.config.getBool('scripting-at-script-nodes') or
-            c.config.getBool('scripting-abbreviations'))
+        self.enabled = c.config.getBool('scripting-at-script-nodes') or c.config.getBool('scripting-abbreviations')
         self.globalDynamicAbbrevs = c.config.getBool('globalDynamicAbbrevs')
-        #@verbatim
+        # @verbatim
         # @data abbreviations-subst-env must *only* be defined in leoSettings.leo or myLeoSettings.leo!
         self.subst_env: list[str]
         if c.config:
@@ -174,7 +188,8 @@
                 self.subst_env = []
             else:
                 self.subst_env = c.config.getData(key, strip_data=False)
-    #@+node:ekr.20150514043850.9: *6* abbrev.init_tree_abbrev
+
+    # @+node:ekr.20150514043850.9: *6* abbrev.init_tree_abbrev
     def init_tree_abbrev(self) -&gt; None:
         """Init tree_abbrevs_d from @data tree-abbreviations nodes."""
         c = self.c
@@ -208,7 +223,8 @@
             finally:
                 g.app.disable_redraw = old_disable
         self.tree_abbrevs_d = d
-    #@+node:ekr.20170227062001.1: *7* abbrev.init_tree_abbrev_helper
+
+    # @+node:ekr.20170227062001.1: *7* abbrev.init_tree_abbrev_helper
     def init_tree_abbrev_helper(self, d: dict[str, str], tree_s: str) -&gt; None:
         """Init d from tree_s, the text of a copied outline."""
         c = self.c
@@ -228,7 +244,8 @@
                             break
                     else:
                         g.trace(f"no definition for {abbrev_name}")
-    #@+node:ekr.20150514043850.11: *3* abbrev.expandAbbrev &amp; helpers (entry point)
+
+    # @+node:ekr.20150514043850.11: *3* abbrev.expandAbbrev &amp; helpers (entry point)
     def expandAbbrev(self, event: LeoKeyEvent, stroke: g.KeyStroke) -&gt; bool:
         """
         Not a command.  Expand abbreviations in event.widget.
@@ -255,14 +272,18 @@
         for prefix in prefixes:
             i, tag, word, val = self.match_prefix(ch, i, j, prefix, s)
             if word:
+                # #4462: Make only one substitution in headlines.
+                if w_name.startswith('head'):
+                    ok = self.make_script_substitutions_in_headline(i, p, val)
+                    if ok:
+                        return True
                 # Fix another part of #438.
-                if w_name.startswith('head'):
-                    if val == '__NEXT_PLACEHOLDER':
-                        i = w.getInsertPoint()
-                        if i &gt; 0:
-                            w.delete(i - 1)
-                            p.h = w.getAllText()
-                    # Do not call c.endEditing here.
+                if val == '__NEXT_PLACEHOLDER':
+                    i = w.getInsertPoint()
+                    if i &gt; 0:
+                        w.delete(i - 1)
+                        p.h = w.getAllText()
+                # Do not call c.endEditing here.
                 break
         else:
             if trace and verbose:
@@ -289,19 +310,16 @@
             if self.save_ins:
                 ins = self.save_ins
                 sel1, sel2 = self.save_sel
-                if sel1 == sel2:
-                    # New in Leo 5.5
-                    self.post_pass()
-                else:
-                    # some abbreviations *set* the selection range
-                    # so only restore non-empty ranges
-                    w.setSelectionRange(sel1, sel2, insert=ins)
+                w.setSelectionRange(sel1, sel2, insert=ins)
         return True
-    #@+node:ekr.20161121121636.1: *4* abbrev.exec_content
+
+    # @+node:ekr.20161121121636.1: *4* abbrev.exec_content
     def exec_content(self, content: str) -&gt; None:
         """Execute the content in the environment, and return the result."""
-    #@+node:ekr.20150514043850.12: *4* abbrev.expand_text
-    def expand_text(self,
+
+    # @+node:ekr.20150514043850.12: *4* abbrev.expand_text
+    def expand_text(
+        self,
         w: Wrapper,
         i: int,
         j: int,
@@ -327,7 +345,7 @@
         else:
             self.find_place_holder(p, do_placeholder)
 
-    #@+node:ekr.20150514043850.13: *4* abbrev.expand_tree (entry) &amp; helpers
+    # @+node:ekr.20150514043850.13: *4* abbrev.expand_tree (entry) &amp; helpers
     def expand_tree(self, w: Wrapper, i: int, j: int, tree_s: str, word: str) -&gt; None:
         """
         Paste tree_s as children of c.p.
@@ -352,7 +370,8 @@
         for p in old_p.subtree():
             if self.find_place_holder(p, do_placeholder):
                 break
-    #@+node:ekr.20150514043850.17: *5* abbrev.paste_tree
+
+    # @+node:ekr.20150514043850.17: *5* abbrev.paste_tree
     def paste_tree(self, old_p: Position, s: str) -&gt; None:
         """Paste the tree corresponding to s (xml) into the tree."""
         c = self.c
@@ -367,7 +386,8 @@
             c.redraw(old_p)  # 2017/02/27: required.
         else:
             g.trace('paste failed')
-    #@+node:ekr.20150514043850.14: *4* abbrev.find_place_holder
+
+    # @+node:ekr.20150514043850.14: *4* abbrev.find_place_holder
     def find_place_holder(self, p: Position, do_placeholder: bool) -&gt; bool:
         """
         Search for the next place-holder.
@@ -410,10 +430,11 @@
             c.bodyWantsFocusNow()
             return True
         # #453: do nothing here.
-            # c.frame.body.forceFullRecolor()
-            # c.bodyWantsFocusNow()
+        # c.frame.body.forceFullRecolor()
+        # c.bodyWantsFocusNow()
         return False
-    #@+node:ekr.20150514043850.15: *4* abbrev.make_script_substitutions
+
+    # @+node:ekr.20150514043850.15: *4* abbrev.make_script_substitutions
     def make_script_substitutions(self, i: int, j: int, val: str) -&gt; tuple[str, bool]:
         """Make scripting substitutions in node p."""
         c = self.c
@@ -457,32 +478,35 @@
             do_placeholder = False
             c.p.v.b = w.getAllText()
         return val, do_placeholder
-    #@+node:ekr.20161121102113.1: *4* abbrev.make_script_substitutions_in_headline
-    def make_script_substitutions_in_headline(self, p: Position) -&gt; bool:
-        """Make scripting substitutions in p.h."""
-        c = self.c
-        p = c.p
-        pattern = re.compile(r'^(.*)%s(.+)%s(.*)$' % (
-            re.escape(c.abbrev_subst_start),
-            re.escape(c.abbrev_subst_end),
-        ))
-        changed = False
-        # Perform at most one scripting substitution.
-        if m := pattern.match(p.h):
+
+    # @+node:ekr.20161121102113.1: *4* abbrev.make_script_substitutions_in_headline
+    def make_script_substitutions_in_headline(self, i: int, p: Position, val: str) -&gt; bool:
+        """Make the first scripting substitution in p.h."""
+        c = self.c
+        c.endEditing()
+        pattern = re.compile(
+            r'^(.*)%s(.+)%s(.*)$'
+            % (
+                re.escape(c.abbrev_subst_start),
+                re.escape(c.abbrev_subst_end),
+            )
+        )
+        if m := pattern.match(val):
             content = m.group(2)
             c.abbrev_subst_env['x'] = ''
             try:
                 exec(content, c.abbrev_subst_env, c.abbrev_subst_env)
                 x = c.abbrev_subst_env.get('x')
                 if x:
-                    p.h = f"{m.group(1)}{x}{m.group(3)}"
-                    changed = True
+                    p.h = f"{p.h[:i]}{m.group(1)}{x}{m.group(3)}"
+                    return True
             except Exception:
                 # Leave p.h alone.
                 g.trace('scripting error in', p.h)
                 g.es_exception()
-        return changed
-    #@+node:ekr.20161121112837.1: *4* abbrev.match_prefix
+        return False
+
+    # @+node:ekr.20161121112837.1: *4* abbrev.match_prefix
     def match_prefix(self, ch: str, i: int, j: int, prefix: str, s: str) -&gt; tuple[int, str, str, str]:
         """A match helper."""
         i = j - len(prefix)
@@ -505,7 +529,8 @@
             i -= 1
             word, val = None, None
         return i, tag, word, val
-    #@+node:ekr.20150514043850.16: *4* abbrev.next_place
+
+    # @+node:ekr.20150514043850.16: *4* abbrev.next_place
     def next_place(self, s: str, offset: int = 0) -&gt; tuple[str, int, int]:
         """
         Given string s containing a placeholder like &lt;| block |&gt;,
@@ -526,18 +551,12 @@
             return s, None, None
         start = new_pos
         place_holder_delim = s[new_pos : new_end + len(c.abbrev_place_end)]
-        place_holder = place_holder_delim[
-            len(c.abbrev_place_start) : -len(c.abbrev_place_end)]
+        place_holder = place_holder_delim[len(c.abbrev_place_start) : -len(c.abbrev_place_end)]
         s2 = s[:start] + place_holder + s[start + len(place_holder_delim) :]
         end = start + len(place_holder)
         return s2, start, end
-    #@+node:ekr.20161121114504.1: *4* abbrev.post_pass
-    def post_pass(self) -&gt; None:
-        """The post pass: make script substitutions in all headlines."""
-        if self.root:
-            for p in self.root.self_and_subtree():
-                self.make_script_substitutions_in_headline(p)
-    #@+node:ekr.20150514043850.18: *4* abbrev.replace_selection
+
+    # @+node:ekr.20150514043850.18: *4* abbrev.replace_selection
     def replace_selection(self, w: Wrapper, i: int, j: int, s: str) -&gt; None:
         """Replace w[i:j] by s."""
         p, u = self.c.p, self.c.undoer
@@ -563,7 +582,8 @@
             delta = len(s) - len(abbrev)
             self.save_sel = i + delta, j + delta
             self.save_ins = ins + delta
-    #@+node:ekr.20161121111502.1: *4* abbrev_get_ch
+
+    # @+node:ekr.20161121111502.1: *4* abbrev_get_ch
     def get_ch(self, event: LeoKeyEvent, stroke: g.KeyStroke, w: Wrapper) -&gt; str:
         """Get the ch from the stroke."""
         ch = g.checkUnicode(event and event.char or '')
@@ -578,17 +598,15 @@
         if stroke:
             ch = d.get(stroke.s, stroke.s)
             if len(ch) &gt; 1:
-                if (stroke.find('Ctrl+') &gt; -1 or
-                    stroke.find('Alt+') &gt; -1 or
-                    stroke.find('Meta+') &gt; -1
-                ):
+                if stroke.find('Ctrl+') &gt; -1 or stroke.find('Alt+') &gt; -1 or stroke.find('Meta+') &gt; -1:
                     ch = ''
                 else:
                     ch = event.char if event else ''
         else:
             ch = event.char
         return ch
-    #@+node:ekr.20161121112346.1: *4* abbrev_get_prefixes
+
+    # @+node:ekr.20161121112346.1: *4* abbrev_get_prefixes
     def get_prefixes(self, w: Wrapper) -&gt; tuple[str, int, int, list[str]]:
         """Return the prefixes at the current insertion point of w."""
         # New code allows *any* sequence longer than 1 to be an abbreviation.
@@ -603,8 +621,9 @@
         if '' not in prefixes:
             prefixes.append('')
         return s, i, j, prefixes
-    #@+node:ekr.20150514043850.19: *3* abbrev.dynamic abbreviation...
-    #@+node:ekr.20150514043850.20: *4* abbrev.dynamicCompletion C-M-/
+
+    # @+node:ekr.20150514043850.19: *3* abbrev.dynamic abbreviation...
+    # @+node:ekr.20150514043850.20: *4* abbrev.dynamicCompletion C-M-/
     @cmd('dabbrev-completion')
     def dynamicCompletion(self, event: LeoKeyEvent = None) -&gt; None:
         """
@@ -638,7 +657,8 @@
             w.setYScrollPosition(ypos)
             c.undoer.afterChangeNodeContents(p, command='dabbrev-completion', bunch=b)
             c.recolor()
-    #@+node:ekr.20150514043850.21: *4* abbrev.dynamicExpansion M-/ &amp; helper
+
+    # @+node:ekr.20150514043850.21: *4* abbrev.dynamicExpansion M-/ &amp; helper
     @cmd('dabbrev-expands')
     def dynamicExpansion(self, event: LeoKeyEvent = None) -&gt; None:
         """
@@ -666,8 +686,10 @@
         prefix = functools.reduce(g.longestCommonPrefix, aList)
         prefix = prefix.strip()
         self.dynamicExpandHelper(event, prefix, aList, w)
-    #@+node:ekr.20150514043850.22: *5* abbrev.dynamicExpandHelper
-    def dynamicExpandHelper(self,
+
+    # @+node:ekr.20150514043850.22: *5* abbrev.dynamicExpandHelper
+    def dynamicExpandHelper(
+        self,
         event: LeoKeyEvent,
         prefix: str = None,
         aList: list[str] = None,
@@ -709,7 +731,8 @@
             w.setYScrollPosition(ypos)
             c.undoer.afterChangeNodeContents(p, command='dabbrev-expand', bunch=b)
             c.recolor()
-    #@+node:ekr.20150514043850.23: *4* abbrev.getDynamicList (helper)
+
+    # @+node:ekr.20150514043850.23: *4* abbrev.getDynamicList (helper)
     def getDynamicList(self, w: Wrapper, s: str) -&gt; list[str]:
         """Return a list of dynamic abbreviations."""
         if self.globalDynamicAbbrevs:
@@ -722,8 +745,9 @@
             items = self.dynaregex.findall(w.getAllText())
         items = sorted(set([z for z in items if z.startswith(s)]))
         return items
-    #@+node:ekr.20150514043850.24: *3* abbrev.static abbrevs
-    #@+node:ekr.20150514043850.25: *4* abbrev.addAbbrevHelper
+
+    # @+node:ekr.20150514043850.24: *3* abbrev.static abbrevs
+    # @+node:ekr.20150514043850.25: *4* abbrev.addAbbrevHelper
     def addAbbrevHelper(self, s: str, tag: str = '') -&gt; None:
         """Enter the abbreviation 's' into the self.abbrevs dict."""
         if not s.strip():
@@ -737,19 +761,30 @@
             if val.endswith('\n'):
                 val = val[:-1]
             val = self.n_regex.sub('\n', val).replace('\\\\n', '\\n')
-            old, tag = d.get(name, (None, None),)
+            old, tag = d.get(
+                name,
+                (None, None),
+            )
             if old and old != val and not g.unitTesting:
-                g.es_print('redefining abbreviation', name,
-                    '\nfrom', repr(old), 'to', repr(val))
+                g.es_print(
+                    'redefining abbreviation',
+                    name,
+                    '\nfrom',
+                    repr(old),
+                    'to',
+                    repr(val),
+                )
             d[name] = val, tag
         except ValueError:
             g.es_print(f"bad abbreviation: {s}")
-    #@+node:ekr.20150514043850.28: *4* abbrev.killAllAbbrevs
+
+    # @+node:ekr.20150514043850.28: *4* abbrev.killAllAbbrevs
     @cmd('abbrev-kill-all')
     def killAllAbbrevs(self, event: LeoKeyEvent) -&gt; None:
         """Delete all abbreviations."""
         self.abbrevs = {}
-    #@+node:ekr.20150514043850.29: *4* abbrev.listAbbrevs
+
+    # @+node:ekr.20150514043850.29: *4* abbrev.listAbbrevs
     @cmd('abbrev-list')
     def listAbbrevs(self, event: LeoKeyEvent = None) -&gt; None:
         """List all abbreviations."""
@@ -766,7 +801,8 @@
                 g.es_print('', f"{tag}{name}={val}")
         else:
             g.es_print('No present abbreviations')
-    #@+node:ekr.20150514043850.32: *4* abbrev.toggleAbbrevMode
+
+    # @+node:ekr.20150514043850.32: *4* abbrev.toggleAbbrevMode
     @cmd('toggle-abbrev-mode')
     def toggleAbbrevMode(self, event: LeoKeyEvent = None) -&gt; None:
         """Toggle abbreviation mode."""
@@ -775,6 +811,9 @@
         k.keyboardQuit()
         if not g.unitTesting and not g.app.batchMode:
             g.es('Abbreviations are ' + 'on' if k.abbrevOn else 'off')
-    #@-others
-#@-others
-#@-leo
+
+    # @-others
+
+
+# @-others
+# @-leo
@language python
'''
)</t>
<t tx="ekr.20260116001413.1">g.cls()
from leo.commands import editFileCommands as efc

# Any branch or rev is valid.
efc.GitDiffController(c).summary_diff_two_revs(
    rev1='main',    # Old
    rev2='6.8.8',     # New
    path='leo/commands',  # Limit diffs to this directory, relative to the nearest git repo.
)  # fmt: skip
</t>
<t tx="ekr.20260503052547.1">from leo.commands import editFileCommands as efc

efc.GitDiffController(c).diff_two_revs(
    rev1='main',  # Old
    rev2='devel',  # New
    # Optional path, relative to the git directory.
    # path='leo/core',
)
</t>
<t tx="ekr.20260503063616.1"></t>
<t tx="ekr.20260503063649.1"></t>
<t tx="ekr.20260503063747.1">from leo.commands import editFileCommands as efc

efc.GitDiffController(c).diff_two_revs(
    rev1='main',  # Old
    rev2='6.8.9',  # New
    # Optional path, relative to the git directory.
    # path='leo/core',
)
</t>
<t tx="ekr.20260508180923.1">g.cls()
import os
import leo.commands.editFileCommands as efc

path = g.finalize_join(g.app.loadDir, '..', '..')
# print(f"os.chdir({path})")
os.chdir(path)

# Any revspec is valid as an argument to the "branch1" and "branch2" args.
# See https://git-scm.com/book/en/v2/Git-Tools-Revision-Selection

efc.GitDiffController(c).diff_two_branches(
    branch1='6.8.7',  # old branch/rev
    branch2='devel',  # new branch/rev
    fn='leo/commands/abbrevCommands.py',  # Don't use back slashes.
)
</t>
<t tx="ekr.20260526171943.1"></t>
<t tx="ekr.20260803125533.1">@g.command('find-todo')
@g.command('todo-find')
def find_todo(event: LeoKeyEvent) -&gt; None:
    c = event['c']
    if hasattr(c, 'cleo'):
        c.cleo.find_todo(c.p)
        c.redraw()


</t>
<t tx="tbnorth.20170925093004.1">def _date(self, timestamp: str = '') -&gt; dt.date | None:
    """_date - convert a string to a date

    :param timestamp: date to convert
    :return: datetime.date or None.
    """
    if not timestamp.strip():
        return None  # pragma: no cover
    try:
        return dt.datetime.fromisoformat(timestamp).date()
    except ValueError:
        return None  # pragma: no cover

def _time(self, timestamp: str = '') -&gt; dt.time | None:
    """_time - convert a string to a time

    :param timestamp: time to convert
    :return: datetime.time or None.
    """
    if not timestamp.strip():
        return None  # pragma: no cover
    try:
        return dt.datetime.fromisoformat(timestamp).time()
    except ValueError:
        return None  # pragma: no cover

</t>
<t tx="tbrown.20090119215428.10">priorities: dict[int, dict[str, str]] = {
    1: {'long': 'Urgent', 'short': '1', 'icon': 'pri1.png'},
    2: {'long': 'Very High', 'short': '2', 'icon': 'pri2.png'},
    3: {'long': 'High', 'short': '3', 'icon': 'pri3.png'},
    4: {'long': 'Medium', 'short': '4', 'icon': 'pri4.png'},
    5: {'long': 'Low', 'short': '5', 'icon': 'pri5.png'},
    6: {'long': 'Very Low', 'short': '6', 'icon': 'pri6.png'},
    7: {'long': 'Sometime', 'short': '7', 'icon': 'pri7.png'},
    8: {'long': 'Level 8', 'short': '8', 'icon': 'pri8.png'},
    9: {'long': 'Level 9', 'short': '9', 'icon': 'pri9.png'},
    10: {'long': 'Level 0', 'short': '0', 'icon': 'pri0.png'},
    19: {'long': 'To do', 'short': 'o', 'icon': 'chkboxblk.png'},
    20: {'long': 'Bang', 'short': '!', 'icon': 'bngblk.png'},
    21: {'long': 'Cross', 'short': 'X', 'icon': 'xblk.png'},
    22: {'long': '(cross)', 'short': 'x', 'icon': 'xgry.png'},
    23: {'long': 'Query', 'short': '?', 'icon': 'qryblk.png'},
    24: {'long': 'Bullet', 'short': '-', 'icon': 'bullet.png'},
    100: {'long': 'Done', 'short': 'D', 'icon': 'chkblk.png'},
}

todo_priorities = 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 19

_date_fields = ['created', 'date', 'duedate', 'nextworkdate', 'prisetdate']
_time_fields = ['duetime', 'nextworktime', 'time']
_datetime_fields = _date_fields + _time_fields
</t>
<t tx="tbrown.20090119215428.11">def __init__(self, c: Cmdr) -&gt; None:
    """ctor for todoController class."""
    self.c = c
    c.cleo = self
    self.donePriority = 100
    self.menuicons: dict[int | str, QtGui.QIcon] = {}
    self.recentIcons: list[int | str] = []  # PR #4840: was list[QtGui.QIcon] (!)
    self.redrawLevels = 0
    self._widget_to_style: Any | None = None  # see updateStyle()
    self.reloadSettings()
    self.handlers: list[tuple[str, Any]] = [
        ("close-frame", self.close),
        ('select3', self.updateUI),
        ('save2', self.loadAllIcons),
        ('idle', self.updateStyle),
    ]
    # chdir so the Icons can be located, needed for uic resources
    owd = os.getcwd()
    os.chdir(g.os_path_join(g.app.loadDir, '..', 'plugins'))
    self.ui = todoQtUI(self)
    os.chdir(owd)
    for i in self.handlers:
        g.registerHandler(i[0], i[1])  # type:ignore
    self.loadAllIcons()
    # correct spinTime suffix:
    self.ui.UI.spinTime.setSuffix(" " + self.time_name)
    # #1591: patch labels if necessary.
    self.patch_1591()

</t>
<t tx="tbrown.20090119215428.12">def reloadSettings(self) -&gt; None:
    c = self.c
    c.registerReloadSettings(self)
    self.time_name = c.config.getString('todo-time-name') or 'days'
    self.icon_location = c.config.getString('todo-icon-location') or 'beforeHeadline'
    self.prog_location = c.config.getString('todo-prog-location') or 'beforeHeadline'
    self.icon_order = c.config.getString('todo-icon-order') or 'pri-first'

</t>
<t tx="tbrown.20090119215428.13"># mypy complains about missing 'self' arg.
# pylint: disable=no-self-argument
def redrawer(fn: Callable) -&gt; Callable:  # type:ignore
    """decorator for methods which create the need for a redraw"""

    def todo_redrawer_callback(self: Any, *args: Any, **kargs: Any) -&gt; Any:
        self.redrawLevels += 1
        try:
            self.c.endEditing()  # #3932.
            ans = fn(self, *args, **kargs)  # pylint: disable=not-callable
        finally:
            self.redrawLevels -= 1
            if self.redrawLevels == 0:
                self.updateUI()
        return ans

    return todo_redrawer_callback

</t>
<t tx="tbrown.20090119215428.14"># mypy complaints there is no 'self' argument.
def projectChanger(fn: Callable) -&gt; Callable:  # type:ignore
    """decorator for methods which change projects"""

    # pylint: disable=no-self-argument
    def project_changer_callback(self, *args: Any, **kargs: Any) -&gt; Any:
        # g.trace(f"{fn=} {g.callers()=}")
        ans = fn(self, *args, **kargs)  # pylint: disable=not-callable
        self.update_project()
        return ans

    return project_changer_callback

</t>
<t tx="tbrown.20090119215428.15">@redrawer
def loadAllIcons(self, tag: str = '', k: int | None = None, clear: bool = False) -&gt; None:
    """Load icons to represent cleo state"""
    for p in self.c.all_positions():
        self.loadIcons(p, clear=clear)

</t>
<t tx="tbrown.20090119215428.16">@redrawer
def loadIcons(self, p: Position, clear: bool = False) -&gt; None:
    c = self.c
    editCommands = c.editCommands
    allIcons = editCommands.getIconList(p.v)
    icons = [i for i in allIcons if 'cleoIcon' not in i]
    if self.icon_order == 'pri-first':
        iterations = ['priority', 'progress', 'duedate']
    else:
        iterations = ['progress', 'priority', 'duedate']  # pragma: no cover
    if clear:
        iterations = []
    today = dt.datetime.now(tz=dt.timezone.utc).date()  # PR #4841
    for which in iterations:
        if which == 'priority':
            pri = self.getat(p.v, 'priority')
            if pri:
                pri = int(pri)
            if pri in self.priorities:
                editCommands.appendImageDictToList(
                    icons,
                    g.os_path_join('cleo', self.priorities[pri]['icon']),
                    2,
                    on='vnode',
                    cleoIcon='1',
                    where=self.icon_location,
                )
                # Icon location defaults to 'beforeIcon' unless cleo_icon_location global defined.
                # Example: @strings[beforeIcon,beforeHeadline] cleo_icon_location = beforeHeadline
        elif which == 'progress':
            prog = self.getat(p.v, 'progress')
            # pylint: disable=literal-comparison
            if prog != '':
                prog = int(prog or 0)
                use = prog // 10 * 10
                use = 'prg%03d.png' % use  # type:ignore
                editCommands.appendImageDictToList(
                    icons,
                    g.os_path_join('cleo', use),
                    2,
                    on='vnode',
                    cleoIcon='1',
                    where=self.prog_location,
                )
        elif which == 'duedate':
            duedate = self.getat(p.v, 'duedate')
            nextworkdate = self.getat(p.v, 'nextworkdate')
            icondate = min(  # PR #4841
                duedate or NO_TIME,
                nextworkdate.date() if nextworkdate else NO_TIME
            )  # fmt: skip
            if icondate != NO_TIME:
                if icondate &lt; today:
                    icon = "date_past.png"
                elif icondate == today:
                    icon = "date_today.png"
                else:
                    icon = "date_future.png"
                # Append the icon to the icons list.
                editCommands.appendImageDictToList(
                    icons, g.os_path_join('cleo', icon), 2,
                    on='vnode',
                    cleoIcon='1',
                    where=self.prog_location,
                )  # fmt: skip
    # Set the p.v.u for the icons.
    editCommands.setIconList(p, icons)
    p.v.updateIcon()  # #2870.

</t>
<t tx="tbrown.20090119215428.17">def close(self, tag: str, d: dict) -&gt; None:
    "unregister handlers on closing commander"
    if self.c == d.get('c'):
        for tag, func in self.handlers:
            g.unregisterHandler(tag, func)

</t>
<t tx="tbrown.20090119215428.18">def showHelp(self) -&gt; None:
    g.es('Check the Plugins menu Todo entry')

</t>
<t tx="tbrown.20090119215428.19">@
annotate was the previous name of this plugin, which is why the default values
for several keyword args is 'annotate'.
</t>
<t tx="tbrown.20090119215428.2">  # PR #4845

&lt;&lt; todo docstring &gt;&gt;
# TNB: derived from cleo.py.

&lt;&lt; todo imports &amp; annotations &gt;&gt;

NO_TIME = dt.date(3000, 1, 1)

@others
@language python
@tabwidth -4
</t>
<t tx="tbrown.20090119215428.20">def delUD(self, node: VNode, udict: str = "annotate") -&gt; None:
    """Remove our dict from the node"""
    if hasattr(node, "unknownAttributes") and udict in node.unknownAttributes:
        del node.unknownAttributes[udict]

</t>
<t tx="tbrown.20090119215428.21">def hasUD(self, node: VNode, udict: str = "annotate") -&gt; bool:
    """Return True if the node has an UD."""
    return (
        hasattr(node, "unknownAttributes")
        and udict in node.unknownAttributes
        and isinstance(node.unknownAttributes.get(udict), dict)
    )

</t>
<t tx="tbrown.20090119215428.22">def getat(self, node: VNode, attrib: str) -&gt; Any:  # Hard to annotate.
    "new attribute getter"
    if (
        hasattr(node, 'unknownAttributes')
        and "annotate" in node.unknownAttributes
        and isinstance(node.unknownAttributes["annotate"], dict)
        and attrib in node.unknownAttributes["annotate"]
    ):
        x: Any = node.unknownAttributes["annotate"][attrib]
        ### g.trace(f"{x=}")
        if attrib in self._date_fields and isinstance(x, str):
            x = self._date(x)
        if attrib in self._time_fields and isinstance(x, str):
            x = self._time(x)
        return x
    return 9999 if attrib == "priority" else ''

</t>
<t tx="tbrown.20090119215428.23">def testDefault(self, attrib: str, val: Any) -&gt; bool:
    "return true if val is default val for attrib"
    # pylint: disable=consider-using-ternary
    return attrib == "priority" and val == 9999 or val == ""

</t>
<t tx="tbrown.20090119215428.24">def setat(self, node: VNode, attrib: Any, val: Any) -&gt; None:
    "new attribute setter"

    c = self.c

    if attrib in self._datetime_fields and isinstance(val, (dt.date, dt.time, dt.datetime)):
        val = val.isoformat()

    if 'annotate' in node.u and 'src_unl' in node.u['annotate']:
        if not hasattr(node, '_cached_src_vnode') or not node._cached_src_vnode:
            src_unl = node.u['annotate']['src_unl']
            c1 = c
            p1 = c1.vnode2position(node)
            c2, p2 = self.unl_to_pos(src_unl, p1)
            if p2 is None:
                g.es("Failed to access '%s' for attribute update." % src_unl)
            else:
                node._cached_src_c = c2
                node._cached_src_vnode = p2.v

        # if the above succeeded in getting the required attributes
        if hasattr(node, '_cached_src_vnode') and node._cached_src_vnode:
            node._cached_src_c.cleo.setat(node._cached_src_vnode, attrib, val)
            op = node._cached_src_c.vnode2position(node._cached_src_vnode)
            node._cached_src_c.cleo.loadIcons(op)
            node._cached_src_c.cleo.updateUI(k={'c': node._cached_src_c})
            node._cached_src_c.setChanged()

    isDefault = self.testDefault(attrib, val)

    if (
        not hasattr(node, 'unknownAttributes')
        or "annotate" not in node.unknownAttributes
        or not isinstance(node.unknownAttributes["annotate"], dict)
    ):
        # dictionary doesn't exist
        if isDefault:
            return  # don't create dict. for default value
        if not hasattr(node, 'unknownAttributes'):  # node has no unknownAttributes
            node.unknownAttributes = {}
            node.unknownAttributes["annotate"] = {}
        elif "annotate" not in node.unknownAttributes or not isinstance(
            node.unknownAttributes["annotate"], dict
        ):
            node.unknownAttributes["annotate"] = {}
        # node.unknownAttributes["annotate"]['created'] = datetime.datetime.now()
        node.unknownAttributes["annotate"][attrib] = val
        return

    # dictionary exists
    if (
        attrib not in node.unknownAttributes["annotate"]
        or node.unknownAttributes["annotate"][attrib] != val
    ):
        c.setChanged()
        node.setDirty()

    node.unknownAttributes["annotate"][attrib] = val

    if isDefault:  # check if all default, if so drop dict.
        self.dropEmpty(node)  ###, dictOk=True)

</t>
<t tx="tbrown.20090119215428.25">def dropEmpty(self, v: VNode) -&gt; bool:
    if (
        hasattr(v, 'unknownAttributes')
        and "annotate" in v.unknownAttributes
        and isinstance(v.unknownAttributes["annotate"], dict)
    ):
        isDefault = True
        for key, value in v.unknownAttributes["annotate"].items():
            if not self.testDefault(key, value):
                isDefault = False
                break
        if isDefault:  # no non-defaults seen, drop the whole cleo dictionary
            del v.unknownAttributes["annotate"]
            self.c.setChanged()
            return True
    return False

</t>
<t tx="tbrown.20090119215428.27"></t>
<t tx="tbrown.20090119215428.29">@redrawer
def clear_all(self) -&gt; None:
    for p in self.c.all_unique_positions():
        self.delUD(p.v)
        self.loadIcons(p)
        self.show_times(p)

@redrawer
def clear_node(self) -&gt; None:
    p = self.c.p
    self.delUD(p.v)
    self.loadIcons(p)
    self.show_times(p)

@redrawer
def clear_subtree(self) -&gt; None:
    for p in self.c.p.self_and_subtree():
        self.delUD(p.v)
        self.loadIcons(p)
        self.show_times(p)

</t>
<t tx="tbrown.20090119215428.3">"""Provides to-do list and simple task management.

This plugin adds time required, progress and priority settings for nodes. With
the @project tag a branch can display progress and time required with dynamic
hierarchical updates.

The Task Tab
============

The plugin creates a "Task" Tab in the log pane.  It looks like this:

    .. image:: ../Icons/cleo/LeoTaskTab.png

Along the top are icons that you can associate with nodes.
Just click on the icon: it will appear on the presently selected node.

Next are a set of fields that allow you to associate **due dates** and
**completion times** with nodes. The @setting @data todo_due_date_offsets lists
date offsets, +n -n days from now, or &lt;n &gt;n to subtract / add n days to existing
date.

Clicking on the Button named "Menu" reveals submenus.

For full details, see http://leo.zwiki.org/Tododoc

Icons
=====

The plugin uses icons in the leo/Icons/cleo folder. These icons are generated
from the file cleo_icons.svg in the same directory. You may replace the PNG
images with any others you wish.

@Settings
=========

Most setting documented elsewhere (http://leo.zwiki.org/Tododoc).

todo_compact_interface
  Hide one line of the interface to preserve original height
todo_icon_location
  "beforeHeadline", "afterHeadline" might also work
todo_due_date_offsets
  A list of offsets like "+7" or "&lt;3" or "&gt;5", for 7 days from now,
  3 days earlier, or 5 days later
todo_calendar_n
  Number of months to display at once in calendar pop up, default 3
todo_calendar_cols
  Number of columns to use when displaying multiple months in
  in calendar pop up, default 3 - extra rows are used as needed to
  display `todo_calendar_n` months.


"""


</t>
<t tx="tbrown.20090119215428.30"></t>
<t tx="tbrown.20090119215428.31">@redrawer
@projectChanger
def progress_clear(self) -&gt; None:
    self.setat(self.c.p.v, 'progress', '')

</t>
<t tx="tbrown.20090119215428.32">@redrawer
@projectChanger
def set_progress(self, val: str | int = '') -&gt; None:
    c = self.c
    self.setat(c.p.v, 'progress', val)

</t>
<t tx="tbrown.20090119215428.33">@redrawer
@projectChanger
def set_time_req(self, val: str | int = '') -&gt; None:
    c = self.c
    v = c.p.v
    self.setat(v, 'time_req', val)
    if self.getat(v, 'progress') == '':
        self.setat(v, 'progress', 0)

</t>
<t tx="tbrown.20090119215428.34">@redrawer
def show_times(self, p: Position = None, *, show: bool = False) -&gt; None:
    def rnd(x: float) -&gt; str:
        return re.sub('.0$', '', '%.1f' % x)

    if p is None:
        p = self.c.currentPosition()

    for nd in p.self_and_subtree():
        new_h = re.sub(' &lt;[^&gt;]*&gt;$', '', nd.headString())
        if new_h != nd.h:  # PR #4840: Don't mark nodes dirty unless they change!
            nd.h = new_h
        tr = self.getat(nd.v, 'time_req')
        pr = self.getat(nd.v, 'progress')
        try:
            pr = float(pr)
        except Exception:  # pragma: no cover
            pr = ''
        if tr != '' or pr != '':
            ans = ' &lt;'
            if tr != '':
                if pr == '' or pr == 0 or pr == 100:
                    ans += rnd(tr) + ' ' + self.time_name
                else:
                    ans += '%s+%s=%s %s' % (
                        rnd(pr / 100.0 * tr),
                        rnd((1 - pr / 100.0) * tr),
                        rnd(tr),
                        self.time_name,
                    )
                if pr != '':
                    ans += ', '
            if pr != '':
                ans += rnd(pr) + '%'  # pr may be non-integer if set by recalc_time
            ans += '&gt;'

            if show:
                nd.h = nd.h + ans
            self.loadIcons(nd)  # update progress icon

</t>
<t tx="tbrown.20090119215428.35">def recalc_time(self, p: Position, clear: Position | None = None) -&gt; tuple[str, str]:
    assert isinstance(p, Position), repr(p)
    assert isinstance(clear, (Position, NoneType)), repr(clear)
    v = p.v
    time_totl: str | None = None
    time_done: str | None = None

    # get values from children, if any
    for cn in p.children():
        ans = self.recalc_time(cn, clear)
        if time_totl is None:
            time_totl = ans[0]
        else:
            if ans[0] is not None:
                time_totl += ans[0]

        if time_done is None:
            time_done = ans[1]
        else:
            if ans[1] is not None:
                time_done += ans[1]

    if time_totl is not None:  # some value returned
        if clear:  # then we should just clear our values
            self.setat(v, 'progress', '')
            self.setat(v, 'time_req', '')
            return (time_totl, time_done)

        if time_done is not None:  # some work done
            # can't round derived progress without getting bad results form show_times
            if time_totl == 0:
                pr = 0.0
            else:
                pr = float(time_done) / float(time_totl) * 100.0
            self.setat(v, 'progress', pr)
        else:
            self.setat(v, 'progress', 0)
        self.setat(v, 'time_req', time_totl)
    else:  # no values from children, use own
        tr = self.getat(v, 'time_req')
        pr = self.getat(v, 'progress')
        if tr != '':
            time_totl = tr
            if pr != '':
                time_done = float(pr) / 100.0 * tr
            else:
                self.setat(v, 'progress', 0)

    return (time_totl, time_done)

</t>
<t tx="tbrown.20090119215428.36">@redrawer
@projectChanger
def clear_time_req(self) -&gt; None:
    c = self.c
    self.setat(c.p.v, 'time_req', '')

</t>
<t tx="tbrown.20090119215428.37">@redrawer
def update_project(self, p: Position = None) -&gt; None:
    """
    Find highest parent with '@project' in headline and run recalc_time
    and maybe show_times (if headline has '@project time')
    """

    if p is None:
        p = self.c.currentPosition()
    project: Position | None = None

    for nd in p.self_and_parents():
        if nd.headString().find('@project') &gt; -1:
            project = nd.copy()

    if project:
        self.recalc_time(p, project)
        if project.headString().find('@project time') &gt; -1:
            self.show_times(project, show=True)
        else:
            self.show_times(p, show=True)
    else:
        self.show_times(p, show=False)

</t>
<t tx="tbrown.20090119215428.38">@redrawer
def local_recalc(self) -&gt; None:
    self.recalc_time(self.c.p)

</t>
<t tx="tbrown.20090119215428.39">@redrawer
def local_clear(self) -&gt; None:
    self.recalc_time(self.c.p)

</t>
<t tx="tbrown.20090119215428.4">from __future__ import annotations
from collections.abc import Callable
import os
import re
import datetime as dt
import time
from types import NoneType
from typing import Any, TYPE_CHECKING
from leo.core import leoGlobals as g
from leo.core.leoNodes import Position
from leo.core.leoQt import Qt, QtCore, QtGui, QtWidgets, uic
from leo.core.leoQt import Checked, Unchecked

if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoGui import LeoKeyEvent
    from leo.core.leoNodes import VNode

# May raise g.UiTypeException, caught by the plugins manager.
g.assertUi('qt')
</t>
<t tx="tbrown.20090119215428.40"></t>
<t tx="tbrown.20090119215428.41">@redrawer
def childrenTodo(self, p: Position = None) -&gt; None:
    if p is None:
        p = self.c.currentPosition()
    for p in p.children():
        if self.getat(p.v, 'priority') != 9999:
            continue
        self.setat(p.v, 'priority', 19)
        self.loadIcons(p)

</t>
<t tx="tbrown.20090119215428.42">@redrawer
def find_todo(self, p: Position = None, stage: int = 0) -&gt; bool:
    """Recursively find the next todo"""

    # search is like XPath 'following' axis, all nodes after p in document order.
    # returning True should always propogate all the way back up to the top
    # stages: 0 - user selected start node,
    #         1 - search siblings, parents siblings,
    #         2 - searching children
    if p is None:
        p = self.c.currentPosition()

    # see if this node is a todo
    if stage != 0 and self.needs_doing(p.v):
        if p.getParent():
            self.c.selectPosition(p.getParent())
            self.c.expandNode()
        self.c.selectPosition(p)
        return True

    for nd in p.children():
        if self.find_todo(nd, stage=2):
            return True

    if stage &lt; 2 and p.getNext():
        if self.find_todo(p.getNext(), stage=1):
            return True

    if stage &lt; 2 and p.getParent() and p.getParent().getNext():
        if self.find_todo(p.getParent().getNext(), stage=1):
            return True

    if stage == 0:
        g.es("None found")

    return False

</t>
<t tx="tbrown.20090119215428.43">def prikey(self, v: VNode) -&gt; int:
    """key function for sorting by priority"""
    # getat returns 9999 for nodes without priority, so you'll only get -1
    # if a[1] is not a node.  Or even an object.

    try:
        pa = int(self.getat(v, 'priority'))
    except ValueError:
        pa = -1

    return pa if pa != 24 else 0

</t>
<t tx="tbrown.20090119215428.44">@redrawer
def priority_clear(self, v: VNode = None) -&gt; None:
    if v is None:
        v = self.c.currentPosition().v
    self.setat(v, 'priority', 9999)
    self.loadIcons(self.c.currentPosition())

</t>
<t tx="tbrown.20090119215428.45">@redrawer
def priSort(self, p: Position = None) -&gt; None:
    if p is None:
        p = self.c.currentPosition()
    self.c.selectPosition(p)
    self.c.sortSiblings(key=self.prikey)

</t>
<t tx="tbrown.20090119215428.46">@redrawer
def reclassify(self, p: Position = None) -&gt; None:
    """change priority codes"""

    if p is None:
        p = self.c.currentPosition()
    g.es('\n Current distribution:')
    self.showDist()
    dat: dict = {}
    x0: Any
    for end in 'from', 'to':
        if Qt:
            x0, ok = QtWidgets.QInputDialog.getText(
                None, 'Reclassify priority', '%s priorities (1-9,19)' % end
            )
            if not ok:
                x0 = None
            else:
                x0 = str(x0)
        else:
            x0 = g.app.gui.runAskOkCancelStringDialog(
                self.c, 'Reclassify priority', '%s priorities (1-7,19)' % end.upper()
            )
        try:
            while re.search(r'\d+-\d+', x0):
                what = re.search(r'\d+-\d+', x0).group(0)
                rng = [int(n) for n in what.split('-')]
                repl = []
                if rng[0] &gt; rng[1]:
                    for n in range(rng[0], rng[1] - 1, -1):
                        repl.append(str(n))
                else:
                    for n in range(rng[0], rng[1] + 1):
                        repl.append(str(n))
                x0 = x0.replace(what, ','.join(repl))

            x0 = [int(i) for i in x0.replace(',', ' ').split()]
        # if int(i) in self.todo_priorities]
        except Exception:  # pragma: no cover
            g.es('Not understood, no action')
            return
        if not x0:
            g.es('No action')
            return
        dat[end] = x0

    if len(dat['from']) != len(dat['to']):
        g.es('Unequal list lengths, no action')
        return

    cnt = 0
    for p in p.subtree():
        pri = int(self.getat(p.v, 'priority'))
        if pri in dat['from']:
            self.setat(p.v, 'priority', dat['to'][dat['from'].index(pri)])
            self.loadIcons(p)
            cnt += 1
    g.es('\n%d priorities reclassified, new distribution:' % cnt)
    self.showDist()

</t>
<t tx="tbrown.20090119215428.47">@redrawer
def setPri(self, priority: int) -&gt; None:
    if priority in self.recentIcons:
        self.recentIcons.remove(priority)
    self.recentIcons.insert(0, priority)
    self.recentIcons = self.recentIcons[:3]

    p = self.c.currentPosition()
    self.setat(p.v, 'priority', priority)
    self.setat(p.v, 'prisetdate', str(dt.datetime.now(tz=dt.timezone.utc)))
    self.loadIcons(p)

</t>
<t tx="tbrown.20090119215428.48">def showDist(self, p: Position = None) -&gt; None:
    """show distribution of priority levels in subtree"""
    if p is None:
        p = self.c.currentPosition()
    pris: dict = {}
    for p in p.subtree():
        pri = int(self.getat(p.v, 'priority'))
        if pri not in pris:
            pris[pri] = 1
        else:
            pris[pri] += 1
    pris_list = sorted([(k, v) for k, v in pris.items()])
    for item in pris_list:
        if item[0] in self.priorities:
            g.es(
                '%s\t%d\t%s\t(%s)'
                % (
                    self.priorities[item[0]]['short'],
                    item[1],
                    self.priorities[item[0]]['long'],
                    item[0],
                )
            )

</t>
<t tx="tbrown.20090119215428.49">def updateUI(self, tag: str = '', k: dict | None = None) -&gt; None:
    if k and k['c'] != self.c:
        return  # wrong number

    # check work date &lt; due date and do stylesheet re-evaluation stuff
    v = self.c.currentPosition().v
    nwd = self.getat(v, 'nextworkdate')
    due = self.getat(v, 'duedate')
    if hasattr(self.ui.UI, "frmDates"):
        if w := self.ui.UI.frmDates:
            if nwd and due and str(nwd) &gt; str(due):
                w.setProperty('style_class', 'tododate_error')
            else:
                w.setProperty('style_class', '')
            # update style on this widget on idle, see updateStyle()
            self._widget_to_style = (w, time.time())

    self.ui.setProgress(int(self.getat(v, 'progress') or 0))
    self.ui.setTime(float(self.getat(v, 'time_req') or 0))

    self.ui.setDueDate(self.getat(v, 'duedate'))
    # default is "", which is understood by setDueDate()
    self.ui.setDueTime(self.getat(v, 'duetime'))
    # ditto

    self.ui.setDueDate(self.getat(v, 'duedate'))
    self.ui.setDueTime(self.getat(v, 'duetime'))
    self.ui.setNextWorkDate(self.getat(v, 'nextworkdate'))
    self.ui.setNextWorkTime(self.getat(v, 'nextworktime'))
    created = self.getat(v, 'created')
    if created and isinstance(created, dt.datetime) and created.year &gt;= 1900:
        created = created.date()  # PR #4841
        self.ui.UI.createdTxt.setText(created.strftime("%d %b %y"))
        self.ui.UI.createdTxt.setToolTip(created.strftime("Created %H:%M %d %b %Y"))
    else:
        created = dt.datetime.now(tz=dt.timezone.utc).date()
        self.ui.UI.createdTxt.setText(created.strftime("Created %d %b %Y"))
        self.ui.UI.createdTxt.setToolTip(created.strftime("gnx created %H:%M %d %b %Y"))

    # Update the label.
    h = self.c and self.c.p and self.c.p.h
    due = self.getat(v, 'duedate')
    now = dt.datetime.now(tz=dt.timezone.utc).date()  # PR #4841
    ago = (now - created).days if created else 0
    if due:
        days = (due - now).days
        txt = f"{h}\nCreated {ago} days ago, due in {days}"
    else:
        txt = f"{h}\nCreated {ago} days ago"
    self.ui.UI.txtDetails.setText(txt)
    prisetdate = self.getat(v, 'prisetdate')
    self.ui.UI.txtDetails.setToolTip("Priority set %s" % (str(prisetdate).strip() or '?'))

</t>
<t tx="tbrown.20090119215428.6">warning_given = False


def init() -&gt; bool:
    """Return True if the plugin has loaded successfully."""
    global warning_given
    if warning_given:
        return False
    name = g.app.gui.guiName()
    if name != "qt":  # pragma: no cover
        warning_given = True
        if name not in ('browser', 'curses', 'nullGui'):
            print('todo.py plugin not loaded because gui is not Qt')
        return False
    if not uic:  # pragma: no cover
        warning_given = True
        print('todo.py plugin not loaded because uic can not be imported')
        return False

    g.registerHandler('after-create-leo-frame', onCreate)
    # can't use before-create-leo-frame because Qt dock's not ready
    g.plugin_signon(__name__)
    g.tree_popup_handlers.append(popup_entry)
    return True


</t>
<t tx="tbrown.20090119215428.7">def onCreate(tag: str, key: dict) -&gt; None:
    if c := key.get('c'):  # PR #4840
        todoController(c)


</t>
<t tx="tbrown.20090119215428.8">if 1:

    class todoQtUI(QtWidgets.QWidget):
        @others


</t>
<t tx="tbrown.20090119215428.9">class todoController:
    """A per-commander class that manages tasks."""

    &lt;&lt; todoController data &gt;&gt;

    @others


</t>
<t tx="tbrown.20090630144958.5318">def popup_entry(c: Cmdr, p: Position, menu: QtWidgets.QMenu) -&gt; None:
    """Add the menus for the todo.py plugin.  Called from Qt."""

    assert isinstance(menu, QtWidgets.QMenu)  # PR #4840

    if getattr(c, 'cleo', None):  # #2856.
        c.cleo.addPopupMenu(c, p, menu)


</t>
<t tx="tbrown.20090630144958.5319">def addPopupMenu(self, c: Cmdr, p: Position, menu: QtWidgets.QMenu) -&gt; None:

    assert isinstance(menu, QtWidgets.QMenu)

    def rnd(x: float) -&gt; str:  # pragma: no cover
        return re.sub('.0$', '', '%.1f' % x)

    taskmenu = menu.addMenu("Task")
    submenu = taskmenu.addMenu("Status")
    iconlist = [(menu, i) for i in self.recentIcons]
    iconlist.extend([(submenu, i) for i in self.priorities])
    for m, i in iconlist:
        icon = self.menuicon(i)
        a = m.addAction(icon, self.priorities[i]["long"])
        a.setIconVisibleInMenu(True)

        def icon_cb(checked: Any, priority: int | str = i) -&gt; None:
            self.setPri(priority)

        a.triggered.connect(icon_cb)
    submenu = taskmenu.addMenu("Progress")
    for i in range(11):
        icon = self.menuicon(10 * i, progress=True)
        a = submenu.addAction(icon, "%d%%" % (i * 10))
        a.setIconVisibleInMenu(True)

        def progress_cb(checked: bool, prog: int = i) -&gt; None:
            self.set_progress(val=10 * prog)

        a.triggered.connect(progress_cb)
    prog = self.getat(p.v, 'progress')
    if isinstance(prog, int):
        a = taskmenu.addAction("(%d%% complete)" % prog)
        a.setIconVisibleInMenu(True)
        a.enabled = False
    time_ = self.getat(p.v, 'time_req')
    if isinstance(time_, float):
        if isinstance(prog, int):
            f = prog / 100.0
            a = taskmenu.addAction(
                "(%s+%s=%s %s)"
                % (rnd(f * time_), rnd((1.0 - f) * time_), rnd(time_), self.time_name)
            )
        else:
            a = taskmenu.addAction("(%s %s)" % (rnd(time_), self.time_name))
        a.enabled = False
    todoQtUI.populateMenu(taskmenu, self)

</t>
<t tx="tbrown.20090630144958.5320">def menuicon(self, pri: int | str, progress: bool = False) -&gt; QtGui.QIcon:
    """return icon from cache, placing it there if needed"""
    key = f"prog-{pri}" if progress else pri
    # mypy doesn't know (and can't be told) that priorities[key]["icon"] is a string.
    fn: str = 'prg%03d.png' % pri if progress else self.priorities[key]["icon"]  # type:ignore
    if key not in self.menuicons:
        # use getImageImage because it's theme aware
        fn = g.os_path_join('cleo', fn)
        self.menuicons[key] = QtGui.QIcon(g.app.gui.getImageImage(fn))
    return self.menuicons[key]

</t>
<t tx="tbrown.20100701093750.13800">@g.command('todo-dec-pri')
def todo_dec_pri(event: LeoKeyEvent, direction: int = 1) -&gt; None:
    c = event['c']
    if not hasattr(c, 'cleo'):
        return  # pragma: no cover
    p = c.p
    priority = int(c.cleo.getat(p.v, 'priority'))

    if priority not in c.cleo.priorities:
        priority = 1
    else:
        keys = sorted(c.cleo.priorities.keys())
        index = (keys.index(priority) + direction) % len(keys)
        priority = keys[index]

    priority = c.cleo.setPri(priority)
    c.redraw()


@g.command('todo-inc-pri')
def todo_inc_pri(event: LeoKeyEvent) -&gt; None:
    todo_dec_pri(event, direction=-1)


</t>
<t tx="tbrown.20110213091328.16233">def set_due_date(
    self,
    val: QtCore.QDate | None = None,
    mode: str = 'adjust',
    field: str = 'duedate',
) -&gt; None:
    "mode: `adjust` for change in time, `check` for checkbox toggle"
    c = self.c
    p = c.p
    v = p.v

    if field == 'duedate':
        toggle = self.ui.UI.dueDateToggle
    else:
        toggle = self.ui.UI.nxtwkDateToggle

    if mode == 'check':
        if toggle.checkState() == Unchecked:
            self.setat(v, field, "")
        else:
            self.setat(v, field, val.toPyDate())
    else:
        toggle.setCheckState(Checked)
        self.setat(v, field, val.toPyDate())

    self.updateUI()  # if change was made to date with offset selector
    self.loadIcons(p)

</t>
<t tx="tbrown.20110213091328.16235">def set_due_time(
    self,
    val: QtCore.QTime | None = None,
    mode: str = 'adjust',
    field: str = 'duetime',
) -&gt; None:
    "mode: `adjust` for change in time, `check` for checkbox toggle"
    c = self.c
    p = c.p
    v = p.v

    if field == 'duetime':
        toggle = self.ui.UI.dueTimeToggle
    else:
        toggle = self.ui.UI.nxtwkTimeToggle

    if mode == 'check':
        if toggle.checkState() == Unchecked:
            self.setat(v, field, "")
        else:
            self.setat(v, field, val.toPyTime())
    else:
        toggle.setCheckState(Checked)
        self.setat(v, field, val.toPyTime())
    self.loadIcons(p)

</t>
<t tx="tbrown.20110213153425.16373">def duekey(self, v: VNode, field: str = 'due') -&gt; tuple[bool, dt.date, dt.time, int]:
    """key function for sorting by due date/time"""
    # pylint: disable=boolean-datetime
    priority = self.getat(v, 'priority')
    done = priority not in self.todo_priorities
    date_ = self.getat(v, field + 'date') or dt.date(3000, 1, 1)
    time_ = self.getat(v, field + 'time') or dt.time(23, 59, 59)
    return done, date_, time_, priority

</t>
<t tx="tbrown.20110213153425.16377">@redrawer
def dueSort(self, p: Position = None, field: str = 'due') -&gt; None:
    if p is None:
        p = self.c.currentPosition()
    self.c.selectPosition(p)
    self.c.sortSiblings(key=lambda x: self.duekey(x, field=field))

</t>
<t tx="tbrown.20121129095833.39490">def unl_to_pos(self, unl: Any, for_p: Any) -&gt; tuple[Cmdr, Position]:
    """ "unl may be an outline (like c) or an UNL (string)

    return c, p where c is an outline and p is a node to copy data to
    in that outline

    for_p is the p to be copied - needed to check for invalid recursive
    copy / move
    """

    # COPIED FROM quickMove.py

    # unl is an UNL indicating where to insert
    full_path = unl
    path, unl = full_path.split('#', 1)
    c2 = g.openWithFileName(path, old_c=self.c)
    self.c.bringToFront(c2=self.c)
    maxp = g.findAnyUnl(unl, c2)
    if maxp:
        if for_p == maxp or for_p.isAncestorOf(maxp):
            g.es("Invalid move")
            return None, None
        nd = maxp
    else:
        g.es("Could not find '%s'" % full_path)
        self.c.bringToFront(c2=self.c)
        return None, None
    return c2, nd

</t>
<t tx="tbrown.20121204084515.60965">def set_date_offset(self, field: str = 'nextworkdate') -&gt; None:
    """set_nxtwk_date_offset - update date by selected offset

    offset sytax::

        +5 five days after today
        -5 five days before today
        &gt;5 move current date 5 days later
        &lt;5 move current date 5 days earlier

    """

    if field == 'nextworkdate':
        offset = str(self.ui.UI.nxtwkDateOffset.currentText())
    else:
        offset = str(self.ui.UI.dueDateOffset.currentText())

    mult = 1  # to handle '&lt;' as a negative relative offset

    date = QtCore.QDate.currentDate()

    if '&lt;' in offset or '&gt;' in offset:
        date = self.ui.UI.nxtwkDateEdit.date()

    if offset.startswith('&lt;'):
        mult = -1

    self.set_due_date(val=date.addDays(mult * int(offset.strip('&lt;&gt;'))), field=field)
    p = self.c.currentPosition()
    self.loadIcons(p)

</t>
<t tx="tbrown.20130207095125.20463">@redrawer
def dueClear(self, p: Position = None) -&gt; None:
    """clear due date on descendants, useful for creating a master todo
    item with sub items which previously had their own dates"""
    if p is None:
        p = self.c.currentPosition()
    for p in p.subtree():
        self.setat(p.v, 'duedate', '')

</t>
<t tx="tbrown.20130207103126.28498">def needs_doing(
    self, v: VNode = None, pri: Any = None, due: Any = None
) -&gt; bool:  # Hard to annotate.
    """needs_doing - Return true if the node is a todo node that needs doing

    :Parameters:
    - `v`: vnode
    """

    if v is not None:
        pri = self.getat(v, 'priority')
        due = self.getat(v, 'duedate')

    return (pri in self.todo_priorities) or (due and pri == 9999)

</t>
<t tx="tbrown.20150605111428.1">def updateStyle(self, tag: str = '', k: int | None = None) -&gt; None:
    """
    updateStyle - calling widget.setStyleSheet("/* */") is a trick to get Qt to
    update appearance on a widget styled depending on changes in attributes.
    It's faster than applying the whole stylesheet at top level or applying the
    whole stylesheet to the widget, which also breaks style cascading. But it's
    still too slow to do as the user up/down-arrows through nodes, so we just do
    it on idle instead.

    However, the idle event isn't only called when Leo is truely idle, it's just
    called at a set frequency. So by checking that time (0.2 sec) as passed
    since the need to restyle the node was noted, we avoid updating every
    idle-time seconds as the user scrolls through the outline with the arrow
    keys, which causes hiccups in scrolling speed.
    """

    if self._widget_to_style:
        # pylint: disable = unpacking-non-sequence
        # this would be neat, but hasPendingEvents() always returns True
        # (google it), so check time has passed instead
        # if QtWidgets.QApplication.instance().hasPendingEvents():
        #     return  # not truely idle
        w, old_time = self._widget_to_style
        if time.time() - old_time &gt; 0.2:
            w.setStyleSheet("/* */")
            self._widget_to_style = None

</t>
<t tx="tbrown.20170928065405.1">@g.command('todo-fix-datetime')
def todo_fix_datetime(event: LeoKeyEvent) -&gt; None:
    c = event['c']
    if not hasattr(c, 'cleo'):
        return  # pragma: no cover
    changed = 0
    for nd in c.all_unique_nodes():
        for key in c.cleo._datetime_fields:
            x = c.cleo.getat(nd, key)
            if not isinstance(x, str):
                c.cleo.setat(nd, key, x)
                changed += 1
                g.es("%r -&gt; %r" % (x, c.cleo.getat(nd, key)))
    g.es("Changed %d attribs." % changed)


</t>
</tnodes>
</leo_file>
