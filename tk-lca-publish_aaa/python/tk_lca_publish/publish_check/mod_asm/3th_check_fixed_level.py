# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: guan
#
# Date: 2022.2.15
#
# Description:
#
############################################

import traceback

import os
import re
import pymel.core as pm


# All system check classes will use StdCheck as the class name.
class StdCheck():
    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查捏资产的固定层级结构。"
        self.description = u"检查捏资产的固定层级结构。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def run_check(self):

        try:

            if not pm.objExists("rig"):
                return u"请检测这个是否是可以捏脸的文件，没找到rig文件夹"

            if not pm.objExists("master|poly|hi|mesh_grp"):
                return u"文件层级结构错误请检查一下。"

            name_list=["head_grp","head_geo","head_low_eyeopen_geo","head_hi_eyeopen_geo","head_hi_geo"]

            for child in pm.listRelatives('mesh_grp', c=True):

                if child not in name_list:
                    return u"meshgrp命名错误，head_grp，head_geo，head_low_eyeopen_geo，head_hi_eyeopen_geo，head_hi_geo，这几个文件必须存在。"





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
