# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2016.03
#
# Description: 
#
############################################
import traceback
import os
import pymel.core as pm

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u'检查放错的 Assembly Reference 节点。'
        self.description = u'Assembly Reference 节点引用的资产，不能移到其他Assembly Reference节点下。'
        self.auto_fix = False
        self.duty = u'艺术家本人。'
        return

    def run_check(self):
        try:
            l_ar = []
            for node in pm.ls(type='assemblyReference'):
                if (not ':' in node.name()):
                    tokens = node.fullPath().split('|')
                    for t in tokens[:-1]:
                        if ':' in t or '_AR' in t:
                            l_ar.append(node.fullPath())

            l_ar = list(set(l_ar))
            if len(l_ar) > 0:
                return u"发现被放错的 Assembly Referece 节点：\n" + u'\n'.join(l_ar)

            return ""
        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        try:
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

