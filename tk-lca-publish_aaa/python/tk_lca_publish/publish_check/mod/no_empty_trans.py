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
from proc.function_running_time import record_time

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查空组。"
        self.description = u"|master|poly 下的组最底层应该带有 mesh 或者 curve。如果是空组就直接删除。"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return


    @record_time(__file__)
    def run_check(self):

        try:
            l_empty_trans = []
            for asset_name in self.dialog.d_assets_info.keys():
                root = self.dialog.d_assets_info[asset_name]['node']
                # root = '|master|poly'
                l_trans = pm.listRelatives(root, ad=True, type='transform', fullPath=True)
                if '|master|poly|hi' in l_trans:
                    l_trans.remove('|master|poly|hi')

                for trans in l_trans:
                    l_shapes = pm.listRelatives(trans, ad=True, s=True)
                    if len(l_shapes) == 0:
                        l_empty_trans.append(trans.name())

            if len(l_empty_trans) > 0:
                return u'发现空组:\n' + '\n'.join(l_empty_trans)

            return ""

        except:
            return traceback.format_exc()
    

    def run_fix(self):
        '''Auto Fix'''
        try:
            for asset_name in self.dialog.d_assets_info.keys():
                root = self.dialog.d_assets_info[asset_name]['node']
                l_trans = pm.listRelatives(root, ad=True, type='transform')
                if '|master|poly|hi' in l_trans:
                    l_trans.remove('|master|poly|hi')

                for trans in l_trans:
                    if not pm.objExists(trans):
                        continue

                    l_meshes = pm.listRelatives(trans, ad=True, type = 'mesh')
                    if len(l_meshes) == 0:
                        pm.delete(trans)

            return ''

        except:
            return traceback.format_exc()

        return


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty


