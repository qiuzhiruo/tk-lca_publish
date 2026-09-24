# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.11
#
# Description: As the description shows below
#
############################################

import traceback, os
from pymel.core import *

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查插件"
        self.description = u"检查shave和Arnold for Maya是否安装，以及extensions是否配置正确。"
        self.auto_fix = False
        self.duty = u"运维或自己安装"
        return


    def run_check(self):
        try:
            pluginInfo('shaveNode',q=1,v=1)     # raise exception if not setup
        except:
            return u'shave插件未安装。'
        try:
            pluginInfo('mtoa',q=1,v=1)          # raise exception if not setup
        except:
            return u'mtoa插件未安装。'
            
        if not os.getenv('MTOA_EXTENSIONS_PATH'):
            return u'MTOA_EXTENSIONS_PATH 未设置'
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


