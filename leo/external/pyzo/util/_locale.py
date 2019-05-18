# -*- coding: utf-8 -*-
# Copyright (C) 2013, the Pyzo development team
#
# Pyzo is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

""" pyzo.util._locale
Module for locale stuff like language and translations.
"""

import os, sys, time

import pyzo
from pyzo.util.qt import QtCore, QtWidgets

QLocale = QtCore.QLocale

# Define supported languages. The key defines the name as shown to the
# user. The value is passed to create a Locale object. From the local
# object we obtain the name for the .tr file.
# Chinese:
LANGUAGES = {
    'English (US)': QLocale.C,
    # == (QLocale.English, QLocale.UnitedStates),
    #'English (UK)': (QLocale.English, QLocale.UnitedKingdom),
    'Dutch': QLocale.Dutch,
    'Spanish': QLocale.Spanish,
    'Catalan': QLocale.Catalan,
    'French': QLocale.French,
    'German': QLocale.German,
    'Russian': QLocale.Russian,  # not updated for 3.4
    'Portuguese': QLocale.Portuguese,
    'Portuguese (BR)': (QLocale.Portuguese, QLocale.Brazil),
    'Simplified Chinese': QLocale.Chinese,
    'Traditional Chinese': (QLocale.Chinese, QLocale.Taiwan),  # https://bugreports.qt.io/browse/QTBUG-1573
    # Languages for which the is a .tr file, but no translations available yet:
    # 'Slovak': QLocale.Slovak,
    }


LANGUAGE_SYNONYMS = {   None: 'English (US)',
                        '': 'English (US)',
                        'English': 'English (US)',
                        'ca_ES' : 'Catalan',
                        'de_DE' : 'German',
                        'es_ES' : 'Spanish',
                        'fr_FR' : 'French',
                        'nl_NL' : 'Dutch',
                        'pt_BR' : 'Portuguese (BR)',
                        'pt_PT' : 'Portuguese',
                        'ru_RU' : 'Russian',
                        'zh_CN' : 'Simplified Chinese',
                        'zh_TW' : 'Traditional Chinese'
                     }


def getLocale(languageName):
    """ getLocale(languageName)
    Get the QLocale object for the given language (as a string).
    """
    
    # Try System  Language if nothing defined
    if languageName == "":
         languageName = QLocale.system().name()
            
    # Apply synonyms
    languageName = LANGUAGE_SYNONYMS.get(languageName, languageName)
    
    # if no language applicable, get back to default
    if LANGUAGES.get(languageName, None) is None:
         languageName = LANGUAGE_SYNONYMS.get("", "")
            
    # Select language in qt terms
    qtLanguage = LANGUAGES.get(languageName, None)
    if qtLanguage is None:
        raise ValueError('Unknown language')
    
    # Return locale
    if isinstance(qtLanguage, tuple):
        return QLocale(*qtLanguage)
    else:
        return QLocale(qtLanguage)


def setLanguage(languageName):
    """ setLanguage(languageName)
    Set the language for the app. Loads qt and pyzo translations.
    Returns the QLocale instance to pass to the main widget.
    """
    
    # Get locale
    locale = getLocale(languageName)
    
    # Get paths were language files are
    qtTransPath = str(QtCore.QLibraryInfo.location(
                    QtCore.QLibraryInfo.TranslationsPath))
    pyzoTransPath = os.path.join(pyzo.pyzoDir, 'resources', 'translations')
    
    # Get possible names for language files
    # (because Qt's .tr files may not have the language component.)
    localeName1 = locale.name()
    localeName2 = localeName1.split('_')[0]
    
    # Uninstall translators
    if not hasattr(QtCore, '_translators'):
        QtCore._translators = []
    for trans in QtCore._translators:
        QtWidgets.QApplication.removeTranslator(trans)
    
    # The default language
    if localeName1 == 'C':
        return locale
    
    # Set Qt translations
    # Note that the translator instances must be stored
    # Note that the load() method is very forgiving with the file name
    for what, where in [('qt', qtTransPath),('pyzo', pyzoTransPath)]:
        trans = QtCore.QTranslator()
        # Try loading both names
        for localeName in [localeName1, localeName2]:
            success = trans.load(what + '_' + localeName + '.tr', where)
            if success:
                QtWidgets.QApplication.installTranslator(trans)
                QtCore._translators.append(trans)
                print('loading %s %s: ok' % (what, languageName))
                break
        else:
            print('loading %s %s: failed' % (what, languageName))
    
    # Done
    return locale



class Translation(str):
    """ Derives from str class. The translate function returns an instance
    of this class and assigns extra atrributes:
      * original: the original text passed to the translation
      * tt: the tooltip text
      * key: the original text without tooltip (used by menus as a key)
    
    We adopt a simple system to include tooltip text in the same
    translation as the label text. By including ":::" in the text,
    the text after that identifier is considered the tooltip.
    The text returned by the translate function is always the
    string without tooltip, but the text object has an attribute
    "tt" that stores the tooltip text. In this way, if you do not
    use this feature or do not know about this feature, everything
    keeps working as expected.
    """
    pass


