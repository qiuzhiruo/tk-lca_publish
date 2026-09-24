# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.10
#
# Description: No referenced nodes under |master.
#
########################################################################################

import traceback
import pymel.core as pm

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"master 组是否有位移。"
        self.description = u"master 组是否有位移。"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return


    def run_check(self):
        try:

            if not pm.general.objExists('|master'):
                return u'没有找到 |master 组。'

            for a in 'tr':
                for aa in 'xyz':
                    if pm.getAttr('%s.%s%s' %('master',a,aa)) != 0.0:
                        return u'|master 组有位移'

            for a in 's':
                for aa in 'xyz':
                    if pm.getAttr('%s.%s%s' %('master',a,aa)) != 1.0:
                        return u'|master 组有缩放'

            return ""

        except:
            return traceback.format_exc()
    

    def run_fix(self):
        '''Auto Fix'''
        try:
            if not pm.general.objExists('|master'):
                return u'没有找到 |master 组。'
            for a in 'tr':
                for aa in 'xyz':
                    pm.setAttr('%s.%s%s' %('master',a,aa),0.0)

            for a in 's':
                for aa in 'xyz':
                    pm.setAttr('%s.%s%s' %('master',a,aa),1.0)
            return ''
        except:
            return traceback.format_exc()


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty



