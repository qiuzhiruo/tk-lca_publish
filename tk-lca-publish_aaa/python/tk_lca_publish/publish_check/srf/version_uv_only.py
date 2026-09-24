# -*- coding:utf-8 -*-
__author__ = 'huazhuo'


import traceback

import os
import re
import sgtk
from sgtk.platform.qt import QtCore, QtGui

import traceback
import shutil


# All system check classes will use StdCheck as the class name.
class StdCheck():
    
    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"提交贴图后不能只提交UV"
        self.description = u"提交带贴图的版本后不能提交只有UV的版本"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return
    
    def run_check(self):
        try:
            if not int(self.dialog.w_publish_file.checkBox.isChecked()):
                return ''

            tex_dir = os.path.join(self.dialog.publish_root,'tex')
            
            if os.path.exists(tex_dir):
                return u"提交带贴图的版本后不能提交只有UV的版本"
        except:
            return traceback.format_exc()
        
        return ''
    def run_fix(self):
        '''Auto Fix'''
        return
    
    def get_check_name(self):
        return self.check_name
    
    def get_description(self):
        return self.description
    
    def get_auto_fix(self):
        return self.auto_fix
    
    def get_duty(self):
        return self.duty


