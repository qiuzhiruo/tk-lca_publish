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
        self.check_name = u"检查当前plt任务命名是否规范"
        self.description = u"PLT任务名必须是plant 或者 <资产名>+'_'+<描述>(不能有_)。"
        self.auto_fix = False
        self.duty = u"项目管理。"
        return


    def run_check(self):
        try:
            asset = self.dialog.entity['name']
            task_name = self.dialog.task['name'].lower()
            self.dialog.print_log(asset+'\n'+task_name)

            if task_name!=self.dialog.task['name']:
                return u"PLT任务名必须小写"
            if task_name!='plant' and not re.match(asset+'_[a-z0-9]+$', task_name):
                return u"PLT任务名必须是plant 或者 <资产名>+'_'+ <描述> (不能有_)"

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

