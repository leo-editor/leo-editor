'''Adapted from
    https://dzone.com/articles/bypassing-windows-10-uac-withnbsppython
'''
import os
import sys
import ctypes
import winreg

def is_running_as_admin():
    '''
    Checks if the script is running with administrative privileges.
    Returns True if is running as admin, False otherwise.
    '''    
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False
def execute():
    if not is_running_as_admin():
        print('[!] The script is NOT running with administrative privileges')
    else:
        print('[+] The script is running with administrative privileges!')
if __name__ == '__main__':
    execute()