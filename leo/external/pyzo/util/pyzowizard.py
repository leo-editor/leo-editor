# -*- coding: utf-8 -*-
# Copyright (C) 2013, the Pyzo development team
#
# Pyzo is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

""" pyzowizard module

Implements a wizard to help new users get familiar with pyzo.

"""

import os
import re

import pyzo
from pyzo.util.qt import QtCore, QtGui, QtWidgets
from pyzo import translate

from pyzo.util._locale import LANGUAGES, LANGUAGE_SYNONYMS, setLanguage


def retranslate(t):
    """ To allow retranslating after selecting the language.
    """
    if hasattr(t, 'original'):
        return translate('wizard', t.original)
    else:
        return t



class PyzoWizard(QtWidgets.QWizard):
    
    def __init__(self, parent):
        QtWidgets.QWizard.__init__(self, parent)
        
        # Set some appearance stuff
        self.setMinimumSize(600, 500)
        self.setWindowTitle(translate('wizard', 'Getting started with Pyzo'))
        self.setWizardStyle(self.ModernStyle)
        self.setButtonText(self.CancelButton, 'Stop')
        
        # Set logo
        pm = QtGui.QPixmap()
        pm.load(os.path.join(pyzo.pyzoDir, 'resources', 'appicons', 'pyzologo48.png'))
        self.setPixmap(self.LogoPixmap, pm)
        
        # Define pages
        klasses = [ IntroWizardPage,
                    TwocomponentsWizardPage, EditorWizardPage,
                    ShellWizardPage1, ShellWizardPage2,
                    RuncodeWizardPage1, RuncodeWizardPage2,
                    ToolsWizardPage1, ToolsWizardPage2,
                    FinalPage]
        
        # Create pages
        self._n = len(klasses)
        for i, klass in enumerate(klasses):
            self.addPage(klass(self, i))
    
    def show(self, startPage=None):
        """ Show the wizard. If startPage is given, open the Wizard at
        that page. startPage can be an integer or a string that matches
        the classname of a page.
        """
        QtWidgets.QWizard.show(self)
        
        # Check startpage
        if isinstance(startPage, int):
            pass
        elif isinstance(startPage, str):
            for i in range(self._n):
                page = self.page(i)
                if page.__class__.__name__.lower() == startPage.lower():
                    startPage = i
                    break
            else:
                print('Pyzo wizard: Could not find start page: %r' % startPage)
                startPage = None
        elif startPage is not None:
            print('Pyzo wizard: invalid start page: %r' % startPage)
            startPage = None
        
        # Go to start page
        if startPage is not None:
            for i in range(startPage):
                self.next()


class BasePyzoWizardPage(QtWidgets.QWizardPage):
    
    _prefix = translate('wizard', 'Step')
    
    _title = 'dummy title'
    _descriptions = []
    _image_filename = ''
    
    def __init__(self, parent, i):
        QtWidgets.QWizardPage.__init__(self, parent)
        self._i = i
        
        # Create label for description
        self._text_label = QtWidgets.QLabel(self)
        self._text_label.setTextFormat(QtCore.Qt.RichText)
        self._text_label.setWordWrap(True)
        
        # Create label for image
        self._comicLabel = QtWidgets.QLabel(self)
        pm = QtGui.QPixmap()
        if 'logo' in self._image_filename:
            pm.load(os.path.join(pyzo.pyzoDir, 'resources', 'appicons', self._image_filename))
        elif self._image_filename:
            pm.load(os.path.join(pyzo.pyzoDir, 'resources', 'images', self._image_filename))
        self._comicLabel.setPixmap(pm)
        self._comicLabel.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        
        # Layout
        theLayout = QtWidgets.QVBoxLayout(self)
        self.setLayout(theLayout)
        #
        theLayout.addWidget(self._text_label)
        theLayout.addStretch()
        theLayout.addWidget(self._comicLabel)
        theLayout.addStretch()
    
    
    def initializePage(self):
        
        # Get prefix
        i = self._i
        n = self.wizard()._n - 2 # Dont count the first and last page
        prefix = ''
        if i and i <= n:
            prefix = retranslate(self._prefix) + ' %i/%i: ' % (i, n)
        
        # Set title
        self.setTitle(prefix + retranslate(self._title))
        
        # Parse description
        # Two description units are separated with BR tags
        # Emphasis on words is set to italic tags.
        lines = []
        descriptions = [retranslate(d).strip() for d in self._descriptions]
        for description in descriptions:
            for line in description.splitlines():
                line = line.strip()
                line = re.sub(r'\*(.+?)\*', r'<b>\1</b>', line)
                lines.append(line)
            lines.append('<br /><br />')
        lines = lines[:-1]
        
        # Set description
        self._text_label.setText('\n'.join(lines))



