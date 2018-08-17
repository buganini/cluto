from PyQt5 import QtCore
from functools import partial

class UI(QtCore.QObject):
    signal = QtCore.pyqtSignal(int)
    def __init__(self, func):
        QtCore.QObject.__init__(self)
        self.serial = 0
        self.data = {}
        self.func = func
        self.signal.connect(self.run)
    def run(self, token):
        args, kwargs = self.data.pop(token)
        self.func(*args, **kwargs)
    def __call__(self, *args, **kwargs):
        token = self.serial
        self.serial = (self.serial + 1) % 65536
        payload = (args, kwargs)
        self.data[token] = payload
        self.signal.emit(token)
    def __get__(self, instance, owner):
        return partial(self.__call__, instance)