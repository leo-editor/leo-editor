#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EKR:change-startup. Add leo/plugins/pyzo to sys.path and import pyzo."""
try:
    import leo.core.leoGlobals as leo_g
    leo_g.pr('pyzo.__main__.py')
except Exception:
    leo_g.pr('FAIL: import leo_g')
    leo_g = None
    
# import os
# import sys

# EKR:change-startup. We *are* running a script.
# However, it's probably already too late to do this.
    # thisDir = os.path.abspath(os.path.dirname(__file__))
    # sys.path.insert(0, os.path.split(thisDir)[0])
try:
    import pyzo
except ImportError:
    raise ImportError('Could not import leo/plugins/pyzo.') # EKR:change-message.

def main():
    pyzo.start()
        # Defined in pyzo.__init__.
###
    # if __name__ == '__main__':
        # main()
pyzo.start_pyzo_in_leo() # EKR: change-startup.
