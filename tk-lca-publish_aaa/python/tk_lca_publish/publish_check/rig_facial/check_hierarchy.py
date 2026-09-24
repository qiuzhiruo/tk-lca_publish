# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.07
#
# Description: Check asset geometry hierarchy
#
############################################

import traceback

import os
import re

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查资产层级命名。"
        self.description = u"资产最上层组为master,其次为rig,poly, hi/lo组。lo组必须有。如果是layout rig任务，只有lo组"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    def run_check(self):
        try:
            import pymel.core as pm

            if not pm.objExists("|facial_model_grp"):
                return u"没有找到次高层的 |facial_model_grp 组。"

            if not pm.objExists("facial_head_geo"):
                return u"没有找到名为 facial_head_geo 的模型。"

            if pm.objExists("facial_guides_grp"):
                return u"facial_guides_grp 是表情摆位模板应该删除。"

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


