"""
leo_cloud.py - synchronize Leo subtrees with remote central server

(this is the server half, see also leo_cloud.py for the Leo plugin)

Terry N. Brown, terrynbrown@gmail.com, Fri Sep 22 10:34:10 2017
"""

import os
import sys
from collections import namedtuple, defaultdict
