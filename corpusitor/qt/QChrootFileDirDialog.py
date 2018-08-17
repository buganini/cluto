import os
from PyQt5.QtWidgets import QFileDialog

class QChrootFileDirDialog(QFileDialog):
    def __init__(self, root, filesMode=True, *args, **kwargs):
        QFileDialog.__init__(self, *args, **kwargs)
        self.root = root
        self.directoryEntered.connect(self.onDirectoryEntered)
        self.setOption(QFileDialog.DontUseNativeDialog)
        if filesMode:
            self.setFileMode(QFileDialog.ExistingFiles)
        else:
            self.setFileMode(QFileDialog.Directory)
        self.setDirectory(root)

    def accept(self):
        super(QChrootFileDirDialog, self).accept()

    def onDirectoryEntered(self, path):
        root = os.path.abspath(self.root)+"/"
        here = os.path.abspath(path)
        if not here.startswith(root):
            self.setDirectory(self.root)
