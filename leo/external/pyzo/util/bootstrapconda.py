"""
Tools to install miniconda from pyzo and register that env in pyzo's
shell config.
"""

import os
import sys
import stat
import time
import struct
import shutil
import threading
import subprocess
import urllib.request

import pyzo
from pyzo.util.qt import QtCore, QtWidgets
from pyzo import translate

base_url = 'http://repo.continuum.io/miniconda/'
links = {'win32': 'Miniconda3-latest-Windows-x86.exe',
         'win64': 'Miniconda3-latest-Windows-x86_64.exe',
         'osx64': 'Miniconda3-latest-MacOSX-x86_64.sh',
         'linux32': 'Miniconda3-latest-Linux-x86.sh',
         'linux64': 'Miniconda3-latest-Linux-x86_64.sh',
         'arm': 'Miniconda3-latest-Linux-armv7l.sh',  # raspberry pi
         }


# Get where we want to put miniconda installer
miniconda_path = os.path.join(pyzo.appDataDir, 'miniconda')
miniconda_path += '.exe' if sys.platform.startswith('win') else '.sh'

# Get default dir where we want the env
#default_conda_dir = os.path.join(pyzo.appDataDir, 'conda_root')
default_conda_dir = 'C:\\miniconda3' if sys.platform.startswith('win') else os.path.expanduser('~/miniconda3')


def check_for_conda_env(parent=None):
    """ Check if it is reasonable to ask to install a conda env. If
    users says yes, do it. If user says no, don't, and remember.
    """
    
    # Interested previously?
    if getattr(pyzo.config.state, 'did_not_want_conda_env', False):
        print('User has previously indicated to have no interest in a conda env')
        return
    
    # Needed?
    if pyzo.config.shellConfigs2:
        exe = pyzo.config.shellConfigs2[0]['exe']
        r = ''
        try:
            r = subprocess.check_output([exe, '-m', 'conda', 'info'], shell=sys.platform.startswith('win'))
            r = r.decode()
        except Exception:
            pass  # no Python or no conda
        if r and 'is foreign system : False' in r:
            print('First shell config looks like a conda env.')
            return
    
    # Ask if interested now?
    d = AskToInstallConda(parent)
    d.exec_()
    if not d.result():
        pyzo.config.state.did_not_want_conda_env = True  # Mark for next time
        return
    
    # Launch installer
    d = Installer(parent)
    d.exec_()


class AskToInstallConda(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setWindowTitle('Install a conda env?')
        self.setModal(True)
        
        text = 'Pyzo is only an editor. To execute code, you need a Python environment.\n\n'
        text += 'Do you want Pyzo to install a Python environment (miniconda)?\n'
        text += 'If not, you must arrange for a Python interpreter yourself'
        if not sys.platform.startswith('win'):
            text += ' or use the system Python'
        text += '.'
        text += '\n(You can always launch the installer from the shell menu.)'
        
        self._label = QtWidgets.QLabel(text, self)
        self._no = QtWidgets.QPushButton("No thanks (dont ask again)")
        self._yes = QtWidgets.QPushButton("Yes, please install Python!")
        
        self._no.clicked.connect(self.reject)
        self._yes.clicked.connect(self.accept)
        
        vbox = QtWidgets.QVBoxLayout(self)
        hbox = QtWidgets.QHBoxLayout()
        self.setLayout(vbox)
        vbox.addWidget(self._label, 1)
        vbox.addLayout(hbox, 0)
        hbox.addWidget(self._no, 2)
        hbox.addWidget(self._yes, 2)
        
        self._yes.setDefault(1)


class Installer(QtWidgets.QDialog):
    
    lineFromStdOut = QtCore.Signal(str)
    
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setWindowTitle('Install miniconda')
        self.setModal(True)
        self.resize(500, 500)
        
        text = translate('bootstrapconda', 'This will download and install miniconda on your computer.')
        
        self._label = QtWidgets.QLabel(text, self)
        
        self._scipystack = QtWidgets.QCheckBox(translate('bootstrapconda', 'Also install scientific packages'), self)
        self._scipystack.setChecked(True)
        self._path = QtWidgets.QLineEdit(default_conda_dir, self)
        self._progress = QtWidgets.QProgressBar(self)
        self._outputLine = QtWidgets.QLabel(self)
        self._output = QtWidgets.QPlainTextEdit(self)
        self._output.setReadOnly(True)
        self._button = QtWidgets.QPushButton('Install', self)
        
        self._outputLine.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Fixed)
        
        vbox = QtWidgets.QVBoxLayout(self)
        self.setLayout(vbox)
        vbox.addWidget(self._label, 0)
        vbox.addWidget(self._path, 0)
        vbox.addWidget(self._scipystack, 0)
        vbox.addWidget(self._progress, 0)
        vbox.addWidget(self._outputLine, 0)
        vbox.addWidget(self._output, 1)
        vbox.addWidget(self._button, 0)
        
        self._button.clicked.connect(self.go)
        
        self.addOutput(translate('bootstrapconda', 'Waiting to start installation.\n'))
        self._progress.setVisible(False)
        
        self.lineFromStdOut.connect(self.setStatus)
    
    def setStatus(self, line):
        self._outputLine.setText(line)
    
    def addOutput(self, text):
        #self._output.setPlainText(self._output.toPlainText() + '\n' + text)
        cursor = self._output.textCursor()
        cursor.movePosition(cursor.End, cursor.MoveAnchor)
        cursor.insertText(text)
        cursor.movePosition(cursor.End, cursor.MoveAnchor)
        self._output.setTextCursor(cursor)
        self._output.ensureCursorVisible()
    
    def addStatus(self, line):
        self.addOutput('\n' + line)
        self.setStatus(line)
    
    def go(self):
        
        # Check if we can install
        try:
            self._conda_dir = self._path.text()
            if not os.path.isabs(self._conda_dir):
                raise ValueError('Given installation path must be absolute.')
            if os.path.exists(self._conda_dir):
                raise ValueError('The given installation path already exists.')
        except Exception as err:
            self.addOutput('\nCould not install:\n' + str(err))
            return
        
        ok = False
        
        try:
            
            # Disable user input, get ready for installation
            self._progress.setVisible(True)
            self._button.clicked.disconnect()
            self._button.setEnabled(False)
            self._scipystack.setEnabled(False)
            self._path.setEnabled(False)
            
            if not os.path.exists(self._conda_dir):
                self.addStatus('Downloading installer ... ')
                self._progress.setMaximum(100)
                self.download()
                self.addStatus('Done downloading installer.')
                self.make_done()
                
                self.addStatus('Installing (this can take a minute) ... ')
                self._progress.setMaximum(0)
                ret = self.install()
                self.addStatus(('Failed' if ret else 'Done') + ' installing.')
                self.make_done()
            
            self.post_install()
            
            if self._scipystack.isChecked():
                self.addStatus('Installing scientific packages ... ')
                self._progress.setMaximum(0)
                ret = self.install_scipy()
                self.addStatus('Done installing scientific packages')
                self.make_done()
            
            self.addStatus('Verifying ... ')
            self._progress.setMaximum(100)
            ret = self.verify()
            if ret:
                self.addOutput('Error\n' + ret)
                self.addStatus('Verification Failed!')
            else:
                self.addOutput('Done verifying')
                self.addStatus('Ready to go!')
                self.make_done()
                ok = True
        
        except Exception as err:
            self.addStatus('Installation failed ...')
            self.addOutput('\n\nException!\n' + str(err))
        
        if not ok:
            self.addOutput('\n\nWe recommend installing miniconda or anaconda, ')
            self.addOutput('and making Pyzo aware if it via the shell configuration.')
        else:
            self.addOutput('\n\nYou can install additional packages by running "conda install" in the shell.')
        
        # Wrap up, allow user to exit
        self._progress.hide()
        self._button.setEnabled(True)
        self._button.setText('Close')
        self._button.clicked.connect(self.close)
    
    def make_done(self):
        self._progress.setMaximum(100)
        self._progress.setValue(100)
        etime = time.time() + 0.2
        while time.time() < etime:
            time.sleep(0.01)
            QtWidgets.qApp.processEvents()
    
    def download(self):
        
        # Installer already downloaded?
        if os.path.isfile(miniconda_path):
            self.addOutput('Already downloaded.')
            return  # os.remove(miniconda_path)
        
        # Get url key
        key = ''
        if sys.platform.startswith('win'):
            key = 'win'
        elif sys.platform.startswith('darwin'):
            key = 'osx'
        elif sys.platform.startswith('linux'):
            key = 'linux'
        key += '64' if is_64bit() else '32'
        
        # Get url
        if key not in links:
            raise RuntimeError('Cannot download miniconda for this platform.')
        url = base_url + links[key]
        
        _fetch_file(url, miniconda_path, self._progress)
    
    def install(self):
        dest = self._conda_dir
        
        # Clear dir
        assert not os.path.isdir(dest), 'Miniconda dir already exists'
        assert ' ' not in dest, 'miniconda dest path must not contain spaces'
        
        if sys.platform.startswith('win'):
            return self._run_process([miniconda_path, '/S', '/D=%s' % dest])
        else:
            os.chmod(miniconda_path, os.stat(miniconda_path).st_mode | stat.S_IEXEC)
            return self._run_process([miniconda_path, '-b', '-p', dest])
    
    def post_install(self):
        
        exe = py_exe(self._conda_dir)
        
        # Add Pyzo channel
        cmd = [exe, '-m', 'conda', 'config', '--system', '--add', 'channels', 'pyzo']
        subprocess.check_call(cmd, shell=sys.platform.startswith('win'))
        self.addStatus('Added Pyzo channel to conda env')
        
        # Add to pyzo shell config
        if pyzo.config.shellConfigs2 and pyzo.config.shellConfigs2[0]['exe'] == exe:
            pass
        else:
            s = pyzo.ssdf.new()
            s.name = 'Py3-conda'
            s.exe = exe
            s.gui='PyQt4'
            pyzo.config.shellConfigs2.insert(0, s)
            pyzo.saveConfig()
            self.addStatus('Prepended new env to Pyzo shell configs.')
    
    def install_scipy(self):
        
        packages = ['numpy', 'scipy', 'pandas', 'matplotlib', 'sympy',
                    #'scikit-image', 'scikit-learn',
                    'pyopengl', # 'visvis', 'imageio',
                    'tornado', 'pyqt', #'ipython', 'jupyter',
                    #'requests', 'pygments','pytest',
                    ]
        exe = py_exe(self._conda_dir)
        cmd = [exe, '-m', 'conda', 'install', '--yes'] + packages
        return self._run_process(cmd)
    
    def _run_process(self, cmd):
        """ Run command in a separate process, catch stdout, show lines
        in the output label. On fail, show all output in output text.
        """
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=sys.platform.startswith('win'))
        catcher = StreamCatcher(p.stdout, self.lineFromStdOut)
        
        while p.poll() is None:
            time.sleep(0.01)
            QtWidgets.qApp.processEvents()
        
        catcher.join()
        if p.poll():
            self.addOutput(catcher.output())
        return p.poll()
    
    def verify(self):
        
        self._progress.setValue(1)
        if not os.path.isdir(self._conda_dir):
            return 'Conda dir not created.'
        
        self._progress.setValue(11)
        exe = py_exe(self._conda_dir)
        if not os.path.isfile(exe):
            return 'Conda dir does not have Python exe'
        
        self._progress.setValue(21)
        try:
            ver = subprocess.check_output([exe, '-c', 'import sys; print(sys.version)'])
        except Exception as err:
            return 'Error getting Python version: ' + str(err)
        
        self._progress.setValue(31)
        if ver.decode() < '3.4':
            return 'Expected Python version 3.4 or higher'
        
        self._progress.setValue(41)
        try:
            ver = subprocess.check_output([exe, '-c', 'import conda; print(conda.__version__)'])
        except Exception as err:
            return 'Error calling Python exe: ' + str(err)
        
        self._progress.setValue(51)
        if ver.decode() < '3.16':
            return 'Expected Conda version 3.16 or higher'
        
        # Smooth toward 100%
        for i in range(self._progress.value(), 100, 5):
            time.sleep(0.05)
            self._progress.setValue(i)
            QtWidgets.qApp.processEvents()


def is_64bit():
    """ Get whether the OS is 64 bit. On WIndows yields what it *really*
    is, not what the process is.
    """
    if False:#sys.platform.startswith('win'):  ARG, causes problems with subprocess
        if 'PROCESSOR_ARCHITEW6432' in os.environ:
            return True
        return os.environ['PROCESSOR_ARCHITECTURE'].endswith('64')
    else:
        return struct.calcsize('P') == 8


def py_exe(dir):
    if sys.platform.startswith('win'):
        return os.path.join(dir, 'python.exe')
    else:
        return os.path.join(dir, 'bin', 'python')


def _chunk_read(response, local_file, chunk_size=1024, initial_size=0, progress=None):
    """Download a file chunk by chunk and show advancement
    """
    # Adapted from NISL:
    # https://github.com/nisl/tutorial/blob/master/nisl/datasets.py

    bytes_so_far = initial_size
    # Returns only amount left to download when resuming, not the size of the
    # entire file
    total_size = int(response.headers['Content-Length'].strip())
    total_size += initial_size
    
    if progress:
        progress.setMaximum(total_size)
    
    while True:
        QtWidgets.qApp.processEvents()
        chunk = response.read(chunk_size)
        bytes_so_far += len(chunk)
        if not chunk:
            sys.stderr.write('\n')
            break
        #_chunk_write(chunk, local_file, progress)
        progress.setValue(bytes_so_far)
        local_file.write(chunk)


