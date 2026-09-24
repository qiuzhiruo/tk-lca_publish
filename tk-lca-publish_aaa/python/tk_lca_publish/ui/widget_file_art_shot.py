# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:/liulu/sgtk/tk-lca-publish/resources/widget_file_art.ui'
#
# Created: Fri Apr 11 10:51:13 2014
#      by: PyQt4 UI code generator 4.10.2
#
# WARNING! All changes made in this file will be lost!
import os
from sgtk.platform.qt import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class FlowLayout(QtGui.QLayout):
    def __init__(self, parent=None, margin=0, spacing=-1):
        super(FlowLayout, self).__init__(parent)

        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)

        self.setSpacing(spacing)
        self.margin = margin

        # spaces between each item
        self.spaceX = 5
        self.spaceY = 5

        self.itemList = []

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self.itemList.append(item)

    def count(self):
        return len(self.itemList)

    def itemAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList[index]

        return None

    def takeAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList.pop(index)

        return None

    def expandingDirections(self):
        return QtCore.Qt.Orientations(QtCore.Qt.Orientation(0))

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self.doLayout(QtCore.QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QtCore.QSize()

        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())

        size += QtCore.QSize(2 * self.margin, 2 * self.margin)
        return size

    def doLayout(self, rect, testOnly):
        x = rect.x()
        y = rect.y()
        lineHeight = 0

        for item in self.itemList:
            nextX = x + item.sizeHint().width() + self.spaceX
            if nextX - self.spaceX > rect.right() and lineHeight > 0:
                x = rect.x()
                y = y + lineHeight + self.spaceY
                nextX = x + item.sizeHint().width() + self.spaceX
                lineHeight = 0

            if not testOnly:
                item.setGeometry(QtCore.QRect(QtCore.QPoint(x, y), item.sizeHint()))

            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())

        return y + lineHeight - rect.y()




class ui_Lib(QtGui.QWidget):
    def __init__(self, parent=None):
        super(ui_Lib,self).__init__(parent)
        self.setupUi()
    def setupUi(self):
        self.mainHboxLayout=QtGui.QHBoxLayout(self)

        self.ThexShowImageWidget=QtGui.QWidget()

        self.ThexShowImageWidgetFlowLayout=FlowLayout(self.ThexShowImageWidget)
        self.ThexShowImageWidgetScrollArea=QtGui.QScrollArea()
        self.ThexShowImageWidgetScrollArea.setWidget(self.ThexShowImageWidget)
        self.ThexShowImageWidgetScrollArea.setWidgetResizable(True)

        self.Seq_TableWidget = QtGui.QTableWidget()
        self.Seq_TableWidget.setColumnCount(1)
        self.Seq_TableWidget.setRowCount(1)

        seq_item = QtGui.QTableWidgetItem('Seq')
        self.Seq_TableWidget.setHorizontalHeaderItem(0,seq_item)
        self.Seq_TableWidget.setMaximumSize(70, 500)
        self.Seq_TableWidget.setColumnWidth(0,70)
        self.Seq_TableWidget.verticalHeader().setVisible(False)
        self.mainHboxLayout.addWidget(self.ThexShowImageWidgetScrollArea)
        self.mainHboxLayout.addWidget(self.Seq_TableWidget)


class ui_ThxWidgetItem(QtGui.QWidget):
    def __init__(self, parent=None,image_path=None):
        super(ui_ThxWidgetItem,self).__init__(parent)
        self.image_path=image_path
        self.name=os.path.basename(image_path).rsplit('.',2)[0]
        self.isDel=False
        self.setupUi()

    def setupUi(self):
        self.mainVboxLayout=QtGui.QVBoxLayout(self)
        ######!!!!
        self.ImageWidgetItem=QtGui.QToolButton()
        self.pixmap=QtGui.QPixmap(self.image_path)
        self.ImageWidgetItem.setIcon(QtGui.QIcon(self.pixmap))
        self.ImageWidgetItem.setIconSize(QtCore.QSize(110,100))
        self.ImageWidgetItem.setAutoRaise(1)
        self.ImageWidgetItem.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.ImageWidgetItem.setText(self.name)
        self.ImageWidgetItem.setFixedSize(115,130)
        self.ImageWidgetItem.setCheckable(1)
        self.mainVboxLayout.addWidget(self.ImageWidgetItem)
        self.mainVboxLayout.setContentsMargins(0,0,0,0)
        self.ImageWidgetItem.clicked.connect(self.del_image)

    def del_image(self):
        if self.isDel:
            self.ImageWidgetItem.setIcon(QtGui.QIcon(self.pixmap))
            self.isDel=False
        else:
            temp = QtGui.QPixmap(self.pixmap)
            color = QtGui.QColor(255,0,0,255)

            painter = QtGui.QPainter(temp)
            painter.setCompositionMode(painter.CompositionMode_Overlay)
            painter.fillRect(temp.rect(), color)
            painter.end()

            self.ImageWidgetItem.setDown(1)
            self.ImageWidgetItem.setIcon(QtGui.QIcon(temp))
            self.isDel=True

class Ui_Form(object):

    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(680, 320)
        self.label = QtGui.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(10, 10, 621, 60))
        self.label.setObjectName(_fromUtf8("label"))
        self.layout_image = ui_Lib(Form)
        self.layout_image.setObjectName(_fromUtf8("old_image"))
        self.layout_image.setGeometry(QtCore.QRect(5, 70, 670, 230))
        self.delete_button = QtGui.QPushButton(u'DELETE',Form)
        # self.delete_button.clicked.connect(delete_image)
        self.delete_button.setGeometry(QtCore.QRect(10, 300, 60, 20))
        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.label.setText(
                _translate("Form",
                           "本Publish需要提交单张/多张图片或者图片序列，并删除老版本中不需要的。给下游一个完成的图片集\n上面点击选择上一版不需要的图，下面提交新增的图片。\n右边的Sequences勾选上对应的场次号，可以同时publish到场次的任务里面。",
                           None))
