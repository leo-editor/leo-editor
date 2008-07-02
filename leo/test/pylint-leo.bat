echo off
rem ekr pylint-leo.bat

rem *** Most warnings are disabled in the .rc file.

rem E0602 Undefined variable
rem E1101 Instance of <class> has no x member

echo cd c:\leo.repo\trunk\leo
cd c:\leo.repo\trunk\leo

REM tests that fail...
goto good_plugins
goto plugins
goto all

echo tests that fail with dangerous settings enabled...

echo .
echo leoTkinterFind.py Dangerous: E1101,E1103: many Erroneous errors given.
call pylint.bat core\leoTkinterFind.py   --rcfile=test\pylint-leo-rc.txt

echo .
echo leoTkinterFrame.py Harmless: W0221: mismatch between Tk.Text methods and overridden methods.
echo leoTkinterFrame.py Dangerous: E1101 : many ERRONEOUS errors given
call pylint.bat core\leoTkinterFrame.py  --disable-msg=W0221 --rcfile=test\pylint-leo-rc.txt

echo .
echo leoTkinterMenu.py Dangerous: E1101: many ERRONEOUS errors given.
call pylint.bat core\leoTkinterMenu.py   --rcfile=test\pylint-leo-rc.txt

goto done

:all
echo all tests, suppressing known errors...

echo .
echo runLeo.py Harmless: W0611 (import pychecker)
call pylint.bat core\runLeo.py            --disable-msg=W0611 --rcfile=test\pylint-leo-rc.txt
echo .
echo leoApp.py
call pylint.bat core\leoApp.py           --rcfile=test\pylint-leo-rc.txt
echo .
echo leoAtFile.py
call pylint.bat core\leoAtFile.py        --rcfile=test\pylint-leo-rc.txt
echo .
echo leoChapters.py
call pylint.bat core\leoChapters.py      --rcfile=test\pylint-leo-rc.txt
echo .
echo leoCommands.py
call pylint.bat core\leoCommands.py      --rcfile=test\pylint-leo-rc.txt
echo .
echo leoEditCommands.py
call pylint.bat core\leoEditCommands.py  --rcfile=test\pylint-leo-rc.txt
echo .
echo leoFileCommands.py
call pylint.bat core\leoFileCommands.py  --rcfile=test\pylint-leo-rc.txt
echo .
echo leoFind.py
call pylint.bat core\leoFind.py          --rcfile=test\pylint-leo-rc.txt
echo .
echo leoFrame.py
call pylint.bat core\leoFrame.py         --rcfile=test\pylint-leo-rc.txt
echo .
echo leoGlobals.py
call pylint.bat core\leoGlobals.py       --rcfile=test\pylint-leo-rc.txt
echo .
echo leoGui.py
call pylint.bat core\leoGui.py           --rcfile=test\pylint-leo-rc.txt
echo .
echo leoImport.py
call pylint.bat core\leoImport.py        --rcfile=test\pylint-leo-rc.txt
echo .
echo leoMenu.py
call pylint.bat core\leoMenu.py          --rcfile=test\pylint-leo-rc.txt
echo .
echo leoNodes.py
call pylint.bat core\leoNodes.py         --rcfile=test\pylint-leo-rc.txt
echo .
echo leoPlugins.py
call pylint.bat core\leoPlugins.py       --rcfile=test\pylint-leo-rc.txt
echo .
echo leoTangle.py
call pylint.bat core\leoTangle.py        --rcfile=test\pylint-leo-rc.txt
echo .
echo leoUndo.py harmless: W0102: dangerous default argument: []
call pylint.bat core\leoUndo.py          --disable-msg=W0102 --rcfile=test\pylint-leo-rc.txt
echo .
echo leoTkinterDialog.py
call pylint.bat core\leoTkinterDialog.py --rcfile=test\pylint-leo-rc.txt
echo .
echo leoTkinterFind.py Dangerous: E1101,E1103: many ERRONEOUS errors
call pylint.bat core\leoTkinterFind.py   --disable-msg=E1101,E1103 --rcfile=test\pylint-leo-rc.txt
echo .
echo leoTkinterGui.py
call pylint.bat core\leoTkinterGui.py    --rcfile=test\pylint-leo-rc.txt
echo .
echo leoTkinterFrame.py Harmless: W0221: mismatch between Tk.Text methods and overridden methods.
echo leoTkinterFrame.py Dangerous: E1101: many ERRONEOUS errors
call pylint.bat core\leoTkinterFrame.py  --disable-msg=W0221,E1101 --rcfile=test\pylint-leo-rc.txt
echo .
echo leoTkinterKeys.py
call pylint.bat core\leoTkinterKeys.py   --rcfile=test\pylint-leo-rc.txt
echo .
echo leoTkinterMenu.py Dangerous: E1101: many ERRONEOUS errors
call pylint.bat core\leoTkinterMenu.py   --disable-msg=E1101 --rcfile=test\pylint-leo-rc.txt
echo .
echo leoTkinterTree.py Dangerous: E1101: many ERRONEOUS errors
call pylint.bat core\leoTkinterTree.py   --disable-msg=E1101 --rcfile=test\pylint-leo-rc.txt

