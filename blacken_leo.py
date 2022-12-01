#!/usr/bin/env python3

# from leo.core import leoGlobals as g

tag = 'blacken_leo.py:'

try:
    import black
    print('blacken_leo.py: black', black)
except ImportError:
    print('blacken_leo.py: can not import black')
    
print(tag, '*** Call black.main ***')
black.main()
    
# try:
    # from black import __main__
    # print(tag, __main__)
# except Exception as e:
    # print(tag, e)
