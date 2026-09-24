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
        self.process_name = u"拷贝 Light Rig 文件到服务器上版本文件夹"
        self.description = u"将Light Rig文件拷贝到版本文件夹。"
        return



    def proceed(self):
        try:
            for i in range(self.dialog.w_publish_file.listWidget_lgt_rig.count()):
                file_path = str(self.dialog.w_publish_file.listWidget_lgt_rig.item(i).text())
                if os.path.isfile(file_path):
                    shutil.copyfile(file_path, self.dialog.version_dir + '/' + os.path.basename(file_path))

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


