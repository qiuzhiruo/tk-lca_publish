# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.07
#
# Description: Check shtogun data
#
############################################

import traceback

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查任务(Task)是否有完整的链接"
        self.description = u"检查Task是否被归于任何项目(project)之下。\n检查Task有没有接到 资产/镜头/场(asset/shot/sequence)链接。"
        self.auto_fix = False
        self.duty = u"项目管理人员检查shotgun数据。"
        return


    def run_check(self):
        try:
            if not self.dialog.task:
                return u"Shotgun: 没有发现任务(Task)。"

            if not self.dialog.project:
                return u"Shotgun: 任务(Task)没有被归于任何项目(project)之下。"

            if not self.dialog.entity:
                return u"Shotgun: 任务(Task)没有有效地链接到 资产/镜头/场(asset/shot/sequence)。"

            if not self.dialog.step:
                return u"Shotgun: 任务(Task)没有 pipeline step。"

            return ""

        except:
            return traceback.format_exc()
    

    def run_fix(self):
        '''Auto Fix'''
        return


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty

