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

import os
import traceback

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"在服务器上为子资产建立版本文件夹"
        self.description = u"在服务器上为子资产建立版本文件夹。"
        return


    def proceed(self):
        try:

            for asset_name in self.dialog.d_assets_info.keys():
                version_dir = self.dialog.d_assets_info[asset_name]['version_dir']

                if not os.path.isdir(version_dir):
                    os.makedirs(version_dir)

                if not os.path.isdir(version_dir + '/preview'):
                    os.makedirs(version_dir + '/preview')

                if self.dialog.entity['name'] == asset_name:
                    self.dialog.version_dir = self.dialog.d_assets_info[asset_name]['version_dir']

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description