def _fetch_file(url, file_name, progress=None):
    """Load requested file, downloading it if needed or requested
    """
    # Adapted from NISL:
    # https://github.com/nisl/tutorial/blob/master/nisl/datasets.py

    temp_file_name = file_name + ".part"
    local_file = None
    initial_size = 0
    try:
        # Checking file size and displaying it alongside the download url
        response = urllib.request.urlopen(url, timeout=5.)
        # file_size = int(response.headers['Content-Length'].strip())
        # Downloading data (can be extended to resume if need be)
        local_file = open(temp_file_name, "wb")
        _chunk_read(response, local_file, initial_size=initial_size, progress=progress)
        # temp file must be closed prior to the move
        if not local_file.closed:
            local_file.close()
        shutil.move(temp_file_name, file_name)
    except Exception as e:
        raise RuntimeError('Error while fetching file %s.\n'
                           'Dataset fetching aborted (%s)' % (url, e))
    finally:
        if local_file is not None:
            if not local_file.closed:
                local_file.close()


class StreamCatcher(threading.Thread):

    def __init__(self, file, signal):
        self._file = file
        self._signal = signal
        self._lines = []
        self._line = ''
        threading.Thread.__init__(self)
        self.setDaemon(True)  # do not let this thread hold up Python shutdown
        self.start()
    
    def run(self):
        while True:
            time.sleep(0.0001)
            try:
                part = self._file.read(20)
            except ValueError:  # pragma: no cover
                break
            if not part:
                break
            part = part.decode('utf-8', 'ignore')
            #print(part, end='')
            
            self._line += part.replace('\r', '\n')
            lines = [line for line in self._line.split('\n') if line]
            self._lines.extend(lines[:-1])
            self._line = lines[-1]
            
            if self._lines:
                self._signal.emit(self._lines[-1])
        
        self._lines.append(self._line)
        self._signal.emit(self._lines[-1])

    def output(self):
        return '\n'.join(self._lines)


if __name__ == '__main__':
    
    check_for_conda_env()
