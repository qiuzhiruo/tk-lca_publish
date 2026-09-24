# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:/liulu/sgtk/tk-lca-publish/resources/widget_file_no_file.ui'
#
# Created: Fri Apr 11 10:51:14 2014
#      by: PyQt4 UI code generator 4.10.2
#
# WARNING! All changes made in this file will be lost!

from sgtk.platform.qt import QtCore, QtGui
from ....proc.file_list_widget import FileListWidget

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
        self.label = QtGui.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(30, 30, 621, 71))
        self.label.setObjectName(_fromUtf8("label"))

        self.pushButton_upload_img = QtGui.QPushButton(Form)
        self.pushButton_upload_img.setGeometry(QtCore.QRect(10, 240, 85, 70))
        self.pushButton_upload_img.setObjectName("pushButton_upload_img")
        self.listWidget_upload_img = FileListWidget(Form)
        self.listWidget_upload_img.setGeometry(QtCore.QRect(105, 240, 560, 70))
        self.listWidget_upload_img.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.listWidget_upload_img.setObjectName("listWidget_upload_img")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(_translate("Form", "Publish 的文件由当前场景输出，不用选取。", None))
        self.pushButton_upload_img.setText(QtGui.QApplication.translate("Form", "client\nimage", None, QtGui.QApplication.UnicodeUTF8))

