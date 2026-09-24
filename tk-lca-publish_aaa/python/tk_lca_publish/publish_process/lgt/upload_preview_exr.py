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
import re
import traceback
import shutil
import subprocess
import tempfile
import ConfigParser
# All publish process will use StdProcess as the class name.


class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"拷贝预览用exr到服务器上版本文件夹"
        self.description = u"将艺术家提交的文件拷贝到版本文件夹。"
        return

    def proceed(self):
        if 'R3' in self.dialog.version_tag:
            return ''

        if self.dialog.publish_mode == 0:
            # copy lossy exr to publish folder
            l_exr_path = os.path.dirname(self.dialog.l_preview_files[0])
            lossy_exr = re.sub('/L', '/lossy_exr', l_exr_path)
            publish_lossy_exr = self.dialog.version_dir+'/lossy_exr'
            self.dialog.print_log('Copy {0} to {1}'.format(
                lossy_exr, publish_lossy_exr))
            if os.path.isdir(lossy_exr):
                try:
                    if os.path.isdir(publish_lossy_exr):
                        shutil.rmtree(publish_lossy_exr)
                    shutil.copytree(lossy_exr, publish_lossy_exr)
                except Exception, e:
                    self.dialog.print_log(str(e))
            else:
                self.dialog.print_log(u'预览用lossy exr未找到!\n'+l_exr_path)

        return ''

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description