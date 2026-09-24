# -*- coding:utf-8 -*-
import os
import sys
import re
import pymel.core as pm

from PySide2 import QtWidgets, QtCore
from production.shotgun_connection import Connection


class ReuseAssetWin(QtWidgets.QDialog):
    ConfirmDescriptionSign = QtCore.Signal(int)
    def __init__(self):
        super(ReuseAssetWin, self).__init__()
        self.sg = Connection('get_project_info').get_sg()
        scence_path = pm.sceneName().replace('\\', '/')
        asset_name = os.path.basename(scence_path).split('.')[0]
        proj_name = re.search('projects/(\w{3})/', scence_path).group(1)
        proj = self.sg.find_one('Project', [['name', 'is', proj_name]], [])
        self.asset_info = self.sg.find_one('Asset', [['project', 'is', proj], ['code', 'is', asset_name]], ['description'])
        self.versions = self.sg.find('Version', [['entity', 'is', {'type': 'Asset', 'id': self.asset_info['id']}]], ['sg_task'])
        self.resize(670, 200)
        self.confirm_btn = QtWidgets.QPushButton(u'确认描述')
        self.reuse_label = QtWidgets.QLabel(u'复用类型:')
        self.note_label = QtWidgets.QLabel(u'【注】：该页面仅限mod组用来更改复用资产描述，修改会通知到制片。\n\t如果确认描述按钮可以点击，请确认描述后再进入下一步，如果不可以，请忽略。\n\t'
                                           u'除了 ‘不改描述’ 选项外其余选项都会根据输入框的内容更改shotgun上资产的描述。\n\t')
        self.all_v_layout = QtWidgets.QVBoxLayout()
        self.description_edit = QtWidgets.QTextEdit()
        self.asset_label = QtWidgets.QLabel(u'复用资产名:')
        self.asset_line = QtWidgets.QLineEdit(asset_name)
        self.asset_h_layout = QtWidgets.QHBoxLayout()
        self.reuse_h_layout = QtWidgets.QHBoxLayout()
        self.reuse_cbbx = QtWidgets.QComboBox()
        self.init_ui()
        self.init_layout()
        self.init_connect()
        if self.versions:
            self.default_description = self.asset_info['description']
        else:
            try:
                self.default_description = os.path.basename(pm.getAttr('master.modPath')).replace('.ma', '')
            except Exception as e:
                self.default_description = ''

        self.description_edit.setText(self.default_description)
        self.confirm_btn.setEnabled(False)

    def init_ui(self):
        reuse_select = [u'不改描述', u'复用', u'半复用', u'无复用']
        self.reuse_cbbx.addItems(reuse_select)

    def init_layout(self):

        self.all_v_layout.addWidget(self.description_edit)
        self.all_v_layout.addWidget(self.reuse_cbbx)
        self.asset_h_layout.addWidget(self.asset_label)
        self.asset_h_layout.addWidget(self.asset_line)
        # self.all_v_layout.addLayout(self.asset_h_layout)
        self.all_v_layout.addWidget(self.confirm_btn)
        self.all_v_layout.addWidget(self.note_label)
        # self.asset_h_layout.addWidget(self.confirm_btn)

        self.setLayout(self.all_v_layout)

    def init_connect(self):
        self.confirm_btn.clicked.connect(self.confirm_description)
        self.description_edit.textChanged.connect(self.reuse_cbbx_change)
        self.reuse_cbbx.currentTextChanged.connect(self.reuse_cbbx_change)

    def confirm_description(self):
        # self.ConfirmDescriptionSign.connect(self.hello)
        self.confirm_btn.setStyleSheet('color: rgb(132, 143, 186);')
        # self.ConfirmDescriptionSign.emit(1)

    def description_edit_change(self):
        if u'复用' == self.reuse_cbbx.currentText() and self.description_edit.toPlainText().encode('utf-8') != self.default_description:
            self.confirm_btn.setEnabled(True)
        else:
            self.confirm_btn.setEnabled(False)

    def reuse_cbbx_change(self):
        description_edit_info = self.description_edit.toPlainText().replace(u'：', ':')
        if u'复用' == self.reuse_cbbx.currentText() and self.description_edit.toPlainText().encode('utf-8') != self.default_description:
            self.confirm_btn.setEnabled(True)
        else:
            self.confirm_btn.setEnabled(False)
        self.description_edit.textChanged.disconnect(self.description_edit_change)
        print(self.description_edit.toPlainText())
        print(u'复用')
        if self.reuse_cbbx.currentText() in [u'复用', u'半复用'] and not description_edit_info.startswith((u'复用:', u'半复用:')):
            self.description_edit.setText( self.reuse_cbbx.currentText() + ':' + description_edit_info)
        elif description_edit_info.startswith(u'复用:') and self.reuse_cbbx.currentText() not in (u'不改描述', u'无复用'):
            self.description_edit.setText(description_edit_info.replace(u'复用:', self.reuse_cbbx.currentText() + ':'))
        elif description_edit_info.startswith(u'半复用:') and self.reuse_cbbx.currentText() not in (u'不改描述', u'无复用'):
            self.description_edit.setText(description_edit_info.replace(u'半复用:', self.reuse_cbbx.currentText() + ':'))
        else:
            self.description_edit.setText(self.default_description)

        self.description_edit.textChanged.connect(self.description_edit_change)


    # def init_description(self):
    #     print('h' * 1000)
    #     if self.versions:
    #         default_description = self.asset_info['description']
    #         default_description = os.path.basename(pm.getAttr('master.modPath')).replace('.ma', '')
    #     else:
    #         default_description = os.path.basename(pm.getAttr('master.modPath')).replace('.ma', '')
    #
    #     self.description_edit.setText(default_description)
    #     self.confirm_btn.setEnabled(False)

    # def hello(self):
    #     print('hello========================================')


def show_win():
    win = ReuseAssetWin()
    win.show()
    win.exec_()

