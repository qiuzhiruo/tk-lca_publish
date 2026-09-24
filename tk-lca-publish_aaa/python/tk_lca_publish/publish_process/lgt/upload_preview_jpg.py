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
import tempfile
import ConfigParser
# All publish process will use StdProcess as the class name.


class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"拷贝文件到服务器上版本文件夹"
        self.description = u"将艺术家提交的文件拷贝到版本文件夹。"
        return


    def proceed(self):
        if 'R3' in self.dialog.version_tag:
            return ''

        if self.dialog.publish_mode==0:
            self.dialog.print_log('Copy seq to ./jpg/L')
            try:
                os.makedirs(self.dialog.version_dir+'/jpg/L')
            except:
                pass
            for l in self.dialog.l_jpg_seqs:
                shutil.copy(l,self.dialog.version_dir+'/jpg/L/'+os.path.basename(l))

        return ''

    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description