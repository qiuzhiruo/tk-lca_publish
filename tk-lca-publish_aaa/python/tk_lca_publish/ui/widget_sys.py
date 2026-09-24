# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:/liulu/sgtk/tk-lca-publish/resources/widget_sys.ui'
#
# Created: Fri Apr 11 10:51:14 2014
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
        self.pushButton_check = QtGui.QPushButton(Form)
        self.pushButton_check.setGeometry(QtCore.QRect(570, 460, 120, 30))
        self.pushButton_check.setObjectName(_fromUtf8("pushButton_check"))
        self.label_description = QtGui.QLabel(Form)
        self.label_description.setGeometry(QtCore.QRect(80, 0, 610, 30))
        self.label_description.setObjectName(_fromUtf8("label_description"))
        self.comboBox_tag = QtGui.QComboBox(Form)
        self.comboBox_tag.setGeometry(QtCore.QRect(10, 460, 150, 30))
        self.comboBox_tag.setObjectName(_fromUtf8("comboBox_tag"))

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.label_title.setText(_translate("Form", "<html><head/><body><p>系统需求:</p></body></html>", None))
        self.pushButton_check.setText(_translate("Form", "全部检查", None))
        self.label_description.setText(_translate("Form", "<html><head/><body><p>检查Shotgun信息是否准确;服务器文件目标路径是否存在;必须的软件是否安装，等等。请点击右下角的 全部检查 。</p></body></html>", None))

