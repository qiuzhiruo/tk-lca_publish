# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/yingjie/git_repo/tk-lca-publish/resources/widget_file_audio.ui'
#
# Created: Wed Jul  2 11:16:31 2014
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
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(680, 420)
        self.pushButton_pick_wav = QtGui.QPushButton(Form)
        self.pushButton_pick_wav.setGeometry(QtCore.QRect(10, 20, 101, 25))
        self.pushButton_pick_wav.setObjectName("pushButton_pick_wav")

        self.pushButton_clear_wav = QtGui.QPushButton(Form)
        self.pushButton_clear_wav.setGeometry(QtCore.QRect(140, 20, 111, 25))
        self.pushButton_clear_wav.setObjectName("pushButton_clear_wav")

        self.seq_checkbox = QtGui.QCheckBox('Sequence wav', Form)
        self.seq_checkbox.setGeometry(QtCore.QRect(280, 20, 111, 25))
        self.seq_checkbox.setObjectName('seq_checkbox')

        self.stb_checkbox = QtGui.QCheckBox('From Storyboard', Form)
        self.stb_checkbox.setGeometry(QtCore.QRect(400, 20, 130, 25))
        self.stb_checkbox.setObjectName('seq_checkbox')

        self.add_wave_length_checkbox = QtGui.QCheckBox('Add Wave Length', Form)
        self.add_wave_length_checkbox.setGeometry(QtCore.QRect(540, 20, 130, 25))
        self.add_wave_length_checkbox.setObjectName('add_wave_length_checkbox')

        self.listWidget_wavfiles = QtGui.QListWidget(Form)
        self.listWidget_wavfiles.setGeometry(QtCore.QRect(10, 50, 651, 180))
        self.listWidget_wavfiles.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.listWidget_wavfiles.setObjectName("listWidget_wavfiles")

        self.exclusive_label = QtGui.QLabel(Form)
        self.exclusive_label.setGeometry(QtCore.QRect(10, 240, 100, 25))
        self.exclusive_label.setObjectName('exclusive_label')
        self.exclusive_label.setEnabled(False)

        # use space to split shots
        self.exclusive_lineEdit = QtGui.QLineEdit(Form)
        self.exclusive_lineEdit.setGeometry(QtCore.QRect(113, 240, 550, 25))
        self.exclusive_lineEdit.setObjectName('exclusive_lineEdit')
        self.exclusive_lineEdit.setEnabled(False)

        # 新增：只更新的镜头号
        self.inclusive_label = QtGui.QLabel(Form)
        self.inclusive_label.setGeometry(QtCore.QRect(10, 275, 100, 25))
        self.inclusive_label.setObjectName('inclusive_label')
        self.inclusive_label.setEnabled(False)

        # use space to split shots
        self.inclusive_lineEdit = QtGui.QLineEdit(Form)
        self.inclusive_lineEdit.setGeometry(QtCore.QRect(113, 275, 550, 25))
        self.inclusive_lineEdit.setObjectName('inclusive_lineEdit')
        self.inclusive_lineEdit.setEnabled(False)

        self.xml_label = QtGui.QLabel(Form)
        self.xml_label.setGeometry(QtCore.QRect(10, 310, 50, 25))
        self.xml_label.setObjectName('xml_label')

        self.xml_lineEdit = QtGui.QLineEdit(Form)
        self.xml_lineEdit.setGeometry(QtCore.QRect(70, 310, 550, 25))
        self.xml_lineEdit.setObjectName('xml_lineEdit')

        self.xml_file_btn = QtGui.QPushButton(Form)
        self.xml_file_btn.setGeometry(QtCore.QRect(628, 310, 35, 25))
        self.xml_file_btn.setObjectName("xml_file_btn")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_pick_wav.setText(QtGui.QApplication.translate("Form", "添加声音wav", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_clear_wav.setText(QtGui.QApplication.translate("Form", "清除选择的wav", None, QtGui.QApplication.UnicodeUTF8))
        self.add_wave_length_checkbox.setText(QtGui.QApplication.translate("Form", "加一个静音采样点", None, QtGui.QApplication.UnicodeUTF8))
        self.xml_label.setText(QtGui.QApplication.translate("Form", "xml / aaf", None, QtGui.QApplication.UnicodeUTF8))
        self.xml_file_btn.setText(QtGui.QApplication.translate("Form", "Dir ", None, QtGui.QApplication.UnicodeUTF8))
        self.exclusive_label.setText(QtGui.QApplication.translate("Form", "不需更新的镜头号", None, QtGui.QApplication.UnicodeUTF8))
        self.inclusive_label.setText(QtGui.QApplication.translate("Form", "只更新的镜头号", None, QtGui.QApplication.UnicodeUTF8))