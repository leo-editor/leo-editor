#@+leo-ver=5-thin
#@+node:ekr.20100221142603.5638: * @file ../../pylint-leo.py
#@@language python

#@+<< imports >>
#@+node:ekr.20100221142603.5639: ** << imports >>
import os
import sys
from pylint import lint

#@-<< imports >>
#@+others
#@+node:ekr.20100221142603.5640: ** getCoreList
def getCoreList():

    return (
        ('leoApp',          ''),
        ('leoAtFile',       ''),
        ('leoCache',        ''),
        ('leoChapters',     ''),
        ('leoCommands',     ''),
        ('leoEditCommands', ''),
        ('leoFileCommands', 'E1120'),
            # E1120: no value passed for param.
            # E1101: (dangerous) Class 'str' has no 'maketrans' member
        ('leoFind',         ''),
        ('leoFrame',        ''),
        ('leoGlobals',      ''), 
            # E1103: (dangerous) Instance of 'ParseResult' has no 'xxx' member,
            # (but some types could not be inferred)
        ('leoGui',          ''),
        ('leoImport',       ''),
        ('leoMenu',         ''),
        ('leoNodes',        ''),
        ('leoPlugins',      ''),
        ('leoShadow',       ''),
        ('leoTangle',       ''),
        ('leoUndo',         ''),
    )
#@+node:ekr.20100221142603.5641: ** getPassList
def getPassList():

    return (
        '__init__','FileActions',
        # 'UNL', # in plugins table.
        'active_path','add_directives','attrib_edit',
        'backlink','base64Packager','baseNativeTree','bibtex','bookmarks',
        'codewisecompleter','colorize_headlines','contextmenu',
        'ctagscompleter','cursesGui','datenodes','debugger_pudb',
        'detect_urls','dtest','empty_leo_file','enable_gc','initinclass',
        'leo_to_html','leo_interface','leo_pdf','leo_to_rtf',
        'leoOPML','leoremote','lineNumbers',
        'macros','mime','mod_autosave','mod_framesize','mod_leo2ascd',
        # 'mod_scripting', # in plugins table.
        'mod_speedups','mod_timestamp',
        'nav_buttons','nav_qt','niceNosent','nodeActions','nodebar',
        'open_shell','open_with','outline_export','quit_leo',
        'paste_as_headlines','plugins_menu','pretty_print','projectwizard',
        'qt_main','qt_quicksearch','qtframecommands',
        'quickMove','quicksearch','redirect_to_log','rClickBasePluginClasses',
        'run_nodes', # Changed thread.allocate_lock to threading.lock().acquire()
        'rst3',
        'scrolledmessage','setHomeDirectory','slideshow','spydershell','startfile',
        'testRegisterCommand','todo',
        # 'toolbar', # in plugins table.
        'trace_gc_plugin','trace_keys','trace_tags',
        'vim','xemacs',
    )
#@+node:ekr.20100221142603.5642: ** getPluginsTable
def getPluginsTable ():

    return (
        ('mod_scripting','E0611'),
            # Harmless: E0611:489:scriptingController.runDebugScriptCommand:
            # No name 'leoScriptModule' in module 'leo.core'
        ('toolbar','E1101,W0221,W0511'),
            # Dangerous: many erroneous E1101 errors
            # Harmless: W0221: Arguments number differs from overridden method
            # Harmless: W0511: Fixme and to-do.
        ('UNL','E0611'),
            # Dangerous: one E0611 error: 94: No name 'parse' in module 'urllib'
    )
#@+node:ekr.20100221142603.5643: ** getTkPass
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
        'script_io_to_body',
        'templates','textnode','tkGui','toolbar',
        'xcc_nodes',
    )
#@+node:ekr.20100221142603.5644: ** run
# Important: I changed lint.py:Run.__init__ so pylint can handle more than one file.
# From: sys.exit(self.linter.msg_status)
# To:   print('EKR: exit status',self.linter.msg_status)
def run(theDir,fn,suppress,rpython=False):
    fn = os.path.join('leo',theDir,fn)
    rc_fn = os.path.abspath(os.path.join('leo','test','pylint-leo-rc.txt'))
    assert os.path.exists(rc_fn)
    args = ['--rcfile=%s' % (rc_fn)]
    if suppress: args.append('--disable=%s' % (suppress))
    # if rpython: args.append('--rpython-mode') # Probably does not exist.
    fn = os.path.abspath(fn)
    if not fn.endswith('.py'): fn = fn+'.py'
    args.append(fn)
    if os.path.exists(fn):
        if suppress:
            print('pylint-leo.py: %s suppress: %s' % (fn,suppress))
        else:
            print('pylint-leo.py: %s' % fn)
        lint.Run(args)
    else:
        print('file not found:',fn)
#@-others
#@+<< defines >>
#@+node:ekr.20100221142603.5645: ** << defines >>
coreList = getCoreList()
externalList = ('ipy_leo','lproto',)
passList = getPassList()
pluginsTable = getPluginsTable()
tkPass = getTkPass()
#@-<< defines >>

all_suppressions = 'C0111,C0301,C0321,C0322,C0323,C0324,\
F0401,\
R0201,R0903,\
W0102,W0122,W0141,W0142,W0201,W0212,W0231,W0232,W0401,W0402,W0404,W0406,\
W0602,W0603,W0612,W0613,W0621,W0622,W0631,W0702,W0703,W0704,W1111'

no_suppressions = ''

recentCoreList = (
    # ('leoAtFile',no_suppressions),
    # ('leoEditCommands',no_suppressions),
    ('leoFileCommands','E1120,E1101'),
        # E1120: no value passed for param.
        # #1101: (dangerous) Class 'str' has no 'maketrans' member
    ('leoGlobals','E0611'),
        # E0611: no name 'parse' in urllib.
)

guiPluginsTable = (
    ('qtGui','E0611,W0221,W0233'),
        # E0611: No name 'xxx' in module 'urllib'
        # W0233: __init__ method from a non direct base class 'QDateTimeEdit' is called
    ('tkGui','W0221,W0222'),
)

recentPluginsList = (
    # 'screenshots',
    # 'tkGui','codewisecompleter',
    # 'baseNativeTree','contextmenu',
    # 'mod_scripting','plugins_menu','projectwizard',
    # 'trace_gc_plugin',
)

# rpythonList = (
#    'leoApp',
# )

tables_table = (
    # (rpythonList,'core'),
    # (recentCoreList,'core'),
    # (recentPluginsList,'plugins'),
    # (coreList,'core'),
    # (guiPluginsTable,'plugins'),
    # (tkPass,'plugins'),
    # (passList,'plugins'),
    # (externalList,'external'),
    (pluginsTable,'plugins'),
)

for table,theDir in tables_table:
    #if table in (rpythonList,):
        # for fn in table:
            # run(theDir,fn,suppress='',rpython=True) 
    if table in (coreList,pluginsTable,guiPluginsTable,recentCoreList):
        # These tables have suppressions.
        for fn,suppress in table:
            run(theDir,fn,suppress) 
    else:
        for fn in table:
            run(theDir,fn,suppress='')
#@-leo
