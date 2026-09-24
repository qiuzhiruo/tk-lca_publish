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
import pymel.core as pm
import sys
import os


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"资产的中心设置为资产的底部。"
        self.description = u"如果勾选，资产中心和大环都放在资产的底部。\n如果不勾选，资产中心和大环放在世界坐标原点。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def run_check(self):

        try:
            for asset_name in self.dialog.d_assets_info.keys():
                root = self.dialog.d_assets_info[asset_name]['node']
                parent = self.dialog.d_assets_info[asset_name]['parent']

                if parent:
                    pm.parent(root, world=True)

                rotation = root.getRotation()
                root.setRotation((0.0, 0.0, 0.0))
                # bbox = root.getBoundingBox()
                # (x_min,y_min,z_min) = root.getBoundingBox()[0]
                # (x_max,y_max,z_max) = root.getBoundingBox()[1]
                # # translation = ((x_min + x_max)/2.0,  y_min, (z_min + z_max)/2.0)
                root.setRotation(rotation)
                # self.dialog.d_assets_info[asset_name]['translation'] = translation
                self.dialog.d_assets_info[asset_name]['rotation'] = rotation

                if parent:
                    pm.parent(root, parent)

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


