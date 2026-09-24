# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: John Su
#
# Date: 2014.1
#
# Description: As the description shows below
#
############################################

import os
import traceback
import re

class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"Asset路径检查"
        self.description = u"检查所选Asset路径的合法性"
        self.auto_fix = False
        self.duty = u"艺术家本人"
        return

    def run_check(self):
        try:
            c = self.dialog.w_publish_file.listWidget_cache.count()
            if c>1:
                return u'请只选择一个顶层文件夹路径'

            path = self.dialog.w_publish_file.listWidget_cache.item(0).text()
            if len(path.split())>=2:
                return u'路径中不能包含空格 '+path

            component_name=path.split('/')[-3]
            extension=path.split('.')[-1]
            if not os.path.isdir(path):
                return u'请选择文件夹'

            exp = r'.*/[\d\w]*\..*\..*\.v\d{3}$'
            if not re.match(exp, path):
                return path+u'不标准，选择一个顶层文件夹路径'

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


