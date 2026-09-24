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
import subprocess

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"拷贝文件到服务器上版本文件夹"
        self.description = u"将艺术家提交的文件拷贝到版本文件夹。"
        return



    def proceed(self):
        try:
            # Copy the look file.
            if self.dialog.srf_config_file:
                shutil.copyfile(self.dialog.srf_config_file[0], self.dialog.version_dir + '/' + self.dialog.entity['name']+'.srf')
                            
                for i in range(1,len(self.dialog.srf_config_file)):
                    if os.path.isfile(self.dialog.srf_config_file[i]):
                        shutil.copyfile(self.dialog.srf_config_file[i], self.dialog.version_dir + '/' + os.path.basename(self.dialog.srf_config_file[i]))

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


