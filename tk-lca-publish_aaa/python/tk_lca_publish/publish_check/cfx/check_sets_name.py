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

import traceback
from pymel.core import *
import re

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查各sets名称是否无意义"
        self.description = u"set在publish前必须修正set1等无意义命名。"
        self.auto_fix = False
        self.duty = u"艺术家本人"
        return


    def run_check(self):
        try:
            sets = ls(et = 'objectSet')
            for s in sets:
                set_name = s.name()
                if re.match(r'set\d+',set_name):
                    select(s,ne=1)
                    return (set_name+u'命名无意义')
                
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


