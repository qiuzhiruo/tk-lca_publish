# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2015.07
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
        self.check_name = u"ASB资产的assembly任务文件中，不能有暴露的 master 节点。"
        self.description = u"资产的最上层的节点中不能有master。如果存在，需要改名或者删除。这个任务文件不能直接publish给下游。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    def run_check(self):

        try:

            if pm.objExists("|master"):
                return u"资产的最上层的节点中不能有 |master 组。如果存在，需要改名或者删除。"

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


