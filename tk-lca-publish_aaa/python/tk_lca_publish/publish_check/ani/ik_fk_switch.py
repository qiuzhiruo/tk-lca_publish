# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2014 Light Chaser Animation
#
# Author: wanghuan
#
# Date: 2014.11
#
# Description: see description below
#
############################################

import traceback
import os
import maya.cmds as cmds

import production.mayautils as mutils

SWITCH_CTRLS = ('L_armSettings_ctrl',
                'R_armSettings_ctrl',
                'L_legSettings_ctrl',
                'R_legSettings_ctrl')
SWITCH_ATTR = 'fkIkBlend'

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查IK/FK切换的动画曲线。"
        self.description = u"切换属性的动画曲线，tangents需要为step模式，防止运动模糊出问题"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return


    def run_check(self):
        try:
            self.invalid_nodes = []
            switchCtrls = cmds.ls(SWITCH_CTRLS, recursive=True, referencedNodes=True)
            for ctrl in mutils.progressIter(switchCtrls,
                                            status=self.get_check_name(),
                                            isInterruptable=False):
                path = '.'.join([ctrl, SWITCH_ATTR])
                if not cmds.objExists(path):
                    continue

                curves = cmds.listConnections(path, d=False, type='animCurve')
                if not curves:
                    continue

                keys = cmds.keyframe(curves, query=True, valueChange=True)
                keys = set(keys)
                if len(keys) <= 1:
                    continue

                tangents = cmds.keyTangent(curves, query=True, outTangentType=True)
                if set(tangents) != set(['step']):
                    self.invalid_nodes.extend(curves)

            if self.invalid_nodes:
                cmds.select(self.invalid_nodes)
                return u'发现tangents不是step模式的动画曲线:\n' + ',\n'.join(self.invalid_nodes)

            return ''
        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        try:
            cmds.keyTangent(self.invalid_nodes, edit=True, outTangentType='step')
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

