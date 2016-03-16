#@+leo-ver=5-thin
#@+node:ekr.20160316065700.1: * @file ../test/report_test.py
'''Test file for HTMLReportTraverser class.'''
#@+<< includes >>
#@+node:ekr.20160316065936.1: ** << includes >>
import ast
import xml.sax.saxutils as saxutils
import leo.core.leoGlobals as g
#@-<< includes >>
#@+others
#@+node:ekr.20160316070146.1: ** class TestClass
class TestClass(object):
    '''A class exercising important cases in the HTMLReportTraverser code.'''
    #@+others
    #@+node:ekr.20160316070255.1: *3* if_tests
    def if_tests(self, a, b):
        '''Test if statements, especially 'elif' vs. 'else if'.'''
        if a and b:
            rt.gen("<div class='%s' %s>" % (full_class_name, extra))
        elif a:
            rt.gen("<div class='%s'>" % (full_class_name))
        else:
            assert not extra
            rt.gen("<div>")
        if a:
            print('a')
        else: # elif is not correct here.
            if b:
                print(b)
            print(c)
    #@+node:ekr.20160316070709.1: *3* comprehension_tests
    def comprehension_tests(self):
        '''Test comprehensions'''
        for i, aList in enumerate(self.line_tokens):
            print('hi')
        return [z for z in aList if self.token_kind(z) == 'string']
    #@+node:ekr.20160316081359.1: *3* try_tests
    def try_tests(self):
        '''Test try/except/finally'''
        try:
            for z in node.optional_vars:
                vars_list.append(self.visit(z))
        except TypeError:
            vars_list.append(self.visit(node.optional_vars))
        finally:
            print('ooops')
            raise
        
    #@-others
#@-others

#@-leo