goto done

:good_plugins

echo .
echo UASearch.py
call pylint.bat plugins\UASearch.py     --rcfile=test\pylint-leo-rc.txt

goto done

echo .
echo active_path.py  W0511: A todo message
call pylint.bat plugins\active_path.py        --disable-msg=W0511 --rcfile=test\pylint-leo-rc.txt
echo .
echo add_directives.py
call pylint.bat plugins\add_directives.py     --rcfile=test\pylint-leo-rc.txt
echo .
echo at_folder.py
call pylint.bat plugins\at_folder.py          --rcfile=test\pylint-leo-rc.txt
echo .
echo at_produce.py
rem                                           W0102: Dangerous default value pl ([]) as argument
call pylint.bat plugins\at_produce.py          --disable-msg=W0102 --rcfile=test\pylint-leo-rc.txt
echo .
echo at_view.py
call pylint.bat plugins\at_view.py            --rcfile=test\pylint-leo-rc.txt
echo .
echo base64Packager.py Dangerous: E1101: two ERRONEOUS errors
call pylint.bat plugins\base64Packager.py     --disable-msg=E1101 --rcfile=test\pylint-leo-rc.txt
echo .
echo bibtex.py
call pylint.bat plugins\bibtex.py             --rcfile=test\pylint-leo-rc.txt
echo .
echo bookmarks.py
call pylint.bat plugins\bookmarks.py          --rcfile=test\pylint-leo-rc.txt
echo .
echo chapter_hoist.py
call pylint.bat plugins\chapter_hoist.py      --rcfile=test\pylint-leo-rc.txt
echo .
echo color_markup.py
call pylint.bat plugins\color_markup.py       --rcfile=test\pylint-leo-rc.txt
echo .
echo ConceptualSort.py
call pylint.bat plugins\ConceptualSort.py     --rcfile=test\pylint-leo-rc.txt
echo .
echo datenodes.py
call pylint.bat plugins\datenodes.py          --rcfile=test\pylint-leo-rc.txt
echo .
echo detect_urls.py
call pylint.bat plugins\detect_urls.py        --rcfile=test\pylint-leo-rc.txt
echo .
echo dtest.py
rem                                           W0611: Unused import g (may be needed for doctests)
rem                                           E1101: A pylint bug: setCommand defined in baseLeoPlugin.
call pylint.bat plugins\dtest.py              --disable-msg=W0611,E1101 --rcfile=test\pylint-leo-rc.txt
echo .
echo dump_globals.py
call pylint.bat plugins\dump_globals.py       --rcfile=test\pylint-leo-rc.txt
echo .
echo EditAttributes.py
call pylint.bat plugins\EditAttributes.py     --rcfile=test\pylint-leo-rc.txt
echo .
echo empty_leo_file.py
call pylint.bat plugins\empty_leo_file.py     --rcfile=test\pylint-leo-rc.txt
echo .
echo enable_gc.py
call pylint.bat plugins\enable_gc.py          --rcfile=test\pylint-leo-rc.txt
echo .
echo exampleTemacsExtension.py
call pylint.bat plugins\exampleTemacsExtension.py --rcfile=test\pylint-leo-rc.txt
echo .
echo expfolder.py
call pylint.bat plugins\expfolder.py           --rcfile=test\pylint-leo-rc.txt
echo .
echo FileActions.py
call pylint.bat plugins\FileActions.py         --rcfile=test\pylint-leo-rc.txt
echo .
echo gtkGui.py
call pylint.bat plugins\gtkGui.py              --rcfile=test\pylint-leo-rc.txt
echo .
echo hoist.py
call pylint.bat plugins\hoist.py               --rcfile=test\pylint-leo-rc.txt
echo .
echo image.py
call pylint.bat plugins\image.py               --rcfile=test\pylint-leo-rc.txt
echo .
echo import_cisco_config.py
call pylint.bat plugins\import_cisco_config.py --rcfile=test\pylint-leo-rc.txt
echo .
echo initinclass.py
call pylint.bat plugins\initinclass.py         --rcfile=test\pylint-leo-rc.txt
echo .
echo ipython.py
call pylint.bat plugins\ipython.py             --rcfile=test\pylint-leo-rc.txt
echo .
echo keybindings.py
call pylint.bat plugins\keybindings.py         --rcfile=test\pylint-leo-rc.txt
echo .
echo leo_pdf.py
rem
rem  A pylint error(?):  E0602:391:Bunch.__setitem__: Undefined variable 'operator'
rem  This may be needed: W0105:415:Writer: String statement has no effect
call pylint.bat plugins\leo_pdf.py             --disable-msg=E0602,W0105 --rcfile=test\pylint-leo-rc.txt
echo .
echo leo_to_html.py
call pylint.bat plugins\leo_to_html.py         --rcfile=test\pylint-leo-rc.txt
echo .
echo leo_to_rtf.py
call pylint.bat plugins\leo_to_rtf.py          --rcfile=test\pylint-leo-rc.txt
echo .
echo Library.py
call pylint.bat plugins\Library.py             --rcfile=test\pylint-leo-rc.txt
echo .
echo lineNumbers.py
call pylint.bat plugins\lineNumbers.py         --rcfile=test\pylint-leo-rc.txt
echo .
echo macros.py
call pylint.bat plugins\macros.py              --rcfile=test\pylint-leo-rc.txt
echo .
echo maximizeNewWindows.py
call pylint.bat plugins\maximizeNewWindows.py  --rcfile=test\pylint-leo-rc.txt
echo .
echo mnplugins.py
call pylint.bat plugins\mnplugins.py           --rcfile=test\pylint-leo-rc.txt
echo .
echo mod_leo2ascd.py
call pylint.bat plugins\mod_leo2ascd.py       --rcfile=test\pylint-leo-rc.txt
echo .
echo mod_read_dir_outline.py
call pylint.bat plugins\mod_read_dir_outline.py --rcfile=test\pylint-leo-rc.txt
echo .
echo mod_shadow.py
call pylint.bat plugins\mod_shadow.py         --rcfile=test\pylint-leo-rc.txt
echo .
echo mod_shadow_core.py
rem                                           W0311: bad indentation
call pylint.bat plugins\mod_shadow_core.py    --disable-msg=W0311 --rcfile=test\pylint-leo-rc.txt
echo .
echo mod_scripting.py
call pylint.bat plugins\mod_scripting.py       --rcfile=test\pylint-leo-rc.txt
echo .
echo mod_timestamp.py
call pylint.bat plugins\mod_timestamp.py       --rcfile=test\pylint-leo-rc.txt
echo .
echo multifile.py
call pylint.bat plugins\multifile.py           --rcfile=test\pylint-leo-rc.txt
echo .
echo newButtons.py Dangerous: E1101
rem  E1101: UIHelperClass.addWidgets: Instance of 'FlatOptionMenu' has no 'pack' member
call pylint.bat plugins\newButtons.py        --disable-msg=E1101 --rcfile=test\pylint-leo-rc.txt
echo .
echo niceNosent.py
call pylint.bat plugins\niceNosent.py          --rcfile=test\pylint-leo-rc.txt
echo .
echo nodenavigator.py
call pylint.bat plugins\nodenavigator.py       --rcfile=test\pylint-leo-rc.txt
echo .
echo open_shell.py
call pylint.bat plugins\open_shell.py         --rcfile=test\pylint-leo-rc.txt
echo .
echo open_with.py
call pylint.bat plugins\open_with.py           --rcfile=test\pylint-leo-rc.txt
echo .
echo outline_export.py
call pylint.bat plugins\outline_export.py      --rcfile=test\pylint-leo-rc.txt
echo .
echo override_commands.py
call pylint.bat plugins\override_commands.py   --rcfile=test\pylint-leo-rc.txt
echo .
echo paste_as_headlines.py
call pylint.bat plugins\paste_as_headlines.py   --rcfile=test\pylint-leo-rc.txt
echo .
echo plugins_menu.py
call pylint.bat plugins\plugins_menu.py         --rcfile=test\pylint-leo-rc.txt
echo .
echo pluginsTest.py
call pylint.bat plugins\pluginsTest.py          --rcfile=test\pylint-leo-rc.txt
echo .
echo quickMove.py
call pylint.bat plugins\quickMove.py            --rcfile=test\pylint-leo-rc.txt
echo .
echo quit_leo.py
call pylint.bat plugins\quit_leo.py             --rcfile=test\pylint-leo-rc.txt
echo .
echo redirect_to_log.py
call pylint.bat plugins\redirect_to_log.py      --rcfile=test\pylint-leo-rc.txt
echo .
echo rowcol.py
call pylint.bat plugins\rowcol.py               --rcfile=test\pylint-leo-rc.txt
echo .
echo rst.py
call pylint.bat plugins\rst.py                  --rcfile=test\pylint-leo-rc.txt
echo .
echo rst3.py
call pylint.bat plugins\rst3.py                 --rcfile=test\pylint-leo-rc.txt
echo .
echo run_nodes.py
call pylint.bat plugins\run_nodes.py            --rcfile=test\pylint-leo-rc.txt
echo .
echo scheduler.py
call pylint.bat plugins\scheduler.py            --rcfile=test\pylint-leo-rc.txt
echo .
echo script_io_to_body.py
call pylint.bat plugins\script_io_to_body.py    --rcfile=test\pylint-leo-rc.txt
echo .
echo scripts_menu.py
call pylint.bat plugins\scripts_menu.py         --rcfile=test\pylint-leo-rc.txt
echo .
echo searchbox.py Dangerous: E1101: two ERRONEOUS errors
call pylint.bat plugins\searchbox.py            --disable-msg=E1101 --rcfile=test\pylint-leo-rc.txt
echo .
echo shortcut_button.py
call pylint.bat plugins\shortcut_button.py      --rcfile=test\pylint-leo-rc.txt
echo .
echo slideshow.py
call pylint.bat plugins\slideshow.py            --rcfile=test\pylint-leo-rc.txt
echo .
echo startfile.py
call pylint.bat plugins\startfile.py            --rcfile=test\pylint-leo-rc.txt
echo .
echo table.py
call pylint.bat plugins\table.py                --rcfile=test\pylint-leo-rc.txt
echo .
echo testRegisterCommand.py
call pylint.bat plugins\testRegisterCommand.py  --rcfile=test\pylint-leo-rc.txt
echo .
echo textnode.py
call pylint.bat plugins\textnode.py             --rcfile=test\pylint-leo-rc.txt
echo .
echo threading_colorizer.py
call pylint.bat plugins\threading_colorizer.py  --rcfile=test\pylint-leo-rc.txt
echo .
echo trace_gc_plugin.py
call pylint.bat plugins\trace_gc_plugin.py      --rcfile=test\pylint-leo-rc.txt
echo .
echo trace_keys.py
call pylint.bat plugins\trace_keys.py           --rcfile=test\pylint-leo-rc.txt
echo .
echo trace_tags.py
call pylint.bat plugins\trace_tags.py           --rcfile=test\pylint-leo-rc.txt
echo .
echo UniversalScrolling.py
call pylint.bat plugins\UniversalScrolling.py   --rcfile=test\pylint-leo-rc.txt
echo .
echo vim.py
call pylint.bat plugins\vim.py                  --rcfile=test\pylint-leo-rc.txt
echo .
echo word_count.py
call pylint.bat plugins\word_count.py           --rcfile=test\pylint-leo-rc.txt
echo .
echo word_export.py
call pylint.bat plugins\word_export.py          --rcfile=test\pylint-leo-rc.txt
echo .
echo xemacs.py
call pylint.bat plugins\xemacs.py               --rcfile=test\pylint-leo-rc.txt
echo .
echo xsltWithNodes.py
rem                                          W0105:697: String statement has no effect
rem                                          This string is needed as an example
call pylint.bat plugins\xsltWithNodes.py     --disable-msg=W0105 --rcfile=test\pylint-leo-rc.txt

