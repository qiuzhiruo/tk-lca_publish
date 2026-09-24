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
        self.description = u"将提交的edl文件和wav文件拷贝到版本文件夹。"
        return



    def proceed(self):
        try:
            fc_edl = str(self.dialog.w_publish_file.lineEdit_edl.text())
            if os.path.isfile(fc_edl):
                shutil.copyfile(fc_edl, self.dialog.version_dir + '/' + self.dialog.version_name + '.edl')

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


