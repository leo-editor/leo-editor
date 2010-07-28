echo off
rem ekr pylint-leo.bat

rem *** Most warnings are disabled in the .rc file.
rem W0511 To do
rem E0602 Undefined variable
rem E1101 Instance of <class> has no x member

rem Important: all tests must be run from the root directory.
rem This ensures that imports of base classes work.
rem cd c:\leo.repo\trunk

REM tests that fail...
REM goto good_plugins
REM goto bad_plugins

REM goto essential_plugins
goto errors
goto all

:errors

echo leoAtFile.py
call pylint.bat leo\core\leoAtFile.py        --rcfile=leo\test\pylint-leo-rc.txt

goto done

:all

echo runLeo.py (suppress W0611)
rem Harmless: W0611 (import pychecker)
call pylint.bat leo\core\runLeo.py           --disable-msg=W0611 --rcfile=leo\test\pylint-leo-rc.txt

echo leoApp.py
call pylint.bat leo\core\leoApp.py           --rcfile=leo\test\pylint-leo-rc.txt

echo leoAtFile.py
call pylint.bat leo\core\leoAtFile.py        --rcfile=leo\test\pylint-leo-rc.txt

echo leoChapters.py
call pylint.bat leo\core\leoChapters.py      --rcfile=leo\test\pylint-leo-rc.txt

echo leoCommands.py
call pylint.bat leo\core\leoCommands.py      --rcfile=leo\test\pylint-leo-rc.txt

echo leoEditCommands.py (Supress W0511: Fixme)
rem W0511:2380: FIXME lineYOffset is expected to be on a tnode in drawing code
call pylint.bat leo\core\leoEditCommands.py  --disable-msg=W0511 --rcfile=leo\test\pylint-leo-rc.txt

echo leoFileCommands.py
call pylint.bat leo\core\leoFileCommands.py  --rcfile=leo\test\pylint-leo-rc.txt

echo leoFind.py
call pylint.bat leo\core\leoFind.py          --rcfile=leo\test\pylint-leo-rc.txt

echo leoFrame.py
call pylint.bat leo\core\leoFrame.py         --rcfile=leo\test\pylint-leo-rc.txt

rem E0602:4528:isBytes: Undefined variable 'bytes'
echo leoGlobals.py
call pylint.bat leo\core\leoGlobals.py       --rcfile=leo\test\pylint-leo-rc.txt

echo leoGui.py
rem W0511: to do
call pylint.bat leo\core\leoGui.py           --disable-msg=W0511 --rcfile=leo\test\pylint-leo-rc.txt

echo leoImport.py
call pylint.bat leo\core\leoImport.py        --rcfile=leo\test\pylint-leo-rc.txt

echo leoMenu.py
call pylint.bat leo\core\leoMenu.py          --rcfile=leo\test\pylint-leo-rc.txt

echo leoNodes.py
call pylint.bat leo\core\leoMenu.py          --rcfile=leo\test\pylint-leo-rc.txt

echo leoPlugins.py
call pylint.bat leo\core\leoPlugins.py       --rcfile=leo\test\pylint-leo-rc.txt

echo leoShadow.py
call pylint.bat leo\core\leoShadow.py       --rcfile=leo\test\pylint-leo-rc.txt

echo leoTangle.py
call pylint.bat leo\core\leoTangle.py        --rcfile=leo\test\pylint-leo-rc.txt

echo leoUndo.py
call pylint.bat leo\core\leoUndo.py          --rcfile=leo\test\pylint-leo-rc.txt

echo qtGui.py (suppress W0221)
call pylint.bat leo\plugins\qtGui.py         --disable-msg=W0221 --rcfile=leo\test\pylint-leo-rc.txt

goto done

:essential_plugins

echo mod_scripting.py
rem Harmless: E0611:489:scriptingController.runDebugScriptCommand: No name 'leoScriptModule' in module 'leo.core'
call pylint.bat leo\plugins\mod_scripting.py        --disable-msg=E0611 --rcfile=leo\test\pylint-leo-rc.txt

echo open_with.py
call pylint.bat leo\plugins\open_with.py            --rcfile=leo\test\pylint-leo-rc.txt

echo toolbar.py (Suppress E1101,W0221,W0511)
rem doesn't help: cd c:\leo.repo\trunk\leo\plugins
rem call pylint.bat toolbar.py     --rcfile=c:\leo.repo\trunk\leo\test\pylint-leo-rc.txt
rem cd c:\leo.repo\trunk
rem Dangerous: many erroneous E1101 errors
rem Harmless: W0221: Arguments number differs from overridden method
rem Harmless: W0511: Fixme and to-do.
call pylint.bat leo\plugins\toolbar.py     --disable-msg=E1101,W0221,W0511 --rcfile=leo\test\pylint-leo-rc.txt

echo UNL.py
call pylint.bat leo\plugins\UNL.py                  --rcfile=leo\test\pylint-leo-rc.txt

echo vim.py
call pylint.bat leo\plugins\vim.py                  --rcfile=leo\test\pylint-leo-rc.txt

echo xemacs.py
call pylint.bat leo\plugins\xemacs.py               --rcfile=leo\test\pylint-leo-rc.txt

goto done

:good_plugins


echo active_path.py (Suppress W0511)
rem                                               W0511: A todo message
call pylint.bat leo\plugins\active_path.py        --disable-msg=W0511 --rcfile=leo\test\pylint-leo-rc.txt

echo add_directives.py
call pylint.bat leo\plugins\add_directives.py     --rcfile=leo\test\pylint-leo-rc.txt

echo at_folder.py
call pylint.bat leo\plugins\at_folder.py          --rcfile=leo\test\pylint-leo-rc.txt

echo at_produce.py
rem                                               W0102: Dangerous default value pl ([]) as argument
call pylint.bat leo\plugins\at_produce.py         --disable-msg=W0102 --rcfile=leo\test\pylint-leo-rc.txt

echo at_view.py
call pylint.bat leo\plugins\at_view.py            --rcfile=leo\test\pylint-leo-rc.txt

echo base64Packager.py (suppress E1101)
rem                                               E1101:166:viewAsGif: Module 'Pmw' has no 'Dialog' member
rem                                               E1101:167:viewAsGif: Module 'Pmw' has no 'ScrolledCanvas' member
call pylint.bat leo\plugins\base64Packager.py     --disable-msg=E1101 --rcfile=leo\test\pylint-leo-rc.txt

echo bibtex.py
call pylint.bat leo\plugins\bibtex.py             --rcfile=leo\test\pylint-leo-rc.txt

echo bookmarks.py
call pylint.bat leo\plugins\bookmarks.py          --rcfile=leo\test\pylint-leo-rc.txt

echo chapter_hoist.py
call pylint.bat leo\plugins\chapter_hoist.py      --rcfile=leo\test\pylint-leo-rc.txt

echo color_markup.py
call pylint.bat leo\plugins\color_markup.py       --rcfile=leo\test\pylint-leo-rc.txt

echo ConceptualSort.py
call pylint.bat leo\plugins\ConceptualSort.py     --rcfile=leo\test\pylint-leo-rc.txt

echo datenodes.py
call pylint.bat leo\plugins\datenodes.py          --rcfile=leo\test\pylint-leo-rc.txt

echo detect_urls.py
call pylint.bat leo\plugins\detect_urls.py        --rcfile=leo\test\pylint-leo-rc.txt

echo dtest.py (Suppress W0611)
rem                                               W0611: Unused import g (may be needed for doctests)
call pylint.bat leo\plugins\dtest.py              --disable-msg=W0611 --rcfile=leo\test\pylint-leo-rc.txt

echo dump_globals.py
call pylint.bat leo\plugins\dump_globals.py       --rcfile=leo\test\pylint-leo-rc.txt

echo EditAttributes.py
call pylint.bat leo\plugins\EditAttributes.py     --rcfile=leo\test\pylint-leo-rc.txt

echo empty_leo_file.py
call pylint.bat leo\plugins\empty_leo_file.py     --rcfile=leo\test\pylint-leo-rc.txt

echo enable_gc.py
call pylint.bat leo\plugins\enable_gc.py          --rcfile=leo\test\pylint-leo-rc.txt

echo exampleTemacsExtension.py
call pylint.bat leo\plugins\exampleTemacsExtension.py --rcfile=leo\test\pylint-leo-rc.txt

echo expfolder.py
call pylint.bat leo\plugins\expfolder.py           --rcfile=leo\test\pylint-leo-rc.txt

echo FileActions.py
call pylint.bat leo\plugins\FileActions.py         --rcfile=leo\test\pylint-leo-rc.txt

echo gtkGui.py
call pylint.bat leo\plugins\gtkGui.py              --rcfile=leo\test\pylint-leo-rc.txt

echo hoist.py
call pylint.bat leo\plugins\hoist.py               --rcfile=leo\test\pylint-leo-rc.txt

echo image.py
call pylint.bat leo\plugins\image.py               --rcfile=leo\test\pylint-leo-rc.txt

echo import_cisco_config.py
call pylint.bat leo\plugins\import_cisco_config.py --rcfile=leo\test\pylint-leo-rc.txt

echo initinclass.py
call pylint.bat leo\plugins\initinclass.py         --rcfile=leo\test\pylint-leo-rc.txt

echo ipython.py
call pylint.bat leo\plugins\ipython.py             --rcfile=leo\test\pylint-leo-rc.txt

echo keybindings.py
call pylint.bat leo\plugins\keybindings.py         --rcfile=leo\test\pylint-leo-rc.txt

echo leo_pdf.py (suppress E0602,W0105)
rem  A pylint error(?):  E0602:391:Bunch.__setitem__: Undefined variable 'operator'
rem  This may be needed: W0105:415:Writer: String statement has no effect
call pylint.bat leo\plugins\leo_pdf.py             --disable-msg=E0602,W0105 --rcfile=leo\test\pylint-leo-rc.txt

echo leo_to_html.py
call pylint.bat leo\plugins\leo_to_html.py         --rcfile=leo\test\pylint-leo-rc.txt

echo leo_to_rtf.py
call pylint.bat leo\plugins\leo_to_rtf.py          --rcfile=leo\test\pylint-leo-rc.txt

echo Library.py
call pylint.bat leo\plugins\Library.py             --rcfile=leo\test\pylint-leo-rc.txt

echo lineNumbers.py
call pylint.bat leo\plugins\lineNumbers.py         --rcfile=leo\test\pylint-leo-rc.txt

echo macros.py
rem E1103:141:paramClass.parameterize: Instance of 'tkinterGui' has no 'getInsertPoint' member (but some types could not be inferred)
rem E1103:141:paramClass.parameterize: Instance of 'unitTestGui' has no 'getInsertPoint' member (but some types could not be inferred)
rem E1103:141:paramClass.parameterize: Instance of 'nullGui' has no 'getInsertPoint' member (but some types could not be inferred)
call pylint.bat leo\plugins\macros.py              --rcfile=leo\test\pylint-leo-rc.txt

echo maximizeNewWindows.py
call pylint.bat leo\plugins\maximizeNewWindows.py  --rcfile=leo\test\pylint-leo-rc.txt

echo mnplugins.py
call pylint.bat leo\plugins\mnplugins.py           --rcfile=leo\test\pylint-leo-rc.txt

echo mod_leo2ascd.py
call pylint.bat leo\plugins\mod_leo2ascd.py       --rcfile=leo\test\pylint-leo-rc.txt

echo mod_read_dir_outline.py
call pylint.bat leo\plugins\mod_read_dir_outline.py --rcfile=leo\test\pylint-leo-rc.txt

echo mod_tempfname.py
call pylint.bat leo\plugins\mod_tempfname.py      --rcfile=leo\test\pylint-leo-rc.txt

echo mod_timestamp.py
call pylint.bat leo\plugins\mod_timestamp.py      --rcfile=leo\test\pylint-leo-rc.txt

echo multifile.py
call pylint.bat leo\plugins\multifile.py          --rcfile=leo\test\pylint-leo-rc.txt

echo newButtons.py
rem  E1101: UIHelperClass.addWidgets: Instance of 'FlatOptionMenu' has no 'pack' member
call pylint.bat leo\plugins\newButtons.py         --rcfile=leo\test\pylint-leo-rc.txt

echo niceNosent.py
call pylint.bat leo\plugins\niceNosent.py          --rcfile=leo\test\pylint-leo-rc.txt

echo nodenavigator.py
call pylint.bat leo\plugins\nodenavigator.py       --rcfile=leo\test\pylint-leo-rc.txt

echo open_shell.py
call pylint.bat leo\plugins\open_shell.py         --rcfile=leo\test\pylint-leo-rc.txt

echo outline_export.py
call pylint.bat leo\plugins\outline_export.py      --rcfile=leo\test\pylint-leo-rc.txt

echo override_commands.py
call pylint.bat leo\plugins\override_commands.py   --rcfile=leo\test\pylint-leo-rc.txt

echo paste_as_headlines.py
call pylint.bat leo\plugins\paste_as_headlines.py   --rcfile=leo\test\pylint-leo-rc.txt

echo plugins_menu.py
call pylint.bat leo\plugins\plugins_menu.py         --rcfile=leo\test\pylint-leo-rc.txt

echo pluginsTest.py
call pylint.bat leo\plugins\pluginsTest.py          --rcfile=leo\test\pylint-leo-rc.txt

echo quickMove.py
call pylint.bat leo\plugins\quickMove.py            --rcfile=leo\test\pylint-leo-rc.txt

echo quit_leo.py
call pylint.bat leo\plugins\quit_leo.py             --rcfile=leo\test\pylint-leo-rc.txt

echo redirect_to_log.py
call pylint.bat leo\plugins\redirect_to_log.py      --rcfile=leo\test\pylint-leo-rc.txt

echo rowcol.py
call pylint.bat leo\plugins\rowcol.py               --rcfile=leo\test\pylint-leo-rc.txt

echo run_nodes.py
call pylint.bat leo\plugins\run_nodes.py            --rcfile=leo\test\pylint-leo-rc.txt

echo scheduler.py
call pylint.bat leo\plugins\scheduler.py            --rcfile=leo\test\pylint-leo-rc.txt

echo script_io_to_body.py
call pylint.bat leo\plugins\script_io_to_body.py    --rcfile=leo\test\pylint-leo-rc.txt

echo scripts_menu.py
call pylint.bat leo\plugins\scripts_menu.py         --rcfile=leo\test\pylint-leo-rc.txt

echo shortcut_button.py
call pylint.bat leo\plugins\shortcut_button.py      --rcfile=leo\test\pylint-leo-rc.txt

echo slideshow.py
call pylint.bat leo\plugins\slideshow.py            --rcfile=leo\test\pylint-leo-rc.txt

echo startfile.py
call pylint.bat leo\plugins\startfile.py            --rcfile=leo\test\pylint-leo-rc.txt

echo table.py
call pylint.bat leo\plugins\table.py                --rcfile=leo\test\pylint-leo-rc.txt

echo testRegisterCommand.py
call pylint.bat leo\plugins\testRegisterCommand.py  --rcfile=leo\test\pylint-leo-rc.txt

echo textnode.py
call pylint.bat leo\plugins\textnode.py             --rcfile=leo\test\pylint-leo-rc.txt

echo threading_colorizer.py
call pylint.bat leo\plugins\threading_colorizer.py  --rcfile=leo\test\pylint-leo-rc.txt

echo trace_gc_plugin.py
call pylint.bat leo\plugins\trace_gc_plugin.py      --rcfile=leo\test\pylint-leo-rc.txt

echo trace_keys.py
call pylint.bat leo\plugins\trace_keys.py           --rcfile=leo\test\pylint-leo-rc.txt

echo trace_tags.py
call pylint.bat leo\plugins\trace_tags.py           --rcfile=leo\test\pylint-leo-rc.txt

echo UASearch.py
call pylint.bat leo\plugins\UASearch.py             --rcfile=leo\test\pylint-leo-rc.txt

echo UniversalScrolling.py
call pylint.bat leo\plugins\UniversalScrolling.py   --rcfile=leo\test\pylint-leo-rc.txt

echo URLloader.py
call pylint.bat leo\plugins\URLloader.py            --rcfile=leo\test\pylint-leo-rc.txt

echo word_count.py
call pylint.bat leo\plugins\word_count.py           --rcfile=leo\test\pylint-leo-rc.txt

echo word_export.py
call pylint.bat leo\plugins\word_export.py          --rcfile=leo\test\pylint-leo-rc.txt

echo xsltWithNodes.py (Suppress W0105)
rem                                              W0105:697: String statement has no effect
rem                                              This string is needed as an example
call pylint.bat leo\plugins\xsltWithNodes.py     --disable-msg=W0105 --rcfile=leo\test\pylint-leo-rc.txt

goto done

:unchecked_plugins

REM 
REM echo dynacommon.py
REM call pylint.bat leo\plugins\dynacommon.py    --rcfile=leo\test\pylint-leo-rc.txt
REM 
REM echo dyna_menu.py
REM call pylint.bat leo\plugins\dyna_menu.py     --rcfile=leo\test\pylint-leo-rc.txt
REM 
REM echo ironPythonGui.py
REM call pylint.bat leo\plugins\ironPythonGui.py --rcfile=leo\test\pylint-leo-rc.txt
REM 
REM echo LeoN.py
REM call pylint.bat leo\plugins\LeoN.py          --rcfile=leo\test\pylint-leo-rc.txt
REM 
REM echo rst2.py
REM call pylint.bat leo\plugins\rst2.py          --rcfile=leo\test\pylint-leo-rc.txt
REM 
REM echo temacs.py
REM call pylint.bat leo\plugins\temacs.py        --rcfile=leo\test\pylint-leo-rc.txt
REM 
REM echo usetemacs.py
REM call pylint.bat leo\plugins\usetemacs.py     --rcfile=leo\test\pylint-leo-rc.txt

