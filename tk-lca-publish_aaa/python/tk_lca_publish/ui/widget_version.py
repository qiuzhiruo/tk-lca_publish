# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:/liulu/sgtk/tk-lca-publish/resources/widget_version.ui'
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
        self.tableWidget_old_versions = QtGui.QTableWidget(Form)
        self.tableWidget_old_versions.setGeometry(QtCore.QRect(10, 80, 680, 410))
        self.tableWidget_old_versions.setObjectName(_fromUtf8("tableWidget_old_versions"))
        self.tableWidget_old_versions.setColumnCount(4)
        self.tableWidget_old_versions.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.tableWidget_old_versions.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget_old_versions.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget_old_versions.setHorizontalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget_old_versions.setHorizontalHeaderItem(3, item)
        self.label_version_name_a = QtGui.QLabel(Form)
        self.label_version_name_a.setGeometry(QtCore.QRect(10, 50, 90, 20))
        self.label_version_name_a.setObjectName(_fromUtf8("label_version_name_a"))
        self.lineEdit_version_name = QtGui.QLineEdit(Form)
        self.lineEdit_version_name.setGeometry(QtCore.QRect(580, 45, 110, 25))
        self.lineEdit_version_name.setObjectName(_fromUtf8("lineEdit_version_name"))
        self.label_version_name_b = QtGui.QLabel(Form)
        self.label_version_name_b.setGeometry(QtCore.QRect(100, 50, 478, 20))
        self.label_version_name_b.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_version_name_b.setObjectName(_fromUtf8("label_version_name_b"))
        self.label_description = QtGui.QLabel(Form)
        self.label_description.setGeometry(QtCore.QRect(80, 0, 610, 30))
        self.label_description.setObjectName(_fromUtf8("label_description"))

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.label_title.setText(_translate("Form", "版本信息:", None))
        item = self.tableWidget_old_versions.horizontalHeaderItem(0)
        item.setText(_translate("Form", "版本", None))
        item = self.tableWidget_old_versions.horizontalHeaderItem(1)
        item.setText(_translate("Form", "提交人", None))
        item = self.tableWidget_old_versions.horizontalHeaderItem(2)
        item.setText(_translate("Form", "时间", None))
        item = self.tableWidget_old_versions.horizontalHeaderItem(3)
        item.setText(_translate("Form", "描述", None))
        self.label_version_name_a.setText(_translate("Form", "版本名:", None))
        self.lineEdit_version_name.setText(_translate("Form", ".v", None))
        self.label_description.setText(_translate("Form", "<html><head/><body><p>列出shotgun该任务已经publish的版本。请将版本号补充完整。</p></body></html>", None))

