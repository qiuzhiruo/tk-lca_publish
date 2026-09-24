# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2016.08
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
        self.process_name = u"拷贝文件到服务器上版本文件夹"
        self.description = u"拷贝文件到服务器上版本文件夹"
        return

    def proceed(self):
        try:
            shutil.copyfile(self.dialog.edt_file, self.dialog.version_dir + '/' + self.dialog.version_name + '.txt')
            shutil.copyfile(self.dialog.audio_file, self.dialog.version_dir + '/' + self.dialog.version_name + '.wav')
            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


