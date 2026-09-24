# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2019.02
#
# Description: As the description shows below
#
############################################

import traceback
import pymel.core as pm

    
# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查毛发节点命名"
        self.description = u"检查毛发节点命名"
        self.auto_fix = True
        self.duty = u"艺术家本人"
        return

    def run_check(self):
        try:
            l_bad_names = []
            for n in pm.ls(type='xgmDescription'):
                p = n.getParent()
                if n.nodeName() != p.nodeName() + 'Shape':
                    l_bad_names.append(n.nodeName())

            return ''.join(l_bad_names)
        except:
            return traceback.format_exc()
    

    def run_fix(self):
        '''Auto Fix'''
        for n in pm.ls(type='xgmDescription'):
            p = n.getParent()
            if n.nodeName() != p.nodeName() + 'Shape':
                n.rename(p.nodeName() + 'Shape')
        return ''


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty



