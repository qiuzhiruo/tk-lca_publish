# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\widget_rp_entity.ui'
#
# Created: Thu May 16 12:07:11 2019
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
        Form.resize(641, 43)
        Form.setMinimumSize(QtCore.QSize(0, 30))
        Form.setMaximumSize(QtCore.QSize(16777215, 43))
        self.horizontalLayout = QtGui.QHBoxLayout(Form)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label_rp_name = QtGui.QLabel(Form)
        self.label_rp_name.setMinimumSize(QtCore.QSize(300, 25))
        self.label_rp_name.setMaximumSize(QtCore.QSize(300, 25))
        self.label_rp_name.setText(_fromUtf8(""))
        self.label_rp_name.setObjectName(_fromUtf8("label_rp_name"))
        self.horizontalLayout.addWidget(self.label_rp_name)
        self.lineEdit_rp_attr = QtGui.QLineEdit(Form)
        self.lineEdit_rp_attr.setMinimumSize(QtCore.QSize(0, 25))
        self.lineEdit_rp_attr.setMaximumSize(QtCore.QSize(16777215, 25))
        self.lineEdit_rp_attr.setObjectName(_fromUtf8("lineEdit_rp_attr"))
        self.horizontalLayout.addWidget(self.lineEdit_rp_attr)
        self.lineEdit_rp_value = QtGui.QLineEdit(Form)
        self.lineEdit_rp_value.setMinimumSize(QtCore.QSize(50, 25))
        self.lineEdit_rp_value.setMaximumSize(QtCore.QSize(50, 25))
        self.lineEdit_rp_value.setObjectName(_fromUtf8("lineEdit_rp_value"))
        self.horizontalLayout.addWidget(self.lineEdit_rp_value)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))

