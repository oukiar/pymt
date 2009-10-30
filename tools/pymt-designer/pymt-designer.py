
import sys,os
os.environ['PYMT_SHADOW_WINDOW'] = 'False'

from PyQt4 import QtCore, QtGui, QtOpenGL
from OpenGL import GL
from syntaxhighlighter import Highlighter
from pymt import pymt_logger
from cStringIO import StringIO
from qtmtwindow import *
import pymt
import traceback

class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.setupFileMenu()
        self.setupEditor()
        self.setupMTWindow()
        self.central_widget = QtGui.QWidget()
        self.layout = QtGui.QHBoxLayout()
        self.layout.addWidget(self.editor)

        self.vlayout = QtGui.QVBoxLayout()
        self.vlayout.addWidget(self.glWidget)
        self.vlayout.addWidget(self.console)
        self.layout.addLayout(self.vlayout)

        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)
        self.setWindowTitle("PyMT Designer")

    def setupFileMenu(self):
        fileMenu = QtGui.QMenu("&File", self)
        self.menuBar().addMenu(fileMenu)

        fileMenu.addAction("&New...", self.newFile, "Ctrl+N")
        fileMenu.addAction("&Open...", self.openFile, "Ctrl+O")
        fileMenu.addAction("&Run", self.run, "Ctrl+R")
        fileMenu.addAction("E&xit", QtGui.qApp.quit, "Ctrl+Q")


    def setupMTWindow(self):
        pymt.pymt_config.set('modules', 'touchring', '')
        self.glWidget = QTMTWindow()


    def setupEditor(self):
        font = QtGui.QFont()
        font.setFamily('Courier')
        font.setFixedPitch(True)
        font.setPointSize(10)

        self.editor = QtGui.QTextEdit()
        self.console = QtGui.QTextEdit()
        self.console.readOnly = True
        self.console.setFont(font)
        self.editor.setFont(font)
        self.editor.setMinimumSize(400,600)
        self.highlighter = Highlighter(self.editor.document())
        self.openFile('test.py')


    def newFile(self):
        self.editor.clear()


    def openFile(self, path=None):
        if not path:
            path = QtGui.QFileDialog.getOpenFileName(self, "Open File",
                    '', "PyMT Files (*.py *.xml)")

        if path:
            inFile = QtCore.QFile(path)
            if inFile.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
                text = inFile.readAll()
                text = str(text)
                self.editor.setPlainText(text)



    def run(self):
        pymt.stopTouchApp()
        buff1 = StringIO()
        buff2 = StringIO()
        stdout = sys.stdout
        stderr = sys.stderr
        sys.stdout = buff1
        sys.stderr = buff2
        self.execute_pymt_code()
        self.console.setPlainText(buff1.getvalue() + buff2.getvalue())
        sys.stdout = stdout
        sys.stderr = stderr



    def execute_pymt_code(self):
        oldRunApp = pymt.runTouchApp
        def designerRunTouchApp(w):
            oldRunApp(w, slave=True)
        pymt.runTouchApp = designerRunTouchApp

        try:
            self.glWidget.create_new_pymt_window()
            d = {}
            exec str(self.editor.toPlainText()) in d
            #pymt.stopTouchApp()
        except Exception as e:
            #pymt.pymt_logger.exception("Error Running PyMT Code:")
            traceback.print_exc()
        pymt.runTouchApp = oldRunApp





if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.resize(640, 512)
    window.show()
    sys.exit(app.exec_())

