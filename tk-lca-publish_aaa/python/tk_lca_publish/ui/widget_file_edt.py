# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'P:\home\liulu\td_dev_zone\sgtk\tk-lca-publish\resources\widget_file_edt.ui'
#
# Created: Thu Aug 21 16:39:07 2014
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
        self.lineEdit_edl = QtGui.QLineEdit(Form)
        self.lineEdit_edl.setGeometry(QtCore.QRect(110, 20, 480, 25))
        self.lineEdit_edl.setObjectName(_fromUtf8("lineEdit_edl"))
        self.pushButton_pick_edl = QtGui.QPushButton(Form)
        self.pushButton_pick_edl.setGeometry(QtCore.QRect(10, 20, 90, 25))
        self.pushButton_pick_edl.setObjectName(_fromUtf8("pushButton_pick_edl"))
        self.tableWidget_shots = QtGui.QTableWidget(Form)
        self.tableWidget_shots.setGeometry(QtCore.QRect(10, 50, 660, 260))
        self.tableWidget_shots.setObjectName(_fromUtf8("tableWidget_shots"))
        self.tableWidget_shots.setColumnCount(6)
        self.tableWidget_shots.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.tableWidget_shots.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget_shots.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget_shots.setHorizontalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget_shots.setHorizontalHeaderItem(3, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget_shots.setHorizontalHeaderItem(4, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget_shots.setHorizontalHeaderItem(5, item)
        self.pushButton_reload = QtGui.QPushButton(Form)
        self.pushButton_reload.setGeometry(QtCore.QRect(600, 20, 70, 25))
        self.pushButton_reload.setObjectName(_fromUtf8("pushButton_reload"))

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.pushButton_pick_edl.setText(_translate("Form", "选取edl文件", None))
        item = self.tableWidget_shots.horizontalHeaderItem(0)
        item.setText(_translate("Form", "shot", None))
        item = self.tableWidget_shots.horizontalHeaderItem(1)
        item.setText(_translate("Form", "SG cut in", None))
        item = self.tableWidget_shots.horizontalHeaderItem(2)
        item.setText(_translate("Form", "SG cut out", None))
        item = self.tableWidget_shots.horizontalHeaderItem(3)
        item.setText(_translate("Form", "SG duration", None))
        item = self.tableWidget_shots.horizontalHeaderItem(4)
        item.setText(_translate("Form", "edl cut duration", None))
        item = self.tableWidget_shots.horizontalHeaderItem(5)
        item.setText(_translate("Form", "mov file", None))
        self.pushButton_reload.setText(_translate("Form", "Reload", None))

