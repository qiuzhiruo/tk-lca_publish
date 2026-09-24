# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'widget_file_ani_crowd.ui'
#
# Created: Thu Oct 29 13:43:36 2015
#      by: PyQt4 UI code generator 4.6.2
#
# WARNING! All changes made in this file will be lost!

from sgtk.platform.qt import QtCore, QtGui

if False:
    from PySide import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(680, 320)
        self.tableWidget_actions = QtGui.QTableWidget(Form)
        self.tableWidget_actions.setGeometry(QtCore.QRect(10, 19, 621, 291))
        self.tableWidget_actions.setObjectName("tableWidget_actions")
        self.tableWidget_actions.setColumnCount(5)
        self.tableWidget_actions.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.tableWidget_actions.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget_actions.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget_actions.setHorizontalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget_actions.setHorizontalHeaderItem(3, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget_actions.setHorizontalHeaderItem(4, item)
        self.tableWidget_actions.verticalHeader().setVisible(False)
        self.pushButton_add = QtGui.QPushButton(Form)
        self.pushButton_add.setGeometry(QtCore.QRect(640, 20, 31, 27))
        self.pushButton_add.setObjectName("pushButton_add")
        self.pushButton_remove = QtGui.QPushButton(Form)
        self.pushButton_remove.setGeometry(QtCore.QRect(640, 50, 31, 27))
        self.pushButton_remove.setObjectName("pushButton_remove")
        self.pushButton_default = QtGui.QPushButton(Form)
        self.pushButton_default.setGeometry(QtCore.QRect(640, 280, 31, 27))
        self.pushButton_default.setObjectName("pushButton_default")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget_actions.horizontalHeaderItem(0).setText(QtGui.QApplication.translate("Form", "名称", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget_actions.horizontalHeaderItem(1).setText(QtGui.QApplication.translate("Form", "起始帧", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget_actions.horizontalHeaderItem(2).setText(QtGui.QApplication.translate("Form", "结束帧", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget_actions.horizontalHeaderItem(3).setText(QtGui.QApplication.translate("Form", "运动类型", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget_actions.horizontalHeaderItem(4).setText(QtGui.QApplication.translate("Form", "循环", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_add.setText(QtGui.QApplication.translate("Form", "+", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_remove.setText(QtGui.QApplication.translate("Form", "-", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_default.setText(QtGui.QApplication.translate("Form", "D", None, QtGui.QApplication.UnicodeUTF8))

