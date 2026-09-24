# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2015.07
#
# Description: Check file reference
#
############################################
import traceback
import os
import pymel.core as pm

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u'检查镜头中的 Assembly Definition 节点。'
        self.description = u'镜头中不允许有 Assembly Definition 节点。'
        self.auto_fix = True
        self.duty = u'艺术家本人。'
        return

    def run_check(self):
        try:
            l_ad = []
            for n in pm.ls(type='assemblyDefinition'):
                l_ad.append(n.name())

            if len(l_ad) > 0:
                return u"发现 Assembly Definition 节点：" + u' '.join(l_ad)

            return ""
        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        try:
            for n in pm.ls(type='assemblyDefinition'):
                pm.delete(n)
            return ''
        except:
            return traceback.format_exc()

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty

