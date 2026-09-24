# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'P:/home/liulu/td_dev_zone/sgtk/tk-lca-publish/resources/widget_file_hyperloop.ui'
#
# Created: Fri Jun 28 15:13:27 2019
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
        self.pushButton_xml = QtGui.QPushButton(Form)
        self.pushButton_xml.setGeometry(QtCore.QRect(5, 150, 75, 25))
        self.pushButton_xml.setMinimumSize(QtCore.QSize(0, 25))
        self.pushButton_xml.setObjectName(_fromUtf8("pushButton_xml"))
        self.lineEdit_xml = QtGui.QLineEdit(Form)
        self.lineEdit_xml.setGeometry(QtCore.QRect(90, 150, 581, 25))
        self.lineEdit_xml.setMinimumSize(QtCore.QSize(0, 25))
        self.lineEdit_xml.setObjectName(_fromUtf8("lineEdit_xml"))

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.pushButton_xml.setText(_translate("Form", "XML", None))

