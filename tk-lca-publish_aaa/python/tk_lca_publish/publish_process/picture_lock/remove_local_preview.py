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
import subprocess


class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"删除在本地生成的预览 mov"
        self.description = u"删除在本地生成的预览 mov"
        return

    def proceed(self):
        try:
            p = subprocess.Popen('ls -d ~', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            (out, err) = p.communicate()
            home_dir = out[:-1]
            v_preview = home_dir + '/Temp/' + self.dialog.version_name + '.mov'
            if os.path.isfile(v_preview):
                os.remove(v_preview)

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description

