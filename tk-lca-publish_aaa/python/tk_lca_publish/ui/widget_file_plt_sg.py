# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/mnt/work/home/yingjie/git_repo/tk-lca-publish/resources/widget_file_plt_sg.ui'
#
# Created: Wed Aug 16 10:31:14 2017
#      by: PyQt4 UI code generator 4.6.2
#
# WARNING! All changes made in this file will be lost!

from sgtk.platform.qt import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(680, 320)
        self.pushButton_pick_cache = QtGui.QPushButton(Form)
        self.pushButton_pick_cache.setGeometry(QtCore.QRect(10, 20, 90, 25))
        self.pushButton_pick_cache.setObjectName("pushButton_pick_cache")
        self.lineEdit_cache = QtGui.QLineEdit(Form)
        self.lineEdit_cache.setGeometry(QtCore.QRect(110, 20, 561, 25))
        self.lineEdit_cache.setObjectName("lineEdit_cache")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_pick_cache.setText(QtGui.QApplication.translate("Form", "Cache 文件夹", None, QtGui.QApplication.UnicodeUTF8))

