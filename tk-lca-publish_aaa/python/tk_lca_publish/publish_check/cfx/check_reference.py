# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2015.01
#
# 
#
########################################################################################

import traceback
import pymel.core as pm

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"cloth任务是否reference了模型publish的最新本。"
        self.description = u"制作中应该refernece无版本号的最新版模型。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    def run_check(self):
        try:
            if not pm.general.objExists('|master'):
                return u'没有找到 |master 组。'

            task_name = self.dialog.task['name'].lower()
            if task_name.startswith('hair' ) or task_name.startswith('plant' ):
                return ""

            dept = self.dialog.step['name']
            asset_name = self.dialog.entity['name']
            mod_file = self.dialog.publish_root.replace('/'+dept+'/', '/mod/') + '/' + asset_name + '.mod.model/' + asset_name + '.ma'

            if not pm.referenceQuery('|master', isNodeReferenced=True):
                return u"没有reference模型版本"

            ref_path = pm.referenceQuery('|master', filename =True)

            if ref_path != mod_file:
                return u"没有使用最新的模型版本: " + mod_file

            return ""

        except:
            return traceback.format_exc()
    

    def run_fix(self):
        '''Auto Fix'''
        try:
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



