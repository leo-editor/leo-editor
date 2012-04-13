#@+leo-ver=5-thin
#@+node:ekr.20100221142603.5638: * @file ../../pylint-leo.py
#@@language python

import optparse
import os
import sys
from pylint import lint

all_suppressions = 'C0111,C0301,C0321,C0322,C0323,C0324,\
F0401,\
R0201,R0903,\
W0102,W0122,W0141,W0142,W0201,W0212,W0231,W0232,W0401,W0402,W0404,W0406,\
W0602,W0603,W0612,W0613,W0621,W0622,W0631,W0702,W0703,W0704,W1111'

#@+others
#@+node:ekr.20100221142603.5640: ** getCoreList
def getCoreList():

    return (

        ('runLeo',          ''),
        ('leoApp',          ''),
        ('leoAtFile',       ''),
        ('leoBridge',       ''),
        ('leoCache',        ''),
        ('leoChapters',     ''),
        ('leoCommands',     ''),
        ('leoConfig',       ''),
        ('leoEditCommands', ''),
        ('leoFileCommands', 'E1120,E1101'),
            # E1120: no value passed for param.
            # E1101: (dangerous) Class 'str' has no 'maketrans' member
        ('leoFind',         ''),
        ('leoFrame',        'R0923'),
            # R0923: Interface not implemented.
        ('leoGlobals',      'E0611,E1103'), 
            # E0611: no name 'parse' in urllib.
            # E1103: (dangerous) Instance of 'ParseResult' has no 'xxx' member,
            # (but some types could not be inferred)
        ('leoGui',          ''),
        ('leoImport',       ''),
        ('leoKeys',         ''),
        ('leoMenu',         'W0108'),
            # W0108: Lambda may not be necessary (it is).
        ('leoNodes',        ''),
        ('leoPlugins',      ''),
        ('leoRst',          ''),
        ('leoShadow',       ''),
        ('leoTangle',       ''),
        ('leoTest',         ''),
        ('leoUndo',         'W0511'),
            # WO511: TODO 
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
        # 'scrolledmessage', # No longer exists.
        'setHomeDirectory','slideshow','spydershell','startfile',
        'testRegisterCommand','todo',
        # 'toolbar', # in plugins table.
        'trace_gc_plugin','trace_keys','trace_tags',
        'vim','xemacs',
    )
#@+node:ekr.20100221142603.5642: ** getPluginsList
def getPluginsList():

    return (
        ('bookmarks',       ''),
        # ('mod_http',      ''),
        ('mod_scripting',   'E0611'),
            # Harmless: E0611:489:scriptingController.runDebugScriptCommand:
            # No name 'leoScriptModule' in module 'leo.core'
            
        ('vim.py',          ''),
        ('viewrendered.py', 'E1103'),
            # Dangerous: PyQt4.phonon has no x member.
        ('xemacs.py',       ''),

        # ('toolbar','E1101,W0221,W0511'),
            # Dangerous: many erroneous E1101 errors
            # Harmless: W0221: Arguments number differs from overridden method
            # Harmless: W0511: Fixme and to-do.
    )
#@+node:ekr.20120225032124.17089: ** getRecentCoreList
def getRecentCoreList():
    
    return (
        # ('runLeo',            ''),
        # ('leoApp',            ''),
        # ('leoAtFile',         ''),
        # ('leoBridge',       ''),
        # ('leoCache',          ''),
        # ('leoChapters',       ''),
        # ('leoCommands',       ''),
        # ('leoConfig',           ''),
        # ('leoEditCommands',   ''),
        # ('leoFind',           ''),
        # ('leoFrame',          'R0923'),
            # R0923: Interface not implemented.

        # ('leoGlobals',          'E0611,E1103'),
            # E0611: no name 'parse' in urllib.
            # E1103: Instance of 'ParseResult' has no 'xxx' member
            # (but some types could not be inferred)

        # ('leoGui',            ''),
        # ('leoImport',         ''),

        ('leoIPython',           'E0611,W0108,R0923'),
            # E0611: No name 'x' in module 'y'
                # Not serious: the imports will find any problems.
            # W0108: Lambda may not be necessary (who cares).
            # R0923: Interface not implemented.
    
        # ('leoKeys',           ''),
        # ('leoMenu',           'W0108'),
            # W0108: Lambda may not be necessary (it is).
        # ('leoNodes',          ''),
        # ('leoPlugins',        ''),
        # ('leoFileCommands',   'E1120,E1101'),
            # E1120: no value passed for param.
            # E1101: (dangerous) Class 'str' has no 'maketrans' member
        # ('leoRst',            ''),
        # ('leoShadow',         ''),
        # ('leoTangle',         ''),
        # ('leoTest',           ''),
        # ('leoUndo',           'W0511'),
            # WO511: TODO 
)
#@+node:ekr.20100221142603.5643: ** getTkPass
def getTkPass():
    
    return []

    # return (
        # 'EditAttributes','Library',
        # 'URLloader','UniversalScrolling','UASearch',
        # 'autotrees','chapter_hoist','cleo','dump_globals',
        # 'expfolder','geotag','graphed','groupOperations',
        # 'hoist','import_cisco_config',
        # 'keybindings','leoupdate',
        # 'maximizeNewWindows', 'mnplugins','mod_labels',
        # 'mod_read_dir_outline','mod_tempfname','multifile',
        # 'newButtons','nodeActions','nodenavigator',
        # 'open_with','pie_menus','pluginsTest',
        # 'read_only_nodes','rClick',
        # 'scheduler','searchbar','searchbox','shortcut_button',
        # 'script_io_to_body',
        # 'templates','textnode','tkGui','toolbar',
        # 'xcc_nodes',
    # )
