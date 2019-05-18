"""

The import wizard helps the user importing CSV-like data from a file into a
numpy array. The wizard containst three pages:

SelectFilePage:
    - The user selects a file and previews its contents (or, the beginning of it)
    
SetParametersPage:
    - The user selects delimiters, etc. and selects which columns to import
    - A preview of the data in tabualar form is shown, with colors indicating
      how the file is parsed: yellow for header rows, green for the comments
      column and red for values that could not be parsed
      
ResultPage:
    - The wizard shows the generated code that is to be used to import the file
      according to the settings
    - The user chooses to execute the code in the current shell or paste the
      code into the editor


"""

import unicodedata
import os.path as op

import pyzo.codeeditor
from . import QtCore, QtGui, QtWidgets
from pyzo import translate


# All keywords in Python 2 and 3. Obtained using: import keyword; keyword.kwlist
# Merged from Py2 and 3
keywords = ['False', 'None', 'True', 'and', 'as', 'assert', 'break',
    'class', 'continue', 'def', 'del', 'elif', 'else', 'except', 'exec',
    'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is',
    'lambda', 'nonlocal', 'not', 'or', 'pass', 'print', 'raise', 'return',
    'try', 'while', 'with', 'yield']


class CodeView(
    pyzo.codeeditor.IndentationGuides,
    pyzo.codeeditor.CodeFolding,
    pyzo.codeeditor.Indentation,
    pyzo.codeeditor.HomeKey,
    pyzo.codeeditor.EndKey,
    pyzo.codeeditor.NumpadPeriodKey,
    
    pyzo.codeeditor.AutoIndent,
    pyzo.codeeditor.PythonAutoIndent,
    
    pyzo.codeeditor.SyntaxHighlighting,
    
    pyzo.codeeditor.CodeEditorBase):  #CodeEditorBase must be the last one in the list
    """
    Code viewer, stripped down version of the CodeEditor
    """
    pass



class SelectFilePage(QtWidgets.QWizardPage):
    """
    First page of the wizard, select file and preview contents
    """
    def __init__(self):
        QtWidgets.QWizardPage.__init__(self)
        
        self.setTitle(translate('importwizard', 'Select file'))
        
        self.txtFilename = QtWidgets.QLineEdit()
        self.btnBrowse = QtWidgets.QPushButton(translate('importwizard', 'Browse...'))
        self.preview = QtWidgets.QPlainTextEdit()
        self.preview.setReadOnly(True)

        vlayout = QtWidgets.QVBoxLayout()
        hlayout = QtWidgets.QHBoxLayout()

        
        hlayout.addWidget(self.txtFilename)
        hlayout.addWidget(self.btnBrowse)
        vlayout.addLayout(hlayout)
        vlayout.addWidget(QtWidgets.QLabel(translate('importwizard', 'Preview:')))
        vlayout.addWidget(self.preview)
        
        self.setLayout(vlayout)
        
        self.registerField('fname', self.txtFilename)
        
        self.btnBrowse.clicked.connect(self.onBrowseClicked)
        self.txtFilename.editingFinished.connect(self.updatePreview)
        self._isComplete = False
        
    def onBrowseClicked(self):
        # Difference between PyQt4 and PySide: PySide returns filename, filter
        # while PyQt4 returns only the filename
        filename = QtWidgets.QFileDialog.getOpenFileName(filter = 'Text files (*.txt *.csv);;All files (*.*)')
        if isinstance(filename, tuple):
            filename = filename[0]
        
        filename = str(filename).replace('/', op.sep) # Show native file separator
            
        self.txtFilename.setText(filename)
        self.updatePreview()
        
    def updatePreview(self):
        filename = self.txtFilename.text()
        if not filename:
            data = ''
            self._isComplete = False
            self.wizard().setPreviewData(None)
        else:
            try:
                with open(filename,'rb') as file:
                    maxsize = 5000
                    data = file.read(maxsize)
                    more = bool(file.read(1)) # See if there is more data available
                    
                data = data.decode('ascii', 'replace')
                
                self.wizard().setPreviewData(data)

                if more:
                    data += '...'
                        
                self._isComplete = True  # Allow to proceed to the next page
            except Exception as e:
                data = str(e)
                self._isComplete = False
                self.wizard().setPreviewData(None)
            
        self.preview.setPlainText(data)
        self.completeChanged.emit()
        
    def isComplete(self):
        return self._isComplete
        
        

