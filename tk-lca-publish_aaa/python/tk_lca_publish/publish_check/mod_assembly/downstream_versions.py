# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2015.07
#
# Description: 
#
########################################################################################

import traceback
import sys
import os

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查被选择的子资产有没有downstream版本。"
        self.description = u"如果已经有了downstream版本，会提出警告。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def run_check(self):

        try:
            l_ds_assets = []
            for asset_name in self.dialog.d_assets_info.keys():
                l_sg_versions = self.dialog.d_assets_info[asset_name]['sg_versions']
                for version in l_sg_versions:
                    if version['sg_version_type'] == 'Downstream':
                        l_ds_assets.append(asset_name)

            l_ds_assets = list(set(l_ds_assets))
            if len(l_ds_assets):
                return u"有些资产: " + ', '.join(l_ds_assets) + u" 已经有了 downstream publish, 需要确认是否需要再publish更新。"

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


