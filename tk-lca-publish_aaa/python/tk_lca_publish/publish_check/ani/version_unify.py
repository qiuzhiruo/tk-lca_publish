# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2014.01
#
# Description: 
#
############################################

import traceback
import os

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查版本(Version)号是否统一。"
        self.description = u"版本号必须和当前动画文件。\n比如动画要Pulbish的是 v016 版，相应当前的动画文件应该也是 ***.v016.ma。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    def run_check(self):

        try:
            import pymel.core as pm
            ma_file = str(pm.sceneName())

            if os.path.basename(ma_file) != self.dialog.version_name + '.ma':
                return  u"当前要提交的Maya文件名应该是: "  + os.path.basename(ma_file)+ u", 而设定的publish版本是 " + self.dialog.version_name

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

