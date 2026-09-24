# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Yingjie
#
# Date: 2015.5
#
# Description: 
#
############################################

import os
import re
import subprocess
import traceback
import shutil
# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"Copy Mod advice info."
        self.description = u"Copy Mod advice info."
        return


    def proceed(self):
        try:
            in_ma=str(self.dialog.w_publish_file.lineEdit_ma_file.text())
            if not in_ma or not os.path.isfile(in_ma):
                return ''

            out_info_file=os.path.join(self.dialog.version_dir,self.dialog.entity['name']+'.info')                
            shutil.copy(in_ma,out_info_file)
            if not os.path.isfile(out_info_file):
                return 'Copy info failed.'
                
            return ''

        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


