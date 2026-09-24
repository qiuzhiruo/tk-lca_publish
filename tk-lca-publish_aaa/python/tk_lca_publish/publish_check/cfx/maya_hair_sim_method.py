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

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查HairSystem设置"
        self.description = u"检查HairSystem设置。"
        self.auto_fix = True
        self.duty = u"艺术家本人"
        return


    def run_check(self):

        try:
            if 'cloth' in self.dialog.task['name']:
                return ''
            hairs = listRelatives('|master|hair',typ='hairSystem')
            for hair in hairs:
                if hair.simulationMethod.get() is not 1:
                    return hair.longName()+u' 的simulationMethod设置不是 Static'
        except:
            return traceback.format_exc()
            
        return ''

    def run_fix(self):
        '''Auto Fix'''
        hairs = ls(typ='hairSystem')
        n_set = 0
        for hair in hairs:
            if hair.simulationMethod.get() is not 1:
                hair.simulationMethod.set(1)
                n_set+= 1
                print u'已将 '+hair.longName()+u' 的simulationMethod设置为Static'
        print str(n_set)+u' 个hairSystem被设置。'
        return ''


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty


