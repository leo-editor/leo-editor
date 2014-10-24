import os
os.chdir('../plugins')
os.system('pyuic4 -o qt_main.py qt_main.ui')
# os.system('pyuic4 -o qt_quicksearch.py qt_quicksearch.ui')
    # 2014/10/24: qt_quicksearch.py now contain modified code,
    # sot it's not wise to run pyuic4 on qt_quicksearch.ui
