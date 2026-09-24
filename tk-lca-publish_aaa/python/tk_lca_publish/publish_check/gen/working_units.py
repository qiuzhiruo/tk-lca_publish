# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Wang Huan
#
# Date: 2015.05
#
# Description: Check scene working units
#
############################################

import traceback
import pymel.core as pm


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查Maya场景工作单位。"
        self.description = u"目前应统一使用厘米（cm）作为工作单位，即便实际制作中一个单位（一格）相当于一分米。"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        self.target_linear = 'cm'
        return


    def run_check(self):
        try:
            current_linear = pm.general.currentUnit(query=True, linear=True)
            if current_linear != self.target_linear:
                return u'当前工作单位为%s，应该使用%s'%(current_linear, self.target_linear)

            return ""

        except:
            return traceback.format_exc()


    def run_fix(self):
        '''Auto Fix'''
        pm.mel.changeLinearUnit(self.target_linear)
        return ''


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty

