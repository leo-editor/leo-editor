# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20210901140718.1: * @file ../unittests/basic_tests.py
#@@first
"""Basic tests for Leo"""
# pylint: disable=no-member
import glob
import inspect
import os
import sys
# import textwrap
import unittest
from leo.core import leoGlobals as g
from leo.core import leoTest2
from leo.core import leoCommands
import leo.core.leoGui as leoGui
import leo.core.leoVim as leoVim
#@+others
#@+node:ekr.20210901140855.1: ** class BasicTest
class BasicTest(unittest.TestCase):
    """Basic unit tests for Leo."""
    #@+others
    #@+node:ekr.20210901140855.2: *3* BasicTest: setUp, tearDown...
    def setUp(self):
        """Create the nodes in the commander."""
        # Create a new commander for each test.
        # This is fast, because setUpClass has done all the imports.
        self.c = c = leoCommands.Commands(fileName=None, gui=g.app.gui)
        c.selectPosition(c.rootPosition())
        g.unitTesting = True

    def tearDown(self):
        self.c = None
        g.unitTesting = False

    @classmethod
    def setUpClass(cls):
        leoTest2.create_app()
    #@+node:ekr.20210901140645.1: *3* BasicTest.tests...
    #@+node:ekr.20210901140645.2: *4* BasicTest.test_all_commands_have_an_event_arg
    def test_all_commands_have_an_event_arg(self):
        c = self.c
        d = c.commandsDict
        keys = sorted(d.keys())
        table = ('bookmark', 'quickmove_', 'screen-capture', 'stickynote')
        for key in keys:
            continue_flag = False
            for prefix in table:
                if key.startswith(prefix):
                    continue_flag = True
                    break # These plugins have their own signatures.
            if continue_flag:
                continue
            f = d.get(key)
            # print(key, f.__name__ if f else repr(f))
            # Test true __call__ methods if they exist.
            name = getattr(f,'__name__',None) or repr(f)
            if hasattr(f,'__call__') and inspect.ismethod(f.__call__):
                f = getattr(f,'__call__')
            t = inspect.getfullargspec(f)  # t is a named tuple.
            args = t.args
            arg0 = len(args) > 0 and args[0]
            arg1 = len(args) > 1 and args[1]
            expected = ('event',)
            message = f"no event arg for command {key}, func: {name}, args: {args}"
            assert arg0 in expected or arg1 in expected, message
    #@+node:ekr.20210901140645.3: *4* BasicTest.test_All_menus_execute_the_proper_command
    def test_All_menus_execute_the_proper_command(self):
        """
        We want to ensure that when masterMenuHandler does::
        
            event = g.app.gui.create_key_event(c,binding=stroke,w=w)
            return k.masterKeyHandler(event)
        
        that the effect will be to call commandName, where commandName
        is the arg passed to masterMenuHandler.

        createMenuEntries creates the association of stroke to commandName.
        """
        trace = False # False: the unit test can fail.
        c, p = self.c, self.c.p
        k = c.k
        d = g.app.unitTestMenusDict
        d2 = k.bindingsDict
        d2name = 'k.bindingsDict'
        commandNames = list(d.keys())
        commandNames.sort()
        exclude_strokes = ('Alt+F4','Ctrl+q','Ctrl+Shift+Tab',)
        for name in commandNames:
            assert name in c.commandsDict,'unexpected command name: %s' % (
                repr(name))
            aSet = d.get(name)
            aList = list(aSet)
            aList.sort()
            for z in exclude_strokes:
                if z in aList:
                    aList.remove(z)
            for stroke in aList:
                aList2 = d2.get(stroke)
                assert aList2,'stroke %s not in %s' % (
                    repr(stroke),d2name)
                for b in aList2:
                    if b.commandName == name:
                        break
                else:
                    if trace:
                        inverseBindingDict = k.computeInverseBindingDict()
                        print('%s: stroke %s not bound to %s in %s' % (
                            p.h,repr(stroke),repr(name),d2name))
                        print('%s: inverseBindingDict.get(%s): %s' % (
                            p.h,name,inverseBindingDict.get(name)))
                    else:
                        assert False,'stroke %s not bound to %s in %s' % (
                            repr(stroke),repr(name),d2name)
    #@+node:ekr.20210901140645.4: *4* BasicTest.test_batch_mode
    def test_batch_mode(self):
       
        silent = True
        trace = False
        python_interp = f"\"{sys.executable}\""  # 2021/07/05: Allow blanks in path to python.
        test_path = g.os_path_join(g.app.loadDir,"..","test","unittest")
        src_path  = g.os_path_join(g.app.loadDir,"..","..")

        leo_file   = g.os_path_join(src_path,"launchLeo.py")
        batch_file = g.os_path_join(test_path,"batchTest.py")
        test_file  = g.os_path_join(test_path,"createdFile.txt")

        assert g.os_path_exists(batch_file)

        # Execute this command: python launchLeo.py --script test\unittest\batchTest.py
        # Note: batchTest.py is defined in this file, unitTest.leo.
        if silent:
            command = r'%s %s --silent --script %s' % (python_interp,leo_file,batch_file)
        else:
            command = r'%s %s --script %s' % (python_interp,leo_file,batch_file)

        #@+others
        #@-others

        if trace:
            print('@test batch mode: loadDir: %s' % g.app.loadDir)
            print('test_file: %s' % test_file)
        os.remove(test_file)
        if trace:
            print('command: %s' %  command)
        os.system(command)
        assert g.os_path_exists(test_file), repr(test_file)
    #@+node:ekr.20210901140645.5: *4* BasicTest.test_event_classes
    def test_event_classes(self):
        c = self.c
        if not g.app.gui.guiName().startswith('qt'):
            self.skipTest('Requires Qt')
        event = None
        char = shortcut = stroke = w = x = y = None
        x_root = y_root = None
        # The EventWrapper class is buried too deep to test easily.
        # I'll try harder if it ever become a problem ;-)
            # dw = qt_frame.DynamicWindow(c, parent)
            # event_wrapper = dw.EventWrapper(c, w, next_w, func)
        key_event = leoGui.LeoKeyEvent(
            c, char, event, shortcut,
            w, x, y, x_root, y_root)
        vim_event = leoVim.VimEvent(c, char, stroke, w)
        # assert hasattr(event_wrapper, 'c')
        assert hasattr(key_event, 'c')
        assert hasattr(vim_event, 'c')
    #@+node:ekr.20210901140645.6: *4* BasicTest.test_save_new_file
    def test_save_new_file(self):
        c = self.c
        if g.in_bridge:
            self.skipTest('Not for TravisCI')
        if sys.platform.startswith('linux'):
            # There is a PyQt issue: https://bugreports.qt.io/browse/QTBUG-35600
            # The crash causes several other unit tests to fail.
            self.skipTest('Not for Linux.')
        c1 = c
        fn = g.os_path_finalize_join(g.app.loadDir,'..','test','save-new-test.py')
        if g.os_path_exists(fn):
            os.remove(fn)
        assert not g.os_path_exists(fn)
        try:
            c = c1.new()
            # Not a perfect unit test, but it similar to c.save.
            c.mFileName = fn
            c.openDirectory = c.frame.openDirectory = g.os_path_dirname(fn)
            c.fileCommands.save(c.mFileName,silent=False)
            c.close()
            assert g.os_path_exists(fn)
        finally:
            if g.os_path_exists(fn):
                os.remove(fn)
    #@+node:ekr.20210901140645.7: *4* BasicTest.test_c_config_initIvar_sets_commander_ivars
    def test_c_config_initIvar_sets_commander_ivars(self):
        c = self.c
        for ivar,setting_type,default in g.app.config.ivarsData:
            assert hasattr(c,ivar),ivar
            assert hasattr(c.config,ivar),ivar
            val = getattr(c.config,ivar)
            val2 = c.config.get(ivar,setting_type)
            assert val == val2,"%s %s" % (val,val2)
    #@+node:ekr.20210901140645.8: *4* BasicTest.test_k_settings_ivars_match_settings
    def test_k_settings_ivars_match_settings(self):
        c = self.c
        k = c.k
        getBool  = c.config.getBool
        getColor = c.config.getColor
        bg = getColor('body_text_background_color') or 'white'
        fg = getColor('body_text_foreground_color') or 'black'
        table = (
            ('command_mode_bg_color',           getColor('command_mode_bg_color') or bg),
            ('command_mode_fg_color',           getColor('command_mode_fg_color') or fg),
            ('enable_alt_ctrl_bindings',        getBool('enable_alt_ctrl_bindings')),
            ('enable_autocompleter',            getBool('enable_autocompleter_initially')),
            ('enable_calltips',                 getBool('enable_calltips_initially')),
            ('ignore_unbound_non_ascii_keys',   getBool('ignore_unbound_non_ascii_keys')),
            ('insert_mode_bg_color',            getColor('insert_mode_bg_color') or bg),
            ('insert_mode_fg_color',            getColor('insert_mode_fg_color') or fg),
            ('minibuffer_background_color',     getColor('minibuffer_background_color') or 'lightblue'),
            ('minibuffer_error_color',          getColor('minibuffer_error_color') or 'red'),
            ('minibuffer_warning_color',        getColor('minibuffer_warning_color') or 'lightgrey'),
            ('overwrite_mode_bg_color',         getColor('overwrite_mode_bg_color') or bg),
            ('overwrite_mode_fg_color',         getColor('overwrite_mode_fg_color') or fg),
            # ('swap_mac_keys',                   getBool('swap_mac_keys')),
            ('unselected_body_bg_color',        getColor('unselected_body_bg_color') or bg),
            ('unselected_body_fg_color',        getColor('unselected_body_fg_color') or bg),
            ('warn_about_redefined_shortcuts',  getBool('warn_about_redefined_shortcuts')),
        )
        for ivar,setting in table:
            assert hasattr(k,ivar),ivar
            val = getattr(k,ivar)
            assert val == setting,'%s k.%s setting: %s' % (
                ivar,ivar,val)
    #@+node:ekr.20210901140645.9: *4* BasicTest.test_official_commander_ivars
    def test_official_commander_ivars(self):
        c = self.c
        f = c.frame
        assert(f.c==c)
        assert(c.frame==f)
        ivars = (
            '_currentPosition',
            'hoistStack',
            'mFileName', 
            # Subcommanders...
            'atFileCommands','fileCommands','importCommands','undoer',
            # Args...
            'page_width','tab_width', 'target_language',
        )
        for ivar in ivars:
            assert hasattr(c,ivar), 'missing commander ivar: %s' % ivar
            val = getattr(c,ivar)
            assert val is not None,'null commander ivar: %s'% ivar
    #@+node:ekr.20210901140645.10: *4* BasicTest.test_official_frame_ivars
    def test_official_frame_ivars(self):
        c = self.c
        f = c.frame
        assert(f.c==c)
        assert(c.frame==f)
        for ivar in ('body', 'iconBar', 'log', 'statusLine', 'tree',):
            assert hasattr(f,ivar), 'missing frame ivar: %s' % ivar
            val = getattr(f,ivar)
            assert val is not None,'null frame ivar: %s'% ivar

        # These do not have to be initied.
        for ivar in ('findPanel',):
            assert hasattr(f,ivar), 'missing frame ivar: %s' % ivar
    #@+node:ekr.20210901140645.11: *4* BasicTest.test_official_g_app_directories
    def test_official_g_app_directories(self):
        ivars = ('extensionsDir','globalConfigDir','loadDir','testDir')

        for ivar in ivars:
            assert hasattr(g.app,ivar), 'missing g.app directory: %s' % ivar
            val = getattr(g.app,ivar)
            assert val is not None, 'null g.app directory: %s'% ivar
            assert g.os_path_exists(g.os_path_abspath(val)), 'non-existent g.app directory: %s' % ivar

        assert hasattr(g.app,'homeDir') # May well be None.
    #@+node:ekr.20210901140645.12: *4* BasicTest.test_official_g_app_ivars
    def test_official_g_app_ivars(self):
        ivars = (
            # Global managers.
            'config',
            # 'externalFilesController',
            'loadManager','pluginsController','recentFilesManager',
            # Official ivars.
            'gui',
            'initing','killed','quitting',
            'leoID',
            'log','logIsLocked','logWaiting',
            'nodeIndices',
            'unitTesting','unitTestDict',
            'windowList',
            # Less-official and might be removed...
            'batchMode',
            # 'debugSwitch',
            'disableSave',
            'hookError','hookFunction',
            'numberOfUntitledWindows',
            'realMenuNameDict',
            'searchDict','scriptDict',
            'use_psyco',
        )
        if g.app.isExternalUnitTest or g.in_bridge or g.app.gui.guiName() == 'browser':
            mayBeNone = ('hookFunction','idleTimeHook','log','openWithInstance')
        else:
            mayBeNone = ('hookFunction','openWithInstance')
        fails = []
        for ivar in ivars:
            assert hasattr(g.app, ivar), 'missing app ivar: %s %r' % (ivar,g.app)
            if ivar not in mayBeNone and getattr(g.app, 'old_gui_name', None) != 'browser':
                val = getattr(g.app, ivar)
                if val is None:
                    fails.append(ivar)
        assert not fails, 'old gui: %s: null g.app ivars in %s...\n%s' % (
            g.app.old_gui_name, g.app, g.objToString(fails))
    #@+node:ekr.20210901140645.13: *4* BasicTest.test_at_checkPythonSyntax
    def test_at_checkPythonSyntax(self):
        c, p = self.c, self.c.p
        at = c.atFileCommands
        s = '''
        # no error
        def spam():
            pass
        '''

        assert at.checkPythonSyntax(p,s),'fail 1'

        s2 = '''
        # syntax error
        def spam:
            pass
        '''

        assert not at.checkPythonSyntax(p,s2,supress=True),'fail2'

        if not g.unitTesting: # A hand test of at.syntaxError
            at.checkPythonSyntax(p,s2)
    #@+node:ekr.20210901140645.14: *4* BasicTest.test_at_tabNannyNode
    def test_at_tabNannyNode(self):
        ### @tabwidth -4
        c, p = self.c, self.c.p
        at = c.atFileCommands
        s = '''
        # no error
        def spam():
            pass
        '''
        at.tabNannyNode (p, body=s, suppress=True)
        s2 = '''
        # syntax error
        def spam:
            pass
          a = 2
        '''
        try:
            at.tabNannyNode(p,body=s2,suppress=True)
        except IndentationError:
            pass
    #@+node:ekr.20210901140645.15: *4* BasicTest.test_c_checkPythonCode
    def test_c_checkPythonCode(self):
        c = self.c
        c.checkPythonCode(event=None,
            unittestFlag=True,ignoreAtIgnore=False,
            suppressErrors=True,checkOnSave=False)
    #@+node:ekr.20210901140645.16: *4* BasicTest.test_c_checkPythonNode
    def test_c_checkPythonNode(self):
        c , p = self.c, self.c.p
        table = (
            ('syntax-error','error'),
        )
        for h, expected in table:
            p2 = g.findNodeInTree(c, p, h)
            assert p2,'node not found: %s' % h
            result = c.checkPythonCode(event=None,
                unittestFlag=True,ignoreAtIgnore=True,
                suppressErrors=True,checkOnSave=False)
            assert result==expected, 'expected %s got %s' % (
                expected,result)
    #@+node:ekr.20210901140645.17: *4* BasicTest.test_c_tabNannyNode
    def test_c_tabNannyNode(self):
        ### @tabwidth -4
        c, p = self.c, self.c.p
        s = '''
        # no error
        def spam():
            pass
        '''

        c.tabNannyNode(p,headline=p.h,body=s,unittestFlag=True,suppressErrors=True)

        s2 = '''
        # syntax error
        def spam:
            pass
          a = 2
        '''

        try:
            c.tabNannyNode(p,headline=p.h,body=s2,unittestFlag=True,suppressErrors=True)
        except IndentationError:
            pass
    #@+node:ekr.20210901140645.18: *4* BasicTest.test_g_es_exception
    def test_g_es_exception(self):
        # This is just a hand test.
        if not g.unitTesting:
            try:
                assert False
            except AssertionError:
                g.es_exception(full=True,c=None,color='red')
    #@+node:ekr.20210901140645.19: *4* BasicTest.test_g_getLastTracebackFileAndLineNumber
    def test_g_getLastTracebackFileAndLineNumber(self):
        c = self.c
        try:
            assert False
        except AssertionError:
            fn,n = g.getLastTracebackFileAndLineNumber()
        
        if g.app.isExternalUnitTest:
            writeScriptFile = True
        else:
            writeScriptFile = c.config.getBool('write_script_file')

        if writeScriptFile:
            assert fn != '<string>',repr(fn)
        else:
            assert fn == '<string>',repr(fn)

        assert n == 4,repr(n)
    #@+node:ekr.20210901140645.20: *4* BasicTest.test_leoTest_checkFileSyntax
    def test_leoTest_checkFileSyntax(self):
        c = self.c
        s = '''
        # syntax error
        def spam:
            pass
        '''
        try:
            c.testManager.checkFileSyntax('<fileName>',s,suppress=True)
            assert False
        except SyntaxError:
            pass
    #@+node:ekr.20210901140645.21: *4* BasicTest.test_syntax_of_all_files
    def test_syntax_of_all_files(self):
        c = self.c
        failed,n = [],0
        skip_tuples = (
            ('extensions','asciidoc.py'),
        )
        join = g.os_path_finalize_join
        skip_list = [join(g.app.loadDir,'..',a,b) for a,b in skip_tuples]
        for theDir in ('core','external','extensions','plugins','scripts','test'):
            path = g.os_path_finalize_join(g.app.loadDir,'..',theDir)
            assert g.os_path_exists(path),path
            aList = glob.glob(g.os_path_join(path,'*.py'))
            if g.isWindows:
                aList = [z.replace('\\','/') for z in aList]
            for z in aList:
                if z in skip_list:
                    pass # print('%s: skipped: %s' % (p.h,z))
                else:
                    n += 1
                    fn = g.shortFileName(z)
                    s,e = g.readFileIntoString(z)
                    if not c.testManager.checkFileSyntax(fn,s,reraise=False,suppress=False):
                        failed.append(z)
        assert not failed,'failed %s\n' % g.listToString(failed)
    #@+node:ekr.20210901140645.22: *4* BasicTest.test_syntax_of_setup_py
    def test_syntax_of_setup_py(self):
        c = self.c
        fn = g.os_path_finalize_join(g.app.loadDir, '..', '..', 'setup.py')
        # Only run this test if setup.py exists: it may not in the actual distribution.
        if g.os_path_exists(fn):
            s, e = g.readFileIntoString(fn)
            c.testManager.checkFileSyntax(fn, s, reraise=True, suppress=False)
    #@+node:ekr.20210901140645.23: *4* BasicTest.test__operator_with_unicode
    def test__operator_with_unicode(self):
        
        s = "testᾹ(U+1FB9: Greek Capital Letter Alpha With Macron)"
        s2 = 'test: %s' % s
        assert s2
    #@+node:ekr.20210901140645.24: *4* BasicTest.test_can_t_open_message_in_g_openWithFileName
    def test_can_t_open_message_in_g_openWithFileName(self):
        c = self.c
        if sys.platform.startswith('linux') or g.app.isExternalUnitTest:
            # There is a PyQt issue: https://bugreports.qt.io/browse/QTBUG-35600
            # The crash causes several other unit tests to fail.
            self.skipTest('Not for Linux')
        old_c = c
        filename = "testᾹ(U+1FB9: Greek Capital Letter Alpha With Macron)"
        try:
            c2 = None
            c2 = g.openWithFileName(filename,old_c=old_c)
        finally:
            if c2:
                g.app.destroyWindow(c2.frame)
            c.setLog()
            c.bodyWantsFocus()
    #@+node:ekr.20210901140645.25: *4* BasicTest.test_failure_to_convert_unicode_characters_to_ascii
    def test_failure_to_convert_unicode_characters_to_ascii(self):
        encoding = 'ascii'
        s = '炰' # This is already unicode.
        s2, ok = g.toUnicodeWithErrorCode(s,encoding)
        assert ok, 'toUnicodeWithErrorCode returns False for %s with ascii encoding' % s
        s3, ok = g.toEncodedStringWithErrorCode(s,encoding)
        assert not ok, 'toEncodedStringWithErrorCode returns True for %s with ascii encoding' % s
    #@+node:ekr.20210901140645.26: *4* BasicTest.test_failure_with_ascii_encodings
    def test_failure_with_ascii_encodings(self):
        encoding = 'ascii'
        s = '炰'
        s2, ok = g.toUnicodeWithErrorCode(s,encoding)
        assert ok, 'toUnicodeWithErrorCode returns True for %s with ascii encoding' % s
        s3, ok = g.toEncodedStringWithErrorCode(s,encoding)
        assert not ok, 'toEncodedStringWithErrorCode returns True for %s with ascii encoding' % s
    #@+node:ekr.20210901140645.27: *4* BasicTest.test_koi8_r_encoding
    def test_koi8_r_encoding(self):
        c, p = self.c, self.c.p
        p1 = p.insertAsLastChild()
        s = '\xd4\xc5\xd3\xd4' # the word 'test' in Russian, koi8-r
        assert isinstance(s, str), repr(s)
        p1.setBodyString(s)
        c.selectPosition(p1)
        c.copyOutline()
        c.pasteOutline()
        p2 = p1.next()
        assert p1.b == p2.b
        
    #@+node:ekr.20210901140645.28: *4* BasicTest.test_open_non_existent_non_ascii_directory
    def test_open_non_existent_non_ascii_directory(self):

        # g.openWithFileName *always* opens the file.
        # theFile = 'Ỗ'
        c = self.c
        path = g.os_path_join('Ỗ','Ỗ')
        try:
            c2 = g.openWithFileName(path,old_c=c)
        finally:
            if c2:
                g.app.destroyWindow(c2.frame)
            c.setLog()
            c.bodyWantsFocus()
    #@+node:ekr.20210901140645.29: *4* BasicTest.test_rst_write_with_unicode_character
    def test_rst_write_with_unicode_character(self):
        name = g.os_path_finalize_join(g.app.loadDir,'..','test','unittest','rst_write_test.txt')
        s = "testᾹ(U+1FB9: Greek Capital Letter Alpha With Macron)"
        with open(name,'w',encoding='utf-8') as f:
            f.write(s)
        assert g.os_path_exists(name)
    #@-others
#@-others
#@-leo
