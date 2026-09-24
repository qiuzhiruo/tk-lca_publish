# -*- coding:utf-8 -*-

import os
import  sys
import pymel.core as pm
import maya.cmds as cmds
from proc.function_running_time import record_time


class StdCheck:

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查是否有model_lite任务"
        self.description = u"检查是否有model_lite任务，提醒制作人更新lite。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    @record_time(__file__)
    def run_check(self):
        self.asset_name = os.path.basename(pm.sceneName()).split('.')[0]

        asset =  self.dialog.sg.find_one('Asset', [['code', 'is', self.asset_name]], ['sg_asset_type'])

        model_task =  self.dialog.sg.find('Task', [['entity', 'is', asset], ['content', 'is', 'model_lite']])
        if model_task:
            msg = u'当前资产有lite版模型任务，记得审查lite版本是否需要更新。(点 Yes 便可以继续当前发布)'
            result = pm.confirmDialog( title=u"注意！！！" , message=msg, button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No' )
            if result == 'No':
                return u'已停止当前版本更新。'
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


