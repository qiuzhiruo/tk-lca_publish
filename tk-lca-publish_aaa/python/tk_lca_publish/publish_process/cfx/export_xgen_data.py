# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: yingjie
#
# Date: 2013.11
#
# Description: As the description shows below
#
#export xgen file need to change 1 the "xgFileName" 2 the datapath 3 export the ma file 4 restore the oreint state
#
#
#
#
#
#
############################################

import os, shutil,sys
import traceback
import plt.xgen_file_manager.file_utils as pxfu
reload(pxfu)
from pymel.core import *

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"输出xgen数据。"
        self.description = u"导出xgen cache，将文件导出为一个ma文件，合并reference。"
        return


    def proceed(self):
        try:
            palettes = ls(et='xgmPalette')
            if len(palettes)>0:
                pxfu.publish_cfx_asset_xgen(self.dialog.version_dir)
            
            # self.dialog.tank_file = self.dialog.version_dir +'/'+ self.dialog.entity['name'] + '.ma'
            
            return ""
        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description
