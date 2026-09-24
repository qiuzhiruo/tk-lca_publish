# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.12
#
# Description: As the description below
#
############################################

import traceback
import pprint
import os

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查任务(Task)和任务所属的资产/镜头是否已经da/final。"
        self.description = u"Shotgun上如果任务的状态变为da/fin/omt就不能再publish了。如果一定要publish，需要找到项目管理修改任务状态。"
        self.auto_fix = False
        self.duty = u"项目管理。"
        return


    def run_check(self):

        try:

            sg_info = self.dialog.sg.find_one('Task', [['id', 'is', self.dialog.task['id']]], ['sg_status_list'])
            if not sg_info['sg_status_list']:
                return u'任务状态不明。'

            if sg_info['sg_status_list'] in ['omt', 'fin', 'da']:
                return u'任务 '+self.dialog.task['name'] + u' 状态为: '+sg_info['sg_status_list'] + u'，这样状态的任务无法publish，请找项目管理改任务状态。'

            sg_info = self.dialog.sg.find_one(self.dialog.entity['type'], [['id', 'is', self.dialog.entity['id']]], ['sg_status_list'])
            if not sg_info['sg_status_list']:
                return self.dialog.entity['type'] + u'状态不明。'

            if sg_info['sg_status_list'] in ['omt', 'fin']:
                return self.dialog.entity['type'] + ' '+self.dialog.entity['name'] + u' 状态为: '+sg_info['sg_status_list'] + u'，这样状态的任务无法publish，请找项目管理改任务状态。'

            return ""

        except:
            return traceback.format_exc()
    

    def run_fix(self):
        '''Auto Fix'''
        return ""


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty

