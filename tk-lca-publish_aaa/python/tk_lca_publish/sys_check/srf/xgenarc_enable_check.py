# -*- coding:utf-8 -*-
__author__='yingjie'

import traceback

import os
import re

# All system check classes will use StdCheck as the class name.
class StdCheck():


    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查是否需要出Xgen Archive"
        self.description = u"通过资产类型，判断xgen archive是否需要自动出"
        self.auto_fix = False
        self.duty = u"Srf"
        return


    def run_check(self):
        try:
            self.dialog.xgenarc_enable()
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

