# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'P:\home\liulu\td_dev_zone\sgtk\tk-lca-publish\resources\widget_file_mod_dynamic.ui'
#
# Created: Fri Oct 09 17:47:01 2015
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
        self.pushButton_dynamic = QtGui.QPushButton(Form)
        self.pushButton_dynamic.setGeometry(QtCore.QRect(30, 70, 70, 70))
        self.pushButton_dynamic.setObjectName(_fromUtf8("pushButton_dynamic"))
        self.listWidget_dynamic = FileListWidget(Form)
        self.listWidget_dynamic.setGeometry(QtCore.QRect(110, 70, 560, 70))
        self.listWidget_dynamic.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.listWidget_dynamic.setObjectName(_fromUtf8("listWidget_dynamic"))
        self.listWidget_proxy = FileListWidget(Form)
        self.listWidget_proxy.setGeometry(QtCore.QRect(110, 150, 560, 70))
        self.listWidget_proxy.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.listWidget_proxy.setObjectName(_fromUtf8("listWidget_proxy"))
        self.pushButton_proxy = QtGui.QPushButton(Form)
        self.pushButton_proxy.setGeometry(QtCore.QRect(30, 150, 70, 70))
        self.pushButton_proxy.setObjectName(_fromUtf8("pushButton_proxy"))

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.pushButton_dynamic.setText(_translate("Form", "动态\n"
"(*.abc)", None))
        self.pushButton_proxy.setText(_translate("Form", "动态预览\n"
"(*.abc)", None))

from ..proc.file_list_widget import FileListWidget
