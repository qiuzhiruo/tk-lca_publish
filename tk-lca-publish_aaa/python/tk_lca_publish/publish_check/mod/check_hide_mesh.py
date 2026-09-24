# -*- coding:utf-8 -*-
import pymel.core as pm
from proc.function_running_time import record_time


class StdCheck():
    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查隐藏的资产"
        self.description = u"hi层级下不允许有隐藏的mesh。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    @record_time(__file__)
    def run_check(self):

        for mesh_obj in pm.listRelatives('|master|poly|hi', ad=True):
            mesh_obj.setAttr('visibility', 1)
        return ''

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








