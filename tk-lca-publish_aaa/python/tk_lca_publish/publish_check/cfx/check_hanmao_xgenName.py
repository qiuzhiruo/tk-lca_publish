# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Ma mengxiao
#
# Date: 2026.04
#
# Description: As the description shows below
#
############################################

import traceback
import maya.cmds as cmds

class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查汗毛xgen命名正确性"
        self.description = u"检查汗毛xgen命名正确性"
        self.auto_fix = False
        self.duty = u"艺术家本人"
        return

    def run_check(self):
        try:
            l_bad_names = []
            for n in cmds.ls(type='xgmDescription'):
                if 'hanmao' in n :
                    parents = cmds.listRelatives(n, parent=True, fullPath=True)[0]
                    l_bad_names.append(parents)
            if l_bad_names:
                return ',\n'.join(l_bad_names) + ',\n确认以上 Cllection 是否为真正意义上的汗毛，如果不是请手动更改为正确部位毛发的命名，如果是请取消勾选此检查项忽略即可。'
            else:
                return ''
        except:
            return traceback.format_exc()
    

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