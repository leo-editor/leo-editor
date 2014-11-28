'''setup.py for leo'''
import leo.core.leoVersion
from setuptools import setup, find_packages


# Note :
    # Folder without __init__.py are not included by default
    # Even if it unecessary (because no __init__.py), 
    # We explicitely exclude unwanted packages with :
    # find_packages(exclude=('leo.extensions','leo.test','leo.plugins.test',))

    #We have to specify data, ie not .py files & not __init__.py folders
    
package_data = {
# Files to include for every packages

'':['*.leo', '*.ini', '*.ui', '*.txt', '*.json', '*.css', '*.html', '*.js', '*.svg', '*.bat', '*.sh', '*.rst', '*.md'],

# Include www folder and its content. What is it for ?
'leo':['www/*'],
        
# Include icons...
'leo':[ 
        'Icons/*.*',
        'Icons/Tango/*/*/*.png', #Why this entire theme folder ?
        'Icons/recorder/*.png', 
        'Icons/cleo/*.*',  # Duplicate (Themes)
        'Icons/cleo/small/*.png'
      ],  

# Include themes icons... 
# It would be simpler to bring them on same level ex: 'themes/*/icons/*.png   
'leo':[ 
       'themes/leo_dark_0/Icons/*.png',
       'themes/leo_dark_0/Icons/cleo/*.png',# Duplicate : Icons
       'themes/leo_dark_0/Icons/cleo/*.html','themes/leo_dark_0/Icons/cleo/small/*.png',
       'themes/leo_dark_0/Icons/Tango/16x16/apps/*.png'
      ],
       
# We could also specify extensions or declare it as package with an __init__.py
'leo':['scripts/*'],
      
# For plugins we create __init__.py into sub-folders 
#Do we want to include obsolete ones ?
'leo.plugins':['*.pyd'], # Do we want it ?
'leo.plugins.qmlnb':['qml/*'],
'leo.plugins.modes':['catalog','*.xml'],

# Wouldn't it be better to install ckedito separatly ?

# Do we have to install external.obsolete ?

#Leo distribution files (do we need to install them ?)
'leo':['dist/*.*'],

}

exclude_package_data = {}

setup(
    name =     'leo'
,
    version =     leo.core.leoVersion.version
,
    author =     "Edward K. Ream"
,
    author_email =     'edreamleo@gmail.com'
,
    license =     'MIT License'
,
    description =     "Leo: Leonine Editor with Outlines"
, # becomes "Summary" in pkg-info
    long_description =     open('README.TXT', 'r').read()
,
    url =     'http://leoeditor.com'
,
    download_url =     'http://sourceforge.net/projects/leo/files/Leo/'
,
    bugtrack_url =     'https://github.com/leo-editor/leo-editor/issues'
,# pypi still needs this added manually via web form
    platforms =     ['linux','windows']
,
    requires =     ['docutils']
, # only include dependencies which can be installed by pip (so not PyQt or SIP)
    classifiers =     [
            'Development Status :: 5 - Production/Stable',
            'Environment :: Win32 (MS Windows)',
            'Environment :: X11 Applications :: Qt',
            'Intended Audience :: End Users/Desktop',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Natural Language :: English',
            'Operating System :: MacOS',
            'Operating System :: Microsoft :: Windows',
            'Operating System :: POSIX :: Linux',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 3',
            'Topic :: Software Development',
            'Topic :: Text Editors',
            'Topic :: Text Processing',
        ]
,
    packages =     find_packages(exclude=('leo.extensions','leo.test','leo.plugins.test',))
,
    package_data = package_data,
    #scripts = ['leo-install.py'],# Not needed anymore ?
    entry_points =     {
            'console_scripts': ['leoc = leo.core.runLeo:run'],
            'gui_scripts' : ['leo = leo.core.runLeo:run'],
        }
)
