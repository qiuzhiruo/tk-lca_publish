# -*- coding:utf-8 -*-

import traceback

import os
import re
import pymel.core as pm

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查资产组装位移。"
        self.description = u"组装资产|master|asb不可以有位移。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def run_check(self):

        try:
            if not pm.objExists("|master"):
                return u"没有找到最高层的 |master 组。"

            if not pm.objExists("|master|asb"):
                return u"没有找到次高层的 |master|asb 组。"

            master = pm.PyNode('|master')
            asb = pm.PyNode('|master|asb')

            if master.hasAttr('blendWorldPC'):
                master.setAttr('blendWorldPC', 0)

            if not master.getMatrix().isEquivalent(pm.dt.Matrix.identity) or not asb.getMatrix().isEquivalent(pm.dt.Matrix.identity):
                return u"|master 和 |master|asb 组不能有任何位移、旋转和缩放"
                # why don't we auto fix it? because moving top master will raise issue of double transformation on objects with deform rigging sets

            return ""

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


