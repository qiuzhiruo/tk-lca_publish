# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:/liulu/sgtk/tk-lca-publish/resources/widget_check.ui'
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
        Form.resize(700, 500)
        self.label_title = QtGui.QLabel(Form)
        self.label_title.setGeometry(QtCore.QRect(10, 0, 70, 30))
        self.label_title.setObjectName(_fromUtf8("label_title"))
        self.label_description = QtGui.QLabel(Form)
        self.label_description.setGeometry(QtCore.QRect(80, 0, 610, 30))
        self.label_description.setObjectName(_fromUtf8("label_description"))
        self.pushButton_check = QtGui.QPushButton(Form)
        self.pushButton_check.setGeometry(QtCore.QRect(570, 460, 120, 30))
        self.pushButton_check.setObjectName(_fromUtf8("pushButton_check"))
        self.cancle_check = QtGui.QPushButton(Form)
        self.cancle_check.setGeometry(QtCore.QRect(440, 460, 120, 30))
        self.cancle_check.setObjectName(_fromUtf8("cancle_check"))

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.label_title.setText(_translate("Form", "提交检查:", None))
        self.label_description.setText(_translate("Form", "<html><head/><body><p>提交版本之前做的检查，如果不能全部通过则无法进入下一页。请点击右下角的 全部检查 按钮。</p></body></html>", None))
        self.pushButton_check.setText(_translate("Form", "全部检查", None))
        self.cancle_check.setText(_translate("Form", "取消勾选", None))

