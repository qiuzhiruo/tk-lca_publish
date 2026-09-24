# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.07
#
# Description: Create version dir on the server
#
############################################

import os
import traceback
import pymel.core as pm
import shutil
# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"输出子资产的ma文件"
        self.description = u"将选取的子资产组分别输出到各自的版本文件夹下。删除当前场景中的资产。"
        return


    def proceed(self):
        try:

            for asset_name in self.dialog.d_assets_info.keys():
                version_dir = self.dialog.d_assets_info[asset_name]['version_dir']
                root = self.dialog.d_assets_info[asset_name]['node']
                tank_file = self.dialog.d_assets_info[asset_name]['tank_file']

                # translation = self.dialog.d_assets_info[asset_name]['translation']
                # pm.xform(root, r=True, translation=(translation[0] * -1,  translation[1] * -1, translation[2] * -1))

                pm.select(root, r=True)
                pm.exportSelected( tank_file, force=True, options="v=0;", type="mayaAscii", pr=True, es=True)
                pm.delete(root)
                
                shutil.copy(tank_file,self.dialog.d_assets_info[asset_name]['work_file'])
            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description

