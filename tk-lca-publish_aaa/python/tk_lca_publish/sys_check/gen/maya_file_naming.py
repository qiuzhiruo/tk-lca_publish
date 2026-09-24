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

import os
import re

# All system check classes will use StdCheck as the class name.
class StdCheck():


    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查当前Maya文件是否命名规范"
        self.description = u"检查当前Maya文件是否是ma文件。是否遵守LCA文件命名规范。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    def run_check(self):
        try:
            import pymel.core as pm
            file_path = pm.sceneName()

            if file_path == '':
                return u"当前Maya文件还没有保存。"

            file_dir = os.path.split(file_path)[0]
            file_name = os.path.split(file_path)[1]

            if not file_dir.startswith(self.dialog.work_root):
                return u"当前Maya文件需要存放在工作路径之下:\n"+self.dialog.work_root

            # naming convention

            if not file_name == file_name.lower():
                return u"错误的文件名:" +file_name+ u"\n文件名必须全小写。"

            if not file_name.endswith('.ma'):
                return u"当前Maya文件不是 ma 格式。"

            p = re.compile("[\w\.]*$")
            if not p.match(file_name):
                return u"错误的文件名:" + file_name+ u"\n文件名只能由a-z的字母，0-9数字，下划线\"_\"和点\".\"组成。"

            tokens = file_name.split('.')
            if len(tokens) != 5:
                return u"错误的文件名:" + file_name+ u"\n文件名应该是:{entity}.{department}.{task}.{version number}.ma 五段组成。"

            if '.'.join(tokens[:3]) != self.dialog.version_key:
                return u"错误的文件名:" + file_name+ u"\n文件名应该由:"+self.dialog.version_key+u"开头。"

            if len(tokens[3]) !=4 or tokens[3][0] != 'v' or not tokens[3][1:].isdigit():
                return u"错误的文件名:" + file_name+ u"\n版本号必须是 v + 3位数字格式。"
        
            if tokens[3] == 'v000':
                return u"错误的文件名:" + file_name+ u"\nv000版不允许publish。"

            self.dialog.w_ver.lineEdit_version_name.setText('.'+tokens[3])

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

