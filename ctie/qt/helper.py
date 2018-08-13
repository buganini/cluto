from PyQt5 import QtCore
from functools import partial

class UI(QtCore.QObject):
    signal = QtCore.pyqtSignal()
    def __init__(self, func):
        QtCore.QObject.__init__(self)
        self.func = func
        self.signal.connect(self.run)
    def run(self):
        self.func(*self.args, **self.kwargs)
    def __call__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.signal.emit()
    def __get__(self, instance, owner):
        return partial(self.__call__, instance)