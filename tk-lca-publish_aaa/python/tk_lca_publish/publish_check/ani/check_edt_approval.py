# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Wang Huan
#
# Date: 2015.12
#
# Description: As the description shows below
#
############################################

import os
import traceback

EDT_TASK_NAME = 'edt_check'
APPROVAL_STATUS = ('aa', 'aaa')

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查当前镜头剪辑任务是否通过。"
        self.description = u"镜头剪辑任务（%s）需要标记为aa或aaa，否则动画不能提交下游。"%(EDT_TASK_NAME)
        self.auto_fix = False
        self.duty = u"剪辑组或PC"
        return

    def run_check(self):
        try:
            if self.dialog.project['name'].lower() == 'cat':
                return ''

            edt_task = self.dialog.sg.find_one(
                'Task',
                [['entity', 'is', self.dialog.entity],
                 ['step', 'name_is', 'edt'],
                 ['content', 'is', EDT_TASK_NAME]],
                ['sg_status_list', ]
            )
            if not edt_task:
                self.dialog.print_log(u"当前镜头未找到名为%s的剪辑任务，自动跳过检查……"%(EDT_TASK_NAME))
                return ''

            if edt_task['sg_status_list'] not in APPROVAL_STATUS:
                return u'当前镜头剪辑任务尚未通过，请先找剪辑组检查。'

            return ''
        except:
            return traceback.format_exc()

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