goto done

:unchecked_plugins

REM echo .
REM echo dynacommon.py
REM call pylint.bat plugins\dynacommon.py    --rcfile=test\pylint-leo-rc.txt
REM echo .
REM echo dyna_menu.py
REM call pylint.bat plugins\dyna_menu.py     --rcfile=test\pylint-leo-rc.txt
REM echo .
REM echo ironPythonGui.py
REM call pylint.bat plugins\ironPythonGui.py --rcfile=test\pylint-leo-rc.txt
REM echo .
REM echo LeoN.py
REM call pylint.bat plugins\LeoN.py          --rcfile=test\pylint-leo-rc.txt
REM echo .
REM echo rst2.py
REM call pylint.bat plugins\rst2.py          --rcfile=test\pylint-leo-rc.txt
REM echo .
REM echo temacs.py
REM call pylint.bat plugins\temacs.py        --rcfile=test\pylint-leo-rc.txt
REM echo .
REM echo usetemacs.py
REM call pylint.bat plugins\usetemacs.py         --rcfile=test\pylint-leo-rc.txt

:plugins

echo .
rem  this file has a bug that I don't know how to fix.
echo autotrees.py
call pylint.bat plugins\autotrees.py     --rcfile=test\pylint-leo-rc.txt
echo .
echo cleo.py
call pylint.bat plugins\cleo.py     --rcfile=test\pylint-leo-rc.txt
echo .
echo cursesGui.py W0311: uses @tabwidth -2
call pylint.bat plugins\cursesGui.py          --disable-msg=W0311 --rcfile=test\pylint-leo-rc.txt
echo .
echo fastGotoNode.py
call pylint.bat plugins\fastGotoNode.py     --rcfile=test\pylint-leo-rc.txt
echo .
echo footprints.py
call pylint.bat plugins\footprints.py     --rcfile=test\pylint-leo-rc.txt
echo .
echo graphed.py
call pylint.bat plugins\graphed.py     --rcfile=test\pylint-leo-rc.txt
echo .
echo groupOperations.py
call pylint.bat plugins\groupOperations.py     --rcfile=test\pylint-leo-rc.txt
echo .
echo gtkDialogs.py
call pylint.bat plugins\gtkDialogs.py     --rcfile=test\pylint-leo-rc.txt
echo .
echo leoOPML.py
call pylint.bat plugins\leoOPML.py     --rcfile=test\pylint-leo-rc.txt
echo .
echo leoupdate.py
call pylint.bat plugins\leoupdate.py     --rcfile=test\pylint-leo-rc.txt
echo .
echo leo_interface.py
call pylint.bat plugins\leo_interface.py     --rcfile=test\pylint-leo-rc.txt
echo .
echo mod_autosave.py
call pylint.bat plugins\mod_autosave.py     --rcfile=test\pylint-leo-rc.txt
echo .
echo mod_http.py
call pylint.bat plugins\mod_http.py     --rcfile=test\pylint-leo-rc.txt
echo .
echo mod_labels.py
call pylint.bat plugins\mod_labels.py     --rcfile=test\pylint-leo-rc.txt
echo .
echo .
echo mod_tempfname.py
call pylint.bat plugins\mod_tempfname.py     --rcfile=test\pylint-leo-rc.txt
echo .
echo nav_buttons.py
call pylint.bat plugins\nav_buttons.py     --rcfile=test\pylint-leo-rc.txt
echo .
echo nodebar.py
call pylint.bat plugins\nodebar.py     --rcfile=test\pylint-leo-rc.txt
echo .
echo pie_menus.py
call pylint.bat plugins\pie_menus.py     --rcfile=test\pylint-leo-rc.txt
echo .
echo pretty_print.py
call pylint.bat plugins\pretty_print.py     --rcfile=test\pylint-leo-rc.txt
echo .
echo rClick.py
call pylint.bat plugins\rClick.py     --rcfile=test\pylint-leo-rc.txt
echo .
echo rClickBasePluginClasses.py
call pylint.bat plugins\rClickBasePluginClasses.py     --rcfile=test\pylint-leo-rc.txt
echo .
echo read_only_nodes.py
call pylint.bat plugins\read_only_nodes.py     --rcfile=test\pylint-leo-rc.txt
echo .
echo searchbar.py
call pylint.bat plugins\searchbar.py     --rcfile=test\pylint-leo-rc.txt
echo .
echo templates.py
call pylint.bat plugins\templates.py     --rcfile=test\pylint-leo-rc.txt
echo .
echo toolbar.py
call pylint.bat plugins\toolbar.py     --rcfile=test\pylint-leo-rc.txt
echo .
echo UNL.py
call pylint.bat plugins\UNL.py     --rcfile=test\pylint-leo-rc.txt
echo .
echo URLloader.py
call pylint.bat plugins\URLloader.py     --rcfile=test\pylint-leo-rc.txt
echo .
echo xcc_nodes.py
call pylint.bat plugins\xcc_nodes.py     --rcfile=test\pylint-leo-rc.txt
echo .
echo zenity_file_dialogs.py
call pylint.bat plugins\zenity_file_dialogs.py     --rcfile=test\pylint-leo-rc.txt


:done
echo "*****done*****"
cd c:\leo.repo\trunk\leo\test

pause