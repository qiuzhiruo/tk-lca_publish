# -*-coding:utf-8-*-
"""
 @Time : 5/8/23 6:30 PM
 @Author : Taka(xutao)
"""


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

        self.cb_render_srf = QtGui.QCheckBox(Form)
        self.cb_render_srf.setGeometry(QtCore.QRect(20, 30, 111, 20))
        self.cb_render_srf.setObjectName(_fromUtf8('cb_render_srf'))

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.cb_render_srf.setText(_translate('From', '渲染材质版本', None))
