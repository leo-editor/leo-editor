# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20210903162431.1: * @file ../unittests/core/test_leoCommands.py
#@@first
"""Tests of leoCommands.py"""

import inspect
import textwrap
from leo.core import leoGlobals as g
from leo.core.leoTest2 import LeoUnitTest

#@+others
#@+node:ekr.20210903162431.2: ** class TestCommands(LeoUnitTest)
class TestCommands(LeoUnitTest):
    """Test cases for leoCommands.py"""
    #@+others
    #@+node:ekr.20210901140645.2: *3* TestCommands.test_all_commands_have_an_event_arg
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
    #@+node:ekr.20210901140645.3: *3* TestCommands.test_all_menus_execute_the_proper_command
    def test_all_menus_execute_the_proper_command(self):
        """
        We want to ensure that when masterMenuHandler does:
        
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
    #@+node:ekr.20210901140645.15: *3* TestCommands.test_c_checkPythonCode
    def test_c_checkPythonCode(self):
        c = self.c
        c.checkPythonCode(event=None,
            unittestFlag=True,ignoreAtIgnore=False,
            suppressErrors=True,checkOnSave=False)
    #@+node:ekr.20210901140645.16: *3* TestCommands.test_c_checkPythonNode
    def test_c_checkPythonNode(self):
        c , p = self.c, self.c.p
        p.b = textwrap.dedent("""\
            @language python

            def abc:  # missing parens.
                pass
        """)
        result = c.checkPythonCode(
            checkOnSave=False,
            event=None,
            ignoreAtIgnore=True,
            suppressErrors=True,
            unittestFlag=True,
        )
        self.assertEqual(result, 'error')
    #@+node:ekr.20210901140645.7: *3* TestCommands.test_c_config_initIvar_sets_commander_ivars
    def test_c_config_initIvar_sets_commander_ivars(self):
        c = self.c
        for ivar,setting_type,default in g.app.config.ivarsData:
            assert hasattr(c,ivar),ivar
            assert hasattr(c.config,ivar),ivar
            val = getattr(c.config,ivar)
            val2 = c.config.get(ivar,setting_type)
            assert val == val2,"%s %s" % (val,val2)
    #@+node:ekr.20210901140645.17: *3* TestCommands.test_c_tabNannyNode
    def test_c_tabNannyNode(self):
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
    #@+node:ekr.20210901140645.27: *3* TestCommands.test_koi8_r_encoding
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
        
    #@+node:ekr.20210901140645.9: *3* TestCommands.test_official_commander_ivars
    def test_official_commander_ivars(self):
        c = self.c
        f = c.frame
        self.assertEqual(c, f.c)
        self.assertEqual(f, c.frame)
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
            self.assertTrue(hasattr(c, ivar), msg=ivar)
    #@-others
#@-others
#@-leo
