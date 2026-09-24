# -*- coding:utf-8 -*-

import traceback

import os
import re
import pymel.core as pm

from proc.function_running_time import record_time


@record_time(__file__)
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查scene组位移。"
        self.description = u"|scene组和其下的组不可以有位移。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    @record_time(__file__)
    def run_check(self):

        try:
            scn = pm.PyNode('|scene')
            children = pm.listRelatives(scn, c=True, type='transform')

            if not scn.getMatrix().isEquivalent(pm.dt.Matrix.identity):
                return u"|scene 组不能有任何位移、旋转和缩放"

            for c in children:
                if not c.getMatrix().isEquivalent(pm.dt.Matrix.identity):
                    return u"|scene|" + str(c) + u"组发现位移、旋转或缩放信息"

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


