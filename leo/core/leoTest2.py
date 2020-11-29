#@+leo-ver=5-thin
#@+node:ekr.20201129023817.1: * @file leoTest2.py
"""
Support for coverage tests embedded in Leo's source files.

The general pattern is inspired by the coverage tests in leoAst.py.

Each of Leo's source files will end with:
    
    if __name__ == '__main__':
        run_unit_tests()
        
Full unit tests for x.py can be run from the command line:
    
    python -m leo.core.x
"""
#@-leo
