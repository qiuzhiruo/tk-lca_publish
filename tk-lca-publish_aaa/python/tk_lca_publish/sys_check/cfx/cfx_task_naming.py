# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.07
#
# 
#
############################################

import traceback

import os
import re

# All system check classes will use StdCheck as the class name.
class StdCheck():


    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查当前CFX任务命名是否规范"
        self.description = u"CFX任务名必须以 hair 或者 cloth 结尾。"
        self.auto_fix = False
        self.duty = u"项目管理。"
        return


    def run_check(self):
        try:
            task_name = self.dialog.task['name'].lower()
            if not (task_name.endswith('hair') or task_name.endswith('cloth') or  task_name.endswith('plant')):
                return u"CFX任务名必须以 hair 或者 cloth  或者 plant 结尾。"

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

