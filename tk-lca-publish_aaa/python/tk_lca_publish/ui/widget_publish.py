# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'P:\home\liulu\td_dev_zone\sgtk\tk-lca-publish\resources\widget_publish.ui'
#
# Created: Fri Aug 12 12:35:47 2016
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
        self.label_description_2 = QtGui.QLabel(Form)
        self.label_description_2.setGeometry(QtCore.QRect(10, 420, 31, 25))
        self.label_description_2.setObjectName(_fromUtf8("label_description_2"))
        self.plainTextEdit_description = QtGui.QPlainTextEdit(Form)
        self.plainTextEdit_description.setGeometry(QtCore.QRect(50, 420, 320, 71))
        self.plainTextEdit_description.setObjectName(_fromUtf8("plainTextEdit_description"))
        self.label_description = QtGui.QLabel(Form)
        self.label_description.setGeometry(QtCore.QRect(80, 0, 610, 30))
        self.label_description.setObjectName(_fromUtf8("label_description"))
        self.label_title = QtGui.QLabel(Form)
        self.label_title.setGeometry(QtCore.QRect(10, 0, 70, 30))
        self.label_title.setObjectName(_fromUtf8("label_title"))
        self.label_email = QtGui.QLabel(Form)
        self.label_email.setGeometry(QtCore.QRect(10, 390, 30, 25))
        self.label_email.setObjectName(_fromUtf8("label_email"))
        self.lineEdit_email = QtGui.QLineEdit(Form)
        self.lineEdit_email.setGeometry(QtCore.QRect(50, 390, 640, 25))
        self.lineEdit_email.setObjectName(_fromUtf8("lineEdit_email"))
        self.verticalLayoutWidget = QtGui.QWidget(Form)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 30, 681, 351))
        self.verticalLayoutWidget.setObjectName(_fromUtf8("verticalLayoutWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        #self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.scrollArea_process = QtGui.QScrollArea(self.verticalLayoutWidget)
        self.scrollArea_process.setWidgetResizable(True)
        self.scrollArea_process.setObjectName(_fromUtf8("scrollArea_process"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 677, 347))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.scrollArea_process.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.scrollArea_process)
        self.plainTextEdit_auto_description = QtGui.QPlainTextEdit(Form)
        self.plainTextEdit_auto_description.setEnabled(False)
        self.plainTextEdit_auto_description.setGeometry(QtCore.QRect(375, 420, 315, 71))
        self.plainTextEdit_auto_description.setObjectName(_fromUtf8("plainTextEdit_auto_description"))

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.label_description_2.setText(_translate("Form", "描述:", None))
        self.label_description.setText(_translate("Form", "<html><head/><body><p>描述这个版本做了哪些内容或者有哪些修改；填写需要通知的人。最后点击 提交 按钮提交。</p></body></html>", None))
        self.label_title.setText(_translate("Form", "最终提交:", None))
        self.label_email.setText(_translate("Form", "通知:", None))

