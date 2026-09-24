# -*- coding: utf-8 -*-
# @Time    : 18-8-9 上午11:36
# @Author  : zhangzheng
__author__ = 'zhangzheng'
__maintainer__ = 'zhangzheng'

import os
import traceback
import shutil


# All publish process will use StdProcess as the class name.
class StdProcess():
    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"拷贝文件到服务器上版本文件夹"
        self.description = u"将艺术家提交的文件拷贝到版本文件夹内。"
        return
    
    def proceed(self):
        try:
            import pymel.core as pm
            # Copy ma file
            ma_file = str(pm.saveFile())
            self.dialog.publish_ma = self.dialog.version_dir + '/' + os.path.basename(ma_file)
            
            if os.path.isfile(ma_file):
                shutil.copyfile(ma_file, self.dialog.publish_ma)
    
            return ""

        except:
            return traceback.format_exc()
    
    def get_process_name(self):
        return self.process_name
    
    def get_description(self):
        return self.description