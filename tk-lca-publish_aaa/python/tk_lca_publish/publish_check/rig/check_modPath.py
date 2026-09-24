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
import maya.cmds as mc
import os
import re


class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查 master.modPath 模型路径是否正确"
        self.description = u"检查 master.modPath 模型路径是否正确"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def run_check(self):
        try:
            current_file_path = mc.file(sn=1, q=1)
            char_name = re.findall('(?<=maya/)\w+', current_file_path)[0]
            current_file_path = os.path.normpath(mc.getAttr("master.modPath"))
            modPath = os.path.split(current_file_path)[1].split('.')[0]
            if char_name != modPath:
                return self.description
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


