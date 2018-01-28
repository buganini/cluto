import os
from PySide import QtGui

class QChrootFileDirDialog(QtGui.QFileDialog):
    def __init__(self, root, filesMode=True, *args, **kwargs):
        QtGui.QFileDialog.__init__(self, *args, **kwargs)
        self.root = root
        self.directoryEntered.connect(self.onDirectoryEntered)
        self.setOption(QtGui.QFileDialog.DontUseNativeDialog)
        if filesMode:
            self.setFileMode(QtGui.QFileDialog.ExistingFiles)
        else:
            self.setFileMode(QtGui.QFileDialog.Directory)
        self.setDirectory(root)

    def accept(self):
        super(QChrootFileDirDialog, self).accept()

    def onDirectoryEntered(self, path):
        root = os.path.abspath(self.root)+"/"
        here = os.path.abspath(path)
        if not here.startswith(root):
            self.setDirectory(self.root)