def _splitMainAndTt(s):
        if ':::' in s:
            parts = s.split(':::', 1)
            return parts[0].rstrip(), parts[1].lstrip()
        else:
            return s, ''


def translate(context, text, disambiguation=None):
    """ translate(context, text, disambiguation=None)
    The translate function used throughout pyzo.
    """
    # Get translation and split tooltip
    newtext = QtCore.QCoreApplication.translate(context, text, disambiguation)
    s, tt = _splitMainAndTt(newtext)
    # Create translation object (string with extra attributes)
    translation = Translation(s)
    translation.original = text
    translation.tt = tt
    translation.key = _splitMainAndTt(text)[0].strip()
    return translation



## Development tools
import subprocess

LHELP = """
Language help - info for translaters

For translating, you will need a set of working Qt language tools:
pyside-lupdate, linguist, lrelease. On Windows, these should come
with your PySide installation. On (Ubuntu) Linux, you can install
these with 'sudo apt-get install pyside-tools qt4-dev-tools'.

You also need to run pyzo from source as checked out from the repo
(e.g. by running pyzolauncher.py).

To create a new language:
  * the file 'pyzo/util/locale.py' should be edited to add the language
    to the LANGUAGES dict
  * run 'linguist(your_lang)', this will raise an erro, but it will show
    the name of the .tr file
  * the file 'pyzo/pyzo.pro' should be edited to include the new .tr file
  * run 'lupdate()' to create the .tr file
  * run 'linguist(your_lang)' again to initialize the .tr file.

To update a language:
  * run 'lupdate()'
  * run 'linguist(your_lang)'
  * make all the translations and save
  * run lrelease() and restart pyzo to see translations
  * repeat if necessary

"""

def lhelp():
    """ lhelp()
    Print help text on using the language tools.
    """
    print(LHELP)


def linguist(languageName):
    """ linguist(languageName)
    Open linguist with the language file as specified by lang. The
    languageName can be one of the fields as visible in the language
    list in the menu. This function is intended for translators.
    """
    # Get locale
    locale = getLocale(languageName)
    
    # Get file to open
    fname = 'pyzo_{}.tr'.format(locale.name())
    filename = os.path.join(pyzo.pyzoDir, 'resources', 'translations', fname)
    if not os.path.isfile(filename):
        raise ValueError('Could not find {}'.format(filename))
    
    # Get Command for linguist
    pysideDir = os.path.abspath(os.path.dirname(pyzo.QtCore.__file__))
    ISWIN = sys.platform.startswith('win')
    exe_ = 'linguist' + '.exe' * ISWIN
    exe = os.path.join(pysideDir, exe_)
    if not os.path.isfile(exe):
        exe = exe_
    
    # Spawn process
    return subprocess.Popen([exe , filename])


def lupdate():
    """ For developers. From pyzo.pro create the .tr files
    """
    # Get file to open
    fname = 'pyzo.pro'
    filename = os.path.realpath(os.path.join(pyzo.pyzoDir, '..', fname))
    if not os.path.isfile(filename):
        raise ValueError('Could not find {}. This function must run from the source repo.'.format(fname))
   
    # Get Command for python lupdate
    pysideDir = os.path.abspath(os.path.dirname(pyzo.QtCore.__file__))
    ISWIN = sys.platform.startswith('win')
    exe_ = 'pylupdate' + pyzo.QtCore.__version__[0] + '.exe' * ISWIN
    exe = os.path.join(pysideDir, exe_)
    if not os.path.isfile(exe):
        exe = exe_
    
    # Spawn process
    cmd = [exe, '-noobsolete', '-verbose', filename]
    p = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while p.poll() is None:
        time.sleep(0.1)
    output =  p.stdout.read().decode('utf-8')
    if p.returncode:
        raise RuntimeError('lupdate failed (%i): %s' % (p.returncode, output))
    else:
        print(output)


def lrelease():
    """ For developers. From pyzo.pro and the .tr files, create the .qm files.
    """
    # Get file to open
    fname = 'pyzo.pro'
    filename = os.path.realpath(os.path.join(pyzo.pyzoDir, '..', fname))
    if not os.path.isfile(filename):
        raise ValueError('Could not find {}. This function must run from the source repo.'.format(fname))
   
    # Get Command for lrelease
    pysideDir = os.path.abspath(os.path.dirname(pyzo.QtCore.__file__))
    ISWIN = sys.platform.startswith('win')
    exe_ = 'lrelease' + '.exe' * ISWIN
    exe = os.path.join(pysideDir, exe_)
    if not os.path.isfile(exe):
        exe = exe_
    
    # Spawn process
    cmd = [exe, filename]
    p = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while p.poll() is None:
        time.sleep(0.1)
    output =  p.stdout.read().decode('utf-8')
    if p.returncode:
        raise RuntimeError('lrelease failed (%i): %s' % (p.returncode, output))
    else:
        print(output)


if __name__ == '__main__':
    # Print names of translator files
    
    print('Language data files:')
    for key in LANGUAGES:
        s = '{}: {}'.format(key, getLocale(key).name()+'.tr')
        print(s)
