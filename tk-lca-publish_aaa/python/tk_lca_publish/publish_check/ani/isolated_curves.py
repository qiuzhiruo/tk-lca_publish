# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2014.07
#
# Description: As the description shows below
#
############################################

import os
import traceback
import pymel.core as pm

import production.mayautils as mutils


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查无效动画曲线。"
        self.description = u"如果非 Referece 的动画曲线，没有连接到场景内，说明是一些垃圾节点，可以清理掉。"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return


    def run_check(self):

        try:
            l_curves = pm.ls(type="animCurve")
            self.l_isolated_curves = []

            for c in mutils.progressIter(l_curves,
                                         status=self.get_check_name(),
                                         isInterruptable=False):
                if len( pm.listConnections(c , s=False, d=True) ) == 0:
                    if not c.isReferenced():
                        self.l_isolated_curves.append(c.name())

            if self.l_isolated_curves:
                return u"发现冗余的动画节点: " + ', '.join(self.l_isolated_curves)

            return ""

        except:
            return traceback.format_exc()


    def run_fix(self):
        try:
            pm.lockNode(self.l_isolated_curves, lock=False)
            pm.general.delete(self.l_isolated_curves)
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