#@+node:ekr.20100221142603.5644: ** run
# Important: I changed lint.py:Run.__init__ so pylint can handle more than one file.
# From: sys.exit(self.linter.msg_status)
# To:   print('EKR: exit status',self.linter.msg_status)

def run(theDir,fn,suppress,rpython=False):
    fn = os.path.join('leo',theDir,fn)
    rc_fn = os.path.abspath(os.path.join('leo','test','pylint-leo-rc.txt'))
    assert os.path.exists(rc_fn)
    
    args = ['--rcfile=%s' % (rc_fn)]
    if suppress:
        args.append('--disable=%s' % (suppress))
    # if rpython: args.append('--rpython-mode') # Probably does not exist.

    fn = os.path.abspath(fn)
    # print('run: theDir',theDir,'fn',fn)
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
#@+node:ekr.20120307142211.9886: ** scanOptions
def scanOptions():

    '''Handle all options, remove them from sys.argv and set lm.options.'''

    # print('scanOptions 1',sys.argv)

    # This automatically implements the -h (--help) option.
    parser = optparse.OptionParser()
    
    def add(name,help):
        add = parser.add_option(name,action="store_true",help=help)
    
    add('-a', help = 'all')
    add('-c', help = 'core')
    add('-e', help = 'external')
    add('-g', help = 'gui plugins')
    add('-p', help = 'plugins')
    add('-r', help = 'recent')
    add('-s', help = 'suppressions')
    
    # Parse the options.
    options, args = parser.parse_args()
    # sys.argv = [sys.argv[0]]
    # sys.argv.extend(args)
    
    if   options.a: return 'all'
    elif options.c: return 'core'
    elif options.e: return 'external'
    elif options.g: return 'gui'
    elif options.p: return 'plugins'
    elif options.r: return 'recent'
    elif options.s: return 'suppressions'
    else:           return 'core'
#@-others

scope = scanOptions()

coreList = getCoreList()
externalList = ('ipy_leo','lproto',)
passList = getPassList()
pluginsList = getPluginsList()
recentCoreList = getRecentCoreList()
tkPass = getTkPass()

onlySupressionsList = (z for z in coreList if z[1])

guiPluginsList = (
    ('baseNativeTree',  ''),
    # ('nested_splitter', ''),
    ('qtGui','E0611,E1101,R0923,W0221,W0233'),
        # E1101:7584:leoQtGui.embed_ipython: Module 'IPython' has no 'ipapi' member
        # E0611: No name 'xxx' in module 'urllib'
        # W0233: __init__ method from a non direct base class 'QDateTimeEdit' is called
        # R0923: Interface not implemented
)

recentPluginsList = (
    # 'screenshots',
    # 'codewisecompleter',
    # 'baseNativeTree','contextmenu',
    # 'mod_scripting','plugins_menu','projectwizard',
    # 'trace_gc_plugin',
)

if scope == 'all':
    tables_table = (
        (coreList,'core'),
        (guiPluginsList,'plugins'),
        # (pluginsList,'plugins'),
        (externalList,'external'),
    )
elif scope == 'core':
    tables_table =  (
        (coreList,'core'),
        (guiPluginsList,'plugins'),
    )
elif scope == 'external':
    tables_table = (
        (externalList,'external'),
    )
elif scope == 'gui':
    tables_table = (
        (guiPluginsList,'plugins'),
)
elif scope == 'plugins':
    tables_table = (
        (pluginsList,'plugins'),
        # (passList,'plugins'),
    )
elif scope == 'recent':
    tables_table = (
        (recentCoreList,'core'),
        (recentPluginsList,'plugins'),
    )
elif scope == 'suppressions':
    # These tests are run *without* suppressions.
    tables_table = (
        (onlySupressionsList,'core'),
    )
else:
    print('bad scope',scope)
    tables_table = ()

for table,theDir in tables_table:
    if table in (coreList,pluginsList,guiPluginsList,recentCoreList):
        # These tables have suppressions.
        for fn,suppress in table:
            run(theDir,fn,suppress)
    elif table == onlySupressionsList:
        # Run *without suppressions.
        for fn,suppress in table:
            run(theDir,fn,suppress='')
    else:
        for fn in table:
            run(theDir,fn,suppress='')
#@-leo
