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

import re
from proc.function_running_time import record_time


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查版本(Version)的命名是否规范。"
        self.description = u"版本名应该是由\".\"分割的4段组成:{entity}.{department}.{task}.{version number}。\n比如 dog.art.concept_design.v001; e30020.ani.animation.v075"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    @record_time(__file__)
    def run_check(self):

        try:
            # This is tricky, any input from the GUI need to consider the possible issue from Chinese letters
            version_name_qtstr = self.dialog.version_key.decode("utf-8") + self.dialog.w_ver.lineEdit_version_name.text()
            version_name = str(version_name_qtstr)
            if version_name != version_name.lower():
                return u"错误的版本名:" +version_name+ u"\n版本名必须全小写。"

            p = re.compile("[\w\.]*$")
            if not p.match(version_name):
                return u"错误的版本名:" + version_name+ u"\n版本名只能由a-z的字母，0-9数字，下划线\"_\"和点\".\"组成。"

            tokens = version_name.split('.')
            if len(tokens) != 4:
                return version_name+ u"\n版本名应该是{entity}.{department}.{task}.{version number}四段。"

            if len(tokens[3]) !=4 or tokens[3][0] != 'v' or not tokens[3][1:].isdigit():
                return version_name+ u"\n版本号必须是 v + 3位数字格式。"

            self.dialog.version_name = version_name
            self.dialog.version_num  = tokens[3][1:]

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

