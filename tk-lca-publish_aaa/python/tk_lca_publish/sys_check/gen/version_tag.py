# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2015.01
#
# Description: 
#
############################################

import traceback
import pprint
import os

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查版本的标签是否选择。"
        self.description = u"检查版本的标签是否选择。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    def run_check(self):

        try:
            self.dialog.version_tag = self.dialog.w_sys.comboBox_tag.currentText()

            if self.dialog.version_tag == '':
                return u"还没有选择版本的标签。"

            if self.dialog.version_tag =='Rough lgt':
                self.dialog.w_publish.plainTextEdit_description.setPlainText(u"本版本仅供组内审核。")

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