class IntroWizardPage(BasePyzoWizardPage):
    
    _title = translate('wizard', 'Welcome to the Interactive Editor for Python!')
    _image_filename = 'pyzologo128.png'
    _descriptions = [
        translate('wizard', """This wizard helps you get familiarized with the workings of Pyzo."""),
        
        translate('wizard', """Pyzo is a cross-platform Python IDE
        focused on *interactivity* and *introspection*, which makes it
        very suitable for scientific computing. Its practical design
        is aimed at *simplicity* and *efficiency*."""),
        ]
    
    def __init__(self, parent, i):
        BasePyzoWizardPage.__init__(self, parent, i)
        
        # Create label and checkbox
        t1 = translate('wizard', "This wizard can be opened using 'Help > Pyzo wizard'")
        # t2 = translate('wizard', "Show this wizard on startup")
        self._label_info = QtWidgets.QLabel(t1, self)
        #self._check_show = QtWidgets.QCheckBox(t2, self)
        #self._check_show.stateChanged.connect(self._setNewUser)
        
        # Create language switcher
        self._langLabel = QtWidgets.QLabel(translate('wizard', "Select language"), self)
        #
        self._langBox = QtWidgets.QComboBox(self)
        self._langBox.setEditable(False)
        # Fill
        index, theIndex = -1, -1
        cur = pyzo.config.settings.language
        for lang in sorted(LANGUAGES):
            index += 1
            self._langBox.addItem(lang)
            if lang == LANGUAGE_SYNONYMS.get(cur, cur):
                theIndex = index
        # Set current index
        if theIndex >= 0:
            self._langBox.setCurrentIndex(theIndex)
        # Bind signal
        self._langBox.activated.connect(self.onLanguageChange)
        
        # Init check state
        #if pyzo.config.state.newUser:
        #    self._check_show.setCheckState(QtCore.Qt.Checked)
        
        # Create sublayout
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self._langLabel, 0)
        layout.addWidget(self._langBox, 0)
        layout.addStretch(2)
        self.layout().addLayout(layout)
        
        # Add to layout
        self.layout().addSpacing(10)
        self.layout().addWidget(self._label_info)
        #self.layout().addWidget(self._check_show)
        
    def _setNewUser(self, newUser):
        newUser = bool(newUser)
        self._label_info.setHidden(newUser)
        pyzo.config.state.newUser = newUser
    
    def onLanguageChange(self):
        languageName = self._langBox.currentText()
        if pyzo.config.settings.language == languageName:
            return
        # Save new language
        pyzo.config.settings.language = languageName
        setLanguage(pyzo.config.settings.language)
        # Notify user
        text = translate('wizard', """
        The language has been changed for this wizard.
        Pyzo needs to restart for the change to take effect application-wide.
        """)
        m = QtWidgets.QMessageBox(self)
        m.setWindowTitle(translate("wizard", "Language changed"))
        m.setText(text)
        m.setIcon(m.Information)
        m.exec_()
        
        # Get props of current wizard
        geo = self.wizard().geometry()
        parent = self.wizard().parent()
        # Close ourself!
        self.wizard().close()
        # Start new one
        w = PyzoWizard(parent)
        w.setGeometry(geo)
        w.show()



class TwocomponentsWizardPage(BasePyzoWizardPage):
    
    _title = translate('wizard', 'Pyzo consists of two main components')
    _image_filename = 'pyzo_two_components.png'
    _descriptions = [
        translate('wizard',
        "You can execute commands directly in the *shell*,"),
        translate('wizard',
        "or you can write code in the *editor* and execute that."),
        ]


class EditorWizardPage(BasePyzoWizardPage):
    
    _title = translate('wizard', 'The editor is where you write your code')
    _image_filename = 'pyzo_editor.png'
    _descriptions = [
        translate('wizard',
        """In the *editor*, each open file is represented as a tab. By
        right-clicking on a tab, files can be run, saved, closed, etc."""),
        translate('wizard',
        """The right mouse button also enables one to make a file the
        *main file* of a project. This file can be recognized by its star
        symbol, and it enables running the file more easily."""),
        ]


class ShellWizardPage1(BasePyzoWizardPage):
    
    _title = translate('wizard', 'The shell is where your code gets executed')
    _image_filename = 'pyzo_shell1.png'
    _descriptions = [
        translate('wizard',
        """When Pyzo starts, a default *shell* is created. You can add more
        shells that run simultaneously, and which may be of different
        Python versions."""),
        translate('wizard',
        """Shells run in a sub-process, such that when it is busy, Pyzo
        itself stays responsive, allowing you to keep coding and even
        run code in another shell."""),
        ]


class ShellWizardPage2(BasePyzoWizardPage):
    
    _title = translate('wizard', 'Configuring shells')
    _image_filename = 'pyzo_shell2.png'
    _descriptions = [
        translate('wizard',
        """Pyzo can integrate the event loop of five different *GUI toolkits*,
        thus enabling interactive plotting with e.g. Visvis or Matplotlib."""),
        translate('wizard',
        """Via 'Shell > Edit shell configurations', you can edit and add
        *shell configurations*. This allows you to for example select the
        initial directory, or use a custom Pythonpath."""),
        ]


class RuncodeWizardPage1(BasePyzoWizardPage):
    
    _title = translate('wizard', 'Running code')
    _image_filename = 'pyzo_run1.png'
    _descriptions = [
        translate('wizard',
        "Pyzo supports several ways to run source code in the editor. (see the 'Run' menu)."),
        translate('wizard',
        """*Run selection:* if there is no selected text, the current line
        is executed; if the selection is on a single line, the selection
        is evaluated; if the selection spans multiple lines, Pyzo will
        run the the (complete) selected lines."""),
        translate('wizard',
        "*Run cell:* a cell is everything between two lines starting with '##'."),
        translate('wizard',
        "*Run file:* run all the code in the current file."),
        translate('wizard',
        "*Run project main file:* run the code in the current project's main file."),
        ]


class RuncodeWizardPage2(BasePyzoWizardPage):
    
    _title = translate('wizard', 'Interactive mode vs running as script')
    _image_filename = ''
    _descriptions = [
        translate('wizard',
        """You can run the current file or the main file normally, or as a script.
        When run as script, the shell is restared to provide a clean
        environment. The shell is also initialized differently so that it
        closely resembles a normal script execution."""),
        translate('wizard',
        """In interactive mode, sys.path[0] is an empty string (i.e. the current dir),
        and sys.argv is set to ['']."""),
        translate('wizard',
        """In script mode, __file__ and sys.argv[0] are set to the scripts filename,
        sys.path[0] and the working dir are set to the directory containing the script."""),
        ]


class ToolsWizardPage1(BasePyzoWizardPage):
    
    _title = translate('wizard', 'Tools for your convenience')
    _image_filename = 'pyzo_tools1.png'
    _descriptions = [
        translate('wizard',
        """Via the *Tools menu*, one can select which tools to use. The tools can
        be positioned in any way you want, and can also be un-docked."""),
        translate('wizard',
        """Note that the tools system is designed such that it's easy to
        create your own tools. Look at the online wiki for more information,
        or use one of the existing tools as an example."""),
        ]


class ToolsWizardPage2(BasePyzoWizardPage):
    
    _title = translate('wizard', 'Recommended tools')
    _image_filename = 'pyzo_tools2.png'
    _descriptions = [
        translate('wizard',
        """We especially recommend the following tools:"""),
        translate('wizard',
        """The *Source structure tool* gives an outline of the source code."""),
        translate('wizard',
        """The *File browser tool* helps keep an overview of all files
        in a directory. To manage your projects, click the star icon."""),
        ]


class FinalPage(BasePyzoWizardPage):
    
    _title = translate('wizard', 'Get coding!')
    _image_filename = 'pyzologo128.png'
    _descriptions = [
        translate('wizard',
        """This concludes the Pyzo wizard. Now, get coding and have fun!"""),
        ]


# def smooth_images():
#     """ This was used to create the images from their raw versions.
#     """
#
#     import os
#     import visvis as vv
#     import scipy as sp
#     import scipy.ndimage
#     for fname in os.listdir('images'):
#         im = vv.imread(os.path.join('images', fname))
#         for i in range(im.shape[2]):
#             im[:,:,i] = sp.ndimage.gaussian_filter(im[:,:,i], 0.7)
#         #fname = fname.replace('.png', '.jpg')
#         print(fname)
#         vv.imwrite(fname, im[::2,::2,:])


if __name__ == '__main__':
    w = PyzoWizard(None)
    w.show()
    
