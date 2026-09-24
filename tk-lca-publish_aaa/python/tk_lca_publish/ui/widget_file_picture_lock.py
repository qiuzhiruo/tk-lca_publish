# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'P:\home\liulu\td_dev_zone\sgtk\tk-lca-publish\resources\widget_file_picture_lock.ui'
#
# Created: Mon Aug 22 15:31:07 2016
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
        self.pushButton_edt = QtGui.QPushButton(Form)
        self.pushButton_edt.setGeometry(QtCore.QRect(30, 70, 70, 25))
        self.pushButton_edt.setObjectName(_fromUtf8("pushButton_edt"))
        self.pushButton_audio = QtGui.QPushButton(Form)
        self.pushButton_audio.setGeometry(QtCore.QRect(30, 110, 70, 25))
        self.pushButton_audio.setObjectName(_fromUtf8("pushButton_audio"))
        self.lineEdit_edt = QtGui.QLineEdit(Form)
        self.lineEdit_edt.setGeometry(QtCore.QRect(110, 70, 560, 25))
        self.lineEdit_edt.setObjectName(_fromUtf8("lineEdit_edt"))
        self.lineEdit_audio = QtGui.QLineEdit(Form)
        self.lineEdit_audio.setGeometry(QtCore.QRect(110, 110, 560, 25))
        self.lineEdit_audio.setObjectName(_fromUtf8("lineEdit_audio"))
        
        self.stereo_checkBox = QtGui.QCheckBox('Stereo', Form)
        self.stereo_checkBox.setGeometry(QtCore.QRect(30, 150, 100, 25))
        self.stereo_checkBox.setCheckState(QtCore.Qt.Unchecked)
        self.lineEdit_audio.setObjectName(_fromUtf8("stereo_checkBox"))
        
        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.pushButton_edt.setText(_translate("Form", "Edt", None))
        self.pushButton_audio.setText(_translate("Form", "Audio", None))

