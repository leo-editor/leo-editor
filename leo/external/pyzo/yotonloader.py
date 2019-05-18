""" This is a bit awkward, but yoton is a package that is designed to
work from Python 2.4 to Python 3.x. As such, it does not have relative
imports and must be imported as an absolute package. That is what this
module does...
"""

import os
import sys

# Import yoton
sys.path.insert(0, os.path.dirname(__file__))
import yoton  # noqa

# Reset
sys.path.pop(0)
