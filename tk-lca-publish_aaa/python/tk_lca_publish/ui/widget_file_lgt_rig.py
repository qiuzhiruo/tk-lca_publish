# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'P:\home\liulu\td_dev_zone\sgtk\tk-lca-publish\resources\widget_file_lgt_rig.ui'
#
# Created: Wed Jul 09 10:43:03 2014
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
        self.pushButton_pick_lgt_rig = QtGui.QPushButton(Form)
        self.pushButton_pick_lgt_rig.setGeometry(QtCore.QRect(10, 20, 150, 25))
        self.pushButton_pick_lgt_rig.setObjectName(_fromUtf8("pushButton_pick_lgt_rig"))
        self.listWidget_lgt_rig = QtGui.QListWidget(Form)
        self.listWidget_lgt_rig.setGeometry(QtCore.QRect(10, 60, 650, 240))
        self.listWidget_lgt_rig.setAlternatingRowColors(True)
        self.listWidget_lgt_rig.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.listWidget_lgt_rig.setObjectName(_fromUtf8("listWidget_lgt_rig"))

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.pushButton_pick_lgt_rig.setText(_translate("Form", "添加 light rig 文件", None))

