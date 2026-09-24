#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2025/5/19 15:14
# @File    : check_dynamics_attribute.py


import traceback
import maya.cmds as mc
import os
import re


class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查动力学属性命名是否正确"
        self.description = u"检查动力学属性命名是否正确"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def run_check(self):
        self.extra_run()
        control = "mus_dynamic_ctrl"
        attr_array = ["enable_pri", "enable_sec", "start_frame", "fps"]
        try:
            if mc.objExists(control):
                result = []
                for item in attr_array:
                    if not mc.objExists("{}.{}".format(control, item)):
                        result.append(item)
                if len(result) == 0:
                    return ''
                else:
                    return u'{}: \n缺少属性：{}'.format(self.description, result)
            else:
                return ''
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


    def extra_run(self):
        obj_array = ["bangsheng_jian_hi", "bangsheng_qiao_hi"]
        for i in obj_array:
            if mc.objExists(i):
                mc.delete(i)
                print "delete obj ({})".format(i)

