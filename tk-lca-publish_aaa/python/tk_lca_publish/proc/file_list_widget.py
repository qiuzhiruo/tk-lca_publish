import sgtk
from sgtk.platform.qt import QtCore, QtGui

class FileListWidget(QtGui.QListWidget):
    def __init__(self, parent=None):
        super(FileListWidget, self).__init__(parent)
        self.itemPressed.connect(self.on_item_clicked)

    def mousePressEvent(self, event):
        self._mouse_button = event.button()
        super(FileListWidget, self).mousePressEvent(event)

    def on_item_clicked(self, item):
        print item.text(), self._mouse_button.name


