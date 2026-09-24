# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/mnt/work/home/yingjie/git_repo/tk-lca-publish/resources/widget_file_srf_sg.ui'
#
# Created: Wed May 25 15:05:57 2016
#      by: PyQt4 UI code generator 4.6.2
#
# WARNING! All changes made in this file will be lost!

from sgtk.platform.qt import QtCore, QtGui
from ..proc.file_list_widget import FileListWidget

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
        self.pushButton_pick_katana = QtGui.QPushButton(Form)
        self.pushButton_pick_katana.setGeometry(QtCore.QRect(10, 20, 90, 25))
        self.pushButton_pick_katana.setObjectName("pushButton_pick_katana")
        self.lineEdit_katana = QtGui.QLineEdit(Form)
        self.lineEdit_katana.setGeometry(QtCore.QRect(110, 20, 561, 25))
        self.lineEdit_katana.setObjectName("lineEdit_katana")
        self.checkBox = QtGui.QCheckBox(Form)
        self.checkBox.setGeometry(QtCore.QRect(110, 60, 121, 20))
        self.checkBox.setObjectName("checkBox")
        self.checkBox_xgenarc = QtGui.QCheckBox(Form)
        self.checkBox_xgenarc.setGeometry(QtCore.QRect(110, 90, 111, 20))
        self.checkBox_xgenarc.setObjectName("checkBox_xgenarc")

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
        self.pushButton_pick_katana.setText(QtGui.QApplication.translate("Form", "Katana 文件", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox.setText(QtGui.QApplication.translate("Form", "只publish xml", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_xgenarc.setText(QtGui.QApplication.translate("Form", "Xgen Archive", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_upload_img.setText(QtGui.QApplication.translate("Form", "client\nimage", None, QtGui.QApplication.UnicodeUTF8))
