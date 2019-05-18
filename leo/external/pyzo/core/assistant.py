# -*- coding: utf-8 -*-
# Copyright (C) 2016, the Pyzo development team
# Author: Windel Bouwman
#
# Pyzo is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

"""
Tool that can view qt help files via the qthelp engine.

Run make_docs.sh from:
https://bitbucket.org/windel/qthelpdocs

Copy the "docs" directory to the pyzo root!

"""

from pyzo.util.qt import QtCore, QtGui, QtWidgets  # noqa
from pyzo import getResourceDirs
import os


help_help = """
<h1>Documentation</h1>
<p>
Welcome to the Pyzo assistant. Pyzo uses the Qt Help system for documentation.
This is also used by the Qt Assistant. You can use this viewer
to view documentation provided by other projects.
</p>

<h2>Add documentation</h2>
<p>
To add documentation to Pyzo, go to the settings tab and select add. Then
select a Qt Compressed Help file (*.qch). qch-files can be found in the Qt
installation directory (for example in /usr/share/doc/qt under linux). For
other projects you can download pre-build qch files from here:
<a href="https://github.com/windelbouwman/qthelpdocs/releases">https://github.com/windelbouwman/qthelpdocs/releases</a>.

</p>

<p>
<strong>Note</strong>
When a documentation file is added, it is not copied into the pyzo settings
dir, so you have to leave this file in place.
</p>

"""

tool_name = "Assistant"
tool_summary = "Browse qt help documents"


class Settings(QtWidgets.QWidget):
    def __init__(self, engine):
        super().__init__()
        self._engine = engine
        layout = QtWidgets.QVBoxLayout(self)
        add_button = QtWidgets.QPushButton("Add")
        del_button = QtWidgets.QPushButton("Delete")
        self._view = QtWidgets.QListView()
        layout.addWidget(self._view)
        layout2 = QtWidgets.QHBoxLayout()
        layout2.addWidget(add_button)
        layout2.addWidget(del_button)
        layout.addLayout(layout2)
        self._model = QtCore.QStringListModel()
        self._view.setModel(self._model)

        self._model.setStringList(self._engine.registeredDocumentations())

        add_button.clicked.connect(self.add_doc)
        del_button.clicked.connect(self.del_doc)

    def add_doc(self):
        doc_file = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select a compressed help file",
            filter="Qt compressed help files (*.qch)")
        if isinstance(doc_file, tuple):
            doc_file = doc_file[0]
        self.add_doc_do(doc_file)

    def add_doc_do(self, doc_file):
        ok = self._engine.registerDocumentation(doc_file)
        if ok:
            self._model.setStringList(self._engine.registeredDocumentations())
        else:
            QtWidgets.QMessageBox.critical(self, "Error", "Error loading doc")

    def del_doc(self):
        idx = self._view.currentIndex()
        if idx.isValid():
            doc_file = self._model.data(idx, QtCore.Qt.DisplayRole)
            self.del_doc_do(doc_file)

    def del_doc_do(self, doc_file):
        self._engine.unregisterDocumentation(doc_file)
        self._model.setStringList(self._engine.registeredDocumentations())


class HelpBrowser(QtWidgets.QTextBrowser):
    """ Override textbrowser to implement load resource """
    def __init__(self, engine):
        super().__init__()
        self._engine = engine

        # Override default navigation behavior:
        self.anchorClicked.connect(self.handle_url)
        self.setOpenLinks(False)

    def handle_url(self, url):
        """ Open external urls not in this viewer """
        if url.scheme() in ['http', 'https']:
            QtGui.QDesktopServices.openUrl(url)
        else:
            self.setSource(url)

    def loadResource(self, typ, url):
        if url.scheme() == "qthelp":
            return self._engine.fileData(url)
        else:
            return super().loadResource(typ, url)


class PyzoAssistant(QtWidgets.QWidget):
    """
        Show help contents and browse qt help files.
    """
    def __init__(self, parent=None, collection_filename=None):
        """
            Initializes an assistance instance.
            When collection_file is none, it is determined from the
            appDataDir.
        """
        from pyzo.util.qt import QtHelp
        super().__init__(parent)
        self.setWindowTitle('Help')
        pyzoDir, appDataDir = getResourceDirs()
        if collection_filename is None:
            # Collection file is stored in pyzo data dir:
            collection_filename = os.path.join(appDataDir, 'tools', 'docs.qhc')
        self._engine = QtHelp.QHelpEngine(collection_filename)

        # Important, call setup data to load the files:
        self._engine.setupData()

        # If no files are loaded, register at least the pyzo docs:
        if len(self._engine.registeredDocumentations()) == 0:
            doc_file = os.path.join(pyzoDir, 'resources', 'pyzo.qch')
            self._engine.registerDocumentation(doc_file)

        # The main players:
        self._content = self._engine.contentWidget()
        self._index = self._engine.indexWidget()
        self._indexTab = QtWidgets.QWidget()
        il = QtWidgets.QVBoxLayout(self._indexTab)
        filter_text = QtWidgets.QLineEdit()
        il.addWidget(filter_text)
        il.addWidget(self._index)

        self._helpBrowser = HelpBrowser(self._engine)
        self._searchEngine = self._engine.searchEngine()
        self._settings = Settings(self._engine)

        self._progress = QtWidgets.QWidget()
        pl = QtWidgets.QHBoxLayout(self._progress)
        bar = QtWidgets.QProgressBar()
        bar.setMaximum(0)
        pl.addWidget(QtWidgets.QLabel('Indexing'))
        pl.addWidget(bar)

        self._searchResultWidget = self._searchEngine.resultWidget()
        self._searchQueryWidget = self._searchEngine.queryWidget()
        self._searchTab = QtWidgets.QWidget()
        search_layout = QtWidgets.QVBoxLayout(self._searchTab)
        search_layout.addWidget(self._searchQueryWidget)
        search_layout.addWidget(self._searchResultWidget)

        tab = QtWidgets.QTabWidget()
        tab.addTab(self._content, "Contents")
        tab.addTab(self._indexTab, "Index")
        tab.addTab(self._searchTab, "Search")
        tab.addTab(self._settings, "Settings")

        splitter = QtWidgets.QSplitter(self)
        splitter.addWidget(tab)
        splitter.addWidget(self._helpBrowser)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(splitter)
        layout.addWidget(self._progress)

        # Connect clicks:
        self._content.linkActivated.connect(self._helpBrowser.setSource)
        self._index.linkActivated.connect(self._helpBrowser.setSource)
        self._searchEngine.searchingFinished.connect(self.onSearchFinish)
        self._searchEngine.indexingStarted.connect(self.onIndexingStarted)
        self._searchEngine.indexingFinished.connect(self.onIndexingFinished)
        filter_text.textChanged.connect(self._index.filterIndices)
        self._searchResultWidget.requestShowLink.connect(self._helpBrowser.setSource)
        self._searchQueryWidget.search.connect(self.goSearch)

        # Always re-index on startup:
        self._searchEngine.reindexDocumentation()

        self._search_term = None

        # Show initial page:
        # self.showHelpForTerm('welcome to pyzo')
        self._helpBrowser.setHtml(help_help)

    def goSearch(self):
        query = self._searchQueryWidget.query()
        self._searchEngine.search(query)

    def onIndexingStarted(self):
        self._progress.show()

    def onIndexingFinished(self):
        self._progress.hide()

    def find_best_page(self, hits):
        if self._search_term is None:
            url, _ = hits[0]
            return url

        try:
            # Try to find max with fuzzy wuzzy:
            from fuzzywuzzy import fuzz
            url, title = max(hits, key=lambda hit: fuzz.ratio(hit[1], self._search_term))
            return url
        except ImportError:
            pass

        # Find exact page title:
        for url2, page_title in hits:
            if page_title == self._search_term:
                url = url2
                return url

        for url2, page_title in hits:
            if self._search_term in page_title:
                url = url2
                return url

        # Pick first hit:
        url, _ = hits[0]
        return url

    def onSearchFinish(self, hits):
        if hits == 0:
            return
        hits = self._searchEngine.hits(0, hits)
        if not hits:
            return
        url = self.find_best_page(hits)
        self._helpBrowser.setSource(QtCore.QUrl(url))

    def showHelpForTerm(self, name):
        from pyzo.util.qt import QtHelp
        # Cache for later use:
        self._search_term = name

        # Create a query:
        query = QtHelp.QHelpSearchQuery(QtHelp.QHelpSearchQuery.DEFAULT, [name])
        self._searchEngine.search([query])


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    view = PyzoAssistant()
    view.show()
    app.exec()
