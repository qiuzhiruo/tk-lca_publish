# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.08
#
# Description: 
#
############################################

import os
import traceback
import shutil

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"拷贝文件到服务器。"
        self.description = u"拷贝当前的 maya 文件到服务器。"
        return


    def proceed(self):
        try:
            import pymel.core as pm
            self.dialog.tank_file = self.dialog.version_dir + '/' + os.path.basename(pm.system.sceneName())
            shutil.copyfile(pm.system.sceneName(), self.dialog.tank_file)
            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


