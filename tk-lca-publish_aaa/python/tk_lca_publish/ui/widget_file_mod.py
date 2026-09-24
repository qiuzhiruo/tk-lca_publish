# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/huazhuo/tk-lca-publish/resources/widget_file_mod.ui'
#
# Created: Wed Nov 23 19:23:19 2016
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
        self.comboBox_publish_mode = QtGui.QComboBox(Form)
        self.comboBox_publish_mode.setGeometry(QtCore.QRect(30, 40, 70, 25))
        self.comboBox_publish_mode.setObjectName("comboBox_publish_mode")
        self.comboBox_publish_mode.addItem("")
        self.comboBox_publish_mode.addItem("")

        self.comboBox_copyuv_mode = QtGui.QComboBox(Form)
        self.comboBox_copyuv_mode.setGeometry(QtCore.QRect(100, 40, 150, 25))
        self.comboBox_copyuv_mode.setObjectName("comboBox_copyuv_mode")
        self.comboBox_copyuv_mode.addItem("")
        self.comboBox_copyuv_mode.addItem("")

        self.comboBox_make_low = QtGui.QComboBox(Form)
        self.comboBox_make_low.setGeometry(QtCore.QRect(250, 40, 110, 25))
        self.comboBox_make_low.setObjectName("make_low")
        self.comboBox_make_low.addItem("")
        self.comboBox_make_low.addItem("")

        self.pushButton_speed_tree = QtGui.QPushButton(Form)
        self.pushButton_speed_tree.setGeometry(QtCore.QRect(30, 190, 71, 51))
        self.pushButton_speed_tree.setObjectName("pushButton_speed_tree")
        self.listWidget_speed_tree = FileListWidget(Form)
        self.listWidget_speed_tree.setGeometry(QtCore.QRect(110, 190, 561, 51))
        self.listWidget_speed_tree.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.listWidget_speed_tree.setObjectName("listWidget_speed_tree")
        self.pushButton_zb = QtGui.QPushButton(Form)
        self.pushButton_zb.setGeometry(QtCore.QRect(30, 130, 70, 51))
        self.pushButton_zb.setObjectName("pushButton_zb")
        self.listWidget_zb = FileListWidget(Form)
        self.listWidget_zb.setGeometry(QtCore.QRect(110, 130, 560, 51))
        self.listWidget_zb.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.listWidget_zb.setObjectName("listWidget_zb")
        self.pushButton_dy = QtGui.QPushButton(Form)
        self.pushButton_dy.setEnabled(False)
        self.pushButton_dy.setGeometry(QtCore.QRect(30, 250, 70, 31))
        self.pushButton_dy.setObjectName("pushButton_dy")
        self.listWidget_dy = FileListWidget(Form)
        self.listWidget_dy.setGeometry(QtCore.QRect(210, 249, 461, 61))
        self.listWidget_dy.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.listWidget_dy.setObjectName("listWidget_dy")
        self.end_f = QtGui.QLineEdit(Form)
        self.end_f.setEnabled(False)
        self.end_f.setGeometry(QtCore.QRect(150, 280, 41, 27))
        self.end_f.setMinimumSize(QtCore.QSize(0, 0))
        self.end_f.setMaximumSize(QtCore.QSize(80, 16777215))
        self.end_f.setObjectName("end_f")
        self.start_f = QtGui.QLineEdit(Form)
        self.start_f.setEnabled(False)
        self.start_f.setGeometry(QtCore.QRect(150, 253, 41, 28))
        self.start_f.setMinimumSize(QtCore.QSize(0, 20))
        self.start_f.setMaximumSize(QtCore.QSize(500, 16777215))
        self.start_f.setObjectName("start_f")
        self.label_s = QtGui.QLabel(Form)
        self.label_s.setEnabled(False)
        self.label_s.setGeometry(QtCore.QRect(70, 260, 73, 16))
        self.label_s.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_s.setObjectName("label_s")
        self.label_e = QtGui.QLabel(Form)
        self.label_e.setEnabled(False)
        self.label_e.setGeometry(QtCore.QRect(60, 287, 81, 16))
        self.label_e.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_e.setObjectName("label_e")
        self.pushButton_dy_export = QtGui.QPushButton(Form)
        self.pushButton_dy_export.setEnabled(False)
        self.pushButton_dy_export.setGeometry(QtCore.QRect(30, 280, 70, 31))
        self.pushButton_dy_export.setObjectName("pushButton_dy_export")
        self.pushButton_zb_view = QtGui.QPushButton(Form)
        self.pushButton_zb_view.setGeometry(QtCore.QRect(30, 70, 70, 51))
        self.pushButton_zb_view.setObjectName("pushButton_zb_2")
        self.listWidget_zb_view = FileListWidget(Form)
        self.listWidget_zb_view.setGeometry(QtCore.QRect(110, 70, 560, 51))
        self.listWidget_zb_view.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.listWidget_zb_view.setObjectName("listWidget_zb_view")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_publish_mode.setItemText(0, QtGui.QApplication.translate("Form", "poly", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_publish_mode.setItemText(1, QtGui.QApplication.translate("Form", "shape", None, QtGui.QApplication.UnicodeUTF8))

        self.comboBox_copyuv_mode.setItemText(0, QtGui.QApplication.translate("Form", "Copy UV  (Yes)", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_copyuv_mode.setItemText(1, QtGui.QApplication.translate("Form", "Copy UV  (No)", None, QtGui.QApplication.UnicodeUTF8))

        self.comboBox_make_low.setItemText(0, QtGui.QApplication.translate("Form", "Make Low(No)", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_make_low.setItemText(1, QtGui.QApplication.translate("Form", "Make Low(Yes)", None,QtGui.QApplication.UnicodeUTF8))

        self.pushButton_speed_tree.setText(QtGui.QApplication.translate("Form", "Speed\n"
"Tree", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_zb.setText(QtGui.QApplication.translate("Form", "ZBrush", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_dy.setText(QtGui.QApplication.translate("Form", "Dynamic\n"
"(*.abc)", None, QtGui.QApplication.UnicodeUTF8))
        self.end_f.setText(QtGui.QApplication.translate("Form", "200", None, QtGui.QApplication.UnicodeUTF8))
        self.start_f.setText(QtGui.QApplication.translate("Form", "1", None, QtGui.QApplication.UnicodeUTF8))
        self.label_s.setText(QtGui.QApplication.translate("Form", "start", None, QtGui.QApplication.UnicodeUTF8))
        self.label_e.setText(QtGui.QApplication.translate("Form", "end", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_dy_export.setText(QtGui.QApplication.translate("Form", "export", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_zb_view.setText(QtGui.QApplication.translate("Form", "ZB 预览", None, QtGui.QApplication.UnicodeUTF8))


from ..proc.file_list_widget import FileListWidget
