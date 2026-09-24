# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Wang Huan
# Date: 2015.10
#
# Description: As the description shows below
#
############################################

import os
import traceback

import pymel.core as pm

SKELETON_GROUP_NAME = 'anim_skeletons_grp'


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"骨骼组存在且唯一。"
        self.description = u"存在唯一一个名为%s的组，用于导出行为数据。"%SKELETON_GROUP_NAME
        self.auto_fix = False
        self.duty = u"艺术家本人，及绑定组。"
        return

    def run_check(self):
        try:
            groups = pm.ls(SKELETON_GROUP_NAME, recursive=True, exactType='transform')
            if not groups:
                return u'未找到名为%s的组。'%SKELETON_GROUP_NAME

            # if len(groups) > 1:
            #     return u'找到多个名为%s的组，请确保场景中只引用了一个资产。'%SKELETON_GROUP_NAME

            self.dialog.skeletons_group = groups[0]
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
