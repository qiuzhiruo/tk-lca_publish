# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2015.07
#
# Description: As the description shows below
#
############################################

import os
import traceback
import pymel.core as pm
import shutil


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"升文件版本号后保存"
        self.description = u"将场景升级版本号后保存"


    def proceed(self):
        try:
            ma_file = pm.sceneName()
            version_up = ma_file[:-7] + 'v' + format( int(self.dialog.version_num)+1, '#03' ) + '.ma'
            pm.saveAs(version_up)
            return ""
        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


