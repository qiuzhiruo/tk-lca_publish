# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.07
#
# Description: Check asset model group hierarchy
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
        self.check_name = u"检查资产相机层级命名。"
        self.description = u"相机最上层组为cameras,其下可以有多组摄像机，包括立体相机。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    def run_check(self):

        try:
            import maya.cmds as cmds

            if not cmds.objExists("|cameras"):
                return u"没有找到最高层级的 |cameras 组。"

            if not cmds.objExists("|assets"):
                return u"没有找到最高层的 |assets 组。"

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


