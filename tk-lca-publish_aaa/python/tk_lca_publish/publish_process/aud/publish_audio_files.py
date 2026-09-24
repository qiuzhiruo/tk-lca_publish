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
import subprocess
import sys
import copy_audio as ca

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"拷贝文件到服务器上版本文件夹"
        self.description = u"将艺术家提交的文件拷贝到版本文件夹。"
        return



    def proceed(self):
        try:
            # For art/edt department, the publish files and the preview files are the same.
            # for file_path in self.dialog.l_preview_files:
            #     shutil.copyfile(file_path, self.dialog.version_dir + '/' + os.path.basename(file_path))

            # self.dialog.wav_files
            # cks.copy_katana_set(self.dialog)
            copy_audio =ca.CopyAudio(self.dialog) 
            copy_audio.do_publish()

            return ''

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


