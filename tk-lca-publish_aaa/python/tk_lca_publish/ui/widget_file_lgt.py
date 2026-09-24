# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/yingjie/git_repo/tk-lca-publish/resources/widget_file_lgt.ui'
#
# Created: Mon Aug 11 19:54:03 2014
#      by: PyQt4 UI code generator 4.6.2
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
        Form.setObjectName("Form")
        Form.resize(699, 140)
        self.pushButton_lseq = QtGui.QPushButton(Form)
        self.pushButton_lseq.setGeometry(QtCore.QRect(20, 20, 85, 27))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_lseq.sizePolicy().hasHeightForWidth())
        self.pushButton_lseq.setSizePolicy(sizePolicy)
        self.pushButton_lseq.setObjectName("pushButton_lseq")
        self.lineEdit_lseq = QtGui.QLineEdit(Form)
        self.lineEdit_lseq.setGeometry(QtCore.QRect(111, 21, 561, 25))
        self.lineEdit_lseq.setObjectName("lineEdit_lseq")
        self.lineEdit_rseq = QtGui.QLineEdit(Form)
        self.lineEdit_rseq.setEnabled(False)
        self.lineEdit_rseq.setGeometry(QtCore.QRect(111, 56, 561, 25))
        self.lineEdit_rseq.setObjectName("lineEdit_rseq")
        self.pushButton_rseq = QtGui.QPushButton(Form)
        self.pushButton_rseq.setEnabled(False)
        self.pushButton_rseq.setGeometry(QtCore.QRect(20, 55, 85, 27))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_rseq.sizePolicy().hasHeightForWidth())
        self.pushButton_rseq.setSizePolicy(sizePolicy)
        self.pushButton_rseq.setObjectName("pushButton_rseq")
        self.pushButton_nk = QtGui.QPushButton(Form)
        self.pushButton_nk.setGeometry(QtCore.QRect(20, 90, 85, 27))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_nk.sizePolicy().hasHeightForWidth())
        self.pushButton_nk.setSizePolicy(sizePolicy)
        self.pushButton_nk.setObjectName("pushButton_nk")
        self.lineEdit_nk = QtGui.QLineEdit(Form)
        self.lineEdit_nk.setGeometry(QtCore.QRect(111, 91, 561, 25))
        self.lineEdit_nk.setObjectName("lineEdit_nk")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_lseq.setText(QtGui.QApplication.translate("Form", "L", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_rseq.setText(QtGui.QApplication.translate("Form", "R", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_nk.setText(QtGui.QApplication.translate("Form", "Nuke", None, QtGui.QApplication.UnicodeUTF8))

from ..proc.file_list_widget import FileListWidget
