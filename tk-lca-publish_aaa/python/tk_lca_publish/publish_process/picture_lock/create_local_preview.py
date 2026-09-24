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
import sys
import traceback
import shutil
import subprocess


os.environ['RV_ENABLE_MIO_FFMPEG'] = '1'

class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"在本地生成预览的 mov (带声音)"
        self.description = u"在本地生成预览的 mov (带声音)"
        return

    def proceed(self):
        try:
            p = subprocess.Popen('ls -d ~', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            (out, err) = p.communicate()
            home_dir = out[:-1]
            if not os.path.isdir(home_dir + '/Temp'):
                os.makedirs(home_dir + '/Temp')

            v_preview = home_dir + '/Temp/' + self.dialog.version_name + '.mov'
            img_dir = self.dialog.version_dir + '/jpg/L/'
            audio_file = self.dialog.version_dir + '/' + self.dialog.version_name + '.wav'
            cmd = '"'+ self.dialog.rvio_path +'" [ ' + img_dir + ' ' + audio_file + ' ] -scale 0.25 -o ' + v_preview

            self.dialog.print_log('Create mov files. '+cmd)
            p = subprocess.Popen(cmd, shell=True)
            p.communicate()

            if os.path.isfile(v_preview):
                self.dialog.l_preview_files = [v_preview]

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description

