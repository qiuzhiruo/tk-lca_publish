# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/yingjie/git_repo/tk-lca-publish/resources/widget_file_efx.ui'
#
# Created: Wed Jan  7 10:19:14 2015
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
        Form.resize(680, 320)
        self.pushButton_pick_cache = QtGui.QPushButton(Form)
        self.pushButton_pick_cache.setGeometry(QtCore.QRect(10, 20, 90, 25))
        self.pushButton_pick_cache.setObjectName("pushButton_pick_cache")
        self.listWidget_cache = FileListWidget(Form)
        self.listWidget_cache.setGeometry(QtCore.QRect(110, 20, 561, 281))
        self.listWidget_cache.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.listWidget_cache.setObjectName("listWidget_cache")
        self.pushButton_clear_cache = QtGui.QPushButton(Form)
        self.pushButton_clear_cache.setGeometry(QtCore.QRect(10, 60, 91, 27))
        self.pushButton_clear_cache.setObjectName("pushButton_clear_cache")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_pick_cache.setText(QtGui.QApplication.translate("Form", "选取顶层文件夹", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_clear_cache.setText(QtGui.QApplication.translate("Form", "清空列表", None, QtGui.QApplication.UnicodeUTF8))

from ..proc.file_list_widget import FileListWidget
