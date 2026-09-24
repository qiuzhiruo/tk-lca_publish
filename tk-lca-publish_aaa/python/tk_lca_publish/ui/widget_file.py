# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:/liulu/sgtk/tk-lca-publish/resources/widget_file.ui'
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
        self.label_description = QtGui.QLabel(Form)
        self.label_description.setGeometry(QtCore.QRect(80, 0, 610, 30))
        self.label_description.setObjectName(_fromUtf8("label_description"))
        self.label_title = QtGui.QLabel(Form)
        self.label_title.setGeometry(QtCore.QRect(10, 0, 70, 30))
        self.label_title.setObjectName(_fromUtf8("label_title"))
        self.groupBox_preview_files = QtGui.QGroupBox(Form)
        self.groupBox_preview_files.setGeometry(QtCore.QRect(10, 370, 680, 120))
        self.groupBox_preview_files.setObjectName(_fromUtf8("groupBox_preview_files"))
        self.thumbnail_widget = ThumbnailWidget(self.groupBox_preview_files)
        self.thumbnail_widget.setGeometry(QtCore.QRect(10, 20, 90, 60))
        self.thumbnail_widget.setMinimumSize(QtCore.QSize(0, 0))
        self.thumbnail_widget.setMaximumSize(QtCore.QSize(16777215, 16777215))
        # self.thumbnail_widget.setFocusPolicy(QtCore.Qt.NoFocus)
        self.thumbnail_widget.setStyleSheet(_fromUtf8(""))
        self.thumbnail_widget.setObjectName(_fromUtf8("thumbnail_widget"))
        self.pushButton_pick_preview = QtGui.QPushButton(self.groupBox_preview_files)
        self.pushButton_pick_preview.setGeometry(QtCore.QRect(10, 85, 90, 25))
        self.pushButton_pick_preview.setObjectName(_fromUtf8("pushButton_pick_preview"))
        self.listWidget_preview = FileListWidget(self.groupBox_preview_files)
        self.listWidget_preview.setGeometry(QtCore.QRect(110, 20, 560, 90))
        self.listWidget_preview.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.listWidget_preview.setObjectName(_fromUtf8("listWidget_preview"))
        self.groupBox_publish_files = QtGui.QGroupBox(Form)
        self.groupBox_publish_files.setGeometry(QtCore.QRect(10, 40, 680, 320))
        self.groupBox_publish_files.setObjectName(_fromUtf8("groupBox_publish_files"))

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.label_description.setText(_translate("Form", "<html><head/><body><p>选择要提交的文件和预览用的文件。请点击左侧的 选取文件 按钮。如果选错，右击可以清空</p></body></html>", None))
        self.label_title.setText(_translate("Form", "提交文件:", None))
        self.groupBox_preview_files.setTitle(_translate("Form", "版本预览", None))
        self.pushButton_pick_preview.setText(_translate("Form", "选取预览文件", None))
        self.groupBox_publish_files.setTitle(_translate("Form", "版本提交文件", None))

from ..proc.snapshot_form import ThumbnailWidget
from ..proc.file_list_widget import FileListWidget
