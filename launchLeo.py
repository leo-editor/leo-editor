#!/usr/bin/env python

""" Leo launcher script
A minimal script to launch leo.
"""

import leo.core.runLeo  # Overrides sys.excepthook.
leo.core.runLeo.run()
