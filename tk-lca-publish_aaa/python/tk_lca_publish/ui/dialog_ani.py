# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'P:\home\liulu\td_dev_zone\sgtk\tk-lca-publish\resources\dialog.ui'
#
# Created: Tue Sep 22 12:06:28 2015
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

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(720, 637)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        Dialog.setStyleSheet(_fromUtf8("QWidget\n"
"{\n"
"    font-size: 12px;\n"
"}\n"
""))
        self.verticalLayout_3 = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.stackedWidget = QtGui.QStackedWidget(Dialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.stackedWidget.sizePolicy().hasHeightForWidth())
        self.stackedWidget.setSizePolicy(sizePolicy)
        self.stackedWidget.setMinimumSize(QtCore.QSize(700, 500))
        self.stackedWidget.setObjectName(_fromUtf8("stackedWidget"))
        self.verticalLayout_2.addWidget(self.stackedWidget)
        self.verticalLayout_3.addLayout(self.verticalLayout_2)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(10, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.comboBox_publish_mode = QtGui.QComboBox(Dialog)
        self.comboBox_publish_mode.setMinimumSize(QtCore.QSize(150, 30))
        self.comboBox_publish_mode.setObjectName(_fromUtf8("comboBox_publish_mode"))
        self.comboBox_publish_mode.addItem(_fromUtf8(""))
        self.comboBox_publish_mode.addItem(_fromUtf8(""))
        self.comboBox_publish_mode.addItem(_fromUtf8(""))
        self.horizontalLayout.addWidget(self.comboBox_publish_mode)
        self.progressBar_publish_process = QtGui.QProgressBar(Dialog)
        self.progressBar_publish_process.setMinimumSize(QtCore.QSize(260, 30))
        self.progressBar_publish_process.setTextVisible(False)
        self.progressBar_publish_process.setObjectName(_fromUtf8("progressBar_publish_process"))
        self.horizontalLayout.addWidget(self.progressBar_publish_process)
        self.pushButton_prev = QtGui.QPushButton(Dialog)
        self.pushButton_prev.setMinimumSize(QtCore.QSize(120, 30))
        self.pushButton_prev.setObjectName(_fromUtf8("pushButton_prev"))
        self.horizontalLayout.addWidget(self.pushButton_prev)
        self.pushButton_next = QtGui.QPushButton(Dialog)
        self.pushButton_next.setMinimumSize(QtCore.QSize(120, 30))
        self.pushButton_next.setObjectName(_fromUtf8("pushButton_next"))
        self.horizontalLayout.addWidget(self.pushButton_next)
        spacerItem1 = QtGui.QSpacerItem(10, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.textEdit_log = QtGui.QTextEdit(Dialog)
        self.textEdit_log.setObjectName(_fromUtf8("textEdit_log"))
        self.verticalLayout.addWidget(self.textEdit_log)
        self.verticalLayout_3.addLayout(self.verticalLayout)

        self.retranslateUi(Dialog)
        self.stackedWidget.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "LCA Publish Tool", None))
        self.comboBox_publish_mode.setItemText(0, _translate("Dialog", "只交预览( For Daily)", None))
        self.comboBox_publish_mode.setItemText(1, _translate("Dialog", "预提交(Checked)", None))
        self.comboBox_publish_mode.setItemText(2, _translate("Dialog", "为下游提交文件(Downstream)", None))
        self.pushButton_prev.setText(_translate("Dialog", "<< 返回", None))
        self.pushButton_next.setText(_translate("Dialog", "下一步 >>", None))

