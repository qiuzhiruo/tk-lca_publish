# -*- coding:utf-8 -*-

import traceback

import os
import re
import pymel.core as pm

from proc.function_running_time import record_time


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查大纲层级结构。"
        self.description = u"master 层级下不能有并列的group"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return
        
    @record_time(__file__)
    def run_check(self):

        try:
            node_list = pm.listRelatives('master', c=True)
            error_list =[]
            for i in node_list:
                if i.type() != 'assemblyReference':
                    error_list.append(i) 

            if error_list:
                return u"master下只能有 AR节点，请清理多余的group节点：" + ', '.join([i.name() for i in error_list])
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