class SetParametersPage(QtWidgets.QWizardPage):
    def __init__(self):
        QtWidgets.QWizardPage.__init__(self)
        
        self.setTitle("Select parameters")
    
        self._columnNames = None
        
        def genComboBox(choices):
            cbx = QtWidgets.QComboBox()
            for choice in choices:
                cbx.addItem(choice)
            cbx.setEditable(True)
            return cbx

        self.cbxDelimiter = genComboBox(",;")
        self.cbxComments = genComboBox("#%'")
        self.sbSkipHeader = QtWidgets.QSpinBox()
        
        self.preview = QtWidgets.QTableWidget()
        self.preview.setSelectionModel(QtCore.QItemSelectionModel(self.preview.model())) # Work-around for reference tracking bug in PySide
        self.preview.setSelectionBehavior(self.preview.SelectColumns)
        self.preview.setSelectionMode(self.preview.MultiSelection)


        # Layout

        formlayout = QtWidgets.QFormLayout()
        formlayout.addRow('Delimiter', self.cbxDelimiter)
        formlayout.addRow('Comments', self.cbxComments)
        formlayout.addRow('Header rows to skip', self.sbSkipHeader)
        
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(formlayout)
        layout.addWidget(QtWidgets.QLabel(
            translate('importwizard', 'Select columns to import:')))
        layout.addWidget(self.preview)

        self.setLayout(layout)
        
        # Wizard fields
        self.registerField('delimiter', self.cbxDelimiter, "currentText")
        self.registerField('comments', self.cbxComments, "currentText")
        self.registerField('skip_header', self.sbSkipHeader)
        
               
        # Signals
        self.cbxComments.editTextChanged.connect(self.updatePreview)
        self.cbxDelimiter.editTextChanged.connect(self.updatePreview)
        self.sbSkipHeader.valueChanged.connect(self.updatePreview)
        self.preview.verticalHeader().sectionClicked.connect(self.onRowHeaderClicked)
    
    def columnNames(self):
        if self._columnNames is None:
            return list(['d' + str(i + 1) for i in range(self.preview.columnCount()-1)])
        
        return list(self._columnNames)
            
    
    def updateHorizontalHeaderLabels(self):
        self.preview.setHorizontalHeaderLabels(self.columnNames() + ['Comments'])

    
    def onRowHeaderClicked(self, row):
        names = self.parseColumnNames(row)
        self._columnNames = names
        self.updateHorizontalHeaderLabels()


    def parseColumnNames(self, row):
        """
        Use the data in the given row to create column names. First, try the
        data in the data columns. If these are all empty, use the comments
        column, split by the given delimiter.
        
        Names are fixed up to be valid Python 2 / Python 3 identifiers
        (chars a-z A-Z _ 0-9 , no Python 2 or 3 keywords, not starting with 0-9)
        
        returns: list of names, exactly as many as there are data columns
        """
        names = []
        columnCount = self.preview.columnCount()-1
        for col in range(columnCount):
            cell = self.preview.item(row, col)
            if cell is None:
                names.append('')
            else:
                names.append(cell.text().strip())
        
        # If no values found, try the comments:
        if not any(names):
            cell = self.preview.item(row, columnCount)
            if cell is not None:
                comment = cell.text()[1:].strip() # Remove comment char and whitespace
                delimiter = self.cbxDelimiter.currentText()
                names = list(name.strip() for name in comment.split(delimiter))
                
                # Ensure names is exactly columnCount long
                names += [''] * columnCount
                names = names[:columnCount]

        
        # Fixup names
        def fixname(name, col):
            # Remove accents
            name = ''.join(c for c in unicodedata.normalize('NFD', name)
                                        if unicodedata.category(c) != 'Mn')
            # Replace invalid chars with _
            name = ''.join(c if (c.lower()>='a' and c.lower()<='z') or (c>='0' and c<='9') else '_' for c in name)
            
            if not name:
                return 'd' + str(col)
            
            if name[0]>='0' and name<='9':
                name = 'd' + name
            
            if name in keywords:
                name = name + '_'
            
            return name

        names = list(fixname(name, i + 1) for i, name in enumerate(names))

        return names

    def selectedColumns(self):
        """
        Returns a tuple of the columns that are selected, or None if no columns
        are selected
        """
        selected = []
        for selrange in self.preview.selectionModel().selection():
            selected += range(selrange.left(), selrange.right() + 1)

        selected.sort()

        if not selected:
            return None
        else:
            return tuple(selected)

    def initializePage(self):
        self.updatePreview()
    
    def updatePreview(self):
        # Get settings from the currently specified values in the wizard
        comments = self.cbxComments.currentText()
        delimiter = self.cbxDelimiter.currentText()
        skipheader = self.sbSkipHeader.value()
        if not comments or not delimiter:
            return

        # Store current selection, will be restored at the end
        selectedColumns = self.selectedColumns()
        
        # Clear the complete table
        self.preview.clear()
        self.preview.setColumnCount(0)
        self.preview.setRowCount(0)

        # Iterate through the source file line by line
        # Process like genfromtxt, with names = False
        # However, we do keep the header lines and comments; we show them in
        # distinct colors so that the user can see how the data is selected
        
        source = iter(self.wizard().previewData().splitlines())
        


        
        def split_line(line):
            """Chop off comments, strip, and split at delimiter."""
            line, sep, commentstr = line.partition(comments)
            line = line.strip(' \r\n')
            if line:
                return line.split(delimiter), sep + commentstr
            else:
                return [], sep + commentstr
           

        # Insert comments column
        self.preview.insertColumn(0)
        
        ncols = 0           # Number of columns, excluding comments column
        headerrows = 0      # Number of header rows, including empty header rows
        
        inheader = True
        
        for lineno, line in enumerate(source):
            fields, commentstr = split_line(line)
            
            # Process header like genfromtxt, with names = False
            if lineno>=skipheader and fields:
                inheader = False

            if inheader:
                headerrows = lineno + 1 # +1 since lineno = 0 is the first line

            self.preview.insertRow(lineno)
            
            # Add columns to fit all fields
            while len(fields)>ncols:
                self.preview.insertColumn(ncols)
                ncols += 1
            
            # Add fields to the table
            for col, field in enumerate(fields):
                cell = QtWidgets.QTableWidgetItem(field)
                if not inheader:
                    try:
                        float(field)
                    except ValueError:
                        cell.setBackground(QtGui.QBrush(QtGui.QColor("pink")))
                    
                self.preview.setItem(lineno,col, cell)
            
            # Add the comment
            cell = QtWidgets.QTableWidgetItem(commentstr)
            cell.setBackground(QtGui.QBrush(QtGui.QColor("lightgreen")))
            
            self.preview.setItem(lineno,ncols, cell)
            
        # Colorize the header cells. This is done as the last step, since
        # meanwhile new columns (and thus new cells) may have been added
        for row in range(headerrows):
            for col in range(ncols):
                cell = self.preview.item(row, col)
                if not cell:
                    cell = QtWidgets.QTableWidgetItem('')
                    self.preview.setItem(row, col, cell)
                    
                cell.setBackground(QtGui.QBrush(QtGui.QColor("khaki")))
        
        # Try to restore selection
        if selectedColumns is not None:
            for column in selectedColumns:
                self.preview.selectColumn(column)
        
        # Restore column names
        self.updateHorizontalHeaderLabels()
            
        
