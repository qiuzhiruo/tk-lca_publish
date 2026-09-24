# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:/liulu/sgtk/tk-lca-publish/resources/widget_file_doc.ui'
#
# Created: Fri Apr 11 10:51:13 2014
#      by: PyQt4 UI code generator 4.10.2
#
# WARNING! All changes made in this file will be lost!

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

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(680, 320)
        self.pushButton_pick_document = QtGui.QPushButton(Form)
        self.pushButton_pick_document.setGeometry(QtCore.QRect(10, 20, 90, 25))
        self.pushButton_pick_document.setObjectName(_fromUtf8("pushButton_pick_document"))
        self.listWidget_document = FileListWidget(Form)
        self.listWidget_document.setGeometry(QtCore.QRect(110, 20, 561, 281))
        self.listWidget_document.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.listWidget_document.setObjectName(_fromUtf8("listWidget_document"))

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.pushButton_pick_document.setText(_translate("Form", "选取文档", None))

from ..proc.file_list_widget import FileListWidget
