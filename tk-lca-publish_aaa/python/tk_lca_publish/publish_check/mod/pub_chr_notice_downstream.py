# -*- coding:utf-8 -*-

import os
import maya.cmds as cmds
import production.shotgun_connection as shotgun
from PySide2 import QtWidgets
from proc.function_running_time import record_time


class NoteTool(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(NoteTool, self).__init__(parent)
        self.setWindowTitle(u'角色第一次发高模型是否通知下游?')
        self.tool_tip = QtWidgets.QLabel('[注]： 此消息只有模型发布成功后才会发送给相关人员！这里只做信息收集。')
        self.three_chr_cbx = QtWidgets.QCheckBox('三级角色完全复用')
        self.note_text = QtWidgets.QTextEdit()
        self.resize(300, 150)
        self.yes_btn = QtWidgets.QPushButton(u'通知')
        self.cancel_bnt = QtWidgets.QPushButton(u'不通知')
        self.all_v_layout = QtWidgets.QVBoxLayout()
        self.btn_h_layout = QtWidgets.QHBoxLayout()
        self.init_layout()
        self.init_connect()
        self.is_note_downstream = False
        self.is_three_chr = False

    def init_layout(self):
        self.btn_h_layout.addWidget(self.yes_btn)
        self.btn_h_layout.addWidget(self.cancel_bnt)
        self.all_v_layout.addWidget(self.note_text)
        self.all_v_layout.addWidget(self.three_chr_cbx)
        self.all_v_layout.addLayout(self.btn_h_layout)
        self.all_v_layout.addWidget(self.tool_tip)

        self.setLayout(self.all_v_layout)

    def yes_bnt_clicked(self):
        self.is_note_downstream = True
        self.close()

    def three_chr_status(self):
        self.is_three_chr = bool(self.three_chr_cbx.checkState())

    def cancel_bnt_clicked(self):
        self.close()

    def init_connect(self):
        self.yes_btn.clicked.connect(self.yes_bnt_clicked)
        self.cancel_bnt.clicked.connect(self.cancel_bnt_clicked)
        self.three_chr_cbx.stateChanged.connect(self.three_chr_status)



class StdCheck:

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"角色第一次发高模型是否通知下游?"
        self.description = u"角色发布第一版高模的时候是否通知下游。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    @record_time(__file__)
    def run_check(self):

        file_name = cmds.file(q=True, sn=True)
        asset_name = os.path.basename(file_name).split('.')[0]
        sg = shotgun.Connection('get_project_info').get_sg()
        filters_asset = [['code', 'is', asset_name]]
        asset = sg.find_one('Asset', filters_asset, ['id', 'sg_asset_type'])
        self.dialog.note_downstream = False
        if not asset or self.dialog.w_sys.comboBox_tag.currentText() not in [u'精模']:
            return ''
        if asset['sg_asset_type'] not in ['chr']:
            return ''
        project = sg.find_one("Project", [["name", "is", self.dialog.project['name']]], ["id", "name"])
        filters_version = [['project', 'is', {'type': 'Project', 'id': project['id']}],
                   ['entity', 'is', {'type': 'Asset', 'id': asset['id']}]]
        versions = sg.find("Version", filters_version, ["description", 'sg_version_type', 'tag_list'])
        is_first_high = True

        for version in versions:
            if version['sg_version_type']=='Downstream':
                tag_list = version['tag_list']
                if "精模" in tag_list:
                    is_first_high = False
                    break

        if not is_first_high:
            return ''

        msg = u'资产 {} 第一版高模已发布，请及时查看。'.format(asset_name)
        note_tool = NoteTool(self.dialog)
        note_tool.note_text.setText(msg)
        note_tool.show()
        note_tool.exec_()

        if note_tool.is_note_downstream:
            self.dialog.note_downstream = True
            self.dialog.is_three_chr = note_tool.is_three_chr
            self.dialog.note_msg = note_tool.note_text.toPlainText()

        return ''


    def run_fix(self):
        '''Auto Fix'''

        return ''

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty


