# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.08
#
# Description: Copy publish files
#
############################################

import os
import traceback
import shutil


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"拷贝文件到服务器上版本文件夹"
        self.description = u"将艺术家提交的文件拷贝到版本文件夹。"
        return

    def proceed(self):
        try:
            import pymel.core as pm
            # Copy ma file
            ma_file = str(pm.saveFile())
            if os.path.isfile(ma_file):
                shutil.copyfile(ma_file, self.dialog.version_dir + '/' + os.path.basename(ma_file))
                self.dialog.publish_ma = self.dialog.version_dir + '/' + os.path.basename(ma_file)
            return ""

        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
