# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'widget_file_srf.ui'
#
# Created: Thu Aug 22 17:26:05 2019
#      by: PyQt4 UI code generator 4.10.1
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
        self.checkBox_xgenarc = QtGui.QCheckBox(Form)
        self.checkBox_xgenarc.setGeometry(QtCore.QRect(20, 50, 111, 20))
        self.checkBox_xgenarc.setObjectName(_fromUtf8("checkBox_xgenarc"))
        self.checkBox = QtGui.QCheckBox(Form)
        self.checkBox.setGeometry(QtCore.QRect(20, 20, 121, 20))
        self.checkBox.setObjectName(_fromUtf8("checkBox"))
        self.checkBox_shader = QtGui.QCheckBox(Form)
        self.checkBox_shader.setGeometry(QtCore.QRect(20, 80, 111, 22))
        self.checkBox_shader.setObjectName(_fromUtf8("checkBox_shader"))
        self.checkBox_exp = QtGui.QCheckBox(Form)
        self.checkBox_exp.setGeometry(QtCore.QRect(20, 110, 150, 22))
        self.checkBox_exp.setObjectName(_fromUtf8("checkBox_expression"))
        
        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.checkBox_xgenarc.setText(_translate("Form", "Xgen Archive", None))
        self.checkBox.setText(_translate("Form", "只publish xml", None))
        self.checkBox_shader.setText(_translate("Form", "Push Shader", None))
        self.checkBox_exp.setText(_translate("Form", "Publish Expression", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Form = QtGui.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())

