# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Zhang Zhixiang
#
# Date: 2015.11
#
# Description: As the description shows below
#
############################################

import traceback
import pymel.core as pm
import re

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查毛发 MPW 和 Opaque 渲染设置"
        self.description = u"检查毛发节点 Min Pixel Width 设置, 保证其大于0.05；自动修复会改成 0.1; Ai Opaque 不能勾选。"
        self.auto_fix = True
        self.duty = u"艺术家本人"
        return


    def run_check(self):
        try:

            for node in pm.ls(et = 'xgmDescription'):
                if node.aiMinPixelWidth.get() < 0.05:
                    return (u'Xgen 节点 ' + str(node) + u' Min Pixel Width 设置不正确, 应该>0.05')
                if node.aiOpaque.get() == True:
                    return (u'Xgen 节点 ' + str(node) + u' Ai Opaque 设置不正确, 不应该勾选')

            for node in pm.ls(et = 'pgYetiMaya'):
                if node.aiMinPixelWidth.get() <0.05:
                    return (u'Yeti 节点 ' + str(node)+u'MPW 设置不正确 >0.05')
                if node.aiOpaque.get() == True:
                    return (u'Yeti 节点 ' + str(node) + u' Ai Opaque 设置不正确, 不应该勾选')

        except:
            return traceback.format_exc()
        return ''

    def run_fix(self):
        '''Auto Fix'''
        try:
            for n_type in ['xgmDescription', 'pgYetiMaya']:
                for node in pm.ls(et = n_type):
                    if node.aiMinPixelWidth.get() < 0.05:
                        node.aiMinPixelWidth.set(0.1)
                    if node.aiOpaque.get() == True:
                        node.aiOpaque.set(False)
            return ''

        except:
            return traceback.format_exc()
        return


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty


