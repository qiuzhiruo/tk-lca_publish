# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Yingjie
#
# Date: 2017.8
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

import os
import sys
import shutil
import traceback
import glob
import re
import subprocess
import plt.xgen_file_manager.file_utils as pxfu
reload(pxfu)


class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"将xgen cache从output盘拷贝到publish"
        self.description = u"将xgen cache从output盘拷贝到publish"
        return

    def proceed(self):
        try:
            ctx=self.dialog.ctx
            me_entity=self.dialog.sg.find_one(ctx.entity['type'], [['id', 'is', ctx.entity['id']]], ['type', 'sg_asset_type', 'code'])
            
            output_cache=str(self.dialog.w_publish_file.lineEdit_cache.text())
            self.dialog.tank_file=''

            if me_entity['type'] == 'Shot':
                if output_cache and os.path.isdir(output_cache+'/cache'):
                    pxfu.copy_xgen_cache_to(output_cache,self.dialog.version_dir)
                else:
                    return u"文件夹为空，或者没有/cache文件夹"
            else:
                if output_cache and os.path.isdir(output_cache+'/xgen'):
                    pxfu.copy_xgen_assetcache_to(output_cache,self.dialog.version_dir)
                else:
                    return u"不是资产下的output版本"

            return ""
        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description

