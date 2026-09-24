# -*- coding:utf-8 -*-

import traceback

import os
import re
import pymel.core as pm

from proc.function_running_time import record_time


class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"文件中不能有常规的 reference。"
        self.description = u"文件中不能有常规的 reference"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    @record_time(__file__)
    def run_check(self):

        try:
            ref = pm.ls(type='reference')
            if len(ref) > 0:
                l_names = [n.name() for n in ref]
                return u"文件中有常规的 reference 节点：" + ', '.join(l_names)
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


