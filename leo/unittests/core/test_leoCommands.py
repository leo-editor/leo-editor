# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20210903162431.1: * @file ../unittests/core/test_leoCommands.py
#@@first
"""Tests of leoCommands.py"""
# pylint: disable=no-member
import inspect
import textwrap
from leo.core import leoGlobals as g
from leo.core.leoTest2 import LeoUnitTest

#@+others
#@+node:ekr.20210903162431.2: ** class TestCommands(LeoUnitTest)
class TestCommands(LeoUnitTest):
    """Test cases for leoCommands.py"""
    #@+others
    #@+node:ekr.20210906075242.1: *3* --- Converted nodes
    #@+node:ekr.20210906075242.28: *3* TestCommands.test_add_comments_with_multiple_language_directives
    def test_add_comments_with_multiple_language_directives(self):
        c = self.c
        p = c.p
        w = c.frame.body.wrapper
        s = textwrap.dedent("""\
            @language rest
            rest text.
            @language python
            def spam():
                # pass
            # after
    """)
        assert s  ###
        table = (
            (
                False,
                '@language rest\nrest text.\n@language python\ndef spam():\n    pass\n# after',
                '@language rest\nrest text.\n@language python\ndef spam():\n#     pass\n# after',
            ),
            (
                True,
                '@language rest\nrest text.\n@language python\ndef spam():\n    pass\n# after',
                '@language rest\nrest text.\n@language python\ndef spam():\n    # pass\n# after',
            ),
        )
        for indent, s1, expected in table:
            # Step 1: set the setting.
            c.config.set(None, 'bool', 'indent_added_comments', indent, warn=False)
            val = c.config.getBool('indent_added_comments')
            assert indent == val, (repr(indent), repr(val))
            # Step 2: set p.b and the insert point.
            c.selectPosition(p)
            p.b = s1
            i = p.b.find('pass')
            assert i > -1,'fail1: %s' % (repr(p.b))
            w.setSelectionRange(i,i+4)
            # Step 3: test add-comments
            c.addComments()
            ### assert p.b == expected, ('indent: %5s got:\n%r\nexpected:\n%r' % (indent, p.b, expected))
            self.assertEqual(p.b, expected)
    #@+node:ekr.20210906075242.30: *3* TestCommands.test_add_html_comments
    def test_add_html_comments(self):
        c = self.c
        p = c.p
        w = c.frame.body.wrapper
        ### p = g.findNodeInTree(c,p,'html')
        ### assert p,'not found: html'
        s = textwrap.dedent("""\
            @language html
            <html>
                <!-- text -->
            </html>
    """)
        assert s  ###
        old_indent = c.config.getBool('indent_added_comments',default=True)
        table = (
            (
                False,
                '@language html\n<html>\ntext\n</html>\n',
                '@language html\n<html>\n<!-- text -->\n</html>\n',
            ),
            (
                True,
                '@language html\n<html>\n    text\n</html>\n',
                '@language html\n<html>\n    <!-- text -->\n</html>\n'
            ),
        )
        try:
            for indent, s1, expected in table:
                # Step 1: set the setting.
                c.config.set(None, 'bool', 'indent_added_comments', indent, warn=False)
                val = c.config.getBool('indent_added_comments')
                assert indent == val, (repr(indent), repr(val))
                # Step 2: set p.b and the insert point.
                c.selectPosition(p)
                p.b = s1
                i = p.b.find('text')
                assert i > -1,'fail1: %s' % (repr(p.b))
                w.setSelectionRange(i,i+4)
                # Step 3: test add-comments
                c.addComments()
                assert p.b == expected, ('indent: %5s got:\n%r\nexpected:\n%r' % (indent, p.b, expected))
        finally:
            c.config.set(p, 'bool', 'indent_added_comments', old_indent)
            val = c.config.getBool('indent_added_comments')
            assert old_indent == val, (repr(indent), repr(val))
    #@+node:ekr.20210906075242.32: *3* TestCommands.test_add_python_comments
    def test_add_python_comments(self):
        c = self.c
        p = c.p
        w = c.frame.body.wrapper
        ### p = g.findNodeInTree(c,p,'python')
        ### assert p,'not found: python'
        s = textwrap.dedent("""\
            @language python
            def spam():
            #     pass
            
            # after
    """)
        assert s  ###
        old_indent = c.config.getBool('indent_added_comments',default=True)
        table = (
            (
                True,
                '@language python\ndef spam():\n    pass\n\n# after',
                '@language python\ndef spam():\n    # pass\n\n# after',
            ),
            (
                False,
                '@language python\ndef spam():\n    pass\n\n# after',
                '@language python\ndef spam():\n#     pass\n\n# after',
            ),
        )
        try:
            for indent, s1, expected in table:
                # Step 1: set the setting.
                c.config.set(None, 'bool', 'indent_added_comments', indent, warn=False)
                val = c.config.getBool('indent_added_comments')
                assert indent == val, (repr(indent), repr(val))
                # Step 2: set p.b and the insert point.
                c.selectPosition(p)
                p.b = s1
                i = p.b.find('pass')
                assert i > -1,'fail1: %s' % (repr(p.b))
                w.setSelectionRange(i,i+4)
                # Step 3: test add-comments
                c.addComments()
                assert p.b == expected, ('indent: %5s got:\n%r\nexpected:\n%r' % (indent, p.b, expected))
        finally:
            c.config.set(p, 'bool', 'indent_added_comments', old_indent)
            val = c.config.getBool('indent_added_comments')
            assert old_indent == val, (repr(indent), repr(val))
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
    #@+node:ekr.20210906075242.2: *3* TestCommands.test_c_alert
    def test_c_alert(self):
        c = self.c
        c.alert('test of c.alert')
    #@+node:ekr.20210906075242.3: *3* TestCommands.test_c_checkOutline
    def test_c_checkOutline(self):
        c = self.c
        errors = c.checkOutline()
        assert errors == 0, "Check Outline reported %d errors" % errors
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
    #@+node:ekr.20210906075242.4: *3* TestCommands.test_c_contractAllHeadlines
    def test_c_contractAllHeadlines(self):
        c = self.c
        c.contractAllHeadlines()
        p = c.rootPosition()
        while p.hasNext():
            p.moveToNext()
        c.selectPosition(p)
    #@+node:ekr.20210906075242.6: *3* TestCommands.test_c_demote_illegal_clone_demote
    def test_c_demote_illegal_clone_demote(self):
        c = self.c
        p = c.p
        # Remove any previous children.
        while p.hasChildren():
            p.firstChild().doDelete()
        # Create two cloned children.
        c.selectPosition(p)
        c.insertHeadline()
        p2 = c.p
        p2.moveToFirstChildOf(p)
        p2.setHeadString('aClone')
        c.selectPosition(p2)
        c.clone()
        assert 2 == p.numberOfChildren()

        # Select the first clone and demote (it should be illegal)
        c.selectPosition(p2)
        c.demote() # This should do nothing.
        assert g.app.unitTestDict.get('checkMoveWithParentWithWarning'),'fail 1'
        assert 0 == c.checkOutline(), 'fail 2'
        assert 2 == p.numberOfChildren(), 'fail 3'
        # Delete the children, but only if there are no errors.
        while p.hasChildren():
            p.firstChild().doDelete()
    #@+node:ekr.20210906075242.7: *3* TestCommands.test_c_expand_path_expression
    def test_c_expand_path_expression(self):
        c = self.c
        import os
        sep = os.sep
        table = (
            ('~{{sep}}tmp{{sep}}x.py', '~%stmp%sx.py' % (sep, sep)),
        )
        for s, expected in table:
            if g.isWindows:
                expected = expected.replace('\\','/')
            got = c.expand_path_expression(s)
            assert got==expected,'s: %r expected: %r got: %r' % (s,expected,got)
    #@+node:ekr.20210906075242.8: *3* TestCommands.test_c_findMatchingBracket
    def test_c_findMatchingBracket(self):
        c = self.c
        w = c.frame.body.wrapper
        s = w.getAllText()
        i = s.find('(')
        w.setInsertPoint(i)
        c.findMatchingBracket(event=None)
        i,j = w.getSelectionRange()
        assert i < j,'i: %s j: %s' % (i,j)
    #@+node:ekr.20210906075242.9: *3* TestCommands.test_c_hiddenRootNode_fileIndex
    def test_c_hiddenRootNode_fileIndex(self):
        c = self.c
        assert c.hiddenRootNode.fileIndex.startswith('hidden-root-vnode-gnx'), c.hiddenRootNode.fileIndex
    #@+node:ekr.20210906075242.10: *3* TestCommands.test_c_hoist_chapter_node
    def test_c_hoist_chapter_node(self):
        c = self.c
        # # # p1 = g.findNodeAnywhere(c,'@chapter aaa')
        # # # assert p1
        # # # p2 = g.findNodeAnywhere(c,'aaa node 1')
        # # # assert p2
        
        p1 = None  ### To do: create @settings, etc.
       
        # g.es_print('**1**', c.hoistStack)
        assert not c.hoistStack, ('fail1', c.hoistStack)
        c.selectPosition(p1)
        assert c.p == p1, ('fail2', c.p, p1)
        c.hoist()
            # New in Leo 5.3: should do nothing
        assert c.p == p1, ('fail3', c.p, p1)
        # assert c.p == p2, ('fail3', c.p, p2)
        c.dehoist()
            # New in Leo 5.3: should do nothing:
        assert c.p == p1, ('fail3', c.p, p1)
        # assert c.p == p2, 'fail4\n%s\n%s' % (c.p, p2)
        assert c.hoistStack == [], ('fail5', c.hoistStack)
    #@+node:ekr.20210906075242.11: *3* TestCommands.test_c_hoist_followed_by_goto_first_node
    def test_c_hoist_followed_by_goto_first_node(self):
        c = self.c
        assert not c.hoistStack
        c.hoist()
        c.goToFirstNode()
        assert not c.hoistStack
            # The hoist stack must be cleared to show the first node.
        assert c.p == c.rootPosition()
        assert c.p.isVisible(c)
    #@+node:ekr.20210906075242.12: *3* TestCommands.test_c_hoist_with_no_children
    def test_c_hoist_with_no_children(self):
        c = self.c
        c.hoist()
        c.dehoist()
    #@+node:ekr.20210906075242.13: *3* TestCommands.test_c_insertBodyTime
    def test_c_insertBodyTime(self):
        c = self.c
        # p = c.p
        # w = c.frame.body.wrapper
        # s = w.getAllText()
        # w.setInsertPoint(len(s))
        c.insertBodyTime()
    #@+node:ekr.20210906075242.14: *3* TestCommands.test_c_markAllAtFileNodesDirty
    def test_c_markAllAtFileNodesDirty(self):
        c = self.c
        marks = [p.v for p in c.all_positions() if p.isMarked()]
        try:
            ok = True
            try:
                c.markAllAtFileNodesDirty()
            except Exception:
                g.es_exception()
                ok = False
        finally:
            for p in c.all_positions():
                if p.v in marks:
                    if not p.isMarked():
                        c.setMarked(p)
                else:
                    if p.isMarked():
                        c.clearMarked(p)

        assert ok
    #@+node:ekr.20210906075242.15: *3* TestCommands.test_c_markSubheads
    def test_c_markSubheads(self):
        c = self.c
        child1 = c.rootPosition().insertAsLastChild()
        child2 = c.rootPosition().insertAsLastChild()
        assert child1 and child2
        c.markSubheads()
    #@+node:ekr.20210906075242.16: *3* TestCommands.test_c_pasteOutline_does_not_clone_top_node
    def test_c_pasteOutline_does_not_clone_top_node(self):
        c = self.c
        p = c.p
        p.b = '# text.'
        # child1 = c.rootPosition().insertAsLastChild()
        # c.selectPosition(child)
        c.copyOutline()
        p2 = c.pasteOutline()
        assert p2
        assert not p2.isCloned()
    #@+node:ekr.20210906075242.17: *3* TestCommands.test_c_scanAllDirectives
    def test_c_scanAllDirectives(self):
        c = self.c
        p = c.p
        # # # @language python
        # # # @comment a b c
            # # # # @comment must follow @language
        # # # @tabwidth -4
        # # # @pagewidth 72
        # # # @encoding utf-8
        # # # @lineending crlf

        d = c.scanAllDirectives(p)

        table = (
            ('delims', ('a','b','c'),),
            ('encoding','utf-8'),
            ('language','python'),
            ('lineending','\r\n'),
            ('pagewidth',72),
            ('tabwidth',-4),
        )

        for kind,expected in table:
            got = d.get(kind)
            assert got == expected, 'kind: %s, expected %s, got %s' % (
                kind,repr(expected),repr(got))
    #@+node:ekr.20210906075242.18: *3* TestCommands.test_c_scanAtPathDirectives
    def test_c_scanAtPathDirectives(self):
        c = self.c
        p = c.p
        ### p2 = p.firstChild().firstChild().firstChild()
        child = p.insertAfter()
        grand = child.insertAsLastChild()
        great = grand.insertAsLastChild()
        aList = g.get_directives_dict_list(great)
        path = c.scanAtPathDirectives(aList)
        endpath = g.os_path_normpath('one/two')
        assert path and path.endswith(endpath),'expected ending %s got %s' % (
            endpath,path)
    #@+node:ekr.20210906075242.19: *3* TestCommands.test_c_scanAtPathDirectives_same_name_subdirs
    def test_c_scanAtPathDirectives_same_name_subdirs(self):
        c = self.c
        # p2 = p.firstChild().firstChild().firstChild()
        p = c.p
        child = p.insertAfter()
        child.h = '@path again'
        grand = child.insertAsLastChild()
        grand.h = '@path again'
        great = grand.insertAsLastChild()
        great.h = 'xyz'
        aList = g.get_directives_dict_list(great)
        path = c.scanAtPathDirectives(aList)
        endpath = g.os_path_normpath('again/again')
        self.assertTrue(path and path.endswith(endpath))
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
    #@+node:ekr.20210906075242.20: *3* TestCommands.test_c_unmarkAll
    def test_c_unmarkAll(self):
        c = self.c
        c.unmarkAll()
        for p in c.all_positions():
            assert not p.isMarked(), p.h
    #@+node:ekr.20210906075242.21: *3* TestCommands.test_class_StubConfig
    def test_class_StubConfig(self):
        c = self.c
        class StubConfig(g.NullObject):
            pass

        x = StubConfig()
        assert not x.getBool(c,'mySetting')
        assert not x.enabledPluginsFileName
    #@+node:ekr.20210906075242.29: *3* TestCommands.test_delete_comments_with_multiple_at_language_directives
    def test_delete_comments_with_multiple_at_language_directives(self):
        c = self.c
        p = c.p
        w = c.frame.body.wrapper
        ### p = g.findNodeInTree(c,p,'rest and python')
        ### assert p,'not found: rest and python'
        s = textwrap.dedent("""\
            @language rest
            rest text.
            @language python
            def spam():
                pass
            # after
    """)
        assert s  ###
        old_indent = c.config.getBool('indent_added_comments',default=True)
        table = (
            (
                False,
                '@language rest\nrest text.\n@language python\ndef spam():\n#     pass\n# after',
                '@language rest\nrest text.\n@language python\ndef spam():\n    pass\n# after',
            ),
            (
                True,
                '@language rest\nrest text.\n@language python\ndef spam():\n    # pass\n# after',
                '@language rest\nrest text.\n@language python\ndef spam():\n    pass\n# after',
            ),
        )
        try:
            for indent, s1, expected in table:
                # Step 1: set the setting.
                c.config.set(None, 'bool', 'indent_added_comments', indent, warn=False)
                val = c.config.getBool('indent_added_comments')
                assert indent == val, (repr(indent), repr(val))
                # Step 2: set p.b and the insert point.
                c.selectPosition(p)
                p.b = s1
                i = p.b.find('pass')
                assert i > -1,'fail1: %s' % (repr(p.b))
                w.setSelectionRange(i,i+4)
                # Step 3: test add-comments
                c.deleteComments()
                assert p.b == expected, ('indent: %5s got:\n%r\nexpected:\n%r' % (indent, p.b, expected))
        finally:
            c.config.set(p, 'bool', 'indent_added_comments', old_indent)
            val = c.config.getBool('indent_added_comments')
            assert old_indent == val, (repr(indent), repr(val))
    #@+node:ekr.20210906075242.31: *3* TestCommands.test_delete_html_comments
    def test_delete_html_comments(self):
        c = self.c
        p = c.p
        w = c.frame.body.wrapper
        ### p = g.findNodeInTree(c,p,'html')
        ### assert p,'not found: html'
        s = textwrap.dedent("""\
            @language html
            <html>
                text
            </html>
    """)
        assert s  ###
        old_indent = c.config.getBool('indent_added_comments',default=True)
        table = (
            (
                False,
                '@language html\n<html>\n<!-- text -->\n</html>\n',
                '@language html\n<html>\ntext\n</html>\n',
            ),
            (
                True,
                '@language html\n<html>\n    <!-- text -->\n</html>\n',
                '@language html\n<html>\n    text\n</html>\n',
            ),
        )
        try:
            for indent, s1, expected in table:
                # Step 1: set the setting.
                c.config.set(None, 'bool', 'indent_added_comments', indent, warn=False)
                val = c.config.getBool('indent_added_comments')
                assert indent == val, (repr(indent), repr(val))
                # Step 2: set p.b and the insert point.
                c.selectPosition(p)
                p.b = s1
                i = p.b.find('text')
                assert i > -1,'fail1: %s' % (repr(p.b))
                w.setSelectionRange(i,i+4)
                # Step 3: test delete-comments
                c.deleteComments()
                assert p.b == expected, ('indent: %5s got:\n%r\nexpected:\n%r' % (indent, p.b, expected))
        finally:
            c.config.set(p, 'bool', 'indent_added_comments', old_indent)
            val = c.config.getBool('indent_added_comments')
            assert old_indent == val, (repr(indent), repr(val))
    #@+node:ekr.20210906075242.33: *3* TestCommands.test_delete_python_comments
    def test_delete_python_comments(self):
        c = self.c
        p = c.p
        w = c.frame.body.wrapper
        ### p = g.findNodeInTree(c, p,'python')
        ### assert p,'not found: python'
        s = textwrap.dedent("""\
            @language python
            def spam():
                pass
            
            # after
    """)
        assert s  ###
        old_indent = c.config.getBool('indent_added_comments',default=True)
        table = (
            (
                True,
                '@language python\ndef spam():\n    # pass\n\n# after',
                '@language python\ndef spam():\n    pass\n\n# after',
            ),
            (
                False,
                '@language python\ndef spam():\n#     pass\n\n# after',
                '@language python\ndef spam():\n    pass\n\n# after',
            ),
        )
        try:
            for indent, s1, expected in table:
                # Step 1: set the setting.
                c.config.set(None, 'bool', 'indent_added_comments', indent, warn=False)
                val = c.config.getBool('indent_added_comments')
                assert indent == val, (repr(indent), repr(val))
                # Step 2: set p.b and the insert point.
                c.selectPosition(p)
                p.b = s1
                i = p.b.find('pass')
                assert i > -1,'fail1: %s' % (repr(p.b))
                w.setSelectionRange(i,i+4)
                # Step 3: test delete-comments
                c.deleteComments()
                assert p.b == expected, ('indent: %5s got:\n%r\nexpected:\n%r' % (indent, p.b, expected))
        finally:
            c.config.set(p, 'bool', 'indent_added_comments', old_indent)
            val = c.config.getBool('indent_added_comments')
            assert old_indent == val, (repr(indent), repr(val))
    #@+node:ekr.20210906075242.22: *3* TestCommands.test_efc_ask
    def test_efc_ask(self):
        c = self.c
        p = c.p
        # Not a perfect test, but stil significant.
        efc = g.app.externalFilesController
        if not efc:
            self.skipTest('No externalFilesController')
        result = efc.ask(c,p.h)
        assert result in (True, False),result
    #@+node:ekr.20210906075242.23: *3* TestCommands.test_efc_compute_ext
    def test_efc_compute_ext(self):
        c = self.c
        p = c.p
        ### @language python

        efc = g.app.externalFilesController
        if not efc:
            self.skipTest('No externalFilesController')
        table = (
            # (None,'.py'),
            # ('','.py'),
            ('txt','.txt'),
            ('.txt','.txt'),
        )
        for ext,result in table:
            result2 = efc.compute_ext(c,p,ext)
            assert result==result2,'ext: %s, expected %s, got %s' % (
                repr(ext),repr(result),repr(result2))
    #@+node:ekr.20210906075242.24: *3* TestCommands.test_efc_compute_temp_file_path
    def test_efc_compute_temp_file_path(self):
        c = self.c
        p = c.p
        efc = g.app.externalFilesController
        if not efc:
            self.skipTest('no externalFilesController')
        s = efc.compute_temp_file_path(c, p,'.py')
        assert s.endswith('.py')
    #@+node:ekr.20210906075242.25: *3* TestCommands.test_g_command_decorator
    def test_g_command_decorator(self):
        
        # pylint: disable=global-variable-undefined
        c = self.c
        _foo = 0

        @g.command('my-test-command')
        def mytestcommand(event):
            global _foo
            _foo = 1

        try:
            c.k.simulateCommand('my-test-command')
            assert _foo == 1
        
            # bonus test: c.app.commanders()
            assert c in g.app.commanders()

        except AttributeError:
            # Raised only for unit testing.
            pass
    #@+node:ekr.20210906075242.26: *3* TestCommands.test_g_isCallable
    def test_g_isCallable(self):
        c = self.c
        
        def spam():
            pass

        lam = lambda a: None
        
        class aCallable:
            def __call__ (self):
                pass

        c = aCallable()
        table = (
            ('abc',False),
            (spam,True),
            (lam,True),
            (c,True)
        )
        for obj,val in table:
            val2 = g.isCallable(obj)
            assert val == val2,'%s, expected %s, got %s' % (
                repr(obj),val,val2)
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
