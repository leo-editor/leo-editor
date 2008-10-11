import os
os.chdir('../plugins')
os.system('pyuic4 -o qt_main.py qt_main.ui')
os.system('pyuic4 -o qt_quicksearch.py qt_quicksearch.ui')
