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

import traceback
import os
import sys
import shutil

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"拷贝相关配置文件到服务器上版本文件夹"
        self.description = u"将艺术家提交的相关配置文件拷贝到版本文件夹。"
        return


    def copy_xml(self):
        """
        copy & rename sequence xml
        """
        edt_file = str(self.dialog.w_publish_file.xml_lineEdit.text())
        if edt_file:
            seq_name = self.dialog.entity['name']
            ext = '.aaf' if self.dialog.aaf_file else '.xml'
            dst_file = os.path.join(self.dialog.version_dir, seq_name + ext).replace('\\', '/')
            shutil.copyfile(edt_file, dst_file)

    def proceed(self):
        try:
            self.copy_xml()
            return ''

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