:bad_plugins

rem  this file has a bug that I don't know how to fix.
echo autotrees.py
call pylint.bat leo\plugins\autotrees.py     --rcfile=leo\test\pylint-leo-rc.txt

echo cleo.py
call pylint.bat leo\plugins\cleo.py     --rcfile=leo\test\pylint-leo-rc.txt

echo cursesGui.py W0311: uses @tabwidth -2
call pylint.bat leo\plugins\cursesGui.py          --disable-msg=W0311 --rcfile=leo\test\pylint-leo-rc.txt

echo fastGotoNode.py
call pylint.bat leo\plugins\fastGotoNode.py     --rcfile=leo\test\pylint-leo-rc.txt

echo footprints.py
call pylint.bat leo\plugins\footprints.py     --rcfile=leo\test\pylint-leo-rc.txt

echo graphed.py
call pylint.bat leo\plugins\graphed.py     --rcfile=leo\test\pylint-leo-rc.txt

echo groupOperations.py
call pylint.bat leo\plugins\groupOperations.py     --rcfile=leo\test\pylint-leo-rc.txt

echo gtkDialogs.py
call pylint.bat leo\plugins\gtkDialogs.py     --rcfile=leo\test\pylint-leo-rc.txt

echo leoOPML.py
call pylint.bat leo\plugins\leoOPML.py     --rcfile=leo\test\pylint-leo-rc.txt

echo leoupdate.py
call pylint.bat leo\plugins\leoupdate.py     --rcfile=leo\test\pylint-leo-rc.txt

echo leo_interface.py
call pylint.bat leo\plugins\leo_interface.py     --rcfile=leo\test\pylint-leo-rc.txt

echo mod_autosave.py
call pylint.bat leo\plugins\mod_autosave.py     --rcfile=leo\test\pylint-leo-rc.txt

echo mod_http.py
call pylint.bat leo\plugins\mod_http.py     --rcfile=leo\test\pylint-leo-rc.txt

echo mod_labels.py
call pylint.bat leo\plugins\mod_labels.py     --rcfile=leo\test\pylint-leo-rc.txt

echo mod_scripting.py
rem E0611:461:scriptingController.runDebugScriptCommand: No name 'leoScriptModule' in module 'leo.core'
rem The code that creates the 'debug-script' button writes leoScriptModule.py is written to the core directory.
call pylint.bat leo\plugins\mod_scripting.py  --disable-msg=E0611 --rcfile=leo\test\pylint-leo-rc.txt

echo nav_buttons.py
call pylint.bat leo\plugins\nav_buttons.py     --rcfile=leo\test\pylint-leo-rc.txt

echo nodebar.py
call pylint.bat leo\plugins\nodebar.py     --rcfile=leo\test\pylint-leo-rc.txt

echo pie_menus.py
call pylint.bat leo\plugins\pie_menus.py     --rcfile=leo\test\pylint-leo-rc.txt

echo pretty_print.py
call pylint.bat leo\plugins\pretty_print.py     --rcfile=leo\test\pylint-leo-rc.txt

echo rClick.py
call pylint.bat leo\plugins\rClick.py     --rcfile=leo\test\pylint-leo-rc.txt

echo rClickBasePluginClasses.py
call pylint.bat leo\plugins\rClickBasePluginClasses.py     --rcfile=leo\test\pylint-leo-rc.txt

echo read_only_nodes.py
call pylint.bat leo\plugins\read_only_nodes.py     --rcfile=leo\test\pylint-leo-rc.txt

echo searchbar.py
call pylint.bat leo\plugins\searchbar.py     --rcfile=leo\test\pylint-leo-rc.txt

echo searchbox.py (suppress W0221)
rem  		                             W0221:284:QuickFind.init_s_ctrl: Arguments number differs from overridden method
call pylint.bat leo\plugins\searchbox.py     disable-msg=W0221 --rcfile=leo\test\pylint-leo-rc.txt

echo templates.py
call pylint.bat leo\plugins\templates.py     --rcfile=leo\test\pylint-leo-rc.txt

echo xcc_nodes.py
call pylint.bat leo\plugins\xcc_nodes.py     --rcfile=leo\test\pylint-leo-rc.txt

echo zenity_file_dialogs.py
call pylint.bat leo\plugins\zenity_file_dialogs.py     --rcfile=leo\test\pylint-leo-rc.txt

:done
echo "*****done*****"

pause