class ResultPage(QtWidgets.QWizardPage):
    """
    The resultpage lets the user select wether to import the data as a single
    2D-array, or as one variable (1D-array) per column
    
    Then, the code to do the import is generated (Py2 and Py3 compatible). This
    code can be executed in the current shell, or copied into the current editor
    
    """
    def __init__(self):
        QtWidgets.QWizardPage.__init__(self)
        self.setTitle("Execute import")
        self.setButtonText(QtWidgets.QWizard.FinishButton,
            translate('importwizard', 'Close'))

        self.rbAsArray = QtWidgets.QRadioButton(translate('importwizard', 'Import data as single array'))
        self.rbPerColumn = QtWidgets.QRadioButton(translate('importwizard', 'Import data into one variable per column'))
        self.rbAsArray.setChecked(True)

        self.chkInvalidRaise = QtWidgets.QCheckBox(translate('importwizard', 'Raise error upon invalid data'))
        self.chkInvalidRaise.setChecked(True)

        self.codeView = CodeView()
        self.codeView.setParser('python')
        self.codeView.setZoom(pyzo.config.view.zoom)
        self.codeView.setFont(pyzo.config.view.fontname)
        
        self.btnExecute = QtWidgets.QPushButton('Execute in current shell')
        self.btnInsert = QtWidgets.QPushButton('Paste into current file')
        
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.rbAsArray)
        layout.addWidget(self.rbPerColumn)
        layout.addWidget(self.chkInvalidRaise)
        
        layout.addWidget(QtWidgets.QLabel('Resulting import code:'))
        layout.addWidget(self.codeView)
        layout.addWidget(self.btnExecute)
        layout.addWidget(self.btnInsert)
        self.setLayout(layout)
        
        self.registerField('invalid_raise', self.chkInvalidRaise)
        
        self.btnExecute.clicked.connect(self.onBtnExecuteClicked)
        self.btnInsert.clicked.connect(self.onBtnInsertClicked)
        self.rbAsArray.clicked.connect(self.updateCode)
        self.rbPerColumn.clicked.connect(self.updateCode)
        self.chkInvalidRaise.stateChanged.connect(lambda state: self.updateCode())
        
        
    def initializePage(self):
        self.updateCode()
        
    def updateCode(self):
        perColumn = self.rbPerColumn.isChecked()

        if perColumn:
            columnNames = self.wizard().field('columnnames')
            usecols = self.wizard().field('usecols')
            
            if usecols is not None: # User selected a subset of all columns
                # Pick corrsponding column names
                columnNames = [columnNames[i] for i in usecols]
            
            variables = ', '.join(columnNames)
        else:
            variables = 'data'
        
        code = "import numpy\n"
        
        code += variables + " = numpy.genfromtxt(\n"
        for param, default in (
            ('fname', None),
            ('skip_header', 0),
            ('comments', '#'),
            ('delimiter', None),
            ('usecols', None),
            ('invalid_raise', True),
            ):
                value = self.wizard().field(param)
                if value != default:
                    code += "\t%s = %r,\n" % (param, value)
        if perColumn:
            code += '\tunpack = True,\n'
        code += '\t)\n'
    
        self.codeView.setPlainText(code)
    
    def getCode(self):
        return self.codeView.toPlainText()
    
    def onBtnExecuteClicked(self):
        shell = pyzo.shells.getCurrentShell()
        if shell is None:
            QtWidgets.QMessageBox.information(self,
                translate('importwizard', 'Import data wizard'),
                translate('importwizard', 'No current shell active'))
            return
            
        shell.executeCode(self.getCode(), 'importwizard')
        
    def onBtnInsertClicked(self):
        editor = pyzo.editors.getCurrentEditor()
        if editor is None:
            QtWidgets.QMessageBox.information(self,
                translate('importwizard', 'Import data wizard'),
                translate('importwizard', 'No current file open'))
            return
        
        code = self.getCode()
        
        # Format tabs/spaces according to editor setting
        if editor.indentUsingSpaces():
            code = code.replace('\t', ' ' * editor.indentWidth())
        
        
        # insert code at start of line
        cursor = editor.textCursor()
        cursor.movePosition(cursor.StartOfBlock)
        cursor.insertText(code)
        
        
