# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Huang Xin
#
# Date: 2018.7.19
#
# Description: As the description shows below
#
############################################

import os
import traceback
import re
import glob
import sys


# All system check classes will use StdCheck as the class name.


class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查output cache的任务名和当前publish任务名是否匹配"
        self.description = u"output路径所带任务名必须和publish任务名匹配"
        self.auto_fix = False
        self.duty = u"艺术家本人"
        return

    def run_check(self):
        try:
            if self.dialog.ui.comboBox_publish_mode.currentIndex()==0:
                return ''

            output_cache=str(self.dialog.w_publish_file.lineEdit_cache.text())
            task_name = self.dialog.task['name'].lower()

            if self.dialog.entity_type == 'Shot':
                if output_cache:
                    path_task = output_cache.split('.')[-2]
                    if path_task != task_name:
                        return u'选择的cache属于 [%s] 任务, 不能publish在当前任务 [%s] 下,\n请到该任务 [%s] 下publish\n'%(path_task, task_name, path_task)
                    else:
                        return ''
                else:
                    return u"文件夹为空，或者没有/cache文件夹"
            
            return ""

        except:
            return traceback.format_exc()
    

    def run_fix(self):
        '''Auto Fix'''
        try:
            return ''

        except:
            return traceback.format_exc()


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty


