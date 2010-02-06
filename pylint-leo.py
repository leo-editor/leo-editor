import os
import sys
from pylint import lint

tkPass = (
    'EditAttributes','Library',
    'URLloader','UniversalScrolling','UASearch',
    'autotrees','chapter_hoist','cleo','dump_globals',
    'expfolder','geotag','graphed','groupOperations',
    'hoist','import_cisco_config',
    'keybindings','leoupdate',
    'maximizeNewWindows', 'mnplugins','mod_labels',
    'mod_read_dir_outline','mod_tempfname','multifile',
    'newButtons','nodeActions','nodenavigator',
    'open_with','pie_menus','pluginsTest',
    'read_only_nodes','rClick',
    'scheduler','searchbar','searchbox','shortcut_button',
    'script_io_to_body','searchbox',
    'templates','textnode','tkGui','toolbar',
    'xcc_nodes',
)
passList = (
    '__init__','FileActions','UNL',
    'active_path','add_directives','attrib_edit',
    'backlink','base64Packager','baseNativeTree','bibtex','bookmarks',
    'codewisecompleter','colorize_headlines','contextmenu',
    'ctagscompleter','cursesGui','datenodes','debugger_pudb',
    'detect_urls','dtest','empty_leo_file','enable_gc','initinclass',
    'leo_to_html','leo_interface','leo_pdf','leo_to_rtf',
    'leoOPML','leoremote','lineNumbers',
    'macros','mime','mod_autosave','mod_framesize','mod_leo2ascd',
    'mod_scripting','mod_speedups','mod_timestamp',
    'nav_buttons','nav_qt','niceNosent','nodeActions','nodebar',
    'open_shell','outline_export','quit_leo',
    'paste_as_headlines','plugins_menu','pretty_print','projectwizard',
    'qtGui','qt_main','qt_quicksearch','qtframecommands',
    'quickMove',
        # Warning: changed this line by guessing!
        # func = types.MethodType(func, quickMove)
    'quicksearch','redirect_to_log','rClickBasePluginClasses',
    'run_nodes', # Changed thread.allocate_lock to threading.lock().acquire()
    'rst3',
    'scrolledmessage','setHomeDirectory','slideshow','spydershell','startfile',
    'testRegisterCommand','todo','trace_gc_plugin','trace_keys','trace_tags',
    'vim','xemacs',
)
core_files = (
    'leoApp','leoAtFile','leoChapters','leoCommands',
    'leoEditCommands','leoFileCommands','leoFind','leoFrame',
    'leoGlobals','leoGui','leoImport','leoMenu','leoNodes',
    'leoPlugins','leoShadow','leoTangle','leoUndo',
)
external_files = (
    'ipy_leo','lproto','path','pickleshare',
)
recent_core_table = (
    # ('leoAtFile',''),
    ('leoCommands',''),
    # ('leoFileCommands',''),
)
core_table = (
    ('leoGlobals',''),
    ('leoApp',''),
    ('leoAtFile',''),
    ('leoChapters',''),
    ('leoCommands',''),
    ('leoEditCommands','W0511'),
    ('leoFileCommands',''),
    ('leoFind',''),
    ('leoFrame',''),
    ('leoGlobals',''), # E0602:4528:isBytes: Undefined variable 'bytes'
    ('leoGui','W0511'), # W0511: to do
    ('leoImport',''),
    ('leoMenu',''),
    ('leoNodes',''),
    ('leoPlugins',''),
    ('leoShadow',''),
    ('leoTangle',''),
    ('leoUndo',''),
)
external_table = (
    ('ipy_leo',''),
    ('lproto',''),
    ('path',''),
    ('pickleshare',''),
)
plugins_table = (
    ('qtGui','W0221'),
    ('tkGui','W0221'),
    ('mod_scripting','E0611'),
        # Harmless: E0611:489:scriptingController.runDebugScriptCommand:
        # No name 'leoScriptModule' in module 'leo.core'
    ('open_with',''),
    ('toolbar','E1101,W0221,W0511'),
        # Dangerous: many erroneous E1101 errors
        # Harmless: W0221: Arguments number differs from overridden method
        # Harmless: W0511: Fixme and to-do.
    ('UNL',''),
    ('vim',''),
    ('xemacs',''),
)

def run(fn,suppress):
    args = ['--rcfile=leo/test/pylint-leo-rc.txt']
    if suppress: args.append('--disable-msg=%s' % (suppress))
    fn = os.path.abspath(fn)
    if not fn.endswith('.py'): fn = fn+'.py'
    args.append(fn)
    if os.path.exists(fn):
        print('*****',fn,suppress)
        lint.Run(args)
    else:
        print('file not found:',fn)

tables_table = (
    # (tkPass,'plugins'),
    # (passList,'plugins'),
    (recent_core_table,'core'),
    # (core_table,'core'),
    # (external_table,'external'),
    # (plugins_table,'plugins'),
)

for table,theDir in tables_table:
    if table in (tkPass,passList):
        for fn in table:
            fn = os.path.join('leo',theDir,fn)
            run(fn,suppress='')
    else:
        for fn,suppress in table:
            fn = os.path.join('leo',theDir,fn)
            run(fn,suppress)