class ImportWizard(QtWidgets.QWizard):
    def __init__(self):
        QtWidgets.QWizard.__init__(self)
        self.setMinimumSize(500,400)
        self.resize(700,500)
        
        self.setPreviewData(None)
        
        self.selectFilePage = SelectFilePage()
        self.setParametersPage = SetParametersPage()
        self.resultPage = ResultPage()
        
        
        self.addPage(self.selectFilePage)
        self.addPage(self.setParametersPage)
        self.addPage(self.resultPage)
                
        self.setWindowTitle(translate('importwizard', 'Import data'))
    
        self.currentIdChanged.connect(self.onCurrentIdChanged)
        
    def onCurrentIdChanged(self, id):
        # Hide the 'cancel' button on the last page
        if self.nextId() == -1:
            self.button(QtWidgets.QWizard.CancelButton).hide()
        else:
            self.button(QtWidgets.QWizard.CancelButton).show()
    
    def open(self, filename):
        if self.isVisible():
            QtWidgets.QMessageBox.information(self,
                translate('importwizard', 'Import data wizard'),
                translate('importwizard', 'The import data wizard is already open'))
            return

        self.restart()
        self.selectFilePage.txtFilename.setText(filename)
        self.selectFilePage.updatePreview()
        self.show()
    
    def field(self, name):
        # Allow access to all data via field, some properties are not avaialble
        # as actual controls and therefore we have to handle them ourselves
        if name == 'usecols':
            return self.setParametersPage.selectedColumns()
        elif name == 'columnnames':
            return self.setParametersPage.columnNames()
        else:
            return QtWidgets.QWizard.field(self, name)
    
    def setPreviewData(self, data):
        self._previewData = data
    def previewData(self):
        if self._previewData is None:
            raise RuntimeError('Preview data not loaded')
            
        return self._previewData

if __name__=='__main__':
    iw = ImportWizard()
    iw.open('test.txt')


