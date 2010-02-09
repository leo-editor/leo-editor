#@+leo-ver=4-thin
#@+node:ekr.20100118190802.2000:@thin ../../pylint-leo.py
#@@language python

#@<< imports >>
#@+node:ekr.20100209120215.2106:<< imports >>
import os
import sys
from pylint import lint

#@-node:ekr.20100209120215.2106:<< imports >>
#@nl
#@+others
#@+node:ekr.20100209120215.2104:getCoreList
def getCoreList():

    return (
        'leoApp','leoAtFile','leoCache','leoChapters','leoCommands',
        'leoEditCommands','leoFileCommands','leoFind','leoFrame',
        'leoGlobals','leoGui','leoImport','leoMenu','leoNodes',
        'leoPlugins','leoShadow','leoTangle','leoUndo',
    )
#@nonl
#@-node:ekr.20100209120215.2104:getCoreList
#@+node:ekr.20100209115702.2102:getPassList
def getPassList():

    return (
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
#@-node:ekr.20100209115702.2102:getPassList
#@+node:ekr.20100209120215.2105:getPluginsTable
def getPluginsTable ():

    return (
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
            # Dangerous: one E0611 error: 94: No name 'parse' in module 'urllib'
        ('vim',''),
        ('xemacs',''),
    )
#@-node:ekr.20100209120215.2105:getPluginsTable
#@+node:ekr.20100209115702.2101:getTkPass
def getTkPass():
    return (
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
#@-node:ekr.20100209115702.2101:getTkPass
#@+node:ekr.20100209115702.2103:run
def run(theDir,fn,suppress):
    fn = os.path.join('leo',theDir,fn)
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
#@-node:ekr.20100209115702.2103:run
#@-others
#@<< defines >>
#@+node:ekr.20100209121055.2107:<< defines >>
coreList = getCoreList()
pluginsTable = getPluginsTable()
tkPass = getTkPass()
passList = getPassList()
externalList = ('ipy_leo','lproto',)
#@-node:ekr.20100209121055.2107:<< defines >>
#@nl

recentList = ()

tables_table = (
    # (recentList,'core'),
    (coreList,'core'),
    # (tkPass,'plugins'),
    # (passList,'plugins'),
    # (externalList,'external'),
    # (plugins_table,'plugins'),
)

for table,theDir in tables_table:
    if table in (tkPass,passList,coreList,externalList):
        for fn in table:
            run(theDir,fn,suppress='')
    else:
        for fn,suppress in table:
            run(theDir,fn,suppress)
#@-node:ekr.20100118190802.2000:@thin ../../pylint-leo.py
#@-leo
