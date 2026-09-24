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
        self.check_name = u"检查master组。"
        self.description = u"资产最上层组为master,其次为rig,poly,lo组。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    def run_check(self):

        try:
            import pymel.core as pm
            if not pm.objExists("|master"):
                return u"没有找到最高层的 |master 组。"

            #if not pm.objExists("|master|poly"):
            #    pm.group(n="poly",em=1,p="|master")

            #if not pm.objExists("|master|poly|hi"):
            #    pm.group(n="hi",em=1,p="|master|poly")

            #if not pm.objExists("|master|rig"):
            #    return u"没有找到次高层的 |master|rig 组。"

            for root in ["global_ctrl"]:
                scale = pm.getAttr("{}.scale".format(root))
                for a in scale:
                    if a != 1.0:
                        return u"root_ctrl 或者 global_ctrl 有缩放值."

            # if pm.objExists("|master|poly|hi"):
                # return u"如果是layout rig任务,没有hi组,只有lo组"

            # if not pm.objExists("|master|poly|lo"):
                # return u"没有找到低模 |master|poly|lo 组。"

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


